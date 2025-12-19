"""Audit logging middleware for FastAPI applications.

This middleware captures HTTP request/response metadata and stores it in the
AuditLog collection using Beanie. It integrates with structured logging for
consistent observability across all MySingle microservices.

Features:
- Automatic correlation ID propagation
- User context extraction from Kong Gateway or AuthMiddleware
- Performance metrics (latency, payload sizes)
- Distributed tracing support
- Environment-aware logging (disabled in test)

Version: 2.2.1
"""

from __future__ import annotations

import time
import uuid
from typing import Awaitable, Callable

from beanie import PydanticObjectId
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from mysingle.core.config import settings
from mysingle.core.logging import (
    get_correlation_id,
    get_logger,
    set_correlation_id,
    set_request_id,
    set_user_id,
)

from .models import AuditLog

logger = get_logger(__name__)


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that writes an audit log per HTTP request.

    Captures request/response metadata and stores it in MongoDB for
    compliance, security analysis, and performance monitoring.

    Args:
        app: FastAPI application instance
        service_name: Service identifier (e.g., "strategy-service")
        enabled: Enable audit logging (default: True)

    Note:
        - Automatically disabled in test environment
        - Uses structured logging for error handling
        - Integrates with Kong Gateway headers
        - Propagates correlation IDs for distributed tracing

    Example:
        >>> from mysingle.core import AuditLoggingMiddleware
        >>> app.add_middleware(
        ...     AuditLoggingMiddleware,
        ...     service_name="strategy-service",
        ...     enabled=True,
        ... )
    """

    def __init__(
        self,
        app,
        service_name: str,
        enabled: bool = True,
        exclude_paths: list[str] | None = None,
    ):  # type: ignore[no-untyped-def]
        super().__init__(app)
        self.service_name = service_name
        self.enabled = enabled

        # Parse exclude paths from environment if not provided
        if exclude_paths is None:
            exclude_paths_str = getattr(settings, "AUDIT_EXCLUDE_PATHS", "")
            exclude_paths = (
                [path.strip() for path in exclude_paths_str.split(",") if path.strip()]
                if exclude_paths_str
                else []
            )

        self.exclude_paths = exclude_paths

        logger.info(
            "Audit logging middleware initialized",
            service=service_name,
            enabled=enabled,
            exclude_paths=exclude_paths,
        )

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process HTTP request and create audit log.

        Args:
            request: FastAPI Request object
            call_next: Next middleware or route handler

        Returns:
            HTTP Response
        """
        # Skip when disabled or in test environment
        should_log = bool(self.enabled) and (
            getattr(settings, "ENVIRONMENT", "").lower() != "test"
        )

        # Check if path should be excluded from audit logging
        path = request.url.path
        if should_log and self._should_exclude_path(path):
            should_log = False
            # Skip debug log for excluded paths to reduce noise
            # logger.debug(
            #     "Skipping audit log for excluded path",
            #     path=path,
            # )

        start = time.monotonic()

        # Extract request metadata
        method = request.method
        path = request.url.path
        req_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        trace_id = request.headers.get("x-trace-id") or request.headers.get(
            "traceparent"
        )
        user_agent = request.headers.get("user-agent")
        ip = request.client.host if request.client else None

        # Extract or generate correlation ID
        correlation_id = (
            request.headers.get("x-correlation-id")
            or get_correlation_id()
            or str(uuid.uuid4())
        )

        # Set logging context
        set_correlation_id(correlation_id)
        set_request_id(req_id)

        try:
            req_bytes = int(request.headers.get("content-length", "0"))
        except (ValueError, TypeError):
            req_bytes = 0

        # Extract user_id from multiple sources (priority order)
        user_id = self._extract_user_id(request)
        if user_id:
            set_user_id(user_id)

        # Log request start only if we should log
        if should_log:
            logger.debug(
                "HTTP request started",
                method=method,
                path=path,
                correlation_id=correlation_id,
                request_id=req_id,
            )

        response: Response = await call_next(request)

        # Extract response metadata
        try:
            resp_bytes = int(response.headers.get("content-length", "0"))
        except (ValueError, TypeError):
            resp_bytes = 0
        latency_ms = int((time.monotonic() - start) * 1000)

        # Log request completion only if we should log
        if should_log:
            logger.info(
                "HTTP request completed",
                method=method,
                path=path,
                status_code=response.status_code,
                latency_ms=latency_ms,
                req_bytes=req_bytes,
                resp_bytes=resp_bytes,
            )

        if should_log:
            try:
                audit = AuditLog(
                    user_id=PydanticObjectId(user_id) if user_id else None,
                    service=self.service_name,
                    request_id=req_id,
                    trace_id=trace_id,
                    correlation_id=correlation_id,
                    method=method,
                    path=path,
                    ip=ip,
                    user_agent=user_agent,
                    req_bytes=req_bytes,
                    status_code=response.status_code,
                    resp_bytes=resp_bytes,
                    latency_ms=latency_ms,
                )
                await audit.insert()

                logger.debug(
                    "Audit log created",
                    audit_id=str(audit.id),
                    user_id=user_id,
                )
            except Exception as e:
                logger.error(
                    "Failed to insert audit log",
                    error=str(e),
                    error_type=type(e).__name__,
                    method=method,
                    path=path,
                    status_code=response.status_code,
                )

        return response

    def _extract_user_id(self, request: Request) -> str | None:
        """Extract user ID from request context.

        Priority order:
        1. request.state.user.id (AuthMiddleware - most reliable)
        2. X-User-Id header (Kong Gateway or service-to-service)
        3. X-Consumer-Custom-ID header (Kong JWT plugin - legacy)

        Args:
            request: FastAPI Request object

        Returns:
            User ID string or None if not found
        """
        from mysingle.constants import HEADER_KONG_USER_ID, HEADER_USER_ID

        # Priority 1: request.state.user (AuthMiddleware)
        # AuthMiddleware가 먼저 실행되어 이미 user를 설정했으면 이를 사용
        try:
            user = getattr(request.state, "user", None)
            if user and hasattr(user, "id"):
                return str(user.id)
        except Exception as e:
            logger.debug(
                "Failed to extract user from request.state",
                error=str(e),
            )

        # Priority 2: X-User-Id (standard)
        # 대소문자 구분 없이 헤더 검색 (HTTP 헤더는 대소문자 구분 없음)
        for header_key in request.headers:
            if header_key.lower() == HEADER_USER_ID.lower():
                user_id = request.headers.get(header_key)
                if user_id:
                    return user_id.strip()

        # Priority 3: X-Consumer-Custom-ID (Kong - legacy)
        for header_key in request.headers:
            if header_key.lower() == HEADER_KONG_USER_ID.lower():
                kong_user_id = request.headers.get(header_key)
                if kong_user_id:
                    return kong_user_id.strip()

        return None

    def _should_exclude_path(self, path: str) -> bool:
        """Check if request path should be excluded from audit logging.

        Args:
            path: Request path to check

        Returns:
            True if path matches any exclude pattern, False otherwise

        Note:
            Supports both exact matches and prefix patterns:
            - "/health" matches both "/health" and "/health/"
            - "/api/*" matches "/api/..." (prefix wildcard)
        """
        # Normalize path: remove trailing slash except for root path
        normalized_path = path.rstrip("/") if path != "/" else path

        for exclude_pattern in self.exclude_paths:
            # Normalize exclude pattern as well
            normalized_pattern = (
                exclude_pattern.rstrip("/")
                if exclude_pattern != "/"
                else exclude_pattern
            )

            # Check for wildcard patterns (e.g., "/api/internal/*")
            if normalized_pattern.endswith("*"):
                prefix = normalized_pattern[:-1]  # Remove the asterisk
                if normalized_path.startswith(prefix.rstrip("/")):
                    return True
            # Exact match after normalization
            elif normalized_path == normalized_pattern:
                return True

        return False

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

    def __init__(self, app, service_name: str, enabled: bool = True):  # type: ignore[no-untyped-def]
        super().__init__(app)
        self.service_name = service_name
        self.enabled = enabled

        logger.info(
            "Audit logging middleware initialized",
            service=service_name,
            enabled=enabled,
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

        # Log request start
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

        # Log request completion
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
        1. X-User-Id header (Kong Gateway or service-to-service)
        2. X-Consumer-Custom-ID header (Kong JWT plugin)
        3. request.state.user.id (AuthMiddleware)

        Args:
            request: FastAPI Request object

        Returns:
            User ID string or None if not found
        """
        from mysingle.constants import HEADER_KONG_USER_ID, HEADER_USER_ID

        # Priority 1: X-User-Id (standard)
        user_id = request.headers.get(HEADER_USER_ID)
        if user_id:
            return user_id.strip()

        # Priority 2: X-Consumer-Custom-ID (Kong)
        kong_user_id = request.headers.get(HEADER_KONG_USER_ID)
        if kong_user_id:
            return kong_user_id.strip()

        # Priority 3: request.state.user (AuthMiddleware)
        try:
            user = getattr(request.state, "user", None)
            if user and hasattr(user, "id"):
                return str(user.id)
        except Exception as e:
            logger.debug(
                "Failed to extract user from request.state",
                error=str(e),
            )

        return None

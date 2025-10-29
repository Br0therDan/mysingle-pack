"""Audit logging middleware for FastAPI apps.

This middleware captures minimal request/response metadata and stores it in the
AuditLog collection using Beanie. It's designed to be added via the shared
app factory so all microservices can use it consistently.
"""

from __future__ import annotations

import time
from typing import Awaitable, Callable

from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.config import settings
from ..logging import get_logger
from .models import AuditLog

logger = get_logger(__name__)


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that writes an audit log per HTTP request.

    Parameters
    - service_name: Name of the service, stored with each audit record.
    - enabled: Toggle to enable/disable logging (default True). This will be
      AND-ed with environment check to skip in test.
    """

    def __init__(self, app, service_name: str, enabled: bool = True):  # type: ignore[no-untyped-def]
        super().__init__(app)
        self.service_name = service_name
        self.enabled = enabled

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Skip when disabled or in test environment
        should_log = bool(self.enabled) and (
            getattr(settings, "ENVIRONMENT", "").lower() != "test"
        )

        start = time.monotonic()

        # Request metadata
        method = request.method
        path = request.url.path
        req_id = request.headers.get("x-request-id")
        trace_id = request.headers.get("x-trace-id") or request.headers.get(
            "traceparent"
        )
        user_agent = request.headers.get("user-agent")
        ip = request.client.host if request.client else None
        try:
            req_bytes = int(request.headers.get("content-length", "0"))
        except Exception:
            req_bytes = 0

        response: Response = await call_next(request)

        # Response metadata
        try:
            resp_bytes = int(response.headers.get("content-length", "0"))
        except Exception:
            resp_bytes = 0
        latency_ms = int((time.monotonic() - start) * 1000)

        if should_log:
            try:
                # Best-effort user context (avoid importing heavy auth deps here)
                user_id = None
                audit = AuditLog(
                    user_id=user_id,
                    service=self.service_name,
                    request_id=req_id,
                    trace_id=trace_id,
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
            except Exception as e:  # pragma: no cover - best-effort
                logger.warning("audit log insert failed: %s", e)

        return response

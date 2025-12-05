"""Audit log data models for HTTP request/response tracking.

This module provides AuditLog document for storing HTTP audit trails
with correlation IDs, user context, and performance metrics.

Version: 2.2.1
"""

from datetime import UTC, datetime

from beanie import PydanticObjectId
from pydantic import Field

from mysingle.core.base.models import BaseTimeDoc


class AuditLog(BaseTimeDoc):
    """HTTP request/response audit log document.

    Captures minimal request/response metadata for compliance and observability.
    Automatically populated by AuditLoggingMiddleware.

    Attributes:
        user_id: User who made the request (from Kong Gateway or AuthMiddleware)
        service: Service name that handled the request
        request_id: Unique request identifier (X-Request-Id header)
        trace_id: Distributed tracing ID (X-Trace-Id or traceparent)
        correlation_id: Correlation ID for request chain tracking
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        path: Request path (e.g., /api/strategies)
        ip: Client IP address
        user_agent: Client user agent string
        req_bytes: Request payload size in bytes
        status_code: HTTP response status code
        resp_bytes: Response payload size in bytes
        latency_ms: Request processing time in milliseconds
        occurred_at: Timestamp when request occurred

    Indexes:
        - user_id: For user activity queries
        - service: For service-specific queries
        - occurred_at: For time-based queries
        - trace_id: For distributed tracing

    Example:
        >>> audit = AuditLog(
        ...     user_id=user.id,
        ...     service="strategy-service",
        ...     method="POST",
        ...     path="/api/strategies",
        ...     status_code=201,
        ...     latency_ms=123,
        ... )
        >>> await audit.insert()
    """

    # Context fields
    user_id: PydanticObjectId | None = Field(
        None, description="User ID from authentication"
    )
    service: str = Field(..., description="Service name handling request")
    request_id: str | None = Field(None, description="Unique request ID")
    trace_id: str | None = Field(None, description="Distributed trace ID")
    correlation_id: str | None = Field(None, description="Correlation ID for tracking")

    # Request metadata
    method: str = Field(..., description="HTTP method")
    path: str = Field(..., description="Request path")
    ip: str | None = Field(None, description="Client IP address")
    user_agent: str | None = Field(None, description="Client user agent")
    req_bytes: int = Field(0, description="Request size in bytes")

    # Response metadata
    status_code: int = Field(..., description="HTTP status code")
    resp_bytes: int = Field(0, description="Response size in bytes")

    # Performance metrics
    latency_ms: int = Field(0, description="Request latency in milliseconds")
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when request occurred",
    )

    class Settings:
        """Beanie document settings."""

        name = "audit_logs"
        indexes = [
            "user_id",
            "service",
            "occurred_at",
            "trace_id",
            "correlation_id",
        ]

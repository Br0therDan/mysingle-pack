from .app_factory import create_fastapi_app, create_lifespan
from .config import CommonSettings, get_settings, settings
from .db import (
    get_database_name,
    get_mongodb_url,
    init_mongo,
)
from .http_client import (
    HttpClientConfig,
    ServiceHttpClient,
    ServiceHttpClientManager,
    create_service_http_client,
    get_service_http_client,
    http_client_lifespan,
    make_service_request,
)
from .middleware import (
    HealthCheckLoggingFilter,
    LoggingMiddleware,
    TimingLogMiddleware,
    add_logging_middleware,
    setup_request_id_dependency,
)
from .service_types import ServiceType, create_service_config

# Consolidated modules (base, logging, metrics, health, email, audit → core)
from .base import BaseDoc, BaseResponseSchema, BaseTimeDoc, BaseTimeDocWithUserId
from .logging import get_logger, setup_logging
from .metrics import MetricsCollector, get_metrics_collector
from .health import HealthChecker, register_health_routes
from .email import EmailService, send_email
from .audit import AuditLogger, log_audit_event

__all__ = [
    # Core Settings
    "settings",
    "CommonSettings",
    "get_settings",
    # App Factory
    "create_lifespan",
    "create_fastapi_app",
    # Database
    "init_mongo",
    "get_mongodb_url",
    "get_database_name",
    # Service Types
    "ServiceType",
    "create_service_config",
    # HTTP Client
    "ServiceHttpClient",
    "ServiceHttpClientManager",
    "create_service_http_client",
    "get_service_http_client",
    "make_service_request",
    "http_client_lifespan",
    "HttpClientConfig",
    # Middleware
    "LoggingMiddleware",
    "HealthCheckLoggingFilter",
    "TimingLogMiddleware",
    "add_logging_middleware",
    "setup_request_id_dependency",
    # Base (consolidated)
    "BaseDoc",
    "BaseTimeDoc",
    "BaseTimeDocWithUserId",
    "BaseResponseSchema",
    # Logging (consolidated)
    "setup_logging",
    "get_logger",
    # Metrics (consolidated)
    "MetricsCollector",
    "get_metrics_collector",
    # Health (consolidated)
    "HealthChecker",
    "register_health_routes",
    # Email (consolidated)
    "EmailService",
    "send_email",
    # Audit (consolidated)
    "AuditLogger",
    "log_audit_event",
]

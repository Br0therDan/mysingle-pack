from .app_factory import create_fastapi_app, create_lifespan
from .audit import AuditLog, AuditLoggingMiddleware

# Consolidated modules (base, logging, metrics, health, email, audit → core)
from .base import BaseDoc, BaseResponseSchema, BaseTimeDoc, BaseTimeDocWithUserId
from .config import CommonSettings, get_settings, settings
from .db import (
    get_database_name,
    get_mongodb_url,
    init_mongo,
)
from .email import send_email
from .health import HealthStatus, create_health_router, get_health_checker
from .logging import get_structured_logger, setup_logging
from .metrics import MetricsCollector, get_metrics_collector
from .middleware import (
    HealthCheckLoggingFilter,
    LoggingMiddleware,
    TimingLogMiddleware,
    add_logging_middleware,
    setup_request_id_dependency,
)
from .service_types import ServiceType, create_service_config

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
    "get_structured_logger",
    # Metrics (consolidated)
    "MetricsCollector",
    "get_metrics_collector",
    # Health (consolidated)
    "HealthStatus",
    "get_health_checker",
    "create_health_router",
    # Email (consolidated)
    "send_email",
    # Audit (consolidated)
    "AuditLog",
    "AuditLoggingMiddleware",
]

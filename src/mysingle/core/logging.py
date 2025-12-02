"""
MySingle Integrated Logging System

Unified structured and traditional logging with context propagation.

Features:
- Structured logging (structlog) with JSON output support
- Traditional logging (logging) with color output and file rotation
- Context variables: correlation_id, user_id, request_id
- Environment-aware configuration (development/production)
- Convenience functions for common logging patterns

Version: 2.2.1
"""

import logging
import sys
from contextvars import ContextVar
from pathlib import Path
from typing import Optional

import structlog

try:
    import colorlog

    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False


# =============================================================================
# Context Variables
# =============================================================================

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


# =============================================================================
# Structured Logging Processors
# =============================================================================


class CorrelationIdProcessor:
    """Inject correlation_id into log events"""

    def __call__(self, logger, method_name, event_dict):
        correlation_id = correlation_id_var.get()
        if correlation_id:
            event_dict["correlation_id"] = correlation_id
        return event_dict


class ServiceNameProcessor:
    """Inject service name into log events"""

    def __init__(self, service_name: str):
        self.service_name = service_name

    def __call__(self, logger, method_name, event_dict):
        event_dict["service"] = self.service_name
        return event_dict


class UserContextProcessor:
    """Inject user_id and request_id into log events"""

    def __call__(self, logger, method_name, event_dict):
        user_id = user_id_var.get()
        request_id = request_id_var.get()

        if user_id:
            event_dict["user_id"] = user_id

        if request_id:
            event_dict["request_id"] = request_id

        return event_dict


# =============================================================================
# Structured Logging Configuration
# =============================================================================


def configure_structured_logging(
    service_name: str,
    log_level: str = "INFO",
    enable_json: bool = False,
):
    """
    Configure structlog-based logging

    Args:
        service_name: Service identifier
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_json: Enable JSON output (recommended for production)
    """
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        ServiceNameProcessor(service_name),
        CorrelationIdProcessor(),
        UserContextProcessor(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if enable_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_structured_logger(name: str):
    """
    Get a structured logger instance

    Args:
        name: Logger name (typically __name__)

    Returns:
        Structured logger with context support
    """
    return structlog.get_logger(name)


# =============================================================================
# Context Management
# =============================================================================


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current context"""
    correlation_id_var.set(correlation_id)
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)


def set_user_id(user_id: str) -> None:
    """Set user ID for current context"""
    user_id_var.set(user_id)
    structlog.contextvars.bind_contextvars(user_id=user_id)


def set_request_id(request_id: str) -> None:
    """Set request ID for current context"""
    request_id_var.set(request_id)
    structlog.contextvars.bind_contextvars(request_id=request_id)


def get_correlation_id() -> str:
    """Get current correlation ID"""
    return correlation_id_var.get()


def get_user_id() -> str:
    """Get current user ID"""
    return user_id_var.get()


def get_request_id() -> str:
    """Get current request ID"""
    return request_id_var.get()


def clear_logging_context() -> None:
    """Clear all logging context variables"""
    correlation_id_var.set("")
    user_id_var.set("")
    request_id_var.set("")
    structlog.contextvars.clear_contextvars()


# =============================================================================
# Convenience Logging Functions
# =============================================================================


def log_user_action(
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    success: bool = True,
    error: Optional[str] = None,
) -> None:
    """
    Log user actions with standardized format

    Args:
        action: Action performed (e.g., "create", "update", "delete")
        resource_type: Type of resource (e.g., "strategy", "backtest")
        resource_id: Resource identifier
        details: Additional action details
        success: Whether action succeeded
        error: Error message if failed
    """
    logger = get_structured_logger("user_action")

    log_data = {
        "action": action,
        "resource_type": resource_type,
        "success": success,
    }

    if resource_id:
        log_data["resource_id"] = resource_id

    if details:
        log_data.update(details)

    if error:
        logger.error("User action failed", **log_data, error=error)
    else:
        logger.info("User action completed", **log_data)


def log_service_call(
    service_name: str,
    method: str,
    endpoint: str,
    duration: float,
    status_code: Optional[int] = None,
    error: Optional[str] = None,
) -> None:
    """
    Log service-to-service calls

    Args:
        service_name: Target service name
        method: HTTP method or RPC method
        endpoint: Endpoint or RPC name
        duration: Call duration in seconds
        status_code: HTTP status code
        error: Error message if failed
    """
    logger = get_structured_logger("service_call")

    log_data = {
        "target_service": service_name,
        "method": method,
        "endpoint": endpoint,
        "duration_ms": round(duration * 1000, 2),
    }

    if status_code:
        log_data["status_code"] = status_code

    if error:
        logger.error("Service call failed", **log_data, error=error)
    else:
        logger.info("Service call completed", **log_data)


def log_database_operation(
    operation: str,
    collection: str,
    duration: float,
    document_count: Optional[int] = None,
    error: Optional[str] = None,
) -> None:
    """
    Log database operations

    Args:
        operation: Operation type (e.g., "insert", "update", "find")
        collection: Collection/table name
        duration: Operation duration in seconds
        document_count: Number of documents affected
        error: Error message if failed
    """
    logger = get_structured_logger("database")

    log_data = {
        "operation": operation,
        "collection": collection,
        "duration_ms": round(duration * 1000, 2),
    }

    if document_count is not None:
        log_data["document_count"] = document_count

    if error:
        logger.error("Database operation failed", **log_data, error=error)
    else:
        logger.info("Database operation completed", **log_data)


# =============================================================================
# Traditional Logging Configuration
# =============================================================================


def setup_traditional_logging(log_level: str = "INFO") -> None:
    """
    Configure traditional file and console logging

    Args:
        log_level: Logging level for traditional logger
    """
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler with color support
    if HAS_COLORLOG:
        color_format = (
            "%(log_color)s%(asctime)s%(reset)s | "
            "%(log_color)s%(levelname)-8s%(reset)s | "
            "%(cyan)s%(name)-30s%(reset)s | "
            "%(message_log_color)s%(message)s%(reset)s"
        )
        console_formatter = colorlog.ColoredFormatter(
            color_format,
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG": "blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={
                "message": {
                    "DEBUG": "white",
                    "INFO": "white",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red",
                }
            },
        )
    else:
        log_format = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
        console_formatter = logging.Formatter(log_format, datefmt="%H:%M:%S")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handlers (without color codes)
    file_format = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
    file_formatter = logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")

    # General log file
    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Error log file
    error_handler = logging.FileHandler(log_dir / "error.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)

    # Configure external library loggers
    _configure_external_loggers()


def _configure_external_loggers() -> None:
    """Suppress noisy external library logs"""
    external_loggers = {
        "uvicorn.access": logging.WARNING,
        "uvicorn.error": logging.INFO,
        "httpx": logging.WARNING,
        "httpcore": logging.WARNING,
        "watchfiles": logging.WARNING,
        "watchfiles.main": logging.WARNING,
        "pymongo": logging.WARNING,
        "pymongo.serverSelection": logging.WARNING,
        "pymongo.connection": logging.WARNING,
        "pymongo.command": logging.WARNING,
        "pymongo.topology": logging.WARNING,
        "beanie": logging.INFO,
        "grpc": logging.WARNING,
    }

    for logger_name, level in external_loggers.items():
        logging.getLogger(logger_name).setLevel(level)


# =============================================================================
# Unified Setup (Recommended)
# =============================================================================


def setup_logging(
    service_name: str = "unknown-service",
    log_level: str = "INFO",
    environment: str = "development",
    enable_json: bool = False,
) -> None:
    """
    Configure integrated logging system (recommended entry point)

    Args:
        service_name: Service identifier for log tagging
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Runtime environment (development, production)
        enable_json: Enable JSON output (auto-enabled for production)

    Example:
        >>> from mysingle.core import setup_logging
        >>> setup_logging(service_name="strategy-service", environment="production")
    """
    # Environment-based defaults
    if environment == "production":
        enable_json = True
        if log_level == "DEBUG":
            log_level = "INFO"  # Override debug in production

    # Traditional logging (console + file)
    setup_traditional_logging(log_level=log_level)

    # Structured logging (structlog)
    configure_structured_logging(
        service_name=service_name,
        log_level=log_level,
        enable_json=enable_json,
    )

    # Log configuration summary
    logger = get_structured_logger(__name__)
    logger.info(
        "Logging system initialized",
        service=service_name,
        environment=environment,
        log_level=log_level,
        json_output=enable_json,
    )


# =============================================================================
# Public API
# =============================================================================

# Primary logger factory (recommended)
get_logger = get_structured_logger

__all__ = [
    # Setup
    "setup_logging",
    # Logger factories
    "get_logger",
    "get_structured_logger",
    # Context management
    "set_correlation_id",
    "set_user_id",
    "set_request_id",
    "get_correlation_id",
    "get_user_id",
    "get_request_id",
    "clear_logging_context",
    # Convenience functions
    "log_user_action",
    "log_service_call",
    "log_database_operation",
]

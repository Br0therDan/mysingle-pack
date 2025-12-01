"""
Tests for mysingle.core.logging module.
"""


import pytest
import structlog

from mysingle.core.logging import configure_logging, get_structured_logger


def test_configure_logging_development():
    """Test logging configuration in development mode."""
    configure_logging(
        service_name="test-service",
        log_level="DEBUG",
        environment="development",
    )

    logger = get_structured_logger(__name__)
    assert logger is not None
    assert isinstance(logger, structlog.stdlib.BoundLogger)


def test_configure_logging_production():
    """Test logging configuration in production mode."""
    configure_logging(
        service_name="test-service",
        log_level="INFO",
        environment="production",
    )

    logger = get_logger(__name__)
    assert logger is not None


def test_logger_with_context():
    """Test logger with context binding."""
    configure_logging(
        service_name="test-service",
        log_level="DEBUG",
        environment="development",
    )

    logger = get_logger(__name__)
    bound_logger = logger.bind(user_id="123", request_id="abc")

    assert bound_logger is not None
    # Actual logging test would require capturing output


def test_log_levels():
    """Test different log levels."""
    configure_logging(
        service_name="test-service",
        log_level="DEBUG",
        environment="development",
    )

    logger = get_logger(__name__)

    # These should not raise exceptions
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")


def test_get_logger_returns_bound_logger():
    """Test that get_logger returns a properly configured bound logger."""
    configure_logging(
        service_name="test-service",
        log_level="INFO",
        environment="development",
    )

    logger = get_logger("my_module")
    assert hasattr(logger, "bind")
    assert hasattr(logger, "info")
    assert hasattr(logger, "error")

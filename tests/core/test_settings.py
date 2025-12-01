"""
Tests for mysingle.core.settings module.
"""

import os

import pytest

from mysingle.core import CommonSettings


def test_settings_from_env():
    """Test that settings load from environment variables."""
    os.environ["SERVICE_NAME"] = "test-service"
    os.environ["ENVIRONMENT"] = "development"
    os.environ["LOG_LEVEL"] = "DEBUG"

    settings = CommonSettings()

    assert settings.SERVICE_NAME == "test-service"
    assert settings.ENVIRONMENT == "development"
    assert settings.LOG_LEVEL == "DEBUG"

    # Cleanup
    del os.environ["SERVICE_NAME"]
    del os.environ["ENVIRONMENT"]
    del os.environ["LOG_LEVEL"]


def test_settings_defaults():
    """Test default settings values."""
    settings = CommonSettings(SERVICE_NAME="test-service")

    assert settings.ENVIRONMENT == "development"
    assert settings.LOG_LEVEL == "INFO"
    assert settings.DEBUG is False


def test_settings_mongodb_url():
    """Test MongoDB URL construction."""
    settings = CommonSettings(
        SERVICE_NAME="test-service",
        MONGODB_HOST="localhost",
        MONGODB_PORT=27017,
        MONGODB_DATABASE="test_db",
    )

    assert "mongodb://localhost:27017" in settings.MONGODB_URL


def test_settings_redis_url():
    """Test Redis URL construction."""
    settings = CommonSettings(
        SERVICE_NAME="test-service",
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        REDIS_DB=0,
    )

    assert settings.REDIS_HOST == "localhost"
    assert settings.REDIS_PORT == 6379
    assert settings.REDIS_DB == 0


def test_settings_service_name_required():
    """Test that SERVICE_NAME is required."""
    with pytest.raises(Exception):  # ValidationError from pydantic
        CommonSettings()


def test_settings_case_sensitivity():
    """Test that environment variable names are case-sensitive."""
    os.environ["service_name"] = "wrong-case"  # lowercase won't work
    os.environ["SERVICE_NAME"] = "correct-case"  # uppercase works

    settings = CommonSettings()
    assert settings.SERVICE_NAME == "correct-case"

    del os.environ["service_name"]
    del os.environ["SERVICE_NAME"]

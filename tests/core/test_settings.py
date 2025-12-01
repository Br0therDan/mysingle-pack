"""
Tests for mysingle.core.settings module.
"""

import os

from mysingle.core import CommonSettings


def test_settings_from_env():
    """Test that settings load from environment variables."""
    os.environ["PROJECT_NAME"] = "Test Project"
    os.environ["ENVIRONMENT"] = "production"

    settings = CommonSettings()

    assert settings.PROJECT_NAME == "Test Project"
    assert settings.ENVIRONMENT == "production"

    # Cleanup
    del os.environ["PROJECT_NAME"]
    del os.environ["ENVIRONMENT"]


def test_settings_defaults():
    """Test default settings values."""
    settings = CommonSettings()

    assert settings.ENVIRONMENT == "development"
    assert settings.DEBUG is True
    assert settings.PROJECT_NAME == "MySingle Quant"  # Actual default value


def test_settings_mongodb_config():
    """Test MongoDB configuration."""
    settings = CommonSettings(
        MONGODB_SERVER="localhost:27017",
        MONGODB_USERNAME="testuser",
        MONGODB_PASSWORD="testpass",
    )

    assert settings.MONGODB_SERVER == "localhost:27017"
    assert settings.MONGODB_USERNAME == "testuser"


def test_settings_redis_url():
    """Test Redis URL configuration."""
    settings = CommonSettings(
        REDIS_URL="redis://localhost:6379/0",
    )

    assert settings.REDIS_URL == "redis://localhost:6379/0"


def test_settings_project_name_default():
    """Test that PROJECT_NAME has a default value."""
    settings = CommonSettings()

    # PROJECT_NAME has a default value
    assert settings.PROJECT_NAME is not None
    assert isinstance(settings.PROJECT_NAME, str)
    assert settings.PROJECT_NAME == "MySingle Quant"  # Actual default value


def test_settings_case_sensitivity():
    """Test that environment variable names are case-sensitive."""
    # Test that uppercase environment variable is used
    os.environ["PROJECT_NAME"] = "Correct Case Project"

    settings = CommonSettings()
    assert settings.PROJECT_NAME == "Correct Case Project"

    del os.environ["PROJECT_NAME"]

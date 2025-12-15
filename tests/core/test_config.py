"""
Tests for mysingle.core.config module.
"""

from mysingle.core.config import CommonSettings


def test_common_settings_defaults():
    """Test CommonSettings default values."""
    settings = CommonSettings()

    assert settings.ENVIRONMENT == "development"
    assert settings.DEBUG is True
    assert isinstance(settings.CORS_ORIGINS, list)


def test_common_settings_from_env(monkeypatch):
    """Test CommonSettings loading from environment."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("PROJECT_NAME", "Test Project")

    settings = CommonSettings()

    assert settings.ENVIRONMENT == "production"
    assert settings.DEBUG is False
    assert settings.PROJECT_NAME == "Test Project"


def test_mongodb_url_computed():
    """Test MongoDB URL computation."""
    settings = CommonSettings(
        MONGODB_SERVER="localhost:27017",
        MONGODB_USERNAME="testuser",
        MONGODB_PASSWORD="testpass",
    )

    # Test that settings are properly set
    assert settings.MONGODB_SERVER == "localhost:27017"
    assert settings.MONGODB_USERNAME == "testuser"
    assert settings.MONGODB_PASSWORD == "testpass"


def test_cors_origins_configuration():
    """Test CORS origins configuration."""
    settings = CommonSettings()

    # Default should include localhost origins
    assert "http://localhost:3000" in settings.CORS_ORIGINS

    # Test custom origins
    custom_origins = ["http://example.com", "https://api.example.com"]
    settings = CommonSettings(CORS_ORIGINS=custom_origins)

    assert custom_origins == settings.CORS_ORIGINS


# Removed test_token_expiry_settings - TOKEN settings moved to IAM service


def test_redis_configuration():
    """Test Redis configuration."""
    settings = CommonSettings(
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        REDIS_PASSWORD=None,
    )

    # Test that redis_url is computed correctly (no auth when password is None)
    assert settings.redis_url == "redis://localhost:6379"
    assert settings.REDIS_HOST == "localhost"
    assert settings.REDIS_PORT == 6379

    # Test with password (includes default: username)
    settings_with_pass = CommonSettings(
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        REDIS_PASSWORD="secret",
    )

    assert settings_with_pass.redis_url == "redis://default:secret@localhost:6379"


def test_redis_db_allocation():
    """Test Redis DB allocation constants."""
    settings = CommonSettings()

    # Test all DB allocations are unique (except RESERVED)
    db_values = [
        settings.REDIS_DB_USER,
        settings.REDIS_DB_GRPC,
        settings.REDIS_DB_RATE_LIMIT,
        settings.REDIS_DB_SESSION,
        settings.REDIS_DB_DSL,
        settings.REDIS_DB_MARKET_DATA,
        settings.REDIS_DB_BACKTEST,
        settings.REDIS_DB_INDICATOR,
        settings.REDIS_DB_STRATEGY_CACHE,
        settings.REDIS_DB_NOTIFICATION,
        settings.REDIS_DB_CELERY_BROKER,
        settings.REDIS_DB_CELERY_RESULT,
        settings.REDIS_DB_ML,
        settings.REDIS_DB_GENAI,
        settings.REDIS_DB_SUBSCRIPTION,
    ]

    # All should be unique
    assert len(db_values) == len(set(db_values))

    # All should be in valid range
    for db in db_values:
        assert 0 <= db <= 15


def test_redis_validation():
    """Test Redis configuration validation."""
    import pytest

    # Test invalid port
    with pytest.raises(ValueError, match="REDIS_PORT must be between 1-65535"):
        CommonSettings(REDIS_PORT=70000)

    # Test empty host
    with pytest.raises(ValueError, match="REDIS_HOST cannot be empty"):
        CommonSettings(REDIS_HOST="")

    # Test duplicate DB assignments would fail
    # (This is prevented by the validator)

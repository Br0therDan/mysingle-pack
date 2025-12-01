"""
Tests for mysingle.core.config module.
"""


from mysingle.core.config import CommonSettings, get_settings


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


def test_get_settings():
    """Test get_settings function."""
    settings = get_settings()

    assert isinstance(settings, CommonSettings)
    assert settings.ENVIRONMENT in ["development", "production", "staging"]


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


def test_token_expiry_settings():
    """Test token expiry configurations."""
    settings = CommonSettings()

    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS > 0
    assert settings.SERVICE_TOKEN_EXPIRE_MINUTES > 0
    assert settings.RESET_TOKEN_EXPIRE_MINUTES > 0
    assert settings.VERIFY_TOKEN_EXPIRE_MINUTES > 0


def test_redis_configuration():
    """Test Redis configuration."""
    settings = CommonSettings(
        REDIS_URL="redis://localhost:6379/1",
    )

    assert settings.REDIS_URL == "redis://localhost:6379/1"

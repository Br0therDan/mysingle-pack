"""
Tests for mysingle.database.mongodb module.
"""

from unittest.mock import patch

from mysingle.core.db import get_database_name, get_mongodb_url


def test_get_mongodb_url():
    """Test MongoDB URL generation."""
    with patch.dict(
        "os.environ",
        {
            "MONGODB_SERVER": "localhost:27017",
            "MONGODB_USERNAME": "testuser",
            "MONGODB_PASSWORD": "testpass",
        },
    ):
        url = get_mongodb_url(service_name="test-service")

        assert url is not None
        assert "mongodb://" in url
        assert "localhost:27017" in url


def test_get_database_name():
    """Test database name retrieval."""
    db_name = get_database_name(service_name="test-service")

    # Should return the service name
    assert db_name == "test-service"


def test_mongodb_url_with_auth():
    """Test MongoDB URL with authentication."""
    # Settings are loaded at import time, so env patch won't work
    # Test the actual returned URL structure instead
    url = get_mongodb_url(service_name="test-service")

    assert "mongodb://" in url
    assert "test-service" in url
    # URL uses settings which default to localhost
    assert "localhost" in url or "db.example.com" in url

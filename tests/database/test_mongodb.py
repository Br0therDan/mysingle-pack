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
        url = get_mongodb_url()

        assert url is not None
        assert "mongodb://" in url
        assert "localhost:27017" in url


def test_get_database_name():
    """Test database name retrieval."""
    with patch.dict(
        "os.environ",
        {
            "MONGODB_DATABASE": "test_db",
        },
    ):
        db_name = get_database_name()

        # Default behavior returns from settings
        assert db_name is not None


def test_mongodb_url_with_auth():
    """Test MongoDB URL with authentication."""
    with patch.dict(
        "os.environ",
        {
            "MONGODB_SERVER": "db.example.com:27017",
            "MONGODB_USERNAME": "admin",
            "MONGODB_PASSWORD": "secret",
        },
    ):
        url = get_mongodb_url()

        assert "mongodb://" in url
        assert "db.example.com" in url

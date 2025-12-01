"""
Test configuration and fixtures for mysingle package tests.
"""

import os
from unittest.mock import Mock

import pytest
from beanie import PydanticObjectId

# Enable auth bypass for testing
os.environ["MYSINGLE_AUTH_BYPASS"] = "true"
os.environ["ENVIRONMENT"] = "development"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_mongodb_client():
    """
    Mock MongoDB client fixture for testing.
    """
    client = Mock()
    client.test_db = Mock()
    return client


@pytest.fixture
def mock_user():
    """Mock user for auth testing."""
    from mysingle.auth.models import User

    # Use model_construct to bypass Beanie initialization
    user = User.model_construct(
        id=PydanticObjectId("507f1f77bcf86cd799439011"),
        email="test@example.com",
        hashed_password="$2b$12$test_hashed_password",
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )
    return user


@pytest.fixture
def mock_admin_user():
    """Mock admin user for auth testing."""
    from mysingle.auth.models import User

    user = User.model_construct(
        id=PydanticObjectId("507f1f77bcf86cd799439012"),
        email="admin@example.com",
        hashed_password="$2b$12$test_admin_hashed_password",
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )
    return user


@pytest.fixture
def test_settings():
    """Test settings override."""
    from mysingle.core.config import CommonSettings

    return CommonSettings(
        ENVIRONMENT="development",
        DEBUG=True,
        # MongoDB settings
        MONGODB_SERVER="localhost:27017",
        MONGODB_USERNAME="test",
        MONGODB_PASSWORD="test",
        # Redis settings
        REDIS_URL="redis://localhost:6379/0",
    )


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing DSL and data operations."""
    import pandas as pd

    return pd.DataFrame(
        {
            "close": [100.0, 101.0, 102.0, 103.0, 104.0, 105.0],
            "open": [99.0, 100.0, 101.0, 102.0, 103.0, 104.0],
            "high": [101.0, 102.0, 103.0, 104.0, 105.0, 106.0],
            "low": [98.0, 99.0, 100.0, 101.0, 102.0, 103.0],
            "volume": [1000, 1100, 1200, 1300, 1400, 1500],
        }
    )

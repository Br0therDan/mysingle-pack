"""
Test configuration and fixtures for mysingle package tests.
"""

import os
from typing import AsyncGenerator
from unittest.mock import Mock

import pytest
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

# Enable auth bypass for testing
os.environ["MYSINGLE_AUTH_BYPASS"] = "true"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mongodb_client() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """
    MongoDB client fixture for testing using mongomock.
    """
    import mongomock

    # Use mongomock for testing (no real MongoDB needed)
    client = mongomock.MongoClient()
    yield client
    # No cleanup needed for mongomock
    client.close()


@pytest.fixture
async def init_test_beanie(mongodb_client):
    """
    Initialize Beanie with test database.
    Note: mongomock has limitations with Beanie, so some tests may need mocking.
    """
    from mysingle.base.documents import BaseDoc, BaseTimeDoc, BaseTimeDocWithUserId

    # For mongomock, we skip Beanie initialization
    # Tests should mock Beanie operations when needed
    yield


@pytest.fixture
def mock_user():
    """Mock user for auth testing."""
    from beanie import PydanticObjectId

    # Create a mock User-like object without requiring Beanie
    user = Mock()
    user.id = PydanticObjectId("507f1f77bcf86cd799439011")
    user.email = "test@example.com"
    user.hashed_password = "$2b$12$test_hashed_password"
    user.is_active = True
    user.is_verified = True
    return user


@pytest.fixture
def test_settings():
    """Test settings override."""
    from mysingle.core.config import CommonSettings

    return CommonSettings(
        SERVICE_NAME="test-service",
        ENVIRONMENT="test",
        LOG_LEVEL="DEBUG",
        # MongoDB settings
        MONGODB_URL="mongodb://localhost:27017",
        MONGODB_DATABASE="test_db",
        # Redis settings (optional)
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
    )


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing DSL and data operations."""
    import pandas as pd

    return pd.DataFrame(
        {
            "close": [100, 101, 102, 103, 104, 105],
            "open": [99, 100, 101, 102, 103, 104],
            "high": [101, 102, 103, 104, 105, 106],
            "low": [98, 99, 100, 101, 102, 103],
            "volume": [1000, 1100, 1200, 1300, 1400, 1500],
        }
    )

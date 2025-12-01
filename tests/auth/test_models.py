"""
Tests for mysingle.auth.models module.
"""

import pytest
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient

from mysingle.auth.models import User


@pytest.fixture
async def init_db():
    """Initialize test database."""
    client = AsyncMongoMockClient()
    await init_beanie(
        database=client.test_db,
        document_models=[User],
    )
    yield
    # Cleanup
    await client.drop_database("test_db")


@pytest.mark.asyncio
async def test_user_model_creation(init_db):
    """Test User model creation."""
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$test_hash",
        is_active=True,
        is_verified=False,
        is_superuser=False,
    )

    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.is_verified is False
    assert user.is_superuser is False


@pytest.mark.asyncio
async def test_user_model_defaults(init_db):
    """Test User model default values."""
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$test_hash",
    )

    # Check default values
    assert user.is_active is True
    assert user.is_verified is False
    assert user.is_superuser is False


@pytest.mark.asyncio
async def test_user_model_with_optional_fields(init_db):
    """Test User model with optional fields."""
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$test_hash",
        full_name="Test User",
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )

    assert user.full_name == "Test User"
    assert user.is_verified is True


@pytest.mark.asyncio
async def test_user_model_serialization(init_db):
    """Test User model serialization."""
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$test_hash",
        full_name="Test User",
    )

    user_dict = user.model_dump()

    assert user_dict["email"] == "test@example.com"
    assert "hashed_password" in user_dict
    assert user_dict["full_name"] == "Test User"


@pytest.mark.asyncio
async def test_user_model_exclude_password(init_db):
    """Test User model serialization excluding password."""
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$test_hash",
    )

    user_dict = user.model_dump(exclude={"hashed_password"})

    assert "hashed_password" not in user_dict
    assert user_dict["email"] == "test@example.com"

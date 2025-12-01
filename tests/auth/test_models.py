"""
Tests for mysingle.auth.models module.
"""


from mysingle.auth.models import User


def test_user_model_creation():
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


def test_user_model_defaults():
    """Test User model default values."""
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$test_hash",
    )

    # Check default values
    assert user.is_active is True
    assert user.is_verified is False
    assert user.is_superuser is False


def test_user_model_with_optional_fields():
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


def test_user_model_serialization():
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


def test_user_model_exclude_password():
    """Test User model serialization excluding password."""
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$test_hash",
    )

    user_dict = user.model_dump(exclude={"hashed_password"})

    assert "hashed_password" not in user_dict
    assert user_dict["email"] == "test@example.com"

"""
Tests for mysingle.auth.security module.
"""

from mysingle.auth.security.password import PasswordHelper


def test_password_hashing():
    """Test password hashing."""
    helper = PasswordHelper()
    password = "test_password_123"
    hashed = helper.hash(password)

    assert hashed is not None
    assert hashed != password
    assert len(hashed) > 0


def test_password_verification_success():
    """Test successful password verification."""
    helper = PasswordHelper()
    password = "test_password_123"
    hashed = helper.hash(password)

    verified, _ = helper.verify_and_update(password, hashed)
    assert verified is True


def test_password_verification_failure():
    """Test failed password verification."""
    helper = PasswordHelper()
    password = "test_password_123"
    wrong_password = "wrong_password"
    hashed = helper.hash(password)

    verified, _ = helper.verify_and_update(wrong_password, hashed)
    assert verified is False


def test_different_passwords_different_hashes():
    """Test that different passwords produce different hashes."""
    helper = PasswordHelper()
    password1 = "password1"
    password2 = "password2"

    hash1 = helper.hash(password1)
    hash2 = helper.hash(password2)

    assert hash1 != hash2


def test_same_password_different_hashes():
    """Test that same password produces different hashes (due to salt)."""
    helper = PasswordHelper()
    password = "test_password_123"

    hash1 = helper.hash(password)
    hash2 = helper.hash(password)

    # Hashes should be different due to salt
    assert hash1 != hash2

    # But both should verify correctly
    verified1, _ = helper.verify_and_update(password, hash1)
    verified2, _ = helper.verify_and_update(password, hash2)
    assert verified1 is True
    assert verified2 is True


def test_password_generation():
    """Test password generation."""
    helper = PasswordHelper()

    generated = helper.generate()

    assert generated is not None
    assert isinstance(generated, str)
    assert len(generated) > 0

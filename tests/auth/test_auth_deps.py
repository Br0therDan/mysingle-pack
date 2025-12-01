"""
Tests for mysingle.auth.deps module.
"""

from unittest.mock import Mock

import pytest
from fastapi import HTTPException, Request

from mysingle.auth.deps import (
    get_current_active_user,
    get_current_active_verified_user,
    get_current_user,
)


@pytest.fixture
def mock_request():
    """Mock FastAPI request."""
    request = Mock(spec=Request)
    request.headers = {}
    request.state = Mock()
    return request


@pytest.mark.asyncio
async def test_get_current_user_with_bypass(mock_request, mock_user):
    """Test get_current_user with auth bypass enabled."""
    # Auth bypass is enabled in conftest.py
    mock_request.state.user = mock_user

    user = await get_current_user(mock_request)

    assert user is not None
    assert user.email == mock_user.email


@pytest.mark.asyncio
async def test_get_current_active_user_with_bypass(mock_request, mock_user):
    """Test get_current_active_user with auth bypass."""
    mock_request.state.user = mock_user

    user = await get_current_active_user(mock_request)

    assert user is not None
    assert user.is_active is True


@pytest.mark.asyncio
async def test_get_current_active_verified_user_with_bypass(mock_request, mock_user):
    """Test get_current_active_verified_user with auth bypass."""
    mock_request.state.user = mock_user

    user = await get_current_active_verified_user(mock_request)

    assert user is not None
    assert user.is_active is True
    assert user.is_verified is True


@pytest.mark.asyncio
async def test_get_current_user_inactive_user(mock_request, mock_user):
    """Test get_current_active_user with inactive user."""
    mock_user.is_active = False
    mock_request.state.user = mock_user

    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(mock_request)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_get_current_verified_user_unverified(mock_request, mock_user):
    """Test get_current_active_verified_user with unverified user."""
    mock_user.is_verified = False
    mock_request.state.user = mock_user

    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_verified_user(mock_request)

    assert exc_info.value.status_code == 403

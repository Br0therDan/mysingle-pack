"""
Tests for mysingle.auth.deps module.
"""

from unittest.mock import Mock

import pytest
from fastapi import Request

from mysingle.auth import (
    get_user_id,
)


@pytest.fixture
def mock_request():
    """Mock FastAPI request."""
    request = Mock(spec=Request)
    request.headers = {}
    request.state = Mock()
    return request


@pytest.mark.asyncio
async def test_get_user_id_with_kong_headers(mock_request, mock_user):
    """Test get_user_id with Kong Gateway headers."""
    # Simulate Kong Gateway headers set by middleware
    mock_request.state.user_id = str(mock_user.id)
    mock_request.state.email = mock_user.email

    user_id = get_user_id(mock_request)

    assert user_id is not None
    assert user_id == str(mock_user.id)


# Note: get_verified_user_id removed - IAM login already validates is_verified
# All authenticated users are active + verified

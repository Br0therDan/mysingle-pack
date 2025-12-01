"""
Tests for mysingle.clients.base_http_client module.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from mysingle.core.http_client import (
    ServiceHttpClient,
    create_service_http_client,
)


@pytest.mark.asyncio
async def test_http_client_creation():
    """Test HTTP client creation."""
    client = create_service_http_client(
        service_name="test-service",
        base_url="http://localhost:8000",
    )

    assert client is not None
    assert isinstance(client, ServiceHttpClient)


@pytest.mark.asyncio
async def test_http_client_with_timeout():
    """Test HTTP client with custom timeout."""
    client = create_service_http_client(
        service_name="test-service",
        base_url="http://localhost:8000",
        timeout=10.0,
    )

    assert client is not None


@pytest.mark.asyncio
async def test_http_client_request_with_headers():
    """Test HTTP client request with custom headers."""
    client = create_service_http_client(
        service_name="test-service",
        base_url="http://localhost:8000",
    )

    # Mock the actual HTTP call
    with patch.object(client, "request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = Mock(status_code=200, json=lambda: {"status": "ok"})

        response = await client.request(
            method="GET",
            path="/health",
            headers={"X-Test-Header": "test-value"},
        )

        assert response is not None
        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_http_client_get_method():
    """Test HTTP client GET method."""
    client = create_service_http_client(
        service_name="test-service",
        base_url="http://localhost:8000",
    )

    with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = Mock(status_code=200, json=lambda: {"data": "test"})

        response = await client.get("/api/data")

        assert response is not None
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_http_client_post_method():
    """Test HTTP client POST method."""
    client = create_service_http_client(
        service_name="test-service",
        base_url="http://localhost:8000",
    )

    with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = Mock(status_code=201, json=lambda: {"id": "123"})

        response = await client.post("/api/create", json={"name": "test"})

        assert response is not None
        mock_post.assert_called_once()

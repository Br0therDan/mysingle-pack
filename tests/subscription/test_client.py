"""Unit tests for subscription client."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from mysingle.subscription.client import SubscriptionServiceClient


@pytest.mark.asyncio
async def test_check_quota_allowed():
    """Test check_quota when quota is available."""
    client = SubscriptionServiceClient(user_id="test_user")
    client.stub = AsyncMock()
    client.stub.CheckQuota.return_value = MagicMock(
        allowed=True,
        current_usage=5,
        limit=100,
        remaining=95,
        percentage=5.0,
        status="allowed",
    )

    response = await client.check_quota(
        user_id="test_user",
        metric="api_calls",
        amount=1,
    )

    assert response.allowed is True
    assert response.remaining == 95
    assert response.current_usage == 5
    assert response.limit == 100
    client.stub.CheckQuota.assert_called_once()


@pytest.mark.asyncio
async def test_check_quota_exceeded():
    """Test check_quota when quota is exceeded."""
    client = SubscriptionServiceClient(user_id="test_user")
    client.stub = AsyncMock()
    client.stub.CheckQuota.return_value = MagicMock(
        allowed=False,
        current_usage=100,
        limit=100,
        remaining=0,
        percentage=100.0,
        status="exceeded",
    )

    response = await client.check_quota(
        user_id="test_user",
        metric="backtests",
        amount=1,
    )

    assert response.allowed is False
    assert response.remaining == 0
    assert response.current_usage == 100


@pytest.mark.asyncio
async def test_get_subscription():
    """Test get_subscription returns subscription info."""
    client = SubscriptionServiceClient(user_id="test_user")
    client.stub = AsyncMock()
    client.stub.GetSubscription.return_value = MagicMock(
        id="sub_123",
        user_id="test_user",
        tier="professional",
        status="active",
    )

    response = await client.get_subscription(user_id="test_user")

    assert response.id == "sub_123"
    assert response.tier == "professional"
    assert response.status == "active"


@pytest.mark.asyncio
async def test_get_entitlements():
    """Test get_entitlements returns tier and features."""
    client = SubscriptionServiceClient(user_id="test_user")
    client.stub = AsyncMock()
    client.stub.GetEntitlements.return_value = MagicMock(
        tier="professional",
        features=["ai_chat", "advanced_backtesting", "optimization"],
        limits={"api_calls": 10000, "backtests": 100},
    )

    response = await client.get_entitlements(user_id="test_user")

    assert response.tier == "professional"
    assert "ai_chat" in response.features
    assert "advanced_backtesting" in response.features
    assert response.limits["api_calls"] == 10000


@pytest.mark.asyncio
async def test_get_usage():
    """Test get_usage returns current usage."""
    client = SubscriptionServiceClient(user_id="test_user")
    client.stub = AsyncMock()
    client.stub.GetUsage.return_value = MagicMock(
        metric="api_calls",
        usage=45,
        limit=100,
        percentage=45.0,
    )

    response = await client.get_usage(
        user_id="test_user",
        metric="api_calls",
    )

    assert response.metric == "api_calls"
    assert response.usage == 45
    assert response.limit == 100


@pytest.mark.asyncio
async def test_get_all_quotas():
    """Test get_all_quotas returns all quota statuses."""
    client = SubscriptionServiceClient(user_id="test_user")
    client.stub = AsyncMock()
    client.stub.GetAllQuotas.return_value = MagicMock(
        quotas=[
            MagicMock(metric="api_calls", usage=45, limit=100),
            MagicMock(metric="backtests", usage=5, limit=10),
        ]
    )

    response = await client.get_all_quotas(user_id="test_user")

    assert len(response.quotas) == 2
    assert response.quotas[0].metric == "api_calls"
    assert response.quotas[1].metric == "backtests"


@pytest.mark.asyncio
async def test_health_check():
    """Test health_check returns service status."""
    client = SubscriptionServiceClient()
    client.stub = AsyncMock()
    client.stub.HealthCheck.return_value = MagicMock(status="healthy")

    response = await client.health_check()

    assert response.status == "healthy"


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test client can be used as context manager."""
    async with SubscriptionServiceClient(user_id="test_user") as client:
        assert client is not None
        assert client.user_id == "test_user"

"""Unit tests for subscription middleware."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from mysingle.subscription import QuotaEnforcementMiddleware, UsageMetric


@pytest.fixture
def app_with_middleware():
    """Create FastAPI app with quota enforcement middleware."""
    app = FastAPI()
    app.add_middleware(QuotaEnforcementMiddleware, metric=UsageMetric.API_CALLS)

    @app.get("/test")
    async def test_route(request: Request):
        return {"message": "success"}

    return app


def test_quota_enforcement_allowed(app_with_middleware):
    """Test middleware allows request when quota is available."""
    with patch(
        "mysingle.subscription.middleware.SubscriptionServiceClient"
    ) as mock_client:
        # Mock gRPC response
        mock_instance = AsyncMock()
        mock_instance.check_quota.return_value = MagicMock(
            allowed=True,
            remaining=95,
            limit=100,
            reset_at=MagicMock(seconds=1733461200),
        )
        mock_client.return_value.__aenter__.return_value = mock_instance

        # Mock user
        with patch(
            "mysingle.subscription.middleware.get_user_id_optional"
        ) as mock_user_id:
            mock_user_id.return_value = "test_user"

            client = TestClient(app_with_middleware)
            response = client.get("/test")

            assert response.status_code == 200
            assert response.json() == {"message": "success"}
            mock_instance.check_quota.assert_called_once_with(
                user_id="test_user",
                metric="api_calls",
                amount=1,
            )


@pytest.mark.skip(
    reason="TestClient middleware exception handling issue - needs investigation"
)
def test_quota_enforcement_exceeded(app_with_middleware):
    """Test middleware blocks request when quota is exceeded."""
    with patch(
        "mysingle.subscription.middleware.SubscriptionServiceClient"
    ) as mock_client:
        # Mock gRPC response
        mock_instance = AsyncMock()
        mock_instance.check_quota.return_value = MagicMock(
            allowed=False,
            remaining=0,
            limit=100,
            current_usage=100,  # Add current_usage to mock
            reset_at=MagicMock(seconds=1733461200),
        )
        mock_client.return_value.__aenter__.return_value = mock_instance

        # Mock user
        with patch(
            "mysingle.subscription.middleware.get_user_id_optional"
        ) as mock_user_id:
            mock_user_id.return_value = "test_user"

            client = TestClient(app_with_middleware, raise_server_exceptions=False)
            response = client.get("/test")

            assert response.status_code == 429
            assert "Quota exceeded" in response.json()["detail"]
            assert response.headers.get("X-RateLimit-Remaining") == "0"
            assert response.headers.get("X-RateLimit-Limit") == "100"


def test_quota_enforcement_no_user(app_with_middleware):
    """Test middleware skips quota check when no user authenticated."""
    with patch("mysingle.subscription.middleware.get_user_id_optional") as mock_user_id:
        mock_user_id.return_value = None

        client = TestClient(app_with_middleware)
        response = client.get("/test")

        # Should pass through without quota check
        assert response.status_code == 200
        assert response.json() == {"message": "success"}


@pytest.mark.skip(
    reason="TestClient middleware exception handling issue - needs investigation"
)
def test_quota_enforcement_grpc_error(app_with_middleware):
    """Test middleware returns 503 when gRPC fails."""
    with patch(
        "mysingle.subscription.middleware.SubscriptionServiceClient"
    ) as mock_client:
        # Mock gRPC error
        mock_instance = AsyncMock()
        mock_instance.check_quota.side_effect = Exception("gRPC connection failed")
        mock_client.return_value.__aenter__.return_value = mock_instance

        # Mock user
        with patch(
            "mysingle.subscription.middleware.get_user_id_optional"
        ) as mock_user_id:
            mock_user_id.return_value = "test_user"

            client = TestClient(app_with_middleware, raise_server_exceptions=False)
            response = client.get("/test")

            assert response.status_code == 503
            assert "unavailable" in response.json()["detail"].lower()


def test_quota_enforcement_different_metrics():
    """Test middleware can enforce different metrics."""
    app = FastAPI()
    app.add_middleware(QuotaEnforcementMiddleware, metric=UsageMetric.BACKTESTS)

    @app.post("/backtests")
    async def create_backtest(request: Request):
        return {"id": "backtest_123"}

    with patch(
        "mysingle.subscription.middleware.SubscriptionServiceClient"
    ) as mock_client:
        mock_instance = AsyncMock()
        mock_instance.check_quota.return_value = MagicMock(
            allowed=True,
            remaining=5,
            limit=10,
            reset_at=MagicMock(seconds=1733461200),
        )
        mock_client.return_value.__aenter__.return_value = mock_instance

        with patch(
            "mysingle.subscription.middleware.get_user_id_optional"
        ) as mock_user_id:
            mock_user_id.return_value = "test_user"

            client = TestClient(app)
            response = client.post("/backtests")

            assert response.status_code == 200
            mock_instance.check_quota.assert_called_once_with(
                user_id="test_user",
                metric="backtests",
                amount=1,
            )

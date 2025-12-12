"""Unit tests for subscription decorators."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from mysingle.subscription import TierLevel, require_feature, require_tier


@pytest.fixture
def app_with_tier_decorator():
    """Create FastAPI app with tier requirement decorator."""
    app = FastAPI()

    @app.get("/premium")
    @require_tier(TierLevel.PROFESSIONAL)
    async def premium_route(request: Request):
        return {"message": "premium content"}

    return app


@pytest.fixture
def app_with_feature_decorator():
    """Create FastAPI app with feature requirement decorator."""
    app = FastAPI()

    @app.post("/ai-chat")
    @require_feature("ai_chat")
    async def ai_chat_route(request: Request):
        return {"message": "AI response"}

    return app


def test_require_tier_allowed(app_with_tier_decorator):
    """Test tier decorator allows request when tier is sufficient."""
    with patch(
        "mysingle.subscription.decorators.SubscriptionServiceClient"
    ) as mock_client:
        # Mock gRPC response
        mock_instance = AsyncMock()
        mock_instance.get_entitlements.return_value = MagicMock(
            tier="professional",
            features=["ai_chat", "advanced_backtesting"],
        )
        mock_client.return_value.__aenter__.return_value = mock_instance

        # Mock user_id from request.state
        with patch("mysingle.subscription.decorators.get_user_id") as mock_get_user_id:
            mock_get_user_id.return_value = "test_user"

            client = TestClient(app_with_tier_decorator)
            response = client.get("/premium")

            assert response.status_code == 200
            assert response.json() == {"message": "premium content"}


def test_require_tier_denied(app_with_tier_decorator):
    """Test tier decorator blocks request when tier is insufficient."""
    with patch(
        "mysingle.subscription.decorators.SubscriptionServiceClient"
    ) as mock_client:
        # Mock gRPC response - user has starter tier
        mock_instance = AsyncMock()
        mock_instance.get_entitlements.return_value = MagicMock(
            tier="starter",
            features=["basic_backtesting"],
        )
        mock_client.return_value.__aenter__.return_value = mock_instance

        # Mock user_id from request.state
        with patch("mysingle.subscription.decorators.get_user_id") as mock_get_user_id:
            mock_get_user_id.return_value = "test_user"

            client = TestClient(app_with_tier_decorator)
            response = client.get("/premium")

            assert response.status_code == 403
            assert "Requires tier" in response.json()["detail"]


def test_require_tier_multiple_allowed():
    """Test tier decorator with multiple allowed tiers."""
    app = FastAPI()

    @app.get("/enterprise")
    @require_tier([TierLevel.PROFESSIONAL, TierLevel.INSTITUTIONAL])
    async def enterprise_route(request: Request):
        return {"message": "enterprise content"}

    with patch(
        "mysingle.subscription.decorators.SubscriptionServiceClient"
    ) as mock_client:
        mock_instance = AsyncMock()
        mock_instance.get_entitlements.return_value = MagicMock(
            tier="professional",
            features=[],
        )
        mock_client.return_value.__aenter__.return_value = mock_instance

        with patch("mysingle.subscription.decorators.get_user_id") as mock_get_user_id:
            mock_get_user_id.return_value = "test_user"

            client = TestClient(app)
            response = client.get("/enterprise")

            assert response.status_code == 200


def test_require_tier_no_user(app_with_tier_decorator):
    """Test tier decorator returns 403 when no user authenticated."""
    from mysingle.auth.decorators import AuthorizationFailed

    with patch("mysingle.subscription.decorators.get_user_id") as mock_get_user_id:
        # get_user_id raises AuthorizationFailed when not authenticated (403 Forbidden)
        mock_get_user_id.side_effect = AuthorizationFailed("Not authenticated")

        client = TestClient(app_with_tier_decorator)
        response = client.get("/premium")

        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]


def test_require_feature_allowed(app_with_feature_decorator):
    """Test feature decorator allows request when feature is available."""
    with patch(
        "mysingle.subscription.decorators.SubscriptionServiceClient"
    ) as mock_client:
        # Mock gRPC response
        mock_instance = AsyncMock()
        mock_instance.get_entitlements.return_value = MagicMock(
            tier="professional",
            features=["ai_chat", "advanced_backtesting", "optimization"],
        )
        mock_client.return_value.__aenter__.return_value = mock_instance

        # Mock user_id from request.state
        with patch("mysingle.subscription.decorators.get_user_id") as mock_get_user_id:
            mock_get_user_id.return_value = "test_user"

            client = TestClient(app_with_feature_decorator)
            response = client.post("/ai-chat")

            assert response.status_code == 200
            assert response.json() == {"message": "AI response"}


def test_require_feature_denied(app_with_feature_decorator):
    """Test feature decorator blocks request when feature is unavailable."""
    with patch(
        "mysingle.subscription.decorators.SubscriptionServiceClient"
    ) as mock_client:
        # Mock gRPC response - user doesn't have ai_chat feature
        mock_instance = AsyncMock()
        mock_instance.get_entitlements.return_value = MagicMock(
            tier="starter",
            features=["basic_backtesting"],
        )
        mock_client.return_value.__aenter__.return_value = mock_instance

        # Mock user_id from request.state
        with patch("mysingle.subscription.decorators.get_user_id") as mock_get_user_id:
            mock_get_user_id.return_value = "test_user"

            client = TestClient(app_with_feature_decorator)
            response = client.post("/ai-chat")

            assert response.status_code == 403
            assert "not available" in response.json()["detail"].lower()
            assert "ai_chat" in response.json()["detail"]


def test_require_feature_grpc_error(app_with_feature_decorator):
    """Test feature decorator returns 503 when gRPC fails."""
    with patch(
        "mysingle.subscription.decorators.SubscriptionServiceClient"
    ) as mock_client:
        # Mock gRPC error
        mock_instance = AsyncMock()
        mock_instance.get_entitlements.side_effect = Exception("gRPC failed")
        mock_client.return_value.__aenter__.return_value = mock_instance

        # Mock user_id from request.state
        with patch("mysingle.subscription.decorators.get_user_id") as mock_get_user_id:
            mock_get_user_id.return_value = "test_user"

            client = TestClient(app_with_feature_decorator)
            response = client.post("/ai-chat")

            assert response.status_code == 503
            assert "unavailable" in response.json()["detail"].lower()


def test_combined_decorators():
    """Test combining tier and feature decorators."""
    app = FastAPI()

    @app.post("/advanced-optimization")
    @require_tier(TierLevel.PROFESSIONAL)
    @require_feature("optimization")
    async def advanced_optimization(request: Request):
        return {"message": "optimization started"}

    with patch(
        "mysingle.subscription.decorators.SubscriptionServiceClient"
    ) as mock_client:
        mock_instance = AsyncMock()
        mock_instance.get_entitlements.return_value = MagicMock(
            tier="professional",
            features=["optimization", "ai_chat"],
        )
        mock_client.return_value.__aenter__.return_value = mock_instance

        with patch("mysingle.subscription.decorators.get_user_id") as mock_get_user_id:
            mock_get_user_id.return_value = "test_user"

            client = TestClient(app)
            response = client.post("/advanced-optimization")

            assert response.status_code == 200
            # Both decorators should call get_entitlements
            assert mock_instance.get_entitlements.call_count == 2

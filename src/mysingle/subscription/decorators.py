"""Feature gate decorators (gRPC wrapper).

These decorators wrap gRPC calls to Subscription Service for feature gating.
All entitlement logic resides in Subscription Service.
"""

from functools import wraps
from typing import Callable, List, Union

from fastapi import HTTPException, Request

from mysingle.auth import get_user_id
from mysingle.core.logging import get_structured_logger
from mysingle.subscription.client import SubscriptionServiceClient
from mysingle.subscription.models import TierLevel

logger = get_structured_logger(__name__)


def require_tier(required_tier: Union[TierLevel, List[TierLevel]]) -> Callable:
    """Require minimum tier level (gRPC wrapper).

    Calls Subscription Service's GetEntitlements gRPC API to check user's tier.

    Args:
        required_tier: Minimum tier level or list of allowed tiers

    Returns:
        Decorator function

    Example:
        from mysingle.subscription import require_tier, TierLevel

        @router.get("/premium-feature")
        @require_tier(TierLevel.PROFESSIONAL)
        async def premium_feature(request: Request):
            ...

        @router.get("/enterprise-feature")
        @require_tier([TierLevel.PROFESSIONAL, TierLevel.INSTITUTIONAL])
        async def enterprise_feature(request: Request):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user_id = get_user_id(request)

            # Call Subscription Service via gRPC
            async with SubscriptionServiceClient(user_id=user_id) as client:
                try:
                    response = await client.get_entitlements(user_id)
                    user_tier = TierLevel(response.tier)
                except Exception as e:
                    logger.error(
                        "Failed to get entitlements",
                        extra={
                            "user_id": user_id,
                            "error": str(e),
                        },
                        exc_info=True,
                    )
                    raise HTTPException(
                        status_code=503,
                        detail="Subscription service unavailable",
                    )

            # Check tier
            allowed_tiers = (
                [required_tier]
                if isinstance(required_tier, TierLevel)
                else required_tier
            )

            if user_tier not in allowed_tiers:
                logger.warning(
                    "Tier requirement not met",
                    extra={
                        "user_id": user_id,
                        "user_tier": user_tier.value,
                        "required_tiers": [t.value for t in allowed_tiers],
                    },
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"Requires tier: {', '.join([t.value for t in allowed_tiers])}",
                )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


def require_feature(feature: str) -> Callable:
    """Require specific feature access (gRPC wrapper).

    Calls Subscription Service's GetEntitlements gRPC API to check user's features.

    Args:
        feature: Feature name (e.g., "ai_chat", "advanced_backtesting")

    Returns:
        Decorator function

    Example:
        from mysingle.subscription import require_feature

        @router.post("/ai-chat")
        @require_feature("ai_chat")
        async def ai_chat(request: Request):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user_id = get_user_id(request)

            # Call Subscription Service via gRPC
            async with SubscriptionServiceClient(user_id=user_id) as client:
                try:
                    response = await client.get_entitlements(user_id)
                except Exception as e:
                    logger.error(
                        "Failed to get entitlements",
                        extra={
                            "user_id": user_id,
                            "error": str(e),
                        },
                        exc_info=True,
                    )
                    raise HTTPException(
                        status_code=503,
                        detail="Subscription service unavailable",
                    )

            # Check feature
            if feature not in response.features:
                logger.warning(
                    "Feature not available",
                    extra={
                        "user_id": user_id,
                        "feature": feature,
                        "available_features": list(response.features),
                    },
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"Feature '{feature}' not available in your tier",
                )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator

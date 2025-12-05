"""Quota enforcement middleware (gRPC wrapper).

This middleware wraps gRPC calls to Subscription Service for quota checking.
All quota enforcement logic resides in Subscription Service.
"""

from typing import Callable

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from mysingle.auth import get_current_user
from mysingle.core.logging import get_structured_logger
from mysingle.subscription.client import SubscriptionServiceClient
from mysingle.subscription.models import UsageMetric

logger = get_structured_logger(__name__)


class QuotaEnforcementMiddleware(BaseHTTPMiddleware):
    """Quota enforcement middleware (gRPC wrapper).

    Automatically checks quota via Subscription Service gRPC API before processing requests.
    Real quota checking logic is in Subscription Service.

    Example:
        from fastapi import FastAPI
        from mysingle.subscription import QuotaEnforcementMiddleware, UsageMetric

        app = FastAPI()
        app.add_middleware(
            QuotaEnforcementMiddleware,
            metric=UsageMetric.API_CALLS,
        )

    Attributes:
        metric: Usage metric to enforce (e.g., UsageMetric.API_CALLS)
    """

    def __init__(self, app, metric: UsageMetric):
        """Initialize quota enforcement middleware.

        Args:
            app: FastAPI application
            metric: Usage metric to enforce
        """
        super().__init__(app)
        self.metric = metric

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check quota via gRPC before processing request.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response

        Raises:
            HTTPException(429): If quota exceeded
            HTTPException(503): If Subscription Service unavailable
        """
        user = get_current_user(request)
        if not user:
            # No user authenticated - skip quota check
            return await call_next(request)

        # Call Subscription Service via gRPC
        async with SubscriptionServiceClient(user_id=str(user.id)) as client:
            try:
                response = await client.check_quota(
                    user_id=str(user.id),
                    metric=self.metric.value,
                    amount=1,
                )

                if not response.allowed:
                    logger.warning(
                        "Quota exceeded",
                        extra={
                            "user_id": str(user.id),
                            "metric": self.metric.value,
                            "current_usage": response.current_usage,
                            "limit": response.limit,
                        },
                    )
                    raise HTTPException(
                        status_code=429,
                        detail=f"Quota exceeded for {self.metric.value}",
                        headers={
                            "X-RateLimit-Remaining": str(response.remaining),
                            "X-RateLimit-Limit": str(response.limit),
                            "X-RateLimit-Reset": str(response.reset_at.seconds),
                        },
                    )

            except HTTPException:
                # Re-raise HTTP exceptions
                raise
            except Exception as e:
                # gRPC or network error - log and return 503
                logger.error(
                    "Subscription service unavailable",
                    extra={
                        "user_id": str(user.id),
                        "metric": self.metric.value,
                        "error": str(e),
                    },
                    exc_info=True,
                )
                raise HTTPException(
                    status_code=503,
                    detail="Subscription service temporarily unavailable",
                )

        # Quota check passed - process request
        # Subscription Service automatically tracks usage
        return await call_next(request)

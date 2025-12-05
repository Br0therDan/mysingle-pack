"""Subscription Service gRPC client.

This client wraps gRPC calls to Subscription Service.
All business logic resides in Subscription Service.

Port Configuration:
    - Default: 50052 (Subscription Service gRPC port)
    - Override via environment variable: SUBSCRIPTION_GRPC_PORT=50052
"""

from typing import Optional

from mysingle.clients import BaseGrpcClient
from mysingle.protos.services.subscription.v1 import (
    subscription_service_pb2,
    subscription_service_pb2_grpc,
)


class SubscriptionServiceClient(BaseGrpcClient):
    """Subscription Service gRPC client.

    Used by other services to call Subscription Service APIs.
    Automatically propagates user_id and correlation_id metadata.

    Example:
        async with SubscriptionServiceClient(user_id="user123") as client:
            response = await client.check_quota(
                user_id="user123",
                metric="api_calls",
                requested_count=1,
            )
            if response.allowed:
                # Process request
                ...
    """

    def __init__(
        self,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ):
        """Initialize Subscription Service gRPC client.

        Port is determined by BaseGrpcClient in the following priority:
        1. Environment variable: SUBSCRIPTION_GRPC_PORT
        2. Default port: 50052

        Args:
            user_id: User ID for metadata propagation
            correlation_id: Correlation ID for request tracing
        """
        super().__init__(
            service_name="subscription-service",
            default_port=50052,  # Fallback if SUBSCRIPTION_GRPC_PORT not set
            user_id=user_id,
            correlation_id=correlation_id,
        )
        self.stub = subscription_service_pb2_grpc.SubscriptionServiceStub(self.channel)

    async def get_subscription(self, user_id: str):
        """Get user's current subscription information.

        Args:
            user_id: User ID

        Returns:
            GetSubscriptionResponse (proto)
        """
        request = subscription_service_pb2.GetSubscriptionRequest(user_id=user_id)
        return await self.stub.GetSubscription(request)

    async def check_quota(
        self,
        user_id: str,
        metric: str,
        amount: int = 1,
    ):
        """Check if user has sufficient quota.

        Calls Subscription Service's QuotaEnforcer via gRPC.

        Args:
            user_id: User ID
            metric: Usage metric name (e.g., "api_calls", "backtests")
            amount: Requested quota amount

        Returns:
            CheckQuotaResponse (proto): allowed, current_usage, limit, remaining, etc.
        """
        request = subscription_service_pb2.CheckQuotaRequest(
            user_id=user_id,
            metric=metric,
            amount=amount,
        )
        return await self.stub.CheckQuota(request)

    async def get_entitlements(self, user_id: str):
        """Get user's tier-based entitlements.

        Used for feature gating. Returns tier, features, and limits.

        Args:
            user_id: User ID

        Returns:
            GetEntitlementsResponse (proto): tier, features, limits
        """
        request = subscription_service_pb2.GetEntitlementsRequest(user_id=user_id)
        return await self.stub.GetEntitlements(request)

    async def get_usage(
        self,
        user_id: str,
        metric: str,
        date: Optional[str] = None,
    ):
        """Get current usage for a specific metric.

        Args:
            user_id: User ID
            metric: Usage metric name
            date: Optional date (YYYY-MM-DD, default: today)

        Returns:
            GetUsageResponse (proto)
        """
        request = subscription_service_pb2.GetUsageRequest(
            user_id=user_id,
            metric=metric,
        )
        if date:
            request.date = date
        return await self.stub.GetUsage(request)

    async def get_all_quotas(
        self,
        user_id: str,
        date: Optional[str] = None,
    ):
        """Get all quota statuses for a user.

        Args:
            user_id: User ID
            date: Optional date (YYYY-MM-DD, default: today)

        Returns:
            GetAllQuotasResponse (proto)
        """
        request = subscription_service_pb2.GetAllQuotasRequest(user_id=user_id)
        if date:
            request.date = date
        return await self.stub.GetAllQuotas(request)

    async def health_check(self):
        """Check Subscription Service health.

        Returns:
            HealthCheckResponse (proto)
        """
        request = subscription_service_pb2.HealthCheckRequest()
        return await self.stub.HealthCheck(request)

"""MySingle Subscription Package.

Provides thin client layer for subscription-based service control:
- Quota enforcement middleware (gRPC wrapper)
- Feature gating decorators (gRPC wrapper)
- Subscription service gRPC client
- Common models and exceptions

All business logic remains in Subscription Service (port 50057).
This package only wraps gRPC calls for convenient use in other services.
"""

from mysingle.subscription.client import SubscriptionServiceClient
from mysingle.subscription.decorators import require_feature, require_tier
from mysingle.subscription.exceptions import (
    FeatureNotAvailableError,
    QuotaExceededError,
    SubscriptionServiceError,
    TierNotFoundError,
)
from mysingle.subscription.middleware import QuotaEnforcementMiddleware
from mysingle.subscription.models import TierLevel, UsageMetric

__version__ = "1.0.0"
__all__ = [
    # gRPC Client
    "SubscriptionServiceClient",
    # Middleware
    "QuotaEnforcementMiddleware",
    # Decorators
    "require_feature",
    "require_tier",
    # Models (enums only)
    "TierLevel",
    "UsageMetric",
    # Exceptions
    "QuotaExceededError",
    "FeatureNotAvailableError",
    "TierNotFoundError",
    "SubscriptionServiceError",
]

"""Common exceptions for subscription package."""


class SubscriptionServiceError(Exception):
    """Base exception for subscription service errors."""

    pass


class QuotaExceededError(SubscriptionServiceError):
    """Raised when usage quota is exceeded."""

    pass


class FeatureNotAvailableError(SubscriptionServiceError):
    """Raised when feature is not available in user's tier."""

    pass


class TierNotFoundError(SubscriptionServiceError):
    """Raised when tier configuration is not found."""

    pass

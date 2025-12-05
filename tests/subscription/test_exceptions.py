"""Unit tests for subscription exceptions."""

import pytest

from mysingle.subscription.exceptions import (
    FeatureNotAvailableError,
    QuotaExceededError,
    SubscriptionServiceError,
    TierNotFoundError,
)


def test_subscription_service_error():
    """Test SubscriptionServiceError can be raised."""
    with pytest.raises(SubscriptionServiceError) as exc_info:
        raise SubscriptionServiceError("Service error")
    assert "Service error" in str(exc_info.value)


def test_quota_exceeded_error():
    """Test QuotaExceededError is a SubscriptionServiceError."""
    with pytest.raises(SubscriptionServiceError):
        raise QuotaExceededError("Quota exceeded")

    with pytest.raises(QuotaExceededError) as exc_info:
        raise QuotaExceededError("API calls quota exceeded")
    assert "API calls" in str(exc_info.value)


def test_feature_not_available_error():
    """Test FeatureNotAvailableError is a SubscriptionServiceError."""
    with pytest.raises(SubscriptionServiceError):
        raise FeatureNotAvailableError("Feature not available")

    with pytest.raises(FeatureNotAvailableError) as exc_info:
        raise FeatureNotAvailableError("AI chat not available")
    assert "AI chat" in str(exc_info.value)


def test_tier_not_found_error():
    """Test TierNotFoundError is a SubscriptionServiceError."""
    with pytest.raises(SubscriptionServiceError):
        raise TierNotFoundError("Tier not found")

    with pytest.raises(TierNotFoundError) as exc_info:
        raise TierNotFoundError("Professional tier not found")
    assert "Professional" in str(exc_info.value)


def test_exception_inheritance():
    """Test exception inheritance hierarchy."""
    assert issubclass(QuotaExceededError, SubscriptionServiceError)
    assert issubclass(FeatureNotAvailableError, SubscriptionServiceError)
    assert issubclass(TierNotFoundError, SubscriptionServiceError)
    assert issubclass(SubscriptionServiceError, Exception)

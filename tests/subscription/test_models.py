"""Unit tests for subscription models."""

import pytest

from mysingle.subscription.models import TierLevel, UsageMetric


def test_tier_level_enum():
    """Test TierLevel enum values."""
    assert TierLevel.FREE.value == "free"
    assert TierLevel.STARTER.value == "starter"
    assert TierLevel.PROFESSIONAL.value == "professional"
    assert TierLevel.INSTITUTIONAL.value == "institutional"


def test_tier_level_string_comparison():
    """Test TierLevel can be compared as string."""
    tier = TierLevel.PROFESSIONAL
    assert tier == "professional"
    assert tier.value == "professional"


def test_tier_level_from_string():
    """Test TierLevel can be created from string."""
    tier = TierLevel("professional")
    assert tier == TierLevel.PROFESSIONAL


def test_usage_metric_enum():
    """Test UsageMetric enum values."""
    assert UsageMetric.API_CALLS.value == "api_calls"
    assert UsageMetric.BACKTESTS.value == "backtests"
    assert UsageMetric.AI_CHAT_MESSAGES.value == "ai_chat_messages"
    assert UsageMetric.AI_TOKENS.value == "ai_tokens"
    assert UsageMetric.INDICATORS.value == "indicators"
    assert UsageMetric.STRATEGIES.value == "strategies"
    assert UsageMetric.OPTIMIZATIONS.value == "optimizations"
    assert UsageMetric.STORAGE_BYTES.value == "storage_bytes"


def test_usage_metric_string_comparison():
    """Test UsageMetric can be compared as string."""
    metric = UsageMetric.API_CALLS
    assert metric == "api_calls"
    assert metric.value == "api_calls"


def test_usage_metric_from_string():
    """Test UsageMetric can be created from string."""
    metric = UsageMetric("backtests")
    assert metric == UsageMetric.BACKTESTS


def test_invalid_tier_level():
    """Test invalid TierLevel raises ValueError."""
    with pytest.raises(ValueError):
        TierLevel("invalid_tier")


def test_invalid_usage_metric():
    """Test invalid UsageMetric raises ValueError."""
    with pytest.raises(ValueError):
        UsageMetric("invalid_metric")

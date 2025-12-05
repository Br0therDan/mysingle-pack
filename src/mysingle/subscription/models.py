"""Common models for subscription package.

These models are synchronized with Proto definitions and shared across services.
"""

from enum import Enum


class TierLevel(str, Enum):
    """Subscription tier levels (synchronized with Proto)."""

    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    INSTITUTIONAL = "institutional"


class UsageMetric(str, Enum):
    """Usage metrics for quota enforcement (synchronized with Proto)."""

    API_CALLS = "api_calls"
    BACKTESTS = "backtests"
    AI_CHAT_MESSAGES = "ai_chat_messages"
    AI_TOKENS = "ai_tokens"
    INDICATORS = "indicators"
    STRATEGIES = "strategies"
    OPTIMIZATIONS = "optimizations"
    STORAGE_BYTES = "storage_bytes"

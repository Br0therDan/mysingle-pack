"""Example: Using quota enforcement middleware in app factory.

This example shows how to enable quota enforcement when creating a FastAPI app
using mysingle's app factory pattern.
"""

from mysingle.core import ServiceType, create_fastapi_app, create_service_config

# Example 1: Strategy Service with quota enforcement enabled
strategy_config = create_service_config(
    service_name="strategy-service",
    service_type=ServiceType.NON_IAM_SERVICE,
    enable_quota_enforcement=True,
    quota_metric="strategies",  # Will enforce strategy creation quota
)

strategy_app = create_fastapi_app(service_config=strategy_config)


# Example 2: Backtest Service with quota enforcement enabled
backtest_config = create_service_config(
    service_name="backtest-service",
    service_type=ServiceType.NON_IAM_SERVICE,
    enable_quota_enforcement=True,
    quota_metric="backtests",  # Will enforce backtest quota
)

backtest_app = create_fastapi_app(service_config=backtest_config)


# Example 3: GenAI Service with quota enforcement enabled
genai_config = create_service_config(
    service_name="genai-service",
    service_type=ServiceType.NON_IAM_SERVICE,
    enable_quota_enforcement=True,
    quota_metric="ai_chat_messages",  # Will enforce AI chat quota
)

genai_app = create_fastapi_app(service_config=genai_config)


# Example 4: Service WITHOUT quota enforcement (default)
indicator_config = create_service_config(
    service_name="indicator-service",
    service_type=ServiceType.NON_IAM_SERVICE,
    # enable_quota_enforcement=False (default)
)

indicator_app = create_fastapi_app(service_config=indicator_config)


# Example 5: Service with multiple configurations
ml_config = create_service_config(
    service_name="ml-service",
    service_type=ServiceType.NON_IAM_SERVICE,
    enable_quota_enforcement=True,
    quota_metric="optimizations",
    enable_metrics=True,
    enable_audit_logging=True,
    cors_origins=["https://app.mysingle.ai"],
)

ml_app = create_fastapi_app(service_config=ml_config)


"""
Available quota metrics (from mysingle.subscription.models.UsageMetric):
- api_calls
- backtests
- ai_chat_messages
- ai_tokens
- indicators
- strategies
- optimizations
- storage_bytes

The middleware will automatically:
1. Check quota via Subscription Service gRPC (port 50057)
2. Return 429 if quota exceeded with rate limit headers
3. Return 503 if Subscription Service unavailable
4. Skip quota check for unauthenticated requests

Rate limit headers on 429 response:
- X-RateLimit-Remaining: Number of requests remaining
- X-RateLimit-Limit: Total quota limit
- X-RateLimit-Reset: Unix timestamp when quota resets
"""

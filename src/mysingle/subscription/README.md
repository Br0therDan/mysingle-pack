# MySingle Subscription Package

Thin client layer for subscription-based service control in MySingle Quant MSA.

## Overview

This package provides **minimal wrappers** around Subscription Service gRPC APIs for:
- **Quota enforcement**: Automatic quota checking middleware
- **Feature gating**: Tier-based access control decorators
- **Subscription info**: Direct gRPC client for custom queries

**All business logic resides in Subscription Service (port 50057).** This package only wraps gRPC calls for convenient use in other microservices.

## Installation

```bash
# In mysingle-pack
uv add "mysingle[subscription]"

# Or include in pyproject.toml
[project.dependencies]
mysingle = {git = "https://github.com/Br0therDan/mysingle-pack.git", tag = "v1.1.0", extras = ["subscription"]}
```

## Quick Start

### 1. App Factory Integration (Recommended)

The easiest way to enable quota enforcement is through the app factory:

```python
from mysingle.core import create_fastapi_app, create_service_config, ServiceType

# Enable quota enforcement in service config
config = create_service_config(
    service_name="strategy-service",
    service_type=ServiceType.NON_IAM_SERVICE,
    enable_quota_enforcement=True,
    quota_metric="strategies",  # Enforces strategy creation quota
)

app = create_fastapi_app(service_config=config)
```

Available metrics: `api_calls`, `backtests`, `ai_chat_messages`, `ai_tokens`, `indicators`, `strategies`, `optimizations`, `storage_bytes`

### 2. Manual Middleware Application

Alternatively, apply middleware manually to specific routes:

```python
from fastapi import FastAPI
from mysingle.subscription import QuotaEnforcementMiddleware, UsageMetric

app = FastAPI()

# Apply to all routes
app.add_middleware(
    QuotaEnforcementMiddleware,
    metric=UsageMetric.API_CALLS,
)

# Or apply to specific router
from fastapi import APIRouter
router = APIRouter()
router.add_middleware(QuotaEnforcementMiddleware, metric=UsageMetric.STRATEGIES)
app.include_router(router, prefix="/strategies")
```

### 3. Feature Gating Decorators

Require specific tier or feature:

```python
from fastapi import APIRouter, Request
from mysingle.subscription import require_tier, require_feature, TierLevel

router = APIRouter()

@router.post("/backtests")
@require_tier(TierLevel.STARTER)  # Starter tier or higher
async def create_backtest(request: Request, ...):
    """Basic backtest creation."""
    ...

@router.post("/backtests/advanced")
@require_tier(TierLevel.PROFESSIONAL)  # Professional tier or higher
@require_feature("advanced_backtesting")  # Requires specific feature
async def create_advanced_backtest(request: Request, ...):
    """Advanced backtest with optimization."""
    ...
```

### 4. Direct gRPC Client

For custom queries:

```python
from mysingle.subscription import SubscriptionServiceClient, UsageMetric

async def process_chat_message(user_id: str, message: str):
    # Check subscription and quota
    async with SubscriptionServiceClient(user_id=user_id) as client:
        # Get subscription info
        subscription = await client.get_subscription(user_id)

        # Check quota
        quota_response = await client.check_quota(
            user_id=user_id,
            metric=UsageMetric.AI_CHAT_MESSAGES.value,
            amount=1,
        )

        if not quota_response.allowed:
            raise QuotaExceededError(
                f"AI chat quota exceeded. Remaining: {quota_response.remaining}"
            )

        # Process message...
        return await generate_ai_response(message)
```

## Available Models

### TierLevel Enum

```python
from mysingle.subscription import TierLevel

TierLevel.FREE
TierLevel.STARTER
TierLevel.PROFESSIONAL
TierLevel.INSTITUTIONAL
```

### UsageMetric Enum

```python
from mysingle.subscription import UsageMetric

UsageMetric.API_CALLS
UsageMetric.BACKTESTS
UsageMetric.AI_CHAT_MESSAGES
UsageMetric.AI_TOKENS
UsageMetric.INDICATORS
UsageMetric.STRATEGIES
UsageMetric.OPTIMIZATIONS
UsageMetric.STORAGE_BYTES
```

## Exceptions

```python
from mysingle.subscription import (
    SubscriptionServiceError,  # Base exception
    QuotaExceededError,        # Quota exceeded
    FeatureNotAvailableError,  # Feature not available
    TierNotFoundError,         # Tier not found
)
```

## Architecture

```
┌─────────────────────┐
│  Strategy Service   │
│  (or other service) │
└──────────┬──────────┘
           │ import mysingle.subscription
           │ (QuotaEnforcementMiddleware)
           ▼
┌─────────────────────┐
│ mysingle.subscription│  ← Thin wrapper (this package)
│    (gRPC client)     │
└──────────┬──────────┘
           │ gRPC call (port 50057)
           ▼
┌─────────────────────┐
│ Subscription Service│  ← All business logic here
│  - QuotaEnforcer    │
│  - UsageTracker     │
│  - TierManager      │
│  - Redis, MongoDB   │
└─────────────────────┘
```

**Key Principle**: This package has **no business logic**. It only wraps gRPC calls to Subscription Service.

## Error Handling

### Quota Exceeded (429)

```python
# Middleware automatically returns 429 with headers
HTTP/1.1 429 Too Many Requests
X-RateLimit-Remaining: 0
X-RateLimit-Limit: 100
X-RateLimit-Reset: 1733461200
```

### Feature Not Available (403)

```python
# Decorator automatically returns 403
HTTP/1.1 403 Forbidden
{"detail": "Feature 'advanced_backtesting' not available in your tier"}
```

### Service Unavailable (503)

```python
# Middleware/Decorator returns 503 on gRPC errors
HTTP/1.1 503 Service Unavailable
{"detail": "Subscription service temporarily unavailable"}
```

## Testing

Mock gRPC calls in tests:

```python
from unittest.mock import AsyncMock, MagicMock, patch
from mysingle.subscription import SubscriptionServiceClient

@pytest.mark.asyncio
async def test_quota_check():
    with patch("mysingle.subscription.middleware.SubscriptionServiceClient") as mock:
        mock_instance = AsyncMock()
        mock_instance.check_quota.return_value = MagicMock(
            allowed=True,
            remaining=95,
            limit=100,
        )
        mock.return_value.__aenter__.return_value = mock_instance

        # Test your route...
```

## Migration from Subscription Service

If migrating from direct Subscription Service imports:

**Before:**
```python
from app.core.feature_gate import require_tier
from app.middleware.quota_enforcement import QuotaEnforcementMiddleware
```

**After:**
```python
from mysingle.subscription import require_tier, QuotaEnforcementMiddleware
```

## Related Documentation

- [Migration Plan](../../docs/MYSINGLE_PACK_MIGRATION_PLAN_V2.md)
- [Subscription Service Strategy](../../../services/subscription-service/SUBSCRIPTION_SERVICE_STRATEGY.md)
- [MySingle Pack README](../../README.md)

## Support

For issues or questions:
- GitHub Issues: https://github.com/Br0therDan/mysingle-pack/issues
- Internal Slack: #mysingle-quant-dev

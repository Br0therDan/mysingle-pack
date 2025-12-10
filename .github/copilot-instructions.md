# MySingle Package - Development Guide

**Version:** 2.2.1 | **Updated:** 2025-12-02

MySingle provides standardized authentication, gRPC communication, and core utilities for MySingle Quant microservices.

**Installation:** `pip install mysingle[full]`

---

## Core Principles

### 1. Authentication Standard

- **Kong Gateway-based:** All services use `Request.state.user`
- **Functions:** `get_current_active_verified_user(request)` (recommended)
- **Test Bypass:** Set `MYSINGLE_AUTH_BYPASS=true` + `ENVIRONMENT=development`
- **Production:** Bypass automatically disabled

### 2. Service Communication

- **Inter-service:** gRPC only via `BaseGrpcClient`
- **Required Metadata:** `user-id`, `correlation-id` (auto-generated if missing)
- **External API:** Kong Gateway routes

### 3. FastAPI App Factory

```python
from mysingle.core import create_fastapi_app, create_service_config, ServiceType

config = create_service_config(
    service_name="my-service",
    service_type=ServiceType.NON_IAM_SERVICE,
)
app = create_fastapi_app(service_config=config)
```

**Service Types:**

- **IAM_SERVICE:** JWT validation + user management (creates User/OAuthAccount collections)
- **NON_IAM_SERVICE:** Kong headers only (no user collections)

### 4. MongoDB Collections

```python
# Custom models only (NON_IAM services)
from app.models import MyModel

app = create_fastapi_app(
    service_config=config,
    document_models=[MyModel],
)
```

---

## Module Structure

| Module   | Purpose                  | Install Extra     |
| -------- | ------------------------ | ----------------- |
| core     | Logging, metrics, health | (always included) |
| auth     | JWT, Kong Gateway auth   | `[auth]`          |
| database | MongoDB, DuckDB, Redis   | `[database]`      |
| dsl      | Strategy DSL parser      | `[dsl]`           |
| clients  | gRPC clients             | `[clients]`       |
| grpc     | gRPC interceptors        | `[grpc]`          |

**Recommended:** `mysingle[common-grpc]` (auth + database + web + grpc + clients)

---

## CLI Tools

### Package Management

```bash
mysingle version auto              # Auto-detect version from commits
mysingle submodule add             # Add MySingle as git submodule
mysingle submodule update          # Update to latest version
```

### Proto Management

```bash
mysingle-proto generate            # Generate Python stubs
mysingle-proto validate            # Lint + format check
mysingle-proto validate --breaking # Check breaking changes
```

---

## Common Patterns

### Authentication

```python
from mysingle.auth import get_current_active_verified_user
from fastapi import Request

@router.get("/items")
async def list_items(request: Request):
    user = get_current_active_verified_user(request)
    return await get_user_items(str(user.id))
```

### gRPC Client

```python
from mysingle.clients import BaseGrpcClient

class MyServiceClient(BaseGrpcClient):
    def __init__(self, user_id=None, correlation_id=None):
        super().__init__("my-service", 50051, user_id=user_id, correlation_id=correlation_id)
        self.stub = my_service_pb2_grpc.MyServiceStub(self.channel)

async with MyServiceClient(user_id=user_id) as client:
    result = await client.method()
```

### Routing Convention

- **External Routes:** Public CRUD/query endpoints (e.g., `POST /items`)
- **Internal Routes:** Service triggers (e.g., `POST /items/{id}/start`)

---

## Redis Cache Standards

### Database Allocation

All services MUST use `BaseRedisCache` from `mysingle.database` and follow the platform-wide DB allocation policy:

| DB  | Purpose                | Owner Service(s)  | Key Prefix Examples                                   | TTL Guidance |
| --- | ---------------------- | ----------------- | ----------------------------------------------------- | ------------ |
| 0   | User Authentication    | IAM               | `user:{user_id}`                                      | 300s (5min)  |
| 1   | gRPC Response Cache    | All Services      | `grpc:{service_name}:{method}:{hash}`                 | 3600s (1h)   |
| 2   | Rate Limiting          | Kong/Gateway      | `ratelimit:{user_id}:{endpoint}`, `quota:{user_id}`   | 60-3600s     |
| 3   | Session Storage        | IAM               | `session:{session_id}`                                | 86400s (24h) |
| 4   | DSL Bytecode Cache     | Strategy          | `dsl:bytecode:{strategy_id}`, `dsl:warmed:{hash}`     | 3600-86400s  |
| 5   | Market Data Cache      | Market Data       | `market:{symbol}:{interval}:{date_range_hash}`        | 300-3600s    |
| 6   | Backtest Service Cache | Backtest          | `walkforward:{job_id}:{window}`, `progress:{task_id}` | 3600-86400s  |
| 7   | Indicator Cache        | Indicator         | `indicator:{name}:{symbol}:{params_hash}`             | 1800-7200s   |
| 8   | Strategy Cache         | Strategy          | `strategy:{strategy_id}`, `version:{version_id}`      | 600-3600s    |
| 9   | Notification Queue     | Notification      | `notif:{user_id}:{timestamp}`, `email_queue:{id}`     | 300-1800s    |
| 10  | Celery Broker          | Backtest (Celery) | `celery:task:{task_id}`, `celery:group:{group_id}`    | Managed      |
| 11  | Celery Result Backend  | Backtest (Celery) | `celery-task-meta-{task_id}`                          | Managed      |
| 12  | ML Model Cache         | ML                | `ml:model:{model_id}`, `ml:prediction:{request_hash}` | 3600-86400s  |
| 13  | GenAI Response Cache   | GenAI             | `genai:{prompt_hash}`, `genai:context:{session_id}`   | 1800-7200s   |
| 14  | Subscription Cache     | Subscription      | `subscription:{user_id}`, `plan:{plan_id}`            | 3600s        |
| 15  | Reserved               | Platform          | -                                                     | -            |

### Usage Guidelines

**DO:**

- ✅ Use `BaseRedisCache` for service-specific caching
- ✅ Reference `REDIS_DB_*` constants from `CommonSettings`
- ✅ Follow key_prefix standards for your service
- ✅ Set appropriate TTL based on data volatility
- ✅ Use `get_redis_client(db=N)` for direct operations when needed

**DON'T:**

- ❌ Hard-code DB numbers in your code
- ❌ Use `redis.asyncio` directly without `BaseRedisCache`
- ❌ Share DB numbers across unrelated purposes
- ❌ Use DB 15 (reserved for future platform needs)
- ❌ Create keys without proper prefix namespacing

### Implementation Example

**New in v2.2.1:** Use factory functions (recommended)

```python
from mysingle.database import create_service_cache
from mysingle.core.config import settings

# Option 1: Factory function (recommended)
cache = create_service_cache(
    service_name="myservice",
    db_constant=settings.REDIS_DB_MYSERVICE,
)

# Option 2: Custom cache class (if custom logic needed)
from mysingle.database import BaseRedisCache

class MyServiceCache(BaseRedisCache):
    """Service-specific cache following platform standards"""

    def __init__(self):
        super().__init__(
            key_prefix="myservice",  # Service-specific prefix
            default_ttl=3600,
            # Note: redis_db is now internal (_redis_db)
            # Use factory functions or direct client for DB selection
        )
```

**Factory Functions (v2.2.1+):**

```python
from mysingle.database import (
    create_user_cache,      # User auth cache (DB 0)
    create_grpc_cache,      # gRPC response cache (DB 1)
    create_service_cache,   # Service-specific cache (custom DB)
)

# User cache (DB 0)
user_cache = create_user_cache()

# gRPC cache (DB 1)
grpc_cache = create_grpc_cache(service_name="strategy")

# Service cache (custom DB)
from mysingle.core.config import settings
market_cache = create_service_cache("market", settings.REDIS_DB_MARKET_DATA)
```

---

## Required Standards

### Headers

- **X-User-Id:** Propagate in all downstream calls
- **Correlation-Id:** Request tracing across services

### Health Endpoints

All services must expose:

- `/health` - Basic health check
- `/ready` - Readiness probe
- `/metrics` - Prometheus metrics

### Environment Variables

- Use ENV for service discovery (e.g., `MY_SERVICE_GRPC_HOST`)
- Never hard-code URLs or ports

---

## Anti-Patterns (DO NOT)

❌ Direct HTTP calls between services → Use Kong Gateway or gRPC
❌ Manual JWT token extraction → Use `mysingle.auth` functions
❌ Missing `user_id`/`correlation_id` in gRPC calls
❌ Hard-coded service URLs → Use environment variables
❌ Creating User/OAuthAccount collections in NON_IAM services

---

## Migration from v1.x

### Removed Components

- `BaseServiceClient` (HTTP client) → Use `BaseGrpcClient`
- Legacy auth patterns → Use Kong Gateway standard
- Hybrid HTTP/gRPC clients → gRPC only

### Import Path Changes

```python
# Old
from mysingle.base import BaseDocument

# New
from mysingle.core.base import BaseDocument
```

---

## Documentation

- **Module Guides:** See `src/mysingle/{module}/README.md`
- **App Factory:** `docs/MYSINGLE_APP_FACTORY_USAGE_GUIDE.md`
- **Submodule PR:** `docs/SUBMODULE_PR_WORKFLOW.md`
- **Full Guide:** `AGENTS.md`

---

**Platform:** MySingle Quant (Beta: Early 2026)
**License:** MIT

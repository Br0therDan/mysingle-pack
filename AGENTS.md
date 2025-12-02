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

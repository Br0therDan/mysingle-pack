# MySingle Package - Copilot Development Instructions

## Overview

MySingle package provides standardized auth, gRPC, and utilities for MySingle Quant microservices (Beta: Early 2026).

**Type:** PyPI package (not local)
**Install:** `pip install mysingle[full]`

---

## 1. Authentication

**Standard:** Kong Gateway + Request.state.user

### Core Functions (Request-Based)

```python
from mysingle.auth import (
    get_current_user,                    # Basic user
    get_current_active_user,             # Active only
    get_current_active_verified_user,    # Verified (recommended)
    get_current_user_optional,           # Optional auth
    get_current_active_superuser,        # Admin only
)
```

### Usage Pattern

```python
from fastapi import APIRouter, Request

@router.get("/items")
async def list_items(request: Request):
    user = get_current_active_verified_user(request)
    items = await get_user_items(str(user.id))
    return items
```

### Test Bypass

**Environment Variables:**

```bash
# Enable authentication bypass (development/staging only)
export MYSINGLE_AUTH_BYPASS=true
export ENVIRONMENT=development

# Regular test user (default)
export TEST_USER_EMAIL="test_user@test.com"
export TEST_USER_FULLNAME="Test User"

# Admin test user (use with MYSINGLE_AUTH_BYPASS_ADMIN=true)
export MYSINGLE_AUTH_BYPASS_ADMIN=true
export TEST_ADMIN_EMAIL="test_admin@test.com"
export TEST_ADMIN_FULLNAME="Test Admin"
```

**Behavior:**

- Auto-injects test user into `request.state.user`
- Bypasses all authentication checks
- Disabled in production for security
- Use `MYSINGLE_AUTH_BYPASS_ADMIN=true` for superuser privileges

---

## 2. gRPC Communication

**Standard:** BaseGrpcClient only

### Client Pattern

```python
from mysingle.clients import BaseGrpcClient
from app.grpc import my_service_pb2_grpc

class MyServiceClient(BaseGrpcClient):
    def __init__(self, user_id=None, correlation_id=None, **kwargs):
        super().__init__(
            service_name="my-service",
            default_port=50051,
            user_id=user_id,
            correlation_id=correlation_id,
            **kwargs,
        )
        self.stub = my_service_pb2_grpc.MyServiceStub(self.channel)

# Usage
async with MyServiceClient(user_id=user_id) as client:
    result = await client.method()
```

### Metadata Headers

- `user-id`: Required (server validates)
- `correlation-id`: Auto-generated if missing
- `request-id`: Always auto-generated

---

## 3. FastAPI App Factory

```python
from mysingle.core import create_fastapi_app, create_service_config, ServiceType

config = create_service_config(
    service_name="my-service",
    service_type=ServiceType.NON_IAM_SERVICE,
)

app = create_fastapi_app(service_config=config)
```

**Service Types:**

- **IAM_SERVICE**: Direct JWT + user management
  - Auto-creates: users, oauth_accounts collections
  - Manages user lifecycle and OAuth
- **NON_IAM_SERVICE**: Kong headers only
  - **NO** User/OAuthAccount collections
  - Uses Kong Gateway headers (X-User-ID, etc.)

**Custom Models:**

```python
from app.models import MyModel

app = create_fastapi_app(
    service_config=config,
    document_models=[MyModel],  # NON_IAM: only custom models
)
```

---

## Common Standards

### Routing

- External: Public CRUD/query (`POST /items`)
- Internal: Control triggers (`POST /items/{id}/start`)

### Headers

- `X-User-Id`: Required in all downstream calls
- `Correlation-Id`: Request tracing

### Health

- `/health`, `/ready`, `/metrics` required

---

## Removed (v2.0)

❌ `BaseServiceClient` (HTTP) - Use gRPC only
❌ Legacy auth patterns
❌ Hybrid HTTP/gRPC clients

---

## Anti-Patterns

❌ Direct service HTTP calls (use Kong)
❌ Manual token extraction (use `mysingle.auth`)
❌ Missing user_id/correlation_id in gRPC
❌ Hard-coded URLs (use ENV)
❌ HTTP for inter-service (use gRPC)

---

**Version:** 2.0
**Last Updated:** 2025-11-20

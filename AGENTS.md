# MySingle Package - Development Guide

## Overview

The MySingle package provides standardized authentication, gRPC communication, and core utilities for the MySingle Quant microservices platform (Beta: Early 2026).

**Package Type:** Published to PyPI (not a local package)
**Installation:** `pip install mysingle[full]`

---

## Core Components

### 1. Authentication System

**Single Standard:** Kong Gateway-based authentication with Request.state.user injection

#### Core Functions

All services use these Request-based authentication functions:

```python
from mysingle.auth import (
    get_current_user,                    # Basic authenticated user
    get_current_active_user,             # Active user (is_active=True)
    get_current_active_verified_user,    # Verified user (recommended)
    get_current_user_optional,           # Optional auth (public APIs)
    get_current_active_superuser,        # Admin/superuser only
)

# Usage in route handlers
from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/items")
async def list_items(request: Request):
    user = get_current_active_verified_user(request)
    # user.id, user.email, user.is_verified, user.is_superuser available
    items = await get_user_items(str(user.id))
    return items
```

#### Kong Integration Functions

**Simplified Minimal Integration** (JWT plugin only, no Consumer headers):

```python
from mysingle.auth import (
    get_kong_user_id,          # Extract user ID from X-User-Id header
    is_kong_authenticated,     # Check Kong authentication status
)

# Advanced (optional)
from mysingle.auth.deps import (
    get_kong_correlation_id,   # Request correlation ID
    get_kong_request_id,       # Unique request ID
    get_kong_upstream_latency, # Upstream service latency (ms)
    get_kong_proxy_latency,    # Kong proxy latency (ms)
)
```

**Note:** Consumer-related functions (`get_kong_consumer_id`, `get_kong_consumer_username`, `get_kong_headers_dict`) were removed as Kong configuration only uses JWT plugin without Consumer header injection.

#### Authentication Middleware

Automatically enabled via `create_fastapi_app()`:

- IAM Service: JWT token validation → Kong headers (fallback)
- Non-IAM Services: Kong headers → JWT tokens (fallback)

#### Test Environment Bypass

**Configuration:**

```bash
# Enable authentication bypass (development/staging only)
export MYSINGLE_AUTH_BYPASS=true
export ENVIRONMENT=development

# Regular test user (default)
export TEST_USER_EMAIL="test_user@test.com"
export TEST_USER_FULLNAME="Test User"

# Admin test user (superuser privileges)
export MYSINGLE_AUTH_BYPASS_ADMIN=true
export TEST_ADMIN_EMAIL="test_admin@test.com"
export TEST_ADMIN_FULLNAME="Test Admin"
```

**Behavior:**

- Auto-injects test user into `request.state.user`
- Bypasses all authentication checks
- Default: Regular user (not superuser)
- Use `MYSINGLE_AUTH_BYPASS_ADMIN=true` for superuser testing
- Fixed test user ID: `000000000000000000000001`
- All test users have: `is_active=True`, `is_verified=True`

**Security:** Bypass is automatically disabled in production environments.

---

### 2. gRPC Communication

**Standard:** All inter-service communication uses `BaseGrpcClient`

#### BaseGrpcClient Features

- Automatic channel management (secure/insecure)
- Metadata injection: `user-id`, `correlation-id`, `request-id`
- Async context manager support
- Environment-based host resolution
- Standard gRPC options (keepalive, timeout)

#### Service-Specific Client Pattern

```python
from mysingle.clients import BaseGrpcClient
from app.grpc import indicator_service_pb2_grpc

class IndicatorGrpcClient(BaseGrpcClient):
    def __init__(
        self,
        user_id: str | None = None,
        correlation_id: str | None = None,
        timeout: float = 10.0,
        **kwargs,
    ):
        super().__init__(
            service_name="indicator-service",
            default_port=50052,
            user_id=user_id,
            correlation_id=correlation_id,
            timeout=timeout,
            **kwargs,
        )
        self.stub = indicator_service_pb2_grpc.IndicatorServiceStub(self.channel)

    async def get_metadata(self, name: str):
        request = indicator_service_pb2.GetIndicatorMetadataRequest(
            name=name,
            user_id=self.user_id or "",
        )
        response = await self.stub.GetIndicatorMetadata(
            request,
            timeout=self.timeout,
            metadata=self.metadata,  # Auto-includes user-id, correlation-id, request-id
        )
        return response

# Usage in service layer
async with IndicatorGrpcClient(
    user_id=user_id,
    correlation_id=correlation_id
) as client:
    result = await client.get_metadata("sma")
```

#### Metadata Headers (gRPC)

```python
GRPC_METADATA_USER_ID = "user-id"              # Required (validated by server)
GRPC_METADATA_CORRELATION_ID = "correlation-id"  # Auto-generated if missing
GRPC_METADATA_REQUEST_ID = "request-id"        # Always auto-generated
```

#### Host Resolution

Priority:
1. Environment variable: `{SERVICE}_GRPC_HOST` (e.g., `INDICATOR_GRPC_HOST`)
2. Docker environment: service name (e.g., `indicator-service`)
3. Default: `localhost`

---

### 3. FastAPI App Factory

```python
from mysingle.core import (
    create_fastapi_app,
    create_service_config,
    ServiceType,
)

# Create service configuration
config = create_service_config(
    service_name="my-service",
    service_type=ServiceType.NON_IAM_SERVICE,
    service_version="1.0.0",
    description="My Service Description",
)

# Create FastAPI app with standard middleware
app = create_fastapi_app(service_config=config)

# Authentication middleware is auto-configured based on ServiceType
```

#### Service Types

- **IAM_SERVICE**: Direct JWT validation + user management capabilities
  - Automatically includes User and OAuthAccount MongoDB collections
  - Creates super admin and test users on startup
  - Manages OAuth flows and user lifecycle

- **NON_IAM_SERVICE**: Kong Gateway header-based authentication
  - **Does NOT** create User/OAuthAccount collections
  - Relies on Kong Gateway headers (X-User-ID, X-User-Email, etc.)
  - Consumes user context from upstream without managing users

#### MongoDB Collection Initialization

**IAM Service:**
```python
# Automatic collections created:
# - users (User model)
# - oauth_accounts (OAuthAccount model)
# - audit_logs (if enable_audit_logging=True)
# - custom models passed to create_fastapi_app()

config = ServiceConfig(
    service_name="iam-service",
    service_type=ServiceType.IAM_SERVICE,
)
app = create_fastapi_app(service_config=config)
```

**NON_IAM Service:**
```python
# Only creates:
# - audit_logs (if enable_audit_logging=True)
# - custom models passed to create_fastapi_app()
# NO User or OAuthAccount collections

from app.models import BacktestResult, Portfolio

config = ServiceConfig(
    service_name="backtest-service",
    service_type=ServiceType.NON_IAM_SERVICE,
)
app = create_fastapi_app(
    service_config=config,
    document_models=[BacktestResult, Portfolio],
)
```

---

## Common Standards

### Router Separation

- **External Router**: Public-facing CRUD/query endpoints
  - Example: `POST /backtests`, `GET /backtests/{id}`
- **Internal Router**: Service-to-service control/trigger endpoints
  - Example: `POST /backtests/{id}/start`
  - Not publicly exposed via Kong Gateway

### Header Propagation

Required in all downstream calls:
- `X-User-Id`: Original requester identity
- `Correlation-Id`: Request tracing across services

### Health & Observability

- All services expose `/health` and `/ready`
- Structured logging with correlation IDs
- Metrics exported at `/metrics`

### Performance Best Practices

- Use FastAPI lifespan for resource initialization/cleanup
- Reuse HTTP/gRPC clients (connection pooling)
- Eliminate N+1 queries (batch fetch → map join)
- Composite indexes for user-scoped lists: `(user_id, created_at desc)`

---

## Package Structure

### Recommended Imports

```python
# Core
from mysingle.core import create_fastapi_app, settings, init_mongo

# Authentication
from mysingle.auth import (
    get_current_active_verified_user,
    get_kong_user_id,
)

# gRPC Clients
from mysingle.clients import BaseGrpcClient

# Logging
from mysingle.core import get_logger

# Constants
from mysingle.constants import (
    HEADER_USER_ID,
    GRPC_METADATA_USER_ID,
)
```

### Available Extras

```bash
# Core only
pip install mysingle

# Feature-specific
pip install mysingle[auth]      # Authentication
pip install mysingle[web]       # FastAPI/web features
pip install mysingle[database]  # MongoDB/DuckDB
pip install mysingle[dsl]       # DSL runtime
pip install mysingle[monitoring] # Metrics/health

# All features
pip install mysingle[full]

# Development
pip install mysingle[dev]
```

---

## Testing

### Unit Testing with Auth Bypass

```python
import os
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def enable_auth_bypass():
    os.environ["MYSINGLE_AUTH_BYPASS"] = "true"
    os.environ["ENVIRONMENT"] = "development"
    yield
    del os.environ["MYSINGLE_AUTH_BYPASS"]
    del os.environ["ENVIRONMENT"]

def test_protected_endpoint(client: TestClient):
    # Test user automatically injected by middleware
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    # Test user: test@example.com (superuser)
```

### gRPC Client Testing

```python
from mysingle.clients import BaseGrpcClient

async def test_grpc_metadata():
    client = BaseGrpcClient(
        service_name="test-service",
        default_port=50051,
        user_id="user123",
        correlation_id="corr456",
    )

    metadata = client.metadata
    metadata_dict = dict(metadata)

    assert metadata_dict["user-id"] == "user123"
    assert metadata_dict["correlation-id"] == "corr456"
    assert "request-id" in metadata_dict
```

---

## Anti-Patterns to Avoid

❌ Direct service-to-service HTTP calls (must go through Kong)
❌ Manual token extraction (use `mysingle.auth` functions)
❌ Forgetting to propagate `user_id` and `correlation_id` in gRPC calls
❌ Hard-coded service URLs (use ENV or service discovery)
❌ Skipping authentication on endpoints requiring user context
❌ Using HTTP clients for inter-service communication (use gRPC)

---

## Migration Notes

### Removed Components (v2.0)

- ❌ `BaseServiceClient` (HTTP client) - Use `BaseGrpcClient` only
- ❌ Legacy authentication patterns - Single Kong-based standard only
- ❌ Hybrid HTTP/gRPC client implementations

### Upgrade Guide

```python
# Old (removed)
from mysingle import BaseServiceClient

class MyClient(BaseServiceClient):
    pass

# New (use gRPC)
from mysingle.clients import BaseGrpcClient

class MyGrpcClient(BaseGrpcClient):
    pass
```

---

## References

- **Main Architecture:** `/AGENTS.md`
- **Kong Configuration:** `KONG_API_GATEWAY_CONFIGURATION_GUIDE.md`
- **Service-Specific Guides:** See individual service `AGENTS.md` files

---

**Version:** 2.0
**Last Updated:** 2025-11-20
**Platform:** MySingle Quant (Beta: Early 2026)

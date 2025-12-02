# mysingle.core

**Version:** 2.2.1 | **Updated:** 2025-12-02

Core utilities and infrastructure for MySingle Quant microservices.

---

## Overview

`mysingle.core` provides foundational components for building standardized FastAPI microservices in the MySingle Quant ecosystem. It includes application factories, configuration management, observability tools, and common utilities.

### Design Philosophy

- **Convention over Configuration:** Sensible defaults for rapid development
- **12-Factor App Compliance:** Environment-based configuration, stateless services
- **Production-Ready:** Built-in observability, health checks, and graceful shutdown
- **Type-Safe:** Pydantic-based configuration and schemas
- **Extensible:** Easy to customize while maintaining standards

---

## Module Structure

```
mysingle/core/
├── app_factory.py          # FastAPI app factory with auto-configuration
├── config.py               # CommonSettings base class
├── constants.py            # Global constants and enums
├── base/                   # Base classes for documents and schemas
├── logging/                # Structured logging system
├── metrics/                # Prometheus metrics collection
├── audit/                  # HTTP audit logging middleware
├── health/                 # Health check endpoints
└── email/                  # Email sending utilities
```

---

## Documentation Index

Comprehensive guides for each major component:

| Document                                                                       | Description                       | Key Topics                                                                              |
| ------------------------------------------------------------------------------ | --------------------------------- | --------------------------------------------------------------------------------------- |
| **[App Factory Guide](../../../docs/core/APP_FACTORY_USAGE_GUIDE.md)**         | FastAPI application factory usage | Service types (IAM/Non-IAM), auto-configuration, middleware setup, lifecycle management |
| **[Structured Logging Guide](../../../docs/core/STRUCTURED_LOGGING_GUIDE.md)** | Production logging system         | JSON output, correlation IDs, context propagation, environment-specific formatting      |
| **[Metrics Guide](../../../docs/core/METRICS_USAGE_GUIDE.md)**                 | Prometheus metrics collection     | HTTP metrics, custom metrics (counters/gauges/histograms), percentiles, endpoints       |
| **[Audit Logging Guide](../../../docs/core/AUDIT_LOGGING_USAGE_GUIDE.md)**     | Request/response audit trails     | Compliance tracking, distributed tracing, user context, MongoDB storage                 |
| **[Common Settings Guide](../../../docs/core/COMMON_SETTINGS_GUIDE.md)**       | Configuration inheritance pattern | Environment variables, service-specific settings, best practices                        |

---

## Common Patterns

### 1. Standard Service Initialization

All MySingle services follow this initialization pattern:

```python
from mysingle.core import (
    create_fastapi_app,
    create_service_config,
    ServiceType,
)

# 1. Create service configuration
config = create_service_config(
    service_name="strategy-service",
    service_type=ServiceType.NON_IAM_SERVICE,
    service_version="1.0.0",
)

# 2. Create FastAPI app with auto-configuration
app = create_fastapi_app(service_config=config)

# 3. Add custom routes
from app.routes import router
app.include_router(router, prefix="/api/v1")
```

**What happens automatically:**
- ✅ Structured logging configured
- ✅ Metrics collection enabled
- ✅ Health check endpoints registered
- ✅ Audit logging middleware added
- ✅ CORS configured (if enabled)
- ✅ MongoDB connection (if database enabled)
- ✅ Authentication middleware (based on service type)

### 2. Configuration Management

```python
from mysingle.core.config import CommonSettings
from pydantic_settings import SettingsConfigDict

class Settings(CommonSettings):
    """Service-specific settings extending CommonSettings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Add service-specific settings
    STRATEGY_EXECUTION_TIMEOUT: int = 300
    BACKTEST_MAX_WORKERS: int = 4

# Create singleton instance
settings = Settings()
```

**Inherited from CommonSettings:**
- Database connections (MongoDB, Redis, DuckDB)
- Authentication settings (JWT, OAuth2, Kong Gateway)
- SMTP configuration
- Logging levels
- Cache settings

### 3. Structured Logging

```python
from mysingle.core import get_structured_logger

logger = get_structured_logger(__name__)

# Basic logging
logger.info("Strategy created", strategy_id="strat-123")

# With context
logger.error(
    "Backtest failed",
    strategy_id="strat-123",
    user_id="user-456",
    error="timeout",
    duration_ms=5000,
)
```

**Output (Production - JSON):**
```json
{
  "timestamp": "2025-12-02T10:30:45.123Z",
  "level": "info",
  "event": "Strategy created",
  "service": "strategy-service",
  "strategy_id": "strat-123",
  "correlation_id": "abc-123-def",
  "user_id": "user-456"
}
```

**Output (Development - Console):**
```
2025-12-02T10:30:45.123Z [info] Strategy created service=strategy-service strategy_id=strat-123
```

### 4. Custom Metrics

```python
from mysingle.core.metrics import get_metrics_collector

collector = get_metrics_collector()

# Counter: Increment on events
collector.increment_counter(
    "strategies_created_total",
    labels={"user_id": "user-123", "type": "momentum"}
)

# Gauge: Set current value
collector.set_gauge("active_backtests", value=15)

# Histogram: Track distributions
collector.record_histogram(
    "backtest_duration_seconds",
    value=42.5,
    labels={"strategy_type": "momentum"}
)
```

### 5. Base Document Classes

```python
from mysingle.core.base import BaseTimeDocWithUserId
from beanie import Indexed

class Strategy(BaseTimeDocWithUserId):
    """Strategy document with automatic timestamps and user tracking"""

    name: Indexed(str)
    description: str
    parameters: dict

    class Settings:
        name = "strategies"
```

**Inherited fields:**
- `id: PydanticObjectId` - Unique identifier
- `created_at: datetime` - Auto-populated on creation
- `updated_at: datetime` - Auto-updated on save
- `user_id: str` - User who created/owns the document

---

## Environment Variables

### Core Settings (CommonSettings)

All services inherit these environment variables:

| Category           | Variables                                                 | Description                 |
| ------------------ | --------------------------------------------------------- | --------------------------- |
| **Project**        | `PROJECT_NAME`, `ENVIRONMENT`, `DEBUG`                    | Basic project configuration |
| **Database**       | `MONGODB_SERVER`, `MONGODB_USERNAME`, `MONGODB_PASSWORD`  | MongoDB connection          |
| **Redis**          | `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD`  | Redis connection            |
| **DuckDB**         | `DUCKDB_PATH`, `DUCKDB_READ_ONLY`                         | DuckDB analytical database  |
| **Authentication** | `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`  | JWT settings                |
| **Kong Gateway**   | `USE_API_GATEWAY`, `API_GATEWAY_URL`, `KONG_JWT_SECRET_*` | Gateway integration         |
| **SMTP**           | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`    | Email configuration         |
| **OAuth2**         | `GOOGLE_CLIENT_ID`, `KAKAO_CLIENT_ID`, etc.               | OAuth providers             |
| **Cache**          | `USER_CACHE_TTL_SECONDS`, `USER_CACHE_KEY_PREFIX`         | User cache settings         |

### Environment-Specific Behavior

| Setting         | Development         | Production  |
| --------------- | ------------------- | ----------- |
| **DEBUG**       | `true`              | `false`     |
| **Log Level**   | `DEBUG`             | `INFO`      |
| **Log Format**  | Color console       | JSON        |
| **CORS**        | Permissive          | Restrictive |
| **Auth Bypass** | Allowed (with flag) | Disabled    |

---

## Service Types

### IAM_SERVICE

**Authentication/Authorization service** managing users and JWT tokens.

**Characteristics:**
- Direct JWT validation
- OAuth2 integration
- User/OAuthAccount collections created
- Issues and verifies tokens

**Example:** `iam-service`

**Configuration:**
```python
config = create_service_config(
    service_name="iam-service",
    service_type=ServiceType.IAM_SERVICE,
)
```

### NON_IAM_SERVICE

**Business logic services** consuming JWT tokens via Kong Gateway.

**Characteristics:**
- Kong Gateway header-based auth (`X-User-Id`, `X-Kong-JWT-Claim-*`)
- No direct JWT validation
- No User collections (reads from IAM via gRPC if needed)
- Focuses on domain logic

**Examples:** `backtest-service`, `ml-service`, `market-data-service`

**Configuration:**
```python
config = create_service_config(
    service_name="backtest-service",
    service_type=ServiceType.NON_IAM_SERVICE,
)
```

---

## Health Checks

All services automatically expose health endpoints:

### GET /health

**Basic health check** - Always returns 200 OK if service is running.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "strategy-service",
  "version": "1.0.0",
  "timestamp": "2025-12-02T10:30:45.123Z"
}
```

### GET /ready

**Readiness check** - Returns 200 only if all dependencies are available.

**Checks:**
- MongoDB connection (if `enable_database=True`)
- Redis connection (if configured)
- Custom health checks (via `register_health_check()`)

```bash
curl http://localhost:8000/ready
```

**Response (healthy):**
```json
{
  "status": "ready",
  "checks": {
    "mongodb": "ok",
    "redis": "ok"
  }
}
```

**Response (unhealthy):**
```json
{
  "status": "not_ready",
  "checks": {
    "mongodb": "ok",
    "redis": "failed: connection refused"
  }
}
```

---

## Observability Stack

### 1. Structured Logging

**Technology:** structlog + Python logging

**Features:**
- JSON output (production)
- Color console (development)
- Correlation ID propagation
- Context variables (user_id, request_id)

**See:** [Structured Logging Guide](../../../docs/core/STRUCTURED_LOGGING_GUIDE.md)

### 2. Metrics

**Technology:** Prometheus client

**Metrics:**
- HTTP request counts, latency, errors
- Custom business metrics (counters, gauges, histograms)
- Percentiles (P50, P90, P95, P99)

**Endpoints:**
- `/metrics/` - JSON summary
- `/metrics/prometheus` - Prometheus exposition format

**See:** [Metrics Guide](../../../docs/core/METRICS_USAGE_GUIDE.md)

### 3. Audit Logging

**Technology:** MongoDB + Beanie ODM

**Captured:**
- User ID, IP address, User-Agent
- Request path, method, status code
- Request/response sizes
- Latency, correlation IDs

**See:** [Audit Logging Guide](../../../docs/core/AUDIT_LOGGING_USAGE_GUIDE.md)

---

## Best Practices

### ✅ DO

```python
# Use app factory for consistent setup
app = create_fastapi_app(service_config=config)

# Inherit from CommonSettings
class Settings(CommonSettings):
    CUSTOM_SETTING: str

# Use structured logging
logger.info("Event occurred", entity_id=id, user_id=user)

# Register custom health checks
register_health_check("external_api", check_external_api)

# Use base document classes
class MyDocument(BaseTimeDocWithUserId):
    pass
```

### ❌ DON'T

```python
# Don't create FastAPI app manually
app = FastAPI()  # Missing auto-configuration!

# Don't duplicate CommonSettings fields
class Settings(BaseSettings):
    MONGODB_SERVER: str  # Already in CommonSettings!

# Don't use print() for logging
print("Something happened")  # Not structured!

# Don't hardcode configuration
MONGODB_URL = "mongodb://localhost"  # Use env vars!

# Don't create timestamp fields manually
class MyDocument(Document):
    created_at: datetime  # Use BaseTimeDoc instead!
```

### Configuration Priority

1. Environment variables (highest priority)
2. `.env` file
3. `CommonSettings` defaults (lowest priority)

### Logging Guidelines

- Use structured fields instead of string formatting
- Include `user_id` and `correlation_id` when available
- Use appropriate log levels:
  - `DEBUG`: Detailed debugging information
  - `INFO`: Normal operational events
  - `WARNING`: Unexpected but handled situations
  - `ERROR`: Errors requiring attention
  - `CRITICAL`: System-level failures

### Metrics Naming

Follow Prometheus naming conventions:

- Use `_total` suffix for counters: `strategies_created_total`
- Use `_seconds` for durations: `backtest_duration_seconds`
- Use descriptive labels: `{"strategy_type": "momentum"}`

---

## Migration from v1.x

### App Creation

**Old (v1.x):**
```python
from mysingle.core import create_app

app = create_app(
    service_name="my-service",
    enable_auth=True,
)
```

**New (v2.x):**
```python
from mysingle.core import create_fastapi_app, create_service_config, ServiceType

config = create_service_config(
    service_name="my-service",
    service_type=ServiceType.IAM_SERVICE,  # or NON_IAM_SERVICE
)
app = create_fastapi_app(service_config=config)
```

### Logging

**Old:**
```python
from mysingle.core import get_logger
logger = get_logger(__name__)
```

**New:**
```python
from mysingle.core import get_structured_logger
logger = get_structured_logger(__name__)
```

### Settings

**Old:**
```python
from mysingle.core.settings import Settings
```

**New:**
```python
from mysingle.core.config import CommonSettings

class Settings(CommonSettings):
    pass
```

---

## Testing

### Unit Tests

```python
import pytest
from mysingle.core import create_service_config, ServiceType

def test_service_config():
    config = create_service_config(
        service_name="test-service",
        service_type=ServiceType.NON_IAM_SERVICE,
    )

    assert config.service_name == "test-service"
    assert config.enable_auth is False
    assert config.is_gateway_downstream is True
```

### Integration Tests

```python
from fastapi.testclient import TestClient
from mysingle.core import create_fastapi_app, create_service_config, ServiceType

@pytest.fixture
def client():
    config = create_service_config(
        service_name="test-service",
        service_type=ServiceType.NON_IAM_SERVICE,
    )
    app = create_fastapi_app(service_config=config)
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Mocking

```python
from unittest.mock import MagicMock, patch

@patch("mysingle.core.config.settings")
def test_with_mocked_settings(mock_settings):
    mock_settings.ENVIRONMENT = "test"
    mock_settings.DEBUG = True
    # Test code here
```

---

## Dependencies

### Required

- `fastapi` - Web framework
- `pydantic >= 2.0` - Data validation
- `pydantic-settings` - Environment configuration
- `structlog` - Structured logging
- `prometheus-client` - Metrics

### Optional

- `motor` + `beanie` - MongoDB ODM (if `enable_database=True`)
- `redis` - Redis cache (if Redis configured)
- `duckdb` - Analytical database (if DuckDB configured)
- `emails` + `jinja2` - Email sending (if SMTP configured)

### Installation

```bash
# Minimal (core only)
pip install mysingle[core]

# With database
pip install mysingle[database]

# With auth
pip install mysingle[auth]

# Full installation
pip install mysingle[full]
```

---

## Troubleshooting

### Issue: App Factory Not Applying Middleware

**Symptom:** Metrics/audit logging not working

**Solution:** Ensure middleware order and `enable_*` flags:

```python
config = create_service_config(
    service_name="my-service",
    service_type=ServiceType.NON_IAM_SERVICE,
    enable_metrics=True,        # Enable metrics
    enable_audit_logging=True,  # Enable audit
)
```

### Issue: Settings Not Loading from .env

**Symptom:** Environment variables ignored

**Solution:** Check `model_config` in Settings class:

```python
class Settings(CommonSettings):
    model_config = SettingsConfigDict(
        env_file=".env",              # Specify .env file
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
```

### Issue: Correlation ID Not Propagating

**Symptom:** Missing correlation IDs in logs

**Solution:** Ensure middleware order (LoggingMiddleware before others):

```python
# App factory handles this automatically
app = create_fastapi_app(service_config=config)
```

### Issue: Health Check Fails

**Symptom:** `/ready` returns 503

**Solution:** Check dependency status:

```bash
# Check MongoDB
mongosh $MONGODB_SERVER

# Check Redis
redis-cli -h $REDIS_HOST ping
```

---

## Related Documentation

- **[App Factory Guide](../../../docs/core/APP_FACTORY_USAGE_GUIDE.md)** - Complete app factory reference
- **[Structured Logging Guide](../../../docs/core/STRUCTURED_LOGGING_GUIDE.md)** - Logging system details
- **[Metrics Guide](../../../docs/core/METRICS_USAGE_GUIDE.md)** - Metrics collection and exposition
- **[Audit Logging Guide](../../../docs/core/AUDIT_LOGGING_USAGE_GUIDE.md)** - Audit trail implementation
- **[Common Settings Guide](../../../docs/core/COMMON_SETTINGS_GUIDE.md)** - Configuration management
- **[Database Module README](../database/README.md)** - MongoDB, Redis, DuckDB usage
- **[Auth Module README](../auth/README.md)** - Authentication and authorization

---

**Platform:** MySingle Quant (Beta: Early 2026)
**License:** MIT

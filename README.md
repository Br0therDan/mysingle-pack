# MySingle Package

**Version:** 2.2.1 | **Updated:** 2025-12-02

Unified platform package for MySingle Quant microservices ecosystem.

---

## Overview

MySingle is a comprehensive Python package providing standardized infrastructure, authentication, database management, and utilities for building production-ready microservices in the MySingle Quant platform.

### Key Features

- **🏗️ App Factory:** Zero-config FastAPI application setup with auto-middleware
- **🔐 Authentication:** Kong Gateway integration with JWT and OAuth2 support
- **📊 Observability:** Built-in structured logging, metrics, and audit trails
- **💾 Database:** MongoDB, Redis, DuckDB integration with connection pooling
- **🔄 Service Communication:** gRPC clients with metadata propagation
- **📝 DSL Engine:** Safe code execution for user-defined strategies
- **🛠️ CLI Tools:** Version management and submodule workflows

---

## Installation

### From Git Repository

```bash
# Latest stable version
pip install git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.1

# Development version
pip install git+https://github.com/Br0therDan/mysingle-pack.git@main
```

### With Optional Dependencies

```bash
# Recommended: Common services (auth + database + web)
pip install "git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.1#egg=mysingle[common-grpc]"

# Full installation
pip install "git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.1#egg=mysingle[full]"

# Individual extras
pip install "mysingle[auth]"        # Authentication module
pip install "mysingle[database]"    # Database integrations
pip install "mysingle[dsl]"         # DSL engine
pip install "mysingle[grpc]"        # gRPC support
pip install "mysingle[clients]"     # Service clients
```

**Available Extras:**
- `auth` - JWT, OAuth2, Kong Gateway integration
- `database` - MongoDB, Redis, DuckDB
- `dsl` - Strategy DSL parser
- `grpc` - gRPC interceptors
- `clients` - HTTP/gRPC clients
- `common` - auth + database + web
- `common-grpc` - common + grpc + clients
- `full` - All modules

---

## Package Structure

| Module                                          | Description                                                       | Documentation                  |
| ----------------------------------------------- | ----------------------------------------------------------------- | ------------------------------ |
| **[core](src/mysingle/core/README.md)**         | Application factory, logging, metrics, health checks, audit       | Core infrastructure utilities  |
| **[auth](src/mysingle/auth/README.md)**         | JWT validation, OAuth2, Kong Gateway auth, user management        | Authentication & authorization |
| **[database](src/mysingle/database/README.md)** | MongoDB (Beanie), Redis cache, DuckDB analytics                   | Database integrations          |
| **[dsl](src/mysingle/dsl/README.md)**           | Safe Python execution for user strategies, 60+ built-in functions | Strategy DSL engine            |
| **[clients](src/mysingle/clients/README.md)**   | gRPC/HTTP clients with Kong auth propagation                      | Service communication          |
| **[grpc](src/mysingle/grpc/README.md)**         | gRPC interceptors for logging, metrics, auth                      | gRPC middleware                |
| **[protos](src/mysingle/protos/README.md)**     | Protocol Buffers definitions for all services                     | Service contracts              |
| **[cli](src/mysingle/cli/README.md)**           | CLI tools for version management and submodules                   | Development tools              |

---

## Quick Start

### 1. Create a Service

```python
from mysingle.core import create_fastapi_app, create_service_config, ServiceType

# Configure service
config = create_service_config(
    service_name="strategy-service",

    service_version="1.0.0",
)

# Create app with auto-configuration
app = create_fastapi_app(service_config=config)
```

**What you get automatically:**
- ✅ Structured logging (JSON in production)
- ✅ Prometheus metrics at `/metrics/`
- ✅ Health checks at `/health` and `/ready`
- ✅ Audit logging middleware
- ✅ Kong Gateway authentication
- ✅ MongoDB connection (if enabled)

### 2. Use Authentication

```python
from mysingle.auth import get_user_id, authorized
from fastapi import Request

@app.get("/strategies")
async def list_strategies(request: Request):
    user = get_current_active_verified_user(request)
    return await get_user_strategies(user_id)
```

### 3. Database Operations

```python
from mysingle.core.base import BaseTimeDocWithUserId
from mysingle.database import get_redis_client

# MongoDB document
class Strategy(BaseTimeDocWithUserId):
    name: str
    code: str

    class Settings:
        name = "strategies"

# Redis cache
redis = await get_redis_client(db=1)
await redis.setex("ticker:AAPL", 60, "150.25")
```

### 4. Service Communication

```python
from mysingle.grpc import BaseGrpcClient

class BacktestClient(BaseGrpcClient):
    def __init__(self, user_id=None):
        super().__init__("backtest-service", 50052, user_id=user_id)
        self.stub = backtest_pb2_grpc.BacktestServiceStub(self.channel)

async with BacktestClient(user_id=user.id) as client:
    result = await client.stub.RunBacktest(request)
```

---

## Module Overview

### Core (`mysingle.core`)

Central infrastructure for all services.

**Features:**
- FastAPI app factory with auto-middleware
- Structured logging with correlation IDs
- Prometheus metrics collection
- Health check endpoints
- Audit logging
- Base document classes

**Common Patterns:**
- Service initialization
- Configuration management
- Logging and metrics
- Health monitoring

📖 **[Read Core Documentation →](src/mysingle/core/README.md)**

---

### Auth (`mysingle.auth`)

Authentication and authorization for IAM and downstream services.

**Features:**
- Kong Gateway integration
- JWT token validation
- OAuth2 (Google, Kakao, Naver)
- User management (IAM only)
- Redis user cache

**Service Types:**
- **IAM Service:** Issues and validates tokens
- **Non-IAM Service:** Consumes Kong headers

📖 **[Read Auth Documentation →](src/mysingle/auth/README.md)**

---

### Database (`mysingle.database`)

Integrated database management with connection pooling.

**Features:**
- **MongoDB:** Beanie ODM with base document classes
- **Redis:** Multi-DB cache with connection pooling
- **DuckDB:** Analytical queries with TTL cache

**Components:**
- `BaseDuckDBManager` - DuckDB wrapper
- `RedisClientManager` - Redis connection pool
- `BaseRedisCache[T]` - Type-safe cache

📖 **[Read Database Documentation →](src/mysingle/database/README.md)**

---

### DSL (`mysingle.dsl`)

Safe execution engine for user-defined strategies.

**Features:**
- RestrictedPython sandbox
- 60+ built-in functions (SMA, EMA, crossover, etc.)
- Resource limits (CPU, memory)
- Bytecode compilation/caching
- Parameter injection

**Use Cases:**
- Technical indicators
- Trading signals
- Backtesting strategies

📖 **[Read DSL Documentation →](src/mysingle/dsl/README.md)**

---

### Clients (`mysingle.clients`)

Service-to-service communication.

**Features:**
- **BaseGrpcClient:** gRPC with metadata propagation
- **ServiceHttpClient:** HTTP with Kong auth
- Connection pooling
- Health checks
- Error handling

**Metadata Auto-Injection:**
- `user-id`
- `correlation-id`
- `request-id`
- `authorization`

📖 **[Read Clients Documentation →](src/mysingle/clients/README.md)**

---

### gRPC (`mysingle.grpc`)

gRPC middleware and interceptors.

**Features:**
- Logging interceptor
- Metrics interceptor
- Auth interceptor
- Error handling

📖 **[Read gRPC Documentation →](src/mysingle/grpc/README.md)**

---

### Protos (`mysingle.protos`)

Protocol Buffers service definitions.

**Services:**
- IAM (user, auth)
- Backtest
- ML/Indicator
- Strategy
- Market Data

📖 **[Read Protos Documentation →](src/mysingle/protos/README.md)**

---

### CLI (`mysingle.cli`)

Command-line tools for development.

**Tools:**
- `mysingle` - Version and submodule management
- `mysingle-proto` - Protocol Buffer operations

📖 **[Read CLI Documentation →](src/mysingle/cli/README.md)**

---

## Development Workflow

### As Git Submodule (Recommended)

MySingle is designed to be used as a Git submodule in microservice repositories for cross-repository development.

#### 1. Add Submodule to Your Service

```bash
cd /path/to/your-service

# Interactive mode (recommended)
mysingle submodule add

# Manual mode
git submodule add https://github.com/Br0therDan/mysingle-pack.git packages/mysingle
cd packages/mysingle
git checkout main
```

#### 2. Install in Development Mode

```bash
# In your service repository
cd packages/mysingle
pip install -e ".[full]"
```

#### 3. Develop and Test

```python
# Make changes to mysingle in packages/mysingle/
# Test in your service immediately

# Example: Edit proto files
vim packages/mysingle/protos/services/user/v1/user_service.proto

# Generate stubs
cd packages/mysingle
mysingle-proto generate

# Test in your service
pytest tests/
```

#### 4. Submit PR to MySingle

```bash
# Prepare changes for PR
mysingle submodule sync

# Follow interactive prompts to:
# 1. Create feature branch
# 2. Commit changes
# 3. Push to fork
# 4. Open PR via browser
```

#### 5. Update After PR Merge

```bash
# Update to latest version
mysingle submodule update

# Commit submodule update in your service
git add packages/mysingle
git commit -m "chore: update mysingle to v2.2.1"
```

📖 **[Complete Submodule Workflow Guide →](docs/cicd/SUBMODULE_PR_WORKFLOW.md)**

---

## CI/CD Integration

### GitHub Actions Workflows

MySingle includes automated workflows:

| Workflow                 | Trigger                          | Purpose                           |
| ------------------------ | -------------------------------- | --------------------------------- |
| **auto-release.yml**     | `pyproject.toml` changes on main | Create GitHub Release + Git Tag   |
| **validate-commits.yml** | Pull Request                     | Validate Conventional Commits     |
| **proto-ci.yml**         | Proto file changes               | Validate + Generate + Auto-commit |

### Version Management

```bash
# Automatic version bump (analyzes commits)
mysingle version auto --push

# Manual version bump
mysingle version patch  # 2.2.0 → 2.2.1
mysingle version minor  # 2.2.0 → 2.3.0
mysingle version major  # 2.2.0 → 3.0.0
```

**Conventional Commits:**
- `fix:` → Patch version
- `feat:` → Minor version
- `BREAKING CHANGE:` → Major version

### Service Updates

```bash
# In your service repository
cd packages/mysingle
git pull origin main

# Or use CLI
mysingle submodule update
```

---

## Testing

### Running Tests

```bash
# Recommended: Use test runner script
./run_tests.sh

# Direct pytest (with coverage)
pytest tests/ -v --cov=src/mysingle --cov-report=html

# Run specific module tests
pytest tests/core/ -v
pytest tests/auth/ -v
pytest tests/database/ -v

# Run with markers
pytest -m "not slow"              # Skip slow tests
pytest -m "not e2e"               # Skip end-to-end tests
pytest -m unit                    # Only unit tests
```

### Test Configuration

Tests are configured via `pytest.ini`:

- **Test Discovery:** `tests/` directory, `test_*.py` files
- **Coverage:** Source in `src/mysingle/`, excludes generated proto files
- **Async Mode:** Auto-detection with pytest-asyncio
- **Markers:** `unit`, `integration`, `slow`, `e2e`

### Coverage Reports

After running tests with coverage:

```bash
# View HTML report
open htmlcov/index.html

# View terminal summary
cat coverage.xml | grep line-rate
```

**Target Coverage:** 80%+ for core modules

### Test Environment Setup

```bash
# Set test environment variables
export MYSINGLE_AUTH_BYPASS=true
export ENVIRONMENT=development

# Or use the test runner (automatically sets these)
./run_tests.sh
```

**Note:** Auth bypass is automatically disabled in production environments.

---

## Contributing

### Local Development

```bash
git clone https://github.com/Br0therDan/mysingle-pack.git
cd mysingle-pack
pip install -e ".[full,dev]"
```

### Code Quality

```bash
# Linting
ruff check src/ tests/

# Formatting
ruff format src/ tests/

# Type checking
mypy src/
```

### Proto Management

```bash
# Generate stubs
mysingle-proto generate

# Validate
mysingle-proto validate --breaking
```

---

## Environment Variables

MySingle uses environment-based configuration with Pydantic Settings.

### Quick Setup

```bash
# Copy example configuration
cp .env.example .env

# Edit with your values
vim .env
```

### Configuration Files

- **[.env.example](.env.example)** - Complete environment variable reference
- **[Core Module - Environment Variables](src/mysingle/core/README.md#environment-variables)** - Detailed documentation

### Key Variables

| Category         | Variables                                    | Description             |
| ---------------- | -------------------------------------------- | ----------------------- |
| **Project**      | `ENVIRONMENT`, `DEBUG`                       | Runtime environment     |
| **Database**     | `MONGODB_SERVER`, `REDIS_HOST`               | Database connections    |
| **Auth**         | `SECRET_KEY`, `KONG_JWT_SECRET_SERVICE_NAME` | Authentication          |
| **Kong Gateway** | `USE_API_GATEWAY`, `API_GATEWAY_URL`         | API Gateway integration |
| **OAuth2**       | `GOOGLE_CLIENT_ID`, `KAKAO_CLIENT_ID`, etc.  | Social login providers  |

**For complete list:** See [.env.example](.env.example)

---

## Documentation

### Module Guides
- **[Core Module](src/mysingle/core/README.md)** - App factory, logging, metrics, health
- **[Auth Module](src/mysingle/auth/README.md)** - Authentication and authorization
- **[Database Module](src/mysingle/database/README.md)** - MongoDB, Redis, DuckDB
- **[DSL Module](src/mysingle/dsl/README.md)** - Strategy execution engine
- **[Clients Module](src/mysingle/clients/README.md)** - Service communication
- **[gRPC Module](src/mysingle/grpc/README.md)** - gRPC middleware
- **[Protos Module](src/mysingle/protos/README.md)** - Service contracts
- **[CLI Module](src/mysingle/cli/README.md)** - Development tools

### Specialized Guides
- **[App Factory Usage](docs/core/APP_FACTORY_USAGE_GUIDE.md)** - FastAPI app creation patterns
- **[Structured Logging](docs/core/STRUCTURED_LOGGING_GUIDE.md)** - Logging architecture
- **[Metrics Collection](docs/core/METRICS_USAGE_GUIDE.md)** - Prometheus integration
- **[Audit Logging](docs/core/AUDIT_LOGGING_USAGE_GUIDE.md)** - Compliance tracking
- **[Common Settings](docs/core/COMMON_SETTINGS_GUIDE.md)** - Configuration patterns

### Workflow Guides
- **[Submodule PR Workflow](docs/cicd/SUBMODULE_PR_WORKFLOW.md)** - Cross-repo development process

---

## Support

- **Issues:** [GitHub Issues](https://github.com/Br0therDan/mysingle-pack/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Br0therDan/mysingle-pack/discussions)
- **Documentation:** [docs/](docs/)

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

## Version History

### v2.2.1 (2025-12-02)
- ✨ Redis infrastructure with multi-DB support
- 📚 Comprehensive module documentation
- 🔧 CLI tools for submodule management
- 🏗️ App factory improvements

### v2.0.0 (2025-11-15)
- 🎯 Module restructuring (Phase 0)
- 📦 Optional dependencies
- 🚀 Git-based installation

**For full changelog:** [CHANGELOG.md](CHANGELOG.md)

---

**Platform:** MySingle Quant (Beta: Early 2026)
**Maintained by:** MySingle Team
**Repository:** https://github.com/Br0therDan/mysingle-pack

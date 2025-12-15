"""Template generators for scaffolding services."""

from __future__ import annotations


def generate_agents_md(service_name: str, service_name_pascal: str) -> str:
    """Generate AGENTS.md template."""
    service_title = service_name.replace("-", " ").title()
    return f"""# {service_title} - Agent Instructions

**Version**: 1.0.0
**Date**: {{% import datetime %}}{{{{ datetime.date.today() }}}}

---

## 1. Phase Planning

### Before Starting a Phase
- Review MASTER_PLAN.md and PROJECT_DASHBOARD.md
- Create detailed plan: `PHASE{{N}}_{{DESCRIPTION}}.md`
- DO NOT include time estimates (weeks/days)

### Phase Plan Structure
- Tasks formatted as: `[ ] P{{Phase#}}-{{Task#}}. {{Task Name}}`
- Each Task includes:
  - **Purpose**: Goal of the task
  - **Implementation Details**: Technical requirements
  - **Deliverables**: Files/documents to create
  - **Completion Criteria**: Clear acceptance criteria
- NO example code in planning documents

---

## 2. Task Execution

### Task Completion Criteria (ALL required)
1. **Code Quality**
   - `ruff check` pass (0 lint errors)
   - `ruff format` applied
   - Type validation pass (mypy/pyright 0 errors)

2. **Testing**
   - Unit tests written and passing
   - Skip only if test not applicable (e.g., docs)

3. **Documentation**
   - Update PROJECT_DASHBOARD.md: `[ ]` → `[x]`
   - NO modifications to completed task details

### Git Workflow
**Task completion:**
```bash
git commit -m "P{{Phase#}}-{{Task#}}: {{Task Name}} completed

{{Brief implementation summary}}"
```

**Phase completion:**
```bash
git commit -m "Phase {{N}} completed: {{Phase Name}}

- {{N}} tasks completed
- {{N}} unit tests passed
- Deliverables: {{file list}}"
```

### Phase Completion Criteria (ALL required)
- All tasks completed
- All unit tests passing (80%+ coverage)
- PROJECT_DASHBOARD.md updated (⚪ → 🟡 → 🟢)
- NO additional summary documents

---

## 3. Code Standards

### Type Safety
- Type hints required for all functions/methods
- Use Pydantic models (NO dicts)
- IDs as `str`, convert to `PydanticObjectId` only at query boundaries

### Beanie Models
- User-owned: `BaseTimeDocWithUserId`
- Shared: `BaseTimeDoc`
- Simple: `BaseDoc`

### Response Schemas
- Inherit `BaseResponseSchema`
- Naming: `{{Entity}}Response`
- Return: `model_dump(by_alias=True)`

### Logging
- Use `get_structured_logger(__name__)` (mysingle.core.logging)
- NO `print()` or standard logging
- Include context: `user_id`, `correlation_id`, `operation`

### Authentication
- External API: `get_verified_user_id(request)`
- Internal API: `get_user_id(request)`
- ALWAYS filter user-owned resources by `user_id`

### Error Handling
- Define custom exceptions in `app/core/exceptions.py`
- Use `HTTPException(status_code, detail)`
- Status codes: 401 (unauthorized), 403 (forbidden), 404 (not found), 400 (bad request), 500 (server error)

---

## 4. Testing

### Unit Tests
- Location: `tests/unit/`
- Naming: `test_{{module_name}}.py`
- Use pytest fixtures

### Integration Tests
- Location: `tests/integration/`
- Mock external services (Redis, MongoDB)

---

## 5. Anti-Patterns

### Prohibited
- ❌ Jumping between phases (complete Phase 1 before Phase 2)
- ❌ Modifying completed task details
- ❌ Creating unnecessary summary documents
- ❌ Including code examples in planning docs
- ❌ Using `print()` or standard logging
- ❌ Using dicts instead of Pydantic models
- ❌ Querying all docs without user_id filter

### Recommended
- ✅ Sequential phase execution
- ✅ Commit after each task completion
- ✅ Test-driven development
- ✅ Structured logging with context
- ✅ Explicit type hints

---

## 6. MySingle Package Patterns

### Settings Configuration
- Extend `CommonSettings` from `mysingle.core.config`
- DO NOT redefine CommonSettings fields (MONGODB_URL, REDIS_HOST, etc.)
- Override defaults via environment variables only

### Authentication (NON_IAM Service)
- Import from `mysingle.auth`: `get_user_id`, `get_verified_user_id`
- External API: `get_verified_user_id(request)` - raises 401/403
- Internal API: `get_user_id(request)` - service-to-service only
- User info from Kong Gateway headers (`X-User-Id`, `X-Correlation-Id`)
- NO MongoDB user lookup in NON_IAM services

### Database Initialization
- Create `app/models/__init__.py` with `document_models = [Model1, Model2]`
- Pass to `create_fastapi_app(document_models=document_models)`
- Beanie auto-initialized on startup via `app_factory`
- NO manual `init_beanie()` calls needed

### Dependencies Pattern
```python
from fastapi import Request
from mysingle.auth import get_verified_user_id
from app.core.config import get_settings

# Direct usage (recommended)
async def route(request: Request):
    user_id = get_verified_user_id(request)
    settings = get_settings()
```

### App Factory (NON_IAM Service)
```python
from mysingle.core import create_fastapi_app, create_service_config, ServiceType

config = create_service_config(
    service_name="{service_name}",

)

app = create_fastapi_app(
    service_config=config,
    document_models=models.document_models,
)
```

---

## References
- [.github/copilot-instructions.md](./.github/copilot-instructions.md): Development guidelines
- [MySingle Package Docs](https://github.com/Br0therDan/mysingle-pack/tree/main/docs): API documentation
"""


def generate_copilot_instructions_md(
    service_name: str, service_name_pascal: str
) -> str:
    """Generate .github/copilot-instructions.md template."""
    service_title = service_name.replace("-", " ").title()
    return f"""# {service_title} - Development Guidelines

## Architecture Principles

- Kong Gateway for all HTTP traffic (no direct service HTTP calls)
- gRPC for inter-service communication only
- Auth: Kong JWT + `X-User-Id` header propagation
- Proto: https://github.com/Br0therDan/grpc-protos

---

## Type Safety & Models

**Pydantic Everywhere:** No raw dicts in routes/services. Define schemas in `app/schemas/<domain>.py`.
**Beanie Inheritance:**

- User-owned: `BaseTimeDocWithUserId`
- Shared: `BaseTimeDoc`
- Simple: `BaseDoc`

**Response Schemas:** Inherit `BaseResponseSchema`, name as `<Entity>Response`, construct via `model_dump(by_alias=True)`.
**IDs:** Use `str` in schemas/docs, convert to `PydanticObjectId` only at query boundaries.
**DateTime:** Use `datetime.now(UTC)` not `utcnow()`.
**Return Types:** All route functions require type hints.

---

## Directory Structure

- Models (ODM): `app/models/` (inherit mysingle.base)
- Public schemas: `app/schemas/<domain>.py`
- Internal models: `app/services/<domain>/models.py`
- External clients: `app/clients/`
- No inline schemas in routers

---

## Configuration & Logging

**Settings:** Extend `CommonSettings` from mysingle.core. Env vars: `<SERVICE>_<FEATURE>_<PROPERTY>`. Access via `get_settings()`.
**Logging:** Use `get_structured_logger(__name__)` from mysingle.core.logging. Never `print()` or standard logging. Include context keys (user_id, correlation_id).
**Audit:** Auto-enabled in production. Add custom metadata via `request.state.audit_metadata`.

---

## Authentication

**Import:** `mysingle.auth` provides `get_user_id`, `get_verified_user_id`, `get_kong_user_id`, `get_kong_correlation_id`.
**External API:** Use `get_verified_user_id(request)` (raises 401).
**Internal API:** Use `get_user_id(request)` (service-to-service only).
**User Ownership:** ALWAYS filter by `user_id` before returning/modifying resources.
**Testing:** Set `MYSINGLE_AUTH_BYPASS=true` and `ENVIRONMENT=development`.

---

## Database

**MongoDB:**

- Inherit `BaseTimeDocWithUserId` for user-scoped
- Filter: `Model.find(Model.user_id == user_id)`
- Avoid N+1: batch fetch → map join
- Index: `(user_id, created_at desc)`

**Redis:**

- Get client: `get_redis_client(db=N)`
- DB allocation: 0=IAM, 1=Market, 2=Indicators, 3=Strategies, 4=Backtests
- Key format: `{{resource}}:{{user_id}}:{{resource_id}}`

**Idempotency:** Support `Idempotency-Key` header, cache in Redis (TTL: 86400s).

---

## gRPC Communication

**Client:** Extend `BaseGrpcClient(service_name, port, user_id, correlation_id)` - auto-propagates metadata headers (user-id, correlation-id, request-id).
**Package:** `mysingle-protos @ git+https://github.com/Br0therDan/grpc-protos.git@v1.x.x`

**Versioning:** Major=breaking, Minor=new features, Patch=fixes.

---

## Routing

**External Router:** Public CRUD endpoints. Use `get_verified_user_id(request)`.
**Internal Router:** Service-to-service triggers. Use `get_user_id(request)`. NOT exposed via Kong.
**Registration:** Include router with prefix, tags, dependencies (auth required).

---

## Error Handling

**Custom Exceptions:** Define narrow exceptions (e.g., `ValidationError`, `ResourceNotFoundError`).
**HTTP Errors:** Use `HTTPException(status_code, detail)`. Status codes: 401=unauthenticated, 403=forbidden, 404=not found, 400=bad request, 500=server error.
**Logging:** Log with context (service, operation, IDs). Re-raise IO/network errors.

---

## File Operations

**Replacement Pattern:** Create `file_new.py` → delete `file.py` → rename `file_new.py` to `file.py`.

---

## MySingle Package Updates

**Submodule add / update / Sync:**:
- To add: `uv run mysingle submodule add`
- To update: `uv run mysingle submodule update`
- To sync: `uv run mysingle submodule sync`

**Proto Changes (Owner):**

1. Edit `packages/mysingle/protos/services/{'service'}/v1/*.proto`
2. Validate: `uv run mysingle-proto validate`
3. Generate: `uv run mysingle-proto generate`
4. Submit PR: `uv run mysingle submodule sync`

**Proto Changes (Consumer):** Create issue or PR in mysingle-pack repo.

---

## Anti-Patterns

❌ Service-to-service HTTP (bypass Kong)
❌ Mixed HTTP/gRPC for same service
❌ Manual auth without mysingle.auth
❌ Missing user_id/correlation_id propagation
❌ Hard-coded URLs/ports
❌ Exposing internal routes via Kong
❌ N+1 queries
❌ Missing user_id filters
❌ Using print() or standard logging
❌ Querying all docs without user scope
❌ Creating User/OAuthAccount in non-IAM services

---

## Service Infrastructure

| Service      | HTTP  | gRPC   | Kong Path     |
| ------------ | ----- | ------ | ------------- |
| IAM          | :8001 | :50051 | /iam          |
| Subscription | :8002 | :50052 | /subscription |
| Strategy     | :8003 | :50053 | /strategy     |
| Backtest     | :8004 | :50054 | /backtest     |
| Indicator    | :8005 | :50055 | /indicator    |
| Portfolio    | :8006 | :50056 | /portfolio    |
| Dashboard    | :8007 | :50057 | /dashboard    |
| Notification | :8008 | :50058 | /notification |
| Market Data  | :8009 | :50059 | /market-data  |
| GenAI        | :8010 | :50060 | /genai        |
| ML           | :8011 | :50061 | /ml           |

**MongoDB:** `db-mongo:27017`
**Redis:** `db-redis:6379`
**Kong:** `kong-gateway:8000` (Admin: :8100)

---

**Repos:** [mysingle-quant](https://github.com/Br0therDan/mysingle-quant) | [grpc-protos](https://github.com/Br0therDan/grpc-protos) | [mysingle-pack](https://github.com/Br0therDan/mysingle-pack)
"""


def generate_dockerignore() -> str:
    """Generate .dockerignore template."""
    return """# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/
.mypy_cache/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
.venv/
venv/

# Development files
*.log
*.tmp

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Testing
tests/
*.test.py
test_*.py

# Documentation
docs/

# CI/CD
.github/
"""


def generate_pre_commit_config() -> str:
    """Generate .pre-commit-config.yaml template."""
    return """# Pre-commit hooks for code quality and formatting
repos:
  # Basic file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
        exclude: '\\.vscode/.*\\.json$'
      - id: check-toml
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ["--maxkb=1000"]
      - id: check-case-conflict

  # Linting and formatting with Ruff (replaces Black + Flake8)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format

  # Security checks with Bandit
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.10
    hooks:
      - id: bandit
        args: ["-s", "B311,B110", "--severity-level", "medium"]
        exclude: "^tests/"

# Global settings
default_language_version:
  python: python3.12

# Files to exclude from all hooks
exclude: |
  (?x)^(
    data/.*|
    logs/.*|
    .*\\.log|
    .*\\.cache/.*|
    \\.vscode/.*|
    __pycache__/.*|
    build/.*|
    dist/.*
  )$
"""


def generate_conftest_py(service_name: str) -> str:
    """Generate tests/conftest.py template."""
    service_db_name = service_name.replace("-", "_")
    return f'''"""Pytest configuration and fixtures."""

from unittest.mock import MagicMock, patch

import pytest
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    import os

    # Auth bypass for tests
    os.environ["MYSINGLE_AUTH_BYPASS"] = "true"
    os.environ["ENVIRONMENT"] = "development"


@pytest.fixture(scope="session")
async def init_test_db():
    """Initialize test database and Beanie ODM with mongomock."""
    from app.models import document_models

    # Use mongomock for unit tests (no real MongoDB needed)
    client = AsyncMongoMockClient()
    db = client.get_database("{service_db_name}_test")

    # Initialize Beanie with all document models
    await init_beanie(database=db, document_models=document_models)  # type: ignore

    yield db

    # Cleanup
    client.close()


@pytest.fixture(autouse=True)
async def setup_db(init_test_db):
    """Ensure database is initialized for each test."""
    yield init_test_db


@pytest.fixture(scope="session")
def test_app():
    """Create FastAPI test app with settings mock."""
    # Mock settings before importing app
    with patch("app.core.config.get_settings") as mock_settings:
        mock_settings.return_value.SERVICE_NAME = "{service_name}"
        mock_settings.return_value.MONGODB_URL = "mongodb://localhost:27017"
        from app.main import app

        return app


@pytest.fixture(scope="session")
def test_client(test_app):
    """Create test client."""
    from fastapi.testclient import TestClient

    return TestClient(test_app)
'''


def generate_main_py(
    service_name: str, service_name_snake: str, grpc_enabled: bool
) -> str:
    """Generate main.py content."""
    return f'''"""
{service_name.replace("-", " ").title()} - Main Application Entrypoint
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI
from mysingle.core import (
    create_fastapi_app,
    create_service_config,
    get_structured_logger,
    setup_logging,
)

from app.api.v1.api_v1 import api_router
from app.core.config import settings
from app.models import document_models
from app.services.service_factory import get_service_factory

setup_logging(service_name=settings.SERVICE_NAME)
logger = get_structured_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    App lifecycle for efficient resource management.

    - Initialize shared singletons (HTTP clients, service factory)
    - Ensure graceful shutdown of resources
    """
    logger.info(f"🚀 Starting {service_name.replace("-", " ").title()}...")

    try:
        # Initialize service factory
        factory = get_service_factory()
        await factory.initialize()
        logger.info("✅ Service factory initialized")

    except Exception as e:
        logger.error(f"❌ Startup failed: {{e}}")
        raise

    logger.info(f"✅ {service_name.replace("-", " ").title()} started successfully")

    yield

    # Shutdown
    try:
        logger.info(f"🛑 Shutting down {service_name.replace("-", " ").title()}...")

        # Cleanup service factory
        factory = get_service_factory()
        await factory.shutdown()
        logger.info("✅ Service factory cleanup completed")

    except Exception as e:
        logger.error(f"❌ Shutdown error: {{e}}")

    logger.info(f"👋 {service_name.replace("-", " ").title()} shutdown completed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    # Create ServiceConfig for Non-IAM service (gateway handles auth)
    service_config = create_service_config(

        service_name=settings.SERVICE_NAME,
        service_version=settings.APP_VERSION,
        description="{service_name.replace("-", " ").title()}",
        enable_audit_logging=settings.AUDIT_LOGGING_ENABLED,
        enable_metrics=True,
        lifespan=lifespan,
    )

    # Create standardized FastAPI app using mysingle factory
    app = cast(
        FastAPI,
        create_fastapi_app(
            service_config=service_config,
            document_models=document_models,
        ),
    )

    # Include API router
    app.include_router(api_router)

    return app


# Application instance
app = create_app()
'''


def generate_config_py(
    service_name: str, service_name_snake: str, grpc_enabled: bool
) -> str:
    """Generate config.py content."""
    grpc_settings = ""
    if grpc_enabled:
        grpc_settings = f"""
    # gRPC Settings
    USE_GRPC: bool = True
    GRPC_CLIENT_TIMEOUT: float = 10.0
    {service_name_snake.upper()}_GRPC_PORT: int = 50051
"""

    return f'''"""{service_name.replace("-", " ").title()} Configuration."""

from mysingle.core import CommonSettings


class Settings(CommonSettings):
    """{service_name.replace("-", " ").title()} settings extending CommonSettings."""

    # Service Info
    SERVICE_NAME: str = "{service_name}"
    APP_VERSION: str = "0.1.0"

    # Feature Settings
    AUDIT_LOGGING_ENABLED: bool = True
{grpc_settings}
    # Common service endpoints (from main .env)
    IAM_HOST: str = "localhost"
    STRATEGY_HOST: str = "localhost"
    BACKTEST_HOST: str = "localhost"
    INDICATOR_HOST: str = "localhost"
    PORTFOLIO_HOST: str = "localhost"
    NOTIFICATION_HOST: str = "localhost"
    MARKET_DATA_HOST: str = "localhost"
    GENAI_HOST: str = "localhost"
    ML_HOST: str = "localhost"

    # gRPC Ports (from main .env)
    IAM_GRPC_PORT: int = 50051
    STRATEGY_GRPC_PORT: int = 50053
    BACKTEST_GRPC_PORT: int = 50054
    INDICATOR_GRPC_PORT: int = 50055
    PORTFOLIO_GRPC_PORT: int = 50056
    NOTIFICATION_GRPC_PORT: int = 50058
    MARKET_DATA_GRPC_PORT: int = 50059
    GENAI_GRPC_PORT: int = 50060
    ML_GRPC_PORT: int = 50061


settings = Settings()


'''


def generate_api_v1_py() -> str:
    """Generate api_v1.py content."""
    return '''"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.routes import health, items

api_router = APIRouter(prefix="/api/v1")

# Sample Item routes
api_router.include_router(items.router, prefix="/items", tags=["items"])
'''


def generate_sample_item_model() -> str:
    """Generate sample item model (app/models/item.py)."""
    return '''"""Sample Item model."""

from beanie import PydanticObjectId
from pydantic import Field

from mysingle.core.base import BaseTimeDocWithUserId


class SampleItem(BaseTimeDocWithUserId):
    """Sample item document model.

    Demonstrates user-owned resource with CRUD operations.
    """

    name: str = Field(..., description="Item name")
    description: str | None = Field(None, description="Item description")
    quantity: int = Field(default=0, ge=0, description="Item quantity")
    is_active: bool = Field(default=True, description="Whether item is active")

    class Settings:
        """Beanie document settings."""

        name = "sample_items"
        indexes = [
            "user_id",
            "name",
            ("user_id", "created_at"),
        ]
'''


def generate_sample_item_schema() -> str:
    """Generate sample item schemas (app/schemas/item.py)."""
    return '''"""Sample Item schemas."""

from pydantic import Field

from mysingle.core.base import BaseResponseSchema


class SampleItemCreate(BaseResponseSchema):
    """Schema for creating a sample item."""

    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: str | None = Field(None, max_length=500, description="Item description")
    quantity: int = Field(default=0, ge=0, description="Item quantity")
    is_active: bool = Field(default=True, description="Whether item is active")


class SampleItemUpdate(BaseResponseSchema):
    """Schema for updating a sample item."""

    name: str | None = Field(None, min_length=1, max_length=100, description="Item name")
    description: str | None = Field(None, max_length=500, description="Item description")
    quantity: int | None = Field(None, ge=0, description="Item quantity")
    is_active: bool | None = Field(None, description="Whether item is active")


class SampleItemResponse(BaseResponseSchema):
    """Schema for sample item response."""

    id: str = Field(..., description="Item ID")
    user_id: str = Field(..., description="Owner user ID")
    name: str = Field(..., description="Item name")
    description: str | None = Field(None, description="Item description")
    quantity: int = Field(..., description="Item quantity")
    is_active: bool = Field(..., description="Whether item is active")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
'''


def generate_sample_item_router() -> str:
    """Generate sample item router (app/api/v1/routes/items.py)."""
    return '''"""Sample Item CRUD endpoints."""

from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Request, status, Depends
from mysingle.auth import get_user_id, authorized
from mysingle.core import get_structured_logger

from app.models.item import SampleItem
from app.schemas.item import SampleItemCreate, SampleItemResponse, SampleItemUpdate

router = APIRouter()
logger = get_structured_logger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SampleItemResponse)
@authorized
async def create_item(
    item_data: SampleItemCreate,
    user_id: str = Depends(get_user_id),
) -> SampleItemResponse:
    """
    Create a new sample item.

    - **name**: Item name (required)
    - **description**: Item description (optional)
    - **quantity**: Item quantity (default: 0)
    - **is_active**: Whether item is active (default: true)
    """

    logger.info(
        "Creating sample item",
        user_id=user_id,
        item_name=item_data.name,
    )

    # Create item with user ownership
    item = SampleItem(
        user_id=user_id,
        **item_data.model_dump(exclude_unset=True),
    )

    await item.insert()

    logger.info(
        "Sample item created",
        user_id=user_id,
        item_id=str(item.id),
        item_name=item.name,
    )

    return SampleItemResponse(**item.model_dump(by_alias=True))


@router.get("", response_model=list[SampleItemResponse])
@authorized
async def list_items(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    user_id: str = Depends(get_user_id),
) -> list[SampleItemResponse]:
    """
    List user's sample items.

    - **skip**: Number of items to skip (default: 0)
    - **limit**: Maximum number of items to return (default: 100)
    - **is_active**: Filter by active status (optional)
    """

    logger.info(
        "Listing sample items",
        user_id=user_id,
        skip=skip,
        limit=limit,
    )

    # Build query - ALWAYS filter by user_id
    query = SampleItem.find(SampleItem.user_id == user_id)

    if is_active is not None:
        query = query.find(SampleItem.is_active == is_active)

    items = await query.skip(skip).limit(limit).sort("-created_at").to_list()

    logger.info(
        "Sample items retrieved",
        user_id=user_id,
        count=len(items),
    )

    return [SampleItemResponse(**item.model_dump(by_alias=True)) for item in items]


@router.get("/{item_id}", response_model=SampleItemResponse)
@authorized
async def get_item(
    item_id: str,
    user_id: str = Depends(get_user_id),
) -> SampleItemResponse:
    """
    Get a specific sample item by ID.

    - **item_id**: Item ID
    """

    logger.info(
        "Retrieving sample item",
        user_id=user_id,
        item_id=item_id,
    )

    # Find item and verify ownership
    item = await SampleItem.find_one(
        SampleItem.id == PydanticObjectId(item_id),
        SampleItem.user_id == user_id,  # Critical: user_id filter
    )

    if not item:
        logger.warning(
            "Sample item not found",
            user_id=user_id,
            item_id=item_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return SampleItemResponse(**item.model_dump(by_alias=True))


@router.put("/{item_id}", response_model=SampleItemResponse)
@authorized
async def update_item(
    item_id: str,
    item_data: SampleItemUpdate,
    user_id: str = Depends(get_user_id),
) -> SampleItemResponse:
    """
    Update a sample item.

    - **item_id**: Item ID
    - **name**: Updated item name (optional)
    - **description**: Updated item description (optional)
    - **quantity**: Updated item quantity (optional)
    - **is_active**: Updated active status (optional)
    """
    logger.info(
        "Updating sample item",
        user_id=user_id,
        item_id=item_id,
    )

    # Find item and verify ownership
    item = await SampleItem.find_one(
        SampleItem.id == PydanticObjectId(item_id),
        SampleItem.user_id == user_id,
    )

    if not item:
        logger.warning(
            "Sample item not found for update",
            user_id=user_id,
            item_id=item_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    # Update fields
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await item.save()

    logger.info(
        "Sample item updated",
        user_id=user_id,
        item_id=str(item.id),
    )

    return SampleItemResponse(**item.model_dump(by_alias=True))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
@authorized
async def delete_item(
    item_id: str,
    user_id: str = Depends(get_user_id),
) -> None:
    """
    Delete a sample item.

    - **item_id**: Item ID
    """

    logger.info(
        "Deleting sample item",
        user_id=user_id,
        item_id=item_id,
    )

    # Find item and verify ownership
    item = await SampleItem.find_one(
        SampleItem.id == PydanticObjectId(item_id),
        SampleItem.user_id == user_id,
    )

    if not item:
        logger.warning(
            "Sample item not found for deletion",
            user_id=user_id,
            item_id=item_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    await item.delete()

    logger.info(
        "Sample item deleted",
        user_id=user_id,
        item_id=str(item.id),
    )
'''


def generate_sample_item_test() -> str:
    """Generate sample item test (tests/unit/test_items.py)."""
    return '''"""Tests for sample item endpoints."""

import pytest
from beanie import PydanticObjectId
from httpx import AsyncClient

from app.models.item import SampleItem


@pytest.mark.asyncio
async def test_create_item(test_app):
    """Test creating a sample item."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        # Set mock user ID in headers (simulating Kong Gateway)
        user_id = str(PydanticObjectId())
        headers = {"X-User-Id": user_id}

        response = await client.post(
            "/api/v1/items",
            json={
                "name": "Test Item",
                "description": "Test description",
                "quantity": 10,
            },
            headers=headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["user_id"] == user_id
        assert data["quantity"] == 10


@pytest.mark.asyncio
async def test_list_items(test_app):
    """Test listing user's items."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        user_id = str(PydanticObjectId())
        headers = {"X-User-Id": user_id}

        # Create test items
        for i in range(3):
            await SampleItem(
                user_id=PydanticObjectId(user_id),
                name=f"Item {i}",
                quantity=i * 10,
            ).insert()

        response = await client.get("/api/v1/items", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(item["user_id"] == user_id for item in data)


@pytest.mark.asyncio
async def test_get_item(test_app):
    """Test getting a specific item."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        user_id = str(PydanticObjectId())
        headers = {"X-User-Id": user_id}

        # Create test item
        item = await SampleItem(
            user_id=PydanticObjectId(user_id),
            name="Test Item",
            quantity=5,
        ).insert()

        response = await client.get(f"/api/v1/items/{str(item.id)}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(item.id)
        assert data["name"] == "Test Item"


@pytest.mark.asyncio
async def test_update_item(test_app):
    """Test updating an item."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        user_id = str(PydanticObjectId())
        headers = {"X-User-Id": user_id}

        # Create test item
        item = await SampleItem(
            user_id=PydanticObjectId(user_id),
            name="Original Name",
            quantity=5,
        ).insert()

        response = await client.put(
            f"/api/v1/items/{str(item.id)}",
            json={"name": "Updated Name", "quantity": 10},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["quantity"] == 10


@pytest.mark.asyncio
async def test_delete_item(test_app):
    """Test deleting an item."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        user_id = str(PydanticObjectId())
        headers = {"X-User-Id": user_id}

        # Create test item
        item = await SampleItem(
            user_id=PydanticObjectId(user_id),
            name="Test Item",
        ).insert()

        response = await client.delete(f"/api/v1/items/{str(item.id)}", headers=headers)

        assert response.status_code == 204

        # Verify deletion
        deleted_item = await SampleItem.get(item.id)
        assert deleted_item is None


@pytest.mark.asyncio
async def test_user_isolation(test_app):
    """Test that users can only access their own items."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        user1_id = str(PydanticObjectId())
        user2_id = str(PydanticObjectId())

        # Create item for user1
        item = await SampleItem(
            user_id=PydanticObjectId(user1_id),
            name="User1 Item",
        ).insert()

        # Try to access with user2
        headers = {"X-User-Id": user2_id}
        response = await client.get(f"/api/v1/items/{str(item.id)}", headers=headers)

        assert response.status_code == 404  # Not found (due to user_id filter)
'''


def generate_health_router_py() -> str:
    """Generate health router content."""
    return '''"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns service status.
    """
    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check() -> dict:
    """
    Readiness check endpoint.

    Returns whether service is ready to accept traffic.
    """
    return {"status": "ready"}
'''


def generate_models_init_py() -> str:
    """Generate models __init__.py content."""
    return '''"""Database models for the service."""

from beanie import Document

from .item import SampleItem

# List of all document models for Beanie initialization
document_models: list[type[Document]] = [
    SampleItem,
]

__all__ = ["SampleItem", "document_models"]
'''


def generate_service_factory_py() -> str:
    """Generate service factory content."""
    return '''"""Service factory for managing shared resources."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mysingle.core import get_structured_logger

if TYPE_CHECKING:
    pass

logger = get_structured_logger(__name__)


class ServiceFactory:
    """Factory for managing shared service resources."""

    def __init__(self):
        """Initialize service factory."""
        self._initialized = False

    async def initialize(self):
        """Initialize async resources."""
        if self._initialized:
            return

        # Initialize your async resources here
        # e.g., Redis clients, HTTP clients, etc.

        self._initialized = True
        logger.info("✅ Service factory initialized")

    async def shutdown(self):
        """Shutdown and cleanup resources."""
        if not self._initialized:
            return

        # Cleanup your resources here

        self._initialized = False
        logger.info("✅ Service factory shutdown completed")


# Singleton instance
_service_factory: ServiceFactory | None = None


def get_service_factory() -> ServiceFactory:
    """Get or create the service factory singleton."""
    global _service_factory
    if _service_factory is None:
        _service_factory = ServiceFactory()
    return _service_factory
'''


def generate_pyproject_toml(
    service_name: str, service_name_pascal: str, grpc_enabled: bool
) -> str:
    """Generate pyproject.toml content."""
    grpc_deps = ""
    if grpc_enabled:
        grpc_deps = """    # gRPC
    "grpcio>=1.76.0",
    "grpcio-reflection>=1.76.0",
"""

    return f"""[project]
name = "{service_name}"
version = "0.1.0"
description = "{service_name_pascal} for MySingle Quant Platform"
requires-python = ">=3.12"
dependencies = [
    # Common dependencies
    "mysingle @ git+https://github.com/Br0therDan/mysingle-pack.git@v2.8.7",
{grpc_deps}    # Specific dependencies
    # Add here any additional dependencies your service needs
]

[tool.hatch.metadata]
allow-direct-references = true

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.5.0",
    "httpx>=0.26.0",
    "ruff>=0.1.9",
    "mypy>=1.8.0",
    "mongomock_motor>=0.0.16",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.5.0",
    "httpx>=0.26.0",
    "asgi-lifespan>=2.1.0",
    "ruff>=0.1.9",
    "mypy>=1.8.0",
    "pre-commit>=4.3.0",
    "bandit[toml]>=1.8.6",
    "black>=24.10.0",
    "mongomock-motor>=0.0.16",
    "fakeredis>=2.32.1",
    "protobuf>=6.33.1",
    "grpcio-tools>=1.76.0",
]

# Ruff configuration (replaces Black + Flake8 + isort)
[tool.ruff]
line-length = 88
target-version = "py312"
exclude = [
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "data/",
    "logs/",
]

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "SIM"]
ignore = ["E501", "B008", "B006", "B904", "SIM105", "E402", "SIM102"]

[tool.ruff.lint.isort]
known-first-party = ["app"]

[tool.bandit]
exclude_dirs = ["tests", "venv", ".venv", "__pycache__"]
skips = ["B101", "B105", "B106", "B107", "B601", "B608"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
markers = [
    "e2e: End-to-end integration tests (deselect with '-m \"not e2e\"')",
    "slow: Slow-running tests (deselect with '-m \"not slow\"')",
]


[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true
exclude = ["tests/", "build/", "dist/"]
ignore_errors = true
"""


def generate_env_file(service_name: str, service_name_snake: str) -> str:
    """Generate .env file content."""
    return f"""# {service_name.replace("-", " ").title()} Environment Variables
# Copy to .env.local for local development

# Service Info
SERVICE_NAME={service_name}
APP_VERSION=0.1.0
ENVIRONMENT=development
LOG_LEVEL=INFO

# MongoDB
MONGODB_SERVER=localhost:27017
MONGODB_USERNAME=root
MONGODB_PASSWORD=example

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Logging
AUDIT_LOGGING_ENABLED=true
"""


def generate_dockerfile(service_name: str, grpc_port: int | None = None) -> str:
    """Generate Dockerfile content."""
    service_title = service_name.replace("-", " ").title()

    # gRPC port exposure (optional)
    grpc_expose = ""
    grpc_comment = ""
    if grpc_port:
        grpc_expose = f"\n# gRPC port (enabled via USE_GRPC_FOR_{service_name.replace('-', '_').upper()}=true)\nEXPOSE {grpc_port}"
        grpc_comment = f", gRPC support (:{grpc_port})"

    return f"""# ==============================================
# {service_title} Dockerfile
# Optimized for: Service management, data persistence{grpc_comment}
# ==============================================

FROM python:3.12-slim AS base

# GitHub token for private repo access
ARG GITHUB_TOKEN

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    build-essential \\
    pkg-config \\
    libgomp1 \\
    && rm -rf /var/lib/apt/lists/*

# Set Python environment variables
ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1 \\
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create application user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Configure git credentials and install dependencies
RUN if [ -n "$GITHUB_TOKEN" ]; then \\
    git config --global url."https://${{GITHUB_TOKEN}}@github.com/".insteadOf "https://github.com/" ; \\
    fi && \\
    pip install -e . && \\
    git config --global --unset url."https://github.com/".insteadOf || true

# Copy source code
COPY app ./app
COPY logs ./logs

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000{grpc_expose}

# Health check for {service_name}
HEALTHCHECK --interval=20s --timeout=15s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start with moderate worker count
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
"""


def generate_readme(
    service_name: str, service_name_pascal: str, port: int, grpc_port: int | None
) -> str:
    """Generate README.md content."""
    grpc_section = ""
    if grpc_port:
        grpc_section = f"""
### gRPC

- **Port**: {grpc_port}
- **Enabled**: Set `USE_GRPC_FOR_{service_name.replace("-", "_").upper()}=true`
"""

    return f"""# {service_name_pascal}

{service_name_pascal} for MySingle Quant Platform.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- uv package manager
- MongoDB
- Redis

### Installation

```bash
# Install dependencies
uv pip install -e .

# Copy environment file
cp .env .env.local

# Edit environment variables
vim .env.local
```

### Configuration

Edit `.env.local`:

```bash
SERVICE_NAME={service_name}
MONGODB_SERVER=localhost:27017
REDIS_HOST=localhost
```

### Development

```bash
# Run development server
uvicorn app.main:app --reload --port {port}

# Run tests
pytest tests/ -v

# API documentation
open http://localhost:{port}/docs
```

## 📋 API Endpoints

### Health Checks

- `GET /health` - Health check
- `GET /ready` - Readiness check

### API v1

- `GET /api/v1/...` - API endpoints (to be implemented)

## 🏗️ Architecture

```
app/
├── main.py              # FastAPI application
├── api/v1/             # API routes
├── core/               # Core configuration
├── models/             # Beanie document models
└── services/           # Business logic
```

## 🔧 Configuration

### Environment Variables

| Variable               | Description           | Default     |
| ---------------------- | --------------------- | ----------- |
| `SERVICE_NAME`         | Service identifier    | {service_name} |
| `APP_VERSION`          | Service version       | 0.1.0       |
| `MONGODB_SERVER`       | MongoDB connection    | localhost:27017 |
| `REDIS_HOST`           | Redis host            | localhost   |
| `LOG_LEVEL`            | Logging level         | INFO        |
{grpc_section}
## 📊 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_example.py -v
```

## 🐛 Troubleshooting

### MongoDB Connection

```bash
# Check MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# Check connection from app
python -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; asyncio.run(AsyncIOMotorClient('mongodb://localhost:27017').admin.command('ping'))"
```

### Redis Connection

```bash
# Check Redis is running
redis-cli ping

# Should return: PONG
```

## 📚 Documentation

- [MySingle Core](https://github.com/Br0therDan/mysingle-pack/blob/main/docs/core/APP_FACTORY_USAGE_GUIDE.md)
- [NON_IAM Service Guide](https://github.com/Br0therDan/mysingle-pack/blob/main/docs/auth/NON_IAM_SERVICE_GUIDE.md)

## 📝 License

Proprietary - MySingle Quant Platform
"""


def generate_gitignore() -> str:
    """Generate .gitignore content."""
    return """.venv/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.mypy_cache/
.env.local
.env
*.log
logs/*.log
.DS_Store
*.sqlite
htmlcov/
.coverage
coverage.xml
*.egg-info/
dist/
build/
"""


def generate_pytest_ini() -> str:
    """Generate pytest.ini content."""
    return """[pytest]
asyncio_mode = auto
testpaths = tests
pythonpath = .
filterwarnings =
    ignore::DeprecationWarning
addopts =
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-report=xml
    --cov-branch
    --cov-fail-under=60
"""


def generate_test_example() -> str:
    """Generate example test file."""
    return '''"""Example test file."""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_readiness_check():
    """Test readiness check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}
'''

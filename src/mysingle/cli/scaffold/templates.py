"""Template generators for scaffolding services."""

from __future__ import annotations


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
    ServiceType,
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
    logger.info(f"🚀 Starting {service_name.replace('-', ' ').title()}...")

    try:
        # Initialize service factory
        factory = get_service_factory()
        await factory.initialize()
        logger.info("✅ Service factory initialized")

    except Exception as e:
        logger.error(f"❌ Startup failed: {{e}}")
        raise

    logger.info(f"✅ {service_name.replace('-', ' ').title()} started successfully")

    yield

    # Shutdown
    try:
        logger.info(f"🛑 Shutting down {service_name.replace('-', ' ').title()}...")

        # Cleanup service factory
        factory = get_service_factory()
        await factory.shutdown()
        logger.info("✅ Service factory cleanup completed")

    except Exception as e:
        logger.error(f"❌ Shutdown error: {{e}}")

    logger.info(f"👋 {service_name.replace('-', ' ').title()} shutdown completed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    # Create ServiceConfig for Non-IAM service (gateway handles auth)
    service_config = create_service_config(
        service_type=ServiceType.NON_IAM_SERVICE,
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
    # gRPC SERVER SETTINGS
    USE_GRPC_FOR_{service_name_snake.upper()}: bool = False
    {service_name_snake.upper()}_GRPC_PORT: int = 50051
"""

    return f'''"""{service_name.replace("-", " ").title()} Configuration."""

from mysingle.core import CommonSettings
from pydantic_settings import SettingsConfigDict


class Settings(CommonSettings):
    """{service_name.replace("-", " ").title()} settings extending CommonSettings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # APP INFO
    SERVICE_NAME: str = "{service_name}"
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"

    # Audit logging (HTTP request/response) toggle
    AUDIT_LOGGING_ENABLED: bool = True
{grpc_settings}

settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
'''


def generate_api_v1_py() -> str:
    """Generate api_v1.py content."""
    return '''"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.routes import health

api_router = APIRouter(prefix="/api/v1")

# Health check routes
api_router.include_router(health.router, tags=["health"])
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

# Import your models here
# from .example import ExampleModel

# List of all document models for Beanie initialization
document_models: list[type[Document]] = [
    # Add your models here
    # ExampleModel,
]
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
    "grpcio>=1.60.0",
    "grpcio-tools>=1.60.0",
    "grpcio-reflection>=1.76.0",
    "mysingle-protos @ git+https://github.com/Br0therDan/grpc-protos.git@v1.0.0",
"""

    return f"""[project]
name = "{service_name}"
version = "0.1.0"
description = "{service_name_pascal} for MySingle Quant Platform"
requires-python = ">=3.12"
dependencies = [
    # FastAPI stack
    "fastapi[standard]>=0.117.1",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.3",
    "pydantic-settings>=2.1.0",
    # MongoDB ODM
    "motor>=3.3.2",
    "beanie>=1.24.0",
    # Inter-service HTTP
    "httpx>=0.26.0",
    # MySingle shared library
    "mysingle>=2.2.0",
{grpc_deps}    # Utilities
    "python-dateutil>=2.8.2",
    "python-json-logger>=2.0.7",
    "tenacity>=9.1.2",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "pytest-asyncio>=0.21.1",
    "httpx>=0.26.0",
    "ruff>=0.1.9",
    "mypy>=1.8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501", "N805"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
pythonpath = ["."]
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
*.log
logs/*.log
.DS_Store
*.sqlite
htmlcov/
.coverage
"""


def generate_pytest_ini() -> str:
    """Generate pytest.ini content."""
    return """[pytest]
asyncio_mode = auto
testpaths = tests
pythonpath = .
filterwarnings =
    ignore::DeprecationWarning
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

"""
Tests for mysingle.core.health module.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mysingle.core.health import create_health_router, get_health_checker


@pytest.fixture
def health_router():
    """Create health router for tests."""
    return create_health_router(
        service_name="test-service",
        service_version="1.0.0",
    )


def test_health_checker_initialization(health_router):
    """Test HealthChecker initialization."""
    # Create router first to initialize the checker
    checker = get_health_checker()

    assert checker is not None


@pytest.mark.asyncio
async def test_health_check_basic(health_router):
    """Test basic health check."""
    # Router initializes the checker
    checker = get_health_checker()

    # Use correct method name: get_health, not check_health
    status = await checker.get_health()

    assert status is not None
    # Check for status attribute or field
    assert hasattr(status, "status") or isinstance(status, dict)


def test_health_router_creation():
    """Test health router creation."""
    router = create_health_router(
        service_name="test-service",
        service_version="1.0.0",
    )

    assert router is not None

    # Test router integration with FastAPI
    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_readiness_endpoint():
    """Test readiness endpoint."""
    router = create_health_router(
        service_name="test-service",
        service_version="1.0.0",
    )
    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_liveness_endpoint():
    """Test liveness endpoint."""
    router = create_health_router(
        service_name="test-service",
        service_version="1.0.0",
    )
    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)
    response = client.get("/health/live")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data

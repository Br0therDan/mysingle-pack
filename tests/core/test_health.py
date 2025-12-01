"""
Tests for mysingle.core.health module.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mysingle.core.health import HealthStatus, create_health_router, get_health_checker


def test_health_checker_initialization():
    """Test HealthChecker initialization."""
    checker = get_health_checker()

    assert checker is not None


@pytest.mark.asyncio
async def test_health_check_basic():
    """Test basic health check."""
    checker = get_health_checker()

    status = await checker.check_health()

    assert isinstance(status, HealthStatus)
    assert status.status in ["healthy", "unhealthy", "degraded"]


def test_health_router_creation():
    """Test health router creation."""
    router = create_health_router()

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
    router = create_health_router()
    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)
    response = client.get("/ready")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_liveness_endpoint():
    """Test liveness endpoint."""
    router = create_health_router()
    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)
    response = client.get("/live")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest
from beanie import PydanticObjectId
from fastapi import FastAPI
from starlette.testclient import TestClient

from mysingle.core.audit.middleware import AuditLoggingMiddleware
from mysingle.core.config import settings


@contextmanager
def override_settings(**kwargs):
    original = {}
    try:
        for k, v in kwargs.items():
            original[k] = getattr(settings, k)
            setattr(settings, k, v)
        yield
    finally:
        for k, v in original.items():
            setattr(settings, k, v)


@pytest.mark.asyncio
async def test_audit_logs_on_request():
    """Test that audit logs are created when enabled in development environment."""
    recorded = []

    # Mock the entire AuditLog class to avoid Beanie initialization
    class MockAuditLog:
        def __init__(self, **kwargs):
            self.service = kwargs.get("service")
            self.path = kwargs.get("path")
            self.method = kwargs.get("method")
            self.status_code = kwargs.get("status_code")
            self.latency_ms = kwargs.get("latency_ms")

        async def insert(self):
            recorded.append(
                {
                    "service": self.service,
                    "path": self.path,
                    "method": self.method,
                    "status_code": self.status_code,
                    "latency_ms": self.latency_ms,
                }
            )

    app = FastAPI()
    app.add_middleware(
        AuditLoggingMiddleware, service_name="test-service", enabled=True
    )

    @app.get("/ping")
    def ping():  # pragma: no cover - simple route
        return {"ok": True}

    with override_settings(ENVIRONMENT="development", AUDIT_LOGGING_ENABLED=True):
        # Patch AuditLog in the correct module
        with patch("mysingle.core.audit.middleware.AuditLog", MockAuditLog):
            with TestClient(app) as client:
                resp = client.get("/ping")
                assert resp.status_code == 200

    # One audit record should be written
    assert len(recorded) == 1
    rec = recorded[0]
    assert rec["service"] == "test-service"
    assert rec["path"] == "/ping"
    assert rec["method"] == "GET"
    assert isinstance(rec["latency_ms"], int)


@pytest.mark.asyncio
async def test_audit_skipped_in_test_env():
    """Test that audit logs are skipped in test environment."""
    recorded = []

    class MockAuditLog:
        def __init__(self, **kwargs):
            self.path = kwargs.get("path")

        async def insert(self):
            recorded.append({"path": self.path})

    app = FastAPI()
    app.add_middleware(
        AuditLoggingMiddleware, service_name="test-service", enabled=True
    )

    @app.get("/pong")
    def pong():  # pragma: no cover - simple route
        return {"ok": True}

    # ENVIRONMENT=test should skip logging regardless of enabled flag
    with override_settings(ENVIRONMENT="test", AUDIT_LOGGING_ENABLED=True):
        with patch("mysingle.core.audit.middleware.AuditLog", MockAuditLog):
            with TestClient(app) as client:
                resp = client.get("/pong")
                assert resp.status_code == 200

    assert recorded == []


@pytest.mark.asyncio
async def test_audit_extracts_user_id_from_headers():
    """Test that user_id is extracted from various header formats."""
    recorded = []

    class MockAuditLog:
        def __init__(self, **kwargs):
            self.user_id = kwargs.get("user_id")
            self.path = kwargs.get("path")
            self.id = PydanticObjectId()

        async def insert(self):
            recorded.append({"user_id": self.user_id, "path": self.path})

    app = FastAPI()
    app.add_middleware(
        AuditLoggingMiddleware, service_name="test-service", enabled=True
    )

    @app.get("/test")
    def test_endpoint():
        return {"ok": True}

    with override_settings(ENVIRONMENT="development", AUDIT_LOGGING_ENABLED=True):
        with patch("mysingle.core.audit.middleware.AuditLog", MockAuditLog):
            with TestClient(app) as client:
                # Test 1: X-User-Id header (standard case)
                resp = client.get(
                    "/test", headers={"X-User-Id": "507f1f77bcf86cd799439011"}
                )
                assert resp.status_code == 200

                # Test 2: x-user-id header (lowercase)
                resp = client.get(
                    "/test", headers={"x-user-id": "507f1f77bcf86cd799439012"}
                )
                assert resp.status_code == 200

                # Test 3: X-USER-ID header (uppercase)
                resp = client.get(
                    "/test", headers={"X-USER-ID": "507f1f77bcf86cd799439013"}
                )
                assert resp.status_code == 200

    # All requests should have captured user_id
    assert len(recorded) == 3
    assert recorded[0]["user_id"] == PydanticObjectId("507f1f77bcf86cd799439011")
    assert recorded[1]["user_id"] == PydanticObjectId("507f1f77bcf86cd799439012")
    assert recorded[2]["user_id"] == PydanticObjectId("507f1f77bcf86cd799439013")


@pytest.mark.asyncio
async def test_audit_extracts_user_id_from_request_state():
    """Test that user_id is extracted from request.state.user (AuthMiddleware)."""
    recorded = []

    class MockAuditLog:
        def __init__(self, **kwargs):
            self.user_id = kwargs.get("user_id")
            self.path = kwargs.get("path")
            self.id = PydanticObjectId()

        async def insert(self):
            recorded.append({"user_id": self.user_id, "path": self.path})

    app = FastAPI()

    # Add AuditLoggingMiddleware first
    app.add_middleware(
        AuditLoggingMiddleware, service_name="test-service", enabled=True
    )

    # Add a middleware that sets request.state.user (simulating AuthMiddleware)
    # This is added AFTER Audit, so it will execute BEFORE Audit (LIFO order)
    @app.middleware("http")
    async def mock_auth_middleware(request, call_next):
        # Simulate AuthMiddleware setting user in request.state
        mock_user = MagicMock()
        mock_user.id = PydanticObjectId("507f1f77bcf86cd799439014")
        request.state.user = mock_user
        response = await call_next(request)
        return response

    @app.get("/test")
    def test_endpoint():
        return {"ok": True}

    with override_settings(ENVIRONMENT="development", AUDIT_LOGGING_ENABLED=True):
        with patch("mysingle.core.audit.middleware.AuditLog", MockAuditLog):
            with TestClient(app) as client:
                # Request without headers - should use request.state.user
                resp = client.get("/test")
                assert resp.status_code == 200

    # Should have extracted user_id from request.state.user
    assert len(recorded) == 1
    assert recorded[0]["user_id"] == PydanticObjectId("507f1f77bcf86cd799439014")


@pytest.mark.asyncio
async def test_audit_user_id_none_when_not_provided():
    """Test that user_id is None when no user information is available."""
    recorded = []

    class MockAuditLog:
        def __init__(self, **kwargs):
            self.user_id = kwargs.get("user_id")
            self.path = kwargs.get("path")
            self.id = PydanticObjectId()

        async def insert(self):
            recorded.append({"user_id": self.user_id, "path": self.path})

    app = FastAPI()
    app.add_middleware(
        AuditLoggingMiddleware, service_name="test-service", enabled=True
    )

    @app.get("/test")
    def test_endpoint():
        return {"ok": True}

    with override_settings(ENVIRONMENT="development", AUDIT_LOGGING_ENABLED=True):
        with patch("mysingle.core.audit.middleware.AuditLog", MockAuditLog):
            with TestClient(app) as client:
                # Request without any user information
                resp = client.get("/test")
                assert resp.status_code == 200

    # user_id should be None
    assert len(recorded) == 1
    assert recorded[0]["user_id"] is None

from contextlib import contextmanager
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from mysingle.audit.middleware import AuditLoggingMiddleware
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
        # Patch AuditLog in the middleware module
        with patch("mysingle.audit.middleware.AuditLog", MockAuditLog):
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
        with patch("mysingle.audit.middleware.AuditLog", MockAuditLog):
            with TestClient(app) as client:
                resp = client.get("/pong")
                assert resp.status_code == 200

    assert recorded == []

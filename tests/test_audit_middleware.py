from contextlib import contextmanager

from fastapi import FastAPI
from starlette.testclient import TestClient

from mysingle_quant.audit.middleware import AuditLoggingMiddleware
from mysingle_quant.audit.models import AuditLog
from mysingle_quant.core.config import settings


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


def test_audit_logs_on_request(monkeypatch):
    recorded = []

    async def mock_insert(self):  # type: ignore[no-redef]
        recorded.append(
            {
                "service": self.service,
                "path": self.path,
                "method": self.method,
                "status_code": self.status_code,
                "latency_ms": self.latency_ms,
            }
        )

    monkeypatch.setattr(AuditLog, "insert", mock_insert, raising=True)

    app = FastAPI()
    app.add_middleware(
        AuditLoggingMiddleware, service_name="test-service", enabled=True
    )

    @app.get("/ping")
    def ping():  # pragma: no cover - simple route
        return {"ok": True}

    with override_settings(ENVIRONMENT="development", AUDIT_LOGGING_ENABLED=True):
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


def test_audit_skipped_in_test_env(monkeypatch):
    recorded = []

    async def mock_insert(self):  # type: ignore[no-redef]
        recorded.append({"path": self.path})

    monkeypatch.setattr(AuditLog, "insert", mock_insert, raising=True)

    app = FastAPI()
    app.add_middleware(
        AuditLoggingMiddleware, service_name="test-service", enabled=True
    )

    @app.get("/pong")
    def pong():  # pragma: no cover - simple route
        return {"ok": True}

    # ENVIRONMENT=test should skip logging regardless of enabled flag
    with override_settings(ENVIRONMENT="test", AUDIT_LOGGING_ENABLED=True):
        with TestClient(app) as client:
            resp = client.get("/pong")
            assert resp.status_code == 200

    assert recorded == []

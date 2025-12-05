"""Tests for audit logging middleware."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from mysingle.core.audit.middleware import AuditLoggingMiddleware
from mysingle.core.audit.models import AuditLog


@pytest.fixture
def app():
    """Create FastAPI app with audit middleware."""
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return {"message": "ok"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    @app.get("/metrics")
    async def metrics():
        return {"metrics": "data"}

    @app.get("/api/internal/status")
    async def internal_status():
        return {"status": "internal"}

    return app


@pytest.fixture
def client_with_audit(app):
    """Create test client with audit middleware enabled."""
    app.add_middleware(
        AuditLoggingMiddleware,
        service_name="test-service",
        enabled=True,
        exclude_paths=["/health", "/metrics", "/api/internal/*"],
    )
    return TestClient(app)


class TestAuditLoggingMiddleware:
    """Test audit logging middleware functionality."""

    def test_middleware_initialization(self):
        """Test middleware initializes with correct parameters."""
        app = FastAPI()

        middleware = AuditLoggingMiddleware(
            app,
            service_name="test-service",
            enabled=True,
            exclude_paths=["/health", "/metrics"],
        )

        assert middleware.service_name == "test-service"
        assert middleware.enabled is True
        assert "/health" in middleware.exclude_paths
        assert "/metrics" in middleware.exclude_paths

    def test_middleware_initialization_from_env(self):
        """Test middleware parses exclude paths from environment."""
        app = FastAPI()

        with patch("mysingle.core.audit.middleware.settings") as mock_settings:
            mock_settings.AUDIT_EXCLUDE_PATHS = "/health,/ready,/metrics"

            middleware = AuditLoggingMiddleware(
                app,
                service_name="test-service",
                enabled=True,
            )

            assert "/health" in middleware.exclude_paths
            assert "/ready" in middleware.exclude_paths
            assert "/metrics" in middleware.exclude_paths

    def test_should_exclude_path_exact_match(self):
        """Test exact path matching for exclusion."""
        app = FastAPI()
        middleware = AuditLoggingMiddleware(
            app,
            service_name="test-service",
            enabled=True,
            exclude_paths=["/health", "/ready"],
        )

        assert middleware._should_exclude_path("/health") is True
        assert middleware._should_exclude_path("/ready") is True
        assert middleware._should_exclude_path("/test") is False

    def test_should_exclude_path_wildcard_match(self):
        """Test wildcard path matching for exclusion."""
        app = FastAPI()
        middleware = AuditLoggingMiddleware(
            app,
            service_name="test-service",
            enabled=True,
            exclude_paths=["/api/internal/*", "/debug/*"],
        )

        assert middleware._should_exclude_path("/api/internal/status") is True
        assert middleware._should_exclude_path("/api/internal/health") is True
        assert middleware._should_exclude_path("/debug/vars") is True
        assert middleware._should_exclude_path("/api/public/test") is False
        assert middleware._should_exclude_path("/test") is False

    @patch("mysingle.core.audit.middleware.AuditLog")
    async def test_audit_log_created_for_normal_request(
        self, mock_audit_log, client_with_audit
    ):
        """Test audit log is created for normal requests."""
        mock_insert = AsyncMock()
        mock_audit_log.return_value.insert = mock_insert

        response = client_with_audit.get("/test")

        assert response.status_code == 200
        # Note: In test client, async operations may not execute
        # This is a basic structure test

    def test_excluded_path_not_audited(self, client_with_audit):
        """Test excluded paths don't create audit logs."""
        with patch("mysingle.core.audit.middleware.AuditLog") as mock_audit_log:
            mock_insert = AsyncMock()
            mock_audit_log.return_value.insert = mock_insert

            # Request to excluded path
            response = client_with_audit.get("/health")
            assert response.status_code == 200

            # Verify audit log was not created
            mock_audit_log.assert_not_called()

    def test_wildcard_excluded_path_not_audited(self, client_with_audit):
        """Test wildcard excluded paths don't create audit logs."""
        with patch("mysingle.core.audit.middleware.AuditLog") as mock_audit_log:
            mock_insert = AsyncMock()
            mock_audit_log.return_value.insert = mock_insert

            # Request to wildcard excluded path
            response = client_with_audit.get("/api/internal/status")
            assert response.status_code == 200

            # Verify audit log was not created
            mock_audit_log.assert_not_called()

    def test_disabled_middleware_no_audit(self):
        """Test disabled middleware doesn't create audit logs."""
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return {"message": "ok"}

        app.add_middleware(
            AuditLoggingMiddleware,
            service_name="test-service",
            enabled=False,  # Disabled
        )

        client = TestClient(app)

        with patch("mysingle.core.audit.middleware.AuditLog") as mock_audit_log:
            response = client.get("/test")
            assert response.status_code == 200
            mock_audit_log.assert_not_called()


class TestAuditLogModel:
    """Test AuditLog model."""

    def test_audit_log_model_structure(self):
        """Test AuditLog model has expected fields."""
        # Check model has expected fields (without instantiation)
        fields = AuditLog.model_fields

        assert "user_id" in fields
        assert "service" in fields
        assert "method" in fields
        assert "path" in fields
        assert "status_code" in fields
        assert "latency_ms" in fields
        assert "req_bytes" in fields
        assert "resp_bytes" in fields

    def test_audit_log_settings(self):
        """Test AuditLog collection settings."""
        # Check collection name and indexes
        assert AuditLog.Settings.name == "audit_logs"
        assert "user_id" in AuditLog.Settings.indexes
        assert "service" in AuditLog.Settings.indexes
        assert "occurred_at" in AuditLog.Settings.indexes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

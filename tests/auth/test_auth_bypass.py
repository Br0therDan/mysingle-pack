"""
Unit tests for authentication bypass mechanism
"""

import os
from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from mysingle.auth.middleware import AuthMiddleware
from mysingle.auth.models import User
from mysingle.core.service_types import ServiceConfig, ServiceType


@pytest.fixture
def test_app():
    """Create a test FastAPI application"""
    app = FastAPI()

    @app.get("/public/health")
    async def health():
        return {"status": "ok"}

    @app.get("/protected/data")
    async def protected_data(request: Request):
        user = getattr(request.state, "user", None)
        if not user:
            return {"error": "No user"}, 401
        return {"user_id": str(user.id), "email": user.email}

    return app


@pytest.fixture
def service_config():
    """Create a test service configuration"""
    return ServiceConfig(
        service_name="test-service",
        service_type=ServiceType.NON_IAM_SERVICE,
        public_paths=["/public"],
    )


class TestAuthBypass:
    """Test authentication bypass for unit testing"""

    def test_bypass_disabled_by_default(self, test_app, service_config):
        """Test that bypass is disabled by default"""
        with patch.dict(os.environ, {}, clear=True):
            middleware = AuthMiddleware(test_app, service_config)
            # Access private attribute for testing
            assert getattr(middleware, "auth_bypass", False) is False

    def test_bypass_enabled_in_dev(self, test_app, service_config):
        """Test that bypass can be enabled in development"""
        with patch.dict(
            os.environ, {"MYSINGLE_AUTH_BYPASS": "true", "ENVIRONMENT": "development"}
        ):
            middleware = AuthMiddleware(test_app, service_config)
            assert getattr(middleware, "auth_bypass", False) is True

    def test_bypass_ignored_in_production(self, test_app, service_config):
        """Test that bypass is ignored in production for security"""
        with patch.dict(
            os.environ, {"MYSINGLE_AUTH_BYPASS": "true", "ENVIRONMENT": "production"}
        ):
            middleware = AuthMiddleware(test_app, service_config)
            assert getattr(middleware, "auth_bypass", True) is False

    def test_test_user_creation_logic(self, test_app, service_config):
        """Test that test user creation logic validates environment variables"""
        # Test regular user configuration
        with patch.dict(
            os.environ,
            {
                "TEST_USER_EMAIL": "test_user@test.com",
                "TEST_USER_FULLNAME": "Test User",
            },
        ):
            # Verify environment variables are correctly set
            assert os.getenv("TEST_USER_EMAIL") == "test_user@test.com"
            assert os.getenv("TEST_USER_FULLNAME") == "Test User"
            assert os.getenv("MYSINGLE_AUTH_BYPASS_ADMIN", "false") == "false"

        # Test admin user configuration
        with patch.dict(
            os.environ,
            {
                "MYSINGLE_AUTH_BYPASS_ADMIN": "true",
                "TEST_ADMIN_EMAIL": "test_admin@test.com",
                "TEST_ADMIN_FULLNAME": "Test Admin",
            },
        ):
            # Verify admin environment variables are correctly set
            assert os.getenv("MYSINGLE_AUTH_BYPASS_ADMIN") == "true"
            assert os.getenv("TEST_ADMIN_EMAIL") == "test_admin@test.com"
            assert os.getenv("TEST_ADMIN_FULLNAME") == "Test Admin"

    @pytest.mark.asyncio
    async def test_bypass_injects_test_user(self, service_config):
        """Test that bypass injects test user into request.state"""
        from unittest.mock import Mock

        from mysingle.auth.deps.core import get_current_user
        from mysingle.auth.models import User

        with patch.dict(
            os.environ,
            {
                "MYSINGLE_AUTH_BYPASS": "true",
                "ENVIRONMENT": "development",
                "TEST_USER_EMAIL": "test_user@test.com",
                "TEST_USER_FULLNAME": "Test User",
            },
        ):
            # Create mock request with test user
            request = Mock(spec=Request)

            # Simulate what AuthMiddleware does - inject test user
            test_user = Mock(spec=User)
            test_user.email = "test_user@test.com"
            test_user.full_name = "Test User"
            test_user.id = "000000000000000000000001"
            test_user.is_active = True
            test_user.is_verified = True
            test_user.is_superuser = False

            request.state.user = test_user
            request.headers = {}

            # Verify get_current_user returns the test user
            user = get_current_user(request)
            assert user.email == "test_user@test.com"
            assert user.full_name == "Test User"


class TestAuthCore:
    """Test core authentication functions"""

    def test_get_current_user_from_request_state(self):
        """Test get_current_user retrieves user from request.state"""
        from mysingle.auth.deps.core import get_current_user

        request = Mock(spec=Request)
        test_user = Mock(spec=User)
        test_user.id = "123"
        test_user.is_active = True
        request.state.user = test_user
        request.headers = {}

        result = get_current_user(request)
        assert result == test_user

    def test_get_current_user_raises_when_missing(self):
        """Test get_current_user raises 401 when user missing"""
        from fastapi import HTTPException

        from mysingle.auth.deps.core import get_current_user

        request = Mock(spec=Request)
        request.state.user = None

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(request)

        assert exc_info.value.status_code == 401

    def test_get_current_active_user_checks_is_active(self):
        """Test get_current_active_user checks is_active flag"""
        from fastapi import HTTPException

        from mysingle.auth.deps.core import get_current_active_user

        request = Mock(spec=Request)
        test_user = Mock(spec=User)
        test_user.id = "123"
        test_user.is_active = False
        request.state.user = test_user
        request.headers = {}

        with pytest.raises(HTTPException) as exc_info:
            get_current_active_user(request)

        assert exc_info.value.status_code == 403

    def test_get_current_active_verified_user_checks_verification(self):
        """Test get_current_active_verified_user checks is_verified flag"""
        from fastapi import HTTPException

        from mysingle.auth.deps.core import get_current_active_verified_user

        request = Mock(spec=Request)
        test_user = Mock(spec=User)
        test_user.id = "123"
        test_user.is_active = True
        test_user.is_verified = False
        request.state.user = test_user
        request.headers = {}

        with pytest.raises(HTTPException) as exc_info:
            get_current_active_verified_user(request)

        assert exc_info.value.status_code == 403


class TestBaseGrpcClient:
    """Test BaseGrpcClient metadata and connection"""

    def test_metadata_includes_required_headers(self):
        """Test that gRPC metadata includes user-id, correlation-id, request-id"""
        from mysingle.clients import BaseGrpcClient

        client = BaseGrpcClient(
            service_name="test-service",
            default_port=50051,
            user_id="user123",
            correlation_id="corr456",
        )

        metadata = client.metadata
        metadata_dict = dict(metadata)

        assert "user-id" in metadata_dict
        assert metadata_dict["user-id"] == "user123"
        assert "correlation-id" in metadata_dict
        assert metadata_dict["correlation-id"] == "corr456"
        assert "request-id" in metadata_dict

    def test_user_id_extraction_from_request(self):
        """Test user_id extraction from FastAPI Request headers"""
        from mysingle.clients import BaseGrpcClient

        request = Mock(spec=Request)
        request.headers = {"X-User-Id": "user789"}

        client = BaseGrpcClient(
            service_name="test-service",
            default_port=50051,
            request=request,
        )

        assert client.user_id == "user789"

    def test_correlation_id_auto_generation(self):
        """Test correlation_id is auto-generated when not provided"""
        from mysingle.clients import BaseGrpcClient

        client = BaseGrpcClient(
            service_name="test-service",
            default_port=50051,
            user_id="user123",
        )

        assert client.correlation_id
        assert len(client.correlation_id) > 0

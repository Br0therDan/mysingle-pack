"""Tests for scaffold templates."""

from __future__ import annotations

from mysingle.cli.scaffold.templates import (
    generate_api_v1_py,
    generate_config_py,
    generate_dockerfile,
    generate_env_file,
    generate_gitignore,
    generate_health_router_py,
    generate_main_py,
    generate_models_init_py,
    generate_pyproject_toml,
    generate_pytest_ini,
    generate_readme,
    generate_service_factory_py,
    generate_test_example,
)


class TestTemplateGeneration:
    """Test template generation functions."""

    def test_generate_main_py_without_grpc(self):
        """Test main.py generation without gRPC."""
        result = generate_main_py("test-service", "test_service", grpc_enabled=False)

        assert "Test Service" in result
        assert "create_fastapi_app" in result
        assert "ServiceType.NON_IAM_SERVICE" in result
        assert "lifespan" in result
        assert "get_service_factory" in result

    def test_generate_main_py_with_grpc(self):
        """Test main.py generation with gRPC."""
        result = generate_main_py("grpc-service", "grpc_service", grpc_enabled=True)

        assert "Grpc Service" in result
        assert "create_fastapi_app" in result
        assert "lifespan" in result

    def test_generate_config_py_without_grpc(self):
        """Test config.py generation without gRPC."""
        result = generate_config_py("my-service", "my_service", grpc_enabled=False)

        assert "My Service" in result
        assert "CommonSettings" in result
        assert "SERVICE_NAME" in result
        assert "my-service" in result
        assert "GRPC" not in result

    def test_generate_config_py_with_grpc(self):
        """Test config.py generation with gRPC."""
        result = generate_config_py("grpc-service", "grpc_service", grpc_enabled=True)

        assert "CommonSettings" in result
        assert "USE_GRPC_FOR_GRPC_SERVICE" in result
        assert "GRPC_SERVICE_GRPC_PORT" in result

    def test_generate_api_v1_py(self):
        """Test api_v1.py generation."""
        result = generate_api_v1_py()

        assert "APIRouter" in result
        assert "api_router" in result
        assert "/api/v1" in result
        assert "health" in result

    def test_generate_health_router_py(self):
        """Test health router generation."""
        result = generate_health_router_py()

        assert "APIRouter" in result
        assert "/health" in result
        assert "/ready" in result
        assert "healthy" in result
        assert "ready" in result

    def test_generate_models_init_py(self):
        """Test models __init__.py generation."""
        result = generate_models_init_py()

        assert "Document" in result
        assert "document_models" in result
        assert "type[Document]" in result

    def test_generate_service_factory_py(self):
        """Test service factory generation."""
        result = generate_service_factory_py()

        assert "ServiceFactory" in result
        assert "get_service_factory" in result
        assert "initialize" in result
        assert "shutdown" in result

    def test_generate_pyproject_toml_without_grpc(self):
        """Test pyproject.toml generation without gRPC."""
        result = generate_pyproject_toml(
            "my-service",
            "MyService",
            grpc_enabled=False,
        )

        assert 'name = "my-service"' in result
        assert "MyService" in result
        assert "fastapi" in result
        assert "mysingle" in result
        assert "grpcio" not in result

    def test_generate_pyproject_toml_with_grpc(self):
        """Test pyproject.toml generation with gRPC."""
        result = generate_pyproject_toml(
            "grpc-service",
            "GrpcService",
            grpc_enabled=True,
        )

        assert "grpcio" in result
        assert "grpcio-tools" in result
        assert "mysingle-protos" in result

    def test_generate_env_file(self):
        """Test .env file generation."""
        result = generate_env_file("test-service", "test_service")

        assert "SERVICE_NAME=test-service" in result
        assert "MONGODB_SERVER" in result
        assert "REDIS_HOST" in result
        assert "ENVIRONMENT=development" in result

    def test_generate_dockerfile(self):
        """Test Dockerfile generation."""
        result = generate_dockerfile("my-service")

        assert "python:3.12-slim" in result
        assert "uv" in result
        assert "uvicorn" in result
        assert "EXPOSE 8000" in result

    def test_generate_readme(self):
        """Test README.md generation."""
        result = generate_readme(
            "test-service",
            "TestService",
            port=8011,
            grpc_port=None,
        )

        assert "TestService" in result
        assert "8011" in result
        assert "Quick Start" in result
        assert "Prerequisites" in result

    def test_generate_readme_with_grpc(self):
        """Test README.md generation with gRPC."""
        result = generate_readme(
            "grpc-service",
            "GrpcService",
            port=8011,
            grpc_port=50051,
        )

        assert "50051" in result
        assert "gRPC" in result

    def test_generate_gitignore(self):
        """Test .gitignore generation."""
        result = generate_gitignore()

        assert ".venv/" in result
        assert "__pycache__/" in result
        assert ".env.local" in result
        assert "*.log" in result

    def test_generate_pytest_ini(self):
        """Test pytest.ini generation."""
        result = generate_pytest_ini()

        assert "asyncio_mode = auto" in result
        assert "testpaths = tests" in result

    def test_generate_test_example(self):
        """Test example test file generation."""
        result = generate_test_example()

        assert "test_health_check" in result
        assert "test_readiness_check" in result
        assert "AsyncClient" in result
        assert "pytest" in result


class TestTemplateConsistency:
    """Test template consistency and correctness."""

    def test_service_name_conversion(self):
        """Test service name is properly converted in templates."""
        service_name = "my-awesome-service"
        service_name_snake = "my_awesome_service"

        main_py = generate_main_py(service_name, service_name_snake, False)
        config_py = generate_config_py(service_name, service_name_snake, False)

        # Check service name appears in human-readable form
        assert "My Awesome Service" in main_py
        assert service_name in config_py

    def test_grpc_settings_consistency(self):
        """Test gRPC settings are consistent across templates."""
        service_name_snake = "test_service"

        # With gRPC enabled
        config_with_grpc = generate_config_py("test-service", service_name_snake, True)

        assert "USE_GRPC_FOR_TEST_SERVICE" in config_with_grpc
        assert "TEST_SERVICE_GRPC_PORT" in config_with_grpc

        pyproject_with_grpc = generate_pyproject_toml(
            "test-service", "TestService", True
        )
        assert "grpcio" in pyproject_with_grpc

        # Without gRPC
        config_without_grpc = generate_config_py(
            "test-service", service_name_snake, False
        )
        assert "GRPC" not in config_without_grpc

        pyproject_without_grpc = generate_pyproject_toml(
            "test-service", "TestService", False
        )
        assert "grpcio" not in pyproject_without_grpc

    def test_mysingle_integration(self):
        """Test templates properly integrate MySingle library."""
        main_py = generate_main_py("test-service", "test_service", False)
        config_py = generate_config_py("test-service", "test_service", False)
        pyproject = generate_pyproject_toml("test-service", "TestService", False)

        # Check MySingle imports
        assert "from mysingle.core import" in main_py
        assert "create_fastapi_app" in main_py
        assert "ServiceType.NON_IAM_SERVICE" in main_py

        assert "from mysingle.core import CommonSettings" in config_py

        assert "mysingle" in pyproject

    def test_standard_endpoints_included(self):
        """Test standard endpoints are included."""
        health_router = generate_health_router_py()

        assert "/health" in health_router
        assert "/ready" in health_router

        api_v1 = generate_api_v1_py()
        assert "/api/v1" in api_v1
        assert "health" in api_v1

    def test_logging_setup(self):
        """Test logging is properly set up in templates."""
        main_py = generate_main_py("test-service", "test_service", False)

        assert "setup_logging" in main_py
        assert "get_structured_logger" in main_py
        assert "logger" in main_py

    def test_env_file_required_variables(self):
        """Test .env file contains all required variables."""
        env_content = generate_env_file("test-service", "test_service")

        required_vars = [
            "SERVICE_NAME",
            "APP_VERSION",
            "ENVIRONMENT",
            "LOG_LEVEL",
            "MONGODB_SERVER",
            "REDIS_HOST",
        ]

        for var in required_vars:
            assert var in env_content

    def test_pyproject_required_dependencies(self):
        """Test pyproject.toml contains required dependencies."""
        pyproject = generate_pyproject_toml("test-service", "TestService", False)

        required_deps = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "motor",
            "beanie",
            "mysingle",
        ]

        for dep in required_deps:
            assert dep in pyproject

    def test_dockerfile_best_practices(self):
        """Test Dockerfile follows best practices."""
        dockerfile = generate_dockerfile("test-service")

        # Multi-stage build
        assert "FROM python:3.12-slim AS builder" in dockerfile

        # Non-root user
        assert "useradd" in dockerfile
        assert "USER appuser" in dockerfile

        # Python 3.12
        assert "3.12" in dockerfile

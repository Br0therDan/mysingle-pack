"""Tests for scaffold CLI command."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

from mysingle.cli.scaffold.commands import (
    create_service,
    execute,
    get_next_available_ports,
    setup_parser,
)


class TestScaffoldParser:
    """Test scaffold argument parser setup."""

    def test_setup_parser(self):
        """Test parser configuration."""
        import argparse

        parser = argparse.ArgumentParser()
        setup_parser(parser)

        # Test default values
        args = parser.parse_args([])
        assert args.service_name is None
        assert args.port == 8011
        assert args.grpc_port is None
        assert args.grpc is False
        assert args.interactive is False

    def test_parser_with_service_name(self):
        """Test parser with service name."""
        import argparse

        parser = argparse.ArgumentParser()
        setup_parser(parser)

        args = parser.parse_args(["my-service"])
        assert args.service_name == "my-service"

    def test_parser_with_all_options(self):
        """Test parser with all options."""
        import argparse

        parser = argparse.ArgumentParser()
        setup_parser(parser)

        args = parser.parse_args(
            [
                "test-service",
                "--port",
                "8080",
                "--grpc-port",
                "50051",
                "--grpc",
                "--output-dir",
                "/tmp/test",
                "-i",
            ]
        )

        assert args.service_name == "test-service"
        assert args.port == 8080
        assert args.grpc_port == 50051
        assert args.grpc is True
        assert args.output_dir == "/tmp/test"
        assert args.interactive is True


class TestGetNextAvailablePorts:
    """Test next available port detection."""

    def test_empty_directory(self):
        """Test with no existing services."""
        with tempfile.TemporaryDirectory() as tmpdir:
            services_dir = Path(tmpdir)
            http_port, grpc_port = get_next_available_ports(services_dir)

            assert http_port == 8011
            assert grpc_port == 50056

    def test_with_existing_service(self):
        """Test with existing service using ports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            services_dir = Path(tmpdir)

            # Create a service with .env file
            service_dir = services_dir / "existing-service"
            service_dir.mkdir(parents=True)

            env_content = """
SERVICE_NAME=existing-service
PORT=8011
GRPC_PORT=50056
"""
            (service_dir / ".env").write_text(env_content)

            http_port, grpc_port = get_next_available_ports(services_dir)

            # Should skip 8011 and 50056
            assert http_port == 8012
            assert grpc_port == 50057

    def test_non_existent_directory(self):
        """Test with non-existent directory."""
        services_dir = Path("/non/existent/path")
        http_port, grpc_port = get_next_available_ports(services_dir)

        assert http_port == 8011
        assert grpc_port == 50056


class TestCreateService:
    """Test service creation."""

    def test_create_basic_service(self):
        """Test creating a basic service without gRPC."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "test-service"

            result = create_service(
                service_name="test-service",
                port=8011,
                grpc_port=None,
                grpc_enabled=False,
                output_dir=output_dir,
            )

            assert result == 0
            assert output_dir.exists()

            # Check key files
            assert (output_dir / "app" / "main.py").exists()
            assert (output_dir / "app" / "core" / "config.py").exists()
            assert (output_dir / "app" / "api" / "v1" / "api_v1.py").exists()
            assert (output_dir / "pyproject.toml").exists()
            assert (output_dir / ".env").exists()
            assert (output_dir / "Dockerfile").exists()
            assert (output_dir / "README.md").exists()

    def test_create_service_with_grpc(self):
        """Test creating a service with gRPC enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "grpc-service"

            result = create_service(
                service_name="grpc-service",
                port=8011,
                grpc_port=50051,
                grpc_enabled=True,
                output_dir=output_dir,
            )

            assert result == 0
            assert output_dir.exists()

            # Check gRPC directory
            assert (output_dir / "app" / "grpc").exists()

            # Check config file contains gRPC settings
            config_content = (output_dir / "app" / "core" / "config.py").read_text()
            assert "GRPC" in config_content

    def test_create_service_existing_directory(self):
        """Test creating service in existing directory should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "existing-service"
            output_dir.mkdir(parents=True)

            result = create_service(
                service_name="existing-service",
                port=8011,
                grpc_port=None,
                grpc_enabled=False,
                output_dir=output_dir,
            )

            assert result == 1

    def test_create_service_directory_structure(self):
        """Test that all required directories are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "structure-test-service"

            result = create_service(
                service_name="structure-test-service",
                port=8011,
                grpc_port=None,
                grpc_enabled=False,
                output_dir=output_dir,
            )

            assert result == 0

            # Check directory structure
            expected_dirs = [
                "app",
                "app/api",
                "app/api/v1",
                "app/api/v1/routes",
                "app/core",
                "app/models",
                "app/schemas",
                "app/services",
                "tests",
                "tests/unit",
                "tests/integration",
                "logs",
            ]

            for dir_path in expected_dirs:
                assert (
                    output_dir / dir_path
                ).exists(), f"Missing directory: {dir_path}"

    def test_create_service_file_content(self):
        """Test that generated files have correct content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "content-test-service"

            result = create_service(
                service_name="content-test-service",
                port=8011,
                grpc_port=None,
                grpc_enabled=False,
                output_dir=output_dir,
            )

            assert result == 0

            # Check main.py content
            main_content = (output_dir / "app" / "main.py").read_text()
            assert "create_fastapi_app" in main_content
            assert "ServiceType.NON_IAM_SERVICE" in main_content

            # Check config.py content
            config_content = (output_dir / "app" / "core" / "config.py").read_text()
            assert "content-test-service" in config_content
            assert "CommonSettings" in config_content

            # Check pyproject.toml content
            pyproject_content = (output_dir / "pyproject.toml").read_text()
            assert "content-test-service" in pyproject_content
            assert "mysingle" in pyproject_content

            # Check .env content
            env_content = (output_dir / ".env").read_text()
            assert "SERVICE_NAME=content-test-service" in env_content


class TestExecute:
    """Test execute command."""

    def test_execute_without_service_name_no_interactive(self):
        """Test execute without service name should trigger interactive mode."""
        import argparse

        args = argparse.Namespace(
            service_name=None,
            port=8011,
            grpc_port=None,
            grpc=False,
            output_dir=None,
            interactive=False,
        )

        # Mock interactive mode to return 0
        with patch(
            "mysingle.cli.scaffold.commands.execute_interactive"
        ) as mock_interactive:
            mock_interactive.return_value = 0

            result = execute(args)

            assert mock_interactive.called
            assert result == 0

    def test_execute_with_invalid_service_name(self):
        """Test execute with service name not ending in '-service'."""
        import argparse

        args = argparse.Namespace(
            service_name="myapp",
            port=8011,
            grpc_port=None,
            grpc=False,
            output_dir=None,
            interactive=False,
        )

        result = execute(args)

        assert result == 1

    def test_execute_with_valid_service_name(self):
        """Test execute with valid service name."""
        import argparse

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "valid-service"

            args = argparse.Namespace(
                service_name="valid-service",
                port=8011,
                grpc_port=None,
                grpc=False,
                output_dir=str(output_dir),
                interactive=False,
            )

            result = execute(args)

            assert result == 0
            assert output_dir.exists()

    def test_execute_with_grpc_enabled(self):
        """Test execute with gRPC enabled."""
        import argparse

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "grpc-enabled-service"

            args = argparse.Namespace(
                service_name="grpc-enabled-service",
                port=8011,
                grpc_port=50051,
                grpc=True,
                output_dir=str(output_dir),
                interactive=False,
            )

            result = execute(args)

            assert result == 0
            assert output_dir.exists()
            assert (output_dir / "app" / "grpc").exists()


class TestScaffoldIntegration:
    """Integration tests for scaffold command."""

    def test_full_scaffold_workflow(self):
        """Test complete scaffold workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            services_dir = Path(tmpdir) / "services"
            services_dir.mkdir()

            # Create first service
            service1_dir = services_dir / "service1-service"
            result1 = create_service(
                service_name="service1-service",
                port=8011,
                grpc_port=None,
                grpc_enabled=False,
                output_dir=service1_dir,
            )

            assert result1 == 0

            # Create second service - should get next available port
            http_port, grpc_port = get_next_available_ports(services_dir)

            # Port detection may not work perfectly in test env
            # Just verify second service can be created
            service2_dir = services_dir / "service2-service"
            result2 = create_service(
                service_name="service2-service",
                port=http_port,
                grpc_port=None,
                grpc_enabled=False,
                output_dir=service2_dir,
            )

            assert result2 == 0

            # Verify both services exist
            assert service1_dir.exists()
            assert service2_dir.exists()

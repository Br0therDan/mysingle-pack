"""Scaffold command implementation."""

from __future__ import annotations

import argparse
from pathlib import Path

from mysingle.cli.utils import (
    console,
    print_error,
    print_header,
    print_info,
    print_success,
)

from .templates import (
    generate_agents_md,
    generate_api_v1_py,
    generate_config_py,
    generate_conftest_py,
    generate_copilot_instructions_md,
    generate_dockerfile,
    generate_dockerignore,
    generate_gitignore,
    generate_health_router_py,
    generate_main_py,
    generate_models_init_py,
    generate_pre_commit_config,
    generate_pyproject_toml,
    generate_pytest_ini,
    generate_readme,
    generate_sample_item_model,
    generate_sample_item_router,
    generate_sample_item_schema,
    generate_sample_item_test,
    generate_service_factory_py,
    generate_test_example,
)


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Set up the scaffold command parser."""
    parser.add_argument(
        "service_name",
        nargs="?",
        help="Name of the service (e.g., reporting-service)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8011,
        help="HTTP port for the service (default: 8011)",
    )
    parser.add_argument(
        "--grpc-port",
        type=int,
        help="gRPC port (if gRPC is needed)",
    )
    parser.add_argument(
        "--grpc",
        action="store_true",
        help="Include gRPC support",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory (default: services/<service-name>)",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Force interactive mode",
    )


def get_next_available_ports(services_dir: Path) -> tuple[int, int]:
    """Get next available HTTP and gRPC ports."""
    used_http_ports = set()
    used_grpc_ports = set()

    if services_dir.exists():
        for service_dir in services_dir.iterdir():
            if not service_dir.is_dir() or service_dir.name.startswith("."):
                continue

            # Check pyproject.toml or .env for port info
            env_file = service_dir / ".env"
            if env_file.exists():
                try:
                    content = env_file.read_text()
                    # Simple port extraction (not perfect but good enough)
                    for line in content.split("\n"):
                        if "PORT" in line and "=" in line:
                            try:
                                port = int(line.split("=")[1].strip())
                                if 8000 <= port < 9000:
                                    used_http_ports.add(port)
                                elif 50000 <= port < 60000:
                                    used_grpc_ports.add(port)
                            except (ValueError, IndexError):
                                pass
                except Exception:
                    pass

    # Find next available ports
    next_http = 8011
    while next_http in used_http_ports:
        next_http += 1

    next_grpc = 50056
    while next_grpc in used_grpc_ports:
        next_grpc += 1

    return next_http, next_grpc


def execute_interactive(services_dir: Path) -> int:
    """Execute scaffold in interactive mode."""
    try:
        from rich.prompt import Confirm, IntPrompt, Prompt
    except ImportError:
        print_error(
            "Interactive mode requires 'rich' package. Install it with: pip install rich"
        )
        return 1

    print_header("🚀 MySingle Service Scaffolding Tool")

    # Service name
    console.print("\n[bold cyan]Service Configuration[/bold cyan]\n")
    service_name = Prompt.ask(
        "Service name (kebab-case, e.g., reporting-service)",
        default="my-service",
    )

    if not service_name:
        print_error("Service name is required")
        return 1

    # Validate service name
    if not service_name.endswith("-service"):
        add_suffix = Confirm.ask(
            "Service name should end with '-service'. Add it automatically?",
            default=True,
        )
        if add_suffix:
            service_name = f"{service_name}-service"
        else:
            print_error("Service name must end with '-service'")
            return 1

    # Port configuration
    next_http, next_grpc = get_next_available_ports(services_dir)
    console.print(f"\n💡 Next available ports: HTTP {next_http}, gRPC {next_grpc}\n")

    use_suggested = Confirm.ask(
        f"Use suggested HTTP port ({next_http})?",
        default=True,
    )

    if use_suggested:
        port = next_http
    else:
        port = IntPrompt.ask("Enter HTTP port", default=8011)

    # gRPC support
    grpc_enabled = Confirm.ask("Enable gRPC support?", default=False)
    grpc_port = None

    if grpc_enabled:
        use_suggested_grpc = Confirm.ask(
            f"Use suggested gRPC port ({next_grpc})?",
            default=True,
        )
        if use_suggested_grpc:
            grpc_port = next_grpc
        else:
            grpc_port = IntPrompt.ask("Enter gRPC port", default=50056)

    # Output directory
    default_output = str(services_dir / service_name)
    output_dir_str = Prompt.ask(
        "Output directory",
        default=default_output,
    )
    output_dir = Path(output_dir_str)

    # Confirmation
    console.print("\n[bold]Configuration Summary[/bold]")
    console.print(f"Service Name:     {service_name}")
    console.print(f"HTTP Port:        {port}")
    console.print(f"gRPC Enabled:     {'Yes' if grpc_enabled else 'No'}")
    if grpc_enabled:
        console.print(f"gRPC Port:        {grpc_port}")
    console.print(f"Output Directory: {output_dir}\n")

    if not Confirm.ask("Proceed with this configuration?", default=True):
        print_info("Cancelled by user")
        return 0

    # Create service
    return create_service(
        service_name=service_name,
        port=port,
        grpc_port=grpc_port,
        grpc_enabled=grpc_enabled,
        output_dir=output_dir,
    )


def execute(args: argparse.Namespace) -> int:
    """Execute scaffold command."""
    # Determine services directory (workspace root / services)
    current_dir = Path.cwd()

    # Try to find workspace root
    workspace_root = current_dir
    while workspace_root != workspace_root.parent:
        if (workspace_root / "pyproject.toml").exists() or (
            workspace_root / "services"
        ).exists():
            break
        workspace_root = workspace_root.parent

    services_dir = workspace_root / "services"

    # Interactive mode
    if args.interactive or not args.service_name:
        return execute_interactive(services_dir)

    # Command-line mode
    service_name = args.service_name

    # Validate service name
    if not service_name.endswith("-service"):
        print_error("Service name must end with '-service'")
        print_info(f"Try: {service_name}-service")
        return 1

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = services_dir / service_name

    return create_service(
        service_name=service_name,
        port=args.port,
        grpc_port=args.grpc_port,
        grpc_enabled=args.grpc,
        output_dir=output_dir,
    )


def create_service(
    service_name: str,
    port: int,
    grpc_port: int | None,
    grpc_enabled: bool,
    output_dir: Path,
) -> int:
    """Create service structure."""
    print_info(f"Creating service: {service_name}")

    if output_dir.exists():
        print_error(f"Directory already exists: {output_dir}")
        return 1

    try:
        # Convert names
        service_name_snake = service_name.replace("-", "_")
        service_name_pascal = "".join(
            word.capitalize() for word in service_name.split("-")
        )

        # Create directory structure
        _create_directory_structure(output_dir, grpc_enabled)

        # Create files
        _create_app_files(output_dir, service_name, service_name_snake, grpc_enabled)
        _create_config_files(
            output_dir,
            service_name,
            service_name_snake,
            service_name_pascal,
            port,
            grpc_port,
            grpc_enabled,
        )
        _create_tests(output_dir)

        print_success(f"Service '{service_name}' created successfully!")
        _print_next_steps(output_dir, service_name, port)

        return 0

    except Exception as e:
        print_error(f"Failed to create service: {e}")
        import traceback

        traceback.print_exc()
        return 1


def _create_directory_structure(base_dir: Path, grpc_enabled: bool) -> None:
    """Create base directory structure."""
    dirs = [
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
        ".github",
    ]

    if grpc_enabled:
        dirs.append("app/grpc")

    for dir_path in dirs:
        (base_dir / dir_path).mkdir(parents=True, exist_ok=True)

    print_info("📁 Created directory structure")


def _create_app_files(
    base_dir: Path, service_name: str, service_name_snake: str, grpc_enabled: bool
) -> None:
    """Create main application files."""
    # app/__init__.py
    (base_dir / "app" / "__init__.py").write_text('"""Application package."""\n')

    # app/main.py
    (base_dir / "app" / "main.py").write_text(
        generate_main_py(service_name, service_name_snake, grpc_enabled)
    )

    # app/core/config.py
    (base_dir / "app" / "core" / "__init__.py").write_text("")
    (base_dir / "app" / "core" / "config.py").write_text(
        generate_config_py(service_name, service_name_snake, grpc_enabled)
    )

    # app/api/v1/api_v1.py
    (base_dir / "app" / "api" / "__init__.py").write_text("")
    (base_dir / "app" / "api" / "v1" / "__init__.py").write_text("")
    (base_dir / "app" / "api" / "v1" / "api_v1.py").write_text(generate_api_v1_py())

    # app/api/v1/routes/health.py
    (base_dir / "app" / "api" / "v1" / "routes" / "__init__.py").write_text("")
    (base_dir / "app" / "api" / "v1" / "routes" / "health.py").write_text(
        generate_health_router_py()
    )

    # app/api/v1/routes/items.py (SampleItem router)
    (base_dir / "app" / "api" / "v1" / "routes" / "items.py").write_text(
        generate_sample_item_router()
    )

    # app/models/__init__.py
    (base_dir / "app" / "models" / "__init__.py").write_text(generate_models_init_py())

    # app/models/item.py (SampleItem model)
    (base_dir / "app" / "models" / "item.py").write_text(generate_sample_item_model())

    # app/schemas/__init__.py
    (base_dir / "app" / "schemas" / "__init__.py").write_text("")

    # app/schemas/item.py (SampleItem schemas)
    (base_dir / "app" / "schemas" / "item.py").write_text(generate_sample_item_schema())

    # app/services/service_factory.py
    (base_dir / "app" / "services" / "__init__.py").write_text("")
    (base_dir / "app" / "services" / "service_factory.py").write_text(
        generate_service_factory_py()
    )

    print_info("📝 Created application files")


def _create_config_files(
    base_dir: Path,
    service_name: str,
    service_name_snake: str,
    service_name_pascal: str,
    port: int,
    grpc_port: int | None,
    grpc_enabled: bool,
) -> None:
    """Create configuration files."""
    # pyproject.toml
    (base_dir / "pyproject.toml").write_text(
        generate_pyproject_toml(service_name, service_name_pascal, grpc_enabled)
    )

    # .gitignore
    (base_dir / ".gitignore").write_text(generate_gitignore())

    # .dockerignore
    (base_dir / ".dockerignore").write_text(generate_dockerignore())

    # .pre-commit-config.yaml
    (base_dir / ".pre-commit-config.yaml").write_text(generate_pre_commit_config())

    # pytest.ini
    (base_dir / "pytest.ini").write_text(generate_pytest_ini())

    # Dockerfile
    (base_dir / "Dockerfile").write_text(generate_dockerfile(service_name, grpc_port))

    # README.md
    (base_dir / "README.md").write_text(
        generate_readme(service_name, service_name_pascal, port, grpc_port)
    )

    # AGENTS.md
    (base_dir / "AGENTS.md").write_text(
        generate_agents_md(service_name, service_name_pascal)
    )

    # .github/copilot-instructions.md
    (base_dir / ".github" / "copilot-instructions.md").write_text(
        generate_copilot_instructions_md(service_name, service_name_pascal)
    )

    # .env template
    env_content = f"""# {service_name.replace("-", " ").title()} Environment Variables
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
    (base_dir / ".env").write_text(env_content)

    print_info("⚙️  Created configuration files")


def _create_tests(base_dir: Path) -> None:
    """Create test files."""
    # tests/__init__.py
    (base_dir / "tests" / "__init__.py").write_text("")
    (base_dir / "tests" / "unit" / "__init__.py").write_text("")
    (base_dir / "tests" / "integration" / "__init__.py").write_text("")

    # tests/conftest.py
    service_name = base_dir.name  # Extract service name from directory
    (base_dir / "tests" / "conftest.py").write_text(generate_conftest_py(service_name))

    # tests/unit/test_health.py
    (base_dir / "tests" / "unit" / "test_health.py").write_text(generate_test_example())

    # tests/unit/test_items.py (SampleItem tests)
    (base_dir / "tests" / "unit" / "test_items.py").write_text(
        generate_sample_item_test()
    )

    print_info("🧪 Created test files")


def _print_next_steps(output_dir: Path, service_name: str, port: int) -> None:
    """Print next steps for the user."""
    console.print("\n[bold green]✅ Next Steps:[/bold green]\n")
    console.print(f"1. cd {output_dir}")
    console.print("2. uv pip install -e .")
    console.print("3. cp .env .env.local")
    console.print("4. vim .env.local  # Edit configuration")
    console.print(f"5. uvicorn app.main:app --reload --port {port}")
    console.print(f"6. open http://localhost:{port}/docs\n")

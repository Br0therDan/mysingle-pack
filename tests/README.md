# MySingle Package Tests

## Overview

This directory contains comprehensive tests for the `mysingle` package, covering all major modules and functionality.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── auth/                    # Authentication tests
│   ├── test_auth_bypass.py
│   ├── test_auth_deps.py
│   ├── test_models.py
│   └── test_security.py
├── cli/                     # CLI tests
│   └── test_proto_cli.py
├── clients/                 # HTTP/gRPC client tests
│   ├── test_http_client.py
│   └── test_grpc_client.py
├── core/                    # Core module tests
│   ├── test_audit_middleware.py
│   ├── test_base_documents.py
│   ├── test_config.py
│   ├── test_health.py
│   ├── test_logging.py
│   ├── test_metrics.py
│   ├── test_service_model_initialization.py
│   └── test_settings.py
├── database/                # Database tests
│   ├── test_duckdb.py
│   └── test_mongodb.py
├── dsl/                     # DSL tests
│   ├── test_dsl_parser.py
│   └── test_stdlib.py
└── protos/                  # Proto tests
    ├── test_proto_imports.py
    └── test_proto_version.py
```

## Running Tests

### All Tests

```bash
# Using the test runner script
./run_tests.sh

# Or using pytest directly
uv run pytest tests/

# With coverage
uv run pytest tests/ --cov=mysingle --cov-report=html
```

### Specific Test Modules

```bash
# Test specific module
uv run pytest tests/core/

# Test specific file
uv run pytest tests/core/test_logging.py

# Test specific function
uv run pytest tests/core/test_logging.py::test_setup_logging_development
```

### Test Markers

```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Skip slow tests
uv run pytest -m "not slow"
```

## Test Environment

Tests require the following environment variables:

```bash
export MYSINGLE_AUTH_BYPASS=true  # Enable auth bypass for testing
export ENVIRONMENT=development     # Set to development mode
```

These are automatically set in `conftest.py` and `run_tests.sh`.

## Fixtures

Common fixtures are defined in `tests/conftest.py`:

- `mock_user`: Mock user for auth testing
- `mock_admin_user`: Mock admin user
- `test_settings`: Test configuration settings
- `sample_dataframe`: Sample pandas DataFrame for DSL tests
- `mock_mongodb_client`: Mock MongoDB client

## Writing New Tests

### Test File Naming

- Files: `test_*.py`
- Classes: `Test*`
- Functions: `test_*`

### Example Test

```python
"""
Tests for mysingle.module_name.
"""

import pytest
from mysingle.module_name import function_to_test


def test_basic_functionality():
    """Test basic functionality."""
    result = function_to_test()
    assert result is not None


@pytest.mark.asyncio
async def test_async_functionality():
    """Test async functionality."""
    result = await async_function_to_test()
    assert result is not None


class TestClassName:
    """Group related tests."""
    
    def test_method_one(self):
        """Test method one."""
        pass
    
    def test_method_two(self):
        """Test method two."""
        pass
```

### Skip Conditions

Use `@pytest.mark.skipif` for optional dependencies:

```python
try:
    from mysingle.optional_module import SomeClass
    MODULE_AVAILABLE = True
except ImportError:
    MODULE_AVAILABLE = False


@pytest.mark.skipif(not MODULE_AVAILABLE, reason="Module not installed")
def test_optional_feature():
    """Test optional feature."""
    pass
```

## Coverage

Coverage reports are generated in multiple formats:

- **Terminal**: Inline summary after test run
- **HTML**: `htmlcov/index.html` - Interactive browser view
- **XML**: `coverage.xml` - For CI/CD integration

### Coverage Goals

- **Core modules**: ≥ 90% coverage
- **Auth/Database**: ≥ 85% coverage
- **Clients/DSL**: ≥ 80% coverage
- **Overall**: ≥ 85% coverage

## CI/CD Integration

Tests are automatically run in CI/CD pipelines:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    export MYSINGLE_AUTH_BYPASS=true
    uv run pytest tests/ --cov=mysingle --cov-report=xml
```

## Troubleshooting

### Import Errors

If you encounter import errors, ensure the package is installed in development mode:

```bash
cd packages/quant-pack
uv pip install -e .
```

### Missing Dependencies

Install optional dependencies for specific test suites:

```bash
# For auth tests
uv pip install -e ".[auth]"

# For database tests
uv pip install -e ".[database]"

# For all features
uv pip install -e ".[full]"
```

### Async Test Failures

Ensure `pytest-asyncio` is installed and configured:

```bash
uv pip install pytest-asyncio
```

## Best Practices

1. **Keep tests isolated**: Each test should be independent
2. **Use fixtures**: Share common setup through fixtures
3. **Mock external dependencies**: Use `unittest.mock` for external services
4. **Test edge cases**: Include tests for error conditions
5. **Document tests**: Add docstrings explaining what each test validates
6. **Keep tests fast**: Use mocks to avoid slow I/O operations
7. **Follow AAA pattern**: Arrange, Act, Assert

## Continuous Improvement

- Add tests for new features before implementation (TDD)
- Maintain or increase coverage with each PR
- Refactor tests when refactoring code
- Review test failures carefully in CI/CD
- Update this README when adding new test categories

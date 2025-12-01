"""
Tests for mysingle.cli.protos module.
"""


import pytest

try:
    from mysingle.cli.protos.commands import generate, init, status, validate

    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not installed")
class TestProtoCLI:
    """Tests for proto CLI commands."""

    def test_init_command_structure(self):
        """Test init command structure."""
        assert hasattr(init, "init_command") or callable(init)

    def test_status_command_structure(self):
        """Test status command structure."""
        assert hasattr(status, "status_command") or callable(status)

    def test_validate_command_structure(self):
        """Test validate command structure."""
        assert hasattr(validate, "validate_command") or callable(validate)

    def test_generate_command_structure(self):
        """Test generate command structure."""
        assert hasattr(generate, "generate_command") or callable(generate)


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not installed")
def test_cli_module_imports():
    """Test that CLI modules can be imported."""
    from mysingle.cli import protos

    assert protos is not None
    assert hasattr(protos, "commands") or hasattr(protos, "__main__")

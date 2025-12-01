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
        # init is a module, check for setup_parser function
        assert hasattr(init, "setup_parser") and callable(init.setup_parser)

    def test_status_command_structure(self):
        """Test status command structure."""
        # status is a module, check for setup_parser function
        assert hasattr(status, "setup_parser") and callable(status.setup_parser)

    def test_validate_command_structure(self):
        """Test validate command structure."""
        # validate is a module, check for setup_parser function
        assert hasattr(validate, "setup_parser") and callable(validate.setup_parser)

    def test_generate_command_structure(self):
        """Test generate command structure."""
        # generate is a module, check for setup_parser function
        assert hasattr(generate, "setup_parser") and callable(generate.setup_parser)


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not installed")
def test_cli_module_imports():
    """Test that CLI modules can be imported."""
    from mysingle.cli import protos

    assert protos is not None
    assert hasattr(protos, "commands") or hasattr(protos, "__main__")

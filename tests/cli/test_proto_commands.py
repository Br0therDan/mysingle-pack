"""
Tests for mysingle.cli.protos commands.
"""

from pathlib import Path
from unittest.mock import Mock, patch

from mysingle.cli.protos.models import ProtoConfig


def test_proto_config_from_repo_root():
    """Test ProtoConfig initialization."""
    repo_root = Path(__file__).parent.parent.parent
    config = ProtoConfig.from_repo_root(repo_root)

    assert config.repo_root == repo_root
    assert config.protos_dir == repo_root / "protos"
    assert config.buf_yaml == repo_root / "protos" / "buf.yaml"
    assert config.buf_template == repo_root / "protos" / "buf.gen.yaml"


def test_proto_config_generated_root():
    """Test generated root path."""
    repo_root = Path(__file__).parent.parent.parent
    config = ProtoConfig.from_repo_root(repo_root)

    assert config.generated_root == repo_root / "src"
    assert config.package_name == "mysingle"


@patch("subprocess.run")
def test_proto_generate_command(mock_run):
    """Test proto generate command execution."""
    from mysingle.cli.protos.commands.generate import buf_generate

    mock_run.return_value = Mock(returncode=0)
    repo_root = Path(__file__).parent.parent.parent
    config = ProtoConfig.from_repo_root(repo_root)

    # Should not raise
    buf_generate(config)

    # Verify subprocess was called with correct arguments
    mock_run.assert_called_once()
    call_args = mock_run.call_args
    assert "buf" in call_args[0][0]
    assert "generate" in call_args[0][0]


def test_proto_validate_command():
    """Test proto validate command."""
    from mysingle.cli.protos.commands.validate import setup_parser

    parser = Mock()
    setup_parser(parser)

    # Parser should have arguments added
    parser.add_argument.assert_called()


def test_proto_status_command():
    """Test proto status command."""
    from mysingle.cli.protos.commands.status import setup_parser

    parser = Mock()
    setup_parser(parser)

    # Parser should have arguments added
    parser.add_argument.assert_called()


def test_proto_info_command():
    """Test proto info command."""
    from mysingle.cli.protos.commands.info import get_current_proto_version

    repo_root = Path(__file__).parent.parent.parent
    config = ProtoConfig.from_repo_root(repo_root)

    version = get_current_proto_version(config)
    assert version is not None
    assert isinstance(version, str)

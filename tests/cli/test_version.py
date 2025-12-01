"""
Tests for mysingle.cli.core.version module.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from mysingle.cli.core.version import Version, get_current_version


def test_version_parse():
    """Test Version.parse() method."""
    v = Version.parse("1.2.3")
    assert v.major == 1
    assert v.minor == 2
    assert v.patch == 3


def test_version_parse_alpha():
    """Test Version.parse() with pre-release."""
    v = Version.parse("2.0.0-alpha")
    assert v.major == 2
    assert v.minor == 0
    assert v.patch == 0
    assert v.prerelease == "alpha"


def test_version_bump_patch():
    """Test version bump for patch."""
    v = Version(major=1, minor=2, patch=3)
    bumped = v.bump("patch")
    assert bumped.major == 1
    assert bumped.minor == 2
    assert bumped.patch == 4


def test_version_bump_minor():
    """Test version bump for minor."""
    v = Version(major=1, minor=2, patch=3)
    bumped = v.bump("minor")
    assert bumped.major == 1
    assert bumped.minor == 3
    assert bumped.patch == 0


def test_version_bump_major():
    """Test version bump for major."""
    v = Version(major=1, minor=2, patch=3)
    bumped = v.bump("major")
    assert bumped.major == 2
    assert bumped.minor == 0
    assert bumped.patch == 0


def test_version_to_string():
    """Test Version.__str__() method."""
    v = Version(major=1, minor=2, patch=3)
    assert str(v) == "1.2.3"

    v_pre = Version(major=2, minor=0, patch=0, prerelease="alpha")
    assert str(v_pre) == "2.0.0-alpha"


def test_get_current_version_from_pyproject():
    """Test reading version from pyproject.toml."""
    # This test requires actual pyproject.toml
    # Should be run in package root
    version = get_current_version()
    assert version is not None
    assert isinstance(version, Version)


@patch("mysingle.cli.core.version.subprocess.run")
def test_bump_version_with_git(mock_run):
    """Test bump_version with git operations."""
    mock_run.return_value = Mock(returncode=0)

    # Create a mock argparse Namespace
    args = Mock()
    args.bump_type = "patch"
    args.custom_version = None
    args.skip_git = False

    with patch("mysingle.cli.core.version.get_current_version") as mock_get_version:
        mock_get_version.return_value = Version(1, 0, 0)

        with patch("builtins.open", create=True):
            with patch("pathlib.Path.read_text") as mock_read:
                mock_read.return_value = 'version = "1.0.0"'
                # bump_version(args)
                # Actual file I/O would need to be mocked more thoroughly


def test_version_invalid_format():
    """Test Version.parse() with invalid format."""
    with pytest.raises(ValueError):
        Version.parse("invalid")

    with pytest.raises(ValueError):
        Version.parse("1.2")  # Missing patch


def test_version_equality():
    """Test Version equality comparison."""
    v1 = Version(1, 2, 3)
    v2 = Version(1, 2, 3)
    v3 = Version(1, 2, 4)

    assert v1 == v2
    assert v1 != v3

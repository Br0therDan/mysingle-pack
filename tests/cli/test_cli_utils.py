"""Test mysingle CLI utilities."""

import pytest

from mysingle.cli.utils import (
    console,
    print_error,
    print_info,
    print_success,
    print_warning,
)


def test_console_instance():
    """Test console instance is available."""
    from rich.console import Console

    assert isinstance(console, Console)


def test_print_functions_execute():
    """Test print functions execute without error."""
    # These should not raise exceptions
    print_success("Success message")
    print_error("Error message")
    print_warning("Warning message")
    print_info("Info message")


def test_version_parser():
    """Test version parsing."""
    from mysingle.cli.core.version import Version

    # Normal version
    v = Version.parse("1.2.3")
    assert v.major == 1
    assert v.minor == 2
    assert v.patch == 3
    assert v.prerelease is None
    assert str(v) == "1.2.3"

    # Prerelease version
    v2 = Version.parse("2.0.0-alpha")
    assert v2.major == 2
    assert v2.minor == 0
    assert v2.patch == 0
    assert v2.prerelease == "alpha"
    assert str(v2) == "2.0.0-alpha"


def test_version_bump():
    """Test version bumping."""
    from mysingle.cli.core.version import Version

    v = Version(1, 2, 3)

    # Patch bump
    v_patch = v.bump("patch")
    assert str(v_patch) == "1.2.4"

    # Minor bump
    v_minor = v.bump("minor")
    assert str(v_minor) == "1.3.0"

    # Major bump
    v_major = v.bump("major")
    assert str(v_major) == "2.0.0"


def test_invalid_version():
    """Test invalid version parsing."""
    from mysingle.cli.core.version import Version

    with pytest.raises(ValueError):
        Version.parse("invalid")

    with pytest.raises(ValueError):
        Version.parse("1.2")

    with pytest.raises(ValueError):
        Version.parse("a.b.c")

"""
Tests for mysingle.protos module version tracking.
"""

import pytest


def test_proto_version_exists():
    """Test that proto version information exists."""
    try:
        from mysingle.protos import __version__

        assert __version__ is not None
    except ImportError:
        # Version file may not exist yet, skip test
        pytest.skip("Proto version file not yet generated")


def test_proto_module_structure():
    """Test that proto module has expected structure."""
    from mysingle import protos

    assert hasattr(protos, "common")
    assert hasattr(protos, "services")


def test_common_protos_available():
    """Test that common protos are available."""
    from mysingle.protos import common

    assert hasattr(common, "metadata_pb2")
    assert hasattr(common, "error_pb2")
    assert hasattr(common, "pagination_pb2")


def test_service_protos_available():
    """Test that service protos are available."""
    from mysingle.protos import services

    # Check that services module exists
    assert services is not None

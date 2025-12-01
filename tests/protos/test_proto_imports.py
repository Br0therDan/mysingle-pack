"""
Tests for mysingle.protos module (gRPC stubs).
"""



def test_proto_imports():
    """Test that proto stubs can be imported."""
    # Common protos
    from mysingle.protos.common import error_pb2, metadata_pb2

    assert error_pb2 is not None
    assert metadata_pb2 is not None

    # Check that message types are defined
    assert hasattr(metadata_pb2, "Metadata")
    assert hasattr(error_pb2, "ErrorDetail")  # Fixed: actual message name


def test_proto_message_creation():
    """Test creating proto message instances."""
    from mysingle.protos.common import metadata_pb2

    metadata = metadata_pb2.Metadata(
        user_id="test-user",
        request_id="test-request",  # Fixed: actual field name
        session_id="test-session",
    )

    assert metadata.user_id == "test-user"
    assert metadata.request_id == "test-request"
    assert metadata.session_id == "test-session"


def test_proto_error_message():
    """Test error proto message."""
    from mysingle.protos.common import error_pb2

    error = error_pb2.ErrorDetail(  # Fixed: actual message name
        code="TEST_ERROR",
        message="Test error message",
        severity=error_pb2.ERROR_SEVERITY_ERROR,
    )

    assert error.code == "TEST_ERROR"
    assert error.message == "Test error message"
    assert error.severity == error_pb2.ERROR_SEVERITY_ERROR


def test_proto_service_imports():
    """Test service proto imports."""
    # Test that service proto modules can be imported
    from mysingle.protos.services import (
        backtest,
        genai,
        iam,
        indicator,
        market_data,
        ml,
        strategy,
    )

    # Verify all service modules are accessible
    assert backtest is not None
    assert genai is not None
    assert iam is not None
    assert indicator is not None
    assert market_data is not None
    assert ml is not None
    assert strategy is not None


def test_proto_grpc_stub_imports():
    """Test gRPC stub imports."""
    # Test that gRPC stubs can be imported from common protos
    from mysingle.protos.common import (
        error_pb2_grpc,
        metadata_pb2_grpc,
        pagination_pb2_grpc,
    )

    # Verify gRPC stub modules are accessible (even if empty for common protos)
    assert error_pb2_grpc is not None
    assert metadata_pb2_grpc is not None
    assert pagination_pb2_grpc is not None

    # These are message-only protos, so they don't have service stubs
    # But the modules should exist and be importable


def test_proto_pagination():
    """Test pagination proto."""
    from mysingle.protos.common import pagination_pb2

    pagination = pagination_pb2.PaginationRequest(
        page=1,
        page_size=10,
    )

    assert pagination.page == 1
    assert pagination.page_size == 10


def test_proto_serialization():
    """Test proto message serialization."""
    from mysingle.protos.common import metadata_pb2

    metadata = metadata_pb2.Metadata(
        user_id="test-user",
        request_id="test-request",  # Fixed: actual field name
    )

    # Serialize to bytes
    serialized = metadata.SerializeToString()
    assert isinstance(serialized, bytes)

    # Deserialize
    deserialized = metadata_pb2.Metadata()
    deserialized.ParseFromString(serialized)

    assert deserialized.user_id == "test-user"
    assert deserialized.request_id == "test-request"

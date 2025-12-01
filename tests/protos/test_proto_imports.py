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
    assert hasattr(error_pb2, "Error")


def test_proto_message_creation():
    """Test creating proto message instances."""
    from mysingle.protos.common import metadata_pb2

    metadata = metadata_pb2.Metadata(
        user_id="test-user",
        correlation_id="test-correlation",
        request_id="test-request",
    )

    assert metadata.user_id == "test-user"
    assert metadata.correlation_id == "test-correlation"
    assert metadata.request_id == "test-request"


def test_proto_error_message():
    """Test error proto message."""
    from mysingle.protos.common import error_pb2

    error = error_pb2.Error(
        code="TEST_ERROR",
        message="Test error message",
        details="Additional details",
    )

    assert error.code == "TEST_ERROR"
    assert error.message == "Test error message"
    assert error.details == "Additional details"


def test_proto_service_imports():
    """Test service proto imports."""
    # Strategy service
    from mysingle.protos.services.strategy.v1 import strategy_service_pb2

    assert strategy_service_pb2 is not None


def test_proto_grpc_stub_imports():
    """Test gRPC stub imports."""
    from mysingle.protos.services.strategy.v1 import strategy_service_pb2_grpc

    assert strategy_service_pb2_grpc is not None
    # Check that stub classes are defined
    assert hasattr(strategy_service_pb2_grpc, "StrategyServiceStub")


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
        correlation_id="test-correlation",
    )

    # Serialize to bytes
    serialized = metadata.SerializeToString()
    assert isinstance(serialized, bytes)

    # Deserialize
    deserialized = metadata_pb2.Metadata()
    deserialized.ParseFromString(serialized)

    assert deserialized.user_id == "test-user"
    assert deserialized.correlation_id == "test-correlation"

"""
Tests for mysingle.clients.base_grpc_client module.
"""


import pytest

try:
    from mysingle.clients import BaseGrpcClient

    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False


@pytest.mark.skipif(not GRPC_AVAILABLE, reason="gRPC not installed")
class TestGrpcClient:
    """Tests for gRPC client."""

    def test_grpc_client_initialization(self):
        """Test gRPC client initialization."""
        client = BaseGrpcClient(
            service_name="test-service",
            default_port=50051,
        )

        assert client is not None
        assert client.service_name == "test-service"

    def test_grpc_client_with_user_context(self):
        """Test gRPC client with user context."""
        client = BaseGrpcClient(
            service_name="test-service",
            default_port=50051,
            user_id="test-user-123",
            correlation_id="test-correlation-456",
        )

        assert client.user_id == "test-user-123"
        assert client.correlation_id == "test-correlation-456"

    def test_grpc_client_metadata_generation(self):
        """Test gRPC client metadata generation."""
        client = BaseGrpcClient(
            service_name="test-service",
            default_port=50051,
            user_id="test-user-123",
        )

        metadata = client.get_metadata()

        assert metadata is not None
        # Check that user_id is in metadata
        metadata_dict = dict(metadata)
        assert "user-id" in metadata_dict
        assert metadata_dict["user-id"] == "test-user-123"

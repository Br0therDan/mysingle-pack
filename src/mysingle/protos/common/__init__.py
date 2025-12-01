"""Common proto messages."""

# Import well-known types first to ensure they're loaded in the descriptor pool
from google.protobuf import struct_pb2  # noqa: F401

from . import error_pb2, metadata_pb2, pagination_pb2

__all__ = [
    "error_pb2",
    "metadata_pb2",
    "pagination_pb2",
]

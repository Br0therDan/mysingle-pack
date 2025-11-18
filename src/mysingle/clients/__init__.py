"""
Microservice HTTP/gRPC Clients

마이크로서비스 간 HTTP/gRPC 통신을 위한 공통 클라이언트 베이스 클래스
"""

from .base_client import BaseServiceClient
from .base_grpc_client import BaseGrpcClient

__all__ = ["BaseServiceClient", "BaseGrpcClient"]

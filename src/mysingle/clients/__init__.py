"""
Microservice gRPC Clients

마이크로서비스 간 gRPC 통신을 위한 공통 클라이언트 베이스 클래스
"""

from .base_grpc_client import BaseGrpcClient
from .http_client import (
    HttpClientConfig,
    ServiceHttpClient,
    ServiceHttpClientManager,
    create_service_http_client,
    get_service_http_client,
    http_client_lifespan,
    make_service_request,
)

__all__ = [
    "BaseGrpcClient",
    # HTTP Client
    "ServiceHttpClient",
    "ServiceHttpClientManager",
    "create_service_http_client",
    "get_service_http_client",
    "make_service_request",
    "http_client_lifespan",
    "HttpClientConfig",
]

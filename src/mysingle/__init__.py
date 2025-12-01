"""mysingle package public API (lazy exports)

이 패키지의 루트에서는 무거운 서브모듈을 즉시 import 하지 않고,
요청 시점에 지연 로딩하여 순환 참조와 초기화 비용을 줄입니다.

외부 사용자는 기존과 동일하게 다음과 같이 사용할 수 있습니다:

    from mysingle import get_logger, BaseDuckDBManager, create_fastapi_app

내부적으로는 PEP 562의 __getattr__을 활용해 필요한 기호만 지연 import 합니다.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

# 공개 심볼 목록(동일 유지)
__all__ = [
    # Core: Config
    "settings",
    "get_settings",
    "CommonSettings",
    # Core: Logging (consolidated)
    "get_logger",
    "setup_logging",
    # Core: Base (consolidated)
    "BaseDoc",
    "BaseTimeDoc",
    "BaseTimeDocWithUserId",
    "BaseResponseSchema",
    # Core: Metrics (consolidated)
    "MetricsCollector",
    "get_metrics_collector",
    # Core: Health (consolidated)
    "HealthChecker",
    "register_health_routes",
    # Core: Email (consolidated)
    "EmailService",
    "send_email",
    # Core: Audit (consolidated)
    "AuditLogger",
    "log_audit_event",
    # Core: Database
    "init_mongo",
    "get_mongodb_url",
    "get_database_name",
    # Core: FastAPI app factory
    "create_fastapi_app",
    "create_lifespan",
    # Database: DuckDB
    "BaseDuckDBManager",
    # Clients: gRPC Service Clients
    "BaseGrpcClient",
    # Constants: HTTP Headers
    "HEADER_AUTHORIZATION",
    "HEADER_USER_ID",
    "HEADER_CORRELATION_ID",
    "HEADER_KONG_USER_ID",
    "HEADER_KONG_CONSUMER_ID",
    "HEADER_KONG_REQUEST_ID",
    # Constants: gRPC Metadata
    "GRPC_METADATA_USER_ID",
    "GRPC_METADATA_AUTHORIZATION",
    "GRPC_METADATA_CORRELATION_ID",
    "GRPC_METADATA_REQUEST_ID",
    # gRPC: Interceptors
    "AuthInterceptor",
    "LoggingInterceptor",
    "MetadataInterceptor",
    "ClientAuthInterceptor",
]

# 지연 로딩 매핑: 심볼명 -> (모듈경로, 속성명)
_EXPORTS = {
    # Core
    "settings": ("mysingle.core", "settings"),
    "get_settings": ("mysingle.core", "get_settings"),
    "CommonSettings": ("mysingle.core", "CommonSettings"),
    "create_fastapi_app": ("mysingle.core", "create_fastapi_app"),
    "create_lifespan": ("mysingle.core", "create_lifespan"),
    "init_mongo": ("mysingle.core", "init_mongo"),
    "get_mongodb_url": ("mysingle.core", "get_mongodb_url"),
    "get_database_name": ("mysingle.core", "get_database_name"),
    # Logging (consolidated to core)
    "get_logger": ("mysingle.core.logging", "get_logger"),
    "setup_logging": ("mysingle.core.logging", "setup_logging"),
    # Base (consolidated to core)
    "BaseDoc": ("mysingle.core.base", "BaseDoc"),
    "BaseTimeDoc": ("mysingle.core.base", "BaseTimeDoc"),
    "BaseTimeDocWithUserId": ("mysingle.core.base", "BaseTimeDocWithUserId"),
    "BaseResponseSchema": ("mysingle.core.base", "BaseResponseSchema"),
    # Metrics (consolidated to core)
    "MetricsCollector": ("mysingle.core.metrics", "MetricsCollector"),
    "get_metrics_collector": ("mysingle.core.metrics", "get_metrics_collector"),
    # Health (consolidated to core)
    "HealthChecker": ("mysingle.core.health", "HealthChecker"),
    "register_health_routes": ("mysingle.core.health", "register_health_routes"),
    # Email (consolidated to core)
    "EmailService": ("mysingle.core.email", "EmailService"),
    "send_email": ("mysingle.core.email", "send_email"),
    # Audit (consolidated to core)
    "AuditLogger": ("mysingle.core.audit", "AuditLogger"),
    "log_audit_event": ("mysingle.core.audit", "log_audit_event"),
    # Database
    "BaseDuckDBManager": ("mysingle.database", "BaseDuckDBManager"),
    # Clients: gRPC
    "BaseGrpcClient": ("mysingle.clients", "BaseGrpcClient"),
    # Constants: HTTP Headers
    "HEADER_AUTHORIZATION": ("mysingle.constants", "HEADER_AUTHORIZATION"),
    "HEADER_USER_ID": ("mysingle.constants", "HEADER_USER_ID"),
    "HEADER_CORRELATION_ID": ("mysingle.constants", "HEADER_CORRELATION_ID"),
    "HEADER_KONG_USER_ID": ("mysingle.constants", "HEADER_KONG_USER_ID"),
    "HEADER_KONG_CONSUMER_ID": ("mysingle.constants", "HEADER_KONG_CONSUMER_ID"),
    "HEADER_KONG_REQUEST_ID": ("mysingle.constants", "HEADER_KONG_REQUEST_ID"),
    # Constants: gRPC Metadata
    "GRPC_METADATA_USER_ID": ("mysingle.constants", "GRPC_METADATA_USER_ID"),
    "GRPC_METADATA_AUTHORIZATION": (
        "mysingle.constants",
        "GRPC_METADATA_AUTHORIZATION",
    ),
    "GRPC_METADATA_CORRELATION_ID": (
        "mysingle.constants",
        "GRPC_METADATA_CORRELATION_ID",
    ),
    "GRPC_METADATA_REQUEST_ID": ("mysingle.constants", "GRPC_METADATA_REQUEST_ID"),
    # gRPC Interceptors
    "AuthInterceptor": ("mysingle.grpc", "AuthInterceptor"),
    "LoggingInterceptor": ("mysingle.grpc", "LoggingInterceptor"),
    "MetadataInterceptor": ("mysingle.grpc", "MetadataInterceptor"),
    "ClientAuthInterceptor": ("mysingle.grpc", "ClientAuthInterceptor"),
}


def __getattr__(name: str):
    target = _EXPORTS.get(name)
    if not target:
        raise AttributeError(f"module 'mysingle' has no attribute {name!r}")
    module_name, attr_name = target
    module = importlib.import_module(module_name)
    try:
        attr = getattr(module, attr_name)
    except AttributeError as e:
        raise AttributeError(
            f"Failed to resolve attribute {name!r} from {module_name}.{attr_name}"
        ) from e
    globals()[name] = attr  # cache for future lookups
    return attr


def __dir__():  # pragma: no cover
    return sorted(list(globals().keys()) + list(__all__))


if TYPE_CHECKING:  # 타입체커를 위한 정적 import (런타임에는 지연 로딩)
    from .clients import BaseGrpcClient as BaseGrpcClient
    from .constants import GRPC_METADATA_AUTHORIZATION as GRPC_METADATA_AUTHORIZATION
    from .constants import GRPC_METADATA_CORRELATION_ID as GRPC_METADATA_CORRELATION_ID
    from .constants import GRPC_METADATA_REQUEST_ID as GRPC_METADATA_REQUEST_ID
    from .constants import GRPC_METADATA_USER_ID as GRPC_METADATA_USER_ID
    from .constants import HEADER_AUTHORIZATION as HEADER_AUTHORIZATION
    from .constants import HEADER_CORRELATION_ID as HEADER_CORRELATION_ID
    from .constants import HEADER_KONG_CONSUMER_ID as HEADER_KONG_CONSUMER_ID
    from .constants import HEADER_KONG_REQUEST_ID as HEADER_KONG_REQUEST_ID
    from .constants import HEADER_KONG_USER_ID as HEADER_KONG_USER_ID
    from .constants import HEADER_USER_ID as HEADER_USER_ID
    from .core import (
        CommonSettings as CommonSettings,
    )
    from .core import (
        create_fastapi_app as create_fastapi_app,
    )
    from .core import (
        create_lifespan as create_lifespan,
    )
    from .core import (
        get_database_name as get_database_name,
    )
    from .core import (
        get_mongodb_url as get_mongodb_url,
    )
    from .core import (
        get_settings as get_settings,
    )
    from .core import (
        init_mongo as init_mongo,
    )
    from .core import (
        settings as settings,
    )
    from .database import BaseDuckDBManager as BaseDuckDBManager
    from .grpc import AuthInterceptor as AuthInterceptor
    from .grpc import ClientAuthInterceptor as ClientAuthInterceptor
    from .grpc import LoggingInterceptor as LoggingInterceptor
    from .grpc import MetadataInterceptor as MetadataInterceptor
    from .logging import get_logger as get_logger

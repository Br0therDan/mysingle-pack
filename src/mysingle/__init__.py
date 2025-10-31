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
    "get_logger",
    # Core: Database
    "init_mongo",
    "get_mongodb_url",
    "get_database_name",
    # Core: FastAPI app factory
    "create_fastapi_app",
    "create_lifespan",
    # Database: DuckDB
    "BaseDuckDBManager",
    # Clients: HTTP Service Clients
    "BaseServiceClient",
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
    # Logging
    "get_logger": ("mysingle.logging", "get_logger"),
    # Database
    "BaseDuckDBManager": ("mysingle.database", "BaseDuckDBManager"),
    # Clients
    "BaseServiceClient": ("mysingle.clients", "BaseServiceClient"),
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
    from .clients import BaseServiceClient as BaseServiceClient
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
    from .logging import get_logger as get_logger

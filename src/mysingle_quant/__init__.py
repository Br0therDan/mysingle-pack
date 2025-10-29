from .clients import BaseServiceClient
from .core import (
    CommonSettings,
    create_fastapi_app,
    create_lifespan,
    get_database_name,
    get_mongodb_url,
    get_settings,
    init_mongo,
    settings,
)
from .logging import get_logger
from .database import BaseDuckDBManager

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

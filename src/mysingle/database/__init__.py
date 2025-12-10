"""Database utilities for DuckDB and Redis"""

from .cache_factory import (
    create_grpc_cache,
    create_service_cache,
    create_user_cache,
)
from .duckdb_manager import BaseDuckDBManager
from .redis import (
    RedisClientManager,
    RedisConfig,
    get_redis_client,
    get_redis_manager,
    reset_redis_manager,
)
from .redis_cache import BaseRedisCache

__all__ = [
    # DuckDB
    "BaseDuckDBManager",
    # Redis Client
    "RedisConfig",
    "RedisClientManager",
    "get_redis_client",
    "get_redis_manager",
    "reset_redis_manager",
    # Redis Cache
    "BaseRedisCache",
    # Cache Factories
    "create_user_cache",
    "create_grpc_cache",
    "create_service_cache",
]

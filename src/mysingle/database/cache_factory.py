"""
Cache Factory Functions

플랫폼 표준 Redis 캐시 생성을 위한 팩토리 함수들입니다.
이 함수들을 사용하면 올바른 DB 번호가 자동으로 할당됩니다.

Usage:
    from mysingle.database import create_service_cache
    from mysingle.core.config import settings

    # Create a service-specific cache
    cache = create_service_cache(
        service_name="backtest",
        db_constant=settings.REDIS_DB_BACKTEST,
    )
"""

from mysingle.core.config import settings
from mysingle.core.logging import get_structured_logger
from mysingle.database.redis_cache import BaseRedisCache

logger = get_structured_logger(__name__)


def create_user_cache(
    *,
    default_ttl: int = 300,
) -> BaseRedisCache:
    """
    User authentication cache 생성 (DB 0)

    Args:
        default_ttl: 기본 TTL (초), 기본값 300초 (5분)

    Returns:
        User 캐시 인스턴스

    Example:
        ```python
        cache = create_user_cache()
        await cache.set(user_id, user_data)
        ```
    """
    logger.debug("Creating user cache", extra={"db": settings.REDIS_DB_USER})

    class UserCache(BaseRedisCache):
        def __init__(self):
            super().__init__(
                key_prefix="user",
                default_ttl=default_ttl,
                redis_db=settings.REDIS_DB_USER,
            )

    return UserCache()


def create_grpc_cache(
    service_name: str,
    *,
    default_ttl: int = 3600,
) -> BaseRedisCache:
    """
    gRPC response cache 생성 (DB 1)

    Args:
        service_name: 서비스 이름 (key prefix에 사용)
        default_ttl: 기본 TTL (초), 기본값 3600초 (1시간)

    Returns:
        gRPC 캐시 인스턴스

    Example:
        ```python
        cache = create_grpc_cache("strategy-service")
        await cache.set(cache_key, response_data)
        ```
    """
    logger.debug(
        "Creating gRPC cache",
        extra={"service_name": service_name, "db": settings.REDIS_DB_GRPC},
    )

    class GrpcResponseCache(BaseRedisCache):
        def __init__(self):
            super().__init__(
                key_prefix=f"grpc:{service_name}",
                default_ttl=default_ttl,
                redis_db=settings.REDIS_DB_GRPC,
                use_json=False,  # Use pickle for protobuf
            )

    return GrpcResponseCache()


def create_service_cache(
    service_name: str,
    db_constant: int,
    *,
    default_ttl: int = 3600,
    use_json: bool = True,
) -> BaseRedisCache:
    """
    범용 서비스 캐시 생성

    Args:
        service_name: 서비스 이름 (key prefix에 사용)
        db_constant: CommonSettings의 REDIS_DB_* 상수
        default_ttl: 기본 TTL (초)
        use_json: JSON 직렬화 사용 여부

    Returns:
        서비스 캐시 인스턴스

    Example:
        ```python
        from mysingle.core.config import settings

        # Backtest service cache
        cache = create_service_cache(
            "backtest",
            db_constant=settings.REDIS_DB_BACKTEST,
            default_ttl=7200,
        )

        # Market data cache
        market_cache = create_service_cache(
            "market",
            db_constant=settings.REDIS_DB_MARKET_DATA,
            default_ttl=300,
        )
        ```
    """
    logger.debug(
        "Creating service cache",
        extra={
            "service_name": service_name,
            "db": db_constant,
            "ttl": default_ttl,
        },
    )

    class ServiceCache(BaseRedisCache):
        def __init__(self):
            super().__init__(
                key_prefix=service_name,
                default_ttl=default_ttl,
                redis_db=db_constant,
                use_json=use_json,
            )

    return ServiceCache()

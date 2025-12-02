"""
Base Redis Cache for Generic Key-Value Storage

범용 Redis 캐시 기본 클래스를 제공합니다.
서비스별 커스텀 캐시 구현의 기반이 됩니다.

Features:
- TTL-based expiration
- Automatic serialization (JSON/Pickle)
- Type-safe operations
- Health monitoring

Usage:
    from mysingle.database.redis_cache import BaseRedisCache

    class MarketDataCache(BaseRedisCache):
        '''Market data specific cache'''

        def __init__(self, redis_db: int = 1):
            super().__init__(
                key_prefix="market",
                default_ttl=60,
                redis_db=redis_db
            )

    # Use the cache
    cache = MarketDataCache()
    await cache.set("ticker:AAPL", {"price": 150.0, "volume": 1000000})
    data = await cache.get("ticker:AAPL")
"""

import json
import pickle
from abc import ABC
from typing import Generic, Optional, TypeVar

from mysingle.core.logging import get_structured_logger
from mysingle.database.redis import get_redis_client

logger = get_structured_logger(__name__)

T = TypeVar("T")


class BaseRedisCache(ABC, Generic[T]):
    """
    범용 Redis 캐시 기본 클래스

    서비스별 캐시를 구현할 때 이 클래스를 상속받습니다.
    """

    def __init__(
        self,
        *,
        key_prefix: str,
        default_ttl: int = 300,
        redis_db: int = 0,
        use_json: bool = True,
    ):
        """
        Args:
            key_prefix: 캐시 키 접두사 (예: "market", "indicator")
            default_ttl: 기본 TTL (초)
            redis_db: Redis DB 번호
            use_json: JSON 직렬화 사용 (False면 pickle 사용)
        """
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self.redis_db = redis_db
        self.use_json = use_json
        self._redis_client = None

    async def _get_redis(self):
        """Redis 클라이언트 가져오기 (lazy loading)"""
        if self._redis_client is None:
            self._redis_client = await get_redis_client(db=self.redis_db)
        return self._redis_client

    def _make_key(self, key: str) -> str:
        """전체 캐시 키 생성"""
        return f"{self.key_prefix}:{key}"

    def _serialize(self, value: T) -> str | bytes:
        """값 직렬화"""
        if self.use_json:
            return json.dumps(value, default=str)
        else:
            return pickle.dumps(value)

    def _deserialize(self, data: str | bytes) -> T:
        """값 역직렬화"""
        if self.use_json:
            return json.loads(data)  # type: ignore
        else:
            return pickle.loads(data)  # type: ignore

    async def get(self, key: str) -> Optional[T]:
        """
        캐시에서 값 조회

        Args:
            key: 캐시 키 (접두사 제외)

        Returns:
            캐시된 값 또는 None
        """
        redis = await self._get_redis()
        if redis is None:
            logger.warning(f"Redis not available for get: {key}")
            return None

        try:
            cache_key = self._make_key(key)
            data = await redis.get(cache_key)

            if data:
                logger.debug(f"Cache HIT: {cache_key}")
                return self._deserialize(data)
            else:
                logger.debug(f"Cache MISS: {cache_key}")
                return None

        except Exception as e:
            logger.error(f"Redis get error for {key}: {e}")
            return None

    async def set(self, key: str, value: T, ttl: Optional[int] = None) -> bool:
        """
        캐시에 값 저장

        Args:
            key: 캐시 키 (접두사 제외)
            value: 저장할 값
            ttl: TTL (초), None이면 default_ttl 사용

        Returns:
            성공 여부
        """
        redis = await self._get_redis()
        if redis is None:
            logger.warning(f"Redis not available for set: {key}")
            return False

        try:
            cache_key = self._make_key(key)
            data = self._serialize(value)
            ttl_to_use = ttl if ttl is not None else self.default_ttl

            await redis.setex(cache_key, ttl_to_use, data)
            logger.debug(f"Cache SET: {cache_key}, TTL: {ttl_to_use}s")
            return True

        except Exception as e:
            logger.error(f"Redis set error for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        캐시에서 값 삭제

        Args:
            key: 캐시 키 (접두사 제외)

        Returns:
            성공 여부
        """
        redis = await self._get_redis()
        if redis is None:
            logger.warning(f"Redis not available for delete: {key}")
            return False

        try:
            cache_key = self._make_key(key)
            await redis.delete(cache_key)
            logger.debug(f"Cache DELETE: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Redis delete error for {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        캐시 키 존재 여부 확인

        Args:
            key: 캐시 키 (접두사 제외)

        Returns:
            존재 여부
        """
        redis = await self._get_redis()
        if redis is None:
            return False

        try:
            cache_key = self._make_key(key)
            result = await redis.exists(cache_key)
            return bool(result)

        except Exception as e:
            logger.error(f"Redis exists error for {key}: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """
        캐시 키의 TTL 갱신

        Args:
            key: 캐시 키 (접두사 제외)
            ttl: 새로운 TTL (초)

        Returns:
            성공 여부
        """
        redis = await self._get_redis()
        if redis is None:
            return False

        try:
            cache_key = self._make_key(key)
            await redis.expire(cache_key, ttl)
            logger.debug(f"Cache EXPIRE: {cache_key}, TTL: {ttl}s")
            return True

        except Exception as e:
            logger.error(f"Redis expire error for {key}: {e}")
            return False

    async def clear_all(self) -> int:
        """
        접두사에 해당하는 모든 캐시 삭제

        Returns:
            삭제된 키 개수
        """
        redis = await self._get_redis()
        if redis is None:
            return 0

        try:
            pattern = f"{self.key_prefix}:*"
            cursor = 0
            deleted = 0

            while True:
                cursor, keys = await redis.scan(cursor, match=pattern, count=100)
                if keys:
                    deleted += await redis.delete(*keys)
                if cursor == 0:
                    break

            logger.info(
                f"Cache CLEARED: {deleted} keys with prefix '{self.key_prefix}'"
            )
            return deleted

        except Exception as e:
            logger.error(f"Redis clear_all error: {e}")
            return 0

    async def health_check(self) -> bool:
        """Redis 연결 상태 확인"""
        redis = await self._get_redis()
        if redis is None:
            return False

        try:
            await redis.ping()
            return True
        except Exception:
            return False

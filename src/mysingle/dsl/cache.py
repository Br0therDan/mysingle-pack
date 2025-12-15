"""
DSL Caching Layer - Redis-based bytecode cache

Provides distributed caching for compiled DSL bytecode with TTL management
and cache invalidation strategies.

Usage:
    from mysingle.dsl.cache import DSLBytecodeCache

    # Redis cache (production)
    cache = DSLBytecodeCache()
    await cache.set("strategy:hash123", bytecode)
    bytecode = await cache.get("strategy:hash123")

    # In-memory cache (development/testing)
    cache = InMemoryDSLCache()
    await cache.set("strategy:hash123", bytecode)
"""

from datetime import UTC, datetime
from typing import Any, Dict, Optional

from mysingle.core.config import settings
from mysingle.core.logging import get_structured_logger
from mysingle.database import BaseRedisCache

logger = get_structured_logger(__name__)


class DSLBytecodeCache(BaseRedisCache[bytes]):
    """
    Redis-based DSL bytecode cache using BaseRedisCache

    Inherits from BaseRedisCache for standardized caching with:
    - Automatic TTL management
    - Connection pooling
    - Health checks
    - Structured logging
    """

    def __init__(self):
        """
        Initialize DSL bytecode cache with settings from config

        Uses:
            - REDIS_DB_DSL: Redis database number (default: 5)
            - DSL_CACHE_TTL_SECONDS: Default TTL (default: 3600)
            - DSL_CACHE_KEY_PREFIX: Key prefix (default: "dsl:bytecode")
        """

        super().__init__(
            key_prefix=settings.DSL_CACHE_KEY_PREFIX,
            default_ttl=settings.DSL_CACHE_TTL_SECONDS,
            redis_db=settings.REDIS_DB_DSL,
            use_json=False,  # Use pickle for bytes serialization
        )

        logger.info(
            "DSL bytecode cache initialized",
            redis_db=settings.REDIS_DB_DSL,
            default_ttl=settings.DSL_CACHE_TTL_SECONDS,
        )

    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern (compatible with old API)

        Args:
            pattern: Pattern to match (e.g., "strategy:*")

        Returns:
            Number of keys deleted
        """
        # Convert pattern to full key format
        full_pattern = f"{self.key_prefix}:{pattern}"

        redis = await self._get_redis()
        if redis is None:
            logger.warning("Redis not available for clear_pattern")
            return 0

        try:
            cursor = 0
            deleted = 0

            while True:
                cursor, keys = await redis.scan(cursor, match=full_pattern, count=100)
                if keys:
                    deleted += await redis.delete(*keys)
                if cursor == 0:
                    break

            logger.info("Cache cleared", pattern=pattern, count=deleted)
            return deleted

        except Exception as e:
            logger.error("Clear pattern failed", pattern=pattern, error=str(e))
            return 0


# Legacy alias for backward compatibility
RedisDSLCache = DSLBytecodeCache


class InMemoryDSLCache:
    """
    In-memory DSL cache for testing/development

    Provides the same interface as DSLBytecodeCache but stores data in memory.
    Useful for testing and development environments where Redis is not available.
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize in-memory cache

        Args:
            max_size: Maximum number of cached items
        """
        self.max_size = max_size
        self._cache: Dict[
            str, tuple[bytes, float]
        ] = {}  # key -> (value, expiry_timestamp)

        logger.info("In-memory DSL cache initialized", max_size=max_size)

    def _is_expired(self, expiry: float) -> bool:
        """Check if cache entry is expired"""
        return datetime.now(UTC).timestamp() > expiry

    def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        now = datetime.now(UTC).timestamp()
        expired_keys = [k for k, (_, exp) in self._cache.items() if now > exp]

        for key in expired_keys:
            del self._cache[key]

    async def get(self, key: str) -> Optional[bytes]:
        """Retrieve from in-memory cache"""
        self._cleanup_expired()

        if key in self._cache:
            value, expiry = self._cache[key]
            if not self._is_expired(expiry):
                logger.debug("Cache hit", key=key)
                return value
            else:
                del self._cache[key]

        logger.debug("Cache miss", key=key)
        return None

    async def set(self, key: str, value: bytes, ttl: int = 3600) -> bool:
        """Store in in-memory cache"""
        self._cleanup_expired()

        # Evict oldest if at max size
        if len(self._cache) >= self.max_size and key not in self._cache:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        expiry = datetime.now(UTC).timestamp() + ttl
        self._cache[key] = (value, expiry)

        logger.debug("Cache set", key=key, ttl=ttl, size=len(value))
        return True

    async def delete(self, key: str) -> bool:
        """Delete from in-memory cache"""
        if key in self._cache:
            del self._cache[key]
            logger.debug("Cache delete", key=key)
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        self._cleanup_expired()
        return key in self._cache

    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern (simple prefix match)"""
        # Simple implementation: pattern is prefix
        prefix = pattern.replace("*", "")
        matching_keys = [k for k in self._cache if k.startswith(prefix)]

        for key in matching_keys:
            del self._cache[key]

        logger.info("Cache cleared", pattern=pattern, count=len(matching_keys))
        return len(matching_keys)

    async def health_check(self) -> bool:
        """Health check always succeeds for in-memory cache"""
        return True


class DSLCacheManager:
    """
    Cache manager with warming and invalidation strategies

    Supports both Redis and in-memory cache backends.

    Usage:
        # Redis backend (production)
        cache = DSLCacheManager(backend=DSLBytecodeCache())
        await cache.warm_cache(popular_strategies)
        await cache.invalidate_version("1.1.0")

        # In-memory backend (development/testing)
        cache = DSLCacheManager(backend=InMemoryDSLCache())
    """

    def __init__(self, backend: DSLBytecodeCache | InMemoryDSLCache):
        """
        Initialize cache manager

        Args:
            backend: Cache backend (DSLBytecodeCache or InMemoryDSLCache)
        """
        self.backend = backend

        logger.info("DSL cache manager initialized", backend=backend.__class__.__name__)

    async def warm_cache(
        self,
        code_list: list[tuple[str, str]],  # [(code, version), ...]
        service_name: str = "strategy",
    ) -> int:
        """
        Warm cache with popular DSL code

        Args:
            code_list: List of (code, version) tuples
            service_name: Service name for cache key

        Returns:
            Number of entries warmed
        """
        import hashlib

        from mysingle.dsl.parser import DSLParser

        parser = DSLParser()
        warmed_count = 0

        logger.info(
            "Starting cache warming", count=len(code_list), service=service_name
        )

        for code, _version in code_list:
            try:
                # Compile
                bytecode = parser.parse(code)
                if bytecode:
                    # Generate cache key (without prefix, backend adds it)
                    code_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()
                    cache_key = f"{service_name}:{code_hash}"

                    # Store in cache with warming TTL
                    await self.backend.set(
                        cache_key, bytecode, ttl=settings.DSL_CACHE_WARMING_TTL_SECONDS
                    )
                    warmed_count += 1

            except Exception as e:
                logger.error("Cache warming failed for code", error=str(e))

        logger.info("Cache warming complete", warmed=warmed_count)
        return warmed_count

    async def invalidate_version(self, version: str, service_name: str = "*") -> int:
        """
        Invalidate all cache entries for a specific DSL version

        Args:
            version: DSL version to invalidate
            service_name: Service name or "*" for all services

        Returns:
            Number of entries invalidated
        """
        pattern = f"{service_name}:*"

        logger.info("Invalidating cache", version=version, pattern=pattern)

        deleted = await self.backend.clear_pattern(pattern)

        logger.info("Cache invalidation complete", deleted=deleted)
        return deleted

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics (if supported by backend)"""
        # This would require backend-specific implementation
        return {
            "backend": self.backend.__class__.__name__,
            "timestamp": datetime.now(UTC).isoformat(),
        }

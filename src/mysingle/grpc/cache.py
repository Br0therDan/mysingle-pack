"""
gRPC Cache Manager

BaseRedisCache를 상속받아 gRPC 특화 캐싱 기능을 제공합니다.
- L1 In-Memory LRU + L2 Redis 2-tier 캐시
- Protobuf 메시지 직렬화 지원
- gRPC 메타데이터 통합 (user_id, correlation_id)
- Prometheus 메트릭 자동 수집

Usage:
    ```python
    from mysingle.grpc.cache import GrpcCache, grpc_cached

    class StrategyServiceServicer:
        def __init__(self):
            self.cache = GrpcCache(
                service_name="strategy-service",
                redis_db=2,  # gRPC 전용 DB
            )

        @grpc_cached(ttl=300, use_metadata=True)
        async def GetStrategyVersion(self, request, context):
            # 캐시 미스 시에만 실행
            version = await db.get_strategy_version(...)
            return version
    ```
"""

from __future__ import annotations

import hashlib
import json
import time
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar

from google.protobuf.message import Message as ProtoMessage

from mysingle.core.config import settings
from mysingle.core.logging import get_structured_logger
from mysingle.database.redis_cache import BaseRedisCache

if TYPE_CHECKING:
    from mysingle.core.config import CommonSettings

logger = get_structured_logger(__name__)

T = TypeVar("T")

# Prometheus 메트릭 (lazy import)
try:
    from prometheus_client import Counter

    grpc_cache_hits = Counter(
        "mysingle_grpc_cache_hits_total",
        "gRPC cache hits",
        ["service", "method", "layer"],
    )
    grpc_cache_misses = Counter(
        "mysingle_grpc_cache_misses_total",
        "gRPC cache misses",
        ["service", "method"],
    )
    _METRICS_ENABLED = True
except ImportError:
    _METRICS_ENABLED = False
    logger.warning("prometheus_client not installed - cache metrics disabled")


class GrpcCache(BaseRedisCache[T]):
    """
    gRPC 전용 2-tier 캐시 (L1: In-Memory + L2: Redis)

    BaseRedisCache를 상속받아 Redis 연결 관리를 재사용하고,
    gRPC 특화 기능(Protobuf 직렬화, 메타데이터)을 추가합니다.

    CommonSettings의 GRPC_CACHE_* 환경변수를 기본값으로 사용합니다.

    Features:
    - L1 In-Memory LRU (기본 5분 TTL, 100개 제한)
    - L2 Redis (기본 1시간 TTL, BaseRedisCache)
    - Protobuf 메시지 직렬화
    - gRPC 메타데이터 자동 포함 (user_id, correlation_id)
    - Prometheus 메트릭 (cache_hits, cache_misses)

    Example:
        ```python
        from mysingle.core.config import settings
        from mysingle.grpc.cache import GrpcCache

        # CommonSettings 기반 자동 구성
        cache = GrpcCache.from_settings(
            settings=settings,
            service_name="strategy-service",
        )

        # 또는 수동 구성
        cache = GrpcCache(
            service_name="strategy-service",
            redis_db=2,
            memory_ttl=300,
        )
        ```
    """

    def __init__(
        self,
        *,
        service_name: str,
        memory_ttl: int = 300,  # L1 TTL (5분)
        memory_max_size: int = 100,  # L1 LRU 크기
        default_ttl: int = 3600,  # L2 Redis TTL (1시간)
    ):
        """
        gRPC 캐시 초기화 (Redis DB 1 전용)

        Args:
            service_name: 서비스 이름 (캐시 키 prefix)
            memory_ttl: L1 in-memory TTL (초)
            memory_max_size: L1 LRU 캐시 최대 크기
            default_ttl: L2 Redis TTL (초)

        Note:
            Redis DB는 자동으로 settings.REDIS_DB_GRPC(=1)로 고정됩니다.
            플랫폼 표준을 준수하기 위해 변경할 수 없습니다.
        """
        # BaseRedisCache 초기화 (key_prefix="grpc:{service_name}", DB=1)
        super().__init__(
            key_prefix=f"grpc:{service_name}",
            default_ttl=default_ttl,
            redis_db=settings.REDIS_DB_GRPC,  # Always use DB 1 for gRPC cache
            use_json=False,  # Protobuf는 pickle 사용
        )

        self.service_name = service_name
        self.memory_ttl = memory_ttl
        self.memory_max_size = memory_max_size

        # L1: In-Memory LRU Cache
        self._memory_cache: dict[str, tuple[Any, float]] = {}  # (value, timestamp)

    @classmethod
    def from_settings(
        cls,
        settings: CommonSettings,
        service_name: str,
        **overrides,
    ) -> GrpcCache:
        """
        CommonSettings에서 캐시 설정을 가져와 GrpcCache 생성

        Args:
            settings: CommonSettings 인스턴스
            service_name: 서비스 이름 (캐시 키 prefix)
            **overrides: 추가 오버라이드 설정

        Returns:
            GrpcCache 인스턴스

        Example:
            ```python
            from mysingle.core.config import settings
            from mysingle.grpc.cache import GrpcCache

            cache = GrpcCache.from_settings(
                settings=settings,
                service_name="strategy-service",
                memory_ttl=600,  # 10분으로 오버라이드
            )
            ```
        """
        cache_config = {
            "service_name": service_name,
            "memory_ttl": settings.GRPC_CACHE_L1_TTL_SECONDS,
            "memory_max_size": settings.GRPC_CACHE_L1_MAX_SIZE,
            "default_ttl": settings.GRPC_CACHE_L2_TTL_SECONDS,
        }

        # 오버라이드 적용 (redis_db는 제외 - 항상 REDIS_DB_GRPC 사용)
        allowed_overrides = {k: v for k, v in overrides.items() if k != "redis_db"}
        cache_config.update(allowed_overrides)

        if "redis_db" in overrides:
            logger.warning(
                "redis_db override ignored for GrpcCache (always uses REDIS_DB_GRPC)",
                extra={
                    "service_name": service_name,
                    "attempted_db": overrides["redis_db"],
                },
            )

        logger.info(
            f"Creating GrpcCache for {service_name} from CommonSettings",
            extra={
                "redis_db": settings.REDIS_DB_GRPC,
                "memory_ttl": cache_config["memory_ttl"],
                "default_ttl": cache_config["default_ttl"],
            },
        )

        return cls(**cache_config)

    def make_cache_key(self, method: str, request: ProtoMessage, **kwargs) -> str:
        """
        gRPC 요청에서 캐시 키 생성

        Args:
            method: gRPC 메서드명 (예: "GetStrategyVersion")
            request: Protobuf request 메시지
            **kwargs: 추가 키 파라미터 (user_id, correlation_id 등)

        Returns:
            캐시 키 (예: "GetStrategyVersion:abc123def456")
        """
        # Request를 JSON으로 직렬화 (deterministic)
        try:
            from google.protobuf.json_format import MessageToJson

            request_json = MessageToJson(request, sort_keys=True)
            params = {"request": request_json, **kwargs}
            params_str = json.dumps(params, sort_keys=True)

        except Exception as e:
            # JSON 변환 실패 시 SerializeToString 사용
            logger.warning(
                f"Failed to convert request to JSON: {e}, using binary serialization"
            )
            request_bytes = request.SerializeToString()
            params_str = f"{request_bytes!r}:{json.dumps(kwargs, sort_keys=True)}"

        # MD5 해시로 키 단축
        hash_suffix = hashlib.md5(params_str.encode()).hexdigest()[:12]
        return f"{method}:{hash_suffix}"

    async def get_with_l1(self, key: str) -> Optional[T]:
        """
        L1 (메모리) → L2 (Redis) 캐시 조회

        Args:
            key: 캐시 키 (make_cache_key() 결과)

        Returns:
            캐시된 값 또는 None
        """
        # L1: In-Memory (5분 TTL)
        if key in self._memory_cache:
            value, timestamp = self._memory_cache[key]
            if time.time() - timestamp < self.memory_ttl:
                if _METRICS_ENABLED:
                    grpc_cache_hits.labels(
                        service=self.service_name,
                        method=key.split(":")[0],
                        layer="L1",
                    ).inc()
                logger.debug(f"L1 cache HIT: {key}")
                return value
            else:
                # TTL 만료
                del self._memory_cache[key]

        # L2: Redis (BaseRedisCache.get 사용)
        value = await super().get(key)
        if value is not None:
            if _METRICS_ENABLED:
                grpc_cache_hits.labels(
                    service=self.service_name, method=key.split(":")[0], layer="L2"
                ).inc()
            logger.debug(f"L2 cache HIT: {key}")

            # L1에 복사 (write-back)
            self._add_to_memory(key, value)
            return value

        # Cache miss
        if _METRICS_ENABLED:
            grpc_cache_misses.labels(
                service=self.service_name, method=key.split(":")[0]
            ).inc()
        logger.debug(f"Cache MISS: {key}")
        return None

    async def set_with_l1(self, key: str, value: T, ttl: Optional[int] = None) -> bool:
        """
        L1 + L2 캐시 동시 저장

        Args:
            key: 캐시 키
            value: 저장할 값 (Protobuf 메시지 또는 일반 객체)
            ttl: Redis TTL (None이면 default_ttl 사용)

        Returns:
            성공 여부
        """
        # L1: In-Memory
        self._add_to_memory(key, value)

        # L2: Redis (BaseRedisCache.set 사용)
        return await super().set(key, value, ttl)

    def _add_to_memory(self, key: str, value: Any):
        """LRU 메모리 캐시 추가"""
        if len(self._memory_cache) >= self.memory_max_size:
            # LRU: 가장 오래된 항목 제거
            oldest_key = min(self._memory_cache.items(), key=lambda x: x[1][1])[0]
            del self._memory_cache[oldest_key]
            logger.debug(f"L1 cache EVICT: {oldest_key}")

        self._memory_cache[key] = (value, time.time())

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        패턴 매칭으로 캐시 무효화 (L1 + L2)

        Args:
            pattern: 키 패턴 (예: "GetStrategy*")

        Returns:
            삭제된 키 개수
        """
        # L1: In-Memory
        import fnmatch

        deleted_l1 = 0
        for key in list(self._memory_cache.keys()):
            if fnmatch.fnmatch(key, pattern):
                del self._memory_cache[key]
                deleted_l1 += 1

        # L2: Redis (SCAN + DEL)
        redis = await self._get_redis()
        if redis is None:
            return deleted_l1

        full_pattern = self._make_key(pattern)
        cursor = 0
        deleted_l2 = 0

        while True:
            cursor, keys = await redis.scan(cursor, match=full_pattern, count=100)
            if keys:
                deleted_l2 += await redis.delete(*keys)
            if cursor == 0:
                break

        logger.info(
            f"Cache invalidated: {pattern} (L1: {deleted_l1}, L2: {deleted_l2})"
        )
        return deleted_l1 + deleted_l2

    def clear_l1(self):
        """L1 메모리 캐시 전체 삭제"""
        count = len(self._memory_cache)
        self._memory_cache.clear()
        logger.info(f"L1 cache cleared: {count} keys")


def grpc_cached(ttl: int = 3600, use_metadata: bool = True):
    """
    gRPC 메서드 캐싱 데코레이터 (BaseRedisCache 기반)

    Example:
        ```python
        class StrategyServiceServicer:
            def __init__(self):
                self.cache = GrpcCache(service_name="strategy-service")

            @grpc_cached(ttl=300, use_metadata=True)
            async def GetStrategyVersion(self, request, context):
                # 캐시 미스 시에만 실행
                version = await db.get_strategy_version(...)
                return version
        ```

    Args:
        ttl: Redis 캐시 TTL (초)
        use_metadata: gRPC 메타데이터 포함 여부 (user_id, correlation_id)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, request, context):
            # servicer에 cache 속성이 없으면 데코레이터 무시
            if not hasattr(self, "cache"):
                logger.warning(
                    f"{func.__name__}: @grpc_cached requires self.cache (GrpcCache)"
                )
                return await func(self, request, context)

            cache: GrpcCache = self.cache

            # 캐시 키 생성
            kwargs = {}
            if use_metadata:
                # gRPC 메타데이터에서 user_id, correlation_id 추출
                try:
                    metadata = dict(context.invocation_metadata())
                    kwargs["user_id"] = metadata.get("user-id")
                    kwargs["correlation_id"] = metadata.get("correlation-id")
                except Exception as e:
                    logger.warning(f"Failed to extract gRPC metadata: {e}")

            cache_key = cache.make_cache_key(
                method=func.__name__, request=request, **kwargs
            )

            # L1 + L2 캐시 조회
            cached = await cache.get_with_l1(cache_key)
            if cached is not None:
                logger.info(
                    f"Cache hit: {func.__name__}",
                    extra={"method": func.__name__, "cache_key": cache_key},
                )
                return cached

            # 실제 메서드 실행 (캐시 미스)
            result = await func(self, request, context)

            # L1 + L2 캐시 저장
            await cache.set_with_l1(cache_key, result, ttl=ttl)
            logger.debug(
                f"Cache set: {func.__name__}",
                extra={"method": func.__name__, "cache_key": cache_key, "ttl": ttl},
            )

            return result

        return wrapper

    return decorator


__all__ = ["GrpcCache", "grpc_cached"]

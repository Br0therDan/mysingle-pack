"""
User Authentication Cache System

Kong Gateway 인증 성능 최적화를 위한 User 객체 캐싱 시스템입니다.
Redis를 우선 사용하고, Redis가 없으면 In-Memory 캐시로 폴백합니다.

Architecture:
- Primary: Redis (다중 인스턴스 간 캐시 공유)
- Fallback: In-Memory TTL Cache (단일 인스턴스)

Cache Strategy:
- Key Pattern: user:{user_id}
- TTL: 5 minutes (300 seconds)
- Invalidation: 명시적 호출 또는 TTL 만료

Usage:
    from mysingle.auth.cache import get_user_cache

    cache = get_user_cache()

    # 캐시에서 조회
    user = await cache.get_user(user_id)

    # 캐시에 저장
    await cache.set_user(user)

    # 캐시 무효화
    await cache.invalidate_user(user_id)
"""

import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Optional

from ..core.logging import get_structured_logger
from .models import User

logger = get_structured_logger(__name__)

# Redis 타입 힌트 (optional)
try:
    from redis.asyncio import Redis
except ImportError:
    Redis = Any  # type: ignore


# =============================================================================
# Base Cache Interface
# =============================================================================


class BaseUserCache(ABC):
    """User 캐시 추상 기본 클래스"""

    default_ttl: int = 300
    key_prefix: str = "user"

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[User]:
        """사용자 조회"""
        pass

    @abstractmethod
    async def set_user(self, user: User, ttl: int | None = None) -> None:
        """사용자 캐시 저장"""
        pass

    @abstractmethod
    async def invalidate_user(self, user_id: str) -> None:
        """사용자 캐시 무효화"""
        pass

    @abstractmethod
    async def clear_all(self) -> None:
        """전체 캐시 삭제"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """캐시 시스템 상태 확인"""
        pass


# =============================================================================
# Redis Cache Implementation
# =============================================================================


class RedisUserCache(BaseUserCache):
    """
    Redis 기반 User 캐시

    다중 서비스 인스턴스 간 캐시를 공유할 수 있습니다.
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        *,
        key_prefix: str = "user",
        default_ttl: int = 300,
    ):
        """
        Redis 캐시 초기화

        Args:
            redis_url: Redis 연결 URL
        """
        self.redis_url = redis_url
        self.redis_client: Optional[Redis] = None  # type: ignore
        self._initialized = False
        self._init_attempted = False
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl

    async def _ensure_initialized(self):
        """Redis 클라이언트 초기화 (lazy initialization)"""
        if self._initialized:
            return True

        if self._init_attempted:
            return False

        self._init_attempted = True

        try:
            import redis.asyncio as redis

            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )

            # 연결 테스트
            if self.redis_client:
                await self.redis_client.ping()
            self._initialized = True
            logger.info("Redis User Cache initialized successfully")
            return True

        except ImportError:
            logger.warning(
                "redis package not installed - falling back to in-memory cache"
            )
            return False
        except Exception as e:
            logger.warning(
                f"Redis connection failed: {e} - falling back to in-memory cache"
            )
            return False

    def _user_cache_key(self, user_id: str) -> str:
        """User 캐시 키 생성"""
        return f"{self.key_prefix}:{user_id}"

    def _serialize_user(self, user: User) -> str:
        """User 객체를 JSON 문자열로 직렬화"""
        user_dict = {
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_superuser": user.is_superuser,
            # 추가 필드는 필요에 따라 확장
        }

        # 선택적 필드 추가
        optional_fields = ["full_name", "first_name", "last_name"]
        for field in optional_fields:
            if hasattr(user, field):
                user_dict[field] = getattr(user, field)

        return json.dumps(user_dict)

    def _deserialize_user(self, data: str) -> User:
        """JSON 문자열을 User 객체로 역직렬화"""
        user_dict = json.loads(data)

        # User 모델 생성 (Beanie Document의 경우 직접 생성 불가능할 수 있음)
        # 여기서는 dict를 User처럼 사용할 수 있는 Proxy 객체 반환
        # 실제 프로덕션에서는 User.parse_obj(user_dict) 또는 from_dict() 메서드 사용
        return User(**user_dict)

    async def get_user(self, user_id: str) -> Optional[User]:
        """Redis에서 사용자 조회"""
        if not await self._ensure_initialized():
            return None

        if self.redis_client is None:
            return None

        try:
            cache_key = self._user_cache_key(user_id)
            data = await self.redis_client.get(cache_key)

            if data:
                logger.debug(f"Redis cache HIT for user_id: {user_id}")
                return self._deserialize_user(data)
            else:
                logger.debug(f"Redis cache MISS for user_id: {user_id}")
                return None

        except Exception as e:
            logger.error(f"Redis get_user error: {e}")
            return None

    async def set_user(self, user: User, ttl: int | None = None) -> None:
        """Redis에 사용자 캐시 저장"""
        if not await self._ensure_initialized():
            return

        if self.redis_client is None:
            return

        try:
            cache_key = self._user_cache_key(str(user.id))
            data = self._serialize_user(user)
            ttl_to_use = ttl if ttl is not None else self.default_ttl
            await self.redis_client.setex(cache_key, ttl_to_use, data)
            logger.debug(f"Redis cache SET for user_id: {user.id}, TTL: {ttl_to_use}s")

        except Exception as e:
            logger.error(f"Redis set_user error: {e}")

    async def invalidate_user(self, user_id: str) -> None:
        """Redis에서 사용자 캐시 무효화"""
        if not await self._ensure_initialized():
            return

        if self.redis_client is None:
            return

        try:
            cache_key = self._user_cache_key(user_id)
            await self.redis_client.delete(cache_key)
            logger.debug(f"Redis cache INVALIDATED for user_id: {user_id}")

        except Exception as e:
            logger.error(f"Redis invalidate_user error: {e}")

    async def clear_all(self) -> None:
        """모든 user 캐시 삭제 (개발/테스트용)"""
        if not await self._ensure_initialized():
            return

        if self.redis_client is None:
            return

        try:
            # user:* 패턴의 모든 키 삭제
            cursor = 0
            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor, match="user:*", count=100
                )
                if keys:
                    await self.redis_client.delete(*keys)
                if cursor == 0:
                    break

            logger.info("Redis cache CLEARED (all user keys)")

        except Exception as e:
            logger.error(f"Redis clear_all error: {e}")

    async def health_check(self) -> bool:
        """Redis 연결 상태 확인"""
        if not await self._ensure_initialized():
            return False

        if self.redis_client is None:
            return False

        try:
            await self.redis_client.ping()
            return True
        except Exception:
            return False


# =============================================================================
# In-Memory Cache Implementation
# =============================================================================


class InMemoryUserCache(BaseUserCache):
    """
    In-Memory TTL 기반 User 캐시

    Redis가 없을 때 폴백으로 사용됩니다.
    단일 프로세스 내에서만 유효합니다.
    """

    def __init__(self, *, key_prefix: str = "user", default_ttl: int = 300):
        """In-Memory 캐시 초기화"""
        self._cache: dict[str, tuple[User, datetime]] = {}
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        logger.info("In-Memory User Cache initialized")

    def _is_expired(self, expiry: datetime) -> bool:
        """캐시 만료 여부 확인"""
        return datetime.utcnow() > expiry

    def _cleanup_expired(self):
        """만료된 캐시 항목 제거 (주기적 실행 필요)"""
        now = datetime.utcnow()
        expired_keys = [key for key, (_, expiry) in self._cache.items() if now > expiry]
        for key in expired_keys:
            del self._cache[key]

    async def get_user(self, user_id: str) -> Optional[User]:
        """In-Memory 캐시에서 사용자 조회"""
        self._cleanup_expired()
        cache_key = f"{self.key_prefix}:{user_id}"
        if cache_key in self._cache:
            user, expiry = self._cache[cache_key]
            if not self._is_expired(expiry):
                logger.debug(f"In-Memory cache HIT for user_id: {user_id}")
                return user
            else:
                # 만료된 항목 삭제
                del self._cache[cache_key]
                logger.debug(f"In-Memory cache EXPIRED for user_id: {user_id}")

        logger.debug(f"In-Memory cache MISS for user_id: {user_id}")
        return None

    async def set_user(self, user: User, ttl: int | None = None) -> None:
        """In-Memory 캐시에 사용자 저장"""
        cache_key = f"{self.key_prefix}:{user.id}"
        ttl_to_use = ttl if ttl is not None else self.default_ttl
        expiry = datetime.utcnow() + timedelta(seconds=ttl_to_use)
        self._cache[cache_key] = (user, expiry)
        logger.debug(f"In-Memory cache SET for user_id: {user.id}, TTL: {ttl_to_use}s")

    async def invalidate_user(self, user_id: str) -> None:
        """In-Memory 캐시에서 사용자 무효화"""
        cache_key = f"{self.key_prefix}:{user_id}"
        if cache_key in self._cache:
            del self._cache[cache_key]
            logger.debug(f"In-Memory cache INVALIDATED for user_id: {user_id}")

    async def clear_all(self) -> None:
        """전체 캐시 삭제"""
        self._cache.clear()
        logger.info("In-Memory cache CLEARED")

    async def health_check(self) -> bool:
        """In-Memory 캐시는 항상 사용 가능"""
        return True


# =============================================================================
# Hybrid Cache (Redis with In-Memory Fallback)
# =============================================================================


class HybridUserCache(BaseUserCache):
    """
    Redis + In-Memory 하이브리드 캐시

    Redis를 우선 사용하고, Redis가 없으면 In-Memory로 폴백합니다.
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        *,
        key_prefix: str = "user",
        default_ttl: int = 300,
    ):
        """
        하이브리드 캐시 초기화

        Args:
            redis_url: Redis 연결 URL (None이면 환경변수 사용)
        """
        # Redis 캐시 (Primary)
        self.redis_cache = RedisUserCache(
            redis_url or "redis://localhost:6379/0",
            key_prefix=key_prefix,
            default_ttl=default_ttl,
        )

        # In-Memory 캐시 (Fallback)
        self.memory_cache = InMemoryUserCache(
            key_prefix=key_prefix, default_ttl=default_ttl
        )

        self._use_redis = True  # Redis 사용 가능 여부
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl

    async def _check_redis_available(self) -> bool:
        """Redis 사용 가능 여부 확인 (캐싱)"""
        if not self._use_redis:
            return False

        is_available = await self.redis_cache.health_check()
        if not is_available and self._use_redis:
            logger.warning("Redis unavailable - falling back to in-memory cache")
            self._use_redis = False

        return is_available

    async def get_user(self, user_id: str) -> Optional[User]:
        """하이브리드 캐시에서 사용자 조회"""
        # Redis 우선 시도
        if await self._check_redis_available():
            user = await self.redis_cache.get_user(user_id)
            if user:
                return user

        # Redis 실패 시 In-Memory 폴백
        return await self.memory_cache.get_user(user_id)

    async def set_user(self, user: User, ttl: int | None = None) -> None:
        """하이브리드 캐시에 사용자 저장"""
        # Redis에 저장 시도
        if await self._check_redis_available():
            await self.redis_cache.set_user(user, ttl)

        # In-Memory에도 저장 (이중 캐싱)
        await self.memory_cache.set_user(user, ttl)

    async def invalidate_user(self, user_id: str) -> None:
        """하이브리드 캐시에서 사용자 무효화"""
        # 양쪽 모두 무효화
        if await self._check_redis_available():
            await self.redis_cache.invalidate_user(user_id)

        await self.memory_cache.invalidate_user(user_id)

    async def clear_all(self) -> None:
        """전체 캐시 삭제"""
        if await self._check_redis_available():
            await self.redis_cache.clear_all()

        await self.memory_cache.clear_all()

    async def health_check(self) -> bool:
        """캐시 시스템 상태 확인"""
        redis_ok = await self.redis_cache.health_check()
        memory_ok = await self.memory_cache.health_check()

        return redis_ok or memory_ok  # 하나라도 사용 가능하면 OK


# =============================================================================
# Cache Factory & Singleton
# =============================================================================

_user_cache_instance: Optional[BaseUserCache] = None


def get_user_cache(redis_url: Optional[str] = None) -> BaseUserCache:
    """
    User 캐시 싱글톤 인스턴스 반환

    Redis URL이 제공되면 Redis 캐시를 사용하고,
    없으면 In-Memory 캐시로 폴백합니다.

    Args:
        redis_url: Redis 연결 URL (선택)

    Returns:
        BaseUserCache: 캐시 인스턴스

    Example:
        cache = get_user_cache()
        user = await cache.get_user(user_id)
    """
    global _user_cache_instance

    if _user_cache_instance is None:
        # 환경설정에서 Redis URL 및 캐시 설정 가져오기
        key_prefix = "user"
        default_ttl = 300
        if redis_url is None:
            try:
                from ..core.config import CommonSettings

                settings = CommonSettings()
                redis_url = getattr(settings, "REDIS_URL", None)
                key_prefix = getattr(settings, "USER_CACHE_KEY_PREFIX", "user")
                default_ttl = getattr(settings, "USER_CACHE_TTL_SECONDS", 300)
            except Exception:
                redis_url = None
        # 하이브리드 캐시 생성 (Redis + In-Memory)
        _user_cache_instance = HybridUserCache(
            redis_url, key_prefix=key_prefix, default_ttl=default_ttl
        )
        logger.info(
            f"User cache singleton initialized (Hybrid: Redis + In-Memory, prefix='{key_prefix}', ttl={default_ttl}s)"
        )

    return _user_cache_instance


def reset_user_cache():
    """
    캐시 싱글톤 리셋 (테스트용)
    """
    global _user_cache_instance
    _user_cache_instance = None
    logger.info("User cache singleton reset")

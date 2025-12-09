"""
User Authentication Cache System

Kong Gateway 인증 성능 최적화를 위한 User 객체 캐싱 시스템입니다.
표준 Redis 인프라를 활용하며, Redis가 없으면 In-Memory 캐시로 폴백합니다.

Architecture:
- Primary: Redis (mysingle.database.redis 활용)
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

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr

from mysingle.auth.models import User
from mysingle.core.config import settings
from mysingle.core.logging import get_structured_logger
from mysingle.database.redis import get_redis_client

logger = get_structured_logger(__name__)


# =============================================================================
# Cached User Model (Lightweight for Cache)
# =============================================================================


class CachedUser(BaseModel):
    """
    캐시 전용 경량 User 모델

    인증/인가에 필요한 최소 필드만 포함하며,
    보안상 hashed_password는 제외합니다.
    """

    id: str
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    full_name: str | None = None

    @classmethod
    def from_user(cls, user: User) -> "CachedUser":
        """User 모델에서 CachedUser 생성"""
        return cls(
            id=str(user.id),
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            full_name=user.full_name,
        )

    def to_user(self) -> User:
        """CachedUser를 User 모델로 변환 (hashed_password는 빈 문자열)"""
        return User(
            id=PydanticObjectId(self.id),
            email=self.email,
            hashed_password="",  # 캐시에서는 사용하지 않음
            is_active=self.is_active,
            is_verified=self.is_verified,
            is_superuser=self.is_superuser,
            full_name=self.full_name,
        )


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
# Redis Cache Implementation (using standard mysingle.database.redis)
# =============================================================================


class RedisUserCache(BaseUserCache):
    """
    Redis 기반 User 캐시

    mysingle.database.redis 표준 인프라를 활용합니다.
    다중 서비스 인스턴스 간 캐시를 공유할 수 있습니다.
    """

    def __init__(
        self,
        *,
        key_prefix: str = "user",
        default_ttl: int = 300,
        redis_db: int = settings.REDIS_DB_USER,
    ):
        """
        Redis 캐시 초기화

        Args:
            key_prefix: 캐시 키 접두사
            default_ttl: 기본 TTL (초)
            redis_db: Redis DB 번호
        """
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self.redis_db = redis_db
        self._redis_client = None

    async def _get_redis(self):
        """Redis 클라이언트 가져오기 (lazy loading)"""
        if self._redis_client is None:
            try:
                self._redis_client = await get_redis_client(db=self.redis_db)
                if self._redis_client:
                    logger.info(f"Redis User Cache initialized (DB {self.redis_db})")
            except Exception as e:
                logger.warning(f"Failed to get Redis client: {e}")
                return None

        return self._redis_client

    def _user_cache_key(self, user_id: str) -> str:
        """User 캐시 키 생성"""
        return f"{self.key_prefix}:{user_id}"

    def _serialize_user(self, user: User) -> str:
        """User 객체를 JSON 문자열로 직렬화 (캐시 전용 경량 모델 사용)"""
        cached_user = CachedUser.from_user(user)
        return cached_user.model_dump_json()

    def _deserialize_user(self, data: str) -> User:
        """JSON 문자열을 User 객체로 역직렬화"""
        cached_user = CachedUser.model_validate_json(data)
        return cached_user.to_user()

    async def get_user(self, user_id: str) -> Optional[User]:
        """Redis에서 사용자 조회"""
        redis = await self._get_redis()
        if redis is None:
            return None

        try:
            cache_key = self._user_cache_key(user_id)
            data = await redis.get(cache_key)

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
        redis = await self._get_redis()
        if redis is None:
            return

        try:
            cache_key = self._user_cache_key(str(user.id))
            data = self._serialize_user(user)
            ttl_to_use = ttl if ttl is not None else self.default_ttl
            await redis.setex(cache_key, ttl_to_use, data)
            logger.debug(f"Redis cache SET for user_id: {user.id}, TTL: {ttl_to_use}s")

        except Exception as e:
            logger.error(f"Redis set_user error: {e}")

    async def invalidate_user(self, user_id: str) -> None:
        """Redis에서 사용자 캐시 무효화"""
        redis = await self._get_redis()
        if redis is None:
            return

        try:
            cache_key = self._user_cache_key(user_id)
            await redis.delete(cache_key)
            logger.debug(f"Redis cache INVALIDATED for user_id: {user_id}")

        except Exception as e:
            logger.error(f"Redis invalidate_user error: {e}")

    async def clear_all(self) -> None:
        """모든 user 캐시 삭제 (개발/테스트용)"""
        redis = await self._get_redis()
        if redis is None:
            return

        try:
            # user:* 패턴의 모든 키 삭제
            cursor = 0
            while True:
                cursor, keys = await redis.scan(
                    cursor, match=f"{self.key_prefix}:*", count=100
                )
                if keys:
                    await redis.delete(*keys)
                if cursor == 0:
                    break

            logger.info("Redis cache CLEARED (all user keys)")

        except Exception as e:
            logger.error(f"Redis clear_all error: {e}")

    async def health_check(self) -> bool:
        """Redis 연결 상태 확인"""
        redis = await self._get_redis()
        if redis is None:
            return False

        try:
            ping_result = await redis.ping()  # type: ignore[misc]
            return bool(ping_result)
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

    표준 Redis 인프라를 우선 사용하고, Redis가 없으면 In-Memory로 폴백합니다.
    """

    def __init__(
        self,
        *,
        key_prefix: str = "user",
        default_ttl: int = 300,
        redis_db: int = 0,
    ):
        """
        하이브리드 캐시 초기화

        Args:
            key_prefix: 캐시 키 접두사
            default_ttl: 기본 TTL (초)
            redis_db: Redis DB 번호
        """
        # Redis 캐시 (Primary)
        self.redis_cache = RedisUserCache(
            key_prefix=key_prefix,
            default_ttl=default_ttl,
            redis_db=redis_db,
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


def get_user_cache() -> BaseUserCache:
    """
    User 캐시 싱글톤 인스턴스 반환

    표준 Redis 인프라를 활용하며, Redis가 없으면 In-Memory 캐시로 폴백합니다.

    Returns:
        BaseUserCache: 캐시 인스턴스

    Example:
        cache = get_user_cache()
        user = await cache.get_user(user_id)
    """
    global _user_cache_instance

    if _user_cache_instance is None:
        # 환경설정에서 캐시 설정 가져오기
        key_prefix = "user"
        default_ttl = 300
        redis_db = 0

        try:
            from mysingle.core.config import settings

            key_prefix = getattr(settings, "USER_CACHE_KEY_PREFIX", "user")
            default_ttl = getattr(settings, "USER_CACHE_TTL_SECONDS", 300)
            redis_db = getattr(settings, "REDIS_DB_USER", 0)
        except Exception as e:
            logger.warning(f"Failed to load cache settings: {e}, using defaults")

        # 하이브리드 캐시 생성 (Redis + In-Memory)
        _user_cache_instance = HybridUserCache(
            key_prefix=key_prefix,
            default_ttl=default_ttl,
            redis_db=redis_db,
        )
        logger.info(
            f"User cache singleton initialized (Hybrid: Redis DB {redis_db} + In-Memory, prefix='{key_prefix}', ttl={default_ttl}s)"
        )

    return _user_cache_instance


def reset_user_cache():
    """
    캐시 싱글톤 리셋 (테스트용)
    """
    global _user_cache_instance
    _user_cache_instance = None
    logger.info("User cache singleton reset")

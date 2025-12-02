"""
Redis Client Management for MySingle Services

표준화된 Redis 클라이언트 및 연결 풀 관리를 제공합니다.
서비스 간 캐시 공유와 고성능 데이터 저장을 지원합니다.

Architecture:
- Connection Pooling: 효율적인 연결 관리
- Lazy Initialization: 필요시에만 연결
- Health Checks: 연결 상태 모니터링
- Multi-DB Support: 용도별 DB 분리

Usage:
    # User 인증 캐시 (DB 0)
    from mysingle.database.redis import get_redis_client

    redis = await get_redis_client(db=0)
    await redis.set("user:123", user_data, ex=300)

    # 마켓 데이터 캐시 (DB 1)
    market_redis = await get_redis_client(db=1)
    await market_redis.set("ticker:AAPL", price_data, ex=60)

    # 인디케이터 캐시 (DB 2)
    indicator_redis = await get_redis_client(db=2)
    await indicator_redis.set("indicator:RSI:AAPL", rsi_data, ex=120)
"""

from typing import Any, Optional

from mysingle.core.logging import get_structured_logger

logger = get_structured_logger(__name__)

# Redis 타입 힌트
try:
    from redis.asyncio import ConnectionPool, Redis
except ImportError:
    Redis = Any  # type: ignore
    ConnectionPool = Any  # type: ignore


class RedisConfig:
    """Redis 연결 설정"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        username: Optional[str] = None,
        *,
        max_connections: int = 50,
        socket_timeout: float = 5.0,
        socket_connect_timeout: float = 5.0,
        socket_keepalive: bool = True,
        health_check_interval: int = 30,
        retry_on_timeout: bool = True,
        decode_responses: bool = True,
        encoding: str = "utf-8",
    ):
        """
        Redis 연결 설정 초기화

        Args:
            host: Redis 호스트
            port: Redis 포트
            db: Redis DB 번호 (0-15)
            password: Redis 비밀번호
            username: Redis 사용자명 (Redis 6.0+)
            max_connections: 최대 연결 수
            socket_timeout: 소켓 타임아웃 (초)
            socket_connect_timeout: 연결 타임아웃 (초)
            socket_keepalive: TCP keepalive 사용 여부
            health_check_interval: 헬스체크 간격 (초)
            retry_on_timeout: 타임아웃시 재시도 여부
            decode_responses: 자동 디코딩 여부
            encoding: 문자열 인코딩
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.username = username
        self.max_connections = max_connections
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.socket_keepalive = socket_keepalive
        self.health_check_interval = health_check_interval
        self.retry_on_timeout = retry_on_timeout
        self.decode_responses = decode_responses
        self.encoding = encoding

    @classmethod
    def from_url(cls, url: str, **kwargs) -> "RedisConfig":
        """
        Redis URL에서 설정 생성

        Args:
            url: redis://[:password]@host:port/db 형식
            **kwargs: 추가 설정

        Returns:
            RedisConfig 인스턴스
        """
        import re

        # URL 파싱: redis://[username:password@]host:port/db
        pattern = r"redis://(?:([^:]+):([^@]+)@)?([^:]+):(\d+)/(\d+)"
        match = re.match(pattern, url)

        if not match:
            raise ValueError(f"Invalid Redis URL format: {url}")

        username, password, host, port, db = match.groups()

        return cls(
            host=host,
            port=int(port),
            db=int(db),
            password=password,
            username=username,
            **kwargs,
        )

    def to_connection_kwargs(self) -> dict[str, Any]:
        """Redis 클라이언트 연결 인자로 변환"""
        kwargs = {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "password": self.password,
            "username": self.username,
            "max_connections": self.max_connections,
            "socket_timeout": self.socket_timeout,
            "socket_connect_timeout": self.socket_connect_timeout,
            "socket_keepalive": self.socket_keepalive,
            "health_check_interval": self.health_check_interval,
            "retry_on_timeout": self.retry_on_timeout,
            "decode_responses": self.decode_responses,
            "encoding": self.encoding,
        }

        # None 값 제거
        return {k: v for k, v in kwargs.items() if v is not None}


class RedisClientManager:
    """
    Redis 클라이언트 관리자

    연결 풀을 관리하고 DB별 클라이언트 인스턴스를 제공합니다.
    """

    def __init__(self, config: RedisConfig):
        """
        Args:
            config: Redis 연결 설정
        """
        self.config = config
        self._pool: Optional[ConnectionPool] = None  # type: ignore
        self._clients: dict[int, Redis] = {}  # type: ignore
        self._initialized = False
        self._init_attempted = False

    async def _ensure_initialized(self) -> bool:
        """Redis 연결 풀 초기화 (lazy initialization)"""
        if self._initialized:
            return True

        if self._init_attempted:
            return False

        self._init_attempted = True

        try:
            import redis.asyncio as redis

            # 연결 풀 생성
            conn_kwargs = self.config.to_connection_kwargs()
            self._pool = redis.ConnectionPool(**conn_kwargs)

            # 연결 테스트
            test_client = redis.Redis(connection_pool=self._pool)
            ping_result = await test_client.ping()  # type: ignore[misc]
            if not ping_result:
                raise ConnectionError("Redis ping failed")
            await test_client.aclose()

            self._initialized = True
            logger.info(
                f"Redis connection pool initialized: {self.config.host}:{self.config.port}"
            )
            return True

        except ImportError:
            logger.error("redis package not installed - run: pip install redis")
            return False
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            return False

    async def get_client(self, db: Optional[int] = None) -> Optional[Redis]:  # type: ignore
        """
        Redis 클라이언트 반환

        Args:
            db: DB 번호 (None이면 설정의 기본 DB 사용)

        Returns:
            Redis 클라이언트 또는 None (연결 실패시)
        """
        if not await self._ensure_initialized():
            return None

        if self._pool is None:
            return None

        db_num = db if db is not None else self.config.db

        # 이미 생성된 클라이언트 재사용
        if db_num in self._clients:
            return self._clients[db_num]

        # 새 클라이언트 생성
        try:
            import redis.asyncio as redis

            client = redis.Redis(connection_pool=self._pool, db=db_num)
            self._clients[db_num] = client
            logger.debug(f"Redis client created for DB {db_num}")
            return client

        except Exception as e:
            logger.error(f"Failed to create Redis client for DB {db_num}: {e}")
            return None

    async def health_check(self, db: Optional[int] = None) -> bool:
        """
        Redis 연결 상태 확인

        Args:
            db: DB 번호 (None이면 기본 DB)

        Returns:
            연결 성공 여부
        """
        client = await self.get_client(db)
        if client is None:
            return False

        try:
            ping_result = await client.ping()  # type: ignore[misc]
            return bool(ping_result)
        except Exception as e:
            logger.error(
                f"Redis health check failed for DB {db or self.config.db}: {e}"
            )
            return False

    async def close(self):
        """모든 Redis 연결 종료"""
        for db_num, client in self._clients.items():
            try:
                await client.aclose()
                logger.debug(f"Redis client closed for DB {db_num}")
            except Exception as e:
                logger.error(f"Error closing Redis client for DB {db_num}: {e}")

        self._clients.clear()

        if self._pool:
            try:
                await self._pool.aclose()  # type: ignore
                logger.info("Redis connection pool closed")
            except Exception as e:
                logger.error(f"Error closing Redis pool: {e}")

        self._initialized = False
        self._init_attempted = False

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        await self._ensure_initialized()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.close()


# =============================================================================
# Global Redis Client Manager
# =============================================================================

_global_redis_manager: Optional[RedisClientManager] = None


def _get_redis_config_from_settings() -> RedisConfig:
    """CommonSettings에서 Redis 설정 가져오기"""
    try:
        from mysingle.core.config import settings

        # URL 파싱 또는 개별 설정 사용
        redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        redis_password = getattr(settings, "REDIS_PASSWORD", None)

        # URL에 비밀번호가 없고 설정에 있으면 추가
        if ":" not in redis_url.split("//")[1].split("@")[0] and redis_password:
            # redis://host:port/db -> redis://:password@host:port/db
            parts = redis_url.split("//")
            parts[1] = f":{redis_password}@{parts[1]}"
            redis_url = "//".join(parts)

        config = RedisConfig.from_url(redis_url)

        logger.info(
            f"Redis config loaded from settings: {config.host}:{config.port}/{config.db}"
        )
        return config

    except Exception as e:
        logger.warning(
            f"Failed to load Redis config from settings: {e}, using defaults"
        )
        return RedisConfig()


async def get_redis_client(db: Optional[int] = None) -> Optional[Redis]:  # type: ignore
    """
    글로벌 Redis 클라이언트 반환

    Args:
        db: DB 번호 (None이면 설정의 기본 DB 사용)

    Returns:
        Redis 클라이언트 또는 None

    Example:
        # User 캐시 (DB 0)
        redis = await get_redis_client(db=0)
        await redis.set("user:123", user_data, ex=300)

        # Market data 캐시 (DB 1)
        market_redis = await get_redis_client(db=1)
        await market_redis.set("ticker:AAPL", price_data)
    """
    global _global_redis_manager

    if _global_redis_manager is None:
        config = _get_redis_config_from_settings()
        _global_redis_manager = RedisClientManager(config)
        logger.info("Global Redis manager initialized")

    return await _global_redis_manager.get_client(db)


async def get_redis_manager() -> RedisClientManager:
    """
    글로벌 Redis 매니저 반환

    Returns:
        RedisClientManager 인스턴스

    Example:
        manager = await get_redis_manager()
        is_healthy = await manager.health_check(db=0)
    """
    global _global_redis_manager

    if _global_redis_manager is None:
        config = _get_redis_config_from_settings()
        _global_redis_manager = RedisClientManager(config)
        logger.info("Global Redis manager initialized")

    return _global_redis_manager


def reset_redis_manager():
    """
    글로벌 Redis 매니저 리셋 (테스트용)

    Warning:
        이 함수는 테스트 목적으로만 사용해야 합니다.
        프로덕션 환경에서는 사용하지 마세요.
    """
    global _global_redis_manager
    _global_redis_manager = None
    logger.warning("Global Redis manager reset (test mode)")

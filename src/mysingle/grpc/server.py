"""
gRPC Server Base Class

모든 마이크로서비스의 gRPC 서버를 위한 추상 기본 클래스입니다.
BaseGrpcServer를 상속받아 register_servicers() 메서드만 구현하면
표준화된 서버 초기화, Interceptor 체인, 리소스 관리가 자동으로 제공됩니다.

Features:
- Pydantic 기반 설정 스키마
- 표준 Interceptor 체인 (Metrics, Auth, RateLimit, Metadata, Logging, Error)
- Graceful shutdown
- Health check integration
- Service Factory 통합 (MongoDB, Redis connection pooling)

Usage:
    ```python
    from mysingle.grpc.server import BaseGrpcServer, GrpcServerConfig

    class MyGrpcServer(BaseGrpcServer):
        def register_servicers(self, server):
            my_service_pb2_grpc.add_MyServiceServicer_to_server(
                MyServiceServicer(), server
            )

    # 서버 시작
    config = GrpcServerConfig(
        service_name="my-service",
        port=50051,
        enable_reflection=True,  # 개발 환경
    )
    grpc_server = MyGrpcServer(config)
    await grpc_server.start()
    ```
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

import grpc
from pydantic import BaseModel, Field

from mysingle.core.logging import get_structured_logger
from mysingle.grpc.interceptors import (
    AuthInterceptor,
    ErrorHandlingInterceptor,
    LoggingInterceptor,
    MetadataInterceptor,
    MetricsInterceptor,
    RateLimiterInterceptor,
)

if TYPE_CHECKING:
    from mysingle.core.config import CommonSettings

logger = get_structured_logger(__name__)


class GrpcServerConfig(BaseModel):
    """
    gRPC 서버 설정 스키마

    CommonSettings의 GRPC_* 환경변수를 기본값으로 사용합니다.
    서비스별 커스터마이징이 필요한 경우 파라미터로 오버라이드 가능합니다.

    Example:
        ```python
        from mysingle.core.config import settings
        from mysingle.grpc import GrpcServerConfig

        # CommonSettings 기반 자동 구성
        config = GrpcServerConfig.from_settings(
            settings=settings,
            service_name="strategy-service",
            port=50051,  # 서비스별 포트만 지정
        )
        ```
    """

    # Basic settings
    service_name: str = Field(..., description="서비스 이름 (예: strategy-service)")
    port: int = Field(..., description="gRPC 서버 포트")
    max_workers: int = Field(default=10, description="Thread pool 크기")

    # Interceptor settings
    enable_auth: bool = Field(default=True, description="인증 활성화")
    enable_rate_limiting: bool = Field(default=True, description="Rate limiting 활성화")
    enable_metrics: bool = Field(default=True, description="메트릭 수집 활성화")
    enable_error_handling: bool = Field(default=True, description="에러 핸들링 활성화")

    # Rate limiting
    rate_limit_max_requests: int = Field(
        default=1000, description="Rate limit 최대 요청 수"
    )
    rate_limit_window_seconds: int = Field(
        default=60, description="Rate limit 윈도우 (초)"
    )

    # gRPC options
    keepalive_time_ms: int = Field(default=30000, description="Keepalive time (ms)")
    keepalive_timeout_ms: int = Field(
        default=10000, description="Keepalive timeout (ms)"
    )
    max_concurrent_streams: int = Field(default=100, description="최대 동시 스트림")
    max_message_length: int = Field(
        default=10 * 1024 * 1024, description="최대 메시지 크기 (10MB)"
    )

    # Reflection (개발 환경)
    enable_reflection: bool = Field(
        default=False, description="gRPC reflection 활성화 (grpcurl)"
    )
    reflection_service_names: list[str] = Field(
        default_factory=list, description="Reflection 서비스 이름"
    )

    # Exempt methods (인증 면제)
    auth_exempt_methods: list[str] = Field(
        default_factory=list, description="인증 면제 메서드 (예: ['/health/Check'])"
    )

    @classmethod
    def from_settings(
        cls,
        settings: CommonSettings,
        service_name: str,
        port: Optional[int] = None,
        **overrides,
    ) -> GrpcServerConfig:
        """
        CommonSettings에서 gRPC 설정을 가져와 GrpcServerConfig 생성

        Args:
            settings: CommonSettings 인스턴스
            service_name: 서비스 이름
            port: gRPC 포트 (None이면 settings.GRPC_SERVER_PORT 사용)
            **overrides: 추가 오버라이드 설정

        Returns:
            GrpcServerConfig 인스턴스

        Example:
            ```python
            from mysingle.core.config import settings

            config = GrpcServerConfig.from_settings(
                settings=settings,
                service_name="strategy-service",
                port=50051,
                enable_reflection=True,  # 개발 환경에서만
            )
            ```
        """
        # CommonSettings에서 기본값 추출
        config_dict = {
            "service_name": service_name,
            "port": port or settings.GRPC_SERVER_PORT,
            "max_workers": settings.GRPC_SERVER_MAX_WORKERS,
            "enable_auth": settings.GRPC_ENABLE_AUTH,
            "enable_rate_limiting": settings.GRPC_ENABLE_RATE_LIMITING,
            "enable_metrics": settings.GRPC_ENABLE_METRICS,
            "enable_error_handling": settings.GRPC_ENABLE_ERROR_HANDLING,
            "rate_limit_max_requests": settings.GRPC_RATE_LIMIT_MAX_REQUESTS,
            "rate_limit_window_seconds": settings.GRPC_RATE_LIMIT_WINDOW_SECONDS,
            "keepalive_time_ms": settings.GRPC_KEEPALIVE_TIME_MS,
            "keepalive_timeout_ms": settings.GRPC_KEEPALIVE_TIMEOUT_MS,
            "max_concurrent_streams": settings.GRPC_MAX_CONCURRENT_STREAMS,
            "max_message_length": settings.GRPC_MAX_MESSAGE_LENGTH,
            "enable_reflection": settings.GRPC_SERVER_ENABLE_REFLECTION,
        }

        # 오버라이드 적용
        config_dict.update(overrides)

        logger.info(
            f"Creating GrpcServerConfig for {service_name} from CommonSettings",
            extra={
                "port": config_dict["port"],
                "enable_auth": config_dict["enable_auth"],
            },
        )

        return cls(**config_dict)

    class Config:
        use_enum_values = True


class BaseGrpcServer(ABC):
    """
    gRPC 서버 기본 클래스.

    모든 마이크로서비스의 gRPC 서버는 이 클래스를 상속받아 구현합니다.

    Example:
        ```python
        from mysingle.core.config import settings
        from mysingle.grpc import BaseGrpcServer, GrpcServerConfig

        class StrategyGrpcServer(BaseGrpcServer):
            def register_servicers(self, server):
                strategy_service_pb2_grpc.add_StrategyServiceServicer_to_server(
                    StrategyServiceServicer(), server
                )

            async def before_start(self):
                # DB 연결 등 초기화
                await super().before_start()
                self.db = await get_database()

            async def after_stop(self):
                # 리소스 정리
                await self.db.close()
                await super().after_stop()

        # CommonSettings 기반 자동 구성
        config = GrpcServerConfig.from_settings(
            settings=settings,
            service_name="strategy-service",
            port=50051,
        )
        grpc_server = StrategyGrpcServer(config)
        await grpc_server.start()
        ```
    """

    def __init__(self, config: GrpcServerConfig):
        """
        Args:
            config: GrpcServerConfig 인스턴스 (GrpcServerConfig.from_settings() 권장)
        """
        self.config = config
        self.server: Optional[grpc.aio.Server] = None
        self._running = False

        logger.info(
            f"Initializing gRPC server: {config.service_name} on port {config.port}"
        )

    def _build_interceptor_chain(self) -> list[grpc.aio.ServerInterceptor]:
        """
        표준 Interceptor 체인 구성

        순서:
        1. MetricsInterceptor (성능 측정)
        2. AuthInterceptor (user_id 검증)
        3. RateLimiterInterceptor (요청 제한)
        4. MetadataInterceptor (correlation_id 자동 생성)
        5. LoggingInterceptor (구조화 로깅)
        6. ErrorHandlingInterceptor (에러 변환)

        Returns:
            Interceptor 리스트
        """
        interceptors = []

        # 1. Metrics (가장 먼저 실행)
        if self.config.enable_metrics:
            interceptors.append(
                MetricsInterceptor(service_name=self.config.service_name)
            )

        # 2. Auth
        if self.config.enable_auth:
            interceptors.append(
                AuthInterceptor(
                    require_auth=True,
                    exempt_methods=self.config.auth_exempt_methods,
                )
            )

        # 3. Rate Limiting
        if self.config.enable_rate_limiting:
            interceptors.append(
                RateLimiterInterceptor(
                    max_requests=self.config.rate_limit_max_requests,
                    window_seconds=self.config.rate_limit_window_seconds,
                )
            )

        # 4. Metadata (correlation_id 자동 생성)
        interceptors.append(MetadataInterceptor(auto_generate=True))

        # 5. Logging
        interceptors.append(LoggingInterceptor())

        # 6. Error Handling (가장 마지막)
        if self.config.enable_error_handling:
            interceptors.append(ErrorHandlingInterceptor())

        logger.info(
            f"Interceptor chain configured: {[type(i).__name__ for i in interceptors]}"
        )
        return interceptors

    def _build_server_options(self) -> list[tuple[str, Any]]:
        """
        gRPC 서버 옵션 구성

        Returns:
            gRPC 옵션 리스트
        """
        return [
            ("grpc.max_send_message_length", self.config.max_message_length),
            ("grpc.max_receive_message_length", self.config.max_message_length),
            ("grpc.keepalive_time_ms", self.config.keepalive_time_ms),
            ("grpc.keepalive_timeout_ms", self.config.keepalive_timeout_ms),
            (
                "grpc.http2.max_pings_without_data",
                0,
            ),  # keepalive 핑 제한 없음
            ("grpc.http2.min_time_between_pings_ms", 10000),
            ("grpc.http2.min_ping_interval_without_data_ms", 5000),
            ("grpc.max_concurrent_streams", self.config.max_concurrent_streams),
        ]

    @abstractmethod
    def register_servicers(self, server: grpc.aio.Server):
        """
        서비스별 Servicer 등록 (추상 메서드)

        서브클래스에서 반드시 구현해야 합니다.

        Args:
            server: gRPC 서버 인스턴스

        Example:
            ```python
            def register_servicers(self, server):
                strategy_service_pb2_grpc.add_StrategyServiceServicer_to_server(
                    StrategyServiceServicer(), server
                )
            ```
        """
        pass

    async def before_start(self):
        """
        서버 시작 전 훅 (선택적 오버라이드)

        데이터베이스 연결, 캐시 초기화 등 사전 작업 수행

        Example:
            ```python
            async def before_start(self):
                await super().before_start()
                self.db = await get_database()
                self.cache = GrpcCache(service_name=self.config.service_name)
            ```
        """
        logger.info(f"{self.config.service_name}: before_start hook")

    async def after_start(self):
        """
        서버 시작 후 훅 (선택적 오버라이드)

        Example:
            ```python
            async def after_start(self):
                await super().after_start()
                logger.info("gRPC server is ready to accept requests")
            ```
        """
        logger.info(
            f"{self.config.service_name}: gRPC server started on port {self.config.port}"
        )

    async def before_stop(self):
        """
        서버 종료 전 훅 (선택적 오버라이드)

        진행 중인 요청 완료 대기 등
        """
        logger.info(f"{self.config.service_name}: before_stop hook")

    async def after_stop(self):
        """
        서버 종료 후 훅 (선택적 오버라이드)

        리소스 정리 (DB 연결 종료 등)

        Example:
            ```python
            async def after_stop(self):
                await self.db.close()
                await super().after_stop()
            ```
        """
        logger.info(f"{self.config.service_name}: gRPC server stopped")

    async def start(self):
        """
        gRPC 서버 시작

        1. before_start() 훅 실행
        2. Interceptor 체인 구성
        3. 서버 생성 및 servicer 등록
        4. Reflection 활성화 (개발 환경)
        5. 포트 바인딩 및 시작
        6. after_start() 훅 실행
        """
        if self._running:
            logger.warning(f"{self.config.service_name}: Server already running")
            return

        try:
            # 1. before_start hook
            await self.before_start()

            # 2. Interceptor chain
            interceptors = self._build_interceptor_chain()

            # 3. gRPC 서버 생성
            self.server = grpc.aio.server(
                interceptors=interceptors,
                options=self._build_server_options(),
            )

            # 4. Servicer 등록
            self.register_servicers(self.server)

            # 5. Reflection 활성화 (개발 환경)
            if self.config.enable_reflection:
                from grpc_reflection.v1alpha import reflection

                service_names = self.config.reflection_service_names or []
                reflection.enable_server_reflection(service_names, self.server)
                logger.info(f"gRPC reflection enabled for services: {service_names}")

            # 6. 포트 바인딩
            address = f"[::]:{self.config.port}"
            self.server.add_insecure_port(address)

            # 7. 서버 시작
            await self.server.start()
            self._running = True

            # 8. after_start hook
            await self.after_start()

            logger.info(
                f"✅ {self.config.service_name} gRPC server listening on {address}"
            )

        except Exception as e:
            logger.error(
                f"Failed to start gRPC server: {e}",
                exc_info=True,
            )
            raise

    async def stop(self, grace_period: int = 5):
        """
        gRPC 서버 정상 종료 (Graceful Shutdown)

        Args:
            grace_period: 진행 중인 요청 완료 대기 시간 (초)
        """
        if not self._running or self.server is None:
            logger.warning(f"{self.config.service_name}: Server not running")
            return

        try:
            logger.info(f"Shutting down gRPC server (grace period: {grace_period}s)...")

            # 1. before_stop hook
            await self.before_stop()

            # 2. Graceful shutdown
            await self.server.stop(grace_period)
            self._running = False

            # 3. after_stop hook
            await self.after_stop()

            logger.info(f"✅ {self.config.service_name} gRPC server stopped")

        except Exception as e:
            logger.error(
                f"Error during gRPC server shutdown: {e}",
                exc_info=True,
            )
            raise

    async def wait_for_termination(self):
        """서버 종료 대기 (블로킹)"""
        if self.server:
            await self.server.wait_for_termination()

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.stop()

"""
Base gRPC Client

모든 마이크로서비스 gRPC 클라이언트의 베이스 클래스
공통 기능: 채널 관리, 메타데이터 주입, 컨텍스트 매니저, 환경별 연결 설정

Note:
    - 이 클라이언트는 gRPC 연결 관리만 담당합니다.
    - 응답 캐싱이 필요한 경우 `mysingle.grpc.cache.GrpcCache`를 별도로 사용하세요.
    - GrpcCache는 Redis DB 1 (REDIS_DB_GRPC)을 사용하여 응답을 캐싱합니다.

Usage:
    ```python
    from mysingle.clients import BaseGrpcClient
    from app.grpc import my_service_pb2_grpc

    class MyServiceGrpcClient(BaseGrpcClient):
        def __init__(
            self,
            user_id: str | None = None,
            correlation_id: str | None = None,
            **kwargs,
        ):
            super().__init__(
                service_name="my-service",
                default_port=50051,
                user_id=user_id,
                correlation_id=correlation_id,
                **kwargs,
            )
            self.stub = my_service_pb2_grpc.MyServiceStub(self.channel)

        async def get_data(self, request_id: str):
            request = my_service_pb2.GetDataRequest(id=request_id)
            response = await self.stub.GetData(request, metadata=self.metadata)
            return response

    # 사용 1: 컨텍스트 매니저
    async with MyServiceGrpcClient(user_id="user123") as client:
        data = await client.get_data("req_id")

    # 사용 2: 수동 연결 관리
    client = MyServiceGrpcClient(user_id="user123")
    try:
        data = await client.get_data("req_id")
    finally:
        await client.close()

    # 사용 3: 캐싱과 함께 사용 (선택적)
    from mysingle.grpc.cache import GrpcCache

    cache = GrpcCache(service_name="my-service")
    cache_key = "get_data:req_id"

    # 캐시 확인
    cached = await cache.get(cache_key)
    if cached:
        return cached

    # 캐시 미스 시 gRPC 호출
    async with MyServiceGrpcClient(user_id="user123") as client:
        data = await client.get_data("req_id")
        await cache.set(cache_key, data, ttl=3600)
        return data
    ```
"""

from __future__ import annotations

import os
import uuid
from typing import TYPE_CHECKING, Any

import grpc

from mysingle.constants import (
    GRPC_METADATA_CORRELATION_ID,
    GRPC_METADATA_REQUEST_ID,
    GRPC_METADATA_USER_ID,
)
from mysingle.core.logging import get_logger

if TYPE_CHECKING:
    from fastapi import Request

logger = get_logger(__name__)


class BaseGrpcClient:
    """
    마이크로서비스 gRPC 클라이언트 베이스 클래스

    Features:
        - 자동 채널 관리 (secure/insecure)
        - 메타데이터 자동 주입 (user_id, correlation_id, request_id)
        - 비동기 컨텍스트 매니저 지원
        - 환경별 연결 설정 (Docker 내부 vs 외부)
        - Keepalive 및 연결 옵션 표준화

    Metadata Headers:
        - user-id: 사용자 식별자 (필수, 서버 인터셉터에서 검증)
        - correlation-id: 요청 추적 ID (자동 생성 또는 전파)
        - request-id: 개별 요청 ID (항상 자동 생성)

    Environment Variables:
        - {SERVICE}_GRPC_HOST: 서비스별 호스트 오버라이드
          예) INDICATOR_HOST=indicator-service
        - GRPC_USE_TLS: TLS 사용 여부 (기본값: false)
    """

    def __init__(
        self,
        service_name: str,
        default_port: int,
        host: str | None = None,
        user_id: str | None = None,
        correlation_id: str | None = None,
        request: "Request | None" = None,
        timeout: float = 10.0,
        use_tls: bool | None = None,
        **kwargs: Any,
    ):
        """
        Args:
            service_name: 서비스 이름 (예: "indicator-service", "market-data-service")
            default_port: gRPC 포트 (예: 50052, 50053)
            host: 명시적 호스트 (없으면 자동 결정)
            user_id: 사용자 ID (request가 주어지면 자동 추출)
            correlation_id: 상관관계 ID (없으면 자동 생성)
            request: FastAPI Request 객체 (메타데이터 자동 추출)
            timeout: 요청 타임아웃 (초)
            use_tls: TLS 사용 여부 (None이면 환경변수 기반)
            **kwargs: grpc.aio.Channel 추가 옵션

        Note:
            - request 객체가 제공되면 user_id와 correlation_id를 헤더에서 추출합니다.
            - user_id가 없으면 서버 AuthInterceptor에서 UNAUTHENTICATED 오류가 발생합니다.
        """
        self.service_name = service_name
        self.default_port = default_port
        self.timeout = timeout

        # User ID 결정: 명시적 user_id > request 헤더
        if user_id:
            self.user_id: str = user_id
        elif request:
            self.user_id = self._extract_user_id_from_request(request)
        else:
            self.user_id = ""

        # Correlation ID 결정: 명시적 correlation_id > request 헤더 > 자동 생성
        if correlation_id:
            self.correlation_id: str = correlation_id
        elif request:
            extracted_cid = self._extract_correlation_id_from_request(request)
            self.correlation_id = extracted_cid if extracted_cid else str(uuid.uuid4())
        else:
            self.correlation_id = str(uuid.uuid4())

        # 호스트 결정
        if host is None:
            host = self._determine_host()

        self.host = host

        # 포트 결정 (환경변수 우선)
        port = self._determine_port()

        self.address = f"{host}:{port}"

        # TLS 설정 결정
        if use_tls is None:
            use_tls = os.getenv("GRPC_USE_TLS", "false").lower() == "true"

        self.use_tls = use_tls

        # 채널 생성
        self.channel = self._create_channel(**kwargs)

        logger.info(
            "gRPC client initialized",
            client_class=self.__class__.__name__,
            service_name=self.service_name,
            address=self.address,
            tls=self.use_tls,
            timeout=timeout,
            user_id=self.user_id,
            correlation_id=self.correlation_id,
        )

    @staticmethod
    def _extract_user_id_from_request(request: "Request") -> str:
        """
        FastAPI Request 객체에서 User ID 추출

        Kong Gateway 헤더 우선순위:
        1. X-User-Id (Kong pre-function이 JWT sub claim에서 추출)
        2. request.state.user.id (AuthMiddleware가 주입한 User 객체)

        Note: X-Consumer-Custom-ID는 Kong Consumer 이름이므로 사용하지 않음

        Args:
            request: FastAPI Request 객체

        Returns:
            추출된 User ID (없으면 빈 문자열)
        """
        from mysingle.constants import HEADER_USER_ID

        # 우선순위 1: X-User-Id (Kong pre-function에서 JWT sub claim 추출)
        user_id = request.headers.get(HEADER_USER_ID, "")
        if user_id:
            return user_id.strip()

        # 우선순위 2: request.state.user (AuthMiddleware)
        try:
            user = getattr(request.state, "user", None)
            if user and hasattr(user, "id"):
                return str(user.id)
        except Exception as e:
            logger.debug(f"Failed to extract user from request.state: {e}")

        logger.warning(
            "User ID not found in request headers or state",
            headers=dict(request.headers),
            has_state_user=hasattr(request.state, "user"),
        )
        return ""

    @staticmethod
    def _extract_correlation_id_from_request(request: "Request") -> str | None:
        """
        FastAPI Request 객체에서 Correlation ID 추출

        Kong Gateway 헤더 우선순위:
        1. X-Correlation-Id (표준)
        2. Correlation-Id (대체)

        Args:
            request: FastAPI Request 객체

        Returns:
            추출된 Correlation ID (없으면 None)
        """
        from mysingle.constants import HEADER_CORRELATION_ID

        # 우선순위 1: X-Correlation-Id (표준)
        correlation_id = request.headers.get(HEADER_CORRELATION_ID)
        if correlation_id:
            return correlation_id.strip()

        # 우선순위 2: Correlation-Id (대체)
        alt_correlation_id = request.headers.get("Correlation-Id")
        if alt_correlation_id:
            return alt_correlation_id.strip()

        return None

    def _determine_host(self) -> str:
        """
        환경 기반 호스트 결정

        우선순위:
        1. 환경변수 {SERVICE}_HOST (예: INDICATOR_HOST)
        2. Docker 환경: service_name (예: indicator-service)
        3. 기본값: localhost

        Returns:
            결정된 호스트
        """
        # 환경변수로 서비스명 변환 (indicator-service -> INDICATOR)
        env_key = (
            self.service_name.upper().replace("-SERVICE", "").replace("-", "_")
            + "_HOST"
        )
        env_host = os.getenv(env_key)
        if env_host:
            return env_host

        # Docker 환경 감지
        if os.path.exists("/.dockerenv") or os.getenv("DOCKER_ENV"):
            return self.service_name

        # 기본값
        return "localhost"

    def _determine_port(self) -> int:
        """
        환경 기반 포트 결정

        우선순위:
        1. 환경변수 {SERVICE}_GRPC_PORT (예: SUBSCRIPTION_GRPC_PORT)
        2. default_port 파라미터

        Returns:
            결정된 포트

        Example:
            # subscription-service -> SUBSCRIPTION_GRPC_PORT
            # market-data-service -> MARKET_DATA_GRPC_PORT
        """
        # 환경변수로 서비스명 변환 (subscription-service -> SUBSCRIPTION)
        env_key = (
            self.service_name.upper().replace("-SERVICE", "").replace("-", "_")
            + "_GRPC_PORT"
        )
        env_port = os.getenv(env_key)
        if env_port:
            try:
                return int(env_port)
            except ValueError:
                logger.warning(
                    f"Invalid port in environment variable {env_key}={env_port}, "
                    f"using default_port={self.default_port}"
                )

        # 기본값
        return self.default_port

    def _create_channel(self, **kwargs: Any) -> grpc.aio.Channel:
        """
        gRPC 채널 생성

        Args:
            **kwargs: 추가 채널 옵션

        Returns:
            생성된 gRPC 채널
        """
        # 기본 keepalive 옵션
        default_options = [
            ("grpc.keepalive_time_ms", 30000),  # 30초마다 keepalive ping
            ("grpc.keepalive_timeout_ms", 10000),  # 10초 타임아웃
            ("grpc.keepalive_permit_without_calls", True),  # 활성 호출 없어도 ping 허용
            ("grpc.http2.max_pings_without_data", 0),  # ping 제한 없음
        ]

        # 사용자 정의 옵션과 병합
        user_options = kwargs.pop("options", [])
        merged_options = default_options + user_options

        if self.use_tls:
            credentials = grpc.ssl_channel_credentials()
            return grpc.aio.secure_channel(
                self.address,
                credentials,
                options=merged_options,
                **kwargs,
            )
        else:
            return grpc.aio.insecure_channel(
                self.address,
                options=merged_options,
                **kwargs,
            )

    @property
    def metadata(self) -> list[tuple[str, str]]:
        """
        gRPC 메타데이터 생성 (모든 요청에 자동 주입)

        Returns:
            메타데이터 튜플 리스트

        Note:
            - request_id는 매 호출마다 새로 생성됩니다.
            - user_id가 없으면 빈 문자열이지만, 서버에서 UNAUTHENTICATED 오류 발생.
            - 모든 값은 문자열로 변환되며, None은 빈 문자열로 처리됩니다.
        """
        request_id = str(uuid.uuid4())

        metadata = [
            (GRPC_METADATA_USER_ID, self.user_id or ""),
            (GRPC_METADATA_CORRELATION_ID, self.correlation_id or ""),
            (GRPC_METADATA_REQUEST_ID, request_id),
        ]

        # Debug logging for metadata
        logger.debug(
            "gRPC metadata prepared",
            service=self.service_name,
            user_id=self.user_id or "<empty>",
            correlation_id=self.correlation_id,
            request_id=request_id,
        )

        return metadata

    async def close(self):
        """채널 종료"""
        if self.channel:
            try:
                await self.channel.close()
                logger.info(
                    "gRPC channel closed",
                    client_class=self.__class__.__name__,
                    service=self.service_name,
                    address=self.address,
                )
            except Exception as e:
                logger.error(
                    "Error closing gRPC channel",
                    service=self.service_name,
                    error=str(e),
                    exc_info=True,
                )

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.close()
        return False  # 예외를 전파

    def _handle_grpc_error(
        self, error: grpc.RpcError, operation: str = "RPC call"
    ) -> None:
        """
        gRPC 에러 처리 및 로깅

        Args:
            error: gRPC 에러 객체
            operation: 작업 설명 (로깅용)
        """
        status_code = error.code() if hasattr(error, "code") else "UNKNOWN"
        details = error.details() if hasattr(error, "details") else str(error)

        logger.error(
            "gRPC error occurred",
            service=self.service_name,
            operation=operation,
            status_code=status_code,
            details=details,
            user_id=self.user_id,
            correlation_id=self.correlation_id,
        )

    async def check_health(self) -> bool:
        """
        서비스 헬스 체크 (gRPC Health Checking Protocol)

        Returns:
            서비스가 정상이면 True, 아니면 False

        Note:
            서비스가 gRPC Health Checking Protocol을 구현한 경우에만 동작합니다.
            구현되지 않은 경우 UNIMPLEMENTED 오류가 발생하며 False를 반환합니다.
        """
        try:
            from grpc_health.v1 import health_pb2, health_pb2_grpc  # type: ignore

            health_stub = health_pb2_grpc.HealthStub(self.channel)
            health_request = health_pb2.HealthCheckRequest(service=self.service_name)
            response = await health_stub.Check(health_request, timeout=5.0)  # type: ignore

            is_healthy = response.status == health_pb2.HealthCheckResponse.SERVING

            logger.info(
                "Health check completed",
                service=self.service_name,
                status="healthy" if is_healthy else "unhealthy",
                is_healthy=is_healthy,
            )

            return is_healthy
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNIMPLEMENTED:
                logger.warning(
                    "Health check not implemented",
                    service=self.service_name,
                )
            else:
                self._handle_grpc_error(e, "health check")
            return False
        except ImportError:
            logger.warning(
                "grpcio-health-checking package not installed",
                service=self.service_name,
            )
            return False
        except Exception as e:
            logger.error(
                "Unexpected error during health check",
                service=self.service_name,
                error=str(e),
                exc_info=True,
            )
            return False

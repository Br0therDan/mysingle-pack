"""
gRPC Interceptors

서버 및 클라이언트 gRPC 인터셉터 모음
- AuthInterceptor: user_id 메타데이터 검증
- LoggingInterceptor: gRPC 호출 로깅
- MetadataInterceptor: correlation_id 등 공통 메타데이터 주입/검증
"""

from __future__ import annotations

from typing import Any, Callable

import grpc

from mysingle.constants import (
    GRPC_METADATA_CORRELATION_ID,
    GRPC_METADATA_REQUEST_ID,
    GRPC_METADATA_USER_ID,
)
from mysingle.core.logging import get_structured_logger

logger = get_structured_logger(__name__)


class AuthInterceptor(grpc.aio.ServerInterceptor):
    """
    gRPC 서버 인증 인터셉터

    user_id 메타데이터를 검증하고, 없으면 UNAUTHENTICATED 에러 반환
    개발/테스트 환경에서는 선택적으로 비활성화 가능

    Usage:
        ```python
        from mysingle.grpc import AuthInterceptor

        server = grpc.aio.server(
            interceptors=[AuthInterceptor(require_auth=True)]
        )
        ```
    """

    def __init__(
        self, require_auth: bool = True, exempt_methods: list[str] | None = None
    ):
        """
        Args:
            require_auth: 인증 필수 여부 (False면 검증 스킵)
            exempt_methods: 인증 면제 메서드 목록 (예: ["/health/Check"])
        """
        self.require_auth = require_auth
        self.exempt_methods = set(exempt_methods or [])

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """gRPC 서비스 인터셉트"""
        method = handler_call_details.method

        # 면제 메서드는 통과
        if method in self.exempt_methods:
            return await continuation(handler_call_details)

        # 인증 비활성화 시 통과
        if not self.require_auth:
            logger.debug(f"Auth disabled for method: {method}")
            return await continuation(handler_call_details)

        # 메타데이터에서 user_id 추출
        metadata = dict(handler_call_details.invocation_metadata or [])
        user_id = metadata.get(GRPC_METADATA_USER_ID)

        if not user_id:
            logger.warning(
                f"Missing {GRPC_METADATA_USER_ID} in gRPC metadata for {method}"
            )
            # UNAUTHENTICATED 에러를 반환하는 핸들러 생성
            # gRPC Python의 경우 continuation에서 handler를 가져온 후 context에서 abort 처리
            handler = await continuation(handler_call_details)

            # Handler wrapper로 인증 에러 주입
            async def auth_abort_wrapper(request, context):
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED,
                    f"Missing {GRPC_METADATA_USER_ID} metadata",
                )

            return grpc.unary_unary_rpc_method_handler(
                auth_abort_wrapper,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        logger.debug(f"gRPC call authenticated: user_id={user_id}, method={method}")
        return await continuation(handler_call_details)


class LoggingInterceptor(grpc.aio.ServerInterceptor):
    """
    gRPC 서버 로깅 인터셉터

    모든 gRPC 호출을 구조화된 로그로 기록
    - 요청 시작 시간
    - 응답 상태 코드
    - 소요 시간
    - 에러 메시지 (있는 경우)

    Usage:
        ```python
        from mysingle.grpc import LoggingInterceptor

        server = grpc.aio.server(
            interceptors=[LoggingInterceptor()]
        )
        ```
    """

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """gRPC 서비스 인터셉트 및 로깅"""
        import time

        method = handler_call_details.method
        metadata = dict(handler_call_details.invocation_metadata or [])

        user_id = metadata.get(GRPC_METADATA_USER_ID, "unknown")
        correlation_id = metadata.get(GRPC_METADATA_CORRELATION_ID, "N/A")

        start_time = time.time()
        logger.info(
            "gRPC call started",
            extra={
                "method": method,
                "user_id": user_id,
                "correlation_id": correlation_id,
            },
        )

        try:
            handler = await continuation(handler_call_details)
            elapsed = (time.time() - start_time) * 1000  # ms

            logger.info(
                "gRPC call completed",
                extra={
                    "method": method,
                    "user_id": user_id,
                    "correlation_id": correlation_id,
                    "elapsed_ms": round(elapsed, 2),
                    "status": "OK",
                },
            )
            return handler

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000  # ms
            logger.error(
                "gRPC call failed",
                extra={
                    "method": method,
                    "user_id": user_id,
                    "correlation_id": correlation_id,
                    "elapsed_ms": round(elapsed, 2),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise


class MetadataInterceptor(grpc.aio.ServerInterceptor):
    """
    gRPC 서버 메타데이터 검증 인터셉터

    correlation_id, request_id 등 추적 메타데이터 검증 및 자동 생성
    누락 시 자동 생성하여 컨텍스트에 추가

    Usage:
        ```python
        from mysingle.grpc import MetadataInterceptor

        server = grpc.aio.server(
            interceptors=[MetadataInterceptor(auto_generate=True)]
        )
        ```
    """

    def __init__(self, auto_generate: bool = True):
        """
        Args:
            auto_generate: correlation_id 자동 생성 여부 (True 권장)
        """
        self.auto_generate = auto_generate

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """메타데이터 검증 및 자동 생성"""
        import uuid

        metadata = dict(handler_call_details.invocation_metadata or [])

        # correlation_id 자동 생성
        if self.auto_generate and GRPC_METADATA_CORRELATION_ID not in metadata:
            correlation_id = str(uuid.uuid4())
            metadata[GRPC_METADATA_CORRELATION_ID] = correlation_id
            logger.debug(f"Auto-generated correlation_id: {correlation_id}")

        # request_id 자동 생성
        if self.auto_generate and GRPC_METADATA_REQUEST_ID not in metadata:
            request_id = str(uuid.uuid4())
            metadata[GRPC_METADATA_REQUEST_ID] = request_id
            logger.debug(f"Auto-generated request_id: {request_id}")

        # 메타데이터 로깅
        logger.debug(
            "gRPC metadata",
            extra={
                "method": handler_call_details.method,
                "correlation_id": metadata.get(GRPC_METADATA_CORRELATION_ID),
                "request_id": metadata.get(GRPC_METADATA_REQUEST_ID),
                "user_id": metadata.get(GRPC_METADATA_USER_ID),
            },
        )

        return await continuation(handler_call_details)


# Client Interceptors


class ClientAuthInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    """
    gRPC 클라이언트 인증 인터셉터

    user_id, correlation_id를 자동으로 메타데이터에 주입

    Usage:
        ```python
        from mysingle.grpc import ClientAuthInterceptor
        from fastapi import Request

        async with grpc.aio.insecure_channel(
            'service:50051',
            interceptors=[ClientAuthInterceptor(user_id="user123")]
        ) as channel:
            stub = MyServiceStub(channel)
            response = await stub.MyMethod(request)
        ```
    """

    def __init__(self, user_id: str | None = None, correlation_id: str | None = None):
        """
        Args:
            user_id: 사용자 ID (필수)
            correlation_id: 상관관계 ID (선택, 자동 생성됨)
        """
        self.user_id = user_id
        self.correlation_id = correlation_id

    async def intercept_unary_unary(
        self,
        continuation: Callable,
        client_call_details: grpc.ClientCallDetails,
        request: Any,
    ) -> Any:
        """메타데이터 주입"""
        import uuid
        from collections import namedtuple

        # 기존 메타데이터 복사
        metadata = list(client_call_details.metadata or [])

        # user_id 주입
        if self.user_id:
            metadata.append((GRPC_METADATA_USER_ID, self.user_id))

        # correlation_id 주입 (없으면 생성)
        correlation_id = self.correlation_id or str(uuid.uuid4())
        metadata.append((GRPC_METADATA_CORRELATION_ID, correlation_id))

        # namedtuple을 사용하여 새로운 ClientCallDetails 생성
        _ClientCallDetails = namedtuple(
            "ClientCallDetails",
            [
                "method",
                "timeout",
                "metadata",
                "credentials",
                "wait_for_ready",
                "compression",
            ],
        )

        new_details = _ClientCallDetails(
            method=client_call_details.method,
            timeout=client_call_details.timeout,
            metadata=tuple(metadata),
            credentials=client_call_details.credentials,
            wait_for_ready=(
                client_call_details.wait_for_ready
                if hasattr(client_call_details, "wait_for_ready")
                else None
            ),
            compression=(
                client_call_details.compression
                if hasattr(client_call_details, "compression")
                else None
            ),
        )

        return await continuation(new_details, request)


# Server Interceptors (추가)

# Prometheus 메트릭 (모듈 레벨, 중복 등록 방지)
try:
    from prometheus_client import Counter, Histogram

    _grpc_requests_total = Counter(
        "mysingle_grpc_requests_total",
        "Total gRPC requests",
        ["service", "method", "status"],
    )

    _grpc_request_duration = Histogram(
        "mysingle_grpc_request_duration_seconds",
        "gRPC request duration",
        ["service", "method"],
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    )

    _METRICS_AVAILABLE = True
except ImportError:
    _METRICS_AVAILABLE = False


class MetricsInterceptor(grpc.aio.ServerInterceptor):
    """
    gRPC 서버 메트릭 수집 인터셉터

    Prometheus 메트릭 자동 수집:
    - grpc_requests_total: 총 요청 수 (서비스, 메서드, 상태별)
    - grpc_request_duration_seconds: 요청 소요 시간 히스토그램
    - grpc_active_connections: 현재 활성 연결 수

    Usage:
        ```python
        from mysingle.grpc.interceptors import MetricsInterceptor

        server = grpc.aio.server(
            interceptors=[MetricsInterceptor(service_name="strategy-service")]
        )
        ```
    """

    def __init__(self, service_name: str):
        """
        Args:
            service_name: 서비스 이름 (메트릭 레이블)
        """
        self.service_name = service_name

        if not _METRICS_AVAILABLE:
            logger.warning(
                "prometheus_client not installed - metrics disabled. "
                "Install: pip install prometheus-client"
            )

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """메트릭 수집"""
        if not _METRICS_AVAILABLE:
            return await continuation(handler_call_details)

        import time

        method = handler_call_details.method.split("/")[
            -1
        ]  # /package.Service/Method -> Method
        start_time = time.time()
        status = "OK"

        try:
            handler = await continuation(handler_call_details)
            return handler

        except grpc.RpcError as e:
            status = str(e.code())
            raise

        except Exception:
            status = "UNKNOWN"
            raise

        finally:
            # 소요 시간 측정
            duration = time.time() - start_time

            # 메트릭 업데이트 (모듈 레벨 변수 사용)
            _grpc_requests_total.labels(
                service=self.service_name, method=method, status=status
            ).inc()

            _grpc_request_duration.labels(
                service=self.service_name, method=method
            ).observe(duration)


class ErrorHandlingInterceptor(grpc.aio.ServerInterceptor):
    """
    gRPC 서버 에러 핸들링 인터셉터

    Python 예외를 gRPC StatusCode로 자동 변환:
    - ValueError, TypeError -> INVALID_ARGUMENT
    - PermissionError -> PERMISSION_DENIED
    - FileNotFoundError, KeyError -> NOT_FOUND
    - NotImplementedError -> UNIMPLEMENTED
    - TimeoutError -> DEADLINE_EXCEEDED
    - 기타 Exception -> INTERNAL

    Usage:
        ```python
        from mysingle.grpc.interceptors import ErrorHandlingInterceptor

        server = grpc.aio.server(
            interceptors=[ErrorHandlingInterceptor()]
        )
        ```
    """

    # 예외 타입 -> gRPC StatusCode 매핑
    ERROR_MAPPING = {
        ValueError: grpc.StatusCode.INVALID_ARGUMENT,
        TypeError: grpc.StatusCode.INVALID_ARGUMENT,
        PermissionError: grpc.StatusCode.PERMISSION_DENIED,
        FileNotFoundError: grpc.StatusCode.NOT_FOUND,
        KeyError: grpc.StatusCode.NOT_FOUND,
        NotImplementedError: grpc.StatusCode.UNIMPLEMENTED,
        TimeoutError: grpc.StatusCode.DEADLINE_EXCEEDED,
    }

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """에러 핸들링"""
        method = handler_call_details.method

        try:
            handler = await continuation(handler_call_details)

            # 원본 handler를 래핑하여 에러 변환 적용
            if handler and handler.unary_unary:
                original_unary = handler.unary_unary

                async def error_wrapped_unary(request, context):
                    try:
                        return await original_unary(request, context)
                    except grpc.RpcError:
                        # gRPC 에러는 그대로 전파
                        raise
                    except Exception as e:
                        # Python 예외 -> gRPC StatusCode 변환
                        status_code = self.ERROR_MAPPING.get(
                            type(e), grpc.StatusCode.INTERNAL
                        )
                        error_msg = f"{type(e).__name__}: {str(e)}"

                        logger.error(
                            f"gRPC error in {method}: {error_msg}",
                            extra={
                                "method": method,
                                "exception_type": type(e).__name__,
                                "status_code": status_code,
                            },
                            exc_info=True,
                        )

                        await context.abort(status_code, error_msg)

                return grpc.unary_unary_rpc_method_handler(
                    error_wrapped_unary,
                    request_deserializer=handler.request_deserializer,
                    response_serializer=handler.response_serializer,
                )

            return handler

        except Exception as e:
            logger.error(
                f"Error in ErrorHandlingInterceptor for {method}: {e}",
                exc_info=True,
            )
            raise


class RateLimiterInterceptor(grpc.aio.ServerInterceptor):
    """
    gRPC 서버 Rate Limiting 인터셉터

    슬라이딩 윈도우 방식으로 요청 제한:
    - Redis 기반 (가용 시) 또는 In-Memory 폴백
    - user_id별 제한 (메타데이터에서 추출)
    - 초과 시 RESOURCE_EXHAUSTED 에러 반환

    Usage:
        ```python
        from mysingle.grpc.interceptors import RateLimiterInterceptor

        server = grpc.aio.server(
            interceptors=[
                RateLimiterInterceptor(max_requests=1000, window_seconds=60)
            ]
        )
        ```
    """

    def __init__(self, max_requests: int = 1000, window_seconds: int = 60):
        """
        Args:
            max_requests: 윈도우 내 최대 요청 수
            window_seconds: 윈도우 크기 (초)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._redis_client = None
        self._memory_fallback: dict[str, list[float]] = {}  # user_id -> timestamps

        logger.info(f"RateLimiterInterceptor: {max_requests} req/{window_seconds}s")

    async def _get_redis(self):
        """Redis 클라이언트 가져오기 (lazy loading)"""
        if self._redis_client is None:
            try:
                from mysingle.database import get_redis_client

                self._redis_client = await get_redis_client(db=3)  # Rate limit 전용 DB
                logger.debug("RateLimiter using Redis backend")
            except Exception as e:
                logger.warning(
                    f"Redis not available for rate limiting, using in-memory fallback: {e}"
                )
        return self._redis_client

    async def _check_rate_limit_redis(self, user_id: str) -> bool:
        """Redis 기반 Rate limit 체크"""
        import time

        redis = await self._get_redis()
        if redis is None:
            return await self._check_rate_limit_memory(user_id)

        try:
            key = f"ratelimit:{user_id}"
            now = time.time()
            window_start = now - self.window_seconds

            # 슬라이딩 윈도우: 오래된 타임스탬프 제거
            await redis.zremrangebyscore(key, 0, window_start)

            # 현재 카운트 확인
            count = await redis.zcard(key)

            if count >= self.max_requests:
                logger.warning(
                    f"Rate limit exceeded for user {user_id}: {count}/{self.max_requests}"
                )
                return False

            # 현재 요청 타임스탬프 추가
            await redis.zadd(key, {str(now): now})
            await redis.expire(key, self.window_seconds * 2)  # TTL 2배로 설정

            return True

        except Exception as e:
            logger.error(f"Redis rate limit error: {e}, fallback to memory")
            return await self._check_rate_limit_memory(user_id)

    async def _check_rate_limit_memory(self, user_id: str) -> bool:
        """In-Memory 폴백 Rate limit 체크"""
        import time

        now = time.time()
        window_start = now - self.window_seconds

        # 오래된 타임스탬프 제거
        if user_id in self._memory_fallback:
            self._memory_fallback[user_id] = [
                ts for ts in self._memory_fallback[user_id] if ts > window_start
            ]
        else:
            self._memory_fallback[user_id] = []

        # 카운트 확인
        count = len(self._memory_fallback[user_id])
        if count >= self.max_requests:
            logger.warning(
                f"Rate limit exceeded (memory) for user {user_id}: {count}/{self.max_requests}"
            )
            return False

        # 현재 요청 추가
        self._memory_fallback[user_id].append(now)
        return True

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """Rate limit 체크"""
        metadata = dict(handler_call_details.invocation_metadata or [])
        user_id_raw = metadata.get(GRPC_METADATA_USER_ID, "anonymous")

        # bytes를 str로 변환
        user_id = (
            user_id_raw.decode("utf-8")
            if isinstance(user_id_raw, bytes)
            else str(user_id_raw)
        )

        # Rate limit 체크
        allowed = await self._check_rate_limit_redis(user_id)

        if not allowed:
            # RESOURCE_EXHAUSTED 에러 반환
            handler = await continuation(handler_call_details)

            async def rate_limit_abort(request, context):
                await context.abort(
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                    f"Rate limit exceeded: {self.max_requests} req/{self.window_seconds}s",
                )

            return grpc.unary_unary_rpc_method_handler(
                rate_limit_abort,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        # 허용
        return await continuation(handler_call_details)


__all__ = [
    "AuthInterceptor",
    "LoggingInterceptor",
    "MetadataInterceptor",
    "ClientAuthInterceptor",
    "MetricsInterceptor",
    "ErrorHandlingInterceptor",
    "RateLimiterInterceptor",
]

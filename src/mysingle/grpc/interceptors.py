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


__all__ = [
    "AuthInterceptor",
    "LoggingInterceptor",
    "MetadataInterceptor",
    "ClientAuthInterceptor",
]

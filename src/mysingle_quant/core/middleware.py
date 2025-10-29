"""
FastAPI 미들웨어 for Correlation ID and Request Logging
"""

import time
import uuid
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..logging.structured_logging import (
    get_structured_logger,
    set_correlation_id,
    set_user_id,
    set_request_id,
    clear_logging_context,
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """요청/응답 로깅 및 Correlation ID 관리 미들웨어"""

    def __init__(self, app, service_name: str = "unknown"):
        super().__init__(app)
        self.service_name = service_name
        self.logger = get_structured_logger(__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 컨텍스트 초기화
        clear_logging_context()

        # Request ID 생성
        request_id = str(uuid.uuid4())
        set_request_id(request_id)

        # Correlation ID 설정
        correlation_id = request.headers.get("correlation-id") or str(uuid.uuid4())
        set_correlation_id(correlation_id)

        # User ID 설정 (X-User-Id 헤더에서)
        user_id = request.headers.get("x-user-id", "")
        if user_id:
            set_user_id(user_id)

        # 요청 시작 시간
        start_time = time.time()

        # 요청 로깅
        self.logger.info(
            "Request started",
            extra={
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": (
                    str(request.query_params) if request.query_params else None
                ),
                "user_agent": request.headers.get("user-agent"),
                "client_ip": self._get_client_ip(request),
            },
        )

        # 요청 처리
        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # 성공 응답 로깅
            self.logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                },
            )

        except Exception as exc:
            duration = time.time() - start_time

            # 에러 응답 로깅
            self.logger.error(
                "Request failed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
            )
            raise

        # Correlation ID를 응답 헤더에 추가
        response.headers["correlation-id"] = correlation_id
        response.headers["request-id"] = request_id

        return response

    def _get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 주소 추출"""
        # X-Forwarded-For 헤더 확인 (프록시 환경)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # 첫 번째 IP가 실제 클라이언트 IP
            return forwarded_for.split(",")[0].strip()

        # X-Real-IP 헤더 확인
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # 직접 연결된 클라이언트 IP
        return request.client.host if request.client else "unknown"


class HealthCheckLoggingFilter:
    """헬스체크 요청 로깅 필터"""

    def __init__(self, health_paths: Optional[list[str]] = None):
        self.health_paths = health_paths or ["/health", "/ready", "/alive"]

    def should_log_request(self, request: Request) -> bool:
        """요청을 로깅할지 결정"""
        path = request.url.path

        # 헬스체크 경로는 로깅하지 않음
        if path in self.health_paths:
            return False

        # OPTIONS 요청은 로깅하지 않음 (CORS preflight)
        if request.method == "OPTIONS":
            return False

        return True


class TimingLogMiddleware(BaseHTTPMiddleware):
    """간단한 타이밍 로그 미들웨어 (디버그용)"""

    def __init__(self, app, enable_timing_logs: bool = False):
        super().__init__(app)
        self.enable_timing_logs = enable_timing_logs
        self.logger = get_structured_logger(__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.enable_timing_logs:
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # 느린 요청만 로깅 (>1초)
        if duration > 1.0:
            self.logger.warning(
                "Slow request detected",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                },
            )

        return response


def add_logging_middleware(app, service_name: str, enable_timing_logs: bool = False):
    """로깅 미들웨어를 FastAPI 앱에 추가"""

    # 타이밍 로그 미들웨어 (선택적)
    if enable_timing_logs:
        app.add_middleware(TimingLogMiddleware, enable_timing_logs=True)

    # 메인 로깅 미들웨어
    app.add_middleware(LoggingMiddleware, service_name=service_name)


def setup_request_id_dependency():
    """Request ID 의존성 함수 (FastAPI dependency)"""
    from fastapi import Depends, Header
    from typing import Optional

    def get_request_context(
        correlation_id: Optional[str] = Header(None, alias="correlation-id"),
        user_id: Optional[str] = Header(None, alias="x-user-id"),
        request_id: Optional[str] = Header(None, alias="request-id"),
    ):
        """요청 컨텍스트 정보 반환"""
        return {
            "correlation_id": correlation_id,
            "user_id": user_id,
            "request_id": request_id,
        }

    return Depends(get_request_context)

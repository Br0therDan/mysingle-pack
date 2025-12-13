"""
Kong Gateway Authentication Middleware (Lightweight)

Kong Gateway가 이미 JWT 인증을 완료했으므로,
이 미들웨어는 단순히 Kong 헤더를 추출하여 Request.state에 주입합니다.

Features:
- X-User-Id 헤더 추출 및 검증
- Request.state에 user_id, email 등 주입
- 공개 경로 자동 제외
- 테스트 환경 인증 우회 지원
"""

import os
from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from mysingle.core.config import get_settings
from mysingle.core.logging import get_logger
from mysingle.core.service_types import ServiceConfig

logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Kong Gateway 헤더 기반 경량 인증 미들웨어

    Kong이 이미 JWT 검증을 완료했으므로, X-User-Id 헤더만 추출합니다.
    """

    def __init__(self, app: ASGIApp, service_config: ServiceConfig):
        super().__init__(app)
        self.service_config = service_config
        self.settings = get_settings()
        self.auth_bypass = self._check_auth_bypass()
        self.public_paths = self._prepare_public_paths()

    def _check_auth_bypass(self) -> bool:
        """테스트 환경 인증 우회 확인"""
        bypass_enabled = os.getenv("MYSINGLE_AUTH_BYPASS", "false").lower() == "true"
        env = os.getenv("ENVIRONMENT", "development").lower()

        if bypass_enabled and env == "production":
            logger.warning(
                "MYSINGLE_AUTH_BYPASS ignored in production",
                bypass_enabled=bypass_enabled,
                environment=env,
            )
            return False

        if bypass_enabled:
            logger.info(
                "Authentication bypass enabled",
                environment=env,
            )

        return bypass_enabled

    def _prepare_public_paths(self) -> list[str]:
        """공개 경로 목록 (중복 제거 및 정규화)"""
        # 기본 공개 경로
        default_public_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
        ]

        # ServiceConfig에서 추가 경로 수집
        # Note: ServiceConfig.__post_init__이 기본값을 설정하지만,
        # 사용자가 명시적으로 제공한 경우만 추가하여 중복 방지
        service_public_paths = self.service_config.public_paths or []
        auth_public_paths = self.service_config.auth_public_paths or []

        # 모든 경로 결합 및 중복 제거
        all_paths = default_public_paths + service_public_paths + auth_public_paths

        # Trailing slash 정규화 및 중복 제거
        normalized_paths = set()
        for path in all_paths:
            # 경로 정규화 (trailing slash 제거)
            normalized = path.rstrip("/") if path != "/" else path
            normalized_paths.add(normalized)

        return sorted(normalized_paths)  # 정렬로 예측 가능한 순서 보장

    def _is_public_path(self, path: str) -> bool:
        """공개 경로 확인 (정확한 경로 또는 접두사 매칭)"""
        # Trailing slash 정규화
        normalized_path = path.rstrip("/") if path != "/" else path

        for public_path in self.public_paths:
            # 정확한 매칭
            if normalized_path == public_path:
                return True
            # 접두사 매칭 (하위 경로 포함, 예: /docs → /docs/swagger)
            # 단, 부분 문자열이 아닌 경로 세그먼트 단위로 매칭
            if normalized_path.startswith(public_path + "/"):
                return True

        return False

    def _extract_kong_headers(self, request: Request) -> Optional[dict]:
        """Kong Gateway 헤더 추출"""
        x_user_id = request.headers.get("X-User-Id")

        if not x_user_id:
            return None

        return {
            "user_id": x_user_id,
            "email": request.headers.get("X-User-Email", "unknown@gateway.local"),
            "is_verified": request.headers.get("X-User-Verified", "false").lower()
            == "true",
            "is_active": request.headers.get("X-User-Active", "true").lower() == "true",
            "is_superuser": request.headers.get("X-User-Superuser", "false").lower()
            == "true",
        }

    def _create_test_user_context(self) -> dict:
        """테스트 사용자 컨텍스트 생성"""
        use_admin = os.getenv("MYSINGLE_AUTH_BYPASS_ADMIN", "false").lower() == "true"

        if use_admin:
            return {
                "user_id": "000000000000000000000001",
                "email": os.getenv("TEST_ADMIN_EMAIL", "test_admin@test.com"),
                "is_verified": True,
                "is_active": True,
                "is_superuser": True,
            }
        else:
            return {
                "user_id": "000000000000000000000002",
                "email": os.getenv("TEST_USER_EMAIL", "test_user@test.com"),
                "is_verified": True,
                "is_active": True,
                "is_superuser": False,
            }

    async def dispatch(self, request: Request, call_next):
        """미들웨어 메인 로직"""
        path = request.url.path
        method = request.method

        # 공개 경로는 인증 건너뛰기
        if self._is_public_path(path):
            request.state.user_id = None
            request.state.authenticated = False
            return await call_next(request)

        # 인증 비활성화된 경우
        if not self.service_config.enable_auth:
            return await call_next(request)

        # 테스트 환경 인증 우회
        if self.auth_bypass:
            test_context = self._create_test_user_context()
            request.state.user_id = test_context["user_id"]
            request.state.email = test_context["email"]
            request.state.is_verified = test_context["is_verified"]
            request.state.is_active = test_context["is_active"]
            request.state.is_superuser = test_context["is_superuser"]
            request.state.authenticated = True
            return await call_next(request)

        # Kong Gateway 헤더 추출
        kong_context = self._extract_kong_headers(request)

        if not kong_context:
            logger.warning(
                "No Kong authentication headers",
                method=method,
                path=path,
            )
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Authentication required",
                    "message": "X-User-Id header missing",
                },
            )

        # 비활성 사용자 차단
        if not kong_context["is_active"]:
            logger.warning(
                "Inactive user blocked",
                user_id=kong_context["user_id"],
                method=method,
                path=path,
            )
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "User account is inactive",
                },
            )

        # Request.state에 사용자 정보 저장
        request.state.user_id = kong_context["user_id"]
        request.state.email = kong_context["email"]
        request.state.is_verified = kong_context["is_verified"]
        request.state.is_active = kong_context["is_active"]
        request.state.is_superuser = kong_context["is_superuser"]
        request.state.authenticated = True

        logger.debug(
            "User authenticated via Kong Gateway",
            user_id=kong_context["user_id"],
            email=kong_context["email"],
            method=method,
            path=path,
        )

        return await call_next(request)

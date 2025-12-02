"""
Authentication Middleware v2 - Request-Based Authentication with Kong Gateway Integration

새로운 Request 기반 인증 시스템을 위한 리팩토링된 미들웨어입니다.
기존 gateway_deps 의존성을 제거하고 내장 인증 로직으로 대체했습니다.

Features:
- Request.state.user 직접 주입 (deps_new.py와 완전 호환)
- 서비스 타입별 자동 인증 방식 선택 (IAM vs NON_IAM)
- Kong Gateway 헤더 기반 인증 지원
- 공개 경로 자동 제외
- 테스트 환경 인증 우회 지원 (MYSINGLE_AUTH_BYPASS=true)
- 높은 성능 및 에러 처리
"""

import os
from typing import Optional, cast

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from mysingle.core.config import get_settings
from mysingle.core.logging import get_logger
from mysingle.core.service_types import ServiceConfig, ServiceType

from .cache import get_user_cache
from .exceptions import AuthorizationFailed, InvalidToken, UserInactive, UserNotExists
from .models import User

logger = get_logger(__name__)
settings = get_settings()


class AuthMiddleware(BaseHTTPMiddleware):
    """
    MSA 환경에서 Kong Gateway와 연동되는 인증 미들웨어

    Features:
    - 서비스 타입별 자동 인증 방식 선택 (IAM vs NON_IAM)
    - Kong Gateway 헤더 기반 인증 지원
    - 공개 경로 자동 제외
    - Request.state에 사용자 정보 주입
    """

    def __init__(self, app: ASGIApp, service_config: ServiceConfig):
        super().__init__(app)
        self.service_config = service_config
        self.public_paths = self._prepare_public_paths()
        # User Cache (Hybrid: Redis + In-Memory)
        self.user_cache = get_user_cache()
        # Test bypass flag (only active in non-production)
        self.auth_bypass = self._check_auth_bypass()
        self.settings = settings

    def _check_auth_bypass(self) -> bool:
        """Check if authentication bypass is enabled for testing"""
        bypass_enabled = os.getenv("MYSINGLE_AUTH_BYPASS", "false").lower() == "true"
        env = os.getenv("ENVIRONMENT", "development").lower()

        if bypass_enabled and env == "production":
            logger.warning(
                "MYSINGLE_AUTH_BYPASS is set in production environment - IGNORING for security",
                bypass_enabled=bypass_enabled,
                environment=env,
                security_risk="high",
            )
            return False

        if bypass_enabled:
            logger.info(
                "Authentication bypass enabled for testing",
                bypass_enabled=bypass_enabled,
                environment=env,
                mode="testing",
            )

        return bypass_enabled

    def _prepare_public_paths(self) -> list[str]:
        """공개 경로 목록 준비"""
        default_public_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
        ]

        # 서비스별 공개 경로 추가
        service_public_paths = self.service_config.public_paths or []

        # IAM 서비스는 인증 관련 경로도 공개
        if self.service_config.service_type == ServiceType.IAM_SERVICE:
            # settings.AUTH_PUBLIC_PATHS를 사용하여 중앙 관리
            auth_public_paths = getattr(self.settings, "AUTH_PUBLIC_PATHS", [])
            default_public_paths.extend(auth_public_paths)

        return default_public_paths + service_public_paths

    def _is_public_path(self, path: str) -> bool:
        """요청 경로가 공개 경로인지 확인"""
        return any(path.startswith(public_path) for public_path in self.public_paths)

    async def _authenticate_iam_service(self, request: Request) -> Optional[User]:
        """IAM 서비스용 직접 JWT 토큰 검증"""
        try:
            # Authorization 헤더에서 Bearer 토큰 추출
            authorization = request.headers.get("Authorization", "")
            token: Optional[str] = None
            if authorization.startswith("Bearer "):
                token = authorization.replace("Bearer ", "").strip()
                logger.debug(
                    "Token extracted from Authorization header",
                    has_token=bool(token),
                )

            # Authorization이 없으면 쿠키에서 access_token 검색 (브라우저 호출 대비)
            if not token:
                try:
                    token = request.cookies.get("access_token")
                    if token:
                        logger.debug(
                            "Token extracted from cookie",
                            has_token=True,
                        )
                except Exception:
                    token = None

            if not token:
                logger.debug(
                    "No authentication token found",
                    checked_sources=["Authorization header", "access_token cookie"],
                )
                return None

            # JWT 토큰 직접 검증
            try:
                from .security.jwt import get_jwt_manager
            except ImportError:
                logger.warning(
                    "JWT security module not available",
                    module="mysingle.auth.security.jwt",
                )
                return None

            jwt_manager = get_jwt_manager()
            decoded_token = jwt_manager.decode_token(token)
            user_id = decoded_token.get("sub")
            if not user_id:
                logger.debug(
                    "No user_id (sub) in JWT token",
                    token_claims=list(decoded_token.keys()),
                )
                return None

            # 캐시 우선 조회 -> 미스 시 DB 조회 후 캐시 저장
            user = await self._get_user_with_cache(user_id)

            if user and not user.is_active:
                logger.warning(
                    "Inactive user attempted access",
                    user_id=user_id,
                    source="iam_jwt_validation",
                )
                return None

            # DB에 사용자 레코드가 없더라도, JWT 클레임으로 최소 사용자 컨텍스트를 구성해 허용
            # (게이트웨이에서 이미 서명 검증을 통과했고, 여기서도 검증됨)
            if not user:
                try:
                    from beanie import PydanticObjectId
                except Exception:
                    PydanticObjectId = None  # 타입 회피

                user_obj_id = (
                    PydanticObjectId(decoded_token.get("sub"))
                    if PydanticObjectId
                    else decoded_token.get("sub")
                )
                user = User(
                    id=user_obj_id,  # type: ignore[arg-type]
                    email=decoded_token.get("email") or "unknown@token.local",
                    hashed_password="",
                    is_verified=bool(decoded_token.get("is_verified", False)),
                    is_active=bool(decoded_token.get("is_active", True)),
                    is_superuser=bool(decoded_token.get("is_superuser", False)),
                )

                # 비활성 토큰은 거부
                if not user.is_active:
                    logger.warning(
                        "Inactive user (from token claims) attempted access",
                        user_id=user_id,
                        source="jwt_claims_fallback",
                    )
                    return None

                logger.debug(
                    "Authenticated via JWT claims fallback",
                    user_email=user.email,
                    user_id=str(user.id),
                    source="jwt_claims",
                )

                # 캐시에도 적재 시도 (최소 컨텍스트)
                try:
                    await self.user_cache.set_user(user)  # type: ignore
                except Exception as e:
                    logger.debug(
                        "Failed to cache user from claims",
                        error=str(e),
                    )

            return user

        except Exception as e:
            logger.debug(
                "IAM service authentication failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            return None

    async def _authenticate_non_iam_service(self, request: Request) -> Optional[User]:
        """NON_IAM 서비스용 Kong Gateway 헤더 기반 인증"""
        try:
            # Kong Gateway에서 전달하는 헤더들
            x_user_id = request.headers.get("X-User-Id")
            x_user_email = request.headers.get("X-User-Email")
            x_user_verified = request.headers.get("X-User-Verified", "false")
            x_user_active = request.headers.get("X-User-Active", "false")
            x_user_superuser = request.headers.get("X-User-Superuser", "false")

            if not x_user_id:
                logger.debug(
                    "No X-User-Id header found in request",
                    source="kong_gateway_headers",
                )
                return None

            # 캐시에 사용자 정보가 있으면 우선 사용 (게이트웨이 경로에서도 재사용)
            cached_user = await self.user_cache.get_user(str(x_user_id))
            if cached_user:
                if not cached_user.is_active:
                    logger.warning(
                        "Inactive user from cache via gateway headers",
                        user_id=x_user_id,
                        source="cache",
                    )
                    return None
                logger.debug(
                    "User authenticated via cache (gateway)",
                    user_email=cached_user.email,
                    user_id=str(cached_user.id),
                    source="cache",
                )
                # Cast to local User type to avoid cross-package typing incompatibility at type-check time
                return cast(User, cached_user)

            # Gateway 헤더로부터 User 객체 구성
            try:
                from beanie import PydanticObjectId
            except ImportError:
                logger.warning(
                    "Beanie not available for user ID conversion",
                    module="beanie",
                )
                return None

            # 헤더 값 검증 및 변환
            try:
                user_object_id = PydanticObjectId(x_user_id)
            except Exception as e:
                logger.warning(
                    "Invalid user ID format in X-User-Id header",
                    user_id=x_user_id,
                    error=str(e),
                )
                return None

            # User 객체 생성 (Gateway에서 이미 검증된 정보)
            user = User(
                id=user_object_id,
                email=x_user_email or "unknown@gateway.local",
                hashed_password="",  # Gateway 인증에서는 불필요
                is_verified=x_user_verified.lower() == "true",
                is_active=x_user_active.lower() == "true",
                is_superuser=x_user_superuser.lower() == "true",
            )

            # 활성 사용자만 허용
            if not user.is_active:
                logger.warning(
                    "Inactive user from gateway headers",
                    user_id=str(user_object_id),
                    source="kong_gateway_headers",
                )
                return None

            logger.debug(
                "User authenticated via gateway headers",
                user_email=user.email,
                user_id=str(user.id),
                is_verified=user.is_verified,
                is_superuser=user.is_superuser,
                source="kong_gateway_headers",
            )

            # 게이트웨이 기반 사용자도 단기 캐시 (TTL 기본값)
            try:
                await self.user_cache.set_user(user)  # type: ignore
            except Exception as e:
                logger.debug(
                    "Failed to set user in cache (gateway)",
                    error=str(e),
                )
            return user

        except Exception as e:
            logger.debug(
                "NON_IAM service authentication failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            return None

    async def _authenticate_user(self, request: Request) -> Optional[User]:
        """서비스 타입에 따른 인증 수행"""
        if self.service_config.service_type == ServiceType.IAM_SERVICE:
            # IAM 서비스: 직접 JWT 검증 우선
            user = await self._authenticate_iam_service(request)
            if user:
                logger.debug(
                    "IAM service: User authenticated via JWT",
                    user_email=user.email,
                    user_id=str(user.id),
                    auth_method="jwt",
                )
                return user

            # Fallback: Gateway 헤더 (개발/테스트 환경)
            logger.debug(
                "IAM service: Falling back to gateway headers",
                service_type="IAM_SERVICE",
                fallback_method="gateway_headers",
            )
            return await self._authenticate_non_iam_service(request)

        else:
            # NON_IAM 서비스: Gateway 헤더 우선
            user = await self._authenticate_non_iam_service(request)
            if user:
                logger.debug(
                    "NON_IAM service: User authenticated via gateway",
                    user_email=user.email,
                    user_id=str(user.id),
                    auth_method="gateway_headers",
                )
                return user

            # Fallback: 직접 토큰 (개발 환경에서 Gateway 없이 테스트할 때)
            logger.debug(
                "NON_IAM service: Falling back to direct JWT validation",
                service_type="NON_IAM_SERVICE",
                fallback_method="jwt",
            )
            return await self._authenticate_iam_service(request)

    async def _get_user_with_cache(self, user_id: str) -> Optional[User]:
        """캐시 우선으로 사용자 조회, 미스 시 DB 조회 후 캐시 저장"""
        try:
            # 1) 캐시 조회
            cached = await self.user_cache.get_user(str(user_id))
            if cached:
                logger.debug(
                    "Cache HIT for user",
                    user_id=user_id,
                    cache_result="hit",
                )
                return cached  # type: ignore

            logger.debug(
                "Cache MISS for user - querying DB",
                user_id=user_id,
                cache_result="miss",
            )

            # 2) DB 조회
            from beanie import PydanticObjectId

            from .user_manager import UserManager

            user_manager = UserManager()
            user = await user_manager.get(PydanticObjectId(user_id))

            # 3) 캐시에 저장 (성공 시)
            if user:
                try:
                    await self.user_cache.set_user(user)
                    logger.debug(
                        "User cached successfully",
                        user_id=user_id,
                    )
                except Exception as e:
                    logger.debug(
                        "Failed to set user in cache",
                        user_id=user_id,
                        error=str(e),
                    )
            return user  # type: ignore

        except Exception as e:
            logger.debug(
                "_get_user_with_cache error",
                user_id=user_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            return None

    def _create_test_user(self) -> User:
        """Create a test user for authentication bypass

        Uses environment variables for test user configuration:
        - TEST_USER_EMAIL: Test user email (default: test_user@test.com)
        - TEST_USER_FULLNAME: Test user full name (default: Test User)
        - TEST_ADMIN_EMAIL: Test admin email (for superuser bypass)
        """
        # Determine if superuser based on auth bypass mode
        # Default to regular test user, use admin if explicitly configured
        use_admin = os.getenv("MYSINGLE_AUTH_BYPASS_ADMIN", "false").lower() == "true"

        if use_admin:
            email = os.getenv("TEST_ADMIN_EMAIL", "test_admin@test.com")
            fullname = os.getenv("TEST_ADMIN_FULLNAME", "Test Admin")
            is_superuser = True
        else:
            email = os.getenv("TEST_USER_EMAIL", "test_user@test.com")
            fullname = os.getenv("TEST_USER_FULLNAME", "Test User")
            is_superuser = False

        try:
            from beanie import PydanticObjectId

            test_id = PydanticObjectId("000000000000000000000001")
        except ImportError:
            test_id = "000000000000000000000001"  # type: ignore

        return User(
            id=test_id,  # type: ignore
            email=email,
            full_name=fullname,
            hashed_password="",
            is_verified=True,
            is_active=True,
            is_superuser=is_superuser,
        )

    def _create_error_response(self, error: Exception) -> JSONResponse:
        """인증 에러 응답 생성"""
        if isinstance(error, UserNotExists):
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Authentication required",
                    "error_type": "UserNotExists",
                    "message": "Valid authentication credentials required",
                },
            )
        elif isinstance(error, InvalidToken):
            # Avoid directly accessing attributes that may not exist on the exception
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid authentication token",
                    "error_type": "InvalidToken",
                    "message": getattr(error, "reason", "Token validation failed"),
                },
            )
        elif isinstance(error, UserInactive):
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "User account is inactive",
                    "error_type": "UserInactive",
                    "message": "Account has been deactivated",
                },
            )
        elif isinstance(error, AuthorizationFailed):
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Insufficient permissions",
                    "error_type": "AuthorizationFailed",
                    "message": str(error),
                },
            )
        else:
            logger.error(
                "Unexpected authentication error",
                error=str(error),
                error_type=type(error).__name__,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal authentication error",
                    "error_type": "InternalError",
                    "message": "An unexpected error occurred during authentication",
                },
            )

    async def dispatch(self, request: Request, call_next):
        """미들웨어 메인 로직 - Request.state.user 주입"""
        path = request.url.path
        method = request.method

        # 공개 경로는 인증 건너뛰기
        if self._is_public_path(path):
            logger.debug(
                "Skipping authentication for public path",
                method=method,
                path=path,
                reason="public_endpoint",
            )
            return await call_next(request)

        # 인증이 비활성화된 경우 건너뛰기
        if not self.service_config.enable_auth:
            logger.debug(
                "Authentication disabled for service",
                service_name=self.service_config.service_name,
                enable_auth=False,
            )
            return await call_next(request)

        # 테스트 환경 인증 우회
        if self.auth_bypass:
            logger.debug(
                "Auth bypass: injecting test user",
                method=method,
                path=path,
                mode="testing",
            )
            test_user = self._create_test_user()
            request.state.user = test_user
            request.state.authenticated = True
            request.state.service_type = self.service_config.service_type
            return await call_next(request)

        try:
            # 사용자 인증 수행
            user = await self._authenticate_user(request)

            if user:
                # 이중 활성화 상태 확인 (인증 과정에서도 확인하지만 보안을 위해 재확인)
                if not user.is_active:
                    logger.warning(
                        "Inactive user blocked",
                        user_id=str(user.id),
                        method=method,
                        path=path,
                        reason="user_inactive",
                    )
                    raise UserInactive(user_id=str(user.id))

                # Request.state에 사용자 정보 저장 (deps_new.py와 호환)
                request.state.user = user
                request.state.authenticated = True
                request.state.service_type = self.service_config.service_type

                logger.debug(
                    "User authenticated successfully",
                    user_email=user.email,
                    user_id=str(user.id),
                    is_verified=user.is_verified,
                    is_superuser=user.is_superuser,
                    method=method,
                    path=path,
                )
            else:
                # 인증 필요한 경로에서 사용자 정보 없음
                logger.warning(
                    "Authentication required for protected endpoint",
                    method=method,
                    path=path,
                    reason="no_credentials",
                )
                raise UserNotExists(
                    identifier="user", identifier_type="authenticated user"
                )

        except (UserNotExists, InvalidToken, UserInactive, AuthorizationFailed) as e:
            logger.warning(
                "Authentication failed",
                method=method,
                path=path,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return self._create_error_response(e)

        except Exception as e:
            logger.error(
                "Unexpected authentication error",
                method=method,
                path=path,
                error=str(e),
                exc_info=True,
            )
            return self._create_error_response(e)

        # 다음 미들웨어/핸들러 호출
        response = await call_next(request)

        # 응답 헤더에 사용자 정보 추가 (디버깅용, 프로덕션에서는 제거 권장)
        if hasattr(request.state, "user") and request.state.user:
            response.headers["X-Authenticated-User"] = str(request.state.user.id)

        return response

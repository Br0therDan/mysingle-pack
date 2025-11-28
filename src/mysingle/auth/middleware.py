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
from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..core.service_types import ServiceConfig, ServiceType
from ..logging import get_structured_logger
from .cache import get_user_cache
from .exceptions import AuthorizationFailed, InvalidToken, UserInactive, UserNotExists
from .models import User

logger = get_structured_logger(__name__)


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

    def _check_auth_bypass(self) -> bool:
        """Check if authentication bypass is enabled for testing"""
        bypass_enabled = os.getenv("MYSINGLE_AUTH_BYPASS", "false").lower() == "true"
        env = os.getenv("ENVIRONMENT", "development").lower()

        if bypass_enabled and env == "production":
            logger.warning(
                "⚠️ MYSINGLE_AUTH_BYPASS is set in production environment - IGNORING for security"
            )
            return False

        if bypass_enabled:
            logger.info(
                f"🧪 Authentication bypass enabled for testing (Environment: {env})"
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
            auth_public_paths = [
                "/api/v1/auth/login",
                "/api/v1/auth/register",
                "/api/v1/auth/verify-email",
                "/api/v1/auth/reset-password",
                "/api/v1/oauth2/google/authorize",
                "/api/v1/oauth2/google/callback",
                "/api/v1/oauth2/kakao/authorize",
                "/api/v1/oauth2/kakao/callback",
                "/api/v1/oauth2/naver/authorize",
                "/api/v1/oauth2/naver/callback",
            ]
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

            # Authorization이 없으면 쿠키에서 access_token 검색 (브라우저 호출 대비)
            if not token:
                try:
                    token = request.cookies.get("access_token")
                except Exception:
                    token = None

            if not token:
                return None

            # JWT 토큰 직접 검증
            try:
                from .security.jwt import get_jwt_manager
            except ImportError:
                logger.warning("JWT security module not available")
                return None

            jwt_manager = get_jwt_manager()
            decoded_token = jwt_manager.decode_token(token)
            user_id = decoded_token.get("sub")
            if not user_id:
                return None

            # 캐시 우선 조회 -> 미스 시 DB 조회 후 캐시 저장
            user = await self._get_user_with_cache(user_id)

            if user and not user.is_active:
                logger.warning(f"Inactive user attempted access: {user_id}")
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
                        f"Inactive user (from token claims) attempted access: {user_id}"
                    )
                    return None

                logger.debug(
                    "Authenticated via JWT claims fallback: %s (ID: %s)",
                    user.email,
                    user.id,
                )

                # 캐시에도 적재 시도 (최소 컨텍스트)
                try:
                    await self.user_cache.set_user(user)
                except Exception as e:
                    logger.debug(f"Failed to cache user from claims: {e}")

            return user

        except Exception as e:
            logger.debug(f"IAM service authentication failed: {e}")
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
                logger.debug("No X-User-Id header found in request")
                return None

            # 캐시에 사용자 정보가 있으면 우선 사용 (게이트웨이 경로에서도 재사용)
            cached_user = await self.user_cache.get_user(str(x_user_id))
            if cached_user:
                if not cached_user.is_active:
                    logger.warning(
                        f"Inactive user from cache via gateway headers: {x_user_id}"
                    )
                    return None
                logger.debug(
                    f"User authenticated via cache (gateway): {cached_user.email} (ID: {cached_user.id})"
                )
                return cached_user

            # Gateway 헤더로부터 User 객체 구성
            try:
                from beanie import PydanticObjectId
            except ImportError:
                logger.warning("Beanie not available for user ID conversion")
                return None

            # 헤더 값 검증 및 변환
            try:
                user_object_id = PydanticObjectId(x_user_id)
            except Exception as e:
                logger.warning(
                    f"Invalid user ID format in X-User-Id header: {x_user_id} ({e})"
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
                logger.warning(f"Inactive user from gateway headers: {user_object_id}")
                return None

            logger.debug(
                f"User authenticated via gateway headers: {user.email} (ID: {user.id})"
            )

            # 게이트웨이 기반 사용자도 단기 캐시 (TTL 기본값)
            try:
                await self.user_cache.set_user(user)
            except Exception as e:
                logger.debug(f"Failed to set user in cache (gateway): {e}")
            return user

        except Exception as e:
            logger.debug(f"NON_IAM service authentication failed: {e}")
            return None

    async def _authenticate_user(self, request: Request) -> Optional[User]:
        """서비스 타입에 따른 인증 수행"""
        if self.service_config.service_type == ServiceType.IAM_SERVICE:
            # IAM 서비스: 직접 JWT 검증 우선
            user = await self._authenticate_iam_service(request)
            if user:
                logger.debug(f"IAM service: User authenticated via JWT: {user.email}")
                return user

            # Fallback: Gateway 헤더 (개발/테스트 환경)
            logger.debug("IAM service: Falling back to gateway headers")
            return await self._authenticate_non_iam_service(request)

        else:
            # NON_IAM 서비스: Gateway 헤더 우선
            user = await self._authenticate_non_iam_service(request)
            if user:
                logger.debug(
                    f"NON_IAM service: User authenticated via gateway: {user.email}"
                )
                return user

            # Fallback: 직접 토큰 (개발 환경에서 Gateway 없이 테스트할 때)
            logger.debug("NON_IAM service: Falling back to direct JWT validation")
            return await self._authenticate_iam_service(request)

    async def _get_user_with_cache(self, user_id: str) -> Optional[User]:
        """캐시 우선으로 사용자 조회, 미스 시 DB 조회 후 캐시 저장"""
        try:
            # 1) 캐시 조회
            cached = await self.user_cache.get_user(str(user_id))
            if cached:
                logger.debug(f"Cache HIT for user_id={user_id}")
                return cached

            logger.debug(f"Cache MISS for user_id={user_id} - querying DB")

            # 2) DB 조회
            from beanie import PydanticObjectId

            from .user_manager import UserManager

            user_manager = UserManager()
            user = await user_manager.get(PydanticObjectId(user_id))

            # 3) 캐시에 저장 (성공 시)
            if user:
                try:
                    await self.user_cache.set_user(user)
                except Exception as e:
                    logger.debug(f"Failed to set user in cache: {e}")
            return user

        except Exception as e:
            logger.debug(f"_get_user_with_cache error: {e}")
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
            logger.error(f"Unexpected authentication error: {error}")
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
            logger.debug(f"Skipping authentication for public path: {method} {path}")
            return await call_next(request)

        # 인증이 비활성화된 경우 건너뛰기
        if not self.service_config.enable_auth:
            logger.debug(
                f"Authentication disabled for service: {self.service_config.service_name}"
            )
            return await call_next(request)

        # 테스트 환경 인증 우회
        if self.auth_bypass:
            logger.debug(f"🧪 Auth bypass: injecting test user for {method} {path}")
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
                        f"Inactive user blocked: {user.id} at {method} {path}"
                    )
                    raise UserInactive(user_id=str(user.id))

                # Request.state에 사용자 정보 저장 (deps_new.py와 호환)
                request.state.user = user
                request.state.authenticated = True
                request.state.service_type = self.service_config.service_type

                logger.debug(
                    f"✅ User authenticated: {user.email} "
                    f"(ID: {user.id}, Verified: {user.is_verified}, "
                    f"Superuser: {user.is_superuser}) for {method} {path}"
                )
            else:
                # 인증 필요한 경로에서 사용자 정보 없음
                logger.warning(
                    f"❌ Authentication required for protected endpoint: {method} {path}"
                )
                raise UserNotExists(
                    identifier="user", identifier_type="authenticated user"
                )

        except (UserNotExists, InvalidToken, UserInactive, AuthorizationFailed) as e:
            logger.warning(
                f"🔒 Authentication failed for {method} {path}: {type(e).__name__} - {e}"
            )
            return self._create_error_response(e)

        except Exception as e:
            logger.error(
                f"💥 Unexpected authentication error for {method} {path}: {e}",
                exc_info=True,
            )
            return self._create_error_response(e)

        # 다음 미들웨어/핸들러 호출
        response = await call_next(request)

        # 응답 헤더에 사용자 정보 추가 (디버깅용, 프로덕션에서는 제거 권장)
        if hasattr(request.state, "user") and request.state.user:
            response.headers["X-Authenticated-User"] = str(request.state.user.id)

        return response

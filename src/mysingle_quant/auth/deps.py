"""
Authentication Dependencies v2 - Request-Based Unified Authentication

이 모듈은 AuthMiddleware와 완전히 통합된 새로운 Request 기반 인증 의존성 시스템입니다.
기존의 Depends() 패턴 대신 Request 파라미터를 직접 사용하여 미들웨어와 더 효율적으로 상호작
용합니다.
Key Features:
- Request 기반 인증 (Request.state.user 직접 활용)
- AuthMiddleware 완전 통합
- Kong Gateway 완전 지원 (헤더 기반 인증)
- User 캐싱 시스템 (Redis + In-Memory)
- 서비스 타입별 자동 인증 (IAM vs NON_IAM)
- 높은 성능 (캐시를 통한 DB 조회 최소화)
- 일관된 에러 처리

Usage Example:
    from fastapi import Request
    from mysingle_quant.auth.deps_new import get_current_active_verified_user

    @router.get("/protected")
    async def protected_endpoint(request: Request):
        user = get_current_active_verified_user(request)
        return {"user_id": str(user.id)}
"""

from typing import Optional

from fastapi import Request

from ..logging import get_logger
from .exceptions import AuthorizationFailed, UserInactive, UserNotExists
from .models import User

logger = get_logger(__name__)


# =============================================================================
# Kong Gateway Integration Helpers
# =============================================================================


def get_kong_user_id(request: Request) -> Optional[str]:
    """
    Kong Gateway에서 전달한 사용자 ID 추출

    Kong JWT Plugin이 JWT의 'sub' 클레임을 X-Consumer-Custom-ID 헤더로 전달합니다.
    (Kong 3.x 기준: JWT의 sub claim → X-Consumer-Custom-ID)

    헤더 우선순위:
    1. X-Consumer-Custom-ID (Kong 3.x 표준)
    2. X-User-Id (하위 호환성)

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: Kong에서 전달한 사용자 ID 또는 None
    """
    return (
        request.headers.get("x-consumer-custom-id")
        or request.headers.get("X-Consumer-Custom-ID")
        or request.headers.get("x-user-id")
        or request.headers.get("X-User-Id")
    )


def get_kong_consumer_id(request: Request) -> Optional[str]:
    """
    Kong Gateway Consumer ID 추출 (Kong 내부 Consumer ID)

    Kong이 인증한 Consumer의 ID를 X-Consumer-ID 헤더로 전달합니다.
    이는 Kong 내부 Consumer ID이며, 사용자 ID와는 다릅니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: Kong Consumer의 ID 또는 None
    """
    return request.headers.get("x-consumer-id") or request.headers.get("X-Consumer-ID")


def get_kong_consumer_username(request: Request) -> Optional[str]:
    """
    Kong Gateway Consumer Username 추출

    Kong이 인증한 Consumer의 username을 X-Consumer-Username 헤더로 전달합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: Kong Consumer의 username 또는 None
    """
    return request.headers.get("x-consumer-username") or request.headers.get(
        "X-Consumer-Username"
    )


def get_kong_forwarded_service(request: Request) -> Optional[str]:
    """
    Kong Gateway에서 전달한 서비스 식별자 추출

    Request Transformer Plugin이 설정한 X-Forwarded-Service 헤더를 반환합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: 전달된 서비스 이름 (예: "kong-gateway") 또는 None
    """
    return request.headers.get("x-forwarded-service") or request.headers.get(
        "X-Forwarded-Service"
    )


def is_kong_authenticated(request: Request) -> bool:
    """
    Kong Gateway를 통한 인증 여부 확인

    Returns:
        bool: Kong 헤더가 존재하면 True
    """
    return get_kong_user_id(request) is not None


def get_kong_headers_dict(request: Request) -> dict:
    """
    Kong Gateway에서 전달된 모든 인증 헤더를 dict로 반환

    디버깅 및 로깅 목적으로 사용합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        dict: Kong 인증 헤더 정보
            {
                "user_id": "507f1f77bcf86cd799439011",
                "consumer_id": "f7b1c3d4-5e6f-7890-ab12-3456789abcde",
                "consumer_username": "test_user@example.com",
                "forwarded_service": "kong-gateway",
                "is_authenticated": True
            }
    """
    return {
        "user_id": get_kong_user_id(request),
        "consumer_id": get_kong_consumer_id(request),
        "consumer_username": get_kong_consumer_username(request),
        "forwarded_service": get_kong_forwarded_service(request),
        "is_authenticated": is_kong_authenticated(request),
    }


# =============================================================================
# Core Request-Based Authentication Functions
# =============================================================================


def get_current_user(request: Request) -> User:
    """
    현재 인증된 사용자 반환 (Kong Gateway + AuthMiddleware 통합)

    인증 흐름:
    - Kong Gateway 헤더 (X-Consumer-Custom-ID) 확인
    - Kong JWT Plugin이 JWT를 검증하고 헤더 설정
    - AuthMiddleware가 헤더를 보고 DB에서 User 로드
    - request.state.user에서 User 반환

    보안 검증:
    - Kong 헤더의 user_id와 실제 User ID 일치 확인
    - AuthMiddleware가 User를 로드하지 못한 경우 UserNotExists 발생

    Args:
        request: FastAPI Request 객체

    Returns:
        User: 인증된 사용자 객체

    Raises:
        UserNotExists: 사용자 정보가 없는 경우 (미들웨어 인증 실패)

    Example:
        @router.get("/profile")
        async def get_profile(request: Request):
            user = get_current_user(request)
            return {"user_id": str(user.id)}
    """
    # AuthMiddleware가 이미 User를 로드함
    user: Optional[User] = getattr(request.state, "user", None)

    if not user:
        logger.warning("No user found in request.state - authentication failed")
        raise UserNotExists(identifier="user", identifier_type="authenticated user")

    # Type safety check
    if not isinstance(user, User):
        logger.error(f"Invalid user type in request.state: {type(user)}")
        raise UserNotExists(identifier="user", identifier_type="invalid_user_type")

    # Kong Gateway 보안 검증 (Kong 헤더가 있는 경우)
    kong_user_id = get_kong_user_id(request)
    if kong_user_id:
        kong_headers = get_kong_headers_dict(request)
        logger.debug(f"Kong authenticated request: {kong_headers}")

        # Kong user_id와 실제 User ID 일치 확인
        if str(user.id) != kong_user_id:
            logger.error(f"User ID mismatch: Kong={kong_user_id}, User={user.id}")
            raise UserNotExists(
                identifier=kong_user_id, identifier_type="user_id_mismatch"
            )

    return user


def get_current_active_user(request: Request) -> User:
    """
    활성 사용자 확인

    사용자가 활성 상태(is_active=True)인지 확인합니다.
    미들웨어에서 이미 기본 확인을 하지만, 추가 보안을 위해 재확인합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        User: 활성 사용자 객체

    Raises:
        UserInactive: 사용자가 비활성 상태인 경우

    Example:
        @router.post("/action")
        async def perform_action(request: Request):
            user = get_current_active_user(request)
            # 활성 사용자만 작업 수행 가능
            return perform_user_action(user)
    """
    user = get_current_user(request)
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user.id}")
        raise UserInactive(user_id=str(user.id))
    return user


def get_current_active_verified_user(request: Request) -> User:
    """
    이메일 검증된 활성 사용자 확인

    사용자가 활성 상태이면서 이메일 인증(is_verified=True)을 완료했는지 확인합니다.
    이메일 인증이 필요한 기능에 사용합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        User: 이메일 검증된 활성 사용자 객체

    Raises:
        AuthorizationFailed: 이메일 인증이 완료되지 않은 경우

    Example:
        @router.post("/sensitive-action")
        async def sensitive_action(request: Request):
            user = get_current_active_verified_user(request)
            # 이메일 검증된 사용자만 민감한 작업 수행 가능
            return perform_sensitive_action(user)
    """
    user = get_current_active_user(request)
    if not user.is_verified:
        logger.warning(f"Unverified user attempted access: {user.id}")
        raise AuthorizationFailed("Email verification required", user_id=str(user.id))
    return user


def get_current_active_superuser(request: Request) -> User:
    """
    슈퍼유저 권한 검증

    사용자가 슈퍼유저 권한(is_superuser=True)을 가지고 있는지 확인합니다.
    관리자 권한이 필요한 기능에 사용합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        User: 슈퍼유저 권한을 가진 사용자 객체

    Raises:
        AuthorizationFailed: 슈퍼유저 권한이 없는 경우

    Example:
        @router.delete("/admin/users/{user_id}")
        async def delete_user(request: Request, user_id: str):
            admin_user = get_current_active_superuser(request)
            # 슈퍼유저만 다른 사용자 삭제 가능
            return delete_user_by_admin(user_id, admin_user)
    """
    user = get_current_active_verified_user(request)
    if not user.is_superuser:
        logger.warning(f"Non-superuser attempted admin access: {user.id}")
        raise AuthorizationFailed("Superuser privileges required", user_id=str(user.id))
    return user


def get_current_user_optional(request: Request) -> Optional[User]:
    """
    선택적 사용자 인증 (공개 경로 또는 선택적 인증용)

    사용자가 로그인했으면 User 객체 반환, 아니면 None을 반환합니다.
    공개 경로나 선택적 인증이 필요한 엔드포인트에서 사용합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[User]: 인증된 사용자 객체 또는 None

    Example:
        @router.get("/public-content")
        async def public_content(request: Request):
            user = get_current_user_optional(request)
            if user:
                # 로그인된 사용자에게는 개인화된 콘텐츠
                return get_personalized_content(user)
            else:
                # 비로그인 사용자에게는 기본 콘텐츠
                return get_default_content()
    """
    return getattr(request.state, "user", None)


# =============================================================================
# Role-Based Access Control Functions
# =============================================================================


def require_user_role(request: Request, required_roles: list[str]) -> User:
    """
    특정 역할이 필요한 사용자 검증

    사용자에게 특정 역할이 있는지 확인합니다.
    현재는 is_superuser만 지원하지만, 향후 role 시스템 확장 시 사용됩니다.

    Args:
        request: FastAPI Request 객체
        required_roles: 필요한 역할 목록

    Returns:
        User: 역할 요구사항을 만족하는 사용자 객체

    Raises:
        AuthorizationFailed: 필요한 역할이 없는 경우

    Example:
        @router.get("/admin-only")
        async def admin_endpoint(request: Request):
            user = require_user_role(request, ["admin", "superuser"])
            return {"message": "Admin access", "user": str(user.id)}
    """
    user = get_current_active_verified_user(request)

    # 현재는 superuser만 지원
    # if "admin" in required_roles or "superuser" in required_roles:
    #     if not user.is_superuser:
    #         logger.warning(f"User {user.id} lacks required roles: {required_roles}")
    #         raise AuthorizationFailed(
    #             f"Required roles: {required_roles}", user_id=str(user.id)
    #         )

    # 향후 확장: user.roles 필드 체크
    # user_roles = getattr(user, 'roles', [])
    # if not any(role in user_roles for role in required_roles):
    #     raise AuthorizationFailed(
    #         f"Required roles: {required_roles}", user_id=str(user.id)
    #     )

    return user


def require_admin_access(request: Request) -> User:
    """
    관리자 권한 요구 (편의 함수)

    Args:
        request: FastAPI Request 객체

    Returns:
        User: 관리자 권한을 가진 사용자 객체

    Example:
        @router.get("/admin/dashboard")
        async def admin_dashboard(request: Request):
            admin_user = require_admin_access(request)
            return get_admin_dashboard_data(admin_user)
    """
    return require_user_role(request, ["admin", "superuser"])


# =============================================================================
# Utility Functions
# =============================================================================


def is_user_authenticated(request: Request) -> bool:
    """
    사용자가 인증되었는지 확인하는 유틸리티 함수

    Args:
        request: FastAPI Request 객체

    Returns:
        bool: 인증 여부

    Example:
        @router.get("/conditional")
        async def conditional_endpoint(request: Request):
            if is_user_authenticated(request):
                return {"message": "Welcome back!"}
            else:
                return {"message": "Hello, guest!"}
    """
    return hasattr(request.state, "user") and request.state.user is not None


def get_user_id(request: Request) -> Optional[str]:
    """
    인증된 사용자의 ID를 반환하는 유틸리티 함수

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: 사용자 ID 또는 None

    Example:
        @router.get("/activity")
        async def track_activity(request: Request):
            user_id = get_user_id(request)
            if user_id:
                track_user_activity(user_id, "page_view")
            return {"status": "tracked"}
    """
    user = getattr(request.state, "user", None)
    return str(user.id) if user else None


def get_user_email(request: Request) -> Optional[str]:
    """
    인증된 사용자의 이메일을 반환하는 유틸리티 함수

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: 사용자 이메일 또는 None

    Example:
        @router.post("/newsletter")
        async def subscribe_newsletter(request: Request):
            user_email = get_user_email(request)
            if user_email:
                return subscribe_user_to_newsletter(user_email)
            else:
                return {"error": "Authentication required"}
    """
    user = getattr(request.state, "user", None)
    if not user:
        return None
    return user.email if user else None


def get_user_display_name(request: Request) -> Optional[str]:
    """
    인증된 사용자의 표시 이름을 반환하는 유틸리티 함수

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: 사용자 표시 이름 또는 None

    Example:
        @router.get("/welcome")
        async def welcome_message(request: Request):
            display_name = get_user_display_name(request)
            if display_name:
                return {"message": f"Welcome, {display_name}!"}
            else:
                return {"message": "Welcome, guest!"}
    """
    user: Optional[User] = getattr(request.state, "user", None)
    if not user:
        return None

    # Type guard
    if not isinstance(user, User):
        return None

    # 표시 이름 우선순위: full_name → email → user_id
    if hasattr(user, "full_name") and user.full_name:
        return str(user.full_name)
    elif user.email:
        return str(user.email).split("@")[0]  # 이메일의 @ 앞부분
    else:
        return f"User {str(user.id)[:8]}"  # ID의 앞 8자리


# =============================================================================
# Security Context Helpers
# =============================================================================


def get_request_security_context(request: Request) -> dict:
    """
    요청의 보안 컨텍스트 정보를 반환

    Args:
        request: FastAPI Request 객체

    Returns:
        dict: 보안 컨텍스트 정보

    Example:
        @router.post("/sensitive-action")
        async def sensitive_action(request: Request):
            user = get_current_active_verified_user(request)
            security_context = get_request_security_context(request)

            # 보안 감사 로그
            logger.info(f"Sensitive action by user {user.id}", extra=security_context)

            return perform_action(user)
    """
    user = getattr(request.state, "user", None)

    context = {
        "authenticated": user is not None,
        "user_id": str(user.id) if user else None,
        "user_email": user.email if user else None,
        "is_active": user.is_active if user else False,
        "is_verified": user.is_verified if user else False,
        "is_superuser": user.is_superuser if user else False,
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "endpoint": f"{request.method} {request.url.path}",
    }

    return context


# =============================================================================
# Convenience Aliases
# =============================================================================

# 자주 사용되는 함수들의 간단한 별칭
get_authenticated_user = get_current_user
get_active_user = get_current_active_user
get_verified_user = get_current_active_verified_user
get_admin_user = get_current_active_superuser
get_optional_user = get_current_user_optional

# 유틸리티 별칭
check_authentication = is_user_authenticated
extract_user_id = get_user_id
extract_user_email = get_user_email


# =============================================================================
# FastAPI Depends() Compatibility Wrappers
# =============================================================================

"""
기존 Depends() 패턴과의 호환성을 위한 래퍼 함수들

이 함수들은 기존 코드에서 Depends() 패턴을 사용하는 경우의 호환성을 제공합니다.
새로운 코드에서는 Request 기반 함수를 직접 사용하는 것을 권장합니다.

Example:
    # 기존 방식 (호환성 유지)
    @router.get("/")
    async def endpoint(user: User = Depends(get_current_active_user_deps)):
        return {"user_id": str(user.id)}

    # 권장 방식 (새로운 코드)
    @router.get("/")
    async def endpoint(request: Request):
        user = get_current_active_user(request)
        return {"user_id": str(user.id)}
"""

from fastapi import Depends


def get_current_user_deps(request: Request = Depends()) -> User:
    """
    Depends() 패턴용 래퍼 - 현재 인증된 사용자 반환

    Args:
        request: FastAPI Request 객체 (Depends를 통해 자동 주입)

    Returns:
        User: 인증된 사용자 객체

    Raises:
        UserNotExists: 사용자 정보가 없는 경우
    """
    return get_current_user(request)


def get_current_active_user_deps(request: Request = Depends()) -> User:
    """
    Depends() 패턴용 래퍼 - 현재 활성 사용자 반환

    Args:
        request: FastAPI Request 객체 (Depends를 통해 자동 주입)

    Returns:
        User: 활성 사용자 객체

    Raises:
        UserNotExists: 사용자 정보가 없는 경우
        UserInactive: 비활성 사용자인 경우
    """
    return get_current_active_user(request)


def get_current_active_verified_user_deps(request: Request = Depends()) -> User:
    """
    Depends() 패턴용 래퍼 - 현재 활성 검증된 사용자 반환

    Args:
        request: FastAPI Request 객체 (Depends를 통해 자동 주입)

    Returns:
        User: 활성 검증된 사용자 객체

    Raises:
        UserNotExists: 사용자 정보가 없는 경우
        UserInactive: 비활성 사용자인 경우
        AuthorizationFailed: 미검증 사용자인 경우
    """
    return get_current_active_verified_user(request)


def get_current_active_superuser_deps(request: Request = Depends()) -> User:
    """
    Depends() 패턴용 래퍼 - 현재 활성 슈퍼유저 반환

    Args:
        request: FastAPI Request 객체 (Depends를 통해 자동 주입)

    Returns:
        User: 활성 슈퍼유저 객체

    Raises:
        UserNotExists: 사용자 정보가 없는 경우
        UserInactive: 비활성 사용자인 경우
        AuthorizationFailed: 권한이 부족한 경우
    """
    return get_current_active_superuser(request)


def get_current_user_optional_deps(request: Request = Depends()) -> Optional[User]:
    """
    Depends() 패턴용 래퍼 - 현재 사용자 반환 (선택적)

    Args:
        request: FastAPI Request 객체 (Depends를 통해 자동 주입)

    Returns:
        Optional[User]: 인증된 사용자 객체 또는 None
    """
    return get_current_user_optional(request)


# =============================================================================
# Kong Gateway 헤더 표준화 확장
# =============================================================================


def get_kong_correlation_id(request: Request) -> Optional[str]:
    """
    Kong Gateway에서 전달한 Correlation ID 추출

    Kong Request Transformer Plugin이 설정한 X-Correlation-Id 또는
    Correlation-Id 헤더를 반환합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: Correlation ID 또는 None
    """
    return (
        request.headers.get("x-correlation-id")
        or request.headers.get("X-Correlation-Id")
        or request.headers.get("correlation-id")
        or request.headers.get("Correlation-Id")
    )


def get_kong_request_id(request: Request) -> Optional[str]:
    """
    Kong Gateway에서 생성한 Request ID 추출

    Kong이 각 요청에 대해 생성한 고유 ID를 X-Kong-Request-Id 헤더로 전달합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: Kong Request ID 또는 None
    """
    return (
        request.headers.get("x-kong-request-id")
        or request.headers.get("X-Kong-Request-Id")
        or request.headers.get("x-request-id")
        or request.headers.get("X-Request-Id")
    )


def get_kong_upstream_latency(request: Request) -> Optional[str]:
    """
    Kong Gateway에서 측정한 업스트림 지연시간 추출

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: 업스트림 지연시간 (밀리초) 또는 None
    """
    return request.headers.get("x-kong-upstream-latency") or request.headers.get(
        "X-Kong-Upstream-Latency"
    )


def get_kong_proxy_latency(request: Request) -> Optional[str]:
    """
    Kong Gateway에서 측정한 프록시 지연시간 추출

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: 프록시 지연시간 (밀리초) 또는 None
    """
    return request.headers.get("x-kong-proxy-latency") or request.headers.get(
        "X-Kong-Proxy-Latency"
    )


def get_extended_kong_headers_dict(request: Request) -> dict:
    """
    Kong Gateway에서 전달된 모든 헤더를 포함한 확장된 dict 반환

    기본 인증 헤더 + 추가 운영 헤더들을 포함합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        dict: 확장된 Kong 헤더 정보
    """
    base_headers = get_kong_headers_dict(request)

    extended_headers = {
        **base_headers,
        "correlation_id": get_kong_correlation_id(request),
        "request_id": get_kong_request_id(request),
        "upstream_latency": get_kong_upstream_latency(request),
        "proxy_latency": get_kong_proxy_latency(request),
    }

    return extended_headers

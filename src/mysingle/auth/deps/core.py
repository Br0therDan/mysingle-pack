from typing import Optional

from fastapi import Request

from ...logging import get_structured_logger
from ..exceptions import AuthorizationFailed, UserInactive, UserNotExists
from ..models import User
from .kong import get_kong_headers_dict, get_kong_user_id

logger = get_structured_logger(__name__)


def get_current_user(request: Request) -> User:
    """
    현재 인증된 사용자 반환 (Kong Gateway + AuthMiddleware 통합)
    """
    user: Optional[User] = getattr(request.state, "user", None)

    if not user:
        logger.warning("No user found in request.state - authentication failed")
        raise UserNotExists(identifier="user", identifier_type="authenticated user")

    if not isinstance(user, User):
        logger.error(f"Invalid user type in request.state: {type(user)}")
        raise UserNotExists(identifier="user", identifier_type="invalid_user_type")

    # Kong Gateway 보안 검증 (헤더가 있으면 교차 확인)
    kong_user_id = get_kong_user_id(request)
    if kong_user_id:
        kong_headers = get_kong_headers_dict(request)
        logger.debug(f"Kong authenticated request: {kong_headers}")
        if str(user.id) != kong_user_id:
            logger.error(f"User ID mismatch: Kong={kong_user_id}, User={user.id}")
            raise UserNotExists(
                identifier=kong_user_id, identifier_type="user_id_mismatch"
            )

    return user


def get_current_active_user(request: Request) -> User:
    """활성 사용자 (is_active) 보장"""
    user = get_current_user(request)
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user.id}")
        raise UserInactive(user_id=str(user.id))
    return user


def get_current_active_verified_user(request: Request) -> User:
    """활성 + 이메일 검증 사용자 보장"""
    user = get_current_active_user(request)
    if not user.is_verified:
        logger.warning(f"Unverified user attempted access: {user.id}")
        raise AuthorizationFailed("Email verification required", user_id=str(user.id))
    return user


def get_current_active_superuser(request: Request) -> User:
    """슈퍼유저 보장"""
    user = get_current_active_verified_user(request)
    if not user.is_superuser:
        logger.warning(f"Non-superuser attempted admin access: {user.id}")
        raise AuthorizationFailed("Superuser privileges required", user_id=str(user.id))
    return user


def get_current_user_optional(request: Request) -> Optional[User]:
    """선택적 인증: 없으면 None"""
    return getattr(request.state, "user", None)


def is_user_authenticated(request: Request) -> bool:
    """사용자 인증 여부"""
    return hasattr(request.state, "user") and request.state.user is not None


def get_user_id(request: Request) -> Optional[str]:
    """사용자 ID 반환"""
    user = getattr(request.state, "user", None)
    return str(user.id) if user else None


def get_user_email(request: Request) -> Optional[str]:
    """사용자 이메일 반환"""
    user = getattr(request.state, "user", None)
    if not user:
        return None
    return user.email if user else None


def get_user_display_name(request: Request) -> Optional[str]:
    """표시 이름 반환: full_name → email 앞부분 → id prefix"""
    user: Optional[User] = getattr(request.state, "user", None)
    if not user or not isinstance(user, User):
        return None

    if hasattr(user, "full_name") and user.full_name:
        return str(user.full_name)
    elif user.email:
        return str(user.email).split("@")[0]
    else:
        return f"User {str(user.id)[:8]}"


def get_request_security_context(request: Request) -> dict:
    """요청 보안 컨텍스트 반환"""
    user = getattr(request.state, "user", None)
    return {
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

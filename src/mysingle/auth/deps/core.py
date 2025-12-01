from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status

from ...core.logging import get_structured_logger
from ..models import User
from .kong import (
    get_kong_correlation_id,
    get_kong_request_id,
    get_kong_user_id,
)

logger = get_structured_logger(__name__)


def get_current_user(request: Request) -> User:
    """
    현재 인증된 사용자 반환 (Kong Gateway + AuthMiddleware 통합)
    """
    user: Optional[User] = getattr(request.state, "user", None)

    if not user:
        logger.warning("No user found in request.state - authentication failed")
        # 인증 실패는 서버 에러(500)가 아닌 401을 반환해야 함
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    if not isinstance(user, User):
        logger.error(f"Invalid user type in request.state: {type(user)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication context",
        )

    # Kong Gateway 보안 검증 (헤더가 있으면 교차 확인)
    # Kong의 pre-function 플러그인이 JWT의 sub 클레임을 X-User-Id로 추출하여 전달
    kong_user_id = get_kong_user_id(request)
    if kong_user_id:
        # ObjectId 형식인지 확인 (24자 hex 문자열)
        is_object_id = len(kong_user_id) == 24 and all(
            c in "0123456789abcdef" for c in kong_user_id.lower()
        )

        if is_object_id:
            # Kong에서 추출한 사용자 ID와 JWT 토큰에서 추출한 사용자 ID 일치 확인
            if str(user.id) != kong_user_id:
                logger.error(f"User ID mismatch: Kong={kong_user_id}, User={user.id}")
                # 보안상 불일치는 인증 실패로 간주하여 401 반환
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication user mismatch",
                )
            logger.debug(f"Kong user ID validation passed: {kong_user_id}")
        else:
            # Legacy: Consumer 이름인 경우 (구 Kong 설정 호환성)
            logger.debug(
                f"Kong X-User-Id is Consumer name (legacy): {kong_user_id}, authenticated user: {user.id}"
            )

    return user


def get_current_active_user(request: Request) -> User:
    """활성 사용자 (is_active) 보장"""
    user = get_current_user(request)
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user.id}")
        # 비활성 사용자는 인가 실패로 403 반환
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    return user


def get_current_active_verified_user(request: Request) -> User:
    """활성 + 이메일 검증 사용자 보장"""
    user = get_current_active_user(request)
    if not user.is_verified:
        logger.warning(f"Unverified user attempted access: {user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        )
    return user


def get_current_active_superuser(request: Request) -> User:
    """슈퍼유저 보장"""
    user = get_current_active_verified_user(request)
    if not user.is_superuser:
        logger.warning(f"Non-superuser attempted admin access: {user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required",
        )
    return user


def get_current_user_optional(request: Request) -> Optional[User]:
    """선택적 인증: 없으면 None (타입 보장)"""
    user = getattr(request.state, "user", None)
    return user if isinstance(user, User) else None


def is_user_authenticated(request: Request) -> bool:
    """사용자 인증 여부"""
    return isinstance(getattr(request.state, "user", None), User)


def get_user_id(request: Request) -> Optional[str]:
    """사용자 ID 반환"""
    user = getattr(request.state, "user", None)
    return str(user.id) if user else None


def get_user_email(request: Request) -> Optional[str]:
    """사용자 이메일 반환"""
    user = get_current_user_optional(request)
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


def get_request_security_context(request: Request) -> Dict[str, Any]:
    """요청 보안 컨텍스트 반환 (Kong 트레이싱 일부 포함)"""
    user = get_current_user_optional(request)
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
        "correlation_id": get_kong_correlation_id(request),
        "request_id": get_kong_request_id(request),
    }

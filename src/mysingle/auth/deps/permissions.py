from typing import List

from fastapi import Request

from mysingle.auth.exceptions import AuthorizationFailed
from mysingle.auth.models import User
from mysingle.core.logging import get_structured_logger

from .core import get_current_active_verified_user

logger = get_structured_logger(__name__)


def require_user_role(request: Request, required_roles: List[str]) -> User:
    """역할 요구: 현재는 superuser 중심, 향후 확장 가능"""
    user = get_current_active_verified_user(request)

    # 간단한 관리자 권한 체크 (role 시스템 확장 전까지)
    if (
        any(role in ("admin", "superuser") for role in required_roles)
        and not user.is_superuser
    ):
        logger.warning(f"User {user.id} lacks required roles: {required_roles}")
        raise AuthorizationFailed(
            f"Required roles: {required_roles}", user_id=str(user.id)
        )

    return user


def require_admin_access(request: Request) -> User:
    """관리자 권한 편의 함수"""
    return require_user_role(request, ["admin", "superuser"])

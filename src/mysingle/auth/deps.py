"""
Kong Gateway 기반 인증 의존성 (경량화 - SIMPLIFIED)

Request.state에서 Kong Gateway가 주입한 사용자 정보를 추출합니다.

IMPORTANT:
- is_active, is_verified는 IAM 로그인 시 이미 검증됨
- 로그인 성공한 사용자 = is_active=true AND is_verified=true 보장
- 따라서 불필요한 검증 함수들은 제거
"""

from typing import Optional

from fastapi import HTTPException, Request, status

from mysingle.constants import (
    HEADER_CORRELATION_ID,
    HEADER_KONG_REQUEST_ID,
)
from mysingle.core.logging import get_structured_logger

logger = get_structured_logger(__name__)


# ========================================
# Core Authentication Functions
# ========================================


def get_user_id(request: Request) -> str:
    """
    현재 인증된 사용자 ID 반환

    Kong Gateway가 X-User-Id 헤더를 통해 전달한 사용자 ID를 반환합니다.
    인증되지 않은 경우 401 에러를 발생시킵니다.

    Returns:
        str: User ID (MongoDB ObjectId as string)

    Raises:
        HTTPException: 인증되지 않은 경우 401
    """
    user_id: Optional[str] = getattr(request.state, "user_id", None)

    if not user_id:
        logger.warning("No user_id in request.state - authentication required")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return user_id


def get_user_id_optional(request: Request) -> Optional[str]:
    """
    선택적 사용자 ID 반환 (인증되지 않은 경우 None)

    공개 API에서 사용자가 로그인했는지 선택적으로 확인할 때 사용합니다.

    Returns:
        Optional[str]: User ID 또는 None
    """
    return getattr(request.state, "user_id", None)


def get_user_email(request: Request) -> Optional[str]:
    """
    사용자 이메일 반환

    Returns:
        Optional[str]: Email 또는 None
    """
    return getattr(request.state, "email", None)


# ========================================
# Kong Header Utilities
# ========================================


def _get_header(request: Request, key: str) -> Optional[str]:
    """Case-insensitive, trimmed header getter.

    Starlette's Headers mapping is case-insensitive, so we can use a single
    canonical lowercase key. Returns None for missing or empty values.
    """
    val = request.headers.get(key)
    if val is None:
        return None
    val = val.strip()
    return val or None


def get_correlation_id(request: Request) -> Optional[str]:
    """
    Correlation ID 추출

    X-Correlation-Id 헤더를 우선 사용하며, 없으면 대체 헤더 확인
    """
    return _get_header(request, HEADER_CORRELATION_ID.lower()) or _get_header(
        request, "correlation-id"
    )


def get_request_id(request: Request) -> Optional[str]:
    """
    Kong Request ID 추출

    X-Kong-Request-Id 헤더를 우선 사용하며, 없으면 대체 헤더 확인
    """
    return _get_header(request, HEADER_KONG_REQUEST_ID.lower()) or _get_header(
        request, "x-request-id"
    )


# ========================================
# Request Context Utilities
# ========================================


def get_request_security_context(request: Request) -> dict:
    """
    요청 보안 컨텍스트 반환 (로깅/모니터링용)

    Returns:
        dict: 보안 컨텍스트 정보
    """
    return {
        "authenticated": get_user_id_optional(request) is not None,
        "user_id": get_user_id_optional(request),
        "email": get_user_email(request),
        "is_superuser": getattr(request.state, "is_superuser", False),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "endpoint": f"{request.method} {request.url.path}",
        "correlation_id": get_correlation_id(request),
        "request_id": get_request_id(request),
    }


def get_user_display_name(request: Request) -> Optional[str]:
    """
    표시 이름 반환 (로깅/UI용)

    Returns:
        Optional[str]: Email 앞부분 또는 user_id prefix
    """
    email = get_user_email(request)
    if email:
        return email.split("@")[0]

    user_id = get_user_id_optional(request)
    if user_id:
        return f"User {user_id[:8]}"

    return None

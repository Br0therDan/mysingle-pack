"""
mysingle_quant.auth - Authentication & Authorization Module

Public API for microservices authentication with Kong Gateway support.
"""

from .deps import (
    # Admin authentication
    get_current_active_superuser,
    get_current_active_user,
    # Primary authentication functions (권장)
    get_current_active_verified_user,
    get_current_user,
    get_current_user_optional,
    # Kong Gateway integration
    get_kong_headers_dict,
    get_kong_user_id,
    is_kong_authenticated,
)
from .middleware import AuthMiddleware
from .models import User

__all__ = [
    # ==========================================
    # Core Authentication (Most Used)
    # ==========================================
    "get_current_user",  # 기본 인증 (활성 여부 체크 안 함)
    "get_current_active_user",  # 활성 사용자 (is_active=True)
    "get_current_active_verified_user",  # 이메일 검증된 사용자 (권장)
    "get_current_user_optional",  # 선택적 인증 (공개 API용)
    # ==========================================
    # Admin Authentication
    # ==========================================
    "get_current_active_superuser",  # 관리자 권한 필요
    # ==========================================
    # Kong Gateway Integration
    # ==========================================
    "get_kong_user_id",  # Kong 헤더에서 user_id 추출
    "get_kong_headers_dict",  # Kong 헤더 전체 정보 (디버깅용)
    "is_kong_authenticated",  # Kong 헤더 존재 여부 확인
    # ==========================================
    # Core Components
    # ==========================================
    "User",  # User 모델
    "AuthMiddleware",  # 인증 미들웨어
]

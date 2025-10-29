"""
JWT Token Management - Unified System

Kong Gateway와 통합된 JWT 토큰 관리 시스템입니다.
- 토큰 생성 (로그인 시)
- 토큰 검증
- 토큰 디코딩
- 서비스 간 통신용 토큰 생성

Usage Example:
    from mysingle_quant.auth.security.jwt import get_jwt_manager

    # 사용자 로그인 토큰 생성
    jwt_manager = get_jwt_manager()
    token = jwt_manager.create_user_token(
        user_id="507f1f77bcf86cd799439011",
        email="user@example.com",
        is_verified=True,
        is_superuser=False
    )

    # 토큰 검증
    payload = jwt_manager.decode_token(token)
"""

from datetime import UTC, datetime, timedelta
from typing import Any, Optional

import jwt

from ...core.config import CommonSettings
from ...logging import get_logger

logger = get_logger(__name__)


class JWTManager:
    """
    JWT Token 관리 클래스

    Kong Gateway와 호환되는 JWT 토큰을 생성하고 검증합니다.
    """

    def __init__(self, settings: Optional[CommonSettings] = None):
        """
        JWTManager 초기화

        Args:
            settings: CommonSettings 인스턴스 (None이면 자동 생성)
        """
        self.settings = settings or CommonSettings()

        # JWT 설정
        self.algorithm = "HS256"
        self.access_token_expire_hours = 24  # 24시간
        self.service_token_expire_minutes = 5  # 서비스 토큰은 5분

        # Kong Consumer Keys
        self.frontend_consumer_key = "frontend-key"
        self.service_consumer_keys = {
            "strategy-service": "strategy-service-key",
            "market-data-service": "market-data-service-key",
            "genai-service": "genai-service-key",
            "ml-service": "ml-service-key",
        }

    def create_user_token(
        self,
        user_id: str,
        email: str,
        is_verified: bool = False,
        is_superuser: bool = False,
        is_active: bool = True,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        사용자 로그인용 JWT 토큰 생성

        Args:
            user_id: 사용자 ID (MongoDB ObjectId string)
            email: 사용자 이메일
            is_verified: 이메일 인증 여부
            is_superuser: 관리자 여부
            is_active: 활성 사용자 여부
            expires_delta: 만료 시간 (None이면 24시간)

        Returns:
            str: JWT 토큰
        """
        if expires_delta is None:
            expires_delta = timedelta(hours=self.access_token_expire_hours)

        now = datetime.now(UTC)
        expire = now + expires_delta

        payload = {
            # JWT 표준 클레임
            "iss": self.frontend_consumer_key,  # Issuer (Kong Consumer Key)
            "sub": user_id,  # Subject (User ID)
            "exp": expire,  # Expiration Time
            "iat": now,  # Issued At
            # 커스텀 클레임 (사용자 정보)
            "email": email,
            "is_verified": is_verified,
            "is_superuser": is_superuser,
            "is_active": is_active,
        }

        # JWT Secret (환경변수에서 가져옴)
        secret = self._get_jwt_secret_for_consumer(self.frontend_consumer_key)

        try:
            token = jwt.encode(payload, secret, algorithm=self.algorithm)
            logger.debug(
                f"Created user token for user_id={user_id}, expires_at={expire}"
            )
            return token
        except Exception as e:
            logger.error(f"Failed to create user token: {e}")
            raise

    def create_service_token(
        self,
        service_name: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        서비스 간 통신용 JWT 토큰 생성

        Args:
            service_name: 서비스 이름 (strategy-service, market-data-service 등)
            expires_delta: 만료 시간 (None이면 5분)

        Returns:
            str: JWT 토큰
        """
        if service_name not in self.service_consumer_keys:
            raise ValueError(
                f"Unknown service: {service_name}. "
                f"Valid services: {list(self.service_consumer_keys.keys())}"
            )

        if expires_delta is None:
            expires_delta = timedelta(minutes=self.service_token_expire_minutes)

        now = datetime.now(UTC)
        expire = now + expires_delta

        consumer_key = self.service_consumer_keys[service_name]

        payload = {
            # JWT 표준 클레임
            "iss": consumer_key,  # Issuer (Service Consumer Key)
            "sub": "service-account",  # Subject (Service Account)
            "exp": expire,  # Expiration Time
            "iat": now,  # Issued At
            # 커스텀 클레임 (서비스 정보)
            "service": service_name,
            "type": "service-to-service",
        }

        # JWT Secret (서비스별 Secret)
        secret = self._get_jwt_secret_for_consumer(consumer_key)

        try:
            token = jwt.encode(payload, secret, algorithm=self.algorithm)
            logger.debug(
                f"Created service token for {service_name}, expires_at={expire}"
            )
            return token
        except Exception as e:
            logger.error(f"Failed to create service token: {e}")
            raise

    def decode_token(
        self,
        token: str,
        verify: bool = True,
    ) -> dict[str, Any]:
        """
        JWT 토큰 디코딩 및 검증

        Args:
            token: JWT 토큰
            verify: 서명 검증 여부 (False는 디버깅용)

        Returns:
            dict: JWT Payload

        Raises:
            jwt.ExpiredSignatureError: 토큰 만료
            jwt.InvalidTokenError: 유효하지 않은 토큰
        """
        try:
            if verify:
                # iss 클레임으로 Consumer 식별
                unverified_payload = jwt.decode(
                    token, options={"verify_signature": False}
                )
                consumer_key = unverified_payload.get("iss")

                if not consumer_key:
                    raise jwt.InvalidTokenError("Missing 'iss' claim")

                secret = self._get_jwt_secret_for_consumer(consumer_key)

                # 서명 검증
                payload = jwt.decode(
                    token,
                    secret,
                    algorithms=[self.algorithm],
                    options={"verify_exp": True},
                )
            else:
                # 검증 없이 디코딩 (디버깅용)
                payload = jwt.decode(token, options={"verify_signature": False})

            return dict(payload)

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            raise

    def verify_token(self, token: str) -> bool:
        """
        토큰 유효성 간단 검증

        Args:
            token: JWT 토큰

        Returns:
            bool: 유효하면 True, 아니면 False
        """
        try:
            self.decode_token(token, verify=True)
            return True
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return False

    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """
        토큰 만료 시간 조회

        Args:
            token: JWT 토큰

        Returns:
            Optional[datetime]: 만료 시간 (UTC)
        """
        try:
            payload = self.decode_token(token, verify=False)
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp, tz=UTC)
            return None
        except Exception as e:
            logger.error(f"Failed to get token expiry: {e}")
            return None

    def is_token_expired(self, token: str) -> bool:
        """
        토큰 만료 여부 확인

        Args:
            token: JWT 토큰

        Returns:
            bool: 만료되었으면 True
        """
        expiry = self.get_token_expiry(token)
        if expiry is None:
            return True
        return datetime.now(UTC) > expiry

    def _get_jwt_secret_for_consumer(self, consumer_key: str) -> str:
        """
        Consumer Key에 해당하는 JWT Secret 조회

        Args:
            consumer_key: Kong Consumer Key

        Returns:
            str: JWT Secret

        Raises:
            ValueError: Secret이 설정되지 않은 경우
        """
        # 환경변수 이름 매핑
        secret_env_map = {
            "frontend-key": "KONG_JWT_SECRET_FRONTEND",
            "strategy-service-key": "KONG_JWT_SECRET_STRATEGY",
            "market-data-service-key": "KONG_JWT_SECRET_MARKET_DATA",
            "genai-service-key": "KONG_JWT_SECRET_GENAI",
            "ml-service-key": "KONG_JWT_SECRET_ML",
        }

        env_var = secret_env_map.get(consumer_key)
        if not env_var:
            raise ValueError(f"Unknown consumer key: {consumer_key}")

        secret = getattr(self.settings, env_var, None)
        if not secret:
            # 개발 환경 fallback
            logger.warning(
                f"JWT secret not found in environment variable {env_var}, "
                f"using SECRET_KEY as fallback"
            )
            return self.settings.SECRET_KEY

        return str(secret)

    def extract_user_id_from_token(self, token: str) -> Optional[str]:
        """
        토큰에서 User ID 추출 (편의 함수)

        Args:
            token: JWT 토큰

        Returns:
            Optional[str]: User ID
        """
        try:
            payload = self.decode_token(token, verify=False)
            return payload.get("sub")
        except Exception:
            return None

    def extract_user_email_from_token(self, token: str) -> Optional[str]:
        """
        토큰에서 이메일 추출 (편의 함수)

        Args:
            token: JWT 토큰

        Returns:
            Optional[str]: 이메일
        """
        try:
            payload = self.decode_token(token, verify=False)
            return payload.get("email")
        except Exception:
            return None


# =============================================================================
# Singleton Instance & Convenience Functions
# =============================================================================

# 전역 JWTManager 인스턴스 (싱글톤 패턴)
_jwt_manager_instance: Optional[JWTManager] = None


def get_jwt_manager() -> JWTManager:
    """
    JWTManager 싱글톤 인스턴스 반환

    Returns:
        JWTManager: JWTManager 인스턴스
    """
    global _jwt_manager_instance
    if _jwt_manager_instance is None:
        _jwt_manager_instance = JWTManager()
    return _jwt_manager_instance


def create_access_token(
    user_id: str,
    email: str,
    is_verified: bool = False,
    is_superuser: bool = False,
) -> str:
    """
    사용자 액세스 토큰 생성 (편의 함수)

    Args:
        user_id: 사용자 ID
        email: 이메일
        is_verified: 이메일 인증 여부
        is_superuser: 관리자 여부

    Returns:
        str: JWT 토큰
    """
    jwt_manager = get_jwt_manager()
    return jwt_manager.create_user_token(
        user_id=user_id, email=email, is_verified=is_verified, is_superuser=is_superuser
    )


def verify_access_token(token: str) -> bool:
    """
    액세스 토큰 검증 (편의 함수)

    Args:
        token: JWT 토큰

    Returns:
        bool: 유효하면 True
    """
    jwt_manager = get_jwt_manager()
    return jwt_manager.verify_token(token)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    액세스 토큰 디코딩 (편의 함수)

    Args:
        token: JWT 토큰

    Returns:
        dict: JWT Payload
    """
    jwt_manager = get_jwt_manager()
    return jwt_manager.decode_token(token)

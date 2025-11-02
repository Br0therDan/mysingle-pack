from typing import Any, Literal, Union

from fastapi import HTTPException
from fastapi.responses import Response
from pydantic import SecretStr

from ..core.config import settings
from ..logging import get_structured_logger
from .cache import get_user_cache
from .models import User
from .schemas.auth import TokenResponse
from .security.cookie import delete_cookie, set_auth_cookies
from .security.jwt import get_jwt_manager
from .user_manager import UserManager

logger = get_structured_logger(__name__)
SecretType = Union[str, SecretStr]
user_manager = UserManager()


class Authentication:
    def __init__(self) -> None:
        self.logger = get_structured_logger(__name__)
        self.jwt_manager = get_jwt_manager()
        self.transport_type = settings.TOKEN_TRANSPORT_TYPE

    def login(
        self,
        user: User,
        response: Response,
    ) -> TokenResponse | None:
        if user is None:
            raise HTTPException(status_code=400, detail="Invalid user")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        if not user.is_verified:
            raise HTTPException(status_code=400, detail="Unverified user")

        # JWT Manager로 토큰 생성 (access / refresh 구분)
        access_token = self.jwt_manager.create_user_token(
            user_id=str(user.id),
            email=user.email,
            token_type="access",
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            is_active=user.is_active,
            audience="quant-users",
        )
        refresh_token = self.jwt_manager.create_user_token(
            user_id=str(user.id),
            email=user.email,
            token_type="refresh",
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            is_active=user.is_active,
            audience="quant-users",
        )

        # 캐시 갱신: 로그인 성공 시 최신 사용자 정보 캐시에 저장 (비동기, 실패 무시)
        try:
            import asyncio

            async def _cache_set():
                try:
                    await get_user_cache().set_user(user)
                except Exception:
                    pass

            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(_cache_set())
            else:
                loop.run_until_complete(_cache_set())
        except Exception:
            pass

        # 토큰 전송 방식에 따른 처리
        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

        if self.transport_type in ["cookie", "hybrid"]:
            # 쿠키에 토큰 설정
            set_auth_cookies(
                response,
                access_token=access_token,
                refresh_token=refresh_token,
            )

        if self.transport_type in ["bearer", "hybrid"]:
            # Bearer 방식에서는 토큰 정보 반환
            return token_response

        # Cookie 전용 방식에서는 None 반환 (토큰은 쿠키에만 설정)
        return None

    def refresh_token(
        self,
        refresh_token: str,
        response: Response,
        transport_type: Literal["cookie", "bearer", "hybrid"] | None = None,
    ) -> TokenResponse | None:
        """Refresh token을 사용하여 새로운 access token과 refresh token을 생성합니다."""
        try:
            payload = self.jwt_manager.decode_token(refresh_token)
        except Exception as e:
            self.logger.error(f"Failed to decode refresh token: {e}")
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user_id = payload.get("sub")
        email = payload.get("email", "")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # refresh 토큰 유형/오디언스 검증
        token_typ = payload.get("typ")
        token_aud = payload.get("aud")
        if token_typ != "refresh" or token_aud != "quant-users":
            raise HTTPException(status_code=401, detail="Invalid refresh token type")

        # 새로운 토큰 생성
        access_token = self.jwt_manager.create_user_token(
            user_id=user_id,
            email=email,
            token_type="access",
            is_verified=payload.get("is_verified", False),
            is_superuser=payload.get("is_superuser", False),
            is_active=payload.get("is_active", True),
            audience="quant-users",
        )
        new_refresh_token = self.jwt_manager.create_user_token(
            user_id=user_id,
            email=email,
            token_type="refresh",
            is_verified=payload.get("is_verified", False),
            is_superuser=payload.get("is_superuser", False),
            is_active=payload.get("is_active", True),
            audience="quant-users",
        )

        # 캐시 갱신: refresh 토큰 갱신 시에도 사용자 캐시 최신화 (비동기, 실패 무시)
        try:
            import asyncio

            from beanie import PydanticObjectId

            async def _refresh_cache():
                try:
                    user = await user_manager.get(PydanticObjectId(user_id))
                    if user:
                        await get_user_cache().set_user(user)
                except Exception:
                    pass

            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(_refresh_cache())
            else:
                loop.run_until_complete(_refresh_cache())
        except Exception:
            pass

        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

        # 기본 전송 방식은 인스턴스 설정을 따른다
        effective_transport = transport_type or self.transport_type

        if effective_transport in ["cookie", "hybrid"]:
            set_auth_cookies(
                response,
                access_token=access_token,
                refresh_token=new_refresh_token,
            )

        if effective_transport in ["bearer", "hybrid"]:
            return token_response

        return None

    def validate_token(self, token: str) -> dict[str, Any]:
        """토큰을 검증하고 payload를 반환합니다."""
        try:
            return self.jwt_manager.decode_token(token)
        except Exception as e:
            self.logger.error(f"Failed to validate token: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")

    def logout(self, response: Response) -> None:
        """로그아웃 처리 (쿠키 삭제)."""
        delete_cookie(response, key="access_token")
        delete_cookie(response, key="refresh_token")


authenticator = Authentication()

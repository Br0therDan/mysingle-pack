# path: app/auth/providers.py

import logging
import secrets
from typing import Optional, Union

import httpx
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.kakao import KakaoOAuth2
from httpx_oauth.clients.naver import NaverOAuth2

from app.core.config import settings

from .schemas.oauth2 import (
    BaseOAuthToken,
    GoogleProfile,
    GoogleToken,
    KakaoProfile,
    KakaoToken,
    NaverProfile,
    NaverToken,
)

logger = logging.getLogger(__name__)

# ---------------------------
# OAuth2 Clients
# ---------------------------
google_client = GoogleOAuth2(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
)
kakao_client = KakaoOAuth2(
    client_id=settings.KAKAO_CLIENT_ID,
    client_secret=settings.KAKAO_CLIENT_SECRET,
)
naver_client = NaverOAuth2(
    client_id=settings.NAVER_CLIENT_ID,
    client_secret=settings.NAVER_CLIENT_SECRET,
)

AVAILABLE_PROVIDERS = {
    "google": google_client,
    "kakao": kakao_client,
    "naver": naver_client,
}


class OAuthManager:
    """
    OAuthManager 클래스를 통해
    - Provider별 authorize URL
    - Callback 시 Access Token & Profile
    - User DB 업데이트
    를 일관되게 처리.
    """

    @staticmethod
    def get_provider_client(provider: str):
        if provider not in AVAILABLE_PROVIDERS:
            raise ValueError(f"Unknown OAuth provider: {provider}")
        return AVAILABLE_PROVIDERS[provider]

    @staticmethod
    def get_redirect_uri(provider: str) -> str:
        return f"{settings.FRONTEND_URL}/api/auth/oauth2/{provider}/callback"

    @staticmethod
    async def generate_auth_url(
        provider: str, state: Optional[str], redirect_uri: str | None = None
    ) -> str:
        client = OAuthManager.get_provider_client(provider)
        if not redirect_uri:
            redirect_uri = OAuthManager.get_redirect_uri(provider)
        state_string = state or secrets.token_urlsafe(16)
        scope = None
        if provider == "google":
            scope = ["openid", "email", "profile"]
        try:
            authorization_url = await client.get_authorization_url(
                redirect_uri=redirect_uri, state=state_string, scope=scope
            )
            return str(authorization_url)
        except Exception as e:
            logger.error(f"{provider} Authorization URL 생성 오류: {e}")
            raise ValueError(f"{provider.capitalize()} Authorization URL 생성 실패")

    @staticmethod
    async def get_access_token_and_profile(
        provider: str,
        code: str,
        redirect_uri: str,
    ) -> tuple[BaseOAuthToken, Union[GoogleProfile, KakaoProfile, NaverProfile]]:
        """
        1) Access Token 획득
        2) Provider별 Profile API 호출
        3) (token_data, profile_data) 반환
        """
        client = OAuthManager.get_provider_client(provider)
        try:
            token_response = await client.get_access_token(
                code=code,
                redirect_uri=redirect_uri,
            )
        except Exception as e:
            logger.error(f"{provider} 토큰 획득 오류: {e}")
            raise ValueError(f"{provider.capitalize()} 토큰 획득 실패")
        token_data: BaseOAuthToken
        profile_data: Union[GoogleProfile, KakaoProfile, NaverProfile]
        async with httpx.AsyncClient() as httpc:
            if provider == "google":
                token_data = GoogleToken(**token_response)
                res = await httpc.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    params={"access_token": token_data.access_token},
                )
                res.raise_for_status()
                raw_profile = res.json()
                profile_data = GoogleProfile(**raw_profile)
            elif provider == "kakao":
                token_data = KakaoToken(**token_response)
                res = await httpc.get(
                    "https://kapi.kakao.com/v2/user/me",
                    headers={"Authorization": f"Bearer {token_data.access_token}"},
                )
                res.raise_for_status()
                raw_profile = res.json()
                profile_data = KakaoProfile(**raw_profile)
            elif provider == "naver":
                token_data = NaverToken(**token_response)
                res = await httpc.get(
                    "https://openapi.naver.com/v1/nid/me",
                    headers={"Authorization": f"Bearer {token_data.access_token}"},
                )
                res.raise_for_status()
                raw_profile = res.json()
                profile_data = NaverProfile(**raw_profile["response"])
            else:
                raise ValueError(f"Not implemented provider: {provider}")
        return token_data, profile_data


oauth_manager = OAuthManager()

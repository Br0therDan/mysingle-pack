from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Query, Request, Response

from ...logging import get_logger
from ..authenticate import authenticator
from ..exceptions import AuthenticationFailed
from ..oauth_manager import oauth_manager
from ..schemas.auth import LoginResponse, UserInfo
from ..security.jwt import get_jwt_manager
from ..user_manager import UserManager

user_manager = UserManager()
jwt_manager = get_jwt_manager()
logger = get_logger(__name__)


def get_oauth2_router() -> APIRouter:
    """Generate a router with the OAuth routes to associate an authenticated user."""

    router = APIRouter()

    # def generate_state_token(data: dict[str, str], secret: SecretType) -> str:
    #     data["aud"] = "users:oauth-state"
    #     # OAuth state 토큰 생성 (특수 payload)
    #     import jwt

    #     return jwt.encode(data, secret, algorithm="HS256")

    @router.get(
        "/{provider}/authorize",
    )
    async def authorize(
        provider: str,
        redirect_url: str | None = None,
        state: str | None = Query(None),
    ) -> str:
        """
        Initiate the OAuth2 authorization process for associating an OAuth account
        with the currently authenticated user.
        """

        try:
            authorization_url = await oauth_manager.generate_auth_url(
                provider, state, redirect_url
            )
            return authorization_url
        except Exception as e:
            if str(e) == "Unknown OAuth provider":
                logger.error(f"Failed to get OAuth URL for provider {provider}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            logger.error(f"{provider} authorize error: {e}")
            raise HTTPException(status_code=500, detail="Unknown authorize error")

    @router.get(
        "/{provider}/callback",
        response_model=LoginResponse,
        description="The response varies based on the authentication backend used.",
    )
    async def callback(
        request: Request,
        response: Response,
        provider: str,
        code: str = Query(...),
        redirect_url: str | None = None,
    ) -> LoginResponse:
        decoded_code = unquote(code)
        # (1) token, profile
        token_data, profile_data = await oauth_manager.get_access_token_and_profile(
            provider,
            decoded_code,
            redirect_url or oauth_manager.get_redirect_uri(provider),
        )

        # (2) upsert user (신규 가입 여부 반환)
        def parse_google_profile(profile_data):
            return {
                "profile_email": profile_data.email,
                "profile_id": profile_data.id,
                "profile_image": getattr(profile_data, "picture", None),
                "fullname": getattr(profile_data, "name", None),
            }

        def parse_kakao_profile(profile_data):
            return {
                "profile_email": profile_data.kakao_account.email,
                "profile_id": str(profile_data.id),
                "profile_image": profile_data.kakao_account.profile.profile_image_url,
                "fullname": profile_data.kakao_account.profile.nickname,
            }

        def parse_naver_profile(profile_data):
            return {
                "profile_email": profile_data.email,
                "profile_id": profile_data.id,
                "profile_image": profile_data.profile_image,
                "fullname": profile_data.name,
            }

        profile_parsers = {
            "google": parse_google_profile,
            "kakao": parse_kakao_profile,
            "naver": parse_naver_profile,
        }

        if provider not in profile_parsers:
            raise HTTPException(status_code=400, detail="Not supported provider")

        try:
            profile_kwargs = profile_parsers[provider](profile_data)
        except Exception as e:
            logger.error(f"Failed to parse profile data for provider {provider}: {e}")
            raise HTTPException(
                status_code=400, detail=f"Failed to parse profile data: {e}"
            )

        user = await user_manager.oauth_callback(
            oauth_name=provider,
            token_data=token_data,
            **profile_kwargs,
            request=request,
        )
        if not user:
            raise AuthenticationFailed("Invalid credentials")

        # authenticator.login을 호출하여 토큰 생성
        auth_token = authenticator.login(user=user, response=response)

        return LoginResponse(
            access_token=auth_token.access_token if auth_token else None,
            refresh_token=auth_token.refresh_token if auth_token else None,
            token_type="bearer",
            user_info=UserInfo(**user.model_dump(by_alias=True)),
        )

    return router

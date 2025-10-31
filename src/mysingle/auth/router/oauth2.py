from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Query, Request, Response, status

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
    """OAuth2 인증을 위한 라우터 생성"""

    router = APIRouter()

    @router.get(
        "/{provider}/authorize",
        response_model=str,
    )
    async def authorize(
        provider: str,
        redirect_url: str | None = None,
        state: str | None = Query(None),
    ) -> str:
        """
        OAuth2 인증 프로세스를 시작합니다.

        Args:
            provider: OAuth 제공자 (google, kakao, naver 등)
            redirect_url: 인증 후 리다이렉트할 URL
            state: CSRF 방지를 위한 state 파라미터

        Returns:
            str: OAuth 제공자의 인증 URL
        """
        try:
            authorization_url = await oauth_manager.generate_auth_url(
                provider, state, redirect_url
            )
            return authorization_url
        except Exception as e:
            error_msg = str(e)
            if error_msg == "Unknown OAuth provider":
                logger.error(f"Unknown OAuth provider: {provider}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unknown OAuth provider: {provider}",
                )
            logger.error(f"{provider} authorize error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate authorization URL",
            )

    @router.get(
        "/{provider}/callback",
        response_model=LoginResponse,
        description="OAuth2 콜백 엔드포인트. 인증 백엔드에 따라 응답이 달라집니다.",
    )
    async def callback(
        request: Request,
        response: Response,
        provider: str,
        code: str = Query(...),
        redirect_url: str | None = None,
    ) -> LoginResponse:
        """
        OAuth2 콜백을 처리하고 사용자를 인증합니다.

        Args:
            request: FastAPI Request 객체
            response: FastAPI Response 객체
            provider: OAuth 제공자
            code: 인증 코드
            redirect_url: 리다이렉트 URL

        Returns:
            LoginResponse: 액세스 토큰과 사용자 정보
        """
        decoded_code = unquote(code)

        # (1) 액세스 토큰 및 프로필 정보 가져오기
        token_data, profile_data = await oauth_manager.get_access_token_and_profile(
            provider,
            decoded_code,
            redirect_url or oauth_manager.get_redirect_uri(provider),
        )

        # (2) 프로필 파서 정의
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}",
            )

        # (3) 프로필 데이터 파싱
        try:
            profile_kwargs = profile_parsers[provider](profile_data)
        except Exception as e:
            logger.error(f"Failed to parse profile data for provider {provider}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse profile data: {e}",
            )

        # (4) 사용자 생성 또는 업데이트
        user = await user_manager.oauth_callback(
            oauth_name=provider,
            token_data=token_data,  # type: ignore[arg-type]
            **profile_kwargs,
            request=request,
        )
        if not user:
            raise AuthenticationFailed("Failed to authenticate with OAuth provider")

        # (5) 로그인 토큰 생성
        auth_token = authenticator.login(user=user, response=response)

        return LoginResponse(
            access_token=auth_token.access_token if auth_token else None,
            refresh_token=auth_token.refresh_token if auth_token else None,
            token_type="bearer",
            user_info=UserInfo(**user.model_dump(by_alias=True)),
        )

    return router

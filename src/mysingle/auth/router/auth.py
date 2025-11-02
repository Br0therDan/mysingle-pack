"""Health check utilities and endpoints."""

from typing import Annotated

from beanie import PydanticObjectId
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from ...core.config import settings
from ...logging import get_structured_logger
from ..authenticate import authenticator
from ..deps import get_current_user, get_current_user_optional, verified_only
from ..exceptions import AuthenticationFailed
from ..schemas.auth import LoginResponse, UserInfo, VerifyTokenResponse
from ..user_manager import UserManager

logger = get_structured_logger(__name__)
access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
user_manager = UserManager()
authenticator = authenticator


def create_auth_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "/login",
        response_model=LoginResponse,
        status_code=status.HTTP_200_OK,  # 202 -> 200 변경
    )
    async def login(
        response: Response,  # Response 객체를 직접 받도록 수정
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> LoginResponse | None:
        user = await user_manager.authenticate(
            username=form_data.username, password=form_data.password
        )

        if not user:
            raise AuthenticationFailed("Invalid credentials")

        # authenticator.login을 호출하여 토큰 생성
        token_data = authenticator.login(user=user, response=response)

        if settings.TOKEN_TRANSPORT_TYPE in ["bearer", "hybrid"]:
            # Bearer 또는 Hybrid 방식: 응답에 토큰 포함
            return LoginResponse(
                access_token=token_data.access_token if token_data else None,
                refresh_token=token_data.refresh_token if token_data else None,
                token_type="bearer",
                user_info=UserInfo(**user.model_dump(by_alias=True)),
            )
        else:
            # Cookie 방식: 토큰은 쿠키에만 설정, 응답에는 사용자 정보만
            return None

    @router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
    async def logout(
        request: Request,
        response: Response,
    ) -> None:
        """
        로그아웃 엔드포인트.

        쿠키에서 토큰을 삭제하고 로그아웃 처리를 합니다.
        """
        # 현재 사용자 가져오기 (선택적)
        user = get_current_user_optional(request)

        # authenticator를 사용하여 쿠키 삭제
        authenticator.logout(response)

        # 사용자가 인증된 경우에만 후처리 로직 실행
        if user:
            try:
                current_user = await user_manager.get(PydanticObjectId(user.id))
                if current_user:
                    await user_manager.on_after_logout(current_user, request)
            except Exception as e:
                logger.warning(f"Failed to execute logout callback: {e}")

        # HTTP 204는 응답 본문이 없어야 하므로 None 반환
        return None

    @router.post("/refresh", response_model=LoginResponse)
    async def refresh_token(
        response: Response,  # Response 객체 추가
        refresh_token_header: str | None = Header(None, alias="X-Refresh-Token"),
        refresh_token_cookie: str | None = Cookie(None, alias="refresh_token"),
    ) -> LoginResponse | None:
        """JWT 토큰 갱신 엔드포인트"""

        # 토큰 전송 방식에 따라 refresh token 소스 결정
        if settings.TOKEN_TRANSPORT_TYPE == "bearer":
            refresh_token = refresh_token_header
        elif settings.TOKEN_TRANSPORT_TYPE == "cookie":
            refresh_token = refresh_token_cookie
        else:  # hybrid
            refresh_token = refresh_token_header or refresh_token_cookie

        if not refresh_token:
            raise AuthenticationFailed("Refresh token not provided")

        try:
            # 토큰 전송 방식에 맞게 새 토큰 생성
            from typing import Literal

            transport_type: Literal["cookie", "header", "bearer", "hybrid"]
            if settings.TOKEN_TRANSPORT_TYPE == "bearer":
                transport_type = "bearer"
            elif settings.TOKEN_TRANSPORT_TYPE == "cookie":
                transport_type = "cookie"
            else:  # hybrid
                transport_type = "hybrid"

            token_data = authenticator.refresh_token(
                refresh_token=refresh_token,
                response=response,
                transport_type=transport_type,
            )
        except HTTPException:
            raise AuthenticationFailed("Invalid refresh token")

        # 사용자 정보 조회
        try:
            payload = authenticator.validate_token(refresh_token)
            user_id = payload.get("sub")
            user = await user_manager.get(PydanticObjectId(user_id))
            if not user:
                raise AuthenticationFailed("User not found")
        except Exception:
            raise AuthenticationFailed("Failed to retrieve user information")

        # 토큰 전송 방식에 따른 응답 생성
        if settings.TOKEN_TRANSPORT_TYPE in ["bearer", "hybrid"] and token_data:
            return LoginResponse(
                access_token=token_data.access_token,
                refresh_token=token_data.refresh_token,
                token_type=token_data.token_type,
                user_info=UserInfo(**user.model_dump(by_alias=True)),
            )
        else:
            # Cookie 방식
            return None

    @router.get("/token/verify")
    @verified_only
    async def verify_token(
        request: Request,
    ) -> VerifyTokenResponse:
        """토큰 검증 및 사용자 정보 반환 (디버깅용)"""
        current_user = get_current_user(request)
        return VerifyTokenResponse(
            valid=True,
            user_id=str(current_user.id),
            email=current_user.email,
            is_verified=current_user.is_verified,
            is_superuser=current_user.is_superuser,
            is_active=current_user.is_active,
        )

    return router

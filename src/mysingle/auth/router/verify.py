from fastapi import APIRouter, Body, Request, status
from pydantic import EmailStr

from mysingle.auth.exceptions import (
    UserAlreadyVerified,
    UserInactive,
    UserNotExists,
)
from mysingle.auth.schemas import UserResponse
from mysingle.auth.user_manager import UserManager

user_manager = UserManager()


def get_verify_router() -> APIRouter:
    """이메일 검증을 위한 라우터 생성"""
    router = APIRouter()

    @router.post(
        "/request-verify-token",
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def request_verify_token(
        request: Request,
        email: EmailStr = Body(..., embed=True),
    ) -> None:
        """
        이메일 검증 토큰을 요청합니다.

        보안을 위해 이메일 존재 여부와 관계없이 항상 202 응답을 반환합니다.
        """
        try:
            user = await user_manager.get_by_email(email)
            await user_manager.request_verify(user, request)
        except (
            UserNotExists,
            UserInactive,
            UserAlreadyVerified,
        ):
            # 보안: 사용자 존재 여부를 노출하지 않음
            pass

        return None

    @router.post(
        "/verify",
        response_model=UserResponse,
    )
    async def verify(
        request: Request,
        token: str = Body(..., embed=True),
    ) -> UserResponse:
        """
        이메일 검증 토큰을 사용하여 사용자를 검증합니다.
        """
        # UserManager.verify에서 이미 적절한 예외를 발생시키므로
        # 직접 전파하도록 수정
        user = await user_manager.verify(token, request)
        return UserResponse.model_validate(user, from_attributes=True)

    return router

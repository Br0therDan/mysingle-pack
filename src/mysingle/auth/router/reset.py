from fastapi import APIRouter, Body, Request, status
from pydantic import EmailStr

from ..exceptions import (
    UserInactive,
    UserNotExists,
)
from ..user_manager import UserManager

user_manager = UserManager()


def get_reset_password_router() -> APIRouter:
    """비밀번호 재설정을 위한 라우터 생성"""
    router = APIRouter()

    @router.post(
        "/forgot-password",
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def forgot_password(
        request: Request,
        email: EmailStr = Body(..., embed=True),
    ) -> None:
        """
        비밀번호 재설정 이메일을 요청합니다.

        보안을 위해 이메일 존재 여부와 관계없이 항상 202 응답을 반환합니다.
        """
        try:
            user = await user_manager.get_by_email(email)
        except UserNotExists:
            # 보안: 사용자 존재 여부를 노출하지 않음
            return None

        try:
            await user_manager.forgot_password(user, request)
        except UserInactive:
            # 보안: 사용자 상태를 노출하지 않음
            pass

        return None

    @router.post(
        "/reset-password",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def reset_password(
        request: Request,
        token: str = Body(...),
        password: str = Body(...),
    ) -> None:
        """
        토큰을 사용하여 비밀번호를 재설정합니다.
        """
        # UserManager.reset_password에서 이미 적절한 예외를 발생시키므로
        # 직접 전파하도록 수정
        await user_manager.reset_password(token, password, request)
        return None

    return router

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Request, Response, status

from mysingle_quant.auth.models import User

from ..deps import get_current_active_superuser, get_current_active_verified_user
from ..exceptions import (
    UserNotExists,
)
from ..schemas import UserResponse, UserUpdate
from ..user_manager import UserManager

user_manager = UserManager()


def get_users_router() -> APIRouter:
    """Generate a router with the authentication routes."""
    router = APIRouter()

    @router.get(
        "/me",
        response_model=UserResponse,
    )
    async def get_user_me(
        current_user: User = Depends(get_current_active_verified_user),
    ) -> UserResponse:
        if current_user is None:
            raise UserNotExists(identifier="current user", identifier_type="user")

        return UserResponse(**current_user.model_dump(by_alias=True))

    @router.get(
        "/me/activity",
        response_model=dict,
    )
    async def get_user_activity(
        current_user: User = Depends(get_current_active_verified_user),
    ) -> dict:
        """
        현재 사용자의 활동 기록 조회.

        Returns:
            dict: 사용자 활동 요약 정보
        """
        return await user_manager.get_user_activity_summary(current_user)

    @router.patch(
        "/me",
        response_model=UserResponse,
    )
    async def update_user_me(
        obj_in: UserUpdate,
        current_user: User = Depends(get_current_active_verified_user),
    ) -> UserResponse:
        # UserManager.update에서 이미 적절한 예외를 발생시키므로
        # 직접 전파하도록 수정
        user = await user_manager.update(obj_in, current_user)
        return UserResponse(**user.model_dump(by_alias=True))

    @router.get(
        "/{user_id}",
        response_model=UserResponse,
        dependencies=[Depends(get_current_active_superuser)],
    )
    async def get_user(
        user_id: PydanticObjectId,
    ) -> UserResponse:
        user = await user_manager.get(user_id)
        if user is None:
            raise UserNotExists(identifier=str(user_id), identifier_type="user")
        return UserResponse(**user.model_dump(by_alias=True))

    @router.get(
        "/{user_id}/activity",
        response_model=dict,
        dependencies=[Depends(get_current_active_superuser)],
    )
    async def get_user_activity_by_id(
        user_id: PydanticObjectId,
    ) -> dict:
        """
        특정 사용자의 활동 기록 조회 (관리자 전용).

        Args:
            id: 조회할 사용자 ID

        Returns:
            dict: 사용자 활동 요약 정보
        """
        user = await user_manager.get(user_id)
        if user is None:
            raise UserNotExists(identifier=str(user_id), identifier_type="user")
        return await user_manager.get_user_activity_summary(user)

    @router.patch(
        "/{user_id}",
        response_model=UserResponse,
        dependencies=[Depends(get_current_active_superuser)],
    )
    async def update_user(
        request: Request,
        user_id: PydanticObjectId,
        obj_in: UserUpdate,  # type: ignore
    ) -> UserResponse:
        # 슈퍼유저 권한 확인
        user = await user_manager.get(user_id)
        if user is None:
            raise UserNotExists(identifier=str(user_id), identifier_type="user")
        updated_user = await user_manager.update(obj_in, user, request=request)
        return UserResponse(**updated_user.model_dump(by_alias=True))

    @router.delete(
        "/{user_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        response_class=Response,
        dependencies=[Depends(get_current_active_superuser)],
    )
    async def delete_user(
        request: Request,
        user_id: PydanticObjectId,
    ) -> None:
        # 슈퍼유저 권한 확인
        user = await user_manager.get(user_id)
        if user is None:
            raise UserNotExists(identifier=str(id), identifier_type="user")
        await user_manager.delete(user, request=request)
        return None

    return router

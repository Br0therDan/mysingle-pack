from fastapi import APIRouter, Request, status

from ..schemas import UserCreate, UserResponse
from ..user_manager import UserManager

user_manager = UserManager()


def get_register_router() -> APIRouter:
    """회원 가입을 위한 라우터 생성"""
    router = APIRouter()

    @router.post(
        "/register",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def register(
        request: Request,
        obj_in: UserCreate,
    ) -> UserResponse:
        """
        새로운 사용자를 등록합니다.

        Args:
            request: FastAPI Request 객체
            obj_in: 사용자 생성 정보 (이메일, 비밀번호 등)

        Returns:
            UserResponse: 생성된 사용자 정보
        """
        # UserManager.create에서 이미 적절한 예외를 발생시키므로
        # 직접 전파하도록 수정
        created_user = await user_manager.create(obj_in, request=request)
        return UserResponse.model_validate(created_user, from_attributes=True)

    return router

"""OAuth 계정 관리 엔드포인트"""

from beanie import PydanticObjectId
from fastapi import APIRouter, Request, status

from mysingle.auth.deps import admin_only, get_current_user, verified_only
from mysingle.auth.exceptions import UserNotExists
from mysingle.auth.user_manager import UserManager

user_manager = UserManager()


def get_oauth_management_router() -> APIRouter:
    """OAuth 계정 관리를 위한 라우터 생성"""
    router = APIRouter()

    @router.get(
        "/me/oauth-accounts",
        response_model=dict,
    )
    @verified_only
    async def get_my_oauth_accounts(
        request: Request,
    ) -> dict:
        """현재 사용자의 연결된 OAuth 계정 목록을 조회합니다."""
        current_user = get_current_user(request)

        oauth_accounts = []
        for oauth_account in current_user.oauth_accounts:
            oauth_accounts.append(
                {
                    "oauth_name": oauth_account.oauth_name,
                    "account_id": oauth_account.account_id,
                    "account_email": oauth_account.account_email,
                    "expires_at": oauth_account.expires_at,
                    "created_at": getattr(oauth_account, "created_at", None),
                }
            )

        return {"oauth_accounts": oauth_accounts, "total_count": len(oauth_accounts)}

    @router.delete(
        "/me/oauth-accounts/{oauth_name}/{account_id}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    @verified_only
    async def remove_oauth_account(
        request: Request,
        oauth_name: str,
        account_id: str,
    ) -> None:
        """특정 OAuth 계정 연결을 해제합니다."""
        current_user = get_current_user(request)

        await user_manager.remove_oauth_account(current_user, oauth_name, account_id)
        await user_manager.on_after_update(
            current_user, {"oauth_accounts": "removed"}, request
        )

    @router.get(
        "/{user_id}/oauth-accounts",
        response_model=dict,
    )
    @admin_only
    async def get_user_oauth_accounts(
        request: Request,
        user_id: PydanticObjectId,
    ) -> dict:
        """특정 사용자의 OAuth 계정 목록을 조회합니다. (관리자 전용)"""

        user = await user_manager.get(user_id)
        if user is None:
            raise UserNotExists(identifier=str(user_id), identifier_type="user")

        oauth_accounts = []
        for oauth_account in user.oauth_accounts:
            oauth_accounts.append(
                {
                    "oauth_name": oauth_account.oauth_name,
                    "account_id": oauth_account.account_id,
                    "account_email": oauth_account.account_email,
                    "expires_at": oauth_account.expires_at,
                    "created_at": getattr(oauth_account, "created_at", None),
                }
            )

        return {
            "user_id": str(user.id),
            "user_email": user.email,
            "oauth_accounts": oauth_accounts,
            "total_count": len(oauth_accounts),
        }

    return router

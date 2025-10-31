import uuid
from datetime import datetime, timezone
from typing import Any, TypeVar

import jwt
from beanie import PydanticObjectId
from fastapi import Request, Response
from pydantic import BaseModel

from mysingle.auth.schemas.oauth2 import BaseOAuthToken

from ..auth.models import OAuthAccount, User
from ..auth.schemas.user import UserCreate, UserUpdate
from ..auth.types import DependencyCallable
from ..core.config import settings
from ..email.email_gen import (
    generate_new_account_email,
    generate_reset_password_email,
    generate_verification_email,
)
from ..email.email_sending import send_email
from ..logging import get_logger
from .cache import get_user_cache
from .exceptions import (
    InvalidID,
    InvalidResetPasswordToken,
    InvalidVerifyToken,
    UserAlreadyExists,
    UserAlreadyVerified,
    UserInactive,
    UserNotExists,
)
from .security.jwt import get_jwt_manager
from .security.password import PasswordHelper, password_helper

logger = get_logger(__name__)
jwt_manager = get_jwt_manager()

# RESET_PASSWORD_TOKEN_AUDIENCE = "users:reset"
# VERIFY_USER_TOKEN_AUDIENCE = "users:verify"
SCHEMA = TypeVar("SCHEMA", bound=BaseModel)


class UserManager:
    """
    사용자 관리 로직.

    :attribute reset_password_token_secret: 비밀번호 재설정 토큰을
        인코딩하는 데 사용되는 비밀 키.

    :attribute reset_password_token_audience: 비밀번호 재설정 토큰의 JWT 대상(audience).
    :attribute verification_token_secret: 인증 토큰을 인코딩하는 데 사용되는 비밀 키.
    :attribute verification_token_lifetime_seconds: 인증 토큰의 유효 기간.
    :attribute verification_token_audience: 인증 토큰의 JWT 대상.

    :param user_db: 데이터베이스 어댑터 인스턴스.
    """

    password_helper: PasswordHelper

    def __init__(
        self,
    ):
        self.password_helper = password_helper

    async def read_user_from_token(
        self,
        token: str | None,
        token_audience: list[str] = ["quant-users"],
    ) -> User | None:
        if token is None:
            return None
        try:
            data = jwt_manager.decode_token(token)
            user_id = data.get("sub")
            if user_id is None:
                return None
        except jwt.PyJWTError:
            return None

        try:
            user = await self.get(user_id)
            return user
        except (UserNotExists, InvalidID):
            return None

    @staticmethod
    def model_dump(model: BaseModel, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return model.model_dump(*args, **kwargs)

    @staticmethod
    def model_validate(
        schema: type[BaseModel], obj: Any, *args: Any, **kwargs: Any
    ) -> BaseModel:
        return schema.model_validate(obj, *args, **kwargs)

    async def get(self, id: PydanticObjectId) -> User:
        """
        ID로 사용자를 조회합니다.

        :param id: 조회할 사용자의 ID.
        :raises UserNotExists: 해당 사용자가 존재하지 않습니다.
        :return: 사용자 객체.
        """
        user = await User.get(id)

        if user is None:
            raise UserNotExists()

        return user

    async def get_by_email(self, user_email: str) -> User:
        """
        이메일로 사용자를 조회합니다.

        :param user_email: 조회할 사용자의 이메일 주소.
        :raises UserNotExists: 해당 사용자가 존재하지 않습니다.
        :return: 사용자 객체.
        """
        user = await User.find_one({"email": user_email})

        if user is None:
            raise UserNotExists()

        return user

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> User:
        """
        OAuth 계정으로 사용자 가져오기.

        :param oauth: OAuth 클라이언트 이름.
        :param account_id: 외부 OAuth 서비스의 계정 ID.
        :raises UserNotExists: 사용자가 존재하지 않습니다.
        :return: 사용자 객체.
        """
        user = await User.find_one(
            {
                "oauth_accounts.oauth_name": oauth,
                "oauth_accounts.account_id": account_id,
            }
        )

        if user is None:
            raise UserNotExists()

        return user

    def find_oauth_account(
        self, user: User, oauth_name: str, account_id: str
    ) -> OAuthAccount | None:
        """
        사용자의 특정 OAuth 계정을 찾습니다.

        :param user: 검색할 사용자.
        :param oauth_name: OAuth 클라이언트 이름.
        :param account_id: OAuth 계정 ID.
        :return: 찾은 OAuth 계정 또는 None.
        """
        for oauth_account in user.oauth_accounts:
            if (
                oauth_account.oauth_name == oauth_name
                and oauth_account.account_id == account_id
            ):
                return oauth_account
        return None

    async def remove_oauth_account(
        self, user: User, oauth_name: str, account_id: str
    ) -> User:
        """
        사용자에서 OAuth 계정을 제거합니다.

        :param user: OAuth 계정을 제거할 사용자.
        :param oauth_name: OAuth 클라이언트 이름.
        :param account_id: OAuth 계정 ID.
        :return: 업데이트된 사용자 객체.
        :raises UserNotExists: OAuth 계정이 존재하지 않습니다.
        """
        oauth_account = self.find_oauth_account(user, oauth_name, account_id)
        if oauth_account is None:
            raise UserNotExists(
                identifier=f"{oauth_name}:{account_id}", identifier_type="OAuth account"
            )

        user.oauth_accounts.remove(oauth_account)
        await user.save()
        return user

    async def add_oauth_account(
        self, user: User, oauth_account_dict: dict[str, Any]
    ) -> User:
        """
        사용자에게 OAuth 계정 추가.

        :param user: OAuth 계정을 추가할 사용자.
        :param oauth_account_dict: 추가할 OAuth 계정의 세부 정보.
        :return: 업데이트된 사용자 객체.
        """
        oauth_account = OAuthAccount(**oauth_account_dict)
        user.oauth_accounts.append(oauth_account)
        await user.save()
        return user

    async def update_oauth_account(
        self,
        user: User,
        existing_oauth_account: OAuthAccount,
        oauth_account_dict: dict[str, Any],
    ) -> User:
        """
        사용자 OAuth 계정 업데이트.

        :param user: OAuth 계정을 업데이트할 사용자.
        :param existing_oauth_account: 업데이트할 기존 OAuth 계정.
        :param oauth_account_dict: 업데이트할 OAuth 계정의 새 세부 정보.
        :return: 업데이트된 사용자 객체.
        """
        existing_oauth_account.access_token = oauth_account_dict.get(
            "access_token", existing_oauth_account.access_token
        )
        existing_oauth_account.expires_at = oauth_account_dict.get(
            "expires_at", existing_oauth_account.expires_at
        )
        existing_oauth_account.refresh_token = oauth_account_dict.get(
            "refresh_token", existing_oauth_account.refresh_token
        )
        # 프로바이더에서 내려준 표시 정보도 가능하면 최신화
        # Only update if changed
        if oauth_account_dict.get("avatar_url") is not None and (
            existing_oauth_account.avatar_url != oauth_account_dict["avatar_url"]
        ):
            existing_oauth_account.avatar_url = oauth_account_dict["avatar_url"]
        if oauth_account_dict.get("name") is not None and (
            existing_oauth_account.name != oauth_account_dict["name"]
        ):
            existing_oauth_account.name = oauth_account_dict["name"]
        await user.save()
        return user

    async def create(
        self,
        obj_in: UserCreate,
        request: Request | None = None,
    ) -> User:
        """
        데이터베이스에 사용자를 생성합니다.

        성공 시 on_after_register 핸들러를 트리거합니다.

        :param user_create: 생성할 UserCreate 모델입니다.
        :param safe: True인 경우 is_superuser 또는 is_verified와 같은 민감한 값이
        생성 과정에서 무시됩니다. 기본값은 False입니다.
        :param request: 작업을 트리거한 선택적 FastAPI 요청입니다.
        기본값은 None입니다.
        :raises UserAlreadyExists: 동일한 이메일로 이미 사용자가 존재할 경우 발생합니다.
        :return: 새로 생성된 사용자입니다.
        """
        await self.validate_password(obj_in.password, obj_in)

        existing_user = await User.find_one({"email": obj_in.email})
        if existing_user is not None:
            raise UserAlreadyExists()

        user_dict = User(
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=self.password_helper.hash(obj_in.password),
        )
        # Remove password if exists (keeping for safety)
        # password = user_dict.pop("password")

        created_user = await User.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def oauth_callback(
        self,
        oauth_name: str,
        token_data: BaseOAuthToken,
        profile_id: str,
        profile_email: str,
        profile_image: str | None = None,
        fullname: str | None = None,
        *,
        request: Request | None = None,
        associate_by_email: bool = True,
    ) -> User | None:
        """
        OAuth 연결 성공 후 콜백 처리.

        지정된 사용자에게 이 새로운 OAuth 계정을 추가하거나 기존 OAuth 계정을 업데이트합니다.

        :param oauth_name: OAuth 클라이언트 이름.
        :param access_token: 서비스 공급자에 대한 유효한 액세스 토큰.
        :param account_id: 서비스 공급자 내 사용자의 models.ID.
        :param account_email: 서비스 공급자 측 사용자의 이메일.
        :param expires_at: 액세스 토큰이 만료되는 선택적 타임스탬프.
        :param refresh_token: 서비스 공급자로부터 새로운 액세스
            토큰을 얻기 위한 선택적 리프레시 토큰.
        :param request: 작업을 트리거한 선택적 FastAPI 요청, 기본값은 None
        :return: 사용자 객체.
        """
        oauth_account_dict = {
            "oauth_name": oauth_name,
            "avatar_url": profile_image,
            "name": fullname,
            "access_token": token_data.access_token,
            "account_id": profile_id,
            "account_email": profile_email,
            "expires_at": token_data.expires_at,
            "refresh_token": token_data.refresh_token,
        }

        # 기존 OAuth 계정이 있는지 확인
        try:
            user = await self.get_by_oauth_account(oauth_name, profile_id)
        except UserNotExists:
            try:
                # 기존 이메일 사용자와 연동
                user = await self.get_by_email(profile_email)
                if not associate_by_email:
                    raise UserAlreadyExists()
                user = await self.add_oauth_account(user, oauth_account_dict)

                # 프로바이더에서 제공한 아바타/이름으로 사용자 정보 보강
                updated = False
                if profile_image and user.avatar_url != profile_image:
                    user.avatar_url = profile_image
                    updated = True
                if fullname and (not user.full_name or user.full_name.strip() == ""):
                    user.full_name = fullname
                    updated = True
                if updated:
                    await user.save()
            except UserNotExists:
                # 신규 사용자 생성
                password = self.password_helper.generate_secure_password()
                new_user = UserCreate(
                    email=profile_email,
                    full_name=fullname,
                    password=password,
                    avatar_url=profile_image,
                    is_verified=True,
                    is_active=True,
                )
                user = await self.create(new_user)
                user = await self.add_oauth_account(user, oauth_account_dict)
                await self.on_after_register_by_oauth(user, password, request)
        else:
            # 기존 OAuth 계정 정보 업데이트
            for existing_oauth_account in user.oauth_accounts:
                if (
                    existing_oauth_account.account_id == profile_id
                    and existing_oauth_account.oauth_name == oauth_name
                ):
                    user = await self.update_oauth_account(
                        user, existing_oauth_account, oauth_account_dict
                    )

            # 프로바이더에서 제공한 아바타/이름으로 사용자 정보 보강
            updated = False
            if profile_image and user.avatar_url != profile_image:
                user.avatar_url = profile_image
                updated = True
            if fullname and (not user.full_name or user.full_name.strip() == ""):
                user.full_name = fullname
                updated = True
            if updated:
                await user.save()

        return user

    async def request_verify(self, user: User, request: Request | None = None) -> None:
        """
        인증 요청을 시작합니다.

        성공 시 on_after_request_verify 핸들러를 트리거합니다.

        :param user: 인증할 사용자.
        :param request: 작업을 트리거한 선택적 FastAPI 요청, 기본값은 None입니다.
        :raises UserInactive: 사용자가 비활성 상태입니다.
        :raises UserAlreadyVerified: 사용자가 이미 인증되었습니다.
        """
        if not user.is_active:
            raise UserInactive()
        if user.is_verified:
            raise UserAlreadyVerified()

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "aud": "users:verify",
        }
        # Verify 토큰은 특수 payload로 직접 생성
        token = jwt.encode(
            token_data, jwt_manager.settings.SECRET_KEY, algorithm=jwt_manager.algorithm
        )
        await self.on_after_request_verify(user, token, request)

    async def verify(self, token: str, request: Request | None = None) -> User:
        """
        인증 요청을 검증합니다.

        사용자의 is_verified 플래그를 True로 변경합니다.

        성공 시 on_after_verify 핸들러를 트리거합니다.

        :param token: request_verify로 생성된 인증 토큰.
        :param request: 작업을 트리거한 선택적 FastAPI 요청, 기본값은 None.
        :raises InvalidVerifyToken: 토큰이 유효하지 않거나 만료됨.
        :raises UserAlreadyVerified: 사용자가 이미 인증됨.
        :return: 인증된 사용자.
        """
        try:
            data = jwt.decode(
                token,
                jwt_manager.settings.SECRET_KEY,
                algorithms=[jwt_manager.algorithm],
                audience="users:verify",
            )
        except jwt.PyJWTError:
            raise InvalidVerifyToken()

        try:
            # user_id = data["sub"]
            email = data["email"]
        except KeyError:
            raise InvalidVerifyToken()

        try:
            user = await self.get_by_email(email)
        except UserNotExists:
            raise InvalidVerifyToken()
        if user.is_verified:
            raise UserAlreadyVerified()

        verified_user = await self._update(user, {"is_verified": True})

        await self.on_after_verify(verified_user, request)

        return verified_user

    async def forgot_password(self, user: User, request: Request | None = None) -> None:
        """
        비밀번호 찾기 요청을 시작합니다.

        성공 시 on_after_forgot_password 핸들러를 트리거합니다.

        :param user: 비밀번호를 분실한 사용자입니다.
        :param request: 작업을 트리거한 선택적 FastAPI 요청입니다.
        기본값은 None입니다.
        :raises UserInactive: 사용자가 비활성 상태입니다.
        """
        if not user.is_active:
            raise UserInactive()

        token_data = {
            "sub": str(user.id),
            "password_fgpt": password_helper.hash(user.hashed_password),
            "aud": "users:reset",
        }
        # Reset 토큰은 특수 payload로 직접 생성
        token = jwt.encode(
            token_data, jwt_manager.settings.SECRET_KEY, algorithm=jwt_manager.algorithm
        )
        await self.on_after_forgot_password(user, token, request)

    async def reset_password(
        self, token: str, password: str, request: Request | None = None
    ) -> User:
        """
        사용자의 비밀번호를 재설정합니다.

        성공 시 on_after_reset_password 핸들러를 트리거합니다.

        :param token: forgot_password에서 생성된 토큰입니다.
        :param password: 설정할 새 비밀번호입니다.
        :param request: 작업을 트리거한 선택적 FastAPI 요청, 기본값은 None입니다.
        :raises InvalidResetPasswordToken: 토큰이 유효하지 않거나 만료되었습니다.
        :raises UserInactive: 사용자가 비활성 상태입니다.
        :raises InvalidPasswordException: 비밀번호가 유효하지 않습니다.
        :return: 비밀번호가 업데이트된 사용자.
        """
        try:
            data = jwt.decode(
                token,
                jwt_manager.settings.SECRET_KEY,
                algorithms=[jwt_manager.algorithm],
                audience="users:reset",
            )
        except jwt.PyJWTError:
            raise InvalidResetPasswordToken()

        try:
            user_id = data["sub"]
            password_fingerprint = data["password_fgpt"]
        except KeyError:
            raise InvalidResetPasswordToken()
        user = await self.get(user_id)

        valid_password_fingerprint, _ = self.password_helper.verify_and_update(
            user.hashed_password, password_fingerprint
        )
        if not valid_password_fingerprint:
            raise InvalidResetPasswordToken()

        if not user.is_active:
            raise UserInactive()

        updated_user = await self._update(user, {"password": password})

        await self.on_after_reset_password(user, request)

        return updated_user

    async def update(
        self,
        obj_in: UserUpdate,
        user: User,
        request: Request | None = None,
    ) -> User:
        """
        사용자 업데이트.

        성공 시 on_after_update 핸들러를 트리거합니다.

        :param obj_in: 사용자에게 적용할 변경 사항을 포함하는
        UserUpdate 모델.
        :param user: 업데이트할 현재 사용자.
        :param safe: True인 경우 is_superuser 또는 is_verified와 같은 민감한 값이
        업데이트 중 무시됩니다. 기본값은 False입니다.
        :param request: 작업을 트리거한 선택적 FastAPI 요청입니다.
        기본값은 None입니다.
        :return: 업데이트된 사용자.
        """
        updated_user = await self._update(
            user, self.model_dump(obj_in, exclude_unset=True)
        )
        await self.on_after_update(
            updated_user, self.model_dump(updated_user, exclude_unset=True), request
        )
        return updated_user

    async def delete(
        self,
        user: User,
        request: Request | None = None,
    ) -> None:
        """
        Delete a user.

        :param user: The user to delete.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        await self.on_before_delete(user, request)
        # 실제 삭제 수행 (Beanie Document instance 삭제)
        await user.delete()
        await self.on_after_delete(user, request)

    async def validate_password(self, password: str, user: UserCreate | User) -> None:
        """
        Validate a password.

        *You should overload this method to add your own validation logic.*

        :param password: The password to validate.
        :param user: The user associated to this password.
        :raises InvalidPasswordException: The password is invalid.
        :return: None if the password is valid.
        """

        return  # pragma: no cover

    async def on_after_register(self, user: User, request: Request | None = None):
        """신규 가입 후 이메일 인증 발송"""
        logger.info(f"New user registered: {user.email} (ID: {user.id})")

        if not user.is_verified and settings.emails_enabled():
            try:
                # 인증 이메일 발송
                origin = (
                    str(request.base_url).rstrip("/")
                    if request
                    else settings.FRONTEND_URL
                )
                email_data = generate_verification_email(user.email, origin)

                send_email(
                    email_to=user.email,
                    subject=email_data.subject,
                    html_content=email_data.html_content,
                )

                logger.info(f"Verification email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send verification email to {user.email}: {e}")

    async def on_after_register_by_oauth(
        self, user: User, password: str | None = None, request: Request | None = None
    ):
        """OAuth로 신규 가입 후(관리자)"""
        logger.info(f"New user registered via OAuth: {user.email} (ID: {user.id})")

        if settings.emails_enabled() and password is not None:
            try:
                # 신규 계정 생성 이메일 발송
                origin = (
                    str(request.base_url).rstrip("/")
                    if request
                    else settings.FRONTEND_URL
                )
                email_data = generate_new_account_email(
                    email_to=user.email,
                    username=user.full_name or user.email,
                    password=password,
                    origin=origin,
                )

                send_email(
                    email_to=user.email,
                    subject=email_data.subject,
                    html_content=email_data.html_content,
                )

                logger.info(f"New account email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send new account email to {user.email}: {e}")

    async def on_after_update(
        self, user: User, update_dict: dict, request: Request | None = None
    ):
        """사용자 정보 업데이트 후"""
        logger.info(
            f"User updated: {user.email} (ID: {user.id}), fields: {list(update_dict.keys())}"
        )
        # 캐시 무효화
        try:
            await get_user_cache().invalidate_user(str(user.id))
            logger.debug(f"User cache invalidated after update: {user.id}")
        except Exception as e:
            logger.debug(f"Failed to invalidate user cache after update: {e}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        """인증 이메일 재요청 후 발송"""
        logger.info(
            f"Email verification re-requested for user: {user.email} (ID: {user.id})"
        )

        if settings.emails_enabled():
            try:
                origin = (
                    str(request.base_url).rstrip("/")
                    if request
                    else settings.FRONTEND_URL
                )
                email_data = generate_verification_email(user.email, origin)

                send_email(
                    email_to=user.email,
                    subject=email_data.subject,
                    html_content=email_data.html_content,
                )

                logger.info(f"Verification email re-sent to {user.email}")
            except Exception as e:
                logger.error(
                    f"Failed to re-send verification email to {user.email}: {e}"
                )

    async def on_after_verify(self, user: User, request: Request | None = None):
        """이메일 인증 완료 후"""
        logger.info(f"User email verified successfully: {user.email} (ID: {user.id})")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        """패스워드 복구 요청 후 이메일 발송"""
        logger.info(f"Password reset requested for user: {user.email} (ID: {user.id})")

        if settings.emails_enabled():
            try:
                origin = (
                    str(request.base_url).rstrip("/")
                    if request
                    else settings.FRONTEND_URL
                )
                email_data = generate_reset_password_email(
                    email_to=user.email,
                    email=user.email,
                    token=token,
                    origin=origin,
                )

                send_email(
                    email_to=user.email,
                    subject=email_data.subject,
                    html_content=email_data.html_content,
                )

                logger.info(f"Password reset email sent to {user.email}")
            except Exception as e:
                logger.error(
                    f"Failed to send password reset email to {user.email}: {e}"
                )

    async def on_after_reset_password(
        self, user: User, request: Request | None = None
    ) -> None:
        """
        비밀번호 재설정 성공 후 실행되는 로직.

        보안 알림 이메일을 발송하고 로그를 기록합니다.

        :param user: 비밀번호를 재설정한 사용자.
        :param request: 작업을 트리거한 선택적 FastAPI 요청, 기본값은 None.
        """
        logger.info(f"Password reset completed for user: {user.email} (ID: {user.id})")

        # 보안 알림 이메일 발송
        if settings.emails_enabled():
            try:
                origin = (
                    str(request.base_url).rstrip("/")
                    if request
                    else settings.FRONTEND_URL
                )

                # 새로운 템플릿을 사용한 보안 알림 이메일
                from ..email.email_gen import generate_password_reset_confirmation_email

                email_data = generate_password_reset_confirmation_email(
                    email_to=user.email,
                    username=user.full_name or user.email,
                    origin=origin,
                )

                send_email(
                    email_to=user.email,
                    subject=email_data.subject,
                    html_content=email_data.html_content,
                )

                logger.info(f"Password reset confirmation email sent to {user.email}")
            except Exception as e:
                logger.error(
                    f"Failed to send password reset confirmation email to {user.email}: {e}"
                )

    async def on_after_login(
        self,
        user: User,
        request: Request | None = None,
        response: Response | None = None,
    ) -> None:
        """
        Perform logic after user login.

        *You should overload this method to add your own logic.*

        :param user: The user that is logging in
        :param request: Optional FastAPI request
        :param response: Optional response built by the transport.
        Defaults to None
        """
        # 로그인 활동 기록 업데이트
        await self.update_login_activity(user, request)
        return  # pragma: no cover

    async def update_login_activity(
        self, user: User, request: Request | None = None
    ) -> User:
        """
        사용자 로그인 활동 기록 업데이트.

        :param user: 로그인한 사용자
        :param request: 선택적 FastAPI 요청
        :return: 업데이트된 사용자
        """
        now = datetime.now(timezone.utc)
        client_ip = None

        if request and request.client:
            client_ip = request.client.host
            # X-Forwarded-For 헤더 확인 (프록시/로드밸런서 뒤에 있는 경우)
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()

        update_dict: dict[str, Any] = {
            "last_login_at": now,
            "last_activity_at": now,
            "login_count": user.login_count + 1,
        }

        if client_ip:
            update_dict["last_login_ip"] = client_ip
            update_dict["last_activity_ip"] = client_ip

        updated_user = await self._update(user, update_dict)
        logger.info(
            f"Login activity recorded for user: {user.email} "
            f"(ID: {user.id}, IP: {client_ip}, Login count: {updated_user.login_count})"
        )

        return updated_user

    async def update_activity(self, user: User, request: Request | None = None) -> User:
        """
        사용자 활동 시간 업데이트 (마지막 활동 시각만 갱신).

        API 호출 등 일반적인 활동에 사용합니다.

        :param user: 활동한 사용자
        :param request: 선택적 FastAPI 요청
        :return: 업데이트된 사용자
        """
        now = datetime.now(timezone.utc)
        client_ip = None

        if request and request.client:
            client_ip = request.client.host
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()

        update_dict: dict[str, Any] = {"last_activity_at": now}

        if client_ip:
            update_dict["last_activity_ip"] = client_ip

        updated_user = await self._update(user, update_dict)

        return updated_user

    async def get_user_activity_summary(self, user: User) -> dict[str, Any]:
        """
        사용자 활동 요약 정보 반환.

        :param user: 조회할 사용자
        :return: 활동 요약 정보
        """
        return {
            "user_id": str(user.id),
            "email": user.email,
            "last_login_at": user.last_login_at,
            "last_activity_at": user.last_activity_at,
            "login_count": user.login_count,
            "last_login_ip": user.last_login_ip,
            "last_activity_ip": user.last_activity_ip,
            "account_created_at": user.created_at,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
        }

    async def on_after_logout(
        self,
        user: User,
        request: Request | None = None,
    ) -> None:
        """
        로그아웃 후 실행되는 로직.

        *필요에 따라 이 메소드를 오버로드하여 사용자 정의 로직을 추가할 수 있습니다.*

        :param user: 로그아웃하는 사용자
        :param request: 선택적 FastAPI 요청
        """
        logger.info(f"User logged out: {user.email} (ID: {user.id})")
        # 로그아웃 시 캐시 무효화 정책 적용 (세션 종료 시점에 최신 정책 반영)
        try:
            await get_user_cache().invalidate_user(str(user.id))
            logger.debug(f"User cache invalidated after logout: {user.id}")
        except Exception as e:
            logger.debug(f"Failed to invalidate user cache after logout: {e}")
        return  # pragma: no cover

    async def on_before_delete(
        self, user: User, request: Request | None = None
    ) -> None:
        """
        Perform logic before user delete.

        *You should overload this method to add your own logic.*

        :param user: The user to be deleted
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_delete(self, user: User, request: Request | None = None) -> None:
        """
        Perform logic before user delete.

        *You should overload this method to add your own logic.*

        :param user: The user to be deleted
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        # 캐시 무효화
        try:
            await get_user_cache().invalidate_user(str(user.id))
            logger.debug(f"User cache invalidated after delete: {user.id}")
        except Exception as e:
            logger.debug(f"Failed to invalidate user cache after delete: {e}")
        return  # pragma: no cover

    async def authenticate(self, username: str, password: str) -> User | None:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.

        :param credentials: The user credentials.
        """
        try:
            user = await self.get_by_email(username)
        except UserNotExists:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            password, user.hashed_password
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self._update(user, {"hashed_password": updated_password_hash})

        return user

    async def _update(self, user: User, update_dict: dict[str, Any]) -> User:
        validated_update_dict: dict[str, Any] = {}
        for field, value in update_dict.items():
            if field == "email" and value != user.email:
                try:
                    await self.get_by_email(value)
                    raise UserAlreadyExists()
                except UserNotExists:
                    validated_update_dict["email"] = value
                    validated_update_dict["is_verified"] = False
            elif field == "password" and value is not None:
                await self.validate_password(value, user)
                validated_update_dict["hashed_password"] = self.password_helper.hash(
                    value
                )
            else:
                validated_update_dict[field] = value

        # Beanie Document update
        for key, val in validated_update_dict.items():
            setattr(user, key, val)
        await user.save()
        # 업데이트 후 캐시 무효화 (중앙화)
        try:
            await get_user_cache().invalidate_user(str(user.id))
            logger.debug(f"User cache invalidated in _update: {user.id}")
        except Exception as e:
            logger.debug(f"Failed to invalidate user cache in _update: {e}")
        return user


class UUIDIDMixin:
    def parse_id(self, value: Any) -> uuid.UUID:
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except ValueError as e:
            raise InvalidID() from e


class IntegerIDMixin:
    def parse_id(self, value: Any) -> int:
        if isinstance(value, float):
            raise InvalidID()
        try:
            return int(value)
        except ValueError as e:
            raise InvalidID() from e


UserManagerDependency = DependencyCallable[UserManager]

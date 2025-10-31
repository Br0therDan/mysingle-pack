from datetime import datetime

from pydantic import EmailStr, Field
from pymongo import IndexModel

from mysingle.base import BaseDoc, BaseTimeDoc


class User(BaseTimeDoc):
    """Base User Document model."""

    email: EmailStr
    hashed_password: str
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    avatar_url: str | None = None
    oauth_accounts: list["OAuthAccount"] = Field(default_factory=list)

    # 활동 기록 필드
    last_login_at: datetime | None = None
    last_activity_at: datetime | None = None
    login_count: int = 0
    last_login_ip: str | None = None
    last_activity_ip: str | None = None

    class Settings:
        """Beanie settings."""

        name = "users"
        # Unique constraint: email + is_superuser 조합이 unique해야 함
        # 이렇게 하면 같은 이메일로 일반 유저(is_superuser=False) 1명과
        # 슈퍼유저(is_superuser=True) 1명만 존재 가능
        # 여러 워커가 동시에 실행되어도 MongoDB가 중복 생성을 방지함
        indexes = [
            IndexModel([("email", 1)]),  # 검색 성능을 위한 일반 인덱스
            IndexModel(
                [("email", 1), ("is_superuser", 1)],
                unique=True,
                name="unique_email_superuser",
            ),  # email + is_superuser unique 조합
        ]


class OAuthAccount(BaseDoc):
    """Base OAuth account Document model."""

    oauth_name: str
    name: str | None = None
    avatar_url: str | None = None
    access_token: str
    account_id: str
    account_email: str
    expires_at: int | None = None
    refresh_token: str | None = None

    class Settings:
        """Beanie settings."""

        name = "oauth_accounts"
        indexes = ["account_email"]

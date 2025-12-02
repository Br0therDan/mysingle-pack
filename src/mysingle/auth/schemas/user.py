from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from mysingle.core.base import BaseResponseSchema


class UserResponse(BaseResponseSchema):
    """Base User model."""

    email: EmailStr
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    avatar_url: str | None = None
    oauth_accounts: list["OAuthAccountResponse"] = Field(default_factory=list)

    # 활동 기록 필드
    last_login_at: datetime | None = None
    last_activity_at: datetime | None = None
    login_count: int = 0
    last_login_ip: str | None = None
    last_activity_ip: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "_id": "string",
                "email": "user@example.com",
                "full_name": "string",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
                "avatar_url": "string",
                "oauth_accounts": [
                    {
                        "oauth_name": "string",
                        "account_id": "string",
                        "account_email": "user@example.com",
                    }
                ],
            }
        },
    )


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str | None = None
    password: str
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False
    avatar_url: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "full_name": "string",
                "password": "string",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
                "avatar_url": "string",
            }
        }
    )


class UserUpdate(BaseModel):
    password: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None
    avatar_url: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "full_name": "string",
                "password": "string",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
                "avatar_url": "string",
            }
        }
    )


class OAuthAccountResponse(BaseModel):
    """Base OAuth account model."""

    oauth_name: str
    account_id: str
    account_email: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "_id": "string",
                "oauth_name": "string",
                "account_id": "string",
                "account_email": "user@example.com",
            }
        },
    )


class UserInfo(BaseModel):
    id: PydanticObjectId = Field(..., alias="_id")
    email: str
    avatar_url: str | None = None
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

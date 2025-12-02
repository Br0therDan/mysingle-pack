from datetime import UTC, datetime, timedelta

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field

from mysingle.core.config import settings


class UserInfo(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    email: str
    full_name: str | None = None
    is_active: bool
    is_superuser: bool
    is_verified: bool
    avatar_url: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "string",
                "email": "user@example.com",
                "full_name": "string",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
                "avatar_url": "string",
            }
        }
    )


class LoginResponse(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None
    user_info: UserInfo


class OAuth2AuthorizeResponse(BaseModel):
    authorization_url: str


now = datetime.now(UTC)
access_exp = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
refresh_exp = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
default_audience = [settings.DEFAULT_AUDIENCE]


class AccessTokenData(BaseModel):
    sub: str
    email: str | None = None
    exp: int = Field(default_factory=lambda: int(access_exp.timestamp()))
    iat: int = Field(default_factory=lambda: int(now.timestamp()))
    aud: list[str] = Field(default_factory=lambda: default_audience)
    type: str = "access"


class RefreshTokenData(BaseModel):
    sub: str
    exp: int = Field(default_factory=lambda: int(refresh_exp.timestamp()))
    iat: int = Field(default_factory=lambda: int(now.timestamp()))
    aud: list[str] = Field(default_factory=lambda: default_audience)
    type: str = "refresh"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "string",
                "refresh_token": "string",
                "token_type": "bearer",
            }
        }
    )


class VerifyTokenResponse(BaseModel):
    valid: bool
    user_id: str
    email: str
    is_verified: bool
    is_superuser: bool
    is_active: bool

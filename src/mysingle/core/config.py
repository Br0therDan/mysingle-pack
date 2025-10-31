"""Common configuration settings for all microservices."""

from typing import Literal, Self

from pydantic import EmailStr, Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    """Common settings for all microservices."""

    model_config = SettingsConfigDict(
        env_file="../../.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # PROJECT INFORMATION
    PROJECT_NAME: str = "Quant Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DEV_MODE: bool = True
    MOCK_DATABASE: bool = False

    AUDIT_LOGGING_ENABLED: bool = True

    FRONTEND_URL: str = "http://localhost:3000"

    # INITIAL SUPERUSER CREDENTIAL SETTINGS
    SUPERUSER_EMAIL: EmailStr = "your_email@example.com"
    SUPERUSER_PASSWORD: str = "change-this-admin-password"
    SUPERUSER_FULLNAME: str = "Admin User"

    # TEST USER CREDENTIAL SETTINGS (development/local only)
    TEST_USER_EMAIL: str = "test_user"
    TEST_USER_PASSWORD: str = "1234"
    TEST_USER_FULLNAME: str = "Test User"

    TEST_ADMIN_EMAIL: str = "test_admin"
    TEST_ADMIN_PASSWORD: str = "1234"
    TEST_ADMIN_FULLNAME: str = "Test Admin"

    # AUTH HOST SETTINGS (서비스 내부통신용 )
    AUTH_HOST: str = "http://localhost:8001"  # 또는 http://localhost:8000/strategy
    AUTH_API_VERSION: str = "v1"  # MySingle Auth 패키지 내부용

    AUTH_PUBLIC_PATHS: list[str] = [
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/verify-email",
        "/api/v1/auth/reset-password",
        "/api/v1/oauth2/google/authorize",
        "/api/v1/oauth2/google/callback",
        "/api/v1/oauth2/kakao/authorize",
        "/api/v1/oauth2/kakao/callback",
        "/api/v1/oauth2/naver/authorize",
        "/api/v1/oauth2/naver/callback",
    ]

    # DATABASE SETTINGS
    MONGODB_SERVER: str = "localhost:27017"
    MONGODB_USERNAME: str = "root"
    MONGODB_PASSWORD: str = "example"
    REDIS_URL: str = "redis://localhost:6379/0"
    # USER CACHE SETTINGS
    USER_CACHE_TTL_SECONDS: int = 300
    USER_CACHE_KEY_PREFIX: str = "user"

    # SECURITY & AUTH TOKEN SETTINGS
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    TOKEN_TRANSPORT_TYPE: Literal["bearer", "cookie", "hybrid"] = "hybrid"
    HTTPONLY_COOKIES: bool = False
    SAMESITE_COOKIES: Literal["lax", "strict", "none"] = "lax"
    ALGORITHM: str = "HS256"
    DEFAULT_AUDIENCE: str = "your-audience"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_MINUTES: int = 60
    VERIFY_TOKEN_EXPIRE_MINUTES: int = 60
    EMAIL_TOKEN_EXPIRE_HOURS: int = 48

    # API Settings
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS origins",
    )

    # PERFORMANCE SETTINGS
    MAX_CONNECTIONS_COUNT: int = 10
    MIN_CONNECTIONS_COUNT: int = 1

    # HTTP CLIENT SETTINGS
    HTTP_CLIENT_TIMEOUT: float = 30.0
    HTTP_CLIENT_MAX_CONNECTIONS: int = 100
    HTTP_CLIENT_MAX_KEEPALIVE: int = 20
    HTTP_CLIENT_MAX_RETRIES: int = 3
    HTTP_CLIENT_RETRY_DELAY: float = 1.0

    @property
    def all_cors_origins(self) -> list[str]:
        """Get all CORS origins including environment-specific ones."""
        origins = self.CORS_ORIGINS.copy()

        # Add localhost variants for development
        if self.ENVIRONMENT in ["development", "local"]:
            dev_origins = [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://localhost:8080",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000",
                "http://127.0.0.1:8080",
            ]
            for origin in dev_origins:
                if origin not in origins:
                    origins.append(origin)

        return origins

    # API GATEWAY SETTINGS
    USE_API_GATEWAY: bool = True
    API_GATEWAY_URL: str = "http://localhost:8000"
    KONG_JWT_SECRET_FRONTEND: str = "ypMmUBFkXFkMOfWpIxSvg+ypeCN/vhuZe7OUsb2L+LY="
    KONG_JWT_SECRET_STRATEGY_SERVICE: str = (
        "qE81i/aoJxrZ8+yDQz9nz2x5RT+Qk4zKq/iDMBDuc7E="
    )
    KONG_JWT_SECRET_MARKET_DATA_SERVICE: str = (
        "I+bh/ABpzCm23hKr44jc95LomKYCaRUCiYZFot/hk2Q="
    )
    KONG_JWT_SECRET_GENAI_SERVICE: str = "sLLR+xIYt5/82es5NJJ2G08xb0satQm/IGsSyV2kQwY="
    KONG_JWT_SECRET_ML_SERVICE: str = "tkYXxgR1ty7/e35DzPBkRBU1Z5fmzNDM5RznuVAx/SM="
    KONG_ADMIN_URL: str = "http://localhost:8100"
    KONG_PROXY_URL: str = "http://localhost:8000"

    # SMTP SETTINGS
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str = "your_smtp_host"
    SMTP_USER: str = "your_smtp_user"
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str = "your_email@example.com"
    EMAILS_FROM_NAME: str = "Admin Name"

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    @computed_field
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST == "your_smtp_host")

    # External API Keys

    # OAUTH2 SETTINGS
    GOOGLE_CLIENT_ID: str = "your-google-client-id"
    GOOGLE_CLIENT_SECRET: str = "your-google-client-secret"
    GOOGLE_OAUTH_SCOPES: list[str] = ["openid", "email", "profile"]
    OKTA_CLIENT_ID: str = "your-okta-client-id"
    OKTA_CLIENT_SECRET: str = "your-okta-client-secret"
    OKTA_DOMAIN: str = "your-okta-domain"
    KAKAO_CLIENT_ID: str = "your-kakao-client-id"
    KAKAO_CLIENT_SECRET: str = "your-kakao-client-secret"
    KAKAO_OAUTH_SCOPES: list[str] = ["profile", "account_email"]
    NAVER_CLIENT_ID: str = "your-naver-client-id"
    NAVER_CLIENT_SECRET: str = "your-naver-client-secret"
    NAVER_OAUTH_SCOPES: list[str] = ["profile", "email"]


# Global settings instance
settings = CommonSettings()


def get_settings() -> CommonSettings:
    """Get the global settings instance."""
    return settings

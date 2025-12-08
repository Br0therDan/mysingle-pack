"""Common configuration settings for all microservices."""

from typing import Literal, Self

from pydantic import EmailStr, Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    """Common settings for all microservices."""

    model_config = SettingsConfigDict(
        env_file=[".env"],
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # PROJECT INFORMATION
    PROJECT_NAME: str = "My Project"
    ENVIRONMENT: str = "development"

    FRONTEND_URL: str = "http://localhost:3000"

    DEBUG: bool = True  # Enable debug logging (auto-disabled in production)
    MOCK_DATABASE: bool = False

    AUDIT_LOGGING_ENABLED: bool = False
    AUDIT_EXCLUDE_PATHS: str = "/health,/ready,/metrics,/docs,/openapi.json,/redoc"

    ##################################################################
    # MONGODB SETTINGS
    ##################################################################
    MONGODB_SERVER: str = "localhost:27017"
    MONGODB_USERNAME: str = "admin"
    MONGODB_PASSWORD: str = "your_password"

    ##################################################################
    # REDIS SETTINGS
    ##################################################################
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0  # Default DB for user cache
    REDIS_PASSWORD: str | None = None  # Set to enable AUTH
    REDIS_URL: str = "redis://localhost:6379/0"  # Override for custom URL

    # REDIS DB ALLOCATION
    REDIS_DB_USER: int = 0  # User authentication cache
    REDIS_DB_GRPC: int = 2  # gRPC response cache
    REDIS_DB_RATE_LIMIT: int = 3  # Rate limiting counters
    REDIS_DB_SESSION: int = 4  # Session storage
    REDIS_DB_DSL: int = 5  # DSL bytecode cache

    # USER CACHE SETTINGS
    USER_CACHE_TTL_SECONDS: int = 300
    USER_CACHE_KEY_PREFIX: str = "user"

    # DSL CACHE SETTINGS
    DSL_CACHE_TTL_SECONDS: int = 3600  # 1 hour default TTL
    DSL_CACHE_KEY_PREFIX: str = "dsl:bytecode"
    DSL_CACHE_WARMING_TTL_SECONDS: int = 86400  # 24 hours for warmed cache

    ##################################################################
    # REDIS SETTINGS
    ##################################################################

    # GRPC SERVER SETTINGS

    GRPC_SERVER_MAX_WORKERS: int = 10  # Thread pool size
    GRPC_SERVER_ENABLE_REFLECTION: bool = False  # Enable in development only

    # GRPC Interceptor Settings
    GRPC_ENABLE_AUTH: bool = True  # Require user_id metadata
    GRPC_ENABLE_RATE_LIMITING: bool = True  # Enable rate limiting
    GRPC_ENABLE_METRICS: bool = True  # Prometheus metrics collection
    GRPC_ENABLE_ERROR_HANDLING: bool = True  # Auto error conversion

    # GRPC Rate Limiting
    GRPC_RATE_LIMIT_MAX_REQUESTS: int = 1000  # Max requests per window
    GRPC_RATE_LIMIT_WINDOW_SECONDS: int = 60  # Rate limit window (seconds)

    # GRPC Server Options
    GRPC_KEEPALIVE_TIME_MS: int = 30000  # TCP keepalive time (30s)
    GRPC_KEEPALIVE_TIMEOUT_MS: int = 10000  # TCP keepalive timeout (10s)
    GRPC_MAX_CONCURRENT_STREAMS: int = 100  # Max concurrent streams
    GRPC_MAX_MESSAGE_LENGTH: int = 10 * 1024 * 1024  # Max message size (10MB)

    # GRPC Cache Settings
    GRPC_CACHE_ENABLED: bool = True  # Enable response caching
    GRPC_CACHE_L1_TTL_SECONDS: int = 300  # L1 in-memory TTL (5 min)
    GRPC_CACHE_L1_MAX_SIZE: int = 100  # L1 LRU cache size
    GRPC_CACHE_L2_TTL_SECONDS: int = 3600  # L2 Redis TTL (1 hour)
    GRPC_CACHE_DEFAULT_TTL: int = 300  # Default cache TTL (5 min)

    ##################################################################
    # HTTP CLIENT SETTINGS
    ##################################################################

    HTTP_CLIENT_TIMEOUT: float = 30.0
    HTTP_CLIENT_MAX_CONNECTIONS: int = 100
    HTTP_CLIENT_MAX_KEEPALIVE: int = 20
    HTTP_CLIENT_MAX_RETRIES: int = 3
    HTTP_CLIENT_RETRY_DELAY: float = 1.0

    ##################################################################
    # CORS SETTINGS
    ##################################################################

    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS origins",
    )

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

    ##################################################################
    # LOGGING SETTINGS
    ##################################################################

    @computed_field
    @property
    def log_level(self) -> str:
        """Get appropriate log level based on DEBUG and ENVIRONMENT settings."""
        if self.ENVIRONMENT == "production":
            return "INFO"  # Force INFO in production for security
        return "DEBUG" if self.DEBUG else "INFO"

    @computed_field
    @property
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled (considers both DEBUG and ENVIRONMENT)."""
        return self.DEBUG and self.ENVIRONMENT != "production"

    ##################################################################
    # API GATEWAY SETTINGS
    ##################################################################
    USE_API_GATEWAY: bool = True
    API_GATEWAY_URL: str = "http://localhost:8000"

    KONG_JWT_SECRET_FRONTEND: str = "change-this-frontend-jwt-secret"
    KONG_JWT_SECRET_IAM: str = "change-this-iam-service-jwt-secret"
    KONG_JWT_SECRET_SUBSCRIPTION: str = "change-this-subscription-service-jwt-secret"
    KONG_JWT_SECRET_STRATEGY: str = "change-this-strategy-service-jwt-secret"
    KONG_JWT_SECRET_BACKTEST: str = "change-this-backtest-service-jwt-secret"
    KONG_JWT_SECRET_INDICATOR: str = "change-this-indicator-service-jwt-secret"
    KONG_JWT_SECRET_OPTIMIZATION: str = "change-this-optimization-service-jwt-secret"
    KONG_JWT_SECRET_DASHBOARD: str = "change-this-dashboard-service-jwt-secret"
    KONG_JWT_SECRET_NOTIFICATION: str = "change-this-notification-service-jwt-secret"
    KONG_JWT_SECRET_MARKET_DATA: str = "change-this-market-data-service-jwt-secret"
    KONG_JWT_SECRET_GENAI: str = "change-this-genai-service-jwt-secret"
    KONG_JWT_SECRET_ML: str = "change-this-ml-service-jwt-secret"

    ##################################################################
    # SMTP SETTINGS
    ##################################################################

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
        """Check if email sending is properly configured."""
        return bool(
            self.SMTP_HOST
            and self.SMTP_HOST != "your_smtp_host"
            and self.EMAILS_FROM_EMAIL != "your_email@example.com"
        )

    ##################################################################
    # IAM & SECURITY SETTINGS
    ##################################################################

    TOKEN_TRANSPORT_TYPE: Literal["bearer", "cookie", "hybrid"] = "hybrid"
    HTTPONLY_COOKIES: bool = False
    SAMESITE_COOKIES: Literal["lax", "strict", "none"] = "lax"
    ALGORITHM: str = "HS256"
    DEFAULT_AUDIENCE: str = "your-audience"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    SERVICE_TOKEN_EXPIRE_MINUTES: int = 10
    RESET_TOKEN_EXPIRE_MINUTES: int = 60
    VERIFY_TOKEN_EXPIRE_MINUTES: int = 60
    EMAIL_TOKEN_EXPIRE_HOURS: int = 48

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
    # AUTH MIDDLEWARE SETTINGS
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
    # OAUTH2 SETTINGS
    GOOGLE_CLIENT_ID: str = "your-google-client-id"
    GOOGLE_CLIENT_SECRET: str = "your-google-client-secret"
    GOOGLE_OAUTH_SCOPES: list[str] = ["openid", "email", "profile"]
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


def get_environment() -> str:
    """
    현재 실행 환경 반환

    Returns:
        환경 문자열: "development", "testing", "staging", "production"
    """
    return settings.ENVIRONMENT.lower()


def is_production() -> bool:
    """프로덕션 환경 여부"""
    return get_environment() == "production"


def is_development() -> bool:
    """개발 환경 여부 (development, testing 포함)"""
    env = get_environment()
    return env in ["development", "testing", "local"]

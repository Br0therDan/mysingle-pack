"""Common configuration settings for all microservices."""

from typing import Self

from pydantic import Field, computed_field, model_validator
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
    # JWT COMMON SETTINGS (used by all services)
    ##################################################################

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    SERVICE_TOKEN_EXPIRE_MINUTES: int = 10
    RESET_TOKEN_EXPIRE_MINUTES: int = 60
    VERIFY_TOKEN_EXPIRE_MINUTES: int = 60

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
    REDIS_PASSWORD: str | None = None  # Set to enable AUTH

    # REDIS DB ALLOCATION - Platform-wide standard
    REDIS_DB_USER: int = 0  # User authentication cache (IAM)
    REDIS_DB_GRPC: int = 1  # gRPC response cache (All services)
    REDIS_DB_RATE_LIMIT: int = 2  # Rate limiting counters (Kong/Gateway)
    REDIS_DB_SESSION: int = 3  # Session storage (IAM)
    REDIS_DB_DSL: int = 4  # DSL bytecode cache (Strategy)
    REDIS_DB_MARKET_DATA: int = 5  # Market data cache (Market Data)
    REDIS_DB_BACKTEST: int = 6  # Backtest service cache (Backtest)
    REDIS_DB_STRATEGY_CACHE: int = 8  # Strategy cache (Strategy)
    REDIS_DB_NOTIFICATION: int = 9  # Notification queue (Notification)
    REDIS_DB_CELERY_BROKER: int = 10  # Celery broker (Backtest)
    REDIS_DB_CELERY_RESULT: int = 11  # Celery result backend (Backtest)
    REDIS_DB_ML: int = 12  # ML model cache (ML)
    REDIS_DB_GENAI: int = 13  # GenAI response cache (GenAI)
    REDIS_DB_SUBSCRIPTION: int = 14  # Subscription cache (Subscription)
    REDIS_DB_PORTFOLIO: int = 15  # Portfolio service cache (Portfolio)
    REDIS_DB_RESERVED: int = 16  # Reserved for future platform needs

    @computed_field
    @property
    def redis_url(self) -> str:
        """Construct Redis URL from HOST/PORT/PASSWORD (read-only).

        Uses 'default' username for Redis 7.x ACL compatibility.
        """
        if self.REDIS_PASSWORD:
            return f"redis://default:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    # USER CACHE SETTINGS
    USER_CACHE_TTL_SECONDS: int = 300
    USER_CACHE_KEY_PREFIX: str = "user"

    # DSL CACHE SETTINGS
    DSL_CACHE_TTL_SECONDS: int = 3600  # 1 hour default TTL
    DSL_CACHE_KEY_PREFIX: str = "dsl:bytecode"
    DSL_CACHE_WARMING_TTL_SECONDS: int = 86400  # 24 hours for warmed cache

    ##################################################################
    # GRPC SERVER SETTINGS
    ##################################################################

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

    @model_validator(mode="after")
    def _validate_redis_config(self) -> Self:
        """Validate Redis configuration settings."""
        # Validate REDIS_HOST is not empty
        if not self.REDIS_HOST or self.REDIS_HOST.strip() == "":
            raise ValueError("REDIS_HOST cannot be empty")

        # Validate REDIS_PORT range
        if not (1 <= self.REDIS_PORT <= 65535):
            raise ValueError(
                f"REDIS_PORT must be between 1-65535, got {self.REDIS_PORT}"
            )

        # Validate all REDIS_DB_* values are within valid range (0-15)
        db_fields = {
            "REDIS_DB_USER": self.REDIS_DB_USER,
            "REDIS_DB_GRPC": self.REDIS_DB_GRPC,
            "REDIS_DB_RATE_LIMIT": self.REDIS_DB_RATE_LIMIT,
            "REDIS_DB_SESSION": self.REDIS_DB_SESSION,
            "REDIS_DB_DSL": self.REDIS_DB_DSL,
            "REDIS_DB_MARKET_DATA": self.REDIS_DB_MARKET_DATA,
            "REDIS_DB_BACKTEST": self.REDIS_DB_BACKTEST,
            "REDIS_DB_STRATEGY_CACHE": self.REDIS_DB_STRATEGY_CACHE,
            "REDIS_DB_NOTIFICATION": self.REDIS_DB_NOTIFICATION,
            "REDIS_DB_CELERY_BROKER": self.REDIS_DB_CELERY_BROKER,
            "REDIS_DB_CELERY_RESULT": self.REDIS_DB_CELERY_RESULT,
            "REDIS_DB_ML": self.REDIS_DB_ML,
            "REDIS_DB_GENAI": self.REDIS_DB_GENAI,
            "REDIS_DB_SUBSCRIPTION": self.REDIS_DB_SUBSCRIPTION,
            "REDIS_DB_RESERVED": self.REDIS_DB_RESERVED,
        }

        for field_name, db_value in db_fields.items():
            if not (0 <= db_value <= 20):
                raise ValueError(f"{field_name} must be between 0-20, got {db_value}")

        # Check for duplicate DB assignments (excluding RESERVED)
        db_values = [v for k, v in db_fields.items() if k != "REDIS_DB_RESERVED"]
        if len(db_values) != len(set(db_values)):
            duplicates = {x for x in db_values if db_values.count(x) > 1}
            raise ValueError(
                f"Duplicate Redis DB assignments detected: {duplicates}. "
                "Each service must use a unique DB number."
            )

        return self


# Global settings instance
settings = CommonSettings()


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

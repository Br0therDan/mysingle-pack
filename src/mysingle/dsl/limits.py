"""Resource Limits and Quota Configuration for User DSL Execution"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ResourceLimits(BaseSettings):
    """
    DSL 실행 리소스 제한

    사용자별 안전한 실행 환경을 위한 제약 조건
    """

    # 실행 시간 제한
    MAX_EXECUTION_TIME_SECONDS: int = Field(
        default=30, description="최대 실행 시간 (초)"
    )

    # 메모리 제한
    MAX_MEMORY_MB: int = Field(default=512, description="최대 메모리 사용량 (MB)")

    # 반복 제한
    MAX_ITERATIONS: int = Field(default=10_000, description="최대 루프 반복 횟수")

    # 출력 크기 제한
    MAX_OUTPUT_SIZE_MB: int = Field(default=10, description="최대 출력 크기 (MB)")

    # 재귀 깊이 제한
    MAX_RECURSION_DEPTH: int = Field(default=100, description="최대 재귀 깊이")

    model_config = SettingsConfigDict(env_prefix="DSL_")


class UserQuota(BaseSettings):
    """
    사용자별 할당량 설정

    무료/프리미엄 티어별 차등 적용
    """

    # 무료 티어 (Free Tier)
    FREE_DAILY_CALCULATIONS: int = Field(
        default=10_000, description="무료 사용자 일일 계산 횟수"
    )
    FREE_MAX_INDICATORS: int = Field(
        default=10, description="무료 사용자 최대 인디케이터 수"
    )
    FREE_MAX_PRIVATE_INDICATORS: int = Field(
        default=10, description="무료 사용자 최대 프라이빗 인디케이터 수"
    )

    # 프리미엄 티어 (Premium Tier)
    PREMIUM_DAILY_CALCULATIONS: int = Field(
        default=100_000, description="프리미엄 사용자 일일 계산 횟수"
    )
    PREMIUM_MAX_INDICATORS: int = Field(
        default=-1, description="프리미엄 사용자 최대 인디케이터 수 (-1: 무제한)"
    )
    PREMIUM_MAX_PRIVATE_INDICATORS: int = Field(
        default=-1,
        description="프리미엄 사용자 최대 프라이빗 인디케이터 수 (-1: 무제한)",
    )

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=100, description="분당 API 호출 제한 (사용자별)"
    )
    RATE_LIMIT_PER_HOUR: int = Field(
        default=1000, description="시간당 API 호출 제한 (사용자별)"
    )

    # 캐시 TTL
    QUOTA_CACHE_TTL_SECONDS: int = Field(
        default=300, description="할당량 캐시 TTL (초)"
    )

    model_config = SettingsConfigDict(env_prefix="USER_QUOTA_")


# 싱글톤 인스턴스
resource_limits = ResourceLimits()
user_quota = UserQuota()


def get_user_daily_limit(is_premium: bool = False) -> int:
    """사용자 일일 계산 한도 조회"""
    if is_premium:
        return user_quota.PREMIUM_DAILY_CALCULATIONS
    return user_quota.FREE_DAILY_CALCULATIONS


def get_user_max_indicators(is_premium: bool = False) -> int:
    """사용자 최대 인디케이터 수 조회"""
    if is_premium:
        return user_quota.PREMIUM_MAX_INDICATORS
    return user_quota.FREE_MAX_INDICATORS


def get_user_max_private_indicators(is_premium: bool = False) -> int:
    """사용자 최대 프라이빗 인디케이터 수 조회"""
    if is_premium:
        return user_quota.PREMIUM_MAX_PRIVATE_INDICATORS
    return user_quota.FREE_MAX_PRIVATE_INDICATORS

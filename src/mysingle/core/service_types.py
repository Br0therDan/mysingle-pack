"""
Simplified Service Configuration for MSA
간소화된 MSA 서비스 설정
"""

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class ServiceConfig:
    """통합 서비스 설정"""

    # 기본 정보
    service_name: str
    service_version: str = "1.0.0"
    description: Optional[str] = None

    # 데이터베이스
    enable_database: bool = True
    database_name: Optional[str] = None

    # 감사 로깅
    enable_audit_logging: bool = True

    # 인증 (Kong Gateway 헤더 기반)
    enable_auth: bool = True

    # Gateway 관련
    is_gateway_downstream: bool = True
    public_paths: list[str] = None

    # 기능
    enable_metrics: bool = True
    enable_health_check: bool = True
    cors_origins: Optional[list[str]] = None

    # Quota enforcement (선택적)
    enable_quota_enforcement: bool = False
    quota_metric: Optional[str] = None  # "api_calls", "backtests", etc.

    # 생명주기
    lifespan: Optional[Callable] = None

    def __post_init__(self):
        """기본값 설정"""
        # 데이터베이스명 기본값 설정
        if not self.database_name:
            self.database_name = f"{self.service_name.replace('-', '_')}_db"

        # public_paths 기본값 설정
        if self.public_paths is None:
            self.public_paths = [
                "/health",
                "/metrics",
                "/docs",
                "/openapi.json",
                "/redoc",
            ]


def create_service_config(
    service_name: str,
    service_version: str = "1.0.0",
    description: Optional[str] = None,
    **kwargs,
) -> ServiceConfig:
    """ServiceConfig 생성 헬퍼 함수"""

    return ServiceConfig(
        service_name=service_name,
        service_version=service_version,
        description=description,
        **kwargs,
    )


__all__ = [
    "ServiceConfig",
    "create_service_config",
]

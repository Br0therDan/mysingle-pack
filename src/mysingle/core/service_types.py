"""
Simplified Service Configuration for MSA
간소화된 MSA 서비스 설정 (IAM vs Non-IAM)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


class ServiceType(str, Enum):
    """간소화된 마이크로서비스 유형"""

    # IAM 서비스 - 인증/사용자 관리 기능 포함 (직접 JWT 검증)
    IAM_SERVICE = "iam_service"

    # Non-IAM 서비스 - Gateway 헤더 기반 인증
    NON_IAM_SERVICE = "non_iam_service"


@dataclass
class ServiceConfig:
    """통합 서비스 설정 (AppConfig + ServiceConfig 일원화)"""

    # 기본 정보
    service_name: str
    service_type: ServiceType
    service_version: str = "1.0.0"
    description: Optional[str] = None

    # 데이터베이스
    enable_database: bool = True
    database_name: Optional[str] = None

    # 감사 로깅
    enable_audit_logging: bool = True

    # 인증 (ServiceType에 따라 자동 설정)
    enable_auth: bool = field(init=False)
    enable_oauth: bool = field(init=False)
    enable_user_management: bool = field(init=False)

    # Gateway 관련
    is_gateway_downstream: bool = field(init=False)
    public_paths: list[str] = field(default_factory=lambda: ["/health", "/metrics"])

    # 기능
    enable_metrics: bool = True
    enable_health_check: bool = True
    cors_origins: Optional[list[str]] = None

    # 생명주기
    lifespan: Optional[Callable] = None

    def __post_init__(self):
        """ServiceType에 따라 인증 설정 자동 구성"""
        if self.service_type == ServiceType.IAM_SERVICE:
            # IAM 서비스: 직접 JWT 검증
            self.enable_auth = True
            self.enable_oauth = True
            self.enable_user_management = True
            self.is_gateway_downstream = False
            self.public_paths.extend(["/docs", "/openapi.json"])

        else:  # NON_IAM_SERVICE
            # Non-IAM 서비스: Gateway 헤더 기반 인증 우선 + 미들웨어 활성화
            # 미들웨어는 우선 Kong 헤더를 사용하고, 없으면 직접 JWT(헤더/쿠키)로 폴백합니다.
            # 따라서 Non-IAM 서비스에서도 enable_auth 를 True 로 설정해 미들웨어를 장착합니다.
            self.enable_auth = True
            self.enable_oauth = False
            self.enable_user_management = False
            self.is_gateway_downstream = True

        # 데이터베이스명 기본값 설정
        if not self.database_name:
            self.database_name = f"{self.service_name.replace('-', '_')}_db"


def create_service_config(
    service_name: str,
    service_type: ServiceType,
    service_version: str = "1.0.0",
    description: Optional[str] = None,
    **kwargs,
) -> ServiceConfig:
    """ServiceConfig 생성 헬퍼 함수"""

    return ServiceConfig(
        service_name=service_name,
        service_type=service_type,
        service_version=service_version,
        description=description,
        **kwargs,
    )


# 환경변수에서 ServiceType 파싱
def parse_service_type(type_str: str) -> ServiceType:
    """환경변수 문자열을 ServiceType으로 변환"""
    try:
        return ServiceType(type_str.lower())
    except ValueError:
        # 기본값: Non-IAM 서비스
        return ServiceType.NON_IAM_SERVICE


__all__ = [
    "ServiceType",
    "ServiceConfig",
    "create_service_config",
    "parse_service_type",
]

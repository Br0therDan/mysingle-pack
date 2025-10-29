# Quant Pack 개선 요구사항

현재 mysingle_quant 패키지의 분석 결과, 다음과 같은 개선사항이 필요합니다.

## 1. 핵심 개선사항

### 1.1 App Factory 표준화 (완료됨)

**현재 상황**: `core/app_factory.py`가 이미 완전히 구현되어 있음
**구현 상태**: ✅ 완전 구현됨

**현재 구현된 기능들**:
- `create_fastapi_app()`: 표준화된 FastAPI 앱 팩토리
- `create_service_config()`: ServiceConfig 생성 헬퍼
- 자동 미들웨어 장착 (Auth, Metrics, CORS, Audit)
- Lifespan 관리 (MongoDB, 리소스 정리)
- 환경별 설정 (개발/프로덕션 모드)
- Health check 라우터 자동 등록

**실제 사용 패턴**:
```python
# 현재 서비스들에서 사용 중인 표준 패턴
from mysingle_quant.core import (
    ServiceType,
    create_fastapi_app,
    create_service_config,
)

def create_app() -> FastAPI:
    service_config = create_service_config(
        service_name=settings.SERVICE_NAME,
        service_type=ServiceType.NON_IAM_SERVICE,
        service_version="0.1.0",
        description="Service Description",
        lifespan=lifespan,
        enable_auth=True,
        enable_database=True,
        enable_metrics=True,
    )

    app = create_fastapi_app(
        service_config=service_config,
        document_models=models.document_models,
    )
    
    return app
```

### 1.2 DI 함수 개선 및 현행화 (중요)

**현재 상황**: `auth/deps.py`가 Request 기반으로 완전히 재설계됨
**구현 상태**: ✅ Request 기반 새로운 DI 시스템 완성

**현재 구현된 함수들**:
```python
# mysingle_quant/auth/deps.py - 현재 구현된 주요 함수들
from fastapi import Request

# Core 함수들
def get_current_user(request: Request) -> User
def get_current_active_user(request: Request) -> User  
def get_current_active_verified_user(request: Request) -> User
def get_current_active_superuser(request: Request) -> User
def get_current_user_optional(request: Request) -> Optional[User]

# Kong Gateway 통합 함수들
def get_kong_user_id(request: Request) -> Optional[str]
def get_kong_consumer_id(request: Request) -> Optional[str] 
def is_kong_authenticated(request: Request) -> bool

# 유틸리티 함수들
def get_user_id(request: Request) -> Optional[str]
def get_user_email(request: Request) -> Optional[str]
def is_user_authenticated(request: Request) -> bool
```

**개선 요구사항**: 
- Depends() 패턴과 Request 패턴 혼용 해결
- 기존 미들웨어 기반 함수들과의 호환성 보장
- API Gateway 환경에서 AuthMiddleware 중복 제거 옵션

**현재 구조 분석**:
- **NON_IAM_SERVICE**: `enable_auth = False` → AuthMiddleware 자동 비활성화 ✅
- **Request 기반 함수들**: Kong Gateway 헤더 직접 읽기 (미들웨어 무관) ✅
- **IAM_SERVICE**: 직접 JWT 검증용 AuthMiddleware 필요 ✅

**제안 해결책**:
```python
# 1. Depends() 호환성을 위한 래퍼 함수들 추가
from fastapi import Depends, Request

def get_current_active_user_deps(request: Request = Depends()) -> User:
    """Depends() 패턴용 래퍼 - 기존 코드 호환성"""
    return get_current_active_user(request)

def get_current_active_verified_user_deps(request: Request = Depends()) -> User:
    """Depends() 패턴용 래퍼"""  
    return get_current_active_verified_user(request)

def get_current_active_superuser_deps(request: Request = Depends()) -> User:
    """Depends() 패턴용 래퍼"""
    return get_current_active_superuser(request)

# 2. ServiceConfig에 명시적 AuthMiddleware 제어 옵션 추가 (선택사항)
@dataclass
class ServiceConfig:
    # ... 기존 필드들
    
    # 명시적 AuthMiddleware 제어 (고급 사용자용)
    force_disable_auth_middleware: bool = False
    
    def __post_init__(self):
        # 기존 로직...
        
        # 강제 비활성화 옵션
        if self.force_disable_auth_middleware:
            self.enable_auth = False
```

**사용 시나리오**:
```python
# 시나리오 1: 표준 Non-IAM 서비스 (권장)
service_config = create_service_config(
    service_type=ServiceType.NON_IAM_SERVICE,  # 자동으로 enable_auth=False
    # AuthMiddleware 자동 비활성화, Kong 헤더 기반 인증 사용
)

# 시나리오 2: IAM 서비스에서 Gateway 모드 강제 (특수 케이스)
service_config = create_service_config(
    service_type=ServiceType.IAM_SERVICE,
    force_disable_auth_middleware=True,  # 명시적 비활성화
    # IAM 서비스이지만 Gateway 뒤에서만 동작하는 특수 구성
)
```

### 1.3 Configuration 표준화 개선 (중요)

**현재 상황**: `CommonSettings` 기반 구조가 이미 구현됨
**구현 상태**: ✅ 기본 구조는 완성, 서비스별 확장 필요

**현재 CommonSettings 구조**:
```python
# mysingle_quant/core/config.py
class CommonSettings(BaseSettings):
    # Project Information
    PROJECT_NAME: str = "Quant Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Auth Settings
    AUTH_HOST: str = "http://localhost:8001"
    AUTH_API_VERSION: str = "v1"
    AUTH_PUBLIC_PATHS: list[str] = [...]
    
    # Database Settings
    MONGODB_SERVER: str = "localhost:27017"
    MONGODB_USERNAME: str = "root"
    MONGODB_PASSWORD: str = "example"
    
    # Security & Token Settings
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # API Gateway Settings
    USE_API_GATEWAY: bool = True
    API_GATEWAY_URL: str = "http://localhost:8000"
    KONG_JWT_SECRET_FRONTEND: str = "..."
    
    # CORS Settings
    @property
    def all_cors_origins(self) -> list[str]:
        # 환경별 CORS 오리진 자동 설정
```

**서비스별 확장 패턴**:
```python
# app/core/config.py (각 서비스)
from mysingle_quant.core.config import CommonSettings

class BacktestServiceSettings(CommonSettings):
    SERVICE_NAME: str = "backtest-service"
    
    # 서비스별 설정
    ML_SERVICE_URL: str = "http://kong-gateway:8000/ml"
    STRATEGY_SERVICE_URL: str = "http://kong-gateway:8000/strategy"
    
    # 백테스트 전용 설정
    MAX_CONCURRENT_BACKTESTS: int = 5
    BACKTEST_TIMEOUT_MINUTES: int = 60
    
    class Config:
        env_prefix = "BACKTEST_"

settings = BacktestServiceSettings()
```

**개선 요구사항**:
- 서비스별 설정 클래스 템플릿 제공
- Gateway URL 자동 구성 로직 개선

## 2. 구조 개선사항

### 2.1 서비스 타입 확장 (부분 완료)

**현재**: ServiceType.IAM_SERVICE vs NON_IAM_SERVICE만 지원
**구현 상태**: ✅ 기본 구조 완성, 확장 필요

**현재 구현된 ServiceType**:
```python
# mysingle_quant/core/service_types.py - 현재 상태
class ServiceType(Enum):
    IAM_SERVICE = "iam"
    NON_IAM_SERVICE = "non_iam"
```

**제안 확장안**:
```python
class ServiceType(Enum):
    IAM_SERVICE = "iam"
    NON_IAM_SERVICE = "non_iam"
    
    # 새로운 세분화된 타입들
    ORCHESTRATOR_SERVICE = "orchestrator"  # Journey Orchestrator
    EXECUTION_SERVICE = "execution"        # Backtest, Optimization  
    DATA_SERVICE = "data"                  # Market Data, Strategy
    ANALYTICS_SERVICE = "analytics"        # Dashboard
    UTILITY_SERVICE = "utility"            # Notification, GenAI, ML

class ServiceCategory(Enum):
    CORE = "core"           # IAM, Orchestrator
    COMPUTE = "compute"     # Execution services
    DATA = "data"           # Data services  
    FRONTEND = "frontend"   # Analytics services
    SUPPORT = "support"     # Utility services
```

### 2.2 ServiceConfig 개선 (부분 완료)

**현재**: ServiceConfig가 이미 잘 구현되어 있음
**구현 상태**: ✅ 기본 완성, 세부 개선 필요

**현재 ServiceConfig 구조**:
```python
@dataclass
class ServiceConfig:
    service_name: str
    service_type: ServiceType
    service_version: str = "1.0.0"
    description: Optional[str] = None
    
    # Feature flags
    enable_auth: bool = True
    enable_database: bool = True  
    enable_metrics: bool = True
    enable_health_check: bool = True
    enable_audit_logging: bool = True
    enable_oauth: bool = False
    
    # Network settings
    cors_origins: Optional[list[str]] = None
    
    # Lifecycle
    lifespan: Optional[Callable] = None
```

**제안 개선안**:
```python
@dataclass  
class ServiceConfig:
    service_name: str
    service_type: ServiceType
    service_category: Optional[ServiceCategory] = None  # 새로운 필드
    service_version: str = "1.0.0"
    description: Optional[str] = None
    
    # Enhanced feature flags
    enable_auth: bool = True
    enable_database: bool = True
    enable_metrics: bool = True
    enable_health_check: bool = True
    enable_audit_logging: bool = True
    enable_oauth: bool = False
    enable_internal_routes: bool = False  # 새로운 플래그
    
    # Enhanced network settings
    cors_origins: Optional[list[str]] = None
    public_paths: list[str] = field(default_factory=lambda: [
        "/health", "/ready", "/docs", "/openapi.json", "/metrics"
    ])
    
    # Gateway integration
    gateway_base_url: Optional[str] = None
    internal_route_suffix: str = "-internal"
    
    # Lifecycle
    lifespan: Optional[Callable] = None
```

## 3. 성능 및 안정성 개선

### 3.1 연결 풀링 표준화 (완료됨) ✅

**현재 상황**: 표준 HTTP 클라이언트 팩토리 구현 완료
**구현 상태**: ✅ 완전 구현됨

**구현된 기능들**:
- `ServiceHttpClient`: httpx 기반 비동기 HTTP 클라이언트 (연결 풀링 지원)
- `ServiceHttpClientManager`: 싱글톤 패턴으로 서비스별 클라이언트 재사용
- 자동 URL 구성: Gateway/Direct 모드 자동 감지
- App Factory 통합: 생명주기 자동 관리 (startup/shutdown)
- 환경 설정: 타임아웃, 연결 수 등 환경 변수로 제어

**실제 사용 패턴**:
```python
# 현재 구현된 표준 패턴
from mysingle_quant.core import get_service_http_client, make_service_request

# 싱글톤 클라이언트 (권장)
strategy_client = get_service_http_client("strategy-service")
response = await strategy_client.get("/strategies")

# 편의 함수
response = await make_service_request(
    service_name="backtest-service",
    method="POST", 
    endpoint="/backtests/start",
    json={"strategy_id": "123"}
)
```

**자동 URL 구성**:
- Gateway 모드: `http://localhost:8000/strategy`
- Direct 모드: `http://localhost:8003`
- Docker 환경: `http://strategy-service:8000`

### 3.2 로깅 표준화 (부분 완료)

**현재 상황**: `setup_logging()`, `get_logger()` 이미 구현됨
**구현 상태**: ✅ 기본 로깅 완성, 구조화 로깅 개선 필요

**현재 로깅 구조**:
```python
# mysingle_quant/core/logging_config.py - 이미 구현됨
def setup_logging():
    """서비스별 표준 로깅 설정"""
    
def get_logger(name: str):
    """로거 인스턴스 획득"""
```

**제안 개선안**:
```python
# 구조화 로깅 및 Correlation ID 지원 추가
import structlog
from contextvars import ContextVar

# Correlation ID 컨텍스트 변수
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')

def configure_structured_logging(
    service_name: str,
    log_level: str = "INFO",
    enable_correlation_id: bool = True
):
    """구조화된 로깅 설정"""
    processors = [
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        add_service_name_processor(service_name),
    ]
    
    if enable_correlation_id:
        processors.append(add_correlation_id_processor)
    
    processors.append(structlog.processors.JSONRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            min_level=getattr(structlog, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )

def add_correlation_id_processor(logger, method_name, event_dict):
    """Correlation ID를 로그에 추가"""
    correlation_id = correlation_id_var.get()
    if correlation_id:
        event_dict['correlation_id'] = correlation_id
    return event_dict

def add_service_name_processor(service_name: str):
    """서비스 이름을 로그에 추가"""
    def processor(logger, method_name, event_dict):
        event_dict['service'] = service_name
        return event_dict
    return processor
```

## 4. 개발자 경험 개선

### 4.1 CLI 도구 추가

**요구사항**: 서비스 생성/관리 CLI

```python
# mysingle_quant/cli/service_generator.py 신규
import click
from pathlib import Path

@click.group()
def cli():
    """MySingle Quant 개발 도구"""
    pass

@cli.command()
@click.argument('service_name')
@click.option('--service-type', type=click.Choice(['iam', 'orchestrator', 'execution', 'data', 'analytics', 'utility']))
@click.option('--enable-internal', is_flag=True, help='내부 API 라우터 생성')
def create_service(service_name: str, service_type: str, enable_internal: bool):
    """새 서비스 스켈레톤 생성"""
    # 서비스 템플릿 생성 로직
    pass

@cli.command()
@click.argument('service_path')
def validate_service(service_path: str):
    """서비스 구성 검증"""
    # 설정, 라우터, 미들웨어 검증
    pass
```

### 4.2 테스트 유틸리티

**요구사항**: 인증 테스트 헬퍼

```python
# mysingle_quant/testing/auth_helpers.py 신규
from typing import Dict, Any
import pytest
from fastapi.testclient import TestClient

class AuthTestHelper:
    """인증 테스트 헬퍼"""
    
    @staticmethod
    def create_test_headers(
        user_id: str = "test-user-123",
        email: str = "test@example.com",
        is_active: bool = True,
        is_verified: bool = True,
        is_superuser: bool = False
    ) -> Dict[str, str]:
        """테스트용 Gateway 헤더 생성"""
        return {
            "X-User-Id": user_id,
            "X-User-Email": email,
            "X-User-Active": str(is_active).lower(),
            "X-User-Verified": str(is_verified).lower(),
            "X-User-Superuser": str(is_superuser).lower(),
            "Correlation-Id": "test-correlation-123"
        }
    
    @staticmethod
    def create_jwt_token(payload: Dict[str, Any]) -> str:
        """테스트용 JWT 토큰 생성"""
        # JWT 생성 로직
        pass
```

## 5. 우선순위별 실행 계획

### Phase 1 (즉시 실행 - 1주일)
- [x] ~~App Factory 구현 및 배포~~ ✅ 완료됨
- [x] ~~HTTP 클라이언트 표준화 구현~~ ✅ 완료됨
- [ ] DI 함수 호환성 개선 (Depends() 래퍼 추가)
- [ ] ServiceConfig 확장 (ServiceCategory, internal_routes 플래그)
- [ ] Configuration 상속 패턴 문서화

### Phase 2 (중요 - 2주일)  
- [x] 구조화된 로깅 시스템 구현
- [ ] 서비스별 설정 템플릿 생성
- [x] Kong Gateway 헤더 표준화 완료 ✅ 이미 표준화 되어 있음
- [ ] 서비스 타입 확장 (ORCHESTRATOR, EXECUTION 등)

### Phase 3 (개선 - 4주일)
- [ ] CLI 도구 개발 (서비스 생성기)
- [ ] 테스트 유틸리티 확장
- [x] 메트릭 수집 고도화 ✅ 추가작업 없이 기존 구성 확정
- [ ] 문서 자동 생성 도구

## 6. 마이그레이션 가이드

### 기존 서비스 업데이트

1. **App Factory 적용** ✅ 이미 적용됨
```python
# 현재 사용 중인 패턴 (올바름)
from mysingle_quant.core import create_fastapi_app, create_service_config

app = create_fastapi_app(
    service_config=create_service_config(...),
    document_models=models.document_models
)
```

2. **Configuration 상속 패턴 적용**
```python
# Before (개별 설정)
class Settings(BaseSettings):
    PROJECT_NAME: str = "My Service"
    MONGODB_SERVER: str = "localhost:27017"
    # ... 모든 설정 반복

# After (CommonSettings 상속)  
from mysingle_quant.core.config import CommonSettings

class MyServiceSettings(CommonSettings):
    SERVICE_NAME: str = "my-service"
    
    # 서비스별 추가 설정만
    MY_SERVICE_SPECIFIC_CONFIG: str = "value"
    
    class Config:
        env_prefix = "MY_SERVICE_"

settings = MyServiceSettings()
```

3. **DI 함수 현행화**
```python
# 권장: Request 기반 패턴 (최신)
from fastapi import Request
from mysingle_quant.auth.deps import get_current_active_user

@router.get("/")
async def endpoint(request: Request):
    user = get_current_active_user(request)
    return {"user_id": str(user.id)}

# 대안: Depends 패턴 (호환성)
from fastapi import Depends
from mysingle_quant.auth.deps import get_current_active_user_middleware

@router.get("/")
async def endpoint(user: User = Depends(get_current_active_user_middleware)):
    return {"user_id": str(user.id)}
```

### 검증 체크리스트

- [x] ~~모든 서비스에서 App Factory 사용~~ ✅ 완료
- [ ] CommonSettings 상속 패턴 적용
- [ ] Request 기반 DI 패턴으로 전환 (또는 호환 함수 사용)
- [ ] Kong Gateway 헤더 표준 준수
- [ ] 테스트 코드 업데이트
- [ ] 환경 설정 마이그레이션
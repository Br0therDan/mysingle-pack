# App Factory Usage Guide

**Version:** 2.2.1 | **Module:** `mysingle.core.app_factory`

> **📖 Core Module Overview:** [mysingle.core README](../../src/mysingle/core/README.md)

FastAPI application factory for standardized microservice creation.

---

## Overview

`mysingle.core.app_factory` implements the factory pattern for creating consistent FastAPI applications in the MySingle Quant ecosystem.

**For standard initialization pattern, see:** [Core README - Standard Service Initialization](../../src/mysingle/core/README.md#1-standard-service-initialization)

### Supported Service Types

| Service Type      | Description            | Authentication       |
| ----------------- | ---------------------- | -------------------- |
| `IAM_SERVICE`     | Auth/authz service     | Direct JWT + OAuth2  |
| `NON_IAM_SERVICE` | Business logic service | Kong Gateway headers |

**For detailed service type explanation, see:** [Core README - Service Types](../../src/mysingle/core/README.md#service-types)

---

## Quick Start

### ServiceConfig

서비스의 모든 설정을 담는 데이터 클래스입니다.

```python
from dataclasses import dataclass
from mysingle.core import ServiceType

@dataclass
class ServiceConfig:
    # 필수 필드
    service_name: str           # 서비스 식별자
    service_type: ServiceType   # IAM_SERVICE | NON_IAM_SERVICE
    service_version: str        # 버전 (e.g., "1.0.0")

    # 선택적 필드 (기본값 있음)
    description: str | None = None
    enable_database: bool = True
    enable_audit_logging: bool = True
    enable_metrics: bool = True
    enable_health_check: bool = True
    cors_origins: list[str] | None = None
    lifespan: Callable | None = None

    # 자동 설정 필드 (ServiceType에 따라 자동 결정)
    enable_auth: bool           # __post_init__에서 설정
    enable_oauth: bool          # __post_init__에서 설정
    is_gateway_downstream: bool # __post_init__에서 설정
```

### 자동 설정 로직

`ServiceConfig`는 `service_type`에 따라 인증 관련 설정을 자동으로 구성합니다:

```python
def __post_init__(self):
    if self.service_type == ServiceType.IAM_SERVICE:
        self.enable_auth = True          # JWT 직접 검증
        self.enable_oauth = True         # OAuth2 제공
        self.enable_user_management = True
        self.is_gateway_downstream = False
    else:  # NON_IAM_SERVICE
        self.enable_auth = False         # Gateway에서 인증 처리
        self.enable_oauth = False
        self.enable_user_management = False
        self.is_gateway_downstream = True
```

---

## 프로세스 플로우

애플리케이션 생성 및 생명주기 전체 과정을 이해하려면 플로우차트를 참고하세요:

📊 **[APP Factory 플로우차트 보기](./APP_FACTORY_FLOWCHART.md)**

주요 프로세스:
1. **Main Flow**: `create_fastapi_app()` 실행 흐름
2. **Lifespan Process**: Startup/Shutdown 생명주기
3. **Middleware Stack**: 미들웨어 실행 순서
4. **Configuration Options**: ServiceConfig 옵션 구조

---

## 빠른 시작

### 1. 기본 구조

모든 서비스는 다음 구조를 따릅니다:

```
service-name/
├── app/
│   ├── __init__.py
│   ├── main.py              # 애플리케이션 진입점
│   ├── api/
│   │   └── v1/
│   │       └── api_v1.py    # API 라우터
│   ├── core/
│   │   └── config.py        # 서비스별 설정
│   ├── models/              # Beanie Document 모델
│   │   └── __init__.py
│   └── services/            # 비즈니스 로직
├── Dockerfile
├── pyproject.toml
└── README.md
```

### 2. 최소 구현 (Minimal Setup)

가장 간단한 서비스 생성 예제:

```python
# app/main.py
from fastapi import FastAPI
from mysingle.core import (
    ServiceType,
    create_fastapi_app,
    create_service_config,
    setup_logging,
)

from app.core.config import settings

setup_logging()

# ServiceConfig 생성
service_config = create_service_config(
    service_name=settings.SERVICE_NAME,

    service_version="1.0.0",
    description="My Awesome Service",
)

# FastAPI 앱 생성
app = create_fastapi_app(service_config=service_config)
```

이것만으로도 다음 기능이 자동으로 추가됩니다:
- ✅ CORS 설정
- ✅ Health Check (`/health`, `/ready`)
- ✅ Metrics 수집 (`/metrics`)
- ✅ Structured Logging
- ✅ MongoDB 연결 (기본 활성화)

---

## 서비스 타입별 구현

### IAM Service (인증 서비스)

IAM 서비스는 **직접 JWT를 검증**하고 **사용자 관리 기능**을 제공합니다.

```python
# services/iam-service/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from mysingle.core import (
    ServiceType,
    create_fastapi_app,
    create_service_config,
    get_logger,
    setup_logging,
)

from app.core.config import settings

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """IAM 서비스 생명주기 관리"""
    # Startup
    logger.info("🚀 Starting IAM Service...")

    try:
        # 초기 데이터 생성은 app_factory의 lifespan에서 자동 처리
        # - create_first_super_admin()
        # - create_test_users() (dev/local only)

        # 추가 초기화 로직이 있다면 여기에 작성
        pass

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    logger.info("✅ IAM Service started successfully")

    yield

    # Shutdown
    try:
        logger.info("🛑 Shutting down IAM Service...")
        # 커스텀 정리 로직
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

    logger.info("👋 IAM Service shutdown completed")


# ServiceConfig 생성 (IAM_SERVICE)
service_config = create_service_config(
    service_type=ServiceType.IAM_SERVICE,
    service_name=settings.SERVICE_NAME,
    service_version=settings.APP_VERSION,
    description="Identity and Access Management Service",
    enable_audit_logging=True,  # 감사 로그 활성화 (보안 중요)
    lifespan=lifespan,
)

# FastAPI 앱 생성
# IAM_SERVICE는 자동으로 다음 기능 활성화:
# - enable_auth=True (JWT 직접 검증)
# - enable_oauth=True (OAuth2 라우터)
# - Auth 라우터: /api/v1/auth, /api/v1/users
app = create_fastapi_app(service_config=service_config)

# IAM 서비스는 User, OAuthAccount 모델이 자동으로 등록됨
# 추가 Document 모델이 필요하면 document_models 파라미터 사용
```

#### IAM Service 특징

1. **자동 인증 설정**
   - `enable_auth=True`: JWT 검증 미들웨어 자동 추가
   - `enable_oauth=True`: OAuth2 라우터 자동 포함
   - Auth Exception Handlers 자동 등록

2. **기본 라우터**
   - `/api/v1/auth/*`: 로그인, 회원가입, 토큰 갱신
   - `/api/v1/users/*`: 사용자 CRUD, 프로필 관리
   - `/api/v1/auth/oauth/*`: Google, GitHub OAuth2 (enable_oauth=True)

3. **자동 초기화**
   - Super Admin 계정 자동 생성 (최초 실행 시)
   - Test Users 생성 (개발 환경만)

### Non-IAM Service (일반 서비스)

비즈니스 로직을 담당하는 서비스입니다. **API Gateway에서 인증을 처리**합니다.

```python
# services/backtest-service/app/main.py
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI
from mysingle.core import (
    ServiceType,
    create_fastapi_app,
    create_service_config,
)
from mysingle.core import get_structured_logger, setup_logging

from app import models
from app.api.v1.api_v1 import api_router
from app.core.config import settings

setup_logging()
logger = get_structured_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Backtest 서비스 생명주기 관리"""
    logger.info("🚀 Starting Backtest Service...")

    try:
        # 외부 서비스 HTTP 클라이언트 초기화
        from app.services.service_factory import service_factory

        service_factory.initialize()
        logger.info("✅ Service factory initialized")

        # 추가 리소스 초기화
        # - 캐시 워밍업
        # - 백그라운드 작업 시작
        # - 외부 API 연결 확인 등

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    logger.info("✅ Backtest Service started successfully")

    yield

    # Shutdown
    try:
        logger.info("🛑 Shutting down Backtest Service...")

        # 리소스 정리
        from app.services.service_factory import service_factory
        await service_factory.shutdown()

        logger.info("✅ Service factory cleanup completed")

    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

    logger.info("👋 Backtest Service shutdown completed")


def create_app() -> FastAPI:
    """애플리케이션 팩토리 패턴"""

    # ServiceConfig 생성 (NON_IAM_SERVICE)
    service_config = create_service_config(
        service_name=settings.SERVICE_NAME,

        service_version="1.0.0",
        description="Backtesting Engine Service",
        enable_audit_logging=True,  # API 호출 추적
        enable_metrics=True,        # 성능 모니터링
        lifespan=lifespan,
    )

    # FastAPI 앱 생성
    # NON_IAM_SERVICE는 자동으로:
    # - enable_auth=False (Gateway에서 인증 처리)
    # - is_gateway_downstream=True
    app = cast(
        FastAPI,
        create_fastapi_app(
            service_config=service_config,
            document_models=models.document_models,  # Beanie 모델 등록
        ),
    )

    # 비즈니스 로직 라우터 추가
    app.include_router(api_router)

    return app


# 앱 인스턴스 생성
app = create_app()
```

#### Non-IAM Service 특징

1. **Gateway 의존**
   - `enable_auth=False`: 인증 미들웨어 없음
   - `is_gateway_downstream=True`: Gateway 헤더 신뢰
   - Gateway가 `X-User-ID`, `X-User-Email` 헤더 전달

2. **인증 컨텍스트 사용**
   ```python
   from fastapi import Depends
   from mysingle.auth.dependencies import get_current_user_from_gateway

   @router.get("/my-endpoint")
   async def my_endpoint(
       user_context: dict = Depends(get_current_user_from_gateway)
   ):
       user_id = user_context["user_id"]
       user_email = user_context["email"]
       # 비즈니스 로직...
   ```

3. **문서화 엔드포인트**
   - Development 환경에서만 `/docs`, `/openapi.json` 활성화
   - Production에서는 보안을 위해 비활성화

---

## 고급 설정

### Document Models 등록

MongoDB Beanie 모델을 사용하는 경우:

```python
# app/models/__init__.py
from beanie import Document
from pydantic import Field

class BacktestResult(Document):
    strategy_id: str
    profit: float
    sharpe_ratio: float

    class Settings:
        name = "backtest_results"

class Portfolio(Document):
    user_id: str
    positions: list[dict]

    class Settings:
        name = "portfolios"

# 모델 리스트 내보내기
document_models = [BacktestResult, Portfolio]
```

```python
# app/main.py
from app import models

app = create_fastapi_app(
    service_config=service_config,
    document_models=models.document_models,  # 모델 등록
)
```

### Custom CORS 설정

특정 Origin만 허용:

```python
service_config = create_service_config(
    service_name="my-service",

    service_version="1.0.0",
    cors_origins=[
        "https://app.example.com",
        "https://admin.example.com",
    ],
)
```

### Metrics 설정 커스터마이징

```python
from mysingle.metrics import MetricsConfig

# app/main.py 내에서
service_config = create_service_config(
    service_name="my-service",

    service_version="1.0.0",
    enable_metrics=True,  # 메트릭 활성화
)

app = create_fastapi_app(service_config=service_config)

# 메트릭 설정은 app_factory 내부에서 자동 구성:
# - max_duration_samples=1000
# - enable_percentiles=True
# - retention_period=3600s
# - cleanup_interval=300s
```

### 감사 로그 비활성화

```python
service_config = create_service_config(
    service_name="my-service",

    service_version="1.0.0",
    enable_audit_logging=settings.AUDIT_LOGGING_ENABLED,  # 감사 로그 비활성화
)
```

### Database 비활성화 (Stateless Service)

```python
service_config = create_service_config(
    service_name="proxy-service",

    service_version="1.0.0",
    enable_database=False,  # DB 연결 없음
)

# document_models도 전달하지 않음
app = create_fastapi_app(service_config=service_config)
```

### Public Paths 확장

인증이 필요 없는 경로 추가:

```python
service_config = create_service_config(
    service_name="my-service",
    service_type=ServiceType.IAM_SERVICE,
    service_version="1.0.0",
)

# public_paths는 기본값에 추가됨
# 기본값: ["/health", "/metrics", "/docs", "/openapi.json"]
service_config.public_paths.extend([
    "/api/v1/public/pricing",
    "/api/v1/webhooks/stripe",
])
```

### Custom Lifespan Events

복잡한 초기화/정리 로직:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    """고급 생명주기 관리"""
    # Startup - 여러 리소스 초기화
    logger.info("🚀 Initializing resources...")

    resources = {}

    try:
        # 1. Redis 연결
        from app.cache import RedisManager
        resources["redis"] = await RedisManager.connect()

        # 2. 외부 API 클라이언트
        from app.clients import ExternalAPIClient
        resources["api_client"] = ExternalAPIClient()

        # 3. 백그라운드 작업 시작
        from app.tasks import BackgroundScheduler
        scheduler = BackgroundScheduler()
        await scheduler.start()
        resources["scheduler"] = scheduler

        # 4. 캐시 워밍업
        from app.services import CacheWarmer
        await CacheWarmer.warm_up()

        logger.info("✅ All resources initialized")

    except Exception as e:
        logger.error(f"❌ Resource initialization failed: {e}")
        # 부분 초기화된 리소스 정리
        for resource in resources.values():
            await resource.cleanup()
        raise

    # 리소스를 app.state에 저장
    app.state.resources = resources

    yield

    # Shutdown - 역순으로 정리
    logger.info("🛑 Cleaning up resources...")

    try:
        # 백그라운드 작업 중지
        if "scheduler" in resources:
            await resources["scheduler"].stop()

        # API 클라이언트 정리
        if "api_client" in resources:
            await resources["api_client"].close()

        # Redis 연결 해제
        if "redis" in resources:
            await resources["redis"].disconnect()

        logger.info("✅ All resources cleaned up")

    except Exception as e:
        logger.error(f"❌ Cleanup error: {e}")


service_config = create_service_config(
    service_name="my-service",

    service_version="1.0.0",
    lifespan=lifespan,  # 커스텀 lifespan 전달
)
```

---

## Best Practices

### 1. 환경별 설정 분리

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 환경 변수에서 로드
    SERVICE_NAME: str = "my-service"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"  # development, staging, production

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

```python
# app/main.py
from app.core.config import settings

service_config = create_service_config(
    service_name=settings.SERVICE_NAME,

    service_version=settings.APP_VERSION,
    cors_origins=settings.ALLOWED_ORIGINS,
)
```

### 2. 구조화된 로깅 활용

```python
from mysingle.core import get_structured_logger

logger = get_structured_logger(__name__)

# 구조화된 로그 (JSON 포맷)
logger.info(
    "User action performed",
    extra={
        "user_id": user_id,
        "action": "create_backtest",
        "strategy_id": strategy_id,
        "duration_ms": elapsed_time,
    }
)
```

### 3. Health Check 활용

기본 제공되는 엔드포인트:

```bash
# 기본 상태 확인
curl http://localhost:8000/health

# 응답:
{
  "status": "healthy",
  "service": "my-service",
  "version": "1.0.0",
  "timestamp": "2025-10-31T10:30:00Z"
}

# Kubernetes Readiness Probe
curl http://localhost:8000/ready

# 응답:
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "cache": "ok"
  }
}
```

Kubernetes 배포 설정:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-service
spec:
  containers:
  - name: app
    image: my-service:latest
    livenessProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 30
    readinessProbe:
      httpGet:
        path: /ready
        port: 8000
      initialDelaySeconds: 5
      periodSeconds: 10
```

### 4. Metrics 모니터링

Prometheus에서 수집 가능한 메트릭:

```bash
# 메트릭 조회
curl http://localhost:8000/metrics

# 주요 메트릭:
# - http_requests_total: 총 요청 수
# - http_request_duration_seconds: 요청 처리 시간
# - http_requests_in_progress: 진행 중인 요청 수
# - app_info: 앱 버전 정보
```

Grafana 대시보드 쿼리 예제:

```promql
# 요청 처리량 (RPS)
rate(http_requests_total{service="my-service"}[5m])

# 평균 응답 시간
rate(http_request_duration_seconds_sum[5m])
  / rate(http_request_duration_seconds_count[5m])

# P95 레이턴시
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m]))

# 에러율
rate(http_requests_total{status=~"5.."}[5m])
  / rate(http_requests_total[5m])
```

### 5. Factory Pattern 적용

테스트 용이성을 위해 팩토리 패턴 사용:

```python
# app/main.py
def create_app() -> FastAPI:
    """테스트 가능한 앱 팩토리"""
    service_config = create_service_config(
        service_name="my-service",

        service_version="1.0.0",
    )

    app = create_fastapi_app(
        service_config=service_config,
        document_models=models.document_models,
    )

    # 라우터 등록
    app.include_router(api_router)

    return app

# 프로덕션 인스턴스
app = create_app()
```

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client():
    """테스트 클라이언트"""
    app = create_app()
    return TestClient(app)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### 6. 의존성 주입 활용

```python
from fastapi import Depends
from mysingle.auth.dependencies import get_current_user_from_gateway

@router.post("/backtest")
async def create_backtest(
    data: BacktestRequest,
    user_context: dict = Depends(get_current_user_from_gateway),
    db: AsyncIOMotorClient = Depends(get_database),
):
    """Gateway에서 인증된 사용자 정보 자동 주입"""
    user_id = user_context["user_id"]

    # 비즈니스 로직
    result = await backtest_service.run(
        user_id=user_id,
        strategy=data.strategy,
    )

    return result
```

---

## 트러블슈팅

### 문제: MongoDB 연결 실패

**증상**:
```
❌ Failed to connect to MongoDB: [Errno 61] Connection refused
```

**해결**:

1. MongoDB가 실행 중인지 확인:
   ```bash
   docker-compose up -d mongodb
   ```

2. 환경 변수 확인:
   ```bash
   echo $MONGODB_URL
   # 예상: mongodb://localhost:27017
   ```

3. Mock DB로 실행 (개발 환경):
   ```python
   # .env
   MOCK_DATABASE=true
   ```

### 문제: 인증 미들웨어 오류 (IAM Service)

**증상**:
```
⚠️ Authentication middleware not available: No module named 'mysingle.auth'
```

**해결**:

1. mysingle-quant 패키지 버전 확인:
   ```bash
   pip list | grep mysingle
   # mysingle-quant >= 0.2.0 필요
   ```

2. 패키지 재설치:
   ```bash
   pip install --upgrade mysingle-quant
   ```

### 문제: CORS 에러

**증상**:
```
Access to fetch at 'http://api.example.com' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**해결**:

```python
service_config = create_service_config(
    service_name="my-service",

    service_version="1.0.0",
    cors_origins=[
        "http://localhost:3000",
        "https://app.example.com",
    ],
)
```

또는 환경 변수 사용:

```python
# app/core/config.py
class Settings(BaseSettings):
    ALLOWED_ORIGINS: list[str] = ["*"]  # 개발 환경만 사용

settings = Settings()
```

### 문제: Metrics가 수집되지 않음

**증상**:
```
curl http://localhost:8000/metrics
# 404 Not Found
```

**해결**:

1. Metrics 활성화 확인:
   ```python
   service_config = create_service_config(
       service_name="my-service",

       service_version="1.0.0",
       enable_metrics=True,  # 확인
   )
   ```

2. Prometheus 클라이언트 설치 확인:
   ```bash
   pip list | grep prometheus
   # prometheus-client가 설치되어 있어야 함
   ```

### 문제: Gateway 헤더가 전달되지 않음 (Non-IAM Service)

**증상**:
```python
user_context = await get_current_user_from_gateway(request)
# KeyError: 'X-User-ID'
```

**해결**:

1. API Gateway 설정 확인 (Kong):
   ```yaml
   # kong.yml
   plugins:
   - name: jwt
     config:
       header_names:
       - X-User-ID
       - X-User-Email
   ```

2. 로컬 테스트 시 헤더 직접 전달:
   ```python
   headers = {
       "X-User-ID": "test-user-123",
       "X-User-Email": "test@example.com",
   }
   response = client.get("/api/v1/backtest", headers=headers)
   ```

### 문제: 개발 환경에서 /docs 접근 불가

**증상**:
```
http://localhost:8000/docs
# 404 Not Found
```

**해결**:

환경 변수 확인:
```bash
# .env
ENVIRONMENT=development  # 또는 local

# production/staging이면 docs가 비활성화됨
```

---

## 체크리스트

새 서비스 생성 시 확인사항:

- [ ] `ServiceType` 올바르게 선택 (IAM vs Non-IAM)
- [ ] `service_name`이 고유하고 명확함
- [ ] `service_version` 시맨틱 버전 사용 (e.g., `1.0.0`)
- [ ] Document Models 등록 (`document_models` 파라미터)
- [ ] Custom `lifespan` 함수 구현 (필요 시)
- [ ] CORS Origins 설정 (프로덕션)
- [ ] 환경 변수 분리 (`.env`, `.env.production`)
- [ ] Health Check 엔드포인트 테스트
- [ ] Metrics 수집 확인
- [ ] 구조화된 로깅 사용
- [ ] Kubernetes Probes 설정
- [ ] API 문서 확인 (`/docs`)

---

## 참고 자료

- 📊 [APP Factory 플로우차트](./APP_FACTORY_FLOWCHART.md)
- 📘 [MySingle Pack 사용 가이드](./MYSINGLE_PACK_USAGE_GUIDE.md)
- 🔐 [Kong API Gateway 구성 가이드](./KONG_API_GATEWAY_CONFIGURATION_GUIDE.md)
- 🏗️ [마이크로서비스 최적화 계획](../docs/MICROSERVICE_OPTIMIZATION_PLAN.md)
- 🚀 [Phase 1 완료 보고서](../docs/Inter-service-communications/copilot-instructions.md)

---

## 변경 이력

**v1.5.0 (2025-11-20) - Phase 1 완료:**
- ✅ Kong Gateway JWT Plugin 기반 단일 인증 표준 확립
- ✅ HTTP BaseClient 제거, gRPC 표준화
- ✅ Consumer 관련 레거시 함수 제거
- ✅ 코드 간소화 (77개 Python 파일)
- ✅ 인증 우회 메커니즘 (MYSINGLE_AUTH_BYPASS)
- ✅ 영문 문서화 (AGENTS.md, copilot-instructions.md)

---

## 요약

`create_fastapi_app()` 팩토리는 다음을 자동화합니다:

1. **표준 미들웨어 구성** - CORS, Auth, Metrics, Audit
2. **환경별 최적화** - Development vs Production
3. **생명주기 관리** - Startup/Shutdown 이벤트
4. **관측성 제공** - Logging, Metrics, Health Checks
5. **보안 기본값** - 인증, 감사 로그, CORS

**간단하게 시작하고, 필요에 따라 확장하세요!** 🚀

---

**Document Version:** 2.0
**Last Updated:** 2025-11-20
**Package Version:** v1.5.0

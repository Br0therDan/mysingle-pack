# MySingle Package 활용 가이드
**최근업데이트 : 2025-11-20**

## 개요

MySingle-Quant Package는 마이크로서비스 아키텍처를 위한 통합 개발 프레임워크입니다. 이 가이드는 주요 기능들의 활용 방법을 설명합니다.

**Package Version:** v1.5.0 (Released: 2025-11-20)

**주요 업데이트 (2025-11-20 - Phase 1 완료):**
- ✅ Kong Gateway JWT Plugin 기반 단일 인증 표준 확립
- ✅ Request.state.user 기반 통합 인증 패턴 정립
- ✅ HTTP BaseClient 제거, gRPC BaseGrpcClient 표준화
- ✅ Consumer 관련 레거시 함수 제거 (Kong JWT Plugin 중심)
- ✅ 인증 우회 메커니즘 구현 (MYSINGLE_AUTH_BYPASS)
- ✅ 코드 간소화: 77개 Python 파일로 정리
- ✅ 영문 문서화 완료 (AGENTS.md, copilot-instructions.md)

**이전 업데이트 (2025-10-31):**
- ✅ Depends() vs 직접 호출 패턴 가이드 추가
- ✅ External/Internal 라우터 케이스별 사용법 추가
- ✅ 데코레이터 적절한 사용 케이스 명시 (라우터 함수 직접 적용 금지)
- ✅ MSA 표준 패턴 (직접 호출 우선) 명확화
- ✅ MongoDB/Beanie ODM 환경에 맞게 Depends() 사용 케이스 재정의

## 목차

1. [FastAPI App 생성](#1-fastapi-app-생성)
2. [인증 시스템 (Authentication)](#2-인증-시스템-authentication)
3. [Kong Gateway 헤더 표준화](#3-kong-gateway-헤더-표준화)
4. [통합 로깅 시스템](#4-통합-로깅-시스템)
5. [HTTP Client](#5-http-client)
6. [모니터링 메트릭](#6-모니터링-메트릭)
7. [감사 로깅 (Audit Logging)](#7-감사-로깅-audit-logging)
8. [종합 활용 예시](#8-종합-활용-예시)
9. [베스트 프랙티스](#9-베스트-프랙티스)
10. [트러블슈팅](#10-트러블슈팅)

---

## 권장 임포트 경로

루트(`mysingle`)에서도 주요 심볼을 그대로 사용할 수 있지만, 가능한 서브패키지 경로를 권장합니다. 이렇게 하면 순환참조를 피하고, 필요한 모듈만 지연 로딩하여 초기화 비용을 줄일 수 있습니다.

- Core (루트에서도 노출 유지)
    - 권장: `from mysingle.core import create_fastapi_app, CommonSettings, settings, get_settings, init_mongo, get_mongodb_url, get_database_name`
    - 루트도 가능: `from mysingle import create_fastapi_app, CommonSettings, settings, get_settings, init_mongo, get_mongodb_url, get_database_name`

- Logging
    - 권장: `from mysingle.core import get_logger, setup_logging, configure_structured_logging`
    - 루트도 가능: `from mysingle import get_logger`

- Database
    - 권장: `from mysingle.database import BaseDuckDBManager`
    - 루트도 가능: `from mysingle import BaseDuckDBManager`

- Clients
    - 권장: `from mysingle.clients import BaseServiceClient`
    - 루트도 가능: `from mysingle import BaseServiceClient`

루트 패키지는 지연 로딩(lazy export) 구조입니다. 심볼 접근 시점에만 해당 서브패키지를 가져오므로, 불필요한 의존성 로딩을 줄일 수 있습니다.

---

## 1. FastAPI App 생성

### 1.1 개요

MySingle Package는 **Application Factory 패턴**을 사용하여 표준화되고 일관된 FastAPI 애플리케이션을 생성합니다. 이를 통해 MSA(Microservices Architecture) 환경에서 모든 서비스가 동일한 구조와 기능을 갖도록 보장합니다.

### 1.2 주요 기능

- ✅ **표준화된 설정**: `ServiceConfig`를 통한 선언적 서비스 구성
- ✅ **자동 미들웨어**: CORS, Auth, Metrics, Audit 자동 추가
- ✅ **서비스 타입별 전략**: IAM vs Non-IAM 자동 분기
- ✅ **생명주기 관리**: Startup/Shutdown 이벤트 통합
- ✅ **관측성 내장**: Logging, Metrics, Health Check 기본 제공

### 1.3 빠른 시작

```python
from mysingle.core import (
    ServiceType,
    create_fastapi_app,
    create_service_config,
    setup_logging,
)

# 로깅 초기화
setup_logging()

# 서비스 설정 생성
service_config = create_service_config(
    service_name="my-service",
    service_type=ServiceType.NON_IAM_SERVICE,
    service_version="1.0.0",
    description="My Awesome Service",
)

# FastAPI 앱 생성
app = create_fastapi_app(service_config=service_config)
```

이것만으로 다음 기능이 자동으로 추가됩니다:
- ✅ CORS 설정
- ✅ Health Check (`/health`, `/ready`)
- ✅ Metrics 수집 (`/metrics`)
- ✅ Structured Logging
- ✅ MongoDB 연결

### 1.4 서비스 타입

| 서비스 타입       | 설명                 | 인증 방식         | 사용 사례                    |
| ----------------- | -------------------- | ----------------- | ---------------------------- |
| `IAM_SERVICE`     | 인증/인가 서비스     | 직접 JWT 검증     | 사용자 관리, 인증 서버       |
| `NON_IAM_SERVICE` | 일반 비즈니스 서비스 | Gateway 헤더 기반 | Backtest, ML, Market Data 등 |

### 1.5 상세 가이드

FastAPI 애플리케이션 생성에 대한 전체 가이드는 다음 문서를 참고하세요:

📘 **[APP Factory 사용 가이드](./APP_FACTORY_USAGE_GUIDE.md)**

주요 내용:
- 핵심 개념 및 ServiceConfig 설명
- IAM/Non-IAM 서비스 구현 예제
- 고급 설정 (Document Models, CORS, Metrics 등)
- Best Practices 및 트러블슈팅
- 생명주기 관리 및 리소스 정리

📊 **[APP Factory 플로우차트](./APP_FACTORY_FLOWCHART.md)**

프로세스 플로우:
- Main Flow: `create_fastapi_app()` 실행 흐름
- Lifespan Process: Startup/Shutdown 생명주기
- Middleware Stack: 미들웨어 실행 순서
- Configuration Options: ServiceConfig 옵션 구조

---

## 2. 인증 시스템 (Authentication)

### 2.1 개요

MySingle 패키지의 인증 시스템은 Kong Gateway와 완전히 통합된 Request 기반 인증 의존성 시스템을 제공합니다.

**Phase 1 완료 (v1.5.0):**
- ✅ Kong Gateway JWT Plugin 기반 단일 표준 확립
- ✅ Consumer 관련 레거시 함수 제거
- ✅ Request.state.user 통합 인증 패턴
- ✅ 5개 핵심 인증 함수로 간소화

### 2.2 주요 특징

- **직접 호출 패턴 (MSA 표준)**: Request 기반 직접 호출로 간결하고 유연한 인증 처리
- **Kong Gateway 완전 지원**: JWT Plugin 기반 헤더 인증으로 높은 성능
- **User 캐싱 시스템**: Redis + In-Memory 캐싱으로 DB 조회 최소화
- **서비스 타입별 자동 인증**: IAM vs NON_IAM 서비스 구분
- **단위 테스트 지원**: MYSINGLE_AUTH_BYPASS 환경 변수 기반 인증 우회

### 2.3 기본 사용법

#### 🔷 직접 호출 패턴 (권장 - MSA 표준)

mysingle-quant 프로젝트는 **직접 호출 방식을 표준**으로 채택합니다. 이는 MSA 아키텍처에서 Gateway가 인증을 처리하고, 내부 서비스는 간결하고 유연한 로직에 집중하기 위함입니다.

```python
from fastapi import Request, APIRouter
from mysingle.auth.deps import (
    get_current_user,
    get_current_active_user,
    get_current_active_verified_user,
    get_current_active_superuser,
    get_current_user_optional,
)

router = APIRouter()

@router.get("/profile")
async def get_user_profile(request: Request):
    """사용자 프로필 조회 - 활성 사용자 필수"""
    user = get_current_active_user(request)
    return {"user_id": str(user.id), "email": user.email}

@router.get("/admin")
async def admin_only(request: Request):
    """관리자 전용 엔드포인트"""
    admin_user = get_current_active_superuser(request)
    return {"message": f"Hello admin {admin_user.email}"}

@router.get("/public-or-private")
async def flexible_endpoint(request: Request):
    """인증 선택적 엔드포인트"""
    user = get_current_user_optional(request)
    if user:
        return {"message": f"Hello {user.email}"}
    else:
        return {"message": "Hello anonymous user"}

@router.patch("/resources/{resource_id}")
async def update_resource(request: Request, resource_id: str, data: dict):
    """조건부 권한 체크 - 직접 호출 방식의 장점"""
    user = get_current_user(request)
    resource = await get_resource(resource_id)

    # 조건에 따라 다른 권한 체크
    if resource.owner_id != user.id:
        # 소유자가 아니면 관리자 권한 필요
        get_current_active_superuser(request)

    return await update_resource_logic(resource, data)
```

#### 🔷 Depends() 패턴 (특정 케이스)

**사용하는 경우:**
- 복잡한 중첩 의존성 그래프
- Public API에서 OpenAPI 문서화가 중요한 경우
- 라우터 레벨 공통 검증

**참고:** MongoDB/Beanie 환경에서는 세션 관리가 불필요하므로 Depends()의 주요 사용 이유가 제한적입니다.

```python
from fastapi import Depends, APIRouter

router = APIRouter()

# 복잡한 중첩 의존성 예제
def get_cache_client(config: Config = Depends(get_config)) -> CacheClient:
    """Redis 캐시 클라이언트"""
    return CacheClient(config.redis_url)

def get_notification_service(
    cache: CacheClient = Depends(get_cache_client),
) -> NotificationService:
    """알림 서비스 - 캐시 의존성 주입"""
    return NotificationService(cache)

@router.post("/notify")
async def send_notification(
    request: Request,
    data: NotificationData,
    service: NotificationService = Depends(get_notification_service),
):
    """Depends로 복잡한 의존성 그래프 처리"""
    user = get_current_active_user(request)  # 인증은 직접 호출
    return await service.send(user.id, data)

# 라우터 레벨 공통 검증
admin_router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(verify_admin_token)]  # 모든 엔드포인트에 적용
)
```

#### 🔷 External vs Internal 라우터 케이스

**External 라우터** (프론트엔드 공개):
- OpenAPI 문서화가 중요한 경우 `Depends()` 고려
- 하지만 mysingle-quant는 직접 호출 + 수동 문서화 권장

```python
# External API - 프론트엔드 대상
@router.get(
    "/api/v1/strategies",
    response_model=list[StrategyResponse],
    responses={
        401: {"description": "Unauthorized - 인증 필요"},
        403: {"description": "Forbidden - 권한 부족"},
    },
    summary="사용자 전략 목록 조회",
    description="인증된 사용자의 전략 목록을 반환합니다."
)
async def list_strategies(request: Request, limit: int = 100):
    """External API: 직접 호출 + 수동 문서화"""
    user = get_current_active_verified_user(request)
    strategies = await strategy_service.list_user_strategies(user.id, limit)
    return strategies
```

**Internal 라우터** (서비스 간 통신):
- 무조건 직접 호출 방식 ✅
- OpenAPI 문서화 우선순위 낮음
- Gateway에서 이미 인증 처리

```python
# Internal API - 서비스 간 호출
@internal_router.post("/internal/backtests/{backtest_id}/start")
async def start_backtest_internal(
    request: Request,
    backtest_id: str,
    config: BacktestConfig,
):
    """Internal API: Gateway에서 인증됨, 간결한 로직"""
    # Kong이 X-User-ID 헤더 주입, 필요시만 사용자 정보 조회
    user_id = request.headers.get("X-User-ID")

    # 비즈니스 로직에 집중
    result = await backtest_engine.start(backtest_id, config, user_id)
    return {"job_id": result.job_id, "status": "started"}
```

### 1.7 캐시 정책(Cache Policy)

- 미들웨어: JWT( IAM )·Kong 헤더(NON_IAM) 인증 시 사용자 캐시 우선 조회, MISS 시 DB 조회 후 저장
- 로그인: 성공 시 사용자 정보를 비동기으로 캐시에 갱신(set)
- 리프레시: refresh-token 갱신 시 사용자 캐시도 비동기로 최신화(set)
- 로그아웃: `UserManager.on_after_logout`에서 사용자 캐시 무효화(invalidate)
- 업데이트/삭제: `UserManager._update`, `on_after_update`, `on_after_delete`에서 캐시 무효화
- TTL/키 전략: 설정에서 관리(아래 참고)

#### 캐시 설정

`CommonSettings`에서 TTL과 키 프리픽스를 환경별로 조정할 수 있습니다.

```python
from mysingle.core.config import CommonSettings

class Settings(CommonSettings):
    USER_CACHE_TTL_SECONDS: int = 600       # 10분
    USER_CACHE_KEY_PREFIX: str = "user"     # 키 프리픽스
```

환경변수(.env) 예시:

```
USER_CACHE_TTL_SECONDS=600
USER_CACHE_KEY_PREFIX=user
```

---

### 2.4 인증 함수 종류

| 함수명                               | 설명                 | 예외 발생 조건            |
| ------------------------------------ | -------------------- | ------------------------- |
| `get_current_user()`                 | 기본 인증된 사용자   | 미인증                    |
| `get_current_active_user()`          | 활성 사용자          | 미인증 또는 비활성        |
| `get_current_active_verified_user()` | 활성 + 검증된 사용자 | 미인증, 비활성, 미검증    |
| `get_current_active_superuser()`     | 슈퍼유저             | 미인증, 비활성, 권한 부족 |
| `get_current_user_optional()`        | 선택적 인증          | 예외 없음 (None 반환)     |

### 2.5 패턴 선택 가이드

#### ✅ 직접 호출을 사용해야 하는 경우 (기본)

1. **조건부 권한 체크**
```python
@router.patch("/resources/{resource_id}")
async def update_resource(request: Request, resource_id: str, data: dict):
    user = get_current_user(request)
    resource = await get_resource(resource_id)

    # 소유자가 아니면 관리자만 가능
    if resource.owner_id != user.id:
        get_current_active_superuser(request)

    return await update_logic(resource, data)
```

2. **복잡한 비즈니스 로직**
```python
@router.post("/orders")
async def create_order(request: Request, data: OrderCreate):
    user = get_current_active_verified_user(request)

    # 사용자 등급별 할인
    discount = calculate_discount(user.tier)

    # 재고 확인
    if not await check_inventory(data.items):
        raise HTTPException(400, "Out of stock")

    # 결제 처리
    payment = await process_payment(user, data.payment_info)

    return await create_order_logic(user, data, discount, payment)
```

3. **Internal 라우터 (서비스 간 통신)**
```python
@internal_router.post("/internal/execute")
async def execute_internal(request: Request, config: dict):
    """Gateway에서 인증됨, 간결한 로직 유지"""
    user_id = request.headers.get("X-User-ID")
    return await execute_logic(user_id, config)
```

4. **세밀한 에러 처리**
```python
@router.post("/sensitive-data")
async def handle_sensitive(request: Request):
    try:
        user = get_current_active_verified_user(request)
    except UserNotExists:
        # 보안: 사용자 존재 여부 노출 방지
        await asyncio.sleep(random.uniform(0.1, 0.3))
        raise HTTPException(404, "Not found")
    except UserInactive:
        await log_suspicious_activity(request)
        raise HTTPException(403, "Account suspended")

    # 민감한 작업...
```

#### ✅ Depends()를 사용해야 하는 경우 (특수)

**중요:** MongoDB/Beanie ODM 환경에서는 SQLAlchemy처럼 세션 생명주기 관리가 필요 없으므로, Depends()의 실질적 사용 케이스가 매우 제한적입니다.

1. **복잡한 중첩 의존성 (서비스 팩토리)**
```python
def get_redis_client(config: Config = Depends(get_config)) -> Redis:
    return Redis(config.redis_url)

def get_cache_service(
    redis: Redis = Depends(get_redis_client),
) -> CacheService:
    return CacheService(redis)

@router.get("/cached-data")
async def get_cached_data(
    request: Request,
    cache: CacheService = Depends(get_cache_service),
):
    user = get_current_active_user(request)
    return await cache.get_user_data(user.id)
```

2. **라우터 레벨 공통 검증**
```python
# 모든 엔드포인트에 자동 적용
router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(verify_admin_token)]
)
```

3. **Public API OpenAPI 문서화 중시 (선택적)**
```python
@router.get(
    "/api/v1/products/{product_id}",
    response_model=ProductResponse,
)
async def get_product(
    request: Request,
    product_id: UUID,
    current_user: User = Depends(get_current_active_user),  # 문서에 반영
):
    """OpenAPI 문서화를 위한 Depends 사용 (선택적)"""
    # MongoDB/Beanie는 직접 쿼리
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(404)
    return product
```

**mysingle-quant 프로젝트 권장:**
- MongoDB/Beanie 환경에서는 **직접 호출 패턴을 우선**으로 사용
- Depends()는 라우터 레벨 공통 검증이나 복잡한 서비스 팩토리에만 제한적 사용

#### ❌ 데코레이터를 피해야 하는 경우

**FastAPI 라우터 함수에 직접 적용 금지** - OpenAPI 스키마 생성 방해, 타입 추론 손실, 디버깅 복잡도 증가

```python
# ❌ 나쁜 예: 라우터에 데코레이터 직접 적용
@router.get("/protected")
@authenticated  # OpenAPI 스키마 문제 발생
async def protected_endpoint(request: Request):
    user = request.state.user
    return user

# ✅ 좋은 예: 직접 호출
@router.get("/protected")
async def protected_endpoint(request: Request):
    user = get_current_active_user(request)
    return user
```

#### ✅ 데코레이터 적절한 사용 케이스

**비즈니스 로직 함수, 유틸리티 함수, 클래스 메서드**에만 사용

```python
from mysingle.auth.deps import authenticated

class StrategyService:
    @authenticated
    async def create_strategy(self, request: Request, data: dict):
        """서비스 레이어에서는 데코레이터 사용 가능"""
        user = request.state.user
        return await self._create_logic(user, data)

# 유틸리티 함수
@authenticated
async def process_user_data(request: Request, data: dict):
    """라우터가 아닌 헬퍼 함수에는 사용 가능"""
    user = request.state.user
    return transform_data(user, data)

# 라우터는 이를 호출
@router.post("/process")
async def process_endpoint(request: Request, data: dict):
    return await process_user_data(request, data)
```

### 2.6 유틸리티 함수들

```python
from mysingle.auth.deps import (
    get_user_id,
    get_user_email,
    is_user_authenticated,
    get_user_display_name,
    get_request_security_context,
)

@router.post("/sensitive-action")
async def sensitive_action(request: Request):
    """보안 컨텍스트를 포함한 액션"""
    user = get_current_active_verified_user(request)

    # 보안 컨텍스트 정보 수집
    security_context = get_request_security_context(request)

    # 감사 로그를 위한 정보
    logger.info(
        f"Sensitive action performed by {get_user_display_name(user)}",
        extra=security_context
    )

    return {"success": True}
```

---

## 3. Kong Gateway 헤더 표준화

### 3.1 개요

Kong Gateway와의 완벽한 통합을 위한 표준화된 헤더 처리 시스템입니다.

### 3.2 표준 Kong 헤더들

#### 인증 관련 헤더

| 헤더명                 | 설명                       | Kong 플러그인      |
| ---------------------- | -------------------------- | ------------------ |
| `X-Consumer-Custom-ID` | JWT sub 클레임 (사용자 ID) | JWT Plugin         |
| `X-Consumer-ID`        | Kong Consumer ID           | 모든 인증 플러그인 |
| `X-Consumer-Username`  | Kong Consumer Username     | 모든 인증 플러그인 |

#### 운영 관련 헤더

| 헤더명                    | 설명              | 용도                |
| ------------------------- | ----------------- | ------------------- |
| `X-Forwarded-Service`     | 서비스 식별자     | Request Transformer |
| `X-Correlation-Id`        | 분산 추적 ID      | Request Transformer |
| `X-Kong-Request-Id`       | Kong 요청 ID      | Kong 자동 생성      |
| `X-Kong-Upstream-Latency` | 업스트림 지연시간 | 성능 모니터링       |
| `X-Kong-Proxy-Latency`    | 프록시 지연시간   | 성능 모니터링       |

### 3.3 헤더 추출 함수들

```python
from fastapi import Request
from mysingle.auth.deps import (
    get_kong_user_id,
    get_kong_consumer_id,
    get_kong_consumer_username,
    get_kong_forwarded_service,
    get_kong_correlation_id,
    get_kong_request_id,
    get_kong_upstream_latency,
    get_kong_proxy_latency,
    is_kong_authenticated,
    get_kong_headers_dict,
    get_extended_kong_headers_dict,
)

@router.get("/debug/headers")
async def debug_kong_headers(request: Request):
    """Kong 헤더 디버깅 엔드포인트"""

    # 기본 인증 헤더
    basic_headers = get_kong_headers_dict(request)

    # 확장된 모든 헤더
    extended_headers = get_extended_kong_headers_dict(request)

    return {
        "basic": basic_headers,
        "extended": extended_headers,
        "performance": {
            "upstream_latency": get_kong_upstream_latency(request),
            "proxy_latency": get_kong_proxy_latency(request),
        }
    }

@router.get("/trace-info")
async def get_trace_info(request: Request):
    """분산 추적 정보 조회"""
    return {
        "correlation_id": get_kong_correlation_id(request),
        "request_id": get_kong_request_id(request),
        "service": get_kong_forwarded_service(request),
        "user_id": get_kong_user_id(request),
    }
```

### 3.4 Kong Gateway 설정 예시

#### JWT Plugin 설정

```yaml
plugins:
- name: jwt
  config:
    header_names: ["Authorization"]
    claims_to_verify: ["exp", "sub"]
    # sub 클레임을 X-Consumer-Custom-ID로 전달
    run_on_preflight: false
```

#### Request Transformer 설정

```yaml
plugins:
- name: request-transformer
  config:
    add:
      headers:
        - "X-Forwarded-Service:kong-gateway"
        - "X-Correlation-Id:$(uuid)"
    append:
      headers:
        - "X-Request-Timestamp:$(current_timestamp)"
```

---



### 4.6 미들웨어 통합

```python
from mysingle.core import (
    create_fastapi_app,
    create_service_config,
    ServiceType,
    LoggingMiddleware,
    add_logging_middleware,
)

def create_app():
    service_config = create_service_config(
        service_name="my-service",
        service_type=ServiceType.NON_IAM_SERVICE,
        enable_auth=True,
    )

    app = create_fastapi_app(service_config)

    # 로깅 미들웨어 추가
    add_logging_middleware(
        app,
        service_name="my-service",
        enable_timing_logs=True  # 느린 요청 감지
    )

    return app
```

---
## 5. HTTP Client

### 5.1 주요 특징

- **연결 풀링**: httpx 기반 비동기 연결 풀 관리
- **자동 URL 구성**: 서비스명으로부터 Gateway/Direct URL 자동 생성
- **싱글톤 패턴**: 서비스별 클라이언트 재사용으로 리소스 효율성
- **생명주기 관리**: App Factory와 통합된 자동 정리
- **환경 설정**: 환경 변수로 타임아웃, 연결 수 등 제어 가능

### 5.2 기본사용법
#### 1) 서비스 클라이언트 생성 (일회성)

```python
from mysingle.core import create_service_http_client

# 기본 생성 (URL 자동 구성)
client = create_service_http_client("strategy-service")

# 커스텀 설정
client = create_service_http_client(
    service_name="strategy-service",
    base_url="http://custom-host:8003",
    timeout=60.0,
    max_connections=50,
    headers={"X-Custom-Header": "value"}
)

# 사용
async with client:
    response = await client.get("/strategies")
    data = response.json()
```

#### 2) 싱글톤 클라이언트 사용 (권장)

```python
from mysingle.core import get_service_http_client

# 서비스별 클라이언트 재사용
strategy_client = get_service_http_client("strategy-service")
backtest_client = get_service_http_client("backtest-service")

# HTTP 메서드 사용
strategies = await strategy_client.get("/strategies")
result = await backtest_client.post("/backtests", json={"strategy_id": "123"})
```

#### 3) 편의 함수 사용

```python
from mysingle.core import make_service_request

# 한 줄로 요청
response = await make_service_request(
    service_name="strategy-service",
    method="GET",
    endpoint="/strategies",
    headers={"Authorization": "Bearer token"}
)
```

### 5.3 서비스별 클라이언트 예시

#### 1) Strategy Service 연동

```python
from mysingle.core import get_service_http_client

class StrategyServiceClient:
    def __init__(self):
        self.client = get_service_http_client("strategy-service")

    async def get_strategies(self, user_id: str) -> list[dict]:
        """사용자 전략 목록 조회"""
        response = await self.client.get(
            "/strategies",
            headers={"X-User-Id": user_id}
        )
        response.raise_for_status()
        return response.json()

    async def create_strategy(self, strategy_data: dict, user_id: str) -> dict:
        """전략 생성"""
        response = await self.client.post(
            "/strategies",
            json=strategy_data,
            headers={"X-User-Id": user_id}
        )
        response.raise_for_status()
        return response.json()

    async def update_strategy(self, strategy_id: str, data: dict, user_id: str) -> dict:
        """전략 수정"""
        response = await self.client.put(
            f"/strategies/{strategy_id}",
            json=data,
            headers={"X-User-Id": user_id}
        )
        response.raise_for_status()
        return response.json()
```

#### 2) Backtest Service 연동

```python
from mysingle.core import get_service_http_client

class BacktestServiceClient:
    def __init__(self):
        self.client = get_service_http_client("backtest-service")

    async def start_backtest(self, config: dict, user_id: str) -> dict:
        """백테스트 시작"""
        response = await self.client.post(
            "/backtests/start",
            json=config,
            headers={"X-User-Id": user_id}
        )
        response.raise_for_status()
        return response.json()

    async def get_backtest_status(self, backtest_id: str, user_id: str) -> dict:
        """백테스트 상태 조회"""
        response = await self.client.get(
            f"/backtests/{backtest_id}/status",
            headers={"X-User-Id": user_id}
        )
        response.raise_for_status()
        return response.json()
```

### 4.4 환경 설정

#### 1) .env 파일 설정

```bash
# HTTP 클라이언트 설정
HTTP_CLIENT_TIMEOUT=30.0
HTTP_CLIENT_MAX_CONNECTIONS=100
HTTP_CLIENT_MAX_KEEPALIVE=20
HTTP_CLIENT_MAX_RETRIES=3
HTTP_CLIENT_RETRY_DELAY=1.0

# API Gateway 설정
USE_API_GATEWAY=true
API_GATEWAY_URL=http://localhost:8000
```

#### 2) 서비스별 설정 확장

```python
# app/core/config.py
from mysingle.core.config import CommonSettings

class MyServiceSettings(CommonSettings):
    SERVICE_NAME: str = "my-service"

    # 서비스별 HTTP 클라이언트 설정
    STRATEGY_SERVICE_URL: str = "http://kong-gateway:8000/strategy"
    BACKTEST_SERVICE_URL: str = "http://kong-gateway:8000/backtest"

    # 커스텀 타임아웃
    STRATEGY_CLIENT_TIMEOUT: float = 60.0
    BACKTEST_CLIENT_TIMEOUT: float = 300.0  # 백테스트는 오래 걸림

settings = MyServiceSettings()
```

### 4.5 FastAPI 서비스에서 사용

#### 1) 의존성 주입 패턴

```python
from fastapi import FastAPI, Depends
from mysingle.core import get_service_http_client, ServiceHttpClient

# 의존성 함수
def get_strategy_client() -> ServiceHttpClient:
    return get_service_http_client("strategy-service")

def get_backtest_client() -> ServiceHttpClient:
    return get_service_http_client("backtest-service")

# 라우터에서 사용
@app.post("/journeys")
async def create_journey(
    journey_data: dict,
    strategy_client: ServiceHttpClient = Depends(get_strategy_client),
    backtest_client: ServiceHttpClient = Depends(get_backtest_client)
):
    # 전략 검증
    strategy = await strategy_client.get(f"/strategies/{journey_data['strategy_id']}")

    # 백테스트 시작
    backtest = await backtest_client.post("/backtests/start", json=journey_data)

    return {"journey_id": "123", "backtest_id": backtest.json()["id"]}
```

#### 2) 서비스 클래스 패턴

```python
from mysingle.core import get_service_http_client

class JourneyOrchestrator:
    def __init__(self):
        self.strategy_client = get_service_http_client("strategy-service")
        self.backtest_client = get_service_http_client("backtest-service")
        self.notification_client = get_service_http_client("notification-service")

    async def execute_journey(self, journey_config: dict, user_id: str) -> dict:
        """여정 실행"""
        headers = {"X-User-Id": user_id}

        try:
            # 1. 전략 검증
            strategy_response = await self.strategy_client.get(
                f"/strategies/{journey_config['strategy_id']}",
                headers=headers
            )
            strategy = strategy_response.json()

            # 2. 백테스트 시작
            backtest_response = await self.backtest_client.post(
                "/backtests/start",
                json={
                    "strategy_id": strategy["id"],
                    "config": journey_config["backtest_config"]
                },
                headers=headers
            )
            backtest = backtest_response.json()

            # 3. 알림 발송
            await self.notification_client.post(
                "/notifications/send",
                json={
                    "user_id": user_id,
                    "type": "journey_started",
                    "data": {"journey_id": journey_config["id"]}
                },
                headers=headers
            )

            return {
                "status": "started",
                "strategy": strategy,
                "backtest": backtest
            }

        except Exception as e:
            # 에러 알림
            await self.notification_client.post(
                "/notifications/send",
                json={
                    "user_id": user_id,
                    "type": "journey_error",
                    "data": {"error": str(e)}
                },
                headers=headers
            )
            raise
```

### 4.6 에러 처리 및 재시도

#### 1) httpx 예외 처리

```python
import httpx
from mysingle.core import get_service_http_client

async def robust_service_call():
    client = get_service_http_client("strategy-service")

    try:
        response = await client.get("/strategies", timeout=30.0)
        response.raise_for_status()  # HTTP 에러 발생 시 예외
        return response.json()

    except httpx.TimeoutException:
        # 타임아웃 처리
        logger.error("Strategy service timeout")
        raise

    except httpx.HTTPStatusError as e:
        # HTTP 에러 처리
        if e.response.status_code == 404:
            logger.warning("Strategy not found")
            return None
        elif e.response.status_code >= 500:
            logger.error(f"Strategy service error: {e}")
            raise
        else:
            logger.warning(f"Client error: {e}")
            raise

    except httpx.RequestError as e:
        # 연결 에러 처리
        logger.error(f"Connection error to strategy service: {e}")
        raise
```

#### 2) 재시도 패턴

```python
import asyncio
from typing import TypeVar, Callable
from mysingle.core import get_service_http_client, HttpClientConfig

T = TypeVar('T')

async def retry_service_call(
    func: Callable[[], T],
    max_retries: int = HttpClientConfig.DEFAULT_MAX_RETRIES,
    delay: float = HttpClientConfig.DEFAULT_RETRY_DELAY
) -> T:
    """서비스 호출 재시도"""
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            last_exception = e
            if attempt < max_retries:
                await asyncio.sleep(delay * (2 ** attempt))  # 지수 백오프
                continue
            break
        except httpx.HTTPStatusError as e:
            # 5xx 에러만 재시도
            if e.response.status_code >= 500 and attempt < max_retries:
                last_exception = e
                await asyncio.sleep(delay * (2 ** attempt))
                continue
            raise

    raise last_exception

# 사용 예시
async def get_strategy_with_retry(strategy_id: str):
    client = get_service_http_client("strategy-service")

    async def call():
        response = await client.get(f"/strategies/{strategy_id}")
        response.raise_for_status()
        return response.json()

    return await retry_service_call(call)
```

### 4.7 성능 모니터링

#### 1) 요청 로깅

```python
import time
from mysingle.core import get_service_http_client, get_logger

logger = get_logger(__name__)

async def logged_service_call(service_name: str, method: str, endpoint: str, **kwargs):
    """로깅이 포함된 서비스 호출"""
    client = get_service_http_client(service_name)

    start_time = time.time()
    try:
        response = await client.request(method, endpoint, **kwargs)
        duration = time.time() - start_time

        logger.info(
            f"Service call: {service_name} {method} {endpoint} "
            f"-> {response.status_code} ({duration:.3f}s)"
        )

        return response

    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Service call failed: {service_name} {method} {endpoint} "
            f"-> {type(e).__name__}: {e} ({duration:.3f}s)"
        )
        raise
```

### 4.8 테스트 지원

#### 1) 모킹

```python
import pytest
from unittest.mock import AsyncMock, patch
from mysingle.core import ServiceHttpClientManager

@pytest.fixture
async def mock_strategy_service():
    """Strategy Service 모킹"""
    mock_client = AsyncMock()
    mock_client.get.return_value.json.return_value = {
        "id": "strategy-123",
        "name": "Test Strategy"
    }

    with patch.object(ServiceHttpClientManager, 'get_client', return_value=mock_client):
        yield mock_client

async def test_journey_creation(mock_strategy_service):
    """여정 생성 테스트"""
    orchestrator = JourneyOrchestrator()

    result = await orchestrator.execute_journey({
        "strategy_id": "strategy-123",
        "backtest_config": {}
    }, "user-456")

    assert result["status"] == "started"
    mock_strategy_service.get.assert_called_once()
```

이제 표준화된 HTTP 클라이언트가 완성되었습니다! 🎉

---

## 6. 모니터링 메트릭

### 6.1 개요

고성능 메트릭 수집 및 모니터링 시스템으로 Prometheus 형식 지원과 성능 최적화가 특징입니다.

### 5.2 주요 특징

- **비동기 메트릭 수집**: 요청 처리 지연 최소화
- **메모리 효율적**: 순환 버퍼로 메모리 사용량 제한
- **자동 경로 정규화**: UUID, 숫자 ID를 `{uuid}`, `{id}`로 정규화
- **풍부한 메트릭**: 기본 메트릭, 백분위수, 히스토그램
- **Prometheus 지원**: 완전한 Prometheus 형식 내보내기

### 5.3 기본 설정

```python
from mysingle.core import create_fastapi_app, create_service_config
from mysingle.metrics import MetricsConfig

# 메트릭이 활성화된 서비스 설정
service_config = create_service_config(
    service_name="my-service",
    service_version="1.0.0",
    enable_metrics=True,  # 메트릭 활성화
)

app = create_fastapi_app(service_config)

# 커스텀 메트릭 설정 (선택적)
from mysingle.metrics import create_metrics_middleware, MetricsConfig

metrics_config = MetricsConfig(
    max_duration_samples=2000,      # 응답 시간 샘플 수
    enable_percentiles=True,        # 백분위수 계산 활성화
    enable_histogram=True,          # 히스토그램 활성화
    retention_period_seconds=3600,  # 1시간 보존
)

create_metrics_middleware("my-service", config=metrics_config)
```

### 5.4 메트릭 엔드포인트

```python
from mysingle.metrics import create_metrics_router

# 메트릭 라우터 추가
metrics_router = create_metrics_router()
app.include_router(metrics_router)

# 사용 가능한 엔드포인트:
# GET /metrics/           - JSON 또는 Prometheus 형식
# GET /metrics/json       - JSON 상세 메트릭
# GET /metrics/prometheus - Prometheus 형식
# GET /metrics/health     - 메트릭 시스템 상태
# GET /metrics/routes     - 라우트별 통계
```

### 5.5 수집되는 메트릭

#### 기본 메트릭

- **총 요청 수**: `{service}_requests_total`
- **에러 수**: `{service}_errors_total`
- **초당 요청**: `{service}_requests_per_second`
- **서비스 가동시간**: `{service}_uptime_seconds`

#### 응답 시간 메트릭

- **백분위수**: P50, P90, P95, P99
- **평균 응답시간**: `{service}_route_duration_seconds`
- **히스토그램**: 응답시간 분포

#### 라우트별 메트릭

- **라우트별 요청 수**: `{service}_route_requests_total`
- **라우트별 에러 수**: `{service}_route_errors_total`
- **라우트별 응답시간**: 백분위수 포함

### 5.6 메트릭 조회 예시

```python
from mysingle.metrics import get_metrics_collector

@router.get("/custom-metrics")
async def get_custom_metrics():
    """커스텀 메트릭 조회"""
    collector = get_metrics_collector()

    # JSON 형식 메트릭
    json_metrics = collector.get_metrics()

    # Prometheus 형식 메트릭
    prometheus_metrics = collector.get_prometheus_metrics()

    return {
        "summary": {
            "total_requests": json_metrics["total_requests"],
            "error_rate": json_metrics["error_rate"],
            "uptime_seconds": json_metrics["uptime_seconds"],
        },
        "routes": len(json_metrics["routes"]),
    }
```

### 5.7 성능 최적화 설정

```python
# 제외 경로 설정 (성능 최적화)
exclude_paths = {
    "/health",      # 헬스체크
    "/metrics",     # 메트릭 자체
    "/docs",        # API 문서
    "/favicon.ico", # 파비콘
}

create_metrics_middleware(
    "my-service",
    exclude_paths=exclude_paths
)
```

---

## 7. 감사 로깅 (Audit Logging)

### 7.1 개요

HTTP 요청/응답에 대한 감사 로그를 자동으로 수집하고 저장하는 시스템입니다.

### 6.2 주요 특징

- **자동 로깅**: 모든 HTTP 요청/응답 자동 기록
- **최소한의 성능 영향**: 비동기 처리로 응답 지연 최소화
- **포괄적 정보**: 사용자, 요청, 응답, 타이밍 정보 포함
- **MongoDB 저장**: Beanie를 통한 효율적인 문서 저장
- **환경별 제어**: 테스트 환경에서 자동 비활성화

### 6.3 감사 로그 데이터 모델

```python
from mysingle.audit.models import AuditLog

# AuditLog 필드들:
class AuditLog(BaseTimeDoc):
    # 컨텍스트 정보
    user_id: PydanticObjectId | None    # 사용자 ID
    service: str                        # 서비스명
    request_id: str | None              # 요청 ID
    trace_id: str | None                # 추적 ID

    # 요청 정보
    method: str                         # HTTP 메서드
    path: str                           # 요청 경로
    ip: str | None                      # 클라이언트 IP
    user_agent: str | None              # User-Agent
    req_bytes: int                      # 요청 크기

    # 응답 정보
    status_code: int                    # HTTP 상태 코드
    resp_bytes: int                     # 응답 크기

    # 성능 정보
    latency_ms: int                     # 응답 시간 (밀리초)
    occurred_at: datetime               # 발생 시간
```

### 6.4 기본 설정

```python
from mysingle.core import create_fastapi_app, create_service_config
from mysingle.audit import AuditLoggingMiddleware

def create_app():
    service_config = create_service_config(
        service_name="my-service",
        service_type=ServiceType.NON_IAM_SERVICE,
        enable_audit_logging=True,  # 감사 로깅 활성화
    )

    app = create_fastapi_app(service_config)

    # 수동으로 감사 미들웨어 추가 (필요시)
    app.add_middleware(
        AuditLoggingMiddleware,
        service_name="my-service",
        enabled=True
    )

    return app
```

### 6.5 감사 로그 조회

```python
from mysingle.audit.models import AuditLog
from datetime import datetime, timedelta

@router.get("/admin/audit-logs")
async def get_audit_logs(
    user_id: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    limit: int = 100
):
    """감사 로그 조회 (관리자 전용)"""

    # 기본 쿼리
    query = {}

    # 사용자 필터
    if user_id:
        query["user_id"] = ObjectId(user_id)

    # 날짜 범위 필터
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        query["occurred_at"] = date_filter

    # 감사 로그 조회
    logs = await AuditLog.find(query).limit(limit).to_list()

    return {
        "total": len(logs),
        "logs": [
            {
                "id": str(log.id),
                "user_id": str(log.user_id) if log.user_id else None,
                "method": log.method,
                "path": log.path,
                "status_code": log.status_code,
                "latency_ms": log.latency_ms,
                "occurred_at": log.occurred_at.isoformat(),
                "ip": log.ip,
            }
            for log in logs
        ]
    }

@router.get("/admin/audit-stats")
async def get_audit_statistics():
    """감사 로그 통계"""

    # 최근 24시간 통계
    since = datetime.utcnow() - timedelta(hours=24)

    total_requests = await AuditLog.find(
        {"occurred_at": {"$gte": since}}
    ).count()

    error_requests = await AuditLog.find({
        "occurred_at": {"$gte": since},
        "status_code": {"$gte": 400}
    }).count()

    unique_users = await AuditLog.find(
        {"occurred_at": {"$gte": since}}
    ).distinct("user_id")

    return {
        "period": "last_24_hours",
        "total_requests": total_requests,
        "error_requests": error_requests,
        "error_rate": error_requests / max(total_requests, 1),
        "unique_users": len([u for u in unique_users if u is not None]),
    }
```

### 6.6 보안 및 컴플라이언스

```python
# 민감한 경로 제외 설정
SENSITIVE_PATHS = [
    "/auth/login",      # 로그인 정보
    "/auth/register",   # 회원가입 정보
    "/admin/secrets",   # 관리자 민감 정보
]

class CustomAuditMiddleware(AuditLoggingMiddleware):
    """커스텀 감사 미들웨어"""

    def should_log_request(self, request: Request) -> bool:
        """감사 로그 기록 여부 결정"""
        path = request.url.path

        # 민감한 경로 제외
        if path in SENSITIVE_PATHS:
            return False

        # 헬스체크 제외
        if path.startswith(("/health", "/metrics")):
            return False

        return True

    async def get_user_id(self, request: Request) -> str | None:
        """요청에서 사용자 ID 추출"""
        # Kong 헤더에서 사용자 ID 추출
        user_id = request.headers.get("x-consumer-custom-id")

        # 또는 JWT에서 추출
        if not user_id:
            # JWT 파싱 로직
            pass

        return user_id
```

---

## 8. 종합 활용 예시

### 8.1 완전한 서비스 설정

```python
from fastapi import FastAPI, Request, APIRouter
from mysingle.core import (
    create_fastapi_app,
    create_service_config,
    ServiceType,
)
from mysingle.auth.deps import get_current_active_user
from mysingle.core import setup_logging, get_structured_logger, log_user_action
from mysingle.metrics import create_metrics_router

# 로깅 설정
setup_logging(
    service_name="strategy-service",
    environment="development",
)

logger = get_structured_logger(__name__)

def create_app() -> FastAPI:
    """완전한 서비스 앱 생성"""

    # 서비스 설정
    service_config = create_service_config(
        service_name="strategy-service",
        service_type=ServiceType.NON_IAM_SERVICE,
        service_version="1.0.0",
        enable_auth=True,           # 인증 활성화
        enable_metrics=True,        # 메트릭 활성화
        enable_audit_logging=True,  # 감사 로그 활성화
    )

    # 앱 생성
    app = create_fastapi_app(service_config)

    # 메트릭 라우터 추가
    app.include_router(create_metrics_router())

    # 비즈니스 라우터 추가
    app.include_router(create_strategy_router(), prefix="/strategies")

    return app

def create_strategy_router() -> APIRouter:
    """전략 관리 라우터"""
    router = APIRouter()

    @router.post("/")
    async def create_strategy(request: Request, strategy_data: dict):
        """전략 생성 - 모든 기능 통합 예시"""

        # 1. 인증
        user = get_current_active_user(request)
        logger.info(f"Strategy creation request from user {user.id}")

        # 2. 입력 검증
        if not strategy_data.get("name"):
            logger.warning("Strategy creation failed: missing name")
            raise HTTPException(400, "Strategy name is required")

        try:
            # 3. 비즈니스 로직
            strategy = await create_strategy_logic(user.id, strategy_data)

            # 4. 사용자 액션 로깅
            log_user_action(
                action="create_strategy",
                resource_type="strategy",
                resource_id=str(strategy.id),
                details={"name": strategy_data["name"]},
                success=True
            )

            logger.info(
                "Strategy created successfully",
                extra={
                    "strategy_id": str(strategy.id),
                    "user_id": str(user.id),
                    "strategy_name": strategy_data["name"],
                }
            )

            return {
                "strategy_id": str(strategy.id),
                "name": strategy.name,
                "created_at": strategy.created_at.isoformat(),
            }

        except Exception as e:
            # 5. 에러 로깅
            log_user_action(
                action="create_strategy",
                resource_type="strategy",
                details=strategy_data,
                success=False,
                error=str(e)
            )

            logger.error(
                "Strategy creation failed",
                extra={
                    "user_id": str(user.id),
                    "error": str(e),
                    "strategy_data": strategy_data,
                }
            )

            raise HTTPException(500, "Strategy creation failed")

    return router

if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 8.2 모니터링 대시보드 구성

```python
@router.get("/admin/system-status")
async def get_system_status(request: Request):
    """시스템 전체 상태 조회"""

    # 관리자 권한 확인
    admin_user = get_current_active_superuser(request)

    # 메트릭 수집
    from mysingle.metrics import get_metrics_collector
    collector = get_metrics_collector()
    metrics = collector.get_metrics()

    # 감사 로그 통계
    from mysingle.audit.models import AuditLog
    recent_requests = await AuditLog.find(
        {"occurred_at": {"$gte": datetime.utcnow() - timedelta(hours=1)}}
    ).count()

    # Kong 헤더 정보
    from mysingle.auth.deps import get_extended_kong_headers_dict
    kong_info = get_extended_kong_headers_dict(request)

    return {
        "service": metrics["service"],
        "uptime_seconds": metrics["uptime_seconds"],
        "performance": {
            "total_requests": metrics["total_requests"],
            "error_rate": metrics["error_rate"],
            "requests_per_second": metrics["requests_per_second"],
            "recent_requests_1h": recent_requests,
        },
        "gateway": {
            "proxy_latency": kong_info.get("proxy_latency"),
            "upstream_latency": kong_info.get("upstream_latency"),
            "correlation_id": kong_info.get("correlation_id"),
        },
        "admin_user": {
            "id": str(admin_user.id),
            "email": admin_user.email,
        }
    }
```

---

## 9. 베스트 프랙티스

### 9.1 성능 최적화

1. **메트릭 제외 경로 설정**: 헬스체크, 정적 파일 제외
2. **로그 레벨 조정**: Production에서는 INFO 이상만
3. **감사 로그 선택적 기록**: 민감한 정보 제외
4. **Kong 헤더 캐싱**: 자주 사용하는 헤더값 캐시

### 9.2 보안 고려사항

1. **민감한 정보 로그 제외**: 비밀번호, 토큰 등
2. **감사 로그 접근 제한**: 관리자만 접근 가능
3. **헤더 검증**: Kong 헤더 위조 방지
4. **로그 보존 정책**: 개인정보 보호 규정 준수

### 9.3 운영 가이드라인

1. **로그 모니터링**: 에러 로그 실시간 모니터링
2. **메트릭 알림**: 성능 임계값 기반 알림
3. **감사 로그 분석**: 정기적인 보안 감사
4. **백업 정책**: 로그 및 메트릭 데이터 백업

---

## 10. 트러블슈팅

### 10.1 인증 문제

**문제**: `UserNotExists` 예외 발생
**해결**: Kong 헤더 확인, AuthMiddleware 설정 검토

**문제**: `UserInactive` 예외 발생
**해결**: 사용자 활성화 상태 확인

### 10.2 로깅 문제

**문제**: 로그가 기록되지 않음
**해결**: 로깅 설정, 로그 레벨 확인

**문제**: Correlation ID가 전파되지 않음
**해결**: 미들웨어 순서, 헤더 설정 확인

### 10.3 메트릭 문제

**문제**: 메트릭이 수집되지 않음
**해결**: MetricsMiddleware 활성화 확인

**문제**: 메모리 사용량 증가
**해결**: retention_period_seconds 설정 조정

---

이 가이드를 통해 MySingle-Quant Package의 모든 주요 기능을 효과적으로 활용할 수 있습니다. 추가 질문이나 상세한 설명이 필요한 부분이 있다면 언제든지 문의해 주세요.

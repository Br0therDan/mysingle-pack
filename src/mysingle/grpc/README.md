# gRPC Server Usage Guide

**Version:** 2.2.1 | **Updated:** 2025-12-05

MySingle Quant 플랫폼의 표준 gRPC 서버 구현 가이드입니다.

---

## 📋 목차

1. [빠른 시작](#1-빠른-시작)
2. [BaseGrpcServer 사용법](#2-basegrpcserver-사용법)
3. [GrpcCache 사용법](#3-grpccache-사용법)
4. [설정 관리](#4-설정-관리)
5. [Interceptor](#5-interceptor)
6. [모범 사례](#6-모범-사례)

---

## 1. 빠른 시작

### 1.1 설치

```bash
pip install mysingle[grpc]
# 또는 전체 설치
pip install mysingle[common-grpc]
```

### 1.2 최소 구현 (3단계)

**Step 1: 서비스 설정 클래스 작성**

```python
# app/core/config.py
from mysingle.core.config import CommonSettings

class MyServiceSettings(CommonSettings):
    """서비스별 설정 (CommonSettings 상속)"""
    SERVICE_NAME: str = "my-service"

    # gRPC 포트 오버라이드 (선택사항)
    GRPC_SERVER_PORT: int = 50052

settings = MyServiceSettings()
```

**Step 2: gRPC 서버 클래스 작성**

```python
# app/grpc_server.py
from mysingle.grpc.server import BaseGrpcServer

class MyGrpcServer(BaseGrpcServer):
    """gRPC 서버 구현"""

    def register_servicers(self, server):
        """Servicer 등록 (필수 구현)"""
        from app.servicers import MyServiceServicer
        from mysingle.protos.services.my_service.v1 import my_service_pb2_grpc

        my_service_pb2_grpc.add_MyServiceServicer_to_server(
            MyServiceServicer(), server
        )
```

**Step 3: 서버 시작**

```python
# main.py
from app.core.config import settings
from app.grpc_server import MyGrpcServer
from mysingle.grpc.server import GrpcServerConfig

# CommonSettings에서 설정 자동 로드
config = GrpcServerConfig.from_settings(
    settings,
    service_name="my-service",
)

grpc_server = MyGrpcServer(config)
await grpc_server.start()
```

**완료!** 🎉 다음 기능이 자동으로 적용됩니다:
- ✅ 인증 (X-User-Id 검증)
- ✅ Rate Limiting (Redis 기반)
- ✅ Prometheus 메트릭 수집
- ✅ 구조화된 로깅
- ✅ 에러 자동 변환 (Python 예외 → gRPC StatusCode)
- ✅ Correlation ID 추적

---

## 2. BaseGrpcServer 사용법

### 2.1 기본 구조

```python
from mysingle.grpc.server import BaseGrpcServer, GrpcServerConfig

class MyGrpcServer(BaseGrpcServer):
    """
    BaseGrpcServer를 상속받아 구현합니다.

    필수 구현:
    - register_servicers(): Servicer 등록

    선택 구현 (Lifecycle Hooks):
    - before_start(): 서버 시작 전 초기화
    - after_start(): 서버 시작 후 작업
    - before_stop(): 서버 중지 전 정리
    - after_stop(): 서버 중지 후 정리
    """

    def register_servicers(self, server):
        """Servicer 등록 (필수)"""
        from app.servicers import MyServiceServicer
        from mysingle.protos.services.my_service.v1 import my_service_pb2_grpc

        my_service_pb2_grpc.add_MyServiceServicer_to_server(
            MyServiceServicer(), server
        )
```

### 2.2 Lifecycle Hooks 활용

**복잡한 리소스 관리가 필요한 경우:**

```python
class GenAIGrpcServer(BaseGrpcServer):
    """GenAI Service gRPC 서버"""

    async def before_start(self):
        """서버 시작 전: 외부 리소스 초기화"""
        await super().before_start()

        # Service Factory 초기화
        from app.services.service_factory import get_service_factory
        self.genai_factory = get_service_factory()
        await self.genai_factory.initialize()

        logger.info("GenAI Service Factory initialized")

    async def after_stop(self):
        """서버 중지 후: 리소스 정리"""
        if hasattr(self, 'genai_factory'):
            await self.genai_factory.shutdown()

        await super().after_stop()
        logger.info("GenAI resources cleaned up")

    def register_servicers(self, server):
        """Servicer 등록 (Service Factory 주입)"""
        from app.servicers import ChatOpsServicer, StrategyBuilderServicer
        from mysingle.protos.services.genai.v1 import (
            chatops_pb2_grpc,
            strategy_builder_pb2_grpc,
        )

        # Service Factory를 Servicer에 주입
        chatops_pb2_grpc.add_ChatOpsServiceServicer_to_server(
            ChatOpsServicer(self.genai_factory), server
        )
        strategy_builder_pb2_grpc.add_StrategyBuilderServiceServicer_to_server(
            StrategyBuilderServicer(self.genai_factory), server
        )
```

### 2.3 설정 커스터마이징

**개발 환경에서 Reflection 활성화:**

```python
from app.core.config import settings

config = GrpcServerConfig.from_settings(
    settings,
    service_name="my-service",
    # 환경별 오버라이드
    enable_reflection=settings.ENVIRONMENT in ["development", "local"],
    reflection_service_names=[
        "my_service.v1.MyService",
        "grpc.reflection.v1alpha.ServerReflection",
    ],
)
```

**특정 메서드 인증 면제:**

```python
config = GrpcServerConfig.from_settings(
    settings,
    service_name="my-service",
    # Health check는 인증 면제
    auth_exempt_methods=[
        "/grpc.health.v1.Health/Check",
    ],
)
```

---

## 3. GrpcCache 사용법

### 3.1 2-Tier 캐시 구조

```
┌────────────────┐
│ L1: In-Memory  │  ← 5분 TTL, LRU 100개 (초고속)
└───────┬────────┘
        │ Miss
        ▼
┌────────────────┐
│ L2: Redis      │  ← 1시간 TTL (지속성)
└───────┬────────┘
        │ Miss
        ▼
┌────────────────┐
│ MongoDB/API    │  ← 원본 데이터
└────────────────┘
```

### 3.2 데코레이터 방식 (권장)

```python
# app/servicers/strategy_servicer.py
from mysingle.grpc.cache import GrpcCache, grpc_cached

class StrategyServiceServicer(strategy_service_pb2_grpc.StrategyServiceServicer):
    def __init__(self):
        # CommonSettings에서 캐시 설정 자동 로드
        from app.core.config import settings
        self._grpc_cache = GrpcCache.from_settings(
            settings,
            service_name="strategy-service"
        )

    @grpc_cached(ttl=300)  # 5분 캐싱
    async def GetStrategyVersion(self, request, context):
        """
        캐시 적용 메서드:
        - 첫 호출: MongoDB 조회 → 캐시 저장
        - 이후 호출: 캐시에서 즉시 반환 (L1 → L2 → MongoDB)
        """
        version = await StrategyVersion.find_one(
            StrategyVersion.strategy_id == request.strategy_id,
            StrategyVersion.seq == request.seq,
            StrategyVersion.user_id == request.user_id,
        )
        if not version:
            raise FileNotFoundError(f"Version not found: {request.strategy_id}/v{request.seq}")

        return convert_to_protobuf(version)
```

### 3.3 수동 캐시 제어

```python
class IndicatorServiceServicer(indicator_service_pb2_grpc.IndicatorServiceServicer):
    def __init__(self):
        from app.core.config import settings
        self._grpc_cache = GrpcCache.from_settings(
            settings,
            service_name="indicator-service"
        )

    async def GetIndicatorMetadata(self, request, context):
        """수동 캐시 조회/저장"""
        # 캐시 키 생성
        cache_key = self._grpc_cache.make_cache_key(
            method="GetIndicatorMetadata",
            request=request,
        )

        # 캐시 조회
        cached = await self._grpc_cache.get_with_l1(cache_key)
        if cached:
            return cached

        # 원본 데이터 조회
        metadata = await IndicatorMetadata.find_one(...)
        result = convert_to_protobuf(metadata)

        # 캐시 저장 (1시간 TTL)
        await self._grpc_cache.set_with_l1(cache_key, result, ttl=3600)

        return result
```

### 3.4 캐시 무효화

```python
async def UpdateStrategyVersion(self, request, context):
    """전략 버전 업데이트 시 캐시 무효화"""
    # DB 업데이트
    await StrategyVersion.update(...)

    # 관련 캐시 무효화
    await self._grpc_cache.invalidate_pattern(
        f"GetStrategyVersion*{request.strategy_id}*"
    )

    return UpdateResponse(success=True)
```

---

## 4. 설정 관리

### 4.1 CommonSettings 환경변수

**모든 마이크로서비스는 `CommonSettings`를 상속받아 동일한 gRPC 설정을 사용합니다.**

```bash
# .env 파일

# Redis DB 할당
REDIS_DB_GRPC=1          # gRPC 캐시 전용 (L2 Redis cache)
REDIS_DB_RATE_LIMIT=2    # Rate Limiting 전용

# gRPC 서버 기본 설정
GRPC_SERVER_PORT=50051
GRPC_SERVER_MAX_WORKERS=10
GRPC_SERVER_ENABLE_REFLECTION=false  # 프로덕션: false

# Interceptor 활성화/비활성화
GRPC_ENABLE_AUTH=true
GRPC_ENABLE_RATE_LIMITING=true
GRPC_ENABLE_METRICS=true
GRPC_ENABLE_ERROR_HANDLING=true

# Rate Limiting 설정
GRPC_RATE_LIMIT_MAX_REQUESTS=1000
GRPC_RATE_LIMIT_WINDOW_SECONDS=60

# 캐시 설정
GRPC_CACHE_L1_TTL_SECONDS=300      # L1 In-Memory TTL (5분)
GRPC_CACHE_L1_MAX_SIZE=100         # L1 최대 크기
GRPC_CACHE_L2_TTL_SECONDS=3600     # L2 Redis TTL (1시간)
```

### 4.2 서비스별 커스터마이징

```python
# app/core/config.py
from mysingle.core.config import CommonSettings

class StrategyServiceSettings(CommonSettings):
    """Strategy Service 전용 설정"""

    # 서비스별 gRPC 포트
    GRPC_SERVER_PORT: int = 50052

    # 높은 처리량 필요
    GRPC_RATE_LIMIT_MAX_REQUESTS: int = 2000

    # 더 긴 캐시 TTL
    GRPC_CACHE_L1_TTL_SECONDS: int = 600  # 10분

settings = StrategyServiceSettings()
```

### 4.3 환경별 설정

**개발 환경 (.env.development):**
```bash
ENVIRONMENT=development
GRPC_SERVER_ENABLE_REFLECTION=true   # grpcurl 사용 가능
GRPC_ENABLE_AUTH=false               # 로컬 테스트 편의
GRPC_RATE_LIMIT_MAX_REQUESTS=10000   # 제한 완화
```

**프로덕션 (.env.production):**
```bash
ENVIRONMENT=production
GRPC_SERVER_ENABLE_REFLECTION=false  # 보안상 필수
GRPC_ENABLE_AUTH=true
GRPC_RATE_LIMIT_MAX_REQUESTS=1000
GRPC_SERVER_MAX_WORKERS=20           # 고성능 서버
```

---

## 5. Interceptor

### 5.1 표준 Interceptor 체인

**모든 gRPC 서버는 다음 순서로 Interceptor가 자동 적용됩니다:**

```
Request
  │
  ▼
┌─────────────────────────────────────┐
│ 1. MetricsInterceptor               │  ← 전체 latency 측정
│    - Request count, latency 수집    │
│    - Prometheus 메트릭              │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 2. AuthInterceptor                  │  ← 인증 실패 시 조기 종료
│    - X-User-Id 검증                 │
│    - Exempt methods 체크            │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 3. RateLimiterInterceptor           │  ← Redis 기반 속도 제한
│    - Sliding window 알고리즘        │
│    - user_id별 요청 수 제한         │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 4. MetadataInterceptor              │  ← Correlation ID 생성
│    - correlation_id 자동 생성       │
│    - 메타데이터 전파                │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 5. LoggingInterceptor               │  ← 구조화된 로깅
│    - Request/Response 로깅          │
│    - 에러 로깅                      │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 6. ErrorHandlingInterceptor         │  ← 최종 에러 처리
│    - Python 예외 → gRPC StatusCode  │
│    - ValueError → INVALID_ARGUMENT  │
│    - FileNotFoundError → NOT_FOUND  │
└──────────────┬──────────────────────┘
               ▼
          Servicer Method
```

### 5.2 에러 처리 자동화

**Servicer에서 Python 예외를 던지면 자동으로 gRPC 상태 코드로 변환됩니다:**

```python
class StrategyServiceServicer(strategy_service_pb2_grpc.StrategyServiceServicer):
    async def GetStrategyVersion(self, request, context):
        # ❌ Before: 수동 에러 처리
        # try:
        #     version = await StrategyVersion.find_one(...)
        #     if not version:
        #         await context.abort(grpc.StatusCode.NOT_FOUND, "...")
        # except Exception as e:
        #     await context.abort(grpc.StatusCode.INTERNAL, str(e))

        # ✅ After: Python 예외만 던지면 자동 변환
        version = await StrategyVersion.find_one(...)
        if not version:
            raise FileNotFoundError(f"Version not found")  # → NOT_FOUND

        if not self._validate(version):
            raise ValueError("Invalid version format")  # → INVALID_ARGUMENT

        return convert_to_protobuf(version)
```

**자동 변환 규칙:**
- `ValueError` → `INVALID_ARGUMENT`
- `PermissionError` → `PERMISSION_DENIED`
- `FileNotFoundError` → `NOT_FOUND`
- `TimeoutError` → `DEADLINE_EXCEEDED`
- 기타 `Exception` → `INTERNAL`

---

## 6. 모범 사례

### 6.1 서비스 구조 예시

```
my-service/
├── app/
│   ├── core/
│   │   └── config.py              # MyServiceSettings (CommonSettings 상속)
│   ├── grpc_server.py             # MyGrpcServer (BaseGrpcServer 상속)
│   ├── servicers/
│   │   ├── __init__.py
│   │   └── my_servicer.py         # gRPC Servicer 구현
│   └── main.py                    # 서버 시작 로직
├── .env                           # 환경변수 (GRPC_* 설정)
└── pyproject.toml
```

### 6.2 캐시 전략 가이드

| 데이터 유형     | TTL 권장값 | 레이어 | 예시                    |
| --------------- | ---------- | ------ | ----------------------- |
| 정적 메타데이터 | 1시간      | L1+L2  | Indicator 메타데이터    |
| 버전 정보       | 5-10분     | L1+L2  | Strategy 버전           |
| 실시간 데이터   | 1분 이하   | L1     | 주가, 체결              |
| AI 생성 결과    | 캐시 안함  | -      | GenAI 스트리밍 응답     |
| 사용자 프로필   | 10분       | L1+L2  | User 정보 (변경 빈도 ↓) |

### 6.3 성능 최적화 팁

**1. Batch 조회로 N+1 문제 해결:**
```python
async def BatchGetStrategies(self, request, context):
    # ❌ Bad: N+1 쿼리
    # for strategy_id in request.strategy_ids:
    #     strategy = await Strategy.find_one(Strategy.id == strategy_id)

    # ✅ Good: 단일 쿼리
    strategies = await Strategy.find(
        {"id": {"$in": list(request.strategy_ids)}}
    ).to_list()

    # 인덱스 맵 생성
    strategy_map = {str(s.id): s for s in strategies}

    # Streaming 응답
    for strategy_id in request.strategy_ids:
        if strategy_id in strategy_map:
            yield convert_to_protobuf(strategy_map[strategy_id])
```

**2. Connection Pooling 활용:**
```python
class MyGrpcServer(BaseGrpcServer):
    async def before_start(self):
        """MongoDB/Redis 연결은 서버 시작 시 1회만"""
        await super().before_start()

        # Service Factory에서 공유 연결 풀 사용
        from mysingle.database import get_mongodb_client, get_redis_client
        self.mongo = await get_mongodb_client()
        self.redis = await get_redis_client()
```

**3. 캐시 키 최적화:**
```python
# ✅ Good: 결정적 키 생성 (동일 요청 → 동일 키)
cache_key = self._grpc_cache.make_cache_key(
    method="GetStrategy",
    request=request,  # Protobuf는 자동으로 정렬됨
)

# ❌ Bad: 비결정적 키 (매번 다른 키)
cache_key = f"strategy:{time.time()}"  # timestamp 포함
```

### 6.4 테스트 모범 사례

```python
# tests/grpc/test_my_service.py
import pytest
from app.core.config import MyServiceSettings
from app.grpc_server import MyGrpcServer
from mysingle.grpc.server import GrpcServerConfig

@pytest.fixture
async def grpc_server():
    """테스트용 gRPC 서버"""
    settings = MyServiceSettings(
        ENVIRONMENT="test",
        GRPC_ENABLE_AUTH=False,  # 테스트에서 인증 비활성화
        GRPC_ENABLE_RATE_LIMITING=False,
    )

    config = GrpcServerConfig.from_settings(
        settings,
        service_name="test-service",
        port=50099,  # 테스트 전용 포트
    )

    server = MyGrpcServer(config)
    await server.start()

    yield server

    await server.stop()

async def test_get_strategy(grpc_server):
    """gRPC 메서드 테스트"""
    # gRPC 클라이언트 생성
    async with grpc.aio.insecure_channel("localhost:50099") as channel:
        stub = my_service_pb2_grpc.MyServiceStub(channel)

        response = await stub.GetStrategy(
            GetStrategyRequest(strategy_id="test-123")
        )

        assert response.strategy_id == "test-123"
```

---

## 7. 마이그레이션 가이드

### 7.1 기존 서비스에서 이전하기

**Before (기존 함수 기반):**
```python
# old_server.py (150줄)
async def start_grpc_server(port):
    server = grpc.aio.server(
        interceptors=[
            AuthInterceptor(...),
            MetadataInterceptor(...),
            LoggingInterceptor(...),
        ],
        options=[...],
    )

    my_service_pb2_grpc.add_MyServiceServicer_to_server(
        MyServiceServicer(), server
    )

    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    return server
```

**After (BaseGrpcServer):**
```python
# app/grpc_server.py (30줄)
from mysingle.grpc.server import BaseGrpcServer

class MyGrpcServer(BaseGrpcServer):
    def register_servicers(self, server):
        from app.servicers import MyServiceServicer
        from mysingle.protos.services.my_service.v1 import my_service_pb2_grpc

        my_service_pb2_grpc.add_MyServiceServicer_to_server(
            MyServiceServicer(), server
        )

# main.py
from app.core.config import settings

config = GrpcServerConfig.from_settings(settings, service_name="my-service")
grpc_server = MyGrpcServer(config)
await grpc_server.start()
```

**개선 효과:**
- 코드 라인 수 80% 감소
- Interceptor 자동 적용 (6개)
- Prometheus 메트릭 자동 수집
- Graceful shutdown 기본 제공

---

## 8. 트러블슈팅

### 8.1 자주 묻는 질문

**Q: "UNAUTHENTICATED: Missing user-id" 에러가 발생합니다.**

A: gRPC 클라이언트에서 `user-id` 메타데이터를 전송해야 합니다.

```python
# gRPC 클라이언트
from mysingle.grpc import BaseGrpcClient

async with MyServiceClient(user_id=user_id) as client:
    response = await client.stub.GetStrategy(request)
```

또는 테스트 환경에서 인증 비활성화:
```python
config = GrpcServerConfig.from_settings(
    settings,
    service_name="my-service",
    enable_auth=False,  # 테스트 전용
)
```

**Q: 캐시가 작동하지 않습니다.**

A: Servicer에 `_grpc_cache` 속성을 추가했는지 확인하세요.

```python
class MyServiceServicer:
    def __init__(self):
        from app.core.config import settings
        self._grpc_cache = GrpcCache.from_settings(
            settings,
            service_name="my-service"
        )

    @grpc_cached(ttl=300)
    async def GetData(self, request, context):
        ...
```

**Q: Rate Limit에 자주 걸립니다.**

A: `.env`에서 제한 완화:
```bash
GRPC_RATE_LIMIT_MAX_REQUESTS=5000
GRPC_RATE_LIMIT_WINDOW_SECONDS=60
```

### 8.2 디버깅 팁

**Interceptor 로그 확인:**
```bash
# 구조화된 로그에서 gRPC 호출 추적
tail -f logs/app.log | jq 'select(.logger == "mysingle.grpc")'
```

**Prometheus 메트릭 확인:**
```bash
curl http://localhost:8000/metrics | grep mysingle_grpc
```

**gRPC Reflection으로 메서드 확인 (개발 환경):**
```bash
grpcurl -plaintext localhost:50051 list
grpcurl -plaintext localhost:50051 describe my_service.v1.MyService
```

---

## 9. 참고 자료

- **mysingle 패키지 문서:** [AGENTS.md](../../AGENTS.md)
- **gRPC 공식 문서:** https://grpc.io/docs/languages/python/
- **Prometheus 메트릭:** https://prometheus.io/docs/practices/naming/
- **CommonSettings:** [src/mysingle/core/config.py](../core/config.py)

---

**문서 버전:** 2.2.1
**마지막 업데이트:** 2025-12-05
**작성자:** MySingle Quant Platform Team

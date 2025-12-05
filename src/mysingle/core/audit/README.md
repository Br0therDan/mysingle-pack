# Audit Logging Module

**Version:** 2.2.1 | **Updated:** 2025-12-05

HTTP 요청/응답 감사 로그를 자동으로 MongoDB에 저장하는 미들웨어를 제공합니다.

---

## 주요 기능

- **자동 감사 로그 생성**: 모든 HTTP 요청/응답 메타데이터 자동 캡처
- **경로 필터링**: 환경변수로 시스템 레벨 엔드포인트 제외 가능
- **분산 추적**: Correlation ID, Trace ID 지원
- **성능 메트릭**: 응답 시간, 페이로드 크기 측정
- **사용자 컨텍스트**: Kong Gateway/AuthMiddleware 통합

---

## 빠른 시작

### 1. 기본 사용법

```python
from mysingle.core import create_fastapi_app, create_service_config, ServiceType

config = create_service_config(
    service_name="my-service",
    service_type=ServiceType.NON_IAM_SERVICE,
)

app = create_fastapi_app(
    service_config=config,
    audit_logging_enabled=True,  # 감사 로깅 활성화
)
```

### 2. 환경변수 설정

```bash
# .env 파일
AUDIT_LOGGING_ENABLED=true

# 감사 로그에서 제외할 경로 (쉼표로 구분)
AUDIT_EXCLUDE_PATHS="/health,/ready,/metrics,/docs,/openapi.json"
```

### 3. 수동 미들웨어 추가 (고급)

```python
from mysingle.core.audit import AuditLoggingMiddleware

app.add_middleware(
    AuditLoggingMiddleware,
    service_name="my-service",
    enabled=True,
    exclude_paths=["/health", "/ready", "/metrics"],  # 선택적으로 직접 지정
)
```

---

## 경로 필터링

### 기본 제외 경로

기본적으로 다음 경로는 감사 로그에서 제외됩니다:

- `/health` - 헬스 체크
- `/ready` - 준비 상태 확인
- `/metrics` - Prometheus 메트릭
- `/docs` - Swagger UI
- `/openapi.json` - OpenAPI 스펙
- `/redoc` - ReDoc 문서

### 커스텀 제외 경로

환경변수로 제외 경로를 커스터마이징할 수 있습니다:

```bash
# 정확히 일치하는 경로
AUDIT_EXCLUDE_PATHS="/health,/ready,/metrics"

# 와일드카드 패턴 지원 (prefix matching)
AUDIT_EXCLUDE_PATHS="/health,/api/internal/*,/debug/*"
```

**패턴 매칭 규칙:**

- **정확한 일치**: `/health` → `/health`만 매칭
- **Prefix 매칭**: `/api/internal/*` → `/api/internal/...` 하위 모든 경로 매칭

---

## AuditLog 모델

```python
class AuditLog(BaseTimeDoc):
    """HTTP 요청/응답 감사 로그 문서"""

    # 컨텍스트 필드
    user_id: PydanticObjectId | None  # 인증된 사용자 ID
    service: str                        # 서비스 이름
    request_id: str | None              # 고유 요청 ID
    trace_id: str | None                # 분산 추적 ID
    correlation_id: str | None          # 상관관계 ID

    # 요청 메타데이터
    method: str                         # HTTP 메서드
    path: str                           # 요청 경로
    ip: str | None                      # 클라이언트 IP
    user_agent: str | None              # User-Agent
    req_bytes: int                      # 요청 크기 (bytes)

    # 응답 메타데이터
    status_code: int                    # HTTP 상태 코드
    resp_bytes: int                     # 응답 크기 (bytes)

    # 성능 메트릭
    latency_ms: int                     # 응답 시간 (ms)
    occurred_at: datetime               # 요청 발생 시간
```

### 인덱스

효율적인 쿼리를 위해 다음 필드에 인덱스가 생성됩니다:

- `user_id` - 사용자별 활동 조회
- `service` - 서비스별 로그 필터링
- `occurred_at` - 시간 기반 쿼리
- `trace_id` - 분산 추적
- `correlation_id` - 요청 체인 추적

---

## 사용 예시

### 특정 사용자 활동 조회

```python
from mysingle.core.audit import AuditLog
from datetime import datetime, timedelta

# 최근 24시간 내 특정 사용자 활동
cutoff = datetime.utcnow() - timedelta(days=1)
logs = await AuditLog.find(
    AuditLog.user_id == user_id,
    AuditLog.occurred_at >= cutoff
).sort("-occurred_at").to_list()
```

### 느린 요청 분석

```python
# 1초 이상 걸린 요청 조회
slow_requests = await AuditLog.find(
    AuditLog.latency_ms >= 1000,
    AuditLog.service == "strategy-service"
).to_list()
```

### 분산 추적

```python
# 특정 trace_id로 전체 요청 체인 조회
trace_logs = await AuditLog.find(
    AuditLog.trace_id == "trace-123"
).sort("occurred_at").to_list()
```

---

## 통합 가이드

### Kong Gateway 통합

AuditLoggingMiddleware는 Kong Gateway 헤더를 자동으로 인식합니다:

- `X-User-Id` - 사용자 식별
- `X-Request-Id` - 요청 추적
- `X-Trace-Id` / `traceparent` - 분산 추적
- `X-Correlation-Id` - 요청 체인 추적

### AuthMiddleware 통합

AuthMiddleware가 먼저 실행되면 `request.state.user`에서 사용자 정보를 자동으로 추출합니다.

**미들웨어 실행 순서:**

```python
app.add_middleware(AuthMiddleware)  # 1순위
app.add_middleware(AuditLoggingMiddleware)  # 2순위
```

---

## 환경별 동작

### Development

```bash
ENVIRONMENT=development
AUDIT_LOGGING_ENABLED=true
AUDIT_EXCLUDE_PATHS="/health,/ready"
```

→ 감사 로그 활성화, 제외 경로만 스킵

### Test

```bash
ENVIRONMENT=test
AUDIT_LOGGING_ENABLED=true
```

→ **자동으로 비활성화** (DB I/O 제거)

### Production

```bash
ENVIRONMENT=production
AUDIT_LOGGING_ENABLED=true
AUDIT_EXCLUDE_PATHS="/health,/ready,/metrics"
```

→ 감사 로그 활성화, 시스템 엔드포인트 제외

---

## 성능 고려사항

### 비동기 삽입

감사 로그는 비동기로 MongoDB에 삽입되지만, 응답 전송 전에 완료됩니다.

### 에러 처리

감사 로그 삽입 실패 시:
- 응답에는 영향 없음 (사용자에게 투명)
- 구조화된 로깅으로 에러 기록
- 메트릭 카운터 증가

### DB 부하 최적화

불필요한 로그를 제외하여 DB 부하 감소:

```bash
# Health check가 1초마다 실행되는 경우
# 하루 86,400개 로그 → 0개로 감소
AUDIT_EXCLUDE_PATHS="/health,/ready,/metrics"
```

---

## 모범 사례

### ✅ DO

- 프로덕션에서 `/health`, `/ready`, `/metrics` 제외
- `AUDIT_LOGGING_ENABLED=true` 명시적 설정
- 분산 추적을 위해 `X-Correlation-Id` 전파
- 주기적으로 오래된 로그 아카이브/삭제

### ❌ DON'T

- 민감한 데이터를 요청/응답 바디에 포함 (메타데이터만 저장)
- 모든 경로 제외 (감사 로그 목적 상실)
- 테스트 환경에서 강제 활성화
- 수동으로 AuditLog 생성 (미들웨어 사용)

---

## 문제 해결

### 감사 로그가 생성되지 않음

1. 환경변수 확인:
   ```bash
   AUDIT_LOGGING_ENABLED=true
   ENVIRONMENT!=test
   ```

2. MongoDB 연결 확인:
   ```python
   from mysingle.core.audit import AuditLog
   await AuditLog.find_one()  # 연결 테스트
   ```

3. 제외 경로 확인:
   ```bash
   # 로그에서 확인
   "Audit logging middleware initialized" exclude_paths=[...]
   ```

### 너무 많은 로그 생성

```bash
# 더 많은 경로 제외
AUDIT_EXCLUDE_PATHS="/health,/ready,/metrics,/api/internal/*"
```

---

## 변경 이력

### v2.2.1 (2025-12-05)

- **FEATURE**: `AUDIT_EXCLUDE_PATHS` 환경변수 추가
- **FEATURE**: 와일드카드 패턴 매칭 지원
- **IMPROVEMENT**: 기본 제외 경로 추가 (`/health`, `/ready`, `/metrics`, etc.)
- **DOCS**: README 작성

### v2.2.0

- 초기 릴리스

---

## 관련 문서

- **FastAPI App Factory**: `docs/MYSINGLE_APP_FACTORY_USAGE_GUIDE.md`
- **인증**: `src/mysingle/auth/README.md`
- **코어 모듈**: `src/mysingle/core/README.md`

---

**Platform**: MySingle Quant (Beta: Early 2026)
**License**: MIT

# Port Configuration Enhancement - Changelog

**Date**: 2025-12-05
**Version**: 2.5.3 (준비중)
**Category**: Architecture Improvement

---

## Summary

BaseGrpcClient의 포트 설정을 환경 변수로 오버라이드할 수 있도록 개선하여, 서비스별 포트 하드코딩을 제거하고 배포 환경별 유연성을 향상시켰습니다.

---

## Changes

### 1. BaseGrpcClient 개선 (`src/mysingle/clients/base_grpc_client.py`)

**추가된 메서드:**
```python
def _determine_port(self) -> int:
    """
    환경 기반 포트 결정

    우선순위:
    1. 환경변수 {SERVICE}_GRPC_PORT (예: SUBSCRIPTION_GRPC_PORT)
    2. default_port 파라미터
    """
```

**변경 사항:**
- 호스트와 동일한 패턴으로 포트도 환경 변수 우선 처리
- 잘못된 환경 변수 값 시 경고 로그 + 기본값 폴백
- 서비스명 변환 로직: `subscription-service` → `SUBSCRIPTION_GRPC_PORT`

**영향:**
- 모든 BaseGrpcClient 기반 클라이언트가 자동으로 혜택 받음
- 기존 코드 변경 불필요 (하위 호환성 유지)

---

### 2. SubscriptionServiceClient 문서 개선 (`src/mysingle/subscription/client.py`)

**변경 전:**
```python
"""This client wraps gRPC calls to Subscription Service (port 50057)."""
```

**변경 후:**
```python
"""
Port Configuration:
    - Default: 50052 (Subscription Service gRPC port)
    - Override via environment variable: SUBSCRIPTION_GRPC_PORT=50052
"""
```

**`__init__` 문서 개선:**
```python
"""
Port is determined by BaseGrpcClient in the following priority:
1. Environment variable: SUBSCRIPTION_GRPC_PORT
2. Default port: 50052
"""
```

**코멘트 명확화:**
```python
default_port=50052,  # Fallback if SUBSCRIPTION_GRPC_PORT not set
```

---

### 3. BaseGrpcClient 문서 업데이트 (`src/mysingle/clients/README.md`)

**추가된 섹션:** "Environment Configuration"

**내용:**
- Host 우선순위: `{SERVICE}_GRPC_HOST` > Docker 감지 > `localhost`
- Port 우선순위: `{SERVICE}_GRPC_PORT` > `default_port`
- 서비스명 매핑 예시:
  - `backtest-service` → `BACKTEST_GRPC_HOST`, `BACKTEST_GRPC_PORT`
  - `subscription-service` → `SUBSCRIPTION_GRPC_HOST`, `SUBSCRIPTION_GRPC_PORT`

**설정 예시:**
```bash
# 호스트 + 포트 오버라이드
export BACKTEST_GRPC_HOST=backtest.example.com
export BACKTEST_GRPC_PORT=9090

# 포트만 오버라이드
export SUBSCRIPTION_GRPC_PORT=50052
```

---

## Test Results

### Test 1: 기본 포트 (환경 변수 없음)
```
address = localhost:50052  ✅
```

### Test 2: 환경 변수 오버라이드
```bash
export SUBSCRIPTION_GRPC_PORT=60000
```
```
address = localhost:60000  ✅
```

### Test 3: 잘못된 포트 (폴백)
```bash
export SUBSCRIPTION_GRPC_PORT=invalid
```
```
[WARNING] Invalid port in environment variable SUBSCRIPTION_GRPC_PORT=invalid,
          using default_port=50052
address = localhost:50052  ✅
```

---

## Migration Guide

### For Service Developers

**기존 코드 (변경 불필요):**
```python
class SubscriptionServiceClient(BaseGrpcClient):
    def __init__(self, user_id=None, correlation_id=None):
        super().__init__(
            service_name="subscription-service",
            default_port=50052,  # 이제 fallback으로 동작
            user_id=user_id,
            correlation_id=correlation_id,
        )
```

**환경별 설정:**

**개발 환경 (.env):**
```bash
SUBSCRIPTION_GRPC_PORT=50052
SUBSCRIPTION_GRPC_HOST=localhost
```

**스테이징 환경:**
```bash
SUBSCRIPTION_GRPC_PORT=50052
SUBSCRIPTION_GRPC_HOST=subscription-service.staging.svc.cluster.local
```

**프로덕션 환경:**
```bash
SUBSCRIPTION_GRPC_PORT=9090
SUBSCRIPTION_GRPC_HOST=subscription-service.prod.svc.cluster.local
```

### For Service Consumers (GenAI Service 예시)

**GenAI Service config.py:**
```python
class Settings(CommonSettings):
    # 환경 변수로 오버라이드 가능
    SUBSCRIPTION_GRPC_PORT: int = 50052  # 기본값
    SUBSCRIPTION_GRPC_HOST: str = "subscription-service"  # Docker 기본값
```

**Docker Compose:**
```yaml
genai-service:
  environment:
    - SUBSCRIPTION_GRPC_PORT=50052
    - SUBSCRIPTION_GRPC_HOST=subscription-service
```

**Kubernetes ConfigMap:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: genai-service-config
data:
  SUBSCRIPTION_GRPC_PORT: "50052"
  SUBSCRIPTION_GRPC_HOST: "subscription-service.default.svc.cluster.local"
```

---

## Benefits

### 1. 배포 환경별 유연성
- 개발/스테이징/프로덕션 환경에서 서로 다른 포트 사용 가능
- 포트 충돌 시 환경 변수로 즉시 변경 가능

### 2. 하드코딩 제거
- 소스 코드 수정 없이 인프라 설정으로 포트 변경
- Kubernetes/Docker Compose 설정 중앙화

### 3. 일관된 패턴
- 호스트와 포트 모두 동일한 환경 변수 패턴 사용
- 서비스명 기반 자동 변환 (`subscription-service` → `SUBSCRIPTION`)

### 4. 하위 호환성
- 기존 코드 동작 변경 없음
- 환경 변수 없으면 `default_port` 사용

---

## Breaking Changes

**없음** - 완전한 하위 호환성 유지

---

## Next Steps

1. **mysingle-pack 버전 업데이트**: v2.5.2 → v2.5.3
2. **genai-service 의존성 업데이트**: mysingle-pack@v2.5.3
3. **통합 테스트 실행**: GenAI ↔ Subscription Service 연동
4. **문서 배포**: README.md 업데이트

---

## References

- **PR**: (TBD)
- **Issue**: Port configuration hardcoding in SubscriptionServiceClient
- **Related Files**:
  - `src/mysingle/clients/base_grpc_client.py` (+ `_determine_port()`)
  - `src/mysingle/subscription/client.py` (문서 개선)
  - `src/mysingle/clients/README.md` (환경 설정 섹션 추가)

---

**Author**: GenAI Team, Architecture Team
**Reviewers**: Backend Team Lead

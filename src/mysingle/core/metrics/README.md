# Enhanced Metrics System

고성능 메트릭 수집 및 모니터링 시스템으로, FastAPI 애플리케이션의 성능 지표를 효율적으로 수집하고 제공합니다.

## 주요 기능

### 🚀 성능 최적화
- **비동기 메트릭 수집**: 요청 처리 지연 최소화
- **메모리 효율적 데이터 구조**: 제한된 메모리 사용량
- **자동 정리**: 오래된 데이터 자동 제거
- **경로 정규화**: ID 패턴 자동 정규화로 메트릭 집계 최적화

### 📊 풍부한 메트릭
- **기본 메트릭**: 요청 수, 에러 수, 응답 시간
- **백분위수**: P50, P90, P95, P99 응답 시간
- **히스토그램**: 응답 시간 분포
- **상태 코드 분석**: HTTP 상태 코드별 통계

### 🔧 설정 가능
- **수집 범위 조절**: 샘플 수, 보존 기간 설정
- **제외 경로**: 성능을 위한 경로 필터링
- **출력 형식**: JSON, Prometheus 형식 지원

## 설치 및 설정

### 기본 설정

```python
from mysingle.core.app_factory import create_fastapi_app
from mysingle.core.service_types import ServiceConfig

# 메트릭이 활성화된 서비스 설정
service_config = ServiceConfig(
    service_name="my-service",
    service_version="1.0.0",
    enable_metrics=True,  # 메트릭 활성화
)

app = create_fastapi_app(service_config)
```

### 고급 설정

```python
from mysingle.metrics import MetricsConfig, create_metrics_middleware

# 커스텀 메트릭 설정
metrics_config = MetricsConfig(
    max_duration_samples=2000,      # 응답 시간 샘플 수
    enable_percentiles=True,        # 백분위수 계산 활성화
    enable_histogram=True,          # 히스토그램 활성화
    retention_period_seconds=7200,  # 2시간 데이터 보존
    cleanup_interval_seconds=600,   # 10분마다 정리
)

# 제외할 경로 설정
exclude_paths = {
    "/health", "/metrics", "/docs",
    "/static", "/assets", "/favicon.ico"
}

# 수동으로 메트릭 미들웨어 설정
create_metrics_middleware(
    service_name="my-service",
    config=metrics_config,
    exclude_paths=exclude_paths
)
```

## API 엔드포인트

메트릭이 활성화되면 다음 엔드포인트가 자동으로 추가됩니다:

### 기본 메트릭

```bash
# JSON 형식으로 전체 메트릭 조회
GET /metrics/

# Prometheus 형식으로 메트릭 조회
GET /metrics/prometheus

# JSON 형식 메트릭 (명시적)
GET /metrics/json
```

### 요약 정보

```bash
# 요약된 메트릭 (라우트 상세 제외)
GET /metrics/summary

# 메트릭 시스템 상태 확인
GET /metrics/health
```

### 라우트별 상세 정보

```bash
# 모든 라우트 메트릭
GET /metrics/routes

# 특정 패턴 필터링
GET /metrics/routes?route_filter=api/v1
```

### 관리 기능

```bash
# 메트릭 초기화 (테스트/디버깅용)
POST /metrics/reset
```

## 메트릭 예시

### JSON 응답 예시

```json
{
  "service": "strategy-service",
  "timestamp": 1697123456.789,
  "uptime_seconds": 3600.5,
  "total_requests": 1250,
  "total_errors": 15,
  "error_rate": 0.012,
  "requests_per_second": 0.347,
  "active_routes": 8,
  "config": {
    "max_duration_samples": 1000,
    "enable_percentiles": true,
    "enable_histogram": true,
    "retention_period_seconds": 3600
  },
  "routes": {
    "GET:/api/v1/strategies": {
      "request_count": 245,
      "error_count": 2,
      "error_rate": 0.008,
      "status_codes": {
        "200": 243,
        "404": 2
      },
      "avg_response_time": 0.156,
      "min_response_time": 0.045,
      "max_response_time": 1.234,
      "p50": 0.123,
      "p90": 0.289,
      "p95": 0.456,
      "p99": 0.890,
      "histogram": {
        "buckets": {
          "le_0.100": 89,
          "le_0.200": 134,
          "le_0.500": 20,
          "le_1.000": 2
        },
        "bucket_size": 0.062,
        "total_samples": 245
      },
      "last_accessed": 1697123456.789
    }
  }
}
```

### Prometheus 형식 예시

```prometheus
# HELP strategy_service_uptime_seconds Service uptime in seconds
# TYPE strategy_service_uptime_seconds gauge
strategy_service_uptime_seconds 3600.50

# HELP strategy_service_requests_total Total number of requests
# TYPE strategy_service_requests_total counter
strategy_service_requests_total 1250

# HELP strategy_service_route_duration_p95_seconds P95 response time per route
# TYPE strategy_service_route_duration_p95_seconds gauge
strategy_service_route_duration_p95_seconds{method="GET",path="/api/v1/strategies"} 0.4560
```

## 성능 최적화 기능

### 자동 경로 정규화

ID가 포함된 경로를 자동으로 정규화하여 메트릭을 효율적으로 집계합니다:

```
/api/v1/strategies/123e4567-e89b-12d3-a456-426614174000  →  /api/v1/strategies/{uuid}
/api/v1/users/42                                        →  /api/v1/users/{id}
```

### 메모리 관리

- **순환 버퍼**: 응답 시간 샘플을 제한된 메모리로 관리
- **자동 정리**: 설정된 시간 후 오래된 데이터 자동 제거
- **백그라운드 작업**: 메인 요청 처리에 영향 없는 정리 작업

### 경로 제외

성능을 위해 메트릭 수집에서 제외할 경로들:

```python
exclude_paths = {
    "/health",          # 헬스체크
    "/metrics",         # 메트릭 자체
    "/docs",            # API 문서
    "/static/",         # 정적 파일
    "/favicon.ico",     # 파비콘
}
```

## 모니터링 및 알림

### Prometheus와 연동

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'quant-services'
    static_configs:
      - targets: ['localhost:8501', 'localhost:8502', 'localhost:8503']
    metrics_path: '/metrics/prometheus'
    scrape_interval: 30s
```

### Grafana 대시보드

주요 메트릭 시각화:

1. **서비스 개요**: 요청률, 에러율, 응답 시간
2. **라우트별 성능**: 각 엔드포인트의 상세 메트릭
3. **에러 분석**: 상태 코드별 에러 분포
4. **응답 시간 분포**: 히스토그램 및 백분위수

### 알림 규칙

```yaml
# alerting.yml
groups:
  - name: quant_services
    rules:
      - alert: HighErrorRate
        expr: rate(service_errors_total[5m]) / rate(service_requests_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected in {{ $labels.service }}"

      - alert: HighResponseTime
        expr: service_route_duration_p95_seconds > 1.0
        for: 2m
        annotations:
          summary: "High response time in {{ $labels.service }}"
```

## 문제 해결

### 메모리 사용량이 높은 경우

```python
# 샘플 수 줄이기
metrics_config = MetricsConfig(
    max_duration_samples=500,        # 기본 1000에서 줄임
    retention_period_seconds=1800,   # 30분으로 줄임
    cleanup_interval_seconds=60,     # 1분마다 정리
)
```

### 성능 영향이 큰 경우

```python
# 기능 비활성화
metrics_config = MetricsConfig(
    enable_percentiles=False,        # 백분위수 계산 비활성화
    enable_histogram=False,          # 히스토그램 비활성화
)

# 더 많은 경로 제외
exclude_paths = {
    "/health", "/metrics", "/docs", "/redoc", "/openapi.json",
    "/static", "/assets", "/favicon.ico", "/robots.txt",
    "/api/health",  # 추가 헬스체크 경로
}
```

### 메트릭이 수집되지 않는 경우

1. **설정 확인**:
   ```python
   service_config.enable_metrics = True  # 메트릭 활성화 확인
   ```

2. **로그 확인**:
   ```bash
   # 메트릭 초기화 로그 확인
   grep "Metrics collector initialized" logs/app.log
   ```

3. **엔드포인트 테스트**:
   ```bash
   curl http://localhost:8501/metrics/health
   ```

## 예제 코드

### 커스텀 메트릭 추가

```python
from mysingle.metrics import get_metrics_collector

# 현재 컬렉터 가져오기
collector = get_metrics_collector()

# 수동으로 메트릭 기록
collector.record_request_sync(
    method="POST",
    path="/api/v1/custom",
    status_code=201,
    duration=0.234
)
```

### 메트릭 기반 헬스체크

```python
from fastapi import APIRouter, Depends
from mysingle.metrics import get_metrics_collector

router = APIRouter()

@router.get("/custom-health")
async def custom_health_check(
    collector: MetricsCollector = Depends(get_metrics_collector)
):
    metrics = collector.get_metrics()

    # 커스텀 헬스체크 로직
    is_healthy = (
        metrics["error_rate"] < 0.05 and  # 에러율 5% 미만
        metrics["total_requests"] > 0      # 요청이 있음
    )

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "error_rate": metrics["error_rate"],
        "total_requests": metrics["total_requests"]
    }
```

## 라이센스

이 메트릭 시스템은 퀀트 플랫폼의 일부로 제공됩니다.

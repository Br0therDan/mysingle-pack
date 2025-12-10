# MySingle Database 모듈

**버전:** 2.2.1 | **모듈:** `mysingle.database`

MySingle Quant 서비스를 위한 고성능 데이터베이스 및 캐싱 유틸리티입니다.

---

## 개요

`mysingle.database` 모듈은 MySingle Quant 서비스를 위한 표준화된 데이터베이스 및 캐싱 관리를 제공합니다:

- **Redis**: 고성능 캐싱 및 서비스 간 데이터 공유
- **DuckDB**: 분석 워크로드 및 시계열 데이터 처리

---

## 모듈 구조

```
database/
├── __init__.py          # 통합 export
├── README.md            # 이 파일
├── redis/               # Redis 캐싱 모듈
│   ├── __init__.py
│   ├── README.md        # Redis 상세 가이드
│   ├── client.py        # Redis 클라이언트 관리
│   ├── cache.py         # 기본 캐시 클래스
│   └── factory.py       # 캐시 팩토리 함수
└── duckdb/              # DuckDB 분석 모듈
    ├── __init__.py
    ├── README.md        # DuckDB 상세 가이드
    └── manager.py       # DuckDB 매니저
```

---

## 빠른 시작

### Redis 캐싱

```python
from mysingle.database import create_service_cache
from mysingle.core.config import settings

# 서비스별 캐시 생성
cache = create_service_cache(
    service_name="backtest",
    db_constant=settings.REDIS_DB_BACKTEST,
)

await cache.set("job:123", job_data, ttl=3600)
result = await cache.get("job:123")
```

### DuckDB 분석

```python
from mysingle.database import BaseDuckDBManager

class AnalyticsManager(BaseDuckDBManager):
    def _create_tables(self) -> None:
        self.duckdb_conn.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                event_data JSON,
                created_at TIMESTAMP NOT NULL
            )
        """)

with AnalyticsManager(db_path="data/analytics.duckdb") as db:
    results = db.query_data()
```

---

## 설치

```bash
# Database extras 포함 설치
pip install mysingle[database]

# 또는 공통 의존성 포함
pip install mysingle[common-grpc]
```

---

## 상세 문서

각 서브모듈의 상세 가이드는 해당 폴더의 README.md를 참조하세요:

- **[Redis 캐싱 가이드](redis/README.md)** - Redis 클라이언트, 캐시, 팩토리 함수
- **[DuckDB 분석 가이드](duckdb/README.md)** - DuckDB 매니저, 캐싱, 쿼리

---

## 주요 기능

### Redis 모듈

- 플랫폼 전체 DB 할당 표준 (0-15)
- 팩토리 함수를 통한 표준화된 캐시 생성
- 자동 연결 풀 관리
- TTL 기반 캐시 만료
- JSON/Pickle 직렬화

### DuckDB 모듈

- 컨텍스트 관리자를 통한 안전한 리소스 처리
- 내장 TTL 캐싱
- Pydantic 모델 자동 직렬화
- 파일 잠금 시 자동 메모리 DB 전환
- 고성능 OLAP 쿼리

---

## 환경 변수

```bash
# Redis 구성
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# DuckDB 구성
BACKTEST_DB_PATH=/data/backtests.duckdb
ANALYTICS_DB_PATH=/data/analytics.duckdb
```

---

## 관련 문서

- [구조화된 로깅 가이드](../../docs/core/STRUCTURED_LOGGING_GUIDE.md)
- [Core 모듈 README](../core/README.md)

---

**버전:** 2.2.1
**모듈:** `mysingle.database`
**라이선스:** MIT

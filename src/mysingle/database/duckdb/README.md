# DuckDB 데이터베이스 모듈

**버전:** 2.2.1 | **모듈:** `mysingle.database.duckdb`

MySingle Quant 서비스를 위한 고성능 분석형 데이터베이스 관리 모듈입니다.

---

## 개요

DuckDB 모듈은 분석 워크로드와 시계열 데이터를 위한 표준화된 데이터베이스 관리를 제공합니다:

- **컨텍스트 관리**: 안전한 리소스 처리
- **내장 캐싱**: TTL 기반 자동 캐싱
- **JSON 직렬화**: Pydantic 모델 자동 변환
- **Fallback 지원**: 파일 잠금 시 메모리 DB로 자동 전환

### 주요 기능

| 기능              | 설명                        |
| ----------------- | --------------------------- |
| **컨텍스트 관리** | 자동 연결 및 정리           |
| **TTL 캐싱**      | 시간 기반 캐시 만료         |
| **JSON 직렬화**   | 복잡한 객체 자동 변환       |
| **자동 Fallback** | 잠금 오류 시 메모리 DB 사용 |
| **구조화된 로깅** | Correlation ID 포함 로깅    |
| **분석 쿼리**     | 고성능 OLAP 쿼리 지원       |
| **시계열 데이터** | 효율적인 시계열 데이터 처리 |

---

## 설치

```bash
# Database extras 포함 설치
pip install mysingle[database]

# 또는 공통 의존성 포함
pip install mysingle[common-grpc]
```

---

## 빠른 시작

### 기본 사용법

```python
from datetime import UTC, datetime
import uuid
from mysingle.database import BaseDuckDBManager

class BacktestDataManager(BaseDuckDBManager):
    """백테스트 결과 저장을 위한 DuckDB 매니저"""

    def _create_tables(self) -> None:
        """백테스트 전용 테이블 생성"""
        self.duckdb_conn.execute("""
            CREATE TABLE IF NOT EXISTS backtest_results (
                id VARCHAR PRIMARY KEY,
                strategy_id VARCHAR NOT NULL,
                user_id VARCHAR NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                total_return DOUBLE,
                sharpe_ratio DOUBLE,
                max_drawdown DOUBLE,
                trades JSON,
                created_at TIMESTAMP NOT NULL
            )
        """)

        # 인덱스 생성
        self.duckdb_conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_backtest_strategy
            ON backtest_results(strategy_id)
        """)

# 컨텍스트 관리자 사용 (권장)
with BacktestDataManager(db_path="data/backtests.duckdb") as db:
    # 연결이 자동으로 설정됨
    result = db.store_backtest_result(result_data)
    results = db.get_user_backtests(user_id)
# 연결이 자동으로 종료됨
```

### 내장 캐싱 사용

```python
# 캐시에 데이터 저장
data = [
    {"symbol": "AAPL", "price": 150.25, "volume": 1000000},
    {"symbol": "GOOGL", "price": 2800.50, "volume": 500000},
]

db.store_cache_data(
    cache_key="market_data:2024-12-10",
    data=data,
    table_name="market_cache"
)

# TTL과 함께 캐시 데이터 조회
cached_data = db.get_cache_data(
    cache_key="market_data:2024-12-10",
    table_name="market_cache",
    ttl_hours=24  # 24시간 후 만료
)

if cached_data:
    print(f"캐시에서 {len(cached_data)}개 레코드 발견")
else:
    print("캐시 미스 - 새 데이터 가져오기")
```

### JSON 직렬화

```python
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class TradeResult(BaseModel):
    symbol: str
    quantity: int
    price: Decimal
    executed_at: datetime

# 복잡한 타입 자동 직렬화
trade = TradeResult(
    symbol="AAPL",
    quantity=100,
    price=Decimal("150.25"),
    executed_at=datetime.now(UTC)
)

# JSON 직렬화 가능한 형식으로 변환
serializable = db._make_json_serializable(trade)
# 결과: {"symbol": "AAPL", "quantity": 100, "price": 150.25,
#        "executed_at": "2024-12-10T10:30:45.123Z"}
```

---

## 핵심 컴포넌트

### BaseDuckDBManager

모든 DuckDB 작업을 위한 기본 클래스로, 내장 캐싱 및 연결 관리 기능을 제공합니다.

#### 주요 메서드

| 메서드                      | 설명                            |
| --------------------------- | ------------------------------- |
| `connect()`                 | 데이터베이스 연결 설정          |
| `close()`                   | 연결 종료 및 리소스 정리        |
| `store_cache_data()`        | TTL과 함께 캐시에 데이터 저장   |
| `get_cache_data()`          | 캐시된 데이터 조회              |
| `_create_tables()`          | 서비스 테이블 생성 (오버라이드) |
| `_make_json_serializable()` | 객체를 JSON 호환 형식으로 변환  |

#### 속성

| 속성          | 타입                       | 설명                   |
| ------------- | -------------------------- | ---------------------- |
| `duckdb_conn` | `DuckDBPyConnection`       | 활성 데이터베이스 연결 |
| `db_path`     | `str`                      | 데이터베이스 파일 경로 |
| `connection`  | `DuckDBPyConnection\|None` | 원시 연결 객체         |

---

## 구성

### 데이터베이스 경로

```python
# 프로덕션: 파일 기반
db = MyDataManager(db_path="/data/analytics/prod.duckdb")

# 개발: 로컬 파일
db = MyDataManager(db_path="./dev_data/analytics.duckdb")

# 테스트: 메모리 내 (명시적)
db = MyDataManager(db_path=":memory:")

# 자동 Fallback: 잠금 시 메모리 DB로 전환
db = MyDataManager(db_path="/data/locked.duckdb")
# 파일이 잠겨있으면 자동으로 :memory: 사용
```

### 환경 변수

```bash
# 서비스별 데이터베이스 경로
export BACKTEST_DB_PATH="/data/backtests/prod.duckdb"
export ANALYTICS_DB_PATH="/data/analytics/prod.duckdb"

# 캐시 TTL 구성
export CACHE_TTL_HOURS=24
```

```python
import os

db_path = os.getenv("BACKTEST_DB_PATH", "./data/backtests.duckdb")
cache_ttl = int(os.getenv("CACHE_TTL_HOURS", "24"))

db = BacktestDataManager(db_path=db_path)
cached_data = db.get_cache_data(cache_key, ttl_hours=cache_ttl)
```

---

## 고급 사용법

### 복잡한 쿼리

```python
class AnalyticsManager(BaseDuckDBManager):
    """고급 분석 쿼리"""

    def get_top_strategies(self, limit: int = 10) -> list[dict]:
        """상위 성과 전략 조회"""
        result = self.duckdb_conn.execute("""
            SELECT
                strategy_id,
                COUNT(*) as backtest_count,
                AVG(total_return) as avg_return,
                AVG(sharpe_ratio) as avg_sharpe,
                MAX(created_at) as last_backtest
            FROM backtest_results
            GROUP BY strategy_id
            HAVING avg_sharpe > 1.0
            ORDER BY avg_return DESC
            LIMIT ?
        """, [limit]).fetchall()

        return [
            {
                "strategy_id": row[0],
                "backtest_count": row[1],
                "avg_return": row[2],
                "avg_sharpe": row[3],
                "last_backtest": row[4],
            }
            for row in result
        ]
```

### 배치 작업

```python
def batch_insert_trades(self, trades: list[dict]) -> int:
    """여러 거래를 효율적으로 삽입"""
    try:
        # 데이터 준비
        serialized_trades = [
            self._make_json_serializable(trade) for trade in trades
        ]

        # 배치 삽입
        self.duckdb_conn.executemany("""
            INSERT INTO trades (id, strategy_id, symbol, quantity, price, executed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (
                str(uuid.uuid4()),
                trade["strategy_id"],
                trade["symbol"],
                trade["quantity"],
                trade["price"],
                trade["executed_at"],
            )
            for trade in serialized_trades
        ])

        return len(trades)
    except Exception as e:
        logger.error(f"배치 삽입 실패: {e}")
        return 0
```

### 다중 캐시 테이블

```python
class MultiCacheManager(BaseDuckDBManager):
    """여러 캐시 테이블을 가진 매니저"""

    def _create_tables(self) -> None:
        """여러 캐시 테이블 생성"""
        # 시장 데이터 캐시
        self._create_cache_table("market_data_cache")

        # 전략 캐시
        self._create_cache_table("strategy_cache")

        # 사용자 선호도 캐시
        self._create_cache_table("user_prefs_cache")

    def cache_market_data(self, symbol: str, data: list[dict]) -> bool:
        """심볼별 시장 데이터 캐싱"""
        return self.store_cache_data(
            cache_key=f"market:{symbol}",
            data=data,
            table_name="market_data_cache"
        )

    def get_market_data(self, symbol: str, ttl_hours: int = 1) -> list[dict] | None:
        """캐시된 시장 데이터 조회 (실시간 데이터용 짧은 TTL)"""
        return self.get_cache_data(
            cache_key=f"market:{symbol}",
            table_name="market_data_cache",
            ttl_hours=ttl_hours
        )
```

---

## 연결 관리 패턴

```python
# 패턴 1: 컨텍스트 관리자 (권장)
with MyDataManager(db_path=db_path) as db:
    results = db.query_data()
    # 자동으로 종료됨

# 패턴 2: try-finally를 사용한 수동 관리
db = MyDataManager(db_path=db_path)
db.connect()
try:
    results = db.query_data()
finally:
    db.close()  # 항상 실행됨

# 패턴 3: 장기 실행 연결 (서비스 시작 시)
class MyService:
    def __init__(self):
        self.db = MyDataManager(db_path=db_path)
        self.db.connect()

    def shutdown(self):
        self.db.close()
```

---

## 모범 사례

### ✅ 권장

```python
# 자동 정리를 위한 컨텍스트 관리자 사용
with MyDataManager(db_path="data.duckdb") as db:
    db.store_cache_data(cache_key, data)

# 반환값 확인
success = db.store_cache_data(cache_key, data)
if not success:
    logger.warning("캐시 쓰기 실패")

# TTL과 함께 구조화된 캐싱 사용
cached = db.get_cache_data(cache_key, ttl_hours=24)
if cached is None:
    cached = fetch_fresh_data()
    db.store_cache_data(cache_key, cached)

# 저장 전 복잡한 객체 직렬화
serializable = db._make_json_serializable(pydantic_model)

# 자주 쿼리하는 컬럼에 인덱스 생성
self.duckdb_conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_user_id ON table(user_id)
""")
```

### ❌ 금지

```python
# 연결 닫기 잊지 말 것
db = MyDataManager(db_path="data.duckdb")
db.connect()
# ... 작업 ...
# db.close() 누락 - 리소스 누수!

# 캐시 실패 무시
db.store_cache_data(cache_key, data)  # 반환값 무시

# 직렬화되지 않은 객체 직접 저장
db.duckdb_conn.execute("INSERT ...", [datetime_object])  # 실패할 수 있음

# 모든 메서드에서 테이블 생성
def my_method(self):
    self.duckdb_conn.execute("CREATE TABLE ...")  # _create_tables()에 있어야 함

# 하드코딩된 경로 사용
db = MyDataManager(db_path="/hardcoded/path.duckdb")  # 설정/환경 변수 사용
```

---

## 성능 팁

### 1. 배치 작업 사용

```python
# 나쁨: 여러 개별 삽입
for trade in trades:
    db.duckdb_conn.execute("INSERT ...", [trade])

# 좋음: 배치 삽입
db.duckdb_conn.executemany("INSERT ...", trades)
```

### 2. 적절한 인덱스 생성

```python
# 자주 쿼리하는 컬럼 인덱싱
self.duckdb_conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_user_date
    ON analytics(user_id, created_at)
""")
```

### 3. 효과적인 캐시 사용

```python
# 실시간 데이터용 짧은 TTL
market_data = db.get_cache_data(f"market:{symbol}", ttl_hours=1)

# 정적 데이터용 긴 TTL
strategy_config = db.get_cache_data(f"config:{id}", ttl_hours=168)  # 1주
```

### 4. 연결 풀링

```python
# 장기 실행 서비스에서 연결 재사용
class AnalyticsService:
    def __init__(self):
        self.db = AnalyticsManager(db_path=config.DB_PATH)
        self.db.connect()

    async def on_shutdown(self):
        self.db.close()
```

---

## 문제 해결

### 데이터베이스 잠금

**증상:** `database is locked` 오류

**해결:** BaseDuckDBManager가 자동으로 메모리 내 데이터베이스로 전환
```python
# 자동 fallback이 로그에 기록됨
# WARNING: Falling back to in-memory database (reason: file_locked)
```

### 캐시가 작동하지 않음

**증상:** `get_cache_data()`가 항상 None 반환

**가능한 원인:**
1. TTL 만료 - `ttl_hours` 증가
2. 테이블 미생성 - `_create_cache_table()` 호출 확인
3. 연결 문제 - 구조화된 로그 확인

**디버깅:**
```python
# 디버그 로깅 활성화
import logging
logging.getLogger("mysingle.database").setLevel(logging.DEBUG)

# 캐시 테이블 존재 확인
result = db.duckdb_conn.execute("""
    SELECT name FROM sqlite_master WHERE type='table'
""").fetchall()
print("테이블:", result)
```

### JSON 직렬화 오류

**증상:** `TypeError: Object of type X is not JSON serializable`

**해결:** `_make_json_serializable()` 사용
```python
# 이전
data = {"datetime": datetime.now(), "decimal": Decimal("10.5")}

# 이후
serializable = db._make_json_serializable(data)
# 결과: {"datetime": "2024-12-10T10:30:45.123Z", "decimal": 10.5}
```

---

## API 레퍼런스

### BaseDuckDBManager

```python
class BaseDuckDBManager:
    def __init__(self, db_path: str) -> None: ...

    def connect(self) -> None: ...
    def close(self) -> None: ...

    def store_cache_data(
        self,
        cache_key: str,
        data: list[dict],
        table_name: str = "cache_data"
    ) -> bool: ...

    def get_cache_data(
        self,
        cache_key: str,
        table_name: str = "cache_data",
        ttl_hours: int = 24
    ) -> list[dict] | None: ...

    def _create_tables(self) -> None: ...  # 추상 - 반드시 오버라이드
    def _create_cache_table(self, table_name: str) -> None: ...
    def _make_json_serializable(self, obj: Any) -> Any: ...
    def _ensure_connected(self) -> None: ...

    @property
    def duckdb_conn(self) -> duckdb.DuckDBPyConnection: ...
```

---

## 테스트

### In-Memory 테스팅

```python
def test_with_real_duckdb():
    """실제 메모리 내 DuckDB로 테스트"""
    with MyDataManager(db_path=":memory:") as db:
        # 실제 데이터베이스 작업 테스트
        db.store_cache_data("test", [{"value": 1}])
        result = db.get_cache_data("test")
        assert result == [{"value": 1}]
```

### 테스트용 Fixture

```python
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_duckdb():
    """테스트용 임시 DuckDB 파일"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.duckdb"
        yield str(db_path)
        # 정리는 자동

def test_with_temp_db(temp_duckdb):
    """임시 데이터베이스 파일로 테스트"""
    with MyDataManager(db_path=temp_duckdb) as db:
        # 작업 테스트
        pass
```

---

**버전:** 2.2.1
**모듈:** `mysingle.database.duckdb`
**라이선스:** MIT

# mysingle.database

데이터베이스 유틸리티

## 주요 기능

- MongoDB 연결 관리 (Beanie ODM)
- DuckDB 쿼리 실행
- Redis 캐싱

## 사용 예시

```python
from mysingle.database import init_mongodb, get_duckdb_connection

# MongoDB
await init_mongodb(
    connection_string="mongodb://localhost:27017",
    database_name="mydb"
)

# DuckDB
conn = get_duckdb_connection("data.duckdb")
result = conn.execute("SELECT * FROM table").fetchall()
```

## 설치

```bash
pip install mysingle[database]
```

## 의존성

- motor, beanie (기본 포함)
- duckdb
- redis

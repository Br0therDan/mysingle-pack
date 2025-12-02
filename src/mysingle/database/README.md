# MySingle Database Module

**Version:** 2.2.1 | **Module:** `mysingle.database`

High-performance database and caching utilities for MySingle Quant services.

---

## Overview

The `mysingle.database` module provides standardized database and caching management for MySingle Quant services:

- **DuckDB**: Analytical workloads and time-series data
- **Redis**: High-performance caching and data sharing across services

### Key Features

| Feature                   | Description                                      |
| ------------------------- | ------------------------------------------------ |
| **DuckDB Management**     | Base class for DuckDB connections and operations |
| **Redis Client Pool**     | Connection pooling and multi-DB support          |
| **Generic Redis Cache**   | Base cache class for service-specific caching    |
| **Built-in TTL Caching**  | Automatic expiration with configurable TTL       |
| **Context Management**    | Safe resource handling with context managers     |
| **Fallback Support**      | Automatic fallback for locked resources          |
| **Structured Logging**    | Production-ready logging with correlation IDs    |
| **JSON Serialization**    | Automatic serialization for Pydantic models      |
| **Multi-Service Sharing** | Share cache across microservices via Redis       |

---

## Installation

```bash
# Install with database extras (includes Redis)
pip install mysingle[database]

# Or with common dependencies
pip install mysingle[common-grpc]
```

---

## Quick Start

### DuckDB Usage

```python
from mysingle.database import BaseDuckDBManager

class MyDataManager(BaseDuckDBManager):
    """Custom DuckDB manager for your service"""

    def _create_tables(self) -> None:
        """Create service-specific tables"""
        self.duckdb_conn.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                event_type VARCHAR NOT NULL,
                event_data JSON,
                created_at TIMESTAMP NOT NULL
            )
        """)

# Usage with context manager (recommended)
with MyDataManager(db_path="data/analytics.duckdb") as db:
    db.duckdb_conn.execute("""
        INSERT INTO analytics (id, user_id, event_type, event_data, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, [record_id, user_id, "strategy_created", json.dumps(data), now])

    results = db.duckdb_conn.execute("SELECT * FROM analytics").fetchall()
```

### Redis Usage

#### Standard Redis Client

```python
from mysingle.database import get_redis_client

# Get Redis client for specific DB
async def cache_market_data():
    # Market data cache (DB 1)
    redis = await get_redis_client(db=1)
    if redis:
        await redis.set("ticker:AAPL:price", "150.0", ex=60)
        price = await redis.get("ticker:AAPL:price")

# User cache (DB 0 - default)
async def cache_user_data():
    redis = await get_redis_client(db=0)
    if redis:
        await redis.setex("user:123", 300, user_json)
```

#### Generic Redis Cache

```python
from mysingle.database import BaseRedisCache

class MarketDataCache(BaseRedisCache[dict]):
    """Market-specific cache"""

    def __init__(self):
        super().__init__(
            key_prefix="market",
            default_ttl=60,
            redis_db=1,  # Dedicated DB for market data
        )

# Usage
cache = MarketDataCache()
await cache.set("AAPL:price", {"price": 150.0, "volume": 1000000})
data = await cache.get("AAPL:price")
await cache.delete("AAPL:price")
```

#### Custom Cache Implementation

```python
from mysingle.database import BaseRedisCache
from pydantic import BaseModel

class Indicator(BaseModel):
    symbol: str
    indicator_type: str
    value: float
    timestamp: str

class IndicatorCache(BaseRedisCache[Indicator]):
    """Indicator-specific cache with type safety"""

    def __init__(self):
        super().__init__(
            key_prefix="indicator",
            default_ttl=120,
            redis_db=2,  # Dedicated DB for indicators
            use_json=True,  # JSON serialization
        )

    async def get_rsi(self, symbol: str) -> Optional[float]:
        """Get RSI indicator for symbol"""
        data = await self.get(f"RSI:{symbol}")
        return data["value"] if data else None

    async def set_rsi(self, symbol: str, value: float) -> bool:
        """Set RSI indicator"""
        indicator = {
            "symbol": symbol,
            "indicator_type": "RSI",
            "value": value,
            "timestamp": str(datetime.now(UTC))
        }
        return await self.set(f"RSI:{symbol}", indicator, ttl=60)

# Usage
cache = IndicatorCache()
await cache.set_rsi("AAPL", 65.5)
rsi_value = await cache.get_rsi("AAPL")
```

---

## Architecture

### DuckDB Architecture

```mermaid
flowchart TB
    subgraph Service["Service Layer"]
        A[Service Code] --> B[Custom DuckDB Manager]
    end

    subgraph BaseClass["BaseDuckDBManager"]
        B --> C[Connection Management]
        B --> D[Cache Operations]
        B --> E[Table Creation]
        B --> F[JSON Serialization]
    end

    subgraph Storage["Storage Layer"]
        C --> G[(DuckDB File)]
        C --> H[(In-Memory DB)]
        D --> I[Cache Table]
    end

    subgraph Logging["Structured Logging"]
        C --> J[get_logger]
        D --> J
        E --> J
        J --> K[Correlation ID]
        J --> L[Operation Context]
    end

    G -.lock error.-> H

    style B fill:#4CAF50,color:#fff
    style G fill:#2196F3,color:#fff
    style H fill:#FF9800,color:#fff
    style J fill:#9C27B0,color:#fff
```

### Redis Architecture

```mermaid
flowchart TB
    subgraph Services["Microservices"]
        S1[Market Data Service]
        S2[Indicator Service]
        S3[Strategy Service]
        S4[IAM Service]
    end

    subgraph ClientLayer["Redis Client Layer"]
        S1 --> RC1[Redis Client]
        S2 --> RC2[Redis Client]
        S3 --> RC3[Redis Client]
        S4 --> RC4[Redis Client]
    end

    subgraph CacheLayer["Cache Abstractions"]
        RC1 --> MC[MarketDataCache]
        RC2 --> IC[IndicatorCache]
        RC3 --> SC[StrategyCache]
        RC4 --> UC[UserCache]
    end

    subgraph RedisServer["Redis Server"]
        MC --> DB1[(DB 1: Market Data)]
        IC --> DB2[(DB 2: Indicators)]
        SC --> DB3[(DB 3: Strategies)]
        UC --> DB0[(DB 0: Users)]
    end

    subgraph ConnectionPool["Connection Pool"]
        DB0 -.-> CP[Shared Pool]
        DB1 -.-> CP
        DB2 -.-> CP
        DB3 -.-> CP
    end

    style MC fill:#FF5722,color:#fff
    style IC fill:#3F51B5,color:#fff
    style SC fill:#009688,color:#fff
    style UC fill:#9C27B0,color:#fff
    style CP fill:#FFC107,color:#000
```

---

## Core Components

### BaseDuckDBManager

Base class for all DuckDB operations with built-in caching and connection management.

#### Key Methods

| Method                      | Description                             |
| --------------------------- | --------------------------------------- |
| `connect()`                 | Establish database connection           |
| `close()`                   | Close connection and cleanup resources  |
| `store_cache_data()`        | Store data in cache with TTL            |
| `get_cache_data()`          | Retrieve cached data                    |
| `_create_tables()`          | Override to create service tables       |
| `_make_json_serializable()` | Convert objects to JSON-compatible form |

#### Properties

| Property      | Type                       | Description                |
| ------------- | -------------------------- | -------------------------- |
| `duckdb_conn` | `DuckDBPyConnection`       | Active database connection |
| `db_path`     | `str`                      | Path to database file      |
| `connection`  | `DuckDBPyConnection\|None` | Raw connection object      |

### Redis Components

#### RedisConfig

Configuration class for Redis connections with connection pooling support.

```python
from mysingle.database import RedisConfig

# From URL
config = RedisConfig.from_url("redis://:password@localhost:6379/1")

# Manual configuration
config = RedisConfig(
    host="redis-server.example.com",
    port=6379,
    db=1,
    password="secure-password",
    max_connections=50,
    socket_timeout=5.0,
)
```

#### RedisClientManager

Manages Redis connection pools and provides DB-specific clients.

```python
from mysingle.database import RedisClientManager, RedisConfig

config = RedisConfig(host="localhost", port=6379, password="secret")
manager = RedisClientManager(config)

# Get client for specific DB
async with manager:
    client = await manager.get_client(db=1)
    if client:
        await client.set("key", "value")

    # Health check
    is_healthy = await manager.health_check(db=1)
```

#### BaseRedisCache

Generic Redis cache base class for type-safe caching with TTL.

**Key Methods:**

| Method             | Description                |
| ------------------ | -------------------------- |
| `get(key)`         | Retrieve cached value      |
| `set(key, val)`    | Store value with TTL       |
| `delete(key)`      | Remove cached value        |
| `exists(key)`      | Check if key exists        |
| `expire(key, ttl)` | Update TTL                 |
| `clear_all()`      | Clear all keys with prefix |
| `health_check()`   | Check Redis connection     |

**Properties:**

| Property      | Type   | Description                       |
| ------------- | ------ | --------------------------------- |
| `key_prefix`  | `str`  | Cache key prefix (e.g., "market") |
| `default_ttl` | `int`  | Default TTL in seconds            |
| `redis_db`    | `int`  | Redis DB number (0-15)            |
| `use_json`    | `bool` | Use JSON (True) or Pickle (False) |

---

## Configuration

### Environment Variables

Configure Redis in your service's `.env` file:

```bash
# Redis Connection
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0              # Default DB for user cache
REDIS_PASSWORD=         # Optional: Set for AUTH

# Or use URL (takes precedence)
REDIS_URL=redis://localhost:6379/0

# User Cache Settings (for mysingle.auth)
USER_CACHE_KEY_PREFIX=user
USER_CACHE_TTL_SECONDS=300
```

### Service-Specific Redis Configuration

Each service can use dedicated Redis DBs for different purposes:

| Service             | DB  | Purpose          | Key Prefix  | TTL (sec) |
| ------------------- | --- | ---------------- | ----------- | --------- |
| IAM Service         | 0   | User cache       | `user`      | 300       |
| Market Data Service | 1   | Price data       | `market`    | 60        |
| Indicator Service   | 2   | Indicators       | `indicator` | 120       |
| Strategy Service    | 3   | Strategy cache   | `strategy`  | 600       |
| Backtest Service    | 4   | Backtest results | `backtest`  | 3600      |

### Database Path (DuckDB)

```python
# Production: File-based
db = MyDataManager(db_path="/data/analytics/prod.duckdb")

# Development: Local file
db = MyDataManager(db_path="./dev_data/analytics.duckdb")

# Testing: In-memory (explicit)
db = MyDataManager(db_path=":memory:")
```

```python
from datetime import UTC, datetime
import uuid
from mysingle.database import BaseDuckDBManager

class BacktestDataManager(BaseDuckDBManager):
    """DuckDB manager for backtest results"""

    def _create_tables(self) -> None:
        """Create backtest-specific tables"""
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

        # Indexes for common queries
        self.duckdb_conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_backtest_strategy
            ON backtest_results(strategy_id)
        """)

        self.duckdb_conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_backtest_user
            ON backtest_results(user_id)
        """)

    def store_backtest_result(self, result_data: dict) -> bool:
        """Store backtest result with automatic serialization"""
        try:
            # Convert Pydantic models to JSON-serializable format
            serializable_data = self._make_json_serializable(result_data)

            self.duckdb_conn.execute("""
                INSERT INTO backtest_results
                (id, strategy_id, user_id, start_date, end_date,
                 total_return, sharpe_ratio, max_drawdown, trades, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                str(uuid.uuid4()),
                serializable_data["strategy_id"],
                serializable_data["user_id"],
                serializable_data["start_date"],
                serializable_data["end_date"],
                serializable_data["total_return"],
                serializable_data["sharpe_ratio"],
                serializable_data["max_drawdown"],
                json.dumps(serializable_data["trades"]),
                datetime.now(UTC),
            ])
            return True
        except Exception as e:
            logger.error(f"Failed to store backtest result: {e}")
            return False

    def get_user_backtests(self, user_id: str) -> list[dict]:
        """Get all backtest results for a user"""
        result = self.duckdb_conn.execute("""
            SELECT * FROM backtest_results
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, [user_id]).fetchall()

        return [dict(row) for row in result]
```

### 2. Context Manager Pattern

```python
# Recommended: Automatic connection cleanup
with BacktestDataManager(db_path="data/backtests.duckdb") as db:
    # Connection is automatically established
    success = db.store_backtest_result(result_data)

    if success:
        results = db.get_user_backtests(user_id)
# Connection is automatically closed

# Manual management (if needed)
db = BacktestDataManager(db_path="data/backtests.duckdb")
db.connect()
try:
    # Your operations
    pass
finally:
    db.close()  # Always close to free resources
```

### 3. Built-in Caching

```python
# Store data in cache
data = [
    {"symbol": "AAPL", "price": 150.25, "volume": 1000000},
    {"symbol": "GOOGL", "price": 2800.50, "volume": 500000},
]

db.store_cache_data(
    cache_key="market_data:2024-12-02",
    data=data,
    table_name="market_cache"  # Optional: custom table name
)

# Retrieve cached data with TTL
cached_data = db.get_cache_data(
    cache_key="market_data:2024-12-02",
    table_name="market_cache",
    ttl_hours=24  # Data expires after 24 hours
)

if cached_data:
    print(f"Found {len(cached_data)} cached records")
else:
    print("Cache miss - fetch fresh data")
```

### 4. JSON Serialization

```python
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class TradeResult(BaseModel):
    symbol: str
    quantity: int
    price: Decimal
    executed_at: datetime

# Automatic serialization of complex types
trade = TradeResult(
    symbol="AAPL",
    quantity=100,
    price=Decimal("150.25"),
    executed_at=datetime.now(UTC)
)

# Convert to JSON-serializable format
serializable = db._make_json_serializable(trade)
# Result: {"symbol": "AAPL", "quantity": 100, "price": 150.25, "executed_at": "2024-12-02T10:30:45.123Z"}
```

---

## Configuration

### Database Path

```python
# Production: File-based
db = MyDataManager(db_path="/data/analytics/prod.duckdb")

# Development: Local file
db = MyDataManager(db_path="./dev_data/analytics.duckdb")

# Testing: In-memory (explicit)
db = MyDataManager(db_path=":memory:")

# Auto-fallback: File with in-memory fallback on lock
db = MyDataManager(db_path="/data/locked.duckdb")  # Falls back to :memory: if locked
```

### Environment Variables

```bash
# Service-specific database paths
export BACKTEST_DB_PATH="/data/backtests/prod.duckdb"
export ANALYTICS_DB_PATH="/data/analytics/prod.duckdb"

# Cache TTL configuration
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

## Advanced Usage

### Custom Cache Tables

```python
class MultiCacheManager(BaseDuckDBManager):
    """Manager with multiple cache tables"""

    def _create_tables(self) -> None:
        """Create multiple cache tables"""
        # Market data cache
        self._create_cache_table("market_data_cache")

        # Strategy cache
        self._create_cache_table("strategy_cache")

        # User preferences cache
        self._create_cache_table("user_prefs_cache")

    def cache_market_data(self, symbol: str, data: list[dict]) -> bool:
        """Cache market data by symbol"""
        return self.store_cache_data(
            cache_key=f"market:{symbol}",
            data=data,
            table_name="market_data_cache"
        )

    def get_market_data(self, symbol: str, ttl_hours: int = 1) -> list[dict] | None:
        """Get cached market data (short TTL for real-time data)"""
        return self.get_cache_data(
            cache_key=f"market:{symbol}",
            table_name="market_data_cache",
            ttl_hours=ttl_hours
        )
```

### Complex Queries

```python
class AnalyticsManager(BaseDuckDBManager):
    """Advanced analytics queries"""

    def get_top_strategies(self, limit: int = 10) -> list[dict]:
        """Get top performing strategies"""
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

    def get_user_statistics(self, user_id: str) -> dict:
        """Get aggregated user statistics"""
        result = self.duckdb_conn.execute("""
            SELECT
                COUNT(*) as total_backtests,
                AVG(total_return) as avg_return,
                MAX(total_return) as best_return,
                MIN(total_return) as worst_return,
                AVG(sharpe_ratio) as avg_sharpe
            FROM backtest_results
            WHERE user_id = ?
        """, [user_id]).fetchone()

        if result:
            return {
                "total_backtests": result[0],
                "avg_return": result[1],
                "best_return": result[2],
                "worst_return": result[3],
                "avg_sharpe": result[4],
            }
        return {}
```

### Batch Operations

```python
def batch_insert_trades(self, trades: list[dict]) -> int:
    """Insert multiple trades efficiently"""
    try:
        # Prepare data
        serialized_trades = [
            self._make_json_serializable(trade) for trade in trades
        ]

        # Batch insert
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
        logger.error(f"Batch insert failed: {e}")
        return 0
```

---

## Error Handling

### Connection Failures

```python
try:
    db = MyDataManager(db_path="/locked/database.duckdb")
    db.connect()
except Exception as e:
    logger.error(f"Failed to connect: {e}")
    # Fallback to in-memory database
    db = MyDataManager(db_path=":memory:")
    db.connect()
```

### Automatic Fallback

```python
# BaseDuckDBManager automatically falls back to in-memory on lock errors
db = MyDataManager(db_path="/data/database.duckdb")
db.connect()
# If file is locked, automatically uses `:memory:` instead
```

### Cache Errors

```python
# store_cache_data returns bool for success/failure
success = db.store_cache_data(cache_key, data)
if not success:
    logger.warning("Cache write failed - continuing without cache")

# get_cache_data returns None on error or cache miss
cached_data = db.get_cache_data(cache_key)
if cached_data is None:
    # Fetch fresh data
    fresh_data = fetch_from_api()
    db.store_cache_data(cache_key, fresh_data)
    cached_data = fresh_data
```

---

## Structured Logging

All database operations emit structured logs following the MySingle logging guide.

### Log Examples

```json
// Connection success
{
  "timestamp": "2024-12-02T10:30:45.123Z",
  "level": "info",
  "event": "DuckDB connected successfully",
  "db_path": "/data/analytics.duckdb",
  "status": "success",
  "operation": "connect"
}

// Cache hit
{
  "timestamp": "2024-12-02T10:31:12.456Z",
  "level": "debug",
  "event": "Cache data retrieved successfully",
  "cache_key": "market_data:2024-12-02",
  "table_name": "market_cache",
  "data_count": 150,
  "ttl_hours": 24,
  "operation": "get_cache"
}

// Lock error with fallback
{
  "timestamp": "2024-12-02T10:32:00.789Z",
  "level": "warning",
  "event": "Falling back to in-memory database",
  "reason": "file_locked",
  "original_db_path": "/data/locked.duckdb"
}

// Cache write failure
{
  "timestamp": "2024-12-02T10:33:15.321Z",
  "level": "error",
  "event": "Failed to store cache data",
  "cache_key": "strategy_results:123",
  "table_name": "cache_data",
  "error": "Database is locked",
  "error_type": "OperationalError"
}
```

---

## Best Practices

### DuckDB Best Practices

#### ✅ DO

```python
# Use context managers for automatic cleanup
with MyDataManager(db_path="data.duckdb") as db:
    db.store_cache_data(cache_key, data)

# Check return values
success = db.store_cache_data(cache_key, data)
if not success:
    logger.warning("Cache write failed")

# Use structured caching with TTL
cached = db.get_cache_data(cache_key, ttl_hours=24)
if cached is None:
    cached = fetch_fresh_data()
    db.store_cache_data(cache_key, cached)

# Serialize complex objects before storage
serializable = db._make_json_serializable(pydantic_model)

# Create indexes for frequently queried columns
self.duckdb_conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_user_id ON table(user_id)
""")
```

#### ❌ DON'T

```python
# Don't forget to close connections
db = MyDataManager(db_path="data.duckdb")
db.connect()
# ... operations ...
# Missing db.close() - resource leak!

# Don't ignore cache failures
db.store_cache_data(cache_key, data)  # Ignoring return value

# Don't store non-serializable objects directly
db.duckdb_conn.execute("INSERT ...", [datetime_object])  # May fail

# Don't create tables in every method
def my_method(self):
    self.duckdb_conn.execute("CREATE TABLE ...")  # Should be in _create_tables()

# Don't use hardcoded paths
db = MyDataManager(db_path="/hardcoded/path.duckdb")  # Use config/env vars
```

### Redis Best Practices

#### ✅ DO

```python
# Use dedicated DBs for different service types
market_cache = MarketDataCache()  # Uses DB 1
indicator_cache = IndicatorCache()  # Uses DB 2

# Check Redis availability before operations
redis = await get_redis_client(db=1)
if redis:
    await redis.set("key", "value")
else:
    logger.warning("Redis unavailable - using fallback")

# Use TTL for all cached data
await cache.set("key", data, ttl=300)  # 5 minutes

# Use clear key naming conventions
await redis.set(f"{service}:{entity}:{id}", value)
# Example: "market:ticker:AAPL", "indicator:RSI:GOOGL"

# Handle connection errors gracefully
try:
    result = await cache.get("key")
except Exception as e:
    logger.error(f"Redis error: {e}")
    result = None  # Fallback to direct fetch

# Use pipelines for batch operations
pipe = redis.pipeline()
for item in items:
    pipe.set(f"item:{item.id}", item.value)
await pipe.execute()

# Close connections properly
async with get_redis_client(db=1) as redis:
    await redis.set("key", "value")
# Auto-closed
```

#### ❌ DON'T

```python
# Don't use DB 0 for service-specific data (reserved for IAM)
redis = await get_redis_client(db=0)  # Only for user auth cache!

# Don't forget TTL on temporary data
await redis.set("temp_data", value)  # Will never expire!

# Don't ignore None returns (Redis unavailable)
redis = await get_redis_client(db=1)
await redis.set("key", "value")  # Crashes if redis is None!

# Don't use generic keys without prefixes
await redis.set("data", value)  # Collision risk!

# Don't serialize manually (use BaseRedisCache)
import json
await redis.set("key", json.dumps(data))  # Use cache.set() instead

# Don't share Redis client instances across async contexts
self.redis = await get_redis_client(db=1)  # Risk of connection issues
# Always call get_redis_client() in each async function

# Don't perform individual operations in loops
for item in items:
    await redis.set(f"item:{item.id}", item.value)  # Use pipeline!
```

#### Key Naming Conventions

```python
# Service-level pattern: {service}:{entity}:{identifier}
"market:ticker:AAPL"
"market:ohlcv:GOOGL:1h"
"indicator:RSI:AAPL:14"
"strategy:momentum:result:123"

# User-specific pattern: {service}:user:{user_id}:{entity}
"iam:user:123:profile"
"market:user:456:watchlist"

# Temporary data: {service}:temp:{identifier}
"market:temp:snapshot:20241202"
```

#### TTL Strategy

```python
# Real-time data (30s - 1min)
await cache.set("market:ticker:AAPL", price_data, ttl=60)

# Calculated indicators (2-5min)
await cache.set("indicator:RSI:AAPL", rsi_data, ttl=300)

# Strategy results (5-10min)
await cache.set("strategy:result:123", result, ttl=600)

# User sessions (30min - 1hr)
await cache.set("iam:user:123:session", session, ttl=3600)

# Configuration (1-24hrs)
await cache.set("config:strategy:456", config, ttl=86400)
```

### Connection Management

```python
# Pattern 1: Context manager (recommended)
with MyDataManager(db_path=db_path) as db:
    results = db.query_data()
    # Automatically closed

# Pattern 2: Manual with try-finally
db = MyDataManager(db_path=db_path)
db.connect()
try:
    results = db.query_data()
finally:
    db.close()  # Always executed

# Pattern 3: Long-lived connection (service startup)
class MyService:
    def __init__(self):
        self.db = MyDataManager(db_path=db_path)
        self.db.connect()

    def shutdown(self):
        self.db.close()
```

---

## Testing

### Mock DuckDB Manager

```python
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_duckdb_manager():
    """Mock DuckDB manager for testing"""
    manager = MagicMock(spec=BaseDuckDBManager)
    manager.store_cache_data.return_value = True
    manager.get_cache_data.return_value = [{"symbol": "AAPL", "price": 150.0}]
    return manager

def test_cache_operations(mock_duckdb_manager):
    """Test cache operations with mock"""
    # Store data
    success = mock_duckdb_manager.store_cache_data("test_key", [{"data": "value"}])
    assert success is True

    # Retrieve data
    cached = mock_duckdb_manager.get_cache_data("test_key")
    assert cached is not None
    assert len(cached) == 1
```

### In-Memory Testing

```python
def test_with_real_duckdb():
    """Test with real in-memory DuckDB"""
    with MyDataManager(db_path=":memory:") as db:
        # Test actual database operations
        db.store_cache_data("test", [{"value": 1}])
        result = db.get_cache_data("test")
        assert result == [{"value": 1}]
```

### Fixture for Tests

```python
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_duckdb():
    """Temporary DuckDB file for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.duckdb"
        yield str(db_path)
        # Cleanup is automatic

def test_with_temp_db(temp_duckdb):
    """Test with temporary database file"""
    with MyDataManager(db_path=temp_duckdb) as db:
        # Test operations
        pass
```

---

## Performance Tips

### 1. Use Batch Operations

```python
# Bad: Multiple individual inserts
for trade in trades:
    db.duckdb_conn.execute("INSERT ...", [trade])

# Good: Batch insert
db.duckdb_conn.executemany("INSERT ...", trades)
```

### 2. Create Appropriate Indexes

```python
# Index frequently queried columns
self.duckdb_conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_user_date
    ON analytics(user_id, created_at)
""")
```

### 3. Use Cache Effectively

```python
# Short TTL for real-time data
market_data = db.get_cache_data(f"market:{symbol}", ttl_hours=1)

# Long TTL for static data
strategy_config = db.get_cache_data(f"config:{id}", ttl_hours=168)  # 1 week
```

### 4. Connection Pooling

```python
# Reuse connections in long-lived services
class AnalyticsService:
    def __init__(self):
        self.db = AnalyticsManager(db_path=config.DB_PATH)
        self.db.connect()

    async def on_shutdown(self):
        self.db.close()
```

---

## Troubleshooting

### DuckDB Issues

#### Issue: Database Locked

**Symptom:** `database is locked` error

**Solution:** BaseDuckDBManager automatically falls back to in-memory database
```python
# Automatic fallback is logged
# WARNING: Falling back to in-memory database (reason: file_locked)
```

#### Issue: Cache Not Working

**Symptom:** `get_cache_data()` always returns None

**Possible Causes:**
1. TTL expired - increase `ttl_hours`
2. Table not created - check `_create_cache_table()` is called
3. Connection issue - check structured logs

**Debug:**
```python
# Enable debug logging
import logging
logging.getLogger("mysingle.database").setLevel(logging.DEBUG)

# Check cache table exists
result = db.duckdb_conn.execute("""
    SELECT name FROM sqlite_master WHERE type='table'
""").fetchall()
print("Tables:", result)
```

#### Issue: JSON Serialization Error

**Symptom:** `TypeError: Object of type X is not JSON serializable`

**Solution:** Use `_make_json_serializable()`
```python
# Before
data = {"datetime": datetime.now(), "decimal": Decimal("10.5")}

# After
serializable = db._make_json_serializable(data)
# Result: {"datetime": "2024-12-02T10:30:45.123Z", "decimal": 10.5}
```

### Redis Issues

#### Issue: Redis Returns None

**Symptom:** `get_redis_client()` returns None

**Possible Causes:**
1. Redis server not running
2. Connection refused (wrong host/port)
3. Authentication failed (wrong password)
4. Network timeout

**Debug:**
```python
# Check Redis connection manually
from mysingle.database import get_redis_client

redis = await get_redis_client(db=1)
if redis is None:
    print("Redis unavailable - check REDIS_HOST, REDIS_PORT, REDIS_PASSWORD")
else:
    # Test ping
    try:
        await redis.ping()
        print("Redis connection OK")
    except Exception as e:
        print(f"Redis ping failed: {e}")
```

**Solution:**
```python
# Verify environment variables
echo $REDIS_HOST      # Should be localhost or redis service
echo $REDIS_PORT      # Should be 6379 (default)
echo $REDIS_PASSWORD  # Check if required

# Test Redis connection
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping
```

#### Issue: Cache Always Returns None

**Symptom:** `cache.get()` always returns None even after `cache.set()`

**Possible Causes:**
1. Wrong Redis DB - check `redis_db` parameter
2. TTL too short - data expired immediately
3. Serialization error - check logs
4. Key mismatch - verify key prefix

**Debug:**
```python
# Check what's in Redis
redis = await get_redis_client(db=1)
keys = await redis.keys("*")
print(f"Keys in DB 1: {keys}")

# Check specific key
value = await redis.get("market:ticker:AAPL")
print(f"Raw value: {value}")

# Check TTL
ttl = await redis.ttl("market:ticker:AAPL")
print(f"TTL remaining: {ttl} seconds")
```

#### Issue: Connection Pool Exhausted

**Symptom:** `Too many open connections` or timeouts

**Cause:** Not properly closing Redis connections

**Solution:**
```python
# Bad: Creates new connection each time
async def bad_pattern():
    redis = await get_redis_client(db=1)
    await redis.set("key", "value")
    # Connection not closed!

# Good: Reuses connection pool
async def good_pattern():
    redis = await get_redis_client(db=1)
    if redis:
        await redis.set("key", "value")
        # Connection returned to pool automatically

# Best: Use BaseRedisCache
cache = MarketDataCache()
await cache.set("ticker:AAPL", data)  # Handles connection internally
```

#### Issue: Data Not Shared Between Services

**Symptom:** Service A writes data, Service B can't read it

**Possible Causes:**
1. Different Redis DBs - check `redis_db` parameter
2. Different key prefixes - verify key names
3. Different Redis instances - check REDIS_HOST

**Debug:**
```python
# Service A (Market Data)
redis = await get_redis_client(db=1)  # Must use same DB
await redis.set("market:ticker:AAPL", "150.25")

# Service B (Indicator)
redis = await get_redis_client(db=1)  # Must match DB 1
value = await redis.get("market:ticker:AAPL")  # Must match exact key
```

**Solution:** Use standardized DB allocation (see Configuration table)

#### Issue: Serialization Error

**Symptom:** `pickle.PicklingError` or `json.JSONDecodeError`

**Solution:**
```python
# For JSON-serializable data, use use_json=True
class MyCache(BaseRedisCache[dict]):
    def __init__(self):
        super().__init__(
            key_prefix="my_data",
            use_json=True,  # Use JSON instead of pickle
        )

# For complex objects, ensure they're serializable
from pydantic import BaseModel

class MarketData(BaseModel):
    symbol: str
    price: float

# BaseRedisCache handles Pydantic serialization automatically
await cache.set("AAPL", MarketData(symbol="AAPL", price=150.25))
```

#### Issue: Memory Usage Too High

**Symptom:** Redis memory grows indefinitely

**Cause:** Missing TTL on cached data

**Solution:**
```python
# Always set TTL
await cache.set("key", data, ttl=300)  # 5 minutes

# For existing keys without TTL
await redis.expire("key", 300)

# Check current TTL
ttl = await redis.ttl("key")
if ttl == -1:  # No TTL set
    await redis.expire("key", 3600)

# Monitor memory usage
info = await redis.info("memory")
print(f"Used memory: {info['used_memory_human']}")
```

---

## API Reference

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

    def _create_tables(self) -> None: ...  # Abstract - must override
    def _create_cache_table(self, table_name: str) -> None: ...
    def _make_json_serializable(self, obj: Any) -> Any: ...
    def _ensure_connected(self) -> None: ...

    @property
    def duckdb_conn(self) -> duckdb.DuckDBPyConnection: ...
```

### RedisConfig

```python
@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None
    decode_responses: bool = True
    max_connections: int = 50
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    retry_on_timeout: bool = True

    @classmethod
    def from_url(cls, redis_url: str, db: int = 0) -> "RedisConfig": ...

    def to_connection_kwargs(self) -> dict[str, Any]: ...
```

### RedisClientManager

```python
class RedisClientManager:
    def __init__(self, config: RedisConfig | None = None): ...

    async def get_client(
        self,
        db: int | None = None
    ) -> redis.Redis | None: ...

    async def close_all(self) -> None: ...

    async def health_check(self, db: int = 0) -> bool: ...

# Global instance
async def get_redis_client(db: int = 0) -> redis.Redis | None: ...
```

### BaseRedisCache[T]

```python
class BaseRedisCache(Generic[T]):
    def __init__(
        self,
        key_prefix: str,
        default_ttl: int = 300,
        redis_db: int = 0,
        use_json: bool = False,
    ): ...

    async def get(self, key: str) -> T | None: ...

    async def set(
        self,
        key: str,
        value: T,
        ttl: int | None = None
    ) -> bool: ...

    async def delete(self, key: str) -> bool: ...

    async def exists(self, key: str) -> bool: ...

    async def expire(self, key: str, ttl: int) -> bool: ...

    async def clear_all(self, pattern: str = "*") -> int: ...

    def _serialize(self, value: T) -> str | bytes: ...
    def _deserialize(self, data: str | bytes) -> T | None: ...
```

---

## Migration Guide

### DuckDB Migration

#### From Custom DuckDB Implementation

```python
# Old: Custom implementation
import duckdb
conn = duckdb.connect("data.duckdb")
try:
    conn.execute("CREATE TABLE ...")
finally:
    conn.close()

# New: BaseDuckDBManager
class MyManager(BaseDuckDBManager):
    def _create_tables(self):
        self.duckdb_conn.execute("CREATE TABLE ...")

with MyManager("data.duckdb") as db:
    # Automatic connection management
    pass
```

#### Adding Caching

```python
# Before: No caching
data = fetch_expensive_data()

# After: With caching
cached = db.get_cache_data("expensive_data", ttl_hours=24)
if cached is None:
    cached = fetch_expensive_data()
    db.store_cache_data("expensive_data", cached)
data = cached
```

### Redis Migration

#### From Direct Redis Usage

```python
# Old: Direct redis client management
import redis.asyncio as redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)

try:
    await redis_client.set("key", json.dumps(data))
    raw_value = await redis_client.get("key")
    data = json.loads(raw_value) if raw_value else None
finally:
    await redis_client.close()

# New: Standardized client manager
from mysingle.database import get_redis_client

redis = await get_redis_client(db=0)
if redis:
    await redis.set("key", json.dumps(data))
    raw_value = await redis.get("key")
    data = json.loads(raw_value) if raw_value else None
# Connection automatically managed
```

#### From Custom Cache to BaseRedisCache

```python
# Old: Custom cache implementation (from auth/cache.py)
class RedisUserCache:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.key_prefix = settings.USER_CACHE_KEY_PREFIX
        self.ttl = settings.USER_CACHE_TTL_SECONDS
        self._client: redis.Redis | None = None

    async def _get_client(self) -> redis.Redis | None:
        if self._client is None:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                await self._client.ping()
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                return None
        return self._client

    async def get_user(self, user_id: str) -> dict | None:
        client = await self._get_client()
        if not client:
            return None

        key = f"{self.key_prefix}{user_id}"
        cached = await client.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def set_user(self, user_id: str, user_data: dict) -> bool:
        client = await self._get_client()
        if not client:
            return False

        key = f"{self.key_prefix}{user_id}"
        await client.setex(key, self.ttl, json.dumps(user_data))
        return True

# New: Using BaseRedisCache
from mysingle.database import BaseRedisCache

class RedisUserCache(BaseRedisCache[dict]):
    """User cache using standard Redis infrastructure"""

    def __init__(self):
        super().__init__(
            key_prefix=settings.USER_CACHE_KEY_PREFIX,
            default_ttl=settings.USER_CACHE_TTL_SECONDS,
            redis_db=0,  # IAM service uses DB 0
            use_json=True,
        )

    async def get_user(self, user_id: str) -> dict | None:
        """Get cached user data"""
        return await self.get(user_id)

    async def set_user(self, user_id: str, user_data: dict) -> bool:
        """Cache user data"""
        return await self.set(user_id, user_data)

# Benefits:
# - No manual connection management
# - Automatic serialization
# - Built-in error handling
# - Connection pooling
# - Health checks
# - Consistent logging
```

#### From auth/cache.py Migration (Real Example)

```python
# Before (v2.1.0): 60+ lines with manual Redis management
class RedisUserCache:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.key_prefix = settings.USER_CACHE_KEY_PREFIX
        # ... 15+ lines of initialization

    async def _get_client(self):
        # ... 20+ lines of connection logic
        pass

    async def get_user(self, user_id: str):
        client = await self._get_client()
        if not client:
            return None
        # ... 10+ lines of get logic

    async def set_user(self, user_id: str, user_data: dict):
        # ... 15+ lines of set logic
        pass

# After (v2.2.0): 20 lines using standard infrastructure
from mysingle.database import get_redis_client

class RedisUserCache:
    """User cache using standard Redis infrastructure"""

    def __init__(self):
        self.key_prefix = settings.USER_CACHE_KEY_PREFIX
        self.ttl = settings.USER_CACHE_TTL_SECONDS

    async def get_user(self, user_id: str) -> dict | None:
        redis = await get_redis_client(db=0)
        if not redis:
            return None

        key = f"{self.key_prefix}{user_id}"
        cached = await redis.get(key)
        return json.loads(cached) if cached else None

    async def set_user(self, user_id: str, user_data: dict) -> bool:
        redis = await get_redis_client(db=0)
        if not redis:
            return False

        key = f"{self.key_prefix}{user_id}"
        await redis.setex(key, self.ttl, json.dumps(user_data))
        return True

# Code reduction: 60+ lines → 20 lines (67% reduction)
# Benefits: Connection pooling, health checks, automatic error handling
```

#### Multi-DB Migration

```python
# Old: Single Redis instance for everything
redis_client = redis.Redis(host="localhost", port=6379, db=0)

# All data in DB 0 - potential key collisions!
await redis_client.set("user:123", user_data)
await redis_client.set("market:AAPL", market_data)
await redis_client.set("indicator:RSI", indicator_data)

# New: Service-specific databases
from mysingle.database import get_redis_client

# IAM Service - DB 0
iam_redis = await get_redis_client(db=0)
await iam_redis.set("user:123", user_data)

# Market Data Service - DB 1
market_redis = await get_redis_client(db=1)
await market_redis.set("ticker:AAPL", market_data)

# Indicator Service - DB 2
indicator_redis = await get_redis_client(db=2)
await indicator_redis.set("RSI:AAPL", indicator_data)

# Benefits:
# - No key collisions
# - Easier to flush service-specific data
# - Better isolation and debugging
# - Independent TTL policies per service
```

---

## Related Documentation

- [Structured Logging Guide](../../docs/core/STRUCTURED_LOGGING_GUIDE.md) - Logging integration
- [Core Module README](../core/README.md) - Core utilities
- [DuckDB Documentation](https://duckdb.org/docs/) - DuckDB reference

---

**Version:** 2.2.1
**Module:** `mysingle.database`
**License:** MIT

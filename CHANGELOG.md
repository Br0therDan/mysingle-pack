# Changelog - mysingle.dsl

## [2.2.1] - 2025-01-XX

### Added - Redis Cache Standardization

#### Platform-Wide Redis DB Allocation
- **REDIS_DB_* Constants**: Added 16 constants (DB 0-15) to `CommonSettings`
  - `REDIS_DB_USER` (0): User authentication cache (IAM)
  - `REDIS_DB_GRPC` (1): gRPC response cache (all services)
  - `REDIS_DB_RATE_LIMIT` (2): Rate limiting (Kong/Gateway)
  - `REDIS_DB_SESSION` (3): Session storage (IAM)
  - `REDIS_DB_DSL_BYTECODE` (4): DSL bytecode cache (Strategy)
  - `REDIS_DB_MARKET_DATA` (5): Market data cache (Market Data)
  - `REDIS_DB_BACKTEST` (6): Backtest cache (Backtest)
  - `REDIS_DB_INDICATOR` (7): Indicator cache (Indicator)
  - `REDIS_DB_STRATEGY` (8): Strategy cache (Strategy)
  - `REDIS_DB_NOTIFICATION` (9): Notification queue (Notification)
  - `REDIS_DB_CELERY_BROKER` (10): Celery task broker (Backtest/Celery)
  - `REDIS_DB_CELERY_RESULT` (11): Celery result backend (Backtest/Celery)
  - `REDIS_DB_ML_MODEL` (12): ML model cache (ML)
  - `REDIS_DB_GENAI` (13): GenAI response cache (GenAI)
  - `REDIS_DB_SUBSCRIPTION` (14): Subscription cache (Subscription)
  - `REDIS_DB_RESERVED` (15): Reserved for platform use

#### Redis Configuration Validation
- Added `@model_validator` in `CommonSettings` to validate Redis configuration
- Validates `REDIS_HOST` and `REDIS_PORT` are set together
- Validates all `REDIS_DB_*` values are in range 0-15
- Detects duplicate DB allocations across services

#### Cache Factory Functions
- **`create_user_cache()`**: User authentication cache (DB 0)
- **`create_grpc_cache(service_name)`**: gRPC response cache (DB 1)
- **`create_service_cache(service_name, db_constant)`**: Generic service cache with custom DB

#### BaseRedisCache API Changes
- **`redis_db` → `_redis_db`**: Made internal (breaking change)
- Added `@property redis_db` for read-only access
- Enhanced docstring with usage guidelines and warnings
- Added warning log for invalid DB numbers

### Changed - Breaking Changes

#### REDIS_URL Now Computed Field
- **`REDIS_URL`**: Changed from field to `@computed_field` (read-only)
- Auto-constructed from `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- Prevents configuration ambiguity (URL override no longer allowed)

#### GrpcCache Standardization
- **`GrpcCache.__init__`**: Removed `redis_db` parameter
- Now always uses `settings.REDIS_DB_GRPC` (DB 1)
- `from_settings()` ignores `redis_db` parameter with warning
- Ensures platform-wide consistency for gRPC caching

#### RedisUserCache Standardization
- **`RedisUserCache.__init__`**: Removed `redis_db` parameter
- Now always uses `settings.REDIS_DB_USER` (DB 0)
- **`HybridUserCache.__init__`**: Removed `redis_db` parameter
- **`get_user_cache()`**: No longer accepts DB override

### Documentation

#### Updated Files
- `src/mysingle/database/README.md`:
  - Added "Redis DB Allocation Standards" section
  - Added "Cache Factory Functions" section
  - Updated migration examples for v2.2.1
- `.github/copilot-instructions.md`:
  - Updated "Redis Cache Standards" with factory functions
  - Added v2.2.1 implementation examples
- `services/backtest-service/.github/copilot-instructions.md`:
  - Synced Redis DB allocation table
  - Updated usage guidelines

### Migration Guide

#### From v2.2.0 to v2.2.1

**Before (deprecated):**
```python
from mysingle.database import BaseRedisCache

class MyCache(BaseRedisCache):
    def __init__(self):
        super().__init__(
            key_prefix="myservice",
            default_ttl=3600,
            redis_db=5,  # ❌ No longer allowed
        )
```

**After (recommended):**
```python
from mysingle.database import create_service_cache
from mysingle.core.config import settings

# Option 1: Factory function (recommended)
cache = create_service_cache("myservice", settings.REDIS_DB_MYSERVICE)

# Option 2: Custom class (if custom logic needed)
from mysingle.database import BaseRedisCache

class MyCache(BaseRedisCache):
    def __init__(self):
        super().__init__(
            key_prefix="myservice",
            default_ttl=3600,
            # Note: redis_db is now internal (_redis_db)
            # DB selection via factory or get_redis_client(db=N)
        )
```

### Technical Details

#### Modified Files
- `mysingle/core/config.py`:
  - Added all `REDIS_DB_*` constants with inline comments
  - Changed `REDIS_URL` to `@computed_field`
  - Added `_validate_redis_configuration` model validator
- `mysingle/database/redis.py`:
  - Simplified `_get_redis_config_from_settings()` to use HOST/PORT/PASSWORD
- `mysingle/database/redis_cache.py`:
  - Changed `redis_db` to `_redis_db` (internal)
  - Added `@property redis_db` for read-only access
- `mysingle/database/cache_factory.py` (NEW):
  - Created factory functions for standardized cache creation
- `mysingle/database/__init__.py`:
  - Exported factory functions
- `mysingle/grpc/cache.py`:
  - Removed `redis_db` parameter, fixed to `settings.REDIS_DB_GRPC`
- `mysingle/auth/cache.py`:
  - Removed `redis_db` parameter from `RedisUserCache`, `HybridUserCache`, `get_user_cache()`

#### Test Coverage
- `tests/core/test_config.py`:
  - Updated `test_redis_configuration` for computed field
  - Added `test_redis_db_allocation`
  - Added `test_redis_validation`
- All auth tests (28 tests) passing
- All config tests (9 tests) passing

### Benefits

- ✅ **Consistency**: Platform-wide DB allocation prevents conflicts
- ✅ **Safety**: Prevents accidental DB number overrides
- ✅ **Clarity**: Factory functions make cache creation explicit
- ✅ **Validation**: Auto-validation of Redis configuration at startup
- ✅ **Documentation**: Centralized DB allocation reference

---

## [2.6.5] - 2025-12-10

### Fixed
- **DSL Executor**: DataFrame columns are now auto-injected as namespace variables
  - OHLCV columns (`open`, `high`, `low`, `close`, `volume`) are now directly accessible
  - Previously: DSL code had to use `data['close']` or `data.close`
  - Now: Can use `close`, `high`, `low` directly in DSL code
  - Improves readability and aligns with TradingView Pine Script syntax
  - **Breaking Change**: None (backward compatible - `data.close` still works)

### Impact
- **Backtest Service**: Fixes `name 'close' is not defined` execution errors
- **Strategy Templates**: All `.msl` templates can now use direct OHLCV variable access
- **Performance**: No performance impact (same namespace injection mechanism)

### Example
```python
# Before (still works)
fast_ema = EMA(data['close'], 9)

# After (now also works)
fast_ema = EMA(close, 9)
```

### Technical Details
- Modified: `src/mysingle/dsl/executor.py::_build_namespace()`
- Added loop to inject all DataFrame columns as individual variables
- Tested with 34 DSL test cases - all passing

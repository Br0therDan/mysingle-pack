# DSL Cache Migration Guide

**Version:** 1.3.0
**Date:** 2025-12-08

## Overview

DSL 캐시가 `mysingle.database.BaseRedisCache`를 사용하도록 리팩토링되었습니다. 이는 표준화된 캐싱 인터페이스, 향상된 연결 관리, 그리고 일관된 설정 관리를 제공합니다.

---

## What Changed

### Before (v1.2.0)

```python
from mysingle.dsl.cache import RedisDSLCache, DSLCacheManager

# Manual Redis DB configuration
cache = RedisDSLCache(redis_db=5)
manager = DSLCacheManager(backend=cache)
```

### After (v1.3.0)

```python
from mysingle.dsl.cache import DSLBytecodeCache, DSLCacheManager

# Uses settings from config (REDIS_DB_DSL=5)
cache = DSLBytecodeCache()
manager = DSLCacheManager(backend=cache)
```

---

## Key Changes

### 1. New Class Name

- **Old:** `RedisDSLCache`
- **New:** `DSLBytecodeCache` (inherits from `BaseRedisCache`)
- **Alias:** `RedisDSLCache` still available for backward compatibility

### 2. Configuration via Settings

**Environment Variables (`.env`):**

```bash
# Redis DB allocation
REDIS_DB_DSL=5  # DSL bytecode cache (default)

# DSL cache settings
DSL_CACHE_TTL_SECONDS=3600           # Default TTL (1 hour)
DSL_CACHE_KEY_PREFIX=dsl:bytecode    # Key prefix
DSL_CACHE_WARMING_TTL_SECONDS=86400  # Warming TTL (24 hours)
```

**Code:**

```python
from mysingle.core.config import get_settings

settings = get_settings()
print(settings.REDIS_DB_DSL)              # 5
print(settings.DSL_CACHE_TTL_SECONDS)     # 3600
print(settings.DSL_CACHE_KEY_PREFIX)      # "dsl:bytecode"
```

### 3. Standardized Interface

`DSLBytecodeCache` now uses `BaseRedisCache` which provides:

- ✅ Automatic connection pooling
- ✅ Graceful Redis unavailability handling
- ✅ Consistent TTL management
- ✅ Health check support
- ✅ Structured logging

---

## Migration Steps

### Step 1: Update Imports

**Before:**
```python
from mysingle.dsl.cache import RedisDSLCache
```

**After (recommended):**
```python
from mysingle.dsl.cache import DSLBytecodeCache
```

**Or (backward compatible):**
```python
from mysingle.dsl.cache import RedisDSLCache  # Still works, but deprecated
```

### Step 2: Remove redis_db Parameter

**Before:**
```python
cache = RedisDSLCache(redis_db=5)
```

**After:**
```python
cache = DSLBytecodeCache()  # Uses REDIS_DB_DSL from settings
```

### Step 3: Update Cache Key Format

**Before:**
```python
# Keys included full prefix
cache_key = "dsl:bytecode:strategy:hash123"
await cache.set(cache_key, bytecode)
```

**After:**
```python
# Backend adds prefix automatically
cache_key = "strategy:hash123"  # Becomes "dsl:bytecode:strategy:hash123"
await cache.set(cache_key, bytecode)
```

### Step 4: Environment Variables

Add to your service's `.env`:

```bash
# DSL Cache Configuration
REDIS_DB_DSL=5
DSL_CACHE_TTL_SECONDS=3600
DSL_CACHE_KEY_PREFIX=dsl:bytecode
DSL_CACHE_WARMING_TTL_SECONDS=86400
```

---

## Service-Specific Examples

### Strategy Service

**Before:**
```python
from mysingle.dsl.cache import RedisDSLCache, DSLCacheManager

cache_backend = RedisDSLCache(redis_db=3)  # Custom DB
manager = DSLCacheManager(cache_backend)
```

**After:**
```python
from mysingle.dsl.cache import DSLBytecodeCache, DSLCacheManager

# Uses REDIS_DB_DSL from settings (no hardcoded DB)
cache_backend = DSLBytecodeCache()
manager = DSLCacheManager(cache_backend)
```

**`.env`:**
```bash
REDIS_DB_DSL=5  # Standardized DSL cache DB
```

### Backtest Service

**Before:**
```python
cache_backend = RedisDSLCache(redis_db=4)
```

**After:**
```python
cache_backend = DSLBytecodeCache()  # Uses shared DSL cache
```

**Note:** All services now use the same Redis DB (5) for DSL bytecode cache, avoiding unnecessary DB fragmentation.

---

## Backward Compatibility

### Alias Support

```python
# Both work identically
from mysingle.dsl.cache import DSLBytecodeCache
from mysingle.dsl.cache import RedisDSLCache  # Alias to DSLBytecodeCache

cache1 = DSLBytecodeCache()
cache2 = RedisDSLCache()  # Same class
```

### Deprecation Timeline

- **v1.3.0:** `RedisDSLCache` available as alias
- **v1.4.0:** Deprecation warning added
- **v2.0.0:** `RedisDSLCache` alias removed

---

## Testing

### Unit Tests

**Before:**
```python
@pytest.fixture
def redis_cache():
    return RedisDSLCache(redis_db=5)
```

**After:**
```python
@pytest.fixture
def redis_cache():
    return DSLBytecodeCache()  # Uses test config
```

### Integration Tests

```python
import pytest
from mysingle.dsl.cache import DSLBytecodeCache, InMemoryDSLCache

@pytest.mark.asyncio
async def test_cache_operations():
    # Redis cache (requires Redis running)
    cache = DSLBytecodeCache()

    # Check health
    is_healthy = await cache.health_check()
    if not is_healthy:
        pytest.skip("Redis not available")

    # Test operations
    await cache.set("test:key", b"bytecode", ttl=60)
    value = await cache.get("test:key")
    assert value == b"bytecode"

    await cache.delete("test:key")
    assert await cache.get("test:key") is None

@pytest.mark.asyncio
async def test_in_memory_fallback():
    # In-memory cache (no Redis required)
    cache = InMemoryDSLCache(max_size=100)

    await cache.set("test:key", b"bytecode")
    value = await cache.get("test:key")
    assert value == b"bytecode"
```

---

## Troubleshooting

### Issue: Cache Not Working

**Symptom:** Cache operations return None

**Solution:**
```python
# Check Redis connection
cache = DSLBytecodeCache()
is_healthy = await cache.health_check()

if not is_healthy:
    # Check environment variables
    from mysingle.core.config import get_settings
    settings = get_settings()

    print(f"REDIS_HOST: {settings.REDIS_HOST}")
    print(f"REDIS_PORT: {settings.REDIS_PORT}")
    print(f"REDIS_DB_DSL: {settings.REDIS_DB_DSL}")
```

### Issue: Wrong Redis DB

**Symptom:** Cache data in unexpected Redis DB

**Solution:**
```bash
# Check .env file
cat .env | grep REDIS_DB_DSL

# Should be:
REDIS_DB_DSL=5
```

### Issue: Import Error

**Symptom:** `ImportError: cannot import name 'DSLBytecodeCache'`

**Solution:**
```bash
# Update mysingle package
uv sync --all-extras

# Or reinstall
uv pip install -e ".[common-grpc]"
```

---

## Benefits

### 1. Standardization

- ✅ Consistent with other MySingle services (IAM, Market Data, etc.)
- ✅ Single Redis DB for all DSL bytecode (no fragmentation)
- ✅ Unified configuration pattern

### 2. Reliability

- ✅ Connection pooling from `BaseRedisCache`
- ✅ Automatic reconnection handling
- ✅ Graceful degradation when Redis unavailable

### 3. Maintainability

- ✅ Less duplicate code
- ✅ Centralized Redis client management
- ✅ Easier testing and debugging

### 4. Performance

- ✅ Connection reuse via pooling
- ✅ Optimized serialization (pickle for bytes)
- ✅ Batch operations support

---

## Related Documentation

- [MySingle Database Module](../../database/README.md)
- [BaseRedisCache API](../../database/redis_cache.py)
- [Configuration Guide](../../core/config.py)
- [DSL Enhancement Dashboard](./DSL_ENHANCEMENT_DASHBOARD.md)

---

## Questions?

For issues or questions:
- Slack: #dsl-runtime
- GitHub Issues: https://github.com/Br0therDan/mysingle-pack/issues

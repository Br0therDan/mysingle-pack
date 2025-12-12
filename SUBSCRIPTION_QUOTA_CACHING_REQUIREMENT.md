# Subscription Service - Quota Caching Implementation Request

**Date**: 2025-12-12
**Requestor**: Platform Architecture Team
**Target Team**: Subscription Service Team
**Priority**: High (Performance Critical)
**Estimated Impact**: 80-90% latency reduction for quota checks

---

## 📋 Executive Summary

**Problem**:
QuotaEnforcementMiddleware가 모든 API 요청마다 Subscription Service에 gRPC 호출을 수행하여 5-10ms의 latency가 발생합니다. 이는 전체 요청 시간의 25-50%를 차지하는 주요 병목입니다.

**Solution**:
Subscription Service에 Redis 기반 캐싱 레이어를 추가하여 반복적인 quota 조회를 캐시에서 처리합니다.

**Expected Outcome**:
- Cache hit rate 80-90% 가정 시 quota check latency: 5-10ms → 0.5-2ms (80-90% 감소)
- 전체 API 응답 시간: 15-20ms → 10-15ms (25-30% 개선)
- Subscription Service 부하: 1000 req/sec → 100-200 req/sec (80-90% 감소)

---

## 🎯 Requirements

### 1. Redis Cache Layer

**Cache Key Structure**:
```
quota:{user_id}:{metric}
```

**Example**:
```
quota:507f1f77bcf86cd799439011:api_calls
quota:507f1f77bcf86cd799439011:backtest_jobs
quota:507f1f77bcf86cd799439011:strategy_count
```

**Cache Value (JSON)**:
```json
{
  "allowed": true,
  "current_usage": 450,
  "limit": 1000,
  "remaining": 550,
  "reset_at": 1702368000,
  "cached_at": 1702364400
}
```

**TTL (Time-to-Live)**:
- Default: 10초 (빠른 갱신 + 충분한 캐시 효과)
- Configurable: 환경 변수로 조정 가능 (`QUOTA_CACHE_TTL`)

---

### 2. CheckQuota gRPC Method Update

**Current Behavior**:
```
Client → Subscription Service → Database → Response
(모든 요청이 DB 조회)
```

**New Behavior (With Cache)**:
```
Client → Subscription Service → Redis Cache (try)
                               ├─ Cache HIT → Return cached result (fast)
                               └─ Cache MISS → Database → Update cache → Return result
```

**Implementation Logic**:
```
function CheckQuota(user_id, metric, amount):
    cache_key = f"quota:{user_id}:{metric}"

    # 1. Try cache first
    cached_data = redis.get(cache_key)
    if cached_data:
        return cached_data  # Fast path (0.5-2ms)

    # 2. Cache miss: Query database
    db_result = database.query_quota(user_id, metric)

    # 3. Update cache
    redis.set(cache_key, db_result, ttl=10)

    # 4. Return result
    return db_result
```

---

### 3. Cache Invalidation Strategy

**Invalidation Triggers**:

1. **Quota Exceeded** (usage update):
   ```
   When RecordUsage() is called:
   → Delete cache key: quota:{user_id}:{metric}
   → Next CheckQuota() will fetch fresh data
   ```

2. **Subscription Changed** (tier upgrade/downgrade):
   ```
   When UpdateSubscription() is called:
   → Delete ALL cache keys for user: quota:{user_id}:*
   → Ensures new limits are immediately reflected
   ```

3. **Manual Reset** (admin action):
   ```
   When ResetQuota() is called:
   → Delete specific cache key
   ```

**Implementation**:
```python
def record_usage(user_id, metric, amount):
    # Update database
    database.increment_usage(user_id, metric, amount)

    # Invalidate cache
    cache_key = f"quota:{user_id}:{metric}"
    redis.delete(cache_key)

    return success

def update_subscription(user_id, new_tier):
    # Update database
    database.update_user_subscription(user_id, new_tier)

    # Invalidate ALL quota caches for user
    pattern = f"quota:{user_id}:*"
    for key in redis.scan_iter(match=pattern):
        redis.delete(key)

    return success
```

---

### 4. Configuration

**Environment Variables**:
```bash
# Subscription Service .env
QUOTA_CACHE_ENABLED=true              # Enable/disable caching
QUOTA_CACHE_TTL=10                    # Cache TTL in seconds
QUOTA_CACHE_REDIS_DB=14               # Redis DB allocation (per platform standards)
QUOTA_CACHE_KEY_PREFIX=quota          # Cache key prefix
```

**Redis Connection** (Reuse existing):
- Use `mysingle.database.get_redis_client(db=14)` from mysingle-pack
- DB 14 allocated for Subscription Service (platform standard)

---

### 5. Monitoring & Metrics

**Required Metrics** (Prometheus):
```
# Cache hit/miss rates
subscription_quota_cache_hits_total
subscription_quota_cache_misses_total

# Cache latency
subscription_quota_cache_latency_seconds

# Cache size
subscription_quota_cache_keys_total

# Invalidation counts
subscription_quota_cache_invalidations_total
```

**Logging**:
```python
# On cache hit
logger.debug("Quota cache hit", user_id=user_id, metric=metric)

# On cache miss
logger.debug("Quota cache miss", user_id=user_id, metric=metric)

# On invalidation
logger.info("Quota cache invalidated", user_id=user_id, metric=metric, reason="usage_recorded")
```

---

## 📊 Performance Requirements

### Latency Targets

| Operation               | Current | Target  | Improvement       |
| ----------------------- | ------- | ------- | ----------------- |
| CheckQuota (cache hit)  | 5-10ms  | 0.5-2ms | 80-90%            |
| CheckQuota (cache miss) | 5-10ms  | 6-12ms  | -20% (acceptable) |
| Cache invalidation      | N/A     | <1ms    | N/A               |

### Throughput Targets

| Metric                    | Current      | Target                       | Improvement      |
| ------------------------- | ------------ | ---------------------------- | ---------------- |
| Subscription Service load | 1000 req/sec | 100-200 req/sec              | 80-90% reduction |
| Redis operations          | 0            | 800-900 req/sec (cache hits) | New workload     |

### Cache Hit Rate

- **Target**: 80-90% (typical workload)
- **Measurement**: `cache_hits / (cache_hits + cache_misses)`

---

## 🧪 Testing Requirements

### Unit Tests

- [ ] Cache hit scenario (return cached data)
- [ ] Cache miss scenario (query DB + update cache)
- [ ] Cache invalidation on usage update
- [ ] Cache invalidation on subscription change
- [ ] TTL expiration behavior
- [ ] Redis connection failure fallback (directly query DB)

### Integration Tests

- [ ] End-to-end quota check with caching
- [ ] Cache invalidation triggers
- [ ] Concurrent requests (cache race conditions)
- [ ] Cache warm-up scenario

### Performance Tests

- [ ] Latency comparison (with/without cache)
- [ ] Cache hit rate measurement (realistic workload)
- [ ] Redis load test (1000 req/sec)

---

## 🔄 Rollout Strategy

### Phase 1: Implementation (Week 1)
- Implement cache layer in Subscription Service
- Add cache invalidation logic
- Unit tests + integration tests

### Phase 2: Staging Deployment (Week 2)
- Deploy to staging environment
- Enable caching with `QUOTA_CACHE_ENABLED=true`
- Monitor cache hit rate + latency
- Load testing (simulate production traffic)

### Phase 3: Production Rollout (Week 3)
- Deploy to production
- Feature flag: Start with 10% traffic → 50% → 100%
- Monitor metrics:
  - Cache hit rate (target: 80-90%)
  - Latency reduction (target: 80-90%)
  - Error rate (must remain <0.1%)

### Phase 4: Optimization (Week 4)
- Tune TTL based on cache hit rate vs. staleness trade-off
- Optimize Redis connection pooling
- Add cache warm-up for frequently accessed users

---

## ⚠️ Edge Cases & Considerations

### 1. Cache Staleness

**Problem**: Cache에서 반환한 데이터가 실제 DB와 다를 수 있음 (TTL 내에서)

**Mitigation**:
- Short TTL (10초) - 최대 10초 stale
- Critical operations (RecordUsage)는 항상 cache invalidation
- Acceptable trade-off: 10초 stale data는 quota 시스템에서 허용 가능

### 2. Redis Failure

**Problem**: Redis 다운 시 caching 불가

**Mitigation**:
```python
def check_quota(user_id, metric):
    try:
        # Try cache
        cached = redis.get(cache_key)
        if cached:
            return cached
    except RedisConnectionError:
        logger.warning("Redis unavailable, falling back to DB")

    # Fallback to DB (always works)
    return database.query_quota(user_id, metric)
```

### 3. Cache Thundering Herd

**Problem**: 많은 요청이 동시에 cache miss 발생 시 DB 부하

**Mitigation**:
- Use `SET NX` (set if not exists) with short lock
- First request updates cache, others wait and retry
- Low priority (unlikely with 10s TTL)

### 4. Multi-Instance Race Condition

**Problem**: 여러 Subscription Service 인스턴스가 동시에 cache update

**Mitigation**:
- Redis atomic operations (INCR, SET)
- "Last write wins" is acceptable (quota는 eventual consistency 허용)

---

## 📦 Deliverables

### Code Changes

- [ ] Redis cache layer implementation
- [ ] CheckQuota method update (cache-first logic)
- [ ] Cache invalidation in RecordUsage/UpdateSubscription
- [ ] Configuration support (QUOTA_CACHE_ENABLED, etc.)
- [ ] Prometheus metrics export

### Documentation

- [ ] Architecture diagram (with cache layer)
- [ ] Configuration guide (how to enable/tune caching)
- [ ] Monitoring playbook (how to interpret metrics)

### Testing

- [ ] Unit tests (>80% coverage)
- [ ] Integration tests (end-to-end scenarios)
- [ ] Performance benchmark report (before/after comparison)

---

## 📈 Success Metrics

### Primary Metrics

- ✅ Cache hit rate: **80-90%**
- ✅ CheckQuota latency (cache hit): **<2ms** (p95)
- ✅ Overall API latency reduction: **25-30%**
- ✅ Subscription Service load reduction: **80-90%**

### Secondary Metrics

- ✅ Zero increase in error rate
- ✅ Cache invalidation latency: <1ms
- ✅ Redis memory usage: <500MB (for 100K users)

---

## 🤝 Coordination Points

### With Platform Team

- Redis DB allocation confirmed (DB 14 for Subscription Service)
- `mysingle.database.get_redis_client()` usage pattern
- Monitoring/alerting setup (Prometheus + Grafana)

### With Service Teams

- No changes required in other services (transparent optimization)
- QuotaEnforcementMiddleware continues to work as-is
- Backward compatible (cache can be disabled via feature flag)

---

## 📞 Questions & Support

**Technical Questions**:
- Contact: Platform Architecture Team
- Slack: #platform-architecture

**Implementation Support**:
- Redis setup: DevOps Team (#devops)
- mysingle-pack usage: Backend Team (#backend-help)

**Monitoring & Metrics**:
- Prometheus setup: SRE Team (#sre)

---

## Appendix: Example Implementation (Pseudocode)

```python
# Subscription Service - quota_service.py

from mysingle.database import get_redis_client
from mysingle.core.config import settings
import json

class QuotaService:
    def __init__(self):
        self.redis = get_redis_client(db=14) if settings.QUOTA_CACHE_ENABLED else None
        self.cache_ttl = settings.QUOTA_CACHE_TTL or 10

    async def check_quota(self, user_id: str, metric: str, amount: int = 1):
        """Check quota with caching"""

        # Try cache first
        if self.redis:
            cache_key = f"quota:{user_id}:{metric}"
            try:
                cached = await self.redis.get(cache_key)
                if cached:
                    logger.debug("Quota cache hit", user_id=user_id, metric=metric)
                    return json.loads(cached)
            except Exception as e:
                logger.warning("Cache read failed", error=str(e))

        # Cache miss or disabled: Query database
        logger.debug("Quota cache miss", user_id=user_id, metric=metric)
        result = await self._query_quota_from_db(user_id, metric, amount)

        # Update cache (fire and forget)
        if self.redis:
            try:
                await self.redis.set(
                    cache_key,
                    json.dumps(result),
                    ex=self.cache_ttl
                )
            except Exception as e:
                logger.warning("Cache write failed", error=str(e))

        return result

    async def record_usage(self, user_id: str, metric: str, amount: int):
        """Record usage and invalidate cache"""

        # Update database
        await self._update_usage_in_db(user_id, metric, amount)

        # Invalidate cache
        if self.redis:
            cache_key = f"quota:{user_id}:{metric}"
            try:
                await self.redis.delete(cache_key)
                logger.info("Quota cache invalidated", user_id=user_id, metric=metric)
            except Exception as e:
                logger.warning("Cache invalidation failed", error=str(e))

    async def _query_quota_from_db(self, user_id, metric, amount):
        # Existing database query logic
        ...

    async def _update_usage_in_db(self, user_id, metric, amount):
        # Existing database update logic
        ...
```

---

**Document Owner**: Platform Architecture Team
**Review Date**: 2025-12-12
**Target Start Date**: 2025-12-16 (Sprint 24)
**Estimated Duration**: 3-4 weeks
**Status**: 📋 **Request Submitted** - Awaiting Subscription Service Team review

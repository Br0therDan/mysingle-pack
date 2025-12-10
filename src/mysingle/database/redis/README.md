# Redis 캐시 모듈

**버전:** 2.2.1 | **모듈:** `mysingle.database.redis`

MySingle Quant 서비스를 위한 고성능 Redis 캐시 및 클라이언트 관리 모듈입니다.

---

## 개요

Redis 모듈은 플랫폼 전반에 걸친 표준화된 캐싱 인프라를 제공합니다:

- **연결 풀 관리**: 효율적인 Redis 연결 관리
- **멀티 DB 지원**: 서비스별 DB 분리 (0-15)
- **범용 캐시 클래스**: 타입 안전한 캐싱 기본 클래스
- **팩토리 함수**: 플랫폼 표준을 강제하는 캐시 생성 함수

### 주요 기능

| 기능               | 설명                                       |
| ------------------ | ------------------------------------------ |
| **연결 풀**        | 자동 연결 풀 관리 및 재사용                |
| **DB 분리**        | 서비스별 전용 DB 할당 (0-15)               |
| **TTL 관리**       | 자동 만료 시간 설정                        |
| **직렬화**         | JSON/Pickle 자동 직렬화                    |
| **타입 안전성**    | Generic 타입을 통한 타입 체크              |
| **헬스 체크**      | 연결 상태 모니터링                         |
| **구조화된 로깅**  | Correlation ID 포함 로깅                   |
| **서비스 간 공유** | Redis를 통한 마이크로서비스 간 데이터 공유 |

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

### 팩토리 함수 사용 (권장)

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

### 직접 Redis 클라이언트 사용

```python
from mysingle.database import get_redis_client

# 특정 DB의 Redis 클라이언트 가져오기
redis = await get_redis_client(db=5)
if redis:
    await redis.set("market:AAPL:price", "150.25", ex=60)
    price = await redis.get("market:AAPL:price")
```

### 커스텀 캐시 클래스

```python
from mysingle.database import BaseRedisCache
from pydantic import BaseModel

class MarketData(BaseModel):
    symbol: str
    price: float
    volume: int

class MarketDataCache(BaseRedisCache[MarketData]):
    """시장 데이터 전용 캐시"""

    def __init__(self):
        super().__init__(
            key_prefix="market",
            default_ttl=60,
            use_json=True,
        )

    async def get_ticker_price(self, symbol: str) -> float | None:
        """티커 가격 조회"""
        data = await self.get(f"ticker:{symbol}")
        return data.price if data else None

# 사용 예시
cache = MarketDataCache()
await cache.set("ticker:AAPL", MarketData(
    symbol="AAPL",
    price=150.25,
    volume=1000000
))
```

---

## Redis DB 할당 표준

MySingle Quant은 플랫폼 전체에 걸쳐 표준화된 Redis DB 할당을 사용합니다.

| DB  | 용도                | 담당 서비스       | 키 프리픽스 예시                      | TTL 가이드      |
| --- | ------------------- | ----------------- | ------------------------------------- | --------------- |
| 0   | 사용자 인증         | IAM               | `user:{user_id}`                      | 300s (5분)      |
| 1   | gRPC 응답 캐시      | 모든 서비스       | `grpc:{service_name}:{method}:{hash}` | 3600s (1시간)   |
| 2   | Rate Limiting       | Kong/Gateway      | `ratelimit:{user_id}:{endpoint}`      | 60-3600s        |
| 3   | 세션 저장소         | IAM               | `session:{session_id}`                | 86400s (24시간) |
| 4   | DSL 바이트코드 캐시 | Strategy          | `dsl:bytecode:{strategy_id}`          | 3600-86400s     |
| 5   | 시장 데이터 캐시    | Market Data       | `market:{symbol}:{interval}:{hash}`   | 300-3600s       |
| 6   | 백테스트 캐시       | Backtest          | `walkforward:{job_id}:{window}`       | 3600-86400s     |
| 7   | 인디케이터 캐시     | Indicator         | `indicator:{name}:{symbol}:{params}`  | 1800-7200s      |
| 8   | 전략 캐시           | Strategy          | `strategy:{strategy_id}`              | 600-3600s       |
| 9   | 알림 큐             | Notification      | `notif:{user_id}:{timestamp}`         | 300-1800s       |
| 10  | Celery Broker       | Backtest (Celery) | `celery:task:{task_id}`               | 자동 관리       |
| 11  | Celery Result       | Backtest (Celery) | `celery-task-meta-{task_id}`          | 자동 관리       |
| 12  | ML 모델 캐시        | ML                | `ml:model:{model_id}`                 | 3600-86400s     |
| 13  | GenAI 응답 캐시     | GenAI             | `genai:{prompt_hash}`                 | 1800-7200s      |
| 14  | 구독 캐시           | Subscription      | `subscription:{user_id}`              | 3600s           |
| 15  | 예약됨              | Platform          | -                                     | -               |

### 사용 가이드라인

**✅ 권장 사항:**
- 서비스별 캐싱은 `BaseRedisCache` 사용
- `CommonSettings`의 `REDIS_DB_*` 상수 참조
- 서비스별 key_prefix 표준 준수
- 데이터 휘발성에 따른 적절한 TTL 설정
- 직접 작업이 필요한 경우 `get_redis_client(db=N)` 사용

**❌ 금지 사항:**
- 코드에 DB 번호 하드코딩
- `BaseRedisCache` 없이 `redis.asyncio` 직접 사용
- 관련 없는 용도로 DB 번호 공유
- DB 15 사용 (플랫폼 예약)
- 프리픽스 네임스페이스 없이 키 생성

---

## 팩토리 함수

### create_user_cache

사용자 인증 캐시 생성 (DB 0)

```python
from mysingle.database import create_user_cache

cache = create_user_cache()
await cache.set("user_id_123", user_data, ttl=300)
user = await cache.get("user_id_123")
```

### create_grpc_cache

특정 서비스의 gRPC 응답 캐시 생성 (DB 1)

```python
from mysingle.database import create_grpc_cache

cache = create_grpc_cache(service_name="strategy")
await cache.set("GetStrategy:abc123", response_data)
result = await cache.get("GetStrategy:abc123")
```

### create_service_cache

커스텀 DB를 사용하는 서비스별 캐시 생성

```python
from mysingle.database import create_service_cache
from mysingle.core.config import settings

# 시장 데이터 캐시 (DB 5)
market_cache = create_service_cache(
    service_name="market",
    db_constant=settings.REDIS_DB_MARKET_DATA,
)

# 인디케이터 캐시 (DB 7)
indicator_cache = create_service_cache(
    service_name="indicator",
    db_constant=settings.REDIS_DB_INDICATOR,
)
```

**팩토리 함수의 장점:**
- ✅ 플랫폼 전체 DB 할당 표준 강제
- ✅ DB 번호 충돌 방지
- ✅ 합리적인 기본값으로 캐시 생성 간소화
- ✅ 캐시 구성 관리 중앙화
- ✅ 자동 key_prefix 및 TTL 표준화

---

## 핵심 컴포넌트

### RedisConfig

연결 풀을 지원하는 Redis 연결 구성 클래스

```python
from mysingle.database import RedisConfig

# URL에서 생성
config = RedisConfig.from_url("redis://:password@localhost:6379/1")

# 수동 구성
config = RedisConfig(
    host="redis-server.example.com",
    port=6379,
    db=1,
    password="secure-password",
    max_connections=50,
    socket_timeout=5.0,
)
```

### RedisClientManager

Redis 연결 풀을 관리하고 DB별 클라이언트를 제공합니다.

```python
from mysingle.database import RedisClientManager, RedisConfig

config = RedisConfig(host="localhost", port=6379, password="secret")
manager = RedisClientManager(config)

async with manager:
    client = await manager.get_client(db=1)
    if client:
        await client.set("key", "value")

    # 헬스 체크
    is_healthy = await manager.health_check(db=1)
```

### BaseRedisCache

TTL과 타입 안전성을 갖춘 범용 Redis 캐시 기본 클래스

**주요 메서드:**

| 메서드             | 설명                 |
| ------------------ | -------------------- |
| `get(key)`         | 캐시 값 조회         |
| `set(key, val)`    | TTL과 함께 값 저장   |
| `delete(key)`      | 캐시 값 삭제         |
| `exists(key)`      | 키 존재 여부 확인    |
| `expire(key, ttl)` | TTL 업데이트         |
| `clear_all()`      | 프리픽스로 모두 삭제 |
| `health_check()`   | Redis 연결 확인      |

**속성:**

| 속성          | 타입   | 설명                               |
| ------------- | ------ | ---------------------------------- |
| `key_prefix`  | `str`  | 캐시 키 프리픽스 (예: "market")    |
| `default_ttl` | `int`  | 기본 TTL (초)                      |
| `redis_db`    | `int`  | Redis DB 번호 (0-15, 읽기 전용)    |
| `use_json`    | `bool` | JSON(True) 또는 Pickle(False) 사용 |

---

## 환경 변수

서비스의 `.env` 파일에서 Redis 구성:

```bash
# Redis 연결
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=         # 선택사항: AUTH 설정시 사용

# DB 할당 (CommonSettings에서 정의됨)
REDIS_DB_USER=0              # 사용자 캐시
REDIS_DB_GRPC=1              # gRPC 응답 캐시
REDIS_DB_MARKET_DATA=5       # 시장 데이터
REDIS_DB_INDICATOR=7         # 인디케이터
```

---

## 고급 사용법

### 배치 작업

```python
from mysingle.database import get_redis_client

redis = await get_redis_client(db=1)
if redis:
    # 파이프라인 사용으로 네트워크 왕복 감소
    pipe = redis.pipeline()
    for item in items:
        pipe.set(f"item:{item.id}", item.value, ex=300)
    await pipe.execute()
```

### 키 네이밍 규칙

```python
# 서비스 레벨 패턴: {service}:{entity}:{identifier}
"market:ticker:AAPL"
"market:ohlcv:GOOGL:1h"
"indicator:RSI:AAPL:14"
"strategy:momentum:result:123"

# 사용자별 패턴: {service}:user:{user_id}:{entity}
"market:user:456:watchlist"

# 임시 데이터: {service}:temp:{identifier}
"market:temp:snapshot:20241210"
```

### TTL 전략

```python
# 실시간 데이터 (30초 - 1분)
await cache.set("market:ticker:AAPL", price_data, ttl=60)

# 계산된 인디케이터 (2-5분)
await cache.set("indicator:RSI:AAPL", rsi_data, ttl=300)

# 전략 결과 (5-10분)
await cache.set("strategy:result:123", result, ttl=600)

# 사용자 세션 (30분 - 1시간)
await cache.set("session:123", session, ttl=3600)

# 구성 데이터 (1-24시간)
await cache.set("config:strategy:456", config, ttl=86400)
```

---

## 모범 사례

### ✅ 권장

```python
# 전용 DB 사용
market_cache = create_service_cache("market", settings.REDIS_DB_MARKET_DATA)

# Redis 가용성 확인
redis = await get_redis_client(db=1)
if redis:
    await redis.set("key", "value")
else:
    logger.warning("Redis 사용 불가 - 대체 방법 사용")

# 항상 TTL 설정
await cache.set("key", data, ttl=300)

# 명확한 키 네이밍 규칙
await redis.set(f"{service}:{entity}:{id}", value)

# 에러 우아하게 처리
try:
    result = await cache.get("key")
except Exception as e:
    logger.error(f"Redis 오류: {e}")
    result = None

# 배치 작업에 파이프라인 사용
pipe = redis.pipeline()
for item in items:
    pipe.set(f"item:{item.id}", item.value)
await pipe.execute()
```

### ❌ 금지

```python
# DB 0를 서비스 데이터에 사용하지 말 것 (IAM 전용)
redis = await get_redis_client(db=0)  # 사용자 인증 캐시 전용!

# TTL 없이 임시 데이터 저장
await redis.set("temp_data", value)  # 절대 만료되지 않음!

# None 반환 무시 (Redis 사용 불가)
redis = await get_redis_client(db=1)
await redis.set("key", "value")  # redis가 None이면 크래시!

# 프리픽스 없는 일반 키
await redis.set("data", value)  # 충돌 위험!

# 수동 직렬화 (BaseRedisCache 사용)
import json
await redis.set("key", json.dumps(data))  # cache.set() 사용!

# 루프에서 개별 작업
for item in items:
    await redis.set(f"item:{item.id}", item.value)  # 파이프라인 사용!
```

---

## 문제 해결

### Redis가 None 반환

**증상:** `get_redis_client()`가 None 반환

**가능한 원인:**
1. Redis 서버 미실행
2. 연결 거부 (잘못된 host/port)
3. 인증 실패 (잘못된 password)
4. 네트워크 타임아웃

**해결:**
```python
# Redis 연결 수동 확인
from mysingle.database import get_redis_client

redis = await get_redis_client(db=1)
if redis is None:
    print("Redis 사용 불가 - REDIS_HOST, REDIS_PORT, REDIS_PASSWORD 확인")
else:
    try:
        await redis.ping()
        print("Redis 연결 정상")
    except Exception as e:
        print(f"Redis ping 실패: {e}")
```

### 캐시가 항상 None 반환

**증상:** `cache.set()` 후에도 `cache.get()`이 None 반환

**가능한 원인:**
1. 잘못된 Redis DB
2. TTL이 너무 짧음
3. 직렬화 오류
4. 키 불일치

**디버깅:**
```python
# Redis에 무엇이 있는지 확인
redis = await get_redis_client(db=1)
keys = await redis.keys("*")
print(f"DB 1의 키: {keys}")

# 특정 키 확인
value = await redis.get("market:ticker:AAPL")
print(f"원시 값: {value}")

# TTL 확인
ttl = await redis.ttl("market:ticker:AAPL")
print(f"남은 TTL: {ttl}초")
```

### 메모리 사용량이 너무 높음

**증상:** Redis 메모리가 무한정 증가

**원인:** 캐시 데이터에 TTL 누락

**해결:**
```python
# 항상 TTL 설정
await cache.set("key", data, ttl=300)

# TTL이 없는 기존 키에 설정
await redis.expire("key", 300)

# 현재 TTL 확인
ttl = await redis.ttl("key")
if ttl == -1:  # TTL 미설정
    await redis.expire("key", 3600)

# 메모리 사용량 모니터링
info = await redis.info("memory")
print(f"사용 메모리: {info['used_memory_human']}")
```

---

## API 레퍼런스

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

    async def get_client(self, db: int | None = None) -> redis.Redis | None: ...
    async def close_all(self) -> None: ...
    async def health_check(self, db: int = 0) -> bool: ...

# 글로벌 인스턴스
async def get_redis_client(db: int = 0) -> redis.Redis | None: ...
```

### BaseRedisCache[T]

```python
class BaseRedisCache(Generic[T]):
    def __init__(
        self,
        key_prefix: str,
        default_ttl: int = 300,
        use_json: bool = False,
    ): ...

    async def get(self, key: str) -> T | None: ...
    async def set(self, key: str, value: T, ttl: int | None = None) -> bool: ...
    async def delete(self, key: str) -> bool: ...
    async def exists(self, key: str) -> bool: ...
    async def expire(self, key: str, ttl: int) -> bool: ...
    async def clear_all(self, pattern: str = "*") -> int: ...

    @property
    def redis_db(self) -> int: ...  # 읽기 전용
```

### 팩토리 함수

```python
def create_user_cache(*, default_ttl: int = 300) -> BaseRedisCache: ...

def create_grpc_cache(
    service_name: str,
    *,
    default_ttl: int = 3600,
) -> BaseRedisCache: ...

def create_service_cache(
    service_name: str,
    db_constant: int,
    *,
    default_ttl: int = 3600,
) -> BaseRedisCache: ...
```

---

**버전:** 2.2.1
**모듈:** `mysingle.database.redis`
**라이선스:** MIT

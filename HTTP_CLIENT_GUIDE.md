# HTTP Client 사용 가이드

MySingle Quant 패키지의 표준 HTTP 클라이언트 사용법을 설명합니다.

## 주요 특징

- **연결 풀링**: httpx 기반 비동기 연결 풀 관리
- **자동 URL 구성**: 서비스명으로부터 Gateway/Direct URL 자동 생성
- **싱글톤 패턴**: 서비스별 클라이언트 재사용으로 리소스 효율성
- **생명주기 관리**: App Factory와 통합된 자동 정리
- **환경 설정**: 환경 변수로 타임아웃, 연결 수 등 제어 가능

## 기본 사용법

### 1. 서비스 클라이언트 생성 (일회성)

```python
from mysingle_quant.core import create_service_http_client

# 기본 생성 (URL 자동 구성)
client = create_service_http_client("strategy-service")

# 커스텀 설정
client = create_service_http_client(
    service_name="strategy-service",
    base_url="http://custom-host:8003",
    timeout=60.0,
    max_connections=50,
    headers={"X-Custom-Header": "value"}
)

# 사용
async with client:
    response = await client.get("/strategies")
    data = response.json()
```

### 2. 싱글톤 클라이언트 사용 (권장)

```python
from mysingle_quant.core import get_service_http_client

# 서비스별 클라이언트 재사용
strategy_client = get_service_http_client("strategy-service")
backtest_client = get_service_http_client("backtest-service")

# HTTP 메서드 사용
strategies = await strategy_client.get("/strategies")
result = await backtest_client.post("/backtests", json={"strategy_id": "123"})
```

### 3. 편의 함수 사용

```python
from mysingle_quant.core import make_service_request

# 한 줄로 요청
response = await make_service_request(
    service_name="strategy-service",
    method="GET",
    endpoint="/strategies",
    headers={"Authorization": "Bearer token"}
)
```

## 서비스별 클라이언트 예시

### Strategy Service 연동

```python
from mysingle_quant.core import get_service_http_client

class StrategyServiceClient:
    def __init__(self):
        self.client = get_service_http_client("strategy-service")
    
    async def get_strategies(self, user_id: str) -> list[dict]:
        """사용자 전략 목록 조회"""
        response = await self.client.get(
            "/strategies",
            headers={"X-User-Id": user_id}
        )
        response.raise_for_status()
        return response.json()
    
    async def create_strategy(self, strategy_data: dict, user_id: str) -> dict:
        """전략 생성"""
        response = await self.client.post(
            "/strategies",
            json=strategy_data,
            headers={"X-User-Id": user_id}
        )
        response.raise_for_status()
        return response.json()
    
    async def update_strategy(self, strategy_id: str, data: dict, user_id: str) -> dict:
        """전략 수정"""
        response = await self.client.put(
            f"/strategies/{strategy_id}",
            json=data,
            headers={"X-User-Id": user_id}
        )
        response.raise_for_status()
        return response.json()
```

### Backtest Service 연동

```python
from mysingle_quant.core import get_service_http_client

class BacktestServiceClient:
    def __init__(self):
        self.client = get_service_http_client("backtest-service")
    
    async def start_backtest(self, config: dict, user_id: str) -> dict:
        """백테스트 시작"""
        response = await self.client.post(
            "/backtests/start",
            json=config,
            headers={"X-User-Id": user_id}
        )
        response.raise_for_status()
        return response.json()
    
    async def get_backtest_status(self, backtest_id: str, user_id: str) -> dict:
        """백테스트 상태 조회"""
        response = await self.client.get(
            f"/backtests/{backtest_id}/status",
            headers={"X-User-Id": user_id}
        )
        response.raise_for_status()
        return response.json()
```

## 환경 설정

### .env 파일 설정

```bash
# HTTP 클라이언트 설정
HTTP_CLIENT_TIMEOUT=30.0
HTTP_CLIENT_MAX_CONNECTIONS=100
HTTP_CLIENT_MAX_KEEPALIVE=20
HTTP_CLIENT_MAX_RETRIES=3
HTTP_CLIENT_RETRY_DELAY=1.0

# API Gateway 설정
USE_API_GATEWAY=true
API_GATEWAY_URL=http://localhost:8000
```

### 서비스별 설정 확장

```python
# app/core/config.py
from mysingle_quant.core.config import CommonSettings

class MyServiceSettings(CommonSettings):
    SERVICE_NAME: str = "my-service"
    
    # 서비스별 HTTP 클라이언트 설정
    STRATEGY_SERVICE_URL: str = "http://kong-gateway:8000/strategy"
    BACKTEST_SERVICE_URL: str = "http://kong-gateway:8000/backtest"
    
    # 커스텀 타임아웃
    STRATEGY_CLIENT_TIMEOUT: float = 60.0
    BACKTEST_CLIENT_TIMEOUT: float = 300.0  # 백테스트는 오래 걸림

settings = MyServiceSettings()
```

## FastAPI 서비스에서 사용

### 의존성 주입 패턴

```python
from fastapi import FastAPI, Depends
from mysingle_quant.core import get_service_http_client, ServiceHttpClient

# 의존성 함수
def get_strategy_client() -> ServiceHttpClient:
    return get_service_http_client("strategy-service")

def get_backtest_client() -> ServiceHttpClient:
    return get_service_http_client("backtest-service")

# 라우터에서 사용
@app.post("/journeys")
async def create_journey(
    journey_data: dict,
    strategy_client: ServiceHttpClient = Depends(get_strategy_client),
    backtest_client: ServiceHttpClient = Depends(get_backtest_client)
):
    # 전략 검증
    strategy = await strategy_client.get(f"/strategies/{journey_data['strategy_id']}")
    
    # 백테스트 시작
    backtest = await backtest_client.post("/backtests/start", json=journey_data)
    
    return {"journey_id": "123", "backtest_id": backtest.json()["id"]}
```

### 서비스 클래스 패턴

```python
from mysingle_quant.core import get_service_http_client

class JourneyOrchestrator:
    def __init__(self):
        self.strategy_client = get_service_http_client("strategy-service")
        self.backtest_client = get_service_http_client("backtest-service")
        self.notification_client = get_service_http_client("notification-service")
    
    async def execute_journey(self, journey_config: dict, user_id: str) -> dict:
        """여정 실행"""
        headers = {"X-User-Id": user_id}
        
        try:
            # 1. 전략 검증
            strategy_response = await self.strategy_client.get(
                f"/strategies/{journey_config['strategy_id']}",
                headers=headers
            )
            strategy = strategy_response.json()
            
            # 2. 백테스트 시작
            backtest_response = await self.backtest_client.post(
                "/backtests/start",
                json={
                    "strategy_id": strategy["id"],
                    "config": journey_config["backtest_config"]
                },
                headers=headers
            )
            backtest = backtest_response.json()
            
            # 3. 알림 발송
            await self.notification_client.post(
                "/notifications/send",
                json={
                    "user_id": user_id,
                    "type": "journey_started",
                    "data": {"journey_id": journey_config["id"]}
                },
                headers=headers
            )
            
            return {
                "status": "started",
                "strategy": strategy,
                "backtest": backtest
            }
            
        except Exception as e:
            # 에러 알림
            await self.notification_client.post(
                "/notifications/send",
                json={
                    "user_id": user_id,
                    "type": "journey_error",
                    "data": {"error": str(e)}
                },
                headers=headers
            )
            raise
```

## 에러 처리 및 재시도

### httpx 예외 처리

```python
import httpx
from mysingle_quant.core import get_service_http_client

async def robust_service_call():
    client = get_service_http_client("strategy-service")
    
    try:
        response = await client.get("/strategies", timeout=30.0)
        response.raise_for_status()  # HTTP 에러 발생 시 예외
        return response.json()
        
    except httpx.TimeoutException:
        # 타임아웃 처리
        logger.error("Strategy service timeout")
        raise
        
    except httpx.HTTPStatusError as e:
        # HTTP 에러 처리
        if e.response.status_code == 404:
            logger.warning("Strategy not found")
            return None
        elif e.response.status_code >= 500:
            logger.error(f"Strategy service error: {e}")
            raise
        else:
            logger.warning(f"Client error: {e}")
            raise
            
    except httpx.RequestError as e:
        # 연결 에러 처리
        logger.error(f"Connection error to strategy service: {e}")
        raise
```

### 재시도 패턴

```python
import asyncio
from typing import TypeVar, Callable
from mysingle_quant.core import get_service_http_client, HttpClientConfig

T = TypeVar('T')

async def retry_service_call(
    func: Callable[[], T],
    max_retries: int = HttpClientConfig.DEFAULT_MAX_RETRIES,
    delay: float = HttpClientConfig.DEFAULT_RETRY_DELAY
) -> T:
    """서비스 호출 재시도"""
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            last_exception = e
            if attempt < max_retries:
                await asyncio.sleep(delay * (2 ** attempt))  # 지수 백오프
                continue
            break
        except httpx.HTTPStatusError as e:
            # 5xx 에러만 재시도
            if e.response.status_code >= 500 and attempt < max_retries:
                last_exception = e
                await asyncio.sleep(delay * (2 ** attempt))
                continue
            raise
    
    raise last_exception

# 사용 예시
async def get_strategy_with_retry(strategy_id: str):
    client = get_service_http_client("strategy-service")
    
    async def call():
        response = await client.get(f"/strategies/{strategy_id}")
        response.raise_for_status()
        return response.json()
    
    return await retry_service_call(call)
```

## 성능 모니터링

### 요청 로깅

```python
import time
from mysingle_quant.core import get_service_http_client, get_logger

logger = get_logger(__name__)

async def logged_service_call(service_name: str, method: str, endpoint: str, **kwargs):
    """로깅이 포함된 서비스 호출"""
    client = get_service_http_client(service_name)
    
    start_time = time.time()
    try:
        response = await client.request(method, endpoint, **kwargs)
        duration = time.time() - start_time
        
        logger.info(
            f"Service call: {service_name} {method} {endpoint} "
            f"-> {response.status_code} ({duration:.3f}s)"
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Service call failed: {service_name} {method} {endpoint} "
            f"-> {type(e).__name__}: {e} ({duration:.3f}s)"
        )
        raise
```

## 테스트 지원

### 모킹

```python
import pytest
from unittest.mock import AsyncMock, patch
from mysingle_quant.core import ServiceHttpClientManager

@pytest.fixture
async def mock_strategy_service():
    """Strategy Service 모킹"""
    mock_client = AsyncMock()
    mock_client.get.return_value.json.return_value = {
        "id": "strategy-123",
        "name": "Test Strategy"
    }
    
    with patch.object(ServiceHttpClientManager, 'get_client', return_value=mock_client):
        yield mock_client

async def test_journey_creation(mock_strategy_service):
    """여정 생성 테스트"""
    orchestrator = JourneyOrchestrator()
    
    result = await orchestrator.execute_journey({
        "strategy_id": "strategy-123",
        "backtest_config": {}
    }, "user-456")
    
    assert result["status"] == "started"
    mock_strategy_service.get.assert_called_once()
```

이제 표준화된 HTTP 클라이언트가 완성되었습니다! 🎉
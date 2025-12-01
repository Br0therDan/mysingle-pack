# mysingle.clients

HTTP 및 gRPC 클라이언트 베이스 클래스

## 주요 기능

- `BaseHttpClient`: HTTP 클라이언트 (httpx 기반)
- `BaseGrpcClient`: gRPC 클라이언트 (metadata 자동 전파)

## 사용 예시

```python
from mysingle.clients import BaseGrpcClient
from mysingle_protos.services.strategy.v1 import strategy_service_pb2_grpc

class StrategyClient(BaseGrpcClient):
    def __init__(self, user_id=None, correlation_id=None):
        super().__init__(
            service_name="strategy-service",
            default_port=50051,
            user_id=user_id,
            correlation_id=correlation_id
        )
        self.stub = strategy_service_pb2_grpc.StrategyServiceStub(self.channel)

    async def get_strategy(self, strategy_id: str):
        request = strategy_service_pb2.GetStrategyRequest(id=strategy_id)
        return await self.stub.GetStrategy(request, metadata=self.metadata)
```

## 설치

```bash
pip install mysingle[clients]
```

## 의존성

- httpx, aiohttp
- grpcio

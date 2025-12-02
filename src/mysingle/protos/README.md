# MySingle Protocol Buffers

이 디렉토리는 MySingle 마이크로서비스 간 gRPC 통신에 사용되는 Protocol Buffer 정의로부터 자동 생성된 Python 스텁을 포함합니다.

## 📦 구조

```
mysingle/protos/
├── common/              # 공통 메시지 타입
│   ├── error_pb2.py     # 에러 응답 정의
│   ├── metadata_pb2.py  # 메타데이터 (user-id, correlation-id 등)
│   └── pagination_pb2.py # 페이지네이션 요청/응답
└── services/            # 서비스별 gRPC 정의
    ├── backtest/v1/
    ├── genai/v1/
    ├── iam/v1/
    ├── indicator/v1/
    ├── market_data/v1/
    ├── ml/v1/
    └── strategy/v1/
```

## 🔧 사용법

### 기본 import

```python
from mysingle.protos.common import metadata_pb2, error_pb2, pagination_pb2
from mysingle.protos.services.strategy.v1 import strategy_service_pb2
from mysingle.protos.services.strategy.v1 import strategy_service_pb2_grpc
```

### gRPC 클라이언트 예시

```python
from mysingle.clients import BaseGrpcClient
from mysingle.protos.services.strategy.v1 import (
    strategy_service_pb2,
    strategy_service_pb2_grpc,
)

class StrategyGrpcClient(BaseGrpcClient):
    def __init__(self, user_id=None, correlation_id=None, **kwargs):
        super().__init__(
            service_name="strategy-service",
            default_port=50051,
            user_id=user_id,
            correlation_id=correlation_id,
            **kwargs
        )
        self.stub = strategy_service_pb2_grpc.StrategyServiceStub(self.channel)

    async def get_strategy(self, strategy_id: str):
        request = strategy_service_pb2.GetStrategyRequest(strategy_id=strategy_id)
        return await self.stub.GetStrategy(request, metadata=self.metadata)
```

### gRPC 서버 예시

```python
from mysingle.protos.services.strategy.v1 import (
    strategy_service_pb2,
    strategy_service_pb2_grpc,
)

class StrategyServicer(strategy_service_pb2_grpc.StrategyServiceServicer):
    async def GetStrategy(self, request, context):
        # Extract metadata
        user_id = dict(context.invocation_metadata()).get("user-id")

        # Business logic
        strategy = await get_strategy_from_db(request.strategy_id, user_id)

        return strategy_service_pb2.GetStrategyResponse(
            strategy=strategy
        )
```

## 🔄 재생성

Proto 파일이 변경되면 자동으로 스텁이 재생성됩니다:

### 로컬 재생성 (mysingle-proto CLI 사용)

```bash
# 프로젝트 루트에서
uv run mysingle-proto generate              # Python 스텁 생성
uv run mysingle-proto validate              # Lint + Format 검사
uv run mysingle-proto validate --breaking   # Breaking change 검사
```

### CI/CD 자동 재생성

**통합 워크플로우** (`proto-ci.yml` - 권장):
- Proto 파일 변경 시 자동 실행
- ✅ **Validate**: Lint + Format 검사
- ✅ **Generate**: Python 스텁 자동 생성
- ✅ **Breaking Check**: PR에서 breaking change 검사
- ✅ **Auto-commit**: main/develop push 시 자동 커밋
- ❌ **PR Fail**: PR에서 스텁이 out-of-sync면 실패

**개별 워크플로우**:
- `validate-protos.yml`: 검증만 수행
- `auto-generate-protos.yml`: 생성 + 검증 + Auto-commit

## ⚠️ 주의사항

1. **직접 수정 금지**: 이 디렉토리의 `*_pb2.py`, `*_pb2_grpc.py` 파일은 자동 생성되므로 직접 수정하지 마세요.
2. **소스 위치**: Proto 정의 파일은 `protos/` 디렉토리에 있습니다.
3. **버전 관리**:
   - Proto 버전: `protos/` 디렉토리의 .proto 파일에서 관리
   - 생성된 스텁 버전: `__init__.py`의 `__version__`으로 추적
4. **PR 전 필수**: Proto 파일 수정 시 반드시 `uv run mysingle-proto generate` 실행 후 커밋
5. **CI/CD 검증**: PR에서 스텁이 최신 상태가 아니면 자동으로 실패

## 🚀 개발 워크플로우

### Proto 파일 수정 시

```bash
# 1. Proto 파일 수정
vim protos/services/strategy/v1/strategy_service.proto

# 2. 검증 (옵션)
uv run mysingle-proto validate

# 3. 스텁 재생성
uv run mysingle-proto generate

# 4. 커밋 & 푸시
git add protos/ src/mysingle/protos/
git commit -m "feat: add new strategy API"
git push
```

### CI/CD 플로우

1. **PR 생성** → `proto-ci.yml` 실행
   - ✅ Validate: Lint + Format 통과해야 함
   - ✅ Breaking Check: Breaking change 경고 (continue-on-error)
   - ✅ Generate: 스텁 생성
   - ❌ **Fail if out-of-sync**: 로컬에서 generate 안 했으면 실패

2. **PR 머지 → main** → `proto-ci.yml` 실행
   - ✅ Validate + Generate
   - ✅ Auto-commit: 스텁 변경사항 자동 커밋 (없으면 스킵)

## 🔗 관련 문서

- [mysingle-proto CLI 가이드](../cli/README.md)
- [mysingle.clients 사용법](../clients/README.md)
- [개발 가이드](../../README.md#-개발)

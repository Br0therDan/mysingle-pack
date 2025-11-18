# MySingle

Common utilities and configurations for MySingle Platform microservices.

## 📦 Installation

### Basic Installation
```bash
pip install mysingle
```
Installs only core dependencies (`pydantic`, `pydantic-settings`).

### Feature-specific Installation
```bash
# Authentication features
pip install mysingle[auth]

# Web framework features
pip install mysingle[web]

# Database features
pip install mysingle[database]

# Email features
pip install mysingle[email]

# Monitoring features
pip install mysingle[monitoring]

# DSL runtime features
pip install mysingle[dsl]

# All features
pip install mysingle[full]

# Development tools
pip install mysingle[dev]
```

### Combined Installation
```bash
# Web + Auth + Database
pip install mysingle[web,auth,database]

# Full features + development tools
pip install mysingle[full,dev]
```

## 🚀 Quick Start

### Basic Usage
```python
from mysingle.core import create_fastapi_app
from mysingle.core.config import settings

# Create FastAPI app with common configurations
app = create_fastapi_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🧭 Imports: 권장 경로

루트 재노출은 유지되지만, 서브패키지 경로를 사용하면 순환참조를 피하고 초기화 비용을 줄일 수 있습니다.

- Core (루트에서도 노출 유지)
    - 권장: `from mysingle.core import create_fastapi_app, CommonSettings, settings, get_settings, init_mongo, get_mongodb_url, get_database_name`
    - 루트도 가능: `from mysingle import create_fastapi_app, CommonSettings, settings, get_settings, init_mongo, get_mongodb_url, get_database_name`

- Logging
    - 권장: `from mysingle.logging import get_logger, setup_logging, configure_structured_logging`
    - 루트도 가능: `from mysingle import get_logger`

- Database
    - 권장: `from mysingle.database import BaseDuckDBManager`
    - 루트도 가능: `from mysingle import BaseDuckDBManager`

- Clients
    - 권장: `from mysingle.clients import BaseServiceClient`
    - 루트도 가능: `from mysingle import BaseServiceClient`

- DSL
    - 권장: `from mysingle.dsl import DSLParser, DSLExecutor, SecurityValidator, ResourceLimits`
    - 루트도 가능: `from mysingle import DSLParser, DSLExecutor, SecurityValidator, ResourceLimits`

루트 패키지(`mysingle`)는 지연 로딩(lazy export)으로 구성되어 있어, 심볼 접근 시점에만 서브패키지를 가져옵니다.

### With Authentication
```python
from mysingle.core import create_fastapi_app
from mysingle.auth import get_user_manager
from mysingle.auth.router import auth_router

app = create_fastapi_app()
app.include_router(auth_router, prefix="/auth")
```

### With Database
```python
from mysingle.core import create_fastapi_app
from mysingle.core.db import init_db

app = create_fastapi_app()

@app.on_event("startup")
async def startup():
    await init_db()
```

### With DSL Runtime
```python
from mysingle.dsl import DSLParser, DSLExecutor
import pandas as pd

# Parse and compile DSL code
parser = DSLParser()
bytecode = parser.parse("result = sma(close, 20)")

# Execute with data
executor = DSLExecutor()
data = pd.DataFrame({"close": [100, 102, 105, 103, 107]})
result = executor.execute(bytecode, data={"close": data["close"]})
print(result["result"])  # 20-period SMA
```

## 📋 Features

- **🔐 Authentication**: JWT-based auth with OAuth support
- **🌐 Web Framework**: FastAPI with common configurations
- **🗄️ Database**: MongoDB with Beanie ODM
- **📧 Email**: Template-based email system
- **📊 Monitoring**: Prometheus metrics and structured logging
- **⚙️ Configuration**: Pydantic-based settings management
- **🔧 DSL Runtime**: Secure Python DSL execution engine for user-defined indicators and strategies
- **🔑 Standard Constants**: HTTP headers and environment variable naming conventions

## 🔑 Standard Constants

모든 마이크로서비스에서 일관된 헤더 및 환경 변수 사용을 위한 표준 상수를 제공합니다.

### HTTP 헤더 상수

```python
from mysingle.constants import (
    # Kong Gateway 원본 헤더
    HEADER_KONG_USER_ID,         # "X-Consumer-Custom-ID" (JWT sub 클레임)
    HEADER_KONG_CONSUMER_ID,     # "X-Consumer-ID"
    HEADER_KONG_REQUEST_ID,      # "X-Kong-Request-Id"
    HEADER_CORRELATION_ID,       # "X-Correlation-Id"

    # 서비스 간 전파용 헤더
    HEADER_USER_ID,              # "X-User-Id" (다운스트림 전파)
    HEADER_AUTHORIZATION,        # "Authorization"
)

# 사용 예시
headers = {
    HEADER_AUTHORIZATION: f"Bearer {token}",
    HEADER_USER_ID: user_id,
    HEADER_CORRELATION_ID: correlation_id,
}
```

### gRPC 메타데이터 상수

```python
from mysingle.constants import (
    GRPC_METADATA_USER_ID,       # "user_id"
    GRPC_METADATA_AUTHORIZATION, # "authorization"
    GRPC_METADATA_CORRELATION_ID,# "correlation_id"
)

# 사용 예시
metadata = [
    (GRPC_METADATA_USER_ID, user_id),
    (GRPC_METADATA_CORRELATION_ID, correlation_id),
]
```

### 환경 변수 네이밍 규칙

```python
from mysingle.constants import (
    HTTP_CLIENT_MAX_CONNECTIONS,  # "HTTP_CLIENT_MAX_CONNECTIONS"
    HTTP_CLIENT_TIMEOUT,           # "HTTP_CLIENT_TIMEOUT"
    ENV_TEST_ALLOW_SIMPLE_USER,   # "TEST_ALLOW_SIMPLE_USER"
)

# 서비스별 gRPC 설정 패턴
# USE_GRPC_FOR_<SERVICE_NAME>
# <SERVICE_NAME>_GRPC_HOST
# <SERVICE_NAME>_GRPC_PORT
```

### BaseServiceClient 표준 사용법

```python
from mysingle.clients import BaseServiceClient
from fastapi import Request

class MyServiceClient(BaseServiceClient):
    def __init__(self, request: Request | None = None):
        super().__init__(
            service_name="my-service",
            default_port=8001,
            request=request,  # JWT와 X-User-Id 자동 전파
        )

    async def get_data(self) -> dict:
        return await self._request("GET", "/api/v1/data")

# 엔드포인트에서 사용
@router.get("/endpoint")
async def endpoint(request: Request):
    async with MyServiceClient(request=request) as client:
        # request에서 Authorization, X-User-Id 자동 추출 및 전파
        data = await client.get_data()
    return data
```

## � gRPC Interceptors

gRPC 서비스에서 인증, 로깅, 메타데이터 전파를 위한 표준 인터셉터를 제공합니다.

### 서버 인터셉터 적용

```python
import grpc
from mysingle.grpc import AuthInterceptor, LoggingInterceptor, MetadataInterceptor

# gRPC 서버 생성 시 인터셉터 적용
async def serve():
    server = grpc.aio.server(
        interceptors=[
            AuthInterceptor(
                require_auth=True,
                exempt_methods=["/health/Check", "/health/Ready"]
            ),
            MetadataInterceptor(auto_generate=True),
            LoggingInterceptor(),
        ]
    )

    # servicer 등록
    my_pb2_grpc.add_MyServiceServicer_to_server(MyServiceServicer(), server)

    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()
```

### 클라이언트 인터셉터 적용

```python
from mysingle.grpc import ClientAuthInterceptor

async def call_grpc_service(user_id: str, correlation_id: str | None = None):
    async with grpc.aio.insecure_channel(
        'strategy-service:50051',
        interceptors=[
            ClientAuthInterceptor(
                user_id=user_id,
                correlation_id=correlation_id
            )
        ]
    ) as channel:
        stub = strategy_pb2_grpc.StrategyServiceStub(channel)
        response = await stub.GetStrategy(request)
        return response
```

### 메타데이터 표준

모든 gRPC 호출은 아래 메타데이터를 전파합니다:

```python
from mysingle.constants import (
    GRPC_METADATA_USER_ID,        # "user_id" (필수)
    GRPC_METADATA_CORRELATION_ID, # "correlation_id" (선택, 자동 생성)
    GRPC_METADATA_REQUEST_ID,     # "request_id" (선택, 자동 생성)
)
```

**주의사항:**
- `user_id`는 모든 gRPC 호출에 필수입니다.
- `AuthInterceptor`는 `user_id` 누락 시 `UNAUTHENTICATED` 에러를 반환합니다.
- 개발/테스트 환경에서는 `require_auth=False`로 인증을 비활성화할 수 있습니다.

## �📝 Available Dependencies by Feature

### Core (always installed)
- `pydantic>=2.5.0`
- `pydantic-settings>=2.1.0`

### Auth
- `httpx-oauth>=0.16.1`
- `pyjwt>=2.10.1`
- `pwdlib>=0.2.1`

### Web
- `fastapi>=0.104.1`
- `uvicorn[standard]>=0.24.0`
- `python-multipart>=0.0.6`

### Database
- `motor>=3.3.2`
- `beanie>=1.23.6`
- `redis>=6.4.0`

### Email
- `emails>=0.6`
- `jinja2>=3.1.6`

### Monitoring
- `prometheus-client>=0.19.0`
- `structlog>=23.2.0`

### DSL
- `RestrictedPython>=7.4`
- `pandas>=2.1.4`
- `numpy>=1.24.0`

## 🛠️ Development

```bash
# Clone repository
git clone <repo-url>
cd quant-pack

# Install with development dependencies
pip install -e .[full,dev]

# Run tests
pytest

# Format code
black src/
ruff check src/ --fix

# Type checking
mypy src/mysingle/
```

## 🔖 Release & Versioning

CI는 기본적으로 Conventional Commits를 파싱해 자동으로 다음 버전을 결정(major/minor/patch)합니다. 하지만 릴리스 전에 수동으로 버전을 지정하고 싶다면, 제공된 대화형 스크립트를 사용하세요. 이 스크립트로 직접 버전을 올리면 CI의 자동 버전 결정은 스킵됩니다(수동 변경 우선).

### 대화형 버전 업 스크립트 사용법

```bash
python scripts/bump_version.py
```

- 현재 버전을 읽어와 bump 종류(major/minor/patch/custom)를 선택할 수 있습니다.
- 옵션으로 main 브랜치 전환/최신 반영, 커밋/태그 생성, 원격 푸시까지 지원합니다.
- 커밋 메시지는 `chore(release): vX.Y.Z (bump <type>)` 형태로 생성됩니다.
- pyproject.toml의 `project.version`이 변경되므로, 같은 커밋에서 다시 자동 버전 올리기를 하지 않습니다.

권장 플로우(수동 릴리스):

1) 테스트/검토 완료 → 2) `python scripts/bump_version.py` 실행 → 3) 커밋/태그/푸시 → 4) CI가 빌드/퍼블리시 수행(수동 버전 유지)

## �️ Roadmap

### Phase 1: Enhanced Developer Experience (Current)
- [ ] **DI Functions Compatibility**: Add `Depends()` wrapper functions for backward compatibility
- [ ] **ServiceConfig Extensions**: Add ServiceCategory enum and internal routes flag
- [ ] **Configuration Documentation**: Create inheritance pattern templates for services

### Phase 2: Advanced Architecture (Q4 2024)
- [ ] **Service Templates**: Generate service-specific configuration templates
- [ ] **Service Type Expansion**: Add ORCHESTRATOR, EXECUTION, DATA, ANALYTICS, UTILITY types
- [ ] **Enhanced Routing**: Support for internal vs external API separation

### Phase 3: Developer Tools (Q1 2025)
- [ ] **CLI Tools**: Service generator and validator commands
- [ ] **Testing Utilities**: Enhanced auth helpers and service testing framework
- [ ] **Auto Documentation**: Generate service documentation from configuration

### Completed Features ✅
- **App Factory Standardization**: Unified FastAPI app creation with automatic middleware setup
- **HTTP Client Pooling**: Standardized service-to-service communication with connection pooling
- **Structured Logging**: JSON logging with correlation ID support and context management
- **Kong Gateway Integration**: Complete header standardization and authentication flow
- **Metrics Collection**: Prometheus-compatible metrics with performance monitoring
- **Audit Logging**: Comprehensive request/response logging system

### Migration Status
- [x] All services using App Factory pattern
- [x] HTTP client standardization implemented
- [x] Kong Gateway headers standardized
- [x] Structured logging system deployed
- [ ] CommonSettings inheritance pattern adoption
- [ ] Request-based DI pattern migration
- [ ] Test code updates
- [ ] Environment configuration migration

## �📄 License

This project is licensed under the MIT License.

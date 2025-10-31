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

## 📋 Features

- **🔐 Authentication**: JWT-based auth with OAuth support
- **🌐 Web Framework**: FastAPI with common configurations
- **🗄️ Database**: MongoDB with Beanie ODM
- **📧 Email**: Template-based email system
- **📊 Monitoring**: Prometheus metrics and structured logging
- **⚙️ Configuration**: Pydantic-based settings management

## 📝 Available Dependencies by Feature

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

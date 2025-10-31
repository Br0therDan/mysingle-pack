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

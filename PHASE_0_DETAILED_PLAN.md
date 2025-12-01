# Phase 0: 패키지 구조 재편 상세 작업 계획서

**목표**: mysingle 패키지 구조 최적화 (core 모듈 통합 및 문서화 개선)
**예상 기간**: 2-3일
**전제조건**: 현재 mysingle v1.6.1 설치 및 동작 중

---

## 📋 작업 개요

### 핵심 목표
1. **Core 모듈 통합**: base, logging, metrics, health, email, audit → core/
2. **문서 구조 개선**: 루트 가이드 → docs/ + 서브패키지 README
3. **의존성 최적화**: pyproject.toml 재구성
4. **Import 경로 자동 수정**: 전체 패키지 및 서비스 업데이트

### 성공 기준
- ✅ 모든 모듈이 core로 이동 완료
- ✅ 순환 의존성 없음
- ✅ 모든 테스트 통과
- ✅ 서브패키지별 README.md 생성 (7개)
- ✅ pyproject.toml 업데이트 완료

---

## 🗂️ 이동 대상 모듈 상세

### 1. base/ → core/base/
**현재 구조:**
```
src/mysingle/base/
├── __init__.py
├── documents.py        # BaseDoc, BaseTimeDoc, BaseTimeDocWithUserId
└── schemas.py          # BaseResponseSchema
```

**이동 후:**
```
src/mysingle/core/base/
├── __init__.py
├── documents.py
└── schemas.py
```

**주요 내용:**
- Beanie ODM 기본 문서 클래스
- 공통 응답 스키마
- 의존성: motor, beanie

---

### 2. logging/ → core/logging.py
**현재 구조:**
```
src/mysingle/logging/
├── __init__.py
├── config.py           # setup_logging()
└── middleware.py       # FastAPI 미들웨어
```

**통합 후:**
```
src/mysingle/core/logging.py
```

**주요 함수:**
- `setup_logging(service_name: str, log_level: str) -> None`
- `get_logger(name: str) -> BoundLogger`
- `LoggingMiddleware` (FastAPI 미들웨어)

**의존성:** structlog, colorlog

---

### 3. metrics/ → core/metrics.py
**현재 구조:**
```
src/mysingle/metrics/
├── __init__.py
└── prometheus.py       # Prometheus 메트릭 유틸
```

**통합 후:**
```
src/mysingle/core/metrics.py
```

**주요 함수:**
- `track_request_duration()`
- `increment_counter()`
- `set_gauge()`

**의존성:** prometheus-client

---

### 4. health/ → core/health.py
**현재 구조:**
```
src/mysingle/health/
├── __init__.py
└── checks.py           # 헬스체크 엔드포인트
```

**통합 후:**
```
src/mysingle/core/health.py
```

**주요 함수:**
- `register_health_routes(app: FastAPI) -> None`
- `mongodb_health_check() -> dict`
- `redis_health_check() -> dict`

**의존성:** 없음 (FastAPI 사용)

---

### 5. email/ → core/email.py
**현재 구조:**
```
src/mysingle/email/
├── __init__.py
└── sender.py           # 이메일 발송 유틸
```

**통합 후:**
```
src/mysingle/core/email.py
```

**주요 함수:**
- `send_email(to: str, subject: str, body: str) -> bool`
- `send_template_email(to: str, template: str, context: dict) -> bool`

**의존성:** emails, jinja2

---

### 6. audit/ → core/audit.py
**현재 구조:**
```
src/mysingle/audit/
├── __init__.py
└── logger.py           # 감사 로그 전송
```

**통합 후:**
```
src/mysingle/core/audit.py
```

**주요 함수:**
- `log_audit_event(event_type: str, user_id: str, details: dict) -> None`
- `AuditLogMiddleware` (FastAPI 미들웨어)

**의존성:** httpx

---

## 🛠️ 작업 단계

### Step 1: 백업 및 브랜치 생성 (10분)

```bash
cd /Users/donghakim/mysingle-quant/packages/quant-pack

# 현재 상태 백업
git add -A
git commit -m "chore: backup before Phase 0 restructure"

# 작업 브랜치 생성
git checkout -b feat/phase-0-package-restructure

# 작업 디렉터리 생성
mkdir -p scripts/phase-0
```

---

### Step 2: 자동화 스크립트 작성 (30분)

#### 2.1 디렉터리 재구성 스크립트

**scripts/phase-0/restructure_package.sh:**
```bash
#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC_DIR="$PACKAGE_ROOT/src/mysingle"

echo "=== Phase 0: Package Restructure ==="
echo "Package root: $PACKAGE_ROOT"
echo "Source dir: $SRC_DIR"

# 1. base → core/base 이동
echo "[1/6] Moving base/ to core/base/"
if [ -d "$SRC_DIR/base" ]; then
    mv "$SRC_DIR/base" "$SRC_DIR/core/base"
    echo "  ✓ base/ moved to core/base/"
else
    echo "  ⚠ base/ not found, skipping"
fi

# 2. logging → core/logging.py 통합
echo "[2/6] Merging logging/ to core/logging.py"
if [ -d "$SRC_DIR/logging" ]; then
    cat > "$SRC_DIR/core/logging.py" << 'EOF'
"""Logging utilities for MySingle Platform.

Consolidated from mysingle.logging module.
"""

from .logging_impl import (
    setup_logging,
    get_logger,
    LoggingMiddleware,
)

__all__ = [
    "setup_logging",
    "get_logger",
    "LoggingMiddleware",
]
EOF

    # logging/ 내용을 core/logging_impl.py로 복사
    cat "$SRC_DIR/logging/config.py" "$SRC_DIR/logging/middleware.py" > "$SRC_DIR/core/logging_impl.py"

    # 원본 삭제
    rm -rf "$SRC_DIR/logging"
    echo "  ✓ logging/ merged to core/logging.py"
else
    echo "  ⚠ logging/ not found, skipping"
fi

# 3. metrics → core/metrics.py
echo "[3/6] Merging metrics/ to core/metrics.py"
if [ -d "$SRC_DIR/metrics" ]; then
    cp "$SRC_DIR/metrics/prometheus.py" "$SRC_DIR/core/metrics.py"
    rm -rf "$SRC_DIR/metrics"
    echo "  ✓ metrics/ merged to core/metrics.py"
else
    echo "  ⚠ metrics/ not found, skipping"
fi

# 4. health → core/health.py
echo "[4/6] Merging health/ to core/health.py"
if [ -d "$SRC_DIR/health" ]; then
    cp "$SRC_DIR/health/checks.py" "$SRC_DIR/core/health.py"
    rm -rf "$SRC_DIR/health"
    echo "  ✓ health/ merged to core/health.py"
else
    echo "  ⚠ health/ not found, skipping"
fi

# 5. email → core/email.py
echo "[5/6] Merging email/ to core/email.py"
if [ -d "$SRC_DIR/email" ]; then
    cp "$SRC_DIR/email/sender.py" "$SRC_DIR/core/email.py"
    rm -rf "$SRC_DIR/email"
    echo "  ✓ email/ merged to core/email.py"
else
    echo "  ⚠ email/ not found, skipping"
fi

# 6. audit → core/audit.py
echo "[6/6] Merging audit/ to core/audit.py"
if [ -d "$SRC_DIR/audit" ]; then
    cp "$SRC_DIR/audit/logger.py" "$SRC_DIR/core/audit.py"
    rm -rf "$SRC_DIR/audit"
    echo "  ✓ audit/ merged to core/audit.py"
else
    echo "  ⚠ audit/ not found, skipping"
fi

echo ""
echo "=== Restructure Complete ==="
echo "Next: Run update_internal_imports.py"
```

#### 2.2 Import 경로 수정 스크립트

**scripts/phase-0/update_internal_imports.py:**
```python
#!/usr/bin/env python3
"""
Import 경로 자동 수정 스크립트
mysingle.base → mysingle.core.base
mysingle.logging → mysingle.core.logging
등으로 일괄 변경
"""

import re
from pathlib import Path
from typing import Dict, List

# Import 매핑 테이블
IMPORT_MAPPINGS = {
    "from mysingle.base import": "from mysingle.core.base import",
    "from mysingle.base.": "from mysingle.core.base.",
    "import mysingle.base": "import mysingle.core.base",

    "from mysingle.logging import": "from mysingle.core.logging import",
    "from mysingle.logging.": "from mysingle.core.logging.",
    "import mysingle.logging": "import mysingle.core.logging",

    "from mysingle.metrics import": "from mysingle.core.metrics import",
    "from mysingle.metrics.": "from mysingle.core.metrics.",
    "import mysingle.metrics": "import mysingle.core.metrics",

    "from mysingle.health import": "from mysingle.core.health import",
    "from mysingle.health.": "from mysingle.core.health.",
    "import mysingle.health": "import mysingle.core.health",

    "from mysingle.email import": "from mysingle.core.email import",
    "from mysingle.email.": "from mysingle.core.email.",
    "import mysingle.email": "import mysingle.core.email",

    "from mysingle.audit import": "from mysingle.core.audit import",
    "from mysingle.audit.": "from mysingle.core.audit.",
    "import mysingle.audit": "import mysingle.core.audit",
}


def update_file_imports(file_path: Path) -> int:
    """파일의 import 구문을 업데이트합니다."""
    content = file_path.read_text(encoding="utf-8")
    original_content = content
    changes = 0

    for old_import, new_import in IMPORT_MAPPINGS.items():
        if old_import in content:
            content = content.replace(old_import, new_import)
            changes += 1

    if content != original_content:
        file_path.write_text(content, encoding="utf-8")
        return changes

    return 0


def find_python_files(root_dir: Path, exclude_dirs: List[str]) -> List[Path]:
    """Python 파일 목록을 찾습니다."""
    python_files = []

    for py_file in root_dir.rglob("*.py"):
        # 제외 디렉터리 체크
        if any(excl in str(py_file) for excl in exclude_dirs):
            continue
        python_files.append(py_file)

    return python_files


def main():
    # quant-pack 루트 찾기
    script_dir = Path(__file__).parent
    package_root = script_dir.parent.parent
    src_dir = package_root / "src" / "mysingle"

    print("=== Phase 0: Update Internal Imports ===")
    print(f"Package root: {package_root}")
    print(f"Source dir: {src_dir}")
    print()

    # mysingle 패키지 내부 파일 수정
    exclude_dirs = [".venv", "__pycache__", ".pytest_cache", ".mypy_cache", "logs"]
    python_files = find_python_files(src_dir, exclude_dirs)

    print(f"Found {len(python_files)} Python files in mysingle package")

    total_changes = 0
    updated_files = []

    for py_file in python_files:
        changes = update_file_imports(py_file)
        if changes > 0:
            total_changes += changes
            updated_files.append(py_file)
            print(f"  ✓ {py_file.relative_to(package_root)} ({changes} changes)")

    print()
    print(f"=== Summary ===")
    print(f"Updated {len(updated_files)} files")
    print(f"Total {total_changes} import statements changed")
    print()
    print("Next: Update __init__.py exports")


if __name__ == "__main__":
    main()
```

#### 2.3 서브패키지 README 생성 스크립트

**scripts/phase-0/generate_package_readmes.py:**
```python
#!/usr/bin/env python3
"""
서브패키지별 README.md 자동 생성 스크립트
"""

from pathlib import Path
from typing import Dict

README_TEMPLATES = {
    "core": """# mysingle.core

핵심 유틸리티 모듈 (통합)

## 포함 모듈

### settings.py
- `CommonSettings`: 공통 설정 클래스
- 환경 변수 기반 설정 관리

### app_factory.py
- `create_app()`: FastAPI 앱 팩토리
- 미들웨어, 라우터, CORS 자동 설정

### constants.py
- 전역 상수 정의
- 서비스 이름, 포트, 타임아웃 등

### logging.py
- `setup_logging()`: 로깅 초기화
- `get_logger()`: 구조화된 로거 반환
- `LoggingMiddleware`: 요청/응답 로깅

### metrics.py
- `track_request_duration()`: 요청 시간 추적
- `increment_counter()`: 카운터 증가
- Prometheus 메트릭 유틸리티

### health.py
- `register_health_routes()`: 헬스체크 엔드포인트 등록
- MongoDB, Redis 상태 체크

### email.py
- `send_email()`: 이메일 발송
- `send_template_email()`: 템플릿 기반 발송

### audit.py
- `log_audit_event()`: 감사 로그 전송
- `AuditLogMiddleware`: 요청 감사 로깅

### base/
- `BaseDoc`, `BaseTimeDoc`, `BaseTimeDocWithUserId`: Beanie 문서 클래스
- `BaseResponseSchema`: 공통 응답 스키마

## 사용 예시

```python
from mysingle.core import get_logger, CommonSettings, create_app
from mysingle.core.base import BaseTimeDocWithUserId

# 로깅
logger = get_logger(__name__)
logger.info("Application started", extra={"version": "1.0.0"})

# 설정
settings = CommonSettings()
print(settings.SERVICE_NAME)

# FastAPI 앱 생성
app = create_app(
    service_name="my-service",
    version="1.0.0",
    enable_cors=True
)

# Beanie 문서
class User(BaseTimeDocWithUserId):
    name: str
    email: str
```

## 의존성

설치: `pip install mysingle` (core는 기본 포함)

- pydantic
- structlog, colorlog
- prometheus-client
- motor, beanie
- emails, jinja2
- httpx
""",

    "auth": """# mysingle.auth

인증 및 인가 모듈

## 주요 기능

- JWT 토큰 발급/검증
- Kong Gateway 통합
- OAuth 2.0 지원
- 비밀번호 해싱 (Argon2, Bcrypt)

## 사용 예시

```python
from mysingle.auth import (
    get_current_user,
    get_current_active_verified_user,
    get_kong_user_id,
)

@router.get("/me")
async def get_me(user: User = Depends(get_current_active_verified_user)):
    return user

@router.get("/profile")
async def get_profile(user_id: str = Depends(get_kong_user_id)):
    return {"user_id": user_id}
```

## 설치

```bash
pip install mysingle[auth]
```

## 의존성

- PyJWT
- pwdlib[argon2,bcrypt]
- httpx-oauth
""",

    "database": """# mysingle.database

데이터베이스 유틸리티

## 주요 기능

- MongoDB 연결 관리 (Beanie ODM)
- DuckDB 쿼리 실행
- Redis 캐싱

## 사용 예시

```python
from mysingle.database import init_mongodb, get_duckdb_connection

# MongoDB
await init_mongodb(
    connection_string="mongodb://localhost:27017",
    database_name="mydb"
)

# DuckDB
conn = get_duckdb_connection("data.duckdb")
result = conn.execute("SELECT * FROM table").fetchall()
```

## 설치

```bash
pip install mysingle[database]
```

## 의존성

- motor, beanie (기본 포함)
- duckdb
- redis
""",

    "dsl": """# mysingle.dsl

도메인 특화 언어 (DSL) 파서 및 실행 엔진

## 주요 기능

- 전략 DSL 파싱
- 지표 계산 실행
- 백테스팅 스크립트 검증

## 사용 예시

```python
from mysingle.dsl import parse_strategy, execute_indicator

# 전략 파싱
strategy = parse_strategy(\"\"\"
WHEN close > sma(close, 20)
THEN buy(100)
\"\"\")

# 지표 실행
result = execute_indicator("sma", data=df, period=20)
```

## 설치

```bash
pip install mysingle[dsl]
```

## 의존성

- RestrictedPython
- pandas, numpy
""",

    "clients": """# mysingle.clients

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
""",

    "protos": """# mysingle.protos

gRPC Protocol Buffers (자동 생성)

## 구조

- `common/`: 공통 메시지 (metadata, error)
- `services/`: 서비스별 proto
  - `strategy/v1/`
  - `indicator/v1/`
  - `market_data/v1/`
  - `genai/v1/`
  - `ml/v1/`

## 사용 예시

```python
from mysingle.protos.services.strategy.v1 import strategy_service_pb2
from mysingle.protos.common import metadata_pb2

# 메시지 생성
request = strategy_service_pb2.GetStrategyRequest(id="strategy-123")

# 메타데이터
metadata = metadata_pb2.RequestMetadata(
    user_id="user-456",
    correlation_id="corr-789"
)
```

## 설치

```bash
pip install mysingle[grpc]
```

## 의존성

- grpcio
- protobuf

## 버전 관리

Proto 버전은 `mysingle.protos.__version__`에서 확인:

```python
from mysingle.protos import __version__
print(__version__)  # 예: "v1.2.0"
```
""",

    "cli": """# mysingle.cli

명령줄 도구

## 주요 기능

### mysingle-proto
Proto 파일 관리 CLI

```bash
# Proto 초기화
mysingle-proto init

# Proto 검증
mysingle-proto validate

# Proto 생성
mysingle-proto generate

# Proto 버전 확인
mysingle-proto version
```

### mysingle-cli (향후)
기타 유틸리티 CLI

## 설치

CLI는 전체 설치 시 포함:

```bash
pip install mysingle[full]
```

## 의존성

- buf (외부 도구)
- grpcio-tools
""",
}


def generate_readmes(package_root: Path):
    """서브패키지 README 생성"""
    src_dir = package_root / "src" / "mysingle"

    print("=== Phase 0: Generate Subpackage READMEs ===")
    print(f"Source dir: {src_dir}")
    print()

    created = 0
    for module_name, readme_content in README_TEMPLATES.items():
        module_dir = src_dir / module_name

        if not module_dir.exists():
            print(f"  ⚠ {module_name}/ not found, skipping")
            continue

        readme_path = module_dir / "README.md"
        readme_path.write_text(readme_content.strip() + "\n", encoding="utf-8")
        print(f"  ✓ Created {readme_path.relative_to(package_root)}")
        created += 1

    print()
    print(f"=== Summary ===")
    print(f"Created {created} README.md files")
    print()
    print("Next: Update root README.md")


if __name__ == "__main__":
    from pathlib import Path
    script_dir = Path(__file__).parent
    package_root = script_dir.parent.parent
    generate_readmes(package_root)
```

---

### Step 3: 스크립트 실행 (30분)

```bash
cd /Users/donghakim/mysingle-quant/packages/quant-pack

# 1. 디렉터리 재구성
chmod +x scripts/phase-0/restructure_package.sh
./scripts/phase-0/restructure_package.sh

# 2. Import 경로 수정
chmod +x scripts/phase-0/update_internal_imports.py
./scripts/phase-0/update_internal_imports.py

# 3. 서브패키지 README 생성
chmod +x scripts/phase-0/generate_package_readmes.py
./scripts/phase-0/generate_package_readmes.py

# 4. 중간 커밋
git add -A
git commit -m "feat(phase-0): restructure package (base, logging, metrics, health, email, audit → core)"
```

---

### Step 4: core/__init__.py 업데이트 (20분)

**src/mysingle/core/__init__.py:**
```python
"""
mysingle.core - Core utilities for MySingle Platform

Consolidated module containing:
- settings: Configuration management
- app_factory: FastAPI application factory
- constants: Global constants
- logging: Structured logging
- metrics: Prometheus metrics
- health: Health check endpoints
- email: Email utilities
- audit: Audit logging
- base: Beanie document base classes
"""

from .settings import CommonSettings
from .app_factory import create_app
from .constants import *

# Logging
from .logging import (
    setup_logging,
    get_logger,
    LoggingMiddleware,
)

# Metrics
from .metrics import (
    track_request_duration,
    increment_counter,
    set_gauge,
)

# Health
from .health import (
    register_health_routes,
    mongodb_health_check,
    redis_health_check,
)

# Email
from .email import (
    send_email,
    send_template_email,
)

# Audit
from .audit import (
    log_audit_event,
    AuditLogMiddleware,
)

# Base (nested)
from .base.documents import (
    BaseDoc,
    BaseTimeDoc,
    BaseTimeDocWithUserId,
)
from .base.schemas import (
    BaseResponseSchema,
)

__all__ = [
    # Settings & Factory
    "CommonSettings",
    "create_app",

    # Logging
    "setup_logging",
    "get_logger",
    "LoggingMiddleware",

    # Metrics
    "track_request_duration",
    "increment_counter",
    "set_gauge",

    # Health
    "register_health_routes",
    "mongodb_health_check",
    "redis_health_check",

    # Email
    "send_email",
    "send_template_email",

    # Audit
    "log_audit_event",
    "AuditLogMiddleware",

    # Base
    "BaseDoc",
    "BaseTimeDoc",
    "BaseTimeDocWithUserId",
    "BaseResponseSchema",
]
```

---

### Step 5: 루트 __init__.py 업데이트 (20분)

**src/mysingle/__init__.py:**
```python
"""
MySingle Platform Unified Package

통합 패키지: mysingle + mysingle-protos

모듈 구조:
- core: 핵심 유틸리티 (settings, logging, metrics, health, email, audit, base)
- auth: 인증/인가 [선택]
- database: 데이터베이스 [선택]
- dsl: DSL 파서 [선택]
- clients: HTTP/gRPC 클라이언트 [선택]
- protos: gRPC Proto 생성 코드 [선택]
- cli: CLI 도구 [선택]
"""

__version__ = "2.0.0"

import sys
from typing import Any


# Lazy loading을 위한 모듈 매핑
_LAZY_MODULES = {
    # Core (항상 사용 가능)
    "core": "mysingle.core",

    # Optional modules
    "auth": "mysingle.auth",
    "database": "mysingle.database",
    "dsl": "mysingle.dsl",
    "clients": "mysingle.clients",
    "protos": "mysingle.protos",
    "cli": "mysingle.cli",
}


# Core 주요 함수는 직접 노출 (lazy 아님)
from mysingle.core import (
    CommonSettings,
    create_app,
    get_logger,
    setup_logging,
    BaseDoc,
    BaseTimeDoc,
    BaseTimeDocWithUserId,
    BaseResponseSchema,
)


__all__ = [
    # Version
    "__version__",

    # Core exports
    "CommonSettings",
    "create_app",
    "get_logger",
    "setup_logging",
    "BaseDoc",
    "BaseTimeDoc",
    "BaseTimeDocWithUserId",
    "BaseResponseSchema",

    # Lazy modules
    "core",
    "auth",
    "database",
    "dsl",
    "clients",
    "protos",
    "cli",
]


def __getattr__(name: str) -> Any:
    """PEP 562: Lazy module loading"""
    if name in _LAZY_MODULES:
        module_path = _LAZY_MODULES[name]
        try:
            module = __import__(module_path, fromlist=[""])
            globals()[name] = module
            return module
        except ImportError as e:
            raise ImportError(
                f"Module '{name}' requires optional dependencies. "
                f"Install with: pip install mysingle[{name}]"
            ) from e

    raise AttributeError(f"module 'mysingle' has no attribute '{name}'")
```

---

### Step 6: pyproject.toml 업데이트 (15분)

**pyproject.toml** (dependencies 섹션만):
```toml
dependencies = [
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    # Core 통합 모듈 의존성
    "structlog>=23.2.0",           # logging
    "colorlog>=6.9.0",             # logging
    "prometheus-client>=0.19.0",   # metrics
    "motor>=3.3.2",                # base.documents (Beanie)
    "beanie>=1.23.6",              # base.documents
    "emails>=0.6",                 # email
    "jinja2>=3.1.6",               # email
    "httpx>=0.25.2",               # audit
]
```

커밋:
```bash
git add pyproject.toml src/mysingle/__init__.py src/mysingle/core/__init__.py
git commit -m "feat(phase-0): update package exports and dependencies"
```

---

### Step 7: 루트 문서 재구성 (30분)

```bash
cd /Users/donghakim/mysingle-quant/packages/quant-pack

# docs/ 디렉터리 생성
mkdir -p docs

# 기존 가이드 이동
mv MYSINGLE_APP_FACTORY_USAGE_GUIDE.md docs/
mv MYSINGLE_DSL_USAGE_GUIDE.md docs/
mv MYSINGLE_PACK_USAGE_GUIDE.md docs/
mv FRONTEND_AUTH_DEV_GUIDE.md docs/
mv MYSINGLE_APP_FACTORY_FLOWCHART.md docs/

# AGENTS.md는 유지 (루트에 필요)
# copilot-instructions.md도 유지

git add -A
git commit -m "docs: move guides to docs/ directory"
```

**새 README.md 작성:**
```markdown
# MySingle - Unified Platform Package

**Version**: 2.0.0
**Repository**: https://github.com/Br0therDan/mysingle-pack.git

MySingle + gRPC Protos 통합 패키지

---

## 📦 설치

### 최소 설치 (core만)
```bash
pip install mysingle
```

### 선택적 설치
```bash
# 인증 필요
pip install mysingle[auth]

# 웹 서비스 (FastAPI)
pip install mysingle[web]

# 데이터베이스
pip install mysingle[database]

# gRPC
pip install mysingle[grpc]

# 조합형
pip install mysingle[common]        # auth + database + web
pip install mysingle[common-grpc]   # common + grpc + clients
pip install mysingle[full]          # 전체
```

---

## 📚 모듈 구조

| 모듈     | 설명                                  | 설치         |
| -------- | ------------------------------------- | ------------ |
| **core** | 핵심 유틸리티 (설정, 로깅, 메트릭 등) | 기본 포함    |
| auth     | 인증/인가 (JWT, Kong)                 | `[auth]`     |
| database | MongoDB, DuckDB, Redis                | `[database]` |
| dsl      | 전략 DSL 파서                         | `[dsl]`      |
| clients  | HTTP/gRPC 클라이언트                  | `[clients]`  |
| protos   | gRPC Proto 정의                       | `[grpc]`     |
| cli      | CLI 도구                              | `[full]`     |

각 모듈의 상세 문서는 해당 디렉터리의 `README.md` 참조.

---

## 🚀 빠른 시작

### 1. 로깅
```python
from mysingle import get_logger

logger = get_logger(__name__)
logger.info("Hello MySingle", extra={"user_id": "123"})
```

### 2. FastAPI 앱 생성
```python
from mysingle import create_app

app = create_app(
    service_name="my-service",
    version="1.0.0",
    enable_cors=True
)
```

### 3. Beanie 문서
```python
from mysingle.core.base import BaseTimeDocWithUserId

class Strategy(BaseTimeDocWithUserId):
    name: str
    code: str
```

### 4. gRPC 클라이언트
```python
from mysingle.clients import BaseGrpcClient
from mysingle.protos.services.strategy.v1 import strategy_service_pb2_grpc

class StrategyClient(BaseGrpcClient):
    def __init__(self, user_id=None):
        super().__init__("strategy-service", 50051, user_id=user_id)
        self.stub = strategy_service_pb2_grpc.StrategyServiceStub(self.channel)
```

---

## 📖 문서

- [Core 모듈 가이드](src/mysingle/core/README.md)
- [Auth 가이드](src/mysingle/auth/README.md)
- [Database 가이드](src/mysingle/database/README.md)
- [DSL 가이드](src/mysingle/dsl/README.md)
- [Proto 사용법](src/mysingle/protos/README.md)
- [CLI 도구](src/mysingle/cli/README.md)

### 추가 가이드
- [FastAPI 앱 팩토리 사용법](docs/MYSINGLE_APP_FACTORY_USAGE_GUIDE.md)
- [DSL 상세 가이드](docs/MYSINGLE_DSL_USAGE_GUIDE.md)
- [프론트엔드 인증 가이드](docs/FRONTEND_AUTH_DEV_GUIDE.md)

---

## 🏗️ 아키텍처

### 레이어링 구조
```
[Layer 1: Core] (자체 완결)
  └─ settings, logging, metrics, health, email, audit, base

[Layer 2: Optional Modules] (core에만 의존)
  └─ auth, database, dsl, clients

[Layer 3: Proto] (core의 constants만 사용)
  └─ protos/

[Layer 4: CLI] (파일 시스템만 접근)
  └─ cli/
```

---

## 🔄 버전 관리

- **패키지 버전**: `mysingle.__version__` (수동 관리)
- **Proto 버전**: `mysingle.protos.__version__` (자동 생성)

---

## 🛠️ 개발

### 설치 (개발 모드)
```bash
git clone https://github.com/Br0therDan/mysingle-pack.git
cd mysingle-pack
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,full]"
```

### 테스트
```bash
pytest tests/
```

### 린트
```bash
ruff check src/
```

---

## 📝 라이선스

MIT License

---

**Last Updated**: 2025-12-01
```

커밋:
```bash
git add README.md
git commit -m "docs: update root README with module index"
```

---

### Step 8: 테스트 실행 (30분)

```bash
cd /Users/donghakim/mysingle-quant/packages/quant-pack

# 패키지 재설치
uv pip install -e ".[dev,full]"

# 테스트 실행
pytest tests/core/ -v

# 전체 테스트
pytest tests/ -v

# Import 검증
python -c "from mysingle import get_logger; print('✓ Core import OK')"
python -c "from mysingle.core.base import BaseDoc; print('✓ Base import OK')"
python -c "from mysingle.core.logging import setup_logging; print('✓ Logging import OK')"
```

---

### Step 9: 서비스 마이그레이션 확인 (30분)

10개 서비스 중 1개 (strategy-service) 테스트:

```bash
cd /Users/donghakim/mysingle-quant/services/strategy-service

# 의존성 업데이트
uv pip install -e "../../packages/quant-pack[common-grpc]"

# Import 에러 체크
uv run python -c "from app.api.v1.router import api_router"

# 서비스 실행 테스트
uv run uvicorn app.main:app --port 8002 --reload
```

에러 발생 시:
1. Import 경로 확인
2. `scripts/phase-0/update_internal_imports.py` 재실행
3. 수동 수정

---

### Step 10: 최종 커밋 및 푸시 (10분)

```bash
cd /Users/donghakim/mysingle-quant/packages/quant-pack

# 최종 상태 확인
git status

# 마지막 커밋
git add -A
git commit -m "feat(phase-0): complete package restructure

- Consolidate base, logging, metrics, health, email, audit → core/
- Update all import paths automatically
- Generate subpackage README.md files (7)
- Reorganize root documentation
- Update pyproject.toml dependencies
- Version bump to 2.0.0-alpha

BREAKING CHANGE: Import paths changed
  - mysingle.base → mysingle.core.base
  - mysingle.logging → mysingle.core.logging
  - mysingle.metrics → mysingle.core.metrics
  - mysingle.health → mysingle.core.health
  - mysingle.email → mysingle.core.email
  - mysingle.audit → mysingle.core.audit
"

# 브랜치 푸시
git push origin feat/phase-0-package-restructure
```

---

## ✅ 검증 체크리스트

- [ ] 모든 모듈이 core로 이동 완료
- [ ] src/mysingle/ 구조 확인:
  - [ ] core/ (8개 파일 + base/)
  - [ ] auth/
  - [ ] database/
  - [ ] dsl/
  - [ ] clients/
  - [ ] grpc/ (있을 경우)
- [ ] Import 경로 수정 완료
  - [ ] mysingle 패키지 내부
  - [ ] 테스트 파일
- [ ] 7개 README.md 생성 완료
  - [ ] core/README.md
  - [ ] auth/README.md
  - [ ] database/README.md
  - [ ] dsl/README.md
  - [ ] clients/README.md
  - [ ] protos/README.md (Phase 1에서)
  - [ ] cli/README.md (Phase 1에서)
- [ ] 루트 README.md 업데이트
- [ ] pyproject.toml dependencies 업데이트
- [ ] 전체 테스트 통과
- [ ] 1개 이상 서비스 정상 동작 확인

---

## 🐛 예상 문제 및 해결

### 1. 순환 Import 발생
**증상:**
```
ImportError: cannot import name 'get_logger' from partially initialized module
```

**해결:**
- core 내부에서 상대 import 사용
- `from . import logging` 대신 `from .logging import get_logger`

### 2. Beanie 문서 클래스 Import 실패
**증상:**
```
ImportError: cannot import name 'BaseTimeDocWithUserId'
```

**해결:**
- `from mysingle.core.base.documents import BaseTimeDocWithUserId`
- 또는 `from mysingle.core.base import BaseTimeDocWithUserId`

### 3. 서비스 Import 에러
**증상:**
```python
# strategy-service
from mysingle.base import BaseTimeDocWithUserId  # 에러
```

**해결:**
```bash
cd services/strategy-service
grep -r "from mysingle.base" app/
# 수동 수정 또는 스크립트 재실행
```

---

## 📊 예상 결과

### Before (v1.6.1)
```
src/mysingle/
├── __init__.py
├── core/           # 2 files
├── base/           # 3 files
├── logging/        # 3 files
├── metrics/        # 2 files
├── health/         # 2 files
├── email/          # 2 files
├── audit/          # 2 files
├── auth/
├── database/
├── dsl/
└── clients/
```

### After (v2.0.0-alpha)
```
src/mysingle/
├── __init__.py
├── core/           # 통합 (14 files)
│   ├── README.md
│   ├── settings.py
│   ├── app_factory.py
│   ├── constants.py
│   ├── logging.py
│   ├── metrics.py
│   ├── health.py
│   ├── email.py
│   ├── audit.py
│   └── base/
│       ├── documents.py
│       └── schemas.py
├── auth/
│   └── README.md
├── database/
│   └── README.md
├── dsl/
│   └── README.md
└── clients/
    └── README.md
```

---

## 🎯 다음 단계

Phase 0 완료 후:
1. **Phase 1**: Proto 통합 (grpc-protos → mysingle/protos)
2. **Phase 2**: GitHub Actions 구성
3. **Phase 3**: 10개 서비스 전환
4. **Phase 4**: 문서 최종 정리
5. **Phase 5**: grpc-protos 저장소 제거

---

**문서 버전**: 1.0.0
**작성일**: 2025-12-01
**예상 소요 시간**: 2-3일 (스크립트 자동화 포함)

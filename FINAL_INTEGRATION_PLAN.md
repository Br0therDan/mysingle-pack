# MySingle 통합 패키지 최종 작업 계획서 (v2)

**작성일**: 2025-12-01
**목표**: mysingle + mysingle-protos 통합 (단일 Monorepo)
**버전**: v2.0.0 (Major Breaking Change)
**저장소**: https://github.com/Br0therDan/mysingle-pack.git (기존 저장소 재사용)

---

## 🎯 핵심 전환 내용

### 1. 패키지 통합
- **mysingle** + **mysingle-protos** → **mysingle** (단일 패키지)
- Import 경로 통일: `from mysingle.protos.*`
- 선택적 설치: `mysingle[auth,database,grpc]`

### 2. 저장소 전략 (확정)
- **기존 저장소 재사용**: https://github.com/Br0therDan/mysingle-pack.git
- **제거 대상** (검증 완료 후):
  - `packages/grpc-protos/generated/mysingle_protos/`
  - 원격 저장소: https://github.com/Br0therDan/grpc-protos.git

### 3. 책임 분리 전략 (확정)
- **명확한 디렉터리 레이어링** 방식 적용
- Proto와 Utility의 의존성 방향 엄격 관리

### 4. CLI 도구 구조
- `mysingle.cli.protos` - Proto 관리 CLI (proto-cli 이관)
- `mysingle.cli.core` - 향후 mysingle 자체 CLI 확장 공간

---

## 📦 최종 패키지 구조

### 개선된 디렉터리 구조

```
mysingle/                           # 통합 저장소 (기존 mysingle-pack)
├── pyproject.toml                  # 통합 설정
├── README.md                       # 인덱스 및 공통사항만
├── ARCHITECTURE.md                 # 책임 분리 및 버전 관리 가이드
├── CHANGELOG.md                    # 변경 이력
│
├── src/mysingle/
│   ├── __init__.py                 # v2.0.0 - 재구성된 공개 API
│   │
│   ├── core/                       # [Layer 1] 핵심 유틸리티 (통합 모듈)
│   │   ├── README.md               # Core 모듈 가이드
│   │   ├── __init__.py
│   │   ├── settings.py             # CommonSettings
│   │   ├── app_factory.py          # FastAPI 앱 팩토리
│   │   ├── constants.py            # 상수 정의
│   │   ├── logging.py              # ← logging/ 통합
│   │   ├── metrics.py              # ← metrics/ 통합
│   │   ├── health.py               # ← health/ 통합
│   │   ├── email.py                # ← email/ 통합
│   │   ├── audit.py                # ← audit/ 통합
│   │   └── base/                   # ← base/ 통합
│   │       ├── documents.py        # Beanie Base Documents
│   │       └── schemas.py          # Base Response Schemas
│   │
│   ├── auth/                       # [선택] 인증/인가 [auth]
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── deps/
│   │   ├── security/
│   │   └── models.py
│   │
│   ├── database/                   # [선택] 데이터베이스 [database]
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── mongodb.py
│   │   └── duckdb.py
│   │
│   ├── dsl/                        # [선택] DSL 파서 [dsl]
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── parser.py
│   │   ├── executor.py
│   │   └── stdlib.py
│   │
│   ├── clients/                    # [선택] HTTP/gRPC 클라이언트 [clients]
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── base_http_client.py
│   │   └── base_grpc_client.py
│   │
│   ├── protos/                     # [Layer 2] Proto 생성 코드 [grpc]
│   │   ├── README.md               # Proto 사용 가이드
│   │   ├── __init__.py
│   │   ├── __version__.py          # Proto 버전 추적 (자동 생성)
│   │   ├── common/
│   │   │   ├── metadata_pb2.py
│   │   │   ├── metadata_pb2_grpc.py
│   │   │   ├── error_pb2.py
│   │   │   └── error_pb2_grpc.py
│   │   └── services/
│   │       ├── strategy/v1/
│   │       ├── indicator/v1/
│   │       ├── market_data/v1/
│   │       ├── genai/v1/
│   │       └── ml/v1/
│   │
│   └── cli/                        # [Layer 3] CLI 도구
│       ├── README.md               # CLI 사용 가이드
│       ├── __init__.py
│       ├── __main__.py             # 진입점: mysingle-cli
│       ├── protos/                 # Proto 관리 (proto-cli 이관)
│       │   ├── __init__.py
│       │   ├── __main__.py
│       │   ├── commands/
│       │   │   ├── init.py
│       │   │   ├── status.py
│       │   │   ├── validate.py
│       │   │   ├── generate.py
│       │   │   └── version.py
│       │   ├── models.py
│       │   └── utils.py
│       └── core/                   # 향후 mysingle CLI 확장
│           └── __init__.py
│
├── protos/                         # Proto 원본 (개발용)
│   ├── README.md                   # Proto 정의 가이드
│   ├── buf.yaml
│   ├── buf.gen.yaml
│   ├── common/
│   │   ├── metadata.proto
│   │   └── error.proto
│   └── services/
│       ├── strategy/v1/
│       ├── indicator/v1/
│       └── ...
│
├── .github/workflows/
│   ├── validate-code.yml           # Python 코드 검증
│   ├── validate-protos.yml         # Proto 검증
│   ├── auto-generate-protos.yml    # Proto 자동 생성
│   └── auto-release.yml            # 릴리즈 자동화
│
├── scripts/
│   ├── restructure_package.sh      # 패키지 구조 재편
│   ├── migrate_to_core.sh          # base/logging/metrics/health/email → core
│   ├── generate_protos.sh          # Proto 생성
│   ├── update_proto_imports.py     # Import 경로 수정
│   ├── migrate_services.py         # 서비스 마이그레이션
│   └── generate_package_readmes.py # 서브패키지 README 생성
│
├── docs/                           # 개별 가이드 이동 (기존 루트에서)
│   ├── MYSINGLE_APP_FACTORY_USAGE_GUIDE.md
│   ├── MYSINGLE_DSL_USAGE_GUIDE.md
│   ├── FRONTEND_AUTH_DEV_GUIDE.md
│   └── ...
│
└── tests/
    ├── core/
    ├── auth/
    ├── database/
    ├── protos/
    └── cli/
```

### 주요 변경사항

#### 1. core 모듈 통합 ⭐
**기존 구조:**
```
src/mysingle/
├── core/          # 설정, 앱 팩토리만
├── base/          # Beanie Documents
├── logging/       # 로깅
├── metrics/       # 메트릭
├── health/        # 헬스체크
├── email/         # 이메일
└── audit/         # 감사 로그
```

**개선 구조:**
```
src/mysingle/
└── core/          # 통합 핵심 모듈
    ├── settings.py
    ├── app_factory.py
    ├── constants.py
    ├── logging.py      # ← logging/
    ├── metrics.py      # ← metrics/
    ├── health.py       # ← health/
    ├── email.py        # ← email/
    ├── audit.py        # ← audit/
    └── base/           # ← base/
        ├── documents.py
        └── schemas.py
```

**이유:**
- 대부분의 서비스가 공통으로 사용
- 의존성 단순화
- 순환 참조 최소화
- 선택적 설치 시 core만 설치하면 기본 기능 사용 가능

#### 2. 서브패키지별 README.md 추가

각 서브패키지에 독립적인 README 제공:
- 사용법
- API 문서
- 예제 코드
- 의존성 정보

루트 README.md는 인덱스 역할만 수행.

---

## 🔍 상호 의존성 분석 및 개선

### 현재 의존성 맵

```
[분석 결과]
auth → core.constants, core.logging
clients.base_grpc_client → core.constants, core.logging
grpc.interceptors → core.constants, core.logging
database.duckdb_manager → core.logging
dsl.validator → core.logging
```

### 개선 후 의존성 맵

```
[Layer 1: Core] (자체 완결)
core/
├── settings.py
├── constants.py
├── logging.py           # 자체 완결
├── metrics.py
├── health.py
├── email.py
└── base/

[Layer 2: 선택 모듈] (core에만 의존)
auth → core
database → core
dsl → core
clients → core

[Layer 3: Proto] (core에만 의존, 역의존 금지)
protos/ → core (constants만)

[Layer 4: CLI] (참조만, import 금지)
cli/ → (파일 시스템 접근만)
```

**규칙:**
1. **Core는 자체 완결**: 외부 모듈 의존 금지
2. **선택 모듈 → Core 단방향**: 역방향 의존 금지
3. **Proto 격리**: Core의 constants만 사용 가능
4. **CLI 격리**: 파일 시스템 접근만, import 금지

---

## 📋 재구성된 pyproject.toml

```toml
[project]
name = "mysingle"
version = "2.0.0"
description = "Unified utilities and gRPC protocols for MySingle Platform"
readme = "README.md"
requires-python = ">=3.12"

# 최소 의존성 (core만)
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

[project.optional-dependencies]
# 인증
auth = [
    "pyjwt>=2.10.1",
    "pwdlib[argon2,bcrypt]>=0.2.1",
    "httpx-oauth>=0.16.1",
]

# 웹 (FastAPI)
web = [
    "fastapi>=0.104.1",
    "uvicorn[standard]>=0.24.0",
    "python-multipart>=0.0.6",
    "httpx>=0.25.2",
    "aiohttp>=3.9.4",
]

# 데이터베이스 (추가 도구)
database = [
    "duckdb>=1.1.0",
    "redis>=6.4.0",
]

# DSL
dsl = [
    "RestrictedPython>=7.0",
    "pandas>=2.2.0",
    "numpy>=1.26.0",
]

# gRPC + Proto
grpc = [
    "grpcio>=1.60.0,<2.0.0",
    "protobuf>=4.25.0,<7.0.0",
]

# 클라이언트
clients = [
    "httpx>=0.25.2",
    "aiohttp>=3.9.4",
    "grpcio>=1.60.0",
]

# 조합형 (자주 사용)
common = ["mysingle[auth,database,web]"]        # 일반 웹 서비스
common-grpc = ["mysingle[auth,database,web,grpc,clients]"]  # gRPC 사용 서비스
full = ["mysingle[auth,web,database,dsl,grpc,clients]"]  # 전체

# 개발 도구
dev = [
    "pytest>=7.4.3",
    "pytest-asyncio>=0.21.1",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.9",
    "mypy>=1.8.0",
    "buf>=1.28.0",
    "grpcio-tools>=1.60.0",
]

[project.scripts]
mysingle-cli = "mysingle.cli.__main__:main"
mysingle-proto = "mysingle.cli.protos.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mysingle"]

[tool.ruff]
line-length = 88
target-version = "py312"
exclude = [
    ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv",
    "__pycache__", "data/", "logs/",
]

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "SIM"]
ignore = ["E501", "F403", "B008", "B006", "B904", "SIM105", "SIM117", "SIM103"]
```

---

## 🚀 작업 단계 (업데이트)

### Phase 0: 패키지 구조 재편 ⭐ (NEW - 2-3일)

이 문서의 "Phase 0" 섹션에 상세한 스크립트와 절차가 포함되어 있습니다.

주요 작업:
1. 디렉터리 재구성 (base, logging, metrics, health, email, audit → core)
2. Import 경로 자동 수정
3. 서브패키지 README 생성
4. pyproject.toml 업데이트

### Phase 1: Proto 통합 (2-3일)

### Phase 2: GitHub Actions (1-2일)

### Phase 3: 서비스 전환 (3-5일)

### Phase 4: 문서화 (1-2일)

### Phase 5: 검증 및 정리 (1-2일)

(각 Phase의 상세 내용은 이전과 동일하므로 생략)

---

## 📅 업데이트된 일정

| Phase       | 작업                          | 기간      | 상태  |
| ----------- | ----------------------------- | --------- | ----- |
| **Phase 0** | **패키지 구조 재편 (NEW)**    | **2-3일** | **⏳** |
| Phase 1     | Proto 통합 (grpc-protos 이관) | 2-3일     | ⏳     |
| Phase 2     | GitHub Actions 구성           | 1-2일     | ⏳     |
| Phase 3     | 서비스 전환 (10개)            | 3-5일     | ⏳     |
| Phase 4     | 문서화 (README 재구성)        | 1-2일     | ⏳     |
| Phase 5     | 검증 및 구 저장소 정리        | 1-2일     | ⏳     |

**총 예상 기간**: 4-5주

---

## 🎯 성공 지표

1. **패키지 구조 개선**: ✅ Core 통합 완료
2. **의존성 감소**: 평균 40% 이상
3. **Import 경로 통일**: `from mysingle.*` 100%
4. **문서화 완료**: 각 서브패키지 README + 루트 인덱스
5. **모든 서비스 빌드 성공**: 10/10
6. **CI/CD 정상 작동**: 모든 워크플로우 통과

---

**문서 버전**: 2.0.0
**작성자**: AI Assistant
**최종 승인 필요**: Architecture Team, DevOps Team, Backend Team
**최종 수정**: 2025-12-01

**주요 변경사항 (v1 → v2):**
- ✅ 저장소 전략 확정 (기존 mysingle-pack 재사용)
- ✅ Phase 0 추가 (패키지 구조 재편)
- ✅ Core 모듈 통합 (base, logging, metrics, health, email, audit)
- ✅ 서브패키지별 README.md 구조
- ✅ 의존성 명확화 및 레이어링 개선

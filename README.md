# MySingle - Unified Platform Package

**Version**: 2.2.1
**Repository**: https://github.com/Br0therDan/mysingle-pack.git

MySingle 플랫폼 통합 유틸리티 패키지

---

## 📦 설치

### 기본 설치 (core만)
```bash
# Git 저장소에서 직접 설치 (권장)
uv pip install git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.0
```

### 선택적 설치 (extras)
```bash
# 인증 필요
uv pip install "git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.0#egg=mysingle[auth]"

# 데이터베이스 추가 도구
uv pip install "git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.0#egg=mysingle[database]"

# DSL 파서
uv pip install "git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.0#egg=mysingle[dsl]"

# gRPC 지원
uv pip install "git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.0#egg=mysingle[grpc]"

# 조합형 (추천)
uv pip install "git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.0#egg=mysingle[common]"        # auth + database + web
uv pip install "git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.0#egg=mysingle[common-grpc]"   # common + grpc + clients
uv pip install "git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.0#egg=mysingle[full]"          # 전체
```


---

## 📚 모듈 구조

| 모듈     | 설명                                        | 설치         |
| -------- | ------------------------------------------- | ------------ |
| **core** | 핵심 유틸리티 (설정, 로깅, 메트릭, 헬스 등) | 기본 포함    |
| auth     | 인증/인가 (JWT, Kong Gateway)               | `[auth]`     |
| database | MongoDB, DuckDB, Redis                      | `[database]` |
| dsl      | 전략 DSL 파서                               | `[dsl]`      |
| clients  | HTTP/gRPC 클라이언트                        | `[clients]`  |
| grpc     | gRPC Interceptors                           | `[grpc]`     |

각 모듈의 상세 문서는 해당 디렉터리의 `README.md` 참조.

---

## 🔧 CLI 도구

### mysingle - 패키지 관리

MySingle 패키지와 마이크로서비스 협업을 위한 통합 CLI 도구입니다.

```bash
# 대화형 모드
mysingle

# 버전 관리 (Conventional Commits 자동 분석)
mysingle version auto        # 커밋 분석하여 자동 버전 결정
mysingle version show        # 현재 버전 확인
mysingle version patch       # 패치 버전 업그레이드
mysingle version minor       # 마이너 버전 업그레이드
mysingle version major       # 메이저 버전 업그레이드

# Git Submodule 관리 (마이크로서비스에서 사용)
mysingle submodule add       # MySingle을 submodule로 추가
mysingle submodule status    # Submodule 상태 확인
mysingle submodule update    # 최신 버전으로 업데이트
mysingle submodule sync      # 변경사항 PR 준비
```

### mysingle-proto - Proto 파일 관리

```bash
# 대화형 모드
mysingle-proto

# Proto 관리
mysingle-proto init          # 환경 초기화
mysingle-proto generate      # Python 스텁 생성
mysingle-proto validate      # Proto 검증
mysingle-proto status        # Proto 현황
```

**상세 문서**: [CLI 사용 가이드](src/mysingle/cli/README.md)

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
from mysingle import create_fastapi_app

app = create_fastapi_app(
    service_name="my-service",
    version="1.0.0"
)
```

### 3. Beanie 문서 클래스
```python
from mysingle.core.base import BaseTimeDocWithUserId

class Strategy(BaseTimeDocWithUserId):
    name: str
    code: str
```

### 4. gRPC 클라이언트
```python
from mysingle.clients import BaseGrpcClient

class MyGrpcClient(BaseGrpcClient):
    def __init__(self, user_id=None):
        super().__init__("my-service", 50051, user_id=user_id)
```

---

## 📖 문서

### 모듈별 가이드
- [Core 모듈 가이드](src/mysingle/core/README.md)
- [Auth 가이드](src/mysingle/auth/README.md)
- [Database 가이드](src/mysingle/database/README.md)
- [DSL 가이드](src/mysingle/dsl/README.md)
- [Clients 가이드](src/mysingle/clients/README.md)

### 상세 가이드
- [FastAPI 앱 팩토리 사용법](docs/MYSINGLE_APP_FACTORY_USAGE_GUIDE.md)
- [DSL 상세 가이드](docs/MYSINGLE_DSL_USAGE_GUIDE.md)
- [프론트엔드 인증 가이드](docs/FRONTEND_AUTH_DEV_GUIDE.md)
- [전체 패키지 사용법](docs/MYSINGLE_PACK_USAGE_GUIDE.md)

---

## 🏗️ Phase 0 완료 내역

### ✅ 완료된 작업
- **모듈 통합**: base, logging, metrics, health, email, audit → core/
- **Import 경로 업데이트**: 4개 파일 자동 수정
- **서브패키지 README**: 5개 생성 (core, auth, database, dsl, clients)
- **의존성 재구성**: optional dependencies 도입
- **문서 재구성**: 루트 가이드 → docs/

### 📦 새로운 패키지 구조
```
src/mysingle/
├── core/                    # 통합 핵심 모듈
│   ├── base/               # Beanie 문서 클래스
│   ├── logging/            # 구조화된 로깅
│   ├── metrics/            # Prometheus 메트릭
│   ├── health/             # 헬스체크
│   ├── email/              # 이메일 발송
│   └── audit/              # 감사 로그
├── auth/                   # 인증/인가 [선택]
├── database/               # 데이터베이스 [선택]
├── dsl/                    # DSL 파서 [선택]
├── clients/                # HTTP/gRPC 클라이언트 [선택]
└── grpc/                   # gRPC Interceptors [선택]
```

---

## 🔄 버전 관리

- **패키지 버전**: `mysingle.__version__` = "2.0.0-alpha"
- **Breaking Changes**: Import 경로 변경
  - `mysingle.base` → `mysingle.core.base`
  - `mysingle.core` → `mysingle.core.logging`
  - `mysingle.metrics` → `mysingle.core.metrics`
  - 기타 모듈들도 core로 통합

---

## 🚀 배포 가이드

### Git-based 설치 방식

MySingle 패키지는 **Git 저장소를 통해 직접 설치**하는 방식으로 배포됩니다.

#### 서비스에서 사용하기

**pyproject.toml:**
```toml
dependencies = [
    "mysingle @ git+https://github.com/Br0therDan/mysingle-pack.git@v2.3.5",
    # 또는 최신 main 브랜치
    "mysingle @ git+https://github.com/Br0therDan/mysingle-pack.git@main",
]
```

**또는 uv로 직접 설치:**
```bash
uv pip install git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.0

# extras와 함께 설치
uv pip install "git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.0#egg=mysingle[full]"
```

**마이크로서비스에서 Git Submodule로 사용:**
```bash
# 1. 마이크로서비스 저장소에 submodule 추가
cd ~/my-service
mysingle submodule add

# 2. Proto/공통 코드 수정 후 PR
cd libs/mysingle
vim protos/services/user/v1/user_service.proto
mysingle submodule sync

# 3. PR 머지 후 업데이트
mysingle submodule update
```

### 릴리즈 프로세스

1. **버전 업데이트** (Conventional Commits 자동 분석):
   ```bash
   # 자동 분석 (권장)
   mysingle version auto --push     # 커밋 분석 → 버전 업데이트 → 푸시
   mysingle version auto --dry-run  # 분석만 수행 (변경 안함)

   # 수동 지정
   mysingle version patch  # 2.2.0 → 2.2.1
   mysingle version minor  # 2.2.0 → 2.3.0
   mysingle version major  # 2.2.0 → 3.0.0
   ```

2. **변경사항 푸시**:
   ```bash
   # CLI가 자동으로 커밋/태그 생성
   # --push 옵션으로 자동 푸시 가능
   mysingle version patch --push
   ```

3. **자동 배포 실행**:
   - `auto-release.yml` 워크플로우가 자동 실행됨
   - GitHub Release 생성 (dist 파일 첨부)
   - Git tag 생성 (예: `v2.0.2`)

4. **서비스 업데이트**:
   ```bash
   # 직접 설치 방식
   uv pip install --upgrade git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.1

   # Submodule 방식 (권장)
   mysingle submodule update
   ```

### 워크플로우 설명

| 워크플로우                 | 트리거                     | 동작                      |
| -------------------------- | -------------------------- | ------------------------- |
| `auto-release.yml`         | pyproject.toml 변경 (main) | GitHub Release + Git Tag  |
| `validate-commits.yml`     | Pull Request               | Conventional Commits 검증 |
| `validate-protos.yml`      | Proto 파일 변경            | Buf lint + format check   |
| `auto-generate-protos.yml` | Proto 파일 변경            | Proto stub 자동 생성      |

---

## 🛠️ 개발

### 설치 (개발 모드)
```bash
git clone https://github.com/Br0therDan/mysingle-pack.git
cd mysingle-pack
uv sync --all-extras
```

### Proto 생성
```bash
uv run mysingle-proto generate
```

### 테스트
```bash
# 전체 테스트
uv run python -m pytest tests/ -v

# 커버리지 포함
uv run python -m pytest tests/ --cov=mysingle --cov-report=term-missing

# 특정 모듈만
uv run python -m pytest tests/core/ -v
```

### 린트
```bash
# 체크
uv run ruff check src/ tests/

# 자동 수정
uv run ruff check --fix src/ tests/

# 포맷
uv run ruff format src/ tests/
```

### 빌드
```bash
# 로컬 빌드
uv build --out-dir dist

# 설치 테스트
uv pip install dist/mysingle-*.whl
```

---

## 📝 라이선스

MIT License

---

**Last Updated**: 2025-12-02
**Version**: 2.2.0
**Phase**: Git Submodule Management & Auto Versioning ✅

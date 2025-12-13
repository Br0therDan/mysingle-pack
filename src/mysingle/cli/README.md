# MySingle CLI

MySingle 플랫폼을 위한 통합 명령줄 도구입니다.

## 📦 설치

```bash
# mysingle 패키지와 함께 자동 설치됨
uv add mysingle
# 또는
uv pip install mysingle

# CLI 스크립트 확인
which mysingle mysingle-proto
```

## 🎨 새로운 기능 (v2.2.0)

**업데이트**: 2025-12-02

### ✨ 주요 기능

1. **Git Submodule 관리**: 마이크로서비스에서 MySingle을 submodule로 관리 ⭐ NEW
2. **서비스 스캐폴딩**: 표준화된 마이크로서비스 구조 자동 생성 ⭐ NEW
3. **자동 버전 관리**: Conventional Commits 분석 기반 자동 버전 결정 ⭐ NEW
4. **명령어 간소화**: `mysingle-cli` → `mysingle`
5. **한국어 인터페이스**: 모든 메시지가 한국어로 제공
6. **컬러 출력**: Rich 라이브러리 기반의 시각적 개선
7. **대화형 모드**: 인자 없이 실행 시 단계별 메뉴 제공

### 🚀 대화형 모드

```bash
# 옵션 없이 실행하면 대화형 메뉴 표시
$ mysingle

🚀 MySingle CLI

사용 가능한 명령:

  1. version    - 패키지 버전 관리
  2. submodule  - Git Submodule 관리
  3. scaffold   - 서비스 스캐폴딩
  4. proto      - Proto 파일 관리
  5. help       - 도움말 표시
  q. quit       - 종료

명령을 선택하세요 [1/2/3/4/5/q] (기본: q):
```

## 🔧 사용 가능한 도구

### 1. mysingle submodule - Git Submodule 관리 ⭐ NEW

마이크로서비스에서 MySingle 패키지를 submodule로 관리하는 도구입니다.

#### 사용 시나리오

MySingle은 **중앙 집중식 공유 패키지**로, 여러 마이크로서비스에서 공통으로 사용됩니다.
각 서비스에서 Proto나 공통 코드를 수정할 필요가 있을 때 submodule로 추가하여 작업 후 PR을 제출합니다.

#### 워크플로우

```bash
# 1. 마이크로서비스 저장소에 MySingle submodule 추가
cd ~/my-microservice
mysingle submodule add

# 2. Submodule 상태 확인
mysingle submodule status

# 3. Proto 파일 수정
cd libs/mysingle
vim protos/services/user/v1/user_service.proto

# 4. 변경사항 PR 준비 (자동으로 브랜치 생성, 커밋, 푸시)
mysingle submodule sync

# 5. GitHub에서 PR 생성
# https://github.com/Br0therDan/mysingle-pack/compare

# 6. PR 머지 후 최신 버전 업데이트
mysingle submodule update
```

#### 명령어

```bash
# Submodule 추가
mysingle submodule add                           # 기본 경로(libs/mysingle)에 추가
mysingle submodule add --path packages/mysingle  # 커스텀 경로 지정
mysingle submodule add --branch develop          # 특정 브랜치 추가
mysingle submodule add --force                   # 기존 디렉토리 덮어쓰기

# 상태 확인
mysingle submodule status    # 현재 브랜치, 버전, 변경사항 확인

# 업데이트
mysingle submodule update              # 원격 저장소에서 최신 변경사항 가져오기
mysingle submodule update --no-remote  # 부모 저장소에 기록된 커밋으로 업데이트

# 변경사항 동기화 (PR 준비)
mysingle submodule sync    # 브랜치 생성 → 커밋 → 푸시 (대화형)
```

#### 예시: Proto 파일 수정 및 PR

```bash
# 1. 마이크로서비스에서 submodule 추가
$ cd ~/projects/user-service
$ mysingle submodule add

MySingle 패키지를 submodule로 추가합니다...
  저장소: https://github.com/Br0therDan/mysingle-pack.git
  경로: libs/mysingle
  브랜치: main

✅ Submodule 추가 완료: libs/mysingle
✅ Submodule 초기화 완료

다음 단계:
  1. 변경사항 커밋: git add libs/mysingle .gitmodules && git commit -m 'chore: add mysingle submodule'
  2. 상태 확인: mysingle submodule status
  3. Proto 생성: cd libs/mysingle && mysingle-proto generate

# 2. Proto 파일 수정
$ cd libs/mysingle
$ vim protos/services/user/v1/user_service.proto
# ... 수정 작업 ...

# 3. 변경사항 PR 준비
$ cd ~/projects/user-service
$ mysingle submodule sync

로컬 변경사항:
 M protos/services/user/v1/user_service.proto

⚠️  main 브랜치에서 작업 중입니다.
새 브랜치를 생성하시겠습니까? [Y/n]: y
브랜치 이름을 입력하세요 [feature/update-from-user-service]: feature/add-user-avatar-field
✅ 새 브랜치 생성: feature/add-user-avatar-field

변경사항을 커밋하시겠습니까? [Y/n]: y
커밋 메시지를 입력하세요 [feat: update from user-service]: feat(proto): add avatar field to user service
✅ 커밋 완료

'feature/add-user-avatar-field' 브랜치를 origin에 푸시하시겠습니까? [Y/n]: y
✅ 푸시 완료

✅ 동기화 완료!

다음 단계:
  1. GitHub에서 PR 생성
  2. https://github.com/Br0therDan/mysingle-pack/compare
  3. base: main ← compare: feature/add-user-avatar-field

# 4. PR 생성 및 머지 (GitHub에서)

# 5. 머지 후 최신 버전 업데이트
$ mysingle submodule update

MySingle submodule 업데이트 중...
✅ 원격 저장소에서 업데이트 완료: libs/mysingle
```

#### Fork 설정

MySingle에 변경사항을 PR하려면 fork가 필요합니다:

```bash
# 1. GitHub에서 mysingle-pack을 fork

# 2. Submodule 디렉토리로 이동
cd libs/mysingle

# 3. Origin을 fork로 변경
git remote set-url origin https://github.com/YOUR_USERNAME/mysingle-pack.git

# 4. Upstream 추가
git remote add upstream https://github.com/Br0therDan/mysingle-pack.git

# 5. 확인
git remote -v
```

### 2. mysingle scaffold - 서비스 스캐폴딩 ⭐ NEW

표준화된 NON_IAM 마이크로서비스 구조를 자동으로 생성하는 도구입니다.

#### 사용 시나리오

새로운 마이크로서비스를 빠르게 시작할 때 MySingle 표준 구조로 자동 생성합니다.

#### 명령어

```bash
# 대화형 모드 (권장)
mysingle scaffold
mysingle scaffold -i

# 커맨드라인 모드
mysingle scaffold my-service --port 8011
mysingle scaffold my-service --port 8011 --grpc --grpc-port 50056

# 출력 디렉토리 지정
mysingle scaffold my-service --output-dir ./custom-services/my-service

# 도움말
mysingle scaffold --help
```

#### 대화형 모드 예시

```bash
$ mysingle scaffold

🚀 MySingle Service Scaffolding Tool

Service Configuration

? Service name (kebab-case, e.g., reporting-service): reporting
? Service name should end with '-service'. Add it automatically? Yes

💡 Next available ports: HTTP 8011, gRPC 50056

? Use suggested HTTP port (8011)? Yes
? Enable gRPC support? No

Configuration Summary
Service Name:     reporting-service
HTTP Port:        8011
gRPC Enabled:     No
Output Directory: /Users/you/mysingle-quant/services/reporting-service

? Proceed with this configuration? Yes

Creating service: reporting-service
📁 Created directory structure
📝 Created application files
⚙️  Created configuration files
🧪 Created test files

✅ Service 'reporting-service' created successfully!

✅ Next Steps:

1. cd /Users/you/mysingle-quant/services/reporting-service
2. uv pip install -e .
3. cp .env .env.local
4. vim .env.local  # Edit configuration
5. uvicorn app.main:app --reload --port 8011
6. open http://localhost:8011/docs
```

#### 생성되는 구조

```
services/{service-name}/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 진입점 (ServiceType.NON_IAM_SERVICE)
│   ├── api/
│   │   └── v1/
│   │       ├── api_v1.py    # API 라우터
│   │       └── routes/
│   │           └── health.py
│   ├── core/
│   │   └── config.py        # CommonSettings 상속
│   ├── models/
│   │   └── __init__.py      # document_models 리스트
│   ├── schemas/
│   └── services/
│       └── service_factory.py
├── tests/
│   ├── unit/
│   │   └── test_health.py
│   └── integration/
├── Dockerfile               # Multi-stage build
├── pyproject.toml           # mysingle>=2.2.0
├── .env                     # 환경 변수 템플릿
├── .gitignore
├── pytest.ini
└── README.md
```

#### 주요 특징

1. **NON_IAM Service 패턴**: Kong Gateway 기반 인증
2. **CommonSettings 상속**: 표준 환경변수 구조
3. **ServiceFactory 패턴**: 공유 리소스 관리
4. **Beanie ODM**: document_models 리스트 구조
5. **Health Check**: `/health`, `/ready` 엔드포인트
6. **테스트 구조**: pytest + pytest-asyncio

#### 생성된 코드 예시

**app/main.py**:
```python
from mysingle.core import (
    ServiceType,
    create_fastapi_app,
    create_service_config,
    setup_logging,
)

service_config = create_service_config(

    service_name=settings.SERVICE_NAME,
    service_version=settings.APP_VERSION,
    description="My Service",
    enable_audit_logging=settings.AUDIT_LOGGING_ENABLED,
    enable_metrics=True,
    lifespan=lifespan,
)

app = create_fastapi_app(
    service_config=service_config,
    document_models=document_models,
)
```

**app/core/config.py**:
```python
from mysingle.core import CommonSettings

class Settings(CommonSettings):
    SERVICE_NAME: str = "my-service"
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"
    AUDIT_LOGGING_ENABLED: bool = True

settings = Settings()
```

### 3. mysingle version - 패키지 버전 관리

패키지 버전을 관리하고 Git 태그를 생성하는 도구입니다.

#### 명령어

```bash
# 도움말
mysingle --help
mysingle version --help

# 현재 버전 확인
mysingle version show

# 자동 버전 관리 (Conventional Commits 기반) ⭐ NEW
mysingle version auto              # 커밋 분석하여 자동 결정
mysingle version auto --dry-run    # 분석만 수행 (변경 안함)
mysingle version auto --push       # 분석 후 바로 푸시

# 수동 버전 업그레이드
mysingle version patch   # 2.0.0 → 2.0.1
mysingle version minor   # 2.0.0 → 2.1.0
mysingle version major   # 2.0.0 → 3.0.0

# 대화형 모드로 버전 관리
mysingle version         # 단계별 선택 메뉴 제공 (auto 옵션 포함)

# 커스텀 버전 설정
mysingle version patch --custom 2.1.0-beta

# Git 커밋/태그 없이 버전만 변경
mysingle version patch --no-commit
mysingle version patch --no-tag

# 변경사항을 원격에 푸시
mysingle version patch --push
```

#### 자동 버전 관리 (Conventional Commits)

**Conventional Commits** 형식의 커밋 메시지를 분석하여 자동으로 버전을 결정합니다.

**커밋 메시지 규칙:**
```bash
# Major 버전 증가 (2.0.0 → 3.0.0)
git commit -m "feat!: breaking change"
git commit -m "feat: new feature\n\nBREAKING CHANGE: API changed"

# Minor 버전 증가 (2.0.0 → 2.1.0)
git commit -m "feat: add new feature"
git commit -m "feat(auth): implement OAuth"

# Patch 버전 증가 (2.0.0 → 2.0.1)
git commit -m "fix: resolve bug"
git commit -m "fix(api): handle edge case"

# 버전 변경 없음
git commit -m "docs: update README"
git commit -m "chore: update dependencies"
git commit -m "style: format code"
git commit -m "refactor: restructure module"
git commit -m "test: add unit tests"
```

**Proto 변경 특수 처리:**
```bash
# Proto 파일만 변경된 경우 → 메인 버전 유지
git commit -m "proto: update user service"
git commit -m "feat: add user field" # protos/ 파일만 변경

# Proto + 일반 코드 변경 → 일반 규칙 적용
git commit -m "feat: integrate new proto fields"
```

**사용 예시:**
```bash
# 1. 커밋 메시지 분석만 수행 (실제 변경 안함)
$ mysingle version auto --dry-run
현재 버전: 2.0.1
분석된 커밋 수: 5

✨ Features: 2개
🐛 Bug Fixes: 1개
📦 Proto Changes: 3개

권장 버전: 2.0.1 → 2.1.0 (minor)

생성될 CHANGELOG:
## [2.1.0] - 2025-12-02

### ✨ Features
- feat: add authentication module (a1b2c3d)
- feat(api): implement rate limiting (d4e5f6g)

### 🐛 Bug Fixes
- fix: resolve memory leak (g7h8i9j)

### 📦 Proto Changes
- proto: update user service schema (j1k2l3m)

# 2. 자동 버전 업데이트 및 푸시
$ mysingle version auto --push
현재 버전: 2.0.1
분석된 커밋 수: 5

✨ Features: 2개
🐛 Bug Fixes: 1개

권장 버전: 2.0.1 → 2.1.0 (minor)

✅ pyproject.toml 업데이트 완료
✅ 커밋 생성 완료: v2.1.0
✅ 태그 생성 완료: v2.1.0
✅ 커밋 푸시 완료
✅ 태그 푸시 완료
```

#### 주요 기능

1. **show**: 현재 패키지 버전 표시
2. **auto**: Conventional Commits 분석으로 자동 버전 결정 ⭐
3. **major/minor/patch**: 시맨틱 버전 수동 업그레이드
4. **대화형 모드**: 인자 없이 실행 시 단계별 선택
5. **--custom**: 커스텀 버전 문자열 설정 (prerelease 포함)
6. **--dry-run**: 분석만 수행 (auto 모드 전용)
7. **--no-commit**: Git 커밋 생성 건너뛰기
8. **--no-tag**: Git 태그 생성 건너뛰기
9. **--push**: 변경사항을 원격 저장소에 푸시

#### 예시

```bash
# 현재 버전 확인 (컬러 출력)
$ mysingle version show
현재 버전: 2.0.1

# Patch 버전 업그레이드 (2.0.1 → 2.0.2)
$ mysingle version patch
버전 변경: 2.0.1 → 2.0.2
✅ pyproject.toml 업데이트 완료
✅ 커밋 생성 완료: chore(release): v2.0.2 (bump patch)
✅ 태그 생성 완료: v2.0.2

# 대화형 모드
$ mysingle version

현재 버전: 2.0.2

버전 업데이트 유형을 선택하세요 [major/minor/patch/show/cancel] (기본: patch): patch

버전 변경: 2.0.2 → 2.0.3

계속하시겠습니까? [y/n] (y): y
✅ pyproject.toml 업데이트 완료
Git 커밋을 생성하시겠습니까? [y/n] (y): y
✅ 커밋 생성 완료: chore(release): v2.0.3 (bump patch)
Git 태그를 생성하시겠습니까? [y/n] (y): y
✅ 태그 생성 완료: v2.0.3
origin에 푸시하시겠습니까? [y/n] (n): n

# Git 작업 없이 버전만 변경
$ mysingle version minor --no-commit --no-tag
버전 변경: 2.0.3 → 2.1.0
✅ pyproject.toml 업데이트 완료

# 커스텀 prerelease 버전
$ mysingle version patch --custom 2.1.0-rc.1
버전 변경: 2.1.0 → 2.1.0-rc.1
✅ pyproject.toml 업데이트 완료
```

### 4. mysingle-proto - Proto 파일 관리

gRPC Proto 파일의 생성, 검증, 상태 확인을 위한 도구입니다.

#### 🆕 대화형 모드 (v2.0.2+)

```bash
# 옵션 없이 실행하면 대화형 메뉴 표시
$ mysingle-proto

🔧 MySingle Proto CLI

사용 가능한 명령:

  1. init      - 저장소 초기화 및 환경 확인
  2. status    - 서비스별 proto 파일 현황
  3. generate  - Python gRPC 스텁 생성
  4. validate  - Proto 파일 검증
  5. info      - 패키지 버전 및 상태 정보
  h. help      - 도움말 표시
  q. quit      - 종료

명령을 선택하세요 [1/2/3/4/5/h/q] (기본: q):
```

#### 명령어

```bash
# 도움말
mysingle-proto --help

# 저장소 초기화 및 환경 확인
mysingle-proto init
mysingle-proto init --check-only  # 초기화 없이 상태만 확인

# 서비스별 proto 파일 현황 확인 (메인 저장소에서만 사용)
mysingle-proto status
mysingle-proto status -v  # 상세 파일 목록 포함

# Proto 파일 검증
mysingle-proto validate
mysingle-proto validate --fix  # Format 오류 자동 수정
mysingle-proto validate --skip-lint  # Lint 검사 건너뛰기
mysingle-proto validate --skip-format  # Format 검사 건너뛰기
mysingle-proto validate --breaking  # Breaking change 검사
mysingle-proto validate --breaking --against develop  # 특정 브랜치와 비교

# Python 스텁 생성
mysingle-proto generate
mysingle-proto generate --skip-rewrite  # import 경로 수정 건너뛰기
mysingle-proto generate --skip-init     # __init__.py 생성 건너뛰기

# 패키지 버전 및 상태 정보
mysingle-proto info
mysingle-proto info --check-git  # Git 상태도 함께 확인
```

#### 주요 기능

1. **init**: Git 및 Buf CLI 설치 확인, 필수 디렉터리 검증
2. **status**: 서비스별 proto 파일 개수 및 경로 표시 (메인 저장소 전용)
3. **validate**: Buf를 이용한 Lint, 포맷, Breaking change 검사
4. **generate**: Python gRPC 스텁 자동 생성, import 경로 수정, __init__.py 생성
5. **info**: 현재 패키지 버전, Git 브랜치, 작업 트리 상태 표시

#### 예시

```bash
# 1. 저장소 환경 확인
$ mysingle-proto init --check-only

============================================================
  MySingle Proto 패키지 초기화
============================================================

✅ Git 저장소 확인: /Users/donghakim/mysingle-quant/packages/quant-pack
ℹ️  현재 브랜치: main
ℹ️  원격 저장소:
  origin        https://github.com/Br0therDan/mysingle-pack.git (fetch)
  origin        https://github.com/Br0therDan/mysingle-pack.git (push)
✅ Buf 설치 확인: 1.60.0

필수 디렉터리 확인:
✅   ✅ Proto 원본: /Users/donghakim/mysingle-quant/packages/quant-pack/protos
✅   ✅ Proto 생성: /Users/donghakim/mysingle-quant/packages/quant-pack/src/mysingle/protos

Buf 설정 파일 확인:
✅   ✅ buf.yaml: /Users/donghakim/mysingle-quant/packages/quant-pack/protos/buf.yaml
✅   ✅ buf.gen.yaml: /Users/donghakim/mysingle-quant/packages/quant-pack/protos/buf.gen.yaml

# 2. 패키지 정보 확인
$ mysingle-proto info --check-git

============================================================
  Proto 패키지 정보
============================================================

ℹ️  현재 버전: v2.0.0-alpha
ℹ️  현재 브랜치: main
✅ Git 작업 트리: ✅ 깨끗함

📦 GitHub 릴리즈: https://github.com/Br0therDan/mysingle-pack/releases/tag/v2.0.0-alpha

# 3. Proto 검증 (Lint + Format)
$ mysingle-proto validate
🔍 Linting proto files...
✅ Lint check passed
🔍 Checking proto format...
✅ Format check passed

# 4. Breaking change 검사
$ mysingle-proto validate --breaking
🔍 Checking for breaking changes against main...
⚠️  Breaking changes detected
...

# 5. Python 스텁 생성
$ mysingle-proto generate
🔧 Generating proto code...
✅ Generated 28 files
✅ Fixed import paths (15 files)
✅ Created __init__.py files (8 directories)
```

## 📁 디렉터리 구조

```
src/mysingle/cli/
├── __init__.py              # CLI 패키지 루트
├── __main__.py              # mysingle 진입점
├── core/                    # 패키지 버전 관리
│   ├── __init__.py
│   └── version.py           # 버전 bump 및 Git 태깅
├── submodule/               # Git Submodule 관리
│   ├── __init__.py
│   └── commands.py          # Submodule 명령어
├── scaffold/                # 서비스 스캐폴딩 ⭐ NEW
│   ├── __init__.py
│   ├── commands.py          # Scaffold 명령어
│   └── templates.py         # 파일 템플릿
└── protos/                  # Proto 관리 도구
    ├── __init__.py
    ├── __main__.py          # mysingle-proto 진입점
    ├── models.py            # 데이터 모델
    ├── utils.py             # 유틸리티 함수
    └── commands/            # 명령어 구현
        ├── init.py          # 환경 초기화
        ├── status.py        # Proto 현황
        ├── validate.py      # Proto 검증
        ├── generate.py      # 스텁 생성
        └── info.py          # 패키지 정보
```

## 🔗 관련 문서

- [Proto 사용 가이드](../protos/README.md)
- [서비스 개발 가이드](../../../docs/SERVICE_DEVELOPMENT_GUIDE.md)
- [gRPC 통신 가이드](../../../docs/GRPC_COMMUNICATION.md)

## ⚠️ 주의사항

1. **Proto 생성 워크플로우**:
   - Proto 파일 수정 시 반드시 `mysingle-proto generate` 실행
   - 자동 생성된 `*_pb2.py`, `*_pb2_grpc.py` 파일은 직접 수정 금지
   - Import 경로는 자동으로 `mysingle.protos.*`로 수정됨

2. **환경 요구사항**:
   - Git 설치 필요
   - Buf CLI 설치 필요 (`brew install bufbuild/buf/buf`)
   - Python 3.12 이상

3. **서비스 연동**:
   - 각 서비스는 `mysingle[common-grpc]` 설치 필요
   - Proto 파일 경로: `protos/` (소스), `src/mysingle/protos/` (생성)

## 🐛 문제 해결

### mysingle scaffold

#### 대화형 모드를 사용할 수 없음

```bash
# rich 패키지 설치 확인
python -c "import rich; print('✅ OK')"

# 미설치 시
pip install rich

# 또는 커맨드라인 모드 사용
mysingle scaffold my-service --port 8011
```

#### 서비스 디렉토리가 이미 존재

```bash
# 기존 디렉토리 삭제 (주의!)
rm -rf services/my-service

# 재생성
mysingle scaffold my-service
```

### mysingle-proto

#### Buf CLI를 찾을 수 없음

```bash
# macOS
brew install bufbuild/buf/buf

# 다른 플랫폼
# https://docs.buf.build/installation
```

#### Import 경로 오류

```bash
# Import 경로 자동 수정
cd packages/quant-pack
./scripts/fix_proto_imports.py
```

### Proto 생성 실패

```bash
# 1. buf.yaml 및 buf.gen.yaml 확인
cat buf.yaml
cat buf.gen.yaml

# 2. 수동 생성 시도
buf generate

# 3. 캐시 초기화
rm -rf src/mysingle/protos/*
mysingle-proto generate
```

## 🔮 향후 확장 계획

향후 다음 기능이 추가될 예정입니다:

```bash
# 패키지 관리
mysingle package install <name>
mysingle package list

# 환경 관리
mysingle env setup
mysingle env validate
```

## 📁 디렉터리 구조

```
src/mysingle/cli/
├── __init__.py              # CLI 패키지 루트
├── __main__.py              # mysingle-cli 진입점
├── README.md                # 이 문서
├── core/                    # 패키지 버전 관리
│   ├── __init__.py
│   └── version.py           # 버전 bump 및 Git 태깅
└── protos/                  # Proto 관리 도구
    ├── __init__.py
    ├── __main__.py          # mysingle-proto 진입점
    ├── models.py            # 데이터 모델 (ProtoConfig, ServiceProtoInfo)
    ├── utils.py             # 유틸리티 (로깅, 색상, 테이블)
    └── commands/            # 명령어 구현
        ├── __init__.py
        ├── init.py          # 환경 초기화 및 검증
        ├── status.py        # Proto 현황 확인
        ├── validate.py      # Proto 검증 (lint, format, breaking)
        ├── generate.py      # 스텁 생성 및 경로 수정
        └── info.py          # 패키지 정보 표시
```

## 🎯 CLI 설계 원칙

### 1. 명령어 네이밍
- **mysingle-cli**: 플랫폼 전체 관리 (버전, 환경, 패키지)
- **mysingle-proto**: Proto 전용 도구 (독립적 사용 가능)

### 2. 출력 형식
- ✅/❌/⚠️/ℹ️ 아이콘을 활용한 직관적 피드백
- 색상 코드를 통한 시각적 구분
- 테이블 형식의 구조화된 데이터 출력

### 3. 에러 처리
- 명확한 에러 메시지와 해결 방법 제시
- 비정상 종료 시 적절한 exit code 반환
- 환경 검증 후 작업 진행

### 4. 확장성
- 서브커맨드 기반 구조로 기능 추가 용이
- 공통 유틸리티 모듈화
- 설정 기반 동작 (ProtoConfig)

## 🔗 관련 문서

- [MySingle Package 사용 가이드](../../../docs/MYSINGLE_PACK_USAGE_GUIDE.md)
- [Proto 사용 가이드](../../protos/README.md)
- [gRPC 통신 가이드](../clients/README.md)

## ⚠️ 주의사항

### mysingle-cli

1. **버전 관리 워크플로우**:
   - pyproject.toml의 `project.version` 필드를 자동으로 업데이트
   - Git 커밋 및 태그 자동 생성 (선택 가능)
   - Prerelease 버전 지원 (alpha, beta, rc 등)

2. **Git 요구사항**:
   - Git 저장소 내에서만 동작
   - 기본적으로 커밋과 태그를 생성 (--no-commit, --no-tag로 비활성화)
   - --push 옵션으로 원격 푸시 가능

### mysingle-proto

1. **Proto 생성 워크플로우**:
   - Proto 파일 수정 시 반드시 `mysingle-proto generate` 실행
   - 자동 생성된 `*_pb2.py`, `*_pb2_grpc.py` 파일은 직접 수정 금지
   - Import 경로는 자동으로 `mysingle.protos.*`로 수정됨

2. **환경 요구사항**:
   - Git 설치 필요
   - Buf CLI 설치 필요 (`brew install bufbuild/buf/buf`)
   - Python 3.12 이상

3. **저장소 구조**:
   - 메인 저장소: 모든 명령어 사용 가능
   - 서비스 submodule: init, validate, info, generate만 사용
   - status 명령은 메인 저장소에서만 동작

4. **Breaking Change 검사**:
   - Buf의 breaking change detection 사용
   - 기본적으로 main 브랜치와 비교
   - --against 옵션으로 다른 브랜치 지정 가능

## 🐛 문제 해결

### mysingle-cli

#### pyproject.toml을 찾을 수 없음

```bash
# pyproject.toml이 있는 디렉터리에서 실행
cd /path/to/mysingle-pack
mysingle-cli version show
```

#### Git 커밋/태그 생성 실패

```bash
# Git 설정 확인
git config user.name
git config user.email

# 수동으로 커밋/태그 스킵
mysingle-cli version patch --no-commit --no-tag
```

### mysingle-proto

#### Buf CLI를 찾을 수 없음

```bash
# macOS
brew install bufbuild/buf/buf

# 버전 확인
buf --version

# 다른 플랫폼
# https://buf.build/docs/installation
```

#### Import 경로 오류

```bash
# Import 경로 자동 수정
mysingle-proto generate

# 수동 수정이 필요한 경우 (대화형 모드)
mysingle-proto
# 메뉴에서 3. generate 선택
```

#### Proto 생성 실패

```bash
# 1. buf.yaml 및 buf.gen.yaml 확인
cat protos/buf.yaml
cat protos/buf.gen.yaml

# 2. Buf 캐시 초기화
buf mod clear-cache

# 3. 생성 디렉터리 초기화 후 재생성
rm -rf src/mysingle/protos/*
mysingle-proto generate
```

#### status 명령이 동작하지 않음

```bash
# 메인 저장소인지 확인
ls -la | grep services

# services 디렉터리가 없으면 submodule 환경
# 대신 다른 명령어 사용
mysingle-proto info
mysingle-proto validate
```

## 📊 테스트 결과

모든 CLI 명령어는 다음과 같이 테스트되었습니다:

### mysingle (v2.0.1+)
- ✅ 대화형 모드: 메뉴 표시 및 명령 선택
- ✅ `--help`: 도움말 표시
- ✅ `version --help`: 버전 명령어 도움말
- ✅ `version show`: 현재 버전 출력 (한국어 메시지)
- ✅ `version`: 대화형 버전 관리 (bump type 선택, Git 작업 확인)
- ✅ `version patch`: 패치 버전 업그레이드 (컬러 출력)
- ✅ Entry point 설치 확인: `/Users/donghakim/mysingle-quant/.venv/bin/mysingle`

### mysingle-proto (v2.0.1+)
- ✅ 대화형 모드: 메뉴 표시 및 명령 선택
- ✅ `--help`: 도움말 표시
- ✅ `init --help`: 초기화 명령어 도움말
- ✅ `init --check-only`: 환경 검증 (Git, Buf, 디렉터리 확인)
- ✅ `status`: 대화형 상세 모드 선택
- ✅ `validate`: 대화형 검증 옵션 선택 (lint/format/breaking)
- ✅ `generate`: 대화형 확인 프롬프트
- ✅ `info`: 버전 및 릴리즈 정보 표시
- ✅ Entry point 설치 확인: `/Users/donghakim/mysingle-quant/.venv/bin/mysingle-proto`

**새로운 기능**:
- 🎨 Rich 라이브러리 기반 컬러 출력
- 🇰🇷 전체 한국어 인터페이스
- 🤝 대화형 프롬프트 (ask_choice, ask_confirm)
- ✨ 단계별 진행 안내

**테스트 환경**: macOS, Python 3.12.8, Buf 1.60.0, Git 2.39+, Rich 13.9.0
**테스트 날짜**: 2025년 12월 2일
**패키지 버전**: v2.2.0

### 추가된 기능 (v2.2.0)

#### Git Submodule 관리
- ✅ `mysingle submodule add`: Submodule 추가 (대화형 경로/브랜치 선택)
- ✅ `mysingle submodule status`: 상태 확인 (브랜치, 버전, 변경사항, 업스트림 차이)
- ✅ `mysingle submodule update`: 업데이트 (원격/기록된 커밋)
- ✅ `mysingle submodule sync`: PR 준비 (브랜치 생성, 커밋, 푸시)
- ✅ Fork 자동 감지 및 설정 안내

#### Conventional Commits 자동 버전 관리
- ✅ `mysingle version auto`: 커밋 메시지 분석으로 자동 버전 결정
- ✅ `--dry-run`: 분석만 수행 (실제 변경 안함)
- ✅ Proto-only 변경 특수 처리 (메인 버전 유지)
- ✅ CHANGELOG 자동 생성
- ✅ GitHub Actions 커밋 검증 워크플로우

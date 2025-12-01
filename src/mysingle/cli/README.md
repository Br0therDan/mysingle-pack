# MySingle CLI

MySingle 플랫폼을 위한 통합 명령줄 도구입니다.

## 📦 설치

```bash
# mysingle 패키지와 함께 자동 설치됨
pip install mysingle

# CLI 스크립트 확인
which mysingle-cli mysingle-proto
```

## 🔧 사용 가능한 도구

### 1. mysingle-cli - 패키지 버전 관리

패키지 버전을 관리하고 Git 태그를 생성하는 도구입니다.

#### 명령어

```bash
# 도움말
mysingle-cli --help
mysingle-cli version --help

# 현재 버전 확인
mysingle-cli version show

# 버전 업그레이드
mysingle-cli version patch   # 2.0.0 → 2.0.1
mysingle-cli version minor   # 2.0.0 → 2.1.0
mysingle-cli version major   # 2.0.0 → 3.0.0

# 커스텀 버전 설정
mysingle-cli version --custom 2.1.0-beta

# Git 커밋/태그 없이 버전만 변경
mysingle-cli version patch --no-commit
mysingle-cli version patch --no-tag

# 변경사항을 원격에 푸시
mysingle-cli version patch --push
```

#### 주요 기능

1. **show**: 현재 패키지 버전 표시
2. **major/minor/patch**: 시맨틱 버전 업그레이드
3. **--custom**: 커스텀 버전 문자열 설정 (prerelease 포함)
4. **--no-commit**: Git 커밋 생성 건너뛰기
5. **--no-tag**: Git 태그 생성 건너뛰기
6. **--push**: 변경사항을 원격 저장소에 푸시

#### 예시

```bash
# 현재 버전 확인
$ mysingle-cli version show
Current version: 2.0.0-alpha

# Patch 버전 업그레이드 (2.0.0 → 2.0.1)
$ mysingle-cli version patch
Updated version: 2.0.0-alpha → 2.0.1
Created commit: 4a3b2c1
Created tag: v2.0.1

# Git 작업 없이 버전만 변경
$ mysingle-cli version minor --no-commit --no-tag
Updated version: 2.0.1 → 2.1.0

# 커스텀 prerelease 버전
$ mysingle-cli version --custom 2.1.0-rc.1
Updated version: 2.1.0 → 2.1.0-rc.1
```

### 2. mysingle-proto - Proto 파일 관리

gRPC Proto 파일의 생성, 검증, 상태 확인을 위한 도구입니다.

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
├── __main__.py              # mysingle-cli 진입점
├── core/                    # 패키지 버전 관리
│   ├── __init__.py
│   └── version.py           # 버전 bump 및 Git 태깅
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

### Buf CLI를 찾을 수 없음

```bash
# macOS
brew install bufbuild/buf/buf

# 다른 플랫폼
# https://docs.buf.build/installation
```

### Import 경로 오류

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
# 서비스 스캐폴딩
mysingle-cli new service <name>

# 패키지 관리
mysingle-cli package install <name>
mysingle-cli package list

# 환경 관리
mysingle-cli env setup
mysingle-cli env validate
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

# 수동 수정이 필요한 경우
cd packages/quant-pack
python scripts/fix_proto_imports.py
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

### mysingle-cli
- ✅ `--help`: 도움말 표시
- ✅ `version --help`: 버전 명령어 도움말
- ✅ `version show`: 현재 버전 출력 (2.0.0-alpha)
- ✅ Entry point 설치 확인: `/Users/donghakim/mysingle-quant/.venv/bin/mysingle-cli`

### mysingle-proto
- ✅ `--help`: 도움말 표시
- ✅ `init --help`: 초기화 명령어 도움말
- ✅ `init --check-only`: 환경 검증 (Git, Buf, 디렉터리 확인)
- ✅ `status`: 메인 저장소 검증 경고 표시
- ✅ `validate --help`: 검증 명령어 도움말
- ✅ `generate --help`: 생성 명령어 도움말
- ✅ `info`: 버전 및 릴리즈 정보 표시
- ✅ `info --check-git`: Git 브랜치 및 작업 트리 상태 표시
- ✅ Entry point 설치 확인: `/Users/donghakim/mysingle-quant/.venv/bin/mysingle-proto`

**테스트 환경**: macOS, Python 3.12.8, Buf 1.60.0, Git 2.39+  
**테스트 날짜**: 2025년 12월 1일  
**패키지 버전**: v2.0.0-alpha

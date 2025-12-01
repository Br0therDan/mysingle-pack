# MySingle CLI

MySingle 플랫폼을 위한 통합 명령줄 도구입니다.

## 📦 설치

```bash
# mysingle 패키지와 함께 자동 설치됨
pip install mysingle
```

## 🔧 사용 가능한 도구

### 1. mysingle-proto - Proto 파일 관리

gRPC Proto 파일의 생성, 검증, 상태 확인을 위한 도구입니다.

#### 명령어

```bash
# 도움말
mysingle-proto --help

# 저장소 초기화 및 환경 확인
mysingle-proto init

# 서비스별 proto 파일 현황 확인
mysingle-proto status
mysingle-proto status -v  # 상세 파일 목록 포함

# Proto 파일 검증
mysingle-proto validate
mysingle-proto validate --fix  # 자동 수정

# Python 스텁 생성
mysingle-proto generate
mysingle-proto generate --skip-rewrite  # import 경로 수정 건너뛰기
mysingle-proto generate --skip-init     # __init__.py 생성 건너뛰기

# 패키지 버전 및 상태 정보
mysingle-proto info
mysingle-proto info --check-git  # Git 상태도 함께 확인
```

#### 주요 기능

1. **init**: 필수 도구 확인 (Git, Buf CLI)
2. **status**: 서비스별 proto 파일 개수 및 경로 표시
3. **validate**: Lint, 포맷 체크, Breaking change 감지
4. **generate**: Python gRPC 스텁 자동 생성, import 경로 수정, __init__.py 생성
5. **info**: 현재 패키지 버전 및 Git 상태 정보

#### 예시

```bash
# 1. 저장소 환경 확인
$ mysingle-proto init
✅ Git: /usr/bin/git (2.39.0)
✅ Buf: /opt/homebrew/bin/buf (1.28.1)
✅ Proto files: 14 files found

# 2. 서비스별 proto 현황 확인
$ mysingle-proto status -v
📊 Proto Files Status
┌─────────────┬────────┬──────────────────────────────────┐
│ Service     │ Count  │ Files                            │
├─────────────┼────────┼──────────────────────────────────┤
│ common      │ 3      │ error.proto                      │
│             │        │ metadata.proto                   │
│             │        │ pagination.proto                 │
├─────────────┼────────┼──────────────────────────────────┤
│ strategy    │ 1      │ strategy_service.proto           │
├─────────────┼────────┼──────────────────────────────────┤
│ genai       │ 5      │ chatops.proto                    │
│             │        │ dsl_validator.proto              │
│             │        │ ir_converter.proto               │
│             │        │ narrative.proto                  │
│             │        │ strategy_builder.proto           │
└─────────────┴────────┴──────────────────────────────────┘

# 3. Proto 검증
$ mysingle-proto validate
🔍 Validating proto files...
✅ Lint check passed
✅ Format check passed
⚠️  Breaking changes detected (use --fix to ignore)

# 4. Python 스텁 생성
$ mysingle-proto generate
🔧 Proto 코드 생성
✅ Generated 28 files
✅ Fixed import paths (15 files)
✅ Created __init__.py files (8 directories)

# 5. 패키지 정보 확인
$ mysingle-proto info --check-git
📦 Proto 패키지 정보
현재 버전: v2.0.0-alpha
현재 브랜치: feat/phase-0-package-restructure
Git 작업 트리: ✅ 깨끗함
📦 GitHub 릴리즈: https://github.com/Br0therDan/mysingle-pack/releases/tag/v2.0.0-alpha
```

## 🔮 향후 확장 계획

### mysingle-cli (패키지 버전 관리)

현재는 패키지 버전 관리 기능을 제공합니다:

```bash
# 버전 정보 확인
mysingle-cli version

# 버전 업그레이드
mysingle-cli version patch   # 1.0.0 → 1.0.1
mysingle-cli version minor   # 1.0.0 → 1.1.0
mysingle-cli version major   # 1.0.0 → 2.0.0

# 커스텀 버전 설정
mysingle-cli version 2.0.0-alpha

# Git 작업 스킵 (버전 변경만)
mysingle-cli version patch --skip-git
```

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

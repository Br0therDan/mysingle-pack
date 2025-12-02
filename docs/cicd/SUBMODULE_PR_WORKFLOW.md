# MySingle Submodule PR 워크플로우 가이드

**Version**: 1.0.0
**Last Updated**: 2025-12-02

이 문서는 MySingle 패키지를 Git Submodule로 사용하는 마이크로서비스에서 패키지 업데이트 및 PR(Pull Request)을 진행하는 전체 프로세스를 설명합니다.

---

## 📋 목차

1. [개요](#개요)
2. [사전 준비](#사전-준비)
3. [서브모듈 등록 프로세스](#서브모듈-등록-프로세스)
4. [MySingle 패키지 업데이트 워크플로우](#mysingle-패키지-업데이트-워크플로우)
5. [PR 프로세스](#pr-프로세스)
6. [트러블슈팅](#트러블슈팅)
7. [Best Practices](#best-practices)

---

## 개요

### 아키텍처

```
마이크로서비스 저장소
├── .gitmodules                    # Submodule 설정
├── packages/
│   └── mysingle/                  # Git Submodule
│       ├── src/mysingle/          # MySingle 패키지 소스
│       ├── pyproject.toml
│       └── README.md
├── src/
│   └── app/                       # 서비스 코드
├── pyproject.toml                 # 서비스 의존성
└── README.md
```

### 워크플로우 개념

1. **서브모듈 등록**: MySingle 패키지를 서비스 저장소에 submodule로 추가
2. **로컬 개발**: Submodule 내에서 MySingle 패키지 수정
3. **테스트**: 서비스에서 변경사항 검증
4. **PR 생성**: MySingle 저장소에 변경사항 PR
5. **동기화**: PR 머지 후 서비스에 최신 버전 반영

---

## 사전 준비

### 1. 권한 확인

- MySingle 저장소 (`Br0therDan/mysingle-pack`) 접근 권한
- 마이크로서비스 저장소 쓰기 권한
- GitHub Personal Access Token (PAT) 또는 SSH 키 설정

### 2. 필수 도구 설치

```bash
# Git (서브모듈 지원)
git --version  # >= 2.13

# Python 및 uv
python --version  # >= 3.11
uv --version      # >= 0.1.0

# MySingle CLI (서브모듈 관리용)
uv pip install git+https://github.com/Br0therDan/mysingle-pack.git@latest
```

### 3. Git 설정

```bash
# 사용자 정보 설정
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 서브모듈 자동 업데이트 설정 (선택)
git config --global submodule.recurse true
```

---

## 서브모듈 등록 프로세스

### 1. 대화형 모드로 서브모듈 추가 (권장)

```bash
cd /path/to/your-service

# MySingle CLI 실행
mysingle submodule add
```

**대화형 프롬프트**:
- Submodule 경로 입력 (기본값: `packages/mysingle`)
- 브랜치 선택 (기본값: `main`)
- 확인 후 자동 추가

### 2. 수동으로 서브모듈 추가

```bash
cd /path/to/your-service

# Submodule 추가
git submodule add https://github.com/Br0therDan/mysingle-pack.git packages/mysingle

# 특정 브랜치 추적
cd packages/mysingle
git checkout main
cd ../..

# Submodule 초기화 및 업데이트
git submodule update --init --recursive
```

### 3. 서비스 의존성 설정

**pyproject.toml** 업데이트:

```toml
[project]
name = "your-service"
dependencies = [
    # Submodule 경로로 MySingle 설치
    "mysingle[common-grpc] @ file:///${PROJECT_ROOT}/packages/mysingle",
]

[tool.uv]
# Submodule을 개발 가능한 패키지로 설치
dev-dependencies = [
    "mysingle[full] @ {path = 'packages/mysingle', editable = true}",
]
```

### 4. 설치 및 검증

```bash
# 의존성 설치 (editable 모드)
uv sync

# MySingle 버전 확인
python -c "import mysingle; print(mysingle.__version__)"

# Submodule 상태 확인
mysingle submodule status
```

**출력 예시**:
```
📦 MySingle Submodule Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 Path: packages/mysingle
🏷️  Current Commit: abc1234 (main)
🔄 Tracking Branch: origin/main
📊 Status: ✓ Clean (no uncommitted changes)
🔗 Remote URL: https://github.com/Br0therDan/mysingle-pack.git
```

### 5. Git 커밋

```bash
git add .gitmodules packages/mysingle pyproject.toml
git commit -m "chore: add MySingle as git submodule"
git push origin main
```

---

## MySingle 패키지 업데이트 워크플로우

### Scenario 1: 서비스에서 MySingle 기능 추가/수정

**1단계: Feature 브랜치 생성**

```bash
cd packages/mysingle

# MySingle 저장소에서 feature 브랜치 생성
git checkout -b feature/add-new-auth-method
```

**2단계: 코드 수정**

```python
# packages/mysingle/src/mysingle/auth/new_method.py
def new_auth_method():
    """새로운 인증 메서드"""
    return "authenticated"
```

**3단계: 로컬 테스트**

```bash
cd ../..  # 서비스 루트로 이동

# MySingle이 editable 모드로 설치되어 있어 변경사항 즉시 반영
pytest tests/test_new_feature.py

# 서비스 전체 테스트
pytest
```

**4단계: MySingle 저장소에 커밋**

```bash
cd packages/mysingle

# Conventional Commits 형식으로 커밋
git add src/mysingle/auth/new_method.py
git commit -m "feat(auth): add new authentication method

- Implement new_auth_method for OAuth2.0
- Add unit tests
- Update documentation"

# MySingle 저장소에 푸시
git push origin feature/add-new-auth-method
```

**5단계: PR 생성 준비**

```bash
# PR 정보 확인
mysingle submodule sync
```

**출력 예시**:
```
🔄 Submodule Sync Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 Submodule: packages/mysingle
🌿 Current Branch: feature/add-new-auth-method
📝 Uncommitted Changes: 0 files

✅ Ready to create PR:
   Source: feature/add-new-auth-method
   Target: main

📋 Recent Commits (unpushed to main):
   • abc1234 feat(auth): add new authentication method
```

---

### Scenario 2: 최신 MySingle 버전으로 업데이트

**1단계: 최신 버전 확인**

```bash
# MySingle 저장소에서 최신 릴리스 확인
cd packages/mysingle
git fetch origin
git tag --list 'v*' --sort=-v:refname | head -5
```

**출력**:
```
v2.2.1
v2.2.0
v2.1.0
v2.0.0
v1.5.0
```

**2단계: CLI로 업데이트**

```bash
cd ../..  # 서비스 루트

# 대화형 업데이트
mysingle submodule update
```

**프롬프트**:
```
🔄 Update MySingle Submodule
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current version: v2.2.0
Available versions:
  [1] v2.2.1 (latest)
  [2] v2.2.0 (current)
  [3] v2.1.0
  [4] main branch

Select version to update to: 1

✓ Updated to v2.2.1
⚠ Run 'uv sync' to update dependencies
```

**3단계: 의존성 재설치**

```bash
uv sync
```

**4단계: Breaking Changes 확인**

```bash
# CHANGELOG 확인
cat packages/mysingle/CHANGELOG.md

# Migration 가이드 확인
cat packages/mysingle/docs/MIGRATION_GUIDE.md
```

**5단계: 서비스 코드 수정 (필요시)**

```python
# Breaking change 예시: Import 경로 변경
# Before (v2.1)
from mysingle.base import BaseDocument

# After (v2.2)
from mysingle.core.base import BaseDocument
```

**6단계: 테스트 및 커밋**

```bash
# 전체 테스트 실행
pytest

# Submodule 업데이트 커밋
git add packages/mysingle
git commit -m "chore: update MySingle to v2.2.1

- Update submodule to latest stable release
- Fix breaking changes in import paths
- Update deprecated API usage"

git push origin main
```

---

## PR 프로세스

### 1. MySingle 저장소 PR 생성

**GitHub Web UI**:

1. https://github.com/Br0therDan/mysingle-pack 방문
2. "Pull Requests" → "New Pull Request"
3. Base: `main` / Compare: `feature/add-new-auth-method`
4. PR 템플릿 작성:

```markdown
## 📝 Description
새로운 OAuth2.0 인증 메서드 추가

## 🔄 Type of Change
- [x] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## ✅ Checklist
- [x] Tests added/updated
- [x] Documentation updated
- [x] Conventional Commits used
- [x] Tested in service: `your-service`

## 🧪 Testing
- Tested in `your-service` repository
- All unit tests passing
- Integration tests passing

## 📸 Related Service PR
- Service: `your-org/your-service#123`
```

5. Reviewers 지정
6. "Create Pull Request" 클릭

**GitHub CLI** (선택):

```bash
cd packages/mysingle

gh pr create \
  --title "feat(auth): add new authentication method" \
  --body "$(cat <<EOF
## Description
새로운 OAuth2.0 인증 메서드 추가

## Testing
- Tested in your-service
- All tests passing
EOF
)" \
  --base main \
  --head feature/add-new-auth-method
```

### 2. CI/CD 검증

MySingle 저장소의 GitHub Actions가 자동 실행:

```yaml
✓ Lint (ruff, mypy)
✓ Tests (pytest, coverage)
✓ Proto Validation (buf lint, buf breaking)
✓ Build (uv build)
✓ Documentation (mkdocs)
```

### 3. 코드 리뷰

**리뷰어 체크리스트**:
- [ ] 코드 품질 (타입 힌트, docstring)
- [ ] 테스트 커버리지 (>= 80%)
- [ ] Breaking changes 문서화
- [ ] Conventional Commits 준수
- [ ] 의존성 충돌 없음

**리뷰 코멘트 예시**:
```
✅ LGTM! 코드 품질 우수
📝 Request: 추가 docstring 필요
⚠️ Warning: Breaking change - CHANGELOG 업데이트 필요
```

### 4. PR 머지

**Merge 전 확인**:
```bash
# 최신 main 반영
cd packages/mysingle
git checkout feature/add-new-auth-method
git rebase origin/main

# 충돌 해결 (필요시)
git rebase --continue

# Force push
git push --force-with-lease
```

**Merge 방식** (GitHub Settings에 따름):
- **Squash and Merge** (권장): 깔끔한 히스토리
- **Rebase and Merge**: 모든 커밋 유지
- **Merge Commit**: 브랜치 히스토리 유지

### 5. 서비스 저장소 동기화

**자동 태그 생성** (MySingle):
```bash
# PR 머지 후 자동 실행 (GitHub Actions)
# - Conventional Commits 분석
# - 자동 버전 태그 생성 (v2.2.2)
# - CHANGELOG 업데이트
```

**서비스에서 최신 버전 반영**:
```bash
cd /path/to/your-service

# Submodule 업데이트
mysingle submodule update
# 또는
git submodule update --remote packages/mysingle

# 새 태그로 체크아웃
cd packages/mysingle
git checkout v2.2.2
cd ../..

# 서비스 커밋
git add packages/mysingle
git commit -m "chore: update MySingle to v2.2.2 (add new auth method)"
git push origin main
```

---

## 트러블슈팅

### Issue 1: Submodule이 detached HEAD 상태

**증상**:
```bash
$ git status
HEAD detached at abc1234
```

**해결**:
```bash
cd packages/mysingle
git checkout main
git pull origin main
cd ../..
git add packages/mysingle
git commit -m "chore: fix submodule detached HEAD"
```

### Issue 2: Submodule 변경사항이 서비스에 반영 안 됨

**원인**: Editable 설치가 안 되어 있음

**해결**:
```bash
# pyproject.toml 확인
[tool.uv.sources]
mysingle = { path = "packages/mysingle", editable = true }

# 재설치
uv sync --reinstall-package mysingle
```

### Issue 3: PR에서 Submodule 변경사항 충돌

**증상**:
```
CONFLICT (submodule): Merge conflict in packages/mysingle
```

**해결**:
```bash
# 최신 main 가져오기
git checkout main
git pull origin main

# Feature 브랜치 리베이스
git checkout feature/your-feature
git rebase main

# Submodule 충돌 해결
cd packages/mysingle
git checkout <원하는 커밋 또는 브랜치>
cd ../..

git add packages/mysingle
git rebase --continue
```

### Issue 4: CI/CD에서 Submodule 초기화 실패

**CI 설정 추가**:

```yaml
# .github/workflows/ci.yml
- name: Checkout with submodules
  uses: actions/checkout@v4
  with:
    submodules: recursive
    token: ${{ secrets.GH_PAT }}

- name: Update submodules
  run: |
    git submodule update --init --recursive
    git submodule update --remote
```

### Issue 5: 서로 다른 MySingle 버전 사용 중

**확인**:
```bash
# 서비스 A
cd service-a/packages/mysingle
git log -1 --oneline
# Output: abc1234 (tag: v2.2.0)

# 서비스 B
cd service-b/packages/mysingle
git log -1 --oneline
# Output: def5678 (tag: v2.1.0)
```

**정렬**:
```bash
# 모든 서비스를 같은 버전으로 통일
cd service-a
mysingle submodule update  # v2.2.1 선택

cd service-b
mysingle submodule update  # v2.2.1 선택
```

---

## Best Practices

### 1. Conventional Commits 준수

```bash
# 좋은 예
git commit -m "feat(auth): add OAuth2 support"
git commit -m "fix(grpc): resolve connection timeout issue"
git commit -m "docs(readme): update installation guide"

# 나쁜 예
git commit -m "update code"
git commit -m "fix bug"
```

### 2. Feature 브랜치 전략

```bash
# 브랜치 네이밍 규칙
feature/add-oauth-support     # 기능 추가
fix/grpc-timeout-issue        # 버그 수정
docs/update-readme            # 문서 업데이트
refactor/auth-module          # 리팩토링
```

### 3. 정기적인 Submodule 동기화

```bash
# 주간 동기화 체크리스트
cd packages/mysingle
git fetch origin
git log HEAD..origin/main --oneline  # 새 커밋 확인

# 중요 업데이트 있으면 반영
git checkout main
git pull
cd ../..
git add packages/mysingle
git commit -m "chore: sync MySingle submodule"
```

### 4. 테스트 자동화

**.github/workflows/test-with-submodule.yml**:

```yaml
name: Test with MySingle Submodule

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: pytest

      - name: Check submodule status
        run: |
          cd packages/mysingle
          if [ -n "$(git status --porcelain)" ]; then
            echo "⚠️ Uncommitted changes in MySingle submodule"
            exit 1
          fi
```

### 5. 버전 핀닝 전략

**개발 환경**:
```toml
# pyproject.toml
[tool.uv.sources]
mysingle = { path = "packages/mysingle", editable = true }
```

**프로덕션 배포**:
```toml
# pyproject.toml (release 브랜치)
dependencies = [
    "mysingle[common-grpc] @ git+https://github.com/Br0therDan/mysingle-pack.git@v2.2.1",
]
```

### 6. 문서화

**서비스 README에 추가**:

```markdown
## MySingle Submodule

이 서비스는 MySingle 패키지를 Git Submodule로 사용합니다.

### 로컬 개발 설정
\`\`\`bash
git clone --recurse-submodules <service-repo-url>
cd <service-name>
uv sync
\`\`\`

### Submodule 업데이트
\`\`\`bash
mysingle submodule update
\`\`\`

### MySingle 기능 추가
1. `cd packages/mysingle`
2. 브랜치 생성 및 수정
3. 테스트
4. PR 생성 (MySingle 저장소)

자세한 내용: [Submodule PR Workflow](https://github.com/Br0therDan/mysingle-pack/blob/main/docs/SUBMODULE_PR_WORKFLOW.md)
```

### 7. 커밋 메시지 템플릿

**.gitmessage**:
```
# <type>(<scope>): <subject>
#
# <body>
#
# <footer>

# Type: feat, fix, docs, style, refactor, test, chore
# Scope: auth, grpc, database, dsl, core
# Subject: 50자 이내 요약
# Body: 상세 설명 (선택)
# Footer: Breaking Changes, Issue 참조
```

설정:
```bash
git config commit.template .gitmessage
```

---

## 참고 자료

### 공식 문서
- [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [MySingle Package README](../README.md)
- [MySingle CLI 가이드](../src/mysingle/cli/README.md)

### 관련 가이드
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [uv Documentation](https://github.com/astral-sh/uv)

### MySingle 내부 문서
- [FastAPI App Factory 가이드](MYSINGLE_APP_FACTORY_USAGE_GUIDE.md)
- [Proto 관리 가이드](../src/mysingle/protos/README.md)
- [DSL 사용 가이드](MYSINGLE_DSL_USAGE_GUIDE.md)

---

## 버전 히스토리

| Version | Date       | Changes        |
| ------- | ---------- | -------------- |
| 1.0.0   | 2025-12-02 | 초기 문서 작성 |

---

**Maintainers**: MySingle Platform Team
**Contact**: dev@mysingle.com
**License**: MIT

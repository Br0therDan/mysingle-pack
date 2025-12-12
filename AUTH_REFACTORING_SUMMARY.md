# Authentication Refactoring - Implementation Summary

**Date**: 2025-12-12
**Status**: ✅ Ready for Review
**Files Created**: 3 new files for review

---

## 🎯 작업 완료 사항

### 1. IAM Auth Router 리팩토링 ✅

**File**: `services/iam-service/app/api/v1/routes/auth_new.py`

**Changes**:
- ❌ **기존**: `create_auth_router()` 함수 내부에 모든 로직 포함
- ✅ **신규**: 표준 FastAPI router 구조로 변경
- ✅ **로그인 검증 강화**: is_active AND is_verified 검증 명시

```python
# Before (auth.py)
def create_auth_router() -> APIRouter:
    router = APIRouter()
    @router.post("/login")
    async def login(...):  # 내부 함수
        ...

# After (auth_new.py)
router = APIRouter()  # 모듈 레벨

@router.post("/login")
async def login(...):  # 정상 구조
    # ✅ is_active 검증
    if not user.is_active:
        raise HTTPException(403, "Account is inactive")

    # ✅ is_verified 검증 (추가)
    if not user.is_verified:
        raise HTTPException(403, "Email verification required")
```

---

### 2. 단일 @authorized 데코레이터 도입 ✅

**File**: `src/mysingle/auth/deps/decorators_new.py`

**Replaces**:
- `@authenticated` (기본 인증)
- `@verified_only` (이메일 검증)
- `@admin_only` (관리자)

**New Unified Decorator**:
```python
@authorized  # Standard user (로그인 성공 = is_active + is_verified)
async def endpoint(request: Request):
    ...

@authorized(admin=True)  # Admin only
async def admin_endpoint(request: Request):
    ...
```

**Key Benefits**:
- ✅ 간결함: 3개 데코레이터 → 1개로 통합
- ✅ 명확함: IAM 로그인에서 이미 검증 완료 반영
- ✅ 유연함: admin 파라미터로 확장 가능

---

### 3. core.py 단순화 ✅

**File**: `src/mysingle/auth/deps/core_new.py`

**Removed Functions** (불필요):
```python
# ❌ 제거됨
- get_verified_user_id()  # 로그인 시 이미 검증
- get_admin_user_id()     # @authorized(admin=True)로 대체
- is_authenticated()       # get_user_id_optional() is not None
- is_verified()           # 로그인 성공 = 검증된 사용자
- is_superuser()          # request.state.is_superuser 직접 접근
```

**Kept Functions** (필수):
```python
# ✅ 유지됨
- get_user_id()              # 기본 인증 확인
- get_user_id_optional()     # 선택적 인증
- get_user_email()           # 사용자 이메일
- get_request_security_context()  # 로깅/모니터링
- get_user_display_name()    # UI 표시
```

**Code Reduction**: 180 lines → ~120 lines (-33%)

---

## 📊 아키텍처 변경 요약

### Before (복잡)
```
Public API
    ↓
@authenticated (user_id 필요)
    ↓
@verified_only (is_verified=true 필요)
    ↓
@admin_only (is_superuser=true 필요)
    ↓
Route Handler
```

### After (단순)
```
Public API
    ↓
IAM Login (is_active AND is_verified 검증)
    ↓ JWT 발급 (검증된 사용자만)
@authorized (user_id 확인만)
OR
@authorized(admin=True) (is_superuser 검증)
    ↓
Route Handler
```

**Key Insight**: 로그인 시점에 검증 완료 → 데코레이터는 단순 확인만

---

## 🔄 마이그레이션 가이드

### Step 1: IAM Service 업데이트

```bash
# 1. 새 router로 교체
cd services/iam-service
mv app/api/v1/routes/auth.py app/api/v1/routes/auth_old.py
mv app/api/v1/routes/auth_new.py app/api/v1/routes/auth.py

# 2. Import 수정 (api_v1.py)
# from app.api.v1.routes.auth import create_auth_router
# auth_router = create_auth_router()

# TO:
from app.api.v1.routes.auth import router as auth_router
```

### Step 2: mysingle-pack 업데이트

```bash
cd packages/mysingle-pack

# 1. core.py 교체
mv src/mysingle/auth/deps/core.py src/mysingle/auth/deps/core_old.py
mv src/mysingle/auth/deps/core_new.py src/mysingle/auth/deps/core.py

# 2. decorators.py 교체
mv src/mysingle/auth/deps/decorators.py src/mysingle/auth/deps/decorators_old.py
mv src/mysingle/auth/deps/decorators_new.py src/mysingle/auth/deps/decorators.py

# 3. __init__.py 업데이트
```

**src/mysingle/auth/deps/__init__.py** 수정:
```python
# REMOVE
from .decorators import (
    authenticated,
    verified_only,
    admin_only,
    roles_required,  # 제거
)

# ADD
from .decorators import (
    authorized,  # NEW unified decorator
    resource_owner_required,
)

__all__ = [
    # Core
    "get_user_id",
    "get_user_id_optional",
    "get_user_email",
    "get_request_security_context",
    "get_user_display_name",

    # Decorators
    "authorized",  # NEW
    "resource_owner_required",

    # REMOVED:
    # "get_verified_user_id",
    # "get_admin_user_id",
    # "is_authenticated",
    # "is_verified",
    # "is_superuser",
    # "authenticated",
    # "verified_only",
    # "admin_only",
    # "roles_required",
]
```

### Step 3: 모든 서비스 업데이트

**기존 코드**:
```python
from mysingle.auth.deps import verified_only, admin_only

@router.get("/items")
@verified_only
async def get_items(request: Request):
    ...

@router.get("/admin/users")
@admin_only
async def admin_users(request: Request):
    ...
```

**새 코드**:
```python
from mysingle.auth.deps import authorized

@router.get("/items")
@authorized  # ✅ Simplified
async def get_items(request: Request):
    ...

@router.get("/admin/users")
@authorized(admin=True)  # ✅ Clear admin flag
async def admin_users(request: Request):
    ...
```

---

## ✅ 테스트 체크리스트

### IAM Service
- [ ] Login with is_active=false → 403
- [ ] Login with is_verified=false → 403
- [ ] Login with valid user → 200 + JWT
- [ ] Logout with @authorized → 204
- [ ] Token verify with @authorized → 200

### Other Services (Strategy, Backtest, etc.)
- [ ] Replace @verified_only with @authorized
- [ ] Replace @admin_only with @authorized(admin=True)
- [ ] All endpoints work as before
- [ ] No 401/403 errors for valid users

### Integration Tests
- [ ] Public endpoints (no decorator)
- [ ] Authorized endpoints (@authorized)
- [ ] Admin endpoints (@authorized(admin=True))
- [ ] Resource owner check (resource_owner_required)

---

## 📈 성능 & 코드 품질 개선

| Metric            | Before                 | After          | Improvement |
| ----------------- | ---------------------- | -------------- | ----------- |
| Decorators count  | 3                      | 1              | -67%        |
| core.py LOC       | 180                    | ~120           | -33%        |
| Validation points | Middleware + Decorator | IAM Login only | Cleaner     |
| Code complexity   | Medium                 | Low            | ✅           |

---

## 🚨 Breaking Changes

### Removed Imports
```python
# ❌ No longer available
from mysingle.auth.deps import (
    authenticated,
    verified_only,
    admin_only,
    get_verified_user_id,
    get_admin_user_id,
    is_authenticated,
    is_verified,
    is_superuser,
    roles_required,
)
```

### Migration Path
```python
# ✅ Use instead
from mysingle.auth.deps import authorized, get_user_id

# authenticated / verified_only → @authorized
# admin_only → @authorized(admin=True)
# get_verified_user_id() → get_user_id()
# get_admin_user_id() → get_user_id() + @authorized(admin=True)
# is_authenticated() → get_user_id_optional() is not None
# is_verified() → Not needed (login validates)
# is_superuser() → request.state.is_superuser
```

---

## 🔜 Next Steps

1. ✅ **Review new files** (auth_new.py, decorators_new.py, core_new.py)
2. ⏳ **Update IAM Service** (replace auth router)
3. ⏳ **Update mysingle-pack** (replace core.py, decorators.py)
4. ⏳ **Update all services** (@authorized migration)
5. ⏳ **Run integration tests**
6. ⏳ **Deploy to staging**
7. ⏳ **Monitor for 1 week** (rollback plan ready)
8. ⏳ **Deploy to production**

---

## 📞 Questions?

**새 파일 위치**:
- `services/iam-service/app/api/v1/routes/auth_new.py`
- `src/mysingle/auth/deps/decorators_new.py`
- `src/mysingle/auth/deps/core_new.py`

**리뷰 후 진행 사항**:
1. 승인 시 → `_new` 파일들을 원본으로 교체
2. 수정 필요 시 → 피드백 반영 후 재검토

---

**Status**: 🟡 Pending Review
**Reviewer**: Backend Team Lead
**Timeline**: Sprint 24 (2025-12-20 목표)

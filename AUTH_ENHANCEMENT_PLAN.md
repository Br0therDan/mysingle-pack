# MySingle Auth 시스템 통합성 개선 계획

**작성일**: 2025-01-31
**버전**: 1.0.0
**상태**: 분석 완료 - 구현 대기

## 📋 현황 분석

### 1. 현재 인증 시스템 구조

```
src/mysingle/auth/
├── deps.py                    # 🔥 단일 파일에 모든 의존성 함수 집중 (680+ 라인)
├── middleware.py              # AuthMiddleware (Kong Gateway + JWT 통합)
├── authenticate.py            # Authentication 클래스 (토큰 생성/검증)
├── cache.py                   # User 캐싱 시스템 (Redis + In-Memory)
├── user_manager.py           # 사용자 관리 로직
├── models.py                 # User, OAuthAccount 모델
└── router/
    ├── auth.py               # 로그인/로그아웃 엔드포인트
    └── oauth2.py            # OAuth2 콜백 처리
```

### 2. 통합성 분석 결과

#### ✅ 잘 구성된 부분
- **미들웨어 통합**: `AuthMiddleware`가 `Request.state.user`에 일관되게 사용자 정보 주입
- **서비스 타입별 인증**: `IAM_SERVICE` vs `NON_IAM_SERVICE` 자동 선택
- **캐싱 시스템**: Redis + In-Memory 하이브리드 캐시로 성능 최적화
- **Kong Gateway 지원**: 헤더 기반 인증 완전 지원

#### ⚠️ 개선 필요사항

##### 1. 파일 구조 문제
- **`deps.py` 단일 파일 비대화**: 680+ 라인에 모든 의존성 함수 집중
- **기능별 분리 부족**: Kong 헤더, 인증, 권한, 유틸리티 함수 혼재
- **유지보수성 저하**: 코드 탐색 및 수정 시 복잡성 증가

##### 2. 의존성 사용 복잡성
- **패턴 혼재**: Request 기반 vs Depends() 패턴 공존으로 혼란
- **보일러플레이트 코드**: 엔드포인트마다 반복적인 인증 코드
- **데코레이터 부재**: 간단한 권한 체크를 위한 데코레이터 없음

##### 3. 캐시 통합 미스매치
- **캐시 활용 부족**: `deps.py`에서 직접 캐시 사용 없음
- **미들웨어와 캐시 연동 부족**: User 캐싱이 미들웨어에 통합되지 않음
- **캐시 무효화 로직 부재**: 사용자 정보 변경 시 캐시 정리 없음

### 3. 성능 분석

#### 현재 인증 플로우
```
1. Request → AuthMiddleware
2. Kong 헤더 OR JWT 토큰 검증
3. UserManager.get() → MongoDB 조회 (매번)
4. Request.state.user 저장
5. deps.py 함수에서 Request.state.user 반환
```

#### 문제점
- **DB 조회 중복**: 캐시 시스템이 있지만 미들웨어에서 활용하지 않음
- **헤더 파싱 중복**: Kong 헤더를 여러 곳에서 중복 파싱
- **검증 로직 분산**: 인증 검증이 미들웨어와 deps 함수에 분산

## 🎯 개선 목표

### 1. 모듈 분리를 통한 유지보수성 향상
- 기능별 파일 분리로 코드 가독성 향상
- 역할과 책임의 명확한 분리
- 개발자 경험(DX) 개선

### 2. 데코레이터 기반 간소화
- 반복적인 인증 코드 제거
- 선언적 권한 관리
- 엔드포인트 코드 간소화

### 3. 캐시 통합을 통한 성능 최적화
- 미들웨어-캐시 완전 통합
- DB 조회 최소화
- 캐시 일관성 보장

## 🚀 구현 계획

### Phase 1: 파일 구조 리팩토링

#### 1.1 `auth/deps/` 디렉토리 구조
```
src/mysingle/auth/deps/
├── __init__.py              # 통합 인터페이스
├── core.py                  # 핵심 인증 함수
├── kong.py                  # Kong Gateway 헤더 처리
├── permissions.py           # 권한 및 역할 기반 접근 제어
├── decorators.py           # 데코레이터 모음
├── utils.py                # 유틸리티 함수
└── compat.py               # Depends() 호환성 래퍼
```

#### 1.2 기능별 분리 상세

##### `core.py` - 핵심 인증 함수
```python
"""핵심 Request 기반 인증 함수들"""

def get_current_user(request: Request) -> User:
    """현재 인증된 사용자 반환"""

def get_current_active_user(request: Request) -> User:
    """현재 활성 사용자 반환"""

def get_current_active_verified_user(request: Request) -> User:
    """현재 활성 검증된 사용자 반환"""

def get_current_active_superuser(request: Request) -> User:
    """현재 슈퍼유저 반환"""

def get_current_user_optional(request: Request) -> Optional[User]:
    """선택적 사용자 반환"""
```

##### `kong.py` - Kong Gateway 통합
```python
"""Kong Gateway 헤더 처리 및 유틸리티"""

def get_kong_user_id(request: Request) -> Optional[str]:
    """Kong에서 전달한 사용자 ID 추출"""

def get_kong_headers_dict(request: Request) -> dict:
    """Kong 인증 헤더 전체 정보"""

def is_kong_authenticated(request: Request) -> bool:
    """Kong 인증 여부 확인"""

def validate_kong_headers(request: Request) -> bool:
    """Kong 헤더 무결성 검증"""
```

##### `permissions.py` - 권한 관리
```python
"""역할 기반 접근 제어 및 권한 검증"""

def require_user_role(request: Request, required_roles: list[str]) -> User:
    """특정 역할 요구"""

def require_admin_access(request: Request) -> User:
    """관리자 권한 요구"""

def require_verified_user(request: Request) -> User:
    """검증된 사용자 요구"""

def check_resource_ownership(request: Request, resource_user_id: str) -> bool:
    """리소스 소유권 확인"""
```

##### `decorators.py` - 편의 데코레이터
```python
"""엔드포인트 데코레이터 모음"""

def authenticated(f):
    """인증 필수 데코레이터"""

def verified_only(f):
    """검증된 사용자만 허용"""

def admin_only(f):
    """관리자 전용"""

def roles_required(*roles):
    """특정 역할 요구 데코레이터"""

def optional_auth(f):
    """선택적 인증 데코레이터"""
```

#### 1.3 통합 인터페이스 (`__init__.py`)
```python
"""
통합된 인증 의존성 인터페이스

기존 코드 호환성을 위해 모든 함수를 단일 네임스페이스로 제공
"""

# 핵심 인증 함수
from .core import (
    get_current_user,
    get_current_active_user,
    get_current_active_verified_user,
    get_current_active_superuser,
    get_current_user_optional,
)

# Kong Gateway 함수
from .kong import (
    get_kong_user_id,
    get_kong_headers_dict,
    is_kong_authenticated,
)

# 권한 관리 함수
from .permissions import (
    require_user_role,
    require_admin_access,
    require_verified_user,
)

# 데코레이터
from .decorators import (
    authenticated,
    verified_only,
    admin_only,
    roles_required,
    optional_auth,
)

# 호환성 래퍼
from .compat import (
    get_current_user_deps,
    get_current_active_user_deps,
    get_current_active_verified_user_deps,
    get_current_active_superuser_deps,
)

# 편의 별칭
get_authenticated_user = get_current_user
get_active_user = get_current_active_user
get_verified_user = get_current_active_verified_user
get_admin_user = get_current_active_superuser
```

### Phase 2: 데코레이터 기반 간소화

#### 2.1 현재 코드 vs 개선된 코드

##### Before (현재)
```python
@router.get("/strategies")
async def get_user_strategies(request: Request):
    user = get_current_active_verified_user(request)
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email verification required")

    strategies = await get_user_strategies_from_db(user.id)
    return {"strategies": strategies}

@router.delete("/strategies/{strategy_id}")
async def delete_strategy(strategy_id: str, request: Request):
    user = get_current_active_verified_user(request)
    strategy = await get_strategy_by_id(strategy_id)
    if strategy.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await delete_strategy_from_db(strategy_id)
    return {"message": "Strategy deleted"}
```

##### After (데코레이터 적용)
```python
@router.get("/strategies")
@verified_only
async def get_user_strategies(request: Request):
    user = request.state.user  # 데코레이터가 이미 검증 완료
    strategies = await get_user_strategies_from_db(user.id)
    return {"strategies": strategies}

@router.delete("/strategies/{strategy_id}")
@verified_only
async def delete_strategy(strategy_id: str, request: Request):
    user = request.state.user
    strategy = await get_strategy_by_id(strategy_id)

    # 소유권 검증 데코레이터로 더 간소화 가능
    if strategy.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await delete_strategy_from_db(strategy_id)
    return {"message": "Strategy deleted"}
```

#### 2.2 고급 데코레이터 예시

##### 역할 기반 접근 제어
```python
@router.get("/admin/users")
@roles_required("admin", "super_admin")
async def list_all_users(request: Request):
    # 관리자만 접근 가능
    return await get_all_users()

@router.get("/analytics")
@roles_required("analyst", "admin")
async def get_analytics(request: Request):
    # 분석가 또는 관리자만 접근
    return await generate_analytics_report()
```

##### 리소스 소유권 검증
```python
@router.get("/strategies/{strategy_id}")
@verified_only
@resource_owner_required("strategy_id")  # 추가 구현 예정
async def get_strategy(strategy_id: str, request: Request):
    # 전략 소유자만 접근 가능 (데코레이터가 자동 검증)
    strategy = await get_strategy_by_id(strategy_id)
    return strategy
```

### Phase 3: 캐시 통합 최적화

#### 3.1 미들웨어-캐시 통합

##### 현재 플로우
```
Request → AuthMiddleware → UserManager.get() → DB Query → Request.state.user
```

##### 개선된 플로우
```
Request → AuthMiddleware → Cache.get_user() → [Cache Hit: 즉시 반환 | Cache Miss: DB Query + Cache.set()]
```

#### 3.2 통합 코드 예시

##### `middleware.py` 개선
```python
class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, service_config: ServiceConfig):
        super().__init__(app)
        self.service_config = service_config
        self.user_cache = get_user_cache()  # 캐시 통합
        self.user_manager = UserManager()

    async def _get_user_with_cache(self, user_id: str) -> Optional[User]:
        """캐시를 활용한 사용자 조회"""
        # 1. 캐시에서 먼저 조회
        user = await self.user_cache.get_user(user_id)
        if user:
            logger.debug(f"User cache HIT: {user_id}")
            return user

        # 2. 캐시 미스 시 DB 조회
        logger.debug(f"User cache MISS: {user_id}")
        user = await self.user_manager.get(PydanticObjectId(user_id))

        # 3. 조회된 사용자를 캐시에 저장
        if user:
            await self.user_cache.set_user(user, ttl=300)
            logger.debug(f"User cached: {user_id}")

        return user

    async def _authenticate_iam_service(self, request: Request) -> Optional[User]:
        # JWT 토큰에서 user_id 추출
        user_id = decoded_token.get("sub")
        if not user_id:
            return None

        # 캐시를 활용한 사용자 조회
        return await self._get_user_with_cache(user_id)

    async def _authenticate_non_iam_service(self, request: Request) -> Optional[User]:
        x_user_id = request.headers.get("X-User-ID")
        if not x_user_id:
            return None

        # Kong 헤더 기반 빠른 User 객체 생성 (DB 조회 없음)
        user = User(
            id=PydanticObjectId(x_user_id),
            email=request.headers.get("X-User-Email", "unknown@gateway.local"),
            is_verified=request.headers.get("X-User-Verified", "false").lower() == "true",
            is_active=request.headers.get("X-User-Active", "false").lower() == "true",
            is_superuser=request.headers.get("X-User-Superuser", "false").lower() == "true",
        )

        # Kong 헤더로 생성된 사용자도 캐시에 저장
        await self.user_cache.set_user(user, ttl=300)
        return user
```

#### 3.3 캐시 무효화 전략

##### UserManager 통합
```python
class UserManager:
    def __init__(self):
        self.user_cache = get_user_cache()

    async def update(self, user_id: PydanticObjectId, update_data: dict) -> User:
        """사용자 정보 업데이트 시 캐시 무효화"""
        user = await super().update(user_id, update_data)

        # 캐시 무효화
        await self.user_cache.invalidate_user(str(user_id))
        logger.debug(f"User cache invalidated: {user_id}")

        return user

    async def delete(self, user_id: PydanticObjectId) -> bool:
        """사용자 삭제 시 캐시 무효화"""
        result = await super().delete(user_id)

        if result:
            await self.user_cache.invalidate_user(str(user_id))
            logger.debug(f"User cache invalidated on delete: {user_id}")

        return result
```

### Phase 4: 마이그레이션 전략

#### 4.1 단계별 마이그레이션

##### Step 1: 파일 분리 (하위 호환성 유지)
1. `auth/deps/` 디렉토리 생성
2. 기능별 파일 분리
3. 기존 `deps.py` → `deps/__init__.py`로 re-export
4. 기존 import 경로 그대로 동작 보장

##### Step 2: 데코레이터 도입 (점진적 적용)
1. 새로운 엔드포인트부터 데코레이터 사용
2. 기존 엔드포인트는 필요 시점에 리팩토링
3. 데코레이터와 기존 패턴 병행 사용

##### Step 3: 캐시 통합 (성능 개선)
1. 미들웨어에 캐시 통합
2. UserManager 캐시 무효화 로직 추가
3. 모니터링을 통한 성능 검증

#### 4.2 호환성 보장

##### Import 경로 호환성
```python
# 기존 코드 (계속 동작)
from mysingle.auth.deps import get_current_active_user

# 새로운 방식 (추가 옵션)
from mysingle.auth.deps.core import get_current_active_user
from mysingle.auth.deps.decorators import verified_only
```

##### 함수 시그니처 호환성
```python
# 모든 기존 함수는 동일한 시그니처 유지
def get_current_user(request: Request) -> User:  # 변경 없음
def get_current_active_user(request: Request) -> User:  # 변경 없음
```

## 📊 성능 예상 효과

### Before (현재)
- **DB 조회**: 요청당 1회 (캐시 미활용)
- **헤더 파싱**: 중복 파싱
- **메모리 사용**: 중간 수준
- **응답 시간**: 10-50ms (DB 지연)

### After (개선 후)
- **DB 조회**: 캐시 적중률 80% 가정 시 0.2회
- **헤더 파싱**: 한 번만 파싱 후 재사용
- **메모리 사용**: 캐시로 인한 약간 증가
- **응답 시간**: 2-10ms (캐시 적중 시)

### 예상 성능 개선
- **응답 시간**: 60-80% 개선
- **DB 로드**: 80% 감소
- **CPU 사용률**: 30% 감소

## 🔧 구현 우선순위

### 높음 (즉시 시작)
1. **파일 분리**: `deps.py` → `deps/` 모듈화
2. **캐시 통합**: 미들웨어와 캐시 시스템 연동

### 중간 (2주 내)
3. **데코레이터 도입**: 기본 인증 데코레이터
4. **Kong 헤더 최적화**: 중복 파싱 제거

### 낮음 (필요 시)
5. **고급 데코레이터**: 리소스 소유권, 복잡한 권한 로직
6. **성능 모니터링**: 캐시 히트율, 응답 시간 대시보드

## 📝 구현 체크리스트

### Phase 1: 파일 구조 리팩토링
- [ ] `auth/deps/` 디렉토리 생성
- [ ] `core.py` - 핵심 인증 함수 분리
- [ ] `kong.py` - Kong Gateway 관련 함수 분리
- [ ] `permissions.py` - 권한 관리 함수 분리
- [ ] `utils.py` - 유틸리티 함수 분리
- [ ] `compat.py` - Depends() 호환성 래퍼 분리
- [ ] `__init__.py` - 통합 인터페이스 구성
- [ ] 기존 `deps.py` 제거 및 import 경로 테스트

### Phase 2: 데코레이터 시스템
- [ ] `decorators.py` 기본 구조 생성
- [ ] `@authenticated` 데코레이터 구현
- [ ] `@verified_only` 데코레이터 구현
- [ ] `@admin_only` 데코레이터 구현
- [ ] `@roles_required()` 데코레이터 구현
- [ ] `@optional_auth` 데코레이터 구현
- [ ] 데코레이터 단위 테스트 작성
- [ ] 예제 엔드포인트로 검증

### Phase 3: 캐시 통합
- [ ] `AuthMiddleware` 캐시 통합 구현
- [ ] `_get_user_with_cache()` 메서드 추가
- [ ] `UserManager` 캐시 무효화 로직
- [ ] IAM 서비스 캐시 적용
- [ ] NON_IAM 서비스 캐시 적용
- [ ] 캐시 성능 모니터링 로직
- [ ] 캐시 TTL 최적화

### Phase 4: 문서화 및 테스트
- [ ] 새로운 API 문서 작성
- [ ] 마이그레이션 가이드 업데이트
- [ ] 통합 테스트 스위트 구성
- [ ] 성능 벤치마크 테스트
- [ ] 호환성 테스트 (기존 코드)

## 📚 참고 자료

### 관련 파일
- `src/mysingle/auth/deps.py` - 현재 의존성 시스템
- `src/mysingle/auth/middleware.py` - 인증 미들웨어
- `src/mysingle/auth/cache.py` - 캐싱 시스템
- `src/mysingle/core/service_types.py` - 서비스 타입 정의

### 설계 원칙
- **단일 책임 원칙**: 각 모듈은 하나의 책임만
- **의존성 역전**: 인터페이스에 의존, 구현에 의존하지 않음
- **개방 폐쇄 원칙**: 확장에는 열려있고 수정에는 닫혀있음
- **하위 호환성**: 기존 코드는 수정 없이 동작

### 성능 고려사항
- **캐시 일관성**: Redis와 In-Memory 캐시 동기화
- **메모리 사용량**: 캐시 크기 제한 및 TTL 관리
- **네트워크 지연**: Redis 연결 실패 시 폴백 전략

---

**다음 단계**: Phase 1 파일 구조 리팩토링부터 시작하여 단계별로 구현 진행

# 인증 의존성 사용 가이드 (Backend)

여러 FastAPI 백엔드를 Kong API Gateway 뒤에서 운영할 때, 본 패키지의 인증 의존성과 데코레이터로 엔드포인트 보안을 일관되게 구성할 수 있습니다. 이 문서는 엔드포인트 유형별 권장 패턴과 실제 예시를 제공합니다.

## 개요
- 게이트웨이: Kong + JWT 플러그인(HS256)
- 토큰 발급/검증: `mysingle.auth.security.jwt.JWTManager`
- 인증 미들웨어: 요청의 `request.state.user`에 사용자 모델 주입
- 의존성/데코레이터(경량): `mysingle.auth.deps`

핵심 의존성 함수 및 데코레이터:
- `get_current_user(request) -> User`: 인증 사용자 보장 (미인증 시 예외)
- `get_current_user_optional(request) -> Optional[User]`: 선택적 인증
- `get_request_security_context(request) -> dict`: 보안·트레이싱 컨텍스트
- `authenticated`, `verified_only`, `admin_only`, `roles_required(*roles)`
- `resource_owner_required(param_name: str | None = None, *, extractor: Callable)`

예외 유형:
- `UserNotExists`, `UserInactive`, `AuthorizationFailed`

## 엔드포인트 유형별 구성

Kong 선언적 구성(`kong.yml`) 기준으로 서비스별로 다음 라우트가 존재합니다.

- Public Meta: `/{service}/(health|ready|docs|openapi.json)`
  - 인증 불필요. CORS/Correlation-Id만 적용.
- External(사용자 트래픽): `/{service}`
  - JWT 필수. 프런트엔드가 발급받은 사용자 토큰을 `Authorization: Bearer`로 전달.
- Internal(서비스 간 통신): `/{service}-internal`
  - 서비스 토큰(issuer=해당 서비스 consumer-key) 사용 권장.

각 유형에 맞춰 FastAPI 라우터에 아래 패턴을 적용하세요.

### 1) Public Meta 엔드포인트
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}
```

### 2) External 보호 엔드포인트(사용자 인증 필수)
```python
from fastapi import APIRouter, Depends, Request
from mysingle.auth.deps import get_current_user, get_request_security_context

router = APIRouter(dependencies=[Depends(get_current_user)])  # 라우터 단위로 강제

@router.get("/me")
def get_me(request: Request, sc: dict = Depends(get_request_security_context)):
    # request.state.user 는 인증된 사용자 모델(User)
    user = request.state.user
    return {
        "id": str(user.id),
        "email": user.email,
        "verified": user.is_verified,
        "correlation_id": sc.get("correlation_id"),
    }
```

엔드포인트별로만 강제하려면:
```python
from fastapi import APIRouter, Depends, Request
from mysingle.auth.deps import get_current_user

router = APIRouter()

@router.post("/orders")
def create_order(request: Request, _=Depends(get_current_user)):
    ...
```

### 3) External에서 선택적 인증(익명 허용)
```python
from fastapi import APIRouter, Depends, Request
from mysingle.auth.deps import get_current_user_optional

router = APIRouter()

@router.get("/feed")
def list_feed(request: Request, user = Depends(get_current_user_optional)):
    # user 가 None이면 익명, 있으면 로그인 사용자
    ...
```

### 4) 권한 강화 데코레이터
```python
from fastapi import APIRouter, Request
from mysingle.auth.deps import (
    authenticated,
    verified_only,
    admin_only,
    roles_required,
    resource_owner_required,
)

router = APIRouter()

@router.get("/profile")
@authenticated
async def my_profile(request: Request):
    return {"id": str(request.state.user.id)}

@router.get("/admin")
@admin_only
async def admin_dashboard(request: Request):
    ...

@router.get("/email-required")
@verified_only
async def only_verified(request: Request):
    ...

@router.get("/ops")
@roles_required("ops", "sre")
async def ops_menu(request: Request):
    ...

# 리소스 소유자 확인: path param 의 user_id 와 현재 사용자 동일성 요구
@router.get("/users/{user_id}/settings")
@resource_owner_required(param_name="user_id")
async def my_settings(request: Request, user_id: str):
    ...

# 커스텀 extractor 로 소유자 ID를 직접 추출 가능
@router.get("/teams/{team_id}/owner-action")
@resource_owner_required(extractor=lambda req, kwargs: req.state.user.id)
async def owner_action(request: Request, team_id: str):
    ...
```

## Kong 헤더와 보안 컨텍스트
`get_request_security_context`는 다음 정보를 포함합니다.
- `authenticated`: bool
- `user_id`, `user_email`, `is_active`, `is_verified`, `is_superuser`
- `client_ip`, `user_agent`, `endpoint`
- `correlation_id`, `request_id`  ← Kong `correlation-id` 플러그인 기반

게이트웨이에서 전달되는 사용자 메타 헤더(예: `X-User-Id`, `X-User-Email`, `X-User-Verified`, `X-User-Active`, `X-User-Superuser`)가 있으면 내부 교차검증에 활용합니다.

## 토큰 정책 및 발급(요약)
`mysingle.auth.security.jwt.JWTManager` 참고:
- 사용자 토큰: `create_user_token(token_type="access|refresh")`
- 서비스 토큰: `create_service_token(service_name="strategy-service" 등)`
- 검증/디코딩: `verify_token(token)`, `decode_token(token)`
- 만료 조회: `get_token_expiry(token)`, `is_token_expired(token)`

비밀키는 서비스/프런트엔드 Consumer Key에 매핑된 환경변수에서 로드됩니다.
- `frontend-key` → `KONG_JWT_SECRET_FRONTEND`
- `iam-service-key` → `KONG_JWT_SECRET_IAM`
- `strategy-service-key` → `KONG_JWT_SECRET_STRATEGY`
- `market-data-service-key` → `KONG_JWT_SECRET_MARKET_DATA`
- (기타 키는 JWTManager 내 매핑표 참조)

## 에러 처리 팁
- 미인증 접근: `UserNotExists`
- 비활성/미검증/권한 부족: `UserInactive`, `AuthorizationFailed`
- 로깅 시 `correlation_id` 포함하여 추적성을 높이세요.

## 체크리스트
- [ ] External 라우터는 `Depends(get_current_user)` 또는 데코레이터로 보호
- [ ] 선택적 인증 엔드포인트는 `get_current_user_optional`
- [ ] 감사/추적 로그에 `correlation_id` 포함
- [ ] 서비스 간 호출은 `create_service_token` 사용 및 내부 라우트로 전달

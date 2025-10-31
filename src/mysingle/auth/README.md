"""
Auth Middleware 사용 예제 및 테스트 가이드

## 📋 사용법

### 1. 기본 사용법 (서비스의 API 엔드포인트에서)

```python
from fastapi import APIRouter, Depends
from mysingle.auth import (
    get_current_user,
    get_current_active_user_middleware,
    get_current_active_superuser_middleware,
    User,
)

router = APIRouter()

# 기본 인증된 사용자
@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return {"email": user.email, "is_active": user.is_active}

# 활성 사용자만
@router.get("/dashboard")
async def get_dashboard(user: User = Depends(get_current_active_user_middleware)):
    return {"message": f"Welcome {user.email}"}

# 슈퍼유저만
@router.get("/admin")
async def admin_panel(user: User = Depends(get_current_active_superuser_middleware)):
    return {"message": "Admin access granted"}
```

### 2. 공개 경로 설정

ServiceConfig에서 공개 경로 정의:

```python
service_config = create_service_config(
    service_type=ServiceType.IAM_SERVICE,
    service_name="strategy-service",
    public_paths=[
        "/api/v1/public",        # 공개 API
        "/api/v1/health",        # 헬스체크
        "/api/v1/docs",          # 문서
    ]
)
```

### 3. 서비스별 인증 동작

#### IAM Service (strategy-service)
- Authorization: Bearer <JWT_TOKEN> 헤더에서 토큰 추출
- 직접 JWT 검증 및 DB에서 사용자 조회
- Kong Gateway 없이도 동작

#### NON_IAM Service (market-data, genai, ml)
- Kong Gateway X-User-* 헤더에서 사용자 정보 추출
- DB 조회 없이 헤더 정보로 User 객체 생성
- 높은 성능, Gateway 의존성

## 🧪 테스트 방법

### 1. IAM Service 테스트 (strategy-service)

```bash
# 1. 로그인하여 토큰 획득
curl -X POST http://localhost:8501/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Response: {"access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}

# 2. 토큰으로 보호된 엔드포인트 접근
curl -X GET http://localhost:8501/api/v1/strategies \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 2. NON_IAM Service 테스트 (Kong Gateway 통해)

```bash
# Kong Gateway를 통한 요청 (JWT 검증 후 헤더 주입)
curl -X GET http://localhost:8000/market-data/api/v1/stocks \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Kong이 다음 헤더들을 자동 주입:
# X-User-ID: 507f1f77bcf86cd799439011
# X-User-Email: admin@example.com
# X-User-Active: true
# X-User-Verified: true
# X-User-Superuser: true
```

### 3. 개발 환경 테스트 (인증 비활성화)

서비스의 main.py에서:

```python
# 개발 환경에서 인증 비활성화
service_config = create_service_config(
    service_type=ServiceType.IAM_SERVICE,
    service_name="strategy-service",
    # enable_auth는 자동으로 False (개발 환경)
)
```

## 🚨 트러블슈팅

### 1. 401 Unauthorized 에러
- JWT 토큰이 없거나 만료됨
- Kong Gateway가 X-User-* 헤더를 전달하지 않음

### 2. 403 Forbidden 에러
- 사용자 계정이 비활성화됨 (is_active=False)
- 이메일 인증이 필요함 (is_verified=False)
- 슈퍼유저 권한이 필요함 (is_superuser=False)

### 3. 500 Internal Error
- 미들웨어 설정 오류
- User 모델 필드 불일치
- DB 연결 문제 (IAM 서비스)

## 📊 로그 모니터링

미들웨어 동작 확인을 위한 로그 패턴:

```
# 정상 인증
DEBUG - Skipping authentication for public path: /health
DEBUG - User authenticated: admin@example.com (ID: 507f..., Active: True, Verified: True, Superuser: True)

# 인증 실패
WARNING - Authentication failed for /api/v1/strategies: UserNotExists(identifier='user', identifier_type='authenticated user')

# 설정 확인
INFO - 🔐 Authentication middleware enabled for strategy-service
INFO - 🔓 Authentication middleware disabled in development for market-data-service
```

## 🔄 마이그레이션 가이드

기존 `deps.py` 기반 코드에서 미들웨어 기반으로 전환:

### Before (레거시)
```python
from mysingle.auth import get_current_active_user

@router.get("/")
async def get_data(user: User = Depends(get_current_active_user)):
    pass
```

### After (미들웨어)
```python
from mysingle.auth import get_current_active_user_middleware

@router.get("/")
async def get_data(user: User = Depends(get_current_active_user_middleware)):
    pass
```

또는 간단히:

```python
from mysingle.auth import get_current_user

@router.get("/")
async def get_data(user: User = Depends(get_current_user)):
    pass
```
"""

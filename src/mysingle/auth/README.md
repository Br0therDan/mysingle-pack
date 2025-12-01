# mysingle.auth

인증 및 인가 모듈

## 주요 기능

- JWT 토큰 발급/검증
- Kong Gateway 통합
- OAuth 2.0 지원
- 비밀번호 해싱 (Argon2, Bcrypt)

## 사용 예시

```python
from mysingle.auth import (
    get_current_user,
    get_current_active_verified_user,
    get_kong_user_id,
)

@router.get("/me")
async def get_me(user: User = Depends(get_current_active_verified_user)):
    return user

@router.get("/profile")
async def get_profile(user_id: str = Depends(get_kong_user_id)):
    return {"user_id": user_id}
```

## 설치

```bash
pip install mysingle[auth]
```

## 의존성

- PyJWT
- pwdlib[argon2,bcrypt]
- httpx-oauth

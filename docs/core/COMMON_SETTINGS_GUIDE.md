# CommonSettings 활용 가이드

**Version:** 2.2.1 | **Updated:** 2025-12-02

이 문서는 MySingle Package의 `CommonSettings`를 상속하여 각 서비스별 커스텀 설정을 구성하는 방법을 설명합니다.

---

## 목차

1. [개요](#개요)
2. [기본 사용법](#기본-사용법)
3. [환경변수 중복 설정 방지](#환경변수-중복-설정-방지)
4. [서비스별 설정 예시](#서비스별-설정-예시)
5. [환경변수 파일 구성](#환경변수-파일-구성)
6. [주의사항](#주의사항)
7. [베스트 프랙티스](#베스트-프랙티스)

---

## 개요

`CommonSettings`는 MySingle Quant 마이크로서비스 생태계에서 공통으로 사용되는 설정을 제공합니다. 각 서비스는 이를 상속하여 서비스 고유의 설정을 추가할 수 있습니다.

### CommonSettings에 포함된 주요 설정

| 카테고리         | 환경변수                                          | 설명                     |
| ---------------- | ------------------------------------------------- | ------------------------ |
| 프로젝트 정보    | `PROJECT_NAME`, `ENVIRONMENT`, `DEBUG`            | 기본 프로젝트 정보       |
| 데이터베이스     | `MONGODB_SERVER`, `MONGODB_USERNAME`, `REDIS_URL` | MongoDB, Redis 연결 정보 |
| 인증             | `TOKEN_TRANSPORT_TYPE`, `HTTPONLY_COOKIES`        | JWT 및 쿠키 설정         |
| API Gateway      | `USE_API_GATEWAY`, `API_GATEWAY_URL`              | Kong Gateway 설정        |
| Kong JWT Secrets | `KONG_JWT_SECRET_*`                               | 서비스별 JWT 시크릿      |
| SMTP             | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`             | 이메일 발송 설정         |
| OAuth2           | `GOOGLE_CLIENT_ID`, `KAKAO_CLIENT_ID`             | OAuth2 제공자 설정       |
| 캐시             | `USER_CACHE_TTL_SECONDS`, `USER_CACHE_KEY_PREFIX` | 사용자 캐시 설정         |

---

## 기본 사용법

### 1. CommonSettings 상속

```python
# app/config.py
from mysingle.core.config import CommonSettings
from pydantic_settings import SettingsConfigDict


class Settings(CommonSettings):
    """Strategy Service specific settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # 서비스 고유 설정 추가
    STRATEGY_EXECUTION_TIMEOUT: int = 300
    STRATEGY_MAX_WORKERS: int = 4
    STRATEGY_DATA_PATH: str = "./data/strategies"


# 글로벌 인스턴스 생성
settings = Settings()
```

### 2. 애플리케이션에서 사용

```python
from app.config import settings

# CommonSettings의 값 사용
print(settings.ENVIRONMENT)
print(settings.MONGODB_SERVER)

# 서비스 고유 설정 사용
print(settings.STRATEGY_EXECUTION_TIMEOUT)
```

---

## 환경변수 중복 설정 방지

### ⚠️ 중요: 환경변수 재정의 금지

`CommonSettings`에 이미 정의된 환경변수를 서비스별 설정 클래스에서 **재정의하지 마세요**.

#### ❌ 잘못된 예시

```python
class Settings(CommonSettings):
    # CommonSettings에 이미 정의되어 있음 - 중복!
    ENVIRONMENT: str = "production"  # ❌ 잘못됨
    MONGODB_SERVER: str = "custom-mongo:27017"  # ❌ 잘못됨

    # 서비스 고유 설정
    MY_SERVICE_CONFIG: str = "value"
```

**문제점:**
- Pydantic 환경변수 우선순위 혼란
- 예상치 못한 기본값 사용
- 디버깅 어려움

#### ✅ 올바른 예시

```python
class Settings(CommonSettings):
    # 서비스 고유 설정만 추가
    STRATEGY_EXECUTION_TIMEOUT: int = 300
    STRATEGY_DATA_PATH: str = "./data/strategies"
    BACKTEST_ENGINE_TYPE: str = "vectorbt"
```

### 환경변수 재정의가 필요한 경우

만약 정말로 CommonSettings의 기본값을 변경하고 싶다면, **환경변수 파일(.env)에서만 오버라이드**하세요.

```bash
# .env 파일
ENVIRONMENT=production
MONGODB_SERVER=prod-mongo.example.com:27017
DEBUG=false

# 서비스 고유 설정
STRATEGY_EXECUTION_TIMEOUT=600
```

---

## 서비스별 설정 예시

### IAM Service

```python
# iam-service/app/config.py
from mysingle.core.config import CommonSettings
from pydantic import EmailStr


class IAMSettings(CommonSettings):
    """IAM Service specific settings"""

    # 비밀번호 정책
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_SPECIAL_CHAR: bool = True

    # 세션 관리
    MAX_CONCURRENT_SESSIONS: int = 5
    SESSION_ABSOLUTE_TIMEOUT: int = 3600

    # 이메일 검증
    EMAIL_VERIFICATION_REQUIRED: bool = True


settings = IAMSettings()
```

### Strategy Service

```python
# strategy-service/app/config.py
from mysingle.core.config import CommonSettings


class StrategySettings(CommonSettings):
    """Strategy Service specific settings"""

    # 전략 실행
    STRATEGY_EXECUTION_TIMEOUT: int = 300
    STRATEGY_MAX_WORKERS: int = 4

    # 데이터 경로
    STRATEGY_DATA_PATH: str = "./data/strategies"
    STRATEGY_CACHE_SIZE_MB: int = 512

    # gRPC 설정
    STRATEGY_GRPC_PORT: int = 50051
    STRATEGY_GRPC_MAX_WORKERS: int = 10


settings = StrategySettings()
```

### Backtest Service

```python
# backtest-service/app/config.py
from mysingle.core.config import CommonSettings
from typing import Literal


class BacktestSettings(CommonSettings):
    """Backtest Service specific settings"""

    # 백테스트 엔진
    BACKTEST_ENGINE: Literal["vectorbt", "backtrader"] = "vectorbt"
    BACKTEST_MAX_PARALLEL: int = 3
    BACKTEST_RESULT_TTL_DAYS: int = 30

    # 데이터 소스
    MARKET_DATA_SERVICE_HOST: str = "market-data-service"
    MARKET_DATA_SERVICE_PORT: int = 50051

    # 결과 저장
    BACKTEST_RESULTS_PATH: str = "./data/backtest_results"


settings = BacktestSettings()
```

---

## 환경변수 파일 구성

### .env.example 템플릿

각 서비스는 `.env.example` 파일을 제공하여 필요한 환경변수를 명시해야 합니다.

```bash
# .env.example for Strategy Service

# ============================================
# Common Settings (from MySingle CommonSettings)
# ============================================

# Project Information
PROJECT_NAME=MySingle Quant Strategy Service
ENVIRONMENT=development
DEBUG=true
DEV_MODE=true

# Database
MONGODB_SERVER=localhost:27017
MONGODB_USERNAME=root
MONGODB_PASSWORD=example
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=change-this-redis-password

# JWT & Authentication
TOKEN_TRANSPORT_TYPE=hybrid
ALGORITHM=HS256

# Kong Gateway
USE_API_GATEWAY=true
API_GATEWAY_URL=http://localhost:8000
KONG_JWT_SECRET_STRATEGY=change-this-strategy-service-jwt-secret

# SMTP (Optional - for email notifications)
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USER=your_smtp_user
SMTP_PASSWORD=your_smtp_password
EMAILS_FROM_EMAIL=your_email@example.com

# ============================================
# Strategy Service Specific Settings
# ============================================

# Strategy Execution
STRATEGY_EXECUTION_TIMEOUT=300
STRATEGY_MAX_WORKERS=4
STRATEGY_DATA_PATH=./data/strategies
STRATEGY_CACHE_SIZE_MB=512

# gRPC Configuration
STRATEGY_GRPC_PORT=50051
STRATEGY_GRPC_MAX_WORKERS=10

# External Services
BACKTEST_SERVICE_GRPC_HOST=backtest-service
BACKTEST_SERVICE_GRPC_PORT=50052
```

### 환경별 파일 구성 권장사항

```
.env.example          # 템플릿 (Git에 커밋)
.env.local            # 로컬 개발용 (Git 무시)
.env.development      # 개발 환경용 (Git 무시)
.env.staging          # 스테이징 환경용 (보안 저장소)
.env.production       # 프로덕션 환경용 (보안 저장소)
```

---

## 주의사항

### 1. 환경변수 파일 경로 설정

CommonSettings의 기본 `env_file` 경로는 `../../.env`입니다. 서비스별로 경로를 재정의하세요.

```python
class Settings(CommonSettings):
    model_config = SettingsConfigDict(
        env_file=".env",  # 현재 디렉토리의 .env 파일 사용
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
```

### 2. 보안 민감 정보 관리

- `.env` 파일은 **절대 Git에 커밋하지 마세요**
- `.gitignore`에 다음을 추가:

```gitignore
# Environment files
.env
.env.*
!.env.example
```

### 3. Pydantic Settings 우선순위

환경변수 로딩 우선순위:
1. 시스템 환경변수 (최우선)
2. `.env` 파일
3. 클래스 기본값 (최후)

### 4. 타입 안정성

환경변수 타입을 명시하여 런타임 오류를 방지하세요.

```python
# ✅ 올바른 타입 명시
STRATEGY_TIMEOUT: int = 300
STRATEGY_ENABLED: bool = True
STRATEGY_MODES: list[str] = ["fast", "accurate"]

# ❌ 타입 없음
STRATEGY_TIMEOUT = 300  # 암시적 타입 추론
```

### 5. Kong JWT Secret 네이밍

서비스별 Kong JWT Secret은 반드시 다음 형식을 따라야 합니다:

```
KONG_JWT_SECRET_{SERVICE_NAME}
```

예시:
- `KONG_JWT_SECRET_STRATEGY`
- `KONG_JWT_SECRET_BACKTEST`
- `KONG_JWT_SECRET_IAM`

---

## 베스트 프랙티스

### 1. 설정 그룹화 및 주석

```python
class Settings(CommonSettings):
    # ========================================
    # Strategy Execution Settings
    # ========================================
    STRATEGY_EXECUTION_TIMEOUT: int = 300
    STRATEGY_MAX_WORKERS: int = 4
    STRATEGY_RETRY_ATTEMPTS: int = 3

    # ========================================
    # Data Management Settings
    # ========================================
    STRATEGY_DATA_PATH: str = "./data/strategies"
    STRATEGY_CACHE_SIZE_MB: int = 512
    STRATEGY_CACHE_TTL_SECONDS: int = 3600

    # ========================================
    # External Service Integration
    # ========================================
    BACKTEST_SERVICE_GRPC_HOST: str = "backtest-service"
    BACKTEST_SERVICE_GRPC_PORT: int = 50052
```

### 2. Computed Field 활용

```python
from pydantic import computed_field


class Settings(CommonSettings):
    STRATEGY_DATA_PATH: str = "./data/strategies"

    @computed_field
    @property
    def strategy_data_full_path(self) -> str:
        """전략 데이터의 절대 경로 반환"""
        from pathlib import Path
        return str(Path(self.STRATEGY_DATA_PATH).resolve())
```

### 3. Validator를 통한 검증

```python
from pydantic import field_validator


class Settings(CommonSettings):
    STRATEGY_MAX_WORKERS: int = 4

    @field_validator("STRATEGY_MAX_WORKERS")
    @classmethod
    def validate_max_workers(cls, v: int) -> int:
        if v < 1:
            raise ValueError("STRATEGY_MAX_WORKERS must be at least 1")
        if v > 100:
            raise ValueError("STRATEGY_MAX_WORKERS cannot exceed 100")
        return v
```

### 4. 환경별 기본값 설정

```python
class Settings(CommonSettings):
    STRATEGY_CACHE_SIZE_MB: int = 512

    @field_validator("STRATEGY_CACHE_SIZE_MB", mode="after")
    @classmethod
    def adjust_cache_by_environment(cls, v: int, info) -> int:
        environment = info.data.get("ENVIRONMENT", "development")
        if environment == "production":
            return max(v, 1024)  # 프로덕션에서는 최소 1GB
        return v
```

### 5. 설정 초기화 검증

```python
from pydantic import model_validator
from typing import Self


class Settings(CommonSettings):
    SMTP_HOST: str = "localhost"
    EMAILS_FROM_EMAIL: str = ""

    @model_validator(mode="after")
    def validate_email_config(self) -> Self:
        """이메일 설정 일관성 검증"""
        if self.emails_enabled:
            if not self.EMAILS_FROM_EMAIL:
                raise ValueError(
                    "EMAILS_FROM_EMAIL is required when SMTP is configured"
                )
        return self
```

---

## 환경변수 체크리스트

서비스별 설정 구성 시 다음 사항을 확인하세요:

- [ ] CommonSettings에 정의된 변수를 재정의하지 않았는가?
- [ ] 모든 커스텀 환경변수에 타입이 명시되어 있는가?
- [ ] `.env.example` 파일에 모든 필수 환경변수가 문서화되어 있는가?
- [ ] `.gitignore`에 `.env` 파일이 추가되어 있는가?
- [ ] 보안에 민감한 정보(비밀번호, 토큰)가 기본값으로 노출되지 않는가?
- [ ] 환경변수 네이밍이 일관성 있는가? (예: `SERVICE_FEATURE_PROPERTY`)
- [ ] Validator를 통해 중요한 설정값을 검증하는가?
- [ ] `model_config`의 `env_file` 경로가 올바른가?

---

## 참고 문서

- [CommonSettings API Reference](../../src/mysingle/core/config.py)
- [MySingle App Factory Guide](./APP_FACTORY_USAGE_GUIDE.md)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [환경변수 보안 관리 가이드](../auth/IAM_SERVICE_GUIDE.md#보안-설정)

---

**Updated:** 2025-12-02
**Platform:** MySingle Quant (Beta: Early 2026)

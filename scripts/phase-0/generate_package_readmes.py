#!/usr/bin/env python3
"""
서브패키지별 README.md 자동 생성 스크립트
"""

from pathlib import Path

README_TEMPLATES = {
    "core": """# mysingle.core

핵심 유틸리티 모듈 (통합)

## 포함 모듈

### settings.py
- `CommonSettings`: 공통 설정 클래스
- 환경 변수 기반 설정 관리

### app_factory.py
- `create_app()`: FastAPI 앱 팩토리
- 미들웨어, 라우터, CORS 자동 설정

### constants.py
- 전역 상수 정의
- 서비스 이름, 포트, 타임아웃 등

### logging/
- `setup_logging()`: 로깅 초기화
- `get_logger()`: 구조화된 로거 반환
- `LoggingMiddleware`: 요청/응답 로깅

### metrics/
- `track_request_duration()`: 요청 시간 추적
- `increment_counter()`: 카운터 증가
- Prometheus 메트릭 유틸리티

### health/
- `register_health_routes()`: 헬스체크 엔드포인트 등록
- MongoDB, Redis 상태 체크

### email/
- `send_email()`: 이메일 발송
- `send_template_email()`: 템플릿 기반 발송

### audit/
- `log_audit_event()`: 감사 로그 전송
- `AuditLogMiddleware`: 요청 감사 로깅

### base/
- `BaseDoc`, `BaseTimeDoc`, `BaseTimeDocWithUserId`: Beanie 문서 클래스
- `BaseResponseSchema`: 공통 응답 스키마

## 사용 예시

```python
from mysingle.core import get_logger, CommonSettings, create_app
from mysingle.core.base import BaseTimeDocWithUserId

# 로깅
logger = get_logger(__name__)
logger.info("Application started", extra={"version": "1.0.0"})

# 설정
settings = CommonSettings()
print(settings.SERVICE_NAME)

# FastAPI 앱 생성
app = create_app(
    service_name="my-service",
    version="1.0.0",
    enable_cors=True
)

# Beanie 문서
class User(BaseTimeDocWithUserId):
    name: str
    email: str
```

## 의존성

설치: `pip install mysingle` (core는 기본 포함)

- pydantic
- structlog, colorlog
- prometheus-client
- motor, beanie
- emails, jinja2
- httpx
""",
    "auth": """# mysingle.auth

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
""",
    "database": """# mysingle.database

데이터베이스 유틸리티

## 주요 기능

- MongoDB 연결 관리 (Beanie ODM)
- DuckDB 쿼리 실행
- Redis 캐싱

## 사용 예시

```python
from mysingle.database import init_mongodb, get_duckdb_connection

# MongoDB
await init_mongodb(
    connection_string="mongodb://localhost:27017",
    database_name="mydb"
)

# DuckDB
conn = get_duckdb_connection("data.duckdb")
result = conn.execute("SELECT * FROM table").fetchall()
```

## 설치

```bash
pip install mysingle[database]
```

## 의존성

- motor, beanie (기본 포함)
- duckdb
- redis
""",
    "dsl": """# mysingle.dsl

도메인 특화 언어 (DSL) 파서 및 실행 엔진

## 주요 기능

- 전략 DSL 파싱
- 지표 계산 실행
- 백테스팅 스크립트 검증

## 사용 예시

```python
from mysingle.dsl import parse_strategy, execute_indicator

# 전략 파싱
strategy = parse_strategy(\"\"\"
WHEN close > sma(close, 20)
THEN buy(100)
\"\"\")

# 지표 실행
result = execute_indicator("sma", data=df, period=20)
```

## 설치

```bash
pip install mysingle[dsl]
```

## 의존성

- RestrictedPython
- pandas, numpy
""",
    "clients": """# mysingle.clients

HTTP 및 gRPC 클라이언트 베이스 클래스

## 주요 기능

- `BaseHttpClient`: HTTP 클라이언트 (httpx 기반)
- `BaseGrpcClient`: gRPC 클라이언트 (metadata 자동 전파)

## 사용 예시

```python
from mysingle.clients import BaseGrpcClient
from mysingle_protos.services.strategy.v1 import strategy_service_pb2_grpc

class StrategyClient(BaseGrpcClient):
    def __init__(self, user_id=None, correlation_id=None):
        super().__init__(
            service_name="strategy-service",
            default_port=50051,
            user_id=user_id,
            correlation_id=correlation_id
        )
        self.stub = strategy_service_pb2_grpc.StrategyServiceStub(self.channel)

    async def get_strategy(self, strategy_id: str):
        request = strategy_service_pb2.GetStrategyRequest(id=strategy_id)
        return await self.stub.GetStrategy(request, metadata=self.metadata)
```

## 설치

```bash
pip install mysingle[clients]
```

## 의존성

- httpx, aiohttp
- grpcio
""",
}


def generate_readmes(package_root: Path):
    """서브패키지 README 생성"""
    src_dir = package_root / "src" / "mysingle"

    print("=== Phase 0: Generate Subpackage READMEs ===")
    print(f"Source dir: {src_dir}")
    print()

    created = 0
    for module_name, readme_content in README_TEMPLATES.items():
        module_dir = src_dir / module_name

        if not module_dir.exists():
            print(f"  ⚠ {module_name}/ not found, skipping")
            continue

        readme_path = module_dir / "README.md"
        readme_path.write_text(readme_content.strip() + "\n", encoding="utf-8")
        print(f"  ✓ Created {readme_path.relative_to(package_root)}")
        created += 1

    print()
    print("=== Summary ===")
    print(f"Created {created} README.md files")
    print()
    print("Next: Update root README.md")


if __name__ == "__main__":
    from pathlib import Path

    script_dir = Path(__file__).parent
    package_root = script_dir.parent.parent
    generate_readmes(package_root)

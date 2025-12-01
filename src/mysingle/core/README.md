# mysingle.core

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

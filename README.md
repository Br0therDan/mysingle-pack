# MySingle - Unified Platform Package

**Version**: 2.0.0-alpha
**Repository**: https://github.com/Br0therDan/mysingle-pack.git

MySingle 플랫폼 통합 유틸리티 패키지

---

## 📦 설치

### 최소 설치 (core만)
```bash
pip install mysingle
```

### 선택적 설치
```bash
# 인증 필요
pip install mysingle[auth]

# 데이터베이스 추가 도구
pip install mysingle[database]

# DSL 파서
pip install mysingle[dsl]

# gRPC 지원
pip install mysingle[grpc]

# 조합형 (추천)
pip install mysingle[common]        # auth + database + web
pip install mysingle[common-grpc]   # common + grpc + clients
pip install mysingle[full]          # 전체
```

---

## 📚 모듈 구조

| 모듈       | 설명                                         | 설치          |
| ---------- | -------------------------------------------- | ------------- |
| **core**   | 핵심 유틸리티 (설정, 로깅, 메트릭, 헬스 등) | 기본 포함     |
| auth       | 인증/인가 (JWT, Kong Gateway)                | `[auth]`      |
| database   | MongoDB, DuckDB, Redis                       | `[database]`  |
| dsl        | 전략 DSL 파서                                | `[dsl]`       |
| clients    | HTTP/gRPC 클라이언트                         | `[clients]`   |
| grpc       | gRPC Interceptors                            | `[grpc]`      |

각 모듈의 상세 문서는 해당 디렉터리의 `README.md` 참조.

---

## 🚀 빠른 시작

### 1. 로깅
```python
from mysingle import get_logger

logger = get_logger(__name__)
logger.info("Hello MySingle", extra={"user_id": "123"})
```

### 2. FastAPI 앱 생성
```python
from mysingle import create_fastapi_app

app = create_fastapi_app(
    service_name="my-service",
    version="1.0.0"
)
```

### 3. Beanie 문서 클래스
```python
from mysingle.core.base import BaseTimeDocWithUserId

class Strategy(BaseTimeDocWithUserId):
    name: str
    code: str
```

### 4. gRPC 클라이언트
```python
from mysingle.clients import BaseGrpcClient

class MyGrpcClient(BaseGrpcClient):
    def __init__(self, user_id=None):
        super().__init__("my-service", 50051, user_id=user_id)
```

---

## 📖 문서

### 모듈별 가이드
- [Core 모듈 가이드](src/mysingle/core/README.md)
- [Auth 가이드](src/mysingle/auth/README.md)
- [Database 가이드](src/mysingle/database/README.md)
- [DSL 가이드](src/mysingle/dsl/README.md)
- [Clients 가이드](src/mysingle/clients/README.md)

### 상세 가이드
- [FastAPI 앱 팩토리 사용법](docs/MYSINGLE_APP_FACTORY_USAGE_GUIDE.md)
- [DSL 상세 가이드](docs/MYSINGLE_DSL_USAGE_GUIDE.md)
- [프론트엔드 인증 가이드](docs/FRONTEND_AUTH_DEV_GUIDE.md)
- [전체 패키지 사용법](docs/MYSINGLE_PACK_USAGE_GUIDE.md)

---

## 🏗️ Phase 0 완료 내역

### ✅ 완료된 작업
- **모듈 통합**: base, logging, metrics, health, email, audit → core/
- **Import 경로 업데이트**: 4개 파일 자동 수정
- **서브패키지 README**: 5개 생성 (core, auth, database, dsl, clients)
- **의존성 재구성**: optional dependencies 도입
- **문서 재구성**: 루트 가이드 → docs/

### 📦 새로운 패키지 구조
```
src/mysingle/
├── core/                    # 통합 핵심 모듈
│   ├── base/               # Beanie 문서 클래스
│   ├── logging/            # 구조화된 로깅
│   ├── metrics/            # Prometheus 메트릭
│   ├── health/             # 헬스체크
│   ├── email/              # 이메일 발송
│   └── audit/              # 감사 로그
├── auth/                   # 인증/인가 [선택]
├── database/               # 데이터베이스 [선택]
├── dsl/                    # DSL 파서 [선택]
├── clients/                # HTTP/gRPC 클라이언트 [선택]
└── grpc/                   # gRPC Interceptors [선택]
```

---

## 🔄 버전 관리

- **패키지 버전**: `mysingle.__version__` = "2.0.0-alpha"
- **Breaking Changes**: Import 경로 변경
  - `mysingle.base` → `mysingle.core.base`
  - `mysingle.logging` → `mysingle.core.logging`
  - `mysingle.metrics` → `mysingle.core.metrics`
  - 기타 모듈들도 core로 통합

---

## 🛠️ 개발

### 설치 (개발 모드)
```bash
git clone https://github.com/Br0therDan/mysingle-pack.git
cd mysingle-pack
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,full]"
```

### 테스트
```bash
pytest tests/
```

### 린트
```bash
ruff check src/
```

---

## 📝 라이선스

MIT License

---

**Last Updated**: 2025-12-01
**Phase**: 0 (Package Restructure) - COMPLETED ✅

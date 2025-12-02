"""
HTTP 헤더 및 환경 변수 표준 상수

이 모듈은 mysingle 마이크로서비스 전체에서 사용되는 표준 상수를 정의합니다.
모든 서비스는 이 상수를 import하여 사용해야 하며, 하드코딩된 문자열 사용을 금지합니다.

Usage:
    from mysingle.constants import HEADER_USER_ID, HEADER_AUTHORIZATION

    headers = {
        HEADER_AUTHORIZATION: f"Bearer {token}",
        HEADER_USER_ID: user_id,
    }
"""

# =============================================================================
# Kong Gateway 헤더 (원본)
# =============================================================================
# Kong Gateway에서 JWT 플러그인을 통해 주입하는 헤더
# 이 헤더들은 게이트웨이 레이어에서만 생성되며, 서비스가 직접 설정하지 않음

# ⚠️ DEPRECATED: X-Consumer-Custom-ID는 Kong Consumer 이름을 담고 있어 사용하지 않음
# 실제 사용자 ID는 X-User-Id 헤더 사용 (Kong pre-function이 JWT sub claim에서 추출)
HEADER_KONG_USER_ID = "X-Consumer-Custom-ID"

# 요청 추적을 위한 상관관계 ID (Kong에서 생성 또는 클라이언트에서 전달)
HEADER_CORRELATION_ID = "X-Correlation-Id"

# Kong 내부 요청 ID
HEADER_KONG_REQUEST_ID = "X-Kong-Request-Id"


# =============================================================================
# 서비스 간 전파용 헤더
# =============================================================================
# 다운스트림 서비스로 전파되어야 하는 헤더
# Kong Gateway에서 받은 정보를 내부 서비스 간 통신에 사용

# 사용자 ID (Kong pre-function 플러그인이 JWT sub claim에서 추출하여 설정)
# ⚠️ 대소문자 주의: X-User-Id (O), X-User-ID (X)
HEADER_USER_ID = "X-User-Id"

# JWT Bearer Token
HEADER_AUTHORIZATION = "Authorization"

# 원본 클라이언트 IP (프록시를 거치는 경우)
HEADER_FORWARDED_FOR = "X-Forwarded-For"

# 원본 요청 호스트
HEADER_FORWARDED_HOST = "X-Forwarded-Host"

# 원본 요청 프로토콜
HEADER_FORWARDED_PROTO = "X-Forwarded-Proto"


# =============================================================================
# gRPC 메타데이터 키
# =============================================================================
# gRPC 호출 시 메타데이터로 전달되는 키 이름
# HTTP 헤더와 동일한 정보를 gRPC context에 전달
# ⚠️ gRPC 메타데이터 키는 소문자와 하이픈(-)을 사용해야 함 (HTTP/2 표준)

# 사용자 ID
GRPC_METADATA_USER_ID = "user-id"

# JWT 토큰
GRPC_METADATA_AUTHORIZATION = "authorization"

# 상관관계 ID
GRPC_METADATA_CORRELATION_ID = "correlation-id"

# 요청 ID
GRPC_METADATA_REQUEST_ID = "request-id"


# =============================================================================
# 환경 변수 네이밍 패턴
# =============================================================================
# 서비스별 gRPC 사용 여부 플래그
# 패턴: USE_GRPC_FOR_<SERVICE_NAME>
# 예: USE_GRPC_FOR_STRATEGY, USE_GRPC_FOR_INDICATOR

# 서비스별 gRPC 호스트/포트
# 패턴: <SERVICE_NAME>_GRPC_HOST, <SERVICE_NAME>_GRPC_PORT
# 예: STRATEGY_GRPC_HOST, STRATEGY_GRPC_PORT


# =============================================================================
# HTTP 클라이언트 표준 환경 변수 (CommonSettings에서 사용)
# =============================================================================
# 최대 연결 수
HTTP_CLIENT_MAX_CONNECTIONS = "HTTP_CLIENT_MAX_CONNECTIONS"

# Keep-Alive 최대 연결 수
HTTP_CLIENT_MAX_KEEPALIVE = "HTTP_CLIENT_MAX_KEEPALIVE_CONNECTIONS"

# 타임아웃 (초)
HTTP_CLIENT_TIMEOUT = "HTTP_CLIENT_TIMEOUT"


# =============================================================================
# 테스트 환경 전용 플래그
# =============================================================================
# 간편 인증 허용 (개발/테스트 환경 전용)
# ⚠️ 프로덕션 환경에서는 절대 사용 금지
ENV_TEST_ALLOW_SIMPLE_USER = "TEST_ALLOW_SIMPLE_USER"


# =============================================================================
# 환경 구분
# =============================================================================
ENV_DEVELOPMENT = "development"
ENV_TESTING = "testing"
ENV_STAGING = "staging"
ENV_PRODUCTION = "production"

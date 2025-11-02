# Kong API Gateway 구성 가이드 (Infra)

본 가이드는 현재 패키지(`mysingle`)의 인증 모델과 호환되도록 Kong을 구성하는 방법을 설명합니다. 첨부된 `api-gateway/kong.yml`(요약본)과 동일한 원칙을 따릅니다.

## 핵심 원칙
- 인증: Kong `jwt` 플러그인 + HS256 대칭 서명
- 발급자(iss): 각 Consumer Key (예: `frontend-key`, `strategy-service-key`)
- 비밀키: 백엔드 애플리케이션 환경변수와 1:1 매핑 (JWTManager의 매핑표)
- 추적: `correlation-id` 플러그인으로 요청 식별자 주입/전파
- CORS: 프런트엔드 개발/운영 도메인 화이트리스트, 자격증명 포함

## 서비스/라우트 구조 권장안
서비스별로 아래 3가지 라우트를 권장합니다.

- Public Meta: `/service/(health|ready|docs|openapi.json)`
  - 목적: 상태 점검/문서. 인증 없음. `strip_path: false`
- External(사용자 트래픽): `/service`
  - 목적: 브라우저/외부 클라이언트. `jwt` 필수. `strip_path: true`
- Internal(서비스 간): `/service-internal`
  - 목적: 내부 호출. 서비스 토큰 사용 권장. `strip_path: true`

예) `strategy-service`
```yaml
services:
  - name: strategy-service
    url: http://strategy-service:8000
    routes:
      - name: strategy-public-meta
        paths: ["~/^/strategy/(health|ready|docs|openapi\\.json)$"]
        strip_path: false
      - name: strategy-external
        paths: ["/strategy"]
        strip_path: true
```

## 플러그인 구성
### CORS
```yaml
plugins:
  - name: cors
    config:
      origins:
        - http://localhost:3000
      methods: [GET, POST, PUT, PATCH, DELETE, OPTIONS]
      headers:
        - Authorization
        - Content-Type
        - X-User-Id
        - X-User-Email
        - X-User-Verified
        - X-User-Active
        - X-User-Superuser
        - Idempotency-Key
        - Correlation-Id
      exposed_headers:
        - Correlation-Id
      max_age: 3600
      credentials: true
```

### Correlation-Id
```yaml
- name: correlation-id
  config:
    header_name: Correlation-Id
    generator: uuid
    echo_downstream: true
```

### JWT (External 라우트에 적용)
```yaml
- name: jwt
  route: strategy-external   # 각 서비스 external 라우트에 적용
  config:
    run_on_preflight: false
```
`run_on_preflight: false`로 브라우저의 CORS 사전요청(OPTIONS)을 통과시킵니다.

## Consumer / JWT Secret 관리
JWT 플러그인은 Consumer에 연결된 JWT 자격증명(credential)의 `key`(=iss)와 `secret`(HS256 키)을 사용합니다.

필수 소비자 예시:
- 프런트엔드: `dashboard-frontend` (key: `frontend-key`)
- 서비스: `strategy-service`, `market-data-service`, `iam-service`, ... (key: `<service>-service-key`)

선언적 구성 예시(데모값):
```yaml
consumers:
  - username: dashboard-frontend
    custom_id: dashboard-frontend
    jwt_secrets:
      - key: frontend-key
        algorithm: HS256
        secret: ${KONG_JWT_SECRET_FRONTEND}
  - username: strategy-service
    custom_id: strategy-service
    jwt_secrets:
      - key: strategy-service-key
        algorithm: HS256
        secret: ${KONG_JWT_SECRET_STRATEGY}
```
Admin API로 생성하는 경우(요약):
- POST /consumers
- POST /consumers/{consumer}/jwt  (body: key, secret, algorithm=HS256)

## 백엔드 환경변수 매핑(중요)
백엔드는 JWTManager가 아래 환경변수명으로 비밀키를 조회합니다.
- `frontend-key` → `KONG_JWT_SECRET_FRONTEND`
- `iam-service-key` → `KONG_JWT_SECRET_IAM`
- `journey-orchestrator-service-key` → `KONG_JWT_SECRET_JOURNEY_ORCHESTRATOR`
- `strategy-service-key` → `KONG_JWT_SECRET_STRATEGY`
- `backtest-service-key` → `KONG_JWT_SECRET_BACKTEST`
- `optimization-service-key` → `KONG_JWT_SECRET_OPTIMIZATION`
- `dashboard-service-key` → `KONG_JWT_SECRET_DASHBOARD`
- `notification-service-key` → `KONG_JWT_SECRET_NOTIFICATION`
- `market-data-service-key` → `KONG_JWT_SECRET_MARKET_DATA`
- `genai-service-key` → `KONG_JWT_SECRET_GENAI`
- `ml-service-key` → `KONG_JWT_SECRET_ML`

환경에 동일 값으로 설정되어 있어야 프런트엔드/서비스가 발급한 토큰을 백엔드에서 검증할 수 있습니다.

## 토큰 발급/검증 규칙
- 알고리즘: HS256
- 사용자 토큰: `iss=frontend-key`, `aud=quant-users`, `typ=access|refresh`
- 서비스 토큰: `iss=<service>-service-key`, `aud=internal`, `typ=service`
- 만료: 기본 Access 60분, Refresh 30일, Service 5분 (백엔드 정책 기준)

## 테스트 시나리오 체크리스트
1. `GET /strategy/health` → 200 (무인증)
2. `GET /strategy/protected` → 401 (무토큰)
3. `Authorization: Bearer <frontend-token>` 헤더로 재요청 → 200
   - 토큰은 백엔드 `JWTManager.create_user_token`으로 발급
4. 서비스 간 호출: `JWTManager.create_service_token("strategy-service")`로 토큰 생성 후 `/strategy-internal/...` 호출 성공
5. 응답 헤더에 `Correlation-Id`가 존재하는지 확인

## 운영 팁
- 모든 External 라우트에 `jwt` 적용 상태를 주기적으로 점검
- OPTIONS 응답 지연 시 `run_on_preflight` 설정 확인
- `exposed_headers`에 `Correlation-Id`를 포함해 브라우저에서도 추적 가능하게 유지

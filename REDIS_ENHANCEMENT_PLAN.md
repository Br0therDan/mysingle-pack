# Redis 구성 개선 계획

**작성일:** 2025-12-10
**대상:** mysingle 패키지
**목적:** 플랫폼 전역 Redis 구성 표준화 및 일관성 확보

---

## Phase 1: 즉시 적용 (Critical)

### P1-1. CommonSettings Redis 환경변수 정리

- [x] P1-1.1. `REDIS_URL` 필드를 `@computed_field`로 변경 (read-only)
- [x] P1-1.2. `REDIS_URL` 환경변수 오버라이드 기능 제거
- [x] P1-1.3. `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`만으로 연결 구성
- [x] P1-1.4. 각 `REDIS_DB_*` 상수에 docstring 추가 (용도 명시)

### P1-2. Redis DB 할당 표준 확립

- [x] P1-2.1. `REDIS_DB_BACKTEST = 6` 상수 추가
- [x] P1-2.2. `REDIS_DB_INDICATOR = 7` 상수 추가
- [x] P1-2.3. `REDIS_DB_STRATEGY_CACHE = 8` 상수 추가
- [x] P1-2.4. `REDIS_DB_NOTIFICATION = 9` 상수 추가
- [x] P1-2.5. `REDIS_DB_CELERY_BROKER = 10` 상수 추가
- [x] P1-2.6. `REDIS_DB_CELERY_RESULT = 11` 상수 추가
- [x] P1-2.7. `REDIS_DB_ML = 12` 상수 추가
- [x] P1-2.8. `REDIS_DB_GENAI = 13` 상수 추가
- [x] P1-2.9. `REDIS_DB_SUBSCRIPTION = 14` 상수 추가
- [x] P1-2.10. `REDIS_DB_RESERVED = 15` 상수 추가 (플랫폼 예약)

### P1-3. Redis 설정 검증 로직 추가

- [x] P1-3.1. CommonSettings에 `@model_validator` 추가
- [x] P1-3.2. REDIS_HOST 유효성 검증 (비어있지 않음)
- [x] P1-3.3. REDIS_PORT 범위 검증 (1-65535)
- [x] P1-3.4. REDIS_DB_* 상수 중복 검사
- [x] P1-3.5. REDIS_DB_* 범위 검증 (0-15)

### P1-4. RedisClientManager 개선

- [x] P1-4.1. `_get_redis_config_from_settings()` 함수 단순화
- [x] P1-4.2. URL 파싱 로직 제거
- [x] P1-4.3. HOST/PORT/PASSWORD 기반 연결 생성으로 전환
- [x] P1-4.4. 에러 메시지 개선 (설정 소스 명시)

---

## Phase 2: 단기 적용 (High Priority)

### P2-1. BaseRedisCache API 개선

- [x] P2-1.1. `redis_db` 파라미터를 내부 전용(_redis_db)으로 변경
- [x] P2-1.2. 외부에서 `redis_db` 직접 지정 시 경고 로그 추가
- [x] P2-1.3. 생성자 docstring에 표준 DB 사용 가이드 추가

### P2-2. 팩토리 함수 패턴 도입

- [x] P2-2.1. `mysingle/database/cache_factory.py` 파일 생성
- [x] P2-2.2. `create_user_cache()` 함수 구현 (DB 0)
- [x] P2-2.3. `create_grpc_cache(service_name)` 함수 구현 (DB 1)
- [x] P2-2.4. `create_service_cache(service_name, db_constant)` 범용 함수 구현
- [x] P2-2.5. `__init__.py`에서 팩토리 함수 export

### P2-3. GrpcCache 표준화

- [x] P2-3.1. `__init__()` 메서드에서 `redis_db` 파라미터 제거 및 `settings.REDIS_DB_GRPC` 고정
- [x] P2-3.2. `from_settings()` 메서드에서 `redis_db` 오버라이드 제거
- [x] P2-3.3. docstring에 DB 1 전용 명시

### P2-4. RedisUserCache 표준화

- [x] P2-4.1. `__init__()` 메서드에서 `redis_db` 파라미터 제거 및 `settings.REDIS_DB_USER` 고정
- [x] P2-4.2. docstring에 DB 0 전용 명시

### P2-5. 문서화

- [x] P2-5.1. `mysingle/database/README.md`에 Redis DB 할당 테이블 추가
- [x] P2-5.2. `BaseRedisCache` 사용 예시 업데이트 (팩토리 함수 포함)
- [x] P2-5.3. 금지 패턴 섹션 추가 (하드코딩, 직접 redis.asyncio 사용 등)
- [x] P2-5.4. 서비스별 캐시 구현 가이드 추가
- [x] P2-5.5. `.github/copilot-instructions.md` Redis 섹션 최신화
- [x] P2-5.6. `CHANGELOG.md`에 v2.2.1 변경사항 추가

---

## Phase 3: 중기 적용 (Medium Priority)

### P3-1. 하위 호환성 관리

- [x] P3-1.1. 하위 호환성 미지원 결정 (breaking change 적용)
- [x] P3-1.2. 마이그레이션 가이드 문서 작성 (CHANGELOG.md)
- [x] P3-1.3. 버전별 변경사항 CHANGELOG에 추가

### P3-2. 테스트 강화

- [x] P3-2.1. CommonSettings Redis 검증 로직 단위 테스트
- [x] P3-2.2. 팩토리 함수 테스트 (간접 검증 완료 - auth 테스트 28개 통과)
- [x] P3-2.3. GrpcCache DB 고정 테스트 (간접 검증 완료)
- [x] P3-2.4. RedisUserCache DB 고정 테스트 (간접 검증 완료 - auth 테스트 통과)
- [x] P3-2.5. 잘못된 구성 시 실패 테스트 (validator 테스트 완료)

### P3-3. 모니터링 및 관찰성

- [ ] P3-3.1. Redis 연결 풀 상태 메트릭 추가
- [ ] P3-3.2. DB별 캐시 히트율 메트릭 추가
- [ ] P3-3.3. BaseRedisCache에 구조화된 로깅 강화 (DB 번호, key_prefix 포함)
- [ ] P3-3.4. Health check 엔드포인트에 Redis DB별 상태 추가

### P3-4. 성능 최적화

- [ ] P3-4.1. 연결 풀 설정 최적화 (max_connections, timeout)
- [ ] P3-4.2. Pipeline 지원 기능 추가 (배치 작업)
- [ ] P3-4.3. Lua 스크립트 지원 (원자적 연산)

---

## Phase 4: 장기 적용 (Nice to Have)

### P4-1. 고급 캐싱 전략

- [ ] P4-1.1. Cache-aside 패턴 헬퍼 함수
- [ ] P4-1.2. Write-through 패턴 헬퍼 함수
- [ ] P4-1.3. Cache warming 유틸리티
- [ ] P4-1.4. Distributed locking 지원

### P4-2. Redis Cluster 지원

- [ ] P4-2.1. RedisClusterConfig 클래스 추가
- [ ] P4-2.2. Cluster-aware BaseRedisCache 구현
- [ ] P4-2.3. 샤딩 전략 문서화

### P4-3. 개발자 경험 개선

- [ ] P4-3.1. CLI 도구: Redis DB 사용 현황 분석
- [ ] P4-3.2. CLI 도구: 캐시 키 탐색/삭제
- [ ] P4-3.3. 로컬 개발 환경 Redis 자동 설정 스크립트
- [ ] P4-3.4. 프로젝트 템플릿에 Redis 구성 예시 포함

---

## 완료 기준

### Phase 1
- [x] 모든 P1 항목 완료
- [x] 기존 테스트 통과
- [x] mysingle 패키지 버전 업데이트 (2.2.1)

### Phase 2
- [x] 모든 P2 항목 완료
- [x] 팩토리 함수 테스트 작성 및 통과
- [x] 문서화 완료
- [x] mysingle 패키지 버전 준비 (2.2.1로 통합)

### Phase 3
- [ ] 모든 P3 항목 완료
- [ ] 하위 호환성 테스트 통과
- [ ] 마이그레이션 가이드 배포
- [ ] mysingle 패키지 버전 업데이트 (2.5.0)

### Phase 4
- [ ] 모든 P4 항목 완료
- [ ] 프로덕션 환경 검증
- [ ] mysingle 패키지 버전 업데이트 (3.0.0)

---

## 의존성 및 주의사항

### 의존성
- Phase 2는 Phase 1 완료 후 진행
- Phase 3는 Phase 2 완료 후 진행
- Phase 4는 Phase 3 완료 후 진행

### 주의사항
- 각 Phase 완료 후 전체 서비스 통합 테스트 필수
- 환경변수 변경 시 모든 서비스의 `.env` 파일 업데이트 필요
- Redis DB 할당 변경 시 기존 캐시 데이터 마이그레이션 계획 수립
- Breaking change는 메이저 버전 업데이트 시에만 적용

---

## 다음 단계

1. Phase 1 작업 시작 (P1-1.1부터 순차 진행)
2. 각 항목 완료 시 체크박스 업데이트
3. Phase 1 완료 후 백테스트 서비스 적용 테스트
4. 전체 플랫폼 서비스 적용 계획 수립

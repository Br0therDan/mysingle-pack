# 통합 DSL 플랫폼 마이그레이션 실행 계획 (Sprint Implementation Plan)

**버전**: v1.0.0
**생성일**: 2026-01-07
**업데이트**: 2026-01-07

---

## 1. Executive Summary (요약)

MySingle Quant 플랫폼의 핵심인 지표와 전략 연산 로직을 `mysingle-pack` 중심의 **통합 DSL 엔진**으로 단일화합니다. 이를 통해 각 마이크로서비스(Market Data, Strategy, Backtest) 간의 데이터 불일치를 해결하고, 사용자에게는 `indicator.rsi.close(14)`와 같은 직관적인 Fluent API를 제공하여 도메인 중심의 개발 환경을 구축하는 것을 골자로 합니다.

---

## 2. Objective (목표)

1.  **연산 엔진 통합**: 플랫폼 내 모든 지표 및 전략 계산을 `mysingle-pack`의 [DSLExecutor](file:///Users/donghakim/mysingle-quant/packages/mysingle-pack/src/mysingle/dsl/executor.py#19-279)로 일원화.
2.  **Fluent API 안정화**: 명세([DSL_CLASS_SPECIFICATION.md](file:///Users/donghakim/mysingle-quant/packages/mysingle-pack/src/mysingle/dsl/docs/DSL_CLASS_SPECIFICATION.md))에 따른 객체 지향적 인터페이스 구현.
3.  **서비스 마이그레이션**: MDS, Strategy, Backtest 서비스의 레거시 엔진을 제거하고 통합 엔진으로 교체.
4.  **개발자 경험(DX) 고도화**: 프론트엔드 에디터(Monaco)를 위한 자동 완성 및 타입 정의 시스템 구축.

---

## 3. Progress Dashboard (진행 현황)

| Phase | Task | Status | Expected Artifacts |
| :--- | :--- | :--- | :--- |
| **Phase 1** | `mysingle-pack` Fluent Core 구현 | [ ] | [extensions.py](file:///Users/donghakim/mysingle-quant/packages/mysingle-pack/src/mysingle/dsl/extensions.py), `proxies.py` |
| **Phase 2** | Market Data Service 마이그레이션 | [ ] | [UniversalDslIndicatorEngine](file:///Users/donghakim/mysingle-quant/services/market-data-service/app/services/indicator/engines/universal.py#18-147) 고도화 |
| **Phase 3** | Strategy Service 마이그레이션 | [ ] | [StrategyDSLService](file:///Users/donghakim/mysingle-quant/services/strategy-service/app/services/dsl_service.py#27-248) 리팩토링 |
| **Phase 4** | Backtest Service 연동 | [ ] | `SimulatedExecutor` 개발 |
| **Phase 5** | Frontend & 문서화 | [ ] | `monaco-types.d.ts`, OpenAPI Spec |

---

## 4. Implementation Plan (세부 실행 계획)

### 4.1. Phase 1: `mysingle-pack` 코어 확장
- [ ] **Fluent Proxy 레이어 구현**
    - `IndicatorProxy`, [StrategyWrapper](file:///Users/donghakim/mysingle-quant/packages/mysingle-pack/src/mysingle/dsl/extensions.py#62-147), `InputWrapper` 클래스 개발.
    - Metaprogramming을 활용하여 [stdlib](file:///Users/donghakim/mysingle-quant/packages/mysingle-pack/src/mysingle/dsl/stdlib.py#1073-1148) 함수를 객체 메서드로 자동 바인딩.
- [ ] **MSLSeries 클래스 도입**
    - 연산자 오버로딩(`>`, `<` 등) 및 유틸리티 메서드(`crosses_over`, [highest](file:///Users/donghakim/mysingle-quant/packages/mysingle-pack/src/mysingle/dsl/stdlib.py#84-96) 등)를 포함하는 전용 시계열 객체.

```python
# [핵심 로직 예시] 도트 연산자 지원을 위한 Proxies
class IndicatorProxy:
    def __getattr__(self, name):
        # rsi, sma 등 지표명을 stdlib에서 찾아 팩토리 반환
        return IndicatorFactory(name, self._data)
```

### 4.2. Phase 2: Market Data Service 마이그레이션
- [ ] **기존 Python 지표 엔진의 DSL 자산화**
    - [momentum.py](file:///Users/donghakim/mysingle-quant/services/market-data-service/app/services/indicator/engines/momentum.py) 등에 하드코딩된 로직을 [.dsl](file:///Users/donghakim/mysingle-quant/services/market-data-service/app/indicators/dsl/trend/adx.dsl) 파일로 추출하여 DB 저장.
- [ ] **Universal Engine 기본 채택**
    - 모든 지표 계산 요청에 대해 [UniversalDslIndicatorEngine](file:///Users/donghakim/mysingle-quant/services/market-data-service/app/services/indicator/engines/universal.py#18-147)을 사용하여 정합성 확보.

### 4.3. Phase 3: Strategy Service 마이그레이션
- [ ] **커스텀 IR/파서 제거**
    - 서비스 내부에 복잡하게 얽힌 [dsl_to_ir.py](file:///Users/donghakim/mysingle-quant/services/strategy-service/app/services/conversion/dsl_to_ir.py) 로직을 `mysingle-pack` 표준 파서로 대체.
- [ ] **ExecutionContext 연동**
    - 주문(entry, exit) 및 시각화(plot) 시그널을 표준화된 포맷으로 캡처하여 백테스트 서비스에 전달.

### 4.4. Phase 4: Backtest Service & Frontend
- [ ] **백테스트 데이터 파이프라인 통합**
    - 백테스트 엔진이 [DSLExecutor](file:///Users/donghakim/mysingle-quant/packages/mysingle-pack/src/mysingle/dsl/executor.py#19-279)의 중간 연산 결과(지표값)를 직접 활용하여 시뮬레이션 속도 개선.
- [ ] **Monaco용 타입 정의(`d.ts`) 자동 생성**
    - 백엔드 클래스 구조를 기반으로 프론트엔드 에디터용 타입 라이브러리 자동 추출.

---

## 5. Verification Plan (검증 계획)

### Automated Tests
- **Consistency Check**: 동일한 DSL 스크립트를 MDS(지표)와 Strategy(백테스트)에서 실행했을 때 결과값이 완전히 일치하는지 확인.
- **Resource Limit Test**: 복잡한 대규모 연산 시 메모리 및 CPU 제한(Sandboxing) 기능이 정상 작동하는지 확인.

### Manual Verification
- 프론트엔드 `DSLEditor`에서 `indicator.` 입력 시 나타나는 자동 완성 목록 및 툴팁 확인.
- 실제 복합 전략 실행 후, 차트에 실시간으로 표시되는 시그널과 로그의 정합성 확인.

# MSL 클래스 및 메서드 설계 명세: Fluent API & DSLEditor 최적화

**작성일**: 2026-01-07
**작성자**: Antigravity (Google Deepmind AI Agent)
**상태**: Technical Specification

---

## 1. 서론 (Introduction)

본 문서는 MySingle Strategy Language (MSL)의 사용자 경험(DX)을 극대화하기 위한 객체 지향적 클래스 설계를 정의합니다. 특히 프론트엔드의 **DSLEditor (Monaco Editor)**에서 강력한 타입 자동 완성(IntelliSense)을 제공하고, 사용자가 복잡한 파이썬 라이브러리 지식 없이도 도메인 용어만으로 전략을 수립할 수 있도록 하는 데 목적이 있습니다.

---

## 2. 핵심 클래스 구조 (Core Class Structure)

### 2.1. `input` 객체: 데이터 접근 및 시계열 상태
전문화된 시계열 데이터 접근점입니다.

| Property | Type | Description |
| :--- | :--- | :--- |
| `input.open`, `input.high`, `input.low`, `input.close`, `input.volume` | `Series` | 기본 OHLCV 데이터 |
| `input.symbol` | `string` | 현재 자산 심볼 (예: 'AAPL') |
| `input.interval` | `string` | 현재 타임프레임 (예: '1d', '1h') |
| `input.is_new_bar` | `boolean` | 새로운 봉이 시작되었는지 여부 |

### 2.2. `indicator` 객체: 지표 계산 (Fluent API)
지표를 카테고리 또는 이름별로 탐색하고 계산합니다.

#### 기본 사용 패턴
`indicator.{indicator_name}.{input_source}(params...)`

#### 예시: rsi
- `indicator.rsi.close(14)`: 종가 기준 14일 RSI
- `indicator.rsi.open(14)`: 시가 기준 14일 RSI

#### 예시: macd (복합 결과물 처리)
```python
macd_val = indicator.macd.close(12, 26, 9)
# macd_val은 전용 Result 객체로, 내부 속성에 접근 가능
line = macd_val.macd
signal = macd_val.signal
hist = macd_val.histogram
```

### 2.3. `strategy` 객체: 트레이딩 명령 및 상태
전략 수립에 필요한 액션과 계좌 상태 정보를 제공합니다.

| Method / Property | Description |
| :--- | :--- |
| `strategy.entry(id, direction, qty=None)` | 포지션 진입 (long/short) |
| `strategy.exit(id, from_entry)` | 특정 진입에 대한 청산 |
| `strategy.close(id)` | 특정 ID의 포지션 즉시 종료 |
| `strategy.cancel(id)` | 대기 중인 주문 취소 |
| `strategy.position_size` | 현재 보유 포지션 수량 (Property) |
| `strategy.equity` | 현재 전체 자산 가치 (Property) |
| `strategy.unrealized_pnl` | 미실현 손익 |
| `strategy.realized_pnl` | 실현 손익 |

### 2.4. `market` 객체: 시간 및 시장 상태
시장 운영 시간 및 시간 기반 필터링을 제공합니다.

| Method / Property | Description |
| :--- | :--- |
| `market.is_open` | 현재 시장이 열려있는지 여부 |
| `market.is_regular_session` | 정규장 여부 |
| `market.time` | 현재 봉의 시간 (datetime 객체) |
| `market.day_of_week` | 요일 (1:월 ~ 7:일) |
| `market.hour`, `market.minute` | 시간, 분 정보 |

### 2.5. `pattern` 객체: 캔들 패턴 인식
캔들스틱 유형을 자동으로 감지합니다.

- `pattern.doji()`: 도지 패턴 감지
- `pattern.hammer()`: 망치형 패턴 감지
- `pattern.engulfing()`: 장대봉(Bullish/Bearish) 감지
- `pattern.morning_star()`: 샛별형 패턴 감지

### 2.6. `portfolio` & `universe`: 다중 자산 및 메타 데이터
자산 정보 및 성과 지표에 접근합니다.

- `universe.sector`: 현재 종목의 섹터 정보
- `universe.market_cap`: 시가총액 정보
- `portfolio.sharpe_ratio`: 실시간 샤프 지수
- `portfolio.drawdown`: 현재 낙폭(MDD)

---

## 3. 세부 클래스 설계 (Detailed Design)

### 3.1. `Series` 클래스 (Internal/DSL)
Pandas Series를 래핑한 객체로, 안전한 연산과 추가 유틸리티를 제공합니다.

- **연산자 오버로딩**: `>`, `<`, `==`, `+`, `-`, `*`, `/` 등을 지원하여 시계열 간 직관적 비교 가능.
- **메서드**:
  - `.shift(n)`: n봉 이전 값
  - `.highest(n)`: n봉간 최고값
  - `.lowest(n)`: n봉간 최저값
  - `.crosses_over(other)`: 상향 돌파 여부 (Boolean Series)

### 3.2. `Signal` 객체: 논리 구조화
단순한 Boolean 결과 이상을 포함하는 시그널 객체입니다.

```python
# 사용 예시
buy_signal = indicator.rsi.close(14) < 30
sell_signal = indicator.rsi.close(14) > 70

# 시그널 복합 구성
strategy.entry("RSI_BUY", strategy.long) if buy_signal else None
```

---

## 4. DSLEditor (Monaco) 통합 방안

프론트엔드의 Monaco Editor에서 위 구조를 지원하기 위해 다음과 같은 기능을 구현해야 합니다.

### 4.1. TypeScript Definition (d.ts) 제공
Monaco는 내부적으로 TypeScript 언어 서비스를 사용하므로, DSL의 글로벌 객체들을 정의한 `d.ts` 파일을 주입합니다.

```typescript
// Monaco에 주입할 내부 타입 정의 예시
interface MSLIndicator {
  rsi: {
    close(window: number): MSLSeries;
    open(window: number): MSLSeries;
  };
  macd: {
    close(fast: number, slow: number, signal: number): MACDResult;
  };
}

interface MSLStrategy {
  long: string;
  short: string;
  entry(id: string, direction: string, qty?: number): void;
}

declare const indicator: MSLIndicator;
declare const strategy: MSLStrategy;
declare const input: { close: MSLSeries; open: MSLSeries; ... };
```

### 4.2. Hover & Documentation
사용자가 `indicator.rsi` 위에 마우스를 올렸을 때, `mysingle-pack`의 `stdlib` 도큐먼트를 기반으로 한 지표 설명과 파라미터 정보를 팝업으로 노출합니다.

---

## 5. 단계별 실행 계획 (Action Plan)

1.  **1단계 (Bridge)**: `mysingle-pack`의 `extensions.py`에 `IndicatorProxy`, `StrategyWrapper` 등을 고도화하여 위 인터페이스를 실제 연산 엔진으로 연결.
2.  **2단계 (Metadata Extraction)**: `stdlib.py`의 함수들을 분석하여 자동으로 `d.ts` 또는 JSON 스키마를 생성하는 스크립트 작성.
3.  **3단계 (Frontend Integration)**: 프론트엔드 `DSLEditor` 컴포넌트에 생성된 메타데이터를 로드하여 자동 완성 엔진(Monaco `languages.setMonarchTokensProvider`)에 주입.

---

## 6. 결론

이러한 도메인 주도 설계는 **"코딩을 모르는 사용자도 비즈니스 로직에만 집중하게 만든다"**는 가치를 실현합니다. `indicator.rsi.close(14)`와 같은 자연스러운 문법은 사용자에게 강력한 도구를 쥐어주는 동시에, 시스템적으로는 표준화된 데이터를 ML과 백테스트에 안정적으로 공급할 수 있는 기반이 됩니다.

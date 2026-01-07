# MSL Fluent API 활용 예시 (Examples)

본 문서는 `DSL_CLASS_SPECIFICATION.md`에 정의된 클래스 구조를 활용하여 작성된 실제 DSL 코드 예시를 제공합니다.

---

## 1. 커스텀 인디케이터 예시: Volume Normalized Volatility (VNV)

이 지표는 가격 변동성(ATR)을 거래량의 변동 수치로 정규화하여, 거래량이 동반된 진짜 변동성을 포착합니다.

```python
@metadata
  name: VNV_INDICATOR
  category: volatility
  description: Volume Normalized Volatility for trend quality assessment.

@params
  atr_period: 14
  vol_period: 20
  smoothing: 5

@calculate
  # 1. 원시 데이터 접근 (input 객체)
  close_data = input.close

  # 2. 표준 지표 활용 (indicator 객체 & Fluent API)
  # ATR 계산
  raw_atr = indicator.atr.close(atr_period)

  # 거래량 표준편차 계산
  vol_std = indicator.stddev.volume(vol_period)

  # 3. 사용자 정의 연산 (Series 객체의 연산자 오버로딩 활용)
  # 거래량이 0인 경우를 방지하기 위해 아주 작은 값 추가
  vnv_raw = (raw_atr / (vol_std + 0.00001)) * 100

  # 4. 결과 스무딩
  # 큐레이션된 rsi나 ema 메서드에 사용자 정의 시계열(vnv_raw)을 전달할 수도 있음
  vnv_final = indicator.ema.apply(vnv_raw, smoothing)

  return vnv_final
```

---

## 2. 복합 전략 예시: Triple-EMA Trend & RSI Momentum Reversal

이 전략은 장기 추세를 추종하면서, 단기 눌림목과 모멘텀 강도를 결합하여 진입/청산하며 리스크 관리를 수행합니다.

```python
@metadata
  name: ADVANCED_TREND_STRATEGY
  description: Multi-layered trend strategy with dynamic risk management.

@params
  fast_ema: 20
  med_ema: 50
  slow_ema: 200
  rsi_period: 14
  atr_period: 14
  risk_per_trade: 0.02  # 전체 자산의 2% 리스크

@strategy
  # 1. 지표 준비
  e_fast = indicator.ema.close(fast_ema)
  e_med = indicator.ema.close(med_ema)
  e_slow = indicator.ema.close(slow_ema)
  rsi_val = indicator.rsi.close(rsi_period)
  atr_val = indicator.atr.close(atr_period)

  # 2. 시장 상태 정의 (추세 확인 및 시간 필터)
  # 정규장 시간(9:30-16:00)에만 거래하며, 금요일 오후는 진입 자제
  is_trading_time = market.is_regular_session and not (market.day_of_week == 5 and market.hour >= 14)

  e_fast = indicator.ema.close(fast_ema)
  e_med = indicator.ema.close(med_ema)
  e_slow = indicator.ema.close(slow_ema)
  rsi_val = indicator.rsi.close(rsi_period)
  atr_val = indicator.atr.close(atr_period)

  is_bull_trend = (input.close > e_slow) and (e_fast > e_med)

  # 3. 캔들 패턴 결합 (pattern 객체 활용)
  # 강세 추세에서 '망치형' 혹은 '장대 양봉' 발생 시 진입 가점
  bullish_setup = pattern.hammer() or pattern.engulfing().is_bullish

  # 4. 진입 로직 (Entry)
  long_condition = (is_trading_time and
                   is_bull_trend and
                   bullish_setup and
                   rsi_val.crosses_over(35))

  if long_condition and strategy.position_size == 0:
      # 포트폴리오 상태에 따른 동적 리스크 조절 (Drawdown이 크면 리스크 축소)
      current_risk = risk_per_trade if portfolio.drawdown < 0.10 else risk_per_trade * 0.5

      stop_dist = atr_val * 2
      qty = (strategy.equity * current_risk) / stop_dist
      strategy.entry("Long_Trend", strategy.long, qty=qty)

  # 5. 청산 및 익절 (Exit)
  # 미실현 수익이 일정 수준 이상이면 절반 익절
  if strategy.unrealized_pnl > (strategy.equity * 0.05):
      strategy.close("Long_Trend", qty_percent=50)

  # 6. 시각화
  plot(e_fast, title="Fast EMA", color="blue")
  plot(e_slow, title="Slow EMA", color="red")

  # 시장 상태 정보 기록 (디버깅용)
  if market.is_open:
      var last_bar_time = market.time
```

---

## 3. 예시 코드의 가치

1.  **가독성**: `indicator.ema.close(20)`와 같은 문법은 함수의 파라미터가 무엇인지, 어떤 데이터를 사용하는지 명확히 보여줍니다.
2.  **리스크 관리 연동**: `strategy.equity`를 이용해 실제 전체 자산 대비 리스크를 계산하여 수량을 조절하는 **자금 관리(Money Management)** 로직을 구현할 수 있습니다.
3.  **데이터 안전성**: 사용자가 Pandas의 복잡한 슬라이싱이나 인덱싱을 고민하지 않고 `shift(1)`나 `crosses_over()` 같은 도메인 친화적 함수를 사용할 수 있습니다.

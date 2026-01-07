# 도메인 주도 DSL 설계 제안: 객체 지향 및 Fluent API 도입

**작성일**: 2026-01-07
**작성자**: Antigravity (Google Deepmind AI Agent)
**상태**: Draft Proposal

---

## 1. 배경 및 동기 (Context & Motivation)

현재 MySingle DSL(MSL)은 `RSI(close, 14)`와 같이 함수형 스타일을 주로 사용합니다. 이 방식은 간단하지만 다음과 같은 한계가 있습니다.

- **낮은 발견 가능성 (Discoverability)**: 사용자가 어떤 지표가 존재하는지 알기 어렵습니다.
- **빈약한 도구 지원 (IDE Support)**: 일반적인 코드 에디터에서 타입 힌트나 자동 완성을 제공하기 어렵습니다.
- **추상화 부족**: 사용자가 `pandas.Series`나 `numpy` 배열의 내부 구조를 어느 정도 이해해야 합니다.

사용자의 제안대로 **객체 지향적(OO) 스타일**과 **Fluent API**를 도입하면, "말하듯이 코딩하는" 경험(Natural Language-like Coding)과 강력한 타입 힌트 지원이 가능해집니다.

---

## 2. 제안: Fluent API 디자인

### 2.1. 인디케이터 접근 (Indicator Discovery)
기존의 전역 함수 방식에서 `indicator` 객체를 통한 계층적 접근 방식으로 전환합니다.

```python
# AS-IS (함수형)
rsi_val = RSI(close, 14)
sma_val = SMA(close, 20)

# TO-BE (Fluent API) - 사용자가 제안한 형태
rsi_val = indicator.rsi.close(14)
sma_val = indicator.sma.close(20)

# 복합 데이터 접근
macd_res = indicator.macd.close(12, 26, 9)
hist = macd_res.histogram
```

### 2.2. 입력 데이터 추상화 (Input Abstraction)
`input` 객체를 통해 원시 데이터에 접근하며, 이는 내부적으로 `pandas.Series`를 래핑한 전용 객체를 반환합니다.

```python
close_price = input.close
high_price = input.high

# 전용 객체는 연산자 오버로딩을 통해 직관적인 비교 가능
condition = input.close > indicator.sma.close(20)
```

### 2.3. 전략 및 시그널 (Strategy & Signal)
`strategy` 객체를 통해 시그널 생성 및 포지션 관리를 수행합니다.

```python
if crossover(input.close, indicator.sma.close(20)):
    strategy.entry("long_position", strategy.long)
```

---

## 3. 구현 아키텍처 (Implementation Architecture)

### 3.1. 래퍼 클래스 패턴 (Wrapper Pattern)
`mysingle-pack`의 `stdlib`에 있는 순수 함수들을 객체 지향적으로 감싸는 래퍼 레이어를 구축합니다.

```python
class IndicatorProxy:
    def __init__(self, data):
        self._data = data

    @property
    def rsi(self):
        return IndicatorFactory(self._data, RSI_func)

class IndicatorFactory:
    def __init__(self, data, func):
        self._data = data
        self._func = func

    def close(self, *args, **kwargs):
        return self._func(self._data['close'], *args, **kwargs)

    def open(self, *args, **kwargs):
        return self._func(self._data['open'], *args, **kwargs)
```

### 3.2. 타입 힌트 및 자동 완성 (Developer Experience)
에디터(VS Code 등)가 `.msl` 파일 내에서 자동 완성을 제공하게 하기 위해 다음 전략을 사용합니다.

1.  **Python Stub Files (.pyi)**: DSL의 전역 네임스페이스(`indicator`, `input`, `strategy`)를 정의한 `.pyi` 파일을 제공합니다.
2.  **VS Code Extension**: `msl` 파일 확장자를 인식하고, 내부적으로 Python 언어 서버(Pylance)를 활용하여 해당 Stub 파일을 참조하게 설정합니다.

---

## 4. 기대 효과 (Expected Benefits)

1.  **진입 장벽 완화**: 사용자에게 사용 가능한 모든 메서드가 도트(`.`) 연산자를 통해 노출되므로 학습 곡선이 매우 낮아집니다.
2.  **코드 안정성**: 사용자가 원시 데이터(Pandas)를 직접 만지지 않으므로, 데이터 오염이나 인덱스 불일치 등의 런타임 에러를 방지할 수 있습니다.
3.  **컴파일러 최적화**: 객체 지향적 구조는 AST 파싱 시 더 명확한 의미(Semantics)를 제공하므로, 실행 전 최적화(JIT 등)가 용이해집니다.

---

## 5. 결론 및 제언

사용자께서 제안하신 `indicator.rsi.close(14)`와 같은 인터페이스는 현대적인 트레이딩 플랫폼(Pine Script 등)이 지향하는 방향과 일치하며, 특히 **노코드 환경에서 작성된 로직을 코드로 변환했을 때의 가독성**을 극대화할 수 있습니다.

본 제안을 바탕으로 `mysingle-pack`의 `extensions.py`를 확장하여 프로토타입을 구현하고, 이를 실제 서비스에 단계적으로 적용할 것을 권장합니다.

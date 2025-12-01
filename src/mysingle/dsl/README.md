# mysingle.dsl

도메인 특화 언어 (DSL) 파서 및 실행 엔진

## 주요 기능

- 전략 DSL 파싱
- 지표 계산 실행
- 백테스팅 스크립트 검증

## 사용 예시

```python
from mysingle.dsl import parse_strategy, execute_indicator

# 전략 파싱
strategy = parse_strategy("""
WHEN close > sma(close, 20)
THEN buy(100)
""")

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

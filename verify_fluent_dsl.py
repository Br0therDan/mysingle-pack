import numpy as np
import pandas as pd

from mysingle.dsl.executor import DSLExecutor
from mysingle.dsl.extensions import ExecutionContext
from mysingle.dsl.parser import DSLParser

# 1. 샘플 데이터 생성 (OHLCV + Time Index)
dates = pd.date_range("2026-01-01 09:00", periods=100, freq="15min")
data = pd.DataFrame(
    {
        "open": np.random.randn(100).cumsum() + 100,
        "high": np.random.randn(100).cumsum() + 105,
        "low": np.random.randn(100).cumsum() + 95,
        "close": np.random.randn(100).cumsum() + 100,
        "volume": np.random.randint(100, 1000, 100),
    },
    index=dates,
)

# 메타데이터 주입
data.attrs["symbol"] = "AAPL"
data.attrs["metadata"] = {"sector": "Technology", "market_cap": 3e12}

# 2. 전용 파서 및 실행기 초기화
parser = DSLParser()
executor = DSLExecutor(parser=parser)

# 3. 신규 Fluent API를 사용하는 DSL 코드 (종합 테스트)
dsl_code = """
# 1. Market & Input 테스트
is_afternoon = market.hour >= 13
sym = input.symbol

# 2. Pattern 테스트 (Doji)
doji_signal = pattern.doji()

# 3. Indicator & Portfolio 테스트
rsi_val = indicator.rsi.close(14)
risk_factor = 0.01 if portfolio.drawdown < 0.05 else 0.005

# 4. Strategy & Visualization 테스트
if doji_signal and is_afternoon:
    strategy.entry("Doji_Buy", strategy.long, qty=portfolio.equity * risk_factor)

plot(rsi_val, title="RSI", color="blue")

# 최종 결과값 반환
result = (rsi_val > 50) & (market.is_regular_session)
"""

# 4. Execution Context 준비

context = ExecutionContext(equity=50000.0)
params = {"_context": context}

print("--- DSL Execution Start ---")
try:
    # 컴파일 및 실행
    compiled = parser.parse(dsl_code)
    result = executor.execute(compiled, data, params=params)

    print("\n[Result Sample]")
    print(result.tail())
    print(f"Result Length: {len(result)}")

    print("\n[Context Summary]")
    print(f"Equity: {context.equity}")
    print(f"Trading Commands: {len(context.trading_commands)}")
    if context.trading_commands:
        print(f"First Command: {context.trading_commands[0]}")
    print(f"Visualizations: {len(context.visualizations)}")

    if len(result) == 100 and context.trading_commands:
        print(
            "\nSUCCESS: All P1 objects (market, pattern, portfolio, strategy) worked!"
        )
    else:
        print("\nFAILURE: Some components failed to execute correctly")

except Exception as e:
    print(f"\nERROR: Execution failed: {e}")
    import traceback

    traceback.print_exc()

"""
Test DSL extensions (var, plot, strategy)
"""

import pandas as pd

from mysingle.dsl.executor import DSLExecutor
from mysingle.dsl.extensions import ExecutionContext


def test_extensions_execution():
    """Test that var, plot, and strategy commands work in DSL"""

    # Setup data
    data = pd.DataFrame(
        {"close": [10, 11, 12, 11, 10], "volume": [100, 110, 120, 110, 100]}
    )

    # Setup context
    context = ExecutionContext()
    params = {"_context": context, "fast": 12}

    # DSL code using extensions
    dsl_code = """
# State variable (mock)
x = var(0, title="MyVar")

# Visualization
plot(close, title="Close Price", color="blue")

# Strategy command
strategy.entry("long_entry", strategy.long, qty=1.0, comment="Enter Long")

# Result
result = close + x
"""

    # Execute
    executor = DSLExecutor()
    result = executor.compile_and_execute(dsl_code, data, params)

    # Verify result
    assert isinstance(result, pd.Series)
    assert len(result) == 5

    # Verify side effects in context
    assert len(context.visualizations) == 1
    viz = context.visualizations[0]
    assert viz.type == "plot"
    assert viz.title == "Close Price"
    assert viz.color == "blue"
    # Series equality check
    pd.testing.assert_series_equal(viz.series, data["close"])

    assert len(context.trading_commands) == 1
    cmd = context.trading_commands[0]
    assert cmd.type == "entry"
    assert cmd.id == "long_entry"
    assert cmd.direction == "long"
    assert cmd.qty == 1.0
    assert cmd.comment == "Enter Long"


def test_strategy_methods():
    """Test all strategy methods"""
    data = pd.DataFrame({"close": [10]})
    context = ExecutionContext()
    params = {"_context": context}

    dsl_code = """
strategy.entry("e1", strategy.long)
strategy.exit("x1", "e1", stop=9.0, limit=11.0)
strategy.close("e1", comment="Close it")
strategy.cancel("e1")
result = close
"""

    executor = DSLExecutor()
    executor.compile_and_execute(dsl_code, data, params)

    assert len(context.trading_commands) == 4
    assert context.trading_commands[0].type == "entry"
    assert context.trading_commands[1].type == "exit"
    assert context.trading_commands[2].type == "close"
    assert context.trading_commands[3].type == "cancel"

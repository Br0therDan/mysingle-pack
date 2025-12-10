# Changelog - mysingle.dsl

## [2.6.5] - 2025-12-10

### Fixed
- **DSL Executor**: DataFrame columns are now auto-injected as namespace variables
  - OHLCV columns (`open`, `high`, `low`, `close`, `volume`) are now directly accessible
  - Previously: DSL code had to use `data['close']` or `data.close`
  - Now: Can use `close`, `high`, `low` directly in DSL code
  - Improves readability and aligns with TradingView Pine Script syntax
  - **Breaking Change**: None (backward compatible - `data.close` still works)

### Impact
- **Backtest Service**: Fixes `name 'close' is not defined` execution errors
- **Strategy Templates**: All `.msl` templates can now use direct OHLCV variable access
- **Performance**: No performance impact (same namespace injection mechanism)

### Example
```python
# Before (still works)
fast_ema = EMA(data['close'], 9)

# After (now also works)
fast_ema = EMA(close, 9)
```

### Technical Details
- Modified: `src/mysingle/dsl/executor.py::_build_namespace()`
- Added loop to inject all DataFrame columns as individual variables
- Tested with 34 DSL test cases - all passing

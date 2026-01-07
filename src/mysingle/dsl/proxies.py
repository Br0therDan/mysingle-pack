"""
MSL (MySingle Strategy Language) Fluent API Proxies.
Provides 'indicator' and 'input' objects within the DSL.
"""

from typing import Any

import pandas as pd

from mysingle.dsl import stdlib
from mysingle.dsl.extensions import ExecutionContext, TradingCommand, Visualization
from mysingle.dsl.series import MSLSeries


class IndicatorFactory:
    """
    Factory that binds a specific indicator function (from stdlib) to an input source.
    Example: indicator.rsi.close(14)
    """

    def __init__(self, name: str, data: pd.DataFrame):
        self._name = name.upper()
        self._data = data
        self._func = getattr(stdlib, self._name, None)

    def __call__(self, series: Any, *args, **kwargs):
        """Allows direct call if necessary: indicator.rsi(input.close, 14)"""
        if self._func:
            # Unwrap if MSLSeries
            unwrapped_series = series.series if hasattr(series, "series") else series
            result = self._func(unwrapped_series, *args, **kwargs)
            return MSLSeries(result) if isinstance(result, pd.Series) else result
        raise AttributeError(f"Indicator '{self._name}' not found in stdlib")

    def _call_with_source(self, source: str, *args, **kwargs):
        if source not in self._data.columns:
            raise AttributeError(f"Data source '{source}' not found in input data")
        return self(self._data[source], *args, **kwargs)

    def close(self, *args, **kwargs):
        return self._call_with_source("close", *args, **kwargs)

    def open(self, *args, **kwargs):
        return self._call_with_source("open", *args, **kwargs)

    def high(self, *args, **kwargs):
        return self._call_with_source("high", *args, **kwargs)

    def low(self, *args, **kwargs):
        return self._call_with_source("low", *args, **kwargs)

    def volume(self, *args, **kwargs):
        return self._call_with_source("volume", *args, **kwargs)

    def apply(self, series: Any, *args, **kwargs):
        """Allows applying indicator to any series: indicator.ema.apply(custom_series, 20)"""
        return self(series, *args, **kwargs)


class IndicatorProxy:
    """
    Root 'indicator' object.
    Usage: indicator.rsi.close(14)
    """

    def __init__(self, data: pd.DataFrame):
        self._data = data

    def __getattr__(self, name: str) -> IndicatorFactory:
        # Avoid recursion or private attributes
        if name.startswith("_"):
            raise AttributeError(name)
        return IndicatorFactory(name, self._data)


class InputProxy:
    """
    Root 'input' object.
    Usage: input.close
    """

    def __init__(self, data: pd.DataFrame):
        self._data = data

    def __getattr__(self, name: str) -> MSLSeries:
        if name in self._data.columns:
            return MSLSeries(self._data[name], name=name)
        raise AttributeError(f"Input source '{name}' not found")

    @property
    def symbol(self) -> str:
        return self._data.attrs.get("symbol", "unknown")

    @property
    def interval(self) -> str:
        return self._data.attrs.get("interval", "unknown")


class MarketProxy:
    """
    Root 'market' object for time and session info.
    """

    def __init__(self, data: pd.DataFrame):
        self._data = data
        self._index = pd.to_datetime(data.index)

    @property
    def time(self):
        return MSLSeries(pd.Series(self._index, index=self._data.index))

    @property
    def hour(self):
        return MSLSeries(pd.Series(self._index.hour, index=self._data.index))

    @property
    def minute(self):
        return MSLSeries(pd.Series(self._index.minute, index=self._data.index))

    @property
    def day_of_week(self):
        return MSLSeries(
            pd.Series(self._index.dayofweek + 1, index=self._data.index)
        )  # 1:Mon, 7:Sun

    @property
    def is_regular_session(self):
        # Basic logic: 09:30 - 16:00
        time_nums = self._index.hour * 100 + self._index.minute
        mask = (time_nums >= 930) & (time_nums < 1600)
        return MSLSeries(pd.Series(mask, index=self._data.index))


class PatternProxy:
    """
    Root 'pattern' object for candlestick patterns.
    """

    def __init__(self, data: pd.DataFrame):
        self._data = data

    def doji(self):
        from mysingle.dsl.stdlib import DOJI

        return MSLSeries(DOJI(self._data))

    def hammer(self):
        from mysingle.dsl.stdlib import HAMMER

        return MSLSeries(HAMMER(self._data))

    def engulfing(self):
        class Comp:
            def __init__(self, data):
                self._data = data

            @property
            def is_bullish(self):
                from mysingle.dsl.stdlib import BULLISH_ENGULFING

                return MSLSeries(BULLISH_ENGULFING(self._data))

            @property
            def is_bearish(self):
                from mysingle.dsl.stdlib import BEARISH_ENGULFING

                return MSLSeries(BEARISH_ENGULFING(self._data))

        return Comp(self._data)


class PortfolioProxy:
    """
    Root 'portfolio' object for real-time account/backtest metrics.
    """

    def __init__(self, context):
        self._ctx = context

    @property
    def equity(self):
        return self._ctx.equity if self._ctx else 100000.0

    @property
    def position_size(self):
        return self._ctx.position_size if self._ctx else 0.0

    @property
    def drawdown(self):
        return getattr(self._ctx, "drawdown", 0.0)


class UniverseProxy:
    """
    Root 'universe' object for asset metadata.
    """

    def __init__(self, data: pd.DataFrame):
        self._meta = data.attrs.get("metadata", {})

    @property
    def sector(self):
        return self._meta.get("sector", "unknown")

    @property
    def market_cap(self):
        return self._meta.get("market_cap", 0)


class StrategyWrapper:
    """
    Root 'strategy' object for trading commands.
    Usage: strategy.entry("buy", strategy.long)
    """

    long = "long"
    short = "short"

    def __init__(self, context: ExecutionContext):
        self._ctx = context

    def entry(
        self,
        id: str,
        direction: str,
        qty: float = None,
        limit: float = None,
        stop: float = None,
        comment: str = None,
    ):
        if self._ctx:
            self._ctx.add_trading_command(
                TradingCommand("entry", id, direction, qty, limit, stop, comment)
            )

    def close(self, id: str, comment: str = None, qty_percent: float = None):
        if self._ctx:
            self._ctx.add_trading_command(
                TradingCommand("close", id, comment=comment, qty=qty_percent)
            )

    def exit(
        self,
        id: str,
        from_entry: str,
        stop: float = None,
        limit: float = None,
        comment: str = None,
    ):
        if self._ctx:
            self._ctx.add_trading_command(
                TradingCommand(
                    "exit",
                    id,
                    direction=from_entry,
                    stop=stop,
                    limit=limit,
                    comment=comment,
                )
            )

    def cancel(self, id: str):
        if self._ctx:
            self._ctx.add_trading_command(TradingCommand("cancel", id))

    @property
    def equity(self):
        return self._ctx.equity if self._ctx else 100000.0

    @property
    def position_size(self):
        return self._ctx.position_size if self._ctx else 0.0


class VarProxy:
    """
    Root 'var' object for managing strategy variables.
    Usage: var("my_var", 10) or var("my_var")
    """

    def __init__(self, context: ExecutionContext):
        self._ctx = context

    def __call__(self, name: str, value: Any = None):
        if self._ctx:
            if value is not None:
                self._ctx.set_variable(name, value)
            else:
                return self._ctx.get_variable(name)
        return None  # Or raise an error if context is None and trying to get


class PlotProxy:
    """
    Root 'plot' object for visualizing series.
    Usage: plot(indicator.rsi.close(14), name="RSI", color="blue")
    """

    def __init__(self, context: ExecutionContext):
        self._ctx = context

    def __call__(
        self,
        series: MSLSeries,
        title: str = None,
        color: str = None,
        style: str = None,
        **kwargs,
    ):
        name = title or kwargs.get("name")
        if self._ctx:
            self._ctx.add_visualization(
                Visualization("plot", series, name, color, style)
            )

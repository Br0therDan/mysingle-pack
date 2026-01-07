"""
MSL (MySingle Strategy Language) Series Wrapper.
Wraps pandas.Series to provide operator overloading and fluent API.
"""

import pandas as pd


class MSLSeries:
    """
    Wraps a pandas Series to provide a restricted and fluent interface within the DSL.
    """

    def __init__(self, series: pd.Series, name: str = None):
        if not isinstance(series, pd.Series):
            # Handle list/array conversion if necessary, but usually it should be a Series
            series = pd.Series(series)
        self._series = series
        self._name = name or series.name

    @property
    def series(self) -> pd.Series:
        return self._series

    @property
    def values(self):
        return self._series.values

    def __len__(self):
        return len(self._series)

    def __getitem__(self, key):
        result = self._series.__getitem__(key)
        if isinstance(result, pd.Series):
            return MSLSeries(result)
        return result

    # Operator Overloading: Arithmetic
    def __add__(self, other):
        return self._wrap_op(self._series + self._unwrap(other))

    def __sub__(self, other):
        return self._wrap_op(self._series - self._unwrap(other))

    def __mul__(self, other):
        return self._wrap_op(self._series * self._unwrap(other))

    def __truediv__(self, other):
        return self._wrap_op(self._series / self._unwrap(other))

    # Operator Overloading: Comparison
    def __gt__(self, other):
        return self._wrap_op(self._series > self._unwrap(other))

    def __lt__(self, other):
        return self._wrap_op(self._series < self._unwrap(other))

    def __ge__(self, other):
        return self._wrap_op(self._series >= self._unwrap(other))

    def __le__(self, other):
        return self._wrap_op(self._series <= self._unwrap(other))

    def __eq__(self, other):
        return self._wrap_op(self._series == self._unwrap(other))

    # Logical
    def __and__(self, other):
        return self._wrap_op(self._series & self._unwrap(other))

    def __or__(self, other):
        return self._wrap_op(self._series | self._unwrap(other))

    # Fluent Methods
    def shift(self, periods: int = 1):
        """Returns the series shifted by n periods."""
        return MSLSeries(self._series.shift(periods))

    def highest(self, window: int):
        """Returns the highest value over a rolling window."""
        return MSLSeries(self._series.rolling(window=window).max())

    def lowest(self, window: int):
        """Returns the lowest value over a rolling window."""
        return MSLSeries(self._series.rolling(window=window).min())

    def sma(self, window: int):
        """Simple Moving Average."""
        return MSLSeries(self._series.rolling(window=window).mean())

    def ema(self, span: int):
        """Exponential Moving Average."""
        return MSLSeries(self._series.ewm(span=span, adjust=False).mean())

    def crosses_over(self, other):
        """Detects upward crossover of this series over 'other'."""
        other_series = self._unwrap(other)
        curr = self._series
        prev = self._series.shift(1)
        o_curr = other_series
        o_prev = other_series.shift(1)
        return MSLSeries((curr > o_curr) & (prev <= o_prev))

    def crosses_under(self, other):
        """Detects downward crossunder of this series under 'other'."""
        other_series = self._unwrap(other)
        curr = self._series
        prev = self._series.shift(1)
        o_curr = other_series
        o_prev = other_series.shift(1)
        return MSLSeries((curr < o_curr) & (prev >= o_prev))

    # Internal helpers
    def _unwrap(self, other):
        if isinstance(other, MSLSeries):
            return other.series
        return other

    def _wrap_op(self, result):
        if isinstance(result, pd.Series):
            return MSLSeries(result)
        return result

    def __repr__(self):
        return f"MSLSeries(name={self._name}, length={len(self._series)})"

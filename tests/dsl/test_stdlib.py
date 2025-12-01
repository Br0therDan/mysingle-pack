"""
Tests for mysingle.dsl.stdlib module.
"""

import pandas as pd
import pytest

try:
    from mysingle.dsl.stdlib import EMA, RSI, SMA

    DSL_STDLIB_AVAILABLE = True
except ImportError:
    DSL_STDLIB_AVAILABLE = False


@pytest.mark.skipif(not DSL_STDLIB_AVAILABLE, reason="DSL stdlib not installed")
class TestDSLStandardLibrary:
    """Tests for DSL standard library functions."""

    def test_sma_calculation(self, sample_dataframe):
        """Test Simple Moving Average calculation."""
        result = SMA(sample_dataframe["close"], period=3)

        assert result is not None
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_dataframe)

    def test_ema_calculation(self, sample_dataframe):
        """Test Exponential Moving Average calculation."""
        result = EMA(sample_dataframe["close"], period=3)

        assert result is not None
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_dataframe)

    def test_rsi_calculation(self, sample_dataframe):
        """Test RSI calculation."""
        result = RSI(sample_dataframe["close"], period=14)

        assert result is not None
        assert isinstance(result, pd.Series)
        # RSI values should be between 0 and 100
        valid_rsi = result.dropna()
        assert all((valid_rsi >= 0) & (valid_rsi <= 100))

    def test_indicator_with_invalid_period(self, sample_dataframe):
        """Test indicator with invalid period."""
        with pytest.raises((ValueError, Exception)):
            SMA(sample_dataframe["close"], period=0)

    def test_indicator_with_short_data(self):
        """Test indicator with insufficient data."""
        short_df = pd.DataFrame({"close": [100.0, 101.0]})

        # Should handle short data gracefully
        result = SMA(short_df["close"], period=3)
        assert result is not None

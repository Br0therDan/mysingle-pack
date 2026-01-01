"""
Tests for mysingle.dsl.stdlib module.
"""

import pandas as pd
import pytest

try:
    from mysingle.dsl.stdlib import (
        EMA,
        RSI,
        SMA,
        adx,
        cci,
        donchian_channels,
        keltner_channels,
        parabolic_sar,
        stochrsi,
        supertrend,
        tema,
        williams_r,
    )

    DSL_STDLIB_AVAILABLE = True
except ImportError:
    DSL_STDLIB_AVAILABLE = False


@pytest.mark.skipif(not DSL_STDLIB_AVAILABLE, reason="DSL stdlib not installed")
class TestDSLStandardLibrary:
    """Tests for DSL standard library functions."""

    def test_sma_calculation(self, sample_dataframe):
        """Test Simple Moving Average calculation."""
        result = SMA(sample_dataframe["close"], window=3)

        assert result is not None
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_dataframe)

    def test_ema_calculation(self, sample_dataframe):
        """Test Exponential Moving Average calculation."""
        result = EMA(sample_dataframe["close"], span=3)

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
            RSI(sample_dataframe["close"], period=0)

    def test_indicator_with_short_data(self):
        """Test indicator with insufficient data."""
        short_df = pd.DataFrame({"close": [100.0, 101.0]})

        # Should handle short data gracefully
        result = SMA(short_df["close"], window=3)
        assert result is not None

    def test_ichimoku_calculation(self, sample_dataframe):
        """Test Ichimoku Cloud calculation."""
        from mysingle.dsl.stdlib import ichimoku

        result = ichimoku(
            sample_dataframe["high"],
            sample_dataframe["low"],
            sample_dataframe["close"],
            tenkan_period=3,
            kijun_period=5,
            senkou_b_period=5,
        )

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert "tenkan" in result.columns
        assert "kijun" in result.columns
        assert "senkou_a" in result.columns
        assert "senkou_b" in result.columns
        assert "chikou" in result.columns
        assert len(result) == len(sample_dataframe)

    def test_cci_calculation(self, sample_dataframe):
        """Test CCI calculation."""
        result = cci(
            sample_dataframe["high"],
            sample_dataframe["low"],
            sample_dataframe["close"],
            period=14,
        )
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_dataframe)

    def test_donchian_channels(self, sample_dataframe):
        """Test Donchian Channels."""
        result = donchian_channels(
            sample_dataframe["high"], sample_dataframe["low"], period=20
        )
        assert isinstance(result, pd.DataFrame)
        assert "upper" in result.columns
        assert "middle" in result.columns
        assert "lower" in result.columns

    def test_keltner_channels(self, sample_dataframe):
        """Test Keltner Channels."""
        result = keltner_channels(
            sample_dataframe["high"],
            sample_dataframe["low"],
            sample_dataframe["close"],
            ema_period=20,
            atr_period=10,
            multiplier=2.0,
        )
        assert isinstance(result, pd.DataFrame)
        assert "upper" in result.columns
        assert "middle" in result.columns
        assert "lower" in result.columns

    def test_adx_calculation(self, sample_dataframe):
        """Test ADX calculation."""
        result = adx(
            sample_dataframe["high"],
            sample_dataframe["low"],
            sample_dataframe["close"],
            period=14,
        )
        assert isinstance(result, pd.DataFrame)
        assert "adx" in result.columns
        assert "plus_di" in result.columns
        assert "minus_di" in result.columns

        # ADX should be between 0 and 100 (mostly)
        valid_adx = result["adx"].dropna()
        assert all((valid_adx >= 0) & (valid_adx <= 100))

    def test_parabolic_sar(self, sample_dataframe):
        """Test Parabolic SAR."""
        result = parabolic_sar(
            sample_dataframe["high"],
            sample_dataframe["low"],
            acceleration=0.02,
            maximum=0.2,
        )
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_dataframe)

    def test_stochrsi(self, sample_dataframe):
        """Test Stochastic RSI."""
        result = stochrsi(
            sample_dataframe["close"],
            rsi_period=14,
            stoch_period=14,
            k_smooth=3,
            d_smooth=3,
        )
        assert isinstance(result, pd.DataFrame)
        assert "k" in result.columns
        assert "d" in result.columns

        # K and D should be between 0 and 100
        valid_k = result["k"].dropna()
        assert all((valid_k >= 0) & (valid_k <= 100))

    def test_supertrend(self, sample_dataframe):
        """Test Supertrend."""
        result = supertrend(
            sample_dataframe["high"],
            sample_dataframe["low"],
            sample_dataframe["close"],
            atr_period=10,
            multiplier=3.0,
        )
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_dataframe)

    def test_tema(self, sample_dataframe):
        """Test TEMA."""
        result = tema(sample_dataframe["close"], period=20)
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_dataframe)

    def test_williams_r(self, sample_dataframe):
        """Test Williams %R."""
        result = williams_r(
            sample_dataframe["high"],
            sample_dataframe["low"],
            sample_dataframe["close"],
            period=14,
        )
        assert isinstance(result, pd.Series)

        valid_wr = result.dropna()
        # Williams %R is between -100 and 0
        assert all((valid_wr >= -100) & (valid_wr <= 0))

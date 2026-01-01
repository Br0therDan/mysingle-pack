"""DSL 표준 라이브러리 - 공통 함수"""

from typing import Any, Callable, Literal

import numpy as np
import pandas as pd


def SMA(series: pd.Series, window: int) -> pd.Series:
    """
    Simple Moving Average

    Args:
        series: 입력 시리즈 (보통 close 가격)
        window: 이동평균 기간

    Returns:
        pd.Series: SMA 값
    """
    return series.rolling(window=window).mean()


def EMA(series: pd.Series, span: int) -> pd.Series:
    """
    Exponential Moving Average

    Args:
        series: 입력 시리즈
        span: EMA 기간

    Returns:
        pd.Series: EMA 값
    """
    return series.ewm(span=span, adjust=False).mean()


def WMA(series: pd.Series, window: int) -> pd.Series:
    """
    Weighted Moving Average

    Args:
        series: 입력 시리즈
        window: WMA 기간

    Returns:
        pd.Series: WMA 값
    """
    weights = pd.Series(range(1, window + 1))
    return series.rolling(window).apply(lambda x: (x * weights).sum() / weights.sum())


def crossover(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """
    상향 돌파 검사

    series1이 series2를 아래에서 위로 돌파하는 시점 탐지

    Args:
        series1: 비교 대상 시리즈 1
        series2: 비교 대상 시리즈 2

    Returns:
        pd.Series: 상향 돌파 시 True
    """
    return (series1 > series2) & (series1.shift(1) <= series2.shift(1))


def crossunder(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """
    하향 돌파 검사

    series1이 series2를 위에서 아래로 돌파하는 시점 탐지

    Args:
        series1: 비교 대상 시리즈 1
        series2: 비교 대상 시리즈 2

    Returns:
        pd.Series: 하향 돌파 시 True
    """
    return (series1 < series2) & (series1.shift(1) >= series2.shift(1))


def highest(series: pd.Series, window: int) -> pd.Series:
    """
    N일 최고값

    Args:
        series: 입력 시리즈
        window: 기간

    Returns:
        pd.Series: N일 최고값
    """
    return series.rolling(window=window).max()


def lowest(series: pd.Series, window: int) -> pd.Series:
    """
    N일 최저값

    Args:
        series: 입력 시리즈
        window: 기간

    Returns:
        pd.Series: N일 최저값
    """
    return series.rolling(window=window).min()


def change(series: pd.Series, periods: int = 1) -> pd.Series:
    """
    절대 변화량

    Args:
        series: 입력 시리즈
        periods: 기간 (기본 1)

    Returns:
        pd.Series: 절대 변화량
    """
    return series.diff(periods)


def pct_change(series: pd.Series, periods: int = 1) -> pd.Series:
    """
    백분율 변화량

    Args:
        series: 입력 시리즈
        periods: 기간 (기본 1)

    Returns:
        pd.Series: 백분율 변화량
    """
    return series.pct_change(periods)


def stdev(series: pd.Series, window: int) -> pd.Series:
    """
    표준편차

    Args:
        series: 입력 시리즈
        window: 기간

    Returns:
        pd.Series: 표준편차
    """
    return series.rolling(window=window).std()


def bbands(series: pd.Series, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    """
    Bollinger Bands

    Args:
        series: 입력 시리즈 (보통 close 가격)
        window: 이동평균 기간 (기본 20)
        num_std: 표준편차 배수 (기본 2.0)

    Returns:
        pd.DataFrame: upper, middle, lower 컬럼
    """
    middle = SMA(series, window)
    std = stdev(series, window)

    return pd.DataFrame(
        {
            "upper": middle + (std * num_std),
            "middle": middle,
            "lower": middle - (std * num_std),
        }
    )


def RSI(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index

    Args:
        series: 입력 시리즈 (보통 close 가격)
        period: RSI 기간 (기본 14)

    Returns:
        pd.Series: RSI 값 (0-100 범위)
    """
    if period <= 0:
        raise ValueError("Period must be greater than 0")

    # 가격 변화 계산
    delta = series.diff().astype(float)

    # 상승/하락 분리
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # 평균 상승/하락 (EMA 사용)
    avg_gain = gain.ewm(span=period, adjust=False).mean()
    avg_loss = loss.ewm(span=period, adjust=False).mean()

    # RS 계산
    rs = avg_gain / avg_loss

    # RSI 계산
    rsi = 100 - (100 / (1 + rs))

    return rsi


def atr(
    high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14
) -> pd.Series:
    """
    Average True Range

    Args:
        high: 고가 시리즈
        low: 저가 시리즈
        close: 종가 시리즈
        window: ATR 기간 (기본 14)

    Returns:
        pd.Series: ATR 값
    """
    # True Range 계산
    high_low = high - low
    high_close = abs(high - close.shift(1))
    low_close = abs(low - close.shift(1))

    tr = pd.DataFrame({"hl": high_low, "hc": high_close, "lc": low_close}).max(axis=1)

    # ATR (EMA of TR)
    return EMA(tr, window)


# ============================================================================
# 전략 특화 함수 (Strategy Service 전용)
# ============================================================================


def generate_signal(
    condition: pd.Series, signal_type: Literal["long", "short"] = "long"
) -> pd.Series:
    """
    조건을 명시적 boolean 시그널로 변환

    Args:
        condition: 조건 Series (True/False)
        signal_type: 시그널 방향 ("long" or "short")

    Returns:
        pd.Series[bool]: 시그널 (True = 진입, False = 보유)

    Example:
        >>> oversold = data['RSI'] < 30
        >>> buy_signal = generate_signal(oversold, signal_type="long")
    """
    # 명시적 boolean 변환
    return condition.astype(bool)


def entry_exit_signals(
    entry_condition: pd.Series, exit_condition: pd.Series
) -> pd.DataFrame:
    """
    진입 조건과 청산 조건을 페어로 생성

    Args:
        entry_condition: 진입 조건 Series
        exit_condition: 청산 조건 Series

    Returns:
        pd.DataFrame: {'entry': pd.Series[bool], 'exit': pd.Series[bool]}

    Example:
        >>> entry = crossover(data['SMA_50'], data['SMA_200'])
        >>> exit = crossunder(data['SMA_50'], data['SMA_200'])
        >>> signals = entry_exit_signals(entry, exit)
        >>> result = signals['entry']  # 진입 시그널만 반환
    """
    return pd.DataFrame(
        {"entry": entry_condition.astype(bool), "exit": exit_condition.astype(bool)}
    )


def signal_filter(signals: pd.Series, filter_condition: pd.Series) -> pd.Series:
    """
    시그널을 필터 조건으로 필터링

    Args:
        signals: 시그널 Series
        filter_condition: 필터 조건 Series

    Returns:
        pd.Series[bool]: 필터링된 시그널

    Example:
        >>> # RSI 과매도 시그널
        >>> oversold = data['RSI'] < 30
        >>>
        >>> # 거래량 필터 (평균 대비 1.5배 이상)
        >>> high_volume = data['volume'] > data['volume'].rolling(20).mean() * 1.5
        >>>
        >>> # 필터링된 시그널
        >>> filtered = signal_filter(oversold, high_volume)
    """
    return (signals & filter_condition).astype(bool)


# ============================================================================
# M2.1: Advanced Technical Indicators
# ============================================================================


def MACD(
    series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.DataFrame:
    """
    Moving Average Convergence Divergence

    Args:
        series: 입력 시리즈 (보통 close)
        fast: Fast EMA 기간 (기본 12)
        slow: Slow EMA 기간 (기본 26)
        signal: Signal line 기간 (기본 9)

    Returns:
        pd.DataFrame: macd, signal, histogram 컬럼
    """
    fast_ema = EMA(series, fast)
    slow_ema = EMA(series, slow)
    macd_line = fast_ema - slow_ema
    signal_line = EMA(macd_line, signal)
    histogram = macd_line - signal_line

    return pd.DataFrame(
        {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram,
        }
    )


def stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k_period: int = 14,
    d_period: int = 3,
) -> pd.DataFrame:
    """
    Stochastic Oscillator

    Args:
        high: 고가 시리즈
        low: 저가 시리즈
        close: 종가 시리즈
        k_period: %K 기간 (기본 14)
        d_period: %D 기간 (기본 3)

    Returns:
        pd.DataFrame: k, d 컬럼
    """
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()

    k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    d = k.rolling(window=d_period).mean()

    return pd.DataFrame({"k": k, "d": d})


def ichimoku(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    tenkan_period: int = 9,
    kijun_period: int = 26,
    senkou_b_period: int = 52,
) -> pd.DataFrame:
    """
    Ichimoku Cloud

    Args:
        high: 고가 시리즈
        low: 저가 시리즈
        close: 종가 시리즈
        tenkan_period: Tenkan-sen 기간 (기본 9)
        kijun_period: Kijun-sen 기간 (기본 26)
        senkou_b_period: Senkou Span B 기간 (기본 52)

    Returns:
        pd.DataFrame: tenkan, kijun, senkou_a, senkou_b, chikou 컬럼
    """
    # Tenkan-sen (Conversion Line)
    tenkan = (highest(high, tenkan_period) + lowest(low, tenkan_period)) / 2

    # Kijun-sen (Base Line)
    kijun = (highest(high, kijun_period) + lowest(low, kijun_period)) / 2

    # Senkou Span A (Leading Span A)
    senkou_a = ((tenkan + kijun) / 2).shift(kijun_period)

    # Senkou Span B (Leading Span B)
    senkou_b = (
        (highest(high, senkou_b_period) + lowest(low, senkou_b_period)) / 2
    ).shift(kijun_period)

    # Chikou Span (Lagging Span)
    chikou = close.shift(-kijun_period)

    return pd.DataFrame(
        {
            "tenkan": tenkan,
            "kijun": kijun,
            "senkou_a": senkou_a,
            "senkou_b": senkou_b,
            "chikou": chikou,
        }
    )


def pivot_points(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.DataFrame:
    """
    Classic Pivot Points

    Args:
        high: 전일 고가
        low: 전일 저가
        close: 전일 종가

    Returns:
        pd.DataFrame: pivot, r1, r2, r3, s1, s2, s3 컬럼
    """
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    r3 = high + 2 * (pivot - low)
    s3 = low - 2 * (high - pivot)

    return pd.DataFrame(
        {
            "pivot": pivot,
            "r1": r1,
            "r2": r2,
            "r3": r3,
            "s1": s1,
            "s2": s2,
            "s3": s3,
        }
    )


def fibonacci_retracement(high: float, low: float) -> dict[str, float]:
    """
    Fibonacci Retracement Levels

    Args:
        high: 구간 최고가
        low: 구간 최저가

    Returns:
        dict: 피보나치 레벨 (0%, 23.6%, 38.2%, 50%, 61.8%, 100%)
    """
    diff = high - low
    return {
        "0%": low,
        "23.6%": low + diff * 0.236,
        "38.2%": low + diff * 0.382,
        "50%": low + diff * 0.5,
        "61.8%": low + diff * 0.618,
        "100%": high,
    }


def vwap(close: pd.Series, volume: pd.Series, window: int | None = None) -> pd.Series:
    """
    Volume Weighted Average Price

    Args:
        close: 종가 시리즈
        volume: 거래량 시리즈
        window: 기간 (None이면 누적)

    Returns:
        pd.Series: VWAP 값
    """
    typical_price = close
    pv = typical_price * volume

    if window is None:
        return pv.cumsum() / volume.cumsum()
    else:
        return pv.rolling(window).sum() / volume.rolling(window).sum()


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    On-Balance Volume

    Args:
        close: 종가 시리즈
        volume: 거래량 시리즈

    Returns:
        pd.Series: OBV 값
    """
    direction = np.sign(close.diff())
    direction[direction == 0] = 1  # 변화 없으면 양수로 처리
    result = (direction * volume).cumsum()
    return pd.Series(result, index=close.index)


# ============================================================================
# M2.4: Enhanced Technical Indicators (Extended)
# ============================================================================


def cci(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20
) -> pd.Series:
    """
    Commodity Channel Index

    Args:
        high: 고가
        low: 저가
        close: 종가
        period: 기간 (기본 20)

    Returns:
        pd.Series: CCI 값
    """
    tp = (high + low + close) / 3
    sma_tp = tp.rolling(window=period).mean()
    mean_dev = tp.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
    return (tp - sma_tp) / (0.015 * mean_dev)


def donchian_channels(
    high: pd.Series, low: pd.Series, period: int = 20
) -> pd.DataFrame:
    """
    Donchian Channels

    Args:
        high: 고가
        low: 저가
        period: 기간 (기본 20)

    Returns:
        pd.DataFrame: upper, middle, lower
    """
    upper = high.rolling(window=period).max()
    lower = low.rolling(window=period).min()
    middle = (upper + lower) / 2
    return pd.DataFrame({"upper": upper, "middle": middle, "lower": lower})


def keltner_channels(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    ema_period: int = 20,
    atr_period: int = 10,
    multiplier: float = 2.0,
) -> pd.DataFrame:
    """
    Keltner Channels

    Args:
        high: 고가
        low: 저가
        close: 종가
        ema_period: EMA 기간 (기본 20)
        atr_period: ATR 기간 (기본 10)
        multiplier: ATR 배수 (기본 2.0)

    Returns:
        pd.DataFrame: upper, middle, lower
    """
    middle = EMA(close, ema_period)
    atr_val = atr(high, low, close, atr_period)
    upper = middle + (atr_val * multiplier)
    lower = middle - (atr_val * multiplier)
    return pd.DataFrame({"upper": upper, "middle": middle, "lower": lower})


def adx(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.DataFrame:
    """
    Average Directional Index

    Args:
        high: 고가
        low: 저가
        close: 종가
        period: 기간 (기본 14)

    Returns:
        pd.DataFrame: adx, plus_di, minus_di
    """
    # True Range
    tr = pd.DataFrame(
        {
            "hl": high - low,
            "hc": abs(high - close.shift(1)),
            "lc": abs(low - close.shift(1)),
        }
    ).max(axis=1)

    # Directional Movement
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    # Wilder's Smoothing (RMA)
    def rma(series: pd.Series, window: int) -> pd.Series:
        return series.ewm(alpha=1 / window, adjust=False).mean()

    tr_smooth = rma(tr, period)
    plus_dm_smooth = rma(pd.Series(plus_dm, index=high.index), period)
    minus_dm_smooth = rma(pd.Series(minus_dm, index=high.index), period)

    # Avoid division by zero
    tr_smooth = tr_smooth.replace(0, np.nan)

    plus_di = 100 * (plus_dm_smooth / tr_smooth)
    minus_di = 100 * (minus_dm_smooth / tr_smooth)

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx_val = rma(dx, period)

    return pd.DataFrame({"adx": adx_val, "plus_di": plus_di, "minus_di": minus_di})


def parabolic_sar(
    high: pd.Series,
    low: pd.Series,
    acceleration: float = 0.02,
    maximum: float = 0.2,
) -> pd.Series:
    """
    Parabolic SAR

    Args:
        high: 고가
        low: 저가
        acceleration: 가속도 (기본 0.02)
        maximum: 최대 가속도 (기본 0.2)

    Returns:
        pd.Series: PSAR 값
    """
    # 초기화
    psar_vals = np.zeros(len(high))
    bull = True
    af = acceleration
    ep = low.iloc[0]
    psar_vals[0] = low.iloc[0]  # 초기값

    high_arr = high.values
    low_arr = low.values

    for i in range(1, len(high)):
        prev_psar = psar_vals[i - 1]

        # PSAR 계산
        if bull:
            psar_vals[i] = prev_psar + af * (ep - prev_psar)
            # PSAR는 이전 두 기간의 저가보다 높을 수 없음
            if i > 1:
                psar_vals[i] = min(psar_vals[i], low_arr[i - 1], low_arr[i - 2])
            else:
                psar_vals[i] = min(psar_vals[i], low_arr[i - 1])
        else:
            psar_vals[i] = prev_psar + af * (ep - prev_psar)
            # PSAR는 이전 두 기간의 고가보다 낮을 수 없음
            if i > 1:
                psar_vals[i] = max(psar_vals[i], high_arr[i - 1], high_arr[i - 2])
            else:
                psar_vals[i] = max(psar_vals[i], high_arr[i - 1])

        # 추세 반전 체크
        reverse = False
        if bull:
            if low_arr[i] < psar_vals[i]:
                bull = False
                reverse = True
                psar_vals[i] = ep
                ep = low_arr[i]
                af = acceleration
        else:
            if high_arr[i] > psar_vals[i]:
                bull = True
                reverse = True
                psar_vals[i] = ep
                ep = high_arr[i]
                af = acceleration

        if not reverse:
            if bull:
                if high_arr[i] > ep:
                    ep = high_arr[i]
                    af = min(af + acceleration, maximum)
            else:
                if low_arr[i] < ep:
                    ep = low_arr[i]
                    af = min(af + acceleration, maximum)

    return pd.Series(psar_vals, index=high.index)


def stochrsi(
    close: pd.Series,
    rsi_period: int = 14,
    stoch_period: int = 14,
    k_smooth: int = 3,
    d_smooth: int = 3,
) -> pd.DataFrame:
    """
    Stochastic RSI

    Args:
        close: 종가
        rsi_period: RSI 기간
        stoch_period: Stochastic 기간
        k_smooth: %K 스무딩
        d_smooth: %D 스무딩

    Returns:
        pd.DataFrame: k, d
    """
    rsi_val = RSI(close, rsi_period)
    min_rsi = rsi_val.rolling(window=stoch_period).min()
    max_rsi = rsi_val.rolling(window=stoch_period).max()

    # 0으로 나누기 방지
    denom = max_rsi - min_rsi
    denom = denom.replace(0, np.nan)

    stoch_rsi = (rsi_val - min_rsi) / denom
    k = stoch_rsi.rolling(window=k_smooth).mean() * 100
    d = k.rolling(window=d_smooth).mean()

    return pd.DataFrame({"k": k, "d": d})


def supertrend(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    atr_period: int = 10,
    multiplier: float = 3.0,
) -> pd.Series:
    """
    Supertrend

    Args:
        high: 고가
        low: 저가
        close: 종가
        atr_period: ATR 기간
        multiplier: ATR 배수

    Returns:
        pd.Series: Supertrend 라인
    """
    atr_val = atr(high, low, close, atr_period)
    hl2 = (high + low) / 2
    basic_upper = hl2 + (multiplier * atr_val)
    basic_lower = hl2 - (multiplier * atr_val)

    close_arr = close.values
    bu_arr = basic_upper.values
    bl_arr = basic_lower.values

    final_upper = np.zeros(len(close))
    final_lower = np.zeros(len(close))
    supertrend_val = np.zeros(len(close))

    # 초기화
    final_upper[0] = bu_arr[0] if not np.isnan(bu_arr[0]) else 0
    final_lower[0] = bl_arr[0] if not np.isnan(bl_arr[0]) else 0

    # Trend: 1 = Up, -1 = Down
    trend = np.ones(len(close))

    for i in range(1, len(close)):
        # Final Upper
        if (bu_arr[i] < final_upper[i - 1]) or (close_arr[i - 1] > final_upper[i - 1]):
            final_upper[i] = bu_arr[i]
        else:
            final_upper[i] = final_upper[i - 1]

        # Final Lower
        if (bl_arr[i] > final_lower[i - 1]) or (close_arr[i - 1] < final_lower[i - 1]):
            final_lower[i] = bl_arr[i]
        else:
            final_lower[i] = final_lower[i - 1]

        # Trend Update
        if trend[i - 1] == 1:
            if close_arr[i] < final_lower[i - 1]:
                trend[i] = -1
                supertrend_val[i] = final_upper[i]
            else:
                trend[i] = 1
                supertrend_val[i] = final_lower[i]
        else:
            if close_arr[i] > final_upper[i - 1]:
                trend[i] = 1
                supertrend_val[i] = final_lower[i]
            else:
                trend[i] = -1
                supertrend_val[i] = final_upper[i]

    return pd.Series(supertrend_val, index=close.index)


def tema(series: pd.Series, period: int = 20) -> pd.Series:
    """
    Triple Exponential Moving Average

    Args:
        series: 입력 시리즈
        period: 기간

    Returns:
        pd.Series: TEMA 값
    """
    ema1 = EMA(series, period)
    ema2 = EMA(ema1, period)
    ema3 = EMA(ema2, period)
    return 3 * ema1 - 3 * ema2 + ema3


def williams_r(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.Series:
    """
    Williams %R

    Args:
        high: 고가
        low: 저가
        close: 종가
        period: 기간

    Returns:
        pd.Series: %R 값 (-100 ~ 0)
    """
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()

    # 0으로 나누기 방지
    denom = highest_high - lowest_low
    denom = denom.replace(0, np.nan)

    return -100 * (highest_high - close) / denom


# ============================================================================
# M2.2: Strategy Primitives
# ============================================================================


def position_sizing_fixed(
    capital: float, risk_percent: float, stop_loss_pct: float
) -> float:
    """
    Fixed Fractional Position Sizing

    Args:
        capital: 총 자본
        risk_percent: 리스크 비율 (0.02 = 2%)
        stop_loss_pct: 손절 비율 (0.05 = 5%)

    Returns:
        float: 포지션 크기 (금액)
    """
    risk_amount = capital * risk_percent
    position_size = risk_amount / stop_loss_pct
    return position_size


def position_sizing_kelly(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """
    Kelly Criterion Position Sizing

    Args:
        win_rate: 승률 (0.6 = 60%)
        avg_win: 평균 수익
        avg_loss: 평균 손실

    Returns:
        float: Kelly 비율 (0.2 = 자본의 20%)
    """
    if avg_loss == 0:
        return 0.0

    win_loss_ratio = avg_win / avg_loss
    kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

    # Kelly의 1/2 또는 1/4 사용 권장 (위험 감소)
    return max(0.0, kelly * 0.5)


def stop_loss(entry_price: float, atr_value: float, multiplier: float = 2.0) -> float:
    """
    ATR-based Stop Loss

    Args:
        entry_price: 진입 가격
        atr_value: ATR 값
        multiplier: ATR 배수 (기본 2.0)

    Returns:
        float: 손절가
    """
    return entry_price - (atr_value * multiplier)


def take_profit(entry_price: float, atr_value: float, multiplier: float = 3.0) -> float:
    """
    ATR-based Take Profit

    Args:
        entry_price: 진입 가격
        atr_value: ATR 값
        multiplier: ATR 배수 (기본 3.0)

    Returns:
        float: 익절가
    """
    return entry_price + (atr_value * multiplier)


def trailing_stop(
    current_price: pd.Series, atr: pd.Series, multiplier: float = 2.0
) -> pd.Series:
    """
    Trailing Stop Loss

    Args:
        current_price: 현재 가격 시리즈
        atr: ATR 시리즈
        multiplier: ATR 배수

    Returns:
        pd.Series: 트레일링 스톱 레벨
    """
    stop = current_price - (atr * multiplier)
    return stop.expanding().max()


def combine_signals(
    *signals: pd.Series, mode: Literal["and", "or"] = "and"
) -> pd.Series:
    """
    Combine multiple signals

    Args:
        *signals: 시그널 시리즈들
        mode: 결합 방식 ("and" 또는 "or")

    Returns:
        pd.Series[bool]: 결합된 시그널
    """
    if not signals:
        raise ValueError("At least one signal required")

    result = signals[0].astype(bool)
    for sig in signals[1:]:
        if mode == "and":
            result = result & sig.astype(bool)
        else:  # or
            result = result | sig.astype(bool)

    return result


# ============================================================================
# M2.3: Utility Functions
# ============================================================================


def check_missing_data(data: pd.DataFrame, threshold: float = 0.05) -> dict[str, float]:
    """
    Check for missing data in DataFrame

    Args:
        data: OHLCV DataFrame
        threshold: 허용 결측치 비율 (기본 0.05 = 5%)

    Returns:
        dict: 컬럼별 결측치 비율
    """
    missing_pct = data.isnull().sum() / len(data)
    issues = {
        str(col): float(pct) for col, pct in missing_pct.items() if pct > threshold
    }
    return issues


def detect_outliers(series: pd.Series, n_std: float = 3.0) -> pd.Series:
    """
    Detect outliers using standard deviation

    Args:
        series: 입력 시리즈
        n_std: 표준편차 배수 (기본 3.0)

    Returns:
        pd.Series[bool]: 이상치 위치 (True = 이상치)
    """
    mean = series.mean()
    std = series.std()
    lower = mean - (n_std * std)
    upper = mean + (n_std * std)
    return (series < lower) | (series > upper)


def normalize(
    series: pd.Series, method: Literal["minmax", "zscore"] = "minmax"
) -> pd.Series:
    """
    Normalize series

    Args:
        series: 입력 시리즈
        method: 정규화 방식 ("minmax" 또는 "zscore")

    Returns:
        pd.Series: 정규화된 시리즈
    """
    if method == "minmax":
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series(0.5, index=series.index)
        return (series - min_val) / (max_val - min_val)
    else:  # zscore
        return (series - series.mean()) / series.std()


def correlation_matrix(
    data: pd.DataFrame, columns: list[str] | None = None
) -> pd.DataFrame:
    """
    Calculate correlation matrix

    Args:
        data: 입력 DataFrame
        columns: 계산할 컬럼 리스트 (None이면 전체)

    Returns:
        pd.DataFrame: 상관계수 행렬
    """
    if columns is None:
        return data.corr()
    return data[columns].corr()


def get_stdlib_functions() -> dict[str, Callable[..., Any]]:
    """
    표준 라이브러리 함수 딕셔너리 반환

    Returns:
        dict: 함수명 -> 함수 매핑
    """
    return {
        # Moving Averages (대소문자 별칭 지원)
        "SMA": SMA,
        "sma": SMA,
        "EMA": EMA,
        "ema": EMA,
        "WMA": WMA,
        "wma": WMA,
        "TEMA": tema,
        "tema": tema,
        # Technical Indicators (Basic) (대소문자 별칭 지원)
        "RSI": RSI,
        "rsi": RSI,
        "MACD": MACD,
        "macd": MACD,
        "stochastic": stochastic,
        "ichimoku": ichimoku,
        "CCI": cci,
        "cci": cci,
        "ADX": adx,
        "adx": adx,
        "stochrsi": stochrsi,
        "williams_r": williams_r,
        # Channels
        "bbands": bbands,
        "donchian_channels": donchian_channels,
        "keltner_channels": keltner_channels,
        "supertrend": supertrend,
        "parabolic_sar": parabolic_sar,
        # Crossover Signals
        "crossover": crossover,
        "crossunder": crossunder,
        # High/Low
        "highest": highest,
        "lowest": lowest,
        # Change Metrics
        "change": change,
        "pct_change": pct_change,
        # Volatility
        "stdev": stdev,
        "atr": atr,
        "ATR": atr,
        # Support/Resistance
        "pivot_points": pivot_points,
        "fibonacci_retracement": fibonacci_retracement,
        # Volume Indicators
        "vwap": vwap,
        "VWAP": vwap,
        "obv": obv,
        "OBV": obv,
        # Strategy Functions
        "generate_signal": generate_signal,
        "entry_exit_signals": entry_exit_signals,
        "signal_filter": signal_filter,
        "combine_signals": combine_signals,
        # Position Sizing
        "position_sizing_fixed": position_sizing_fixed,
        "position_sizing_kelly": position_sizing_kelly,
        # Risk Management
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "trailing_stop": trailing_stop,
        # Utilities
        "check_missing_data": check_missing_data,
        "detect_outliers": detect_outliers,
        "normalize": normalize,
        "correlation_matrix": correlation_matrix,
    }

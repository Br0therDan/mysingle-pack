"""DSL 표준 라이브러리 - 공통 함수"""

from typing import Any, Callable, Literal

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


def get_stdlib_functions() -> dict[str, Callable[..., Any]]:
    """
    표준 라이브러리 함수 딕셔너리 반환

    Returns:
        dict: 함수명 -> 함수 매핑
    """
    return {
        # 이동평균
        "SMA": SMA,
        "EMA": EMA,
        "WMA": WMA,
        # 기술적 지표
        "RSI": RSI,
        # 크로스오버
        "crossover": crossover,
        "crossunder": crossunder,
        # 최고/최저
        "highest": highest,
        "lowest": lowest,
        # 변화율
        "change": change,
        "pct_change": pct_change,
        # 변동성
        "stdev": stdev,
        "bbands": bbands,
        "atr": atr,
        # 전략 특화 함수
        "generate_signal": generate_signal,
        "entry_exit_signals": entry_exit_signals,
        "signal_filter": signal_filter,
    }

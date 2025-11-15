"""DSL 표준 라이브러리 - 공통 함수"""

from typing import Any, Callable

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
    }

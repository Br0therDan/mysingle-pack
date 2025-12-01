"""DSL 전략 특화 stdlib 함수 테스트"""

import pandas as pd
import pytest

from mysingle.dsl import DSLExecutor, DSLParser


@pytest.fixture
def executor():
    """DSL Executor 인스턴스"""
    parser = DSLParser()
    return DSLExecutor(parser)


@pytest.fixture
def sample_data():
    """샘플 데이터"""
    return pd.DataFrame(
        {
            "close": [100, 101, 102, 103, 104],
            "RSI_14": [35, 28, 25, 32, 45],
            "SMA_50": [100, 100, 101, 102, 103],
            "SMA_200": [101, 101, 101, 101, 101],
            "volume": [1000, 1500, 2000, 1800, 1200],
        }
    )


def test_generate_signal_long(executor, sample_data):
    """generate_signal() long 시그널 테스트"""
    code = """
oversold = data['RSI_14'] < 30
buy_signal = generate_signal(oversold, signal_type="long")
result = buy_signal
"""
    compiled = executor.parser.parse(code)
    result = executor.execute(compiled, sample_data, params={})

    assert isinstance(result, pd.Series)
    assert result.dtype == bool
    # RSI_14: [35, 28, 25, 32, 45]
    assert not result.iloc[0]  # 35 < 30 = False
    assert result.iloc[1]  # 28 < 30 = True
    assert result.iloc[2]  # 25 < 30 = True


def test_generate_signal_short(executor, sample_data):
    """generate_signal() short 시그널 테스트"""
    code = """
overbought = data['RSI_14'] > 40
sell_signal = generate_signal(overbought, signal_type="short")
result = sell_signal
"""
    compiled = executor.parser.parse(code)
    result = executor.execute(compiled, sample_data, params={})

    assert isinstance(result, pd.Series)
    assert result.dtype == bool
    # RSI_14: [35, 28, 25, 32, 45]
    assert result.iloc[4]  # 45 > 40 = True


def test_entry_exit_signals(executor, sample_data):
    """entry_exit_signals() 테스트"""
    code = """
fast_ma = data['SMA_50']
slow_ma = data['SMA_200']

entry = crossover(fast_ma, slow_ma)
exit = crossunder(fast_ma, slow_ma)

signals = entry_exit_signals(entry, exit)
result = signals['entry']  # 진입 시그널만 반환
"""
    compiled = executor.parser.parse(code)
    result = executor.execute(compiled, sample_data, params={})

    assert isinstance(result, pd.Series)
    assert result.dtype == bool


def test_entry_exit_signals_dataframe(executor, sample_data):
    """entry_exit_signals()가 DataFrame을 반환하는지 테스트"""
    code = """
fast_ma = data['SMA_50']
slow_ma = data['SMA_200']

entry = crossover(fast_ma, slow_ma)
exit = crossunder(fast_ma, slow_ma)

result = entry_exit_signals(entry, exit)
"""
    compiled = executor.parser.parse(code)
    result = executor.execute(compiled, sample_data, params={})

    assert isinstance(result, pd.DataFrame)
    assert "entry" in result.columns
    assert "exit" in result.columns
    assert result["entry"].dtype == bool
    assert result["exit"].dtype == bool


def test_signal_filter(executor, sample_data):
    """signal_filter() 테스트"""
    code = """
# RSI 과매도 시그널
oversold = data['RSI_14'] < 30

# 거래량 필터 (평균 대비 1.5배 이상)
avg_volume = data['volume'].rolling(3).mean()
high_volume = data['volume'] > avg_volume * 1.5

# 필터링된 시그널
result = signal_filter(oversold, high_volume)
"""
    compiled = executor.parser.parse(code)
    result = executor.execute(compiled, sample_data, params={})

    assert isinstance(result, pd.Series)
    assert result.dtype == bool


def test_signal_filter_complex(executor, sample_data):
    """signal_filter() 복잡한 필터 테스트"""
    code = """
# 여러 조건 결합
rsi_oversold = data['RSI_14'] < 30
price_above_ma = data['close'] > data['SMA_50']
volume_spike = data['volume'] > 1500

# 조건 1: RSI 과매도
signal = rsi_oversold

# 필터 1: 가격이 50일선 위
signal = signal_filter(signal, price_above_ma)

# 필터 2: 거래량 급증
result = signal_filter(signal, volume_spike)
"""
    compiled = executor.parser.parse(code)
    result = executor.execute(compiled, sample_data, params={})

    assert isinstance(result, pd.Series)
    assert result.dtype == bool


def test_combined_strategy_functions(executor, sample_data):
    """전략 함수들을 조합한 테스트"""
    code = """
# 1. 기본 시그널 생성
rsi = data['RSI_14']
oversold = rsi < params.get('rsi_threshold', 30)
buy_signal = generate_signal(oversold, signal_type="long")

# 2. 거래량 필터 적용
avg_volume = data['volume'].rolling(3).mean()
high_volume = data['volume'] > avg_volume * 1.2
filtered_signal = signal_filter(buy_signal, high_volume)

# 3. 청산 조건
overbought = rsi > params.get('rsi_exit', 70)
exit_signal = generate_signal(overbought, signal_type="short")

# 4. 진입/청산 페어
signals = entry_exit_signals(filtered_signal, exit_signal)

# 최종 결과: 진입 시그널
result = signals['entry']
"""
    compiled = executor.parser.parse(code)
    result = executor.execute(
        compiled, sample_data, params={"rsi_threshold": 30, "rsi_exit": 70}
    )

    assert isinstance(result, pd.Series)
    assert result.dtype == bool

"""DSL params 네임스페이스 테스트"""

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
        }
    )


def test_params_dict_access(executor, sample_data):
    """params 딕셔너리 직접 접근 테스트"""
    code = """
threshold = params['threshold']
window = params['window']
result = data['RSI_14'] < threshold
"""
    compiled = executor.parser.parse(code)
    result = executor.execute(
        compiled, sample_data, params={"threshold": 30, "window": 14}
    )

    assert isinstance(result, pd.Series)
    assert result.dtype == bool
    # RSI_14 값: [35, 28, 25, 32, 45]
    # threshold = 30
    assert not result.iloc[0]  # 35 < 30 = False
    assert result.iloc[1]  # 28 < 30 = True
    assert result.iloc[2]  # 25 < 30 = True
    assert not result.iloc[3]  # 32 < 30 = False


def test_params_get_with_default(executor, sample_data):
    """params.get() 기본값 테스트"""
    code = """
threshold = params.get('threshold', 30)
window = params.get('window', 14)
result = data['RSI_14'] < threshold
"""
    compiled = executor.parser.parse(code)

    # params 비어있음 - 기본값 사용
    result = executor.execute(compiled, sample_data, params={})

    assert isinstance(result, pd.Series)
    assert result.dtype == bool
    # 기본값 threshold=30 사용
    assert result.iloc[1]  # 28 < 30 = True
    assert result.iloc[2]  # 25 < 30 = True


def test_params_get_with_provided_value(executor, sample_data):
    """params.get() 제공된 값 테스트"""
    code = """
threshold = params.get('threshold', 30)
result = data['RSI_14'] < threshold
"""
    compiled = executor.parser.parse(code)

    # params에 값 제공 - 기본값 무시
    result = executor.execute(compiled, sample_data, params={"threshold": 26})

    assert isinstance(result, pd.Series)
    # threshold=26 사용
    assert not result.iloc[0]  # 35 < 26 = False
    assert not result.iloc[1]  # 28 < 26 = False
    assert result.iloc[2]  # 25 < 26 = True
    assert not result.iloc[3]  # 32 < 26 = False


def test_params_in_complex_strategy(executor, sample_data):
    """복잡한 전략에서 params 사용 테스트"""
    code = """
# RSI 과매도 + Golden Cross
rsi = data['RSI_14']
fast_ma = data['SMA_50']
slow_ma = data['SMA_200']

# params에서 threshold 가져오기
rsi_threshold = params.get('rsi_threshold', 30)

oversold = rsi < rsi_threshold
golden = crossover(fast_ma, slow_ma)

result = oversold & golden
"""
    compiled = executor.parser.parse(code)
    result = executor.execute(compiled, sample_data, params={"rsi_threshold": 35})

    assert isinstance(result, pd.Series)
    assert result.dtype == bool


def test_params_backward_compatibility(executor, sample_data):
    """기존 방식(개별 변수)도 여전히 작동하는지 테스트"""
    code = """
# 기존 방식: params가 개별 변수로 주입됨
result = data['RSI_14'] < threshold
"""
    compiled = executor.parser.parse(code)

    # params의 값이 개별 변수로 주입됨
    result = executor.execute(compiled, sample_data, params={"threshold": 30})

    assert isinstance(result, pd.Series)
    assert result.dtype == bool
    assert result.iloc[1]  # 28 < 30 = True


def test_params_validation(executor, sample_data):
    """params 검증 테스트"""
    code = """
threshold = params.get('threshold')
if threshold is None:
    raise ValueError("threshold is required")
if not isinstance(threshold, (int, float)):
    raise TypeError("threshold must be numeric")
if threshold < 0 or threshold > 100:
    raise ValueError("threshold must be between 0 and 100")

result = data['RSI_14'] < threshold
"""
    compiled = executor.parser.parse(code)

    # 유효한 params
    result = executor.execute(compiled, sample_data, params={"threshold": 30})
    assert isinstance(result, pd.Series)

    # threshold 누락
    with pytest.raises(Exception) as exc_info:
        executor.execute(compiled, sample_data, params={})
    assert "threshold is required" in str(exc_info.value)

    # threshold 범위 초과
    with pytest.raises(Exception) as exc_info:
        executor.execute(compiled, sample_data, params={"threshold": 150})
    assert "must be between 0 and 100" in str(exc_info.value)

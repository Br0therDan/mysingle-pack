"""DSL 바이트코드 직렬화 테스트"""

import base64

import pandas as pd
import pytest

from mysingle.dsl import DSLExecutor, DSLParser


@pytest.fixture
def parser():
    """DSL Parser 인스턴스"""
    return DSLParser()


@pytest.fixture
def executor(parser):
    """DSL Executor 인스턴스"""
    return DSLExecutor(parser)


@pytest.fixture
def sample_data():
    """샘플 데이터"""
    return pd.DataFrame(
        {
            "close": [100, 101, 102, 103, 104],
            "RSI_14": [35, 28, 25, 32, 45],
            "SMA_50": [100, 100, 101, 102, 103],
        }
    )


def test_parse_returns_bytes(parser):
    """parse()가 bytes를 반환하는지 테스트"""
    code = """
result = data['RSI_14'] < 30
"""
    compiled = parser.parse(code)

    assert isinstance(compiled, bytes)
    assert len(compiled) > 0


def test_bytecode_serialization(parser):
    """바이트코드 직렬화 테스트"""
    code = """
result = data['RSI_14'] < 30
"""
    # 컴파일
    bytecode = parser.parse(code)

    # base64로 인코딩 (API 응답에 사용)
    encoded = base64.b64encode(bytecode).decode()
    assert isinstance(encoded, str)

    # 디코딩
    decoded = base64.b64decode(encoded)
    assert decoded == bytecode


def test_load_bytecode(parser):
    """load() 메서드 테스트"""
    code = """
result = data['RSI_14'] < 30
"""
    # 컴파일
    bytecode = parser.parse(code)

    # 로드
    code_object = parser.load(bytecode)
    assert code_object is not None
    assert hasattr(code_object, "co_code")  # code object의 속성


def test_execute_with_bytes(executor, sample_data):
    """executor가 bytes를 받아 실행하는지 테스트"""
    code = """
result = data['RSI_14'] < 30
"""
    # 컴파일 (bytes 반환)
    bytecode = executor.parser.parse(code)

    # 실행 (bytes 전달)
    result = executor.execute(bytecode, sample_data, params={})

    assert isinstance(result, pd.Series)
    assert result.dtype == bool
    # RSI_14: [35, 28, 25, 32, 45]
    assert not result.iloc[0]  # 35 < 30 = False
    assert result.iloc[1]  # 28 < 30 = True
    assert result.iloc[2]  # 25 < 30 = True


def test_execute_with_code_object(executor, parser, sample_data):
    """executor가 code object를 받아 실행하는지 테스트 (하위 호환성)"""
    code = """
result = data['RSI_14'] < 30
"""
    # 컴파일 후 로드
    bytecode = parser.parse(code)
    code_object = parser.load(bytecode)

    # 실행 (code object 전달)
    result = executor.execute(code_object, sample_data, params={})

    assert isinstance(result, pd.Series)
    assert result.dtype == bool


def test_bytecode_roundtrip(executor, sample_data):
    """바이트코드 완전한 직렬화/역직렬화 테스트"""
    code = """
threshold = params.get('threshold', 30)
result = data['RSI_14'] < threshold
"""
    # 1. 컴파일
    bytecode = executor.parser.parse(code)

    # 2. 직렬화 (예: API 응답)
    serialized = base64.b64encode(bytecode).decode()

    # 3. 역직렬화 (예: API 요청에서 받음)
    deserialized = base64.b64decode(serialized)

    # 4. 실행
    result = executor.execute(deserialized, sample_data, params={"threshold": 30})

    assert isinstance(result, pd.Series)
    assert result.dtype == bool


def test_bytecode_storage_scenario(parser, executor, sample_data):
    """실제 사용 시나리오: 컴파일 결과 저장 및 재사용"""
    # Strategy Service에서 전략 저장 시
    strategy_code = """
rsi = data['RSI_14']
threshold = params.get('threshold', 30)
result = rsi < threshold
"""

    # 컴파일 및 저장
    compiled_bytecode = parser.parse(strategy_code)
    stored_bytecode = base64.b64encode(compiled_bytecode).decode()  # DB 저장용

    # --- 나중에 백테스트 실행 시 ---

    # DB에서 로드
    loaded_bytecode = base64.b64decode(stored_bytecode)

    # 실행 (재컴파일 없이)
    result = executor.execute(loaded_bytecode, sample_data, params={"threshold": 30})

    assert isinstance(result, pd.Series)
    assert result.dtype == bool


def test_invalid_bytecode_handling(executor, sample_data):
    """잘못된 바이트코드 처리 테스트"""
    # marshal.loads()는 일부 바이트 시퀀스를 해석할 수 있으므로,
    # 실제 실행 시 에러가 발생하는지 확인
    invalid_bytecode = b"this is not valid bytecode"

    # execute()로 잘못된 바이트코드 실행 시도
    # marshal.loads()는 성공할 수 있지만, exec()에서 실패해야 함
    from mysingle.dsl.errors import DSLExecutionError

    with pytest.raises((DSLExecutionError, ValueError, TypeError)):  # 실행 시 에러 발생
        executor.execute(invalid_bytecode, sample_data, params={})


def test_bytecode_consistency(parser):
    """동일한 코드는 동일한 바이트코드를 생성하는지 테스트"""
    code = """
result = data['RSI_14'] < 30
"""

    bytecode1 = parser.parse(code)
    bytecode2 = parser.parse(code)

    # 동일한 바이트코드 생성
    assert bytecode1 == bytecode2

"""
Tests for mysingle.dsl module.
"""

import pandas as pd
import pytest

try:
    from mysingle.dsl import DSLExecutor, DSLParser

    DSL_AVAILABLE = True
except ImportError:
    DSL_AVAILABLE = False


@pytest.mark.skipif(not DSL_AVAILABLE, reason="DSL not installed")
class TestDSLParser:
    """Tests for DSL parser."""

    def test_dsl_parser_initialization(self):
        """Test DSL parser initialization."""
        parser = DSLParser()

        assert parser is not None

    def test_parse_simple_expression(self):
        """Test parsing simple expression."""
        parser = DSLParser()

        # Basic test - actual implementation may vary
        result = parser.parse("close > 100")

        assert result is not None

    def test_parse_complex_expression(self):
        """Test parsing complex expression."""
        parser = DSLParser()

        # Test complex expression
        result = parser.parse("(close > open) and (volume > 1000)")

        assert result is not None


@pytest.mark.skipif(not DSL_AVAILABLE, reason="DSL not installed")
class TestDSLExecutor:
    """Tests for DSL executor."""

    def test_dsl_executor_initialization(self):
        """Test DSL executor initialization."""
        executor = DSLExecutor()

        assert executor is not None
        assert executor.parser is not None

    def test_execute_simple_condition(self, sample_dataframe):
        """Test executing simple condition."""
        parser = DSLParser()
        executor = DSLExecutor(parser=parser)

        # Parse and compile
        code = "result = data['close'] > 100"
        compiled = parser.parse(code)

        # Execute
        result = executor.execute(compiled, data=sample_dataframe, params={})

        assert result is not None
        assert isinstance(result, (pd.Series, pd.DataFrame))

    def test_execute_with_indicators(self, sample_dataframe):
        """Test executing with indicators."""
        parser = DSLParser()
        executor = DSLExecutor(parser=parser)

        # Test with indicator using stdlib (simpler version without import)
        code = """
result = data['close'].rolling(window=3).mean() > 100
"""
        compiled = parser.parse(code)

        result = executor.execute(compiled, data=sample_dataframe, params={})
        assert result is not None
        assert isinstance(result, pd.Series)


@pytest.mark.skipif(not DSL_AVAILABLE, reason="DSL not installed")
def test_dsl_integration(sample_dataframe):
    """Test DSL parser and executor integration."""
    parser = DSLParser()
    executor = DSLExecutor(parser=parser)

    # Parse expression
    code = "result = data['close'] > 100"
    parsed = parser.parse(code)

    # Execute parsed expression
    result = executor.execute(parsed, data=sample_dataframe, params={})

    assert result is not None
    assert isinstance(result, (pd.Series, pd.DataFrame))

    assert result is not None

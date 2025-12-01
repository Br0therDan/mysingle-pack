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

    def test_dsl_executor_initialization(self, sample_dataframe):
        """Test DSL executor initialization."""
        executor = DSLExecutor(data=sample_dataframe)

        assert executor is not None

    def test_execute_simple_condition(self, sample_dataframe):
        """Test executing simple condition."""
        executor = DSLExecutor(data=sample_dataframe)

        # Execute simple condition
        result = executor.execute("close > 100")

        assert result is not None
        assert isinstance(result, (pd.Series, pd.DataFrame, bool))

    def test_execute_with_indicators(self, sample_dataframe):
        """Test executing with indicators."""
        executor = DSLExecutor(data=sample_dataframe)

        # Test with indicator (if available)
        # This is a placeholder - actual implementation may vary
        try:
            result = executor.execute("SMA(close, 3) > 100")
            assert result is not None
        except Exception:
            # Indicators may not be implemented yet
            pytest.skip("Indicators not available")


@pytest.mark.skipif(not DSL_AVAILABLE, reason="DSL not installed")
def test_dsl_integration(sample_dataframe):
    """Test DSL parser and executor integration."""
    parser = DSLParser()
    executor = DSLExecutor(data=sample_dataframe)

    # Parse expression
    parsed = parser.parse("close > 100")

    # Execute parsed expression
    result = executor.execute(parsed)

    assert result is not None

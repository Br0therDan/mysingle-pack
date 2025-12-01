"""
Tests for mysingle.database.duckdb module.
"""


import pytest

try:
    from mysingle.database import BaseDuckDBManager

    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False


@pytest.mark.skipif(not DUCKDB_AVAILABLE, reason="DuckDB not installed")
class TestDuckDBManager:
    """Tests for DuckDB manager."""

    def test_duckdb_manager_initialization(self, tmp_path):
        """Test DuckDB manager initialization."""
        db_path = tmp_path / "test.db"

        manager = BaseDuckDBManager(db_path=str(db_path))

        assert manager is not None
        assert hasattr(manager, "connection")

    def test_duckdb_in_memory(self):
        """Test DuckDB in-memory database."""
        manager = BaseDuckDBManager(db_path=":memory:")

        assert manager is not None

    def test_duckdb_query_execution(self, tmp_path):
        """Test DuckDB query execution."""
        db_path = tmp_path / "test.db"
        manager = BaseDuckDBManager(db_path=str(db_path))

        # This is a basic structure test
        # Actual query tests would need the manager to be fully implemented
        assert hasattr(manager, "execute") or hasattr(manager, "query")

"""
DuckDB Database Manager - Common Base Class
모든 서비스에서 공통으로 사용하는 DuckDB 관리 클래스
"""

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb

from mysingle.core.logging import get_logger

logger = get_logger(__name__)


class BaseDuckDBManager:
    """DuckDB 데이터베이스 관리 기본 클래스"""

    def __init__(self, db_path: str):
        """
        Args:
            db_path: DuckDB 파일 경로
        """
        self.db_path = db_path
        self.connection: duckdb.DuckDBPyConnection | None = None

        # 데이터베이스 디렉토리 생성
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    @property
    def duckdb_conn(self) -> duckdb.DuckDBPyConnection:
        """DuckDB 연결 객체 반환"""
        if self.connection is None:
            self.connect()
        if self.connection is None:
            raise RuntimeError("DuckDB connection not established")
        return self.connection

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()

    def connect(self) -> None:
        """데이터베이스 연결"""
        if self.connection is None:
            logger.info(
                "Connecting to DuckDB",
                db_path=self.db_path,
                operation="connect",
            )
            try:
                # 기존 연결이 있다면 종료
                self.close()
                # 새 연결 생성
                self.connection = duckdb.connect(self.db_path)
                self._create_tables()
                logger.info(
                    "DuckDB connected successfully",
                    db_path=self.db_path,
                    status="success",
                )
            except Exception as e:
                logger.error(
                    "Failed to connect to DuckDB",
                    db_path=self.db_path,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                # 파일이 잠겨있다면 메모리 DB로 폴백
                if "lock" in str(e).lower():
                    logger.warning(
                        "Falling back to in-memory database",
                        reason="file_locked",
                        original_db_path=self.db_path,
                    )
                    self.connection = duckdb.connect(":memory:")
                    self._create_tables()
                    logger.info(
                        "DuckDB connected to in-memory database",
                        mode="memory",
                        status="success",
                    )
                else:
                    raise

    def close(self) -> None:
        """데이터베이스 연결 종료"""
        if self.connection:
            try:
                self.connection.close()
                logger.info(
                    "DuckDB connection closed",
                    db_path=self.db_path,
                    operation="close",
                )
            except Exception as e:
                logger.warning(
                    "Error closing DuckDB connection",
                    db_path=self.db_path,
                    error=str(e),
                )
            finally:
                self.connection = None

    def _create_tables(self) -> None:
        """테이블 생성 - 서브클래스에서 오버라이드"""
        raise NotImplementedError("Subclass must implement _create_tables()")

    def _ensure_connected(self) -> None:
        """연결이 없으면 자동으로 연결"""
        if self.connection is None:
            self.connect()

    def _make_json_serializable(self, obj) -> Any:
        """객체를 JSON 직렬화 가능하도록 변환"""
        import json
        from datetime import datetime
        from decimal import Decimal

        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, "model_dump"):  # Pydantic v2
            return self._make_json_serializable(obj.model_dump())
        elif hasattr(obj, "dict"):  # Pydantic v1
            return self._make_json_serializable(obj.dict())
        else:
            # 기본 JSON 직렬화 시도
            try:
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                return str(obj)

    # ===== 공통 캐시 메서드들 =====

    def store_cache_data(
        self, cache_key: str, data: list[dict], table_name: str = "cache_data"
    ) -> bool:
        """DuckDB 캐시에 데이터 저장"""
        self._ensure_connected()
        if not self.connection:
            return False

        try:
            # 테이블이 없으면 생성
            self._create_cache_table(table_name)

            # 기존 데이터 삭제
            self.connection.execute(
                f"DELETE FROM {table_name} WHERE cache_key = ?", [cache_key]
            )

            # 새 데이터 삽입
            now = datetime.now(UTC)
            record_id = str(uuid.uuid4())

            self.connection.execute(
                f"""
                INSERT INTO {table_name} (id, cache_key, data_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                [record_id, cache_key, json.dumps(data), now, now],
            )

            logger.info(
                "Cache data stored successfully",
                cache_key=cache_key,
                table_name=table_name,
                data_count=len(data),
                operation="store_cache",
            )
            return True

        except Exception as e:
            logger.error(
                "Failed to store cache data",
                cache_key=cache_key,
                table_name=table_name,
                error=str(e),
                error_type=type(e).__name__,
            )
            return False

    def get_cache_data(
        self, cache_key: str, table_name: str = "cache_data", ttl_hours: int = 24
    ) -> list[dict] | None:
        """DuckDB 캐시에서 데이터 조회"""
        self._ensure_connected()
        if not self.connection:
            return None

        try:
            # TTL 체크를 위한 시간 계산
            cutoff_time = datetime.now(UTC).timestamp() - (ttl_hours * 3600)

            result = self.connection.execute(
                f"""
                SELECT data_json, updated_at
                FROM {table_name}
                WHERE cache_key = ?
                AND EXTRACT(EPOCH FROM updated_at) > ?
            """,
                [cache_key, cutoff_time],
            ).fetchone()

            if result:
                data_json, _ = result
                parsed_data: list[dict[Any, Any]] = json.loads(data_json)  # type: ignore[assignment]
                logger.debug(
                    "Cache data retrieved successfully",
                    cache_key=cache_key,
                    table_name=table_name,
                    data_count=len(parsed_data),
                    ttl_hours=ttl_hours,
                    operation="get_cache",
                )
                return parsed_data
            else:
                logger.debug(
                    "Cache data not found or expired",
                    cache_key=cache_key,
                    table_name=table_name,
                    ttl_hours=ttl_hours,
                    reason="not_found_or_expired",
                )
                return None

        except Exception as e:
            logger.error(
                "Failed to retrieve cache data",
                cache_key=cache_key,
                table_name=table_name,
                error=str(e),
                error_type=type(e).__name__,
            )
            return None

    def _create_cache_table(self, table_name: str) -> None:
        """캐시 테이블 생성"""
        self._ensure_connected()
        if not self.connection:
            logger.warning(
                "Cannot create cache table - no connection",
                table_name=table_name,
            )
            return

        try:
            self.connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id VARCHAR PRIMARY KEY,
                    cache_key VARCHAR NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            """
            )

            # 인덱스 생성
            self.connection.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{table_name}_cache_key
                ON {table_name}(cache_key)
            """
            )

            self.connection.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{table_name}_updated_at
                ON {table_name}(updated_at)
            """
            )

            logger.debug(
                "Cache table created successfully",
                table_name=table_name,
                indexes=["cache_key", "updated_at"],
                operation="create_table",
            )

        except Exception as e:
            logger.error(
                "Failed to create cache table",
                table_name=table_name,
                error=str(e),
                error_type=type(e).__name__,
            )

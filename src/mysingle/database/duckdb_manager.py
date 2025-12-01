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

from mysingle.core.logging import get_structured_logger

logger = get_structured_logger(__name__)


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
            logger.info(f"Connecting to DuckDB at: {self.db_path}")
            try:
                # 기존 연결이 있다면 종료
                self.close()
                # 새 연결 생성
                self.connection = duckdb.connect(self.db_path)
                self._create_tables()
                logger.info(f"✅ DuckDB connected successfully at: {self.db_path}")
            except Exception as e:
                logger.error(f"❌ Failed to connect to DuckDB: {e}")
                # 파일이 잠겨있다면 메모리 DB로 폴백
                if "lock" in str(e).lower():
                    logger.warning("🔄 Falling back to in-memory database")
                    self.connection = duckdb.connect(":memory:")
                    self._create_tables()
                    logger.info("✅ DuckDB connected to in-memory database")
                else:
                    raise

    def close(self) -> None:
        """데이터베이스 연결 종료"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("🔒 DuckDB connection closed")
            except Exception as e:
                logger.warning(f"⚠️ Error closing DuckDB connection: {e}")
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

            logger.info(f"캐시 데이터 저장 완료: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"캐시 데이터 저장 실패: {e}")
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
                return parsed_data
            else:
                return None

        except Exception as e:
            logger.error(f"캐시 데이터 조회 실패: {e}")
            return None

    def _create_cache_table(self, table_name: str) -> None:
        """캐시 테이블 생성"""
        self._ensure_connected()
        if not self.connection:
            return

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

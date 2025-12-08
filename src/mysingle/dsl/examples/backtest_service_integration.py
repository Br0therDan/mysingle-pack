"""
Backtest DSL Service - Refactored using DSLRuntimeService

Example implementation showing how to use the unified DSL runtime
for strategy execution in Backtest Service.
"""

from typing import Any, Dict, Optional

import pandas as pd

from mysingle.core.logging import get_structured_logger
from mysingle.dsl.cache import DSLBytecodeCache, InMemoryDSLCache
from mysingle.dsl.limits import ResourceLimits
from mysingle.dsl.runtime_service import (
    DSLCompileResult,
    DSLExecuteResult,
    DSLRuntimeService,
)
from mysingle.dsl.stdlib import get_stdlib_functions

logger = get_structured_logger(__name__)


class BacktestDSLService(DSLRuntimeService):
    """
    DSL service for Backtest Service

    Handles execution of compiled strategy bytecode against historical data.

    Usage:
        service = BacktestDSLService()

        # Execute pre-compiled bytecode
        result = await service.execute_strategy(
            bytecode=strategy_bytecode,
            market_data=ohlcv_dataframe,
            params={"rsi_period": 14}
        )
    """

    def __init__(self, enable_redis_cache: bool = True, **kwargs):
        """
        Initialize Backtest DSL Service

        Args:
            enable_redis_cache: Use Redis cache
            **kwargs: Additional arguments for DSLRuntimeService
        """
        super().__init__(**kwargs)

        # Setup caching
        if enable_redis_cache:
            try:
                cache_backend = DSLBytecodeCache()  # Uses config settings
                self._cache_backend = cache_backend
                logger.info("Backtest DSL using Redis cache")
            except Exception as e:
                logger.warning(f"Redis cache unavailable, using in-memory: {e}")
                self._cache_backend = InMemoryDSLCache(max_size=100)
        else:
            self._cache_backend = InMemoryDSLCache(max_size=100)

    def _get_service_name(self) -> str:
        """Service name for logging"""
        return "backtest"

    def _get_resource_limits(self) -> ResourceLimits:
        """Resource limits for backtest execution"""
        return ResourceLimits(
            MAX_EXECUTION_TIME_SECONDS=60,  # 60 seconds per execution
            MAX_MEMORY_MB=1024,  # 1GB
            MAX_ITERATIONS=1000000,  # More iterations for backtests
        )

    async def _get_from_cache(self, cache_key: str) -> Optional[bytes]:
        """Get compiled bytecode from cache"""
        return await self._cache_backend.get(cache_key)

    async def _put_in_cache(
        self, cache_key: str, bytecode: bytes, ttl: int = 3600
    ) -> None:
        """Store compiled bytecode in cache"""
        await self._cache_backend.set(cache_key, bytecode, ttl=ttl)

    def _prepare_execution_context(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Prepare execution context with market data and stdlib

        Args:
            market_data: OHLCV DataFrame

        Returns:
            Execution context dict
        """
        # Get stdlib functions
        stdlib = get_stdlib_functions()

        # Add market data columns
        context = {
            **stdlib,
            "data": market_data,
            "open": market_data["open"],
            "high": market_data["high"],
            "low": market_data["low"],
            "close": market_data["close"],
            "volume": market_data["volume"],
        }

        return context

    async def execute_strategy(
        self,
        bytecode: bytes,
        market_data: pd.DataFrame,
        params: Optional[Dict[str, Any]] = None,
        strategy_id: Optional[str] = None,
        backtest_id: Optional[str] = None,
    ) -> DSLExecuteResult:
        """
        Execute strategy bytecode against market data

        Args:
            bytecode: Compiled strategy bytecode
            market_data: OHLCV DataFrame
            params: Strategy parameters
            strategy_id: Strategy ID for logging
            backtest_id: Backtest ID for logging

        Returns:
            DSLExecuteResult with signals
        """
        logger.info(
            "Executing strategy",
            strategy_id=strategy_id,
            backtest_id=backtest_id,
            data_rows=len(market_data),
            params=params,
        )

        # Prepare execution context
        context = self._prepare_execution_context(market_data)

        # Execute
        result = await self.execute(
            bytecode=bytecode, context=context, params=params or {}
        )

        if result.success:
            logger.info(
                "Strategy executed successfully",
                strategy_id=strategy_id,
                backtest_id=backtest_id,
                execution_time_ms=result.execution_time_ms,
                memory_used_mb=result.memory_used_mb,
            )
        else:
            logger.error(
                "Strategy execution failed",
                strategy_id=strategy_id,
                backtest_id=backtest_id,
                error=str(result.error),
            )

        return result

    async def compile_and_execute_strategy(
        self,
        code: str,
        market_data: pd.DataFrame,
        params: Optional[Dict[str, Any]] = None,
        validate: bool = True,
    ) -> tuple[DSLCompileResult, Optional[DSLExecuteResult]]:
        """
        Compile and execute strategy in one call

        Useful for ad-hoc backtests without pre-compiled bytecode

        Args:
            code: Strategy DSL code
            market_data: OHLCV DataFrame
            params: Strategy parameters
            validate: Run validation before compilation

        Returns:
            Tuple of (compile_result, execute_result)
        """
        logger.info(
            "Compiling and executing strategy",
            code_length=len(code),
            data_rows=len(market_data),
        )

        # Compile
        compile_result = await self.compile(code, validate=validate, use_cache=True)

        if not compile_result.success or not compile_result.bytecode:
            return compile_result, None

        # Prepare context
        context = self._prepare_execution_context(market_data)

        # Execute
        execute_result = await self.execute(
            bytecode=compile_result.bytecode, context=context, params=params or {}
        )

        return compile_result, execute_result


# Example: How to use in Backtest Service


async def example_run_backtest(
    strategy_bytecode: bytes,
    market_data: pd.DataFrame,
    strategy_params: Dict[str, Any],
    strategy_id: str,
    backtest_id: str,
) -> Dict[str, Any]:
    """
    Example backtest execution

    This would be in app/services/backtest/executor.py
    """
    service = BacktestDSLService()

    # Execute strategy
    result = await service.execute_strategy(
        bytecode=strategy_bytecode,
        market_data=market_data,
        params=strategy_params,
        strategy_id=strategy_id,
        backtest_id=backtest_id,
    )

    if not result.success:
        return {"success": False, "error": str(result.error)}

    # Process signals
    signals = result.result

    # Calculate performance metrics
    # ...

    return {
        "success": True,
        "signals": signals,
        "execution_time_ms": result.execution_time_ms,
        "memory_used_mb": result.memory_used_mb,
    }


async def example_adhoc_backtest(
    strategy_code: str, market_data: pd.DataFrame, strategy_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Example ad-hoc backtest without pre-compiled bytecode

    This would be in app/services/backtest/router.py for quick testing
    """
    service = BacktestDSLService()

    # Compile and execute
    compile_result, execute_result = await service.compile_and_execute_strategy(
        code=strategy_code,
        market_data=market_data,
        params=strategy_params,
        validate=True,
    )

    if not compile_result.success:
        return {
            "success": False,
            "errors": [str(e) for e in compile_result.errors],
            "warnings": compile_result.warnings,
        }

    if not execute_result or not execute_result.success:
        return {
            "success": False,
            "error": (
                str(execute_result.error) if execute_result else "Execution failed"
            ),
        }

    return {
        "success": True,
        "signals": execute_result.result,
        "compile_time_ms": compile_result.compile_time_ms,
        "execution_time_ms": execute_result.execution_time_ms,
        "warnings": compile_result.warnings,
    }

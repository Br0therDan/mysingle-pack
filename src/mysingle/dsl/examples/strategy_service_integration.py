"""
Strategy DSL Service - Refactored using DSLRuntimeService

Example implementation showing how to use the unified DSL runtime
for strategy compilation and validation in Strategy Service.
"""

from typing import Any, Dict, Optional

from mysingle.core.logging import get_structured_logger
from mysingle.dsl.cache import DSLBytecodeCache, DSLCacheManager, InMemoryDSLCache
from mysingle.dsl.limits import ResourceLimits
from mysingle.dsl.runtime_service import (
    DSLCompileResult,
    DSLRuntimeService,
    DSLValidateResult,
)

logger = get_structured_logger(__name__)


class StrategyDSLService(DSLRuntimeService):
    """
    DSL service for Strategy Service

    Handles compilation and validation of strategy DSL code.
    Does NOT execute strategies (execution is done in Backtest Service).

    Usage:
        service = StrategyDSLService()

        # Compile strategy
        result = await service.compile(strategy_code)
        if result.success:
            # Store bytecode in database
            await store_strategy_bytecode(result.bytecode, result.code_hash)

        # Validate without compilation
        validation = await service.validate(strategy_code)
    """

    def __init__(self, enable_redis_cache: bool = True, **kwargs):
        """
        Initialize Strategy DSL Service

        Args:
            enable_redis_cache: Use Redis cache (fallback to in-memory)
            **kwargs: Additional arguments for DSLRuntimeService
        """
        super().__init__(**kwargs)

        # Setup caching
        if enable_redis_cache:
            try:
                cache_backend = DSLBytecodeCache()  # Uses config settings
                self.cache_manager = DSLCacheManager(cache_backend)
                logger.info("Strategy DSL using Redis cache")
            except Exception as e:
                logger.warning(f"Redis cache unavailable, using in-memory: {e}")
                cache_backend = InMemoryDSLCache(max_size=500)
                self.cache_manager = DSLCacheManager(cache_backend)
        else:
            cache_backend = InMemoryDSLCache(max_size=500)
            self.cache_manager = DSLCacheManager(cache_backend)

        self._cache_backend = cache_backend

    def _get_service_name(self) -> str:
        """Service name for logging"""
        return "strategy"

    def _get_resource_limits(self) -> ResourceLimits:
        """Resource limits for strategy compilation"""
        return ResourceLimits(
            MAX_EXECUTION_TIME_SECONDS=10,  # 10 seconds for compilation
            MAX_MEMORY_MB=512,  # 512MB
            MAX_ITERATIONS=100000,
        )

    async def _get_from_cache(self, cache_key: str) -> Optional[bytes]:
        """Get compiled bytecode from cache"""
        return await self._cache_backend.get(cache_key)

    async def _put_in_cache(
        self, cache_key: str, bytecode: bytes, ttl: int = 3600
    ) -> None:
        """Store compiled bytecode in cache"""
        await self._cache_backend.set(cache_key, bytecode, ttl=ttl)

    def _record_metric(
        self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record metric (integrate with Prometheus)"""
        # TODO: Integrate with mysingle.core.metrics when available
        super()._record_metric(metric_name, value, tags)

    async def compile_strategy(
        self, code: str, strategy_id: str, user_id: str, validate: bool = True
    ) -> DSLCompileResult:
        """
        Compile strategy DSL code

        Args:
            code: Strategy DSL source code
            strategy_id: Strategy ID for logging
            user_id: User ID for logging
            validate: Run validation before compilation

        Returns:
            DSLCompileResult with bytecode
        """
        logger.info(
            "Compiling strategy",
            strategy_id=strategy_id,
            user_id=user_id,
            code_length=len(code),
        )

        result = await self.compile(code, validate=validate, use_cache=True)

        if result.success:
            logger.info(
                "Strategy compiled successfully",
                strategy_id=strategy_id,
                code_hash=result.code_hash,
                compile_time_ms=result.compile_time_ms,
            )
        else:
            logger.error(
                "Strategy compilation failed",
                strategy_id=strategy_id,
                errors=[str(e) for e in result.errors],
            )

        return result

    async def validate_strategy(
        self, code: str, strategy_id: Optional[str] = None
    ) -> DSLValidateResult:
        """
        Validate strategy DSL code

        Args:
            code: Strategy DSL source code
            strategy_id: Strategy ID for logging (optional)

        Returns:
            DSLValidateResult with validation errors/warnings
        """
        logger.info(
            "Validating strategy", strategy_id=strategy_id, code_length=len(code)
        )

        result = await self.validate(code)

        if result.success:
            logger.info(
                "Strategy validation passed",
                strategy_id=strategy_id,
                warnings_count=len(result.warnings),
            )
        else:
            logger.error(
                "Strategy validation failed",
                strategy_id=strategy_id,
                errors=[str(e) for e in result.errors],
            )

        return result

    async def warm_popular_strategies(
        self,
        strategy_codes: list[tuple[str, str]],  # [(code, version), ...]
    ) -> int:
        """
        Warm cache with popular strategies

        Args:
            strategy_codes: List of (code, version) tuples

        Returns:
            Number of strategies warmed
        """
        logger.info("Warming strategy cache", count=len(strategy_codes))

        warmed = await self.cache_manager.warm_cache(
            strategy_codes, service_name="strategy"
        )

        logger.info("Strategy cache warmed", warmed=warmed)
        return warmed


# Example: How to use in Strategy Service routers


async def example_compile_endpoint(
    strategy_code: str, strategy_id: str, user_id: str
) -> Dict[str, Any]:
    """
    Example endpoint for compiling strategy

    This would be in app/services/strategies/router.py
    """
    service = StrategyDSLService()

    # Compile strategy
    result = await service.compile_strategy(
        code=strategy_code, strategy_id=strategy_id, user_id=user_id, validate=True
    )

    if not result.success:
        return {
            "success": False,
            "errors": [str(e) for e in result.errors],
            "warnings": result.warnings,
        }

    # Store bytecode in database
    # await store_in_database(strategy_id, result.bytecode, result.code_hash)

    return {
        "success": True,
        "code_hash": result.code_hash,
        "compile_time_ms": result.compile_time_ms,
        "version": str(result.version),
        "warnings": result.warnings,
    }


async def example_validate_endpoint(
    strategy_code: str, strategy_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Example endpoint for validating strategy

    This would be in app/services/strategies/router.py
    """
    service = StrategyDSLService()

    # Validate strategy
    result = await service.validate_strategy(
        code=strategy_code, strategy_id=strategy_id
    )

    return {
        "success": result.success,
        "errors": [str(e) for e in result.errors],
        "warnings": result.warnings,
        "type_info": result.type_info,
        "security_issues": result.security_issues,
    }

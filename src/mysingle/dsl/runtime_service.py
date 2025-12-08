"""
DSL Runtime Service - Unified interface for DSL execution across services

Provides standardized compile/execute/validate methods with version management,
caching, and monitoring hooks for Strategy/Indicator/Backtest services.
"""

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from mysingle.core.logging import get_structured_logger
from mysingle.dsl.errors import DSLCompilationError, DSLError, DSLValidationError
from mysingle.dsl.executor import DSLExecutor
from mysingle.dsl.limits import ResourceLimits
from mysingle.dsl.parser import DSLParser
from mysingle.dsl.validator import SecurityValidator

logger = get_structured_logger(__name__)


@dataclass
class DSLVersion:
    """DSL version information with semantic versioning"""

    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, version_str: str) -> "DSLVersion":
        """Parse version string like '1.2.0'"""
        parts = version_str.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version_str}")
        return cls(major=int(parts[0]), minor=int(parts[1]), patch=int(parts[2]))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def is_compatible(self, other: "DSLVersion") -> bool:
        """Check if versions are compatible (same major version)"""
        return self.major == other.major

    def is_newer_than(self, other: "DSLVersion") -> bool:
        """Check if this version is newer"""
        if self.major != other.major:
            return self.major > other.major
        if self.minor != other.minor:
            return self.minor > other.minor
        return self.patch > other.patch

    def __lt__(self, other: "DSLVersion") -> bool:
        """Less than comparison for sorting"""
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        return self.patch < other.patch

    def __le__(self, other: "DSLVersion") -> bool:
        """Less than or equal comparison"""
        return self < other or self == other

    def __gt__(self, other: "DSLVersion") -> bool:
        """Greater than comparison"""
        return not self <= other

    def __ge__(self, other: "DSLVersion") -> bool:
        """Greater than or equal comparison"""
        return not self < other

    def __eq__(self, other: object) -> bool:
        """Equality comparison"""
        if not isinstance(other, DSLVersion):
            return False
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )


@dataclass
class DSLCompileResult:
    """Result of DSL compilation"""

    success: bool
    code_hash: str
    bytecode: Optional[bytes] = None
    ast_tree: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[DSLError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    compile_time_ms: float = 0.0
    version: Optional[DSLVersion] = None

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


@dataclass
class DSLExecuteResult:
    """Result of DSL execution"""

    success: bool
    result: Optional[Any] = None
    error: Optional[DSLError] = None
    execution_time_ms: float = 0.0
    memory_used_mb: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DSLValidateResult:
    """Result of DSL validation"""

    success: bool
    errors: List[DSLError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    type_info: Optional[Dict[str, Any]] = None
    security_issues: List[str] = field(default_factory=list)


class DSLRuntimeService(ABC):
    """
    Base class for DSL runtime services

    Provides unified interface for compile/execute/validate operations
    with built-in caching, versioning, and monitoring.

    Usage:
        class StrategyDSLService(DSLRuntimeService):
            def _get_service_name(self) -> str:
                return "strategy"

            def _get_resource_limits(self) -> ResourceLimits:
                return ResourceLimits(timeout=5.0, memory_limit=256*1024*1024)
    """

    def __init__(
        self,
        version: Optional[str] = None,
        enable_cache: bool = True,
        enable_monitoring: bool = True,
    ):
        """
        Initialize DSL runtime service

        Args:
            version: DSL version string (e.g., "1.2.0"), defaults to package version
            enable_cache: Enable bytecode caching
            enable_monitoring: Enable performance monitoring
        """
        from mysingle.dsl import __version__

        self.version = DSLVersion.from_string(version or __version__)
        self.enable_cache = enable_cache
        self.enable_monitoring = enable_monitoring

        self._parser = DSLParser()
        self._validator = SecurityValidator()
        self._executor = DSLExecutor()

        # Service-specific configuration
        self._service_name = self._get_service_name()
        self._resource_limits = self._get_resource_limits()

        logger.info(
            "DSL runtime service initialized",
            service=self._service_name,
            version=str(self.version),
            cache_enabled=enable_cache,
            monitoring_enabled=enable_monitoring,
        )

    @abstractmethod
    def _get_service_name(self) -> str:
        """Return service name for logging/monitoring"""
        pass

    @abstractmethod
    def _get_resource_limits(self) -> ResourceLimits:
        """Return resource limits for this service"""
        pass

    def _compute_code_hash(self, code: str) -> str:
        """Compute SHA256 hash of DSL code"""
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    def _get_cache_key(self, code_hash: str) -> str:
        """Generate cache key for compiled bytecode"""
        return f"dsl:bytecode:{self._service_name}:{code_hash}"

    async def _get_from_cache(self, cache_key: str) -> Optional[bytes]:
        """
        Retrieve compiled bytecode from cache

        Override this method to implement caching (Redis, etc.)
        Default implementation does nothing (no cache).
        """
        return None

    async def _put_in_cache(
        self, cache_key: str, bytecode: bytes, ttl: int = 3600
    ) -> None:
        """
        Store compiled bytecode in cache

        Override this method to implement caching (Redis, etc.)
        Default implementation does nothing (no cache).
        """
        # Default: no caching - subclasses can override
        return None  # Explicit return to avoid B027

    def _record_metric(
        self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record performance metric

        Override this method to implement monitoring (Prometheus, etc.)
        """
        if self.enable_monitoring:
            logger.debug(
                f"Metric: {metric_name}",
                value=value,
                tags=tags or {},
                service=self._service_name,
            )

    async def compile(
        self, code: str, validate: bool = True, use_cache: bool = True
    ) -> DSLCompileResult:
        """
        Compile DSL code to bytecode

        Args:
            code: DSL source code
            validate: Run security validation before compilation
            use_cache: Use cached bytecode if available

        Returns:
            DSLCompileResult with bytecode and metadata
        """
        start_time = datetime.now(UTC)
        code_hash = self._compute_code_hash(code)

        logger.info(
            "Compiling DSL code",
            service=self._service_name,
            code_hash=code_hash,
            code_length=len(code),
            validate=validate,
            use_cache=use_cache,
        )

        try:
            # Check cache first
            if use_cache and self.enable_cache:
                cache_key = self._get_cache_key(code_hash)
                cached_bytecode = await self._get_from_cache(cache_key)

                if cached_bytecode:
                    compile_time = (
                        datetime.now(UTC) - start_time
                    ).total_seconds() * 1000
                    logger.info("Cache hit for DSL bytecode", code_hash=code_hash)
                    self._record_metric("dsl_compile_cache_hit", 1.0)

                    return DSLCompileResult(
                        success=True,
                        code_hash=code_hash,
                        bytecode=cached_bytecode,
                        metadata={"cache_hit": True},
                        compile_time_ms=compile_time,
                        version=self.version,
                    )

            # Validate if requested
            if validate:
                validation_result = await self.validate(code)
                if not validation_result.success:
                    compile_time = (
                        datetime.now(UTC) - start_time
                    ).total_seconds() * 1000
                    return DSLCompileResult(
                        success=False,
                        code_hash=code_hash,
                        errors=validation_result.errors,
                        warnings=validation_result.warnings,
                        compile_time_ms=compile_time,
                        version=self.version,
                    )

            # Compile code (parser.parse returns bytes directly)
            try:
                bytecode = self._parser.parse(code)
            except Exception as parse_error:
                compile_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
                return DSLCompileResult(
                    success=False,
                    code_hash=code_hash,
                    errors=[
                        DSLCompilationError(str(parse_error) or "Compilation failed")
                    ],
                    compile_time_ms=compile_time,
                    version=self.version,
                )

            # Cache compiled bytecode
            if use_cache and self.enable_cache and bytecode:
                cache_key = self._get_cache_key(code_hash)
                await self._put_in_cache(cache_key, bytecode)
                self._record_metric("dsl_compile_cache_miss", 1.0)

            compile_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self._record_metric("dsl_compile_time_ms", compile_time)

            return DSLCompileResult(
                success=True,
                code_hash=code_hash,
                bytecode=bytecode,
                ast_tree=None,
                metadata={"cache_hit": False},
                compile_time_ms=compile_time,
                version=self.version,
            )

        except Exception as e:
            compile_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            logger.error(
                "DSL compilation failed",
                error=str(e),
                code_hash=code_hash,
                service=self._service_name,
            )
            return DSLCompileResult(
                success=False,
                code_hash=code_hash,
                errors=[DSLCompilationError(f"Compilation error: {str(e)}")],
                compile_time_ms=compile_time,
                version=self.version,
            )

    async def execute(
        self,
        bytecode: bytes,
        context: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> DSLExecuteResult:
        """
        Execute compiled DSL bytecode

        Args:
            bytecode: Compiled bytecode
            context: Execution context (globals)
            params: User parameters

        Returns:
            DSLExecuteResult with execution result
        """
        start_time = datetime.now(UTC)

        logger.info(
            "Executing DSL bytecode",
            service=self._service_name,
            bytecode_size=len(bytecode),
            has_context=context is not None,
            has_params=params is not None,
        )

        try:
            # Note: DSLExecutor.execute signature is (compiled_code, data, params)
            # Provide a minimal DataFrame if not available in context
            import pandas as pd

            data = (
                context.get("data") if context and "data" in context else pd.DataFrame()
            )

            result = self._executor.execute(
                compiled_code=bytecode,
                data=data if isinstance(data, pd.DataFrame) else pd.DataFrame(),
                params=params or {},
            )

            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self._record_metric("dsl_execution_time_ms", execution_time)

            return DSLExecuteResult(
                success=True,
                result=result,
                execution_time_ms=execution_time,
                metadata={},
            )

        except Exception as e:
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            logger.error(
                "DSL execution failed", error=str(e), service=self._service_name
            )
            return DSLExecuteResult(
                success=False,
                error=DSLError(f"Execution error: {str(e)}"),
                execution_time_ms=execution_time,
            )

    async def validate(self, code: str) -> DSLValidateResult:
        """
        Validate DSL code for security and correctness

        Args:
            code: DSL source code

        Returns:
            DSLValidateResult with validation errors/warnings
        """
        logger.info(
            "Validating DSL code", service=self._service_name, code_length=len(code)
        )

        try:
            # Security validation (returns tuple[bool, list[SecurityViolation]])
            is_valid, violations = self._validator.validate(code)

            if not is_valid:
                return DSLValidateResult(
                    success=False,
                    errors=[DSLValidationError(str(v)) for v in violations],
                    security_issues=[str(v) for v in violations],
                )

            # Type inference (if available)
            type_info = None
            try:
                from mysingle.dsl.type_system import check_types

                type_result = check_types(code)
                type_info = {"types": type_result} if type_result else None
            except Exception as e:
                logger.warning("Type inference failed", error=str(e))

            return DSLValidateResult(success=True, warnings=[], type_info=type_info)

        except Exception as e:
            logger.error(
                "DSL validation failed", error=str(e), service=self._service_name
            )
            return DSLValidateResult(
                success=False,
                errors=[DSLValidationError(f"Validation error: {str(e)}")],
            )

    async def compile_and_execute(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        validate: bool = True,
        use_cache: bool = True,
    ) -> tuple[DSLCompileResult, Optional[DSLExecuteResult]]:
        """
        Compile and execute DSL code in one call

        Args:
            code: DSL source code
            context: Execution context
            params: User parameters
            validate: Run validation before compilation
            use_cache: Use cached bytecode

        Returns:
            Tuple of (compile_result, execute_result)
        """
        # Compile
        compile_result = await self.compile(
            code, validate=validate, use_cache=use_cache
        )

        if not compile_result.success or not compile_result.bytecode:
            return compile_result, None

        # Execute
        execute_result = await self.execute(
            bytecode=compile_result.bytecode, context=context, params=params
        )

        return compile_result, execute_result

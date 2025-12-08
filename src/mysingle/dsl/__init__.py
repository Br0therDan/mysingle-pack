"""
mysingle.dsl - Domain Specific Language Runtime

안전한 사용자 코드 실행을 위한 공통 DSL 런타임
"""

from mysingle.dsl.cache import (
    DSLBytecodeCache,
    DSLCacheManager,
    InMemoryDSLCache,
    RedisDSLCache,  # Legacy alias
)
from mysingle.dsl.errors import (
    DSLCompilationError,
    DSLError,
    DSLExecutionError,
    DSLMemoryError,
    DSLSecurityError,
    DSLTimeoutError,
    DSLValidationError,
    SecurityViolation,
)
from mysingle.dsl.executor import DSLExecutor
from mysingle.dsl.limits import ResourceLimits, UserQuota
from mysingle.dsl.migration import (
    DSLMigrationTool,
    DSLVersionRegistry,
    MigrationResult,
    MigrationRule,
    MigrationStrategy,
    get_version_registry,
)
from mysingle.dsl.parser import DSLParser
from mysingle.dsl.runtime_service import (
    DSLCompileResult,
    DSLExecuteResult,
    DSLRuntimeService,
    DSLValidateResult,
    DSLVersion,
)
from mysingle.dsl.stdlib import get_stdlib_functions
from mysingle.dsl.type_system import TypeInferenceEngine, check_types
from mysingle.dsl.validator import SecurityValidator

__all__ = [
    # Executor
    "DSLParser",
    "SecurityValidator",
    "DSLExecutor",
    # Errors
    "DSLError",
    "DSLCompilationError",
    "DSLValidationError",
    "DSLSecurityError",
    "DSLExecutionError",
    "DSLTimeoutError",
    "DSLMemoryError",
    "SecurityViolation",
    # Config
    "ResourceLimits",
    "UserQuota",
    # Stdlib
    "get_stdlib_functions",
    # Type System
    "TypeInferenceEngine",
    "check_types",
    # Runtime Service
    "DSLRuntimeService",
    "DSLVersion",
    "DSLCompileResult",
    "DSLExecuteResult",
    "DSLValidateResult",
    # Cache
    "DSLBytecodeCache",
    "RedisDSLCache",  # Legacy alias
    "InMemoryDSLCache",
    "DSLCacheManager",
    # Migration
    "DSLVersionRegistry",
    "DSLMigrationTool",
    "MigrationStrategy",
    "MigrationRule",
    "MigrationResult",
    "get_version_registry",
]

__version__ = "1.3.0"  # Phase 1-3 in progress

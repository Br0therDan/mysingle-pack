"""
mysingle.dsl - Domain Specific Language Runtime

안전한 사용자 코드 실행을 위한 공통 DSL 런타임
"""

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
from mysingle.dsl.parser import DSLParser
from mysingle.dsl.stdlib import get_stdlib_functions
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
]

__version__ = "1.0.0"

"""DSL 관련 사용자 정의 예외"""


class DSLError(Exception):
    """DSL 관련 기본 예외"""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        line: int | None = None,
        column: int | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code  # DSL-001, DSL-002 등 구조화된 에러 코드
        self.line = line
        self.column = column

    def __str__(self) -> str:
        parts = []
        if self.code:
            parts.append(f"[{self.code}]")
        parts.append(self.message)
        if self.line is not None:
            parts.append(f"at line {self.line}")
            if self.column is not None:
                parts.append(f", column {self.column}")
        return " ".join(parts)


class DSLCompilationError(DSLError):
    """DSL 코드 컴파일 실패"""

    def __init__(
        self, message: str, line: int | None = None, column: int | None = None
    ):
        super().__init__(message, code="DSL-001", line=line, column=column)


class DSLValidationError(DSLError):
    """DSL 코드 검증 실패 (보안, 타입 등)"""

    def __init__(
        self, message: str, line: int | None = None, column: int | None = None
    ):
        super().__init__(message, code="DSL-002", line=line, column=column)


class DSLSecurityError(DSLValidationError):
    """보안 위반 (금지된 import, builtin 등)"""

    def __init__(
        self, message: str, line: int | None = None, column: int | None = None
    ):
        super().__init__(message, line=line, column=column)
        self.code = "DSL-003"  # Override to more specific code


class DSLExecutionError(DSLError):
    """DSL 코드 실행 중 에러"""

    def __init__(
        self, message: str, line: int | None = None, column: int | None = None
    ):
        super().__init__(message, code="DSL-004", line=line, column=column)


class DSLTimeoutError(DSLExecutionError):
    """실행 시간 초과"""

    def __init__(self, message: str = "Execution time limit exceeded"):
        super().__init__(message)
        self.code = "DSL-005"


class DSLMemoryError(DSLExecutionError):
    """메모리 제한 초과"""

    def __init__(self, message: str = "Memory limit exceeded"):
        super().__init__(message)
        self.code = "DSL-006"


class SecurityViolation:
    """보안 위반 사항"""

    def __init__(
        self,
        level: str,
        message: str,
        line: int | None = None,
        column: int | None = None,
    ):
        self.level = level  # ERROR, WARNING, INFO
        self.message = message
        self.line = line
        self.column = column

    def __repr__(self) -> str:
        location = f" (line {self.line})" if self.line else ""
        return f"[{self.level}]{location} {self.message}"

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "level": self.level,
            "message": self.message,
            "line": self.line,
            "column": self.column,
        }

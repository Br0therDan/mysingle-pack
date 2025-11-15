"""DSL 관련 사용자 정의 예외"""


class DSLError(Exception):
    """DSL 관련 기본 예외"""

    pass


class DSLCompilationError(DSLError):
    """DSL 코드 컴파일 실패"""

    pass


class DSLValidationError(DSLError):
    """DSL 코드 검증 실패 (보안, 타입 등)"""

    pass


class DSLSecurityError(DSLValidationError):
    """보안 위반 (금지된 import, builtin 등)"""

    pass


class DSLExecutionError(DSLError):
    """DSL 코드 실행 중 에러"""

    pass


class DSLTimeoutError(DSLExecutionError):
    """실행 시간 초과"""

    pass


class DSLMemoryError(DSLExecutionError):
    """메모리 제한 초과"""

    pass


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

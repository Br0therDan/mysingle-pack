"""RestrictedPython 기반 DSL 파서"""

import hashlib
import marshal
from types import CodeType
from typing import Any

from RestrictedPython import compile_restricted
from RestrictedPython.Guards import (
    guarded_iter_unpack_sequence,
    safe_builtins,
    safer_getattr,
)

from mysingle.dsl.errors import DSLCompilationError


class DSLParser:
    """
    RestrictedPython 기반 DSL 파서

    사용자 DSL 코드를 안전하게 컴파일하고 실행 가능한 바이트코드로 변환
    """

    # 허용된 builtin 함수 (보안 검증됨)
    ALLOWED_BUILTINS = {
        # 수학 함수
        "abs",
        "all",
        "any",
        "enumerate",
        "filter",
        "len",
        "list",
        "map",
        "max",
        "min",
        "range",
        "round",
        "sorted",
        "sum",
        "zip",
        # 타입 변환
        "bool",
        "dict",
        "float",
        "int",
        "str",
        "tuple",
        # 예외
        "ValueError",
        "TypeError",
        "IndexError",
        "KeyError",
        "AttributeError",
        # 기타
        "isinstance",
        "hasattr",
        "getattr",
    }

    def __init__(self):
        """DSL 파서 초기화"""
        self._safe_builtins = self._get_safe_builtins()

    def parse(self, code: str, filename: str = "<indicator>") -> bytes:
        """
        DSL 코드를 바이트코드로 컴파일

        Args:
            code: DSL 소스 코드
            filename: 파일명 (에러 메시지용)

        Returns:
            bytes: 컴파일된 바이트코드 (marshal로 직렬화됨)

        Raises:
            DSLCompilationError: 컴파일 실패 시
        """
        try:
            # RestrictedPython으로 컴파일
            result = compile_restricted(code, filename=filename, mode="exec")

            # compile_restricted는 CompileResult 또는 code object를 반환할 수 있음
            # CompileResult인 경우 errors/warnings 속성 확인
            if hasattr(result, "errors") and result.errors:
                error_msg = "\n".join(result.errors)
                raise DSLCompilationError(
                    f"Compilation failed with {len(result.errors)} error(s):\n{error_msg}"
                )

            if hasattr(result, "warnings") and result.warnings:
                # 경고는 로깅만 (컴파일 계속)
                import logging

                logger = logging.getLogger(__name__)
                for warning in result.warnings:
                    logger.warning(f"Compilation warning: {warning}")

            # code object 추출
            code_object = result.code if hasattr(result, "code") else result

            if code_object is None:
                raise DSLCompilationError("Compilation produced no code object")

            # marshal을 사용하여 바이트코드로 직렬화
            return marshal.dumps(code_object)

        except SyntaxError as e:
            raise DSLCompilationError(f"Syntax error: {e}") from e
        except Exception as e:
            raise DSLCompilationError(f"Unexpected compilation error: {e}") from e

    def load(self, bytecode: bytes) -> CodeType:
        """
        직렬화된 바이트코드를 code object로 로드

        Args:
            bytecode: marshal로 직렬화된 바이트코드

        Returns:
            CodeType: 로드된 code object

        Raises:
            DSLCompilationError: 로드 실패 시
        """
        try:
            return marshal.loads(bytecode)
        except Exception as e:
            raise DSLCompilationError(f"Failed to load bytecode: {e}") from e

    def get_code_hash(self, code: str) -> str:
        """
        코드 해시 생성 (캐싱용)

        Args:
            code: DSL 소스 코드

        Returns:
            str: SHA-256 해시 (hex)
        """
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    def get_safe_globals(self) -> dict[str, Any]:
        """
        안전한 글로벌 네임스페이스 반환

        Returns:
            dict: 안전한 글로벌 변수 딕셔너리
        """

        # 기본 guard 함수들 정의
        def _getitem_(obj, index, wrap=True):
            """안전한 인덱스 접근"""
            return obj[index]

        def _getiter_(obj):
            """안전한 iterator 접근"""
            return iter(obj)

        def _write_(obj):
            """쓰기 guard (모든 쓰기 허용)"""
            return obj

        return {
            "__builtins__": self._safe_builtins,
            "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
            "_getattr_": safer_getattr,
            "_getitem_": _getitem_,
            "_getiter_": _getiter_,
            "_write_": _write_,
            # NumPy, Pandas는 executor에서 주입
        }

    def _get_safe_builtins(self) -> dict[str, Any]:
        """
        허용된 builtin 함수만 포함한 딕셔너리 생성

        Returns:
            dict: 안전한 builtin 함수 딕셔너리
        """
        return {
            name: safe_builtins.get(name) or __builtins__[name]
            for name in self.ALLOWED_BUILTINS
            if name in safe_builtins or name in __builtins__
        }

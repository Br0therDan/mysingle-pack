"""DSL 코드 정적 분석 및 보안 검증"""

import ast

from mysingle.dsl.errors import SecurityViolation


class SecurityValidator:
    """
    DSL 코드 보안 검증기

    AST 기반 정적 분석으로 금지된 연산 탐지
    """

    # 금지된 import 모듈
    FORBIDDEN_IMPORTS = {
        # 파일 I/O
        "os",
        "sys",
        "io",
        "pathlib",
        "shutil",
        "tempfile",
        # 네트워크
        "socket",
        "urllib",
        "urllib3",
        "requests",
        "httpx",
        "aiohttp",
        "websocket",
        # 시스템
        "subprocess",
        "multiprocessing",
        "threading",
        "signal",
        "resource",
        # 동적 실행
        "pickle",
        "marshal",
        "shelve",
        "importlib",
        "__builtin__",
        "builtins",
        # 기타 위험
        "ctypes",
        "gc",
        "inspect",
        "code",
        "codeop",
    }

    # 금지된 builtin 함수
    FORBIDDEN_BUILTINS = {
        "open",
        "input",
        "print",  # 콘솔 출력 금지 (로깅은 별도 제공)
        "eval",
        "exec",
        "compile",
        "__import__",
        "globals",
        "locals",
        "vars",
        "dir",
        "delattr",
        "setattr",
        "help",
        "breakpoint",
        "exit",
        "quit",
    }

    # 금지된 속성 접근
    FORBIDDEN_ATTRIBUTES = {
        "__class__",
        "__bases__",
        "__subclasses__",
        "__globals__",
        "__code__",
        "__closure__",
        "__dict__",
        "__module__",
        "__builtins__",
        "__import__",
        "__loader__",
        "__spec__",
        "__cached__",
        "__file__",
        "__name__",
        "__package__",
    }

    # 허용된 pandas/numpy 속성 (whitelist)
    ALLOWED_PANDAS_ATTRS = {
        # DataFrame/Series methods
        "rolling",
        "mean",
        "std",
        "sum",
        "max",
        "min",
        "shift",
        "diff",
        "pct_change",
        "fillna",
        "dropna",
        "iloc",
        "loc",
        "at",
        "iat",
        "head",
        "tail",
        "index",
        "values",
        "columns",
        "shape",
        "dtype",
        "dtypes",
        # Aggregation
        "groupby",
        "agg",
        "aggregate",
        "apply",
        "transform",
        "cumsum",
        "cumprod",
        "cummax",
        "cummin",
        # Statistical
        "corr",
        "cov",
        "describe",
        "quantile",
        "rank",
        # EWM
        "ewm",
        "expanding",
    }

    ALLOWED_NUMPY_ATTRS = {
        # Array operations
        "array",
        "asarray",
        "zeros",
        "ones",
        "full",
        "arange",
        "linspace",
        "logspace",
        # Math functions
        "abs",
        "sqrt",
        "exp",
        "log",
        "log10",
        "log2",
        "sin",
        "cos",
        "tan",
        "arcsin",
        "arccos",
        "arctan",
        "floor",
        "ceil",
        "round",
        # Statistical
        "mean",
        "median",
        "std",
        "var",
        "percentile",
        "min",
        "max",
        "sum",
        "prod",
        # Comparison
        "isnan",
        "isinf",
        "isfinite",
        "where",
        "select",
        "choose",
    }

    def __init__(self):
        """SecurityValidator 초기화"""
        pass

    def analyze(self, code: str) -> list[SecurityViolation]:
        """
        코드 정적 분석 수행

        Args:
            code: DSL 소스 코드

        Returns:
            list[SecurityViolation]: 발견된 보안 위반 사항 목록
        """
        violations: list[SecurityViolation] = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            violations.append(
                SecurityViolation(
                    level="ERROR", message=f"Syntax error: {e}", line=e.lineno
                )
            )
            return violations

        # AST 순회하며 검사
        for node in ast.walk(tree):
            # Import 검사
            if isinstance(node, ast.Import):
                violations.extend(self._check_import(node))

            elif isinstance(node, ast.ImportFrom):
                violations.extend(self._check_import_from(node))

            # 함수 호출 검사
            elif isinstance(node, ast.Call):
                violations.extend(self._check_call(node))

            # 속성 접근 검사
            elif isinstance(node, ast.Attribute):
                violations.extend(self._check_attribute(node))

            # 클래스 정의 검사 (Phase 1에서는 금지)
            elif isinstance(node, ast.ClassDef):
                violations.append(
                    SecurityViolation(
                        level="ERROR",
                        message="Class definition is not allowed in Phase 1",
                        line=node.lineno,
                    )
                )

            # async/await 검사 (금지)
            elif isinstance(node, (ast.AsyncFunctionDef, ast.Await)):
                violations.append(
                    SecurityViolation(
                        level="ERROR",
                        message="Async/await is not allowed",
                        line=node.lineno,
                    )
                )

            # Subscript with slice 검사 (임의 메모리 접근 방지)
            elif isinstance(node, ast.Subscript):
                violations.extend(self._check_subscript(node))

            # Name 바인딩 검사 (위험한 변수명)
            elif isinstance(node, ast.Name):
                violations.extend(self._check_name(node))

        return violations

    def _check_import(self, node: ast.Import) -> list[SecurityViolation]:
        """Import 문 검사"""
        violations = []

        for alias in node.names:
            if alias.name in self.FORBIDDEN_IMPORTS:
                violations.append(
                    SecurityViolation(
                        level="ERROR",
                        message=f"Forbidden import: {alias.name}",
                        line=node.lineno,
                    )
                )

        return violations

    def _check_import_from(self, node: ast.ImportFrom) -> list[SecurityViolation]:
        """ImportFrom 문 검사"""
        violations = []

        if node.module and node.module in self.FORBIDDEN_IMPORTS:
            violations.append(
                SecurityViolation(
                    level="ERROR",
                    message=f"Forbidden import: {node.module}",
                    line=node.lineno,
                )
            )

        return violations

    def _check_call(self, node: ast.Call) -> list[SecurityViolation]:
        """함수 호출 검사"""
        violations = []

        # builtin 함수 호출 검사
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.FORBIDDEN_BUILTINS:
                violations.append(
                    SecurityViolation(
                        level="ERROR",
                        message=f"Forbidden builtin function: {func_name}",
                        line=node.lineno,
                    )
                )

        return violations

    def _check_attribute(self, node: ast.Attribute) -> list[SecurityViolation]:
        """속성 접근 검사"""
        violations = []

        # 금지된 속성 접근
        if node.attr in self.FORBIDDEN_ATTRIBUTES:
            violations.append(
                SecurityViolation(
                    level="ERROR",
                    message=f"Forbidden attribute access: {node.attr}",
                    line=node.lineno,
                )
            )

        # pandas/numpy 속성 화이트리스트 검증
        if isinstance(node.value, ast.Name):
            var_name = node.value.id
            # pd.* 또는 np.* 접근 검사
            if var_name in ("pd", "pandas"):
                if node.attr not in self.ALLOWED_PANDAS_ATTRS:
                    violations.append(
                        SecurityViolation(
                            level="WARNING",
                            message=f"Unverified pandas attribute: {node.attr}",
                            line=node.lineno,
                        )
                    )
            elif (
                var_name in ("np", "numpy")
                and node.attr not in self.ALLOWED_NUMPY_ATTRS
            ):
                violations.append(
                    SecurityViolation(
                        level="WARNING",
                        message=f"Unverified numpy attribute: {node.attr}",
                        line=node.lineno,
                    )
                )

        return violations

    def _check_subscript(self, node: ast.Subscript) -> list[SecurityViolation]:
        """Subscript 접근 검사 (임의 메모리 접근 방지)"""
        violations = []

        # 복잡한 slice 패턴 검사
        if (
            isinstance(node.slice, ast.Slice)
            and isinstance(node.slice.step, ast.UnaryOp)
            and isinstance(node.slice.step.op, ast.USub)
        ):
            violations.append(
                SecurityViolation(
                    level="WARNING",
                    message="Negative slice step detected",
                    line=node.lineno,
                )
            )

        return violations

    def _check_name(self, node: ast.Name) -> list[SecurityViolation]:
        """Name 바인딩 검사 (위험한 변수명)"""
        violations = []

        # 언더스코어로 시작하는 변수명 경고 (private 규약)
        if (
            isinstance(node.ctx, ast.Store)
            and node.id.startswith("_")
            and node.id.startswith("__")
            and node.id.endswith("__")
        ):
            violations.append(
                SecurityViolation(
                    level="ERROR",
                    message=f"Dunder name assignment forbidden: {node.id}",
                    line=node.lineno,
                )
            )

        return violations

    def validate(self, code: str) -> tuple[bool, list[SecurityViolation]]:
        """
        코드 검증 및 결과 반환

        Args:
            code: DSL 소스 코드

        Returns:
            tuple[bool, list[SecurityViolation]]:
                - bool: 검증 통과 여부 (ERROR가 없으면 True)
                - list: 위반 사항 목록
        """
        violations = self.analyze(code)

        # ERROR 레벨 위반이 있으면 실패
        has_errors = any(v.level == "ERROR" for v in violations)

        return not has_errors, violations

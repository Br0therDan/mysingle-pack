"""DSL 코드 실행 엔진"""

import marshal
import resource
import signal
import threading
from contextlib import contextmanager
from types import CodeType
from typing import Any

import pandas as pd

from mysingle.dsl.errors import DSLExecutionError, DSLMemoryError, DSLTimeoutError
from mysingle.dsl.parser import DSLParser


class DSLExecutor:
    """
    DSL 코드 안전 실행 엔진

    리소스 제한과 함께 사용자 코드를 안전하게 실행
    """

    # 리소스 제한 설정
    MAX_EXECUTION_TIME_SECONDS = 30  # 최대 실행 시간
    MAX_MEMORY_MB = 512  # 최대 메모리
    MAX_RECURSION_DEPTH = 100  # 최대 재귀 깊이

    def __init__(self, parser: DSLParser | None = None):
        """
        DSLExecutor 초기화

        Args:
            parser: DSL 파서 인스턴스 (None이면 새로 생성)
        """
        self.parser = parser or DSLParser()

    def execute(
        self,
        compiled_code: bytes | CodeType,
        data: pd.DataFrame,
        params: dict[str, Any],
    ) -> pd.Series | pd.DataFrame:
        """
        컴파일된 DSL 코드 실행

        Args:
            compiled_code: 컴파일된 바이트코드 (bytes) 또는 code object (CodeType)
            data: OHLCV 데이터프레임
            params: 파라미터 딕셔너리

        Returns:
            pd.Series | pd.DataFrame: 계산 결과

        Raises:
            DSLExecutionError: 실행 중 에러 발생
            DSLTimeoutError: 실행 시간 초과
            DSLMemoryError: 메모리 제한 초과
        """
        with self._resource_limits():
            try:
                # 바이트코드인 경우 code object로 변환
                if isinstance(compiled_code, bytes):
                    code_object = marshal.loads(compiled_code)
                else:
                    code_object = compiled_code

                # 안전한 글로벌 네임스페이스 구성
                namespace = self._build_namespace(data, params)

                # 바이트코드 실행
                exec(code_object, namespace)  # nosec B102 - Controlled execution with RestrictedPython

                # 'result' 변수 확인 (DSL 코드가 result = ... 형식으로 작성됨)
                if "result" not in namespace:
                    raise DSLExecutionError(
                        "Variable 'result' not found. DSL code must assign result to 'result' variable"
                    )

                result = namespace.get("result")

                # Handle MSLSeries wrapper
                from mysingle.dsl.series import MSLSeries

                if isinstance(result, MSLSeries):
                    result = result.series

                # 결과 타입 검증
                if not isinstance(result, (pd.Series, pd.DataFrame)):
                    raise DSLExecutionError(
                        f"Result must be pd.Series or pd.DataFrame, "
                        f"got {type(result).__name__}"
                    )

                return result

            except TimeoutError as e:
                raise DSLTimeoutError(
                    f"Execution exceeded {self.MAX_EXECUTION_TIME_SECONDS}s timeout. "
                    f"Consider optimizing your code or reducing data size."
                ) from e

            except MemoryError as e:
                raise DSLMemoryError(
                    f"Execution exceeded {self.MAX_MEMORY_MB}MB memory limit. "
                    f"Consider reducing data size or simplifying calculation."
                ) from e

            except DSLExecutionError:
                # 이미 DSL 에러면 그대로 re-raise
                raise

            except Exception as e:
                # 기타 예외를 DSLExecutionError로 래핑
                raise DSLExecutionError(f"Execution failed: {e}") from e

    def compile_and_execute(
        self,
        code: str,
        data: pd.DataFrame,
        params: dict[str, Any],
    ) -> pd.Series | pd.DataFrame:
        """
        DSL 코드 컴파일 및 실행 (편의 함수)

        Args:
            code: DSL 소스 코드
            data: OHLCV 데이터프레임
            params: 파라미터 딕셔너리

        Returns:
            pd.Series | pd.DataFrame: 계산 결과
        """
        compiled_code = self.parser.parse(code)
        return self.execute(compiled_code, data, params)

    def _build_namespace(
        self, data: pd.DataFrame, params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        안전한 실행 네임스페이스 구성

        Args:
            data: OHLCV 데이터
            params: 파라미터

        Returns:
            dict: 실행 네임스페이스
        """
        # 기본 안전 글로벌
        namespace = self.parser.get_safe_globals()

        # Fluent API Proxies 주입
        from mysingle.dsl.proxies import (
            IndicatorProxy,
            InputProxy,
            MarketProxy,
            PatternProxy,
            PlotProxy,
            PortfolioProxy,
            StrategyWrapper,
            UniverseProxy,
            VarProxy,
        )
        from mysingle.dsl.series import MSLSeries

        # Context for side effects (visualizations, trading commands)
        context = params.get("_context")

        # 주입할 객체들 초기화
        input_proxy = InputProxy(data)
        indicator_proxy = IndicatorProxy(data)
        market_proxy = MarketProxy(data)
        pattern_proxy = PatternProxy(data)
        portfolio_proxy = PortfolioProxy(context)
        universe_proxy = UniverseProxy(data)
        strategy_proxy = StrategyWrapper(context)
        var_proxy = VarProxy(context)
        plot_proxy = PlotProxy(context)

        namespace.update(
            {
                "input": input_proxy,
                "indicator": indicator_proxy,
                "market": market_proxy,
                "pattern": pattern_proxy,
                "portfolio": portfolio_proxy,
                "universe": universe_proxy,
                "strategy": strategy_proxy,
                "var": var_proxy,
                "plot": plot_proxy,
            }
        )

        # DataFrame 컬럼을 개별 변수로 주입 (MSLSeries로 래핑하여 연산자 지원)
        for col in data.columns:
            namespace[col] = MSLSeries(data[col], name=col)

        # 파라미터를 개별 변수로도 주입 (하위 호환성)
        namespace.update({k: v for k, v in params.items() if k != "_context"})

        # StdLib 함수 추가
        from mysingle.dsl.stdlib import get_stdlib_functions

        namespace.update(get_stdlib_functions())

        # External Data Science Libraries (Phase 1: Whitelist)
        # Import on demand to strict namespace
        try:
            import scipy
            import sklearn
            import statsmodels

            namespace.update(
                {
                    "scipy": scipy,
                    "sklearn": sklearn,
                    "statsmodels": statsmodels,
                }
            )
        except ImportError:
            # If standard backtest service environment doesn't have them installed (e.g. minimal install)
            # we just don't expose them.
            pass

        return namespace

    @contextmanager
    def _resource_limits(self):
        """
        리소스 제한 컨텍스트 매니저

        CPU 시간 및 메모리 제한 적용 (크로스 플랫폼 지원)
        """
        # 기존 제한 값 저장
        old_recursion_limit = None
        old_alarm_handler = None
        old_memory_limit = None
        timeout_timer = None

        try:
            # 재귀 깊이 제한
            import sys

            old_recursion_limit = sys.getrecursionlimit()
            sys.setrecursionlimit(self.MAX_RECURSION_DEPTH)

            # CPU 시간 제한 (크로스 플랫폼)
            try:
                # UNIX: signal.SIGALRM 사용
                def timeout_handler(signum, frame):
                    raise TimeoutError("Execution time limit exceeded")

                old_alarm_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(self.MAX_EXECUTION_TIME_SECONDS)
            except (AttributeError, ValueError):
                # Windows: threading.Timer 대체 사용
                def timeout_callback():
                    raise TimeoutError("Execution time limit exceeded (Windows)")

                timeout_timer = threading.Timer(
                    self.MAX_EXECUTION_TIME_SECONDS, timeout_callback
                )
                timeout_timer.daemon = True
                timeout_timer.start()

            # 메모리 제한 (UNIX 시스템만)
            try:
                soft, hard = resource.getrlimit(resource.RLIMIT_AS)
                old_memory_limit = (soft, hard)

                new_limit = self.MAX_MEMORY_MB * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (new_limit, new_limit))
            except (AttributeError, ValueError, OSError):
                # Windows 등 resource 미지원 시스템
                # psutil로 메모리 모니터링 (선택적)
                pass

            yield

        finally:
            # 리소스 제한 복원
            if old_recursion_limit is not None:
                import sys

                sys.setrecursionlimit(old_recursion_limit)

            if old_alarm_handler is not None:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_alarm_handler)

            if timeout_timer is not None:
                timeout_timer.cancel()

            if old_memory_limit is not None:
                try:
                    resource.setrlimit(resource.RLIMIT_AS, old_memory_limit)
                except (AttributeError, ValueError, OSError):
                    pass

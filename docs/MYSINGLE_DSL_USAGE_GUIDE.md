# mysingle.dsl 모듈 완전 활용 가이드

**버전**: v1.3.0
**최종 업데이트**: 2025-11-15
**대상**: Indicator Service, Strategy Service 개발팀

---

## 📋 목차

1. [개요](#개요)
2. [아키텍처](#아키텍처)
3. [설치 및 설정](#설치-및-설정)
4. [핵심 컴포넌트](#핵심-컴포넌트)
5. [기본 사용법](#기본-사용법)
6. [고급 활용](#고급-활용)
7. [보안 및 제한](#보안-및-제한)
8. [표준 라이브러리](#표준-라이브러리)
9. [에러 처리](#에러-처리)
10. [성능 최적화](#성능-최적화)
11. [테스트 가이드](#테스트-가이드)
12. [FAQ](#faq)

---

## 🎯 개요

### mysingle.dsl이란?

**mysingle.dsl**은 MySingle Platform의 공통 DSL(Domain Specific Language) 런타임입니다. 사용자가 Python 코드로 지표(Indicator) 및 전략(Strategy) 로직을 작성할 수 있도록 **안전한 실행 환경**을 제공합니다.

### 주요 특징

- ✅ **RestrictedPython 기반**: 샌드박스 환경에서 안전한 코드 실행
- ✅ **보안 우선**: 파일 I/O, 네트워크, 동적 실행 차단
- ✅ **리소스 제한**: CPU 시간(30초), 메모리(512MB) 제한
- ✅ **표준 라이브러리**: SMA, EMA, crossover 등 60+ 함수
- ✅ **직렬화 지원**: 컴파일 결과를 바이트코드로 저장/재사용
- ✅ **파라미터화**: 동적 파라미터 전달 및 기본값 설정

### 사용 사례

| 서비스             | 용도                    | 입력                | 출력                     |
| ------------------ | ----------------------- | ------------------- | ------------------------ |
| **Indicator**      | 기술적 지표 계산        | OHLCV 데이터        | `pd.Series`, `DataFrame` |
| **Strategy**       | 매매 시그널 생성        | OHLCV + 계산된 지표 | `pd.Series[bool]`        |
| **Backtest**       | 백테스트 실행 (간접)    | 전략 DSL            | 성과 지표                |
| **Custom Scripts** | 사용자 정의 분석 (예정) | 임의 데이터         | 임의 결과                |

---

## 🏗️ 아키텍처

### 모듈 구조

```
mysingle.dsl/
├── __init__.py          # 패키지 진입점
├── parser.py            # DSL 코드 컴파일 (RestrictedPython)
├── validator.py         # 정적 분석 및 보안 검증
├── executor.py          # 안전한 코드 실행
├── stdlib.py            # 표준 라이브러리 함수
├── errors.py            # 예외 클래스 정의
└── limits.py            # 리소스 제한 및 할당량
```

### 실행 흐름

```
┌─────────────┐
│ 사용자 코드 │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ SecurityValidator│ ← 정적 분석 (금지된 import/builtin 검증)
└──────┬───────────┘
       │ ✅ 보안 통과
       ▼
┌──────────────┐
│  DSLParser   │ ← RestrictedPython 컴파일 → bytes
└──────┬───────┘
       │ compiled bytecode
       ▼
┌──────────────┐
│ DSLExecutor  │ ← 리소스 제한 + 안전한 네임스페이스
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    결과      │ (pd.Series, pd.DataFrame)
└──────────────┘
```

### 핵심 설계 원칙

1. **Security by Default**: 모든 코드는 샌드박스에서 실행
2. **Fail Fast**: 보안 위반은 컴파일 단계에서 차단
3. **Resource Bounded**: 실행 시간/메모리 제한으로 DoS 방지
4. **Serializable**: 컴파일 결과를 저장하여 재사용 가능
5. **Extensible**: 표준 라이브러리 확장 가능

---

## 📦 설치 및 설정

### 설치

```bash
# mysingle 패키지 설치
pip install mysingle

# 또는 전체 기능 설치
pip install mysingle[full]
```

### 환경 변수 설정

```bash
# .env 파일 또는 환경 변수
DSL_MAX_EXECUTION_TIME_SECONDS=30     # 최대 실행 시간 (초)
DSL_MAX_MEMORY_MB=512                 # 최대 메모리 (MB)
DSL_MAX_ITERATIONS=10000              # 최대 루프 반복
DSL_MAX_OUTPUT_SIZE_MB=10             # 최대 출력 크기 (MB)
DSL_MAX_RECURSION_DEPTH=100           # 최대 재귀 깊이

# 사용자 할당량 (선택)
USER_QUOTA_FREE_DAILY_CALCULATIONS=10000
USER_QUOTA_PREMIUM_DAILY_CALCULATIONS=100000
USER_QUOTA_RATE_LIMIT_PER_MINUTE=100
```

### Import

```python
# 기본 Import
from mysingle.dsl import DSLParser, DSLExecutor, SecurityValidator

# 에러 클래스
from mysingle.dsl import (
    DSLError,
    DSLCompilationError,
    DSLValidationError,
    DSLSecurityError,
    DSLExecutionError,
    DSLTimeoutError,
    DSLMemoryError,
)

# 설정
from mysingle.dsl import ResourceLimits, UserQuota

# 표준 라이브러리
from mysingle.dsl import get_stdlib_functions
```

---

## 🧩 핵심 컴포넌트

### 1. DSLParser - 코드 컴파일러

**역할**: Python 코드를 안전한 바이트코드로 컴파일

```python
from mysingle.dsl import DSLParser

parser = DSLParser()

# 컴파일 (bytes 반환)
code = """
result = data['close'] > data['SMA_50']
"""
compiled = parser.parse(code)  # bytes

# 바이트코드 로드
code_object = parser.load(compiled)  # CodeType

# 코드 해시 생성 (캐싱용)
code_hash = parser.get_code_hash(code)  # str (SHA-256)
```

**주요 메서드**:

| 메서드                 | 설명                       | 반환 타입  |
| ---------------------- | -------------------------- | ---------- |
| `parse(code)`          | DSL 코드 컴파일            | `bytes`    |
| `load(bytecode)`       | 바이트코드 → CodeType 변환 | `CodeType` |
| `get_code_hash(code)`  | 코드 해시 생성 (캐싱)      | `str`      |
| `get_safe_globals()`   | 안전한 글로벌 네임스페이스 | `dict`     |
| `_get_safe_builtins()` | 허용된 builtin 함수        | `dict`     |

**허용된 Builtin**:

```python
# 수학
abs, min, max, sum, round

# 시퀀스
len, list, dict, tuple, range, enumerate, zip

# 함수형
map, filter, sorted

# 타입 변환
int, float, str, bool

# 예외
ValueError, TypeError, IndexError, KeyError, AttributeError

# 기타
isinstance, hasattr, getattr
```

---

### 2. SecurityValidator - 보안 검증기

**역할**: AST 기반 정적 분석으로 보안 위반 탐지

```python
from mysingle.dsl import SecurityValidator

validator = SecurityValidator()

# 코드 검증
code = """
import os  # ❌ 금지된 import
result = data['close']
"""

is_valid, violations = validator.validate(code)

if not is_valid:
    for v in violations:
        print(f"{v.level}: {v.message} (line {v.line})")
    # ERROR: Forbidden import: os (line 2)
```

**주요 메서드**:

| 메서드            | 설명                     | 반환 타입                         |
| ----------------- | ------------------------ | --------------------------------- |
| `validate(code)`  | 코드 검증 (종합)         | `(bool, list[SecurityViolation])` |
| `analyze(code)`   | 정적 분석만 수행         | `list[SecurityViolation]`         |
| `has_errors(...)` | 에러 레벨 위반 존재 여부 | `bool`                            |
| `format_report()` | 보안 보고서 텍스트 생성  | `str`                             |

**금지된 Import**:

```python
# 파일 I/O
os, sys, io, pathlib, shutil, tempfile

# 네트워크
socket, urllib, requests, httpx, aiohttp

# 시스템
subprocess, multiprocessing, threading

# 동적 실행
pickle, marshal, shelve, importlib

# 기타
ctypes, gc, inspect, code
```

**금지된 Builtin**:

```python
# 파일/입출력
open, input, print

# 동적 실행
eval, exec, compile, __import__

# 리플렉션
globals, locals, vars, dir

# 속성 조작
delattr, setattr

# 기타
help, breakpoint, exit, quit
```

**금지된 속성 접근**:

```python
__class__, __bases__, __subclasses__
__globals__, __code__, __closure__
__dict__, __module__
```

---

### 3. DSLExecutor - 코드 실행 엔진

**역할**: 리소스 제한과 함께 안전하게 코드 실행

```python
from mysingle.dsl import DSLExecutor, DSLParser
import pandas as pd

parser = DSLParser()
executor = DSLExecutor(parser)

# 데이터 준비
data = pd.DataFrame({
    'close': [100, 101, 102, 103, 104],
    'SMA_50': [99, 100, 101, 102, 103],
    'volume': [1000, 1500, 2000, 1800, 1200]
})

# 코드 컴파일
code = """
threshold = params.get('threshold', 100)
result = data['close'] > threshold
"""
compiled = parser.parse(code)

# 실행
result = executor.execute(
    compiled,
    data,
    params={'threshold': 102}
)

print(result)
# 0    False
# 1    False
# 2    False
# 3     True
# 4     True
```

**주요 메서드**:

| 메서드                            | 설명                   | 반환 타입                |
| --------------------------------- | ---------------------- | ------------------------ |
| `execute(compiled, data, params)` | 컴파일된 코드 실행     | `pd.Series \| DataFrame` |
| `compile_and_execute(code, ...)`  | 컴파일 + 실행 (원스텝) | `pd.Series \| DataFrame` |
| `_build_namespace(data, params)`  | 네임스페이스 구성      | `dict`                   |
| `_resource_limits()`              | 리소스 제한 적용       | `ContextManager`         |

**네임스페이스 구성**:

```python
namespace = {
    # 라이브러리
    'np': numpy,
    'pd': pandas,

    # 데이터
    'data': pd.DataFrame,      # OHLCV + 계산된 지표
    'params': dict,            # 파라미터 딕셔너리 ✨ v1.3.0

    # 파라미터 개별 주입 (하위 호환)
    'threshold': params.get('threshold'),
    'window': params.get('window'),

    # 표준 라이브러리 함수
    'SMA': function,
    'EMA': function,
    'crossover': function,
    # ... (60+ 함수)
}
```

**리소스 제한**:

| 항목               | 기본값 | 환경 변수                         |
| ------------------ | ------ | --------------------------------- |
| **최대 실행 시간** | 30초   | `DSL_MAX_EXECUTION_TIME_SECONDS`  |
| **최대 메모리**    | 512MB  | `DSL_MAX_MEMORY_MB`               |
| **최대 재귀 깊이** | 100    | `DSL_MAX_RECURSION_DEPTH`         |
| **최대 루프 반복** | 10,000 | `DSL_MAX_ITERATIONS` (미구현)     |
| **최대 출력 크기** | 10MB   | `DSL_MAX_OUTPUT_SIZE_MB` (미구현) |

---

## 🚀 기본 사용법

### 1. 간단한 예제 (Indicator Service)

```python
from mysingle.dsl import DSLParser, DSLExecutor, SecurityValidator
from mysingle.dsl.errors import DSLSecurityError, DSLCompilationError
import pandas as pd

# 1. 초기화
parser = DSLParser()
validator = SecurityValidator()
executor = DSLExecutor(parser)

# 2. 사용자 코드
code = """
# 이동평균 크로스오버
fast_ma = SMA(data['close'], 10)
slow_ma = SMA(data['close'], 20)
result = crossover(fast_ma, slow_ma)
"""

# 3. 보안 검증
is_valid, violations = validator.validate(code)
if not is_valid:
    errors = [v for v in violations if v.level == "ERROR"]
    raise DSLSecurityError(f"Security violations: {errors}")

# 4. 컴파일
try:
    compiled = parser.parse(code)
except DSLCompilationError as e:
    print(f"Compilation failed: {e}")
    raise

# 5. 실행
data = pd.DataFrame({
    'close': [100, 101, 99, 102, 105, 103, 107, 110, 108, 112],
})

result = executor.execute(compiled, data, params={})

print(result)
# 크로스오버 시점에서 True
```

### 2. 파라미터 활용 (Strategy Service)

```python
# 전략 코드 (params 사용)
code = """
# RSI 과매도 전략
rsi = data['RSI_14']
threshold = params.get('rsi_threshold', 30)  # 기본값 30

# 거래량 필터
min_volume = params['min_volume']
volume_filter = data['volume'] > min_volume

# 최종 시그널
oversold = rsi < threshold
result = oversold & volume_filter
"""

# 컴파일
compiled = parser.parse(code)

# 데이터 준비
data = pd.DataFrame({
    'RSI_14': [35, 28, 25, 32, 45],
    'volume': [1000, 1500, 2000, 1800, 1200]
})

# 실행 (파라미터 전달)
result = executor.execute(
    compiled,
    data,
    params={
        'rsi_threshold': 30,
        'min_volume': 1500
    }
)

print(result)
# 0    False  # RSI 35 > 30
# 1    False  # RSI 28 < 30, volume 1500 (경계값)
# 2     True  # RSI 25 < 30, volume 2000 > 1500
# 3    False  # RSI 32 > 30
# 4    False  # RSI 45 > 30
```

### 3. 바이트코드 직렬화 (v1.3.0)

```python
import base64

# 컴파일
code = """
result = data['close'] > data['SMA_50']
"""
compiled = parser.parse(code)  # bytes

# 직렬화 (API 응답, DB 저장)
encoded = base64.b64encode(compiled).decode()
print(f"Serialized: {encoded[:50]}...")

# --- 나중에 재사용 ---

# 역직렬화
decoded = base64.b64decode(encoded)

# 재컴파일 없이 실행
result = executor.execute(decoded, data, params={})
```

---

## 🎓 고급 활용

### 1. 컴파일 캐싱

```python
import hashlib
from typing import Dict

class CachedDSLService:
    """컴파일 결과 캐싱 서비스"""

    def __init__(self):
        self.parser = DSLParser()
        self.executor = DSLExecutor(self.parser)
        self._cache: Dict[str, bytes] = {}

    def compile_or_cache(self, code: str) -> bytes:
        """코드 해시 기반 캐싱"""
        code_hash = self.parser.get_code_hash(code)

        if code_hash not in self._cache:
            compiled = self.parser.parse(code)
            self._cache[code_hash] = compiled

        return self._cache[code_hash]

    def execute(self, code: str, data, params):
        """캐싱된 컴파일 결과로 실행"""
        compiled = self.compile_or_cache(code)
        return self.executor.execute(compiled, data, params)

# 사용
service = CachedDSLService()

# 첫 실행 (컴파일)
result1 = service.execute(code, data1, params)

# 두 번째 실행 (캐시 사용)
result2 = service.execute(code, data2, params)  # ⚡ 빠름
```

### 2. 전략 특화 함수 활용 (v1.3.0)

```python
# generate_signal() - 명시적 타입 변환
code = """
oversold = data['RSI'] < 30
buy_signal = generate_signal(oversold, signal_type="long")
result = buy_signal
"""

# entry_exit_signals() - 진입/청산 페어
code = """
entry = crossover(data['SMA_50'], data['SMA_200'])
exit = crossunder(data['SMA_50'], data['SMA_200'])
signals = entry_exit_signals(entry, exit)
result = signals['entry']  # 진입 시그널만 반환
"""

# signal_filter() - 시그널 필터링
code = """
# 기본 시그널
rsi_signal = data['RSI'] < 30

# 거래량 필터
avg_volume = data['volume'].rolling(20).mean()
high_volume = data['volume'] > avg_volume * 1.5

# 필터링된 시그널
result = signal_filter(rsi_signal, high_volume)
"""
```

### 3. 복잡한 전략 패턴

```python
# 다중 조건 결합
code = """
# 1. 추세 확인
sma_50 = data['SMA_50']
sma_200 = data['SMA_200']
uptrend = sma_50 > sma_200

# 2. 모멘텀 확인
rsi = data['RSI_14']
oversold = (rsi > 30) & (rsi < 50)  # 반등 구간

# 3. 변동성 확인
atr = data['ATR_14']
high_volatility = atr > atr.rolling(50).mean() * 1.2

# 4. 거래량 확인
volume_spike = data['volume'] > data['volume'].rolling(20).mean() * 2

# 5. 모든 조건 결합
entry_conditions = uptrend & oversold & high_volatility & volume_spike

# 6. 최종 시그널
result = generate_signal(entry_conditions, signal_type="long")
"""
```

### 4. 에러 처리 패턴

```python
from mysingle.dsl.errors import (
    DSLCompilationError,
    DSLValidationError,
    DSLExecutionError,
    DSLTimeoutError,
    DSLMemoryError
)

def safe_execute(code: str, data, params):
    """안전한 DSL 실행 (에러 처리 포함)"""

    try:
        # 1. 검증
        is_valid, violations = validator.validate(code)
        if not is_valid:
            error_msgs = [v.message for v in violations if v.level == "ERROR"]
            raise DSLValidationError(f"Validation failed: {error_msgs}")

        # 2. 컴파일
        compiled = parser.parse(code)

        # 3. 실행
        result = executor.execute(compiled, data, params)

        return {"success": True, "result": result.tolist()}

    except DSLCompilationError as e:
        return {"success": False, "error": "compilation_error", "detail": str(e)}

    except DSLValidationError as e:
        return {"success": False, "error": "validation_error", "detail": str(e)}

    except DSLTimeoutError as e:
        return {"success": False, "error": "timeout", "detail": "Execution exceeded 30s"}

    except DSLMemoryError as e:
        return {"success": False, "error": "memory_limit", "detail": "Exceeded 512MB"}

    except DSLExecutionError as e:
        return {"success": False, "error": "execution_error", "detail": str(e)}

    except Exception as e:
        return {"success": False, "error": "unknown", "detail": str(e)}
```

---

## 🔒 보안 및 제한

### 보안 정책

#### 1. 금지된 연산

```python
# ❌ 파일 I/O
import os
with open('file.txt') as f:
    pass

# ❌ 네트워크
import requests
requests.get('http://example.com')

# ❌ 동적 실행
eval("1 + 1")
exec("x = 1")

# ❌ 시스템 접근
import subprocess
subprocess.run(['ls'])

# ❌ 리플렉션
globals()
locals()
```

#### 2. 허용된 연산

```python
# ✅ 산술 연산
result = (data['close'] - data['open']) / data['open']

# ✅ 논리 연산
result = (data['RSI'] < 30) & (data['volume'] > 1000000)

# ✅ pandas/numpy 연산
result = data['close'].rolling(10).mean()

# ✅ stdlib 함수
result = crossover(data['SMA_50'], data['SMA_200'])

# ✅ 조건 분기
result = data['close'] > 100 if condition else False
```

### 리소스 제한

#### CPU 시간 제한

```python
# 30초 제한
try:
    result = executor.execute(compiled, data, params)
except DSLTimeoutError:
    print("실행 시간 초과")
```

#### 메모리 제한

```python
# 512MB 제한
try:
    result = executor.execute(compiled, data, params)
except DSLMemoryError:
    print("메모리 제한 초과")
```

#### 재귀 깊이 제한

```python
# 100 레벨 제한
# 재귀 함수는 사용 가능하지만 깊이 제한됨
def recursive_func(n):
    if n > 100:  # RecursionError
        return recursive_func(n + 1)
```

### 할당량 관리

```python
from mysingle.dsl.limits import (
    get_user_daily_limit,
    get_user_max_indicators,
    resource_limits,
    user_quota
)

# 사용자 티어별 제한 조회
free_daily = get_user_daily_limit(is_premium=False)      # 10,000
premium_daily = get_user_daily_limit(is_premium=True)    # 100,000

# 리소스 제한 조회
max_time = resource_limits.MAX_EXECUTION_TIME_SECONDS    # 30
max_memory = resource_limits.MAX_MEMORY_MB               # 512

# Rate Limiting
rate_limit = user_quota.RATE_LIMIT_PER_MINUTE            # 100
```

---

## 📚 표준 라이브러리

### 이동평균 함수

#### SMA - Simple Moving Average

```python
SMA(series: pd.Series, window: int) -> pd.Series
```

**예제**:
```python
sma_20 = SMA(data['close'], 20)
sma_50 = SMA(data['close'], 50)
golden_cross = crossover(sma_20, sma_50)
```

#### EMA - Exponential Moving Average

```python
EMA(series: pd.Series, span: int) -> pd.Series
```

**예제**:
```python
ema_12 = EMA(data['close'], 12)
ema_26 = EMA(data['close'], 26)
macd_line = ema_12 - ema_26
```

#### WMA - Weighted Moving Average

```python
WMA(series: pd.Series, window: int) -> pd.Series
```

### 크로스오버 함수

#### crossover - 상향 돌파

```python
crossover(series1: pd.Series, series2: pd.Series) -> pd.Series
```

**예제**:
```python
# Golden Cross
golden = crossover(data['SMA_50'], data['SMA_200'])

# MACD 크로스
macd_cross = crossover(data['MACD_line'], data['MACD_signal'])
```

#### crossunder - 하향 돌파

```python
crossunder(series1: pd.Series, series2: pd.Series) -> pd.Series
```

**예제**:
```python
# Death Cross
death = crossunder(data['SMA_50'], data['SMA_200'])
```

### 최고/최저 함수

#### highest - N일 최고값

```python
highest(series: pd.Series, window: int) -> pd.Series
```

**예제**:
```python
high_20 = highest(data['high'], 20)
breakout = data['close'] > high_20.shift(1)
```

#### lowest - N일 최저값

```python
lowest(series: pd.Series, window: int) -> pd.Series
```

### 변화율 함수

#### change - 절대 변화량

```python
change(series: pd.Series, periods: int = 1) -> pd.Series
```

#### pct_change - 백분율 변화량

```python
pct_change(series: pd.Series, periods: int = 1) -> pd.Series
```

### 변동성 함수

#### stdev - 표준편차

```python
stdev(series: pd.Series, window: int) -> pd.Series
```

#### bbands - Bollinger Bands

```python
bbands(series: pd.Series, window: int = 20, num_std: float = 2.0) -> pd.DataFrame
```

**반환**: `{'upper': ..., 'middle': ..., 'lower': ...}`

**예제**:
```python
bands = bbands(data['close'], 20, 2.0)
oversold = data['close'] < bands['lower']
overbought = data['close'] > bands['upper']
```

#### atr - Average True Range

```python
atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series
```

### 전략 특화 함수 (v1.3.0)

#### generate_signal - 시그널 생성

```python
generate_signal(condition: pd.Series, signal_type: Literal["long", "short"] = "long") -> pd.Series
```

**예제**:
```python
oversold = data['RSI'] < 30
buy_signal = generate_signal(oversold, signal_type="long")
```

#### entry_exit_signals - 진입/청산 페어

```python
entry_exit_signals(entry_condition: pd.Series, exit_condition: pd.Series) -> pd.DataFrame
```

**반환**: `{'entry': ..., 'exit': ...}`

**예제**:
```python
entry = crossover(data['SMA_50'], data['SMA_200'])
exit = crossunder(data['SMA_50'], data['SMA_200'])
signals = entry_exit_signals(entry, exit)
```

#### signal_filter - 시그널 필터링

```python
signal_filter(signals: pd.Series, filter_condition: pd.Series) -> pd.Series
```

**예제**:
```python
rsi_signal = data['RSI'] < 30
high_volume = data['volume'] > data['volume'].rolling(20).mean() * 1.5
filtered = signal_filter(rsi_signal, high_volume)
```

### 전체 함수 목록

```python
from mysingle.dsl import get_stdlib_functions

stdlib = get_stdlib_functions()
print(list(stdlib.keys()))
# ['SMA', 'EMA', 'WMA', 'crossover', 'crossunder',
#  'highest', 'lowest', 'change', 'pct_change',
#  'stdev', 'bbands', 'atr',
#  'generate_signal', 'entry_exit_signals', 'signal_filter']
```

---

## ⚠️ 에러 처리

### 에러 계층 구조

```
DSLError (기본 예외)
├── DSLCompilationError      # 컴파일 실패
├── DSLValidationError       # 검증 실패
│   └── DSLSecurityError     # 보안 위반
└── DSLExecutionError        # 실행 에러
    ├── DSLTimeoutError      # 시간 초과
    └── DSLMemoryError       # 메모리 초과
```

### 에러별 처리 방법

#### 1. DSLCompilationError

**원인**: 문법 오류

```python
# ❌ 잘못된 코드
code = "result = data['close' > 100"  # 괄호 누락

try:
    compiled = parser.parse(code)
except DSLCompilationError as e:
    print(f"Syntax error: {e}")
    # "Syntax error: ..."
```

**해결**: 문법 수정

#### 2. DSLSecurityError

**원인**: 금지된 import, builtin 사용

```python
# ❌ 보안 위반
code = """
import os
result = data['close']
"""

is_valid, violations = validator.validate(code)
if not is_valid:
    for v in violations:
        print(v)
    # [ERROR] (line 2) Forbidden import: os
```

**해결**: 금지된 연산 제거

#### 3. DSLExecutionError

**원인**: 실행 중 에러

```python
# ❌ result 변수 누락
code = """
signal = data['RSI'] < 30
# result 할당 없음
"""

try:
    result = executor.execute(compiled, data, params)
except DSLExecutionError as e:
    print(e)
    # "Variable 'result' not found"
```

**해결**: `result` 변수 할당

#### 4. DSLTimeoutError

**원인**: 실행 시간 초과 (30초)

```python
# ❌ 무한 루프
code = """
while True:
    pass
result = data['close']
"""

try:
    result = executor.execute(compiled, data, params)
except DSLTimeoutError as e:
    print("Execution timeout")
```

**해결**: 알고리즘 최적화, 루프 제거

#### 5. DSLMemoryError

**원인**: 메모리 제한 초과 (512MB)

```python
# ❌ 대용량 데이터 생성
code = """
huge_array = [0] * 100_000_000
result = data['close']
"""

try:
    result = executor.execute(compiled, data, params)
except DSLMemoryError as e:
    print("Memory limit exceeded")
```

**해결**: 데이터 크기 축소, 벡터화 연산 사용

---

## ⚡ 성능 최적화

### 1. 벡터화 연산 사용

```python
# ❌ 느린 방법: 루프
result = pd.Series([False] * len(data))
for i in range(len(data)):
    if data['RSI'].iloc[i] < 30:
        result.iloc[i] = True

# ✅ 빠른 방법: 벡터화
result = data['RSI'] < 30
```

**성능 차이**: 벡터화는 **100~1000배 빠름**

### 2. 불필요한 계산 제거

```python
# ❌ 중복 계산
result = (SMA(data['close'], 50) > SMA(data['close'], 200)) & \
         (SMA(data['close'], 50) > data['close'])

# ✅ 변수 재사용
sma_50 = SMA(data['close'], 50)
sma_200 = SMA(data['close'], 200)
result = (sma_50 > sma_200) & (sma_50 > data['close'])
```

### 3. 조기 반환 (필터 순서)

```python
# ❌ 무거운 계산 먼저
rsi_signal = data['RSI'] < 30  # 가벼움
ma_cross = crossover(data['SMA_50'], data['SMA_200'])  # 무거움
volume_filter = data['volume'] > 1000000  # 가벼움

result = rsi_signal & ma_cross & volume_filter

# ✅ 가벼운 필터 먼저 적용
volume_filter = data['volume'] > 1000000
if not volume_filter.any():  # 어차피 결과 없음
    result = pd.Series([False] * len(data))
else:
    rsi_signal = data['RSI'] < 30
    ma_cross = crossover(data['SMA_50'], data['SMA_200'])
    result = rsi_signal & ma_cross & volume_filter
```

### 4. 컴파일 캐싱

```python
# 동일한 코드는 한 번만 컴파일
cache = {}

def get_compiled(code: str):
    code_hash = parser.get_code_hash(code)
    if code_hash not in cache:
        cache[code_hash] = parser.parse(code)
    return cache[code_hash]

# 사용
compiled = get_compiled(strategy_code)
result = executor.execute(compiled, data, params)
```

### 5. 데이터 크기 최소화

```python
# ✅ 필요한 컬럼만 전달
needed_columns = ['close', 'RSI_14', 'SMA_50', 'volume']
data_subset = data[needed_columns]

result = executor.execute(compiled, data_subset, params)
```

---

## 🧪 테스트 가이드

### 단위 테스트 예제

```python
import pytest
import pandas as pd
from mysingle.dsl import DSLParser, DSLExecutor, SecurityValidator

@pytest.fixture
def parser():
    return DSLParser()

@pytest.fixture
def executor(parser):
    return DSLExecutor(parser)

@pytest.fixture
def validator():
    return SecurityValidator()

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'close': [100, 101, 102, 103, 104],
        'RSI_14': [35, 28, 25, 32, 45],
        'SMA_50': [99, 100, 101, 102, 103],
        'volume': [1000, 1500, 2000, 1800, 1200]
    })

def test_simple_comparison(executor, sample_data):
    """간단한 비교 연산 테스트"""
    code = "result = data['close'] > 100"
    compiled = executor.parser.parse(code)
    result = executor.execute(compiled, sample_data, {})

    assert isinstance(result, pd.Series)
    assert result.iloc[0] == False  # 100 > 100
    assert result.iloc[1] == True   # 101 > 100

def test_params_access(executor, sample_data):
    """params 딕셔너리 접근 테스트"""
    code = """
threshold = params['threshold']
result = data['RSI_14'] < threshold
"""
    compiled = executor.parser.parse(code)
    result = executor.execute(compiled, sample_data, {'threshold': 30})

    assert result.iloc[1] == True   # 28 < 30
    assert result.iloc[0] == False  # 35 < 30

def test_security_violation(validator):
    """보안 위반 검증 테스트"""
    code = """
import os
result = data['close']
"""
    is_valid, violations = validator.validate(code)

    assert not is_valid
    assert len(violations) > 0
    assert violations[0].level == "ERROR"

def test_stdlib_function(executor, sample_data):
    """stdlib 함수 테스트"""
    code = """
fast = SMA(data['close'], 2)
slow = SMA(data['close'], 3)
result = crossover(fast, slow)
"""
    compiled = executor.parser.parse(code)
    result = executor.execute(compiled, sample_data, {})

    assert isinstance(result, pd.Series)
    assert result.dtype == bool
```

### 통합 테스트 예제

```python
def test_full_pipeline(parser, validator, executor, sample_data):
    """전체 파이프라인 테스트"""
    code = """
# RSI 과매도 + Golden Cross
rsi = data['RSI_14']
fast_ma = data['SMA_50']

threshold = params.get('threshold', 30)
oversold = rsi < threshold

result = oversold
"""
    # 1. 검증
    is_valid, violations = validator.validate(code)
    assert is_valid

    # 2. 컴파일
    compiled = parser.parse(code)
    assert isinstance(compiled, bytes)

    # 3. 실행
    result = executor.execute(compiled, sample_data, {'threshold': 30})
    assert isinstance(result, pd.Series)
    assert result.dtype == bool
```

### 성능 테스트

```python
import time

def test_execution_performance(executor):
    """실행 성능 테스트 (< 1초)"""
    # 대용량 데이터 (1년 일봉)
    data = pd.DataFrame({
        'close': np.random.uniform(90, 110, 252),
        'RSI_14': np.random.uniform(20, 80, 252),
    })

    code = "result = data['RSI_14'] < 30"
    compiled = executor.parser.parse(code)

    start = time.time()
    result = executor.execute(compiled, data, {})
    elapsed = time.time() - start

    assert elapsed < 1.0
```

---

## ❓ FAQ

### Q1. params 딕셔너리와 개별 변수 주입의 차이는?

**A**: 둘 다 지원됩니다 (v1.3.0부터).

```python
# 방법 1: params 딕셔너리
threshold = params['threshold']
window = params.get('window', 20)

# 방법 2: 개별 변수 (하위 호환)
result = data['RSI'] < threshold  # threshold가 자동 주입됨
```

둘 다 작동하지만, **params 딕셔너리 방식**을 권장합니다 (명시적).

### Q2. 컴파일 결과를 DB에 저장할 수 있나요?

**A**: 가능합니다 (v1.3.0부터).

```python
# 컴파일 및 저장
compiled = parser.parse(code)  # bytes
stored = base64.b64encode(compiled).decode()  # str

# DB에 저장
db.save(strategy_id, stored)

# 나중에 로드
loaded = db.load(strategy_id)
bytecode = base64.b64decode(loaded)
result = executor.execute(bytecode, data, params)
```

### Q3. 여러 타임프레임을 동시에 사용할 수 있나요?

**A**: Phase 1에서는 **단일 타임프레임만** 지원됩니다. Phase 2에서 다중 타임프레임 지원 예정입니다.

### Q4. 실시간 데이터를 사용할 수 있나요?

**A**: 가능합니다. DSL은 백테스트와 라이브 트레이딩 모두 지원합니다.

**차이점**:
- 백테스트: 전체 데이터 (`data`는 전체 DataFrame)
- 라이브: 최신 N개 행만 포함

### Q5. 상태를 저장할 수 있나요?

**A**: Phase 1에서는 **불가능**합니다 (순수 함수). Phase 3에서 상태 관리 지원 예정입니다.

### Q6. print()로 디버깅할 수 있나요?

**A**: `print()`는 보안상 금지됩니다. 대신:

```python
# 테스트 환경에서 assert 사용
rsi_signal = data['RSI'] < 30
assert rsi_signal.sum() > 0, "No RSI signals found"
```

### Q7. pandas 외 다른 라이브러리를 쓸 수 있나요?

**A**: **numpy**만 제한적으로 사용 가능합니다.

```python
# ✅ numpy 사용 가능 (자동 주입)
result = data['close'] > np.mean(data['close'])

# ❌ 다른 라이브러리 불가
import talib  # ERROR: Forbidden import
```

### Q8. 에러 발생 시 어떻게 되나요?

**A**: 에러 타입에 따라 다릅니다:

| 에러                  | 처리                     |
| --------------------- | ------------------------ |
| `DSLCompilationError` | 전략 저장 실패           |
| `DSLSecurityError`    | 전략 거부                |
| `DSLExecutionError`   | 백테스트 중단, 로그 기록 |
| `DSLTimeoutError`     | 백테스트 중단            |
| `DSLMemoryError`      | 백테스트 중단            |

---

## 📖 참고 문서

### 내부 문서
- [DSL_REQUIREMENTS_FOR_MYSINGLE.md](./DSL_REQUIREMENTS_FOR_MYSINGLE.md) - 요구사항
- [DSL_UPGRADE_SUMMARY_v1.3.0.md](./DSL_UPGRADE_SUMMARY_v1.3.0.md) - 업그레이드 내역
- [CHANGELOG_DSL_v1.3.0.md](./CHANGELOG_DSL_v1.3.0.md) - 변경 로그
- [STRATEGY_DSL_GUIDE.md](../services/strategy-service/docs/dsl_strategy/STRATEGY_DSL_GUIDE.md) - Strategy Service 가이드

### 외부 참고
- [RestrictedPython 문서](https://restrictedpython.readthedocs.io/)
- [pandas 문서](https://pandas.pydata.org/docs/)
- [numpy 문서](https://numpy.org/doc/)

### 예제 코드
- `tests/test_dsl_params_namespace.py` - params 네임스페이스 예제
- `tests/test_dsl_strategy_functions.py` - 전략 함수 예제
- `tests/test_dsl_serialization.py` - 직렬화 예제

---

## 🔄 버전 히스토리

### v1.3.0 (2025-11-15) - 현재 버전

**추가**:
- ✅ params 네임스페이스 지원
- ✅ 전략 특화 stdlib 함수 (generate_signal, entry_exit_signals, signal_filter)
- ✅ 바이트코드 직렬화 (marshal 기반)
- ✅ DSLParser.load() 메서드

**변경**:
- DSLParser.parse() 반환 타입: `CodeType` → `bytes`
- DSLExecutor.execute() 파라미터: `bytes | CodeType` 지원

**테스트**:
- 22개 신규 테스트 추가 (100% 통과)

### v1.2.x - 이전 버전

- RestrictedPython 기반 DSL 런타임
- SecurityValidator, DSLExecutor
- 표준 라이브러리 함수 (SMA, EMA 등)

---

## 📞 문의 및 지원

**패키지 관리자**: mysingle 패키지 개발팀
**이슈 보고**: GitHub Issues
**문서 업데이트 요청**: Pull Request

---

**작성일**: 2025-11-15
**버전**: v1.3.0
**작성자**: GitHub Copilot

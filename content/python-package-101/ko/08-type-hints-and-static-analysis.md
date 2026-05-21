---
title: "Python Package 101 (8/10): 타입 힌트와 정적 검사"
series: python-package-101
episode: 8
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- Python
- Type Hints
- mypy
- py.typed
- Static Analysis
- Typing
last_reviewed: '2026-05-15'
seo_description: 타입 힌트는 함수의 입력과 출력 타입을 명시하는 것이고, mypy는 코드를 실행하지 않고 타입 오류를 찾아주는 도구입니다.
---

# Python Package 101 (8/10): 타입 힌트와 정적 검사

패키지를 다른 사람이 쓰는 순간부터 “이 함수에는 무엇을 넘겨야 하나”, “반환값은 어떤 구조인가” 같은 질문이 생깁니다. 타입 힌트는 이 질문에 코드 수준에서 답하게 해 주고, 정적 분석기는 실행 전에 실수를 잡아 줍니다.

이 글은 Python Package 101 시리즈의 8번째 글입니다. 여기서는 타입 힌트의 기본 문법, `mypy` 검사 흐름, `py.typed` 마커 파일의 의미를 정리하겠습니다.

## 먼저 던지는 질문

- 타입 힌트는 왜 필요하고 런타임에 영향을 줄까요?
- `mypy`는 어떤 오류를 잡아 줄까요?
- `py.typed` 마커 파일은 왜 필요할까요?

## 큰 그림

![Python Package 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/08/08-01-mental-model.ko.png)

*Python Package 101 8장 흐름 개요*

## 이 글에서 배우는 내용

- 함수, 변수, 반환값에 타입 힌트를 추가하는 방법
- `mypy`로 정적 타입 검사를 실행하는 방법
- `py.typed`로 타입 정보를 패키지와 함께 배포하는 방법
- Generic, Union, Optional 같은 고급 타입 사용법

## 왜 중요한가

Python은 동적 타입 언어이기 때문에 작은 프로젝트에서는 자유롭게 느껴집니다. 하지만 코드가 커질수록 “이 함수에 무엇을 넘겨야 하지?”를 코드만 보고 즉시 판단하기 어려워집니다. 타입 힌트는 IDE 자동완성과 정적 분석을 가능하게 하고, `mypy`는 실행 전 단계에서 오류를 먼저 알려 줍니다.

> 함수가 dict를 반환하지만 어떤 키가 들어 있는지 문서가 없다고 가정해 보겠습니다. 호출하는 쪽에서는 `result["username"]`을 썼는데, 실제 키는 `result["user_name"]`이었습니다. 결국 런타임 `KeyError`가 운영에서 터집니다.

## 멘탈 모델

타입 힌트는 택배 상자에 붙인 라벨과 비슷합니다. 상자에 “깨지기 쉬움”이라고 적혀 있으면 운송 과정에서 주의를 기울일 수 있듯이, 타입 라벨이 있으면 `mypy`와 IDE가 코드를 더 정확하게 읽어 냅니다.

```text
def greet(name: str) -> str:
         ↑ input label    ↑ output label

mypy checks:
  greet(42)    # Error: expected str, got int
  x: int = greet("Alice")  # Error: str assigned to int
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| type hint | 변수/인자/반환값에 붙는 타입 주석 | `name: str` |
| mypy | Python 정적 타입 검사기 | `mypy src/` |
| py.typed | 패키지가 타입 힌트를 포함함을 알리는 마커 | 빈 파일 |
| Generic | 다른 타입을 매개변수로 받는 타입 | `list[str]`, `dict[str, int]` |
| Union | 여러 타입 중 하나 | `str \| None` |

## Before / After

**Before (no type hints)**

```python
def process(data):
    # What is data? dict? list? str?
    return data["name"]  # possible KeyError

result = process({"username": "alice"})  # runtime error
```

**After (type hints + mypy)**

```python
from typing import TypedDict

class UserData(TypedDict):
    name: str
    age: int

def process(data: UserData) -> str:
    return data["name"]

result = process({"username": "alice"})  # mypy catches this before runtime
```

## 단계별 실습

### Step 1. 기본 타입 힌트 추가

```python
# src/mylib/core.py
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

def find_user(user_id: int) -> dict[str, str] | None:
    users = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
    return users.get(user_id)
```

### Step 2. `mypy` 설치와 실행

```bash
pip install mypy
mypy src/
# Success: no issues found in 2 source files
```

```python
# Add an intentional error
result: int = greet("Alice")  # assigning str to int
```

```bash
mypy src/
# error: Incompatible types in assignment
#   (expression has type "str", variable has type "int")
```

### Step 3. `pyproject.toml`에 `mypy` 설정 추가

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

```bash
mypy src/
```

### Step 4. `py.typed` 마커 추가

```bash
touch src/mylib/py.typed
```

```toml
# Include in pyproject.toml
[tool.setuptools.package-data]
mylib = ["py.typed"]
```

### Step 5. 고급 타입 활용

```python
# src/mylib/utils.py
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

def retry(func: Callable[..., T], attempts: int = 3) -> T | None:
    """Retry a function up to N times."""
    for i in range(attempts):
        try:
            return func()
        except Exception:
            if i == attempts - 1:
                return None
    return None

# Usage
def fetch_data() -> dict[str, str]:
    return {"key": "value"}

result = retry(fetch_data)  # mypy: dict[str, str] | None
```

## 이 코드에서 눈여겨볼 점

- 타입 힌트는 런타임 동작을 바꾸지 않고, `mypy`나 IDE 같은 도구를 위해 존재합니다.
- `py.typed`가 있으면 이 패키지에 의존하는 프로젝트도 타입 정보를 활용할 수 있습니다.
- `strict = true`는 새 프로젝트에서 시작하기 좋은 강한 검사 모드입니다.
- Python 3.10+에서는 `Optional[X]` 대신 `X | None` 문법을 자연스럽게 쓸 수 있습니다.

## 자주 하는 실수

### 실수 1. `Any`를 남용한다

```python
from typing import Any
def process(data: Any) -> Any:  # type hints become meaningless
    ...
```

구체적인 타입을 쓸 수 있다면 최대한 구체적으로 적는 편이 좋습니다. `dict[str, Any]`라도 bare `Any`보다는 낫습니다.

### 실수 2. `py.typed`를 만들고도 빌드에 포함하지 않는다

파일만 만든다고 끝나지 않습니다. `[tool.setuptools.package-data]`에 추가하지 않으면 wheel 안에 들어가지 않습니다.

### 실수 3. 기존 대규모 코드베이스에 strict 모드를 한 번에 적용한다

에러가 너무 많아져 팀이 금방 포기할 수 있습니다. 기존 프로젝트는 `--disallow-untyped-defs` 같은 옵션부터 점진적으로 도입하는 편이 현실적입니다.

### 실수 4. 타입 힌트가 런타임 검증까지 해 준다고 오해한다

```python
def greet(name: str) -> str: ...
greet(42)  # runs fine at runtime! mypy catches it, not Python
```

런타임 검증이 필요하다면 `isinstance`, `pydantic` 같은 별도 수단을 써야 합니다.

### 실수 5. 서드파티 라이브러리의 타입 스텁을 설치하지 않는다

```bash
pip install types-requests  # type stubs for requests
mypy src/  # resolves import type errors for requests
```

## 실무 적용

- **CI 게이트**: `mypy --strict src/`를 CI에 추가해 타입 오류가 있는 PR을 차단할 수 있습니다.
- **IDE 지원**: VSCode Pylance 같은 도구가 타입 힌트를 읽어 자동완성과 경고를 제공합니다.
- **API 문서화**: 타입 힌트를 기반으로 API 문서를 더 풍부하게 생성할 수 있습니다.
- **리팩터링 안전망**: 함수 시그니처를 바꿀 때 영향 범위를 빠르게 찾을 수 있습니다.
- **Pydantic 연동**: 타입 힌트를 데이터 모델과 런타임 검증에 함께 활용할 수 있습니다.

## 실무에서는 이렇게 생각합니다

타입 힌트는 “미래의 나와 팀원을 위한 실행 가능한 문서”에 가깝습니다. `data: dict[str, list[int]]`만 봐도 구조를 빠르게 이해할 수 있기 때문입니다.

새 프로젝트라면 처음부터 `strict = true`로 시작하는 편이 좋습니다. 반대로 기존 프로젝트에서는 새 파일부터 타입을 추가하고 점진적으로 넓혀 가는 전략이 현실적입니다. 실무에서는 전면 도입보다 **점진적 도입**이 성공 확률이 높습니다.

## 체크리스트

- [ ] 함수 인자와 반환값에 타입 힌트를 추가할 수 있다
- [ ] `mypy`로 타입 오류를 검사할 수 있다
- [ ] `py.typed`의 역할을 이해하고 패키지에 포함할 수 있다
- [ ] Generic, Union, Optional을 적절히 사용할 수 있다
- [ ] `pyproject.toml`에서 `mypy` 설정을 구성할 수 있다

## 연습 문제

1. 이전 글의 CLI 패키지에 있는 모든 함수에 타입 힌트를 추가하고 `mypy --strict src/`를 통과시켜 보세요.
2. `TypedDict`로 사용자 정보 구조를 정의하고, 잘못된 키 접근을 `mypy`가 잡는지 확인해 보세요.
3. `py.typed`를 추가한 뒤 wheel을 빌드하고, wheel 내부에 이 파일이 포함되는지 확인해 보세요.

## 정리 · 다음 글

- 타입 힌트는 함수의 입력과 출력 계약을 코드에 남겨 실행 전 오류 검출을 돕습니다.
- `mypy`는 코드를 실행하지 않고 타입 오류를 검사합니다.
- `py.typed`가 있으면 패키지 사용자도 타입 검사 혜택을 받을 수 있습니다.
- 새 프로젝트는 `strict = true`로 시작하고, 기존 프로젝트는 점진적으로 도입하는 편이 좋습니다.
- `Any`를 남용하면 타입 힌트의 효과가 크게 줄어듭니다.

다음 글에서는 문서화 — README, MkDocs, API Reference를 다룹니다.

## 타입 힌트 기초부터 고급까지

### 기본 타입 어노테이션

```python
# 기본 타입
name: str = "acme"
count: int = 42
ratio: float = 3.14
is_active: bool = True

# 컬렉션 타입 (Python 3.9+)
names: list[str] = ["alice", "bob"]
scores: dict[str, int] = {"alice": 95, "bob": 87}
unique_ids: set[int] = {1, 2, 3}
coordinates: tuple[float, float] = (37.5, 127.0)
```

### 함수 시그니처

```python
def greet(name: str, times: int = 1) -> str:
    return f"Hello, {name}! " * times

def process_items(items: list[dict[str, int]]) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items:
        result.update(item)
    return result
```

### Union과 Optional

```python
from typing import Union

# Python 3.10+ 문법
def parse_value(value: str | int) -> str:
    return str(value)

# Optional은 X | None의 축약
def find_user(user_id: int) -> dict[str, str] | None:
    users = {"1": {"name": "Alice"}}
    return users.get(str(user_id))
```

### TypedDict: 딕셔너리에 구조 부여

```python
from typing import TypedDict, NotRequired

class UserConfig(TypedDict):
    name: str
    email: str
    age: NotRequired[int]  # 선택 필드

def create_user(config: UserConfig) -> None:
    print(f"Creating user: {config['name']}")

# mypy가 잘못된 키나 타입을 잡아줌
create_user({"name": "Alice", "email": "a@b.com"})  # OK
create_user({"name": 123, "email": "a@b.com"})      # mypy error!
```

### Protocol: 구조적 서브타이핑

```python
from typing import Protocol

class Serializable(Protocol):
    def to_dict(self) -> dict[str, str]: ...

class User:
    def to_dict(self) -> dict[str, str]:
        return {"name": self.name}

class Config:
    def to_dict(self) -> dict[str, str]:
        return {"key": self.key}

def save(obj: Serializable) -> None:
    data = obj.to_dict()
    # User와 Config 모두 전달 가능 (to_dict 메서드가 있으므로)
```

### Generic 타입

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Result(Generic[T]):
    def __init__(self, value: T | None = None, error: str | None = None):
        self.value = value
        self.error = error
    
    def is_ok(self) -> bool:
        return self.error is None

def fetch_data() -> Result[list[str]]:
    try:
        return Result(value=["data1", "data2"])
    except Exception as e:
        return Result(error=str(e))
```

## mypy 설정과 실전 사용

### pyproject.toml에 mypy 설정

```toml
[tool.mypy]
python_version = "3.11"
strict = true                    # 모든 엄격 옵션 활성화
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true     # 모든 함수에 타입 필수
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true

# 서드파티 라이브러리별 설정
[[tool.mypy.overrides]]
module = "httpx.*"
ignore_missing_imports = false

[[tool.mypy.overrides]]
module = "legacy_module.*"
ignore_errors = true             # 레거시 코드 점진적 마이그레이션
```

### mypy가 잡아내는 대표적 에러

```python
# 에러 1: 반환 타입 불일치
def get_name() -> str:
    return None  # error: Incompatible return value type (got "None", expected "str")

# 에러 2: 잘못된 인자 타입
def add(a: int, b: int) -> int:
    return a + b

add("1", "2")  # error: Argument 1 has incompatible type "str"; expected "int"

# 에러 3: None 체크 누락
def process(value: str | None) -> str:
    return value.upper()  # error: Item "None" has no attribute "upper"
    # 수정:
    # if value is None:
    #     return ""
    # return value.upper()

# 에러 4: 불완전한 딕셔너리 타입
data: dict[str, int] = {}
data["count"] = "five"  # error: Incompatible types in assignment
```

### 점진적 타입 도입 전략

기존 프로젝트에 타입을 한꺼번에 추가하는 것은 비현실적입니다. 점진적으로 도입합니다.

```toml
# 1단계: 느슨한 설정으로 시작
[tool.mypy]
python_version = "3.11"
warn_return_any = true
# strict = false (기본값)

# 2단계: 새 파일에만 엄격 적용
[[tool.mypy.overrides]]
module = "acme_utils.new_module.*"
disallow_untyped_defs = true

# 3단계: 전체 strict 전환
[tool.mypy]
strict = true
```

## PEP 561: 패키지의 타입 정보 배포

패키지를 설치한 사용자도 타입 검사를 활용하려면 PEP 561 마커가 필요합니다.

### py.typed 마커 파일

```bash
# src/acme_utils/py.typed (빈 파일)
touch src/acme_utils/py.typed
```

```toml
# pyproject.toml에서 패키지 데이터로 포함
[tool.setuptools.package-data]
acme_utils = ["py.typed", "*.pyi"]
```

### 인라인 타입 vs 스텁 파일

| 방식 | 파일 | 장점 | 단점 |
|---|---|---|---|
| 인라인 타입 | `.py` 파일에 직접 | 코드와 타입이 항상 동기화 | 런타임 import 비용 (미미) |
| 스텁 파일 | `.pyi` 파일 | C 확장이나 레거시 코드에 적합 | 동기화 관리 필요 |

### 스텁 파일 예시

```python
# src/acme_utils/core.pyi
from typing import overload

class Engine:
    def __init__(self, config: dict[str, str]) -> None: ...
    
    @overload
    def run(self, query: str) -> str: ...
    @overload
    def run(self, query: list[str]) -> list[str]: ...
    def run(self, query: str | list[str]) -> str | list[str]: ...
```

### stubgen: 자동 스텁 생성

```bash
# mypy의 stubgen 도구
pip install mypy
stubgen src/acme_utils -o stubs/

# 생성된 스텁 확인
cat stubs/acme_utils/core.pyi
```

## Ruff: 초고속 린터와 포매터

Ruff는 Rust로 작성된 Python 린터로, flake8 + isort + pycodestyle을 하나로 대체합니다.

```toml
# pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
]
ignore = ["E501"]  # line-too-long (formatter가 처리)

[tool.ruff.lint.isort]
known-first-party = ["acme_utils"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

```bash
# 린트 실행
ruff check .
ruff check --fix .  # 자동 수정 가능한 것은 즉시 수정

# 포맷 실행
ruff format .
ruff format --check .  # CI에서 검증만
```

### Ruff vs 기존 도구 속도 비교

```text
프로젝트: 10,000줄 Python 코드 기준
- flake8 + isort + black: ~5초
- ruff check + ruff format: ~0.1초 (50배 빠름)
```

## CI에서 타입 검사와 린트 통합

```yaml
name: Quality
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      
      # 린트 (가장 빠름 - 먼저 실행)
      - run: ruff check .
      - run: ruff format --check .
      
      # 타입 검사
      - run: mypy src
      
      # 테스트
      - run: pytest --cov=acme_utils
```

## pyright: mypy의 대안

```toml
# pyproject.toml
[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "strict"
reportMissingImports = true
reportMissingTypeStubs = true
```

```bash
pip install pyright
pyright src/
```

| 항목 | mypy | pyright |
|---|---|---|
| 언어 | Python | TypeScript (Node.js) |
| 속도 | 보통 | 빠름 |
| IDE 통합 | 보통 | VSCode 최적화 (Pylance) |
| 생태계 | 가장 넓음 | 빠르게 성장 |
| 설정 난이도 | 중간 | 낮음 |

## 타입 힌트 실전 패턴

### Callable 타입

```python
from typing import Callable

# 함수를 인자로 받는 함수
def retry(
    func: Callable[[], str],
    max_attempts: int = 3,
) -> str:
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception:
            if attempt == max_attempts - 1:
                raise
    return ""  # unreachable, but makes mypy happy

# 데코레이터 타입
from typing import TypeVar, ParamSpec
from functools import wraps

P = ParamSpec("P")
R = TypeVar("R")

def log_calls(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

### Literal 타입

```python
from typing import Literal

def set_log_level(level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]) -> None:
    print(f"Setting level to {level}")

set_log_level("INFO")     # OK
set_log_level("VERBOSE")  # mypy error: not in Literal values
```

### Self 타입 (Python 3.11+)

```python
from typing import Self

class Builder:
    def __init__(self) -> None:
        self._name: str = ""
        self._version: str = ""
    
    def name(self, name: str) -> Self:
        self._name = name
        return self
    
    def version(self, version: str) -> Self:
        self._version = version
        return self

# 메서드 체이닝이 타입 안전
builder = Builder().name("acme").version("1.0")
```

### Overload: 입력에 따라 다른 반환 타입

```python
from typing import overload

@overload
def process(data: str) -> str: ...
@overload
def process(data: bytes) -> bytes: ...
@overload
def process(data: list[str]) -> list[str]: ...

def process(data: str | bytes | list[str]) -> str | bytes | list[str]:
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, bytes):
        return data.upper()
    else:
        return [item.upper() for item in data]

# mypy가 반환 타입을 정확히 추론
result: str = process("hello")        # OK
result2: bytes = process(b"hello")    # OK
result3: list[str] = process(["a"])   # OK
```

## pre-commit에서 자동 검사

커밋 전에 타입 검사와 린트를 자동으로 실행하면 PR에서 기본적인 문제가 발견되는 것을 방지합니다.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.5
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
          - pydantic>=2.5
```

```bash
# pre-commit 설치
pip install pre-commit
pre-commit install

# 수동 전체 실행
pre-commit run --all-files
```

## 타입 검사 커버리지 측정

```bash
# mypy 리포트 생성
mypy src --html-report reports/mypy

# 또는 텍스트 요약
mypy src --txt-report reports/mypy
cat reports/mypy/index.txt
```

```text
Module                Lines  Precise  Imprecise  Any
acme_utils            450    420      20         10
acme_utils.core       200    195      3          2
acme_utils.config     120    118      2          0
acme_utils.cli        130    107      15         8
```

타입 커버리지를 CI에서 추적하면 점진적으로 타입 안전성을 높일 수 있습니다.

`Any` 비율이 높은 모듈은 타입 안전성의 빈틈입니다. 해당 모듈부터 우선적으로 타입을 보강하면 전체 프로젝트의 타입 신뢰도를 효율적으로 높일 수 있습니다. 목표는 `Precise` 비율 90% 이상을 유지하는 것입니다.

실무에서는 mypy strict 모드를 새 모듈에만 먼저 적용하고, 레거시 모듈은 `ignore_errors = true`로 예외를 두되 점진적으로 줄여가는 전략이 현실적입니다.

## 처음 질문으로 돌아가기

- **타입 힌트는 왜 필요하고 런타임에 영향을 줄까요?**
  - 타입 힌트는 코드의 의도를 명시하여 mypy 같은 도구가 실행 전에 타입 불일치, None 체크 누락, 잘못된 인자 전달을 잡아줍니다. 런타임에는 타입 힌트가 무시되므로 성능에 영향을 주지 않습니다. 단, `typing` 모듈 import는 약간의 시작 시간을 추가합니다.

- **`mypy`는 어떤 오류를 잡아 줄까요?**
  - 반환 타입 불일치, None일 수 있는 값에 대한 메서드 호출, 잘못된 타입의 인자 전달, 존재하지 않는 속성 접근, TypedDict의 필수 키 누락 등을 잡습니다. `strict` 모드를 사용하면 타입이 없는 함수 정의도 에러로 처리하여 프로젝트 전체의 타입 안전성을 보장합니다.

- **패키지 사용자에게 타입 정보를 제공하려면 어떻게 해야 할까요?**
  - `src/패키지/py.typed` 빈 파일을 추가하고 `pyproject.toml`의 package-data에 포함시킵니다. 이것이 PEP 561 마커로, mypy와 pyright가 이 패키지에서 타입 정보를 읽어야 한다는 신호입니다. 인라인 타입이 가장 간편하고, C 확장이나 레거시 코드에는 `.pyi` 스텁 파일을 사용합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package 101 (1/10): Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): 프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [Python Package 101 (3/10): 의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- [Python Package 101 (4/10): 패키지 빌드하기 — wheel과 sdist](./04-building-packages.md)
- [Python Package 101 (5/10): PyPI에 배포하기 — TestPyPI부터 실제 배포까지](./05-publishing-to-pypi.md)
- [Python Package 101 (6/10): 버전 관리와 릴리스](./06-versioning-and-releases.md)
- [Python Package 101 (7/10): CLI 패키지 만들기](./07-cli-packages.md)
- **Python Package 101 (8/10): 타입 힌트와 정적 검사 (현재 글)**
- Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference (예정)
- Python Package 101 (10/10): 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/python-package-101/ko)
- [mypy documentation](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 561 - Distributing and Packaging Type Information](https://peps.python.org/pep-0561/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)

Tags: Python, Packaging, PyPI, pyproject.toml

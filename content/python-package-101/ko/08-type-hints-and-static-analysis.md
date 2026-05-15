---
title: 타입 힌트와 정적 검사
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
last_reviewed: '2026-05-12'
seo_description: 타입 힌트는 함수의 입력과 출력 타입을 명시하는 것이고, mypy는 코드를 실행하지 않고 타입 오류를 찾아주는 도구입니다.
---

# 타입 힌트와 정적 검사

패키지를 다른 사람이 쓰는 순간부터 “이 함수에는 무엇을 넘겨야 하나”, “반환값은 어떤 구조인가” 같은 질문이 생깁니다. 타입 힌트는 이 질문에 코드 수준에서 답하게 해 주고, 정적 분석기는 실행 전에 실수를 잡아 줍니다. 이 글은 Python Package 101 시리즈의 8번째 글입니다. 여기서는 타입 힌트의 기본 문법, `mypy` 검사 흐름, `py.typed` 마커 파일의 의미를 정리하겠습니다.

## 이 글에서 다룰 문제

- 타입 힌트는 왜 필요하고 런타임에 영향을 줄까요?
- `mypy`는 어떤 오류를 잡아 줄까요?
- `py.typed` 마커 파일은 왜 필요할까요?
- Generic, Union, Optional은 언제 쓸까요?

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
from typing import TypeVar, Callable

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

<!-- toc:begin -->
## 시리즈 목차

- [Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- [패키지 빌드하기 — wheel과 sdist](./04-building-packages.md)
- [PyPI에 배포하기 — TestPyPI부터 실제 배포까지](./05-publishing-to-pypi.md)
- [버전 관리와 릴리스](./06-versioning-and-releases.md)
- [CLI 패키지 만들기](./07-cli-packages.md)
- **타입 힌트와 정적 검사 (현재 글)**
- 문서화 — README, MkDocs, API Reference (예정)
- 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [mypy documentation](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 561 - Distributing and Packaging Type Information](https://peps.python.org/pep-0561/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)

Tags: Python, Type Hints, mypy, py.typed, Static Analysis, Typing

---
series: type-hints-python-101
episode: 4
title: 함수 타입 힌트
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Type Hints
  - Callable
  - 함수 시그니처
  - 오버로드
  - 데코레이터
seo_description: Callable, 콜백, 데코레이터, 오버로드까지 함수와 관련된 타입 힌트 심화 문법을 다룹니다.
last_reviewed: '2026-05-04'
---

# 함수 타입 힌트

> Type Hints in Python 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 함수를 인자로 받는 함수의 타입 힌트는 어떻게 작성할까요?

> 고차 함수, 콜백, 데코레이터는 함수를 값으로 다룹니다. `Callable`로 함수 시그니처를 표현하고, `@overload`로 입력에 따라 달라지는 반환 타입을 명시할 수 있습니다. 이 글에서는 함수와 관련된 심화 타입 힌트를 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- `Callable[[ArgTypes], ReturnType]` 사용법
- 콜백 함수의 타입 표현
- 데코레이터의 타입 힌트
- `@overload`로 조건부 반환 타입 명시

## 왜 중요한가

`map()`, `filter()`, `sorted()`의 `key` 인자처럼 함수를 전달하는 패턴은 Python에서 흔합니다. 이런 함수의 타입을 명시하지 않으면, 잘못된 시그니처의 함수를 전달해도 에러를 잡을 수 없습니다.

> Callable = 함수 타입의 청사진

`@overload`는 입력 타입에 따라 반환 타입이 달라지는 함수를 정확하게 표현하여, 호출 시점에 올바른 타입 추론을 가능하게 합니다.

## 핵심 개념 잡기

> Callable의 구조

```
Callable[[인자1, 인자2], 반환타입]

예시:
  Callable[[str], int]          → str을 받아 int 반환
  Callable[[int, int], float]   → int 2개를 받아 float 반환
  Callable[[], None]            → 인자 없이 None 반환
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Callable | 함수 타입을 표현하는 제네릭 타입입니다 |
| 콜백(callback) | 다른 함수에 인자로 전달되는 함수입니다 |
| @overload | 입력에 따라 다른 반환 타입을 명시하는 데코레이터입니다 |
| ParamSpec | 데코레이터에서 원본 함수의 시그니처를 보존합니다 |
| TypeVar | 제네릭 함수에서 타입 매개변수를 정의합니다 |

## Before / After

타입 없는 콜백을 Callable로 명시합니다.

```python
# before: callback이 어떤 함수인지 알 수 없음
def apply(items, callback):
    return [callback(item) for item in items]
```

```python
# after: callback의 시그니처가 명확
from typing import Callable

def apply(items: list[str], callback: Callable[[str], str]) -> list[str]:
    return [callback(item) for item in items]
```

## 단계별 실습

### Step 1: Callable 기본

```python
from typing import Callable


# 함수를 인자로 받는 함수
def apply_operation(
    x: int,
    y: int,
    operation: Callable[[int, int], int],
) -> int:
    return operation(x, y)


def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b


print(apply_operation(3, 5, add))       # 8
print(apply_operation(3, 5, multiply))   # 15

# lambda도 Callable로 전달 가능
print(apply_operation(3, 5, lambda a, b: a - b))  # -2
```

### Step 2: 콜백 패턴

```python
from typing import Callable


# 이벤트 핸들러 등록
EventHandler = Callable[[str, dict], None]

class EventEmitter:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}

    def on(self, event: str, handler: EventHandler) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def emit(self, event: str, data: dict) -> None:
        for handler in self._handlers.get(event, []):
            handler(event, data)


def log_handler(event: str, data: dict) -> None:
    print(f"[LOG] {event}: {data}")

def alert_handler(event: str, data: dict) -> None:
    print(f"[ALERT] {event} 발생!")


emitter = EventEmitter()
emitter.on("error", log_handler)
emitter.on("error", alert_handler)
emitter.emit("error", {"code": 500, "message": "서버 오류"})
# [LOG] error: {'code': 500, 'message': '서버 오류'}
# [ALERT] error 발생!
```

### Step 3: 반환값이 함수인 경우

```python
from typing import Callable


def make_multiplier(factor: int) -> Callable[[int], int]:
    """팩터를 곱하는 함수를 반환합니다."""
    def multiplier(x: int) -> int:
        return x * factor
    return multiplier


double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))   # 10
print(triple(5))   # 15


# 검증 함수 팩토리
def make_validator(
    min_val: int,
    max_val: int,
) -> Callable[[int], bool]:
    def validate(value: int) -> bool:
        return min_val <= value <= max_val
    return validate


is_valid_age = make_validator(0, 150)
is_valid_score = make_validator(0, 100)

print(is_valid_age(25))     # True
print(is_valid_score(150))  # False
```

### Step 4: 데코레이터 타입 힌트

```python
from typing import Callable, ParamSpec, TypeVar
from functools import wraps
import time

P = ParamSpec("P")
R = TypeVar("R")


def timer(func: Callable[P, R]) -> Callable[P, R]:
    """실행 시간을 측정하는 데코레이터입니다."""
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__}: {elapsed:.4f}초")
        return result
    return wrapper


@timer
def slow_function(n: int) -> int:
    """느린 계산을 시뮬레이션합니다."""
    total = sum(range(n))
    return total


result = slow_function(1_000_000)
# slow_function: 0.0312초
print(f"결과: {result:,}")
# 결과: 499,999,500,000
```

### Step 5: @overload

```python
from typing import overload


@overload
def process(value: int) -> str: ...
@overload
def process(value: str) -> int: ...
@overload
def process(value: list[int]) -> int: ...

def process(value: int | str | list[int]) -> str | int:
    """입력 타입에 따라 다른 변환을 수행합니다."""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return len(value)
    if isinstance(value, list):
        return sum(value)
    raise TypeError(f"지원하지 않는 타입: {type(value)}")


# mypy가 각 호출에 대해 정확한 반환 타입을 추론
result_str = process(42)        # mypy: str
result_int = process("hello")   # mypy: int
result_sum = process([1, 2, 3]) # mypy: int

print(f"process(42) = '{result_str}'")        # process(42) = '42'
print(f"process('hello') = {result_int}")     # process('hello') = 5
print(f"process([1,2,3]) = {result_sum}")     # process([1,2,3]) = 6
```

## 이 코드에서 주목할 점

- `Callable[[ArgTypes], ReturnType]`으로 함수 타입을 정확히 표현합니다
- `ParamSpec`은 데코레이터에서 원본 함수의 시그니처를 보존합니다
- `@overload`는 입력에 따라 다른 반환 타입을 명시하여 호출 시점 추론을 가능하게 합니다
- 타입 별칭(`EventHandler`)으로 복잡한 Callable을 읽기 쉽게 만듭니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `Callable` 인자 타입 생략 | 시그니처 검증이 불가능합니다 | `Callable[[int], str]`로 완전히 명시합니다 |
| 데코레이터에서 ParamSpec 미사용 | 원본 함수의 시그니처가 손실됩니다 | `ParamSpec`과 `TypeVar`를 사용합니다 |
| @overload 실제 구현에 타입 누락 | 구현체 시그니처가 모든 오버로드를 포함해야 합니다 | Union으로 모든 경우를 커버합니다 |
| Callable에 키워드 인자 표현 | Callable은 위치 인자만 표현합니다 | `Protocol`로 정확한 시그니처를 정의합니다 |
| lambda에 타입 힌트 시도 | lambda는 타입 힌트 문법을 지원하지 않습니다 | 일반 함수를 정의합니다 |

## 실무에서 이렇게 쓰입니다

- FastAPI의 의존성 주입에서 Callable 타입으로 팩토리를 전달합니다
- pytest의 fixture가 반환하는 팩토리 함수에 Callable을 사용합니다
- 이벤트 드리븐 아키텍처에서 핸들러 타입을 Callable로 정의합니다
- 미들웨어 체인에서 `Callable[[Request], Response]`를 사용합니다
- `@overload`로 `json.loads` 같은 다형 함수를 정확히 타입 지정합니다

## 현업 개발자는 이렇게 생각합니다

`Callable`은 함수형 프로그래밍과 타입 시스템의 교차점입니다. 콜백, 팩토리, 데코레이터 패턴에서 함수의 시그니처를 명시하면 잘못된 함수 전달을 사전에 방지할 수 있습니다.

`ParamSpec`은 Python 3.10에서 추가된 강력한 도구입니다. 데코레이터를 작성할 때 원본 함수의 시그니처를 그대로 보존하므로, IDE 자동완성과 mypy 검증이 데코레이터를 투과해서 동작합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **Callable** — 콜백 타입을 명시해 호출 계약을 분명히 합니다.
- **Default와 타입** — 기본값과 Optional을 혼동하지 않습니다.
- **Overload** — 복합 시그니처는 @overload로 표현합니다.
- **ParamSpec** — 데코레이터 타입 보존에 ParamSpec을 활용합니다.
- **Return None 명시** — 절차형 함수도 -> None을 명시합니다.

## 체크리스트

- [ ] `Callable[[ArgTypes], ReturnType]`을 작성할 수 있다
- [ ] 콜백 패턴에 적절한 Callable 타입을 정의할 수 있다
- [ ] `ParamSpec`으로 데코레이터 타입을 정확히 표현할 수 있다
- [ ] `@overload`로 조건부 반환 타입을 명시할 수 있다
- [ ] Callable 타입 별칭을 활용하여 가독성을 높일 수 있다

## 연습 문제

1. `list[int]`를 받아 정렬 키 함수(`Callable[[int], Any]`)를 적용하여 정렬하는 함수를 작성하세요.
2. `ParamSpec`을 사용하여 호출 횟수를 세는 데코레이터를 작성하세요.
3. `@overload`로 문자열이면 대문자, 정수면 절대값, 리스트면 길이를 반환하는 함수를 작성하세요.

## 정리 및 다음 글 안내

`Callable`로 함수 타입을, `ParamSpec`으로 데코레이터의 시그니처 보존을, `@overload`로 조건부 반환 타입을 표현했습니다. 다음 글에서는 딕셔너리 구조를 타입으로 정의하는 **TypedDict와 dataclass**를 다룹니다.

<!-- toc:begin -->
- [Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Optional과 Union](./03-optional-and-union.md)
- **함수 타입 힌트 (현재 글)**
- [TypedDict와 dataclass](./05-typeddict-and-dataclass.md)
- [Protocol과 structural typing](./06-protocol-and-structural-typing.md)
- [Generic 이해하기](./07-generic.md)
- [mypy와 pyright 사용하기](./08-mypy-and-pyright.md)
- [Pydantic과 타입 힌트](./09-pydantic-and-type-hints.md)
- [타입 힌트를 잘 쓰는 기준](./10-type-hints-best-practices.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — typing.Callable](https://docs.python.org/3/library/typing.html#callable)
- [PEP 612 — Parameter Specification Variables](https://peps.python.org/pep-0612/)
- [PEP 484 — @overload](https://peps.python.org/pep-0484/#function-method-overloading)
- [mypy 공식 문서 — Callable types](https://mypy.readthedocs.io/en/stable/kinds_of_types.html#callable-types-and-lambdas)

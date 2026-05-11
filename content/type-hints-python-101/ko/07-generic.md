---
series: type-hints-python-101
episode: 7
title: Generic 이해하기
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
  - Generic
  - TypeVar
  - 타입 매개변수
  - 제네릭 프로그래밍
seo_description: TypeVar와 Generic으로 타입 안전한 재사용 코드를 작성하는 방법을 다룹니다.
last_reviewed: '2026-05-11'
---

# Generic 이해하기

> Type Hints in Python 101 시리즈 (7/10)


## 이 글에서 다룰 문제

라이브러리나 유틸리티 함수를 작성할 때 여러 타입을 지원해야 하는 경우가 많습니다. `Any`를 쓰면 타입 검사기가 오류를 잡지 못하고, Union으로 나열하면 반환 타입이 넓어집니다. Generic은 호출 시점에 구체적인 타입이 결정되므로 재사용성과 타입 안전성을 동시에 확보합니다.

> Generic = 타입을 매개변수로 받는 코드

FastAPI의 `Response[T]`, SQLAlchemy의 `Mapped[T]` 등 실무 라이브러리가 Generic을 적극 활용합니다.

## 전체 흐름
> Generic은 "타입 변수"를 선언하고, 그 변수를 함수나 클래스의 타입 힌트에 사용합니다. 호출 시점에 구체적인 타입이 대입됩니다.

```text
TypeVar("T") ──> 함수 시그니처에 T 사용
                     │
              호출: f([1,2,3])
                     │
              T = int로 결정
                     │
              반환 타입 = int
```

## Before / After

**Before — Any를 사용한 코드:**

```python
from typing import Any


def first(items: list[Any]) -> Any:
    return items[0]


value = first([1, 2, 3])
# value의 타입: Any → 타입 정보 소실
```

**After — Generic을 사용한 코드:**

```python
from typing import TypeVar

T = TypeVar("T")


def first(items: list[T]) -> T:
    return items[0]


value = first([1, 2, 3])
# value의 타입: int → 정확한 추론
```

## 단계별로 따라하기

### 1단계: TypeVar 선언과 기본 사용

```python
from typing import TypeVar

T = TypeVar("T")


def identity(value: T) -> T:
    """받은 값을 그대로 반환합니다."""
    return value


text = identity("hello")   # str
number = identity(42)       # int
```

TypeVar의 이름 문자열은 변수 이름과 일치해야 합니다. `T = TypeVar("T")`처럼 같은 이름을 사용합니다.

### 2단계: Generic 클래스 작성

```python
from typing import Generic, TypeVar

T = TypeVar("T")


class Stack(Generic[T]):
    """타입 안전한 스택 자료구조입니다."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0


int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
value = int_stack.pop()  # int로 추론
```

### 3단계: bound로 상한 제한

```python
from typing import TypeVar


class Comparable:
    def __lt__(self, other: object) -> bool:
        return NotImplemented


C = TypeVar("C", bound=Comparable)


def find_min(items: list[C]) -> C:
    """Comparable을 구현한 타입만 허용합니다."""
    result = items[0]
    for item in items[1:]:
        if item < result:
            result = item
    return result
```

`bound=Comparable`은 `C`가 `Comparable`의 하위 타입이어야 한다는 뜻입니다.

### 4단계: constraint로 허용 타입 나열

```python
from typing import TypeVar

Number = TypeVar("Number", int, float)


def add(a: Number, b: Number) -> Number:
    """int 또는 float만 허용합니다."""
    return a + b


add(1, 2)       # OK — int
add(1.0, 2.5)   # OK — float
# add("a", "b") # Error — str은 허용되지 않음
```

constraint는 나열된 타입 중 하나여야 합니다. bound와 달리 하위 타입 관계가 아니라 정확한 타입 일치를 요구합니다.

### 5단계: Python 3.12 타입 매개변수 문법

```python
# Python 3.12 이상
def first[T](items: list[T]) -> T:
    return items[0]


class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()
```

Python 3.12부터 `TypeVar`를 명시적으로 선언하지 않아도 `[T]` 문법으로 타입 매개변수를 선언할 수 있습니다.

## 이 코드에서 주목할 점

- TypeVar는 같은 함수 시그니처 안에서 동일한 타입으로 결정됩니다
- Generic 클래스를 인스턴스화할 때 `Stack[int]`처럼 구체 타입을 지정합니다
- bound는 상속 관계를, constraint는 허용 목록을 기반으로 제한합니다
- Python 3.12 문법은 TypeVar 선언 없이 간결하게 작성할 수 있습니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| TypeVar 이름 불일치 | `T = TypeVar("U")`는 혼란을 유발합니다 | 변수 이름과 문자열을 일치시킵니다 |
| 모듈 수준 대신 함수 안에서 TypeVar 선언 | 매 호출마다 새 TypeVar가 생깁니다 | 모듈 수준에서 한 번만 선언합니다 |
| bound와 constraint 혼동 | 상속 제한과 허용 목록은 다릅니다 | bound는 상한, constraint는 목록입니다 |
| Generic 미상속 | 타입 매개변수가 무시됩니다 | `class MyClass(Generic[T]):`로 상속합니다 |
| 여러 TypeVar를 같은 이름으로 선언 | 타입 관계가 깨집니다 | 고유한 이름을 사용합니다 |

## 실무에서는 이렇게 쓰입니다

- FastAPI `Response[T]`: API 응답을 타입 안전하게 감싸는 Generic 래퍼
- SQLAlchemy `Mapped[T]`: ORM 컬럼의 Python 타입을 Generic으로 표현
- Pydantic `BaseModel`의 Generic 서브클래스: 페이지네이션 응답 등 공통 래퍼
- 캐시 데코레이터: 원본 함수의 반환 타입을 그대로 유지하는 `ParamSpec` 활용
- Repository 패턴: `Repository[T]`로 엔티티별 CRUD를 타입 안전하게 추상화

## 체크리스트

- [ ] TypeVar를 모듈 수준에서 선언했는가
- [ ] Generic 클래스가 `Generic[T]`를 상속했는가
- [ ] bound와 constraint의 차이를 이해했는가
- [ ] Python 3.12 문법과 기존 문법의 차이를 파악했는가
- [ ] 불필요한 Generic을 남용하지 않았는가

## 정리 및 다음 단계

Generic은 타입을 매개변수로 받아 재사용 가능한 코드를 작성하는 도구입니다. TypeVar로 타입 변수를 선언하고, Generic을 상속하여 타입 안전한 클래스를 만들 수 있습니다. bound와 constraint로 허용 범위를 제한하면 더 정밀한 타입 검사가 가능합니다.

다음 글에서는 작성한 타입 힌트를 실제로 검증하는 도구인 mypy와 pyright를 다룹니다.

<!-- toc:begin -->
- [Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Optional과 Union](./03-optional-and-union.md)
- [함수 타입 힌트](./04-function-type-hints.md)
- [TypedDict와 dataclass](./05-typeddict-and-dataclass.md)
- [Protocol과 structural typing](./06-protocol-and-structural-typing.md)
- **Generic 이해하기 (현재 글)**
- [mypy와 pyright 사용하기](./08-mypy-and-pyright.md)
- [Pydantic과 타입 힌트](./09-pydantic-and-type-hints.md)
- [타입 힌트를 잘 쓰는 기준](./10-type-hints-best-practices.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — typing.TypeVar](https://docs.python.org/3/library/typing.html#typing.TypeVar)
- [Python 공식 문서 — typing.Generic](https://docs.python.org/3/library/typing.html#typing.Generic)
- [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/)
- [mypy 문서 — Generics](https://mypy.readthedocs.io/en/stable/generics.html)

Tags: Python, Type Hints, Generic, TypeVar, 타입 매개변수, 제네릭 프로그래밍

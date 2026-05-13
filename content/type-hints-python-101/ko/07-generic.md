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
last_reviewed: '2026-05-12'
---

# Generic 이해하기

여러 타입에 재사용되는 함수를 만들고 싶은데, 입력 타입과 출력 타입의 관계는 유지하고 싶을 때가 있습니다. `Any`를 쓰면 타입 정보가 사라지고, 타입별 함수를 따로 만들면 코드가 늘어납니다. 이때 Generic이 등장합니다.

이 글은 Type Hints (Python) 101 시리즈의 7번째 글입니다. 여기서는 `TypeVar`, `Generic`, bound, constraint, Python 3.12 문법까지 제네릭 타입의 핵심을 정리합니다.

## 이 글에서 다룰 문제

- 입력 타입을 그대로 반환 타입에 연결하려면 어떻게 적을까요?
- 재사용 가능한 컨테이너 클래스를 타입 안전하게 만들려면 무엇이 필요할까요?
- bound와 constraint는 어떤 차이가 있을까요?
- Python 3.12의 새 타입 매개변수 문법은 무엇이 달라졌을까요?

> Generic의 핵심은 여러 타입을 한 번에 허용하는 데 있지 않고, 타입들 사이의 관계를 보존하는 데 있습니다.

## 왜 이 주제가 중요한가

실무 유틸리티 함수와 라이브러리는 여러 타입을 다뤄야 합니다. 그런데 `Any`를 쓰는 순간 분석기는 더 이상 값의 관계를 추적하지 못합니다. 예를 들어 리스트의 첫 원소를 꺼내는 함수는 `list[int]`를 받으면 `int`를, `list[str]`를 받으면 `str`을 돌려줘야 자연스럽습니다.

이 관계를 정확히 적어야 API 래퍼, 저장소 패턴, 컨테이너 클래스, 프레임워크 헬퍼가 타입 안전하게 유지됩니다. FastAPI의 `Response[T]`, SQLAlchemy의 `Mapped[T]`가 모두 같은 원리를 씁니다.

## 한눈에 보는 개념

```text
TypeVar("T") ──> 함수 시그니처에 T 사용
                     │
              호출: f([1, 2, 3])
                     │
              T = int 로 결정
                     │
              반환 타입 = int
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| TypeVar | 제네릭 함수와 클래스에서 쓸 타입 변수를 선언합니다 |
| Generic | 타입 변수를 받는 클래스를 만드는 베이스 클래스입니다 |
| bound | 타입 변수가 따라야 하는 상한 타입입니다 |
| constraint | 타입 변수가 가질 수 있는 정확한 허용 목록입니다 |
| ParamSpec | 함수 전체 시그니처를 다루는 특수한 타입 변수입니다 |

## 바꾸기 전과 후

```python
from typing import Any


def first(items: list[Any]) -> Any:
    return items[0]


value = first([1, 2, 3])
# value: Any — 타입 정보 소실
```

```python
from typing import TypeVar

T = TypeVar("T")


def first(items: list[T]) -> T:
    return items[0]


value = first([1, 2, 3])
# value: int — 정확한 타입 유지
```

## 단계별로 익히기

### 1단계: `TypeVar` 기본

```python
from typing import TypeVar

T = TypeVar("T")


def identity(value: T) -> T:
    """입력값을 그대로 반환합니다."""
    return value


text = identity("hello")   # str
number = identity(42)       # int
```

`TypeVar("T")`의 문자열은 보통 변수 이름과 맞춰 두는 편이 읽기 쉽습니다.

### 2단계: Generic 클래스 만들기

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
value = int_stack.pop()  # int
```

`Stack[int]`처럼 인스턴스화할 때 구체 타입을 넣으면 push와 pop이 같은 타입 관계를 유지합니다.

### 3단계: bound로 상한 제한하기

```python
from typing import TypeVar


class Comparable:
    def __lt__(self, other: object) -> bool:
        return NotImplemented


C = TypeVar("C", bound=Comparable)


def find_min(items: list[C]) -> C:
    """Comparable의 하위 타입만 받습니다."""
    result = items[0]
    for item in items[1:]:
        if item < result:
            result = item
    return result
```

bound는 "이 타입보다 더 넓어질 수는 없다"는 상한입니다.

### 4단계: constraint로 허용 타입 나열하기

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

constraint는 상속 계보가 아니라 허용 타입 목록 자체를 제한합니다.

### 5단계: Python 3.12 타입 매개변수 문법

```python
# Python 3.12+
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

새 문법은 `TypeVar` 선언을 위로 끌어올리지 않아도 타입 매개변수를 바로 표시할 수 있습니다.

## 여기서 먼저 봐야 할 점

- 한 함수 호출 안에서 같은 `TypeVar`는 같은 구체 타입으로 결정됩니다.
- Generic 클래스는 `Stack[int]`처럼 구체 타입을 넣어 사용할 수 있습니다.
- bound는 상속 관계, constraint는 허용 목록이라는 점이 다릅니다.
- Python 3.12 문법은 더 짧지만 의미는 같습니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| `T = TypeVar("U")`처럼 이름을 다르게 둠 | 읽는 사람이 혼란스럽습니다 | 변수명과 문자열을 맞춥니다 |
| 함수 안에서 TypeVar를 선언함 | 재사용 구조가 불분명해집니다 | 모듈 수준에서 선언합니다 |
| bound와 constraint를 같은 개념으로 봄 | 타입 제한 의미가 달라집니다 | 상한과 허용 목록으로 구분합니다 |
| Generic을 상속하지 않음 | 클래스의 타입 매개변수 의도가 흐려집니다 | `Generic[T]` 또는 Python 3.12 문법을 사용합니다 |
| 단순 함수에도 과하게 Generic을 도입함 | 코드가 더 복잡해집니다 | 입력-출력 관계가 실제로 있을 때만 씁니다 |

## 실무에서는 이렇게 연결됩니다

- `Repository[T]` 패턴은 엔티티별 CRUD 계약을 재사용합니다.
- `Response[T]` 래퍼는 응답 본문의 구체 타입을 유지합니다.
- Pydantic 제네릭 모델은 페이지네이션이나 공통 응답 포맷에 자주 쓰입니다.
- ORM 컬럼 래퍼와 캐시 헬퍼도 Generic 덕분에 API가 안전해집니다.

## 실무 판단 기준

숙련된 개발자는 Generic을 "여러 타입을 받을 수 있어서"보다 "입력과 출력의 관계를 잃지 않으려고" 사용합니다. 반환 타입이 입력 타입에 의존하지 않는 함수라면 굳이 TypeVar를 넣지 않아도 됩니다. 반대로 그 관계가 핵심인 함수와 클래스에서는 Generic이 거의 필수입니다.

또한 제네릭 매개변수가 너무 많아지면 설계를 다시 봅니다. `T`, `U`, `V`, `W`가 한 번에 등장하기 시작하면 타입 안전성보다 복잡성이 더 커졌다는 신호일 수 있습니다.

## 체크리스트

- [ ] TypeVar를 모듈 수준에 선언했습니다
- [ ] Generic 클래스에 `Generic[T]` 또는 Python 3.12 문법을 사용했습니다
- [ ] bound와 constraint의 차이를 구분했습니다
- [ ] Python 3.12 문법 사용 여부를 프로젝트 버전에 맞춰 판단했습니다
- [ ] 단순 함수에 불필요한 Generic을 남발하지 않았습니다

## 연습 문제

1. `Pair[K, V]` 클래스를 만들어 `first: K`, `second: V`를 저장해 보세요.

2. `bound=Sized`를 사용해 `longest(a: T, b: T) -> T` 함수를 작성해 보세요.

3. Python 3.12 문법으로 `Queue[T]` 클래스를 다시 작성해 `enqueue`, `dequeue`, `peek`를 구현해 보세요.

## 정리와 다음 글

Generic은 하나의 함수나 클래스가 여러 타입을 다루더라도 타입 관계를 보존하게 해 줍니다. `TypeVar`는 그 관계를 선언하고, `Generic`은 클래스 수준으로 확장하며, bound와 constraint는 허용 범위를 정밀하게 조절합니다. 잘 쓴 Generic은 재사용성과 타입 안전성을 함께 가져옵니다.

다음 글에서는 지금까지 붙인 타입 힌트를 실제로 검증하는 mypy와 pyright를 살펴보겠습니다.

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

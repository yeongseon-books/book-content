---
series: type-hints-python-101
episode: 5
title: "Type Hints in Python 101 (5/10): TypedDict와 dataclass"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Type Hints
  - TypedDict
  - dataclass
  - 구조화 데이터
  - 타입 안전
seo_description: TypedDict와 dataclass로 딕셔너리와 객체 구조에 타입 안전성을 부여하는 방법을 다룹니다.
last_reviewed: '2026-05-12'
---

# Type Hints in Python 101 (5/10): TypedDict와 dataclass

`dict[str, Any]`는 편하지만 너무 많은 것을 숨깁니다. 어떤 키가 반드시 있어야 하는지, 값 타입이 무엇인지, 이 데이터가 단순 JSON 덩어리인지 아니면 동작을 가진 도메인 객체인지가 흐려집니다.

이 글은 Type Hints (Python) 101 시리즈의 5번째 글입니다. 여기서는 딕셔너리 형태를 유지하면서 키 구조를 고정하는 `TypedDict`와, 보일러플레이트를 줄인 구조화 클래스를 만드는 `dataclass`를 비교합니다.

## 먼저 던지는 질문

- 이름 있는 키와 값 타입을 가진 딕셔너리는 어떻게 표현할까요?
- 자동 생성된 `__init__`, `__repr__`, `__eq__`가 필요한 가벼운 데이터 객체는 어떻게 만들까요?
- 선택 키, 상속, 불변 객체 같은 패턴은 어디서 쓸까요?

## 큰 그림

![Type Hints in Python 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/05/05-01-big-picture.ko.png)

*Type Hints in Python 101 5장 흐름 개요*

## 왜 이 주제가 중요한가

딕셔너리 기반 버그는 대개 단순합니다. 키 오타, 값 타입 불일치, 빠진 필수 필드입니다. 그런데 이런 실수는 런타임 전까지 숨어 있다가 운영 데이터가 들어온 뒤에야 터지곤 합니다. `TypedDict`는 이 문제를 정적 분석 단계로 끌어옵니다.

반대로 데이터가 단순 저장을 넘어 메서드, 비교, 불변성 같은 의미를 가져야 한다면 일반 딕셔너리보다 객체가 더 잘 맞습니다. 이때 `dataclass`는 수동으로 생성자와 비교 메서드를 작성하는 반복을 줄여 줍니다.

## 한눈에 보는 개념

```text
TypedDict                        dataclass
┌──────────────────┐    ┌──────────────────────┐
│ {"name": str,   │    │ class User:           │
│  "age": int}    │    │   name: str           │
│                  │    │   age: int            │
│ 런타임에서는 dict │    │ __init__ 자동 생성     │
└──────────────────┘    └──────────────────────┘
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| TypedDict | 특정 키와 값 타입을 가진 dict 하위 타입입니다 |
| dataclass | 어노테이션을 읽어 `__init__`, `__repr__`, `__eq__` 등을 만들어 주는 데코레이터입니다 |
| total | TypedDict에서 모든 키를 필수로 볼지 정하는 옵션입니다 |
| frozen | dataclass 인스턴스를 불변으로 만드는 옵션입니다 |
| field | dataclass 필드별 기본값, 팩토리, 비교 정책 등을 설정하는 함수입니다 |

## 바꾸기 전과 후

```python
def create_user(name: str, age: int) -> dict[str, object]:
    return {"name": name, "age": age}

user = create_user("Alice", 30)
print(user["nmae"])  # 런타임 KeyError
```

```python
from typing import TypedDict

class User(TypedDict):
    name: str
    age: int

def create_user(name: str, age: int) -> User:
    return {"name": name, "age": age}

user = create_user("Alice", 30)
# user["nmae"]  # mypy 오류: TypedDict "User"에 없는 키
```

## 단계별로 익히기

### 1단계: `TypedDict` 정의하기

```python
from typing import TypedDict

class UserProfile(TypedDict):
    name: str
    age: int
    email: str

# 올바른 사용
profile: UserProfile = {"name": "Alice", "age": 30, "email": "alice@example.com"}

# 필수 키 누락 — mypy 오류
# bad: UserProfile = {"name": "Alice", "age": 30}
```

런타임에서는 여전히 일반 `dict`입니다. 타입 정보는 분석기에게만 의미가 있습니다.

### 2단계: `total=False`로 선택 키 만들기

```python
from typing import TypedDict

class UserProfile(TypedDict):
    name: str
    age: int

class ExtendedProfile(UserProfile, total=False):
    bio: str
    website: str

# bio와 website는 선택 키
profile: ExtendedProfile = {"name": "Alice", "age": 30}
profile_full: ExtendedProfile = {
    "name": "Alice",
    "age": 30,
    "bio": "Engineer",
    "website": "https://example.com",
}
```

### 3단계: 기본 `dataclass`

```python
from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: int
    quantity: int = 0

product = Product(name="Python Book", price=35)
print(product)          # Product(name='Python Book', price=35, quantity=0)
print(product.name)     # Python Book
print(product == Product("Python Book", 35, 0))  # True
```

필드 어노테이션만 적으면 생성자, 문자열 표현, 동등 비교를 자동으로 얻습니다.

### 4단계: `frozen=True`로 불변 객체 만들기

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

point = Point(1.0, 2.0)
# point.x = 3.0  # FrozenInstanceError — 불변 객체
```

불변 dataclass는 해시 가능하므로 딕셔너리 키나 집합 원소로 쓰기 좋습니다.

### 5단계: `field()`로 세밀하게 설정하기

```python
from dataclasses import dataclass, field

@dataclass
class Order:
    customer: str
    items: list[str] = field(default_factory=list)
    total: int = 0
    _internal: str = field(default="", repr=False, compare=False)

order = Order(customer="Alice")
order.items.append("Python Book")
print(order)  # Order(customer='Alice', items=['Python Book'], total=0)
```

`field(default_factory=list)`는 mutable 기본값 함정을 피하는 핵심 패턴입니다.

## 여기서 먼저 봐야 할 점

- `TypedDict`는 런타임에 dict이고, `dataclass`는 클래스 인스턴스입니다.
- `TypedDict`는 JSON 직렬화나 dict API와 잘 맞습니다.
- `dataclass`는 메서드, 불변성, 값 객체 모델링에 더 적합합니다.
- mutable 기본값에는 반드시 `field(default_factory=...)`를 써야 합니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| dataclass 필드에 `[]`를 기본값으로 둠 | 인스턴스가 같은 리스트를 공유합니다 | `field(default_factory=list)`를 사용합니다 |
| TypedDict를 클래스처럼 다룸 | 메서드와 생성자 개념이 없습니다 | dict 문법으로 다룹니다 |
| TypedDict와 dataclass를 같은 용도로 섞음 | 데이터 의미가 흐려집니다 | dict가 본질이면 TypedDict, 객체가 본질이면 dataclass를 씁니다 |
| 선택 키인데 `total=False`를 빼먹음 | 모든 키가 필수로 해석됩니다 | 상속과 `total=False`를 사용합니다 |
| dataclass를 곧바로 JSON 직렬화 모델로 봄 | 직렬화 정책이 자동으로 붙지 않습니다 | 필요하면 `asdict()` 또는 Pydantic을 함께 검토합니다 |

## 실무에서는 이렇게 연결됩니다

- API 응답 본문은 `TypedDict`로 JSON 형태를 정확히 적을 수 있습니다.
- 애플리케이션 설정 객체는 `dataclass`로 표현하면 가독성이 좋습니다.
- 도메인 값 객체는 `frozen=True` dataclass로 두면 비교와 해시가 편해집니다.
- DB 조회 결과는 `TypedDict`, 내부 로직 객체는 `dataclass`로 나누는 패턴이 흔합니다.

## 실무 판단 기준

숙련된 개발자는 먼저 데이터의 본질을 봅니다. "이것은 키가 정해진 딕셔너리인가"라는 질문에 예라면 `TypedDict`가 맞고, "이것은 필드와 동작을 가진 객체인가"라는 질문에 예라면 `dataclass`가 맞습니다. 기능 차이보다 의미 차이로 판단하는 편이 흔들림이 적습니다.

외부 시스템과 주고받는 JSON 호환성이 중요하다면 `TypedDict`가 자연스럽고, 내부 도메인 모델이나 불변 값 객체가 필요하다면 `dataclass`가 훨씬 읽기 좋습니다.

## 체크리스트

- [ ] 키 구조가 정해진 dict 데이터에 `TypedDict`를 사용했습니다
- [ ] 구조화된 객체에는 `dataclass`를 고려했습니다
- [ ] mutable 기본값에는 `field(default_factory=...)`를 적용했습니다
- [ ] 불변 값 객체에는 `frozen=True`를 검토했습니다
- [ ] dict와 객체 중 어떤 의미가 더 맞는지 먼저 판단했습니다

## 연습 문제

1. `title`, `author`, `year`, 선택 필드 `isbn`을 가진 `BookInfo` TypedDict를 정의해 보세요.

2. `owner`, `balance`를 가진 `BankAccount` dataclass를 만들고 `deposit`, `withdraw` 메서드를 추가해 보세요.

3. `dict[str, Any]`를 반환하던 함수를 `TypedDict` 반환으로 바꾸고, 키 오타를 mypy가 잡는지 확인해 보세요.

## 정리와 다음 글

`TypedDict`는 딕셔너리 형태를 유지한 채 키와 값 타입을 고정하고, `dataclass`는 구조화된 객체를 적은 코드로 만들게 해 줍니다. 두 도구 모두 타입 검사기와 잘 맞지만, 문제를 푸는 방식은 다릅니다. 데이터를 dict로 볼지 객체로 볼지 먼저 결정하면 선택이 쉬워집니다.

다음 글에서는 상속 없이 인터페이스를 정의하는 `Protocol`과 structural typing을 살펴보겠습니다.

## 실전 패턴 추가: TypeVar, Generic, Protocol을 함께 쓰는 방법

타입 힌트가 본격적으로 효율을 내는 구간은 공통 유틸리티와 도메인 인터페이스를 다룰 때입니다. 단순한 `list[int]`를 넘어서 `TypeVar`, `Generic`, `Protocol`을 함께 쓰면 구체 클래스에 묶이지 않는 API를 만들 수 있습니다.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

T = TypeVar("T")
K = TypeVar("K")


class SupportsKey(Protocol[K]):
    def key(self) -> K:
        ...


class Repository(Protocol[T]):
    def add(self, item: T) -> None:
        ...

    def all(self) -> list[T]:
        ...


@dataclass
class User:
    user_id: int
    name: str

    def key(self) -> int:
        return self.user_id


class InMemoryRepository(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def add(self, item: T) -> None:
        self._items.append(item)

    def all(self) -> list[T]:
        return self._items


def index_by_key(items: list[SupportsKey[K]]) -> dict[K, SupportsKey[K]]:
    return {item.key(): item for item in items}
```

```python
repo: Repository[User] = InMemoryRepository()
repo.add(User(user_id=1, name="A"))
repo.add(User(user_id=2, name="B"))
indexed = index_by_key(repo.all())
```

이 패턴의 장점은 구현 교체 비용이 낮다는 점입니다. `Repository[User]` 계약만 지키면 메모리 저장소를 DB 저장소로 바꿔도 상위 서비스 타입 시그니처를 유지할 수 있습니다. 또한 Protocol 기반 설계는 상속 계층 없이도 구조적 타이핑으로 계약을 검사할 수 있어, 기존 코드에 점진적으로 타입 안전성을 도입할 때 특히 유리합니다.

## 처음 질문으로 돌아가기

- **이름 있는 키와 값 타입을 가진 딕셔너리는 어떻게 표현할까요?**
  - 본문의 기준은 TypedDict와 dataclass를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **자동 생성된 `__init__`, `__repr__`, `__eq__`가 필요한 가벼운 데이터 객체는 어떻게 만들까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **선택 키, 상속, 불변 객체 같은 패턴은 어디서 쓸까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Type Hints in Python 101 (1/10): Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [Type Hints in Python 101 (2/10): 기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Type Hints in Python 101 (3/10): Optional과 Union](./03-optional-and-union.md)
- [Type Hints in Python 101 (4/10): 함수 타입 힌트](./04-function-type-hints.md)
- **TypedDict와 dataclass (현재 글)**
- Protocol과 structural typing (예정)
- Generic 이해하기 (예정)
- mypy와 pyright 사용하기 (예정)
- Pydantic과 타입 힌트 (예정)
- 타입 힌트를 잘 쓰는 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — typing.TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict)
- [Python 공식 문서 — dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [PEP 589 — TypedDict](https://peps.python.org/pep-0589/)
- [Real Python — Data Classes](https://realpython.com/python-data-classes/)

Tags: Python, Type Hints, TypedDict, dataclass, 구조화 데이터, 타입 안전

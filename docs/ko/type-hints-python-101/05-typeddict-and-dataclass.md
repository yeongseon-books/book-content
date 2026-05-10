---
series: type-hints-python-101
episode: 5
title: TypedDict와 dataclass
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
  - TypedDict
  - dataclass
  - 구조화 데이터
  - 타입 안전
seo_description: TypedDict와 dataclass로 딕셔너리와 객체 구조에 타입 안전성을 부여하는 방법을 다룹니다.
last_reviewed: '2026-05-04'
---

# TypedDict와 dataclass

> Type Hints in Python 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: `dict[str, Any]`보다 정확하게 딕셔너리 구조를 타입으로 정의할 수 있을까요?

> API 응답, 설정 파일, JSON 데이터처럼 키-값 구조가 고정된 딕셔너리는 `TypedDict`로, 비즈니스 도메인 모델은 `dataclass`로 타입 안전하게 정의할 수 있습니다. 이 글에서는 두 도구의 차이와 사용 기준을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- TypedDict로 딕셔너리의 키-값 타입을 정의하는 방법
- dataclass와 frozen dataclass 활용
- TypedDict vs dataclass 선택 기준
- NamedTuple과의 비교

## 왜 중요한가

`dict[str, Any]`는 아무 키나 넣을 수 있어 타입 안전성이 없습니다. `TypedDict`와 `dataclass`를 사용하면 구조가 명확한 데이터에 타입 검증을 적용하여 실수를 사전에 방지합니다.

> TypedDict = 딕셔너리의 스키마, dataclass = 객체의 스키마

두 도구는 목적이 다릅니다. TypedDict는 딕셔너리 형태를 유지하면서 타입을 강화하고, dataclass는 새로운 타입을 만듭니다.

## 핵심 개념 잡기

> TypedDict vs dataclass

```
TypedDict                      dataclass
─────────────────             ─────────────────
딕셔너리 구조 유지              새로운 클래스 생성
user["name"]                  user.name
JSON 호환 유지                 메서드 추가 가능
런타임은 일반 dict              런타임은 클래스 인스턴스
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| TypedDict | 키별 값 타입을 정의한 딕셔너리 타입입니다 |
| dataclass | `@dataclass` 데코레이터로 자동 생성되는 데이터 클래스입니다 |
| frozen dataclass | 생성 후 속성 변경이 불가능한 불변 dataclass입니다 |
| NamedTuple | 이름 있는 필드를 가진 불변 튜플입니다 |
| total | TypedDict에서 모든 키의 필수 여부를 제어합니다 |

## Before / After

느슨한 dict를 TypedDict로 구조화합니다.

```python
# before: 어떤 키가 있는지 알 수 없음
def create_user(name, age):
    return {"name": name, "age": age, "active": True}
```

```python
# after: 키와 값 타입이 명확
from typing import TypedDict

class User(TypedDict):
    name: str
    age: int
    active: bool

def create_user(name: str, age: int) -> User:
    return {"name": name, "age": age, "active": True}
```

## 단계별 실습

### Step 1: TypedDict 기본

```python
from typing import TypedDict


class UserProfile(TypedDict):
    name: str
    age: int
    email: str


# TypedDict는 런타임에는 일반 dict
user: UserProfile = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com",
}

print(type(user))        # <class 'dict'>
print(user["name"])      # Alice

# mypy가 잡아주는 오류들:
# user["age"] = "thirty"  # error: incompatible type
# user["phone"] = "123"   # error: extra key
# del user["name"]        # error: required key


# 선택적 키 — NotRequired (Python 3.11+)
from typing import NotRequired

class Config(TypedDict):
    host: str
    port: int
    debug: NotRequired[bool]

config1: Config = {"host": "localhost", "port": 8080}            # OK
config2: Config = {"host": "localhost", "port": 8080, "debug": True}  # OK
```

### Step 2: dataclass 기본

```python
from dataclasses import dataclass


@dataclass
class Product:
    name: str
    price: float
    category: str
    in_stock: bool = True


# 자동 생성: __init__, __repr__, __eq__
product = Product(name="노트북", price=1200000, category="전자기기")
print(product)
# Product(name='노트북', price=1200000, category='전자기기', in_stock=True)

# 속성 접근
print(f"제품명: {product.name}")
print(f"가격: {product.price:,.0f}원")

# 동등 비교
product2 = Product(name="노트북", price=1200000, category="전자기기")
print(product == product2)  # True (값 기반 비교)
```

### Step 3: frozen dataclass (불변)

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "KRW"


price = Money(50000)
print(price)  # Money(amount=50000, currency='KRW')

# 불변 — 수정 시도하면 에러
# price.amount = 60000  # FrozenInstanceError

# replace()로 새 인스턴스 생성
discounted = replace(price, amount=45000)
print(discounted)  # Money(amount=45000, currency='KRW')

# hashable — set이나 dict 키로 사용 가능
prices = {Money(1000), Money(2000), Money(1000)}
print(len(prices))  # 2 (중복 제거)
```

### Step 4: NamedTuple

```python
from typing import NamedTuple


class Point(NamedTuple):
    x: float
    y: float


class RGB(NamedTuple):
    red: int
    green: int
    blue: int


# NamedTuple은 불변 + 인덱스 접근 가능
p = Point(3.5, 7.2)
print(f"x={p.x}, y={p.y}")  # 이름 접근
print(f"x={p[0]}, y={p[1]}")  # 인덱스 접근

# 언패킹
x, y = p
print(f"언패킹: ({x}, {y})")

# 튜플 연산 지원
color = RGB(255, 128, 0)
print(f"RGB: {color}")
print(f"hex: #{color.red:02x}{color.green:02x}{color.blue:02x}")
# hex: #ff8000
```

### Step 5: 선택 기준

```python
from typing import TypedDict
from dataclasses import dataclass


# 사용 기준 1: JSON 호환이 필요하면 → TypedDict
class APIResponse(TypedDict):
    status: int
    data: dict[str, str]
    message: str

response: APIResponse = {
    "status": 200,
    "data": {"user": "Alice"},
    "message": "OK",
}
# json.dumps(response) 바로 가능


# 사용 기준 2: 메서드가 필요하면 → dataclass
@dataclass
class Rectangle:
    width: float
    height: float

    @property
    def area(self) -> float:
        return self.width * self.height

    def scale(self, factor: float) -> "Rectangle":
        return Rectangle(self.width * factor, self.height * factor)

rect = Rectangle(10, 5)
print(f"면적: {rect.area}")  # 50.0
print(rect.scale(2))  # Rectangle(width=20, height=10)


# 사용 기준 3: 불변 값 객체 → frozen dataclass 또는 NamedTuple
@dataclass(frozen=True)
class Coordinate:
    lat: float
    lng: float

coord = Coordinate(37.5665, 126.9780)
# 딕셔너리 키로 사용 가능
locations = {coord: "서울시청"}
print(locations[Coordinate(37.5665, 126.9780)])  # 서울시청
```

## 이 코드에서 주목할 점

- TypedDict는 딕셔너리 형태를 유지하면서 키-값 타입을 검증합니다
- dataclass는 `__init__`, `__repr__`, `__eq__`를 자동 생성합니다
- frozen dataclass는 불변이며 hashable하여 set/dict 키로 사용 가능합니다
- 선택 기준: JSON 호환 → TypedDict, 메서드 필요 → dataclass

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| TypedDict를 런타임 검증으로 착각 | 런타임에는 일반 dict입니다 | Pydantic으로 런타임 검증합니다 |
| dataclass에 가변 기본값 | 인스턴스 간 공유됩니다 | `field(default_factory=list)`를 사용합니다 |
| frozen이 아닌 dataclass를 dict 키로 | unhashable 에러가 발생합니다 | `frozen=True`를 추가합니다 |
| TypedDict 상속 오남용 | 복잡한 상속 구조는 혼란을 줍니다 | 단순한 구조를 유지합니다 |
| NamedTuple에 가변 속성 기대 | NamedTuple은 항상 불변입니다 | 가변이 필요하면 dataclass를 사용합니다 |

## 실무에서 이렇게 쓰입니다

- API 응답 타입을 TypedDict로 정의하여 JSON 호환성을 유지합니다
- 도메인 모델을 dataclass로 정의하여 비즈니스 로직을 캡슐화합니다
- 불변 설정값을 frozen dataclass로 관리합니다
- 데이터베이스 행을 NamedTuple로 표현합니다
- Pydantic의 BaseModel과 dataclass를 목적에 따라 구분합니다

## 현업 개발자는 이렇게 생각합니다

TypedDict와 dataclass 선택은 "데이터가 딕셔너리로 존재해야 하는가?"로 판단합니다. JSON API 경계에서는 TypedDict, 내부 도메인에서는 dataclass가 자연스럽습니다. frozen dataclass는 함수형 프로그래밍의 불변 값 객체와 같은 역할을 합니다.

실무에서는 하나만 고집하지 않고 혼합 사용합니다. 외부 데이터는 TypedDict로 받고, 내부에서 dataclass 인스턴스로 변환하는 패턴이 깔끔합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **TypedDict 활용** — JSON-like 데이터에 가성비가 큽니다.
- **dataclass 표준** — 값 객체는 dataclass가 표준입니다.
- **frozen 우선** — 변경 가능성을 입증한 뒤에만 가변으로 둡니다.
- **Required/NotRequired** — 선택 필드를 명시적으로 표현합니다.
- **Pydantic 비교** — 검증이 필요하면 Pydantic이 자연스럽습니다.

## 체크리스트

- [ ] TypedDict로 딕셔너리 구조를 정의할 수 있다
- [ ] dataclass로 데이터 클래스를 생성할 수 있다
- [ ] frozen dataclass의 용도와 제약을 설명할 수 있다
- [ ] TypedDict, dataclass, NamedTuple의 선택 기준을 적용할 수 있다
- [ ] NotRequired로 선택적 키를 정의할 수 있다

## 연습 문제

1. 도서 정보(제목, 저자, 가격, ISBN)를 TypedDict와 dataclass 각각으로 정의하고 차이를 비교하세요.
2. frozen dataclass로 불변 좌표 타입을 만들고 set에서 중복 제거를 확인하세요.
3. JSON API 응답을 TypedDict로 정의하고, dataclass로 변환하는 함수를 작성하세요.

## 정리 및 다음 글 안내

TypedDict는 딕셔너리에, dataclass는 클래스에 타입 안전성을 부여합니다. 선택 기준은 데이터의 형태와 용도에 따라 달라집니다. 다음 글에서는 구조적 타입 체계인 **Protocol과 structural typing**을 다룹니다.

<!-- toc:begin -->
- [Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Optional과 Union](./03-optional-and-union.md)
- [함수 타입 힌트](./04-function-type-hints.md)
- **TypedDict와 dataclass (현재 글)**
- [Protocol과 structural typing](./06-protocol-and-structural-typing.md)
- [Generic 이해하기](./07-generic.md)
- [mypy와 pyright 사용하기](./08-mypy-and-pyright.md)
- [Pydantic과 타입 힌트](./09-pydantic-and-type-hints.md)
- [타입 힌트를 잘 쓰는 기준](./10-type-hints-best-practices.md)
<!-- toc:end -->

## 참고 자료

- [PEP 589 — TypedDict](https://peps.python.org/pep-0589/)
- [Python 공식 문서 — dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [PEP 655 — Marking individual TypedDict items as required or not-required](https://peps.python.org/pep-0655/)
- [Real Python — Data Classes in Python](https://realpython.com/python-data-classes/)

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


![Type Hints in Python 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/05/05-01-big-picture.ko.png)
*Type Hints in Python 101 5장 흐름 개요*

## 먼저 던지는 질문

- 이름 있는 키와 값 타입을 가진 딕셔너리는 어떻게 표현할까요?
- 자동 생성된 `__init__`, `__repr__`, `__eq__`가 필요한 가벼운 데이터 객체는 어떻게 만들까요?
- 선택 키, 상속, 불변 객체 같은 패턴은 어디서 쓸까요?

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
# user["nmae"] # mypy 오류: TypedDict "User"에 없는 키
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
# 불량: UserProfile = {"name": "Alice", "age": 30}
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
# point.x = 3.0 # FrozenInstanceError — 불변
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


## TypedDict와 dataclass 선택 실전표

| 상황 | TypedDict | dataclass |
| --- | --- | --- |
| JSON 입출력 중심 | Pass | 제한적 |
| 메서드/동작 포함 모델 | 제한적 | Pass |
| 불변 값 객체 | 어려움 | `frozen=True`로 용이 |
| 키 오타 탐지 | Pass | 해당 없음 |
| 직렬화 편의 | dict 그대로 | `asdict()` 필요 |

## mypy 오류와 수정

```python
from typing import TypedDict

class Profile(TypedDict):
    username: str
    age: int

profile: Profile = {"username": "min", "age": "20"}
```

```text
example.py:7: error: Incompatible types (expression has type "str", TypedDict item "age" has type "int")  [typeddict-item]
```

```python
profile: Profile = {"username": "min", "age": 20}
```

## dataclass 적용 전후 비교

```python
# before
class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
```

```python
# after
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float
```

코드량이 줄고 비교/표현 계약이 명확해집니다.


## mypy 오류를 읽는 순서

실무에서는 오류 개수보다 읽는 순서가 더 중요합니다. 다음 순서를 고정하면 수정 시간이 크게 줄어듭니다.

1. `error:` 뒤의 핵심 문장을 먼저 읽고, 기대 타입과 실제 타입을 분리합니다.
2. 함수 시그니처 오류인지, 호출부 오류인지 위치를 구분합니다.
3. `Any`가 끼어 있는지 확인합니다. `Any`가 있으면 오류 메시지가 흐려집니다.
4. 마지막으로 수정 코드를 넣고 같은 파일만 다시 검사합니다.

```bash
mypy content/type-hints-python-101/examples/episode.py
```

```text
example.py:42: error: Incompatible return value type (got "str", expected "int")  [return-value]
example.py:51: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
Found 2 errors in 1 file (checked 1 source file)
```

위 출력에서 첫 줄은 반환 계약 위반, 둘째 줄은 Optional 처리 누락입니다. 즉, 타입 힌트 작성과 별개로 **오류를 분류해서 고치는 습관**이 필요합니다.

## 팀 적용 체크포인트

| 항목 | 느슨한 상태 | 권장 상태 |
| --- | --- | --- |
| 공개 함수 시그니처 | 일부 누락 | 모두 명시 |
| `Any` 사용 | 편의상 광범위 사용 | 경계에서만 제한적 사용 |
| Optional 처리 | 호출부 임의 처리 | `None` 분기 패턴 고정 |
| 정적 검사 | 로컬 선택 실행 | CI 필수 게이트 |
| 코드 리뷰 | 스타일 중심 | 타입 계약 위반 중심 |

이 체크포인트를 팀 규칙으로 두면 신규 코드와 레거시 코드의 품질 편차를 줄일 수 있습니다.


## 실전 보강: 타입 힌트 + mypy 오류 해결 루프

아래 예시는 타입 힌트가 문서가 아니라 검증 가능한 계약이라는 점을 분명하게 보여 줍니다.

```python
from typing import TypedDict

class Payment(TypedDict):
    order_id: int
    amount: int
    currency: str


def normalize_amount(raw: int | str) -> int:
    if isinstance(raw, int):
        return raw
    if raw.isdigit():
        return int(raw)
    raise ValueError("amount must be int or numeric string")


def build_payment(order_id: int, amount: int | str, currency: str | None) -> Payment:
    if currency is None:
        raise ValueError("currency is required")
    return {
        "order_id": order_id,
        "amount": normalize_amount(amount),
        "currency": currency.upper(),
    }
```

```python
# 오류를 일부러 넣은 버전

def build_payment(order_id: int, amount: int | str, currency: str | None) -> Payment:
    return {
        "order_id": str(order_id),
        "amount": amount,
        "currency": currency.upper(),
    }
```

```text
example.py:24: error: Incompatible types (expression has type "str", TypedDict item "order_id" has type "int")  [typeddict-item]
example.py:25: error: Incompatible types (expression has type "int | str", TypedDict item "amount" has type "int")  [typeddict-item]
example.py:26: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
Found 3 errors in 1 file (checked 1 source file)
```

위 메시지는 각각 키 타입 불일치, Union 좁히기 누락, Optional 처리 누락을 의미합니다. 즉, 정적 분석기가 실제 운영 버그 후보를 실행 전에 보여 준다는 뜻입니다.

## 적용 전후 요약

| 구분 | before (느슨한 타입) | after (구체 타입) |
| --- | --- | --- |
| 입력 계약 | `dict`, `Any` 위주 | `TypedDict`, `Union`, `Optional` 명시 |
| 오류 발견 시점 | 테스트/운영 단계 | 커밋 전 타입 검사 단계 |
| 코드 리뷰 초점 | 스타일/명명 | 계약 위반/경계 검증 |
| 리팩터링 안정성 | 변경 영향 추적 어려움 | 시그니처 기반 영향 추적 가능 |

## Optional vs Union 판단 표

| 상황 | 권장 타입 | 이유 |
| --- | --- | --- |
| 값이 없을 수 있음 | `T | None` | 부재 가능성을 명시적으로 표현 |
| 입력 포맷이 둘 이상 | `T1 | T2` | 허용 범위를 코드로 고정 |
| 외부 입력 정규화 | `str | int` -> `int` | 경계에서 한 번만 변환 |
| 내부 도메인 모델 | 가능한 단일 타입 유지 | 분기 복잡도 축소 |

## Protocol vs ABC 판단 표

| 기준 | Protocol | ABC |
| --- | --- | --- |
| 호환성 기준 | 구조(메서드/속성) | 명시적 상속 |
| 외부 클래스 수용 | 유리함 | 불리함 |
| 공통 구현 제공 | 제한적 | 유리함 |
| 대규모 플러그인 구조 | 유리함 | 상황별 |

## 실무 패턴: 타입 힌트 적용 순서

1. 공개 함수와 반환 타입부터 고정합니다.
2. `Any`를 반환하는 경계 함수를 구체 타입으로 줄입니다.
3. `Optional`과 `Union` 분기를 helper 함수로 끌어올립니다.
4. mypy/pyright를 CI에 연결해 회귀를 막습니다.

```bash
mypy content/type-hints-python-101/ko
```

```text
Success: no issues found in N source files
```

위 결과가 나오더라도 끝이 아닙니다. 새로운 기능을 추가할 때 같은 원칙을 반복해 계약을 유지해야 타입 힌트가 장기적으로 품질을 지켜 줍니다.


## 추가 사례: 주문 처리 모듈 타입 하드닝

아래 코드는 실제로 자주 보는 레거시 패턴입니다.

```python
from typing import Any


def build_invoice(payload: dict[str, Any]) -> dict[str, Any]:
    user = payload.get("user")
    total = payload.get("total")
    return {
        "email": user.get("email"),
        "total": int(total),
    }
```

이 구현은 `user` 누락, `total` 비정상 값, 잘못된 타입을 조용히 통과시킵니다. 아래처럼 경계를 분리하면 검증 경로가 명확해집니다.

```python
from typing import TypedDict

class UserInfo(TypedDict):
    email: str

class InvoicePayload(TypedDict):
    user: UserInfo
    total: int | str

class InvoiceResult(TypedDict):
    email: str
    total: int


def parse_total(raw: int | str) -> int:
    if isinstance(raw, int):
        return raw
    if raw.isdigit():
        return int(raw)
    raise ValueError("total must be int or numeric string")


def build_invoice(payload: InvoicePayload) -> InvoiceResult:
    return {
        "email": payload["user"]["email"],
        "total": parse_total(payload["total"]),
    }
```

```text
before: 런타임 오류 중심
after: 타입 오류 + 명시적 예외 중심
```

## mypy 출력 해석 연습

```text
service.py:18: error: Key "email" of TypedDict "UserInfo" cannot be deleted  [misc]
service.py:29: error: Argument 1 to "parse_total" has incompatible type "float"; expected "int | str"  [arg-type]
service.py:36: error: Missing key "user" for TypedDict "InvoicePayload"  [typeddict-item]
```

- 첫 번째 오류는 구조적 계약 위반입니다.
- 두 번째 오류는 허용 타입 범위를 벗어난 호출입니다.
- 세 번째 오류는 필수 필드 누락입니다.

즉, 오류는 단순 문법 문제가 아니라 **도메인 계약 위반 지표**로 해석해야 합니다.

## 운영 적용 포인트

- 새 기능 PR에서는 최소한 공개 함수의 반환 타입을 반드시 명시합니다.
- 외부 입력 파싱 함수에는 `Optional`/`Union` 처리 분기를 강제합니다.
- 리뷰에서 `Any` 추가가 보이면 대체 타입 후보를 함께 요구합니다.
- CI에서는 타입 검사 실패를 테스트 실패와 동등하게 취급합니다.


## 보강 메모: 실전 리뷰에서 확인하는 타입 힌트 패턴

### 패턴 1: 경계 파싱 함수를 별도로 둡니다

```python
def parse_positive_int(raw: int | str) -> int:
    if isinstance(raw, int):
        value = raw
    elif raw.isdigit():
        value = int(raw)
    else:
        raise ValueError("value must be int or numeric string")

    if value <= 0:
        raise ValueError("value must be positive")
    return value
```

이 방식은 서비스 본문에서 반복되는 분기와 형변환을 줄여 줍니다.

### 패턴 2: Optional 값을 바로 사용하지 않습니다

```python
def normalize_display_name(value: str | None) -> str:
    if value is None:
        return "anonymous"
    stripped = value.strip()
    if stripped == "":
        return "anonymous"
    return stripped
```

### 패턴 3: 검증 결과 타입을 반환 타입에 고정합니다

```python
from typing import TypedDict

class NormalizedUser(TypedDict):
    id: int
    email: str


def build_user(user_id: int, email: str) -> NormalizedUser:
    return {"id": user_id, "email": email.lower()}
```

반환 타입 고정은 호출부의 예측 가능성을 크게 높입니다.

## 코드 리뷰 체크 질문

- 이 함수 시그니처만 보고 입력/출력을 이해할 수 있는가?
- `None` 가능성은 본문에서 실제로 처리되었는가?
- `Any`가 도입되면 대체 가능한 구체 타입은 없는가?
- mypy 오류를 숨기는 `type: ignore`가 정말 필요한가?


## 짧은 실전 확인

아래 명령으로 수정 직후 타입 검사를 바로 확인합니다.

```bash
mypy path/to/example.py
```

검사 결과가 통과해도 `Optional` 분기와 예외 메시지 품질까지 함께 점검해야 실제 운영에서 디버깅 비용을 줄일 수 있습니다.


TypedDict와 dataclass를 함께 쓰는 팀에서는 보통 외부 입출력 경계는 TypedDict로, 내부 계산 모델은 dataclass로 분리합니다. 이렇게 두 계층을 나누면 직렬화 형식 변화와 도메인 로직 변경을 독립적으로 다룰 수 있어 유지보수성이 높아집니다.


## 비교 기준 보강: TypedDict vs dataclass

| 비교 항목 | TypedDict | dataclass |
| --- | --- | --- |
| 런타임 형태 | `dict` | 클래스 인스턴스 |
| 키/필드 오타 탐지 | 강함(정적) | 필드명 기준(정적/런타임) |
| 메서드 추가 | 제한적 | 자연스러움 |
| 불변성 모델링 | 직접 구현 필요 | `frozen=True`로 간결 |

```python
from dataclasses import dataclass
from typing import TypedDict

class PaymentRow(TypedDict):
    amount: int
    currency: str

@dataclass(frozen=True)
class Payment:
    amount: int
    currency: str
```

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

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/type-hints-python-101/ko)
Tags: Python, Type Hints, TypedDict, dataclass, 구조화 데이터, 타입 안전

---
series: type-hints-python-101
episode: 1
title: "Type Hints in Python 101 (1/10): Python type hint란 무엇인가?"
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
  - 타입 힌트
  - 정적 분석
  - mypy
  - 코드 품질
seo_description: Python 타입 힌트의 개념, 등장 배경, 기본 문법과 활용 이유를 살펴봅니다.
last_reviewed: '2026-05-12'
---

# Type Hints in Python 101 (1/10): Python type hint란 무엇인가?

작은 스크립트에서는 `data`, `value`, `result` 같은 이름만으로도 버틸 수 있습니다. 하지만 코드가 길어지고 함수가 여러 파일을 오가기 시작하면, 호출자가 무엇을 넘겨야 하고 무엇을 돌려받는지 시그니처만 보고 알 수 있어야 합니다.

이 글은 Type Hints (Python) 101 시리즈의 첫 번째 글입니다. 여기서는 타입 힌트가 무엇이고, Python의 동적 타이핑과 어떻게 공존하며, 왜 실무에서 빠르게 가치가 드러나는지부터 정리합니다.


![Type Hints in Python 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/01/01-01-big-picture.ko.png)
*Type Hints in Python 101 1장 흐름 개요*

## 먼저 던지는 질문

- 타입 힌트는 정적 타입 언어의 타입 선언과 무엇이 다를까요?
- PEP 484가 해결하려던 문제는 무엇이었을까요?
- 변수, 매개변수, 반환값에 어떤 문법으로 타입을 붙일까요?

## 왜 이 주제가 중요한가

Python은 유연합니다. 같은 변수에 문자열도 넣고, 리스트도 넣고, `None`도 넣을 수 있습니다. 이 유연성은 빠른 개발에는 유리하지만, 팀 단위 코드베이스에서는 함수 계약이 숨어 버리는 문제가 생깁니다. `calculate_total(data)`라는 시그니처만 보고는 `data`가 리스트인지, 딕셔너리인지, 모델 객체인지 알기 어렵습니다.

타입 힌트는 이 모호함을 줄입니다. 호출자는 함수 몸체를 열어 보지 않아도 입력과 출력의 형태를 먼저 읽을 수 있고, IDE와 정적 분석 도구는 그 계약을 코드 실행 전에 검증할 수 있습니다. 즉, 타입 힌트는 문서이면서 동시에 자동 검사 대상입니다.

## 한눈에 보는 개념

타입 힌트는 선택적 주석이지만, 도구는 이 주석을 진지하게 읽습니다.

```text
def greet(name: str) -> str:
         ^^^^  ^^^     ^^^
         매개변수 이름  타입    반환 타입
              │               │
        Python 런타임은 무시함
              │               │
        mypy/pyright는 정적으로 검증함
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 타입 힌트 | 변수나 표현식이 기대하는 타입을 적는 주석성 어노테이션입니다 |
| PEP 484 | 2014년에 타입 힌트를 표준화한 Python 제안서입니다 |
| 정적 분석 | 코드를 실행하지 않고 오류 가능성을 검사하는 방식입니다 |
| 동적 타이핑 | 타입을 컴파일 시점이 아니라 실행 시점에 다루는 모델입니다 |
| 점진적 타이핑 | 기존 코드베이스에 타입 힌트를 조금씩 확장하는 방식입니다 |

## 바꾸기 전과 후

타입 힌트가 없으면 함수 계약을 시그니처에서 읽을 수 없습니다.

```python
def calculate_total(prices, tax_rate):
    subtotal = sum(prices)
    return int(subtotal * (1 + tax_rate))

# 가격이 목록 인지 튜플 인지, 세금 세율이 무엇인지 시그니처 단독 수는 없습니다.
```

```python
def calculate_total(prices: list[int], tax_rate: float) -> int:
    subtotal = sum(prices)
    return int(subtotal * (1 + tax_rate))

# 가격은 목록[int], 세금 세율은 float, 반환값은 int라는 서명이 불편한 것입니다.
```

## 단계별로 익히기

### 1단계: 함수 매개변수와 반환값에 붙이기

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

result = greet("Alice")  # OK
# Greeting(42) # mypy 오류: 인수 1에 호환되지 않는 유형 "int"가 있습니다.
```

기본 문법은 `매개변수: 타입`, `-> 반환타입`입니다. 중요한 점은 Python이 이 힌트를 실행 시점에 강제하지 않는다는 사실입니다.

### 2단계: 변수에도 붙이기

```python
count: int = 0
name: str = "Alice"
prices: list[int] = [1000, 2000, 3000]
config: dict[str, str] = {"host": "localhost", "port": "8080"}
```

변수 주석은 `이름: 타입 = 값` 형태를 씁니다. 다만 값만 봐도 타입이 분명한 지역 변수는 굳이 모두 적지 않아도 됩니다.

### 3단계: 내장 제네릭 타입 쓰기

```python
# Python 3.9+ — 내장 타입을 직접 사용합니다.
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 95, "Bob": 87}
coordinates: tuple[float, float] = (37.5, 127.0)
unique_ids: set[int] = {1, 2, 3}
```

Python 3.9부터는 `typing.List[str]` 대신 `list[str]`처럼 표준 컬렉션 타입을 바로 사용할 수 있습니다.

### 4단계: 클래스에도 적용하기

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hi, I'm {self.name}."

user = User("Alice", 30)
print(user.greet())
```

`__init__`의 반환 타입은 항상 `None`입니다. `self`는 별도로 적지 않아도 분석기가 추론합니다.

### 5단계: 타입 검사기로 확인하기

```bash
pip install mypy
mypy app.py
```

```python
# app.py
def add(a: int, b: int) -> int:
    return a + b

add("hello", "world")  # mypy: Argument 1 has incompatible type "str"
```

이 순간부터 타입 힌트는 단순 메모가 아니라 자동으로 검증되는 계약이 됩니다.

## 여기서 먼저 봐야 할 점

- 타입 힌트 문법의 핵심은 `:`와 `->` 두 가지입니다.
- Python 런타임은 타입 힌트를 무시하므로, 잘못된 값이 들어와도 실행 자체는 될 수 있습니다.
- 실제 가치는 mypy, pyright, IDE 자동완성 같은 도구가 힌트를 읽을 때 생깁니다.
- 모든 지역 변수보다 공개 함수 시그니처에 먼저 붙일 때 투자 대비 효과가 큽니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| 타입 힌트가 런타임 검증도 해 준다고 생각함 | Python은 힌트를 강제하지 않습니다 | 검증은 mypy, pyright, Pydantic 같은 도구에 맡깁니다 |
| Python 3.9+에서도 `typing.List`를 계속 씀 | 불필요한 임포트가 늘어납니다 | `list[str]`처럼 내장 타입을 바로 씁니다 |
| 모든 지역 변수에 타입을 붙임 | 코드만 길어지고 읽기 어려워집니다 | 추론 가능한 지역 변수는 생략합니다 |
| `__init__`에 `-> None`을 빼먹음 | 시그니처가 덜 분명해집니다 | 생성자는 항상 `-> None`을 적습니다 |
| 타입 힌트와 런타임 데이터 검증을 혼동함 | 잘못된 JSON 입력은 막지 못합니다 | 외부 데이터 검증은 Pydantic 같은 도구로 처리합니다 |

## 실무에서는 이렇게 연결됩니다

- FastAPI는 타입 힌트로 API 문서와 요청 스키마를 생성합니다.
- VS Code와 Pylance는 타입 정보를 바탕으로 자동완성과 오류 표시를 강화합니다.
- 대규모 코드베이스는 mypy를 CI에 넣어 리팩터링 회귀를 미리 잡습니다.
- 라이브러리는 `.pyi` 스텁 파일로 사용자에게 타입 정보를 제공합니다.

## 실무 판단 기준

시니어 엔지니어는 타입 힌트를 규칙 준수 항목보다 커뮤니케이션 도구로 봅니다. 여섯 달 뒤의 동료가 함수 몸체를 열어 보기 전에, 시그니처만 읽고도 안전하게 호출할 수 있게 만드는 편이 더 중요합니다. 좋은 타입 시그니처 하나가 긴 docstring보다 더 빨리 오해를 줄일 때가 많습니다.

또한 타입 힌트는 규모가 커질수록 복리처럼 이익이 커집니다. 처음에는 함수 몇 개에 불과하지만, 시간이 지나면 자동완성 품질, 리팩터링 안정성, 코드 리뷰 속도, 신규 입사자 온보딩 속도까지 영향을 줍니다.

## 체크리스트

- [ ] 함수 매개변수에 타입을 붙였습니다
- [ ] 함수 반환 타입을 명시했습니다
- [ ] Python 3.9+ 스타일의 내장 제네릭 타입을 사용했습니다
- [ ] mypy 또는 pyright로 타입 힌트를 검증할 준비가 되어 있습니다
- [ ] 추론 가능한 지역 변수에는 과한 주석을 달지 않았습니다

## 연습 문제

1. 예전에 작성한 Python 파일 하나를 골라 모든 함수 시그니처에 타입 힌트를 추가해 보세요. 그런 다음 `mypy`를 실행해 오류를 정리해 보세요.

2. `width: float`, `height: float`, `area() -> float`를 가진 `Rectangle` 클래스를 작성하고 mypy로 검사해 보세요.

3. 일부러 세 가지 타입 오류를 넣어 보세요. 잘못된 인자 타입, 잘못된 반환 타입, 누락된 반환 힌트를 각각 넣고 분석기가 어떤 메시지를 내는지 확인해 보세요.

## 정리와 다음 글

타입 힌트는 Python 코드의 실행 방식을 바꾸지 않습니다. 대신 함수와 데이터의 계약을 코드 위에 명시하고, 정적 분석 도구가 그 계약을 실행 전에 검사할 수 있게 만듭니다. 처음에는 공개 함수 시그니처부터 붙이는 방식이 가장 효율적입니다.

다음 글에서는 `int`, `str`, `bool` 같은 기본 타입과 `list`, `dict`, `tuple`, `set` 같은 컬렉션 타입을 어떻게 정확하게 적는지 자세히 보겠습니다.

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

## 추가 실무 메모: TypeVar 경계와 Any 확산 방지

타입 힌트를 도입할 때 가장 먼저 막아야 하는 것은 `Any`의 확산입니다. 제네릭 함수에서 `TypeVar`를 사용하면 입력-출력 타입 연계를 유지할 수 있고, 실수로 타입 정보가 사라지는 경로를 줄일 수 있습니다.

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    if not items:
        raise ValueError("items must not be empty")
    return items[0]
```

위 시그니처는 `list[int]`를 넣으면 `int`, `list[str]`를 넣으면 `str`을 반환한다는 계약을 유지합니다.

## 추가 패턴: 타입 힌트 도입 순서를 고정하기

팀 코드베이스에 타입 힌트를 도입할 때는 공개 API 함수, 도메인 모델, 경계 레이어 순으로 적용하면 리뷰 비용을 줄일 수 있습니다. 내부 구현부터 무작정 annotating하면 변경량은 커지는데 품질 신호는 약해집니다. 반대로 호출 경계부터 타입 계약을 세우면 IDE와 분석기가 즉시 오류를 보여 주기 때문에 리팩터링 안전성이 빠르게 올라갑니다.

## 운영 관점 보강

현업에서는 타입 힌트나 패키지 메타데이터를 문서로만 남기지 않고 CI 실패 신호로 연결합니다. 사람이 기억해서 지키는 규칙은 시간이 지나면 흐려지므로, 검사 도구가 자동으로 막는 경로를 만들어 두는 편이 장기적으로 더 안정적입니다.

타입 힌트는 코드베이스가 커질수록 유지보수 비용을 낮추는 장치입니다. 특히 함수 경계가 많은 서비스에서는 호출 계약을 자동으로 검증할 수 있다는 점이 큰 차이를 만듭니다.

또한 타입 정보를 기준으로 코드 검색과 리팩터링 범위를 좁힐 수 있어 팀 협업에서 의사결정 속도가 올라갑니다.


## 정적 검사 도입 전후 비교

타입 힌트의 가치는 문법 자체보다 도입 전후의 실패 비용 차이에서 드러납니다.

```python
# before.py

def calculate_discount(price, rate):
    return price * (1 - rate)

print(calculate_discount("10000", 0.1))
```

```python
# after.py

def calculate_discount(price: int, rate: float) -> int:
    return int(price * (1 - rate))

print(calculate_discount(10000, 0.1))
```

```text
$ mypy before.py
Success: no issues found in 1 source file

$ mypy after.py
Success: no issues found in 1 source file

$ mypy bad_call.py
bad_call.py:6: error: Argument 1 to "calculate_discount" has incompatible type "str"; expected "int"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

위 결과처럼 함수 계약을 먼저 선언하면 잘못된 호출이 실행 전에 실패합니다. 이 차이가 운영 단계에서의 장애 비용을 크게 줄입니다.

## Optional, Union, Protocol이 왜 뒤에서 필요한가

초기 글에서 타입 힌트를 단순 주석으로 이해하면 시리즈 후반의 문법이 뜬금없게 보입니다. 하지만 실제로는 같은 문제를 다른 수준에서 푸는 도구입니다.

| 문제 | 1차 해법 | 확장 해법 |
| --- | --- | --- |
| 입력 타입이 불분명함 | 기본 타입 주석 | Union, overload |
| 값이 없을 수 있음 | 반환 타입 명시 | Optional + 타입 좁히기 |
| 구현 교체가 필요함 | 클래스 타입 고정 | Protocol, Generic |
| 검증 시점이 늦음 | 수동 테스트 | mypy/pyright + CI |


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


## 실전 점검 로그: 타입 힌트를 계약으로 다루는 최소 루프

아래 로그는 타입 힌트를 단순 문서가 아니라 검증 가능한 계약으로 운영할 때 가장 자주 쓰는 확인 루프입니다.

```bash
$ mypy src/user_service.py
src/user_service.py:18: error: Incompatible return value type (got "str", expected "int")  [return-value]
Found 1 error in 1 file (checked 1 source file)

$ pyright src/user_service.py
.../src/user_service.py:18:12 - error: Type "str" is not assignable to return type "int" (reportReturnType)
1 error, 0 warnings, 0 informations
```

```text
Traceback (most recent call last):
  File "app.py", line 44, in <module>
    print(load_user_id("A-100"))
ValueError: user_id must be numeric
```

정적 검사에서 이미 실패를 만들고, 런타임 경계에서는 명시적 예외로 실패 형태를 고정해 두는 구성이 운영에서 가장 안정적입니다.

## 처음 질문으로 돌아가기

- **타입 힌트는 정적 타입 언어의 타입 선언과 무엇이 다를까요?**
  - 이 글의 타입 힌트는 `def greet(name: str) -> str`처럼 계약을 적어 두되, Python 런타임이 즉시 강제하지 않는 선택적 어노테이션입니다. 대신 mypy, pyright, IDE가 그 계약을 읽고 정적 분석과 자동완성에 활용한다는 점이 정적 타입 언어의 강제 선언과 다릅니다.
- **PEP 484가 해결하려던 문제는 무엇이었을까요?**
  - `calculate_total(prices, tax_rate)`처럼 시그니처만으로 입력과 반환 구조를 읽기 어려운 문제를 줄이려는 것이 핵심이었습니다. 그래서 공개 함수 계약을 코드 위에 올리고, 팀 코드베이스에서 정적 분석과 리팩터링 안전성을 확보하는 표준이 필요했습니다.
- **변수, 매개변수, 반환값에 어떤 문법으로 타입을 붙일까요?**
  - 변수는 `count: int = 0`, 매개변수는 `name: str`, 반환값은 `-> str`처럼 적는다고 본문에서 정리했습니다. 컬렉션도 `list[int]`, `dict[str, str]`, `tuple[float, float]`처럼 내장 제네릭 문법으로 구체화해야 도구가 실제 계약을 추적할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- **Python type hint란 무엇인가? (현재 글)**
- 기본 타입과 collection 타입 (예정)
- Optional과 Union (예정)
- 함수 타입 힌트 (예정)
- TypedDict와 dataclass (예정)
- Protocol과 structural typing (예정)
- Generic 이해하기 (예정)
- mypy와 pyright 사용하기 (예정)
- Pydantic과 타입 힌트 (예정)
- 타입 힌트를 잘 쓰는 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [Python 공식 문서 — typing 모듈](https://docs.python.org/3/library/typing.html)
- [mypy 공식 문서](https://mypy.readthedocs.io/en/stable/)
- [Real Python — Python Type Checking](https://realpython.com/python-type-checking/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/type-hints-python-101/ko)
Tags: Python, Type Hints, 타입 힌트, 정적 분석, mypy, 코드 품질

---
series: type-hints-python-101
episode: 2
title: "Type Hints in Python 101 (2/10): 기본 타입과 collection 타입"
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
  - 컬렉션 타입
  - list
  - dict
  - tuple
seo_description: int, str부터 list, dict, tuple까지 Python 타입 힌트의 기본 타입과 컬렉션 타입을 다룹니다.
last_reviewed: '2026-05-12'
---

# Type Hints in Python 101 (2/10): 기본 타입과 collection 타입

타입 힌트를 처음 붙일 때 가장 많이 나오는 질문은 단순합니다. `name: str`은 알겠는데, 리스트와 딕셔너리 안에 무엇이 들어가는지는 어떻게 적어야 할까요? 바로 이 지점부터 타입 힌트가 문서 수준을 넘어 실제 오류 방지 도구로 바뀝니다.

이 글은 Type Hints (Python) 101 시리즈의 2번째 글입니다. 여기서는 기본 스칼라 타입과 컬렉션 타입을 어떻게 표현하는지, 그리고 컨테이너 안쪽 타입까지 적어야 하는 이유를 정리합니다.


![Type Hints in Python 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/02/02-01-big-picture.ko.png)
*Type Hints in Python 101 2장 흐름 개요*

> 타입 힌트는 컨테이너 안쪽 타입까지 적어야 비로소 문서 수준에서 실제 오류 방지 도구로 바뀝니다 — `list`만 적는 것과 `list[User]`로 적는 것은 정적 검사기에게 완전히 다른 정보입니다.

## 먼저 던지는 질문

- `int`, `str`, `float`, `bool`, `bytes`, `None`은 어떻게 적을까요?
- `list`, `dict`, `tuple`, `set`은 왜 원소 타입까지 붙여야 할까요?
- 고정 길이 튜플과 가변 길이 튜플은 어떻게 다를까요?

## 왜 이 주제가 중요한가

실무 Python 코드는 대부분 컬렉션과 함께 움직입니다. API 응답은 딕셔너리와 리스트로 오고, 설정은 중첩 딕셔너리로 들어오며, 쿼리 결과는 튜플 목록으로 다뤄집니다. 이때 `list`나 `dict`만 적어 두면 분석기는 안쪽 원소를 `object`에 가깝게 취급하고, 엉뚱한 메서드 호출이나 잘못된 값 삽입을 충분히 잡아내지 못합니다.

예를 들어 `list[int]`와 `list[str]`는 전혀 다른 계약입니다. 전자에는 합계를 구할 수 있지만 후자에는 `sum()`을 쓰기 어렵습니다. 이 차이를 타입 힌트에 적지 않으면, 도구는 호출자가 어떤 연산을 해도 미리 경고할 근거를 얻지 못합니다.

## 한눈에 보는 개념

```text
스칼라 타입:  int    str    float    bool    None
                  \    |      /         |
컬렉션 타입:   list[int]  dict[str, float]  tuple[str, int]
                  \            |                /
중첩 타입:     dict[str, list[int]]
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 스칼라 타입 | `int`, `str`, `float`, `bool`처럼 단일 값을 나타내는 타입입니다 |
| 매개화된 타입 | `list[int]`처럼 타입 인자를 가진 제네릭 타입입니다 |
| 동종 튜플 | 길이는 가변이고 원소 타입은 같은 튜플입니다. 예: `tuple[int, ...]` |
| 이종 튜플 | 길이와 위치별 타입이 정해진 튜플입니다. 예: `tuple[str, int]` |
| 타입 별칭 | 복잡한 타입에 이름을 붙여 가독성을 높이는 방식입니다 |

## 바꾸기 전과 후

```python
def get_prices(items: list) -> dict:
    result = {}
    for item in items:
        result[item.name] = item.price  # 타입 검사기: 속성을 알 수 없음
    return result
```

```python
def get_prices(items: list[Product]) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items:
        result[item.name] = item.price  # 타입 검사기: OK
    return result
```

컨테이너의 내부 타입을 적는 순간, 분석기는 `item.name`, `item.price`, `result`의 키와 값까지 추적할 수 있습니다.

## 단계별로 익히기

### 1단계: 기본 스칼라 타입

```python
name: str = "Alice"
age: int = 30
height: float = 5.7
is_active: bool = True
data: bytes = b"hello"
nothing: None = None
```

복잡한 타입도 결국은 이런 기본 타입을 조합해서 표현합니다.

### 2단계: list와 set

```python
names: list[str] = ["Alice", "Bob", "Charlie"]
unique_ids: set[int] = {1, 2, 3}

# 중첩 리스트
matrix: list[list[int]] = [
    [1, 2, 3],
    [4, 5, 6],
]

def get_active_users(users: list[str]) -> set[str]:
    return set(users)
```

`list[str]`는 모든 원소가 문자열이어야 한다는 뜻입니다. 따라서 `names.append(42)` 같은 코드는 타입 검사기에서 바로 걸립니다.

### 3단계: dict

```python
scores: dict[str, int] = {"Alice": 95, "Bob": 87}
config: dict[str, str | int | bool] = {
    "host": "localhost",
    "port": 8080,
    "debug": True,
}

def get_headers() -> dict[str, str]:
    return {"Content-Type": "application/json"}
```

`dict[str, int]`는 키는 문자열, 값은 정수라는 뜻입니다. 값 타입이 섞여 있다면 `Union` 또는 `|` 문법을 함께 써야 합니다.

### 4단계: tuple — 고정 구조와 가변 구조

```python
# 이종 튜플: 길이 고정, 위치별 타입 고정
coordinate: tuple[float, float] = (37.5, 127.0)
record: tuple[str, int, bool] = ("Alice", 30, True)

# 동종 튜플: 길이 가변, 모든 원소 타입 동일
numbers: tuple[int, ...] = (1, 2, 3, 4, 5)
empty: tuple[()] = ()
```

`tuple[int, ...]`의 `...`는 정수 원소가 0개 이상 이어질 수 있다는 뜻입니다. 반대로 `tuple[str, int]`는 정확히 두 칸짜리 구조입니다.

### 5단계: 복잡한 타입은 별칭으로 정리하기

```python
# 가독성을 위한 타입 별칭
UserScores = dict[str, list[int]]
Config = dict[str, str | int | bool | list[str]]

def aggregate_scores(data: UserScores) -> dict[str, float]:
    return {name: sum(scores) / len(scores) for name, scores in data.items()}

scores: UserScores = {
    "Alice": [95, 87, 92],
    "Bob": [78, 85, 90],
}
```

중첩 구조가 길어지면 타입 별칭이 가독성에 큰 도움을 줍니다. Python 3.12 이상에서는 `type UserScores = dict[str, list[int]]` 문법도 사용할 수 있습니다.

## 여기서 먼저 봐야 할 점

- 컬렉션 타입은 원소 타입까지 적어야 정적 분석에 의미가 생깁니다.
- 튜플은 `tuple[int, int]`와 `tuple[int, ...]`가 전혀 다른 구조입니다.
- `dict[str, list[int]]` 같은 중첩 타입도 충분히 실용적으로 사용할 수 있습니다.
- 타입 별칭은 중첩 구조가 길어질수록 가치가 커집니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| `list`, `dict`만 적음 | 원소 타입을 추적할 수 없습니다 | `list[int]`, `dict[str, str]`처럼 매개화합니다 |
| `tuple[int, int]`와 `tuple[int, ...]`를 혼동함 | 하나는 고정 길이, 하나는 가변 길이입니다 | 의도한 구조를 정확히 구분합니다 |
| Python 3.9+에서 `typing.List`를 계속 씀 | 불필요한 임포트가 늘어납니다 | 내장 컬렉션 타입을 직접 사용합니다 |
| `dict[str, Any]`를 너무 넓게 씀 | 값 타입 안전성이 사라집니다 | 가능한 한 구체 타입이나 TypedDict를 씁니다 |
| 불변 집합인데 `set`을 사용함 | 가변성 계약이 어긋납니다 | 불변이 필요하면 `frozenset[T]`를 검토합니다 |

## 실무에서는 이렇게 연결됩니다

- JSON 구조는 `dict[str, list[dict[str, str]]]`처럼 중첩 타입으로 표현합니다.
- 데이터베이스 결과는 `list[tuple[int, str, float]]`처럼 행 구조를 타입으로 적을 수 있습니다.
- 설정 로더는 `dict[str, str | int | bool]` 형태로 혼합 값을 관리합니다.
- 캐시나 저장소 래퍼는 이후 Generic과 결합해 `dict[str, T]` 형태로 확장됩니다.

## 실무 판단 기준

경험 많은 개발자는 컬렉션 타입을 절대 맨몸으로 두지 않습니다. `list`라고만 적는 순간 가장 중요한 정보인 원소 타입을 버리기 때문입니다. `list[int]`를 적는 데 몇 초 더 걸리더라도, 잘못된 타입이 세 단계 아래 호출 체인으로 흘러가는 문제를 미리 막는 효과가 훨씬 큽니다.

또한 타입을 넓게 잡는 것보다 정확하게 잡는 편을 선호합니다. `dict[str, Any]`는 편해 보이지만 곧 분석기를 무력화합니다. 데이터의 모양을 알고 있다면 더 구체적인 컬렉션 타입이나 `TypedDict`로 이동하는 편이 좋습니다.

## 체크리스트

- [ ] 컬렉션 타입에 원소 타입을 함께 적었습니다
- [ ] 고정 구조 데이터에는 이종 튜플을 사용했습니다
- [ ] 복잡한 중첩 타입에는 타입 별칭을 고려했습니다
- [ ] `list`, `dict`, `tuple`을 타입 인자 없이 두지 않았습니다
- [ ] Python 3.9+ 스타일의 내장 타입 문법을 사용했습니다

## 연습 문제

1. `flatten(matrix: list[list[int]]) -> list[int]` 함수를 작성하고 mypy로 검사해 보세요.

2. `StudentRecord = tuple[str, int, list[float]]` 타입 별칭을 만들고, 학생 목록에서 평균 점수를 계산하는 함수를 작성해 보세요.

3. `dict[str, dict[str, str | int | list[str]]]` 형태의 설정 구조를 타입으로 적고, 특정 값을 꺼내는 함수를 만들어 보세요.

## 정리와 다음 글

기본 타입과 컬렉션 타입은 Python 타입 힌트의 가장 넓은 바닥을 이룹니다. `int`, `str`, `float`, `bool` 같은 스칼라 타입 위에 `list[T]`, `dict[K, V]`, `tuple[...]`, `set[T]` 같은 컨테이너가 쌓입니다. 여기서 중요한 습관은 컬렉션 안쪽 타입을 생략하지 않는 것입니다.

다음 글에서는 값이 없을 수도 있거나 여러 타입 중 하나일 수 있는 상황을 표현하는 `Optional`과 `Union`을 다룹니다.

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

이 패턴의 장점은 구현 교체 비용이 낮다는 사실입니다. `Repository[User]` 계약만 지키면 메모리 저장소를 DB 저장소로 바꿔도 상위 서비스 타입 시그니처를 유지할 수 있습니다. 또한 Protocol 기반 설계는 상속 계층 없이도 구조적 타이핑으로 계약을 검사할 수 있어, 기존 코드에 점진적으로 타입 안전성을 도입할 때 특히 유리합니다.

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


## 컬렉션 타입에서 자주 나는 mypy 오류

컬렉션 타입은 겉보기에는 단순하지만, 원소 타입이 섞이는 순간 오류가 빠르게 늘어납니다.

```python
from typing import TypedDict

class Item(TypedDict):
    name: str
    price: int


def total_price(items: list[Item]) -> int:
    return sum(item["price"] for item in items)

rows: list[Item] = [
    {"name": "book", "price": 12000},
    {"name": "pen", "price": "3000"},
]

print(total_price(rows))
```

```text
example.py:13: error: Incompatible types (expression has type "str", TypedDict item "price" has type "int")  [typeddict-item]
Found 1 error in 1 file (checked 1 source file)
```

해결은 원소 타입을 고치는 것뿐입니다.

```python
rows: list[Item] = [
    {"name": "book", "price": 12000},
    {"name": "pen", "price": 3000},
]
```

## Optional과 컬렉션을 함께 쓸 때

```python
def average(values: list[int] | None) -> float:
    if values is None or len(values) == 0:
        return 0.0
    return sum(values) / len(values)
```

이 패턴은 데이터 파이프라인에서 빈 배치와 누락 배치를 분리할 때 자주 쓰입니다.

## 튜플 설계 기준

| 데이터 형태 | 권장 타입 | 이유 |
| --- | --- | --- |
| 좌표 두 개 | `tuple[float, float]` | 위치별 의미 고정 |
| 임의 길이 숫자열 | `tuple[int, ...]` | 길이 가변 허용 |
| 레코드 구조 | `TypedDict` 또는 dataclass | 필드 이름이 더 명확 |


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


## 실전 표: TypedDict와 dataclass 경계 분리

컬렉션 타입을 다룰 때는 "외부 입출력 구조"와 "내부 계산 모델"을 분리하면 유지보수성이 높아집니다.

| 경계 | 권장 구조 | 이유 |
| --- | --- | --- |
| HTTP/Queue 입력 | `TypedDict` | 키 누락/오타를 정적 검사에서 바로 탐지할 수 있습니다 |
| 내부 계산 | `dataclass` | 메서드와 불변성(`frozen=True`)을 함께 설계하기 쉽습니다 |
| DB row 변환 | `TypedDict -> dataclass` | 파싱 지점을 한 곳에 모아 타입 확산을 막습니다 |

```python
from dataclasses import dataclass
from typing import TypedDict

class UserRow(TypedDict):
    id: int
    email: str

@dataclass(frozen=True)
class User:
    id: int
    email: str
```

## 처음 질문으로 돌아가기

- **`int`, `str`, `float`, `bool`, `bytes`, `None`은 어떻게 적을까요?**
  - 기본 스칼라 타입은 `name: str`, `age: int`, `data: bytes`, `nothing: None = None`처럼 이름 옆에 바로 적으면 됩니다. 이 기본 타입들이 이후 `list[str]`, `dict[str, int]` 같은 복합 타입의 재료가 됩니다.
- **`list`, `dict`, `tuple`, `set`은 왜 원소 타입까지 붙여야 할까요?**
  - `list`나 `dict`만 적으면 분석기가 내부 원소를 제대로 추적하지 못해서 `item.price`나 `sum()` 같은 연산 안전성을 보장하기 어렵습니다. 본문에서 `get_prices(items: list[Product]) -> dict[str, int]`로 바꾼 뒤에야 키와 값, 원소 속성까지 함께 검사할 수 있었습니다.
- **고정 길이 튜플과 가변 길이 튜플은 어떻게 다를까요?**
  - `tuple[float, float]`나 `tuple[str, int, bool]`은 길이와 위치별 의미가 고정된 이종 튜플입니다. 반대로 `tuple[int, ...]`은 정수만 들어오면 길이는 얼마든지 늘어날 수 있는 동종 튜플이라, 좌표와 숫자열 같은 서로 다른 구조를 구분할 때 중요합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Type Hints in Python 101 (1/10): Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- **기본 타입과 collection 타입 (현재 글)**
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

- [Python 공식 문서 — typing 모듈](https://docs.python.org/3/library/typing.html)
- [PEP 585 — Type Hinting Generics In Standard Collections](https://peps.python.org/pep-0585/)
- [mypy 문서 — Built-in types](https://mypy.readthedocs.io/en/stable/builtin_types.html)
- [Real Python — Python Type Checking](https://realpython.com/python-type-checking/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/type-hints-python-101/ko)
Tags: Python, Type Hints, 컬렉션 타입, list, dict, tuple

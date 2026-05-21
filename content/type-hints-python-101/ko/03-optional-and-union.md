---
series: type-hints-python-101
episode: 3
title: "Type Hints in Python 101 (3/10): Optional과 Union"
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
  - Optional
  - Union
  - None
  - 타입 안전
seo_description: Optional과 Union으로 None 가능성과 여러 타입을 안전하게 표현하는 방법을 다룹니다.
last_reviewed: '2026-05-12'
---

# Type Hints in Python 101 (3/10): Optional과 Union

실무 Python 코드에서는 값이 항상 존재하지 않습니다. 조회 결과가 없으면 `None`이 나오고, 유연한 입력을 받으려다 보면 하나의 매개변수가 문자열일 수도 정수일 수도 있습니다. 이런 상황을 타입에 적지 않으면 가장 흔한 버그가 조용히 숨어 듭니다.

이 글은 Type Hints (Python) 101 시리즈의 3번째 글입니다. 여기서는 `Optional`과 `Union`으로 값의 가능 범위를 어떻게 표현하는지, 그리고 호출자가 그 가능성을 어떻게 안전하게 처리해야 하는지 살펴봅니다.


![Type Hints in Python 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/03/03-01-big-picture.ko.png)
*Type Hints in Python 101 3장 흐름 개요*

## 먼저 던지는 질문

- 반환값이 `None`일 수 있다는 사실을 타입에 어떻게 드러낼까요?
- 하나의 값이 여러 타입 중 하나일 수 있을 때 어떤 문법을 써야 할까요?
- Python 3.10+의 `X | Y` 문법은 언제 유용할까요?

## 왜 이 주제가 중요한가

Python 런타임 오류 중에는 `None` 관련 예외가 매우 많습니다. 함수가 찾지 못한 값을 `None`으로 반환했는데 호출자는 항상 객체가 온다고 가정하고 메서드를 호출해 버리는 식입니다. 이런 문제는 원인이 생긴 지점과 폭발하는 지점이 멀리 떨어져 있어서 디버깅 비용도 큽니다.

`Union`도 마찬가지입니다. 하나의 매개변수가 문자열 ID와 숫자 ID를 모두 받는다면, 코드와 타입은 그 사실을 숨기지 말아야 합니다. 입력이 여러 타입을 받을 수 있다는 사실을 명시해야 분기 처리, 자동완성, 코드 리뷰 모두가 쉬워집니다.

## 한눈에 보는 개념

```text
Optional[str]  =  str | None
                    │
            if value is not None:
                    │
            value: str 로 좁혀짐

Union[int, str]  =  int | str
                      │
            if isinstance(value, int):
                      │
            value: int 로 좁혀짐
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Optional[T] | `T | None`과 같은 뜻입니다 |
| Union[T1, T2] | 값이 나열된 타입 중 하나라는 뜻입니다 |
| 파이프 문법 | Python 3.10+에서 `Union[int, str]` 대신 `int | str`로 적는 방식입니다 |
| 타입 좁히기 | 분기 조건을 통해 분석기가 구체 타입을 확정하는 과정입니다 |
| 타입 가드 | 특정 검사가 타입을 좁혀 준다는 사실을 표현하는 방식입니다 |

## 바꾸기 전과 후

```python
def find_user(user_id: int) -> dict:
    if user_id == 0:
        return None  # 타입은 dict라고 적었지만 실제로는 None 반환
    return {"id": user_id, "name": "Alice"}

user = find_user(0)
print(user["name"])  # 런타임 오류
```

```python
def find_user(user_id: int) -> dict[str, str | int] | None:
    if user_id == 0:
        return None
    return {"id": user_id, "name": "Alice"}

user = find_user(0)
if user is not None:
    print(user["name"])  # 안전함
```

여기서 중요한 점은 `None` 가능성을 숨기지 않는다는 사실입니다.

## 단계별로 익히기

### 1단계: Optional로 nullable 반환값 표현하기

```python
from typing import Optional

def find_by_name(name: str) -> Optional[str]:
    """찾으면 이메일을, 없으면 None을 반환합니다."""
    users = {"Alice": "alice@example.com", "Bob": "bob@example.com"}
    return users.get(name)

email = find_by_name("Alice")
# email: Optional[str] — 사용 전에 확인 필요
if email is not None:
    print(email.upper())  # 안전함
```

`Optional[str]`는 정확히 `str | None`입니다. 선택적 매개변수라는 말이 아니라, 값 자체가 비어 있을 수도 있다는 설명에 가깝습니다.

### 2단계: Python 3.10+ 파이프 문법 쓰기

```python
# Python 3.10+: Union/Optional 대신 | 문법을 사용합니다.
def find_by_name(name: str) -> str | None:
    users = {"Alice": "alice@example.com"}
    return users.get(name)

def process(value: int | str) -> str:
    return str(value)
```

이 문법은 더 짧고, `typing` 임포트를 줄여 줍니다.

### 3단계: Union으로 여러 타입 받기

```python
def format_id(value: int | str) -> str:
    """정수 ID와 문자열 UUID를 모두 받습니다."""
    if isinstance(value, int):
        return f"ID-{value:06d}"
    return f"UUID-{value}"

print(format_id(42))          # ID-000042
print(format_id("abc-123"))   # UUID-abc-123
```

`isinstance` 분기 안에서는 분석기가 `value`를 `int`로 좁혀서 봅니다.

### 4단계: 타입 좁히기 패턴 익히기

```python
def process(value: str | int | None) -> str:
    # 패턴 1: None 확인
    if value is None:
        return "default"

    # 패턴 2: isinstance 확인
    if isinstance(value, int):
        return str(value)

    # 다른 경우를 제거했으므로 여기서는 str만 남습니다.
    return value.upper()

def safe_len(text: str | None) -> int:
    # 패턴 3: 조기 반환
    if text is None:
        return 0
    return len(text)
```

이런 분기 구조가 있어야 mypy와 pyright가 모든 경우를 안전하게 처리했다고 판단합니다.

### 5단계: 기본값이 `None`인 매개변수 적기

```python
def greet(name: str, title: str | None = None) -> str:
    """title은 기본값이 None인 선택적 값입니다."""
    if title is not None:
        return f"Hello, {title} {name}!"
    return f"Hello, {name}!"

print(greet("Alice"))              # Hello, Alice!
print(greet("Alice", "Dr."))      # Hello, Dr. Alice!
```

매개변수 기본값이 `None`이면 대개 `T | None` 형태로 적는 편이 가장 분명합니다.

## 여기서 먼저 봐야 할 점

- `Optional[T]`와 `T | None`은 의미가 같습니다.
- `Optional` 값을 쓰기 전에는 `None` 확인이 필요합니다.
- `Union`을 받는 코드는 분기 안에서 타입을 좁혀야 안전합니다.
- Python 3.10+에서는 `|` 문법이 가장 읽기 좋습니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| Optional 값을 확인 없이 사용함 | `NoneType` 관련 런타임 오류가 납니다 | `is not None` 확인 후 사용합니다 |
| Optional을 "매개변수를 안 넘겨도 된다"로 이해함 | nullable과 optional argument를 혼동합니다 | `Optional`은 값이 `None`일 수 있다는 뜻으로 읽습니다 |
| `Union[int, str, float, bool, list]`처럼 너무 넓게 잡음 | 호출자와 구현 모두 복잡해집니다 | 2~3개 수준으로 유지하거나 API를 나눕니다 |
| 분기에서 타입 좁히기를 하지 않음 | 분석기가 여전히 여러 타입 가능성을 봅니다 | `isinstance`, `is None` 패턴을 씁니다 |
| `Optional[Optional[str]]`를 중첩함 | 의미가 늘지 않습니다 | `str | None` 하나면 충분합니다 |

## 실무에서는 이렇게 연결됩니다

- 데이터베이스 조회 함수는 찾지 못한 경우 `Model | None`을 반환합니다.
- 설정 조회는 `str | None`으로 받고 호출부에서 기본값을 정합니다.
- API 클라이언트는 성공 응답과 오류 응답을 `Union`으로 모델링할 수 있습니다.
- 폼 입력은 `str | int`처럼 여러 형태를 받되 내부에서 빨리 정규화합니다.

## 실무 판단 기준

숙련된 개발자는 "없음"을 숫자 `-1`이나 빈 문자열 같은 센티널 값으로 감추기보다 `None`과 `Optional`로 드러내는 쪽을 선호합니다. 그래야 호출자가 빠뜨릴 수 없고, 분석기도 그 분기를 강제할 수 있습니다.

또한 `Union`이 계속 넓어지면 타입 문제가 아니라 설계 문제로 봅니다. 하나의 함수가 너무 많은 입력 형태를 받기 시작했다는 뜻일 수 있기 때문입니다. 이때는 타입을 더 복잡하게 적는 것보다 인터페이스를 쪼개는 편이 낫습니다.

## 체크리스트

- [ ] nullable 값에는 `Optional[T]` 또는 `T | None`을 사용했습니다
- [ ] Optional 값을 쓰기 전에 `None` 확인을 했습니다
- [ ] Union 분기에서 `isinstance`나 `is None`으로 타입을 좁혔습니다
- [ ] Union 타입 개수를 과도하게 늘리지 않았습니다
- [ ] Python 3.10+ 환경에서는 `|` 문법을 고려했습니다

## 연습 문제

1. `safe_divide(a: float, b: float) -> float | None` 함수를 작성해 0으로 나누려 할 때 `None`을 반환하게 해 보세요.

2. `format_value(value: int | float | str) -> str` 함수를 만들고, 각 타입마다 다른 포맷을 적용해 보세요.

3. 지금은 빈 문자열 `""`로 "없음"을 표현하는 함수를 하나 골라 `Optional[str]` 기반으로 바꿔 보세요.

## 정리와 다음 글

`Optional[T]`는 값이 `None`일 수 있음을, `Union[T1, T2]`는 여러 타입 중 하나가 올 수 있음을 적는 방법입니다. 중요한 점은 타입을 적는 데서 끝나지 않고, 분기 안에서 그 가능성을 실제로 처리하는 것입니다. `isinstance`와 `is None`은 그 계약을 코드로 드러내는 가장 기본적인 패턴입니다.

다음 글에서는 함수 자체를 값처럼 다룰 때 필요한 `Callable`, `*args`, `**kwargs`, `@overload`를 살펴보겠습니다.

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


## Optional 처리 전후 예제

```python
class User:
    def __init__(self, email: str) -> None:
        self.email = email


def find_user(user_id: int) -> User | None:
    if user_id == 1:
        return User("buyer@example.com")
    return None


def get_email(user_id: int) -> str:
    user = find_user(user_id)
    return user.email
```

```text
example.py:14: error: Item "None" of "User | None" has no attribute "email"  [union-attr]
Found 1 error in 1 file (checked 1 source file)
```

```python
def get_email(user_id: int) -> str:
    user = find_user(user_id)
    if user is None:
        raise LookupError("user not found")
    return user.email
```

## Optional vs Union 비교

| 항목 | `Optional[T]` | `Union[T1, T2]` |
| --- | --- | --- |
| 의미 | `T | None` | 여러 타입 중 하나 |
| 대표 용도 | 조회 실패 가능성 | 유연한 입력 포맷 |
| 필수 분기 | `is None` 검사 | `isinstance` 또는 패턴 매칭 |
| 남용 위험 | 기본값 남발 | 과도한 타입 수 |

## API 경계 패턴

외부 입력은 `str | int`로 받고 내부에서는 한 번에 정규화하는 편이 안정적입니다.

```python
def parse_user_id(raw: str | int) -> int:
    if isinstance(raw, int):
        return raw
    if raw.isdigit():
        return int(raw)
    raise ValueError("user_id must be int or numeric string")
```


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

## before/after 요약

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


## 실전 실패/복구 시나리오

`Optional`과 `Union`의 핵심은 분기 누락을 조기에 드러내는 것입니다.

```text
Traceback (most recent call last):
  File "service.py", line 57, in send_notice
    return user.email.upper()
AttributeError: 'NoneType' object has no attribute 'email'
```

```python
def send_notice(user: User | None) -> str:
    if user is None:
        raise LookupError("user not found")
    return user.email.upper()
```

```bash
$ mypy service.py
Success: no issues found in 1 source file
```

이 패턴은 분기 누락을 런타임 예외에서 설계된 예외로 바꾸고, 호출부 계약을 분명하게 만듭니다.

## 처음 질문으로 돌아가기

- **반환값이 `None`일 수 있다는 사실을 타입에 어떻게 드러낼까요?**
  - 본문의 기준은 Optional과 Union를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **하나의 값이 여러 타입 중 하나일 수 있을 때 어떤 문법을 써야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Python 3.10+의 `X | Y` 문법은 언제 유용할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Type Hints in Python 101 (1/10): Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [Type Hints in Python 101 (2/10): 기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- **Optional과 Union (현재 글)**
- 함수 타입 힌트 (예정)
- TypedDict와 dataclass (예정)
- Protocol과 structural typing (예정)
- Generic 이해하기 (예정)
- mypy와 pyright 사용하기 (예정)
- Pydantic과 타입 힌트 (예정)
- 타입 힌트를 잘 쓰는 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — typing.Optional](https://docs.python.org/3/library/typing.html#typing.Optional)
- [Python 공식 문서 — typing.Union](https://docs.python.org/3/library/typing.html#typing.Union)
- [PEP 604 — Allow writing union types as X | Y](https://peps.python.org/pep-0604/)
- [mypy 문서 — Optional types and None](https://mypy.readthedocs.io/en/stable/kinds_of_types.html#optional-types-and-the-none-type)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/type-hints-python-101/ko)
Tags: Python, Type Hints, Optional, Union, None, 타입 안전

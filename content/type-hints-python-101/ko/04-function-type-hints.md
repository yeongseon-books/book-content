---
series: type-hints-python-101
episode: 4
title: "Type Hints in Python 101 (4/10): 함수 타입 힌트"
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
  - Callable
  - 함수 시그니처
  - 오버로드
  - 데코레이터
seo_description: Callable, 콜백, 데코레이터, 오버로드까지 함수와 관련된 타입 힌트 심화 문법을 다룹니다.
last_reviewed: '2026-05-12'
---

# Type Hints in Python 101 (4/10): 함수 타입 힌트

Python에서 함수는 값입니다. 함수에 함수를 넘기고, 함수를 반환하고, 데코레이터로 감쌀 수 있습니다. 이 유연성은 강력하지만, 타입 힌트 없이 쓰면 가장 먼저 흐려지는 것도 함수 계약입니다.

이 글은 Type Hints (Python) 101 시리즈의 4번째 글입니다. 여기서는 `Callable`, `*args`, `**kwargs`, `@overload`, `ParamSpec`으로 함수 수준 계약을 어떻게 적는지 살펴봅니다.


![Type Hints in Python 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/04/04-01-big-picture.ko.png)
*Type Hints in Python 101 4장 흐름 개요*

## 먼저 던지는 질문

- 함수 자체를 인자로 받는 매개변수는 어떻게 타입을 붙일까요?
- `*args`, `**kwargs`는 무엇에 타입을 붙이는 걸까요?
- 입력 타입에 따라 반환 타입이 달라지는 함수는 어떻게 표현할까요?

## 왜 이 주제가 중요한가

콜백, 전략 패턴, 이벤트 핸들러, 데코레이터는 Python 실무에서 흔합니다. 그런데 함수 타입을 적지 않으면 잘못된 시그니처를 가진 콜백을 넘겨도 리뷰 단계까지 숨어 있을 수 있습니다. 데코레이터를 잘못 타입 지정하면 감싼 함수들의 타입 정보가 연쇄적으로 `Any`로 무너질 수도 있습니다.

특히 FastAPI나 Flask 같은 프레임워크를 많이 쓰는 팀이라면 데코레이터 타입 안정성이 중요합니다. 한 번 어긋난 데코레이터는 그 아래 함수들의 자동완성과 오류 검출 품질을 함께 떨어뜨립니다.

## 한눈에 보는 개념

```text
Callable[[int, str], bool]
    │       │   │      │
    │    인자 타입들   반환 타입
    │
    "(int, str)을 받아 bool을 반환하는 함수"

@overload
def parse(raw: str) -> dict: ...
def parse(raw: bytes) -> dict: ...
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Callable | 함수 타입 값을 적는 문법입니다. `Callable[[Args], Return]` 형태를 씁니다 |
| @overload | 하나의 구현에 여러 호출 시그니처를 제공하는 장치입니다 |
| ParamSpec | 함수의 전체 매개변수 목록을 타입 변수처럼 보존합니다 |
| Concatenate | 데코레이터 래퍼에서 매개변수를 앞에 붙일 때 사용합니다 |
| TypeGuard | 불리언 함수가 타입을 좁힌다는 사실을 분석기에 알려 주는 반환 타입입니다 |

## 바꾸기 전과 후

```python
def retry(func, attempts):
    for i in range(attempts):
        try:
            return func()
        except Exception:
            if i == attempts - 1:
                raise
```

```python
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

def retry(func: Callable[[], T], attempts: int) -> T:
    for i in range(attempts):
        try:
            return func()
        except Exception:
            if i == attempts - 1:
                raise
    raise RuntimeError("unreachable")
```

이제 분석기는 `func`가 인자 없이 호출 가능해야 하고, 반환값 타입이 그대로 바깥으로 이어진다는 사실을 압니다.

## 단계별로 익히기

### 1단계: `Callable`로 함수 매개변수 적기

```python
from collections.abc import Callable

def apply_operation(values: list[int], op: Callable[[int], int]) -> list[int]:
    return [op(v) for v in values]

def double(x: int) -> int:
    return x * 2

result = apply_operation([1, 2, 3], double)  # [2, 4, 6]
result = apply_operation([1, 2, 3], lambda x: x + 1)  # [2, 3, 4]
```

`Callable[[int], int]`는 정수 하나를 받아 정수를 돌려주는 함수라는 뜻입니다.

### 2단계: `*args`와 `**kwargs` 적기

```python
def log_call(*args: str, **kwargs: int) -> None:
    for arg in args:
        print(arg)        # arg: str
    for key, value in kwargs.items():
        print(f"{key}={value}")  # value: int

log_call("hello", "world", retries=3, timeout=30)
```

여기서 `*args: str`은 `args` 전체가 `tuple[str, ...]`라는 뜻이 아니라, 각 개별 인자가 `str`이라는 뜻입니다.

### 3단계: `@overload`로 여러 시그니처 제공하기

```python
from typing import overload

@overload
def parse_value(raw: str) -> dict[str, str]: ...

@overload
def parse_value(raw: bytes) -> dict[str, bytes]: ...

def parse_value(raw: str | bytes) -> dict[str, str] | dict[str, bytes]:
    if isinstance(raw, str):
        return {"data": raw}
    return {b"data": raw}

text_result = parse_value("hello")    # dict[str, str]
bytes_result = parse_value(b"hello")  # dict[str, bytes]
```

호출자는 오버로드 선언만 보게 되고, 실제 구현은 모든 경우를 한 번에 처리합니다.

### 4단계: 데코레이터에 `ParamSpec` 쓰기

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")

def log_calls(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def add(a: int, b: int) -> int:
    return a + b

result = add(1, 2)  # 타입 검사기는 여전히 (int, int) -> int로 압니다
```

`ParamSpec`이 없으면 데코레이터가 원본 함수의 매개변수 구조를 잃어버리기 쉽습니다.

### 5단계: 인자가 없거나 제한하지 않을 때

```python
from collections.abc import Callable
from typing import Any

# 인자가 없고 str을 반환
factory: Callable[[], str] = lambda: "hello"

# 어떤 인자든 허용함 (가능하면 제한적으로 사용)
handler: Callable[..., None] = lambda *args, **kwargs: None
```

`Callable[..., None]`는 편하지만 인자 검사를 사실상 포기하므로, 정말 필요한 경우에만 쓰는 편이 좋습니다.

## 여기서 먼저 봐야 할 점

- `Callable`은 인자 타입 목록과 반환 타입을 함께 적습니다.
- `@overload`는 여러 선언 뒤에 하나의 실제 구현이 따라와야 합니다.
- `ParamSpec`은 데코레이터가 원본 함수 시그니처를 지키게 해 줍니다.
- `*args`, `**kwargs` 주석은 각각의 원소 타입에 붙는다는 점이 중요합니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| `Callable[..., int]`를 남발함 | 매개변수 타입 안전성이 사라집니다 | 인자 타입을 알면 구체적으로 적습니다 |
| `@overload` 선언만 적고 구현을 빠뜨림 | 실제 함수가 없어 분석기와 런타임 모두 어색해집니다 | 마지막에 구현 함수를 둡니다 |
| 데코레이터 반환 타입을 `Any`로 둠 | 감싼 함수 타입 정보가 사라집니다 | `ParamSpec`과 `TypeVar`를 씁니다 |
| `*args: tuple[str, ...]`처럼 적음 | 의미가 어긋납니다 | `*args: str`처럼 개별 인자 타입을 적습니다 |
| 같은 시그니처를 중복 오버로드함 | 읽기만 복잡해집니다 | 입력 관계가 분명히 다를 때만 씁니다 |

## 실무에서는 이렇게 연결됩니다

- 이벤트 시스템은 `Callable[[Event], None]` 형태의 콜백 계약을 둡니다.
- 재시도 데코레이터는 `Callable[P, T]`로 원래 함수 계약을 보존합니다.
- 전략 패턴은 `Callable[[Data], Result]`를 받아 교체 가능한 알고리즘을 구성합니다.
- 프레임워크 데코레이터는 `ParamSpec` 없이는 타입 정보가 쉽게 무너집니다.

## 실무 판단 기준

경험 많은 개발자는 특히 데코레이터 타입을 대충 두지 않습니다. 데코레이터는 한 번 쓰고 끝나는 코드가 아니라 여러 함수에 반복 적용되기 때문에, 여기서 타입 정보가 무너지면 영향 범위가 넓기 때문입니다. `ParamSpec`은 선택 기능이라기보다 typed codebase의 기본 장치에 가깝습니다.

또한 `@overload`는 강력하지만 남용하지 않습니다. 입력 타입에 따라 반환 타입이 실제로 달라질 때만 쓰고, 오버로드가 너무 많아지면 함수 설계를 다시 봅니다.

## 체크리스트

- [ ] 함수 값을 받는 매개변수에 `Callable[[...], ...]`를 사용했습니다
- [ ] `*args`, `**kwargs`에 개별 원소 타입을 붙였습니다
- [ ] 입력-출력 관계가 달라지는 함수에 `@overload`를 검토했습니다
- [ ] 데코레이터에서 `ParamSpec`으로 시그니처를 보존했습니다
- [ ] 불필요한 `Callable[..., T]` 사용을 줄였습니다

## 연습 문제

1. `map_values(data: dict[str, int], transform: Callable[[int], float]) -> dict[str, float]` 함수를 작성해 보세요.

2. `ParamSpec`을 사용해 실행 시간을 출력하는 데코레이터를 만들고, 감싼 함수 시그니처가 유지되는지 확인해 보세요.

3. `serialize(data: dict) -> str`, `serialize(data: list) -> str` 두 경우를 가진 오버로드 함수를 작성해 보세요.

## 정리와 다음 글

함수 타입 힌트는 "함수도 값"이라는 Python 특성을 타입 시스템 안으로 끌어옵니다. `Callable`은 함수 모양을, `@overload`는 여러 합법적 호출 계약을, `ParamSpec`은 데코레이터를 거친 뒤에도 시그니처가 살아남게 해 줍니다. 콜백과 데코레이터를 많이 쓰는 코드일수록 이 도구들의 가치가 빨리 드러납니다.

다음 글에서는 키와 필드 이름이 있는 구조화 데이터를 타입으로 다루는 `TypedDict`와 `dataclass`를 보겠습니다.

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


## Callable과 overload 실전 조합

```python
from typing import overload
from collections.abc import Callable

@overload
def execute(fn: Callable[[int], int], value: int) -> int: ...

@overload
def execute(fn: Callable[[str], str], value: str) -> str: ...


def execute(fn: Callable[[int], int] | Callable[[str], str], value: int | str) -> int | str:
    return fn(value)  # type: ignore[arg-type]
```

위 구현은 오버로드 선언과 구현의 분리가 필요하다는 점을 보여 줍니다. 구현 본문에서 오류를 피하려면 분기 처리가 필요합니다.

```python
def execute(fn: Callable[[int], int] | Callable[[str], str], value: int | str) -> int | str:
    if isinstance(value, int):
        int_fn = fn  # 실제 코드에서는 분리 설계를 권장
        return int_fn(value)  # type: ignore[misc]
    str_fn = fn
    return str_fn(value)  # type: ignore[misc]
```

## 데코레이터에서 흔한 오류

```text
error: Untyped decorator makes function "create_order" untyped  [misc]
```

이 오류가 보이면 `ParamSpec`과 `TypeVar` 기반 데코레이터로 바꾸는 것이 우선입니다.

## 콜백 계약 설계 표

| 상황 | 권장 시그니처 |
| --- | --- |
| 성공/실패 콜백 | `Callable[[Result], None]` |
| 변환 함수 주입 | `Callable[[T], U]` |
| 지연 실행 팩토리 | `Callable[[], T]` |
| 임시 우회 | `Callable[..., Any]` (최소화) |


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


## 데코레이터 점검: ParamSpec 유지 확인

데코레이터를 적용한 뒤 원래 시그니처가 보존되는지 반드시 확인해야 합니다.

```python
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def traced(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)
    return wrapper
```

```bash
$ pyright src/decorators.py
0 errors, 0 warnings, 0 informations
```

이 확인이 빠지면 데코레이터 계층 아래에서 `Any`가 확산되기 쉽습니다.

## 처음 질문으로 돌아가기

- **함수 자체를 인자로 받는 매개변수는 어떻게 타입을 붙일까요?**
  - 함수 값은 `Callable[[인자 타입들], 반환 타입]`으로 적습니다. 본문에서 `apply_operation(values: list[int], op: Callable[[int], int])`와 `retry(func: Callable[[], T], attempts: int) -> T`를 사용해 콜백 시그니처와 반환 타입 연결을 구체적으로 보여 줬습니다.
- **`*args`, `**kwargs`는 무엇에 타입을 붙이는 걸까요?**
  - `*args: str`은 각 위치 인자가 문자열이라는 뜻이고, `**kwargs: int`는 각 키워드 값이 정수라는 뜻입니다. 그래서 `log_call(*args: str, **kwargs: int)` 예시에서 분석기는 `args`를 `tuple[str, ...]`로, `kwargs` 값을 `int`로 추론합니다.
- **입력 타입에 따라 반환 타입이 달라지는 함수는 어떻게 표현할까요?**
  - 이런 함수는 `@overload`로 합법적인 호출 시그니처를 먼저 나열하고, 마지막에 실제 구현 하나를 둡니다. `parse_value(raw: str) -> dict[str, str]`와 `parse_value(raw: bytes) -> dict[str, bytes]`를 분리해 적은 뒤 구현에서 `str | bytes`를 함께 처리한 패턴이 그 예입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Type Hints in Python 101 (1/10): Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [Type Hints in Python 101 (2/10): 기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Type Hints in Python 101 (3/10): Optional과 Union](./03-optional-and-union.md)
- **함수 타입 힌트 (현재 글)**
- TypedDict와 dataclass (예정)
- Protocol과 structural typing (예정)
- Generic 이해하기 (예정)
- mypy와 pyright 사용하기 (예정)
- Pydantic과 타입 힌트 (예정)
- 타입 힌트를 잘 쓰는 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — typing.Callable](https://docs.python.org/3/library/typing.html#typing.Callable)
- [Python 공식 문서 — typing.overload](https://docs.python.org/3/library/typing.html#typing.overload)
- [PEP 612 — Parameter Specification Variables](https://peps.python.org/pep-0612/)
- [mypy 문서 — Callable types](https://mypy.readthedocs.io/en/stable/kinds_of_types.html#callable-types-and-lambdas)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/type-hints-python-101/ko)
Tags: Python, Type Hints, Callable, 함수 시그니처, 오버로드, 데코레이터

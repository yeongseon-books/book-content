---
series: type-hints-python-101
episode: 7
title: "Type Hints in Python 101 (7/10): Generic 이해하기"
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
  - Generic
  - TypeVar
  - 타입 매개변수
  - 제네릭 프로그래밍
seo_description: TypeVar와 Generic으로 타입 안전한 재사용 코드를 작성하는 방법을 다룹니다.
last_reviewed: '2026-05-15'
---

# Type Hints in Python 101 (7/10): Generic 이해하기

여러 타입에 재사용되는 함수를 만들고 싶은데, 입력 타입과 출력 타입의 관계는 유지하고 싶을 때가 있습니다. `Any`를 쓰면 타입 정보가 사라지고, 타입별 함수를 따로 만들면 코드가 늘어납니다. 이때 Generic이 등장합니다.

이 글은 Type Hints (Python) 101 시리즈의 7번째 글입니다. 여기서는 `TypeVar`, `Generic`, bound, constraint, Python 3.12 문법까지 제네릭 타입의 핵심을 정리합니다.


![Type Hints in Python 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/07/07-01-concept-at-a-glance.ko.png)
*Type Hints in Python 101 7장 흐름 개요*

> Generic은 '여러 타입에 재사용되지만 입력과 출력의 타입 관계는 유지해야 하는' 함수·클래스를 적기 위한 장치입니다 — `Any`로 도망가면 정보가 사라지고, 타입별로 함수를 복제하면 코드가 늘어나는 두 실패 모드를 한 번에 해결합니다.

## 먼저 던지는 질문

- 입력 타입을 그대로 반환 타입에 연결하려면 어떻게 적을까요?
- 재사용 가능한 컨테이너 클래스를 타입 안전하게 만들려면 무엇이 필요할까요?
- bound와 constraint는 어떤 차이가 있을까요?

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
# add("a", "b") # 오류 — str은 허용되지 않습니다.
```

constraint는 상속 계보가 아니라 허용 타입 목록 자체를 제한합니다.

### 5단계: Python 3.12 타입 매개변수 문법

```python
# 예: Python 3.12+ 유형 매개변수 구문
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

## 실무 패턴: 제네릭 래퍼를 도입할 때

Generic은 작은 예제에서는 `first()`나 `Stack[T]`로 보이지만, 실제 저장소에서는 **공통 래퍼와 저장소 추상화**에서 가장 빨리 가치를 드러냅니다. 예를 들어 페이지네이션 응답, 캐시 래퍼, `Repository[T]`, `Result[T]` 같은 구조는 내부 데이터 타입만 바뀌고 나머지 계약은 반복되는 경우가 많습니다.

이때 먼저 해야 할 일은 "타입 매개변수가 실제로 어느 경로를 따라 흐르는가"를 확인하는 것입니다. 입력과 출력이 정말 연결돼 있다면 Generic이 맞습니다. 반대로 반환 타입이 입력 타입과 무관하다면 단순한 구체 타입이나 Protocol이 더 읽기 좋을 수 있습니다.

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Page(Generic[T]):
    def __init__(self, items: list[T], total: int) -> None:
        self.items = items
        self.total = total

def first_item(page: Page[T]) -> T:
    return page.items[0]
```

이 예제의 핵심은 `Page[int]`를 넣으면 `int`가, `Page[str]`를 넣으면 `str`이 그대로 이어진다는 사실입니다. 이런 흐름이 없다면 Generic은 종종 불필요한 추상화가 됩니다.

## 타입 추론이 기대와 다를 때 먼저 볼 점

- 같은 `TypeVar`를 한 함수에서 여러 의미로 재사용하고 있지 않은지 확인합니다.
- `list[T]` 같은 가변 컨테이너는 invariant이므로 `list[Child]`를 `list[Parent]`로 넘길 수 없다는 점을 기억합니다.
- 타입 매개변수가 많아질수록 호출부 추론이 어려워지므로, `T`, `U`, `V`가 동시에 늘어나면 API를 나누는 편이 낫습니다.
- Generic이 필요 없는 곳에서 `Any` 대체재처럼 쓰고 있지 않은지 점검합니다.

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

다음 글에서는 지금까지 붙인 타입 힌트를 실제로 검증하는 mypy와 pyright를 봅니다.

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


## 실전 보강: 적용 전후 + 오류 해결

```python
# before
from typing import Any

def build(value: Any) -> Any:
    return value
```

```python
# after
from typing import TypeVar

T = TypeVar("T")

def build(value: T) -> T:
    return value
```

```text
before 상태에서는 검사기가 의미 있는 오류를 거의 만들지 못합니다.
after 상태에서는 호출부 타입 불일치를 정확히 보고합니다.
```

## 팀 운영 패턴

| 단계 | 실행 항목 |
| --- | --- |
| 로컬 개발 | pyright/Pylance 즉시 피드백 |
| PR 전 검증 | mypy 단일 명령 통과 |
| CI 게이트 | 실패 시 병합 차단 |
| 예외 관리 | `type: ignore`에 사유와 코드 기재 |


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


## Generic 클래스 구현 예시: Repository[T]

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Repository(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def add(self, item: T) -> None:
        self._items.append(item)

    def get_all(self) -> list[T]:
        return self._items
```

```bash
$ pyright src/repository.py
0 errors, 0 warnings, 0 informations
```

`Repository[User]`, `Repository[Order]`처럼 타입 매개변수를 바꿔도 동일한 계약을 재사용할 수 있다는 점이 핵심입니다.

## 처음 질문으로 돌아가기

- **입력 타입을 그대로 반환 타입에 연결하려면 어떻게 적을까요?**
  - `T = TypeVar("T")`를 선언한 뒤 `def identity(value: T) -> T`나 `def first(items: list[T]) -> T`처럼 같은 타입 변수를 입력과 반환에 함께 쓰면 됩니다. 그래서 `first([1, 2, 3])`는 `int`, `identity("hello")`는 `str`로 추론되며 `Any`처럼 정보가 사라지지 않습니다.
- **재사용 가능한 컨테이너 클래스를 타입 안전하게 만들려면 무엇이 필요할까요?**
  - 클래스에 `Generic[T]`를 붙여 타입 매개변수를 올려야 합니다. 본문의 `Stack(Generic[T])`, `Page[T]`, `Repository[T]` 예시처럼 `push`, `pop`, `items`, `all()`이 같은 `T`를 공유해야 컨테이너 전체 계약이 무너지지 않습니다.
- **bound와 constraint는 어떤 차이가 있을까요?**
  - `bound=Comparable`은 상한 타입을 두어 그 계열 안에서만 허용하는 방식이고, `TypeVar("Number", int, float)`는 허용 가능한 타입 목록을 직접 제한하는 constraint입니다. 본문의 `find_min(items: list[C]) -> C`와 `add(a: Number, b: Number) -> Number`가 이 차이를 각각 보여 줍니다.

<!-- toc:begin -->
## 시리즈 목차

- [Type Hints in Python 101 (1/10): Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [Type Hints in Python 101 (2/10): 기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Type Hints in Python 101 (3/10): Optional과 Union](./03-optional-and-union.md)
- [Type Hints in Python 101 (4/10): 함수 타입 힌트](./04-function-type-hints.md)
- [Type Hints in Python 101 (5/10): TypedDict와 dataclass](./05-typeddict-and-dataclass.md)
- [Type Hints in Python 101 (6/10): Protocol과 structural typing](./06-protocol-and-structural-typing.md)
- **Generic 이해하기 (현재 글)**
- mypy와 pyright 사용하기 (예정)
- Pydantic과 타입 힌트 (예정)
- 타입 힌트를 잘 쓰는 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — typing.TypeVar](https://docs.python.org/3/library/typing.html#typing.TypeVar)
- [Python 공식 문서 — typing.Generic](https://docs.python.org/3/library/typing.html#typing.Generic)
- [Python typing specification — Generics](https://typing.python.org/en/latest/spec/generics.html)
- [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/)
- [mypy 문서 — Variance of generic types](https://mypy.readthedocs.io/en/stable/generics.html#variance-of-generic-types)
- [mypy 문서 — Generics](https://mypy.readthedocs.io/en/stable/generics.html)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/type-hints-python-101/ko)
Tags: Python, Type Hints, Generic, TypeVar, 타입 매개변수, 제네릭 프로그래밍

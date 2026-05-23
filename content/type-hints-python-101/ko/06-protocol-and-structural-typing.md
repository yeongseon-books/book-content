---
series: type-hints-python-101
episode: 6
title: "Type Hints in Python 101 (6/10): Protocol과 structural typing"
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
  - Protocol
  - structural typing
  - 덕 타이핑
  - 인터페이스
seo_description: Protocol로 상속 없이 인터페이스를 정의하고 structural typing을 활용하는 방법을 다룹니다.
last_reviewed: '2026-05-15'
---

# Type Hints in Python 101 (6/10): Protocol과 structural typing

Python은 오래전부터 덕 타이핑을 써 왔습니다. `close()`가 있으면 닫을 수 있는 객체로 취급하고, `render()`가 있으면 렌더링 가능한 객체로 취급합니다. 그런데 전통적인 추상 베이스 클래스는 여전히 명시적 상속을 요구합니다.

이 글은 Type Hints (Python) 101 시리즈의 6번째 글입니다. 여기서는 `Protocol`로 "이 메서드가 있으면 충분하다"는 계약을 어떻게 적는지, 그리고 그것이 structural typing과 어떻게 연결되는지 살펴봅니다.


![Type Hints in Python 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/06/06-01-concept-at-a-glance.ko.png)
*Type Hints in Python 101 6장 흐름 개요*

## 먼저 던지는 질문

- 상속 없이 인터페이스 계약을 적을 수 있을까요?
- ABC와 Protocol은 무엇이 다를까요?
- 속성만으로도 Protocol을 만족시킬 수 있을까요?

## 왜 이 주제가 중요한가

상속 기반 인터페이스는 결합도를 높입니다. 외부 라이브러리 클래스나 이미 만들어진 내부 클래스가 필요한 메서드를 모두 갖고 있어도, 베이스 클래스를 상속하지 않았다는 이유만으로 타입 호환이 깨질 수 있습니다. `Protocol`은 이 문제를 줄입니다.

즉, 중요한 것은 계보가 아니라 구조입니다. 필요한 메서드와 속성이 있으면 타입 검사기는 그 객체를 호환 가능한 것으로 봅니다. 이 방식은 Python 런타임의 실제 사용 방식과도 잘 맞습니다.

## 한눈에 보는 개념

```text
class Closeable(Protocol):     class FileHandler:
    def close(self) -> None:       def close(self) -> None:
        ...                            self.file.close()

        │                                    │
        └──── 구조가 맞으므로 호환됨 ───────────┘
                 (상속 필요 없음)
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Protocol | 필요한 메서드와 속성을 정의하지만 상속을 강제하지 않는 타입 계약입니다 |
| structural typing | 상속 계보가 아니라 구조로 타입 호환성을 판단하는 방식입니다 |
| nominal typing | 명시적 클래스 계층으로 호환성을 판단하는 방식입니다 |
| @runtime_checkable | Protocol에 대해 `isinstance()`를 허용하는 데코레이터입니다 |
| ABC | 공통 구현과 추상 메서드를 함께 둘 수 있는 상속 기반 추상 클래스입니다 |

## 바꾸기 전과 후

```python
from abc import ABC, abstractmethod

class Closeable(ABC):
    @abstractmethod
    def close(self) -> None: ...

class FileHandler(Closeable):  # 상속 필요
    def close(self) -> None:
        print("closed")

def cleanup(resource: Closeable) -> None:
    resource.close()
```

```python
from typing import Protocol

class Closeable(Protocol):
    def close(self) -> None: ...

class FileHandler:  # 상속 불필요
    def close(self) -> None:
        print("closed")

def cleanup(resource: Closeable) -> None:
    resource.close()

cleanup(FileHandler())  # OK
```

## 단계별로 익히기

### 1단계: 기본 Protocol 정의하기

```python
from typing import Protocol

class Renderable(Protocol):
    def render(self) -> str: ...

class HtmlWidget:
    def render(self) -> str:
        return "<div>Hello</div>"

class JsonResponse:
    def render(self) -> str:
        return '{"message": "hello"}'

def display(item: Renderable) -> None:
    print(item.render())

display(HtmlWidget())     # OK
display(JsonResponse())   # OK
```

둘 다 `Renderable`을 상속하지 않았지만, `render() -> str` 구조가 맞기 때문에 호환됩니다.

### 2단계: 속성을 가진 Protocol

```python
from typing import Protocol

class Named(Protocol):
    name: str

class User:
    def __init__(self, name: str) -> None:
        self.name = name

class Product:
    def __init__(self, name: str, price: int) -> None:
        self.name = name
        self.price = price

def greet(entity: Named) -> str:
    return f"Hello, {entity.name}!"

greet(User("Alice"))             # OK
greet(Product("Book", 25))       # OK
```

메서드뿐 아니라 속성도 Protocol 계약에 넣을 수 있습니다.

### 3단계: `@runtime_checkable`

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Sizeable(Protocol):
    def __len__(self) -> int: ...

print(isinstance([1, 2, 3], Sizeable))   # True
print(isinstance("hello", Sizeable))     # True
print(isinstance(42, Sizeable))          # False
```

다만 이 검사는 메서드 존재 여부만 확인할 뿐, 시그니처 전체를 정밀하게 검증하지는 않습니다.

### 4단계: Protocol 상속으로 합성하기

```python
from typing import Protocol

class Readable(Protocol):
    def read(self) -> str: ...

class Writable(Protocol):
    def write(self, data: str) -> None: ...

class ReadWritable(Readable, Writable, Protocol):
    ...

class FileHandler:
    def read(self) -> str:
        return "data"

    def write(self, data: str) -> None:
        print(f"Writing: {data}")

def process(stream: ReadWritable) -> None:
    content = stream.read()
    stream.write(content.upper())

process(FileHandler())  # OK
```

### 5단계: ABC와 Protocol의 선택 기준

```python
from abc import ABC, abstractmethod
from typing import Protocol

# 모든 구현 클래스를 직접 관리하고, 공통 구현도 주고 싶을 때
class BasePlugin(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    def log(self) -> None:
        print(f"Running {self.__class__.__name__}")

# 외부 클래스도 구조만 맞으면 받으려 할 때
class Executable(Protocol):
    def execute(self) -> None: ...
```

공통 구현이 필요하면 ABC가 맞고, 느슨한 인터페이스 계약이 필요하면 Protocol이 더 잘 맞습니다.

## 실무 마이그레이션 패턴

기존 저장소에는 이미 `S3Storage`, `LocalStorage`, `FakeStorage` 같은 구현이 흩어져 있고, 그 위에 서비스 코드가 구체 클래스 이름을 직접 물고 있는 경우가 많습니다. 이때 가장 안전한 시작점은 모든 구현을 당장 상속 구조로 묶는 일이 아니라, **지금 공통으로 쓰이는 최소 시그니처를 Protocol로 먼저 추출하는 것**입니다.

예를 들어 업로드 서비스가 실제로 쓰는 기능이 `save()`와 `open()`뿐이라면, 먼저 그 둘만 가진 `StorageBackend` Protocol을 만들고 서비스 함수의 매개변수를 그 타입으로 바꿉니다. 그다음 테스트 더블, 로컬 구현, 클라우드 구현이 모두 통과하는지 mypy나 pyright로 확인합니다. 이렇게 하면 구현 클래스를 뜯어고치지 않고도 의존성 방향을 뒤집을 수 있습니다.

```python
from typing import Protocol

class StorageBackend(Protocol):
    def save(self, path: str, data: bytes) -> None: ...
    def open(self, path: str) -> bytes: ...

def publish_report(storage: StorageBackend, path: str, data: bytes) -> bytes:
    storage.save(path, data)
    return storage.open(path)
```

이 방식의 장점은 리뷰 범위를 작게 유지한다는 사실입니다. 호출부는 계약만 바꾸고, 각 구현체는 구조가 맞는지만 확인하면 됩니다. Protocol 도입 초기에 저장소 전체를 한 번에 일반화하려고 들면 오히려 메서드 수만 불필요하게 늘고 계약이 흐려지기 쉽습니다.

## 호환성 문제가 생기면 먼저 볼 점

- Protocol 속성 타입이 실제 구현보다 더 좁지 않은지 확인합니다.
- 메서드 이름은 같지만 반환 타입이 다르면 structural typing도 통과하지 못합니다.
- `@runtime_checkable` 결과와 정적 검사 결과가 다를 수 있다는 점을 구분합니다. 런타임 `isinstance()`는 시그니처 전체를 보지 않습니다.
- Protocol이 너무 커져서 대부분 구현이 일부 메서드만 쓰는 상태라면, 읽기 전용/쓰기 전용처럼 더 작은 계약으로 분리합니다.

## 여기서 먼저 봐야 할 점

- Protocol은 구현보다 시그니처를 정의하는 도구입니다.
- 구조만 맞으면 상속 없이도 호환됩니다.
- `@runtime_checkable`은 제한적인 런타임 확인 수단입니다.
- 여러 Protocol을 합쳐 더 큰 계약으로 만들 수 있습니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| Protocol에 실제 구현을 넣음 | 인터페이스와 구현 경계가 흐려집니다 | 본문은 `...`로 두고 계약만 적습니다 |
| 다중 상속 Protocol에서 `Protocol` 베이스를 빼먹음 | 일반 클래스로 바뀔 수 있습니다 | 베이스 목록에 `Protocol`을 유지합니다 |
| `runtime_checkable`로 시그니처 검증까지 된다고 생각함 | 존재 여부만 봅니다 | 정밀 검증은 mypy/pyright에 맡깁니다 |
| 공통 구현이 필요한데 Protocol을 선택함 | 기본 메서드를 제공하기 어렵습니다 | 공통 구현이 필요하면 ABC를 씁니다 |
| Protocol을 너무 잘게 쪼갬 | 읽기와 유지보수가 어려워집니다 | 함께 움직이는 메서드는 하나로 묶습니다 |

## 실무에서는 이렇게 연결됩니다

- 플러그인 시스템은 `execute()`만 있으면 받는 Protocol을 둘 수 있습니다.
- 테스트에서는 mock 객체가 구조만 맞아도 Protocol 계약을 만족할 수 있습니다.
- 어댑터 패턴은 외부 클래스 수정 없이 내부 Protocol을 만족시키는 데 유리합니다.
- 저장소 계층은 서로 다른 백엔드가 같은 Protocol을 구현하도록 만들 수 있습니다.

## 실무 판단 기준

공개 인터페이스를 설계할 때는 ABC보다 Protocol이 더 유연한 경우가 많습니다. 구현 클래스가 인터페이스의 존재를 미리 알 필요가 없고, 외부 라이브러리 타입도 쉽게 수용할 수 있기 때문입니다. 특히 "우리가 소유하지 않은 클래스도 받아야 한다"는 조건이 있다면 Protocol이 거의 기본 선택입니다.

반대로 공통 기본 구현, 헬퍼 메서드, 서브클래스 강제가 중요하면 ABC가 낫습니다. 두 도구는 경쟁 관계라기보다 계약의 성격이 다른 도구라고 보는 편이 정확합니다.

## 체크리스트

- [ ] 외부 클래스도 만족해야 하는 인터페이스에 Protocol을 사용했습니다
- [ ] 공통 구현이 필요한 경우에만 ABC를 고려했습니다
- [ ] `isinstance()`가 꼭 필요할 때만 `@runtime_checkable`을 붙였습니다
- [ ] Protocol을 핵심 메서드 중심으로 유지했습니다
- [ ] mypy나 pyright로 호환성을 확인할 준비가 되어 있습니다

## 연습 문제

1. `to_json() -> str`와 `from_json(data: str)`를 가진 `Serializable` Protocol을 정의해 보세요.

2. `get(id: int)`, `save(entity)`, `delete(id: int)`를 가진 `Repository` Protocol을 만들고 서비스 함수를 연결해 보세요.

3. 같은 인터페이스를 ABC와 Protocol 두 방식으로 각각 구현해 차이를 비교해 보세요.

## 정리와 다음 글

`Protocol`은 Python 타입 시스템에서 structural typing을 구현하는 핵심 도구입니다. 상속이 아니라 메서드와 속성의 구조로 호환성을 판단하므로, Python의 덕 타이핑과 잘 맞습니다. 공통 구현이 필요할 때는 ABC, 느슨하고 확장 가능한 인터페이스 계약이 필요할 때는 Protocol을 쓰면 됩니다.

다음 글에서는 타입 관계를 입력과 출력 사이에 그대로 보존하는 Generic을 다루겠습니다.


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


## Protocol 호환성 점검 로그

```python
from typing import Protocol

class Sender(Protocol):
    def send(self, payload: bytes) -> None: ...

class KafkaProducer:
    def send(self, payload: bytes) -> None:
        ...
```

```bash
$ mypy src/messaging.py
Success: no issues found in 1 source file
```

```text
핵심 점검: 명시적 상속 없이도 시그니처 구조가 맞으면 Protocol 계약이 성립합니다.
```

구조 기반 계약을 쓰면 외부 라이브러리 객체를 래핑하지 않고도 인터페이스 경계를 세울 수 있습니다.

## 처음 질문으로 돌아가기

- **상속 없이 인터페이스 계약을 적을 수 있을까요?**
  - 가능합니다. `class Closeable(Protocol): def close(self) -> None: ...`처럼 계약만 적어 두면 `FileHandler`가 이를 상속하지 않아도 `close()` 구조가 맞는 순간 `cleanup(resource: Closeable)`에 그대로 넘길 수 있습니다.
- **ABC와 Protocol은 무엇이 다를까요?**
  - ABC는 `BasePlugin` 예시처럼 공통 구현과 명시적 상속을 전제로 하고, Protocol은 `Executable`처럼 구조만 맞으면 외부 클래스도 받을 수 있습니다. 그래서 본문은 공통 로직을 줄 때는 ABC, 느슨한 인터페이스 경계와 외부 타입 수용이 중요할 때는 Protocol을 선택하라고 정리했습니다.
- **속성만으로도 Protocol을 만족시킬 수 있을까요?**
  - 가능합니다. `class Named(Protocol): name: str`처럼 속성 계약만 둔 뒤 `User`와 `Product`가 `self.name`만 제공해도 `greet(entity: Named)`에 모두 통과했습니다. 즉, Protocol은 메서드뿐 아니라 속성 구조도 계약의 일부로 다룰 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Type Hints in Python 101 (1/10): Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [Type Hints in Python 101 (2/10): 기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Type Hints in Python 101 (3/10): Optional과 Union](./03-optional-and-union.md)
- [Type Hints in Python 101 (4/10): 함수 타입 힌트](./04-function-type-hints.md)
- [Type Hints in Python 101 (5/10): TypedDict와 dataclass](./05-typeddict-and-dataclass.md)
- **Protocol과 structural typing (현재 글)**
- Generic 이해하기 (예정)
- mypy와 pyright 사용하기 (예정)
- Pydantic과 타입 힌트 (예정)
- 타입 힌트를 잘 쓰는 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Python typing specification — Protocols](https://typing.python.org/en/latest/spec/protocol.html)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Python 공식 문서 — abc 모듈](https://docs.python.org/3/library/abc.html)
- [mypy 문서 — Protocols and structural subtyping](https://mypy.readthedocs.io/en/stable/protocols.html)
- [Real Python — Structural Typing](https://realpython.com/python-protocol/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/type-hints-python-101/ko)
Tags: Python, Type Hints, Protocol, structural typing, 덕 타이핑, 인터페이스

---
title: "Object-Oriented Programming 101 (5/10): 다형성"
series: oop-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
  - Python
  - OOP
  - 다형성
  - 덕 타이핑
  - 프로토콜
last_reviewed: '2026-05-12'
seo_description: 덕 타이핑과 Protocol을 포함해 Python 다형성을 실무 관점에서 설명합니다.
---

# Object-Oriented Programming 101 (5/10): 다형성

다형성을 이해하지 못하면 객체지향 코드는 곧 분기문 모음으로 돌아가기 쉽습니다. 결제 수단이 늘 때마다 `if isinstance(...)`가 늘어나고, 파일 저장 방식이 바뀔 때마다 호출부가 함께 수정됩니다. 겉으로는 객체를 썼는데, 실제로는 타입 분기 중심 코드에 머무는 셈입니다.

Python은 여기서 특히 흥미롭습니다. 상속만으로 다형성을 만드는 언어가 아니라, 덕 타이핑과 `Protocol`까지 활용해 같은 인터페이스를 다양한 방식으로 표현할 수 있기 때문입니다. 중요한 것은 클래스 계층보다 호출부가 무엇을 기대하는지 명확히 하는 일입니다.

이 글은 OOP 101 시리즈의 5번째 글입니다.


![Object-Oriented Programming 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/05/05-01-big-picture.ko.png)
*Object-Oriented Programming 101 5장 흐름 개요*

## 먼저 던지는 질문

- 다형성은 왜 타입 분기문을 줄이는 가장 강력한 도구일까요?
- 상속 기반 다형성과 덕 타이핑은 어떤 차이로 쓰일까요?
- `Protocol`은 덕 타이핑을 정적 분석 차원에서 어떻게 보강할까요?

## 핵심 개념 잡기

> Python에서 다형성의 세 가지 방식

```text
1. Inheritance-based polymorphism
   Animal -> Dog.speak(), Cat.speak()

2. Duck Typing
   "If it has a quack() method, it's a duck"
   No inheritance needed — just matching methods

3. Protocol — Python 3.8+
   Structural subtyping: type hints verify duck typing
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 다형성(polymorphism) | 같은 인터페이스가 타입에 따라 다르게 동작하는 것입니다 |
| 덕 타이핑(duck typing) | 객체의 타입이 아니라 메서드의 존재 여부로 판단합니다 |
| 프로토콜(Protocol) | 구조적 서브타이핑을 지원하는 typing 모듈의 클래스입니다 |
| 디스패치(dispatch) | 호출 시점에 실제 타입의 메서드를 선택하는 메커니즘입니다 |
| 인터페이스(interface) | 객체가 제공해야 하는 메서드의 집합입니다 |

## 전후 비교

결제 처리를 비교합니다.

```python
# before: 타입 기반 분기 — 결제 수단이 늘 때마다 수정 필요
def process_payment(payment, amount):
    if payment["type"] == "credit_card":
        print(f"Credit card payment: ${amount}")
    elif payment["type"] == "bank_transfer":
        print(f"Bank transfer: ${amount}")
    # 새 결제 수단 추가 -> elif 추가
```

```python
# after: polymorphism — 새 결제 수단에도 기존 코드 수정 불필요
class CreditCard:
    def pay(self, amount: int) -> str:
        return f"Credit card payment: ${amount}"

class BankTransfer:
    def pay(self, amount: int) -> str:
        return f"Bank transfer: ${amount}"

def process_payment(payment, amount: int) -> None:
    print(payment.pay(amount))  # any type with pay() works
```

## 단계별 실습

### 1단계: 상속 기반 다형성

```python
class Shape:
    def area(self) -> float:
        raise NotImplementedError

    def describe(self) -> str:
        return f"{type(self).__name__}: area = {self.area():.2f}"

class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

class Triangle(Shape):
    def __init__(self, base: float, height: float) -> None:
        self.base = base
        self.height = height

    def area(self) -> float:
        return 0.5 * self.base * self.height

shapes: list[Shape] = [Circle(5), Rectangle(4, 6), Triangle(3, 8)]
for shape in shapes:
    print(shape.describe())
# Circle: area = 78.54
# Rectangle: area = 24.00
# Triangle: area = 12.00
```

### 2단계: 덕 타이핑

```python
class FileWriter:
    def write(self, data: str) -> None:
        print(f"Writing to file: {data}")

class DatabaseWriter:
    def write(self, data: str) -> None:
        print(f"Saving to DB: {data}")

class ApiWriter:
    def write(self, data: str) -> None:
        print(f"Sending to API: {data}")

def save_data(writer, data: str) -> None:
    """The type of writer does not matter — only the write() method"""
    writer.write(data)

save_data(FileWriter(), "hello")       # Writing to file: hello
save_data(DatabaseWriter(), "hello")   # Saving to DB: hello
save_data(ApiWriter(), "hello")        # Sending to API: hello
```

### 3단계: Protocol을 사용한 구조적 서브타이핑

```python
from typing import Protocol

class Writable(Protocol):
    def write(self, data: str) -> None: ...

class ConsoleWriter:
    def write(self, data: str) -> None:
        print(f"Console output: {data}")

class NetworkWriter:
    def write(self, data: str) -> None:
        print(f"Network send: {data}")

def save_all(writers: list[Writable], data: str) -> None:
    for writer in writers:
        writer.write(data)

writers: list[Writable] = [ConsoleWriter(), NetworkWriter()]
save_all(writers, "important data")
# 콘솔 출력: 중요한 데이터
# 네트워크 전송: 중요한 데이터
```

### 4단계: 내장 다형성 활용

```python
class Team:
    def __init__(self, name: str, members: list[str]) -> None:
        self.name = name
        self.members = members

    def __len__(self) -> int:
        return len(self.members)

    def __contains__(self, member: str) -> bool:
        return member in self.members

    def __iter__(self):
        return iter(self.members)

team = Team("Backend", ["Kim", "Lee", "Park"])
print(len(team))          # 3
print("Kim" in team)      # True
print(list(team))         # ['Kim', 'Lee', 'Park']

for member in team:
    print(member)
```

### 5단계: functools.singledispatch

```python
from functools import singledispatch

@singledispatch
def format_value(value) -> str:
    return str(value)

@format_value.register(int)
def _(value: int) -> str:
    return f"{value:,}"

@format_value.register(float)
def _(value: float) -> str:
    return f"{value:.2f}"

@format_value.register(list)
def _(value: list) -> str:
    return f"[{len(value)} items]"

print(format_value(1000000))       # 1,000,000
print(format_value(3.14159))       # 3.14
print(format_value([1, 2, 3]))     # [3 items]
print(format_value("hello"))       # hello
```

## 이 코드에서 주목할 점

- Python의 덕 타이핑은 상속 없이도 다형성을 구현합니다
- `Protocol`은 타입 검사기가 덕 타이핑을 검증하게 합니다
- `__len__`, `__contains__`, `__iter__` 등 특수 메서드로 Python 내장 문법과 통합합니다
- `singledispatch`는 인자 타입에 따라 다른 함수를 호출하는 함수 수준 다형성입니다

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `isinstance()` 분기 남발 | 다형성의 이점이 사라집니다 | 공통 인터페이스로 통일합니다 |
| 덕 타이핑에서 메서드 이름 불일치 | `AttributeError`가 런타임에 발생합니다 | `Protocol`로 타입 힌트를 추가합니다 |
| 모든 것을 상속으로 해결 | 불필요한 계층이 생깁니다 | 덕 타이핑이나 Protocol을 먼저 고려합니다 |
| `NotImplementedError` 미발생 | 부모의 기본 구현이 의도치 않게 사용됩니다 | 추상 메서드가 필요하면 ABC를 사용합니다 |
| Protocol에 구현 코드 작성 | Protocol은 인터페이스 정의용입니다 | 메서드 본문은 `...`만 작성합니다 |

## 실무에서 이렇게 쓰입니다

- 플러그인 시스템에서 공통 인터페이스로 확장 모듈을 통합합니다
- 테스트에서 mock 객체가 같은 인터페이스를 구현하여 실제 의존성을 대체합니다
- 직렬화 라이브러리(JSON, YAML, pickle)가 같은 `dump`/`load` 인터페이스를 제공합니다
- 웹 프레임워크의 미들웨어가 공통 인터페이스로 요청/응답을 처리합니다
- 데이터베이스 드라이버가 DB-API 2.0 인터페이스를 통일하여 교체 가능합니다

## 현업 개발자는 이렇게 생각합니다

Python에서 다형성은 "의도적으로 설계"하기보다 "자연스럽게 발생"합니다. 덕 타이핑 덕분에 같은 메서드를 가진 객체는 상속 관계 없이 교체할 수 있습니다.

타입 안전성이 중요한 프로젝트에서는 `Protocol`을 적극 활용합니다. 런타임에는 아무 영향이 없지만 타입 검사기(mypy)가 인터페이스 위반을 잡아줍니다.

## 체크리스트

- [ ] 상속 기반 다형성을 구현할 수 있다
- [ ] 덕 타이핑의 원리를 이해하고 활용할 수 있다
- [ ] `Protocol`을 사용하여 구조적 서브타이핑을 정의할 수 있다
- [ ] 특수 메서드로 Python 내장 문법과 통합할 수 있다
- [ ] `isinstance()` 분기 대신 다형성을 적용할 수 있다

## 정리 및 다음 글 안내

다형성은 같은 인터페이스로 다른 구현을 호출하여 코드의 유연성을 높입니다. Python은 덕 타이핑, 상속, Protocol 세 가지 방식으로 다형성을 지원합니다. 다음 글에서는 추상화를 통해 공통 인터페이스를 강제하는 방법을 알아봅니다.

## 실전 패턴 추가: SOLID와 상속 경계를 코드로 확인하기

객체지향 설계에서 흔한 실패는 클래스 수를 늘리는 것 자체를 목표로 삼는 경우입니다. 실제로는 역할 분리와 변경 방향 분리가 핵심입니다. 아래 예시는 SRP와 OCP를 지키는 방식으로 결제 도메인을 구성하고, 상속 대신 조합을 어떻게 쓰는지 보여 줍니다.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class PaymentRequest:
    order_id: str
    amount: int


class PaymentGateway(Protocol):
    def pay(self, req: PaymentRequest) -> str:
        ...


class CardGateway:
    def pay(self, req: PaymentRequest) -> str:
        return f"card:{req.order_id}:{req.amount}"


class BankGateway:
    def pay(self, req: PaymentRequest) -> str:
        return f"bank:{req.order_id}:{req.amount}"


class PaymentService:
    def __init__(self, gateway: PaymentGateway) -> None:
        self.gateway = gateway

    def process(self, order_id: str, amount: int) -> str:
        if amount <= 0:
            raise ValueError("amount must be positive")
        return self.gateway.pay(PaymentRequest(order_id=order_id, amount=amount))
```

새 결제 수단을 추가할 때 `PaymentService`는 수정하지 않고 `PaymentGateway` 계약을 구현한 클래스를 하나 더 추가하면 됩니다. 이것이 OCP의 실제 효과입니다. 또한 상속을 억지로 사용하지 않고 Protocol + 조합을 사용했기 때문에, 런타임 교체와 테스트 더블 주입이 쉬워집니다. 객체지향의 목적은 계층 깊이를 늘리는 것이 아니라 변경 파급을 줄이는 데 있다는 점을 항상 기준으로 두는 편이 좋습니다.

## 다형성의 핵심은 if/elif 제거가 아니라 협력 계약입니다

다형성은 분기문을 없애는 기술이 아니라, 호출자가 구체 타입을 몰라도 같은 계약으로 협력하는 설계입니다.

```text
[CheckoutService] --> [PaymentMethod]
PaymentMethod (interface)
  + pay(amount)
      ^            ^            ^
      |            |            |
 [CardPay]     [BankPay]    [PointPay]
```

## 적용 전후: 타입 분기에서 다형성으로

```python
# before

def pay(method: str, amount: int) -> str:
    if method == 'card':
        return f'card:{amount}'
    if method == 'bank':
        return f'bank:{amount}'
    if method == 'point':
        return f'point:{amount}'
    raise ValueError('unsupported method')
```

```python
# after
from typing import Protocol

class PaymentMethod(Protocol):
    def pay(self, amount: int) -> str:
        ...

class CardPay:
    def pay(self, amount: int) -> str:
        return f'card:{amount}'

class BankPay:
    def pay(self, amount: int) -> str:
        return f'bank:{amount}'

class PointPay:
    def pay(self, amount: int) -> str:
        return f'point:{amount}'

class CheckoutService:
    def __init__(self, method: PaymentMethod) -> None:
        self.method = method

    def checkout(self, amount: int) -> str:
        if amount <= 0:
            raise ValueError('amount must be positive')
        return self.method.pay(amount)
```

## 원칙 위반과 수정

| 위반 | 결과 | 수정 |
|---|---|---|
| `if method == ...` 분기문이 여러 모듈에 복제 | 결제 수단 추가 시 다중 수정 | 계약 인터페이스 + 구현 클래스 |
| 구현 클래스가 호출자 내부 상태를 직접 읽음 | 결합도 상승 | 필요한 데이터만 파라미터로 전달 |
| 공통 예외 처리 누락 | 구현마다 실패 형식 다름 | 공통 예외 정책 계층 분리 |

## 비교표: 상속 기반 다형성 vs 덕 타이핑 Protocol

| 기준 | 상속 기반 | Protocol 기반 |
|---|---|---|
| 기존 코드 적용 | 베이스 클래스 수정 필요 | 기존 클래스에 메서드만 맞추면 됨 |
| 프레임워크 의존 | 상대적으로 큼 | 작음 |
| 테스트 더블 작성 | 서브클래스 필요 | 간단한 스텁 객체로 충분 |

## 리팩터링 체크

- 분기 조건이 타입 이름 문자열인지 먼저 확인합니다.
- 호출자의 관심사를 `pay(amount)` 같은 단일 계약으로 줄입니다.
- 새 타입 추가 시 기존 호출자 수정이 0인지 확인합니다.

## 실전 시나리오: 요구사항 변경을 견디는 구조로 바꾸기

현업에서는 기능 추가보다 규칙 변경이 더 자주 발생합니다. 따라서 클래스 구조를 평가할 때는 "지금 동작하는가"보다 "다음 변경을 어디까지 건드려야 하는가"를 기준으로 보는 편이 안전합니다.

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass
class LineItem:
    name: str
    quantity: int
    unit_price: int

    def subtotal(self) -> int:
        return self.quantity * self.unit_price


class DiscountPolicy(Protocol):
    def apply(self, amount: int) -> int:
        ...


class NoDiscount:
    def apply(self, amount: int) -> int:
        return amount


class PercentDiscount:
    def __init__(self, percent: int) -> None:
        if not 0 <= percent <= 100:
            raise ValueError('percent must be 0..100')
        self.percent = percent

    def apply(self, amount: int) -> int:
        return int(amount * (100 - self.percent) / 100)


class Invoice:
    def __init__(self, items: list[LineItem], policy: DiscountPolicy) -> None:
        self.items = items
        self.policy = policy

    def total(self) -> int:
        base = sum(i.subtotal() for i in self.items)
        return self.policy.apply(base)
```

이 코드는 할인 규칙이 바뀌어도 `Invoice.total()`을 수정할 필요가 없습니다. 확장은 구현 클래스 추가로 닫히고, 핵심 흐름은 안정적으로 유지됩니다.

## UML 스타일로 보는 협력 관계

```text
[Invoice]
  - items: list[LineItem]
  - policy: DiscountPolicy
  + total()

[LineItem]
  + subtotal()

[DiscountPolicy] <<interface>>
  + apply(amount)
      ^
      +-- [NoDiscount]
      +-- [PercentDiscount]
```

협력 구조를 이렇게 텍스트로 적어 두면 코드 리뷰에서 "어디가 정책 축이고 어디가 도메인 축인가"를 빠르게 맞출 수 있습니다.

## 안티패턴과 교정 절차

| 안티패턴 | 발견 신호 | 교정 순서 |
|---|---|---|
| 거대 클래스(God Object) | 메서드가 20개 이상, 변경 이력이 분산됨 | 책임 축 분해 → 협력 인터페이스 도출 |
| 데이터만 가진 빈 클래스 | 메서드 없이 getter/setter만 존재 | 규칙 메서드 이동 또는 dataclass로 단순화 |
| 상속 트리 우회 분기 | 하위 클래스 타입 체크 분기 존재 | 다형성 계약 재정의 |
| 인프라 타입 누수 | 도메인 계층이 SDK 응답 객체 의존 | DTO 변환 계층 추가 |

## 전후 비교: 테스트 유지비

| 항목 | 리팩터링 전 | 리팩터링 후 |
|---|---|---|
| 테스트 준비 | 전역 상태 초기화 필요 | 객체 단위 상태 생성 |
| 실패 원인 추적 | 함수 체인 전체 역추적 | 클래스 메서드 단위 추적 |
| 회귀 범위 | 넓고 불명확 | 좁고 예측 가능 |

## 팀 적용 체크리스트

- 도메인 용어와 클래스 이름이 일치하는지 확인합니다.
- 인스턴스 생성 시점에 불변식이 완성되는지 확인합니다.
- 정책 변경이 기존 코드 수정이 아닌 구현 추가로 가능한지 점검합니다.
- 코드 리뷰에서 UML 텍스트 10줄로 협력 구조를 먼저 합의합니다.
- 테스트 이름이 메서드명보다 비즈니스 규칙을 설명하는지 확인합니다.

## 미니 케이스 스터디: 규칙 추가 한 번으로 검증하기

아래 예시는 정책 확장을 기존 코드 수정 없이 추가하는 최소 단위입니다.

```python
class WeekendPolicy:
    def apply(self, amount: int, is_weekend: bool) -> int:
        if is_weekend:
            return int(amount * 0.95)
        return amount


def estimate(amount: int, is_weekend: bool) -> int:
    policy = WeekendPolicy()
    return policy.apply(amount, is_weekend)
```

핵심은 새로운 정책이 호출 경로를 깨지 않고 들어온다는 사실입니다. 변경 이력이 정책 클래스에만 남도록 경계를 유지하면 회귀 위험이 줄어듭니다.

| 확인 질문 | Pass 기준 |
|---|---|
| 새 정책 추가 시 기존 함수 수정이 필요한가 | 아니오 |
| 예외 정책이 기존 계약과 같은가 | 예 |
| 테스트가 정책별로 분리되어 있는가 | 예 |


## 리팩터링 회고: 변경 비용을 수치로 보는 방법

- 수정 파일 수가 기능 하나당 5개를 넘으면 경계 재설계를 검토합니다.
- 타입 분기 if/elif가 3개 이상 누적되면 다형성 또는 전략 객체로 이동합니다.
- 회귀 테스트 작성 시간이 구현 시간보다 길어지면 책임 배치를 재검토합니다.

```python
def complexity_signal(changed_files: int, branch_count: int) -> str:
    if changed_files >= 5 or branch_count >= 3:
        return 'refactor-needed'
    return 'acceptable'
```

위 방식은 엄밀한 메트릭은 아니지만, 팀이 감각이 아니라 기준으로 논의하게 만드는 데 유용합니다.

## 검증 노트: 객체 설계 품질을 점검하는 질문

아래 질문은 구현 이후 리뷰에서 반복적으로 사용하는 기준입니다.

- 이 메서드가 실패할 때 예외 타입과 메시지가 호출자 계약과 일치하는가.
- 같은 규칙이 다른 클래스나 함수에 중복되어 있지 않은가.
- 상태 변경이 메서드 한 경로로만 이루어지는가.
- 외부 의존성 없이 단위 테스트가 가능한가.

```python
def review_signal(duplicate_rules: int, mutable_paths: int) -> str:
    if duplicate_rules > 0:
        return '중복 규칙 제거 필요'
    if mutable_paths > 1:
        return '상태 변경 경로 통합 필요'
    return '구조 안정'
```

이런 체크를 글 단위 예제에도 적용하면, 객체지향을 문법이 아니라 유지보수 전략으로 이해하는 데 도움이 됩니다.

## 추가 비교: 변경 요청 대응 시간

| 변경 요청 | 경계가 약한 코드 | 경계가 선명한 코드 |
|---|---|---|
| 할인 규칙 추가 | 분기문 탐색 후 다중 수정 | 정책 구현 추가 |
| 상태 전이 수정 | 여러 함수 동시 수정 | 도메인 메서드 수정 |
| 테스트 보강 | 통합 테스트 중심 | 단위 테스트 우선 |

이 비교는 성능 수치가 아니라 유지보수 리드타임을 줄이는 관점에서 중요합니다.

## 보강 메모

설계 선택은 정답 찾기가 아니라 변경 비용을 낮추는 의사결정입니다. 같은 기능이라도 경계를 먼저 정의하면 리뷰와 테스트가 단순해집니다.

## 짧은 리마인더

객체지향을 적용할 때는 "클래스를 몇 개 만들었는가"보다 "다음 변경에서 몇 파일을 수정해야 하는가"를 기준으로 품질을 평가합니다.

## 마지막 점검 문장

이 글의 예제는 모두 변경 파급을 줄이는 경계 설계를 기준으로 구성했습니다.


설계 의도와 테스트 계약을 함께 유지하는 것이 핵심입니다.

## 처음 질문으로 돌아가기

- **다형성은 왜 타입 분기문을 줄이는 가장 강력한 도구일까요?**
  - 글의 출발점은 `payment["type"]`에 따라 `if`를 늘리는 결제 함수였고, 이를 `payment.pay(amount)` 호출 하나로 바꾸면서 새 결제 수단 추가 시 호출부 수정이 사라졌습니다. 같은 흐름은 `Shape.area()`와 `describe()`, 그리고 `CheckoutService`가 `PaymentMethod` 계약만 아는 구조에서도 반복되어, 다형성이 분기문보다 확장 비용을 훨씬 낮춘다는 점을 구체적으로 보여 줍니다.
- **상속 기반 다형성과 덕 타이핑은 어떤 차이로 쓰일까요?**
  - `Circle`, `Rectangle`, `Triangle`은 `Shape`를 상속해 같은 `area()` 계약을 공유하므로 상속 기반 다형성의 전형입니다. 반면 `FileWriter`, `DatabaseWriter`, `ApiWriter`는 공통 부모 없이도 `write()`만 맞추면 `save_data()`에 들어갈 수 있어서, Python에서는 덕 타이핑이 더 느슨하고 기존 코드에도 쉽게 얹을 수 있다는 차이를 확인할 수 있습니다.
- **`Protocol`은 덕 타이핑을 정적 분석 차원에서 어떻게 보강할까요?**
  - `Writable` Protocol을 두면 `ConsoleWriter`와 `NetworkWriter`처럼 상속 관계가 없는 객체도 `write(self, data: str)` 계약만 맞추면 타입 검사기의 확인을 받을 수 있습니다. 즉 런타임의 유연함은 유지하면서도, 메서드 이름 불일치나 잘못된 시그니처를 배포 전에 잡아 주는 안전망이 `Protocol`의 실질적인 가치입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): 캡슐화](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): 상속](./04-inheritance.md)
- **다형성 (현재 글)**
- 추상화 (예정)
- 합성과 상속 (예정)
- SOLID 원칙 기초 (예정)
- 객체지향 설계 예제 (예정)
- 객체지향을 언제 피해야 할까? (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Real Python — Duck Typing in Python](https://realpython.com/duck-typing-python/)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Fluent Python — Chapter 13: Interfaces, Protocols, and ABCs](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 다형성, 덕 타이핑, 프로토콜

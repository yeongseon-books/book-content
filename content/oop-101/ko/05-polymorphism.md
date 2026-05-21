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

## 먼저 던지는 질문

- 다형성은 왜 타입 분기문을 줄이는 가장 강력한 도구일까요?
- 상속 기반 다형성과 덕 타이핑은 어떤 차이로 쓰일까요?
- `Protocol`은 덕 타이핑을 정적 분석 차원에서 어떻게 보강할까요?

## 큰 그림

![Object-Oriented Programming 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/05/05-01-big-picture.ko.png)

*Object-Oriented Programming 101 5장 흐름 개요*

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
# before: type-based branching — requires modification for each new payment method
def process_payment(payment, amount):
    if payment["type"] == "credit_card":
        print(f"Credit card payment: ${amount}")
    elif payment["type"] == "bank_transfer":
        print(f"Bank transfer: ${amount}")
    # new payment method -> add elif
```

```python
# after: polymorphism — no modification needed for new payment methods
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
# Console output: important data
# Network send: important data
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

## 처음 질문으로 돌아가기

- **다형성은 왜 타입 분기문을 줄이는 가장 강력한 도구일까요?**
  - 본문의 기준은 다형성를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **상속 기반 다형성과 덕 타이핑은 어떤 차이로 쓰일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`Protocol`은 덕 타이핑을 정적 분석 차원에서 어떻게 보강할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Python, OOP, 다형성, 덕 타이핑, 프로토콜

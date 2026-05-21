---
title: "Object-Oriented Programming 101 (2/10): 클래스와 인스턴스"
series: oop-101
episode: 2
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
  - 클래스
  - 인스턴스
  - 생성자
last_reviewed: '2026-05-12'
seo_description: Python 클래스의 생성자, 메서드, dunder 메서드 설계를 실무 관점에서 정리합니다.
---

# Object-Oriented Programming 101 (2/10): 클래스와 인스턴스

객체지향 입문에서 가장 흔한 막힘은 클래스와 인스턴스를 문장으로는 아는데, 설계로는 연결되지 않는 순간입니다. 생성자에 무엇을 넣어야 하는지, 어떤 함수는 인스턴스 메서드여야 하고 어떤 함수는 클래스 메서드나 정적 메서드여야 하는지 감이 잘 오지 않습니다.

실무에서 좋은 클래스는 화려한 문법보다 책임이 분명합니다. 어떤 데이터가 이 객체의 상태인지, 어떤 동작이 이 상태를 바꾸는지, 객체를 출력하거나 비교할 때 Python이 어떤 규약을 기대하는지만 이해해도 클래스 설계의 절반은 정리됩니다.

이 글은 OOP 101 시리즈의 2번째 글입니다.

## 먼저 던지는 질문

- 생성자(`__init__`)는 어디까지 책임져야 하고, 어디서부터 과해질까요?
- 인스턴스 메서드, 클래스 메서드, 정적 메서드는 어떤 기준으로 나눠야 할까요?
- Python의 dunder 메서드는 왜 디버깅과 비교 연산에 중요할까요?

## 큰 그림

![Object-Oriented Programming 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/02/02-01-big-picture.ko.png)

*Object-Oriented Programming 101 2장 흐름 개요*

## 핵심 개념 잡기

> 클래스의 구성 요소

```text
Class
├── class variable
├── __init__()       → instance initialization
├── instance method  → self as first arg
├── @classmethod     → cls as first arg
├── @staticmethod    → no self/cls
└── dunder methods   → __repr__, __str__, __eq__, ...
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 생성자(`__init__`) | 인스턴스 생성 시 자동 호출되는 초기화 메서드입니다 |
| 인스턴스 메서드 | `self`를 첫 번째 매개변수로 받아 인스턴스 데이터에 접근합니다 |
| 클래스 메서드(`@classmethod`) | `cls`를 첫 번째 매개변수로 받아 클래스 수준에서 동작합니다 |
| 정적 메서드(`@staticmethod`) | 인스턴스나 클래스에 의존하지 않는 유틸리티 함수입니다 |
| 특수 메서드(dunder method) | `__`로 시작하고 끝나는 Python 내장 프로토콜 메서드입니다 |

## 전후 비교

객체 비교와 출력을 개선합니다.

```python
# before: no dunder methods — unhelpful output and comparison
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1)        # <__main__.Point object at 0x...>
print(p1 == p2)  # False — same coordinates but considered different
```

```python
# after: dunder methods — intuitive output and comparison
class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1)        # Point(1, 2)
print(p1 == p2)  # True
```

## 단계별 실습

### 1단계: 생성자 패턴

```python
class Product:
    """Product class — validation in the constructor"""

    def __init__(self, name: str, price: int, quantity: int = 0) -> None:
        if price < 0:
            raise ValueError(f"Price cannot be negative: {price}")
        self.name = name
        self.price = price
        self.quantity = quantity

    def total_value(self) -> int:
        return self.price * self.quantity

    def __repr__(self) -> str:
        return f"Product({self.name!r}, {self.price}, {self.quantity})"

p = Product("Keyboard", 50000, 3)
print(p.total_value())  # 150000
print(p)                # Product('Keyboard', 50000, 3)
```

### 2단계: 클래스 메서드로 대안 생성자 만들기

```python
class Date:
    def __init__(self, year: int, month: int, day: int) -> None:
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def from_string(cls, date_str: str) -> "Date":
        """Create Date from 'YYYY-MM-DD' string"""
        year, month, day = map(int, date_str.split("-"))
        return cls(year, month, day)

    @classmethod
    def today(cls) -> "Date":
        """Create Date from today's date"""
        from datetime import date
        d = date.today()
        return cls(d.year, d.month, d.day)

    def __repr__(self) -> str:
        return f"Date({self.year}, {self.month}, {self.day})"

d1 = Date(2026, 5, 4)
d2 = Date.from_string("2026-05-04")
print(d1)  # Date(2026, 5, 4)
print(d2)  # Date(2026, 5, 4)
```

### 3단계: 정적 메서드

```python
class MathUtils:
    @staticmethod
    def is_even(n: int) -> bool:
        return n % 2 == 0

    @staticmethod
    def factorial(n: int) -> int:
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

print(MathUtils.is_even(4))     # True
print(MathUtils.factorial(5))   # 120
```

### 4단계: 특수 메서드 활용

```python
class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)

    def __abs__(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"

v1 = Vector(3, 4)
v2 = Vector(1, 2)
print(v1 + v2)    # Vector(4, 6)
print(v1 * 2)     # Vector(6, 8)
print(abs(v1))    # 5.0
```

### 5단계: __slots__로 메모리 최적화

```python
class RegularPoint:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

class OptimizedPoint:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

import sys

rp = RegularPoint(1, 2)
op = OptimizedPoint(1, 2)
print(sys.getsizeof(rp.__dict__))  # size of regular instance __dict__
# OptimizedPoint has no __dict__ → saves memory
```

## 이 코드에서 주목할 점

- `@classmethod`는 대안 생성자(팩토리 메서드) 패턴에서 주로 사용합니다
- `@staticmethod`는 클래스와 논리적으로 관련되지만 인스턴스 데이터가 필요 없는 유틸리티입니다
- `__eq__`에서 `isinstance` 검사와 `NotImplemented` 반환은 타입 안전한 비교의 관례입니다
- `__slots__`는 인스턴스가 대량 생성될 때 메모리를 절약합니다

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `__init__`에서 반환값 사용 | `__init__`은 `None`만 반환해야 합니다 | 초기화 로직만 작성하고 `return`은 생략합니다 |
| `@classmethod`와 `@staticmethod` 혼동 | 클래스 데이터 접근 여부가 다릅니다 | `cls` 필요 시 `@classmethod`, 아닐 시 `@staticmethod`입니다 |
| `__eq__` 정의 시 `__hash__` 미정의 | `dict` 키나 `set` 원소로 사용 불가합니다 | `__eq__`를 정의하면 `__hash__`도 함께 정의합니다 |
| 모든 메서드를 `@staticmethod`로 만듦 | 클래스를 쓸 이유가 없어집니다 | 인스턴스 데이터를 다루면 인스턴스 메서드를 사용합니다 |
| 가변 기본값을 매개변수에 사용 | 모든 호출이 같은 객체를 공유합니다 | `None`을 기본값으로 쓰고 함수 내부에서 생성합니다 |

## 실무에서 이렇게 쓰입니다

- Django ORM의 `Model.objects.create()`는 클래스 메서드 기반 팩토리입니다
- dataclasses와 Pydantic은 `__init__`, `__repr__`, `__eq__`를 자동 생성합니다
- `__slots__`는 대량 데이터 객체(수백만 건) 처리에서 메모리를 절약합니다
- FastAPI의 의존성 주입에서 클래스를 callable로 활용합니다
- 테스트에서 `__eq__`를 정의하면 `assert actual == expected`로 비교합니다

## 현업 개발자는 이렇게 생각합니다

클래스를 설계할 때 가장 중요한 원칙은 "하나의 클래스는 하나의 책임"입니다. 클래스가 너무 많은 일을 하면 테스트하기 어렵고 변경에 취약해집니다.

Python 3.7 이후에는 `dataclasses`를 먼저 고려합니다. 보일러플레이트 코드를 줄이면서도 필요하면 커스텀 메서드를 추가할 수 있어 대부분의 데이터 중심 클래스에 적합합니다.

## 체크리스트

- [ ] 생성자에서 유효성 검증을 수행할 수 있다
- [ ] `@classmethod`로 대안 생성자를 만들 수 있다
- [ ] `@staticmethod`의 적절한 사용 시점을 판단할 수 있다
- [ ] `__repr__`, `__eq__` 등 특수 메서드를 구현할 수 있다
- [ ] `__slots__`의 목적과 제약을 이해한다

## 정리 및 다음 글 안내

클래스는 생성자, 인스턴스 메서드, 클래스 메서드, 정적 메서드, 특수 메서드로 구성됩니다. 각 구성 요소의 역할을 이해하면 깔끔하고 Pythonic한 클래스를 설계할 수 있습니다. 다음 글에서는 캡슐화를 통해 클래스의 내부 구현을 보호하는 방법을 알아봅니다.

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

- **생성자(`__init__`)는 어디까지 책임져야 하고, 어디서부터 과해질까요?**
  - 본문의 기준은 클래스와 인스턴스를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **인스턴스 메서드, 클래스 메서드, 정적 메서드는 어떤 기준으로 나눠야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Python의 dunder 메서드는 왜 디버깅과 비교 연산에 중요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- **클래스와 인스턴스 (현재 글)**
- 캡슐화 (예정)
- 상속 (예정)
- 다형성 (예정)
- 추상화 (예정)
- 합성과 상속 (예정)
- SOLID 원칙 기초 (예정)
- 객체지향 설계 예제 (예정)
- 객체지향을 언제 피해야 할까? (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Data Model](https://docs.python.org/3/reference/datamodel.html)
- [Real Python — Python Classes](https://realpython.com/python3-object-oriented-programming/)
- [Fluent Python — Luciano Ramalho](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Python dataclasses 공식 문서](https://docs.python.org/3/library/dataclasses.html)

Tags: Python, OOP, 클래스, 인스턴스, 생성자

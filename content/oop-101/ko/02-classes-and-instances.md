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

![Object-Oriented Programming 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/02/02-01-big-picture.ko.png)
*Object-Oriented Programming 101 2장 흐름 개요*

## 이 글에서 다룰 문제

- 생성자(`__init__`)는 어디까지 책임져야 하고, 어디서부터 과해질까요?
- 인스턴스 메서드, 클래스 메서드, 정적 메서드는 어떤 기준으로 나눠야 할까요?
- Python의 dunder 메서드는 왜 디버깅과 비교 연산에 중요할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 이 글에서 배울 것

- `__init__`의 역할과 생성자에서의 유효성 검증 패턴을 익힙니다
- `@classmethod`로 대안 생성자(팩토리 메서드)를 만드는 법을 배웁니다
- `@staticmethod`를 적절하게 사용하는 기준을 세웁니다
- `__repr__`, `__eq__`, `__hash__` 등 dunder 메서드의 역할을 이해합니다
- `__slots__`로 메모리를 최적화하는 방법을 확인합니다

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
# before: dunder method 없음 — 출력/비교가 불편함
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
# after: dunder methods — 출력/비교가 직관적임
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

    def __hash__(self) -> int:
        return hash((self.x, self.y))

p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1)        # Point(1, 2)
print(p1 == p2)  # True
print({p1, p2})  # {Point(1, 2)} — 중복 제거 동작
```

`__eq__`를 정의하면 Python은 자동으로 `__hash__`를 `None`으로 설정합니다. `set`이나 `dict` 키로 사용하려면 반드시 `__hash__`도 함께 정의해야 합니다.

## 단계별 실습

### 1단계: 생성자에서 유효성 검증

```python
class Product:
    """Product class — validation in the constructor"""

    def __init__(self, name: str, price: int, quantity: int = 0) -> None:
        if not name.strip():
            raise ValueError("Product name cannot be empty")
        if price < 0:
            raise ValueError(f"Price cannot be negative: {price}")
        if quantity < 0:
            raise ValueError(f"Quantity cannot be negative: {quantity}")
        self.name = name.strip()
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

생성자에서 검증하면 잘못된 상태의 인스턴스가 만들어지지 않습니다. 검증을 메서드로 분리하면 인스턴스가 이미 생성된 후에야 오류를 알게 됩니다.

### 2단계: @classmethod로 대안 생성자 만들기

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return (self.year, self.month, self.day) == (other.year, other.month, other.day)

d1 = Date(2026, 5, 4)
d2 = Date.from_string("2026-05-04")
print(d1)        # Date(2026, 5, 4)
print(d2)        # Date(2026, 5, 4)
print(d1 == d2)  # True
```

`@classmethod`를 팩토리 메서드로 활용하면 생성 방식을 여러 개 제공하면서도 기본 생성자를 단순하게 유지할 수 있습니다.

### 3단계: @staticmethod로 유틸리티 함수 정리

```python
class PasswordValidator:
    MIN_LENGTH = 8

    @staticmethod
    def has_uppercase(password: str) -> bool:
        return any(c.isupper() for c in password)

    @staticmethod
    def has_digit(password: str) -> bool:
        return any(c.isdigit() for c in password)

    @classmethod
    def is_valid(cls, password: str) -> bool:
        return (
            len(password) >= cls.MIN_LENGTH
            and cls.has_uppercase(password)
            and cls.has_digit(password)
        )

print(PasswordValidator.is_valid("SecurePass1"))  # True
print(PasswordValidator.is_valid("weakpass"))     # False
```

`@staticmethod`는 클래스와 논리적으로 관련되지만 인스턴스 데이터(`self`)나 클래스 데이터(`cls`)가 필요 없는 함수에 사용합니다.

### 4단계: 특수 메서드로 수치 연산 지원

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

v1 = Vector(3, 4)
v2 = Vector(1, 2)
print(v1 + v2)    # Vector(4, 6)
print(v1 * 2)     # Vector(6, 8)
print(abs(v1))    # 5.0
```

dunder 메서드를 정의하면 Python 내장 연산자(+, *, abs)와 자연스럽게 통합됩니다.

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
# OptimizedPoint는 __dict__ 없이 슬롯만 사용하여 메모리를 절약합니다.
# 수백만 개의 인스턴스를 생성할 때 효과가 명확합니다.
print(hasattr(rp, "__dict__"))  # True
print(hasattr(op, "__dict__"))  # False
```

`__slots__`는 인스턴스가 대량 생성될 때(수십만~수백만 건) 유효합니다. 일반적인 경우에는 가독성을 위해 사용하지 않아도 됩니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `__init__`에서 값을 반환(return) | `__init__`은 `None`만 반환해야 합니다 | 초기화 로직만 작성하고 `return`을 쓰지 않습니다 |
| `@classmethod`와 `@staticmethod` 혼동 | 클래스 데이터 접근 여부가 다릅니다 | `cls` 필요 시 `@classmethod`, 아닐 시 `@staticmethod`입니다 |
| `__eq__` 정의 시 `__hash__` 미정의 | `dict` 키나 `set` 원소로 사용 불가합니다 | `__eq__`를 정의하면 `__hash__`도 함께 정의합니다 |
| 모든 메서드를 `@staticmethod`로 만듦 | 클래스를 쓸 이유가 없어집니다 | 인스턴스 데이터를 다루면 인스턴스 메서드를 사용합니다 |
| 가변 기본값을 매개변수에 사용 | 모든 호출이 같은 객체를 공유합니다 | `None`을 기본값으로 쓰고 함수 내부에서 생성합니다 |

## 실무에서 이렇게 쓰입니다

```python
from dataclasses import dataclass, field
from typing import ClassVar

@dataclass
class OrderLine:
    """dataclass는 __init__, __repr__, __eq__를 자동 생성합니다"""
    product_id: str
    quantity: int
    unit_price: int

    # ClassVar: 인스턴스 변수가 아닌 클래스 변수
    TAX_RATE: ClassVar[float] = 0.1

    def subtotal(self) -> int:
        return self.quantity * self.unit_price

    def subtotal_with_tax(self) -> int:
        return int(self.subtotal() * (1 + self.TAX_RATE))

    @classmethod
    def from_dict(cls, data: dict) -> "OrderLine":
        return cls(
            product_id=data["product_id"],
            quantity=data["quantity"],
            unit_price=data["unit_price"],
        )

line = OrderLine.from_dict({"product_id": "P001", "quantity": 2, "unit_price": 15000})
print(line)                      # OrderLine(product_id='P001', quantity=2, unit_price=15000)
print(line.subtotal())           # 30000
print(line.subtotal_with_tax())  # 33000
```

Python 3.7 이후에는 `dataclasses`를 먼저 고려합니다. 보일러플레이트 코드를 줄이면서도 필요하면 커스텀 메서드를 추가할 수 있습니다.

## 현업 개발자는 이렇게 생각합니다

클래스를 설계할 때 가장 중요한 원칙은 "하나의 클래스는 하나의 책임"입니다. 클래스가 너무 많은 일을 하면 테스트하기 어렵고 변경에 취약해집니다.

인스턴스 생성 시점에 불변식이 성립해야 합니다. 생성자에서 검증을 건너뛰고 나중에 `validate()` 메서드를 호출하는 패턴은 검증을 잊기 쉽습니다. "잘못된 상태의 객체가 존재할 수 없다"를 목표로 설계합니다.

## 운영 체크리스트

- [ ] 생성자에서 유효성 검증을 수행할 수 있다
- [ ] `@classmethod`로 대안 생성자를 만들 수 있다
- [ ] `@staticmethod`의 적절한 사용 시점을 판단할 수 있다
- [ ] `__repr__`, `__eq__`, `__hash__` 등 특수 메서드를 구현할 수 있다
- [ ] `__slots__`의 목적과 제약을 이해한다

## 연습 문제

1. `Temperature` 클래스를 만드세요. 섭씨로 초기화하고, `@classmethod`로 화씨와 켈빈에서 생성하는 팩토리 메서드를 추가합니다.
2. `Fraction` 클래스를 구현하세요. `__add__`, `__mul__`, `__eq__`, `__repr__`을 정의하고 분수 연산이 동작하게 만듭니다.
3. 100만 개의 좌표 포인트를 처리하는 시뮬레이션에서 `__slots__`의 메모리 절약 효과를 측정해 보세요.

## 정리 및 다음 단계

클래스는 생성자, 인스턴스 메서드, 클래스 메서드, 정적 메서드, 특수 메서드로 구성됩니다. 각 구성 요소의 역할을 이해하면 깔끔하고 Pythonic한 클래스를 설계할 수 있습니다.

다음 글에서는 캡슐화를 통해 클래스의 내부 구현을 보호하는 방법을 알아봅니다. `property` 데코레이터와 Python의 접근 제어 관례를 실무 예제로 정리합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- **Object-Oriented Programming 101 (2/10): 클래스와 인스턴스 (현재 글)**
- [Object-Oriented Programming 101 (3/10): 캡슐화](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): 상속](./04-inheritance.md)
- [Object-Oriented Programming 101 (5/10): 다형성](./05-polymorphism.md)
- [Object-Oriented Programming 101 (6/10): 추상화](./06-abstraction.md)
- [Object-Oriented Programming 101 (7/10): 합성과 상속](./07-composition-vs-inheritance.md)
- [Object-Oriented Programming 101 (8/10): SOLID 원칙 기초](./08-solid-principles.md)
- [Object-Oriented Programming 101 (9/10): 객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Data Model](https://docs.python.org/3/reference/datamodel.html)
- [Real Python — Python Classes](https://realpython.com/python3-object-oriented-programming/)
- [Fluent Python — Luciano Ramalho](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Python dataclasses 공식 문서](https://docs.python.org/3/library/dataclasses.html)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 클래스, 인스턴스, 생성자

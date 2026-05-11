---
series: oop-101
episode: 2
title: 클래스와 인스턴스
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - OOP
  - 클래스
  - 인스턴스
  - 생성자
seo_description: Python 클래스의 생성자, 인스턴스 메서드, 특수 메서드를 다룹니다.
last_reviewed: '2026-05-11'
---

# 클래스와 인스턴스

> Object-Oriented Programming 101 시리즈 (2/10)


## 이 글에서 다룰 문제

클래스를 만드는 것 자체는 어렵지 않습니다. 어려운 것은 "어떤 데이터를 속성으로, 어떤 동작을 메서드로 설계할 것인가"입니다. 좋은 클래스 설계는 코드 재사용성과 가독성을 동시에 높입니다.

> 좋은 클래스 = 명확한 책임 + 적절한 인터페이스 + 내부 구현 은닉

Python의 특수 메서드(매직 메서드)를 활용하면 클래스를 Python의 내장 문법과 자연스럽게 통합할 수 있습니다. `print()`, `==`, `len()`, `for` 루프 등에서 사용자 정의 객체가 매끄럽게 동작합니다.

## 핵심 개념 잡기

> 클래스의 구성 요소

```text
클래스 (Class)
├── 클래스 변수 (class variable)
├── __init__()       → 인스턴스 초기화
├── 인스턴스 메서드   → self를 첫 인자로
├── @classmethod     → cls를 첫 인자로
├── @staticmethod    → self/cls 없음
└── 특수 메서드       → __repr__, __str__, __eq__, ...
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 생성자(`__init__`) | 인스턴스 생성 시 자동 호출되는 초기화 메서드입니다 |
| 인스턴스 메서드 | `self`를 첫 번째 매개변수로 받아 인스턴스 데이터에 접근합니다 |
| 클래스 메서드(`@classmethod`) | `cls`를 첫 번째 매개변수로 받아 클래스 수준에서 동작합니다 |
| 정적 메서드(`@staticmethod`) | 인스턴스나 클래스에 의존하지 않는 유틸리티 함수입니다 |
| 특수 메서드(dunder method) | `__`로 시작하고 끝나는 Python 내장 프로토콜 메서드입니다 |

## Before / After

객체 비교와 출력을 개선합니다.

```python
# before: 특수 메서드 없이 — 불편한 출력과 비교
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1)        # <__main__.Point object at 0x...>
print(p1 == p2)  # False — 같은 좌표인데 다르다고 판단
```

```python
# after: 특수 메서드 활용 — 직관적인 출력과 비교
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

### Step 1: 생성자 패턴

```python
class Product:
    """상품 클래스 — 생성자에서 유효성 검증"""

    def __init__(self, name: str, price: int, quantity: int = 0) -> None:
        if price < 0:
            raise ValueError(f"가격은 음수일 수 없습니다: {price}")
        self.name = name
        self.price = price
        self.quantity = quantity

    def total_value(self) -> int:
        return self.price * self.quantity

    def __repr__(self) -> str:
        return f"Product({self.name!r}, {self.price}, {self.quantity})"

p = Product("키보드", 50000, 3)
print(p.total_value())  # 150000
print(p)                # Product('키보드', 50000, 3)
```

### Step 2: 클래스 메서드로 대안 생성자 만들기

```python
class Date:
    def __init__(self, year: int, month: int, day: int) -> None:
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def from_string(cls, date_str: str) -> "Date":
        """'YYYY-MM-DD' 형식 문자열에서 Date 생성"""
        year, month, day = map(int, date_str.split("-"))
        return cls(year, month, day)

    @classmethod
    def today(cls) -> "Date":
        """오늘 날짜로 Date 생성"""
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

### Step 3: 정적 메서드

```python
class MathUtils:
    @staticmethod
    def is_even(n: int) -> bool:
        return n % 2 == 0

    @staticmethod
    def factorial(n: int) -> int:
        if n < 0:
            raise ValueError("음수의 팩토리얼은 정의되지 않습니다")
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

print(MathUtils.is_even(4))     # True
print(MathUtils.factorial(5))   # 120
```

### Step 4: 특수 메서드 활용

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

### Step 5: __slots__로 메모리 최적화

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
print(sys.getsizeof(rp.__dict__))  # 일반 인스턴스의 __dict__ 크기
# OptimizedPoint에는 __dict__가 없음 → 메모리 절약
```

## 이 코드에서 주목할 점

- `@classmethod`는 대안 생성자(팩토리 메서드) 패턴에서 주로 사용합니다
- `@staticmethod`는 클래스와 논리적으로 관련되지만 인스턴스 데이터가 필요 없는 유틸리티입니다
- `__eq__`에서 `isinstance` 검사와 `NotImplemented` 반환은 타입 안전한 비교의 관례입니다
- `__slots__`는 인스턴스가 대량 생성될 때 메모리를 절약합니다

## 흔한 실수 5가지

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

<!-- toc:begin -->
- [객체지향이란 무엇인가?](./01-what-is-oop.md)
- **클래스와 인스턴스 (현재 글)**
- [캡슐화](./03-encapsulation.md)
- [상속](./04-inheritance.md)
- [다형성](./05-polymorphism.md)
- [추상화](./06-abstraction.md)
- [합성과 상속](./07-composition-vs-inheritance.md)
- [SOLID 원칙 기초](./08-solid-principles.md)
- [객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Data Model](https://docs.python.org/3/reference/datamodel.html)
- [Real Python — Python Classes](https://realpython.com/python3-object-oriented-programming/)
- [Fluent Python — Luciano Ramalho](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Python dataclasses 공식 문서](https://docs.python.org/3/library/dataclasses.html)

Tags: Python, OOP, 클래스, 인스턴스, 생성자

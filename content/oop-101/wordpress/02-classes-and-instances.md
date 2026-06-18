---
title: "바이브코딩을 위한 객체지향 기초 (2/10): 클래스와 인스턴스"
series: oop-101
episode: 2
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - Python
  - OOP
  - 클래스
  - 인스턴스
  - 바이브코딩
  - 생성자
last_reviewed: '2026-06-18'
seo_description: 바이브코딩에서 AI가 만들어주는 생성자, 클래스 메서드, dunder 메서드 패턴을 이해하고 직접 읽을 수 있도록 설명합니다.
---

# 바이브코딩을 위한 객체지향 기초 (2/10): 클래스와 인스턴스

이 글은 **바이브코딩을 위한 객체지향 기초** 시리즈의 두 번째 글입니다.

---

AI에게 날짜 처리 유틸리티를 만들어 달라고 하면 `Date.from_string("2026-06-18")`처럼 생겨먹은 코드가 나옵니다. 또 어떤 클래스에는 `@classmethod`가 붙고, 어떤 메서드에는 `@staticmethod`가 붙습니다. `__repr__`, `__eq__` 같은 더블 언더바 메서드도 심심치 않게 보입니다.

AI가 이렇게 짠 이유가 있습니다. 생성자에 무엇을 넣는지, 어떤 함수는 인스턴스 메서드여야 하고 어떤 함수는 클래스 메서드여야 하는지, 그 기준을 알면 AI 코드를 그냥 실행하는 것에서 나아가 이해하고 수정할 수 있습니다.

AI가 클래스 계층을 만들어줬는데 왜 이렇게 짰는지 이해하려면 OOP를 알아야 합니다. 이번 글에서는 클래스의 구성 요소를 하나씩 살펴봅니다.

> "AI가 만들어준 `@classmethod`를 보고 '이게 뭐지?' 하면 그냥 지나치지 마세요. 설계 의도가 담겨 있습니다."

## 이 글에서 다룰 문제

- 생성자(`__init__`)는 어디까지 책임져야 하고, 어디서부터 과해질까요?
- 인스턴스 메서드, 클래스 메서드, 정적 메서드는 어떤 기준으로 나눠야 할까요?
- Python의 dunder 메서드는 왜 디버깅과 비교 연산에 중요할까요?
- AI가 생성한 클래스에서 이 패턴들을 어떻게 식별할 수 있을까요?
- 잘못 이해하면 어떤 버그가 생길까요?

## 핵심 개념 잡기

클래스의 구성 요소를 한눈에 정리하면 다음과 같습니다.

```text
Class
├── class variable        # 모든 인스턴스가 공유
├── __init__()            # 인스턴스 초기화
├── instance method       # self를 첫 번째 인자로 받음
├── @classmethod          # cls를 첫 번째 인자로 받음
├── @staticmethod         # self나 cls 없음
└── dunder methods        # __repr__, __str__, __eq__, ...
```

| 용어 | 설명 |
|------|------|
| 생성자(`__init__`) | 인스턴스 생성 시 자동 호출되는 초기화 메서드입니다 |
| 인스턴스 메서드 | `self`를 첫 번째 매개변수로 받아 인스턴스 데이터에 접근합니다 |
| 클래스 메서드(`@classmethod`) | `cls`를 첫 번째 매개변수로 받아 클래스 수준에서 동작합니다 |
| 정적 메서드(`@staticmethod`) | 인스턴스나 클래스에 의존하지 않는 유틸리티 함수입니다 |
| dunder 메서드 | `__`로 시작하고 끝나는 Python 내장 프로토콜 메서드입니다 |

## Before / After: AI가 dunder 메서드를 추가하는 이유

AI가 클래스를 만들 때 `__repr__`과 `__eq__`를 자동으로 추가하는 경우가 많습니다. 왜 그런지 비교해 봅니다.

```python
# Before: dunder method 없음 — 출력/비교가 불편함
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1)        # <__main__.Point object at 0x...>  <- 쓸모 없음
print(p1 == p2)  # False  <- 같은 좌표인데도 다르다고 나옴
```

```python
# After: dunder methods 추가 — 출력/비교가 직관적임
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
print(p1)        # Point(1, 2)  <- 읽을 수 있음
print(p1 == p2)  # True  <- 의미 있는 비교
```

## 바이브코딩 관점: `@classmethod`는 왜 생기는가?

AI가 `Date.from_string("2026-06-18")`처럼 생긴 메서드를 만들 때, 그것은 **대안 생성자** 패턴입니다. `__init__`만으로 모든 입력 형식을 처리하기 어려울 때 AI는 `@classmethod`로 팩토리 메서드를 추가합니다.

```python
class Date:
    def __init__(self, year: int, month: int, day: int) -> None:
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def from_string(cls, date_str: str) -> "Date":
        """'YYYY-MM-DD' 문자열에서 Date 생성"""
        year, month, day = map(int, date_str.split("-"))
        return cls(year, month, day)  # cls는 Date 클래스 자체

    def __repr__(self) -> str:
        return f"Date({self.year}, {self.month}, {self.day})"

# AI가 이 패턴을 만드는 이유: 다양한 입력 형식을 지원하기 위해
d1 = Date(2026, 6, 18)
d2 = Date.from_string("2026-06-18")
print(d1)  # Date(2026, 6, 18)
print(d2)  # Date(2026, 6, 18)
```

`cls`는 `self`와 비슷하지만 인스턴스가 아닌 **클래스 자체**를 가리킵니다. `cls(year, month, day)`는 `Date(year, month, day)`와 같습니다. 이렇게 하면 나중에 `Date`를 상속해도 올바른 클래스가 생성됩니다.

## `@staticmethod`는 언제 나타나는가?

```python
class MathUtils:
    @staticmethod
    def is_even(n: int) -> bool:
        return n % 2 == 0  # self나 cls 없이도 동작하는 유틸리티

    @staticmethod
    def factorial(n: int) -> int:
        if n < 0:
            raise ValueError("음수의 팩토리얼은 정의되지 않습니다")
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

print(MathUtils.is_even(4))    # True
print(MathUtils.factorial(5))  # 120
```

`@staticmethod`는 클래스와 논리적으로 관련 있지만 인스턴스 데이터가 전혀 필요 없는 유틸리티 함수에 씁니다. AI가 이 데코레이터를 붙인다면 "이 메서드는 인스턴스 상태를 쓰지 않는다"는 신호입니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `__init__`에서 반환값 사용 | `__init__`은 `None`만 반환해야 합니다 | 초기화 로직만 작성하고 `return`은 생략합니다 |
| `@classmethod`와 `@staticmethod` 혼동 | 클래스 데이터 접근 여부가 다릅니다 | `cls` 필요 시 `@classmethod`, 아닐 시 `@staticmethod`입니다 |
| `__eq__` 정의 시 `__hash__` 미정의 | `dict` 키나 `set` 원소로 사용 불가합니다 | `__eq__`를 정의하면 `__hash__`도 함께 정의합니다 |
| 모든 메서드를 `@staticmethod`로 만듦 | 클래스를 쓸 이유가 없어집니다 | 인스턴스 데이터를 다루면 인스턴스 메서드를 사용합니다 |
| 가변 기본값을 매개변수에 사용 | 모든 호출이 같은 객체를 공유합니다 | `None`을 기본값으로 쓰고 함수 내부에서 생성합니다 |

## AI 팁: AI가 만든 클래스를 분석하는 법

AI가 생성한 클래스를 마주쳤을 때 이렇게 접근하세요.

```python
# 이런 클래스를 봤을 때 분석 순서:
class Product:
    def __init__(self, name: str, price: int, quantity: int = 0) -> None:
        if price < 0:
            raise ValueError(f"가격은 음수일 수 없습니다: {price}")
        self.name = name
        self.price = price
        self.quantity = quantity

    def total_value(self) -> int:
        return self.price * self.quantity  # 인스턴스 메서드: self 데이터 사용

    def __repr__(self) -> str:
        return f"Product({self.name!r}, {self.price}, {self.quantity})"

# 분석 포인트:
# 1. __init__: 어떤 데이터를 초기화하고, 어떤 검증을 하는가?
# 2. 인스턴스 메서드: self 데이터를 어떻게 활용하는가?
# 3. __repr__: 디버깅 시 어떻게 보이는가?
```

AI에게 "이 클래스의 각 메서드가 하는 역할을 한 줄씩 설명해 줘"라고 하면 빠르게 파악할 수 있습니다.

## 체크리스트

- [ ] 생성자에서 유효성 검증을 수행할 수 있다
- [ ] `@classmethod`로 대안 생성자를 만들 수 있다
- [ ] `@staticmethod`의 적절한 사용 시점을 판단할 수 있다
- [ ] `__repr__`, `__eq__` 등 특수 메서드를 구현할 수 있다
- [ ] AI가 생성한 클래스에서 각 메서드의 종류를 식별할 수 있다

## 처음 질문으로 돌아가기

- **생성자는 어디까지 책임져야 할까요?**
  생성자는 인스턴스가 유효한 상태로 만들어지는 것만 책임져야 합니다. 입력 검증, 초기값 설정까지는 괜찮습니다. 데이터베이스 연결, 파일 읽기 같은 부수 효과는 다른 메서드로 분리합니다.

- **`@classmethod`와 `@staticmethod`는 어떻게 구분할까요?**
  `cls`로 클래스 자체나 다른 클래스 변수에 접근해야 하면 `@classmethod`, 그냥 관련 유틸리티 함수라면 `@staticmethod`입니다. AI가 `from_string`, `from_dict`, `from_json` 같은 이름을 붙인다면 대부분 `@classmethod`입니다.

- **dunder 메서드는 왜 중요한가요?**
  `__repr__`은 디버깅할 때 객체를 읽을 수 있게 해줍니다. `__eq__`는 의미 있는 비교를 가능하게 합니다. AI가 자동으로 추가하는 이유는 이 메서드들이 없으면 클래스를 실용적으로 쓰기 어렵기 때문입니다.

## 정리

클래스는 생성자, 인스턴스 메서드, 클래스 메서드, 정적 메서드, 특수 메서드로 구성됩니다. AI가 각 종류를 만드는 데는 이유가 있습니다. `@classmethod`는 대안 생성자, `@staticmethod`는 인스턴스 데이터 불필요한 유틸리티, dunder 메서드는 Python 프로토콜 통합입니다. 다음 글에서는 캡슐화를 통해 클래스 내부 상태를 보호하는 방법을 알아봅니다.

## 참고 자료

- [Python 공식 문서 — Data Model](https://docs.python.org/3/reference/datamodel.html)
- [Real Python — Python Classes](https://realpython.com/python3-object-oriented-programming/)
- [Python dataclasses 공식 문서](https://docs.python.org/3/library/dataclasses.html)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 객체지향 기초 (1/10): 객체지향이란 무엇인가?
- **바이브코딩을 위한 객체지향 기초 (2/10): 클래스와 인스턴스 (현재 글)**
- 바이브코딩을 위한 객체지향 기초 (3/10): 캡슐화
- 바이브코딩을 위한 객체지향 기초 (4/10): 상속
- 바이브코딩을 위한 객체지향 기초 (5/10): 다형성
- 바이브코딩을 위한 객체지향 기초 (6/10): 추상화
- 바이브코딩을 위한 객체지향 기초 (7/10): 합성과 상속
- 바이브코딩을 위한 객체지향 기초 (8/10): SOLID 원칙 기초
- 바이브코딩을 위한 객체지향 기초 (9/10): 객체지향 설계 예제
- 바이브코딩을 위한 객체지향 기초 (10/10): 객체지향을 언제 피해야 할까?

<!-- toc:end -->

Tags: Python, OOP, 클래스, 인스턴스, 바이브코딩, 생성자

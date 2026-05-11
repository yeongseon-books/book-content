---
series: oop-101
episode: 5
title: 다형성
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
  - 다형성
  - 덕 타이핑
  - 프로토콜
seo_description: Python에서 다형성을 구현하는 방법과 덕 타이핑, 프로토콜을 다룹니다.
last_reviewed: '2026-05-11'
---

# 다형성

> Object-Oriented Programming 101 시리즈 (5/10)


## 이 글에서 다룰 문제

결제 시스템에서 신용카드, 은행 이체, 전자지갑을 처리한다고 가정합니다. 각 결제 수단의 내부 로직은 다르지만, 호출하는 쪽에서는 `pay(amount)` 하나로 통일하고 싶습니다. 다형성이 이 문제를 해결합니다.

> 다형성 = 같은 인터페이스, 다른 구현

다형성이 없으면 `if isinstance(payment, CreditCard): ...` 같은 분기문이 결제 수단이 추가될 때마다 늘어납니다. 다형성을 활용하면 새 결제 수단을 추가해도 기존 코드를 수정할 필요가 없습니다.

## 핵심 개념 잡기

> Python에서 다형성의 세 가지 방식

```text
1. 상속 기반 다형성
   Animal → Dog.speak(), Cat.speak()

2. 덕 타이핑 (Duck Typing)
   "quack() 메서드가 있으면 오리다"
   상속 관계 없이 같은 메서드만 있으면 됨

3. 프로토콜 (Protocol) — Python 3.8+
   구조적 서브타이핑: 타입 힌트로 덕 타이핑 검증
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 다형성(polymorphism) | 같은 인터페이스가 타입에 따라 다르게 동작하는 것입니다 |
| 덕 타이핑(duck typing) | 객체의 타입이 아니라 메서드의 존재 여부로 판단합니다 |
| 프로토콜(Protocol) | 구조적 서브타이핑을 지원하는 typing 모듈의 클래스입니다 |
| 디스패치(dispatch) | 호출 시점에 실제 타입의 메서드를 선택하는 메커니즘입니다 |
| 인터페이스(interface) | 객체가 제공해야 하는 메서드의 집합입니다 |

## Before / After

결제 처리를 비교합니다.

```python
# before: 타입별 분기 — 결제 수단 추가마다 수정 필요
def process_payment(payment, amount):
    if payment["type"] == "credit_card":
        print(f"신용카드 결제: {amount}원")
    elif payment["type"] == "bank_transfer":
        print(f"계좌이체: {amount}원")
    # 새 결제 수단 추가 → elif 추가 필요
```

```python
# after: 다형성 — 새 결제 수단 추가 시 기존 코드 수정 불필요
class CreditCard:
    def pay(self, amount: int) -> str:
        return f"신용카드 결제: {amount}원"

class BankTransfer:
    def pay(self, amount: int) -> str:
        return f"계좌이체: {amount}원"

def process_payment(payment, amount: int) -> None:
    print(payment.pay(amount))  # 어떤 타입이든 pay()만 있으면 됨
```

## 단계별 실습

### Step 1: 상속 기반 다형성

```python
class Shape:
    def area(self) -> float:
        raise NotImplementedError

    def describe(self) -> str:
        return f"{type(self).__name__}: 넓이 = {self.area():.2f}"

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
# Circle: 넓이 = 78.54
# Rectangle: 넓이 = 24.00
# Triangle: 넓이 = 12.00
```

### Step 2: 덕 타이핑

```python
class FileWriter:
    def write(self, data: str) -> None:
        print(f"파일에 저장: {data}")

class DatabaseWriter:
    def write(self, data: str) -> None:
        print(f"DB에 저장: {data}")

class ApiWriter:
    def write(self, data: str) -> None:
        print(f"API로 전송: {data}")

def save_data(writer, data: str) -> None:
    """writer의 타입은 상관없음 — write() 메서드만 있으면 됨"""
    writer.write(data)

save_data(FileWriter(), "hello")       # 파일에 저장: hello
save_data(DatabaseWriter(), "hello")   # DB에 저장: hello
save_data(ApiWriter(), "hello")        # API로 전송: hello
```

### Step 3: Protocol을 사용한 구조적 서브타이핑

```python
from typing import Protocol


class Writable(Protocol):
    def write(self, data: str) -> None: ...


class ConsoleWriter:
    def write(self, data: str) -> None:
        print(f"콘솔 출력: {data}")


class NetworkWriter:
    def write(self, data: str) -> None:
        print(f"네트워크 전송: {data}")


def save_all(writers: list[Writable], data: str) -> None:
    for writer in writers:
        writer.write(data)


writers: list[Writable] = [ConsoleWriter(), NetworkWriter()]
save_all(writers, "중요한 데이터")
# 콘솔 출력: 중요한 데이터
# 네트워크 전송: 중요한 데이터
```

### Step 4: 내장 다형성 활용

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

team = Team("백엔드팀", ["김개발", "이서버", "박디비"])
print(len(team))             # 3
print("김개발" in team)       # True
print(list(team))            # ['김개발', '이서버', '박디비']

for member in team:
    print(member)
```

### Step 5: functools.singledispatch

```python
from functools import singledispatch


@singledispatch
def format_value(value) -> str:
    return str(value)

@format_value.register(int)
def _(value: int) -> str:
    return f"{value:,}원"

@format_value.register(float)
def _(value: float) -> str:
    return f"{value:.2f}"

@format_value.register(list)
def _(value: list) -> str:
    return f"[{len(value)}개 항목]"

print(format_value(1000000))       # 1,000,000원
print(format_value(3.14159))       # 3.14
print(format_value([1, 2, 3]))     # [3개 항목]
print(format_value("hello"))       # hello
```

## 이 코드에서 주목할 점

- Python의 덕 타이핑은 상속 없이도 다형성을 구현합니다
- `Protocol`은 타입 검사기가 덕 타이핑을 검증하게 합니다
- `__len__`, `__contains__`, `__iter__` 등 특수 메서드로 Python 내장 문법과 통합합니다
- `singledispatch`는 인자 타입에 따라 다른 함수를 호출하는 함수 수준 다형성입니다

## 흔한 실수 5가지

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

<!-- toc:begin -->
- [객체지향이란 무엇인가?](./01-what-is-oop.md)
- [클래스와 인스턴스](./02-classes-and-instances.md)
- [캡슐화](./03-encapsulation.md)
- [상속](./04-inheritance.md)
- **다형성 (현재 글)**
- [추상화](./06-abstraction.md)
- [합성과 상속](./07-composition-vs-inheritance.md)
- [SOLID 원칙 기초](./08-solid-principles.md)
- [객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Real Python — Duck Typing in Python](https://realpython.com/duck-typing-python/)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Fluent Python — Chapter 13: Interfaces, Protocols, and ABCs](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

Tags: Python, OOP, 다형성, 덕 타이핑, 프로토콜

---
title: "Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?"
series: oop-101
episode: 1
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
  - 객체지향
  - 프로그래밍 패러다임
  - 클래스
last_reviewed: '2026-05-12'
seo_description: 객체지향의 핵심 아이디어와 절차지향 코드와의 차이를 실무 예제로 설명합니다.
---

# Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?

처음 객체지향을 배울 때 가장 자주 생기는 오해는 이것입니다. 클래스를 쓰면 코드가 더 고급스러워지고, 함수를 쓰면 덜 구조적이라는 생각입니다. 하지만 현업에서는 반대로 묻는 편이 더 정확합니다. 이 문제에서 정말 데이터와 동작을 함께 묶어야 하는가, 아니면 함수 몇 개로 끝내는 편이 더 나은가 하는 질문입니다.

객체지향은 문법 기능이 아니라 구조를 잡는 방식입니다. 코드가 커질수록 관련 데이터와 로직이 여러 함수에 흩어지고, 한 군데를 고치면 다른 군데도 함께 손봐야 할 때가 많아집니다. 그때 객체라는 경계를 세워 책임을 모으는 접근이 힘을 발휘합니다.

이 글은 OOP 101 시리즈의 첫 번째 글입니다.

## 먼저 던지는 질문

- 객체지향은 절차지향과 무엇이 다르고, 왜 등장했을까요?
- 클래스, 인스턴스, 속성, 메서드는 어떤 관계로 이해하면 쉬울까요?
- 작은 스크립트에서는 함수만으로 충분한데, 언제 객체가 더 자연스러울까요?

## 큰 그림

![Object-Oriented Programming 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/01/01-01-big-picture.ko.png)

*Object-Oriented Programming 101 1장 흐름 개요*

## 핵심 개념 잡기

> 절차지향 vs 객체지향 비교

```text
Procedural                     Object-Oriented
┌────────────────────┐        ┌────────────────────┐
│ Function A         │        │ Object A           │
│ Function B         │        │  ├─ Data           │
│ Function C         │        │  └─ Methods        │
│                    │        ├────────────────────┤
│ Global Data        │        │ Object B           │
│  ├─ var 1          │        │  ├─ Data           │
│  └─ var 2          │        │  └─ Methods        │
└────────────────────┘        └────────────────────┘
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 클래스(class) | 객체를 생성하기 위한 템플릿(설계도)입니다 |
| 인스턴스(instance) | 클래스를 기반으로 생성된 실제 객체입니다 |
| 속성(attribute) | 객체가 가진 데이터입니다 |
| 메서드(method) | 객체가 수행하는 행위(함수)입니다 |
| 캡슐화(encapsulation) | 데이터와 메서드를 하나로 묶고 외부 접근을 제한하는 것입니다 |

## 전후 비교

사용자 관리 로직을 비교합니다.

```python
# before: procedural — data and functions are separate
users = []

def create_user(name, email):
    user = {"name": name, "email": email, "active": True}
    users.append(user)
    return user

def deactivate_user(user):
    user["active"] = False

def get_user_display(user):
    status = "active" if user["active"] else "inactive"
    return f"{user['name']} ({status})"
```

```python
# after: OOP — data and behavior live in one class
class User:
    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email
        self.active = True

    def deactivate(self) -> None:
        self.active = False

    def display(self) -> str:
        status = "active" if self.active else "inactive"
        return f"{self.name} ({status})"
```

## 단계별 실습

### 1단계: 첫 번째 클래스 만들기

```python
class Dog:
    """A simple Dog class"""

    def __init__(self, name: str, breed: str) -> None:
        self.name = name
        self.breed = breed

    def bark(self) -> str:
        return f"{self.name} says woof!"

    def __repr__(self) -> str:
        return f"Dog(name={self.name!r}, breed={self.breed!r})"

my_dog = Dog("Buddy", "Golden Retriever")
print(my_dog.bark())  # Buddy says woof!
print(my_dog)          # Dog(name='Buddy', breed='Golden Retriever')
```

### 2단계: 여러 인스턴스 생성

```python
dog1 = Dog("Buddy", "Golden Retriever")
dog2 = Dog("Charlie", "Poodle")
dog3 = Dog("Max", "Labrador")

dogs = [dog1, dog2, dog3]
for dog in dogs:
    print(f"{dog.name} ({dog.breed}): {dog.bark()}")
# Buddy (Golden Retriever): Buddy says woof!
# Charlie (Poodle): Charlie says woof!
# Max (Labrador): Max says woof!

print(dog1 is dog2)  # False — different instances
```

### 3단계: 절차지향 → 객체지향 리팩터링

```python
# procedural version
def create_rect(width, height):
    return {"width": width, "height": height}

def area(rect):
    return rect["width"] * rect["height"]

def perimeter(rect):
    return 2 * (rect["width"] + rect["height"])

r = create_rect(5, 3)
print(area(r))       # 15
print(perimeter(r))  # 16
```

```python
# OOP version
class Rectangle:
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

    def __repr__(self) -> str:
        return f"Rectangle({self.width}, {self.height})"

r = Rectangle(5, 3)
print(r.area())       # 15
print(r.perimeter())  # 16
```

### 4단계: self의 의미

```python
class Counter:
    def __init__(self) -> None:
        self.count = 0

    def increment(self) -> None:
        self.count += 1

    def reset(self) -> None:
        self.count = 0

    def value(self) -> int:
        return self.count

c1 = Counter()
c2 = Counter()
c1.increment()
c1.increment()
c2.increment()
print(c1.value())  # 2
print(c2.value())  # 1 — each instance is independent
```

### 5단계: 클래스 변수 vs 인스턴스 변수

```python
class Student:
    school = "Python Academy"  # class variable: shared by all instances

    def __init__(self, name: str, grade: int) -> None:
        self.name = name    # instance variable: unique per instance
        self.grade = grade

    def introduce(self) -> str:
        return f"{self.name} at {self.school}, grade {self.grade}"

s1 = Student("Alice", 3)
s2 = Student("Bob", 2)
print(s1.introduce())  # Alice at Python Academy, grade 3
print(s2.introduce())  # Bob at Python Academy, grade 2

Student.school = "Code Academy"  # changing class variable affects all instances
print(s1.introduce())  # Alice at Code Academy, grade 3
```

## 이 코드에서 주목할 점

- `__init__`은 인스턴스 생성 시 자동 호출되는 초기화 메서드입니다
- `self`는 현재 인스턴스를 가리키며, 모든 인스턴스 메서드의 첫 번째 매개변수입니다
- 클래스 변수는 모든 인스턴스가 공유하고, 인스턴스 변수는 각 인스턴스에 독립적입니다
- `__repr__`을 정의하면 디버깅 시 객체를 읽기 쉬운 형태로 출력합니다

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `__init__`에서 self를 빠뜨림 | 인스턴스 변수가 아닌 지역 변수가 됩니다 | 반드시 `self.속성 = 값` 형태로 작성합니다 |
| 클래스 변수에 가변 객체 사용 | 모든 인스턴스가 같은 리스트를 공유합니다 | 가변 객체는 `__init__`에서 인스턴스 변수로 선언합니다 |
| 클래스와 인스턴스를 혼동 | `Dog.bark()` 호출 시 TypeError입니다 | 반드시 인스턴스를 생성한 후 메서드를 호출합니다 |
| 모든 것을 클래스로 감쌈 | 불필요한 복잡성이 추가됩니다 | 간단한 로직은 함수만으로 충분합니다 |
| `__repr__` 미정의 | 디버깅 시 `<__main__.Dog object>` 출력입니다 | `__repr__`을 정의하여 유용한 정보를 출력합니다 |

## 실무에서 이렇게 쓰입니다

- Django, Flask 등 웹 프레임워크의 모델은 클래스 기반입니다
- REST API에서 요청/응답 데이터를 클래스로 표현합니다
- 게임 개발에서 캐릭터, 아이템 등을 객체로 모델링합니다
- 데이터 파이프라인에서 각 처리 단계를 클래스로 추상화합니다
- 테스트 프레임워크(pytest, unittest)가 클래스 기반 테스트를 지원합니다

## 현업 개발자는 이렇게 생각합니다

객체지향은 만능이 아닙니다. 작은 스크립트에 클래스를 도입하면 오히려 복잡해집니다. 그러나 코드가 성장하면서 같은 데이터를 여러 함수가 공유할 때, 객체지향은 자연스러운 해결책이 됩니다.

실무에서는 "이것을 클래스로 만들어야 할까?"라는 질문을 자주 합니다. 답은 대부분 "관련 데이터와 행위가 함께 변경되는가?"입니다. 함께 변경된다면 하나의 클래스로 묶는 것이 유지보수에 유리합니다.

## 체크리스트

- [ ] 절차지향과 객체지향의 차이를 설명할 수 있다
- [ ] 클래스와 인스턴스의 관계를 이해한다
- [ ] `__init__`과 `self`의 역할을 설명할 수 있다
- [ ] 클래스 변수와 인스턴스 변수를 구분할 수 있다
- [ ] 간단한 클래스를 직접 설계하고 구현할 수 있다

## 정리 및 다음 글 안내

객체지향은 데이터와 행위를 하나의 단위로 묶어 코드의 구조를 명확하게 만드는 프로그래밍 방식입니다. 다음 글에서는 클래스와 인스턴스를 더 깊이 살펴보겠습니다.

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

- **객체지향은 절차지향과 무엇이 다르고, 왜 등장했을까요?**
  - 본문의 기준은 객체지향이란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **클래스, 인스턴스, 속성, 메서드는 어떤 관계로 이해하면 쉬울까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **작은 스크립트에서는 함수만으로 충분한데, 언제 객체가 더 자연스러울까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **객체지향이란 무엇인가? (현재 글)**
- 클래스와 인스턴스 (예정)
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

- [Python 공식 문서 — Classes](https://docs.python.org/3/tutorial/classes.html)
- [Real Python — Object-Oriented Programming in Python](https://realpython.com/python3-object-oriented-programming/)
- [Clean Code — Robert C. Martin](https://www.oreilly.com/library/view/clean-code/9780136083238/)
- [Python Crash Course — Eric Matthes](https://nostarch.com/python-crash-course-3rd-edition)

Tags: Python, OOP, 객체지향, 프로그래밍 패러다임, 클래스

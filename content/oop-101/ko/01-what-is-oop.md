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

![Object-Oriented Programming 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/01/01-01-big-picture.ko.png)
*Object-Oriented Programming 101 1장 흐름 개요*

## 이 글에서 다룰 문제

- 객체지향은 절차지향과 무엇이 다르고, 왜 등장했을까요?
- 클래스, 인스턴스, 속성, 메서드는 어떤 관계로 이해하면 쉬울까요?
- 작은 스크립트에서는 함수만으로 충분한데, 언제 객체가 더 자연스러울까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 이 글에서 배울 것

- 절차지향과 객체지향의 구조적 차이를 코드로 확인합니다
- 클래스, 인스턴스, 속성, 메서드의 역할을 명확하게 구분합니다
- `__init__`, `self`, `__repr__` 등 핵심 문법을 실습합니다
- 클래스 변수와 인스턴스 변수의 차이를 이해합니다
- 객체를 도입할 타이밍을 판단하는 기준을 익힙니다

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
# before: procedural — 데이터와 함수가 분리됨
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
# after: OOP — 데이터와 동작이 한 클래스에 함께 있음
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

절차지향 코드에서 `deactivate_user`와 `get_user_display`는 항상 `user` 딕셔너리를 함께 들고 다녀야 합니다. 관련 함수가 늘어날수록 이 의존 관계가 복잡해집니다. OOP 버전은 관련 데이터와 동작을 `User` 클래스 하나에 묶어 경계를 선명하게 만듭니다.

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

print(dog1 is dog2)  # False — different instances
```

각 인스턴스는 독립적인 상태를 가집니다. `dog1`의 이름을 바꾸어도 `dog2`는 영향을 받지 않습니다.

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

OOP 버전에서는 `r.area()`와 `r.perimeter()`가 모두 `r` 객체 하나에서 출발합니다. 함수를 별도로 임포트하거나 딕셔너리 키를 기억할 필요가 없습니다.

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

`self`는 메서드가 호출된 특정 인스턴스를 가리킵니다. `c1.increment()`는 `c1.count`만 바꾸고, `c2`는 그대로입니다.

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

클래스 변수는 모든 인스턴스가 공유합니다. 가변 객체(list, dict)를 클래스 변수로 선언하면 의도치 않은 공유 문제가 생깁니다. 인스턴스마다 다른 상태는 반드시 `__init__`에서 인스턴스 변수로 선언합니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `__init__`에서 `self` 없이 변수 선언 | 인스턴스 변수가 아닌 지역 변수가 됩니다 | 반드시 `self.속성 = 값` 형태로 작성합니다 |
| 클래스 변수에 가변 객체(`[]`, `{}`) 사용 | 모든 인스턴스가 같은 객체를 공유합니다 | 가변 객체는 `__init__`에서 인스턴스 변수로 선언합니다 |
| 클래스와 인스턴스를 혼동 | `Dog.bark()` 호출 시 `TypeError`가 납니다 | 인스턴스를 생성한 후 메서드를 호출합니다 |
| 간단한 로직에도 클래스를 억지로 씀 | 불필요한 복잡성이 추가됩니다 | 순수 변환 로직은 함수만으로 충분합니다 |
| `__repr__` 미정의 | 디버깅 시 `<__main__.Dog object>` 출력입니다 | `__repr__`을 정의하여 유용한 정보를 출력합니다 |

## 실무에서 이렇게 쓰입니다

실무에서는 사용자 인증 시스템을 구현할 때 OOP가 자연스럽게 등장합니다.

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

@dataclass
class UserAccount:
    username: str
    email: str
    role: UserRole = UserRole.VIEWER
    created_at: datetime = field(default_factory=datetime.now)
    _failed_attempts: int = field(default=0, repr=False)

    def promote(self, new_role: UserRole) -> None:
        if self.role == UserRole.ADMIN:
            raise ValueError("Admin role cannot be changed")
        self.role = new_role

    def record_failed_login(self) -> None:
        self._failed_attempts += 1

    def is_locked(self) -> bool:
        return self._failed_attempts >= 5

    def reset_failed_attempts(self) -> None:
        self._failed_attempts = 0

user = UserAccount("alice", "alice@example.com")
user.promote(UserRole.EDITOR)
user.record_failed_login()
user.record_failed_login()
print(user.is_locked())  # False
print(user.role)         # UserRole.EDITOR
```

이 예시처럼 상태 전이 규칙(`promote`, `is_locked`)이 사용자 데이터와 함께 `UserAccount` 클래스에 있으면, 어디서 호출하더라도 같은 규칙이 적용됩니다.

## 현업 개발자는 이렇게 생각합니다

객체지향은 만능이 아닙니다. 작은 스크립트에 클래스를 도입하면 오히려 복잡해집니다. 그러나 코드가 성장하면서 같은 데이터를 여러 함수가 공유할 때, 객체지향은 자연스러운 해결책이 됩니다.

실무에서는 "이것을 클래스로 만들어야 할까?"라는 질문을 자주 합니다. 가장 실용적인 기준은 "관련 데이터와 행위가 함께 변경되는가?"입니다. 함께 변경된다면 하나의 클래스로 묶는 것이 유지보수에 유리합니다.

객체를 도입할 타이밍:
- 같은 데이터 묶음이 세 곳 이상에서 함께 바뀔 때
- 상태 전이 규칙이 여러 함수에 중복될 때
- 테스트 픽스처를 준비하는 코드가 점점 길어질 때

## 운영 체크리스트

- [ ] 절차지향과 객체지향의 차이를 설명할 수 있다
- [ ] 클래스와 인스턴스의 관계를 이해한다
- [ ] `__init__`과 `self`의 역할을 설명할 수 있다
- [ ] 클래스 변수와 인스턴스 변수를 구분할 수 있다
- [ ] 간단한 클래스를 직접 설계하고 구현할 수 있다

## 연습 문제

1. `BankAccount` 클래스를 만드세요. `balance` 속성과 `deposit(amount)`, `withdraw(amount)` 메서드를 구현하고, 잔액이 부족할 때 `ValueError`를 발생시킵니다.
2. 절차지향으로 작성된 장바구니 코드를 OOP로 리팩터링하세요. 딕셔너리 리스트 대신 `Cart`와 `CartItem` 클래스를 설계합니다.
3. `Student` 클래스에 `__eq__`와 `__hash__`를 정의하여 `set`에 넣을 수 있게 만드세요.

## 정리 및 다음 단계

객체지향은 데이터와 행위를 하나의 단위로 묶어 코드의 구조를 명확하게 만드는 프로그래밍 방식입니다. 핵심은 클래스를 쓰는 것 자체가 아니라, 변경 이유가 같은 것들을 하나의 경계 안에 모으는 설계 감각입니다.

다음 글에서는 클래스와 인스턴스를 더 깊이 다룹니다. 생성자 패턴, `@classmethod`, `@staticmethod`, 그리고 dunder 메서드를 실무 예제로 정리합니다.

<!-- toc:begin -->
## 시리즈 목차

- **Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가? (현재 글)**
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
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

- [Python 공식 문서 — Classes](https://docs.python.org/3/tutorial/classes.html)
- [Real Python — Object-Oriented Programming in Python](https://realpython.com/python3-object-oriented-programming/)
- [Clean Code — Robert C. Martin](https://www.oreilly.com/library/view/clean-code/9780136083238/)
- [Python Crash Course — Eric Matthes](https://nostarch.com/python-crash-course-3rd-edition)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 객체지향, 프로그래밍 패러다임, 클래스

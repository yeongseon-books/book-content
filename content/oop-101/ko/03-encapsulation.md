---
title: "Object-Oriented Programming 101 (3/10): 캡슐화"
series: oop-101
episode: 3
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
  - 캡슐화
  - Property
  - 정보 은닉
last_reviewed: '2026-05-12'
seo_description: Python에서 캡슐화와 property를 활용해 안전한 객체 인터페이스를 만드는 법을 설명합니다.
---

# Object-Oriented Programming 101 (3/10): 캡슐화

객체가 외부에서 아무 제약 없이 내부 상태를 바꿀 수 있게 열려 있으면, 버그는 대개 늦게 발견됩니다. 더 곤란한 점은 원인을 좁히기 어렵다는 데 있습니다. 어디선가 값을 잘못 넣었는데도, 그 시점에는 시스템이 조용히 지나가다가 훨씬 뒤에서야 이상한 상태가 드러나기 때문입니다.

캡슐화는 값을 숨기기 위한 장식이 아니라 상태를 지키기 위한 계약입니다. Python은 Java처럼 강한 접근 제한 키워드를 두지 않지만, 밑줄 관례와 `property`만 제대로 써도 실무에서 충분히 강한 경계를 만들 수 있습니다.

이 글은 OOP 101 시리즈의 3번째 글입니다.

![Object-Oriented Programming 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/03/03-01-big-picture.ko.png)
*Object-Oriented Programming 101 3장 흐름 개요*

## 이 글에서 다룰 문제

- Python에서 public, `_protected`, `__private` 관례는 각각 어떻게 받아들이면 될까요?
- `property`는 단순 getter/setter 문법을 넘어 어떤 설계 이점을 줄까요?
- 유효성 검증을 속성 접근에 녹이면 객체 상태 관리가 왜 쉬워질까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 이 글에서 배울 것

- Python의 접근 제어 관례(`_`, `__`)를 이해합니다
- `@property`로 getter/setter를 구현하는 법을 익힙니다
- 읽기 전용 속성과 계산 속성 패턴을 배웁니다
- `__init__`에서 setter를 통한 검증 패턴을 적용합니다
- 캡슐화가 필요한 상황과 불필요한 상황을 구분합니다

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 캡슐화(encapsulation) | 데이터와 메서드를 묶고 내부 구현을 숨기는 원칙입니다 |
| 정보 은닉(information hiding) | 내부 상태를 외부에서 직접 접근할 수 없게 하는 것입니다 |
| property | Python 내장 데코레이터로 속성 접근을 메서드로 제어합니다 |
| 이름 맹글링(name mangling) | `__`로 시작하는 이름을 `_클래스명__이름`으로 변환합니다 |
| 불변식(invariant) | 객체 수명 동안 항상 참이어야 하는 조건입니다 |

## 전후 비교

계좌 잔액 관리를 비교합니다.

```python
# before: 직접 접근 — 잘못된 상태가 가능함
class BankAccount:
    def __init__(self, balance):
        self.balance = balance

account = BankAccount(1000)
account.balance = -500  # 음수 잔액이 허용됨 — 버그 가능성
```

```python
# after: property 보호 — validation 보장
class BankAccount:
    def __init__(self, owner: str, balance: int = 0) -> None:
        if balance < 0:
            raise ValueError("Opening balance cannot be negative")
        self.owner = owner
        self._balance = balance

    @property
    def balance(self) -> int:
        return self._balance

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient balance")
        self._balance -= amount

account = BankAccount("Alice", 1000)
account.deposit(500)
account.withdraw(200)
print(account.balance)  # 1300
# account.balance = -500  # AttributeError — setter가 없음
```

`balance`를 읽기 전용 property로 만들어 외부에서 직접 수정할 수 없게 합니다. 잔액 변경은 반드시 `deposit`과 `withdraw`를 통해야 하므로 검증이 항상 실행됩니다.

## 단계별 실습

### 1단계: Python 접근 제어 관례 이해

```python
class Employee:
    def __init__(self, name: str, salary: int) -> None:
        self.name = name              # public: 자유롭게 접근 가능
        self._department = "Unassigned"  # protected: 관례적 내부 사용 표시
        self.__salary = salary         # private: 이름 맹글링 적용

    def get_salary_band(self) -> str:
        if self.__salary >= 8000:
            return "senior"
        if self.__salary >= 5000:
            return "mid"
        return "junior"

emp = Employee("Kim", 6000)
print(emp.name)             # Kim
print(emp._department)      # Unassigned (접근은 되지만 관례상 비권장)
# print(emp.__salary)       # AttributeError
print(emp._Employee__salary)  # 6000 — 맹글링된 이름 (비권장)
print(emp.get_salary_band())  # mid
```

이름 맹글링은 보안 수단이 아닙니다. 실수로 하위 클래스에서 이름이 충돌하는 것을 방지하는 관례입니다.

### 2단계: property 기본 패턴

```python
class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius  # setter를 통해 검증 실행

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value <= 0:
            raise ValueError(f"Radius must be positive: {value}")
        self._radius = value

    @property
    def area(self) -> float:
        """읽기 전용 계산 속성"""
        import math
        return math.pi * self._radius ** 2

    @property
    def diameter(self) -> float:
        return self._radius * 2

c = Circle(5)
print(c.radius)    # 5
print(c.area)      # 78.539...
print(c.diameter)  # 10

c.radius = 10
print(c.area)      # 314.159...
# c.area = 100     # AttributeError — setter 없음
# c.radius = -1    # ValueError
```

`__init__`에서 `self.radius = radius`로 setter를 통해 검증을 실행합니다. `self._radius = radius`로 직접 할당하면 검증을 우회합니다.

### 3단계: 다중 속성 검증

```python
class UserProfile:
    def __init__(self, username: str, age: int, email: str) -> None:
        self.username = username
        self.age = age
        self.email = email

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not value.isalnum():
            raise ValueError("Username must be alphanumeric")
        self._username = value

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Age must be an integer")
        if not 0 <= value <= 150:
            raise ValueError(f"Invalid age: {value}")
        self._age = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        value = value.strip().lower()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError(f"Invalid email: {value}")
        self._email = value

user = UserProfile("alice123", 30, "ALICE@EXAMPLE.COM")
print(user.username)  # alice123
print(user.email)     # alice@example.com (소문자로 정규화)
```

### 4단계: 읽기 전용 속성

```python
from datetime import datetime

class Transaction:
    def __init__(self, amount: int, description: str) -> None:
        if amount == 0:
            raise ValueError("Transaction amount cannot be zero")
        self._amount = amount
        self._description = description
        self._created_at = datetime.now()

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def description(self) -> str:
        return self._description

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def __repr__(self) -> str:
        return f"Transaction({self._amount}, {self._description!r})"

tx = Transaction(10000, "Grocery shopping")
print(tx.amount)       # 10000
print(tx.created_at)   # datetime 객체
# tx.amount = 5000     # AttributeError
```

생성 후 변경하면 안 되는 데이터는 setter를 정의하지 않아 읽기 전용으로 만듭니다.

### 5단계: 일일 한도가 있는 계좌

```python
class LimitedBankAccount:
    DAILY_LIMIT = 1_000_000

    def __init__(self, owner: str, opening_balance: int = 0) -> None:
        if opening_balance < 0:
            raise ValueError("Opening balance must be >= 0")
        self.owner = owner
        self._balance = opening_balance
        self._daily_withdrawn = 0

    @property
    def balance(self) -> int:
        return self._balance

    @property
    def daily_withdrawn(self) -> int:
        return self._daily_withdrawn

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self._daily_withdrawn + amount > self.DAILY_LIMIT:
            raise ValueError(
                f"Daily limit {self.DAILY_LIMIT:,} exceeded. "
                f"Already withdrawn: {self._daily_withdrawn:,}"
            )
        if self._balance < amount:
            raise ValueError(f"Insufficient balance: {self._balance:,}")
        self._balance -= amount
        self._daily_withdrawn += amount

    def reset_daily_limit(self) -> None:
        """자정에 배치로 호출"""
        self._daily_withdrawn = 0

acc = LimitedBankAccount("Alice", 2_000_000)
acc.withdraw(500_000)
acc.deposit(100_000)
print(acc.balance)          # 1_600_000
print(acc.daily_withdrawn)  # 500_000
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 모든 속성을 `__`로 만듦 | 상속 시 하위 클래스에서 접근 불가합니다 | `_` 관례로 충분합니다 |
| property에서 무거운 계산 실행 | 속성 접근마다 비용이 발생합니다 | 무거운 연산은 일반 메서드로 분리합니다 |
| `__init__`에서 `_속성`에 직접 할당 | setter 검증을 우회합니다 | `__init__`에서도 `self.속성 = 값`으로 setter를 호출합니다 |
| 이름 맹글링을 보안으로 오해 | `_Class__name`으로 접근 가능합니다 | 관례적 보호이며 강제 수단이 아닙니다 |
| 검증 없는 getter/setter만 정의 | 단순 접근 방식과 같아 캡슐화 이점이 없습니다 | 검증이나 변환이 없으면 public 속성을 그대로 사용합니다 |

## 실무에서 이렇게 쓰입니다

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """읽기 전용 설정 클래스"""
    host: str
    port: int
    max_connections: int = 10
    _instance: Optional["Config"] = None

    def __post_init__(self) -> None:
        if not self.host:
            raise ValueError("host is required")
        if not 1 <= self.port <= 65535:
            raise ValueError(f"Invalid port: {self.port}")
        if self.max_connections < 1:
            raise ValueError("max_connections must be >= 1")

    @property
    def connection_string(self) -> str:
        return f"{self.host}:{self.port}"

config = Config(host="localhost", port=5432, max_connections=20)
print(config.connection_string)  # localhost:5432
```

Pydantic의 `@validator`, Django 모델의 `@property`, SQLAlchemy의 `hybrid_property` 모두 이 패턴을 확장한 것입니다.

## 현업 개발자는 이렇게 생각합니다

Python에서 캡슐화는 "강제"가 아니라 "계약"입니다. 밑줄 관례를 지키지 않아도 코드는 동작하지만, 내부 구현에 의존한 코드는 라이브러리 업데이트 시 깨지기 쉽습니다.

실무에서 가장 흔한 패턴은 "처음에는 public 속성으로 시작하고, 검증이 필요해지면 property로 전환"하는 것입니다. Python의 property 덕분에 이 전환이 호출자 코드를 변경하지 않고 가능합니다. 즉, `obj.radius = 5`라는 호출 방식은 그대로 유지하면서 내부 로직을 추가할 수 있습니다.

## 운영 체크리스트

- [ ] `_`와 `__` 관례의 차이를 설명할 수 있다
- [ ] `@property` 데코레이터로 getter/setter를 구현할 수 있다
- [ ] 읽기 전용 속성을 만들 수 있다
- [ ] `__init__`에서 setter를 통한 검증 패턴을 적용할 수 있다
- [ ] 캡슐화가 필요한 상황과 불필요한 상황을 구분할 수 있다

## 연습 문제

1. `Temperature` 클래스를 만드세요. 켈빈 단위로 내부 저장하고, 섭씨/화씨 property를 통해 읽고 쓸 수 있게 합니다. 절대영도 아래로는 설정할 수 없습니다.
2. `Inventory` 클래스에서 재고 수량을 property로 관리하세요. 감소 시 0 이하가 되면 예외를 발생시킵니다.
3. `Color` 클래스에서 RGB 값을 각각 property로 만들고, 0~255 범위를 벗어나면 ValueError를 발생시킵니다.

## 정리 및 다음 단계

캡슐화는 객체의 내부 상태를 보호하고 안전한 인터페이스를 제공하는 원칙입니다. Python에서는 밑줄 관례와 property 데코레이터로 이를 구현합니다. 핵심은 "어떤 상태가 항상 유효한가"를 결정하고, 그 규칙을 객체 내부에 가두는 것입니다.

다음 글에서는 상속을 통해 기존 클래스를 확장하는 방법을 알아봅니다. `super()`, 메서드 오버라이딩, MRO(Method Resolution Order)를 실무 예제로 정리합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
- **Object-Oriented Programming 101 (3/10): 캡슐화 (현재 글)**
- [Object-Oriented Programming 101 (4/10): 상속](./04-inheritance.md)
- [Object-Oriented Programming 101 (5/10): 다형성](./05-polymorphism.md)
- [Object-Oriented Programming 101 (6/10): 추상화](./06-abstraction.md)
- [Object-Oriented Programming 101 (7/10): 합성과 상속](./07-composition-vs-inheritance.md)
- [Object-Oriented Programming 101 (8/10): SOLID 원칙 기초](./08-solid-principles.md)
- [Object-Oriented Programming 101 (9/10): 객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Property](https://docs.python.org/3/library/functions.html#property)
- [Real Python — Python Property](https://realpython.com/python-property/)
- [Fluent Python — Chapter 11: A Pythonic Object](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Effective Python — Item 44: Use Plain Attributes Instead of Setter and Getter Methods](https://effectivepython.com/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 캡슐화, Property, 정보 은닉

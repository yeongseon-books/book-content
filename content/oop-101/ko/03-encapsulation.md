---
title: 캡슐화
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

# 캡슐화

객체가 외부에서 아무 제약 없이 내부 상태를 바꿀 수 있게 열려 있으면, 버그는 대개 늦게 발견됩니다. 더 곤란한 점은 원인을 좁히기 어렵다는 데 있습니다. 어디선가 값을 잘못 넣었는데도, 그 시점에는 시스템이 조용히 지나가다가 훨씬 뒤에서야 이상한 상태가 드러나기 때문입니다.

캡슐화는 값을 숨기기 위한 장식이 아니라 상태를 지키기 위한 계약입니다. Python은 Java처럼 강한 접근 제한 키워드를 두지 않지만, 밑줄 관례와 `property`만 제대로 써도 실무에서 충분히 강한 경계를 만들 수 있습니다.

이 글은 OOP 101 시리즈의 3번째 글입니다.

## 이 글에서 다룰 문제

> 캡슐화의 목적은 외부 접근을 무조건 막는 데 있지 않습니다. 객체가 유효한 상태를 스스로 지키게 만드는 데 있습니다.

- Python에서 public, `_protected`, `__private` 관례는 각각 어떻게 받아들이면 될까요?
- `property`는 단순 getter/setter 문법을 넘어 어떤 설계 이점을 줄까요?
- 유효성 검증을 속성 접근에 녹이면 객체 상태 관리가 왜 쉬워질까요?
- 캡슐화를 과하게 적용하면 오히려 복잡해지는 경우는 언제일까요?

## 핵심 개념 잡기

> Python의 접근 제어 관례

```text
Naming Pattern           Access Level
─────────────────────────────────────
name                    public — accessible by anyone
_name                   protected — internal / subclass use (convention)
__name                  private — name mangling applied (_Class__name)
__name__                dunder — Python internal protocol
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 캡슐화(encapsulation) | 데이터와 메서드를 묶고 내부 구현을 숨기는 원칙입니다 |
| 정보 은닉(information hiding) | 내부 상태를 외부에서 직접 접근할 수 없게 하는 것입니다 |
| property | Python 내장 데코레이터로 속성 접근을 메서드로 제어합니다 |
| 이름 맹글링(name mangling) | `__`로 시작하는 이름을 `_클래스명__이름`으로 변환합니다 |
| getter/setter | 속성 값을 읽거나 설정할 때 호출되는 메서드입니다 |

## 전후 비교

계좌 잔액 관리를 비교합니다.

```python
# before: direct access — invalid state possible
class BankAccount:
    def __init__(self, balance):
        self.balance = balance

account = BankAccount(1000)
account.balance = -500  # negative balance allowed — bug
```

```python
# after: property protection — validation guaranteed
class BankAccount:
    def __init__(self, balance: int) -> None:
        self._balance = balance  # protected

    @property
    def balance(self) -> int:
        return self._balance

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount: int) -> None:
        if amount > self._balance:
            raise ValueError("Insufficient balance")
        self._balance -= amount

account = BankAccount(1000)
account.deposit(500)    # 1500
account.withdraw(200)   # 1300
# account.balance = -500  # AttributeError — no setter defined
```

## 단계별 실습

### 1단계: 밑줄 관례 이해

```python
class Employee:
    def __init__(self, name: str, salary: int) -> None:
        self.name = name           # public
        self._department = "Unassigned"  # protected (convention)
        self.__salary = salary      # private (name mangling)

    def get_salary(self) -> int:
        return self.__salary

emp = Employee("Kim", 5000)
print(emp.name)            # Kim
print(emp._department)     # Unassigned (accessible but discouraged)
# print(emp.__salary)      # AttributeError
print(emp._Employee__salary)  # 5000 — mangled name access (not recommended)
print(emp.get_salary())    # 5000
```

### 2단계: property 기본

```python
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius

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
        """Read-only computed property"""
        import math
        return math.pi * self._radius ** 2

c = Circle(5)
print(c.radius)   # 5
print(c.area)     # 78.539...

c.radius = 10
print(c.area)     # 314.159...

# c.radius = -1   # ValueError
# c.area = 100    # AttributeError — no setter
```

### 3단계: 연쇄 유효성 검증

```python
class User:
    def __init__(self, name: str, age: int, email: str) -> None:
        self.name = name    # triggers setter validation
        self.age = age
        self.email = email

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value.strip():
            raise ValueError("Name cannot be empty")
        self._name = value.strip()

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if not 0 <= value <= 150:
            raise ValueError(f"Invalid age: {value}")
        self._age = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if "@" not in value:
            raise ValueError(f"Invalid email: {value}")
        self._email = value

user = User("Alice", 30, "alice@example.com")
print(user.name)   # Alice
user.age = 31      # OK
# user.age = -1    # ValueError
```

### 4단계: 읽기 전용 속성

```python
class ImmutablePoint:
    def __init__(self, x: float, y: float) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def __repr__(self) -> str:
        return f"ImmutablePoint({self._x}, {self._y})"

p = ImmutablePoint(3, 4)
print(p.x, p.y)  # 3 4
# p.x = 10       # AttributeError — read-only
```

### 5단계: 캡슐화와 인터페이스 분리

```python
class TemperatureSensor:
    """Hides internal implementation and exposes only converted values"""

    def __init__(self) -> None:
        self._raw_readings: list[float] = []

    def add_reading(self, celsius: float) -> None:
        self._raw_readings.append(celsius)

    @property
    def average_celsius(self) -> float:
        if not self._raw_readings:
            return 0.0
        return sum(self._raw_readings) / len(self._raw_readings)

    @property
    def average_fahrenheit(self) -> float:
        return self.average_celsius * 9 / 5 + 32

    @property
    def reading_count(self) -> int:
        return len(self._raw_readings)

sensor = TemperatureSensor()
sensor.add_reading(20.0)
sensor.add_reading(25.0)
sensor.add_reading(22.5)
print(f"{sensor.average_celsius:.1f}°C")     # 22.5°C
print(f"{sensor.average_fahrenheit:.1f}°F")   # 72.5°F
print(f"Readings: {sensor.reading_count}")     # Readings: 3
```

## 이 코드에서 주목할 점

- `@property`는 메서드를 속성처럼 접근할 수 있게 하여 인터페이스를 깔끔하게 유지합니다
- `__init__`에서 `self.name = value`는 setter를 통해 검증을 수행합니다
- 읽기 전용 속성은 setter를 정의하지 않으면 됩니다
- 이름 맹글링(`__`)은 실수 방지용이지 보안 수단이 아닙니다

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 모든 속성을 `__`로 만듦 | 상속 시 하위 클래스에서 접근 불가합니다 | `_` 관례로 충분합니다 |
| property에서 무거운 계산 | 속성 접근마다 비용이 발생합니다 | 무거운 연산은 메서드로 분리합니다 |
| setter 없이 `__init__`에서 직접 할당 | 유효성 검증을 우회합니다 | `__init__`에서도 setter를 사용합니다 |
| 이름 맹글링을 보안으로 오해 | `_Class__name`으로 접근 가능합니다 | 관례적 보호이며 강제가 아닙니다 |
| getter/setter만 있는 property | Java 스타일 boilerplate입니다 | 검증이나 계산이 없으면 public 속성을 사용합니다 |

## 실무에서 이렇게 쓰입니다

- Pydantic의 `@validator`는 property와 유사한 필드 수준 검증입니다
- SQLAlchemy의 `hybrid_property`는 Python과 SQL 양쪽에서 동작합니다
- Django 모델의 `@property`로 계산 필드를 추가합니다
- 설정 클래스에서 환경 변수를 읽기 전용 property로 노출합니다
- API 응답 객체에서 내부 구조를 숨기고 property로 필요한 값만 제공합니다

## 현업 개발자는 이렇게 생각합니다

Python에서 캡슐화는 "강제"가 아니라 "계약"입니다. 밑줄 관례를 지키지 않아도 코드는 동작하지만, 내부 구현에 의존한 코드는 라이브러리 업데이트 시 깨지기 쉽습니다.

실무에서 가장 흔한 패턴은 "처음에는 public 속성으로 시작하고, 검증이 필요해지면 property로 전환"하는 것입니다. Python의 property 덕분에 이 전환이 호출자 코드를 변경하지 않고 가능합니다.

## 체크리스트

- [ ] `_`와 `__` 관례의 차이를 설명할 수 있다
- [ ] `@property` 데코레이터로 getter/setter를 구현할 수 있다
- [ ] 읽기 전용 속성을 만들 수 있다
- [ ] `__init__`에서 setter를 통한 검증 패턴을 적용할 수 있다
- [ ] 캡슐화가 필요한 상황과 불필요한 상황을 구분할 수 있다

## 정리 및 다음 글 안내

캡슐화는 객체의 내부 상태를 보호하고 안전한 인터페이스를 제공하는 원칙입니다. Python에서는 밑줄 관례와 property 데코레이터로 이를 구현합니다. 다음 글에서는 상속을 통해 기존 클래스를 확장하는 방법을 알아봅니다.

<!-- toc:begin -->
- [객체지향이란 무엇인가?](./01-what-is-oop.md)
- [클래스와 인스턴스](./02-classes-and-instances.md)
- **캡슐화 (현재 글)**
- 상속 (예정)
- 다형성 (예정)
- 추상화 (예정)
- 합성과 상속 (예정)
- SOLID 원칙 기초 (예정)
- 객체지향 설계 예제 (예정)
- 객체지향을 언제 피해야 할까? (예정)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Property](https://docs.python.org/3/library/functions.html#property)
- [Real Python — Python Property](https://realpython.com/python-property/)
- [Fluent Python — Chapter 11: A Pythonic Object](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Effective Python — Item 44: Use Plain Attributes Instead of Setter and Getter Methods](https://effectivepython.com/)

Tags: Python, OOP, 캡슐화, Property, 정보 은닉

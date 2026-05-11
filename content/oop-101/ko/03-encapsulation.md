---
series: oop-101
episode: 3
title: 캡슐화
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
  - 캡슐화
  - Property
  - 정보 은닉
seo_description: Python에서 캡슐화를 구현하는 방법과 property를 활용한 접근 제어를 다룹니다.
last_reviewed: '2026-05-04'
---

# 캡슐화

> Object-Oriented Programming 101 시리즈 (3/10)


## 이 글에서 다룰 문제

외부 코드가 객체의 내부 데이터를 자유롭게 변경할 수 있으면, 객체가 잘못된 상태에 빠져도 원인을 찾기 어렵습니다. 캡슐화는 "이 데이터는 이 메서드를 통해서만 변경하세요"라는 계약을 만들어 버그를 줄입니다.

> 캡슐화 = 내부 구현 숨기기 + 안전한 인터페이스 제공

Python은 Java처럼 `private` 키워드가 없습니다. 대신 밑줄(`_`) 관례와 `property` 데코레이터를 사용합니다. 이 관례를 이해하면 Python 생태계의 코드를 자연스럽게 읽을 수 있습니다.

## 핵심 개념 잡기

> Python의 접근 제어 관례

```text
이름 규칙                접근 수준
─────────────────────────────────────
name                    public — 누구나 접근 가능
_name                   protected — 내부/하위 클래스용 (관례)
__name                  private — 이름 맹글링 적용 (_Class__name)
__name__                특수 메서드 — Python 내부 프로토콜
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 캡슐화(encapsulation) | 데이터와 메서드를 묶고 내부 구현을 숨기는 원칙입니다 |
| 정보 은닉(information hiding) | 내부 상태를 외부에서 직접 접근할 수 없게 하는 것입니다 |
| property | Python 내장 데코레이터로 속성 접근을 메서드로 제어합니다 |
| 이름 맹글링(name mangling) | `__`로 시작하는 이름을 `_클래스명__이름`으로 변환합니다 |
| getter/setter | 속성 값을 읽거나 설정할 때 호출되는 메서드입니다 |

## Before / After

계좌 잔액 관리를 비교합니다.

```python
# before: 직접 접근 — 잘못된 상태 가능
class BankAccount:
    def __init__(self, balance):
        self.balance = balance

account = BankAccount(1000)
account.balance = -500  # 음수 잔액 허용 — 버그
```

```python
# after: property로 보호 — 유효성 검증 보장
class BankAccount:
    def __init__(self, balance: int) -> None:
        self._balance = balance  # protected

    @property
    def balance(self) -> int:
        return self._balance

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("입금액은 양수여야 합니다")
        self._balance += amount

    def withdraw(self, amount: int) -> None:
        if amount > self._balance:
            raise ValueError("잔액이 부족합니다")
        self._balance -= amount

account = BankAccount(1000)
account.deposit(500)    # 1500
account.withdraw(200)   # 1300
# account.balance = -500  # AttributeError — setter 미정의
```

## 단계별 실습

### Step 1: 밑줄 관례 이해

```python
class Employee:
    def __init__(self, name: str, salary: int) -> None:
        self.name = name           # public
        self._department = "미배정"  # protected (관례)
        self.__salary = salary      # private (이름 맹글링)

    def get_salary(self) -> int:
        return self.__salary

emp = Employee("김개발", 5000)
print(emp.name)            # 김개발
print(emp._department)     # 미배정 (접근 가능하지만 관례상 외부 사용 자제)
# print(emp.__salary)      # AttributeError
print(emp._Employee__salary)  # 5000 — 맹글링된 이름으로 접근 가능 (비권장)
print(emp.get_salary())    # 5000
```

### Step 2: property 기본

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
            raise ValueError(f"반지름은 양수여야 합니다: {value}")
        self._radius = value

    @property
    def area(self) -> float:
        """읽기 전용 계산 속성"""
        import math
        return math.pi * self._radius ** 2

c = Circle(5)
print(c.radius)   # 5
print(c.area)     # 78.539...

c.radius = 10
print(c.area)     # 314.159...

# c.radius = -1   # ValueError
# c.area = 100    # AttributeError — setter 없음
```

### Step 3: 연쇄 유효성 검증

```python
class User:
    def __init__(self, name: str, age: int, email: str) -> None:
        self.name = name    # setter를 통해 검증
        self.age = age
        self.email = email

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value.strip():
            raise ValueError("이름은 비어있을 수 없습니다")
        self._name = value.strip()

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if not 0 <= value <= 150:
            raise ValueError(f"나이가 올바르지 않습니다: {value}")
        self._age = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if "@" not in value:
            raise ValueError(f"올바른 이메일이 아닙니다: {value}")
        self._email = value

user = User("홍길동", 30, "hong@example.com")
print(user.name)   # 홍길동
user.age = 31      # OK
# user.age = -1    # ValueError
```

### Step 4: 읽기 전용 속성

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
# p.x = 10       # AttributeError — 읽기 전용
```

### Step 5: 캡슐화와 인터페이스 분리

```python
class TemperatureSensor:
    """센서 내부 구현을 숨기고 변환된 값만 제공"""

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
print(f"측정 횟수: {sensor.reading_count}")    # 측정 횟수: 3
```

## 이 코드에서 주목할 점

- `@property`는 메서드를 속성처럼 접근할 수 있게 하여 인터페이스를 깔끔하게 유지합니다
- `__init__`에서 `self.name = value`는 setter를 통해 검증을 수행합니다
- 읽기 전용 속성은 setter를 정의하지 않으면 됩니다
- 이름 맹글링(`__`)은 실수 방지용이지 보안 수단이 아닙니다

## 흔한 실수 5가지

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
- [상속](./04-inheritance.md)
- [다형성](./05-polymorphism.md)
- [추상화](./06-abstraction.md)
- [합성과 상속](./07-composition-vs-inheritance.md)
- [SOLID 원칙 기초](./08-solid-principles.md)
- [객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Property](https://docs.python.org/3/library/functions.html#property)
- [Real Python — Python Property](https://realpython.com/python-property/)
- [Fluent Python — Chapter 11: A Pythonic Object](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Effective Python — Item 44: Use Plain Attributes Instead of Setter and Getter Methods](https://effectivepython.com/)

Tags: Python, OOP, 캡슐화, Property, 정보 은닉

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

## 먼저 던지는 질문

- Python에서 public, `_protected`, `__private` 관례는 각각 어떻게 받아들이면 될까요?
- `property`는 단순 getter/setter 문법을 넘어 어떤 설계 이점을 줄까요?
- 유효성 검증을 속성 접근에 녹이면 객체 상태 관리가 왜 쉬워질까요?

## 큰 그림

![Object-Oriented Programming 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/03/03-01-big-picture.ko.png)

*Object-Oriented Programming 101 3장 흐름 개요*

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

## 캡슐화는 private 문법보다 변경 통제 전략입니다

캡슐화는 외부 접근을 무조건 막는 기법이 아니라, 변경 책임을 객체 내부로 모아 외부 파급을 줄이는 전략입니다.

```text
[BankAccount]
  - _balance: int
  - _daily_withdrawn: int
  + deposit(amount)
  + withdraw(amount)
  + balance (read-only)

[TransferService] --> [BankAccount]
```

## before/after: 필드 직접 수정에서 규칙 기반 메서드로

```python
# before
account = {'balance': 10000, 'daily_withdrawn': 0}
account['balance'] -= 7000
account['daily_withdrawn'] += 7000
```

```python
# after
class BankAccount:
    DAILY_LIMIT = 500000

    def __init__(self, owner: str, opening_balance: int = 0) -> None:
        if opening_balance < 0:
            raise ValueError('opening_balance must be >= 0')
        self.owner = owner
        self._balance = opening_balance
        self._daily_withdrawn = 0

    @property
    def balance(self) -> int:
        return self._balance

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError('amount must be positive')
        self._balance += amount

    def withdraw(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError('amount must be positive')
        if self._daily_withdrawn + amount > self.DAILY_LIMIT:
            raise ValueError('daily limit exceeded')
        if self._balance < amount:
            raise ValueError('insufficient balance')
        self._balance -= amount
        self._daily_withdrawn += amount
```

## 설계 원칙 위반 사례

| 위반 | 증상 | 수정 |
|---|---|---|
| 외부에서 `_balance` 직접 수정 | 음수 잔액, 한도 우회 | 읽기 전용 노출 + 메서드 통제 |
| 검증 로직이 컨트롤러마다 중복 | 정책 변경 누락 | 객체 메서드로 단일화 |
| getter/setter 자동 생성만 사용 | 캡슐화 없이 필드 공개와 동일 | 도메인 행위 메서드로 의도 표현 |

## 비교표: 공개 필드 vs 캡슐화 객체

| 항목 | 공개 필드 중심 | 캡슐화 객체 |
|---|---|---|
| 정책 변경 대응 | 호출부 동시 수정 필요 | 객체 내부 수정으로 수렴 |
| 회귀 위험 | 누락 지점 다수 | 변경 지점 제한 |
| 디버깅 | 값만 보고 맥락 파악 어려움 | 메서드 경로로 원인 추적 가능 |

## 리팩터링 절차

1. 쓰기 경로를 모두 검색해 한 지점으로 모읍니다.
2. 필드 쓰기를 private로 숨기고 메서드 호출로 치환합니다.
3. 검증 규칙을 메서드 내부로 이동합니다.
4. 기존 호출부 테스트를 행위 기반 테스트로 갱신합니다.

## 실전 시나리오: 요구사항 변경을 견디는 구조로 바꾸기

현업에서는 기능 추가보다 규칙 변경이 더 자주 발생합니다. 따라서 클래스 구조를 평가할 때는 "지금 동작하는가"보다 "다음 변경을 어디까지 건드려야 하는가"를 기준으로 보는 편이 안전합니다.

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass
class LineItem:
    name: str
    quantity: int
    unit_price: int

    def subtotal(self) -> int:
        return self.quantity * self.unit_price


class DiscountPolicy(Protocol):
    def apply(self, amount: int) -> int:
        ...


class NoDiscount:
    def apply(self, amount: int) -> int:
        return amount


class PercentDiscount:
    def __init__(self, percent: int) -> None:
        if not 0 <= percent <= 100:
            raise ValueError('percent must be 0..100')
        self.percent = percent

    def apply(self, amount: int) -> int:
        return int(amount * (100 - self.percent) / 100)


class Invoice:
    def __init__(self, items: list[LineItem], policy: DiscountPolicy) -> None:
        self.items = items
        self.policy = policy

    def total(self) -> int:
        base = sum(i.subtotal() for i in self.items)
        return self.policy.apply(base)
```

이 코드는 할인 규칙이 바뀌어도 `Invoice.total()`을 수정할 필요가 없습니다. 확장은 구현 클래스 추가로 닫히고, 핵심 흐름은 안정적으로 유지됩니다.

## UML 스타일로 보는 협력 관계

```text
[Invoice]
  - items: list[LineItem]
  - policy: DiscountPolicy
  + total()

[LineItem]
  + subtotal()

[DiscountPolicy] <<interface>>
  + apply(amount)
      ^
      +-- [NoDiscount]
      +-- [PercentDiscount]
```

협력 구조를 이렇게 텍스트로 적어 두면 코드 리뷰에서 "어디가 정책 축이고 어디가 도메인 축인가"를 빠르게 맞출 수 있습니다.

## 안티패턴과 교정 절차

| 안티패턴 | 발견 신호 | 교정 순서 |
|---|---|---|
| 거대 클래스(God Object) | 메서드가 20개 이상, 변경 이력이 분산됨 | 책임 축 분해 → 협력 인터페이스 도출 |
| 데이터만 가진 빈 클래스 | 메서드 없이 getter/setter만 존재 | 규칙 메서드 이동 또는 dataclass로 단순화 |
| 상속 트리 우회 분기 | 하위 클래스 타입 체크 분기 존재 | 다형성 계약 재정의 |
| 인프라 타입 누수 | 도메인 계층이 SDK 응답 객체 의존 | DTO 변환 계층 추가 |

## 전후 비교: 테스트 유지비

| 항목 | 리팩터링 전 | 리팩터링 후 |
|---|---|---|
| 테스트 준비 | 전역 상태 초기화 필요 | 객체 단위 상태 생성 |
| 실패 원인 추적 | 함수 체인 전체 역추적 | 클래스 메서드 단위 추적 |
| 회귀 범위 | 넓고 불명확 | 좁고 예측 가능 |

## 팀 적용 체크리스트

- 도메인 용어와 클래스 이름이 일치하는지 확인합니다.
- 인스턴스 생성 시점에 불변식이 완성되는지 확인합니다.
- 정책 변경이 기존 코드 수정이 아닌 구현 추가로 가능한지 점검합니다.
- 코드 리뷰에서 UML 텍스트 10줄로 협력 구조를 먼저 합의합니다.
- 테스트 이름이 메서드명보다 비즈니스 규칙을 설명하는지 확인합니다.

## 미니 케이스 스터디: 규칙 추가 한 번으로 검증하기

아래 예시는 정책 확장을 기존 코드 수정 없이 추가하는 최소 단위입니다.

```python
class WeekendPolicy:
    def apply(self, amount: int, is_weekend: bool) -> int:
        if is_weekend:
            return int(amount * 0.95)
        return amount


def estimate(amount: int, is_weekend: bool) -> int:
    policy = WeekendPolicy()
    return policy.apply(amount, is_weekend)
```

핵심은 새로운 정책이 호출 경로를 깨지 않고 들어온다는 점입니다. 변경 이력이 정책 클래스에만 남도록 경계를 유지하면 회귀 위험이 줄어듭니다.

| 확인 질문 | Pass 기준 |
|---|---|
| 새 정책 추가 시 기존 함수 수정이 필요한가 | 아니오 |
| 예외 정책이 기존 계약과 같은가 | 예 |
| 테스트가 정책별로 분리되어 있는가 | 예 |


## 리팩터링 회고: 변경 비용을 수치로 보는 방법

- 수정 파일 수가 기능 하나당 5개를 넘으면 경계 재설계를 검토합니다.
- 타입 분기 if/elif가 3개 이상 누적되면 다형성 또는 전략 객체로 이동합니다.
- 회귀 테스트 작성 시간이 구현 시간보다 길어지면 책임 배치를 재검토합니다.

```python
def complexity_signal(changed_files: int, branch_count: int) -> str:
    if changed_files >= 5 or branch_count >= 3:
        return 'refactor-needed'
    return 'acceptable'
```

위 방식은 엄밀한 메트릭은 아니지만, 팀이 감각이 아니라 기준으로 논의하게 만드는 데 유용합니다.


## 추가 비교표: 설계 결정 매트릭스

| 상황 | 권장 구조 | 피해야 할 선택 |
|---|---|---|
| 규칙이 자주 바뀜 | 정책 객체 분리 + 주입 | 하드코딩 분기 누적 |
| 상태 전이가 핵심 | 메서드 기반 전이 모델 | 외부에서 필드 직접 변경 |
| 외부 연동 잦음 | 포트/어댑터 분리 | 도메인에서 SDK 직접 호출 |
| 팀 온보딩 필요 | UML 텍스트와 용어 사전 유지 | 암묵 규칙 의존 |

이 매트릭스는 설계 정답을 고정하려는 목적이 아닙니다. 같은 팀 내에서 판단 언어를 통일해 코드 리뷰 시간을 줄이는 데 목적이 있습니다.

## 검증 노트: 객체 설계 품질을 점검하는 질문

아래 질문은 구현 이후 리뷰에서 반복적으로 사용하는 기준입니다.

- 이 메서드가 실패할 때 예외 타입과 메시지가 호출자 계약과 일치하는가.
- 같은 규칙이 다른 클래스나 함수에 중복되어 있지 않은가.
- 상태 변경이 메서드 한 경로로만 이루어지는가.
- 외부 의존성 없이 단위 테스트가 가능한가.

```python
def review_signal(duplicate_rules: int, mutable_paths: int) -> str:
    if duplicate_rules > 0:
        return '중복 규칙 제거 필요'
    if mutable_paths > 1:
        return '상태 변경 경로 통합 필요'
    return '구조 안정'
```

이런 체크를 글 단위 예제에도 적용하면, 객체지향을 문법이 아니라 유지보수 전략으로 이해하는 데 도움이 됩니다.

## 검증 노트: 객체 설계 품질을 점검하는 질문

아래 질문은 구현 이후 리뷰에서 반복적으로 사용하는 기준입니다.

- 이 메서드가 실패할 때 예외 타입과 메시지가 호출자 계약과 일치하는가.
- 같은 규칙이 다른 클래스나 함수에 중복되어 있지 않은가.
- 상태 변경이 메서드 한 경로로만 이루어지는가.
- 외부 의존성 없이 단위 테스트가 가능한가.

```python
def review_signal(duplicate_rules: int, mutable_paths: int) -> str:
    if duplicate_rules > 0:
        return '중복 규칙 제거 필요'
    if mutable_paths > 1:
        return '상태 변경 경로 통합 필요'
    return '구조 안정'
```

이런 체크를 글 단위 예제에도 적용하면, 객체지향을 문법이 아니라 유지보수 전략으로 이해하는 데 도움이 됩니다.

## 추가 비교: 변경 요청 대응 시간

| 변경 요청 | 경계가 약한 코드 | 경계가 선명한 코드 |
|---|---|---|
| 할인 규칙 추가 | 분기문 탐색 후 다중 수정 | 정책 구현 추가 |
| 상태 전이 수정 | 여러 함수 동시 수정 | 도메인 메서드 수정 |
| 테스트 보강 | 통합 테스트 중심 | 단위 테스트 우선 |

이 비교는 성능 수치가 아니라 유지보수 리드타임을 줄이는 관점에서 중요합니다.


## 추가 코드 예시: 규칙 변경을 메서드로 고립

```python
class Membership:
    def __init__(self, level: str) -> None:
        self.level = level

    def discount_rate(self) -> int:
        if self.level == 'gold':
            return 20
        if self.level == 'silver':
            return 10
        return 0


class PriceCalculator:
    def __init__(self, membership: Membership) -> None:
        self.membership = membership

    def final_price(self, amount: int) -> int:
        rate = self.membership.discount_rate()
        return int(amount * (100 - rate) / 100)
```

이 구조에서 멤버십 정책이 바뀌면 `Membership` 구현만 수정하면 됩니다.

## 보강 메모

설계 선택은 정답 찾기가 아니라 변경 비용을 낮추는 의사결정입니다. 같은 기능이라도 경계를 먼저 정의하면 리뷰와 테스트가 단순해집니다.

## 짧은 리마인더

객체지향을 적용할 때는 "클래스를 몇 개 만들었는가"보다 "다음 변경에서 몇 파일을 수정해야 하는가"를 기준으로 품질을 평가합니다.

## 처음 질문으로 돌아가기

- **Python에서 public, `_protected`, `__private` 관례는 각각 어떻게 받아들이면 될까요?**
  - 본문의 기준은 캡슐화를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`property`는 단순 getter/setter 문법을 넘어 어떤 설계 이점을 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **유효성 검증을 속성 접근에 녹이면 객체 상태 관리가 왜 쉬워질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
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

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 캡슐화, Property, 정보 은닉

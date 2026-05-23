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

## 먼저 던지는 질문

- 객체지향은 절차지향과 무엇이 다르고, 왜 등장했을까요?
- 클래스, 인스턴스, 속성, 메서드는 어떤 관계로 이해하면 쉬울까요?
- 작은 스크립트에서는 함수만으로 충분한데, 언제 객체가 더 자연스러울까요?

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
# Buddy (Golden Retriever): Buddy가 멍멍!
# Charlie (Poodle): Charlie가 멍멍!
# Max (Labrador): Max가 멍멍!

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

객체지향은 데이터와 행위를 하나의 단위로 묶어 코드의 구조를 명확하게 만드는 프로그래밍 방식입니다. 다음 글에서는 클래스와 인스턴스를 더 깊이 다룹니다.

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

## 설계 경계를 텍스트 UML로 그려 보기

객체지향 입문에서 클래스 문법보다 먼저 잡아야 하는 감각은 경계입니다. 경계가 선명하면 어떤 데이터가 어디에서 바뀌는지 추적할 수 있고, 요구사항이 바뀌어도 수정 범위를 예측하기 쉬워집니다.

```text
[OrderService]
  - place_order(cart, payment)
  - cancel_order(order_id)
        |
        | uses
        v
[Order]
  - id: str
  - lines: list[OrderLine]
  - status: OrderStatus
  - total_amount()
        |
        | has many
        v
[OrderLine]
  - product_id: str
  - quantity: int
  - unit_price: int
```

이 구조의 핵심은 `OrderService`가 흐름을 조정하고, `Order`가 도메인 규칙을 책임진다는 점입니다. 서비스가 모든 계산을 들고 있으면 규칙이 흩어지고, 엔티티가 외부 인프라를 알면 경계가 무너집니다.

## 절차지향 코드에서 객체 경계로 이동하는 리팩터링

아래 코드는 초기에 빠르게 만들기 쉬운 형태입니다. 문제는 주문 금액 계산, 쿠폰 적용, 상태 변경 규칙이 한 함수에 섞여 있다는 점입니다.

```python
# before

def checkout(order_dict: dict, coupon: dict | None) -> dict:
    if order_dict['status'] != 'draft':
        raise ValueError('invalid status')

    total = 0
    for line in order_dict['lines']:
        total += line['quantity'] * line['unit_price']

    if coupon and coupon['type'] == 'percent':
        total = int(total * (100 - coupon['value']) / 100)

    order_dict['total'] = total
    order_dict['status'] = 'placed'
    return order_dict
```

```python
# after
from dataclasses import dataclass
from enum import Enum


class OrderStatus(str, Enum):
    DRAFT = 'draft'
    PLACED = 'placed'


@dataclass(frozen=True)
class OrderLine:
    product_id: str
    quantity: int
    unit_price: int

    def amount(self) -> int:
        return self.quantity * self.unit_price


class Order:
    def __init__(self, lines: list[OrderLine]) -> None:
        self.lines = lines
        self.status = OrderStatus.DRAFT
        self._discount_rate = 0

    def apply_percent_coupon(self, value: int) -> None:
        if not 0 <= value <= 100:
            raise ValueError('coupon percent must be 0..100')
        self._discount_rate = value

    def total_amount(self) -> int:
        subtotal = sum(line.amount() for line in self.lines)
        return int(subtotal * (100 - self._discount_rate) / 100)

    def place(self) -> None:
        if self.status != OrderStatus.DRAFT:
            raise ValueError('only draft can be placed')
        self.status = OrderStatus.PLACED
```

절차지향 코드에서 객체지향 코드로 바뀌며 생긴 가장 큰 차이는 계산식이 아니라 규칙 위치입니다. 쿠폰 검증, 상태 전이, 금액 계산이 `Order` 내부로 모여 테스트 단위가 명확해졌습니다.

## 원칙 위반 시그널과 수정 방법

| 위반 시그널 | 어떤 문제가 생기나 | 수정 방향 |
|---|---|---|
| 서비스 함수가 200줄 이상으로 비대해짐 | 정책 변경 시 함수 전체를 읽어야 함 | 도메인 클래스로 규칙 이동 |
| 같은 키 문자열(`'status'`, `'total'`)이 여러 파일에 중복 | 오타가 런타임까지 숨어 있음 | 속성을 가진 타입으로 치환 |
| 검증 로직이 API, 서비스, 배치에 각각 존재 | 규칙 불일치로 장애 발생 | 객체 메서드에 단일 규칙 정의 |
| 테스트가 입력 딕셔너리 조립에 집중 | 의미보다 형태를 검증 | 행위를 검증하는 메서드 테스트로 전환 |

## 비교표: 함수 중심과 객체 중심의 유지보수 비용

| 관점 | 함수 중심 코드 | 객체 중심 코드 |
|---|---|---|
| 규칙 탐색 | 여러 함수와 전역 상수 추적 필요 | 클래스 내부 메서드에서 집중 확인 |
| 변경 영향도 | 호출 그래프를 넓게 따라가야 함 | 해당 객체와 협력 객체 위주로 좁아짐 |
| 타입 안정성 | 딕셔너리 키 오타가 늦게 발견 | 속성, 메서드 계약으로 빨리 드러남 |
| 온보딩 | 파일 순서에 따라 이해 편차 큼 | 도메인 용어 단위로 학습 가능 |

## 실무 체크: 객체를 도입할 타이밍

- 같은 데이터 묶음이 세 곳 이상에서 함께 바뀌면 클래스로 묶는 편이 유리합니다.
- 상태 전이가 중요하면 enum + 메서드로 전이 규칙을 명시하는 편이 안전합니다.
- 입출력 스키마와 도메인 규칙을 분리하면 API 변경이 도메인 전체로 전파되는 일을 줄일 수 있습니다.
- 클래스 수를 늘리는 것보다 변경 이유를 분리하는 것이 우선입니다.

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

## 보강 메모

설계 선택은 정답 찾기가 아니라 변경 비용을 낮추는 의사결정입니다. 같은 기능이라도 경계를 먼저 정의하면 리뷰와 테스트가 단순해집니다.

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

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 객체지향, 프로그래밍 패러다임, 클래스

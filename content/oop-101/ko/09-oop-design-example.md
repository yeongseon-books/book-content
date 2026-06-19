---
title: "Object-Oriented Programming 101 (9/10): 객체지향 설계 예제"
series: oop-101
episode: 9
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
  - 설계 예제
  - 리팩터링
  - 클래스 설계
last_reviewed: '2026-05-15'
seo_description: 온라인 서점 주문 시스템 예제로 OOP 설계와 리팩터링 과정을 단계별로 보여줍니다.
---

# Object-Oriented Programming 101 (9/10): 객체지향 설계 예제

개념을 따로 배울 때는 캡슐화, 상속, 다형성, 합성, SOLID가 각각 이해되는 듯 보입니다. 그런데 실제 기능 하나를 설계하려고 하면 갑자기 어려워집니다. 어디서 클래스를 나누고, 어떤 규칙은 지금 적용하고 어떤 규칙은 나중으로 미뤄야 할지 판단이 필요해지기 때문입니다.

이 글은 온라인 서점 주문 시스템을 절차지향 코드에서 출발하여 OOP로 점진적으로 발전시키는 과정을 보여줍니다. 완벽한 설계를 목표로 하는 것이 아니라, 변경이 생길 때마다 설계를 어떻게 조정하는지에 집중합니다.

이 글은 OOP 101 시리즈의 9번째 글입니다.

![Object-Oriented Programming 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/09/09-01-big-picture.ko.png)
*Object-Oriented Programming 101 9장 흐름 개요*

## 이 글에서 다룰 문제

- 절차지향 코드에서 OOP로 전환할 때 첫 번째 경계를 어디에 그어야 할까요?
- Value Object, Entity, Service는 어떤 기준으로 구분하나요?
- 요구사항이 바뀔 때 설계를 어떻게 조정하나요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 이 글에서 배울 것

- 절차지향에서 OOP로 전환하는 리팩터링 과정을 따라갑니다
- Value Object, Entity, Service의 역할을 구분합니다
- 도메인 규칙을 올바른 계층에 배치하는 기준을 익힙니다
- 할인 정책 확장을 OCP 방식으로 처리합니다
- 테스트 가능한 설계를 위한 DIP 적용 방법을 배웁니다

## 핵심 개념

| 패턴 | 역할 |
|------|------|
| Value Object | 동일성이 값에 있고, 불변입니다. (예: Money, Email) |
| Entity | 동일성이 식별자에 있고, 상태가 변합니다. (예: Order, User) |
| Service | 도메인 규칙을 조합하는 역할로, 자체 상태가 없습니다. |
| Repository | 영속성 저장/조회를 담당합니다. |
| Policy / Strategy | 교체 가능한 비즈니스 규칙 단위입니다. |

## 전후 비교

절차지향 주문 처리를 OOP로 전환합니다.

```python
# before: 절차지향 — 데이터와 로직이 딕셔너리와 함수로 분산
def create_order(book_id: str, qty: int, price: int, coupon: str | None) -> dict:
    total = price * qty
    if coupon == "SAVE10":
        total = int(total * 0.9)
    if total <= 0:
        raise ValueError("Invalid total")
    return {"book_id": book_id, "qty": qty, "total": total, "status": "pending"}

def confirm_order(order: dict) -> None:
    if order["status"] != "pending":
        raise ValueError("Only pending orders can be confirmed")
    order["status"] = "confirmed"
    print(f"Order confirmed: {order['total']}")
```

```python
# after: OOP — 도메인 규칙이 각 객체에 모임
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

@dataclass(frozen=True)
class Money:
    """Value Object: 금액 표현"""
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"Money cannot be negative: {self.amount}")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)

    def __repr__(self) -> str:
        return f"{self.amount:,} {self.currency}"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

@dataclass
class OrderItem:
    book_id: str
    quantity: int
    unit_price: Money

    def subtotal(self) -> Money:
        return Money(self.unit_price.amount * self.quantity)
```

## 단계별 실습: 온라인 서점 주문 시스템

### 1단계: Value Object — Money와 Email

```python
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"Money cannot be negative: {self.amount}")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)

    def apply_discount(self, rate: float) -> "Money":
        if not 0 <= rate <= 1:
            raise ValueError("Rate must be 0.0 to 1.0")
        return Money(int(self.amount * (1 - rate)), self.currency)

    def __repr__(self) -> str:
        return f"{self.amount:,} {self.currency}"

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.value):
            raise ValueError(f"Invalid email: {self.value}")

m1 = Money(10000)
m2 = Money(5000)
print(m1.add(m2))                # 15,000 KRW
print(m1.apply_discount(0.2))   # 8,000 KRW

email = Email("alice@example.com")
# Email("not-an-email")  # ValueError
```

Value Object는 `frozen=True`로 불변성을 보장합니다. 두 Money가 같은 금액과 통화를 가지면 동일합니다.

### 2단계: Entity — Order

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol
import uuid

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

@dataclass
class OrderItem:
    book_id: str
    quantity: int
    unit_price: Money

    def subtotal(self) -> Money:
        return Money(self.unit_price.amount * self.quantity)

class DiscountPolicy(Protocol):
    def apply(self, amount: Money) -> Money: ...

class NoDiscount:
    def apply(self, amount: Money) -> Money:
        return amount

class PercentDiscount:
    def __init__(self, rate: float) -> None:
        self.rate = rate

    def apply(self, amount: Money) -> Money:
        return amount.apply_discount(self.rate)

@dataclass
class Order:
    """Entity: 식별자(id)로 동일성 판단"""
    customer_email: Email
    items: list[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    _discount: DiscountPolicy = field(default_factory=NoDiscount, repr=False)

    def add_item(self, item: OrderItem) -> None:
        if self.status != OrderStatus.PENDING:
            raise ValueError("Cannot modify non-pending order")
        self.items.append(item)

    def apply_discount(self, policy: DiscountPolicy) -> None:
        if self.status != OrderStatus.PENDING:
            raise ValueError("Discount can only be applied to pending orders")
        self._discount = policy

    def subtotal(self) -> Money:
        return Money(sum(item.subtotal().amount for item in self.items))

    def total(self) -> Money:
        return self._discount.apply(self.subtotal())

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot confirm order in {self.status} status")
        if not self.items:
            raise ValueError("Cannot confirm empty order")
        self.status = OrderStatus.CONFIRMED

    def cancel(self) -> None:
        if self.status == OrderStatus.SHIPPED:
            raise ValueError("Cannot cancel shipped order")
        self.status = OrderStatus.CANCELLED
```

### 3단계: Repository 인터페이스와 구현

```python
from typing import Protocol

class OrderRepository(Protocol):
    def save(self, order: Order) -> None: ...
    def find(self, order_id: str) -> Order | None: ...
    def find_by_customer(self, email: Email) -> list[Order]: ...

class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._store: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._store[order.id] = order

    def find(self, order_id: str) -> Order | None:
        return self._store.get(order_id)

    def find_by_customer(self, email: Email) -> list[Order]:
        return [
            o for o in self._store.values()
            if o.customer_email == email
        ]
```

### 4단계: Service — OrderService

```python
class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repo = repository

    def create_order(self, customer_email: str) -> Order:
        email = Email(customer_email)
        order = Order(customer_email=email)
        self._repo.save(order)
        return order

    def add_book(
        self,
        order_id: str,
        book_id: str,
        quantity: int,
        unit_price: int,
    ) -> None:
        order = self._find_or_raise(order_id)
        item = OrderItem(book_id, quantity, Money(unit_price))
        order.add_item(item)
        self._repo.save(order)

    def apply_coupon(self, order_id: str, discount_rate: float) -> None:
        order = self._find_or_raise(order_id)
        order.apply_discount(PercentDiscount(discount_rate))
        self._repo.save(order)

    def confirm(self, order_id: str) -> Money:
        order = self._find_or_raise(order_id)
        order.confirm()
        self._repo.save(order)
        return order.total()

    def _find_or_raise(self, order_id: str) -> Order:
        order = self._repo.find(order_id)
        if order is None:
            raise ValueError(f"Order not found: {order_id}")
        return order
```

### 5단계: 전체 조립과 실행

```python
# 조립
repo = InMemoryOrderRepository()
service = OrderService(repo)

# 시나리오: 책 2권 주문, 10% 할인 쿠폰 적용
order = service.create_order("alice@example.com")
service.add_book(order.id, "BOOK-001", quantity=2, unit_price=18000)
service.add_book(order.id, "BOOK-002", quantity=1, unit_price=25000)
service.apply_coupon(order.id, discount_rate=0.10)

print(f"Subtotal: {order.subtotal()}")  # 61,000 KRW
total = service.confirm(order.id)
print(f"Total after discount: {total}")  # 54,900 KRW
print(f"Status: {order.status}")         # OrderStatus.CONFIRMED

# 같은 고객의 주문 조회
customer_orders = repo.find_by_customer(Email("alice@example.com"))
print(f"Order count: {len(customer_orders)}")  # 1
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 모든 클래스를 Service로 만듦 | 도메인 규칙이 서비스에 흩어집니다 | 규칙은 Entity/Value Object 내부에 둡니다 |
| Value Object에 식별자(id) 추가 | Value Object의 동일성 의미가 깨집니다 | 식별자가 필요하면 Entity로 설계합니다 |
| Repository에 비즈니스 규칙 포함 | 저장 계층이 도메인 변경에 영향받습니다 | Repository는 저장/조회만 담당합니다 |
| 상태 전이를 외부에서 직접 변경 | `order.status = "confirmed"` 처럼 우회 | 상태 변경은 반드시 메서드를 통해 합니다 |
| `dataclass`에서 가변 기본값 | 모든 인스턴스가 같은 리스트를 공유합니다 | `field(default_factory=list)`를 사용합니다 |

## 실무에서 이렇게 쓰입니다

이 설계 패턴은 Django의 모델-뷰 분리, FastAPI의 Pydantic 모델, DDD(Domain-Driven Design)의 Aggregate 패턴으로 이어집니다.

`Money`처럼 도메인 값을 별도 타입으로 만들면 `int`를 잘못 전달하는 실수를 타입 검사기가 잡아줍니다. `order.status = "shipped"`처럼 잘못된 문자열 직접 할당을 막고 `order.ship()` 메서드만 허용하면 상태 전이 규칙이 항상 지켜집니다.

## 현업 개발자는 이렇게 생각합니다

설계는 한 번에 완성하지 않습니다. 처음에는 절차지향 코드로 빠르게 동작시키고, 같은 데이터를 여러 함수가 공유하거나, 규칙이 여러 곳에 중복될 때 객체 경계를 그어갑니다.

"어떤 규칙이 바뀔 때 어떤 코드를 수정해야 하는가"를 기준으로 경계를 그으면, 변경 범위가 예측 가능해집니다.

## 운영 체크리스트

- [ ] Value Object와 Entity의 차이를 설명할 수 있다
- [ ] 도메인 규칙을 적절한 클래스에 배치할 수 있다
- [ ] Repository 인터페이스를 Protocol로 정의할 수 있다
- [ ] 상태 전이를 메서드로만 처리할 수 있다
- [ ] 할인 정책을 OCP 방식으로 확장할 수 있다

## 연습 문제

1. `Book` 클래스를 Value Object로 설계하세요. ISBN, 제목, 저자, 정가를 포함하고, ISBN 형식 검증을 추가합니다.
2. `Cart` Entity를 설계하세요. 항목 추가/제거, 수량 변경, 총 금액 계산 기능을 포함합니다. 항목이 비어 있을 때 결제 시도 시 예외를 발생시킵니다.
3. `VolumeDiscount` 정책을 추가하세요. 총 금액이 50,000원 이상이면 5%, 100,000원 이상이면 10% 할인합니다. 기존 코드를 수정하지 않고 추가합니다.

## 정리 및 다음 단계

OOP 설계는 도메인 규칙을 적절한 객체에 배치하고, 변경이 일어날 때 수정 범위를 좁히는 것입니다. Value Object, Entity, Service, Repository의 역할을 구분하면 코드 구조가 도메인 언어를 그대로 반영합니다.

다음 글에서는 객체지향을 피해야 할 때를 다룹니다. 함수, `dataclass`, 함수형 접근이 더 나은 상황을 실제 코드로 비교합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): 캡슐화](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): 상속](./04-inheritance.md)
- [Object-Oriented Programming 101 (5/10): 다형성](./05-polymorphism.md)
- [Object-Oriented Programming 101 (6/10): 추상화](./06-abstraction.md)
- [Object-Oriented Programming 101 (7/10): 합성과 상속](./07-composition-vs-inheritance.md)
- [Object-Oriented Programming 101 (8/10): SOLID 원칙 기초](./08-solid-principles.md)
- **Object-Oriented Programming 101 (9/10): 객체지향 설계 예제 (현재 글)**
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)

<!-- toc:end -->

## 참고 자료

- [Python dataclasses 공식 문서](https://docs.python.org/3/library/dataclasses.html)
- [typing.Protocol 공식 문서](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Refactoring — Martin Fowler](https://refactoring.com/)
- [Domain-Driven Design — Eric Evans](https://www.oreilly.com/library/view/domain-driven-design-tackling/0321125215/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 설계 예제, 리팩터링, 클래스 설계

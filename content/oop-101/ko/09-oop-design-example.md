---
title: 객체지향 설계 예제
series: oop-101
episode: 9
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
  - Python
  - OOP
  - 설계 예제
  - 리팩터링
  - 클래스 설계
last_reviewed: '2026-05-12'
seo_description: 온라인 서점 주문 시스템 예제로 OOP 설계와 리팩터링 과정을 단계별로 보여줍니다.
---

# 객체지향 설계 예제

개념을 따로 배울 때는 캡슐화, 상속, 다형성, 합성, SOLID가 각각 이해되는 듯 보입니다. 그런데 실제 기능 하나를 설계하려고 하면 갑자기 어려워집니다. 어디서 클래스를 나누고, 어떤 규칙은 지금 적용하고 어떤 규칙은 나중으로 미뤄야 할지 판단이 필요해지기 때문입니다.

그래서 실전 예제가 중요합니다. 좋은 설계는 처음부터 완벽한 다이어그램을 그려서 나오기보다, 동작하는 모델을 만들고 변경 가능성이 큰 지점에 유연성을 추가하면서 점점 다듬어집니다. 이 글에서는 그 흐름을 주문 시스템 예제로 따라가 보겠습니다.

이 글은 OOP 101 시리즈의 9번째 글입니다.

## 이 글에서 다룰 문제

> 실전 객체지향 설계의 핵심은 원칙을 많이 아는 데 있지 않습니다. 변경이 예상되는 경계에만 적절한 유연성을 두는 데 있습니다.

- 요구사항에서 어떤 클래스를 도출하고, 어떤 책임을 어디에 둘지 어떻게 판단할까요?
- 값 객체, 엔티티, 서비스 클래스는 어떤 식으로 역할을 나누면 좋을까요?
- 할인 정책, 결제 수단, 저장소처럼 바뀌기 쉬운 요소는 어떻게 분리해야 할까요?
- 절차지향 주문 처리 코드를 객체지향 구조로 옮길 때 무엇부터 분리하는 편이 안전할까요?

## 핵심 개념 잡기

> 온라인 서점 주문 시스템 구조

```text
OrderService
├── Cart          -> cart management
├── Discount      -> discount policy (strategy pattern)
├── PaymentGateway -> payment processing (DIP)
└── OrderRepository -> order persistence (DIP)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 도메인 모델 | 비즈니스 개념을 클래스로 표현한 것입니다 |
| 서비스 클래스 | 도메인 객체 간의 협력을 조율하는 클래스입니다 |
| 값 객체(value object) | 동등성으로 비교되는 불변 객체입니다 |
| 엔티티(entity) | 고유 식별자로 구분되는 객체입니다 |
| 리팩터링 | 동작을 유지하면서 코드 구조를 개선하는 것입니다 |

## 전후 비교

주문 처리 로직을 비교합니다.

```python
# before: procedural — all logic in a single function
def process_order(items, payment_type, discount_code):
    total = sum(item["price"] * item["qty"] for item in items)
    if discount_code == "SAVE10":
        total = int(total * 0.9)
    if payment_type == "card":
        print(f"Card payment: ${total}")
    elif payment_type == "bank":
        print(f"Bank transfer: ${total}")
    print(f"Order saved: ${total}, {len(items)} items")
```

```python
# after: OOP — responsibilities separated
class Order:
    def __init__(self, items: list["OrderItem"]) -> None:
        self.items = items

    @property
    def subtotal(self) -> int:
        return sum(item.total for item in self.items)

class OrderItem:
    def __init__(self, name: str, price: int, quantity: int) -> None:
        self.name = name
        self.price = price
        self.quantity = quantity

    @property
    def total(self) -> int:
        return self.price * self.quantity
```

## 단계별 실습

### 1단계: 도메인 모델 정의

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """Value object — represents monetary amounts"""
    amount: int

    def __add__(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)

    def __mul__(self, factor: int) -> "Money":
        return Money(self.amount * factor)

    def apply_discount(self, percent: int) -> "Money":
        return Money(self.amount - (self.amount * percent // 100))


@dataclass
class Book:
    """Entity — identified by unique ID"""
    book_id: str
    title: str
    price: Money

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self.book_id == other.book_id


book = Book("B001", "Python Basics", Money(25000))
print(book.price.amount)  # 25000
print((book.price * 3).amount)  # 75000
```

### 2단계: 장바구니 클래스

```python
@dataclass
class CartItem:
    book: Book
    quantity: int

    @property
    def total(self) -> Money:
        return self.book.price * self.quantity


class Cart:
    def __init__(self) -> None:
        self._items: dict[str, CartItem] = {}

    def add(self, book: Book, quantity: int = 1) -> None:
        if book.book_id in self._items:
            existing = self._items[book.book_id]
            self._items[book.book_id] = CartItem(book, existing.quantity + quantity)
        else:
            self._items[book.book_id] = CartItem(book, quantity)

    def remove(self, book_id: str) -> None:
        self._items.pop(book_id, None)

    @property
    def items(self) -> list[CartItem]:
        return list(self._items.values())

    @property
    def subtotal(self) -> Money:
        total = Money(0)
        for item in self._items.values():
            total = total + item.total
        return total

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self._items.values())


cart = Cart()
cart.add(Book("B001", "Python Basics", Money(25000)), 2)
cart.add(Book("B002", "Django in Practice", Money(35000)))
print(f"Subtotal: ${cart.subtotal.amount}, {cart.item_count} books")
# Subtotal: $85000, 3 books
```

### 3단계: 할인 정책 — 전략 패턴

```python
from typing import Protocol


class DiscountPolicy(Protocol):
    def calculate(self, subtotal: Money) -> Money: ...


class NoDiscount:
    def calculate(self, subtotal: Money) -> Money:
        return subtotal

class PercentDiscount:
    def __init__(self, percent: int) -> None:
        self._percent = percent

    def calculate(self, subtotal: Money) -> Money:
        return subtotal.apply_discount(self._percent)

class BulkDiscount:
    """10% off for orders over $50,000"""
    def calculate(self, subtotal: Money) -> Money:
        if subtotal.amount >= 50000:
            return subtotal.apply_discount(10)
        return subtotal


print(NoDiscount().calculate(Money(85000)).amount)       # 85000
print(PercentDiscount(20).calculate(Money(85000)).amount) # 68000
print(BulkDiscount().calculate(Money(85000)).amount)      # 76500
```

### 4단계: 결제 게이트웨이 — DIP

```python
from typing import Protocol


class PaymentGateway(Protocol):
    def charge(self, amount: Money) -> bool: ...


class CardPayment:
    def charge(self, amount: Money) -> bool:
        print(f"Card payment: ${amount.amount}")
        return True

class BankTransfer:
    def charge(self, amount: Money) -> bool:
        print(f"Bank transfer: ${amount.amount}")
        return True


class OrderRepository(Protocol):
    def save(self, order_data: dict) -> str: ...


class InMemoryOrderRepo:
    def __init__(self) -> None:
        self._orders: dict[str, dict] = {}
        self._counter = 0

    def save(self, order_data: dict) -> str:
        self._counter += 1
        order_id = f"ORD-{self._counter:04d}"
        self._orders[order_id] = order_data
        print(f"Order saved: {order_id}")
        return order_id
```

### 5단계: 주문 서비스 — 전체 조립

```python
class OrderService:
    def __init__(
        self,
        discount: DiscountPolicy,
        payment: PaymentGateway,
        repo: OrderRepository,
    ) -> None:
        self._discount = discount
        self._payment = payment
        self._repo = repo

    def checkout(self, cart: Cart) -> str | None:
        if cart.item_count == 0:
            print("Cart is empty")
            return None

        subtotal = cart.subtotal
        final = self._discount.calculate(subtotal)

        success = self._payment.charge(final)
        if not success:
            print("Payment failed")
            return None

        order_data = {
            "items": [(i.book.title, i.quantity) for i in cart.items],
            "subtotal": subtotal.amount,
            "total": final.amount,
        }
        return self._repo.save(order_data)


# Assembly and execution
cart = Cart()
cart.add(Book("B001", "Python Basics", Money(25000)), 2)
cart.add(Book("B002", "Django in Practice", Money(35000)))

service = OrderService(
    discount=BulkDiscount(),
    payment=CardPayment(),
    repo=InMemoryOrderRepo(),
)

order_id = service.checkout(cart)
# Card payment: $76500
# Order saved: ORD-0001
print(f"Order complete: {order_id}")  # Order complete: ORD-0001
```

## 이 코드에서 주목할 점

- `Money`는 값 객체로 금액 연산을 안전하게 캡슐화합니다
- `Cart`는 내부 딕셔너리를 숨기고 메서드로만 접근하게 합니다(캡슐화)
- `DiscountPolicy`는 전략 패턴으로 할인 정책을 런타임에 교체합니다(OCP)
- `OrderService`는 모든 의존성을 Protocol로 받아 교체와 테스트가 쉽습니다(DIP)

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 도메인 로직을 서비스에 넣음 | 모델이 빈껍데기(빈혈 도메인 모델)가 됩니다 | 비즈니스 로직은 도메인 모델에 넣습니다 |
| 모든 것을 한 번에 설계 | 과도한 추상화로 시작합니다 | 간단하게 시작하고 필요할 때 리팩터링합니다 |
| 값 객체를 가변으로 만듦 | 공유 참조 시 예기치 않은 변경입니다 | `frozen=True` 또는 읽기 전용으로 만듭니다 |
| 순환 의존성 | A가 B를, B가 A를 참조합니다 | 인터페이스를 분리하여 의존 방향을 통일합니다 |
| 테스트 없이 리팩터링 | 동작이 바뀌어도 알 수 없습니다 | 리팩터링 전 테스트를 작성합니다 |

## 실무에서 이렇게 쓰입니다

- 이커머스 플랫폼에서 장바구니, 결제, 할인을 분리 설계합니다
- 도메인 주도 설계(DDD)에서 엔티티와 값 객체 패턴을 활용합니다
- 결제 게이트웨이 교체(PG사 변경)를 Protocol로 대응합니다
- 마이크로서비스에서 각 서비스의 도메인 모델을 독립적으로 설계합니다
- A/B 테스트에서 할인 정책을 전략 패턴으로 교체합니다

## 현업 개발자는 이렇게 생각합니다

좋은 설계의 핵심은 "변경이 예상되는 곳에 유연성을 두는 것"입니다. 할인 정책이 자주 바뀔 것이라면 전략 패턴으로, 결제 수단이 추가될 것이라면 DIP로 대비합니다.

처음부터 모든 것을 완벽하게 설계하려 하지 마세요. 동작하는 간단한 코드를 먼저 작성하고, 중복이나 결합도가 문제가 될 때 원칙을 적용하여 리팩터링하는 것이 실무적 접근입니다.

## 체크리스트

- [ ] 요구사항에서 클래스를 도출할 수 있다
- [ ] 값 객체와 엔티티를 구분하여 설계할 수 있다
- [ ] 합성과 DIP로 클래스 간 결합도를 낮출 수 있다
- [ ] 전략 패턴으로 교체 가능한 정책을 설계할 수 있다
- [ ] 절차지향 코드를 객체지향으로 리팩터링할 수 있다

## 정리 및 다음 글 안내

실전 설계에서는 단일 원칙이 아니라 여러 OOP 원칙이 함께 적용됩니다. 간단하게 시작하고, 변경이 필요할 때 점진적으로 개선하는 것이 현실적인 접근입니다. 다음 글에서는 객체지향을 언제 사용하지 말아야 하는지 알아봅니다.

<!-- toc:begin -->
- [객체지향이란 무엇인가?](./01-what-is-oop.md)
- [클래스와 인스턴스](./02-classes-and-instances.md)
- [캡슐화](./03-encapsulation.md)
- [상속](./04-inheritance.md)
- [다형성](./05-polymorphism.md)
- [추상화](./06-abstraction.md)
- [합성과 상속](./07-composition-vs-inheritance.md)
- [SOLID 원칙 기초](./08-solid-principles.md)
- **객체지향 설계 예제 (현재 글)**
- 객체지향을 언제 피해야 할까? (예정)
<!-- toc:end -->

## 참고 자료

- [Domain-Driven Design — Eric Evans](https://www.oreilly.com/library/view/domain-driven-design/0321125215/)
- [Clean Code — Robert C. Martin](https://www.oreilly.com/library/view/clean-code/9780136083238/)
- [Refactoring — Martin Fowler](https://refactoring.com/)
- [Python Patterns — Brandon Rhodes](https://python-patterns.guide/)

Tags: Python, OOP, 설계 예제, 리팩터링, 클래스 설계

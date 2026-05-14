---
series: oop-101
episode: 9
title: OOP Design Example
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Python
  - OOP
  - Design Example
  - Refactoring
  - Class Design
seo_description: Apply OOP principles to a real-world online bookstore order system with step-by-step class design and refactoring.
last_reviewed: '2026-05-04'
---

# OOP Design Example

This is post 9 in the Object-Oriented Programming 101 series.

> Object-Oriented Programming 101 Series (9/10)

<!-- a-grade-intro:begin -->

**Key Question**: How do you integrate OOP principles into a real project?

> Theory alone does not produce good design. This article incrementally designs an online bookstore order system, applying encapsulation, inheritance, polymorphism, composition, and SOLID principles in practice.

<!-- a-grade-intro:end -->

## What You Will Learn

- How to derive classes from requirements
- Responsibility separation and class collaboration design
- Flexible architecture using composition and dependency injection
- Procedural-to-OOP refactoring process

## Why It Matters

The hardest part of class design in practice is "where to draw the boundaries." Too many responsibilities in one class makes change difficult; too many tiny classes adds complexity. Real examples build intuition for finding the right balance.

> Good design = proper boundaries + clear responsibilities + loose coupling

Design is never completed in one pass. Start simple, then refactor when requirements change — this is the realistic approach.

## Concept Overview

> Online bookstore order system structure

```text
OrderService
├── Cart          -> cart management
├── Discount      -> discount policy (strategy pattern)
├── PaymentGateway -> payment processing (DIP)
└── OrderRepository -> order persistence (DIP)
```

## Key Concepts

| Term | Description |
|------|-------------|
| Domain model | Business concepts expressed as classes |
| Service class | A class that orchestrates collaboration between domain objects |
| Value object | An immutable object compared by value equality |
| Entity | An object identified by a unique identifier |
| Refactoring | Improving code structure while preserving behavior |

## Before / After

Comparing order processing logic.

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

## Hands-On Steps

### Step 1: Define Domain Models

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

### Step 2: Cart Class

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

### Step 3: Discount Policy — Strategy Pattern

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

### Step 4: Payment Gateway — DIP

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

### Step 5: Order Service — Full Assembly

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

## What to Notice in This Code

- `Money` is a value object that safely encapsulates monetary operations
- `Cart` hides its internal dictionary and exposes access only through methods (encapsulation)
- `DiscountPolicy` uses the strategy pattern for runtime-swappable discount policies (OCP)
- `OrderService` receives all dependencies as Protocols, making replacement and testing easy (DIP)

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Putting domain logic in services | Models become empty shells (anemic domain model) | Place business logic in domain models |
| Designing everything upfront | Starts with over-abstraction | Start simple; refactor when needed |
| Making value objects mutable | Unexpected changes via shared references | Use `frozen=True` or read-only properties |
| Circular dependencies | A references B and B references A | Separate interfaces to unify dependency direction |
| Refactoring without tests | Cannot detect behavioral changes | Write tests before refactoring |

## Real-World Applications

- E-commerce platforms separate cart, payment, and discount design
- Domain-Driven Design (DDD) uses entity and value object patterns
- Payment gateway swaps (PG provider changes) are handled via Protocol
- Microservices design each service's domain model independently
- A/B tests swap discount policies using the strategy pattern

## How Senior Engineers Think About This

The core of good design is "placing flexibility where change is expected." If discount policies change frequently, use the strategy pattern. If payment methods will be added, prepare with DIP.

Do not try to design everything perfectly from the start. Write simple working code first, then apply principles and refactor when duplication or coupling becomes a problem. This is the practical approach.

## Checklist

- [ ] I can derive classes from requirements
- [ ] I can distinguish and design value objects and entities
- [ ] I can reduce coupling between classes using composition and DIP
- [ ] I can design swappable policies with the strategy pattern
- [ ] I can refactor procedural code into object-oriented code

## Exercises

1. Add a `CouponDiscount` (fixed-amount discount) to the order system without modifying existing code.
2. Implement a `JsonFileOrderRepo` that saves orders to a JSON file as an `OrderRepository` implementation.
3. Design a library loan system: implement `Book`, `Member`, `Loan`, and `LoanService` classes.

## Summary and Next Steps

Real-world design applies multiple OOP principles together, not in isolation. Start simple and improve incrementally when change demands it — this is the realistic approach. In the next article, we explore when you should not use object-oriented programming.

<!-- toc:begin -->
- [What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Classes and Instances](./02-classes-and-instances.md)
- [Encapsulation](./03-encapsulation.md)
- [Inheritance](./04-inheritance.md)
- [Polymorphism](./05-polymorphism.md)
- [Abstraction](./06-abstraction.md)
- [Composition vs Inheritance](./07-composition-vs-inheritance.md)
- [SOLID Principles Basics](./08-solid-principles.md)
- **OOP Design Example (current)**
- [When to Avoid OOP](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## References

- [Domain-Driven Design — Eric Evans](https://www.oreilly.com/library/view/domain-driven-design/0321125215/)
- [Clean Code — Robert C. Martin](https://www.oreilly.com/library/view/clean-code/9780136083238/)
- [Refactoring — Martin Fowler](https://refactoring.com/)
- [Python Patterns — Brandon Rhodes](https://python-patterns.guide/)

Tags: Python, OOP, Design Example, Refactoring, Class Design

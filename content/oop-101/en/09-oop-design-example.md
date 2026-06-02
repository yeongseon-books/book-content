---
series: oop-101
episode: 9
title: "Object-Oriented Programming 101 (9/10): OOP Design Example"
status: publish-ready
targets:
  tistory: false
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
last_reviewed: '2026-05-15'
---

# Object-Oriented Programming 101 (9/10): OOP Design Example

This is the 9th post in the Object-Oriented Programming 101 series.

> Object-Oriented Programming 101 Series (9/10)

**Key Question**: How do you integrate OOP principles into a real project?

> Theory alone does not produce good design. This article incrementally designs an online bookstore order system, applying encapsulation, inheritance, polymorphism, composition, and SOLID principles in practice.


![Object-Oriented Programming 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/09/09-01-concept-overview.en.png)
*Object-Oriented Programming 101 chapter 9 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying OOP Design Example?
- Which signal should the example or diagram make visible for OOP Design Example?
- What failure should be prevented first when OOP Design Example reaches a real system?

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

## Where This Design Usually Breaks First in Production

| Weak spot | Typical symptom | What to tighten first |
|-----------|-----------------|-----------------------|
| Payment gateway integration | Charge failures and save failures get mixed into one retry path | Split payment result handling from persistence and make the order outcome explicit |
| Discount policy growth | Checkout logic turns into a branching block inside the service | Keep policies as objects and move composition rules into a factory or rule layer |
| Repository implementation | Tests are fast, but real DB transactions behave differently | Keep the repository contract stable and make transaction boundaries explicit |
| Cart model | Quantity updates, stock checks, and coupon rules pile into one class | Separate state mutation from validation and move stock checks into a collaborator |

## A Safer Refactoring Order

1. Freeze the current procedural flow with tests first.
2. Move pure calculations into value objects such as `Money`.
3. Push payment and persistence behind Protocol boundaries only after the calculations are stable.
4. Keep final assembly in one place so that domain objects do not learn about framework or infrastructure details.

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

## Anchoring the Design with Text UML Before Coding

If you fix the collaboration structure in text UML before writing code, responsibility boundaries stay stable during refactoring.

```text
[TicketController]
    |
    v
[TicketService]
  + create_ticket()
  + close_ticket()
    |
    +--> [TicketRepository]
    +--> [AssignmentPolicy]
    +--> [NotificationPort]

[Ticket]
  - id
  - status
  - assignee
  + assign_to()
  + close()
```

## Before/After: Decomposing a Monolithic Service Method

```python
# before

def create_ticket(payload: dict, db, slack_client):
    # parsing, validation, assignee selection, persistence, notification all mixed
    ...
```

```python
# after
from dataclasses import dataclass

@dataclass
class Ticket:
    id: str
    title: str
    status: str = 'open'
    assignee: str | None = None

    def assign_to(self, engineer: str) -> None:
        if self.status != 'open':
            raise ValueError('only open ticket can be assigned')
        self.assignee = engineer

    def close(self) -> None:
        if self.status == 'closed':
            raise ValueError('already closed')
        self.status = 'closed'

class RoundRobinAssignmentPolicy:
    def __init__(self, members: list[str]) -> None:
        self.members = members
        self._index = 0

    def pick(self) -> str:
        engineer = self.members[self._index % len(self.members)]
        self._index += 1
        return engineer
```

## Violations and Corrections

| Violation | Operational Problem | Correction |
|---|---|---|
| Controller directly modifies domain state transitions | Inconsistent rules across API endpoints | Unify state transitions through domain methods |
| Policy hard-coded in service | Difficult to experiment or replace | Inject policy objects |
| Notification failure coupled to transaction | Core functionality rolls back unnecessarily | Separate via outbox/async notification |

## Comparison: Before vs After Refactoring

| Aspect | Before Refactoring | After Refactoring |
|---|---|---|
| Code navigation | Tracing inside one function | Navigating by object boundaries |
| Testing | Depends on integration tests | Domain-level unit tests possible |
| Change response | Frequent merge conflicts | Reduced blast radius |

## Real Scenario: Building a Change-Resilient Structure

In practice, rule changes happen more often than feature additions. Therefore, when evaluating class structure, "how far does the next change reach?" is a safer criterion than "does it work now?"

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

This code never needs to edit `Invoice.total()` when discount rules change. Extension is closed by adding implementation classes, and the core flow stays stable.

## UML View of the Collaboration

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

Writing the collaboration structure in text UML like this lets code reviews quickly agree on "where is the policy axis and where is the domain axis."

## Anti-Patterns and Correction Steps

| Anti-Pattern | Detection Signal | Correction Sequence |
|---|---|---|
| God Object | 20+ methods, change history scattered across concerns | Decompose by responsibility axis → extract collaboration interfaces |
| Data-only empty class | Only getters/setters, no methods | Move rule methods in, or simplify to dataclass |
| Inheritance tree bypass branching | Type-checking branches for subclass types | Redefine polymorphic contract |
| Infrastructure type leakage | Domain layer depends on SDK response objects | Add DTO translation layer |

## Before/After: Test Maintenance Cost

| Aspect | Before Refactoring | After Refactoring |
|---|---|---|
| Test setup | Requires global state initialization | Object-level state creation |
| Failure root-cause tracing | Backtrack entire function chain | Trace at class method level |
| Regression scope | Broad and unclear | Narrow and predictable |

## Team Adoption Checklist

- Verify that domain terms match class names.
- Confirm that invariants are established at instance creation time.
- Check that policy changes are possible via new implementations, not existing code edits.
- In code review, agree on collaboration structure with 10 lines of UML text first.
- Ensure test names describe business rules rather than method names.

## Mini Case Study: Verify with One Rule Addition

The following example demonstrates the smallest unit of policy extension that lands without touching existing code.

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

The key observation is that the new policy enters without breaking the existing call path. Keeping the change boundary at the policy class means regression risk stays low.

| Verification Question | Pass Criterion |
|---|---|
| Does adding a new policy require editing existing functions? | No |
| Does the exception policy match the existing contract? | Yes |
| Are tests isolated per policy? | Yes |

## Refactoring Retrospective: Measuring Change Cost

- If modified files exceed 5 per feature, review boundary design.
- If type-branching `if/elif` accumulates to 3+, move to polymorphism or strategy objects.
- If writing regression tests takes longer than the implementation, revisit responsibility placement.

```python
def complexity_signal(changed_files: int, branch_count: int) -> str:
    if changed_files >= 5 or branch_count >= 3:
        return 'refactor-needed'
    return 'acceptable'
```

This is not a rigorous metric, but it helps teams discuss based on criteria rather than gut feel.

## Verification Notes: Questions for Reviewing Object Design Quality

These questions are used repeatedly in post-implementation reviews.

- Does the exception type and message match the caller's contract when this method fails?
- Is the same rule duplicated in another class or function?
- Does state mutation happen through exactly one method path?
- Can unit tests run without external dependencies?

```python
def review_signal(duplicate_rules: int, mutable_paths: int) -> str:
    if duplicate_rules > 0:
        return 'duplicate rule removal needed'
    if mutable_paths > 1:
        return 'state mutation path consolidation needed'
    return 'structure stable'
```

Applying these checks even to article-level examples helps understand OOP as a maintenance strategy rather than just syntax.

## One-Line Takeaway

OOP quality is judged not by the number of classes, but by how much the blast radius of change has been reduced.

## Design Note

Design choices are not about finding the right answer—they are decisions that lower the cost of change. Even for the same feature, defining boundaries first simplifies reviews and tests.


## Answering the Opening Questions

- **How do you derive classes from requirements and decide which responsibilities go where?**
  - This article started by separating cart, discount, payment, and persistence into a collaboration structure for an online bookstore order system, then assigned `OrderService` to assembly and flow, `Cart` to item management, and `Money` to monetary operations. The subsequent ticket example with `TicketService`, `AssignmentPolicy`, and `NotificationPort` UML further clarified that the criteria for class derivation are domain terms and axes of change.
- **How should value objects, entities, and service classes divide their roles?**
  - `Money` is an immutable value object with `__add__` and `apply_discount()` that holds rules about amounts themselves, while `Book` is an entity identified by `book_id`. `OrderService` does not substitute for either—it orchestrates the checkout flow by wiring collaborators like `BulkDiscount`, `CardPayment`, and `InMemoryOrderRepo`, showing that a service class is closer to an orchestrator than a rule repository.
- **How should frequently changing elements—discount policies, payment methods, repositories—be separated?**
  - The article pushed `DiscountPolicy`, `PaymentGateway`, and `OrderRepository` behind Protocol boundaries, placing `PercentDiscount`, `BulkDiscount`, `CardPayment`, `BankTransfer`, and `InMemoryOrderRepo` as swappable implementations. This way, when a PG switch or discount experiment occurs, core domain objects like `Cart` and `Money` remain untouched—only the assembly code swaps implementations.
<!-- toc:begin -->
## In this series

- [Object-Oriented Programming 101 (1/10): What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): Classes and Instances](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): Encapsulation](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): Inheritance](./04-inheritance.md)
- [Object-Oriented Programming 101 (5/10): Polymorphism](./05-polymorphism.md)
- [Object-Oriented Programming 101 (6/10): Abstraction](./06-abstraction.md)
- [Object-Oriented Programming 101 (7/10): Composition vs Inheritance](./07-composition-vs-inheritance.md)
- [Object-Oriented Programming 101 (8/10): SOLID Principles Basics](./08-solid-principles.md)
- **OOP Design Example (current)**
- When to Avoid OOP (upcoming)

<!-- toc:end -->

## References

- [Python Official Docs — dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Python Official Docs — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Refactoring — Martin Fowler](https://refactoring.com/)
- [Domain-Driven Design — Eric Evans](https://www.oreilly.com/library/view/domain-driven-design/0321125215/)

Tags: Python, OOP, Design Example, Refactoring, Class Design

---
series: design-patterns-101
episode: 3
title: "Design Patterns 101 (3/10): Structural Patterns"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - DesignPatterns
  - Structural
  - Adapter
  - Decorator
  - Facade
seo_description: How structural patterns use composition and delegation to connect objects without freezing the design too early.
last_reviewed: '2026-05-23'
---

# Design Patterns 101 (3/10): Structural Patterns

Once object creation is sorted out, the next wall is "how do I wire existing objects together?" In my experience the three situations where this wall appears most often are: connecting an external SDK to the domain, bolting logging or caching onto an existing object, and presenting a complex subsystem through a simple entry point. All three are assembly problems, and GoF grouped them under the name Structural patterns.

This is the 3rd post in the Design Patterns 101 series. It covers Adapter, Bridge, Composite, Decorator, Facade, Flyweight, and Proxy. Adapter gets a dedicated deep-dive in episode 6, so here it stays at overview level.

![Structural pattern responsibility boundaries](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/03/03-01-concept-at-a-glance.en.png)

*The boundary structural patterns create between caller and implementation*
> Structural patterns are about how classes and objects fit together, so a system can grow without rewiring every connection.

## Questions to Keep in Mind

- What concretely changes when composition replaces inheritance?
- Decorator and Proxy both "wrap" an object — when should each be chosen?
- What do structural patterns cost?

## Two Recurring Problems When Connecting Objects

Two problems show up repeatedly when designing structure.

**First, interface mismatch.** The method signature an external library exposes differs from the signature the domain expects. Translating at every call site scatters conversion logic across the codebase.

**Second, responsibility accumulation.** When cross-cutting concerns like logging, caching, access control, and lazy loading pile onto a single object, the class bloats. Inheritance leads to combinatorial explosion; conditionals lead to endless branching.

Structural patterns solve both problems through **composition**. They wrap, translate, or tree-compose objects so that the interface callers see stays stable while the internals remain swappable.

## Adapter and Facade Solve the Same Problem at Different Distances

Adapter translates **one interface** into another. Facade hides **multiple subsystems** behind a single simple entry point. Both aim to reduce what the caller needs to know, but they operate at different distances.

### Adapter: Contract Translation

Suppose a legacy payment SDK requires `execute_payment(merchant_id, cents, currency_code)`, but the domain expects `PaymentGateway.charge(order: Order)`.

```python
from typing import Protocol
from dataclasses import dataclass


@dataclass
class Order:
    merchant: str
    amount_cents: int
    currency: str


class PaymentGateway(Protocol):
    def charge(self, order: Order) -> str: ...


class LegacySDKAdapter:
    """Thin translation layer mapping the legacy SDK to the domain interface."""

    def __init__(self, sdk) -> None:
        self._sdk = sdk

    def charge(self, order: Order) -> str:
        return self._sdk.execute_payment(
            order.merchant, order.amount_cents, order.currency
        )
```

There is no business logic inside the Adapter — only signature translation. The moment business logic creeps in, the Adapter stops being a "translator" and becomes a "policy maker," making it harder to test and replace. Episode 6 explores this boundary in depth.

### Facade: Subsystem Simplification

If order processing requires inventory check, payment, shipping reservation, and notification, having the caller orchestrate four systems directly is a burden.

```python
class OrderFacade:
    def __init__(self, inventory, payment, shipping, notifier) -> None:
        self._inventory = inventory
        self._payment = payment
        self._shipping = shipping
        self._notifier = notifier

    def place_order(self, user_id: str, item_id: str, amount: int) -> str:
        self._inventory.reserve(item_id)
        tx_id = self._payment.charge(user_id, amount)
        tracking = self._shipping.schedule(user_id, item_id)
        self._notifier.send(user_id, f"Order confirmed: {tracking}")
        return tx_id
```

The trap with Facade is the temptation "it is convenient, so let us add more logic here." Once a Facade starts housing new business rules it becomes a God Object. A Facade should **orchestrate only**; decisions stay in the subsystems.

## Why Decorator Feels Natural in Python

Python has `@decorator` syntax built into the language, so GoF's Decorator pattern integrates more naturally than in most other languages. The core idea is the same: **wrap an object while preserving its interface, adding responsibility.**

Below is an example chaining logging, retry, and timing onto an HTTP client.

```python
from typing import Protocol
import time


class HttpClient(Protocol):
    def get(self, url: str) -> bytes: ...


class LoggingClient:
    def __init__(self, inner: HttpClient) -> None:
        self._inner = inner

    def get(self, url: str) -> bytes:
        print(f"[REQ] GET {url}")
        result = self._inner.get(url)
        print(f"[RES] {len(result)} bytes")
        return result


class RetryClient:
    def __init__(self, inner: HttpClient, max_retries: int = 3) -> None:
        self._inner = inner
        self._max_retries = max_retries

    def get(self, url: str) -> bytes:
        for attempt in range(self._max_retries):
            try:
                return self._inner.get(url)
            except OSError:
                if attempt == self._max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        raise RuntimeError("unreachable")


class TimingClient:
    def __init__(self, inner: HttpClient) -> None:
        self._inner = inner

    def get(self, url: str) -> bytes:
        start = time.perf_counter()
        result = self._inner.get(url)
        elapsed = time.perf_counter() - start
        print(f"[TIME] {url} -> {elapsed:.3f}s")
        return result
```

Assembly is one line.

```python
client = TimingClient(RetryClient(LoggingClient(RealHttpClient())))
```

Changing the order changes behavior. Placing `TimingClient` outermost measures total time including retries; placing it inside `RetryClient` measures individual attempt time. This order control is the key advantage of Decorator chaining — and simultaneously the reason debugging gets harder.

I recommend keeping Decorator chains to three layers or fewer. Beyond four, stack traces become painful to read.

## The One Thing to Evaluate Before Introducing Proxy

Proxy exposes the **same interface** as the real object while performing access control, caching, or lazy loading in front of it. It looks similar to Decorator, but the intent differs. Decorator "adds functionality"; Proxy "controls access."

The one thing to evaluate before introducing Proxy is **transparency**. The caller must not be aware it is using a Proxy. If the signature changes, exception types shift, or return-value semantics subtly differ, it is not a Proxy — it is a separate service.

```python
from typing import Protocol


class UserRepository(Protocol):
    def find(self, user_id: str) -> dict: ...


class CachedUserRepository:
    """Lazy-loading + cache Proxy."""

    def __init__(self, real: UserRepository) -> None:
        self._real = real
        self._cache: dict[str, dict] = {}

    def find(self, user_id: str) -> dict:
        if user_id not in self._cache:
            self._cache[user_id] = self._real.find(user_id)
        return self._cache[user_id]
```

From the caller's perspective this Proxy behaves identically to `UserRepository`. Add a cache-invalidation policy and it is production-ready.

## Why Composite Shines Only in Tree Structures

Composite lets single objects and collections of objects be treated through the **same interface**. File-system files/folders, UI widgets/containers, and menu items/submenus are textbook examples.

```python
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class MenuItem:
    name: str
    price: int

    def total(self) -> int:
        return self.price

    def display(self, indent: int = 0) -> str:
        return f"{'  ' * indent}{self.name}: ${self.price / 100:.2f}"


@dataclass
class Menu:
    name: str
    children: list[MenuItem | Menu] = field(default_factory=list)

    def total(self) -> int:
        return sum(child.total() for child in self.children)

    def display(self, indent: int = 0) -> str:
        lines = [f"{'  ' * indent}[{self.name}]"]
        for child in self.children:
            lines.append(child.display(indent + 1))
        return "\n".join(lines)
```

```python
lunch = Menu("Lunch Set", [
    MenuItem("Soup", 800),
    MenuItem("Rice", 200),
    Menu("Sides", [
        MenuItem("Egg Roll", 350),
        MenuItem("Kimchi", 0),
    ]),
])

print(lunch.display())
print(f"Total: ${lunch.total() / 100:.2f}")
```

Output:

```text
[Lunch Set]
  Soup: $8.00
  Rice: $2.00
  [Sides]
    Egg Roll: $3.50
    Kimchi: $0.00
Total: $13.50
```

The condition under which Composite shines is clear: **the data is actually tree-shaped.** If the data is a graph or a flat list and Composite is forced onto it, parent-child relationships must be manufactured and the model becomes unnatural.

## Bridge and Flyweight: Rarely Used but Worth Knowing

### Bridge

Bridge separates abstraction from implementation so each can evolve independently. When "Shape" and "Renderer" each need to grow independently, inheritance produces `CircleSVGRenderer`, `CircleCanvasRenderer`, `RectSVGRenderer`... — combinatorial explosion. Bridge splits the two axes.

```python
class Renderer(Protocol):
    def render_circle(self, x: int, y: int, radius: int) -> str: ...

class SVGRenderer:
    def render_circle(self, x: int, y: int, radius: int) -> str:
        return f'<circle cx="{x}" cy="{y}" r="{radius}"/>'

class Shape:
    def __init__(self, renderer: Renderer) -> None:
        self._renderer = renderer

    def draw(self) -> str:
        raise NotImplementedError

class Circle(Shape):
    def __init__(self, renderer: Renderer, x: int, y: int, radius: int) -> None:
        super().__init__(renderer)
        self._x, self._y, self._radius = x, y, radius

    def draw(self) -> str:
        return self._renderer.render_circle(self._x, self._y, self._radius)
```

Explicitly introducing Bridge in production is rare. But DB driver abstractions (`sqlalchemy.Engine` + each dialect) and logging handlers (`logging.Handler` + each output target) already use Bridge structure under the hood.

### Flyweight

Flyweight saves memory when large numbers of similar objects consume too much of it, by separating shared state (intrinsic) from per-instance state (extrinsic). Thousands of bullets in a game sharing the same texture, or a text editor reusing the same glyph objects, are classic examples.

In Python, `__slots__`, string interning (`sys.intern`), and `functools.lru_cache` already embody the Flyweight spirit, so explicitly implementing the pattern is uncommon.

## The Cost Each Pattern Demands

Patterns are not free. Knowing what is lost before introducing one matters.

| Pattern | Gained | Lost |
| --- | --- | --- |
| Adapter | Interface compatibility, easy replacement | One extra indirection layer, possible translation bugs |
| Bridge | Independent extension of abstraction/implementation | Higher initial design complexity |
| Composite | Uniform tree traversal | Blurred leaf/container distinction |
| Decorator | Dynamic responsibility addition, free combination | Complex stack traces, order dependence |
| Facade | Caller simplification | Harder access to subsystem details |
| Flyweight | Memory savings | Complex state-separation logic, thread-safety concerns |
| Proxy | Access control, caching, lazy loading | Cache invalidation complexity, harder real-object tracing during debugging |

I recommend that whenever a team introduces a structural pattern, they write one sentence answering "is what this pattern costs less than the cost of the current problem?" If the sentence cannot be written, it is not yet time to introduce the pattern.

## Answering the Opening Questions

- **What concretely changes when composition replaces inheritance?**
  - The interface stays stable while only the implementation swaps. The Adapter wrapping a legacy SDK without touching a single line of domain code, and the Decorator chain whose behavior changes just by reordering layers — both are composition's flexibility in action. With inheritance, the entire class hierarchy would need redesigning.

- **Decorator and Proxy both "wrap" an object — when should each be chosen?**
  - Distinguish by intent. "Add functionality" means Decorator; "control access" means Proxy. `TimingClient` added measurement as functionality, so it is a Decorator. `CachedUserRepository` controlled actual DB access (lazy + cache), so it is a Proxy. The implementation shape is similar, but using distinct names communicates intent clearly in code review.

- **What do structural patterns cost?**
  - Indirection increases, and during debugging it takes one or two extra hops to find where behavior actually lives. As the cost table showed, Decorator complicates stack traces, Facade obscures subsystem details, and Proxy makes cache invalidation harder. A pattern is worth introducing only when that cost is smaller than the pain of the current structural problem.

<!-- toc:begin -->
## Series Table of Contents

- [What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Creational Patterns](./02-creational-patterns.md)
- **Structural Patterns (current)**
- Behavioral Patterns (upcoming)
- Strategy Pattern (upcoming)
- Adapter Pattern (upcoming)
- Observer Pattern (upcoming)
- Factory and Dependency Injection (upcoming)
- When Not to Use Patterns (upcoming)
- Patterns That Suit Python (upcoming)

<!-- toc:end -->

## References

### Core References

- [Design Patterns: Elements of Reusable Object-Oriented Software (GoF)](https://en.wikipedia.org/wiki/Design_Patterns)
- [Adapter Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/adapter)
- [Decorator Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/decorator)
- [Facade Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/facade)
- [Composite Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/composite)
- [Proxy Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/proxy)

### Practical Extensions

- [Python typing — Protocol (Python docs)](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Head First Design Patterns — Structural Patterns](https://www.oreilly.com/library/view/head-first-design/9781492077992/)
- [Example code for this series (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/en)

Tags: Computer Science, DesignPatterns, Structural, Adapter, Decorator, Facade

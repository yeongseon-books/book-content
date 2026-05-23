---
series: design-patterns-101
episode: 10
title: "Design Patterns 101 (10/10): Pythonic Patterns"
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
  - Python
  - Idioms
  - Protocols
  - Decorators
seo_description: How Python modules, functions, Protocols, and decorators express classic pattern intent with less ceremony than direct GoF translations.
last_reviewed: '2026-05-23'
---

# Design Patterns 101 (10/10): Pythonic Patterns

When the GoF book appeared in 1994, its authors worked primarily in C++ and Smalltalk. Java later became the de facto language for pattern education, and many developers unconsciously absorbed the idea that patterns mean "class hierarchies." The first time I implemented Strategy in Python, I created an ABC and three concrete classes — then a colleague asked in code review, "Why not just pass a function?" That was the moment I internalized that when the language changes, the expression of a pattern must change with it.

This is the final article in the Design Patterns 101 series. It closes with a single question that runs through the entire series: **How lightly can we express GoF pattern intent using tools Python already provides?** And when is that lightness inappropriate?

![Design Patterns 101 chapter 10 concept overview](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/10/10-01-concept-at-a-glance.en.png)

*Transition flow from GoF class structures to Python-native expressions*

## Questions to Keep in Mind

- When implementing Singleton as a class in Python, what problems arise — and what new problems appear when replacing it with a module variable?
- What do we lose when expressing Strategy or Command as plain functions instead of classes?
- In which situations is the full GoF class structure still the better choice in Python?

## Why It Matters That GoF Originated in a Java Context

A significant number of the 23 GoF patterns exist to work around language limitations. Java had no first-class functions, so Strategy required an interface plus implementation classes. Java had no module concept, so Singleton needed a `private` constructor. C++ had no garbage collector, so Creational patterns that explicitly separated object creation and destruction were more urgent.

Python lacks most of these constraints.

| Language constraint (Java/C++) | Python alternative |
| --- | --- |
| Cannot pass functions as values | First-class functions, `Callable` type hint |
| No mechanism to enforce a single global instance | Modules load exactly once |
| No polymorphism without interfaces | Duck typing + `Protocol` |
| Adding behavior to objects requires inheritance | `@` decorator syntax |
| Separate class needed for iterators | A single `yield` produces an Iterator |

The takeaway is simple: **pattern intent remains valid, but expression must adapt to the language.** Transplanting Java-style class hierarchies into Python means re-solving problems the language already solved.

## Singleton Replaced by a Module Variable — and When It Cannot Be

### Before: Traditional Singleton Class

```python
import threading

class AppConfig:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._loaded = False
        return cls._instance

    def load(self, path: str) -> None:
        # Load configuration file
        self._loaded = True
```

Double-checked locking alone takes over ten lines. But there is a more serious problem: tests have no way to reset the instance. Adding a `reset()` method risks accidental production calls; omitting it breaks test isolation.

### After: Module Variable

```python
# config.py
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class _Config:
    env: str
    db_url: str
    debug: bool

config = _Config(
    env=os.environ.get("APP_ENV", "dev"),
    db_url=os.environ.get("DB_URL", "sqlite:///local.db"),
    debug=os.environ.get("DEBUG", "0") == "1",
)
```

```python
# Consumer side
from config import config

def connect_db():
    return create_engine(config.db_url)
```

Python's import system executes a module exactly once. The result is cached in `sys.modules`, so every import receives the same object. Thread safety is guaranteed by the import lock. In tests, `monkeypatch` or `unittest.mock.patch` replaces the `config` object cleanly.

### When a Module Variable Is Not Enough

Module variables are not a universal solution. The following situations still call for a class-based approach:

- **Lazy initialization is mandatory**: If opening an external service connection at module-load time causes side effects on import, a factory that controls instantiation timing is preferable.
- **Configuration must be swapped at runtime**: A `frozen=True` dataclass is immutable; if hot-reload is needed, a mutable object or a dedicated reload mechanism is required.
- **The framework demands a class instance**: Django's `AppConfig`, Flask's `app` object — some frameworks assume class-based singletons by design.

## Strategy as Functions — What We Gain and What We Lose

### Before: ABC-Based Strategy

```python
from abc import ABC, abstractmethod
from decimal import Decimal

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, order: "Order") -> Decimal:
        ...

class NoDiscount(DiscountStrategy):
    def calculate(self, order: "Order") -> Decimal:
        return Decimal("0")

class BulkDiscount(DiscountStrategy):
    def calculate(self, order: "Order") -> Decimal:
        if order.quantity >= 100:
            return order.subtotal * Decimal("0.1")
        return Decimal("0")

class VIPDiscount(DiscountStrategy):
    def calculate(self, order: "Order") -> Decimal:
        return order.subtotal * Decimal("0.15")
```

One ABC, three implementation classes. Each class contains exactly one method.

### After: Function-Based Strategy

```python
from decimal import Decimal
from typing import Callable

type DiscountFn = Callable[["Order"], Decimal]

def no_discount(order: "Order") -> Decimal:
    return Decimal("0")

def bulk_discount(order: "Order") -> Decimal:
    if order.quantity >= 100:
        return order.subtotal * Decimal("0.1")
    return Decimal("0")

def vip_discount(order: "Order") -> Decimal:
    return order.subtotal * Decimal("0.15")

def apply_discount(order: "Order", strategy: DiscountFn) -> Decimal:
    return strategy(order)
```

A `type` statement (3.12+) or `TypeAlias` makes the signature explicit so the type checker catches incorrect function arguments.

### What We Gain

- Three classes become three functions. Boilerplate disappears.
- `functools.partial` binds parameters to create new strategies in a single line.
- Tests can stub with a one-line lambda.

### What We Lose

- **Stateful strategies**: A strategy that accumulates discount history or holds an external service client is awkward as a bare function. Closures can wrap state, but once state grows complex, a class reads more clearly.
- **Multi-method strategies**: When `calculate` must be accompanied by `describe` and `validate`, a single function is insufficient.
- **Framework integration**: If a DI container assumes class-based registration, forcing functions in creates more friction than it removes.

My default rule: "If the strategy has one method and no state, use a function. Two or more methods — use a class."

## Command as a Callable

The core of GoF Command is "encapsulate a request as an object so it can be queued or undone." In Python, anything callable is already a Command.

```python
from functools import partial

def send_email(to: str, subject: str, body: str) -> None:
    print(f"Sending to {to}: {subject}")

def delete_file(path: str) -> None:
    print(f"Deleting {path}")

# Command queue: a list of callables
command_queue: list[partial] = [
    partial(send_email, "admin@ex.com", "Report", "Monthly stats"),
    partial(delete_file, "/tmp/old_report.csv"),
]

# Execute
for cmd in command_queue:
    cmd()
```

`partial` creates a callable with pre-bound arguments. Queuing, serializing, and deferred execution all feel natural. When undo is needed, extend with `(do, undo)` tuples:

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class UndoableCommand:
    execute: Callable[[], None]
    undo: Callable[[], None]

history: list[UndoableCommand] = []

def do(cmd: UndoableCommand) -> None:
    cmd.execute()
    history.append(cmd)

def undo_last() -> None:
    if history:
        history.pop().undo()
```

Even with undo support, a dataclass plus callables suffices — no class hierarchy required.

## Observer as Callback Lists and Signals

### Before: GoF Observer Classes

```python
from abc import ABC, abstractmethod

class Subject:
    def __init__(self):
        self._observers: list["Observer"] = []

    def attach(self, obs: "Observer") -> None:
        self._observers.append(obs)

    def notify(self, event: str) -> None:
        for obs in self._observers:
            obs.update(event)

class Observer(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class Logger(Observer):
    def update(self, event: str) -> None:
        print(f"[LOG] {event}")

class Metrics(Observer):
    def update(self, event: str) -> None:
        print(f"[METRIC] {event}")
```

### After: Callback List

```python
from typing import Callable

type EventHandler = Callable[[str], None]

class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = {}

    def on(self, event: str, handler: EventHandler) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def emit(self, event: str, data: str) -> None:
        for handler in self._handlers.get(event, []):
            handler(data)

bus = EventBus()
bus.on("order.created", lambda data: print(f"[LOG] {data}"))
bus.on("order.created", lambda data: print(f"[METRIC] {data}"))
bus.emit("order.created", "order-123")
```

Pub/sub in under twenty lines. For production-grade robustness, reach for `blinker` or `pyee`:

```python
from blinker import signal

order_created = signal("order-created")

@order_created.connect
def log_order(sender, **kwargs):
    print(f"[LOG] {kwargs['order_id']}")

order_created.send(None, order_id="order-123")
```

`blinker` is the signal library Flask uses internally. It relies on weak references to avoid memory leaks and supports namespace isolation.

## How Generators Absorb the Iterator Pattern

GoF Iterator exists to traverse a collection without exposing its internal structure. Java requires a separate class implementing the `Iterator` interface. Python needs a single `yield`.

### Before: `__iter__` + `__next__` Class

```python
class FibonacciIterator:
    def __init__(self, limit: int):
        self.limit = limit
        self.a, self.b = 0, 1
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.count >= self.limit:
            raise StopIteration
        value = self.a
        self.a, self.b = self.b, self.a + self.b
        self.count += 1
        return value
```

### After: Generator Function

```python
from collections.abc import Iterator

def fibonacci(limit: int) -> Iterator[int]:
    a, b = 0, 1
    for _ in range(limit):
        yield a
        a, b = b, a + b
```

Twelve lines collapse to five. State management (`self.a`, `self.b`, `self.count`) is handled by the Python runtime. A generator automatically implements `__iter__` and `__next__`, so it works directly with `for` loops, `list()`, and `itertools` functions.

The real power of generators is **lazy evaluation**. A billion Fibonacci numbers can be consumed one at a time without loading them all into memory. This property makes hand-written Iterator classes nearly obsolete in practice — large file processing, streaming API responses, and pagination all benefit directly.

## Python Decorators vs. GoF Decorator — Same Pattern?

Short answer: **same intent, different mechanism.**

GoF Decorator wraps an object to add behavior while preserving the original interface. Java achieves this with a wrapper class implementing the same interface. Python's `@` decorator is a higher-order function that receives a function (or class) and returns a new one.

### Before: GoF-Style Wrapper Classes

```python
from typing import Protocol

class HttpClient(Protocol):
    def get(self, url: str) -> str: ...

class BasicClient:
    def get(self, url: str) -> str:
        return f"response from {url}"

class LoggingClient:
    def __init__(self, inner: HttpClient):
        self._inner = inner

    def get(self, url: str) -> str:
        print(f"[REQ] GET {url}")
        result = self._inner.get(url)
        print(f"[RES] {len(result)} bytes")
        return result

class RetryClient:
    def __init__(self, inner: HttpClient, retries: int = 3):
        self._inner = inner
        self._retries = retries

    def get(self, url: str) -> str:
        for attempt in range(self._retries):
            try:
                return self._inner.get(url)
            except Exception:
                if attempt == self._retries - 1:
                    raise
        return ""  # unreachable

# Assembly
client = RetryClient(LoggingClient(BasicClient()))
```

### After: Function Decorators

```python
import functools
import time
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def logged(fn: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"[CALL] {fn.__name__}")
        result = fn(*args, **kwargs)
        print(f"[DONE] {fn.__name__}")
        return result
    return wrapper

def retry(retries: int = 3):
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(retries):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == retries - 1:
                        raise
                    time.sleep(0.1 * (2 ** attempt))
            return fn(*args, **kwargs)  # unreachable
        return wrapper
    return decorator

@retry(retries=3)
@logged
def fetch(url: str) -> str:
    return f"response from {url}"
```

`functools.wraps` preserves the original function's `__name__`, `__doc__`, and `__module__`. Without it, stack traces show only `wrapper`, making debugging painful.

The key difference between the two approaches is **composition style**. Class wrappers can be assembled dynamically at runtime; function decorators stack statically at definition time. For HTTP clients where middleware must be conditionally inserted at runtime, class wrappers remain more flexible.

## Template Method as a Higher-Order Function

GoF Template Method defines an algorithm skeleton in a base class and lets subclasses override individual steps. In Python, passing hook callables to a higher-order function feels more natural.

### Before: ABC + Inheritance

```python
from abc import ABC, abstractmethod

class DataExporter(ABC):
    def export(self, data: list[dict]) -> str:
        filtered = self.filter(data)
        transformed = self.transform(filtered)
        return self.format(transformed)

    @abstractmethod
    def filter(self, data: list[dict]) -> list[dict]: ...

    @abstractmethod
    def transform(self, data: list[dict]) -> list[dict]: ...

    @abstractmethod
    def format(self, data: list[dict]) -> str: ...
```

Every subclass must implement all three methods.

### After: Higher-Order Function + Hook Callables

```python
from typing import Callable

type Filter = Callable[[list[dict]], list[dict]]
type Transform = Callable[[list[dict]], list[dict]]
type Formatter = Callable[[list[dict]], str]

def export_data(
    data: list[dict],
    *,
    filter_fn: Filter = lambda d: d,
    transform_fn: Transform = lambda d: d,
    format_fn: Formatter = str,
) -> str:
    return format_fn(transform_fn(filter_fn(data)))

# Usage
import json

result = export_data(
    raw_data,
    filter_fn=lambda d: [r for r in d if r["active"]],
    transform_fn=lambda d: [{"name": r["name"]} for r in d],
    format_fn=lambda d: json.dumps(d, ensure_ascii=False),
)
```

Each step can be replaced independently without an inheritance hierarchy. Default values mean not every hook needs to be specified every time.

## State as dict-of-handlers and match

GoF State separates per-state behavior into distinct classes. In Python, when states are simple, a dict mapping or `match` statement suffices.

### dict-of-handlers

```python
from typing import Callable

type Handler = Callable[["Order"], "Order"]

def handle_pending(order: "Order") -> "Order":
    print(f"Validating order {order.id}")
    return order._replace(state="confirmed")

def handle_confirmed(order: "Order") -> "Order":
    print(f"Processing payment for {order.id}")
    return order._replace(state="paid")

def handle_paid(order: "Order") -> "Order":
    print(f"Shipping order {order.id}")
    return order._replace(state="shipped")

STATE_HANDLERS: dict[str, Handler] = {
    "pending": handle_pending,
    "confirmed": handle_confirmed,
    "paid": handle_paid,
}

def advance(order: "Order") -> "Order":
    handler = STATE_HANDLERS.get(order.state)
    if handler is None:
        raise ValueError(f"No handler for state: {order.state}")
    return handler(order)
```

### match Statement (3.10+)

```python
def advance(order: "Order") -> "Order":
    match order.state:
        case "pending":
            return order._replace(state="confirmed")
        case "confirmed":
            return order._replace(state="paid")
        case "paid":
            return order._replace(state="shipped")
        case _:
            raise ValueError(f"Unknown state: {order.state}")
```

With 3-5 states and simple transition logic, `match` is the most readable option. Beyond ten states or with complex transition conditions, dict-of-handlers scales better. When entry/exit hooks per state are needed or shared context between states grows complex, that is when class-based State becomes the natural choice.

## Protocol-Based Adapter — Interfaces Without Classes

GoF Adapter bridges incompatible interfaces. Java requires an adapter class implementing the target interface. In Python, Protocol enables **matching an interface without modifying the existing class**.

```python
from typing import Protocol

class Notifier(Protocol):
    def notify(self, message: str) -> None: ...

# External library class — cannot modify
class SlackWebhook:
    def __init__(self, url: str):
        self.url = url

    def post(self, text: str) -> None:
        print(f"Slack: {text}")

# Adapter: fits SlackWebhook to Notifier
class SlackNotifier:
    def __init__(self, webhook: SlackWebhook):
        self._webhook = webhook

    def notify(self, message: str) -> None:
        self._webhook.post(message)

def send_alert(notifier: Notifier, msg: str) -> None:
    notifier.notify(msg)

# SlackNotifier satisfies the Notifier Protocol — no inheritance
send_alert(SlackNotifier(SlackWebhook("https://hooks.slack.com/...")), "Server down")
```

`SlackNotifier` does not inherit from `Notifier`. As long as the `notify` method signature matches, mypy accepts it as Protocol-compatible. This is the power of structural typing. It is especially useful when wrapping external library classes — the original code stays untouched while our system's interface is satisfied.

## Abstract Factory as Factory Functions and Closures

GoF Abstract Factory provides an interface for creating families of related objects. In Python, this simplifies to factory functions returning dataclass instances.

```python
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Button:
    label: str
    style: str

@dataclass(frozen=True)
class Dialog:
    title: str
    buttons: list[Button]

type UIFactory = Callable[[str], Dialog]

def dark_theme_factory(title: str) -> Dialog:
    return Dialog(
        title=title,
        buttons=[
            Button("OK", style="dark-primary"),
            Button("Cancel", style="dark-secondary"),
        ],
    )

def light_theme_factory(title: str) -> Dialog:
    return Dialog(
        title=title,
        buttons=[
            Button("OK", style="light-primary"),
            Button("Cancel", style="light-secondary"),
        ],
    )

def create_dialog(factory: UIFactory, title: str) -> Dialog:
    return factory(title)
```

A single function signature expresses the factory contract without a class hierarchy. Adding a new theme means writing one more function.

## When Class-Based Patterns Are Still the Right Choice in Python

Everything above shows how functions, modules, and Protocols lighten pattern expression. But this does not mean classes should be avoided in all cases. Three situations where GoF class structures remain the better choice in Python:

### 1. State and Behavior Are Tightly Coupled

```python
class ConnectionPool:
    def __init__(self, max_size: int):
        self._pool: list[Connection] = []
        self._max_size = max_size
        self._lock = threading.Lock()

    def acquire(self) -> Connection:
        with self._lock:
            if self._pool:
                return self._pool.pop()
            return self._create()

    def release(self, conn: Connection) -> None:
        with self._lock:
            if len(self._pool) < self._max_size:
                self._pool.append(conn)
            else:
                conn.close()

    def _create(self) -> Connection:
        return Connection(...)
```

A connection pool becomes dangerous if internal state (`_pool`, `_lock`) is separated from behavior (`acquire`, `release`). Splitting into functions pushes state management responsibility onto callers and invites concurrency bugs.

### 2. Multiple Objects Collaborate in a Composite Pattern

Patterns like Mediator and Chain of Responsibility, where multiple participants reference each other, need classes to make roles and relationships explicit. Functions and closures obscure "who knows about whom."

### 3. The Framework Assumes Class-Based Extension

Django's `View`, `ModelAdmin`, and `Form` are designed for inheritance-based extension. Forcing a functional approach on top of such frameworks means losing framework features — middleware hooks, signals, admin auto-registration. Following the framework's conventions serves team productivity better.

I summarize this judgment in one sentence: **"If expressing something as functions pushes state management onto callers, or makes object relationships invisible in the code, classes are the right tool."**

## Answering the Opening Questions

- **When implementing Singleton as a class in Python, what problems arise — and what new problems appear when replacing it with a module variable?**
  - A Singleton class carries the complexity of double-checked locking and the test-isolation problem simultaneously. A module variable eliminates both because the import system guarantees a single instance, but lazy initialization or runtime configuration swapping requires a separate mechanism.

- **What do we lose when expressing Strategy or Command as plain functions instead of classes?**
  - Stateful strategies, multi-method strategies, and DI container integration all become more awkward with functions. When a strategy has a single method and no state, functions remove boilerplate while type hints preserve the contract — the best of both worlds.

- **In which situations is the full GoF class structure still the better choice in Python?**
  - When state and behavior are tightly coupled (connection pools), when multiple objects reference each other in collaboration (Mediator), and when the framework assumes class-based extension (Django Views). The signal to return to classes is when function-based expression pushes state management onto callers or makes object relationships invisible.

This series began in article 1 by defining patterns as "names attached to problem-solution pairs." Here at article 10, the same statement bears repeating: the essence of a pattern is its intent, not its class structure. Once intent is understood, it can be expressed with whatever tool the language provides most naturally — and class hierarchies need only appear when those tools fall short.

<!-- toc:begin -->
## Series Table of Contents

- [Design Patterns 101 (1/10): What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational Patterns](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural Patterns](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral Patterns](./04-behavioral-patterns.md)
- [Design Patterns 101 (5/10): Strategy Pattern](./05-strategy-pattern.md)
- [Design Patterns 101 (6/10): Adapter Pattern](./06-adapter-pattern.md)
- [Design Patterns 101 (7/10): Observer Pattern](./07-observer-pattern.md)
- [Design Patterns 101 (8/10): Factory and Dependency Injection](./08-factory-and-di.md)
- [Design Patterns 101 (9/10): Avoiding Pattern Overuse](./09-avoiding-pattern-overuse.md)
- **Pythonic Patterns (current)**

<!-- toc:end -->

## References

### Core References

- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)
- [PEP 634 — Structural Pattern Matching](https://peps.python.org/pep-0634/)
- [dataclasses (Python docs)](https://docs.python.org/3/library/dataclasses.html)
- [functools.wraps (Python docs)](https://docs.python.org/3/library/functools.html#functools.wraps)

### Practical Extensions

- [Python 3 Patterns, Recipes and Idioms (Bruce Eckel)](https://python-3-patterns-idioms-test.readthedocs.io/)
- [Fluent Python, 2nd Edition (Luciano Ramalho)](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) — Part IV: Object-Oriented Idioms
- [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/)
- [Example code for this series (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/en)

Tags: Computer Science, DesignPatterns, Python, Idioms, Protocols, Decorators

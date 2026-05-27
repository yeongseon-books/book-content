---
series: design-patterns-101
episode: 2
title: "Design Patterns 101 (2/10): Creational Patterns"
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
  - Creational
  - Factory
  - Singleton
  - Builder
seo_description: How creational patterns separate object construction from use so teams can reduce coupling, simplify tests, and control object assembly.
last_reviewed: '2026-05-23'
---

# Design Patterns 101 (2/10): Creational Patterns

Early in a project, object-creation code stays invisible. Call `SomeService(config)` and move on. Then the service needs a different DB connection per environment, tests demand a fake repository, and constructor arguments creep past ten. At that point, the code that creates objects becomes the most frequently changed spot in the system. I call this the moment "creation responsibility starts screaming."

This is the 2nd post in the Design Patterns 101 series. It covers the five Creational patterns classified by the GoF — Factory Method, Abstract Factory, Builder, Prototype, Singleton — examining what problem each solves and what it costs, with Python code throughout.

![Responsibility boundaries of the five Creational patterns](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/02/02-01-concept-at-a-glance.en.png)

*The scope of creation responsibility each Creational pattern owns*

## Questions to Keep in Mind

- What exactly improves — and what gets worse — when object-creation code is separated out?
- Factory Method and Builder both "make things." When does each one apply?
- Is there a real situation in Python where a Singleton class needs to be implemented directly?

## Why Separate Object Creation

The pattern I flag most often in code review is "the caller knows the concrete class directly." Consider this service layer:

```python
class OrderService:
    def __init__(self, env: str) -> None:
        if env == "prod":
            self.repo = PostgresRepository(dsn="host=db port=5432 ...")
            self.cache = RedisCache(url="redis://cache:6379")
        elif env == "staging":
            self.repo = PostgresRepository(dsn="host=staging-db ...")
            self.cache = RedisCache(url="redis://staging-cache:6379")
        else:
            self.repo = MemoryRepository()
            self.cache = DictCache()
```

Three problems here:

1. **Testing is hard.** To test `OrderService`, the `env` string must be manipulated, yet the test is still coupled to `MemoryRepository` and `DictCache` as concrete classes.
2. **Changes propagate.** Adding a new environment (say `canary`) forces a change inside `OrderService` even though its business logic has not changed at all.
3. **Creation knowledge is duplicated.** If `PostgresRepository(dsn=...)` is copy-pasted into other services, a DSN format change requires hunting down every occurrence.

Creational patterns address all three. They push the creation decision outside the caller so the caller knows only "what it receives," never "how it gets built."

## The Problem Factory Method Solves

The core of Factory Method is simple: **a separate function (or method) decides which concrete class to instantiate, not the caller.**

Refactoring the `OrderService` example with Factory Method:

```python
from typing import Protocol
import os


class OrderRepository(Protocol):
    def save(self, order_id: str, data: dict) -> None: ...
    def find(self, order_id: str) -> dict | None: ...


def create_repository() -> OrderRepository:
    """Return the appropriate repository based on environment variables."""
    env = os.getenv("APP_ENV", "local")
    if env == "prod":
        from app.infra.postgres import PostgresRepository
        return PostgresRepository(dsn=os.environ["DATABASE_URL"])
    return MemoryRepository()


class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self.repo = repo

    def place_order(self, order_id: str, items: list[str]) -> None:
        self.repo.save(order_id, {"items": items, "status": "placed"})
```

What changed:

- `OrderService` knows only the `OrderRepository` Protocol. It imports no concrete class.
- The branching logic lives in `create_repository()` alone.
- Tests inject directly: `OrderService(FakeRepository())`. No environment-variable manipulation needed.

Factory Method shines when **two or more implementations exist and the choice is determined at runtime.** If there is only one implementation, a factory adds nothing. Direct construction is easier to read.

## The Problem Builder Solves — and How It Differs

Factory Method decides "what type to build." Builder solves a different problem: **assembling a single type step by step when arguments are numerous and combinations vary.**

An HTTP request object as an example:

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes | None = None
    timeout_seconds: float = 30.0
    retry_count: int = 0


class HttpRequestBuilder:
    def __init__(self, method: str, url: str) -> None:
        self._method = method
        self._url = url
        self._headers: dict[str, str] = {}
        self._body: bytes | None = None
        self._timeout: float = 30.0
        self._retries: int = 0

    def header(self, key: str, value: str) -> "HttpRequestBuilder":
        self._headers[key] = value
        return self

    def body(self, data: bytes) -> "HttpRequestBuilder":
        self._body = data
        return self

    def timeout(self, seconds: float) -> "HttpRequestBuilder":
        self._timeout = seconds
        return self

    def retries(self, count: int) -> "HttpRequestBuilder":
        self._retries = count
        return self

    def build(self) -> HttpRequest:
        if not self._url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {self._url}")
        return HttpRequest(
            method=self._method,
            url=self._url,
            headers=self._headers,
            body=self._body,
            timeout_seconds=self._timeout,
            retry_count=self._retries,
        )
```

Usage at the call site:

```python
request = (
    HttpRequestBuilder("POST", "https://api.example.com/orders")
    .header("Authorization", f"Bearer {token}")
    .header("Content-Type", "application/json")
    .body(payload)
    .timeout(10.0)
    .retries(3)
    .build()
)
```

The difference from Factory Method is clear. Factory Method decides "which type to create." Builder expresses "how to configure one type, step by step." They are not competitors — they solve problems on different axes.

In my experience, Builder earns its keep when:

- Constructor arguments exceed five, with more than half being optional
- Validity depends on assembly order (e.g., if `body` is present, a `Content-Type` header is mandatory)
- The same type is frequently instantiated in multiple variations

Conversely, if there are three arguments and all are required, Builder is overkill. A plain `dataclass` constructor is better.

## Why Singleton Is Most Often Misused in Python

Singleton is conceptually simple: "create exactly one instance and share it everywhere." The problem is that this simplicity invites abuse.

Whenever I see a hand-rolled Singleton class in a Python codebase, my first question is "is this actually necessary?" In Python, a module is imported only once.

```python
# config.py — the module-level object already acts as a Singleton
import os

DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///local.db")
DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"
```

Import this module with `from app.config import DATABASE_URL` from anywhere — it is the same object every time. No class needed.

Still, there are cases where a Singleton class is justified: **when initialization is expensive and lifecycle must be managed explicitly.** A connection pool is the canonical example.

```python
import threading


class ConnectionPool:
    _instance: "ConnectionPool | None" = None
    _lock = threading.Lock()

    def __new__(cls, max_size: int = 10) -> "ConnectionPool":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._max_size = max_size
                    cls._instance._connections: list = []
        return cls._instance

    def acquire(self) -> object:
        # Pull a connection from the pool
        ...

    def release(self, conn: object) -> None:
        # Return a connection to the pool
        ...
```

This code improves on a module variable by guaranteeing thread safety via `_lock` and accepting initialization parameters like `max_size`.

But the costs of Singleton are real:

- **Test isolation breaks.** An instance created in test A leaks into test B. Every test must reset `ConnectionPool._instance = None`.
- **Dependencies hide.** If a function calls `ConnectionPool()` internally without declaring it in its signature, the dependency on global state is invisible.
- **Lifecycle control is difficult.** The pool must be cleaned up at shutdown, but tracking "who uses it last" is hard.

I narrow the cases where Singleton is justified in Python to three: (1) resource lifecycle management is mandatory, like a connection pool; (2) thread-safe initialization must prevent races in a multithreaded environment; (3) the framework requires it (e.g., Django's `AppConfig`). Everything else is handled by module-level variables or a DI container's scope configuration.

## The Rare Case Where Abstract Factory Earns Its Place

Abstract Factory **creates families of related objects consistently.** The GoF textbook example is cross-platform UI: Mac buttons paired with Mac text inputs, Windows buttons paired with Windows text inputs, never mixed.

```python
from typing import Protocol


class Button(Protocol):
    def render(self) -> str: ...

class TextInput(Protocol):
    def render(self) -> str: ...


class UIFactory(Protocol):
    def create_button(self, label: str) -> Button: ...
    def create_text_input(self, placeholder: str) -> TextInput: ...


class WebUIFactory:
    def create_button(self, label: str) -> Button:
        return HtmlButton(label)

    def create_text_input(self, placeholder: str) -> TextInput:
        return HtmlTextInput(placeholder)


class TerminalUIFactory:
    def create_button(self, label: str) -> Button:
        return TerminalButton(label)

    def create_text_input(self, placeholder: str) -> TextInput:
        return TerminalTextInput(placeholder)
```

Honestly, I have almost never implemented Abstract Factory directly in a Python backend project. For this pattern to shine, two conditions must hold simultaneously:

1. **Two or more object families must exist.** If there is only one family, plain Factory Method suffices.
2. **Objects within a family must be combined only with members of the same family.** The pattern is meaningful only when a Mac button + Windows text input combination causes a runtime error.

In Python web backends, both conditions rarely hold at the same time. Most cases are solved by a single Factory Method. Introducing Abstract Factory causes the interface count to explode (Factory + each product Protocol), making the code harder to follow. I recommend it only "when there are three or more families and a mix-up has actually caused an outage."

## Prototype — When Cloning Is Cheaper Than Creating

Prototype creates new objects by cloning an existing one. In Python, `copy.deepcopy` fills this role.

```python
import copy
from dataclasses import dataclass, field


@dataclass
class ReportConfig:
    title: str
    columns: list[str] = field(default_factory=list)
    filters: dict[str, str] = field(default_factory=dict)
    page_size: int = 50


# Base template
monthly_template = ReportConfig(
    title="Monthly Sales",
    columns=["date", "product", "revenue", "region"],
    filters={"status": "completed"},
    page_size=100,
)


def create_monthly_report(month: str) -> ReportConfig:
    """Clone the template and add a month-specific filter."""
    report = copy.deepcopy(monthly_template)
    report.filters["month"] = month
    return report
```

Prototype is useful in limited situations: when object initialization is heavy (e.g., external API calls, file parsing), most of the result is identical, and only a small part changes across variations.

A caveat: `deepcopy` is not free. If the nested object graph is deep, cloning itself can be slow, and circular references produce unexpected behavior. Whenever I use Prototype, I measure the size of the clone target and verify that cloning is genuinely cheaper than constructing from scratch.

## Cost Summary of the Five Patterns

Introducing a pattern always costs something. When I propose a Creational pattern to a team, I show this table alongside:

| Pattern | Gain | Loss |
| --- | --- | --- |
| Factory Method | Decouples caller from concrete class | One level of indirection added; "where is this built?" tracing cost |
| Abstract Factory | Prevents cross-family mix-ups | Interface count explodes (Factory + N products); over-engineering if only one family exists |
| Builder | Decomposes complex assembly into readable steps | One extra class; verbose if the object is simple |
| Prototype | Avoids expensive initialization via cloning | deepcopy cost; risk of shared mutable state; harder to trace the original during debugging |
| Singleton | Guarantees a single global instance | Destroys test isolation; hides dependencies; lifecycle management burden |

If the "Loss" column describes a cost the current project cannot absorb, that pattern should not be introduced. Patterns are tools pulled out when a problem exists, not infrastructure laid down in advance.

## Criteria for Choosing Which Pattern to Reach For

During code review, I ask these questions in order when deciding whether to introduce a Creational pattern:

1. **Are there two or more implementations, with the choice determined at runtime?** — Consider Factory Method.
2. **Are there more than five constructor arguments, with diverse optional combinations?** — Consider Builder.
3. **Must related objects be combined only within the same family, and do at least two families exist?** — Consider Abstract Factory.
4. **Is initialization expensive, with most settings identical and only a few varying?** — Consider Prototype.
5. **Must there be exactly one instance, and is a module variable insufficient?** — Only then consider Singleton.

Reaching question 5 is rare. Most creation problems resolve at 1 or 2.

## Answering the Opening Questions

- **What exactly improves — and what gets worse — when object-creation code is separated out?**
  - The improvement: the caller no longer knows the concrete class, making test injection trivial and reducing changes when a new implementation is added. The cost: indirection increases, and tracing "where is this object built?" requires an extra hop. In the `OrderService` example, after introducing the factory, tests finish with a one-line injection — but someone reading the production code for the first time must navigate to `create_repository()` to see the full picture.

- **Factory Method and Builder both "make things." When does each one apply?**
  - Factory Method decides "which type to create." Builder expresses "how to configure one type, step by step." If a DB connection must be selected per environment, Factory Method applies. If an HTTP request needs optional headers, a timeout, and a retry count combined, Builder applies. They are not in competition — they solve problems on different axes.

- **Is there a real situation in Python where a Singleton class needs to be implemented directly?**
  - Yes, but rarely. It is limited to cases requiring thread-safe initialization and explicit lifecycle management, like a connection pool. For sharing configuration values, loggers, or registries, module-level variables suffice and test isolation is easier. Before writing a Singleton class, the question "why can't a module variable do this?" must have a clear answer.

<!-- toc:begin -->
## In this series

- [Design Patterns 101 (1/10): What Are Design Patterns?](./01-what-are-design-patterns.md)
- **Design Patterns 101 (2/10): Creational Patterns (current)**
- Structural Patterns (upcoming)
- Behavioral Patterns (upcoming)
- The Strategy Pattern (upcoming)
- The Adapter Pattern (upcoming)
- The Observer Pattern (upcoming)
- Factory and Dependency Injection (upcoming)
- Avoiding Pattern Overuse (upcoming)
- Pythonic Patterns (upcoming)

<!-- toc:end -->

## References

### Core References

- [Design Patterns: Elements of Reusable Object-Oriented Software (GoF)](https://en.wikipedia.org/wiki/Design_Patterns)
- [Factory Method (refactoring.guru)](https://refactoring.guru/design-patterns/factory-method)
- [Builder (refactoring.guru)](https://refactoring.guru/design-patterns/builder)

### Practical Extensions

- [Abstract Factory (refactoring.guru)](https://refactoring.guru/design-patterns/abstract-factory)
- [Singleton — Why You Should Use It Sparingly](https://martinfowler.com/bliki/InversionOfControl.html)
- [copy — Shallow and deep copy operations (Python docs)](https://docs.python.org/3/library/copy.html)
- [Example code for this series (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/en)

Tags: Computer Science, DesignPatterns, Creational, Factory, Singleton, Builder

---
series: design-patterns-101
episode: 4
title: "Design Patterns 101 (4/10): Behavioral Patterns"
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
  - Behavioral
  - Strategy
  - Observer
  - Command
seo_description: How behavioral patterns turn branching, notifications, requests, and state transitions into readable collaboration structures.
last_reviewed: '2026-05-23'
---

# Design Patterns 101 (4/10): Behavioral Patterns

Code can be neatly separated into classes and still resist change. Modify one class and the notification logic breaks. Add a state transition and existing branches wobble. Swap a sorting strategy and every call site needs updating. These problems surface not because the structure is wrong, but because the **flow of responsibility between objects** is tangled. Behavioral patterns name that flow and draw boundaries so that change does not cascade.

This is the 4th post in the Design Patterns 101 series. Strategy and Observer each get their own deep-dive chapters later (chapters 5 and 7), so here they receive only an overview. The bulk of the discussion goes to Command, Iterator, State, Template Method, and Chain of Responsibility.

![Behavioral pattern responsibility flow](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/04/04-01-concept-at-a-glance.en.png)
*Responsibility distribution in behavioral patterns — algorithm swap, event propagation, request objectification, state transition, traversal abstraction*

## Questions to Keep in Mind

- What makes Command different from a plain function call?
- State and Strategy look almost identical in code — why are they classified as separate patterns?
- Why is there almost never a reason to implement the Iterator pattern explicitly in Python?

## Why Distributing Responsibility Between Objects Is Hard

Creational patterns answer "who creates?", Structural patterns answer "how do we compose?" Behavioral patterns tackle the next question: **once objects exist, how do they talk to each other, and who makes which decisions?**

I see two reasons this is hard.

First, responsibility flow is not visible in code. A class diagram shows "A calls B," but it does not show "who decides whether A notifies B" or "can A's algorithm be swapped at runtime."

Second, poor responsibility distribution causes cascading change. If adding one payment status breaks notification logic, logging logic, and UI rendering logic simultaneously, that is the absence of responsibility boundaries.

The ten behavioral patterns in the GoF catalog attack this problem from different angles. This article covers the seven most frequently encountered in practice.

## Strategy and Observer — Overview

These two patterns get full chapters later (5 and 7), so here I cover only the essentials.

**Strategy** separates an algorithm from its call site so it can be swapped. In Python, functions are first-class objects, so Strategy often needs no class at all.

```python
from typing import Callable

PricingStrategy = Callable[[int], int]

def no_discount(price: int) -> int:
    return price

def vip_discount(price: int) -> int:
    return int(price * 0.7)

def checkout(price: int, strategy: PricingStrategy = no_discount) -> int:
    return strategy(price)
```

**Observer** propagates one object's state change to multiple subscribers. The publisher does not know who the subscribers are; subscribers do not know the publisher's internals. Django signals, JavaScript's `addEventListener`, and Redis Pub/Sub all follow this structure.

What the two patterns share is **introducing indirection to break coupling**. The difference is that Strategy is a 1:1 swap while Observer is a 1:N broadcast.

## What Makes Command Different From a Plain Function Call

Calling a function executes immediately and leaves no trace. The Command pattern turns "an action to perform" into an object, enabling **storage, forwarding, deferred execution, and undo**.

I think of the difference as "phone call vs. letter." A phone call connects instantly but leaves no record. A letter can be stored, reordered, and opened later.

### Undo Stack Example

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol


class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self) -> None: ...


@dataclass
class InsertText:
    document: list[str]
    position: int
    text: str

    def execute(self) -> None:
        self.document.insert(self.position, self.text)

    def undo(self) -> None:
        self.document.pop(self.position)


@dataclass
class Editor:
    document: list[str] = field(default_factory=list)
    history: list[Command] = field(default_factory=list)

    def run(self, cmd: Command) -> None:
        cmd.execute()
        self.history.append(cmd)

    def undo_last(self) -> None:
        if self.history:
            self.history.pop().undo()
```

```python
editor = Editor()
editor.run(InsertText(editor.document, 0, "Hello"))
editor.run(InsertText(editor.document, 1, "World"))
assert editor.document == ["Hello", "World"]

editor.undo_last()
assert editor.document == ["Hello"]
```

Command differs from a function call in three decisive ways.

1. **Serializable** — persist a Command object to JSON or a database and it becomes a task queue.
2. **Undoable** — implement an `undo` method and execution can be reversed.
3. **Composable** — bundle multiple Commands and treat them as a transaction.

### What It Costs

Introducing Command turns a simple method call into a class. Ten actions means ten classes. If undo is unnecessary and queuing is unnecessary, that cost is not justified.

## Why State and Strategy Look Identical in Code

Both delegate behavior to a separate object. Their class diagrams are nearly the same. The difference lies in **intent**.

- **Strategy**: the caller selects the algorithm. Once injected, it typically stays fixed.
- **State**: the object itself switches behavior based on its internal state. Transitions happen repeatedly at runtime.

### TCP Connection State Machine

```python
from __future__ import annotations
from typing import Protocol


class ConnectionState(Protocol):
    def open(self, ctx: Connection) -> None: ...
    def close(self, ctx: Connection) -> None: ...
    def send(self, ctx: Connection, data: bytes) -> None: ...


class Closed:
    def open(self, ctx: Connection) -> None:
        print("Opening connection...")
        ctx.state = Established()

    def close(self, ctx: Connection) -> None:
        print("Already closed.")

    def send(self, ctx: Connection, data: bytes) -> None:
        raise RuntimeError("Cannot send on closed connection")


class Established:
    def open(self, ctx: Connection) -> None:
        print("Already open.")

    def close(self, ctx: Connection) -> None:
        print("Closing connection...")
        ctx.state = Closed()

    def send(self, ctx: Connection, data: bytes) -> None:
        print(f"Sending {len(data)} bytes")


class Connection:
    def __init__(self) -> None:
        self.state: ConnectionState = Closed()

    def open(self) -> None:
        self.state.open(self)

    def close(self) -> None:
        self.state.close(self)

    def send(self, data: bytes) -> None:
        self.state.send(self, data)
```

`Connection` does not know its own state. Each state object decides "which state comes next." This structure means adding a new state (say, `Listening`) requires no modification to existing state classes.

### What It Costs

When there are three or fewer states and transitions are simple, `if/elif` reads better. The State pattern pays for itself when states number five or more, or when transition rules are complex enough to need a table to understand.

## Why Iterator Almost Never Appears Explicitly in Python

The GoF Iterator pattern provides "a way to traverse a collection without exposing its internal structure." In Java, implementing `Iterator<T>` is manual work. Python **baked this pattern into the language itself.**

```python
class SensorReadings:
    """Stores the last N sensor values in a circular buffer."""

    def __init__(self, capacity: int) -> None:
        self._buf: list[float] = []
        self._capacity = capacity

    def add(self, value: float) -> None:
        if len(self._buf) >= self._capacity:
            self._buf.pop(0)
        self._buf.append(value)

    def __iter__(self):
        """Allows traversal without exposing the internal buffer structure."""
        return iter(self._buf)

    def __len__(self) -> int:
        return len(self._buf)
```

The moment `__iter__` is implemented, the object is compatible with `for` loops, `list()`, `sum()`, unpacking — every iteration protocol Python offers. No separate `Iterator` class needed.

For more complex traversal, generators exist.

```python
from pathlib import Path
from typing import Iterator


def walk_python_files(root: Path) -> Iterator[Path]:
    """Recursively traverse directories, yielding only .py files."""
    for child in sorted(root.iterdir()):
        if child.is_dir() and not child.name.startswith("."):
            yield from walk_python_files(child)
        elif child.suffix == ".py":
            yield child
```

Generators manage state automatically and suspend at `yield`, resuming on the next call. The language already solved the problem GoF Iterator was designed to address.

### What It Costs

In Python the cost is less about "losing something" and more about **forgetting to implement `__iter__`**. Build a custom collection without it and `for` loops raise `TypeError` — a debugging detour that catches people off guard.

## Template Method Revisited Through a Functional Lens

Template Method fixes the skeleton of an algorithm in a parent class and lets subclasses fill in the steps. In the GoF era, inheritance was the only option. In Python, passing functions is often more natural.

### Inheritance-Based — ETL Pipeline

```python
from abc import ABC, abstractmethod
from typing import Any


class ETLPipeline(ABC):
    """Skeleton: extract -> transform -> load order is fixed."""

    def run(self) -> None:
        raw = self.extract()
        cleaned = self.transform(raw)
        self.load(cleaned)

    @abstractmethod
    def extract(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def transform(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]: ...

    @abstractmethod
    def load(self, data: list[dict[str, Any]]) -> None: ...


class CsvToPostgres(ETLPipeline):
    def extract(self) -> list[dict[str, Any]]:
        # Read CSV file
        return [{"name": "Alice", "age": "30"}]

    def transform(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [{"name": r["name"], "age": int(r["age"])} for r in data]

    def load(self, data: list[dict[str, Any]]) -> None:
        print(f"Inserting {len(data)} rows into PostgreSQL")
```

### Function Composition — Same Problem, Different Shape

```python
from typing import Any, Callable

ExtractFn = Callable[[], list[dict[str, Any]]]
TransformFn = Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
LoadFn = Callable[[list[dict[str, Any]]], None]


def run_etl(extract: ExtractFn, transform: TransformFn, load: LoadFn) -> None:
    load(transform(extract()))
```

The function-composition version has no inheritance hierarchy, and each step is independently testable. However, when steps share significant state or the step count grows to seven or eight, the class-based approach becomes more readable.

### What It Costs

Template Method forces inheritance. Deep inheritance hierarchies in Python make debugging painful. When there are three or fewer steps and no shared state, function composition wins.

## Chain of Responsibility — When Nobody Knows Who Handles the Request

Chain of Responsibility links objects that might handle a request into a chain. The request flows along the chain until it meets a handler that can process it.

I encounter this pattern most often in web framework middleware stacks. Django middleware, Express's `next()`, and FastAPI's dependency chain all follow this structure.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


@dataclass
class Request:
    path: str
    headers: dict[str, str]
    user: str | None = None


class Handler(Protocol):
    def handle(self, request: Request) -> str | None: ...


@dataclass
class AuthHandler:
    next_handler: Handler | None = None

    def handle(self, request: Request) -> str | None:
        token = request.headers.get("Authorization")
        if not token:
            return "401 Unauthorized"
        request.user = token.split(" ")[-1]  # simplified
        if self.next_handler:
            return self.next_handler.handle(request)
        return None


@dataclass
class RateLimitHandler:
    next_handler: Handler | None = None
    _counter: int = 0

    def handle(self, request: Request) -> str | None:
        self._counter += 1
        if self._counter > 100:
            return "429 Too Many Requests"
        if self.next_handler:
            return self.next_handler.handle(request)
        return None


@dataclass
class RouteHandler:
    next_handler: Handler | None = None

    def handle(self, request: Request) -> str | None:
        return f"200 OK — {request.path} by {request.user}"
```

```python
# Assemble the chain
chain = AuthHandler(next_handler=RateLimitHandler(next_handler=RouteHandler()))

req = Request(path="/api/data", headers={"Authorization": "Bearer alice"})
result = chain.handle(req)
assert result == "200 OK — /api/data by alice"
```

### What It Costs

As the chain grows longer, tracing "where was this request handled?" becomes difficult. Debugging requires walking every handler in order. With three or fewer handlers, a plain `if/elif` is clearer.

## Mediator and Memento — Brief Introduction

**Mediator** prevents objects from referencing each other directly by routing communication through a central coordinator. A chat room is the canonical example: user A sends a message, and the chat room (Mediator) distributes it to other users. GUI frameworks use the same structure to coordinate interactions between form components.

**Memento** saves an object's internal state externally so it can be restored later. Text editor undo and game save/load are textbook cases. It looks similar to Command's `undo`, but Command reverses "the inverse of an action" while Memento restores "a snapshot of state."

## Visitor — Adding Operations Without Changing Structure

Visitor traverses an object structure (e.g., an AST, a file tree) and performs type-specific operations on each node. In Python, `functools.singledispatch` and pattern matching (`match/case`) serve a similar role, so implementing GoF-style Visitor directly is rare.

## Trade-offs by Pattern

| Pattern | What It Gives | What It Costs |
| --- | --- | --- |
| Strategy | Algorithm swap in one line | Extra indirection, strategy object management |
| Observer | Publisher-subscriber fully decoupled | Circular notification risk, harder debugging |
| Command | Storage, undo, queuing | One class per action |
| State | Transition rules made explicit | One class per state |
| Iterator | Internal structure hidden | Python already provides it at the language level |
| Template Method | Algorithm skeleton locked in | Inheritance forced, deep hierarchy risk |
| Chain of Responsibility | Handlers added/removed flexibly | Request tracing difficulty |
| Mediator | Direct coupling between objects removed | Mediator risks becoming a God Object |
| Memento | State restoration possible | Memory usage increase |
| Visitor | Operations added without structure change | Every Visitor must update when a new node type is added |

## Answering the Opening Questions

- **What makes Command different from a plain function call?**
  - A function call executes immediately and vanishes. Command turns an action into an object, enabling storage, forwarding, and undo. In the Editor example, `InsertText` objects accumulate in the `history` list and `undo_last()` reverses them. The value of Command surfaces the moment queuing or retry becomes necessary.

- **State and Strategy look almost identical in code — why are they classified as separate patterns?**
  - Both delegate behavior, but Strategy has the caller select the algorithm externally — once injected, it typically stays fixed. State has the object itself switch behavior based on internal state, with transitions happening repeatedly at runtime. In the TCP Connection example, `Closed` transitioning itself to `Established` is a characteristic absent from Strategy.

- **Why is there almost never a reason to implement the Iterator pattern explicitly in Python?**
  - Python provides the `__iter__`/`__next__` protocol and generators at the language level. As the `SensorReadings` example shows, implementing `__iter__` alone grants compatibility with `for` loops, `sum()`, unpacking, and every other iteration facility. The language already solved the problem GoF addressed with a separate Iterator class.

<!-- toc:begin -->
## Series Table of Contents

- [What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Creational Patterns](./02-creational-patterns.md)
- [Structural Patterns](./03-structural-patterns.md)
- **Behavioral Patterns (current)**
- Strategy Pattern (upcoming)
- Adapter Pattern (upcoming)
- Observer Pattern (upcoming)
- Factory and Dependency Injection (upcoming)
- When Not to Use Patterns (upcoming)
- Patterns That Suit Python (upcoming)

<!-- toc:end -->

## References

### Core References

- [Strategy Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/strategy)
- [Observer Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/observer)
- [Command Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/command)
- [State Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/state)
- [Chain of Responsibility (refactoring.guru)](https://refactoring.guru/design-patterns/chain-of-responsibility)

### Practical Extensions

- [The Python Language Reference — Data model (`__iter__`)](https://docs.python.org/3/reference/datamodel.html)
- [Python `functools.singledispatch`](https://docs.python.org/3/library/functools.html#functools.singledispatch)
- [Example code for this series (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/en)

Tags: Computer Science, DesignPatterns, Behavioral, Strategy, Observer, Command

---
series: functional-programming-101
episode: 6
title: "Functional Programming 101 (6/10): Closures and Partial Application"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Python
  - Functional Programming
  - Closures
  - partial
  - functools
seo_description: Learn how closures capture variables and how functools.partial customizes functions by fixing arguments.
last_reviewed: '2026-05-04'
---

# Functional Programming 101 (6/10): Closures and Partial Application

Closures start to feel practical the moment you need a callback, decorator, or handler to carry a little bit of context. The function itself may be small, but once it has to remember which tenant it belongs to, how many retries are left, or which logger prefix to use, a plain parameter list stops being the whole story.

`functools.partial` solves a nearby problem from a different angle. Instead of remembering mutable context, it pre-fills stable arguments of an existing function. That distinction matters in production code because it tells you whether you are carrying state or simply specializing configuration.

This is the 6th post in the Functional Programming 101 series.


![Functional Programming 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/06/06-01-closure-vs-partial-decision-flow.en.png)
*Functional Programming 101 chapter 6 flow overview*

## Questions to Keep in Mind

- What is a closure and what does it capture?
- What problem does partial application solve?
- When does a closure cause a subtle bug?

## Why It Matters

Closures encapsulate state without using classes — a lightweight pattern. Decorators, factory functions, and callbacks are all built on closures.

> Closures = functions that carry data

`functools.partial` pre-fills arguments of an existing function to create a specialized version. Both patterns combine with higher-order functions to produce flexible code.

## Concept Overview

> Structure of a Closure

```text
outer_func(x)
  |
  +-- local variable x (becomes a free variable)
  |
  +-- inner_func(y)
       |
       +-- x + y  <- remembers outer x
            (closure)
```

## Closure vs partial decision flow

## Key Concepts

| Term | Description |
|------|-------------|
| Closure | An inner function that remembers variables from its enclosing scope |
| Free variable | A variable used inside a function that is not locally defined |
| Cell object | Python's internal structure for storing free variables |
| partial | Creates a new function by fixing some arguments of an existing function |
| Currying | Transforming a multi-argument function into a chain of single-argument functions |

## Before / After

Remove repeated arguments with a closure.

```python
# before: passing the same argument every time
import logging

logger = logging.getLogger("app")

logger.info("[UserService] User created")
logger.info("[UserService] User queried")
logger.info("[UserService] User deleted")
```

```python
# after: closure fixes the prefix
import logging

def make_logger(prefix: str):
    logger = logging.getLogger("app")
    def log(message: str) -> None:
        logger.info(f"[{prefix}] {message}")
    return log

user_log = make_logger("UserService")
user_log("User created")
user_log("User queried")
user_log("User deleted")
```

## Hands-On Steps

### Step 1: Closure Basics

```python
def make_counter(start: int = 0):
    """Creates a counter function."""
    count = start

    def counter() -> int:
        nonlocal count
        count += 1
        return count

    return counter

c1 = make_counter()
print(c1())  # 1
print(c1())  # 2
print(c1())  # 3

c2 = make_counter(100)
print(c2())  # 101

# c1 and c2 maintain independent state
print(c1())  # 4
print(c2())  # 102
```

### Step 2: Inspecting Free Variables

```python
def make_greeter(greeting: str):
    def greet(name: str) -> str:
        return f"{greeting}, {name}!"
    return greet

hello = make_greeter("Hello")
bye = make_greeter("Goodbye")

print(hello("Alice"))  # Hello, Alice!
print(bye("Bob"))      # Goodbye, Bob!

# inspect free variables
print(hello.__code__.co_freevars)      # ('greeting',)
print(hello.__closure__[0].cell_contents)  # Hello
print(bye.__closure__[0].cell_contents)    # Goodbye
```

### Step 3: functools.partial

```python
from functools import partial

# basic usage: fix arguments
def power(base: int, exponent: int) -> int:
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(5))    # 125

# practical example: API client configuration
def send_request(method: str, url: str, headers: dict) -> str:
    return f"{method} {url} (headers={headers})"

api_get = partial(send_request, "GET", headers={"Authorization": "Bearer token"})
api_post = partial(send_request, "POST", headers={"Authorization": "Bearer token"})

print(api_get("/users"))
# GET /users (headers={'Authorization': 'Bearer token'})
print(api_post("/orders"))
# POST /orders (headers={'Authorization': 'Bearer token'})
```

### Step 4: Closures vs partial

```python
from functools import partial

# approach 1: closure
def make_tax_calculator_closure(rate: float):
    def calculate(amount: float) -> float:
        return round(amount * rate, 2)
    return calculate

# approach 2: partial
def calculate_tax(amount: float, rate: float) -> float:
    return round(amount * rate, 2)

make_tax_calculator_partial = lambda rate: partial(calculate_tax, rate=rate)

# usage is identical
tax_10 = make_tax_calculator_closure(0.1)
tax_10_p = make_tax_calculator_partial(0.1)

print(tax_10(50000))    # 5000.0
print(tax_10_p(50000))  # 5000.0

# selection criteria
# - closure: when state mutation (nonlocal) is needed
# - partial: when you only need to fix arguments
```

### Step 5: Real-World Usage — Event Handlers

```python
from functools import partial
from collections.abc import Callable

# event system
class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = {}

    def on(self, event: str, handler: Callable) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def emit(self, event: str, **data) -> None:
        for handler in self._handlers.get(event, []):
            handler(**data)

# closure to create a handler with context
def make_logger_handler(prefix: str):
    def handler(**data) -> None:
        print(f"[{prefix}] {data}")
    return handler

# partial to convert an existing function into a handler
def log_event(level: str, **data) -> None:
    print(f"[{level}] {data}")

bus = EventBus()
bus.on("user.created", make_logger_handler("UserService"))
bus.on("user.created", partial(log_event, "INFO"))

bus.emit("user.created", name="Alice", email="alice@example.com")
# [UserService] {'name': 'Alice', 'email': 'alice@example.com'}
# [INFO] {'name': 'Alice', 'email': 'alice@example.com'}
```

### Step 6: Production-shaped example — tenant-aware webhook handlers

```python
from dataclasses import dataclass
from functools import partial

@dataclass(frozen=True)
class TenantPolicy:
    tenant: str
    retry_limit: int
    audit_channel: str

def make_retry_decider(policy: TenantPolicy):
    attempts = 0

    def should_retry(status: str) -> bool:
        nonlocal attempts
        attempts += 1
        return status == "temporary-failure" and attempts < policy.retry_limit

    return should_retry

def publish_audit(channel: str, event_name: str, payload: dict) -> None:
    print(f"[{channel}] {event_name}: {payload}")

policy = TenantPolicy(
    tenant="store-kr",
    retry_limit=3,
    audit_channel="orders.webhook",
)

should_retry = make_retry_decider(policy)
record_audit = partial(publish_audit, policy.audit_channel)

event = {"order_id": "A-1024", "status": "temporary-failure"}
record_audit("webhook.received", {"tenant": policy.tenant, **event})

if should_retry(event["status"]):
    record_audit("webhook.retry_scheduled", {"order_id": event["order_id"], "attempt": 1})
```

This is closer to the kind of code you meet in production. The closure keeps retry state for one tenant policy, while `partial` binds a shared audit channel once so every handler does not have to pass it around again.

## What to Notice in This Code

- Closures store outer variables in `__closure__`, keeping them alive after the outer function returns
- `nonlocal` is needed to modify an outer variable (not needed for read-only access)
- `partial` is a convenient way to fix arguments and create specialized functions
- Use closures when state mutation is needed; use `partial` when only fixing arguments

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Sharing variables across closures in a loop | All closures reference the same variable | Copy the value via a default argument |
| Modifying an outer variable without nonlocal | UnboundLocalError is raised | Add a `nonlocal` declaration |
| Managing too much state with closures | A class would be more appropriate | Use a class when state is complex |
| Using lambda instead of partial | `partial` is clearer and faster | Use partial when the goal is fixing arguments |
| Not inspecting closure state during debugging | Free variables may differ from expectations | Check `__closure__` to verify state |

## Real-World Applications

- Decorators use closures to remember configuration values
- Callbacks receive extra arguments via `partial`
- Tests use `partial` to fix common parameters
- Logging utilities use closures to fix a prefix
- Event handlers bind context with closures

## How Senior Engineers Think About This

Closures are "lightweight objects." When state is simple and there is only one method, a closure is more appropriate than a class. Conversely, when state is complex and multiple methods are needed, a class is the right choice.

`functools.partial` is an underrated tool. Using `partial(f, fixed_arg)` instead of `lambda x: f(x, fixed_arg)` is clearer and enables `repr()` to display the fixed arguments, making debugging easier.

## Checklist

- [ ] I can explain the mechanism by which closures remember outer variables
- [ ] I can distinguish when `nonlocal` is needed and when it is not
- [ ] I can fix function arguments with `functools.partial`
- [ ] I know the selection criteria between closures and partial
- [ ] I can solve the loop variable sharing problem with closures

## Exercises

1. Write a `make_call_counter(func)` closure that counts how many times the wrapped function is called.
2. Use `partial` to customize the `key` argument of `sorted` in a utility function.
3. Reproduce the loop variable sharing problem with closures and fix it.

## Summary and Next Steps

Closures let functions remember the environment where they were defined, and `partial` fixes arguments of existing functions. Use closures when state is needed; use partial when only fixing arguments. The next article covers a core functional programming technique: **recursion and tail calls**.

## Answering the Opening Questions

- **What is a closure and what does it capture?**
  - A closure remembers values because the inner function holds references to free variables, so they survive even after the outer function finishes. `make_counter()` accumulating `count` via `nonlocal` and `make_greeter()` maintaining different `greeting` values show the mechanism directly.
- **What problem does partial application solve?**
  - When you only need to fix some arguments of an existing function without remembering new state, `partial` is more appropriate than a closure. `square = partial(power, exponent=2)`, `api_get = partial(send_request, "GET", ...)`, and `record_audit = partial(publish_audit, policy.audit_channel)` make the fixed values visible in the code, which is more readable than a closure.
- **When does a closure cause a subtle bug?**
  - `co_freevars` and `__closure__[0].cell_contents` provide direct evidence when investigating why a closure returns unexpected values. Like the example checking which `greeting` `hello` and `bye` each captured, these are very useful for tracking loop-variable sharing or incorrect state capture.

<!-- toc:begin -->
## In this series

- [Functional Programming 101 (1/10): What Is Functional Programming?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): Pure Functions and Side Effects](./02-pure-functions.md)
- [Functional Programming 101 (3/10): Immutable Data](./03-immutable-data.md)
- [Functional Programming 101 (4/10): Higher-Order Functions](./04-higher-order-functions.md)
- [Functional Programming 101 (5/10): map, filter, reduce](./05-map-filter-reduce.md)
- **Closures and Partial Application (current)**
- Recursion and Tail Calls (upcoming)
- Lazy Evaluation and Generators (upcoming)
- Function Composition and Pipelines (upcoming)
- Balancing OOP and Functional Programming (upcoming)

<!-- toc:end -->

## References

- [Python Official Docs — functools.partial](https://docs.python.org/3/library/functools.html#functools.partial)
- [Real Python — Closures in Python](https://realpython.com/python-closure/)
- [Fluent Python — Chapter 9: Decorators and Closures](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [PEP 3104 — Access to Names in Outer Scopes (nonlocal)](https://peps.python.org/pep-3104/)

Tags: Python, Functional Programming, Closures, partial, functools


# Closures and Partial Application

> Functional Programming 101 Series (6/10)

<!-- a-grade-intro:begin -->

**Key Question**: If a function remembers variables from the scope where it was defined, what patterns become possible?

> A closure is an inner function that remembers variables from its enclosing scope. `functools.partial` fixes some arguments of an existing function to create a new one. This article covers how closures work and practical patterns with partial application.

<!-- a-grade-intro:end -->

## What You Will Learn

- The definition and mechanics of closures
- The relationship between free variables and cell objects
- Fixing function arguments with functools.partial
- When to choose closures vs partial

## Why It Matters

Closures encapsulate state without using classes — a lightweight pattern. Decorators, factory functions, and callbacks are all built on closures.

> Closures = functions that carry data

`functools.partial` pre-fills arguments of an existing function to create a specialized version. Both patterns combine with higher-order functions to produce flexible code.

## Concept Overview

> Structure of a Closure

```
outer_func(x)
  |
  +-- local variable x (becomes a free variable)
  |
  +-- inner_func(y)
       |
       +-- x + y  <- remembers outer x
           (closure)
```

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
from typing import Callable


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

- [What Is Functional Programming?](./01-what-is-fp.md)
- [Pure Functions and Side Effects](./02-pure-functions.md)
- [Immutable Data](./03-immutable-data.md)
- [Higher-Order Functions](./04-higher-order-functions.md)
- [map, filter, reduce](./05-map-filter-reduce.md)
- **Closures and Partial Application (current)**
- [Recursion and Tail Calls](./07-recursion.md)
- [Lazy Evaluation and Generators](./08-lazy-evaluation.md)
- [Function Composition and Pipelines](./09-function-composition.md)
- [Balancing OOP and Functional Programming](./10-oop-and-fp-balance.md)
## References

- [Python Official Docs — functools.partial](https://docs.python.org/3/library/functools.html#functools.partial)
- [Real Python — Closures in Python](https://realpython.com/python-closure/)
- [Fluent Python — Chapter 9: Decorators and Closures](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [PEP 3104 — Access to Names in Outer Scopes (nonlocal)](https://peps.python.org/pep-3104/)

Tags: Python, Functional Programming, Closures, partial, functools

---

© 2026 YeongseonBooks. All rights reserved.

---
series: type-hints-python-101
episode: 1
title: "Type Hints in Python 101 (1/10): What Are Python Type Hints?"
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
  - Type Hints
  - Static Typing
  - PEP 484
  - Code Quality
  - Developer Productivity
seo_description: Learn what Python type hints are, why they matter, and how to start using them for safer, more readable code.
last_reviewed: '2026-05-04'
---

# Type Hints in Python 101 (1/10): What Are Python Type Hints?

This is the first post in the Type Hints in Python 101 series.

> Type Hints in Python 101 Series (1/10)

**Key Question**: Can Python code be both dynamically typed and statically verified at the same time?

> Python is dynamically typed — variables can hold any value, and types are checked at runtime. This flexibility is powerful but makes it harder to catch bugs early. Type hints, introduced in PEP 484, let you annotate expected types without changing how Python runs. Static analysis tools then verify these annotations before your code ever executes. This article introduces what type hints are, why they matter, and how to start using them.


![Type Hints in Python 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/01/01-01-big-picture.en.png)
*Type Hints in Python 101 chapter 1 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Are Python Type Hints??
- Which signal should the example or diagram make visible for What Are Python Type Hints??
- What failure should be prevented first when What Are Python Type Hints? reaches a real system?

## What You Will Learn

- What type hints are and how they differ from static typing
- The history and motivation behind PEP 484
- Basic syntax for annotating variables, parameters, and return types
- How type hints improve code quality without affecting runtime

## Why It Matters

As Python projects grow beyond a few hundred lines, the lack of explicit types becomes a liability. A function that accepts "data" could receive a dict, a list, a string, or None — and the only way to know is to read the implementation. Type hints make the contract explicit: what goes in, what comes out.

> Type hints = executable documentation that tools can verify.

IDEs use type hints for better autocomplete. CI pipelines use them to catch bugs before code review. New team members read them to understand APIs faster.

> Type hints are optional annotations that describe expected types. Python ignores them at runtime, but static analysis tools use them to find errors.

```text
def greet(name: str) -> str:
         ^^^^  ^^^     ^^^
         param type    return type
              │              │
         Python ignores both at runtime
              │              │
         mypy/pyright verify both statically
```

## Key Concepts

| Term | Description |
| --- | --- |
| Type hint | An annotation indicating the expected type of a variable or expression |
| PEP 484 | The Python Enhancement Proposal that introduced type hints (2014) |
| Static analysis | Checking code for errors without executing it |
| Dynamic typing | Types are checked at runtime, not at compile time |
| Gradual typing | Adding type hints incrementally to an existing codebase |

## Before / After

**Before — No type hints:**

```python
def calculate_total(prices, tax_rate):
    subtotal = sum(prices)
    return int(subtotal * (1 + tax_rate))

# What type is prices? list? tuple? What about tax_rate?
```

**After — With type hints:**

```python
def calculate_total(prices: list[int], tax_rate: float) -> int:
    subtotal = sum(prices)
    return int(subtotal * (1 + tax_rate))

# Clear: prices is list[int], tax_rate is float, returns int
```

## Hands-On Steps

### Step 1: Annotate Function Parameters

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

result = greet("Alice")  # OK
# greet(42)  # mypy error: Argument 1 has incompatible type "int"
```

The syntax is `parameter: Type` for inputs and `-> Type` for the return value. Python does not enforce these at runtime.

### Step 2: Annotate Variables

```python
count: int = 0
name: str = "Alice"
prices: list[int] = [1000, 2000, 3000]
config: dict[str, str] = {"host": "localhost", "port": "8080"}
```

Variable annotations use the same `name: Type = value` syntax. In most cases, the type checker can infer the type from the assigned value, so explicit variable annotations are optional.

### Step 3: Use Built-in Generic Types

```python
# Python 3.9+ — use built-in types directly
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 95, "Bob": 87}
coordinates: tuple[float, float] = (37.5, 127.0)
unique_ids: set[int] = {1, 2, 3}
```

Since Python 3.9, you can use `list[str]` instead of `typing.List[str]`. Built-in types support subscript notation directly.

### Step 4: Annotate a Class

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hi, I'm {self.name}."

user = User("Alice", 30)
print(user.greet())
```

`__init__` always returns `None`. Annotate `self` is not required — type checkers infer it automatically.

### Step 5: Run a Type Checker

```bash
pip install mypy
mypy app.py
```

```python
# app.py
def add(a: int, b: int) -> int:
    return a + b

add("hello", "world")  # mypy: Argument 1 has incompatible type "str"
```

mypy reads your type hints and reports errors without running the code.

## What to Notice in This Code

- Type hints use the colon syntax for parameters and `->` for return types
- Python ignores type hints at runtime — they are metadata only
- Type checkers (mypy, pyright) use hints to find bugs before execution
- Variable annotations are optional when the type is obvious from the assignment

## 5 Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Thinking type hints are enforced at runtime | Code runs even with wrong types | Use mypy or pyright to verify |
| Using `typing.List` on Python 3.9+ | Unnecessary import | Use `list[str]` directly |
| Annotating every local variable | Code becomes verbose | Let the type checker infer local types |
| Forgetting `-> None` on `__init__` | Incomplete signature | Always add `-> None` to `__init__` |
| Mixing type hints with runtime validation | Type hints do not validate data | Use Pydantic for runtime validation |

## Real-World Applications

- FastAPI uses type hints to auto-generate API documentation and validate requests
- VS Code + Pylance provides intelligent autocomplete based on type annotations
- Large codebases at Dropbox, Instagram, and Google use mypy for early bug detection
- CI pipelines run type checks alongside tests to catch regressions
- Library authors ship `.pyi` stub files so users get type-aware IDE support

## How Senior Engineers Think About This

Senior engineers treat type hints as a communication tool, not a bureaucratic requirement. The primary audience is the next developer who reads the code — including yourself six months from now. A well-typed function signature is worth more than a paragraph of docstring explaining what types it accepts.

The key insight is that type hints pay compound interest. The initial investment is small — a few annotations per function — but the returns grow as the codebase scales. Refactoring becomes safer, code review becomes faster, and onboarding becomes smoother. The earlier you start, the more you benefit.

## Checklist

- [ ] Annotated function parameters with types
- [ ] Added return type annotations to all functions
- [ ] Used built-in generic types (Python 3.9+) instead of typing imports
- [ ] Ran mypy or pyright to verify annotations
- [ ] Avoided annotating obvious local variables

## Exercises

1. Take a Python file you have written before and add type hints to all function signatures. Run `mypy` and fix any errors it reports.

2. Write a `Rectangle` class with `width: float`, `height: float`, and an `area() -> float` method. Verify it with mypy.

3. Intentionally introduce three type errors (wrong argument type, wrong return type, missing annotation) and observe how mypy reports each one.

## Summary and Next Steps

Type hints are optional annotations that describe expected types in Python code. They do not affect runtime behavior but enable static analysis tools to catch bugs before execution. Starting with function signatures gives the highest return on investment.

In the next article, we will explore basic types and collection types in detail, including `list`, `dict`, `tuple`, and `set` with their type parameters.

## Answering the Opening Questions

- **How do type hints differ from type declarations in statically typed languages?**
  Type hints like `def greet(name: str) -> str` are optional annotations that Python's runtime doesn't enforce immediately. Instead, tools like mypy, pyright, and IDEs read these contracts for static analysis and autocompletion—unlike mandatory declarations in static languages.
- **What problem was PEP 484 trying to solve?**
  The core issue was signatures like `calculate_total(prices, tax_rate)` where input and return structure were unreadable from code alone. PEP 484 established a standard for placing public function contracts in code, enabling static analysis and safe refactoring across team codebases.
- **What syntax attaches types to variables, parameters, and return values?**
  Variables use `count: int = 0`, parameters use `name: str`, and return values use `-> str`. Collections use built-in generic syntax—`list[int]`, `dict[str, str]`, `tuple[float, float]`—to let tools track the actual contract.

<!-- toc:begin -->
## In this series

- **What Are Python Type Hints? (current)**
- Basic Types and Collection Types (upcoming)
- Optional and Union (upcoming)
- Function Type Hints (upcoming)
- TypedDict and dataclass (upcoming)
- Protocol and Structural Typing (upcoming)
- Understanding Generics (upcoming)
- Using mypy and pyright (upcoming)
- Pydantic and Type Hints (upcoming)
- Type Hint Best Practices (upcoming)

<!-- toc:end -->

## References

- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [Python docs — typing module](https://docs.python.org/3/library/typing.html)
- [mypy documentation](https://mypy.readthedocs.io/en/stable/)
- [Real Python — Python Type Checking](https://realpython.com/python-type-checking/)

Tags: Python, Type Hints, Static Typing, PEP 484, Code Quality, Developer Productivity

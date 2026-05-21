---
title: "Python Package 101 (8/10): Type Hints and Static Analysis"
series: python-package-101
episode: 8
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Python
- Type Hints
- mypy
- py.typed
- Static Analysis
- Typing
last_reviewed: '2026-05-15'
seo_description: Type hints declare the input and output types of functions, and mypy
  catches type errors without running the code.
---

# Python Package 101 (8/10): Type Hints and Static Analysis

The moment other developers import your package, they need more than working code. They need a contract they can read quickly, and type hints are the fastest way to make that contract visible to both humans and tools.

This is post 8 in the Python Package 101 series. Here we use type hints, `mypy`, and `py.typed` to turn Python packaging into something safer to consume and easier to refactor.

## Questions to Keep in Mind

- Why are type hints needed and do they affect runtime?
- What kinds of errors does `mypy` catch?
- Why is the `py.typed` marker file needed?

## Big Picture

![Python Package 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/08/08-01-mental-model.en.png)

*Python Package 101 chapter 8 flow overview*

This picture places Type Hints and Static Analysis inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What you will learn

- How to add type hints to functions, variables, and return values
- How to run static type checking with `mypy`
- How to make a package type-safe with the `py.typed` marker
- Advanced types: generics, Union, Optional

## Why it matters

Python is dynamically typed, but as projects grow, it becomes hard to tell "what should I pass to this function?" just by reading code. Type hints let IDEs autocomplete and let mypy catch errors before execution.

> A function returns a dict but you do not know which keys it has. The caller writes `result["username"]` but the actual key is `result["user_name"]`. A runtime KeyError hits production.

## Mental Model

> Type hints are labels on a shipping box. If a box says "fragile," the courier (mypy) handles it carefully. Without a label, breakage goes unnoticed.

```text
def greet(name: str) -> str:
         ↑ input label    ↑ output label

mypy checks:
  greet(42)    # Error: expected str, got int
  x: int = greet("Alice")  # Error: str assigned to int
```

## Core Concepts

| Term | Description | Example |
|---|---|---|
| type hint | Type annotation on variables/arguments/return values | `name: str` |
| mypy | Python static type checker | `mypy src/` |
| py.typed | Marker file indicating a package includes type hints | empty file |
| Generic | Type parameterized by another type | `list[str]`, `dict[str, int]` |
| Union | One of several types | `str \| None` (Python 3.10+) |

## Before / After

**Before (no type hints)**

```python
def process(data):
    # What is data? dict? list? str?
    return data["name"]  # possible KeyError

result = process({"username": "alice"})  # runtime error
```

**After (type hints + mypy)**

```python
from typing import TypedDict

class UserData(TypedDict):
    name: str
    age: int

def process(data: UserData) -> str:
    return data["name"]

result = process({"username": "alice"})  # mypy catches this before runtime
```

## Step-by-step practice

### Step 1. Basic type hints

```python
# src/mylib/core.py
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

def find_user(user_id: int) -> dict[str, str] | None:
    users = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
    return users.get(user_id)
```

### Step 2. Install and run mypy

```bash
pip install mypy
mypy src/
# Success: no issues found in 2 source files
```

```python
# Add an intentional error
result: int = greet("Alice")  # assigning str to int
```

```bash
mypy src/
# error: Incompatible types in assignment
#   (expression has type "str", variable has type "int")
```

### Step 3. Configure mypy in pyproject.toml

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

```bash
mypy src/
```

### Step 4. Add the py.typed marker

```bash
touch src/mylib/py.typed
```

```toml
# Include in pyproject.toml
[tool.setuptools.package-data]
mylib = ["py.typed"]
```

### Step 5. Advanced type usage

```python
# src/mylib/utils.py
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

def retry(func: Callable[..., T], attempts: int = 3) -> T | None:
    """Retry a function up to N times."""
    for i in range(attempts):
        try:
            return func()
        except Exception:
            if i == attempts - 1:
                return None
    return None

# Usage
def fetch_data() -> dict[str, str]:
    return {"key": "value"}

result = retry(fetch_data)  # mypy: dict[str, str] | None
```

## What to notice in this code

- Type hints have no runtime effect. They exist purely for tools like mypy and IDEs
- When `py.typed` is present, projects that depend on your package also get mypy checking
- `strict = true` enables the strictest checking mode, ideal for new projects
- Python 3.10+ allows `X | None` as a replacement for `Optional[X]`

## Common mistakes

### Mistake 1. Overusing Any

```python
from typing import Any
def process(data: Any) -> Any:  # type hints become meaningless
    ...
```

Use specific types. Even `dict[str, Any]` is better than bare `Any`.

### Mistake 2. Not including py.typed in the build

Creating `py.typed` but not adding it to `[tool.setuptools.package-data]` means it will not be in the wheel.

### Mistake 3. Applying strict mode to an existing codebase at once

You will get thousands of errors. For existing code, enable flags like `--disallow-untyped-defs` incrementally.

### Mistake 4. Assuming type hints enforce types at runtime

```python
def greet(name: str) -> str: ...
greet(42)  # runs fine at runtime! mypy catches it, not Python
```

For runtime validation, use `isinstance` or `pydantic`.

### Mistake 5. Not installing type stubs for third-party libraries

```bash
pip install types-requests  # type stubs for requests
mypy src/  # resolves import type errors for requests
```

## Practical applications

- **CI gate**: Add `mypy --strict src/` to CI to block PRs with type errors
- **IDE support**: VSCode Pylance reads type hints for autocomplete and error highlighting
- **API docs**: Auto-generate API documentation from type hints (Sphinx autodoc)
- **Refactoring safety net**: Changing a function signature flags all call sites, preventing missed updates
- **Pydantic integration**: Define data models with type hints and get runtime validation

## How practitioners think about this

Type hints are "documentation for your future self and your team." When you see `data: dict[str, list[int]]`, you understand the structure without reading a docstring.

For new projects, start with `strict = true` from day one. For existing projects, add types to new files first and expand incrementally. "All or nothing" is unrealistic — "gradual adoption" is the practical strategy.

## Checklist

- [ ] You can add type hints to function arguments and return values
- [ ] You can check for type errors with `mypy`
- [ ] You understand the role of `py.typed` and can include it in your package
- [ ] You can use Generic, Union, and Optional types appropriately
- [ ] You can configure mypy settings in pyproject.toml

## Exercises

1. Add type hints to all functions in the CLI package from the previous post and pass `mypy --strict src/`.
2. Define a user info structure with `TypedDict` and verify that mypy catches incorrect key access.
3. Add `py.typed`, build a wheel, and confirm that `py.typed` is included inside the wheel.

## Summary and next

- Type hints declare input and output types so tools can catch errors before execution.
- `mypy` is a static analyzer that checks types without running the code.
- The `py.typed` marker lets consumers of your package benefit from type checking too.
- Start with `strict = true` for new projects; adopt incrementally for existing ones.
- Overusing `Any` defeats the purpose of type hints.

The next post covers **documentation** — README, MkDocs, and API Reference.

## Answering the Opening Questions

- **Why are type hints needed and do they affect runtime?**
  - The article treats Type Hints and Static Analysis as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What kinds of errors does `mypy` catch?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why is the `py.typed` marker file needed?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Python Package 101 (1/10): What Is a Python Package?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): Project Structure — src layout and pyproject.toml](./02-project-structure.md)
- [Python Package 101 (3/10): Dependency Management — venv, pip, uv, requirements](./03-dependency-management.md)
- [Python Package 101 (4/10): Building Packages — wheel and sdist](./04-building-packages.md)
- [Python Package 101 (5/10): Publishing to PyPI — from TestPyPI to production](./05-publishing-to-pypi.md)
- [Python Package 101 (6/10): Versioning and Releases](./06-versioning-and-releases.md)
- [Python Package 101 (7/10): CLI Packages](./07-cli-packages.md)
- **Python Package 101 (8/10): Type Hints and Static Analysis (current)**
- Python Package 101 (9/10): Documentation — README, MkDocs, API Reference (upcoming)
- Python Package 101 (10/10): Production Package Template (upcoming)

<!-- toc:end -->

## References

- [mypy documentation](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 561 - Distributing and Packaging Type Information](https://peps.python.org/pep-0561/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)

Tags: Python, Packaging, PyPI, pyproject.toml

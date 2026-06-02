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

This is the 8th post in the Python Package 101 series. Here we use type hints, `mypy`, and `py.typed` to turn Python packaging into something safer to consume and easier to refactor.

![Python Package 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/08/08-01-mental-model.en.png)
*Python Package 101 chapter 8 flow overview*

## Questions to Keep in Mind

- Why are type hints needed and do they affect runtime?
- What kinds of errors does `mypy` catch?
- Why is the `py.typed` marker file needed?

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

## Type Hints from Basics to Advanced

### Basic type annotations

```python
# Basic types
name: str = "acme"
count: int = 42
ratio: float = 3.14
is_active: bool = True

# Collection types (Python 3.9+)
names: list[str] = ["alice", "bob"]
scores: dict[str, int] = {"alice": 95, "bob": 87}
unique_ids: set[int] = {1, 2, 3}
coordinates: tuple[float, float] = (37.5, 127.0)
```

### Function signatures

```python
def greet(name: str, times: int = 1) -> str:
    return f"Hello, {name}! " * times

def process_items(items: list[dict[str, int]]) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items:
        result.update(item)
    return result
```

### Union and Optional

```python
from typing import Union

# Python 3.10+ syntax
def parse_value(value: str | int) -> str:
    return str(value)

# Optional is shorthand for X | None
def find_user(user_id: int) -> dict[str, str] | None:
    users = {"1": {"name": "Alice"}}
    return users.get(str(user_id))
```

### TypedDict: Adding structure to dictionaries

```python
from typing import TypedDict, NotRequired

class UserConfig(TypedDict):
    name: str
    email: str
    age: NotRequired[int]  # Optional field

def create_user(config: UserConfig) -> None:
    print(f"Creating user: {config['name']}")

# mypy catches incorrect keys or types
create_user({"name": "Alice", "email": "a@b.com"})  # OK
create_user({"name": 123, "email": "a@b.com"})      # mypy error!
```

### Protocol: Structural subtyping

```python
from typing import Protocol

class Serializable(Protocol):
    def to_dict(self) -> dict[str, str]: ...

class User:
    def to_dict(self) -> dict[str, str]:
        return {"name": self.name}

class Config:
    def to_dict(self) -> dict[str, str]:
        return {"key": self.key}

def save(obj: Serializable) -> None:
    data = obj.to_dict()
    # Both User and Config are valid (they have to_dict method)
```

### Generic types

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Result(Generic[T]):
    def __init__(self, value: T | None = None, error: str | None = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

def fetch_data() -> Result[list[str]]:
    try:
        return Result(value=["data1", "data2"])
    except Exception as e:
        return Result(error=str(e))
```

## mypy Configuration and Practical Usage

### mypy settings in pyproject.toml

```toml
[tool.mypy]
python_version = "3.11"
strict = true                    # Enable all strict options
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true     # Require types on all functions
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true

# Per-library overrides
[[tool.mypy.overrides]]
module = "httpx.*"
ignore_missing_imports = false

[[tool.mypy.overrides]]
module = "legacy_module.*"
ignore_errors = true             # Gradual migration for legacy code
```

### Common errors mypy catches

```python
# Error 1: Return type mismatch
def get_name() -> str:
    return None  # error: Incompatible return value type (got "None", expected "str")

# Error 2: Wrong argument type
def add(a: int, b: int) -> int:
    return a + b

add("1", "2")  # error: Argument 1 has incompatible type "str"; expected "int"

# Error 3: Missing None check
def process(value: str | None) -> str:
    return value.upper()  # error: Item "None" has no attribute "upper"

# Error 4: Incomplete dict type
data: dict[str, int] = {}
data["count"] = "five"  # error: Incompatible types in assignment
```

### Gradual type adoption strategy

Adding types all at once to an existing project is impractical. Adopt gradually.

```toml
# Phase 1: Start with loose settings
[tool.mypy]
python_version = "3.11"
warn_return_any = true
# strict = false (default)

# Phase 2: Apply strict only to new files
[[tool.mypy.overrides]]
module = "acme_utils.new_module.*"
disallow_untyped_defs = true

# Phase 3: Switch to full strict
[tool.mypy]
strict = true
```

## PEP 561: Distributing Type Information with Packages

For users of your package to benefit from type checking, you need a PEP 561 marker.

### py.typed marker file

```bash
# src/acme_utils/py.typed (empty file)
touch src/acme_utils/py.typed
```

```toml
# Include as package data in pyproject.toml
[tool.setuptools.package-data]
acme_utils = ["py.typed", "*.pyi"]
```

### Inline types vs stub files

| Approach | File | Advantage | Disadvantage |
|---|---|---|---|
| Inline types | Directly in `.py` files | Types always in sync with code | Minor runtime import cost |
| Stub files | `.pyi` files | Suitable for C extensions or legacy code | Requires sync management |

### Stub file example

```python
# src/acme_utils/core.pyi
from typing import overload

class Engine:
    def __init__(self, config: dict[str, str]) -> None: ...

    @overload
    def run(self, query: str) -> str: ...
    @overload
    def run(self, query: list[str]) -> list[str]: ...
    def run(self, query: str | list[str]) -> str | list[str]: ...
```

### stubgen: Automatic stub generation

```bash
# mypy's stubgen tool
pip install mypy
stubgen src/acme_utils -o stubs/

# Check generated stubs
cat stubs/acme_utils/core.pyi
```

## Ruff: Ultra-Fast Linter and Formatter

Ruff is a Python linter written in Rust that replaces flake8 + isort + pycodestyle in a single tool.

```toml
# pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
]
ignore = ["E501"]  # line-too-long (formatter handles it)

[tool.ruff.lint.isort]
known-first-party = ["acme_utils"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

```bash
# Run linting
ruff check .
ruff check --fix .  # Auto-fix what can be fixed

# Run formatting
ruff format .
ruff format --check .  # Verify-only for CI
```

### Ruff vs traditional tools speed comparison

```text
Project: 10,000 lines of Python code
- flake8 + isort + black: ~5 seconds
- ruff check + ruff format: ~0.1 seconds (50x faster)
```

## Integrating Type Checking and Linting in CI

```yaml
name: Quality
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"

      # Lint (fastest - run first)
      - run: ruff check .
      - run: ruff format --check .

      # Type checking
      - run: mypy src

      # Tests
      - run: pytest --cov=acme_utils
```

## pyright: An Alternative to mypy

```toml
# pyproject.toml
[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "strict"
reportMissingImports = true
reportMissingTypeStubs = true
```

```bash
pip install pyright
pyright src/
```

| Aspect | mypy | pyright |
|---|---|---|
| Language | Python | TypeScript (Node.js) |
| Speed | Moderate | Fast |
| IDE integration | Moderate | Optimized for VSCode (Pylance) |
| Ecosystem | Broadest | Growing rapidly |
| Config difficulty | Medium | Low |

## Practical Type Hint Patterns

### Callable types

```python
from typing import Callable

# Function that takes a function as argument
def retry(
    func: Callable[[], str],
    max_attempts: int = 3,
) -> str:
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception:
            if attempt == max_attempts - 1:
                raise
    return ""  # unreachable, but makes mypy happy

# Decorator type
from typing import TypeVar, ParamSpec
from functools import wraps

P = ParamSpec("P")
R = TypeVar("R")

def log_calls(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

### Literal types

```python
from typing import Literal

def set_log_level(level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]) -> None:
    print(f"Setting level to {level}")

set_log_level("INFO")     # OK
set_log_level("VERBOSE")  # mypy error: not in Literal values
```

### Self type (Python 3.11+)

```python
from typing import Self

class Builder:
    def __init__(self) -> None:
        self._name: str = ""
        self._version: str = ""

    def name(self, name: str) -> Self:
        self._name = name
        return self

    def version(self, version: str) -> Self:
        self._version = version
        return self

# Method chaining is type-safe
builder = Builder().name("acme").version("1.0")
```

### Overload: Different return types based on input

```python
from typing import overload

@overload
def process(data: str) -> str: ...
@overload
def process(data: bytes) -> bytes: ...
@overload
def process(data: list[str]) -> list[str]: ...

def process(data: str | bytes | list[str]) -> str | bytes | list[str]:
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, bytes):
        return data.upper()
    else:
        return [item.upper() for item in data]

# mypy infers exact return types
result: str = process("hello")        # OK
result2: bytes = process(b"hello")    # OK
result3: list[str] = process(["a"])   # OK
```

## Automatic Checks with pre-commit

Running type checks and linting automatically before commits prevents basic issues from reaching PRs.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.5
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
          - pydantic>=2.5
```

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Manual full run
pre-commit run --all-files
```

## Measuring Type Check Coverage

```bash
# Generate mypy report
mypy src --html-report reports/mypy

# Or text summary
mypy src --txt-report reports/mypy
cat reports/mypy/index.txt
```

```text
Module                Lines  Precise  Imprecise  Any
acme_utils            450    420      20         10
acme_utils.core       200    195      3          2
acme_utils.config     120    118      2          0
acme_utils.cli        130    107      15         8
```

Tracking type coverage in CI lets you gradually increase type safety.

Modules with high `Any` ratios are gaps in type safety. Prioritize adding types to those modules first for the most efficient improvement in overall project type reliability. The goal is to maintain a `Precise` ratio above 90%.

In practice, applying mypy strict mode only to new modules first while setting `ignore_errors = true` for legacy modules — then gradually reducing exceptions — is the realistic strategy.

## Answering the Opening Questions

- **Why are type hints needed, and do they affect runtime?**
  - Type hints make code intent explicit so tools like mypy can catch type mismatches, missing None checks, and wrong argument passes before execution. At runtime, type hints are ignored so they don't affect performance. However, `typing` module imports add slight startup time.
- **What errors does `mypy` catch?**
  - Return type mismatches, method calls on possibly-None values, wrong-type argument passing, access to nonexistent attributes, and missing required keys in TypedDict. Using `strict` mode also errors on untyped function definitions, ensuring type safety across the entire project.
- **How do you provide type information to package users?**
  - Add an empty `src/package/py.typed` file and include it in `pyproject.toml`'s package-data. This is the PEP 561 marker signaling that mypy and pyright should read type information from this package. Inline types are most convenient; for C extensions or legacy code, use `.pyi` stub files.

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

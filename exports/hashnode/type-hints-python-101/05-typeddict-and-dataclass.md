
# TypedDict and dataclass

> Type Hints in Python 101 Series (5/10)

<!-- a-grade-intro:begin -->

**Key Question**: How do you give a dictionary named, typed keys — or define a lightweight class with automatic `__init__`, `__repr__`, and type annotations?

> Dictionaries are everywhere in Python — API responses, config files, database rows. But `dict[str, Any]` tells the type checker nothing about which keys exist or what their values are. `TypedDict` solves this by defining expected keys and their types. For richer data models, `dataclass` generates boilerplate methods while keeping full type support. This article covers both tools and when to use each.

<!-- a-grade-intro:end -->

## What You Will Learn

- TypedDict for dictionaries with known keys and typed values
- dataclass for structured data with automatic method generation
- When to choose TypedDict vs. dataclass
- Advanced patterns: optional keys, inheritance, frozen dataclasses

## Why It Matters

Most Python bugs with dictionaries come from key typos and wrong value types. `user["nmae"]` silently returns a `KeyError` at runtime. TypedDict catches this statically. For objects that need methods and behavior, dataclass provides a clean alternative to manually writing `__init__`, `__eq__`, and `__repr__` while maintaining full type checker support.

> TypedDict = typed dictionary. dataclass = typed class without boilerplate.

Both turn unstructured data into structured, type-safe code.

## Concept at a Glance

> TypedDict annotates dictionary shapes. dataclass generates class boilerplate from type annotations.

```text
TypedDict                        dataclass
┌──────────────────┐    ┌──────────────────────┐
│ {"name": str,    │    │ class User:           │
│  "age": int}     │    │   name: str           │
│                  │    │   age: int            │
│ Still a dict     │    │   __init__ generated  │
│ at runtime       │    │   __repr__ generated  │
└──────────────────┘    └──────────────────────┘
```

## Key Concepts

| Term | Description |
| --- | --- |
| TypedDict | A dict subtype with specific keys and value types |
| dataclass | A decorator that generates `__init__`, `__repr__`, `__eq__` from annotations |
| total | TypedDict parameter — `True` means all keys required (default) |
| frozen | dataclass parameter — `True` makes instances immutable |
| field | dataclass function for per-field configuration (defaults, factories) |

## Before / After

**Before — Plain dict:**

```python
def create_user(name: str, age: int) -> dict[str, object]:
    return {"name": name, "age": age}


user = create_user("Alice", 30)
print(user["nmae"])  # KeyError at runtime — no static check
```

**After — TypedDict:**

```python
from typing import TypedDict


class User(TypedDict):
    name: str
    age: int


def create_user(name: str, age: int) -> User:
    return {"name": name, "age": age}


user = create_user("Alice", 30)
# user["nmae"]  # mypy error: TypedDict "User" has no key "nmae"
```

## Hands-On Steps

### Step 1: Define a TypedDict

```python
from typing import TypedDict


class UserProfile(TypedDict):
    name: str
    age: int
    email: str


# Correct usage
profile: UserProfile = {"name": "Alice", "age": 30, "email": "alice@example.com"}

# Missing key — mypy error
# bad: UserProfile = {"name": "Alice", "age": 30}
```

TypedDict is a regular `dict` at runtime. The type annotations only exist for the type checker.

### Step 2: Optional Keys with total=False

```python
from typing import TypedDict


class UserProfile(TypedDict):
    name: str
    age: int


class ExtendedProfile(UserProfile, total=False):
    bio: str
    website: str


# bio and website are optional
profile: ExtendedProfile = {"name": "Alice", "age": 30}
profile_full: ExtendedProfile = {
    "name": "Alice",
    "age": 30,
    "bio": "Engineer",
    "website": "https://example.com",
}
```

### Step 3: Basic dataclass

```python
from dataclasses import dataclass


@dataclass
class Product:
    name: str
    price: int
    quantity: int = 0


product = Product(name="Python Book", price=35)
print(product)          # Product(name='Python Book', price=35, quantity=0)
print(product.name)     # Python Book
print(product == Product("Python Book", 35, 0))  # True
```

`@dataclass` reads the type annotations and generates `__init__`, `__repr__`, and `__eq__` automatically.

### Step 4: Frozen dataclass for Immutability

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float


point = Point(1.0, 2.0)
# point.x = 3.0  # FrozenInstanceError — immutable
```

Frozen dataclasses are hashable and can be used as dictionary keys or set elements.

### Step 5: dataclass with field()

```python
from dataclasses import dataclass, field


@dataclass
class Order:
    customer: str
    items: list[str] = field(default_factory=list)
    total: int = 0
    _internal: str = field(default="", repr=False, compare=False)


order = Order(customer="Alice")
order.items.append("Python Book")
print(order)  # Order(customer='Alice', items=['Python Book'], total=0)
```

`field(default_factory=list)` avoids the mutable default argument trap. `repr=False` excludes the field from the string representation.

## What to Notice in This Code

- TypedDict is a dict at runtime — it works with JSON serialization and dict APIs
- dataclass generates methods from type annotations — less boilerplate, same type safety
- `frozen=True` makes dataclass instances immutable and hashable
- `field(default_factory=...)` handles mutable defaults safely

## 5 Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Mutable default in dataclass | `list` default is shared across instances | Use `field(default_factory=list)` |
| Treating TypedDict as a class | TypedDict has no methods or `__init__` | It is a dict — use dict syntax |
| Mixing TypedDict and dataclass | Different purposes — one is a dict, one is a class | Choose based on the use case |
| Forgetting `total=False` for optional keys | All keys become required | Use inheritance with `total=False` |
| Using dataclass for serialization | No built-in JSON support | Use Pydantic or `dataclasses.asdict()` |

## Real-World Applications

- API response typing with TypedDict for JSON payloads
- Configuration models with dataclass for application settings
- Database row mapping with TypedDict for query results
- Domain models with frozen dataclass for value objects
- Event payloads with TypedDict for message queue contracts

## How Senior Engineers Think About This

Senior engineers choose TypedDict when the data is fundamentally a dictionary — JSON from an API, rows from a database, kwargs being passed around. They choose dataclass when the data is an object with identity and potentially behavior.

The decision is not about features but about semantics. A TypedDict says "this is a dict with known keys." A dataclass says "this is a domain object." If you need methods, validation, or immutability guarantees, use dataclass (or Pydantic). If you need dict compatibility for serialization, use TypedDict.

## Checklist

- [ ] Used TypedDict for dict-shaped data with known keys
- [ ] Used dataclass for structured objects with behavior
- [ ] Applied `field(default_factory=...)` for mutable defaults
- [ ] Used `frozen=True` for immutable value objects
- [ ] Chose between TypedDict and dataclass based on semantics

## Exercises

1. Define a `BookInfo` TypedDict with `title: str`, `author: str`, `year: int`, and optional `isbn: str`. Write a function that accepts and returns it.

2. Create a `BankAccount` dataclass with `owner: str`, `balance: int`, and methods `deposit(amount: int)` and `withdraw(amount: int)`. Use `frozen=False`.

3. Convert a function that returns `dict[str, Any]` to return a TypedDict, and verify with mypy that key typos are caught.

## Summary and Next Steps

TypedDict adds type safety to dictionaries by defining expected keys and value types. dataclass generates boilerplate class methods from type annotations. Use TypedDict for dict-shaped data and dataclass for structured objects. Both integrate seamlessly with mypy and pyright.

In the next article, we will explore Protocol and structural typing — defining interfaces without inheritance.

- [What Are Python Type Hints?](./01-what-is-type-hint.md)
- [Basic Types and Collection Types](./02-basic-and-collection-types.md)
- [Optional and Union](./03-optional-and-union.md)
- [Function Type Hints](./04-function-type-hints.md)
- **TypedDict and dataclass (current)**
- [Protocol and Structural Typing](./06-protocol-and-structural-typing.md)
- [Understanding Generics](./07-generic.md)
- [Using mypy and pyright](./08-mypy-and-pyright.md)
- [Pydantic and Type Hints](./09-pydantic-and-type-hints.md)
- [Type Hint Best Practices](./10-type-hints-best-practices.md)
## References

- [Python docs — typing.TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict)
- [Python docs — dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [PEP 589 — TypedDict](https://peps.python.org/pep-0589/)
- [Real Python — Data Classes](https://realpython.com/python-data-classes/)

Tags: Python, Type Hints, TypedDict, dataclass, Structured Data, Data Modeling

---

© 2026 YeongseonBooks. All rights reserved.

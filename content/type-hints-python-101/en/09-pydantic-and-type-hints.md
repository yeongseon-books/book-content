---
series: type-hints-python-101
episode: 9
title: Pydantic and Type Hints
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Python
  - Type Hints
  - Pydantic
  - BaseModel
  - Data Validation
  - FastAPI
seo_description: Use Pydantic BaseModel for runtime data validation and serialization powered by Python type hints.
last_reviewed: '2026-05-04'
---

# Pydantic and Type Hints

This is post 9 in the Type Hints in Python 101 series.

> Type Hints in Python 101 Series (9/10)

<!-- a-grade-intro:begin -->

**Key Question**: Can type hints enforce data correctness at runtime, not just during static analysis?

> Python type hints are metadata — the interpreter ignores them. mypy checks them statically, but nothing stops invalid data from entering your system at runtime. Pydantic changes this equation. It reads type hints and generates runtime validators that reject bad data immediately. This is why FastAPI chose Pydantic as its foundation. This article covers BaseModel, Field, validators, and FastAPI integration patterns.

<!-- a-grade-intro:end -->

## What You Will Learn

- Pydantic BaseModel fundamentals and usage
- Field for fine-grained validation rules
- field_validator and model_validator for custom logic
- FastAPI integration patterns

## Why It Matters

External data is never trustworthy. API requests, config files, database rows — all can contain unexpected values. Manual if-else validation is verbose, fragile, and easy to forget. Pydantic generates validation logic from type hints, turning annotations into executable contracts that reject bad data with detailed error messages.

> Pydantic = type hints as runtime validation rules.

It elevates type hints from "documentation" to "enforceable contracts."

## Concept at a Glance

> Pydantic reads class type hints and generates a validator. Invalid data raises ValidationError with detailed messages.

```text
Input data (dict/JSON)
       │
  BaseModel.__init__
       │
  type-hint-based validation
       │
  ├── pass → model instance
  └── fail → ValidationError
```

## Key Concepts

| Term | Description |
| --- | --- |
| BaseModel | Pydantic's base class for validated data models |
| Field | Defines per-field validation rules and metadata |
| field_validator | Decorator for custom single-field validation logic |
| model_validator | Decorator for cross-field validation logic |
| BaseSettings | Model that reads values from environment variables |

## Before / After

**Before — Manual validation:**

```python
def create_user(data: dict) -> dict:
    if "name" not in data:
        raise ValueError("name is required")
    if not isinstance(data["name"], str):
        raise ValueError("name must be a string")
    if "age" not in data:
        raise ValueError("age is required")
    if not isinstance(data["age"], int) or data["age"] < 0:
        raise ValueError("age must be a non-negative integer")
    return data
```

**After — Pydantic model:**

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str
    age: int = Field(ge=0)
```

## Hands-On Steps

### Step 1: BaseModel Basics

```python
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
    email: str


# Create from keyword arguments
user = User(name="Alice", age=30, email="alice@example.com")
print(user.name)       # Alice
print(user.model_dump())  # {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}

# Automatic type coercion
user2 = User(name="Bob", age="25", email="bob@example.com")
print(user2.age)       # 25 (str → int coerced)
print(type(user2.age)) # <class 'int'>
```

Pydantic coerces compatible types automatically. `"25"` becomes `int(25)`, `"true"` becomes `bool(True)`.

### Step 2: Field for Validation Rules

```python
from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: int = Field(gt=0, description="Price in cents")
    quantity: int = Field(ge=0, default=0)
    tags: list[str] = Field(default_factory=list, max_length=10)


product = Product(name="Python Book", price=3500)
print(product.quantity)  # 0 (default)

# Validation failure
# Product(name="", price=-100)
# ValidationError: name must have at least 1 character,
#                  price must be greater than 0
```

### Step 3: field_validator for Custom Logic

```python
from pydantic import BaseModel, field_validator


class SignupRequest(BaseModel):
    username: str
    password: str
    email: str

    @field_validator("username")
    @classmethod
    def username_must_be_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Only alphanumeric characters allowed")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
```

Validators can also transform values. The `username` validator normalizes to lowercase.

### Step 4: model_validator for Cross-Field Logic

```python
from pydantic import BaseModel, model_validator


class DateRange(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode="after")
    def end_after_start(self) -> "DateRange":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


# DateRange(start_date="2026-01-10", end_date="2026-01-01")
# ValidationError: end_date must be after start_date
```

`mode="after"` runs after individual field validation completes.

### Step 5: FastAPI Integration

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)
    email: str


class UserResponse(BaseModel):
    id: int
    name: str
    age: int


@app.post("/users", response_model=UserResponse)
def create_user(request: CreateUserRequest) -> UserResponse:
    # request is already a validated Pydantic model
    return UserResponse(id=1, name=request.name, age=request.age)
```

FastAPI automatically parses request bodies into Pydantic models. Validation failures return 422 responses with detailed error messages.

## What to Notice in This Code

- Inheriting from BaseModel turns type hints into validation rules
- Field adds constraints like ranges, lengths, and defaults
- Validators can both validate and transform values
- FastAPI integration automates request/response validation

## 5 Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Mutable default values | `list[str] = []` shares reference across instances | Use `Field(default_factory=list)` |
| Missing @classmethod on validators | Pydantic v2 requires it | Add `@classmethod` below `@field_validator` |
| Using `.dict()` in Pydantic v2 | Deprecated method | Use `model_dump()` and `model_dump_json()` |
| Over-relying on type coercion | `"abc"` cannot coerce to `int` | Use strict mode to disable coercion |
| Optional field without default | Field becomes required | Use `Optional[str] = None` |

## Real-World Applications

- FastAPI endpoints with request/response models defining API contracts
- BaseSettings for environment variable configuration (12-Factor App)
- Data pipelines using models as validation gates for raw data
- ORM-to-API layer conversion with separate Pydantic and SQLAlchemy models
- Auto-generated JSON Schema for API documentation and client code generation

## How Senior Engineers Think About This

Senior engineers place Pydantic at system boundaries — API requests, external service responses, config files, anywhere "untrusted data" enters the system. Inside the boundary, validated data flows through internal logic using plain dataclasses or typed dicts without re-validation overhead.

Not every data class needs to be a BaseModel. Internal domain objects that never touch external data are simpler as dataclasses. The principle is: validate once at the boundary, trust the types internally. This keeps the codebase performant and avoids unnecessary Pydantic overhead on hot paths.

## Checklist

- [ ] Defined data models with BaseModel
- [ ] Added validation rules with Field
- [ ] Applied field_validator for custom single-field logic
- [ ] Used model_validator for cross-field validation
- [ ] Integrated with FastAPI for automated request validation

## Exercises

1. Create an `OrderItem` model with `product_name` (1+ chars), `quantity` (1+), `unit_price` (> 0), and a computed `total_price` field.

2. Write a signup model where `password` and `password_confirm` must match, using `model_validator`.

3. Use `BaseSettings` to read `DATABASE_URL`, `SECRET_KEY`, and `DEBUG` (default False) from environment variables.

## Summary and Next Steps

Pydantic turns type hints into runtime validation rules. BaseModel, Field, and validators combine to create powerful yet concise data validation. FastAPI integration automates API request/response validation. Place Pydantic at system boundaries for maximum impact with minimum overhead.

In the final article, we will establish best practices for applying type hints effectively across a project.

<!-- toc:begin -->
- [What Are Python Type Hints?](./01-what-is-type-hint.md)
- [Basic Types and Collection Types](./02-basic-and-collection-types.md)
- [Optional and Union](./03-optional-and-union.md)
- [Function Type Hints](./04-function-type-hints.md)
- [TypedDict and dataclass](./05-typeddict-and-dataclass.md)
- [Protocol and Structural Typing](./06-protocol-and-structural-typing.md)
- [Understanding Generics](./07-generic.md)
- [Using mypy and pyright](./08-mypy-and-pyright.md)
- **Pydantic and Type Hints (current)**
- [Type Hint Best Practices](./10-type-hints-best-practices.md)
<!-- toc:end -->

## References

- [Pydantic documentation](https://docs.pydantic.dev/latest/)
- [FastAPI docs — Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [Real Python — Pydantic](https://realpython.com/python-pydantic/)

Tags: Python, Type Hints, Pydantic, BaseModel, Data Validation, FastAPI

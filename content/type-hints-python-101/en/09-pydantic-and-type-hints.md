---
series: type-hints-python-101
episode: 9
title: "Type Hints in Python 101 (9/10): Pydantic and Type Hints"
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
  - Pydantic
  - BaseModel
  - Data Validation
  - FastAPI
seo_description: Use Pydantic BaseModel for runtime data validation and serialization powered by Python type hints.
last_reviewed: '2026-05-17'
---

# Type Hints in Python 101 (9/10): Pydantic and Type Hints

Static type checking protects the person writing the code. Real services also need protection from the data entering the system. A malformed email, an underage signup, or mismatched password fields are runtime boundary problems, not mypy problems.

This is post 9 in the Type Hints in Python 101 series. In this article, we will build one continuous `CreateUserRequest` → FastAPI endpoint → `UserResponse` workflow so you can see how Pydantic turns type hints into runtime validation, how a bad request becomes a 422 response, and how the corrected request becomes a successful response.


![Type Hints in Python 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/09/09-01-big-picture.en.png)
*Type Hints in Python 101 chapter 9 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Pydantic and Type Hints?
- Which signal should the example or diagram make visible for Pydantic and Type Hints?
- What failure should be prevented first when Pydantic and Type Hints reaches a real system?

## What You Will Learn

- How to turn type hints into runtime validation rules
- Where `Field`, `field_validator`, and `model_validator` each fit in one request flow
- What FastAPI actually returns when validation fails
- How static typing and runtime validation divide responsibility

> Type hints help authors before execution. Pydantic protects the application at the input boundary.

## Why It Matters

Many production bugs start before business logic runs. The client sends an empty username, an invalid email, a value outside the allowed range, or two fields that contradict each other. If that boundary logic is handwritten with scattered `if` statements, it becomes repetitive, inconsistent, and easy to forget.

Pydantic lets the boundary contract live in one place. The key is not memorizing `BaseModel`, `Field`, and validators as isolated features. The useful skill is seeing one request move through **model definition → field constraints → custom validators → FastAPI 422 failure → corrected success response**.

```text
HTTP request JSON
      │
CreateUserRequest validation
      │
  ├── fail → 422 response
  └── pass → endpoint runs
                │
          UserResponse returned
```

## Key Concepts

| Term | Description |
| --- | --- |
| BaseModel | Pydantic's base class for validated data models |
| Field | Declares field constraints such as length, range, defaults, and metadata |
| field_validator | Validates or normalizes one field at a time |
| model_validator | Validates relationships across multiple fields |
| 422 Unprocessable Entity | FastAPI's response when the JSON body is readable but fails validation |

## Before / After

```python
def create_user(data: dict) -> dict:
    if not data.get("username"):
        raise ValueError("username is required")
    if len(data.get("password", "")) < 8:
        raise ValueError("password is too short")
    if data.get("password") != data.get("password_confirm"):
        raise ValueError("passwords do not match")
    return data
```

```python
class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8)
    password_confirm: str

    @model_validator(mode="after")
    def passwords_match(self) -> "CreateUserRequest":
        if self.password != self.password_confirm:
            raise ValueError("password_confirm must match password")
        return self
```

Instead of spreading validation rules across manual branches, the request contract becomes explicit and reusable.

## Follow One Request Lifecycle End to End

This article keeps one signup API example all the way through.

### Step 1: Start with request and response models

```python
from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    username: str
    email: str
    age: int
    password: str
    password_confirm: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    age: int
```

At this stage the API shape is visible, but the boundary rules are still too loose. We know the fields exist; we have not yet said what counts as valid input.

### Step 2: Add field-level constraints with `Field`

```python
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    age: int = Field(ge=13, le=120)
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)
```

Now the boundary rules are concrete.

- `username` must be 3–20 characters.
- `email` must be a valid email address.
- `age` must be between 13 and 120.
- Both password fields must meet the minimum length.

### Step 3: Use `field_validator` for single-field normalization

```python
from pydantic import BaseModel, EmailStr, Field, field_validator

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    age: int = Field(ge=13, le=120)
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized.replace("_", "").isalnum():
            raise ValueError("username must contain only letters, numbers, or underscores")
        return normalized
```

This validator does two jobs.

- It normalizes whitespace and casing.
- It rejects characters outside the allowed username format.

That is a good example of a field validator: one input, one rule set, optional normalization.

### Step 4: Use `model_validator` for cross-field rules

```python
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    age: int = Field(ge=13, le=120)
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized.replace("_", "").isalnum():
            raise ValueError("username must contain only letters, numbers, or underscores")
        return normalized

    @model_validator(mode="after")
    def passwords_match(self) -> "CreateUserRequest":
        if self.password != self.password_confirm:
            raise ValueError("password_confirm must match password")
        return self
```

This is where model-level validation earns its place. A single field cannot tell whether the two password fields agree, so the model checks the relationship after individual field validation succeeds.

### Step 5: Connect the model to FastAPI

```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

app = FastAPI()

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    age: int = Field(ge=13, le=120)
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized.replace("_", "").isalnum():
            raise ValueError("username must contain only letters, numbers, or underscores")
        return normalized

    @model_validator(mode="after")
    def passwords_match(self) -> "CreateUserRequest":
        if self.password != self.password_confirm:
            raise ValueError("password_confirm must match password")
        return self

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    age: int

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(request: CreateUserRequest) -> UserResponse:
    return UserResponse(
        id=101,
        username=request.username,
        email=request.email,
        age=request.age,
    )
```

Now validation happens before the endpoint body executes. Invalid input never reaches the business logic as a half-trusted dictionary.

### Step 6: Watch a bad request fail with a real 422 response

```http
POST /users
Content-Type: application/json

{
  "username": "  Min!  ",
  "email": "not-an-email",
  "age": 10,
  "password": "short",
  "password_confirm": "different"
}
```

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "username"],
      "msg": "Value error, username must contain only letters, numbers, or underscores",
      "input": "  Min!  "
    },
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "not-an-email"
    },
    {
      "type": "greater_than_equal",
      "loc": ["body", "age"],
      "msg": "Input should be greater than or equal to 13",
      "input": 10,
      "ctx": {"ge": 13}
    },
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "short",
      "ctx": {"min_length": 8}
    }
  ]
}
```

This is the missing runtime story many explanations skip. FastAPI does not just say “validation failed”; it returns structured error data that tells the client exactly which field violated which rule.

For the cross-field mismatch, the model validator adds a body-level error like this:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body"],
      "msg": "Value error, password_confirm must match password"
    }
  ]
}
```

### Step 7: Correct the request and observe the success response

```http
POST /users
Content-Type: application/json

{
  "username": "  Min_Jun  ",
  "email": "minjun@example.com",
  "age": 24,
  "password": "securepass1",
  "password_confirm": "securepass1"
}
```

```json
{
  "id": 101,
  "username": "min_jun",
  "email": "minjun@example.com",
  "age": 24
}
```

Two details matter here.

- The username was normalized to `min_jun` by the field validator.
- The endpoint body gets a fully validated model, so internal code can focus on business logic instead of defensive parsing.

## What to Notice in This Code

- Static typing and runtime validation solve different failure points
- `Field` handles field constraints, `field_validator` handles single-field logic, and `model_validator` handles cross-field logic
- FastAPI automatically turns validation failures into structured 422 responses
- Response models protect the output contract as well as the input contract

## 5 Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Treating `BaseModel`, `Field`, and validators as unrelated snippets | Readers never see how one request flows through the system | Build one request lifecycle end to end |
| Mentioning 422 without showing the payload | Failure remains abstract | Include the invalid request and the response body |
| Using mutable defaults like `list[str] = []` | Instances can share state accidentally | Use `Field(default_factory=list)` |
| Wrapping every internal object with Pydantic | Validation overhead spreads beyond the boundary | Place Pydantic at system boundaries first |
| Trusting coercion too casually | Unintended input may pass farther than expected | Add explicit constraints and validators for important paths |

## Real-World Applications

- FastAPI request models that define API contracts for frontend and backend teams
- Environment and settings validation at application startup
- Queue consumers validating external event payloads before processing
- Response models preventing accidental schema drift in public APIs

## How Senior Engineers Think About This

Senior engineers usually place Pydantic at the edges of the system: HTTP requests, external API responses, config loading, and other untrusted inputs. Validate once at the boundary, then let simpler typed objects or function signatures carry trusted data through the interior.

That division of labor matters. Static checkers help the author before runtime. Pydantic protects the service at runtime. Used together, they cover different failure moments instead of duplicating the same concern.

## Checklist

- [ ] Organized the example around one request/response workflow
- [ ] Used `Field`, `field_validator`, and `model_validator` in the right places
- [ ] Examined a bad request and its 422 response body
- [ ] Examined the corrected request and its success response
- [ ] Can explain the difference between static type checking and runtime validation

## Exercises

1. Build a `CreateOrderRequest` model with rules for `items`, `currency`, and `total_amount`, then write one invalid request and one successful request.

2. Replace the password-confirm rule with a `start_date` / `end_date` cross-field validator.

3. Add `created_at` to the response model and observe how the response contract becomes more explicit.

## Summary and Next Steps

Pydantic turns type hints into runtime validation contracts, but the real lesson is the full request lifecycle: model definition, field constraints, validators, a concrete 422 failure, and a corrected success response. Once that arc is clear, FastAPI's value and Pydantic's role become much more concrete.

In the final article, we will turn the series into an operating guide for applying type hints across a real codebase.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Pydantic and Type Hints?**
  - The article treats Pydantic and Type Hints as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Pydantic and Type Hints?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Pydantic and Type Hints reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Type Hints in Python 101 (1/10): What Are Python Type Hints?](./01-what-is-type-hint.md)
- [Type Hints in Python 101 (2/10): Basic Types and Collection Types](./02-basic-and-collection-types.md)
- [Type Hints in Python 101 (3/10): Optional and Union](./03-optional-and-union.md)
- [Type Hints in Python 101 (4/10): Function Type Hints](./04-function-type-hints.md)
- [Type Hints in Python 101 (5/10): TypedDict and dataclass](./05-typeddict-and-dataclass.md)
- [Type Hints in Python 101 (6/10): Protocol and Structural Typing](./06-protocol-and-structural-typing.md)
- [Type Hints in Python 101 (7/10): Understanding Generics](./07-generic.md)
- [Type Hints in Python 101 (8/10): Using mypy and pyright](./08-mypy-and-pyright.md)
- **Pydantic and Type Hints (current)**
- Type Hint Best Practices (upcoming)

<!-- toc:end -->

## References

- [Pydantic documentation](https://docs.pydantic.dev/latest/)
- [FastAPI docs — Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI docs — Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [Real Python — Pydantic](https://realpython.com/python-pydantic/)

Tags: Python, Type Hints, Pydantic, BaseModel, Data Validation, FastAPI

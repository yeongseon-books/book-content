---
series: type-hints-python-101
episode: 10
title: "Type Hints in Python 101 (10/10): Type Hint Best Practices"
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
  - Best Practices
  - Gradual Typing
  - Code Quality
  - Team Guidelines
seo_description: Practical guidelines for applying type hints effectively with gradual typing, team standards, and anti-patterns to avoid.
last_reviewed: '2026-05-17'
---

# Type Hints in Python 101 (10/10): Type Hint Best Practices

Type hints do not improve code just because there are more of them. But if the important signatures stay vague, the static checks from the previous article and the runtime boundaries from Pydantic never get enough structure to help. The real question is where to harden first.

This is the final post in the Type Hints in Python 101 series. In this article, we will take one loose `order_service.py` module and run a full hardening pass on it: replacing `Any`, making return types explicit, narrowing unions with helper functions, and verifying the result with a checker so the advice ends as runnable code rather than placeholders.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Type Hint Best Practices?
- Which signal should the example or diagram make visible for Type Hint Best Practices?
- What failure should be prevented first when Type Hint Best Practices reaches a real system?

## Big Picture

![Type Hints in Python 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/10/10-01-big-picture.en.png)

*Type Hints in Python 101 chapter 10 flow overview*

This picture places Type Hint Best Practices inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Type Hint Best Practices is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- Where type hint investment pays off first
- How to shrink `Any` without trying to annotate every local variable
- Why return types and public APIs should be hardened before internal details
- How to turn team guidelines into actual checker configuration

> Good type-hint strategy is not “annotate everything.” It is “make high-cost failure paths fail early.”

## Why It Matters

Legacy Python modules usually combine two problems. First, public function signatures are vague enough that callers do not know the contract. Second, one `Any` return type leaks into half the file and quietly disables the checker downstream.

This article is meant to close the loop from episodes 8 and 9. If type hints are going to become a real engineering habit, you need more than principles. You need a repeatable way to take a messy module, harden it in the right order, and verify that the new contract actually holds.

## Concept at a Glance

```text
Loose signatures / Any spread
            │
Public API + return types hardened
            │
Inputs and outputs made explicit
            │
Union narrowing moved into helpers
            │
Checker passes + team rules recorded
```

## Key Concepts

| Term | Description |
| --- | --- |
| Gradual typing | Strengthening types incrementally instead of all at once |
| Public API | Functions, methods, or classes called from other modules |
| Type narrowing | Refining a Union with checks such as `isinstance` or `is None` |
| Any | Compatible with every type, which also means it can cut off type-checker visibility |
| hardening pass | A focused refactor that strengthens contracts and validates them |

## Before / After

```python
from typing import Any

def process_order(payload: Any) -> Any:
    order_id = payload.get("order_id")
    user = payload.get("user")
    return {"order_id": order_id, "email": user.get("email")}
```

```python
class OrderPayload(TypedDict):
    order_id: int | str
    user: dict[str, str | None]

def process_order(payload: OrderPayload) -> dict[str, str]:
    order_id = parse_order_id(payload["order_id"])
    email = require_user_email(payload["user"])
    return {"order_id": str(order_id), "email": email}
```

The important move is not “add more annotations everywhere.” It is “make the boundary contract precise and move uncertainty into explicit helpers.”

## Run One Module Through a Hardening Pass

This entire article uses a single `order_service.py` example.

### Step 1: Start with a loose module

```python
# order_service.py
from typing import Any

def find_user(user_id):
    if user_id == 1:
        return {"id": 1, "email": "buyer@example.com", "is_active": True}
    return None

def get_config() -> Any:
    return {"currency": "KRW", "retry_limit": 3, "sandbox": False}

class OrderService:
    def create_order(self, payload):
        user = find_user(payload.get("user_id"))
        config = get_config()
        total = sum(item["price"] * item["quantity"] for item in payload.get("items", []))
        return {
            "order_id": payload.get("order_id"),
            "user_email": user.get("email"),
            "currency": config["currency"],
            "total": total,
        }
```

This file has multiple structural problems.

- `find_user()` and `create_order()` barely describe their contract.
- `get_config()` returns `Any`, so downstream checking goes soft immediately.
- `payload.get()` means required fields can silently disappear.
- `user` may be `None`, but `user.get()` assumes the opposite.

### Step 2: Harden public signatures and return types first

In practice, signatures matter more than local variables because they define what every caller is allowed to do.

```python
from typing import TypedDict

class UserRecord(TypedDict):
    id: int
    email: str
    is_active: bool

class OrderItem(TypedDict):
    name: str
    price: int
    quantity: int

class OrderPayload(TypedDict):
    order_id: int | str
    user_id: int
    items: list[OrderItem]

def find_user(user_id: int) -> UserRecord | None:
    if user_id == 1:
        return {"id": 1, "email": "buyer@example.com", "is_active": True}
    return None

def get_config() -> dict[str, str | int | bool]:
    return {"currency": "KRW", "retry_limit": 3, "sandbox": False}
```

This already tells the checker three crucial things.

- `find_user()` can legitimately return `None`.
- `order_id` is still flexible, but only within a known union.
- `get_config()` no longer erases all type information.

### Step 3: Replace `Any` with explicit helpers

The next job is not to annotate every intermediate variable. It is to isolate the uncertain boundary decisions into named helpers.

```python
from typing import TypedDict

class UserRecord(TypedDict):
    id: int
    email: str
    is_active: bool

class OrderItem(TypedDict):
    name: str
    price: int
    quantity: int

class OrderPayload(TypedDict):
    order_id: int | str
    user_id: int
    items: list[OrderItem]

class OrderSummary(TypedDict):
    order_id: str
    user_email: str
    currency: str
    total: int

def find_user(user_id: int) -> UserRecord | None:
    if user_id == 1:
        return {"id": 1, "email": "buyer@example.com", "is_active": True}
    return None

def get_config() -> dict[str, str | int | bool]:
    return {"currency": "KRW", "retry_limit": 3, "sandbox": False}

def parse_order_id(order_id: int | str) -> int:
    if isinstance(order_id, int):
        return order_id
    if order_id.isdigit():
        return int(order_id)
    raise ValueError("order_id must be an int or numeric string")

def require_user_email(user: UserRecord | None) -> str:
    if user is None:
        raise LookupError("user not found")
    if not user["is_active"]:
        raise ValueError("inactive user cannot create orders")
    return user["email"]
```

Notice what changed compared with the old placeholder style.

- `find_user`, `get_config`, and `parse_order_id` now contain real code.
- The “best practice” is executable, not rhetorical.
- Union handling moved into a helper where the narrowing logic is easy to review.

### Step 4: Rewrite the service method around the hardened contract

```python
from typing import TypedDict

class UserRecord(TypedDict):
    id: int
    email: str
    is_active: bool

class OrderItem(TypedDict):
    name: str
    price: int
    quantity: int

class OrderPayload(TypedDict):
    order_id: int | str
    user_id: int
    items: list[OrderItem]

class OrderSummary(TypedDict):
    order_id: str
    user_email: str
    currency: str
    total: int

def find_user(user_id: int) -> UserRecord | None:
    if user_id == 1:
        return {"id": 1, "email": "buyer@example.com", "is_active": True}
    return None

def get_config() -> dict[str, str | int | bool]:
    return {"currency": "KRW", "retry_limit": 3, "sandbox": False}

def parse_order_id(order_id: int | str) -> int:
    if isinstance(order_id, int):
        return order_id
    if order_id.isdigit():
        return int(order_id)
    raise ValueError("order_id must be an int or numeric string")

def require_user_email(user: UserRecord | None) -> str:
    if user is None:
        raise LookupError("user not found")
    if not user["is_active"]:
        raise ValueError("inactive user cannot create orders")
    return user["email"]

class OrderService:
    def create_order(self, payload: OrderPayload) -> OrderSummary:
        order_id = parse_order_id(payload["order_id"])
        user_email = require_user_email(find_user(payload["user_id"]))
        config = get_config()
        currency_value = config["currency"]
        if not isinstance(currency_value, str):
            raise ValueError("currency config must be a string")

        total = sum(item["price"] * item["quantity"] for item in payload["items"])
        return {
            "order_id": str(order_id),
            "user_email": user_email,
            "currency": currency_value,
            "total": total,
        }
```

This is the real before/after payoff.

- The input contract is explicit.
- Optionality and unions are handled intentionally, not accidentally.
- The output contract is explicit too, so callers know exactly what comes back.

### Step 5: Verify the hardening pass with a checker

The article should not stop at “this looks cleaner.” It should end with verification.

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
files = ["order_service.py"]
disallow_untyped_defs = true
warn_return_any = true
warn_unused_ignores = true
no_implicit_optional = true
```

```text
$ mypy order_service.py
Success: no issues found in 1 source file
```

That passing output is what turns the module from “example advice” into “copyable standard.”

### Step 6: Extract the practical prioritization rule

From this one refactor, the prioritization rule becomes concrete.

1. **Start with public signatures and return types.** `find_user()` and `create_order()` are the highest-value contracts.
2. **Cut off `Any` at the source.** `get_config()` is more important than annotating ten local variables downstream.
3. **Move unions into named narrowing helpers.** `parse_order_id()` makes the branch logic reusable and readable.
4. **Record the rule in tool config.** `disallow_untyped_defs` and `warn_return_any` make the standard repeatable.

That is what best practices should mean: not abstract slogans, but a reliable order for hardening real modules.

## What to Notice in This Code

- Public signatures and return types create more safety than annotating every local
- `Any` is most dangerous where it enters the module, not where it is already spreading
- Helper functions are a good home for union narrowing
- A hardening pass is incomplete until a checker verifies it

## 5 Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Leaving example bodies as `...` | Readers cannot run or copy the pattern | Use complete code with real behavior |
| Annotating every local variable first | Verbosity rises without strengthening the real contract | Start with public parameters and returns |
| Keeping `Any` as a temporary shortcut | It weakens everything downstream | Replace it with specific types or a narrow union |
| Using Optional/Union values without narrowing | Runtime and checker errors pile up together | Isolate narrowing in helper functions |
| Ending with advice but no verification | Teams cannot operationalize the standard | Show a passing mypy or pyright result |

## Real-World Applications

- New service modules whose public APIs are typed from day one
- Legacy modules that get a hardening pass whenever they are touched
- Internal helpers that replace ad-hoc `Any` parsing with specific typed transforms
- Team-wide `pyproject.toml` rules that prevent new untyped functions from slipping in

## How Senior Engineers Think About This

Senior engineers use type hints as refactoring infrastructure. They harden the places where ambiguity is expensive: public APIs, central parsing helpers, and modules that many other files depend on. They do not waste early effort on obvious locals when a missing return type or an `Any` escape hatch is doing more damage.

Coverage percentage is less important than contract quality on critical paths. One well-hardened module usually delivers more value than dozens of shallow annotations spread across low-risk code.

## Checklist

- [ ] Hardened public function signatures and return types first
- [ ] Replaced `Any` at the boundary instead of downstream only
- [ ] Moved union handling into helper functions
- [ ] Removed placeholder example bodies so the article stays runnable
- [ ] Verified the final module with checker configuration and passing output

## Exercises

1. Pick one service module in an existing codebase and add return types only to `find_*`, `get_*`, and `create_*` functions first.

2. Find one helper that returns `Any`, replace it with a concrete type or narrow union, and describe how much downstream code becomes more checkable.

3. Extend the `order_service.py` example with `coupon_code: str | None` and write a helper that handles it safely.

## Summary and Next Steps

The best type-hint practices are not about annotating everything equally. They are about hardening the right path in the right order: public signatures, return types, `Any` boundaries, union narrowing helpers, and final verification with a checker. That is how type hints become a repeatable engineering standard instead of a style preference.

This series covered the full working arc: basic annotations, unions, structured data, generics, static checking, runtime validation, and finally how to apply those tools as an operating habit in a real codebase.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Type Hint Best Practices?**
  - The article treats Type Hint Best Practices as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Type Hint Best Practices?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Type Hint Best Practices reaches a real system?**
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
- [Type Hints in Python 101 (9/10): Pydantic and Type Hints](./09-pydantic-and-type-hints.md)
- **Type Hint Best Practices (current)**

<!-- toc:end -->

## References

- [Python docs — typing](https://docs.python.org/3/library/typing.html)
- [mypy docs — Using mypy with an existing codebase](https://mypy.readthedocs.io/en/stable/existing_code.html)
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [Google Python Style Guide — Type Annotations](https://google.github.io/styleguide/pyguide.html#319-type-annotations)
- [Typing Python Libraries](https://typing.python.org/en/latest/guides/libraries.html)

Tags: Python, Type Hints, Best Practices, Gradual Typing, Code Quality, Team Guidelines

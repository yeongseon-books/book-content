---
series: functional-programming-101
episode: 2
title: Pure Functions and Side Effects
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
  - Pure Functions
  - Side Effects
  - Testing
seo_description: Learn what makes a function pure, how to identify side effects, and patterns for separating the two.
last_reviewed: '2026-05-04'
---

# Pure Functions and Side Effects

This is post 2 in the Functional Programming 101 series.

> Functional Programming 101 Series (2/10)

<!-- a-grade-intro:begin -->

**Key Question**: How do you write functions that always return the same output for the same input?

> A pure function does not depend on external state and does not modify external state. Separating side effects from pure logic makes code easier to test and reason about. This article covers the definition of pure functions, how to identify side effects, and patterns for managing them.

<!-- a-grade-intro:end -->

## What You Will Learn

- The two conditions that define a pure function
- Types of side effects and how to spot them
- Patterns for separating pure logic from side effects
- Why pure functions simplify testing

## Why It Matters

A significant portion of bugs comes from unexpected state changes. Pure functions are determined entirely by their inputs and outputs, making them easy to reason about and trivial to test.

> Pure functions = the basic unit of predictable code

You cannot make every function pure in practice, but writing business logic as pure functions and pushing IO to the boundary drastically reduces maintenance cost.

## Concept Overview

> Pure Function Decision Flow

```
Call f(x)
  |
  +-- Same x always gives same result? -- No --> Impure
  |          |
  |         Yes
  |          |
  +-- Modifies external state? --------- Yes --> Impure
  |          |
  |         No
  |          |
  +-- Pure function!
```

## Key Concepts

| Term | Description |
|------|-------------|
| Pure function | A function with referential transparency and no side effects |
| Side effect | Any operation that modifies state outside the function |
| Referential transparency | The property that a function call can be replaced by its result |
| Deterministic | Always producing the same output for the same input |
| Idempotent | Producing the same result no matter how many times it runs |

## Before / After

Convert a function with side effects into a pure function.

```python
# before: impure function depending on global state
discount_rate = 0.1

def apply_discount(price: float) -> float:
    return price * (1 - discount_rate)

print(apply_discount(10000))  # 9000.0
discount_rate = 0.2
print(apply_discount(10000))  # 8000.0 — same input, different result!
```

```python
# after: pure function — all dependencies as arguments
def apply_discount(price: float, discount_rate: float) -> float:
    return price * (1 - discount_rate)

print(apply_discount(10000, 0.1))  # 9000.0
print(apply_discount(10000, 0.1))  # 9000.0 — always the same
```

## Hands-On Steps

### Step 1: Identifying Pure Functions

```python
import random
from datetime import datetime


# Pure: output determined by input alone
def add(a: int, b: int) -> int:
    return a + b

def full_name(first: str, last: str) -> str:
    return f"{first} {last}"


# Impure: depends on external state
def get_random_number() -> int:
    return random.randint(1, 100)  # different every time

def get_current_time() -> str:
    return datetime.now().isoformat()  # depends on clock


print(add(2, 3))          # always 5
print(full_name("John", "Doe"))  # always "John Doe"
print(get_random_number())       # varies
print(get_current_time())        # varies
```

### Step 2: Types of Side Effects

```python
# Side effect 1: modifying external variables
counter = 0

def increment() -> int:
    global counter
    counter += 1  # modifies external state
    return counter


# Side effect 2: IO operations
def save_to_file(data: str) -> None:
    with open("output.txt", "w") as f:
        f.write(data)  # modifies file system


# Side effect 3: mutating arguments
def add_item(items: list, item: str) -> list:
    items.append(item)  # mutates the input list
    return items


# Pure alternative: return a new list
def add_item_pure(items: list, item: str) -> list:
    return [*items, item]  # original untouched, new list created


original = ["a", "b"]
new_list = add_item_pure(original, "c")
print(original)  # ['a', 'b'] — unchanged
print(new_list)  # ['a', 'b', 'c']
```

### Step 3: Separating Pure Logic from Side Effects

```python
from dataclasses import dataclass


@dataclass
class Order:
    items: list[str]
    quantities: list[int]
    prices: list[float]


# Pure functions: computation only
def calculate_subtotal(order: Order) -> float:
    return sum(q * p for q, p in zip(order.quantities, order.prices))

def calculate_tax(subtotal: float, rate: float) -> float:
    return round(subtotal * rate, 2)

def calculate_total(subtotal: float, tax: float) -> float:
    return subtotal + tax

def format_receipt(order: Order, subtotal: float, tax: float, total: float) -> str:
    lines = ["=== Receipt ==="]
    for item, qty, price in zip(order.items, order.quantities, order.prices):
        lines.append(f"  {item} x{qty}: ${qty * price:,.2f}")
    lines.append(f"  Subtotal: ${subtotal:,.2f}")
    lines.append(f"  Tax: ${tax:,.2f}")
    lines.append(f"  Total: ${total:,.2f}")
    return "\n".join(lines)


# Side effects: IO only
def print_receipt(order: Order, tax_rate: float) -> None:
    subtotal = calculate_subtotal(order)
    tax = calculate_tax(subtotal, tax_rate)
    total = calculate_total(subtotal, tax)
    receipt = format_receipt(order, subtotal, tax, total)
    print(receipt)  # the only side effect


order = Order(
    items=["Coffee", "Cake"],
    quantities=[2, 1],
    prices=[4.50, 6.00],
)
print_receipt(order, 0.1)
# === Receipt ===
#   Coffee x2: $9.00
#   Cake x1: $6.00
#   Subtotal: $15.00
#   Tax: $1.50
#   Total: $16.50
```

### Step 4: Testing Pure Functions

```python
# Pure functions: no mocks needed
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    return round(weight_kg / (height_m ** 2), 1)

def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
        return "normal"
    elif bmi < 30:
        return "overweight"
    return "obese"


# Tests are simple — just check input and output
assert calculate_bmi(70, 1.75) == 22.9
assert classify_bmi(22.9) == "normal"
assert classify_bmi(17.0) == "underweight"
assert classify_bmi(27.5) == "overweight"
print("All tests passed")
```

### Step 5: Leveraging Referential Transparency

```python
# Referential transparency: function calls can be replaced by their results
def square(x: int) -> int:
    return x * x

def sum_of_squares(a: int, b: int) -> int:
    return square(a) + square(b)


# Equivalent transformations are safe
result1 = sum_of_squares(3, 4)    # square(3) + square(4)
result2 = 9 + 16                   # replace calls with results
print(result1 == result2)  # True

# This property enables:
# 1. Safe caching (memoization)
# 2. Safe parallel execution
# 3. Safe refactoring
print(sum_of_squares(3, 4))  # 25
```

## What to Notice in This Code

- Pure functions are determined by input and output alone, making tests trivial
- Side effects are not eliminated but pushed to the boundary
- Referential transparency makes caching and parallelism safe
- Functions that receive mutable arguments should return new values instead of modifying them

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Functions depending on global variables | Test results vary with environment | Pass dependencies as arguments |
| Mutable default arguments | State is shared across calls | Use `None` as the default |
| Mutating argument lists in place | Caller's data changes unexpectedly | Create and return a new list |
| Calling print inside pure functions | IO is a side effect | Handle logging in a separate layer |
| Trying to make every function pure | Programs cannot run without IO | Distinguish pure core from impure shell |

## Real-World Applications

- Write business rules as pure functions to simplify unit testing
- Build data transformation pipelines from pure functions
- Cache pure functions safely with `functools.lru_cache`
- Separate validation logic into pure functions in FastAPI dependency injection
- Apply the "pure core + impure shell" architecture

## How Senior Engineers Think About This

"Using pure functions" does not mean eliminating all side effects. Programs must communicate with the outside world, so IO is unavoidable. The key is keeping business logic pure and pushing IO to the program boundary.

This pattern is called "Functional Core, Imperative Shell." Wrap a thick layer of tests around the pure core, and verify the thin IO shell with integration tests. This structure is the most effective approach in practice.

## Checklist

- [ ] I can explain the two conditions of a pure function
- [ ] I can identify side effects in code
- [ ] I can write functions that do not mutate their arguments
- [ ] I can apply the pattern of separating pure logic from side effects
- [ ] I can explain the testing benefits of pure functions

## Exercises

1. Refactor a discount calculator that depends on a global config into a pure function.
2. Separate report output into `format_report` (pure) and `print_report` (side effect).
3. Convert a function that mutates a list in place to one that returns a new list.

## Summary and Next Steps

Pure functions always return the same output for the same input and never modify external state. Pushing side effects to the boundary produces testable, predictable code. The next article covers a concept closely tied to pure functions: **immutable data**.

<!-- toc:begin -->
- [What Is Functional Programming?](./01-what-is-fp.md)
- **Pure Functions and Side Effects (current)**
- [Immutable Data](./03-immutable-data.md)
- [Higher-Order Functions](./04-higher-order-functions.md)
- [map, filter, reduce](./05-map-filter-reduce.md)
- [Closures and Partial Application](./06-closure-and-partial.md)
- [Recursion and Tail Calls](./07-recursion.md)
- [Lazy Evaluation and Generators](./08-lazy-evaluation.md)
- [Function Composition and Pipelines](./09-function-composition.md)
- [Balancing OOP and Functional Programming](./10-oop-and-fp-balance.md)
<!-- toc:end -->

## References

- [Python Official Docs — Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html)
- [Real Python — Pure Functions in Python](https://realpython.com/python-functional-programming/)
- [Functional Core, Imperative Shell — Gary Bernhardt](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)
- [Clean Code — Chapter 3: Functions](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)

Tags: Python, Functional Programming, Pure Functions, Side Effects, Testing

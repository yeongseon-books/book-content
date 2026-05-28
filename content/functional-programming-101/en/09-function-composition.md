---
series: functional-programming-101
episode: 9
title: "Functional Programming 101 (9/10): Function Composition and Pipelines"
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
  - Function Composition
  - Pipelines
  - Data Transformation
seo_description: Combine small functions into complex data transformation pipelines using compose and pipe in Python.
last_reviewed: '2026-05-04'
---

# Functional Programming 101 (9/10): Function Composition and Pipelines

Small functions are easy to understand in isolation. The real challenge starts when a system grows into ten or twenty transformation steps and nobody can quickly tell which stage normalized the payload, which stage filtered it out, and which stage produced the final report. That is the moment composition stops being a math term and becomes an operations problem.

This is the 9th post in the Functional Programming 101 series.

Pipelines help because they make execution order visible. Instead of nesting calls from the inside out, you let data move across named stages. That shift is especially valuable in production data flows, where debugging means asking which step changed the value and why.


![Functional Programming 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/09/09-01-how-a-readable-pipeline-flows.en.png)
*Functional Programming 101 chapter 9 flow overview*

## Questions to Keep in Mind

- What is function composition and why is it useful?
- How do you build a data pipeline by composing small functions?
- When does composition make code harder to read?

## Why It Matters

Writing complex data processing logic as one giant function makes it hard to test and reuse. Composing small single-purpose functions lets you test each step independently and recombine them freely.

> Function composition = building large systems from small parts

This follows the UNIX philosophy (`cat file | grep error | sort | uniq`). Each tool does one thing well, and combinations handle complex tasks.

## Concept Overview

> compose vs pipe — a matter of direction

```text
compose(f, g, h)(x)  =  f(g(h(x)))     <- right to left
pipe(h, g, f)(x)     =  f(g(h(x)))     <- left to right

Pipeline visualization:
  x -> [h] -> [g] -> [f] -> result
```

## How a readable pipeline flows

## Key Concepts

| Term | Description |
|------|-------------|
| Function composition | An operation that combines two functions f, g into f(g(x)) |
| Pipeline | A pattern where data passes through a chain of functions sequentially |
| compose | Composes functions from right to left |
| pipe | Composes functions from left to right |
| Point-free style | Expressing logic through function composition alone, without naming arguments |

## Before / After

Replace nested function calls with a pipeline.

```python
# before: nested calls — read from inside out
result = format_output(
    sort_by_score(
        filter_passing(
            calculate_totals(
                load_data()
            )
        )
    )
)
```

```python
# after: pipeline — read top to bottom
result = pipe(
    load_data,
    calculate_totals,
    filter_passing,
    sort_by_score,
    format_output,
)()
```

## Hands-On Steps

### Step 1: Basic compose and pipe

```python
from collections.abc import Callable
from typing import Any
from functools import reduce

def compose(*funcs: Callable) -> Callable:
    """Composes functions from right to left."""
    def composed(x: Any) -> Any:
        result = x
        for f in reversed(funcs):
            result = f(result)
        return result
    return composed

def pipe(*funcs: Callable) -> Callable:
    """Composes functions from left to right."""
    def piped(x: Any) -> Any:
        result = x
        for f in funcs:
            result = f(result)
        return result
    return piped

# compose: f(g(h(x)))
add_one = lambda x: x + 1
double = lambda x: x * 2
to_str = lambda x: f"Result: {x}"

transform_c = compose(to_str, double, add_one)
print(transform_c(5))  # Result: 12  — (5+1)*2 = 12

# pipe: read order matches execution order
transform_p = pipe(add_one, double, to_str)
print(transform_p(5))  # Result: 12
```

### Step 2: String Processing Pipeline

```python
import re

def strip_whitespace(text: str) -> str:
    return text.strip()

def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text)

def to_lowercase(text: str) -> str:
    return text.lower()

def replace_special(text: str) -> str:
    return re.sub(r"[^a-z0-9\s-]", "", text)

def spaces_to_hyphens(text: str) -> str:
    return text.replace(" ", "-")

def truncate(max_len: int):
    def _truncate(text: str) -> str:
        return text[:max_len]
    return _truncate

# slug generation pipeline
slugify = pipe(
    strip_whitespace,
    normalize_spaces,
    to_lowercase,
    replace_special,
    spaces_to_hyphens,
    truncate(50),
)

print(slugify("  Hello, World!  This is  a Test  "))
# hello-world-this-is-a-test

print(slugify("  Functional Programming — A Composition Guide  "))
# functional-programming--a-composition-guide
```

### Step 3: Data Processing Pipeline

```python
from collections.abc import Callable

def pipe_data(*funcs: Callable) -> Callable:
    """Data processing pipeline."""
    def process(data):
        result = data
        for func in funcs:
            result = func(result)
        return result
    return process

# define each stage as an independent function
def parse_records(raw: list[str]) -> list[dict]:
    records = []
    for line in raw:
        name, score = line.split(",")
        records.append({"name": name.strip(), "score": int(score.strip())})
    return records

def add_grade(records: list[dict]) -> list[dict]:
    def grade(score: int) -> str:
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        return "F"
    return [{**r, "grade": grade(r["score"])} for r in records]

def filter_passing(records: list[dict]) -> list[dict]:
    return [r for r in records if r["grade"] != "F"]

def sort_by_score(records: list[dict]) -> list[dict]:
    return sorted(records, key=lambda r: r["score"], reverse=True)

def format_table(records: list[dict]) -> str:
    lines = [f"{'Name':<10} {'Score':>5} {'Grade':>5}"]
    lines.append("-" * 22)
    for r in records:
        lines.append(f"{r['name']:<10} {r['score']:>5} {r['grade']:>5}")
    return "\n".join(lines)

# assemble the pipeline
process_students = pipe_data(
    parse_records,
    add_grade,
    filter_passing,
    sort_by_score,
    format_table,
)

# execute
raw_data = [
    "Alice, 85",
    "Bob, 92",
    "Charlie, 78",
    "Diana, 95",
    "Eve, 60",
]

print(process_students(raw_data))
# Name        Score Grade
# ----------------------
# Diana          95     A
# Bob            92     A
# Alice          85     B
# Charlie        78     C
```

### Step 4: Generator Pipeline

```python
from collections.abc import Callable
from typing import Iterator

def gen_pipe(*funcs: Callable) -> Callable:
    """Generator-based lazy pipeline."""
    def process(data):
        result = data
        for func in funcs:
            result = func(result)
        return result
    return process

def lines(text: str) -> Iterator[str]:
    for line in text.strip().split("\n"):
        yield line

def strip_lines(it: Iterator[str]) -> Iterator[str]:
    for line in it:
        yield line.strip()

def skip_empty(it: Iterator[str]) -> Iterator[str]:
    for line in it:
        if line:
            yield line

def skip_comments(it: Iterator[str]) -> Iterator[str]:
    for line in it:
        if not line.startswith("#"):
            yield line

def to_upper(it: Iterator[str]) -> Iterator[str]:
    for line in it:
        yield line.upper()

# assemble the lazy pipeline
clean_text = gen_pipe(
    strip_lines,
    skip_empty,
    skip_comments,
    to_upper,
)

text = """
  # config file
  host = localhost

  port = 8080

  # debug mode
  debug = true
"""

for line in clean_text(lines(text)):
    print(line)
# HOST = LOCALHOST
# PORT = 8080
# DEBUG = TRUE
```

### Step 5: Conditional Pipeline

```python
from collections.abc import Callable
from typing import Any

def conditional(
    predicate: Callable[[Any], bool],
    if_true: Callable,
    if_false: Callable | None = None,
) -> Callable:
    """Applies different functions based on a condition."""
    def apply(value: Any) -> Any:
        if predicate(value):
            return if_true(value)
        return if_false(value) if if_false else value
    return apply

def when(predicate: Callable[[Any], bool], func: Callable) -> Callable:
    """Applies a function only when the condition is true."""
    return conditional(predicate, func)

# pipeline with conditional steps
process = pipe(
    lambda x: x.strip(),
    when(lambda x: x.startswith("http"), lambda x: x.replace("http://", "https://")),
    lambda x: x.lower(),
    when(lambda x: len(x) > 30, lambda x: x[:27] + "..."),
)

print(process("  http://Example.COM/Very-Long-Path-Name-Here  "))
# https://example.com/very-l...
print(process("  Short URL  "))
# short url
```

## Production-shaped example: order settlement pipeline

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class OrderEvent:
    order_id: str
    store: str
    amount: int
    currency: str
    status: str
    source: str
    margin: int = 0

def normalize_currency(events: list[OrderEvent]) -> list[OrderEvent]:
    rates = {"KRW": 1, "USD": 1380}
    return [replace(e, amount=e.amount * rates[e.currency], currency="KRW") for e in events]

def drop_cancelled(events: list[OrderEvent]) -> list[OrderEvent]:
    return [e for e in events if e.status != "cancelled"]

def enrich_margin(events: list[OrderEvent]) -> list[OrderEvent]:
    return [replace(e, margin=int(e.amount * 0.18)) for e in events]

def keep_marketplace(events: list[OrderEvent]) -> list[OrderEvent]:
    return [e for e in events if e.source == "marketplace"]

def to_store_report(events: list[OrderEvent]) -> dict[str, dict[str, int]]:
    report: dict[str, dict[str, int]] = {}
    for event in events:
        store = report.setdefault(event.store, {"revenue": 0, "margin": 0, "orders": 0})
        store["revenue"] += event.amount
        store["margin"] += event.margin
        store["orders"] += 1
    return report

settle_orders = pipe(
    normalize_currency,
    drop_cancelled,
    keep_marketplace,
    enrich_margin,
    to_store_report,
)

events = [
    OrderEvent("A-1", "seoul", 48000, "KRW", "paid", "marketplace"),
    OrderEvent("A-2", "seoul", 42, "USD", "paid", "marketplace"),
    OrderEvent("A-3", "busan", 31000, "KRW", "cancelled", "marketplace"),
    OrderEvent("A-4", "busan", 27000, "KRW", "paid", "direct"),
]

normalized = normalize_currency(events)
assert [(e.order_id, e.amount, e.currency) for e in normalized] == [
    ("A-1", 48000, "KRW"),
    ("A-2", 57960, "KRW"),
    ("A-3", 31000, "KRW"),
    ("A-4", 27000, "KRW"),
]

active = drop_cancelled(normalized)
assert [e.order_id for e in active] == ["A-1", "A-2", "A-4"]

marketplace_only = keep_marketplace(active)
assert [e.order_id for e in marketplace_only] == ["A-1", "A-2"]

with_margin = enrich_margin(marketplace_only)
assert [(e.order_id, e.margin) for e in with_margin] == [
    ("A-1", 8640),
    ("A-2", 10432),
]

report = to_store_report(with_margin)
assert report == {
    "seoul": {"revenue": 105960, "margin": 19072, "orders": 2}
}

print("Normalized IDs:", [e.order_id for e in normalized])
print("After cancellation filter:", [e.order_id for e in active])
print("Marketplace IDs:", [e.order_id for e in marketplace_only])
print("Store report:", report)

print("Pipeline report:", settle_orders(events))
# Normalized IDs: ['A-1', 'A-2', 'A-3', 'A-4']
# After cancellation filter: ['A-1', 'A-2', 'A-4']
# Marketplace IDs: ['A-1', 'A-2']
# Store report: {'seoul': {'revenue': 105960, 'margin': 19072, 'orders': 2}}
# Pipeline report: {'seoul': {'revenue': 105960, 'margin': 19072, 'orders': 2}}
```

This example is closer to a production data flow than a toy string transformation. Currency normalization, cancellation filtering, channel filtering, margin enrichment, and store-level aggregation remain independent stages, which makes failures and business-rule changes easier to isolate.

#### Expected output

```text
Normalized IDs: ['A-1', 'A-2', 'A-3', 'A-4']
After cancellation filter: ['A-1', 'A-2', 'A-4']
Marketplace IDs: ['A-1', 'A-2']
Store report: {'seoul': {'revenue': 105960, 'margin': 19072, 'orders': 2}}
Pipeline report: {'seoul': {'revenue': 105960, 'margin': 19072, 'orders': 2}}
```

#### If your result differs, inspect this first

- Check that the USD exchange rate is still `1380`. That number directly changes `A-2` and every later aggregate.
- Verify `drop_cancelled()` really removes `cancelled` events. If `A-3` survives, the `busan` store will appear in the report.
- Verify `keep_marketplace()` keeps only `source == "marketplace"`. If `A-4` survives, direct-channel revenue leaks into the settlement.
- Confirm the margin rule is still `int(e.amount * 0.18)`. A different rounding rule changes the final `19072` margin.

## What to Notice in This Code

- `pipe` matches code order to execution order, improving readability
- Each stage function is independent and can be tested individually
- Generator pipelines process large data in a memory-efficient way
- Conditional pipelines express branching logic declaratively

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Mismatched function signatures | Output of one function does not match the next function's input | Verify compatibility with type hints |
| Pipeline grows too long | Debugging becomes difficult | Add intermediate variables or logging steps |
| Side effects in the middle of a pipeline | Makes testing and reuse hard | Place side effects at the end of the pipeline |
| Missing error handling | A failure in one stage halts the entire pipeline | Include error handling stages in the pipeline |
| Mixing compose and pipe | Execution direction becomes confusing | Standardize on one within the project |

## Real-World Applications

- Build ETL pipelines (Extract, Transform, Load) with function composition
- Implement data validation as a pipeline of validator functions
- Compose text preprocessing (normalization, tokenization, filtering) as a pipeline
- Implement API middleware chains through function composition
- Define each stage of a CI/CD pipeline as an independent function

## How Senior Engineers Think About This

The core value of function composition is separation of concerns. When each function handles exactly one transformation, testing is easy and recombination is free. This is the UNIX philosophy — "do one thing well" — applied at the code level.

Python does not have a built-in composition operator like Haskell's `.`, but a single `pipe()` utility is all you need. The point is not the tool — it is the mindset of composing small functions.

## Checklist

- [ ] I can explain the difference between compose and pipe
- [ ] I can combine small functions into a data pipeline
- [ ] I can implement lazy evaluation with generator pipelines
- [ ] I can write conditional pipelines
- [ ] I can test each stage of a pipeline independently

## Exercises

1. Implement both `compose` and `pipe`, and verify they produce the same result.
2. Build a 4-stage pipeline that reads JSON data, filters, transforms, sorts, and formats it.
3. Implement a pipeline with error handling using a `Result` type.

## Summary and Next Steps

Function composition combines small functions into complex transformations. `pipe` aligns code order with execution order for better readability. The next article wraps up the series with **balancing OOP and functional programming**.

## Answering the Opening Questions

- **What is function composition and why is it useful?**
  - Function composition chains multiple functions into a single computation like `f(g(h(x)))`. This article implements `compose()` and `pipe()` directly to show that flow. The example chaining `add_one`, `double`, and `to_str` to produce the same result connects the mathematical definition to a Python implementation.
- **How do you build a data pipeline by composing small functions?**
  - `compose` reads right-to-left; `pipe` reads left-to-right. When execution order matches code order, as in `load_data → calculate_totals → filter_passing → sort_by_score → format_output`, intermediate steps are much easier to follow during review.
- **When does composition make code harder to read?**
  - In text processing, small functions like `strip_whitespace`, `normalize_spaces`, and `replace_special` can be combined to change slug rules step by step. In data processing, pipelines like the student-score pipeline and order-event settlement pipeline make each stage independently testable, so you can quickly narrow down which transformation changed a value.

<!-- toc:begin -->
## In this series

- [Functional Programming 101 (1/10): What Is Functional Programming?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): Pure Functions and Side Effects](./02-pure-functions.md)
- [Functional Programming 101 (3/10): Immutable Data](./03-immutable-data.md)
- [Functional Programming 101 (4/10): Higher-Order Functions](./04-higher-order-functions.md)
- [Functional Programming 101 (5/10): map, filter, reduce](./05-map-filter-reduce.md)
- [Functional Programming 101 (6/10): Closures and Partial Application](./06-closure-and-partial.md)
- [Functional Programming 101 (7/10): Recursion and Tail Calls](./07-recursion.md)
- [Functional Programming 101 (8/10): Lazy Evaluation and Generators](./08-lazy-evaluation.md)
- **Function Composition and Pipelines (current)**
- Balancing OOP and Functional Programming (upcoming)

<!-- toc:end -->

## References

- [Python Official Docs — functools](https://docs.python.org/3/library/functools.html)
- [Real Python — Functional Programming in Python](https://realpython.com/python-functional-programming/)
- [UNIX Philosophy — Doug McIlroy](https://en.wikipedia.org/wiki/Unix_philosophy)
- [Composing Software — Eric Elliott](https://medium.com/javascript-scene/composing-software-the-book-f31c77fc3ddc)

Tags: Python, Functional Programming, Function Composition, Pipelines, Data Transformation

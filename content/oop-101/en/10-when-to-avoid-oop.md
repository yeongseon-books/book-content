---
series: oop-101
episode: 10
title: When to Avoid OOP
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Python
  - OOP
  - Functional Programming
  - dataclass
  - Design Decisions
seo_description: Learn when OOP is overkill and how to use functions, dataclasses, and functional patterns as simpler alternatives.
last_reviewed: '2026-05-17'
---

# When to Avoid OOP

This is the final post in the Object-Oriented Programming 101 series.

The hardest OOP decision is often not "which class should I add?" but "should this become a class at all?"

Python gives you functions, modules, `dataclass`, `NamedTuple`, `TypedDict`, and callables for a reason. In this chapter, we will start with a class-heavy reporting mini-app, simplify it in stages, and then mark the exact point where a class becomes useful again.

## Questions This Article Answers

- Which classes are protecting real state, and which ones are only wrapping a simple transformation?
- When is a function pipeline clearer than a class hierarchy?
- What concrete signal tells me the function-first design has gone far enough and should become a class again?

## What This Article Tries to Solve

> Good design is not measured by how many classes you can introduce. It is measured by whether you can stop at functions and lightweight data structures when state and lifecycle do not justify heavier objects.

- What are the warning signs that a class-based design is mostly ceremony?
- Which kinds of classes are better replaced by functions, `dataclass`, `NamedTuple`, or `TypedDict`?
- When is a callback enough instead of a full strategy class?
- How do you know when a function-first design has gone too far and should become a class again?

## Concept Overview

![Concept Overview](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/10/10-01-concept-overview.en.png)
*The goal is not to avoid classes forever. The goal is to reserve classes for places where state, invariants, and coordinated behavior truly move together.*

The practical question is simple: does this behavior need persistent state and lifecycle coordination, or is it mostly a data transformation pipeline? If the answer is "pipeline," classes are often extra weight.

## Key Concepts

| Term | Description |
|------|-------------|
| Multi-paradigm | Python supports procedural, object-oriented, and functional styles together |
| Anemic class | A class that mostly stores data or wraps a single trivial method |
| `dataclass` | A compact way to model data-centric structures with generated boilerplate |
| Higher-order function | A function that accepts or returns another function |
| Reintroduction threshold | The point where state, validation, or lifecycle coordination becomes strong enough to justify a class again |

## Before / After

The change in this chapter is not "classes are bad." It is "use the lightest tool that still preserves the design intent."

```python
# before: classes everywhere, even for stateless helpers and plain data
class TitleCleaner:
    def clean(self, title: str) -> str:
        return title.strip().title()


class ScoreFilter:
    def keep(self, score: int, minimum: int) -> bool:
        return score >= minimum
```

```python
# after: functions and data structures carry the same workflow more directly
def clean_title(title: str) -> str:
    return title.strip().title()


def keep_score(score: int, minimum: int) -> bool:
    return score >= minimum
```

## One Workflow: Simplifying a Class-Heavy Reporting Mini-App

### Starting Point: Too Many Tiny Classes

Assume a team built a weekly campaign report and wrapped every step in a separate class.

```python
class TitleCleaner:
    def clean(self, title: str) -> str:
        return title.strip().title()


class ScoreFilter:
    def keep(self, score: int, minimum: int) -> bool:
        return score >= minimum


class CurrencyFormatter:
    def format(self, value: int) -> str:
        return f"${value:,.0f}"


class ReportRow:
    def __init__(self, title: str, score: int, spend: int) -> None:
        self.title = title
        self.score = score
        self.spend = spend


class ReportConfig:
    def __init__(self, minimum_score: int, currency: str) -> None:
        self.minimum_score = minimum_score
        self.currency = currency
```

Each class is understandable, but the overall design is heavier than the problem.

### Step 1: Replace Stateless Helper Classes with Functions

If the code has no instance state and no lifecycle, module-level functions are usually clearer.

```python
def clean_title(title: str) -> str:
    return title.strip().title()


def keep_score(score: int, minimum: int) -> bool:
    return score >= minimum


def format_currency(value: int) -> str:
    return f"${value:,.0f}"
```

#### Run

```python
print(clean_title("  spring launch "))
print(keep_score(82, 80))
print(format_currency(12500))
```

Expected output:

```text
Spring Launch
True
$12,500
```

#### Check

What changed: instance creation disappeared because it carried no value. What stayed stable: each transformation still has one clear name and one clear job.

### Step 2: Replace Data-Carrying Boilerplate with `dataclass` and `TypedDict`

The original `ReportRow` and `ReportConfig` classes mainly stored fields. That is what lightweight data structures are for.

```python
from dataclasses import dataclass
from typing import TypedDict


@dataclass(frozen=True)
class ReportRow:
    title: str
    score: int
    spend: int


class ReportConfig(TypedDict):
    minimum_score: int
    channel: str


config: ReportConfig = {"minimum_score": 80, "channel": "email"}
row = ReportRow(title="Spring Launch", score=82, spend=12500)

print(row)
print(config["channel"])
```

Expected output:

```text
ReportRow(title='Spring Launch', score=82, spend=12500)
email
```

#### Check

What changed: manual constructor and representation boilerplate disappeared. What stayed stable: the workflow still has a named row type and explicit configuration keys.

#### Failure Path

If you typo a dict key such as `config["chnanel"]`, plain runtime dict access still fails late. That is acceptable for small, shallow configuration, but it is also the first warning sign that a richer object may become worthwhile later.

### Step 3: Replace Trivial Strategy Classes with Callables

Many strategy classes are really just named formatting functions.

```python
from collections.abc import Callable


def format_currency(value: int) -> str:
    return f"${value:,.0f}"


def format_points(value: int) -> str:
    return f"{value} pts"


def render_value(value: int, formatter: Callable[[int], str]) -> str:
    return formatter(value)


print(render_value(12500, format_currency))
print(render_value(82, format_points))
```

Expected output:

```text
$12,500
82 pts
```

#### Check

What changed: the strategy abstraction shrank to the one thing the caller actually needs — a callable. What stayed stable: formatting still swaps cleanly.

#### Failure Path

If each formatter later needs shared configuration, caching, or helper methods, the callback-only design will start scattering related behavior. That is one threshold for reintroducing a class.

### Step 4: Build the Report as a Function Pipeline

Now the mini-app can become one readable pipeline instead of a collection of tiny shells.

```python
from dataclasses import dataclass
from collections.abc import Callable
from typing import TypedDict


@dataclass(frozen=True)
class ReportRow:
    title: str
    score: int
    spend: int


class ReportConfig(TypedDict):
    minimum_score: int
    channel: str


def clean_title(title: str) -> str:
    return title.strip().title()


def format_currency(value: int) -> str:
    return f"${value:,.0f}"


def normalize_rows(rows: list[dict]) -> list[ReportRow]:
    return [
        ReportRow(
            title=clean_title(row["title"]),
            score=row["score"],
            spend=row["spend"],
        )
        for row in rows
    ]


def filter_rows(rows: list[ReportRow], minimum_score: int) -> list[ReportRow]:
    return [row for row in rows if row.score >= minimum_score]


def sort_rows(rows: list[ReportRow]) -> list[ReportRow]:
    return sorted(rows, key=lambda row: row.score, reverse=True)


def render_report(rows: list[ReportRow], money: Callable[[int], str]) -> list[str]:
    return [f"{row.title} | score={row.score} | spend={money(row.spend)}" for row in rows]


def build_report(raw_rows: list[dict], config: ReportConfig, money: Callable[[int], str]) -> list[str]:
    rows = normalize_rows(raw_rows)
    rows = filter_rows(rows, config["minimum_score"])
    rows = sort_rows(rows)
    return render_report(rows, money)


raw_rows = [
    {"title": "  spring launch ", "score": 82, "spend": 12500},
    {"title": "retargeting", "score": 76, "spend": 4000},
    {"title": "summer promo", "score": 91, "spend": 18000},
]
config: ReportConfig = {"minimum_score": 80, "channel": "email"}

for line in build_report(raw_rows, config, format_currency):
    print(line)
```

### Run

```bash
python report_pipeline.py
```

Expected output:

```text
Summer Promo | score=91 | spend=$18,000
Spring Launch | score=82 | spend=$12,500
```

### Check

Verify three things:

1. Normalization, filtering, sorting, and rendering each stay easy to test as separate functions.
2. The data carrier is lightweight and explicit.
3. The report pipeline reads top to bottom without instance orchestration noise.

### Failure Path: When Function-Only Design Becomes Too Loose

The function pipeline starts to struggle when rules and shared state begin moving together. For example:

```python
config = {"minimum_score": 80, "chnanel": "email"}  # typo hidden in a plain dict
```

Or imagine each formatter now needs currency symbol configuration, locale-aware rounding, and memoized exchange-rate lookup. At that point, a naked callable may stop being the clearest abstraction.

## Reintroduce a Class? Use This Threshold

Move back toward a class-based design when two or more of these become true:

| Signal | Why a class starts helping |
|--------|----------------------------|
| The same bundle of fields travels through many functions together | A richer domain object can hold invariants and behavior in one place |
| Validation rules and state transitions repeat together | Methods plus encapsulated state become easier to reason about |
| A formatter or strategy now needs persistent configuration or caches | A stateful object becomes clearer than passing extra parameters everywhere |
| The pipeline needs retries, lifecycle hooks, or shared collaborators | A coordinator object can own those cross-cutting concerns |

The goal is not to stay "purely functional." The goal is to postpone heavier structure until it earns its keep.

## What to Notice in This Workflow

- Stateless transformation logic usually reads better as functions than as classes with one method.
- `dataclass` and `TypedDict` preserve named structure without full object ceremony.
- Callables are often enough for simple interchangeable behavior.
- Function pipelines stay strong until state, invariants, or lifecycle coordination start repeating together.

## 5 Common Mistakes

| Mistake | Why It Hurts | Better Move |
|---------|--------------|-------------|
| Turning every helper into a class | Extra objects hide a simple pipeline | Start with module-level functions |
| Using a manual class for plain data | Boilerplate grows faster than value | Prefer `dataclass`, `NamedTuple`, or `TypedDict` |
| Keeping strategy classes that only wrap one function | Indirection without state | Pass a callable |
| Taking function-only design as an ideology | State and validation eventually scatter | Reintroduce classes when invariants repeat |
| Leaving dict-based configuration unbounded for too long | Typos and missing defaults surface late | Upgrade to richer objects when config complexity grows |

## Real-World Uses

- CLI utilities often work best as function-first modules.
- Data cleanup and transformation code usually reads naturally as pipelines.
- `dataclass` is ideal for immutable payloads and internal DTO-like structures.
- Stateful integrations such as API clients or caching services often justify classes again.

## How Senior Engineers Think About This

Senior engineers do not avoid classes because classes are bad. They avoid classes when classes are adding lifecycle and hierarchy weight to code that is really just transformation plus data. The best design question is often, "what is the cheapest abstraction that still protects the workflow?"

That is why many Python codebases start with functions, then upgrade only the hot spots that accumulate state, invariants, and coordination. Restraint is part of design skill.

## Checklist

- [ ] I can identify classes that are mostly wrapping stateless helper functions
- [ ] I can replace boilerplate data carriers with `dataclass` or `TypedDict`
- [ ] I can use a callable where a trivial strategy class would be overkill
- [ ] I can build a readable function pipeline for transformation-heavy code
- [ ] I can explain when growing state and invariants justify reintroducing a class

## Summary and Next Steps

You should avoid OOP when classes add more ceremony than protection. In this reporting workflow, stateless helpers became functions, data holders became lightweight structures, trivial strategies became callables, and the whole process became a direct pipeline. Just as important, you now have a concrete threshold for moving back to classes when state and invariants start traveling together.

<!-- toc:begin -->
- [What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Classes and Instances](./02-classes-and-instances.md)
- [Encapsulation](./03-encapsulation.md)
- [Inheritance](./04-inheritance.md)
- [Polymorphism](./05-polymorphism.md)
- [Abstraction](./06-abstraction.md)
- [Composition vs Inheritance](./07-composition-vs-inheritance.md)
- [SOLID Principles Basics](./08-solid-principles.md)
- [OOP Design Example](./09-oop-design-example.md)
- **When to Avoid OOP (current)**
<!-- toc:end -->

## References

- [Python Official Docs — dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Python Official Docs — typing (`NamedTuple`, `TypedDict`, `Callable`)](https://docs.python.org/3/library/typing.html)
- [Python Official Docs — functools](https://docs.python.org/3/library/functools.html)
- [Stop Writing Classes — PyCon Talk by Jack Diederich](https://www.youtube.com/watch?v=o9pEzgHorH0)

Tags: Python, OOP, Functional Programming, dataclass, Design Decisions

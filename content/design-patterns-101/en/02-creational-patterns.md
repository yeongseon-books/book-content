---
series: design-patterns-101
episode: 2
title: "Design Patterns 101 (2/10): Creational Patterns"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - DesignPatterns
  - Creational
  - Factory
  - Singleton
  - Builder
seo_description: How creational patterns separate object construction from use so teams can reduce coupling, simplify tests, and control object assembly.
last_reviewed: '2026-05-15'
---

# Design Patterns 101 (2/10): Creational Patterns

There is a point where object creation becomes more noticeable than the code using those objects. `new SomeService()` starts appearing everywhere, environment-specific construction branches spread, and constructor arguments keep growing. At that point, the real problem is not business logic. It is who owns creation.

This is post 2 in the Design Patterns 101 series.

In this post, we'll look at creational patterns as tools for concentrating construction responsibility in one place. The important question is not just what gets built, but who builds it and how much the caller needs to know.

## Questions to Keep in Mind

- The problem creational patterns solve?
- Factory Method and Abstract Factory?
- When you actually need a Builder?

## Big Picture

![design patterns 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/02/02-01-concept-at-a-glance.en.png)

*design patterns 101 chapter 2 flow overview*

This picture places Creational Patterns inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why It Matters

When `new SomeService()` is sprinkled throughout the code, coupling is already locked in. Concentrating construction in one place makes swapping easy.

> Where you build an object matters more than what you build.

## Key Terms

- **Factory Method**: A subclass decides which concrete class to build.
- **Abstract Factory**: Build families of related objects together.
- **Builder**: Assemble a complex object step by step.
- **Singleton**: Guarantee a single instance.
- **Prototype**: Build new objects by cloning an existing one.

## Before / After

**Before**

```python
def make_notifier(kind):
    if kind == "email": return EmailNotifier(smtp_host="...")
    elif kind == "sms": return SmsNotifier(api_key="...")
```

**After**

```python
class NotifierFactory:
    def create(self, kind) -> Notifier: ...

# the caller knows nothing about the concrete class
notifier = factory.create(kind)
```

The construction responsibility lives in one place.

## Hands-on: Five Steps Through Creational

### Step 1 — Factory Method

```python
# 1_factory.py
class Notifier:
    def send(self, msg): ...

class NotifierFactory:
    def create(self, kind: str) -> Notifier:
        if kind == "email": return EmailNotifier()
        if kind == "sms": return SmsNotifier()
        raise ValueError(kind)
```

The branching lives in one place.

### Step 2 — Abstract Factory

```python
# 2_abstract_factory.py
class UIFactory:
    def button(self) -> "Button": ...
    def textbox(self) -> "TextBox": ...

class MacFactory(UIFactory): ...
class WinFactory(UIFactory): ...
```

Build a family together.

### Step 3 — Builder

```python
# 3_builder.py
class QueryBuilder:
    def __init__(self): self.parts = []
    def select(self, *cols): self.parts.append(("SELECT", cols)); return self
    def from_(self, t): self.parts.append(("FROM", t)); return self
    def where(self, c): self.parts.append(("WHERE", c)); return self
    def build(self) -> str: ...
```

Step-by-step assembly for complex objects.

### Step 4 — Singleton (carefully)

```python
# 4_singleton.py
# In Python, the module itself is usually a singleton.
# A dedicated class is rarely necessary.
import logging
logger = logging.getLogger("app")
```

Always treat global state with suspicion.

### Step 5 — Prototype

```python
# 5_prototype.py
import copy

class ReportTemplate:
    def __init__(self, layout): self.layout = layout

base = ReportTemplate({"header": "Q1", "rows": []})
def new_report():
    return copy.deepcopy(base)
```

Use Prototype when cloning is cheaper than creating.

## What to Notice in This Code

- The caller does not know the concrete class.
- Adding a new kind does not change caller code.
- Complex assembly is broken into readable steps.

## Five Common Mistakes

1. **Singleton overuse.** It just becomes a global variable.
2. **Business logic inside the factory.** Construction and policy mix.
3. **Builder for simple objects.** All ceremony, no payoff.
4. **Abstract Factory introduced too early.** Only one family exists.
5. **Ignoring Prototype's deep-copy cost.** A performance trap.

## How This Shows Up in Production

DI containers, ORM query builders, UI widget libraries — creational patterns sit at the bones of many frameworks.

## Quick verification

Before introducing a creational pattern, test these checkpoints.

- Count how many call sites construct the same family of objects directly.
- Check whether tests need awkward monkey-patching just to replace collaborators.
- Verify whether the caller really needs to know the concrete class, constructor shape, or environment split.

**Expected outcome:** a successful refactor reduces direct knowledge of concrete construction in callers and makes test doubles easier to inject.

## How a Senior Engineer Thinks

- They concentrate the construction responsibility.
- They keep Singleton as a last resort.
- They reach for Builder when there are more than six arguments.
- They use Abstract Factory when there are at least two families.
- They always measure the cost of cloning.

## Checklist

- [ ] Is the caller free of the concrete class?
- [ ] Does adding a new kind avoid breaking caller code?
- [ ] Is the Singleton truly necessary?
- [ ] Does the Builder really lower complexity?
- [ ] Did you measure the Prototype cost?

## Practice Problems

1. Find a class with more than five `new Xxx()` calls and consolidate them in a Factory.
2. Apply a Builder to a constructor with seven arguments.
3. See if a Singleton can be replaced by a module-level variable.

## Wrap-up and Next Steps

Once you control creation, coupling loosens. Next up — how objects get *composed* together — Structural patterns.

## Answering the Opening Questions

- **The problem creational patterns solve?**
  - The article treats Creational Patterns as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Factory Method and Abstract Factory?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **When you actually need a Builder?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Design Patterns 101 (1/10): What Are Design Patterns?](./01-what-are-design-patterns.md)
- **Creational Patterns (current)**
- Structural Patterns (upcoming)
- Behavioral Patterns (upcoming)
- The Strategy Pattern (upcoming)
- The Adapter Pattern (upcoming)
- The Observer Pattern (upcoming)
- Factory and Dependency Injection (upcoming)
- Avoiding Pattern Overuse (upcoming)
- Pythonic Patterns (upcoming)

<!-- toc:end -->

## References

### Core references

- [Factory Method (refactoring.guru)](https://refactoring.guru/design-patterns/factory-method)
- [Abstract Factory (refactoring.guru)](https://refactoring.guru/design-patterns/abstract-factory)
- [Builder (refactoring.guru)](https://refactoring.guru/design-patterns/builder)

### Practical follow-up

- [Singleton — Why You Should Use It Sparingly](https://martinfowler.com/bliki/InversionOfControl.html)
- [copy — Shallow and deep copy operations (Python docs)](https://docs.python.org/3/library/copy.html)

Tags: Computer Science, DesignPatterns, Creational, Factory, Singleton, Builder

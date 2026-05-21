---
series: design-patterns-101
episode: 10
title: "Design Patterns 101 (10/10): Pythonic Patterns"
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
  - Python
  - Idioms
  - Protocols
  - Decorators
seo_description: How Python modules, functions, Protocols, and decorators express classic pattern intent with less ceremony than direct GoF translations.
last_reviewed: '2026-05-15'
---

# Design Patterns 101 (10/10): Pythonic Patterns

It is tempting to copy GoF structures directly into every language. In Python, that often produces more ceremony than value. Modules, first-class functions, Protocols, decorators, and dataclasses already carry much of the same intent in lighter forms.

This is the final post in the Design Patterns 101 series.

In this post, we'll look at how Python's own tools can express classic pattern ideas with less code and less inheritance. The point is not to reject patterns, but to translate their intent into forms that read naturally in Python.

## Questions to Keep in Mind

- Why a module is already a Singleton?
- Strategy and Command expressed as functions?
- Interfaces expressed as Protocols?

## Big Picture

![design patterns 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/10/10-01-concept-at-a-glance.en.png)

*design patterns 101 chapter 10 flow overview*

This picture places Pythonic Patterns inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why It Matters

Python's basic tools — modules, functions, Protocols — already provide *runtime support* for many patterns. The same problem can be solved with *less code*.

> Reach for the language's tools first; pull out a pattern only when those fall short.

## Key Terms

- **Module-as-singleton**: a module is loaded once and acts like a Singleton.
- **First-class function**: functions you can pass, return, and store.
- **Protocol**: structural typing (statically checked duck typing).
- **Decorator (`@`)**: a wrapper that adds behavior to a function or class.
- **dataclass**: a value object with built-in equality, repr, and immutability.

## Before/After

**Before (GoF as-is)**

```python
class SingletonConfig:
    _inst = None
    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst
```

**After (Pythonic)**

```python
# config.py
DEBUG = True
DB_URL = "postgres://..."
# elsewhere: from config import DEBUG, DB_URL
```

A module is already a Singleton.

## Hands-on: Five Steps to Pythonic Patterns

### Step 1 — Module = Singleton

```python
# 1_module_singleton.py
# settings.py
import os
ENV = os.getenv("ENV", "dev")
SECRET = os.getenv("SECRET", "x")
```

Import it anywhere — same value everywhere.

### Step 2 — Function = Strategy / Command

```python
# 2_function_strategy.py
def asc(d): return sorted(d)
def desc(d): return sorted(d, reverse=True)

def run(strategy, data): return strategy(data)
print(run(desc, [3, 1, 2]))
```

Classes were not necessary for clarity.

### Step 3 — Protocol = interface

```python
# 3_protocol.py
from typing import Protocol

class Mailer(Protocol):
    def send(self, to: str, body: str) -> None: ...

class SmtpMailer:
    def send(self, to, body): ...   # satisfies without inheritance
```

The balance of duck typing and static checking.

### Step 4 — `@dataclass` = value object

```python
# 4_dataclass.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str
```

Equality, repr, and immutability in one line.

### Step 5 — `@decorator` = the Decorator pattern

```python
# 5_decorator.py
import time, functools

def timed(fn):
    @functools.wraps(fn)
    def wrap(*a, **k):
        t = time.time()
        try: return fn(*a, **k)
        finally: print(fn.__name__, time.time()-t)
    return wrap

@timed
def work(): time.sleep(0.1)
```

`@` adds responsibility *naturally*.

## What to Notice in This Code

- There is almost no class hierarchy.
- The pattern *emerges* from standard tools.
- The same intent is expressed in *fewer lines*.

## Five Common Mistakes

1. **Porting Java-style GoF directly.** A weight Python does not need.
2. **Singleton class instead of a module.** A second instance becomes possible — risky.
3. **Forcing ABC.** A Protocol is often enough.
4. **Decorator overuse muddying the call flow.** Forgetting `functools.wraps` is common.
5. **Hand-rolled class instead of dataclass.** Missing `__eq__` and `__repr__`.

## How This Shows Up in Production

`logging` is a module Singleton, `sorted(key=...)` is a function Strategy, `typing.Protocol` is an interface, `@app.route(...)` is a Decorator. The standard library and popular frameworks are *living examples* of Pythonic patterns.

## Quick verification

Use this check before porting a textbook GoF structure straight into Python.

- Ask whether a module, function, Protocol, decorator, or dataclass already covers the same intent.
- Compare the direct GoF translation and the Pythonic form side by side for line count and readability.
- Verify that the lighter version still preserves the extension seam you actually need.

**Expected outcome:** the Pythonic form should keep the pattern's intent while reducing ceremony, inheritance, and incidental code.

## How a Senior Engineer Thinks

- Reach for the *language's* tools first.
- Prefer Protocol over ABC, module over Singleton class.
- A function is enough until it isn't.
- Use `functools.wraps` with every decorator.
- Patterns ultimately serve *readability*.

## Checklist

- [ ] Did you avoid Singleton classes where a module would do?
- [ ] Did you avoid Strategy classes where a function would do?
- [ ] Did you avoid forcing ABC where Protocol fits?
- [ ] Did you use a dataclass for value objects?
- [ ] Did you use `functools.wraps` in your decorators?

## Practice Problems

1. Fold a Singleton class into a module.
2. Simplify one Strategy class into a function.
3. Convert an ABC interface to a Protocol and pass mypy.

## Wrap-up and Next Steps

GoF is a *vocabulary*, not a *manual*. Look at Python's tools first, and reach for pattern names only where the tools fall short. The Design Patterns 101 series ends here — use these terms as *units of thought*, not as instruments.

## Answering the Opening Questions

- **Why a module is already a Singleton?**
  - The article treats Pythonic Patterns as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Strategy and Command expressed as functions?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Interfaces expressed as Protocols?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Design Patterns 101 (1/10): What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational Patterns](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural Patterns](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral Patterns](./04-behavioral-patterns.md)
- [Design Patterns 101 (5/10): The Strategy Pattern](./05-strategy-pattern.md)
- [Design Patterns 101 (6/10): The Adapter Pattern](./06-adapter-pattern.md)
- [Design Patterns 101 (7/10): The Observer Pattern](./07-observer-pattern.md)
- [Design Patterns 101 (8/10): Factory and Dependency Injection](./08-factory-and-di.md)
- [Design Patterns 101 (9/10): Avoiding Pattern Overuse](./09-avoiding-pattern-overuse.md)
- **Pythonic Patterns (current)**

<!-- toc:end -->

## References

### Core references

- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)
- [dataclasses (Python docs)](https://docs.python.org/3/library/dataclasses.html)
- [functools.wraps (Python docs)](https://docs.python.org/3/library/functools.html#functools.wraps)

### Practical follow-up

- [Python 3 Patterns, Recipes and Idioms (Bruce Eckel)](https://python-3-patterns-idioms-test.readthedocs.io/)
- [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/)

Tags: Computer Science, DesignPatterns, Python, Idioms, Protocols, Decorators

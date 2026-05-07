---
series: design-patterns-101
episode: 4
title: Behavioral Patterns
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - DesignPatterns
  - Behavioral
  - Strategy
  - Observer
  - Command
seo_description: Behavioral patterns coordinate responsibility and flow between objects. Strategy, Observer, Command, State, and Iterator explained for engineers.
last_reviewed: '2026-05-04'
---

# Behavioral Patterns

> Design Patterns 101 series (4/10)

<!-- a-grade-intro:begin -->

**Core question**: How do objects coordinate their *behavior*?

> By swapping algorithms, propagating notifications, or making requests into objects — the named ways are the behavioral patterns.

<!-- a-grade-intro:end -->

## What You Will Learn

- The problem behavioral patterns solve
- Strategy, Observer, Command
- State and Iterator
- Treating flow as *data*
- How to choose the right pattern

## Why It Matters

Cooperation between objects quickly hardens into piles of if/elif. Behavioral patterns give that cooperation a *name* and a *shape*.

> Turn flow into objects and the flow becomes testable.

## Concept at a Glance

```mermaid
flowchart LR
    S["Strategy (swap algo)"] --> Ctx["Context"]
    O["Observer (notify)"] --> Sub["Subject"]
    Cmd["Command (request as object)"] --> Inv["Invoker"]
    St["State (per-state behavior)"] --> Obj["Object"]
    It["Iterator (traversal)"] --> Col["Collection"]
```

Five styles of cooperation.

## Key Terms

- **Strategy**: turn an algorithm into an object so it can be swapped.
- **Observer**: notify many subscribers when one object changes.
- **Command**: turn a request itself into an object — for queueing or undo.
- **State**: separate behavior into state objects.
- **Iterator**: traverse a collection without exposing its structure.

## Before/After

**Before**

```python
def discount(kind, price):
    if kind == "vip":
        return price * 0.7
    elif kind == "member":
        return price * 0.9
    return price
```

**After**

```python
class Discount:
    def apply(self, p): return p

class Vip(Discount):
    def apply(self, p): return p * 0.7

class Member(Discount):
    def apply(self, p): return p * 0.9
```

New tiers appear without touching existing code.

## Hands-on: Five Steps to Practice Behavioral Patterns

### Step 1 — Strategy

```python
# 1_strategy.py
class Sorter:
    def __init__(self, strategy): self.strategy = strategy
    def sort(self, data): return self.strategy(data)

asc = Sorter(sorted)
desc = Sorter(lambda d: sorted(d, reverse=True))
```

In Python, functions are first-class — Strategy is often just a function.

### Step 2 — Observer

```python
# 2_observer.py
class Subject:
    def __init__(self): self._subs = []
    def subscribe(self, fn): self._subs.append(fn)
    def notify(self, e):
        for fn in self._subs: fn(e)

s = Subject()
s.subscribe(lambda e: print("LOG:", e))
s.notify("created")
```

The Subject can publish without knowing its subscribers.

### Step 3 — Command

```python
# 3_command.py
class Command:
    def execute(self): ...

class SendEmail(Command):
    def __init__(self, to, body): self.to, self.body = to, body
    def execute(self): mailer.send(self.to, self.body)

queue = [SendEmail("a@x", "hi"), SendEmail("b@x", "hi")]
for c in queue: c.execute()
```

Once a request is an object, you can queue, retry, or undo it.

### Step 4 — State

```python
# 4_state.py
class Order:
    def __init__(self): self.state = Draft()
    def submit(self): self.state = self.state.submit()

class Draft:
    def submit(self): return Pending()

class Pending:
    def submit(self): return self  # idempotent
```

Replace state branches with state objects.

### Step 5 — Iterator

```python
# 5_iterator.py
class Bag:
    def __init__(self, items): self.items = items
    def __iter__(self):
        for x in self.items: yield x

for x in Bag([1, 2, 3]):
    print(x)
```

Expose the contract for traversal, not the internal structure.

## What to Notice in This Code

- if/elif branches *condense* into objects.
- Algorithm and context separate cleanly.
- Flow becomes data, so it can be queued, stored, or replayed.

## Five Common Mistakes

1. **A class explosion for Strategy.** A function would have done.
2. **Observer cycles.** A→B→A loops forever.
3. **Business logic scattered into Commands.** A Command is just a *request*.
4. **State objects know each other too well.** Coupling explodes.
5. **Exposing index instead of an Iterator.** The client sees internals.

## How This Shows Up in Production

Django signals are Observer. Celery tasks are Command. FSM libraries are State. Every Python collection implements Iterator. Behavioral patterns sit beneath the daily tools.

## How a Senior Engineer Thinks

- The first candidate for Strategy is a *function*.
- Keep Observer notifications one-directional.
- Command is overkill for a simple request.
- Use State only for a real state machine.
- Iterator is a contract that hides internal structure.

## Checklist

- [ ] Is there a real reason a Strategy is a class, not a function?
- [ ] Does the Observer avoid cyclic notification?
- [ ] Does the Command hold only the *request*?
- [ ] Are state transitions visible in one place?
- [ ] Does the Iterator hide internal structure?

## Practice Problems

1. Refactor a current if/elif branch into Strategy.
2. Model domain event publishing with Observer.
3. Express an external API call queue with Command.

## Wrap-up and Next Steps

Behavior expressed as objects reduces branching and makes cooperation visible. The next post zooms in on the most practical behavioral pattern — Strategy.

<!-- toc:begin -->
- [What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Creational Patterns](./02-creational-patterns.md)
- [Structural Patterns](./03-structural-patterns.md)
- **Behavioral Patterns (current)**
- Strategy Pattern (upcoming)
- Adapter Pattern (upcoming)
- Observer Pattern (upcoming)
- Factory and Dependency Injection (upcoming)
- Avoiding Pattern Overuse (upcoming)
- Pythonic Patterns (upcoming)
<!-- toc:end -->

## References

- [Strategy Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/strategy)
- [Observer Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/observer)
- [Command Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/command)
- [State Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/state)

Tags: Computer Science, DesignPatterns, Behavioral, Strategy, Observer, Command

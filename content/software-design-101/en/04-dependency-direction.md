---
series: software-design-101
episode: 4
title: Dependency Direction
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - SoftwareDesign
  - Dependencies
  - DIP
  - Inversion
  - Architecture
seo_description: How to control the direction of dependencies to lower change cost, with DIP and ports and adapters.
last_reviewed: '2026-05-15'
---

# Dependency Direction

The expensive part of a dependency is not the line of code that imports something. It is the direction of the arrow and who now has to absorb future change.

This is post 4 in the Software Design 101 series.

In this post, we look at dependency direction as the mechanism that keeps a stable core from depending on volatile details. DIP and ports-and-adapters matter because they buy freedom where vendors, databases, and SDKs churn fastest.

> Stable code should define what it needs; volatile code should adapt to it.

## What You Will Learn

- How dependency relates to coupling
- Stable versus volatile modules
- The Dependency Inversion Principle (DIP)
- The ports and adapters pattern
- The freedom you gain from controlling direction

## Why It Matters

Code is a graph. Where the arrows point determines whether a change in one place leaks into another.

> Stable things must not depend on volatile things.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/04/04-01-concept-at-a-glance.en.png)
*Dependency direction stays healthy when the stable core defines the port and volatile adapters implement it*

Details point toward the core.

## Key Terms

- **Dependency**: If A imports or calls B, then A depends on B.
- **Stable module**: Changes rarely; usually the more abstract side.
- **Volatile module**: DB, HTTP, third-party SaaS. Changes often.
- **DIP (Dependency Inversion Principle)**: The core depends on abstractions; details implement those abstractions.
- **Port / Adapter**: The core defines an interface (port) that an external adapter implements.

## Before / After

**Before**

```python
# domain knows the DB directly
import psycopg2

def charge(user_id, amount):
    conn = psycopg2.connect(...)
    conn.execute("UPDATE wallet SET ...")
```

**After**

```python
# domain only knows an abstraction
class WalletRepo:
    def debit(self, user_id, amount): ...

def charge(repo: WalletRepo, user_id, amount):
    repo.debit(user_id, amount)
```

Swapping the DB no longer shakes the domain.

## Hands-on: Five Steps to Fix Dependency Direction

### Step 1 — Draw the arrows

```python
# 1_arrows.py
# On paper, draw which module imports which.
# If the core imports the details, that is a red flag.
```

You can only fix what you can see.

### Step 2 — Define the abstraction in the core

```python
# 2_port.py
from typing import Protocol

class WalletRepo(Protocol):
    def debit(self, user_id: str, amount: int) -> None: ...
```

The core declares the shape it needs.

### Step 3 — Implement in the adapter

```python
# 3_adapter.py
class PostgresWalletRepo:
    def debit(self, user_id, amount):
        # concrete SQL implementation
        ...
```

The detail conforms to the abstraction, not the other way around.

### Step 4 — Compose at the edge

```python
# 4_compose.py
def main():
    repo = PostgresWalletRepo()
    charge(repo, "u-1", 1000)
```

The domain has no idea which implementation showed up.

### Step 5 — Test with a fake

```python
# 5_fake.py
class FakeRepo:
    def __init__(self): self.calls = []
    def debit(self, u, a): self.calls.append((u, a))

def test_charge():
    repo = FakeRepo()
    charge(repo, "u-1", 500)
    assert repo.calls == [("u-1", 500)]
```

You can verify the domain without any database.

## Quick Verification

Dependency direction becomes visible as soon as you sketch the imports. Start by listing whether the domain imports any DB driver, HTTP client, or SDK directly.

```text
domain -> typing, dataclasses
domain -> psycopg2        # warning sign
infra  -> domain          # expected direction
```

**Expected output:** if an arrow runs from the domain into infrastructure, you know immediately that either the port location or the composition location needs work.

That same check should hold in tests. If a fake repository is enough to test the domain, the direction is probably healthy.

## Failure Signals and First Checks

| Failure signal | First check |
| --- | --- |
| The domain test cannot run without a real DB | Check whether the domain knows the concrete repository |
| The interface lives in an infrastructure folder | Revisit who is defining the need |
| You created too many ports | Check whether you inverted places that are not real stable/volatile boundaries |

The point of fixing dependency direction is not “more abstraction.” It is protecting the core from detail churn.

## What to Notice in This Code

- The domain is free of external libraries.
- The abstraction lives on the domain side, not the infrastructure side.
- Composition only happens at the edge (`main`, the composition root).

## Five Common Mistakes

1. **Putting the interface in the infrastructure folder.** The dependency flips back.
2. **Slicing abstractions too thin.** A hundred ports is the same as none.
3. **Business logic inside the adapter.** The domain is leaking out.
4. **Composing inside the domain.** A `new PostgresRepo()` shows up where it should not.
5. **Applying DIP everywhere.** Use it only across real stable / volatile boundaries.

## How This Shows Up in Production

DIP shines around payments, notifications, and third-party SaaS integrations. Vendor swaps and mocks happen without touching the domain.

## How a Senior Engineer Thinks

- They keep the dependency graph in their head.
- They never let an arrow run from the volatile side into the stable side.
- They notice instantly when the domain imports infrastructure.
- They let the domain decide the number and shape of ports.
- They keep composition in one place.

## Checklist

- [ ] Does the domain avoid importing infrastructure?
- [ ] Are ports defined on the domain side?
- [ ] Is composition concentrated at the edge?
- [ ] Can the domain be tested with fake adapters?
- [ ] Is the number of ports kept reasonable?

## Practice Problems

1. Pick one external module the domain currently imports. Is it worth flipping with DIP?
2. Split out a payment module's DB call into a port and an adapter.
3. Write a domain unit test that uses a fake adapter.

## Wrap-up and Next Steps

Once direction is right, the cost of change drops. Next up we look at the tools that hold that direction in place — interfaces and abstraction.

<!-- toc:begin -->
- [What Is Software Design?](./01-what-is-software-design.md)
- [Separation of Concerns](./02-separation-of-concerns.md)
- [Modules and Boundaries](./03-modules-and-boundaries.md)
- **Dependency Direction (current)**
- Interfaces and Abstraction (upcoming)
- Layered Architecture (upcoming)
- Data Flow Design (upcoming)
- Reducing Change Impact (upcoming)
- Design Principles (upcoming)
- Small Design Practice (upcoming)
<!-- toc:end -->

## References

- [Robert C. Martin — Dependency Inversion Principle](https://web.archive.org/web/20110714224327/http://www.objectmentor.com/resources/articles/dip.pdf)
- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture — Dependency Rule](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Ports and Adapters Pattern](https://herbertograca.com/2017/09/14/ports-adapters-architecture/)

### Practical Docs

- [typing — Support for type hints](https://docs.python.org/3/library/typing.html)
- [abc — Abstract Base Classes](https://docs.python.org/3/library/abc.html)


Tags: Computer Science, SoftwareDesign, Dependencies, DIP, Inversion, Architecture

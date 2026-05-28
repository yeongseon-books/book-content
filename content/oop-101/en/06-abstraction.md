---
series: oop-101
episode: 6
title: "Object-Oriented Programming 101 (6/10): Abstraction"
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
  - OOP
  - Abstraction
  - ABC
  - Interface
seo_description: Learn how to design abstract classes with Python ABC and define enforced interfaces using abstractmethod.
last_reviewed: '2026-05-17'
---

# Object-Oriented Programming 101 (6/10): Abstraction

Abstraction matters the moment one workflow has multiple implementations and the caller starts guessing which method name to call. This article is the 6th post in the OOP 101 series.

This is the 6th post in the Object-Oriented Programming 101 series.

In Python, abstraction is not mainly about sounding theoretical. It is about deciding which methods are mandatory, which steps should stay shared, and when a team should require explicit inheritance instead of relying on "it probably has the right shape."


![Object-Oriented Programming 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/06/06-01-concept-overview.en.png)
*Object-Oriented Programming 101 chapter 6 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Abstraction?
- Which signal should the example or diagram make visible for Abstraction?
- What failure should be prevented first when Abstraction reaches a real system?

## What This Article Tries to Solve

> Abstraction is not the act of removing implementation details. It is the act of making the minimum shared contract explicit before a workflow starts spreading across multiple classes.

- When is a plain duck-typed convention no longer enough?
- What should an abstract base class force every implementation to provide?
- Where does the template method pattern help the parent class own the workflow without owning every detail?
- When should you switch from ABC to Protocol instead of forcing explicit inheritance?

## Concept Overview

*Start by eliminating caller-specific method names, then decide whether the shared contract should be enforced through explicit inheritance (ABC) or structural compatibility (Protocol).* 

Without a contract, one ingestion source exposes `read_file()`, another exposes `fetch_rows()`, and a third exposes `pull()`. The orchestrator becomes a bundle of `if` statements. With abstraction, the team agrees on a small contract first, then lets implementations vary behind it.

## Key Concepts

| Term | Description |
|------|-------------|
| Abstract class | A class that cannot be instantiated directly and can force child classes to implement specific members |
| `@abstractmethod` | Marks a method or property that subclasses must implement |
| ABC | Python's explicit contract mechanism from the `abc` module |
| Template method pattern | A parent class keeps the workflow skeleton while subclasses fill in variable steps |
| Protocol | A structural contract: matching the required shape is enough, even without inheritance |

## Before / After

The design change in this article is small but practical.

```python
# before: the caller must know each implementation's private vocabulary
class CsvFeed:
    def read_file(self, path: str) -> list[dict]:
        return [{"email": "alice@example.com", "active": True}]

class WarehouseFeed:
    def fetch_rows(self, table: str) -> list[dict]:
        return [{"email": "bob@example.com", "active": False}]
```

```python
# after: every source agrees on one contract
from abc import ABC, abstractmethod

class FeedSource(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str: ...

    @abstractmethod
    def fetch_records(self) -> list[dict]: ...
```

## One Workflow: Designing an Ingestion Contract

### Step 1: See Where the Caller Starts Breaking

Suppose the team is building one customer-ingestion pipeline, but each developer added a slightly different source class.

```python
class CsvFeed:
    def read_file(self, path: str) -> list[dict]:
        return [{"email": "alice@example.com", "active": True}]

class WarehouseFeed:
    def fetch_rows(self, table: str) -> list[dict]:
        return [{"email": "bob@example.com", "active": False}]

class PartnerApiFeed:
    def pull(self) -> list[dict]:
        return [{"email": "carol@example.com", "active": True}]

def ingest(source: object) -> list[dict]:
    return source.fetch_records()  # caller assumes a method that does not exist

ingest(CsvFeed())
```

#### Failure Signal

```text
AttributeError: 'CsvFeed' object has no attribute 'fetch_records'
```

The failure is not really about one missing method. It is about the workflow having no shared language.

### Step 2: Use ABC to Freeze the Team Contract

The next move is not to add more `if isinstance(...)` branches. It is to make the required shape explicit.

```python
from abc import ABC, abstractmethod

class FeedSource(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable label for logs and metrics."""

    @abstractmethod
    def fetch_records(self) -> list[dict]:
        """Return raw customer rows from this source."""

class CsvFeed(FeedSource):
    @property
    def source_name(self) -> str:
        return "csv"

    def fetch_records(self) -> list[dict]:
        return [{"email": "alice@example.com", "active": True}]

class WarehouseFeed(FeedSource):
    @property
    def source_name(self) -> str:
        return "warehouse"

    def fetch_records(self) -> list[dict]:
        return [{"email": "bob@example.com", "active": False}]
```

At this stage, abstraction does two useful things:

- it forces one method name and one return shape,
- and it keeps broken implementations from being instantiated quietly.

### Step 3: Keep the Workflow in the Parent with a Template Method

Once several sources follow the same ingestion steps, the parent class should own the skeleton instead of letting every subclass reimplement the same sequence.

```python
from abc import ABC, abstractmethod

class IngestionPipeline(ABC):
    def run(self) -> list[dict]:
        raw = self.fetch_records()
        normalized = [self.normalize(row) for row in raw]
        valid = [row for row in normalized if self.is_valid(row)]
        self.store(valid)
        print(f"[{self.source_name}] loaded {len(valid)} records")
        return valid

    @property
    @abstractmethod
    def source_name(self) -> str: ...

    @abstractmethod
    def fetch_records(self) -> list[dict]: ...

    def normalize(self, row: dict) -> dict:
        return {
            "email": row["email"].strip().lower(),
            "active": bool(row["active"]),
        }

    def is_valid(self, row: dict) -> bool:
        return "@" in row["email"]

    @abstractmethod
    def store(self, rows: list[dict]) -> None: ...

class CsvCustomerPipeline(IngestionPipeline):
    @property
    def source_name(self) -> str:
        return "csv"

    def fetch_records(self) -> list[dict]:
        return [
            {"email": " Alice@example.com ", "active": 1},
            {"email": "broken-email", "active": 1},
        ]

    def store(self, rows: list[dict]) -> None:
        for row in rows:
            print(f"store -> {row}")

class PartnerApiPipeline(IngestionPipeline):
    @property
    def source_name(self) -> str:
        return "partner-api"

    def fetch_records(self) -> list[dict]:
        return [{"email": "Carol@Example.com", "active": True}]

    def store(self, rows: list[dict]) -> None:
        for row in rows:
            print(f"store -> {row}")
```

Now the subclasses only explain what varies: where rows come from and where they go. The shared steps stay in one place.

### Step 4: Plug in a Third-Party Implementation Without Editing It

Sometimes the workflow is good, but the class comes from another library. You may not be allowed to inherit from your ABC.

```python
from abc import ABC, abstractmethod

class FeedSource(ABC):
    @abstractmethod
    def fetch_records(self) -> list[dict]: ...

class VendorSnapshot:
    """Pretend this class lives in a third-party package."""

    def fetch_records(self) -> list[dict]:
        return [{"email": "vendor@example.com", "active": True}]

FeedSource.register(VendorSnapshot)

snapshot = VendorSnapshot()
print(isinstance(snapshot, FeedSource))
print(snapshot.fetch_records())
```

`register()` is useful when you trust the external shape and want your runtime checks to recognize it.

### Step 5: Make the Final ABC vs Protocol Decision Explicit

Not every integration should be forced into inheritance.

```python
from abc import ABC, abstractmethod
from typing import Protocol

class InternalFeed(ABC):
    @abstractmethod
    def fetch_records(self) -> list[dict]: ...

class FeedLike(Protocol):
    def fetch_records(self) -> list[dict]: ...

class BackfillExport:
    def fetch_records(self) -> list[dict]:
        return [{"email": "backfill@example.com", "active": True}]

def preview(feed: FeedLike) -> int:
    return len(feed.fetch_records())

print(preview(BackfillExport()))
```

- Use **ABC** when the class is part of your internal framework and you want explicit inheritance, shared defaults, or instantiation-time failures.
- Use **Protocol** when you only need compatibility with a shape and do not control every implementation.

## Run, Verify, and Failure Paths

### Run

Put the Step 3 code in `abstraction_workflow.py` and run:

```bash
python abstraction_workflow.py
```

Expected output:

```text
store -> {'email': 'alice@example.com', 'active': True}
[csv] loaded 1 records
store -> {'email': 'carol@example.com', 'active': True}
[partner-api] loaded 1 records
```

### Verify

Check three things after the run:

1. `normalize()` cleaned casing and whitespace.
2. The invalid row disappeared because `is_valid()` filtered it.
3. Both pipelines produced the same output contract even though the raw input sources differed.

### Failure Path 1: Missing a Required Method

```python
class BrokenPipeline(IngestionPipeline):
    @property
    def source_name(self) -> str:
        return "broken"

    def fetch_records(self) -> list[dict]:
        return []

BrokenPipeline()
```

Expected failure:

```text
TypeError: Can't instantiate abstract class BrokenPipeline with abstract method store
```

That error is useful. It prevents the team from shipping a half-implemented workflow.

### Failure Path 2: Choosing the Wrong Contract Style

If an external library already ships a stable object that happens to expose `fetch_records()`, forcing it to inherit your ABC usually creates unnecessary wrapping work. That is the point where a Protocol-based boundary is simpler.

Use this decision check:

| Question | If yes | Better choice |
|----------|--------|---------------|
| Do we own every implementation? | Mostly yes | ABC |
| Do we need shared default behavior? | Yes | ABC |
| Do we only need shape compatibility? | Yes | Protocol |
| Is the implementation from another library? | Yes | Protocol or `register()` |

## What to Notice in This Workflow

- The first real abstraction problem was not "how do I write an abstract class?" but "why is the caller forced to know three vocabularies?"
- `@abstractmethod` helps at the moment team coordination starts to matter.
- The template method pattern keeps the workflow sequence stable while allowing source-specific variation.
- `register()` and Protocol solve different interoperability problems; they are not interchangeable decoration.

## 5 Common Mistakes

| Mistake | Why It Becomes a Problem | Better Move |
|---------|---------------------------|-------------|
| Turning every interface into an ABC | External integrations get forced into inheritance they do not need | Use Protocol when shape compatibility is enough |
| Putting too much logic in the parent | The abstract class becomes a fragile god object | Keep only truly shared workflow steps |
| Using ABC without any abstract member | The contract stops enforcing anything important | Define at least one required method or property |
| Letting each subclass rename the same responsibility | The caller starts branching on implementation details | Freeze one shared vocabulary first |
| Forgetting to validate the output contract | Ingestion succeeds but produces incompatible rows | Verify normalized shape after the run |

## Real-World Uses

- `collections.abc` defines explicit container contracts in the Python standard library.
- Django class-based views use a template-method-style workflow.
- Plugin systems often use ABC internally and Protocol externally.
- ETL pipelines frequently share one ingestion skeleton while swapping source-specific adapters.

## How Senior Engineers Think About This

Senior engineers rarely ask for abstraction because the code "should look more object-oriented." They ask for it when multiple implementations are already drifting apart and the caller is paying the price. The best abstraction is the smallest contract that removes that drift.

In practice, many Python codebases mix both styles: ABC for internal team-owned frameworks, Protocol for boundaries where compatibility matters more than inheritance purity.

## Checklist

- [ ] I can explain why inconsistent method names are a workflow problem, not just a style problem
- [ ] I can design an ABC with one required property and one required method
- [ ] I can use the template method pattern to keep shared workflow steps in the parent
- [ ] I can tell when `register()` is enough for a third-party class
- [ ] I can justify choosing Protocol instead of ABC for structural compatibility

## Summary and Next Steps

Abstraction becomes useful when one workflow needs multiple implementations and the caller can no longer tolerate private naming conventions. Use ABC when your team needs an explicit contract and shared workflow defaults. Use Protocol when compatibility matters more than inheritance. In the next article, we compare composition and inheritance so you can choose where behavior should live in the first place.

## Answering the Opening Questions

- **When does duck typing convention alone become insufficient?**
  - When each implementation uses its own terminology—`CsvFeed.read_file()`, `WarehouseFeed.fetch_rows()`, `PartnerApiFeed.pull()`—the moment a caller expects `fetch_records()`, an `AttributeError` fires immediately. The article identifies this as precisely the point where duck typing conventions become insufficient and a team-level shared language becomes necessary.
- **Which methods and properties should an abstract class enforce?**
  - This article enforced `source_name` (a property for logs and metrics), `fetch_records()` (actual data retrieval), and `store()` (the pipeline persistence step) as abstract members. It also showed why keeping only the surface essential for maintaining common flow as abstract—while providing default behavior for `normalize()` and `is_valid()` in the parent—matters.
- **How does the Template Method pattern help the parent maintain flow while children handle specifics?**
  - `IngestionPipeline.run()` fixes the `fetch_records() → normalize() → is_valid() → store()` order in the parent, while `CsvCustomerPipeline` and `PartnerApiPipeline` implement only source-specific retrieval and storage. This keeps core rules like email normalization and invalid address filtering in one place, with child classes filling in only the parts that vary.
<!-- toc:begin -->
## In this series

- [Object-Oriented Programming 101 (1/10): What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): Classes and Instances](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): Encapsulation](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): Inheritance](./04-inheritance.md)
- [Object-Oriented Programming 101 (5/10): Polymorphism](./05-polymorphism.md)
- **Abstraction (current)**
- Composition vs Inheritance (upcoming)
- SOLID Principles Basics (upcoming)
- OOP Design Example (upcoming)
- When to Avoid OOP (upcoming)

<!-- toc:end -->

## References

- [Python Official Docs — abc module](https://docs.python.org/3/library/abc.html)
- [PEP 544 — Protocols: Structural Subtyping](https://peps.python.org/pep-0544/)
- [Python collections.abc Docs](https://docs.python.org/3/library/collections.abc.html)
- [Fluent Python — Chapter 13: Interfaces, Protocols, and ABCs](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

Tags: Python, OOP, Abstraction, ABC, Interface

---
title: "SQLAlchemy 101 (8/10): Events, hybrid_property, and custom types"
series: sqlalchemy-101
episode: 8
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Python
- SQLAlchemy
- ORM
- event
- hybrid_property
- SQLite
last_reviewed: '2026-05-03'
seo_description: Think of SQLAlchemy extension points as three layers. The type layer
  transforms values as they cross the column boundary; the attribute layer…
---

# SQLAlchemy 101 (8/10): Events, hybrid_property, and custom types

It helps to think about SQLAlchemy extension points as three layers: types, attributes, and events. This post uses that frame to connect events, `hybrid_property`, and custom types.

This is the 8th article in the SQLAlchemy 101 series.

![Events, hybrid_property, and custom types](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/08/08-01-events-hybrid-property-and-custom-types.en.png)

*Events, hybrid_property, and custom types*

## Questions to Keep in Mind

- How to attach lifecycle hooks at the model, session, and engine levels using the SQLAlchemy event system?
- How to validate inputs with `@validates`?
- How to define `hybrid_property` so the same attribute works in Python and in SQL?

## Big Picture

![sqlalchemy 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/08/08-02-why-this-matters.en.png)

*sqlalchemy 101 chapter 8 flow overview*

This picture places Events, hybrid_property, and custom types inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why this matters

When you first reach for an ORM, a model is just a table. Once the domain grows, you need email normalization, password hashing, audit columns, derived attributes, and encrypted fields. If every handler does this work itself, the same code is scattered everywhere and tests become painful.

SQLAlchemy's event system, `hybrid_property`, and `TypeDecorator` are the official extension points that let domain rules live close to the model. Used well, the rules collect in one place. Used carelessly, your codebase becomes a mystery: nobody can tell where data is being transformed. This article draws the lines.

## Mental model

![Mental model](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/08/08-03-mental-model.en.png)

*Mental model*
> Think of SQLAlchemy extension points as three layers. The **type layer** transforms values as they cross the column boundary; the **attribute layer** defines a single name that works in Python and in SQL; the **event layer** hooks into the lifecycle of objects, sessions, and the engine.

The same behaviour can live in different layers, and the choice changes its blast radius. Suppose you want to store every email in lowercase. There are three options:

- A `TypeDecorator` called `LowerString` attached to the column applies to every model and every session automatically.
- A `@validates("email")` decorator on the model normalizes at setter time, but only for that model.
- A `before_insert` event runs only just before INSERT and leaves the in-memory object as the user typed it until then.

The decision depends on how general the rule is and when it must take effect.

## Core concepts

![Core concepts](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/08/08-04-core-concepts.en.png)

*Core concepts*
### The event system

SQLAlchemy exposes hooks on almost every object via `event.listen` and `@event.listens_for`. The three common targets:

| Target | Common events | Typical use |
| --- | --- | --- |
| Mapper (model) | `before_insert`, `before_update`, `after_insert` | audit columns, derived fields |
| Session | `before_flush`, `after_commit`, `after_rollback` | transaction-scoped post-processing, outbox |
| Engine | `before_cursor_execute`, `after_cursor_execute` | query logging, counting, slow-query tracking |

### `@validates`

`sqlalchemy.orm.validates` is the simplest hook: it intercepts the setter. Whatever it returns becomes the stored value, so it doubles as validation and normalization.

### `hybrid_property`

`sqlalchemy.ext.hybrid.hybrid_property` defines an attribute that behaves like a regular property on instances and like a SQL expression on the class. That is what allows `select(User).where(User.full_name == "Ada Lovelace")` to compile to SQL.

### `TypeDecorator`

`sqlalchemy.types.TypeDecorator` wraps an existing type and lets you transform values in `process_bind_param` (writing) and `process_result_value` (reading). It is the right place for JSON serialization, encryption, currency, and timezone handling.

## Before / after

Here is email normalization and audit timestamps written in a handler, then moved into the model layer.

```python
# Before: every handler does it
def create_user(session, email, name):
    email = email.strip().lower()
    user = User(
        email=email,
        name=name,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(user)
    session.commit()
    return user
```

```python
# After: the model takes responsibility
from sqlalchemy import event
from sqlalchemy.orm import validates

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    name: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

    @validates("email")
    def _normalize_email(self, key, value):
        return value.strip().lower()

@event.listens_for(User, "before_insert")
def _set_timestamps_insert(mapper, connection, target):
    now = datetime.utcnow()
    target.created_at = now
    target.updated_at = now

@event.listens_for(User, "before_update")
def _bump_updated(mapper, connection, target):
    target.updated_at = datetime.utcnow()
```

The "after" version applies the same rules no matter where users are created. Tests only need to assert that `User(email="  A@B  ").email == "a@b"`.

## Step-by-step walkthrough

![Step-by-step walkthrough](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/08/08-05-step-by-step-walkthrough.en.png)

*Step-by-step walkthrough*
### Step 1: Set up

Install with `pip install "sqlalchemy>=2.0"` and reuse the SQLite `Base`, `engine`, and `Session` from earlier episodes.

### Step 2: Validate with `@validates`

```python
class Member(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    score: Mapped[int]

    @validates("email")
    def _v_email(self, key, value):
        if "@" not in value:
            raise ValueError("invalid email")
        return value.strip().lower()

    @validates("score")
    def _v_score(self, key, value):
        if not 0 <= value <= 100:
            raise ValueError("score out of range")
        return value
```

The exception is raised at setter time, so bad data never reaches the session.

### Step 3: Derive an attribute with `hybrid_property`

```python
from sqlalchemy.ext.hybrid import hybrid_property

class Person(Base):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @full_name.expression
    def full_name(cls):
        return cls.first_name + " " + cls.last_name
```

Now `person.full_name` works in Python and `select(Person).where(Person.full_name == "Ada Lovelace")` compiles to SQL `first_name || ' ' || last_name = ?`.

### Step 4: Build LowerString and JSON types with `TypeDecorator`

```python
import json
from sqlalchemy.types import TypeDecorator, String, Text

class LowerString(TypeDecorator):
    impl = String
    cache_ok = True
    def process_bind_param(self, value, dialect):
        return value.lower() if value is not None else None
    def process_result_value(self, value, dialect):
        return value

class JSONText(TypeDecorator):
    impl = Text
    cache_ok = True
    def process_bind_param(self, value, dialect):
        return None if value is None else json.dumps(value, ensure_ascii=False)
    def process_result_value(self, value, dialect):
        return None if value is None else json.loads(value)

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    handle: Mapped[str] = mapped_column(LowerString(64))
    settings: Mapped[dict] = mapped_column(JSONText)
```

Handlers can now pass a dict directly, and `handle` is always lowercased on the way in.

### Step 5: Count queries at the engine level

```python
from sqlalchemy import event

query_counter = {"n": 0}

@event.listens_for(engine, "before_cursor_execute")
def _count(conn, cursor, statement, parameters, context, executemany):
    query_counter["n"] += 1
```

Tests can compare `query_counter["n"]` before and after a code path to catch N+1 regressions. This pairs with the loading strategies from Episode 7.

### Step 6: Outbox pattern with a session event

```python
@event.listens_for(Session, "before_flush")
def _emit_outbox(session, flush_context, instances):
    for obj in session.new:
        if isinstance(obj, Order):
            session.add(OutboxEvent(type="OrderCreated", payload={"id": obj.id}))
```

Adding into the same session inside `before_flush` keeps everything atomic in the same transaction, which is what makes a real outbox.

## Common mistakes

- **Side effects in `@validates`.** The setter runs every time you assign. Doing DB queries or HTTP calls there destroys both performance and tests.
- **Forgetting the `hybrid_property` SQL expression.** Without it, `where` clauses do not compile. Keep both definitions semantically equivalent.
- **Skipping `cache_ok = True` on `TypeDecorator`.** SQLAlchemy 2.x emits warnings when a custom type does not declare cache safety.
- **Triggering another flush from inside an event.** Calling `session.commit()` inside `before_flush` breaks immediately. Only `session.add` is safe.
- **Pushing every business rule into events.** Events run invisibly and are hard to trace. Sometimes an explicit service function is the better answer.

## Production patterns

A typical split looks like this:

- **`TypeDecorator`** for representation: currency, timezone, encryption, JSON.
- **`@validates`** for fast, side-effect-free invariants such as email shape or score range.
- **Mapper events** (`before_insert`, `before_update`) for audit columns and derived fields.
- **Session events** (`before_flush`, `after_commit`) for outbox, cache invalidation, and domain event publishing.
- **Engine events** (`before_cursor_execute`) for observation only. Never put business logic here.

Events are registered at import time, so module load order matters. Either define `@event.listens_for` next to the model in the same module, or call an explicit `register_events()` during application bootstrap so nothing is silently missing.

## Checklist

- [ ] `@validates` only validates and normalizes, no side effects
- [ ] `hybrid_property` defines both the Python and SQL forms
- [ ] `TypeDecorator` declares `cache_ok = True`
- [ ] Mapper events handle lightweight derived fields and audit columns only
- [ ] Session events handle transaction-scoped work like outbox or cache invalidation
- [ ] Engine events handle observation only
- [ ] Event registration is centralized so imports are not silently missed

## Exercises

1. Write a `BcryptString` `TypeDecorator` that hashes a password with bcrypt on write and leaves the hash unchanged on read.
2. Add a `total_amount = unit_price * quantity` `hybrid_property` to an `Order` model and use it in a where clause.
3. Use `before_cursor_execute` and `after_cursor_execute` to log every query that takes longer than one second to a separate file.

## Wrap-up and what is next

The event system, `hybrid_property`, and `TypeDecorator` are SQLAlchemy's official extension points for keeping domain rules near the model. Choosing the right layer in advance, and keeping side effects out of the wrong ones, makes it possible to track where data is being transformed.

The next episode moves the same patterns to async. We will use the `aiosqlite` driver with `AsyncSession`, and explain why lazy loading is even more dangerous in async code.

## Answering the Opening Questions

- **How to attach lifecycle hooks at the model, session, and engine levels using the SQLAlchemy event system?**
  - The article treats Events, hybrid_property, and custom types as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How to validate inputs with `@validates`?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How to define `hybrid_property` so the same attribute works in Python and in SQL?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [SQLAlchemy 101 (1/10): Getting Started with SQLAlchemy 2.x - Engine and Connection Demystified](./01-sqlalchemy-2x-engine-connection.md)
- [SQLAlchemy 101 (2/10): SQLAlchemy Core - Modeling Schema as Python Objects with MetaData, Table, and Column](./02-core-metadata-table-types.md)
- [SQLAlchemy 101 (3/10): SQLAlchemy Core - select, insert, update, delete in 2.x Style](./03-core-select-insert-update-delete.md)
- [SQLAlchemy 101 (4/10): ORM Basics: Defining Models with DeclarativeBase and mapped_column](./04-orm-declarative-mapped-column.md)
- [SQLAlchemy 101 (5/10): Session in Depth: How Unit of Work and Identity Map Actually Work](./05-session-unit-of-work-identity-map.md)
- [SQLAlchemy 101 (6/10): ORM Relationships: Connecting Both Sides Safely with relationship and back_populates](./06-relationships-back-populates.md)
- [SQLAlchemy 101 (7/10): Loading Strategies and the N+1 Problem: When to Pick lazy, joined, or selectin](./07-loading-strategies-n-plus-one.md)
- **SQLAlchemy 101 (8/10): Events, hybrid_property, and custom types (current)**
- SQLAlchemy 101 (9/10): Async SQLAlchemy with aiosqlite and AsyncSession (upcoming)
- SQLAlchemy 101 (10/10): Production patterns: pools, observability, migrations, and deploys (upcoming)

<!-- toc:end -->

## References

- SQLAlchemy: Events — https://docs.sqlalchemy.org/en/20/core/event.html
- SQLAlchemy: ORM Events — https://docs.sqlalchemy.org/en/20/orm/events.html
- SQLAlchemy: Hybrid Attributes — https://docs.sqlalchemy.org/en/20/orm/extensions/hybrid.html
- SQLAlchemy: TypeDecorator — https://docs.sqlalchemy.org/en/20/core/custom_types.html

Tags: Python, SQLAlchemy, ORM, Database

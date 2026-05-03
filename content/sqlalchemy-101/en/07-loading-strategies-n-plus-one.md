---
title: "Loading Strategies and the N+1 Problem: When to Pick lazy, joined, or selectin"
series: sqlalchemy-101
episode: 7
language: en
status: draft
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Python
- SQLAlchemy
- ORM
- N+1
- selectinload
- SQLite
last_reviewed: '2026-05-03'
---

# Loading Strategies and the N+1 Problem: When to Pick lazy, joined, or selectin

The most common complaint about ORMs always lands in the same place: "Why am I seeing 100 SELECTs?" The answer is usually the N+1 query pattern. The `relationship()` we built in Ep6 defaults to lazy loading, so accessing a child attribute on each of N parent objects fires N additional SELECTs. This article shows how N+1 actually arises (with `echo=True` logs you can read line by line), and how to prevent or expose it with `joinedload`, `selectinload`, and `raiseload`.

## Questions this post answers

- What code, exactly, produces an N+1 query pattern?
- How do `lazy="select"` (the default), `joinedload`, and `selectinload` differ at the SQL level?
- Why is `selectinload` typically the safer default for collections (one-to-many, many-to-many)?
- How do you spot the row-explosion (Cartesian) problem caused by `joinedload`?
- What tool catches N+1 automatically in production?
- When is `lazy="raise"` a good idea, and what are its trade-offs?

## Why it matters

Lazy loading makes ORM code readable. You write `user.orders` and SELECTs happen behind the scenes. That convenience often turns into a 50-100x SELECT explosion in production:

- A handler that fetches 100 users and prints each user's most recent order time: 1 + 100 = 101 SELECTs.
- A response listing 50 posts and each post's tags: 1 + 50 = 51 SELECTs.
- An observability dashboard warns "this endpoint averages 80 queries" - that is usually the moment teams notice N+1.

These costs add up: disk IO, network round-trips, lock contention. A 5 ms query becomes 800 ms because of the round-trip count. Even on a single-file engine like SQLite, the lock contention and longer transactions add up; you can't ignore N+1 just because development is local.

## Mental Model

> "Touching a relationship attribute for the first time fires one SELECT." That single sentence is all of lazy loading. N+1 happens when that sentence repeats N times. `joinedload` glues a LEFT JOIN onto the parent SELECT to fetch everything in one shot; `selectinload` fetches the parents first, then loads all children with a single `IN(...)` query.

```
lazy (default):    SELECT users         (1)
                   SELECT orders WHERE user_id = ?   ← user 1
                   SELECT orders WHERE user_id = ?   ← user 2
                   ... (N times)

selectinload:      SELECT users         (1)
                   SELECT orders WHERE user_id IN (1, 2, ...)   (1)

joinedload:        SELECT users LEFT OUTER JOIN orders ...      (1)
```

By query count alone, joinedload looks like the universal winner. But on collection sides (one-to-many), it can multiply rows by parent×child, blowing up traffic. That's why we usually recommend `selectinload` for collections.

## Core concepts

### 1) Default lazy loading and the N+1 it creates

```python
with Session(engine) as session:
    users = session.scalars(select(User)).all()      # SELECT users
    for u in users:
        for o in u.orders:                           # SELECT orders WHERE user_id = ? × N
            print(u.email, o.amount)
```

Every first access to `u.orders` fires one SELECT. That is the textbook N+1 pattern.

### 2) joinedload: one SELECT with a LEFT JOIN

```python
from sqlalchemy.orm import joinedload

stmt = select(User).options(joinedload(User.orders))
users = session.scalars(stmt).unique().all()
```

The ORM emits:

```sql
SELECT users.id, users.email, orders.id, orders.user_id, orders.amount
FROM users
LEFT OUTER JOIN orders ON users.id = orders.user_id
```

Both parents and children come back in one SELECT. But on a one-to-many relationship, the parent row repeats once per child. You must call `unique()` so the ORM collapses the duplicates back to one parent each. With 50 children per parent, the wire payload contains 50 row copies of the parent - traffic-wise, this can hurt.

### 3) selectinload: one IN(...) batch

```python
from sqlalchemy.orm import selectinload

stmt = select(User).options(selectinload(User.orders))
users = session.scalars(stmt).all()
```

The ORM emits exactly two SELECTs:

```sql
SELECT users.id, users.email FROM users
SELECT orders.id, orders.user_id, orders.amount
FROM orders WHERE orders.user_id IN (1, 2, 3, ...)
```

No parent duplication, and all children come back in a tidy IN-batch. For one-to-many collections, this is almost always the most efficient choice.

### 4) Picking the right strategy

| Situation | Recommended | Why |
| --- | --- | --- |
| Many-to-one / one-to-one (child → parent) | `joinedload` | Single LEFT JOIN with no row explosion. |
| One-to-many (parent → child collection) | `selectinload` | One IN-batch. Avoids row explosion. |
| Many-to-many | `selectinload` | Same reasoning. |
| Paginated large child collection | lazy + separate SELECT | Parent up front, children fetched explicitly with LIMIT/OFFSET. |

`subqueryload` exists too, but modern code can almost always rely on `selectinload`.

### 5) raiseload to expose N+1 immediately

```python
from sqlalchemy.orm import raiseload

stmt = select(User).options(raiseload(User.orders))
users = session.scalars(stmt).all()
for u in users:
    print(u.orders)        # raises InvalidRequestError
```

`raiseload` forbids lazy loading. If you reach for a child attribute without explicit eager loading, it raises immediately. Useful for tests or specific handlers where you want to catch N+1 at coding time.

You can also pin a single relationship with `relationship(..., lazy="raise")` to force eager loading on every access.

## Before-After

### Before: lazy loading produces N+1

```python
with Session(engine) as session:
    users = session.scalars(select(User).limit(50)).all()
    return [
        {"email": u.email, "orders": [o.amount for o in u.orders]}
        for u in users
    ]
# echo log: SELECT users (1) + SELECT orders WHERE user_id = ? (50) = 51 SELECTs
```

### After: one line of selectinload

```python
with Session(engine) as session:
    stmt = select(User).options(selectinload(User.orders)).limit(50)
    users = session.scalars(stmt).all()
    return [
        {"email": u.email, "orders": [o.amount for o in u.orders]}
        for u in users
    ]
# echo log: SELECT users (1) + SELECT orders WHERE user_id IN (...) (1) = 2 SELECTs
```

A single `options(selectinload(...))` cuts 51 → 2 SELECTs. That difference shows up as a 5x to 50x improvement in production response time.

## Step-by-step walkthrough

```python
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, Session,
    mapped_column, relationship, selectinload, joinedload, raiseload,
)

engine = create_engine("sqlite:///loader_demo.db", echo=True, future=True)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column()
    user: Mapped[User] = relationship(back_populates="orders")

def seed():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        for i in range(5):
            u = User(email=f"u{i}@example.com")
            for j in range(3):
                u.orders.append(Order(amount=10 * (j + 1)))
            s.add(u)
        s.commit()

def lazy_demo():
    print("--- lazy (default) ---")
    with Session(engine) as s:
        users = s.scalars(select(User)).all()
        for u in users:
            for o in u.orders:
                pass            # N SELECTs

def selectin_demo():
    print("--- selectinload ---")
    with Session(engine) as s:
        users = s.scalars(select(User).options(selectinload(User.orders))).all()
        for u in users:
            for o in u.orders:
                pass            # only 2 SELECTs

def raiseload_demo():
    print("--- raiseload ---")
    with Session(engine) as s:
        users = s.scalars(select(User).options(raiseload(User.orders))).all()
        try:
            users[0].orders         # InvalidRequestError
        except Exception as e:
            print("blocked:", type(e).__name__)

if __name__ == "__main__":
    seed()
    lazy_demo()
    selectin_demo()
    raiseload_demo()
```

With `echo=True`, you can see lazy_demo emit roughly six SELECTs while selectin_demo uses only two. raiseload_demo raises the moment you touch a child attribute.

## Common mistakes

### 1) Using joinedload on collections without thinking

`joinedload(User.orders)` sounds like one SELECT, but with 50 users each averaging 100 orders, you push 5,000 rows over the network. Collections almost always belong to `selectinload`. Reserve `joinedload` for many-to-one and one-to-one.

### 2) Forgetting `unique()`

After joinedload, parent rows repeat. You need `session.scalars(stmt).unique().all()` to collapse them. Skip it and parents will appear in your response duplicated by their child count, with the wrong shape of data downstream.

### 3) Lazy loading in the response phase

Without eager loading at handler time, serialization triggers a SELECT per child. Late SELECTs lengthen the transaction, and serialization libraries hitting detached objects raise errors.

### 4) Putting options outside select

```python
stmt = select(User)
users = session.scalars(stmt, options=selectinload(User.orders)).all()   # wrong
```

`options(...)` belongs to the select object: `select(...).options(...)`. It is not a keyword argument on `scalars()`.

### 5) Hunting N+1 by feel instead of with raiseload

Manual inspection through `echo` regresses easily. In tests, switch on `raiseload` for specific handlers, or wire a query-counter via `event.listens_for(Engine, "before_cursor_execute")` to assert query counts. Regressions then surface immediately.

## In production

- **Per-response eager policy**: the same ORM model often serves several responses, each with different child requirements. Specify `options` per handler. Setting `lazy="joined"` at the model level affects every call site and is usually too blunt.
- **Pagination + selectinload**: `select(User).limit(20).options(selectinload(User.orders))` keeps response size predictable.
- **Query count assertions in tests**: a tiny SQLAlchemy event listener that captures queries inside a context manager makes `assert len(q) == 2` style assertions trivial. They're some of the highest-ROI tests you can write.
- **Logging and tracing**: `echo=True` is impractical in production. Use slow-query logs or an OpenTelemetry SQL exporter to surface N+1.
- **DTO/Pydantic separation**: returning DTOs instead of ORM objects forces you to enumerate which children matter, which makes eager loading policy obvious.

## Checklist

- [ ] Each handler has clearly specified which child collections it needs.
- [ ] Collections use `selectinload`; many-to-one / one-to-one use `joinedload`.
- [ ] When using `joinedload`, `unique()` is called.
- [ ] Tests include query-count assertions or `raiseload`.
- [ ] Production has SQL observability (slow log or tracing).
- [ ] Model-level `lazy=...` changes are reviewed for side effects on other handlers.

## Exercises

1. Run the `lazy_demo` and `selectin_demo` from the walkthrough and count the SELECTs in the echo log. Now bump the seeded users from 5 to 50. How do the SELECT counts change?
2. Apply `joinedload` to `User.orders` and intentionally skip `unique()`. What happens to the result list? Which data is duplicated and how?
3. Apply `raiseload` to every relationship and exercise a typical handler. Which lines blow up? Which N+1 candidates do those failures expose?

## References

- [SQLAlchemy 2.x Loading Relationships](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html)
- [`selectinload` deep dive](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#sqlalchemy.orm.selectinload)
- [`joinedload` and result uniquing](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#joined-eager-loading)
- [`raiseload` for forbidding lazy](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#preventing-unwanted-lazy-loads-with-raiseload)

## Summary and what's next

Default lazy loading reads well, but left alone it produces N+1. The standard recipe is `selectinload` for one-to-many and many-to-many, and `joinedload` for many-to-one and one-to-one. Don't forget `unique()` after joinedload. `raiseload` is the hammer that turns lazy access into an immediate error - paired with query-count assertions, it stops N+1 from ever regressing. Next we look at the event system, hybrid properties, and custom types to see how the ORM grows beyond data mapping into a domain modeling tool.

Tags: Python, SQLAlchemy, ORM, N+1, selectinload, SQLite

---
title: "Session in Depth: How Unit of Work and Identity Map Actually Work"
series: sqlalchemy-101
episode: 5
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
- Session
- Unit of Work
- SQLite
last_reviewed: '2026-05-03'
---

# Session in Depth: How Unit of Work and Identity Map Actually Work

The ORM models from Ep4 do nothing on their own. To push instances back to the database and to read rows back as objects, you need a `Session`. SQLAlchemy's `Session` is more than a connection wrapper - it is a Unit of Work manager that tracks which objects are new, which were modified, and which are scheduled for deletion. It also maintains an Identity Map so that, within a single session, the same primary key always corresponds to the same Python object. This article walks through both mechanisms with real code.

## Questions this post answers

- How does a `Session` relate to connections and transactions?
- What is the Unit of Work, and when is SQL actually emitted?
- How are `flush()` and `commit()` different?
- What does the Identity Map guarantee? Do two lookups for the same PK return the same object?
- What is the impact of `expire_on_commit=True` (the default)?
- Why do we need `sessionmaker`?
- How do ORM objects move between transient/pending/persistent/detached states?

## Why it matters

If you use the ORM without understanding the Session, you bump into mysterious behavior often:

- "I committed, but reading an attribute on the same object in another function fires another SELECT." That's `expire_on_commit`.
- "I fetched a user with `select` here, and another `select` over there - they came back as different objects." Different sessions, or the same session that was already closed.
- "In a test, I INSERTed a row and then SELECTed - the result is empty." A misunderstanding of autoflush or transaction isolation.
- "I kept a `Session` as a module global in my FastAPI handler, and now concurrent requests see weird state." `Session` must be a request-scoped resource.

Every one of these reduces to a single question: "What objects does the Session hold, and when does it emit SQL?" Answering it requires a clear picture of Unit of Work and Identity Map.

## Mental Model

> A `Session` is a notebook that bundles a working scratch pad (Unit of Work) and a cache page (Identity Map) into one cover. While the notebook is open, the same PK is the same object; when you close it (`commit`), all changes are flushed to SQL at once.

Object state transitions look like this:

```
[transient]   → session.add()    → [pending]
[pending]     → session.flush()  → [persistent]   (INSERT goes out)
[persistent]  → session.delete() → [deleted]
[deleted]     → session.flush()  → [persistent×]  (DELETE goes out)
[persistent]  → session.expunge()/session ends → [detached]
```

Two things matter most:

- "Is the object registered with a Session?" decides transient vs pending vs persistent.
- "Does the row this object points to exist in the database?" is decided only after SQL has actually run.

## Core concepts

### 1) Session is a transactional context

A `Session` holds a transaction internally; `commit()` or `rollback()` ends it.

```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    user = User(email="alice@example.com")
    session.add(user)
    session.commit()       # everything up to here is one transaction
```

Leaving the `with` block automatically calls `close()`, returning the connection to the pool (see Ep1 on connection pools). One handler = one Session = one transaction is the simplest mental model.

### 2) Unit of Work: collect changes, then send them together

`session.add(obj)` does not run an INSERT immediately. Instead, the Session puts the object into its "pending" set. The actual SQL fires at one of two moments:

- When you call `session.flush()` explicitly.
- Implicitly, just before the next query or `commit()` (autoflush=True is the default).

```python
with Session(engine) as session:
    a = User(email="a@x.com")
    b = User(email="b@x.com")
    session.add(a)
    session.add(b)
    # No SQL yet - both are pending
    session.flush()
    # Now two INSERT statements go out, and a.id / b.id are populated
    session.commit()
    # Transaction is committed
```

This batching is the heart of Unit of Work. Inserting 100 objects produces a batched flush rather than 100 round-trips, and any UPDATEs and DELETEs in between are sequenced according to dependencies the ORM understands.

### 3) flush versus commit

| Action | flush | commit |
| --- | --- | --- |
| Emits SQL | Yes (INSERT/UPDATE/DELETE) | Yes (flushes if needed, then COMMIT) |
| Ends transaction | No | Yes (`COMMIT;`) |
| Identity Map effect | New PKs filled in | All objects expired if `expire_on_commit=True` |
| When to call | When you need PKs immediately (e.g. for foreign keys) | At end of work unit |

`flush` says "send pending changes to the database now"; `commit` says "end the transaction." A commit usually flushes first.

### 4) Identity Map: same PK, same object

```python
with Session(engine) as session:
    u1 = session.get(User, 1)
    u2 = session.get(User, 1)
    assert u1 is u2          # True - the same object
```

Two lookups for User PK 1 in the same Session run only one SELECT against the database. The second lookup returns the cached object from the Identity Map (a Python dict). Because of this guarantee, ORM code never has two different objects representing the same row carrying conflicting field values.

Across sessions, however, the Identity Map differs. Two objects fetched in two sessions may compare `False` under `is`. Equality should be checked through PKs (`u1.id == u2.id`).

### 5) The expire_on_commit gotcha

The default is `True`, so all ORM objects become expired right after `commit()`. Reading any attribute on an expired object triggers another SELECT.

```python
with Session(engine) as session:
    user = User(email="alice@example.com")
    session.add(user)
    session.commit()
    print(user.email)        # ← extra SELECT here
```

Most web handlers commit and then read object attributes to build a response, so these extra SELECTs add up. You can disable the behavior with `Session(engine, expire_on_commit=False)`, but be aware that objects after commit may then be stale.

## Before-After

### Before: tracking changes by hand

```python
def update_email(conn, user_id, new_email):
    row = conn.execute(select(users).where(users.c.id == user_id)).first()
    if row is None:
        return
    if row.email == new_email:
        return                       # no change → skip UPDATE
    conn.execute(update(users).where(users.c.id == user_id).values(email=new_email))
```

You have to compare manually and craft the UPDATE yourself. The code grows with every column.

### After: let the Session track changes

```python
def update_email(session, user_id, new_email):
    user = session.get(User, user_id)
    if user is None:
        return
    user.email = new_email           # just assign - Session marks it dirty
    # When commit() runs, the Session emits the UPDATE for the changed columns only
```

The Session tracks attribute changes and, on flush, emits an UPDATE that touches only what actually changed. If nothing changed, no UPDATE is emitted at all.

## Step-by-step walkthrough

Save the snippet below and run it; you can watch the SQL and the Identity Map at work.

```python
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

engine = create_engine("sqlite:///session_demo.db", echo=True, future=True)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"

def main() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        a = User(email="a@example.com")
        b = User(email="b@example.com")
        session.add_all([a, b])
        print("before flush, a.id =", a.id)         # None
        session.flush()
        print("after flush, a.id =", a.id)          # 1
        session.commit()

    with Session(engine) as session:
        u1 = session.get(User, 1)
        u2 = session.get(User, 1)
        print("u1 is u2 ?", u1 is u2)               # True

        u1.email = "alice@example.com"
        # No SQL yet - just marked dirty
        session.commit()
        # One UPDATE users SET email=... WHERE id=1 here

if __name__ == "__main__":
    main()
```

With `echo=True`, you can see exactly when SQL is emitted. Early on, leave it on and walk through each line, lining up your intent against the SQL that comes out.

## Common mistakes

### 1) Sharing a module-level Session

```python
session = Session(engine)         # built once at import time

def handler(...):
    user = session.get(User, 1)   # concurrent requests share the Session - dangerous
```

`Session` is not thread-safe. In a web server you must build a new `Session` per request and close it when done. Encapsulate this with `sessionmaker` or your DI container.

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def handler():
    with SessionLocal() as session:
        ...
```

### 2) Using detached objects after commit

```python
with Session(engine) as session:
    user = session.get(User, 1)

print(user.email)        # potential DetachedInstanceError
```

The instant the `with` block ends, `user` is detached. Touching expired attributes raises. Pre-read the fields you need before leaving the block, or use `expire_on_commit=False` to ease the situation.

### 3) Querying while assuming `flush=False`

By default, autoflush=True. Pending changes are flushed automatically right before a query. "I INSERTed and then SELECTed but nothing came back" is usually because the query ran in a different Session. In the same Session, autoflush handles it.

### 4) Exiting the with block without commit

```python
with Session(engine) as session:
    session.add(User(email="x@y.com"))
# no commit() → transaction is rolled back
```

The Session context manager does not auto-commit. You must call `commit()` deliberately. Any write needs an explicit `commit()` or `rollback()`.

### 5) Using `is` comparison across sessions

If the same PK 1 user comes from two different sessions, `u1 is u2` is `False`. The Identity Map is per-session. Always compare with PKs or business keys when crossing session boundaries.

## In production

- **Request-scoped sessions**: in FastAPI, open a `SessionLocal()` context with `Depends` and close it at the end of the response. The cost of creating a Session is negligible; the real cost is acquiring a connection (Ep1 pool).
- **Read-only transactions**: handlers that only read are fine with `expire_on_commit=False` and short transactions. You can let the `with` block close without an explicit commit.
- **Bulk operations**: for tens of thousands of inserts, statement-level bulk inserts (`Session.execute(insert(User), [{...}, ...])`) are far faster than building ORM instances - the dirty-tracking overhead disappears.
- **Using objects outside the transaction**: pre-convert objects to dicts before leaving the block, so you can serialize them safely no matter the state.
- **Tests**: a popular pattern wraps each test in a SAVEPOINT and rolls back fast (using `Session(begin_nested=True)` or wrapping a `connection.begin()` block).

## Checklist

- [ ] Sessions are created and closed per request or work unit.
- [ ] You understand the difference between `commit` and `flush`, and call them deliberately.
- [ ] You audited whether `expire_on_commit` causes extra SELECTs in your response path.
- [ ] You only use `is` comparison within a single Session, and PK comparison elsewhere.
- [ ] Bulk operations consider statement-level inserts instead of ORM objects.
- [ ] `sessionmaker` centralizes your Session creation policy.

## Exercises

1. Build a `Session(engine, autoflush=False)`, then `add` an object and run a SELECT. Then call `flush()` and run the same SELECT. How does the result differ? What does autoflush actually buy you?
2. Compare two sessions: one with `expire_on_commit=False`, the other with the default `True`. After commit, read attributes and count the SQL emitted via `echo=True`. What is the difference?
3. Open two different sessions on the same DB. In session A, fetch user PK 1, change email, commit. In session B (already opened, holding the same user), read the email. What value do you see, and at what moment do you see the new value?

## References

- [SQLAlchemy 2.x ORM Session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [Unit of Work pattern in SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/session_state_management.html)
- [Identity Map](https://docs.sqlalchemy.org/en/20/glossary.html#term-identity-map)
- [`expire_on_commit` parameter](https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.params.expire_on_commit)

## Summary and what's next

A `Session` is not just a connection wrapper. It is the context that combines a working scratch pad (Unit of Work) and a per-PK cache (Identity Map). `add` registers something as pending, `flush` actually emits SQL, and `commit` ends the transaction. `expire_on_commit` is convenient but can trigger extra SELECTs; sharing a Session as a module global is asking for concurrency bugs. Next, we layer relationships on top of this Session - defining `relationship` and using `back_populates` to make bidirectional navigation safe.

Tags: Python, SQLAlchemy, ORM, Session, Unit of Work, SQLite

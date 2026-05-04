---
title: "Async SQLAlchemy with aiosqlite and AsyncSession"
series: sqlalchemy-101
episode: 9
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
  - Python
  - SQLAlchemy
  - async
  - aiosqlite
  - AsyncSession
  - SQLite
last_reviewed: '2026-05-03'
---

# Async SQLAlchemy with aiosqlite and AsyncSession

## What you will learn

- The shape of SQLAlchemy 2.x's async stack: `create_async_engine`, `AsyncEngine`, `AsyncSession`
- How to wire the `aiosqlite` driver to use SQLite from async code
- A one-to-one mapping from sync patterns to async (`session.execute`, `session.scalars`)
- Why lazy loading is more dangerous in async, and how to avoid it
- Session lifecycle in async web frameworks like FastAPI

## Why this matters

Using sync SQLAlchemy from FastAPI, Starlette, or aiohttp blocks the event loop. SQLAlchemy 2.x ships an async API that has been stable since 1.4, and SQLite supports the same patterns through the `aiosqlite` driver.

Async, however, has a few sharp edges that the sync API hides. Lazy loading in particular: in sync code it is just one extra SELECT, but in async it tries to call sync IO from an async context and raises immediately. This article makes those differences explicit.

## Mental model

> Async SQLAlchemy is a **thin awaitable wrapper around the existing ORM**. Internally it does not run the sync ORM on a thread pool; it uses a greenlet-based adapter that exposes sync calls across an async boundary. That is why the API looks almost identical, but every place where IO could happen now requires an explicit `await`.

Two rules cover most of it:

- **Explicit IO**: `select`, `insert`, `update`, `delete` all go through `await session.execute(...)` or `await session.scalars(...)`.
- **Implicit IO is forbidden**: anything that would secretly run SQL behind your back, such as a lazy load, becomes an error in async. That is why eager loading strategies become the default rather than an option.

## Core concepts

### `create_async_engine` and `AsyncEngine`

`from sqlalchemy.ext.asyncio import create_async_engine` builds an `AsyncEngine`. It mirrors the sync `Engine` except `connect` and `begin` are async context managers.

### URL and driver

| DB | URL |
| --- | --- |
| SQLite | `sqlite+aiosqlite:///./app.db` |
| PostgreSQL | `postgresql+asyncpg://user:pass@host/db` |
| MySQL | `mysql+aiomysql://user:pass@host/db` |

This article uses SQLite via `pip install "sqlalchemy>=2.0" aiosqlite`.

### `AsyncSession` and `async_sessionmaker`

`AsyncSession` is the awaitable version of the sync `Session`. Build a factory with `async_sessionmaker` and use it inside an `async with` block. **`expire_on_commit=False` is effectively required** in async; the reason is below.

### No implicit IO

In async, accessing `obj.posts` would issue sync SQL, so SQLAlchemy raises `MissingGreenlet` (or similar). Episode 7's `selectinload` and `joinedload` stop being optional and become the default strategy.

## Before / after

A one-to-one mapping from sync to async:

```python
# Before: sync
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./app.db")
SessionLocal = sessionmaker(engine, expire_on_commit=False)

def list_users():
    with SessionLocal() as session:
        result = session.execute(select(User))
        return result.scalars().all()
```

```python
# After: async
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

engine = create_async_engine("sqlite+aiosqlite:///./app.db")
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def list_users():
    async with SessionLocal() as session:
        result = await session.execute(select(User))
        return result.scalars().all()
```

The deltas are:

- `create_engine` → `create_async_engine`
- URL driver: `sqlite:///` → `sqlite+aiosqlite:///`
- `sessionmaker` → `async_sessionmaker(class_=AsyncSession)`
- `with SessionLocal()` → `async with SessionLocal()`
- `session.execute(...)` → `await session.execute(...)`

## Step-by-step walkthrough

### Step 1: Install

```bash
pip install "sqlalchemy>=2.0" aiosqlite
```

### Step 2: Engine and session factory

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///./app.db", echo=False)
SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
```

### Step 3: Create tables

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): ...

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    name: Mapped[str]

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

`engine.begin()` is an async context manager. DDL methods like `create_all` are sync, so wrap them in `conn.run_sync(...)`.

### Step 4: Basic CRUD

```python
async def create_user(email: str, name: str) -> User:
    async with SessionLocal() as session:
        async with session.begin():
            user = User(email=email, name=name)
            session.add(user)
        await session.refresh(user)
        return user

async def get_user(user_id: int) -> User | None:
    async with SessionLocal() as session:
        return await session.get(User, user_id)

async def list_users() -> list[User]:
    async with SessionLocal() as session:
        result = await session.scalars(select(User).order_by(User.id))
        return list(result)
```

`session.begin()` is also an async context manager that commits on exit, rolls back on exception.

### Step 5: Relationships and eager loading

```python
from sqlalchemy.orm import selectinload

async def list_users_with_posts():
    async with SessionLocal() as session:
        stmt = select(User).options(selectinload(User.posts))
        result = await session.scalars(stmt)
        return list(result)
```

Drop the `selectinload` and the handler will raise `MissingGreenlet` the first time it touches `user.posts`. In async, **eager loading is the default strategy**.

### Step 6: FastAPI integration

```python
from fastapi import FastAPI, Depends

app = FastAPI()

async def get_session():
    async with SessionLocal() as session:
        yield session

@app.get("/users")
async def list_users(session: AsyncSession = Depends(get_session)):
    result = await session.scalars(select(User).options(selectinload(User.posts)))
    return [{"id": u.id, "email": u.email, "posts": len(u.posts)} for u in result]
```

A new session opens and closes per request, and the handler only worries about `await`.

## Common mistakes

- **Leaving `expire_on_commit=True`.** Reading attributes after commit triggers a lazy refresh, which becomes an immediate error in async. `False` is the de facto default.
- **Using lazy relationships.** In sync this is just an extra SELECT; in async it raises `MissingGreenlet`. Always use `selectinload` or `joinedload` explicitly.
- **Using a sync driver URL.** `sqlite:///` cannot build an async engine. The driver must be explicit, e.g. `sqlite+aiosqlite:///`.
- **Forgetting `run_sync` for DDL.** `create_all` is sync, so it must be called as `await conn.run_sync(Base.metadata.create_all)`.
- **Sharing a session across requests.** `AsyncSession` is not thread- or coroutine-safe. Build a new one per request.

## Production patterns

- **Per-request session lifecycle.** Use a FastAPI dependency or Starlette middleware so sessions open and close around each request.
- **Per-handler eager loading policy.** Let the query function describe which relationships it uses. That stops N+1 regressions before they ship.
- **Transactions via `async with session.begin()`.** A context manager is safer than explicit begin/commit pairs.
- **SQLite caveat.** SQLite allows only one writer. Even with async, multiple coroutines writing concurrently will hit `SQLITE_BUSY`. For write-heavy workloads, PostgreSQL with asyncpg is a better fit.
- **Tests.** Use `pytest-asyncio`. Build the engine and session factory in fixtures, and call `await engine.dispose()` at fixture teardown.

## Checklist

- [ ] URL spells out the async driver (`sqlite+aiosqlite://`)
- [ ] Factory is `async_sessionmaker(..., class_=AsyncSession, expire_on_commit=False)`
- [ ] Every SQL call is `await session.execute / scalars / get`
- [ ] Relationships are pre-loaded with `selectinload` or `joinedload`
- [ ] DDL is wrapped in `await conn.run_sync(...)`
- [ ] Sessions are created per request and closed at the boundary
- [ ] `await engine.dispose()` is called on shutdown

## Exercises

1. Port the sync CRUD above to async and verify equivalence with unit tests.
2. Drop the `selectinload` and reproduce the `MissingGreenlet` error to see exactly when it fires.
3. Build a FastAPI `/users/{id}` endpoint that uses an async session dependency and eager loading together.

## Wrap-up and what is next

Async SQLAlchemy is the awaitable version of the sync API, but it requires a real shift in mental model because implicit IO disappears. Switch the driver, add `await`, and make eager loading the default — those three moves cover most of the migration.

The next episode covers production patterns: pool sizing, pre-ping, observability, slow-query logging, and how migrations and deploys should be sequenced.

<!-- toc:begin -->
## In this series

- [Getting Started with SQLAlchemy 2.x - Engine and Connection Demystified](./01-sqlalchemy-2x-engine-connection.md)
- [SQLAlchemy Core - Modeling Schema as Python Objects with MetaData, Table, and Column](./02-core-metadata-table-types.md)
- [SQLAlchemy Core - select, insert, update, delete in 2.x Style](./03-core-select-insert-update-delete.md)
- [ORM Basics: Defining Models with DeclarativeBase and mapped_column](./04-orm-declarative-mapped-column.md)
- [Session in Depth: How Unit of Work and Identity Map Actually Work](./05-session-unit-of-work-identity-map.md)
- [ORM Relationships: Connecting Both Sides Safely with relationship and back_populates](./06-relationships-back-populates.md)
- [Loading Strategies and the N+1 Problem: When to Pick lazy, joined, or selectin](./07-loading-strategies-n-plus-one.md)
- [Events, hybrid_property, and custom types](./08-events-hybrid-types.md)
- **Async SQLAlchemy with aiosqlite and AsyncSession (current)**
- Production patterns: pools, observability, migrations, and deploys (upcoming)

<!-- toc:end -->

## References

- SQLAlchemy: Asynchronous I/O — https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- aiosqlite — https://github.com/omnilib/aiosqlite
- SQLAlchemy: AsyncSession API — https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncSession
- FastAPI: SQL (Relational) Databases — https://fastapi.tiangolo.com/tutorial/sql-databases/

Tags: Python, SQLAlchemy, ORM, Database

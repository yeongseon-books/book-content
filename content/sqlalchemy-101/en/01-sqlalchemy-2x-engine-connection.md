---
title: Getting Started with SQLAlchemy 2.x - Engine and Connection Demystified
series: sqlalchemy-101
episode: 1
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
- Engine
- Connection
- SQLite
- DBAPI
last_reviewed: '2026-05-03'
---

# Getting Started with SQLAlchemy 2.x - Engine and Connection Demystified

> SQLAlchemy 101 series (1/10)

---

When you `pip install sqlalchemy` and write your first lines of code, the most common misconception is that "SQLAlchemy replaces standard drivers like `sqlite3`." The opposite is true. SQLAlchemy sits **on top of** PEP 249 DB-API drivers. The moment you write `create_engine("sqlite:///app.db")`, SQLAlchemy is still doing `import sqlite3` under the hood. Internalizing this single fact makes nearly every SQLAlchemy behavior fall into place.

This series walks through SQLAlchemy 2.x using SQLite, end to end. The first post tackles the lowest layer: what `Engine` and `Connection` are, and why they were designed this way. ORM and Session show up later in the series. For now, we focus on a very concrete question: how does a single line of SQL travel from your Python code to a SQLite file on disk?

## What you will learn

- That SQLAlchemy is split into two layers, Core and ORM, and that Engine and Connection are the entry points to Core
- That `create_engine()` returns a factory bundling a dialect, the DB-API driver, a connection pool, and a parsed URL
- How the 1.x to 2.x transition changed defaults: `future=True` everywhere, unified `select()`, `Mapped[]` typing, native async
- The difference between `engine.connect()` and `engine.begin()`, and how 2.x makes transactions explicit
- How to run raw SQL safely with `text()` and named parameter binding
- SQLite URL conventions (`sqlite:///`, `sqlite:////`, `:memory:`) and how to apply PRAGMA via events

## Questions this post answers

- Do I still need to import `sqlite3` when I use SQLAlchemy?
- Does `create_engine()` open a SQLite file immediately, or is it lazy?
- Why was `engine.execute("SELECT 1")` removed in 2.x?
- How does a Connection differ from an ORM Session?
- Should I default to `with engine.connect()` or `with engine.begin()`?
- Where do I enable SQLite's `foreign_keys` PRAGMA in SQLAlchemy?

## Why this matters

Many SQLAlchemy tutorials begin with `Base = declarative_base()` from the ORM. As a result, when something breaks outside the ORM, say a connection drops or a transaction commits unexpectedly, beginners have no idea where to look. Engine and Connection are the foundation that supports the ORM Session, and when something goes wrong inside a Session, you ultimately have to debug at the Connection level.

In production, the most common SQLAlchemy headaches start at the Engine layer. SQLite's `database is locked` errors, `Lost connection` retries, connection pool exhaustion, autocommit mode confusion: all of these are configured on the Engine. Without a clear mental model, you end up tweaking `pool_size`, `pool_recycle`, and `connect_args` by guesswork.

Finally, the 1.x-to-2.x transition is not just a syntax change, it's a usage-model change. 2.x enforces the rule that "execute belongs to a Connection, and every Connection use happens inside a transaction." If you don't know that rule, code written in 2.x style can silently misbehave because of 1.x thinking.

## Mental Model

The Engine in SQLAlchemy is "the ability to talk to a database, made into an object." A Connection is the actual communication channel; an Engine is the factory that holds the configuration and capability to manufacture those channels.

> The Engine is not a connection. The Engine is the object that **knows how to make** connections, holding a dialect and a pool. SQL actually flows through a Connection, and a Connection always lives inside a transaction context.

Visually:

```
Application code
      │
      ▼
   Engine ── (Dialect: sqlite) ── (URL: sqlite:///app.db)
      │
      ├── ConnectionPool (lazy)
      │       └── DBAPI connection (sqlite3.Connection) × N
      │
      └── connect() / begin()
              │
              ▼
          Connection (SQLAlchemy wrapper)
              │
              ▼
          execute(text("SELECT 1"))
              │
              ▼
          DBAPI cursor → SQLite file
```

Three things matter. First, the Engine bundles a dialect (which database family), a URL (where it lives), and a pool (how many connections to keep and reuse). Second, a Connection wraps a PEP 249 DB-API connection one layer thicker, and all SQL execution flows through Connection methods. Third, in 2.x transactions are explicit. `connect()` starts an implicit transaction but you must commit it yourself, while `begin()` auto-commits or rolls back when its block exits.

## Core concepts

### Two layers: Core and ORM

SQLAlchemy is split into two large layers. **Core** lets you build SQL as Python expressions and execute it through Engine and Connection. **ORM** sits on top of Core and adds mapped Python classes plus a Session for object-relational mapping. They are separate but complementary, and you can always drop down to Core from inside the ORM when needed.

This series spends posts 1 through 3 on Core and starts ORM in post 4. Even if you only use the ORM, you need Core to debug production issues.

### The Engine is a lazy factory

`create_engine()` does not connect to the database when you call it. It imports the dialect, parses the URL, and prepares the pool, nothing more. The first connect attempt is when SQLite actually opens or creates the file.

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite:///app.db", echo=True)
# At this point, app.db is not opened yet.

with engine.connect() as conn:
    # This is when sqlite3.connect("app.db") actually runs.
    ...
```

Because of this laziness, it's safe to define `engine` as a module-level global at application import time. No file lock or network call happens just because your module was imported.

### URLs and dialects

SQLAlchemy URLs follow `dialect+driver://user:pass@host:port/database`, but for SQLite the host and user portions are empty.

| URL | Meaning |
| --- | --- |
| `sqlite:///app.db` | Relative path from current working directory |
| `sqlite:////var/data/app.db` | Absolute path (`///` plus an extra `/`) |
| `sqlite://` | In-memory DB (same as `:memory:`) |
| `sqlite:///:memory:` | Same in-memory DB |

`echo=True` logs every SQL statement SQLAlchemy executes to stderr. During learning it's almost always worth keeping on.

### Connection vs Session

| Aspect | Connection (Core) | Session (ORM) |
| --- | --- | --- |
| Layer | Core | ORM |
| Holds | One DBAPI connection | Identity map, unit of work, plus a Connection |
| Operates on | Rows, Result | Mapped objects |
| Transaction | Explicit (`begin()`) | Explicit (`begin()` or `commit()`) |

This series stays with Connection for now, and Session takes over in post 5.

### 2.x style: explicit transactions

The 1.x-era `engine.execute("SELECT 1")` shortcut was removed in 2.x. In 2.x every SQL execution must go through a Connection, and a Connection lives inside a transaction. The 2.x style boils down to three patterns:

```python
# Pattern A: read-only (no commit needed)
with engine.connect() as conn:
    rows = conn.execute(text("SELECT * FROM users")).all()

# Pattern B: write with explicit commit
with engine.connect() as conn:
    conn.execute(text("INSERT INTO users(name) VALUES (:n)"), {"n": "Alice"})
    conn.commit()

# Pattern C: auto-commit/rollback (most recommended)
with engine.begin() as conn:
    conn.execute(text("INSERT INTO users(name) VALUES (:n)"), {"n": "Bob"})
# On normal exit: commit. On exception: rollback.
```

Default to Pattern C (`engine.begin()`) when writes are involved, and only use Pattern A (`engine.connect()`) for pure reads.

## Before-After

### Before: 1.x style and raw sqlite3

```python
# 1.x or earlier mindset: imprecise lifecycle, fuzzy transaction boundary
import sqlite3
conn = sqlite3.connect("app.db")
cur = conn.cursor()
cur.execute("INSERT INTO users(name) VALUES (?)", ("Alice",))
conn.commit()
conn.close()

# Or SQLAlchemy 1.x:
from sqlalchemy import create_engine
engine = create_engine("sqlite:///app.db")
engine.execute("INSERT INTO users(name) VALUES ('Alice')")  # gone in 2.x
```

Problems: connection lifecycle is manual, transaction scope is unclear, and parameter binding style varies by driver (`?`, `%s`, `:name`, etc.).

### After: 2.x style with explicit transactions

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///app.db", echo=False, future=True)

def add_user(name: str) -> None:
    with engine.begin() as conn:  # auto commit/rollback
        conn.execute(
            text("INSERT INTO users(name) VALUES (:name)"),
            {"name": name},
        )
```

Now you get:

- Connections are returned to the pool automatically when the block exits.
- Exceptions trigger automatic rollback.
- Parameter binding is always `:name` style, regardless of dialect.
- The DB-API is still `sqlite3`, but you no longer have to import it directly.

## Step-by-step practice

This section walks from an empty directory to a working SQLAlchemy 2.x program.

### Step 1: Set up the environment

```bash
mkdir sqlalchemy-101-ep1 && cd sqlalchemy-101-ep1
python3 -m venv .venv && source .venv/bin/activate
pip install "sqlalchemy>=2.0"
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

You should see a 2.x version. If you see 1.4, run `pip install --upgrade "sqlalchemy>=2.0"`.

### Step 2: Create an Engine and connect

`step2.py`:

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///app.db", echo=True)

with engine.connect() as conn:
    result = conn.execute(text("SELECT sqlite_version()"))
    print(result.scalar())
```

Run it and you'll see SQLAlchemy's SQL log along with the SQLite version. This is also when `app.db` gets created on disk.

### Step 3: Create a table and insert rows

`step3.py`:

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///app.db", echo=False)

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
    """))
    conn.execute(
        text("INSERT INTO users(name, email) VALUES (:n, :e)"),
        [
            {"n": "Alice", "e": "alice@example.com"},
            {"n": "Bob", "e": "bob@example.com"},
        ],
    )
```

The form `execute(stmt, list_of_dicts)` behaves like `executemany`. Named binding (`:n`, `:e`) works the same regardless of dialect.

### Step 4: Work with the Result

`step4.py`:

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///app.db")

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, name, email FROM users ORDER BY id"))

    for row in result:
        # row is named-tuple-like
        print(row.id, row.name, row.email)

    # To re-iterate, you need a fresh execute (Result is single-pass)
    rows = conn.execute(text("SELECT * FROM users")).all()
    print(f"total: {len(rows)}")
```

### Step 5: Apply SQLite-specific PRAGMAs

SQLite does not enforce foreign key constraints by default. To apply this on every connection automatically, hook into the `connect` event.

```python
from sqlalchemy import create_engine, event

engine = create_engine("sqlite:///app.db")

@event.listens_for(engine, "connect")
def _enable_fk(dbapi_conn, connection_record):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    cur.close()
```

This is the canonical way to apply dialect-specific configuration uniformly across an application.

## Common mistakes

**1. Calling `create_engine(...)` inside a function.** The Engine should be created once at the application level and shared as a module-level global. Calling it repeatedly recreates the connection pool every time, which defeats its purpose.

**2. Forgetting to commit inside `with engine.connect()`.** In 2.x, `connect()` starts a transaction implicitly but does not commit it for you. If you ran INSERT/UPDATE and the data seems to vanish, this is almost always why. Use `begin()` when writes are involved.

**3. Holding a Connection as a long-lived global instead of passing it as an argument.** A Connection is a short-lived resource. Use it inside a context manager and let it return to the pool.

**4. Building raw SQL with string formatting.** Code like `f"SELECT * FROM users WHERE name = '{name}'"` creates a SQL injection vector. Always combine `text("... WHERE name = :name")` with `{"name": name}`.

**5. Confusing slash counts in SQLite URLs.** After `sqlite:///`, the path is relative; absolute paths need an additional slash, giving `sqlite:////var/data/app.db`. Mixing these up creates database files in unexpected locations.

**6. Leaving `echo=True` on in production.** It's a learning aid, not a production setting. In production, configure SQLAlchemy's logger directly.

## Real-world application

In real applications, the Engine is normally a single global instance. Frameworks like FastAPI or Flask typically wire it up like this:

```python
# db.py
from sqlalchemy import create_engine, event
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_conn, _):
    if DATABASE_URL.startswith("sqlite"):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        cur.execute("PRAGMA journal_mode = WAL")
        cur.close()
```

A few options here are meaningful in production. `pool_pre_ping=True` runs a tiny query when a connection is checked out from the pool, weeding out stale connections automatically. `check_same_thread=False` lets SQLite share a connection across threads in multi-threaded servers like FastAPI workers (we cover the details in post 8). `journal_mode = WAL` greatly improves concurrent reader and writer throughput on SQLite.

For tests, `sqlite:///:memory:` or a temporary file gives you isolated fixtures.

```python
import pytest
from sqlalchemy import create_engine, text

@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    with eng.begin() as conn:
        conn.execute(text("CREATE TABLE t(id INTEGER PRIMARY KEY)"))
    yield eng
    eng.dispose()
```

`engine.dispose()` closes every connection in the pool. It's the canonical way to prevent leaks at test teardown.

## Checklist

- [ ] SQLAlchemy 2.x is installed and `sqlalchemy.__version__` returns 2.0 or higher
- [ ] You can explain that `create_engine()` is a lazy factory
- [ ] You can describe the difference between `engine.connect()` and `engine.begin()` in one sentence
- [ ] You know why `engine.execute(...)` was removed in 2.x
- [ ] You used `text()` with named parameter binding
- [ ] You know the SQLite URL slash rule (`sqlite:///` relative, `sqlite:////` absolute)
- [ ] You applied a PRAGMA via `event.listens_for(engine, "connect")`
- [ ] Application code keeps the Engine as a single module-level instance

## Exercises

1. Create an Engine for `sqlite:///./test.db`, create a `users(id, name)` table, insert two rows, and confirm `SELECT COUNT(*)` returns 2. Every SQL execution must happen inside an `engine.begin()` or `engine.connect()` context.
2. Take the same code and replace `engine.begin()` with `engine.connect()`, but do not call commit. Run it twice and observe whether the data persists. Explain why.
3. Create one Engine that applies `PRAGMA foreign_keys = ON` via `event.listens_for(engine, "connect")` and another that does not. Insert a child row whose parent does not exist, and compare the behavior.
4. Create two `sqlite:///:memory:` Engines. Create a table on one and check whether it's visible from the other. Use the result to explain the isolation scope of an in-memory DB.

## Wrap-up and next post

In this post we looked at SQLAlchemy from the bottom up. The Engine is a lazy factory holding a dialect and a pool, a Connection is a short-lived wrapper around a PEP 249 DB-API connection, and 2.x style insists that every execution lives inside an explicit transaction. For SQLite specifically, you also need URL conventions, in-memory DBs, and PRAGMAs like `foreign_keys` to behave like a grown-up database.

Next, we move one layer up to **MetaData, Table, Column, and the type system**. That's where Core stops being "raw SQL with extra plumbing" and starts becoming a proper Python representation of your schema. Once Core SQL expressions click, the ORM in post 4 onwards reads almost like English.

## References

- [SQLAlchemy 2.x Tutorial - Establishing Connectivity](https://docs.sqlalchemy.org/en/20/tutorial/engine.html)
- [SQLAlchemy 2.x - Working with Engines and Connections](https://docs.sqlalchemy.org/en/20/core/connections.html)
- [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
- [SQLite URL forms in SQLAlchemy](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#connect-strings)
- [PEP 249 - Python Database API Specification 2.0](https://peps.python.org/pep-0249/)

Tags: Python, SQLAlchemy, Engine, Connection, SQLite, DBAPI

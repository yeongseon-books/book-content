---
episode: 8
language: en
last_reviewed: '2026-05-03'
series: python-dbapi-101
status: publish-ready
tags:
- Python
- SQLite
- Connection Pool
- Concurrency
- Threading
- PEP 249
targets:
  ebook: true
  hashnode: true
  medium: true
  mkdocs: true
  tistory: false
title: "Python DB-API 101 (8/10): SQLite Connection Management: thread-safety, check_same_thread, and Pooling"
seo_description: A SQLite connection is not the client/server connection you know
  from PostgreSQL or MySQL. There is no separate process.
---

# Python DB-API 101 (8/10): SQLite Connection Management: thread-safety, check_same_thread, and Pooling

Unlike most databases, SQLite has no separate server process. A connection is just a file handle, and transaction locks are expressed in the filesystem. That simplicity is why SQLite shows up everywhere from embedded apps to mid-sized web services, but it also pushes connection-management decisions back onto the application developer.

"Can I share one connection across all threads?" "Should I open a new one per thread?" "How do I hold a connection in an async framework like FastAPI?" This post answers those questions in order.

This is the 8th post in the Python DB-API 101 series.

![SQLite connection Management: thread-safety, check_same_thread, and pooling](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/08/08-01-sqlite-connection-management-thread-safe.en.png)

*SQLite connection Management: thread-safety, check_same_thread, and pooling*

![python db-api 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/08/08-02-mental-model-a-connection-is-a-file-hand.en.png)
*python db-api 101 chapter 8 flow overview*

## Questions to Keep in Mind

- What are SQLite's three thread-safety modes (single, multi, serialized) and how do you check which one you have?
- What does `sqlite3.connect(check_same_thread=True)` actually protect against, and what becomes risky when you flip it to False?
- When is per-thread vs shared connection appropriate?

## Why this matters

A typical SQLite adoption falls into one of two traps. First, "one global connection" shared across all threads. It works at low traffic, then `ProgrammingError: SQLite objects created in a thread can only be used in that same thread` floods the logs the moment concurrency rises. Second, the team flips `check_same_thread=False` to silence the error and moves on. There may be no immediate corruption, but transaction boundaries become impossible to reason about.

The right answer is to verify the thread-safety mode your build offers and pick a connection strategy explicitly. SQLite gives you a lot of freedom; without an explicit policy in code, every developer eventually assumes a different one.

## Mental Model: a connection is a file handle

> A SQLite connection is not the client/server connection you know from PostgreSQL or MySQL. There is no separate process. The lock is a filesystem lock, and the connection object is essentially a file handle plus cache plus transaction state.

This model decides several things:

- Opening a new connection is cheap relative to PostgreSQL. There is no handshake.
- But the connection object still owns transaction state and a prepared-statement cache, so "session" still has meaning.
- Multiple connections can open the same file simultaneously, but only one writer is allowed at a time, even in WAL mode.
- Thread-safety depends on how the SQLite C library was compiled.

Once you internalize this, "pool connections to save handshake cost" becomes a secondary goal in SQLite. The primary goal is to give every thread or request a clear transaction boundary.

## Core Concepts

![Core concepts](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/08/08-03-core-concepts.en.png)

*Core concepts*
### SQLite's three thread-safety modes

The SQLite C library is compiled in one of three native modes:

- **Single-thread**: no thread concurrency at all. Embedded only.
- **Multi-thread**: separate connections in separate threads is fine. Sharing one connection between threads is not.
- **Serialized**: even one connection can be shared across threads safely; an internal mutex serializes calls.

Those native mode names are not the same numbering as Python's DB-API `sqlite3.threadsafety` value. Python exposes this DB-API mapping instead:

- **0** -> SQLite single-thread
- **1** -> SQLite multi-thread
- **3** -> SQLite serialized

The SQLite compile-time `SQLITE_THREADSAFE` numbers are different again (`0`, `2`, `1` in that same order).

Python's `sqlite3` exposes the DB-API value like this:

```python
import sqlite3
print(sqlite3.threadsafety)  # 0, 1, or 3
```

Most distros report `1` or `3`. In Python 3.11+, `3` maps to SQLite's `serialized` mode; `1` maps to `multi-thread`, which still does not mean one connection should be shared across threads.

### What `check_same_thread` actually does

`sqlite3.connect()` defaults to `check_same_thread=True`. This is a **Python-level guard**, separate from the SQLite C library's thread-safety mode. If you try to use the connection from a thread other than the one that created it, the `sqlite3` module raises `ProgrammingError`.

```python
import sqlite3, threading

conn = sqlite3.connect("app.db")  # check_same_thread=True (default)

def worker():
    conn.execute("SELECT 1")  # ProgrammingError

threading.Thread(target=worker).start()
```

Setting `check_same_thread=False` removes the Python guard. From that point on safety depends entirely on which thread-safety mode the underlying SQLite C library was compiled with. So `check_same_thread=False` alone is **not** enough. If you intend to share one connection across threads, first verify that `sqlite3.threadsafety == 3`. Otherwise keep the safer rule: do not share one connection across threads.

### Per-thread vs shared

| Strategy | Pros | Cons | Fit |
|----------|------|------|-----|
| New connection per request | Simplest. Boundary aligns with request. | Connection churn (cheap in SQLite, but not zero) | Short requests, low concurrency |
| Per-thread connection (`threading.local`) | Reused within a thread. Keeps the `check_same_thread` guard. | Connection count grows with thread pool | Traditional WSGI/Flask |
| Single shared connection | Smallest footprint | Requires `sqlite3.threadsafety == 3` + `check_same_thread=False`; writes serialize anyway | Embedded, single worker |
| External async pool (`aiosqlite`) | Plays nicely with coroutines | Single-writer model still applies | FastAPI/aiohttp |

### Why a big connection pool does not fit SQLite

PostgreSQL pools exist to (1) avoid handshake cost and (2) protect the server's max-connection limit. SQLite has neither (no handshake, no server). What SQLite does have is the **single-writer** rule. Thirty connections in a pool will not increase write throughput; they only increase writer contention and BUSY rate.

So instead of a "big pool", consider a "small pool by role": many readers + one writer.

## Before / After

### Before: a global connection used everywhere

```python
# app.py
import sqlite3
conn = sqlite3.connect("app.db", check_same_thread=False)

def get_user(user_id: int):
    return conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
```

When two threads call `execute()` simultaneously, even in serialized mode the cursor state and transaction boundaries can interleave. One thread's `BEGIN` may be silently committed by another thread's call.

### After: per-request connection + WAL

```python
import sqlite3
from contextlib import contextmanager

DB_PATH = "app.db"

def open_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, isolation_level=None, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def db_session():
    conn = open_conn()
    try:
        yield conn
    finally:
        conn.close()

def get_user(user_id: int):
    with db_session() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id=?", (user_id,)
        ).fetchone()
```

A new connection per request, WAL so readers do not block writers, and `busy_timeout` so concurrent writes wait briefly instead of failing immediately. This is enough for most web apps because connection creation is cheap.

## Step by Step: holding SQLite safely in FastAPI

![Step by Step: holding SQLite safely in FastAPI](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/08/08-04-step-by-step-holding-sqlite-safely-in-fa.en.png)

*Step by Step: holding SQLite safely in FastAPI*
### Step 1. Inspect the environment

```python
import sqlite3
print("sqlite3 version:", sqlite3.sqlite_version)
print("threadsafety:", sqlite3.threadsafety)
```

If `threadsafety` is below 1, you cannot share connections between threads. It is usually 1 or 3.

### Step 2. A connection factory

```python
import sqlite3

DB_PATH = "app.db"

def open_conn(*, readonly: bool = False) -> sqlite3.Connection:
    uri = f"file:{DB_PATH}?mode={'ro' if readonly else 'rwc'}"
    conn = sqlite3.connect(
        uri,
        uri=True,
        isolation_level=None,
        timeout=5.0,
        check_same_thread=True,
    )
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    if readonly:
        conn.execute("PRAGMA query_only=ON")
    conn.row_factory = sqlite3.Row
    return conn
```

The factory can open read-only connections explicitly so that read-heavy paths declare intent.

### Step 3. A FastAPI dependency

```python
from fastapi import FastAPI, Depends
import sqlite3

app = FastAPI()

def get_db() -> sqlite3.Connection:
    conn = open_conn()
    try:
        yield conn
    finally:
        conn.close()

@app.get("/users/{user_id}")
def read_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute(
        "SELECT id, email FROM users WHERE id=?", (user_id,)
    ).fetchone()
    return dict(row) if row else {"error": "not found"}
```

FastAPI calls the generator per dependency injection, so each request gets its own connection that is closed on response.

### Step 4. Separate the write path

```python
@app.post("/users", status_code=201)
def create_user(payload: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    db.execute("BEGIN IMMEDIATE")
    try:
        cur = db.execute(
            "INSERT INTO users(email) VALUES (?)", (payload.email,)
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"id": cur.lastrowid}
```

Because `open_conn()` sets `isolation_level=None`, SQLite stays in autocommit mode until you issue `BEGIN ...` yourself. Here `BEGIN IMMEDIATE` defines the write transaction boundary, `commit()` closes it on success, and `rollback()` handles exceptions.

### Step 5. Simulate concurrent writes

```python
import concurrent.futures, sqlite3

def writer(i):
    conn = open_conn()
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT INTO log(msg) VALUES (?)", (f"msg-{i}",))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    list(ex.map(writer, range(200)))
```

Verify that this finishes without BUSY errors thanks to `timeout=5.0` and WAL. If BUSY shows up often, reduce worker count or serialize writes through a single queue (see Practice section).

## Common Mistakes

**Just flipping `check_same_thread=False` and stopping there.** That removes the guard without proving safety. Check `sqlite3.threadsafety` and clarify whether concurrent writes are even allowed.

**Hand-tuning a connection pool per WSGI worker.** Over-engineering for SQLite. Per-request open/close is simpler and safer.

**Calling writes from many threads at once.** Even WAL allows only one writer. Either separate reads or serialize writes through a queue.

**Running `PRAGMA journal_mode=WAL` inside a transaction.** WAL switching must happen outside any transaction, ideally right after opening the connection.

**Module-level singleton connection in FastAPI.** Async contexts will mix transaction boundaries across requests. Use a dependency-injected per-request connection.

**Leaving `timeout` at the default without measuring.** The default 5.0 may be too long or too short for your workload. Measure p99 lock-wait time before deciding.

## In Practice: read/write split with a single-writer queue

When write throughput is your bottleneck, consider:

```python
import queue, threading, sqlite3

write_queue: queue.Queue = queue.Queue()

def writer_worker():
    conn = open_conn()
    while True:
        job = write_queue.get()
        if job is None:
            break
        sql, params = job
        with conn:
            conn.execute(sql, params)

threading.Thread(target=writer_worker, daemon=True).start()
```

Request handlers only enqueue. A single writer thread serializes the work. This eliminates BUSY entirely and lets you batch transactions for higher throughput. The downside is you cannot return the write result synchronously, so this fits "fire-and-forget" paths (logs, event streams).

Reads stay on per-request connections. Thanks to WAL, readers do not wait on the writer.

## Checklist

- [ ] Did you inspect `sqlite3.threadsafety`?
- [ ] Did you choose ONE connection strategy (per-request / per-thread / single / queue)?
- [ ] Are `journal_mode=WAL`, `synchronous=NORMAL`, `foreign_keys=ON` set right after opening?
- [ ] Is `timeout` (or `busy_timeout`) set deliberately?
- [ ] Is there any code path where multiple threads write through the same writer connection at once?
- [ ] In FastAPI, is `Depends(get_db)` injecting a per-request connection?
- [ ] Are transaction boundaries explicit via `with conn:`?
- [ ] Are read-only paths using `mode=ro` or `query_only=ON`?
- [ ] Did you load-test concurrent writes and measure BUSY rate?
- [ ] Did you confirm there are no leaked connections (OS handles or `PRAGMA database_list`)?

## Exercises

1. **Inspect.** Print `sqlite3.threadsafety`, `sqlite3.sqlite_version`, and the default `journal_mode` in your environment.
2. **Reproduce.** Trigger `ProgrammingError` by using a `check_same_thread=True` connection from another thread. Then flip to False, start two simultaneous transactions, and observe what happens.
3. **Measure.** Run 200 concurrent writes under WAL mode and under `journal_mode=DELETE`. Compare BUSY counts.
4. **Design.** Sketch a connection strategy for a system where user requests are read-only and a back-office batch handles all writes.

## Wrap-up and Next

- A SQLite connection is closer to a file handle than to a TCP session. A small role-based set of connections fits better than a large pool.
- `sqlite3.threadsafety` and `check_same_thread` are independent guards; understand both.
- For most web apps, "per-request open/close + WAL + busy_timeout" is the simplest safe default.
- If writes bottleneck, separate read and write, or serialize writes through a queue.

The next post leaves the synchronous world and moves to `aiosqlite`. We will look at how to hold connections and transactions inside asyncio, and how this composes with FastAPI's async paths.

## Answering the Opening Questions

- **What are SQLite's three thread-safety modes (single, multi, serialized) and how do you check which one you have?**
  - The article distinguished `sqlite3.threadsafety` (showing the SQLite C library's concurrency capability as a DB-API number) from `check_same_thread` (a Python-level guard allowing only same-thread usage). Sharing a connection with only `check_same_thread=False` is risky — if you cannot verify `threadsafety == 3`, avoiding connection sharing is the safe default.
- **What does `sqlite3.connect(check_same_thread=True)` actually protect against, and what becomes risky when you flip it to False?**
  - The table set per-request open/close as the default, `threading.local` for traditional WSGI, shared connection for embedded single-worker setups, and a single-writer queue for write-bottleneck paths. The key criterion is not connection-creation cost but how clearly you can maintain the single-writer constraint and transaction boundaries.
- **When is per-thread vs shared connection appropriate?**
  - The FastAPI example had `get_db()` open and close a new connection per request, aligning transaction boundaries exactly with request boundaries. Adding `BEGIN IMMEDIATE` on write paths prevents other requests from committing someone else's transaction or multiple writers tangling and hitting BUSY late — problems that arise from global connection sharing.

<!-- toc:begin -->
## In this series

- [Python DB-API 101 (1/10): Why DB-API 2.0 - The Problem PEP 249 Solved](./01-why-db-api-pep-249.md)
- [Python DB-API 101 (2/10): Connection and Cursor Lifecycle](./02-connection-cursor-lifecycle.md)
- [Python DB-API 101 (3/10): execute, executemany, and Fetch Patterns](./03-execute-fetch-patterns.md)
- [Python DB-API 101 (4/10): Parameter binding and SQL injection defense (sqlite3, PEP 249)](./04-parameter-binding-sql-injection.md)
- [Python DB-API 101 (5/10): Transactions and isolation levels (sqlite3, PEP 249)](./05-transactions-isolation.md)
- [Python DB-API 101 (6/10): Row factories and type adapters (sqlite3, PEP 249)](./06-row-factories-adapters.md)
- [Python DB-API 101 (7/10): PEP 249 Exception Hierarchy and SQLite Error Handling](./07-error-handling-exception-hierarchy.md)
- **Python DB-API 101 (8/10): SQLite Connection Management: thread-safety, check_same_thread, and Pooling (current)**
- Python DB-API 101 (9/10): Asynchronous SQLite with aiosqlite (upcoming)
- Python DB-API 101 (10/10): SQLite Production Patterns: retry, timeout, observability, backup (upcoming)

<!-- toc:end -->

## References

- [Python `sqlite3` — Threadsafety](https://docs.python.org/3/library/sqlite3.html#sqlite3.threadsafety)
- [SQLite And Multiple Threads](https://www.sqlite.org/threadsafe.html)
- [Write-Ahead Logging](https://www.sqlite.org/wal.html)
- [SQLite URI filenames](https://www.sqlite.org/uri.html)
- [FastAPI — Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

Tags: Python, DB-API, PEP 249, Database

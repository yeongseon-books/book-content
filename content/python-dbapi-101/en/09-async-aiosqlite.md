---
episode: 9
language: en
last_reviewed: '2026-05-03'
series: python-dbapi-101
status: publish-ready
tags:
- Python
- SQLite
- asyncio
- aiosqlite
- Async
- PEP 249
targets:
  ebook: true
  hashnode: true
  medium: true
  mkdocs: true
  tistory: false
title: Asynchronous SQLite with aiosqlite
seo_description: aiosqlite does not make SQLite asynchronous. It spawns a background
  thread per connection, queues the awaited method calls onto that thread, and…
---

# Asynchronous SQLite with aiosqlite

What happens if you call `sqlite3.connect()` directly inside `asyncio` code? The code runs, but every `execute()` is a synchronous call that blocks the event loop for its duration. A 1-second query starves every other request the worker is trying to serve.

`aiosqlite` solves this. But it is important to understand what "solve" means here. The library does not make SQLite truly asynchronous. It is an **adapter that runs each sqlite3 call in a background thread per connection and returns a Future to the event loop**. The loop stays unblocked, but SQLite's single-writer constraint is unchanged.

This is the 9th article in the Python DB-API 101 series.

![Asynchronous SQLite with aiosqlite](../../../assets/python-dbapi-101/09/09-01-asynchronous-sqlite-with-aiosqlite.en.png)

*Asynchronous SQLite with aiosqlite*
## Questions this post answers

- How does `aiosqlite` work under the hood? Is it real async I/O?
- How should you hold connections and transactions in an async path?
- What does the `async with` syntax guarantee, and what does it not?
- Is it worth building a connection pool on top of `aiosqlite`?
- How does it compose with FastAPI's async endpoints?

## Why this matters

In an async framework (FastAPI, aiohttp, Starlette), calling synchronous SQLite directly halts the worker for the duration of every query. If a single worker handles 100 concurrent requests and an average query takes 50 ms, p99 latency for the other 99 requests collapses.

There are two fixes: (1) push synchronous sqlite3 to a separate thread pool (`run_in_executor`, FastAPI's `def` handler), or (2) use `aiosqlite` for an async-shaped interface. They are the same mechanism underneath, but `aiosqlite` encapsulates the per-connection thread and gives you `async with` syntax that fits naturally.

The honest pitch: this post is about what `aiosqlite` actually does and does not do. If the word "async" makes you expect higher write throughput, you will be disappointed.

## Mental Model: aiosqlite is sqlite3 + thread + Future

![Mental Model: aiosqlite is sqlite3 + thread + future](../../../assets/python-dbapi-101/09/09-02-mental-model-aiosqlite-is-sqlite3-thread.en.png)

*Mental Model: aiosqlite is sqlite3 + thread + future*
> `aiosqlite` does not make SQLite asynchronous. It spawns a background thread per connection, queues the awaited method calls onto that thread, and returns a Future the event loop can await.

Implications:

- The event loop is no longer blocked. Other coroutines can progress.
- Calls on the same connection are still serialized. Two coroutines cannot use one connection at once.
- One connection means one extra thread. Many connections means many threads.
- SQLite's single-writer constraint is unchanged. A hundred `aiosqlite` connections still serialize at the writer.

So the real value of `aiosqlite` is **event-loop protection**, not "concurrency win". Treat it as an adapter that lets you stay in async code without blocking, not as a way to make SQLite faster.

## Core Concepts

![Core concepts](../../../assets/python-dbapi-101/09/09-03-core-concepts.en.png)

*Core concepts*
### Install and basic use

```bash
pip install aiosqlite
```

```python
import asyncio
import aiosqlite

async def main():
    async with aiosqlite.connect("app.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, body TEXT)")
        await db.execute("INSERT INTO notes(body) VALUES (?)", ("hello",))
        await db.commit()
        async with db.execute("SELECT id, body FROM notes") as cur:
            async for row in cur:
                print(row)

asyncio.run(main())
```

The interface mirrors `sqlite3` closely; you mostly add `await` and switch to `async with` / `async for`.

### Sync vs async, side by side

```python
# Sync
import sqlite3
conn = sqlite3.connect("app.db")
cur = conn.execute("SELECT 1")
row = cur.fetchone()

# Async
import aiosqlite
async with aiosqlite.connect("app.db") as conn:
    async with conn.execute("SELECT 1") as cur:
        row = await cur.fetchone()
```

Almost a 1:1 mapping. The main rule is that every method that talks to SQLite is now a coroutine.

### Transactions

`aiosqlite` keeps the `isolation_level` argument from `sqlite3`. The default `""` (empty string) replicates the implicit-BEGIN behavior. For explicit control, use `isolation_level=None` and issue your own `BEGIN`:

```python
async with aiosqlite.connect("app.db", isolation_level=None) as db:
    await db.execute("BEGIN IMMEDIATE")
    try:
        await db.execute("UPDATE accounts SET balance=balance-? WHERE id=?", (10, 1))
        await db.execute("UPDATE accounts SET balance=balance+? WHERE id=?", (10, 2))
        await db.commit()
    except Exception:
        await db.rollback()
        raise
```

Note that `async with db:` does not behave like the synchronous `with conn:`. The connection's `__aexit__` closes the connection rather than committing the transaction.

## Before / After: a FastAPI handler

### Before: synchronous sqlite3 inside an async path

```python
from fastapi import FastAPI
import sqlite3

app = FastAPI()
conn = sqlite3.connect("app.db", check_same_thread=False)

@app.get("/notes/{note_id}")
async def read_note(note_id: int):
    cur = conn.execute("SELECT body FROM notes WHERE id=?", (note_id,))
    row = cur.fetchone()
    return {"body": row[0] if row else None}
```

Two problems: (1) `execute()` blocks the event loop, and (2) a global shared connection means transaction boundaries leak across requests.

### After: aiosqlite + per-request connection

```python
from fastapi import FastAPI, Depends
import aiosqlite

app = FastAPI()
DB_PATH = "app.db"

async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        db.row_factory = aiosqlite.Row
        yield db

@app.get("/notes/{note_id}")
async def read_note(note_id: int, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT body FROM notes WHERE id=?", (note_id,)) as cur:
        row = await cur.fetchone()
    return {"body": row["body"] if row else None}
```

The event loop is protected and transaction boundaries align with requests. The cost is one new connection-with-thread per request, which leads us to consider a pool.

## Step by Step: a lightweight connection pool

![Step by Step: a lightweight connection pool](../../../assets/python-dbapi-101/09/09-04-step-by-step-a-lightweight-connection-po.en.png)

*Step by Step: a lightweight connection pool*
`aiosqlite` does not ship a pool. Building one is straightforward.

### Step 1. Pool interface

```python
import asyncio
import aiosqlite
from contextlib import asynccontextmanager

class SQLitePool:
    def __init__(self, path: str, *, size: int = 5):
        self._path = path
        self._size = size
        self._queue: asyncio.Queue[aiosqlite.Connection] = asyncio.Queue(maxsize=size)
        self._initialized = False
        self._lock = asyncio.Lock()

    async def _init(self) -> None:
        for _ in range(self._size):
            conn = await aiosqlite.connect(self._path)
            await conn.execute("PRAGMA journal_mode=WAL")
            await conn.execute("PRAGMA foreign_keys=ON")
            conn.row_factory = aiosqlite.Row
            await self._queue.put(conn)
        self._initialized = True

    async def initialize(self) -> None:
        async with self._lock:
            if not self._initialized:
                await self._init()

    @asynccontextmanager
    async def acquire(self):
        conn = await self._queue.get()
        try:
            yield conn
        finally:
            await self._queue.put(conn)

    async def close(self) -> None:
        while not self._queue.empty():
            conn = self._queue.get_nowait()
            await conn.close()
```

The core is a plain `asyncio.Queue`. Acquire pulls a connection out, release pushes it back.

### Step 2. Initialize in FastAPI lifespan

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

pool = SQLitePool("app.db", size=5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await pool.initialize()
    yield
    await pool.close()

app = FastAPI(lifespan=lifespan)

async def get_db():
    async with pool.acquire() as conn:
        yield conn
```

Connections return to the pool when the request finishes; the next request reuses them. A pool size of 1-2x your worker count is a sensible starting point.

### Step 3. Transaction helper

```python
@asynccontextmanager
async def transactional(conn: aiosqlite.Connection):
    await conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise

@app.post("/notes", status_code=201)
async def create_note(payload: NoteCreate, db = Depends(get_db)):
    async with transactional(db):
        cur = await db.execute(
            "INSERT INTO notes(body) VALUES (?)", (payload.body,)
        )
    return {"id": cur.lastrowid}
```

`transactional` owns commit/rollback so handlers stay readable.

### Step 4. Measure under load

```python
import asyncio, aiosqlite, time

async def reader(pool, i):
    async with pool.acquire() as conn:
        await conn.execute("SELECT 1")

async def main():
    pool = SQLitePool("app.db", size=10)
    await pool.initialize()
    t0 = time.perf_counter()
    await asyncio.gather(*(reader(pool, i) for i in range(1000)))
    print(f"{time.perf_counter()-t0:.3f}s")
    await pool.close()

asyncio.run(main())
```

Compare against a baseline that opens and closes a fresh connection per call. A pool that is too small causes queue waits; one that is too large just adds threads and memory.

## Common Mistakes

**Sharing one connection across coroutines.** `aiosqlite` connections are serialized internally, but "concurrent use" is undefined. Treat one connection as held by one coroutine at a time.

**Expecting `async with db:` to handle transactions.** It closes the connection. Use explicit `BEGIN`/`commit`/`rollback` or the `transactional` helper above.

**Expecting higher write throughput from `aiosqlite`.** SQLite's single-writer rule is unchanged. `aiosqlite` protects the event loop; it does not parallelize writers.

**Oversized pools.** Each connection carries a thread. A pool of 100 means 100 background threads. Start at 1-2x your worker count and tune based on measurements.

**Module-level `connect` outside lifespan.** Without a running event loop at import time, this raises. Initialize in `lifespan` or a startup hook.

**Building `aiosqlite` resources in one `asyncio.run(...)` and reusing them in another.** Different event loops; this will not work. Create and close within the same loop.

## In Practice: when async is actually worth it on SQLite

FastAPI runs `def` handlers in a thread pool automatically. That makes synchronous `sqlite3` perfectly safe in many cases. Switch to `async def` (and `aiosqlite`) only when at least one of these is true:

- The handler awaits other I/O (e.g., outbound HTTP).
- The endpoint protocol requires async (WebSocket, SSE).
- You want to interleave multiple SQLite calls with other awaitables in one request.

If none of those apply, `def` + `sqlite3` is simpler and often faster. Adopt `aiosqlite` when the async path itself is the requirement, not as a default.

## Checklist

- [ ] No async handler calls synchronous sqlite3 directly?
- [ ] No two coroutines share a single connection at the same time?
- [ ] Transactions handled explicitly with `BEGIN`/`commit`/`rollback` or via a helper?
- [ ] If using a pool, is it initialized and closed in lifespan?
- [ ] Pool size derived from measurement (start at 1-2x workers)?
- [ ] PRAGMAs (WAL, foreign_keys, etc.) applied right after each connection opens?
- [ ] `busy_timeout` (or SQLite-side timeout) configured intentionally?
- [ ] You verified an actual async need before adopting `aiosqlite`?
- [ ] Concurrent-write load tested for BUSY rate?
- [ ] Pool-leak monitoring in place (e.g., `_queue.qsize()`)?

## Exercises

1. **Measure blocking.** Inside an async handler, call synchronous `sqlite3.connect().execute("...")`. Then issue concurrent requests and measure how the latency of others changes.
2. **Pool size sweep.** Run 1000 concurrent SELECTs through `SQLitePool` with size 1, 5, and 20. Compare total time and per-call latency.
3. **Single-writer check.** Run 1000 concurrent INSERTs through a pool of size 10; measure BUSY rate and compare against a single-writer-queue version.
4. **Decide.** Audit one FastAPI app and list the real reasons each `async def` handler must be async. If none apply, simplify to `def` + sqlite3.

## Wrap-up and Next

- `aiosqlite` does not make SQLite truly async. It is an adapter that protects your event loop.
- Write throughput will not increase. SQLite's single-writer rule still applies.
- Adopt `aiosqlite` only when async is genuinely required by the path.
- A small `asyncio.Queue` based pool initialized in lifespan is enough.

The next post (Episode 10, the series finale) consolidates production patterns: retry plus timeout plus observability, slow-query logging, OpenTelemetry instrumentation, and a backup strategy.

<!-- toc:begin -->
## In this series

- [Why DB-API 2.0 - The Problem PEP 249 Solved](./01-why-db-api-pep-249.md)
- [Connection and Cursor Lifecycle](./02-connection-cursor-lifecycle.md)
- [execute, executemany, and Fetch Patterns](./03-execute-fetch-patterns.md)
- [Parameter binding and SQL injection defense (sqlite3, PEP 249)](./04-parameter-binding-sql-injection.md)
- [Transactions and isolation levels (sqlite3, PEP 249)](./05-transactions-isolation.md)
- [Row factories and type adapters (sqlite3, PEP 249)](./06-row-factories-adapters.md)
- [PEP 249 Exception Hierarchy and SQLite Error Handling](./07-error-handling-exception-hierarchy.md)
- [SQLite Connection Management: thread-safety, check_same_thread, and Pooling](./08-connection-pooling.md)
- **Asynchronous SQLite with aiosqlite (current)**
- SQLite Production Patterns: retry, timeout, observability, backup (upcoming)

<!-- toc:end -->

## References

- [aiosqlite — Documentation](https://aiosqlite.omnilib.dev/)
- [aiosqlite — GitHub](https://github.com/omnilib/aiosqlite)
- [FastAPI — Concurrency and async/await](https://fastapi.tiangolo.com/async/)
- [Python asyncio — Streams and synchronization primitives](https://docs.python.org/3/library/asyncio.html)
- [SQLite — Write-Ahead Logging](https://www.sqlite.org/wal.html)

Tags: Python, DB-API, PEP 249, Database

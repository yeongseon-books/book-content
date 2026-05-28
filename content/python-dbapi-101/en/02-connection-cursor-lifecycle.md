---
title: "Python DB-API 101 (2/10): Connection and Cursor Lifecycle"
series: python-dbapi-101
episode: 2
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
- Connection
- Cursor
- Context Manager
- Resource Management
- SQLite
last_reviewed: '2026-05-03'
seo_description: The two core DB-API objects are connection and cursor. Their names
  are plain, but mishandling their lifecycle leads to connection leaks, locks, and…
---

# Python DB-API 101 (2/10): Connection and Cursor Lifecycle

The two core DB-API objects are connection and cursor. Their names are plain, but mishandling their lifecycle leads to connection leaks, locks, and race conditions. This episode covers how each is created, used, and closed; the context-manager patterns that keep them safe; and the lifecycle pitfalls that bite most often.

This is the 2nd post in the Python DB-API 101 series.

![Connection and cursor lifecycle](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/02/02-01-connection-and-cursor-lifecycle.en.png)

*Connection and cursor lifecycle*

![python db-api 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/02/02-02-1-what-a-connection-is.en.png)
*python db-api 101 chapter 2 flow overview*

> A Connection is a network session; a Cursor is the in-flight state of one query — once you stop conflating them, connection leaks, mystery rollbacks, and stale-fetch bugs all collapse into one diagnosable picture.

## Questions to Keep in Mind

- What are the distinct responsibilities of Connection vs Cursor?
- How does the `with` context manager protect connection and cursor resources?
- What is the trade-off between opening a new connection per call vs reusing one?

## 1. What a Connection Is

A connection is a single communication channel between the application and the database. It wraps a TCP socket (PostgreSQL, MySQL) or a file handle (SQLite), and one connection holds one transaction context.

```python
import sqlite3
conn = sqlite3.connect("notes.db")
print(type(conn))           # <class 'sqlite3.Connection'>
print(conn.in_transaction)  # False (no query yet)
```

Looking at a few `sqlite3.connect()` arguments makes the lifecycle clearer:

```python
conn = sqlite3.connect(
    "notes.db",
    timeout=5.0,                  # how long to wait for a lock
    isolation_level="DEFERRED",   # transaction-begin strategy (None == autocommit)
    check_same_thread=True,       # disallow cross-thread use
    cached_statements=128,        # statement cache size
)
```

## 2. What a Cursor Is

A cursor is the unit of single-query execution. A connection can spawn multiple cursors, each holding its own result set.

```python
cur = conn.cursor()
cur.execute("SELECT 1")
print(cur.description)  # column metadata of the last query
print(cur.rowcount)     # number of affected rows
```

In SQLite (single file), a cursor is essentially a thin wrapper. In PostgreSQL, especially named cursors created with `cursor("name")`, it carries server-side state. That makes cleanup important.

## 3. Safe Use with Context Managers

![Safe use with context managers](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/02/02-03-3-safe-use-with-context-managers.en.png)

*Safe use with context managers*
Manual close is easy to forget. Python's `with` statement is the safer route.

```python
import sqlite3

with sqlite3.connect("notes.db") as conn:
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (title) VALUES (?)", ("hello",))
    # On block exit, SQLite auto-commits or rolls back the transaction.
```

Caveat: SQLite's `Connection` used inside `with` does not close the connection. It only commits or rolls back the transaction. To also close, call `conn.close()` explicitly or wrap it.

```python
from contextlib import contextmanager

@contextmanager
def open_db(path):
    conn = sqlite3.connect(path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

with open_db("notes.db") as conn:
    conn.execute("INSERT INTO notes (title) VALUES (?)", ("hi",))
```

This pattern is the de facto standard in production code: rollback on exception, commit on success, close in either case.

## 4. Cursor Lifecycle Details

```python
with sqlite3.connect("notes.db") as conn:
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM notes")
    while True:
        row = cur.fetchone()
        if row is None:
            break
        print(row)
    cur.close()
```

A cursor holds at most one active query. Calling `execute()` on the same cursor discards the previous result set. To keep two result sets alive simultaneously, create two cursors.

```python
cur1 = conn.cursor()
cur2 = conn.cursor()
cur1.execute("SELECT id FROM users")
cur2.execute("SELECT id FROM orders")
# Both result sets are alive at the same time.
```

## 5. Reusing vs Reopening a Connection

![Reusing vs reopening a connection](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/02/02-04-5-reusing-vs-reopening-a-connection.en.png)

*Reusing vs reopening a connection*
Opening a fresh connection per query reads cleanly but is expensive.

```python
# Inefficient — connect/close on every call
def get_note(note_id):
    with sqlite3.connect("notes.db") as conn:
        return conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
```

A SQLite file connection takes 1-2ms; a PostgreSQL TCP + auth handshake takes tens of ms. So:

- single-user CLI: per-call open is fine
- multi-request server: connection pool (episode 8)
- long-running script: open once and reuse

```python
# For long-running processes
class NoteRepo:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)

    def get(self, note_id):
        return self.conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()

    def close(self):
        self.conn.close()
```

## 6. What Missing Close Looks Like

If a connection is not closed:

- SQLite: file-handle leaks; eventually `Too many open files`
- PostgreSQL: zombie connections in `pg_stat_activity`; once `max_connections` is hit, new logins are refused
- MySQL: sleeping connections in `SHOW PROCESSLIST`; eventually killed by server timeout

The first step in diagnosing a production connection leak is always: are there old idle connections hanging around?

## Five Common Pitfalls

### 1. Misreading SQLite's `with conn`

`with sqlite3.connect(path) as conn:` does not close the connection. It only commits or rolls back the transaction. Use a wrapper like `open_db` above to also close.

### 2. Passing a cursor as a function argument

```python
def query(cur):
    cur.execute(...)
    return cur.fetchall()
```

Exposing a cursor pushes lifecycle responsibility onto the caller. Cleaner: take a connection, create the cursor inside, close it inside.

### 3. Idle timeout on long-lived connections

PostgreSQL and MySQL kill idle connections after a server-defined timeout. The application, unaware, fires the next query and gets `OperationalError: server closed the connection`. Fix with a connection-pool health check (`SELECT 1` ping) or `pool_pre_ping=True` (SQLAlchemy).

### 4. Sharing a connection across processes after fork

After `fork()`, a child process that uses the parent's connection has both ends writing to the same socket. The result is a corrupted protocol. Create a fresh connection in the child, or open one right after `multiprocessing.Process` starts.

### 5. Starting a new query before draining the cursor

```python
cur.execute("SELECT * FROM big_table")
cur.execute("SELECT 1")  # PostgreSQL: errors or discards the previous result
```

With server-side cursors, drain the previous result or call `cur.close()` before issuing another query.

## Key takeaways

- A connection is a communication channel and transaction context; a cursor is a single-query execution unit.
- `with` is the standard for lifecycle management, but SQLite's `with conn` only handles commit/rollback, not close.
- Production code wraps try/commit/except/rollback/finally/close into a context manager.
- For concurrent result sets, use multiple cursors. Connections are expensive, so reuse them or pool them.
- Connection leaks, idle timeouts, fork sharing, and undrained cursors are the most common lifecycle bugs.

The next episode walks through `execute()`, `executemany()`, and the `fetchone()` / `fetchall()` / `fetchmany()` patterns.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Used `with sqlite3.connect(...) as conn:` to run queries without resource leaks.
- [ ] Opened multiple cursors on one connection and observed concurrent reads.
- [ ] Measured the perf gap between per-call connect and reused connect.
- [ ] Reproduced the warnings or locks that appear when close is skipped.

<!-- a-grade-example:end -->

## Answering the Opening Questions

- **What are the distinct responsibilities of Connection vs Cursor?**
  - A connection is the communication channel to the database and the transaction context; a cursor is the execution unit that handles a single query and its result set within that channel. Examining `conn.in_transaction`, `cur.description`, and `cur.rowcount` separately shows that the two objects hold state at different levels.
- **How does the `with` context manager protect connection and cursor resources?**
  - `with sqlite3.connect(...) as conn:` guarantees rollback on exception and commit on normal exit, safely closing the transaction boundary. However, in SQLite this does not close the connection itself, so a wrapper like the article's `open_db()` with `finally: conn.close()` is needed to prevent resource leaks.
- **What is the trade-off between opening a new connection per call vs reusing one?**
  - Opening a new connection per call like `get_note()` is simple, but in environments with expensive handshakes like PostgreSQL it can add tens of milliseconds per request. Reusing connections like `NoteRepo` reduces that cost but introduces lifecycle responsibility — missing a close can lead to `Too many open files` or zombie connections visible in `pg_stat_activity`.

<!-- toc:begin -->
## In this series

- [Python DB-API 101 (1/10): Why DB-API 2.0 - The Problem PEP 249 Solved](./01-why-db-api-pep-249.md)
- **Python DB-API 101 (2/10): Connection and Cursor Lifecycle (current)**
- Python DB-API 101 (3/10): execute, executemany, and Fetch Patterns (upcoming)
- Python DB-API 101 (4/10): Parameter binding and SQL injection defense (sqlite3, PEP 249) (upcoming)
- Python DB-API 101 (5/10): Transactions and isolation levels (sqlite3, PEP 249) (upcoming)
- Python DB-API 101 (6/10): Row factories and type adapters (sqlite3, PEP 249) (upcoming)
- Python DB-API 101 (7/10): PEP 249 Exception Hierarchy and SQLite Error Handling (upcoming)
- Python DB-API 101 (8/10): SQLite Connection Management: thread-safety, check_same_thread, and Pooling (upcoming)
- Python DB-API 101 (9/10): Asynchronous SQLite with aiosqlite (upcoming)
- Python DB-API 101 (10/10): SQLite Production Patterns: retry, timeout, observability, backup (upcoming)

<!-- toc:end -->

---

## References

- [PEP 249 - Connection and Cursor objects](https://peps.python.org/pep-0249/#connection-objects)
- [Python sqlite3 - Connection class](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection)
- [psycopg 3 - Connection lifecycle](https://www.psycopg.org/psycopg3/docs/basic/usage.html)
- [SQLite - File locking and concurrency](https://www.sqlite.org/lockingv3.html)

Tags: Python, DB-API, PEP 249, Database

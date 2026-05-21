---
title: "Python DB-API 101 (1/10): Why DB-API 2.0 - The Problem PEP 249 Solved"
series: python-dbapi-101
episode: 1
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
- DB-API
- PEP 249
- SQLite
- Database Driver
- Standardization
last_reviewed: '2026-05-03'
seo_description: If you have used Python with a database, you have probably touched
  sqlite3, psycopg, pymysql, or oracledb.
---

# Python DB-API 101 (1/10): Why DB-API 2.0 - The Problem PEP 249 Solved

If you have used Python with a database, you have probably touched `sqlite3`, `psycopg`, `pymysql`, or `oracledb`. Their APIs feel oddly similar: `connect()` to open a connection, `cursor()` to get a cursor, `execute()` to run a query, `fetchone()` / `fetchall()` to read results. That uniformity is not a coincidence. It comes from a 1996 standard called **PEP 249 — Python Database API Specification v2.0** (DB-API 2.0 for short).

This first episode walks through why DB-API 2.0 exists, what it standardizes, why we use SQLite throughout the series, and how the same code transfers to other drivers like PostgreSQL or MySQL.

This is the first article in the Python DB-API 101 series.

![Why DB-API 2.0 - the problem PEP 249 solved](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/01/01-01-why-db-api-2-0-the-problem-pep-249-solve.en.png)

*Why DB-API 2.0 - the problem PEP 249 solved*

![python db-api 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/01/01-02-1-the-chaos-before-db-api.en.png)
*python db-api 101 chapter 1 flow overview*

## Questions to Keep in Mind

- How was database access done in Python before PEP 249?
- What five things did DB-API 2.0 actually standardize?
- Why does paramstyle differ across drivers, and how do you protect your code?

## 1. The Chaos Before DB-API

Before the standard, every database library had its own API.

```python
# Imagined old oracle module
conn = oracle.open("dsn", "user", "pass")
result = oracle.run_sql(conn, "SELECT * FROM users")
rows = oracle.read_all(result)

# Imagined old mysql module
db = mysql.connect("server")
db.send("SELECT * FROM users")
data = db.receive_rows()
```

Function names, argument order, and return types were all different. Even within a single team, Oracle code and MySQL code looked completely different, and swapping databases meant rewriting the codebase.

## 2. Five Things PEP 249 Standardized

![Five things PEP 249 standardized](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/01/01-03-2-five-things-pep-249-standardized.en.png)

*Five things PEP 249 standardized*
DB-API 2.0 defines a minimal contract every driver must satisfy.

1. **Module-level constants**: `apilevel`, `threadsafety`, `paramstyle`
2. **Connection objects**: `connect()`, `close()`, `commit()`, `rollback()`, `cursor()`
3. **Cursor objects**: `execute()`, `executemany()`, `fetchone()`, `fetchall()`, `fetchmany()`, `rowcount`, `description`
4. **Type objects**: `Date`, `Time`, `Timestamp`, `Binary`, `STRING`, `NUMBER`, `DATETIME`, `ROWID`
5. **Exception hierarchy**: `Error` -> `InterfaceError`, `DatabaseError` -> `DataError`, `OperationalError`, `IntegrityError`, `InternalError`, `ProgrammingError`, `NotSupportedError`

Even at this minimum, application code becomes much more flexible across drivers.

## 3. Your First DB-API Code with SQLite

This series uses SQLite for every example. SQLite ships with the Python standard library (`sqlite3`), so there is nothing to install, and a database is just one file. Setup time is essentially zero.

```python
import sqlite3

# 1. Open a connection — the file is auto-created if missing
conn = sqlite3.connect("notes.db")

# 2. Acquire a cursor
cur = conn.cursor()

# 3. Prepare schema
cur.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        body TEXT
    )
""")

# 4. INSERT with parameter binding
cur.execute(
    "INSERT INTO notes (title, body) VALUES (?, ?)",
    ("Starting DB-API", "First PEP 249 example"),
)

# 5. Commit the transaction
conn.commit()

# 6. SELECT
cur.execute("SELECT id, title FROM notes")
for row in cur.fetchall():
    print(row)

# 7. Cleanup
cur.close()
conn.close()
```

These seven steps are nearly identical for PostgreSQL and MySQL. The differences are limited to `connect()` arguments and `paramstyle`.

## 4. Only paramstyle Really Differs

![Only paramstyle really differs](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/01/01-04-4-only-paramstyle-really-differs.en.png)

*Only paramstyle really differs*
PEP 249 allows five paramstyles.

| paramstyle | Example | Drivers |
| --- | --- | --- |
| `qmark` | `WHERE id = ?` | sqlite3 |
| `numeric` | `WHERE id = :1` | oracledb |
| `named` | `WHERE id = :id` | sqlite3, oracledb |
| `format` | `WHERE id = %s` | psycopg2 (legacy), pymysql |
| `pyformat` | `WHERE id = %(id)s` | psycopg2 |

Read `module.paramstyle` after import to see which one a driver uses.

```python
import sqlite3
print(sqlite3.paramstyle)  # 'qmark'
```

Abstracting away this single difference is most of what makes driver swaps painless. Libraries like SQLAlchemy automatically absorb it (we will cover SQLAlchemy in the next series).

## 5. Porting the Same Code to PostgreSQL

The SQLite example above moves to psycopg (PostgreSQL driver) with almost no changes.

```python
import psycopg

conn = psycopg.connect("dbname=notes user=postgres password=secret")
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        body TEXT
    )
""")

cur.execute(
    "INSERT INTO notes (title, body) VALUES (%s, %s)",  # qmark -> format
    ("Starting DB-API", "First PEP 249 example"),
)
conn.commit()

cur.execute("SELECT id, title FROM notes")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
```

Three things changed: the `import` line, the `connect()` arguments, and the parameter style (`?` -> `%s`). All application logic (execute, fetchall, commit, rollback) keeps working as-is.

## 6. What DB-API Does Not Cover

A standard does not standardize everything. PEP 249 deliberately leaves several areas untouched.

- **Connection pooling**: up to the driver or library (sqlite3 prefers a single connection; psycopg ships `psycopg_pool` separately)
- **Async API**: PEP 249 itself is sync; async lives in `aiosqlite`, `asyncpg`, `aiomysql`
- **ORM features**: SQLAlchemy, Django ORM, Tortoise ORM are separate abstractions
- **Schema migrations**: Alembic and Django migrations live above DB-API
- **Server-side cursor details**: only partially standardized; mostly driver extensions

Filling these gaps is exactly why higher-level libraries like SQLAlchemy, Alembic, and FastAPI + databases exist.

## Five Common Pitfalls

### 1. Autocommit varies by driver

PEP 249 assumes explicit transactions. SQLite defaults to "implicit transaction begin", while PostgreSQL and MySQL default to autocommit OFF. Forgetting `conn.commit()` produces driver-dependent behavior.

### 2. Forgetting to close the cursor

Skipping `cur.close()` works because GC eventually cleans up, but PostgreSQL with server-side cursors can look like a connection leak. Use `with conn.cursor() as cur:` (when the driver supports it) as a habit.

### 3. fetchall() on large results

`fetchall()` materializes every row in memory. A million rows is OOM territory. For large results use `fetchmany(size=1000)` or the cursor's own iterator.

```python
cur.execute("SELECT * FROM big_table")
for row in cur:  # streaming iteration
    process(row)
```

### 4. Building execute() with string concatenation

```python
# Never do this — SQL injection
cur.execute(f"SELECT * FROM users WHERE name = '{name}'")
```

Always use parameter binding. Episode 4 covers this in detail.

### 5. Sharing one connection across threads

Drivers with `threadsafety=1` cannot share a connection between threads. sqlite3 defaults to `check_same_thread=True`, raising an error if used from another thread. In multi-threaded apps, create a connection per thread or use a connection pool.

## Key takeaways

- DB-API 2.0 (PEP 249) is the minimum contract every Python database driver follows.
- The seven steps connect → cursor → execute → fetch → commit → close are identical across sqlite3, psycopg, and pymysql.
- The biggest driver-to-driver difference is `paramstyle`; the rest of the application code stays the same.
- DB-API intentionally leaves connection pooling, async, ORM, and migrations to higher-level libraries.
- Autocommit, cursor cleanup, fetchall memory, SQL injection, and thread safety are the most common early pitfalls.

The next episode digs into the connection and cursor lifecycle and the context-manager patterns that make them safe.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Ran a full connect → cursor → execute → fetch → close cycle with sqlite3.
- [ ] Identified what changes when porting the same code to PostgreSQL (psycopg).
- [ ] Can explain paramstyle differences in one sentence.
- [ ] Can name three things DB-API does NOT cover (pooling, ORM, migration).

<!-- a-grade-example:end -->

## Answering the Opening Questions

- **How was database access done in Python before PEP 249?**
  - The article treats Why DB-API 2.0 - The Problem PEP 249 Solved as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What five things did DB-API 2.0 actually standardize?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why does paramstyle differ across drivers, and how do you protect your code?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **Python DB-API 101 (1/10): Why DB-API 2.0 - The Problem PEP 249 Solved (current)**
- Python DB-API 101 (2/10): Connection and Cursor Lifecycle (upcoming)
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

- [PEP 249 - Python Database API Specification v2.0](https://peps.python.org/pep-0249/)
- [Python sqlite3 module documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLite official documentation](https://www.sqlite.org/docs.html)
- [psycopg 3 documentation - DB-API 2.0 compliance](https://www.psycopg.org/psycopg3/docs/)

### Related Series

- [SQLAlchemy 101](../../sqlalchemy-101/en/01-sqlalchemy-2x-engine-connection.md) — covers the ORM and Core layers that sit on top of the DB-API this series unpacks. Drop down to this series whenever SQLAlchemy connection behavior or SQL execution feels opaque and you need to see what the underlying driver actually does.

Tags: Python, DB-API, PEP 249, Database

---
title: 'Transactions and isolation levels (sqlite3, PEP 249)'
series: python-dbapi-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: true
  hashnode: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Python
- SQLite
- Transaction
- Isolation
- WAL
- PEP 249
last_reviewed: '2026-05-03'
---

# Transactions and isolation levels (sqlite3, PEP 249)

## Questions this post answers

- Why does sqlite3 issue an implicit BEGIN by default?
- What does `isolation_level=None` actually mean?
- How do `BEGIN DEFERRED`, `IMMEDIATE`, and `EXCLUSIVE` differ in lock behaviour?
- How does WAL mode change transaction semantics?
- How does Python 3.12's new `autocommit` parameter differ from the legacy `isolation_level`?

> A transaction is not "calling commit/rollback" — it is "deciding what runs as one unit." Because sqlite3 picks that unit for you automatically, you must understand the auto-behaviour to avoid surprise locks and data loss.

> Python DB-API 101 (5/10)

---

## What you will learn

This post covers sqlite3 transaction semantics through a PEP 249 lens. Specifically:

1. **PEP 249's transaction model** — connection is the transaction scope; `commit()`/`rollback()` are the terminators.
2. **sqlite3's implicit BEGIN** — the driver issues `BEGIN` automatically before the first DML statement.
3. **The five `isolation_level` values** — `''` (default deferred), `'DEFERRED'`, `'IMMEDIATE'`, `'EXCLUSIVE'`, and `None` (autocommit).
4. **WAL versus rollback journal** — concurrent reader/writer behaviour.
5. **Nested transactions via SAVEPOINT** — what `with con:` actually does.
6. **Python 3.12's `autocommit` parameter** — the new explicit model.

---

## Why this matters

Two operational data incidents dominate in production:

1. **Forgot `commit()`** — INSERTs live only in memory and disappear when the process exits.
2. **Unexpected `BEGIN IMMEDIATE` blocks other connections** — surfaces as a 5-second timeout error to the user.

The sqlite3 driver hides BEGIN management for convenience, and that very convenience produces both incidents above when developers do not know how it works. PEP 249 lets you control this driver behaviour explicitly via `isolation_level` (sqlite3) or the newer `autocommit` attribute.

This post compares the five modes through code and lock scenarios. Once you have it laid out, roughly 80% of transaction-related production issues stop happening.

---

## Mental Model — connection is the transaction scope

```
Connection lifecycle (sqlite3 default)
─────────────────────────────────────────
  open
    │
    │  cur.execute('SELECT ...')   ← no transaction
    │  cur.execute('INSERT ...')   ← driver issues implicit BEGIN
    │  cur.execute('UPDATE ...')   ← same transaction
    │
    │  con.commit()                ← transaction ends, durable
    │
    │  cur.execute('INSERT ...')   ← new implicit BEGIN
    │  con.rollback()              ← changes discarded
    │
  close
```

Two essentials:

- **PEP 249 assumes every connection is in a transaction** — i.e., `autocommit=False` is the default.
- **sqlite3's default behaviour is "auto BEGIN before DML"** — pure SELECT workloads do not open a transaction and need no commit.

---

## Core concepts

### The five `isolation_level` values

| Value | BEGIN variant | autocommit? | Implicit BEGIN issued |
|---|---|---|---|
| `''` (default) | `BEGIN` (= DEFERRED) | No | Before first DML |
| `'DEFERRED'` | `BEGIN DEFERRED` | No | Same |
| `'IMMEDIATE'` | `BEGIN IMMEDIATE` | No | Same — acquires RESERVED lock immediately |
| `'EXCLUSIVE'` | `BEGIN EXCLUSIVE` | No | Same — acquires EXCLUSIVE lock immediately |
| `None` | (no BEGIN) | **Yes** | Each statement commits immediately |

### Lock behaviour per BEGIN mode

SQLite controls concurrent access with a four-level lock: UNLOCKED → SHARED → RESERVED → PENDING → EXCLUSIVE.

- **DEFERRED** — only `BEGIN` is issued; SHARED is taken on first read, RESERVED on first write. Other readers may proceed concurrently.
- **IMMEDIATE** — RESERVED is acquired at `BEGIN` time. Other writers are blocked immediately; readers continue.
- **EXCLUSIVE** — EXCLUSIVE is acquired at `BEGIN` time. All other readers and writers are blocked.

In the default rollback journal (non-WAL), one writer and many readers may coexist; the writer briefly takes EXCLUSIVE at commit.

### WAL mode

```python
con.execute('PRAGMA journal_mode=WAL')
```

WAL (Write-Ahead Logging) writes changes to a sidecar `.wal` file, so **readers and writers truly run concurrently**. WAL is almost always recommended for production. Caveats: it creates `.wal` and `.shm` files next to the database, and it is not safe on network filesystems.

### Python 3.12 `autocommit` parameter

```python
con = sqlite3.connect(path, autocommit=False)  # PEP 249 compliant
con = sqlite3.connect(path, autocommit=True)   # commit after every statement
con = sqlite3.connect(path, autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL)  # legacy isolation_level behaviour
```

Since 3.12, `autocommit` is explicit and recommended. For backward compatibility, `LEGACY_TRANSACTION_CONTROL` is the default.

---

## Before / After

### Before — missing commit

```python
import sqlite3

con = sqlite3.connect('shop.db')
con.execute('CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, total INTEGER)')
con.execute('INSERT INTO orders(total) VALUES (10000)')
# con.commit()  ← forgotten
con.close()

# In a new process
con2 = sqlite3.connect('shop.db')
print(con2.execute('SELECT COUNT(*) FROM orders').fetchone())
# → (0,)   ← INSERT was discarded
```

`con.close()` does NOT commit. A missing commit silently loses the changes.

### After — context manager

```python
with sqlite3.connect('shop.db') as con:
    con.execute('INSERT INTO orders(total) VALUES (10000)')
# Commit on normal exit, rollback on exception
```

`with con:` is a context manager on the connection that **terminates the transaction**. It does not close the connection — close it separately or with `contextlib.closing`.

---

## Step-by-step walkthrough

### Step 1 — observe default behaviour

```python
import sqlite3

con = sqlite3.connect(':memory:')
con.execute('CREATE TABLE t(v INTEGER)')

# SELECT alone does not open a transaction
con.execute('SELECT * FROM t').fetchall()
print(con.in_transaction)   # → False

# Implicit BEGIN before DML
con.execute('INSERT INTO t(v) VALUES (1)')
print(con.in_transaction)   # → True

con.commit()
print(con.in_transaction)   # → False
```

### Step 2 — autocommit (`isolation_level=None`)

```python
con = sqlite3.connect(':memory:', isolation_level=None)
con.execute('CREATE TABLE t(v INTEGER)')
con.execute('INSERT INTO t(v) VALUES (1)')
# Already durable, no commit needed
print(con.in_transaction)   # → False
```

Not appropriate for batch inserts: every statement triggers an fsync, which is very slow.

### Step 3 — IMMEDIATE to avoid lock surprises

In long transactions doing read → modify → write, default DEFERRED can hit SQLITE_BUSY late in the cycle. When write intent is clear, take the lock up-front with IMMEDIATE.

```python
con = sqlite3.connect('shop.db', isolation_level='IMMEDIATE')

with con:
    balance = con.execute('SELECT balance FROM accounts WHERE id=1').fetchone()[0]
    new_balance = balance - 1000
    con.execute('UPDATE accounts SET balance=? WHERE id=1', (new_balance,))
```

Other writers are blocked immediately at IMMEDIATE, so no lost-update can sneak in mid-transaction.

### Step 4 — enable WAL

```python
con = sqlite3.connect('shop.db')
con.execute('PRAGMA journal_mode=WAL')
con.execute('PRAGMA synchronous=NORMAL')   # safe + fast under WAL
```

`journal_mode` is persisted at the database file level, so set it once.

### Step 5 — nested transactions with SAVEPOINT

PEP 249 does not define nested transactions, but SQLite emulates them via `SAVEPOINT`.

```python
con.execute('SAVEPOINT sp1')
try:
    con.execute("INSERT INTO orders(total) VALUES (5000)")
    con.execute("INSERT INTO order_items VALUES (?, ?)", (1, 'item-A'))
    con.execute('RELEASE SAVEPOINT sp1')
except Exception:
    con.execute('ROLLBACK TO SAVEPOINT sp1')
    con.execute('RELEASE SAVEPOINT sp1')
    raise
```

The outer transaction stays open; only the inner savepoint partially rolls back.

### Step 6 — explicit autocommit on Python 3.12+

```python
import sqlite3
assert sqlite3.sqlite_version_info >= (3, 24)   # SAVEPOINT stable

con = sqlite3.connect('shop.db', autocommit=False)
con.execute('BEGIN IMMEDIATE')
try:
    con.execute('UPDATE accounts SET balance = balance - 1000 WHERE id = 1')
    con.execute('UPDATE accounts SET balance = balance + 1000 WHERE id = 2')
    con.commit()
except Exception:
    con.rollback()
    raise
```

With `autocommit=False`, you write BEGIN explicitly and the driver does not interfere.

---

## Common mistakes

1. **Assuming `con.close()` commits.** It does not. Changes are lost.
2. **Mistaking `with sqlite3.connect(...) as con:` for close.** That context manager only terminates the transaction; the connection stays open. Close it separately or use `contextlib.closing`.
3. **Default DEFERRED for long reads.** A concurrent writer that commits mid-read can trigger SQLITE_BUSY. For pure reads, do not begin a transaction; for read-then-write, prefer `BEGIN IMMEDIATE`.
4. **Using `isolation_level=None` for batch inserts.** Per-statement fsync makes it 100–1000× slower.
5. **Setting WAL on NFS/SMB.** Locking semantics break and may corrupt the database. Use local disk only.
6. **Assuming multiple connections share a transaction.** Each connection has its own transaction context. To share, use the same connection.
7. **Calling `PRAGMA journal_mode=WAL` inside a transaction.** It needs an external lock and fails. Set it right after opening the connection.
8. **Mixing `isolation_level` with `autocommit` on 3.12+.** `autocommit` wins. New code should use `autocommit` only.

---

## Production application

### Recommended baseline configuration

```python
con = sqlite3.connect('app.db', timeout=5.0, isolation_level='IMMEDIATE')
con.execute('PRAGMA journal_mode=WAL')
con.execute('PRAGMA synchronous=NORMAL')
con.execute('PRAGMA foreign_keys=ON')
con.execute('PRAGMA busy_timeout=5000')
```

- `timeout=5.0` (Python) + `busy_timeout=5000` (SQLite) — auto-retry on lock contention for up to five seconds.
- `IMMEDIATE` — declares write intent up-front and surfaces SQLITE_BUSY early.
- `WAL` + `synchronous=NORMAL` — balanced concurrency and performance.

### Transaction-per-request pattern (FastAPI example)

```python
from contextlib import contextmanager

@contextmanager
def tx():
    con = sqlite3.connect('app.db', isolation_level='IMMEDIATE')
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

# Usage
with tx() as con:
    con.execute('INSERT INTO orders(total) VALUES (?)', (10000,))
```

One request = one transaction = one connection. Simple and easy to debug.

### Monitoring

Two metrics catch most issues:

- `SQLITE_BUSY` count — rising contention means too many IMMEDIATE holds or transactions running too long.
- Average transaction duration (ms) — once it crosses ~100 ms, it is time to split read-modify-write phases.

### Backups

Under WAL, `.backup()` is safe.

```python
src = sqlite3.connect('app.db')
dst = sqlite3.connect('backup.db')
with dst:
    src.backup(dst)
```

---

## Checklist

- [ ] Always end with `con.commit()` or `with con:` before `con.close()`.
- [ ] Functions that write start with `isolation_level='IMMEDIATE'`.
- [ ] Production databases default to WAL + `synchronous=NORMAL` + `busy_timeout=5000`.
- [ ] Read-only queries use a separate connection or do not begin a transaction explicitly.
- [ ] `autocommit=None` (legacy) is never used for batch inserts.
- [ ] Nested behaviour uses explicit `SAVEPOINT`.
- [ ] New code on Python 3.12+ uses `autocommit=False` plus explicit BEGIN.

---

## Exercises

1. **Missing-commit experiment.** INSERT and close without `with con:`, then read from a new process and confirm zero rows. Add `with con:` and verify the change persists.
2. **DEFERRED vs IMMEDIATE.** Start two Python processes that both INSERT concurrently. Compare when SQLITE_BUSY appears under DEFERRED versus IMMEDIATE.
3. **WAL impact.** Compare throughput of five readers + one writer with `journal_mode=DELETE` (default) versus `WAL`.
4. **SAVEPOINT.** In a single transaction, INSERT 3 rows → SAVEPOINT → INSERT 2 more → ROLLBACK TO. Verify the row count.
5. **Compare autocommit modes.** On Python 3.12+, exercise `autocommit=True/False/LEGACY_TRANSACTION_CONTROL` and compare `con.in_transaction` under the same scenario.

---

## Summary and next post

sqlite3's transaction handling is conveniently automatic, but that very automation maps directly to lock and data-loss incidents in production when you do not know the rules. Internalising the five `isolation_level` values, the BEGIN variants, and WAL mode makes most transaction-related issues diagnosable.

The next post covers **row factories and type adapters** — returning rows as dicts, dataclasses, or Pydantic models; `detect_types` with custom adapters/converters; and safely mapping new types such as `Decimal` or `Enum`.

<!-- toc:begin -->
## In this series

- [Why DB-API 2.0 - The Problem PEP 249 Solved](./01-why-db-api-pep-249.md)
- [Connection and Cursor Lifecycle](./02-connection-cursor-lifecycle.md)
- [execute, executemany, and Fetch Patterns](./03-execute-fetch-patterns.md)
- [Parameter binding and SQL injection defense (sqlite3, PEP 249)](./04-parameter-binding-sql-injection.md)
- **Transactions and isolation levels (sqlite3, PEP 249) (current)**
- Row factories and type adapters (sqlite3, PEP 249) (upcoming)
- PEP 249 Exception Hierarchy and SQLite Error Handling (upcoming)
- SQLite Connection Management: thread-safety, check_same_thread, and Pooling (upcoming)
- Asynchronous SQLite with aiosqlite (upcoming)
- SQLite Production Patterns: retry, timeout, observability, backup (upcoming)

<!-- toc:end -->

---

## References

- [PEP 249 – Python Database API Specification v2.0](https://peps.python.org/pep-0249/)
- [Python sqlite3 — transaction control](https://docs.python.org/3/library/sqlite3.html#sqlite3-controlling-transactions)
- [SQLite — File Locking and Concurrency](https://www.sqlite.org/lockingv3.html)
- [SQLite — Write-Ahead Logging](https://www.sqlite.org/wal.html)
- [SQLite — PRAGMA journal_mode](https://www.sqlite.org/pragma.html#pragma_journal_mode)
- [Python 3.12 sqlite3 autocommit](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.autocommit)

Tags: Python, DB-API, PEP 249, Database

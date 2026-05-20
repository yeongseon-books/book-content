---
series: computer-science-101
episode: 8
title: "Computer Science 101 (8/10): Databases"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Databases
  - SQL
  - Indexes
  - Transactions
  - ACID
seo_description: How databases store, query, and protect data — focused on indexes and transactions, as part of the CS 101 series.
last_reviewed: '2026-05-15'
---

# Computer Science 101 (8/10): Databases

Finding one row out of millions in milliseconds is rarely about the SQL sentence alone. It is about the data structures, execution plan, and locking behavior hidden underneath that sentence. That is why so many production incidents end up tracing back to the database layer.

This is post 8 in the Computer Science 101 series.

In this article, we'll connect SQL, indexes, execution plans, and ACID transactions so that database behavior stops feeling like a black box.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Databases?
- Which signal should the example or diagram make visible for Databases?
- What failure should be prevented first when Databases reaches a real system?

## Big Picture

![Computer Science 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/08/08-01-concept-at-a-glance.en.png)

*Computer Science 101 chapter 8 flow overview*

This picture places Databases inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Databases is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions This Article Answers

- How does a database store large amounts of data and still answer quickly?
- Why can an index change lookup time so dramatically?
- What is the gap between a SQL statement and the plan the DB actually executes?
- What failures do transactions and ACID protect you from?
- Why do N+1 queries and long transactions so often become production incidents?

## What You Will Learn

- The basic concepts of relational databases
- How to query and modify data with SQL
- How indexes make lookups fast
- Transactions and ACID

## Why It Matters

Most service incidents start at the database. A single slow query can paralyze the whole system, and a missed transaction can corrupt data. Without understanding SQL, indexes, and transactions, you can't grow as a backend engineer.

> A DB is not just storage; it is the system in charge of concurrency and consistency.

Queries are short, but deep algorithms sit behind them.

## Concept at a Glance

> An index is like the index in a book. Instead of skimming every page, you jump straight to the right one through the index.

## Key Terms

| Term | Description |
| --- | --- |
| Table | The basic unit of relational data, made of rows and columns |
| Primary key | The column that uniquely identifies a row |
| Index | A data structure for finding rows quickly by a given column (usually a B-Tree) |
| Transaction | A logical unit grouping several SQL statements together |
| ACID | The four properties a transaction must satisfy: Atomicity, Consistency, Isolation, Durability |
| Query planner | The DB component that decides how to execute a SQL statement |

## Before / After

**Before — N+1 queries with no index:**

```python
# Fetch orders for 100 users — 101 queries
users = cursor.execute("SELECT id FROM users").fetchall()
orders = []
for (user_id,) in users:
    cursor.execute("SELECT * FROM orders WHERE user_id = ?", (user_id,))
    orders.extend(cursor.fetchall())
```

**After — JOIN with an index:**

```python
# A single query, fast when user_id is indexed
cursor.execute("""
    SELECT u.id, o.id, o.amount
    FROM users u
    JOIN orders o ON o.user_id = u.id
""")
orders = cursor.fetchall()
```

## Hands-On: Step by Step

### Step 1: Build a small DB with SQLite

```python
import sqlite3

conn = sqlite3.connect(":memory:")
cur = conn.cursor()

cur.executescript("""
    CREATE TABLE users (
        id    INTEGER PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        name  TEXT NOT NULL
    );

    CREATE TABLE orders (
        id      INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        amount  INTEGER NOT NULL
    );
""")

cur.executemany(
    "INSERT INTO users (email, name) VALUES (?, ?)",
    [("a@x.com", "Alice"), ("b@x.com", "Bob"), ("c@x.com", "Carol")],
)
cur.executemany(
    "INSERT INTO orders (user_id, amount) VALUES (?, ?)",
    [(1, 1000), (1, 500), (2, 700)],
)
conn.commit()
```

### Step 2: Basic queries

```python
# SELECT
for row in cur.execute("SELECT id, email FROM users"):
    print(row)

# WHERE + ORDER BY + LIMIT
for row in cur.execute(
    "SELECT name, email FROM users WHERE name LIKE 'A%' ORDER BY id LIMIT 10"
):
    print(row)

# JOIN
for row in cur.execute("""
    SELECT u.name, SUM(o.amount) AS total
    FROM users u
    LEFT JOIN orders o ON o.user_id = u.id
    GROUP BY u.id
"""):
    print(row)
```

### Step 3: The difference an index makes

```python
import sqlite3
import time
import random

conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute("CREATE TABLE big (id INTEGER PRIMARY KEY, k INTEGER, v TEXT)")
cur.executemany(
    "INSERT INTO big (k, v) VALUES (?, ?)",
    [(random.randint(0, 10_000_000), "x") for _ in range(200_000)],
)
conn.commit()

target = 12345

start = time.perf_counter()
cur.execute("SELECT COUNT(*) FROM big WHERE k = ?", (target,)).fetchone()
print(f"before index: {time.perf_counter() - start:.4f}s")

cur.execute("CREATE INDEX idx_big_k ON big(k)")

start = time.perf_counter()
cur.execute("SELECT COUNT(*) FROM big WHERE k = ?", (target,)).fetchone()
print(f"after  index: {time.perf_counter() - start:.6f}s")
```

**Expected output:** `after index` should be much faster than `before index`, and `EXPLAIN QUERY PLAN` should confirm that the index is used.

### Step 4: Inspect with EXPLAIN QUERY PLAN

```python
for row in cur.execute("EXPLAIN QUERY PLAN SELECT * FROM big WHERE k = 12345"):
    print(row)
# A line like (… USING INDEX idx_big_k …) confirms the index is used
```

### Step 5: Transactions and ACID

```python
conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER)")
cur.executemany(
    "INSERT INTO accounts (id, balance) VALUES (?, ?)",
    [(1, 1000), (2, 1000)],
)
conn.commit()

def transfer(src: int, dst: int, amount: int) -> None:
    """Atomic transfer between two accounts — both succeed or both fail."""
    try:
        cur.execute("BEGIN")
        cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, src))
        cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, dst))
        conn.commit()
    except Exception:
        conn.rollback()
        raise

transfer(1, 2, 300)
print(cur.execute("SELECT * FROM accounts").fetchall())
```

## Notable Points in This Code

- A single index can make the same query hundreds of times faster.
- N+1 queries can almost always be collapsed into one JOIN or IN clause.
- Transactions prevent partial failures and protect data integrity.
- `EXPLAIN` / `EXPLAIN QUERY PLAN` is an essential debugging tool in every DB.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| No index on a frequently filtered column | Full scan, slow responses | Add an index based on `EXPLAIN` |
| Indexing every column | Write performance and disk usage explode | Only index real query patterns |
| Missing transactions | Partial writes corrupt data | Wrap related changes in `BEGIN`/`COMMIT` |
| Letting an ORM lazy-load freely | N+1 queries | Use explicit loading like `select_related`/`joinedload` |
| Calling external APIs inside a transaction | Locks held for too long | Keep DB transactions short; do external calls outside |

## How This Is Used in Practice

- The persistent backbone of nearly every backend API.
- Splitting analytical OLAP DBs (ClickHouse, BigQuery) from transactional OLTP DBs.
- Index design and query tuning driving the latency SLO.
- Choosing isolation levels — Read Committed, Repeatable Read, Serializable.
- Migration strategies — zero-downtime schema changes, online DDL.

## How a Senior Engineer Thinks

When a senior engineer writes SQL, they always picture the execution plan. The SQL on screen and the steps the DB actually runs are not the same. They check `EXPLAIN` for index usage and refine the query while watching row counts and cost.

They also know the database is the most dangerous stateful piece of the system. A code deploy can be rolled back; a bad migration usually cannot. So they follow the rules: every schema change is backward-compatible, every transaction is short, and every operational SQL goes through `EXPLAIN` before it runs.

## Checklist

- [ ] I can explain the difference between a primary key and an index
- [ ] I check whether the column in my WHERE clause is indexed
- [ ] I know what belongs inside a transaction and what does not
- [ ] I can spot and fix an N+1 query
- [ ] I run `EXPLAIN` before firing SQL at production

## Practice Problems

1. Create a table with 2,000,000 rows and measure `SELECT` time before and after adding an index.

2. Compute per-user order totals in two ways: (a) N+1 queries and (b) a single JOIN + GROUP BY, and compare the times.

3. Use a transaction to verify that an account-transfer function leaves balances consistent even when an exception is raised in the middle.

## Wrap-Up and Next Steps

A database stores data permanently and keeps it consistent under concurrent access. SQL is the language to work with the data, indexes are the structures that make lookups fast, and transactions are the mechanism that guards integrity. The habit of looking at queries through `EXPLAIN` is what separates a good backend engineer from a guessing one.

The next article looks at how we keep all of these systems reliable and maintainable over time — software engineering.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Databases?**
  - The article treats Databases as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Databases?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Databases reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Science 101 (1/10): What Is Computer Science?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): Computation and Programs](./02-computation-and-programs.md)
- [Computer Science 101 (3/10): Data Representation](./03-data-representation.md)
- [Computer Science 101 (4/10): Algorithms and Complexity](./04-algorithms-and-complexity.md)
- [Computer Science 101 (5/10): Computer Architecture](./05-computer-architecture.md)
- [Computer Science 101 (6/10): Operating Systems](./06-operating-systems.md)
- [Computer Science 101 (7/10): Networks](./07-networks.md)
- **Databases (current)**
- Software Engineering (upcoming)
- From CS to AI and Data Science (upcoming)

<!-- toc:end -->

## References

- [PostgreSQL — Documentation](https://www.postgresql.org/docs/current/)
- [Use The Index, Luke! — SQL indexing guide](https://use-the-index-luke.com/)
- [SQLite EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html)
- [Designing Data-Intensive Applications — Martin Kleppmann](https://dataintensive.net/)

Tags: Computer Science, Databases, SQL, Indexes, Transactions, ACID

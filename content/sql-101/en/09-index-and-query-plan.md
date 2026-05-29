---
series: sql-101
episode: 9
title: "SQL 101 (9/10): Index and Query Plan"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - SQL
  - Index
  - QueryPlan
  - Performance
  - Postgres
seo_description: How B-tree indexes work, how to read EXPLAIN, why an index might be skipped, and the design principles for composite indexes.
last_reviewed: '2026-05-15'
---

# SQL 101 (9/10): Index and Query Plan

Two SQL statements can look almost identical and still differ by orders of magnitude in runtime. That gap usually has less to do with magic database behavior than with the path the planner chose to read the data.

If you cannot read that path, tuning stays stuck at guesswork. Indexes become cargo-cult fixes, and every slow query turns into trial and error instead of a repeatable investigation.

This is the 9th post in the SQL 101 series. Here we focus on how indexes, selectivity, and EXPLAIN fit together into a practical tuning workflow.


![sql 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/09/09-01-plan-selection-flow.en.png)
*sql 101 chapter 9 flow overview*
> Indexing is not about adding indexes everywhere; it's about using EXPLAIN to identify slow queries, understanding why they're slow, and adding indexes only where they help.

## Questions to Keep in Mind

- What is the simplest mental model for a B-tree index?
- How do EXPLAIN and EXPLAIN ANALYZE differ?
- Why can a database skip an index even when one exists?

## Why It Matters

Query tuning becomes more valuable as data grows because small predicate differences start turning into noticeable latency. Once tables move beyond toy size, you need to know not only what the SQL says, but also how the planner expects to execute it.

Indexes are powerful precisely because they are selective. They make some reads much faster while increasing storage and write cost. That means index work is not about adding more structures everywhere. It is about matching read patterns to the right access path and confirming the plan actually changes.

## Plan selection flow

Run EXPLAIN on a slow query to see if the planner chooses a sequential scan or an index scan. A sequential scan isn't always bad; sometimes it's actually faster than an index for small tables. Check the actual row counts and timing.

## Key Terms

- **B-tree index**: the most common *balanced-tree* index.
- **Seq scan**: read *every row* in order.
- **Index scan**: find rows fast through the index, then *fetch them*.
- **Selectivity**: how much a condition *narrows* the result.
- **Covering index**: the query is answered *from the index alone*.

## Before/After

**Before**: `WHERE LOWER(email) = 'x'` becomes a *Seq scan*.

**After**: `WHERE email = 'x'`, or a *function index* `CREATE INDEX ... ON users (LOWER(email))`.

## Hands-on: A Five-Step Tuning Loop

### Step 1 — EXPLAIN

```sql
EXPLAIN
SELECT * FROM users WHERE email = 'a@b.com';
```

**Expected output:**

```text
Index Scan using idx_users_email on users  (cost=0.28..8.30 rows=1 width=48)
  Index Cond: (email = 'a@b.com'::text)
```

### Step 2 — EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'a@b.com';
```

### Step 3 — Add an index

```sql
CREATE INDEX idx_users_email ON users (email);
```

### Step 4 — Composite index

```sql
CREATE INDEX idx_orders_user_date
ON orders (user_id, created_at DESC);
```

### Step 5 — Partial index

```sql
CREATE INDEX idx_users_active
ON users (id) WHERE deleted_at IS NULL;
```

## What to check first in an EXPLAIN plan

When you open an EXPLAIN plan, start with three questions before you touch any index definition.

1. **Which scan type did the planner choose?** If you expected an index and got a Seq Scan, the problem is often selectivity or predicate shape.
2. **How many rows did the planner estimate?** Large gaps between estimated rows and actual rows often point to stale statistics or skewed data.
3. **Where is the expensive step?** Sorts, hash aggregates, and repeated nested loops can dominate runtime even when the initial filter looks fine.

## Troubleshooting patterns that show up repeatedly

| Symptom | First thing to verify | Common fix |
| --- | --- | --- |
| Index exists but Seq Scan appears | Predicate selectivity and function/cast use | Rewrite the predicate or create the right index type |
| Composite index did not help | Whether the query starts from the leftmost prefix | Reorder columns to match filter and sort patterns |
| EXPLAIN looks fine but runtime is still high | Sorts, joins, and actual row counts in EXPLAIN ANALYZE | Tune the broader plan, not just the filter |

## What to Notice in This Code

- A composite index's *column order* matters — only the *leftmost prefix* is usable.
- *Partial indexes* are *small and fast* when the predicate is *clear*.
- `EXPLAIN ANALYZE` *actually runs* the query — be careful in production.

## Five Common Mistakes

1. **Function on the column** — index *not used*.
2. **Implicit type cast** — index *defeated*.
3. **`LIKE '%x'`** trailing wildcard — *no index*.
4. **Too many ORs** — planner picks a *Seq scan*.
5. **Indexing everything** — write costs *explode*.

## How This Shows Up in Production

Performance work is mostly *slow-query log → EXPLAIN → index or query change*, repeated. Composite index design considers both *predicates and ordering*. *Partial indexes* pair well with *soft deletes*.

## How a Senior Engineer Thinks

- *Read the plan, don't *guess*.*
- *Indexes are a *read/write trade-off*.*
- *Only the *leftmost prefix* of a composite index helps.*
- *Avoid functions and casts on indexed columns.*
- *Always keep the *slow-query log* on.*

## Index Type Comparison

| Type | Structure | Best For | Limitations |
| --- | --- | --- | --- |
| **B-tree** | Balanced tree | Equality, range, ORDER BY | Default; handles most workloads |
| **Hash** | Hash table | Equality only | No range queries, no sorting |
| **GIN** | Inverted index | Full-text search, JSONB, arrays | Slower writes, larger size |
| **GiST** | Generalized search tree | Geometric, range types, nearest-neighbor | Lossy for some types |

## CREATE INDEX + EXPLAIN Before/After

```sql
-- Before: no index on email
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'alice@example.com';
```

```text
Seq Scan on users  (cost=0.00..1250.00 rows=1 width=48) (actual time=8.123..12.456 rows=1 loops=1)
  Filter: (email = 'alice@example.com'::text)
  Rows Removed by Filter: 49999
Planning Time: 0.089 ms
Execution Time: 12.501 ms
```

```sql
-- Add index
CREATE INDEX idx_users_email ON users (email);

-- After: index used
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'alice@example.com';
```

```text
Index Scan using idx_users_email on users  (cost=0.28..8.30 rows=1 width=48) (actual time=0.045..0.047 rows=1 loops=1)
  Index Cond: (email = 'alice@example.com'::text)
Planning Time: 0.112 ms
Execution Time: 0.068 ms
```

Execution time dropped from ~12 ms to ~0.07 ms — a 170x improvement.

## When NOT to Index

### 1. Low selectivity (most rows match)

```sql
-- 90% of orders are 'completed' — index barely helps
CREATE INDEX idx_orders_status ON orders (status);
SELECT * FROM orders WHERE status = 'completed';
-- Planner chooses Seq Scan anyway
```

### 2. Very small tables

Tables with a few hundred rows are faster to scan sequentially than to maintain index lookups.

### 3. Write-heavy tables

Log tables with thousands of INSERTs per second pay heavy index maintenance costs. If reads are rare, minimize indexes.

### 4. Low cardinality columns

```sql
-- is_deleted has only true/false — minimal filtering benefit
CREATE INDEX idx_is_deleted ON users (is_deleted); -- low value
```

Consider a partial index instead, or skip indexing entirely.

## Reading EXPLAIN ANALYZE Output

```sql
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

```text
HashAggregate  (cost=2850.00..2950.00 rows=10000 width=40) (actual time=45.123..46.234 rows=10000 loops=1)
  Group Key: u.id, u.name
  ->  Hash Left Join  (cost=1200.00..2700.00 rows=50000 width=36) (actual time=12.345..38.567 rows=50000 loops=1)
        Hash Cond: (u.id = o.user_id)
        ->  Seq Scan on users u  (cost=0.00..450.00 rows=10000 width=32) (actual time=0.012..5.678 rows=10000 loops=1)
        ->  Hash  (cost=850.00..850.00 rows=50000 width=8) (actual time=12.123..12.123 rows=50000 loops=1)
              Buckets: 65536  Batches: 1  Memory Usage: 2048kB
              ->  Seq Scan on orders o  (cost=0.00..850.00 rows=50000 width=8) (actual time=0.034..6.789 rows=50000 loops=1)
Planning Time: 0.456 ms
Execution Time: 46.789 ms
```

### Reading order

1. Start from the most indented node (bottom-up)
2. `actual time`: real execution time (ms)
3. `rows`: compare estimated vs actual row counts
4. `loops`: how many times the node executed

### Key metrics to watch

- **Estimated vs actual rows diverge** → run `ANALYZE` to update statistics
- **High loops count** → nested loop may be inefficient
- **Long Seq Scan** → candidate for index
- **Hash Batches > 1** → insufficient `work_mem`

## Tuning Troubleshooting Table

| Symptom | Check First | Common Fix |
| --- | --- | --- |
| Seq Scan despite index existing | Selectivity; functions/casts on column | Rewrite condition or redesign index type |
| Composite index underperforming | Are leftmost columns in the WHERE? | Reorder columns to match query pattern |
| EXPLAIN looks good but actual time is high | Sort, join, actual row count | Review full plan, not just the filter node |

## Practical Anchor: Index Design Priority

Indexes consume write cost and storage. Design in this priority order:

1. High-traffic queries' `WHERE` + `ORDER BY` columns
2. JOIN keys
3. High-selectivity conditions
4. Everything else — add only after measurement

```sql
CREATE INDEX idx_orders_status_created_at
    ON orders (status, created_at DESC);
```

## Practical Anchor: Plan Comparison Metrics

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, customer_id, total_amount
FROM orders
WHERE status = 'paid'
  AND created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 100;
```

Compare before/after index addition:

- Actual execution time (`actual time`)
- Blocks read (`shared read blocks`)
- Rows scanned vs rows returned

If these do not improve, the index is not helping.

## Practical Anchor: Partial Index Strategy

When a status value covers a small fraction of rows, a partial index is both smaller and faster:

```sql
CREATE INDEX idx_orders_paid_recent
    ON orders (created_at DESC)
WHERE status = 'paid';
```

Only `status='paid'` queries benefit, but the index is a fraction of the full table's size.

## Practical Anchor: Tuning Record Template

Performance work is hard to reproduce from memory. Record each tuning session:

- Target query and call frequency
- EXPLAIN ANALYZE before change
- Index or query change applied
- EXPLAIN ANALYZE after change
- Write performance impact (INSERT/UPDATE TPS)

## Checklist

- [ ] I can tell Seq from Index scans in EXPLAIN.
- [ ] I know why composite column order matters.
- [ ] I can use partial indexes.
- [ ] I know when a function index is needed.

## Practice Problems

1. Use EXPLAIN to see why a search by `email` is a Seq scan.
2. Tune *recent orders* with a composite `(user_id, created_at DESC)`.
3. Explain why a partial index on `deleted_at IS NULL` *stays small*.

## Wrap-up and Next Steps

Tuning starts with *reading the plan*. Next: *practical analysis SQL*.

## Answering the Opening Questions

- **How should you think about B-tree indexes?**
  A B-tree index is a sorted lookup structure—like a book's index—that lets the engine jump directly to matching rows instead of scanning the entire table. It works best for equality and range conditions on the indexed columns.
- **What's the difference between EXPLAIN and EXPLAIN ANALYZE?**
  EXPLAIN shows the query plan the engine *would* use (estimated costs and row counts). EXPLAIN ANALYZE actually executes the query and shows real timing and row counts. Use EXPLAIN for quick checks; EXPLAIN ANALYZE for accurate performance diagnosis.
- **Why might a sequential scan be chosen even when an index exists?**
  When a large fraction of rows matches the filter, reading the entire table sequentially is cheaper than bouncing between index and heap. The optimizer estimates selectivity—if the index would touch most pages anyway, Seq Scan wins on I/O cost.

<!-- toc:begin -->
## In this series

- [SQL 101 (1/10): What Is SQL?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT Basics](./02-select-basics.md)
- [SQL 101 (3/10): WHERE and Conditions](./03-where-and-conditions.md)
- [SQL 101 (4/10): JOIN](./04-join.md)
- [SQL 101 (5/10): GROUP BY and Aggregates](./05-group-by-and-aggregate.md)
- [SQL 101 (6/10): Subquery](./06-subquery.md)
- [SQL 101 (7/10): Window Function](./07-window-function.md)
- [SQL 101 (8/10): INSERT, UPDATE, DELETE](./08-insert-update-delete.md)
- **Index and Query Plan (current)**
- Practical Analysis SQL (upcoming)

<!-- toc:end -->

## References

- [PostgreSQL — Indexes](https://www.postgresql.org/docs/current/indexes.html)
- [PostgreSQL — EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html)
- [Use The Index, Luke](https://use-the-index-luke.com/)
- [PostgreSQL — Partial Indexes](https://www.postgresql.org/docs/current/indexes-partial.html)
- [PostgreSQL — Planner Statistics](https://www.postgresql.org/docs/current/planner-stats.html)

Tags: SQL, Database, Postgres, Analytics

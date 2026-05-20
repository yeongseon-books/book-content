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

This is post 9 in the SQL 101 series. Here we focus on how indexes, selectivity, and EXPLAIN fit together into a practical tuning workflow.

## Questions to Keep in Mind

- What is the simplest mental model for a B-tree index?
- How do EXPLAIN and EXPLAIN ANALYZE differ?
- Why can a database skip an index even when one exists?

## Big Picture

![sql 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/09/09-01-plan-selection-flow.en.png)

*sql 101 chapter 9 flow overview*

An index lets the database find rows quickly by a specific column value, but maintaining indexes slows down writes. EXPLAIN shows the execution plan, revealing whether your index is actually being used.

> Indexing is not about adding indexes everywhere; it's about using EXPLAIN to identify slow queries, understanding why they're slow, and adding indexes only where they help.

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

- **What is the simplest mental model for a B-tree index?**
  - The article treats Index and Query Plan as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How do EXPLAIN and EXPLAIN ANALYZE differ?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why can a database skip an index even when one exists?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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

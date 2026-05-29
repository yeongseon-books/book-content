---
series: sql-101
episode: 8
title: "SQL 101 (8/10): INSERT, UPDATE, DELETE"
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
  - DML
  - Transaction
  - Database
  - Postgres
seo_description: Safely insert, change, and remove data — transactions, UPSERT, RETURNING, and the habit of never forgetting WHERE.
last_reviewed: '2026-05-15'
---

# SQL 101 (8/10): INSERT, UPDATE, DELETE

So far the series has mostly focused on reading data. Writing data is different. One misplaced condition can update or delete far more rows than intended, and by the time you notice, the mistake may already be live in production.

That is why data-changing SQL is less about syntax and more about safety procedure. Transactions, preview queries, RETURNING, and rollback habits matter as much as the actual INSERT, UPDATE, or DELETE statement.

This is the 8th post in the SQL 101 series. Here we focus on how to change rows safely instead of treating DML as just another clause to memorize.


![sql 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/08/08-01-safe-data-change-flow.en.png)
*sql 101 chapter 8 flow overview*
> Data-changing operations demand more care than reads. A single WHERE typo in DELETE can erase months of data. Always test your filter conditions on a SELECT first.

## Questions to Keep in Mind

- What are the basic shapes of INSERT, UPDATE, and DELETE?
- Why is a transaction the default safety net for data changes?
- Why is RETURNING so useful during verification?

## Why It Matters

Production data is harder to repair than to damage. A missing WHERE clause or a multi-step change executed without a transaction can leave the system in a half-updated state that is difficult to reason about later. That is why strong teams treat DML as operational work, not just query writing.

Transactions and RETURNING help turn risky changes into auditable ones. They let you see what changed before you commit, and they make rollback part of the default workflow instead of an afterthought.

## Safe data-change flow

Before you INSERT, check PRIMARY KEY and NOT NULL constraints. Before you UPDATE or DELETE, always write a SELECT with the same WHERE condition first, and verify you're changing the right rows. Use transactions so you can ROLLBACK if something goes wrong.

## Key Terms

- **DML**: Data Manipulation Language — INSERT, UPDATE, DELETE.
- **Transaction**: a group of operations that succeed or fail *atomically*.
- **UPSERT**: update if present, insert if absent.
- **RETURNING**: get the changed rows back.
- **Constraint**: NOT NULL, UNIQUE, FK — DB-level rules.

## Before/After

**Before**: `DELETE FROM users;` runs by accident — *unrecoverable*.

**After**: `BEGIN; DELETE FROM users WHERE id = 42 RETURNING *;` then `COMMIT` only after checking the output.

## Hands-on: Five Safe DML Patterns

### Step 1 — INSERT

```sql
INSERT INTO users (id, name, signup_at)
VALUES (4, 'Margaret', '2026-04-10');
```

### Step 2 — UPDATE (WHERE required)

```sql
UPDATE users SET name = 'Margaret Hamilton' WHERE id = 4;
```

### Step 3 — DELETE (inside a transaction)

```sql
BEGIN;
DELETE FROM users WHERE id = 4 RETURNING *;
-- review the output, then
COMMIT;
```

**Expected output:**

| id | name | signup_at |
| --- | --- | --- |
| 4 | Margaret Hamilton | 2026-04-10 |

### Step 4 — UPSERT

```sql
INSERT INTO users (id, name, signup_at)
VALUES (4, 'Margaret', '2026-04-10')
ON CONFLICT (id)
DO UPDATE SET name = EXCLUDED.name;
```

### Step 5 — Bulk INSERT

```sql
INSERT INTO users (id, name, signup_at) VALUES
    (5, 'Edsger', '2026-04-11'),
    (6, 'Donald', '2026-04-12'),
    (7, 'Barbara', '2026-04-13');
```

## What to Notice in This Code

- *Every UPDATE/DELETE has a WHERE.* No exceptions.
- Wrap changes in transactions and verify with RETURNING.
- In UPSERT, `EXCLUDED` refers to the *new values* the INSERT was attempting.

## Five Common Mistakes

1. **UPDATE/DELETE without WHERE.** Whole table affected.
2. **Multi-step changes *without* a transaction.** A failure mid-way leaves *half-state*.
3. **Changing rows from *guesswork*.** Always verify with RETURNING.
4. **UPSERT without a unique constraint.** ON CONFLICT *won't fire*.
5. **Bulk INSERT done as N single rows.** Slow and costly.

## How This Shows Up in Production

Production changes go through *PR review* and *migration tools*. Ad-hoc changes always run *inside a transaction* and use RETURNING to *verify*. *Backups and PITR* are the *last line of defense*.

## How a Senior Engineer Thinks

- *Treat DML without WHERE as a *syntax error*.*
- *Changes mean *transaction + RETURNING*.*
- *UPSERT only works *with a constraint*.*
- *Do bulk inserts *in one shot*.*
- *Production DML lives in *migrations*.*

## Normalization Stages

DML safety depends heavily on table design. Normalization reduces redundancy and update anomalies.

| Stage | Requirement | Violation Example | Fix |
| --- | --- | --- | --- |
| 1NF | Every column holds atomic values | `tags` column stores `"python,sql"` | Separate `post_tags` table |
| 2NF | Full dependency on primary key | `(user_id, order_id)` PK includes `user_name` | Move to `users` table |
| 3NF | No transitive dependencies | `orders` stores `user_country` (duplicates `users.country`) | Move to `users` table |
| BCNF | Every determinant is a candidate key | `(instructor, course)` with `instructor → department` | Separate `instructors` table |

Higher normal forms reduce duplication and modification anomalies, but add joins. In practice 3NF is the typical target; denormalize only when measured read performance demands it.

## Denormalization → Normalization Example

### Denormalized table (violates 1NF)

```sql
CREATE TABLE posts_denorm (
    id INT PRIMARY KEY,
    title TEXT,
    tags TEXT  -- "python,sql,database"
);

INSERT INTO posts_denorm VALUES
(1, 'SQL Basics', 'python,sql'),
(2, 'Data Analysis', 'sql,database');
```

Finding posts by tag requires `LIKE '%sql%'` — no index support, false positives possible.

### After normalization

```sql
CREATE TABLE posts (
    id INT PRIMARY KEY,
    title TEXT
);

CREATE TABLE tags (
    id INT PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE post_tags (
    post_id INT REFERENCES posts(id),
    tag_id INT REFERENCES tags(id),
    PRIMARY KEY (post_id, tag_id)
);

-- Query: posts with 'sql' tag
SELECT p.id, p.title
FROM posts p
JOIN post_tags pt ON p.id = pt.post_id
JOIN tags t ON t.id = pt.tag_id
WHERE t.name = 'sql';
```

Each tag is now a separate row — indexable, exact-match searchable, and safe for INSERT/UPDATE.

## When Denormalization Makes Sense

- **Read frequency ≫ write frequency**: dashboards, reports
- **Repeated complex joins**: 3-4 table joins on every request
- **Pre-aggregated metrics**: total spend per user, sales per country

### Denormalization with trigger-based sync

```sql
-- Add a denormalized column
ALTER TABLE users ADD COLUMN order_count INT DEFAULT 0;

-- Keep it in sync via trigger
CREATE OR REPLACE FUNCTION update_user_order_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users SET order_count = (
        SELECT COUNT(*) FROM orders WHERE user_id = NEW.user_id
    ) WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_count
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION update_user_order_count();
```

Denormalization speeds reads but adds sync cost on every write. Alternatives to consider first: Materialized Views, cache layers (Redis), or composite indexes.

## Pre-Change Checklist (6 Steps)

Before any significant UPDATE or DELETE, follow this routine:

1. **Count affected rows**: `SELECT COUNT(*) FROM ... WHERE ...`
2. **Review target data**: `SELECT * FROM ... WHERE ... LIMIT 20`
3. **Begin transaction**: `BEGIN;`
4. **Execute with RETURNING**: `UPDATE ... RETURNING *`
5. **Verify result**: confirm returned rows match expectations
6. **Commit or rollback**: `COMMIT` if correct, `ROLLBACK` if not

```sql
-- Example: cancel old pending orders
-- 1. Count
SELECT COUNT(*) FROM orders WHERE status = 'pending' AND created_at < '2025-01-01';

-- 2. Review
SELECT id, user_id, total, status FROM orders
WHERE status = 'pending' AND created_at < '2025-01-01' LIMIT 20;

-- 3. Begin
BEGIN;

-- 4. Execute
UPDATE orders
SET status = 'cancelled'
WHERE status = 'pending' AND created_at < '2025-01-01'
RETURNING id, user_id, status;

-- 5-6. Verify then commit/rollback
COMMIT;
-- ROLLBACK;
```

## Practical Anchor: Batch Deletes to Reduce Lock Contention

Deleting millions of rows at once holds locks and bloats WAL. Delete in small batches instead:

```sql
DELETE FROM event_logs
WHERE log_id IN (
    SELECT log_id
    FROM event_logs
    WHERE created_at < CURRENT_DATE - INTERVAL '180 days'
    ORDER BY log_id
    LIMIT 5000
);
```

Repeat in a loop until zero rows affected. This coexists with live traffic.

## Practical Anchor: Preventing Update Scope Contamination

Join-based updates are convenient but can silently affect more rows than intended:

```sql
UPDATE orders o
SET risk_grade = r.risk_grade
FROM risk_snapshot r
WHERE o.customer_id = r.customer_id
  AND r.snapshot_date = CURRENT_DATE;
```

Verify key uniqueness in `risk_snapshot` first. If keys are duplicated, the same order row matches multiple snapshot rows — producing non-deterministic results.

## Practical Anchor: Before/After Comparison Query

The most operationally valuable habit: record the same query's output before and after a change.

```sql
SELECT status, COUNT(*)
FROM orders
GROUP BY status
ORDER BY status;
```

Paste both results into your ticket or PR. This accelerates incident response and builds review trust.

## Checklist

- [ ] I always check for WHERE in DML.
- [ ] I can use BEGIN/COMMIT/ROLLBACK.
- [ ] I can write UPSERT.
- [ ] I know what RETURNING does.

## Practice Problems

1. Change the name of *id = 5* inside a transaction and verify with RETURNING.
2. Before deleting *users with no orders*, SELECT them to confirm.
3. Write one UPSERT that *creates a new user or updates an existing one*.

## Wrap-up and Next Steps

DML is the craft of making the *irreversible* feel safe. Next: *Index and query plan*.

## Answering the Opening Questions

- **What are the basic forms of INSERT, UPDATE, and DELETE?**
  INSERT adds rows (verify NOT NULL constraints and PRIMARY KEY uniqueness). UPDATE modifies existing rows matching a WHERE condition. DELETE removes rows matching a WHERE condition. All three are DML operations that modify table state.
- **Why is a transaction the basic safety net for data changes?**
  Wrapping changes in `BEGIN`/`COMMIT` (or `ROLLBACK`) ensures atomicity—either all changes apply or none do. Without transactions, a failed UPDATE can leave data in a half-modified state that's expensive to recover from manually.
- **Why is RETURNING especially useful in practice?**
  `RETURNING` lets you see the affected rows in the same statement—no need for a follow-up SELECT. This eliminates race conditions (another session could modify the row between your UPDATE and SELECT) and reduces round trips.

<!-- toc:begin -->
## In this series

- [SQL 101 (1/10): What Is SQL?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT Basics](./02-select-basics.md)
- [SQL 101 (3/10): WHERE and Conditions](./03-where-and-conditions.md)
- [SQL 101 (4/10): JOIN](./04-join.md)
- [SQL 101 (5/10): GROUP BY and Aggregates](./05-group-by-and-aggregate.md)
- [SQL 101 (6/10): Subquery](./06-subquery.md)
- [SQL 101 (7/10): Window Function](./07-window-function.md)
- **INSERT, UPDATE, DELETE (current)**
- Index and Query Plan (upcoming)
- Practical Analysis SQL (upcoming)

<!-- toc:end -->

## References

- [PostgreSQL — INSERT](https://www.postgresql.org/docs/current/sql-insert.html)
- [PostgreSQL — UPDATE](https://www.postgresql.org/docs/current/sql-update.html)
- [PostgreSQL — DELETE](https://www.postgresql.org/docs/current/sql-delete.html)
- [PostgreSQL — Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)
- [PostgreSQL — Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)

Tags: SQL, Database, Postgres, Analytics

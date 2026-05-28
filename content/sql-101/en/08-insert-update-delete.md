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

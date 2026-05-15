---
series: sql-101
episode: 6
title: Subquery
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
  - Subquery
  - CTE
  - Database
  - Query
seo_description: Scalar subqueries, IN, EXISTS, inline views, and CTEs — the toolkit for breaking complex SQL into layers your team can read.
last_reviewed: '2026-05-15'
---

# Subquery

Real SQL rarely stays flat. One question turns into a smaller question about big spenders, another about recent activity, and another about whether a user has done something at least once. If all of that logic gets packed into one layer, the statement becomes technically valid but hard for a team to review.

Subqueries and CTEs are the tools that let you split that complexity into readable steps. They matter less because they are advanced syntax and more because they let you express a multi-stage thought process without losing control of the result.

This is post 6 in the SQL 101 series. Here we focus on breaking layered questions into SQL that another engineer can still read from top to bottom.

## Questions this chapter answers

- When is a subquery enough, and when is a CTE the better fit?
- What is the difference between a scalar subquery and an inline view?
- How do IN and EXISTS differ in intent and behavior?
- Why do correlated subqueries become expensive so easily?
- How should you name intermediate layers in longer SQL files?

> A subquery is a smaller question nested inside a larger one. If the smaller question is unclear, the final answer is usually untrustworthy too.

## Why It Matters

Analytical queries are usually layered. You compute a cohort start date, attach later activity, aggregate it, and maybe join the result back to user attributes. If that logic is crammed into one long statement, it becomes difficult to debug or modify without breaking something unrelated.

Readable layers are operationally valuable. Once each step has a name, you can test intermediate results, reason about row counts, and explain the logic during review instead of staring at one oversized FROM clause.

## Subquery layering flow

![Subquery layering flow](../../../assets/sql-101/06/06-01-subquery-layering-flow.en.png)
## Key Terms

- **Scalar subquery**: returns a *single value*.
- **Inline view**: `FROM (SELECT ...) AS t`.
- **CTE**: `WITH name AS (...)` — a *named* subquery.
- **Correlated subquery**: references the *outer row*.
- **EXISTS**: tests *existence only*.

## Before/After

**Before**: a 200-line *blob* — no idea where to start reading.

**After**: four CTEs naming each step — anyone can *read and modify* it.

## Hands-on: Five Subquery Patterns

### Step 1 — Scalar

```sql
SELECT name,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_count
FROM users u;
```

### Step 2 — IN

```sql
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE total > 1000);
```

### Step 3 — EXISTS

```sql
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

### Step 4 — Inline view

```sql
SELECT t.country, t.users
FROM (
    SELECT country, COUNT(*) AS users
    FROM users GROUP BY country
) AS t
WHERE t.users > 100;
```

### Step 5 — CTE

```sql
WITH big_orders AS (
    SELECT user_id, SUM(total) AS spend
    FROM orders GROUP BY user_id
    HAVING SUM(total) > 1000
)
SELECT u.name, b.spend
FROM big_orders b
JOIN users u ON u.id = b.user_id;
```

**Expected output:**

| name | spend |
| --- | --- |
| Ada | 1450 |
| Grace | 2100 |

## What to Notice in This Code

- *EXISTS* is *NULL-safe* and can *short-circuit*, unlike `IN`.
- An inline view and a CTE mean the same thing, but the *CTE reads better*.
- A correlated subquery may run *once per row* — *expensive*.

## Five Common Mistakes

1. **`NOT IN (subquery)`** with NULLs in the subquery returns *no rows*.
2. **Correlated subqueries causing *N+1*.** Switch to *join + aggregate*.
3. **CTEs that are *too deep*.** Past five steps, *split the file*.
4. **Inline view without an alias** — some DBs *error out*.
5. **`SELECT *` inside EXISTS.** Use `SELECT 1` to communicate intent.

## How This Shows Up in Production

ETL pipelines are mostly CTE-based *named transformations*. *Cohort analysis*, *funnels*, and *retention* fit cleanly into *three to five CTEs*.

## How a Senior Engineer Thinks

- *Layer to manage complexity.*
- *Prefer NOT EXISTS to NOT IN.*
- *Name CTEs by *what they mean*, not what they do.*
- *For correlated subqueries, ask if a *join* would work.*
- *Use EXISTS for cheap *existence checks*.*

## Checklist

- [ ] I know scalar vs inline vs CTE.
- [ ] I know EXISTS vs IN.
- [ ] I know the cost of correlated subqueries.
- [ ] I can split a query into CTEs.

## Practice Problems

1. List users *with at least one order* using EXISTS.
2. Compute *users per country* with both an inline view and a CTE.
3. Find each *big spender's last order date* using two CTEs.

## Wrap-up and Next Steps

Subqueries split a question into pieces. Next up: *Window functions*.

<!-- toc:begin -->
## In this series

- [What Is SQL?](./01-what-is-sql.md)
- [SELECT Basics](./02-select-basics.md)
- [WHERE and Conditions](./03-where-and-conditions.md)
- [JOIN](./04-join.md)
- [GROUP BY and Aggregates](./05-group-by-and-aggregate.md)
- **Subquery (current)**
- Window Function (upcoming)
- INSERT, UPDATE, DELETE (upcoming)
- Index and Query Plan (upcoming)
- Practical Analysis SQL (upcoming)

<!-- toc:end -->

## References

- [PostgreSQL — Subqueries](https://www.postgresql.org/docs/current/functions-subquery.html)
- [PostgreSQL — WITH Queries (CTE)](https://www.postgresql.org/docs/current/queries-with.html)
- [Mode — Subqueries](https://mode.com/sql-tutorial/sql-sub-queries/)
- [Use The Index, Luke — IN vs EXISTS](https://use-the-index-luke.com/sql/where-clause/null/not-in)
- [PostgreSQL — FROM Clause](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-FROM)

Tags: SQL, Database, Postgres, Analytics

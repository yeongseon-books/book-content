---
series: sql-101
episode: 6
title: "SQL 101 (6/10): Subquery"
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

# SQL 101 (6/10): Subquery

Real SQL rarely stays flat. One question turns into a smaller question about big spenders, another about recent activity, and another about whether a user has done something at least once. If all of that logic gets packed into one layer, the statement becomes technically valid but hard for a team to review.

Subqueries and CTEs are the tools that let you split that complexity into readable steps. They matter less because they are advanced syntax and more because they let you express a multi-stage thought process without losing control of the result.

This is the 6th post in the SQL 101 series. Here we focus on breaking layered questions into SQL that another engineer can still read from top to bottom.


![sql 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/06/06-01-subquery-layering-flow.en.png)
*sql 101 chapter 6 flow overview*
> Subqueries and CTEs don't add new capabilities; they add clarity. They let you name each step, test each piece separately, and build the final query without nesting everything into one unreadable line.

## Questions to Keep in Mind

- When is a subquery enough, and when is a CTE the better fit?
- What is the difference between a scalar subquery and an inline view?
- How do IN and EXISTS differ in intent and behavior?

## Why It Matters

Analytical queries are usually layered. You compute a cohort start date, attach later activity, aggregate it, and maybe join the result back to user attributes. If that logic is crammed into one long statement, it becomes difficult to debug or modify without breaking something unrelated.

Readable layers are operationally valuable. Once each step has a name, you can test intermediate results, reason about row counts, and explain the logic during review instead of staring at one oversized FROM clause.

## Subquery layering flow

A subquery is a query inside a query, often in the FROM or WHERE clause. A CTE is the same idea but uses WITH to name it first, then the main query uses that name. CTEs are usually more readable.

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

## VIEW vs CTE vs Subquery

| Approach | Persistence | Reusability | Optimization | Best for |
| --- | --- | --- | --- | --- |
| **Subquery (inline view)** | Query-scoped | Single use | Inlined by planner | Simple one-off filters |
| **CTE** | Query-scoped | Multiple references in same query | Inlined (PG 12+) or materialized | Multi-step logic, debugging |
| **VIEW** | Schema object | Any query | Re-planned each call | Shared business definitions |
| **Materialized View** | Schema object + stored data | Any query | Pre-computed, refreshed on demand | Expensive aggregations read often |

### WITH RECURSIVE Example (Org Tree)

```sql
WITH RECURSIVE org_tree AS (
    -- anchor: top-level managers
    SELECT id, name, manager_id, 1 AS depth
    FROM employees
    WHERE manager_id IS NULL
    UNION ALL
    -- recursive: each level down
    SELECT e.id, e.name, e.manager_id, t.depth + 1
    FROM employees e
    JOIN org_tree t ON t.id = e.manager_id
)
SELECT * FROM org_tree ORDER BY depth, name;
```

Recursive CTEs solve hierarchical problems (org charts, category trees, graph traversal) that flat SQL cannot express.

## IN vs EXISTS: Performance Comparison

```sql
-- IN: materializes the subquery result, then checks membership
SELECT c.customer_id
FROM customers c
WHERE c.customer_id IN (
    SELECT o.customer_id
    FROM orders o
    WHERE o.status = 'paid'
);

-- EXISTS: stops at first match (short-circuit)
SELECT c.customer_id
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
      AND o.status = 'paid'
);
```

Selection criteria:

- Subquery result is small with no NULLs → `IN`
- Outer table is large and subquery can match quickly → `EXISTS`
- NULL safety matters → `EXISTS` (safer)

In practice, write both and compare with `EXPLAIN ANALYZE`.

## CTE Performance Considerations

CTEs improve readability, but in PostgreSQL 11 and below they are always materialized, limiting optimization. PostgreSQL 12+ inlines most CTEs, but you can control the behavior explicitly:

```sql
-- Force materialization (useful when CTE is referenced multiple times)
WITH big_orders AS MATERIALIZED (
    SELECT user_id, SUM(total) AS spend
    FROM orders GROUP BY user_id
    HAVING SUM(total) > 1000
)
SELECT * FROM big_orders;

-- Force inlining (let planner push predicates into CTE)
WITH big_orders AS NOT MATERIALIZED (
    SELECT user_id, SUM(total) AS spend
    FROM orders GROUP BY user_id
    HAVING SUM(total) > 1000
)
SELECT * FROM big_orders;
```

Default behavior is usually correct. Use `MATERIALIZED` explicitly when a CTE is referenced multiple times or when performance differs from expectations.

## Subquery Anti-Patterns

### Anti-pattern 1: Repeated correlated subqueries in SELECT

```sql
-- Bad: scans orders twice
SELECT id, name,
    (SELECT COUNT(*) FROM orders WHERE user_id = u.id) AS order_count,
    (SELECT SUM(total) FROM orders WHERE user_id = u.id) AS total_spend
FROM users u;
```

Better: aggregate once with a join.

```sql
-- Good: single scan
SELECT u.id, u.name,
    COUNT(o.id) AS order_count,
    SUM(o.total) AS total_spend
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

### Anti-pattern 2: Excessive nesting

```sql
-- Hard to read
SELECT * FROM (
    SELECT * FROM (
        SELECT * FROM orders WHERE total > 100
    ) AS t1 WHERE user_id > 10
) AS t2 WHERE created_at > '2025-01-01';
```

Flatten with a CTE or combine conditions:

```sql
-- Clear
WITH filtered_orders AS (
    SELECT * FROM orders
    WHERE total > 100
      AND user_id > 10
      AND created_at > '2025-01-01'
)
SELECT * FROM filtered_orders;
```

## Practical Anchor: Selection Criteria for Subquery vs CTE

Both produce the same result, but choose based on reuse scope and review difficulty:

- One-time use with short meaning → inline subquery
- Referenced at multiple stages → CTE
- Needs step-by-step debugging → CTE with descriptive names

```sql
WITH paid_orders AS (
    SELECT *
    FROM orders
    WHERE status = 'paid'
),
customer_revenue AS (
    SELECT customer_id, SUM(total_amount) AS revenue
    FROM paid_orders
    GROUP BY customer_id
)
SELECT *
FROM customer_revenue
WHERE revenue >= 100000;
```

## Practical Anchor: Replacing a Correlated Subquery

Correlated subqueries are readable but may execute once per outer row.

```sql
-- Correlated subquery (expensive at scale)
SELECT o.order_id,
       (SELECT SUM(oi.quantity * oi.unit_price)
        FROM order_items oi
        WHERE oi.order_id = o.order_id) AS amount
FROM orders o;
```

Pre-aggregate and JOIN instead:

```sql
WITH item_sum AS (
    SELECT order_id, SUM(quantity * unit_price) AS amount
    FROM order_items
    GROUP BY order_id
)
SELECT o.order_id, i.amount
FROM orders o
LEFT JOIN item_sum i ON i.order_id = o.order_id;
```

## Practical Anchor: CTE Debugging Routine

For complex analytical SQL, do not only look at the final result. Run each CTE independently and verify row counts. Check whether primary-key uniqueness holds at each stage — catching uniqueness violations early prevents downstream JOIN errors.


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

## Answering the Opening Questions

- **When should you use a subquery, and when is a CTE better?**
  Subqueries nest a query inside another. CTEs (`WITH` clause) define named result sets upfront. CTEs win for readability when the same intermediate result is referenced multiple times or when debugging step-by-step. Subqueries are fine for simple, one-off filters.
- **What's the difference between a scalar subquery and an inline view?**
  A scalar subquery returns exactly one value and can appear in SELECT or WHERE. An inline view (subquery in FROM) returns a result set treated as a temporary table. Using the wrong type causes runtime errors—scalar subqueries fail if they return more than one row.
- **In what situations do IN and EXISTS differ?**
  `IN` materializes the subquery result and checks membership. `EXISTS` short-circuits—it stops as soon as one matching row is found. EXISTS tends to outperform IN when the subquery returns many rows but the outer table is small, or when the subquery is correlated.

<!-- toc:begin -->
## In this series

- [SQL 101 (1/10): What Is SQL?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT Basics](./02-select-basics.md)
- [SQL 101 (3/10): WHERE and Conditions](./03-where-and-conditions.md)
- [SQL 101 (4/10): JOIN](./04-join.md)
- [SQL 101 (5/10): GROUP BY and Aggregates](./05-group-by-and-aggregate.md)
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

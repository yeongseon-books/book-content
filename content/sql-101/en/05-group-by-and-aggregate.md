---
series: sql-101
episode: 5
title: "SQL 101 (5/10): GROUP BY and Aggregates"
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
  - GroupBy
  - Aggregate
  - Database
  - Analytics
seo_description: GROUP BY explained — aggregate functions, HAVING vs WHERE, multi-column grouping, and how NULL groups work in practice.
last_reviewed: '2026-05-15'
---

# SQL 101 (5/10): GROUP BY and Aggregates

As soon as someone asks for daily revenue, users per country, or the average order size, you stop reading rows one by one and start compressing them into numbers. That compression is where GROUP BY and aggregate functions become the core of analytical SQL.

The tricky part is not writing SUM or COUNT. It is deciding what a group actually means, what detail disappears when rows collapse, and whether the resulting number still matches the business question you thought you were answering.

This is post 5 in the SQL 101 series. Here we focus on how aggregation turns many rows into interpretable metrics.

## Questions to Keep in Mind

- When does GROUP BY run, and what exactly gets grouped?
- How do SUM, COUNT, and AVG differ in practice?
- What is the real split between WHERE and HAVING?

## Big Picture

![sql 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/05/05-01-aggregation-flow.en.png)

*sql 101 chapter 5 flow overview*

GROUP BY divides rows into groups and aggregate functions (SUM, COUNT, AVG) summarize each group down to a single row.

> GROUP BY's value is not in the aggregate function names, but in deciding the right grouping level so that your summary answers the actual business question.

## Why It Matters

Most dashboard metrics are grouped metrics. Daily active users, revenue by country, average rating per product, and orders per customer all depend on taking raw rows and reducing them to one line per business category. That makes aggregation one of the most reusable shapes in SQL.

It is also one of the easiest places to create plausible but incorrect numbers. A missing grouping key, a join that multiplies rows, or a misunderstood NULL rule can produce a chart that looks clean while hiding a logic bug underneath.

## Aggregation flow

Think of GROUP BY as a pivot: many input rows become fewer output rows. Each row in the output represents one group. You can only SELECT the grouping columns and aggregate functions; other columns have no single value per group.

## Key Terms

- **Aggregate function**: `SUM, COUNT, AVG, MIN, MAX`, etc.
- **Grouping key**: the column rows are bucketed by.
- **HAVING**: a condition on *aggregate output*.
- **NULL group**: NULL is *its own group*.
- **Distinct count**: `COUNT(DISTINCT x)` — count after deduplication.

## Before/After

**Before**: `SELECT user_id, SUM(total) FROM orders;` — *error*. `user_id` must be grouped.

**After**: `SELECT user_id, SUM(total) FROM orders GROUP BY user_id;` — *correct aggregate*.

## Hands-on: Five Aggregations

### Step 1 — Simple total

```sql
SELECT COUNT(*) AS total_users FROM users;
```

### Step 2 — Per category

```sql
SELECT country, COUNT(*) AS users
FROM users
GROUP BY country;
```

**Expected output:**

| country | users |
| --- | --- |
| KR | 2 |
| US | 1 |

### Step 3 — Multiple keys

```sql
SELECT country, signup_at::date AS day, COUNT(*) AS users
FROM users
GROUP BY country, day;
```

### Step 4 — HAVING

```sql
SELECT country, COUNT(*) AS users
FROM users
GROUP BY country
HAVING COUNT(*) > 100;
```

### Step 5 — DISTINCT count

```sql
SELECT country, COUNT(DISTINCT user_id) AS active_users
FROM events
GROUP BY country;
```

## What to Notice in This Code

- WHERE runs *before* aggregation, HAVING *after*.
- `COUNT(*)` includes NULL rows, `COUNT(col)` does not.
- `COUNT(DISTINCT)` is *expensive*. On big tables, consider *approximate functions*.

## Five Common Mistakes

1. **Forgetting a GROUP BY column.** Every *non-aggregated* column in SELECT must be grouped.
2. **Aggregate condition in WHERE.** `WHERE COUNT(*) > 1` is an *error*. Use HAVING.
3. **Treating `AVG` as if NULL counts as 0.** It is *excluded*.
4. **Sums *inflated* after a join.** Cardinality is 1:N.
5. **Grouping by *too many columns*.** Each group is one row, so the result *means nothing*.

## How This Shows Up in Production

*Daily Active Users (DAU)*, *revenue by country*, *average rating per product* — the building blocks of analytics. Heavy aggregations move into *materialized views*.

## How a Senior Engineer Thinks

- *Separate *pre-* and *post-aggregate* conditions in your head.*
- *Assume NULL can *skew* metrics.*
- *Watch the *cost* of DISTINCT COUNT.*
- *For join + aggregate, *aggregate the small side first*.*
- *Group keys must be *interpretable*.*

## Checklist

- [ ] I know the difference between WHERE and HAVING.
- [ ] I know `COUNT(*)` vs `COUNT(col)`.
- [ ] I can group by multiple columns.
- [ ] I know what a NULL group means.

## Practice Problems

1. Compute *users per country* and *active users per country* together.
2. Filter to users with *at least 100 orders*.
3. Compute *daily DAU* from an events table.

## Wrap-up and Next Steps

GROUP BY makes meaning by *shrinking rows*. Next: *Subquery*.

## Answering the Opening Questions

- **When does GROUP BY run, and what exactly gets grouped?**
  - The article treats GROUP BY and Aggregates as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How do SUM, COUNT, and AVG differ in practice?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What is the real split between WHERE and HAVING?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [SQL 101 (1/10): What Is SQL?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT Basics](./02-select-basics.md)
- [SQL 101 (3/10): WHERE and Conditions](./03-where-and-conditions.md)
- [SQL 101 (4/10): JOIN](./04-join.md)
- **GROUP BY and Aggregates (current)**
- Subquery (upcoming)
- Window Function (upcoming)
- INSERT, UPDATE, DELETE (upcoming)
- Index and Query Plan (upcoming)
- Practical Analysis SQL (upcoming)

<!-- toc:end -->

## References

- [PostgreSQL — GROUP BY](https://www.postgresql.org/docs/current/tutorial-agg.html)
- [PostgreSQL — Aggregate Functions](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [Mode — GROUP BY](https://mode.com/sql-tutorial/sql-group-by/)
- [SQLBolt — Aggregates](https://sqlbolt.com/lesson/select_queries_with_aggregates)
- [PostgreSQL — GROUPING SETS, CUBE, and ROLLUP](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUPING-SETS)

Tags: SQL, Database, Postgres, Analytics

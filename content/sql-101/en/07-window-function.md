---
series: sql-101
episode: 7
title: "SQL 101 (7/10): Window Function"
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
  - WindowFunction
  - Analytics
  - Database
  - Query
seo_description: ROW_NUMBER, RANK, LAG/LEAD, running totals — SQL tools for per-group computations without losing the original rows.
last_reviewed: '2026-05-15'
---

# SQL 101 (7/10): Window Function

After GROUP BY, many readers hit the same wall: they can compute one total per group, but they still want to keep the original rows visible. Rankings, previous-value comparisons, running totals, and moving averages all come from that need.

Window functions solve exactly that problem. They let you add group-aware calculations to each row without collapsing the table, which is why they show up constantly in analytical work.

This is the 7th post in the SQL 101 series. Here we focus on the row-preserving calculations that make SQL useful for ranking and time-based analysis.


![sql 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/07/07-01-window-calculation-flow.en.png)
*sql 101 chapter 7 flow overview*
> Window functions let you compute context (rank, running total, comparison) for each row while keeping all the original rows. It's analytical power without aggregation.

## Questions to Keep in Mind

- What does OVER (PARTITION BY ...) really mean?
- How do ROW_NUMBER, RANK, and DENSE_RANK differ?
- Why are LAG and LEAD so common in time-series analysis?

## Why It Matters

Rankings, differences, cumulative sums, and month-over-month comparisons are all row-level questions. GROUP BY alone cannot answer them cleanly because it removes the detail you still need. Window functions keep that detail while still letting you reason about the group around each row.

This is one of the places where SQL becomes more than a retrieval language. Once windows become natural, cohort analysis, retention, funnels, and trend reporting stop feeling like special tricks and start looking like combinations of familiar building blocks.

## Window calculation flow

A window function has three parts: the function (ROW_NUMBER, SUM, LAG, etc.), the PARTITION BY (optional grouping), and ORDER BY (the sequence within each partition). PARTITION BY divides the data; ORDER BY sets the order within each partition.

## Key Terms

- **Partition**: rows *grouped together*.
- **Frame**: how far inside the window we *look*.
- **Ranking function**: `ROW_NUMBER, RANK, DENSE_RANK`.
- **Offset function**: `LAG, LEAD` — previous and next row.
- **Running total**: cumulative sum.

## Before/After

**Before**: Compute *revenue per country* with GROUP BY, then *join back* to the original.

**After**: One line — `SUM(total) OVER (PARTITION BY country)` — adds the total *next to each row*.

## Hands-on: Five Patterns

### Step 1 — Row number

```sql
SELECT id, country,
    ROW_NUMBER() OVER (PARTITION BY country ORDER BY signup_at) AS seq
FROM users;
```

### Step 2 — Rank

```sql
SELECT product_id, total,
    RANK() OVER (PARTITION BY product_id ORDER BY total DESC) AS rk
FROM orders;
```

### Step 3 — Previous value

```sql
SELECT user_id, signup_at,
    LAG(signup_at) OVER (PARTITION BY user_id ORDER BY signup_at) AS prev_signup
FROM users;
```

### Step 4 — Running total

```sql
SELECT day, revenue,
    SUM(revenue) OVER (ORDER BY day) AS running_total
FROM daily_revenue;
```

**Expected output:**

| day | revenue | running_total |
| --- | --- | --- |
| 2026-04-01 | 100 | 100 |
| 2026-04-02 | 120 | 220 |
| 2026-04-03 | 90 | 310 |

### Step 5 — 7-day moving average

```sql
SELECT day, revenue,
    AVG(revenue) OVER (
        ORDER BY day
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS ma_7
FROM daily_revenue;
```

## What to Notice in This Code

- An empty `OVER ()` makes everything one partition.
- Order-dependent functions only mean something with `ORDER BY`.
- If you don't *specify the frame*, the per-DB default differs.

## Five Common Mistakes

1. **Confusing `RANK` and `ROW_NUMBER`.** They handle ties differently.
2. **Forgetting PARTITION.** The *whole table* becomes one group.
3. **Implicit frame.** The default `RANGE UNBOUNDED PRECEDING` is *not what you want*.
4. **Ignoring NULL in `LAG`.** The first row's previous value is NULL.
5. **Mixing GROUP BY and windows.** The order of evaluation surprises you.

## How This Shows Up in Production

*7-day moving average revenue*, *Nth order per user*, *month-over-month growth* — each is one window expression. Windows are core to *time-series analysis*.

## How a Senior Engineer Thinks

- *Windows aggregate *without losing detail*.*
- *Always declare the frame.*
- *Pick RANK by the *tie-breaking policy* you want.*
- *LAG/LEAD is the basic *time comparison* tool.*
- *Pull complex windows into a *CTE*.*

## Checklist

- [ ] I know what PARTITION BY does.
- [ ] I know ROW_NUMBER vs RANK.
- [ ] I can use LAG/LEAD.
- [ ] I know the danger of default frames.

## Practice Problems

1. Pick each user's *first order* using `ROW_NUMBER = 1`.
2. Find the *top-3 revenue rows per product* with RANK.
3. Compute a *7-day moving average* of daily revenue.

## Wrap-up and Next Steps

Windows are *aggregates that keep the rows*. Next: *INSERT/UPDATE/DELETE*.

## Answering the Opening Questions

- **What does OVER (PARTITION BY ...) really mean?**
  - The article treats Window Function as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How do ROW_NUMBER, RANK, and DENSE_RANK differ?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why are LAG and LEAD so common in time-series analysis?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [SQL 101 (1/10): What Is SQL?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT Basics](./02-select-basics.md)
- [SQL 101 (3/10): WHERE and Conditions](./03-where-and-conditions.md)
- [SQL 101 (4/10): JOIN](./04-join.md)
- [SQL 101 (5/10): GROUP BY and Aggregates](./05-group-by-and-aggregate.md)
- [SQL 101 (6/10): Subquery](./06-subquery.md)
- **Window Function (current)**
- INSERT, UPDATE, DELETE (upcoming)
- Index and Query Plan (upcoming)
- Practical Analysis SQL (upcoming)

<!-- toc:end -->

## References

- [PostgreSQL — Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html)
- [PostgreSQL — Window Function Reference](https://www.postgresql.org/docs/current/functions-window.html)
- [Mode — Window Functions](https://mode.com/sql-tutorial/sql-window-functions/)
- [Use The Index, Luke — Top-N](https://use-the-index-luke.com/sql/partial-results/top-n-queries)
- [PostgreSQL — Value Expressions](https://www.postgresql.org/docs/current/sql-expressions.html)

Tags: SQL, Database, Postgres, Analytics

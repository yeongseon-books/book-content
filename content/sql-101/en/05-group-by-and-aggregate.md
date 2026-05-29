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

This is the 5th post in the SQL 101 series. Here we focus on how aggregation turns many rows into interpretable metrics.


![sql 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/05/05-01-aggregation-flow.en.png)
*sql 101 chapter 5 flow overview*
> GROUP BY's value is not in the aggregate function names, but in deciding the right grouping level so that your summary answers the actual business question.

## Questions to Keep in Mind

- When does GROUP BY run, and what exactly gets grouped?
- How do SUM, COUNT, and AVG differ in practice?
- What is the real split between WHERE and HAVING?

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

## Aggregate Function Comparison

Each aggregate function compresses multiple rows into a single value, but they differ in how they handle NULL.

| Function | Role | NULL Handling | Notes |
| --- | --- | --- | --- |
| `COUNT(*)` | Total row count | Includes NULL | Most basic aggregate |
| `COUNT(col)` | Non-NULL row count for a column | Excludes NULL | Different from `COUNT(*)` |
| `SUM(col)` | Sum | Excludes NULL | Returns NULL if all values are NULL |
| `AVG(col)` | Average | Excludes NULL | Does NOT treat NULL as 0 |
| `MIN(col)` | Minimum | Excludes NULL | Works on strings and dates too |
| `MAX(col)` | Maximum | Excludes NULL | Works on strings and dates too |

### NULL Handling Example

```sql
CREATE TABLE sales (
    id INT,
    amount INT
);

INSERT INTO sales VALUES (1, 100), (2, NULL), (3, 200);

SELECT
    COUNT(*) AS total_rows,
    COUNT(amount) AS non_null_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount
FROM sales;
```

**Expected output:**

| total_rows | non_null_count | total_amount | avg_amount |
| --- | --- | --- | --- |
| 3 | 2 | 300 | 150 |

`COUNT(*)` returns 3, but `COUNT(amount)` excludes NULL and returns 2. `AVG(amount)` is 300 / 2 = 150, not 300 / 3 = 100.

## GROUP BY + HAVING: Composite Examples

### Users per country with filter

```sql
SELECT
    country,
    COUNT(*) AS user_count,
    AVG(age) AS avg_age
FROM users
GROUP BY country
HAVING COUNT(*) >= 10
ORDER BY user_count DESC;
```

This groups users by country, keeps only countries with 10+ users, and sorts descending. HAVING applies after aggregation, so it can reference aggregate functions like `COUNT(*)`.

### Order status summary

```sql
SELECT
    status,
    COUNT(*) AS order_count,
    SUM(total) AS total_amount,
    AVG(total) AS avg_amount,
    MIN(total) AS min_amount,
    MAX(total) AS max_amount
FROM orders
WHERE created_at >= '2026-01-01'
GROUP BY status
HAVING SUM(total) > 1000
ORDER BY total_amount DESC;
```

This groups 2026+ orders by status and shows only groups whose total exceeds 1000. Combining multiple aggregate functions in one query gives a full statistical snapshot per group.

### Multi-key grouping + HAVING

```sql
SELECT
    country,
    DATE_TRUNC('month', signup_at) AS month,
    COUNT(*) AS new_users
FROM users
WHERE signup_at >= '2025-01-01'
GROUP BY country, month
HAVING COUNT(*) >= 5
ORDER BY country, month;
```

Using country and month together as grouping keys gives per-country-per-month granularity. This pattern appears frequently in time-series analysis.

### Join then aggregate + HAVING

```sql
SELECT
    u.country,
    COUNT(DISTINCT o.id) AS order_count,
    SUM(o.total) AS total_revenue
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE o.status = 'completed'
GROUP BY u.country
HAVING COUNT(DISTINCT o.id) >= 100
ORDER BY total_revenue DESC;
```

When aggregating after a join, watch cardinality carefully. One user can have many orders, so `COUNT(DISTINCT o.id)` is needed to get the correct order count without inflation.

## GROUP BY vs Window Functions

Aggregate functions compress rows; window functions keep every row while computing aggregate values alongside them. Understanding this distinction tells you when to use GROUP BY and when to reach for a window function.

### GROUP BY aggregation (rows collapse)

```sql
SELECT
    country,
    COUNT(*) AS user_count
FROM users
GROUP BY country;
```

**Expected output:**

| country | user_count |
| --- | --- |
| US | 5 |
| UK | 3 |

The result has one row per country. Individual user details disappear.

### Window function aggregation (rows preserved)

```sql
SELECT
    name,
    country,
    COUNT(*) OVER (PARTITION BY country) AS user_count
FROM users;
```

**Expected output:**

| name | country | user_count |
| --- | --- | --- |
| Ada | US | 5 |
| Bob | US | 5 |
| Grace | UK | 3 |

Every row stays intact, and `user_count` shows the total for that row's country.

### When to use which

- **GROUP BY**: When you want one summary row per group.
- **Window function**: When you want to keep individual rows but display group-level stats alongside each row.

For example, if you only need country totals, use GROUP BY. If you want each order's amount alongside its country total (to compute ratios or ranks), use a window function:

```sql
-- Each order's amount alongside the country total
SELECT
    o.id AS order_id,
    u.country,
    o.total AS order_total,
    SUM(o.total) OVER (PARTITION BY u.country) AS country_total
FROM orders o
JOIN users u ON u.id = o.user_id;
```

This keeps every order row and adds the country-level sum for ratio or rank calculations. Window functions are covered in detail in the next article; here it is enough to understand their relationship to GROUP BY.

## Best Practices for Aggregate Queries

```sql
-- Good: explicit group keys, meaningful aliases, ordered output
SELECT
    country,
    DATE_TRUNC('month', signup_at) AS signup_month,
    COUNT(*) AS new_users,
    AVG(age) AS avg_age
FROM users
WHERE signup_at >= '2025-01-01'
GROUP BY country, signup_month
HAVING COUNT(*) >= 10
ORDER BY country, signup_month;

-- Avoid: ambiguous keys, no aliases
-- SELECT country, DATE_TRUNC('month', signup_at), COUNT(*), AVG(age)
-- FROM users WHERE signup_at >= '2025-01-01'
-- GROUP BY country, DATE_TRUNC('month', signup_at);
```

## Practical Anchor: Start by Defining the Grain

Before writing any aggregate query, lock down the **grain** — the unit each output row represents. Is it per-order, per-order-line, or per-customer-per-day? Changing the grain changes the meaning of every metric.

```sql
-- Customer-day grain
SELECT
    customer_id,
    DATE(ordered_at) AS order_date,
    COUNT(*) AS order_count,
    SUM(total_amount) AS gross_revenue
FROM orders
GROUP BY customer_id, DATE(ordered_at);
```

## Practical Anchor: Separate Cleaning Before Aggregation

Aggregating before removing duplicates or cancelled orders produces dashboard numbers that drift. Isolate cleaning into a CTE so it is reviewable and reusable.

```sql
WITH cleaned_orders AS (
    SELECT *
    FROM orders
    WHERE status = 'paid'
      AND is_test = false
)
SELECT
    DATE(ordered_at) AS d,
    COUNT(*) AS paid_orders,
    SUM(total_amount) AS revenue
FROM cleaned_orders
GROUP BY DATE(ordered_at)
ORDER BY d;
```

## Practical Anchor: WHERE vs HAVING Separation Principle

WHERE runs before grouping; HAVING runs after. Mixing them up is one of the most common review findings.

```sql
SELECT customer_id, COUNT(*) AS order_count
FROM orders
WHERE ordered_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY customer_id
HAVING COUNT(*) >= 3;
```

## Practical Anchor: Role Division with Window Functions

When you need both aggregation and ranking, forcing everything into GROUP BY loses the original rows. Split the responsibilities:

```sql
WITH daily AS (
    SELECT DATE(ordered_at) AS d, customer_id, SUM(total_amount) AS revenue
    FROM orders
    GROUP BY DATE(ordered_at), customer_id
)
SELECT
    d,
    customer_id,
    revenue,
    DENSE_RANK() OVER (PARTITION BY d ORDER BY revenue DESC) AS rank_in_day
FROM daily;
```

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

- **When does GROUP BY execute, and what determines the grouping?**
  GROUP BY runs after WHERE and before SELECT. It collapses rows sharing the same key values into groups, then aggregate functions (SUM, COUNT, AVG) compute one summary value per group.
- **How do SUM, COUNT, and AVG differ in behavior?**
  SUM totals numeric values, COUNT tallies rows (COUNT(*)) or non-NULL values (COUNT(col)), and AVG divides the sum by the non-NULL count. NULL handling is the key difference—aggregates silently skip NULLs except COUNT(*).
- **How do WHERE and HAVING divide their roles?**
  WHERE filters individual rows before grouping. HAVING filters groups after aggregation. Use WHERE to reduce input rows (better performance), HAVING to filter on aggregate results (e.g., `HAVING COUNT(*) > 5`).

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

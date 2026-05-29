---
series: sql-101
episode: 2
title: "SQL 101 (2/10): SELECT Basics"
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
  - SELECT
  - Query
  - Database
  - Postgres
seo_description: A practical tour of SELECT — clause order, column projection, aliases, ORDER BY, and LIMIT — the patterns you use every day.
last_reviewed: '2026-05-15'
---

# SQL 101 (2/10): SELECT Basics

SELECT is usually the first SQL statement people become comfortable with, and that familiarity is exactly why teams get sloppy with it. A query that looks harmless can still waste memory, hide intent, and make later review harder if it pulls too many columns or leaves ordering vague.

Good SELECT habits pay off long after the query leaves your editor. The column list explains the business question, aliases make the result readable, and LIMIT keeps exploration fast instead of noisy.

This is the 2nd post in the SQL 101 series. Here we treat SELECT as the tool that shapes the result set, not as a throwaway read statement.


![sql 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/02/02-01-select-evaluation-flow.en.png)
*sql 101 chapter 2 flow overview*
> SELECT is your first tool for designing result sets. Explicit column lists, meaningful aliases, and clear sorting make the difference between a query that gets answered fast and one that creates confusion downstream.

## Questions to Keep in Mind

- What is the safest way to read a SELECT statement?
- Why is naming columns explicitly more than a style preference?
- Where do aliases work, and where do they not?

## Why It Matters

Analysts write SELECT statements dozens of times a day, and application code behind an ORM still emits SELECT under the hood. That makes this clause the place where readability, cost, and trust start to diverge. Two queries can answer the same question while leaving very different maintenance burdens behind.

Explicit column lists help more than the current query. They show future readers what information was actually needed, and they make it obvious when a query starts dragging along unused JSON blobs, large text columns, or unstable positional ordering.

## SELECT evaluation flow

The logical flow is FROM (source) → WHERE (filter) → SELECT (shape) → ORDER BY (sort) → LIMIT (bound). Though you write them in a different order, understanding this sequence helps explain why aliases work in some clauses and not others.

## Key Terms

- **Projection**: the *set of columns* SELECT picks.
- **Alias**: a renamed column or table via `AS new_name`.
- **Sort key**: the column `ORDER BY` uses.
- **Pagination**: `LIMIT` + `OFFSET` to read in slices.
- **Distinct**: removes duplicates — *not free*.

## Before/After

**Before**: `SELECT * FROM orders ORDER BY id;` returns *hundreds of thousands* of rows.

**After**: Pick the *three columns you need* and add `LIMIT 50` to fit the screen.

## Hands-on: Five Patterns You'll Repeat

### Step 1 — Name the columns

```sql
SELECT id, name, signup_at FROM users;
```

Explicit column names document what the query actually needs. When a table gains new columns later, this query keeps returning the same shape — no surprises for downstream consumers.


### Step 2 — Aliases for readability

```sql
SELECT name AS user_name, signup_at AS joined_on FROM users;
```

Aliases make results self-documenting. `user_name` and `joined_on` tell the reader (and the dashboard) what the columns mean without checking the schema.


### Step 3 — Sort

```sql
SELECT id, name FROM users ORDER BY signup_at DESC;
```

Sorting only matters when order matters. `DESC` shows newest first, which is the most common pattern for time-series exploration.


### Step 4 — Top N

```sql
SELECT id, name FROM users ORDER BY id LIMIT 10;
```

**Expected output:**

| id | name |
| --- | --- |
| 1 | Ada |
| 2 | Linus |
| 3 | Grace |


When exploring a large table, always start with a bounded sample. `LIMIT` keeps the result manageable and prevents the UI from freezing on millions of rows.

### Step 5 — Drop duplicates

```sql
SELECT DISTINCT country FROM users;
```

`DISTINCT` removes duplicate rows, but it is not free — internally it requires a sort or hash. Before adding `DISTINCT`, ask why duplicates exist. If a join is producing them, fixing the join is better than masking the problem.


## What to Notice in This Code

- The *write order* is `SELECT ... FROM ... WHERE ...`, but the *logical evaluation* is *FROM → WHERE → SELECT*.
- Aliases are *not visible in WHERE*, but *are visible in ORDER BY*.
- `DISTINCT` needs a *sort or hash*, so it *costs*.

## Five Common Mistakes

1. **`SELECT *` to fetch every column.** Indexes get *underused* and network traffic *balloons*.
2. **`ORDER BY 1` relying on column position.** Adding a column *breaks* it.
3. **No `LIMIT` on huge tables.** The UI *freezes*.
4. **`DISTINCT` to hide duplicates.** You then miss the *join cardinality bug* causing them.
5. **Quoting nothing on aliases with spaces.** A *syntax error* waiting to happen.

## How This Shows Up in Production

Dashboards repeat the `SELECT cols + ORDER BY + LIMIT` pattern *hundreds of times*. In analysis notebooks, you take a *top 50 sample* first to find the shape, then write the real query.

## How a Senior Engineer Thinks

- *Always name columns.*
- *Sort only when order *matters*.*
- *Assume `LIMIT` should have a sane default.*
- *If `DISTINCT` is hiding things, your *join* is suspicious.*
- *Aliases follow a *team convention*.*

## SELECT evaluation order

The order you write clauses and the order the engine processes them are different. Understanding this explains alias visibility rules:

| Step | Clause | Role |
| --- | --- | --- |
| 1 | `FROM` | Identify the source table(s) |
| 2 | `WHERE` | Filter rows (before aggregation) |
| 3 | `GROUP BY` | Group rows for aggregation |
| 4 | `HAVING` | Filter groups |
| 5 | `SELECT` | Choose columns, assign aliases |
| 6 | `ORDER BY` | Sort the result |
| 7 | `LIMIT` / `OFFSET` | Bound the output |

Because `WHERE` runs before `SELECT`, aliases defined in SELECT are invisible to WHERE. Because `ORDER BY` runs after SELECT, it can use aliases. Once you memorize this table, alias errors stop being mysterious.

## Additional DISTINCT, LIMIT, OFFSET patterns

### LIMIT with explicit sort

```sql
SELECT name, signup_at FROM users ORDER BY signup_at LIMIT 5;
```

Always pair LIMIT with ORDER BY. Without an explicit sort, the database returns rows in an undefined order — your "top 5" could change between runs.

### Cursor-based pagination vs OFFSET

```sql
-- OFFSET approach (cost grows with page number)
SELECT order_id, ordered_at, total_amount
FROM orders
ORDER BY ordered_at DESC, order_id DESC
LIMIT 50 OFFSET 50000;
```

`OFFSET` still scans past all skipped rows internally. For deep pages, cursor-based pagination performs much better:

```sql
-- Cursor approach (constant cost per page)
SELECT order_id, ordered_at, total_amount
FROM orders
WHERE (ordered_at, order_id) < (TIMESTAMP '2026-05-10 09:00:00', 881020)
ORDER BY ordered_at DESC, order_id DESC
LIMIT 50;
```

This approach keeps response time stable regardless of how deep into the dataset the user scrolls.

### DISTINCT vs GROUP BY

```sql
-- Deduplication only
SELECT DISTINCT customer_id
FROM orders
WHERE ordered_at >= CURRENT_DATE - INTERVAL '30 days';

-- Aggregation (gives you more information)
SELECT customer_id, COUNT(*) AS order_count
FROM orders
WHERE ordered_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY customer_id;
```

When the goal is just unique values, `DISTINCT` reads naturally. When you also need counts or sums, `GROUP BY` is the right tool. Breaking the "always use DISTINCT" reflex improves both clarity and performance.

## Alias patterns in depth

### Computed columns need aliases

```sql
SELECT
    name,
    EXTRACT(YEAR FROM signup_at) AS signup_year,
    CURRENT_DATE - signup_at AS days_since_signup
FROM users;
```

Without aliases, computed columns show raw expressions as column names — unreadable for anyone consuming the output.

### Table aliases shorten joins

```sql
SELECT u.name, u.email
FROM users AS u
WHERE u.signup_at >= '2026-01-01';
```

Short table aliases (`u`, `o`, `c`) save repetition, especially in multi-join queries. Pick consistent abbreviations across the team.

### Aliases in ORDER BY

```sql
SELECT name, signup_at AS joined
FROM users
ORDER BY joined DESC;
```

`ORDER BY` executes after `SELECT`, so it can reference aliases. This avoids repeating the same expression.

### Aliases are NOT visible in WHERE

```sql
-- This fails: WHERE runs before SELECT
-- SELECT name, signup_at AS joined FROM users WHERE joined >= '2026-02-01';

-- Correct: use the original column name
SELECT name, signup_at AS joined
FROM users
WHERE signup_at >= '2026-02-01';
```

## Concrete anchor: Covering indexes and column selection

Reducing `SELECT *` is not just about network savings. When you select only indexed columns, the engine can answer entirely from the index without touching the table:

```sql
-- Query pattern
SELECT order_id, ordered_at, total_amount
FROM orders
WHERE customer_id = 1201
ORDER BY ordered_at DESC
LIMIT 20;

-- Supporting index (INCLUDE avoids table lookup)
CREATE INDEX idx_orders_customer_recent
    ON orders (customer_id, ordered_at DESC)
    INCLUDE (total_amount);
```

With this index, the query returns results without a single heap access — latency drops and stays stable under load.

## Column selection design criteria

Before writing any SELECT, run through these checks:

- Only include columns the screen/report actually displays.
- Give ambiguous columns aliases that match domain terminology.
- Always specify ORDER BY when order matters to the consumer.
- Do not mix aggregations and raw-row queries in one statement.


## Checklist

- [ ] I can write any query without `SELECT *`.
- [ ] I know how aliases interact with ORDER BY.
- [ ] I know what `LIMIT` does.
- [ ] I can explain the cost of `DISTINCT`.

## Practice Problems

1. Pull the *names of the five most recent users*.
2. Sort by `signup_at` and show the *first ten ascending*.
3. Count the *distinct countries* in `users`.

## Wrap-up and Next Steps

SELECT is mostly about *sentence shape*. The next post is *WHERE and conditions*.

## Answering the Opening Questions

- **In what order should you read a SELECT statement?**
  You write `SELECT ... FROM ... WHERE ... ORDER BY ... LIMIT`, but the engine processes `FROM → WHERE → SELECT → ORDER BY → LIMIT`. Understanding this logical order explains why aliases defined in SELECT aren't visible in WHERE.
- **Why is the habit of naming columns explicitly important?**
  Naming columns explicitly documents intent, prevents breakage when table schemas change, and avoids pulling unnecessary data over the network. `SELECT *` in production queries is a maintenance hazard hiding behind convenience.
- **Where is an alias visible, and where is it not?**
  A column alias defined in SELECT is visible in ORDER BY and outer queries, but not in WHERE or HAVING (which execute before SELECT in logical order). Use subqueries or CTEs when you need to filter by a computed value.

<!-- toc:begin -->
## In this series

- [SQL 101 (1/10): What Is SQL?](./01-what-is-sql.md)
- **SELECT Basics (current)**
- WHERE and Conditions (upcoming)
- JOIN (upcoming)
- GROUP BY and Aggregates (upcoming)
- Subquery (upcoming)
- Window Function (upcoming)
- INSERT, UPDATE, DELETE (upcoming)
- Index and Query Plan (upcoming)
- Practical Analysis SQL (upcoming)

<!-- toc:end -->

## References

- [PostgreSQL — SELECT](https://www.postgresql.org/docs/current/sql-select.html)
- [SQLBolt — SELECT queries](https://sqlbolt.com/lesson/select_queries_introduction)
- [Mode — SELECT statement](https://mode.com/sql-tutorial/sql-select-statement/)
- [SQL Style Guide](https://www.sqlstyle.guide/)
- [PostgreSQL — ORDER BY](https://www.postgresql.org/docs/current/queries-order.html)

Tags: SQL, Database, Postgres, Analytics

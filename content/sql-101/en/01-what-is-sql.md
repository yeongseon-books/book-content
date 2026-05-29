---
series: sql-101
episode: 1
title: "SQL 101 (1/10): What Is SQL?"
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
  - Database
  - RDBMS
  - Postgres
  - Analytics
seo_description: A practical introduction to SQL — the relational model, declarative queries, and where SQL fits into modern engineering work.
last_reviewed: '2026-05-15'
---

# SQL 101 (1/10): What Is SQL?

Most people start SQL by memorizing syntax. In practice, the real turning point is earlier than that. You need a reason SQL survived across spreadsheets, web apps, dashboards, and warehouses, and you need a mental model for why teams still trust it as the common language around data.

If you start from that angle, the basic clauses stop looking like trivia. They start to look like a compact way to describe the exact rows and columns you want without scripting every step yourself.

This is the first post in the SQL 101 series. It establishes the declarative mental model that makes later topics like filtering, joins, aggregation, and query plans easier to reason about.


![sql 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/01/01-01-query-flow-at-a-glance.en.png)
*sql 101 chapter 1 flow overview*
> SQL's power isn't in memorizing syntax, but in understanding how the relational model and declarative execution model work together to keep data reliable and queries portable across systems.

## Questions to Keep in Mind

- What kind of language is SQL, exactly?
- Why is the relational model still the default foundation for analytical and application data?
- What does it mean that SQL is declarative?

## Why It Matters

Analysts, backend engineers, and data engineers all meet the same database from different directions, and SQL is where that conversation becomes concrete. The moment the problem stops fitting inside a spreadsheet, SQL stops being optional and starts becoming the default tool for counting users, filtering orders, and explaining where a metric came from.

SQL also ages unusually well. PostgreSQL, MySQL, SQLite, BigQuery, and Snowflake differ in details, but the core patterns stay familiar. Once you learn the language properly, you carry that skill across products instead of relearning everything from scratch.

## Query flow at a glance

The database engine receives a SQL statement, parses it into an execution plan, and returns the result set. The key insight: you don't tell the engine which index to scan or in what order. You say what you want, and the engine chooses how.

## Key Terms

- **Table**: the basic unit, made of *rows* and *columns*.
- **Row / Column**: *one fact* and *one attribute*.
- **Schema**: the *blueprint* of tables and their relations.
- **Query**: a *sentence* asking the database something.
- **Result set**: the *rows* a query returns.

## Before/After

**Before**: You chain three *VLOOKUPs* across split spreadsheets to find an answer.

**After**: One SQL statement does the *join, aggregation, and filter* in one shot.

## Hands-on: Your First Query in Five Steps

### Step 1 — Create a table

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    signup_at DATE NOT NULL
);
```

This statement creates a `users` table where each user has an `id`, `name`, and `signup_at`. `PRIMARY KEY` uniquely identifies each row, and `NOT NULL` enforces that neither name nor date can be left empty. These constraints are what make the relational model reliable — structure is declared once and enforced on every write.


### Step 2 — Insert data

```sql
INSERT INTO users (id, name, signup_at) VALUES
    (1, 'Ada', '2026-01-01'),
    (2, 'Linus', '2026-02-15'),
    (3, 'Grace', '2026-03-30');
```

Now the empty structure has actual rows. At this stage, keeping the sample data small (3–5 rows) is deliberate — it lets you verify results by hand before scaling up to thousands.


### Step 3 — Read everything

```sql
SELECT * FROM users;
```

This returns every column for every row. It is convenient for exploration, but in production you should name only the columns you need — `SELECT *` pulls unused data across the network and masks schema changes.


### Step 4 — Filter

```sql
SELECT name FROM users WHERE signup_at >= '2026-02-01';
```

**Expected output:**

| name |
| --- |
| Linus |
| Grace |


Here the query narrows both dimensions: only `name` (one column) and only rows where the signup date passes the filter. SQL lets you trim rows and columns simultaneously in one statement.

### Step 5 — Count

```sql
SELECT COUNT(*) AS total FROM users;
```

Counting is the starting point of most analytical SQL. `COUNT(*)` counts rows regardless of NULL values, and `AS total` gives the result column a readable alias.


## What to Notice in This Code

- You never said *how* to fetch the data — only *what* you want.
- The engine decides *whether to use an index*, *how to sort*.
- The same result can be expressed in *many ways*.

## Five Common Mistakes

1. **Using `SELECT *` *by reflex*.** As columns grow, *network and memory* grow with them.
2. **Storing everything as *strings*.** Aggregations later become *misery*.
3. **Treating NULL like *0*.** NULL means *unknown* — a separate value.
4. **Mixing *case styles* randomly.** Pick a team convention to keep queries *readable*.
5. **Eyeballing results.** Verify with *COUNT, SUM* — actual numbers.

## How This Shows Up in Production

Dashboards, user metrics, A/B test results, revenue reports — *most analytics* starts as one or two SQL queries. Backends *read and tune SQL* even when an *ORM* is in front. Most *ETL* steps are SQL.

## How a Senior Engineer Thinks

- *SQL is the language *closest to the data*.*
- *Reading time is longer than writing time.*
- *If you don't read the *plan*, you are not tuning.*
- *Handle NULL *explicitly*.*
- *Break large queries into *CTEs* with named layers.*

## Core Concepts

### What the relational model promises

The basic unit is a table. A table is made of rows (facts) and columns (attributes). One row in a `users` table is one user; columns like `name` and `signup_at` are that user's attributes.

This model is strong because it forces data into a structured form. When every value has a declared type, when primary keys uniquely identify rows, and when constraints are enforced, joins, aggregation, sorting, and filtering all work reliably.

### What "declarative" actually means

In procedural code you write loops and conditionals to describe *how* to compute. In SQL you describe *what* you want. `SELECT name FROM users WHERE signup_at >= '2026-02-01'` declares the desired output. The engine decides whether to scan the table, use an index, or apply a different strategy entirely.

This separation is why the same SQL can perform differently on different data distributions — and why reading the execution plan matters.

### SQL's broad categories

| Category | Purpose | Key statements |
| --- | --- | --- |
| DDL | Define structure | `CREATE`, `ALTER`, `DROP` |
| DML | Read and modify data | `SELECT`, `INSERT`, `UPDATE`, `DELETE` |
| DCL | Manage permissions | `GRANT`, `REVOKE` |

As a beginner, DML — especially `SELECT` — is the center of gravity. But in operations you will also create indexes (DDL) and manage access (DCL), all within SQL.

## SQL vs NoSQL — When to Choose What

| Criterion | SQL (Relational) | NoSQL |
| --- | --- | --- |
| Structure | Tables with fixed schema (rows + columns) | Document, Key-Value, Column-Family — flexible |
| Schema | Must be defined upfront; changes require migration | Schema-less or dynamic schema |
| Scaling | Primarily vertical (scale-up) | Horizontal (scale-out) focus |
| Transactions | Full ACID, complex transactions | Limited; eventual consistency (with exceptions) |
| Best fit | Complex joins, precise aggregation, transactional consistency | High write throughput, flexible schema, distributed scale |

When data has clear relationships, when aggregations and joins are frequent, and when exact totals matter, the relational model wins. When schema changes often, write volume is enormous, and data must shard across many nodes, NoSQL may be more appropriate.

## Dialect differences — PostgreSQL, MySQL, SQLite

SQL has a standard, but each database diverges in small ways. Knowing the common differences saves debugging time when moving between systems.

### String concatenation

- **PostgreSQL**: `'Hello' || ' ' || 'World'` or `CONCAT('Hello', ' ', 'World')`
- **MySQL**: `CONCAT('Hello', ' ', 'World')`
- **SQLite**: `'Hello' || ' ' || 'World'`

### Auto-increment IDs

- **PostgreSQL**: `SERIAL` or `GENERATED BY DEFAULT AS IDENTITY`
- **MySQL**: `AUTO_INCREMENT`
- **SQLite**: `INTEGER PRIMARY KEY AUTOINCREMENT`

### LIMIT and OFFSET

- **PostgreSQL**: `LIMIT 10 OFFSET 5`
- **MySQL**: `LIMIT 10 OFFSET 5` or `LIMIT 5, 10`
- **SQLite**: `LIMIT 10 OFFSET 5`

### Date/time functions

- **PostgreSQL**: `NOW()`, `CURRENT_DATE`, `INTERVAL '1 day'`
- **MySQL**: `NOW()`, `CURDATE()`, `DATE_ADD(NOW(), INTERVAL 1 DAY)`
- **SQLite**: `datetime('now')`, `date('now')`

Despite these differences, the core `SELECT`, `WHERE`, `JOIN`, `GROUP BY` syntax is shared. Learn one dialect well and switching costs stay low.

## Practical example — Full create-to-aggregate flow

```sql
-- Table definition
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    signup_at DATE NOT NULL,
    country TEXT
);

-- Sample data
INSERT INTO users (name, email, signup_at, country) VALUES
    ('Ada', 'ada@example.com', '2026-01-01', 'US'),
    ('Linus', 'linus@example.com', '2026-02-15', 'FI'),
    ('Grace', 'grace@example.com', '2026-03-30', 'US'),
    ('Alan', 'alan@example.com', '2026-04-12', 'UK'),
    ('Sophie', 'sophie@example.com', '2026-05-08', 'FR');

-- Full scan
SELECT * FROM users;

-- Conditional query
SELECT name, country FROM users WHERE country = 'US';

-- Sorting
SELECT name, signup_at FROM users ORDER BY signup_at DESC;

-- Aggregation
SELECT country, COUNT(*) AS user_count
FROM users
GROUP BY country;
```

This example covers the full basic flow: define, insert, query, filter, sort, aggregate. Repeating this loop with different datasets is the fastest way to internalize SQL's declarative style.

## Points that often trip beginners

### Why `SELECT *` needs caution

On a small table, `SELECT *` feels convenient. But as column count and data volume grow, network cost and memory usage grow with them. Dashboard queries and API-backing queries especially benefit from naming only the columns actually needed.

### NULL is not 0 or empty string

`NULL` does not mean zero. It does not mean blank. It means *unknown* or *not yet provided*. Miss this distinction and your aggregations will silently return wrong numbers — `SUM` ignores NULLs, `COUNT(column)` skips them, and `= NULL` never matches (use `IS NULL`).

### A sloppy schema costs more later

Storing every value as `TEXT` feels easy at first. But dates stored as strings cannot be compared with `>=` reliably, amounts stored as text break `SUM`, and inconsistent ID types make joins fragile. Getting the schema right early is inseparable from writing good SQL.

## Concrete anchor: Feeling declarative thinking

The habit that matters more than memorizing syntax is translating a business question into a data operation. The following query answers "top 5 countries by Q1 2026 revenue from paid orders":

```sql
SELECT
    c.country,
    SUM(o.total_amount) AS revenue
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.status = 'paid'
  AND o.ordered_at >= DATE '2026-01-01'
  AND o.ordered_at <  DATE '2026-04-01'
GROUP BY c.country
ORDER BY revenue DESC
LIMIT 5;
```

Notice: no loops, no iteration order. The engine internally decides filter order, join method, and aggregation strategy. SQL's core value is not hiding loops — it is expressing intent in a form the optimizer can rearrange.

## Concrete anchor: Normalized vs denormalized

When order data is denormalized into one flat table, initial queries look simple:

```sql
SELECT order_id, customer_name, product_name, quantity, unit_price
FROM order_flat
WHERE ordered_at >= DATE '2026-05-01';
```

But every customer name change, price update, or duplicate cleanup multiplies across rows. A normalized structure requires JOINs but keeps change safe:

```sql
SELECT
    o.order_id,
    c.customer_name,
    p.product_name,
    oi.quantity,
    oi.unit_price
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.ordered_at >= DATE '2026-05-01';
```

JOINs look heavier at first, but in production this structure is the safety net that keeps data consistent when updates happen.

## Concrete anchor: Reading an execution plan

Many beginners avoid `EXPLAIN`, but checking three things is enough to start:

```sql
EXPLAIN
SELECT *
FROM orders
WHERE customer_id = 42
  AND ordered_at >= DATE '2026-01-01';
```

1. Is it `Seq Scan` or `Index Scan`?
2. Is the estimated `rows` count realistic?
3. Is there a single node whose cost dwarfs the rest?

Once this routine exists, SQL stops being "syntax you type" and becomes "a program you can profile."

## Concrete anchor: Query quality verification routine

As queries grow longer, quality must be measured, not felt. This routine applies to any SQL topic:

1. State the input range (date, status, tenant).
2. Run `COUNT(*)` first to record the base row count.
3. Run the main query and record result rows plus key metrics.
4. Run `EXPLAIN (ANALYZE, BUFFERS)` to find the bottleneck node.
5. Adjust indexes or conditions, then repeat 2–4.

```sql
-- 1) Base count
SELECT COUNT(*) AS base_rows
FROM orders
WHERE ordered_at >= DATE '2026-01-01'
  AND ordered_at <  DATE '2026-02-01';

-- 2) Main query
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue
FROM orders
WHERE ordered_at >= DATE '2026-01-01'
  AND ordered_at <  DATE '2026-02-01'
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 20;

-- 3) Plan check
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue
FROM orders
WHERE ordered_at >= DATE '2026-01-01'
  AND ordered_at <  DATE '2026-02-01'
GROUP BY customer_id;
```

This habit means you never guess why a query is slow — you explain it with data. In team settings, sharing reproducible performance profiles is far more effective than saying "it feels slow."

## Concrete anchor: JOIN vs subquery vs CTE

Three styles, same result — but the execution plan can differ significantly:

```sql
-- A. Direct JOIN
SELECT c.customer_id, SUM(o.total_amount) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE o.status = 'paid'
GROUP BY c.customer_id;
```

```sql
-- B. Subquery
SELECT c.customer_id, x.revenue
FROM customers c
JOIN (
    SELECT customer_id, SUM(total_amount) AS revenue
    FROM orders
    WHERE status = 'paid'
    GROUP BY customer_id
) x ON x.customer_id = c.customer_id;
```

```sql
-- C. CTE
WITH paid_orders AS (
    SELECT customer_id, total_amount
    FROM orders
    WHERE status = 'paid'
),
revenue_by_customer AS (
    SELECT customer_id, SUM(total_amount) AS revenue
    FROM paid_orders
    GROUP BY customer_id
)
SELECT c.customer_id, r.revenue
FROM customers c
JOIN revenue_by_customer r ON r.customer_id = c.customer_id;
```

The right choice is not about style preference — it is about verifiability. Queries that change often benefit from CTEs because each named layer can be tested independently. One-off queries may be clearer inline.

## Concrete anchor: Index strategy and maintenance cost

Indexes speed reads but slow writes. Design them by read/write ratio:

```sql
-- Composite index matching the query pattern
CREATE INDEX idx_orders_customer_status_created
    ON orders (customer_id, status, created_at DESC);

-- Partial index for the hot path
CREATE INDEX idx_orders_paid_created
    ON orders (created_at DESC)
WHERE status = 'paid';
```

After adding an index, verify:

- INSERT/UPDATE TPS did not drop unacceptably
- VACUUM/ANALYZE frequency is not abnormally elevated
- Key queries now use `Index Scan` or `Bitmap Index Scan`

An index is not a free optimization — it is a structure with ongoing maintenance cost. Record both the performance gain and the write overhead.

## Concrete anchor: Transaction isolation demo

Whether you write analytics or operational SQL, concurrency matters. A minimal reproducible demo:

```sql
-- Session A
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT COUNT(*) FROM inventory WHERE product_id = 10;

-- Session B
BEGIN;
UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 10;
COMMIT;

-- Session A again
SELECT COUNT(*) FROM inventory WHERE product_id = 10;
COMMIT;
```

Under `READ COMMITTED`, the second SELECT in Session A can see Session B's commit — the snapshot moved. Under `REPEATABLE READ`, Session A keeps its original snapshot:

```sql
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT SUM(total_amount) FROM orders WHERE status = 'paid';
-- Even after another session commits, this returns the same number
SELECT SUM(total_amount) FROM orders WHERE status = 'paid';
COMMIT;
```

In batch metric calculations, this difference shows up as number mismatches. Document the isolation level and set it explicitly in batch queries.

## Concrete anchor: SQL review checklist

Relying on memory for SQL reviews means standards drift over time. Pin these items in PR descriptions:

- Is the business question accurately translated into SQL conditions?
- Is key uniqueness (PK/AK) preserved across the join path?
- Are date ranges written as half-open intervals to avoid boundary errors?
- Are NULL handling rules stated explicitly?
- Is verification output (row count, sum, top-N sample) attached?

These criteria apply to learning exercises too. SQL connects data to decisions, so the habit of leaving a verifiable reasoning trail outlasts any single query.


## Checklist

- [ ] I can explain *SELECT, FROM, WHERE* out loud.
- [ ] I know the difference between *table, row, column*.
- [ ] I know what *NULL* means.
- [ ] I can tell *DDL* from *DML*.
- [ ] I know what `NULL` means and why `= NULL` never matches.

## Practice Problems

1. Count the total rows in an *orders* table.
2. List the *names* of users who signed up *after March 2026*.
3. Explain to a teammate why `SELECT *` is *risky*.

## Wrap-up and Next Steps

SQL describes the *result*, not the steps. The next post takes a careful look at *SELECT*, the most-used statement.

## Answering the Opening Questions

- **What kind of language is SQL, exactly?**
  SQL is a declarative, set-based language for managing data in relational databases. You must understand the relational model, declarative querying, and the database engine's role together to use it effectively.
- **Why is the relational model still the foundation of data work today?**
  The relational model structures data into rows and columns, with each table representing a clear set of facts. This clarity—one row = one fact, one table = one entity type—remains the most broadly useful abstraction for structured data.
- **What does "declarative language" mean in practice?**
  A declarative language means you state the desired result without specifying procedure. The engine builds the optimal execution plan, which is why the same SQL can perform differently depending on indexes, statistics, and data distribution.

<!-- toc:begin -->
## In this series

- **What Is SQL? (current)**
- SELECT Basics (upcoming)
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

- [PostgreSQL Tutorial — SQL](https://www.postgresql.org/docs/current/tutorial-sql.html)
- [SQLBolt — Interactive SQL Lessons](https://sqlbolt.com/)
- [Use The Index, Luke](https://use-the-index-luke.com/)
- [Mode — SQL Tutorial](https://mode.com/sql-tutorial/)
- [PostgreSQL — Documentation home](https://www.postgresql.org/docs/current/index.html)

Tags: SQL, Database, Postgres, Analytics

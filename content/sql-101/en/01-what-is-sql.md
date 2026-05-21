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

### Step 2 — Insert data

```sql
INSERT INTO users (id, name, signup_at) VALUES
    (1, 'Ada', '2026-01-01'),
    (2, 'Linus', '2026-02-15'),
    (3, 'Grace', '2026-03-30');
```

### Step 3 — Read everything

```sql
SELECT * FROM users;
```

### Step 4 — Filter

```sql
SELECT name FROM users WHERE signup_at >= '2026-02-01';
```

**Expected output:**

| name |
| --- |
| Linus |
| Grace |

### Step 5 — Count

```sql
SELECT COUNT(*) AS total FROM users;
```

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

## Checklist

- [ ] I can explain *SELECT, FROM, WHERE* out loud.
- [ ] I know the difference between *table, row, column*.
- [ ] I know what *NULL* means.
- [ ] I can tell *DDL* from *DML*.

## Practice Problems

1. Count the total rows in an *orders* table.
2. List the *names* of users who signed up *after March 2026*.
3. Explain to a teammate why `SELECT *` is *risky*.

## Wrap-up and Next Steps

SQL describes the *result*, not the steps. The next post takes a careful look at *SELECT*, the most-used statement.

## Answering the Opening Questions

- **What kind of language is SQL, exactly?**
  - The article treats What Is SQL? as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why is the relational model still the default foundation for analytical and application data?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What does it mean that SQL is declarative?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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

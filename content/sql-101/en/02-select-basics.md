---
series: sql-101
episode: 2
title: SELECT Basics
status: content-ready
targets:
  tistory: true
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
last_reviewed: '2026-05-04'
---

# SELECT Basics

This is post 2 in the SQL 101 series.

> SQL 101 series (2/10)

<!-- a-grade-intro:begin -->

**Core question**: Why is `SELECT *` *risky*, and what changes when you make *naming columns* a habit?

> *SELECT looks like a simple read, but writing it well lowers the *cost for the whole team*.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The *logical order* of SELECT clauses
- Column projection and *aliases*
- *ORDER BY* and *LIMIT*
- The meaning and cost of *DISTINCT*
- Five common mistakes

## Why It Matters

An analyst issues SELECT *hundreds of times a day*. One small habit changes *reading speed, cost, and trust*. Naming columns and using clear aliases is a gift to the *future-you in six months*.

> *SELECT is *easy to say* and *easy to misread*.*

## Concept at a Glance

```mermaid
flowchart LR
    From["FROM table"] --> Where["WHERE filter"]
    Where --> Group["GROUP BY"]
    Group --> Having["HAVING"]
    Having --> Select["SELECT columns"]
    Select --> Order["ORDER BY"]
    Order --> Limit["LIMIT"]
```

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

### Step 2 — Aliases for readability

```sql
SELECT name AS user_name, signup_at AS joined_on FROM users;
```

### Step 3 — Sort

```sql
SELECT id, name FROM users ORDER BY signup_at DESC;
```

### Step 4 — Top N

```sql
SELECT id, name FROM users ORDER BY id LIMIT 10;
```

### Step 5 — Drop duplicates

```sql
SELECT DISTINCT country FROM users;
```

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

<!-- toc:begin -->
- [What Is SQL?](./01-what-is-sql.md)
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

Tags: SQL, SELECT, Query, Database, Postgres

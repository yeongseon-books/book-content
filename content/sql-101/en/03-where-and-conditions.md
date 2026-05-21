---
series: sql-101
episode: 3
title: "SQL 101 (3/10): WHERE and Conditions"
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
  - WHERE
  - Filter
  - Database
  - "NULL"
seo_description: A practical guide to WHERE — comparison operators, AND/OR precedence, IN, BETWEEN, LIKE, and NULL-safe comparisons.
last_reviewed: '2026-05-15'
---

# SQL 101 (3/10): WHERE and Conditions

Most SQL mistakes do not come from exotic syntax. They come from one condition that was slightly too broad, one NULL comparison that silently dropped rows, or one expression shape that forced the database into a full scan.

That is why WHERE deserves more attention than its short syntax suggests. It decides both correctness and cost, and it is often the line that determines whether a query stays cheap or turns into a production incident.

This is post 3 in the SQL 101 series. Here we treat WHERE as the gate that controls both accuracy and performance.


![sql 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/03/03-01-where-evaluation-flow.en.png)
*sql 101 chapter 3 flow overview*
> WHERE determines which rows even make it into the result. Getting the logic right is non-negotiable; getting the performance is about knowing when the database can use an index.

## Questions to Keep in Mind

- How should you read comparison operators and predicates?
- Why do AND and OR precedence mistakes keep showing up in production?
- When do IN, BETWEEN, and LIKE fit best?

## Why It Matters

A single predicate often decides most of the cost of a query. Whether an index is used, how many rows survive, and how much memory the database spends all flow from the condition shape. A broad filter and a selective filter can look almost identical while behaving very differently on large tables.

Correctness is just as important. A query that returns the wrong answer quickly is more dangerous than one that fails loudly, and NULL handling plus precedence mistakes are common reasons apparently reasonable queries end up lying quietly.

## WHERE evaluation flow

WHERE is evaluated before SELECT, which means column aliases from SELECT aren't visible in WHERE. This is why you sometimes need to repeat the same expression—the evaluation order dictates visibility.

## Key Terms

- **Predicate**: a *condition expression* deciding row passage.
- **Sargable**: a condition shape that *can use an index*.
- **Three-valued logic**: true / false / NULL.
- **Operator precedence**: AND binds *before* OR.
- **Pattern matching**: `LIKE` with `%` and `_`.

## Before/After

**Before**: `WHERE name LIKE '%kim%' OR age > 30` — *intent is unclear*.

**After**: `WHERE (name LIKE '%kim%' OR age > 30) AND active = TRUE` — parentheses make intent *explicit*.

## Hands-on: Five Conditions

### Step 1 — Comparison

```sql
SELECT * FROM users WHERE age >= 18;
```

### Step 2 — Range

```sql
SELECT * FROM orders WHERE total BETWEEN 100 AND 500;
```

### Step 3 — Membership

```sql
SELECT * FROM users WHERE country IN ('KR', 'JP', 'US');
```

### Step 4 — Pattern

```sql
SELECT * FROM users WHERE email LIKE '%@example.com';
```

### Step 5 — NULL-safe

```sql
SELECT * FROM users WHERE deleted_at IS NULL;
```

**Expected output:**

| id | name | deleted_at |
| --- | --- | --- |
| 1 | Ada | NULL |
| 2 | Linus | NULL |

## What to Notice in This Code

- `LIKE '%xxx'` *cannot use an index*. Trailing wildcards are *expensive*.
- `IN` works for *small lists*. For larger ones, switch to a *join*.
- Only `IS NULL` matches NULL. `= NULL` is *always false*.

## Five Common Mistakes

1. **Comparing with `= NULL`.** The result is treated as false, so rows *vanish*.
2. **Skipping AND/OR parentheses.** AND binds first and *changes meaning*.
3. **Wrapping the column in a function.** `WHERE LOWER(email) = ...` *kills the index*.
4. **`LIKE '%kim%'`** scans *millions of rows*.
5. **Type mismatch.** `age = '18'` triggers an *implicit cast* that *defeats the index*.

## How This Shows Up in Production

Dashboard filters, *search boxes*, and *permission checks* all funnel into WHERE. Search is usually offloaded to a *full-text index* or a *dedicated search engine*. NULL handling becomes a *team convention*.

## How a Senior Engineer Thinks

- *Never wrap the column in a function.*
- *Handle NULL *explicitly*.*
- *Look at the *selectivity* of each predicate.*
- *Always parenthesize AND/OR.*
- *Big OR lists belong in a *join or IN*.*

## Checklist

- [ ] I know the difference between `IS NULL` and `= NULL`.
- [ ] I know AND/OR precedence.
- [ ] I know when `LIKE` is expensive.
- [ ] I can define *sargable*.

## Practice Problems

1. Return only users where `deleted_at` is NULL.
2. Filter rows where `signup_at` falls in *Q1 2026*.
3. Rewrite `country IN ('KR','JP')` using *OR* and compare.

## Wrap-up and Next Steps

WHERE is the *gatekeeper*. The next post is *JOIN*.

## Answering the Opening Questions

- **How should you read comparison operators and predicates?**
  - The article treats WHERE and Conditions as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why do AND and OR precedence mistakes keep showing up in production?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **When do IN, BETWEEN, and LIKE fit best?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [SQL 101 (1/10): What Is SQL?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT Basics](./02-select-basics.md)
- **WHERE and Conditions (current)**
- JOIN (upcoming)
- GROUP BY and Aggregates (upcoming)
- Subquery (upcoming)
- Window Function (upcoming)
- INSERT, UPDATE, DELETE (upcoming)
- Index and Query Plan (upcoming)
- Practical Analysis SQL (upcoming)

<!-- toc:end -->

## References

- [PostgreSQL — WHERE clause](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-WHERE)
- [PostgreSQL — Pattern Matching](https://www.postgresql.org/docs/current/functions-matching.html)
- [Use The Index, Luke — Where Clause](https://use-the-index-luke.com/sql/where-clause)
- [Mode — WHERE](https://mode.com/sql-tutorial/sql-where/)
- [PostgreSQL — Comparison Functions and Operators](https://www.postgresql.org/docs/current/functions-comparison.html)

Tags: SQL, Database, Postgres, Analytics

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

This is the 3rd post in the SQL 101 series. Here we treat WHERE as the gate that controls both accuracy and performance.


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

Comparison operators work exactly as expected: `>=`, `<=`, `<>` (not equal). The key rule is to keep the column on the left, unmodified — this lets the optimizer use indexes.


### Step 2 — Range

```sql
SELECT * FROM orders WHERE total BETWEEN 100 AND 500;
```

`BETWEEN` is inclusive on both ends: `total >= 100 AND total <= 500`. It reads more naturally for range queries, especially on dates.


### Step 3 — Membership

```sql
SELECT * FROM users WHERE country IN ('KR', 'JP', 'US');
```

`IN` replaces a chain of OR conditions with a compact list. For small sets (3–10 values) it is ideal. For larger sets, join against a temporary table instead.


### Step 4 — Pattern

```sql
SELECT * FROM users WHERE email LIKE '%@example.com';
```

Leading wildcards (`%xxx`) force a full table scan because the engine cannot binary-search the index. Trailing wildcards (`xxx%`) can still use the index.


### Step 5 — NULL-safe

```sql
SELECT * FROM users WHERE deleted_at IS NULL;
```

`NULL` is not a value — it is an unknown state. The only operators that work with it are `IS NULL` and `IS NOT NULL`. Writing `= NULL` always evaluates to unknown and silently returns zero rows.


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

## Operator precedence

| Priority | Operator | Notes |
| --- | --- | --- |
| 1 | `()` | Parentheses — evaluated first |
| 2 | `NOT` | Logical negation |
| 3 | Comparison | `=`, `<>`, `>`, `<`, `>=`, `<=`, `BETWEEN`, `IN`, `LIKE`, `IS NULL` |
| 4 | `AND` | Logical AND |
| 5 | `OR` | Logical OR |

`AND` binds tighter than `OR`. So `A OR B AND C` means `A OR (B AND C)`, not `(A OR B) AND C`. Always use parentheses when mixing AND and OR:

```sql
-- Without parentheses: meaning may surprise you
SELECT * FROM users
WHERE country = 'US' OR country = 'UK' AND age >= 18;

-- Explicit intent
SELECT * FROM users
WHERE (country = 'US' OR country = 'UK') AND age >= 18;
```

## Indexes and WHERE conditions

### Sargable conditions (index-friendly)

```sql
-- Index on user_id can be used directly
SELECT * FROM orders WHERE user_id = 123;
```

The engine jumps straight to the matching rows via the index.

### Non-sargable conditions (index-hostile)

```sql
-- Wrapping the column in a function blocks the index
SELECT * FROM orders WHERE YEAR(order_date) = 2026;

-- Rewrite as a range to restore index usage
SELECT * FROM orders
WHERE order_date >= '2026-01-01' AND order_date < '2027-01-01';
```

Rule: keep the column bare on the left side. Move transformations to the comparison value.

### Type mismatches

Comparing a numeric column against a string (`age = '18'`) causes an implicit cast that can defeat the index silently. Always match types exactly.

## Concrete anchor: Rewriting conditions for index use

Same semantics, very different execution plans:

```sql
-- Bad: function on column
SELECT * FROM events
WHERE DATE(created_at) = DATE '2026-05-01';

-- Good: half-open range
SELECT * FROM events
WHERE created_at >= TIMESTAMP '2026-05-01 00:00:00'
  AND created_at <  TIMESTAMP '2026-05-02 00:00:00';
```

The range form lets the optimizer use an index range scan instead of a full table scan.

## Concrete anchor: OR splitting with UNION ALL

When OR produces wide scans, splitting into UNION ALL can yield better plans:

```sql
-- Planner may choose a broad scan
SELECT * FROM orders
WHERE status = 'paid' OR status = 'refunded';

-- Alternative: separate scans, each using an index
SELECT * FROM orders WHERE status = 'paid'
UNION ALL
SELECT * FROM orders WHERE status = 'refunded';
```

When duplicates are impossible (each row has one status), `UNION ALL` avoids unnecessary sort/dedup overhead.

## Concrete anchor: NULL safety with NOT EXISTS

`NOT IN` behaves unexpectedly when the subquery returns NULLs — the entire expression evaluates to unknown and returns zero rows. `NOT EXISTS` is immune to this trap:

```sql
-- Safe regardless of NULLs in blacklist
SELECT c.customer_id
FROM customers c
WHERE NOT EXISTS (
    SELECT 1
    FROM blacklist b
    WHERE b.customer_id = c.customer_id
);
```


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

- **How should you read comparison operators and conditional expressions?**
  WHERE filters rows coming from FROM. Conditions here directly determine which rows survive—and whether an index can accelerate that filtering. Read each condition as "which rows do I keep?" not "what do I want."
- **Why does AND/OR precedence frequently cause bugs?**
  AND binds tighter than OR, so `A OR B AND C` means `A OR (B AND C)`, not `(A OR B) AND C`. Without explicit parentheses, you may silently select far more (or fewer) rows than intended—a common source of subtle data bugs.
- **When do IN, BETWEEN, and LIKE each fit best?**
  Use `IN` for discrete value lists, `BETWEEN` for continuous ranges (inclusive), and `LIKE` for simple pattern matching. Each can leverage indexes differently—`LIKE 'abc%'` uses a B-tree index, but `LIKE '%abc'` cannot.

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

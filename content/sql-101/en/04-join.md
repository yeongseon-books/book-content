---
series: sql-101
episode: 4
title: "SQL 101 (4/10): JOIN"
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
  - JOIN
  - Relational
  - Database
  - Query
seo_description: A practical tour of INNER, LEFT, RIGHT, FULL, and CROSS JOIN — cardinality traps and safe patterns for multi-table queries.
last_reviewed: '2026-05-15'
---

# SQL 101 (4/10): JOIN

Once you leave single-table questions behind, SQL gets more powerful and more dangerous at the same time. The query still looks readable, but one wrong join assumption can double a metric, erase unmatched rows, or explode the result size before anyone notices.

That is why JOIN is less about memorizing keywords and more about thinking in relationships. The real skill is predicting how many matches each row can have before you trust any aggregate built on top of the result.

This is the 4th post in the SQL 101 series. Here we treat JOIN as a relationship operation between row sets, not as a formatting trick for columns.


![sql 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/04/04-01-join-result-flow.en.png)
*sql 101 chapter 4 flow overview*
> JOIN is not about memorizing the types; it's about predicting what the result will look like when you connect two tables on a condition, and knowing when to use each type.

## Questions to Keep in Mind

- How do INNER, LEFT, RIGHT, FULL, and CROSS JOIN differ?
- Why should you inspect join keys and cardinality before anything else?
- Why do row counts sometimes grow unexpectedly after a join?

## Why It Matters

Most real queries include a join somewhere in the middle. Reports pull users, orders, products, payments, and events together; application debugging queries walk relationships to explain what happened to one customer. In all of those cases, the central risk is not the keyword itself. It is the hidden multiplicity behind the relationship.

Strong SQL reviewers do not just read the ON clause. They ask what kind of match count is expected on each side and whether a later SUM or COUNT will stay stable after that expansion.

## JOIN result flow

INNER JOIN keeps only matching rows. LEFT JOIN keeps all left rows and fills right columns with NULL where there's no match. FULL OUTER JOIN keeps both sides. CROSS JOIN produces every combination—use carefully.

## Key Terms

- **Join key**: the columns that *connect two tables*.
- **Cardinality**: how many *partners* one row has.
- **Equi-join**: the most common form, joined on `=`.
- **Self-join**: a table joined to *itself*.
- **Anti-join**: rows with *no partner*.

## Before/After

**Before**: `SELECT SUM(o.total) FROM orders o JOIN payments p ON o.id = p.order_id;` — split payments *double the total*.

**After**: Join against an *aggregated subquery* on payments to keep cardinality *1:1*.

## Hands-on: Five JOIN Patterns

### Step 1 — INNER JOIN

```sql
SELECT u.name, o.id AS order_id
FROM users u
INNER JOIN orders o ON o.user_id = u.id;
```

INNER JOIN returns only rows where both sides have a match. If a user has no orders, that user disappears from the result entirely.


### Step 2 — LEFT JOIN

```sql
SELECT u.name, o.id AS order_id
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;
```

LEFT JOIN keeps every row from the left table (`users`). When a user has no orders, the order columns come back as NULL — which is the signal "no match found," not a data error.


### Step 3 — Anti-join (users with no orders)

```sql
SELECT u.id, u.name
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.id IS NULL;
```

This anti-join pattern (`LEFT JOIN ... WHERE right.id IS NULL`) is one of the most common analytical patterns. It answers "who has never done X?" efficiently.


**Expected output:**

| id | name |
| --- | --- |
| 3 | Grace |

### Step 4 — Self-join (direct manager)

```sql
SELECT e.name AS emp, m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id;
```

A self-join treats the same table as if it were two separate tables. The alias difference (`e` for employee, `m` for manager) is what makes it readable.


### Step 5 — Multi-join

```sql
SELECT u.name, p.name AS product
FROM users u
JOIN orders o ON o.user_id = u.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id;
```

Multi-join queries read like a path through the data model: user → order → order_item → product. At each step, verify the join key is unique on one side to avoid row multiplication.


## What to Notice in This Code

- A NULL after LEFT JOIN is a *signal of no match*.
- Anti-join is often *clearer than NOT EXISTS* and *easier to tune*.
- Multi-joins go fastest when the *driving table is smallest*.

## Five Common Mistakes

1. **Summing without checking *cardinality*.** Totals *inflate*.
2. **Turning LEFT JOIN into INNER via WHERE.** `WHERE o.x = ...` *drops the NULL rows*.
3. **Mixing `USING` and `ON`** in one query — readability *suffers*.
4. **Accidental CROSS JOIN.** *Cartesian explosion*.
5. **Type mismatch on join keys.** Implicit casts *kill the index*.

## How This Shows Up in Production

Reports usually join *event + user + product* — three to five tables. The *fact table* sits in the middle and *dimensions* are LEFT-joined around it. We verify cardinality with *COUNT comparisons*.

## How a Senior Engineer Thinks

- *Write down the cardinality assumption *before* joining.*
- *Always remember what NULLs in LEFT JOIN mean.*
- *Often you should aggregate *before* joining.*
- *Multi-joins read better as *CTEs*.*
- *Join keys must have *indexes* to be fast.*

## JOIN type comparison

| JOIN type | Result rows | Description |
| --- | --- | --- |
| `INNER JOIN` | Only rows matching on both sides | Intersection |
| `LEFT JOIN` | All left rows + matching right (NULL if no match) | Left-complete |
| `RIGHT JOIN` | All right rows + matching left (NULL if no match) | Right-complete |
| `FULL OUTER JOIN` | All rows from both sides (NULLs where unmatched) | Union |
| `CROSS JOIN` | Every combination (no condition) | Cartesian product |

### Row count expectations

- **INNER**: 0 to `min(left, right)` (depends on match rate)
- **LEFT**: at least `left_count` (more if 1:N on right)
- **CROSS**: exactly `left_count × right_count`

`INNER` and `LEFT` cover 90%+ of production joins. `CROSS JOIN` almost always indicates a missing join condition.

## Why totals inflate after joining

If one order has two payment rows, joining `orders` to `payments` duplicates the order row. Summing `order.total` then counts it twice. Fix: aggregate the right side first, then join:

```sql
-- Safe: aggregate before joining
SELECT o.id, o.total, agg.paid
FROM orders o
JOIN (
    SELECT order_id, SUM(amount) AS paid
    FROM payments
    GROUP BY order_id
) agg ON agg.order_id = o.id;
```

## LEFT JOIN turned into INNER by WHERE

```sql
-- Looks like LEFT JOIN but behaves as INNER:
SELECT u.name, o.total
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.status = 'paid';  -- eliminates NULL rows!

-- To preserve left rows, move the filter into ON:
SELECT u.name, o.total
FROM users u
LEFT JOIN orders o ON o.user_id = u.id AND o.status = 'paid';
```

When you filter on the right table in WHERE, NULL rows from the LEFT JOIN get dropped. Move the condition into the ON clause if you want to keep unmatched left rows.

## Concrete anchor: Verifying cardinality before aggregation

Before summing anything across a join, verify row counts match expectations:

```sql
-- Step 1: count base rows
SELECT COUNT(*) FROM orders WHERE customer_id = 42;

-- Step 2: count after join
SELECT COUNT(*)
FROM orders o
JOIN payments p ON p.order_id = o.id
WHERE o.customer_id = 42;
```

If step 2 is larger than step 1, the join introduced duplication. Aggregate the right side first before joining.


## Checklist

- [ ] I can sketch INNER, LEFT, RIGHT, FULL.
- [ ] I can define cardinality.
- [ ] I can write anti-join two ways.
- [ ] I know the danger of CROSS JOIN.

## Practice Problems

1. Find *users with no orders* using an anti-join.
2. Compute *revenue per product* by *aggregating before joining*.
3. Use a *self-join* to attach the *manager name*.

## Wrap-up and Next Steps

JOIN is the language of *sets*. Next up: *GROUP BY and aggregates*.

## Answering the Opening Questions

- **What distinguishes INNER, LEFT, RIGHT, FULL, and CROSS JOIN?**
  INNER keeps only matching rows from both sides. LEFT keeps all left-table rows (NULLs for no match on right). RIGHT is the mirror. FULL keeps all rows from both. CROSS produces the Cartesian product—every combination. The join type determines result size and NULL behavior.
- **Why must you verify join keys and cardinality first?**
  If a join key has duplicates on one side (1:N), the result multiplies. If duplicates exist on both sides (M:N), the result explodes. Checking cardinality before writing the JOIN prevents unexpected row multiplication that silently corrupts aggregates downstream.
- **Why does the result sometimes grow unexpectedly large?**
  Incorrect or missing join conditions create partial or full Cartesian products. Always verify the join produces the expected row count—especially when joining tables with different granularity or when composite keys are partially matched.

<!-- toc:begin -->
## In this series

- [SQL 101 (1/10): What Is SQL?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT Basics](./02-select-basics.md)
- [SQL 101 (3/10): WHERE and Conditions](./03-where-and-conditions.md)
- **JOIN (current)**
- GROUP BY and Aggregates (upcoming)
- Subquery (upcoming)
- Window Function (upcoming)
- INSERT, UPDATE, DELETE (upcoming)
- Index and Query Plan (upcoming)
- Practical Analysis SQL (upcoming)

<!-- toc:end -->

## References

- [PostgreSQL — Joins](https://www.postgresql.org/docs/current/tutorial-join.html)
- [SQLBolt — Multi-table queries with JOIN](https://sqlbolt.com/lesson/select_queries_with_joins)
- [Mode — JOIN](https://mode.com/sql-tutorial/sql-joins/)
- [Use The Index, Luke — Joins](https://use-the-index-luke.com/sql/join)
- [PostgreSQL — Table Expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html)

Tags: SQL, Database, Postgres, Analytics

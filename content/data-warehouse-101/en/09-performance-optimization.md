---
series: data-warehouse-101
episode: 9
title: Performance Optimization
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DataWarehouse
  - Performance
  - Optimization
  - Cost
  - Analytics
seo_description: Patterns that drive warehouse performance, five ways to cut cost, and how to read a query plan like a senior analyst.
last_reviewed: '2026-05-04'
---

# Performance Optimization
> Data Warehouse 101 series (9/10)

This is post 9 in the Data Warehouse 101 series.

<!-- a-grade-intro:begin -->

**Core question**: Why does *one query finish in a second* and another *take five minutes*? How do you *cut cost*?

> *Warehouse performance is shaped by *bytes read* and *data shuffled*.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The *main patterns* that drive performance
- *Five ways* to cut cost
- How to read a *query plan*
- Five-step optimization hands-on
- Five common pitfalls

## Why It Matters

Warehouses charge by *what you read*. The same answer with *fewer bytes* means *less cost and less time*. *Reading the plan* is where optimization begins.

> *Optimization without measurement is *guessing*. Read the plan first.*

## Concept at a Glance

```mermaid
flowchart LR
    Query["SQL"] --> Plan["Query Plan"]
    Plan --> Scan["Bytes Scanned"]
    Plan --> Shuffle["Shuffle"]
    Plan --> Spill["Spill to Disk"]
    Scan --> Cost["Cost"]
```

## Key Terms

- **Bytes Scanned**: How much data the query *actually read*. The main *cost driver*.
- **Shuffle**: *Data movement* between nodes — happens during *joins/aggregations*.
- **Spill**: Data that overflowed memory and *spilled to disk*.
- **Materialized View**: A pre-computed view of a frequent result.
- **Approximate Aggregate**: Functions like `APPROX_COUNT_DISTINCT`.

## Before/After

**Before**: `SELECT *` reads *all columns* — *tens of GB* scanned, *$5* cost.

**After**: Read only the *four needed columns* — *hundreds of MB*, *$0.05*.

## Hands-on: Five-step Optimization

### Step 1 — Narrow the columns

```sql
-- Before
SELECT * FROM fact_orders WHERE order_date = '2026-05-04';

-- After
SELECT order_id, user_key, amount
FROM fact_orders
WHERE order_date = '2026-05-04';
```

### Step 2 — Preserve partition pruning

```sql
-- Compare directly without functions
WHERE order_date BETWEEN '2026-05-01' AND '2026-05-31'
```

### Step 3 — Use a materialized view

```sql
CREATE MATERIALIZED VIEW mv_daily_revenue AS
SELECT order_date, SUM(amount) AS revenue
FROM fact_orders
GROUP BY order_date;
```

### Step 4 — Approximate aggregate

```sql
-- 99% accuracy is enough most of the time
SELECT APPROX_COUNT_DISTINCT(user_key) AS active_users
FROM fact_orders
WHERE order_date >= CURRENT_DATE - 30;
```

### Step 5 — Broadcast the smaller side of large joins

```sql
-- BigQuery hint example (conceptual)
SELECT /*+ BROADCAST(d) */ f.amount, d.country
FROM fact_orders f
JOIN dim_user d ON d.user_key = f.user_key;
```

## What to Notice in This Code

- Narrowing *columns* is the *biggest win*.
- Keep *partition pruning* alive.
- Cache *frequent results* with materialized views.

## Five Common Mistakes

1. **Using `SELECT *` *out of habit*.** *Cost scales with column count*.
2. **Wrapping the *partition key* in a *function*.** Pruning breaks.
3. **Running large *COUNT(DISTINCT)*.** *Approximate* is often enough.
4. **Skipping *materialized view refresh*.** *Stale data* lands on dashboards.
5. **Relying on *indexes*.** Warehouses are the world of *partition + clustering*.

## How This Shows Up in Production

Analysts read *query plans* daily. *Cost alerts* fire to *Slack* above thresholds. *Repeated heavy queries* get cached as *materialized views*.

## How a Senior Engineer Thinks

- *Look at *bytes scanned* first.*
- *No plan reading, no real tuning.*
- *Be unafraid of *approximate aggregates*.*
- *Put *cost alerts* in the *team channel*.*
- *Break a big query into *small ones*.*

## Checklist

- [ ] You can read a *query plan*.
- [ ] You know what *bytes scanned* means.
- [ ] You know the trade-off of a *materialized view*.
- [ ] You know when to use *approximate aggregates*.

## Practice Problems

1. Pick *one slow query* and apply *column narrowing*.
2. Fix a query where *pruning broke*.
3. List cases where *approximate* fits and where it does not.

## Wrap-up and Next Steps

Performance starts with *measurement*. Next we walk through *designing a warehouse* end to end.

<!-- toc:begin -->
- [What Is a Data Warehouse?](./01-what-is-data-warehouse.md)
- [OLTP and OLAP](./02-oltp-and-olap.md)
- [Fact and Dimension](./03-fact-and-dimension.md)
- [Star Schema](./04-star-schema.md)
- [Partition and Clustering](./05-partition-and-clustering.md)
- [ETL and ELT](./06-etl-and-elt.md)
- [BI and Dashboard](./07-bi-and-dashboard.md)
- [Data Mart](./08-data-mart.md)
- **Performance Optimization (current)**
- Warehouse Design Example (upcoming)
<!-- toc:end -->

## References

- [BigQuery — Optimize Query Performance](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
- [Snowflake — Query Performance](https://docs.snowflake.com/en/user-guide/performance-query)
- [Use The Index, Luke](https://use-the-index-luke.com/)
- [Redshift — Query Tuning](https://docs.aws.amazon.com/redshift/latest/dg/c-query-performance.html)

Tags: DataWarehouse, Performance, Optimization, Cost, Analytics

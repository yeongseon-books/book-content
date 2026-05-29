---
series: data-warehouse-101
episode: 9
title: "Data Warehouse 101 (9/10): Performance Optimization"
status: publish-ready
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
last_reviewed: '2026-05-15'
---

# Data Warehouse 101 (9/10): Performance Optimization

Warehouse tuning starts when someone asks why two queries that look similar cost wildly different amounts. In practice, the answer is usually hiding in scan volume, shuffle volume, or work the engine had no chance to skip.

This is the 9th post in the Data Warehouse 101 series.

In this post, we treat optimization as a measurement discipline instead of a bag of tricks. The goal is to read the plan, locate the expensive stage, and change the query shape before cost becomes a surprise.


![data warehouse 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-warehouse-101/09/09-01-concept-at-a-glance.en.png)
*data warehouse 101 chapter 9 flow overview*
> Performance tuning follows a cycle: measure, find the bottleneck, improve, and measure again. Start with the query plan, not your intuition.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Performance Optimization?
- Which signal should the example or diagram make visible for Performance Optimization?
- What failure should be prevented first when Performance Optimization reaches a real system?

## Questions this article answers

- Which patterns create the biggest performance differences in a warehouse?
- How do you get the same answer at lower cost?
- Why should bytes scanned, shuffle, and spill be the first signals you inspect?
- When do approximate aggregations and materialized views pay off?
- Why does tuning so often miss the mark when you skip the query plan?

## What You Will Learn

- The *main patterns* that drive performance
- *Five ways* to cut cost
- How to read a *query plan*
- Five-step optimization hands-on
- Five common pitfalls

## Why It Matters

Warehouses charge by *what you read*. The same answer with *fewer bytes* means *less cost and less time*. *Reading the plan* is where optimization begins.

> *Optimization without measurement is *guessing*. Read the plan first.*

This picture shows the performance optimization cycle. The key is not to memorize tuning tricks, but to learn how to find where time is actually spent.

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


## Optimization Priority Table

When a warehouse performance request arrives, many teams think of indexes first. But in column-oriented warehouses, scan range and data movement are the bigger bottlenecks.

| Priority | Strategy | Expected benefit | Verification metric |
| --- | --- | --- | --- |
| 1 | Minimize column selection | Immediate drop in bytes scanned | bytes scanned/query |
| 2 | Maintain partition pruning | Range-cut on large tables | partition hit ratio |
| 3 | Fix join order and keys | Reduce shuffle | shuffle bytes |
| 4 | Pre-aggregate / materialize | Accelerate repeated queries | dashboard latency |
| 5 | Approximate functions | Cut cost on large distinct ops | query cost per run |

The core principle: "never add hints without measuring first." Identify which stage is expensive before acting.

## Query Optimization: Before and After

```sql
-- Before: unnecessary full-column scan
SELECT *
FROM marts.fact_orders
WHERE order_date BETWEEN '2026-01-01' AND '2026-12-31';

-- After: select only needed columns
SELECT order_date, user_key, amount
FROM marts.fact_orders
WHERE order_date BETWEEN '2026-01-01' AND '2026-12-31';
```

This looks trivial, but in a columnar system the cost difference is massive. `SELECT *` often starts as "temporary debugging" and stays as a production query — catch it in code review.

## Execution Plan Interpretation Checklist

When reading an execution plan, check these items in order.

1. Is there a large gap between estimated and actual bytes at the scan stage?
2. Does one side of a join expand excessively?
3. Does spill occur after shuffle?
4. Is the same aggregation recomputed in multiple stages?

Each item points to a different fix. Scan problems call for partition/column changes; shuffle problems call for join-key and data-distribution review.

## Query Guardrails

The YAML below shows an automated cost-anomaly watcher.

```yaml
query_guardrails:
  max_bytes_scanned_gb: 50
  max_runtime_seconds: 120
  notify_channel: "#dw-cost-alert"
  actions:
    - warn_on_pr
    - tag_heavy_query
    - require_review_for_select_star
```

Guardrails remove dependence on individual habits and enforce cost control at the team level. Especially effective during new-analyst onboarding.

## Weekly Query Review Routine

To prevent optimization from becoming an ad-hoc event, establish a regular review cadence.

```yaml
weekly_query_review:
  select_candidates:
    - top_20_by_cost
    - top_20_by_runtime
  checks:
    - select_star_usage
    - partition_filter_presence
    - repeated_heavy_aggregations
  output:
    - action_items
    - owner_assignment
    - due_date
```

A standing review turns performance from a one-off heroic effort into a sustainable team practice.
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

## Answering the Opening Questions

- **What's the best way to find slow queries?**
  - Enabling slow query logs for automatic collection is the most objective approach.
- **What happens to write performance when you create many indexes?**
  - Reads speed up but write and maintenance costs increase — a tradeoff to consider.
- **Should you optimize queries or tune the database first?**
  - Start with queries. Bad queries cannot be saved by tuning alone.
<!-- toc:begin -->
## In this series

- [Data Warehouse 101 (1/10): What Is a Data Warehouse?](./01-what-is-data-warehouse.md)
- [Data Warehouse 101 (2/10): OLTP and OLAP](./02-oltp-and-olap.md)
- [Data Warehouse 101 (3/10): Fact and Dimension](./03-fact-and-dimension.md)
- [Data Warehouse 101 (4/10): Star Schema](./04-star-schema.md)
- [Data Warehouse 101 (5/10): Partition and Clustering](./05-partition-and-clustering.md)
- [Data Warehouse 101 (6/10): ETL and ELT](./06-etl-and-elt.md)
- [Data Warehouse 101 (7/10): BI and Dashboard](./07-bi-and-dashboard.md)
- [Data Warehouse 101 (8/10): Data Mart](./08-data-mart.md)
- **Performance Optimization (current)**
- Warehouse Design Example (upcoming)

<!-- toc:end -->

## References

- [BigQuery — Optimize Query Performance](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
- [Snowflake — Query Performance](https://docs.snowflake.com/en/user-guide/performance-query)
- [Use The Index, Luke](https://use-the-index-luke.com/)
- [Redshift — Query Tuning](https://docs.aws.amazon.com/redshift/latest/dg/c-query-performance.html)

Tags: DataWarehouse, Performance, Optimization, Cost, Analytics

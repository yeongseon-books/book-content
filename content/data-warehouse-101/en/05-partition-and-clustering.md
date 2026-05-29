---
series: data-warehouse-101
episode: 5
title: "Data Warehouse 101 (5/10): Partition and Clustering"
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
  - Partition
  - Clustering
  - Performance
  - Analytics
seo_description: How partitioning and clustering differ, the principle of pruning, and the two axes that make huge tables fast to read.
last_reviewed: '2026-05-15'
---

# Data Warehouse 101 (5/10): Partition and Clustering

Warehouse performance is often less about reading faster than about refusing to read what you do not need. On large fact tables, that one design choice is the difference between a cheap daily dashboard refresh and an expensive full-table scan.

This is the 5th post in the Data Warehouse 101 series.

In this post, we focus on how partitioning and clustering help the engine skip work. The useful mental model is simple: first narrow the chunks, then organize what remains inside each chunk.


![data warehouse 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-warehouse-101/05/05-01-concept-at-a-glance.en.png)
*data warehouse 101 chapter 5 flow overview*
> Partitioning reduces the data scanned by skipping irrelevant partitions; clustering arranges data physically to minimize I/O. Together they make large-table queries cheap.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Partition and Clustering?
- Which signal should the example or diagram make visible for Partition and Clustering?
- What failure should be prevented first when Partition and Clustering reaches a real system?

## Questions this article answers

- What problem does partitioning solve, and what problem does clustering solve?
- How does pruning reduce query cost in practice?
- What should guide your choice of partition key and cluster key?
- What kind of cost does bad partitioning create on a large fact table?
- Why do experienced teams check bytes scanned before almost anything else?

## What You Will Learn

- The definition and effect of *partitioning*
- The definition and effect of *clustering*
- How *pruning* works under the hood
- Five-step hands-on
- Five common pitfalls

## Why It Matters

Warehouse facts often hold *billions of rows*. A daily partition alone lets the engine *skip 95%* of the data — and *cost drops directly*.

> *You do not pay for data you do not read.*

This picture shows how partitioning and clustering shrink query scope and I/O. The key is not to memorize when to use each, but to measure where your queries spend time.

## Key Terms

- **Partition**: A *physical chunk* of a table — usually keyed by *date*.
- **Clustering**: Sorting *within a partition* by frequently queried columns.
- **Pruning**: Picking only the *partitions to scan* based on the WHERE clause.
- **Partition key**: The *column used to split* the table.
- **Cluster key**: The *column used to sort* inside partitions.

## Before/After

**Before**: `WHERE order_date = '2026-05-04'` still scans *the whole table*.

**After**: The same query reads *one daily partition*. *Cost drops 100x*.

## Hands-on: Five Steps

### Step 1 — Define partitioning

```sql
-- BigQuery example
CREATE TABLE fact_orders (
    order_id BIGINT,
    user_key BIGINT,
    amount NUMERIC(12, 2),
    order_date DATE
)
PARTITION BY order_date;
```

### Step 2 — Add clustering

```sql
CREATE TABLE fact_orders (
    order_id BIGINT,
    user_key BIGINT,
    amount NUMERIC(12, 2),
    order_date DATE
)
PARTITION BY order_date
CLUSTER BY user_key;
```

### Step 3 — Query that prunes

```sql
-- Reads only one daily partition
SELECT SUM(amount)
FROM fact_orders
WHERE order_date = '2026-05-04';
```

### Step 4 — Query that defeats pruning

```sql
-- Wrapping order_date in a function disables pruning
SELECT SUM(amount)
FROM fact_orders
WHERE EXTRACT(YEAR FROM order_date) = 2026;
```

### Step 5 — Cluster-key benefit

```sql
-- Add user_key and read even less
SELECT SUM(amount)
FROM fact_orders
WHERE order_date BETWEEN '2026-05-01' AND '2026-05-31'
  AND user_key = 100;
```

## What to Notice in This Code

- The condition must hit the *partition key directly* for pruning.
- Wrapping in a *function* breaks pruning.
- Clustering helps *inside* a partition.


## Partitioning Strategy at a Glance

Partitioning and clustering are not about reading faster — they are about refusing to read what is unnecessary. Choosing the wrong key at design time drastically limits optimization headroom.

| Strategy | Key column | Expected benefit | Watch out for | Best when |
| --- | --- | --- | --- | --- |
| Daily partition | `order_date` | Range-scan cost drops sharply | Too fine = metadata bloat | High-traffic event tables |
| Monthly partition | `order_month` | Simpler management | Day-level queries over-scan | Mid-size logs and aggregates |
| 1 cluster key | `user_key` | Point-filter speedup | High cardinality = expensive re-sort | Frequent user-based lookups |
| 2 cluster keys | `user_key, product_key` | Compound filter improvement | Too many keys = diminishing returns | Frequent drill-down analysis |

The table makes the role division clear: partitions cut large ranges; clustering sorts within those ranges.

## SQL Patterns That Preserve Pruning

One line of SQL can make or break pruning.

```sql
-- Good: direct comparison against the partition key
SELECT SUM(amount)
FROM fact_orders
WHERE order_date BETWEEN '2026-05-01' AND '2026-05-31';

-- Bad: function wrapping can disable pruning
SELECT SUM(amount)
FROM fact_orders
WHERE DATE_TRUNC('month', order_date) = DATE '2026-05-01';
```

The first query lets the engine compute partition boundaries directly, so the read range stays narrow. The second may fall back to a full scan depending on the engine.

## Operational Observability Metrics

To verify your key choices, watch operational metrics. Check at least these on a weekly basis.

```yaml
partition_observability:
  - metric: bytes_scanned_per_query
    target: "decreasing trend"
  - metric: partition_pruning_ratio
    target: ">= 0.8 for date-filtered workloads"
  - metric: avg_query_latency
    target: "stable under peak"
  - metric: recluster_jobs_per_day
    target: "controlled"
```

`partition_pruning_ratio` is an especially strong signal of model-design quality. If a date-filtered query shows a low ratio, revisit either the SQL patterns or the partition key itself.

## Partition DDL in Practice

Below is a DDL pattern common in production workloads.

```sql
CREATE TABLE marts.fact_orders (
    order_id STRING,
    user_key INT64,
    product_key INT64,
    order_date DATE,
    amount NUMERIC,
    quantity INT64,
    created_at TIMESTAMP
)
PARTITION BY order_date
CLUSTER BY user_key, product_key;
```

The key principle: align the partition key with the primary query axis. In most domains the time axis is the most stable choice; pick the second axis based on actual filter frequency.

## Operations Check Table

| Check item | Target | Warning signal |
| --- | --- | --- |
| Partition count growth rate | Predictable | Sudden spike |
| Pruning ratio | Stays high | Low on filtered queries |
| Recluster workload | Stable | Persistently excessive |
| Query cost | Gradual | Specific dashboard spikes |

Attaching this table to a weekly retrospective turns optimization from individual heroics into a team habit.

## Cluster Key Selection Guide

Choose cluster keys by the rule "frequently filtered, rarely mutated." Conversely, columns with high randomness or columns that are almost never used in WHERE clauses should be excluded from the candidate list.
## Five Common Mistakes

1. **Wrapping the partition key in a *function*.** Falls back to *full scan*.
2. **Splitting partitions *too small*.** *Metadata cost* exceeds *read cost*.
3. **Choosing *too many* cluster keys.** *Sort cost* outweighs *read benefit*.
4. **Trusting *indexes alone*.** Warehouses are *not the world of indexes*.
5. **Mutating *historical partitions*.** Triggers an *avalanche of recomputes*.

## How This Shows Up in Production

BigQuery, Snowflake, and Redshift all expose *partition + clustering* as primary tools. *Date partition + user cluster* is the default combo.

## How a Senior Engineer Thinks

- *Make the partition key the *first WHERE clause*.*
- *Document patterns that *break pruning*.*
- *Measure cost in *bytes scanned*.*
- *Use *few, frequently used* cluster keys.*
- *Prefer *append* over *update* of historical partitions.*

## Checklist

- [ ] You can distinguish *partition* from *clustering*.
- [ ] You know patterns that *break pruning*.
- [ ] You know how *cost is measured*.
- [ ] You know how to choose a *partition key*.

## Practice Problems

1. Choose a *partition key* and *cluster key* for *fact_payments*.
2. List *three* queries that *break pruning*.
3. Name *two* downsides of *over-splitting* partitions.

## Wrap-up and Next Steps

Partition and clustering improve *cost and speed* together. Next, we look at *ETL* and *ELT* — how data gets in.

## Answering the Opening Questions

- **What problems arise when querying a large table without partitioning?**
  - Unnecessary data must be fully scanned, causing query time and cost to grow linearly.
- **What column should Clustering be based on?**
  - Choose the most frequently filtered column or join key to minimize I/O.
- **Does changing partition strategy require re-sorting the data?**
  - Many data warehouses provide automatic repartitioning, but cost and time must be considered.
<!-- toc:begin -->
## In this series

- [Data Warehouse 101 (1/10): What Is a Data Warehouse?](./01-what-is-data-warehouse.md)
- [Data Warehouse 101 (2/10): OLTP and OLAP](./02-oltp-and-olap.md)
- [Data Warehouse 101 (3/10): Fact and Dimension](./03-fact-and-dimension.md)
- [Data Warehouse 101 (4/10): Star Schema](./04-star-schema.md)
- **Partition and Clustering (current)**
- ETL and ELT (upcoming)
- BI and Dashboard (upcoming)
- Data Mart (upcoming)
- Performance Optimization (upcoming)
- Warehouse Design Example (upcoming)

<!-- toc:end -->

## References

- [BigQuery — Partitioned Tables](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [BigQuery — Clustered Tables](https://cloud.google.com/bigquery/docs/clustered-tables)
- [Snowflake — Clustering Keys](https://docs.snowflake.com/en/user-guide/tables-clustering-keys)
- [Redshift — Distribution and Sort Keys](https://docs.aws.amazon.com/redshift/latest/dg/c_designing-tables-best-practices.html)

Tags: DataWarehouse, Partition, Clustering, Performance, Analytics

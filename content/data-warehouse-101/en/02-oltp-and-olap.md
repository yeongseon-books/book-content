---
series: data-warehouse-101
episode: 2
title: "Data Warehouse 101 (2/10): OLTP and OLAP"
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
  - OLTP
  - OLAP
  - Database
  - Analytics
seo_description: How OLTP and OLAP workloads differ, why row vs column storage matters, and the case for keeping the two systems separate.
last_reviewed: '2026-05-15'
---

# Data Warehouse 101 (2/10): OLTP and OLAP

From far away, both systems speak SQL. Up close, they solve opposite problems. One is built to confirm a payment in milliseconds. The other is built to scan months of history without dragging production down with it.

This is the 2nd post in the Data Warehouse 101 series.

In this post, we compare those workloads directly. The important question is not whether both systems can run queries, but what kind of query pattern each engine is optimized to carry all day.


![data warehouse 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-warehouse-101/02/02-01-concept-at-a-glance.en.png)
*data warehouse 101 chapter 2 flow overview*
> OLTP and OLAP have opposite optimization goals: OLTP for single-row speed, OLAP for bulk-read throughput. A single engine cannot do both well.

## Questions to Keep in Mind

- How do OLTP and OLAP differ in the workloads they are built to handle?
- Where does the gap between row storage and column storage become most visible?
- Why does one engine become a bad compromise when you ask it to serve both workloads?

## Questions this article answers

- How do OLTP and OLAP differ in the workloads they are built to handle?
- Where does the gap between row storage and column storage become most visible?
- Why does one engine become a bad compromise when you ask it to serve both workloads?
- How should you think about CDC and replication lag in a split architecture?
- What practical criteria do teams use to decide when to separate OLTP from OLAP?

## What You Will Learn

- The workload difference between *OLTP* and *OLAP*
- The trade-offs of *row* vs *column* storage
- Why we *separate* the two systems
- Five-step comparison hands-on
- Five common pitfalls

## Why It Matters

OLTP processes *one record right now* fast. OLAP scans *all of history* in one shot. The *optimization directions are opposite*, so a single engine struggles to be great at both.

> *Pick the right tool. Trying to do both with one makes both unhappy.*

This picture places OLTP and OLAP inside an operating flow. The point is not to memorize the workload difference, but to see how row storage and column storage trade off for different access patterns.

## Key Terms

- **OLTP**: Short, *concurrent* read/write workloads.
- **OLAP**: Large-range, *read-heavy* aggregations.
- **Row store**: Stores *all columns of a row* together.
- **Column store**: Stores *values of one column* contiguously.
- **CDC**: *Change Data Capture* — streaming OLTP changes into OLAP.

## Before/After

**Before**: A single Postgres handles *payments* and *monthly analytics*; both *slow down*.

**After**: OLTP on *Postgres*, OLAP on *BigQuery* — each is *optimized for its job*.

## Hands-on: Five-step Comparison

### Step 1 — OLTP pattern

```sql
-- Update one user's balance
UPDATE accounts SET balance = balance - 1000 WHERE id = 42;
```

### Step 2 — OLAP pattern

```sql
-- Average balance across all users
SELECT AVG(balance) FROM accounts;
```

### Step 3 — Row store cost

```sql
-- Row store reads all columns even if you ask for one
SELECT amount FROM fact_orders;
```

### Step 4 — Column store benefit

```sql
-- Column store scans only the amount column
SELECT SUM(amount) FROM fact_orders;
```

### Step 5 — Separated flow

```sql
-- OLTP receives single-row INSERT
INSERT INTO orders VALUES (...);
-- OLAP analyzes accumulated facts
SELECT date_trunc('day', created_at), COUNT(*) FROM fact_orders GROUP BY 1;
```

## What to Notice in This Code

- *Short queries* are fast on *row stores*.
- *Big aggregations* are fast on *column stores*.
- The *concurrency shape* is *completely different*.

## Fixing the Workload Difference in a Table

A common misconception is "OLTP is a small DB, OLAP is a big DB." The real distinction is the *shape* of the workload, not size. The table below clarifies why the two systems must coexist.

| Aspect | OLTP | OLAP |
| --- | --- | --- |
| Basic unit | Single transaction | Multi-row aggregation |
| Query pattern | `INSERT/UPDATE/SELECT by PK` | `JOIN/GROUP BY/WINDOW` |
| Concurrency | Many short requests | Few long-running queries |
| Storage optimization | Row-oriented | Column-oriented |
| Indexing strategy | Point lookup first | Scan reduction, partition first |
| SLA | Strict p95 latency | Report generation time |
| Data freshness | Near-real-time | Batch or micro-batch |
| Typical failure | Lock contention, deadlocks | Excessive scan, shuffle/spill |

Once you look at the table, it becomes clear why trying to optimize both on a single engine rarely lasts. Optimizing one side becomes the other side's cost.

## Row vs Column Storage in Practice

Row storage keeps read-and-write cost low for single records. Column storage keeps bulk-read cost low for specific columns. The example below shows how the same business question maps to different optimal storage:

```sql
-- OLTP-friendly: check one order's status
SELECT order_id, status, updated_at
FROM orders
WHERE order_id = 987654;

-- OLAP-friendly: monthly revenue aggregation
SELECT date_trunc('month', order_date) AS month,
       SUM(amount) AS revenue
FROM fact_orders
GROUP BY 1
ORDER BY 1;
```

The first query reads multiple columns of a single row — row storage wins. The second scans only `amount` and `date` across millions of rows — column storage wins. Storage layout is determined by the *shape of your questions*, not by technology preference.

## Minimum Separation Policy

When splitting systems, "how far do we separate?" is a common debate. The policy below is a practical minimum even small teams can adopt immediately:

```yaml
separation_policy:
  oltp:
    allowed_queries:
      - point_lookup
      - short_transaction
    blocked_patterns:
      - full_table_scan
      - monthly_aggregation_on_prod
  olap:
    source:
      - cdc_stream
      - daily_snapshot
    freshness_slo: "<= 15 minutes"
  governance:
    owner_oltp: "backend"
    owner_olap: "data"
    incident_channel: "#data-runtime"
```

Pairing this policy with code review rules prevents the common regression where heavy queries creep back onto the operational DB after separation. Operational habits make a bigger difference than technology choice in this zone.

## When a Single Engine Fails — Typical Signals

When these signals appear, deferring OLTP/OLAP separation becomes difficult:

- API latency spikes repeat every month-end or week-end reporting window.
- Adding read replicas does not resolve analytical query bottlenecks.
- Each new index degrades write performance.
- Priority conflicts between batch queries and online transactions grow.

These are not performance problems — they are *architecture boundary* problems. Fixing one query does not help; workload separation must be designed.

## Separation Scenario Example

Consider a hypothetical e-commerce service. OLTP handles order creation, payment approval, and stock deduction. OLAP handles campaign analysis, monthly P&L, and channel conversion rates. When both paths share the same storage and cache, mutual interference peaks during traffic surges.

```yaml
traffic_profile:
  oltp:
    peak_rps: 1200
    typical_query_ms: 20
    write_ratio: 0.55
  olap:
    peak_concurrent_queries: 40
    typical_query_seconds: 8
    scan_size_gb: 12
risk_if_shared:
  - cache_eviction_conflict
  - lock_wait_increase
  - planner_instability
```

After separation, OLTP tunes for low latency and OLAP tunes for bulk reads independently. This split improves not just performance but operational resilience through fault isolation.

## Turning the Comparison Table into a Design Checklist

Do not just read the table and move on — convert it to system review questions for immediate practical use:

- Is the most expensive query currently OLTP-shaped or OLAP-shaped?
- Do incident reports show repeated analytical query interference?
- Has the analytics freshness SLA been agreed in minutes?
- Does the user communication plan reflect data delay post-separation?

If you can answer these questions, the separation decision shifts from technology preference to operational evidence.

## Five Common Mistakes

1. **Running OLAP queries *on OLTP*.** Lock waits pile up and *latency cascades*.
2. **Sending *short transactions* to OLAP.** *Cost goes up, value does not*.
3. **Assuming *zero replication lag*.** Always design for *minutes of lag*.
4. **Copying the *index strategy*.** Access patterns differ — *design indexes separately*.
5. **Sharing a backup policy.** OLTP wants *PITR*; OLAP wants *snapshots*.

## How This Shows Up in Production

Payments live on *Postgres / MySQL*. Revenue reports live on *Snowflake / BigQuery*. Between them, *Debezium*-style *CDC* moves changes with a *small lag*.

## How a Senior Engineer Thinks

- *Start by analyzing the *shape of the workload*.*
- *Be skeptical of doing both with one engine.*
- *Cost is shaped by access patterns.*
- *Treat replication lag as a constant, not a bug.*
- *Design *post-separation consistency* from day one.*

## Checklist

- [ ] You can compare OLTP and OLAP in *three lines*.
- [ ] You know the difference between *row and column store*.
- [ ] You can explain what *CDC* is.
- [ ] You can name the *backup difference* between the two.

## Practice Problems

1. List *three* OLTP workloads.
2. List *three* OLAP workloads.
3. Explain which *queries favor row store*.

## Wrap-up and Next Steps

OLTP and OLAP optimize for opposite directions. Next we cover *facts and dimensions*, the core OLAP modeling unit.

## Answering the Opening Questions

- **What workloads do OLTP and OLAP handle differently?**
  - OLTP targets "this one transaction right now"; OLAP targets "the entire historical dataset."
- **Where does the difference between row storage and column storage become significant?**
  - OLTP needs fast access to all columns of one row, favoring row storage; OLAP mass-scans specific columns, favoring columnar storage.
- **Why is handling both requirements in a single engine problematic?**
  - All optimizations — indexing, memory cache, query planner — conflict, making both workloads slower.
<!-- toc:begin -->
## In this series

- [Data Warehouse 101 (1/10): What Is a Data Warehouse?](./01-what-is-data-warehouse.md)
- **OLTP and OLAP (current)**
- Fact and Dimension (upcoming)
- Star Schema (upcoming)
- Partition and Clustering (upcoming)
- ETL and ELT (upcoming)
- BI and Dashboard (upcoming)
- Data Mart (upcoming)
- Performance Optimization (upcoming)
- Warehouse Design Example (upcoming)

<!-- toc:end -->

## References

- [Wikipedia — OLTP](https://en.wikipedia.org/wiki/Online_transaction_processing)
- [Wikipedia — OLAP](https://en.wikipedia.org/wiki/Online_analytical_processing)
- [Snowflake — Columnar Storage](https://docs.snowflake.com/en/user-guide/intro-key-concepts)
- [Designing Data-Intensive Applications](https://dataintensive.net/)

Tags: DataWarehouse, OLTP, OLAP, Database, Analytics

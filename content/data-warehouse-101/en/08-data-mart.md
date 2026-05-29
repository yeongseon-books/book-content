---
series: data-warehouse-101
episode: 8
title: "Data Warehouse 101 (8/10): Data Mart"
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
  - DataMart
  - Modeling
  - Domain
  - Analytics
seo_description: What a data mart is, how it differs from a warehouse, and why teams keep small domain-specific analytical zones.
last_reviewed: '2026-05-15'
---

# Data Warehouse 101 (8/10): Data Mart

One warehouse rarely means one shared language. Sales, finance, and operations may start from the same source data, but they read it through different questions, different permissions, and different levels of aggregation.

This is the 8th post in the Data Warehouse 101 series.

In this post, we look at data marts as the layer that translates common warehouse assets into domain-ready analytical surfaces. The key is to narrow the interface without breaking the shared definitions underneath.


![data warehouse 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-warehouse-101/08/08-01-concept-at-a-glance.en.png)
*data warehouse 101 chapter 8 flow overview*
> A data mart is a specialized warehouse for one department or purpose. The central definitions stay consistent; each mart adds only what it needs.

## Questions to Keep in Mind

- How is a data mart different from the warehouse itself?
- Why separate organization-wide shared data from team-specific analytical space?
- What gets better when you reflect domain vocabulary directly in the data model?

## What You Will Learn

- The definition of a *data mart*
- How it differs from a *warehouse*
- Why we keep *small zones per domain*
- Five-step mart design hands-on
- Five common pitfalls

## Why It Matters

A warehouse holds *org-wide common data*. But *sales, finance, and ops* speak *different vocabularies*. A mart re-organizes data *in each team's words* — a *thin layer* on top of the warehouse.

> *Common in the warehouse, domain in the mart.*

## Key Terms

- **Data Mart**: A *domain-scoped* analytical zone — a *subset* of the warehouse.
- **Conformed Dimension**: A dimension *shared* across marts.
- **Domain Modeling**: Modeling data with the *team's vocabulary and rules*.
- **Aggregated Mart**: A *pre-aggregated* mart for speed.
- **Self-service**: An interface analysts *use directly*.

## Before/After

**Before**: Sales reads *raw facts* from the warehouse. Joins are *complex* and *slow*.

**After**: A *sales mart* aggregates in *team vocabulary*. Dashboards load in *3 seconds*.

## Hands-on: Mart Design in Five Steps

### Step 1 — Define the domain

```text
"The sales mart sees data at the *opportunity* level. It bundles *customer, stage, amount, owner*."
```

### Step 2 — Use conformed dimensions

```sql
CREATE OR REPLACE TABLE sales_mart.fact_opportunity AS
SELECT
    o.opp_id,
    u.user_key AS owner_key,
    c.customer_key,
    o.stage,
    o.amount,
    o.created_at
FROM staging.opportunities o
JOIN warehouse.dim_user u ON u.user_id = o.owner_id
JOIN warehouse.dim_customer c ON c.customer_id = o.customer_id;
```

## Data Mart Types

Data marts can be classified into three types based on their creation method and data source.

| Type | Data Source | Refresh Method | Best For | Characteristics |
|---|---|---|---|---|
| Dependent | Derived from Warehouse | Auto-reflects Warehouse changes | Large orgs, centralized | Shares conformed dims, high consistency |
| Independent | Extracted directly from OLTP | Team-specific ETL pipeline | Small orgs, fast MVPs | Quick to build but high duplication, low consistency |
| Hybrid | Warehouse + domain-specific sources | Common part from Warehouse, specialized part direct | Mid-size orgs | Balance of flexibility and consistency |

A dependent mart uses the central warehouse's consistent definitions so numbers never diverge between teams. An independent mart is fast to build but hard to integrate later. Hybrid combines the strengths of both.

### Step 3 — Pre-aggregate

```sql
CREATE OR REPLACE TABLE sales_mart.agg_pipeline_by_owner AS
SELECT
    owner_key,
    stage,
    SUM(amount) AS pipeline_amount,
    COUNT(*) AS opp_count
FROM sales_mart.fact_opportunity
GROUP BY 1, 2;
```

## SQL Example: Creating a Mart with CTAS

Below is a CTAS (Create Table As Select) example that physically materializes a mart table.

```sql
CREATE TABLE sales_mart.monthly_pipeline AS
SELECT
    DATE_TRUNC('month', o.created_at) AS month,
    u.region,
    o.stage,
    COUNT(*) AS opp_count,
    SUM(o.amount) AS pipeline_amount,
    AVG(o.amount) AS avg_deal_size
FROM staging.opportunities o
JOIN warehouse.dim_user u ON u.user_key = o.owner_key
WHERE o.created_at >= '2025-01-01'
GROUP BY 1, 2, 3;
```

This mart pre-computes a pipeline summary by month, region, and stage. Dashboards read directly from this table, so response times stay fast.

```sql
-- Mart refresh (daily schedule)
TRUNCATE sales_mart.monthly_pipeline;
INSERT INTO sales_mart.monthly_pipeline
SELECT ...; -- re-run the query above
```

Physically storing the result makes reads fast but requires storage and an explicit refresh schedule. For comparison, here is the same logic as a view:

```sql
-- Same logic defined as a view
CREATE OR REPLACE VIEW sales_mart.monthly_pipeline_view AS
SELECT ...; -- same as above
```

A view has no refresh burden but recomputes on every query, which can be slow.

### Step 4 — Query the mart

```sql
SELECT u.name, SUM(a.pipeline_amount) AS total_pipeline
FROM sales_mart.agg_pipeline_by_owner a
JOIN warehouse.dim_user u ON u.user_key = a.owner_key
WHERE a.stage IN ('proposal', 'negotiation')
GROUP BY u.name;
```

### Step 5 — Separate permissions

```sql
GRANT SELECT ON SCHEMA sales_mart TO ROLE sales_readers;
GRANT SELECT ON SCHEMA finance_mart TO ROLE finance_readers;
```

## What to Notice in This Code

- *Conformed dims* come from the *warehouse*.
- The *team vocabulary* shows up in *column names*.
- Permissions split by *domain*.

## Mart vs View vs Materialized View

Three implementation approaches, each with different trade-offs.

### Table (CTAS)

Physically stored, so reads are fast. Requires storage space and an explicit refresh schedule. Best when dashboards query frequently and data volumes are large.

```sql
CREATE TABLE marts.daily_summary AS SELECT ...;
```

### View

Uses no storage and always returns the latest data. Recomputes on every query, so can be slow. Best when data volumes are small and real-time freshness matters.

```sql
CREATE OR REPLACE VIEW marts.daily_summary AS SELECT ...;
```

### Materialized View

A middle ground that stores results physically while supporting automatic refresh. Supported by BigQuery, Snowflake, PostgreSQL, among others. The warehouse engine manages refresh timing.

```sql
CREATE MATERIALIZED VIEW marts.daily_summary AS SELECT ...;
REFRESH MATERIALIZED VIEW marts.daily_summary;
```

Choose among the three based on data size, query frequency, real-time requirements, and cost constraints.

## Five Common Mistakes

1. **Building *separate dims per mart*.** A common cause of *number conflicts*.
2. **Skipping the warehouse and *building marts first*.** *Conforming later* is *hard*.
3. **Pulling *every column* into the mart.** *Unnecessary cost*.
4. **Skipping *permission splits*.** Risk of *sensitive data exposure*.
5. **Unclear if a mart is a *live SQL* or *materialized copy*.** Document *refresh policy*.

## Data Mart Operating Model

A data mart is not a simple copy — it is a consumer-oriented reorganization layer. When deciding which marts to build, define domain boundaries, owners, and refresh cadence first.

| Mart Type | Purpose | Data Sources | Refresh Cadence | Primary Owner |
|---|---|---|---|---|
| Sales Mart | Pipeline/revenue analysis | Orders, customers, channels | Hourly | Sales analytics |
| Finance Mart | Settlement/P&L verification | Payments, refunds, accounting codes | Daily batch | Finance data team |
| Product Mart | Feature usage analysis | Event logs, experiment data | 15 min–hourly | Product analytics |
| Ops Mart | Operational monitoring | Logistics, SLA, incident events | 5 min–hourly | Operations team |

Making purpose and ownership explicit like this prevents mart schemas from growing unnecessarily large.

## Conformed Dimension Management Principles

When building marts quickly, teams tend to create their own customer or product dimensions. Over time this causes metric conflicts, so a conformed dimension policy is essential.

```yaml
conformed_dimensions:
  dim_customer:
    steward: "data-governance"
    required_keys: [customer_key, customer_id]
    scd_type: 2
  dim_product:
    steward: "commerce-data"
    required_keys: [product_key, product_id]
    scd_type: 1
  dim_date:
    steward: "platform"
    required_keys: [date_key, full_date]
    scd_type: 0
```

The key principle: each mart freely composes its own views, but reference dimensions are managed centrally.

## Mart Build SQL Pattern

A common pattern when building the Sales Mart:

```sql
CREATE OR REPLACE TABLE sales_mart.fact_daily_revenue AS
SELECT
    d.full_date,
    c.segment,
    ch.channel_name,
    SUM(f.amount) AS revenue,
    COUNT(DISTINCT f.order_id) AS orders
FROM warehouse.fact_orders f
JOIN warehouse.dim_date d ON d.date_key = f.date_key
JOIN warehouse.dim_customer c ON c.customer_key = f.customer_key
JOIN warehouse.dim_channel ch ON ch.channel_key = f.channel_key
GROUP BY 1, 2, 3;
```

This pattern provides consumer-level pre-aggregation that simplifies dashboard queries. However, over-aggregation reduces flexibility, so limit it to frequently-asked questions.

## Mart Quality Verification Checks

As marts multiply, automated verification becomes critical. At minimum, check these before deployment:

1. No primary key duplicates
2. Common metric definitions match central standards
3. Refresh delay stays within SLA
4. Permissions align with domain boundaries

When these four hold steady, metric interpretation remains consistent even as marts proliferate.

## Domain Mart Design Example

A data mart reflects the team's question units in its model. For example, finance distinguishes "booked revenue" from "pending settlement," while the product team looks at "revenue per active user" over the same period. So even when sharing the same facts, mart expressions differ.

```sql
CREATE OR REPLACE VIEW finance_mart.v_revenue_settlement AS
SELECT
    d.full_date,
    SUM(CASE WHEN f.status = 'paid' THEN f.amount ELSE 0 END) AS booked_revenue,
    SUM(CASE WHEN f.status = 'pending' THEN f.amount ELSE 0 END) AS pending_revenue
FROM warehouse.fact_orders f
JOIN warehouse.dim_date d ON d.date_key = f.date_key
GROUP BY d.full_date;
```

Safely translating the same data into team vocabulary is the essence of a mart.

## Data Governance Policy

| Policy Item | Description | Responsibility |
|---|---|---|
| Metric definition approval | Governance review required for common metric changes | Data governance |
| Access permissions | Least-privilege based on domain roles | Security/Platform |
| Lineage tracking | Track upstream lineage of mart columns | Data platform |
| Change notification | Breaking changes require advance notice | Mart owner |

Without these policies, metric trust erodes quickly as marts multiply.

## Metadata Management

Mart quality cannot be judged from table data alone. Column descriptions, owners, refresh cadence, and quality status must be managed as metadata so consumers can use the data confidently.

## How This Shows Up in Production

dbt's *marts/* folder is split *by domain*. Sales, finance, product, and marketing each have *their own mart* and pull *common dims* from the warehouse.

## How a Senior Engineer Thinks

- *A mart is the warehouse *rewritten in team vocabulary*.*
- *Conformed dimensions are the *org's constitution*.*
- *Refresh marts *small and often*.*
- *Permissions follow *domain boundaries*.*
- *Track each mart's *lifespan* as a metric.*

## Checklist

- [ ] You can distinguish *warehouse* from *mart*.
- [ ] You can define *conformed dimension*.
- [ ] You see why *permission split* matters.
- [ ] You know the trade-off of *pre-aggregation*.

## Practice Problems

1. Pick *three fact tables* for a *finance mart*.
2. Describe a *conflict scenario* when marts use separate dims.
3. List *two risks* of a mart without *permission split*.

## Wrap-up and Next Steps

A mart is a *thin bridge* between the team and the data. Next, we cover *performance optimization patterns*.

## Answering the Opening Questions

- **How does a Data Mart differ from a Warehouse?**
  - A Warehouse is the enterprise-wide integrated store; a Data Mart is a specialized store for a specific team or use case.
- **Won't data definitions diverge if each team builds their own Data Mart?**
  - Fact and Dimension definitions are managed centrally; selection and combination happen at each Mart.
- **What do you do when a Data Mart grows too large?**
  - Either decompose further by purpose, or return to the Warehouse and redesign the structure.
<!-- toc:begin -->
## In this series

- [Data Warehouse 101 (1/10): What Is a Data Warehouse?](./01-what-is-data-warehouse.md)
- [Data Warehouse 101 (2/10): OLTP and OLAP](./02-oltp-and-olap.md)
- [Data Warehouse 101 (3/10): Fact and Dimension](./03-fact-and-dimension.md)
- [Data Warehouse 101 (4/10): Star Schema](./04-star-schema.md)
- [Data Warehouse 101 (5/10): Partition and Clustering](./05-partition-and-clustering.md)
- [Data Warehouse 101 (6/10): ETL and ELT](./06-etl-and-elt.md)
- [Data Warehouse 101 (7/10): BI and Dashboard](./07-bi-and-dashboard.md)
- **Data Mart (current)**
- Performance Optimization (upcoming)
- Warehouse Design Example (upcoming)

<!-- toc:end -->

## References

- [Kimball — Data Mart](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [dbt — Mart Layer](https://docs.getdbt.com/best-practices/how-we-structure/4-marts)
- [Snowflake — Schema Design](https://docs.snowflake.com/en/user-guide/intro-key-concepts)
- [Wikipedia — Data Mart](https://en.wikipedia.org/wiki/Data_mart)

Tags: DataWarehouse, DataMart, Modeling, Domain, Analytics

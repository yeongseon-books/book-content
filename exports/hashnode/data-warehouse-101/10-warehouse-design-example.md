
# Warehouse Design Example

> Data Warehouse 101 series (10/10)

<!-- a-grade-intro:begin -->

**Core question**: How do we *combine* everything we have learned and *design one warehouse* from scratch?

> *Every good design starts with one line of grain.*

<!-- a-grade-intro:end -->

## What You Will Learn

- An *e-commerce* example designed *end to end*
- The order *grain → dimension → schema → partition → ETL → mart*
- How everything *connects to a dashboard*
- A 5-step design exercise
- Five common mistakes

## Why It Matters

Knowing the parts is not enough — *putting them together* is the real skill. A single domain walkthrough makes it clear *why each piece sits where it sits*. This last episode is the *assembly* episode.

> *All clean designs begin with one line of grain.*

## Concept at a Glance

```mermaid
flowchart LR
    Source["Source Systems"] --> Lake["Data Lake"]
    Lake --> Stage["Staging"]
    Stage --> Fact["fact_orders"]
    Stage --> Dim["dim_user, dim_product, dim_date"]
    Fact --> Mart["mart_sales"]
    Dim --> Mart
    Mart --> BI["Dashboard"]
```

## Key Terms

- **Grain**: what *one row* of a fact table represents. The *starting point* of design.
- **Conformed dimension**: a dimension *shared* across multiple facts.
- **Surrogate key**: a *replacement key* issued by the warehouse, not the source.
- **Slowly Changing Dimension (SCD)**: a method to *record changes* in a dimension over time.
- **Mart**: a topic-specific or team-specific *final model* served to consumers.

## Before / After

**Before**: analysts query the source DB *directly* and rewrite SQL for every report. *Slow, expensive, fragile*.

**After**: the warehouse holds a *star schema*, and analysts build dashboards from *short SQL* against a clean mart.

## Hands-on: 5-step Design

### Step 1 — Define the grain

> *fact_orders grain*: one row per *order*.

### Step 2 — Identify dimensions

```text
dim_user      : user attributes
dim_product   : product attributes
dim_date      : date attributes (year, month, weekday)
dim_channel   : acquisition channel
```

### Step 3 — Write the star schema

```sql
CREATE TABLE fact_orders (
    order_id      STRING,
    order_date    DATE,
    user_key      INT64,
    product_key   INT64,
    channel_key   INT64,
    quantity      INT64,
    amount        NUMERIC
)
PARTITION BY order_date
CLUSTER BY user_key, product_key;
```

### Step 4 — ETL/ELT flow

```text
source.orders  --(append)-->  staging.orders
                              |
                              v
              transform: surrogate keys, SCD type 2
                              |
                              v
                       fact_orders / dim_*
```

### Step 5 — Mart and dashboard

```sql
CREATE OR REPLACE VIEW mart_sales AS
SELECT
    d.year,
    d.month,
    p.category,
    SUM(f.amount) AS revenue
FROM fact_orders f
JOIN dim_date d    ON d.date_key   = f.order_date
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY d.year, d.month, p.category;
```

## What to Notice in This Code

- *One line of grain* anchors the entire design.
- *Surrogate keys* protect the warehouse when sources change.
- The *mart* is *prepared answers* for the dashboard, not raw data.

## Five Common Mistakes

1. **Defining the grain only *verbally*.** Write *one line* in the design doc.
2. **Pushing every column into the *fact*.** Move attributes into *dimensions*.
3. **Reusing *source primary keys*.** Source changes will *break* the warehouse.
4. **Ignoring *SCD*.** Historical analysis quietly *breaks*.
5. **Pointing dashboards at *raw fact tables*.** Any *change* hurts every dashboard.

## How This Shows Up in Production

Data teams write a *one-page design doc* listing *grain, dimensions, partition, owner*. The doc is reviewed, then DDL ships through PR, and an *ETL DAG* is added. Dashboards read *only from marts*, never from raw fact tables.

## How a Senior Engineer Thinks

- Define the *grain first*.
- Share *conformed dimensions* across the whole org.
- Keep a *clear boundary* between *fact/dim* and *mart*.
- Never create a table without an *owner*.
- A design *without docs* is *no design at all*.

## Checklist

- [ ] I can write the *grain* in one sentence.
- [ ] I understand *conformed dimensions*.
- [ ] I can write a *star schema* DDL.
- [ ] I can explain the difference between a *mart* and a *fact*.

## Practice Problems

1. Write the grain and dimensions for a *blog comment system*.
2. Design *fact_clicks* for an *ad click log*.
3. Write a *mart view* SQL for a *monthly revenue dashboard*.

## Wrap-up and Next Steps

You can now see a warehouse *as one flow*, from *grain to dashboard*. The next series moves into *Data Science* and *MLOps* — where this warehouse becomes the *training ground* for models.

- [What Is a Data Warehouse?](./01-what-is-data-warehouse.md)
- [OLTP and OLAP](./02-oltp-and-olap.md)
- [Fact and Dimension](./03-fact-and-dimension.md)
- [Star Schema](./04-star-schema.md)
- [Partition and Clustering](./05-partition-and-clustering.md)
- [ETL and ELT](./06-etl-and-elt.md)
- [BI and Dashboard](./07-bi-and-dashboard.md)
- [Data Mart](./08-data-mart.md)
- [Performance Optimization](./09-performance-optimization.md)
- **Warehouse Design Example (current)**
## References

- [Kimball Group — Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [BigQuery — Schema Design Best Practices](https://cloud.google.com/bigquery/docs/best-practices-schema-design)
- [dbt — How We Structure Our Projects](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview)
- [Snowflake — Table Design Considerations](https://docs.snowflake.com/en/user-guide/table-considerations)

Tags: DataWarehouse, Design, Example, EndToEnd, Analytics

---

© 2026 YeongseonBooks. All rights reserved.

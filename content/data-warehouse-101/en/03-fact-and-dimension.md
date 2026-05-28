---
series: data-warehouse-101
episode: 3
title: "Data Warehouse 101 (3/10): Fact and Dimension"
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
  - Fact
  - Dimension
  - Modeling
  - Analytics
seo_description: The roles of fact and dimension tables, why we separate measures from attributes, and the base unit of analytical modeling.
last_reviewed: '2026-05-15'
---

# Data Warehouse 101 (3/10): Fact and Dimension

Most analytical questions hide the same structure: how much happened, and by which slice do you want to explain it? The moment you mix those two jobs in one wide table, every later change becomes more expensive than it needs to be.

This is the 3rd post in the Data Warehouse 101 series.

In this post, we split measures from attributes on purpose. That separation is what keeps aggregations stable, lets context evolve without rewriting history, and gives the warehouse a reusable modeling vocabulary.


![data warehouse 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-warehouse-101/03/03-01-concept-at-a-glance.en.png)
*data warehouse 101 chapter 3 flow overview*
> A fact table records immutable events; dimension tables define how to view them. This separation makes schema changes cheaper and queries more readable.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Fact and Dimension?
- Which signal should the example or diagram make visible for Fact and Dimension?
- What failure should be prevented first when Fact and Dimension reaches a real system?

## Questions this article answers

- What do fact tables and dimension tables each hold?
- What do you gain by separating measures from descriptive attributes?
- Why do you need to define the grain first in an analytical model?
- Why do surrogate keys and conformed dimensions appear so often in warehouse design?
- What is the first sentence you should write before you start OLAP modeling?

## What You Will Learn

- The definition of a *fact* table
- The definition of a *dimension* table
- Why this separation pays off
- Five-step modeling hands-on
- Five common pitfalls

## Why It Matters

Analytical questions almost always read as *how much (measure)* by *which slice (dimension)*. Separating the two lets *aggregations stay fast* and *attribute changes stay flexible*.

> *Split measures from attributes. Together they slow each other down.*

This picture shows how Fact and Dimension tables work together inside a warehouse. The key is not to memorize the definitions, but to see which table records events and which records context.

## Key Terms

- **Fact**: A *measurable event*. Amount, quantity, duration — numbers.
- **Dimension**: The *context* of a fact. User, product, date — attributes.
- **Grain**: What *one row represents* — the *atomic unit* of the fact.
- **Surrogate key**: An *internal identifier* for a dimension.
- **Conformed dimension**: A dimension *shared* across multiple facts.

## Before/After

**Before**: One *order row* contains *user name and product name*. If a name changes, *every row must be updated*.

**After**: User name lives in *dim_user* only. *Facts stay untouched*.

## Hands-on: Modeling in Five Steps

### Step 1 — Build a dimension

```sql
CREATE TABLE dim_user (
    user_key BIGINT PRIMARY KEY,
    user_id BIGINT,
    name TEXT,
    country TEXT
);
```

### Step 2 — Date dimension

```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE,
    year INT,
    month INT,
    day_of_week INT
);
```

### Step 3 — Build a fact

```sql
CREATE TABLE fact_orders (
    order_id BIGINT,
    user_key BIGINT,
    date_key INT,
    amount NUMERIC(12, 2),
    qty INT
);
```

### Step 4 — Join for analysis

```sql
SELECT u.country, SUM(f.amount) AS revenue
FROM fact_orders f
JOIN dim_user u ON u.user_key = f.user_key
GROUP BY u.country;
```

### Step 5 — Time axis analysis

```sql
SELECT d.year, d.month, SUM(f.amount) AS revenue
FROM fact_orders f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year, d.month
ORDER BY 1, 2;
```

## What to Notice in This Code

- The *fact carries only thin numbers*.
- The *dimension carries meaningful attributes*.
- Multiple facts *share* the same dimension.

## Five Common Mistakes

1. **Putting *string attributes* directly in the fact.** Storage explodes when rows reach *hundreds of millions*.
2. **Mixing *grain*.** Combining *order-level* and *line-item* in one fact makes *aggregations lie*.
3. **Using *natural keys only*.** When upstream keys change, *every fact wobbles*.
4. **Skipping the *date dimension*.** *Weekend / holiday* analyses become *painful*.
5. **Putting *measures* in the dimension.** Meaning blurs and the team gets confused.

## How This Shows Up in Production

E-commerce ships *fact_orders, fact_payments, fact_refunds* and *shares* dim_user, dim_product, dim_date. When a user *changes country*, only dim_user is updated.

## How a Senior Engineer Thinks

- *You should be able to write the *grain* in a single sentence.*
- *Treat conformed dimensions as *team assets*.*
- *Use surrogate keys to *absorb upstream change*.*
- *The date dimension is the *spine of all analytics*.*
- *Facts are *narrow and long*; dimensions are *wide and short*.*

## Checklist

- [ ] You can distinguish *fact* from *dimension*.
- [ ] You can write the *grain* in one sentence.
- [ ] You know why *surrogate keys* matter.
- [ ] You see the value of a *date dimension*.

## Practice Problems

1. Write the *grain* of *fact_payments* in one sentence.
2. List *five* columns for *dim_product*.
3. Name *three* downsides of skipping *surrogate keys*.

## Wrap-up and Next Steps

Splitting facts and dimensions is the *starting point* of analytical modeling. Next, we cover the *star schema* — the most common shape.

## Answering the Opening Questions

- **How do you distinguish Fact from Dimension?**
  - Fact is "what happened" (event rows); Dimension is "from which perspective" (attribute collections).
- **What problems arise when a Fact table grows too large?**
  - Joins, indexing, and query performance all degrade, requiring partitioning or aggregate tables.
- **How do you track changes in Dimension tables?**
  - Choose an SCD (Slowly Changing Dimension) strategy: Type 1 (overwrite), Type 2 (versioning), or Type 3 (parallel columns).
<!-- toc:begin -->
## In this series

- [Data Warehouse 101 (1/10): What Is a Data Warehouse?](./01-what-is-data-warehouse.md)
- [Data Warehouse 101 (2/10): OLTP and OLAP](./02-oltp-and-olap.md)
- **Fact and Dimension (current)**
- Star Schema (upcoming)
- Partition and Clustering (upcoming)
- ETL and ELT (upcoming)
- BI and Dashboard (upcoming)
- Data Mart (upcoming)
- Performance Optimization (upcoming)
- Warehouse Design Example (upcoming)

<!-- toc:end -->

## References

- [Kimball — Fact Table Design](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [dbt — Dimensional Modeling](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview)
- [Snowflake — Star Schema](https://docs.snowflake.com/en/user-guide/intro-key-concepts)
- [BigQuery — Schema Design](https://cloud.google.com/bigquery/docs/schemas)

Tags: DataWarehouse, Fact, Dimension, Modeling, Analytics

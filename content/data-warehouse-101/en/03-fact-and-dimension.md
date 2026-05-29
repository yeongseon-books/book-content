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

- What do fact tables and dimension tables each hold?
- Why do you need to define the grain first in an analytical model?
- What happens when you skip surrogate keys and rely on natural keys alone?

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

## Making the Design Concrete with DDL

The reason for separating fact and dimension is not "normalization is good" — it is that *measures* and *context* change on different schedules. The order amount is fixed at event time, but user tier or product category evolves. Mixing them in one table makes historical replay expensive.

Below is a minimal star schema DDL:

```sql
CREATE TABLE dim_customer (
    customer_key BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    customer_name TEXT,
    segment TEXT,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    is_current BOOLEAN
);

CREATE TABLE dim_product (
    product_key BIGINT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    category TEXT,
    brand TEXT,
    unit_price NUMERIC(12, 2)
);

CREATE TABLE fact_sales (
    sales_id BIGINT,
    customer_key BIGINT,
    product_key BIGINT,
    order_date_key INT,
    quantity INT,
    amount NUMERIC(12, 2)
);
```

The rule: fact holds only measures and foreign keys; human-readable attributes go into dimensions. This boundary keeps queries simple and change impact local.

## Why Grain Comes First

The first thing a model review should check is the grain declaration. For example: "fact_sales is one row per order-product line." Once that sentence exists, the next questions answer themselves:

- Is `amount` the order total or the line amount?
- Is `discount` per order or per line?
- Are returns negative rows in the same grain?

Without a grain declaration, different aggregations on the same table produce conflicting metrics.

## SCD Strategy Decision Table

Tracking dimension changes is not a bolt-on option — it is an initial design decision.

| Strategy | Storage | Advantage | Disadvantage | Best for |
| --- | --- | --- | --- | --- |
| Type 1 | Overwrite current value | Simple, low storage cost | Historical state lost | Typo fixes, non-critical attributes |
| Type 2 | Add versioned rows | Full historical replay | Join conditions grow complex | Customer tier, org changes |
| Type 3 | Previous-value column | Easy recent comparison | Breaks on multiple changes | Limited before/after analysis |

For e-commerce customer segment history, Type 2 is effectively the default. For product description typo fixes, Type 1 is enough.

## Patterns for Consistent Analysis Queries

Even a well-designed dimension model produces inconsistent results without query writing rules. Fix these as team conventions:

1. Date axis always joins through `dim_date`.
2. Metric formulas are defined once in the mart layer.
3. Direct fact queries are allowed for exploration, but final reports use marts only.

Following these rules largely eliminates the "same revenue, different numbers across dashboards" problem.

## Fact/Dimension Quality Validation

As the model grows, "definition correct but data wrong" problems increase. Running validation SQL on a schedule catches quality issues early:

```sql
-- Orphan foreign key check
SELECT COUNT(*) AS orphan_rows
FROM fact_sales f
LEFT JOIN dim_customer c ON c.customer_key = f.customer_key
WHERE c.customer_key IS NULL;

-- Negative amount check
SELECT COUNT(*) AS bad_amount_rows
FROM fact_sales
WHERE amount < 0;
```

These checks belong in the deployment pipeline as quality gates, not as one-off queries. The orphan key check, in particular, immediately exposes dimension load order errors.

## Dimension Change Policy as Code

```yaml
dimension_change_policy:
  dim_customer:
    scd: type2
    business_keys: [customer_id]
    mutable_columns: [segment, tier]
  dim_product:
    scd: type1
    business_keys: [product_id]
    mutable_columns: [name, category]
```

When the policy is explicit, teams stop debating "which column changes should be tracked as history." Model reliability comes from consistency of change rules, not from the number of tables.

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

- **What do fact tables and dimension tables each hold?**
  - Fact tables hold measurable events (numbers); dimension tables hold the descriptive context (attributes) by which those numbers are sliced.
- **Why do you need to define the grain first?**
  - Without a grain declaration, the same table produces conflicting aggregations and teams lose trust in the numbers.
- **What happens when you skip surrogate keys?**
  - Upstream key changes propagate into every fact row, breaking historical consistency and complicating backfills.
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

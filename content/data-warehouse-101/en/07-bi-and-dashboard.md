---
series: data-warehouse-101
episode: 7
title: BI and Dashboard
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
  - BI
  - Dashboard
  - Visualization
  - Analytics
seo_description: The role of BI tools and dashboards, what makes a good dashboard, and the visualization principles that turn numbers into decisions.
last_reviewed: '2026-05-15'
---

# BI and Dashboard

Warehouses do not create decisions by themselves. Teams still need a screen that turns a broad question into one number, one comparison, and one obvious next drill-down. When that layer is noisy, even clean data models feel useless.

This is post 7 in the Data Warehouse 101 series.

In this post, we move from storage to consumption. The focus is on how metric definitions, dashboard layout, and drill-down order determine whether a chart becomes an operating tool or just another report no one trusts.

## What You Will Learn

- The role of *BI tools*
- What makes a *good dashboard*
- Visualization principles that turn *numbers into decisions*
- Five-step dashboard design hands-on
- Five common pitfalls

## Why It Matters

BI is the *last centimeter* of a warehouse. You can model *billions of rows* perfectly, but if the *dashboard is noisy*, *no decision is made*. A great dashboard turns a *one-line question* into a *one-screen answer*.

> *A dashboard's success is measured in *decisions made*, not in *opens*.*

## Concept at a Glance

![BI decision flow](../../../assets/data-warehouse-101/07/07-01-concept-at-a-glance.en.png)

*Warehouse data becomes a team decision only after semantic definitions, BI tooling, and dashboard design line up.*

## Key Terms

- **BI Tool**: Tableau, Looker, Power BI — *visualization tools*.
- **Semantic Layer**: A shared layer of *metric definitions*.
- **KPI**: A *key performance indicator* — measured in one line.
- **Drill-down**: Moving from *summary* to *detail*.
- **Refresh cadence**: How *often* a dashboard updates.

## Before/After

**Before**: The *same metric* shows *different numbers* per team. Meetings end in *number negotiation*.

**After**: One *semantic layer* defines metrics. Everyone sees *the same revenue*.

## Hands-on: Dashboard Design in Five Steps

### Step 1 — Define the question

```text
"How much did this month's revenue grow *vs last month*?"
```

### Step 2 — Confirm the model

```sql
SELECT date_trunc('month', order_date) AS month,
       SUM(amount) AS revenue
FROM marts.fact_orders
GROUP BY 1;
```

### Step 3 — KPI cards

```text
- This month revenue: $1,200,000
- vs last month: +12%
- vs same month last year: +35%
```

### Step 4 — Trend chart

```sql
-- 12-month trend
SELECT date_trunc('month', order_date) AS month,
       SUM(amount) AS revenue
FROM marts.fact_orders
WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY 1
ORDER BY 1;
```

### Step 5 — Drill-down

```sql
-- Contribution by category
SELECT p.category, SUM(f.amount) AS revenue
FROM marts.fact_orders f
JOIN marts.dim_product p ON p.product_key = f.product_key
WHERE f.order_date >= date_trunc('month', CURRENT_DATE)
GROUP BY p.category
ORDER BY revenue DESC;
```

## What to Notice in This Code

- One screen answers *one question*.
- Three layers — *KPI → trend → drill-down*.
- All numbers come from *one model*.

## Five Common Mistakes

1. **Too many charts.** *Three to five* per screen is the right balance.
2. **Metric definitions *vary by dashboard*.** Unify via *semantic layer*.
3. **No *comparison baseline*.** Numbers without *vs prior period* are *useless*.
4. **Colors lose meaning.** Stick to *red = bad*, *green = good*.
5. **Too many *decimal places*.** Round for *readability*.

## How This Shows Up in Production

Quarterly review slides start with a *dashboard screenshot*. *Looker / Tableau* dashboards back *product decisions*. Metric definitions live in *code* such as dbt metrics.

## How a Senior Engineer Thinks

- *Dashboards start from a *question*.*
- *The semantic layer is the org's *common language*.*
- *Numbers without comparison are *empty*.*
- *Limit KPIs to *three or fewer*.*
- *Track dashboard *usage*.*

## Checklist

- [ ] You can define *semantic layer*.
- [ ] You can name *three traits* of a good dashboard.
- [ ] You distinguish *KPI*, *trend*, and *drill-down*.
- [ ] You see why *baselines* matter.

## Practice Problems

1. Pick *three KPIs* for *your team's dashboard*.
2. *Simplify* a dashboard with too many charts.
3. Describe a *metric-definition conflict* you resolved.

## Wrap-up and Next Steps

BI is the *face of the warehouse*. Next we cover *data marts* — analytics scoped to a domain.

<!-- toc:begin -->
- [What Is a Data Warehouse?](./01-what-is-data-warehouse.md)
- [OLTP and OLAP](./02-oltp-and-olap.md)
- [Fact and Dimension](./03-fact-and-dimension.md)
- [Star Schema](./04-star-schema.md)
- [Partition and Clustering](./05-partition-and-clustering.md)
- [ETL and ELT](./06-etl-and-elt.md)
- **BI and Dashboard (current)**
- Data Mart (upcoming)
- Performance Optimization (upcoming)
- Warehouse Design Example (upcoming)
<!-- toc:end -->

## References

- [Looker — Semantic Layer](https://cloud.google.com/looker/docs/intro)
- [Tableau — Visual Best Practices](https://www.tableau.com/learn/articles/data-visualization-tips)
- [Power BI — Star Schema](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
- [dbt — Semantic Layer](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl)

Tags: DataWarehouse, BI, Dashboard, Visualization, Analytics

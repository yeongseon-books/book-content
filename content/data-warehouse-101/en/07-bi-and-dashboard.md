---
series: data-warehouse-101
episode: 7
title: "Data Warehouse 101 (7/10): BI and Dashboard"
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

# Data Warehouse 101 (7/10): BI and Dashboard

Warehouses do not create decisions by themselves. Teams still need a screen that turns a broad question into one number, one comparison, and one obvious next drill-down. When that layer is noisy, even clean data models feel useless.

This is the 7th post in the Data Warehouse 101 series.

In this post, we move from storage to consumption. The focus is on how metric definitions, dashboard layout, and drill-down order determine whether a chart becomes an operating tool or just another report no one trusts.


![data warehouse 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-warehouse-101/07/07-01-concept-at-a-glance.en.png)
*data warehouse 101 chapter 7 flow overview*
> BI is the process of turning data into decisions; a dashboard is one medium for that communication. Good dashboards start with the right question, not the available data.

## Questions to Keep in Mind

- What boundary should you inspect first when applying BI and Dashboard?
- Which signal should the example or diagram make visible for BI and Dashboard?
- What failure should be prevented first when BI and Dashboard reaches a real system?

## Questions this article answers

- Why do different teams reach different conclusions even when they look at the same number?
- What role should BI tools play, and what role should dashboards play?
- What question structure does a good dashboard need?
- In what order should KPI, trend, and drill-down appear on the screen?
- When a dashboard keeps failing, is the problem often the design rather than the data?

## What You Will Learn

- The role of *BI tools*
- What makes a *good dashboard*
- Visualization principles that turn *numbers into decisions*
- Five-step dashboard design hands-on
- Five common pitfalls

## Why It Matters

BI is the *last centimeter* of a warehouse. You can model *billions of rows* perfectly, but if the *dashboard is noisy*, *no decision is made*. A great dashboard turns a *one-line question* into a *one-screen answer*.

> *A dashboard's success is measured in *decisions made*, not in *opens*.*

This picture shows how BI connects warehouse data to business action. The key is not to memorize dashboard tool features, but to understand which metrics matter and why.

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


## BI Tool Comparison

Dashboard quality depends not just on screen design but also on the semantic model, permission policies, and cache strategies the tool provides. Below is a comparison of criteria commonly reviewed in practice.

| Tool | Strength | Weakness | Best fit |
| --- | --- | --- | --- |
| Looker | Semantic layer, strong governance | Steep initial modeling curve | Orgs where metric-definition consistency is critical |
| Tableau | High visual exploration freedom | Risk of scattered metric definitions | Analyst-driven exploration culture |
| Power BI | M365 integration, easy deployment | Large-scale model complexity management | Microsoft-ecosystem orgs |
| Metabase | Quick adoption, simple self-service | Governance limits at scale | Early-stage teams, lightweight reporting |

No tool is the answer — the choice should match the team's question structure and operating model. If metric-definition conflicts are frequent, prioritize semantic-layer support.

## Eight Dashboard Design Principles

Good dashboards optimize for interpretation speed, not information density.

1. Limit first-screen KPIs to about three.
2. Always attach a comparison baseline to numbers (prior month, same month last year, target).
3. Keep color meaning consistent across all pages.
4. Design drill-down paths in one direction: top to bottom.
5. State units (currency, %, count) near the title.
6. Expose refresh cadence and last-updated timestamp.
7. Set filter defaults to match real usage scenarios.
8. Provide definition tooltips for metrics that require interpretation.

These principles improve decision speed regardless of visual polish.

## Managing the Semantic Layer as Code

When metric definitions live only in documents, they drift across dashboards over time. The YAML below is a minimal example of managing metrics in code.

```yaml
metrics:
  - name: monthly_revenue
    expression: "SUM(amount)"
    grain: "month"
    owner: "finance-analytics"
    filters:
      - "status = 'paid'"
  - name: active_buyers_30d
    expression: "COUNT(DISTINCT user_key)"
    grain: "day"
    owner: "growth-analytics"
    filters:
      - "order_date >= CURRENT_DATE - 30"
```

Storing definitions in a repository enables review, history tracking, and deployment automation — and eliminates the "whose number is correct?" debate.

## Dashboard Incident Response Criteria

Dashboards look like read-only screens but are operational assets. A minimum response baseline is necessary.

- When p95 render time exceeds the threshold, inspect the query plan first.
- When a metric-mismatch report arrives, verify definition conflicts before editing SQL.
- Before shortening cache-expiry policies, evaluate usage timing and cost together.
- For low-usage dashboards, redefine the question before deleting — then rebuild.
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

## Answering the Opening Questions

- **How do you select which metrics to display on a dashboard?**
  - Prioritize metrics directly tied to business goals and actionable.
- **Where do you start checking when dashboard queries are slow?**
  - Query performance first, then caching strategy, finally UI rendering order.
- **What's the difference between real-time and batch dashboards?**
  - Real-time is higher cost but current information; batch is lower cost but introduces delay.
<!-- toc:begin -->
## In this series

- [Data Warehouse 101 (1/10): What Is a Data Warehouse?](./01-what-is-data-warehouse.md)
- [Data Warehouse 101 (2/10): OLTP and OLAP](./02-oltp-and-olap.md)
- [Data Warehouse 101 (3/10): Fact and Dimension](./03-fact-and-dimension.md)
- [Data Warehouse 101 (4/10): Star Schema](./04-star-schema.md)
- [Data Warehouse 101 (5/10): Partition and Clustering](./05-partition-and-clustering.md)
- [Data Warehouse 101 (6/10): ETL and ELT](./06-etl-and-elt.md)
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

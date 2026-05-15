---
series: sql-101
episode: 10
title: Practical Analysis SQL
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - SQL
  - Analytics
  - Cohort
  - Funnel
  - Retention
seo_description: Cohort, funnel, retention, top-N — patterns for assembling real analytical reports from one SQL file using everything you have learned.
last_reviewed: '2026-05-15'
---

# Practical Analysis SQL

By the time you reach real reporting work, SQL features stop appearing one at a time. A single analytics request usually asks for filtering, grouping, window calculations, and layered intermediate steps in the same query.

That is why the final chapter is best approached as pattern assembly. The goal is not to learn one more clause. It is to see how familiar building blocks combine into the shapes teams actually reuse for dashboards and decision-making.

This is the final post in the SQL 101 series. It ties the earlier clauses together into practical query patterns for analysis work.

## Questions this chapter answers

- What do DAU, WAU, and MAU queries usually look like?
- How do you structure cohort and retention logic in layers?
- What is the cleanest shape for a funnel query?
- Why are window functions a natural fit for top-N per group?
- Which verification steps keep analytical SQL from drifting into misleading metrics?

> Analytical SQL is not a new kind of magic. It is the same familiar tools stacked in layers and named clearly enough for a team to reuse.

## Why It Matters

Most analytics requests are variations on a small set of patterns: active users, retention, conversion, top performers, and trend changes over time. Once those shapes become familiar, new requests stop starting from a blank screen.

Well-structured analytics SQL also becomes reusable team knowledge. A clean cohort query or funnel query does not just answer one ticket. It becomes the basis for dashboards, models, and later reviews about whether the metric definition is still correct.

## Analytics query layering flow

![Analytics query layering flow](../../../assets/sql-101/10/10-01-analytics-query-layering-flow.en.png)
## Key Terms

- **DAU/WAU/MAU**: daily / weekly / monthly *active users*.
- **Cohort**: users who *signed up at the same time*.
- **Retention**: percent of cohort active *N days later*.
- **Funnel**: conversion rate per *step*.
- **Top-N per group**: the *top N* rows *within each group*.

## Before/After

**Before**: Every new request becomes a *new query from scratch*.

**After**: You assemble templates for *cohort, funnel, retention*.

## Hands-on: Five Patterns

### Step 1 — DAU

```sql
SELECT event_at::date AS day, COUNT(DISTINCT user_id) AS dau
FROM events
GROUP BY day
ORDER BY day;
```

### Step 2 — Cohort retention

```sql
WITH cohort AS (
    SELECT user_id, MIN(event_at)::date AS cohort_day FROM events GROUP BY user_id
),
activity AS (
    SELECT e.user_id, c.cohort_day,
        (e.event_at::date - c.cohort_day) AS day_n
    FROM events e JOIN cohort c USING (user_id)
)
SELECT cohort_day, day_n, COUNT(DISTINCT user_id) AS users
FROM activity
GROUP BY cohort_day, day_n
ORDER BY cohort_day, day_n;
```

### Step 3 — Funnel

```sql
SELECT
    COUNT(DISTINCT user_id) FILTER (WHERE step = 'view')   AS s1_view,
    COUNT(DISTINCT user_id) FILTER (WHERE step = 'cart')   AS s2_cart,
    COUNT(DISTINCT user_id) FILTER (WHERE step = 'pay')    AS s3_pay
FROM events;
```

**Expected output:**

| s1_view | s2_cart | s3_pay |
| --- | --- | --- |
| 1200 | 420 | 180 |

### Step 4 — Top-N per group

```sql
WITH ranked AS (
    SELECT product_id, total,
        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY total DESC) AS rk
    FROM orders
)
SELECT * FROM ranked WHERE rk <= 3;
```

### Step 5 — Month-over-month growth

```sql
WITH monthly AS (
    SELECT DATE_TRUNC('month', day) AS month, SUM(revenue) AS rev
    FROM daily_revenue GROUP BY month
)
SELECT month, rev,
    rev - LAG(rev) OVER (ORDER BY month) AS diff,
    (rev - LAG(rev) OVER (ORDER BY month)) * 100.0
        / NULLIF(LAG(rev) OVER (ORDER BY month), 0) AS mom_pct
FROM monthly;
```

## Verification checks before you trust the metric

Analytical SQL should be treated like logic you can audit, not just a query that happened to run.

- **Check the definition first.** Confirm what counts as an active user, a cohort start, or a funnel step before comparing numbers.
- **Check row counts at each layer.** CTE boundaries are the easiest places to confirm whether the dataset is shrinking or expanding as expected.
- **Check the time boundary.** Timezone handling can move daily and monthly metrics enough to invalidate a dashboard.

## Troubleshooting patterns for real reports

| Symptom | First thing to verify | Common fix |
| --- | --- | --- |
| DAU looks lower than expected | Event definition and timezone cutoff | Align the metric definition and date truncation logic |
| Funnel conversion looks too good | Whether users are counted out of chronological order | Add explicit time-order checks between steps |
| Retention shifts after a model change | Cohort definition and deduplication logic | Recheck the cohort layer before blaming the chart |

## What to Notice in This Code

- `DISTINCT user_id` is the standard expression for *active users*.
- `FILTER (WHERE ...)` puts a funnel *on a single line*.
- `NULLIF` prevents *divide-by-zero*.

## Five Common Mistakes

1. **Active definition varies between teams.** Without docs, the *numbers diverge*.
2. **Skipping timezone handling.** Mixing UTC and local time *shifts dates*.
3. **Vague cohort definition.** *Signup* vs *first payment* must be *explicit*.
4. **Funnel ignores time order.** Steps must be *checked chronologically*.
5. **Forgetting NULLIF.** Division by *prior zero* errors out.

## How This Shows Up in Production

Analytics teams maintain a *pattern library* of these queries. With PR review and tools like *dbt*, they become *reusable models*. Behind every dashboard line is *dozens of lines of validated SQL*.

## How a Senior Engineer Thinks

- *Analytics SQL is a *team asset* — document it.*
- *Agree on definitions (active, cohort) *first*.*
- *Always be explicit about timezones.*
- *Build layers with windows and CTEs.*
- *MoM/YoY uses NULLIF by default.*

## Checklist

- [ ] I can write DAU in one line.
- [ ] I can write cohort retention in two steps.
- [ ] I can write a funnel using FILTER.
- [ ] I can write top-N per group with ROW_NUMBER.

## Practice Problems

1. Write *Weekly Active Users (WAU)*.
2. Add *step-to-step conversion rates* to a funnel.
3. Produce a MoM growth table you can chart.

## Wrap-up and Next Steps

Closing the series: *SQL is the shared language of reads, writes, and analytics*. Next stops: *deeper query plans*, *running PostgreSQL*, and *data warehouses*.

<!-- toc:begin -->
## In this series

- [What Is SQL?](./01-what-is-sql.md)
- [SELECT Basics](./02-select-basics.md)
- [WHERE and Conditions](./03-where-and-conditions.md)
- [JOIN](./04-join.md)
- [GROUP BY and Aggregates](./05-group-by-and-aggregate.md)
- [Subquery](./06-subquery.md)
- [Window Function](./07-window-function.md)
- [INSERT, UPDATE, DELETE](./08-insert-update-delete.md)
- [Index and Query Plan](./09-index-and-query-plan.md)
- **Practical Analysis SQL (current)**

<!-- toc:end -->

## References

- [Mode — Advanced SQL](https://mode.com/sql-tutorial/)
- [PostgreSQL — Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html)
- [dbt — Analytics Engineering](https://docs.getdbt.com/)
- [Looker — Block Library](https://cloud.google.com/looker/docs)
- [PostgreSQL — Aggregate Functions](https://www.postgresql.org/docs/current/functions-aggregate.html)

Tags: SQL, Database, Postgres, Analytics

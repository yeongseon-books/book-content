---
series: pandas-101
episode: 6
title: "Pandas 101 (6/10): Groupby and Aggregation"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Pandas
  - GroupBy
  - Aggregation
  - DataAnalysis
  - Beginner
seo_description: Understand groupby through split-apply-combine and master agg, transform, and filter — the three faces of Pandas grouping
last_reviewed: '2026-05-15'
---

# Pandas 101 (6/10): Groupby and Aggregation

Analysis almost never ends with reading a table. Sooner or later you need sales by city, conversion rate by segment, or monthly KPI summaries. That is why `groupby` is not just another Pandas method. It is one of the main ways raw tables become decisions.

This is post 6 in the Pandas 101 series.

In this chapter, we will frame `groupby` as the split-apply-combine workflow. That gives you a clearer mental model for when to reach for `agg`, `transform`, or `filter`.

## Questions to Keep in Mind

- The *split-apply-combine* model?
- The difference between *agg / transform / filter?
- Multi-key grouping?

## Big Picture

![pandas 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/06/06-01-concept-at-a-glance.en.png)

*pandas 101 chapter 6 flow overview*

This picture places Groupby and Aggregation inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Groupby and Aggregation is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why It Matters

*Aggregation is the core of analysis*. With *groupby*, *dozens of for-loop lines* collapse into *one*.

## Concept at a Glance

## Key Terms

- **groupby**: *split into groups* by key.
- **agg**: *reduce to one value* per group.
- **transform**: return per-group computation in *original shape*.
- **filter**: keep rows by a *group-level condition*.
- **as_index**: decides whether the *group key* becomes the *index*.

## Before/After

**Before**: *"For-loop over categories"* — slow and long.

**After**: *"groupby + agg"* — *one line* across *all keys*.

## Hands-on: Five groupby Steps

### Step 1 — Prepare data

```python
import pandas as pd
df = pd.DataFrame({
    "city": ["Seoul", "Seoul", "Busan", "Busan"],
    "month": ["Jan", "Feb", "Jan", "Feb"],
    "sales": [100, 120, 80, 95],
})
```

### Step 2 — Simple sum

```python
print(df.groupby("city")["sales"].sum())
```
A simple grouped sum is the first proof that split and combine already work. Before you reach for richer statistics, make sure the grouped totals themselves match your mental math.

**Expected output:**

```text
city
Busan    175
Seoul    220
Name: sales, dtype: int64
```

### Step 3 — agg with multiple stats

```python
print(df.groupby("city").agg(
    total=("sales", "sum"),
    mean=("sales", "mean"),
    n=("sales", "count"),
))
```

### Step 4 — transform

```python
df["share"] = df["sales"] / df.groupby("city")["sales"].transform("sum")
print(df)
```

`transform` matters because it keeps the original row shape intact. That makes it the natural tool for feature engineering like per-group shares, z-scores, and deviations from a group average.

**Expected output:**

```text
    city month  sales     share
0  Seoul   Jan    100  0.454545
1  Seoul   Feb    120  0.545455
2  Busan   Jan     80  0.457143
3  Busan   Feb     95  0.542857
```

### Step 5 — filter

```python
big = df.groupby("city").filter(lambda g: g["sales"].sum() > 200)
print(big)
```

## What to Notice in This Code

- *agg* yields *one row per group*; *transform* keeps the *original shape*.
- *Named aggregation* controls *output column names*.
- *filter* returns *rows*, not *booleans*.

## Five Common Mistakes

1. **Confusing *transform* and *agg*.**
2. **Skipping *as_index=False* and getting *surprising indexes*.**
3. **Forgetting *reset_index*, making downstream *joins hard*.**
4. **Missing *brackets* on multi-key groupby.**
5. **Overusing *apply* and getting *slow code*.**

## How This Shows Up in Production

Segment analysis, cohort retention, KPI aggregation — *groupby* powers *business intelligence*. *transform* is the workhorse of *feature engineering*.

## How a Senior Engineer Thinks

- *agg first*, *apply last*.
- Use *named aggregation* for *readable output*.
- Use *transform* to *create features*.
- Treat *multi-key* as a *tuple index*.
- Choose *as_index* *deliberately*.

## Checklist

- [ ] I can explain *split-apply-combine*.
- [ ] I distinguish *agg / transform / filter*.
- [ ] I use *named aggregation*.
- [ ] I do *multi-key* groupby.

## Practice Problems

1. Print *mean and std per category* using *named agg*.
2. Use *transform* to attach the *group mean* back to the original DataFrame.
3. Use *filter* to keep groups whose *sum exceeds a threshold*.

## Wrap-up and next steps

groupby is the *engine of analysis*. Next we cover *merge and join*.

## Answering the Opening Questions

- **The *split-apply-combine* model?**
  - The article treats Groupby and Aggregation as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **The difference between *agg / transform / filter?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Multi-key grouping?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Pandas 101 (1/10): What Is Pandas?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): Series and DataFrame](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): Reading CSV and Excel](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): Filtering and Selection](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): Handling Missing Values](./05-missing-values.md)
- **Groupby and Aggregation (current)**
- Merge and Join (upcoming)
- Time Series (upcoming)
- Apply and Vectorization (upcoming)
- Real-World Data Analysis (upcoming)

<!-- toc:end -->

## References

- [pandas — Group by: split-apply-combine](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [pandas — agg](https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.agg.html)
- [pandas — transform](https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.transform.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)

Tags: Pandas, GroupBy, Aggregation, DataAnalysis, Beginner

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

This is the 6th post in the Pandas 101 series.

In this chapter, we will frame `groupby` as the split-apply-combine workflow. That gives you a clearer mental model for when to reach for `agg`, `transform`, or `filter`.


![pandas 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/06/06-01-concept-at-a-glance.en.png)
*pandas 101 chapter 6 flow overview*
> *Aggregation starts with the split. Group by customer, by date, or by region on the same data — you get completely different answers. Choose your grain first.

## Questions to Keep in Mind

- The *split-apply-combine* model?
- The difference between *agg / transform / filter?
- Multi-key grouping?

## Why It Matters

*Aggregation is the core of analysis*. With *groupby*, *dozens of for-loop lines* collapse into *one*. Business metrics, cohort analysis, and feature engineering all build on top of it.

## Key Terms

- **groupby**: *split into groups* by key.
- **agg**: *reduce to one value* per group.
- **transform**: return per-group computation in *original shape*.
- **filter**: keep rows by a *group-level condition*.
- **as_index**: decides whether the *group key* becomes the *index*.
- **split-apply-combine**: the pattern of splitting data into groups, applying a computation, and reassembling results.

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

### Aggregation Function Comparison

The following table summarizes the return shape and use case of common aggregation functions.

| Function | Return Shape | Use Case |
|---|---|---|
| `mean()` | One value per group | Group average |
| `sum()` | One value per group | Group total |
| `count()` | One value per group | Row count per group |
| `agg()` | One row per group | Multiple statistics at once |
| `transform()` | Original row count preserved | Restore group stats to original length |
| `apply()` | Variable | Arbitrary function per group |

The key difference: aggregation functions produce one value per group, while `transform` preserves the original row count and broadcasts group statistics back. For feature engineering, `transform` is far more common.

### Step 3 — agg with multiple stats

```python
print(df.groupby("city").agg(
    total=("sales", "sum"),
    mean=("sales", "mean"),
    n=("sales", "count"),
))
```

Named aggregation controls output column names, making the result table much more readable. This is the most common pattern in practice.

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

### Multi-column groupby with agg

In practice, you often need to group by multiple keys and compute different statistics on different columns.

```python
df = pd.DataFrame({
    "city": ["Seoul", "Seoul", "Busan", "Busan"],
    "category": ["A", "B", "A", "B"],
    "sales": [100, 120, 80, 95],
    "visits": [50, 60, 40, 45],
})

result = df.groupby(["city", "category"]).agg(
    total_sales=("sales", "sum"),
    avg_sales=("sales", "mean"),
    total_visits=("visits", "sum"),
)
print(result)
```

**Expected output:**

```text
               total_sales  avg_sales  total_visits
city  category
Busan A                 80       80.0            40
      B                 95       95.0            45
Seoul A                100      100.0            50
      B                120      120.0            60
```

Multi-key grouping produces a hierarchical index. Call `reset_index()` to flatten it back to a regular table. This pattern appears constantly in business reports.

```python
print(result.reset_index())
```

**Expected output:**

```text
    city category  total_sales  avg_sales  total_visits
0  Busan        A           80       80.0            40
1  Busan        B           95       95.0            45
2  Seoul        A          100      100.0            50
3  Seoul        B          120      120.0            60
```

Keep the hierarchical index when you need `.loc[]` group selection; flatten when joining with other tables.

### Step 5 — filter

```python
big = df.groupby("city").filter(lambda g: g["sales"].sum() > 200)
print(big)
```

`filter` keeps entire groups that satisfy a condition. The key distinction: it operates at the group level, not the row level.

### groupby Performance Tips

Grouping is central to analysis, but it can become a bottleneck on large data. These tips help.

#### 1. Use category dtype

When a group key column has few unique values, converting to category improves memory and speed.

```python
df["city"] = df["city"].astype("category")
print(df.groupby("city")["sales"].sum())
```

Category dtype stores strings as integer codes internally, making comparisons faster than string-by-string. The effect is largest when group count is small but data is large.

#### 2. Drop unnecessary columns

Select only the columns you need before aggregating.

```python
# Slow: groups all columns
df.groupby("city").mean()

# Fast: aggregates only the needed column
df.groupby("city")["sales"].mean()
```

#### 3. Prefer built-in functions over apply

`apply` is slow. Check built-in aggregation functions or `agg` first.

```python
# Slow
df.groupby("city").apply(lambda g: g["sales"].sum())

# Fast
df.groupby("city")["sales"].sum()
```

#### 4. sort=False option

If you do not need sorted output, pass `sort=False` to eliminate the sorting cost.

```python
df.groupby("city", sort=False)["sales"].sum()
```

These four tips alone can noticeably improve groupby speed. Category dtype and column selection in particular make a big difference with a single line of code.

### Practical Example: Cohort Analysis

Grouping powers real-world analyses like cohort analysis.

```python
import pandas as pd

# User signup data
df = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "signup_month": ["2026-01", "2026-01", "2026-02", "2026-02", "2026-03"],
    "purchase_month": ["2026-02", "2026-03", "2026-02", "2026-04", "2026-03"],
    "amount": [100, 150, 80, 200, 120],
})

# Average purchase amount by signup month
cohort = df.groupby("signup_month").agg(
    users=("user_id", "count"),
    avg_amount=("amount", "mean"),
    total_amount=("amount", "sum"),
)
print(cohort)
```

**Expected output:**

```text
              users  avg_amount  total_amount
signup_month                                  
2026-01           2       125.0           250
2026-02           2       140.0           280
2026-03           1       120.0           120
```

Cohort analysis tracks the behavior of user groups who joined at the same time. Grouping by signup month and comparing average purchase amounts reveals which cohort is more valuable.

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

Segment analysis, cohort retention, KPI aggregation — *groupby* powers *business intelligence*. *transform* is the workhorse of *feature engineering*, creating per-group shares, z-scores, and deviations from group averages.

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

- **What flow does `groupby` follow?**
  - `groupby` works through the split-apply-combine flow: splitting data by a key, applying a computation to each group, then recombining results into a single table. `df.groupby("city")["sales"].sum()` is the most basic form—splitting by city, computing sums, and reassembling into a Series.
- **Why are aggregation, transformation, and filtering different faces of the same operation?**
  - Aggregation leaves one value per group, transformation returns group-computed results at the original length, and filtering decides whether to keep or discard entire groups. The article showed `agg(total=("sales", "sum"))`, `transform("sum")`, and `filter(lambda g: g["sales"].sum() > 200)` separately because result shape and usage differ.
- **What is the best approach when computing multiple statistics at once?**
  - Named aggregation with explicit result column names like `total`, `mean`, and `n` is most readable. The pattern `df.groupby("city").agg(total=("sales", "sum"), mean=("sales", "mean"), n=("sales", "count"))` computes multiple statistics while producing output ready for downstream joins and reports.
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

---
series: pandas-101
episode: 1
title: "Pandas 101 (1/10): What Is Pandas?"
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
  - Python
  - DataAnalysis
  - DataFrame
  - Beginner
seo_description: A beginner-friendly intro to Pandas — what Series and DataFrame are, why Pandas became the standard tool for tabular data analysis in Python
last_reviewed: '2026-05-15'
---

# Pandas 101 (1/10): What Is Pandas?

Pandas is easy to misunderstand when you first learn it. On one day it feels like a friendlier spreadsheet library. On another day it looks like the entire foundation of Python data work. If you never settle that ambiguity, filtering, aggregation, joins, and time series features keep feeling like disconnected tricks instead of one coherent toolkit.

This is the first post in the Pandas 101 series.

In this post, I want to define Pandas by role rather than by feature list. Pandas is the standard environment for reading, inspecting, reshaping, and summarizing in-memory tabular data with short, expressive code.

## Questions to Keep in Mind

- The *definition* of *Pandas* and where it sits?
- The intuition behind *Series* and *DataFrame?
- The basic *load → inspect → summarize* workflow?

## Big Picture

![pandas 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/01/01-01-concept-at-a-glance.en.png)

*pandas 101 chapter 1 flow overview*

This picture places What Is Pandas? inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of What Is Pandas? is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why It Matters

CSV, Excel, databases, APIs — *80% of real-world data* is *tabular*. If you cannot drive *Pandas*, you cannot start *data analysis*.

> *If your data fits in memory, Pandas is usually the right answer.*

## Concept at a Glance

## Key Terms

- **Series**: a *1D labeled array*.
- **DataFrame**: a *2D labeled table* — both rows and columns have labels.
- **Index**: the *label that identifies a row*.
- **dtype**: the *type of each column* (int64, float64, object, datetime64).
- **Vectorization**: column-wise computation *without explicit loops* — the core Pandas idiom.

## Before/After

**Before**: *"Loop over rows like Excel"* — chokes at 10K rows.

**After**: *"One DataFrame, one million rows"* — *vectorized operations* that are tens of times faster.

## Hands-on: Your First Five Steps

### Step 1 — Install and import

```python
# pip install pandas
import pandas as pd
print(pd.__version__)
```

### Step 2 — Build a Series

```python
s = pd.Series([10, 20, 30], index=["a", "b", "c"])
print(s)
print("sum:", s.sum())
```

### Step 3 — Build a DataFrame

```python
df = pd.DataFrame({
    "name": ["Ada", "Linus", "Grace"],
    "age": [36, 54, 85],
})
print(df)
```

The first thing to check is whether the whole table looks like the shape you expected. A tiny printout tells you whether column names, row counts, and value types already make sense.

**Expected output:**

```text
    name  age
0    Ada   36
1  Linus   54
2  Grace   85
```

### Step 4 — First summary

```python
print(df.shape)
print(df.dtypes)
print(df.describe(include="all"))
```

### Step 5 — First filter

```python
print(df[df["age"] > 40])
```

A boolean filter is your first proof that Pandas is thinking in terms of whole columns, not manual row loops. If the filtered table shrinks exactly where you expect, the condition is working.

**Expected output:**

```text
    name  age
1  Linus   54
2  Grace   85
```

## What to Notice in This Code

- A *DataFrame* is *column-oriented* — each column has its own dtype.
- *describe()* is your *first numeric summary*.
- *Boolean indexing* is the Pandas equivalent of SQL's *WHERE*.

## Five Common Mistakes

1. **Iterating row by row with a *for* loop** instead of vectorizing.
2. **Skipping *dtype* checks** — numbers loaded as strings.
3. **Ignoring *SettingWithCopyWarning*.**
4. **Misunderstanding the *index*** and forgetting *reset_index*.
5. **Not watching memory** — never calling *df.info()*.

## How This Shows Up in Production

Data cleaning, report generation, ML preprocessing, dashboard prep — *every data pipeline starts in Pandas*. *Jupyter + Pandas* is the *default analysis kit*.

## How a Senior Engineer Thinks

- Always check *shape, dtypes, head* first.
- Reach for *apply* only after vectorization fails.
- Make the *index* a *meaningful key*.
- Be conscious of *view vs copy*.
- When memory is the limit, move to *Polars/Dask*.

## Checklist

- [ ] I can build a *DataFrame*.
- [ ] I call *shape, dtypes, describe*.
- [ ] I can filter with *boolean indexing*.
- [ ] I know the difference between *Series* and *DataFrame*.

## Practice Problems

1. Build a *3x4* DataFrame and print the *mean of each column*.
2. List *three differences* between a *Series* and a Python *list*.
3. Compare *describe()* with and without *include="all"* and note what changes.

## Wrap-up and next steps

Pandas is the *standard language for tabular data*. Next we go deep into the *internal structure* of *Series and DataFrame*.

## Answering the Opening Questions

- **The *definition* of *Pandas* and where it sits?**
  - The article treats What Is Pandas? as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **The intuition behind *Series* and *DataFrame?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The basic *load → inspect → summarize* workflow?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **What Is Pandas? (current)**
- Series and DataFrame (upcoming)
- Reading CSV and Excel (upcoming)
- Filtering and Selection (upcoming)
- Handling Missing Values (upcoming)
- Groupby and Aggregation (upcoming)
- Merge and Join (upcoming)
- Time Series (upcoming)
- Apply and Vectorization (upcoming)
- Real-World Data Analysis (upcoming)

<!-- toc:end -->

## References

- [pandas — Official Documentation](https://pandas.pydata.org/docs/)
- [10 Minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)
- [Real Python — Pandas Tutorials](https://realpython.com/learning-paths/pandas-data-science/)

Tags: Pandas, Python, DataAnalysis, DataFrame, Beginner

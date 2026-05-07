---
series: pandas-101
episode: 9
title: apply and Vectorization
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Pandas
  - Vectorization
  - Performance
  - Apply
  - Beginner
seo_description: Learn the trap of apply and the power of NumPy and Pandas vectorization to make your data pipelines fast and idiomatic
last_reviewed: '2026-05-04'
---

# apply and Vectorization

> Pandas 101 series (9/10)

<!-- a-grade-intro:begin -->

**Core question**: Is *apply* really *faster than a for-loop*?

> *apply is a *thin wrapper around for-loops*. Real speed comes from *vectorization*.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The meaning of *vectorization*
- The difference between *apply / map / vectorize*
- *Interop* with *NumPy*
- A 5-step performance hands-on
- Five common mistakes

## Why It Matters

Analysis speed can differ by *tens to hundreds of times*. *Vectorization* is the *essence of Pandas*, and *apply abuse* is the *most common antipattern*.

## Concept at a Glance

```mermaid
flowchart LR
    Loop["for-loop"] -->|slow| Apply["apply"]
    Apply -->|faster| Vec["vectorized (NumPy / Pandas ops)"]
```

## Key Terms

- **Vectorization**: array-level computation *without explicit loops*.
- **apply**: apply a function *along rows/columns* — internally a Python loop.
- **map**: apply a function/dict to *Series elements*.
- **np.where**: *vectorized conditional*.
- **eval / numexpr**: *acceleration* for *large expressions*.

## Before/After

**Before**: *"for i in range(len(df))"* — minutes on 1M rows.

**After**: *"df['c'] = df['a'] + df['b']"* — milliseconds.

## Hands-on: Five Performance Steps

### Step 1 — Baseline data

```python
import numpy as np, pandas as pd
df = pd.DataFrame({"a": np.arange(1_000_000), "b": np.arange(1_000_000)})
```

### Step 2 — Slow path

```python
# %timeit df.apply(lambda r: r["a"] + r["b"], axis=1)
# Very slow — apply(axis=1) is a per-row Python call
```

### Step 3 — Vectorized

```python
df["c"] = df["a"] + df["b"]   # fastest
```

### Step 4 — np.where for conditional

```python
df["flag"] = np.where(df["a"] % 2 == 0, "even", "odd")
```

### Step 5 — map for code translation

```python
mapping = {0: "zero", 1: "one"}
print(pd.Series([0, 1, 2]).map(mapping))
```

## What to Notice in This Code

- *axis=1 apply* is *the slowest* — Python call *per row*.
- *Vector ops* run at the *C level*.
- *np.where* is the *vectorized if-else*.

## Five Common Mistakes

1. **Overusing *apply(axis=1)*.**
2. **Using *Python for-loops* to compute *row-wise sums*.**
3. **Building giant expressions without *eval/numexpr*.**
4. **Ignoring *NaNs* introduced by *map*.**
5. **Vectorization fails due to *dtype mismatch*, then everything becomes *object dtype*.**

## How This Shows Up in Production

ETL transforms, feature engineering, large reports — *vectorization* directly cuts *cost and time*. The *easiest lever* for *cloud cost reduction*.

## How a Senior Engineer Thinks

- *Always check vectorization first*.
- Use *apply* only when *vectorization is impossible*.
- *Avoid axis=1*.
- *Match dtypes*.
- *Profile* to find the *real bottleneck*.

## Checklist

- [ ] I distinguish *vectorization* from *apply*.
- [ ] I use *np.where*.
- [ ] I use *map* for *code translation*.
- [ ] I avoid *axis=1 apply*.

## Practice Problems

1. Compare *vectorized addition* vs *apply(axis=1)* with timing.
2. Express a *3-tier condition* with *np.where*.
3. Translate *country codes* to *country names* using *map*.

## Wrap-up and Next Steps

Vectorization is the *essence of Pandas*. Next we cover a *real-world data analysis* example.

<!-- toc:begin -->
- [What Is Pandas?](./01-what-is-pandas.md)
- [Series and DataFrame](./02-series-and-dataframe.md)
- [Reading CSV and Excel](./03-read-csv-and-excel.md)
- [Filtering and Selection](./04-filtering-and-selection.md)
- [Handling Missing Values](./05-missing-values.md)
- [groupby](./06-groupby.md)
- [Merge and Join](./07-merge-and-join.md)
- [Time Series](./08-time-series.md)
- **apply and Vectorization (current)**
- Real-world Data Analysis (upcoming)
<!-- toc:end -->

## References

- [pandas — Enhancing performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
- [pandas — apply](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html)
- [NumPy — Universal functions](https://numpy.org/doc/stable/reference/ufuncs.html)
- [Real Python — Fast, Flexible, Easy and Intuitive Pandas](https://realpython.com/fast-flexible-pandas/)

Tags: Pandas, Vectorization, Performance, Apply, Beginner

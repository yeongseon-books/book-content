---
series: pandas-101
episode: 2
title: "Pandas 101 (2/10): Series and DataFrame"
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
  - Series
  - DataFrame
  - Python
  - Beginner
seo_description: A clear introduction to the two core Pandas data structures — Series and DataFrame — covering index, dtype, and column-wise thinking with code
last_reviewed: '2026-05-15'
---

# Pandas 101 (2/10): Series and DataFrame

Very early in Pandas, most people run into the same question: are Series and DataFrame just two names for similar containers, or are they different views of one data model? If that relationship stays fuzzy, column selection, arithmetic, sorting, and joins all feel like memorized syntax instead of predictable behavior.

This is post 2 in the Pandas 101 series.

The core idea in this chapter is simple. A DataFrame is a collection of Series that share the same label system. Once that model clicks, many Pandas behaviors stop feeling magical and start feeling consistent.

## Questions to Keep in Mind

- The *internal structure* of a *Series?
- Column-oriented* thinking with *DataFrame?
- The role of the *Index?

## Big Picture

![pandas 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/02/02-01-concept-at-a-glance.en.png)

*pandas 101 chapter 2 flow overview*

This picture places Series and DataFrame inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Series and DataFrame is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why It Matters

*Every Pandas operation* eventually reduces to *Series-level work*. A *DataFrame column is a Series*. Understanding this model makes *everything else easy*.

## Concept at a Glance

## Key Terms

- **Series**: *values + index* — a *NumPy array* with *labels* on top.
- **DataFrame**: a *dict of Series* that share a *common index*.
- **values**: the underlying *NumPy array*.
- **index**: row labels.
- **columns**: column labels.

## Before/After

**Before**: *"A DataFrame is just a table"* — only row-by-row thinking.

**After**: *"A DataFrame is a collection of Series"* — fluent *column-wise operations*.

## Hands-on: Building the Structures Yourself

### Step 1 — Create a Series and inspect

```python
import pandas as pd
s = pd.Series([1.0, 2.0, 3.0], index=["a", "b", "c"], name="x")
print(s.values, s.index, s.name)
```

### Step 2 — Series arithmetic

```python
print(s * 10)
print(s + s)
```

### Step 3 — Build a DataFrame

```python
df = pd.DataFrame({
    "x": [1, 2, 3],
    "y": [10, 20, 30],
}, index=["a", "b", "c"])
print(df)
```

This output makes the model concrete: two labeled columns sharing one index. That shared label system is why later alignment, joins, and selections feel so natural in Pandas.

**Expected output:**

```text
   x   y
a  1  10
b  2  20
c  3  30
```

### Step 4 — Column selection returns a Series

```python
col = df["x"]
print(type(col), col)
```

### Step 5 — Automatic index alignment

```python
s1 = pd.Series([1, 2, 3], index=["a", "b", "c"])
s2 = pd.Series([10, 20, 30], index=["b", "c", "d"])
print(s1 + s2)
```

The important part is not the arithmetic itself but the label alignment behind it. Pandas lines the indexes up first, then performs the addition only where labels overlap.

**Expected output:**

```text
a     NaN
b    12.0
c    23.0
d     NaN
dtype: float64
```

## What to Notice in This Code

- *df["x"]* returns a *Series*.
- Adding two *Series* triggers *automatic index alignment*.
- *NaN* is the *signature of failed alignment*.

## Five Common Mistakes

1. **Confusing *df["x"]* with a *DataFrame*.**
2. **Missing *NaN from index mismatch* during arithmetic.**
3. **Always converting to NumPy via *values* and losing labels.**
4. **Ignoring the *name* attribute.**
5. **Assuming two DataFrames share row order when added.**

## How This Shows Up in Production

A/B test comparison, time series aggregation, joining *data from multiple sources* by *index key* — the *magic of Pandas* is *index alignment*.

## How a Senior Engineer Thinks

- Always be *aware of what the index means*.
- Treat *column selection* as *Series thinking*.
- Use *NaN from misalignment* as a *debugging clue*.
- Reduce dependence on *df.values*.
- Identify Series with *name*.

## Checklist

- [ ] I can distinguish *Series* and *DataFrame*.
- [ ] I can name *index* and *columns*.
- [ ] I know *df["col"]* is a *Series*.
- [ ] I know *index alignment* is *automatic*.

## Practice Problems

1. Build *three Series*, combine them into a *DataFrame*, and confirm the *common index*.
2. Add two Series with *different indexes* and inspect the *NaN positions*.
3. Show in code the *type difference* between *df["x"]* and *df[["x"]]*.

## Wrap-up and next steps

A DataFrame is *a collection of Series*. Next we cover *reading CSV and Excel files*.

## Answering the Opening Questions

- **The *internal structure* of a *Series?**
  - The article treats Series and DataFrame as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Column-oriented* thinking with *DataFrame?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The role of the *Index?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Pandas 101 (1/10): What Is Pandas?](./01-what-is-pandas.md)
- **Series and DataFrame (current)**
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

- [pandas — Series API](https://pandas.pydata.org/docs/reference/series.html)
- [pandas — DataFrame API](https://pandas.pydata.org/docs/reference/frame.html)
- [pandas — Intro to data structures](https://pandas.pydata.org/docs/user_guide/dsintro.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)

Tags: Pandas, Series, DataFrame, Python, Beginner

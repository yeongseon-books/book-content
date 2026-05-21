---
series: pandas-101
episode: 4
title: "Pandas 101 (4/10): Filtering and Selection"
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
  - Filtering
  - Selection
  - Indexing
  - Beginner
seo_description: Master loc, iloc, boolean indexing, and query — the four ways Pandas selects rows and columns, with code and a clear mental model
last_reviewed: '2026-05-15'
---

# Pandas 101 (4/10): Filtering and Selection

Pandas gets confusing fast when you notice that there are several ways to pick rows and columns from the same table. `loc`, `iloc`, boolean masks, and `query` can look interchangeable at first, but they are not. If you do not separate them by intent, selection code becomes harder to read and assignment bugs show up sooner than you expect.

This is post 4 in the Pandas 101 series.

My goal here is to organize selection tools as a small decision framework: labels, positions, and conditions. Once you think that way, the syntax choices become much easier to justify.


![pandas 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/04/04-01-concept-at-a-glance.en.png)
*pandas 101 chapter 4 flow overview*
> *Filtering is repeating at every stage of analysis. Slow or ambiguous selection code breaks everything downstream — treat this as a core skill, not syntax.

## Questions to Keep in Mind

- The difference between *loc* and *iloc?
- The intuition behind *boolean indexing?
- The readability of *query?

## Why It Matters

*Every step of analysis* involves *subset extraction*. *Slow or wrong selection* shakes the *whole pipeline*.

## Key Terms

- **loc**: *label-based* selection.
- **iloc**: *position-based* selection.
- **boolean mask**: a *True/False Series* selecting rows.
- **query**: filter with a *string expression*.
- **isin**: check *membership* in a *set of values*.

## Before/After

**Before**: *"Just use df[cond]"* — *chained indexing* and *warnings*.

**After**: *"Match tool to intent"* — *loc/iloc/query* used *deliberately*.

## Hands-on: Five Selection Steps

### Step 1 — Column selection

```python
import pandas as pd
df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]}, index=["a", "b", "c"])
print(df["x"])
print(df[["x", "y"]])
```

### Step 2 — loc

```python
print(df.loc["a"])
print(df.loc[["a", "c"], "x"])
```

Label-based selection pays off because the output remains easy to read. The result tells you exactly which rows you asked for, without forcing you to remember positional offsets.

**Expected output:**

```text
a    1
c    3
Name: x, dtype: int64
```

### Step 3 — iloc

```python
print(df.iloc[0])
print(df.iloc[0:2, 0])
```

### Step 4 — Boolean indexing

```python
print(df[df["x"] > 1])
print(df[(df["x"] > 1) & (df["y"] < 30)])
```

### Step 5 — query and isin

```python
print(df.query("x > 1 and y < 30"))
print(df[df["x"].isin([1, 3])])
```

This is where readability starts to matter more than syntax trivia. `query` keeps longer expressions compact, and `isin` replaces brittle chains of repeated OR conditions.

**Expected output:**

```text
   x   y
b  2  20

   x   y
a  1  10
c  3  30
```

## What to Notice in This Code

- *loc* is *endpoint-inclusive*, *iloc* is *endpoint-exclusive*.
- *&* and *|* are *bitwise operators* — not *and/or*.
- *query* wins on *readability* with *large expressions*.

## Five Common Mistakes

1. **Using *and/or* in masks → error.** Need *&/|* and *parentheses*.
2. **Chained indexing**: `df[df["x"]>1]["y"] = ...` → *SettingWithCopyWarning*.
3. **Forgetting that *loc is endpoint-inclusive*.**
4. **Trying *labels with iloc*.**
5. **Replacing *isin* with long *|* chains.**

## How This Shows Up in Production

KPI dashboards, outlier detection, A/B test slicing — *condition-based selection* is the *core of analysis functions*. Many teams *enforce loc* as a code standard.

## How a Senior Engineer Thinks

- *Extract complex conditions* into *named variables*.
- Always use *loc* for *assignment*.
- Use *query* only when it *wins on readability*.
- Use *isin/between* to *shorten code*.
- *Never ignore warnings*.

## Checklist

- [ ] I distinguish *loc* and *iloc*.
- [ ] I use *&/|* with *parentheses*.
- [ ] I avoid *chained indexing*.
- [ ] I know *query* and *isin*.

## Practice Problems

1. Use *loc* to extract *a subset of specific labels*.
2. Use *iloc* to print the *first 5 rows*.
3. Express *two or more conditions* with *query*.

## Wrap-up and next steps

Selection is the *primitive operation of analysis*. Next we tackle *missing value handling*.

## Answering the Opening Questions

- **The difference between *loc* and *iloc?**
  - The article treats Filtering and Selection as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **The intuition behind *boolean indexing?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The readability of *query?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Pandas 101 (1/10): What Is Pandas?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): Series and DataFrame](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): Reading CSV and Excel](./03-read-csv-and-excel.md)
- **Filtering and Selection (current)**
- Handling Missing Values (upcoming)
- Groupby and Aggregation (upcoming)
- Merge and Join (upcoming)
- Time Series (upcoming)
- Apply and Vectorization (upcoming)
- Real-World Data Analysis (upcoming)

<!-- toc:end -->

## References

- [pandas — Indexing and selecting data](https://pandas.pydata.org/docs/user_guide/indexing.html)
- [pandas — query](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html)
- [pandas — Boolean indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing)
- [Real Python — Pandas DataFrame Indexing](https://realpython.com/pandas-dataframe/)

Tags: Pandas, Filtering, Selection, Indexing, Beginner

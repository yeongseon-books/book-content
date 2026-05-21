---
series: pandas-101
episode: 5
title: "Pandas 101 (5/10): Handling Missing Values"
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
  - MissingValues
  - DataCleaning
  - Python
  - Beginner
seo_description: Handle missing data with isna, dropna, fillna, and interpolate — learn the standard patterns and the why behind each choice
last_reviewed: '2026-05-15'
---

# Pandas 101 (5/10): Handling Missing Values

Real datasets are rarely complete. Sensors miss readings, surveys leave blanks behind, and transaction pipelines drop fields at inconvenient moments. That means missing-value handling is not cosmetic cleanup. It is one of the choices that most directly shapes the credibility of your analysis.

This is post 5 in the Pandas 101 series.

In this chapter, I will treat `NaN` as a signal to interpret before it becomes a value to drop or fill. The right first question is not “which method should I use?” but “why is this value missing at all?”

## Questions to Keep in Mind

- The meaning of *NaN* and its *dtype* impact?
- How to use *isna / dropna / fillna?
- The intuition behind *interpolate?

## Big Picture

![pandas 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/05/05-01-concept-at-a-glance.en.png)

*pandas 101 chapter 5 flow overview*

This picture places Handling Missing Values inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> *NaN is not garbage — it's a signal. Whether you drop, fill, or interpolate *changes your distribution and your sample size. Choose mindfully.

## Why It Matters

Real data is *full of missing values*. How you handle them decides *model performance* and *analysis credibility*.

## Key Terms

- **NaN**: *Not a Number* — *float* missing marker.
- **NA / pd.NA**: Pandas' *unified* missing marker (nullable dtypes).
- **dropna**: drop *rows/columns* with missing values.
- **fillna**: *fill* with a *constant, mean, or previous value*.
- **interpolate**: *interpolation* — fits time series naturally.

## Before/After

**Before**: *"Just dropna"* — *80% of rows* vanish.

**After**: *"Treat by cause"* — *interpolate sensors*, *model survey gaps*.

## Hands-on: Five Missing-Value Steps

### Step 1 — Detect

```python
import numpy as np, pandas as pd
df = pd.DataFrame({"x": [1, np.nan, 3], "y": [np.nan, 2, 3]})
print(df.isna())
print(df.isna().sum())
```

Start by measuring the pattern, not by choosing a cleanup tool. A one-line diagnostic already tells you where the missingness is concentrated and which columns deserve a closer look.

**Expected output:**

```text
x    1
y    1
dtype: int64
```

### Step 2 — Drop

```python
print(df.dropna())            # drop rows with any NaN
print(df.dropna(axis=1))      # drop columns with any NaN
```

### Step 3 — Fill

```python
print(df.fillna(0))
print(df.fillna(df.mean(numeric_only=True)))
```

### Step 4 — Forward / backward fill

```python
print(df.fillna(method="ffill"))
print(df.fillna(method="bfill"))
```

### Step 5 — Interpolate

```python
ts = pd.Series([1.0, np.nan, np.nan, 4.0])
print(ts.interpolate())
```

Interpolation preserves the shape of a gradual numeric trend better than a blunt constant fill. Time series work is where that difference becomes immediately visible.

**Expected output:**

```text
0    1.0
1    2.0
2    3.0
3    4.0
dtype: float64
```

## What to Notice in This Code

- *isna().sum()* is the *first diagnostic*.
- *fillna(mean)* may *distort the distribution*.
- *interpolate* is *natural for time series*.

## Five Common Mistakes

1. **Overusing *dropna* and losing *most rows*.**
2. **Filling with *0* and *distorting the distribution*.**
3. **Using only *ffill* and ignoring *leading NaNs*.**
4. **Trying to fill *categorical* columns with the *mean*.**
5. **Treating missingness *arbitrarily* with no *recorded policy*.**

## How This Shows Up in Production

Sensor streams, surveys, transaction logs — the *missingness pattern itself* is a *signal*. Form hypotheses (*MAR/MCAR/MNAR*) and document the *handling decision*.

## How a Senior Engineer Thinks

- *Ask why* before treating missingness.
- *Document the policy*.
- Add a *"was missing" indicator column*.
- Use *interpolate* for *time series*.
- For ML, turn *missingness into a feature*.

## Checklist

- [ ] I diagnose with *isna().sum()*.
- [ ] I measure the *impact of dropna*.
- [ ] I make my *fillna strategy explicit*.
- [ ] I record the *missing rate*.

## Practice Problems

1. Print the *missing rate per column*.
2. Print *row counts before and after dropna*.
3. Compare *ffill* and *interpolate* on a *time series* and inspect differences.

## Wrap-up and next steps

Missing-value handling decides *analysis integrity*. Next we cover *groupby*.

## Answering the Opening Questions

- **The meaning of *NaN* and its *dtype* impact?**
  - The article treats Handling Missing Values as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How to use *isna / dropna / fillna?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The intuition behind *interpolate?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Pandas 101 (1/10): What Is Pandas?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): Series and DataFrame](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): Reading CSV and Excel](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): Filtering and Selection](./04-filtering-and-selection.md)
- **Handling Missing Values (current)**
- Groupby and Aggregation (upcoming)
- Merge and Join (upcoming)
- Time Series (upcoming)
- Apply and Vectorization (upcoming)
- Real-World Data Analysis (upcoming)

<!-- toc:end -->

## References

- [pandas — Working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [pandas — fillna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html)
- [pandas — interpolate](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html)
- [scikit-learn — Imputation](https://scikit-learn.org/stable/modules/impute.html)

Tags: Pandas, MissingValues, DataCleaning, Python, Beginner

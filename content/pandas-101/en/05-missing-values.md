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

This is the 5th post in the Pandas 101 series.

In this chapter, I will treat `NaN` as a signal to interpret before it becomes a value to drop or fill. The right first question is not "which method should I use?" but "why is this value missing at all?"


![pandas 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/05/05-01-concept-at-a-glance.en.png)
*pandas 101 chapter 5 flow overview*
> *NaN is not garbage — it's a signal. Whether you drop, fill, or interpolate *changes your distribution and your sample size. Choose mindfully.

## Questions to Keep in Mind

- The meaning of `NaN` and its dtype impact?
- How to diagnose missing values before treating them?
- When to drop vs when to fill?

## Why It Matters

Missing-value handling changes both model performance and analysis interpretation. The same dataset with blind `dropna` might lose 80% of rows; with careless `fillna(0)` it might distort the distribution into meaninglessness. The choice is never cosmetic.

## Key Terms

- **NaN**: Not a Number — float missing marker.
- **NA / pd.NA**: Pandas' unified missing marker (nullable dtypes).
- **dropna**: drop rows/columns with missing values.
- **fillna**: fill with a constant, mean, or previous value.
- **interpolate**: interpolation — fits time series naturally.

## Before/After

**Before**: "Just dropna" — 80% of rows vanish.

**After**: "Treat by cause" — interpolate sensors, model survey gaps, document the policy.

## Hands-on: Five Missing-Value Steps

### Step 1 — Detect

```python
import numpy as np, pandas as pd
df = pd.DataFrame({"x": [1, np.nan, 3], "y": [np.nan, 2, 3]})
print(df.isna())
print(df.isna().sum())
```

The diagnostic step comes first. Knowing which columns have missing values and how many immediately frames whether dropping or filling is more appropriate.

**Expected output:**

```text
x    1
y    1
dtype: int64
```

Missing-value handling always starts with diagnosis. `isna().sum()` is the fastest way to see the per-column scale of the problem.

### Step 2 — Drop

```python
print(df.dropna())            # drop rows with any NaN
print(df.dropna(axis=1))      # drop columns with any NaN
```

Dropping is simple but expensive. If you do not measure how many rows or columns disappear, the analysis target itself may shift without you noticing.

### Step 3 — Fill

```python
print(df.fillna(0))
print(df.fillna(df.mean(numeric_only=True)))
```

Filling with a constant or mean is fast but semantically weak. Mean imputation in particular compresses variance and can bias downstream models. Always ask whether the fill value makes domain sense.

## Missing-Value Strategy Comparison

A table makes the trade-offs between strategies explicit.

| Strategy | Function | Pros | Cons |
| --- | --- | --- | --- |
| Drop | `dropna()` | Simple, fast | Reduces sample size |
| Constant fill | `fillna(value)` | Predictable | Distorts distribution |
| Statistical fill | `fillna(df.mean())` | Preserves central tendency | Reduces variance |
| Forward/backward | `ffill()`, `bfill()` | Good for time series | Leaves edge NaN |
| Interpolation | `interpolate()` | Preserves trend | Increased complexity |

Each method has clear trade-offs. The right choice depends on data characteristics and the analysis goal.

### Step 4 — Forward / backward fill

```python
print(df.fillna(method="ffill"))
print(df.fillna(method="bfill"))
```

Forward and backward fill are natural for ordered data (time series, sequential events). But leading or trailing NaN values remain untreated—always check the edges.

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

Interpolation fits time series and continuous measurements especially well. It is not a universal tool, but for filling gaps in a smooth numeric sequence, it is the most natural choice.

## Advanced Imputation Techniques

Production scenarios often require more sophisticated approaches than global mean fill.

### Group-mean imputation

```python
df = pd.DataFrame({
    "category": ["A", "A", "B", "B", "B"],
    "value": [10, np.nan, 20, 25, np.nan],
})
df["value"] = df.groupby("category")["value"].transform(
    lambda x: x.fillna(x.mean())
)
print(df)
```

Filling with the mean of the same group is more accurate than a global mean—a missing temperature in "winter" should be filled with winter averages, not the annual average.

### Missingness as a feature

```python
df["value_missing"] = df["value"].isna().astype(int)
print(df.head())
```

In machine learning, whether a value was missing can itself be predictive. Adding a binary indicator column lets the model learn missingness patterns.

### Conditional fill

```python
df["value"] = df["value"].where(
    df["value"].notna(),
    df.groupby("category")["value"].transform("median")
)
```

When you want to fill only under specific conditions—different strategies per group, per time window, or per data source—combine `where` or `mask` with group transforms.

## Missing-Value Ratio Analysis

Before treating missing values, understand their scale and distribution.

### Per-column missing ratio

```python
df = pd.DataFrame({
    "a": [1, np.nan, 3, np.nan, 5],
    "b": [np.nan, 2, 3, 4, 5],
    "c": [1, 2, 3, 4, 5],
})
missing_ratio = df.isna().sum() / len(df) * 100
print(missing_ratio)
```

**Expected output:**

```text
a    40.0
b    20.0
c     0.0
dtype: float64
```

Columns with very high missing rates (>50%) may be better dropped entirely or treated as a separate signal rather than imputed.

### Per-row missing count

```python
missing_per_row = df.isna().sum(axis=1)
print(missing_per_row)
```

Counting missing values per row identifies low-quality records. Rows with many missing columns may deserve exclusion from analysis entirely.

### Visualizing missing patterns

```python
import matplotlib.pyplot as plt
df.isna().sum().plot(kind="bar")
plt.title("Missing Values per Column")
plt.ylabel("Count")
plt.show()
```

A bar chart of missing counts per column reveals whether missingness is spread evenly or concentrated in specific columns—guiding your strategy choice.

## Missing-Value Correlation

When multiple columns have correlated missingness, it often signals a structural data-collection issue.

```python
import seaborn as sns
import matplotlib.pyplot as plt

missing = df.isna()
correlation = missing.corr()
sns.heatmap(correlation, annot=True)
plt.title("Missing Value Correlation")
plt.show()
```

If columns A and B are always missing together, the root cause is likely one event (a sensor offline, a form section skipped). Treating them jointly is more appropriate than imputing each independently.

## What to Notice in This Code

- `isna().sum()` is the first diagnostic—always run it before choosing a strategy.
- `fillna(mean)` may distort the distribution and reduce variance.
- `interpolate` is natural for time series but not for categorical or sparse data.

## Five Common Mistakes

1. **Overusing `dropna` and losing most rows.** Always measure before and after.
2. **Filling with 0 and distorting the distribution.** Zero is rarely the correct domain default.
3. **Using only `ffill` and ignoring leading NaNs.** The first rows stay missing.
4. **Trying to fill categorical columns with the mean.** Mode or a sentinel value is appropriate.
5. **Treating missingness arbitrarily with no recorded policy.** Future you (or your team) will not know why.

## How This Shows Up in Production

Sensor streams, surveys, transaction logs—the missingness pattern itself is often a signal. A sensor that goes silent for 2 hours may indicate a hardware failure, not "no data." That is why production teams form hypotheses about the missing mechanism (MCAR/MAR/MNAR) and document the handling decision alongside the code.

## How a Senior Engineer Thinks

- Ask why before treating missingness—the cause determines the strategy.
- Document the policy in code comments and data dictionaries.
- Add a "was missing" indicator column when missingness may be informative.
- Use interpolation for time series; use group-mean for categorical splits.
- For ML, evaluate whether missingness itself should be a model feature.

## Checklist

- [ ] I diagnose with `isna().sum()` before choosing a strategy.
- [ ] I measure the impact of `dropna` on sample size.
- [ ] I make my `fillna` strategy explicit and domain-appropriate.
- [ ] I record the missing rate and handling policy.

## Practice Problems

1. Print the missing rate per column as a percentage.
2. Print row counts before and after `dropna` and assess the loss.
3. Compare `ffill` and `interpolate` on a time series and inspect differences.

## Wrap-up and next steps

Missing-value handling is not about making data "clean"—it is about preserving the meaning of the data. Ask why values are missing, choose strategies that match the mechanism, and document your decisions. Next we cover groupby and aggregation.

## Answering the Opening Questions

- **What do `NaN` and `pd.NA` represent?**
  - Both indicate a missing value, but the key point is viewing missingness as a state to interpret rather than a simple error. The article created a DataFrame with `np.nan` and did not immediately delete it—instead treating it as the starting point for diagnosis, replacement, and interpolation.
- **How should you diagnose missing values first?**
  - Start with `isna()` and `isna().sum()` to see which columns have how many missing values. Then computing `missing_ratio = df.isna().sum() / len(df) * 100` gives you the basis for deciding between removal and imputation.
- **When should you drop and when should you fill?**
  - If missingness is sparse and information loss is small, `dropna()` is simple. But for time series where flow matters or values with group context, `fillna`, `ffill`, `bfill`, `interpolate()`, or group-mean imputation may be more appropriate. The article distinguished mean imputation's distribution distortion, `ffill`'s boundary limitation, and `interpolate()`'s time-series suitability for exactly this reason.
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

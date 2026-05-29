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

This is the 2nd post in the Pandas 101 series.

The core idea in this chapter is simple. A DataFrame is a collection of Series that share the same label system. Once that model clicks, many Pandas behaviors stop feeling magical and start feeling consistent.


![pandas 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/02/02-01-concept-at-a-glance.en.png)
*pandas 101 chapter 2 flow overview*
> *DataFrame is really a *collection of Series* that share the same index. Understand this, and alignment, broadcasting, and method chaining all make sense.

## Questions to Keep in Mind

- The *internal structure* of a *Series?
- Column-oriented* thinking with *DataFrame?
- The role of the *Index?

## Why It Matters

Every Pandas operation eventually reduces to Series-level work. A DataFrame column is a Series. Understanding this model makes everything else easy—column selection return types, automatic index alignment, and why labels matter as much as values.

## Key Terms

- **Series**: values + index — a NumPy array with labels on top.
- **DataFrame**: a dict of Series that share a common index.
- **values**: the underlying NumPy array.
- **index**: row labels.
- **columns**: column labels.

## Before/After

**Before**: "A DataFrame is just a table" — only row-by-row thinking.

**After**: "A DataFrame is a collection of Series" — fluent column-wise operations.

## Hands-on: Building the Structures Yourself

### Step 1 — Create a Series and inspect

```python
import pandas as pd
s = pd.Series([1.0, 2.0, 3.0], index=["a", "b", "c"], name="x")
print(s.values, s.index, s.name)
```

A Series is not just a value container—it carries labels and a name alongside the data. Every subsequent alignment and arithmetic operation depends on those labels.

### Step 2 — Series arithmetic

```python
print(s * 10)
print(s + s)
```

Series arithmetic is not a simple loop—it is an index-aware array operation. This distinction is what makes label-based computation the core of Pandas.

## Series vs DataFrame Comparison

The relationship between these two structures becomes clearer in a table.

| Aspect | Series | DataFrame |
| --- | --- | --- |
| Dimensions | 1-D | 2-D |
| Index | Row labels | Row labels (shared) |
| Creation | `pd.Series(list, index=...)` | `pd.DataFrame(dict)` |

A DataFrame is a collection of Series sharing one index. That is why `df['column']` returns a Series, while `df[['column']]` returns a single-column DataFrame. Knowing this distinction prevents many type-related bugs.

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

The DataFrame above is exactly two Series placed side by side on a common index. Column-wise operations work naturally because each column already is its own Series.

### Step 4 — Column selection returns a Series

```python
col = df["x"]
print(type(col), col)
```

The fact that `df["x"]` returns a Series—not a DataFrame—is critical. Every method and operation you chain after column selection follows Series rules.

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

Pandas does not simply add values at the same position. It aligns by index first, computes where labels match, and inserts `NaN` where they do not.

## Multiple Ways to Create a DataFrame

The best creation method depends on what shape your source data is already in.

### From a dictionary

```python
df = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "age": [25, 30],
})
print(df)
```

The most intuitive method. Dictionary keys become column names; value lists become column contents.

### From a list of dictionaries

```python
data = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30},
]
df = pd.DataFrame(data)
print(df)
```

Common when parsing JSON API responses or log entries where data arrives row by row.

### From a NumPy array

```python
import numpy as np
arr = np.array([[1, 2], [3, 4], [5, 6]])
df = pd.DataFrame(arr, columns=["x", "y"])
print(df)
```

Pandas operates on NumPy arrays internally, so constructing from an array is natural and zero-copy when types align.

## Practical Example: Time Series Data

Time series data demonstrates the Series-to-DataFrame relationship concretely.

```python
dates = pd.date_range("2024-01-01", periods=5, freq="D")
temp = pd.Series([15, 16, 14, 17, 16], index=dates, name="temperature")
humidity = pd.Series([60, 65, 55, 70, 68], index=dates, name="humidity")
weather = pd.DataFrame({"temp": temp, "humidity": humidity})
print(weather)
print("\nMean temperature:", weather["temp"].mean())
```

In time series, the index is a date, and each column represents a measurement over time. Once you see this structure, time series analysis with Pandas becomes straightforward—resampling, rolling windows, and date filtering all build on this model.

## Performance Considerations

Understanding the internal structure of Series and DataFrame directly impacts performance.

### Prefer vectorized operations

```python
# Slow — Python loop
result = []
for val in df["x"]:
    result.append(val * 2)

# Fast — vectorized
result = df["x"] * 2
```

Column-wise operations delegate to NumPy's optimized C code. A Python loop over a million rows might take 2 seconds; the vectorized equivalent finishes in 5 milliseconds.

### Memory-efficient type selection

```python
# Default int64 uses 8 bytes per value
df["count"] = df["count"].astype("int32")  # 4 bytes — half the memory
df["category"] = df["category"].astype("category")  # categorical encoding
print(df.memory_usage(deep=True))
```

For large datasets, type selection can cut memory usage by 50–75%. This matters when you are loading 10 million rows and hitting swap.

### copy vs view

```python
# view — shares data with original
subset = df[["x", "y"]]

# copy — independent copy
subset = df[["x", "y"]].copy()
```

When you plan to modify a subset, make an explicit copy to avoid `SettingWithCopyWarning` and prevent silent bugs where the original DataFrame mutates unexpectedly.

## Dtype Inspection and Conversion

Each column in a DataFrame has a dtype. Verifying and converting types explicitly ensures correctness in downstream operations.

### Checking dtypes

```python
df = pd.DataFrame({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "score": [85.5, 90.0, 78.5],
})
print(df.dtypes)
```

**Expected output:**

```text
id         int64
name      object
score    float64
dtype: object
```

Pandas infers types automatically, but inference is not always correct—especially when reading CSVs where numeric IDs might load as `int64` when they should be strings.

### Converting dtypes

```python
df["id"] = df["id"].astype("string")
df["score"] = df["score"].astype("int32")
print(df.dtypes)
```

`astype()` converts explicitly. Common conversions: float to int (after confirming no decimals), numeric IDs to strings (to prevent accidental arithmetic), and object columns to `category` for memory savings.

### Memory-efficient types in practice

Since Pandas 1.0, smaller integer types (`int8`, `int16`, `int32`) and the dedicated `string` type are production-ready. For large datasets, switching a column of country codes from `object` to `category` often reduces memory by 90%+.

## Index Operations with fill_value

When indexes do not fully overlap, `NaN` appears. If that `NaN` is unintentional, use `fill_value` to provide a default.

```python
s1 = pd.Series([1, 2, 3], index=["a", "b", "c"])
s2 = pd.Series([10, 20], index=["b", "c"])
print(s1 + s2)
```

Index `a` has no counterpart in `s2`, so the result is `NaN`. If the correct default is zero:

```python
result = s1.add(s2, fill_value=0)
print(result)
```

Now `a` becomes `1 + 0 = 1` instead of `NaN`. This pattern is essential when combining incomplete data sources—sales from two regions where some dates have no transactions.

## Method Chaining

Pandas supports method chaining to compose multiple transformations into a readable pipeline.

```python
result = (df
    .assign(total=lambda x: x["price"] * x["qty"])
    .query("total > 100")
    .sort_values("total", ascending=False)
    .head(10)
)
print(result)
```

This pattern reads top-to-bottom like a recipe: compute a new column, filter, sort, take the top rows. However, chains longer than 5–6 steps become hard to debug. When that happens, break the chain into named intermediate DataFrames and inspect shapes at each step.

## Series Internal Structure

A Series manages a NumPy array and an Index object separately. Understanding this split helps with both performance tuning and debugging.

```python
s = pd.Series([1, 2, 3], index=["a", "b", "c"])
print("Data type:", s.dtype)
print("Array:", s.values)
print("Index:", s.index)
print("Memory:", s.memory_usage(deep=True), "bytes")
```

A Series can hold only one dtype. When you mix integers and strings, the dtype falls back to `object`, which disables NumPy vectorization and can slow operations by 10–100x. Always set dtype explicitly at creation time when you know what the data should be.

## What to Notice in This Code

- `df["x"]` returns a Series.
- Adding two Series triggers automatic index alignment.
- `NaN` is the signature of failed alignment—a debugging clue, not just missing data.

## Five Common Mistakes

1. **Confusing `df["x"]` with a DataFrame.** It is a Series—chain Series methods.
2. **Treating alignment `NaN` as ordinary missing data.** It signals an index mismatch.
3. **Always converting to NumPy via `.values` and losing labels.** Labels are the alignment mechanism.
4. **Ignoring the `name` attribute.** Named Series produce cleaner DataFrames when combined.
5. **Assuming two DataFrames share row order when added.** Pandas aligns by label, not position.

## How This Shows Up in Production

A/B test comparison, time series aggregation, joining data from multiple sources by index key—the reliability of Pandas rests on index alignment. In a real pipeline, you might join user events from Kafka with reference data from a database. If the indexes (user IDs, timestamps) do not align, Pandas surfaces the mismatch as `NaN` immediately, instead of silently computing wrong results.

## How a Senior Engineer Thinks

- Always be aware of what the index represents before computing.
- Treat column selection as the transition into Series thinking.
- Use `NaN` from misalignment as a debugging clue, not a nuisance.
- Reduce dependence on `df.values`—keep labels attached.
- Name your Series explicitly so combined DataFrames are self-documenting.

## Checklist

- [ ] I can distinguish Series and DataFrame.
- [ ] I can explain the role of index and column labels.
- [ ] I know `df["col"]` is a Series.
- [ ] I know index alignment is automatic.

## Practice Problems

1. Build three Series, combine them into a DataFrame, and confirm the common index.
2. Add two Series with different indexes and inspect the NaN positions.
3. Show in code the type difference between `df["x"]` and `df[["x"]]`.

## Wrap-up and next steps

A DataFrame is a collection of Series sharing a common index. This model explains why column selection returns a Series, why arithmetic aligns by label, and why dtype management happens per column. Next we cover reading CSV and Excel files accurately.

## Answering the Opening Questions

- **What is a Series internally?**
  - A Series is not just a value array—it is a one-dimensional structure carrying `values`, `index`, and `name` together. The article created `pd.Series([1.0, 2.0, 3.0], index=["a", "b", "c"], name="x")` and printed these attributes precisely to confirm this structure visually.
- **What does it mean to view a DataFrame as column-centric?**
  - Each column of a DataFrame is an independent Series, so extracting `df["x"]` immediately transitions to Series operation rules. That is why `df["x"]` returns a Series, and per-column type management and vectorized calculations naturally proceed column by column.
- **Why is the index more than just row numbers?**
  - Pandas aligns labels first and then computes, so the index is the computation reference itself. The `s1 + s2` example—where labels `a`, `b`, `c`, `d` are aligned and `NaN` appears where they do not overlap—clearly demonstrates this point.
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

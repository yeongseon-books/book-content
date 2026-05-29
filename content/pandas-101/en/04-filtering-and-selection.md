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

This is the 4th post in the Pandas 101 series.

My goal here is to organize selection tools as a small decision framework: labels, positions, and conditions. Once you think that way, the syntax choices become much easier to justify.


![pandas 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/04/04-01-concept-at-a-glance.en.png)
*pandas 101 chapter 4 flow overview*
> *Filtering is repeating at every stage of analysis. Slow or ambiguous selection code breaks everything downstream — treat this as a core skill, not syntax.

## Questions to Keep in Mind

- The difference between `loc` and `iloc`?
- The intuition behind boolean indexing?
- The readability of `query`?

## Why It Matters

Every step of analysis involves subset extraction. Slow or wrong selection shakes the whole pipeline—aggregation, joins, and visualization all depend on the subset being correct. That is why selection is not small syntax but the fundamental operation of analysis.

## Key Terms

- **loc**: label-based selection—pick by name.
- **iloc**: position-based selection—pick by integer offset.
- **boolean mask**: a True/False Series that selects rows.
- **query**: filter with a string expression.
- **isin**: check membership in a set of values.

## Before/After

**Before**: "Just use df[cond]" — chained indexing and warnings.

**After**: "Match tool to intent" — loc/iloc/query used deliberately.

## Hands-on: Five Selection Steps

### Step 1 — Column selection

```python
import pandas as pd
df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]}, index=["a", "b", "c"])
print(df["x"])
print(df[["x", "y"]])
```

Selecting one column returns a Series; selecting multiple returns a DataFrame. This difference directly affects method chaining and assignment behavior downstream.

### Step 2 — loc (label-based)

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

`loc` is clearest when both selecting and assigning—intent is visible in the code itself.

### Step 3 — iloc (position-based)

```python
print(df.iloc[0])
print(df.iloc[0:2, 0])
```

`iloc` is for when only position matters. Slicing feels like Python lists, but remember: you are addressing positions, not labels.

## Indexing Method Comparison

Pandas offers multiple indexing methods. Understanding their purpose and performance characteristics helps you choose the right tool.

| Method | Purpose | Speed |
| --- | --- | --- |
| `[]` | Column selection, condition filtering | Fast |
| `.loc` | Label-based selection, assignment | Medium |
| `.iloc` | Position-based selection | Fast |
| `.at` | Single-cell label access | Very fast |
| `.iat` | Single-cell position access | Very fast |

For most work, `loc` and `iloc` are sufficient. But inside loops accessing single values, `.at` and `.iat` provide a significant performance advantage.

### Step 4 — Boolean indexing

```python
print(df[df["x"] > 1])
print(df[(df["x"] > 1) & (df["y"] < 30)])
```

Boolean masks are the most common filtering pattern. When combining conditions, you must use parentheses and `&`/`|` (not `and`/`or`).

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

## Boolean Indexing in Detail

Boolean indexing is one of the most frequently used patterns in Pandas. Learning to write conditions clearly improves code readability significantly.

### Single condition

```python
df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})
mask = df["x"] > 1
print(mask)
print(df[mask])
```

The expression `df["x"] > 1` returns a boolean Series. Applying that Series back to the DataFrame keeps only rows where the value is True.

### Multiple conditions

```python
result = df[(df["x"] > 1) & (df["y"] < 30)]
print(result)
```

When combining conditions, each must be wrapped in parentheses. Use `&`/`|` instead of `and`/`or`—this is a common source of errors for beginners.

### Negation

```python
not_match = df[~(df["x"] > 1)]
print(not_match)
```

The `~` operator inverts a condition. Useful for selecting "rows that do NOT satisfy" a criterion.

## MultiIndex

MultiIndex sets multiple levels of labels on rows or columns. It is especially useful for hierarchical data.

### Creating a MultiIndex

```python
index = pd.MultiIndex.from_tuples([
    ("A", 1),
    ("A", 2),
    ("B", 1),
    ("B", 2),
], names=["category", "id"])
df = pd.DataFrame({"value": [10, 20, 30, 40]}, index=index)
print(df)
```

**Expected output:**

```text
               value
category id       
A        1       10
         2       20
B        1       30
         2       40
```

Hierarchical indexes represent grouped data naturally—city-by-date aggregations, for example.

### Accessing MultiIndex levels

```python
print(df.loc["A"])
print(df.loc[("A", 1)])
```

You can access by the first level alone or use a tuple for multi-level lookup. This pattern appears frequently when working with `groupby` results.

### Flattening

```python
flat = df.reset_index()
print(flat)
```

`reset_index()` moves index levels back into regular columns, creating a fresh integer index. This is often necessary before merging or exporting.

## Practical Example: Conditional Data Splitting

In production, you frequently split data by conditions for segment analysis.

```python
df = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "age": [25, 35, 45, 55, 65],
    "purchase": [100, 200, 150, 300, 250],
})

# Split by age group
young = df[df["age"] < 40]
middle = df[(df["age"] >= 40) & (df["age"] < 60)]
senior = df[df["age"] >= 60]

print(f"Young: {len(young)}, Middle: {len(middle)}, Senior: {len(senior)}")
print(f"Young avg purchase: {young['purchase'].mean()}")
```

This pattern is central to A/B testing, cohort analysis, and segment-level KPI computation.

## Performance Tips

### Boolean indexing vs query

```python
# Boolean indexing — fast
result1 = df[(df["x"] > 10) & (df["y"] < 50)]

# query — more readable for complex conditions
result2 = df.query("x > 10 and y < 50")
```

For simple conditions, boolean indexing is faster. For complex multi-clause filters, `query` wins on readability without meaningful speed loss.

### at/iat for single-value access

```python
# Slow — loc in a loop
for i in range(len(df)):
    value = df.loc[i, "column"]

# Fast — iat in a loop
for i in range(len(df)):
    value = df.iat[i, 0]
```

For single-value access inside loops, `at`/`iat` can be 5–10x faster than `loc`/`iloc`.

### Vectorized conditions over apply

```python
# Slow — apply with lambda
df["result"] = df["x"].apply(lambda x: x * 2 if x > 10 else x)

# Fast — vectorized with where
df["result"] = df["x"].where(df["x"] <= 10, df["x"] * 2)
```

Whenever possible, use vectorized operations instead of `apply`.

### Avoiding SettingWithCopyWarning

```python
# Bad — triggers warning
df[df["x"] > 0]["y"] = 100

# Good — use loc for assignment
df.loc[df["x"] > 0, "y"] = 100

# Good — explicit copy if you need a subset
subset = df[df["x"] > 0].copy()
subset["y"] = 100
```

Using `loc` for assignment or making explicit copies prevents silent bugs.

## What to Notice in This Code

- `loc` is endpoint-inclusive, `iloc` is endpoint-exclusive.
- `&` and `|` are bitwise operators—not `and/or`.
- `query` wins on readability with large expressions.

## Five Common Mistakes

1. **Using `and/or` in masks → error.** Need `&/|` and parentheses.
2. **Chained indexing**: `df[df["x"]>1]["y"] = ...` → SettingWithCopyWarning.
3. **Forgetting that `loc` is endpoint-inclusive.**
4. **Trying labels with `iloc`.**
5. **Replacing `isin` with long `|` chains.**

## How This Shows Up in Production

KPI dashboards, outlier detection, A/B test slicing—condition-based selection is the core of analysis functions. Many teams enforce `loc` as a code standard for assignment, and separate complex conditions into named variables to keep filtering logic readable during code review.

## How a Senior Engineer Thinks

- Extract complex conditions into named variables first.
- Always use `loc` for assignment—never chained indexing.
- Use `query` only when it wins on readability.
- Use `isin` and `between` to shorten repetitive logic.
- Never ignore warnings—they point to real bugs.

## Checklist

- [ ] I distinguish `loc` and `iloc`.
- [ ] I use `&/|` with parentheses for multiple conditions.
- [ ] I avoid chained indexing for assignment.
- [ ] I know when `query` and `isin` are appropriate.

## Practice Problems

1. Use `loc` to extract a subset of specific labels.
2. Use `iloc` to print the first 5 rows.
3. Express two or more conditions with `query`.

## Wrap-up and next steps

Selection is the most frequently repeated primitive in analysis. Choosing the right tool for the intent—labels, positions, or conditions—keeps downstream aggregation and joins stable. Next we tackle missing value handling.

## Answering the Opening Questions

- **When should you distinguish between `loc` and `iloc`?**
  - Use `loc` when names are the reference and `iloc` when numeric positions are the reference. The article contrasted `df.loc[["a", "c"], "x"]` for readable label access with `df.iloc[0:2, 0]` for pure positional slicing.
- **In what situations are boolean masks most natural?**
  - Boolean masks are most direct when you need to select rows whose values satisfy a condition. Creating a boolean Series with `df[df["x"] > 1]` or `(df["x"] > 1) & (df["y"] < 30)` makes it immediately readable which rows survive.
- **Why does `query` become more readable as expressions grow longer?**
  - As conditions lengthen, brackets and parentheses pile up, but `df.query("x > 1 and y < 30")` lays them out like a sentence. Combined with `isin([1, 3])`, intent remains clearer than long OR chains.
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

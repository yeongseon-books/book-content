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


![pandas 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/01/01-01-concept-at-a-glance.en.png)
*pandas 101 chapter 1 flow overview*
> *Pandas is the standard language for reading, exploring, reshaping, and summarizing tabular data* within the memory you have. Master this layer first.

## Questions to Keep in Mind

- The *definition* of *Pandas* and where it sits?
- The intuition behind *Series* and *DataFrame?
- The basic *load → inspect → summarize* workflow?

## Why It Matters

CSV, Excel, databases, APIs — *80% of real-world data* is *tabular*. If you cannot drive *Pandas*, you cannot start *data analysis*.

If your data fits in memory, Pandas is still the most practical starting point. Data science, report automation, machine learning preprocessing, and operational metric calculation all connect from here.

> *If your data fits in memory, Pandas is usually the right answer.*

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

Pandas work almost always starts with `import pandas as pd`. Checking the version first helps when reproducing examples or reconciling environment differences within a team. This series is written for Pandas 2.x.

### Step 2 — Build a Series

```python
s = pd.Series([10, 20, 30], index=["a", "b", "c"])
print(s)
print("sum:", s.sum())
```

A Series is a one-dimensional structure where values and an index move together. It looks like a simple list, but sum, sort, and label-based operations are available immediately.

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

`shape`, `dtypes`, and `describe()` form the first inspection set when you receive any table. Row count, column types, and distribution — these three lines cover the basics.

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

## Pandas vs. Pure Python

Before adopting Pandas, a natural question arises: can you handle tabular data with just Python lists and dicts? You can — but the code length and performance gap grow quickly.

| Task | Pure Python | Pandas |
| --- | --- | --- |
| Filter | `[x for x in data if x['age'] > 30]` | `df[df['age'] > 30]` |
| Aggregate | `sum([x['amount'] for x in data])` | `df['amount'].sum()` |
| Sort | `sorted(data, key=lambda x: x['name'])` | `df.sort_values('name')` |

Pure Python requires multiple loops and comprehensions. Pandas handles all of these as single-line column-oriented operations. The performance difference exists, but the more important gain is readability — the intent of "work on a table" becomes explicit in the syntax itself.

## The Pandas Ecosystem

Pandas does not operate in isolation. It sits at the center of the Python data science ecosystem.

### NumPy

Pandas is built on top of NumPy arrays internally. The `.values` attribute of any Series or DataFrame returns the underlying NumPy array directly.

```python
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
s = pd.Series(arr)
print(type(s.values))  # <class 'numpy.ndarray'>
```

You do not need to use NumPy directly, but understanding that Pandas speed comes from NumPy's optimized C code helps explain why vectorization matters.

### Matplotlib

Pandas DataFrames connect directly to visualization. The built-in `.plot()` method uses Matplotlib as a backend.

```python
import matplotlib.pyplot as plt
df = pd.DataFrame({'x': [1, 2, 3], 'y': [10, 20, 15]})
df.plot(x='x', y='y', kind='line')
plt.show()
```

For complex visualizations you move to Seaborn or Plotly, but for quick exploration Pandas built-in plots are sufficient.

### scikit-learn

Machine learning preprocessing almost always starts in Pandas. You read, clean, and extract features, then pass the result to scikit-learn as a NumPy array or DataFrame.

```python
from sklearn.linear_model import LinearRegression
X = df[['feature1', 'feature2']].values
y = df['target'].values
model = LinearRegression().fit(X, y)
```

Think of Pandas as the preprocessing layer and scikit-learn as the model layer.

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

## Practical Example: Sales Data

Combining what you have learned so far into a simple sales data analysis:

```python
sales = pd.DataFrame({
    "product": ["A", "B", "C", "A", "B"],
    "quantity": [10, 15, 8, 12, 20],
    "price": [100, 150, 80, 100, 150],
})
sales["total"] = sales["quantity"] * sales["price"]
print(sales)
print("\nTotal revenue:", sales["total"].sum())
print("Mean quantity per product:", sales.groupby("product")["quantity"].mean())
```

This example covers DataFrame creation, column addition, aggregation, and grouping. Real-world data is far more complex, but the underlying principles are identical.

## Debugging Tips

### Unexpected results

Always check size and types first:

```python
print(df.shape)    # (rows, columns)
print(df.dtypes)   # column types
print(df.head())   # first 5 rows
```

### SettingWithCopyWarning

This warning appears with chained indexing. Use `.loc` for explicit assignment:

```python
# Bad
df[df['x'] > 0]['y'] = 100

# Good
df.loc[df['x'] > 0, 'y'] = 100
```

## Pandas vs. Other Tools

Pandas is not the only option. Knowing the alternatives helps you choose for the situation.

| Scenario | Recommended tool |
| --- | --- |
| Fits in memory (<10 GB) | Pandas |
| Parallel processing needed (>10 GB) | Dask |
| Distributed cluster | Spark |
| Maximum single-machine performance | Polars |

For most analysis work, Pandas is sufficient.

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

Pandas is the *standard language for tabular data*. Once you establish this starting point, selection, aggregation, merging, and time series processing in later chapters all connect within the same syntax. Next we go deep into the *internal structure* of *Series and DataFrame*.

## Answering the Opening Questions

- **What problem does Pandas solve exactly?**
  - Pandas lifts tabular data—arriving as CSV or Excel—into an in-memory DataFrame and lets you read, inspect, and transform it with concise code. The article's immediate flow from `pd.read_csv` to `shape`, `dtypes`, and `describe()` demonstrates that role.
- **How should you understand the relationship between Series and DataFrame?**
  - A Series is a one-dimensional structure with an index, and a DataFrame bundles multiple such columns into a single table. The examples built a Series with `pd.Series([10, 20, 30], index=["a", "b", "c"])` and then expanded to a DataFrame with `name` and `age` columns, showing this relationship.
- **Why do so many analysis tasks start with Pandas?**
  - Because most real-world data ultimately arrives in tabular form, and Pandas lets you check size, verify types, and filter by conditions all in one place. Examples like `df[df["age"] > 40]` and `sales.groupby("product")["quantity"].mean()` show that subsequent aggregation and preprocessing continue with the same syntax.
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

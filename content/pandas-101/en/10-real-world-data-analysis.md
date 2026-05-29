---
series: pandas-101
episode: 10
title: "Pandas 101 (10/10): Real-World Data Analysis"
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
  - DataAnalysis
  - EDA
  - Workflow
  - Beginner
seo_description: Tie load, clean, transform, aggregate, and visualize into one reproducible end-to-end Pandas analysis pipeline
last_reviewed: '2026-05-15'
---

# Pandas 101 (10/10): Real-World Data Analysis

The earlier chapters covered loading, cleaning, selecting, grouping, joining, time handling, and performance habits one piece at a time. Real analysis becomes useful only when those pieces connect into one repeatable flow. That is usually where the gap between knowing Pandas features and delivering analysis results becomes visible.

This is the final post in the Pandas 101 series.

In this chapter, we will connect everything into one standard workflow: load, clean, enrich, aggregate, and visualize. The goal is not a flashy notebook. It is a pipeline you can rerun, review, and share with confidence.


![pandas 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/10/10-01-concept-at-a-glance.en.png)
*pandas 101 chapter 10 flow overview*
> *Analysis is *iteration*. First read is never perfect, first aggregation is never final, you always come back to re-validate.

## Questions to Keep in Mind

- In what order should you process tabular data after reading it?
- What improves when you split analysis code into function units?
- What should you pay attention to for reproducible aggregation results?

## Why It Matters

Knowing each tool separately is not the same as producing a result. Professional analysts are defined by their ability to connect raw data to actionable output in a flow that is reproducible, debuggable, and shareable.

## Key Terms

- **EDA**: Exploratory Data Analysis — the initial analysis flow for understanding data.
- **Pipeline**: ordered transformation steps.
- **Reproducibility**: same input → same output.
- **KPI**: key performance indicator.
- **Notebook**: an environment that records analysis and outcome together.
- **Dependency management**: recording the library versions used in analysis.

### Performance Optimization Techniques

When working with large datasets, performance matters. The following table summarizes key optimization techniques and their expected effects.

| Technique | Description | Effect |
|---|---|---|
| Vectorization | Use column-level operations | 10–100x vs apply |
| apply removal | Replace with built-in functions | Moderate speedup |
| dtype optimization | int64 → int32, object → category | 30–70% memory reduction |
| eval/query | String expression acceleration | Faster for complex expressions |
| Chunk processing | Read files in parts | Prevents memory overflow |

Vectorization gives the largest speedup, but dtype optimization can also dramatically reduce memory. The category type is especially effective for columns with few unique values.

## Before/After

**Before**: all steps crammed into a single script or cell — cannot rerun reliably.

**After**: load, clean, transform, aggregate split into functions — reproducible, testable, shareable.

## Hands-on: Going End-to-End in Five Steps

### Step 1 — Load

```python
import pandas as pd

def load(path):
    return pd.read_csv(path, parse_dates=["date"])

df = load("sales.csv")
print(df.shape)
```

The load step is the starting point for everything that follows. Parsing date columns at read time simplifies all downstream time-based aggregation.

### Step 2 — Clean

```python
def clean(df):
    df = df.dropna(subset=["sales"])
    df["sales"] = df["sales"].astype(float)
    return df

df = clean(df)
```

The clean step handles missing-value removal and type correction. Keeping it in a separate function makes the cleaning rules explicit and auditable.

### Step 3 — Transform

```python
def enrich(df):
    df["month"] = df["date"].dt.to_period("M")
    return df

df = enrich(df)
```

This step creates columns that do not exist in the raw data. In practice, derived variables and feature engineering happen here.

### Step 4 — Aggregate (KPI)

```python
def kpi(df):
    return df.groupby("month").agg(
        total=("sales", "sum"),
        n=("sales", "count"),
        mean=("sales", "mean"),
    )

monthly = kpi(df)
print(monthly)
```

A monthly KPI table is a great checkpoint because it proves the pipeline actually made it from raw input to a business-facing summary. Once this table looks right, visualization becomes a presentation step instead of a debugging step.

**Expected output:**

```text
         total  n   mean
month                    
2026-01  450.0  3  150.0
2026-02  520.0  4  130.0
```

The aggregation function is the core of producing a result table. It gathers key metrics — total, count, average — in one place aligned to the analysis goal.

### Step 5 — Visualize

```python
import matplotlib.pyplot as plt
monthly["total"].plot(kind="bar", title="Monthly Sales")
plt.tight_layout()
plt.savefig("monthly.png")
```

Do not stop at rendering inside a notebook cell. Saving the figure turns the chart into a reusable artifact for reviews, reports, and scheduled jobs. A clear save path also connects directly to pipeline automation.

**Expected output:**

```text
monthly.png saved
```

Seeing a chart alongside numeric tables makes trends and outliers far easier to spot. Saving the result as a file makes sharing and later review straightforward.

### Large Data Section

When data does not fit comfortably in memory, file format and dtype choices must be considered together.

#### Parquet format

Switching from CSV to Parquet dramatically improves both file size and read speed.

```python
import pandas as pd

# large data example
df = pd.DataFrame({
    "id": range(10_000_000),
    "value": range(10_000_000),
})

# save as CSV
df.to_csv("large.csv", index=False)

# save as Parquet
df.to_parquet("large.parquet", index=False)

# compare file sizes
import os
csv_size = os.path.getsize("large.csv") / 1024 / 1024
parquet_size = os.path.getsize("large.parquet") / 1024 / 1024
print(f"CSV: {csv_size:.1f} MB")
print(f"Parquet: {parquet_size:.1f} MB")
```

**Expected output:**

```text
CSV: 171.7 MB
Parquet: 38.2 MB
```

Parquet is a columnar storage format with much better compression and read speed than CSV. The difference is especially pronounced when repeatedly reading large datasets.

#### category dtype

Converting columns with few unique values to category type can dramatically reduce memory.

```python
df = pd.DataFrame({
    "country": ["KR", "US", "JP"] * 1_000_000,
    "value": range(3_000_000),
})

print(f"Before: {df['country'].memory_usage(deep=True) / 1024 / 1024:.1f} MB")

df["country"] = df["country"].astype("category")
print(f"After: {df['country'].memory_usage(deep=True) / 1024 / 1024:.1f} MB")
```

**Expected output:**

```text
Before: 171.7 MB
After: 2.9 MB
```

Category type not only reduces memory but also speeds up operations like groupby.

#### Chunk reading

When files are too large to load at once, read them in parts.

```python
# read only a subset
df = pd.read_csv("large.csv", nrows=100_000)

# read in chunks
for chunk in pd.read_csv("large.csv", chunksize=100_000):
    # process each chunk
    print(chunk.shape)
```

Loading a huge file all at once can exhaust memory. Chunk-based processing keeps memory usage under control.

### Practical Example: Monthly Report Automation

This example shows the full pipeline with function-level separation.

```python
import pandas as pd
import matplotlib.pyplot as plt

def load_data(path):
    return pd.read_csv(path, parse_dates=["date"])

def clean_data(df):
    df = df.dropna(subset=["sales"])
    df["sales"] = df["sales"].astype(float)
    return df

def add_features(df):
    df["month"] = df["date"].dt.to_period("M")
    df["dayofweek"] = df["date"].dt.dayofweek
    return df

def monthly_kpi(df):
    return df.groupby("month").agg(
        total_sales=("sales", "sum"),
        avg_sales=("sales", "mean"),
        order_count=("sales", "count"),
    )

def plot_trend(monthly, path):
    monthly["total_sales"].plot(kind="line", title="Monthly Sales Trend")
    plt.ylabel("Sales")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

# full pipeline
df = load_data("sales.csv")
df = clean_data(df)
df = add_features(df)
monthly = monthly_kpi(df)
plot_trend(monthly, "monthly_sales.png")
monthly.to_csv("monthly_kpi.csv")
print("\nMonthly KPI:")
print(monthly)
```

This pattern demonstrates a function-separated pipeline. Each function has a single responsibility, making testing and debugging easy, and the overall flow readable.

### Before/After Benchmark

Seeing the performance difference firsthand is the most effective way to internalize vectorization.

```python
import pandas as pd
import numpy as np
import time

# 1 million rows
df = pd.DataFrame({
    "a": np.arange(1_000_000),
    "b": np.arange(1_000_000),
})

# Before: apply(axis=1)
start = time.time()
df["c_slow"] = df.apply(lambda r: r["a"] + r["b"], axis=1)
slow = time.time() - start

# After: vectorized
start = time.time()
df["c_fast"] = df["a"] + df["b"]
fast = time.time() - start

print(f"apply(axis=1): {slow:.3f}s")
print(f"Vectorized: {fast:.3f}s")
print(f"Speedup: {slow/fast:.1f}x")
```

**Expected output:**

```text
apply(axis=1): 12.450s
Vectorized: 0.005s
Speedup: 2490.0x
```

The same computation can differ by thousands of times depending on vectorization. On large data, this gap shows up as minutes versus hours.

### Conditional Branch Benchmark

```python
# Before: loop
start = time.time()
result = []
for val in df["a"]:
    result.append("even" if val % 2 == 0 else "odd")
df["flag_slow"] = result
slow = time.time() - start

# After: np.where
start = time.time()
df["flag_fast"] = np.where(df["a"] % 2 == 0, "even", "odd")
fast = time.time() - start

print(f"Loop: {slow:.3f}s")
print(f"np.where: {fast:.3f}s")
print(f"Speedup: {slow/fast:.1f}x")
```

**Expected output:**

```text
Loop: 0.450s
np.where: 0.025s
Speedup: 18.0x
```

Conditional branching also speeds up significantly when vectorized. Prefer `np.where`, `np.select`, and `pd.cut` before reaching for loops.

## What to Notice in This Code

- Function-level separation makes each step independently testable.
- `parse_dates` is the starting point for time series analysis.
- Pandas built-in plotting is very practical for quick visual checks.

## Five Common Mistakes

1. **Putting all steps in a single cell or script.**
2. **Not saving or inspecting intermediate results.**
3. **Not documenting column names and meanings.**
4. **Concluding from tables only, skipping visualization.**
5. **Ignoring reproducibility — no seed or version pinning.**

## How This Shows Up in Production

KPI report automation, marketing analytics, ops dashboards — analysis pipelines become reusable libraries. Teams run Jupyter notebooks alongside Python modules, using notebooks for exploration and explanation, and modules for reuse and automation.

## How a Senior Engineer Thinks

- Split into load, clean, transform, aggregate functions.
- Add brief docstrings and light tests to each function.
- Diagram the raw → result flow.
- Pair visualization with numeric summary.
- Record version, seed, and execution timestamp.

## Checklist

- [ ] I split load/clean/enrich/kpi/visualize into functions.
- [ ] I produce a visualization output.
- [ ] I document column specs.
- [ ] I confirm reproducibility.

## Practice Problems

1. Build a small project with the four functions load/clean/enrich/kpi.
2. Compute monthly and weekly KPIs simultaneously.
3. Save the result as both PNG and CSV.

## Wrap-up and next steps

You have completed Pandas 101. The basic workflow of reading, cleaning, transforming, aggregating, and visualizing tabular data reappears on virtually every path in data work. Next stops: Polars or Dask for scaling, Matplotlib or Plotly for richer visualization, then scikit-learn for ML preprocessing. Every road in data work starts at Pandas.

## Answering the Opening Questions

- **In what order should you process tabular data after reading it?**
  - This article followed the flow of load, clean, add derived columns, compute KPIs, and visualize. The `load()`, `clean()`, `enrich()`, `kpi()` functions and `monthly["total"].plot(...)` example show how read data connects to result tables and charts.
- **What improves when you split analysis code into function units?**
  - Each step's responsibility becomes clear, making testing, re-execution, and debugging easier. For example, if `clean_data()` handles only missing-value removal and type conversion while `monthly_kpi()` handles only aggregation, you can quickly trace at which step results diverged.
- **What should you pay attention to for reproducible aggregation results?**
  - The same input, same version, and same transformation rules must reproduce the output at any time, so you need to preserve function structure, output files, and execution conditions together. The article bundled `monthly.to_csv("monthly_kpi.csv")`, `plt.savefig("monthly_sales.png")`, `parse_dates`, dtype optimization, and chunk processing because reproducibility and operability must be secured simultaneously.
<!-- toc:begin -->
## In this series

- [Pandas 101 (1/10): What Is Pandas?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): Series and DataFrame](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): Reading CSV and Excel](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): Filtering and Selection](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): Handling Missing Values](./05-missing-values.md)
- [Pandas 101 (6/10): Groupby and Aggregation](./06-groupby.md)
- [Pandas 101 (7/10): Merge and Join](./07-merge-and-join.md)
- [Pandas 101 (8/10): Time Series](./08-time-series.md)
- [Pandas 101 (9/10): Apply and Vectorization](./09-apply-and-vectorization.md)
- **Real-World Data Analysis (current)**

<!-- toc:end -->

## References

- [pandas — Cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html)
- [pandas — Visualization](https://pandas.pydata.org/docs/user_guide/visualization.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)
- [Kaggle — Pandas Course](https://www.kaggle.com/learn/pandas)

Tags: Pandas, DataAnalysis, EDA, Workflow, Beginner

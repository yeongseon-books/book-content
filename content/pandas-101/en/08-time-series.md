---
series: pandas-101
episode: 8
title: "Pandas 101 (8/10): Time Series"
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
  - TimeSeries
  - Resample
  - Datetime
  - Beginner
seo_description: Work with DatetimeIndex, resample, rolling, and time zones — the standard Pandas toolkit for time series, with code
last_reviewed: '2026-05-15'
---

# Pandas 101 (8/10): Time Series

Sales, traffic, sensor, and financial data often stop behaving like ordinary tables once time becomes the main organizing dimension. If dates stay as strings, comparisons feel awkward and weekly summaries or moving averages become noisier to implement than they should be. The whole experience changes once time becomes the index.

This is the 8th post in the Pandas 101 series.

In this chapter, we will keep time series work inside core Pandas patterns. The focus is on DatetimeIndex, time-aware grouping, rolling windows, and explicit time-zone handling.


![pandas 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/08/08-01-concept-at-a-glance.en.png)
*pandas 101 chapter 8 flow overview*
> *Time series is about *order and frequency*. Skip the date index, miss a time period, or ignore seasonality and your trend analysis crumbles.

## Questions to Keep in Mind

- The intuition of *DatetimeIndex?
- resample* and *rolling?
- Handling *time zones (tz)?

## Why It Matters

Sales, traffic, sensors, finance — *most operational data* is time series. Treating *time as an index* makes *KPI trends* visible immediately. Weekly totals, monthly averages, moving averages, and day-over-day changes all become short, stable code once the time axis is set up correctly.

## Key Terms

- **DatetimeIndex**: an index of *time labels*.
- **resample**: *change time granularity* — daily to weekly etc.
- **rolling**: *moving window* statistics.
- **shift**: *push rows in time*.
- **tz_localize / tz_convert**: *attach / convert* time zones.

### String Method Comparison

The following table summarizes key Pandas string accessor (`str`) methods, their regex support, and practical examples.

| Method | Regex Support | Returns | Example |
|---|---|---|---|
| `str.contains()` | ● | bool Series | `s.str.contains("error")` |
| `str.extract()` | ● | DataFrame | `s.str.extract(r"(\d+)")` |
| `str.replace()` | ● | Series | `s.str.replace("old", "new")` |
| `str.split()` | - | list Series | `s.str.split(",")` |
| `str.lower()` | - | Series | `s.str.lower()` |
| `str.strip()` | - | Series | `s.str.strip()` |

String methods are essential for text cleaning, log parsing, and tag extraction. `contains` and `extract` support regex, making complex pattern handling efficient.

## Before/After

**Before**: *"Date columns as strings"* — *comparison, filter, aggregation are clumsy*.

**After**: *"Convert to DatetimeIndex"* — natural *string slicing* like *df.loc["2026-05"]*.

## Hands-on: Five Time Series Steps

### Step 1 — Build a DatetimeIndex

```python
import pandas as pd
idx = pd.date_range("2026-01-01", periods=10, freq="D")
ts = pd.Series(range(10), index=idx)
print(ts.head())
```

The starting point of time series work is promoting time from a string to a proper DatetimeIndex. From that moment, Pandas' time series syntax becomes available.

### Step 2 — Time slicing

```python
print(ts.loc["2026-01-03":"2026-01-06"])
```

With a DatetimeIndex, string slicing selects date ranges naturally. Picking a specific month, week, or date range becomes trivial.

### Step 3 — resample

```python
print(ts.resample("3D").sum())
```

Resampling makes the time-axis transformation visible. Once you see daily data collapse into three-day buckets, the difference between plain aggregation and time-aware aggregation becomes much easier to reason about.

**Expected output:**

```text
2026-01-01     3
2026-01-04    12
2026-01-07    21
2026-01-10     9
Freq: 3D, dtype: int64
```

`resample()` regroups data into new time units and computes aggregates. Converting daily data into 3-day or weekly buckets is its primary job.

### Step 4 — rolling

```python
print(ts.rolling(window=3).mean())
```

Rolling window calculations smooth out short-term noise. Moving averages are particularly useful for reading trends in volatile operational data.

### Step 5 — Time zones

```python
ts2 = ts.tz_localize("UTC").tz_convert("Asia/Seoul")
print(ts2.head())
```

Time-zone conversion is one of those details that feels abstract until you print it. The output shows the same underlying instants represented in a different local clock.

**Expected output:**

```text
2026-01-01 09:00:00+09:00    0
2026-01-02 09:00:00+09:00    1
2026-01-03 09:00:00+09:00    2
2026-01-04 09:00:00+09:00    3
2026-01-05 09:00:00+09:00    4
Freq: D, dtype: int64
```

Time zones must be attached first, then converted. Mixing tz-naive and tz-aware objects leads to comparison and merge errors.

### datetime Accessor Examples

When you have a date column, the `dt` accessor extracts year/month/day/weekday components directly.

```python
import pandas as pd

df = pd.DataFrame({
    "date": pd.date_range("2026-01-01", periods=5, freq="D"),
    "value": [10, 20, 30, 40, 50],
})

df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["dayofweek"] = df["date"].dt.dayofweek  # 0=Monday
df["quarter"] = df["date"].dt.quarter

print(df.head())
```

**Expected output:**

```text
        date  value  year  month  dayofweek  quarter
0 2026-01-01     10  2026      1          3        1
1 2026-01-02     20  2026      1          4        1
2 2026-01-03     30  2026      1          5        1
3 2026-01-04     40  2026      1          6        1
4 2026-01-05     50  2026      1          0        1
```

Extracting components from dates makes monthly, quarterly, and day-of-week aggregation straightforward. `dayofweek` is particularly useful for weekday/weekend pattern analysis.

### resample Patterns

Converting time series data to different frequencies with `resample` is extremely common in practice.

```python
# Daily data to weekly sum
df = df.set_index("date")
weekly = df.resample("W")["value"].sum()
print(weekly)
```

**Expected output:**

```text
date
2026-01-04     60
2026-01-11    130
Freq: W-SUN, Name: value, dtype: int64
```

`resample` is the tool for time-axis regrouping. Monthly sales, weekly traffic, hourly sensor values — these operational metrics all rely on it.

### Category Type Conversion

String-based categorical data benefits significantly from conversion to the category dtype.

#### Benefits of Category Type

1. **Memory savings**: stores strings as integer codes.
2. **Speed improvement**: groupby and comparisons run faster.
3. **Order preservation**: you can specify a meaningful ordering for ordinal values.

```python
import pandas as pd

df = pd.DataFrame({
    "city": ["Seoul", "Busan", "Seoul", "Busan"] * 25000,
    "value": range(100000),
})

# Before conversion
print(f"String: {df['city'].memory_usage(deep=True) / 1024:.1f} KB")

# After conversion
df["city"] = df["city"].astype("category")
print(f"Category: {df['city'].memory_usage(deep=True) / 1024:.1f} KB")
```

Columns with few unique values see massive memory reduction from category conversion. Cities, countries, and status codes are typical candidates.

#### Ordered Categories

Category dtype supports explicit ordering for ordinal values.

```python
from pandas.api.types import CategoricalDtype

sizes = ["S", "M", "L", "M", "S", "L"]
cat_type = CategoricalDtype(categories=["S", "M", "L"], ordered=True)
s = pd.Series(sizes, dtype=cat_type)

print(s.sort_values())
print(s > "S")  # comparison works
```

**Expected output:**

```text
4    S
0    S
1    M
3    M
2    L
5    L
dtype: category
Categories (3, object): ['S' < 'M' < 'L']

0    False
1     True
2     True
3     True
4    False
5     True
dtype: bool
```

Ordered categories make sorting and comparison semantically meaningful. Useful for Likert scales, grades, priority levels, and similar ordinal data.

## What to Notice in This Code

- *String slicing* feels natural only on a *DatetimeIndex*.
- *resample* must be paired with an *aggregation function*.
- *Time zones* are *attached first*, then *converted*.

## Five Common Mistakes

1. **Skipping *to_datetime* and using strings as-is.**
2. **Calling *resample* without an *aggregation*.**
3. **Skipping *min_periods* on *rolling*.**
4. **Mixing *tz-naive* and *tz-aware* objects.**
5. **Forgetting to handle *NaN* after *shift*.**

## How This Shows Up in Production

Sales trends, user activity patterns, IoT sensor monitoring — *time-bucket conversion and window statistics* are the core of *KPI dashboards*. *Time-zone normalization* is mandatory for *global services*.

## How a Senior Engineer Thinks

- Normalize all time to *UTC* before analysis.
- Choose *resample frequency* by *analysis intent*.
- Handle *boundary NaN* from *rolling* explicitly.
- Use *interpolate* for *time series gaps*.
- Use *shift* as a *feature engineering* primitive.

## Checklist

- [ ] I create a *DatetimeIndex*.
- [ ] I call *resample* with an *aggregation*.
- [ ] I compute a *moving average* with *rolling*.
- [ ] I run *tz_convert*.

### Practical Example: Weekly Sales Analysis

In practice, time series analysis often combines resampling with moving averages.

```python
import pandas as pd
import numpy as np

# Daily sales data
dates = pd.date_range("2026-01-01", periods=30, freq="D")
sales = np.random.randint(80, 150, size=30)
df = pd.DataFrame({"sales": sales}, index=dates)

# Weekly sum
weekly = df.resample("W").sum()

# 7-day moving average
df["ma7"] = df["sales"].rolling(window=7).mean()

print("\nWeekly totals:")
print(weekly.head())
print("\nMoving average (last 5 days):")
print(df[["sales", "ma7"]].tail())
```

This pattern is highly useful for understanding trends in daily data. Weekly totals reveal weekly-level patterns, while the moving average smooths short-term volatility to expose the underlying trend.

## Practice Problems

1. *Resample* a *daily series* into a *weekly sum*.
2. Build a *7-day moving average* and handle *boundary NaN*.
3. Print the result of *UTC → Asia/Seoul* conversion.

## Wrap-up and next steps

Time series is *a Pandas strength*. Next we cover *apply and vectorization*.

## Answering the Opening Questions

- **What changes when you set a date column as the index?**
  - Promoting dates to a `DatetimeIndex` connects time-range selection, resampling, and rolling calculations to Pandas' native syntax. The biggest change is that string slicing like `ts.loc["2026-01-03":"2026-01-06"]` alone is enough to cut a period.
- **How does resampling differ from simple aggregation?**
  - Resampling is not merely summing values—it changes the time axis's unit and re-groups accordingly. Converting daily data into 3-day or weekly units with `ts.resample("3D").sum()` or `df.resample("W")["value"].sum()` is what distinguishes it from regular aggregation.
- **How do you perform window-based calculations like moving averages?**
  - Create a rolling window and compute statistics per window with `rolling(window=3).mean()`. The article mentioned a 7-day moving average, boundary `NaN` values, and value interpretation after `shift()` together because window-based calculations smooth trends but boundary conditions must always be examined alongside.
<!-- toc:begin -->
## In this series

- [Pandas 101 (1/10): What Is Pandas?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): Series and DataFrame](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): Reading CSV and Excel](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): Filtering and Selection](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): Handling Missing Values](./05-missing-values.md)
- [Pandas 101 (6/10): Groupby and Aggregation](./06-groupby.md)
- [Pandas 101 (7/10): Merge and Join](./07-merge-and-join.md)
- **Time Series (current)**
- Apply and Vectorization (upcoming)
- Real-World Data Analysis (upcoming)

<!-- toc:end -->

## References

- [pandas — Time series / date functionality](https://pandas.pydata.org/docs/user_guide/timeseries.html)
- [pandas — resample](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html)
- [pandas — rolling](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html)
- [Forecasting — Hyndman & Athanasopoulos](https://otexts.com/fpp3/)

Tags: Pandas, TimeSeries, Resample, Datetime, Beginner

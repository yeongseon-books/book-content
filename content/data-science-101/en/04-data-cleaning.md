---
series: data-science-101
episode: 4
title: Data Cleaning
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DataScience
  - DataCleaning
  - Pandas
  - Quality
  - Beginner
seo_description: A 5-step guide to spotting and fixing missing values, duplicates, outliers, and type mismatches in real-world tabular data
last_reviewed: '2026-05-04'
---

# Data Cleaning

> Data Science 101 series (4/10)

<!-- a-grade-intro:begin -->

**Core question**: In what *order* should we find and fix *missing values, duplicates, outliers, and type mismatches*?

> *80% of the time goes into cleaning — good cleaning makes the other 20% *real* analysis.*

<!-- a-grade-intro:end -->

This is post 4 in the Data Science 101 series.

## What You Will Learn

- The *four big data-quality problems*
- Strategies for *handling missing values*
- The basics of *outlier detection*
- A 5-step cleaning exercise
- Five common pitfalls

## Why It Matters

*Garbage in, garbage out.* Even the best model produces *garbage* from dirty input. Cleaning is the *validation step*.

> *Cleaning is the *insurance policy* of analysis.*

## Concept at a Glance

```mermaid
flowchart LR
    Raw["Raw Data"] --> Type["Fix Types"]
    Type --> Dup["Drop Duplicates"]
    Dup --> Null["Handle Missing"]
    Null --> Out["Detect Outliers"]
    Out --> Clean["Clean Data"]
```

## Key Terms

- **Missing**: a value is *empty* (`NaN`, `None`, `''`).
- **Duplicate**: multiple rows with the *same key*.
- **Outlier**: a value *statistically far* from the rest.
- **Type coercion**: converting *strings to numbers/dates*.
- **Imputation**: a strategy to *fill in* missing values.

## Before / After

**Before**: `signup_at` is a *string*, so date comparisons return *wrong results*.

**After**: convert with `pd.to_datetime`, and comparisons are *correct*.

## Hands-on: 5-step Cleaning

### Step 1 — Fix types

```python
import pandas as pd
df = pd.read_csv("users.csv")
df["signup_at"] = pd.to_datetime(df["signup_at"], errors="coerce")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
```

### Step 2 — Drop duplicates

```python
print("before:", len(df))
df = df.drop_duplicates(subset=["user_id"], keep="last")
print("after :", len(df))
```

### Step 3 — Handle missing values

```python
# Inspect missingness
print(df.isna().mean().sort_values(ascending=False).head())

# Strategy: drop critical, fill optional
df = df.dropna(subset=["user_id", "signup_at"])
df["country"] = df["country"].fillna("UNKNOWN")
```

### Step 4 — Detect outliers

```python
q1, q3 = df["amount"].quantile([0.25, 0.75])
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
df["amount_flag"] = ~df["amount"].between(lower, upper)
print(df["amount_flag"].mean())
```

### Step 5 — Validation report

```python
report = {
    "rows": len(df),
    "nulls": df.isna().sum().to_dict(),
    "outlier_rate": float(df["amount_flag"].mean()),
}
print(report)
```

## What to Notice in This Code

- *Fixing types* is the starting point of all cleaning.
- Always inspect *missingness rates first*.
- Outliers should be *flagged*, not dropped on sight.

## Five Common Mistakes

1. **Filling missing with `0`.** Averages get *distorted*.
2. **Silently dropping *duplicates*.** You never learn *why* they appeared.
3. **Deleting *outliers* immediately.** They could be the *real signal*.
4. **Ignoring *type-conversion errors*.** Use `errors="raise"` to surface them.
5. **Not documenting *cleaning steps*.** The analysis is no longer reproducible.

## How This Shows Up in Production

Teams test cleaning steps with tools like *Great Expectations*. CI runs *data-quality alarms*; if they fire, the pipeline halts.

## How a Senior Engineer Thinks

- Put *missingness* on a *dashboard*.
- Outliers go through *flag → review → decide*.
- Extract cleaning logic into *reusable functions*.
- Never modify the *original* — work on a *copy*.
- Treat *validation tests* like *code* — review them in PR.

## Checklist

- [ ] I check *missing/duplicate/outlier/type* in order.
- [ ] I can describe an *imputation* strategy.
- [ ] I know what *IQR* means.
- [ ] I produce a *validation report*.

## Practice Problems

1. Print the *missingness rate* of any public dataset.
2. Build an *outlier flag* and compare *keeping vs dropping*.
3. Document a case where a *type-conversion failure* broke an analysis.

## Wrap-up and Next Steps

Cleaning is *quiet labor* that holds up *every conclusion* you will draw. Next we move to *EDA* — exploring the cleaned data.

<!-- toc:begin -->
- [What Is Data Science?](./01-what-is-data-science.md)
- [Turning a Problem into a Data Problem](./02-problem-to-data-problem.md)
- [Data Collection](./03-data-collection.md)
- **Data Cleaning (current)**
- Exploratory Data Analysis (upcoming)
- Visualization (upcoming)
- Modeling (upcoming)
- Evaluation (upcoming)
- Result Interpretation (upcoming)
- End-to-End Data Project Flow (upcoming)
<!-- toc:end -->

## References

- [pandas — Working with Missing Data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [Great Expectations — Data Quality Tests](https://docs.greatexpectations.io/docs/)
- [Wikipedia — Interquartile Range](https://en.wikipedia.org/wiki/Interquartile_range)
- [Hadley Wickham — Tidy Data](https://vita.had.co.nz/papers/tidy-data.pdf)

Tags: DataScience, DataCleaning, Pandas, Quality, Beginner

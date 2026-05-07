---
series: pandas-101
episode: 3
title: Reading CSV and Excel
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Pandas
  - CSV
  - Excel
  - DataAnalysis
  - Beginner
seo_description: Master read_csv and read_excel — encoding, separator, dtype, and date parsing — to load data correctly the first time
last_reviewed: '2026-05-04'
---

# Reading CSV and Excel

> Pandas 101 series (3/10)

<!-- a-grade-intro:begin -->

**Core question**: Is *loading data well* really *half of the analysis*?

> *Bad loading is *the start of bad analysis*. Get your read_csv options right from the beginning.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The *core options* of *read_csv* and *read_excel*
- Handling *encoding* and *separators*
- The value of explicit *dtype*
- A 5-step loading hands-on
- Five common mistakes

## Why It Matters

*80%* of analysis is *loading and cleaning*. *Mistakes at load time* come back as *debugging cost* later.

## Concept at a Glance

```mermaid
flowchart LR
    File["CSV / Excel"] --> Read["read_csv / read_excel"]
    Read --> Check["dtypes / shape / head"]
    Check --> Fix["fix encoding / dtype / header"]
```

## Key Terms

- **encoding**: file's *character encoding* (utf-8, cp949, latin-1).
- **sep**: *separator* — comma, tab, semicolon.
- **header**: *header row position* — 0 by default, None for no header.
- **dtype**: *explicit per-column type* — better memory and accuracy.
- **parse_dates**: *auto-parse date columns*.

## Before/After

**Before**: *"Just call read_csv"* — broken characters, numbers as strings.

**After**: *"Specify encoding, dtype, parse_dates"* — *data lands as intended*.

## Hands-on: Five Loading Steps

### Step 1 — Basic read_csv

```python
import pandas as pd
df = pd.read_csv("sales.csv")
print(df.shape, df.dtypes)
```

### Step 2 — Encoding and separator

```python
df = pd.read_csv("data.csv", encoding="latin-1", sep=";")
print(df.head())
```

### Step 3 — Explicit dtype

```python
df = pd.read_csv(
    "sales.csv",
    dtype={"product_id": "string", "qty": "int32"},
    parse_dates=["date"],
)
print(df.dtypes)
```

### Step 4 — Read Excel

```python
xls = pd.read_excel("report.xlsx", sheet_name="Q1", header=1)
print(xls.head())
```

### Step 5 — Use chunksize for big files

```python
total = 0
for chunk in pd.read_csv("big.csv", chunksize=100_000):
    total += len(chunk)
print(total)
```

## What to Notice in This Code

- *encoding* is the *first trap* with non-ASCII data.
- Explicit *dtype* secures *memory* and *type safety*.
- *chunksize* is the standard pattern to bypass *memory limits*.

## Five Common Mistakes

1. **Skipping *encoding* and getting garbled text.**
2. **Reading *ID columns* as numbers and *losing leading zeros*.**
3. **Leaving *dates as strings* — never using *parse_dates*.**
4. **Reading Excel files with *non-default header rows* unchanged.**
5. **Skipping *sheet_name* and getting only the *first sheet*.**

## How This Shows Up in Production

ERP CSV exports, accounting Excel files, CSV from external APIs — to *load reliably* you fix *5-10 options* into a *standard pattern*. Loading code becomes a *reusable module*.

## How a Senior Engineer Thinks

- Put *loading code* in a *separate module*.
- Always specify *dtype* explicitly.
- Always review *parse_dates*.
- Guard memory with *chunksize*.
- Keep *original files* untouched.

## Checklist

- [ ] I always specify *encoding*.
- [ ] I specify *dtype*.
- [ ] I review *parse_dates*.
- [ ] I specify *sheet_name* for Excel.

## Practice Problems

1. Read a *non-UTF-8* CSV and print the *dtypes*.
2. Compare *dtype* with and without *parse_dates*.
3. Write a function that counts rows using *chunksize*.

## Wrap-up and Next Steps

Good loading is the *start of good analysis*. Next we cover *filtering and selection*.

<!-- toc:begin -->
- [What Is Pandas?](./01-what-is-pandas.md)
- [Series and DataFrame](./02-series-and-dataframe.md)
- **Reading CSV and Excel (current)**
- Filtering and Selection (upcoming)
- Handling Missing Values (upcoming)
- groupby (upcoming)
- Merge and Join (upcoming)
- Time Series (upcoming)
- apply and Vectorization (upcoming)
- Real-world Data Analysis (upcoming)
<!-- toc:end -->

## References

- [pandas — read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [pandas — read_excel](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)
- [pandas — IO tools](https://pandas.pydata.org/docs/user_guide/io.html)
- [Real Python — Reading and Writing CSV Files](https://realpython.com/python-csv/)

Tags: Pandas, CSV, Excel, DataAnalysis, Beginner

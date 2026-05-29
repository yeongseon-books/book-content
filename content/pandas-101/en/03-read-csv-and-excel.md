---
series: pandas-101
episode: 3
title: "Pandas 101 (3/10): Reading CSV and Excel"
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
  - CSV
  - Excel
  - DataAnalysis
  - Beginner
seo_description: Master read_csv and read_excel — encoding, separator, dtype, and date parsing — to load data correctly the first time
last_reviewed: '2026-05-15'
---

# Pandas 101 (3/10): Reading CSV and Excel

A lot of analysis work goes wrong long before modeling or visualization starts. If text encoding breaks, numeric columns land as strings, or dates stay as plain text, every downstream calculation becomes less trustworthy. File loading is not a throwaway pre-step. It is where data quality gets its first serious test.

This is the 3rd post in the Pandas 101 series.

In this chapter, we will treat `read_csv` and `read_excel` as data-loading contracts rather than convenience helpers. The goal is to make data land in memory the way you intended on the first read.


![pandas 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/03/03-01-concept-at-a-glance.en.png)
*pandas 101 chapter 3 flow overview*
> *Reading is not just opening a file — it's your **first quality gate**. Encoding, delimiter, dtype, datetime parsing — get these right here or pay for it later.

## Questions to Keep in Mind

- The core options of `read_csv` and `read_excel`?
- Handling encoding and separators?
- The value of explicit dtype?

## Why It Matters

A significant share of real analysis time goes into loading and cleaning. A single mistake at load time—wrong encoding, wrong type, wrong date format—cascades into type bugs, alignment errors, and incorrect aggregations downstream. That is why experienced engineers invest more attention at this first gate than anywhere else.

## Key Terms

- **encoding**: file's character encoding (utf-8, cp949, latin-1).
- **sep**: separator — comma, tab, semicolon.
- **header**: header row position — 0 by default, None for no header.
- **dtype**: explicit per-column type — better memory and accuracy.
- **parse_dates**: auto-parse date columns at read time.

## Before/After

**Before**: "Just call read_csv" — broken characters, numbers as strings, fix later.

**After**: "Specify encoding, dtype, parse_dates" — data lands as intended on the first read.

## Hands-on: Five Loading Steps

### Step 1 — Basic read_csv

```python
import pandas as pd
df = pd.read_csv("sales.csv")
print(df.shape, df.dtypes)
```

Checking shape and dtypes immediately after reading tells you whether loading went wrong before you touch any analysis logic. Column count may be correct, but if types are off, every computation downstream will be unreliable.

**Expected output:**

```text
(3, 3)
product_id    object
qty            int64
amount       float64
dtype: object
```

A bare `read_csv` call works for quick exploration, but leaving it as production code is risky. Always pair the read with `shape` and `dtypes` inspection.

### Step 2 — Encoding and separator

```python
df = pd.read_csv("data.csv", encoding="latin-1", sep=";")
print(df.head())
```

When characters are garbled or all columns collapse into one, encoding and separator are the first two things to check. A file may look like CSV by extension, but its actual settings can be anything.

## Read Functions by File Format

Different file formats call for different read functions. Understanding their characteristics and performance helps you choose the right one.

| Format | Function | Key Options | Performance |
| --- | --- | --- | --- |
| CSV | `read_csv` | `encoding`, `sep`, `dtype` | Fast |
| Excel | `read_excel` | `sheet_name`, `header` | Slow |
| JSON | `read_json` | `orient`, `lines` | Medium |
| Parquet | `read_parquet` | `columns` | Very fast |

CSV is the most common but also the most prone to encoding issues. Parquet embeds type information and compression, making it efficient for large datasets—but it can have compatibility issues with legacy systems that only speak CSV.

### Step 3 — Explicit dtype

```python
df = pd.read_csv(
    "sales.csv",
    dtype={"product_id": "string", "qty": "int32"},
    parse_dates=["date"],
)
print(df.dtypes)
```

Specifying types at read time does more than save memory. It preserves identifiers with leading zeros and ensures date columns are immediately usable for time-series operations. Fixing types after the fact is always more expensive than getting them right upfront.

### Step 4 — Read Excel

```python
xls = pd.read_excel("report.xlsx", sheet_name="Q1", header=1)
print(xls.head())
```

Excel files have far more structural variation than CSV. Specifying sheet name and header position explicitly makes reading stable even for human-authored spreadsheets with merged cells and notes above the data.

### Step 5 — Use chunksize for big files

```python
total = 0
for chunk in pd.read_csv("big.csv", chunksize=100_000):
    total += len(chunk)
print(total)
```

Chunked loading lets you validate large files without betting all your memory on a single read. In production, that often turns a risky file load into a routine streaming check.

**Expected output:**

```text
1000000
```

Files that cannot fit in memory are handled safely with `chunksize`. This pattern works well for row counting, partial aggregation, and preprocessing—any task that can be done sequentially.

## Detailed CSV Options

CSV is the most universal format but also the trickiest. Knowing these options covers most real-world edge cases.

### Specifying encoding

```python
df = pd.read_csv("data.csv", encoding="cp949")
```

Non-English data is typically stored as UTF-8 or a locale-specific encoding (CP949 for Korean, Shift_JIS for Japanese, latin-1 for Western European). When characters are garbled, encoding is the first thing to check.

### Parsing date columns

```python
df = pd.read_csv(
    "sales.csv",
    parse_dates=["order_date", "ship_date"],
    date_format="%Y-%m-%d",
)
print(df.dtypes)
```

Leaving dates as strings makes time-series operations impossible—you cannot resample, subtract dates, or filter by month. Parsing at read time eliminates the conversion step later.

### Reading only specific columns

```python
df = pd.read_csv("large.csv", usecols=["id", "name", "amount"])
print(df.columns)
```

`usecols` dramatically reduces memory and I/O time for wide files. When a file has 200 columns and you need 5, skipping the rest at read time is the simplest optimization available.

## Practical Example: Consolidating Multiple Files

In production, you frequently need to read multiple files and merge them into one DataFrame.

```python
import glob
files = glob.glob("data/*.csv")
dfs = []
for file in files:
    df = pd.read_csv(file)
    dfs.append(df)
combined = pd.concat(dfs, ignore_index=True)
print(combined.shape)
```

When combining files, always verify that column structures match across all sources. A single file with an extra or missing column will introduce `NaN` silently after `concat`.

## Error Handling

File reading can fail partway through. Error-handling options make pipelines more robust.

### Skipping bad lines

```python
df = pd.read_csv("dirty.csv", on_bad_lines="skip")
print(f"Loaded {len(df)} rows")
```

Rows that do not match the expected column count are skipped. Always log how many rows were dropped—silent data loss is worse than a crash.

### Handling encoding errors

```python
df = pd.read_csv("data.csv", encoding="utf-8", encoding_errors="ignore")
```

Ignoring encoding errors lets you continue reading, but characters may be lost. When possible, find and specify the correct encoding instead of ignoring errors.

## Large File Processing

When a file does not fit in memory, chunked processing is not optional—it is required.

### Chunked iteration

```python
chunk_iter = pd.read_csv("big.csv", chunksize=50000)
for i, chunk in enumerate(chunk_iter):
    print(f"Chunk {i}: {len(chunk)} rows")
    # Process each chunk independently
```

Each chunk is an independent DataFrame. Filter, aggregate, or transform within each chunk, then collect only the results.

### Partial aggregation example

```python
total_amount = 0
for chunk in pd.read_csv("sales.csv", chunksize=100000):
    total_amount += chunk["amount"].sum()
print(f"Total: {total_amount}")
```

You can compute a total across 50 million rows without loading more than 100K rows at a time. This pattern extends to any associative aggregation (sum, count, min, max).

### Memory monitoring

```python
df = pd.read_csv("data.csv")
print(df.info(memory_usage="deep"))
```

The `memory_usage="deep"` option shows actual memory consumption including string data. String-heavy DataFrames often use 3–5x more memory than numeric ones of the same row count.

## Streaming Read Pattern

For files that exceed available memory, a streaming function that filters and aggregates per chunk is the standard approach.

```python
def process_large_csv(filename):
    result = []
    for chunk in pd.read_csv(filename, chunksize=100000):
        filtered = chunk[chunk["amount"] > 100]
        summary = filtered.groupby("category")["amount"].sum()
        result.append(summary)
    return pd.concat(result).groupby(level=0).sum()

total = process_large_csv("sales.csv")
print(total)
```

This pattern works for any pipeline that can decompose into per-chunk operations followed by a final merge. The key insight is that `groupby(...).sum()` is associative—you can sum within chunks and then sum the partial sums.

### Data validation after reading

Always validate immediately after loading. Catching structure problems early prevents silent downstream corruption.

```python
def validate_dataframe(df, expected_columns, expected_dtypes):
    assert set(df.columns) == set(expected_columns), "Column mismatch"
    for col, dtype in expected_dtypes.items():
        assert df[col].dtype == dtype, f"{col} dtype mismatch"
    return True

df = pd.read_csv("data.csv")
validate_dataframe(df, ["id", "name", "amount"], {"id": "int64", "amount": "float64"})
```

## Reading Compressed Files

Pandas reads compressed files directly—no manual decompression needed.

```python
# gzip
df = pd.read_csv("data.csv.gz", compression="gzip")

# zip
df = pd.read_csv("data.zip")

# auto-detect from extension
df = pd.read_csv("data.csv.bz2", compression="infer")
```

Compressed files save disk space and reduce network transfer time—especially useful in cloud environments where data moves between storage and compute. Pandas auto-detects compression from the file extension by default.

## What to Notice in This Code

- Encoding is the first trap with non-ASCII data.
- Explicit dtype secures both memory and type safety.
- `chunksize` is the standard pattern to bypass memory limits.

## Five Common Mistakes

1. **Skipping encoding and getting garbled text.** Always specify encoding for non-ASCII data.
2. **Reading ID columns as numbers and losing leading zeros.** Use `dtype={"id": "string"}`.
3. **Leaving dates as strings.** Use `parse_dates` at read time.
4. **Reading Excel files with non-default header rows unchanged.** Always check `header` position.
5. **Skipping `sheet_name` and getting only the first sheet.**

## How This Shows Up in Production

ERP CSV exports, accounting Excel files, external agency data—production files never have consistent formats. That is why teams wrap loading code into standard functions with fixed encoding, dtype, and date-parsing settings. The loading module becomes the contract between raw files and clean DataFrames.

## How a Senior Engineer Thinks

- Put loading code in a separate module—it changes independently of analysis logic.
- Always specify dtype explicitly—inference is a convenience, not a contract.
- Always review which columns need `parse_dates`.
- Guard memory with `chunksize` for anything over 1 GB.
- Keep original files untouched—adjust only the reading logic.

## Checklist

- [ ] I always specify encoding for non-ASCII files.
- [ ] I specify dtype for columns where inference is risky.
- [ ] I review which columns need parse_dates.
- [ ] I specify sheet_name and header for Excel files.

## Practice Problems

1. Read a non-UTF-8 CSV and print the dtypes.
2. Compare dtypes with and without `parse_dates`.
3. Write a function that counts rows using `chunksize`.

## Wrap-up and next steps

Good analysis starts with good loading. When you treat file reading as a data contract—encoding, types, dates locked in at read time—everything downstream becomes more reliable. Next we cover filtering and selection.

## Answering the Opening Questions

- **What options should you look at first in `read_csv` and `read_excel`?**
  - Start with encoding, delimiter, header position, sheet name, and structure-deciding options like `dtype` and `parse_dates`. The article also checked `shape` and `dtypes` right after `pd.read_csv("sales.csv")`, and specified `sheet_name="Q1", header=1` for Excel.
- **Why do character encoding and delimiter frequently cause problems?**
  - Even if the extension is CSV, actual storage formats vary—a single difference like `encoding="latin-1"`, `encoding="cp949"`, or `sep=";"` can garble characters or collapse columns into one. When structure breaks at the read stage, all downstream filtering and aggregation proceeds against a malformed table.
- **What are the benefits of specifying data types explicitly?**
  - Fixing types at read time with `dtype={"product_id": "string", "qty": "int32"}` reliably preserves identifiers with leading zeros and reduces memory. Adding `parse_dates=["date"]` lets you transition directly to time-series operations without a later conversion step.
<!-- toc:begin -->
## In this series

- [Pandas 101 (1/10): What Is Pandas?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): Series and DataFrame](./02-series-and-dataframe.md)
- **Reading CSV and Excel (current)**
- Filtering and Selection (upcoming)
- Handling Missing Values (upcoming)
- Groupby and Aggregation (upcoming)
- Merge and Join (upcoming)
- Time Series (upcoming)
- Apply and Vectorization (upcoming)
- Real-World Data Analysis (upcoming)

<!-- toc:end -->

## References

- [pandas — read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [pandas — read_excel](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)
- [pandas — IO tools](https://pandas.pydata.org/docs/user_guide/io.html)
- [Real Python — Reading and Writing CSV Files](https://realpython.com/python-csv/)

Tags: Pandas, CSV, Excel, DataAnalysis, Beginner

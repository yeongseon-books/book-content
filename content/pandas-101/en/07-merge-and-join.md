---
series: pandas-101
episode: 7
title: "Pandas 101 (7/10): Merge and Join"
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
  - Merge
  - Join
  - SQL
  - Beginner
seo_description: Master inner, left, right, outer, and cross joins, and learn the difference between merge and join with hands-on code
last_reviewed: '2026-05-15'
---

# Pandas 101 (7/10): Merge and Join

Production data rarely lives in one perfect table. Customer attributes sit in one dataset, orders in another, and campaign or event data somewhere else. That means the skill of combining tables safely is not optional. It is one of the most important parts of analysis work.

This is the 7th post in the Pandas 101 series.

Here we will treat `merge` and `join` as tools for validating relationships between key systems, not just for gluing columns together. Row counts and key assumptions matter as much as the output table itself.


![pandas 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/07/07-01-concept-at-a-glance.en.png)
*pandas 101 chapter 7 flow overview*
> *Merge is not just combining tables — it's validating relationships. Duplicate keys, unmatched rows, row explosion — most of this is *preventable by checking your keys first.

## Questions to Keep in Mind

- inner / left / right / outer / cross* joins?
- The difference between *merge* and *join?
- Options *suffixes / indicator / validate?

## Why It Matters

Real data is *spread across many tables*. Safely combining users with orders, ads with conversions, products with inventory is what makes metrics correct and model inputs stable.

## Key Terms

- **inner**: keys *present in both*.
- **left**: *all of left* + matched right.
- **right**: the opposite.
- **outer**: *union*.
- **cross**: *cartesian product*.
- **key**: the column(s) used to connect two tables.

### Join Method Comparison

The following table summarizes the five join types, their behavior, and when to use each.

| Join Type | how Parameter | Left Keys | Right Keys | Result Rows | Primary Use |
|---|---|---|---|---|---|
| Inner | `inner` | Matched only | Matched only | Intersection | Analyze data present in both |
| Left | `left` | All preserved | Matched only | Left-based | Preserve base table, add info |
| Right | `right` | Matched only | All preserved | Right-based | Reverse of left join |
| Outer | `outer` | All preserved | All preserved | Union | Preserve all keys from both |
| Cross | `cross` | All rows | All rows | Cartesian product | Generate all combinations |

Inner is the default — omitting `how` applies it automatically. Left join is the most common in practice: it preserves the base table while attaching information from a secondary source.

## Before/After

**Before**: *"One merge, rows exploded"* — *duplicate keys* cause a *cartesian blow-up*.

**After**: *"validate='one_to_one' or 'one_to_many'"* — *errors immediately* on bad assumptions.

## Hands-on: Five Join Steps

### Step 1 — Prepare data

```python
import pandas as pd
users = pd.DataFrame({"uid": [1, 2, 3], "name": ["a", "b", "c"]})
orders = pd.DataFrame({"uid": [1, 1, 2], "amount": [100, 200, 50]})
```

Even in this small example, a key trap is already present: `uid=1` appears twice in `orders`, so joining without thinking about cardinality can change the row count.

### Step 2 — inner

```python
print(users.merge(orders, on="uid"))
```

The default `how` is inner. Only keys present in both tables survive, so user 3 disappears.

### Step 3 — left and outer

```python
print(users.merge(orders, on="uid", how="left"))
print(users.merge(orders, on="uid", how="outer", indicator=True))
```

When you review a join, the `_merge` column is often more valuable than the payload columns. It tells you immediately whether your assumptions about overlap and coverage were actually true.

**Expected output:**

```text
   uid name  amount     _merge
0    1    a   100.0       both
1    1    a   200.0       both
2    2    b    50.0       both
3    3    c     NaN  left_only
```

### Step 4 — suffixes

```python
df1 = pd.DataFrame({"k": [1], "v": [10]})
df2 = pd.DataFrame({"k": [1], "v": [20]})
print(df1.merge(df2, on="k", suffixes=("_a", "_b")))
```

When both tables have columns with the same name, specifying suffixes prevents confusing output. Suffixes serve as both conflict resolution and documentation.

### Step 5 — validate

```python
try:
    users.merge(orders, on="uid", validate="one_to_one")
except Exception as e:
    print("expected:", type(e).__name__)
```

`validate` is the difference between a quiet data bug and an explicit contract check. If your join cardinality assumption is wrong, you want the failure right here.

**Expected output:**

```text
expected: MergeError
```

### Missing Value Strategy After Joins

Joins often produce NaN values when keys exist in only one table. How you handle these depends on the analysis goal.

| Strategy | When to Use | Advantage | Disadvantage |
|---|---|---|---|
| Drop | Missing rows are few | Simple and clear | Information loss |
| Fill with default | Reasonable default exists | Preserves row count | Potential distortion |
| Interpolate | Time/ordered data | Reflects trends | Requires assumptions |
| Add flag column | Missingness is informative | Preserves information | Column proliferation |

```python
users = pd.DataFrame({"uid": [1, 2, 3], "name": ["a", "b", "c"]})
orders = pd.DataFrame({"uid": [1, 1, 2], "amount": [100, 200, 50]})

merged = users.merge(orders, on="uid", how="left")

# Strategy 1: Drop missing
print(merged.dropna())

# Strategy 2: Fill with default
merged["amount"] = merged["amount"].fillna(0)
print(merged)

# Strategy 4: Add flag
merged["has_order"] = merged["amount"].notna()
print(merged)
```

**Expected output (flag added):**

```text
   uid name  amount  has_order
0    1    a   100.0       True
1    1    a   200.0       True
2    2    b    50.0       True
3    3    c     0.0      False
```

Leaving NaN values unhandled after a join can cause unexpected errors downstream. Check missing patterns immediately after joining and handle them explicitly.

### fillna and interpolate Examples

Interpolation after joins is common with time-series or ordered data.

```python
import pandas as pd
import numpy as np

# Time-ordered data
df = pd.DataFrame({
    "date": pd.date_range("2026-01-01", periods=5),
    "value": [10, np.nan, np.nan, 40, 50],
})

# Linear interpolation
df["interpolated"] = df["value"].interpolate(method="linear")

# Forward fill
df["ffill"] = df["value"].fillna(method="ffill")

# Backward fill
df["bfill"] = df["value"].fillna(method="bfill")

print(df)
```

**Expected output:**

```text
        date  value  interpolated  ffill  bfill
0 2026-01-01   10.0          10.0   10.0   10.0
1 2026-01-02    NaN          20.0   10.0   40.0
2 2026-01-03    NaN          30.0   10.0   40.0
3 2026-01-04   40.0          40.0   40.0   40.0
4 2026-01-05   50.0          50.0   50.0   50.0
```

Interpolation estimates values in missing gaps. Linear interpolation is common in time series, but it is not always appropriate — choose based on data characteristics.

### Missing Pattern Visualization

After a join, visualizing where and how much data is missing helps you spot patterns quickly.

```python
import pandas as pd
import numpy as np

users = pd.DataFrame({"uid": [1, 2, 3, 4, 5], "name": ["a", "b", "c", "d", "e"]})
orders = pd.DataFrame({"uid": [1, 1, 2], "amount": [100, 200, 50]})

merged = users.merge(orders, on="uid", how="left")

# Missing as 0/1
missing_map = merged.isnull().astype(int)
print(missing_map)

# Per-column missing ratio
print(merged.isnull().mean())
```

**Expected output:**

```text
   uid  name  amount
0    0     0       0
1    0     0       0
2    0     0       0
3    0     0       1
4    0     0       1

uid       0.0
name      0.0
amount    0.4
dtype: float64
```

Checking missing ratios first gives a quick sense of whether the join worked correctly. If missingness is higher than expected, revisit the key relationship or join type.

### Practical Example: Customer-Order Merge

The most common real-world pattern is merging a customer table with an order table.

```python
import pandas as pd

customers = pd.DataFrame({
    "customer_id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "tier": ["Gold", "Silver", "Gold"],
})

orders = pd.DataFrame({
    "order_id": [101, 102, 103, 104],
    "customer_id": [1, 1, 2, 3],
    "amount": [100, 150, 80, 200],
})

# Compute order totals
order_sum = orders.groupby("customer_id").agg(
    total_amount=("amount", "sum"),
    order_count=("order_id", "count"),
)

# Merge with customer info
result = customers.merge(order_sum, on="customer_id", how="left")
result["total_amount"] = result["total_amount"].fillna(0)
result["order_count"] = result["order_count"].fillna(0)
print(result)
```

**Expected output:**

```text
   customer_id     name    tier  total_amount  order_count
0            1    Alice    Gold         250.0          2.0
1            2      Bob  Silver          80.0          1.0
2            3  Charlie    Gold         200.0          1.0
```

This pattern is the foundation for building per-customer KPIs. Aggregate the order table first, then merge with the customer table to get customer-level statistics.

## What to Notice in This Code

- *indicator=True* tells you *the row's source*.
- *suffixes* resolves *duplicate column names*.
- *validate* makes *join assumptions* explicit *in code*.

## Five Common Mistakes

1. **Row explosion from *duplicate keys*.**
2. **Not knowing the default *how* is *inner*.**
3. **Skipping *suffixes* and overwriting columns.**
4. ***Mismatched key dtypes* between left and right.**
5. **Skipping *reset_index* and getting *index conflicts*.**

## How This Shows Up in Production

CRM x orders, ads x conversions, users x events — *80% of analysis is joins*. Row count tracking, key duplicate checks, and dtype matching are standard pre/post-merge validation steps.

## How a Senior Engineer Thinks

- Always *track row counts*.
- Use *validate* to *make assumptions explicit*.
- *Match key dtypes*.
- Decide whether to *deduplicate before joining*.
- *Profile* the join result.

## Checklist

- [ ] I know the *5 how options*.
- [ ] I use *validate*.
- [ ] I check sources with *indicator*.
- [ ] I use *suffixes*.

## Practice Problems

1. Print the *row count difference* between *left join* and *outer join*.
2. Construct data where *validate='one_to_one'* fails and inspect the *exception message*.
3. Use the *indicator column* to find *right-only rows*.

## Wrap-up and next steps

Joining is not just gluing tables — it is validating data relationships. Checking keys and row counts together is what makes joins safe. Next we cover *time series*.

## Answering the Opening Questions

- **Why does Pandas have both `merge` and `join`?**
  - `merge` is central when you explicitly specify column-based relationships, while `join` provides simpler syntax for index-based attachment. The article used `users.merge(orders, on="uid")` to clearly expose the key column because in the beginning, being explicit about the join criterion is safer.
- **How do inner, left, right, outer, and cross joins differ?**
  - The difference lies in which keys remain in the result. `how="left"` preserved all `users` rows, while `how="outer", indicator=True` kept both sides' keys and used the `_merge` column to distinguish `both` from `left_only`.
- **Why does row count suddenly increase with duplicate keys?**
  - Joins create all possible combinations of matching keys, so if `uid=1` appears twice in `orders`, the single `users` row is replicated into multiple rows. That is why the article demonstrated triggering an exception with `validate="one_to_one"` and emphasized always checking row counts and key duplicates before and after merging.
<!-- toc:begin -->
## In this series

- [Pandas 101 (1/10): What Is Pandas?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): Series and DataFrame](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): Reading CSV and Excel](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): Filtering and Selection](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): Handling Missing Values](./05-missing-values.md)
- [Pandas 101 (6/10): Groupby and Aggregation](./06-groupby.md)
- **Merge and Join (current)**
- Time Series (upcoming)
- Apply and Vectorization (upcoming)
- Real-World Data Analysis (upcoming)

<!-- toc:end -->

## References

- [pandas — Merge, join, concatenate and compare](https://pandas.pydata.org/docs/user_guide/merging.html)
- [pandas — merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)
- [pandas — join](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.join.html)
- [SQL Joins Explained — Mode Analytics](https://mode.com/sql-tutorial/sql-joins/)

Tags: Pandas, Merge, Join, SQL, Beginner

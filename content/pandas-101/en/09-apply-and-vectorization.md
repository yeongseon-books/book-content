---
series: pandas-101
episode: 9
title: "Pandas 101 (9/10): Apply and Vectorization"
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
  - Vectorization
  - Performance
  - Apply
  - Beginner
seo_description: Learn the trap of apply and the power of NumPy and Pandas vectorization to make your data pipelines fast and idiomatic
last_reviewed: '2026-05-15'
---

# Pandas 101 (9/10): Apply and Vectorization

Once you get comfortable with Pandas syntax, the next big lesson is that "working code" and "fast code" are not the same thing. `apply(axis=1)` often feels natural because it resembles row-by-row reasoning, but it becomes a bottleneck surprisingly quickly as datasets grow. Performance improves once you understand what Pandas is optimized to do well.

This is the 9th post in the Pandas 101 series.

In this chapter, I do not want to ban `apply` as a slogan. I want to explain why vectorized column-wise computation is the default fast path, and when `map`, NumPy operations, or direct Series math are the better tools.


![pandas 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/09/09-01-concept-at-a-glance.en.png)
*pandas 101 chapter 9 flow overview*
> *Vectorization is Pandas' *superpower. Reach for `apply` only after built-in methods, list comprehensions, and NumPy fail you.

## Questions to Keep in Mind

- What exactly does *vectorization* mean?
- What are the differences between `apply`, `map`, and NumPy operations?
- Why is `apply(axis=1)` particularly slow?

## Why It Matters

Analysis speed can differ by tens to hundreds of times depending on whether you vectorize. ETL transforms, feature engineering, and large-scale reports involve repeated computation where this gap translates directly into execution time and cloud cost.

## Key Terms

- **Vectorization**: array-level computation without explicit loops.
- **apply**: apply a function along rows/columns — internally a Python loop.
- **map**: apply a function/dict to Series elements.
- **np.where**: vectorized conditional.
- **eval / numexpr**: acceleration for large expressions.

### Reshape Function Comparison

The following table summarizes how Pandas reshape functions transform data shape.

| Function | Input Shape | Output Shape | Primary Use |
|---|---|---|---|
| `pivot()` | Long (id-var-value) | Wide (var as columns) | Simple wide conversion |
| `melt()` | Wide (many columns) | Long (id-var-value) | Wide to long |
| `stack()` | Wide DataFrame | MultiIndex Series | Columns to index |
| `unstack()` | MultiIndex Series/DF | Wide DataFrame | Index to columns |
| `pivot_table()` | Long with duplicates | Wide (aggregated) | Wide with aggregation |

`pivot` and `melt` are inverses. `pivot` spreads values into columns; `melt` stacks columns back into rows. Mastering these two gives you full control over data shape.

## Before/After

**Before**: row-by-row loops or `apply(axis=1)` for computation — minutes on 1M rows.

**After**: column-level operations, vectorized conditionals, and mappings produce the same result orders of magnitude faster.

## Hands-on: Five Performance Steps

### Step 1 — Baseline data

```python
import numpy as np, pandas as pd
df = pd.DataFrame({"a": np.arange(1_000_000), "b": np.arange(1_000_000)})
```

Even one million rows is enough to make the difference between computation styles visible. Bottlenecks that hide in small data become obvious at this scale.

### Step 2 — Slow path

```python
# %timeit df.apply(lambda r: r["a"] + r["b"], axis=1)
# Very slow — apply(axis=1) is a per-row Python call
```

`apply(axis=1)` treats each row as a Python object and calls the function repeatedly. The syntax looks simple, but this is not the computation path Pandas is optimized for.

### Step 3 — Vectorized

```python
df["c"] = df["a"] + df["b"]   # fastest
```

Column-level computation keeps the same syntax regardless of row count. Even a three-row preview makes the win obvious: one column expression computes the whole result at once. The real speedup only grows as row counts rise.

**Expected output:**

```text
   a  b  c
0  0  0  0
1  1  1  2
2  2  2  4
```

This single line is the essence of vectorization. By handing computation to the array level, Pandas and NumPy can use internal optimized paths.

### Step 4 — np.where for conditional

```python
df["flag"] = np.where(df["a"] % 2 == 0, "even", "odd")
```

You do not need row-level loops for conditional branching. `np.where` applies conditions to the entire array at once.

### Step 5 — map for code translation

```python
mapping = {0: "zero", 1: "one"}
print(pd.Series([0, 1, 2]).map(mapping))
```

`map` is a precise fit for code translation tasks. It also leaves unmapped values behind as `NaN`, which makes gaps in the mapping easy to detect.

**Expected output:**

```text
0    zero
1     one
2     NaN
dtype: object
```

Value substitution and code conversion are where `map` shines. Trying to handle everything with `apply` makes code both slower and less readable.

### crosstab Section

`crosstab` is a specialized pivot table for counting frequencies. It is commonly used to examine cross-tabulated counts between two categorical variables.

#### Basic example

```python
import pandas as pd

df = pd.DataFrame({
    "gender": ["M", "F", "M", "F", "M", "F"],
    "product": ["A", "A", "B", "B", "A", "C"],
})

ct = pd.crosstab(df["gender"], df["product"])
print(ct)
```

**Expected output:**

```text
product  A  B  C
gender          
F        1  1  1
M        2  1  0
```

`crosstab` counts occurrences of each combination and arranges them in a table. It is very useful for survey analysis, A/B test results, and customer segment distributions.

#### Showing ratios

The `normalize` parameter converts counts to proportions.

```python
ct_norm = pd.crosstab(df["gender"], df["product"], normalize="index")
print(ct_norm)
```

**Expected output:**

```text
product         A         B         C
gender                              
F        0.333333  0.333333  0.333333
M        0.500000  0.250000  0.000000
```

`normalize="index"` makes each row sum to 1. This is useful for comparing product preference distributions within each gender.

#### Adding margins

`margins=True` adds row and column totals.

```python
ct_margin = pd.crosstab(df["gender"], df["product"], margins=True)
print(ct_margin)
```

**Expected output:**

```text
product  A  B  C  All
gender              
F        1  1  1    3
M        2  1  0    3
All      3  2  1    6
```

`margins=True` displays row and column sums together. You can see the overall distribution at a glance and compute proportions easily.

### wide ↔ long Conversion Examples

The core of reshaping is moving freely between wide and long formats.

#### pivot: long → wide

```python
import pandas as pd

# long format
df_long = pd.DataFrame({
    "id": [1, 1, 2, 2],
    "var": ["A", "B", "A", "B"],
    "val": [10, 20, 30, 40],
})

# convert to wide
df_wide = df_long.pivot(index="id", columns="var", values="val")
print(df_wide)
```

**Expected output:**

```text
var   A   B
id         
1    10  20
2    30  40
```

`pivot` takes row identifiers, column names, and values to spread into a wide format.

#### melt: wide → long

```python
# wide format
df_wide2 = pd.DataFrame({
    "id": [1, 2],
    "A": [10, 30],
    "B": [20, 40],
})

# convert to long
df_long2 = df_wide2.melt(id_vars=["id"], value_vars=["A", "B"],
                          var_name="var", value_name="val")
print(df_long2)
```

**Expected output:**

```text
   id var  val
0   1   A   10
1   2   A   30
2   1   B   20
3   2   B   40
```

`melt` melts a wide table into long format. Use it when you need to collapse multiple columns into a single variable column and a value column.

#### pivot_table: wide with aggregation

When duplicate keys exist, use `pivot_table` instead of `pivot` to aggregate automatically.

```python
df = pd.DataFrame({
    "city": ["Seoul", "Seoul", "Busan", "Busan"],
    "category": ["A", "A", "B", "B"],
    "sales": [100, 120, 80, 95],
})

pt = df.pivot_table(index="city", columns="category", values="sales", aggfunc="sum")
print(pt)
```

**Expected output:**

```text
category     A      B
city               
Busan      NaN  175.0
Seoul    220.0    NaN
```

`pivot_table` handles duplicate key combinations by applying an aggregation function, making it extremely practical in real-world scenarios.

### Practical Example: A/B Test Result Analysis

This example combines grouping, vectorization, and derived metric calculation in one flow.

```python
import pandas as pd

# A/B test data
df = pd.DataFrame({
    "user_id": range(1, 7),
    "variant": ["A", "B", "A", "B", "A", "B"],
    "converted": [1, 0, 1, 1, 0, 1],
    "revenue": [100, 0, 150, 80, 0, 120],
})

# aggregate by variant
result = df.groupby("variant").agg(
    users=("user_id", "count"),
    conversions=("converted", "sum"),
    total_revenue=("revenue", "sum"),
)

# compute CVR and ARPU (vectorized)
result["cvr"] = result["conversions"] / result["users"]
result["arpu"] = result["total_revenue"] / result["users"]

print(result)
```

**Expected output:**

```text
         users  conversions  total_revenue       cvr       arpu
variant                                                         
A            3            2            250  0.666667  83.333333
B            3            2            200  0.666667  66.666667
```

This example shows grouping, vectorization, and derived metrics in one pipeline. Computing conversion rate and ARPU through vectorized division keeps the code concise and fast.

## What to Notice in This Code

- `axis=1` apply is the slowest — Python call per row.
- Column-level operations run through low-level optimized paths and are far faster.
- `np.where` is the vectorized if-else.

## Five Common Mistakes

1. **Overusing `apply(axis=1)` as the default solution.**
2. **Using Python for-loops to accumulate row-wise calculations.**
3. **Processing large expressions with pure Python math only.**
4. **Ignoring `NaN` values introduced by `map`.**
5. **dtype mismatch breaks vectorization, causing everything to fall back to object dtype.**

## How This Shows Up in Production

Large-scale ETL, feature engineering, and report computation pipelines rely on vectorization as the easiest cost reduction lever. The same result can be produced with shorter and faster code.

## How a Senior Engineer Thinks

- Always check vectorization feasibility first.
- Use `apply` only when vectorization is impossible.
- Avoid `axis=1` whenever you can.
- Match dtypes before computation.
- Profile to find the real bottleneck, then optimize.

## Checklist

- [ ] I distinguish vectorization from `apply`.
- [ ] I use `np.where` for conditional branching.
- [ ] I use `map` for code translation.
- [ ] I know why `axis=1` apply is slow.

## Practice Problems

1. Compare vectorized addition vs `apply(axis=1)` with timing.
2. Express a 3-tier condition with `np.where`.
3. Translate country codes to country names using `map`.

## Wrap-up and next steps

Vectorization is the core of Pandas performance and idiom. Once you develop the habit of handing computation to column-level operations rather than calling functions row by row, your code becomes shorter, faster, and easier to read. Next we cover a real-world data analysis example that ties everything together.

## Answering the Opening Questions

- **What exactly does vectorization mean?**
  - Vectorization means computing an entire array or column at once without calling a Python function per row. A single line `df["c"] = df["a"] + df["b"]` applying to all one million rows is the most direct demonstration of this meaning.
- **What are the differences between `apply`, `map`, and NumPy operations?**
  - `apply` is a general-purpose tool that repeatedly applies an arbitrary function, `map` suits Series value substitution or one-to-one mapping, and NumPy operations handle conditional branching and numeric computation fast. That is why the article used `Series.map(mapping)` for code substitution and `np.where(df["a"] % 2 == 0, "even", "odd")` for even/odd branching.
- **Why is `apply(axis=1)` particularly slow?**
  - `axis=1` effectively extracts each row as a Python object and passes it to the function, bypassing nearly all internal optimization paths. The large speed difference when replacing `df.apply(lambda r: r["a"] + r["b"], axis=1)` with `df["a"] + df["b"]` exists precisely for this reason.
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
- **Apply and Vectorization (current)**
- Real-World Data Analysis (upcoming)

<!-- toc:end -->

## References

- [pandas — Enhancing performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
- [pandas — apply](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html)
- [NumPy — Universal functions](https://numpy.org/doc/stable/reference/ufuncs.html)
- [Real Python — Fast, Flexible, Easy and Intuitive Pandas](https://realpython.com/fast-flexible-pandas/)

Tags: Pandas, Vectorization, Performance, Apply, Beginner

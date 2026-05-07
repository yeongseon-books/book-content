---
series: data-science-101
episode: 5
title: Exploratory Data Analysis
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DataScience
  - EDA
  - Pandas
  - Statistics
  - Beginner
seo_description: A 5-step EDA workflow that quickly reveals shape, distribution, missingness, correlation, and outliers before any modeling
last_reviewed: '2026-05-04'
---

# Exploratory Data Analysis

> Data Science 101 series (5/10)

<!-- a-grade-intro:begin -->

**Core question**: Before you build any model, how do you read the *shape of the data* — *quickly* and *correctly*?

> *EDA is the *data's self-introduction* you must read before any model.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The *purpose* and *order* of EDA
- Reading *1-D and 2-D distributions*
- *Missing patterns* and what *correlation* means
- A 5-step EDA exercise
- Five common pitfalls

## Why It Matters

Weak EDA produces *the wrong model*. Skipping the *data's self-introduction* and jumping to decisions leads to deep regret later.

> *A model only *imitates* the data it was given.*

## Concept at a Glance

```mermaid
flowchart LR
    Shape["Shape & dtypes"] --> Dist["1D Distribution"]
    Dist --> Pair["2D Relations"]
    Pair --> Miss["Missing Patterns"]
    Miss --> Corr["Correlation"]
```

## Key Terms

- **Skewness**: how *asymmetric* a distribution is.
- **Outlier**: a value *statistically far* from the rest.
- **Cardinality**: the *number of unique values* in a category.
- **Correlation**: the *strength of a linear relationship*.
- **MCAR / MAR / MNAR**: classes of *missingness mechanisms*.

## Before / After

**Before**: you look at `mean` and *misread* the typical value.

**After**: you look at *distribution + quantiles + outliers* together and see the *full shape*.

## Hands-on: 5-step EDA

### Step 1 — Shape and dtypes

```python
import pandas as pd
df = pd.read_csv("orders.csv")
print(df.shape)
print(df.dtypes)
print(df.head())
```

### Step 2 — 1-D distribution

```python
print(df["amount"].describe())
df["amount"].plot.hist(bins=30, title="amount")
```

### Step 3 — Categorical cardinality

```python
print(df.select_dtypes("object").nunique().sort_values(ascending=False))
print(df["country"].value_counts(normalize=True).head())
```

### Step 4 — 2-D relations

```python
import seaborn as sns
sns.scatterplot(data=df.sample(2000), x="quantity", y="amount")
```

### Step 5 — Missingness and correlation

```python
print(df.isna().mean().sort_values(ascending=False).head())
print(df.select_dtypes("number").corr().round(2))
```

## What to Notice in This Code

- `describe` is a *starting point*, not the answer — always pair with a *distribution plot*.
- *Correlation is not causation*.
- *Cardinality* shapes which models will work well.

## Five Common Mistakes

1. **Deciding from the *mean alone*.** You miss the *shape* of the distribution.
2. **Reading correlation as *causation*.** A classic trap.
3. **Plotting *the entire dataset*.** You blow up memory and time — sample first.
4. **Ignoring *cardinality*.** One-hot encoding *explodes*.
5. **Assuming *MCAR* without checking.** You bake in bias.

## How This Shows Up in Production

Teams keep an *EDA notebook* next to the model code. Key distributions live in *dashboards* that monitor *drift*. EDA is not a one-time event — it repeats.

## How a Senior Engineer Thinks

- Order: *distribution → relations → missing → correlation*.
- Look at *correlation cautiously*.
- Attach the *EDA notebook* to the PR.
- *Sampling* buys time.
- Re-run EDA *periodically* to detect *drift*.

## Checklist

- [ ] I look at *describe + distribution* together.
- [ ] I know what *cardinality* is.
- [ ] I know *correlation ≠ causation*.
- [ ] I can classify *missingness patterns*.

## Practice Problems

1. Run a *5-step EDA* on Iris or Titanic.
2. List 3 cases of *high correlation but no causation*.
3. Describe how *cardinality* affected your *model choice* in a real project.

## Wrap-up and Next Steps

EDA is *time spent listening to the data*. Next we will look at *visualization* — showing what we heard.

<!-- toc:begin -->
- [What Is Data Science?](./01-what-is-data-science.md)
- [Turning a Problem into a Data Problem](./02-problem-to-data-problem.md)
- [Data Collection](./03-data-collection.md)
- [Data Cleaning](./04-data-cleaning.md)
- **Exploratory Data Analysis (current)**
- Visualization (upcoming)
- Modeling (upcoming)
- Evaluation (upcoming)
- Result Interpretation (upcoming)
- End-to-End Data Project Flow (upcoming)
<!-- toc:end -->

## References

- [pandas — Descriptive Statistics](https://pandas.pydata.org/docs/user_guide/basics.html#descriptive-statistics)
- [seaborn — Tutorial](https://seaborn.pydata.org/tutorial.html)
- [Wikipedia — Missing Data Patterns](https://en.wikipedia.org/wiki/Missing_data)
- [Tukey — Exploratory Data Analysis](https://archive.org/details/exploratorydataa00tuke_0)

Tags: DataScience, EDA, Pandas, Statistics, Beginner

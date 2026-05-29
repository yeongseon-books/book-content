---
series: data-science-101
episode: 5
title: "Data Science 101 (5/10): Exploratory Data Analysis"
status: publish-ready
targets:
  tistory: false
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
last_reviewed: '2026-05-15'
---

# Data Science 101 (5/10): Exploratory Data Analysis

Exploratory data analysis is the stage where the dataset stops being an abstraction and starts behaving like evidence. Before EDA, you mostly have assumptions: which variables matter, what "typical" looks like, and whether the data is even shaped the way the problem statement implied.

EDA is how you replace those assumptions with observations. If you skip it, you often build a model that is technically correct for the wrong picture of the data. If you do it well, you discover the distributions, gaps, and relationships that should shape every later decision.

This is the 5th post in the Data Science 101 series. Here we walk through a compact but production-friendly EDA loop that helps you read the dataset before you try to optimize it.


![data science 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/05/05-01-concept-at-a-glance.en.png)
*data science 101 chapter 5 flow overview*
> At its core, Exploratory Data Analysis is about deciding what enters a system, where validation happens, and which signals stay for the next cycle—not about feature names.

## Questions to Keep in Mind

- How can you quickly read the shape of data before building any model?
- Why does looking only at the mean often lead to misunderstanding?
- What order works best for examining distributions, missing patterns, and correlations?

## Questions This Post Answers

- What should you inspect before building any model or dashboard?
- Why are distribution shape and missingness often more important than the mean?
- How do cardinality and pairwise relationships shape later modeling choices?
- What does correlation tell you, and what can it never prove?

> EDA is the fastest way to replace assumptions about the dataset with observations you can verify.

## What You Will Learn

- The *purpose* and *order* of EDA
- Reading *1-D and 2-D distributions*
- *Missing patterns* and what *correlation* means
- A 5-step EDA exercise
- Five common pitfalls

## Why It Matters

Weak EDA produces *the wrong model*. Skipping the data's self-introduction and jumping to decisions leads to deep regret later. A model only imitates the data it was given. So modeling without properly reading the input may look fast, but usually creates a more expensive detour.

> *A model only imitates the data it was given.*

## Key Terms

- **Skewness**: how *asymmetric* a distribution is.
- **Outlier**: a value *statistically far* from the rest.
- **Cardinality**: the *number of unique values* in a category.
- **Correlation**: the *strength of a linear relationship*.
- **MCAR / MAR / MNAR**: classes of *missingness mechanisms*.

## Evaluation Metrics Comparison

After EDA and model training, the next step is evaluating model performance. Evaluation is not just about accuracy — you need to pick metrics that match the problem type and business objective.

| Metric | Formula | Best For | Watch Out |
|---|---|---|---|
| Accuracy | (TP+TN) / Total | Balanced data | Misleading on imbalanced data |
| Precision | TP / (TP+FP) | High FP cost | Positive prediction confidence |
| Recall | TP / (TP+FN) | High FN cost | True positive capture rate |
| F1-score | 2*(P*R)/(P+R) | Need balance | Harmonic mean of P and R |
| AUC-ROC | Area under ROC curve | Threshold comparison | Robust to imbalance |
| RMSE | sqrt(mean((y-pred)^2)) | Regression, penalize large errors | Sensitive to outliers |
| MAE | mean(\|y-pred\|) | Regression, interpretable | Less sensitive to large errors |

For example, a cancer diagnosis model prioritizes Recall (missing cancer is unacceptable), while a spam filter prioritizes Precision (marking real mail as spam is unacceptable).

## Python classification_report Example

After EDA and model training, sklearn's `classification_report` gives you multiple metrics at once.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

# Load data
X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluation report
print(classification_report(y_test, y_pred, target_names=["Malignant", "Benign"]))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
```

This example trains on breast cancer data and prints per-class Precision, Recall, and F1-score. The confusion matrix shows which class has the most misclassifications. After EDA, this evaluation step is mandatory.

## Metric Selection Guide

Once EDA reveals the shape of your data, you need to decide which metrics to track during evaluation.

**Classification:**

1. **Balanced data** — start with Accuracy, confirm with Precision/Recall/F1
2. **Imbalanced data** — ignore Accuracy, prioritize Precision/Recall/F1, add AUC-ROC
3. **High FP cost** — Precision first (e.g., spam filter)
4. **High FN cost** — Recall first (e.g., disease diagnosis)

**Regression:**

1. **Penalize large errors** — RMSE
2. **Interpretability first** — MAE
3. **Percentage errors** — MAPE (Mean Absolute Percentage Error)

**Practical notes:**

- Never rely on a single metric — check several together.
- Keep the test set untouched during training; use it only for final evaluation.
- Record baseline model metrics first, then compare improvements.
- Track business metrics separately from model metrics to catch cases where the model improves but business outcomes worsen.

If EDA revealed class imbalance, choosing the right metric at evaluation is the key next step.

## Before / After

**Before**: you look at `mean` and *misread* the typical value. But if the distribution is skewed or has many outliers, the mean poorly represents the actual center.

**After**: you look at *distribution + quantiles + outliers* together and see the *full shape*. Only then can you judge how far to trust the mean.

## Hands-on: 5-step EDA

### Step 1 — Shape and dtypes

```python
import pandas as pd
df = pd.read_csv("orders.csv")
print(df.shape)
print(df.dtypes)
print(df.head())
```

The first thing to do is simpler than you might expect: how many rows and columns, what type each column is, and what actual values look like. This alone reveals whether dates came in as strings or whether a column looks categorical but is stored as numeric.

### Step 2 — 1-D distribution

```python
print(df["amount"].describe())
df["amount"].plot.hist(bins=30, title="amount")
```

`describe()` is a good starting point but not the answer. Numeric summaries alone miss skew and long tails, so always pair them with a distribution plot.

### Step 3 — Categorical cardinality

```python
print(df.select_dtypes("object").nunique().sort_values(ascending=False))
print(df["country"].value_counts(normalize=True).head())
```

Always check unique-value counts for categorical columns. Manageable cardinality like country is easy to work with, but user-ID-level cardinality becomes a burden at modeling time.

### Step 4 — 2-D relations

```python
import seaborn as sns
sns.scatterplot(data=df.sample(2000), x="quantity", y="amount")
```

When examining variable relationships, sample first rather than plotting everything. Faster, lighter on memory, and most patterns are still clearly visible.

### Step 5 — Missingness and correlation

```python
print(df.isna().mean().sort_values(ascending=False).head())
print(df.select_dtypes("number").corr().round(2))
```

Missing rates show which columns are unstable; correlation shows which variables move together. But correlation does not explain causes — what you can read here is direction and strength, not causation.

**Expected output:** an EDA note that lists the core distribution summary, high-cardinality columns, and the top missingness signals.

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

Teams keep an *EDA notebook* next to the model code. Key distributions live in *dashboards* that monitor *drift*. EDA is not a one-time event — it repeats as an observation loop. Over time distributions change, and you need the same EDA frame to detect data drift post-deployment.

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

## Practical Extension: EDA Checklist and Visualization-Based Exploration Routine

EDA is not intuition-driven exploration but a repeatable verification routine. Many beginners mistake EDA for "drawing a few graphs," but in practice it is the quality-check stage where you generate hypothesis candidates and catch data risks early. That is why teams run EDA against a checklist rather than personal preference.

### EDA Checklist (Production-Grade)

| Area | Question to Answer | Minimum Output |
|---|---|---|
| Schema | Do column types match expectations? | Type inspection table |
| Scale | Are row/column counts and unique keys reasonable? | Data size summary |
| Distribution | Are major numeric distributions skewed? | Histograms / boxplots |
| Missingness | Is missingness concentrated in specific segments? | Missing rate table |
| Relationships | Which features correlate most with the target? | Correlation matrix / scatter |
| Temporality | Are there trends or structural shifts over time? | Time-series line chart |

The purpose of the checklist is gap prevention. Even experienced practitioners skip basic checks when projects get busy.

### Basic Exploration Code with matplotlib/seaborn

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

orders = pd.read_csv("orders.csv", parse_dates=["order_date"])
print(orders.shape)
print(orders.isna().mean().sort_values(ascending=False).head())

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.histplot(orders["amount"], bins=30, ax=axes[0])
axes[0].set_title("Amount Distribution")

sns.boxplot(data=orders, x="channel", y="amount", ax=axes[1])
axes[1].set_title("Amount by Channel")
plt.tight_layout()
plt.show()
```

This routine quickly checks two axes: distribution shape and segment differences. You can spot distribution skew and channel-level variation simultaneously.

### Correlation Interpretation Cautions

- High absolute correlation does not imply causation.
- Changing the aggregation granularity easily changes correlation structure.
- Variables with time lags are misread by simple same-time correlation.

### EDA Findings Template

- **Observation**: "Mobile channel median order value is lower than web."
- **Evidence**: "Boxplot shows approximately 18% median gap."
- **Hypothesis**: "Potential drop-off in mobile checkout flow."
- **Next action**: "Collect additional mobile checkout step logs."

Following this structure ensures EDA findings lead to next actions rather than dead-end observations.

### Exploration Automation Ideas

- Generate daily `profile report` to detect distribution drift
- Alert on quantile shifts in key metrics
- Detect new category values entering (cardinality spikes)
- Slack alert when missing rates exceed a threshold

EDA is not a one-time task but an operational observation loop. The same frame applies to post-deployment drift checks, not just initial projects.

### Team Documentation: What to Record After EDA

In early projects, getting the code to run feels like success. But what matters more in practice is whether the team can reproduce the same result. After running the exercises above, always document:

- Run date and data version
- Key column list and definitions
- Main assumptions (excluded data, thresholds, time window)
- Constraints to keep in mind when interpreting results
- Questions to check in the next iteration

Recording these five items prevents repeating the same discussion from scratch in the next cycle. Especially when numbers look good, writing down constraints alongside them keeps the team from overconfidence.

### Reproducible Result Package Example

```python
from pathlib import Path
import json
import datetime as dt

meta = {
    "run_at": dt.datetime.utcnow().isoformat(),
    "dataset": "example_v1",
    "assumptions": [
        "trial users excluded",
        "analysis window = last 30 days",
        "threshold fixed before final test",
    ],
    "next_question": "Which segment shows largest variance next week?",
}

out = Path("artifacts")
out.mkdir(exist_ok=True)
(out / "run_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved", out / "run_meta.json")
```

This is the smallest example of saving analysis artifacts alongside execution metadata. Small records like these compound into significant team learning velocity, because projects are not about finding a single right answer — they are about improving quality through iteration.

### Review Questions for the Next Iteration

- Can I recalculate this result the same way next week?
- How much would conclusions change if the segmentation criteria changed?
- Is the result written as an actionable sentence the ops team can execute immediately?

These three questions are repeatedly valid across every data project regardless of technical difficulty. Answering them at project close accelerates the next iteration's starting speed.

## Deep Practical Extension: Turning Analysis Design into an Operational Loop

To connect the concepts above to real team operations, you need to go beyond analysis notes and build a repeatable experiment loop. Three essentials: first, feature-creation rules must live in both code and documentation. Second, visualizations should serve as decision-trigger checkpoints, not explanation graphics. Third, model evaluation must be interpreted all the way to behavior change, not just a single score line.

### Building a Feature Table with NumPy and pandas

```python
import numpy as np
import pandas as pd

orders = pd.read_csv("orders.csv", parse_dates=["ordered_at"])
users = pd.read_csv("users.csv", parse_dates=["signup_at"])

base = orders.merge(users[["user_id", "signup_at", "country"]], on="user_id", how="left")
base["days_since_signup"] = (base["ordered_at"] - base["signup_at"]).dt.days.clip(lower=0)
base["is_weekend"] = base["ordered_at"].dt.dayofweek.isin([5, 6]).astype(int)
base["amount_log1p"] = np.log1p(base["amount"].clip(lower=0))

agg = (
    base.groupby("user_id", as_index=False)
    .agg(
        order_count=("order_id", "count"),
        avg_amount=("amount", "mean"),
        recent_amount=("amount", "last"),
        signup_age=("days_since_signup", "max"),
        weekend_ratio=("is_weekend", "mean"),
    )
)

print(agg.head())
```

This example transforms raw tables into a user-level feature set tailored for analysis. The `log1p` transform reduces distribution skew, and behavioral features like `weekend_ratio` often improve explanatory power compared to simple totals.

### Checking Distributions and Segment Patterns with matplotlib

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
agg["avg_amount"].hist(bins=30, edgecolor="black", ax=ax[0])
ax[0].set_title("Average Order Value Distribution")
ax[0].set_xlabel("avg_amount")

agg.sort_values("signup_age").reset_index(drop=True)["order_count"].rolling(100).mean().plot(ax=ax[1])
ax[1].set_title("Order Count Rolling Mean by Signup Age")
ax[1].set_ylabel("rolling mean")

plt.tight_layout()
plt.show()
```

The purpose of visualization is not pretty charts — it is finding anomalous signals quickly. If the distribution is skewed, consider a log transform. If the rolling mean shifts abruptly, reconsider segmentation criteria. Each chart should trigger the next action.

### Managing Preprocessing and Model in One sklearn Pipeline

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

num_cols = ["order_count", "avg_amount", "recent_amount", "signup_age", "weekend_ratio"]
cat_cols = ["country"]

numeric = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

categorical = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore")),
])

preprocess = ColumnTransformer([
    ("num", numeric, num_cols),
    ("cat", categorical, cat_cols),
])

model = Pipeline([
    ("preprocess", preprocess),
    ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
])
```

Pipelines make training and inference paths identical, improving reproducibility. This is one of the most reliable ways to eliminate the "works in notebook, breaks in batch" problem.

### Simple A/B Test Design Template

Experiment design is just as important as modeling. This template applies directly to scenarios like marketing message improvement.

| Item | Design Example |
|---|---|
| Hypothesis | Changing the onboarding message increases 7-day return rate |
| Population | New users who signed up in the last 14 days (excluding internal accounts) |
| Randomization | 50:50 split by user_id hash |
| Primary metric | 7-day return rate |
| Guardrail metrics | Support ticket rate, payment failure rate |
| Duration | Minimum 2 weeks or until sample size reached |
| Stop condition | Guardrail metric degradation exceeds threshold |

The most common A/B testing mistake is declaring results too early. If you peek at intermediate results repeatedly without a pre-registered stopping rule and analysis plan, you risk mistaking random variation for a real effect.

### Operational Checkpoints

- Record feature-creation rules in both code and documentation.
- For every EDA chart, write one line: "What decision does this chart inform?"
- Evaluate cost, latency, and operational complexity alongside model scores.
- Fix hypothesis, sample size, and stopping rules before starting an A/B test.
- End every results document with "What did we learn and what changes next week?"

## Wrap-up and Next Steps

EDA is *time spent listening to the data*. Next we will look at *visualization* — showing what we heard.

## Answering the Opening Questions

- **How can you quickly read the shape of data before building a model?**
  - This article's EDA loop starts with `df.shape`, `df.dtypes`, `df.head()` for the overall outline, then checks distributions with `describe()` and histograms, followed by categorical unique values, scatter plots, missing rates, and correlation matrices. The key is not diving deep at once, but quickly scanning data size, distribution, relationships, and missingness.
- **Why does looking only at a single mean often lead to misunderstanding?**
  - Means easily hide long tails, skewness, and outliers — looking typical but poorly representing the actual distribution. That's why the article emphasized not just checking `df["amount"].describe()` but also building histogram and quantile/boxplot intuition alongside.
- **What order works best for examining distributions, missing patterns, and correlations?**
  - First read 1D distributions to understand value shapes, then check `df.isna().mean()` for empty regions, and finally examine `df.select_dtypes("number").corr().round(2)` for variable relationships. Looking at correlation before understanding distributions risks immediately misinterpreting spurious relationships created by outliers or missing patterns.
<!-- toc:begin -->
## In this series

- [Data Science 101 (1/10): What Is Data Science?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): Turning a Problem into a Data Problem](./02-problem-to-data-problem.md)
- [Data Science 101 (3/10): Data Collection](./03-data-collection.md)
- [Data Science 101 (4/10): Data Cleaning](./04-data-cleaning.md)
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

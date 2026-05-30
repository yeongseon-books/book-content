---
series: data-science-101
episode: 4
title: "Data Science 101 (4/10): Data Cleaning"
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
  - DataCleaning
  - Pandas
  - Quality
  - Beginner
seo_description: A 5-step guide to spotting and fixing missing values, duplicates, outliers, and type mismatches in real-world tabular data
last_reviewed: '2026-05-15'
---

# Data Science 101 (4/10): Data Cleaning

Cleaning is where data projects quietly win or lose. Most teams do not fail because the final model was mathematically weak. They fail because dates were still strings, duplicates were silently kept, or a fill rule changed the distribution without anybody noticing.

That is why cleaning should feel less like "tidying up" and more like quality control. You are not polishing data for presentation. You are deciding which evidence is safe enough to carry into EDA, metrics, and models.

This is the 4th post in the Data Science 101 series. In this chapter, we turn the messy middle of tabular work into a repeatable sequence for types, duplicates, missingness, outliers, and validation.


![data science 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/04/04-01-concept-at-a-glance.en.png)
*data science 101 chapter 4 flow overview*
> At its core, Data Cleaning is about deciding what enters a system, where validation happens, and which signals stay for the next cycle—not about feature names.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Data Cleaning?
- Which signal should the example or diagram make visible for Data Cleaning?
- What failure should be prevented first when Data Cleaning reaches a real system?

## Questions This Post Answers

- Which quality problems should you inspect first in tabular data?
- Why do type fixes, missingness, duplicates, and outliers need different treatment?
- How do simple fill rules distort later analysis if you apply them blindly?
- What should a cleaning report capture before you move on?

> Cleaning is the stage where you decide which rows are trustworthy enough to become evidence.

## What You Will Learn

- The *four big data-quality problems*
- Strategies for *handling missing values*
- The basics of *outlier detection*
- A 5-step cleaning exercise
- Five common pitfalls

## Why It Matters

*Garbage in, garbage out.* Even the best model produces *garbage* from dirty input. Cleaning is the *validation step*.

> *Cleaning is the *insurance policy* of analysis.*

The key boundary in this episode is between the concept itself and how it operates in a real system. You need to know where the data comes in, where the decision happens, and what signal must be recorded.

## Key Terms

- **Missing**: a value is *empty* (`NaN`, `None`, `''`).
- **Duplicate**: multiple rows with the *same key*.
- **Outlier**: a value *statistically far* from the rest.
- **Type coercion**: converting *strings to numbers/dates*.
- **Imputation**: a strategy to *fill in* missing values.

## Model Selection Criteria

After cleaning, you need to choose a suitable model. Model selection is not only about accuracy—it requires balancing data size, interpretability, speed, and precision.

| Condition | Data Size | Interpretability Needed | Speed Priority | Accuracy | Recommended Model |
|---|---|---|---|---|---|
| Small, must explain | Small | High | Medium | Medium | Logistic Regression, Decision Tree |
| Mid-size, balanced | Medium | Medium | Medium | High | Random Forest, Gradient Boosting |
| Large, accuracy first | Large+ | Low | Slow OK | Very High | XGBoost, LightGBM, Neural Network |
| Real-time prediction | Medium | Low | Very Fast | Medium | Logistic Regression, Naive Bayes |

When interpretability matters, Decision Tree or Logistic Regression fits best. When you need maximum accuracy regardless of speed, XGBoost or neural networks become the primary candidates.

## Comparing Multiple Models with cross_val_score

After cleaning, testing a single model is rarely enough. Comparing several models with cross-validation gives you confidence in the final choice.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
import numpy as np

X, y = load_iris(return_X_y=True)

models = {
    "Logistic Regression": LogisticRegression(max_iter=200),
    "Decision Tree": DecisionTreeClassifier(),
    "Random Forest": RandomForestClassifier(),
}

for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
    print(f"{name}: {np.mean(scores):.3f} (±{np.std(scores):.3f})")
```

This example compares three models using 5-fold cross-validation. Printing both mean accuracy and standard deviation shows which model is most stable. Running this kind of comparison after cleaning is always a safe default.

## No Free Lunch Theorem

The most important principle in model selection is the No Free Lunch theorem: **no single model is universally best across all problems.**

A model that dominates on one dataset may lose on another. In practice, clinging to a single algorithm matters less than running experiments and comparing results.

**Practical implications:**

- Start with a baseline model and increase complexity gradually.
- The right answer depends on the data, not on the algorithm's reputation.
- A simple model often beats a complex one.
- Always weigh the trade-off between interpretability, speed, and accuracy.

After cleaning, always pass through a model comparison stage. Starting simple and iterating upward is the safest path.

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

Type fixing is the starting point for nearly all cleaning work. Date comparisons break when dates are stored as strings, and aggregations go wrong when numeric columns contain text. Using `errors="coerce"` surfaces conversion failures as NaN, making problem rows easy to find.

### Step 2 — Drop duplicates

```python
print("before:", len(df))
df = df.drop_duplicates(subset=["user_id"], keep="last")
print("after :", len(df))
```

Simply dropping duplicates is rarely the whole story. Understanding *why* duplicates appeared prevents the same issue from recurring in the next collection cycle. Cleaning is a temporary repair; root-cause tracking is a separate task.

### Step 3 — Handle missing values

```python
# Inspect missingness
print(df.isna().mean().sort_values(ascending=False).head())

# Strategy: drop critical, fill optional
df = df.dropna(subset=["user_id", "signup_at"])
df["country"] = df["country"].fillna("UNKNOWN")
```

Always check missingness rates first. How empty the data is, whether nulls cluster in specific columns, and whether those columns are critical all influence strategy. Key identifiers are usually dropped; auxiliary columns are filled.

### Step 4 — Detect outliers

```python
q1, q3 = df["amount"].quantile([0.25, 0.75])
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
df["amount_flag"] = ~df["amount"].between(lower, upper)
print(df["amount_flag"].mean())
```

Outliers are not automatic deletion targets. They might be data errors, but they could also be important signals. The safe default is to flag first, then review in domain context.

### Step 5 — Validation report

```python
report = {
    "rows": len(df),
    "nulls": df.isna().sum().to_dict(),
    "outlier_rate": float(df["amount_flag"].mean()),
}
print(report)
```

After cleaning, record what changed and by how much. Row counts, remaining nulls per column, and outlier rates give you a baseline to compare against future runs.

**Expected output:** a validation report with remaining row count, null counts by column, and the outlier rate after cleaning.

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

Teams test cleaning steps with tools like *Great Expectations*. CI runs *data-quality alarms*; if they fire, the pipeline halts. The key insight is that cleaning rules should not depend on human intuition alone—they need to be encoded as executable checks.

## How a Senior Engineer Thinks

- Put *missingness* on a *dashboard* and monitor it continuously.
- Outliers go through *flag → review → decide*.
- Extract cleaning logic into *reusable functions*.
- Never modify the *original* — work on a *copy*.
- Treat *validation tests* like *code* — review them in PR.

## Cleaning Pattern Library and Reusable Preprocessing Functions

Cleaning is not something you redo from scratch for every project. The same errors recur within a domain: mixed date formats, amount strings, duplicate records, absent null-handling rules. Production teams therefore manage cleaning as reusable functions and checklists rather than throwaway notebook cells.

### Cleaning Pattern Comparison Table

| Pattern | When to Apply | Method | Side-effect Risk | What to Record |
|---|---|---|---|---|
| Type coercion | String-number/date mix | `to_numeric`, `to_datetime` | Increased coercion failures | Failure count/rate |
| Duplicate collapse | Same-key multiple rows | Latest-wins `drop_duplicates` | Over-deletion | Rows removed, key column |
| Missing-value fill | Non-critical column nulls | Rule-based fill | Distribution skew | Fill rule, fill rate |
| Outlier flag | Long-tailed distribution | IQR/Z-score flag | False positives | Threshold, flag rate |
| Category normalization | Many spelling variants | Mapping table | Unmapped entries | Unmapped list |

### Reusable Cleaning Function

```python
import pandas as pd

def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["order_at"] = pd.to_datetime(out["order_at"], errors="coerce")
    out["amount"] = pd.to_numeric(out["amount"], errors="coerce")

    out = out.dropna(subset=["order_id", "user_id", "order_at"])
    out = out.drop_duplicates(subset=["order_id"], keep="last")

    q1, q3 = out["amount"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    out["amount_outlier"] = ~out["amount"].between(lo, hi)

    out["country"] = out["country"].fillna("UNKNOWN").str.upper()
    return out
```

Wrapping logic in a function guarantees the same input produces the same output, enables code review, and makes testing straightforward.

### Automated Cleaning Report

```python
def build_cleaning_report(raw: pd.DataFrame, clean: pd.DataFrame) -> dict:
    return {
        "raw_rows": int(len(raw)),
        "clean_rows": int(len(clean)),
        "dropped_rows": int(len(raw) - len(clean)),
        "null_rate_top5": clean.isna().mean().sort_values(ascending=False).head().to_dict(),
        "outlier_rate": float(clean["amount_outlier"].mean()) if "amount_outlier" in clean else 0.0,
    }
```

Recording *what changed and by how much* is as important as cleaning itself. In team settings, the report gets read as often as the cleaning code.

### Cleaning Design Principles

- Never modify the original table.
- Record cleaning rules as code, not prose.
- Prefer flags over deletion so you can revisit later.
- Reflect domain rules (e.g., whether negative amounts are valid) in both documentation and code.
- Review cleaning changes as rigorously as model changes.

### Quality Gate Examples

- Pipeline fails if key-column null rate exceeds 0.1%.
- Warning fires if date-conversion failure rate exceeds 1%.
- Alert triggers if duplicate rate spikes (+50% week over week).
- Auto-creates investigation ticket if outlier flag rate jumps.

Cleaning is the invisible foundation of data science. When the foundation is solid, any analysis or model on top operates reliably.

## From Analysis to an Operational Loop

Connecting cleaning to real team operations requires moving past notebook-level notes into repeatable experiment loops. Three principles matter: feature-creation rules must live in both code and documentation; visualizations must serve as decision triggers, not decoration; and model evaluation must include behavioral impact, not just a score on one line.

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

This example transforms raw tables into user-level features designed for analysis. `log1p` mitigates skew, and behavioral features like `weekend_ratio` often provide more explanatory power than raw totals.

### Checking Distributions with matplotlib

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
agg["avg_amount"].hist(bins=30, edgecolor="black", ax=ax[0])
ax[0].set_title("Average Order Amount Distribution")
ax[0].set_xlabel("avg_amount")

agg.sort_values("signup_age").reset_index(drop=True)["order_count"].rolling(100).mean().plot(ax=ax[1])
ax[1].set_title("Order Count Rolling Mean by Signup Age")
ax[1].set_ylabel("rolling mean")

plt.tight_layout()
plt.show()
```

The purpose of visualization is not aesthetics—it is finding anomalies fast. If the distribution skews heavily, consider a log transform. If the rolling mean shifts abruptly, re-evaluate segment boundaries.

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

Using a pipeline keeps training and inference paths identical, eliminating the "works in a notebook but not in batch" class of bugs.

### A/B Test Design Template

Experiment design matters as much as modeling. The template below works for practical scenarios like marketing message improvements.

| Item | Design Example |
|---|---|
| Hypothesis | Changing the onboarding message increases 7-day return rate. |
| Population | New users signed up in the last 14 days (excluding internal accounts). |
| Randomization | 50:50 split by user_id hash. |
| Primary metric | 7-day return rate. |
| Guardrail metrics | Support ticket rate, payment failure rate. |
| Duration | Minimum 2 weeks or until sample size reached. |
| Stop condition | Guardrail metric degradation exceeds threshold. |

The most common A/B mistake is concluding too early. Without a pre-registered stopping rule and analysis plan, random fluctuations get mistaken for real effects.

### Connecting Pipeline Results to Experiment Allocation

```python
import pandas as pd

scored = pd.read_csv("scored_users.csv")
scored = scored.sort_values("risk_score", ascending=False)

eligible = scored.query("is_marketing_opt_in == 1 and recent_complaint == 0").copy()
eligible["bucket"] = (eligible.index % 2).map({0: "A", 1: "B"})

plan = eligible[["user_id", "risk_score", "bucket"]].head(5000)
print(plan["bucket"].value_counts())
print(plan.head())
```

At this stage, rules matter more than scores. Fixing exclusion criteria, assignment rules, and experiment size before launch reduces interpretation conflicts after the experiment ends.

### Operational Checkpoints

- Record feature-creation rules in both code and documentation.
- For every EDA chart, write one line: "What decision does this chart trigger?"
- Evaluate models on cost, latency, and operational complexity alongside accuracy.
- Fix hypothesis, sample size, and stopping rule before an A/B test starts.
- End every results document with "What did we learn and what changes next week?"

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

## Answering the Opening Questions

- **What order should data cleaning follow?**
  - This article's basic order is: type fixes → duplicate removal → missing value handling → outlier flagging → validation report. The `pd.to_datetime`, `drop_duplicates`, `dropna`/`fillna`, IQR-based `amount_flag`, and final `report` dictionary showed that order directly.
- **Why must missing values, duplicates, outliers, and type mismatches be checked first?**
  - These problems break aggregations and filters even before modeling. For example, if `signup_at` is a string, date comparisons break; if `user_id` duplicates or `df.isna().mean()` reveals missing values go unnoticed, all downstream metrics and features are contaminated from the start.
- **Why is a simple treatment like filling with `0` dangerous?**
  - `0` is often a meaningful actual value rather than "no value," so it conflates missing data with real zeros. That's why the article distinguished: drop rows with `dropna(subset=[...])` for key columns, and only use `fillna("UNKNOWN")` for auxiliary columns like `country`.
<!-- toc:begin -->
## In this series

- [Data Science 101 (1/10): What Is Data Science?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): Turning a Problem into a Data Problem](./02-problem-to-data-problem.md)
- [Data Science 101 (3/10): Data Collection](./03-data-collection.md)
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

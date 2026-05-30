---
series: data-science-101
episode: 6
title: "Data Science 101 (6/10): Visualization"
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
  - Visualization
  - Matplotlib
  - Seaborn
  - Beginner
seo_description: A practical map from message to chart — distributions, comparisons, trends, relations, and parts of a whole, with rules that keep them honest
last_reviewed: '2026-05-15'
---

# Data Science 101 (6/10): Visualization

Charts are not the decorative end of analysis. They are the moment when your conclusions become fast enough for other people to consume. A good chart compresses a page of explanation into one glance. A bad chart makes a bad decision look reasonable.

That is why visualization is really about judgment, not software. The core skill is picking a visual form that matches the message, then removing the distortions that exaggerate or hide what the data is actually saying.

This is the 6th post in the Data Science 101 series. In this chapter, we connect common analytical messages to chart choices, and we treat axes, color, labels, and annotations as decision-support tools rather than styling details.


![data science 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/06/06-01-concept-at-a-glance.en.png)
*data science 101 chapter 6 flow overview*
> At its core, Visualization is about deciding what enters a system, where validation happens, and which signals stay for the next cycle—not about feature names.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Visualization?
- Which signal should the example or diagram make visible for Visualization?
- What failure should be prevented first when Visualization reaches a real system?

## Questions This Post Answers

- How do you choose a chart from the message instead of from habit?
- Which chart choices most often create misleading comparisons or trends?
- Why do axis scale, labels, and annotations change the decision a chart supports?
- How can one chart remain readable and honest for more than one audience?

> The right chart is the one that makes the intended decision easier without exaggerating the pattern.

## What You Will Learn

- A mapping from *5 messages* to *5 charts*
- Basic rules for *axis, color, labels*
- Patterns that *mislead* the reader
- A 5-step visualization exercise
- Five common pitfalls

## Why It Matters

Data is fastest to read as a *picture*. The wrong chart leads to the *wrong decision*. A clear *message-to-chart* mapping eliminates *half* of the misreadings.

> *Visualization is the *last line* of an analysis.*

The key boundary in this episode is between the concept itself and how it operates in a real system. You need to know where the data comes in, where the decision happens, and what signal must be recorded.

## Key Terms

- **Encoding**: mapping data to *position, length, color*.
- **Scale**: *linear, log* — the axis transform.
- **Faceting**: *small multiples* for comparison.
- **Annotation**: *notes and highlights* on the chart.
- **Colorblind-safe**: a palette that works for color-vision deficiencies.

## Before / After

**Before**: a *3D pie chart* makes proportions *impossible to compare*.

**After**: a *horizontal bar chart* makes them *exactly comparable*.

## Hands-on: 5-step Visualization

### Step 1 — Distribution (histogram)

```python
import matplotlib.pyplot as plt
df["amount"].plot.hist(bins=30, title="amount distribution")
plt.show()
```

### Step 2 — Comparison (bar)

```python
(
    df.groupby("country")["amount"]
      .sum()
      .sort_values()
      .plot.barh(title="revenue by country")
)
plt.show()
```

### Step 3 — Trend (line)

```python
df.groupby("order_date")["amount"].sum().plot(title="daily revenue")
plt.show()
```

### Step 4 — Relation (scatter + facet)

```python
import seaborn as sns
sns.relplot(
    data=df.sample(2000),
    x="quantity",
    y="amount",
    col="country",
    col_wrap=3,
)
```

### Step 5 — Annotation and color

```python
ax = df.groupby("order_date")["amount"].sum().plot()
ax.axvline(pd.Timestamp("2026-04-01"), color="red", linestyle="--", label="campaign")
ax.legend()
```

**Expected output:** a first-pass chart choice tied to the message, plus the annotation points needed to keep the chart honest.

## What to Notice in This Code

- The *message-to-chart* mapping comes *first*.
- The *axis scale* changes the *reading*.
- *Annotations* save the reader from a paragraph of explanation.

## Five Common Mistakes

1. **Using *3D charts*.** Comparisons become *hard*.
2. **Overusing *dual axes*.** A common source of *misreading*.
3. **Encoding categories *only by color*.** Unfriendly to *colorblind* users.
4. **Bar charts that don't start at *zero*.** They *exaggerate* differences.
5. **Charts without *labels*.** Not reusable next week.

## Message-to-Chart Selection Guide

The same dataset serves different messages depending on the chart you pick. The table below turns "what do I want to say?" into "which chart says it best?"

| Message goal | Recommended chart | Avoid | Why |
| --- | --- | --- | --- |
| Compare items | Horizontal / vertical bar | 3D pie | Length comparison is precise |
| Show time trend | Line chart | Stacked area (early stage) | Direction and rate are clear |
| Reveal distribution | Histogram, box plot | Showing mean only | Tails and outliers become visible |
| Explore relationships | Scatter plot | Overcrowded line chart | Variable-pair patterns emerge |
| Show composition | 100% stacked bar | Pie with too many slices | Category comparison stays easy |

### Same data, different purpose — matplotlib / seaborn example

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sales = pd.read_csv("sales.csv", parse_dates=["date"])

# 1) Trend
trend = sales.groupby("date", as_index=False)["revenue"].sum()
plt.figure(figsize=(10, 4))
plt.plot(trend["date"], trend["revenue"])
plt.title("Daily Revenue Trend")
plt.xlabel("Date")
plt.ylabel("Revenue")
plt.tight_layout()
plt.show()

# 2) Channel comparison
channel = sales.groupby("channel", as_index=False)["revenue"].sum().sort_values("revenue")
plt.figure(figsize=(8, 4))
plt.barh(channel["channel"], channel["revenue"])
plt.title("Revenue by Channel")
plt.tight_layout()
plt.show()
```

When the purpose changes from "show the trend" to "compare channels," the encoding must change too. A line chart for comparison forces the reader to decode endpoints; a bar chart makes the answer immediate.

### Design Rules for Honest Charts

- Bar charts start at zero by default.
- Units and time range appear in the axis label.
- Use one accent color for emphasis; keep the rest neutral.
- Prefer direct labels over legends when possible.
- Mark events (deploys, campaigns) with vertical annotation lines.

### Chart Review Checklist

- Can the question this chart answers be stated in one sentence?
- Can the reader extract the key message within 5 seconds?
- Is there any axis distortion or dual-axis confusion risk?
- Can a colorblind viewer still distinguish categories?
- Does the caption state "so what should we do?"

### Caption Template for Reports

"Mobile-channel revenue dropped 8% week-over-week over the last 4 weeks, while web-channel rose 2% over the same period. Next week's budget adjustment should prioritize a mobile retention campaign."

When a caption closes with an action recommendation, the chart graduates from illustration to decision tool.

## From Analysis to Operational Loop

Connecting visualization to real team workflows requires going beyond analysis notebooks into repeatable experiment loops. Three principles: (1) feature-creation rules live in both code and documentation; (2) charts serve as decision-trigger checkpoints, not decoration; (3) model evaluation includes behavioral change, not just a score.

### Building a Feature Table with NumPy and Pandas

```python
import numpy as np
import pandas as pd

orders = pd.read_csv('orders.csv', parse_dates=['ordered_at'])
users = pd.read_csv('users.csv', parse_dates=['signup_at'])

base = orders.merge(users[['user_id', 'signup_at', 'country']], on='user_id', how='left')
base['days_since_signup'] = (base['ordered_at'] - base['signup_at']).dt.days.clip(lower=0)
base['is_weekend'] = base['ordered_at'].dt.dayofweek.isin([5, 6]).astype(int)
base['amount_log1p'] = np.log1p(base['amount'].clip(lower=0))

agg = (
    base.groupby('user_id', as_index=False)
    .agg(
        order_count=('order_id', 'count'),
        avg_amount=('amount', 'mean'),
        recent_amount=('amount', 'last'),
        signup_age=('days_since_signup', 'max'),
        weekend_ratio=('is_weekend', 'mean'),
    )
)

print(agg.head())
```

This transforms raw tables into a user-level feature set designed for the analysis goal. `log1p` mitigates skew, and behavioral features like `weekend_ratio` often explain more variance than raw totals.

### Checking Distribution and Segment Patterns with Matplotlib

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
agg['avg_amount'].hist(bins=30, edgecolor='black', ax=ax[0])
ax[0].set_title('Average Order Amount Distribution')
ax[0].set_xlabel('avg_amount')

agg.sort_values('signup_age').reset_index(drop=True)['order_count'].rolling(100).mean().plot(ax=ax[1])
ax[1].set_title('Order Count Rolling Mean by Signup Age')
ax[1].set_ylabel('rolling mean')

plt.tight_layout()
plt.show()
```

The goal is not a pretty chart but a fast anomaly signal. If the distribution is heavily skewed, consider a log transform. If the rolling mean jumps at a segment boundary, revisit your segmentation criteria.

### Managing Preprocessing and Model in One sklearn Pipeline

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

num_cols = ['order_count', 'avg_amount', 'recent_amount', 'signup_age', 'weekend_ratio']
cat_cols = ['country']

numeric = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
])

categorical = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore')),
])

preprocess = ColumnTransformer([
    ('num', numeric, num_cols),
    ('cat', categorical, cat_cols),
])

model = Pipeline([
    ('preprocess', preprocess),
    ('clf', LogisticRegression(max_iter=1000, class_weight='balanced')),
])
```

A pipeline guarantees that training and inference follow the same path. This eliminates the classic "works in the notebook, breaks in the batch job" failure mode.

### A/B Test Design Template

Experiment design matters as much as modeling. The template below applies directly to scenarios like onboarding-message improvements.

| Item | Design example |
| --- | --- |
| Hypothesis | Changing the onboarding message increases 7-day return rate. |
| Population | New users who signed up in the last 14 days (internal accounts excluded). |
| Randomization | 50:50 split based on user_id hash. |
| Primary metric | 7-day return rate. |
| Guardrail metrics | Support ticket rate, payment failure rate. |
| Duration | Minimum 2 weeks or until sample size is reached. |
| Stop condition | Guardrail metric degradation exceeds threshold. |

The most common A/B mistake is calling results too early. Without a pre-registered stopping rule and analysis plan, random fluctuations get mistaken for real effects.

### Connecting Pipeline Scores to an Experiment

```python
import pandas as pd

scored = pd.read_csv('scored_users.csv')
scored = scored.sort_values('risk_score', ascending=False)

eligible = scored.query('is_marketing_opt_in == 1 and recent_complaint == 0').copy()
eligible['bucket'] = (eligible.index % 2).map({0: 'A', 1: 'B'})

plan = eligible[['user_id', 'risk_score', 'bucket']].head(5000)
print(plan['bucket'].value_counts())
print(plan.head())
```

At this stage, rules matter more than scores. Fixing exclusion criteria, assignment rules, and experiment size before launch prevents interpretation conflicts after the experiment ends.

### Operational Checkpoints

- Record feature-creation rules in both code and documentation.
- For every EDA chart, write one sentence: "Based on this chart, the decision is..."
- Evaluate model scores alongside cost, latency, and operational complexity.
- Lock hypothesis, sample size, and stopping rules before launching an A/B test.
- Close every results document with "what we learned and what changes next week."

## How This Shows Up in Production

Analysts mix *Tableau / Looker* dashboards with *Python* charts. A *dashboard* is the standard *unit of a weekly report*.

## How a Senior Engineer Thinks

- Write the *message first*, then pick the *chart*.
- Always fill in *axis and labels*.
- Default to a *colorblind-safe palette*.
- Use *annotations* to provide *context*.
- A dashboard should reach a *decision* within *3 screens*.

## Checklist

- [ ] I know the *5 message-to-chart* pairings.
- [ ] I value *axis and labels*.
- [ ] I know *colorblind-safe* palettes.
- [ ] I add *annotations* to aid interpretation.

## Practice Problems

1. Plot the *same data* with *3 different charts* and pick the clearest.
2. Take a *misleading* chart and *fix* it.
3. Sketch a *one-page dashboard* using *3 charts*.

## Wrap-up and Next Steps

Visualization is the *bridge from analysis to decision*. Next we move into *modeling* — using data to *predict*.

## Answering the Opening Questions

- **Which chart should you use for which message?**
  - If the message is about distribution, use histograms; comparisons, `plot.barh`; trends, line charts; relationships, `sns.relplot` or scatter plots. This article was structured to build the habit of choosing charts by the question you want to answer, not the data type.
- **Why do some graphs aid understanding while others create misunderstanding with the same data?**
  - Even the same proportion data becomes hard to compare in a 3D pie chart due to area and perspective distortion, while switching to a horizontal bar chart makes length differences immediately readable. Charts themselves change data interpretation rules, so incorrect encoding creates misunderstanding even without hiding facts.
- **Why are axes, colors, and labels core design elements rather than minor decoration?**
  - Context annotations like `ax.axvline(pd.Timestamp("2026-04-01"), ...)` are needed to read pre/post campaign context, and colorblind-safe palettes with labels are needed to reliably distinguish categories. A chart's message is completed not by data points alone but by axis scale, legend, and text annotations combined.
<!-- toc:begin -->
## In this series

- [Data Science 101 (1/10): What Is Data Science?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): Turning a Problem into a Data Problem](./02-problem-to-data-problem.md)
- [Data Science 101 (3/10): Data Collection](./03-data-collection.md)
- [Data Science 101 (4/10): Data Cleaning](./04-data-cleaning.md)
- [Data Science 101 (5/10): Exploratory Data Analysis](./05-exploratory-data-analysis.md)
- **Visualization (current)**
- Modeling (upcoming)
- Evaluation (upcoming)
- Result Interpretation (upcoming)
- End-to-End Data Project Flow (upcoming)

<!-- toc:end -->

## References

- [matplotlib — Tutorials](https://matplotlib.org/stable/tutorials/index.html)
- [seaborn — Tutorial](https://seaborn.pydata.org/tutorial.html)
- [Cole Knaflic — Storytelling with Data](https://www.storytellingwithdata.com/)
- [Tableau — Visual Best Practices](https://www.tableau.com/learn/articles/data-visualization-tips)

Tags: DataScience, Visualization, Matplotlib, Seaborn, Beginner

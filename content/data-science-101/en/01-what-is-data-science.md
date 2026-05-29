---
series: data-science-101
episode: 1
title: "Data Science 101 (1/10): What Is Data Science?"
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
  - Introduction
  - Workflow
  - Analytics
  - Beginner
seo_description: A practical definition of data science, the differences between analyst, scientist and engineer roles, and the workflow that ties everything together
last_reviewed: '2026-05-15'
---

# Data Science 101 (1/10): What Is Data Science?

People usually enter data science through tools. They install pandas, copy a scikit-learn tutorial, and learn a dashboard product. A few weeks later, the vocabulary gets blurry. Analytics, experimentation, forecasting, ML engineering, and BI all sound adjacent, but not identical.

That confusion matters because the field only starts to make sense when you see the job as a decision pipeline rather than a pile of techniques. If you cannot explain how a question becomes data, how data becomes evidence, and how evidence changes an action, every later chapter feels like isolated syntax.

This is the first post in the Data Science 101 series. Here we build the mental model for the rest of the series: data science is the work of turning a fuzzy business question into a repeatable decision loop.


![data science 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/01/01-01-concept-at-a-glance.en.png)
*data science 101 chapter 1 flow overview*
> Data science is about deciding what to verify at each boundary and which signal to keep—not about feature names or techniques.

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is Data Science??
- Which signal should the example or diagram make visible for What Is Data Science??
- What failure should be prevented first when What Is Data Science? reaches a real system?

## Questions This Post Answers

- What practical definition keeps data science from collapsing into a vague umbrella term?
- Where do analyst, scientist, engineer, and EDA work split apart in a real team?
- Why does the workflow have to end in a decision instead of a notebook or dashboard?
- Which misconceptions make beginners learn tools in the wrong order?

> Data science is the discipline of translating a business problem into evidence strong enough to change a decision.

## What You Will Learn

- A working *definition* of data science
- The *differences* between analyst, scientist, and engineer
- A typical *5-step workflow*
- Common questions from *beginners*
- Five common misconceptions

## Why It Matters

In a field full of *overlapping titles*, the boundaries blur fast. A clear *big picture* tells you *which tools to learn first* and *why*.

> *Learning without a *big picture* is just a pile of fragments.*

The fundamental distinction in this episode is between recognizing What Is Data Science as an abstract concept and understanding how it manifests at system boundaries—where data enters, where checks occur, and which signals persist.

## Key Terms

- **Data Analyst**: answers *business questions* through *metrics and dashboards*.
- **Data Scientist**: builds *models* and runs *experiments*.
- **ML Engineer**: takes models and *puts them into production*.
- **Data Engineer**: builds *pipelines* and the *warehouse*.
- **EDA**: Exploratory Data Analysis — looking at the data before modeling.

## Before / After

**Before**: you *have data*, so you analyze *something* and hope it sticks. Results feel *fuzzy*.

**After**: you frame *one problem* in one sentence and only look at the *data that matters*. Results are *clear*.

## Hands-on: 5-step Workflow

### Step 1 — Define the problem

```text
"Each week, pick 100 users most likely to churn"
```

### Step 2 — Collect data

```python
import pandas as pd
df = pd.read_csv("users.csv")
print(df.shape, df.columns.tolist())
```

The important thing here is not the syntax for reading a file—it is knowing which source produced this data and at what point in time. If you cannot reproduce the same analysis two months later, the result loses trust.

### Step 3 — Clean and EDA

```python
df = df.dropna(subset=["last_login"])
df["days_since_login"] = (
    pd.Timestamp.today() - pd.to_datetime(df["last_login"])
).dt.days
print(df["days_since_login"].describe())
```

Collected data is almost never ready to use directly. There are missing values, type mismatches, and distributions that need visual inspection first. EDA is not a formality before modeling—it is the time the data introduces itself to you.

### Step 4 — Model or rule

```python
candidates = (
    df[df["days_since_login"] > 30]
      .sort_values("amount_total", ascending=False)
      .head(100)
)
```

Not every problem requires a complex model. Sometimes a simple rule-based priority is enough to deliver value. The key is problem fit, not sophistication.

### Step 5 — Tie back to a decision

```text
Email campaign for 100 users → measure conversion → adjust next week
```

Without this last step, data work often stalls at the report stage. Results must close with "what will we do?" That way you can measure again next week, improve, and run the same loop.

**Expected output:** a compact workflow note that connects the problem statement, the key data, and the final decision in one line of reasoning.

## What to Notice in This Code

- *One sentence of problem* sets the direction for *every line*.
- The data flow is simple: *read → clean → explore → decide*.
- A model or dashboard only has value when it ends in a *decision*.

## Five Common Mistakes

1. **Learning *tools first*.** Without a problem, tools have *no direction*.
2. **Optimizing only for *model accuracy*.** Watch the *business metric* too.
3. **Skipping EDA and *fixing a hypothesis* too early.** You miss what the data is actually telling you.
4. **Ignoring *role boundaries*.** Hiring and collaboration get *tangled*.
5. **Not connecting results to *decisions*.** Reports go straight to a *drawer*.

## How This Shows Up in Production

Startup data teams often look like a mini-org of analyst + scientist + engineer. They run on topic-level OKRs, and every week they tie dashboards or models back to concrete decisions. Roles may overlap, but all work converges on one question: "Which decision does this result change?" Data work without that question rarely survives long.

## How a Senior Engineer Thinks

- *Problem framing* is more expensive than *modeling*.
- Never *skimp on EDA*.
- Always *close the loop* with a decision.
- *Document* the boundaries between roles.
- *Data quality* is everyone's job, not just the engineer's.

## Practical Extension: Understanding the Data Science Process as Structure

Once you have the definition and role boundaries from the previous sections, the next step is seeing how real projects are run stage by stage. Beginners tend to memorize tool lists first, but in practice the sequence and deliverables matter more than the tools. The same Python and the same pandas produce unreproducible results when the problem definition is fuzzy. Conversely, when stages and deliverables are explicit, quality holds even as the team grows. This section maps the iterative loop of data science through a CRISP-DM lens and compares which roles take the lead at each stage.

### CRISP-DM: Six Stages and Key Deliverables

| Stage | Core Question | Main Activities | Representative Deliverable | Failure Signal |
| --- | --- | --- | --- | --- |
| Business Understanding | What are we trying to improve? | Define goals, constraints, costs | Problem statement, KPI | Goal is abstract |
| Data Understanding | What data exists? | Source audit, initial EDA | Data inventory, quality notes | Unknown-source data used |
| Data Preparation | Is the data model-ready? | Clean, join, feature engineering | Cleaning script, feature set | Rules not documented |
| Modeling | Which method fits? | Baseline, experiment | Experiment log, model candidates | No comparison to baseline |
| Evaluation | Can it be deployed? | Metrics, cost, risk review | Evaluation report, go/no-go | Only accuracy considered |
| Deployment/Operations | Does it drive action? | Monitoring, retraining plan | Dashboard, alert rules | No post-deploy tracking |

A common thread runs through every stage: each must close as "question → activity → deliverable." If there is activity without a deliverable, the next stage cannot share context. Beginners benefit from measuring progress by "what did I produce?" rather than "what did I try?"

### Role Comparison: Same Team, Different Responsibilities

Role titles look similar, but their centers of gravity differ. The table below is organized around the friction points that commonly arise in team collaboration.

| Role | Primary Question | Primary Deliverable | Collaboration Interface |
| --- | --- | --- | --- |
| Data Analyst | How do we describe the current state? | Metric definitions, dashboards, analysis memos | PM, marketing, ops |
| Data Scientist | What predictions or optimizations are possible? | Experiment notebooks, model evaluation reports | Analyst, ML engineer |
| ML Engineer | How do we serve the model reliably? | Serving pipeline, monitoring | Backend, platform |
| Data Engineer | How do we supply trustworthy data? | ETL/ELT, warehouse models | All roles |

The point is not hierarchy but boundaries. Clear boundaries make responsibilities clear, and clear responsibilities let you trace a quality issue to its root quickly.

### Minimal Analysis Loop in Python

The following code is not about complex modeling—it is the smallest possible check of a "problem → metric → action" loop.

```python
import pandas as pd

orders = pd.read_csv("orders.csv")
orders["order_date"] = pd.to_datetime(orders["order_date"])

recent = orders[orders["order_date"] >= "2026-05-01"]
summary = (
    recent.groupby("channel", as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
)

print(summary)
print("Decision: next week paid budget focuses on top-2 channels")
```

Simple as it is, this code embodies three principles. First, it states a time window explicitly. Second, it states the aggregation key explicitly. Third, it closes with an action sentence. Beginners should repeat small loops like this to build intuition for problem definition and decision closure.

### Operational Checkpoints Before Starting a Project

- Have you written the target metric in one sentence?
- Are the comparison period and target cohort agreed upon?
- Are data sources and extraction timestamps being logged?
- Is there a baseline and a final judgment criterion?
- Is the decision owner who will receive results identified?

If these five items are blank, the project is likely to drag regardless of technical skill. Conversely, when they are filled, even rough tool skills can produce high-quality outcomes quickly.

## Deep Dive: Turning Analysis Design Into a Repeatable Loop

Connecting the concepts above to real team operations means moving beyond analysis notes into repeatable experiment loops. Three things are essential. First, feature creation rules must live in both code and documentation simultaneously. Second, visualizations must serve as decision-trigger checkpoints, not decorative illustrations. Third, model evaluation must include behavioral change, not just a single score line.

### Building a Feature Table with NumPy and pandas

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

This example transforms raw tables into a user-level feature set tailored to the analysis goal. Transforms like `log1p` reduce distribution skew, and behavioral features like `weekend_ratio` often explain more than raw sums.

### Checking Distributions and Segment Patterns with Matplotlib

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

The purpose of visualization is not a pretty chart—it is fast anomaly detection. If a distribution is heavily skewed, consider a log transform. If a rolling average shows a sharp inflection, revisit your segmentation criteria. Each chart should trigger a next action.

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

A pipeline ensures that training and inference follow the same path, eliminating "works in notebook but breaks in batch" problems. This is the most reliable way to keep preprocessing and model logic coupled.

### A/B Test Design Template

Experiment design is as important as modeling. The template below applies directly to scenarios like onboarding message optimization.

| Item | Design Example |
| --- | --- |
| Hypothesis | Changing the new-user onboarding message increases 7-day return rate. |
| Population | Users who signed up in the last 14 days (excluding internal accounts) |
| Randomization | 50:50 split by user_id hash |
| Primary Metric | 7-day return rate |
| Guardrail Metrics | Support ticket rate, payment failure rate |
| Duration | Minimum 2 weeks or until sample size reached |
| Stopping Rule | Guardrail metric deterioration exceeds threshold |

The most common mistake in A/B testing is declaring results too early. When you peek at intermediate results repeatedly, pre-registered stopping rules and analysis plans prevent mistaking random fluctuation for a real effect.

### Operational Checkpoints

- Record feature creation rules in both code and documentation.
- For every EDA chart, write one line: "What decision does this chart inform?"
- Evaluate models on cost, latency, and operational complexity alongside accuracy.
- Fix hypothesis, sample size, and stopping rules before an A/B test starts.
- Close every results document with "what we learned and what we change next week."

## Checklist

- [ ] I can describe the difference between *analyst, scientist, engineer*.
- [ ] I know what *EDA* is.
- [ ] I understand the *problem → data → decision* flow.
- [ ] I know why a *business metric* matters.

## Practice Problems

1. Pick a *recent dashboard* you saw and write down the *decision* it led to.
2. Write *3 things in common* between analyst and scientist roles.
3. Write *3 problem statements* in one sentence each.

## Wrap-up and Next Steps

Data science is the job of bridging problems and data. It is not mastery of any single tool—it is the discipline of closing the loop from question to evidence to action. Once this perspective clicks, collection, cleaning, EDA, visualization, and modeling each find their place naturally. Next, we will see how to turn a vague problem into a data problem you can actually work on.

## Answering the Opening Questions

- **How can you understand data science in one sentence?**
  - Data science is a feedback loop of reading problems, building evidence from data, and using that evidence to change decisions.
- **What distinguishes data analysts, data scientists, ML engineers, and data engineers?**
  - Analysts track metrics, scientists build models, and engineers put those models into production systems.
- **Why must data work always start with problem definition?**
  - A clear problem definition lets you collect only the necessary data and skip unnecessary analysis.
<!-- toc:begin -->
## In this series

- **What Is Data Science? (current)**
- Turning a Problem into a Data Problem (upcoming)
- Data Collection (upcoming)
- Data Cleaning (upcoming)
- Exploratory Data Analysis (upcoming)
- Visualization (upcoming)
- Modeling (upcoming)
- Evaluation (upcoming)
- Result Interpretation (upcoming)
- End-to-End Data Project Flow (upcoming)

<!-- toc:end -->

## References

- [Drew Conway — The Data Science Venn Diagram](http://drewconway.com/zia/2013/3/26/the-data-science-venn-diagram)
- [Google — Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Hadley Wickham — R for Data Science](https://r4ds.hadley.nz/)
- [Stitch Fix — Multithreaded Engineering Blog](https://multithreaded.stitchfix.com/)

Tags: DataScience, Introduction, Workflow, Analytics, Beginner

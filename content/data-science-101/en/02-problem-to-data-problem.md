---
series: data-science-101
episode: 2
title: "Data Science 101 (2/10): Turning a Problem into a Data Problem"
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
  - ProblemFraming
  - Metrics
  - Workflow
  - Beginner
seo_description: A 5-step framing technique for turning vague business questions into measurable data questions, with the falsifiability traps to watch
last_reviewed: '2026-05-15'
---

# Data Science 101 (2/10): Turning a Problem into a Data Problem

Most analytics requests arrive as loose complaints, not well-formed questions. "Revenue feels down." "Churn seems worse." "Did that campaign work?" The problem is not that these questions are unimportant. The problem is that data cannot answer them until someone pins down the metric, the time window, and the population.

Strong data work starts before SQL, notebooks, or models. It starts when the team rewrites a vague request into a sentence that could be proven wrong. That single rewrite usually decides whether the rest of the project is fast and reliable or slow and argumentative.

This is the 2nd post in the Data Science 101 series. In this chapter, we turn problem framing into an explicit workflow you can reuse before any collection, EDA, or modeling begins.


![data science 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/02/02-01-concept-at-a-glance.en.png)
*data science 101 chapter 2 flow overview*
> At its core, Turning a Problem into a Data Problem is about deciding what enters a system, where validation happens, and which signals stay for the next cycle—not about feature names.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Turning a Problem into a Data Problem?
- Which signal should the example or diagram make visible for Turning a Problem into a Data Problem?
- What failure should be prevented first when Turning a Problem into a Data Problem reaches a real system?

## Questions This Post Answers

- Why are business questions usually too vague for data to answer directly?
- How do metric, time window, and population narrow the scope of analysis?
- What makes a data question falsifiable instead of merely interesting?
- How does stronger framing shorten the rest of the project?

> A data question becomes tractable only after you lock the metric, the time window, the population, and the testable claim.

## What You Will Learn

- A 5-step framing for *business question → data question*
- How to pick a *measurable metric*
- How to write a *falsifiable hypothesis*
- A *5-step* framing exercise
- Five common traps

## Why It Matters

A *fuzzy question* gives you *no way to choose* the right data. *Framing* is *half of the analysis*.

> *One precise sentence saves *three weeks* of analysis.*

The key boundary in this episode is between the concept itself and how it operates in a real system. You need to know where the data comes in, where the decision happens, and what signal must be recorded.

## Key Terms

- **Metric**: a *number* you can measure (DAU, conversion rate, revenue).
- **Window**: the *time range* of analysis (last 30 days).
- **Population**: the *group* you analyze (paid subscribers).
- **Hypothesis**: a statement that *could be wrong*.
- **Counterfactual**: the *"what if" scenario* — what would have happened without the change.

## Before / After

**Before**: *"Why did revenue drop?"* → no idea where to start.

**After**: *"Did paid-subscriber MRR drop more than 5% in the last 30 days vs the previous 30 days?"* → one query.

## Hands-on: 5-step Framing

### Step 1 — Write the vague question

```text
"Revenue feels like it's dropping"
```

The starting point is usually this vague. That is fine. What matters is not forcing analysis immediately but surfacing what the question is missing.

### Step 2 — Pick a metric

```text
metric = monthly_revenue
```

The metric is the axis that holds the entire analysis together. Whether it is revenue, active users, or order count changes everything about which data you need.

### Step 3 — Pick a window

```text
window = last 30 days vs previous 30 days
```

Different comparison windows produce different conclusions. If one team looks at 7 days and another looks at 30 days, the discussion diverges. The window must be stated inside the question.

### Step 4 — Narrow the population

```text
population = paid subscribers (excluding trials)
```

Looking at all users at once buries important patterns. Mixing free and paid users, or trials with actual customers, contaminates the comparison.

### Step 5 — Rewrite as falsifiable

```text
"Paid-subscriber monthly revenue dropped more than 5% in the last 30 days versus the prior 30 days."
```

Now the question can be answered by data. You can check whether it is true or false, and the required aggregation is clear. Good data questions are almost always this specific.

**Expected output:** one falsifiable question that explicitly names the metric, time window, and target population.

## What to Notice in This Code

- The *metric* is the spine of the analysis.
- *Window* and *population* keep the comparison *fair*.
- A hypothesis must be *falsifiable* before the data can answer.

## Five Common Mistakes

1. **Choosing the *metric last*.** The analysis loses direction.
2. **Using *different windows* across teams.** Comparisons become *unfair*.
3. **Letting the *population shift*.** Trends get *contaminated*.
4. **Writing *unfalsifiable* hypotheses.** *"We are growing"* can never be proven or disproven.
5. **Asking *several questions at once*.** Answers blur together.

## How This Shows Up in Production

When PMs send a *fuzzy request*, the data team *rewrites* it through the 5-step frame and replies with a *clear question*. Many teams treat this as a *question review* — same rigor as a code review.

## How a Senior Engineer Thinks

- Pick the *metric first*.
- Document *window and population* explicitly.
- Always check *falsifiability*.
- Treat *question review* as seriously as *code review*.
- *If you can't answer it*, rewrite the question.

## Checklist

- [ ] I can write *metric, window, population* clearly.
- [ ] I can write a *falsifiable hypothesis*.
- [ ] I understand *counterfactual*.
- [ ] I can rewrite a *vague request* as a clean question.

## Framing Template for Measurable Questions

Problem framing is the early design phase that determines project quality. Many teams agree "the question matters" but still leave abstract requests in their documents. In practice, teams do not accept requests as-is — they rewrite them through a common template. This process shrinks the data collection scope, speeds up analysis, and reduces interpretation conflicts.

### Problem Frame to Fill Before Choosing Collection Methods

| Item | Must Include | Example |
|---|---|---|
| Goal | What do we want to change? | Reduce paid subscription churn rate |
| Metric | What do we measure with? | 30-day churn rate, re-subscription rate |
| Window | What period do we compare? | Last 30 days vs prior 30 days |
| Population | Who do we include/exclude? | Paid users, excluding trials |
| Action | What do we do with the result? | Retention campaign for at-risk segment |

If you cannot fill this table, the question has not been converted into a data problem yet. Particularly when "Population" is missing, analysis results tend to over-generalize.

### Request Sentence Improvement

- **Before**: "Payments seem to be dropping — can you look into the cause?"
- **After**: "Verify whether paid-user payment amount dropped more than 7% in the last 4 weeks vs the prior 4 weeks. If confirmed, decompose by country/device/acquisition channel and propose the priority response segment."

The improved sentence contains both measurement conditions and action conditions. This structure ensures analysis results lead to operational work rather than ending as reports.

### Python: Converting a Framing Sentence into Verifiable Conditions

```python
import pandas as pd

pay = pd.read_csv("payments.csv", parse_dates=["paid_at"])
now_start = pd.Timestamp("2026-05-01")
prev_start = pd.Timestamp("2026-04-01")

curr = pay[(pay["paid_at"] >= now_start) & (pay["paid_at"] < now_start + pd.Timedelta(days=30))]
prev = pay[(pay["paid_at"] >= prev_start) & (pay["paid_at"] < prev_start + pd.Timedelta(days=30))]

curr_amt = curr.query("plan_type == 'paid' and is_trial == 0")["amount"].sum()
prev_amt = prev.query("plan_type == 'paid' and is_trial == 0")["amount"].sum()
change = (curr_amt - prev_amt) / max(prev_amt, 1)

print({"current": curr_amt, "previous": prev_amt, "change_rate": round(change, 4)})
print("trigger_action:", change <= -0.07)
```

The value of this code is not the calculation itself but the fact that the framing is codified. Who is included, what the period is, and what the action-trigger threshold is — all are visible.

### Framing Quality Checklist

- Did you distinguish whether the question is fact-checking or root-cause exploration?
- Did you define whether the metric is a single metric or composite?
- Is there a falsification condition (threshold, comparison period)?
- Did you define a fallback metric if data does not exist?
- Did you specify the decision-maker and meeting cadence for receiving results?

Structuring questions this way transforms the team from "a team that analyzes well" to "a team that makes decisions fast." Data science maturity shows not in code length but in the ability to convert problem statements into operational rules.

## Turning Analysis Design into a Repeatable Loop

To connect the concepts above to actual team operations, you need to go beyond analysis notes and build a repeatable experiment loop. Three things matter. First, feature-creation rules must live in both code and documentation simultaneously. Second, visualizations must serve as decision-trigger checks, not explanatory illustrations. Third, model evaluation must include behavioral impact, not just a single score line.

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

This example transforms raw tables into a user-level feature set aligned with the analysis goal. `log1p` mitigates distribution skew, and behavioral features like `weekend_ratio` often provide better explanatory power than simple totals.

### Checking Distributions and Segment Patterns with matplotlib

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

The purpose of visualization is not a pretty chart — it is finding anomalies fast. If the distribution skews heavily, consider a log transform. If the rolling mean shifts abruptly by segment, revisit the segmentation criteria. Each chart should map to a next action.

### Managing Preprocessing and Model Together with sklearn Pipeline

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

Pipelines ensure the training and inference paths are identical, improving reproducibility. This is one of the most reliable ways to eliminate "works in the notebook but fails in batch" problems.

### A/B Test Design Template

Experiment design matters as much as modeling. This template works for practical scenarios like marketing message optimization:

| Item | Design Example |
|---|---|
| Hypothesis | Changing the new-user onboarding message increases 7-day revisit rate |
| Population | Users who signed up in the last 14 days (excluding internal accounts) |
| Random assignment | 50:50 split by user_id hash |
| Primary metric | 7-day revisit rate |
| Guardrail metrics | Support ticket rate, payment failure rate |
| Duration | Minimum 2 weeks or until sample size reached |
| Stop condition | Guardrail metric degradation exceeds threshold |

The most common A/B testing mistake is confirming results too early. When you peek at intermediate results repeatedly, fixing the stop rule and analysis plan in a document before the experiment starts prevents mistaking random fluctuation for a real effect.

### Operational Checkpoints

- Record feature-creation rules in both code and documentation.
- For every EDA chart, write one line: "What decision will this chart trigger?"
- Evaluate model scores alongside cost, latency, and operational complexity.
- Fix hypothesis, sample size, and stop rules before starting an A/B test.
- End every results presentation with "What did we learn and what changes next week?"

### Connecting Pipeline Results to Experiment Assignment

This example shows the minimal flow from a scored feature set to actual experiment assignment. Teams that connect analysis to operations typically have transition code like this:

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

At this stage, rules matter more than scores. Fixing exclusion conditions, assignment rules, and experiment size upfront reduces interpretation conflicts after the experiment.

### Additional Verification Checklist

- Record the data extraction query version alongside feature-creation code version.
- Check model score distribution by quantile; review upper-segment bias.
- After experiment group assignment, always verify group balance (country, device, acquisition channel).
- Do not finalize intermediate metrics as decision evidence before experiment completion.

### Pre-Analysis Controls

Before sharing analysis results, running minimal controls stabilizes interpretation quality. Check three things: that the period boundary has not shifted, that missing-value handling rules are consistent across versions, and that experiment group assignment remained random.

```python
import pandas as pd

report = pd.read_csv('experiment_daily_report.csv')
checks = {
    'date_min': str(report['date'].min()),
    'date_max': str(report['date'].max()),
    'null_rate': float(report.isna().mean().mean()),
    'groups': report['bucket'].value_counts(normalize=True).to_dict(),
}
print(checks)
```

This record is not flashy, but it is the most practical safeguard for guaranteeing "we looked at it using the same criteria" in the next iteration.

## Practice Problems

1. Frame *"churn is up"* using the 5-step process.
2. Write 3 *unfalsifiable* hypotheses, then rewrite each to be *falsifiable*.
3. Pick one metric and show how *different windows* change the conclusion.

## Wrap-up and Next Steps

Only *answerable questions* are the start of analysis. Next, we will look at *how to collect* the data behind those questions.

## Answering the Opening Questions

- **Why is a question like "Why did revenue drop?" hard to answer as-is?**
  - As-is, it's missing `metric`, `window`, and `population` — so different teams write completely different queries for the same question. The moment we rewrote it as "Paid-subscriber monthly revenue dropped more than 5% in the last 30 days versus the prior 30 days," what to aggregate finally became fixed.
- **Why are metric, time window, and target population the core of problem definition?**
  - When all three axes are set — like `monthly_revenue`, `last 30 days vs previous 30 days`, `paid subscribers (excluding trials)` — the comparison baseline stops shifting. Without them, the same revenue-drop question yields entirely different conclusions depending on whether free users are included or whether you compare weekly vs. monthly.
- **What form must a question take for data to answer it?**
  - A question data can answer must be a single measurable, falsifiable sentence with metric, time window, and target population specified — something you can actually verify as true or false with `pd.read_csv("revenue_data.csv")` or a SQL aggregate.
<!-- toc:begin -->
## In this series

- [Data Science 101 (1/10): What Is Data Science?](./01-what-is-data-science.md)
- **Turning a Problem into a Data Problem (current)**
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

- [Google — Rules of Machine Learning (Rule #1)](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Cassie Kozyrkov — How to Ask Smart Questions](https://kozyrkov.medium.com/)
- [Stitch Fix — A/B Testing Lessons](https://multithreaded.stitchfix.com/)
- [Andrew Gelman — Statistical Modeling Blog](https://statmodeling.stat.columbia.edu/)

Tags: DataScience, ProblemFraming, Metrics, Workflow, Beginner

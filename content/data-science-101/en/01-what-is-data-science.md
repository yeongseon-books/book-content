---
series: data-science-101
episode: 1
title: What Is Data Science?
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

# What Is Data Science?

People usually enter data science through tools. They install pandas, copy a scikit-learn tutorial, and learn a dashboard product. A few weeks later, the vocabulary gets blurry. Analytics, experimentation, forecasting, ML engineering, and BI all sound adjacent, but not identical.

That confusion matters because the field only starts to make sense when you see the job as a decision pipeline rather than a pile of techniques. If you cannot explain how a question becomes data, how data becomes evidence, and how evidence changes an action, every later chapter feels like isolated syntax.

This is the first post in the Data Science 101 series. Here we build the mental model for the rest of the series: data science is the work of turning a fuzzy business question into a repeatable decision loop.

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

## Concept at a Glance

![The core data science loop from problem framing to data, insight, and decision](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/01/01-01-concept-at-a-glance.en.png)

*The core data science loop from problem framing to data, insight, and decision*
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

### Step 3 — Clean and EDA

```python
df = df.dropna(subset=["last_login"])
df["days_since_login"] = (
    pd.Timestamp.today() - pd.to_datetime(df["last_login"])
).dt.days
print(df["days_since_login"].describe())
```

### Step 4 — Model or rule

```python
candidates = (
    df[df["days_since_login"] > 30]
      .sort_values("amount_total", ascending=False)
      .head(100)
)
```

### Step 5 — Tie back to a decision

```text
Email campaign for 100 users → measure conversion → adjust next week
```

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

Startup data teams often look like a *mini-org* of analyst + scientist + engineer. They run on *topic-level OKRs*, and every week they tie *dashboards or models* back to *concrete decisions*.

## How a Senior Engineer Thinks

- *Problem framing* is more expensive than *modeling*.
- Never *skimp on EDA*.
- Always *close the loop* with a decision.
- *Document* the boundaries between roles.
- *Data quality* is everyone's job, not just the engineer's.

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

Data science is the *job of bridging* problems and data. Next, we will see how to *turn a problem* into a *data problem* you can actually work on.

<!-- toc:begin -->
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

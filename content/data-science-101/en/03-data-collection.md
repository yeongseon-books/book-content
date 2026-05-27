---
series: data-science-101
episode: 3
title: "Data Science 101 (3/10): Data Collection"
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
  - DataCollection
  - API
  - Database
  - Beginner
seo_description: Four common paths for collecting data — files, APIs, databases, and event logs — plus the provenance habits that keep analyses reproducible
last_reviewed: '2026-05-15'
---

# Data Science 101 (3/10): Data Collection

The easiest way to lose trust in an analysis is to lose the origin story of the data. A CSV arrives in Slack, an API export gets copied into a notebook, or someone hand-edits an Excel file “just for now.” Weeks later the team still has charts, but nobody can explain where the rows came from or whether the result is reproducible.

Collection is where reliability starts. Before cleaning or modeling ever matter, someone has to decide which source is authoritative, which copy is disposable, and what metadata must be recorded so the same dataset can be reconstructed later.

This is the 3rd post in the Data Science 101 series. Here we treat collection as an engineering discipline: source selection, provenance, and repeatability come first, and the code that fetches the rows comes second.


![data science 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/03/03-01-concept-at-a-glance.en.png)
*data science 101 chapter 3 flow overview*
> At its core, Data Collection is about deciding what enters a system, where validation happens, and which signals stay for the next cycle—not about feature names.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Data Collection?
- Which signal should the example or diagram make visible for Data Collection?
- What failure should be prevented first when Data Collection reaches a real system?

## Questions This Post Answers

- Which collection paths are most common in analytics and ML projects?
- Why should original sources, copies, and snapshots be treated differently?
- What provenance metadata makes a dataset reproducible later?
- How do collection mistakes leak all the way into the final report?

> Collection is not just retrieval; it is the first reproducibility checkpoint in the project.

## What You Will Learn

- Four common *data sources*: files, APIs, databases, event logs
- The difference between *original*, *copy*, and *snapshot*
- The role of a *data dictionary*
- A 5-step collection exercise
- Five common pitfalls

## Why It Matters

A missing record at the *collection step* haunts you all the way to the final report. The small habit of *writing down the source* is what gives you *reproducibility*.

> *Only *traceable* data is *trustworthy* data.*

The key boundary in this episode is between the concept itself and how it operates in a real system. You need to know where the data comes in, where the decision happens, and what signal must be recorded.

## Key Terms

- **Source of truth**: the *authoritative origin* of the data.
- **Snapshot**: a *frozen copy* taken at a specific moment.
- **Schema**: the *shape and types* of the data.
- **Data dictionary**: a *table that documents* what each column means.
- **Provenance**: the data's *origin and history*.

## Before / After

**Before**: a teammate sends an *Excel file*. You don't know *when* it was pulled or *where* it came from.

**After**: you pull the same data with *SQL from the warehouse*, recording the *hash and timestamp*. You can *reproduce* the analysis months later.

## Hands-on: 5-step Collection

### Step 1 — From a file

```python
import pandas as pd
df = pd.read_csv("data/users-2026-05-04.csv")
print(df.shape)
```

### Step 2 — From an API

```python
import requests
resp = requests.get("https://api.example.com/users", timeout=10)
resp.raise_for_status()
users = resp.json()
```

### Step 3 — From a database

```python
from sqlalchemy import create_engine
engine = create_engine("postgresql://user:pass@host/db")
df = pd.read_sql(
    "SELECT id, signup_at FROM users WHERE signup_at > '2026-01-01'",
    engine,
)
```

### Step 4 — From an event log

```python
# JSONL — one JSON event per line
import json
with open("events.jsonl") as f:
    events = [json.loads(line) for line in f]
```

### Step 5 — Record provenance

```python
import hashlib
import datetime

meta = {
    "source": "postgres://prod-replica/users",
    "fetched_at": datetime.datetime.utcnow().isoformat(),
    "row_count": len(df),
    "sha256": hashlib.sha256(
        pd.util.hash_pandas_object(df).values.tobytes()
    ).hexdigest()[:16],
}
print(meta)
```

**Expected output:** one provenance record containing `source`, `fetched_at`, `row_count`, and `sha256` for the pulled dataset.

## What to Notice in This Code

- Always record the *source and timestamp* together.
- A *hash* is a cheap way to detect *whether the data changed*.
- *Never modify originals* — make all changes downstream in *staging*.

## Five Common Mistakes

1. **Overwriting the *original* in Excel.** No way to roll back.
2. **Ignoring API *rate limits*.** You will get throttled or blocked.
3. **Not documenting the *schema*.** Column meaning evaporates.
4. **Not tracking *log format changes*.** Analyses *silently break*.
5. **Storing *sensitive data* on a personal laptop.** Security incident waiting to happen.

## How This Shows Up in Production

Data teams run collection scripts in *Airflow / dbt*. Every load adds *load_id, fetched_at, source* columns. The *data dictionary* lives in *Notion or Confluence* and updates with every PR.

## How a Senior Engineer Thinks

- Never modify the *original*.
- Record *source, timestamp, hash* by reflex.
- Catch *schema changes* with *alerts*.
- Mask *sensitive data* before analysis.
- The *data dictionary* is your best documentation.

## Checklist

- [ ] I know the four common *sources*.
- [ ] I understand what a *snapshot* is.
- [ ] I can write a *data dictionary*.
- [ ] I record *provenance* by default.

## Practice Problems

1. Pick a *public API*, collect a small sample, and write the *metadata*.
2. Sketch the *original → staging → analysis* flow as a diagram.
3. Document a *case where a schema changed* and how it affected analyses.

## Wrap-up and Next Steps

Collection is the *recording step*. Next, we will look at how to *clean* the data we have collected.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Data Collection?**
  - The article treats Data Collection as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Data Collection?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Data Collection reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Science 101 (1/10): What Is Data Science?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): Turning a Problem into a Data Problem](./02-problem-to-data-problem.md)
- **Data Collection (current)**
- Data Cleaning (upcoming)
- Exploratory Data Analysis (upcoming)
- Visualization (upcoming)
- Modeling (upcoming)
- Evaluation (upcoming)
- Result Interpretation (upcoming)
- End-to-End Data Project Flow (upcoming)

<!-- toc:end -->

## References

- [requests — Quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [pandas — IO Tools](https://pandas.pydata.org/docs/user_guide/io.html)
- [Airflow — Concepts](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html)
- [Google — Data Validation for Machine Learning](https://research.google/pubs/data-validation-for-machine-learning/)

Tags: DataScience, DataCollection, API, Database, Beginner

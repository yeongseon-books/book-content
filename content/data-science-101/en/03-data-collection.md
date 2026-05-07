---
series: data-science-101
episode: 3
title: Data Collection
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
  - DataCollection
  - API
  - Database
  - Beginner
seo_description: Four common paths for collecting data — files, APIs, databases, and event logs — plus the provenance habits that keep analyses reproducible
last_reviewed: '2026-05-04'
---

# Data Collection

> Data Science 101 series (3/10)

<!-- a-grade-intro:begin -->

**Core question**: *Where* and *how* do you actually collect the data your analysis needs — and how do you tell the *original* from a *copy*?

> *Every analysis starts by writing down *where the data came from*.*

<!-- a-grade-intro:end -->

## What You Will Learn

- Four common *data sources*: files, APIs, databases, event logs
- The difference between *original*, *copy*, and *snapshot*
- The role of a *data dictionary*
- A 5-step collection exercise
- Five common pitfalls

## Why It Matters

A missing record at the *collection step* haunts you all the way to the final report. The small habit of *writing down the source* is what gives you *reproducibility*.

> *Only *traceable* data is *trustworthy* data.*

## Concept at a Glance

```mermaid
flowchart LR
    File["File / CSV"] --> Stage["Staging"]
    API["API"] --> Stage
    DB["Database"] --> Stage
    Log["Event Log"] --> Stage
    Stage --> Analysis["Analysis"]
```

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

<!-- toc:begin -->
- [What Is Data Science?](./01-what-is-data-science.md)
- [Turning a Problem into a Data Problem](./02-problem-to-data-problem.md)
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

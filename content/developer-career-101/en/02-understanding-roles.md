---
series: developer-career-101
episode: 2
title: "Developer Career 101 (2/10): Understanding Roles"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
- Career
- Roles
- Frontend
- Backend
- Beginner
seo_description: A beginner-friendly tour comparing frontend, backend, data, SRE,
  and ML developer roles.
last_reviewed: '2026-05-14'
---

# Developer Career 101 (2/10): Understanding Roles

Saying "I want to be a developer" is still too broad to guide real decisions. Frontend, backend, data, SRE, ML, and mobile roles all ship software, but they optimize for different outcomes, carry different failure modes, and measure success with different signals.

This is the 2nd post in the Developer Career 101 series.


![developer career 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/developer-career-101/02/02-01-concept-at-a-glance.en.png)
*developer career 101 chapter 2 flow overview*
> The key to understanding roles is recognizing that the same title can mean different scope, responsibility, and tooling across companies and teams.

## Questions to Keep in Mind

- What actually differs across frontend, backend, data, SRE, ML, and mobile roles?
- Why do responsibilities, tools, and metrics diverge so sharply under the same "developer" label?
- How can you tell whether your current role fits you or whether a transition is worth exploring?

## What You Will Learn

- Six common roles
- Per-role *responsibilities*
- Per-role *tools*
- Per-role *metrics*
- What to weigh when *switching*

## Why It Matters

A bad role fit shortens the path to burnout. Conversely, understanding the differences in responsibility, tools, and metrics lets you either excel in your current role or move strategically when a transition is needed.

> A good role choice starts not with which tools you use, but with which responsibilities you are willing to own.

## The Big Picture

The first criterion that separates roles is responsibility, not tools. Tools change, but what you optimize for and which failures you own first define the character of a role for the long term.

## Key Terms

- **frontend**: Owns user experience.
- **backend**: Owns system logic and data flow.
- **SRE**: Owns operational reliability.
- **data**: Owns analytics and pipelines.
- **ML**: Owns model-driven prediction quality.

## Before/After

**Before**: "Roles look more or less alike."

**After**: "Responsibilities and tools differ completely."

## Hands-on: Compare the Roles

### Step 1 — Frontend

```text
responsibility: UX
tools: React, CSS
metrics: LCP, INP
```

Frontend handles the speed and flow that users perceive directly. Even identical features feel broken when perceived performance and interaction quality are poor.

### Step 2 — Backend

```text
responsibility: data flow
tools: Python, SQL
metrics: p95, error rate
```

Backend is the foundation that makes features actually run. Response time, error rate, and data consistency are the operational metrics that make the role clear.

### Step 3 — Data

```text
responsibility: pipelines
tools: Airflow, dbt
metrics: freshness, accuracy
```

Data roles care less about storing data and more about making it flow reliably. Whether for analysis or model training, if input quality is shaky everything downstream breaks.

### Step 4 — SRE

```text
responsibility: operations
tools: Prometheus, K8s
metrics: SLO, MTTR
```

SRE is less about preventing incidents entirely and more about defining team-level standards for handling them. Reliability sense and operational automation are core.

### Step 5 — ML

```text
responsibility: model quality
tools: PyTorch, MLflow
metrics: AUC, latency
```

ML is not just about model accuracy. Prediction quality, latency, data quality, reproducibility, and deployment operations must all be handled together for a model to mean anything in production.

## Decision Frame for Comparing Roles

| Lens | Frontend | Backend | Data / SRE / ML |
| --- | --- | --- | --- |
| Frequent failure mode | Slow or broken user flow | Error rate, data integrity, service instability | Stale data, incident load, weak model quality |
| What success feels like | Users move with less friction | Systems stay predictable under change | Reliability, freshness, or model quality improves measurably |
| Evidence to inspect early | Performance metrics, design collaboration | API contracts, storage boundaries, production metrics | Pipeline shape, on-call expectations, reproducibility tooling |
| Fit question | Do you enjoy polishing interaction details? | Do you enjoy data flow and edge cases? | Do you like operating with metrics and explicit risk? |

## Role Comparison Table

Comparing major developer roles by core skills, market demand, and entry difficulty helps you see your aptitude and market reality side by side.

| Role | Core skills | Market demand | Entry difficulty |
| --- | --- | --- | --- |
| Frontend | React, TypeScript, CSS, build tools | High | Medium (low learning barrier) |
| Backend | Python/Java, SQL, REST API, testing | Very high | Medium (many language options) |
| Full-stack | Frontend + Backend combined | Medium (startup preference) | High (broad scope) |
| DevOps/SRE | Kubernetes, Terraform, monitoring | High | High (needs ops experience) |
| Data Engineer | Airflow, dbt, SQL, Spark | Medium | Medium (needs stats basics) |
| ML Engineer | PyTorch, MLflow, model deployment | Medium (growing) | High (math + code) |

Frontend and backend have the highest market demand and the richest learning resources. Full-stack offers broad experience but risks being seen as shallow. DevOps and ML have high entry difficulty, but solid fundamentals keep you competitive for a long time.

## T-Shaped Competency

A T-shaped engineer goes deep in one area (the vertical bar) while understanding adjacent areas broadly (the horizontal bar). For example, someone who knows backend deeply while also understanding frontend and data pipeline terminology.

### Vertical: Depth

Being able to handle edge cases, performance bottlenecks, and operational issues in one domain.

```python
# Backend depth example: connection pool tuning
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# When p95 response time is slow, adjust pool size and overflow limits.
```

### Horizontal: Breadth

Understanding other roles' terminology and priorities so you can align quickly during collaboration.

- Understand what frontend means by LCP and INP, and collaborate by reducing API response size.
- Provide the denormalized log format that the data team requests.

Without depth you cannot solve problems end-to-end; without breadth collaboration slows down. A T-shaped profile survives changing tech stacks.

## Role Transition Strategy

Switching roles takes more time than learning a new language because responsibilities and metrics change.

### Phase 1 — Validate in Your Current Role

If you want to move from backend to data engineering, first build a small Airflow pipeline at your current company.

```python
# Backend → Data Engineer transition example
# Phase 1: Build a small data pipeline at your current company
from airflow import DAG
from airflow.operators.python import PythonOperator

def extract_orders():
    # Extract order data
    pass

dag = DAG("daily_orders", schedule="@daily")
task = PythonOperator(task_id="extract", python_callable=extract_orders, dag=dag)
```

### Phase 2 — Three-Month Project

Complete one project you can put on a resume. A side project or internal company work is sufficient.

```markdown
## Project: Daily Order Data Pipeline

- Goal: Extract order data daily and load into the data warehouse
- Duration: 3 months
- Result: Fresh data available every morning at 9 AM
```

### Phase 3 — Internal Transfer or External Move

If your company supports internal mobility, try that first. Otherwise, proceed with an external move once your portfolio is ready.

Transitions can take six months to a year. Do not rush—build evidence in your current role first.

## Tech Stack Selection Decision Table

Choosing a role based solely on a framework's popularity often forces a course correction one or two years later. Tech stacks should be compared not just on trendiness but on problem fit, team operability, and learning curve.

| Criterion | Question | Good signal | Warning signal |
| --- | --- | --- | --- |
| Problem fit | Is this stack directly relevant to the problem at hand? | Requirements and capabilities clearly match | Just "popular right now" |
| Team operability | Does the team have review and operational experience? | Internal references and on-call experience exist | Only one person understands the structure |
| Learning curve | Can you ship production code within 3 months? | Docs, examples, and mentors are sufficient | Intro material is scarce |
| Market viability | Does sustained demand appear in job postings? | Recurring across multiple industries | Used at only one specific company |
| Long-term maintenance | Is replacement cost manageable in 2 years? | Standard ecosystem, stable versioning | Risk of abandoned updates |

The purpose of this table is not to find a perfect answer but to leave clear decision rationale. The harder the stack choice, the more important it is to record "why this choice was made" in writing—so your future self can revise the decision more easily.

## How to Read Market Demand

Market demand analysis is not just counting job postings. You need to look at three dimensions together:

- Posting density: how frequently a tech keyword repeats
- Role depth: whether they want simple usage experience or architecture-level ops capability
- Domain spread: whether demand is locked to one industry or expanding across many

For example, "Python" has high posting volume and wide domain spread (backend, data, automation). Meanwhile, certain tools may have high posting counts but only for maintenance-focused demand. Never judge on a single metric—read the responsibility scope within the posting text.

## Role Transition Simulation

| Current role | Transition target | 90-day prep items | Risk mitigation |
| --- | --- | --- | --- |
| Frontend | Backend | API design, SQL, auth basics | Small internal API contribution |
| Backend | Data | ETL, modeling, quality validation | Weekly report automation |
| Data | ML Engineer | Experiment tracking, deployment pipeline | Mini model service |

The key to transitions is not "move after being perfectly prepared" but bringing small responsibilities from the target role into your current role. This process simultaneously validates actual fit and builds resume evidence.

## Job Posting Fit Matrix

When choosing a role, data beats gut feeling. Even within the same "backend" position, required system complexity, collaboration style, and incident response intensity vary widely. The matrix below is a minimum baseline for comparing three postings.

| Evaluation axis | Question | 1-point benchmark | 3-point benchmark | 5-point benchmark |
| --- | --- | --- | --- | --- |
| Problem difficulty | What kind of problems are solved? | CRUD-centric | API + batch mix | Distributed systems / performance optimization |
| Operational responsibility | On-call/incident scope? | None | Monthly rotation | Weekly rotation + mandatory RCA |
| Collaboration density | Cross-function collaboration frequency? | Request-based | Weekly alignment meetings | Daily sync + documented decisions |
| Growth path | Role expansion in 1 year? | Same work repeated | Partial lead experience | Service ownership granted |

After scoring with this matrix, apply different weights per target role. If you are targeting data engineering, weight data modeling higher than operational responsibility. If targeting frontend, weight collaboration density and product experiment speed. Even with the same table, weight settings should reflect your goal.

## Role Transition Roadmap Timeline

A transition does not end with a single decision. You must build evidence for the new role gradually while maintaining trust in your current role.

| Period | Action items | Deliverable | Align with manager on |
| --- | --- | --- | --- |
| Months 1–2 | Participate in adjacent tasks on current team | 1 data pipeline assist task | Allow 20 % work time for transition learning |
| Months 3–4 | Lead a small initiative | Ops doc + dashboard build | Separate evaluation metrics from current role |
| Months 5–6 | Propose formal role adjustment | Draft job description, competency table | Include transition item in next-half goals |

What matters in this process is not "I did new work" but evidence that "I produced repeatable results in the new role." Therefore project outcomes must be captured in numbers. For instance, "batch failure rate 12 % → 3 %" makes the transition conversation far more concrete.

## What to Notice in This Code

- Responsibility defines the role.
- Metrics define the culture.
- Tools are just tools.

## Five Common Mistakes

1. **Choosing role by tool.**
2. **Not knowing the metrics.**
3. **Crossing role boundaries impulsively.**
4. **Switching on a whim.**
5. **Ignoring the domain.**

## How This Shows Up in Production

Companies recommend roughly six months of onboarding when switching roles because the tools are only part of the change—responsibility and judgment criteria shift entirely.

## How a Senior Engineer Thinks

- A role is a responsibility.
- Metrics are a language.
- Switch strategically.
- Domain is depth.
- Boundaries enable collaboration.

## Checklist

- [ ] Three metrics for current role.
- [ ] Responsibilities of target role written.
- [ ] Learning plan for switch.

## Practice Problems

1. One line: define p95.
2. One line: define SLO.
3. One line: meaning of frontend LCP.

## Wrap-up and Next Steps

Understanding roles means not memorizing names but distinguishing the problems each role owns and how success is measured. Looking at which responsibilities you want to hold long-term—rather than what you want to build—makes the choice much clearer. The next post covers how to build a sustainable learning plan even within a busy schedule.

## Answering the Opening Questions

- **What actually differs between frontend, backend, data, SRE, ML, and mobile roles?**
  - Each role handles different types of problems, uses different tools, and measures success by different metrics. Frontend prioritizes UI and performance, backend prioritizes features and reliability, data prioritizes accuracy and usability.
- **Why do responsibilities, tools, and metrics differ completely under the same "developer" title?**
  - The title may be the same but problem size, responsibility scope, and required communication styles differ. Explicitly understanding this clarifies your own strengths and weaknesses.
- **How can you judge whether your current role fits you or whether you should consider a transition?**
  - Define success metrics for your current role, distinguish what you do well from what's difficult, then use those criteria to decide transition timing and learning plans.
<!-- toc:begin -->
## In this series

- [Developer Career 101 (1/10): What Is a Developer Career](./01-what-is-developer-career.md)
- **Understanding Roles (current)**
- Building a Learning Plan (upcoming)
- Resume and Portfolio (upcoming)
- Preparing for Coding Interviews (upcoming)
- System Design Interviews (upcoming)
- Settling into the First Job (upcoming)
- Side Projects and Learning (upcoming)
- Mentoring and Networking (upcoming)
- The Path to Senior (upcoming)

<!-- toc:end -->

## References

- [web.dev — Web Vitals](https://web.dev/vitals/)
- [Google SRE Book](https://sre.google/books/)
- [MLOps Community](https://mlops.community/)
- [roadmap.sh — Developer roadmaps](https://roadmap.sh/)

Tags: Career, Roles, Frontend, Backend, Beginner

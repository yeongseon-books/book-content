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

A bad role fit shortens the path to burnout.

Each technical role prioritizes different problems: frontend focuses on user experience, backend on stability and scale, data on accuracy and activation.

## Key Terms

- **frontend**: User experience.
- **backend**: System logic.
- **SRE**: Operational reliability.
- **data**: Analytics and pipelines.
- **ML**: Model-driven prediction.

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

### Step 2 — Backend

```text
responsibility: data flow
tools: Python, SQL
metrics: p95, error rate
```

### Step 3 — Data

```text
responsibility: pipelines
tools: Airflow, dbt
metrics: freshness, accuracy
```

### Step 4 — SRE

```text
responsibility: operations
tools: Prometheus, K8s
metrics: SLO, MTTR
```

### Step 5 — ML

```text
responsibility: model quality
tools: PyTorch, MLflow
metrics: AUC, latency
```

## Decision frame for comparing roles

| Lens | Frontend | Backend | Data / SRE / ML |
| --- | --- | --- | --- |
| Frequent failure mode | Slow or broken user flow | Error rate, data integrity, service instability | Stale data, incident load, weak model quality |
| What success feels like | Users move with less friction | Systems stay predictable under change | Reliability, freshness, or model quality improves measurably |
| Evidence to inspect early | Performance metrics, design collaboration | API contracts, storage boundaries, production metrics | Pipeline shape, on-call expectations, reproducibility tooling |
| Fit question | Do you enjoy polishing interaction details? | Do you enjoy data flow and edge cases? | Do you like operating with metrics and explicit risk? |

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

Companies recommend roughly six months of onboarding when switching roles.

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

Next post covers *Building a Learning Plan*.

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

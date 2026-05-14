---
series: sre-101
episode: 8
title: Reducing Toil
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - SRE
  - Toil
  - Automation
  - Productivity
  - Operations
seo_description: A beginner-friendly guide to reducing toil covering definitions, measurement, automation priorities, savings strategies, and tech-debt connections
last_reviewed: '2026-05-04'
---

# Reducing Toil

This is post 8 in the SRE 101 series.

> SRE 101 series (8/10)

<!-- a-grade-intro:begin -->

**Core question**: How much of the *team's time* is being *eaten by repetitive work*?

> *Toil* is *manual labor* that *automation* can *remove*.

<!-- a-grade-intro:end -->

## What You Will Learn

- The *definition* of *toil*
- How to *measure* it
- How to *prioritize automation*
- *Savings* strategies
- The relation to *technical debt*

## Why It Matters

When *toil* exceeds *50%*, *improvement stops*.

## Concept at a Glance

```mermaid
flowchart LR
    Manual["manual"] --> Toil["toil"]
    Toil --> Automate["automate"]
    Automate --> Saved["time saved"]
```

## Key Terms

- **toil**: *repetitive, automatable* work.
- **runbook**: a *manual procedure* document.
- **automation**: *code* that does the work.
- **toil ratio**: the *fraction of time* spent on toil.
- **break-even**: when *automation* pays *back* its build cost.

## Before/After

**Before**: every *night call* requires *manual recovery*.

**After**: a *recovery script* handles it *automatically*.

## Hands-on: Measure and Automate Toil

### Step 1 — Log toil time

```python
def log_toil(task, minutes):
    return {"task": task, "minutes": minutes}
```

### Step 2 — Toil ratio

```python
def toil_ratio(toil_min, total_min):
    return toil_min / total_min
```

### Step 3 — Score automation candidates

```python
def score(freq_per_week, minutes_each):
    return freq_per_week * minutes_each
```

### Step 4 — Break-even

```python
def break_even(saved_per_week, build_minutes):
    return build_minutes / saved_per_week
```

### Step 5 — Write the automation

```python
def auto_restart(service):
    return f"systemctl restart {service}"
```

## What to Notice in This Code

- *Measurement* is the start of *prioritization*.
- A *score* sorts the *candidates*.
- *Break-even* drives the *invest-or-not* call.

## Five Common Mistakes

1. **No *measurement* of toil.**
2. **Automating by *gut feel* without a *score*.**
3. **Stacking *runbooks* without turning them into *code*.**
4. **Letting *automation debt* pile up.**
5. **Ignoring the *post-launch* operational cost of automation.**

## How This Shows Up in Production

*Recovery automation* turns *MTTR* from tens of minutes into *single minutes*.

## How a Senior Engineer Thinks

- *Toil* is *debt*.
- *Automation* lives on top of *repetition*.
- *50%* is the *line* in the sand.
- Without *measurement*, no *priority*.
- *Automation* needs *maintenance*, too.

## Checklist

- [ ] *Toil ratio* measured.
- [ ] *Candidate list*.
- [ ] *Break-even* calculated.
- [ ] *Automation owner*.

## Practice Problems

1. Define *toil* in one line.
2. Define *runbook* in one line.
3. Define *break-even* in one line.

## Wrap-up and Next Steps

Next, we cover *capacity planning*.

<!-- toc:begin -->
- [What is SRE?](./01-what-is-sre.md)
- [Reliability](./02-reliability.md)
- [SLI, SLO, SLA](./03-sli-slo-sla.md)
- [Error Budget](./04-error-budget.md)
- [Monitoring](./05-monitoring.md)
- [Incident Response](./06-incident-response.md)
- [Postmortem](./07-postmortem.md)
- **Reducing Toil (current)**
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)
<!-- toc:end -->

## References

- [Eliminating Toil - Google SRE Book](https://sre.google/sre-book/eliminating-toil/)
- [Identifying and Tracking Toil - Google SRE Workbook](https://sre.google/workbook/eliminating-toil/)
- [Automating Operations - Google SRE Book](https://sre.google/sre-book/automation-at-google/)
- [Toil Reduction - Atlassian](https://www.atlassian.com/incident-management/devops/toil)

Tags: SRE, Toil, Automation, Productivity, Operations

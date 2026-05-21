---
series: sre-101
episode: 8
title: "SRE 101 (8/10): Reducing Toil"
status: content-ready
targets:
  tistory: false
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
last_reviewed: '2026-05-14'
---

# SRE 101 (8/10): Reducing Toil

Teams can be very busy and still spend too much of their time on work that should not stay manual. The danger is that repetitive recovery, repeated validation, and copied communication all start to look normal simply because the service still runs.

Toil matters because it quietly taxes improvement. The more time a team spends repeating automatable work, the less room it has for safer releases, better observability, and structural fixes.

This is post 8 in the SRE 101 series. Here we define toil in operational terms, measure its cost, rank automation candidates, and decide where automation actually pays back.


![sre 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/08/08-01-concept-at-a-glance.en.png)
*sre 101 chapter 8 flow overview*

## Questions to Keep in Mind

- What separates toil from valuable operational work that still takes time?
- How can a team measure how much capacity is disappearing into repetitive work?
- Which automation candidates should move first if time is limited?

## Why this topic matters

When toil becomes a large share of the week, improvement stops. The team is still working hard, but more of that effort goes into keeping the current system upright rather than making the next week better.

Reducing toil is therefore not just a productivity topic. It is a reliability topic because it decides how much engineering time remains for prevention work.

> Toil is manual labor that automation can remove.

## Concept at a glance

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

## Answering the Opening Questions

- **What separates toil from valuable operational work that still takes time?**
  - The article treats Reducing Toil as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How can a team measure how much capacity is disappearing into repetitive work?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Which automation candidates should move first if time is limited?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- [SRE 101 (5/10): Monitoring](./05-monitoring.md)
- [SRE 101 (6/10): Incident Response](./06-incident-response.md)
- [SRE 101 (7/10): Postmortem](./07-postmortem.md)
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

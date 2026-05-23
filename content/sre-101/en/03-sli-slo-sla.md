---
series: sre-101
episode: 3
title: "SRE 101 (3/10): SLI, SLO, SLA"
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
  - SLI
  - SLO
  - SLA
  - Reliability
seo_description: A beginner-friendly guide to SLI, SLO, and SLA covering their definitions, the agreement process, and what makes a good objective
last_reviewed: '2026-05-14'
---

# SRE 101 (3/10): SLI, SLO, SLA

The moment a reliability conversation becomes serious, three acronyms show up: SLI, SLO, and SLA. Because they all involve numbers, teams often compress them into one vague statement like “we promise 99.9%,” which is exactly where confusion starts.

What matters operationally is the separation. You need one layer that defines what you measure, another that defines the target you run the system against, and a final layer that defines what you are willing to promise outside the team.

This is post 3 in the SRE 101 series. Here we separate measurement, internal objective, and external agreement so later error-budget and alerting decisions have a clean contract underneath them.


![sre 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/03/03-01-concept-at-a-glance.en.png)
*sre 101 chapter 3 flow overview*

## Questions to Keep in Mind

- Where exactly is the line between an indicator, an objective, and an external agreement?
- Why should internal targets and customer-facing promises almost never be the same document?
- What information makes an SLO operational instead of decorative?

## Why this topic matters

If you mix the three terms, every decision gets wobbly. Operations may think the team is talking about an internal goal while sales repeats the same number as a public promise.

Separating them makes ownership and consequences clearer. The indicator tells you what changed, the objective tells you when to act, and the agreement tells you what happens if you miss the promise.

> SLI is the indicator, SLO is the internal goal, and SLA is the external promise.

## Key Terms

- **SLI**: a *service-level indicator*.
- **SLO**: a *service-level objective*.
- **SLA**: a *service-level agreement*.
- **window**: the *measurement period*.
- **threshold**: the *allowed limit*.

## Before/After

**Before**: someone says "*99.9%* is the *target*".

**After**: a written spec — *which indicator*, *over what window*, *with what consequence*.

## Hands-on: Writing the Spec

### Step 1 — Define the SLI

```python
sli = {
    "name": "http_success_ratio",
    "formula": "http_2xx / http_total",
    "source": "ingress logs",
}
```

### Step 2 — Define the SLO

```python
slo = {
    "sli": sli["name"],
    "target": 0.999,
    "window_days": 30,
    "owner": "payments-team",
}
```

### Step 3 — Define the SLA

```python
sla = {
    "slo": slo,
    "remedy": "service credit 10%",
    "exclusions": ["scheduled maintenance"],
}
```

### Step 4 — Detect a violation

```python
def violated(success, total, target):
    return (success / total) < target
```

### Step 5 — Report

```python
def report(success, total, target):
    return {
        "value": success / total,
        "violated": (success / total) < target,
    }
```

### Step 6 — Calculate the remaining budget in the same report

```python
def budget_summary(success, total, target):
    errors = total - success
    allowed = (1 - target) * total
    remaining = allowed - errors
    return {
        "availability": success / total,
        "allowed_errors": allowed,
        "remaining_errors": remaining,
    }
```

This is where the three layers start to feel operational. The SLI value tells you what happened, the SLO target tells you whether the result is acceptable, and the remaining-error view tells the team how much room is left before release policy should tighten.

### Step 7 — Resolve metric disputes before they turn into policy disputes

When two dashboards disagree, do not start by arguing about the target. Start by checking whether both dashboards use the same traffic boundary, the same success definition, and the same time window. Many “SLO debates” are really data-source debates in disguise.

| First check | Why it matters |
| --- | --- |
| Are both teams looking at the same request population? | Edge traffic and app-only traffic often produce different availability numbers. |
| Is a redirect or client error counted as success or failure? | The formula can drift even when the chart title stays the same. |
| Is the window rolling 30 days or calendar month? | The same percentage can mean different risk depending on the window. |
| Is maintenance excluded in one report but not the other? | Agreement language often differs from internal measurement language. |

## What to Notice in This Code

- The *SLI* names its *data source*.
- The *SLO* names its *owner*.
- The *SLA* records *exclusions* and *remedies*.

## Five Common Mistakes

1. **Treating *SLOs* like *SLAs* — over-promising.**
2. **An *SLI* with an *unclear data source*.**
3. **Forgetting the *measurement window*.**
4. **An *SLO* without an *owner*.**
5. **Calling something an *SLA* with *no remedy*.**

## How This Shows Up in Production

In *B2B contracts* the *SLA* becomes a legal *document*; *internally*, the *SLO* is the *yardstick*.

## How a Senior Engineer Thinks

- The *indicator* lives at the *customer's* level.
- The *objective* must be *realistic* to be *useful*.
- The *agreement* is reviewed with *legal*.
- If you cannot *measure*, it is not a *target*.
- An *SLO* without an *owner* does not exist.

## Checklist

- [ ] *SLI* spec.
- [ ] Named *SLO* owner.
- [ ] *SLA* remedy policy.
- [ ] *Exclusions* documented.

## Practice Problems

1. Define *SLI* in one line.
2. Define *SLO* in one line.
3. Define *SLA* in one line.

## Wrap-up and Next Steps

Next, we cover the *error budget*.

## Answering the Opening Questions

- **Where exactly is the line between an indicator, an objective, and an external agreement?**
  - The article treats SLI, SLO, SLA as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why should internal targets and customer-facing promises almost never be the same document?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What information makes an SLO operational instead of decorative?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- **SLI, SLO, SLA (current)**
- Error Budget (upcoming)
- Monitoring (upcoming)
- Incident Response (upcoming)
- Postmortem (upcoming)
- Reducing Toil (upcoming)
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)

<!-- toc:end -->

## References

- [Service Level Objectives - Google SRE Book](https://sre.google/sre-book/service-level-objectives/)
- [Implementing SLOs - Google SRE Workbook](https://sre.google/workbook/implementing-slos/)
- [SLI vs SLO vs SLA - Atlassian](https://www.atlassian.com/incident-management/kpis/sla-vs-slo-vs-sli)
- [SLA, SLO, SLI - DigitalOcean](https://www.digitalocean.com/community/tutorials/what-is-sla-slo-sli)

Tags: SRE, SLI, SLO, SLA, Reliability

---
series: observability-101
episode: 8
title: "Observability 101 (8/10): SLI and SLO Basics"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Observability
  - SLO
  - SLI
  - SRE
  - Reliability
seo_description: Define SLIs, set SLO targets, and use the error budget to make reliability a number instead of a feeling.
last_reviewed: '2026-05-15'
---

# Observability 101 (8/10): SLI and SLO Basics

Reliability conversations often go in circles because each side is speaking from instinct. One team says the service is fine, another says it is already risky, and nobody has a shared threshold for when feature work should slow down.

SLIs and SLOs solve that by turning service quality into a number, a target, and a budget the team can spend or protect.

This is the 8th post in the Observability 101 series.


![observability 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/08/08-01-concept-at-a-glance.en.png)
*observability 101 chapter 8 flow overview*
> SLI and SLO Basics is about the boundary decision, not the tool choice.

## Questions to Keep in Mind

- What boundary should you inspect first when applying SLI and SLO Basics?
- Which signal should the example or diagram make visible for SLI and SLO Basics?
- What failure should be prevented first when SLI and SLO Basics reaches a real system?

## Questions this article answers

- What does an SLI measure, and how should you measure it?
- What kind of promise does an SLO create?
- Why does the error budget become the balance point between feature delivery and reliability work?
- What kinds of conditions do burn-rate alerts catch early?
- Why should you separate internal metrics from user-facing metrics?

## Why It Matters

"Stable" is *subjective*. 99.9% is *agreement*. With SLOs, the *features vs reliability* fight is settled *with data*.

> *An SLO is *the shared language between engineers and the business*.*

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Key Terms

- **SLI**: a *measurable ratio* (e.g., success rate).
- **SLO**: a *target value* (e.g., 99.9%).
- **SLA**: a *contract*, breach has *penalty*.
- **Error budget**: the allowed *amount of failure*.
- **Burn rate**: how *fast* the budget is consumed.

## Before/After

**Before**: "It's slow" vs "it's fine" — a *word fight*.

**After**: "This month availability is *99.87%*, below the *99.9%* SLO" — *debate over*.

## Hands-on: SLOs in 5 Steps

### Step 1 — Define an SLI

```promql
# Availability SLI = good / total
sli_good = sum(rate(http_requests_total{status!~"5.."}[5m]))
sli_total = sum(rate(http_requests_total[5m]))
sli = sli_good / sli_total
```

### Step 2 — Pick an SLO target

```text
SLO: 99.9% availability over 30 days
That allows 30 * 24 * 60 * 0.001 = 43.2 minutes/month
```

### Step 3 — Error budget

```promql
1 - (sli_good / sli_total)         # current failure rate
# remaining 30-day budget = 0.001 * total - errors
```

### Step 4 — Burn-rate alert (multi-window)

```yaml
- alert: FastBurn
  expr: error_rate_5m > 14.4 * 0.001
        and error_rate_1h > 14.4 * 0.001
  for: 2m
  labels: { severity: page }
```

### Step 5 — Monthly SLO report

```text
- Availability: 99.92% (target 99.9% PASS)
- Latency: p95 320ms (target <= 500ms PASS)
- Budget burned: 38%
```

## How to Operate an Error Budget

An SLO matters only if it changes release behavior and incident response.

```text
30-day SLO target: 99.9%
allowed downtime: 43.2m
this month burned: 31.4m (72.7%)
current burn rate: 2.1x
decision: keep routine deploys, hold risky changes
```

```text
Expected output:
- The team shares one number for the target, one for remaining budget, and one for burn rate.
- Burn-rate alerts catch both fast incidents and slow degradation.
- Monthly reviews use budget consumption to decide whether feature velocity should slow down.
```

## What to Notice in This Code

- An *SLI* is always a *ratio*.
- *Burn rate* uses a *short window AND a long window*.
- If the budget *remains*, ship faster; if low, *freeze*.

## Five Common Mistakes

1. **Setting SLO to *100%*.** *Unreachable*.
2. **Using an *internal metric* as SLI.** Disconnected from user experience.
3. **Only thresholds, no *burn rate*.** Slow burns *go unnoticed*.
4. **Not using budget for *feature decisions*.** SLO becomes *decoration*.
5. **Multiple SLOs *breaking at once*.** Priority is *unclear*.

## How This Shows Up in Production

Most companies start with *availability + latency* SLOs and use them as the *criterion* for product decisions like deploys and feature additions.

## How a Senior Engineer Thinks

- *100% is *impossible*. 99.9% is a *choice*.*
- *SLI is *user-facing*.*
- *Budget is *budget*. When spent, you *stop*.*
- *Burn rate is *early warning*.*
- *Without an SLO, there is no *priority*.*

## Checklist

- [ ] You have *defined* one SLI.
- [ ] You have *agreed* on one SLO.
- [ ] You can *compute* the error budget.
- [ ] One burn-rate alert exists.

## Practice Problems

1. Write *Availability SLI* for one service in PromQL.
2. Compute the *monthly budget* (minutes) for SLO 99.9%.
3. Write a fast and slow *burn-rate* alert pair.

## Wrap-up and Next Steps

SLOs are a *shared language*. Next: *cost and cardinality*.

## Answering the Opening Questions

- **What does a service level indicator measure and how?**
  - An SLI is user experience quantified. Availability is successful response ratio; latency is p99 response time; correctness is correct result ratio. As shown in the Prometheus recording rule, raw metrics must be aggregated into ratios to become meaningful indicators.
- **What promise does a service level objective create?**
  - An SLO is a measurable internal promise like "availability ≥ 99.9% over a 30-day rolling window." This promise converts to a concrete error budget number, enabling data-driven decisions between feature shipping and stabilization.
- **Why does error budget become the balance point between feature development and stabilization?**
  - As the scenario analysis showed, a 99.9% SLO on 10M monthly requests creates an allowance of 10,000 failures. Deploy while budget remains; freeze when exhausted. Numbers—not gut feeling—make the decision, reducing conflict between dev and ops teams.
<!-- toc:begin -->
## In this series

- [Observability 101 (1/10): What Is Observability?](./01-what-is-observability.md)
- [Observability 101 (2/10): Metrics, Logs, and Traces](./02-metric-log-trace.md)
- [Observability 101 (3/10): Collecting and Visualizing Metrics](./03-metric-collection.md)
- [Observability 101 (4/10): Structured Logging](./04-structured-logging.md)
- [Observability 101 (5/10): Distributed Tracing Basics](./05-distributed-tracing.md)
- [Observability 101 (6/10): Dashboard Design](./06-dashboard-design.md)
- [Observability 101 (7/10): Alerts and On-Call](./07-alert-and-oncall.md)
- **SLI and SLO Basics (current)**
- Cost and Cardinality (upcoming)
- A Production-Ready Observability Stack (upcoming)

<!-- toc:end -->

## References

- [Google SRE — SLO chapter](https://sre.google/sre-book/service-level-objectives/)
- [The SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [Multi-window burn rate](https://sre.google/workbook/alerting-on-slos/)
- [Sloth — SLO generator](https://sloth.dev/)
- [Google Cloud — Service monitoring SLO overview](https://cloud.google.com/stackdriver/docs/solutions/slo-monitoring)

Tags: Observability, SLO, SLI, SRE, Reliability

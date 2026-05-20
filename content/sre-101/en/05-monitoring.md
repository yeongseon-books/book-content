---
series: sre-101
episode: 5
title: "SRE 101 (5/10): Monitoring"
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
  - Monitoring
  - Metrics
  - Alerting
  - Observability
seo_description: A beginner-friendly guide to monitoring covering the four golden signals, metrics, logs, alerting design, and dashboard principles
last_reviewed: '2026-05-14'
---

# SRE 101 (5/10): Monitoring

Early in an operations journey, teams often feel safer when they collect everything. CPU, memory, queue depth, request counts, logs, traces, and every possible warning all look useful because maybe one of them will matter later.

But monitoring gets better when it becomes more selective, not more crowded. A metric is valuable when it helps someone decide what to do next, and an alert is valuable when it changes behavior quickly enough to reduce user impact.

This is post 5 in the SRE 101 series. Here we treat monitoring as action-oriented measurement, then connect the four golden signals to alert rules, dashboard design, and incident response.

## Questions to Keep in Mind

- How is monitoring different from simply collecting a large amount of telemetry?
- Why do latency, traffic, errors, and saturation have to be read together?
- What questions do metrics answer better than logs, and where does that boundary flip?

## Big Picture

![sre 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/05/05-01-concept-at-a-glance.en.png)

*sre 101 chapter 5 flow overview*

This picture places Monitoring inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Monitoring is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why this topic matters

A flood of alerts drowns the real problem. When every threshold pages someone, the urgent signal and the background noise start to sound the same.

Good monitoring reduces decision time. It tells the team whether there is user impact, whether the system is recovering, and what to check first before a broad incident turns into a longer one.

> Monitoring is measurement that leads to action.

## Concept at a glance

## Key Terms

- **golden signals**: *latency, traffic, errors, saturation*.
- **alert**: an *action-required* signal.
- **threshold**: a *limit value*.
- **dashboard**: a *status screen*.
- **paging**: a *call-out notification*.

## Before/After

**Before**: collect *every* possible metric.

**After**: only *alert* on metrics that lead to *action*.

## Hands-on: Measuring the Four Signals

### Step 1 — Latency

```python
def latency_p95(samples):
    s = sorted(samples)
    return s[int(0.95 * len(s)) - 1]
```

### Step 2 — Traffic

```python
def rps(reqs, seconds):
    return reqs / seconds
```

### Step 3 — Errors

```python
def error_ratio(err, total):
    return err / total
```

### Step 4 — Saturation

```python
def saturation(used, capacity):
    return used / capacity
```

### Step 5 — Alert rule

```python
def should_page(err_ratio, p95_ms, sat):
    return err_ratio > 0.01 or p95_ms > 500 or sat > 0.9
```

### Step 6 — Decide what to check first during a latency spike

Golden signals are most useful when they shorten triage. A latency alert should not force the responder to guess where to begin; it should narrow the first few questions.

| Symptom | First check | Why this is first |
| --- | --- | --- |
| p95 latency climbs, traffic stays flat | Saturation and dependency latency | Slowdowns with steady demand often point to resource pressure or a downstream dependency. |
| Traffic drops suddenly | Ingress, CDN, or upstream routing health | Missing traffic can mean the app is healthy but requests never arrive. |
| Errors rise with saturation | Queue depth and timeouts | A service often fails at the edge of capacity before it fully falls over. |
| Errors rise without latency movement | Deployment diff or bad response path | Fast failures often mean logic, config, or auth problems rather than capacity exhaustion. |

### Step 7 — Tie structured events to alert decisions

```python
def classify_event(status_code, latency_ms, cache_hit):
    page = status_code >= 500 or latency_ms > 800
    investigate = latency_ms > 300 and not cache_hit
    return {"page": page, "investigate": investigate}
```

This is a small example, but it shows an important monitoring habit: alerts become stronger when they are linked to operational context. A spike in latency means more when the cache is missing or a dependency is timing out than when the workload is simply busier than normal.

## What to Notice in This Code

- The *four signals* are a *shared language*.
- An *alert* must be *actionable*.
- A *dashboard* should tell a *story*.

## Five Common Mistakes

1. **Alerting on *everything*.**
2. **Monitoring only *averages*.**
3. **Ignoring *saturation*.**
4. **Dashboards that are *graph graveyards*.**
5. **Letting *alert fatigue* fester.**

## How This Shows Up in Production

You combine *Prometheus* metrics with *Loki* logs in a single *Grafana* view.

## How a Senior Engineer Thinks

- An *alert* is a *scheduled phone call*.
- A *dashboard* answers a *question*.
- *Metrics* connect to *customer experience*.
- *Alert fatigue* is a *KPI*.
- *Operations* deserves *design*, too.

## Checklist

- [ ] *Four signals* defined.
- [ ] *Thresholds* agreed.
- [ ] *Dashboards* curated.
- [ ] *Alert fatigue* measured.

## Practice Problems

1. Name the *four golden signals* in one line.
2. Define *saturation* in one line.
3. Define *paging* in one line.

## Wrap-up and Next Steps

Next, we cover *incident response*.

## Answering the Opening Questions

- **How is monitoring different from simply collecting a large amount of telemetry?**
  - The article treats Monitoring as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why do latency, traffic, errors, and saturation have to be read together?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What questions do metrics answer better than logs, and where does that boundary flip?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- **Monitoring (current)**
- Incident Response (upcoming)
- Postmortem (upcoming)
- Reducing Toil (upcoming)
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)

<!-- toc:end -->

## References

- [Monitoring Distributed Systems - Google SRE Book](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Practical Alerting - Google SRE Book](https://sre.google/sre-book/practical-alerting/)
- [USE Method - Brendan Gregg](https://www.brendangregg.com/usemethod.html)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/alerting/)

Tags: SRE, Monitoring, Metrics, Alerting, Observability

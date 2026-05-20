---
series: observability-101
episode: 6
title: "Observability 101 (6/10): Dashboard Design"
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
  - Dashboard
  - Grafana
  - SRE
  - Monitoring
seo_description: USE and RED patterns and how to choose panels that answer questions instead of decorating the wall.
last_reviewed: '2026-05-15'
---

# Observability 101 (6/10): Dashboard Design

Large dashboards often look impressive right until an incident starts. The screen is full, but the first person on call still does not know where to look, what changed first, or whether the problem is user-facing or internal.

Good dashboard design fixes that. The first screen should compress the system into a small number of questions that lead directly to the next action.

This is post 6 in the Observability 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Dashboard Design?
- Which signal should the example or diagram make visible for Dashboard Design?
- What failure should be prevented first when Dashboard Design reaches a real system?

## Big Picture

![observability 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/06/06-01-concept-at-a-glance.en.png)

*observability 101 chapter 6 flow overview*

This picture places Dashboard Design inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> Dashboard Design is about the boundary decision, not the tool choice.

## Questions this article answers

- What separates a good dashboard from one that is just wallpaper?
- What questions do the RED and USE patterns answer?
- Why should you look at distributions instead of averages?
- Which panels belong on the first screen?
- How should you show context such as deploy timestamps alongside the charts?

## Why It Matters

Most dashboards are *decoration*. If you do not know *where to look* during an incident, 30 panels are worth *zero*.

> *A dashboard is a *tool that answers*. If it does not answer, delete it.*

## Concept at a Glance

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Key Terms

- **USE**: the *resource* lens.
- **RED**: the *request* lens.
- **Golden signals**: the four axes of *service health*.
- **Heatmap**: distribution *over time*.
- **Annotation**: a *marker* like a deploy.

## Before/After

**Before**: 30 panels, all *interesting*, none *answering*.

**After**: 6 panels; the first screen *immediately* tells you health.

## Hands-on: Dashboard in 5 Steps

### Step 1 — RED panels (requests)

```promql
# Rate
sum(rate(http_requests_total[1m]))
# Errors
sum(rate(http_requests_total{status=~"5.."}[1m]))
# Duration p95
histogram_quantile(0.95, sum by (le) (rate(http_duration_seconds_bucket[5m])))
```

### Step 2 — USE panels (resources)

```promql
# CPU utilization
avg(rate(node_cpu_seconds_total{mode!="idle"}[1m]))
# Memory saturation
1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes
```

### Step 3 — A Golden-signals row

```text
Row: Service Health
  Panel 1: Latency (p50/p95/p99)
  Panel 2: Traffic (req/s)
  Panel 3: Errors (5xx/min)
  Panel 4: Saturation (queue depth)
```

### Step 4 — Annotation: deploy markers

```yaml
annotations:
  - name: deploy
    datasource: prometheus
    expr: changes(build_info[1m]) > 0
```

### Step 5 — Variables to switch environment

```text
$env = staging | production
$service = api | worker | scheduler
```

## How to Validate the First Screen

The real test is whether the first 30 seconds change your next action. Imagine checkout latency rising right after a deploy.

```text
1) Check latency p95/p99 on the summary row.
2) Check whether 5xx rises at the same time.
3) Check saturation: queue depth, CPU, memory.
4) Align the anomaly with deploy annotations.
```

```text
Expected output:
- The summary row distinguishes latency regression from error spikes.
- Healthy saturation suggests the bottleneck is inside the app or a dependency, not the host.
- A deploy marker overlapping the change makes rollback or config review the next obvious step.
```

## What to Notice in This Code

- *RED* is the *outside view*; *USE* is the *inside view*.
- p95 reflects *most user experience*; p99 is the *tail*.
- *Annotations* mark the *cause* of changes.

## Five Common Mistakes

1. **30 panels on *one screen*.** No idea *where to look*.
2. **Everything as *averages*.** Distribution disappears.
3. **No unit labels.** Meaning is *ambiguous*.
4. **No thresholds.** You cannot tell *risky* from *normal*.
5. **Treating dashboards as *art*.** They cease to answer.

## How This Shows Up in Production

The most consulted *Service Overview* dashboard collapses into 6 *RED + USE* panels. Deeper dashboards are *split by role*.

## How a Senior Engineer Thinks

- *A dashboard's title *is* its question.*
- *Six panels per screen — the rest belongs in *drilldown* dashboards.*
- *p95/p99 is closer to *truth* than the average.*
- *Mark deploys with *annotations*.*
- *Panels that do not answer get *deleted*.*

## Checklist

- [ ] You know the four *RED* queries.
- [ ] You know what *USE* means.
- [ ] The first screen is a *health summary*.
- [ ] Deploy *annotations* are visible.

## Practice Problems

1. Build a *RED* dashboard for one service.
2. Build a *USE* dashboard for host resources.
3. Mark *deploy moments* with annotations.

## Wrap-up and Next Steps

Question-driven dashboards change *decision speed*. Next: *alerts and on-call*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Dashboard Design?**
  - The article treats Dashboard Design as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Dashboard Design?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Dashboard Design reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Observability 101 (1/10): What Is Observability?](./01-what-is-observability.md)
- [Observability 101 (2/10): Metrics, Logs, and Traces](./02-metric-log-trace.md)
- [Observability 101 (3/10): Collecting and Visualizing Metrics](./03-metric-collection.md)
- [Observability 101 (4/10): Structured Logging](./04-structured-logging.md)
- [Observability 101 (5/10): Distributed Tracing Basics](./05-distributed-tracing.md)
- **Dashboard Design (current)**
- Alerts and On-Call (upcoming)
- SLI and SLO Basics (upcoming)
- Cost and Cardinality (upcoming)
- A Production-Ready Observability Stack (upcoming)

<!-- toc:end -->

## References

- [Brendan Gregg — USE Method](https://www.brendangregg.com/usemethod.html)
- [Tom Wilkie — RED Method](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/)
- [Google SRE — Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Grafana dashboard best practices](https://grafana.com/docs/grafana/latest/best-practices/)
- [Grafana panels and visualizations](https://grafana.com/docs/grafana/latest/panels-visualizations/)

Tags: Observability, Dashboard, Grafana, SRE, Monitoring

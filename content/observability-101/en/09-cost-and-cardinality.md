---
series: observability-101
episode: 9
title: "Observability 101 (9/10): Cost and Cardinality"
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
  - Cost
  - Cardinality
  - Metrics
  - Sampling
seo_description: How cardinality explosions, retention tiers, and sampling decisions actually drive — and tame — observability cost.
last_reviewed: '2026-05-15'
---

# Observability 101 (9/10): Cost and Cardinality

Observability rarely looks expensive at the beginning. A few counters, a few logs, a bit of tracing, and the bill seems harmless. Then one month later the cost curve changes shape and nobody can explain why.

The answer is usually structural, not accidental: too many unique labels, too much retention, and too little sampling discipline.

This is the 9th post in the Observability 101 series.


![observability 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/09/09-01-concept-at-a-glance.en.png)
*observability 101 chapter 9 flow overview*
> Cost and Cardinality is about the boundary decision, not the tool choice.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Cost and Cardinality?
- Which signal should the example or diagram make visible for Cost and Cardinality?
- What failure should be prevented first when Cost and Cardinality reaches a real system?

## Questions this article answers

- Why is cardinality directly tied to cost?
- Why should retention be split into tiers?
- How do head sampling and tail sampling differ?
- What cost curve does each signal — metrics, logs, and traces — follow?
- Why does a team need its own observability cost budget?

## Why It Matters

In young companies the *#1 line on the AWS bill* is often *observability*. When monitoring costs *more than the product*, it becomes politics.

> *If you do not know the cost of measurement, *measurement becomes the enemy*.*

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Key Terms

- **Cardinality**: number of *unique label combinations*.
- **Retention tier**: hot / warm / cold *separation*.
- **Head sampling**: decided at the *start*.
- **Tail sampling**: decided after the trace finishes (slow / error first).
- **Aggregation**: shrink volume by *aggregating before retention*.

## Before/After

**Before**: `user_id` as a label, *50M series*, cost *explodes*.

**After**: `user_id` in *logs only*, labels stay *finite*, cost *predictable*.

## Hands-on: Cost Control in 5 Steps

### Step 1 — Measure cardinality

```promql
count({__name__=~".+"})              # total series
topk(20, count by (__name__) (...))  # top metrics
```

### Step 2 — Remove dangerous labels

```text
# Bad: per-user series
http_requests_total{user_id="42", path="/buy"}
# Good: dimension reduction
http_requests_total{path="/buy"}      # user_id goes to logs
```

### Step 3 — Retention tiers

```yaml
prometheus:  retention: 15d
thanos:      retention.resolution-raw: 30d
             retention.resolution-5m: 90d
             retention.resolution-1h: 1y
```

### Step 4 — Tail sampling

```yaml
processors:
  tail_sampling:
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow
        type: latency
        latency: { threshold_ms: 500 }
      - name: random
        type: probabilistic
        probabilistic: { sampling_percentage: 5 }
```

### Step 5 — Per-signal budget

```text
metric:  <= X million series
log:     <= Y GB per day
trace:   <= Z traces per minute after sampling
```

## How to Start a Cost Review

Do not wait for the invoice. Review high-cardinality metrics directly in the monitoring system.

```promql
count({__name__=~".+"})
topk(10, count by (__name__) ({__name__=~".+"}))
```

```text
Expected output:
- A small set of metrics accounts for most time series.
- Finite labels such as `path` and `status` stay, while identifiers such as `user_id` and `request_id` get removed from metrics.
- Teams can act before budgets are exceeded by cutting labels, retention, or sampling volume.
```

## What to Notice in This Code

- *Cardinality* explodes via *label multiplication*.
- *Resolution downsampling* shrinks volume of *older data*.
- *Tail sampling* keeps only *valuable traces*.

## Five Common Mistakes

1. **`user_id`, `request_id` as *labels*.** Cardinality explosion.
2. **Keeping every signal *forever*.** Cost compounds.
3. **Treating sampling as *bad*.** Risk of insolvency.
4. **Embedding *binaries* in logs.** Volume explosion.
5. **No *team-level* cost view.** Accountability dilutes.

## How This Shows Up in Production

Most companies combine *team cardinality budgets*, *retention tiers*, and *tail sampling* to make observability cost *predictable*.

## How a Senior Engineer Thinks

- *Cardinality is *tax*.*
- *Old data lives at *lower resolution*.*
- *Sampling is *not shameful*.*
- *Cost must have an *owner*.*
- *Measure the cost of measurement.*

## Checklist

- [ ] You know the *top-cardinality* metrics.
- [ ] *Retention tiers* are layered.
- [ ] Traces have *sampling*.
- [ ] Each team has a *cost budget*.

## Practice Problems

1. Find three labels that risk cardinality explosion.
2. Design a 3-tier retention plan.
3. Write a tail-sampling policy for *errors / slow / random*.

## Wrap-up and Next Steps

Without cost awareness, *observability becomes the enemy*. Next: *a production-ready stack*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Cost and Cardinality?**
  - The article treats Cost and Cardinality as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Cost and Cardinality?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Cost and Cardinality reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Observability 101 (1/10): What Is Observability?](./01-what-is-observability.md)
- [Observability 101 (2/10): Metrics, Logs, and Traces](./02-metric-log-trace.md)
- [Observability 101 (3/10): Collecting and Visualizing Metrics](./03-metric-collection.md)
- [Observability 101 (4/10): Structured Logging](./04-structured-logging.md)
- [Observability 101 (5/10): Distributed Tracing Basics](./05-distributed-tracing.md)
- [Observability 101 (6/10): Dashboard Design](./06-dashboard-design.md)
- [Observability 101 (7/10): Alerts and On-Call](./07-alert-and-oncall.md)
- [Observability 101 (8/10): SLI and SLO Basics](./08-sli-and-slo.md)
- **Cost and Cardinality (current)**
- A Production-Ready Observability Stack (upcoming)

<!-- toc:end -->

## References

- [Cardinality is the enemy](https://www.robustperception.io/cardinality-is-key/)
- [Thanos downsampling](https://thanos.io/tip/components/compact.md/)
- [OpenTelemetry tail sampling](https://opentelemetry.io/docs/collector/configuration/#processors)
- [Honeycomb on cost](https://www.honeycomb.io/blog/observability-cost)

Tags: Observability, Cost, Cardinality, Metrics, Sampling

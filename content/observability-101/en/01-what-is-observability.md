---
series: observability-101
episode: 1
title: "Observability 101 (1/10): What Is Observability?"
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
  - Monitoring
  - SRE
  - DevOps
  - Metrics
seo_description: Monitoring versus observability, the three pillars (metrics, logs, traces), and where production visibility actually starts.
last_reviewed: '2026-05-15'
---

# Observability 101 (1/10): What Is Observability?

Production systems rarely fail in a dramatic way. Checkout gets slower, a small slice of requests starts timing out, and logs leave only a few clues. You can see the symptom, but not the mechanism, and that gap is what makes incident response expensive.

Observability is what closes that gap. It is the difference between watching a known threshold and being able to infer the inside of a system from the outside when the failure mode is new.

This is the first post in the Observability 101 series.


![observability 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/01/01-01-concept-at-a-glance.en.png)
*observability 101 chapter 1 flow overview*
> What Is Observability is about the boundary decision, not the tool choice.

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is Observability??
- Which signal should the example or diagram make visible for What Is Observability??
- What failure should be prevented first when What Is Observability? reaches a real system?

## Questions this article answers

- How is observability different from monitoring?
- What question does each signal — metrics, logs, and traces — answer?
- Why do you need to read the three signals together?
- Why is `trace_id` the connective tissue of observability?
- Where should a small service start when adding its first signals?

## Why It Matters

Production systems break in *unpredictable ways*. Pre-built dashboards cannot explain *failures you have never seen*. Observability gives you a system you can *ask questions of*.

> *Dashboards are *answers*; observability is *questions*.*

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Key Terms

- **Metric**: a *number* that changes over time. Example: requests per second.
- **Log**: a *text line* recording an event.
- **Trace**: the *path* a single request takes across services.
- **Cardinality**: the number of *unique label combinations*.
- **SLO**: a *numeric promise* the service must keep.

## Before/After

**Before**: An alert fires and you have *no idea where it started*. You *grep* logs and flail.

**After**: You see the *symptom* on a dashboard, find the *responsible service* with a trace, and read *context* from logs.

## Hands-on: Your First Signals in 5 Steps

### Step 1 — The simplest metric

```python
import time
counter = 0

def handle_request():
    global counter
    counter += 1
    return f"requests_total {counter}"
```

### Step 2 — Structured logs

```python
import json, time

def log_event(event, **fields):
    print(json.dumps({"ts": time.time(), "event": event, **fields}))

log_event("request_received", path="/health", status=200)
```

### Step 3 — A simple trace

```python
import uuid

def handle(req):
    trace_id = req.get("trace_id") or str(uuid.uuid4())
    log_event("auth_start", trace_id=trace_id)
    log_event("db_query", trace_id=trace_id)
    log_event("response_sent", trace_id=trace_id)
```

### Step 4 — Reading the three together

```bash
# metric: requests in the last minute
# log: search by trace_id
grep '"trace_id": "abc-123"' app.log
```

### Step 5 — Answer one question

```text
"Why did checkout get slow?"
1. metric: latency curve rises
2. trace: payment span is long
3. log: db connection timeout
```

## How to Narrow the First Incident

Suppose checkout latency jumps right after a deploy. The fastest path is not to open every tool at once, but to keep the three signals in a fixed order.

```text
1) metric  → checkout p95 rises from 180ms to 1.8s
2) trace   → one payment span dominates the request time
3) log     → db_pool_timeout, retry=3, trace_id=9f3c...
```

That order matters. Metrics tell you when the symptom started, traces show where the latency accumulated, and logs explain why that part of the path failed.

```text
Expected output:
- The latency chart shows checkout getting worse before the incident ticket arrives.
- The trace view points to one slow span instead of the whole service.
- The matching log lines confirm whether the cause is a timeout, retry storm, or dependency failure.
```

## What to Notice in This Code

- The three signals *complement each other*. None of them is *enough alone*.
- *trace_id* is what *links* metrics, logs, and traces.
- Structured logs are *machine-readable data*.

## Five Common Mistakes

1. **Treating monitoring and observability as *synonyms*.** One is *answers*, the other is *the ability to ask*.
2. **Collecting only metrics.** You cannot answer *why*.
3. **Writing logs as *unstructured text*.** Search becomes *hell*.
4. **Not propagating *trace_id* across services.** Traces *break*.
5. **Storing every signal *forever*.** Cost *explodes*.

## How This Shows Up in Production

Most SRE teams treat the *three pillars* as their *minimum signal set* and then design alerts on top of *SLOs*.

## How a Senior Engineer Thinks

- *Systems should be *glass boxes*, not *black boxes*.*
- *Dashboards are *answers to questions*, not decoration.*
- *Cardinality is *cost*.*
- *Propagate *trace_id* through every signal.*
- *The real test is whether you can *ask about an unknown failure*.*

## Checklist

- [ ] You can explain *monitoring* vs *observability*.
- [ ] You can name the *three pillars*.
- [ ] You can write one structured log line.
- [ ] You understand the role of *trace_id*.

## Practice Problems

1. Pick a recent incident. Decompose it into the *three pillars*.
2. Rewrite one unstructured log line as *JSON*.
3. Give two examples each of *known unknown* and *unknown unknown*.

## Wrap-up and Next Steps

Observability is the discipline of *asking inside from outside*. Next we look deeper into *the three pillars*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying What Is Observability??**
  - The article treats What Is Observability? as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for What Is Observability??**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when What Is Observability? reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **What Is Observability? (current)**
- Metrics, Logs, and Traces (upcoming)
- Collecting and Visualizing Metrics (upcoming)
- Structured Logging (upcoming)
- Distributed Tracing Basics (upcoming)
- Dashboard Design (upcoming)
- Alerts and On-Call (upcoming)
- SLI and SLO Basics (upcoming)
- Cost and Cardinality (upcoming)
- A Production-Ready Observability Stack (upcoming)

<!-- toc:end -->

## References

- [OpenTelemetry overview](https://opentelemetry.io/docs/concepts/)
- [Google SRE Book — Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Three Pillars of Observability](https://www.cncf.io/blog/2022/05/24/observability-cloud-native/)
- [Observability vs Monitoring](https://www.honeycomb.io/blog/observability-101)

Tags: Observability, Monitoring, SRE, DevOps, Metrics

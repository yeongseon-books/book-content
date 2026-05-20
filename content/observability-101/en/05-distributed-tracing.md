---
series: observability-101
episode: 5
title: "Observability 101 (5/10): Distributed Tracing Basics"
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
  - Tracing
  - OpenTelemetry
  - SRE
  - Microservices
seo_description: Spans, traces, context propagation, and your first OpenTelemetry trace — how a single request flows across many services.
last_reviewed: '2026-05-15'
---

# Observability 101 (5/10): Distributed Tracing Basics

Metrics can tell you a request got slower, and logs can tell you a timeout happened somewhere. But once one request crosses several services, that still leaves the central question unanswered: where did the time go?

Distributed tracing answers that by breaking one request into spans, preserving parent-child relationships, and carrying context across service boundaries.

This is post 5 in the Observability 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Distributed Tracing Basics?
- Which signal should the example or diagram make visible for Distributed Tracing Basics?
- What failure should be prevented first when Distributed Tracing Basics reaches a real system?

## Big Picture

![observability 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/05/05-01-concept-at-a-glance.en.png)

*observability 101 chapter 5 flow overview*

This picture places Distributed Tracing Basics inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> Distributed Tracing Basics is about the boundary decision, not the tool choice.

## Questions this article answers

- What is a span, and what is a trace?
- Why does context propagation matter when a request crosses services?
- Why is sampling central to cost control?
- How do you build your first trace with OpenTelemetry?
- What is hardest about operating without distributed tracing?

## Why It Matters

In a microservice world, finding the cause of a *slow request* with logs and metrics alone is *impossible*. Tracing is the *only answer*.

> *Debugging a distributed system without tracing is *walking a maze blindfolded*.*

## Concept at a Glance

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Key Terms

- **Trace**: the *whole flow* of one request.
- **Span**: a *single segment* inside a trace.
- **Parent / Child**: the *call relationship* between spans.
- **Context propagation**: passing *trace_id* through headers.
- **Sampling**: recording only *some traces*.

## Before/After

**Before**: You *grep* logs and *guess* which service was slow.

**After**: The *slow span* is *immediately* visible in the trace UI.

## Hands-on: Your First Trace in 5 Steps

### Step 1 — Install OpenTelemetry

```bash
pip install opentelemetry-api opentelemetry-sdk \
            opentelemetry-exporter-otlp
```

### Step 2 — Configure tracer

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor, ConsoleSpanExporter)

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter()))
tracer = trace.get_tracer("app")
```

### Step 3 — First span

```python
with tracer.start_as_current_span("handle_request") as s:
    s.set_attribute("user_id", 42)
    with tracer.start_as_current_span("db_query"):
        pass
```

### Step 4 — Context propagation (HTTP headers)

```python
from opentelemetry.propagate import inject, extract

headers = {}
inject(headers)                  # before call: inject trace_id
ctx = extract(incoming_headers)  # at receiver: restore from headers
```

### Step 5 — Sampling

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
TracerProvider(sampler=TraceIdRatioBased(0.1))   # 10% only
```

## How to Verify a Slow Request

Tracing becomes valuable when you can point to one slow span instead of blaming the whole service.

```text
trace_id=9f3c...
handle_request  2450ms
├─ auth_check    120ms
├─ payment_call 1980ms
└─ db_write      210ms
```

```text
Expected output:
- The root span shows total request time.
- One child span stands out as the bottleneck.
- Matching logs with the same `trace_id` explain whether the issue was a timeout, retry storm, or upstream dependency failure.
```

## What to Notice in This Code

- *One trace = a tree of many spans*.
- The *traceparent* header is the W3C standard.
- *Sampling* is the heart of *cost control*.

## Five Common Mistakes

1. **Storing 100% of traces.** Cost *explodes*.
2. **Failing to *propagate* context.** Traces *break*.
3. **Putting *too many attributes* on a span.** Cardinality explodes.
4. **Losing context in *async* code.** Parent tracking fails.
5. **Reading only traces and *ignoring metrics*.** You miss trend.

## How This Shows Up in Production

OpenTelemetry → *Tempo / Jaeger / Honeycomb*, then Grafana shows *trace ↔ log ↔ metric* on *one screen*.

## How a Senior Engineer Thinks

- *Trace is the *map*, log is the *annotation*.*
- *Let the *framework* propagate context.*
- *Sampling rate = *volume × value*.*
- *Span names follow *verb + noun* (`db_query`, `cache_get`).*
- *Every signal carries *trace_id*.*

## Checklist

- [ ] You see your first span in the *console*.
- [ ] You understand the *traceparent* header.
- [ ] You set a *sampling* rate.
- [ ] Logs include *trace_id*.

## Practice Problems

1. Connect a *trace* across two services via propagation.
2. Use a *different* sampling rate per environment.
3. Write a query that finds the *slowest span* (PromQL/TraceQL).

## Wrap-up and Next Steps

When traces flow, *the flow becomes visible*. Next: *dashboard design*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Distributed Tracing Basics?**
  - The article treats Distributed Tracing Basics as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Distributed Tracing Basics?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Distributed Tracing Basics reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Observability 101 (1/10): What Is Observability?](./01-what-is-observability.md)
- [Observability 101 (2/10): Metrics, Logs, and Traces](./02-metric-log-trace.md)
- [Observability 101 (3/10): Collecting and Visualizing Metrics](./03-metric-collection.md)
- [Observability 101 (4/10): Structured Logging](./04-structured-logging.md)
- **Distributed Tracing Basics (current)**
- Dashboard Design (upcoming)
- Alerts and On-Call (upcoming)
- SLI and SLO Basics (upcoming)
- Cost and Cardinality (upcoming)
- A Production-Ready Observability Stack (upcoming)

<!-- toc:end -->

## References

- [OpenTelemetry tracing](https://opentelemetry.io/docs/concepts/signals/traces/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [Jaeger architecture](https://www.jaegertracing.io/docs/latest/architecture/)
- [Sampling strategies](https://opentelemetry.io/docs/concepts/sampling/)

Tags: Observability, Tracing, OpenTelemetry, SRE, Microservices

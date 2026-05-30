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

This is the 5th post in the Observability 101 series.


![observability 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/05/05-01-concept-at-a-glance.en.png)
*observability 101 chapter 5 flow overview*
> Distributed Tracing Basics is about the boundary decision, not the tool choice.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Distributed Tracing Basics?
- Which signal should the example or diagram make visible for Distributed Tracing Basics?
- What failure should be prevented first when Distributed Tracing Basics reaches a real system?

## Questions this article answers

- What is a span, and what is a trace?
- Why does context propagation matter when a request crosses services?
- Why is sampling central to cost control?
- How do you build your first trace with OpenTelemetry?
- What is hardest about operating without distributed tracing?

## Why It Matters

In a microservice world, finding the cause of a *slow request* with logs and metrics alone is *impossible*. Tracing is the *only answer*.

> *Debugging a distributed system without tracing is *walking a maze blindfolded*.*

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

## OpenTelemetry Python Instrumentation — Extended Example

Auto-instrumentation alone often cannot express domain boundaries well enough. Business segments like payment, inventory, or coupon processing benefit from manual spans that make intent explicit.

```python
import time
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer("checkout-service")

def checkout(order_id: str, amount: int) -> None:
    with tracer.start_as_current_span("checkout") as root:
        root.set_attribute("order.id", order_id)
        root.set_attribute("order.amount", amount)

        with tracer.start_as_current_span("validate_order"):
            time.sleep(0.02)

        with tracer.start_as_current_span("charge_payment") as span:
            try:
                time.sleep(0.35)
                raise TimeoutError("gateway timeout")
            except TimeoutError as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                span.set_attribute("payment.retry", 2)
                raise
```

Span names become search keys later, so keep them short and consistent. Mixing `pay`, `payment_call`, and `charge_gateway` for the same operation degrades query quality across the team.

## Context Propagation Patterns in Practice

The most common context-loss points are non-HTTP boundaries: queues, batch jobs, and async workers. The example below covers both HTTP headers and message queues in one minimal pattern.

```python
from opentelemetry.propagate import inject, extract

def build_http_headers() -> dict:
    headers = {}
    inject(headers)
    return headers

def publish_message(payload: dict) -> dict:
    carrier = {}
    inject(carrier)
    return {
        "payload": payload,
        "trace_headers": carrier,
    }

def consume_message(message: dict):
    ctx = extract(message["trace_headers"])
    tracer = trace.get_tracer("worker")
    with tracer.start_as_current_span("worker.handle", context=ctx):
        # actual processing
        pass
```

For message systems, fix the header field name convention in team documentation. Producers and consumers often use different languages, so if only one side knows the rules, traces break mid-stream.

## Sampling Policy Design Guide

| Policy | Advantage | Disadvantage | Recommended for |
| --- | --- | --- | --- |
| 100% storage | Maximum debug info | Cost grows fast | Dev / short experiments |
| Head 10% | Simple, predictable | May miss rare errors | High-traffic normal paths |
| Tail (error/latency first) | Preserves high-value traces | Configuration complexity | Production default |

A practical starting point: "100% errors + 100% high-latency + 5% normal." This combination controls cost while retaining enough samples for incident analysis. Sampling is not a set-and-forget config — adjust monthly based on traffic patterns and incident frequency.

## W3C Trace Context Standard in Detail

Interoperability in distributed tracing is guaranteed by the W3C Trace Context standard, which defines two HTTP headers.

| Header | Format | Example |
| --- | --- | --- |
| `traceparent` | `{version}-{trace-id}-{parent-id}-{trace-flags}` | `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01` |
| `tracestate` | Vendor key-value pairs | `congo=t61rcWkgMzE,rojo=00f067aa0ba902b7` |

Fields in `traceparent`:

- **version** (2 digits): currently fixed at `00`
- **trace-id** (32 hex chars): 128-bit ID identifying the entire request
- **parent-id** (16 hex chars): 64-bit ID of the immediate parent span
- **trace-flags** (2 hex chars): `01` = sampled, `00` = not sampled

`tracestate` carries vendor-specific metadata. Commercial tools like Datadog or Dynatrace use it to attach their own correlation IDs. As long as the standard is followed, services using different tracing backends still share a single trace_id without breaks.

```python
# traceparent header parsing example
def parse_traceparent(header: str) -> dict:
    parts = header.split("-")
    return {
        "version": parts[0],
        "trace_id": parts[1],
        "parent_id": parts[2],
        "trace_flags": parts[3],
        "sampled": parts[3] == "01",
    }

# example
tp = parse_traceparent("00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01")
# {"version": "00", "trace_id": "4bf92f...", "parent_id": "00f067...", "sampled": True}
```

## Async Context Propagation

In Python's `asyncio` environment, `contextvars` automatically carries context across coroutines. But when dispatching to thread pools or process pools, you must copy context explicitly.

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from opentelemetry import context, trace

tracer = trace.get_tracer("async-service")

async def handle_request():
    with tracer.start_as_current_span("async_handler"):
        # asyncio.create_task copies contextvars automatically
        task = asyncio.create_task(fetch_data())
        await task

async def fetch_data():
    # parent span is automatically connected
    with tracer.start_as_current_span("fetch_data"):
        await asyncio.sleep(0.1)

def sync_work():
    # explicit propagation needed when dispatched via ThreadPoolExecutor
    with tracer.start_as_current_span("sync_work"):
        pass

async def dispatch_to_thread():
    with tracer.start_as_current_span("dispatcher"):
        ctx = context.get_current()
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=2)
        # attach/detach to propagate context into thread
        await loop.run_in_executor(
            executor,
            lambda: context.attach(ctx) or sync_work()
        )
```

Key points:

1. **asyncio.create_task**: copies `contextvars` automatically — no extra work needed.
2. **ThreadPoolExecutor**: call `context.get_current()` and `context.attach()` inside the thread.
3. **ProcessPoolExecutor**: context does not cross process boundaries. Serialize `traceparent` into the message payload.

## Trace–Log–Metric Correlation

Traces alone tell you "it was slow" but may miss "why it was slow." Connecting all three signals narrows the cause quickly.

| Connection direction | Method | Effect |
| --- | --- | --- |
| Trace → Log | Include `trace_id` field in logs | Detailed context for slow spans |
| Trace → Metric | Attach trace_id as an exemplar | Click from histogram to trace |
| Metric → Trace | Grafana Tempo integration | Jump from metric dashboard to trace view |

```python
import structlog
from opentelemetry import trace

logger = structlog.get_logger()

def process_order(order_id: str):
    span = trace.get_current_span()
    ctx = span.get_span_context()
    # automatically include trace_id in every log line
    log = logger.bind(
        trace_id=format(ctx.trace_id, "032x"),
        span_id=format(ctx.span_id, "016x"),
    )
    log.info("order_processing_start", order_id=order_id)
    # ... business logic ...
    log.info("order_processing_end", order_id=order_id)
```

In Grafana, registering Loki (logs) and Tempo (traces) as data sources lets you click a `trace_id` field in a log line and jump directly to the trace view. Without this link, correlating logs to traces requires manual copy-paste — adding minutes to every incident.

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

- **What are spans and traces?**
  - A span records one work segment (function call, DB query, HTTP request); a trace is the tree of spans sharing the same trace_id. The root span starts the request; child spans are subordinate calls. The waterfall view in Jaeger or Tempo is this tree.
- **Why is context propagation critical when requests cross multiple services?**
  - Without context propagation, each service generates independent traces and a single request scatters into disconnected fragments. The W3C Trace Context `traceparent` header carries trace_id and parent_span_id, letting receiving services attach their spans to the same tree.
- **Why is sampling the key to cost control?**
  - Each trace costs tens to hundreds of KB in storage. At 10 million requests per day, 100% storage accumulates terabytes. Sampling normal traffic at 5% while preserving 100% of errors and high-latency traces cuts costs by over 90% while maintaining incident analysis quality.
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

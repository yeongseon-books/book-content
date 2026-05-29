---
series: observability-101
episode: 2
title: "Observability 101 (2/10): Metrics, Logs, and Traces"
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
  - Metrics
  - Logging
  - Tracing
  - SRE
seo_description: How metrics, logs, and traces differ, and when to reach for each — answers to how much, what happened, and where it slowed down.
last_reviewed: '2026-05-15'
---

# Observability 101 (2/10): Metrics, Logs, and Traces

Many teams say they use all three signals, but still send every question to the same place. Everything becomes a log search, or everything gets flattened into dashboards. That is where cost grows faster than understanding.

The real skill is not collecting more signals. It is choosing the right one for the question in front of you.

This is the 2nd post in the Observability 101 series.


![observability 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/02/02-01-concept-at-a-glance.en.png)
*observability 101 chapter 2 flow overview*
> Metrics, Logs, and Traces is about the boundary decision, not the tool choice.

## Questions to Keep in Mind

- What questions do metrics, logs, and traces each answer?
- How do the data shapes of the three signals differ?
- Where do cardinality and cost grow?

## What You Will Learn

- The *question domain* of each signal
- Each signal's *data model*
- *Cardinality* and *cost*
- A decision rule for *when to use what*
- Five common pitfalls

## Why It Matters

Teams whose costs grow fastest share a pattern: everything goes into logs, or everything becomes dashboards with no way to explain *why* something failed. Both problems stem from blurred signal boundaries.

When you separate the roles clearly — trends go to metrics, event context goes to logs, request paths go to traces — tools become simpler, search time drops, and you get more answers for less money.

> *One right signal beats ten wrong dashboards.*

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Comparing the Three Signals

Each signal carries a different data shape, storage cost profile, question type, and representative toolset.

| Signal | Data Shape | Storage Cost | Question Type | Representative Tools |
| --- | --- | --- | --- | --- |
| Metric | Numeric time-series | Low (aggregatable) | How much? When? | Prometheus, Grafana |
| Log | Event + context fields | Medium | Why did it fail? | Loki, ELK, BigQuery |
| Trace | Request path tree | High (sampling required) | Which hop was slow? | Jaeger, Tempo |

Cost increases from metric to trace. In operations, the standard order is: narrow the blast radius with metrics first, confirm the reason with logs, then drill into traces only for the specific requests that need it.

## How the Three Signals Connect

Each signal alone is incomplete. Together they form a single narrative.

Metrics show *when* the problem started. Traces point to *where* it happened. Logs explain *why*. When these three questions connect into a single flow, an incident becomes inference rather than intuition.

For example, if the payment API slows down:

1. Metric: p95 latency tripled in the last 10 minutes.
2. Trace: the `payment_gateway` span accounts for 80% of total latency.
3. Log: `{"event": "payment_timeout", "gateway": "stripe", "retry": 3}`

Read in this order, symptom → location → reason forms a single line. Practicing the three signals together builds operational intuition far faster than studying each one in isolation.

## Creating Trace Spans with OpenTelemetry

Among the three signals, traces are the hardest to set up. Below is a Python example that creates a simple span using OpenTelemetry.

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

# Initialize the tracer
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

tracer = trace.get_tracer(__name__)

# Create spans
def process_payment(order_id: int):
    with tracer.start_as_current_span("payment_processing") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("service.name", "payment-service")

        # Child span
        with tracer.start_as_current_span("db_query"):
            # Simulate DB operation
            pass

        with tracer.start_as_current_span("external_api_call"):
            # Simulate external API call
            pass

        return {"status": "success", "order_id": order_id}

# Usage
process_payment(12345)
```

Running this code prints span information to the console. A single request splits into multiple segments, each recording its start and end time. When you later analyze a slow request, you can see at a glance which span took the longest.

## Querying Metrics with PromQL

Once metrics are collected, you need queries to extract answers. PromQL — Prometheus's query language — is the core tool for aggregating and filtering time-series data.

```promql
# Requests per second over the last 5 minutes
rate(http_requests_total{service="checkout-api"}[5m])

# Error rate (5xx ratio)
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))

# p95 latency (histogram-based)
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket{service="checkout-api"}[5m])) by (le)
)

# Top 5 services by error rate
topk(5,
  sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
  / sum(rate(http_requests_total[5m])) by (service)
)
```

These four queries are the patterns you will use most often in operations.

- `rate()`: Computes the per-second change rate of a counter. Shows meaningful trends rather than raw cumulative values.
- `histogram_quantile()`: Estimates percentiles from histogram buckets. Essential for observing tail latency (p95, p99).
- `topk()`: Selects the time-series with the highest values. Convenient for identifying the worst-performing services first.
- `sum() by ()`: Aggregates by label. Used for per-service, per-route, or per-environment comparisons.

When you are comfortable with PromQL, you can get answers directly from the CLI without opening a dashboard. However, if the queried labels are too numerous, query performance drops sharply. Label design is covered in detail in episode 9 (Cost and Cardinality).

## Why Cardinality Determines Cost

To understand metric cost, you must first understand cardinality. Cardinality is the number of unique time-series created by label combinations.

```text
http_requests_total{service="checkout", method="POST", status="200"}
http_requests_total{service="checkout", method="POST", status="500"}
http_requests_total{service="checkout", method="GET", status="200"}
```

Three label combinations produce three time-series. The problem arises when you put unique identifiers in labels.

```text
# Never do this
http_requests_total{user_id="u-123456", ...}
http_requests_total{user_id="u-123457", ...}
# → One time-series per user
```

One million users means one million time-series. Prometheus holds all active time-series in memory, so a cardinality explosion causes OOM and kills the metrics system itself.

Safe label design follows three rules:

1. Label values must come from a finite set (HTTP method, status code, service name).
2. Identifiers (user_id, order_id, trace_id) belong in logs or traces, not in labels.
3. Before adding a new label, calculate the expected series count: `existing series × new label cardinality`.

## Key Terms

- **Counter / Gauge / Histogram**: the three *shapes* of metrics.
- **Sampling**: *cost reduction* by collecting only a portion.
- **Span**: a single segment of a trace.
- **Label / Tag**: an *identifier* attached to a signal.
- **Retention**: how *long* a signal is kept.

## Before/After

**Before**: Everything goes into logs. Search is *slow* and the bill is *huge*. Or everything is dashboards — you see the average but cannot explain failures.

**After**: Throughput and error rates go to metrics, the reason a specific order failed goes to logs, which service call took the time goes to traces. Each signal owns a different question, and operational decisions speed up.

## Using the Three Signals in Order

The order in which you consult the three signals during an incident matters. Below is a real-world incident response flow.

### Step 1 — Narrow the blast radius with metrics

When an alert fires, the first task is determining whether the outage is system-wide or partial.

- Did error rates rise across all endpoints?
- Is only a specific route slow?
- Is the problem confined to a region or user group?

These questions can only be answered by metrics. Narrowing with metrics *before* looking at logs avoids unnecessary log searches.

### Step 2 — Locate the bottleneck with traces

Once you have narrowed the scope, find which segment is slow.

- Pick a few slow requests and open their traces.
- Identify which span took the longest.
- Record the service name and operation name of that span.

Traces are the "where" tool. When multiple services are involved, finding the responsible one without traces is nearly impossible.

### Step 3 — Confirm the reason with logs

After locating the bottleneck, confirm the cause.

- Filter logs by the trace_id from the trace.
- Check ERROR-level logs in that segment.
- Review error messages, stack traces, and external API responses.

Logs are the "why" tool. Metrics narrow, traces point, and logs explain.

### Example: Payment API Outage

```text
1. Metric: payment_api p95 latency 180ms → 1.8s (10× increase)
   ⇒ The entire payment API is slow

2. Trace: trace_id=9f3c...
   payment_api span: 1.7s
     ├─ auth_check: 80ms
     ├─ card_gateway: 1.5s  ← bottleneck!
     └─ db_write: 120ms
   ⇒ The card_gateway call is the problem

3. Log: grep 'trace_id=9f3c' | grep ERROR
   {"level":"ERROR","event":"gateway_timeout","gateway":"stripe","timeout_ms":1500}
   ⇒ Stripe API timed out after 1.5s
```

Following these three steps, the vague symptom "payments are slow" narrows to the specific cause "the external payment gateway is timing out."

## Hands-on: Compare the Three in 5 Steps

### Step 1 — Counter

```python
http_requests_total = 0

def on_request():
    global http_requests_total
    http_requests_total += 1
```

A counter is the simplest metric. It suits values that only accumulate, like total requests. It is the starting point for seeing whether a system is busy or idle.

### Step 2 — Histogram

```python
import time
buckets = {0.1: 0, 0.5: 0, 1.0: 0, "inf": 0}

def observe(d):
    for b in [0.1, 0.5, 1.0]:
        if d <= b: buckets[b] += 1; return
    buckets["inf"] += 1
```

Averages hide the long tail. A histogram preserves the distribution so you can compute p95 and p99. Users remember the slow requests, not the average.

### Step 3 — Structured log

```python
import json
def log(event, **f):
    print(json.dumps({"event": event, **f}))

log("payment_failed", order_id=42, reason="card_declined")
```

Logs record events. Why a payment failed, which order ID, which reason — context that metrics cannot capture. In operations, the material for explaining "why" is almost always in logs.

### Step 4 — Simple trace

```python
import uuid, time

def span(name, trace_id):
    s = time.time()
    log("span_start", trace_id=trace_id, name=name)
    yield
    log("span_end", trace_id=trace_id, name=name, dur=time.time()-s)
```

Traces show the path a request travels. Under the same trace_id, recording start and end lets you read which segment stretched and which service is the bottleneck.

### Step 5 — Decision rule

```text
"overall throughput" → metric
"why this order failed" → log
"which service was slow for this request" → trace
```

The key is the decision rule. Trends and throughput → metric. Event reason → log. Request path → trace. The clearer this rule, the simpler signal design becomes.

## One Failed Order, Three Different Questions

If order failures spike, start by separating the questions instead of mixing them.

```text
Question 1. Is the failure broad or isolated?       → metric
Question 2. Which order failed, and why?            → log
Question 3. Which service call consumed the time?   → trace
```

```text
metric: 5xx ratio 0.4% → 6.2%
log: payment_failed reason=card_gateway_timeout
trace: checkout → payment-gateway span p95 2.4s
```

```text
Expected output:
- Metrics show the blast radius.
- Logs classify the failure type.
- Traces identify the slow or broken hop.
```

## What to Notice in This Code

- A *counter* only goes *up*. A *gauge* moves *up and down*.
- A *histogram* shows *distribution*: p50/p95/p99.
- *trace_id* is the *thread* that ties signals together.

## Five Common Mistakes

1. **Putting everything in logs.** Cost *explodes*, search becomes *hell*.
2. **Confusing counter and gauge.** Your graph stops *making sense*.
3. **Watching only the *average*.** You miss the *long tail*.
4. **Putting *user_id* in a label.** *Cardinality* explodes.
5. **Reading only traces, ignoring metrics.** You miss *overall trend*.

## When to Start With Which Signal

Rather than a rigid rule like "always start with metrics," choosing the starting point by question type shortens incident response time.

| Starting Question | 1st Signal | 2nd Signal | 3rd Signal | Reason |
| --- | --- | --- | --- | --- |
| Has overall quality degraded? | Metric | Trace | Log | Blast radius first. |
| Why did this specific order fail? | Log | Trace | Metric | Event context first. |
| Why is this specific call slow? | Trace | Log | Metric | Bottleneck identification is key. |
| Did the deploy have an impact? | Metric | Log | Trace | Time-based comparison first. |

The important point: never stop at one signal. If metrics show an anomaly, open traces for the same time window, then confirm with logs via the trace_id. If logs reveal a cause, measure the blast radius with metrics to answer "how many users were affected."

## Correlation Field Design

Teams with weak signal linkage usually have inconsistent field names. Defining common fields ensures dashboards, log stores, and trace backends all point to the same request.

```python
import json
import time
from typing import Dict

COMMON_FIELDS = [
    "ts", "service", "env", "trace_id", "span_id", "request_id",
    "route", "status_code", "error_code"
]

def write_log(event: str, fields: Dict[str, object]) -> None:
    payload = {
        "ts": time.time(),
        "event": event,
        **fields,
    }
    print(json.dumps(payload, ensure_ascii=False))

write_log(
    "payment_failed",
    {
        "service": "checkout-api",
        "env": "prod",
        "trace_id": "9f3c1f9e...",
        "span_id": "5a8b...",
        "request_id": "req-42",
        "route": "/checkout",
        "status_code": 502,
        "error_code": "UPSTREAM_TIMEOUT",
    },
)
```

In operations, fixing field *semantics* matters more than adding field *count*. If different services use `requestId`, `req_id`, and `rid` for the same concept, query templates cannot be reused. Define a team-wide field dictionary first, then require new services to follow it.

## Three Signals Compared: Decision Perspective

| Signal | Strength | Weakness | Cost Risk | Practical Guidance |
| --- | --- | --- | --- | --- |
| Metric | Fast aggregation, wide surveillance | Lacks event context | High-cardinality labels | Default signal for symptom detection |
| Log | Failure cause, domain context | Storage growth, search cost | Verbose bodies, PII exposure | Core signal for explaining *why* |
| Trace | Request path, bottleneck location | Expensive without sampling | 100% storage, attribute bloat | Core signal for bottleneck analysis |

As operational maturity grows, each signal's question domain becomes sharper. For example: "p95 rose" → metric team's concern; "which span stretched" → trace team's concern; "why did it timeout" → log team's concern. Clear role separation shortens meetings.

## How This Shows Up in Production

Most teams use a three-step pattern: *metrics for alerts*, *logs for debugging*, *traces for finding the responsible service*. A setup that stores the same information three times does not survive long. The moment you separate question domains, cost and response time both drop.

What senior engineers look at first is the *boundary*. When there is agreement on which questions go to metrics, which to logs, and which deserve deep traces, signal design stays stable even as the system grows.

Teams whose log volume keeps exploding especially need clear signal boundaries. For example: record request *count* in metrics, record request *body* in logs. Without this separation, everything goes to the log store, search time grows, and monthly bills surprise you.

Here is a practical boundary heuristic:

- **Aggregatable numbers** → metrics.
- **Data needing individual event context** → logs.
- **Request paths and per-segment durations** → traces.
- **High-volume data that fits none of the above** → data warehouse (separate pipeline).

## How a Senior Engineer Thinks

- *The three signals have *different question domains*. They are not substitutes.*
- *Cardinality is *tax*.*
- *p99 dwarfs the average.*
- *Without *trace_id* you cannot untangle a distributed system.*
- *Sampling is *not shameful*; it is cost control.*

## Checklist

- [ ] You can distinguish *counter, gauge, histogram*.
- [ ] You know what *cardinality* means.
- [ ] You understand the role of *trace_id*.
- [ ] You can *decide* which signal answers a question.

## Practice Problems

1. Give three examples each of *counter* and *gauge*.
2. Describe a case where the average *hides p99*.
3. Sketch the *trace_id* flow for one request through *three services*.

## Wrap-up and Next Steps

The three signals are tools with *different boundaries*. Next we look at *collecting and visualizing metrics*.

## Answering the Opening Questions

- **What questions do metrics, logs, and traces each answer?**
  - Metrics answer trends (how much, since when), logs answer event context (why it failed, which order), and traces show the entire request path (which hop was slow). No single signal is complete alone.
- **How do the data shapes of the three signals differ?**
  - Metrics are numeric time-series only; logs carry contextual key-value data; traces maintain flow continuity across services via parent-child spans. Each shape determines what questions you can ask.
- **Where do cardinality and cost grow?**
  - More label values create more metric series, and more series means higher memory and processing cost. Longer retention multiplies storage cost. Design with cost in mind from the start and keep label cardinality minimal.
<!-- toc:begin -->
## In this series

- [Observability 101 (1/10): What Is Observability?](./01-what-is-observability.md)
- **Metrics, Logs, and Traces (current)**
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

- [Prometheus metric types](https://prometheus.io/docs/concepts/metric_types/)
- [Structured logging](https://www.datadoghq.com/blog/structured-logging/)
- [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [Histograms vs averages](https://prometheus.io/docs/practices/histograms/)
- [PromQL basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)

Tags: Observability, Metrics, Logging, Tracing, SRE

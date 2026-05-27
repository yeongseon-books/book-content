---
series: serverless-101
episode: 8
title: "Serverless 101 (8/10): Observability"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Serverless
  - Observability
  - Logging
  - Tracing
  - Metrics
seo_description: A beginner-friendly tour of serverless observability covering logs, metrics, distributed tracing, correlation IDs, and cost-aware sampling.
last_reviewed: '2026-05-04'
---

# Serverless 101 (8/10): Observability

Serverless systems are short-lived and distributed. One user request may cross multiple functions, queues, and data stores before it finishes. That is why “just look at the logs” stops working earlier than many teams expect.

Observability is the discipline that turns those short-lived hops into something you can still debug. In serverless, that means connecting logs, metrics, and traces well enough that you can reconstruct what happened after the fact.

This is the 8th post in the Serverless 101 series.


![serverless 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/08/08-01-concept-at-a-glance.en.png)
*serverless 101 chapter 8 flow overview*
> In serverless you cannot SSH into a box — observability is the only window into what your code did, and it has to be built in before something goes wrong.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Observability?
- Which signal should the example or diagram make visible for Observability?
- What failure should be prevented first when Observability reaches a real system?

## What You Will Learn

- the *three legs* of observability
- *correlation IDs*
- distinguishing *cold vs warm*
- *cost-aware* logging
- *dashboard / alarm* design

## Why It Matters

In a long-lived server process, one log stream can sometimes carry enough context. In a serverless system, execution hops between environments and often crosses asynchronous boundaries. If you do not preserve correlation across those boundaries, you are left with symptoms but not a path.

Observability is also a cost design problem. What you log, how long you retain it, where you sample traces, and which metrics power alerts all change both your debugging speed and your bill.

The point is not to collect three disconnected signal types. The point is to connect them so a single slow request can be traced through logs, metrics, and spans without guesswork.

## Key Terms

- **structured log**: *machine-readable* (e.g., JSON).
- **metric**: a *numeric* signal.
- **trace**: the *path* of a *request*.
- **correlation id**: a *request identifier*.
- **sampling**: balance of *cost* and *resolution*.

## Before/After

**Before**: tracing *plain logs* with *grep*.

**After**: *correlation id* + *trace* leads to *root cause* in *5 minutes*.

## Hands-on: Observability Basics

### Step 1 — Structured logging

```python
import json, time

def log(level, msg, **fields):
    print(json.dumps({"t": time.time(), "level": level, "msg": msg, **fields}))
```

### Step 2 — Propagate correlation id

```python
def with_corr(handler):
    def wrap(event, ctx):
        cid = event.get("correlation_id", "unknown")
        log("info", "start", cid=cid)
        return handler(event, ctx)
    return wrap
```

### Step 3 — Metric counts

```python
metrics = {}
def incr(name, n=1):
    metrics[name] = metrics.get(name, 0) + n
```

### Step 4 — Trace span (pseudo)

```python
import contextlib, time

@contextlib.contextmanager
def span(name):
    t0 = time.perf_counter()
    yield
    log("info", "span", name=name, ms=(time.perf_counter() - t0) * 1000)
```

### Step 5 — Mark cold

```python
COLD = True

def handler(event, ctx):
    global COLD
    log("info", "invoke", cold=COLD)
    COLD = False
```

## Verification Workflow

Once the basics are wired in, verify that the signals can answer a real question end to end.

```text
request_id=8d6...
correlation_id=ord-2026-05-12-001
cold=true
duration_ms=842
downstream=db
```

**Output:** one request should be traceable across the edge function, queue consumer, and downstream call with the same correlation key.

If you cannot answer these four questions quickly, the instrumentation is still too weak:

- Which request failed first?
- Was the delay caused by cold start or downstream latency?
- Which function retried, and how many times?
- Did the alert point to an actionable symptom or just to noise?

## What to Notice in This Code

- *Structured logs* enable *aggregation*.
- *Every function* must *propagate* the *correlation id*.
- The *cold flag* is core to *p99 analysis*.

## Five Common Mistakes

1. **Using *plain text* logs.**
2. **Logging *sensitive data*.**
3. **Watching only *logs* and ignoring *metrics*.**
4. **Letting *traces* explode in *cost* without *sampling*.**
5. **Setting *too many alarms*.**

## How This Shows Up in Production

A standard like *OpenTelemetry* unifies the *three signals* into *one backend* viewable on *one screen*.

## How a Senior Engineer Thinks

- Plan *observability* from *design*.
- *Correlation* is the *lifeline*.
- *Observe cost* too.
- *Alarms* must be *actionable*.
- *Sampling* balances *resolution* and *cost*.

## Checklist

- [ ] *Structured logging*.
- [ ] *Correlation id* propagated.
- [ ] *Metrics + traces* collected.
- [ ] *Alarms* are actionable.

## Practice Problems

1. In one line, what the *three legs* are.
2. In one line, the *role* of a *correlation id*.
3. In one line, the *purpose* of *trace sampling*.

## Wrap-up and Next Steps

Next, we cover *Cost*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Observability?**
  - The article treats Observability as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Observability?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Observability reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Serverless 101 (1/10): What is Serverless?](./01-what-is-serverless.md)
- [Serverless 101 (2/10): Function as a Service](./02-function-as-a-service.md)
- [Serverless 101 (3/10): Trigger and Event](./03-trigger-and-event.md)
- [Serverless 101 (4/10): Cold Start](./04-cold-start.md)
- [Serverless 101 (5/10): Scaling](./05-scaling.md)
- [Serverless 101 (6/10): State Management](./06-state-management.md)
- [Serverless 101 (7/10): Queue and Event-driven Architecture](./07-queue-and-event-driven.md)
- **Observability (current)**
- Cost (upcoming)
- Designing a Serverless App (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [OpenTelemetry documentation](https://opentelemetry.io/docs/)
- [AWS X-Ray developer guide](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html)
- [CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html)

### Patterns and Code

- [Distributed tracing in serverless](https://aws.amazon.com/blogs/compute/instrumenting-distributed-systems-for-operational-visibility/)
- [AWS Powertools for Lambda Python (GitHub)](https://github.com/aws-powertools/powertools-lambda-python)

Tags: Serverless, Observability, Logging, Tracing, Metrics

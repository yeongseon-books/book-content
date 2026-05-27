---
series: serverless-101
episode: 4
title: "Serverless 101 (4/10): Cold Start"
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
  - ColdStart
  - Performance
  - Latency
  - Cloud
seo_description: A beginner-friendly tour of cold start in serverless covering causes, measurement, package size, provisioning, and language choice.
last_reviewed: '2026-05-04'
---

# Serverless 101 (4/10): Cold Start

You usually notice *cold start* from the outside first. A function that feels fast most of the time suddenly takes seconds on the first request after idle time, during a burst, or right after deployment. The average looks fine, but the user experience does not.

That is why cold start is one of the earliest serverless topics worth understanding well. It shapes *p99 latency*, user-visible reliability, and the cost you are willing to pay to keep latency stable.

This is the 4th post in the Serverless 101 series.


![serverless 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/04/04-01-concept-at-a-glance.en.png)
*serverless 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Cold Start?
- Which signal should the example or diagram make visible for Cold Start?
- What failure should be prevented first when Cold Start reaches a real system?

## What You Will Learn

- the definition of *Cold Start*
- the *causes* broken down
- how to *measure* it
- *mitigation strategies*
- when to *accept* it

## Why It Matters

Cold start is not just “sometimes slower.” On login, payment, webhook, or synchronous API paths, a few cold invocations can dominate the latency story that users actually feel.

The trap is that averages hide the problem. If warm invocations are common, the mean looks healthy while the tail still hurts real traffic. That makes cold start less of a micro-optimization topic and more of a design decision about where latency matters enough to spend money.

This diagram matters because it shows that *cold start* is not one delay. It is the sum of multiple delays: environment creation, runtime initialization, dependency loading, and your own startup code. The mitigation strategy changes depending on which of those dominates.

## Key Terms

- **cold start**: *initialization latency* on the *first run*.
- **warm**: a *reused* container.
- **provisioned concurrency**: *pre-warmed* instances.
- **init code**: code *outside* the *handler*.
- **package size**: scales with *load time*.

## Before/After

**Before**: *p99 5s* spikes during *peaks*.

**After**: *provisioning* + *lean package* yields a *stable p99*.

## Hands-on: Measure and Mitigate

### Step 1 — Measure init time

```python
import time

t0 = time.perf_counter()
# heavy import here

INIT_MS = (time.perf_counter() - t0) * 1000

def handler(event, context):
    return {"init_ms": INIT_MS}
```

### Step 2 — Trim the package

```python
def lean_requirements(reqs):
    return [r for r in reqs if r not in {"pandas", "numpy"} or r in {"required"}]
```

### Step 3 — Global cache

```python
_client = None

def get_client():
    global _client
    if _client is None:
        _client = build_client()
    return _client

def build_client():
    return {"ready": True}
```

### Step 4 — Provisioning (pseudo)

```python
"""
provisioned_concurrency:
  function: web
  min: 5
"""
```

### Step 5 — Track p50/p95/p99

```python
def percentile(values, p):
    s = sorted(values)
    return s[int(len(s) * p) - 1]
```

## Verification Workflow

When you suspect cold-start regressions, measure them in a way that separates initialization from steady-state work.

```bash
# hit the function once after an idle window
curl -s https://example.com/hello

# hit it again immediately
curl -s https://example.com/hello
```

**Expected output:** the second call should usually be faster than the first if the platform reused a warm environment.

Then compare platform logs or traces with these questions in mind:

- Did the runtime create a fresh environment?
- Did dependency loading dominate the delay?
- Did your own initialization code do more work than the business logic?

If the first request is consistently slow even after package trimming, that is the moment to evaluate provisioned concurrency rather than guessing from averages.

## What to Notice in This Code

- Code *outside the handler* runs *only once* on cold.
- Reusing a *global client* is *core to warming*.
- *Provisioning* trades *cost* for *latency*.

## Five Common Mistakes

1. **Watching *averages* and ignoring *p99*.**
2. **Creating a *client* inside the *handler* every time.**
3. **Pulling in *heavy dependencies* unguarded.**
4. **Treating *provisioning* as the *default*.**
5. **Ignoring the *cold-start cost* of the *language*.**

## How This Shows Up in Production

Use *provisioning* on *latency-sensitive* paths like *payments, login*; *accept* cold for *internal jobs*.

## How a Senior Engineer Thinks

- *Manage* cold rather than *eliminate* it.
- *p99* is the *truth*.
- *Lean dependencies* are the *best weapon*.
- *Provisioning* is the *last card*.
- *Language choice* affects *cold*.

## Checklist

- [ ] *p99* tracked.
- [ ] *Global cache* used.
- [ ] *Package size* monitored.
- [ ] *Provisioning* cost reviewed.

## Practice Problems

1. In one line, the difference between *cold* and *warm*.
2. In one line, the *cost* of *provisioning*.
3. In one line, what *handler-external code* means.

## Wrap-up and Next Steps

Next, we look at *Scaling* and the *concurrency model*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Cold Start?**
  - The article treats Cold Start as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Cold Start?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Cold Start reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Serverless 101 (1/10): What is Serverless?](./01-what-is-serverless.md)
- [Serverless 101 (2/10): Function as a Service](./02-function-as-a-service.md)
- [Serverless 101 (3/10): Trigger and Event](./03-trigger-and-event.md)
- **Cold Start (current)**
- Scaling (upcoming)
- State Management (upcoming)
- Queue and Event-driven Architecture (upcoming)
- Observability (upcoming)
- Cost (upcoming)
- Designing a Serverless App (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [AWS Lambda runtime environment](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html)
- [AWS Lambda Provisioned Concurrency](https://docs.aws.amazon.com/lambda/latest/dg/provisioned-concurrency.html)
- [AWS Lambda best practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [AWS Lambda SnapStart](https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html)

### Code and Related Reading

- [AWS Lambda power tuning (GitHub)](https://github.com/alexcasalboni/aws-lambda-power-tuning)
- [Azure Functions 101](../../azure-functions-101/en/)

Tags: Serverless, ColdStart, Performance, Latency, Cloud

---
series: serverless-101
episode: 5
title: "Serverless 101 (5/10): Scaling"
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
  - Scaling
  - Concurrency
  - Throttling
  - Cloud
seo_description: A beginner-friendly tour of serverless scaling covering concurrency, burst limits, reserved concurrency, downstream protection, and backpressure.
last_reviewed: '2026-05-04'
---

# Serverless 101 (5/10): Scaling

Serverless often gets introduced with a seductive sentence: “it scales automatically.” That is directionally true, but in production it is also one of the most dangerous half-truths. Functions may scale quickly while the database, queue consumers, and third-party APIs behind them remain finite.

That means scaling is not just a story about how far the platform can stretch. It is a story about how much downstream pressure your system can survive without turning a traffic spike into a reliability incident.

This is post 5 in the Serverless 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Scaling?
- Which signal should the example or diagram make visible for Scaling?
- What failure should be prevented first when Scaling reaches a real system?

## Big Picture

![serverless 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/05/05-01-concept-at-a-glance.en.png)

*serverless 101 chapter 5 flow overview*

This picture places Scaling inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- the *concurrency* model
- *burst* vs *sustained* limits
- *reserved/limited concurrency*
- *downstream protection*
- *backpressure* patterns

## Why It Matters

Serverless is strong at horizontal expansion, but that strength becomes a liability if you measure only function throughput. A rapid increase in concurrency can exhaust database connections, hit third-party API limits, or starve peer functions that share the same account-level budget.

That is why experienced operators treat concurrency like a budget. The point is not to remove every limit. The point is to place limits deliberately so that the whole system stays healthy.

The most important part of this diagram is what happens *after* the functions scale out. Good serverless scaling is not about making the left side infinitely elastic. It is about making sure the right side can absorb the parallelism safely.

## Key Terms

- **concurrency**: number of *parallel* *instances*.
- **burst limit**: cap on *short-window* growth.
- **reserved concurrency**: a *fixed* allocation per *function*.
- **throttling**: *rejecting* calls beyond the *limit*.
- **backpressure**: *downstream* pushing back on *demand*.

## Before/After

**Before**: *huge call volume* exhausts *DB connections*.

**After**: *reserved concurrency* + *queue buffering* yield *flow control*.

## Hands-on: Scaling and Protection

### Step 1 — Estimate concurrency

```python
def concurrency(rps, duration_s):
    return rps * duration_s
```

### Step 2 — Burst simulation

```python
import concurrent.futures as cf

def burst(call, n):
    with cf.ThreadPoolExecutor(max_workers=n) as ex:
        list(ex.map(lambda i: call(i), range(n)))
```

### Step 3 — Reserved concurrency (pseudo)

```python
"""
reserved_concurrency:
  function: web
  value: 50
"""
```

### Step 4 — Queue buffering

```python
def enqueue(queue, msg):
    queue.append(msg)

def drain(queue, handler, batch=10):
    chunk, queue[:] = queue[:batch], queue[batch:]
    for m in chunk:
        handler(m, None)
```

### Step 5 — Backpressure

```python
def backoff(attempt):
    return min(2 ** attempt, 30)
```

## Failure-mode Walkthrough

The usual scaling failure is not “the platform refused to scale.” It is “the platform scaled faster than the downstream system could handle.” A simple first-pass check looks like this:

| Signal | What to inspect first | Typical mitigation |
| --- | --- | --- |
| Database timeouts | connection pool saturation | reserved concurrency, queue buffering |
| 429 from external API | vendor rate limit | backoff, token bucket, async buffering |
| Peer function slowdown | shared account concurrency | reserved concurrency per critical path |
| Queue age growing | workers too slow for arrival rate | more worker budget, smaller batch, faster handler |

The pattern is consistent: front-door elasticity is only useful when you also control the rate at which work reaches fragile dependencies.

## What to Notice in This Code

- *Reserved concurrency* protects the *DB*.
- *Queues* absorb *shock*.
- *Backoff* prevents *retry storms*.

## Five Common Mistakes

1. **Leaving the *DB connection pool* unprotected.**
2. **Treating *burst* as *sustained*.**
3. **Ignoring the *rate limit* of *external APIs*.**
4. **Skipping *reserved concurrency*, starving *peer functions*.**
5. **Retrying *immediately* without *backoff*.**

## How This Shows Up in Production

A *queue* absorbs the *spike* and *functions* with *reserved concurrency* drain it while protecting the *DB*.

## How a Senior Engineer Thinks

- The *cost* of *horizontal scale* is paid by *downstream*.
- *Backpressure* is a *base pattern*.
- *Concurrency limits* are a *budget*.
- *Queues* buy *time*.
- Watch *peer-function starvation*.

## Checklist

- [ ] *DB* protection strategy.
- [ ] *Reserved concurrency* reviewed.
- [ ] *Backoff* in place.
- [ ] *External API* limits known.

## Practice Problems

1. In one line, the *purpose* of *reserved concurrency*.
2. In one line, the meaning of *backpressure*.
3. In one line, the *effect* of *queue buffering*.

## Wrap-up and Next Steps

Next, we cover *State Management*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Scaling?**
  - The article treats Scaling as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Scaling?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Scaling reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Serverless 101 (1/10): What is Serverless?](./01-what-is-serverless.md)
- [Serverless 101 (2/10): Function as a Service](./02-function-as-a-service.md)
- [Serverless 101 (3/10): Trigger and Event](./03-trigger-and-event.md)
- [Serverless 101 (4/10): Cold Start](./04-cold-start.md)
- **Scaling (current)**
- State Management (upcoming)
- Queue and Event-driven Architecture (upcoming)
- Observability (upcoming)
- Cost (upcoming)
- Designing a Serverless App (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [AWS Lambda concurrency](https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html)
- [AWS Lambda reserved and provisioned concurrency](https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html)
- [Amazon SQS developer guide](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [AWS Lambda scaling behavior](https://docs.aws.amazon.com/lambda/latest/dg/invocation-scaling.html)

### Patterns and Code

- [AWS Lambda power tuning (GitHub)](https://github.com/alexcasalboni/aws-lambda-power-tuning)
- [Serverless patterns collection](https://serverlessland.com/patterns)

Tags: Serverless, Scaling, Concurrency, Throttling, Cloud

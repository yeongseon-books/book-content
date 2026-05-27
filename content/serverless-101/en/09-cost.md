---
series: serverless-101
episode: 9
title: "Serverless 101 (9/10): Cost"
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
  - Cost
  - FinOps
  - Pricing
  - Cloud
seo_description: A beginner-friendly guide to serverless cost components, invocation pricing, GB-seconds, data transfer, and FinOps strategies for sustainable savings
last_reviewed: '2026-05-04'
---

# Serverless 101 (9/10): Cost

Serverless often gets sold with the easiest line item to quote: the price per invocation. That number is memorable, but it rarely explains the bill you eventually pay. What surprises teams is usually everything wrapped around the call count.

Duration, memory, data transfer, provisioned capacity, and downstream managed services all shape the real total. Once traffic grows, the architecture decisions behind those numbers matter more than the tiny unit price that looked so attractive on day one.

This is the 9th post in the Serverless 101 series.


![serverless 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/09/09-01-concept-at-a-glance.en.png)
*serverless 101 chapter 9 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Cost?
- Which signal should the example or diagram make visible for Cost?
- What failure should be prevented first when Cost reaches a real system?

## What You Will Learn

- The *cost components* of serverless
- The effect of *memory tuning*
- The hidden cost of *data transfer*
- The cost of *idle* provisioning
- A starting point for *FinOps*

## Why It Matters

Serverless is not automatically cheaper. It can be extremely efficient for short and bursty work, and surprisingly expensive for long-running, high-volume, or network-heavy workloads.

That is why cost belongs in architecture review, not just in monthly reporting. The same feature can land in a very different cost envelope depending on memory size, downstream calls, egress, and whether you pay an idle tax for provisioned capacity.

The useful lesson in this diagram is that the bill is a composition of multiple behaviors. Optimizing only call volume or only code runtime is rarely enough.

## Key Terms

- **invocation cost**: price *per call*.
- **GB-seconds**: *memory × duration*.
- **egress**: *outbound data transfer*.
- **idle**: the cost of *provisioned* capacity sitting unused.
- **unit economics**: *margin per call*.

## Before/After

**Before**: estimate cost from the *per-call price* alone.

**After**: compare alternatives using a *total cost of ownership* model.

## Hands-on: Modeling Cost

The constants in the sample below are an **AWS Lambda pricing example**, not a provider-neutral serverless default. Azure Functions and Google Cloud Functions use different pricing rules, free tiers, and billing details, so treat the numbers as one worked example rather than a universal formula.

### Step 1 — Invocation cost (AWS Lambda example)

```python
def calls_cost(n, unit_price=0.0000002):
    return n * unit_price
```

### Step 2 — GB-seconds

```python
def gb_seconds(memory_mb, duration_ms, n):
    return (memory_mb / 1024) * (duration_ms / 1000) * n
```

### Step 3 — Egress (example rate)

```python
def egress_cost(gb, price_per_gb=0.09):
    return gb * price_per_gb
```

### Step 4 — Scenario comparison (AWS-shaped sample)

```python
def total(n, mem_mb, dur_ms, gb_out):
    return (
        calls_cost(n)
        + gb_seconds(mem_mb, dur_ms, n) * 0.0000166667
        + egress_cost(gb_out)
    )
```

### Step 5 — Memory tuning sweep

```python
sizes = [128, 256, 512, 1024]
for s in sizes:
    print(s, total(1_000_000, s, 200, 5))
```

## Scenario Review

Before choosing a cost posture, compare at least two realistic operating scenarios.

| Scenario | What usually dominates | First question to ask |
| --- | --- | --- |
| Spiky low-volume API | invocation + tail latency mitigation | do we need provisioned capacity? |
| High-volume short jobs | memory × duration | can memory tuning cut runtime enough to win overall? |
| Media-heavy responses | egress | can CDN or object storage reduce outbound traffic? |
| Async pipeline | downstream services | which queue, database, and retry costs grow with traffic? |

This keeps the discussion anchored in workload shape instead of in isolated pricing units.

## What to Notice in This Code

- The numeric constants are **provider-specific example values**, not universal serverless defaults.
- *Memory* sets both *CPU* and *cost*.
- *Data transfer* is a *hidden* line item.
- Compare alternatives at the *scenario* level, not the unit level.

## Five Common Mistakes

1. **Treating one provider's published constants as if they were generic *serverless* defaults.**
2. **Pinning *memory* at the *minimum* without measuring duration.**
3. **Ignoring *egress*.**
4. **Forgetting *DB* and *queue* charges.**
5. **Using *provisioned concurrency* without tracking its *idle cost*.**

## How This Shows Up in Production

A *FinOps* team feeds *margin per call* back into *product decisions* — pricing, feature scope, and SLAs.

## How a Senior Engineer Thinks

- *Cost* is part of the *feature*.
- *Memory tuning* is a *time-vs-money* trade.
- *Egress* is solved by *network design*, not code.
- *Idle* is a *tax* on *provisioned* capacity.
- Compare *alternatives* on a *fair* basis.

## Checklist

- [ ] *Total cost model* in place.
- [ ] *Memory tuning* reviewed.
- [ ] *Egress* measured.
- [ ] *FinOps* dashboard live.

## Practice Problems

1. Define *GB-seconds* in one line.
2. Define *egress* in one line.
3. Define the *idle cost* of *provisioned concurrency* in one line.

## Wrap-up and Next Steps

The final episode is *Designing a Serverless App*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Cost?**
  - The article treats Cost as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Cost?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Cost reaches a real system?**
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
- [Serverless 101 (8/10): Observability](./08-observability.md)
- **Cost (current)**
- Designing a Serverless App (upcoming)

<!-- toc:end -->

## References

### Official Pricing Docs

- [AWS Lambda pricing](https://aws.amazon.com/lambda/pricing/)
- [Google Cloud Functions pricing](https://cloud.google.com/functions/pricing)
- [Azure Functions pricing](https://azure.microsoft.com/pricing/details/functions/)

### FinOps and Related Reading

- [FinOps Foundation](https://www.finops.org/)
- [AWS Lambda power tuning (GitHub)](https://github.com/alexcasalboni/aws-lambda-power-tuning)

Tags: Serverless, Cost, FinOps, Pricing, Cloud

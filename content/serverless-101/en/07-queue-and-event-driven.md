---
series: serverless-101
episode: 7
title: "Serverless 101 (7/10): Queue and Event-driven Architecture"
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
  - Queue
  - EventDriven
  - PubSub
  - Cloud
seo_description: A beginner-friendly tour of queues and event-driven architecture covering decoupling, fan-out, FIFO, retries, and DLQs.
last_reviewed: '2026-05-04'
---

# Serverless 101 (7/10): Queue and Event-driven Architecture

As systems grow, what gets heavy first is often not the code but the connections between services. A synchronous chain can look simple on a quiet day and turn brittle as soon as one dependency slows down or fails.

Queues and event buses help because they separate responsibilities in both time and failure scope. In a serverless system, that separation is often what keeps a short function from turning into a long, fragile request path.

This is post 7 in the Serverless 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Queue and Event-driven Architecture?
- Which signal should the example or diagram make visible for Queue and Event-driven Architecture?
- What failure should be prevented first when Queue and Event-driven Architecture reaches a real system?

## Big Picture

![serverless 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/07/07-01-concept-at-a-glance.en.png)

*serverless 101 chapter 7 flow overview*

This picture places Queue and Event-driven Architecture inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- the meaning of *decoupling*
- *queue* vs *Pub/Sub*
- *fan-out* patterns
- *FIFO* and *ordering*
- *retries/DLQ*

## Why It Matters

When an order API directly calls payment, email, analytics, and inventory in sequence, one slow dependency stretches the whole response path. In a serverless environment, that also means more timeout risk, wider failure blast radius, and less flexibility about retries.

Async messaging changes that shape. It lets producers publish facts and lets consumers move at their own speed, with their own retry policy and their own failure handling.

The key value here is not that everything becomes asynchronous. It is that producers and consumers no longer need to know each other's internals. That lower coupling is what makes fan-out, isolated retries, and independent evolution practical.

## Key Terms

- **queue**: *1:1* or *competing consumers*.
- **topic**: *1:N* publish/subscribe.
- **fan-out**: *one event* → *many subscribers*.
- **FIFO**: *order-preserving* queue.
- **DLQ**: *isolation* for *failed messages*.

## Before/After

**Before**: *Order API* → *payment → email → analytics* synchronously.

**After**: publish *order events* to a *topic*; each *function* handles its part *independently*.

## Hands-on: Tiny Messaging

### Step 1 — In-memory queue

```python
from collections import deque
queue = deque()
def publish(msg): queue.append(msg)
def consume(): return queue.popleft() if queue else None
```

### Step 2 — Fan-out

```python
subs = []
def subscribe(fn): subs.append(fn)
def emit(event):
    for fn in subs:
        fn(event)
```

### Step 3 — Consumer functions

```python
def billing(event): print("bill", event)
def mail(event): print("mail", event)
```

### Step 4 — Retry and DLQ

```python
def retry(handler, dlq, attempts=3):
    def wrap(event):
        for i in range(attempts):
            try:
                return handler(event)
            except Exception:
                if i == attempts - 1:
                    dlq.append(event)
                    raise
    return wrap
```

### Step 5 — FIFO ordering key

```python
def fifo_key(order):
    return order["customer_id"]
```

## What to Notice in This Code

- *Fan-out* lowers *coupling*.
- A *FIFO key* defines the *order unit*.
- *DLQs* make *problems visible*.

## Five Common Mistakes

1. **Assuming *order* is needed *everywhere*.**
2. **Misunderstanding *competing-consumer* semantics.**
3. **Doing *fan-out* without *idempotency*.**
4. **Skipping *DLQ* setup.**
5. **Ignoring *message size* limits.**

## How This Shows Up in Production

Domain teams (*orders, billing, analytics*) are *loosely coupled* through an *event bus*.

## How a Senior Engineer Thinks

- *Event schemas* are *public APIs*.
- *Fan-out* helps with *org boundaries* too.
- *FIFO* is *expensive*.
- Pair *DLQ* with *alarms*.
- *Evolve* without *breaking compatibility*.

## Checklist

- [ ] *Event schema* documented.
- [ ] *DLQ* + alarm.
- [ ] *Idempotency* checked.
- [ ] *FIFO* need decided.

## Practice Problems

1. In one line, the difference between *queue* and *topic*.
2. In one line, the *benefit* of *fan-out*.
3. In one line, the *role* of a *FIFO key*.

## Wrap-up and Next Steps

Event-driven design is valuable because it separates time, responsibility, and failure handling. The best result is not “more messaging.” It is a system where independent work can stay independent under load and under failure.

Next, we cover *Observability*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Queue and Event-driven Architecture?**
  - The article treats Queue and Event-driven Architecture as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Queue and Event-driven Architecture?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Queue and Event-driven Architecture reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Serverless 101 (1/10): What is Serverless?](./01-what-is-serverless.md)
- [Serverless 101 (2/10): Function as a Service](./02-function-as-a-service.md)
- [Serverless 101 (3/10): Trigger and Event](./03-trigger-and-event.md)
- [Serverless 101 (4/10): Cold Start](./04-cold-start.md)
- [Serverless 101 (5/10): Scaling](./05-scaling.md)
- [Serverless 101 (6/10): State Management](./06-state-management.md)
- **Queue and Event-driven Architecture (current)**
- Observability (upcoming)
- Cost (upcoming)
- Designing a Serverless App (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [Amazon SQS developer guide](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [Amazon SNS developer guide](https://docs.aws.amazon.com/sns/latest/dg/welcome.html)
- [Amazon EventBridge overview](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html)

### Patterns and Related Reading

- [Event-driven architecture (Martin Fowler)](https://martinfowler.com/articles/201701-event-driven.html)
- [Serverless patterns collection](https://serverlessland.com/patterns)
- [AWS serverless samples (GitHub)](https://github.com/aws-samples/serverless-patterns)

Tags: Serverless, Queue, EventDriven, PubSub, Cloud

---
series: distributed-systems-101
episode: 8
title: "Distributed Systems 101 (8/10): Message Queues and Event Sourcing"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Distributed Systems
  - MessageQueue
  - EventSourcing
  - Kafka
  - CQRS
seo_description: We cover how message queues and event sourcing decouple distributed services and turn time and history into first-class tools.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (8/10): Message Queues and Event Sourcing

Direct calls force every participant to be healthy at the same moment. Queues and logs change that rule: one side can finish now, the other can catch up later, and the system can still preserve a trustworthy history.

This is post 8 in the Distributed Systems 101 series.

Here we use queues, offsets, and event logs to show how distributed systems turn time and replay into design tools rather than accidental side effects.

## Questions to Keep in Mind

- The decoupling and guarantees that a message queue provides?
- The meaning of at-most-once, at-least-once, and exactly-once?
- The definition of event sourcing and its relationship to CQRS?

## Big Picture

![distributed systems 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/08/08-01-concept-at-a-glance.en.png)

*distributed systems 101 chapter 8 flow overview*

This picture places Message Queues and Event Sourcing inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Message Queues and Event Sourcing is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why It Matters

Direct service-to-service calls strongly couple availability and latency. Put a queue in between and one side staying up does not depend on the other. Event sourcing goes one step further by defining state as the sum of events, making history and replay possible.

> Queues separate time. Events separate truth.

## Concept at a Glance

Producers write to the queue and consumers read at their own pace. A single message can be processed by several consumers.

## Key Terms

- **Message queue**: A middleman that stores and dispatches messages.
- **Event sourcing**: A pattern that represents state as the accumulation of events.
- **Offset**: A position pointing at how far a consumer has read.
- **Consumer group**: A unit that shares messages among its members.
- **Idempotency**: The property that processing the same message many times yields the same result.

## Before/After

**Before — direct calls**

```text
order -> payment -> inventory -> notify   (one death stops everything)
```

**After — separated by a queue**

```text
order -> queue
         -> payment consumer
         -> inventory consumer
         -> notify consumer
```

Each consumer works at its own pace; if it dies the queue holds the messages.

## Hands-on: Queues and Event Sourcing

### Step 1 — start with an in-memory queue

```python
# 1_queue.py
from collections import deque
q = deque()
def produce(msg): q.append(msg)
def consume():
    if q: return q.popleft()
```

The simplest in-memory queue. Later steps extend this idea to a distributed setting.

### Step 2 — durable queue (append-only log)

```python
# 2_log.py
import json
def produce(path, msg):
    with open(path, "a") as f: f.write(json.dumps(msg) + "\n")
def consume(path, offset):
    with open(path) as f:
        lines = f.readlines()
    return lines[offset], offset + 1
```

Once the queue becomes a file, messages survive a crash. This is the essence of Kafka.

### Step 3 — at-least-once + idempotent consumer

```python
# 3_idem.py
processed = set()
def consume_once(msg):
    if msg["id"] in processed: return "skip"
    processed.add(msg["id"])
    return "process"
```

Even if the queue delivers the same message twice it is safe — duplicates are filtered by ID.

### Step 4 — event sourcing reconstructs state

```python
# 4_event.py
events = [
    {"type": "deposit", "amount": 100},
    {"type": "withdraw", "amount": 30},
]
def balance(events):
    b = 0
    for e in events:
        if e["type"] == "deposit": b += e["amount"]
        elif e["type"] == "withdraw": b -= e["amount"]
    return b
print(balance(events))  # 70
```

Instead of storing state, compute it from the sum of events. Any past point can be reproduced.

### Step 5 — CQRS read model

```python
# 5_cqrs.py
read_model = {"balance": 0}
def project(event):
    if event["type"] == "deposit": read_model["balance"] += event["amount"]
    elif event["type"] == "withdraw": read_model["balance"] -= event["amount"]
```

Writes go through events; reads use a precomputed model. Splitting the two paths makes each easier to optimize.

## Operational walkthrough: consumer lag and replay recovery

The real operational test for a queue is what happens when consumers fall behind.

1. A producer keeps appending order events at 2,000 messages per second.
2. One consumer group instance restarts and stops committing offsets for three minutes.
3. Lag grows, but producers keep succeeding because the log boundary absorbs time.
4. The consumer returns, reads from the last committed offset, and replays the backlog.
5. Duplicate deliveries happen around the restart boundary, so the consumer's idempotency key decides whether recovery is safe.

This is why teams monitor lag, replay time, and offset-commit age as first-class metrics. Without those signals a queue can hide overload for a while, then suddenly convert it into stale read models or duplicated side effects.

## What to Notice in This Code

- The moment the queue becomes a file, the fate of messages changes — durability and replay.
- Exactly-once is not a property of the queue alone; it is "queue + idempotent consumer."
- In event sourcing the history is essence, snapshots are optimization.
- The read model is throwaway — it can be rebuilt from events anytime.

## Five Common Mistakes

1. **Believing exactly-once is guaranteed by the broker alone.** Consumer idempotency is required too.
2. **Using too many partitions.** Rebalance cost and metadata explosion.
3. **Treating events as mutable.** A written event is never edited.
4. **Replaying a million events every time without snapshots.** Periodic snapshots are necessary.
5. **Treating the read model as the source of truth.** Truth lives in the event log.

## How This Shows Up in Production

Kafka is the most widely used streaming backbone, a distributed append-only log. RabbitMQ and AWS SQS are traditional message queues. Event sourcing is often adopted in finance, order systems, and any domain with audit needs. CQRS suits systems where read and write workloads diverge significantly.

## How a Senior Engineer Thinks

- Before introducing a queue they confirm the flow can really be asynchronous.
- They design consumer idempotency before choosing the queue technology.
- They write down who commits the offset.
- They decide event-schema versioning from day one.
- They measure read-model rebuild time and put it in an SLO.

## Checklist

- [ ] Can you explain at-most-once / at-least-once / exactly-once in one line each?
- [ ] Can you say why event sourcing is strong for audit?
- [ ] Can you describe the relationship between consumer group and partition?
- [ ] Can you say why CQRS separates the read and write paths?
- [ ] Do you have one pattern in mind for guaranteeing idempotency?

## Practice Problems

1. Design an order system with event sourcing. Write the schema for five events.
2. Explain in a paragraph how at-least-once plus an idempotent consumer approximates exactly-once.
3. List two criteria you would use to decide the partition count in Kafka.

## Wrap-up and Next Steps

Queues and event sourcing are tools that handle time in distributed systems. Next we look at the difficulty of transactions across multiple nodes — distributed transactions — and the practical solutions that exist.

## Answering the Opening Questions

- **The decoupling and guarantees that a message queue provides?**
  - The article treats Message Queues and Event Sourcing as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **The meaning of at-most-once, at-least-once, and exactly-once?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The definition of event sourcing and its relationship to CQRS?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Distributed Systems 101 (1/10): What Is a Distributed System?](./01-what-is-a-distributed-system.md)
- [Distributed Systems 101 (2/10): Failure Models](./02-failure-model.md)
- [Distributed Systems 101 (3/10): RPC and Message Passing](./03-rpc-and-message-passing.md)
- [Distributed Systems 101 (4/10): Consistency and CAP](./04-consistency-and-cap.md)
- [Distributed Systems 101 (5/10): Replication](./05-replication.md)
- [Distributed Systems 101 (6/10): Consensus and Raft](./06-consensus-and-raft.md)
- [Distributed Systems 101 (7/10): Leader Election](./07-leader-election.md)
- **Message Queues and Event Sourcing (current)**
- Distributed Transactions (upcoming)
- Patterns for Operable Distributed Systems (upcoming)

<!-- toc:end -->

## References

- [Apache Kafka documentation](https://kafka.apache.org/documentation/)
- [Event Sourcing — Martin Fowler](https://martinfowler.com/eaaDev/EventSourcing.html)
- [CQRS — Martin Fowler](https://martinfowler.com/bliki/CQRS.html)
- [Designing Data-Intensive Applications — chapter 11](https://dataintensive.net/)
- [Kafka consumer design](https://docs.confluent.io/platform/current/clients/consumer.html)

Tags: Computer Science, Distributed Systems, MessageQueue, EventSourcing, Kafka, CQRS

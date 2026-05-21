---
series: distributed-systems-101
episode: 9
title: "Distributed Systems 101 (9/10): Distributed Transactions"
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
  - Transactions
  - TwoPhaseCommit
  - Saga
  - Idempotency
seo_description: We cover the difficulty of distributed transactions and the practical answers - 2PC, Saga, outbox, and idempotent operations - in short code.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (9/10): Distributed Transactions

The painful part of a distributed transaction is not the success path where every service behaves. It is the partial-failure path where one side committed, another side timed out, and the business still expects a single answer.

This is post 9 in the Distributed Systems 101 series.

Here we compare the heavyweight answer of 2PC with the more common production answers: Saga, outbox relay, and idempotent recovery.


![distributed systems 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/09/09-01-concept-at-a-glance.en.png)
*distributed systems 101 chapter 9 flow overview*

## Questions to Keep in Mind

- The difference between a single-node and a distributed transaction?
- How 2-phase commit works and where it falls short?
- The core of Saga — compensating transactions?

## Why It Matters

As microservices and multi-store architectures grow, "two systems in one transaction" appears more often. Single-DB ACID is far more expensive — sometimes impossible — across multiple nodes. Distributed transactions are essentially design under explicit tradeoffs.

> A distributed transaction is the design of "recoverable inconsistency," not an imitation of ACID.

The coordinator sends prepare to both, and only commits when both answer yes. That is 2PC.

## Key Terms

- **2PC**: A protocol that gathers consent from all participants in two phases (prepare, commit).
- **Saga**: A pattern that undoes a sequence of local transactions via compensation.
- **Compensation**: An action that semantically reverses a previously committed step.
- **Outbox**: A table that bundles the DB write and the message publish into the same transaction.
- **Idempotency**: The property that doing the same request many times produces the same result.

## Before/After

**Before — direct calls between services**

```text
service A succeeds / service B fails -> data inconsistency
```

**After — Saga + compensation**

```text
service A succeeds / service B fails -> compensate A -> consistent end state
```

In distributed systems "rollback" is not going back in time — it is adding a new event.

## Hands-on: Distributed Transaction Patterns

### Step 1 — single-DB transaction

```python
# 1_single.py
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE acct(id TEXT, bal INT)")
db.execute("INSERT INTO acct VALUES ('A', 100), ('B', 0)")
with db:
    db.execute("UPDATE acct SET bal=bal-30 WHERE id='A'")
    db.execute("UPDATE acct SET bal=bal+30 WHERE id='B'")
```

Inside one DB, ACID is enough. The hard parts begin from the next step.

### Step 2 — 2PC (pseudocode)

```python
# 2_2pc.py
def prepare(svc): return svc.prepare()    # yes/no
def commit(svc):  svc.commit()
def abort(svc):   svc.abort()
def two_pc(svcs):
    if all(prepare(s) for s in svcs):
        for s in svcs: commit(s)
    else:
        for s in svcs: abort(s)
```

Commit only if every participant says yes. If the coordinator dies, participants can hold locks indefinitely — timeouts are essential.

### Step 3 — Saga (compensation)

```python
# 3_saga.py
def book_flight():  return "F1"
def book_hotel():   raise RuntimeError("no room")
def cancel_flight(f): print(f"cancel {f}")

def saga():
    f = book_flight()
    try:
        h = book_hotel()
    except Exception:
        cancel_flight(f)
        raise
saga()
```

Each step is a local commit. On failure, you semantically undo what you already did.

### Step 4 — outbox pattern

```python
# 4_outbox.py (pseudocode)
# Inside one transaction:
#   INSERT INTO orders ...
#   INSERT INTO outbox(event=...) VALUES (...)
# A separate worker reads outbox and publishes to the message broker.
```

The DB write and the message publish ride in the same transaction, avoiding the dual-write problem.

### Step 5 — idempotent consumer

```python
# 5_idem.py
processed = set()
def apply(event):
    if event["id"] in processed: return
    processed.add(event["id"])
    # actual processing
```

The last safety net for distributed transactions. Even if the same message arrives twice, the result happens once.

## Operational walkthrough: order write succeeds, relay fails

One of the most common real incidents is not a broken database transaction but a broken handoff after the transaction commits.

1. The service writes `orders` and `outbox` rows in one local transaction.
2. The API returns `201 Created` to the caller.
3. The outbox relay crashes before publishing the message to Kafka.
4. On restart, the relay scans the outbox table, finds the unpublished row, and publishes it.
5. Downstream consumers may see the message twice if the relay crashed after publish but before marking the row as sent.

That is why the operational contract is "at-least-once publish plus idempotent consume," not "relay never fails." Outbox reduces the dual-write problem to a recoverable backlog problem, which is a much more survivable failure mode.

## What to Notice in This Code

- 2PC is strong but holds locks long and is fragile to coordinator failure.
- Saga fits environments where failures are common — the meaning of compensation is defined by the domain.
- Outbox turns "write to two systems at once" into a single DB write.
- Idempotency is the common foundation under every pattern.

## Five Common Mistakes

1. **Using 2PC by default in microservices.** Availability and performance drop sharply.
2. **Starting Saga without compensation.** Partial failures become permanent inconsistencies.
3. **Splitting message publish and DB write via dual-write.** You cannot guarantee both succeed together.
4. **Setting 2PC timeouts too short.** Frequent false aborts hurt the business.
5. **Forgetting idempotency.** A single retry can charge a customer twice.

## How This Shows Up in Production

XA/2PC still appears in RDBMS clusters and some brokers. Saga is the standard pattern in microservice payment and booking domains. Outbox is the most common workaround for distributed transactions in Kafka + DB stacks. Global cloud databases like Spanner and CockroachDB combine consensus and 2PC internally so that the user sees ACID.

## How a Senior Engineer Thinks

- They first ask, "Does this flow really need to be atomic?"
- Whenever possible they keep it inside a single DB transaction and use outbox to notify the world.
- They confirm with domain experts that Saga compensations are actually possible in business terms.
- Every failure branch ships with an operational automation script.
- They make idempotency keys a standard for every external call.

## Checklist

- [ ] Can you state the difference between 2PC and Saga in one line?
- [ ] Can you explain the problem the outbox pattern solves?
- [ ] Can you name one limitation of compensating transactions?
- [ ] Do you have a mental picture of where the idempotency key lives?
- [ ] Can you justify which pattern you'd pick for a payment flow?

## Practice Problems

1. Design a flight + hotel booking flow as a Saga and write the compensating steps.
2. Explain the difference between dual-write and the outbox pattern in a paragraph.
3. Construct a scenario where retrying a payment without an idempotency key is dangerous.

## Wrap-up and Next Steps

Distributed transactions are not about imitating ACID — they are about designing for "eventual agreement." In the final post we tie all the tools together into patterns for operable distributed systems.

## Answering the Opening Questions

- **The difference between a single-node and a distributed transaction?**
  - The article treats Distributed Transactions as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How 2-phase commit works and where it falls short?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The core of Saga — compensating transactions?**
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
- [Distributed Systems 101 (8/10): Message Queues and Event Sourcing](./08-message-queue-and-event-sourcing.md)
- **Distributed Transactions (current)**
- Patterns for Operable Distributed Systems (upcoming)

<!-- toc:end -->

## References

- [Two-phase commit — Wikipedia](https://en.wikipedia.org/wiki/Two-phase_commit_protocol)
- [Saga pattern — microservices.io](https://microservices.io/patterns/data/saga.html)
- [Transactional Outbox — microservices.io](https://microservices.io/patterns/data/transactional-outbox.html)
- [Designing Data-Intensive Applications — chapter 9](https://dataintensive.net/)
- [Life of a Cloud Spanner read-write transaction](https://cloud.google.com/spanner/docs/transactions)

Tags: Computer Science, Distributed Systems, Transactions, TwoPhaseCommit, Saga, Idempotency

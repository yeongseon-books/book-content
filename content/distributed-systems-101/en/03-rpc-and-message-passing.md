---
series: distributed-systems-101
episode: 3
title: RPC and Message Passing
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
  - RPC
  - Messaging
  - Async
  - Idempotency
seo_description: We compare two communication models between nodes — RPC and message passing — and the tradeoffs that decide where each fits.
last_reviewed: '2026-05-15'
---

# RPC and Message Passing

Once a system is split into services, the next hard question is no longer "what code should I write?" but "how should these parts talk?" The answer determines whether latency piles up in a synchronous chain or gets absorbed behind a queue boundary.

This is post 3 in the Distributed Systems 101 series.

Here we compare RPC and message passing as two different contracts: one optimized for immediate answers, the other for decoupling time, failure, and load.

## Questions this chapter answers

- The definitions and differences of RPC and message passing
- Synchronous vs asynchronous, request/response vs publish/subscribe
- Strengths and weaknesses of each model and where each fits
- What "function-like" RPC quietly hides
- Patterns for blending the two

## Why It Matters

Once you split services, the next decision is "how do they talk?" That decision drives latency budgets, blast radius, and operational complexity. Picking poorly creates RPC chains that take down the whole system when one node slows, or message flows you cannot trace.

> The communication model decides system coupling.

## Concept at a Glance

![RPC and message-passing communication models](../../../assets/distributed-systems-101/03/03-01-concept-at-a-glance.en.png)

*RPC and message-passing communication models*

RPC is a two-way contract. Message passing is a one-way flow with an intermediary store.

## Key Terms

- **RPC (Remote Procedure Call)**: Call a remote function as if it were local. gRPC, JSON-RPC.
- **Message passing**: A producer drops a message in a broker and a consumer picks it up. Kafka, RabbitMQ.
- **Synchronous**: Wait for the response.
- **Asynchronous**: Do not wait for the response.
- **At-least-once / exactly-once**: Delivery guarantees a broker may offer.

## Before/After

**Before — every call is RPC**

```text
service A -> B -> C -> D: if D slows down, A's response slows
```

**After — important boundaries use messaging**

```text
A drops a message and returns; D processes asynchronously
```

You gain blast-radius isolation and a tighter latency budget.

## Hands-on: Both Models on One Screen

### Step 1 — RPC (FastAPI)

```python
# 1_rpc_server.py
from fastapi import FastAPI
app = FastAPI()
@app.post("/charge")
def charge(amount: int):
    # process payment synchronously
    return {"ok": True, "id": "txn_1"}
```

```python
# 1_rpc_client.py
import requests
r = requests.post("http://127.0.0.1:8000/charge", json={"amount": 100}, timeout=2)
print(r.json())
```

The next line runs only after the response arrives. Almost identical to a function call.

### Step 2 — Message passing (in-memory queue)

```python
# 2_queue.py
from queue import Queue
import threading, time

q = Queue()

def consumer():
    while True:
        msg = q.get()
        time.sleep(0.5)
        print("processed:", msg)

threading.Thread(target=consumer, daemon=True).start()
q.put({"amount": 100, "id": "txn_1"})
print("producer returned immediately")
```

The producer returns instantly. The consumer drains at its own pace.

### Step 3 — Risk of an RPC chain

```python
# 3_chain.py (pseudocode)
def order():
    inv = rpc_inventory()    # 100ms
    pay = rpc_payment()      # 200ms
    ship = rpc_shipping()    # 150ms
    return ok                # total 450ms plus retry/timeout
```

Every step must be alive for a response to come back. One slow node slows the whole call.

### Step 4 — Decouple with async + queue

```python
# 4_async.py (pseudocode)
def order():
    save_order_local()
    publish("order.created", payload)
    return "accepted"  # respond immediately
# separate workers handle inventory/payment/shipping
```

The user sees a fast response and is shielded from a slow downstream step.

### Step 5 — Delivery guarantees

```python
# 5_dedup.py
seen = set()
def consume(msg):
    if msg["id"] in seen:
        return  # idempotent: ignore duplicates
    seen.add(msg["id"])
    process(msg)
```

Most brokers offer at-least-once. The consumer absorbs duplicates with an idempotency key.

## What to Notice in This Code

- RPC's wait creates strong coupling.
- Message passing fits work that does not need to happen now.
- Deeper chains make RPC riskier.
- Exactly-once is almost always a fiction; idempotent consumers are the answer.

## Five Common Mistakes

1. **Making everything RPC.** Chains explode in latency and failure surface.
2. **Making everything queue-based.** User-facing flows that need a synchronous answer suffer in UX.
3. **Believing exactly-once.** Reality is broker guarantee plus idempotent consumer.
4. **Skipping idempotency keys.** A retry can double-charge a customer.
5. **Putting timeouts and retries only on the client.** You also need a DLQ and retry policy on the broker.

## How This Shows Up in Production

User paths that need an immediate answer go through RPC. Long work (sending email, generating receipts, analytics) goes through queues. Microservices commonly split modules within a company by RPC and domain boundaries by messages. Event sourcing and CQRS push the message model all the way.

## How a Senior Engineer Thinks

- They first ask, "do we really need a synchronous answer?"
- They cap chain depth (for example, no more than three).
- They embed idempotency keys from the first commit.
- They assume brokers are at-least-once.
- They treat DLQs and retry policy as operational responsibilities.

## Checklist

- [ ] Can you state the difference between RPC and message passing in one line?
- [ ] Can you explain why deep RPC chains are dangerous?
- [ ] Do you know what at-least-once and exactly-once mean?
- [ ] Have you designed an idempotency key?
- [ ] Can you say what a DLQ is and when to use it?

## Practice Problems

1. Find one call in your service worth converting from RPC to a message and explain why.
2. In one paragraph, describe a payment API that uses idempotency keys.
3. List three conditions a consumer must meet to be safe under at-least-once delivery.

## Wrap-up and Next Steps

RPC and message passing trade off sync/async, coupling, and resilience. Next we tackle the biggest tradeoff that appears the moment data lives on multiple nodes: consistency and CAP.

<!-- toc:begin -->
- [What Is a Distributed System?](./01-what-is-a-distributed-system.md)
- [Failure Models](./02-failure-model.md)
- **RPC and Message Passing (current)**
- consistency and CAP (upcoming)
- replication (upcoming)
- consensus and Raft (upcoming)
- leader election (upcoming)
- message queues and event sourcing (upcoming)
- distributed transactions (upcoming)
- patterns for operable distributed systems (upcoming)
<!-- toc:end -->

## References

- [Remote procedure call (Wikipedia)](https://en.wikipedia.org/wiki/Remote_procedure_call)
- [Message passing (Wikipedia)](https://en.wikipedia.org/wiki/Message_passing)
- [gRPC documentation](https://grpc.io/docs/)
- [Apache Kafka documentation](https://kafka.apache.org/documentation/)

Tags: Computer Science, Distributed Systems, RPC, Messaging, Async, Idempotency

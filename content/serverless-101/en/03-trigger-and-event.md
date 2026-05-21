---
series: serverless-101
episode: 3
title: "Serverless 101 (3/10): Trigger and Event"
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
  - Trigger
  - Event
  - EventDriven
  - Cloud
seo_description: A practical trigger guide following one HTTP-to-queue workflow with idempotency, DLQ routing, replay, and duplicate troubleshooting.
last_reviewed: '2026-05-16'
---

# Serverless 101 (3/10): Trigger and Event

This is the third post in the Serverless 101 series.

Serverless functions do not wake themselves up. Something invokes them, possibly more than once, possibly as a batch, possibly after a delay, and possibly again after a failure. If you do not understand that invocation path, clean handler code still turns into duplicate side effects, invisible retries, and messy incident response.

So this post avoids a taxonomy-only approach. Instead, we will follow one complete flow: **an HTTP request becomes a queue message, a consumer processes it, duplicates are blocked through an external idempotency store, repeated failures are routed to a DLQ, and operators replay from that payload**. Once this path is clear, trigger semantics stop feeling abstract.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Trigger and Event?
- Which signal should the example or diagram make visible for Trigger and Event?
- What failure should be prevented first when Trigger and Event reaches a real system?

## Big Picture

![serverless 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/03/03-01-concept-at-a-glance.en.png)

*serverless 101 chapter 3 flow overview*

This picture places Trigger and Event inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- how HTTP, queue, and schedule triggers differ as delivery contracts
- why idempotency is a default assumption for async consumers
- why a DLQ is not a nice-to-have but an operational observation point
- what to inspect first when duplicate processing or retry storms appear

> A trigger is the connection that turns an event into a function invocation, and each trigger type carries its own latency expectation, retry behavior, and failure visibility.

## Why It Matters

Beginners usually focus on the function body first. In production, the bigger source of failure is often the **invocation contract**. HTTP requests center around user latency and explicit responses. Queue messages center around retries, duplication, and eventual completion. Scheduled triggers center around overlap and re-entrancy.

If you ignore those differences, code that looks perfectly reasonable in a single local run breaks down quickly in production. Real event systems introduce network delay, batch delivery, at-least-once redelivery, out-of-order arrival, and poison messages all at once.

Operationally, this is about role separation. The HTTP endpoint accepts work. The queue creates the async boundary. The consumer performs the actual side effect. The DLQ preserves repeated failures as inspectable payloads. Troubleshooting gets faster when you narrow the problem down in that order.

## The scenario for this post

We will continue the same order example again.

1. An HTTP request arrives at `/orders`.
2. The ingress handler validates it, emits a queue message, and returns `202 Accepted`.
3. A queue consumer reads the message, records an `idempotency_key` in an external store, and performs fulfillment work.
4. If the same message shows up again, the consumer skips the side effect.
5. If the message keeps failing, the system shapes it into a DLQ payload that an operator can replay.

The important idea is not “one function does everything.” It is **separating sync from async work, and separating success paths from failure paths**.

## HTTP → queue → consumer → idempotency → DLQ

The example is shown in one file for learning convenience. In production, the HTTP ingress and the queue consumer would usually be separate functions.

```python
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime

DB_PATH = "idempotency.db"

def build_response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }

def init_store() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_messages (
                idempotency_key TEXT PRIMARY KEY,
                processed_at TEXT NOT NULL,
                order_id TEXT NOT NULL
            )
            """
        )

def already_processed(idempotency_key: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT 1 FROM processed_messages WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()
    return row is not None

def mark_processed(idempotency_key: str, order_id: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO processed_messages VALUES (?, ?, ?)",
            (idempotency_key, datetime.now(UTC).isoformat(), order_id),
        )
        conn.commit()

@dataclass
class QueueMessage:
    message_id: str
    retry_count: int
    body: dict

QUEUE: list[QueueMessage] = []
DLQ: list[dict] = []

def http_ingress_handler(event: dict, context) -> dict:
    payload = json.loads(event.get("body") or "{}")
    order_id = payload.get("order_id")
    items = payload.get("items", [])

    if not order_id or not items:
        return build_response(400, {"ok": False, "error": "invalid order payload"})

    message = QueueMessage(
        message_id=f"msg-{order_id}",
        retry_count=0,
        body={
            "order_id": order_id,
            "items": items,
            "idempotency_key": payload.get("idempotency_key", f"order:{order_id}"),
        },
    )
    QUEUE.append(message)

    return build_response(
        202,
        {
            "ok": True,
            "order_id": order_id,
            "queued": True,
            "message_id": message.message_id,
        },
    )

def apply_fulfillment(order_id: str, items: list[dict]) -> None:
    if any(item["sku"] == "poison-pill" for item in items):
        raise RuntimeError("downstream inventory reservation failed")

def send_to_dlq(message: QueueMessage, error: Exception) -> None:
    DLQ.append(
        {
            "message_id": message.message_id,
            "order_id": message.body["order_id"],
            "idempotency_key": message.body["idempotency_key"],
            "retry_count": message.retry_count,
            "error": str(error),
            "failed_at": datetime.now(UTC).isoformat(),
        }
    )

def queue_consumer_handler(event: dict, context) -> dict:
    processed = []
    skipped = []
    failed = []

    for record in event["records"]:
        message = QueueMessage(**record)
        key = message.body["idempotency_key"]
        order_id = message.body["order_id"]

        if already_processed(key):
            skipped.append({"message_id": message.message_id, "reason": "duplicate"})
            continue

        try:
            apply_fulfillment(order_id, message.body["items"])
            mark_processed(key, order_id)
            processed.append({"message_id": message.message_id, "order_id": order_id})
        except Exception as exc:
            message.retry_count += 1
            if message.retry_count >= 3:
                send_to_dlq(message, exc)
                failed.append({"message_id": message.message_id, "sent_to": "dlq"})
            else:
                QUEUE.append(message)
                failed.append({"message_id": message.message_id, "sent_to": "retry-queue"})

    return {
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
    }
```

This example makes three operational points concrete.

- The HTTP handler responds quickly with `202 Accepted`; real work moves behind the queue.
- Idempotency is handled through an external-store contract, not an in-memory set. SQLite is only a local stand-in here; production systems would use something like DynamoDB, Redis, or Cloud SQL.
- The DLQ is not a place to hide errors. It is a place to preserve replayable failure context.

## Three expected outcomes

### 1) First successful consume

Start with a request like this:

```python
http_event = {
    "body": json.dumps(
        {
            "order_id": "ord-1001",
            "idempotency_key": "order:ord-1001",
            "items": [{"sku": "keyboard", "quantity": 1}],
        }
    )
}
```

After `http_ingress_handler(http_event, None)` and one queue-consumer pass, the expected result is:

```json
{
  "processed": [
    {
      "message_id": "msg-ord-1001",
      "order_id": "ord-1001"
    }
  ],
  "skipped": [],
  "failed": []
}
```

### 2) Duplicate message skipped

If the same `idempotency_key` is delivered again, the result should change to:

```json
{
  "processed": [],
  "skipped": [
    {
      "message_id": "msg-ord-1001",
      "reason": "duplicate"
    }
  ],
  "failed": []
}
```

The point is not “retries never happen.” The point is **retries can happen without duplicate side effects**.

### 3) Poison message routed to the DLQ

The example intentionally fails when an item uses the SKU `poison-pill`. After the third failed attempt, the stored DLQ payload should look like this:

```json
{
  "message_id": "msg-ord-9999",
  "order_id": "ord-9999",
  "idempotency_key": "order:ord-9999",
  "retry_count": 3,
  "error": "downstream inventory reservation failed",
  "failed_at": "2026-05-16T10:20:00+00:00"
}
```

That payload is what makes replay and incident response practical. It tells the operator what failed, on which retry attempt, under which idempotency key, and why.

## Trigger-selection matrix

This is where trigger discussions usually stay too abstract. A trigger is not just an entry point choice. It is a delivery contract.

| Trigger | Latency expectation | Retry default | Ordering expectation | Best-fit workloads |
| --- | --- | --- | --- | --- |
| HTTP | Immediate response, user-visible latency | Often combined with client or API-gateway retries | Not guaranteed | APIs, synchronous validation, fast acceptance paths |
| Queue | Seconds to minutes are acceptable | Assume at-least-once redelivery | Weak by default; use FIFO if needed | Async post-processing, batch consumers, burst buffering |
| Schedule | Time-window execution | Platform retry or next tick may re-run work | Overlap control matters more than strict order | Cleanup jobs, aggregation, sync tasks |

The practical lesson is simple. Choose HTTP and latency becomes the center of the design. Choose a queue and duplication plus DLQ handling become the center. Choose a schedule and re-entrancy plus overlap prevention become the center.

## Duplicate-processing troubleshooting flow

“The same order was processed twice” is one of the most common serverless incident reports. The fastest path is not to start by reading handler code line by line. Start here instead.

1. **Inspect the message ID.**
   - Was it truly the same message redelivered, or a different message with similar business data?
2. **Inspect the idempotency record.**
   - Was the key missing, or was it written too late in the processing flow?
3. **Inspect retry count and last error.**
   - Was this a transient failure followed by a redelivery, or a repeated hard failure?
4. **Inspect the DLQ payload.**
   - If the message has already been isolated, the payload often contains the fastest route to root cause and replay.

Following that order narrows the failure domain quickly: trigger semantics, idempotency-store timing, or downstream dependency behavior.

## Common Confusions

### Do retries really happen that often?

Yes. Network faults, platform timeouts, and downstream transient errors make redelivery routine enough that async triggers should usually be designed with at-least-once assumptions.

### Is ordering guaranteed by default?

Usually not. If order matters, you need to choose an explicit mechanism such as FIFO delivery, partitioning, or a single-consumer design.

### Is a DLQ alone enough for safe operations?

No. A DLQ only preserves failed work. Replay requires the payload to carry enough context: idempotency key, retry count, message identity, and error reason.

## Checklist

- [ ] HTTP and queue triggers have different success semantics by design
- [ ] Idempotency keys are persisted through an external-store contract
- [ ] Retry limits and DLQ routing rules are explicit
- [ ] Operators know what to inspect first in duplicate-processing incidents

## Wrap-up and Next Steps

Understanding triggers and events is not about memorizing invocation syntax. It is about understanding that **delivery semantics become failure semantics, and failure semantics become retry, idempotency, and DLQ design**.

The key pattern in this post is simple: accept quickly at the HTTP edge, move real work behind a queue, stop duplicates at the idempotency boundary, and preserve repeated failures as replayable DLQ payloads. In the next post, we will build on that path and look at why *cold start* changes latency expectations in serverless systems.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Trigger and Event?**
  - The article treats Trigger and Event as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Trigger and Event?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Trigger and Event reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Serverless 101 (1/10): What is Serverless?](./01-what-is-serverless.md)
- [Serverless 101 (2/10): Function as a Service](./02-function-as-a-service.md)
- **Trigger and Event (current)**
- Cold Start (upcoming)
- Scaling (upcoming)
- State Management (upcoming)
- Queue and Event-driven Architecture (upcoming)
- Observability (upcoming)
- Cost (upcoming)
- Designing a Serverless App (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [AWS Lambda event source mappings](https://docs.aws.amazon.com/lambda/latest/dg/invocation-eventsourcemapping.html)
- [Amazon SQS dead-letter queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [Azure Functions triggers and bindings overview](https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings)

### Delivery Patterns and Code

- [Idempotency pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/idempotency.html)
- [AWS Powertools for Lambda Python - Idempotency](https://docs.powertools.aws.dev/lambda/python/latest/utilities/idempotency/)
- [Azure Architecture Center - Queue-based load leveling pattern](https://learn.microsoft.com/azure/architecture/patterns/queue-based-load-leveling)

Tags: Serverless, Trigger, Event, EventDriven, Cloud

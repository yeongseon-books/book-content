---
series: serverless-101
episode: 3
title: Trigger and Event
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
seo_description: A beginner-friendly tour of serverless triggers and event sources, covering invocation types, retries, DLQs, and idempotency.
last_reviewed: '2026-05-04'
---

# Trigger and Event

Serverless functions do not wake themselves. Something invokes them, on a schedule, in response to an HTTP request, because a queue received a message, or because storage emitted an event. If you miss the meaning of that invocation path, clean function code still turns into duplicate processing or retry storms in production.

In practice, trigger semantics matter at least as much as handler logic. *Sync* and *async* invocation change who sees failure, who retries, and what “success” even means.

This is post 3 in the Serverless 101 series.

## What You Will Learn

- categories of *triggers*
- shapes of *event* payloads
- *sync* vs *async* differences
- *retries* and *DLQ*
- the importance of *idempotency*

## Why It Matters

Many production failures are not caused by the handler body at all. They come from misunderstanding the trigger contract: whether the event is delivered at least once, whether records arrive as a batch, whether retries are automatic, and whether ordering is guaranteed.

That is why a trigger discussion should start with failure semantics. The most useful question is often not “how do I parse this payload?” but “what happens when the same payload comes back again?”

## Concept at a Glance

![Concept at a Glance](../../../assets/serverless-101/03/03-01-concept-at-a-glance.en.png)

*Each trigger type adds its own delivery contract, retry behavior, and failure path.*
This separation is operationally important. The event source produces the signal, the trigger converts that signal into invocation behavior, and the DLQ captures work that keeps failing after the normal retry path is exhausted. Faster debugging starts when you know which of those three layers is actually failing.

## Key Terms

- **trigger**: connects an *event* to a *function*.
- **event source**: *queues, storage, HTTP, schedules,* etc.
- **invocation type**: *sync / async / stream*.
- **DLQ**: a *dead-letter queue* for *failed messages*.
- **idempotency**: *same input* → *same outcome*.

## Before/After

**Before**: *cron* + *script* + *manual retry*.

**After**: *scheduled trigger* + *DLQ* + *automatic retry*.

## Hands-on: HTTP / Queue / Schedule

### Step 1 — HTTP event

```python
def http_handler(event, context):
    body = event.get("body", "")
    return {"statusCode": 200, "body": f"echo:{body}"}
```

### Step 2 — Queue event

```python
def queue_handler(event, context):
    for rec in event["records"]:
        process(rec["body"])

def process(msg):
    print("got", msg)
```

### Step 3 — Schedule event

```python
import datetime as dt

def cron_handler(event, context):
    now = dt.datetime.utcnow().isoformat()
    return {"ran_at": now}
```

### Step 4 — Apply an idempotency key

```python
seen = set()

def idempotent(handler):
    def wrap(event, ctx):
        key = event.get("id")
        if key in seen:
            return {"skipped": True}
        seen.add(key)
        return handler(event, ctx)
    return wrap
```

### Step 5 — Decide what goes to DLQ

```python
def safe(handler, dlq):
    def wrap(event, ctx):
        try:
            return handler(event, ctx)
        except Exception as e:
            dlq.append({"event": event, "error": str(e)})
            raise
    return wrap
```

## What to Notice in This Code

- *records* may be a *batch*.
- *Idempotency keys* are a *retry safety net*.
- *DLQs* are the *starting point* for *debugging*.

## Five Common Mistakes

1. **Assuming *retries* will not happen.**
2. **Assuming *order* is *guaranteed*.**
3. **Doing *payment-like* work without *idempotency*.**
4. **Skipping *DLQ* configuration.**
5. **Setting *schedule ticks* too *short*.**

## How This Shows Up in Production

Common flows include *upload → thumbnail, payment event → email, queue → batch ingest* — *async pipelines*.

## How a Senior Engineer Thinks

- Assume *every trigger* is *at-least-once*.
- *Idempotency* protects *cost*.
- Without a *DLQ*, you do not see *problems*.
- Use a *FIFO queue* if *order* matters.
- *Schedules* must prevent *overlap*.

## Checklist

- [ ] *Idempotency* ensured.
- [ ] *DLQ* configured.
- [ ] *Retry count* explicit.
- [ ] *Ordering* requirement explicit.

## Practice Problems

1. In one line, the meaning of *at-least-once*.
2. In one line, the *purpose* of a *DLQ*.
3. In one line, the *risk* of missing *idempotency keys*.

## Wrap-up and Next Steps

Once you understand triggers and events, a function invocation stops looking like a simple entry point. It becomes a delivery contract with retry rules, batching behavior, and failure paths attached.

Next, we look at the causes and mitigations of *Cold Start*.

<!-- toc:begin -->
- [What is Serverless?](./01-what-is-serverless.md)
- [Function as a Service](./02-function-as-a-service.md)
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
- [Amazon EventBridge schedules](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-scheduled-rule-pattern.html)

### Delivery Guarantees and Patterns

- [Idempotency pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/idempotency.html)
- [AWS Powertools idempotency utility (GitHub)](https://github.com/aws-powertools/powertools-lambda-python)

Tags: Serverless, Trigger, Event, EventDriven, Cloud

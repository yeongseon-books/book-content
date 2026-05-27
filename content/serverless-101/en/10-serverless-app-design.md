---
series: serverless-101
episode: 10
title: "Serverless 101 (10/10): Designing a Serverless App"
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
  - Architecture
  - DesignPattern
  - Cloud
  - FinOps
seo_description: A capstone guide to serverless app design covering an image-processing pipeline, triggers, queues, state, observability, and cost tradeoffs
last_reviewed: '2026-05-04'
---

# Serverless 101 (10/10): Designing a Serverless App

One function by itself is simple. A real product is not. It has an upload edge, background processing, retries, state updates, notifications, metrics, and a failure path that still has to be visible when something breaks. At that point, you are still designing a distributed system, even if every piece is “just a function.”

That is why the capstone topic is not another isolated feature. It is composition. The challenge is deciding which responsibilities stay on the request path, which move behind queues, where state lives, and how failures become observable instead of silent.

This is the final post in the Serverless 101 series.


![serverless 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/10/10-01-concept-at-a-glance.en.png)
*serverless 101 chapter 10 flow overview*
> A serverless app is a graph of small functions connected by triggers and queues — the architecture work lives in the edges between them, not inside the functions themselves.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Designing a Serverless App?
- Which signal should the example or diagram make visible for Designing a Serverless App?
- What failure should be prevented first when Designing a Serverless App reaches a real system?

## What You Will Learn

- The core *design principles*
- A worked *image-processing pipeline*
- *Boundaries* and separation of *responsibility*
- *Failure* and *retry* design
- *Cost* and *operational* tradeoffs

## Why It Matters

The difficulty of serverless app design is not the number of functions. It is the quality of the boundaries between them. Weak boundaries create long request paths, unclear retry ownership, mixed responsibilities, and debugging pain.

Strong boundaries make the system easier to scale, easier to retry safely, and easier to operate when only one stage fails. That is why good serverless design is mostly about separation, not about function count.

This shape captures the default serverless instinct worth keeping: keep the request-path function thin, push long work behind a queue, store durable state explicitly, and separate notification from the business-critical path.

## Key Terms

- **edge function**: a thin function at the *request boundary*.
- **worker function**: a background processing function.
- **idempotency key**: a key that *prevents duplicate* processing.
- **dead-letter queue**: a queue that *isolates* failed messages.
- **bounded context**: a unit of *responsibility*.

## Before/After

**Before**: a single *monolithic function* handles *upload*, *transform*, and *notify*.

**After**: *upload*, *transform*, and *notify* are split across *queues*, each with its own *retry policy*.

## Hands-on: Image-processing Pipeline

### Step 1 — Upload function

```python
def upload(event):
    user = event["user_id"]
    key = f"raw/{user}/{event['filename']}"
    s3.put_object(Bucket="uploads", Key=key, Body=event["body"])
    return {"key": key}
```

### Step 2 — S3 event into a queue

```python
def on_object_created(event):
    for r in event["Records"]:
        sqs.send_message(
            QueueUrl=Q,
            MessageBody=json.dumps({"key": r["s3"]["object"]["key"]}),
        )
```

### Step 3 — Idempotent worker

```python
def worker(event):
    for r in event["Records"]:
        msg = json.loads(r["body"])
        key = msg["key"]
        if already_done(key):
            continue
        thumb = make_thumbnail(key)
        save(key, thumb)
        mark_done(key)
```

### Step 4 — Notify function

```python
def notify(event):
    for r in event["Records"]:
        msg = json.loads(r["body"])
        push(msg["user_id"], "Your thumbnail is ready")
```

### Step 5 — Failure isolation

```python
# Queue policy (pseudo-config)
queue_policy = {
    "VisibilityTimeout": 60,
    "MaxReceiveCount": 5,
    "DeadLetterQueue": "arn:.../thumb-dlq",
}
```

## Failure Walkthrough

In production, the hardest question is often not “what is the architecture?” but “where do I restart safely?” A simple review table helps:

| Stage | Typical failure | First check |
| --- | --- | --- |
| Upload edge | request timeout or auth failure | request logs, payload size, edge latency |
| Queue handoff | event never reaches worker | queue depth, publish errors, event schema |
| Worker transform | duplicate or partial processing | idempotency marker, retry count, DLQ |
| Notification | user never informed | notification queue, downstream provider response |

If each stage can fail independently and still be inspected independently, the design is usually on the right track.

## What to Notice in This Code

- *Boundaries* are made *explicit* by the queues.
- *Idempotency* is a *prerequisite* for safe retries.
- A *DLQ* surfaces the *silent* failures.

## Five Common Mistakes

1. **Doing the *transform* inside the *upload* function.**
2. **Skipping the *idempotency key* and *processing twice*.**
3. **No *DLQ*, so *messages disappear*.**
4. **Aggressive *retries* overwhelming the *database*.**
5. **Watching only *logs* and ignoring *metrics*.**

## How This Shows Up in Production

*Profile photo upload* in a mobile app, *receipt OCR*, *video transcoding* — all use the *same pattern*.

## How a Senior Engineer Thinks

- *Boundaries* are the *real* design of the system.
- A *queue* buffers *time*.
- *Idempotency* is the *baseline*, not an upgrade.
- A *DLQ* is your *operational eye*.
- *Cost* and *complexity* are read together.

## Checklist

- [ ] *Function boundaries* defined.
- [ ] *Idempotency key* applied.
- [ ] *DLQ* configured.
- [ ] *Cost model* written down.

## Practice Problems

1. Define *idempotency key* in one line.
2. State the role of a *DLQ* in one line.
3. Explain how a *queue* *buffers* time in one line.

## Wrap-up and Next Steps

The point of serverless design is not to split everything into tiny pieces. It is to draw boundaries that make retries safe, state explicit, failure visible, and costs easier to reason about.

Congratulations on finishing the series. Take the next step: design a *small distributed system* of your own, woven from *functions*, *queues*, and *triggers*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Designing a Serverless App?**
  - The article treats Designing a Serverless App as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Designing a Serverless App?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Designing a Serverless App reaches a real system?**
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
- [Serverless 101 (9/10): Cost](./09-cost.md)
- **Designing a Serverless App (current)**

<!-- toc:end -->

## References

### Official Guidance

- [AWS Serverless Application Lens](https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/welcome.html)
- [Serverless patterns collection](https://serverlessland.com/patterns)

### Architecture and Code

- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/)
- [Idempotency in AWS Powertools for Lambda](https://docs.powertools.aws.dev/lambda/python/latest/utilities/idempotency/)
- [AWS serverless samples (GitHub)](https://github.com/aws-samples/serverless-patterns)

Tags: Serverless, Architecture, DesignPattern, Cloud, FinOps

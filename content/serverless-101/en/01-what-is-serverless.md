---
series: serverless-101
episode: 1
title: What is Serverless?
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
  - Cloud
  - FaaS
  - Architecture
  - DevOps
seo_description: A practical introduction to serverless with a first-function workflow, deployment contract, expected output, and a poor-fit decision ladder.
last_reviewed: '2026-05-16'
---

# What is Serverless?

This is the first post in the Serverless 101 series.

When people first hear *serverless*, they usually compress it into one shortcut: “so the servers are gone.” The shortcut is understandable, but it is wrong enough to distort the design decisions that follow. The servers do not disappear. **The default operational responsibility moves to the platform.**

That is why the first question should not be “how do I write a function?” It should be **“is this workload a good candidate for serverless in the first place?”** Once that is clear, topics like *FaaS*, *triggers*, *cold starts*, and *cost* stop feeling like scattered caveats and start reading like one operating model.

## What You Will Learn

- what *serverless* really delegates to the platform
- what a first function should look like as an *input/output contract*
- what has to stay aligned between *local invocation* and *deployment*
- when *serverless* is a strong default and when it is the wrong one

> Serverless is not a no-server model. It is a model where the platform takes over a meaningful part of server operation and execution control.

## Start with the “wrong default” test

Many teams treat serverless as the quickest way to get started. Sometimes it is. Sometimes it creates more constraint work than it removes. The fastest way to stay honest is to run a simple decision ladder before you write the first handler.

### When serverless is the wrong default: a decision ladder

1. **Does the request finish within a short bounded runtime?**
   - Yes: continue.
   - No: long-running compute, persistent streaming, and session-heavy workloads are often simpler on an always-on runtime.
2. **Can state live outside the process?**
   - Yes: continue.
   - No: if durable in-memory or local-disk state is central to correctness, serverless is already a poor fit.
3. **Is traffic bursty or hard to predict?**
   - Yes: elastic scale is a real advantage.
   - No: steady sustained load may be cheaper and simpler on a continuously running service.
4. **Can you accept platform constraints around timeout, packaging, and runtime control?**
   - Yes: serverless is a solid starting point.
   - No: choose containers or VMs when runtime control itself is part of the requirement.

If one of those questions produces a strong early “no,” there is no prize for forcing a serverless shape anyway. Good architecture decisions are not about choosing the newest label. They are about choosing the execution model whose constraints are the least dishonest for the workload.

## Why It Matters

Serverless is powerful for the same reason it is easy to misuse. The platform absorbs patching, baseline scaling, and part of the runtime operations burden, which is a major win for small teams. But the convenience can hide the real contract.

Paying by usage does not automatically make the system cheap. Cost is shaped by invocation count, duration, memory, network transfer, and the managed services around the function. Breaking a service into functions does not remove distributed-system complexity either. It simply changes where the complexity shows up.

So the key framing for this first post is not “what became automatic?” but **“what do I still have to design explicitly?”** In serverless, that answer usually includes event boundaries, runtime budgets, external state, and observability.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/01/01-01-concept-at-a-glance.en.png)

*The platform sits between the incoming event and the function, which is why serverless is better understood as a responsibility shift than as a “no servers” slogan.*

The platform is the key actor in this diagram. It creates the execution environment, decides how invocations scale, and applies retry or timeout behavior. The developer no longer provisions servers directly, but becomes more responsible for **input contracts, response shape, state boundaries, and log fields**.

## A first serverless workflow: accept one HTTP request correctly

Instead of walking through disconnected toy snippets, we will use one small example that will continue into the next posts: a minimal order-ingest function. The goal is straightforward: **accept one HTTP-style event, validate it, and return a platform-friendly response**.

### Step 1 — Define the handler contract

```python
import json
from datetime import UTC, datetime


def build_response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }


def handler(event: dict, context) -> dict:
    request_id = getattr(context, "aws_request_id", "local-request")
    payload = json.loads(event.get("body") or "{}")

    order_id = payload.get("order_id")
    customer_tier = payload.get("customer_tier", "standard")
    items = payload.get("items", [])

    if not order_id or not items:
        return build_response(
            400,
            {
                "ok": False,
                "request_id": request_id,
                "error": "order_id and items are required",
            },
        )

    total_quantity = sum(item["quantity"] for item in items)

    return build_response(
        202,
        {
            "ok": True,
            "request_id": request_id,
            "accepted_at": datetime.now(UTC).isoformat(),
            "order_id": order_id,
            "customer_tier": customer_tier,
            "total_quantity": total_quantity,
            "next_step": "queued-for-fulfillment",
        },
    )
```

The point of this first function is not business sophistication. It is contract clarity.

- Input arrives through `event` and `context`.
- The actual business payload is JSON inside `event["body"]`.
- Validation failures still return a normalized HTTP response.
- Success explicitly tells the caller what happens next.

### Step 2 — Freeze the event shape on paper

```python
sample_event = {
    "httpMethod": "POST",
    "path": "/orders",
    "headers": {"content-type": "application/json"},
    "body": json.dumps(
        {
            "order_id": "ord-1001",
            "customer_tier": "gold",
            "items": [
                {"sku": "keyboard", "quantity": 1},
                {"sku": "mouse", "quantity": 2},
            ],
        }
    ),
}
```

One of the easiest beginner mistakes is to focus on the handler body and leave the event shape vague. In production, the event shape matters more than the function name. HTTP, queue, and scheduled events carry very different payload contracts and very different failure meanings.

### Step 3 — Separate a local invocation path

```python
class LocalContext:
    aws_request_id = "req-local-001"


if __name__ == "__main__":
    result = handler(sample_event, LocalContext())
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

This is the right kind of “toy” step because it isolates the handler logic from deployment details. If the function fails later, you can more quickly tell whether the problem is in the handler itself or in the managed runtime configuration.

```bash
python3 app.py
```

### Step 4 — Write down the expected output

```json
{
  "statusCode": 202,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"ok\": true, \"request_id\": \"req-local-001\", \"accepted_at\": \"2026-05-16T10:00:00+00:00\", \"order_id\": \"ord-1001\", \"customer_tier\": \"gold\", \"total_quantity\": 3, \"next_step\": \"queued-for-fulfillment\"}"
}
```

Expected output blocks are not just for readability. They define the success contract that the next posts will build on. Without that baseline, queue delivery, retries, and DLQs remain conceptually correct but operationally blurry.

## The deployment contract already hiding inside this example

Even a tiny function stops being useful if it ends at “look, Python runs.” The moment you think about deploying it, four operational contracts are already present.

| Item | Contract in this example | Why it matters |
| --- | --- | --- |
| Event shape | HTTP payload comes in as a JSON string under `body` | Local tests and managed-runtime input must agree |
| Timeout budget | The function owns only short request-time work | Long-running work pushed here becomes timeout and retry cost |
| State boundary | Order state does not live inside the function process | Process memory and local disk are not durable system state |
| Log fields | `request_id`, `order_id`, and `next_step` must be recorded | You need a trace handle before retries and async hops arrive |

That table is the real beginning of serverless design. A function body may look small, but production success usually hinges on **event contract + runtime budget + external state boundary + observability discipline**.

## The operator checklist for a first function

You do not need a huge observability platform on day one. You do need a few early habits.

1. **Document the event shape.**
   - Required and optional fields should be explicit.
2. **Keep request-time work inside the timeout budget.**
   - Slow follow-up work should move to an async path.
3. **Decide the external state boundary early.**
   - “We will keep it in memory for now” becomes technical debt almost immediately in serverless systems.
4. **Standardize traceable log fields.**
   - Keys like `request_id`, `order_id`, and `event_type` are the minimum viable operating vocabulary.

## Common Confusions

### Does serverless automatically lower cost?

No. Low traffic helps, but cost is still a function of duration, memory, transfer, and dependent services. Invocation count alone is an incomplete model.

### If the function is small, does the architecture become simple automatically?

No. Small functions can still create a messy system if boundaries, retries, and state transitions are unclear. In serverless, *event boundaries* matter more than line count.

### Is serverless the right default for every API backend?

It is strong for short independent requests, bursty traffic, and event-driven post-processing. It is a weaker default for long-lived connections, real-time sessions, continuous compute, or workloads that need tight runtime control.

## Checklist

- [ ] The workload passes the serverless decision ladder
- [ ] The first function has an explicit event and response contract
- [ ] State is planned outside the function process
- [ ] Traceable log fields are defined up front

## Wrap-up and Next Steps

The core of serverless is not server removal. It is responsibility transfer. The platform takes over more of the execution surface, while you become more responsible for event contracts, state boundaries, runtime budgets, and observability.

Our first example was only a tiny HTTP order-ingest handler, but it already carried the core contract of a serverless system. In the next post, we will continue with the same example family and turn it into a **real build-package-run-measure FaaS workflow**.

<!-- toc:begin -->
- **What is Serverless? (current)**
- Function as a Service (upcoming)
- Trigger and Event (upcoming)
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

- [AWS Lambda overview](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [Google Cloud Functions overview](https://cloud.google.com/functions/docs)
- [Azure Functions overview](https://learn.microsoft.com/azure/azure-functions/functions-overview)

### Architecture and Operational Guidance

- [Serverless (Martin Fowler)](https://martinfowler.com/articles/serverless.html)
- [AWS Serverless Lens](https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/welcome.html)
- [Azure Well-Architected Framework for serverless workloads](https://learn.microsoft.com/azure/well-architected/service-guides/azure-functions)

### Code and Related Reading

- [AWS Lambda developer guide examples (GitHub)](https://github.com/awsdocs/aws-lambda-developer-guide)
- [Azure Functions 101](../../azure-functions-101/en/)

Tags: Serverless, Cloud, FaaS, Architecture, DevOps

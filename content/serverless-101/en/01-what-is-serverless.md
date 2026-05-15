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
seo_description: A beginner-friendly tour of serverless covering its definition, FaaS, usage-based billing, and how operational responsibility shifts to the platform.
last_reviewed: '2026-05-04'
---

# What is Serverless?

When people first hear *serverless*, they usually land on the same shortcut. “So the servers are gone.” The direction is understandable, but the conclusion is wrong enough to distort every decision that follows.

The servers do not disappear. The operational responsibility moves. Once you see that shift clearly, topics like *cold start*, *state management*, *observability*, and *cost* stop feeling like scattered caveats and start reading like one operating model.

This is the first post in the Serverless 101 series.

## What You Will Learn

- the definition of *serverless*
- its relationship with *FaaS*
- *usage-based billing*
- how *responsibility shifts*
- which *workloads* fit and which do not

## Why It Matters

*Serverless* is not a convenience toggle. It is an architectural choice. For a small team, it can be powerful because the platform absorbs patching, baseline scaling, and part of the runtime operations burden so the team can stay focused on product work.

That benefit comes with a trade. Paying by usage does not automatically make the system cheap, and breaking logic into small functions does not make distributed-system complexity disappear. If you start with “who owns which responsibility now?” the rest of the series becomes much easier to reason about.

## Concept at a Glance

![Concept at a Glance](../../../assets/serverless-101/01/01-01-concept-at-a-glance.en.png)

*The platform sits between events and function execution, which is why responsibility transfer matters more than the slogan “no servers.”*
The key actor in this diagram is the *platform*, not the function. The platform decides when to create an execution environment, how to invoke the function, and what operational guarantees exist around scaling and retries. That is why a serverless design discussion usually starts with boundaries and responsibility, not with the function body itself.

## Key Terms

- **Serverless**: a model that *delegates server operation* to the *platform*.
- **FaaS**: a *function-level* execution environment.
- **Event source**: the *signal* that *wakes* a *function*.
- **Lifetime**: the *short window* a *function* is *alive*.
- **Usage-based billing**: pay only for *invocations*.

## Before/After

**Before**: a *24/7* *server*, *cost* even at *zero traffic*.

**After**: pay only for what is *invoked*; no *provisioning*.

## Hands-on: the Smallest Function

### Step 1 — Write a Python function

```python
def handler(event, context):
    name = event.get("name", "world")
    return {"message": f"hello, {name}"}
```

### Step 2 — Simulate invocation locally

```python
def invoke_local(handler, event):
    return handler(event, context=None)

print(invoke_local(handler, {"name": "Alice"}))
```

### Step 3 — Get used to event shapes

```python
http_event = {"path": "/hello", "method": "GET", "name": "Bob"}
queue_event = {"records": [{"body": "msg-1"}, {"body": "msg-2"}]}
```

### Step 4 — Be aware of timeouts

```python
import time

def slow_handler(event, context):
    time.sleep(0.1)
    return {"ok": True}
```

### Step 5 — Standardize the response

```python
def http_response(status, body):
    return {"statusCode": status, "body": body}
```

## What to Notice in This Code

- The *event* + *context* pair is the *common* signature.
- Functions should be *short and deterministic*.
- *State* belongs *outside* the function.

## Five Common Mistakes

1. **Building *long-running* tasks as *functions*.**
2. **Storing state in *local files*.**
3. **Ignoring *cold starts*.**
4. **Estimating *cost* from *call count* alone.**
5. **Operating without *observability*.**

## How This Shows Up in Production

It fits *event handling, ETL, API backends, scheduled jobs* — work that is *short and self-contained*.

## How a Senior Engineer Thinks

- *Serverless* is an *option*, not a *default*.
- *Cost* equals *calls + duration + resources*.
- Put *state* in *external storage*.
- *Cold start* is a *design variable*.
- *Observability* is *half of debugging*.

## Checklist

- [ ] Function is *short* and *deterministic*.
- [ ] *State* externalized.
- [ ] *Cost model* reviewed.
- [ ] *Observability* in place.

## Practice Problems

1. In one line, why *serverless* does not mean *no servers*.
2. In one line, the *unit* of *FaaS*.
3. In one line, a workload that is a *poor fit*.

## Wrap-up and Next Steps

The core idea is not *server removal* but *responsibility transfer*. The platform takes over more of the operational surface, while you become more responsible for event boundaries, state placement, observability, and cost-aware design.

The next post explores the *structure* and *usage patterns* of *FaaS*.

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

### Architecture and Patterns

- [Serverless (Martin Fowler)](https://martinfowler.com/articles/serverless.html)
- [AWS Serverless Lens](https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/welcome.html)

### Code and Related Reading

- [AWS Lambda developer guide examples (GitHub)](https://github.com/awsdocs/aws-lambda-developer-guide)
- [Azure Functions 101](../../azure-functions-101/en/)

Tags: Serverless, Cloud, FaaS, Architecture, DevOps

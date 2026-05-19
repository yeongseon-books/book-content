---
series: serverless-101
episode: 6
title: State Management
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
  - State
  - Database
  - Cache
  - Cloud
seo_description: A beginner-friendly tour of state in serverless covering external stores, caches, workflow state, and combination with idempotency.
last_reviewed: '2026-05-04'
---

# State Management

Sooner or later, serverless beginners hit the same objection. “If functions must stay stateless, where do sessions, carts, workflow progress, and deduplication state go?” If that question stays fuzzy, serverless feels like an arbitrary restriction instead of a usable design rule.

The important distinction is simple: the business still has state, but the function process is not the place to trust that state. Once you accept that, the rest becomes an architecture exercise about choosing the right external stores.

This is post 6 in the Serverless 101 series.

## What You Will Learn

- the meaning of *stateless*
- where *sessions/caches* live
- *database* selection
- *workflow* state
- pairing with *idempotency*

## Why It Matters

A function instance can disappear at any time, and the next request from the same user may land on a different instance. That makes in-memory or local-disk state look acceptable in a local demo and dangerously unreliable in production.

State management is not a side concern in serverless. It determines where sessions live, how retries become safe, where workflow progress is stored, and how much complexity you keep inside one function versus pushing into a clearer orchestration model.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/06/06-01-concept-at-a-glance.en.png)

*Functions do the work, while caches, databases, and workflow engines hold the durable state.*
This is the core serverless shape: functions do work, but external systems own durable memory. Caches hold short-lived state, databases own long-lived state, and workflow engines track multi-step progress that would be painful to reconstruct from function code alone.

## Key Terms

- **stateless**: the *function* holds no *state*.
- **session store**: *Redis/DynamoDB,* etc.
- **workflow state**: *orchestration* such as *Step Functions*.
- **idempotency token**: makes *retries* safe.
- **TTL**: *expiration time* for *state*.

## Before/After

**Before**: cache in *global variables* → *lost*.

**After**: *Redis* + *TTL* + *idempotent keys*.

## Hands-on: External State

### Step 1 — Key-value cache abstraction

```python
class Cache:
    def __init__(self):
        self.store = {}
    def get(self, k):
        return self.store.get(k)
    def set(self, k, v, ttl=60):
        self.store[k] = (v, ttl)
```

### Step 2 — Session handler

```python
def with_session(handler, cache):
    def wrap(event, ctx):
        sid = event.get("session")
        state = cache.get(sid) or {}
        result = handler(event, ctx, state)
        cache.set(sid, state)
        return result
    return wrap
```

### Step 3 — Idempotency token

```python
def use_token(cache, token):
    if cache.get(token):
        return False
    cache.set(token, "done", ttl=3600)
    return True
```

### Step 4 — Workflow state (pseudo)

```python
"""
states:
  Validate -> Charge -> Notify
on Failure: -> Refund
"""
```

### Step 5 — Separate the data model

```python
def model(record):
    return {"id": record["id"], "status": record.get("status", "new")}
```

## What to Notice in This Code

- Put *sessions* in an *external store*.
- *Idempotency tokens* make *retries* safe.
- Express *workflows* as *state machines*.

## Five Common Mistakes

1. **Caching in *global variables*.**
2. **Opening a *new DB connection* per *function* invocation.**
3. **Letting state grow *unbounded* without *TTL*.**
4. **Missing *idempotency tokens*.**
5. **Cramming *complex flows* into *one function*.**

## How This Shows Up in Production

*Sessions* go to *Redis*, *data* to *DynamoDB/RDS*, *complex flows* to *Step Functions* or similar *orchestrators*.

## How a Senior Engineer Thinks

- *Stateless* is both a *constraint* and *freedom*.
- *State location* is your *architecture*.
- *TTL* protects *cost*.
- Treat *workflows* as *state machines*, not code.
- The *data model* will *evolve*.

## Checklist

- [ ] *Sessions* externalized.
- [ ] *DB connection* reused.
- [ ] *TTL* set.
- [ ] *Workflow* extracted.

## Practice Problems

1. In one line, the meaning of *stateless*.
2. In one line, the *role* of an *idempotency token*.
3. In one line, the *benefit* of a *workflow state machine*.

## Wrap-up and Next Steps

The goal is not to erase state. The goal is to put each kind of state in the place that matches its lifetime, consistency needs, and recovery model.

Next, we cover *Queues* and *Event-driven Architecture*.

<!-- toc:begin -->
- [What is Serverless?](./01-what-is-serverless.md)
- [Function as a Service](./02-function-as-a-service.md)
- [Trigger and Event](./03-trigger-and-event.md)
- [Cold Start](./04-cold-start.md)
- [Scaling](./05-scaling.md)
- **State Management (current)**
- Queue and Event-driven Architecture (upcoming)
- Observability (upcoming)
- Cost (upcoming)
- Designing a Serverless App (upcoming)
<!-- toc:end -->

## References

### Official Docs

- [DynamoDB data modeling best practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-modeling-nosql-B.html)
- [Amazon ElastiCache overview](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/WhatIs.html)
- [AWS Step Functions developer guide](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html)

### Patterns and Code

- [Idempotency pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/idempotency.html)
- [AWS Powertools idempotency utility (GitHub)](https://github.com/aws-powertools/powertools-lambda-python)

Tags: Serverless, State, Database, Cache, Cloud

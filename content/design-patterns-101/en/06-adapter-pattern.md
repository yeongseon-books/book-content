---
series: design-patterns-101
episode: 6
title: "Design Patterns 101 (6/10): The Adapter Pattern"
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
  - DesignPatterns
  - Adapter
  - Structural
  - Compatibility
  - Wrapper
seo_description: How the Adapter pattern protects domain boundaries by translating external interfaces into contracts the application can own.
last_reviewed: '2026-05-15'
---

# Design Patterns 101 (6/10): The Adapter Pattern

Production systems rarely talk only to interfaces we designed ourselves. Payment SDKs, storage clients, mail providers, and third-party APIs all arrive with their own method names, error models, and data shapes. The trouble begins when those external details leak through the domain.

This is post 6 in the Design Patterns 101 series.

In this post, we'll use the Adapter pattern as a thin translation layer at the boundary. The aim is to let the domain speak in its own contract while the adapter absorbs SDK-specific calls, types, and exceptions.

## Questions to Keep in Mind

- The problem Adapter solves?
- Define a domain interface, then wrap external calls?
- Object Adapter vs Class Adapter?

## Big Picture

![design patterns 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/06/06-01-concept-at-a-glance.en.png)

*design patterns 101 chapter 6 flow overview*

This picture places The Adapter Pattern inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why It Matters

When external library calls scatter through the domain, every library tweak shakes the domain. An Adapter pins that movement to a single *boundary line*.

> An Adapter is a *thin coat* at the boundary.

## Key Terms

- **Target**: the interface the domain wants.
- **Adaptee**: the external interface we have.
- **Adapter**: implements Target, calls Adaptee.
- **Object Adapter**: holds Adaptee by composition.
- **Class Adapter**: absorbs Adaptee via multiple inheritance (rare in Python).

## Before/After

**Before**

```python
import boto3
def save_report(data):
    s3 = boto3.client("s3")
    s3.put_object(Bucket="reports", Key="r.json", Body=data)
```

**After**

```python
class FileStore:
    def put(self, key, data): ...

class S3FileStore(FileStore):
    def __init__(self, bucket):
        self._s3 = boto3.client("s3"); self.bucket = bucket
    def put(self, key, data):
        self._s3.put_object(Bucket=self.bucket, Key=key, Body=data)

def save_report(store: FileStore, data):
    store.put("r.json", data)
```

`save_report` no longer knows boto3.

## Hands-on: Five Steps to Practice Adapter

### Step 1 — Domain interface first

```python
# 1_iface.py
from typing import Protocol

class FileStore(Protocol):
    def put(self, key: str, data: bytes) -> None: ...
    def get(self, key: str) -> bytes: ...
```

Define the shape the domain *wants*, before any external library.

### Step 2 — Wrap the external call

```python
# 2_s3_adapter.py
class S3FileStore:
    def __init__(self, client, bucket):
        self.client, self.bucket = client, bucket
    def put(self, key, data):
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)
    def get(self, key):
        return self.client.get_object(Bucket=self.bucket, Key=key)["Body"].read()
```

The S3 call lives only inside this class.

### Step 3 — Use it from the domain

```python
# 3_domain.py
def archive(store, key, data):
    store.put(key, data)
```

In tests, you can inject a fake store.

### Step 4 — Add another backend

```python
# 4_local_adapter.py
import pathlib
class LocalFileStore:
    def __init__(self, root): self.root = pathlib.Path(root)
    def put(self, key, data):
        (self.root / key).write_bytes(data)
    def get(self, key):
        return (self.root / key).read_bytes()
```

A new Adapter slots in without touching the domain.

### Step 5 — Test double

```python
# 5_fake.py
class InMemoryFileStore:
    def __init__(self): self._d = {}
    def put(self, k, v): self._d[k] = v
    def get(self, k): return self._d[k]
```

A fake Adapter makes unit tests fast and deterministic.

## What to Notice in This Code

- External SDK calls live *only* inside the Adapter.
- The domain depends only on a Protocol.
- Test doubles slot into the same seam naturally.

## Five Common Mistakes

1. **Business logic inside the Adapter.** Translation and policy mix.
2. **Leaking external types through the boundary.** The domain learns the SDK.
3. **Adapter calling another Adapter directly.** Boundary violation.
4. **Re-raising external exceptions verbatim.** *Translate* them to domain exceptions.
5. **Adapter growing fat.** Responsibility crept in beyond the boundary.

## How This Shows Up in Production

S3/GCS/Local behind one FileStore, payment gateways (Stripe/Toss/PortOne) behind one PaymentGateway, mail senders (SES/SendGrid/SMTP) behind one Mailer — all Adapters. The freedom to swap operational backends comes from here.

## Quick verification

Check these points before and after introducing an Adapter.

- Search the domain layer for imports of third-party SDK types or clients.
- Swap the production adapter for an in-memory fake in one test and confirm the domain code does not change.
- Verify that external exceptions, identifiers, and payload shapes stop crossing the application boundary.

**Expected outcome:** the domain keeps a stable contract, while infrastructure-specific details move behind one replaceable boundary class or function.

## How a Senior Engineer Thinks

- Sketch the *domain* interface first.
- Keep Adapters *thin* — translation and call only.
- Translate external exceptions into domain ones.
- Build a Fake/InMemory Adapter alongside.
- A fattening Adapter signals misplaced responsibility.

## Checklist

- [ ] Does the domain avoid importing external SDKs?
- [ ] Does the Adapter make no business decisions?
- [ ] Do external types stay inside the boundary?
- [ ] Are external exceptions translated to domain exceptions?
- [ ] Does an InMemory Adapter exist?

## Practice Problems

1. Split mail-sending behind a `Mailer` interface plus an SMTP Adapter.
2. Express payment-gateway calls behind a `PaymentGateway` interface with two or more Adapters.
3. Add `InMemory` versions for both interfaces and write unit tests against them.

## Wrap-up and Next Steps

Adapter is the *thin coat* at the boundary. The next post moves to inter-object notification — the Observer pattern.

## Answering the Opening Questions

- **The problem Adapter solves?**
  - The article treats The Adapter Pattern as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Define a domain interface, then wrap external calls?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Object Adapter vs Class Adapter?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Design Patterns 101 (1/10): What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational Patterns](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural Patterns](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral Patterns](./04-behavioral-patterns.md)
- [Design Patterns 101 (5/10): The Strategy Pattern](./05-strategy-pattern.md)
- **The Adapter Pattern (current)**
- The Observer Pattern (upcoming)
- Factory and Dependency Injection (upcoming)
- Avoiding Pattern Overuse (upcoming)
- Pythonic Patterns (upcoming)

<!-- toc:end -->

## References

### Core references

- [Adapter Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/adapter)
- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Ports and Adapters (Wikipedia)](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))

### Practical follow-up

- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)
- [Boto3 S3 `put_object` reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html)

Tags: Computer Science, DesignPatterns, Adapter, Structural, Compatibility, Wrapper

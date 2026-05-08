
# The Adapter Pattern

> Design Patterns 101 series (6/10)

<!-- a-grade-intro:begin -->

**Core question**: How do we use an interface we *cannot change* in the shape we *want*?

> By placing a thin translator object — an Adapter — between us and it.

<!-- a-grade-intro:end -->

## What You Will Learn

- The problem Adapter solves
- Define a domain interface, then wrap external calls
- Object Adapter vs Class Adapter
- Adapter and test doubles
- Signs an Adapter has gone wrong

## Why It Matters

When external library calls scatter through the domain, every library tweak shakes the domain. An Adapter pins that movement to a single *boundary line*.

> An Adapter is a *thin coat* at the boundary.

## Concept at a Glance

```mermaid
flowchart LR
    Domain["Domain code"] --> Iface["Domain interface"]
    Iface --> Adapter["Adapter"]
    Adapter --> Lib["External library"]
```

The domain knows only the interface; the Adapter takes the external call.

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

- [What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Creational Patterns](./02-creational-patterns.md)
- [Structural Patterns](./03-structural-patterns.md)
- [Behavioral Patterns](./04-behavioral-patterns.md)
- [The Strategy Pattern](./05-strategy-pattern.md)
- **The Adapter Pattern (current)**
- Observer Pattern (upcoming)
- Factory and Dependency Injection (upcoming)
- Avoiding Pattern Overuse (upcoming)
- Pythonic Patterns (upcoming)
## References

- [Adapter Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/adapter)
- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Ports and Adapters (Wikipedia)](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)

Tags: Computer Science, DesignPatterns, Adapter, Structural, Compatibility, Wrapper

---

© 2026 YeongseonBooks. All rights reserved.

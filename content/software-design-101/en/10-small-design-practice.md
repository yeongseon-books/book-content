---
series: software-design-101
episode: 10
title: Small Design Practice
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - SoftwareDesign
  - Practice
  - Project
  - Modularity
  - Architecture
seo_description: Build a tiny URL shortener and apply every design tool from this series in one place.
last_reviewed: '2026-05-04'
---

# Small Design Practice

This is the final post in the Software Design 101 series.

> Software Design 101 series (10/10)

<!-- a-grade-intro:begin -->

**Core question**: How do you actually use all the tools from this series in one project?

> By building a small URL shortener and unfolding separation of concerns, dependency direction, layers, and data flow line by line.

<!-- a-grade-intro:end -->

## What You Will Learn

- How to start design on a small project
- The flow of writing the domain first
- Blocking infrastructure with adapters
- Decisions about likely change points
- Every tool from the series in one place

## Why It Matters

The same principles work in small code. The mini-project here is small but it is the stage for applying every tool.

> Good habits get built in small systems.

## Concept at a Glance

```mermaid
flowchart LR
    HTTP["HTTP layer"] --> APP["shorten_use_case"]
    APP --> DOM["ShortLink domain"]
    APP --> REPO["LinkRepo (port)"]
    REPO --> SQL["SqlLinkRepo (adapter)"]
```

Domain → port → adapter → infrastructure.

## Key Terms

- **Short link**: A short key representing a long URL.
- **Use case**: A single business flow.
- **Port**: An interface defined by the domain.
- **Adapter**: An infrastructure piece that implements a port.
- **Composition root**: The single place where parts get wired together.

## Before / After

**Before**

```python
@app.route("/", methods=["POST"])
def shorten():
    long = request.json["url"]
    key = hashlib.md5(long.encode()).hexdigest()[:6]
    db.execute("INSERT INTO links VALUES (?, ?)", (key, long))
    return {"short": "/r/" + key}
```

**After**

```python
@app.route("/", methods=["POST"])
def shorten_view():
    return shorten_use_case(request.json, repo, key_gen)
```

The view is thin and the domain is protected.

## Hands-on: Build the URL Shortener in Five Steps

### Step 1 — Domain first

```python
# 1_domain.py
from dataclasses import dataclass

@dataclass(frozen=True)
class ShortLink:
    key: str
    target: str

    @staticmethod
    def create(key, target):
        if not target.startswith("http"):
            raise ValueError("invalid url")
        return ShortLink(key=key, target=target)
```

Rules in the domain. Zero external dependencies.

### Step 2 — Define ports

```python
# 2_ports.py
from typing import Protocol

class LinkRepo(Protocol):
    def save(self, link: ShortLink) -> None: ...
    def get(self, key: str) -> ShortLink | None: ...

class KeyGen(Protocol):
    def __call__(self, target: str) -> str: ...
```

The domain declares the shape it needs.

### Step 3 — Use case

```python
# 3_usecase.py
def shorten_use_case(payload, repo: LinkRepo, key_gen: KeyGen):
    target = payload["url"]
    key = key_gen(target)
    link = ShortLink.create(key, target)
    repo.save(link)
    return {"short": "/r/" + link.key}
```

Flow lives in the application layer.

### Step 4 — Adapters

```python
# 4_adapter.py
class InMemoryLinkRepo:
    def __init__(self): self._d = {}
    def save(self, link): self._d[link.key] = link
    def get(self, key): return self._d.get(key)

def md5_key(target: str) -> str:
    import hashlib
    return hashlib.md5(target.encode()).hexdigest()[:6]
```

The same port could host SQL or Redis adapters.

### Step 5 — Compose and present

```python
# 5_compose.py
from flask import Flask, request
app = Flask(__name__)
repo = InMemoryLinkRepo()
key_gen = md5_key

@app.route("/", methods=["POST"])
def shorten_view():
    return shorten_use_case(request.json, repo, key_gen)

@app.route("/r/<key>")
def redirect_view(key):
    link = repo.get(key)
    return ("not found", 404) if not link else ("", 302, {"Location": link.target})
```

Composition at the edge, view stays thin.

## What to Notice in This Code

- The domain has no external dependencies.
- The ports live on the domain side.
- Swapping adapters does not shake the domain.
- Data flows in a single direction.
- The presentation layer is thin.

## Five Common Mistakes

1. **Using Flask request directly inside the domain.** Presentation invades the domain.
2. **Putting concrete decisions like md5 in the domain.** Policy and mechanism mix.
3. **Stuffing every responsibility into the view.** Adding a new channel becomes hard.
4. **Writing only integration tests.** No domain-level unit tests.
5. **Introducing abstraction too early.** Four adapters in the very first version.

## How This Shows Up in Production

The same pattern scales straight into bigger systems — payments, auth, notifications — keeping the domain at the center and blocking the outside with adapters.

## How a Senior Engineer Thinks

- Even small projects start from the domain.
- Even with one adapter at first, they keep an interface in front.
- They keep the presentation layer thin so channels can be swapped.
- They write domain unit tests first.
- They keep composition in one place.

## Checklist

- [ ] Is the domain free of infrastructure?
- [ ] Are ports defined on the domain side?
- [ ] Is the presentation layer thin?
- [ ] Does data flow in one direction?
- [ ] Is composition concentrated in one place?

## Practice Problems

1. Add a SqlLinkRepo adapter to the code above. The domain must not change a single line.
2. Add a CLI presentation layer that calls the same use case.
3. Add an expiration rule to ShortLink and write a domain unit test for it.

## Wrap-up and Next Steps

This is the end of the series. Put the domain in the center, surround it with ports, block the outside with adapters, and let data flow in one direction — that one sentence is the whole game. On the next system you build, take that sentence as the starting point.

<!-- toc:begin -->
- [What Is Software Design?](./01-what-is-software-design.md)
- [Separation of Concerns](./02-separation-of-concerns.md)
- [Modules and Boundaries](./03-modules-and-boundaries.md)
- [Dependency Direction](./04-dependency-direction.md)
- [Interfaces and Abstraction](./05-interfaces-and-abstraction.md)
- [Layered Architecture](./06-layered-architecture.md)
- [Data Flow Design](./07-data-flow-design.md)
- [Reducing Change Impact](./08-reducing-change-impact.md)
- [Design Principles](./09-design-principles.md)
- **Small Design Practice (current)**
<!-- toc:end -->

## References

- [Cosmic Python — Architecture Patterns with Python](https://www.cosmicpython.com/)
- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design (Eric Evans)](https://martinfowler.com/bliki/DomainDrivenDesign.html)

Tags: Computer Science, SoftwareDesign, Practice, Project, Modularity, Architecture

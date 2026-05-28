---
series: clean-code-101
episode: 8
title: "Clean Code 101 (8/10): Testable Code"
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
  - CleanCode
  - Testability
  - Testing
  - DependencyInjection
  - Refactoring
seo_description: Make code testable with pure functions, dependency injection, seams, fakes, and spies; isolate time and IO at boundaries.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (8/10): Testable Code

Some code takes one line to test and some code fights back with clocks, networks, databases, and hidden globals. That difference is usually a design decision, not a testing-library problem.

This is the 8th post in the Clean Code 101 series.

Here we will push time, IO, and randomness to the boundaries, then use seams, fakes, and adapters to make tests fast enough that they can guide everyday refactoring.


![clean code 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/08/08-01-concept-at-a-glance.en.png)
*clean code 101 chapter 8 flow overview*
> Pure logic at the center, thin adapters at the boundary.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Testable Code?
- Which signal should the example or diagram make visible for Testable Code?
- What failure should be prevented first when Testable Code reaches a real system?

## Questions this article answers

- How should you separate pure logic from side effects?
- How does dependency injection create seams for testing?
- When should you use a fake, and when should you use a spy?
- How do you handle non-deterministic dependencies such as time and randomness?
- Which refactorings directly improve testability?

> Testability is not an after-the-fact outcome. It is a byproduct of design, shaped by how well you push side effects and dependencies outward.

## Why It Matters

Hard-to-test code is a sign of hard-to-change structure. Testability is a measure of design quality.

> Testability is not an outcome. It is a result of design.

A pure core surrounded by thin adapters.

## Key Terms

- **Pure function**: Same input → same output, no side effects.
- **Dependency Injection**: Pass external dependencies as arguments.
- **Seam**: A point where behavior can be swapped.
- **Fake**: A simplified working implementation for tests.
- **Spy**: A test double that records calls.

## Before/After

**Before**

```python
import datetime, requests
def is_business_hour():
    now = datetime.datetime.now()
    return 9 <= now.hour < 18

def fetch_user(uid):
    return requests.get(f"https://api/users/{uid}").json()
```

**After**

```python
def is_business_hour(now):
    return 9 <= now.hour < 18

def fetch_user(uid, http):
    return http.get(f"/users/{uid}").json()
```

Time and HTTP arrive from the outside.

## Hands-on: Five Steps to Testability

### Step 1 — Extract pure logic

```python
# 1_pure.py
def total(items):
    return sum(it.price * it.qty for it in items)
```

IO-free computation should always be pure.

### Step 2 — Inject time

```python
# 2_clock.py
from datetime import datetime
def is_overdue(due, now=None):
    now = now or datetime.now()
    return now > due
```

Tests pin `now` to a fixed value.

### Step 3 — Fake objects

```python
# 3_fake.py
class FakeRepo:
    def __init__(self): self.users = {}
    def save(self, u): self.users[u.id] = u
    def get(self, uid): return self.users.get(uid)

def register(repo, user):
    repo.save(user); return user
```

Test domain logic without a database.

### Step 4 — Recording calls (Spy)

```python
# 4_spy.py
class EmailSpy:
    def __init__(self): self.sent = []
    def send(self, to, body): self.sent.append((to, body))

def notify(email, user):
    email.send(user.email, "welcome")
```

Verify call count and arguments in tests.

### Step 5 — Isolate external calls

```python
# 5_adapter.py
class HttpClient:
    def get(self, path): ...

def fetch_user(uid, http: HttpClient):
    return http.get(f"/users/{uid}").json()
```

Concentrate external calls in a single adapter.

## How to Verify This in a Real Codebase

```bash
python -m pytest -q tests/test_total.py tests/test_notify.py
python -m pytest -q tests/test_http_adapter.py
```

**Expected output**

- Pure-function tests should finish almost instantly.
- Only adapter tests should cross real IO boundaries.

## Failure Modes to Watch

- `datetime.now()` or randomness still lives inside core logic.
- Mock count rises but the function responsibilities stay oversized.

## What to Notice in This Code

- The core logic knows nothing about IO.
- Time and randomness are always injected.
- Tests run fast against fake implementations.

## Five Common Mistakes

1. **Calling `datetime.now()` inside the function.** Tests break as time passes.
2. **Coupling DB and network with domain logic.** Unit tests disappear.
3. **Relying solely on mock libraries.** Hidden tight coupling remains.
4. **Public methods only for tests.** Encapsulation breaks.
5. **Global singletons.** Hard to isolate.

## How This Shows Up in Production

Strong teams use hexagonal / ports-and-adapters to keep the domain core away from IO. Thousands of unit tests still finish in under a second.

## How a Senior Engineer Thinks

- Starts with pure functions.
- Receives dependencies as arguments.
- Prefers fakes over mocks.
- Pushes time, randomness, and IO to the edges.
- Treats slow tests as a design smell.

## Checklist

- [ ] Is the core logic pure?
- [ ] Are external dependencies injected?
- [ ] Are time and randomness injected?
- [ ] Can tests run without IO using fakes?
- [ ] Do unit tests finish in under one second?

## Practice Problems

1. Replace one `datetime.now()` call in your code with an injected argument.
2. Unit-test one DB-bound function using a Fake.
3. Extract one external HTTP call into an adapter class.

## Wrap-up and Next Steps

Testability mirrors design. Next: how to safely change code — refactoring basics.

## Answering the Opening Questions

- **How should pure logic and side effects be separated?**
  - Extract computation-centric core as pure functions first; push time, HTTP, and DB side effects to thin adapters at the boundary. `total(items)` and `compute_invoice_total` stay in the core; `fetch_user(uid, http)` and adapter classes live at the edge.
- **How does dependency injection create test seams?**
  - Accepting external dependencies as arguments (`is_business_hour(now)`, `issue_coupon(user_id, clock)`, `fetch_user(uid, http)`) lets you substitute `FakeClock` or a fake HTTP client. Each injection point becomes a seam—the same logic wires differently in production vs test.
- **When should you use Fake vs Spy?**
  - Fake (`FakeRepo`, `FakePaymentGateway`) when you need a simplified stand-in that produces results. Spy (`EmailSpy`, `SpyNotifier`) when you need to verify call count and arguments. Simplify state/results → Fake. Verify interaction contract → Spy.

<!-- toc:begin -->
## In this series

- [Clean Code 101 (1/10): What Is Clean Code?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): Naming](./02-naming.md)
- [Clean Code 101 (3/10): Small Functions](./03-small-functions.md)
- [Clean Code 101 (4/10): Simplifying Conditionals](./04-simplifying-conditionals.md)
- [Clean Code 101 (5/10): Removing Duplication](./05-removing-duplication.md)
- [Clean Code 101 (6/10): Error Handling](./06-error-handling.md)
- [Clean Code 101 (7/10): Comments and Documentation](./07-comments-and-docs.md)
- **Testable Code (current)**
- Refactoring Basics (upcoming)
- Good Code Review Standards (upcoming)

<!-- toc:end -->

## References

- [Working Effectively with Legacy Code (M. Feathers)](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)
- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Mocks Aren't Stubs (Martin Fowler)](https://martinfowler.com/articles/mocksArentStubs.html)
- [Pytest — Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [Pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [Hexagonal architecture](https://alistair.cockburn.us/hexagonal-architecture/)
Tags: Computer Science, CleanCode, Testability, Testing, DependencyInjection, Refactoring

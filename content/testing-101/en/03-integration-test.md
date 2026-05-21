---
series: testing-101
episode: 3
title: "Testing 101 (3/10): Integration Test"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Testing
  - Integration
  - pytest
  - Database
  - HTTP
seo_description: Definition and hands-on for integration tests that exercise multiple modules together, including real DB and HTTP.
last_reviewed: '2026-05-04'
---

# Testing 101 (3/10): Integration Test

A fully green unit-test suite can still leave you staring at a production 500. The reason is simple: most incidents do not live *inside* one function. They live at the seams where HTTP handlers, services, repositories, and databases have to agree on shape, timing, and state.

Integration tests exist to exercise those seams on purpose. They cost more than unit tests, but they catch the exact kinds of contract drift that only appear once components start touching each other.

This is post 3 in the Testing 101 series. Here we show what integration tests verify, when to use a real DB or HTTP layer, and how to keep the suite useful without turning every PR into a long wait.

> Unit tests validate parts in isolation. Integration tests validate whether the assembled path still behaves like one coherent system.


![testing 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/03/03-01-concept-at-a-glance.en.png)
*testing 101 chapter 3 flow overview*
> Integration tests verify that the contract between modules stays intact as they evolve.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Integration Test?
- Which signal should the example or diagram make visible for Integration Test?
- What failure should be prevented first when Integration Test reaches a real system?

## What You Will Learn

- The definition of an *integration test* and how it differs from a unit test
- How to handle *real dependencies* like DB and HTTP
- *Test containers* and fixtures
- Strategies for managing *slow tests*
- Five common pitfalls

## Why It Matters

Most bugs live at *the seams* — DB schema, API contracts, authorization checks — *between modules*, not inside them. Integration tests cover those seams.

> Unit tests look at *parts*; integration tests look at *the assembly*.

## Concept at a Glance
Integration tests exercise two or more modules working together: typically a handler calling a service calling a repository, or a service calling an external API, running against a real or temporary database to catch schema mismatches and state transitions that unit tests cannot see.
## Key Terms

- **Integration test**: a test that exercises *two or more components* *together*.
- **Test container**: a temporary DB or Redis brought up *via container*.
- **Test database**: a *dedicated DB instance* or *transaction-rollback* pattern.
- **Seed data**: *initial data* the test assumes.
- **Slow test marker**: a tag that lets you *skip slow tests by default*.

## Before/After

**Before (unit only)**

```text
- 100 unit tests pass
- Production deploy returns 500 due to *missing DB column*
```

**After (with integration tests)**

```text
- 100 unit tests
- 5 integration tests for POST /users (real DB)
- The schema gap is *caught in CI* before deploy
```

## Hands-on: FastAPI + SQLite in Five Steps

### Step 1 — Code under test

```python
# src/app.py
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
engine = create_engine("sqlite:///./test.db", future=True)
Session = sessionmaker(bind=engine, future=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)

Base.metadata.create_all(engine)
app = FastAPI()

@app.post("/users")
def create_user(email: str):
    with Session() as s:
        u = User(email=email)
        s.add(u); s.commit(); s.refresh(u)
        return {"id": u.id, "email": u.email}
```

### Step 2 — Test client

```python
# tests/test_users_integration.py
from fastapi.testclient import TestClient
from src.app import app, Base, engine

def setup_function():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

client = TestClient(app)
```

### Step 3 — Happy path

```python
def test_create_user_returns_201_and_persists():
    res = client.post("/users", params={"email": "a@b.com"})
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "a@b.com"
```

### Step 4 — Duplicate handling

```python
def test_duplicate_email_fails():
    client.post("/users", params={"email": "a@b.com"})
    res = client.post("/users", params={"email": "a@b.com"})
    assert res.status_code in (400, 409, 500)  # whatever the policy, it must *fail*
```

### Step 5 — Slow test marker

```python
import pytest

@pytest.mark.slow
def test_large_batch_insert():
    for i in range(1000):
        client.post("/users", params={"email": f"u{i}@e.com"})
```

```bash
pytest -m "not slow"   # default
pytest -m slow         # nightly
```

## What to Notice in This Code

- The schema is *recreated before each test* → *state isolation*.
- Real *HTTP calls* are simulated, exercising routing too.
- Slow tests are *isolated by marker*, keeping the *normal cycle fast*.

## Five Common Mistakes

1. **Pointing tests at the *production DB*.** Dangerous — always use *a dedicated DB*.
2. **Sharing *data between tests*.** A reorder *breaks them*.
3. **Running slow tests *every time* until *PR cycle hits 30 minutes*.**
4. **Mocking *down to the DB*.** That is *not an integration test*.
5. **Testing *only happy paths*.** Failure cases prevent more *expensive bugs*.

## Verification Points

1. After the first `POST /users`, query the test database and confirm that the row truly exists. An HTTP 200 alone does not prove persistence worked.
2. Decide what duplicate-email failure should look like in your system and narrow the assertion to that policy. Leaving `400`, `409`, and `500` all acceptable hides regressions.
3. Run both `pytest -m "not slow"` and `pytest -m slow` so you know the fast PR path and the heavier verification path are genuinely separated.

**Expected output:** the happy path should confirm both response and persistence, and the duplicate path should be pinned to one deliberate failure policy.

## Failure Signals and First Checks

- If the suite can point at a production DB by accident, stop and fix isolation before doing anything else.
- If tests fail only when reordered, the reset or seeding strategy is still leaking state.
- If the status-code assertion is too broad, a real regression may stay green.

## How This Shows Up in Production

Most backend teams stand up a *real DB* with combinations like *Postgres + testcontainers*. External APIs are usually replaced by *VCR or mock servers*.

## How a Senior Engineer Thinks

- Believes most bugs come from *seams*.
- Keeps a *ratio* of unit to integration tests (the pyramid).
- Runs *slow tests* *at night*.
- Groups integration tests by *scenario*.
- Treats *state isolation* as the most important property.

## Checklist

- [ ] Integration tests touch a *real DB* or *real HTTP* layer.
- [ ] Each test starts from a *clean state*.
- [ ] Slow tests are *isolated by marker*.
- [ ] At least one failure path is tested.

## Practice Problems

1. Add a `GET /users` route and write *two* integration tests.
2. Verify a *400* response on bad input.
3. Confirm tests pass when *run in different order*.

## Wrap-up and Next Steps

Integration tests show what happens *when parts are connected*. The next post climbs further up to *E2E tests* that include the user-facing screen.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Integration Test?**
  - The article treats Integration Test as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Integration Test?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Integration Test reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Testing 101 (1/10): What Is Testing?](./01-what-is-testing.md)
- [Testing 101 (2/10): Unit Test](./02-unit-test.md)
- **Integration Test (current)**
- E2E Test (upcoming)
- Test Double (upcoming)
- Mock and Stub (upcoming)
- Test Coverage (upcoming)
- Regression Test (upcoming)
- Running Tests in CI (upcoming)
- Building a Test Strategy (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [pytest markers](https://docs.pytest.org/en/stable/example/markers.html)

### Practical Reading
- [Testcontainers](https://testcontainers.com/)
- [Martin Fowler — Integration Test](https://martinfowler.com/bliki/IntegrationTest.html)

Tags: Testing, Integration, pytest, Database, HTTP

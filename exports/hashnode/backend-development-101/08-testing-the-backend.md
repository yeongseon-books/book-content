
# Testing the Backend

> Backend Development 101 series (8/10)

<!-- a-grade-intro:begin -->

**Core question**: Why is "no time to write tests" the *biggest* time waste of all?

> Without tests, every change is a *bet*. A single unit test prevents *hours* of debugging later.

<!-- a-grade-intro:end -->

## What You Will Learn

- The difference between unit, integration, and E2E tests
- How to test a service with pytest
- How to call endpoints with FastAPI's `TestClient`
- How to test without spinning up a *real* database
- When to use fixtures and when to mock

## Why It Matters

Code without tests can be *read but not changed safely*. The mark of a good backend is *how easily it can be changed*, and automated tests are what create that safety.

> Tests are the *insurance* of code — invisible day to day, decisive in incidents.

## Concept at a Glance

```mermaid
flowchart LR
    Unit["Unit"] --> Int["Integration"]
    Int --> E2E["E2E"]
    Unit -->|"fast and many"| Pyramid
    E2E -->|"slow and few"| Pyramid
```

The test pyramid — *many* at the bottom, *few* at the top.

## Key Terms

- **Unit test**: verifies a *single* function or class.
- **Integration test**: verifies that several modules work *together*.
- **E2E test**: drives the *whole system* like a real user.
- **Fixture**: setup code written once and *reused*.
- **Mock**: a fake stand-in for an external dependency.

## Before/After

**Before (manual checks)**

```python
# Click around in the browser every time
```

**After (automatic verification)**

```python
def test_create_user(client):
    r = client.post("/users", json={"name": "Alice"})
    assert r.status_code == 200
    assert r.json()["name"] == "Alice"
```

Every case is verified before deploy.

## Hands-on: Five Steps Through Testing

### Step 1 — First pytest test

```python
# tests/test_basic.py
def add(a, b): return a + b

def test_add():
    assert add(2, 3) == 5
```

```bash
pytest -q
```

### Step 2 — Unit test a service with mocks

```python
# tests/test_user_service.py
from unittest.mock import MagicMock
from services.user_service import UserService

def test_register():
    repo = MagicMock()
    repo.insert.return_value = {"id": 1, "name": "A"}
    svc = UserService(repo)
    result = svc.register("A")
    repo.insert.assert_called_once()
    assert result["id"] == 1
```

### Step 3 — FastAPI TestClient

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200
```

### Step 4 — Fixture for in-memory DB

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from db import Base

@pytest.fixture
def engine():
    e = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(e)
    return e
```

### Step 5 — Dependency override

```python
# tests/test_with_db.py
def test_create_user(client, engine):
    app.dependency_overrides[get_engine] = lambda: engine
    r = client.post("/users", json={"name": "Bob"})
    assert r.status_code == 200
```

FastAPI's `dependency_overrides` lets you test *without a real database*.

## What to Notice in This Code

- Unit tests *cut external dependencies* with mocks.
- Integration tests *bind* with a real session.
- Fixtures keep the same setup from being repeated.

## Five Common Mistakes

1. **Doing only E2E.** They are slow, so *no one runs them*.
2. **Using `time.sleep` to wait inside tests.** They become flaky — poll or mock instead.
3. **Sharing database state between tests.** Cross-test interference — always isolate.
4. **Mocking too much.** Real behavior never gets verified.
5. **Calling without asserting.** That is *execution*, not *verification*.

## How This Shows Up in Production

CI (GitHub Actions and friends) runs `pytest` on every PR. Units take *seconds*, integration *tens of seconds*, E2E *minutes* — break that distribution and dev speed stalls. Seniors keep an eye on the *pyramid shape*.

## How a Senior Engineer Thinks

- A new feature ships *with its tests*.
- Reproduce a bug with a *test* before fixing it.
- Test names read like *sentences* (`test_user_with_zero_age_returns_422`).
- Mock at the *external boundary*, not the internals.
- Risk areas matter more than coverage numbers.

## Checklist

- [ ] You can run a first pytest test.
- [ ] You can unit test a service with mocks.
- [ ] You can call endpoints with TestClient.
- [ ] You can write an in-memory DB fixture.
- [ ] You can use `dependency_overrides`.

## Practice Problems

1. Unit test `OrderService.create` with a mock repository.
2. Verify that `POST /login` with the wrong password returns 401.
3. Add an integration test for the same endpoint using the in-memory DB.

## Wrap-up and Next Steps

Tests are the *safety net for change*. Next, we deliver the code to real users — *deploying the backend*.

- [What Is Backend Development?](./01-what-is-backend-development.md)
- [Building an HTTP Server](./02-building-an-http-server.md)
- [Routing and Controllers](./03-routing-and-controllers.md)
- [The Service Layer](./04-service-layer.md)
- [The Database Layer](./05-database-layer.md)
- [Authentication and Authorization](./06-auth-and-authorization.md)
- [Logging and Error Handling](./07-logging-and-error-handling.md)
- **Testing the Backend (current)**
- Deploying the Backend (upcoming)
- A Production-Ready Backend Structure (upcoming)
## References

- [pytest documentation](https://docs.pytest.org/en/stable/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing pyramid (Martin Fowler)](https://martinfowler.com/articles/practical-test-pyramid.html)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

Tags: Backend, Testing, Pytest, Python, QualityAssurance

---

© 2026 YeongseonBooks. All rights reserved.

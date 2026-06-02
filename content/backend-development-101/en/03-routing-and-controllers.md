---
series: backend-development-101
episode: 3
title: "Backend Development 101 (3/10): Routing and Controllers"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Backend
  - FastAPI
  - Architecture
  - REST
  - Python
seo_description: Split routers from controllers and learn the difference between path, query, and body parameters so your backend stays clean as it grows.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (3/10): Routing and Controllers

A single file feels fine when your API only has a few endpoints. Once features start stacking up, though, the real problem is not line count but the constant question of where each new path, validation rule, and response shape should live.

This is the 3rd post in the Backend Development 101 series. Here, we split routers from controllers, separate path, query, and body parameters, and build the first structure that still reads cleanly after the endpoint count grows.


![backend development 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/03/03-01-concept-at-a-glance.en.png)
*backend development 101 chapter 3 flow overview*

## Questions to Keep in Mind

- The difference between routers and controllers?
- The difference between path, query, and body parameters?
- How to design REST-style endpoints?

## Why It Matters

In a tiny project, a single file works. As endpoints grow, that single file *becomes hell*. Splitting layers from day one makes "where does this code go?" obvious for every new feature.

> Good structure removes the question of *where to put code*.

Routers are the *map*, controllers are the *front desk*, services are the *experts*.

## Key Terms

- **Router**: maps URL patterns to handlers.
- **Controller**: receives the request, validates it, calls a service.
- **Path parameter**: `{id}` in `/users/{id}`.
- **Query parameter**: `active` in `/users?active=true`.
- **Body**: the JSON payload of a POST or PUT request.

## Before/After

**Before (everything in one file)**

```python
# main.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def list_users(): ...

@app.get("/orders")
def list_orders(): ...

@app.get("/products")
def list_products(): ...
```

**After (one router per module)**

```python
# routers/users.py
from fastapi import APIRouter
router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
def list_users():
    return []

# main.py
from fastapi import FastAPI
from routers import users, orders
app = FastAPI()
app.include_router(users.router)
app.include_router(orders.router)
```

Each feature gets its own file, so it is obvious *where to make a change*.

## Hands-on: Five Steps to Tidy Routing

### Step 1 — Path parameters

```python
# 1_path.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}
```

### Step 2 — Query parameters

```python
# 2_query.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def list_users(active: bool = True, limit: int = 10):
    return {"active": active, "limit": limit}
```

### Step 3 — JSON body

```python
# 3_body.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserIn(BaseModel):
    name: str
    age: int

@app.post("/users")
def create_user(payload: UserIn):
    return {"id": 1, **payload.model_dump()}
```

### Step 4 — Split the router

```python
# routers/products.py
from fastapi import APIRouter
router = APIRouter(prefix="/products", tags=["products"])

@router.get("")
def list_products():
    return []

@router.get("/{pid}")
def get_product(pid: int):
    return {"id": pid}
```

### Step 5 — Controller calls the service

```python
# controllers/user_controller.py
from services.user_service import UserService

class UserController:
    def __init__(self, svc: UserService):
        self.svc = svc

    def create(self, payload):
        return self.svc.register(payload.name, payload.age)
```

Controllers stay *thin* — validate, then delegate.

## Verification points

**Expected output:** `/users/10` should return `{"id": 10}`, and `GET /users?active=false&limit=5` should echo the filter values in JSON.

### First failure modes to check

- A wrong path-parameter type should produce `422`, which is the framework doing its validation job.
- If split routers do not show up, check `include_router()` before changing any business code.
- When a controller starts growing, make sure only input mapping and service delegation remain there.

## What to Notice in This Code

- Use path for *identity*, query for *filtering*.
- Body is meaningful only for POST, PUT, and PATCH.
- `tags` *groups* endpoints in the OpenAPI docs.

## Five Common Mistakes

1. **Stuffing everything into the query string.** Filters use query; new resources use body.
2. **Putting business logic in controllers.** Move it to services for reuse and testing.
3. **Using verbs in URLs like `/getUsers`.** REST uses *nouns plus HTTP methods*.
4. **Sending unvalidated input straight to the database.** Always model with Pydantic.
5. **Mutating state with GET.** GET must be *safe*.

## How This Shows Up in Production

Large backends have one router directory per domain (`routers/orders.py`, `routers/payments.py`). When a new feature lands, you only decide *which router* gains *which path*.

### Four Production Incident Scenarios

**1. The 200-line handler.** Auth, parsing, validation, business logic, external calls, and error mapping all in one function. One change causes regression. Fix: extract service layer, leave controller as orchestration-only.

**2. Auth applies to some routes but not others.** Global middleware forces awkward exceptions. Fix: separate routers with explicit dependencies:

```python
private_router = APIRouter(prefix="/users", dependencies=[Depends(get_current_user)])
public_router = APIRouter(prefix="/users")  # no auth dependency
```

**3. URL collision across teams.** Two developers declare the same path independently. Code review alone won't catch it. Fix: maintain a router registration table, run OpenAPI spec diff in CI, keep a single `include_router` assembly file.

**4. 422 log explosion from path type mismatch.** Clients send strings to `int` path params. Server correctly returns 422, but dashboards show an error spike. Fix: monitor 422 rate separately (it's a client contract violation, not server instability), and enforce client-side SDK validation.

### Team Routing Convention Table

| Aspect | Rule | Enforcement |
| --- | --- | --- |
| Resource naming | Plural nouns (`users`, `orders`) | Code review checklist |
| Path parameters | Identifiers only (`{user_id}`) | Type hints + tests |
| Query parameters | Filter/sort/page only | OpenAPI param inspection |
| Create/update input | Body model required | Pydantic schema check |
| Controller length | 30–50 lines max | Static analysis + review |
| Router assembly | Single entry-point file | CI duplicate-path check |

### Observability Implications of Routing Design

- **Log cardinality**: Excessive path variables explode metric label cardinality.
- **Cache efficiency**: Unbounded query combinations kill cache hit rates.
- **Error classification**: Clean 4xx/5xx separation in controllers improves alert signal quality.
- **Traceability**: Domain-router-level tags make OpenTelemetry span analysis straightforward.

## How a Senior Engineer Thinks

- **URLs are nouns; actions are HTTP methods.** `POST /orders` not `POST /createOrder`. This isn't pedantry—it's what keeps 50+ endpoints consistent across a team.
- **A controller fits on one screen.** If you scroll, the handler is doing too much. Extract to service, test the service independently.
- **Inputs are always modeled with Pydantic.** Untyped `dict` inputs produce meaningless OpenAPI docs and force consumers to guess. Type declarations ARE the contract.
- **Auth and logging attach at the router level.** Not per-handler, not globally. Router-scoped dependencies make policy visible in the code structure.
- **Before adding an endpoint, ask if an existing one can be extended.** Query params and body fields are cheaper than new endpoints. Fewer endpoints = fewer things to version, document, and monitor.
## Checklist

- [ ] You can distinguish path, query, and body parameters.
- [ ] You can split routes with APIRouter.
- [ ] You can design noun-based REST URLs.
- [ ] You understand the controller-to-service flow.
- [ ] You have opened the OpenAPI docs at `/docs`.

## Practice Problems

1. Build an `/orders` router with `GET /orders`, `GET /orders/{id}`, and `POST /orders`.
2. Add a `?role=admin` filter to `GET /users`.
3. Define a Pydantic `OrderIn` model and verify a bad payload returns `422`.

## Wrap-up and Next Steps

Routers are the *map*; controllers are the *front desk*. Next, we open the door behind the desk — the Service Layer that holds the *business rules*.

## Answering the Opening Questions

- **What should router and controller each be responsible for?**
  - The router maps URL patterns without conflicts and declares shared dependencies (auth, context). The controller receives validated input, orchestrates service calls, and finalizes the response contract—remaining a thin orchestrator.
- **When and how should path, query, and body parameters be separated?**
  - Resource identifiers go in path; query conditions and sort/page options in query; creation/modification payloads and sensitive data in body. This separation directly affects cache-key composition, URL exposure surface, and 422 error observability.
- **What criteria guide REST-style endpoint design?**
  - URLs use plural-noun resources; action semantics come from HTTP methods. Idempotency, nesting depth, versioning strategy, and deprecation policy must be designed together for a predictable production API.

<!-- toc:begin -->
## In this series

- [Backend Development 101 (1/10): What Is Backend Development?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): Building an HTTP Server](./02-building-an-http-server.md)
- **Routing and Controllers (current)**
- The Service Layer (upcoming)
- The Database Layer (upcoming)
- Authentication and Authorization (upcoming)
- Logging and Error Handling (upcoming)
- Testing the Backend (upcoming)
- Deploying the Backend (upcoming)
- A Production-Ready Backend Structure (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [FastAPI Path operations](https://fastapi.tiangolo.com/tutorial/path-params/)
- [FastAPI APIRouter](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)

### Further Reading

- [REST API Tutorial](https://restfulapi.net/)

Tags: Backend, FastAPI, Architecture, REST, Python

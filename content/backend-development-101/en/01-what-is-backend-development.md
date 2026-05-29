---
series: backend-development-101
episode: 1
title: "Backend Development 101 (1/10): What Is Backend Development?"
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
  - WebDevelopment
  - HTTP
  - Architecture
  - Python
seo_description: A clear map of backend development — HTTP servers, routing, services, databases, auth, and deployment for engineers starting their first backend role.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (1/10): What Is Backend Development?

Users only see the screen, but the part that keeps a service trustworthy is the code behind it. If you cannot explain where a request enters, where rules live, and where data stops being trustworthy, you can add features quickly but you cannot operate the system for long.

This is the first post in the Backend Development 101 series. Here, we define backend development as a set of responsibilities — receiving requests, applying rules, touching data, and returning responses — instead of treating it as one vague technical label.


![backend development 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/01/01-01-concept-at-a-glance.en.png)
*backend development 101 chapter 1 flow overview*

## Questions to Keep in Mind

- The role and the boundaries of a backend?
- The five layers that form a backend system?
- The path of one request through that system?

## Why It Matters

Building only the frontend lets you ship *what the user sees*. Building the backend lets you ship *systems that survive*. Data, authentication, consistency, and operations all live behind the screen, and someone has to design them.

> The backend is invisible, but it decides everything.

Requests flow left to right; responses retrace the same path.

## Key Terms

- **HTTP server**: the front door for requests.
- **Router**: chooses which function will produce the response.
- **Service**: the layer that holds business rules.
- **Repository**: the conversation with the database.
- **Middleware**: behavior that runs on *every* request.

## Before/After

**Before (the frontend does everything)**

```python
# A password check inside the browser
if password == "admin123":
    show_dashboard()
```

**After (the backend owns the rule)**

```python
# server.py
@app.post("/login")
def login(body):
    if not auth.verify(body["email"], body["password"]):
        return 401, {"error": "invalid"}
    return 200, {"token": auth.token(body["email"])}
```

Password verification belongs to the *server*; the client only consumes the result.

## Hands-on: Your First Backend in Five Steps

### Step 1 — The smallest server

```python
# 1_app.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def hello():
    return {"message": "hello"}
```

### Step 2 — Run it

```bash
uvicorn 1_app:app --reload
```

Open `http://127.0.0.1:8000/` and you will see JSON.

### Step 3 — Add a route

```python
# 2_routes.py
from fastapi import FastAPI
app = FastAPI()

USERS = [{"id": 1, "name": "Alice"}]

@app.get("/users")
def list_users():
    return USERS
```

### Step 4 — Accept input

```python
# 3_input.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserIn(BaseModel):
    name: str

@app.post("/users")
def create_user(payload: UserIn):
    return {"id": 99, "name": payload.name}
```

### Step 5 — Call it

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"name":"Bob"}' http://127.0.0.1:8000/users
```

You get JSON back.

## Verification points

**Expected output:** after `uvicorn 1_app:app --reload`, `/` should return `{"message": "hello"}` and `POST /users` should return JSON for the new user.

### First failure modes to check

- If `uvicorn` cannot import `1_app:app`, confirm the filename and app object name match.
- If `POST /users` returns `422`, verify the payload still includes the `name` field.
- An empty `GET /users` response is fine here; the point is verifying the request path reaches the handler and returns data.

## What to Notice in This Code

- A server is a *path-to-function* mapping.
- Input is *validated* before it reaches your function.
- The response is *data* (JSON), not a screen.

## Five Common Mistakes

1. **Equating backend with database code.** It also covers routing, auth, validation, and logging.
2. **Putting all logic inside route handlers.** One file becomes a thousand lines.
3. **Trusting client-side validation.** The server must always validate again.
4. **Returning 500 for every error.** Use meaningful codes like 400, 404, and 409.
5. **Skipping logs.** You will never know what happened in production.

## How This Shows Up in Production

The shape of a backend is similar from a startup to a large company — Router, Service, Repository, and Middleware. Learn the *layer split* once and you can join almost any team without relearning structure. Skip it and every codebase feels foreign.

## How a Senior Engineer Thinks

- Business rules live in services, not routes.
- Every input gets validated, every time.
- Every dependency can be injected for testing.
- Logs and metrics are designed alongside the code.
- The bar is "operable", not "it works on my machine".

## Checklist

- [ ] You can name the five backend layers.
- [ ] You can run the smallest FastAPI server.
- [ ] You can tell GET from POST.
- [ ] You can explain why input validation matters.
- [ ] You know what the next chapter covers.

## Practice Problems

1. Add a `/health` route that returns `{"status": "ok"}`.
2. Add `GET /users/{user_id}` and echo the path parameter.
3. Make `POST /login` return `401` when the password is wrong.

## Wrap-up and Next Steps

The backend is a *set of responsibilities*. Next, we open up the lowest layer and build an *HTTP server* by hand to see how it really works.

## Answering the Opening Questions

- **What role and boundaries define the backend layer?**
  - The backend is the control layer that receives requests, applies rules, safely mutates data, and classifies failures into responses. The 5-layer model (HTTP handling, route contract, shared policy, business rules, storage access) enables fast root-cause isolation in production.
- **How does a single request traverse HTTP server, router, service, and database?**
  - In the `POST /orders` example: the server accepts the connection, the router selects a handler, middleware assigns request ID and timing, the service validates rules, and the repository persists. Failures differ by layer—distinguishing 422, 400, and 500 keeps alerting and response accurate.
- **Why understand the backend as multiple layers rather than one monolith?**
  - Layer separation enables testing rules with fake repositories, limits change scope when swapping storage, and reduces team ownership conflicts. Same functionality, but a layered structure dramatically reduces incident analysis time and regression bugs.


## Why Layering Actually Pays Off

### Testability: Swap One Layer with a Fake

The first payoff of layer separation is testing. Replace the Repository with a fake in your Service tests, and rule verification runs without a database.

```python
class FakeOrderRepository:
    def __init__(self):
        self.saved = []

    def save(self, order_id, user_id, item_id, quantity):
        row = {
            "order_id": order_id,
            "user_id": user_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "created",
        }
        self.saved.append(row)
        return row

def test_create_order_rejects_invalid_quantity():
    repo = FakeOrderRepository()
    svc = OrderService(repo)

    try:
        svc.create_order("u1", "i1", 0)
        assert False, "should have raised"
    except ValueError:
        assert len(repo.saved) == 0
```

The key assertion is "no save happens when a rule is violated." Integration tests alone make this slow to verify and hard to isolate.

### Replaceability: Localize Storage Changes

You may start with SQLite or a single PostgreSQL instance. As traffic grows, you need read caches, sharding, or async message-queue processing. With a Repository boundary, the Service code stays untouched while only the storage implementation changes.

For example, swapping `PostgresOrderRepository` for `DynamoOrderRepository` while keeping the same interface means only the DI configuration changes. When that change does not cascade into routes and business rules, deployment risk drops dramatically.

### Team Boundaries: Clear Ownership

With 2 people the difference is negligible, but at 6+ ownership matters. API contract = platform/backend shared ownership; domain rules = service team; query optimization = data team. Clear layer boundaries reduce merge conflicts and keep reviews focused.

Without responsibility boundaries, a single PR changes a route, an auth policy, and an index simultaneously. Reviews become shallow, and incidents become compound. Layering is not an architecture preference — it is a device for stabilizing team work units.

## Before/After: Same Feature, Two Structures

Both code samples below implement "create order." Same functionality, different operational quality.

### Before: All Responsibilities in One Handler

```python
@app.post("/orders")
def create_order(payload: dict):
    # Input validation
    if "user_id" not in payload or "item_id" not in payload:
        return {"error": "invalid"}, 400

    quantity = int(payload.get("quantity", 0))
    if quantity < 1:
        return {"error": "invalid quantity"}, 400

    # Auth check (in reality, an external service call)
    token = payload.get("token")
    if token != "allow":
        return {"error": "forbidden"}, 403

    # Data storage
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders(user_id, item_id, quantity) VALUES (%s, %s, %s) RETURNING id",
        (payload["user_id"], payload["item_id"], quantity),
    )
    order_id = cur.fetchone()[0]
    conn.commit()

    # Logging
    print("created", order_id)

    # External notification
    send_webhook(order_id)

    return {"order_id": order_id}, 201
```

The problem is not length — it is coupling. This function handles input, authorization, storage, logging, and external communication simultaneously. If `send_webhook` fails, the retry strategy is unclear. When DB commit and notification failure interleave, there is no consistency policy. Testing is effectively only possible as integration tests.

### After: Same Feature, Layered

```python
# router.py
@router.post("/orders", status_code=201)
def create_order(payload: CreateOrderRequest, request: Request):
    result = order_service.create_order(
        actor_token=request.headers.get("authorization"),
        user_id=payload.user_id,
        item_id=payload.item_id,
        quantity=payload.quantity,
    )
    return result

# service.py
class OrderService:
    def __init__(self, authz: AuthzClient, repo: OrderRepository, outbox: EventOutbox):
        self.authz = authz
        self.repo = repo
        self.outbox = outbox

    def create_order(self, actor_token: str, user_id: str, item_id: str, quantity: int) -> dict:
        if quantity < 1:
            raise DomainError("quantity must be >= 1")

        if not self.authz.can_create_order(actor_token, user_id):
            raise PermissionDenied("not allowed")

        order = self.repo.create(user_id=user_id, item_id=item_id, quantity=quantity)
        self.outbox.enqueue("order.created", {"order_id": order["id"]})
        return order
```

The advantage: failure points are explicit. Auth failure = `PermissionDenied`; rule violation = `DomainError`; persistence failure = Repository exception. Observability and retry policies can be designed per layer, making operational response faster.

## Hands-on: Building a 5-Layer Backend with FastAPI

This section is not a quick tutorial — it verifies *why* each step is necessary.

### Step 1: Minimal Server — Separate the Network Boundary

```python
# app.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
```

```bash
uvicorn app:app --reload --port 8000
```

What to verify here is not the application function but the server boundary. Port binding, process startup, and a basic health response must be stable before subsequent layers have meaning.

### Step 2: Router Separation — Fix the API Surface

```python
# routes/orders.py
from fastapi import APIRouter

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/")
def list_orders():
    return []
```

```python
# app.py
from fastapi import FastAPI
from routes.orders import router as orders_router

app = FastAPI()
app.include_router(orders_router)
```

Route separation is not mere file organization. When a team reviews API changes, looking at the router directory immediately shows the scope of contract changes.

### Step 3: Middleware — Establish Observability Defaults

```python
# middlewares/request_id.py
import time
import uuid
from fastapi import Request

async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", uuid.uuid4().hex)
    request.state.request_id = request_id

    started = time.time()
    response = await call_next(request)
    elapsed_ms = int((time.time() - started) * 1000)

    response.headers["x-request-id"] = request_id
    response.headers["x-elapsed-ms"] = str(elapsed_ms)
    return response
```

```python
# app.py
app.middleware("http")(request_id_middleware)
```

This step matters because "we'll add logging later" rarely survives production. After an incident, adding logs retroactively means the root-cause window has no data.

### Step 4: Service — Consolidate Use-Case Rules

```python
# services/order_service.py
class OrderService:
    def __init__(self, repo):
        self.repo = repo

    def create(self, user_id: str, item_id: str, quantity: int):
        # Domain rule: minimum order quantity
        if quantity < 1:
            raise ValueError("quantity must be >= 1")

        return self.repo.create(user_id=user_id, item_id=item_id, quantity=quantity)
```

Consolidating rules in a service enables reuse and testing. The same rule can be shared across API, batch jobs, and message consumers.

### Step 5: Repository — Isolate Storage Dependencies

```python
# repositories/order_repository.py
class OrderRepository:
    def __init__(self, db):
        self.db = db

    def create(self, user_id: str, item_id: str, quantity: int):
        row = self.db.execute(
            """
            INSERT INTO orders(user_id, item_id, quantity)
            VALUES (:user_id, :item_id, :quantity)
            RETURNING id, user_id, item_id, quantity
            """,
            {"user_id": user_id, "item_id": item_id, "quantity": quantity},
        ).fetchone()
        return dict(row)
```

Isolating storage localizes not only DB swaps but also transaction policy changes. When performance issues arise, the query tuning scope stays narrow.

## Common Mistakes and Why They Escalate

| Mistake | Why it feels convenient | Where it breaks | Root cause |
| --- | --- | --- | --- |
| All logic in route handler | Only one file to check | Change conflicts as features grow | No boundary → test/review unit collapses |
| Skipping server-side validation | Frontend already checks | Malicious requests / version mismatch | Client is outside the trust boundary |
| Returning 500 for all errors | Simpler error handling code | Cannot classify incidents | User errors mixed with system errors |
| Exposing DB model as API response | No transformation code needed | Schema change breaks clients | Internal model ≠ external contract |
| Logs without context | Faster to implement | Cannot reproduce issues | Missing request ID, user ID, path info |

Each mistake is not a code-style issue but an operational-cost issue. For example, failing to distinguish 400 from 500 causes excessive alerting, and the team misses real incident signals. Not separating response schemas means a single DB migration cascades into client outages.

The habit of structurally analyzing "why did this happen?" matters. Incidents typically start from missing boundaries, not single-line bugs.

## How a Senior Engineer Decides

A senior defines "which failure to absorb where" before choosing frameworks. For the order-creation use case: input validation failures terminate immediately as 4xx; external payment failures route to retry/compensation transactions; DB consistency is guaranteed within transaction boundaries. The failure flow is drawn before the feature flow.

Second, boundaries are reflected simultaneously in code structure and operational metrics. Each service-layer method defines domain events; middleware attaches request context; the repository layer measures query latency. When a "it's slow" report arrives, layer-by-layer candidate causes can be narrowed immediately.

Third, trade-offs are made explicit. Perfect separation everywhere slows initial development. A senior decides which boundaries to fix now and which to defer, based on team context. For example, at the MVP stage, keep a single DB but introduce the Service/Repository boundary early to reduce future extension costs. The goal is not ideal architecture but keeping change costs at a predictable level.

<!-- toc:begin -->
## In this series

- **What Is Backend Development? (current)**
- Building an HTTP Server (upcoming)
- Routing and Controllers (upcoming)
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

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [The Twelve-Factor App](https://12factor.net/)

### Further Reading

- [Backend roadmap](https://roadmap.sh/backend)

Tags: Backend, WebDevelopment, HTTP, Architecture, Python

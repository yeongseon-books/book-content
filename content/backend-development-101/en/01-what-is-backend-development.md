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

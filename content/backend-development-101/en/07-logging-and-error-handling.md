---
series: backend-development-101
episode: 7
title: "Backend Development 101 (7/10): Logging and Error Handling"
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
  - Logging
  - Observability
  - Python
  - ErrorHandling
seo_description: Use structured logging and a global exception handler to diagnose backend incidents in minutes instead of hours.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (7/10): Logging and Error Handling

When the pager goes off at 3 a.m., re-reading the code is rarely the fastest path to an answer. What matters in production is whether the system leaves enough evidence behind to explain a failed request from logs and error responses alone.

This is the 7th post in the Backend Development 101 series. Here, we focus on three operating basics — structured logs, request IDs, and global exception handling — so incidents become something you can read instead of reconstructing from memory.


![backend development 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/07/07-01-concept-at-a-glance.en.png)
*backend development 101 chapter 7 flow overview*

## Questions to Keep in Mind

- Why we use a logger instead of `print`?
- The shape of a structured log?
- How a global exception handler keeps responses consistent?

## Why It Matters

Code is written once and *operated for years*. Ninety percent of operations is *reading*, and the reading tool is the log. Building structured logs from day one cuts incident response time by *orders of magnitude*.

> Good logs are read more often than the code itself.

Every path leads to the *log*.

## Key Terms

- **Logger**: object that emits log records.
- **Log level**: DEBUG / INFO / WARNING / ERROR / CRITICAL.
- **Structured log**: a log line in a *machine-readable* format (often JSON).
- **request_id**: identifier that follows a single request through every layer.
- **Global exception handler**: the *one place* that turns exceptions into responses.

## Before/After

**Before (print debugging)**

```python
print("user=", user_id, "error", e)
```

**After (structured log)**

```python
import logging, json
log = logging.getLogger("app")

log.error(json.dumps({
    "event": "order_failed",
    "user_id": user_id,
    "error": str(e),
}))
```

The `event` field alone makes the data *aggregable*.

## Hands-on: Five Steps Through Logs and Errors

### Step 1 — Standard logger setup

```python
# 1_setup.py
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
log = logging.getLogger("app")
log.info("server started")
```

### Step 2 — JSON structured log

```python
# 2_json_log.py
import logging, json, sys
class JsonFmt(logging.Formatter):
    def format(self, r):
        return json.dumps({"level": r.levelname, "msg": r.getMessage()})
h = logging.StreamHandler(sys.stdout)
h.setFormatter(JsonFmt())
logging.basicConfig(handlers=[h], level=logging.INFO)
logging.info("hello")
```

### Step 3 — request_id middleware

```python
# 3_request_id.py
from fastapi import FastAPI, Request
import uuid, logging

app = FastAPI()
log = logging.getLogger("app")

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = str(uuid.uuid4())
    request.state.rid = rid
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    log.info(f"req rid={rid} path={request.url.path}")
    return response
```

### Step 4 — Global exception handler

```python
# 4_global_handler.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class DomainError(Exception):
    def __init__(self, code: str, message: str):
        self.code, self.message = code, message

@app.exception_handler(DomainError)
async def handle_domain(_: Request, exc: DomainError):
    return JSONResponse(
        status_code=400,
        content={"code": exc.code, "message": exc.message},
    )
```

### Step 5 — Picking log levels

```python
# 5_levels.py
log.debug("trace data")
log.info("user logged in")
log.warning("retrying upstream call")
log.error("payment failed")
log.critical("database is down")
```

## Verification points

**Expected output:** log lines produced during the same request should share one `request_id`, and `DomainError` should always become the same JSON error shape.

### First failure modes to check

- If logs are hard to search, confirm the JSON formatter still emits one line per event.
- If `X-Request-ID` is missing from responses, inspect the middleware where the response header is set.
- If stack traces never appear, some exception path is swallowing errors before they reach the logger.

## What to Notice in This Code

- A log line stays on *one line* so search works.
- Every log includes the request_id so traces are possible.
- Domain errors carry *business meaning* via stable codes.

## Five Common Mistakes

1. **Stopping at print debugging.** Prints *disappear* in production.
2. **Logging everything as ERROR.** Alarms become noise and real incidents get missed.
3. **Logging passwords or tokens.** That is an immediate security incident.
4. **Catching everything and ignoring it.** Errors *vanish silently*.
5. **Saving only the message and dropping the stack trace.** Debugging becomes guesswork.

## How This Shows Up in Production

In production logs flow into *collectors* (CloudWatch, Loki, Datadog). A field like `event=order_failed` becomes the basis of *dashboards and alerts*. Adopting structured logs early gets you monitoring almost for free.

## How a Senior Engineer Thinks

- Logs are *aggregable data*.
- The request_id is *always* echoed in the response header.
- Domain errors and infra errors stay *separate*.
- Logs that page someone are *actionable*.
- "Why did this fail?" can be answered from the logs alone.

## Checklist

- [ ] You can configure the standard logger.
- [ ] You can emit JSON structured logs.
- [ ] You can write a request_id middleware.
- [ ] You can register a global exception handler.
- [ ] You can choose log levels with intent.

## Practice Problems

1. Add `request_id` to every JSON log line automatically.
2. Define `DomainError` and `InfraError` and handle them separately.
3. Inject a fake exception into a route and confirm the stack trace shows in the log.

## Wrap-up and Next Steps

Good logs and consistent error handling are the *eyes of operations*. Next, we make the code safe to change with *backend testing*.

## Answering the Opening Questions

- **Why we use a logger instead of `print`?**
  - The article treats Logging and Error Handling as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **The shape of a structured log?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How a global exception handler keeps responses consistent?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Backend Development 101 (1/10): What Is Backend Development?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): Building an HTTP Server](./02-building-an-http-server.md)
- [Backend Development 101 (3/10): Routing and Controllers](./03-routing-and-controllers.md)
- [Backend Development 101 (4/10): The Service Layer](./04-service-layer.md)
- [Backend Development 101 (5/10): The Database Layer](./05-database-layer.md)
- [Backend Development 101 (6/10): Authentication and Authorization](./06-auth-and-authorization.md)
- **Logging and Error Handling (current)**
- Testing the Backend (upcoming)
- Deploying the Backend (upcoming)
- A Production-Ready Backend Structure (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [Python logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [FastAPI exception handlers](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Twelve-Factor logs](https://12factor.net/logs)

### Further Reading

- [structlog docs](https://www.structlog.org/en/stable/)

Tags: Backend, Logging, Observability, Python, ErrorHandling

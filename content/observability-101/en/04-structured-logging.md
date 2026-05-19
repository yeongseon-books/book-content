---
series: observability-101
episode: 4
title: Structured Logging
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Observability
  - Logging
  - Python
  - JSON
  - DevOps
seo_description: Replace print with JSON logs that carry level and context, so production debugging becomes a query instead of a grep.
last_reviewed: '2026-05-15'
---

# Structured Logging

Many incident reviews reveal the same problem: logs existed, but the team still could not answer the first two questions quickly. Which request failed, and what was different about it? Free-form lines are readable, but they are poor query surfaces.

Structured logging fixes that by turning log lines into data with fields you can filter, aggregate, and join with traces.

This is post 4 in the Observability 101 series.

## Questions this article answers

- Why do free-form logs hit a limit so quickly in production?
- What changes when logs become structured data?
- How should you choose between log levels?
- How should a per-request correlation ID flow through the system?
- How should you handle sensitive data in logs?

## Why It Matters

To find the responsible line *within five minutes* of an incident, logs must be *queryable*. The age of `print` is over.

> *A log is *data*, not prose.*

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/04/04-01-concept-at-a-glance.en.png)
*Application events become one-line JSON records, flow to a log backend, and come back as field-based queries during incident response.*

## Key Terms

- **Level**: DEBUG / INFO / WARNING / ERROR / CRITICAL.
- **Structured fields**: one key=value pair at a time.
- **Correlation ID**: an ID that *binds* a single request.
- **Sink**: where logs are *shipped*.
- **Sampling**: keeping *only a portion* when volume is high.

## Before/After

**Before**: `print(f"user {uid} failed: {e}")` — regex *hell*.

**After**: `logger.error("login_failed", user_id=uid, reason=str(e))` — *one query*.

## Hands-on: Structured Logging in 5 Steps

### Step 1 — Basic Python `logging`

```python
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")
log.info("started")
```

### Step 2 — JSON formatter

```python
import json, logging

class JsonFmt(logging.Formatter):
    def format(self, r):
        return json.dumps({"lvl": r.levelname, "msg": r.getMessage(),
                            **getattr(r, "extra", {})})

h = logging.StreamHandler(); h.setFormatter(JsonFmt())
log = logging.getLogger("app"); log.addHandler(h); log.setLevel("INFO")
```

### Step 3 — Context fields

```python
def login(uid):
    log.info("login_attempt", extra={"extra": {"user_id": uid}})
```

### Step 4 — Correlation ID

```python
import uuid
def handle(req):
    rid = req.headers.get("x-request-id") or str(uuid.uuid4())
    log.info("request_in", extra={"extra": {"rid": rid}})
```

### Step 5 — Level policy

```text
DEBUG    → development detail
INFO     → normal events
WARNING  → cautions (actionable)
ERROR    → failed requests
CRITICAL → system risk
```

## How to Follow One Request

The practical win is simple: collect every line for one request without guessing the wording.

```bash
grep '"rid": "req-7f2a"' app.log
grep '"lvl": "ERROR"' app.log | grep '"rid": "req-7f2a"'
```

```json
{"lvl":"INFO","msg":"request_in","rid":"req-7f2a","path":"/login"}
{"lvl":"ERROR","msg":"login_failed","rid":"req-7f2a","reason":"db_timeout"}
```

```text
Expected output:
- Every line for the same request clusters under one request ID.
- The ERROR line exposes the failure class immediately.
- Sensitive fields such as email or phone number appear masked or hashed, not raw.
```

## What to Notice in This Code

- `extra` lets you add *arbitrary fields*.
- The *correlation ID* flows on every line.
- One JSON line ships into *Loki, ELK, or BigQuery* equally well.

## Five Common Mistakes

1. **Using only `print`.** *Unsearchable*.
2. **Logging everything at *INFO*.** Real signal *drowns*.
3. **Logging PII *as is*.** Compliance violation.
4. **Only *interpolating into the message*.** No fields, no query.
5. **Collapsing stack traces *into one line*.** Worst readability.

## How This Shows Up in Production

Most teams ship *JSON logs → Loki or ELK → Grafana / Kibana*. The correlation ID *links* logs to traces.

## How a Senior Engineer Thinks

- *A log is an *event*, not a *sentence*.*
- *Every request carries a *correlation ID*.*
- *Levels split by *actionability*.*
- *PII gets *masked* or *hashed*.*
- *DEBUG is *off in prod*; have a *switch* to flip it.*

## Checklist

- [ ] You emit one line as *JSON*.
- [ ] You have a *level* policy.
- [ ] You propagate a *correlation ID*.
- [ ] You *mask* sensitive fields.

## Practice Problems

1. Convert one `print` to a *structured log*.
2. Inject a *correlation ID* via middleware.
3. *Query* every ERROR for one user ID.

## Wrap-up and Next Steps

Once logs are *data*, *queries* begin. Next: *distributed tracing*.

<!-- toc:begin -->
- [What Is Observability?](./01-what-is-observability.md)
- [Metrics, Logs, and Traces](./02-metric-log-trace.md)
- [Collecting and Visualizing Metrics](./03-metric-collection.md)
- **Structured Logging (current)**
- Distributed Tracing Basics (upcoming)
- Dashboard Design (upcoming)
- Alerts and On-Call (upcoming)
- SLI and SLO Basics (upcoming)
- Cost and Cardinality (upcoming)
- A Production-Ready Observability Stack (upcoming)
<!-- toc:end -->

## References

- [Python logging](https://docs.python.org/3/library/logging.html)
- [structlog](https://www.structlog.org/)
- [OpenTelemetry logs](https://opentelemetry.io/docs/concepts/signals/logs/)
- [Twelve-factor logs](https://12factor.net/logs)

Tags: Observability, Logging, Python, JSON, DevOps

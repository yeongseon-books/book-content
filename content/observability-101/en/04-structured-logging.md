---
series: observability-101
episode: 4
title: "Observability 101 (4/10): Structured Logging"
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

# Observability 101 (4/10): Structured Logging

Many incident reviews reveal the same problem: logs existed, but the team still could not answer the first two questions quickly. Which request failed, and what was different about it? Free-form lines are readable, but they are poor query surfaces.

Structured logging fixes that by turning log lines into data with fields you can filter, aggregate, and join with traces.

This is the 4th post in the Observability 101 series.


![observability 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/04/04-01-concept-at-a-glance.en.png)
*observability 101 chapter 4 flow overview*
> Structured Logging is about the boundary decision, not the tool choice.

## Questions to Keep in Mind

- Why do free-form logs hit a limit so quickly in production?
- What changes when logs become structured data?
- By what criteria should log levels be divided?

## Why It Matters

To find the responsible line *within five minutes* of an incident, logs must be *queryable*. The age of `print` is over.

> *A log is *data*, not prose.*

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Unstructured vs Structured Logs

Switching the format alone drastically changes operational efficiency.

| Aspect | Unstructured Log | Structured Log (JSON) |
| --- | --- | --- |
| Searchability | Depends on string grep | Field-based queries |
| Parsing cost | High (regex required) | Low (JSON parser) |
| Alert integration | Difficult (string matching) | Easy (field condition filters) |
| Aggregation | Nearly impossible | Straightforward (GROUP BY) |
| Example | `User 123 login failed` | `{"event":"login_failed","user_id":123}` |

Unstructured logs are comfortable for human eyes but weak for machine queries. Structured logs may feel less readable at first, but they are far faster for incident response and aggregation.

## Key Terms

- **Level**: DEBUG / INFO / WARNING / ERROR / CRITICAL.
- **Structured fields**: one key=value pair at a time.
- **Correlation ID**: an ID that *binds* a single request.
- **Sink**: where logs are *shipped*.
- **Sampling**: keeping *only a portion* when volume is high.

## Before/After

**Before**: `print(f"user {uid} failed: {e}")` — regex *hell*. You can read it, but aggregating failures per user or collecting all lines for one request quickly hits a wall.

**After**: `logger.error("login_failed", user_id=uid, reason=str(e))` — *one query*. The log is both a readable sentence and queryable data.

## Hands-on: Structured Logging in 5 Steps

### Step 1 — Basic Python `logging`

```python
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")
log.info("started")
```

Even a basic logger is better than `print`. At minimum, you gain level separation and output routing control.

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

The moment a line becomes JSON, field-based searching is possible. This single change transforms log analysis workflows.

### Step 3 — Context fields

```python
def login(uid):
    log.info("login_attempt", extra={"extra": {"user_id": uid}})
```

Events alone are not enough. Context — whose request, which order, which route — is what lets you narrow a failure.

### Step 4 — Correlation ID

```python
import uuid
def handle(req):
    rid = req.headers.get("x-request-id") or str(uuid.uuid4())
    log.info("request_in", extra={"extra": {"rid": rid}})
```

With a correlation ID, multiple log lines for the same request cluster together. In distributed systems, treat `trace_id` or `request_id` as a mandatory default field.

### Step 5 — Level policy

```text
DEBUG    → development detail
INFO     → normal events
WARNING  → cautions (actionable)
ERROR    → failed requests
CRITICAL → system risk
```

If everything is logged at INFO, real signals drown. A level policy controls both storage volume and attention simultaneously.

## structlog FastAPI Middleware

structlog is the leading Python library for structured logging. Below is a FastAPI middleware that emits structured JSON for every request.

```python
import structlog
import uuid
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Initialize structlog
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()
app = FastAPI()

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    start_time = time.time()

    # Bind context
    log = logger.bind(request_id=request_id, path=request.url.path, method=request.method)

    log.info("request_start")

    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        log.info(
            "request_end",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2)
        )

        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log.error(
            "request_error",
            error=str(e),
            duration_ms=round(duration_ms, 2)
        )
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    logger.info("user_lookup", user_id=user_id)
    return {"user_id": user_id, "name": "test"}
```

This code attaches a `request_id` to every request and emits structured JSON at start and end. `bind()` groups common fields so you never repeat them.

## Log Level Strategy

Log levels are not simple categories — they control both storage volume and attention simultaneously.

| Level | Criterion | Example | Retention |
| --- | --- | --- | --- |
| DEBUG | Development flow details | Function calls, variable values | Short (1 day or less) |
| INFO | Normal events | Request start/end, user actions | Medium (7 days) |
| WARNING | Attention needed (actionable) | Retries, deprecated API usage | Long (30 days) |
| ERROR | Request failure | Exception raised, external API timeout | Very long (90 days+) |
| CRITICAL | System risk | DB connection lost, memory exhaustion | Permanent |

### Operational Guidelines per Level

- **DEBUG**: Keep off in production. Use only in development to trace flow.
- **INFO**: The default level. Most normal events are INFO.
- **WARNING**: No alert needed, but a sign that things may degrade. Log for later review.
- **ERROR**: Connects to immediate alerts. A user request failed → ERROR.
- **CRITICAL**: Triggers on-call. Reserved for system-wide danger.

If WARNING floods, the criteria are too loose. If ERROR never fires, the criteria are too strict. Include level definitions in code review checklists so the entire team writes to the same standard.

## Log Level Operational Criteria

When defining levels, use "action" rather than "importance" as the criterion. Ask: what should the person reading this log *do*?

| Level | Question | Operational Action | Example Event |
| --- | --- | --- | --- |
| DEBUG | Is the flow correct? | Check in dev env | serializer_mismatch |
| INFO | Is processing normal? | Dashboard reference | request_end |
| WARNING | Are things degrading? | Ticket / review | retry_exhausted_soon |
| ERROR | Did a request fail? | Alert or immediate inspection | payment_failed |
| CRITICAL | Is there a broad outage? | On-call page | db_unavailable |

Without agreed criteria, different teams log the same event at different levels. Alert rule reliability drops and the same incident gets handled multiple times.

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

## JSON Log Field Standard

Even with structured logging, if every team names fields differently, operational efficiency stays low. A minimal common schema makes query templates and alert rules reusable.

| Field | Type | Description | Example |
| --- | --- | --- | --- |
| ts | number | Unix epoch or ISO timestamp | 1716000123.22 |
| level | string | Log level | INFO |
| event | string | Event name | payment_failed |
| service | string | Service name | checkout-api |
| env | string | Execution environment | prod |
| trace_id | string | Distributed tracing ID | 9f3c... |
| request_id | string | Request identifier | req-12ab |
| route | string | Normalized path | /orders/:id |
| status_code | number | HTTP status code | 502 |
| error_code | string | Domain error code | GATEWAY_TIMEOUT |

The goal is not "include everything" but "fix the minimum fields that answer frequently asked questions." Sensitive values like email, card numbers, or SSN must never be stored raw — use masking or hashing.

## structlog Initialization Template

```python
import logging
import structlog

def configure_logger() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def mask_email(email: str) -> str:
    name, domain = email.split("@")
    visible = name[:2] if len(name) >= 2 else name
    return f"{visible}***@{domain}"
```

This configuration satisfies two common production needs. First, it structures exception info inside JSON. Second, it propagates request context via `contextvars`, maintaining common fields even in async code.

## Log Aggregation Pipeline

Structured logs are not enough on their own. You need a pipeline to collect, store, and query them.

### Promtail + Loki Configuration

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: app-logs
    static_configs:
      - targets: [localhost]
        labels:
          job: checkout-api
          env: prod
          __path__: /var/log/app/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            event: event
            trace_id: trace_id
            service: service
      - labels:
          level:
          event:
          service:
      - timestamp:
          source: ts
          format: Unix
```

This configuration extracts fields from JSON logs and converts them to Loki labels. Queries like `{service="checkout-api", level="ERROR"}` work immediately.

### Fluentd + Elasticsearch Configuration

```xml
<source>
  @type tail
  path /var/log/app/*.log
  pos_file /var/log/fluentd/app.pos
  tag app.checkout
  <parse>
    @type json
    time_key ts
    time_type float
  </parse>
</source>

<filter app.**>
  @type record_transformer
  <record>
    hostname "#{Socket.gethostname}"
  </record>
</filter>

<match app.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name app-logs-%Y%m%d
  <buffer>
    flush_interval 5s
    chunk_limit_size 8m
  </buffer>
</match>
```

### Choosing Between Pipelines

| Stack | Strength | Weakness | Best For |
| --- | --- | --- | --- |
| Promtail + Loki | Low cost, Grafana integration | Weak full-text search | Label-based filtering as primary use case |
| Fluentd + ELK | Powerful full-text search | Higher operational complexity | When log body search matters |

## PII Masking Pipeline

If PII reaches production logs unmasked, it becomes a security incident waiting to happen. Handle masking at the logging layer.

```python
import hashlib
import re
from typing import Any

PII_FIELDS = {"email", "phone", "card_number", "ssn"}
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

def mask_value(key: str, value: Any) -> Any:
    """Replace PII fields with hash or mask."""
    if key in PII_FIELDS:
        if isinstance(value, str):
            return hashlib.sha256(value.encode()).hexdigest()[:16]
        return "***"
    if isinstance(value, str) and EMAIL_RE.search(value):
        return EMAIL_RE.sub("[REDACTED_EMAIL]", value)
    return value

def sanitize_log(payload: dict) -> dict:
    """Walk the entire log payload and remove PII."""
    return {k: mask_value(k, v) for k, v in payload.items()}

# Usage
raw = {
    "event": "user_registered",
    "email": "user@example.com",
    "phone": "010-1234-5678",
    "plan": "pro",
}
safe = sanitize_log(raw)
# {"event": "user_registered", "email": "a1b2c3d4e5f6...", "phone": "***", "plan": "pro"}
```

Three key points for masking policies:

1. **Hashability**: Hashing email with SHA-256 lets you correlate the same user's logs without revealing the original value.
2. **Timing**: Mask at write time. Deleting after it reaches the store is already too late.
3. **Verification**: Add a CI step that periodically scans logs for PII leaks.

## Log Volume Control

Logs written without limits cause storage costs to spike. Even with DEBUG off in production, volume can still explode in certain scenarios.

| Strategy | Description | When to Use |
| --- | --- | --- |
| Level filtering | Exclude DEBUG lines in production | Default |
| Sampling | Log only 10% of successful requests | Very high traffic |
| Error-first | Sample successes, log 100% of errors | Balance cost and visibility |
| Rate limiting | Stop logging after 10 occurrences of the same event | Repeated failures flooding logs |

```python
import time
from collections import defaultdict

# Rate-limiting example
_event_counts: dict = defaultdict(lambda: {"count": 0, "last_reset": time.time()})
RATE_LIMIT = 10  # Max per second

def should_log(event: str) -> bool:
    """Suppress if the same event exceeds RATE_LIMIT within 1 second."""
    now = time.time()
    entry = _event_counts[event]
    if now - entry["last_reset"] > 1.0:
        entry["count"] = 0
        entry["last_reset"] = now
    entry["count"] += 1
    return entry["count"] <= RATE_LIMIT
```

Even when suppressing, record the dropped count as a metric. A counter like `logs_dropped_total{event="payment_timeout"}` lets you verify suppression is happening.

To set thresholds: first, measure per-second log line count during normal traffic as a baseline. Second, auto-switch to sampling when volume exceeds 5× baseline, but always record errors and warnings at 100%. This controls cost while maintaining incident visibility.

PromQL examples for monitoring log volume:

```promql
# Log line ingestion rate (per second)
rate(log_lines_total[5m])

# Percentage of suppressed logs
sum(rate(logs_dropped_total[5m])) / sum(rate(log_lines_total[5m])) * 100
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

Most teams ship *JSON logs → Loki or ELK → Grafana / Kibana*. The correlation ID *links* logs to traces. Logging more is less important than logging in a way that is queryable.

One easily forgotten aspect is PII handling. Starting to log raw data because "it's useful for debugging" turns the log store into the fastest-growing risk surface. Masking and hashing policies are part of logging design, not an afterthought.

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

## Answering the Opening Questions

- **Why do free-form logs quickly hit limits in operations?**
  - Free-form logs cannot be parsed by machines. `grep` cannot accurately filter by specific user, error code, or trace ID. Structuring as JSON fields enables index-based queries in Loki or Elasticsearch, gathering relevant logs within 5 minutes during incident response.
- **What makes structured logs different?**
  - Three key differences: (1) machine-parseable format, (2) context fields (trace_id, request_id, service) auto-injected, (3) filtering by log labels answers most operational questions without full-text search.
- **By what criteria should log levels be divided?**
  - Not by "importance" but by "operational action." ERROR triggers immediate inspection; WARNING triggers a review ticket; INFO serves as dashboard reference. Including level definitions in code review checklists ensures the entire team writes logs to the same standard.
<!-- toc:begin -->
## In this series

- [Observability 101 (1/10): What Is Observability?](./01-what-is-observability.md)
- [Observability 101 (2/10): Metrics, Logs, and Traces](./02-metric-log-trace.md)
- [Observability 101 (3/10): Collecting and Visualizing Metrics](./03-metric-collection.md)
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
- [Grafana Loki](https://grafana.com/docs/loki/latest/)

Tags: Observability, Logging, Python, JSON, DevOps

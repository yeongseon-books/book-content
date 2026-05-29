---
series: secure-coding-101
episode: 10
title: "Secure Coding 101 (10/10): Safe Logging and Audit"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Logging
  - AuditLog
  - SecureCoding
  - Compliance
  - SIEM
seo_description: Sensitive-field masking, audit logs, tamper evidence, retention policy, and a five-step playbook for safe logging.
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (10/10): Safe Logging and Audit

When an incident lands, the team's first questions are usually simple: when did it start, who touched the resource, what changed first, and what spread next? If the logs cannot answer those questions, recovery slows down immediately. If the logs answer them by leaking passwords, tokens, or internal secrets, the evidence turns into a second incident.

This is the final post in the Secure Coding 101 series.

Here, we will treat logging as an evidence system rather than a convenience feature. That means designing for structured search, sensitive-field masking, audit-log separation, append-only storage, and retention rules that keep investigations possible without turning logs into a long-lived liability.

> Logs are evidence and risk at the same time. Safe logging requires precise records, deliberate non-recording of secrets, and storage that resists tampering.


![secure coding 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/10/10-01-concept-at-a-glance.en.png)
*secure coding 101 chapter 10 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Safe Logging and Audit?
- Which signal should the example or diagram make visible for Safe Logging and Audit?
- What failure should be prevented first when Safe Logging and Audit reaches a real system?

## Questions This Chapter Answers

- The difference between *application log* and *audit log*
- *Sensitive-field masking* policy
- *Tamper evidence* and *retention*
- The role of a *SIEM*
- A five-step routine and five common mistakes

## Why It Matters

The first question in incident response is *when, who, what*. If you cannot answer, the *incident never ends*. Meanwhile, if passwords, tokens, or card numbers slip into logs, the *incident doubles*.

> *Record everything precisely. Never record secrets.*

## Key Terms

- **Application log**: ordinary logs for *debugging and operations*.
- **Audit log**: *legal evidence* of *who did what*.
- **Tamper evidence**: ability to *detect modifications*.
- **Retention**: *how long* the log is kept.
- **SIEM**: a system that *collects, analyzes, alerts* on security logs.

## Before/After

**Before**: `print` lines containing the *raw password*. *No retention policy*. No way to tell *who deleted what*.

**After**: Structured *JSON logs*, sensitive fields *masked*, *append-only* storage, explicit *retention*.

## Hands-on: Safe Logging in Five Steps

### Step 1 — Structured logs

```python
import json, time
def log_event(event, **fields):
    print(json.dumps({"ts": time.time(), "event": event, **fields}))
```

### Step 2 — Mask sensitive fields

```python
SENSITIVE = {"password", "token", "card_number", "ssn"}

def mask(d):
    return {k: ("***" if k in SENSITIVE else v) for k, v in d.items()}

log_event("login", **mask({"user": "ana", "password": "x"}))
```

### Step 3 — Separate the audit log

```python
def audit(actor, action, target, result):
    log_event(
        "audit", actor=actor, action=action,
        target=target, result=result,
    )
```

### Step 4 — Append-only storage

```bash
# Object storage with Object Lock or immutability turned on
aws s3api put-object-lock-configuration ...
```

### Step 5 — Retention policy

```text
- application log: 30 days
- audit log: 1+ year (per regulation)
- integrity check every quarter
```

## Building an investigation timeline from real events

The most useful logging pattern is one that lets you reconstruct a sequence quickly, not one that merely stores a lot of text.

```json
{"ts":"2026-05-15T09:00:11Z","event":"login","user_id":"u-42","request_id":"r-100"}
{"ts":"2026-05-15T09:00:15Z","event":"role_change","actor_id":"admin-7","target_user_id":"u-42","request_id":"r-101"}
{"ts":"2026-05-15T09:01:02Z","event":"export_started","user_id":"u-42","request_id":"r-102"}
```

With stable IDs and UTC timestamps, the incident question changes from "what even happened?" to "was this role change expected, and which export followed it?" That is exactly the kind of reader value an audit log is supposed to provide.

## What to Notice in This Code

- *Audit log* is *separate* from the application log.
- Masking is the *default*; you opt out, not in.
- Append-only storage *leaves traces* of any tampering.

## Five Common Mistakes

1. **Letting *passwords or tokens* flow into logs.** One line is enough.
2. **Mixing *audit and application* logs.** Investigation becomes *impossible*.
3. **Keeping logs only on *server disks*.** Attackers *delete them*.
4. **Inconsistent timezones.** Local time instead of UTC.
5. **Infinite retention.** Cost *explodes* and incidents *get worse*.

## How This Shows Up in Production

Most teams pipe JSON logs through a collector (Fluent Bit, Vector) into central storage (Loki, Elasticsearch, S3), and a SIEM (Splunk, Datadog, Wazuh) raises alerts on audit patterns.

Senior engineers also think about making logs readable, not just writable. Field names must be consistent, user IDs and request IDs must link together, and core events (auth, authz, payment) must follow a shared format so investigation speed stays high. Good logs are not logs that record everything—they are logs that let you safely re-read the facts you need.

## How a Senior Engineer Thinks

- *Logs are both *asset and risk*.*
- *The audit log directly affects *business trust*.*
- *Storage must be *immutable* to mean anything.*
- *Masking is the *default*; opt-out only.*
- *Retention is a *policy decision*, written down.*

## Practical Deep Dive: structlog Configuration, PII Filtering, WORM Storage, Alert Rules, and Correlation IDs

### Structured Logging with structlog

Python's standard logging module is string-based and makes structured output awkward. structlog provides natural key-value logging.

```python
import structlog
import logging

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

# Usage
logger.info("user_login", user_id="u-42", ip="192.168.1.100", method="password")
# Output: {"event": "user_login", "user_id": "u-42", "ip": "192.168.1.100",
#          "method": "password", "level": "info", "timestamp": "2026-05-15T09:00:11Z"}

logger.warning("auth_failed", user_id="u-42", reason="invalid_password", attempt=3)
```

The key advantage of structlog is automatic context propagation. Values bound at the start of request processing are included in all logs for that request automatically.

```python
from fastapi import FastAPI, Request
import structlog
import uuid

app = FastAPI()

@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        client_ip=request.client.host,
    )
    response = await call_next(request)
    return response

# Any subsequent logger.info("event") call automatically includes
# request_id, path, method, client_ip
```

### PII Auto-Filtering

Relying on developer memory for masking guarantees gaps. Embed filters in the logging pipeline itself.

```python
import re
import structlog

# PII pattern definitions
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"01[016789]-?\d{3,4}-?\d{4}"),
    "card_number": re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
    "resident_id": re.compile(r"\b\d{6}[- ]?\d{7}\b"),
}

# Sensitive field key list
SENSITIVE_KEYS = {
    "password", "token", "secret", "api_key", "access_token",
    "refresh_token", "card_number", "ssn", "resident_id",
    "authorization", "cookie",
}

def pii_filter(logger, method_name, event_dict):
    """structlog processor: automatic PII masking"""
    for key, value in list(event_dict.items()):
        # Key-based masking
        if key.lower() in SENSITIVE_KEYS:
            event_dict[key] = "***REDACTED***"
            continue

        # Value-based pattern masking (strings only)
        if isinstance(value, str):
            for pattern_name, pattern in PII_PATTERNS.items():
                if pattern.search(value):
                    event_dict[key] = pattern.sub(f"[{pattern_name.upper()}_REDACTED]", value)
                    break

    return event_dict

# Add to structlog configuration
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        pii_filter,  # Place PII filter before JSONRenderer
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(),
    ],
)

# Test
logger = structlog.get_logger()
logger.info("user_action", email="user@example.com", password="secret123")
# Output: {"event": "user_action", "email": "[EMAIL_REDACTED]",
#          "password": "***REDACTED***", ...}
```

### Correlation IDs for Distributed Tracing

In microservice environments, a single user request traverses multiple services. Without a Correlation ID, linking logs across services is impossible.

```python
import uuid
from fastapi import FastAPI, Request, Response
import structlog

app = FastAPI()
logger = structlog.get_logger()

CORRELATION_HEADER = "X-Correlation-ID"

@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    # Use upstream ID if present, otherwise generate
    correlation_id = request.headers.get(CORRELATION_HEADER, str(uuid.uuid4()))

    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

    response = await call_next(request)
    response.headers[CORRELATION_HEADER] = correlation_id
    return response

# Propagate ID when calling downstream services
import httpx

async def call_downstream_service(url: str, data: dict):
    ctx = structlog.contextvars.get_contextvars()
    correlation_id = ctx.get("correlation_id", str(uuid.uuid4()))

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=data,
            headers={CORRELATION_HEADER: correlation_id}
        )
    return response
```

```text
Logs linked by Correlation ID:

Service A (API Gateway):
{"correlation_id": "abc-123", "event": "request_received", "path": "/transfer"}

Service B (Payment):
{"correlation_id": "abc-123", "event": "payment_initiated", "amount": 50000}

Service C (Notification):
{"correlation_id": "abc-123", "event": "email_sent", "template": "transfer_confirm"}

Investigation: search correlation_id="abc-123" to see the full flow
```

### Dedicated Audit Log Model

Audit logs differ from application logs at the schema level. They must record who, when, what, and how without gaps.

```python
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import json
import structlog

class AuditAction(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHANGE = "permission_change"
    EXPORT = "export"

@dataclass
class AuditEvent:
    timestamp: str
    actor_id: str
    actor_type: str  # "user", "service", "system"
    action: str
    resource_type: str
    resource_id: str
    result: str  # "success", "failure", "denied"
    details: dict
    correlation_id: str
    source_ip: str

    @classmethod
    def create(cls, actor_id: str, action: AuditAction, resource_type: str,
               resource_id: str, result: str, **kwargs):
        ctx = structlog.contextvars.get_contextvars()
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor_id=actor_id,
            actor_type=kwargs.get("actor_type", "user"),
            action=action.value,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            details=kwargs.get("details", {}),
            correlation_id=ctx.get("correlation_id", ""),
            source_ip=ctx.get("client_ip", ""),
        )

# Dedicated audit logger
audit_logger = structlog.get_logger("audit")

def record_audit(event: AuditEvent):
    audit_logger.info("audit_event", **asdict(event))

# Usage
record_audit(AuditEvent.create(
    actor_id="u-42",
    action=AuditAction.PERMISSION_CHANGE,
    resource_type="user",
    resource_id="u-99",
    result="success",
    details={"old_role": "viewer", "new_role": "admin"},
))
```

### WORM (Write Once Read Many) Storage Configuration

Audit logs must be impossible to modify or delete to hold evidentiary value. WORM storage guarantees this technically.

```bash
# AWS S3 Object Lock — Governance mode
aws s3api put-object-lock-configuration \
  --bucket audit-logs-prod \
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "GOVERNANCE",
        "Days": 365
      }
    }
  }'

# Compliance mode — even root users cannot delete
aws s3api put-object-lock-configuration \
  --bucket audit-logs-compliance \
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "COMPLIANCE",
        "Days": 2555
      }
    }
  }'
```

```text
WORM mode comparison:
| Mode       | Deletion        | Use Case                          |
|------------|-----------------|-----------------------------------|
| Governance | Requires special permission | General audit logs, operational records |
| Compliance | Impossible      | Regulatory (finance, healthcare, legal evidence) |
```

```python
# Batch upload audit logs to S3 WORM bucket
import boto3
from datetime import datetime

s3 = boto3.client("s3")
AUDIT_BUCKET = "audit-logs-prod"

def upload_audit_logs(log_lines: list[str], service_name: str):
    now = datetime.utcnow()
    key = f"audit/{service_name}/{now.strftime('%Y/%m/%d/%H')}/{now.isoformat()}.jsonl"

    body = "\n".join(log_lines)

    s3.put_object(
        Bucket=AUDIT_BUCKET,
        Key=key,
        Body=body.encode(),
        ContentType="application/x-ndjson",
        # Object Lock applies automatically at bucket level
    )
    return key
```

### Alert Rule Design

Collecting logs without creating alerts delays incident detection. Audit-log-based alert rules are the core of security monitoring.

```text
Alert rule examples:

1. Authentication failure spike
   Condition: 10+ login failures from the same IP within 5 minutes
   Severity: HIGH
   Response: Temporary IP block + create incident

2. Privilege escalation detected
   Condition: Admin role granted to a regular user
   Severity: CRITICAL
   Response: Immediate alert + verify change approval

3. Bulk data access
   Condition: Single user queries 1000+ personal records in 1 hour
   Severity: MEDIUM
   Response: Create review request

4. Off-hours access
   Condition: Admin function access between 2-5 AM
   Severity: MEDIUM
   Response: Notify on-call

5. Audit log self-access
   Condition: Attempt to delete/modify audit logs
   Severity: CRITICAL
   Response: Immediate alert + account lock
```

```python
# Simple alert rule engine
from collections import defaultdict
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

class AlertEngine:
    def __init__(self):
        self.login_failures = defaultdict(list)  # ip -> [timestamps]

    def process_event(self, event: dict):
        # Rule 1: Authentication failure spike
        if event.get("event") == "auth_failed":
            ip = event.get("source_ip", "")
            now = datetime.utcnow()
            self.login_failures[ip].append(now)

            # Keep only failures within 5 minutes
            cutoff = now - timedelta(minutes=5)
            self.login_failures[ip] = [
                t for t in self.login_failures[ip] if t > cutoff
            ]

            if len(self.login_failures[ip]) >= 10:
                self.fire_alert(
                    severity="HIGH",
                    rule="brute_force_detected",
                    details={"ip": ip, "count": len(self.login_failures[ip])}
                )

        # Rule 2: Privilege escalation
        if (event.get("action") == "permission_change" and
            event.get("details", {}).get("new_role") == "admin"):
            self.fire_alert(
                severity="CRITICAL",
                rule="privilege_escalation",
                details={
                    "actor": event.get("actor_id"),
                    "target": event.get("resource_id"),
                }
            )

    def fire_alert(self, severity: str, rule: str, details: dict):
        logger.critical("security_alert", severity=severity, rule=rule, **details)
        # Send to Slack/PagerDuty/email
```

### Log Integrity Verification

Stored logs must be periodically verified for tampering. Hash chaining is the simplest yet effective approach.

```python
import hashlib
import json

class LogIntegrityChain:
    def __init__(self):
        self.previous_hash = "0" * 64  # genesis

    def append(self, log_entry: dict) -> dict:
        entry_with_chain = {
            **log_entry,
            "_prev_hash": self.previous_hash,
        }
        entry_json = json.dumps(entry_with_chain, sort_keys=True)
        current_hash = hashlib.sha256(entry_json.encode()).hexdigest()
        entry_with_chain["_hash"] = current_hash
        self.previous_hash = current_hash
        return entry_with_chain

    @staticmethod
    def verify_chain(entries: list[dict]) -> bool:
        for i, entry in enumerate(entries):
            stored_hash = entry.pop("_hash")
            entry_json = json.dumps(entry, sort_keys=True)
            computed_hash = hashlib.sha256(entry_json.encode()).hexdigest()
            if computed_hash != stored_hash:
                return False  # Tampering detected
            entry["_hash"] = stored_hash

            if i > 0 and entry["_prev_hash"] != entries[i-1]["_hash"]:
                return False  # Chain break detected
        return True
```

```text
Integrity verification schedule:
- Real-time: Log collector verifies chain hashes
- Daily: Checksum verification of daily log files
- Quarterly: Full audit log integrity report generation
```

## Checklist

- [ ] Sensitive fields are *masked*.
- [ ] *Audit logs* are *separated*.
- [ ] Storage is *append-only* or *immutable*.
- [ ] *Retention* is documented.

## Practice Problems

1. List five *audit events* in your service.
2. Implement a *masking* function that runs on a *Pydantic model*.
3. Two scenarios where *append-only* could be broken.

## Wrap-up and Next Steps

That closes *Secure Coding 101*: validation, auth, authz, storage, secrets, DB, browser, dependencies, logging. Avoid the most common pitfalls at every step and your system gains security that buys time.

## Answering the Opening Questions

- **What distinguishes application logs from audit logs?**
  - Application logs serve debugging and operational observation with short retention. Audit logs are evidence of "who changed what resource," recorded in a dedicated schema (AuditEvent model) and preserved long-term in WORM storage. As the dedicated audit log model section showed, recording actor, action, resource, and result completely is required for investigation use.
- **How far should the sensitive field masking policy reach?**
  - As the PII filtering section showed, both key-based masking (password, token, etc.) and value-based pattern matching (email, phone, card numbers) must be applied together. Rather than relying on developer memory, embedding filters in the logging pipeline itself (structlog processor) ensures nothing is missed.
- **Why are tamper detection and append-only storage important?**
  - If attackers delete logs after intrusion, evidence disappears. WORM storage (S3 Object Lock Compliance mode) cannot be deleted even by root users, guaranteeing evidence preservation. Verifying integrity with hash chains also detects if logs were tampered with in between.
<!-- toc:begin -->
## In this series

- [Secure Coding 101 (1/10): What Is Secure Coding?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): Input Validation](./02-input-validation.md)
- [Secure Coding 101 (3/10): Authentication and Session](./03-authentication-and-session.md)
- [Secure Coding 101 (4/10): Authorization and Permissions](./04-authorization-and-permissions.md)
- [Secure Coding 101 (5/10): Safe Data Storage](./05-safe-data-storage.md)
- [Secure Coding 101 (6/10): Secret and Key Management](./06-secret-and-key-management.md)
- [Secure Coding 101 (7/10): SQL Injection and Safe ORM Usage](./07-sql-injection-and-orm.md)
- [Secure Coding 101 (8/10): XSS and CSRF Defense](./08-xss-and-csrf.md)
- [Secure Coding 101 (9/10): Managing Dependency Vulnerabilities](./09-dependency-vulnerabilities.md)
- **Safe Logging and Audit (current)**

<!-- toc:end -->

## References

- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [NIST 800-92 — Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)
- [Google SRE — Logging](https://sre.google/sre-book/monitoring-distributed-systems/)
- [AWS S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [OpenTelemetry Logs Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/)

Tags: Logging, AuditLog, SecureCoding, Compliance, SIEM

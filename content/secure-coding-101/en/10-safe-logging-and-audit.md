---
series: secure-coding-101
episode: 10
title: Safe Logging and Audit
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

# Safe Logging and Audit

When an incident lands, the team's first questions are usually simple: when did it start, who touched the resource, what changed first, and what spread next? If the logs cannot answer those questions, recovery slows down immediately. If the logs answer them by leaking passwords, tokens, or internal secrets, the evidence turns into a second incident.

This is the final post in the Secure Coding 101 series.

Here, we will treat logging as an evidence system rather than a convenience feature. That means designing for structured search, sensitive-field masking, audit-log separation, append-only storage, and retention rules that keep investigations possible without turning logs into a long-lived liability.

> Logs are evidence and risk at the same time. Safe logging requires precise records, deliberate non-recording of secrets, and storage that resists tampering.

## Questions This Chapter Answers

- The difference between *application log* and *audit log*
- *Sensitive-field masking* policy
- *Tamper evidence* and *retention*
- The role of a *SIEM*
- A five-step routine and five common mistakes

## Why It Matters

The first question in incident response is *when, who, what*. If you cannot answer, the *incident never ends*. Meanwhile, if passwords, tokens, or card numbers slip into logs, the *incident doubles*.

> *Record everything precisely. Never record secrets.*

## Concept at a Glance

![The audit flow across structured logs, masking, immutable storage, and SIEM](../../../assets/secure-coding-101/10/10-01-concept-at-a-glance.en.png)

*The audit flow across structured logs, masking, immutable storage, and SIEM*
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

Most teams pipe *JSON logs* through a collector (*Fluent Bit*, *Vector*) into *central storage* (*Loki*, *Elasticsearch*, *S3*), and a *SIEM* (*Splunk*, *Datadog*, *Wazuh*) raises alerts on *audit patterns*.

## How a Senior Engineer Thinks

- *Logs are both *asset and risk*.*
- *The audit log directly affects *business trust*.*
- *Storage must be *immutable* to mean anything.*
- *Masking is the *default*; opt-out only.*
- *Retention is a *policy decision*, written down.*

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

That closes *Secure Coding 101*: validation → auth → authz → storage → secrets → DB → browser → dependencies → logging. Avoid the *most common pitfalls* at every step and your system gains *security that buys time*.

<!-- toc:begin -->
- [What Is Secure Coding?](./01-what-is-secure-coding.md)
- [Input Validation](./02-input-validation.md)
- [Authentication and Session](./03-authentication-and-session.md)
- [Authorization and Permissions](./04-authorization-and-permissions.md)
- [Safe Data Storage](./05-safe-data-storage.md)
- [Secret and Key Management](./06-secret-and-key-management.md)
- [SQL Injection and Safe ORM Usage](./07-sql-injection-and-orm.md)
- [XSS and CSRF Defense](./08-xss-and-csrf.md)
- [Managing Dependency Vulnerabilities](./09-dependency-vulnerabilities.md)
- **Safe Logging and Audit (current)**
<!-- toc:end -->

## References

- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [NIST 800-92 — Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)
- [Google SRE — Logging](https://sre.google/sre-book/monitoring-distributed-systems/)
- [AWS S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [OpenTelemetry Logs Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/)

Tags: Logging, AuditLog, SecureCoding, Compliance, SIEM

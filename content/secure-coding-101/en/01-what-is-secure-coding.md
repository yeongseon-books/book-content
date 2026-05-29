---
series: secure-coding-101
episode: 1
title: "Secure Coding 101 (1/10): What Is Secure Coding?"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - SecureCoding
  - Security
  - OWASP
  - DevSecOps
  - AppSec
seo_description: A practical introduction to secure coding — threat modeling, OWASP Top 10, and the daily habits that keep your code safe under attack.
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (1/10): What Is Secure Coding?

A feature can behave exactly as intended in happy-path testing and still fail the first time someone sends hostile input, replays a token, or calls an API out of order. In practice, many security incidents begin not with exotic cryptography failures but with ordinary development shortcuts: trusting a payload too early, logging a secret, or skipping a permission check in one code path.

This is the first post in the Secure Coding 101 series.

Here, we will treat secure coding not as a final review step but as a development habit that keeps the attack surface small from the first route handler to the final audit log. That mental model matters because the rest of the series builds on it: input validation, authentication, authorization, storage, browser defense, dependency hygiene, and logging only make sense when you see them as one connected system.

> Secure coding is not a coating you apply after the feature ships. It is the daily habit of shrinking the attack surface while keeping the system predictable under stress.


![secure coding 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/01/01-01-concept-at-a-glance.en.png)
*secure coding 101 chapter 1 flow overview*

## Questions to Keep in Mind

- What does secure coding mean exactly?
- How do threat models and attack surfaces relate to code design?
- From what perspective should beginners read the OWASP Top 10?

## Why It Matters

Most security incidents are known patterns repeated. Skipped input validation. Secrets in code. No permission check. Secure coding is not exotic cryptography — it is a small, daily set of rules.

> Security is not a coating on top of the feature. It is part of the structure.

## Key Terms

- **Threat model**: a map of who attacks, from where, and what they want.
- **Attack surface**: the input points an attacker can touch.
- **Trust boundary**: the line between trusted and untrusted zones.
- **Defense in depth**: multiple thin defenses layered together.
- **Least privilege**: grant only the access needed.

## Before/After

**Before**: Build the feature first, security later. When something breaks, rewrite it all.

**After**: Design input, auth, storage, logs together from day one. When something breaks, the blast radius is small.

## Hands-on: A Safer Flow in Five Steps

### Step 1 — Mark the input boundary

```python
def parse_age(raw: str) -> int:
    if not raw.isdigit():
        raise ValueError("age must be digits")
    age = int(raw)
    if not (0 < age < 150):
        raise ValueError("age out of range")
    return age
```

### Step 2 — Separate secrets from code

```python
import os
DB_PASSWORD = os.environ["DB_PASSWORD"]  # never hardcoded
```

### Step 3 — Check permission inside the function

```python
def delete_post(user, post):
    if post.author_id != user.id:
        raise PermissionError("not your post")
    post.delete()
```

### Step 4 — Escape on output

```python
import html
def render(name: str) -> str:
    return f"<p>Hello, {html.escape(name)}</p>"
```

### Step 5 — Keep secrets out of logs

```python
def log_login(user):
    print({"event": "login", "user_id": user.id})  # no password
```

## What to Notice in This Code

- Validation happens at every boundary, not only the first one.
- Secrets come from environment variables or a secret store.
- Permission is checked at the route and again inside the function.

## Five Common Mistakes

1. **Validating only on the client.** The server must re-validate every time.
2. **Committing secrets to git.** Once leaked, leaked forever.
3. **Leaking internal structure in error messages.** That hands attackers a map.
4. **Hiding actions in the UI only.** The API is still callable.
5. **Never updating dependencies.** Known CVEs pile up.

## How This Shows Up in Production

Most teams begin with a threat-modeling workshop. They draw a data-flow diagram and list threats at every trust boundary. CI runs secret scanning, dependency scanning, and SAST by default.

## How a Senior Engineer Thinks

- Treat input as hostile by default.
- Secrets must live outside the code.
- The server decides authorization. The UI is a hint.
- Logs are evidence and risk at the same time.
- There is no perfect security — only security that buys time.

## STRIDE Threat Modeling and Attack Surface Analysis

For secure coding principles to translate into real design decisions, you need a structured way to classify "what is dangerous." Here we use Microsoft's STRIDE model to categorize threats and show how to identify attack surfaces at the code level.

### STRIDE Threat Classification

| Category | Meaning | Where it appears in code | Mitigation principle |
| --- | --- | --- | --- |
| **S**poofing | Identity forgery | Unauthenticated API calls, token forgery | Strong auth, token signature verification |
| **T**ampering | Data modification | Cookie manipulation, request body tampering | Integrity checks, HMAC, signatures |
| **R**epudiation | Denying actions | Operations without audit logs | Audit logging, timestamps |
| **I**nformation Disclosure | Data leakage | Error messages, log exposure | Minimal information exposure, masking |
| **D**enial of Service | Service disruption | Unlimited requests, oversized uploads | Rate limiting, size limits |
| **E**levation of Privilege | Privilege escalation | Vertical/horizontal access bypass | Least privilege, server-side authorization |

Adding this table to design reviews replaces vague "we considered security" with specific questions like "how does this feature prevent Spoofing and Tampering?"

### Attack Surface Mapping Code

The first step in identifying the attack surface is listing every path where external input enters the system. Example using a FastAPI service:

```python
"""attack_surface.py — utility to auto-extract attack surface from routes"""
from fastapi import FastAPI
from dataclasses import dataclass

@dataclass
class EntryPoint:
    method: str
    path: str
    auth_required: bool
    input_sources: list[str]  # body, query, path, header, cookie

def map_attack_surface(app: FastAPI) -> list[EntryPoint]:
    """Extract attack surface list from registered routes."""
    entries = []
    for route in app.routes:
        if not hasattr(route, "methods"):
            continue
        for method in route.methods:
            has_auth = any(
                d.dependency.__name__ == "get_current_user"
                for d in getattr(route, "dependencies", [])
            )
            sources = []
            if "{" in route.path:
                sources.append("path")
            if method in ("POST", "PUT", "PATCH"):
                sources.append("body")
            sources.append("query")   # all routes accept query params
            sources.append("header")  # Host, Authorization, etc.
            entries.append(EntryPoint(
                method=method,
                path=route.path,
                auth_required=has_auth,
                input_sources=sources,
            ))
    return entries

def print_surface_report(entries: list[EntryPoint]) -> None:
    """Print attack surface report in table form."""
    unprotected = [e for e in entries if not e.auth_required]
    print(f"Total entry points: {len(entries)}")
    print(f"Unauthenticated entry points: {len(unprotected)}")
    print()
    for ep in unprotected:
        print(f"  [RISK] {ep.method} {ep.path} — inputs: {ep.input_sources}")
```

Adding this script to CI flags missing authentication whenever a new route is added. Because the attack surface changes with every code change, automated extraction is more realistic than static documentation.

### OWASP Top 10 Mapped to This Series

The OWASP Top 10 lists the ten most frequent web application risk categories. Mapping each series post to its corresponding item helps prioritize learning.

| OWASP Item | Series post | Core mitigation pattern |
| --- | --- | --- |
| A01 Broken Access Control | Ch 4 — Authorization | Server-side per-object authorization |
| A02 Cryptographic Failures | Ch 5 — Safe Storage | Envelope encryption, key rotation |
| A03 Injection | Ch 7 — SQL Injection & ORM | Parameter binding, safe ORM usage |
| A04 Insecure Design | Ch 1 (this post) | STRIDE, threat modeling |
| A05 Security Misconfiguration | Ch 6 — Secret & Key Management | Environment separation, default hardening |
| A06 Vulnerable Components | Ch 9 — Dependency Vulnerabilities | SCA, automated updates |
| A07 Auth Failures | Ch 3 — Authentication & Session | Secure sessions, MFA |
| A08 Data Integrity Failures | Ch 5, Ch 9 | Signature verification, SBOM |
| A09 Logging Failures | Ch 10 — Safe Logging | Structured logs, alerting |
| A10 SSRF | Ch 2 — Input Validation | URL allowlist, internal network blocking |

Posting this mapping in your team wiki enables code-review comments like "this change falls under A01 — does it follow the Ch 4 pattern?"

### CI Security Gate Configuration

Keeping a threat model only as a document creates drift as deployments accumulate. Adding security gates to the CI pipeline keeps the threat model alive alongside the code.

```yaml
# .github/workflows/security-gate.yml
name: Security Gate
on: [push, pull_request]
jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Detect secrets
        uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified

  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run safety check
        run: |
          pip install safety
          safety check --full-report

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run bandit
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json || true
      - name: Check high severity
        run: |
          python3 -c "
          import json, sys
          report = json.load(open('bandit-report.json'))
          high = [r for r in report.get('results', []) if r['issue_severity'] == 'HIGH']
          if high:
              for h in high:
                  print(f\"HIGH: {h['filename']}:{h['line_number']} — {h['issue_text']}\")
              sys.exit(1)
          print('No HIGH severity issues found.')
          "
```

This workflow checks three things: no real secrets in commits, no known vulnerabilities in dependencies, and no high-severity patterns in static analysis. All three must pass before a PR merges.

### Defense in Depth as Code

Defense in depth sounds abstract, but in code it manifests as multiple independent verification layers for the same threat.

```python
"""defense_in_depth.py — triple defense in order processing"""
from pydantic import BaseModel, Field
from fastapi import FastAPI, Depends, HTTPException

# Layer 1: Input boundary — schema enforces format and range
class OrderRequest(BaseModel):
    product_id: str = Field(pattern=r"^[A-Z0-9]{8}$")
    quantity: int = Field(ge=1, le=100)

# Layer 2: Authorization — server verifies user permissions
def check_can_order(user, product_id: str) -> None:
    if product_id.startswith("RESTRICTED") and "premium" not in user.roles:
        raise HTTPException(status_code=403, detail="premium only")

# Layer 3: Business rules — re-verify stock and limits
def validate_stock(product_id: str, quantity: int) -> None:
    stock = get_stock(product_id)  # DB lookup
    if quantity > stock:
        raise HTTPException(status_code=409, detail="insufficient stock")

app = FastAPI()

@app.post("/orders")
def create_order(
    req: OrderRequest,
    user=Depends(get_current_user),
):
    check_can_order(user, req.product_id)        # layer 2
    validate_stock(req.product_id, req.quantity)  # layer 3
    order = save_order(user.id, req.product_id, req.quantity)
    audit_log("order_created", user_id=user.id, order_id=order.id)
    return {"order_id": order.id}
```

Even if Layer 1 (schema) is bypassed, Layer 2 (authorization) blocks it. Even if Layer 2 is bypassed, Layer 3 (business rules) blocks it. No single bug translates directly into an incident — that is the core of defense in depth. In production, teams often add rate limiting (Layer 4) and audit logging (Layer 5).

### Threat Modeling Worksheet

When a team designs a new feature, filling out the following form naturally drives a STRIDE analysis:

```text
Feature name: ____________________
Data flow: User → [   ] → [   ] → [   ] → Storage

1. Are there paths accessible without authentication? (Spoofing)
   Answer:

2. Can data be tampered with in transit or at rest? (Tampering)
   Answer:

3. Can we trace who performed this action? (Repudiation)
   Answer:

4. Do error responses or logs expose sensitive information? (Information Disclosure)
   Answer:

5. Can mass requests or malformed input halt the service? (DoS)
   Answer:

6. Can a regular user reach admin functionality? (EoP)
   Answer:

Risk level: [ ] High  [ ] Medium  [ ] Low
Required mitigations:
  - [ ] Add authentication
  - [ ] Strengthen input schema
  - [ ] Add audit logging
  - [ ] Apply rate limiting
  - [ ] Apply encryption
```

Including this form in PR templates turns security reviews from rubber-stamp signatures into concrete question-and-answer exercises.

### Security Priority Matrix

You cannot block every threat simultaneously. In practice, prioritize by impact and likelihood:

```text
           Likelihood High
                │
    ┌───────────┼───────────┐
    │  Medium   │  Highest  │
    │ (monitor) │ (fix now) │
    ├───────────┼───────────┤
    │  Lowest   │  Medium   │
    │ (accept)  │ (plan fix)│
    └───────────┼───────────┘
                │
           Likelihood Low

    Impact Low ←──────────→ Impact High
```

For example, "secrets hardcoded in source" is both high-likelihood and high-impact — fix immediately. "No CSRF token on an internal admin page" is high-impact but low-likelihood — schedule for a planned fix. Documenting these decisions explains why something was not fixed at that time.

### Lessons from a Real Incident

Why these principles matter becomes clear from actual incidents. The 2017 Equifax breach occurred because a known Apache Struts vulnerability (CVE-2017-5638) went unpatched for over two months, exposing 140 million individuals' personal data. The failure was not a single mistake:

- No dependency update process (A06 Vulnerable Components)
- No internal network segmentation (defense in depth failure)
- Sensitive data stored unencrypted (A02 Cryptographic Failures)
- Intrusion-detection certificate expired, leaving the attack unnoticed for months (A09 Logging Failures)

Multiple defense layers were simultaneously empty, which is why the damage scaled so large. Had even one layer of defense in depth been active, the blast radius would have been far smaller. This is exactly why this series treats input, authentication, authorization, storage, and logging as independent defense lines.

## Checklist

- [ ] I can write the threat model in one paragraph.
- [ ] I can list my attack surface.
- [ ] No secret lives in the codebase.
- [ ] Server-side validation covers every input.

## Practice Problems

1. Sketch the trust boundaries of a service you are building.
2. Write the validation rules for the three inputs you receive most often.
3. Grep your repository for strings that look like secrets.

## Wrap-up and Next Steps

Secure coding is a habit. The next post goes deep on the place that leaks most often: input validation.

## Answering the Opening Questions

- **What does secure coding mean exactly?**
  - As the article summarized, it means not bolting security on after feature development but designing input boundaries, permissions, storage, and logging together from the start as a development habit. When each of the 5 practice steps acts as a defense layer, the overall system stays in a predictable state.
- **How do threat models and attack surfaces relate to code design?**
  - The 6 threats classified in the STRIDE table are 6 questions to verify in code. As the attack-surface mapping code showed, automatically extracting routes, auth status, and input sources reveals what is exposed whenever new features are added.
- **From what perspective should beginners read the OWASP Top 10?**
  - As the mapping table organized, reading each item not as isolated knowledge but asking "which of A01–A10 does this code fall under?" is closer to practice. Connecting to automated checks like a CI security gate turns document knowledge into an actual defense line.
<!-- toc:begin -->
## In this series

- **What Is Secure Coding? (current)**
- Input Validation (upcoming)
- Authentication and Session (upcoming)
- Authorization and Permissions (upcoming)
- Safe Data Storage (upcoming)
- Secret and Key Management (upcoming)
- SQL Injection and Safe ORM Usage (upcoming)
- XSS and CSRF Defense (upcoming)
- Managing Dependency Vulnerabilities (upcoming)
- Safe Logging and Audit (upcoming)

<!-- toc:end -->

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Secure Coding Practices Quick Reference](https://owasp.org/www-pdf-archive/OWASP_SCP_Quick_Reference_Guide_v2.pdf)
- [Microsoft Threat Modeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool)
- [Google — Secure by Design](https://security.googleblog.com/2024/01/secure-by-design.html)
- [CISA and International Partners — Shifting the Balance of Cybersecurity Risk](https://www.cisa.gov/resources-tools/resources/shifting-balance-cybersecurity-risk-principles-and-approaches-secure-design)

Tags: SecureCoding, Security, OWASP, DevSecOps, AppSec

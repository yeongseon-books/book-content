---
series: secure-coding-101
episode: 6
title: "Secure Coding 101 (6/10): Secret and Key Management"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Secrets
  - KeyManagement
  - Vault
  - SecureCoding
  - DevSecOps
seo_description: Environment variables, secret managers, key rotation, secret scanning, and a five-step playbook for safe key management.
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (6/10): Secret and Key Management

Secrets tend to stay invisible right up to the moment they become the most expensive line in the incident report. A database password in a repository, a signing key copied across environments, or a CI job that prints environment variables can leave a system operational on the surface while making it extremely fragile to recover once something leaks.

This is post 6 in the Secure Coding 101 series.

In this chapter, we will treat secret handling as an operating model rather than a storage trick: separation from code, central secret storage, access control, masking, rotation, and post-leak recovery. That wider frame is what distinguishes a merely hidden secret from a recoverable one.

> Secrets belong outside the codebase, with short lifetimes, explicit access control, and a rotation path you can execute under pressure.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Secret and Key Management?
- Which signal should the example or diagram make visible for Secret and Key Management?
- What failure should be prevented first when Secret and Key Management reaches a real system?

## Big Picture

![secure coding 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/06/06-01-concept-at-a-glance.en.png)

*secure coding 101 chapter 6 flow overview*

This picture places Secret and Key Management inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Secret and Key Management is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions This Chapter Answers

- What counts as a *secret*
- Why *hard-coded* secrets are dangerous
- The role of a *secret manager*
- What *key rotation* means
- A five-step routine and five common mistakes

## Why It Matters

The most common incident is a *secret committed to git*. Once pushed, it is *forever traceable*. Even *history rewrite* is not a complete fix.

> *Design every secret on the assumption that it *will leak someday*.*

## Concept at a Glance

## Key Terms

- **Secret**: API keys, DB passwords, tokens — *values that are dangerous when known*.
- **Secret manager**: a central place that *stores, rotates, audits* secrets.
- **Rotation**: replacing secrets *on a schedule*.
- **Scope**: how *broadly* a secret reaches.
- **Audit log**: who *read* the secret, and when.

## Before/After

**Before**: `config.py` contains `API_KEY = "..."`. CI logs print it as-is.

**After**: Loaded from env vars, fetched from a secret manager, *masked* in logs.

## Hands-on: Safe Secrets in Five Steps

### Step 1 — Separate the secret

```python
import os
DB_PASSWORD = os.environ["DB_PASSWORD"]  # never in code
```

### Step 2 — Make `.env` *local-only*

```bash
echo ".env" >> .gitignore
```

### Step 3 — Fetch from a secret manager

```python
import boto3
client = boto3.client("secretsmanager")
val = client.get_secret_value(SecretId="prod/db")["SecretString"]
```

### Step 4 — Rotate

```bash
# Issue a new secret -> reload the app -> revoke the old one
aws secretsmanager rotate-secret --secret-id prod/db
```

### Step 5 — Mask exposure

```python
def mask(s, keep=4):
    return s[:keep] + "*" * (len(s) - keep)
print("API key:", mask(API_KEY))
```

## When rotation fails in production

Rotation usually breaks not because the secret manager cannot mint a new value, but because the surrounding system still assumes the old one.

```text
Failure mode: new DB password issued, app still uses pooled old connections
What to verify:
1. connection pool recycle / reload timing
2. rollout order across workers and jobs
3. old credential revocation delay

Failure mode: JWT signing key changed, old tokens fail immediately
What to verify:
1. overlapping key IDs (kid) during transition
2. grace period for active sessions
3. cache invalidation in API gateways
```

These checks matter because secret rotation is successful only when the application can survive it without guesswork. A secret that is easy to create but hard to rotate is still operational debt.

## What to Notice in This Code

- A *secret manager* makes *access auditing* the default.
- Rotation should be possible *without app downtime*.
- Log masking is *on by default*.

## Five Common Mistakes

1. **Committing secrets to *git*.** Once is *forever*.
2. **Printing *env vars* in CI logs.** A *public build* means *public secrets*.
3. **Rotating secrets *manually only*.** It never actually happens.
4. **Reusing the *same secret across environments*.** One leak hits *all of them*.
5. **Holding secrets *in process memory forever*.** A single dump is enough.

## How This Shows Up in Production

Most teams adopt *Vault*, *AWS Secrets Manager*, *Doppler*, or *1Password Connect*, separate secrets *per environment*, and have *CI* fetch *short-lived tokens*. A *secret-scan hook* runs on every `git push`.

## How a Senior Engineer Thinks

- *A secret will leak — design for that.*
- *Rotation that is not *automatic* is not real rotation.*
- *Smaller *scope* means smaller blast radius.*
- *Access is audited by default.*
- *Logs are *masked by default*.*

## Checklist

- [ ] *git secret scanning* is on.
- [ ] Secrets are *separated per environment*.
- [ ] Rotation is *automatic*.
- [ ] An *audit log* exists for secret reads.

## Practice Problems

1. Two commands to find secrets in *git history*.
2. Trade-offs between *env vars* and a *secret manager*.
3. Why *short-lived tokens* beat *long-lived* ones.

## Wrap-up and Next Steps

Safe secrets keep *recovery cost* small. Next we tackle the oldest attack — *SQL injection*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Secret and Key Management?**
  - The article treats Secret and Key Management as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Secret and Key Management?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Secret and Key Management reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Secure Coding 101 (1/10): What Is Secure Coding?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): Input Validation](./02-input-validation.md)
- [Secure Coding 101 (3/10): Authentication and Session](./03-authentication-and-session.md)
- [Secure Coding 101 (4/10): Authorization and Permissions](./04-authorization-and-permissions.md)
- [Secure Coding 101 (5/10): Safe Data Storage](./05-safe-data-storage.md)
- **Secret and Key Management (current)**
- SQL Injection and Safe ORM Usage (upcoming)
- XSS and CSRF Defense (upcoming)
- Managing Dependency Vulnerabilities (upcoming)
- Safe Logging and Audit (upcoming)

<!-- toc:end -->

## References

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [HashiCorp Vault](https://developer.hashicorp.com/vault/docs)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [GitHub — Secret scanning](https://docs.github.com/en/code-security/secret-scanning)
- [The Twelve-Factor App — Config](https://12factor.net/config)

Tags: Secrets, KeyManagement, Vault, SecureCoding, DevSecOps

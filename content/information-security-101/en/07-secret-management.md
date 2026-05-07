---
series: information-security-101
episode: 7
title: Secret Management
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Security
  - Secrets
  - Vault
  - KMS
  - Rotation
seo_description: A short, code-first guide to managing secrets with environment variables, vaults, KMS, and rotation policies that actually run in production.
last_reviewed: '2026-05-04'
---

# Secret Management

> Information Security 101 series (7/10)

<!-- a-grade-intro:begin -->

**Core question**: What do we lose the moment a secret enters source code?

> Secret management is not about where you put them; it is about how you rotate them.

<!-- a-grade-intro:end -->

## What You Will Learn

- Secret types (static, dynamic, user, system)
- The limits of environment variables
- The role of vault and KMS
- Core rotation policy ideas
- Safe patterns for handling secrets in code

## Why It Matters

More than half of large incidents start with leaked secrets. A leaked secret without rotation is a permanent risk.

> Secrets are liabilities, not assets — keep their lifetime short.

## Concept at a Glance

```mermaid
flowchart LR
    A["Application"] -->|"request"| V["Vault / KMS"]
    V -->|"short-lived token"| A
    V -->|"audit log"| L["SIEM"]
```

Code holds the right to fetch a secret, not the secret itself.

## Key Terms

- **Static secret**: manually configured key or password.
- **Dynamic secret**: short-lived credential generated per request.
- **Vault**: secret manager such as HashiCorp Vault.
- **KMS**: key management service (AWS KMS, GCP KMS).
- **Rotation**: regularly replacing a secret.

## Before/After

**Before — Plaintext `.env`**

```text
Accidentally committed -> permanent leak -> rotate every environment
```

**After — Short-lived token from a vault**

```text
App requests a token at boot -> auto-rotates on expiry
```

Lifetime, not location, drives security.

## Hands-on Step by Step

### Step 1 — Environment Variables (Bare Minimum)

```python
# 1_env.py
import os
db_url = os.environ["DATABASE_URL"]
# Never hard-code: db_url = "postgres://user:pw@..."
```

Never commit `.env` files to git.

### Step 2 — Fetch a Secret from Vault

```python
# 2_vault.py
import hvac
client = hvac.Client(url="http://vault:8200", token=os.environ["VAULT_TOKEN"])
data = client.secrets.kv.read_secret_version(path="myapp/db")
db_pw = data["data"]["data"]["password"]
```

The vault token itself must also be short-lived (AppRole, Kubernetes SA, etc).

### Step 3 — Encrypt Data Keys with KMS

```python
# 3_kms.py
import boto3
kms = boto3.client("kms")
resp = kms.generate_data_key(KeyId="alias/app", KeySpec="AES_256")
plaintext = resp["Plaintext"]      # in-memory only
ciphertext = resp["CiphertextBlob"] # store in DB
```

The plaintext data key only lives in memory briefly.

### Step 4 — Secret Scanner (Prevention)

```bash
# 4_scan.sh
# pre-commit hook: trufflehog scans before commit
trufflehog filesystem . --only-verified
```

Always assume git history is hostile, and block leaks early.

### Step 5 — Rotation Pseudocode

```python
# 5_rotation.py
def rotate_db_password():
    new_pw = generate_strong_password()
    db.execute(f"ALTER USER app WITH PASSWORD %s", (new_pw,))
    vault.put("myapp/db", {"password": new_pw})
    notify_apps_to_reload()
```

Rotation must be automated.

## What to Notice in This Code

- Secrets carry the shortest possible lifetime.
- Plaintext secrets only live in memory.
- Every secret access leaves an audit trail.
- Rotation runs as automation, not as a runbook step.

## Five Common Mistakes

1. **Committing `.env`.** The single most common incident.
2. **One master key for everything.** Cannot rotate.
3. **Logging secrets in errors or app logs.** Wide exposure via SIEM.
4. **No rotation policy.** A leak becomes an indefinite exposure.
5. **Sharing secrets via Slack or email.** A searchable secret is no secret.

## How This Shows Up in Production

Kubernetes uses `Secret` plus External Secrets Operator (ESO) to sync from vault. CI/CD federates with OIDC to mint short-lived credentials and removes static keys. AWS issues per-instance short-lived credentials through IAM Roles and STS.

## How a Senior Engineer Thinks

- Every secret has an expiry.
- Secret management is co-designed with identity (IAM).
- `.env` is for local development only.
- Time-to-rotate after an incident is an SLO (e.g., under one hour).
- Secret scanners run at both pre-commit and CI.

## Checklist

- [ ] Does every secret have a defined rotation period?
- [ ] Is `.env` in `.gitignore`?
- [ ] Are secret accesses captured as audit logs?
- [ ] Is the rotation runbook documented?
- [ ] Are static credentials removed from CI/CD?

## Practice Problems

1. Explain the difference between environment variables and a vault in one paragraph.
2. How would you measure a rotation SLO?
3. Outline the safe procedure for handling a secret accidentally committed to git.

## Wrap-up and Next Steps

Secret management is about lifetime, not location. Next we look at what the holder of a secret should be allowed to do — least privilege.

<!-- toc:begin -->
- [What is Information Security?](./01-what-is-information-security.md)
- [Authentication and Authorization](./02-authentication-and-authorization.md)
- [Cryptography and Hashes](./03-cryptography-and-hash.md)
- [TLS and Certificates](./04-tls-and-certificates.md)
- [Web Security Basics](./05-web-security-basics.md)
- [SQL Injection and XSS](./06-sql-injection-and-xss.md)
- **Secret Management (current)**
- Least Privilege (upcoming)
- Logging and Audit (upcoming)
- Incident Response (upcoming)
<!-- toc:end -->

## References

- [HashiCorp Vault — Documentation](https://developer.hashicorp.com/vault/docs)
- [AWS KMS — Best Practices](https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html)
- [OWASP — Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [trufflehog — Find Leaked Credentials](https://github.com/trufflesecurity/trufflehog)

Tags: Computer Science, Security, Secrets, Vault, KMS, Rotation

---
series: information-security-101
episode: 7
title: "Information Security 101 (7/10): Secret Management"
status: content-ready
targets:
  tistory: false
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

# Information Security 101 (7/10): Secret Management

> Information Security 101 series (7/10)

**Core question**: What do we lose the moment a secret enters source code?

> Secret management is not about where you put them; it is about how you rotate them.

This is the 7th post in the Information Security 101 series.


![information security 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/information-security-101/07/07-01-big-picture.en.png)
*information security 101 chapter 7 flow overview*
> Secret management is not just storing encrypted keys. It is tracking who accessed what secret when, detecting abnormal access patterns, and proving that no key was exposed during its lifetime.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Secret Management?
- Which signal should the example or diagram make visible for Secret Management?
- What failure should be prevented first when Secret Management reaches a real system?

## What You Will Learn

- Secret types (static, dynamic, user, system)
- The limits of environment variables
- The role of vault and KMS
- Core rotation policy ideas
- Safe patterns for handling secrets in code

## Why It Matters

More than half of large incidents start with leaked secrets. A leaked secret without rotation is a permanent risk.

> Secrets are liabilities, not assets — keep their lifetime short.

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

### Secret Management Tools Compared

| Criterion | HashiCorp Vault | AWS Secrets Manager |
| --- | --- | --- |
| Deployment | Self-hosted / HCP managed | AWS fully managed |
| Strength | Dynamic secrets, fine-grained policy, multi-cloud | Native AWS integration, easy rotation automation |
| Ops burden | Cluster ops/backup/upgrade required | Relatively low |
| Best fit | Hybrid cloud, advanced policy needs | AWS-centric workloads |

The real question is not "which is more secure" but "which can our team operate consistently."

### Rotation Period Strategy

| Secret type | Recommended rotation | Rationale |
| --- | --- | --- |
| API keys | 90 days | Large blast radius on leak |
| Database passwords | 30 days | Core asset access |
| TLS certificates | 90 days (Let's Encrypt default) | Automated renewal expected |
| SSH keys | 180 days or per-use | Infrastructure access path |
| OAuth refresh tokens | 7 days | Session continuity vs. security balance |

Rotation period = f(sensitivity, blast radius, rotation cost). Shorter is safer but costlier to operate.

### Automated Rotation (Python + Vault)

```python
# rotation_example.py
import secrets, string
import hvac

def generate_strong_password(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def rotate_db_password(vault: hvac.Client, db_conn, path: str):
    new_pw = generate_strong_password()
    db_conn.execute("ALTER USER app_user WITH PASSWORD %s", (new_pw,))
    vault.secrets.kv.v2.create_or_update_secret(
        path=path,
        secret={"password": new_pw, "rotated_at": "2026-05-21T10:00:00Z"},
    )
    # Signal app reload (K8s rolling restart, Lambda env update, etc.)
```

Automated rotation must be code, not a runbook entry. Only automation is fast enough during a real incident.

### Secret Leak Detection

```python
# secret_leak_monitor.py
import re

PATTERNS = [
    r"AKIA[0-9A-Z]{16}",                    # AWS Access Key
    r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",  # JWT
    r"password\s*[:=]\s*['\"][^'\"]{8,}",  # password= pattern
]

def scan_for_secrets(line: str) -> bool:
    return any(re.search(p, line, re.IGNORECASE) for p in PATTERNS)
```

Integrate truffleHog / git-secrets / detect-secrets at both pre-commit and CI. Secrets in logs, Slack, git history, or exception trackers must trigger alerts automatically.

### Vault Policy Example

```hcl
# vault-policy: app-read-db
path "kv/data/myapp/db" {
  capabilities = ["read"]
}
```

```yaml
# AppRole config
approle:
  role_name: myapp
  token_ttl: 30m
  token_max_ttl: 2h
  secret_id_ttl: 24h
```

Policy grants minimal path-level access; tokens are short-lived by default.

### Operational Checklist

- Every secret has an owner field and rotation schedule.
- Unused secrets are auto-detected and decommissioned.
- Secret access events flow to SIEM.
- Dev/staging/prod secrets are fully isolated.
- Emergency rotation is validated via automation, not just documented.

## How a Senior Engineer Thinks

- Every secret has an expiry — no exceptions.
- Secret management is co-designed with IAM (identity = the requester of secrets, not the holder).
- `.env` is local-dev only; CI/CD uses OIDC-federated short-lived credentials.
- Time-to-rotate after incident is an SLO (target: under 1 hour).
- Secret scanners run at pre-commit and CI; findings block merge.
- Good systems have no static secrets in code — identity requests secrets at runtime.

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

## Answering the Opening Questions

- **How do static secrets and dynamic secrets differ?**
  - Clarify where API keys, DB passwords, and OAuth tokens are stored, who can read them, and what logs are produced on access.
- **How far does an environment variable's validity extend?**
  - Understanding Vault secret renewal—existing secret's TTL, new secret's start time, rolling method—reduces deployment failures.
- **What roles do Vault and KMS each play?**
  - Define secret-access log analysis, secret-rotation script audits, and leaked-secret scan automation (git-secrets/truffleHog).
<!-- toc:begin -->
## In this series

- [Information Security 101 (1/10): What Is Information Security?](./01-what-is-information-security.md)
- [Information Security 101 (2/10): Authentication and Authorization](./02-authentication-and-authorization.md)
- [Information Security 101 (3/10): Cryptography and Hashing](./03-cryptography-and-hash.md)
- [Information Security 101 (4/10): TLS and Certificates](./04-tls-and-certificates.md)
- [Information Security 101 (5/10): Web Security Basics](./05-web-security-basics.md)
- [Information Security 101 (6/10): SQL Injection and XSS](./06-sql-injection-and-xss.md)
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

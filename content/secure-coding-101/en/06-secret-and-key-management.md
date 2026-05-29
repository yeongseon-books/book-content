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

This is the 6th post in the Secure Coding 101 series.

In this chapter, we will treat secret handling as an operating model rather than a storage trick: separation from code, central secret storage, access control, masking, rotation, and post-leak recovery. That wider frame is what distinguishes a merely hidden secret from a recoverable one.

> Secrets belong outside the codebase, with short lifetimes, explicit access control, and a rotation path you can execute under pressure.


![secure coding 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/06/06-01-concept-at-a-glance.en.png)
*secure coding 101 chapter 6 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Secret and Key Management?
- Which signal should the example or diagram make visible for Secret and Key Management?
- What failure should be prevented first when Secret and Key Management reaches a real system?

## Questions This Chapter Answers

- What counts as a *secret*
- Why *hard-coded* secrets are dangerous
- The role of a *secret manager*
- What *key rotation* means
- A five-step routine and five common mistakes

## Why It Matters

The most common incident is a *secret committed to git*. Once pushed, it is *forever traceable*. Even *history rewrite* is not a complete fix.

> *Design every secret on the assumption that it *will leak someday*.*

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

## Git Secret Scanning and Pre-Commit Blocking

Once a secret is committed, the entire repository history is contaminated. Manual `git log -p` searches work for small repos, but large codebases need dedicated scanning tools.

```bash
# truffleHog — entropy-based + pattern-based scanning
trufflehog git file://. --since-commit HEAD~100 --json

# git-secrets — AWS pattern built-in, pre-commit hook
git secrets --install
git secrets --register-aws
git secrets --scan

# gitleaks — TOML rule-file based
gitleaks detect --source . --report-format json --report-path leak-report.json
```

The most effective interception point is **pre-commit**. Blocking at commit time prevents secrets from ever reaching the remote.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

CI adds a second layer for PRs. If someone bypasses pre-commit (force push, GUI commit), the PR scan becomes the last defense.

```yaml
# GitHub Actions example
- name: Secret scan
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## HashiCorp Vault Configuration in Practice

Vault provides dynamic credentials, policy-based access control, and audit logging beyond simple key-value storage. The first things to configure in production are policies and authentication methods.

```hcl
# policy: app-db-read.hcl
path "secret/data/prod/db" {
  capabilities = ["read"]
}

path "secret/data/prod/db" {
  capabilities = ["update"]
  required_parameters = ["rotation_id"]
}
```

```bash
# Register policy and issue token
vault policy write app-db-read app-db-read.hcl
vault token create -policy=app-db-read -ttl=1h -use-limit=10
```

Setting both TTL and use-limit narrows the damage window even if a token leaks. In Kubernetes environments, ServiceAccount authentication eliminates the need to embed tokens in code.

```python
import hvac

client = hvac.Client(url="https://vault.internal:8200")
# Kubernetes auth — automatic authentication via Pod's ServiceAccount
client.auth.kubernetes.login(
    role="app-db-reader",
    jwt=open("/var/run/secrets/kubernetes.io/serviceaccount/token").read()
)
secret = client.secrets.kv.v2.read_secret_version(
    mount_point="secret", path="prod/db"
)
db_password = secret["data"]["data"]["password"]
```

## Dynamic Credentials and Lease Management

Vault's dynamic secrets generate temporary credentials on demand and automatically revoke them when the lease expires. This pattern eliminates long-lived passwords entirely.

```bash
# DB secret engine setup
vault secrets enable database
vault write database/config/mydb \
  plugin_name=mysql-database-plugin \
  connection_url="{{username}}:{{password}}@tcp(db.internal:3306)/" \
  allowed_roles="app-role" \
  username="vault-admin" \
  password="vault-admin-pw"

vault write database/roles/app-role \
  db_name=mydb \
  creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}'; \
    GRANT SELECT, INSERT ON mydb.* TO '{{name}}'@'%';" \
  default_ttl="1h" \
  max_ttl="24h"
```

```python
# Request dynamic credentials from the app
creds = client.secrets.database.generate_credentials(name="app-role")
db_user = creds["data"]["username"]  # v-app-role-abc123
db_pass = creds["data"]["password"]  # temporary, auto-revoked after 1 hour
lease_id = creds["lease_id"]

# Renew lease if needed
client.sys.renew_lease(lease_id=lease_id, increment=3600)
```

The advantage of dynamic credentials is that rotation becomes unnecessary. The value itself has a lifespan, so even if it leaks, it becomes useless after expiry.

## Emergency Revocation Procedure

When a secret leak is confirmed, **immediate revocation** must precede replacement. Revocation invalidates the existing value; replacement issues a new one. The order matters.

```text
Emergency Revocation Runbook

1. Determine blast radius
   - Which environments/services use the leaked secret
   - Check recent access via secret manager audit logs

2. Immediate revocation
   - Vault: vault lease revoke -prefix secret/data/prod/
   - AWS: aws secretsmanager delete-secret --secret-id <id> --force-delete
   - GitHub: Settings > Secrets > Delete

3. Issue new value and deploy
   - Generate new secret (entirely unrelated to the old value)
   - Restart services via deployment pipeline
   - Verify connection pools, caches, and worker processes all refreshed

4. Post-verification
   - Attempt authentication with old value → confirm failure
   - Verify revocation event in audit logs
   - Write incident report
```

```python
# Emergency bulk revocation — revoke all leases under a Vault prefix
import hvac

client = hvac.Client(url="https://vault.internal:8200", token=emergency_token)

# Prefix-based bulk revocation
client.sys.revoke_prefix("database/creds/app-role")

# Destroy specific secret versions (unrecoverable)
client.secrets.kv.v2.destroy_secret_versions(
    path="prod/db",
    versions=[1, 2, 3],
    mount_point="secret"
)
```

## Secret Scope Isolation Strategy

The broader a single secret's reach, the higher the cost of a leak. Three patterns reduce scope in practice.

| Isolation axis | Method | Effect |
|---|---|---|
| Per environment | Different values for dev/staging/prod | Dev leak does not affect production |
| Per service | Dedicated secret per service | One service compromise does not spread |
| Per lifetime | Short-lived tokens + dynamic issuance | Leaked value becomes useless after expiry |

```python
# Per-environment isolation — config loader example
import os

ENV = os.environ.get("APP_ENV", "dev")

SECRET_PATHS = {
    "dev": "secret/data/dev/db",
    "staging": "secret/data/staging/db",
    "prod": "secret/data/prod/db",
}

def get_db_secret(vault_client):
    path = SECRET_PATHS[ENV]
    return vault_client.secrets.kv.v2.read_secret_version(
        mount_point="secret", path=path.replace("secret/data/", "")
    )["data"]["data"]["password"]
```

## CI/CD Pipeline Secret Safety

CI environments are high-risk points for secret exposure. Build logs may be public, PR builds from forks may access secrets, and caches can retain values.

```yaml
# GitHub Actions — secret masking and least privilege
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # for OIDC token issuance
      contents: read
    steps:
      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/deploy-role
          aws-region: ap-northeast-2
          # OIDC for temporary credentials instead of long-lived keys

      - name: Read secret
        run: |
          SECRET=$(aws secretsmanager get-secret-value \
            --secret-id prod/api-key \
            --query SecretString --output text)
          echo "::add-mask::$SECRET"  # automatic log masking
          echo "API_KEY=$SECRET" >> "$GITHUB_ENV"
```

Three principles:
1. Use OIDC-based temporary credentials instead of long-lived keys.
2. Use `::add-mask::` to block log output.
3. Never pass secrets to PR builds from forks.

## Secret Audit and Access Monitoring

Even with a secret manager in place, failure to monitor who reads what delays leak detection.

```bash
# Enable Vault audit log
vault audit enable file file_path=/var/log/vault/audit.log

# Audit log format (JSON)
# {
#   "type": "response",
#   "auth": {"token_type": "service", "policies": ["app-db-read"]},
#   "request": {"path": "secret/data/prod/db", "operation": "read"},
#   "response": {"data": {"data": "hmac-sha256:..."}},  # values are HMAC'd
#   "time": "2026-05-15T09:23:41Z"
# }
```

Forward audit logs to a SIEM (Splunk, Elastic, Datadog) and apply alert rules:

```text
Alert rule examples:
- Secret read outside business hours → immediate notification
- Same token reads 50+ times in 10 minutes → automatic token revocation
- Unauthorized policy access attempt → incident creation
- Read from a path never accessed before → review request
```

## In-Memory Secret Protection

Secrets left in process memory are vulnerable to core dumps, heap analysis, and `/proc/<pid>/mem` access.

```python
import ctypes
import os

def secure_zero(buffer: bytearray):
    """Safely wipe a secret from memory."""
    ctypes.memset(
        (ctypes.c_char * len(buffer)).from_buffer(buffer),
        0,
        len(buffer)
    )

# Usage
secret_bytes = bytearray(get_secret_from_vault().encode())
try:
    authenticate(secret_bytes)
finally:
    secure_zero(secret_bytes)  # zero out immediately after use
```

Python strings are immutable, so you must use `bytearray` for zeroing. Go has `memguard`, Rust has the `secrecy` crate. This is not perfect, but it reduces the window during which a value remains in memory after the GC releases the reference.

## Incident Response Timeline for Secret Leaks

The most important metric in an actual incident is MTTC (Mean Time To Contain) — the time from detection to revocation. A recommended timeline:

```text
T+0m    Detection (secret scan alert, external report, anomalous access alarm)
T+5m    Determine blast radius — which env, service, and data the secret reaches
T+15m   Immediate revocation — invalidate the secret (Vault revoke, AWS delete, GitHub invalidate)
T+30m   Issue new value and deploy — restart services, verify pool refresh
T+60m   Post-verification — confirm old value fails auth, audit log clean
T+24h   Incident report — root cause, prevention measures, process improvements
```

The most common failure point is T+5m to T+15m. If there is no documentation of where a secret is used, determining blast radius takes too long. If revocation is manual, finding the responsible person adds more delay.

```python
# Secret inventory — track which secret is used where
SECRET_INVENTORY = {
    "prod/db/password": {
        "services": ["api-server", "batch-worker", "analytics"],
        "environments": ["prod"],
        "rotation_owner": "platform-team",
        "last_rotated": "2026-04-20",
        "emergency_contact": "#incident-channel",
    },
    "prod/stripe/api-key": {
        "services": ["payment-service"],
        "environments": ["prod"],
        "rotation_owner": "payment-team",
        "last_rotated": "2026-05-01",
        "emergency_contact": "#payment-oncall",
    },
}

def get_affected_services(secret_id: str) -> list[str]:
    entry = SECRET_INVENTORY.get(secret_id, {})
    return entry.get("services", ["unknown — inventory update needed"])
```

With this inventory, the question "where is this secret used?" gets an immediate answer during an incident. Vault policies and role mappings partially serve this purpose, but service-level mapping requires separate documentation.

## Responding to a .env File Leak

A `.env` file should be local-only, but accidental commits or backup inclusions happen. The response is not simply deleting the file.

```bash
# 1. Remove .env from Git history (BFG Repo-Cleaner)
bfg --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 2. Treat ALL values in .env as compromised
#    → immediate revocation + new value issuance for each

# 3. Verify .gitignore contains .env (should already, but confirm)
grep -q "^\.env$" .gitignore || echo ".env" >> .gitignore

# 4. Notify the team — forks retain the old history
```

Even after BFG cleans the history, clones, forks, and CI caches still hold the old records. History cleanup is a secondary measure; the essential action is immediate revocation and replacement of every affected secret.

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

- **What values should be treated as secrets?**
  - The criterion defined in the article is "any value that becomes dangerous if known." DB passwords, API keys, signing keys, and tokens are typical, but internal service URLs or environment-specific config values should also be treated as secrets if exposure would widen the attack surface. As the dynamic credentials section showed, shorter-lived values reduce secret management burden.
- **Why is a hardcoded secret fatal even if pushed to Git just once?**
  - Git history leaves traces in forks, CI caches, and collaboration tools even after deletion. History rewriting alone does not fully recover, so blocking at commit time with pre-commit hooks and CI scans is essential, and if exposure is confirmed, immediate revocation and new value issuance is the only response.
- **How does a secret manager differ from environment variables?**
  - Environment variables are merely an injection channel with no answer for who read it, when to rotate, or how to revoke after exposure. A secret manager bundles access policy, audit logs, automatic rotation, dynamic issuance, and emergency revocation into an operational system. As the Vault configuration section showed, TTL, use-limit, and lease-based auto-expiry are impossible with environment variables alone.
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

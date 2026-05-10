---
series: secure-coding-101
episode: 5
title: Safe Data Storage
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Encryption
  - DataProtection
  - PII
  - SecureCoding
  - Cryptography
seo_description: At-rest encryption, transport encryption, sensitive data separation, and a five-step playbook for safe data storage.
last_reviewed: '2026-05-04'
---

# Safe Data Storage

> Secure Coding 101 series (5/10)

<!-- a-grade-intro:begin -->

**Core question**: If somebody walks off with one of *our disks*, how much of the data inside is *readable*?

> *Data must be protected *in motion* and *at rest*. If only one is safe, *everything is at risk*.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The difference between *at-rest* and *in-transit*
- Classifying *PII* and *sensitive data*
- *Symmetric* and *asymmetric* encryption basics
- *Tokenization* and *pseudonymization*
- Five storage steps and five common mistakes

## Why It Matters

Both legally (GDPR, regional privacy laws) and in incident cost, *sensitive data leakage* is the most expensive class of breach. Plaintext storage is a *time bomb*.

> *Collect less, separate more, lock harder.*

## Concept at a Glance

```mermaid
flowchart LR
    App["App"] -->|TLS| DB["Database"]
    DB -->|At-rest encryption| Disk["Disk"]
    App --> KMS["KMS (key management)"]
```

## Key Terms

- **PII**: information that *identifies* a person.
- **At-rest**: data sitting in storage.
- **In-transit**: data *moving* across the network.
- **KMS**: a service that manages *keys themselves*.
- **Tokenization**: store a *substitute token*, not the original.

## Before/After

**Before**: National ID and card numbers stored as *plaintext*. Logs hold them too.

**After**: National ID *hashed*, card number *tokenized*, storage encrypted with a *KMS-managed key*.

## Hands-on: Safe Storage in Five Steps

### Step 1 — Classify the data

```python
SENSITIVE = {"ssn", "card_number", "password", "address"}
def is_sensitive(field): return field in SENSITIVE
```

### Step 2 — Use TLS for transport

```python
# Always TLS between client and DB; do not disable certificate verification.
import psycopg
conn = psycopg.connect("postgresql://...?sslmode=verify-full")
```

### Step 3 — Encrypt at rest with envelope encryption

```python
from cryptography.fernet import Fernet
data_key = Fernet(kms.get_data_key())
ciphertext = data_key.encrypt(b"card-number")
```

### Step 4 — Allow lookup with a *deterministic hash*

```python
import hmac, hashlib
def lookup_hash(value, key):
    return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()
```

### Step 5 — Protect backups too

```bash
# Encrypt the backup file itself; store the key elsewhere.
gpg --symmetric --cipher-algo AES256 backup.sql
```

## What to Notice in This Code

- *Envelope encryption* separates the *data key* from the *KMS key*.
- A *deterministic hash* enables lookup, but the salt is *system-wide*, not per-row.
- Both transit and storage are protected.

## Five Common Mistakes

1. **Storing sensitive data as *plaintext*.** One disk is enough.
2. **Keeping keys *next to the code*.** Then separation buys nothing.
3. **Disabling *TLS certificate verification*.** Opens the door to *MITM*.
4. **Letting *sensitive data flow into logs*.** Logs are also storage.
5. **Plaintext *backups*.** The largest blast radius in any incident.

## How This Shows Up in Production

Most teams use a *KMS* (AWS KMS, GCP KMS, Vault), apply *envelope encryption* with periodic *key rotation*. Some sensitive fields (like card numbers) are *tokenized* so they *never enter our system* at all.

## How a Senior Engineer Thinks

- *The strongest defense is to *collect less*.*
- *Keep keys *physically separate* from data.*
- *Protect transit and storage *both*.*
- *If key rotation is impossible, the design is wrong.*
- *Backups are also *data*.*

## Checklist

- [ ] PII is *catalogued*.
- [ ] Storage is encrypted via *KMS*.
- [ ] Transit uses *TLS with certificate verification*.
- [ ] Backups are *encrypted*.

## Practice Problems

1. List the *PII fields* in your service.
2. Diagram the flow of *envelope encryption*.
3. Write a function to *tokenize* card numbers.

## Wrap-up and Next Steps

Encrypted data is useless if the *keys leak*. Next we look at *secret and key management*.

<!-- toc:begin -->
- [What Is Secure Coding?](./01-what-is-secure-coding.md)
- [Input Validation](./02-input-validation.md)
- [Authentication and Session](./03-authentication-and-session.md)
- [Authorization and Permissions](./04-authorization-and-permissions.md)
- **Safe Data Storage (current)**
- Secret and Key Management (upcoming)
- SQL Injection and Safe ORM Usage (upcoming)
- XSS and CSRF Defense (upcoming)
- Managing Dependency Vulnerabilities (upcoming)
- Safe Logging and Audit (upcoming)
<!-- toc:end -->

## References

- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [AWS KMS — Envelope Encryption](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html)
- [Google Cloud KMS](https://cloud.google.com/kms/docs)
- [HashiCorp Vault](https://developer.hashicorp.com/vault/docs)

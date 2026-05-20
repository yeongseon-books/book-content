---
series: secure-coding-101
episode: 5
title: "Secure Coding 101 (5/10): Safe Data Storage"
status: content-ready
targets:
  tistory: false
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
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (5/10): Safe Data Storage

The moment an application stores sensitive data, it stops being only a feature system and becomes a custody system as well. From the user's perspective, it may be a simple signup flow. From the operator's perspective, it may already include password hashes, address history, export files, and backups that become extremely expensive the moment they leak.

This is post 5 in the Secure Coding 101 series.

Here, we will look past the usual shorthand of "turn on disk encryption" and treat storage security as a chain: data classification, transport protection, storage encryption, key separation, and backup handling. That is the level where real incident cost is determined.

> Secure storage starts before encryption. First decide what not to collect, then separate what you keep, and finally protect the transport, storage, and backup path as one system.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Safe Data Storage?
- Which signal should the example or diagram make visible for Safe Data Storage?
- What failure should be prevented first when Safe Data Storage reaches a real system?

## Big Picture

![secure coding 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/05/05-01-concept-at-a-glance.en.png)

*secure coding 101 chapter 5 flow overview*

This picture places Safe Data Storage inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Safe Data Storage is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions This Chapter Answers

- The difference between *at-rest* and *in-transit*
- Classifying *PII* and *sensitive data*
- *Symmetric* and *asymmetric* encryption basics
- *Tokenization* and *pseudonymization*
- Five storage steps and five common mistakes

## Why It Matters

Both legally (GDPR, regional privacy laws) and in incident cost, *sensitive data leakage* is the most expensive class of breach. Plaintext storage is a *time bomb*.

> *Collect less, separate more, lock harder.*

## Concept at a Glance

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

## Answering the Opening Questions

- **What boundary should you inspect first when applying Safe Data Storage?**
  - The article treats Safe Data Storage as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Safe Data Storage?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Safe Data Storage reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Secure Coding 101 (1/10): What Is Secure Coding?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): Input Validation](./02-input-validation.md)
- [Secure Coding 101 (3/10): Authentication and Session](./03-authentication-and-session.md)
- [Secure Coding 101 (4/10): Authorization and Permissions](./04-authorization-and-permissions.md)
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
- [NIST SP 800-57 Part 1 Rev. 5 — Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)

Tags: Encryption, DataProtection, PII, SecureCoding, Cryptography

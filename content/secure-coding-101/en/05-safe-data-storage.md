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

This is the 5th post in the Secure Coding 101 series.

Here, we will look past the usual shorthand of "turn on disk encryption" and treat storage security as a chain: data classification, transport protection, storage encryption, key separation, and backup handling. That is the level where real incident cost is determined.

> Secure storage starts before encryption. First decide what not to collect, then separate what you keep, and finally protect the transport, storage, and backup path as one system.


![secure coding 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/05/05-01-concept-at-a-glance.en.png)
*secure coding 101 chapter 5 flow overview*

## Questions to Keep in Mind

- What distinguishes encryption at rest from encryption in transit?
- Why must classifying PII and sensitive data come first?
- What roles do symmetric keys, asymmetric keys, and KMS each play?

## Questions This Chapter Answers

- The difference between *at-rest* and *in-transit*
- Classifying *PII* and *sensitive data*
- *Symmetric* and *asymmetric* encryption basics
- *Tokenization* and *pseudonymization*
- Five storage steps and five common mistakes

## Why It Matters

Sensitive data leakage is the most expensive class of breach — both legally (GDPR, regional privacy laws) and in incident cost. Plaintext storage is a time bomb.

Storage security is not a single-component problem either. The transport segment between application and database, the storage segment where the database writes to disk, the backups created for recovery, and the logs kept for operational convenience all belong to the same storage chain. If one link is unprotected, the entire defense collapses.

> *Collect less, separate more, lock harder.*

## Key Terms

- **PII**: information that *identifies* a person — directly or indirectly.
- **At-rest**: data sitting in storage (disk, object store).
- **In-transit**: data *moving* across the network.
- **KMS**: a service that manages *encryption keys themselves* — storage, protection, rotation.
- **Tokenization**: store a *substitute token*, not the original value.

## Before/After

**Before**: National ID and card numbers stored as *plaintext*. Logs and backups contain them too. A single storage exposure creates a large blast radius.

**After**: National ID *hashed* or stored separately for lookup purposes, card number *tokenized*, storage encrypted with a *KMS-managed key*. Backups and logs receive the same level of protection.

## Hands-on: Safe Storage in Five Steps

### Step 1 — Classify the data

```python
SENSITIVE = {"ssn", "card_number", "password", "address"}
def is_sensitive(field): return field in SENSITIVE
```

You cannot design an encryption strategy without knowing what is sensitive. First catalogue which fields fall under regulation and which values can identify a user if leaked. This list drives storage, logging, and backup policy together.

### Step 2 — Use TLS for transport

```python
# Always TLS between client and DB; do not disable certificate verification.
import psycopg
conn = psycopg.connect("postgresql://...?sslmode=verify-full")
```

Even strong disk encryption is meaningless if the segment between application and database is plaintext — it becomes vulnerable to man-in-the-middle attacks. TLS is not an optional feature but a baseline assumption. Disabling certificate verification significantly weakens the protection.

### Step 3 — Encrypt at rest with envelope encryption

```python
from cryptography.fernet import Fernet
data_key = Fernet(kms.get_data_key())
ciphertext = data_key.encrypt(b"card-number")
```

Envelope encryption separates the key that encrypts data (DEK) from the key that protects the DEK (KEK managed by KMS). This separation simplifies key rotation and access control, and reduces the risk of keys ending up next to the data they protect.

### Step 4 — Allow lookup with a *deterministic hash*

```python
import hmac, hashlib
def lookup_hash(value, key):
    return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()
```

Some fields only need equality comparison without decrypting the original. A deterministic hash preserves lookup capability while reducing plaintext exposure. The hash key itself must also be managed separately.

### Step 5 — Protect backups too

```bash
# Encrypt the backup file itself; store the key elsewhere.
gpg --symmetric --cipher-algo AES256 backup.sql
```

In practice, the largest blast radius often comes from backups rather than the live database. Backups are copied, moved, and retained long-term — their exposure surface is wide. Protecting only production data while leaving backups in plaintext means you have done half the job.

## What to Notice in This Code

- *Envelope encryption* separates the *data key* from the *KMS key*.
- A *deterministic hash* enables lookup, but the salt is *system-wide*, not per-row.
- Both transit and storage are protected.
- Backups and logs also fall within the scope of storage security.

## Five Common Mistakes

1. **Storing sensitive data as *plaintext*.** A single disk or backup exposure is enough for a breach.
2. **Keeping keys *next to the code*.** Then separation buys nothing.
3. **Disabling *TLS certificate verification*.** Opens the door to *MITM*.
4. **Letting *sensitive data flow into logs*.** Logs are also storage.
5. **Plaintext *backups*.** The largest blast radius in any incident.

## How This Shows Up in Production

Most teams use a *KMS* (AWS KMS, GCP KMS, Vault), apply *envelope encryption* with periodic *key rotation*. Some sensitive fields (like card numbers) are *tokenized* so they *never enter our system* at all.

A senior engineer also applies the principle of minimal collection here. The strongest protection is not collecting data in the first place. Only retain what is strictly necessary, and check whether hashing or tokenization can replace storing the original for the intended lookup purpose. Storage security often starts with *less storage* rather than *stronger encryption*.

## How a Senior Engineer Thinks

- *The strongest defense is to *collect less*.*
- *Keep keys *physically separate* from data.*
- *Protect transit and storage *both*.*
- *If key rotation is impossible, the design is wrong.*
- *Backups are also *data*.*

## Deep Dive: Envelope Encryption, Field Encryption, Key Rotation, and Compliance

Storage security is not a binary "encrypted or not" question. You must design specifically which layer encrypts what with which key, how keys rotate, and how the scheme maps to regulatory requirements.

### Full Envelope Encryption Flow

Envelope encryption separates the DEK (Data Encryption Key) that encrypts data from the KEK (Key Encryption Key) that encrypts the DEK.

```python
"""envelope_encryption.py — full envelope encryption implementation"""
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class EnvelopeEncryption:
    def __init__(self, kms_client):
        self.kms = kms_client

    def encrypt(self, plaintext: bytes, kms_key_id: str) -> dict:
        """Envelope encrypt: generate DEK → encrypt data → encrypt DEK with KEK"""
        # 1) Generate DEK (256-bit AES key)
        dek = os.urandom(32)
        nonce = os.urandom(12)

        # 2) Encrypt data with DEK (AES-GCM)
        aesgcm = AESGCM(dek)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # 3) Encrypt the DEK itself via KMS
        encrypted_dek = self.kms.encrypt(
            KeyId=kms_key_id,
            Plaintext=dek,
        )["CiphertextBlob"]

        # 4) Store encrypted data + encrypted DEK + nonce together
        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "encrypted_dek": base64.b64encode(encrypted_dek).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "kms_key_id": kms_key_id,
        }

    def decrypt(self, envelope: dict) -> bytes:
        """Decrypt: KEK decrypts DEK → DEK decrypts data"""
        # 1) Decrypt the DEK via KMS
        dek = self.kms.decrypt(
            CiphertextBlob=base64.b64decode(envelope["encrypted_dek"]),
            KeyId=envelope["kms_key_id"],
        )["Plaintext"]

        # 2) Decrypt data with DEK
        aesgcm = AESGCM(dek)
        nonce = base64.b64decode(envelope["nonce"])
        ciphertext = base64.b64decode(envelope["ciphertext"])
        return aesgcm.decrypt(nonce, ciphertext, None)
```

Advantages of this structure:
- Even if a DEK leaks, decryption is impossible without the KEK
- During KEK rotation, you only re-encrypt the DEK — no need to re-encrypt all data
- Minimizes KMS API calls while maintaining strong protection (DEK exists only in memory)

### Field-Level Encryption

Database-wide encryption (TDE) alone cannot control application-level access. Selectively encrypting specific fields means even a DBA cannot see sensitive data in plaintext.

```python
from sqlalchemy import TypeDecorator, String
import json

class EncryptedField(TypeDecorator):
    """SQLAlchemy column type — transparent field encryption/decryption"""
    impl = String
    cache_ok = True

    def __init__(self, envelope_enc: EnvelopeEncryption, kms_key_id: str):
        super().__init__()
        self.enc = envelope_enc
        self.kms_key_id = kms_key_id

    def process_bind_param(self, value, dialect):
        """Encrypt on write"""
        if value is None:
            return None
        envelope = self.enc.encrypt(value.encode("utf-8"), self.kms_key_id)
        return json.dumps(envelope)

    def process_result_value(self, value, dialect):
        """Decrypt on read"""
        if value is None:
            return None
        envelope = json.loads(value)
        return self.enc.decrypt(envelope).decode("utf-8")

# Usage example
class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))  # regular field
    ssn = Column(EncryptedField(enc, "alias/patient-key"))  # encrypted field
    diagnosis = Column(EncryptedField(enc, "alias/medical-key"))  # separate key
```

Using different KMS keys per field lets you enforce field-level access policies. For example, a receptionist can access names only, while a physician can access diagnosis data — controlled through KMS key policies.

### Key Rotation Procedure

Key rotation is not simply creating a new key. Existing data is encrypted with the old key, so gradual migration is required.

```python
def rotate_dek_for_table(table_name: str, old_key_id: str, new_key_id: str):
    """Re-encrypt table's encrypted fields with a new key."""
    rows = db.query(table_name).filter(
        table_name.kms_key_version == old_key_id
    ).limit(1000).all()

    for row in rows:
        # 1) Decrypt with old key
        plaintext = envelope_enc.decrypt(json.loads(row.encrypted_data))
        # 2) Re-encrypt with new key
        new_envelope = envelope_enc.encrypt(plaintext, new_key_id)
        # 3) Update
        row.encrypted_data = json.dumps(new_envelope)
        row.kms_key_version = new_key_id

    db.commit()
    return len(rows)
```

Key rotation principles:
1. Run rotation in batches. Rotating everything at once causes long-running locks.
2. Maintain a grace period where both old and new keys are valid simultaneously.
3. Monitor rotation progress; disable the old key only when zero records remain encrypted with it.
4. Record rotation history in audit logs.

### Regulation Mapping Table

| Regulation | Target Data | Key Requirements | Code-Level Response |
| --- | --- | --- | --- |
| GDPR | EU resident personal data | Right to erasure, minimal collection, encryption | Field encryption + deletion API |
| PIPA (Korea) | Korean resident personal data | Consent-based collection, safety measures | Consent history storage + encryption |
| PCI DSS | Card numbers (PAN) | Tokenization or encryption, key separation | Tokenization service integration |
| HIPAA | Medical information (PHI) | Access control, audit, encryption | Per-field key separation + access logs |

Each regulation defines "encryption" at a different level. PCI DSS specifically prescribes storage and transit protection for PAN, while GDPR requires adequacy of technical measures. Identifying target regulations at design time avoids costly rework later.

### Tokenization Service Integration

For data with particularly heavy regulatory burden — like card numbers — tokenization is the safest approach: the original never enters your system.

```python
class TokenizationService:
    """Client for an external tokenization service"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def tokenize(self, pan: str) -> str:
        """Replace card number with a token. Original is never stored internally."""
        resp = httpx.post(
            f"{self.base_url}/tokenize",
            json={"value": pan, "format": "preserving"},
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        resp.raise_for_status()
        return resp.json()["token"]  # e.g. "tok_4242424242421234"

    def detokenize(self, token: str) -> str:
        """Restore original only at payment time. Access audit required."""
        resp = httpx.post(
            f"{self.base_url}/detokenize",
            json={"token": token},
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        resp.raise_for_status()
        return resp.json()["value"]
```

The key benefit of tokenization is reducing PCI DSS scope. If the original card number never exists in your internal systems, those systems fall outside PCI DSS audit requirements.

### Safe Deletion and Right to Erasure

Implementing GDPR's Right to Erasure or similar deletion requests in code requires a systematic approach beyond a simple DELETE statement.

```python
from datetime import datetime, timezone
from enum import Enum

class DeletionStatus(str, Enum):
    REQUESTED = "requested"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class DeletionRequest:
    id: str
    user_id: str
    requested_at: datetime
    status: DeletionStatus
    affected_systems: list[str]

def process_deletion_request(request_id: str):
    """Process a deletion request. Remove data from all storage systems."""
    req = get_deletion_request(request_id)
    req.status = DeletionStatus.IN_PROGRESS

    systems = [
        ("primary_db", delete_from_primary_db),
        ("search_index", delete_from_search_index),
        ("analytics", anonymize_in_analytics),
        ("backups", schedule_backup_purge),
        ("logs", redact_from_logs),
        ("cache", invalidate_cache),
    ]

    results = {}
    for system_name, delete_fn in systems:
        try:
            delete_fn(req.user_id)
            results[system_name] = "success"
        except Exception as e:
            results[system_name] = f"failed: {e}"

    if all(v == "success" for v in results.values()):
        req.status = DeletionStatus.COMPLETED
    else:
        req.status = DeletionStatus.FAILED

    # Deletion history must be retained (legal evidence)
    audit_log(
        "data_deletion",
        user_id=req.user_id,
        results=results,
        completed_at=datetime.now(timezone.utc).isoformat(),
    )
```

Commonly overlooked points in deletion implementation:
- Deletion from backups may not be immediately possible. Design for automatic removal after the retention period expires.
- Anonymization may be more appropriate than deletion for analytics data.
- The deletion record itself must be preserved as legal evidence.
- Caches and search indexes are also deletion targets.

### Backup Encryption and Restore Testing

Encrypted backups are meaningless if restore is impossible. Verify the restore procedure regularly.

```python
import subprocess
from datetime import datetime

def create_encrypted_backup(db_url: str, backup_dir: str, kms_key_id: str) -> str:
    """Dump database and protect with envelope encryption."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_file = f"{backup_dir}/dump_{timestamp}.sql"
    encrypted_file = f"{dump_file}.enc"

    # 1) DB dump
    subprocess.run(
        ["pg_dump", db_url, "-f", dump_file],
        check=True,
    )

    # 2) Envelope encrypt
    with open(dump_file, "rb") as f:
        plaintext = f.read()

    envelope = envelope_enc.encrypt(plaintext, kms_key_id)

    with open(encrypted_file, "w") as f:
        json.dump(envelope, f)

    # 3) Delete plaintext dump immediately
    os.unlink(dump_file)

    return encrypted_file

def verify_backup_restore(encrypted_file: str) -> bool:
    """Verify backup restorability. Recommend monthly automated runs."""
    try:
        with open(encrypted_file, "r") as f:
            envelope = json.load(f)
        plaintext = envelope_enc.decrypt(envelope)
        # Basic validation that decrypted content is valid SQL
        assert plaintext.startswith(b"--") or plaintext.startswith(b"SET")
        return True
    except Exception as e:
        alert("backup_restore_failed", file=encrypted_file, error=str(e))
        return False
```

Backup security checklist:
- Encrypt backup files at the same level as production data.
- Test backup restoration regularly (at least monthly).
- Set backup retention periods to match regulatory requirements.
- Maintain separate access logs for backups.
- Delete plaintext intermediate files immediately.

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

- **What distinguishes encryption at rest from encryption in transit?**
  - Encryption at rest protects data sitting on disk; encryption in transit protects data moving over the network. As the envelope encryption implementation showed, at-rest uses a DEK+KEK structure separating keys, while in-transit uses TLS to protect the segment. Both must be applied for the full chain to be safe.
- **Why must classifying PII and sensitive data come first?**
  - As the regulation mapping table showed, different data types require different protection levels and regulations. Encrypting everything uniformly without classification degrades performance from over-protection, or conversely creates legal risk by missing regulated targets. Step 1's SENSITIVE classification becomes the reference for all subsequent decisions.
- **What roles do symmetric keys, asymmetric keys, and KMS each play?**
  - In envelope encryption, data is encrypted fast with a symmetric key (AES-GCM), and that symmetric key is protected by a KEK managed by KMS. Asymmetric keys are used for key exchange or signing. KMS is the central service handling KEK storage, access control, rotation, and auditing.
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

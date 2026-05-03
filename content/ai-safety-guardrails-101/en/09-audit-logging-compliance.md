---
title: Audit Logging and Compliance
series: ai-safety-guardrails-101
episode: 9
language: en
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Audit Logging
- Compliance
- GDPR
last_reviewed: '2026-05-03'
---

# Audit Logging and Compliance

> AI Safety & Guardrails 101 Series (9/10)

---
## Section 1

## Why Audit Logs Differ From Application Logs

In LLM systems, audit logs are the basis for compliance, incident investigation, and model improvement, not casual debugging. Design them separately from application logs.

| Property | Application log | Audit log |
| --- | --- | --- |
| Retention | 7 to 30 days | 1 to 7 years (regulation-dependent) |
| Mutability | Freely editable | Append-only, immutable |
| Access | Engineers in general | Security and compliance only |
| Format | Free-form text | Structured schema |
| PII | Masking recommended | Masking required, keys stored separately |

Application logs answer "what happened" quickly. Audit logs reconstruct "why a decision was made" much later.

## What to Record

For each LLM request, the audit record carries these fields.

```python
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import uuid

@dataclass
class AuditRecord:
    request_id: str
    timestamp: str
    user_id_hash: str          # PII becomes a hash
    api_key_id: str
    model: str
    input_token_count: int
    output_token_count: int
    cost_usd: float
    guardrail_decisions: list  # ["pii_redacted", "moderation_passed", ...]
    blocked: bool
    block_reason: str | None
    prompt_hash: str           # raw text lives in a separate store
    response_hash: str
    retrieved_chunk_ids: list[int]
    latency_ms: int

def make_record(user_id: str, prompt: str, response: str, **kw) -> AuditRecord:
    return AuditRecord(
        request_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        user_id_hash=hashlib.sha256(user_id.encode()).hexdigest()[:16],
        prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),
        response_hash=hashlib.sha256(response.encode()).hexdigest(),
        **kw,
    )
```

Raw prompt and response do not enter the audit record. Store them in a separate PII-aware store with KMS encryption. The audit log keeps only the hashes for integrity checks and later joins.

## PII Masking and Separate Storage

GDPR, PIPA, and HIPAA all require that data with different processing purposes live in different stores. Audit serves verification; raw prompts serve model improvement.

```python
def store_audit(record: AuditRecord, prompt: str, response: str):
    # 1. Audit log: append-only, hashes only
    audit_db.insert(asdict(record))

    # 2. PII store: KMS encrypted, short retention based on user consent
    if user_consent_to_train(record.user_id_hash):
        encrypted_prompt = kms.encrypt(prompt)
        encrypted_response = kms.encrypt(response)
        pii_store.put(record.request_id, {
            "prompt": encrypted_prompt,
            "response": encrypted_response,
            "ttl": 90,  # days
        })
```

When a user requests deletion, remove from the PII store but keep the audit log hashes for integrity.

## Append-Only Storage

Once written, an audit record must be unchangeable by anyone. Three patterns:

1. **WORM (Write Once Read Many) S3 bucket**: Object Lock with Compliance Mode. Even root cannot delete within retention.
2. **Append-only database**: ClickHouse or TimescaleDB. Do not grant UPDATE or DELETE to application users.
3. **Hash chain**: each record contains the previous record's hash, so any tampering is detectable later.

```python
from hashlib import sha256

def chain_hash(prev_hash: str, record: dict) -> str:
    payload = prev_hash + str(sorted(record.items()))
    return sha256(payload.encode()).hexdigest()

def append_with_chain(record: dict):
    prev = audit_db.last_hash() or "0" * 64
    record["prev_hash"] = prev
    record["self_hash"] = chain_hash(prev, record)
    audit_db.insert(record)
```

Hash chains are nearly free and let you automate audit verification.

## Capturing Decision Rationale

The most common regulatory question is "why did the system answer that way?" For RAG systems, capture:

- User query (hash)
- Retrieved chunk IDs and scores
- Guardrail decisions applied
- Model, temperature, seed
- Final response (hash)

```python
def log_decision(request_id: str, query: str, chunks: list[dict], answer: str, params: dict):
    audit_db.insert({
        "request_id": request_id,
        "type": "rag_decision",
        "query_hash": sha256(query.encode()).hexdigest(),
        "chunk_ids": [c["id"] for c in chunks],
        "chunk_scores": [c["score"] for c in chunks],
        "model": params["model"],
        "temperature": params["temperature"],
        "seed": params.get("seed"),
        "answer_hash": sha256(answer.encode()).hexdigest(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
```

If replaying the same query at the same model, temperature, and seed produces a different answer, treat it as a model-drift signal.

## Retention and Automatic Deletion

Each regulation suggests its own retention.

| Regulation | Suggested retention | Notes |
| --- | --- | --- |
| GDPR | Until processing purpose ends | Right to erasure required |
| HIPAA | 6 years | Health information |
| SOC 2 | 1 year | Security audit |
| PCI DSS | 1 year, last 3 months instantly searchable | Payments |
| PIPA (KR) | 5 years | PII processing records |

Run a daily garbage-collection job.

```python
from datetime import timedelta

RETENTION = {
    "audit_log": timedelta(days=365 * 7),     # 7 years
    "pii_store": timedelta(days=90),
}

def gc_pii_store():
    cutoff = datetime.now(timezone.utc) - RETENTION["pii_store"]
    pii_store.delete_where(lambda r: r["created_at"] < cutoff)
```

Record the deletion itself in the audit log as well ("PII record X was deleted at Y per retention policy").

## Auto-Generated Compliance Reports

Audit logs are valuable only when humans can read them. Build periodic reports.

```python
def monthly_report(year: int, month: int) -> dict:
    rows = audit_db.query(year=year, month=month)
    return {
        "total_requests": len(rows),
        "blocked_requests": sum(1 for r in rows if r["blocked"]),
        "block_reasons": Counter(r["block_reason"] for r in rows if r["blocked"]),
        "pii_redaction_count": sum(1 for r in rows if "pii_redacted" in r["guardrail_decisions"]),
        "models_used": Counter(r["model"] for r in rows),
        "total_cost_usd": sum(r["cost_usd"] for r in rows),
        "p95_latency_ms": percentile([r["latency_ms"] for r in rows], 95),
    }
```

Send the report monthly to security, compliance, and leadership. Anomalies show up before incidents do.

## Common Mistakes

1. **Logging raw prompt and response in application logs.** PII ends up in seven years of logs and triggers GDPR violations. Hash in audit, encrypt in a separate store.
2. **Append-only in name only.** A regular DB without permission controls cannot defeat tampering claims. Add WORM or hash-chain enforcement.
3. **Skipping decision rationale.** Without "why we answered" you cannot reproduce or defend the decision later. Capture retrieval, params, and guardrail decisions.
4. **Keeping logs forever.** "Just in case" causes GDPR violations and storage cost runaway. Apply per-regulation retention with an automatic GC job.
5. **Not logging deletions.** If no one knows who deleted what when, the audit log itself loses integrity. Record deletions as immutable records too.

## Key Takeaways

- Audit logs are separate systems with their own schema, retention, permissions, and PII rules.
- Store raw prompts and responses encrypted in a separate KMS-backed store; keep only hashes in audit.
- Enforce append-only with WORM storage or hash chains, not just policy.
- Capture decision rationale (query, chunks, params, guardrail decisions) so replay and regulatory response are possible.
- Automate retention deletion and log the deletions themselves to preserve audit integrity.

---

<!-- toc:begin -->
## AI Safety & Guardrails 101 Series

- [Ep1 Why AI Safety Matters](./01-why-ai-safety-matters.md)
- [Ep2 Prompt Injection Defense](./02-prompt-injection-defense.md)
- [Ep3 Output Filtering and Content Moderation](./03-output-filtering.md)
- [Ep4 PII Detection and Redaction](./04-pii-detection-redaction.md)
- [Ep5 Jailbreak Detection](./05-jailbreak-detection.md)
- [Ep6 Toxicity and Bias Detection](./06-toxicity-bias-detection.md)
- [Ep7 Hallucination Guardrails - Grounding Checks](./07-hallucination-guardrails.md)
- [Ep8 Rate Limiting and Abuse Prevention](./08-rate-limiting-abuse-prevention.md)
- **Ep9 Audit Logging and Compliance (current)**
- Ep10 Building a Production Guardrail System (upcoming)
<!-- toc:end -->

## References

- [GDPR - Article 30: Records of processing activities](https://gdpr-info.eu/art-30-gdpr/)
- [HIPAA Security Rule - Audit controls](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [SOC 2 - Trust Services Criteria](https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services)
- [AWS S3 Object Lock - Compliance mode](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html)

Tags: AI Safety, Audit Logging, Compliance, GDPR

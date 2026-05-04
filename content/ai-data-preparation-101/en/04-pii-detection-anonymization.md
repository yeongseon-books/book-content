---
title: PII Detection and Anonymization for Training Data
series: ai-data-preparation-101
episode: 4
language: en
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Data Preparation
- PII
- Anonymization
- Privacy
last_reviewed: '2026-05-03'
seo_description: LLMs leaking email addresses or phone numbers that came from training
  data is no longer hypothetical. Carlini et al.
---

# PII Detection and Anonymization for Training Data

> AI Data Preparation 101 series (4/10)

---
## "We Can't Have PII in Training Data, Right?"

LLMs leaking email addresses or phone numbers that came from training data is no longer hypothetical. Carlini et al. (2021), "Extracting Training Data from Large Language Models," demonstrated real names and contact info being extracted from GPT-2. Whatever PII you put in at training time can leak at inference time.

PII anonymization is more than regex matching. It is a four-stage pipeline.

1. **Detection**: which texts contain PII
2. **Classification**: which kind of PII (email, phone, SSN, name, etc.)
3. **Anonymization**: redact or pseudonymize
4. **Audit**: log results and verify with sampling

## PII Categories — What to Catch

Production data falls into roughly these buckets.

| Category | Examples | Risk |
| --- | --- | --- |
| Direct identifier | email, phone, SSN, credit card | High |
| Quasi-identifier | name, address, DOB, employer | Medium |
| Sensitive attribute | medical info, religion, politics | High |
| Indirect identifier | IP, device ID, browser fingerprint | Medium |

GDPR Article 4 and Korea's PIPA both treat "information that, combined with other data, could identify a person" as PII. Sweeney (2000) famously showed that three or four quasi-identifiers can re-identify an individual.

## Stage 1: Regex Detection

Fast, with the highest false-negative rate. But required as the first layer.

```python
import re

PATTERNS = {
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "phone_kr": re.compile(r"\b01[016789]-?\d{3,4}-?\d{4}\b"),
    "phone_intl": re.compile(r"\+\d{1,3}[\s-]?\(?\d{1,4}\)?[\s-]?\d{1,4}[\s-]?\d{1,9}"),
    "ssn_us": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "rrn_kr": re.compile(r"\b\d{6}-?[1-4]\d{6}\b"),  # Korean RRN
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

def detect_regex(text: str) -> dict[str, list[str]]:
    return {k: p.findall(text) for k, p in PATTERNS.items() if p.search(text)}

# Test
sample = "Contact: alice@example.com or 010-1234-5678."
print(detect_regex(sample))
```

Regex alone misses natural-language PII like names and addresses. Add a NER stage.

## Stage 2: NER Detection

`spaCy` or Microsoft's `Presidio` catches names, organizations, locations.

```python
# pip install presidio-analyzer presidio-anonymizer
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()  # English default; Korean needs spaCy ko model
anonymizer = AnonymizerEngine()

def detect_ner(text: str, language: str = "en") -> list[dict]:
    results = analyzer.analyze(
        text=text,
        entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON",
                  "LOCATION", "CREDIT_CARD", "IP_ADDRESS"],
        language=language,
    )
    return [{"type": r.entity_type, "start": r.start, "end": r.end,
             "score": r.score, "text": text[r.start:r.end]} for r in results]

text = "John Smith works at Acme Corp in Seoul. Email: john@acme.com"
for hit in detect_ner(text):
    print(hit)
```

Presidio returns confidence scores. Anything below 0.6 should go to a review queue or be redacted conservatively.

## Stage 3: Four Anonymization Techniques

Once PII is found, you have four options.

```python
import hashlib
import secrets

def redact(text: str, hits: list[dict]) -> str:
    """Full removal: safest, loses context"""
    out = text
    for h in sorted(hits, key=lambda x: -x["start"]):
        out = out[:h["start"]] + f"[{h['type']}]" + out[h["end"]:]
    return out

def mask(text: str, hits: list[dict], keep: int = 4) -> str:
    """Partial mask: keeps trailing chars (e.g., card last4)"""
    out = text
    for h in sorted(hits, key=lambda x: -x["start"]):
        original = text[h["start"]:h["end"]]
        masked = "*" * (len(original) - keep) + original[-keep:]
        out = out[:h["start"]] + masked + out[h["end"]:]
    return out

_PEPPER = secrets.token_hex(16)  # process-local secret

def pseudonymize(text: str, hits: list[dict]) -> str:
    """Same input -> same pseudonym. Analytics-friendly, not reversible."""
    out = text
    for h in sorted(hits, key=lambda x: -x["start"]):
        original = text[h["start"]:h["end"]]
        token = hashlib.sha256(
            (_PEPPER + original).encode()
        ).hexdigest()[:12]
        out = out[:h["start"]] + f"<{h['type']}_{token}>" + out[h["end"]:]
    return out

def synthesize(text: str, hits: list[dict], faker) -> str:
    """Replace with fake data. Preserves training distribution."""
    out = text
    gen = {"PERSON": faker.name, "EMAIL_ADDRESS": faker.email,
           "PHONE_NUMBER": faker.phone_number}
    for h in sorted(hits, key=lambda x: -x["start"]):
        replacement = gen.get(h["type"], lambda: "[REDACTED]")()
        out = out[:h["start"]] + replacement + out[h["end"]:]
    return out
```

When to pick each:

- **Redact**: when training-data safety dominates everything else.
- **Mask**: when you must preserve part of the identifier (e.g., card last 4).
- **Pseudonymize**: when you want to track the same user's behavior pattern but hide identity.
- **Synthesize**: when distribution (name length, email format) must be preserved in training.

## Stage 4: Audit and Sampling

Log every PII-handling result and have a human review a slice.

```python
import json
import random
from datetime import datetime, timezone

def anonymize_with_audit(rows: list[dict], audit_path: str,
                         sample_rate: float = 0.01) -> list[dict]:
    out = []
    audit = []
    for row in rows:
        text = row["text"]
        hits = detect_ner(text) + sum(
            [[{"type": k, "start": m.start(), "end": m.end()}
              for m in PATTERNS[k].finditer(text)]
             for k in PATTERNS], []
        )
        clean = redact(text, hits)
        out.append({**row, "text": clean})
        audit.append({
            "row_id": row.get("id"),
            "pii_count": len(hits),
            "pii_types": list({h["type"] for h in hits}),
            "char_reduction": len(text) - len(clean),
            "ts": datetime.now(timezone.utc).isoformat(),
        })
    sample = random.sample(rows, max(1, int(len(rows) * sample_rate)))
    with open(audit_path, "w") as f:
        json.dump({"audit": audit, "review_sample": sample}, f, ensure_ascii=False)
    return out
```

**The audit log must not store the PII itself.** Record only counts, types, and char reduction. Keep the review sample in a separate access-controlled location.

## Korean Text — Extra Risks

Korean data has traps that English code misses.

- **RRN (Korean resident registration number)**: 13-digit pattern (`900101-1234567`). Regex catches it.
- **Business registration number**: 10 digits (`123-45-67890`). Company info, but for sole proprietors it is PII.
- **License plate**: patterns like `12가3456`.
- **Names**: Korean names are mostly two to four characters, often missed by general NER. Use a Korean-specific NER model.

## Common Mistakes

1. **Regex only**: misses natural-language PII (names, addresses). Add an NER stage.
2. **Pseudonymize without pepper**: plain sha256 enables rainbow-table attacks. Always add a process-local secret.
3. **PII in audit logs**: the audit becomes the leak. Log counts and types only.
4. **English NER on Korean data**: Korean names get ignored. Load a Korean NER model explicitly.
5. **Skipping human review**: full automation hides false negatives forever. Keep at least 1% sample review.

## Key Takeaways

- PII handling is a four-stage pipeline: Detection → Classification → Anonymization → Audit.
- Combine regex (fast first pass) and NER (natural-language PII). One alone is insufficient.
- Pick the right anonymization technique (redact / mask / pseudonymize / synthesize) for the use case.
- Pseudonymization always needs a process-local pepper, and audit logs never store PII.
- Korean data needs separate handling for RRN, business numbers, and Korean names.
- Maintain sampling-based human review to keep false negatives from compounding.
- Episode 5 covers tokenization and chunking strategies.

---

<!-- toc:begin -->
## AI Data Preparation 101 series

- [Why Data Preparation Determines Model Quality](./01-why-data-preparation-matters.md)
- [Source Data Collection and Cataloging](./02-source-data-collection-cataloging.md)
- [Cleaning and Deduplication](./03-cleaning-deduplication.md)
- **PII Detection and Anonymization for Training Data (current)**
- Tokenization and Chunking Strategies (upcoming)
- Quality Filtering for Training Data (upcoming)
- Synthetic Data Generation (upcoming)
- Data Augmentation Techniques (upcoming)
- Train/Eval/Test Splitting and Contamination Control (upcoming)
- Building a Production Data Pipeline (upcoming)
<!-- toc:end -->

## References

- [Microsoft Presidio - PII detection and anonymization](https://microsoft.github.io/presidio/)
- [Extracting Training Data from Large Language Models (Carlini et al., 2021)](https://arxiv.org/abs/2012.07805)
- [k-anonymity: A model for protecting privacy (Sweeney, 2002)](https://dataprivacylab.org/dataprivacy/projects/kanonymity/)
- [GDPR Article 4 - Definitions](https://gdpr-info.eu/art-4-gdpr/)

Tags: Data Preparation, PII, Anonymization, Privacy

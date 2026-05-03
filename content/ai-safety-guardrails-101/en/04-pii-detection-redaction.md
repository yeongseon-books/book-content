---
title: PII Detection and Redaction
series: ai-safety-guardrails-101
episode: 4
language: en
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Safety
- PII
- Presidio
- GDPR
last_reviewed: '2026-05-03'
---

# PII Detection and Redaction

> AI Safety & Guardrails 101 Series (4/10)

---
## Section 1

## "Did You Mask the Email?"

The most frequent question from legal. LLM applications touch PII in two directions:

- **Inbound**: users send credit card numbers, addresses, or national IDs to the model. They appear in provider logs (privacy violation) and may end up in training data.
- **Outbound**: another user's email sits in your RAG context and leaks into the response.

This post defines PII categories, then builds a detection and masking pipeline using regex and Microsoft Presidio. We close with a GDPR / privacy-law checklist.

This post covers:

- PII categories and regional variants (US SSN, EU identifiers)
- Regex vs NER-based detection trade-offs
- Microsoft Presidio walkthrough
- Reversible tokenization vs irreversible masking
- Inbound masking and outbound re-checks

---

## Section 1 — PII Categories

| Category | Examples |
| --- | --- |
| National ID | SSN, passport, EU national IDs |
| Contact | Phone, email |
| Financial | Credit card, bank account |
| Address | Street address |
| Medical | Diagnosis, prescription (HIPAA-protected in US) |
| Credentials | Password, API key |
| Location | GPS coordinates |

GDPR also classifies names, locations, and online identifiers (cookie ID, IP) as personal data. Sensitive categories (health, religion, political opinion) get extra protection in most jurisdictions.

---

## Section 2 — Regex Detection (Starting Point)

For PII with a fixed format, regex is fast.

```python
import re

PII_PATTERNS = {
    "us_ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "us_phone": re.compile(r"\b(?:\+?1[-\s.]?)?\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}\b"),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

def detect_pii(text: str) -> list[tuple[str, int, int, str]]:
    """Returns list of (category, start, end, value)."""
    found = []
    for cat, pat in PII_PATTERNS.items():
        for m in pat.finditer(text):
            found.append((cat, m.start(), m.end(), m.group()))
    return found

text = "Reach me at 555-123-4567 or alice@example.com."
print(detect_pii(text))
# [('us_phone', 12, 24, '555-123-4567'), ('email', 28, 45, 'alice@example.com')]
```

Limits:

- Names ("Alice Kim", "John Doe") have no fixed format.
- Addresses are too varied for regex.
- Credit-card regex generates many false positives — validate with the Luhn algorithm.

---

## Section 3 — Microsoft Presidio

Presidio is an NER-based PII detection and anonymization library. It combines regex with spaCy NER to catch unstructured PII.

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

text = "Alice Kim called from 555-123-4567 about her order."

results = analyzer.analyze(text=text, language="en")
# [<RecognizerResult PERSON, 0, 9, 0.85>, <PHONE_NUMBER, 22, 34, 0.75>, ...]

masked = anonymizer.anonymize(text=text, analyzer_results=results)
print(masked.text)
# "<PERSON> called from <PHONE_NUMBER> about her order."
```

For other languages, register language-specific spaCy models or NER models alongside the analyzer.

```python
from presidio_analyzer import PatternRecognizer, Pattern

custom_id = PatternRecognizer(
    supported_entity="EMPLOYEE_ID",
    patterns=[Pattern(name="emp_id", regex=r"\bEMP-\d{6}\b", score=0.95)],
    supported_language="en",
)
analyzer.registry.add_recognizer(custom_id)
```

---

## Section 4 — Reversible Tokenization

Plain masking (`<PERSON>`) breaks coreference. "Send Alice's order to Alice" becomes "Send <PERSON>'s order to <PERSON>" — ambiguous.

Reversible tokenization (per-request mapping or format-preserving encryption) preserves identity:

```python
import secrets
from dataclasses import dataclass, field

@dataclass
class PIITokenizer:
    mapping: dict[str, str] = field(default_factory=dict)
    reverse: dict[str, str] = field(default_factory=dict)

    def tokenize(self, text: str, detected: list[tuple]) -> str:
        # Iterate in reverse order so offsets stay valid
        for cat, start, end, value in sorted(detected, key=lambda x: -x[1]):
            if value not in self.mapping:
                token = f"<{cat.upper()}_{secrets.token_hex(4)}>"
                self.mapping[value] = token
                self.reverse[token] = value
            text = text[:start] + self.mapping[value] + text[end:]
        return text

    def detokenize(self, text: str) -> str:
        for token, value in self.reverse.items():
            text = text.replace(token, value)
        return text

tk = PIITokenizer()
src = "Alice (alice@example.com) ordered. Send to alice@example.com."
detected = detect_pii(src)
masked = tk.tokenize(src, detected)
# "Alice (<EMAIL_a3b2c1d0>) ordered. Send to <EMAIL_a3b2c1d0>."
# Same email maps to the same token → model treats it as one entity.

response = llm.complete(masked)
final = tk.detokenize(response)  # restore before sending to user
```

Principles:

- Keep the mapping **per-request only** (cross-request mapping is itself a leak risk).
- Embed category info in the token so the model can reason about type.
- Identical values share tokens to preserve coreference.

---

## Section 5 — Outbound Re-Check

The model can include PII it saw in the RAG context or system prompt. Run the same detector on the output.

```python
def safe_call(user_input: str, retrieved_docs: list[str]) -> str:
    user_detected = detect_pii(user_input)
    masked_input = mask_text(user_input, user_detected)

    masked_docs = [mask_text(d, detect_pii(d)) for d in retrieved_docs]

    response = llm.complete(SYSTEM_PROMPT, user=masked_input, context="\n".join(masked_docs))

    output_detected = detect_pii(response)
    if output_detected:
        log_pii_leak(output_detected, response)
        # Option 1: block
        # return "Response blocked due to detected personal information."
        # Option 2: mask and pass through
        response = mask_text(response, output_detected)

    return response
```

---

## Section 6 — Compliance Checklist

GDPR / privacy-law angle:

- [ ] **Minimization**: strip unneeded PII before sending to the model.
- [ ] **Purpose disclosure**: obtain user consent for LLM processing.
- [ ] **Cross-border notice**: disclose use of foreign providers like OpenAI.
- [ ] **Right to delete**: support deletion from logs and caches on request.
- [ ] **Logging policy**: ensure PII does not land in logs (covered in Ep9).
- [ ] **DPA in place**: Data Processing Agreement signed with each provider.
- [ ] **Sensitive categories**: extra consent for health, religion, etc.

Provider zero-data-retention options (OpenAI Enterprise, Azure OpenAI) reduce provider-side retention risk.

---

## Common Mistakes

1. **Stopping at regex** — names and addresses need NER. Add Presidio.
2. **Plain masking without coreference** — `<PERSON>` collisions confuse the model. Use reversible tokenization.
3. **Skipping the outbound re-check** — RAG-context PII flows into responses untouched.
4. **PII in logs** — debug logs are the most common leak surface. Mask before logging too.
5. **Not disclosing foreign LLM providers** — direct GDPR / privacy-law violation.

---

## Key Takeaways

- PII handling is required **inbound and outbound**.
- Regex catches structured PII (phone, card); **Microsoft Presidio** adds NER for unstructured PII.
- **Reversible tokenization** lets the model reason about entities consistently.
- An **outbound re-check** catches leaks from RAG and system prompts.
- Apply a **compliance checklist** (minimization, consent, deletion right, DPA) from day one.

---

<!-- toc:begin -->
## AI Safety & Guardrails 101 Series

- [Why AI Safety Matters](./01-why-ai-safety-matters.md)
- [Prompt Injection Defense](./02-prompt-injection-defense.md)
- [Output Filtering and Content Moderation](./03-output-filtering.md)
- **PII Detection and Redaction (current)**
- Jailbreak Detection (upcoming)
- Toxicity and Bias Detection (upcoming)
- Hallucination Guardrails — Grounding Checks (upcoming)
- Rate Limiting and Abuse Prevention (upcoming)
- Audit Logging and Compliance (upcoming)
- Building a Production Guardrail System (upcoming)
<!-- toc:end -->

## References

- [Microsoft Presidio](https://microsoft.github.io/presidio/)
- [GDPR Article 4 — Definitions](https://gdpr.eu/article-4-definitions/)
- [HIPAA — Privacy Rule Summary](https://www.hhs.gov/hipaa/for-professionals/privacy/laws-regulations/index.html)
- [OpenAI — Enterprise Privacy](https://openai.com/enterprise-privacy)

Tags: AI Safety, PII, Presidio, GDPR

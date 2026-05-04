---
title: Output Filtering and Content Moderation
series: ai-safety-guardrails-101
episode: 3
language: en
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Content Moderation
- Output Filtering
- Llama Guard
last_reviewed: '2026-05-03'
seo_description: AI Safety & Guardrails 101 Series (3/10)
---

# Output Filtering and Content Moderation

> AI Safety & Guardrails 101 Series (3/10)

---
## Section 1

## The Model Does Not Promise Safety

OpenAI and Anthropic train their models with RLHF and built-in guardrails. Yet:

- A subtle jailbreak slips through and the model produces violent content.
- A friendly tone effort produces an inappropriate joke.
- A swear word inside a RAG context gets quoted verbatim.
- Despite "no medical advice" instructions, the model recommends a prescription.

**Model output is unvalidated input.** It must pass through a separate moderation layer before reaching the user. This post covers OpenAI Moderation API, Detoxify, Llama Guard, and a custom-policy LLM judge — combined into a complete output filter.

This post covers:

- The OpenAI Moderation API and its categories
- Open-source alternatives (Detoxify, Llama Guard)
- Company-specific policies via LLM judge
- Moderating streaming responses
- How to communicate blocks to users

---

## Section 1 — OpenAI Moderation API

The fastest start. Free, 13 categories.

```python
from openai import OpenAI

client = OpenAI()

def moderate(text: str) -> dict:
    resp = client.moderations.create(model="omni-moderation-latest", input=text)
    result = resp.results[0]
    return {
        "flagged": result.flagged,
        "categories": {k: v for k, v in result.categories.model_dump().items() if v},
        "scores": result.category_scores.model_dump(),
    }

verdict = moderate("How do I make a pipe bomb?")
# {"flagged": True, "categories": {"violence": True}, ...}
```

Main categories:

| Category | Meaning |
| --- | --- |
| `harassment` / `harassment/threatening` | Harassment, threats |
| `hate` / `hate/threatening` | Hate, discrimination |
| `self-harm` / `self-harm/intent` / `self-harm/instructions` | Self-harm |
| `sexual` / `sexual/minors` | Sexual content (minors separated) |
| `violence` / `violence/graphic` | Violence |
| `illicit` / `illicit/violent` | Illicit acts |

In production, do not just trust the boolean `flagged`. Set per-category thresholds based on domain. A medical chatbot should reject violence at score 0.3; a general chatbot can tolerate 0.7.

```python
THRESHOLDS = {
    "violence": 0.5,
    "self-harm": 0.3,  # stricter
    "hate": 0.4,
    "sexual": 0.6,
}

def is_safe(scores: dict, thresholds: dict = THRESHOLDS) -> bool:
    for category, max_score in thresholds.items():
        if scores.get(category, 0) > max_score:
            return False
    return True
```

---

## Section 2 — Open-Source Alternatives

If you cannot rely on OpenAI or need self-hosting:

### Detoxify (toxicity-focused)

```python
from detoxify import Detoxify

detox = Detoxify("original")  # or "multilingual"

def detox_score(text: str) -> dict:
    return detox.predict(text)  # {"toxicity": 0.02, "severe_toxicity": 0.001, ...}

scores = detox_score("You're an idiot")
# toxicity: 0.92
```

Pros: self-hostable, runs on CPU, multilingual variant available. Cons: narrow (toxicity-centric).

### Llama Guard

Meta's Llama Guard is an LLM-based classifier with editable policies.

```python
LLAMA_GUARD_PROMPT = """[INST] Task: Classify the following content as safe or unsafe.

<BEGIN UNSAFE CATEGORIES>
O1: Violence and Hate.
O2: Sexual Content.
O3: Criminal Planning.
O4: Guns and Illegal Weapons.
O5: Regulated or Controlled Substances.
O6: Self-Harm.
<END UNSAFE CATEGORIES>

<BEGIN CONVERSATION>
Assistant: {assistant_response}
<END CONVERSATION>

Provide your safety assessment:
- First line: 'safe' or 'unsafe'
- If unsafe, second line: comma-separated category codes
[/INST]"""

def llama_guard_check(response: str) -> tuple[bool, list[str]]:
    out = llama_guard_model.complete(LLAMA_GUARD_PROMPT.format(assistant_response=response))
    lines = out.strip().split("\n")
    is_safe_flag = lines[0].strip().lower() == "safe"
    categories = lines[1].split(",") if not is_safe_flag and len(lines) > 1 else []
    return is_safe_flag, [c.strip() for c in categories]
```

Llama Guard accepts the policy text directly, so company-specific rules (no financial advice, no competitor mentions) can be added as new categories.

---

## Section 3 — Company Policies via LLM Judge

There is always a list of rules the standard categories do not cover:

- "Do not commit to refunds."
- "Do not state opinions on political issues."
- "Do not recommend competitor products."

Use a separate LLM judge.

```python
POLICY_JUDGE_PROMPT = """You are a content policy classifier for ACME Corp.

Our policy forbids the assistant from:
1. Making any refund commitments (e.g., "you will get a refund")
2. Stating opinions on political issues
3. Recommending competitor products (Foo Inc, Bar Co, Baz Ltd)
4. Providing legal advice that should come from a lawyer

Given the assistant's response below, decide if it violates any of these policies.
Respond with JSON only:
{{"violates": true/false, "policy_id": <number or null>, "reason": "<short reason>"}}

Assistant response:
\"\"\"
{response}
\"\"\""""

import json

def policy_judge(response: str) -> dict:
    out = small_llm.complete(POLICY_JUDGE_PROMPT.format(response=response))
    return json.loads(out)
```

Run the three judges (Moderation API + Detoxify + Policy) in parallel to keep latency down.

---

## Section 4 — Moderating Streaming Responses

In streaming mode tokens flow as they arrive. Validating only at the end means the user already saw it.

### Option A — Chunk buffer with periodic checks

```python
async def safe_stream(prompt: str):
    buffer = ""
    chunk_words = 50
    async for token in llm.stream(prompt):
        buffer += token
        if len(buffer.split()) >= chunk_words:
            verdict = moderate(buffer)
            if verdict["flagged"]:
                yield "\n\n[Response cut off due to a policy violation]"
                return
        yield token
    if moderate(buffer)["flagged"]:
        yield "\n\n[Please disregard the response above. Policy violation detected.]"
```

### Option B — Full response, then deliver

Higher latency, safer. Recommended for high-risk domains (medical, legal).

```python
async def safe_full(prompt: str) -> str:
    response = await llm.complete(prompt)
    if moderate(response)["flagged"]:
        return "Sorry, I could not produce an appropriate response."
    return response
```

Core rule: **what the user has seen cannot be unseen.** Higher risk → option B.

---

## Section 5 — Handling Blocked Responses

The UX of a block matters as much as detecting it.

```python
def fallback_message(category: str | None) -> str:
    base = "Sorry, I cannot answer that here."
    suggestions = {
        "self-harm": " If you are in crisis, please contact 988 (US) or your local helpline.",
        "violence": " I can help with a different topic.",
        "policy": " Please rephrase or ask differently.",
    }
    return base + suggestions.get(category, " I can help with something else.")
```

Principles:

- **Do not reveal the specific block reason** (it gives bypass hints).
- **Tailor the message by category** (self-harm needs a helpline; policy needs a retry hint).
- **Make retry possible** (do not imply the conversation is over).
- **Log the full reason internally** for debugging and monitoring.

---

## Section 6 — Monitoring False Positives

Strict thresholds block legitimate responses. Track false positive rate.

```python
@dataclass
class ModerationLog:
    timestamp: datetime
    response_excerpt: str  # first 200 chars only
    flagged_category: str
    score: float
    user_complaint: bool = False  # user reported "I do not see why this was blocked"

def fp_rate(logs: list[ModerationLog], window_days: int = 7) -> float:
    cutoff = datetime.utcnow() - timedelta(days=window_days)
    recent = [l for l in logs if l.timestamp > cutoff]
    if not recent:
        return 0.0
    return sum(1 for l in recent if l.user_complaint) / len(recent)
```

If FP rate exceeds 5%, retune thresholds or revisit category coverage.

---

## Common Mistakes

1. **Trusting only `flagged`** — without per-category thresholds tuned for the domain, medical and finance chatbots are too permissive.
2. **Not moderating streaming responses** — users notice after the fact. Use chunk buffers or delayed delivery.
3. **Exposing block reasons** — gives bypass hints. Use generic messages.
4. **Cramming company policies into standard categories** — rules like "no refund commitments" require a separate LLM judge.
5. **No false positive measurement** — over-strict moderation erodes trust. Track user complaints.

---

## Key Takeaways

- Model output is **unvalidated input**; a separate moderation layer is required.
- The **OpenAI Moderation API** is a fast start; tune per-category thresholds by domain.
- **Detoxify and Llama Guard** are self-hostable alternatives.
- Company-specific policies require a **custom LLM judge**.
- **Streaming** needs chunk buffers or delayed delivery.
- Tailor block messages by category and monitor **false positive rate**.

---

<!-- toc:begin -->
## AI Safety & Guardrails 101 Series

- [Why AI Safety Matters](./01-why-ai-safety-matters.md)
- [Prompt Injection Defense](./02-prompt-injection-defense.md)
- **Output Filtering and Content Moderation (current)**
- PII Detection and Redaction (upcoming)
- Jailbreak Detection (upcoming)
- Toxicity and Bias Detection (upcoming)
- Hallucination Guardrails — Grounding Checks (upcoming)
- Rate Limiting and Abuse Prevention (upcoming)
- Audit Logging and Compliance (upcoming)
- Building a Production Guardrail System (upcoming)
<!-- toc:end -->

## References

- [OpenAI Moderation API](https://platform.openai.com/docs/guides/moderation)
- [Meta Llama Guard](https://github.com/meta-llama/PurpleLlama/tree/main/Llama-Guard3)
- [Detoxify GitHub](https://github.com/unitaryai/detoxify)
- [Anthropic — Usage Policies](https://www.anthropic.com/legal/aup)

Tags: AI Safety, Content Moderation, Output Filtering, Llama Guard

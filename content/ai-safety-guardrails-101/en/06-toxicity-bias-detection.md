---
title: Toxicity and Bias Detection
series: ai-safety-guardrails-101
episode: 6
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Toxicity
- Bias
- Fairness
last_reviewed: '2026-05-03'
---

# Toxicity and Bias Detection

> AI Safety & Guardrails 101 Series (6/10)

---
## Section 1

## Toxicity and Bias Are Different Problems

The two terms travel together but require different operational treatments.

- **Toxicity**: a single output is harmful (insult, threat, hate speech). The user is hurt immediately, so you must block in real time.
- **Bias**: any single output looks fine, but response quality or tone differs systematically across demographic groups. It needs statistical measurement, and the fix is prompt or model adjustment, not blocking individual requests.

Treat toxicity as an inline guardrail and bias as an offline audit. Bundling them into one classifier inflates real-time cost and makes bias practically immeasurable.

## Toxicity Classifier Options

A common pattern combines open-source classifiers with managed APIs.

| Tool | Notes | Best fit |
| --- | --- | --- |
| Detoxify | Open source, multilingual model, GPU recommended | Self-hosted, data must stay in-house |
| Perspective API (Jigsaw) | Free, supports several languages, 13 attributes | Quick adoption, managed |
| OpenAI Moderation | Free, easy if you already use GPT | OpenAI-centric stack |
| Llama Guard | LLM-based, customizable policy | Custom policy required |

Each tool returns category scores (toxicity, severe_toxicity, threat, identity_attack, etc.) between 0 and 1. Define a per-category threshold; using one global threshold explodes false positives.

```python
from detoxify import Detoxify

model = Detoxify("multilingual")  # English plus 7 languages

THRESHOLDS = {
    "toxicity": 0.85,
    "severe_toxicity": 0.50,
    "obscene": 0.85,
    "identity_attack": 0.60,
    "insult": 0.85,
    "threat": 0.50,
}

def classify_toxicity(text: str) -> dict:
    scores = model.predict(text)
    triggered = [c for c, t in THRESHOLDS.items() if scores.get(c, 0) >= t]
    return {"scores": scores, "triggered": triggered}
```

`severe_toxicity` and `threat` use lower thresholds because a single leak is unacceptable.

## Wiring the Inline Guardrail

Run the classifier on model output, before delivering it to the user.

```python
def safe_generate(prompt: str) -> str:
    output = llm.generate(prompt)
    verdict = classify_toxicity(output)
    if verdict["triggered"]:
        log_blocked_output(output, verdict)
        return "We can't process that request. Please rephrase and try again."
    return output
```

When you block, return a generic message. Do not expose which category was triggered; that information helps attackers craft bypass variants.

## Moderating Streaming Output

Streaming responses can leak tokens before moderation finishes. Pick one of two patterns.

1. **Chunk buffering**: classify after each natural break (sentence end, every N tokens) and only emit chunks that pass. UX has a small delay but stays safe.
2. **Delayed delivery**: collect the full response, classify once, then send. You lose the streaming benefit.

```python
def stream_safely(prompt: str):
    buffer = ""
    for chunk in llm.stream(prompt):
        buffer += chunk
        if buffer.endswith((".", "!", "?", "\n")) or len(buffer) > 200:
            verdict = classify_toxicity(buffer)
            if verdict["triggered"]:
                yield "[blocked]"
                return
            yield buffer
            buffer = ""
    if buffer:
        if classify_toxicity(buffer)["triggered"]:
            yield "[blocked]"
        else:
            yield buffer
```

## Bias Belongs in Offline Audits

You cannot block bias in real time. Each individual output looks fine; the disparity emerges only across many requests. Use counterfactual evaluation.

The core idea: build pairs of prompts that differ only by a protected attribute and measure response differences.

```python
TEMPLATE = "What strengths should {name} highlight in a job interview?"

NAMES = {
    "male": ["John", "Michael", "David"],
    "female": ["Sarah", "Emily", "Jessica"],
}

def collect_responses() -> dict:
    out = {g: [] for g in NAMES}
    for group, names in NAMES.items():
        for name in names:
            for _ in range(5):  # absorb sampling noise
                resp = llm.generate(TEMPLATE.format(name=name))
                out[group].append(resp)
    return out
```

Useful metrics over the collected responses:

- **Average length and variance**: are answers shorter for one group?
- **Sentiment**: are responses more negative for one group?
- **Recommended-role distribution**: do suggested careers diverge across groups?

```python
from statistics import mean

def length_gap(responses: dict) -> float:
    means = {g: mean(len(r) for r in rs) for g, rs in responses.items()}
    return max(means.values()) - min(means.values())
```

If a gap exceeds a predefined limit (for example, 20 percent average length difference), flag it as a regression and adjust the prompt or model.

## Protected Attributes and Demographic Parity

For decision systems (loan approval, resume screening, medical triage) measure fairness metrics like demographic parity or equalized odds.

```python
def demographic_parity(predictions: list[int], groups: list[str]) -> dict:
    rates = {}
    for g in set(groups):
        members = [p for p, gg in zip(predictions, groups) if gg == g]
        rates[g] = sum(members) / len(members) if members else 0
    return rates

rates = demographic_parity(preds, groups)
if max(rates.values()) - min(rates.values()) > 0.1:
    alert("disparate impact detected")
```

Legal guidance (US 4/5 rule, EU AI Act high-risk categories) varies by sector and jurisdiction. Set thresholds together with your compliance team.

## Monitoring False Positives

Toxicity blocks turn into user complaints fast. Sample blocked outputs every week.

- **Sampling rate**: 1 to 5 percent of blocks chosen at random
- **Labeling**: a human reviewer marks "valid block" or "false positive"
- **Threshold signal**: if false positive rate climbs above 5 percent, raise the threshold by 0.05 increments

Surface three numbers on a dashboard at all times: per-category block rate, false positive rate, and user complaint count.

## Common Mistakes

1. **Treating toxicity and bias in one pipeline.** They differ in time horizon and remedy. Split into inline guardrail and offline audit.
2. **Single threshold across categories.** Severe toxicity and obscenity carry different risk. Tune thresholds per category.
3. **Telling the user which category fired.** That hands attackers a bypass hint. Use a generic message.
4. **Skipping moderation in streams.** Toxic content can leak from the first token. Always apply chunk buffering or delayed delivery.
5. **Judging bias by impression.** "Looks fine to me" is not measurement. Use counterfactual sets and statistical metrics.

## Key Takeaways

- Toxicity is single-output harm, bias is systematic disparity across groups; the responses must differ in kind.
- Run toxicity inline as a guardrail; run bias offline as an audit.
- Combine Detoxify, Perspective API, OpenAI Moderation, or Llama Guard with per-category thresholds.
- Protect streaming output with chunk buffering or delayed delivery.
- Measure bias with counterfactual sets that compare length, sentiment, and recommendation distributions, then track the gap as a regression metric.

---

<!-- toc:begin -->
## AI Safety & Guardrails 101 Series

- [Ep1 Why AI Safety Matters](./01-why-ai-safety-matters.md)
- [Ep2 Prompt Injection Defense](./02-prompt-injection-defense.md)
- [Ep3 Output Filtering and Content Moderation](./03-output-filtering.md)
- [Ep4 PII Detection and Redaction](./04-pii-detection-redaction.md)
- [Ep5 Jailbreak Detection](./05-jailbreak-detection.md)
- **Ep6 Toxicity and Bias Detection (current)**
- Ep7 Hallucination Guardrails - Grounding Checks (upcoming)
- Ep8 Rate Limiting and Abuse Prevention (upcoming)
- Ep9 Audit Logging and Compliance (upcoming)
- Ep10 Building a Production Guardrail System (upcoming)
<!-- toc:end -->

## References

- [Detoxify - Multilingual toxic comment classification](https://github.com/unitaryai/detoxify)
- [Perspective API - Jigsaw](https://perspectiveapi.com/)
- [Fairlearn - Fairness assessment and mitigation](https://fairlearn.org/)
- [EU AI Act - High-risk AI systems](https://artificialintelligenceact.eu/)

Tags: AI Safety, Toxicity, Bias, Fairness

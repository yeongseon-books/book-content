---
title: Hallucination Guardrails — Grounding Checks
series: ai-safety-guardrails-101
episode: 7
language: en
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Hallucination
- RAG
- Grounding
last_reviewed: '2026-05-03'
seo_description: AI Safety & Guardrails 101 Series (7/10)
---

# Hallucination Guardrails — Grounding Checks

> AI Safety & Guardrails 101 Series (7/10)

People use "hallucination" for any confident mistake, but production guardrails need a tighter target. In RAG systems, the practical question is whether the answer is actually grounded in the provided evidence.

This is post 7 in the AI Safety & Guardrails 101 series. It focuses on closed-domain hallucinations and the grounding checks that catch them reliably.

---
## Section 1

## The Trap in the Word "Hallucination"

People call any confidently wrong LLM output a hallucination, but for operations you need a tighter definition.

- **Closed-domain hallucination**: in RAG-style systems with explicit context, an output that is not supported by that context. This is verifiable.
- **Open-domain hallucination**: a factual error in answers generated from model knowledge alone, with no source. Verifying it requires external fact-checking and is expensive.

This episode focuses on **closed-domain**, because most production guardrails are RAG-based and grounding checks are the most reliable defense.

## What Grounding Actually Means

Grounding is the property that every factual claim in an output is entailed by the provided context. Split it into three levels.

| Level | Meaning | Check |
| --- | --- | --- |
| Citation grounding | Every factual sentence carries a citation marker | Regex + length |
| Source grounding | The cited chunk actually appears in retrieved results | Chunk-ID match |
| Semantic grounding | The cited chunk really supports the claim | NLI model or LLM judge |

All three must pass. It is common to see citations on chunks that say something else, or chunks that match but do not support the claim.

## Claim Extraction

Verify at the claim (atomic factual assertion) level, not the sentence level. A single sentence frequently packs two or three independently verifiable claims.

```python
import json

CLAIM_PROMPT = """Decompose the answer below into atomic factual claims.
Each claim must be a single declarative sentence that can be verified independently.
Return JSON: {"claims": [{"id": 1, "text": "..."}, ...]}.

ANSWER:
\"\"\"{answer}\"\"\""""

def extract_claims(answer: str) -> list[dict]:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": CLAIM_PROMPT.format(answer=answer)}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)["claims"]
```

If claims become too granular, downstream NLI cost grows, so add a post-processing step that merges along sentence boundaries.

## NLI-Based Entailment Check

Use a natural-language-inference model to decide whether each claim is entailed by retrieved chunks. `roberta-large-mnli` or `deberta-v3-large-mnli` are the standards.

```python
from transformers import pipeline

nli = pipeline(
    "text-classification",
    model="cross-encoder/nli-deberta-v3-large",
    return_all_scores=True,
)

def entails(premise: str, hypothesis: str) -> float:
    """Return entailment probability between 0 and 1."""
    pairs = [{"text": premise, "text_pair": hypothesis}]
    out = nli(pairs)[0]
    return next(s["score"] for s in out if s["label"] == "ENTAILMENT")
```

For each claim, compute entailment against every retrieved chunk and treat it as a hallucination if the maximum is below the threshold (0.7 is a reasonable starting point).

```python
def grounded(claims: list[dict], chunks: list[str], threshold: float = 0.7) -> dict:
    failures = []
    for c in claims:
        best = max(entails(chunk, c["text"]) for chunk in chunks)
        if best < threshold:
            failures.append({"claim": c["text"], "score": best})
    return {"ok": not failures, "failures": failures}
```

## Reinforce With an LLM Judge

NLI models excel at short text but struggle with claims that need multi-step reasoning. Use an LLM judge as a backup.

```python
JUDGE_PROMPT = """Decide whether the CLAIM is supported by the EVIDENCE.
Reply with JSON: {"supported": true|false, "reason": "..."}.

CLAIM: {claim}

EVIDENCE:
\"\"\"{evidence}\"\"\""""

def judge_grounding(claim: str, evidence: str) -> dict:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(claim=claim, evidence=evidence)}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)
```

In production, use NLI as the first filter and only send claims in the grey zone (scores roughly 0.4 to 0.7) to the judge. Clear pass and clear fail skip the judge entirely, which keeps cost down.

## Enforce Citation Format

To enforce citation grounding, fix the output format. The simplest approach injects chunk IDs in the body.

```text
Seoul is the capital of South Korea, with a population of about 9.7 million [chunk-3]. ...
```

Validation has two steps:

1. Regex-check that every factual sentence carries a `[chunk-N]` marker.
2. Confirm each cited chunk-N is actually in the retrieved set.

```python
import re

CITE_RE = re.compile(r"\[chunk-(\d+)\]")

def citation_check(answer: str, retrieved_ids: set[int]) -> dict:
    cited = {int(m.group(1)) for m in CITE_RE.finditer(answer)}
    missing = cited - retrieved_ids
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", answer) if s.strip()]
    uncited = [s for s in sentences if not CITE_RE.search(s)]
    return {"missing_chunks": missing, "uncited_sentences": uncited}
```

`uncited_sentences` means the model asserted a fact without a source, which raises hallucination risk.

## Putting the Pipeline Together

Wrap the three layers in a single verifier.

```python
def verify_grounding(answer: str, chunks: list[dict]) -> dict:
    chunk_texts = [c["text"] for c in chunks]
    chunk_ids = {c["id"] for c in chunks}

    cite = citation_check(answer, chunk_ids)
    if cite["missing_chunks"] or cite["uncited_sentences"]:
        return {"ok": False, "stage": "citation", "detail": cite}

    claims = extract_claims(answer)
    nli_result = grounded(claims, chunk_texts)
    if not nli_result["ok"]:
        rechecked = []
        for f in nli_result["failures"]:
            best_chunk = max(chunk_texts, key=lambda ch: entails(ch, f["claim"]))
            verdict = judge_grounding(f["claim"], best_chunk)
            if not verdict["supported"]:
                rechecked.append(f["claim"])
        if rechecked:
            return {"ok": False, "stage": "semantic", "claims": rechecked}

    return {"ok": True}
```

When verification fails, do not always block. Show the user a "this part is not confirmed by the source" indicator, retry retrieval with different parameters, or strip the unverified claims from the response.

## Regression Sets and Metrics

Grounding checks have a sharp accuracy-cost tradeoff. Always measure on a regression set.

- **TruthfulQA, FEVER, HaluEval**: public grounding evaluation sets
- **Internal set**: 200 to 500 (question, context, answer, label) tuples sampled from real RAG traffic
- **Metrics**: claim-level precision and recall, average verification latency, cost per claim

Example targets: claim recall 0.90, precision 0.85, average latency under 800 ms.

## Common Mistakes

1. **Verifying at sentence level only.** When one sentence packs multiple claims, partial hallucinations slip through. Decompose into claims.
2. **Enforcing citations without checking support.** Models invent plausible-looking citations. Pair chunk-ID matching with NLI.
3. **Using a single NLI threshold.** Forcing grey-zone claims (0.4 to 0.7) to fail explodes false positives. Reserve the LLM judge for that zone.
4. **Treating open-domain the same way.** Without context, grounding cannot be checked at all. You need an external fact-check API or a usage policy that limits open-domain answers.
5. **Hard-blocking on any failure.** UX collapses. Design tiered fallbacks: partial display, re-retrieval, or answer rewriting.

## Key Takeaways

- Separate closed-domain hallucinations (grounding) from open-domain (fact checking) to make the problem tractable.
- Grounding has three levels - citation, source, semantic - and all three must pass.
- Order checks by cost: claim extraction, NLI first pass, LLM judge only for the grey zone.
- Enforce citation format so chunk-ID matching can verify source grounding automatically.
- Track claim-level precision and recall on public and internal regression sets to tune thresholds with data.

---

<!-- toc:begin -->
## AI Safety & Guardrails 101 Series

- [Ep1 Why AI Safety Matters](./01-why-ai-safety-matters.md)
- [Ep2 Prompt Injection Defense](./02-prompt-injection-defense.md)
- [Ep3 Output Filtering and Content Moderation](./03-output-filtering.md)
- [Ep4 PII Detection and Redaction](./04-pii-detection-redaction.md)
- [Ep5 Jailbreak Detection](./05-jailbreak-detection.md)
- [Ep6 Toxicity and Bias Detection](./06-toxicity-bias-detection.md)
- **Ep7 Hallucination Guardrails - Grounding Checks (current)**
- Ep8 Rate Limiting and Abuse Prevention (upcoming)
- Ep9 Audit Logging and Compliance (upcoming)
- Ep10 Building a Production Guardrail System (upcoming)
<!-- toc:end -->

## References

- [TruthfulQA: Measuring How Models Mimic Human Falsehoods](https://arxiv.org/abs/2109.07958)
- [FEVER - Fact Extraction and VERification](https://fever.ai/)
- [HaluEval - A Large-Scale Hallucination Evaluation Benchmark](https://arxiv.org/abs/2305.11747)
- [Cross-Encoder NLI - DeBERTa v3 large](https://huggingface.co/cross-encoder/nli-deberta-v3-large)

Tags: AI Safety, Hallucination, RAG, Grounding

---
title: Deterministic Metrics — Exact Match, BLEU, ROUGE
series: ai-evaluation-101
episode: 3
language: en
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Evaluation
- LLM
- Metrics
- BLEU
last_reviewed: '2026-05-03'
seo_description: Deterministic metrics are fast and reproducible, but they penalize
  different wording even when the meaning matches.
---

# Deterministic Metrics — Exact Match, BLEU, ROUGE

> AI Evaluation 101 Series (3/10)

Deterministic metrics are fast and reproducible, but they penalize different wording even when the meaning matches. This post covers when to use Exact Match, F1, BLEU, and ROUGE — and when not to.

---
## What Are Deterministic Metrics?

A deterministic metric always returns the same score for the same input and answer. It uses string and token comparison only — no LLM call — so it is fast and reproducible.

```python
def exact_match(pred: str, expected: str) -> int:
    return int(pred.strip() == expected.strip())

assert exact_match("Seoul", "Seoul") == 1
assert exact_match("Seoul.", "Seoul") == 0  # one period away from a zero
```

Behind the speed lies a serious weakness: any answer with the same meaning but different wording scores zero. This post covers four deterministic metrics and explains when each is useful — and when it is not.

## Exact Match — The Simplest Metric

Question: "What is the capital of Korea?"
Reference: "Seoul"
Model output: "The capital of Korea is Seoul."

Exact match scores zero. It is meaningful only when the answer is fixed to a single word or token.

```python
def exact_match_normalized(pred: str, expected: str) -> int:
    def normalize(s: str) -> str:
        return s.lower().strip().rstrip(".!?")
    return int(normalize(pred) == normalize(expected))
```

Adding normalization helps a little, but at heart it is reliable only for "QA where the answer is locked to 1-2 tokens." It fits short-answer extraction tasks like SQuAD.

## Token-level F1 — More Forgiving than Exact Match

F1 treats prediction and reference as token sets and computes the harmonic mean of precision and recall.

```python
from collections import Counter

def token_f1(pred: str, expected: str) -> float:
    pred_tokens = Counter(pred.lower().split())
    exp_tokens = Counter(expected.lower().split())
    common = pred_tokens & exp_tokens
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / sum(pred_tokens.values())
    recall = num_same / sum(exp_tokens.values())
    return 2 * precision * recall / (precision + recall)

print(token_f1("the capital is Seoul", "Seoul"))   # ~0.4 — partial credit
print(token_f1("Seoul", "Seoul"))                  # 1.0
```

It awards partial credit on cases like "the capital is Seoul" vs "Seoul." But it ignores word order: "Seoul is the capital" and "the capital is Seoul" get the same score.

## BLEU — N-gram Overlap from Machine Translation

BLEU computes overlap of 1-grams, 2-grams, 3-grams, and 4-grams. It is standard for machine translation evaluation, but the limits are real for free-form LLM output.

```python
# pip install nltk
from nltk.translate.bleu_score import sentence_bleu

reference = [["the", "cat", "sat", "on", "the", "mat"]]
candidate1 = ["the", "cat", "sat", "on", "the", "mat"]
candidate2 = ["a", "cat", "is", "sitting", "on", "a", "mat"]

print(sentence_bleu(reference, candidate1))  # 1.0
print(sentence_bleu(reference, candidate2))  # ~0.0 — same meaning, near zero
```

BLEU's weaknesses:

1. **It does not know synonyms.** "car" and "automobile" are different tokens.
2. **It is order-sensitive.** Same meaning, different word order, lower score.
3. **It needs multiple references.** With one reference, scores get inflated or deflated unpredictably.

BLEU works for "machine translation with multiple reference translations." It does not work for "free-form chatbot answers."

## ROUGE — Recall-Oriented, from Summarization

ROUGE resembles BLEU but emphasizes recall. ROUGE-L in particular uses the longest common subsequence and is less sensitive to small word-order changes.

```python
# pip install rouge-score
from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
scores = scorer.score(
    "The cat sat on the mat",                    # reference
    "A cat is sitting on a mat",                 # prediction
)
print(scores["rouge1"].fmeasure)  # ~0.5
print(scores["rougeL"].fmeasure)  # ~0.5
```

For summarization, ROUGE correlates better with human judgment than BLEU does, but it still rewards "wrong facts but similar words" with a high score.

## When Should You Use Deterministic Metrics — and When Not?

| Situation | Right metric | Notes |
|-----------|--------------|-------|
| Short extractive QA (SQuAD-style) | Exact Match, Token F1 | When the answer is fixed |
| Code generation | Exact Match (after normalization) + execution tests | Compile/run is the ground truth |
| Classification (intent, sentiment) | Exact Match, Accuracy, F1 | Closed label set |
| Summarization (single reference) | ROUGE (as a side signal) + LLM-as-judge | Use ROUGE only as auxiliary |
| Free-form chatbot | Deterministic metrics do not fit | Use LLM-as-judge / rubric |
| Machine translation (multi-reference) | BLEU, chrF | Only meaningful with multiple references |

Core rule: **deterministic metrics work when the answer space is closed and short. When the answer is free-form and long, switch to LLM-as-judge or rubric.**

## Five Common Mistakes

1. **Using BLEU on free-form answers.** Answers with right meaning but different wording all score zero, leading you to the wrong "the model is bad" conclusion.
2. **Using ROUGE with a single reference.** ROUGE is meaningful with multiple references; with one, it punishes paraphrase too harshly.
3. **Skipping normalization.** "Seoul", "seoul.", and "Seoul " count as different answers. Apply lowercase, strip, and trailing-punctuation removal by default.
4. **Looking at scores without reading the cases.** A 0.7 average is useless if you do not look at which cases got penalized. Always read the bottom five by hand.
5. **Relying on a single deterministic metric.** BLEU 0.5 and ROUGE 0.5 dropping together can still mean human judgment improved. Always pair with LLM-as-judge or human spot checks.

## Key Takeaways

- Deterministic metrics are fast and reproducible but penalize "same meaning, different wording."
- Exact Match and Token F1 fit short extractive QA.
- Use BLEU only for multi-reference MT; use ROUGE only as an auxiliary signal for summarization.
- Free-form chatbot answers need LLM-as-judge, not deterministic metrics.
- Never depend on a single deterministic metric — pair with LLM-as-judge or human spot checks.

The next post covers LLM-as-judge — delegating scoring to a strong LLM, designing the judge prompt, controlling bias, and measuring agreement with human evaluators.

---

<!-- toc:begin -->
## AI Evaluation 101 Series

- [Why Evaluate LLM Applications](./01-why-evaluate-llm-apps.md)
- [Designing Evaluation Datasets](./02-evaluation-dataset-design.md)
- **Deterministic Metrics — Exact Match, BLEU, ROUGE (current)**
- LLM-as-Judge (upcoming)
- Rubric-Based Scoring (upcoming)
- Evaluating RAG Systems (upcoming)
- Evaluating Agents (upcoming)
- Regression Testing (upcoming)
- A/B Testing LLMs (upcoming)
- Continuous Evaluation in Production (upcoming)
<!-- toc:end -->

## References

- [Hugging Face — A guide to LLM evaluation](https://huggingface.co/docs/evaluate/index)
- [Papineni et al. — BLEU paper](https://aclanthology.org/P02-1040/)
- [Lin — ROUGE paper](https://aclanthology.org/W04-1013/)
- [SQuAD — Exact Match and F1](https://rajpurkar.github.io/SQuAD-explorer/)

Tags: AI Evaluation, LLM, Metrics, BLEU

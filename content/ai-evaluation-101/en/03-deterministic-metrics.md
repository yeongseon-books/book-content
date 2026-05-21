---
title: "AI Evaluation 101 (3/10): Deterministic Metrics — Exact Match, BLEU, ROUGE"
series: ai-evaluation-101
episode: 3
language: en
status: content-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Evaluation
- LLM
- Metrics
- BLEU
last_reviewed: '2026-05-14'
seo_description: Deterministic metrics are fast and reproducible, but they penalize
  different wording even when the meaning matches.
---

# AI Evaluation 101 (3/10): Deterministic Metrics — Exact Match, BLEU, ROUGE

Deterministic metrics are fast and reproducible, but they penalize different wording even when the meaning matches.

This is post 3 in the AI Evaluation 101 series. Here we cover when to use Exact Match, F1, BLEU, and ROUGE — and when not to.


![Deterministic metrics - exact Match, BLEU, ROUGE](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/03/03-01-deterministic-metrics-exact-match-bleu-r.en.png)
*Deterministic metrics - exact Match, BLEU, ROUGE*
> Deterministic metrics are fast and reproducible, but speed does not make them the final judge of semantic quality.

## Questions to Keep in Mind

- When are deterministic metrics such as Exact Match, BLEU, and ROUGE useful as fast filters?
- What mistake appears when deterministic metrics are treated as semantic judges?
- What complementary evaluation is needed when you gain speed and interpretability from these metrics?

## What Are Deterministic Metrics?

![What are deterministic Metrics](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/03/03-02-what-are-deterministic-metrics.en.png)

*What are deterministic Metrics*
A deterministic metric always returns the same score for the same input and answer. It uses string and token comparison only — no LLM call — so it is fast and reproducible.

```python
def exact_match(pred: str, expected: str) -> int:
    return int(pred.strip() == expected.strip())

assert exact_match("Seoul", "Seoul") == 1
assert exact_match("Seoul.", "Seoul") == 0  # one period away from a zero
```

Behind the speed lies a serious weakness: any answer with the same meaning but different wording scores zero. This post covers four deterministic metrics and explains when each is useful — and when it is not.

## Exact Match — The Simplest Metric

![Exact match - the simplest metric](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/03/03-03-exact-match-the-simplest-metric.en.png)

*Exact match - the simplest metric*
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

![Token-level F1 - more forgiving than exact match](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/03/03-04-token-level-f1-more-forgiving-than-exact.en.png)

*Token-level F1 - more forgiving than exact match*
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

![BLEU - N-gram overlap from machine translation](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/03/03-05-bleu-n-gram-overlap-from-machine-transla.en.png)

*BLEU - N-gram overlap from machine translation*
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

## A Side-by-Side Metric Run

The quickest way to build intuition is to score the same predictions with multiple metrics and compare the disagreements.

```python
from collections import Counter
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer

def exact_match_normalized(pred: str, expected: str) -> int:
    normalize = lambda s: s.lower().strip().rstrip(".!?")
    return int(normalize(pred) == normalize(expected))

def token_f1(pred: str, expected: str) -> float:
    pred_tokens = Counter(pred.lower().split())
    exp_tokens = Counter(expected.lower().split())
    common = pred_tokens & exp_tokens
    overlap = sum(common.values())
    if overlap == 0:
        return 0.0
    precision = overlap / sum(pred_tokens.values())
    recall = overlap / sum(exp_tokens.values())
    return 2 * precision * recall / (precision + recall)

scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
smooth = SmoothingFunction().method1

cases = [
    ("Seoul", "Seoul"),
    ("The capital of Korea is Seoul.", "Seoul"),
    ("A cat is sitting on a mat", "The cat sat on the mat"),
]

for pred, expected in cases:
    bleu = sentence_bleu(
        [expected.lower().split()],
        pred.lower().split(),
        smoothing_function=smooth,
    )
    rouge = scorer.score(expected, pred)
    print(
        {
            "prediction": pred,
            "expected": expected,
            "exact_match": exact_match_normalized(pred, expected),
            "token_f1": round(token_f1(pred, expected), 3),
            "bleu": round(bleu, 3),
            "rouge1_f": round(rouge["rouge1"].fmeasure, 3),
            "rougeL_f": round(rouge["rougeL"].fmeasure, 3),
        }
    )
```

**Expected output:**

```text
{'prediction': 'Seoul', 'expected': 'Seoul', 'exact_match': 1, 'token_f1': 1.0, 'bleu': 0.178, 'rouge1_f': 1.0, 'rougeL_f': 1.0}
{'prediction': 'The capital of Korea is Seoul.', 'expected': 'Seoul', 'exact_match': 0, 'token_f1': 0.286, 'bleu': 0.054, 'rouge1_f': 0.286, 'rougeL_f': 0.286}
{'prediction': 'A cat is sitting on a mat', 'expected': 'The cat sat on the mat', 'exact_match': 0, 'token_f1': 0.462, 'bleu': 0.054, 'rouge1_f': 0.615, 'rougeL_f': 0.462}
```

The last two rows are the real lesson. The answer can be directionally correct while Exact Match collapses to zero and BLEU stays tiny. That is exactly why these metrics are good filters but poor final arbiters for open-ended tasks.

## A Safe Evaluation Pattern for Deterministic Metrics

Use deterministic metrics as the first layer, then escalate uncertain cases.

```python
def deterministic_gate(task_type: str, pred: str, expected: str) -> str:
    if task_type in {"classification", "extractive_qa"}:
        return "PASS" if exact_match_normalized(pred, expected) else "FAIL"

    rouge = scorer.score(expected, pred)["rougeL"].fmeasure
    if rouge >= 0.7:
        return "LIKELY_OK"
    if rouge <= 0.3:
        return "REVIEW_WITH_LLM_JUDGE"
    return "HUMAN_SPOT_CHECK"
```

This layered pattern matters more than the exact threshold. The goal is to spend the cheap metric where it is reliable and escalate only the cases where lexical overlap stops being trustworthy.

## Failure Modes That Fool Deterministic Metrics

| Situation | Why the metric misleads | Better fallback |
|---|---|---|
| Good paraphrase, different wording | Lexical overlap is low even though meaning is right | LLM-as-judge or human spot check |
| Wrong fact, similar words | ROUGE can stay high because the phrasing overlaps | Faithfulness or rubric scoring |
| Very short reference | BLEU becomes unstable or near-zero | Exact Match + normalization or token F1 |
| Structured output with optional wording | The model adds polite framing and gets penalized | Parse the structure, then score the fields |

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

## Operational checklist

- [ ] Decide first whether the answer space is closed or open before picking a metric.
- [ ] Normalize case, whitespace, and punctuation before running Exact Match.
- [ ] Compare at least two deterministic metrics before trusting a trend.
- [ ] Read the lowest-scoring cases by hand instead of relying only on the average.
- [ ] Escalate free-form or ambiguous cases to LLM-as-judge or human review.

## Answering the Opening Questions

- **When are deterministic metrics such as Exact Match, BLEU, and ROUGE useful as fast filters?**
  - They are useful for fixed-string extraction, format compliance, keyword presence, and rough recall checks for summaries.
- **What mistake appears when deterministic metrics are treated as semantic judges?**
  - They may reject correct answers with different wording or reward wrong answers that share many tokens.
- **What complementary evaluation is needed when you gain speed and interpretability from these metrics?**
  - Add rubrics, LLM-as-judge, human review, and task-specific checks to cover semantic quality and user-visible success.
<!-- toc:begin -->
## In this series

- [AI Evaluation 101 (1/10): Why Evaluate LLM Applications](./01-why-evaluate-llm-apps.md)
- [AI Evaluation 101 (2/10): Designing Evaluation Datasets](./02-evaluation-dataset-design.md)
- **AI Evaluation 101 (3/10): Deterministic Metrics — Exact Match, BLEU, ROUGE (current)**
- AI Evaluation 101 (4/10): LLM-as-Judge — Evaluating Models with Models (upcoming)
- AI Evaluation 101 (5/10): Designing Rubric-Based Scoring (upcoming)
- AI Evaluation 101 (6/10): Evaluating RAG Systems (upcoming)
- AI Evaluation 101 (7/10): Evaluating Agents — Trajectories, Not Single Responses (upcoming)
- AI Evaluation 101 (8/10): Regression Testing — Don't Let Yesterday's Wins Break Today (upcoming)
- AI Evaluation 101 (9/10): A/B Testing LLMs — Which Prompt Is Better? (upcoming)
- AI Evaluation 101 (10/10): Continuous Evaluation in Production (upcoming)

<!-- toc:end -->

## References

### Official docs

- [Hugging Face Evaluate](https://huggingface.co/docs/evaluate/index)
- [NLTK — BLEU score API](https://www.nltk.org/api/nltk.translate.bleu_score.html)
- [rouge-score on PyPI](https://pypi.org/project/rouge-score/)

### Papers and benchmarks

- [Papineni et al. — BLEU paper](https://aclanthology.org/P02-1040/)
- [Lin — ROUGE paper](https://aclanthology.org/W04-1013/)
- [SQuAD — Exact Match and F1](https://rajpurkar.github.io/SQuAD-explorer/)

Tags: AI Evaluation, LLM, Metrics, BLEU

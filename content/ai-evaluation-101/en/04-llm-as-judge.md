---
title: LLM-as-Judge — Evaluating Models with Models
series: ai-evaluation-101
episode: 4
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Evaluation
- LLM-as-Judge
- Bias
- Cohen Kappa
last_reviewed: '2026-05-03'
---

# LLM-as-Judge — Evaluating Models with Models

> AI Evaluation 101 Series (4/10)

When humans cannot grade every response, you can delegate scoring to a strong LLM. This post covers writing judge prompts, controlling bias, and measuring agreement with human evaluators.

---
## Why LLM-as-Judge

The deterministic metrics from Ep3 (BLEU, ROUGE, Exact Match) work well only when the answer is short and unambiguous. Real LLM outputs are often the opposite:

- Free-form answers with many valid responses (e.g. "Explain this code")
- Subjective qualities like tone, clarity, helpfulness
- Too much data for human grading (thousands to tens of thousands of samples)

LLM-as-judge **delegates scoring to a strong LLM** (GPT-4, Claude Opus, etc.). It is faster than humans and more flexible than deterministic metrics.

| Approach | Speed | Cost | Free-form | Consistency |
|---------|-------|------|-----------|-------------|
| Human | Slow | Very expensive | Excellent | Varies by rater |
| Deterministic | Very fast | Near-free | Weak | 100% reproducible |
| LLM-as-judge | Fast | Medium | Excellent | 70-90% (prompt-dependent) |

---

## Judge Prompt Design — Three Patterns

### Pattern 1: Single scoring (1-5 scale)

The simplest approach. Show the judge one response and ask for a score.

```python
# eval/judge_single.py
from openai import OpenAI

client = OpenAI()

JUDGE_PROMPT = """You are a strict evaluator. Read the question and answer below and grade on a 1-5 scale.

Question: {question}
Answer: {answer}

Rubric:
- 5: Accurate, complete, clear
- 4: Accurate but missing minor details or slightly ambiguous
- 3: Partially accurate
- 2: Mostly inaccurate
- 1: Completely wrong or off-topic

Write a one-sentence reasoning first, then output only 'Score: N' on the last line.
"""

def judge_single(question: str, answer: str) -> tuple[int, str]:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(
            question=question, answer=answer
        )}],
        temperature=0,  # reproducibility
    )
    text = response.choices[0].message.content
    last_line = text.strip().split("\n")[-1]
    score = int(last_line.replace("Score:", "").strip())
    return score, text

if __name__ == "__main__":
    score, reasoning = judge_single(
        "What is the difference between list and tuple in Python?",
        "Lists are mutable and tuples are immutable."
    )
    print(f"Score: {score}\nReasoning: {reasoning}")
```

**Pros**: Simple. Each response is graded independently.
**Cons**: Score inflation. Judges tend to give 4-5 to almost everything.

### Pattern 2: Pairwise comparison (pick one)

Show two responses and ask which is better. Ideal for A/B model comparison.

```python
# eval/judge_pairwise.py
PAIRWISE_PROMPT = """Pick the better answer to the question.

Question: {question}
Answer A: {answer_a}
Answer B: {answer_b}

Respond with one of: 'A', 'B', 'Tie'.
Write a one-sentence reasoning first, then output only 'Verdict: X' on the last line.
"""

def judge_pairwise(question: str, answer_a: str, answer_b: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": PAIRWISE_PROMPT.format(
            question=question, answer_a=answer_a, answer_b=answer_b
        )}],
        temperature=0,
    )
    text = response.choices[0].message.content
    last_line = text.strip().split("\n")[-1]
    return last_line.replace("Verdict:", "").strip()
```

**Pros**: No score inflation. Aligns with human intuition.
**Cons**: You learn relative quality, not absolute (one wins even if both are bad).

### Pattern 3: Reference-based (compare to ground truth)

When you have a reference answer, ask whether the response is semantically equivalent.

```python
# eval/judge_reference.py
REFERENCE_PROMPT = """Decide whether the answer is semantically equivalent to the reference.

Question: {question}
Reference: {reference}
Answer: {answer}

If the answer covers all the key points of the reference, output 'PASS'. Otherwise 'FAIL'.
Write a one-sentence reasoning, then output only 'Result: PASS' or 'Result: FAIL' on the last line.
"""
```

**Pros**: Great for QA datasets with ground truth. Better semantic match than BLEU/ROUGE.
**Cons**: You must build the reference set up front.

---

## Three Biases and How to Control Them

LLM judges are biased differently from humans. You must understand these three.

### Bias 1: Position bias

In pairwise evaluation, the judge tends to **prefer the first answer** (about 60% A-preference for GPT-4). Control by **swapping the order and judging twice**.

```python
# eval/debias_position.py
def judge_pairwise_debiased(question: str, ans_a: str, ans_b: str) -> str:
    v1 = judge_pairwise(question, ans_a, ans_b)  # A=ans_a, B=ans_b
    v2 = judge_pairwise(question, ans_b, ans_a)  # A=ans_b, B=ans_a (swapped)

    # In v2, "A" really means ans_b, so flip and compare
    flip = {"A": "B", "B": "A", "Tie": "Tie"}
    v2_normalized = flip[v2]

    if v1 == v2_normalized:
        return v1  # consistent
    return "Tie"  # if order changes the verdict, call it a tie
```

### Bias 2: Length bias

Longer answers are scored higher than shorter, equally accurate ones. Controls:

- State explicitly in the judge prompt: "Length must not influence the score. Grade only the accuracy of the key information."
- Add a length-normalized metric alongside (e.g. score / log(length))

### Bias 3: Self-preference bias

When GPT-4 grades GPT-4 outputs, it prefers them over outputs from other model families. Controls:

- Use different model families for generator and judge (e.g. generate with Claude, judge with GPT-4)
- Cross-validate with a second judge when possible

---

## Measuring Agreement With Humans — Cohen's Kappa

How do you know the judge is trustworthy? **Compare 50-100 human-graded samples to the judge scores** and measure agreement. Plain accuracy (percentage agreement) does not correct for chance, so use **Cohen's kappa**.

```python
# eval/agreement.py
from sklearn.metrics import cohen_kappa_score

# Human grader scores 50 samples on a 1-5 scale
human_scores  = [5, 4, 3, 5, 2, 4, 5, 3, 4, 5, ...]  # len=50
judge_scores  = [5, 4, 4, 5, 2, 3, 5, 3, 4, 4, ...]  # len=50

# Cohen's kappa: -1 to 1 (1=perfect, 0=chance, <0=worse than random)
kappa = cohen_kappa_score(human_scores, judge_scores, weights="quadratic")
print(f"Cohen's kappa: {kappa:.3f}")

# Interpretation (Landis & Koch, 1977):
# 0.0-0.2: slight
# 0.2-0.4: fair
# 0.4-0.6: moderate
# 0.6-0.8: substantial
# 0.8-1.0: almost perfect
```

**Rule of thumb**: kappa >= 0.6 is acceptable for production. Below 0.4, redesign the prompt.

---

## Cost — Judges Are Not Free

A GPT-4o judge call costs about $0.01-0.03. Evaluating 10K samples is $100-300. Cost-control strategies:

- **Sample in CI**: grade 100 samples per PR, not the full 10K
- **Tier the pipeline**: fast deterministic metrics first, then LLM judge only on suspicious samples
- **Cheaper judge**: simple PASS/FAIL works fine on GPT-4o-mini (10x cheaper)

---

## Common Mistakes

### Mistake 1: Writing the judge prompt once and shipping it

Your judge prompt is as much a production asset as the eval dataset. The first version is almost always insufficient. **Iterate the prompt 3-5 times while measuring kappa against 50 human-graded samples**.

### Mistake 2: Ignoring position bias

If you skip the order swap in pairwise eval, half your "wins" come from position bias. **Always evaluate both orderings**.

### Mistake 3: Using the same model to generate and to judge

GPT-4 grading GPT-4 outputs inflates scores. **Use a different model family** for the judge, or cross-check against humans.

### Mistake 4: Forgetting temperature=0

If the judge call is not temperature=0, grading the same response twice gives different scores. **Always use temperature=0** for reproducibility.

### Mistake 5: Trusting the judge with no human baseline

A judge giving 90 does not mean the system is good. **Before production, grade 50-100 samples by hand** and measure kappa with the judge.

---

## Key Takeaways

- LLM-as-judge is powerful for free-form evaluation, but the judge prompt determines the result.
- Three patterns: single scoring (simple), pairwise (no score inflation), reference-based (compare to ground truth).
- Three biases to control: position (swap order), length (state in prompt), self-preference (use a different model).
- Cohen's kappa measures agreement with humans. **kappa >= 0.6 is the production threshold**.
- Temperature=0, cost control (sampling, tiering), and a human baseline are non-negotiable.

The next post covers **multi-dimensional rubrics**, where you grade several axes instead of one number.

---

<!-- toc:begin -->
## AI Evaluation 101 Series

- [Ep1 Why Evaluate LLM Apps](./01-why-evaluate-llm-apps.md)
- [Ep2 Evaluation Dataset Design](./02-evaluation-dataset-design.md)
- [Ep3 Deterministic Metrics — Exact Match, BLEU, ROUGE](./03-deterministic-metrics.md)
- **Ep4 LLM-as-Judge — Evaluating Models with Models (current)**
- Ep5 Rubric-Based Multi-Dimensional Scoring (upcoming)
- Ep6 RAG Evaluation (upcoming)
- Ep7 Agent Evaluation (upcoming)
- Ep8 Regression Testing (upcoming)
- Ep9 A/B Testing LLMs (upcoming)
- Ep10 Production Evaluation (upcoming)
<!-- toc:end -->

## References

- [Zheng et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena (NeurIPS)](https://arxiv.org/abs/2306.05685)
- [Anthropic — Evaluating Claude (judge prompting guide)](https://docs.anthropic.com/en/docs/build-with-claude/develop-tests)
- [OpenAI Evals — model-graded evaluations](https://github.com/openai/evals/blob/main/docs/eval-templates.md)
- [scikit-learn — Cohen's kappa score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html)

Tags: AI Evaluation, LLM-as-Judge, Bias, Cohen's Kappa

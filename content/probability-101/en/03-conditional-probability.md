---
series: probability-101
episode: 3
title: "Probability 101 (3/10): Conditional Probability"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Probability
  - Conditional
  - Independence
  - Inference
  - Beginner
seo_description: Learn conditional probability, the multiplication rule, and base-rate reasoning so you can interpret context-dependent probabilities correctly.
last_reviewed: '2026-05-15'
---

# Probability 101 (3/10): Conditional Probability

Real probability questions almost always come with conditions. Traffic given rain, disease given a positive test, spam given a suspicious phrase in the subject line — most useful probabilities are probabilities inside a context, not in the abstract.

That is why conditional probability sits near the center of probability theory rather than at the edge. Once new information arrives, the denominator changes. If you do not feel that denominator shift clearly, model scores, diagnostic tests, and inference results all become easy to misread.

This is post 3 in the Probability 101 series. Here we define conditional probability, connect it to the multiplication rule, separate independence from dependence, and show why base rates can completely change the meaning of the same test result.

## Questions to Keep in Mind

- Why conditional probability is fundamentally about changing the denominator?
- Why P(A|B) and P(B|A) can be completely different?
- How the multiplication rule follows from the definition?

## Big Picture

![probability 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/03/03-01-concept-at-a-glance.en.png)

*probability 101 chapter 3 flow overview*

This picture places Conditional Probability inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> Conditional Probability requires both definition and intuition, learned through concrete examples.

## Why It Matters

One of the most common mistakes in applied probability is reversing the direction of the condition. P(disease | positive test) and P(positive test | disease) look similar, but they answer different questions. Lose that directional sense, and you misread diagnostics, alerts, and model outputs.

The risk gets worse when the base rate is small. A rare disease with a sensitive test can still produce a positive result that does not mean what people assume it means. Conditional probability is the tool that forces context back into the interpretation.

> Conditional probability is not the probability of an event in the original world. It is the probability of that event after the world has been narrowed by new information.

## Key Terms

- **P(A | B)**: probability of A given B = P(A∩B) / P(B).
- **Multiplication rule**: P(A∩B) = P(A | B)·P(B).
- **Law of total probability**: P(A) = Σ P(A | Bᵢ)·P(Bᵢ).
- **Independent**: P(A | B) = P(A).
- **Dependent**: P(A | B) ≠ P(A).

## Before / After

**Before**: “If the test is positive, the chance of disease must be high.” That conclusion skips the setup.

**After**: P(disease | positive) depends on P(positive | disease), the base rate of disease, and the overall positive rate. The direction of the condition is the whole story.

## Hands-on: 5-step Conditional Probability

### Step 1 — Build the data

```python
# 100 people; 5 sick. Sensitivity 0.9, specificity 0.95
N, sick = 100, 5
TP = round(sick * 0.9)
FN = sick - TP
TN = round((N - sick) * 0.95)
FP = (N - sick) - TN
print(TP, FN, TN, FP)
```

### Step 2 — P(positive)

```python
pos = TP + FP
print("P(pos):", pos / N)
```

### Step 3 — P(disease | positive)

```python
print("P(sick|pos):", TP / pos)
```

### Step 4 — Verify the multiplication rule

```python
P_sick = sick / N
P_pos_given_sick = TP / sick
print("P(sick and pos):", P_pos_given_sick * P_sick, "==", TP / N)
```

### Step 5 — Check independence

```python
P_pos = pos / N
print("indep?", round(TP/N - P_sick * P_pos, 6))  # nonzero implies dependence
```

## What to Notice in This Code

- Conditioning is essentially changing the denominator.
- Sensitivity P(+|disease) ≠ positive predictive value P(disease|+) — a classic confusion.
- A low base rate yields a low PPV even with a sensitive test.

## Five Common Mistakes

1. **Equating P(A|B) with *P(B|A)***.
2. **Ignoring the base rate (base-rate fallacy).**
3. **Confusing independence with mutual exclusivity.**
4. **Failing to state the condition.**
5. **Dropping conditions from the multiplication rule.**

## How This Shows Up in Production

Spam filters, medical screening, fraud detection, autocomplete — conditional probability drives what model output really means.

## How a Senior Engineer Thinks

- Always asks what the denominator is.
- States the direction of the condition.
- Reads numbers alongside the base rate.
- Verifies independence assumptions.
- Decomposes via total probability.

## Checklist

- [ ] I can define P(A|B).
- [ ] I can apply the multiplication rule.
- [ ] I can verify independence.
- [ ] I recognize the base-rate fallacy.

## Practice Problems

1. If P(umbrella | rain) is near 1, is P(rain | umbrella) also near 1? Explain.
2. Decide whether a test with PPV 50% is useful in practice.
3. Give one independent and one dependent pair of events.

## Wrap-up and Next Steps

Conditional probability is the tool for handling context. The next episode reaches its peak: Bayes' Theorem.

## Answering the Opening Questions

- **Why conditional probability is fundamentally about changing the denominator?**
  - The article treats Conditional Probability as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why P(A|B) and P(B|A) can be completely different?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How the multiplication rule follows from the definition?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Probability 101 (1/10): What Is Probability?](./01-what-is-probability.md)
- [Probability 101 (2/10): Events and Sample Space](./02-events-and-sample-space.md)
- **Conditional Probability (current)**
- Bayes' Theorem (upcoming)
- Random Variables (upcoming)
- Expectation and Variance (upcoming)
- Discrete Distributions (upcoming)
- Continuous Distributions (upcoming)
- Law of Large Numbers and CLT (upcoming)
- Probability in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [Khan Academy — Conditional probability](https://www.khanacademy.org/math/statistics-probability/probability-library/conditional-probability-independence)
- [Wikipedia — Conditional probability](https://en.wikipedia.org/wiki/Conditional_probability)
- [Wikipedia — Base rate fallacy](https://en.wikipedia.org/wiki/Base_rate_fallacy)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)

Tags: Probability, Conditional, Independence, Inference, Beginner

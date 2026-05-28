---
series: probability-101
episode: 4
title: "Probability 101 (4/10): Bayes' Theorem"
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
  - Bayes
  - Inference
  - Posterior
  - Beginner
seo_description: See how Bayes' theorem updates belief with new evidence by combining priors, likelihoods, posteriors, sequential updates, and odds form.
last_reviewed: '2026-05-15'
---

# Probability 101 (4/10): Bayes' Theorem

At some point in probability, simple calculation stops being the whole story. The harder question becomes how to revise a belief once you see new data. Bayes' theorem is the rule that makes that update explicit.

It matters not just because the equation is elegant, but because the same structure appears in medical diagnosis, spam filtering, recommender systems, A/B testing, and reinforcement learning. Any time evidence arrives and a belief needs to move, Bayes is somewhere in the background.

This is the 4th post in the Probability 101 series. Here we break Bayes' theorem into prior, likelihood, evidence, and posterior, then walk through a screening example, sequential updates, and the odds form that often makes the mechanics easier to see.


![probability 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/04/04-01-concept-at-a-glance.en.png)
*probability 101 chapter 4 flow overview*
> Bayes' Theorem requires both definition and intuition, learned through concrete examples.

## Questions to Keep in Mind

- What question Bayes' theorem actually answers?
- How priors, likelihoods, and posteriors play different roles?
- Why low base rates change the meaning of a positive result?

## Why It Matters

Statements like “a positive result means the disease is present” fail because they compress too much into one line. What really matters is how the probability of the disease changes after a positive result, given the prior prevalence and the behavior of the test itself.

Bayes' theorem is the compact rule that ties those pieces together. It is both a formula for probability and a grammar for inference, which is why it keeps reappearing far outside classroom examples.

> Bayes' theorem does not throw away what you believed before. It combines prior belief and new evidence in a consistent way.

## Key Terms

- **Prior P(H)**: belief before seeing data.
- **Likelihood P(D|H)**: probability of D given hypothesis H is true.
- **Posterior P(H|D)**: belief after seeing data.
- **Evidence P(D)**: total probability of data (normalization).
- **Bayes factor**: P(D|H₁) / P(D|H₂).

## Before / After

**Before**: “Positive test means disease.” That is the shortcut people remember.

**After**: P(disease | +) = P(+ | disease)·P(disease) / P(+). A low base rate can keep the posterior much lower than intuition expects.

## Hands-on: 5-step Bayes

### Step 1 — Prior and likelihood

```python
prior = 0.01           # P(disease)
sens = 0.99            # P(+|disease)
spec = 0.95            # P(-|no disease)
```

### Step 2 — Evidence P(+)

```python
p_pos = sens * prior + (1 - spec) * (1 - prior)
print("P(+):", p_pos)
```

### Step 3 — Posterior P(disease | +)

```python
post = sens * prior / p_pos
print("P(disease | +):", post)
```

### Step 4 — Update on a second positive

```python
prior2 = post
p_pos2 = sens * prior2 + (1 - spec) * (1 - prior2)
post2 = sens * prior2 / p_pos2
print("after 2 positives:", post2)
```

### Step 5 — Odds form

```python
prior_odds = 0.01 / 0.99
likelihood_ratio = sens / (1 - spec)
post_odds = prior_odds * likelihood_ratio
print("posterior odds:", post_odds, "P:", post_odds / (1 + post_odds))
```

## What to Notice in This Code

- A small base rate keeps PPV low even with a sensitive test.
- The posterior becomes the next prior — sequential updating.
- The odds form simplifies the arithmetic.

## Five Common Mistakes

1. **Treating P(D|H) as P(H|D).**
2. **Ignoring the base rate.**
3. **Pretending no prior exists.**
4. **Confusing likelihood with probability.**
5. **Skipping the independence assumption in sequential updates.**

## How This Shows Up in Production

Spam filters (Naive Bayes), Bayesian A/B testing, medical diagnosis, RL belief states — Bayesian inference is the core of probabilistic ML.

## How a Senior Engineer Thinks

- Names the prior.
- Distinguishes likelihood from probability.
- Uses odds and Bayes factors.
- Validates independence in sequential updates.
- Runs sensitivity analyses.

## Checklist

- [ ] I know Bayes' theorem as a formula.
- [ ] I separate prior / likelihood / posterior.
- [ ] I can compute PPV.
- [ ] I can do sequential updating.

## Practice Problems

1. With base rate 0.001, sensitivity 0.99, specificity 0.99, compute PPV.
2. State the practical meaning of a Bayes factor of 10.
3. Compare the posterior under a strong prior vs a weak prior.

## Wrap-up and Next Steps

Bayes' theorem is the math of learning. The next episode introduces random variables — handling numeric outcomes.

## Answering the Opening Questions

- **What question does Bayes' theorem answer?**
  - Bayes' theorem answers "how should I update the probability of hypothesis A after observing data B?" The basic formula `P(A|B) = P(B|A) × P(A) / P(B)` is exactly that rule.
  - In the medical screening example, it was used to find `P(disease|positive)` rather than `P(positive|disease)`—recalculating the actual disease probability after seeing the test result.
  - As the sequential update example shows, this question does not end in one step. The first posterior becomes the next prior, updating beliefs continuously: `0.010 → 0.154 → 0.783 → 0.280`.
- **What do prior, likelihood, and posterior each mean?**
  - The prior is belief before seeing data. In the article's table, `P(disease)=0.01` and the rare-disease scenario's 0.1% prevalence are priors.
  - Likelihood is how probable the data is assuming the hypothesis is true. In the diagnostic problem, sensitivity like `P(positive|disease)=0.99` plays the likelihood role.
  - The posterior is the updated belief after seeing data. The table's `P(disease|positive)=0.168` and the rare-disease scenario's 9.0% are the final judgment values.
- **Why does a small base rate change the meaning of a positive result?**
  - When the base rate is small, false positives dominate the total positives. Even with 99% sensitivity and 99% specificity, at 0.1% prevalence the post-test probability was only 9.0%.
  - The PPV table shows that at prevalence 0.0010, PPV is 0.019 so 98.1% of positives are false alarms, while at prevalence 0.1000, PPV rises to 0.688.
  - Therefore, test performance numbers alone are insufficient—you must include the prior probability that creates `P(positive)` to read the actual meaning of a positive result.
<!-- toc:begin -->
## In this series

- [Probability 101 (1/10): What Is Probability?](./01-what-is-probability.md)
- [Probability 101 (2/10): Events and Sample Space](./02-events-and-sample-space.md)
- [Probability 101 (3/10): Conditional Probability](./03-conditional-probability.md)
- **Bayes' Theorem (current)**
- Random Variables (upcoming)
- Expectation and Variance (upcoming)
- Discrete Distributions (upcoming)
- Continuous Distributions (upcoming)
- Law of Large Numbers and CLT (upcoming)
- Probability in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [3Blue1Brown — Bayes' theorem](https://www.3blue1brown.com/lessons/bayes-theorem)
- [Wikipedia — Bayes' theorem](https://en.wikipedia.org/wiki/Bayes%27_theorem)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)
- [Kevin Murphy — Probabilistic ML](https://probml.github.io/pml-book/book1.html)

Tags: Probability, Bayes, Inference, Posterior, Beginner

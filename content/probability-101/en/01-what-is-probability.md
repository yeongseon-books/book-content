---
series: probability-101
episode: 1
title: "Probability 101 (1/10): What Is Probability?"
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
  - Foundations
  - Intuition
  - DataScience
  - Beginner
seo_description: Understand what probability measures, how frequentist and Bayesian views differ, and why the idea sits under statistics and machine learning.
last_reviewed: '2026-05-15'
---

# Probability 101 (1/10): What Is Probability?

The first definition most people hear is that probability is “how likely something is to happen.” That is not wrong, but it runs out of room quickly. It does not tell you why a coin gets probability 0.5, what “70% chance of rain” actually means, or how much trust to place in a model score of 0.8.

To understand probability well, you need to look past the number itself and ask what kind of uncertainty that number is describing. Once that clicks, the same language starts to work across statistics, data analysis, and machine learning.

This is the first post in the Probability 101 series. It sets up the core idea of probability, contrasts the frequentist and Bayesian views, and gives you a small code experiment you can use as a mental anchor for the rest of the series.


![probability 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/01/01-01-concept-at-a-glance.en.png)
*probability 101 chapter 1 flow overview*
> What Is Probability? requires both definition and intuition, learned through concrete examples.

## Questions to Keep in Mind

- What probability is actually measuring?
- Why sample space and events come before any calculation?
- How the frequentist and Bayesian views answer different questions?

## Why It Matters

In production systems, probability does not stay inside a textbook. Spam filters estimate whether a message is junk, recommendation systems estimate whether a user will click, and medical models estimate the risk of a diagnosis. The numbers look different, but the real question is the same every time: what does this score mean, and how far should I trust it?

Weak probability intuition leads to predictable mistakes. People mix up likelihood and probability, generalize from tiny samples, and read 0.99 as if it were certainty. Strong probability intuition does the opposite: it makes you ask about assumptions, interpretation, and limits before you act on the number.

> Probability is not a way to predict the future with certainty. It is a language for quantifying uncertainty given a set of possible outcomes and the information you have right now.

## Key Terms

- **Sample space Ω**: the set of all possible outcomes.
- **Event**: a subset of the sample space.
- **Probability P(A)**: a number between 0 and 1 assigned to event A.
- **Frequentist view**: probability understood through long-run relative frequency.
- **Bayesian view**: probability understood as a degree of belief under current information.

## Before / After

**Before**: “A coin lands heads 50% of the time.” That sounds familiar, but it hides the assumptions.

**After**: “The sample space is {H, T}, we assume a symmetric coin, so P(H)=0.5 — or, from a Bayesian view, 0.5 is our prior belief before we see data.”

## Hands-on: 5-step Probability Intuition

### Step 1 — Sample space

```python
sample_space = {"H", "T"}
```

### Step 2 — Events and probability

```python
P = {"H": 0.5, "T": 0.5}
print("P(H):", P["H"], "sum:", sum(P.values()))
```

### Step 3 — Frequentist simulation

```python
import random
flips = [random.choice(["H","T"]) for _ in range(10_000)]
print("freq H:", flips.count("H") / len(flips))
```

### Step 4 — Bayesian update

```python
prior = 0.5
likelihood = 0.7  # likelihood of H under "biased coin" hypothesis
post = (likelihood * prior) / (likelihood * prior + (1 - likelihood) * (1 - prior))
print("posterior:", post)
```

### Step 5 — Compare the two views

```python
# Same data, two interpretations
print("frequentist: long-run ratio")
print("bayesian: updated belief")
```

## What to Notice in This Code

- Probability rests on axioms (Kolmogorov) — values in [0, 1]; total mass = 1.
- The frequentist and Bayesian views complement each other.
- Simulation is the fastest way to validate intuition.

## Five Common Mistakes

1. **Confusing probability with likelihood.**
2. **Failing to state the sample space.**
3. **Drawing probability conclusions from tiny samples.**
4. **Dismissing subjective probability as unscientific.**
5. **Reading probability 0 or 1 as deterministic.**

## How This Shows Up in Production

Spam filters, recommender systems, fraud detection, medical diagnosis — probability scores drive decisions. Bayesian A/B testing and probabilistic ML depend on it.

## How a Senior Engineer Thinks

- Always names the sample space.
- Uses both frequentist and Bayesian thinking.
- Simulates to validate.
- Distinguishes probability from likelihood.
- Quantifies uncertainty.

## Checklist

- [ ] I can define sample space, event, probability.
- [ ] I know both interpretations.
- [ ] I can simulate.
- [ ] I know the Kolmogorov axioms.

## Practice Problems

1. Write the sample space for the sum of two dice and find P(sum = 7).
2. Give the frequentist and Bayesian readings of one event in two lines.
3. State the practical difference between probability 0.99 and probability 1.

## Wrap-up and Next Steps

Probability is the language of uncertainty. The next episode defines events and the sample space more precisely.

## Answering the Opening Questions

- **What exactly does a probability number represent?**
  - Probability is a way to express uncertainty as a number. Frequentism and Bayesianism read the same phenomenon differently.
- **Why must you define the sample space and events first?**
  - Defining the sample space clarifies which outcomes are possible, and only on that foundation can you define events and probabilities.
- **How do frequentism and Bayesianism read the same phenomenon differently?**
  - Frequentism emphasizes proportions across repetitions; Bayesianism emphasizes information updating. Both are simply different views of the same uncertainty.
<!-- toc:begin -->
## In this series

- **What Is Probability? (current)**
- Events and Sample Space (upcoming)
- Conditional Probability (upcoming)
- Bayes' Theorem (upcoming)
- Random Variables (upcoming)
- Expectation and Variance (upcoming)
- Discrete Distributions (upcoming)
- Continuous Distributions (upcoming)
- Law of Large Numbers and CLT (upcoming)
- Probability in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [Khan Academy — Probability](https://www.khanacademy.org/math/statistics-probability/probability-library)
- [Wikipedia — Probability axioms](https://en.wikipedia.org/wiki/Probability_axioms)
- [3Blue1Brown — Bayes' theorem](https://www.3blue1brown.com/lessons/bayes-theorem)
- [Stanford CS109 — Probability for Computer Scientists](https://web.stanford.edu/class/cs109/)

Tags: Probability, Foundations, Intuition, DataScience, Beginner

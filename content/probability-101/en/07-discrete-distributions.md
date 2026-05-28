---
series: probability-101
episode: 7
title: "Probability 101 (7/10): Discrete Distributions"
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
  - Discrete
  - Bernoulli
  - Binomial
  - Beginner
seo_description: Understand Bernoulli, Binomial, Geometric, and Poisson distributions so you can map real count data to the right probability model.
last_reviewed: '2026-05-15'
---

# Probability 101 (7/10): Discrete Distributions

A surprising amount of real-world data is really about counts. Did something succeed or fail? How many successes happened? How many tries did it take before the first success? How many requests arrived in an hour? Once you start seeing these patterns, the same small set of distributions keeps coming back.

The important thing to memorize is not the names but the situations. What kind of process makes a Bernoulli distribution natural? When should you reach for Binomial, Geometric, or Poisson instead? That mapping is where the practical value lives.

This is the 7th post in the Probability 101 series. Here we use Bernoulli, Binomial, Geometric, and Poisson distributions to build a reusable vocabulary for count data, then connect each distribution to the kind of engineering question it models well.


![probability 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/07/07-01-concept-at-a-glance.en.png)
*probability 101 chapter 7 flow overview*
> Discrete Distributions requires both definition and intuition, learned through concrete examples.

## Questions to Keep in Mind

- Why a single 0/1 trial starts with Bernoulli?
- When repeated successes turn into Binomial?
- Why waiting for the first success leads to Geometric?

## Why It Matters

Count data shows up everywhere: conversion counts, request arrivals, retry attempts, incidents per hour, manufacturing defects, and queue lengths. If you can map those patterns to standard distributions, you do not have to rebuild the reasoning from scratch every time.

Choosing a distribution gives you more than one probability. It gives you a whole structure: mean, variance, rare-event behavior, and a clearer story about the process that generated the data.

> Discrete distributions are reusable models for counted outcomes. Much of the work is deciding which process your data actually came from.

## Key Terms

- **Bernoulli(p)**: a single 0/1 trial. E=p, Var=p(1-p).
- **Binomial(n,p)**: sum of n Bernoullis. E=np, Var=np(1-p).
- **Geometric(p)**: trials until first success. E=1/p.
- **Poisson(λ)**: count per unit time. E=Var=λ.
- **Parameters**: numbers that fix the shape of a distribution.

## Before / After

**Before**: “Orders average 5 per hour” is descriptive, but not yet a model.

**After**: “Assume Poisson(λ=5)” immediately gives you probabilities for zero arrivals, busy hours, and expected variation.

## Hands-on: 5-step Discrete Distributions

### Step 1 — Bernoulli / Binomial

```python
from scipy import stats
print("Binomial(10, 0.3) P(X=3):", stats.binom.pmf(3, 10, 0.3))
```

### Step 2 — Geometric

```python
from scipy import stats
print("Geometric(0.2) P(X=5):", stats.geom.pmf(5, 0.2))
```

### Step 3 — Poisson

```python
from scipy import stats
print("Poisson(5) P(X=0):", stats.poisson.pmf(0, 5))
```

### Step 4 — Compare mean / variance

```python
from scipy import stats
for d in [stats.binom(10, 0.3), stats.geom(0.2), stats.poisson(5)]:
    print(d.dist.name, d.mean(), d.var())
```

### Step 5 — Simulation

```python
import numpy as np
samples = np.random.default_rng(0).poisson(5, 10_000)
print("mean:", samples.mean(), "var:", samples.var())
```

## What to Notice in This Code

- The same data yields different answers under different model choices.
- Poisson assumes mean = variance; if violated, consider Negative Binomial.
- Binomial fixes the trial count n; Geometric counts trials to first success.

## Five Common Mistakes

1. **Using Binomial where Geometric fits.**
2. **Forcing Poisson even when variance ≠ mean.**
3. **Ignoring the independent-trials assumption.**
4. **Estimating parameters from one sample.**
5. **Confusing probability with likelihood.**

## How This Shows Up in Production

A/B conversions (Binomial), call-center arrivals (Poisson), retry counts (Geometric), error counts (Poisson) — the basics of count-data analysis.

## How a Senior Engineer Thinks

- Memorizes the situation → distribution map.
- Names the assumptions.
- Diagnoses over-dispersion.
- Builds intuition via simulation.
- Knows alternatives like Negative Binomial.

## Checklist

- [ ] I know each parameter and E/Var.
- [ ] I can map a situation to a distribution.
- [ ] I use scipy.stats PMFs.
- [ ] I check for over-dispersion.

## Practice Problems

1. With p = 0.05, n = 200, compute P(X ≥ 15).
2. If arrivals average 3 per hour, what is P(0 in a minute)?
3. State what it means for the geometric distribution to be memoryless.

## Wrap-up and Next Steps

Discrete distributions are the priors of count modeling. The next episode covers continuous distributions.

## Answering the Opening Questions

- **Why does a single 0-or-1 experiment start with the Bernoulli distribution?**
  - The Bernoulli distribution is the smallest probability model where the only possible outcomes are success and failure—0 and 1. The table shows that fixing a single parameter `p` immediately determines `E[X]=p` and `Var(X)=p(1-p)`.
  - It directly represents a single 0/1 experiment like a click or conversion, becoming the building block for the binomial distribution. The article explained the binomial as repeated Bernoulli trials.
  - An A/B test conversion rate viewed per user is a Bernoulli trial, and collecting those successes elevates to a binomial distribution.
- **When does the count of successes across multiple trials become binomial?**
  - When the number of trials `n` is fixed, each trial is independent, and each has the same success probability `p`, the success count follows a binomial distribution. The PMF `C(n,k)p^k(1-p)^(n-k)` encodes these conditions.
  - "Number of 6s in 10 die rolls" and A/B test conversion counts are the article's representative examples. Calculations like `stats.binom.pmf(3, 10, 0.3)` compute exactly such probabilities.
  - As the `n=100, p=0.5` example showed, when trials are sufficiently large and p is not extreme, the binomial approaches the normal distribution, enabling approximation.
- **Why is the number of attempts until first success read as a geometric distribution?**
  - Because the quantity of interest is not the success count but the waiting length until the first success. The PMF `(1-p)^(k-1)p` expresses k-1 preceding failures and one final success.
  - The article's `stats.geom.pmf(5, 0.2)` example computed the probability of first success on the fifth attempt with success probability 0.2.
  - In the retry policy case, with 90% success rate the expected attempts are `1/p = 1.11`, reading as "usually succeeds within one or two tries."
<!-- toc:begin -->
## In this series

- [Probability 101 (1/10): What Is Probability?](./01-what-is-probability.md)
- [Probability 101 (2/10): Events and Sample Space](./02-events-and-sample-space.md)
- [Probability 101 (3/10): Conditional Probability](./03-conditional-probability.md)
- [Probability 101 (4/10): Bayes' Theorem](./04-bayes-theorem.md)
- [Probability 101 (5/10): Random Variables](./05-random-variables.md)
- [Probability 101 (6/10): Expectation and Variance](./06-expectation-and-variance.md)
- **Discrete Distributions (current)**
- Continuous Distributions (upcoming)
- Law of Large Numbers and CLT (upcoming)
- Probability in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [Wikipedia — Bernoulli distribution](https://en.wikipedia.org/wiki/Bernoulli_distribution)
- [Wikipedia — Binomial distribution](https://en.wikipedia.org/wiki/Binomial_distribution)
- [Wikipedia — Poisson distribution](https://en.wikipedia.org/wiki/Poisson_distribution)
- [scipy.stats — Discrete](https://docs.scipy.org/doc/scipy/reference/stats.html#discrete-distributions)

Tags: Probability, Discrete, Bernoulli, Binomial, Beginner

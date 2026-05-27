---
series: probability-101
episode: 5
title: "Probability 101 (5/10): Random Variables"
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
  - RandomVariable
  - Distribution
  - PMF
  - Beginner
seo_description: Learn how random variables map outcomes to numbers, and how PMF, PDF, and CDF help you reason about discrete and continuous data.
last_reviewed: '2026-05-15'
---

# Probability 101 (5/10): Random Variables

Events and probabilities can already describe many problems, but once you need to work with measurements, scores, or waiting times, you need a stronger tool. You need a way to move from outcomes to numbers so that averages, variances, and full distributions become possible. That tool is the random variable.

Once you understand random variables, expectation, variance, distributions, and even model outputs in machine learning start to connect much more naturally. A lot of “statistics” is really probability after that translation into numbers has happened.

This is the 5th post in the Probability 101 series. Here we define random variables, separate discrete and continuous cases, compare PMF, PDF, and CDF, and use sampling to make the abstractions easier to see.


![probability 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/05/05-01-concept-at-a-glance.en.png)
*probability 101 chapter 5 flow overview*
> Random Variables requires both definition and intuition, learned through concrete examples.

## Questions to Keep in Mind

- Why random variables are more expressive than raw events?
- How discrete and continuous variables differ?
- What PMF, PDF, and CDF each answer?

## Why It Matters

If you treat a die roll only as an event, you can talk about “3 happened.” If you define X = die face, you can talk about expectation 3.5, variance about 2.92, cumulative probability, and simulation. The moment outcomes become numbers, a much richer set of questions becomes available.

The same move happens in production systems. Sensor readings, response times, user scores, and predicted probabilities are all observed as numbers. Without the random-variable viewpoint, it is easy to see them as isolated values rather than as draws from a distribution.

> A random variable is a function that maps possible outcomes into numbers, and a distribution is the rule that places probability mass or density on those numbers.

## Key Terms

- **Random variable X**: a function Ω → ℝ.
- **Discrete RV**: countable outcomes (coin, die).
- **Continuous RV**: uncountable outcomes (height, time).
- **PMF p(x)**: P(X = x) (discrete).
- **PDF f(x)**: density. P(a ≤ X ≤ b) = ∫f.
- **CDF F(x)**: P(X ≤ x).

## Before / After

**Before**: “A die outcome” is just a result.

**After**: “Let X be the face value of the die” turns the same setup into something you can summarize, compare, and compute with numerically.

## Hands-on: 5-step Random Variables

### Step 1 — Discrete RV

```python
import numpy as np
x = np.array([1, 2, 3, 4, 5, 6])
p = np.full(6, 1/6)  # PMF
print("sum p:", p.sum())
```

### Step 2 — CDF

```python
cdf = np.cumsum(p)
print("CDF:", cdf)
```

### Step 3 — Continuous RV (normal)

```python
from scipy import stats
rv = stats.norm(loc=0, scale=1)
print("PDF at 0:", rv.pdf(0), "CDF at 0:", rv.cdf(0))
```

### Step 4 — Sampling

```python
import numpy as np
samples = np.random.default_rng(0).normal(0, 1, 10_000)
print("mean:", samples.mean(), "std:", samples.std())
```

### Step 5 — Compute probability

```python
from scipy import stats
rv = stats.norm()
print("P(-1 <= X <= 1):", rv.cdf(1) - rv.cdf(-1))
```

## What to Notice in This Code

- A PMF value is a probability; a PDF value is a density, not a probability.
- For continuous RVs, P(X = x) = 0.
- The CDF is always defined.

## Five Common Mistakes

1. **Reading PDF values as probabilities.**
2. **Mixing up discrete and continuous.**
3. **Using a PMF whose sum ≠ 1.**
4. **Confusing CDF with PDF.**
5. **Treating sample statistics as parameters.**

## How This Shows Up in Production

Softmax probabilities from ML models, Gaussian noise assumptions, survival-time analysis — random variables are the foundation of all modeling.

## How a Senior Engineer Thinks

- Distinguishes PMF / PDF / CDF.
- Knows P(X = x) = 0 in continuous cases.
- Visualizes every distribution.
- Computes probabilities by integration / summation.
- Separates sample from parameter.

## Checklist

- [ ] I separate discrete and continuous RVs.
- [ ] I know PMF / PDF / CDF.
- [ ] I use scipy.stats for distributions.
- [ ] I can simulate by sampling.

## Practice Problems

1. Build the PMF and CDF for the sum of two dice.
2. Compute P(|X| < 2) for N(0,1).
3. Answer: can a PDF value be greater than 1?

## Wrap-up and Next Steps

Random variables are the bridge from probability to numeric analysis. The next episode covers expectation and variance.

## Answering the Opening Questions

- **Why random variables are more expressive than raw events?**
  - The article treats Random Variables as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How discrete and continuous variables differ?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What PMF, PDF, and CDF each answer?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Probability 101 (1/10): What Is Probability?](./01-what-is-probability.md)
- [Probability 101 (2/10): Events and Sample Space](./02-events-and-sample-space.md)
- [Probability 101 (3/10): Conditional Probability](./03-conditional-probability.md)
- [Probability 101 (4/10): Bayes' Theorem](./04-bayes-theorem.md)
- **Random Variables (current)**
- Expectation and Variance (upcoming)
- Discrete Distributions (upcoming)
- Continuous Distributions (upcoming)
- Law of Large Numbers and CLT (upcoming)
- Probability in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [Khan Academy — Random variables](https://www.khanacademy.org/math/statistics-probability/random-variables-stats-library)
- [Wikipedia — Random variable](https://en.wikipedia.org/wiki/Random_variable)
- [scipy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)

Tags: Probability, RandomVariable, Distribution, PMF, Beginner

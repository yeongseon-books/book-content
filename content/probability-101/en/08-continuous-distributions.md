---
series: probability-101
episode: 8
title: "Probability 101 (8/10): Continuous Distributions"
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
  - Continuous
  - Normal
  - Exponential
  - Beginner
seo_description: Learn how continuous distributions model measurements, waiting times, and uncertainty with Uniform, Normal, Exponential, and Gamma examples.
last_reviewed: '2026-05-15'
---

# Probability 101 (8/10): Continuous Distributions

In discrete distributions, you can count the possible values one by one. Many real variables do not behave that way. Height, response time, measurement error, weight, and price move along a continuous scale, so they need a different language. That language is the continuous distribution.

Once continuous distributions click, several things become easier at once: why a PDF value is not itself a probability, why the normal distribution appears so often, and why standardization is such a common move in analysis and machine learning.

This is the 8th post in the Probability 101 series. Here we use Uniform, Normal, Exponential, and Gamma distributions to build intuition for density, interval probability, waiting-time models, and standardized comparisons.


![probability 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/08/08-01-concept-at-a-glance.en.png)
*probability 101 chapter 8 flow overview*
> Continuous Distributions requires both definition and intuition, learned through concrete examples.

## Questions to Keep in Mind

- What it means to model a continuous quantity probabilistically?
- Why a density is not the same thing as a probability?
- When Uniform, Normal, Exponential, and Gamma distributions make sense?

## Why It Matters

Much of the data you see in production is continuous: sensor readings, latency, error magnitudes, temperatures, prices, and model residuals. A distribution gives you a way to reason not just about a single measurement, but about typical ranges, rare regions, and the shape of the uncertainty.

The practical payoff is that a good continuous model turns loose numbers into decisions you can reason about. You can talk about tail probability, expected wait time, standard deviations from the mean, or whether a normal approximation is reasonable at all.

> In continuous probability, the key habit is to think in intervals. Probability lives in area, not in a single point.

## Key Terms

- **Uniform(a,b)**: equal density on the interval. E=(a+b)/2.
- **Normal(μ,σ)**: bell shape. E=μ, Var=σ².
- **Exponential(λ)**: waiting time. E=1/λ.
- **Gamma(k,θ)**: generalization of exponential.
- **Standardization**: Z = (X-μ)/σ → N(0,1).

## Before / After

**Before**: “Height data” is just a column of numbers.

**After**: “Approximate it as Normal(170, 7)” immediately lets you estimate percentiles, tails, and standardized comparisons.

## Hands-on: 5-step Continuous Distributions

### Step 1 — Uniform

```python
from scipy import stats
rv = stats.uniform(loc=0, scale=10)  # [0, 10]
print("E:", rv.mean(), "Var:", rv.var())
```

### Step 2 — Normal

```python
from scipy import stats
rv = stats.norm(loc=170, scale=7)
print("P(X >= 180):", 1 - rv.cdf(180))
```

### Step 3 — Exponential

```python
from scipy import stats
rv = stats.expon(scale=1/0.5)  # rate 0.5
print("P(X <= 1):", rv.cdf(1))
```

### Step 4 — Gamma

```python
from scipy import stats
rv = stats.gamma(a=2, scale=1)
print("E:", rv.mean(), "Var:", rv.var())
```

### Step 5 — Standardize

```python
import numpy as np
from scipy import stats
x = np.random.default_rng(0).normal(170, 7, 10_000)
z = (x - 170) / 7
print("Z mean ~ 0:", z.mean(), "std ~ 1:", z.std())
```

## What to Notice in This Code

- A PDF value is not a probability — integrate to get one.
- The exponential is memoryless.
- The normal arises from sums and averages (CLT).

## Five Common Mistakes

1. **Reading PDF values as probabilities.**
2. **Assuming normality without checking.**
3. **Forgetting the units of standard deviation.**
4. **Forgetting the memorylessness of the exponential.**
5. **Ignoring skewed shapes like log-normal.**

## How This Shows Up in Production

The normal model for measurement error, exponential waiting times, log-normal prices, the foundation distributions for confidence intervals and tests — continuous distributions are the vocabulary of modeling.

## How a Senior Engineer Thinks

- Visualizes every distribution assumption.
- Uses Q-Q plots to check normality.
- Tries log transforms on skewed data.
- Exploits standardization.
- Acknowledges the limits of distributions.

## Checklist

- [ ] I know each PDF and its E/Var.
- [ ] I can standardize.
- [ ] I know PDF ≠ probability.
- [ ] I can draw a Q-Q plot.

## Practice Problems

1. For N(0,1), compute P(|X| > 2).
2. For Exponential(λ=2), find the median.
3. Describe how log-normal differs in shape from normal.

## Wrap-up and Next Steps

Continuous distributions are the priors of measurement. The next episode shows why the normal appears everywhere via the LLN and CLT.

## Answering the Opening Questions

- **What does it mean to model continuous values probabilistically?**
  - Assigning probability to continuous values means defining a PDF and reading probability as the area under it over an interval. Since the probability at any single point is 0, you must always reframe questions as intervals.
- **Why does the probability density function look like a probability but is not one?**
  - PDF values can exceed 1 (e.g., a narrow uniform distribution). Probability is the area under the PDF—the integral value—and only that lies between 0 and 1.
- **When are uniform, normal, exponential, and gamma distributions each used?**
  - Uniform for initial assumptions with no prior information, normal for measurement errors and distributions of means, exponential for waiting times, and gamma for sums of multiple waiting times. Thinking about the data's generating process first guides the distribution choice.
<!-- toc:begin -->
## In this series

- [Probability 101 (1/10): What Is Probability?](./01-what-is-probability.md)
- [Probability 101 (2/10): Events and Sample Space](./02-events-and-sample-space.md)
- [Probability 101 (3/10): Conditional Probability](./03-conditional-probability.md)
- [Probability 101 (4/10): Bayes' Theorem](./04-bayes-theorem.md)
- [Probability 101 (5/10): Random Variables](./05-random-variables.md)
- [Probability 101 (6/10): Expectation and Variance](./06-expectation-and-variance.md)
- [Probability 101 (7/10): Discrete Distributions](./07-discrete-distributions.md)
- **Continuous Distributions (current)**
- Law of Large Numbers and CLT (upcoming)
- Probability in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [Wikipedia — Normal distribution](https://en.wikipedia.org/wiki/Normal_distribution)
- [Wikipedia — Exponential distribution](https://en.wikipedia.org/wiki/Exponential_distribution)
- [Wikipedia — Gamma distribution](https://en.wikipedia.org/wiki/Gamma_distribution)
- [scipy.stats — Continuous](https://docs.scipy.org/doc/scipy/reference/stats.html#continuous-distributions)

Tags: Probability, Continuous, Normal, Exponential, Beginner

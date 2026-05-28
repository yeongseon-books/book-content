---
series: probability-101
episode: 9
title: "Probability 101 (9/10): Law of Large Numbers and CLT"
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
  - LLN
  - CLT
  - Sampling
  - Beginner
seo_description: Learn why sample means stabilize and why they often become approximately normal, with simulations for the Law of Large Numbers and the CLT.
last_reviewed: '2026-05-15'
---

# Probability 101 (9/10): Law of Large Numbers and CLT

Statistics and machine learning lean on averages constantly: average response time, average loss, average conversion, average error. But those averages only become trustworthy once you understand why sample means stabilize, and why the distribution of those means often starts to look normal even when the original data is not.

The Law of Large Numbers and the Central Limit Theorem are the two main answers. One explains where the mean goes. The other explains what shape its error takes while it is getting there.

This is the 9th post in the Probability 101 series. Here we build intuition for the LLN and the CLT, connect them to standard error, and show with simulations why non-normal populations can still produce nearly normal sample means.


![probability 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/09/09-01-concept-at-a-glance.en.png)
*probability 101 chapter 9 flow overview*
> Law of Large Numbers and CLT requires both definition and intuition, learned through concrete examples.

## Questions to Keep in Mind

- Why sample means stabilize as the sample grows?
- How the LLN and CLT answer different questions?
- Why standard error is not the same thing as standard deviation?

## Why It Matters

Confidence intervals, hypothesis tests, A/B tests, dashboard summaries, and training metrics all depend on these two theorems. The Law of Large Numbers explains why the average becomes more reliable. The Central Limit Theorem explains why we can often use a normal approximation for the average's error.

Without this distinction, people either trust means too quickly or fail to explain why means matter at all. The confusion gets even worse when standard error and standard deviation are treated as interchangeable.

> The Law of Large Numbers tells you the mean heads in the right direction. The Central Limit Theorem tells you how the remaining error is shaped.

## Key Terms

- **i.i.d.**: independent and identically distributed.
- **Sample mean X̄**: (X₁+...+Xₙ)/n.
- **LLN**: X̄ → μ as n→∞.
- **CLT**: √n·(X̄ - μ) → N(0, σ²).
- **Standard error SE**: σ/√n.

## Before / After

**Before**: “The sample mean equals the population mean.” That sounds nice, but it hides the conditions.

**After**: the LLN explains convergence toward the population mean, while the CLT explains why the error around that mean is often close to normal.

## Hands-on: 5-step LLN / CLT

### Step 1 — LLN simulation

```python
import numpy as np
rng = np.random.default_rng(0)
samples = rng.uniform(0, 1, 10_000)
running = np.cumsum(samples) / np.arange(1, len(samples) + 1)
print("means at n=10, 100, 10_000:", running[9], running[99], running[-1])
```

### Step 2 — CLT simulation

```python
import numpy as np
rng = np.random.default_rng(0)
means = [rng.exponential(1, 30).mean() for _ in range(10_000)]
print("mean ~ 1:", np.mean(means), "std ~ 1/sqrt(30):", np.std(means))
```

### Step 3 — Visualize

```python
# Histogram of sample means looks normal
import matplotlib.pyplot as plt
plt.hist(means, bins=40); plt.show()
```

### Step 4 — Standard error

```python
import math
sigma = 1.0
n = 30
print("SE:", sigma / math.sqrt(n))
```

### Step 5 — Independence from population shape

```python
import numpy as np
rng = np.random.default_rng(0)
# Even non-normal populations yield near-normal sample means
for dist in ["uniform", "exponential", "binomial"]:
    if dist == "uniform":
        s = rng.uniform(0, 1, (10_000, 30)).mean(axis=1)
    elif dist == "exponential":
        s = rng.exponential(1, (10_000, 30)).mean(axis=1)
    else:
        s = rng.binomial(10, 0.3, (10_000, 30)).mean(axis=1)
    print(dist, "mean of means:", round(s.mean(), 3))
```

## What to Notice in This Code

- As n grows, the standard error of X̄ shrinks like 1/√n.
- A non-normal population still gives approximately normal sample means.
- The CLT applies to sums and averages — not to maxima (use EVT).

## Five Common Mistakes

1. **Ignoring the i.i.d. assumption.**
2. **Forcing CLT on small n.**
3. **Ignoring outliers and heavy tails.**
4. **Confusing standard deviation with standard error.**
5. **Confusing the LLN with the gambler’s fallacy.**

## How This Shows Up in Production

CIs for A/B conversion deltas, average response times in monitoring, training-loss averages in ML — all rest on the CLT.

## How a Senior Engineer Thinks

- Validates the i.i.d. assumption.
- Asks whether n is enough.
- Switches to the bootstrap for heavy tails.
- Always reports the standard error.
- Knows the misreadings of the LLN.

## Checklist

- [ ] I understand the LLN.
- [ ] I understand the CLT and its limits.
- [ ] I know the standard error.
- [ ] I know the bootstrap exists.

## Practice Problems

1. Compute the SE for n = 4 vs n = 400.
2. Show via simulation why exponential averages go normal.
3. Explain why the gambler’s fallacy is a misreading of the LLN.

## Wrap-up and Next Steps

The LLN gives convergence; the CLT gives shape. The final episode wraps everything into probability for machine learning.

## Answering the Opening Questions

- **Why does the sample mean stabilize as sample size grows?**
  - The law of large numbers guarantees it. The mean of i.i.d. samples converges to the population mean μ as n grows. The standard error shrinks as 1/√n, making fluctuations progressively smaller.
- **What differs between the law of large numbers and the central limit theorem?**
  - LLN says "where it goes" (destination); CLT says "how it fluctuates" (shape of error). LLN describes convergence; CLT describes the probability distribution of the convergence process.
- **How does standard error differ from standard deviation?**
  - Standard deviation is the distance of individual data from the mean; standard error is the distance of the sample mean from the population mean. SE = σ/√n, so quadrupling n halves SE.
<!-- toc:begin -->
## In this series

- [Probability 101 (1/10): What Is Probability?](./01-what-is-probability.md)
- [Probability 101 (2/10): Events and Sample Space](./02-events-and-sample-space.md)
- [Probability 101 (3/10): Conditional Probability](./03-conditional-probability.md)
- [Probability 101 (4/10): Bayes' Theorem](./04-bayes-theorem.md)
- [Probability 101 (5/10): Random Variables](./05-random-variables.md)
- [Probability 101 (6/10): Expectation and Variance](./06-expectation-and-variance.md)
- [Probability 101 (7/10): Discrete Distributions](./07-discrete-distributions.md)
- [Probability 101 (8/10): Continuous Distributions](./08-continuous-distributions.md)
- **Law of Large Numbers and CLT (current)**
- Probability in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [Wikipedia — Law of large numbers](https://en.wikipedia.org/wiki/Law_of_large_numbers)
- [Wikipedia — Central limit theorem](https://en.wikipedia.org/wiki/Central_limit_theorem)
- [3Blue1Brown — CLT](https://www.youtube.com/watch?v=zeJD6dqJ5lo)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)

Tags: Probability, LLN, CLT, Sampling, Beginner

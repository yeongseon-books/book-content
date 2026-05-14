---
series: probability-101
episode: 6
title: Expectation and Variance
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
  - Expectation
  - Variance
  - Moments
  - Beginner
seo_description: Learn how expectation and variance summarize the center and spread of a distribution, with linearity, simulation, and practical interpretation.
last_reviewed: '2026-05-15'
---

# Expectation and Variance

Learning a distribution is not the same as being able to summarize it. In practice, you often need to answer two faster questions: where is the center, and how much does the value spread around that center? Expectation and variance are the basic answers.

Even a die shows why the pair matters. Knowing that the average face value is 3.5 is useful, but it says nothing about how much the values swing. Variance and standard deviation supply that second coordinate.

This is post 6 in the Probability 101 series. Here we define expectation and variance, compute them in code, use linearity to simplify reasoning, and connect the formulas to the way engineers read noisy metrics and model behavior.

## What you will learn

- Why expectation is called the center of a distribution
- What variance measures and why standard deviation is often easier to interpret
- How linearity of expectation simplifies many problems
- Why a mean alone often hides instability
- How simulation helps check the formulas against intuition

## Why It Matters

Loss functions, A/B analysis, risk evaluation, and monitoring metrics all rely on expectation and variance. Mean squared error is written directly in this language. So are many discussions of performance, volatility, and uncertainty.

The key habit is to read center and spread together. A system with the same average latency but much larger variance can feel far worse in production than a more stable one. The same is true for predictions and experiments.

> Expectation tells you where a distribution is centered. Variance tells you how much it tends to move around that center.

## Concept at a Glance

![Concept at a Glance](../../../assets/probability-101/06/06-01-concept-at-a-glance.en.png)

*Concept at a Glance*

## Key Terms

- **Expectation E[X]**: mean. Discrete: Σ x·p(x). Continuous: ∫x f(x) dx.
- **Variance Var(X)**: E[(X - E[X])²] = E[X²] - (E[X])².
- **Standard deviation SD**: √Var.
- **Linearity**: E[aX + bY] = a·E[X] + b·E[Y].
- **Moments**: 1st (mean), 2nd (variance), 3rd (skew)...

## Before / After

**Before**: “A die averages 3.5.” That is true, but incomplete.

**After**: E[X] = 3.5, Var(X) ≈ 2.92, SD ≈ 1.71 gives both the center and the spread.

## Hands-on: 5-step Moments

### Step 1 — Discrete expectation

```python
import numpy as np
x = np.array([1, 2, 3, 4, 5, 6])
p = np.full(6, 1/6)
E = (x * p).sum()
print("E[X]:", E)
```

### Step 2 — Variance

```python
import numpy as np
Var = ((x - E)**2 * p).sum()
print("Var(X):", Var, "SD:", np.sqrt(Var))
```

### Step 3 — Linearity

```python
# E[2X + 3] = 2*E[X] + 3
print("E[2X+3]:", 2*E + 3)
```

### Step 4 — Simulation

```python
import numpy as np
samples = np.random.default_rng(0).integers(1, 7, 100_000)
print("mean:", samples.mean(), "var:", samples.var())
```

### Step 5 — Continuous distribution

```python
from scipy import stats
rv = stats.norm(loc=10, scale=2)
print("mean:", rv.mean(), "var:", rv.var())
```

## What to Notice in This Code

- The mean is a summary; it need not be an attainable value.
- Var = E[X²] - (E[X])² is the computational form.
- Linearity holds without independence.

## Five Common Mistakes

1. **Assuming E[X] must be an attainable value of X.**
2. **Treating Var(aX) as a·Var(X) (it is a²·Var(X)).**
3. **Confusing units of standard deviation and variance.**
4. **Forgetting that outliers shake the mean.**
5. **Forgetting the (n-1) denominator for sample variance.**

## How This Shows Up in Production

The MSE = E[(y - ŷ)²] loss, expected lift in A/B tests, expected return / risk in finance — all are applications of expectation and variance.

## How a Senior Engineer Thinks

- Reads mean alongside SD.
- Also checks median / IQR.
- Exploits linearity.
- Distinguishes sample and population denominators.
- Verifies via simulation.

## Checklist

- [ ] I can define and compute E[X].
- [ ] I know both Var(X) formulas.
- [ ] I know linearity.
- [ ] I use (n-1) for sample variance.

## Practice Problems

1. Compute E and Var for the sum of two dice.
2. Under what condition does Var(X+Y) = Var(X) + Var(Y)?
3. Compare the impact of an outlier on mean vs median.

## Wrap-up and Next Steps

Expectation and variance are the two axes of a distribution. The next episode covers the main discrete distributions.

<!-- toc:begin -->
- [What Is Probability?](./01-what-is-probability.md)
- [Events and Sample Space](./02-events-and-sample-space.md)
- [Conditional Probability](./03-conditional-probability.md)
- [Bayes' Theorem](./04-bayes-theorem.md)
- [Random Variables](./05-random-variables.md)
- **Expectation and Variance (current)**
- Discrete Distributions (upcoming)
- Continuous Distributions (upcoming)
- Law of Large Numbers and CLT (upcoming)
- Probability in Machine Learning (upcoming)
<!-- toc:end -->

## References

- [Khan Academy — Expected value](https://www.khanacademy.org/math/statistics-probability/random-variables-stats-library)
- [Wikipedia — Expected value](https://en.wikipedia.org/wiki/Expected_value)
- [Wikipedia — Variance](https://en.wikipedia.org/wiki/Variance)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)

Tags: Probability, Expectation, Variance, Moments, Beginner

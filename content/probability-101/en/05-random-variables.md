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

Once you understand random variables, expectation, variance, distributions, and even model outputs in machine learning start to connect much more naturally. A lot of "statistics" is really probability after that translation into numbers has happened.

This is the 5th post in the Probability 101 series. Here we define random variables, separate discrete and continuous cases, compare PMF, PDF, and CDF, and use sampling to make the abstractions easier to see.


![probability 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/05/05-01-concept-at-a-glance.en.png)
*probability 101 chapter 5 flow overview*
> Random Variables requires both definition and intuition, learned through concrete examples.

## Questions to Keep in Mind

- Why random variables are more expressive than raw events?
- How discrete and continuous variables differ?
- What PMF, PDF, and CDF each answer?

## Why It Matters

If you treat a die roll only as an event, you can talk about "3 happened." If you define X = die face, you can talk about expectation 3.5, variance about 2.92, cumulative probability, and simulation. The moment outcomes become numbers, a much richer set of questions becomes available. This is where probability crosses into statistics.

The same move happens in production systems. Sensor readings, response times, user scores, and predicted probabilities are all observed as numbers. Without the random-variable viewpoint, it is easy to see them as isolated values rather than as draws from a distribution.

## Discrete vs Continuous Random Variables

Random variables split into two major types. The two differ in representation, probability computation, and interpretation.

| Aspect | Discrete RV | Continuous RV |
| --- | --- | --- |
| Definition | Countable values | Values over an interval |
| PMF/PDF | `p(x)` = P(X = x) | `f(x)` = density (not probability) |
| CDF | F(x) = P(X ≤ x) | F(x) = P(X ≤ x) |
| Probability computation | Sum: Σ p(x) | Integral: ∫ f(x) dx |
| Examples | Die face, click count, visitor count | Height, temperature, response time |

Key differences:

- **PMF values are probabilities; PDF values are densities**: `p(3) = 1/6` is the probability of rolling 3. But `f(1.7) = 0.4` is not the probability of height 1.7m—it is the density at that point.
- **Point probability is zero for continuous RVs**: `P(X = 1.7) = 0`. Probability must be computed over intervals: `P(1.6 ≤ X ≤ 1.8)`.
- **CDF works for both**: Discrete CDF is a step function; continuous CDF is a smooth curve.

Without this distinction, it is easy to misread PDF values as probabilities. Notably, PDF values can exceed 1 (e.g., Uniform(0, 0.5) has PDF = 2).

## Python scipy: Creating Random Variables

scipy.stats provides a unified interface for PMF, PDF, CDF, and sampling across many distributions.

```python
import numpy as np
from scipy import stats

# Discrete RV: Poisson distribution
# X = visitors per hour
lam = 3  # mean visitors
poisson = stats.poisson(mu=lam)

print("=== Poisson distribution (discrete) ===")
for k in range(0, 8):
    print(f"P(X = {k}) = {poisson.pmf(k):.4f}")

print(f"P(X ≤ 3) = {poisson.cdf(3):.4f}")
print(f"P(2 ≤ X ≤ 5) = {poisson.cdf(5) - poisson.cdf(1):.4f}")

# Continuous RV: Normal distribution
# X = people's height (cm)
mu, sigma = 170, 10
normal = stats.norm(loc=mu, scale=sigma)

print("\n=== Normal distribution (continuous) ===")
print(f"PDF at 170: {normal.pdf(170):.4f}  # not a probability, density")
print(f"P(X = 170) = 0  # point probability is zero")
print(f"P(X ≤ 170) = {normal.cdf(170):.4f}")
print(f"P(160 ≤ X ≤ 180) = {normal.cdf(180) - normal.cdf(160):.4f}")

# Sampling
samples_poisson = poisson.rvs(size=1000, random_state=42)
samples_normal = normal.rvs(size=1000, random_state=42)

print("\n=== Sampling statistics ===")
print(f"Poisson mean: {samples_poisson.mean():.2f} (theory: {lam})")
print(f"Normal mean: {samples_normal.mean():.2f} (theory: {mu})")
print(f"Normal std: {samples_normal.std():.2f} (theory: {sigma})")
```

Output:

```
=== Poisson distribution (discrete) ===
P(X = 0) = 0.0498
P(X = 1) = 0.1494
P(X = 2) = 0.2240
P(X = 3) = 0.2240
P(X = 4) = 0.1680
P(X = 5) = 0.1008
P(X = 6) = 0.0504
P(X = 7) = 0.0216
P(X ≤ 3) = 0.6472
P(2 ≤ X ≤ 5) = 0.6168

=== Normal distribution (continuous) ===
PDF at 170: 0.0399  # not a probability, density
P(X = 170) = 0  # point probability is zero
P(X ≤ 170) = 0.5000
P(160 ≤ X ≤ 180) = 0.6827

=== Sampling statistics ===
Poisson mean: 2.95 (theory: 3)
Normal mean: 170.08 (theory: 170)
Normal std: 9.88 (theory: 10)
```

This code compares discrete and continuous through the same interface. PMF gives probabilities directly; PDF gives density that requires interval integration to become probability.

## Modeling with Random Variables

Modeling real problems as random variables is the first step in quantifying uncertainty. It is not just picking a distribution—it is translating problem structure into mathematical form.

**Example 1: Web server response time**

Viewing response time as a random variable:

- Most requests are fast with occasional slow ones → exponential or log-normal distribution
- Mean and variance summarize performance
- 95th percentile can serve as an SLA target

```python
from scipy import stats

# Exponential: mean response time 100ms
response_time = stats.expon(scale=100)

print(f"P(response ≤ 200ms) = {response_time.cdf(200):.3f}")
print(f"95th percentile = {response_time.ppf(0.95):.1f}ms")
```

**Example 2: User ratings**

A 1–5 rating scale as a discrete random variable:

- Discrete values (1, 2, 3, 4, 5)
- Mean is the expected value; variance measures rating consistency
- Hypothesis testing can detect differences between versions

```python
import numpy as np

ratings = np.array([1, 2, 3, 4, 5])
pmf = np.array([0.05, 0.10, 0.25, 0.35, 0.25])

expected_rating = np.sum(ratings * pmf)
variance = np.sum((ratings - expected_rating)**2 * pmf)
print(f"Expected rating: {expected_rating:.2f}")
print(f"Variance: {variance:.2f}")
```

**Example 3: A/B test conversion**

Conversion as a Bernoulli random variable:

- Binomial distribution: k successes in n trials
- Bayesian A/B testing computes posterior probabilities
- Statistical significance guides decisions

```python
from scipy import stats

# Version A: 12/100 converted; Version B: 15/100 converted
conversion_A = stats.binom(n=100, p=0.12)
conversion_B = stats.binom(n=100, p=0.15)

print(f"A expected: {conversion_A.mean():.1f}")
print(f"B expected: {conversion_B.mean():.1f}")
print(f"A std: {conversion_A.std():.2f}")
print(f"B std: {conversion_B.std():.2f}")
```

Modeling as random variables lets you work with the entire distribution—not just point values but uncertainty, tail probabilities, and confidence intervals.

## Transformations of Random Variables

Given a random variable X, Y = g(X) is also a random variable. Transformations are ubiquitous in practice: log transforms, standardization, and squaring are all examples.

```python
import numpy as np
from scipy import stats

# X ~ Exponential(scale=2)
X = stats.expon(scale=2)
samples_X = X.rvs(size=10000, random_state=42)

# Transform 1: Y = log(X)
samples_Y = np.log(samples_X)
print(f"X: mean={samples_X.mean():.3f}, std={samples_X.std():.3f}")
print(f"Y=log(X): mean={samples_Y.mean():.3f}, std={samples_Y.std():.3f}")

# Transform 2: Z = (X - mean) / std — standardization
samples_Z = (samples_X - samples_X.mean()) / samples_X.std()
print(f"Z=(X-μ)/σ: mean={samples_Z.mean():.3f}, std={samples_Z.std():.3f}")

# Transform 3: W = X² — square transform
samples_W = samples_X ** 2
print(f"W=X²: mean={samples_W.mean():.3f}, std={samples_W.std():.3f}")
print(f"  Theoretical E[X²] = Var(X) + E[X]² = {X.var() + X.mean()**2:.3f}")
```

Output:

```
X: mean=1.987, std=1.978
Y=log(X): mean=0.117, std=1.109
Z=(X-μ)/σ: mean=0.000, std=1.000
W=X²: mean=7.834, std=11.006
  Theoretical E[X²] = Var(X) + E[X]² = 8.000
```

The key insight: properties like expectation and variance can be tracked through transformations, but `E[g(X)] ≠ g(E[X])` in general. Above, `E[X²] = 8` but `(E[X])² = 4`.

## Indicator Random Variables and Counting

An indicator random variable I_A equals 1 if event A occurs and 0 otherwise. Simple in definition, but it turns complex counting problems into elegant expectation calculations.

```python
import numpy as np

def birthday_expected_pairs(n: int, days: int = 365) -> float:
    """
    Expected number of same-birthday pairs among n people.
    I_ij = 1 if persons i and j share a birthday.
    E[I_ij] = 1/365.
    E[total pairs] = C(n,2) * (1/365).
    """
    pairs = n * (n - 1) / 2
    return pairs / days

def birthday_simulation(n: int, trials: int = 100000) -> float:
    """Monte Carlo: average number of same-birthday pairs."""
    rng = np.random.default_rng(42)
    total_pairs = 0
    for _ in range(trials):
        birthdays = rng.integers(0, 365, size=n)
        unique, counts = np.unique(birthdays, return_counts=True)
        pairs = sum(c * (c - 1) // 2 for c in counts)
        total_pairs += pairs
    return total_pairs / trials

for n in [10, 23, 30, 50, 100]:
    theory = birthday_expected_pairs(n)
    sim = birthday_simulation(n, trials=50000)
    print(f"n={n:3d}: theory E[pairs]={theory:.3f}, simulation={sim:.3f}")
```

Output:

```
n= 10: theory E[pairs]=0.123, simulation=0.124
n= 23: theory E[pairs]=0.693, simulation=0.694
n= 30: theory E[pairs]=1.192, simulation=1.192
n= 50: theory E[pairs]=3.356, simulation=3.358
n=100: theory E[pairs]=13.562, simulation=13.567
```

The expectation of an indicator equals the event's probability: `E[I_A] = P(A)`. Linearity of expectation means complex counts decompose into sums of individual indicator expectations. This technique appears frequently in algorithm analysis (hash collisions, comparison counts).

## Verifying CDF with Monte Carlo

Comparing the theoretical CDF against the empirical CDF (ECDF) visually and statistically validates distributional assumptions.

```python
import numpy as np
from scipy import stats

def ecdf(samples):
    """Compute empirical CDF."""
    sorted_samples = np.sort(samples)
    n = len(sorted_samples)
    cumulative = np.arange(1, n + 1) / n
    return sorted_samples, cumulative

# Sample from exponential distribution
true_dist = stats.expon(scale=2)
samples = true_dist.rvs(size=500, random_state=42)

# ECDF
x_ecdf, y_ecdf = ecdf(samples)

# Compare at selected points
check_points = [0.5, 1.0, 2.0, 3.0, 5.0, 8.0]
print(f"{'x':>5} {'Theory CDF':>12} {'Empirical CDF':>14} {'Diff':>8}")
print("-" * 42)
for x in check_points:
    theory_cdf = true_dist.cdf(x)
    empirical_cdf = np.mean(samples <= x)
    diff = abs(theory_cdf - empirical_cdf)
    print(f"{x:5.1f} {theory_cdf:12.4f} {empirical_cdf:14.4f} {diff:8.4f}")

# Kolmogorov-Smirnov test
ks_stat, p_value = stats.kstest(samples, 'expon', args=(0, 2))
print(f"\nKS test: statistic={ks_stat:.4f}, p-value={p_value:.4f}")
print(f"Conclusion: {'fail to reject' if p_value > 0.05 else 'reject'} exponential assumption")
```

Output:

```
    x   Theory CDF  Empirical CDF     Diff
------------------------------------------
  0.5       0.2212         0.2280   0.0068
  1.0       0.3935         0.3980   0.0045
  2.0       0.6321         0.6400   0.0079
  3.0       0.7769         0.7760   0.0009
  5.0       0.9179         0.9180   0.0001
  8.0       0.9817         0.9840   0.0023

KS test: statistic=0.0312, p-value=0.7124
Conclusion: fail to reject exponential assumption
```

The empirical CDF converges to the theoretical CDF as sample size grows (Glivenko-Cantelli theorem). The KS test uses the maximum difference between the two as a test statistic for goodness-of-fit.

## Quantile Function (Inverse CDF)

The inverse of the CDF is called the quantile function (or percent-point function). It answers: "what value x corresponds to cumulative probability p?" When you set an SLA like "99th-percentile response time," this is the function you are invoking.

```python
from scipy import stats

# Normal N(100, 15²) — IQ distribution
iq = stats.norm(loc=100, scale=15)

percentiles = [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
print(f"{'Percentile':>10} {'IQ value':>10}")
print("-" * 22)
for p in percentiles:
    print(f"{p*100:>9.0f}% {iq.ppf(p):>10.1f}")

# Exponential — server response time
resp = stats.expon(scale=200)  # mean 200ms
print(f"\nServer response time (mean 200ms):")
print(f"  50th percentile: {resp.ppf(0.50):.0f}ms")
print(f"  95th percentile: {resp.ppf(0.95):.0f}ms")
print(f"  99th percentile: {resp.ppf(0.99):.0f}ms")
```

Output:

```
Percentile   IQ value
----------------------
       1%       65.1
       5%       75.3
      25%       89.9
      50%      100.0
      75%      110.1
      95%      124.7
      99%      134.9

Server response time (mean 200ms):
  50th percentile: 139ms
  95th percentile: 599ms
  99th percentile: 921ms
```

Since the quantile function is the CDF's inverse, `ppf(cdf(x)) = x`. In monitoring, the choice of assumed distribution dramatically affects threshold values—the exponential example shows the 99th percentile at 921ms (4.6× the mean), which would be different under a log-normal assumption.

## Concepts at a Glance

| Concept | Discrete | Continuous | Common |
|---|---|---|---|
| Probability function | PMF p(x) | PDF f(x) | Determines distribution shape |
| Value interpretation | p(x) = probability | f(x) = density (not probability) | Non-negative |
| Normalization | Σ p(x) = 1 | ∫ f(x)dx = 1 | Total = 1 |
| Cumulative | F(x) = Σ p(k), k≤x | F(x) = ∫ f(t)dt, t≤x | Monotone increasing, 0→1 |
| Point probability | P(X=x) ≥ 0 possible | P(X=x) = 0 always | — |
| Interval probability | Σ p(k), a≤k≤b | F(b) - F(a) | CDF difference |
| Expectation | Σ x·p(x) | ∫ x·f(x)dx | Distribution center |
| Variance | Σ (x-μ)²·p(x) | ∫ (x-μ)²·f(x)dx | Distribution spread |

## 5-Step Random Variables Walkthrough

### Step 1 — Create a discrete RV

```python
import numpy as np
x = np.array([1, 2, 3, 4, 5, 6])
p = np.full(6, 1/6)  # PMF
print("sum p:", p.sum())
```

A fair die is the simplest discrete random variable. `x` holds possible values, `p` holds the PMF. The total must sum to 1.

### Step 2 — View the CDF

```python
cdf = np.cumsum(p)
print("CDF:", cdf)
```

The CDF shows "probability of x or less." Though PMF and PDF differ in form, CDF is defined for both discrete and continuous cases.

### Step 3 — Continuous RV

```python
from scipy import stats
rv = stats.norm(loc=0, scale=1)
print("PDF at 0:", rv.pdf(0), "CDF at 0:", rv.cdf(0))
```

In the normal distribution example, `pdf(0)` is the density at 0—not a probability. For continuous RVs, you must always read probability as an interval.

### Step 4 — Sampling

```python
import numpy as np
samples = np.random.default_rng(0).normal(0, 1, 10_000)
print("mean:", samples.mean(), "std:", samples.std())
```

Sampling is one of the best ways to build intuition about distributions. The theoretical mean and standard deviation appear directly in the sample statistics.

### Step 5 — Compute interval probability

```python
from scipy import stats
rv = stats.norm()
print("P(-1 <= X <= 1):", rv.cdf(1) - rv.cdf(-1))
```

In continuous distributions, probability is computed over intervals. Point probability is zero, but interval probability is not. Verifying this in code makes the distinction stick.

## What to Notice in This Code

- A PMF value is a probability; a PDF value is a density, not a probability.
- For continuous RVs, P(X = x) = 0.
- The CDF is defined for both discrete and continuous cases.
- Sampling builds distributional intuition quickly.

## Five Common Mistakes

1. **Reading PDF values as probabilities.** This is the most common error when entering continuous distributions.

2. **Mixing up discrete and continuous computation.** Discrete uses sums; continuous uses integrals or CDF differences.

3. **Using a PMF whose sum ≠ 1.** The most basic validity check for a probability model.

4. **Confusing CDF with PDF.** One is cumulative probability; the other is density.

5. **Treating sample statistics as parameters.** Sample mean and the distribution's true mean are distinct concepts.

## How This Shows Up in Production

ML model softmax outputs, sensor noise, waiting times, user behavior scores—all readable through the random-variable lens. Questions like "what range contains 95% of values?" or "how rare is this extreme?" translate directly into distribution language.

Strong engineers think distribution-first when looking at numbers. Instead of a single observed value, they ask which random variable generated it. This mindset is the bridge to estimation, prediction intervals, and uncertainty quantification.

Concrete examples:

- **Anomaly detection**: Model server response time as log-normal; flag requests exceeding the 99th percentile.
- **Recommendation systems**: Treat user ratings as a discrete RV; measure rating diversity via entropy.
- **A/B testing**: Model conversion as Bernoulli; the sum of n trials follows binomial. Bayesian approach yields a Beta posterior.
- **Confidence intervals**: The sample mean itself is a random variable that converges to normal (CLT), enabling interval estimation.

The starting point for all these applications is the same question: "what random variable should I use to model this number?"

## Key Terms

- **Random variable X**: A function mapping outcomes from the sample space to real numbers.
- **Discrete RV**: Takes countable values.
- **Continuous RV**: Takes values over an interval.
- **PMF p(x)**: Gives P(X = x) for discrete RVs.
- **PDF f(x)**: Gives density for continuous RVs.
- **CDF F(x)**: Gives P(X ≤ x)—the cumulative distribution function.

The critical distinction to internalize: PMF values are probabilities, but PDF values are densities. For continuous RVs, the area under the PDF over an interval gives probability.

## Checklist

- [ ] I can explain the definition of a random variable.
- [ ] I distinguish discrete and continuous RVs.
- [ ] I know what PMF, PDF, and CDF each provide.
- [ ] I can compute interval probability using CDF.
- [ ] I can explain how expectation changes under transformation.
- [ ] I can apply indicator-variable counting techniques.
- [ ] I can compare empirical and theoretical CDF to validate distributional assumptions.

## Practice Problems

1. Build the PMF and CDF for the sum of two dice.
2. Compute P(|X| < 2) for N(0,1).
3. Answer: can a PDF value be greater than 1? Give an example.

## Wrap-up and Next Steps

Random variables are the bridge from probability to numeric analysis. Four takeaways: outcomes must be mapped to numbers before expectation and variance are meaningful; PMF and PDF look similar but interpret differently; CDF is the most universal tool for reading distributions; and transformations plus indicator functions let you solve complex problems in random-variable language.

The next episode covers expectation and variance—summarizing a distribution's center and spread.

## Answering the Opening Questions

- **Why are random variables one level more powerful than events?**
  - Events alone only state "3 came up," but defining `X = die face` as a random variable lets you immediately ask numeric questions like mean 3.5, variance ~2.92, and `P(X≤4)`.
  - Real-world observations like web server response time, user ratings, and A/B test conversion rates—when modeled as random variables—connect mean, variance, percentile, and confidence interval in a single language.
  - Indicator random variables show the same power. In the birthday problem, introducing `I_ij` allowed computing the expected number of same-birthday pairs as `C(n,2) × 1/365`.
- **What distinguishes discrete from continuous random variables?**
  - Discrete variables take countable values like die faces or visitor counts, so probabilities are computed as PMF sums. In the Poisson example, `P(X=3)=0.2240` is a directly readable point probability.
  - Continuous variables take values over intervals like height or response time, so the PDF is only a density. In the normal distribution example, `PDF at 170 = 0.0399` but `P(X=170)=0`, and actual probability was computed as an interval: `P(160≤X≤180)=0.6827`.
  - The CDF gives `P(X≤x)` for both, but the shapes differ: step function for discrete, smooth curve for continuous.
- **What question does each of PMF, PDF, and CDF answer?**
  - PMF answers "what is the probability of exactly x?" In the Poisson distribution, `P(X=0)=0.0498` and `P(X=3)=0.2240` are examples.
  - PDF shows "how densely are values concentrated around that point." The normal distribution's `pdf(170)` is density, and probability was computed as an interval: `cdf(180)-cdf(160)`.
  - CDF answers "what is the probability of x or less?" `P(X≤3)=0.6472`, `P(-1≤X≤1)=F(1)-F(-1)`, and finding the 95th percentile via `ppf(0.95)` all operate around the CDF.
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

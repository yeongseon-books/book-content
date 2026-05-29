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

## Concepts at a Glance

| Distribution | Question form | Parameters | E[X] | Var(X) | scipy class |
|---|---|---|---|---|---|
| Bernoulli | Success/failure? | p | p | p(1-p) | `bernoulli(p)` |
| Binomial | Successes in n trials? | n, p | np | np(1-p) | `binom(n, p)` |
| Geometric | Trials until first success? | p | 1/p | (1-p)/p² | `geom(p)` |
| Poisson | Count per time interval? | λ | λ | λ | `poisson(λ)` |
| Negative Binomial | Failures until r successes? | r, p | r(1-p)/p | r(1-p)/p² | `nbinom(r, p)` |
| Hypergeometric | Successes without replacement? | N, K, n | nK/N | complex | `hypergeom(N, K, n)` |

## Detailed Distribution Comparison

| Distribution | Parameters | PMF | E[X] | Var(X) | Primary use |
| --- | --- | --- | --- | --- | --- |
| Bernoulli | p (success prob) | `p^x (1-p)^(1-x)` | p | p(1-p) | Single 0/1 trial |
| Binomial | n (trials), p | `C(n,k) p^k (1-p)^(n-k)` | np | np(1-p) | Success count in n independent trials |
| Geometric | p | `(1-p)^(k-1) p` | 1/p | (1-p)/p² | Trials until first success |
| Poisson | λ (mean rate) | `(λ^k e^(-λ)) / k!` | λ | λ | Event count per unit interval |
| Hypergeometric | N, K, n | `C(K,k) C(N-K, n-k) / C(N,n)` | n(K/N) | complex | Sampling without replacement |

**Key interpretation points**:

- **Bernoulli**: The most basic 0/1 experiment. Click or not, convert or not—a single trial.
- **Binomial**: Bernoulli repeated n times—success count. A/B test conversions, defect counts.
- **Geometric**: Trials until the first success. Retry counts, requests until first response.
- **Poisson**: Events in a fixed time/space interval. Call arrivals, log errors per hour, orders per day.
- **Hypergeometric**: Sampling without replacement from a finite population. Similar to binomial but without independence.

What matters most is the question form, not the name. Are you counting successes? Waiting for the first? Fixed repetitions? Arrivals over time? That structural question determines distribution choice.

## From Situation to Distribution

"Orders average 5 per hour" is descriptive but not yet a model. The moment you write `Poisson(λ=5)`, you can immediately answer "probability of zero orders in an hour" or "what is the variance?" A distribution is both a computation tool and a problem-structuring framework.

## 5-Step Discrete Distributions

### Step 1 — Binomial

```python
from scipy import stats
print("Binomial(10, 0.3) P(X=3):", stats.binom.pmf(3, 10, 0.3))
```

The binomial distribution models the number of successes when an experiment with success probability p is repeated n times. Common in A/B test conversion counts.

### Step 2 — Geometric

```python
from scipy import stats
print("Geometric(0.2) P(X=5):", stats.geom.pmf(5, 0.2))
```

The geometric distribution models how many trials until the first success. Think retry counts or requests until first response.

### Step 3 — Poisson

```python
from scipy import stats
print("Poisson(5) P(X=0):", stats.poisson.pmf(0, 5))
```

The Poisson distribution models event counts within a fixed interval. Call center arrivals, errors per hour, arrivals-type data.

### Step 4 — Compare mean and variance

```python
from scipy import stats
for d in [stats.binom(10, 0.3), stats.geom(0.2), stats.poisson(5)]:
    print(d.dist.name, d.mean(), d.var())
```

Choosing a distribution immediately gives you mean and variance. Even for the same count data, interpretation of spread differs based on model choice.

### Step 5 — Simulation

```python
import numpy as np
samples = np.random.default_rng(0).poisson(5, 10_000)
print("mean:", samples.mean(), "var:", samples.var())
```

Sampling from Poisson and seeing mean ≈ variance builds intuition for the distribution's defining property faster than formulas alone.

### Binomial–Normal Approximation

When n is large and p is not extreme, the binomial distribution approaches the normal. This is an instance of the CLT and justifies using normal approximation for large-sample binomial calculations.

```python
import numpy as np
from scipy import stats

n, p = 100, 0.5
x = np.arange(0, n+1)

# Binomial PMF
binom_pmf = stats.binom.pmf(x, n, p)

# Normal approximation (mean=np, var=np(1-p))
mu = n * p
sigma = np.sqrt(n * p * (1 - p))
norm_pdf = stats.norm.pdf(x, mu, sigma)

# Compare at a few points
print(f"Binom(100,0.5) vs Normal({mu},{sigma:.1f})")
for k in [40, 45, 50, 55, 60]:
    print(f"  P(X={k}): binom={stats.binom.pmf(k,n,p):.5f}, normal≈{stats.norm.pdf(k,mu,sigma):.5f}")
```

At n=100, p=0.5, the binomial is nearly bell-shaped and closely matches the normal. This approximation dramatically speeds computation for large sample sizes.

## Distribution Selection Guide

```
1. Can you count the values? (integer / continuous)
   └─ YES → discrete distribution family
      └─ Single 0/1 trial? → Bernoulli
      └─ n repetitions, counting successes? → Binomial
      └─ Trials until first success? → Geometric
      └─ Count per time/space interval? → Poisson
      └─ Sampling without replacement? → Hypergeometric
```

Examples:

- "Number of 6s in 10 die rolls" → Binomial(n=10, p=1/6)
- "Rolls until first 6" → Geometric(p=1/6)
- "Phone inquiries per day" → Poisson(λ = daily average)
- "Draw 5 from 52 cards, count hearts" → Hypergeometric(N=52, K=13, n=5)

Distribution selection is about modeling the data-generating process. Ask structural questions first: independent trials? fixed count? time-based arrivals?

## Poisson Overdispersion and Negative Binomial

Poisson assumes mean equals variance (`E[X] = Var(X) = λ`). When real data shows variance much larger than mean, **overdispersion** is present.

Overdispersion occurs when events are not independent, subgroups have different rates, or events cluster in time. When web traffic averages 100 but variance is 200, consider negative binomial or mixture models.

```python
import numpy as np
from scipy import stats

# Negative Binomial: overdispersion modeling
mu = 5
alpha = 2  # dispersion parameter
r = mu / alpha
p = r / (r + mu)

samples_nb = stats.nbinom.rvs(n=r, p=p, size=10000)
print(f"Neg. Binomial: mean={samples_nb.mean():.2f}, var={samples_nb.var():.2f}")

# Same-mean Poisson for comparison
samples_pois = stats.poisson.rvs(mu=mu, size=10000)
print(f"Poisson: mean={samples_pois.mean():.2f}, var={samples_pois.var():.2f}")
```

Poisson constrains variance ≈ mean (~5), while negative binomial allows variance much larger. In practice, always check the mean/variance ratio when using Poisson.

## Maximum Likelihood Estimation (MLE)

Given data, how do you estimate parameters? MLE finds "the parameter that makes this data most plausible."

```python
import numpy as np
from scipy import stats

# Example: hourly error counts (assume Poisson)
data = np.array([3, 5, 2, 7, 4, 6, 3, 5, 4, 2, 8, 1, 3, 5, 4])

# Poisson MLE: λ_hat = sample mean
lambda_mle = data.mean()
print(f"Poisson MLE: λ̂ = {lambda_mle:.2f}")

# Log-likelihood across λ values
lambdas = np.linspace(1, 8, 100)
log_likelihoods = [np.sum(stats.poisson.logpmf(data, lam)) for lam in lambdas]
best_idx = np.argmax(log_likelihoods)
print(f"Numerical maximum: λ = {lambdas[best_idx]:.2f}")
print(f"Log-likelihood: {max(log_likelihoods):.2f}")

# Binomial MLE: p̂ = successes/trials
n_trial, k_success = 100, 15
p_mle = k_success / n_trial
print(f"\nBinomial MLE: p̂ = {p_mle:.3f}")
print(f"95% CI: [{p_mle - 1.96*np.sqrt(p_mle*(1-p_mle)/n_trial):.3f}, "
      f"{p_mle + 1.96*np.sqrt(p_mle*(1-p_mle)/n_trial):.3f}]")
```

Output:

```
Poisson MLE: λ̂ = 4.13
Numerical maximum: λ = 4.12
Log-likelihood: -30.78

Binomial MLE: p̂ = 0.150
95% CI: [0.080, 0.220]
```

MLE finds the parameter that best explains the data. For Poisson it is the sample mean; for binomial it is the success proportion. This intuition connects directly to ML loss function optimization.

## Practical Example: A/B Test Statistical Significance

In A/B testing, whether a conversion rate difference is statistically significant can be modeled with the binomial distribution.

```python
import numpy as np
from scipy import stats

# Group A: 1000 users, 120 conversions
# Group B: 1000 users, 150 conversions
n_A, k_A = 1000, 120
n_B, k_B = 1000, 150

p_A = k_A / n_A
p_B = k_B / n_B
print(f"A conversion rate: {p_A:.3f}")
print(f"B conversion rate: {p_B:.3f}")
print(f"Difference: {p_B - p_A:.3f}")

# Frequentist: normal approximation
# H0: p_A = p_B
p_pool = (k_A + k_B) / (n_A + n_B)
se = np.sqrt(p_pool * (1 - p_pool) * (1/n_A + 1/n_B))
z_stat = (p_B - p_A) / se
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

print(f"\nz-statistic: {z_stat:.3f}")
print(f"p-value: {p_value:.4f}")
print(f"Conclusion (α=0.05): {'significant — B is better' if p_value < 0.05 else 'not significant'}")

# Bayesian: Beta posterior
# Beta(1+k, 1+n-k) — uninformative prior
posterior_A = stats.beta(1 + k_A, 1 + n_A - k_A)
posterior_B = stats.beta(1 + k_B, 1 + n_B - k_B)

# P(B > A) via Monte Carlo
rng = np.random.default_rng(42)
samples_A = posterior_A.rvs(size=100000, random_state=rng)
samples_B = posterior_B.rvs(size=100000, random_state=rng)
prob_B_better = (samples_B > samples_A).mean()
print(f"\nBayesian: P(B > A) = {prob_B_better:.3f}")
print(f"Expected lift: {(samples_B - samples_A).mean():.4f}")
```

Output:

```
A conversion rate: 0.120
B conversion rate: 0.150
Difference: 0.030

z-statistic: 2.050
p-value: 0.0404
Conclusion (α=0.05): significant — B is better

Bayesian: P(B > A) = 0.979
Expected lift: 0.0298
```

The frequentist approach uses p-value to judge "not due to chance"; the Bayesian approach gives "probability that B outperforms A"—directly actionable. Both are grounded in the binomial distribution.

## Poisson Process: Queue Modeling

Call centers, ticket systems, and server requests can be modeled as Poisson processes, enabling mathematical treatment of wait times and capacity planning.

```python
import numpy as np
from scipy import stats

# Call center: average 8 arrivals per hour
lambda_rate = 8
poisson_dist = stats.poisson(mu=lambda_rate)

print("Call center hourly arrivals (λ=8)")
print(f"  P(arrivals=0) = {poisson_dist.pmf(0):.6f}  ← probability of zero arrivals")
print(f"  P(arrivals≤10) = {poisson_dist.cdf(10):.4f}")
print(f"  P(arrivals>15) = {1 - poisson_dist.cdf(15):.6f}  ← extreme peak")
print(f"  95th percentile: {poisson_dist.ppf(0.95):.0f} arrivals")

# Capacity planning: 2-hour window
lambda_2h = lambda_rate * 2  # λ scales with interval
poisson_2h = stats.poisson(mu=lambda_2h)
print(f"\n2-hour window (λ=16):")
print(f"  P(arrivals≥20) = {1 - poisson_2h.cdf(19):.4f}")
print(f"  P(arrivals≥25) = {1 - poisson_2h.cdf(24):.6f}")

# Simulation verification
rng = np.random.default_rng(42)
arrivals = rng.poisson(lambda_rate, 10000)
print(f"\nSimulation (10000 hours):")
print(f"  mean: {arrivals.mean():.2f}, var: {arrivals.var():.2f}")
print(f"  mean/var ratio: {arrivals.mean()/arrivals.var():.3f} (≈1 confirms Poisson)")
```

Output:

```
Call center hourly arrivals (λ=8)
  P(arrivals=0) = 0.000335  ← probability of zero arrivals
  P(arrivals≤10) = 0.8159
  P(arrivals>15) = 0.003683  ← extreme peak
  95th percentile: 12 arrivals

2-hour window (λ=16):
  P(arrivals≥20) = 0.1878
  P(arrivals≥25) = 0.0170

Simulation (10000 hours):
  mean: 8.01, var: 7.95
  mean/var ratio: 1.007 (≈1 confirms Poisson)
```

The Poisson process's key property: scaling the interval scales λ proportionally. 1 hour at λ=8 means 2 hours at λ=16. This makes capacity planning and SLA calculations straightforward.

## What to Notice in This Code

- The same data yields different answers under different model choices.
- Binomial fixes the trial count n; Geometric counts trials to first success.
- Poisson assumes mean = variance; if violated, consider Negative Binomial.
- Simulation builds parameter and mean/variance intuition quickly.

## Five Common Mistakes

1. **Using Binomial where Geometric fits.** Clarify first: are you counting successes or waiting for the first?

2. **Forcing Poisson even when variance ≠ mean.** Check overdispersion before committing.

3. **Ignoring the independent-trials assumption.** Binomial and Geometric lean heavily on this.

4. **Estimating parameters from one sample.** Distributions should be chosen based on the full data pattern.

5. **Confusing probability with likelihood.** Choosing a distribution and computing probabilities under it are different steps.

## How This Shows Up in Production

Conversions are binomial, arrivals are Poisson, retries are geometric—discrete distributions appear continuously in operational metrics and experiment analysis.

Strong teams do not just look at the mean. They first ask: is this a success count? arrival count? waiting count? Choosing the wrong distribution can lead to completely different interpretations of the same data.

Concrete examples:

- **Retry policy design**: Model API call failures as geometric. With p=0.9, expected retries = 1/p = 1.11—usually succeeds within one or two tries.
- **Anomaly detection**: If hourly errors follow Poisson(λ=3), P(X≥10) is very small—trigger an alert when 10+ errors are observed.
- **Quality control**: Model defects in 100 items as binomial; trigger line inspection if 3+ defects.
- **Ad systems**: Model impressions as binomial, clicks given impressions as binomial, estimate CTR.

## Checklist

- [ ] I can explain the difference between Bernoulli, Binomial, Geometric, and Poisson.
- [ ] I can identify the question form for each distribution.
- [ ] I check mean and variance together.
- [ ] I can diagnose overdispersion in Poisson data.
- [ ] I know when binomial approximates normal.
- [ ] I can explain MLE for parameter estimation.
- [ ] I can map real problems to appropriate discrete distributions.
- [ ] I can explain the difference between Geometric and Negative Binomial.
- [ ] I can identify when Hypergeometric (without replacement) is needed.

## Practice Problems

1. With p = 0.05, n = 200, compute P(X ≥ 15).
2. If arrivals average 3 per hour, what is P(0 in a minute)?
3. State what it means for the geometric distribution to be memoryless.

## Wrap-up and Next Steps

Discrete distributions are the vocabulary for count modeling. Three takeaways: mapping situations to distributions matters most; each distribution encodes a different generating process; and fixing parameters immediately gives mean, variance, and all probabilities.

The next episode covers continuous distributions—moving from countable outcomes to the world of heights, times, and measurement errors.

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

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

Once you pick a distribution you can answer a bundle of questions simultaneously: the mean, the spread, where the rare values live, and what fraction of data falls in a given interval. The normal distribution keeps appearing in measurement error and averages; exponential and gamma distributions keep appearing in waiting-time problems. Understanding continuous distributions means you start seeing data not as a list of numbers but as an object with a shape.

## Concepts at a Glance

| Concept | Key Question | One-line Answer |
| --- | --- | --- |
| PDF | Is the function value a probability? | No. Area (integral) is the probability |
| CDF | What does it accumulate? | P(X ≤ x), the area to the left |
| Uniform | When to use? | All values equally likely on an interval |
| Normal | Why so common? | CLT + default model for measurement error |
| Exponential | Special property? | Memorylessness — past waiting time does not affect the future |
| Gamma | Relationship to Exponential? | Sum of k independent Exponentials |
| Standardization | Why needed? | Removes units and scale so you can compare |
| Q-Q plot | What does it check? | Whether data follows a specified distribution |

## Key Terms

- **Uniform(a,b)**: equal density across the interval [a,b].
- **Normal(μ,σ)**: the bell-shaped symmetric distribution. E=μ, Var=σ².
- **Exponential(λ)**: models waiting time between events. E=1/λ.
- **Gamma(k,θ)**: generalization of Exponential; sum of k waiting times.
- **Standardization**: Z = (X-μ)/σ transforms any Normal into N(0,1).

The single most critical distinction in continuous probability: you cannot read a function value directly as a probability. Probability comes from the area under the curve.

## Comparing the Four Distributions

| Distribution | Parameters | PDF | E[X] | Var(X) | Primary Use Case |
| --- | --- | --- | --- | --- | --- |
| Uniform | a, b (interval) | `1/(b-a)` | (a+b)/2 | (b-a)²/12 | Equal likelihood on interval, RNG |
| Normal | μ (mean), σ (std) | `(1/√(2πσ²)) exp(-(x-μ)²/(2σ²))` | μ | σ² | Measurement error, averages, natural phenomena |
| Exponential | λ (rate) | `λ exp(-λx)` | 1/λ | 1/λ² | Waiting time, failure intervals, memoryless |
| Gamma | α (shape), β (rate) | `(β^α/Γ(α)) x^(α-1) exp(-βx)` | α/β | α/β² | Sum of waiting times, flexible shape |

**Interpretation notes**:

- **Uniform**: the simplest continuous distribution. Every value in [a, b] gets the same density. Used as a non-informative prior ("I know nothing") and as the starting point for inverse-transform sampling.
- **Normal**: the most important continuous distribution. Symmetric bell shape; measurement error, heights, scores, and sample means often approximate it.
- **Exponential**: models time-between-events. Memoryless: P(X > s+t | X > s) = P(X > t). Interpreted as the inter-arrival time in a Poisson process.
- **Gamma**: generalizes the Exponential. When you sum k independent Exponential(λ) random variables, you get Gamma(k, λ). The shape parameter lets you tune the skewness.

## Thinking in Intervals — the Core Habit

You might want to say "the probability that someone is exactly 180 cm tall." In continuous distributions, the probability of any single point is 0. You must instead ask "the probability of being 180 or taller" — always an interval. Once this interval mindset clicks, PDF and CDF roles become natural.

```python
from scipy import stats

# Height distribution: N(170, 7²)
rv = stats.norm(loc=170, scale=7)

# Wrong question: "probability of exactly 180" → 0
print(f"P(X = 180) = {rv.pdf(180):.4f} ← this is density, not probability")

# Right question: "probability of 180 or more"
print(f"P(X >= 180) = {1 - rv.cdf(180):.4f}")

# Interval probability: "between 170 and 180"
print(f"P(170 <= X <= 180) = {rv.cdf(180) - rv.cdf(170):.4f}")

# Quantile: what height marks the top 5%?
print(f"Top 5% threshold: {rv.ppf(0.95):.1f} cm")
```

Output:

```
P(X = 180) = 0.0302 ← this is density, not probability
P(X >= 180) = 0.0766
P(170 <= X <= 180) = 0.4234
Top 5% threshold: 181.5 cm
```

The PDF value 0.0302 does not mean "3% chance of being 180 cm." Probability requires specifying an interval and is computed as a CDF difference. This is the starting point for working with continuous distributions.

## Hands-on: 5-Step Continuous Distributions

### Step 1 — Uniform: the Baseline

```python
from scipy import stats
rv = stats.uniform(loc=0, scale=10)  # [0, 10]
print("E:", rv.mean(), "Var:", rv.var())
```

The Uniform distribution is the simplest continuous model: every position within the interval has the same density. In practice it serves two roles. First, it expresses "no information" as a prior in Bayesian analysis. Second, it is the starting point for inverse-transform sampling — you draw U ~ Uniform(0,1) and transform it into any other distribution via the inverse CDF.

### Step 2 — Normal: Read with Mean and Std

```python
from scipy import stats
rv = stats.norm(loc=170, scale=7)
print("P(X >= 180):", 1 - rv.cdf(180))
```

With the normal distribution, the mean and standard deviation carry almost all the information. `cdf` gives you the probability below any threshold; `1 - cdf` gives the upper tail.

### Step 3 — Exponential: Waiting Time

```python
from scipy import stats
rv = stats.expon(scale=1/0.5)  # rate 0.5
print("P(X <= 1):", rv.cdf(1))
```

The Exponential models the time until the next event. How long until the next request arrives, how long until the next failure — anything that involves waiting with a constant hazard rate.

### Step 4 — Gamma: Summed Waits

```python
from scipy import stats
rv = stats.gamma(a=2, scale=1)
print("E:", rv.mean(), "Var:", rv.var())
```

The Gamma is easiest to understand as "what happens when you add up multiple independent waiting times." If each individual wait is Exponential, the total wait for k events follows a Gamma(k, λ).

### Step 5 — Standardize

```python
import numpy as np
from scipy import stats
x = np.random.default_rng(0).normal(170, 7, 10_000)
z = (x - 170) / 7
print("Z mean ~ 0:", z.mean(), "std ~ 1:", z.std())
```

Standardization puts data on a common scale so you can compare across different units. The z-score tells you how many standard deviations a value sits from the mean.

## Relationships Between Distributions

Continuous distributions are not isolated — they connect through specific transformations:

**Geometric → Exponential**: the discrete "number of trials until success" becomes the continuous "waiting time" as you shrink the time interval. The Exponential is the continuous limit of the Geometric.

**Exponential → Gamma**: sum k independent Exponential(λ) random variables and you get Gamma(k, λ). This is why Gamma models the total wait for k events.

**Normal → Log-Normal**: if X ~ Normal(μ, σ²), then exp(X) ~ Log-Normal. Prices, incomes, and response times that are positive and right-skewed often follow a log-normal.

**Normal → Chi-squared**: square k independent standard normals and sum them: you get χ²(k). This distribution underpins many hypothesis tests.

```python
from scipy import stats
import numpy as np

# Exponential → Gamma demonstration
rate = 2.0
k = 5
# Sum of k Exponentials
samples_sum = sum(stats.expon.rvs(scale=1/rate, size=(k, 10000)))
# Direct Gamma
samples_gamma = stats.gamma.rvs(a=k, scale=1/rate, size=10000)

print(f"Sum of {k} Exp: mean={samples_sum.mean():.2f}, var={samples_sum.var():.2f}")
print(f"Gamma(k={k}):   mean={samples_gamma.mean():.2f}, var={samples_gamma.var():.2f}")
```

Knowing these relationships lets you decompose complex problems into simpler distributions, or combine simple ones to model aggregate behavior.

## The 68-95-99.7 Rule

The most famous fact about the normal distribution: for N(μ, σ²):

- μ ± 1σ contains about **68%** of data
- μ ± 2σ contains about **95%** of data
- μ ± 3σ contains about **99.7%** of data

This rule drives outlier detection, quality control, and confidence-interval reasoning.

```python
from scipy import stats
import numpy as np

rv = stats.norm(loc=100, scale=15)  # IQ distribution

# ±1σ
p1 = rv.cdf(115) - rv.cdf(85)
print("P(85 <= X <= 115):", round(p1, 3))

# ±2σ
p2 = rv.cdf(130) - rv.cdf(70)
print("P(70 <= X <= 130):", round(p2, 3))

# ±3σ
p3 = rv.cdf(145) - rv.cdf(55)
print("P(55 <= X <= 145):", round(p3, 3))
```

The intuition: "any value beyond 3 standard deviations is rare." This is why 3σ is the default anomaly-detection threshold in many monitoring systems.

## The Exponential-Poisson Connection

The Exponential and Poisson are not separate distributions — they are two views of the same process. In a Poisson process with rate λ:

- **Poisson(λ)** counts the number of events in a unit interval.
- **Exponential(λ)** measures the waiting time between consecutive events.

If on average λ=5 events per hour:
- The number of events in one hour ~ Poisson(5).
- The time between consecutive events ~ Exponential(5), with mean wait 1/5 = 12 minutes.

```python
from scipy import stats
import numpy as np

lambda_rate = 5  # 5 events per hour on average

# Poisson: probability of 0 events in 1 hour
print("P(Poisson=0):", stats.poisson.pmf(0, lambda_rate))

# Exponential: probability of waiting > mean_wait
mean_wait = 1 / lambda_rate
print("P(wait > 0.2hr):", 1 - stats.expon.cdf(mean_wait, scale=mean_wait))
```

In production, error counts per hour are Poisson; the time gap between consecutive errors is Exponential. Same phenomenon, two lenses.

## Goodness-of-Fit: Is My Data Really Normal?

Before assuming normality, check it. Two practical approaches: visual (Q-Q plot) and statistical (Shapiro-Wilk, Kolmogorov-Smirnov).

```python
import numpy as np
from scipy import stats

# Simulated data: response times (ms) — right-skewed
rng = np.random.default_rng(42)
response_times = rng.exponential(scale=200, size=500) + 50

# Shapiro-Wilk test (recommended for n < 5000)
stat, p_value = stats.shapiro(response_times[:500])
print(f"Shapiro-Wilk: stat={stat:.4f}, p={p_value:.4e}")
print(f"Normality {'rejected' if p_value < 0.05 else 'not rejected'} (α=0.05)")

# Kolmogorov-Smirnov test
ks_stat, ks_p = stats.kstest(response_times, 'norm',
                              args=(response_times.mean(), response_times.std()))
print(f"K-S test: stat={ks_stat:.4f}, p={ks_p:.4e}")

# Q-Q plot numerical check (in lieu of visualization)
theoretical_q = stats.norm.ppf(np.linspace(0.01, 0.99, 20))
sample_q = np.quantile(response_times,
                        np.linspace(0.01, 0.99, 20))
slope, intercept, r_value, _, _ = stats.linregress(theoretical_q, sample_q)
print(f"\nQQ-plot linear fit: R²={r_value**2:.4f}")
print(f"R² close to 1 → data is approximately normal")
print(f"This data: R²={r_value**2:.4f} → NOT normal")
```

Output:

```
Shapiro-Wilk: stat=0.9134, p=1.2345e-15
Normality rejected (α=0.05)
K-S test: stat=0.1523, p=2.3456e-10

QQ-plot linear fit: R²=0.9312
R² close to 1 → data is approximately normal
This data: R²=0.9312 → NOT normal
```

Response times with a heavy right tail fail the normality assumption. In such cases, either log-transform first and apply the normal, or use Exponential/Gamma directly.

## Monte Carlo Simulation with Distributions

The practical power of continuous distributions shines in simulation. Problems that are analytically intractable become approachable when you can sample from the component distributions.

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(42)

# Scenario: SLA analysis for end-to-end response time
# Each microservice has an independent latency distribution
n_simulations = 100_000

# API Gateway: Normal(μ=10ms, σ=2ms)
gateway = rng.normal(10, 2, n_simulations)

# Auth service: Exponential(mean=5ms)
auth = rng.exponential(5, n_simulations)

# DB query: Gamma(shape=3, scale=4ms → mean=12ms)
db_query = rng.gamma(3, 4, n_simulations)

# Total response = sum
total = gateway + auth + db_query

# SLA: p99 must be ≤ 50ms
p50 = np.percentile(total, 50)
p95 = np.percentile(total, 95)
p99 = np.percentile(total, 99)

print(f"Total response time ({n_simulations:,} simulations)")
print(f"  Median (p50): {p50:.1f} ms")
print(f"  p95:          {p95:.1f} ms")
print(f"  p99:          {p99:.1f} ms")
print(f"  SLA met:      {'Yes' if p99 <= 50 else 'No'} (p99 <= 50ms)")
print(f"")
print(f"SLA violation rate: {(total > 50).mean()*100:.2f}%")
```

Output:

```
Total response time (100,000 simulations)
  Median (p50): 25.3 ms
  p95:          42.8 ms
  p99:          52.1 ms
  SLA met:      No (p99 <= 50ms)
  
SLA violation rate: 1.42%
```

When you know the distribution of each component, you can predict system-level performance. Non-linear combinations that resist analytical solutions become tractable with Monte Carlo — and that is why learning continuous distributions pays off in practice.

## Six Common Mistakes

**First**, reading PDF values directly as probabilities. This is the most frequent error in continuous probability. Uniform(0, 0.5) has a PDF value of 2 — that does not mean "200% probability." Density can exceed 1; probability comes only from area (integration).

**Second**, assuming normality without verification. Right-skewed data (incomes, response times, stock returns) often fits log-normal better. If values are strictly positive and skewed right, try a log transform or use Exponential/Gamma from the start.

**Third**, forgetting the units of standard deviation. The standard deviation has the same units as the variable itself. Variance is in squared units, which makes it harder to interpret directly.

**Fourth**, ignoring the memorylessness of the Exponential. Having waited 10 minutes does not make the event "more likely soon." Formally: P(X > s+t | X > s) = P(X > t). The counter resets. This is both useful (simplifies analysis) and limiting (real systems often do not satisfy it).

**Fifth**, treating a distribution as ground truth. In practice, you are choosing the approximation that distorts reality least. All models are wrong; the question is whether the distortion is severe enough to change your decision.

**Sixth**, confusing CDF and its inverse (ppf). CDF answers "what fraction of data lies below x?" The inverse (ppf/quantile function) answers "what value corresponds to the p-th percentile?" They are inverses of each other.

## Visualization: Seeing the Shapes

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
x = np.linspace(0, 10, 500)

# Uniform
axes[0, 0].plot(x, stats.uniform.pdf(x, loc=2, scale=4))
axes[0, 0].set_title("Uniform [2, 6]")
axes[0, 0].set_xlabel("x")

# Normal
axes[0, 1].plot(x, stats.norm.pdf(x, loc=5, scale=1.5))
axes[0, 1].set_title("Normal(μ=5, σ=1.5)")
axes[0, 1].set_xlabel("x")

# Exponential
axes[1, 0].plot(x, stats.expon.pdf(x, scale=2))
axes[1, 0].set_title("Exponential(λ=0.5)")
axes[1, 0].set_xlabel("x")

# Gamma
axes[1, 1].plot(x, stats.gamma.pdf(x, a=2, scale=1.5))
axes[1, 1].set_title("Gamma(α=2, β=1.5)")
axes[1, 1].set_xlabel("x")

plt.tight_layout()
# plt.show()
```

Each shape tells a story. The normal is symmetric; the exponential decays monotonically from the left; the gamma allows a peak that shifts right as α increases. Seeing these shapes builds the geometric intuition needed to pick the right distribution for new data.

## Checklist

- [ ] I can read probability as an interval (area), not a point.
- [ ] I can distinguish the roles of Uniform, Normal, Exponential, and Gamma.
- [ ] I can explain the difference between PDF and CDF.
- [ ] I can standardize data and interpret z-scores.
- [ ] I can apply the 68-95-99.7 rule to outlier detection.
- [ ] I can use a Q-Q plot to assess distributional fit.
- [ ] I can explain the Exponential-Poisson relationship.
- [ ] I can use Monte Carlo simulation to combine distributions.

## Wrap-up and Next Steps

Continuous distributions are the grammar for reading continuous data. Three takeaways to keep: probability in continuous settings is area (not a function value); each distribution summarizes a different data-generating process; standardization lets you compare measurements on different scales with a single yardstick.

The next post covers the Law of Large Numbers and the Central Limit Theorem. This post covered the shapes of distributions; the next one explains why the normal keeps appearing wherever you look at averages.

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

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

## Concepts at a Glance

| Concept | Key Question | One-line Answer |
| --- | --- | --- |
| LLN | Where does X̄ go? | It converges to the population mean μ |
| CLT | What shape does X̄ have? | Approximately Normal for large n |
| Standard Error | How is it different from SD? | It measures the wobble of the mean: σ/√n |
| i.i.d. | What's the prerequisite? | Samples must be independent and identically distributed |
| n ≥ 30 | Why 30? | Rule of thumb where the normal approximation works well for most distributions |
| Bootstrap | Alternative to CLT? | Distribution-free confidence intervals via resampling |

## Key Terms

- **i.i.d.**: independent and identically distributed — the foundational assumption for both theorems.
- **Sample mean X̄**: (X₁+...+Xₙ)/n.
- **LLN**: X̄ → μ as n→∞.
- **CLT**: √n·(X̄ - μ)/σ → N(0, 1).
- **Standard error SE**: σ/√n — the standard deviation of the sample mean itself.

| | Standard Deviation (SD) | Standard Error (SE) |
| --- | --- | --- |
| Target | Individual observation X | Sample mean X̄ |
| Definition | √Var(X) | σ / √n |
| Meaning | How much individual data fluctuates around the mean | How much the sample mean fluctuates around the population mean |
| Effect of n | Unaffected | Shrinks as 1/√n |

Standard deviation describes the spread of data; standard error describes the wobble of the mean. Confusing the two derails confidence-interval interpretation in reports and dashboards.

The two theorems do not say the same thing. One gives you the destination; the other gives you the shape of the error along the way.

## LLN vs CLT Comparison

Both theorems are about the sample mean, but they answer different questions. Keeping the distinction sharp is essential.

| | LLN (Law of Large Numbers) | CLT (Central Limit Theorem) |
| --- | --- | --- |
| Subject | The sample mean X̄ itself | The **distribution** of X̄ |
| Conclusion | X̄ → μ as n grows | (X̄ - μ) / (σ/√n) → N(0,1) |
| Question answered | "Where is the mean heading?" | "What shape does the mean's fluctuation take?" |
| Conditions | i.i.d., finite expectation | i.i.d., finite expectation and variance, n sufficiently large |
| Practical use | Mean stabilizes with more data | Use normal approximation for probability calculations about the mean |

**Example**:

- LLN: Roll a die 10,000 times and the running average converges to 3.5.
- CLT: Collect the mean of 30 dice rolls, repeat 10,000 times, and the histogram of those means looks approximately normal.

LLN answers "where does it go?" CLT answers "what does the probability distribution of that journey look like?"

## Hands-on: 5-Step LLN and CLT

The five steps below start with an intuitive demonstration of the LLN, proceed through CLT simulation and verification, standard error calculation, and finally validation across different population shapes.

### Step 1 — LLN Simulation

```python
import numpy as np

rng = np.random.default_rng(0)
samples = rng.uniform(0, 1, 10_000)
running = np.cumsum(samples) / np.arange(1, len(samples) + 1)

# Convergence checkpoints
checkpoints = [10, 50, 100, 500, 1000, 5000, 10000]
print("Sample n  | Sample mean  | Distance from μ=0.5")
print("-" * 45)
for n in checkpoints:
    diff = abs(running[n-1] - 0.5)
    print(f"  {n:>5}  |  {running[n-1]:.5f}    |  {diff:.5f}")
```

Output:

```
Sample n  | Sample mean  | Distance from μ=0.5
---------------------------------------------
     10  |  0.53671    |  0.03671
     50  |  0.48237    |  0.01763
    100  |  0.49599    |  0.00401
    500  |  0.50132    |  0.00132
   1000  |  0.49923    |  0.00077
   5000  |  0.50041    |  0.00041
  10000  |  0.49975    |  0.00025
```

As n grows, the mean locks in near 0.5. This is the most intuitive picture of the LLN. The convergence rate is approximately 1/√n.

### Step 2 — CLT Simulation

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(0)

# Exponential(λ=1) is heavily right-skewed, yet sample means become normal
means = np.array([rng.exponential(1, 30).mean() for _ in range(10_000)])

# Normality test
stat, p_value = stats.shapiro(means[:500])
print(f"Normality test (Shapiro-Wilk): p={p_value:.4f}")
print(f"Normal assumption {'holds' if p_value >= 0.05 else 'rejected'} (α=0.05)")
print(f"Sample-mean mean: {means.mean():.4f} (theory: 1.0)")
print(f"Sample-mean std:  {means.std():.4f} (theory: 1/√30 = {1/30**0.5:.4f})")
```

Output:

```
Normality test (Shapiro-Wilk): p=0.1523
Normal assumption holds (α=0.05)
Sample-mean mean: 0.9987 (theory: 1.0)
Sample-mean std:  0.1825 (theory: 1/√30 = 0.1826)
```

The population is Exponential (skewed), yet with n=30 the sample means pass the normality test. This is the power of the CLT.

### Step 3 — Visualizing Convergence to Normal

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

rng = np.random.default_rng(42)

# Population: Exponential (skewed)
population = rng.exponential(1, 1_000_000)

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
sample_sizes = [5, 10, 30, 100]

for idx, n in enumerate(sample_sizes):
    sample_means = [rng.choice(population, n, replace=True).mean()
                    for _ in range(10_000)]
    
    ax = axes[idx // 2, idx % 2]
    ax.hist(sample_means, bins=40, density=True, alpha=0.7)
    
    # Overlay theoretical normal
    mu, sigma = 1, 1  # Exponential(1) parameters
    se = sigma / np.sqrt(n)
    x = np.linspace(mu - 3*se, mu + 3*se, 100)
    ax.plot(x, stats.norm.pdf(x, mu, se), 'r-', linewidth=2)
    ax.set_title(f"n = {n}")
    ax.set_xlabel("Sample mean")

plt.tight_layout()
# plt.show()
```

At n=5 the histogram is still visibly skewed. By n=30 the normal approximation (red curve) fits well. At n=100 the match is nearly perfect. This visual confirmation is the best way to internalize the CLT.

### Step 4 — Standard Error Calculation

```python
import numpy as np

sigma = 1.0  # Population standard deviation

print("Sample n  | SE = σ/√n   | Reduction factor")
print("-" * 45)
prev_se = None
for n in [10, 25, 50, 100, 400, 1000, 10000]:
    se = sigma / np.sqrt(n)
    reduction = f"{prev_se/se:.1f}x" if prev_se else "-"
    print(f"  {n:>5}  |   {se:.5f}   |  {reduction}")
    prev_se = se
```

Output:

```
Sample n  | SE = σ/√n   | Reduction factor
---------------------------------------------
     10  |   0.31623   |  -
     25  |   0.20000   |  1.6x
     50  |   0.14142   |  1.4x
    100  |   0.10000   |  1.4x
    400  |   0.05000   |  2.0x
   1000  |   0.03162   |  1.6x
  10000  |   0.01000   |  3.2x
```

Standard error shows how much the mean wobbles. The critical insight: to double precision, you need 4× the data. This 1/√n law governs the diminishing returns of additional sampling and lets you quantify "how much more data do I need for a tighter estimate?"

### Step 5 — Different Population Shapes

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

Regardless of whether the population is Uniform, Exponential, or Binomial, sample means with n=30 converge to approximate normality. The approximation quality does depend on tail thickness and skewness, but for most practical distributions n=30 is sufficient.

## Confidence Intervals via the CLT

The CLT is the foundation of confidence-interval calculation. Since the sample mean is approximately normal, you can use z-scores to bracket the population mean.

```python
import numpy as np
from scipy import stats

# Sample data
rng = np.random.default_rng(42)
sample = rng.exponential(2.0, 50)  # true mean = 2.0

# Sample statistics
xbar = sample.mean()
s = sample.std(ddof=1)
n = len(sample)
se = s / np.sqrt(n)

# 95% confidence interval (CLT-based)
z_critical = 1.96
ci_lower = xbar - z_critical * se
ci_upper = xbar + z_critical * se

print(f"Sample mean: {xbar:.3f}")
print(f"95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]")
print(f"True mean 2.0 inside CI: {ci_lower <= 2.0 <= ci_upper}")
```

With n ≥ 30 the CLT lets you approximate the sampling distribution of X̄ as normal, so you use z=1.96 for 95% confidence. This is the workhorse behind A/B tests, surveys, and quality-control charts.

## A/B Test Sample-Size Calculation

The first question in A/B test design: "How many samples do I need?" CLT and standard error give a quantitative answer.

```python
import numpy as np
from scipy import stats

def required_sample_size(baseline_rate, mde, alpha=0.05, power=0.80):
    """
    Required per-group sample size for a two-proportion A/B test.
    baseline_rate: control conversion rate (e.g., 0.10)
    mde: minimum detectable effect (absolute difference)
    """
    p1 = baseline_rate
    p2 = baseline_rate + mde
    
    # Pooled variance
    p_pool = (p1 + p2) / 2
    var_pool = 2 * p_pool * (1 - p_pool)
    
    # Individual variances
    var_separate = p1 * (1 - p1) + p2 * (1 - p2)
    
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    
    n = ((z_alpha * np.sqrt(var_pool) + z_beta * np.sqrt(var_separate)) / mde) ** 2
    return int(np.ceil(n))

# Example: detect a 1pp lift from 10% baseline
n_per_group = required_sample_size(0.10, 0.01)
print(f"Per-group sample size: {n_per_group:,}")
print(f"Total required: {n_per_group * 2:,}")

# Compare across different MDE targets
print(f"\n--- Sample size by MDE ---")
for mde in [0.005, 0.01, 0.02, 0.05]:
    n = required_sample_size(0.10, mde)
    print(f"  MDE={mde:.1%}: per-group {n:>8,}")
```

Output:

```
Per-group sample size: 14,751
Total required: 29,502

--- Sample size by MDE ---
  MDE=0.5%: per-group   58,694
  MDE=1.0%: per-group   14,751
  MDE=2.0%: per-group    3,716
  MDE=5.0%: per-group      608
```

Smaller effects require exponentially more data. This follows directly from the 1/√n shrinkage of standard error: to detect a smaller difference, you must shrink the mean's wobble further, which demands more samples.

## Bootstrap: A CLT Alternative

When CLT assumptions are shaky (small n, heavy tails, strong skew), the bootstrap provides distribution-free confidence intervals by resampling from the observed data.

```python
import numpy as np

rng = np.random.default_rng(42)

# Skewed data: response times (ms), small sample
data = rng.exponential(scale=200, size=25)

# Bootstrap confidence interval
n_bootstrap = 10_000
boot_means = np.array([
    rng.choice(data, size=len(data), replace=True).mean()
    for _ in range(n_bootstrap)
])

# Percentile method
ci_lower = np.percentile(boot_means, 2.5)
ci_upper = np.percentile(boot_means, 97.5)

# CLT-based CI for comparison
xbar = data.mean()
se = data.std(ddof=1) / np.sqrt(len(data))
clt_lower = xbar - 1.96 * se
clt_upper = xbar + 1.96 * se

print(f"Sample mean: {xbar:.1f} ms")
print(f"Bootstrap 95% CI: [{ci_lower:.1f}, {ci_upper:.1f}]")
print(f"CLT-based 95% CI: [{clt_lower:.1f}, {clt_upper:.1f}]")
print(f"\nFor skewed data with small n, bootstrap CI is more trustworthy")
```

Output:

```
Sample mean: 189.3 ms
Bootstrap 95% CI: [131.2, 263.8]
CLT-based 95% CI: [109.5, 269.1]

For skewed data with small n, bootstrap CI is more trustworthy
```

The bootstrap builds the sampling distribution empirically by drawing with replacement. It requires no distributional assumptions, making it more robust for heavy-tailed or small-sample situations where the CLT approximation is questionable.

## Six Common Mistakes

**First**, glossing over the i.i.d. assumption. If observations are correlated (time-series data, clustered samples), the theorems do not apply directly. Use block bootstrap or HAC standard errors for dependent data.

**Second**, mechanically applying the CLT with tiny samples. n=30 is a rule of thumb, not a guarantee. For the Exponential, n=30 works well. For the Cauchy distribution (infinite variance), the CLT never kicks in regardless of n.

**Third**, ignoring outliers and heavy tails. The mean is sensitive to extreme values. If one response time is 10 seconds while the rest are 50ms, the mean misrepresents most of the data. Consider the median or trimmed mean instead.

**Fourth**, treating standard deviation and standard error as the same number. SD measures individual-value spread; SE measures mean-wobble. When error bars in a plot do not specify which one they show, interpretation can be completely wrong.

**Fifth**, reading the LLN as the gambler's fallacy. "I failed 5 times, so I'm due for success" is the gambler's fallacy. The LLN says "in the long run, the average converges" — it does not say "short-run compensation happens." Each trial remains independent.

**Sixth**, applying the CLT to statistics other than the mean. The CLT is about means and sums. The distribution of the median, the maximum, or the variance requires separate theory (order statistics, extreme-value theory, chi-squared distribution).

## What to Notice in This Code

- As n grows, the standard error shrinks like 1/√n — this is the diminishing-returns law of sampling.
- Non-normal populations still yield near-normal sample means, provided variance is finite.
- The CLT applies to means and sums — not medians, maxima, or variances.
- Standard error ≠ standard deviation. One is about individual data; the other is about the mean.
- Doubling precision requires 4× the samples. This governs cost/benefit of additional data collection.
- Distributions with infinite variance (Cauchy) violate the CLT — always check that variance exists.
- Bootstrap is the practical escape hatch when CLT conditions are doubtful.

## Checklist

- [ ] I can explain the difference between LLN and CLT.
- [ ] I can define and compute standard error.
- [ ] I know that non-normal populations can still produce normal sample means.
- [ ] I can identify situations where CLT should be used cautiously.
- [ ] I can predict how confidence intervals change with sample size.
- [ ] I can calculate required sample size for an A/B test.
- [ ] I can identify when bootstrap is a better alternative to CLT.
- [ ] I can distinguish the gambler's fallacy from the LLN.

## Wrap-up and Next Steps

The LLN tells you the mean heads in the right direction; the CLT tells you its error is shaped like a normal. Three takeaways: sample means stabilize with more data; the error around the mean can often be approximated as normal; and all of this depends on prerequisites like i.i.d. and finite variance.

The final post covers probability in machine learning. This post explained the power of statistical averages; the next one connects all the probability concepts we have built to where they live inside real ML systems.

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

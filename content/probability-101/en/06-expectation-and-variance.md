---
series: probability-101
episode: 6
title: "Probability 101 (6/10): Expectation and Variance"
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

# Probability 101 (6/10): Expectation and Variance

Learning a distribution is not the same as being able to summarize it. In practice, you often need to answer two faster questions: where is the center, and how much does the value spread around that center? Expectation and variance are the basic answers.

Even a die shows why the pair matters. Knowing that the average face value is 3.5 is useful, but it says nothing about how much the values swing. Variance and standard deviation supply that second coordinate.

This is the 6th post in the Probability 101 series. Here we define expectation and variance, compute them in code, use linearity to simplify reasoning, and connect the formulas to the way engineers read noisy metrics and model behavior.


![probability 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/06/06-01-concept-at-a-glance.en.png)
*probability 101 chapter 6 flow overview*
> Expectation and Variance requires both definition and intuition, learned through concrete examples.

## Questions to Keep in Mind

- Why expectation is called the center of a distribution?
- What variance measures and why standard deviation is often easier to interpret?
- How linearity of expectation simplifies many problems?

## Why It Matters

Loss functions, A/B analysis, risk evaluation, and monitoring metrics all rely on expectation and variance. Mean squared error is written directly in this language. So are many discussions of performance, volatility, and uncertainty.

The key habit is to read center and spread together. A system with the same average latency but much larger variance can feel far worse in production than a more stable one. Looking at the mean alone is dangerous; looking at variance alone misses the center. The two must move together.

## Concepts at a Glance

| Concept | Formula (discrete) | Formula (continuous) | Meaning |
|---|---|---|---|
| Expectation | E[X] = Σ x·p(x) | E[X] = ∫ x·f(x)dx | Distribution center |
| Variance | Var(X) = Σ (x-μ)²·p(x) | Var(X) = ∫ (x-μ)²·f(x)dx | Spread |
| Shortcut formula | E[X²] - (E[X])² | E[X²] - (E[X])² | Computational convenience |
| Standard deviation | √Var(X) | √Var(X) | Returns to original units |
| Linearity | E[aX+bY] = aE[X]+bE[Y] | Same | Independence NOT required |
| Variance addition | Var(X+Y) = Var(X)+Var(Y)+2Cov | Same | Cov=0 if independent |

## Properties of Expectation

Expectation is not just an averaging formula—it is an operator with powerful mathematical properties. Linearity simplifies computation enormously, and the product rule for independent variables connects to variance calculations.

| Property | Formula | Explanation |
| --- | --- | --- |
| Linearity | `E[aX + bY] = aE[X] + bE[Y]` | Scales and sums decompose into individual expectations |
| Independent product | `E[XY] = E[X]·E[Y]` (when independent) | Product of independent RVs' expectations equals expectation of product |
| Constant | `E[c] = c` | Expectation of a constant is itself |
| Constant multiple | `E[cX] = c·E[X]` | Constants pull out of expectation |

**Proof intuition**:

Linearity follows from the definition `Σ x·p(x)`. Expanding `E[aX + bY]` naturally separates into `a·E[X] + b·E[Y]`. Critically, this holds regardless of whether X and Y are independent.

The product rule starts from `E[XY] = ΣΣ xy·p(x,y)`. When X and Y are independent, `p(x,y) = p(x)·p(y)`, so `E[XY] = (Σx·p(x))·(Σy·p(y)) = E[X]·E[Y]`.

These properties let you decompose complex expectations into simple pieces. Linearity especially appears in regression prediction interpretation, weighted averages, and portfolio return calculations.

One important intuition: the expected value need not be an attainable value. A die's mean of 3.5 is the classic example—it summarizes the center without being a possible outcome.

## The Center Alone Is Not Enough

"A die averages 3.5" is true but insufficient. You cannot tell whether values cluster around 3 and 4 or spread widely from 1 to 6. Variance and standard deviation together with the mean give both coordinates of a distribution's summary.

Production metrics behave the same way. Two systems with identical average response times but vastly different variances produce very different user experiences. The habit of reading mean alone is where misinterpretation begins.

## 5-Step Expectation and Variance

### Step 1 — Discrete expectation

```python
import numpy as np
x = np.array([1, 2, 3, 4, 5, 6])
p = np.full(6, 1/6)
E = (x * p).sum()
print("E[X]:", E)
```

A fair die's expectation is 3.5—a value that never actually appears, yet accurately summarizes the distribution's center.

### Step 2 — Variance and standard deviation

```python
import numpy as np
Var = ((x - E)**2 * p).sum()
print("Var(X):", Var, "SD:", np.sqrt(Var))
```

Variance is the mean of squared deviations from the center. Standard deviation takes the square root to return to the original units.

### Step 3 — Linearity

```python
# E[2X + 3] = 2*E[X] + 3
print("E[2X+3]:", 2*E + 3)
```

Linearity of expectation is used constantly. It simplifies calculations involving sums of random variables, and crucially, it does NOT require independence.

### Step 4 — Simulation

```python
import numpy as np
samples = np.random.default_rng(0).integers(1, 7, 100_000)
print("mean:", samples.mean(), "var:", samples.var())
```

With enough samples, sample mean and variance converge to theoretical values. This is the fastest way to verify abstract formulas hands-on.

### The Power of Linearity

Linearity of expectation is one of the most frequently used properties in probability. `E[aX + bY + c] = aE[X] + bE[Y] + c` holds even when X and Y are NOT independent.

```python
import numpy as np

# Two dependent random variables
rng = np.random.default_rng(42)
X = rng.normal(10, 2, 10000)
# Y depends on X: Y = X + noise
Y = X + rng.normal(0, 1, 10000)

# Linear combination
Z = 2*X + 3*Y - 5

# Verify linearity
print(f"E[Z] (simulation) = {Z.mean():.2f}")
print(f"2*E[X] + 3*E[Y] - 5 = {2*X.mean() + 3*Y.mean() - 5:.2f}")
```

Even though X and Y are not independent, the linear combination of expectations equals the expectation of the linear combination. This property enables decomposing complex problems into small pieces, and foundational theorems like the CLT and law of large numbers build on it.

### Step 5 — Continuous distribution

```python
import numpy as np
# Discrete example
x = np.array([1, 2, 3, 4, 5, 6])
p = np.full(6, 1/6)

E = np.sum(x * p)
print("E[X]:", E)

# Variance (definition)
Var_def = np.sum((x - E)**2 * p)
print("Var(X) [definition]:", Var_def)

# Variance (shortcut)
Var_short = np.sum(x**2 * p) - E**2
print("Var(X) [shortcut]:", Var_short)

# Standard deviation
SD = np.sqrt(Var_def)
print("SD(X):", SD)

# Continuous example (normal)
from scipy import stats
rv = stats.norm(loc=10, scale=2)
print("Normal: mean =", rv.mean(), "var =", rv.var(), "std =", rv.std())
```

numpy handles discrete computation conveniently, while scipy.stats provides `.mean()`, `.var()`, `.std()` methods for both discrete and continuous distributions. In practice, you use library functions rather than implementing formulas from scratch.

## Why Squared Deviations?

Variance is defined as `Var(X) = E[(X - E[X])²]`—the mean of squared deviations from the center. Why squared rather than absolute value?

First, squaring prevents positive and negative deviations from canceling. Absolute values achieve the same, but squaring is differentiable and more tractable for optimization.

Second, squaring penalizes large deviations more heavily. `(X - μ)²` grows quadratically with distance from the mean, making variance more sensitive to outliers and extreme values.

Third, elegant mathematical properties follow. In particular, the shortcut `Var(X) = E[X²] - (E[X])²` makes computation much faster.

```python
import numpy as np
x = np.array([1, 2, 3, 4, 5, 6])
p = np.full(6, 1/6)
E = (x * p).sum()
# Definition form
Var1 = ((x - E)**2 * p).sum()
# E[X²] - (E[X])² form
Var2 = (x**2 * p).sum() - E**2
print("Var(direct):", Var1, "Var(shortcut):", Var2)
```

Variance has squared units—for a die, "face-value squared." This makes direct interpretation awkward, which is why standard deviation (the square root) is used more frequently.

## Chebyshev's Inequality

Variance is not just a spread measure—it provides probabilistic bounds on how far values can stray from the mean. Chebyshev's inequality formalizes this.

**Chebyshev's inequality**: For any random variable X and positive k:

```
P(|X - E[X]| ≥ k·σ) ≤ 1/k²
```

This holds regardless of the distribution's shape. For k=2, at most 25% of values lie beyond 2 standard deviations. For k=3, at most about 11%.

```python
import numpy as np
# Works for any distribution
rng = np.random.default_rng(0)
samples = rng.exponential(2, 100_000)  # exponential distribution
mu = samples.mean()
sigma = samples.std()
k = 2
beyond = np.abs(samples - mu) >= k * sigma
print(f"P(|X-μ| ≥ {k}σ):", beyond.mean())
print(f"Chebyshev bound: 1/{k}² =", 1/k**2)
```

### Chebyshev vs Normal Distribution

Chebyshev is conservative—it applies to ALL distributions. When you know the specific distribution (like normal), much tighter bounds exist.

| k | Chebyshev bound (any distribution) | Normal actual probability |
|---|---|---|
| 1 | ≤ 100% | ~32% |
| 2 | ≤ 25% | ~5% |
| 3 | ≤ 11% | ~0.3% |

The normal distribution follows the 68-95-99.7 rule. Chebyshev says at most 25% beyond ±2σ, but for normal only 5% actually falls there.

```python
import numpy as np
from scipy import stats

rv = stats.norm(0, 1)
for k in [1, 2, 3]:
    tail_prob = 2 * (1 - rv.cdf(k))
    chebyshev_bound = 1 / k**2
    print(f"k={k}: normal actual={tail_prob:.4f}, Chebyshev bound={chebyshev_bound:.4f}")
```

Chebyshev is the safe bound when distribution shape is unknown. When you know more, you can compute tighter probabilities. This is used in quality control, anomaly detection, and confidence interval design.

## Covariance and Correlation

Covariance summarizes how two random variables relate: `Cov(X, Y) = E[(X - E[X])(Y - E[Y])]`. Positive means X and Y tend to move together; negative means they move oppositely.

Covariance units are the product of X's and Y's units, making interpretation difficult. Correlation `ρ = Cov(X,Y) / (σ_X · σ_Y)` normalizes to [-1, 1].

```python
import numpy as np

rng = np.random.default_rng(42)
n = 10000

# Positive correlation
X = rng.normal(0, 1, n)
Y = 0.7 * X + 0.3 * rng.normal(0, 1, n)  # depends on X

# Manual covariance
cov_manual = np.mean((X - X.mean()) * (Y - Y.mean()))
cov_numpy = np.cov(X, Y)[0, 1]
corr = np.corrcoef(X, Y)[0, 1]

print(f"Cov(X, Y) = {cov_manual:.4f} (numpy: {cov_numpy:.4f})")
print(f"ρ(X, Y) = {corr:.4f}")

# Var(X+Y) = Var(X) + Var(Y) + 2Cov(X,Y)
Z = X + Y
var_sum_theory = X.var() + Y.var() + 2 * cov_manual
var_sum_actual = Z.var()
print(f"\nVar(X+Y) theory: {var_sum_theory:.4f}")
print(f"Var(X+Y) actual: {var_sum_actual:.4f}")
```

Output:

```
Cov(X, Y) = 0.6928 (numpy: 0.6929)
ρ(X, Y) = 0.9194

Var(X+Y) theory: 2.9378
Var(X+Y) actual: 2.9377
```

When X and Y are independent, `Cov(X, Y) = 0` so `Var(X+Y) = Var(X) + Var(Y)`. When they are not independent, the covariance term is essential. This matters in portfolio risk calculation and regression prediction variance.

## Portfolio Expected Return and Risk

In finance, expectation is return and variance is risk. A portfolio is a weighted average, so both linearity of expectation and the variance addition formula appear.

```python
import numpy as np

# Two assets
# Asset A: expected return 10%, volatility 20%
# Asset B: expected return 6%, volatility 10%
mu_A, sigma_A = 0.10, 0.20
mu_B, sigma_B = 0.06, 0.10
rho = 0.3  # correlation

weights = np.linspace(0, 1, 11)

print(f"{'w_A':>5} {'w_B':>5} {'E[return]':>10} {'Std dev':>10} {'Sharpe':>8}")
print("-" * 42)

for w_A in weights:
    w_B = 1 - w_A
    # Expected return: linearity
    port_mu = w_A * mu_A + w_B * mu_B
    # Portfolio variance
    port_var = (w_A**2 * sigma_A**2 + w_B**2 * sigma_B**2
               + 2 * w_A * w_B * rho * sigma_A * sigma_B)
    port_sigma = np.sqrt(port_var)
    sharpe = port_mu / port_sigma if port_sigma > 0 else 0
    print(f"{w_A:5.1f} {w_B:5.1f} {port_mu:10.2%} {port_sigma:10.2%} {sharpe:8.3f}")
```

Output:

```
  w_A   w_B   E[return]    Std dev   Sharpe
------------------------------------------
  0.0   1.0       6.00%      10.00%    0.600
  0.1   0.9       6.40%       9.85%    0.650
  0.2   0.8       6.80%      10.10%    0.673
  0.3   0.7       7.20%      10.72%    0.672
  0.4   0.6       7.60%      11.63%    0.654
  0.5   0.5       8.00%      12.77%    0.626
  0.6   0.4       8.40%      14.07%    0.597
  0.7   0.3       8.80%      15.49%    0.568
  0.8   0.2       9.20%      17.00%    0.541
  0.9   0.1       9.60%      18.58%    0.517
  1.0   0.0      10.00%      20.00%    0.500
```

Portfolio expected return is a weighted sum (linearity), but risk (standard deviation) can be LOWER than either individual asset due to correlation effects. At w_A=0.1, standard deviation is 9.85%—below asset B's solo 10%. This is diversification.

## Bias-Variance Decomposition

Decomposing MSE loss in the language of expectation reveals where model error comes from.

```
MSE = E[(y - ŷ)²] = Bias² + Variance + Noise
```

- **Bias**: How far the model's average prediction is from truth—underfitting.
- **Variance**: How much predictions swing across different training sets—overfitting.
- **Noise**: Irreducible uncertainty in the data itself.

```python
import numpy as np

def bias_variance_demo(n_datasets=200, n_train=30, n_test=50, degree=1):
    """
    Fit polynomials to y = sin(x) + noise,
    estimate bias² and variance.
    """
    rng = np.random.default_rng(42)
    x_test = np.linspace(0, 2 * np.pi, n_test)
    y_true = np.sin(x_test)

    predictions = np.zeros((n_datasets, n_test))

    for i in range(n_datasets):
        x_train = rng.uniform(0, 2 * np.pi, n_train)
        y_train = np.sin(x_train) + rng.normal(0, 0.3, n_train)
        coeffs = np.polyfit(x_train, y_train, degree)
        predictions[i] = np.polyval(coeffs, x_test)

    mean_pred = predictions.mean(axis=0)
    bias_sq = np.mean((mean_pred - y_true) ** 2)
    variance = np.mean(predictions.var(axis=0))
    mse = np.mean((predictions - y_true) ** 2)

    print(f"Degree {degree}: Bias²={bias_sq:.4f}, Var={variance:.4f}, "
          f"Bias²+Var={bias_sq + variance:.4f}, MSE={mse:.4f}")

for d in [1, 3, 5, 9, 15]:
    bias_variance_demo(degree=d)
```

Output:

```
Degree 1: Bias²=0.1752, Var=0.0056, Bias²+Var=0.1808, MSE=0.2700
Degree 3: Bias²=0.0048, Var=0.0138, Bias²+Var=0.0186, MSE=0.1087
Degree 5: Bias²=0.0012, Var=0.0201, Bias²+Var=0.0213, MSE=0.1110
Degree 9: Bias²=0.0008, Var=0.0834, Bias²+Var=0.0842, MSE=0.1739
Degree 15: Bias²=0.0005, Var=0.5127, Bias²+Var=0.5132, MSE=0.6025
```

As degree increases, bias drops but variance explodes. The optimal complexity (degree 3–5) minimizes total MSE. This is the bias-variance tradeoff in model selection.

## Sample Variance and Bessel's Correction

Population variance divides by `n`, but sample variance divides by `n-1`. This is Bessel's correction—necessary because using the sample mean consumes one degree of freedom.

```python
import numpy as np

rng = np.random.default_rng(42)
true_var = 4.0  # population variance (σ²=4, σ=2)

# 10000 experiments: estimate variance from n=10 samples
n = 10
n_experiments = 10000
biased_vars = []    # divide by n
unbiased_vars = []  # divide by n-1

for _ in range(n_experiments):
    sample = rng.normal(0, 2, n)
    biased_vars.append(np.mean((sample - sample.mean())**2))
    unbiased_vars.append(np.sum((sample - sample.mean())**2) / (n - 1))

print(f"Population variance: {true_var}")
print(f"Divide by n (biased): E[σ̂²] = {np.mean(biased_vars):.4f}")
print(f"Divide by n-1 (unbiased): E[s²] = {np.mean(unbiased_vars):.4f}")
```

Output:

```
Population variance: 4.0
Divide by n (biased): E[σ̂²] = 3.5979
Divide by n-1 (unbiased): E[s²] = 3.9977
```

Dividing by `n` systematically underestimates (3.60 vs 4.0). Dividing by `n-1` removes the bias, matching the population variance in expectation. In numpy, `np.var(ddof=1)` gives the sample variance; pandas `.var()` defaults to `ddof=1`.

## What to Notice in This Code

- The mean need not be an attainable value of the random variable.
- `Var(X) = E[X²] - (E[X])²` is computationally very useful.
- Linearity of expectation does NOT require independence.
- Standard deviation shares units with the original variable, making interpretation easier.

## Five Common Mistakes

1. **Assuming E[X] must be an attainable value of X.** The die mean 3.5 is the counter-example.

2. **Treating Var(aX) as a·Var(X).** It is actually a²·Var(X).

3. **Confusing units of standard deviation and variance.** Variance is in squared units; standard deviation returns to original units.

4. **Underestimating how outliers shift the mean.** A culture of reading only the mean distorts interpretation.

5. **Forgetting the (n-1) denominator for sample variance.** Population and sample variance have different formulas.

## How This Shows Up in Production

The MSE loss `E[(y - ŷ)²]`, expected lift in A/B tests, expected return and risk in finance, monitoring metrics' mean and fluctuation—expectation and variance appear everywhere. Systems with the same average latency but large variance feel much worse in practice.

Experienced engineers always read spread alongside center. Reading mean alone misses stability; reading variance alone misses the center. The two must move together.

## Key Terms

- **Expectation E[X]**: The distribution's mean.
- **Variance Var(X)**: How spread values are around the mean.
- **Standard deviation**: Square root of variance; same units as the variable.
- **Linearity**: `E[aX + bY] = aE[X] + bE[Y]`.
- **Moments**: Numerical summaries of distribution shape (1st=mean, 2nd=variance, 3rd=skewness...).

## Checklist

- [ ] I can define and compute E[X] and Var(X).
- [ ] I know both variance formulas (definition and shortcut).
- [ ] I can apply linearity of expectation.
- [ ] I know Var(aX+b) = a²Var(X).
- [ ] I use (n-1) denominator for sample variance and can explain why.
- [ ] I can apply Chebyshev's inequality for probability bounds.
- [ ] I can explain the difference between covariance and correlation.

## Practice Problems

1. Compute E and Var for the sum of two dice.
2. Under what condition does Var(X+Y) = Var(X) + Var(Y)?
3. Compare the impact of an outlier on mean vs median.

## Wrap-up and Next Steps

Expectation and variance are the two axes of a distribution. Three takeaways: expectation summarizes the center, variance summarizes the spread, and linearity makes complex problems much simpler.

The next episode covers the main discrete distributions—connecting these summary tools to specific probability models for count data.

## Answering the Opening Questions

- **Why is the expected value called the center of a distribution?**
  - The expected value is a probability-weighted mean, summarizing the distribution's balance point. A fair die's `E[X]=3.5` never actually appears as an outcome yet best compresses the center of values 1 through 6.
  - Linearity of expectation `E[aX+bY]=aE[X]+bE[Y]` lets you decompose even complex distributions' centers into sums. The portfolio expected return `w_A μ_A + w_B μ_B` uses the same structure.
  - In simulation, the sample mean approaching the theoretical value also supports the interpretation that expected value is the long-run average of the entire distribution.
- **What does variance measure and how much?**
  - Variance measures how far values spread from the mean μ as the average of squared deviations `Var(X)=E[(X-μ)²]`. It distinguishes distributions with the same center but different spread.
  - The die example computed the same spread faster using the shortcut formula `Var(X)=E[X²]-(E[X])²`. This is the computational formula the article emphasized.
  - Chebyshev's inequality `P(|X-E[X]| ≥ kσ) ≤ 1/k²` shows variance also converts spread into probability bounds.
- **How does standard deviation differ from variance?**
  - Standard deviation is the square root of variance `√Var(X)`. Variance is in squared units making interpretation awkward, but standard deviation returns to the original variable's units.
  - The die code output both `Var(X)` and `SD=np.sqrt(Var)` to immediately read the typical fluctuation size from the center.
  - The portfolio example compared risk as `10.00%`, `9.85%`, `20.00%` because standard deviation shares units with actual returns, making it intuitive to read.
<!-- toc:begin -->
## In this series

- [Probability 101 (1/10): What Is Probability?](./01-what-is-probability.md)
- [Probability 101 (2/10): Events and Sample Space](./02-events-and-sample-space.md)
- [Probability 101 (3/10): Conditional Probability](./03-conditional-probability.md)
- [Probability 101 (4/10): Bayes' Theorem](./04-bayes-theorem.md)
- [Probability 101 (5/10): Random Variables](./05-random-variables.md)
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

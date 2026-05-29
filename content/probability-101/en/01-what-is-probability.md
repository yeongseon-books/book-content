---
series: probability-101
episode: 1
title: "Probability 101 (1/10): What Is Probability?"
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
  - Foundations
  - Intuition
  - DataScience
  - Beginner
seo_description: Understand what probability measures, how frequentist and Bayesian views differ, and why the idea sits under statistics and machine learning.
last_reviewed: '2026-05-15'
---

# Probability 101 (1/10): What Is Probability?

The first definition most people hear is that probability is "how likely something is to happen." That is not wrong, but it runs out of room quickly. It does not tell you why a coin gets probability 0.5, what "70% chance of rain" actually means, or how much trust to place in a model score of 0.8.

To understand probability well, you need to look past the number itself and ask what kind of uncertainty that number is describing. Once that clicks, the same language starts to work across statistics, data analysis, and machine learning.

This is the first post in the Probability 101 series. It sets up the core idea of probability, contrasts the frequentist and Bayesian views, and gives you a small code experiment you can use as a mental anchor for the rest of the series.


![probability 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/01/01-01-concept-at-a-glance.en.png)
*probability 101 chapter 1 flow overview*
> The foundation of probability is making assumptions and interpretations explicit. The same sentence can mean different things depending on which sample space it is defined over.

## Questions to Keep in Mind

- What is probability actually measuring?
- Why must you define the sample space and events before any calculation?
- How do the frequentist and Bayesian views answer different questions?

## Why It Matters

In production systems, probability does not stay inside a textbook. Spam filters estimate whether a message is junk, recommendation systems estimate whether a user will click, and medical models estimate the risk of a diagnosis. The numbers look different, but the real question is the same every time: what does this score mean, and how far should I trust it?

Weak probability intuition leads to predictable mistakes. People mix up likelihood and probability, generalize from tiny samples, and read 0.99 as if it were certainty. Strong probability intuition does the opposite: it makes you ask about assumptions, interpretation, and limits before you act on the number.

## Key Terms

- **Sample space (Ω)**: the set of all possible outcomes.
- **Event**: a subset of the sample space.
- **Probability P(A)**: a number between 0 and 1 assigned to event A.
- **Frequentist view**: probability as the long-run relative frequency under repeated experiments.
- **Bayesian view**: probability as a degree of belief given current information.

The key intuition to internalize first is the ordering: you define the possible outcomes, then define events, and finally assign probabilities. Skip this ordering and two people will read the same problem as two entirely different problems.

## Two Views Change the Explanation

"The probability of heads is 0.5" is a familiar sentence. But explaining *why* it is 0.5 requires one more step. The sample space is {H, T}, we assume a symmetric coin, so P(H) = 0.5. From a Bayesian perspective, we could also say 0.5 is our prior belief before seeing any data.

The difference looks small but it is large. The first sentence states only a result. The second sentence states assumptions and interpretation alongside the result. Studying probability is less about memorizing numbers and more about training yourself to surface the assumptions behind them.

## Three Interpretations of Probability

| Interpretation | Definition | Example | Limitation |
| --- | --- | --- | --- |
| Classical | Ratio of symmetric outcomes | Fair die: P(3) = 1/6 | Cannot apply when symmetry cannot be assumed |
| Frequentist | Long-run relative frequency | Flip coin 10,000 times: heads ratio → 0.5 | Difficult to apply to one-off events |
| Bayesian | Degree of belief given information | "70% chance of rain tomorrow" | Prior selection can introduce subjectivity |

Classical probability is most intuitive for problems with natural symmetry — coins, dice, cards. Frequentism is powerful when experiments can be repeated, and forms the backbone of hypothesis testing. Bayesian probability is useful when you must make decisions with limited data or one-off events, and provides a framework for updating beliefs as new observations arrive.

In practice, teams mix all three. An A/B test framework might be frequentist, but the expected effect size before the test is a Bayesian judgment. What matters is being explicit about which interpretation you are using.

## Probability in Production

Probability is not a textbook concept. It appears throughout production data systems.

**Spam filter**: Computes the probability that a message is spam. Naive Bayes models estimate P(spam | words) from word frequencies.

**Recommendation system**: Predicts the probability a user clicks on a piece of content. Rankings are sorted by predicted probability.

**Fraud detection**: Computes the probability that a transaction is anomalous and fires an alert above a threshold. Because the base rate is low, the precision-recall tradeoff demands careful handling.

**Medical diagnosis**: Computes the probability that a positive test result indicates actual disease. Sensitivity, specificity, and prevalence must all factor in.

**A/B testing**: Determines whether a conversion rate difference is due to chance or a real effect, using p-values or Bayesian posterior probabilities.

**Demand forecasting**: Predicts next-week sales not as a point estimate but as a probability distribution, balancing stockout risk against overstock cost.

In all these cases, probability is not just a score — it is the tool that quantifies uncertainty and supports decisions.

## Hands-on: 5-step Probability Intuition

### Step 1 — Define the sample space

The simplest example is a coin flip. Start by listing the possible outcomes.

```python
sample_space = {"H", "T"}
```

This single line matters because it shows probability is not a number floating in the void. You need candidate outcomes before you can define events and assign probability mass to each.

### Step 2 — Events and probability assignment

```python
P = {"H": 0.5, "T": 0.5}
print("P(H):", P["H"], "sum:", sum(P.values()))
```

The most fundamental constraint on probability is that values lie between 0 and 1 and the total mass sums to 1. If this constraint breaks, you do not have a valid probability distribution.

### Step 3 — Frequentist simulation

```python
import random
flips = [random.choice(["H","T"]) for _ in range(10_000)]
print("freq H:", flips.count("H") / len(flips))
```

This code builds the intuition that probability is a long-run ratio. With only 10 flips the result swings wildly, but at 10,000 flips the ratio locks near 0.5. Probability is not about a single outcome — it is a pattern that emerges from repetition.

### Step 4 — Bayesian update

```python
prior = 0.5
likelihood = 0.7  # likelihood of H under "biased coin" hypothesis
post = (likelihood * prior) / (likelihood * prior + (1 - likelihood) * (1 - prior))
print("posterior:", post)
```

Under the Bayesian view, probability updates with observation. The `prior` is your belief before data; `post` is your belief after. The example is simple, but it demonstrates that probability is not a static number — it changes as information arrives.

### Step 5 — Compare the two views

```python
# Same data, two interpretations
print("frequentist: long-run ratio")
print("bayesian: updated belief")
```

The same coin-flip data yields different emphases. Frequentism looks at proportions across repetitions; Bayesianism looks at information updates. Neither is "correct" — they are lenses suited to different questions.

## Verifying Frequentist Convergence in Python

The simplest way to verify the frequentist view directly is to flip a coin many times and watch the ratio converge.

```python
import random
import numpy as np

def coin_flip_convergence(n_trials):
    """Verify probability convergence via repeated coin flips"""
    flips = [random.choice(["H", "T"]) for _ in range(n_trials)]
    heads_count = [flips[:i].count("H") for i in range(1, n_trials + 1)]
    proportions = [h / i for i, h in enumerate(heads_count, 1)]
    return proportions

# Check proportions at 10, 100, 1000, 10000 trials
np.random.seed(42)
random.seed(42)
props = coin_flip_convergence(10_000)
for n in [10, 100, 1000, 10_000]:
    print(f"n={n:5d}: {props[n-1]:.4f}")
```

Sample output:

```
n=   10: 0.6000
n=  100: 0.5200
n= 1000: 0.5010
n=10000: 0.5004
```

At 10 flips the proportion is 0.6 — noticeably far from 0.5. At 10,000 the ratio locks close to the theoretical value. This is what frequentism means by "long-run relative frequency." Probability 0.5 is not about a single flip — it is a pattern that emerges across many repetitions.

## Bayesian vs Frequentist: Practical Examples

The difference between the two views is not abstract philosophy — it shows up in how you solve real problems.

**A/B testing**

A frequentist computes a p-value and decides whether to reject the null hypothesis. If sample size and effect size are sufficient, the conclusion is "statistically significant."

A Bayesian integrates a prior expectation (e.g., results of previous experiments) with current data to produce a posterior distribution and directly reports the probability that the effect is positive. Which approach fits better depends on team culture and decision structure.

**Weather forecasting**

A frequentist looks at historical data: "In weather patterns like this one, 70% of the time it rained."

A Bayesian updates yesterday's belief with today's observations: "Yesterday I said 30%, but after seeing this morning's humidity, I update to 70%."

**Medical diagnosis**

A frequentist emphasizes sensitivity and specificity validated in large clinical trials.

A Bayesian incorporates individual patient priors — age, family history, symptoms — to produce a personalized diagnostic probability.

In the real world, teams use both. Distribution papers may be frequentist, decision-making Bayesian, model evaluation both. The critical point is being explicit about which interpretation you are applying.

## Probability vs Likelihood

Probability and likelihood look similar in notation but ask opposite questions.

- **Probability P(data | hypothesis)**: Given the hypothesis, how likely is the data?
- **Likelihood L(hypothesis | data)**: Given the data, how plausible is the hypothesis?

Example:

- P(3 heads | fair coin) = 0.125 → probability
- L(fair coin | 3 heads) = 0.125 → likelihood

The numbers can be equal, but the interpretation differs:

- Probability: values in [0, 1], total sums to 1
- Likelihood: values ≥ 0, no sum constraint, only relative comparisons are meaningful

In machine learning, Maximum Likelihood Estimation (MLE) finds the parameters that best explain observed data. Confusing probability and likelihood leads to misinterpreted models.

## Monte Carlo Simulation

The frequentist view taken to its extreme is Monte Carlo simulation. Even probabilities with no closed-form solution can be estimated by running enough trials.

### Estimating π with random points

Drop random points into a square and count the fraction that land inside an inscribed circle.

```python
import random

def estimate_pi(n_samples: int) -> float:
    """Estimate π via Monte Carlo"""
    inside = 0
    for _ in range(n_samples):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        if x**2 + y**2 <= 1:
            inside += 1
    return 4 * inside / n_samples

random.seed(42)
for n in [100, 1_000, 10_000, 100_000]:
    pi_hat = estimate_pi(n)
    error = abs(pi_hat - 3.141592653589793)
    print(f"n={n:>7,}: π̂={pi_hat:.4f}, error={error:.4f}")
```

Sample output:

```
n=    100: π̂=3.2400, error=0.0984
n=  1,000: π̂=3.1480, error=0.0064
n= 10,000: π̂=3.1412, error=0.0004
n=100,000: π̂=3.1425, error=0.0009
```

As sample count increases, error shrinks — the core frequentist idea. Monte Carlo's strength is that even complex systems with no analytic solution can be estimated through simulation alone.

### The Birthday Problem

The counter-intuitive result that 23 people are enough for a >50% chance of a shared birthday, verified by simulation.

```python
import random

def birthday_simulation(n_people: int, n_trials: int = 10_000) -> float:
    """Estimate probability of a shared birthday among n people"""
    match_count = 0
    for _ in range(n_trials):
        birthdays = [random.randint(1, 365) for _ in range(n_people)]
        if len(birthdays) != len(set(birthdays)):
            match_count += 1
    return match_count / n_trials

random.seed(42)
for n in [10, 23, 30, 50, 70]:
    prob = birthday_simulation(n)
    print(f"n={n:2d} people: P(shared birthday)={prob:.3f}")
```

Sample output:

```
n=10 people: P(shared birthday)=0.117
n=23 people: P(shared birthday)=0.506
n=30 people: P(shared birthday)=0.712
n=50 people: P(shared birthday)=0.970
n=70 people: P(shared birthday)=0.999
```

With just 23 people the probability exceeds 50%, and at 50 it is near certainty. Intuition says "23 out of 365 is sparse," but the number of pairs to compare is 23×22/2 = 253. Accurate probability calculations require careful combinatorial counting.

## Kolmogorov Axioms and Basic Properties

To handle probability rigorously, you need the Kolmogorov axioms. In practice, the properties derived from them appear more often than the axioms themselves.

### Kolmogorov Axioms (1933)

1. **Non-negativity**: For every event A, P(A) ≥ 0
2. **Normalization**: P(Ω) = 1 (the entire sample space has probability 1)
3. **Countable additivity**: For mutually exclusive events A₁, A₂, ..., P(A₁ ∪ A₂ ∪ ...) = P(A₁) + P(A₂) + ...

Accept these three and every other probability property follows.

### Basic Properties

| Property | Formula | Meaning |
| --- | --- | --- |
| Complement | P(Aᶜ) = 1 − P(A) | Probability of "not A" |
| Impossible event | P(∅) = 0 | Nothing impossible can happen |
| Monotonicity | A ⊆ B implies P(A) ≤ P(B) | Subsets cannot be more probable |
| Union | P(A ∪ B) = P(A) + P(B) − P(A ∩ B) | Inclusion-exclusion principle |
| Total probability | P(B) = Σᵢ P(B|Aᵢ)P(Aᵢ) | Partition and sum |

```python
# Verify inclusion-exclusion
# Die: A={even}, B={3 or higher}
omega = {1, 2, 3, 4, 5, 6}
A = {2, 4, 6}
B = {3, 4, 5, 6}

P_A = len(A) / len(omega)
P_B = len(B) / len(omega)
P_A_and_B = len(A & B) / len(omega)
P_A_or_B = len(A | B) / len(omega)

# Verify inclusion-exclusion principle
assert abs(P_A_or_B - (P_A + P_B - P_A_and_B)) < 1e-10
print(f"P(A)={P_A:.3f}, P(B)={P_B:.3f}")
print(f"P(A∩B)={P_A_and_B:.3f}, P(A∪B)={P_A_or_B:.3f}")
print(f"Check: {P_A} + {P_B} - {P_A_and_B} = {P_A + P_B - P_A_and_B}")
```

Output:

```
P(A)=0.500, P(B)=0.667
P(A∩B)=0.333, P(A∪B)=0.833
Check: 0.5 + 0.6666666666666666 - 0.3333333333333333 = 0.8333333333333333
```

Inclusion-exclusion removes double-counted overlap. This property is the starting point for conditional probability, Bayes' theorem, and the law of total probability.

## Sample Space Design Determines the Analysis

The same phenomenon can yield different event definitions and probabilities depending on how you construct the sample space.

```python
# Flipping 2 coins: sample space design comparison

# Design 1: Distinguish order
omega_ordered = {"HH", "HT", "TH", "TT"}
event_one_head = {"HT", "TH"}
P_one_head_ordered = len(event_one_head) / len(omega_ordered)
print(f"Order distinguished: P(exactly 1 head) = {P_one_head_ordered:.3f}")

# Design 2: Ignore order (record only count of heads)
# Possible outcomes: 0, 1, 2 heads
# But each outcome does NOT have equal probability!
omega_count = {0: 1/4, 1: 2/4, 2: 1/4}
print(f"Order ignored: P(exactly 1 head) = {omega_count[1]:.3f}")

# Key: Assigning equal probability to unequal outcomes is wrong
# Assigning 1/3 to each of {0, 1, 2} gives incorrect answers
P_wrong = 1/3
print(f"Wrong equiprobability: P(1 head) = {P_wrong:.3f} (incorrect)")
```

A common mistake in sample space design is listing outcomes and blindly assigning equal probability to each. If outcomes are not symmetric, each must receive its own weight. This intuition carries forward into random variables and distributions.

## Five Common Mistakes

1. **Confusing probability with likelihood.** Probability conditions on a hypothesis to predict data; likelihood conditions on data to compare hypotheses. The direction of the question is reversed.

2. **Failing to state the sample space.** Saying "the probability is 0.2" without specifying the full outcome set leaves the number uninterpretable. In practice this omission causes frequent miscommunication.

3. **Drawing conclusions from tiny samples.** Four heads in five flips does not mean the coin is biased. Small samples have large variance.

4. **Dismissing subjective probability as unscientific.** Real decisions always rest on limited information. Bayesian probability makes those limits explicit rather than hiding them.

5. **Reading 0.99 as certainty.** Probability always leaves residual uncertainty. In production environments this difference can translate into large cost differences.

## Checklist

- [ ] I can define sample space, event, and probability and explain the difference.
- [ ] I can state the frequentist and Bayesian interpretations and when each is more appropriate.
- [ ] I can write a simulation to verify probability intuition.
- [ ] I understand that total probability mass must sum to 1.

## Wrap-up

Probability is the language for organizing uncertainty into numbers. Three things to take from this post: probability is defined over a sample space, two complementary views (long-run frequency and belief update) coexist, and small code experiments turn abstract concepts into concrete intuition quickly.

The next post defines events and the sample space more precisely. This post showed why probability matters; the next shows what it is built on.

## Answering the Opening Questions

- **What is probability actually measuring?**
  - Probability expresses uncertainty as a number. Frequentism and Bayesianism read the same phenomenon through different lenses.
- **Why must you define the sample space and events first?**
  - The sample space makes explicit which outcomes are possible. Events and probabilities can only be defined on that foundation.
- **How do the frequentist and Bayesian views answer different questions?**
  - Frequentism emphasizes proportions across repetitions; Bayesianism emphasizes belief updating as information arrives. Both describe the same uncertainty from different angles.

<!-- toc:begin -->
## In this series

- **What Is Probability? (current)**
- Events and Sample Space (upcoming)
- Conditional Probability (upcoming)
- Bayes' Theorem (upcoming)
- Random Variables (upcoming)
- Expectation and Variance (upcoming)
- Discrete Distributions (upcoming)
- Continuous Distributions (upcoming)
- Law of Large Numbers and CLT (upcoming)
- Probability in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [Khan Academy — Probability](https://www.khanacademy.org/math/statistics-probability/probability-library)
- [Wikipedia — Probability axioms](https://en.wikipedia.org/wiki/Probability_axioms)
- [3Blue1Brown — Bayes' theorem](https://www.3blue1brown.com/lessons/bayes-theorem)
- [Stanford CS109 — Probability for Computer Scientists](https://web.stanford.edu/class/cs109/)

Tags: Probability, Foundations, Intuition, DataScience, Beginner

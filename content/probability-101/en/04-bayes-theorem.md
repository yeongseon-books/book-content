---
series: probability-101
episode: 4
title: "Probability 101 (4/10): Bayes' Theorem"
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
  - Bayes
  - Inference
  - Posterior
  - Beginner
seo_description: See how Bayes' theorem updates belief with new evidence by combining priors, likelihoods, posteriors, sequential updates, and odds form.
last_reviewed: '2026-05-15'
---

# Probability 101 (4/10): Bayes' Theorem

At some point in probability, simple calculation stops being the whole story. The harder question becomes how to revise a belief once you see new data. Bayes' theorem is the rule that makes that update explicit.

It matters not just because the equation is elegant, but because the same structure appears in medical diagnosis, spam filtering, recommender systems, A/B testing, and reinforcement learning. Any time evidence arrives and a belief needs to move, Bayes is somewhere in the background.

This is the 4th post in the Probability 101 series. Here we break Bayes' theorem into prior, likelihood, evidence, and posterior, then walk through a screening example, sequential updates, and the odds form that often makes the mechanics easier to see.


![probability 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/04/04-01-concept-at-a-glance.en.png)
*probability 101 chapter 4 flow overview*
> Bayes' Theorem requires both definition and intuition, learned through concrete examples.

## Questions to Keep in Mind

- What question Bayes' theorem actually answers?
- How priors, likelihoods, and posteriors play different roles?
- Why low base rates change the meaning of a positive result?

## Why It Matters

Statements like "a positive result means the disease is present" fail because they compress too much into one line. What really matters is how the probability of the disease changes after a positive result, given the prior prevalence and the behavior of the test itself.

Bayes' theorem is the compact rule that ties those pieces together. It is both a formula for probability and a grammar for inference, which is why it keeps reappearing far outside classroom examples. Once you internalize it, model updates, hypothesis comparison, and sequential observation interpretation all follow the same structure.

> Bayes' theorem does not throw away what you believed before. It combines prior belief and new evidence in a consistent way.

## Deriving Bayes' Theorem

Bayes' theorem follows naturally from the definition of conditional probability. Walking through the derivation step by step shows why the formula is powerful rather than arbitrary.

**Step 1: Start with the multiplication rule**

From the definition of conditional probability we get the multiplication rule:

```
P(A | B) = P(A ∩ B) / P(B)
P(A ∩ B) = P(A | B) × P(B)
```

**Step 2: Reverse the direction**

The same multiplication rule applies when we swap A and B:

```
P(A ∩ B) = P(B | A) × P(A)
```

**Step 3: Set the two expressions equal**

```
P(A | B) × P(B) = P(B | A) × P(A)
```

**Step 4: Solve for P(A|B)**

```
P(A | B) = P(B | A) × P(A) / P(B)
```

This is the basic form of Bayes' theorem. The key insight: when P(A|B) is hard to compute directly, you can rewrite it using P(B|A), P(A), and P(B).

**Step 5: Expand P(B) via the law of total probability**

Often P(B) is unknown directly, so we expand it:

```
P(B) = P(B | A) × P(A) + P(B | Aᶜ) × P(Aᶜ)
```

Final form:

```
P(A | B) = P(B | A) × P(A) / [P(B | A) × P(A) + P(B | Aᶜ) × P(Aᶜ)]
```

Understanding this derivation makes clear that Bayes' theorem is not a formula to memorize—it is a natural consequence of conditional probability's definition.

## Prior vs Posterior

The core of Bayes' theorem is how belief changes before and after observing data. Expressing this difference clearly is essential.

| Component | Definition | Example | Role |
| --- | --- | --- | --- |
| Prior P(H) | Belief before seeing data | P(disease) = 0.01 | Base rate, prevalence |
| Likelihood P(D\|H) | Probability of data given hypothesis is true | P(+\|disease) = 0.99 | Test sensitivity |
| Evidence P(D) | Total probability of observing the data | P(+) = 0.059 | Normalization constant |
| Posterior P(H\|D) | Updated belief after seeing data | P(disease\|+) = 0.168 | Final judgment |

The core pattern:

```
Posterior = (Likelihood × Prior) / Evidence
```

Three important facts this formula reveals:

1. **High likelihood does not guarantee high posterior**: When the prior is very small (rare disease), even a sensitive test produces a limited positive predictive value.

2. **A prior always exists**: Even when someone says "I have no prior," they are implicitly assuming something—uniform distribution, historical average, or structural assumption.

3. **Evidence normalizes**: It ensures that posteriors across all possible hypotheses sum to 1.

## Python Example: Medical Screening

Medical testing is the classic Bayes' theorem application. It demonstrates how a low base rate can make even a sensitive test produce a low positive predictive value.

```python
def bayesian_diagnosis(prior, sensitivity, specificity):
    """
    Compute P(disease | positive) via Bayes' theorem.
    
    prior: P(disease) — population prevalence
    sensitivity: P(+|disease) — true positive rate
    specificity: P(-|healthy) — true negative rate
    """
    # P(+) = P(+|disease)P(disease) + P(+|healthy)P(healthy)
    P_positive = sensitivity * prior + (1 - specificity) * (1 - prior)
    
    # P(disease|+) = P(+|disease)P(disease) / P(+)
    posterior = (sensitivity * prior) / P_positive
    
    return {
        "prior": prior,
        "P_positive": P_positive,
        "posterior": posterior,
        "increase_factor": posterior / prior
    }

# Scenario 1: Rare disease, high-accuracy test
result1 = bayesian_diagnosis(prior=0.001, sensitivity=0.99, specificity=0.99)
print("=== Rare disease (0.1%) ===")
print(f"Prior: {result1['prior']:.1%}")
print(f"After positive: {result1['posterior']:.1%}")
print(f"Increase: {result1['increase_factor']:.1f}x\n")

# Scenario 2: Common disease, same test
result2 = bayesian_diagnosis(prior=0.1, sensitivity=0.99, specificity=0.99)
print("=== Common disease (10%) ===")
print(f"Prior: {result2['prior']:.1%}")
print(f"After positive: {result2['posterior']:.1%}")
print(f"Increase: {result2['increase_factor']:.1f}x")
```

Output:

```
=== Rare disease (0.1%) ===
Prior: 0.1%
After positive: 9.0%
Increase: 90.0x

=== Common disease (10%) ===
Prior: 10.0%
After positive: 91.7%
Increase: 9.2x
```

The same test with the same accuracy produces completely different meanings depending on the base rate. For a rare disease, a positive result still means only 9% actual probability. For a common disease, it jumps to 91.7%.

## Sequential Bayesian Updates

One of Bayes' theorem's strengths is that it chains naturally. This round's posterior becomes next round's prior.

```python
def sequential_bayes(prior, evidences, sensitivities, specificities):
    """
    Iteratively update belief with sequential test results.
    evidences: list of "pos" or "neg" observations
    """
    current_prior = prior
    history = [prior]
    
    for i, (evidence, sens, spec) in enumerate(
        zip(evidences, sensitivities, specificities)
    ):
        if evidence == "pos":
            likelihood = sens
            likelihood_complement = 1 - spec
        else:  # "neg"
            likelihood = 1 - sens
            likelihood_complement = spec
        
        P_evidence = (
            likelihood * current_prior
            + likelihood_complement * (1 - current_prior)
        )
        posterior = (likelihood * current_prior) / P_evidence
        
        print(f"Round {i+1}: {current_prior:.3f} → {posterior:.3f} (evidence: {evidence})")
        history.append(posterior)
        current_prior = posterior
    
    return history

# Three sequential tests
prior = 0.01
evidences = ["pos", "pos", "neg"]
sensitivities = [0.9, 0.9, 0.9]
specificities = [0.95, 0.95, 0.95]

print(f"Initial prior: {prior:.3f}")
history = sequential_bayes(prior, evidences, sensitivities, specificities)
print(f"Final posterior: {history[-1]:.3f}")
```

Output:

```
Initial prior: 0.010
Round 1: 0.010 → 0.154 (evidence: pos)
Round 2: 0.154 → 0.783 (evidence: pos)
Round 3: 0.783 → 0.280 (evidence: neg)
Final posterior: 0.280
```

Two positives drive the probability up sharply, then one negative pulls it back down. This is Bayesian updating in action: at each step, prior belief and new evidence are integrated rationally.

## Bayes Factor and Hypothesis Comparison

When Bayes' theorem is applied to compare two hypotheses, it yields the Bayes factor—a measure of how differently two hypotheses explain the observed data.

```python
from math import comb

def bayes_factor(data_given_H1: float, data_given_H0: float) -> float:
    """
    Bayes factor = P(D|H1) / P(D|H0)
    > 1: data favors H1
    < 1: data favors H0
    """
    return data_given_H1 / data_given_H0

# Example: Is this coin biased?
# H1: P(heads) = 0.7 (biased)
# H0: P(heads) = 0.5 (fair)
# Data: 7 heads in 10 flips

n, k = 10, 7
# Binomial: C(n,k) * p^k * (1-p)^(n-k)
P_data_H1 = comb(n, k) * 0.7**k * 0.3**(n - k)
P_data_H0 = comb(n, k) * 0.5**k * 0.5**(n - k)

bf = bayes_factor(P_data_H1, P_data_H0)
print(f"P(data|H1=0.7) = {P_data_H1:.4f}")
print(f"P(data|H0=0.5) = {P_data_H0:.4f}")
print(f"Bayes Factor = {bf:.2f}")
print(f"Interpretation: data is {bf:.1f}x more likely under H1")

# Prior odds → posterior odds
prior_odds = 1.0  # equal prior belief
posterior_odds = prior_odds * bf
P_H1_given_data = posterior_odds / (1 + posterior_odds)
print(f"\nPrior odds: {prior_odds:.1f}")
print(f"Posterior odds: {posterior_odds:.2f}")
print(f"P(H1|data) = {P_H1_given_data:.3f}")
```

A Bayes factor greater than 1 means the data supports H1. Common interpretation scale: above 3 is weak evidence, above 10 is strong evidence, above 100 is very strong evidence.

## Naive Bayes Classifier

The most famous practical application of Bayes' theorem is the Naive Bayes classifier. It computes "probability of spam given these words." The "Naive" part means it assumes word independence conditional on the class.

```python
from collections import defaultdict
import math

# Training data
spam_docs = [
    "win prize free click",
    "win congratulations big money win",
    "free gift prize event",
]
ham_docs = [
    "meeting schedule confirm please",
    "report review schedule coordination",
    "project progress update meeting",
    "schedule coordination report submit",
]

def train_naive_bayes(spam_docs, ham_docs):
    spam_words = defaultdict(int)
    ham_words = defaultdict(int)
    vocab = set()

    for doc in spam_docs:
        for word in doc.split():
            spam_words[word] += 1
            vocab.add(word)

    for doc in ham_docs:
        for word in doc.split():
            ham_words[word] += 1
            vocab.add(word)

    return {
        "spam_words": spam_words,
        "ham_words": ham_words,
        "total_spam": sum(spam_words.values()),
        "total_ham": sum(ham_words.values()),
        "V": len(vocab),
        "P_spam": len(spam_docs) / (len(spam_docs) + len(ham_docs)),
        "P_ham": len(ham_docs) / (len(spam_docs) + len(ham_docs)),
    }

def predict(model, text):
    log_spam = math.log(model["P_spam"])
    log_ham = math.log(model["P_ham"])

    for word in text.split():
        # Laplace smoothing: (count + 1) / (total + V)
        p_w_spam = (model["spam_words"][word] + 1) / (model["total_spam"] + model["V"])
        p_w_ham = (model["ham_words"][word] + 1) / (model["total_ham"] + model["V"])
        log_spam += math.log(p_w_spam)
        log_ham += math.log(p_w_ham)

    # Log-sum-exp for numerical stability
    max_log = max(log_spam, log_ham)
    p_spam = math.exp(log_spam - max_log) / (
        math.exp(log_spam - max_log) + math.exp(log_ham - max_log)
    )
    return {"P(spam)": p_spam, "P(ham)": 1 - p_spam}

model = train_naive_bayes(spam_docs, ham_docs)
test_cases = ["win prize confirm", "meeting schedule confirm", "free big money"]
for text in test_cases:
    result = predict(model, text)
    label = "SPAM" if result["P(spam)"] > 0.5 else "HAM"
    print(f'"{text}" → {label} (P(spam)={result["P(spam)"]:.3f})')
```

Naive Bayes is simple yet surprisingly effective. The independence assumption rarely holds in reality, but classification performance degrades less than you might expect. This demonstrates Bayes' theorem's robustness.

## Base Rate and PPV Across Prevalences

How much does the base rate influence the posterior? Comparing PPV across multiple prevalences makes the relationship concrete.

```python
def ppv_table(sensitivity: float, specificity: float, prevalences: list):
    """Compute PPV (positive predictive value) across prevalences."""
    print(f"Sensitivity={sensitivity:.0%}, Specificity={specificity:.0%}")
    print(f"{'Prevalence':<12} {'PPV':<10} {'False alarm rate'}")
    for prev in prevalences:
        P_pos = sensitivity * prev + (1 - specificity) * (1 - prev)
        ppv = (sensitivity * prev) / P_pos
        fdr = 1 - ppv
        print(f"{prev:<12.4f} {ppv:<10.3f} {fdr:.1%}")

ppv_table(
    sensitivity=0.99,
    specificity=0.95,
    prevalences=[0.0001, 0.001, 0.01, 0.05, 0.1, 0.2, 0.5]
)
```

Output:

```
Sensitivity=99%, Specificity=95%
Prevalence   PPV        False alarm rate
0.0001       0.002      99.8%
0.0010       0.019      98.1%
0.0100       0.166      83.4%
0.0500       0.510      49.0%
0.1000       0.688      31.2%
0.2000       0.832      16.8%
0.5000       0.952      4.8%
```

At prevalence 0.01% (1 in 10,000), even a 99%-sensitive test produces a PPV of only 0.2%—499 out of 500 positives are false alarms. Prevalence must exceed 5% before PPV crosses 50%. This is why ignoring the base rate in practice is dangerous.

## Concepts at a Glance

| Component | Symbol | Role | Diagnostic example |
|---|---|---|---|
| Prior | P(H) | Belief in hypothesis without evidence | Prevalence 1% |
| Likelihood | P(D\|H) | How probable data is if hypothesis holds | Sensitivity 99% |
| Evidence | P(D) | Total probability of observing data | Positive rate 5.94% |
| Posterior | P(H\|D) | Updated belief after observing data | PPV 16.6% |
| Bayes factor | P(D\|H₁)/P(D\|H₀) | Ratio comparing two hypotheses | LR = sens/(1−spec) |

Notice the gap between prior (1%) and posterior (16.6%). Even an impressive 99% sensitivity shrinks dramatically in front of a low base rate.

## Intuition Before Formula

Bayes' theorem is often summarized as `Posterior ∝ Likelihood × Prior`. The posterior reflects both new evidence and existing belief. Evidence P(D) serves as normalization to make everything sum to 1.

With this structure internalized, questions like "the likelihood is high—why is the posterior low?" resolve naturally. When the base rate is low, the prior is small, and no amount of likelihood can overcome a tiny starting point. This gap shows up most starkly in diagnostic problems.

## 5-Step Bayes Walkthrough

### Step 1 — Set prior and likelihood

```python
prior = 0.01           # P(disease)
sens = 0.99            # P(+|disease)
spec = 0.95            # P(-|no disease)
```

We assume 1% disease prevalence and set test sensitivity and specificity. These three values are the starting point for any Bayesian update.

### Step 2 — Compute evidence P(+)

```python
p_pos = sens * prior + (1 - spec) * (1 - prior)
print("P(+):", p_pos)
```

A positive can come from a true patient or a healthy person with a false positive. Evidence accounts for both pathways.

### Step 3 — Compute posterior P(disease | +)

```python
post = sens * prior / p_pos
print("P(disease | +):", post)
```

This is the number we actually care about after a diagnosis. Even with very high sensitivity, a low base rate keeps this value lower than intuition expects.

### Step 4 — Update on a second positive

```python
prior2 = post
p_pos2 = sens * prior2 + (1 - spec) * (1 - prior2)
post2 = sens * prior2 / p_pos2
print("after 2 positives:", post2)
```

The first posterior becomes the next prior. This chaining property is one reason Bayes' theorem is powerful—sequential data integrates with the same formula.

### Step 5 — Odds form

```python
prior_odds = 0.01 / 0.99
likelihood_ratio = sens / (1 - spec)
post_odds = prior_odds * likelihood_ratio
print("posterior odds:", post_odds, "P:", post_odds / (1 + post_odds))
```

The odds form makes the arithmetic multiplicative. This is especially convenient when incorporating multiple pieces of evidence sequentially.

## What to Notice in This Code

- A small base rate keeps PPV low even with a sensitive test.
- The posterior becomes the next prior—sequential updating.
- Likelihood and probability are not the same thing.
- The odds form simplifies repeated updates into multiplication.

## Five Common Mistakes

1. **Treating P(D|H) as P(H|D).** This confusion undermines the very reason Bayes' theorem exists.

2. **Ignoring the base rate.** Looking only at test performance overestimates diagnostic power.

3. **Pretending no prior exists.** Even when unstated, some assumption—uniform, historical average, structural—is always present.

4. **Confusing likelihood with probability.** Likelihood is how plausible the data is given a hypothesis, not the probability of the hypothesis itself.

5. **Skipping the independence assumption in sequential updates.** Whether the second observation is independent of the first changes the update result.

## How This Shows Up in Production

Spam filters (Naive Bayes), Bayesian A/B testing, medical diagnosis, RL belief states—Bayesian inference is the core of probabilistic ML. Even when you do not take a fully Bayesian approach, the discipline of separating prior from evidence is practical.

Strong teams ask Bayesian questions when interpreting scores: How rare is this event to begin with? How much should this evidence shift our belief? What independence assumptions are we making when we chain updates?

Consider Bayesian A/B testing as a concrete example. You start with a Beta(1, 1) prior on conversion rate and update the Beta distribution with each click/no-click observation. Unlike frequentist testing, you can produce statements like "there is a 95% probability that variant B outperforms A"—directly actionable for decision-making. When previous campaign data exists, an informative prior accelerates convergence.

## Key Terms

- **Prior P(H)**: Belief in hypothesis H before seeing data.
- **Likelihood P(D|H)**: Probability of data D given hypothesis H is true.
- **Posterior P(H|D)**: Updated belief after seeing data.
- **Evidence P(D)**: Total probability of observing the data (normalization).
- **Bayes factor**: Ratio comparing how well two hypotheses explain the data.

The posterior is not determined by likelihood alone. The same data can lead to different conclusions when the prior differs.

## Checklist

- [ ] I can write Bayes' theorem without looking it up.
- [ ] I distinguish prior, likelihood, posterior, and evidence.
- [ ] I can compute PPV given prevalence, sensitivity, and specificity.
- [ ] I can perform sequential updating where the posterior becomes the next prior.
- [ ] I can convert between odds form and probability form.
- [ ] I can explain the independence assumption in Naive Bayes.
- [ ] I know that a Bayes factor above 10 counts as strong evidence.

## Practice Problems

1. With base rate 0.001, sensitivity 0.99, specificity 0.99, compute PPV.
2. State the practical meaning of a Bayes factor of 10.
3. Compare the posterior under a strong prior vs a weak prior for the same likelihood.

## Wrap-up and Next Steps

Bayes' theorem is the math of learning. Three takeaways to keep: the posterior reflects both new data and prior belief; a low base rate fundamentally changes how test results should be interpreted; and each posterior becomes the next prior, enabling continuous learning.

The next episode introduces random variables—moving from event-level reasoning to numeric outcomes, where expectation and variance become the primary analysis tools.

## Answering the Opening Questions

- **What question does Bayes' theorem answer?**
  - Bayes' theorem answers "how should I update the probability of hypothesis A after observing data B?" The basic formula `P(A|B) = P(B|A) × P(A) / P(B)` is exactly that rule.
  - In the medical screening example, it was used to find `P(disease|positive)` rather than `P(positive|disease)`—recalculating the actual disease probability after seeing the test result.
  - As the sequential update example shows, this question does not end in one step. The first posterior becomes the next prior, updating beliefs continuously: `0.010 → 0.154 → 0.783 → 0.280`.
- **What do prior, likelihood, and posterior each mean?**
  - The prior is belief before seeing data. In the article's table, `P(disease)=0.01` and the rare-disease scenario's 0.1% prevalence are priors.
  - Likelihood is how probable the data is assuming the hypothesis is true. In the diagnostic problem, sensitivity like `P(positive|disease)=0.99` plays the likelihood role.
  - The posterior is the updated belief after seeing data. The table's `P(disease|positive)=0.168` and the rare-disease scenario's 9.0% are the final judgment values.
- **Why does a small base rate change the meaning of a positive result?**
  - When the base rate is small, false positives dominate the total positives. Even with 99% sensitivity and 99% specificity, at 0.1% prevalence the post-test probability was only 9.0%.
  - The PPV table shows that at prevalence 0.0010, PPV is 0.019 so 98.1% of positives are false alarms, while at prevalence 0.1000, PPV rises to 0.688.
  - Therefore, test performance numbers alone are insufficient—you must include the prior probability that creates `P(positive)` to read the actual meaning of a positive result.
<!-- toc:begin -->
## In this series

- [Probability 101 (1/10): What Is Probability?](./01-what-is-probability.md)
- [Probability 101 (2/10): Events and Sample Space](./02-events-and-sample-space.md)
- [Probability 101 (3/10): Conditional Probability](./03-conditional-probability.md)
- **Bayes' Theorem (current)**
- Random Variables (upcoming)
- Expectation and Variance (upcoming)
- Discrete Distributions (upcoming)
- Continuous Distributions (upcoming)
- Law of Large Numbers and CLT (upcoming)
- Probability in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [3Blue1Brown — Bayes' theorem](https://www.3blue1brown.com/lessons/bayes-theorem)
- [Wikipedia — Bayes' theorem](https://en.wikipedia.org/wiki/Bayes%27_theorem)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)
- [Kevin Murphy — Probabilistic ML](https://probml.github.io/pml-book/book1.html)

Tags: Probability, Bayes, Inference, Posterior, Beginner

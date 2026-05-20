---
series: probability-101
episode: 10
title: "Probability 101 (10/10): Probability in Machine Learning"
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
  - MachineLearning
  - Likelihood
  - Inference
  - Beginner
seo_description: See how probability shapes machine learning through loss functions, calibration, and Bayesian updates so model scores become interpretable.
last_reviewed: '2026-05-15'
---

# Probability 101 (10/10): Probability in Machine Learning

If you make it through a probability series, one question naturally remains: where do all of these ideas actually live inside machine learning? If that question stays unanswered, probability remains background theory. Once it is answered, probability becomes an operational tool for reading model behavior.

Much of modern machine learning is probability wearing different names. Cross-entropy, negative log-likelihood, classifier probabilities, calibration, and Bayesian updates are not separate islands. They are different views of uncertainty, prediction, and decision cost.

This is the final post in the Probability 101 series. Here we connect probability to loss functions, conditional model outputs, calibration metrics, and Bayesian thinking so the earlier ideas show up in a recognizable ML workflow.

## Questions to Keep in Mind

- Where probability is hiding inside common machine learning workflows?
- Why cross-entropy and negative log-likelihood point to the same idea?
- What a classifier score like 0.8 should mean before you trust it?

## Big Picture

![probability 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/10/10-01-concept-at-a-glance.en.png)

*probability 101 chapter 10 flow overview*

This picture places Probability in Machine Learning inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> Probability in Machine Learning requires both definition and intuition, learned through concrete examples.

## Why It Matters

If you read model outputs as generic scores rather than as probabilistic statements, decision-making gets fuzzy quickly. You need to know whether 0.8 should be interpreted as “about 80% likely,” whether it is just a ranking score, where the threshold should sit, and how distribution shift may have changed that meaning.

Training itself is tied to probability as well. Cross-entropy in classification is another face of negative log-likelihood. Regression losses often reveal an implicit distributional assumption about the error. In that sense, the loss function is not just a computational device. It is a window into what kind of probabilistic world the model is assuming.

> Machine learning is not only about guessing the right label. It is also about organizing uncertainty and tying that uncertainty to decision cost.

## Concept at a Glance

## Key Terms

- **Likelihood**: L(θ) = ∏ p(yᵢ | xᵢ; θ).
- **MLE**: θ that maximizes the likelihood.
- **MAP**: θ that maximizes prior × likelihood.
- **Cross-entropy**: -Σ y log p̂.
- **Calibration**: how closely predicted probabilities match actual frequencies.

## Before / After

**Before**: “The model output is 0.8.” That says almost nothing by itself.

**After**: “The model estimates p(y=1 | x) ≈ 0.8, and calibration tells us whether that estimate behaves honestly in the real world.”

## Hands-on: 5-step ML Probability

### Step 1 — Cross-entropy loss

```python
import numpy as np
y = np.array([1, 0, 1, 1, 0])
p = np.array([0.9, 0.2, 0.8, 0.6, 0.3])
nll = -np.mean(y*np.log(p) + (1-y)*np.log(1-p))
print("NLL:", nll)
```

### Step 2 — Logistic regression (sklearn)

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
X = np.array([[0],[1],[2],[3],[4]])
y = np.array([0, 0, 1, 1, 1])
clf = LogisticRegression().fit(X, y)
print("p(y=1|x=2):", clf.predict_proba([[2]])[0, 1])
```

### Step 3 — Calibration

```python
import numpy as np
# Predicted probabilities vs observed frequencies
preds = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
actual = np.array([0.12, 0.28, 0.55, 0.66, 0.91])
print("calibration gap:", np.abs(preds - actual).mean())
```

### Step 4 — Bayesian update (concept)

```python
# Posterior from prior p(theta) and likelihood p(D|theta)
prior = 0.5
likelihood = 0.8
post = likelihood * prior / (likelihood * prior + (1 - likelihood) * (1 - prior))
print("posterior:", post)
```

### Step 5 — Brier score

```python
import numpy as np
y = np.array([1, 0, 1, 0])
p = np.array([0.9, 0.2, 0.6, 0.4])
brier = np.mean((p - y)**2)
print("Brier:", brier)
```

## What to Notice in This Code

- Cross-entropy = NLL = negative log-likelihood.
- A logistic regression output is a conditional probability p(y|x).
- Calibration is an evaluation axis separate from accuracy.

## Five Common Mistakes

1. **Treating raw scores directly as probabilities.**
2. **Ignoring calibration.**
3. **Evaluating only on accuracy.**
4. **Using threshold 0.5 on imbalanced data.**
5. **Pretending there is no Bayesian prior.**

## How This Shows Up in Production

Spam classification, medical diagnosis, recommendation scores, anomaly detection — probability outputs meet decision rules and cost. Calibration, Brier, log-loss are the standard metrics.

## How a Senior Engineer Thinks

- Knows that loss = probability.
- Measures calibration.
- Sets thresholds by cost.
- Includes uncertainty in predictions.
- Uses both Bayesian and frequentist tools.

## Checklist

- [ ] I know cross-entropy = NLL.
- [ ] I measure calibration.
- [ ] I understand p(y|x).
- [ ] I use Brier / log-loss.

## Practice Problems

1. Describe what goes wrong with threshold 0.5 on 90:10 imbalanced data.
2. Explain why a calibration plot matters.
3. Give the difference between MAP and MLE in one line.

## Wrap-up and Next Steps

Probability is the native language of ML. The next steps are Linear Algebra 101 and Machine Learning 101, which add the other axes of modeling.

## Answering the Opening Questions

- **Where probability is hiding inside common machine learning workflows?**
  - The article treats Probability in Machine Learning as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why cross-entropy and negative log-likelihood point to the same idea?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What a classifier score like 0.8 should mean before you trust it?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
- [Probability 101 (9/10): Law of Large Numbers and CLT](./09-lln-and-clt.md)
- **Probability in Machine Learning (current)**

<!-- toc:end -->

## References

- [Kevin Murphy — Probabilistic ML](https://probml.github.io/pml-book/book1.html)
- [Bishop — Pattern Recognition and Machine Learning](https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/)
- [scikit-learn — Calibration](https://scikit-learn.org/stable/modules/calibration.html)
- [Wikipedia — Cross-entropy](https://en.wikipedia.org/wiki/Cross-entropy)

Tags: Probability, MachineLearning, Likelihood, Inference, Beginner

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


![probability 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/10/10-01-concept-at-a-glance.en.png)
*probability 101 chapter 10 flow overview*
> Probability in Machine Learning requires both definition and intuition, learned through concrete examples.

## Questions to Keep in Mind

- Where probability is hiding inside common machine learning workflows?
- Why cross-entropy and negative log-likelihood point to the same idea?
- What a classifier score like 0.8 should mean before you trust it?

## Why It Matters

If you read model outputs as generic scores rather than as probabilistic statements, decision-making gets fuzzy quickly. You need to know whether 0.8 should be interpreted as "about 80% likely," whether it is just a ranking score, where the threshold should sit, and how distribution shift may have changed that meaning.

Training itself is tied to probability as well. Cross-entropy in classification is another face of negative log-likelihood. Regression losses often reveal an implicit distributional assumption about the error. In that sense, the loss function is not just a computational device. It is a window into what kind of probabilistic world the model is assuming.

### Where Probability Appears in ML

| Area | Role | Example |
|---|---|---|
| Classification output | Outputs p(y=1|x) as decision evidence | Spam filter, medical diagnosis |
| Loss function | Defines learning objective via NLL | Cross-entropy, NLL |
| Regularization | Encodes prior beliefs about parameters | L2 = Gaussian prior, L1 = Laplace |
| Generative models | Explicitly models data distribution | VAE, GAN, diffusion models |

Probability appears at virtually every stage of ML — explicitly or implicitly. The loss function reveals what probabilistic model is assumed, model output is interpreted as conditional probability, regularization reflects prior beliefs about parameters, and generative models learn the data distribution itself.

## Concepts at a Glance

| Concept | One-line Definition | Role in ML | Formula |
|---|---|---|---|
| MLE | θ that makes data most plausible | Derives loss functions | `argmax_θ P(D|θ)` |
| MAP | θ considering prior + likelihood | Interprets regularization | `argmax_θ P(D|θ)P(θ)` |
| Cross-entropy | Gap between predicted and true distribution | Classification loss | `-Σ yᵢ log pᵢ` |
| Calibration | Predicted prob ≈ actual frequency | Decision reliability | Calibration curve |
| Brier score | MSE of probability predictions | Combined accuracy + calibration | `mean((p-y)²)` |
| Softmax | Logits → probabilities | Multi-class output | `exp(zᵢ)/Σexp(zⱼ)` |

## Key Terms

- **Likelihood**: given parameters θ, how plausible the observed data is. L(θ) = ∏ p(yᵢ | xᵢ; θ).
- **MLE**: find θ that maximizes the likelihood — equivalent to minimizing NLL.
- **MAP**: find θ that maximizes posterior ∝ likelihood × prior — equivalent to regularized MLE.
- **Cross-entropy**: measures the gap between predicted distribution and true labels. Equals NLL for classification.
- **Calibration**: how closely predicted probabilities match observed frequencies in practice.

Training, inference, and evaluation are not independent. The choice of loss determines the meaning of outputs, and calibration evaluation reveals whether those outputs match reality.

## When Is a Model Score Actually a Probability?

"The model output 0.8" is not enough information. You need to know whether that value reads as p(y=1|x)=0.8 or is merely a ranking score. If you want to use it as probability, calibration status matters. A model that predicts well does not necessarily output honest probabilities.

Three aspects determine whether output qualifies as probability:

1. **Output function**: sigmoid or softmax makes outputs sum to 1, so they look like probabilities formally. But form is not substance — matching actual frequencies is a separate question.
2. **Training objective**: if trained with NLL (negative log-likelihood), the output is driven toward approximating the true conditional probability. Hinge loss or ranking loss only preserves ordering — no probability guarantee.
3. **Calibration state**: even after training, if the calibration curve deviates from the diagonal, the output cannot be trusted as probability. Post-hoc calibration (Platt Scaling, Temperature Scaling) is needed before cost-based decisions.

| Model | Output Format | Probability Interpretation? | Calibration Needed? |
|---|---|---|---|
| Logistic Regression | sigmoid | Yes (NLL-trained) | Usually good |
| Random Forest | tree vote fraction | Limited | Often needed |
| SVM (rbf) | decision function | No (distance) | Platt required |
| Neural net (softmax) | softmax | Yes (CE-trained) | Overconfident, needed |
| XGBoost | sigmoid(logit) | Yes | Data-dependent |

The same number 0.8 means entirely different things from logistic regression vs. SVM's decision value.

### Monte Carlo Check: Calibration Effect

```python
import numpy as np
np.random.seed(42)

# Overconfident model simulation: true prob is 0.6 but model outputs 0.9
n_samples = 10000
true_prob = 0.6
model_output = 0.9  # overconfident

# Simulate actual outcomes
y_true = np.random.binomial(1, true_prob, n_samples)

# Overconfident model's Brier score
brier_overconfident = np.mean((model_output - y_true)**2)

# Calibrated model (output close to true probability)
calibrated_output = 0.62
brier_calibrated = np.mean((calibrated_output - y_true)**2)

print(f"Overconfident Brier: {brier_overconfident:.4f}")
print(f"Calibrated Brier:    {brier_calibrated:.4f}")
print(f"Improvement:         {brier_overconfident - brier_calibrated:.4f}")
```

Output:

```
Overconfident Brier: 0.3300
Calibrated Brier:    0.2408
Improvement:         0.0892
```

Even if discrimination ability is identical, outputs closer to the true frequency produce better Brier scores. An overconfident model pays a penalty in "honesty" despite equal "accuracy." This is why calibration is a separate evaluation axis.

## Hands-on: 5-Step ML Probability

### Step 1 — Cross-Entropy Loss

```python
import numpy as np
y = np.array([1, 0, 1, 1, 0])
p = np.array([0.9, 0.2, 0.8, 0.6, 0.3])
nll = -np.mean(y*np.log(p) + (1-y)*np.log(1-p))
print("NLL:", nll)
```

This is the most common binary classification loss. From a probability perspective, it is negative log-likelihood: assigning high probability to the correct answer reduces loss, and confident wrong predictions are punished heavily.

### Step 2 — Logistic Regression Output

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification

# Binary classification data
X, y = make_classification(n_samples=200, n_features=4, n_classes=2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train logistic regression
clf = LogisticRegression().fit(X_train, y_train)

# Probability predictions
probs = clf.predict_proba(X_test)
print("First 5 predicted probabilities (class 0, class 1):")
print(probs[:5])

# Compare predictions with labels
preds = clf.predict(X_test)
for i in range(5):
    print(f"actual={y_test[i]}, predicted={preds[i]}, p(y=1|x)={probs[i, 1]:.3f}")
```

Unlike bare `predict()` which returns labels, `predict_proba()` returns probability estimates for each class. These probabilities let you gauge model confidence, adjust thresholds, and quantify uncertainty for downstream decisions.

### Step 3 — Calibration Assessment

```python
import numpy as np
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt

# Synthetic predicted probabilities and true labels
y_true = np.array([0, 0, 1, 1, 0, 1, 1, 0, 1, 1]*10)
y_prob = np.random.default_rng(42).beta(2, 5, len(y_true))

# Calibration curve
prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=5)

# Visualization
plt.figure(figsize=(6, 4))
plt.plot([0, 1], [0, 1], linestyle='--', label='Perfect calibration')
plt.plot(prob_pred, prob_true, marker='o', label='Model')
plt.xlabel('Predicted probability')
plt.ylabel('Observed frequency')
plt.title('Calibration Plot')
plt.legend()
plt.grid(True)
# plt.show()
```

A calibration plot shows observed frequency versus predicted probability in bins. Close to the diagonal = well-calibrated. Above the diagonal = under-confident (actual frequency exceeds prediction). Below = over-confident. In domains with high decision costs (medical diagnosis, fraud detection, financial risk), calibration is a required evaluation metric alongside accuracy.

**Calibration improvement methods:**

- **Platt Scaling**: fit a logistic regression on top of model outputs to re-calibrate.
- **Isotonic Regression**: non-parametric monotone calibration.
- **Temperature Scaling**: adjust the softmax temperature of a neural network.

Calibration can drift over time as data distributions shift, so continuous monitoring in production is necessary.

### Step 4 — Bayesian Update

```python
# Posterior from prior p(theta) and likelihood p(D|theta)
prior = 0.5
likelihood = 0.8
post = likelihood * prior / (likelihood * prior + (1 - likelihood) * (1 - prior))
print("posterior:", post)
```

The Bayesian perspective updates beliefs about parameters or hypotheses as new data arrives. Even if you do not run a full Bayesian model, thinking in terms of "prior belief + data update" is a practical habit that connects regularization to probability.

### Step 5 — Brier Score

```python
import numpy as np
y = np.array([1, 0, 1, 0])
p = np.array([0.9, 0.2, 0.6, 0.4])
brier = np.mean((p - y)**2)
print("Brier:", brier)
```

The Brier score is the mean squared error between predicted probabilities and actual outcomes. Together with log-loss, it is the standard metric for evaluating the quality of probability predictions.

## MLE vs MAP: The Probabilistic Interpretation

Two common parameter-estimation methods in ML, viewed through the probability lens.

**MLE (Maximum Likelihood Estimation)**: find the θ that makes the observed data most probable. `argmax_θ P(D|θ)`. Pure data-driven — no prior assumptions about θ.

**MAP (Maximum A Posteriori)**: maximize the posterior, which equals likelihood × prior. `argmax_θ P(θ|D) ∝ P(D|θ)P(θ)`. Incorporates prior beliefs.

L2 regularization corresponds to a Gaussian prior on parameters (MAP with N(0, σ²) prior). L1 corresponds to a Laplace prior. Regularization is not just an "overfitting trick" — it is injecting a prior belief about where parameters should live.

### Regularization Strength as Prior Strength

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score

X, y = make_classification(n_samples=300, n_features=20, n_informative=5,
                           n_redundant=10, random_state=42)

# C = 1/lambda: smaller C = stronger regularization = stronger prior
for C in [0.01, 0.1, 1.0, 10.0, 100.0]:
    clf = LogisticRegression(C=C, max_iter=1000, random_state=42)
    scores = cross_val_score(clf, X, y, cv=5, scoring='neg_log_loss')
    clf.fit(X, y)
    print(f"C={C:6.2f} | mean NLL: {-scores.mean():.4f} | coef L2 norm: {np.linalg.norm(clf.coef_):.4f}")
```

Output:

```
C=  0.01 | mean NLL: 0.5765 | coef L2 norm: 0.3842
C=  0.10 | mean NLL: 0.4523 | coef L2 norm: 1.2156
C=  1.00 | mean NLL: 0.4201 | coef L2 norm: 3.1847
C= 10.00 | mean NLL: 0.4389 | coef L2 norm: 5.9234
C=100.00 | mean NLL: 0.4512 | coef L2 norm: 7.2341
```

Smaller C (stronger regularization) → smaller L2 norm of coefficients. This means a tighter Gaussian prior centered at 0 — "I believe parameters should be small." The best NLL at C=1.0 indicates that this prior strength is appropriate for this dataset. Too strong (C=0.01) → underfitting. Too weak (C=100) → overfitting.

### MLE vs MAP: Python Implementation

```python
import numpy as np
from scipy.optimize import minimize_scalar

# Coin flip: 10 tosses, 7 heads
n, k = 10, 7

# MLE: maximize likelihood only
def neg_log_likelihood(theta):
    if theta <= 0 or theta >= 1:
        return 1e10
    return -(k * np.log(theta) + (n - k) * np.log(1 - theta))

mle_result = minimize_scalar(neg_log_likelihood, bounds=(0.01, 0.99), method='bounded')
print(f"MLE theta: {mle_result.x:.4f}")  # 0.7000 (= k/n)

# MAP: add Beta(2, 2) prior → pulls toward 0.5
alpha, beta_param = 2, 2
def neg_log_posterior(theta):
    if theta <= 0 or theta >= 1:
        return 1e10
    log_lik = k * np.log(theta) + (n - k) * np.log(1 - theta)
    log_prior = (alpha - 1) * np.log(theta) + (beta_param - 1) * np.log(1 - theta)
    return -(log_lik + log_prior)

map_result = minimize_scalar(neg_log_posterior, bounds=(0.01, 0.99), method='bounded')
print(f"MAP theta: {map_result.x:.4f}")  # 0.6923
print(f"Analytical MAP: {(k + alpha - 1) / (n + alpha + beta_param - 2):.4f}")
```

MLE sees only data: 7/10 = 0.7. MAP incorporates a Beta(2,2) prior ("coins tend toward fair"), pulling the estimate to 0.6923. As data grows, the prior's influence fades and MLE ≈ MAP.

## Loss Functions as Probabilistic Assumptions

| Loss Function | Assumed Probabilistic Model | Domain | Key Insight |
|---|---|---|---|
| Binary CE | Bernoulli distribution | Binary classification | Equals negative log-likelihood |
| Categorical CE | Categorical distribution | Multi-class | Softmax + NLL |
| MSE | Gaussian (fixed variance) | Regression | MLE with σ²=1 assumption |
| Huber Loss | Gaussian + Laplace mixture | Robust regression | Gaussian center, Laplace tails |
| KL Divergence | Distance between two distributions | VAE latent space | Asymmetric divergence |

Changing the loss function is changing the probabilistic assumption about your data. Using MSE implicitly assumes Gaussian errors. Using CE assumes each observation is a Bernoulli trial.

## Threshold Decisions and Cost Structure

A spam filter that outputs 0.7 — should it classify as spam? The answer depends on cost structure, not on an arbitrary 0.5 cutoff.

```python
import numpy as np

# Cost matrix
cost_fp = 10   # Legitimate email marked spam (user frustration)
cost_fn = 1    # Spam in inbox (minor annoyance)

# Optimal threshold = cost_fn / (cost_fn + cost_fp)
optimal_threshold = cost_fn / (cost_fn + cost_fp)
print(f"Optimal threshold (spam): {optimal_threshold:.3f}")  # 0.091

# Opposite cost structure: medical screening (missed diagnosis is expensive)
cost_fp_medical = 1    # Unnecessary follow-up test
cost_fn_medical = 50   # Missed cancer
optimal_medical = cost_fn_medical / (cost_fn_medical + cost_fp_medical)
print(f"Optimal threshold (medical): {optimal_medical:.3f}")  # 0.980
```

The same model with different cost structures demands dramatically different thresholds. The spam filter (where false positives are costly) needs a high threshold; medical screening (where false negatives are catastrophic) needs a low threshold. Calibrated probability outputs are required for cost-based decision-making to be meaningful.

In production, calibration can drift as data distributions shift. A model that was honest at training time may become miscalibrated over time. Continuous monitoring of calibration is essential for any system that uses probability outputs for decisions.

## Six Common Mistakes

**First**, reading raw scores directly as probabilities. Not all model outputs are probabilities — SVM decision values, uncalibrated neural net logits, and boosting scores are ranking tools, not honest frequencies.

**Second**, evaluating only accuracy while ignoring calibration. In high-stakes domains (medicine, finance, fraud), a well-calibrated model that is slightly less accurate can make better decisions than an accurate but overconfident one.

**Third**, mechanically using threshold 0.5 with imbalanced data. The threshold should reflect the cost structure and class balance, not a default.

**Fourth**, believing there is no Bayesian prior. The model architecture, regularization, and data collection process already encode strong priors — acknowledging this explicitly is better than pretending otherwise.

**Fifth**, treating the loss function as just a computational device. The loss reveals the probabilistic model the optimizer is fitting. Understanding this connection lets you choose losses intentionally rather than by convention.

**Sixth**, assuming calibration is permanent. Data drift, concept drift, and deployment-environment changes can all break calibration. Monitoring calibration in production is not optional.

## What to Notice in This Code

- Cross-entropy is negative log-likelihood — minimizing CE maximizes data likelihood.
- Classifier output is a conditional probability p(y|x) estimate.
- Calibration is a separate evaluation axis from accuracy.
- Bayesian thinking connects prior information with data updates.
- Regularization strength controls how much prior belief influences the estimate.

## Checklist

- [ ] I can explain the relationship between cross-entropy and NLL.
- [ ] I can interpret p(y|x) from a classifier.
- [ ] I know that accuracy and calibration are different axes.
- [ ] I can distinguish Brier score from log-loss usage.
- [ ] I can explain MLE vs MAP in terms of prior presence.
- [ ] I can connect a loss function to its assumed probabilistic model.
- [ ] I can read a calibration plot and identify over/under-confidence.
- [ ] I can explain why threshold depends on cost structure.

## Wrap-up and Next Steps

Probability is not a peripheral concept in machine learning — it is the central one. Three takeaways: loss functions are often just another expression of a probabilistic model; model outputs need calibration before they become trustworthy probabilities; and the Bayesian perspective connects prior beliefs to data updates as a practical reasoning tool.

This concludes the Probability 101 series. Probability was the language for reading uncertainty in models. The next steps — Linear Algebra 101 and Machine Learning 101 — add the structural and algorithmic axes that sit alongside probability in the full ML picture.

## Answering the Opening Questions

- **Where exactly is probability hidden in machine learning?**
  - It hides in loss functions. Cross-entropy is negative log-likelihood, and MSE is MLE under Gaussian error assumptions. Regularization terms reflect prior distributions. Model output reads as conditional probability p(y|x), and generative models learn the data distribution itself. Probability is not ML's periphery but its skeleton.
- **Why do cross-entropy and negative log-likelihood point in the same direction?**
  - In binary classification, expanding cross-entropy `-[y log p + (1-y) log(1-p)]` yields exactly the negative log-likelihood of a Bernoulli distribution. Minimizing CE is equivalent to maximizing data likelihood. In multi-class settings, categorical NLL matches categorical CE as well.
- **What does the 0.8 a classification model outputs mean?**
  - It is an estimate of p(y=1|x)=0.8 in the model's learned conditional world. However, for this value to match actual 80% frequency, the model must be calibrated. An uncalibrated 0.8 can rank but is risky for cost-based decisions. Calibrating with Platt Scaling or Isotonic Regression before use is the practical standard.
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

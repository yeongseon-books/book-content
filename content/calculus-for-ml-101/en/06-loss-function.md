---
series: calculus-for-ml-101
episode: 6
title: "Calculus for ML 101 (6/10): Loss Function"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Calculus
  - ML
  - LossFunction
  - MSE
  - Beginner
seo_description: A beginner-friendly tour of loss functions, MSE, cross entropy, gradients, and the training signal intuition for ML
last_reviewed: '2026-05-15'
---

# Calculus for ML 101 (6/10): Loss Function

Producing a prediction is not enough to start learning. You still need a numerical rule that says how wrong that prediction was, and a differentiable way to turn that error into an update signal. That rule is the loss function.

This is the 6th post in the Calculus for ML 101 series.

The important point is that a loss function is not a simple scoreboard. How you define the loss determines *what* the model learns to be good at. Choosing the loss is defining the optimization target itself.

In this post, we'll use MSE, cross entropy, and gradient-based training signals to show that a loss function is more than a number—it is the concrete definition of what you want the model to become good at, and its design shapes every update that follows.

By the end, you'll be able to explain "why did this model learn in that direction?" starting from the loss function definition.

> A loss function does not merely report error after the fact. It creates the pressure signal that pushes the model toward a different set of parameters.

![calculus for ml 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/06/06-01-concept-at-a-glance.en.png)
*calculus for ml 101 chapter 6 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Loss Function?
- Which signal should the example or diagram make visible for Loss Function?
- What failure should be prevented first when Loss Function reaches a real system?

## Questions this article answers

- How is a loss function different from a simple evaluation metric?
- Why is MSE common in regression and cross entropy common in classification?
- Why is the gradient of a loss function called a training signal?
- How does the choice between averaging and summing affect optimization scale?
- How can a numerically unstable loss implementation break training?

## Why It Matters

A loss function concretely defines a model's objective. With the same data and the same network, changing the loss changes the direction the model learns. So loss selection is not an implementation detail—it is part of the problem definition.

In practice, monitoring loss curves, correcting class imbalance, and weighting multi-task losses are all connected to loss design. Using a regression loss for a classification problem can cause slow convergence or awkward calibration. Conversely, choosing the right loss gives the optimizer a much more consistent signal.

Understanding the loss also lets you read the gradient not as "a numerical change" but as "the direction in which the gap between prediction and label applies pressure." This sense becomes critical in the gradient descent and optimization articles that follow.

## Core Perspective

The most practical way to understand a loss function is as a device that transforms prediction error from a simple difference into a learnable numerical signal. It encapsulates both how wrong the model output is and what direction of update that wrongness demands.

Loss functions and evaluation metrics have different roles. Metrics are for reading results; loss functions are for generating gradients that drive learning. They may be similar, but in practice it's safest to distinguish "what measures well" from "what trains well."

> A loss function is not just a tool that scores how wrong the prediction is—it is a training signal generator that determines where the model should move on the next step.

## Core Concepts

### MSE is the default loss for regression

```python
def mse(y, p):
    return sum((yi - pi) ** 2 for yi, pi in zip(y, p)) / len(y)
```

MSE squares the difference between prediction and target, then averages. Larger errors receive disproportionately larger penalties. It's common for regression because the implementation is simple, the derivative is smooth, and minimizing average squared error directly matches the regression objective.

### The MSE gradient pushes predictions toward the target

```python
def mse_grad(y, p):
    n = len(y)
    return [-2 * (yi - pi) / n for yi, pi in zip(y, p)]
```

This gradient produces a negative signal when the prediction overshoots and a positive signal when it undershoots. The key takeaway: the loss function doesn't just say "you're wrong"—it provides both the correction direction and magnitude.

### Binary cross entropy is more natural for classification

```python
import math

def bce(y, p, eps=1e-7):
    return -sum(yi * math.log(pi + eps) + (1 - yi) * math.log(1 - pi + eps) for yi, pi in zip(y, p)) / len(y)
```

Binary cross entropy measures the gap between probability predictions and binary labels. When the model fails to assign high probability to the correct class, loss is large. For classification, the fit of the probability distribution matters more than raw error magnitude, making BCE a more natural expression of the problem.

The `eps` term is for numerical stability. `log(0)` is undefined, so practical implementations must guard against extreme values. A loss function must be not only mathematically correct but numerically safe.

### Comparing loss values reveals design differences

```python
y = [1, 0, 1]
p = [0.9, 0.2, 0.7]
loss = bce(y, p)
```

The same predictions receive different penalty structures under different losses. To understand "why the model updated in this direction," look at the loss definition before the optimizer.

### The training signal turns error into movement

```python
def signal(y, p):
    return sum(abs(yi - pi) for yi, pi in zip(y, p)) / len(y)
```

This isn't a formal gradient, but it shows intuitively how much gap remains between predictions and targets. In practice, you monitor actual gradient magnitude, loss slope, and update norm together to judge whether the training signal is sufficient. The key point: loss is not a reporting number—it generates the signal the optimizer consumes.

### Mean vs sum matters more than you think

Whether you average or sum the loss over the batch changes the gradient scale. This directly affects learning rate interpretation. Teams should standardize reduction policy and always verify loss scales match when comparing experiments.

## MSE Derivation and Gradient

For a batch of size `N`:

`L = (1/N) * Σ (y_i - p_i)²`

The derivative with respect to prediction `p_i`:

`dL/dp_i = (2/N) * (p_i - y_i)`

Positive error → reduce prediction. Negative error → increase prediction.

```python
import numpy as np

def mse(y, p):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    return np.mean((y - p) ** 2)

def mse_grad(y, p):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    n = y.size
    return (2.0 / n) * (p - y)

y = np.array([3.0, -1.0, 2.0])
p = np.array([2.2, -0.5, 3.0])
print('mse:', mse(y, p))
print('grad:', mse_grad(y, p))
```

Because errors are squared, MSE is sensitive to large errors. If outliers are common, consider alternatives like Huber loss rather than clinging to MSE.

## Cross Entropy Derivation and Gradient

For binary classification, BCE is:

`L = -(1/N) * Σ [ y_i log(p_i) + (1-y_i) log(1-p_i) ]`

Derivative with respect to `p_i`:

`dL/dp_i = -( y_i/p_i - (1-y_i)/(1-p_i) ) / N`

The gradient is large when the model is confidently wrong (`p` near 0 or 1 but the label is opposite), creating strong corrective pressure.

```python
import numpy as np

def bce(y, p, eps=1e-12):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    p = np.clip(p, eps, 1.0 - eps)
    return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))

def bce_grad(y, p, eps=1e-12):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    p = np.clip(p, eps, 1.0 - eps)
    n = y.size
    return (-(y / p) + (1 - y) / (1 - p)) / n

y = np.array([1, 0, 1, 0], dtype=float)
p = np.array([0.9, 0.3, 0.6, 0.1], dtype=float)
print('bce :', bce(y, p))
print('grad:', bce_grad(y, p))
```

## Reading the Loss Landscape

A loss function produces a single number, but in parameter space it forms terrain. Reading this terrain explains why optimizer settings are sensitive.

```python
import numpy as np

def loss_surface(w1, w2):
    return (w1 - 1.0)**2 + 0.5*(w2 + 2.0)**2 + 0.2*w1*w2

w1s = np.linspace(-3, 3, 7)
w2s = np.linspace(-4, 2, 7)
grid = np.array([[loss_surface(a, b) for b in w2s] for a in w1s])
print(grid)
```

From a contour perspective, check these first:

| Terrain feature | Training effect | Recommended response |
| --- | --- | --- |
| Flat plateau | Small gradient, stalled learning | lr schedule, warmup, better initialization |
| Narrow ravine | Per-axis oscillation | Normalization, momentum, adaptive optimizer |
| Multiple valleys | Initialization dependence | Multi-seed experiments, ensemble |
| Sharp cliff | Numerical instability risk | Gradient clipping, loss stabilization |

## Custom Loss Implementation

In practice, domain constraints often require adding terms to a base loss. For example, regression error + L2 regularization + threshold-violation penalty:

```python
import torch

class HybridLoss(torch.nn.Module):
    def __init__(self, l2_weight=1e-4, threshold=2.0, penalty_weight=0.5):
        super().__init__()
        self.l2_weight = l2_weight
        self.threshold = threshold
        self.penalty_weight = penalty_weight

    def forward(self, pred, target, model_params):
        mse = torch.mean((pred - target) ** 2)
        l2 = torch.zeros((), device=pred.device)
        for p in model_params:
            l2 = l2 + torch.sum(p ** 2)

        excess = torch.relu(torch.abs(pred - target) - self.threshold)
        robust_penalty = torch.mean(excess)

        return mse + self.l2_weight * l2 + self.penalty_weight * robust_penalty
```

When introducing custom losses, always log each term's scale separately. If you only see the total loss, you can't tell which term is dominating training.

## Loss Selection Guide

Loss selection requires looking at both problem type and operational constraints.

| Scenario | Default candidate | Enhancement option | Diagnostic question |
| --- | --- | --- | --- |
| Continuous regression | MSE | Huber, LogCosh | Are outliers common? |
| Binary classification | BCE | Focal Loss, class weight | Is class imbalance large? |
| Multi-class classification | Cross Entropy | Label Smoothing | Is confidence calibration needed? |
| Ranking/recommendation | Pairwise loss | Sampled softmax | Does relative order matter most? |
| Multi-task | Weighted sum | Uncertainty weighting | Are per-task gradient magnitudes balanced? |

Practical order of operations:

1. Start with the standard loss matching your problem type.
2. Observe failure patterns, then add minimal enhancements.
3. When adding terms, monitor each term's scale and gradient norm together.

## Numerical Stability: Rules for Preventing NaN

Loss functions must satisfy not only differentiability but numerical stability. Log/exp operations in particular require stabilization formulas.

```python
import torch

# logits-based BCE uses internally stabilized implementation
criterion = torch.nn.BCEWithLogitsLoss()
logits = torch.tensor([3.0, -2.0, 0.4])
target = torch.tensor([1.0, 0.0, 1.0])
loss = criterion(logits, target)
print(loss)
```

Implementing `sigmoid → BCE` separately increases underflow/overflow risk. Prefer combined stabilized implementations like `BCEWithLogitsLoss`.

Common stabilization rules:

- Before `log(p)`: apply `p = clip(p, eps, 1-eps)`.
- `exp(x)` overflows for large positive `x`: clamp input range.
- Sum-log forms: use the `log-sum-exp` trick.
- Mixed precision: use loss scaling with gradient overflow checking.

| Dangerous operation | Instability condition | Stabilization method |
| --- | --- | --- |
| `log(p)` | `p → 0` | Clipping or logits-based implementation |
| `exp(x)` | `x >> 0` | Input clamping, `torch.logsumexp` |
| `1/p` | `p → 0` | Denominator epsilon |
| softmax | Large logit differences | Max-shift softmax |

## Loss Debugging Routine

When a model isn't learning, checking the loss path is faster than making complex changes.

1. Run forward/backward on a single batch—verify loss and grad are finite (`isfinite`).
2. If loss has multiple terms, log per-term values and per-term gradient norms separately.
3. Compare label distribution, prediction distribution, and threshold-based performance together.
4. Before changing learning rate, verify reduction (mean/sum) consistency in the loss implementation.

```python
def assert_finite(tensor, name):
    if not torch.isfinite(tensor).all():
        raise ValueError(f'{name} contains NaN or Inf')
```

Automating this routine lets you separate loss problems from model architecture problems faster.

## Multi-Class Cross Entropy and Softmax Gradient

For multi-class problems, softmax and cross entropy are used together. With class probability `p_k`:

`L = - Σ y_k log(p_k)`

For one-hot labels, the gradient simplifies to `dL/dz = p - y` (where `z` is logits). This simplification makes the implementation stable and computationally efficient.

```python
import numpy as np

def softmax(z):
    z = z - np.max(z)
    e = np.exp(z)
    return e / np.sum(e)

def ce_with_logits_grad(logits, y_onehot):
    p = softmax(logits)
    return p - y_onehot

logits = np.array([2.0, 0.5, -1.0])
y = np.array([1.0, 0.0, 0.0])
print(ce_with_logits_grad(logits, y))
```

This is why framework `CrossEntropyLoss` expects logits as input. Applying softmax externally then passing to the loss can distort gradients.

## Loss Design for Imbalanced Data

With severe class imbalance, average loss alone weakens minority class learning. Weight-based losses or focal loss provide stronger signal for rare classes.

| Method | Core idea | Advantage | Caution |
| --- | --- | --- | --- |
| Class weight | Adjust per-class loss weight | Simple implementation | Instability if over-weighted |
| Focal loss | Reduce weight on easy samples | Focuses on hard samples | Gamma tuning needed |
| Resampling + standard loss | Correct data distribution | Intuitive | May increase variance |

```python
import torch

criterion = torch.nn.CrossEntropyLoss(weight=torch.tensor([1.0, 3.0, 6.0]))
logits = torch.randn(8, 3)
target = torch.tensor([0, 1, 2, 2, 1, 0, 2, 1])
loss = criterion(logits, target)
print(loss)
```

## Loss Term Weighting in Practice

For multi-task models or hybrid losses, per-term weights can make or break performance. Rather than choosing weights arbitrarily:

1. In the first 100–500 steps, record each term's mean value and gradient norm.
2. If one term dominates the total, reduce its weight.
3. If a term contributes little to validation metric improvement, consider removing it.

| Item | Tracked metric | Interpretation |
| --- | --- | --- |
| Main prediction loss | Mean, variance | Alignment with learning objective |
| Regularization term | Value vs gradient contribution | Whether over-regularized |
| Constraint penalty | Activation rate | Whether constraint actually fires |

## Loss Implementation Unit Tests

Loss functions are small compared to model code, but a small bug can destroy training entirely. Minimal unit tests reduce this risk significantly.

```python
import numpy as np

def test_mse_zero_when_equal():
    y = np.array([1.0, 2.0, 3.0])
    p = np.array([1.0, 2.0, 3.0])
    assert np.isclose(np.mean((y-p)**2), 0.0)

def test_bce_finite():
    y = np.array([0.0, 1.0])
    p = np.array([1e-15, 1-1e-15])
    p = np.clip(p, 1e-12, 1-1e-12)
    loss = -np.mean(y*np.log(p)+(1-y)*np.log(1-p))
    assert np.isfinite(loss)
```

Even these minimal tests catch `log(0)`-family issues before commit.

## Separating Loss from Evaluation Metrics

Training loss can improve while operational metrics worsen. Monitor them separately.

| Category | Purpose | Examples |
| --- | --- | --- |
| Training loss | Gradient generation | MSE, BCE, CE |
| Offline evaluation | Model comparison | RMSE, F1, AUC |
| Online metric | Product performance | CTR, conversion rate, latency |

Loss is designed for optimization convenience; product metrics are defined for business objectives. They rarely align perfectly, so experiment reports should record both axes for accurate decision-making.

## Numerical Stability Regression Tests

Loss implementations can break from library updates or dtype changes. Periodic regression tests maintain stability.

```python
def finite_check(loss_fn, inputs):
    import numpy as np
    vals = [loss_fn(*x) for x in inputs]
    return all(np.isfinite(v) for v in vals)
```

Keeping a fixed set of extreme-logit, extreme-probability, and empty-batch edge cases catches deployment-time failures early.

## Five Common Misconceptions

1. **Using a classification loss for regression** — the optimization signal mismatches the problem structure.
2. **Forgetting to handle log(0)** — a single NaN propagates and kills training.
3. **Confusing mean vs sum scales** — makes learning rate comparisons across experiments invalid.
4. **Forgetting MSE's outlier sensitivity** — the model chases outliers at the expense of majority patterns.
5. **Conflating loss with evaluation metric** — what trains well and what measures well are not the same thing.

## Operational Checklist

- [ ] Select a loss function matching the problem type (regression vs classification).
- [ ] Include numerical stability guards (`eps`, clipping) in the loss implementation.
- [ ] Document whether reduction is mean or sum in experiment settings.
- [ ] Review class imbalance and task weighting needs at the loss design stage.
- [ ] Monitor loss curve and gradient scale together to assess training signal quality.

## Wrap-up and Next Steps

A loss function summarizes the gap between prediction and target as a single number while simultaneously converting that gap into a learning signal via gradients. Choosing a loss that fits the problem structure—MSE for regression, cross entropy for classification—ensures the optimizer reads the correct direction.

In practice, the loss function *is* the problem definition. What errors to penalize more, how to average, how to correct imbalance—all of this lives in loss design. When model performance is unexpected, look at the loss definition before the network architecture.

Next post: *Gradient Descent*—turning loss gradients into actual parameter updates. The calculus intuition built so far will finally connect to the movement of a training loop.

## Answering the Opening Questions

- **How does a loss function differ from a simple evaluation metric?**
  - An evaluation metric reads results; a loss function creates `dL/dp` to drive parameter updates—it's the learning engine. As shown in the MSE/BCE derivations, loss provides not just error magnitude but the correction direction.
- **Why is MSE commonly used for regression and cross entropy for classification?**
  - MSE treats continuous errors with squared penalties that align well with regression objectives, while BCE connects to the likelihood perspective of probability prediction and strongly corrects classification confidence errors. So the problem structure and gradient signal shape each naturally align.
- **Why is the loss function's gradient called a learning signal?**
  - The gradient converts "how wrong" into "which direction and how far to move." Managing this signal quality—including loss landscape, custom loss terms, and numerical stability rules—is what keeps actual training stable.
<!-- toc:begin -->
## In this series

- [Calculus for ML 101 (1/10): What Is a Derivative](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): Functions and Slope](./02-functions-and-slope.md)
- [Calculus for ML 101 (3/10): Partial Derivatives](./03-partial-derivatives.md)
- [Calculus for ML 101 (4/10): Gradient](./04-gradient.md)
- [Calculus for ML 101 (5/10): Chain Rule](./05-chain-rule.md)
- **Loss Function (current)**
- Gradient Descent (upcoming)
- Optimization (upcoming)
- Backpropagation Intuition (upcoming)
- Calculus in Deep Learning (upcoming)

<!-- toc:end -->

## References

- [Loss Functions - PyTorch](https://pytorch.org/docs/stable/nn.html#loss-functions)
- [Cross Entropy - CS231n](https://cs231n.github.io/linear-classify/)
- [Deep Learning Book - Loss](https://www.deeplearningbook.org/contents/mlp.html)
- [Class Imbalance - scikit-learn](https://scikit-learn.org/stable/modules/svm.html#unbalanced-problems)

Tags: Calculus, ML, LossFunction, MSE, Beginner

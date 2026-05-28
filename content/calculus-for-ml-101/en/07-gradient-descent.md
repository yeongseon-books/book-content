---
series: calculus-for-ml-101
episode: 7
title: "Calculus for ML 101 (7/10): Gradient Descent"
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
  - GradientDescent
  - Optimization
  - Beginner
seo_description: A beginner-friendly tour of gradient descent, learning rate, convergence, divergence, and stochastic gradient descent for ML
last_reviewed: '2026-05-15'
---

# Calculus for ML 101 (7/10): Gradient Descent

Knowing the gradient does not train a model by itself. The remaining question is procedural: how do you convert that directional signal into repeated parameter movement that reliably lowers loss? Gradient descent is the basic answer.

This is the 7th post in the Calculus for ML 101 series.

The important point is that gradient descent is not a mathematical curiosity—it is the common skeleton of all modern optimizers. Adam, Momentum, and RMSProp are all variants designed to make basic gradient descent more stable and faster.

In this post, we'll look at the update rule, the role of the learning rate, convergence vs divergence patterns, and SGD/mini-batch behavior. Once that clicks, loss curves stop feeling like random charts and start looking like readable optimization traces.

By the end, you'll naturally explain why learning rate is the first suspect when a loss curve looks wrong.

> Gradient descent is not magic. It is a repeated decision about how far to move against the local slope that the loss is showing you right now.

![calculus for ml 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/07/07-01-concept-at-a-glance.en.png)
*calculus for ml 101 chapter 7 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Gradient Descent?
- Which signal should the example or diagram make visible for Gradient Descent?
- What failure should be prevented first when Gradient Descent reaches a real system?

## Questions this article answers

- Why does moving in the direction opposite the gradient reduce the loss?
- What does the learning rate do beyond acting as a simple multiplier?
- How can you tell the difference between convergence and divergence in gradient descent?
- What changes when you use the full-dataset gradient versus SGD or mini-batch gradients?
- How do initialization and gradient noise affect the optimization path?

## Why It Matters

Most ML training runs on a variant of gradient descent. The loss function defines the objective and the gradient provides direction, but gradient descent is the execution procedure that connects those two into actual parameter updates. Without this connection, calculus never becomes model training.

In practice, one of the most common causes of training failure is learning rate configuration. Too large causes divergence; too small causes near-zero movement; the appropriate value changes with data scale, initialization, and batch size. Without understanding how gradient descent works, it's easy to blame the optimizer name rather than diagnosing the actual dynamics.

Understanding the noise from SGD and the trade-offs from mini-batching also lets you read loss curve fluctuations naturally. This intuition carries directly into the next article on advanced optimizers.

## Core Perspective

Gradient descent is essentially a very simple loop. Compute the gradient at the current parameters, scale it by the learning rate, and move in the opposite direction. Repeat this loop to lower loss.

But this simplicity reveals the core clearly. Direction is determined by the gradient; step size is determined by the learning rate. So when training behaves oddly, you can almost always decompose the problem: "Is the direction wrong, or is the step size inappropriate?"

> Gradient descent is not a magic loss-reduction machine. It is a repeated procedure that decides how cautiously to walk in the direction opposite to what the gradient says.

## Core Concepts

### Start with the simplest loss and gradient

```python
def loss(w):
    return (w - 3) ** 2

def grad(w):
    return 2 * (w - 3)
```

This loss has its minimum at `w=3`. The gradient tells you whether the current position is left or right of the minimum, and by how much. Gradient descent uses this gradient in reverse to move toward the minimum.

### A single step is very simple

```python
def step(w, lr=0.1):
    return w - lr * grad(w)
```

Here `lr` is the learning rate. Direction is determined by the sign of `grad(w)`; actual travel distance is controlled by `lr`. The same gradient with 10× larger lr produces 10× larger updates. That's why learning rate is the first hyperparameter you adjust.

### Training is this step repeated

```python
def train(w0, lr=0.1, steps=100):
    w = w0
    for _ in range(steps):
        w = step(w, lr)
    return w
```

More repetitions move the parameter closer to the minimum. Real deep learning involves multi-dimensional, non-convex losses with noisy gradients, but the basic loop is the same.

### SGD updates from partial data

```python
import random

def sgd(data, w0, lr=0.01, epochs=10):
    w = w0
    for _ in range(epochs):
        random.shuffle(data)
        for x in data:
            w -= lr * 2 * (w - x)
    return w
```

Full-batch GD uses the gradient over all data; SGD uses a single sample or a very small batch. The gradient becomes noisy but cheap to compute, and sometimes that noise helps escape flat regions or improves generalization.

### Learning rate changes the trajectory

```python
for lr in [0.001, 0.1, 1.5]:
    print(lr, train(0.0, lr, 50))
```

Small lr is stable but slow; large lr can be fast but risks oscillating past the minimum or diverging entirely. So when reading a loss curve, don't just check whether it goes down—also look for oscillation, plateau trapping, or sudden blowup.

### Initialization and noise also change the path

With the same algorithm, different initial parameters and data ordering produce different optimization paths. In non-convex deep learning losses, these differences are amplified. Recording seed, initialization, and batching policy is essential for reproducibility.

## Pure Gradient Descent Implementation and Log Interpretation

To build intuition, run the simplest possible GD on a quadratic function:

```python
import numpy as np

def f(w):
    return (w - 4.0) ** 2 + 1.0

def grad(w):
    return 2.0 * (w - 4.0)

def vanilla_gd(w0, lr, steps):
    w = float(w0)
    hist = []
    for t in range(steps):
        g = grad(w)
        hist.append((t, w, f(w), g))
        w = w - lr * g
    return hist

hist = vanilla_gd(w0=-3.0, lr=0.1, steps=10)
for row in hist[:5]:
    print(row)
```

When reading logs, you must look at `w`, `loss`, and `grad` together. Loss alone shows whether it decreases, but not *why* it's slow or oscillating.

| Log signal | Meaning | Action |
| --- | --- | --- |
| `\|grad\|` large, loss drops significantly | Normal early descent | Keep lr |
| `\|grad\|` small, loss barely changes | Flat region | lr schedule or momentum |
| Loss alternates increase/decrease | Step too large | Reduce lr |

## Batch Method Comparison: Batch vs Mini-Batch vs Stochastic

The same gradient descent behaves differently depending on which data subset computes the gradient.

- Batch GD: full-dataset gradient, stable but expensive.
- Mini-batch GD: small batch, the standard choice in modern deep learning.
- SGD: single-sample, maximum noise but fastest response.

```python
import numpy as np

def grad_linear_mse(x, y, w, b):
    pred = x * w + b
    err = pred - y
    dw = 2.0 * np.mean(err * x)
    db = 2.0 * np.mean(err)
    return dw, db

def sample_batch(x, y, batch_size):
    idx = np.random.choice(len(x), batch_size, replace=False)
    return x[idx], y[idx]
```

| Method | Gradient noise | Compute cost | Convergence behavior |
| --- | --- | --- | --- |
| Batch | Low | High | Smooth but can be slow |
| Mini-batch | Medium | Medium | Speed/stability balance |
| SGD | High | Low | Noisy but can escape local minima |

In practice, mini-batch is the default, with batch size tuned considering GPU efficiency, memory, and generalization.

## Learning Rate Experiment Design

Learning rate should be treated as an experiment design target, not a single fixed value. Even with the same model, the optimal range shifts with data scale and initialization.

```python
def run_lr_sweep(train_fn, lrs):
    results = []
    for lr in lrs:
        final_loss = train_fn(lr)
        results.append((lr, final_loss))
    return results
```

Recommended procedure:

1. Sweep broadly on a log scale (`1e-4, 3e-4, 1e-3, ...`).
2. Fine-search around the best region.
3. If fixed lr is unstable, apply decay, cosine, or warmup schedule.

| Observation | lr interpretation | Response |
| --- | --- | --- |
| Loss diverges from the start | lr too large | Reduce by 3–10× |
| Monotone decrease but very slow | lr too small | Increase 2–3× |
| Stalls after midway | Fixed lr limit | Introduce schedule |
| Sudden instability at a specific epoch | Interaction with data/regularization | Check lr + batch + clipping together |

## Convergence Condition Intuition

In theory, under Lipschitz-continuous gradient assumptions, step size upper bounds are given. In practice, interpret this as "steps too large overshoot the minimum."

For a 1D quadratic `f(w) = a(w - w*)²`:

`w_{t+1} = w_t - lr * 2a(w_t - w*)`

Error `e_t = w_t - w*` evolves as:

`e_{t+1} = (1 - 2a·lr)·e_t`

Convergence requires `|1 - 2a·lr| < 1`.

```python
import numpy as np

def simulate(a, lr, e0=5.0, steps=10):
    e = e0
    out = []
    for t in range(steps):
        out.append((t, e))
        e = (1 - 2*a*lr) * e
    return out

print(simulate(a=1.0, lr=0.4)[:5])
```

This matches practical intuition: higher curvature `a` makes the same lr more dangerous.

## Momentum Intuition and Basic Implementation

Momentum accumulates past update directions as inertia rather than using only the current gradient. It reduces zig-zagging in narrow valleys and accelerates in consistent directions.

```python
def momentum_step(w, g, v, lr=0.01, beta=0.9):
    v = beta * v + (1 - beta) * g
    w = w - lr * v
    return w, v
```

| Scenario | Pure GD | Momentum |
| --- | --- | --- |
| Valley with curvature imbalance | Frequent oscillation | Dampened oscillation |
| Long gentle slope | Slow progress | Accumulation speeds up |
| Noisy SGD | High variance | Averaging effect |

Momentum still requires lr tuning, and excessive `beta` can delay response to direction changes.

## Gradient Descent on Non-Convex Surfaces

Deep learning losses are generally non-convex. Global minimum guarantees are impractical—you must handle saddle points, flat regions, and multiple local minima.

```python
import numpy as np

# saddle-point toy function
def saddle(w):
    x, y = w
    return x**2 - y**2 + 0.1*(x**4 + y**4)

def saddle_grad(w):
    x, y = w
    return np.array([2*x + 0.4*x**3, -2*y + 0.4*y**3])
```

Common observations on non-convex surfaces:

| Phenomenon | Description | Response |
| --- | --- | --- |
| Stalling near saddle point | One axis descends, another ascends | Use noise, momentum, or restarts |
| Performance variance across local minima | Depends on initialization/shuffle | Multi-seed experiments |
| Slow progress in flat regions | Gradient too small | lr schedule, adaptive optimizer |

The goal of gradient descent in practice is almost always "finding a reproducibly good solution" rather than "finding the perfect global minimum."

## Operational Checkpoints: Stabilizing the Training Loop

In production training loops, instrumentation comes before algorithm choice. Standardizing these log items accelerates failure diagnosis:

1. Record train loss and val loss separately per step/epoch.
2. Log total grad norm and update norm together.
3. Include lr schedule value in logs to correlate with curve changes.
4. Store batch size and data shuffle seed as experiment metadata.

```python
def log_step(step, loss, grad_norm, lr):
    print({'step': step, 'loss': float(loss), 'grad_norm': float(grad_norm), 'lr': float(lr)})
```

With these logs, you replace vague "the model is bad" conclusions with actionable diagnoses: "lr too large," "gradient explosion," or "batch noise too high."

## Mini-Batch Training Loop: Full Example

Connecting gradient descent to a real training loop means viewing data shuffling, batch iteration, and validation logging as one unit.

```python
import numpy as np

def train_epoch(x, y, w, b, lr=0.01, batch_size=16):
    n = len(x)
    order = np.random.permutation(n)
    x, y = x[order], y[order]

    losses = []
    for i in range(0, n, batch_size):
        xb = x[i:i+batch_size]
        yb = y[i:i+batch_size]
        pred = xb * w + b
        err = pred - yb
        loss = np.mean(err**2)
        dw = 2*np.mean(err*xb)
        db = 2*np.mean(err)
        w -= lr * dw
        b -= lr * db
        losses.append(loss)
    return w, b, float(np.mean(losses))
```

With this structure, swapping only the optimizer keeps the experiment fair.

## Learning Rate Schedule Comparison

Fixed learning rate isn't always best. Exploring broadly early and fine-tuning later often improves convergence quality.

| Schedule | Concept | Advantage | Disadvantage |
| --- | --- | --- | --- |
| Step decay | Reduce lr at fixed epochs | Simple, interpretable | Abrupt transitions |
| Cosine decay | Gradual cosine-shaped reduction | Smooth transitions | Extra hyperparameter |
| Warmup + decay | Small lr initially, then increase/decrease | Stabilizes large models | Complex to configure |

```python
def cosine_lr(base_lr, step, total_steps):
    import math
    return base_lr * 0.5 * (1 + math.cos(math.pi * step / total_steps))
```

## Convergence Criteria: Making Them Explicit

"It seems to be going down" is not a reproducible stopping criterion. Specify termination numerically:

1. Check if recent `k`-step mean loss improvement is below a threshold.
2. Verify grad norm is small enough with low variance.
3. Early-stop if validation performance doesn't improve for an extended period.

| Criterion | Example threshold | Interpretation |
| --- | --- | --- |
| `Δloss_ma` | `< 1e-5` | Convergence or stagnation |
| `grad_norm` | `< 1e-4` | Possibly near local minimum |
| `val metric patience` | `10 epochs` | Generalization improvement stalled |

## Restart Strategy for Non-Convex Landscapes

Trusting a single training path on a non-convex loss risks getting stuck in an accidental local minimum. Restart strategies are simple but effective:

- Run 3–5 independent trainings with different seeds.
- Compare final validation metrics and stability logs across runs.
- Select models based on variance, not just peak score.

```python
def multi_seed(train_fn, seeds):
    out = []
    for s in seeds:
        np.random.seed(s)
        out.append((s, train_fn()))
    return out
```

This approach secures "reproducible performance."

## Momentum vs Pure GD: Update Magnitude Comparison

Even with the same lr, momentum changes the effective update size. So matching lr numbers alone doesn't make a fair comparison.

| Comparison item | Pure GD | Momentum GD |
| --- | --- | --- |
| Current gradient dependence | 100% | Partial + past accumulation |
| Oscillation suppression | Weak | Strong |
| Initial response speed | Immediate | Slightly delayed |
| Hyperparameters | lr | lr + beta |

In operations, record `update_norm` alongside loss to compare actual travel distance.

## Reproducibility: The Prerequisite for GD Comparisons

Without reproducibility, conclusions about learning rate and optimizer comparisons are unstable. At minimum, record these as experiment metadata:

| Item | Example |
| --- | --- |
| Random seed | `seed=42` |
| Data shuffle policy | Shuffle every epoch or not |
| Batch size | `batch_size=64` |
| Initialization method | Xavier/He/normal |
| lr schedule | cosine, step, etc. |

```python
import numpy as np

def set_seed(seed):
    np.random.seed(seed)
```

This information looks minor, but whether you can reproduce the same curve determines debugging efficiency.

## Learning Rate–Batch Size Joint Tuning

Changing batch size alters gradient variance, so learning rate typically needs adjustment too. Generally, larger batches tolerate somewhat larger lr, but the relationship isn't strictly linear.

| Change | Expected effect | Caution |
| --- | --- | --- |
| Batch increase | Gradient variance decreases | Possible generalization degradation |
| lr increase | Potentially faster convergence | Increased divergence risk |
| Both adjusted | Throughput improvement | Increased tuning cost |

In practice, run a small search grid first, then fine-tune in the most stable region.

## Five Common Misconceptions

1. **Setting the learning rate far too high** — loss diverges immediately but people blame the model.
2. **Using the same lr for differently-scaled weights** — some parameters over-update, others barely move.
3. **Stopping before convergence** — mistaking slow progress for a fundamental problem.
4. **Treating SGD noise as failure** — some fluctuation is normal and even beneficial.
5. **Initializing all weights to zero** — symmetry prevents learning in many architectures.

## Operational Checklist

- [ ] Compare at least 2–3 learning rate candidates via sweep.
- [ ] Read convergence, oscillation, and divergence patterns in the loss curve.
- [ ] Distinguish normal SGD/mini-batch noise from actual errors.
- [ ] Record initialization and seed for experiment reproducibility.
- [ ] Before blaming the optimizer, first interpret basic gradient and lr dynamics.

## Wrap-up and Next Steps

Gradient descent reduces loss by repeatedly taking small steps opposite to the gradient. Direction comes from the gradient; step size comes from the learning rate. This simple structure is the starting point for virtually all modern optimizers.

The most important practical sense is learning rate interpretation. Divergence, slow convergence, and noisy curves are almost always explainable from basic GD elements. So before switching optimizers, always read the phenomenon from a vanilla GD perspective first.

Next post: *Optimization*—momentum, RMSProp, Adam, and other techniques that compensate for plain GD's weaknesses.

## Answering the Opening Questions

- **Why does moving in the opposite direction of the gradient reduce loss?**
  - The gradient is locally the steepest ascent direction, so its opposite is the steepest descent. The pure GD implementation and quadratic function simulation confirmed loss actually decreasing at each step along this path.
- **What role does learning rate play beyond a simple multiplier?**
  - Learning rate is the key control value converting an identical gradient into actual travel distance. As the lr sweep experiment shows, it simultaneously determines convergence speed, oscillation, and divergence risk—governing a substantial portion of optimizer performance.
- **How can you distinguish convergence from divergence patterns in gradient descent?**
  - Convergence is accompanied by decreasing loss and stabilizing grad norm; divergence manifests as loss spikes, oscillation, or abnormal norm growth. Interpreting batch method, momentum, and non-convex surface characteristics together lets you concretely determine which settings to adjust.
<!-- toc:begin -->
## In this series

- [Calculus for ML 101 (1/10): What Is a Derivative](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): Functions and Slope](./02-functions-and-slope.md)
- [Calculus for ML 101 (3/10): Partial Derivatives](./03-partial-derivatives.md)
- [Calculus for ML 101 (4/10): Gradient](./04-gradient.md)
- [Calculus for ML 101 (5/10): Chain Rule](./05-chain-rule.md)
- [Calculus for ML 101 (6/10): Loss Function](./06-loss-function.md)
- **Gradient Descent (current)**
- Optimization (upcoming)
- Backpropagation Intuition (upcoming)
- Calculus in Deep Learning (upcoming)

<!-- toc:end -->

## References

- [Gradient Descent - CS231n](https://cs231n.github.io/optimization-1/)
- [Adam Optimizer - Kingma and Ba](https://arxiv.org/abs/1412.6980)
- [Deep Learning Book - Optimization](https://www.deeplearningbook.org/contents/optimization.html)
- [PyTorch Optimizers](https://pytorch.org/docs/stable/optim.html)

Tags: Calculus, ML, GradientDescent, Optimization, Beginner

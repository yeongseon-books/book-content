---
series: calculus-for-ml-101
episode: 8
title: "Calculus for ML 101 (8/10): Optimization"
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
  - Optimization
  - Adam
  - Beginner
seo_description: A beginner-friendly tour of momentum, RMSProp, Adam, learning-rate schedules, and regularization for ML optimization
last_reviewed: '2026-05-15'
---

# Calculus for ML 101 (8/10): Optimization

Plain gradient descent gives you the basic learning loop, but real deep learning losses are rougher than that simple picture suggests. Valleys can be long and narrow, gradient scale can vary by coordinate, and the first few hundred steps may need very different behavior from the last few thousand.

This is the 8th post in the Calculus for ML 101 series.

In this post, we'll treat momentum, RMSProp, Adam, schedules, and regularization as one optimization toolkit. The goal is not to memorize optimizer names, but to see which weakness of plain gradient descent each tool is trying to fix.

By the end, you'll choose an optimizer not because "everyone uses Adam," but because you can match the optimizer's design intent to the current loss landscape and training stage.

> Modern optimizers do not replace gradient descent with unrelated magic. They are gradient descent with extra machinery for stability, scale mismatch, and stage-specific control.


![calculus for ml 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/08/08-01-concept-at-a-glance.en.png)
*calculus for ml 101 chapter 8 flow overview*

## Questions to Keep in Mind

- Where does plain gradient descent start to break down in real deep learning training?
- Why is momentum easiest to understand through the metaphor of inertia?
- How do RMSProp and Adam reduce coordinate-wise differences in gradient scale?

## Why It Matters

In practice, the optimizer is the center of the training recipe. The same model and data can produce very different convergence speeds and final performance depending on optimizer, learning-rate schedule, and weight decay settings. So optimization is not "post-calculus detail"—it is the operational layer that actually makes training succeed.

In large-scale models especially, the absence of warmup can cause divergence, the absence of adaptive methods can leave coordinate-scale differences unresolved, and the absence of a schedule can make late-stage fine-tuning too coarse. In short, an optimizer is not a single function call—it is a policy bundle that decides how to interpret, accumulate, and decay gradients.

Regularization also needs to be viewed alongside optimization. If the only goal were to reduce loss, the model would easily drift toward overfitting. A good optimizer is not just fast; it must steer training toward generalizable solutions.

## Core Perspective

The most practical way to understand optimization is to first observe where plain GD struggles. It oscillates in narrow valleys, it is vulnerable to per-coordinate gradient-scale differences, it is unstable early, and too coarse late. Momentum, RMSProp, Adam, and schedules each address one of these weaknesses.

Viewed this way, optimizers are not separate magic boxes but clearly intentioned patches. The reason optimizer tuning is possible in practice is that each component targets a fairly clear problem.

> Modern optimizers are not replacements for gradient descent—they are reinforced versions built to withstand the roughness of the loss landscape, the imbalance of gradient scales, and the stage-specific demands of training.

## Core Concepts

### Momentum adds directional consistency

```python
def momentum_step(w, v, g, lr=0.1, beta=0.9):
    v = beta * v + g
    return w - lr * v, v
```

Momentum smooths updates by using a running mean of past gradients alongside the current one. When the landscape is a long, narrow valley, it helps the optimizer travel along the main descent direction instead of oscillating side to side. That is why the inertia analogy works: the optimizer trusts the "recent travel direction" more than a single noisy gradient.

### RMSProp softens coordinate-wise scale differences

```python
def rms_step(w, s, g, lr=0.01, beta=0.99, eps=1e-8):
    s = beta * s + (1 - beta) * g * g
    return w - lr * g / (s ** 0.5 + eps), s
```

RMSProp adaptively scales each coordinate's step size using a running mean of squared gradients. If a coordinate consistently has large gradients, its update is automatically dampened. This makes it far easier to train parameters of very different scales under a single learning rate.

### Adam combines momentum and RMSProp

```python
def adam_step(w, m, v, g, t, lr=0.001, b1=0.9, b2=0.999, eps=1e-8):
    m = b1 * m + (1 - b1) * g
    v = b2 * v + (1 - b2) * g * g
    mh = m / (1 - b1 ** t)
    vh = v / (1 - b2 ** t)
    return w - lr * mh / (vh ** 0.5 + eps), m, v
```

Adam takes directional consistency and adaptive scaling simultaneously. Its defaults provide a strong starting point, but that does not mean tuning is unnecessary. The full recipe includes learning rate, betas, weight decay, and warmup policy.

### Schedules change step size over training stages

```python
def cosine_lr(step, total, lr0=0.01):
    import math
    return 0.5 * lr0 * (1 + math.cos(math.pi * step / total))
```

It is common to explore broadly early and fine-tune with smaller steps late. A cosine schedule implements this pattern smoothly. In large-scale training, warmup is combined with the schedule to avoid applying large learning rates to unstable early gradients.

### Regularization is a brake for generalization

```python
def l2_step(w, g, lr=0.1, wd=1e-4):
    return w - lr * (g + wd * w)
```

L2 regularization suppresses overly large parameters and aids generalization. In modern frameworks, however, it is important to distinguish between L2 penalty and decoupled weight decay. They look similar but bind to the optimizer differently.

### Optimization is a recipe, not a single knob

In practice, "using Adam" is never the full story. Initial learning rate, warmup length, schedule shape, weight decay, gradient clipping, and batch size all work together. So when diagnosing an optimization problem, you inspect the entire recipe rather than a single hyperparameter.

## Adam: Full Formula Expansion

Adam simultaneously tracks a first moment (gradient mean) and a second moment (gradient-squared mean). The core equations:

$$
m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t, \quad
v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2
$$

Because `m_0=0` and `v_0=0`, early estimates are biased toward zero. Bias correction fixes this:

$$
\hat{m}_t = \frac{m_t}{1-\beta_1^t}, \quad
\hat{v}_t = \frac{v_t}{1-\beta_2^t}
$$

The final update:

$$
\theta_{t+1} = \theta_t - \alpha \frac{\hat{m}_t}{\sqrt{\hat{v}_t}+\epsilon}
$$

Interpreting per-coordinate: coordinates with large `v_hat` get automatically smaller steps, while `m_hat` stably accumulates the recent gradient direction. Adam thus performs oscillation dampening and per-coordinate scale correction simultaneously.

### Numerical Example

Initial values: `w=1.0`, `g1=0.3`, `alpha=0.001`, `beta1=0.9`, `beta2=0.999`.

| Step | Value |
| --- | --- |
| t=1, m1 | `0.1*0.3 = 0.03` |
| t=1, v1 | `0.001*0.09 = 0.00009` |
| t=1, m_hat | `0.03/0.1 = 0.3` |
| t=1, v_hat | `0.00009/0.001 = 0.09` |
| Update size | `0.001 * 0.3 / (sqrt(0.09)+eps) ≈ 0.001` |

Without bias correction, `m` and `v` are underestimated in early steps, distorting the update magnitude. That is why bias correction is practically mandatory in Adam implementations.

### Implementation Details Often Missed

- `eps` is not just a divide-by-zero guard—it also limits step size in regions of very small variance.
- Setting `beta2` too small makes the variance estimate noisy, leading to unstable loss curves.
- In mixed precision training, gradient scale and Adam denominator stability (`eps`) must be checked together.

## Learning-Rate Schedule Design

If the optimizer determines direction, the scheduler sets time-axis policy. The same Adam with different schedules yields entirely different training trajectories.

### Step Decay

Reduce learning rate by a fixed factor every N epochs:

$$
\alpha_t = \alpha_0 \cdot \gamma^{\lfloor t/s \rfloor}
$$

```python
def step_lr(step, base_lr=1e-3, drop_every=1000, gamma=0.5):
    return base_lr * (gamma ** (step // drop_every))
```

- Pros: simple, easy to interpret.
- Cons: loss curve can bend sharply at boundary points.

### Cosine Decay

Smoothly decays from initial learning rate toward a minimum:

$$
\alpha_t = \alpha_{min} + \frac{1}{2}(\alpha_{max}-\alpha_{min})(1 + \cos(\pi t/T))
$$

```python
import math

def cosine_lr(step, total_steps, lr_max=1e-3, lr_min=1e-5):
    ratio = step / total_steps
    return lr_min + 0.5 * (lr_max - lr_min) * (1 + math.cos(math.pi * ratio))
```

- Pros: smooth late-stage fine-tuning, low divergence risk.
- Cons: requires knowing total step count approximately.

### Warmup + Main Schedule

Large-batch or Transformer training often faces unstable early gradients. Warmup linearly ramps the learning rate for the first N steps, then hands off to the main schedule (typically cosine):

```python
def warmup_cosine(step, warmup_steps, total_steps, lr_max=3e-4, lr_min=3e-5):
    if step < warmup_steps:
        return lr_max * (step + 1) / warmup_steps
    progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
    import math
    return lr_min + 0.5 * (lr_max - lr_min) * (1 + math.cos(math.pi * progress))
```

### Schedule Selection Guide

| Situation | Recommended Schedule | Reason |
| --- | --- | --- |
| Small model, fast experiments | Step decay | Tuning simplicity |
| Long training, late-stage precision | Cosine | Smooth decay |
| Large batch, frequent early divergence | Warmup + Cosine | Early stability + late performance |

## Weight Decay vs L2 Regularization

On the surface, both add a term that shrinks `w`, so they look identical. But in adaptive optimizers the equivalence breaks.

### L2 Penalty

Adding `λ/2 ||w||^2` to the loss changes the gradient to `g + λw`. The regularization term is coupled into the gradient path.

### Decoupled Weight Decay (AdamW)

AdamW decays parameters directly, separately from the gradient path:

$$
\theta_{t+1} = \theta_t - \alpha \cdot \text{AdamUpdate}(g_t) - \alpha \lambda \theta_t
$$

This keeps the adaptive denominator and regularization from mixing, making hyperparameter interpretation more consistent.

### Comparison Table

| Aspect | L2 Penalty (Adam) | Decoupled WD (AdamW) |
| --- | --- | --- |
| Application point | Inside gradient | Outside parameter update |
| Affected by adaptive denominator | Yes | No |
| Tuning interpretation | Entangled | Relatively clear |
| Practice recommendation | Limited | Generally recommended |

## Optimizer Comparison Table

| Optimizer | Core Idea | Strengths | Weaknesses | Starting Point |
| --- | --- | --- | --- | --- |
| SGD | Current gradient only | Simple, low memory | Slow on rough landscapes | lr≈0.1 |
| SGD+Momentum | Direction accumulation | Oscillation dampening, good generalization | lr sensitive | lr=0.1, m=0.9 |
| RMSProp | Per-coordinate variance correction | Handles anisotropic landscapes | Weak long-term memory | lr=1e-3 |
| Adam | Moment + variance combined | Fast early convergence | Generalization not always best | lr=1e-3 |
| AdamW | Adam + decoupled WD | Stable for large models | wd tuning needed | lr=3e-4, wd=0.01 |

## Hyperparameter Tuning Strategy

Tuning is not blind grid search—it is about following failure signals in a principled order.

### 1) Learning Rate Range Test

Start at a very small value, increase per step, and find the point where loss starts worsening. Use the value just before that as the initial learning-rate candidate:

```python
def lr_range_test(model, optimizer, data_loader, lr_start=1e-6, lr_end=1, steps=200):
    mult = (lr_end / lr_start) ** (1 / steps)
    lr = lr_start
    for i, batch in enumerate(data_loader):
        if i >= steps:
            break
        for pg in optimizer.param_groups:
            pg['lr'] = lr
        loss = model.training_step(batch)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        print(i, lr, float(loss))
        lr *= mult
```

### 2) Tune wd Separately from lr

Fix `lr` first, then compare `wd` across `0, 1e-4, 1e-3, 1e-2`. This isolates the overfitting-suppression effect more cleanly.

### 3) Re-adjust with Batch Size

Larger batch reduces gradient variance, creating room to raise lr. Conversely, smaller batches often need lower lr or longer warmup.

### 4) Log-Based Diagnostics

Recording these metrics on the same x-axis (step) speeds up root-cause isolation:

| Logged Metric | Interpretation |
| --- | --- |
| train loss | Optimization progress speed |
| val loss | Generalization trend |
| grad norm | Explosion/vanishing signal |
| lr | Schedule effect |
| parameter norm | wd/L2 effect |

## Practical Selection Guide

### Small data, fast iteration experiments

- Start with `Adam(lr=1e-3)`.
- If early divergence in the first 5–10 epochs, lower to `lr=3e-4`.
- If overfitting appears, switch to `AdamW(wd=1e-3~1e-2)`.

### Image/language large-scale pretraining or fine-tuning

- Default recipe: `AdamW + warmup + cosine`.
- Warmup ratio: start at 1–5% of total steps.
- Apply gradient clipping to limit large early updates.

### When generalization performance is critical

- Keep `SGD+Momentum` as a strong baseline.
- Convergence may be slower, but check if final val metric is higher.
- Compare at the same wall-clock or same step count, not same epoch count.

## Verifiable Mini-Experiment Design

Running the same model with only the optimizer changed, and logging results, makes it easy to explain your choice to the team:

| Experiment | Config | Observation Point |
| --- | --- | --- |
| A | Adam, lr=1e-3 | Early loss descent speed |
| B | AdamW, lr=3e-4, wd=0.01 | Val stability |
| C | SGD+Momentum, lr=0.1 | Final generalization |

Experiment logs must include `seed`, `batch size`, `augmentation`, and `scheduler` together. If you think you only changed the optimizer but other conditions leaked in, the conclusions are invalid.

## AdamW Implementation: Parameter Groups and Exclusion Rules

In production training code, you do not apply the same weight decay to all parameters. Typically, bias and normalization-layer parameters are excluded from decay:

```python
import torch

def build_param_groups(model, wd=0.01):
    decay, no_decay = [], []
    for n, p in model.named_parameters():
        if not p.requires_grad:
            continue
        if n.endswith('bias') or 'norm' in n.lower():
            no_decay.append(p)
        else:
            decay.append(p)
    return [
        {'params': decay, 'weight_decay': wd},
        {'params': no_decay, 'weight_decay': 0.0},
    ]

optimizer = torch.optim.AdamW(build_param_groups(model), lr=3e-4, betas=(0.9, 0.999), eps=1e-8)
```

This pattern prevents normalization-layer scale/shift parameters from being excessively shrunk by decay.

## Learning-Rate Schedule Mistake Patterns

| Mistake | Result | Fix |
| --- | --- | --- |
| Starting with large lr without warmup | Early loss spike, NaN | Add 1–5% warmup |
| Misplacing `scheduler.step()` | lr curve distortion | Explicitly document epoch/step basis |
| Miscalculating total_steps | Cosine decay timing error | Recompute from dataloader length |
| Not restoring scheduler state on resume | Performance wobble after restart | Include scheduler state in checkpoint |

```python
# Step-based scheduler example
for step, batch in enumerate(loader):
    loss = training_step(batch)
    loss.backward()
    optimizer.step()
    scheduler.step()  # step-based: after optimizer
    optimizer.zero_grad()
```

## Optimizer Decision Tree

This tree provides a quick default for picking an optimizer within a team:

1. **Is early convergence too slow?**
   - Symptom: loss barely decreases for 1–2 epochs.
   - Action: Start with AdamW and run lr range test first.
2. **Is validation performance unstable late?**
   - Action: Lower the cosine minimum lr and slightly increase wd.
3. **Is training stable but final generalization low?**
   - Action: Run an SGD+Momentum baseline in parallel.
4. **Is the batch small and gradients noisy due to memory constraints?**
   - Action: Combine gradient accumulation with warmup.

| Observed Symptom | Primary Hypothesis | First Adjustment |
| --- | --- | --- |
| Large loss oscillation | lr too high, momentum too strong | Halve lr, keep beta1=0.9 |
| Val gap widening | Insufficient regularization | Increase wd, check augmentation |
| Late plateau | Insufficient lr decay | Lower cosine min lr |
| Early NaN | Scale instability | Add warmup, apply clipping |

The decision tree is not a perfect answer key—it is a shared language for narrowing failures quickly. Checking the same symptoms in the same order significantly reduces experiment iteration cost.

## Common Confusions

- Adam's strong defaults do not mean it is always optimal.
- Treating L2 regularization and decoupled weight decay as identical can misalign your analysis.
- Maintaining a fixed learning rate without any schedule can make late-stage fine-tuning too coarse.
- Blaming early divergence solely on optimizer type can mask the real issue: missing warmup.
- Ignoring momentum-state handling on checkpoint resume can silently alter the training trajectory.

## Checklist

- [ ] Can explain optimizer choice in terms of loss landscape and gradient scale
- [ ] Defined a learning-rate policy including warmup, main schedule, and final decay
- [ ] Manage weight decay or regularization settings as an explicitly separated concern
- [ ] Include optimizer state restoration policy in experiment configuration for restarts
- [ ] When diagnosing performance issues, inspect the entire optimization recipe alongside model architecture

## Wrap-up and Next Steps

Optimization is a collection of reinforcement techniques designed to make plain gradient descent faster and more stable. Momentum provides directional consistency, RMSProp provides per-coordinate adaptiveness, and Adam combines both. Schedules and regularization complete the real training loop.

In practice, the recipe matters more than the optimizer name. Learning rate, warmup, weight decay, and gradient clipping must be designed together for the same model to train properly. That is why optimization is closer to "how you handle gradients" than "which algorithm you picked."

Next post: *Backpropagation Intuition*—how the gradient that feeds into this optimization is efficiently computed across the entire network.

## Answering the Opening Questions

- **Where does plain gradient descent break down in actual deep learning training?**
  As confirmed in this article, plain GD cannot directly compensate for per-coordinate gradient scale differences, oscillations grow in narrow valleys, and it cannot reflect the step size changes needed at different training stages. That's why practice requires recipes combining momentum, adaptive scaling, and schedulers.
- **Why is momentum most easily explained with the inertia analogy?**
  Momentum accumulates past gradients as an exponential moving average and reflects them in the current update direction. It trusts the "recent travel direction" more than a single noisy gradient, reducing zigzag while maintaining the main descent direction—so the physical inertia analogy most accurately conveys the operating principle.
- **How do RMSProp and Adam mitigate per-coordinate gradient scale differences?**
  RMSProp creates a denominator from the per-coordinate moving average of `g^2`, reducing the step for large-gradient coordinates. Adam adds a first moment on top and applies bias correction to reduce early-stage distortion. The net effect is stable training of parameters with different scales under the same lr.
<!-- toc:begin -->
## In this series

- [Calculus for ML 101 (1/10): What Is a Derivative](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): Functions and Slope](./02-functions-and-slope.md)
- [Calculus for ML 101 (3/10): Partial Derivatives](./03-partial-derivatives.md)
- [Calculus for ML 101 (4/10): Gradient](./04-gradient.md)
- [Calculus for ML 101 (5/10): Chain Rule](./05-chain-rule.md)
- [Calculus for ML 101 (6/10): Loss Function](./06-loss-function.md)
- [Calculus for ML 101 (7/10): Gradient Descent](./07-gradient-descent.md)
- **Optimization (current)**
- Backpropagation Intuition (upcoming)
- Calculus in Deep Learning (upcoming)

<!-- toc:end -->

## References

- [Adam - Kingma and Ba](https://arxiv.org/abs/1412.6980)
- [Optimizer Overview - Ruder](https://www.ruder.io/optimizing-gradient-descent/)
- [Cosine LR Schedule - Loshchilov and Hutter](https://arxiv.org/abs/1608.03983)
- [Decoupled Weight Decay - Loshchilov and Hutter](https://arxiv.org/abs/1711.05101)

Tags: Calculus, ML, Optimization, Adam, Beginner

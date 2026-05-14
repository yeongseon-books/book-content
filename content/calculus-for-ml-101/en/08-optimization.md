---
series: calculus-for-ml-101
episode: 8
title: Optimization
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

# Optimization

Plain gradient descent gives you the basic learning loop, but real deep learning losses are rougher than that simple picture suggests. Valleys can be long and narrow, gradient scale can vary by coordinate, and the first few hundred steps may need very different behavior from the last few thousand.

This is post 8 in the Calculus for ML 101 series.

In this post, we'll treat momentum, RMSProp, Adam, schedules, and regularization as one optimization toolkit. The goal is not to memorize optimizer names, but to see which weakness of plain gradient descent each tool is trying to fix.

> Modern optimizers do not replace gradient descent with unrelated magic. They are gradient descent with extra machinery for stability, scale mismatch, and stage-specific control.

## What You Will Learn

- *Momentum*
- *RMSProp*
- *Adam*
- *Learning-rate schedules*
- Intuition for *regularization*

## Why It Matters

Modern optimizers like *Adam* work well — and you should *understand why*.

## Concept at a Glance

![Concept at a Glance](../../../assets/calculus-for-ml-101/08/08-01-concept-at-a-glance.en.png)

*Optimization flow: gradient signals are shaped by momentum, adaptive scaling, and scheduling.*
## Key Terms

- **momentum**: a *running mean of gradients*.
- **RMSProp**: a *running mean of squared gradients*.
- **Adam**: *momentum* + *RMSProp*.
- **schedule**: *learning rate* over time.
- **regularization**: a *brake on overfitting*.

## Before/After

**Before**: GD with a *fixed lr*.

**After**: *adaptive* updates plus *schedules*.

## Hands-on: Mini Optimizer Kit

### Step 1 — Momentum

```python
def momentum_step(w, v, g, lr=0.1, beta=0.9):
    v = beta * v + g
    return w - lr * v, v
```

### Step 2 — RMSProp

```python
def rms_step(w, s, g, lr=0.01, beta=0.99, eps=1e-8):
    s = beta * s + (1 - beta) * g * g
    return w - lr * g / (s ** 0.5 + eps), s
```

### Step 3 — Adam (Toy)

```python
def adam_step(w, m, v, g, t, lr=0.001, b1=0.9, b2=0.999, eps=1e-8):
    m = b1 * m + (1 - b1) * g
    v = b2 * v + (1 - b2) * g * g
    mh = m / (1 - b1 ** t)
    vh = v / (1 - b2 ** t)
    return w - lr * mh / (vh ** 0.5 + eps), m, v
```

### Step 4 — Schedule

```python
def cosine_lr(step, total, lr0=0.01):
    import math
    return 0.5 * lr0 * (1 + math.cos(math.pi * step / total))
```

### Step 5 — L2 Regularization

```python
def l2_step(w, g, lr=0.1, wd=1e-4):
    return w - lr * (g + wd * w)
```

## What to Notice in This Code

- *Momentum* adds *inertia*.
- *RMSProp* is *adaptive*.
- *Adam* combines both.
- *Schedules* fine-tune *late training*.
- *L2* aids *generalization*.

## Five Common Mistakes

1. **Using *Adam* defaults without tuning.**
2. **Confusing *weight decay* with *L2*.**
3. **Using a *fixed lr* without a schedule.**
4. **Skipping *warmup* despite early divergence.**
5. **Failing to *reset* momentum on resume.**

## How This Shows Up in Production

*Transformer training* uses *Adam* with *warmup* and a *cosine schedule* as the standard recipe.

## How a Senior Engineer Thinks

- Pick the *optimizer per problem*.
- *Warmup* prevents early divergence.
- *Adaptive* methods absorb *scale* differences.
- *Regularization* drives *generalization*.
- The *learning rate* decides *everything*.

## Checklist

- [ ] Match *optimizer* to *task*.
- [ ] Apply *warmup*.
- [ ] Design the *schedule*.
- [ ] Set *regularization* strength.

## Practice Problems

1. Define *momentum* in one line.
2. Define *Adam* in one line.
3. State the meaning of *warmup* in one line.

## Wrap-up and Next Steps

Next post: *Backpropagation Intuition*.

<!-- toc:begin -->
- [What Is a Derivative](./01-what-is-derivative.md)
- [Functions and Slope](./02-functions-and-slope.md)
- [Partial Derivatives](./03-partial-derivatives.md)
- [Gradient](./04-gradient.md)
- [Chain Rule](./05-chain-rule.md)
- [Loss Function](./06-loss-function.md)
- [Gradient Descent](./07-gradient-descent.md)
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

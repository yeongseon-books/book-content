---
series: calculus-for-ml-101
episode: 10
title: Calculus in Deep Learning
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
  - DeepLearning
  - Capstone
  - Beginner
seo_description: A capstone tour of how networks, loss, optimizers, backprop, and calculus combine into the deep learning training loop
last_reviewed: '2026-05-15'
---

# Calculus in Deep Learning

The ideas from this series do not live in isolation. Functions and slopes, partial derivatives, gradients, the chain rule, loss functions, gradient descent, optimizers, and backpropagation all show up inside the same training loop. The goal of this final post is to put those pieces back together as one working system.

This is the final post in the Calculus for ML 101 series.

In this post, we'll walk through the forward pass, loss computation, backward pass, optimizer update, and the operating rules around that loop. Once the full cycle is visible, calculus stops feeling like a separate math chapter and starts feeling like the control interface for learning itself.

> In deep learning, calculus is the common language that turns prediction error into parameter movement, one training step at a time.

## Questions this article answers

- What stages make up the deep learning training loop, and where does calculus appear in each one?
- How do the forward pass and loss computation prepare the work that backward needs to do?
- How do gradient computation and the optimizer update connect?
- Why do practical details such as `zero_grad`, eval/train mode, and reproducibility belong inside this loop?
- How do all the calculus ideas from this series collapse into one final picture?

## Why It Matters

This *capstone* synthesizes the series and lets you implement the *common skeleton* shared by every ML training run.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/10/10-01-concept-at-a-glance.en.png)

*Training-loop flow: forward, loss, backward, and update repeat as one closed cycle.*
## Key Terms

- **forward**: produce a *prediction*.
- **loss**: measure the *error*.
- **backward**: compute *gradients*.
- **update**: adjust *weights*.
- **epoch**: *one full pass* over the data.

## Before/After

**Before**: use the framework as a *black box*.

**After**: know *why* each stage of the loop exists.

## Hands-on: Mini Training Loop

### Step 1 — Model

```python
import math

def model(x, w, b):
    return sigmoid(w * x + b)

def sigmoid(z):
    return 1 / (1 + math.exp(-z))
```

### Step 2 — Loss (BCE)

```python
def bce(y, p, eps=1e-7):
    return -(y * math.log(p + eps) + (1 - y) * math.log(1 - p + eps))
```

### Step 3 — Analytical Gradients

```python
def grads(x, y, w, b):
    p = model(x, w, b)
    err = p - y
    return err * x, err
```

### Step 4 — One Update Step

```python
def step(x, y, w, b, lr=0.1):
    dw, db = grads(x, y, w, b)
    return w - lr * dw, b - lr * db
```

### Step 5 — Training Loop

```python
def train(data, epochs=100, lr=0.1):
    w, b = 0.0, 0.0
    for _ in range(epochs):
        for x, y in data:
            w, b = step(x, y, w, b, lr)
    return w, b
```

### Step 6 — Framework code uses the same loop

```python
optimizer.zero_grad()
pred = model(x)
loss = criterion(pred, y)
loss.backward()
optimizer.step()
```

These few lines compress the entire series. `pred = model(x)` is function composition. `loss = criterion(pred, y)` makes the training objective explicit. `loss.backward()` executes the chain rule across the computation graph. `optimizer.step()` converts gradient information into real parameter movement.

### Step 7 — Evaluation follows different rules

```python
with torch.no_grad():
    pred = model(x)
    metric = accuracy(pred, y)
```

Evaluation does not need gradients, so it should not build a backward graph. Once you see training as a forward-loss-backward-update loop, it becomes obvious why `train()`/`eval()` mode switches and `no_grad()` blocks matter. They are not framework rituals. They are part of running the loop correctly.

### Step 8 — The first failure points to check

- Did you forget `zero_grad()`, so stale gradients are leaking across steps?
- Is the loss decreasing while the evaluation metric gets worse, suggesting the loss design is misaligned with the real objective?
- Are scheduler timing, `train()`/`eval()` mode, or optimizer-step ordering inconsistent across experiments?
- Is reproducibility weak enough that you are blaming the model architecture for what is really a training-loop configuration issue?

Many training bugs come from this operating layer rather than from exotic calculus mistakes. That is why a clear loop-level mental model is so valuable.

## What to Notice in This Code

- The *forward pass* yields a *prediction*.
- The *loss* gives a *direction*.
- *Backprop* allocates *responsibility*.
- The *optimizer* applies the *update*.
- *Iteration* is *learning*.

## Five Common Mistakes

1. **Skipping *learning rate* tuning.**
2. **Forgetting *zero_grad*.**
3. **Computing gradients during *evaluation*.**
4. **Mixing *eval/train* modes (Dropout, BN).**
5. **Forgetting to *seed* for reproducibility.**

## How This Shows Up in Production

*Image classification*, *language models*, *recommenders*, and *RL* all share the *same skeleton*.

## How a Senior Engineer Thinks

- The training loop fits in *5 lines*.
- *Frameworks* are convenience; *principles* are essence.
- *Monitoring* is *debugging*.
- *Reproducibility* is *productivity*.
- *Numerical stability* is the last line of defense.

## Checklist

- [ ] *Forward* pass correct.
- [ ] *Loss* appropriate.
- [ ] *zero_grad* called.
- [ ] One *backward* pass.
- [ ] *Optimizer* update applied.

## Practice Problems

1. State the *5 stages* of the training loop in one line each.
2. State where *zero_grad* belongs in one line.
3. State the meaning of *eval mode* in one line.

## Wrap-up and Next Steps

This post wraps the *Calculus for ML 101* series. When people say a deep learning model *learns*, what they really mean is that the training loop keeps converting prediction error into gradients and then into parameter updates. Calculus is the language that makes that conversion possible.

<!-- toc:begin -->
- [What Is a Derivative](./01-what-is-derivative.md)
- [Functions and Slope](./02-functions-and-slope.md)
- [Partial Derivatives](./03-partial-derivatives.md)
- [Gradient](./04-gradient.md)
- [Chain Rule](./05-chain-rule.md)
- [Loss Function](./06-loss-function.md)
- [Gradient Descent](./07-gradient-descent.md)
- [Optimization](./08-optimization.md)
- [Backpropagation Intuition](./09-backpropagation-intuition.md)
- **Calculus in Deep Learning (current)**
<!-- toc:end -->

## References

- [Deep Learning Book - Goodfellow et al.](https://www.deeplearningbook.org/)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [CS231n - Convolutional Neural Networks](https://cs231n.stanford.edu/)
- [Reproducibility - PyTorch](https://pytorch.org/docs/stable/notes/randomness.html)
- [Zeroing out gradients in PyTorch](https://pytorch.org/tutorials/recipes/recipes/zeroing_out_gradients.html)

Tags: Calculus, ML, DeepLearning, Capstone, Beginner

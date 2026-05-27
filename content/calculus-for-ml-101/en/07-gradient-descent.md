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

In this post, we'll look at the update rule itself, the role of the learning rate, and the difference between full-batch, stochastic, and mini-batch behavior. Once that clicks, loss curves stop feeling like random charts and start looking like readable optimization traces.

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

Most ML training is a *variant* of gradient descent.

## Key Terms

- **GD**: gradient over *all data*.
- **SGD**: gradient over *one sample*.
- **mini-batch**: gradient over a *small batch*.
- **lr**: *learning rate*.
- **convergence**: settling to a *minimum*.

## Before/After

**Before**: try every combination via *grid search*.

**After**: move *efficiently* using the gradient.

## Hands-on: Mini GD Kit

### Step 1 — Loss and Gradient

```python
def loss(w):
    return (w - 3) ** 2

def grad(w):
    return 2 * (w - 3)
```

### Step 2 — One GD Step

```python
def step(w, lr=0.1):
    return w - lr * grad(w)
```

### Step 3 — Training Loop

```python
def train(w0, lr=0.1, steps=100):
    w = w0
    for _ in range(steps):
        w = step(w, lr)
    return w
```

### Step 4 — SGD

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

### Step 5 — Learning Rate Effect

```python
for lr in [0.001, 0.1, 1.5]:
    print(lr, train(0.0, lr, 50))
```

## What to Notice in This Code

- One *opposite-sign* step.
- The *learning rate* is *decisive*.
- *SGD* introduces *noise*.

## Five Common Mistakes

1. **Setting the *learning rate* far too high.**
2. **Using the same *lr* for differently-scaled weights.**
3. **Stopping *before convergence*.**
4. **Ignoring *SGD noise*.**
5. **Initializing all weights to *zero*.**

## How This Shows Up in Production

*Adam*, *Momentum*, and *RMSProp* are all *refinements* of gradient descent.

## How a Senior Engineer Thinks

- *Learning rate* is the most important hyperparameter.
- See divergence? Cut the *learning rate*.
- *SGD noise* gives *implicit regularization*.
- Use *warmup* and *scheduling*.
- Always inspect the *loss curve*.

## Checklist

- [ ] Search the *learning rate*.
- [ ] Monitor *convergence*.
- [ ] *Early-stop* on divergence.
- [ ] Vary *initialization*.

## Practice Problems

1. Define *gradient descent* in one line.
2. State the role of the *learning rate* in one line.
3. State the difference between *SGD* and *GD* in one line.

## Wrap-up and Next Steps

Next post: *Optimization*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Gradient Descent?**
  - The article treats Gradient Descent as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Gradient Descent?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Gradient Descent reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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

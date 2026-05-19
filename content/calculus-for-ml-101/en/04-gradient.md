---
series: calculus-for-ml-101
episode: 4
title: Gradient
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
  - Gradient
  - Vector
  - Beginner
seo_description: A beginner-friendly tour of gradient vectors, direction, magnitude, contour lines, and the steepest-ascent direction for ML
last_reviewed: '2026-05-15'
---

# Gradient

Once you have one partial derivative per variable, the next question is operational: how do you use all of them together? A model rarely updates one parameter in isolation. Training moves the whole parameter state at once, so you need a representation that preserves both per-coordinate responsibility and overall direction.

This is post 4 in the Calculus for ML 101 series.

In this post, we'll treat the gradient as a direction vector on a loss landscape rather than as a bag of numbers. That makes it much easier to understand why gradient descent follows the negative gradient, why gradient norm matters, and why contour-line intuition is so useful in practice.

> A gradient is not just a list of slopes. It is the direction-and-strength signal that tells an optimizer how the loss surface is pushing back at the current point.

## Questions this article answers

- What does it actually mean to bundle multiple partial derivatives into one gradient vector?
- What do the direction and magnitude of a gradient each mean in practice?
- Why does the gradient point in the direction of steepest increase in the loss?
- Why does gradient descent move in the opposite direction of the gradient?
- Why do contour lines make gradient intuition easier to build?

## Why It Matters

*Gradient descent* takes *one step* in the *opposite* direction of the gradient.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/04/04-01-concept-at-a-glance.en.png)

*Gradient flow: multiple partial derivatives combine into one vector with direction and magnitude.*
## Key Terms

- **gradient**: vector of *partial derivatives*.
- **direction**: a *unit vector*.
- **magnitude**: the *length*.
- **contour**: a *level set* line.
- **steepest**: the *fastest-growing* direction.

## Before/After

**Before**: see each variable *separately*.

**After**: bundle them into *one vector*.

## Hands-on: Mini Gradient Kit

### Step 1 — Gradient Function

```python
def grad(f, x, h=1e-5):
    g = []
    for i in range(len(x)):
        xp = x.copy(); xm = x.copy()
        xp[i] += h; xm[i] -= h
        g.append((f(xp) - f(xm)) / (2 * h))
    return g
```

### Step 2 — Loss

```python
def loss(w):
    return (w[0] - 1) ** 2 + (w[1] + 2) ** 2
```

### Step 3 — Compute Gradient

```python
g = grad(loss, [0.0, 0.0])  # about [-2, 4]
```

### Step 4 — Magnitude

```python
import math

def norm(v):
    return math.sqrt(sum(x ** 2 for x in v))
```

### Step 5 — One Opposite Step

```python
def step(w, g, lr=0.1):
    return [wi - lr * gi for wi, gi in zip(w, g)]
```

## What to Notice in This Code

- A gradient is a *vector*.
- The *opposite* direction *reduces* loss.
- *Magnitude* is the *signal strength*.

## Five Common Mistakes

1. **Treating the *gradient* as a *scalar*.**
2. **Flipping the *sign* incorrectly.**
3. **Confusing *learning rate* with *gradient magnitude*.**
4. **Ignoring *contour-line* intuition.**
5. **Misaligning *coordinates* with *weights*.**

## How This Shows Up in Production

*Backpropagation* computes the *whole-model gradient* in *one pass*.

## How a Senior Engineer Thinks

- A gradient is a *map*.
- The *opposite* direction is the *progress* direction.
- *Magnitude* diagnoses *state*.
- *Coordinate alignment* is *fixed*.
- *Vectorization* drives *speed*.

## Checklist

- [ ] Verify the *vector* shape.
- [ ] Inspect the *sign*.
- [ ] Monitor the *magnitude*.
- [ ] Lock the *coordinate order*.

## Practice Problems

1. Define a *gradient* in one line.
2. State the meaning of the *opposite* direction in one line.
3. State the meaning of *gradient magnitude* in one line.

## Wrap-up and Next Steps

Next post: *Chain Rule*.

<!-- toc:begin -->
- [What Is a Derivative](./01-what-is-derivative.md)
- [Functions and Slope](./02-functions-and-slope.md)
- [Partial Derivatives](./03-partial-derivatives.md)
- **Gradient (current)**
- Chain Rule (upcoming)
- Loss Function (upcoming)
- Gradient Descent (upcoming)
- Optimization (upcoming)
- Backpropagation Intuition (upcoming)
- Calculus in Deep Learning (upcoming)
<!-- toc:end -->

## References

- [Gradient - Khan Academy](https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives/partial-derivative-and-gradient-articles)
- [Vector Calculus - 3Blue1Brown](https://www.3blue1brown.com/topics/calculus)
- [Deep Learning Book - Numerical Computation](https://www.deeplearningbook.org/contents/numerical.html)
- [PyTorch Autograd Mechanics](https://pytorch.org/docs/stable/notes/autograd.html)

Tags: Calculus, ML, Gradient, Vector, Beginner

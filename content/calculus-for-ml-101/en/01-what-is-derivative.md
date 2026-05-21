---
series: calculus-for-ml-101
episode: 1
title: "Calculus for ML 101 (1/10): What Is a Derivative"
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
  - Derivative
  - Math
  - Beginner
seo_description: A beginner-friendly tour of derivatives, rate of change, tangent lines, limits, and numerical differentiation for ML
last_reviewed: '2026-05-15'
---

# Calculus for ML 101 (1/10): What Is a Derivative

When people first meet derivatives, they often memorize rules before they build a working mental model. In ML, that order tends to fail quickly. The useful question is simpler: if you nudge a parameter a little, does the loss go up or down, and how sharply?

This is the first post in the Calculus for ML 101 series.

In this post, we'll connect average rate of change, tangent lines, limits, and numerical differentiation into one practical picture. Once that picture is clear, a gradient stops looking like a mysterious number and starts looking like a directional signal for training.

> A derivative is not mainly about symbol manipulation. It is the local signal that tells you how a function reacts near the point where you are standing.

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is a Derivative?
- Which signal should the example or diagram make visible for What Is a Derivative?
- What failure should be prevented first when What Is a Derivative reaches a real system?

## Big Picture

![calculus for ml 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/01/01-01-concept-at-a-glance.en.png)

*calculus for ml 101 chapter 1 flow overview*

This picture places What Is a Derivative inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Questions this article answers

- Why is learning in ML directly tied to derivatives?
- What is the difference between average rate of change and instantaneous rate of change, and why does that distinction matter?
- What is the most practical way to relate the slope of a tangent line to the derivative?
- Why are limits indispensable in the definition of a derivative?
- When is numerical differentiation useful, and how much should you trust it?

## Why It Matters

*Gradient descent*, *backprop*, and *learning rate* are all defined on top of derivatives.

## Key Terms

- **derivative**: *instantaneous rate of change*.
- **slope**: *rise over run* between two points.
- **limit**: the value being *approached*.
- **tangent**: a line touching at *one point*.
- **numerical**: an *approximate* computation.

## Before/After

**Before**: it is unclear *why* the loss goes down.

**After**: the *slope of the loss* tells you the *direction*.

## Hands-on: Mini Derivative Kit

### Step 1 — Define a Function

```python
def f(x):
    return x ** 2
```

### Step 2 — Average Rate

```python
def avg_rate(f, a, b):
    return (f(b) - f(a)) / (b - a)
```

### Step 3 — Numerical Derivative

```python
def deriv(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)
```

### Step 4 — Tangent Slope

```python
slope = deriv(f, 2.0)  # about 4.0
```

### Step 5 — Loss Intuition

```python
def loss(w):
    return (w - 3) ** 2

g = deriv(loss, 0.0)   # negative -> increase w to reduce loss
```

## What to Notice in This Code

- The numerical derivative uses a *centered difference*.
- The *tangent slope* equals the *derivative*.
- The *sign of the loss gradient* gives the *direction*.

## Five Common Mistakes

1. **Picking *h* so tiny that *floating point* breaks.**
2. **Mixing up *average rate* and *instantaneous rate*.**
3. **Confusing the *derivative* with the *function value*.**
4. **Ignoring the *sign* and only watching *magnitude*.**
5. **Assuming a *limit* exists at a *discontinuity*.**

## How This Shows Up in Production

Updating *model weights* using the *loss gradient* is the *core loop* of every ML training process.

## How a Senior Engineer Thinks

- A derivative is a *direction*.
- A gradient is a *training signal*.
- Numerical derivatives are for *debugging*.
- Analytical derivatives are for *production*.
- *Intuition* about limits is enough.

## Checklist

- [ ] State the *function*.
- [ ] Compute the *gradient*.
- [ ] Interpret the *sign*.
- [ ] Inspect *numerical stability*.

## Practice Problems

1. Define a *derivative* in one line.
2. Define *average rate of change* in one line.
3. Explain what the *loss gradient* means in one line.

## Wrap-up and Next Steps

Next post: *Functions and Slope*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying What Is a Derivative?**
  - The article treats What Is a Derivative as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for What Is a Derivative?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when What Is a Derivative reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **What Is a Derivative (current)**
- Functions and Slope (upcoming)
- Partial Derivatives (upcoming)
- Gradient (upcoming)
- Chain Rule (upcoming)
- Loss Function (upcoming)
- Gradient Descent (upcoming)
- Optimization (upcoming)
- Backpropagation Intuition (upcoming)
- Calculus in Deep Learning (upcoming)

<!-- toc:end -->

## References

- [Calculus - Khan Academy](https://www.khanacademy.org/math/calculus-1)
- [Essence of Calculus - 3Blue1Brown](https://www.3blue1brown.com/topics/calculus)
- [Deep Learning Book - Numerical Computation](https://www.deeplearningbook.org/contents/numerical.html)
- [NumPy Numerical Differentiation](https://numpy.org/doc/stable/reference/generated/numpy.gradient.html)

Tags: Calculus, ML, Derivative, Math, Beginner

---
series: calculus-for-ml-101
episode: 5
title: "Calculus for ML 101 (5/10): Chain Rule"
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
  - ChainRule
  - Backprop
  - Beginner
seo_description: A beginner-friendly tour of the chain rule, function composition, outer and inner functions, gradient products, and backprop foundations
last_reviewed: '2026-05-15'
---

# Calculus for ML 101 (5/10): Chain Rule

Neural networks are not single functions. They are functions composed inside other functions, layer after layer, until a final loss is produced. In that setting, the key question is no longer "can I differentiate this formula?" but "how does a change at one stage travel through the whole path?"

This is post 5 in the Calculus for ML 101 series.

In this post, we'll use outer and inner functions, stage-by-stage derivatives, and broken gradient paths to explain the chain rule. The point is not to memorize a formula, but to see why backpropagation is fundamentally a disciplined application of local derivatives.

> The chain rule says you do not differentiate the whole system in one mysterious jump. You differentiate each local stage and connect those local sensitivities in the right order.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Chain Rule?
- Which signal should the example or diagram make visible for Chain Rule?
- What failure should be prevented first when Chain Rule reaches a real system?

## Big Picture

![calculus for ml 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/05/05-01-concept-at-a-glance.en.png)

*calculus for ml 101 chapter 5 flow overview*

This picture places Chain Rule inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Chain Rule is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions this article answers

- When one function is nested inside another, why is the full derivative connected by multiplication rather than simple addition?
- What is the most practical way to distinguish the outer function from the inner function?
- In a multi-stage composite function, in what order does the gradient propagate?
- Why can one zero-gradient stage block the entire path?
- How does the chain rule connect directly to backpropagation?

## Why It Matters

A *neural network* is a *long composition* of functions, and only the chain rule computes the full gradient *efficiently*.

## Concept at a Glance

## Key Terms

- **composition**: a *function of a function*.
- **outer**: the *outer* function.
- **inner**: the *inner* function.
- **chain**: connection by *multiplication*.
- **propagation**: passing *gradients along*.

## Before/After

**Before**: differentiating composites is hard.

**After**: differentiate each stage and *multiply*.

## Hands-on: Mini Chain Rule Kit

### Step 1 — Composition

```python
def g(x):
    return 2 * x + 1

def f(u):
    return u ** 2

def h(x):
    return f(g(x))
```

### Step 2 — Inner and Outer Derivatives

```python
def dg(x):
    return 2.0

def df(u):
    return 2 * u
```

### Step 3 — Chain Rule

```python
def dh(x):
    return df(g(x)) * dg(x)
```

### Step 4 — Numerical Check

```python
def deriv(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)

assert abs(dh(1.0) - deriv(h, 1.0)) < 1e-3
```

### Step 5 — Multi-Stage Composition

```python
def chain(*derivs):
    p = 1.0
    for d in derivs:
        p *= d
    return p
```

## What to Notice in This Code

- The chain rule is *one product*.
- Validate via *numerical derivative*.
- *Multi-stage* uses the same rule.

## Five Common Mistakes

1. **Reversing the *order*.**
2. **Evaluating the *inner* derivative at *raw x*.**
3. **Forgetting that one *zero gradient* zeroes the chain.**
4. **Forgetting it becomes *matrix multiplication* in many dims.**
5. **Dropping a *sign*.**

## How This Shows Up in Production

*Backpropagation* applies the chain rule *backward* to compute every weight's gradient in a single pass.

## How a Senior Engineer Thinks

- The chain rule is the *essence of backprop*.
- *Order* is *fixed*.
- Watch out for *zero-gradient* stages.
- Use *numerical checks* for *debugging*.
- Generalize via *matrix multiplication*.

## Checklist

- [ ] Mark the *composition order*.
- [ ] Differentiate *each stage*.
- [ ] *Numerically verify*.
- [ ] Inspect *zero-gradient* paths.

## Practice Problems

1. State the *chain rule* in one line.
2. State the meaning of *outer/inner* in one line.
3. State the risk of a *zero-gradient* stage in one line.

## Wrap-up and Next Steps

Next post: *Loss Function*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Chain Rule?**
  - The article treats Chain Rule as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Chain Rule?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Chain Rule reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Calculus for ML 101 (1/10): What Is a Derivative](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): Functions and Slope](./02-functions-and-slope.md)
- [Calculus for ML 101 (3/10): Partial Derivatives](./03-partial-derivatives.md)
- [Calculus for ML 101 (4/10): Gradient](./04-gradient.md)
- **Chain Rule (current)**
- Loss Function (upcoming)
- Gradient Descent (upcoming)
- Optimization (upcoming)
- Backpropagation Intuition (upcoming)
- Calculus in Deep Learning (upcoming)

<!-- toc:end -->

## References

- [Chain Rule - Khan Academy](https://www.khanacademy.org/math/ap-calculus-ab/ab-differentiation-2-new/ab-3-1a/v/chain-rule-introduction)
- [Backpropagation - CS231n](https://cs231n.github.io/optimization-2/)
- [Deep Learning Book - Backprop](https://www.deeplearningbook.org/contents/mlp.html)
- [Automatic Differentiation - Baydin et al.](https://arxiv.org/abs/1502.05767)

Tags: Calculus, ML, ChainRule, Backprop, Beginner

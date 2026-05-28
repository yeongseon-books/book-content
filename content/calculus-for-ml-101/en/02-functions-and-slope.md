---
series: calculus-for-ml-101
episode: 2
title: "Calculus for ML 101 (2/10): Functions and Slope"
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
  - Functions
  - Slope
  - Beginner
seo_description: A beginner-friendly tour of functions, slope, linear and nonlinear shapes, and the graphical meaning of derivatives for ML
last_reviewed: '2026-05-15'
---

# Calculus for ML 101 (2/10): Functions and Slope

An ML model is ultimately a stack of functions. Linear layers are functions, activations are functions, and the final prediction is the output of a long composition. To read training behavior well, you need to see both what a function maps and how sharply it reacts.

This is the 2nd post in the Calculus for ML 101 series.

In this post, we'll treat a function as both an input-output contract and a geometric shape. That viewpoint makes it easier to explain why linear and nonlinear functions behave differently during learning, and why activation choice shows up directly in gradient flow.

> A function tells you what output you get. Its slope tells you how sensitive that output is at the point you currently care about.


![calculus for ml 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/02/02-01-concept-at-a-glance.en.png)
*calculus for ml 101 chapter 2 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Functions and Slope?
- Which signal should the example or diagram make visible for Functions and Slope?
- What failure should be prevented first when Functions and Slope reaches a real system?

## Questions this article answers

- Why should a function be understood as an input-output contract rather than just a formula?
- How does the slope of a linear function differ from the local slope of a nonlinear one?
- How does the slope difference between ReLU and sigmoid affect learning?
- Why does the graph-level meaning of a derivative make activation design easier to reason about?
- How do input scale and function shape affect the way you interpret gradients?

## Why It Matters

ML models are *function compositions*, and training pushes signals through *each function gradient*.

## Key Terms

- **function**: maps *input* to *output*.
- **slope**: the *ratio* of change.
- **linear**: a *straight* line.
- **nonlinear**: a *curve*.
- **activation**: a *nonlinear* ML function.

## Before/After

**Before**: a function is only a *formula*.

**After**: a function is also a *graph* with a *slope*.

## Hands-on: Mini Function Kit

### Step 1 — Linear

```python
def linear(x, a=2, b=1):
    return a * x + b
```

### Step 2 — Linear Slope

```python
def linear_slope(a):
    return a
```

### Step 3 — Nonlinear

```python
def relu(x):
    return max(0.0, x)
```

### Step 4 — ReLU Local Slope

```python
def relu_grad(x):
    return 1.0 if x > 0 else 0.0
```

### Step 5 — Sigmoid

```python
import math

def sigmoid(x):
    return 1 / (1 + math.exp(-x))
```

## What to Notice in This Code

- A linear slope is a *constant*.
- *ReLU* has a slope of *0 or 1*.
- *Sigmoid* is a *smooth step*.

## Five Common Mistakes

1. **Confusing *linear* and *nonlinear*.**
2. **Ignoring that *ReLU* is *not differentiable* at *0*.**
3. **Ignoring the *saturated* region of *sigmoid*.**
4. **Ignoring how *zero gradients* in activations matter.**
5. **Comparing inputs of *different scales* directly.**

## How This Shows Up in Production

Picking *activations*, building *graphical intuition*, and diagnosing *vanishing gradients* all start from function-slope thinking.

## How a Senior Engineer Thinks

- *Functions* are model *bricks*.
- Suspect any *zero-gradient* region.
- *Plot* the function.
- Align *input scales*.
- Treat *nonlinearity* as a *goal*.

## Checklist

- [ ] *Plot* the function.
- [ ] Inspect the *gradient distribution*.
- [ ] Check *saturated* regions.
- [ ] Align *input scales*.

## Practice Problems

1. State the slope of a *linear* function in one line.
2. State the slope of *ReLU* in one line.
3. Describe the *sigmoid* gradient in one line.

## Wrap-up and Next Steps

Next post: *Partial Derivatives*.

## Answering the Opening Questions

- **Why should functions be understood as input-output contracts rather than mere formulas?**
  - Each layer in a model is a function, and the input range and output range must match the next layer's expectations for training to proceed stably. Looking only at formulas hides this range contract, but viewing functions as "what comes in and what goes out" lets you catch inter-layer mismatches (scale differences, saturation) in advance.
- **How do the slope of a linear function and the local slope of a nonlinear function differ?**
  - Linear functions have the same slope everywhere, so gradients propagate uniformly. Nonlinear functions have slopes ranging from 0 to beyond 1 depending on position, so even with the same input, learning speed varies depending on which region inside the model you're in.
- **How does the slope difference between ReLU and sigmoid affect the training process?**
  - ReLU has slope exactly 1 in the positive region, so gradients propagate without attenuation. Sigmoid's maximum slope is 0.25, so gradients shrink at every layer, causing vanishing gradients in deep networks. This is the practical reason most modern models use ReLU-family activations in hidden layers.
<!-- toc:begin -->
## In this series

- [Calculus for ML 101 (1/10): What Is a Derivative](./01-what-is-derivative.md)
- **Functions and Slope (current)**
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

- [Functions - Khan Academy](https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:functions)
- [Activation Functions - Stanford CS231n](https://cs231n.github.io/neural-networks-1/)
- [Deep Learning Book - MLP](https://www.deeplearningbook.org/contents/mlp.html)
- [PyTorch Activations](https://pytorch.org/docs/stable/nn.html#non-linear-activations-weighted-sum-nonlinearity)

Tags: Calculus, ML, Functions, Slope, Beginner

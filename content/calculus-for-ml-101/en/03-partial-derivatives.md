---
series: calculus-for-ml-101
episode: 3
title: Partial Derivatives
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
  - PartialDerivative
  - MultiVariable
  - Beginner
seo_description: A beginner-friendly tour of partial derivatives, multivariable functions, holding variables, per-variable slopes, and ML weights
last_reviewed: '2026-05-15'
---

# Partial Derivatives

Real ML losses are not single-input functions. They depend on many weights, biases, activations, and inputs at once. If you want to know which parameter is responsible for a change in loss, you need a way to isolate one variable without pretending the others disappeared.

This is post 3 in the Calculus for ML 101 series.

In this post, we'll use multivariable functions, fixed variables, and per-parameter responsibility to build intuition for partial derivatives. That is the conceptual step that turns "a derivative" into "a gradient for every trainable weight."

> A partial derivative is the rule that lets you ask one focused question at a time: if only this variable moved, how would the loss respond?

## Questions this article answers

- Why do you need to look at slopes one variable at a time in a function with multiple inputs?
- In a partial derivative, what does it really mean to "hold the other variables fixed"?
- Why can the same function produce different derivative values depending on which variable you differentiate with respect to?
- Why do you need a clear variable order before you can build a gradient vector?
- How do partial derivatives divide responsibility across weights in ML?

## Why It Matters

Every ML *weight* receives its *share of responsibility* through a *partial derivative*.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/03/03-01-concept-at-a-glance.en.png)

*Partial-derivative flow: hold one variable fixed and isolate responsibility along the other axis.*
## Key Terms

- **multivariable**: *many* inputs.
- **partial**: derivative with *others fixed*.
- **slice**: cross-section varying *one variable*.
- **per-variable**: gradient *per input*.
- **weight**: a *trainable* variable in ML.

## Before/After

**Before**: see all inputs at once.

**After**: isolate *one input* at a time.

## Hands-on: Mini Partial Derivative Kit

### Step 1 — Multivariable Function

```python
def f(x, y):
    return x ** 2 + 3 * y
```

### Step 2 — Partial w.r.t. x

```python
def partial_x(f, x, y, h=1e-5):
    return (f(x + h, y) - f(x - h, y)) / (2 * h)
```

### Step 3 — Partial w.r.t. y

```python
def partial_y(f, x, y, h=1e-5):
    return (f(x, y + h) - f(x, y - h)) / (2 * h)
```

### Step 4 — Both at Once

```python
def partials(f, x, y):
    return partial_x(f, x, y), partial_y(f, x, y)
```

### Step 5 — ML Weight Intuition

```python
def loss(w1, w2):
    return (w1 - 1) ** 2 + (w2 + 2) ** 2

g1, g2 = partials(loss, 0.0, 0.0)  # responsibility per weight
```

## What to Notice in This Code

- A *partial* moves *one variable*.
- The *others* are *fixed*.
- Each *weight* gets *its own gradient*.

## Five Common Mistakes

1. **Changing *all variables* at once.**
2. **Using a *different h* per variable.**
3. **Ignoring the *value* of fixed variables.**
4. **Confusing *partial* and *total* derivative.**
5. **Mixing up the *order* of the gradient vector.**

## How This Shows Up in Production

*Per-weight responsibility* is what *backprop* uses to update each parameter *appropriately*.

## How a Senior Engineer Thinks

- *Partial* is *responsibility allocation*.
- *Document* the variable *order*.
- Fixed values *still matter*.
- *Vectorize* for efficiency.
- *Local* views build *global* ones.

## Checklist

- [ ] Separate *variables*.
- [ ] State the *order*.
- [ ] Record *fixed* values.
- [ ] Bundle into a *vector*.

## Practice Problems

1. Define a *partial derivative* in one line.
2. Define a *multivariable* function in one line.
3. State what *responsibility allocation* means in one line.

## Wrap-up and Next Steps

Next post: *Gradient*.

<!-- toc:begin -->
- [What Is a Derivative](./01-what-is-derivative.md)
- [Functions and Slope](./02-functions-and-slope.md)
- **Partial Derivatives (current)**
- Gradient (upcoming)
- Chain Rule (upcoming)
- Loss Function (upcoming)
- Gradient Descent (upcoming)
- Optimization (upcoming)
- Backpropagation Intuition (upcoming)
- Calculus in Deep Learning (upcoming)
<!-- toc:end -->

## References

- [Partial Derivatives - Khan Academy](https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives)
- [Multivariable Calculus - MIT OCW](https://ocw.mit.edu/courses/18-02-multivariable-calculus-fall-2007/)
- [Deep Learning Book - Chapter 4](https://www.deeplearningbook.org/contents/numerical.html)
- [JAX Automatic Differentiation](https://jax.readthedocs.io/en/latest/notebooks/autodiff_cookbook.html)

Tags: Calculus, ML, PartialDerivative, MultiVariable, Beginner

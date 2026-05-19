---
series: math-for-cs-101
episode: 8
title: Calculus
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Math
  - Calculus
  - Derivative
  - GradientDescent
  - Beginner
seo_description: A beginner-friendly tour of limits, derivatives, gradients, the chain rule, and gradient descent intuition for CS
last_reviewed: '2026-05-04'
---

# Calculus

When a model trains by reducing a loss, when a numerical method searches for a better answer, or when a simulation tracks how a system evolves over time, the core question is the same: from the current position, which way should we move?

Calculus gives you that directional sense. You do not need to understand an entire curve at once to learn something useful. Often it is enough to understand how the value wants to change right here, right now, at a single point.

This is post 8 in the Math for CS 101 series.

Here we connect limits, derivatives, gradients, the chain rule, and gradient descent into one practical story about change and optimization.

## Questions this chapter answers

- Why can local slope tell you so much about a global optimization process?
- How are limits and derivatives connected?
- What changes when one variable becomes many variables?
- Why is the chain rule the backbone of backpropagation?
- How does gradient descent turn slope information into repeated improvement?

> Calculus is not mainly about memorizing curves. It is about reading change, choosing direction, and iterating toward a better state.

## Why It Matters

Machine learning training, numerical optimization, physical simulation, and many control problems rely on calculus because they all need a way to reason about change. The point is not to understand every detail of a function globally before you act. The point is to know enough local structure to take the next useful step.

That local information becomes operational in optimization. A derivative gives the slope at one point. A gradient gives the direction of fastest increase in many dimensions. Gradient descent then uses that information to keep moving in the opposite direction.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/08/08-01-concept-at-a-glance.en.png)
*Calculus turns tiny local change into practical direction: first a derivative, then a gradient, then a repeated optimization procedure.*

## Key Terms

- **limit**: the value being *approached*.
- **derivative**: *instantaneous rate of change*.
- **gradient**: derivative for *many variables*.
- **chain rule**: derivative of a *composite* function.
- **gradient descent**: move *opposite* the gradient.

## Before/After

**Before**: estimate the curve from *many points*.

**After**: pick a *direction* from one *slope*.

## Hands-on: Mini Calculus Kit

### Step 1 — Numerical Derivative

```python
def deriv(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)
```

### Step 2 — Gradient

```python
def grad(f, x, h=1e-5):
    return [(f([xi + (h if i == j else 0) for i, xi in enumerate(x)])
             - f([xi - (h if i == j else 0) for i, xi in enumerate(x)])) / (2 * h)
            for j in range(len(x))]
```

### Step 3 — Chain Rule

```python
def chain(df_dy, dy_dx):
    return df_dy * dy_dx
```

### Step 4 — One Descent Step

```python
def step(x, g, lr=0.1):
    return [xi - lr * gi for xi, gi in zip(x, g)]
```

### Step 5 — Mini Training Loop

```python
def descend(f, x, lr=0.1, steps=100):
    for _ in range(steps):
        x = step(x, grad(f, x), lr)
    return x
```

## What to Notice in This Code

- Numerical derivative is an *approximation*.
- *Gradient* is a *vector*.
- Descent moves in the *opposite* direction.

## Five Common Mistakes

1. **Setting the *learning rate* too high.**
2. **Picking *h* too tiny or too large.**
3. **Mixing up the *order* of the chain rule.**
4. **Mistaking a *local* min for *global*.**
5. **Comparing variables of *different scales*.**

## How This Shows Up in Production

*Neural network training*, *recommender tuning*, *ad bidding optimization*, and *control systems* are all calculus-driven.

## How a Senior Engineer Thinks

- *Gradient* is *direction*.
- *Learning rate* is *speed*.
- *Chain rule* is the heart of *backprop*.
- *Numerical stability* matters.
- Always doubt the *local optimum*.

## Checklist

- [ ] Inspect *gradient sign*.
- [ ] Tune *learning rate*.
- [ ] Monitor *convergence*.
- [ ] Check *feature scaling*.

## Practice Problems

1. Define a *derivative* in one line.
2. State the *chain rule* in one line.
3. Describe *gradient descent* in one line.

## Wrap-up and Next Steps

Calculus gives you a language for change that scales from one slope to full optimization loops. Once you connect derivatives, gradients, and the chain rule, many ML and numerical methods stop feeling like magic.

Next, we move into information theory, where uncertainty gets measured in bits instead of slopes.

<!-- toc:begin -->
- [Why Math for CS](./01-why-math-for-cs.md)
- [Logic and Proofs](./02-logic-and-proofs.md)
- [Sets and Functions](./03-sets-and-functions.md)
- [Graphs](./04-graphs.md)
- [Combinatorics](./05-combinatorics.md)
- [Probability](./06-probability.md)
- [Linear Algebra](./07-linear-algebra.md)
- **Calculus (current)**
- Information Theory (upcoming)
- Algorithms and Math (upcoming)
<!-- toc:end -->

## References

- [Calculus - Khan Academy](https://www.khanacademy.org/math/calculus-1)
- [Essence of Calculus - 3Blue1Brown](https://www.3blue1brown.com/topics/calculus)
- [Gradient Descent - Deep Learning Book](https://www.deeplearningbook.org/contents/numerical.html)
- [SymPy Calculus Documentation](https://docs.sympy.org/latest/modules/calculus/index.html)
- [SymPy GitHub repository](https://github.com/sympy/sympy)

Tags: Math, Calculus, Derivative, GradientDescent, Beginner

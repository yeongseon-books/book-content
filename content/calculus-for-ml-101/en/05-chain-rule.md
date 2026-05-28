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

This is the 5th post in the Calculus for ML 101 series.

In this post, we'll use outer and inner functions, stage-by-stage derivatives, and broken gradient paths to explain the chain rule. The point is not to memorize a formula, but to see why backpropagation is fundamentally a disciplined application of local derivatives connected in the right order.

By the end, you'll see the chain rule not as "a technique for hard composite functions" but as "the only road gradients can travel through a deep network."

> The chain rule says you do not differentiate the whole system in one mysterious jump. You differentiate each local stage and connect those local sensitivities in the right order.

![calculus for ml 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/05/05-01-concept-at-a-glance.en.png)
*calculus for ml 101 chapter 5 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Chain Rule?
- Which signal should the example or diagram make visible for Chain Rule?
- What failure should be prevented first when Chain Rule reaches a real system?

## Questions this article answers

- When one function is nested inside another, why is the full derivative connected by multiplication rather than simple addition?
- What is the most practical way to distinguish the outer function from the inner function?
- In a multi-stage composite function, in what order does the gradient propagate?
- Why can one zero-gradient stage block the entire path?
- How does the chain rule connect directly to backpropagation?

## Why It Matters

A deep learning model is a composite function. From input to output there are many transformations, and the loss is defined on top of the entire result. To compute how a specific weight affects the loss, you must trace backward through every intermediate transformation and connect gradients along the way. That connection rule is the chain rule.

In practice, activation saturation, dead ReLU, and exploding/vanishing gradients are all explained from the chain rule perspective. Because multiple stage derivatives are multiplied together, repeated small values kill the signal and repeated large values explode it. Understanding the chain rule is therefore understanding the failure modes of backpropagation.

This article also bridges directly to the loss function, gradient descent, and backpropagation intuition articles that follow. Without the chain rule, the backward pass looks like framework magic; with it, that magic becomes systematic repeated multiplication.

## Core Perspective

The best way to understand the chain rule is to view a composite function as a multi-stage pipeline. Input enters the inner function to produce an intermediate representation, and that result becomes the input to the outer function. To get the overall rate of change, you must connect each stage's rate of change—which naturally introduces multiplication.

This perspective is highly practical in ML. Each layer in a network has its own local derivative, and the backward pass multiplies that local derivative by the upstream gradient to pass the signal to the previous layer. Backpropagation is essentially the chain rule unrolled into code.

> The essence of the chain rule is not "differentiate a complex function in one shot" but "connect each stage's local derivative in the correct order."

## Core Concepts

### First, decompose the composite function

```python
def g(x):
    return 2 * x + 1

def f(u):
    return u ** 2

def h(x):
    return f(g(x))
```

Here `g(x)` is the inner function and `f(u)` is the outer function. You could expand `h(x)` and differentiate directly, but keeping the composition structure and examining each stage separately aligns much better with deep learning intuition.

### Separate the inner and outer derivatives

```python
def dg(x):
    return 2.0

def df(u):
    return 2 * u
```

The inner function transforms input `x` into an intermediate `u`; the outer function transforms `u` into the final output. To get the total rate of change, you need both: how much `x` changes `u`, and how much `u` changes the output.

### The full derivative is a connected product

```python
def dh(x):
    return df(g(x)) * dg(x)
```

The critical point: `df` is evaluated at `g(x)`, not at raw `x`. This single line captures the essence of the outer/inner distinction. First compute the outer function's sensitivity at the intermediate value, then multiply by the inner function's sensitivity.

### Numerical verification confirms correctness

```python
def deriv(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)

assert abs(dh(1.0) - deriv(h, 1.0)) < 1e-3
```

Numerical differentiation serves as a ground-truth check for your chain rule implementation. Production training uses analytic or automatic differentiation, but during debugging this small numerical check is invaluable.

### More stages, same rule

```python
def chain(*derivs):
    p = 1.0
    for d in derivs:
        p *= d
    return p
```

Adding more composition stages doesn't change the principle—just multiply each stage's local derivative in the correct order. In higher dimensions, this scalar product generalizes to Jacobian matrix multiplication, but the essence remains "connecting stage-wise local derivatives."

### Zero-gradient paths must always be watched

Because the chain rule is multiplication, if any intermediate stage frequently produces near-zero gradients, the entire path's gradient shrinks rapidly. This is why sigmoid saturation and dead ReLU are treated seriously in practice—they are chain-rule bottlenecks.

## Worked Example: sin(x²) Step by Step

The formula looks simple, but in practice people frequently confuse where to evaluate which derivative. Let's decompose a representative example.

`h(x) = sin(x²)` splits into:

- Inner function: `u(x) = x²`
- Outer function: `h(u) = sin(u)`

By the chain rule: `dh/dx = (dh/du) * (du/dx) = cos(u) * 2x = 2x cos(x²)`

```python
import math

def h(x):
    return math.sin(x**2)

def dh_analytic(x):
    return 2*x*math.cos(x**2)

def dh_numeric(x, eps=1e-6):
    return (h(x+eps)-h(x-eps))/(2*eps)

for x in [0.2, 0.7, 1.3]:
    print(x, dh_analytic(x), dh_numeric(x))
```

Two verification points:

1. The outer derivative `cos(·)` must be evaluated at the inner result `x²`.
2. You must multiply by the inner derivative `2x` to complete the total rate of change.

For a deeper nesting example, consider `y = exp(sin(3x+1))`:

| Stage | Function | Derivative |
| --- | --- | --- |
| 1 | `a(x) = 3x+1` | `a'(x) = 3` |
| 2 | `b(a) = sin(a)` | `b'(a) = cos(a)` |
| 3 | `y(b) = exp(b)` | `y'(b) = exp(b)` |

Total derivative: `exp(sin(3x+1)) * cos(3x+1) * 3`.

## Computation Graph Perspective

In deep learning implementations, converting expressions to nodes and edges is more practical than working with formulas. Each node provides an intermediate value; each edge provides a local derivative.

```python
# y = (x1 * x2 + x3)^2

def forward(x1, x2, x3):
    m = x1 * x2
    s = m + x3
    y = s ** 2
    cache = (x1, x2, x3, m, s)
    return y, cache

def backward(dy, cache):
    x1, x2, x3, m, s = cache
    ds = dy * (2 * s)
    dm = ds * 1.0
    dx3 = ds * 1.0
    dx1 = dm * x2
    dx2 = dm * x1
    return dx1, dx2, dx3
```

Starting with `dy=1` and running backward shows exactly how the loss distributes from the output node to each input node. This structure scaled to a full deep network *is* backpropagation.

| Graph element | Forward role | Backward role |
| --- | --- | --- |
| Multiplication node | Combine values | Multiply by other operand to pass gradient |
| Addition node | Merge paths | Copy same gradient to each input |
| Nonlinear node | Add expressiveness | Scale signal by local derivative |

## Backpropagation Is Repeated Chain Rule Application

Backpropagation is not new math—it is the chain rule applied efficiently on a large graph. The core operation is multiplying the upstream gradient by the local derivative.

```python
# 1-layer linear + sigmoid + BCE (abbreviated)
import numpy as np

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

def bce_grad(a, y):
    # dL/da for probability-based BCE
    return -(y / (a + 1e-12)) + (1 - y) / (1 - a + 1e-12)

def backward_one_sample(x, w, b, y):
    z = x @ w + b
    a = sigmoid(z)
    dL_da = bce_grad(a, y)
    da_dz = a * (1 - a)
    dL_dz = dL_da * da_dz
    dL_dw = x[:, None] * dL_dz
    dL_db = dL_dz
    return dL_dw, dL_db
```

Production frameworks vectorize this as tensor operations and automatically trace the graph for backward. But the underlying principle is identical.

## Jacobian Introduction: From Scalar Products to Matrix Products

So far we've worked with scalars, but for multi-variable functions the derivative becomes a Jacobian matrix.

- If `f: R^n → R^m`, then Jacobian `J` has shape `m × n`.
- The chain rule generalizes to `J_(f∘g)(x) = J_f(g(x)) · J_g(x)`.

```python
import numpy as np

def jac_g(x1, x2):
    return np.array([
        [1.0, 1.0],
        [x2,  x1],
    ])

def jac_f(u1, u2):
    return np.array([[2*u1, 3.0]])

x1, x2 = 2.0, -1.0
u1, u2 = x1 + x2, x1 * x2
J = jac_f(u1, u2) @ jac_g(x1, x2)
print(J)  # d(f∘g)/dx1, d(f∘g)/dx2
```

This example demonstrates why multiplication order matters. If dimensions don't match, the operation is impossible; if you reverse the order, the meaning changes.

## Triple Verification: Analytic vs Numeric vs Autograd

To build implementation confidence, cross-check three observations:

1. Hand-derived analytic derivative
2. Central-difference numerical derivative
3. Framework automatic differentiation

```python
import math
import torch

# function: y = sin((2x+1)^2)
def fn(x):
    return math.sin((2*x + 1)**2)

def d_analytic(x):
    inner = 2*x + 1
    return math.cos(inner**2) * (2*inner) * 2

def d_numeric(x, h=1e-6):
    return (fn(x+h)-fn(x-h))/(2*h)

x = 0.4

xt = torch.tensor(x, requires_grad=True)
yt = torch.sin((2*xt + 1)**2)
yt.backward()

print('analytic:', d_analytic(x))
print('numeric :', d_numeric(x))
print('autograd:', float(xt.grad))
```

When all three values agree closely, you have strong evidence the chain connection is correct. When they diverge, check operation ordering, broadcasting, and non-differentiable-point handling first.

## Common Error Patterns in Practice

| Symptom | Likely cause | Quick check |
| --- | --- | --- |
| Backward runs but grad is unexpectedly large | Duplicate multiplication or dimension broadcasting error | Inspect each node's shape and local derivative output |
| A specific layer's grad is always 0 | Saturated activation, detach, or mask error | Check that layer's input distribution and graph connection |
| Numerical and autograd derivatives disagree | Non-differentiable op included, poor eps choice | Function smoothness, eps sensitivity sweep |
| NaN from early training | exp/log domain instability | Clip, log-sum-exp, stabilized formulas |

To reduce errors: always validate on a small graph first, then scale up.

## Multi-Layer Hand Calculation Example

Consider a three-stage composition `y = ((2x+3)² + 1)³`:

- `a = 2x + 3`
- `b = a² + 1`
- `y = b³`

Stage derivatives: `da/dx = 2`, `db/da = 2a`, `dy/db = 3b²`. Therefore:

`dy/dx = 3b² * 2a * 2 = 12a·b²`

```python
def d_manual(x):
    a = 2*x + 3
    b = a*a + 1
    return 12*a*(b**2)
```

The key insight: reusing intermediate values `a` and `b` simplifies computation and reduces errors. This reuse strategy is exactly the cache concept in computation graphs.

## Vector-Matrix Chain Rule Mini Example

Beyond scalars, the chain rule naturally becomes matrix multiplication.

Given `z = Wx + b`, `a = tanh(z)`, `L = ||a - t||² / 2`:

- `dL/da = a - t`
- `da/dz = 1 - tanh(z)²` (element-wise)
- `dL/dz = dL/da ⊙ da/dz`
- `dL/dW = (dL/dz) xᵀ`

```python
import numpy as np

x = np.array([[0.5], [1.2]])
W = np.array([[0.3, -0.2], [0.1, 0.4]])
b = np.array([[0.0], [0.2]])
t = np.array([[0.4], [-0.1]])

z = W @ x + b
a = np.tanh(z)
dL_da = a - t
dL_dz = dL_da * (1 - np.tanh(z)**2)
dL_dW = dL_dz @ x.T
print(dL_dW)
```

Understanding this equation lets you verify the `W.grad` shape your framework returns much faster.

## Chain Rule Debugging Checklist

| Check order | Verification | Action on failure |
| --- | --- | --- |
| 1 | Does the intermediate cache match forward values? | Simplify cache structure |
| 2 | Are local derivative shapes correct? | Make broadcasting explicit |
| 3 | Do signs match numerical derivative? | Re-examine operation order |
| 4 | Is final gradient scale unreasonably large? | Check input scale, initialization |

Most chain rule bugs start from shape mismatches and intermediate-value reference errors. The safest habit: pass a small graph through hand calculation first, then extend to the full model.

## Numerical Verification Error Analysis

Understanding why numerical checks are never exactly zero matters for debugging confidence. Central differencing has `O(h²)` approximation error and floating-point rounding error simultaneously—so both too-large and too-small `h` increase error.

```python
import math

def f(x):
    return math.sin((x+1)**3)

def d_true(x):
    return math.cos((x+1)**3) * 3 * (x+1)**2

def d_num(x, h):
    return (f(x+h)-f(x-h))/(2*h)

x = 0.3
for h in [1e-2, 1e-4, 1e-6, 1e-8]:
    err = abs(d_true(x)-d_num(x,h))
    print(h, err)
```

This experiment prevents you from immediately blaming an implementation bug when verification shows a small discrepancy. Check `h` sensitivity first, then suspect graph connection errors.

## Shape Conventions for Backprop Implementation

The math of the chain rule can be correct while the code is wrong—the most common cause is absent shape conventions. For team work, fix these in documentation:

1. Vectors are column vectors `(d, 1)`.
2. Mini-batches use `(batch, feature)` layout.
3. Operations that implicitly hide a Jacobian (`sum`, `mean`) must specify axis explicitly.

Shape conventions alone prevent a large fraction of chain rule errors.

## Learning Routine: Reducing Dependence on Autograd Alone

Framework autograd is powerful, but using it without chain rule understanding makes debugging speed collapse. Repeating this routine significantly improves implementation reliability:

1. When adding a new operation block, perform a single-sample numerical derivative check first.
2. Once block-level backward passes, extend to batch dimension.
3. Finally, confirm gradient norm distribution across the full model.

```python
def gradcheck_scalar(fn, x, d_analytic, h=1e-6):
    num = (fn(x+h)-fn(x-h))/(2*h)
    return abs(num-d_analytic(x))
```

For team collaboration, document "forward cache items" and "backward input/output shapes." In code review, shape contract violations are found more often than formula errors.

| Documentation item | Example | Purpose |
| --- | --- | --- |
| Node name | `z1`, `a1`, `logits` | Trace computation path |
| Tensor shape | `(batch, hidden)` | Prevent broadcasting errors |
| Local derivative | `da/dz = 1-a²` | Backward verification basis |
| Stabilization rule | `eps=1e-12` | Prevent NaN |

Connecting the chain rule across formula, code, and logs ensures that root-cause tracing cost doesn't explode as model scale grows.

## Five Common Misconceptions

1. **Evaluating the outer derivative at raw input** — breaks the composition structure entirely.
2. **Assuming multiplication order doesn't matter** — loses intermediate-value dependencies.
3. **Underestimating the zero-gradient stage** — one saturated activation can block the entire path.
4. **Forgetting matrix generalization** — in multiple dimensions the chain rule becomes matrix multiplication, not scalar product.
5. **Trusting autograd without numerical verification** — subtle implementation bugs go unnoticed.

## Operational Checklist

- [ ] Explicitly identify composition stages and intermediate values before differentiating.
- [ ] Confirm the outer derivative is evaluated at the inner output (not raw input).
- [ ] Check whether any zero-gradient region can block the full path.
- [ ] Verify backward results against numerical derivatives on small examples.
- [ ] Remember that in multi-dimensional models the chain rule extends to matrix operations.

## Wrap-up and Next Steps

The chain rule computes the derivative of a composite function as the product of each stage's local derivative. In structures where functions chain deeply—like neural networks—there is no efficient way to get the full gradient without this rule. So the chain rule is not a calculus technique; it is the central rule of deep learning training.

In practice, vanishing and exploding gradients are best understood on top of the chain rule structure. Because multiple stage derivatives multiply together, the choice of activation and initialization directly controls gradient transmission quality.

Next post: *Loss Function*—what number the gradient is ultimately optimizing, and why that design decision determines model quality.

## Answering the Opening Questions

- **When a function is nested inside another function, why is the total derivative a product rather than a sum?**
  - In composite functions, input changes pass through each stage sequentially, accumulating scale at each step. Just as `sin(x²)` requires multiplying `cos(x²)` by `2x` to get the correct total rate of change, stage-wise sensitivities must be connected by multiplication to preserve the actual amount transmitted.
- **What's the most practical way to distinguish the outer function from the inner function?**
  - Defining intermediate variables at the node level in the computation graph makes the distinction clear. Separating names like `u=x²`, `h=sin(u)` and applying the rule that the outer derivative is always "evaluated at the intermediate value" greatly reduces implementation errors.
- **In a multi-stage composite function, what order does the gradient propagate?**
  - It propagates in reverse order of forward. Starting from the output, the upstream gradient is multiplied by each node's local derivative and sent to the previous node. From a Jacobian perspective, this process generalizes to a chain of matrix multiplications, and backpropagation is the efficient implementation of that computation.
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

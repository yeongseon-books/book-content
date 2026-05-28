---
series: calculus-for-ml-101
episode: 3
title: "Calculus for ML 101 (3/10): Partial Derivatives"
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

# Calculus for ML 101 (3/10): Partial Derivatives

Real ML losses are not single-input functions. They depend on many weights, biases, activations, and inputs at once. If you want to know which parameter is responsible for a change in loss, you need a way to isolate one variable without pretending the others disappeared.

This is the 3rd post in the Calculus for ML 101 series.

In this post, we'll use multivariable functions, fixed variables, and per-parameter responsibility to build intuition for partial derivatives. That is the conceptual step that turns "a derivative" into "a gradient for every trainable weight."

> A partial derivative is the rule that lets you ask one focused question at a time: if only this variable moved, how would the loss respond?


![calculus for ml 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/03/03-01-concept-at-a-glance.en.png)
*calculus for ml 101 chapter 3 flow overview*

## Questions to Keep in Mind

- Why do you need to look at slopes one variable at a time in a function with multiple inputs?
- In a partial derivative, what does it really mean to "hold the other variables fixed"?
- Why can the same function produce different derivative values depending on which variable you differentiate with respect to?

## Why This Post Matters

A deep learning loss function is almost always a multivariable function. Changing a single weight changes the loss; changing a bias changes the loss; input scale and internal activations affect it too. Training is the process of finding a good direction on the surface of this multivariable function, which requires reading the per-variable rate of change—partial derivatives.

In practice this concept is highly direct. An optimizer uses an independent gradient value per weight to perform updates. Without partial derivatives, you could only know "the whole model got worse" without knowing which parameter to adjust by how much.

Understanding partial derivatives is also the prerequisite for the next post's gradient vector. A gradient bundles multiple partial derivatives together, so if the meaning of a partial derivative is fuzzy, the gradient looks like a list of numbers rather than a direction vector.

## Core Perspective

The easiest way to understand a partial derivative is to imagine a multivariable function as a 3D landscape, then slice along one axis at a time. When looking at $x$, fix $y$; when looking at $y$, fix $x$. The slope in that cross-section is the partial derivative.

This convention is simple but powerful. Even when the full function is too complex to analyze at once, decomposing into per-variable local reactions lets you compute each parameter's responsibility. This is why every weight in ML gets its own gradient—thanks to this slice analysis.

> A partial derivative is not "giving up on the whole picture." It is the strategy of "looking at one thing at a time." The convention of fixing the rest is what enables per-variable responsibility separation.

## Core Concepts

### A multivariable function has multiple input axes

```python
def f(x, y):
    return x ** 2 + 3 * y
```

This function has two inputs. Changing $x$ affects the $x^2$ term; changing $y$ affects the $3y$ term. Since both inputs simultaneously influence the output, separating their individual contributions is the starting point of partial derivatives.

### Moving only x gives the partial derivative with respect to x

```python
def partial_x(f, x, y, h=1e-5):
    return (f(x + h, y) - f(x - h, y)) / (2 * h)
```

Here $y$ stays unchanged while $x$ moves slightly in both directions. The code is explicit: we are measuring only $x$'s responsibility right now. Other variables still affect the function value, but we do not perturb them in this measurement.

### Moving only y gives the partial derivative with respect to y

```python
def partial_y(f, x, y, h=1e-5):
    return (f(x, y + h) - f(x, y - h)) / (2 * h)
```

This time $x$ is fixed and only $y$ varies. The crucial point: the same function yields different rates of change depending on which variable you differentiate with respect to. In multivariable functions, "the slope" becomes a collection of per-variable numbers.

### Computing multiple partials together is the material for a gradient

```python
def partials(f, x, y):
    return partial_x(f, x, y), partial_y(f, x, y)
```

This is the simplest precursor to a gradient vector. Even without full vector calculus, the key insight is: each variable has an independent rate of change, and these must be managed in a consistent order.

### In ML, each weight receives its own partial derivative

```python
def loss(w1, w2):
    return (w1 - 1) ** 2 + (w2 + 2) ** 2

g1, g2 = partials(loss, 0.0, 0.0)  # responsibility per weight
```

This shows two weights each learning which direction to move to reduce loss. $g1$ and $g2$ come from the same loss but carry different responsibilities. Backpropagation is ultimately the procedure that computes these partial derivatives efficiently for every parameter in the network.

### Variable order and fixed values matter in practice

When using gradients, variable order must be documented. If it becomes unclear whether the first value is for $w_1$ or $w_2$, update targets get mixed up. Also, "fixed variables" matter: a partial derivative does not erase the other variables—it reads one variable's local reaction while the others hold their current values.

## Analytic vs Numeric Partial Derivatives in Multivariable Functions

Extending the Chapter 1 numeric verification to multivariable functions. As dimensions grow, ensuring analytic derivative correctness becomes harder, making numeric verification more critical.

### Two-Variable Analytic Partial Derivatives

Consider $f(x, y) = x^2 y + \sin(xy)$:

$$\frac{\partial f}{\partial x} = 2xy + y\cos(xy)$$
$$\frac{\partial f}{\partial y} = x^2 + x\cos(xy)$$

```python
import numpy as np

def f(x, y):
    return x ** 2 * y + np.sin(x * y)

def df_dx_analytic(x, y):
    return 2 * x * y + y * np.cos(x * y)

def df_dy_analytic(x, y):
    return x ** 2 + x * np.cos(x * y)

def df_dx_numeric(f, x, y, h=1e-7):
    return (f(x + h, y) - f(x - h, y)) / (2 * h)

def df_dy_numeric(f, x, y, h=1e-7):
    return (f(x, y + h) - f(x, y - h)) / (2 * h)

x, y = 1.5, 2.0
print(f"df/dx: analytic={df_dx_analytic(x, y):.6f}, numeric={df_dx_numeric(f, x, y):.6f}")
print(f"df/dy: analytic={df_dy_analytic(x, y):.6f}, numeric={df_dy_numeric(f, x, y):.6f}")
```

If the difference is within $10^{-6}$, the derivation can be trusted. This pattern is especially common when writing custom loss functions.

### High-Dimensional Partial Derivatives: Vectorized NumPy

In real ML, parameters are vectors or matrices, so partial derivatives are computed in vectorized form.

```python
import numpy as np

def loss_vector(w, X, y):
    """MSE loss: w is (d,), X is (n, d), y is (n,)"""
    pred = X @ w
    return np.mean((pred - y) ** 2)

def grad_vector_analytic(w, X, y):
    """dL/dw = (2/n) * X^T (Xw - y)"""
    n = len(y)
    pred = X @ w
    return (2.0 / n) * X.T @ (pred - y)

def grad_vector_numeric(loss_fn, w, X, y, h=1e-5):
    """Per-element numeric partial derivative"""
    grad = np.zeros_like(w)
    for i in range(len(w)):
        w_plus = w.copy(); w_plus[i] += h
        w_minus = w.copy(); w_minus[i] -= h
        grad[i] = (loss_fn(w_plus, X, y) - loss_fn(w_minus, X, y)) / (2 * h)
    return grad

# Test
np.random.seed(0)
X = np.random.randn(10, 3)
y = X @ np.array([2.0, -1.0, 0.5]) + np.random.randn(10) * 0.1
w = np.zeros(3)

analytic = grad_vector_analytic(w, X, y)
numeric = grad_vector_numeric(loss_vector, w, X, y)
print(f"Analytic grad: {analytic}")
print(f"Numeric grad:  {numeric}")
print(f"Max diff: {np.max(np.abs(analytic - numeric)):.2e}")
```

The key line is `w_plus[i] += h`. Only one element changes while the rest remain fixed—this is the partial derivative definition implemented in code. Element $i$'s response is measured in complete isolation.

### The Cost Problem of Numeric Partial Derivatives

With $d$ parameters, numeric differentiation requires $2d$ function evaluations. BERT has 110 million parameters, which would mean 220 million forward passes for a full gradient. This is why autograd (reverse-mode automatic differentiation) is essential: it computes all partial derivatives in just 2 passes (forward + backward).

| Method | Function calls | Use case |
| --- | --- | --- |
| Numeric differentiation | $2d$ | Verification, debugging |
| Forward-mode autodiff | $d$ | Few variables |
| Reverse-mode autodiff | 2 (forward + backward) | Training (standard) |

## Mixed Partial Derivatives: Cross-Variable Interactions

You can differentiate the same function with respect to different variables twice. This is the mixed partial derivative, corresponding to off-diagonal elements of the Hessian matrix.

### Meaning and Computation

For $f(x, y) = x^2 y + xy^3$:

$$\frac{\partial^2 f}{\partial x \partial y} = 2x + 3y^2$$

```python
def f(x, y):
    return x ** 2 * y + x * y ** 3

def mixed_partial_xy(f, x, y, h=1e-5):
    """Compute d^2f / dx dy numerically"""
    return (f(x+h, y+h) - f(x+h, y-h) - f(x-h, y+h) + f(x-h, y-h)) / (4 * h * h)

x, y = 1.0, 2.0
analytic = 2 * x + 3 * y ** 2  # = 14.0
numeric = mixed_partial_xy(f, x, y)
print(f"Mixed partial: analytic={analytic:.4f}, numeric={numeric:.4f}")
```

A mixed partial derivative asks: "how does $y$'s sensitivity change when $x$ moves?" From an optimizer perspective, this captures variable interactions—used in Newton's method and natural gradient descent. Standard SGD does not use it directly, but it matters for understanding the loss landscape.

## Partial Derivatives and PyTorch Autograd

How PyTorch automatically computes partial derivatives:

```python
import torch

# Two-variable loss function
w1 = torch.tensor(0.5, requires_grad=True)
w2 = torch.tensor(-1.0, requires_grad=True)

loss = (w1 - 2.0) ** 2 + 3 * (w2 + 1.0) ** 2

# backward() computes partial derivatives for all leaf tensors
loss.backward()

print(f"dL/dw1 = {w1.grad.item():.4f}")  # 2*(0.5 - 2) = -3.0
print(f"dL/dw2 = {w2.grad.item():.4f}")  # 6*(-1 + 1) = 0.0
```

`w1.grad` is $\partial L / \partial w_1$ and `w2.grad` is $\partial L / \partial w_2$. Each measures the loss change rate when only that variable moves. A single `loss.backward()` call computes all partial derivatives—this is autograd's core efficiency.

### Matrix Parameter Partial Derivatives

In real models, weights are matrices. The logic is identical.

```python
import torch
import torch.nn as nn

model = nn.Linear(3, 1, bias=False)
X = torch.randn(5, 3)
y = torch.randn(5, 1)

pred = model(X)
loss = ((pred - y) ** 2).mean()
loss.backward()

# weight.grad is (1, 3) — each element is a partial derivative
print(f"weight shape: {model.weight.shape}")
print(f"grad shape:   {model.weight.grad.shape}")
print(f"grad values:  {model.weight.grad}")
```

If the weight is (1, 3), grad is also (1, 3). Each element `grad[0, i]` answers: "if only weight[0, i] changed by a tiny amount, how much would loss change?" That is the definition of a partial derivative.

## Practical Application: Full Partial Derivative Derivation for Linear Regression

Tracing how partial derivatives drive actual learning in the simplest 2-parameter linear regression.

### Model and Loss Definition

Model: $\hat{y} = w_1 x_1 + w_2 x_2$
Loss: $L = \frac{1}{n} \sum_{i=1}^{n} (\hat{y}_i - y_i)^2$

### Deriving Each Partial

$$\frac{\partial L}{\partial w_1} = \frac{2}{n} \sum_{i=1}^{n} (\hat{y}_i - y_i) \cdot x_{i1}$$

$$\frac{\partial L}{\partial w_2} = \frac{2}{n} \sum_{i=1}^{n} (\hat{y}_i - y_i) \cdot x_{i2}$$

The key: when differentiating with respect to $w_1$, the $w_2 x_2$ portion is treated as constant and vanishes. This is what the "fixed" convention of partial derivatives actually does.

### Training Loop Implementation

```python
import numpy as np

np.random.seed(42)
n = 50
X = np.random.randn(n, 2)
true_w = np.array([3.0, -2.0])
y = X @ true_w + np.random.randn(n) * 0.2

w = np.zeros(2)
lr = 0.05

for epoch in range(30):
    pred = X @ w
    residual = pred - y

    # partial derivatives
    grad_w1 = (2.0 / n) * np.sum(residual * X[:, 0])
    grad_w2 = (2.0 / n) * np.sum(residual * X[:, 1])

    # update
    w[0] -= lr * grad_w1
    w[1] -= lr * grad_w2

    if epoch % 10 == 0:
        loss = np.mean(residual ** 2)
        print(f"epoch={epoch:2d}  w=[{w[0]:.3f}, {w[1]:.3f}]  loss={loss:.4f}")

print(f"\nFinal w: [{w[0]:.4f}, {w[1]:.4f}]")
print(f"True  w: [{true_w[0]:.4f}, {true_w[1]:.4f}]")
```

Two partial derivatives are computed independently, each updating its corresponding weight. This is the complete structure of partial-derivative-based learning.

### Partial Derivative Magnitude and Convergence Speed

| Epoch | grad_w1 | grad_w2 | Interpretation |
| --- | --- | --- | --- |
| 0 | large | large | both weights far from answer |
| 10 | small | small | converging |
| 30 | ~0 | ~0 | converged; both partials approach zero |

When a partial derivative approaches zero, moving that variable barely changes the loss. When all partial derivatives are simultaneously zero, the entire gradient vector is the zero vector—the convergence condition.

## Variable Scale Differences and Partial Derivative Interpretation

A common practical issue: when two variables have very different scales, comparing absolute partial derivative values alone cannot determine "which variable is more important."

### Scale Mismatch Example

```python
import numpy as np

# x1 ranges 0~1, x2 ranges 0~1000
np.random.seed(0)
X = np.column_stack([
    np.random.rand(100),          # small scale
    np.random.rand(100) * 1000    # large scale
])
y = 5 * X[:, 0] + 0.01 * X[:, 1] + np.random.randn(100) * 0.1

w = np.zeros(2)
pred = X @ w
residual = pred - y
grad = (2.0 / len(y)) * X.T @ residual

print(f"grad_w1 = {grad[0]:.4f}  (x1 scale: 0~1)")
print(f"grad_w2 = {grad[1]:.4f}  (x2 scale: 0~1000)")
print(f"|grad_w2| >> |grad_w1| but true_w1=5 >> true_w2=0.01")
```

Gradient magnitude is influenced by variable scale. If $x_2$'s scale is large, its partial derivative is also large. This is why feature normalization is needed, and why adaptive optimizers like Adam adjust learning rate per variable.

### Resolution Strategies

| Strategy | Method | Pro | Con |
| --- | --- | --- | --- |
| Input normalization | All features to mean=0, std=1 | Simple, effective | Original interpretation lost |
| Adaptive lr | Adam, RMSProp, etc. | Automatic scale adjustment | Extra hyperparameters |
| Manual scaling | Domain-knowledge based | Interpretation preserved | Labor-intensive |

In practice, input normalization + Adam is the most common combination. When interpreting partial derivative magnitudes, always consider the variable's scale.

### Reading Update Direction from Partial Derivative Sign

The sign of a partial derivative directly determines the update direction. In gradient descent ($w \leftarrow w - \eta \cdot \frac{\partial L}{\partial w}$):

| Partial derivative sign | Meaning | Update direction |
| --- | --- | --- |
| Positive (+) | increasing w increases loss | decrease w |
| Negative (-) | increasing w decreases loss | increase w |
| Zero (0) | changing w does not affect loss | no update needed (converged) |

With this table in mind, you can interpret gradient signs immediately from training logs. If the sign keeps flipping, the learning rate is too large or the loss surface is oscillatory.

## Common Misconceptions

- Changing all variables simultaneously while computing a "partial derivative" measures something entirely different.
- Fixed variables are not unimportant—the partial derivative value can depend on their current values.
- Not documenting variable order causes gradient vector interpretation errors.
- Confusing partial and total derivatives makes it hard to explain chain effects.
- When variables have different scales, treating equal-magnitude gradients as equally meaningful is wrong.
- Confusing the $O(d)$ cost of numeric partial derivatives with the $O(1)$ cost of autograd can lead to putting debugging tools in the training loop.

## Operational Checklist

- [ ] When looking at multivariable loss, be explicit about which variable is fixed and which is moving
- [ ] Ensure gradient vector variable order matches between code and documentation
- [ ] Treat partial derivative values as per-variable responsibility signals—align this as team language
- [ ] Apply the same centered-difference approach per variable during numeric verification
- [ ] Remember that fixed variables' current values still affect interpretation
- [ ] After writing custom loss, verify autograd results with numeric partial derivatives
- [ ] When parameter count is large, apply numeric verification to a sampled subset only

## Summary

A partial derivative measures the local rate of change when only one variable moves in a multivariable function. The convention of fixing the rest lets you temporarily set aside the full complexity and read per-variable responsibility in isolation.

In ML, this concept directly becomes per-parameter gradients. No matter how large the model, each weight receives its own partial derivative value for updates, and those values collectively form the gradient vector that feeds the optimizer. A partial derivative is not a mathematical detail—it is the fundamental unit of learning responsibility distribution.

The next post bundles these partial derivatives into a single gradient vector. That will make it clearer how per-variable responsibilities merge into one directional signal.

## Answering the Opening Questions

- **Why must we look at slopes separately per variable in multi-input functions?**
  - In multivariable functions, a single number cannot simultaneously express all variables' influences. Separating slopes by variable lets you individually assess how much each parameter contributes to loss, enabling appropriately sized and directed updates per parameter.
- **What does "hold other variables fixed" actually mean in partial derivatives?**
  - It means keeping other variables at their current values while varying only the variable of interest by a tiny amount. This convention ensures the measurement purely reflects one variable's effect. In code, this is implemented as `w_plus[i] += h`—perturbing only one element while leaving the rest unchanged.
- **Why do different variables yield different derivative values for the same function?**
  - Because each variable contributes to the function differently. In $f(x, y) = x^2 + 3y$, the partial derivative with respect to $x$ is $2x$ and with respect to $y$ is $3$. Since $x$ contributes nonlinearly and $y$ linearly, their sensitivities differ.
<!-- toc:begin -->
## In this series

- [Calculus for ML 101 (1/10): What Is a Derivative](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): Functions and Slope](./02-functions-and-slope.md)
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

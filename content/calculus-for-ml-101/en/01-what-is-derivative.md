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


![calculus for ml 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/01/01-01-concept-at-a-glance.en.png)
*calculus for ml 101 chapter 1 flow overview*

## Questions to Keep in Mind

- Why is learning in ML directly tied to derivatives?
- What is the difference between average rate of change and instantaneous rate of change, and why does that distinction matter?
- What is the most practical way to relate the slope of a tangent line to the derivative?

## Why This Post Matters

Gradient descent moves parameters in the direction that reduces loss—and that direction comes from differentiation. Backpropagation is an efficient way to compute the derivative of a massive composite function. The learning rate controls how much of that derivative to apply per step. In short, virtually every core term in a training loop stands on top of derivatives.

Frameworks compute gradients automatically, so a model can train even if you never think about calculus. But the moment training becomes unstable, gradients approach zero, or loss suddenly diverges, you need a language for interpreting the numbers. Without derivative intuition you can only stare at logs; with it, you can connect symptoms to function shape and rate of change.

This series does not aim to teach calculus as a standalone math course. Its purpose is to build the minimum viable derivative intuition an ML engineer needs to read training behavior. Once this axis is set in the first post, the later posts read as a connected system rather than isolated techniques.

## Core Perspective

The most practical way to understand a derivative is to shift focus from "what is the function value at this point?" to "if I move slightly from this point, how does the function react?" Average rate of change looks at a wide interval; a derivative shrinks that interval to zero and reads the local reaction at a single point. Once you internalize that difference, a derivative becomes a measurement tool rather than something to memorize.

In ML this local reaction matters enormously. You need to know whether nudging a parameter increases or decreases the loss before you can decide what to do next. A derivative is the mathematically rigorous version of the question "what happens if I change this a little?"

> A derivative does not describe an entire function at once. It is the local signal at the point where you currently stand, telling you which direction to move and how sharply.

## Core Concepts

A derivative ties together rate of change, tangent lines, limits, and numerical approximation. Keep the following flow in mind as you read.

### Rate of change starts with averages

Given two points $a$ and $b$, the average rate of change tells you how much the function changed overall. It is the slope of the secant line. For a straight line this is enough, but for curves the slope differs at every point, so the average is too coarse.

The derivative starts from this average rate and continuously shrinks the interval width toward zero, arriving at the instantaneous rate at a single point. That limiting process is what connects average slope to the tangent line and to the formal definition of a derivative.

### Put a function on the table

```python
def f(x):
    return x ** 2
```

This is one of the simplest nonlinear functions. Because the output grows faster as $x$ increases, the slope changes with position—exactly the property that makes derivatives interesting.

### Average rate of change is the slope of the whole interval

```python
def avg_rate(f, a, b):
    return (f(b) - f(a)) / (b - a)
```

This is the secant-line slope. Not yet a derivative, but it reveals what the derivative refines through a limit. In practical terms, the average rate says "across this whole interval, the function moved roughly like this."

### Numerical differentiation checks derivative intuition computationally

```python
def deriv(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)
```

This centered difference evaluates the slope from both sides of the point and averages them. It is usually more stable than a one-sided (forward) difference. Real deep-learning training does not use this form directly, but it remains a powerful reference for verifying autograd results.

A key practical note: making $h$ smaller is not always better. Too small and floating-point errors dominate; too large and the approximation error grows. Numerical differentiation is theoretically simple but always requires attention to numerical stability.

### The tangent slope is the derivative value

```python
slope = deriv(f, 2.0)  # about 4.0
```

At $x=2$ the function changes at roughly four times the rate of the input. That tangent slope of ~4 means: near this point, a small increase in input produces about four times that increase in output. This "local sensitivity" is exactly what a gradient communicates during training.

### Connecting to a loss function makes the derivative's role clear

```python
def loss(w):
    return (w - 3) ** 2

g = deriv(loss, 0.0)   # negative -> increase w to reduce loss
```

A negative derivative means moving right reduces the loss. This single line is the core intuition of gradient descent. The derivative is not merely describing a function's properties—it is the actionable signal that determines the next update direction.

## Derivative Rules: From Power Rule to Chain Rule Preview

Numerical intuition is valuable for verification, but computing gradients for millions of parameters requires closed-form analytical derivatives.

### Power Rule

The most fundamental rule: if $f(x) = x^n$, then $f'(x) = n \cdot x^{n-1}$.

```python
import numpy as np

def power_rule_check(n, x):
    """Compare analytic and numeric derivatives."""
    analytic = n * x ** (n - 1)
    h = 1e-7
    numeric = ((x + h) ** n - (x - h) ** n) / (2 * h)
    return analytic, numeric, abs(analytic - numeric)

for n in [2, 3, 4]:
    a, num, err = power_rule_check(n, 2.0)
    print(f"x^{n} at x=2: analytic={a:.6f}, numeric={num:.6f}, error={err:.2e}")
# x^2 at x=2: analytic=4.000000, numeric=4.000000, error=3.55e-10
# x^3 at x=2: analytic=12.000000, numeric=12.000000, error=1.43e-09
# x^4 at x=2: analytic=32.000000, numeric=32.000000, error=5.70e-09
```

Errors on the order of $10^{-9}$ confirm that analytic and numeric derivatives agree. This verification pattern applies unchanged when checking gradients of more complex functions.

### Constant Multiple and Sum Rules

If $f(x) = c \cdot g(x)$ then $f'(x) = c \cdot g'(x)$. If $f(x) = g(x) + h(x)$ then $f'(x) = g'(x) + h'(x)$. Simple, but heavily used in ML: when a loss function is a sum of terms, you can compute the gradient of each term independently and add them.

```python
# Sum rule example: L(w) = 0.5*(w-3)^2 + 2*w
# dL/dw = 0.5*2*(w-3) + 2 = (w-3) + 2 = w-1
def loss_sum(w):
    return 0.5 * (w - 3) ** 2 + 2 * w

def loss_sum_grad(w):
    return (w - 3) + 2  # = w - 1

w_test = 1.5
print(f"analytic grad: {loss_sum_grad(w_test)}")  # 0.5
print(f"numeric grad:  {(loss_sum(w_test+1e-7) - loss_sum(w_test-1e-7))/(2e-7):.6f}")
```

### Product Rule

If $f(x) = g(x) \cdot h(x)$ then $f'(x) = g'(x) \cdot h(x) + g(x) \cdot h'(x)$. Needed whenever two learned quantities multiply—regularized losses, attention scores, or gating mechanisms.

### Chain Rule Preview

The derivative of $f(g(x))$ is $f'(g(x)) \cdot g'(x)$. Chapter 5 covers this fully, but it deserves an early taste because it is the single idea that makes backpropagation possible.

```python
import math

# f(x) = sin(x^2)
# f'(x) = cos(x^2) * 2x  (chain rule)
def f_composed(x):
    return math.sin(x ** 2)

def f_composed_grad(x):
    return math.cos(x ** 2) * 2 * x

x = 1.0
analytic = f_composed_grad(x)
numeric = (f_composed(x + 1e-7) - f_composed(x - 1e-7)) / (2e-7)
print(f"chain rule check: analytic={analytic:.6f}, numeric={numeric:.6f}")
# chain rule check: analytic=1.080605, numeric=1.080605
```

## Numerical Differentiation Deep Dive: Choosing h and Error Analysis

How you pick $h$ determines how trustworthy a numerical derivative is. This section runs the experiment.

### Forward Difference vs Central Difference

```python
import numpy as np

def f(x):
    return x ** 3

# Analytic derivative at x=2: 3*x^2 = 12.0
x = 2.0
true_deriv = 12.0

h_values = [1e-2, 1e-4, 1e-6, 1e-8, 1e-10, 1e-12, 1e-14]

print(f"{'h':<12} {'forward err':<16} {'central err':<16}")
print("-" * 44)
for h in h_values:
    forward = (f(x + h) - f(x)) / h
    central = (f(x + h) - f(x - h)) / (2 * h)
    fwd_err = abs(forward - true_deriv)
    ctr_err = abs(central - true_deriv)
    print(f"{h:<12.0e} {fwd_err:<16.2e} {ctr_err:<16.2e}")
```

The pattern that emerges:

| h | Forward difference error | Central difference error |
| --- | --- | --- |
| 1e-2 | ~6e-2 | ~2e-4 |
| 1e-4 | ~6e-4 | ~2e-8 |
| 1e-6 | ~6e-6 | ~1e-10 |
| 1e-8 | ~6e-8 | ~1e-8 (rebound starts) |
| 1e-10 | floating-point dominated | floating-point dominated |
| 1e-14 | useless | useless |

Central difference is most accurate when $h$ is in the range $10^{-5}$ to $10^{-7}$. Below that, the difference $f(x+h) - f(x-h)$ drops below floating-point precision and error grows. In practice, use `h = 1e-5` as the default and adjust only when function values have extreme scale.

### Gradient Checking in Practice

A PyTorch pattern for verifying autograd against numerical differentiation:

```python
import torch

def gradient_check(fn, inputs, eps=1e-5, atol=1e-4):
    """Compare numeric derivative to autograd for each input element."""
    inputs = inputs.detach().requires_grad_(True)
    loss = fn(inputs)
    loss.backward()
    autograd = inputs.grad.clone()

    numeric = torch.zeros_like(inputs)
    flat = inputs.data.view(-1)
    for i in range(flat.numel()):
        orig = flat[i].item()
        flat[i] = orig + eps
        loss_plus = fn(inputs).item()
        flat[i] = orig - eps
        loss_minus = fn(inputs).item()
        flat[i] = orig
        numeric.view(-1)[i] = (loss_plus - loss_minus) / (2 * eps)

    max_diff = (autograd - numeric).abs().max().item()
    passed = max_diff < atol
    return passed, max_diff

# Usage
fn = lambda w: ((w - torch.tensor([1.0, 2.0, 3.0])) ** 2).sum()
w = torch.tensor([0.5, 1.5, 2.5])
ok, diff = gradient_check(fn, w)
print(f"gradient check {'PASS' if ok else 'FAIL'}, max_diff={diff:.2e}")
```

This is the first debugging tool to reach for when implementing a custom layer or when an existing backward pass looks suspicious. The passing criterion is typically relative error below $10^{-4}$.

## When Derivatives Do Not Exist

Not every point admits a derivative. ML encounters this in practice.

### Discontinuities

Where a function jumps, the left and right limits differ, so no derivative exists. This is why step functions are replaced by sigmoid in differentiable pipelines.

### Kinks

$f(x) = |x|$ has different left and right derivatives at $x=0$. ReLU has exactly this structure.

```python
# ReLU derivative: 1 if x > 0, 0 if x < 0, undefined at x = 0
def relu_grad(x):
    if x > 0:
        return 1
    elif x < 0:
        return 0
    else:
        return 0  # convention: 0 or 0.5

# PyTorch returns grad=0 at x=0
import torch
x = torch.tensor(0.0, requires_grad=True)
y = torch.relu(x)
y.backward()
print(f"ReLU grad at x=0: {x.grad.item()}")  # 0.0
```

Frameworks may handle kink-point gradients differently, so when implementing custom activation functions, always specify the boundary behavior explicitly.

### Divergent Derivatives

$f(x) = x^{1/3}$ has an infinite derivative at $x=0$. Rare, but analogous issues arise when a loss function hits an exact zero (e.g., `log(0)`). This is why numerical stability guards like epsilon terms exist.

## Derivatives and the Training Loop: A Complete Example

This section traces how a derivative drives an actual training loop from start to finish.

### Problem Setup

Given input $x$ and target $y$, find parameter $w$ so that $\hat{y} = w \cdot x$ approaches $y$. Loss: $L(w) = (wx - y)^2$.

### Deriving the Gradient

$$\frac{dL}{dw} = 2(wx - y) \cdot x$$

This follows from the power rule and chain rule alone. A positive derivative means $w$ should decrease to reduce loss; negative means increase.

### Training Loop Implementation

```python
import numpy as np

# Data: y = 4x with noise
np.random.seed(42)
X = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
Y = 4.0 * X + np.random.randn(5) * 0.3

# Training parameters
w = 0.0
lr = 0.01
history = []

for epoch in range(20):
    # forward
    pred = w * X
    loss = np.mean((pred - Y) ** 2)

    # backward (analytic derivative)
    grad = np.mean(2 * (pred - Y) * X)

    # update
    w = w - lr * grad
    history.append({'epoch': epoch, 'w': w, 'loss': loss, 'grad': grad})

    if epoch % 5 == 0:
        print(f"epoch={epoch:2d}  w={w:.4f}  loss={loss:.4f}  grad={grad:.4f}")
```

Three patterns emerge from the output:

1. **Early phase**: gradient magnitude is large, $w$ moves fast, loss drops sharply.
2. **Mid phase**: gradient shrinks, update steps get smaller.
3. **Late phase**: gradient approaches zero, $w$ stabilizes near the true value (~4.0).

These three stages are the universal convergence pattern of gradient descent, and the derivative governs every stage.

### Convergence vs Learning Rate

```python
for lr in [0.001, 0.01, 0.05, 0.1]:
    w = 0.0
    for _ in range(50):
        grad = np.mean(2 * (w * X - Y) * X)
        w = w - lr * grad
    final_loss = np.mean((w * X - Y) ** 2)
    print(f"lr={lr:.3f}  final_w={w:.4f}  final_loss={final_loss:.6f}")
```

| Learning rate | w after 50 epochs | Final loss | Observation |
| --- | --- | --- | --- |
| 0.001 | ~2.8 | high | convergence incomplete |
| 0.01 | ~3.97 | low | stable convergence |
| 0.05 | ~3.99 | lowest | fast convergence |
| 0.1 | diverges | increasing | lr too large |

When the learning rate is too large, the step overshoots the minimum and loss increases. Because update magnitude = gradient × learning rate, you must understand the interplay of both to control training stably.

### Reading Training State via Gradient Norm

The magnitude (norm) of the gradient is an indirect diagnostic of training state. Large norm early on means parameters are far from the answer; norm approaching zero means convergence or a saddle point.

```python
grad_norms = [abs(h["grad"]) for h in history]
print(f"early norm: {grad_norms[0]:.4f}")
print(f"mid norm:   {grad_norms[9]:.4f}")
print(f"late norm:  {grad_norms[19]:.4f}")
```

Logging this value to TensorBoard or W&B lets you pinpoint exactly when gradients explode or vanish during training. This is where the concept of a derivative connects directly to production monitoring.

## Common Misconceptions

- The derivative and the function value are different things. A large function value does not imply a large derivative, and vice versa.
- Treating average rate and instantaneous rate as the same concept misses important properties of curved functions.
- Numerical differentiation is convenient but not ground truth. It always carries $h$-selection and floating-point error.
- Watching only gradient magnitude while ignoring sign can reverse your interpretation of the update direction.
- At points where the limit does not exist, the derivative may not exist. Watch for discontinuities and kinks.
- Memorizing "derivative = slope" alone causes confusion when moving to multiple variables. Understanding the derivative as "the coefficient of the local linear approximation" scales better.

## Operational Checklist

- [ ] When looking at a loss function, interpret the gradient sign at the current point first
- [ ] Explain the difference between average rate and instantaneous rate
- [ ] Remember: numerical differentiation is for verification; actual training uses analytic or automatic differentiation
- [ ] When gradients look wrong, verify with a centered-difference check on a small example
- [ ] Read gradient magnitude and direction separately
- [ ] Always run a gradient check after writing a custom layer
- [ ] Check current gradient norm before adjusting the learning rate

## Summary

A derivative tells you the direction and speed at which a function changes near a single point. Tangent lines, limits, and the derivative function are not separate topics—they interlock to read this local change. With this perspective, a derivative is no longer symbol manipulation; it is a sensor for reading the current state.

In ML, this sensor operates on top of the loss function. The loss derivative tells you which direction to move parameters to reduce loss, and that information becomes the optimizer's input. Ultimately, "the model is learning" is a more concrete way of saying "repeatedly reading the loss derivative and updating."

The next post shifts to viewing functions and slopes from a more graphical angle. Having understood the derivative as a single-point rate of change, we'll now look at how function shape and slope connect.

## Answering the Opening Questions

- **Why is learning in machine learning directly connected to differentiation?**
  - Learning is the process of repeatedly updating parameters in the direction that reduces loss. To know the "reducing direction," you need to know which way loss decreases at the current point—and that information is exactly the derivative (gradient). Without differentiation, you cannot determine the next step's direction, so learning itself cannot proceed.
- **What's the difference between average rate of change and instantaneous rate of change, and why must we distinguish them?**
  - Average rate of change summarizes the overall slope across a wide interval, while instantaneous rate of change reads the local slope at a single point by shrinking the interval width toward zero. Since curved functions have different slopes at different positions, the instantaneous rate is needed to determine the precise update direction at the current point.
- **What's the most practical way to understand the relationship between tangent slope and derivative?**
  - The tangent line approximates the function as a straight line near one point, and that line's slope is the derivative value at that point. The derivative organizes tangent slopes at all points into a single function—so understanding it as a "slope map of the function" naturally extends to the gradient concept.
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

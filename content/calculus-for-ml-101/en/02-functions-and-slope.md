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

- Why should a function be understood as an input-output contract rather than just a formula?
- How does the slope of a linear function differ from the local slope of a nonlinear one?
- How does the slope difference between ReLU and sigmoid affect learning?

## Why This Post Matters

A neural network is function composition. Linear transforms map inputs to new representations, nonlinear activations add expressiveness, and the final output function produces predictions. At every stage, learning requires each function to propagate its sensitivity backward through its gradient.

In practice, choosing an activation, diagnosing vanishing gradients, or explaining why input normalization helps always circles back to functions and slopes. Why does sigmoid slow down learning in saturation zones? Why is ReLU practical yet problematic at zero? These questions are answered by the function's shape and gradient structure.

Understanding functions and slopes is not a calculus review—it is building the ability to read model components. This foundation must be solid before extending to partial derivatives and vector-level gradients in later posts.

## Core Perspective

The best way to understand a function is to look at both its formula and its graph. The formula tells you the computation rule; the graph shows how output reacts as input changes. Slope is the bridge between the two.

For linear functions, slope is constant—interpretation is trivial. Nonlinear functions have position-dependent slopes, so which input region the model operates in directly determines where learning is easy and where signal is lost. This is why activation function selection always requires looking at the gradient graph alongside the output graph.

> A function is the contract that maps input to output. Slope is the operational metric showing how sensitively that contract responds at the current point.

## Core Concepts

### A function is an input-output contract

A function consistently defines what output emerges from a given input. This simple definition matters in ML because an entire model is a composition of smaller functions. Each function reveals—through its slope—how sensitively it responds across its input range.

### Linear functions have constant slope

```python
def linear(x, a=2, b=1):
    return a * x + b
```

A linear function produces output that grows at a fixed rate regardless of position. The graph is a straight line, and the slope is the same everywhere. From a model perspective this makes analysis simple, but expressiveness is limited.

```python
def linear_slope(a):
    return a
```

Constant slope is both the strength and the limitation of linearity. Computation and interpretation are trivial, but representing complex patterns requires adding nonlinearity.

### Nonlinear functions have position-dependent slope

```python
def relu(x):
    return max(0.0, x)
```

ReLU clips the negative region to zero and passes the positive region unchanged. Its simplicity is why it's widely used, and that simplicity directly determines its gradient structure.

```python
def relu_grad(x):
    return 1.0 if x > 0 else 0.0
```

The key insight: ReLU gradient is either 0 or 1. In the positive region, signal flows unattenuated. In the negative region, gradient is zero and update signal is cut. This is the origin of "dying ReLU" problems.

### Sigmoid is smooth but has saturation zones

```python
import math

def sigmoid(x):
    return 1 / (1 + math.exp(-x))
```

Sigmoid compresses values into (0, 1)—intuitive for interpretation. But as input magnitude grows, the curve flattens into saturation regions where slope becomes tiny and learning signal weakens.

Looking only at the "nice shape" of a function is not enough. In practice you must simultaneously consider output range, differentiability, saturation zones, and computational stability. Choosing activations without examining gradient distribution makes training performance hard to explain.

### Reading the graphical meaning of the derivative

The derivative of a linear function is a constant. The derivative of ReLU is 0 or 1. The derivative of sigmoid peaks in the center and shrinks at both ends. The derivative's shape directly tells you "where does learning work well?" Input-scale alignment and normalization matter precisely because they keep the model in regions with effective gradients.

## Activation Function Comparison: Reading from a Gradient Perspective

Activation functions are the sole source of nonlinearity in a model. Here we compute and compare gradients of major activations directly.

### Sigmoid Derivative: $\sigma(x)(1-\sigma(x))$

```python
import numpy as np

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def sigmoid_grad(x):
    s = sigmoid(x)
    return s * (1 - s)

x_vals = np.array([-5.0, -2.0, 0.0, 2.0, 5.0])
for x in x_vals:
    print(f"sigmoid({x:+.1f}) = {sigmoid(x):.4f}, grad = {sigmoid_grad(x):.6f}")
# sigmoid(-5.0) = 0.0067, grad = 0.006648
# sigmoid(-2.0) = 0.1192, grad = 0.104994
# sigmoid( 0.0) = 0.5000, grad = 0.250000
# sigmoid(+2.0) = 0.8808, grad = 0.104994
# sigmoid(+5.0) = 0.9933, grad = 0.006648
```

The maximum gradient at $x=0$ is only 0.25. This means every layer with sigmoid shrinks the gradient by at least 3/4. In deep networks, gradients in early layers shrink exponentially—this is the direct cause of vanishing gradients.

### Tanh Derivative: $1 - \tanh^2(x)$

```python
def tanh_grad(x):
    return 1.0 - np.tanh(x) ** 2

for x in x_vals:
    print(f"tanh({x:+.1f}) = {np.tanh(x):+.4f}, grad = {tanh_grad(x):.6f}")
# tanh(-5.0) = -1.0000, grad = 0.000018
# tanh(-2.0) = -0.9640, grad = 0.070651
# tanh( 0.0) = +0.0000, grad = 1.000000
# tanh(+2.0) = +0.9640, grad = 0.070651
# tanh(+5.0) = +1.0000, grad = 0.000018
```

Tanh has a wider output range (-1 to +1) and its gradient at $x=0$ is 1.0—four times sigmoid's peak. Initial training is often faster with tanh, but saturation still occurs at the extremes.

### ReLU and Variants: Gradient Comparison

```python
def relu_grad(x):
    return 1.0 if x > 0 else 0.0

def leaky_relu_grad(x, alpha=0.01):
    return 1.0 if x > 0 else alpha

def elu_grad(x, alpha=1.0):
    return 1.0 if x > 0 else alpha * np.exp(x)

print(f"{'x':<8} {'ReLU':<8} {'Leaky':<8} {'ELU':<10}")
for x in [-2.0, -0.5, 0.0, 0.5, 2.0]:
    r = relu_grad(x)
    l = leaky_relu_grad(x)
    e = elu_grad(x)
    print(f"{x:<8.1f} {r:<8.1f} {l:<8.3f} {e:<10.6f}")
```

| x | ReLU | Leaky ReLU | ELU |
| --- | --- | --- | --- |
| -2.0 | 0.0 | 0.01 | 0.135 |
| -0.5 | 0.0 | 0.01 | 0.607 |
| 0.0 | 0.0 | 0.01 | 1.0 |
| 0.5 | 1.0 | 1.0 | 1.0 |
| 2.0 | 1.0 | 1.0 | 1.0 |

ReLU has zero gradient in the negative region—once a neuron dies it cannot recover. Leaky ReLU and ELU mitigate this by preserving a small gradient.

### Activation Selection Guide

| Criterion | sigmoid | tanh | ReLU | Leaky ReLU |
| --- | --- | --- | --- | --- |
| Output range | (0, 1) | (-1, 1) | [0, inf) | (-inf, inf) |
| Max gradient | 0.25 | 1.0 | 1.0 | 1.0 |
| Saturation zone | both ends | both ends | none (positive) | none |
| Dying problem | no | no | yes | no |
| Primary use | output layer (binary) | RNN hidden | hidden layers (default) | dying-ReLU prevention |

## Function Composition and Gradient Propagation

A neural network is not a single function but a composition of many. Here we trace how gradients propagate through a simple 2-layer network.

### Two-Layer Composition Example

```python
import numpy as np

def layer1(x, w1):
    return w1 * x

def activation(z):
    return 1.0 / (1.0 + np.exp(-z))  # sigmoid

def layer2(a, w2):
    return w2 * a

# forward pass
x = 2.0
w1, w2 = 0.5, 1.5
z1 = layer1(x, w1)      # 1.0
a1 = activation(z1)     # sigmoid(1.0) = 0.7311
y_hat = layer2(a1, w2)  # 1.5 * 0.7311 = 1.0966

print(f"z1={z1:.4f}, a1={a1:.4f}, y_hat={y_hat:.4f}")
```

### Tracing Backpropagation

```python
# assume target y = 3.0
y = 3.0
loss = (y_hat - y) ** 2  # MSE

# backward: dL/dy_hat
dL_dy = 2 * (y_hat - y)  # -3.8068

# dy_hat/da1 = w2
dy_da1 = w2  # 1.5

# da1/dz1 = sigmoid_grad(z1)
s = activation(z1)
da1_dz1 = s * (1 - s)  # 0.1966

# dz1/dw1 = x
dz1_dw1 = x  # 2.0

# chain rule: dL/dw1 = dL/dy * dy/da1 * da1/dz1 * dz1/dw1
dL_dw1 = dL_dy * dy_da1 * da1_dz1 * dz1_dw1
print(f"dL/dw1 = {dL_dw1:.4f}")
# dL/dw1 = -2.2463

# numeric verification
h = 1e-7
w1_plus = w1 + h
y_plus = layer2(activation(layer1(x, w1_plus)), w2)
loss_plus = (y_plus - y) ** 2
numeric_grad = (loss_plus - loss) / h
print(f"numeric dL/dw1 = {numeric_grad:.4f}")
```

The critical number is `da1_dz1 = 0.1966`. Passing through sigmoid shrinks the gradient to about 1/5. With 10 layers: $0.1966^{10} \approx 7 \times 10^{-8}$—the gradient effectively vanishes. Replace sigmoid with ReLU and this multiplier becomes 1, propagating gradient without attenuation.

## Convexity and Optimization Difficulty

Slope alone does not give the full optimization picture. A function's convexity determines whether gradient information reliably leads to the global minimum.

### Convex vs Non-Convex Functions

```python
import numpy as np

# Convex: gradient always points toward minimum
def convex_loss(w):
    return (w - 2.0) ** 2

# Non-convex: multiple local minima
def non_convex_loss(w):
    return w ** 4 - 4 * w ** 2 + w

def non_convex_grad(w):
    return 4 * w ** 3 - 8 * w + 1

# Starting point determines convergence target
for w_init in [-2.0, 0.0, 2.0]:
    w = w_init
    for _ in range(100):
        w = w - 0.01 * non_convex_grad(w)
    print(f"start={w_init:+.1f} -> converged to w={w:.4f}, loss={non_convex_loss(w):.4f}")
```

With convex functions, gradient descent arrives at the same minimum regardless of initialization. With non-convex functions, different starting points may land in different local minima. Deep learning loss surfaces are almost always non-convex, so initialization strategy and learning rate schedules practically determine convergence quality.

### Second Derivative and Curvature

Whether a zero-gradient point is a minimum, maximum, or saddle point is determined by the second derivative.

| Condition | Meaning |
| --- | --- |
| $f'(x) = 0$, $f''(x) > 0$ | local minimum (concave up) |
| $f'(x) = 0$, $f''(x) < 0$ | local maximum (concave down) |
| $f'(x) = 0$, $f''(x) = 0$ | inconclusive (possible inflection) |

```python
# x^3 has f'=0, f''=0 at x=0 -> inflection point, not extremum
def cubic(x):
    return x ** 3

def cubic_grad(x):
    return 3 * x ** 2

def cubic_hessian(x):
    return 6 * x

x = 0.0
print(f"f'(0)={cubic_grad(x)}, f''(0)={cubic_hessian(x)}")
# f'(0)=0.0, f''(0)=0.0 -> inflection point
```

## Input Normalization and Gradient Efficiency

If a function's slope depends on input position, then the input range directly controls learning speed. This is why input normalization is not mere preprocessing—it is directly tied to gradient efficiency.

### Gradient Change Before and After Normalization

```python
import numpy as np

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

def sigmoid_grad(x):
    s = sigmoid(x)
    return s * (1 - s)

# Un-normalized inputs (large scale)
raw_inputs = np.array([100.0, 200.0, 300.0, 400.0, 500.0])
raw_grads = sigmoid_grad(raw_inputs)
print(f"Raw inputs grads: {raw_grads}")  # all nearly 0

# Normalized inputs (mean=0, std=1)
normalized = (raw_inputs - raw_inputs.mean()) / raw_inputs.std()
norm_grads = sigmoid_grad(normalized)
print(f"Normalized grads: {norm_grads}")  # meaningful gradients
```

Before normalization, inputs land in sigmoid's saturation zone where gradients are effectively zero. After normalization, inputs distribute within sigmoid's sensitive range (-2 to +2), producing useful gradients. This is why input normalization was fundamental to training stability even before BatchNorm existed.

### BatchNorm from a Gradient Perspective

BatchNorm re-normalizes activations per mini-batch. From a gradient perspective, what it does is clear:

| Effect | Gradient interpretation |
| --- | --- |
| Mean removal | Centers inputs in sigmoid/tanh's active zone |
| Variance normalization | Keeps inputs within the effective-gradient range |
| Learnable scale/shift | Allows saturation when beneficial |

```python
def batch_norm(x, eps=1e-5):
    mean = np.mean(x)
    var = np.var(x)
    x_hat = (x - mean) / np.sqrt(var + eps)
    return x_hat

x = np.array([3.0, 5.0, 7.0, 9.0, 11.0])
print(f"Before BN - sigmoid grads: {sigmoid_grad(x)}")
x_bn = batch_norm(x)
print(f"After BN  - sigmoid grads: {sigmoid_grad(x_bn)}")
```

## Practical Diagnosis: Reading Learning Problems from Gradients

### Gradient Histogram Patterns

When viewing per-layer gradient histograms in TensorBoard or W&B:

| Pattern | Diagnosis | Action |
| --- | --- | --- |
| Most values near 0 | vanishing gradient | change activation, add skip connections |
| Very wide distribution | exploding gradient | gradient clipping, reduce lr |
| Only specific layer is 0 | dying neuron | Leaky ReLU, change initialization |
| Distribution narrows over time | converging (normal) | continue monitoring |

### Per-Layer Gradient Norm Tracking

```python
import torch
import torch.nn as nn

model = nn.Sequential(
    nn.Linear(10, 64),
    nn.Sigmoid(),
    nn.Linear(64, 64),
    nn.Sigmoid(),
    nn.Linear(64, 1),
)

grad_norms = {}

def hook_fn(name):
    def hook(module, grad_input, grad_output):
        if grad_output[0] is not None:
            grad_norms[name] = grad_output[0].norm().item()
    return hook

for name, layer in model.named_modules():
    if isinstance(layer, (nn.Linear, nn.Sigmoid)):
        layer.register_backward_hook(hook_fn(name))

x = torch.randn(32, 10)
y = torch.randn(32, 1)
loss = nn.MSELoss()(model(x), y)
loss.backward()

for name, norm in grad_norms.items():
    print(f"{name}: grad_norm={norm:.6f}")
```

Run this with sigmoid activations and observe gradient norms shrinking dramatically in earlier layers. Switch to ReLU and norms become uniform. This experiment directly demonstrates the core message of this post: a function's gradient characteristics directly impact learning.

## Common Misconceptions

- Understanding only the formula without looking at the graph makes it easy to miss slope and saturation zones.
- ReLU being simple does not mean it is always problem-free. It is non-differentiable at $x=0$ and has zero gradient in the negative region.
- Sigmoid being smooth does not mean it always helps learning. Gradient becomes extremely small in saturation zones.
- Comparing inputs of different scales directly leads to misinterpretation of function sensitivity.
- Thinking about linear slope and nonlinear local slope in the same way weakens the explanation of why activations are needed.
- A zero gradient does not automatically mean a minimum. Always verify with the second derivative or surrounding landscape.

## Operational Checklist

- [ ] Can explain the graph and gradient characteristics of the model's main activation functions together
- [ ] Distinguish the impact of ReLU's zero region and sigmoid's saturation zone on learning
- [ ] Remember that input scale alignment connects to gradient interpretation
- [ ] Look at derivative shape, not just function values
- [ ] When suspecting vanishing gradients, inspect activation local slopes first
- [ ] Can justify activation choice based on max gradient and saturation characteristics
- [ ] Identify bottleneck points in the gradient propagation path of composed functions

## Summary

A function is the contract mapping input to output, and slope shows how sensitively that contract responds at the current point. Linear functions have constant slope, but nonlinear functions have position-dependent slope—so learning difficulty and signal flow vary by region.

In ML this difference is deeply practical. Choosing even a single activation function is ultimately choosing a function shape and gradient-flow profile. To understand why ReLU, sigmoid, and tanh each have different tradeoffs, look at gradient structure before output range.

The next post extends the view to functions with multiple inputs. Once we do that, partial derivatives—reading slope per variable—become a natural necessity.

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

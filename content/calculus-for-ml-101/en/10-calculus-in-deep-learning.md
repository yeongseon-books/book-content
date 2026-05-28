---
series: calculus-for-ml-101
episode: 10
title: "Calculus for ML 101 (10/10): Calculus in Deep Learning"
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
  - DeepLearning
  - Capstone
  - Beginner
seo_description: A capstone tour of how networks, loss, optimizers, backprop, and calculus combine into the deep learning training loop
last_reviewed: '2026-05-15'
---

# Calculus for ML 101 (10/10): Calculus in Deep Learning

The ideas from this series do not live in isolation. Functions and slopes, partial derivatives, gradients, the chain rule, loss functions, gradient descent, optimizers, and backpropagation all show up inside the same training loop. The goal of this final post is to put those pieces back together as one working system.

This is the final post in the Calculus for ML 101 series.

In this post, we'll walk through the forward pass, loss computation, backward pass, optimizer update, and the operating rules around that loop. Once the full cycle is visible, calculus stops feeling like a separate math chapter and starts feeling like the control interface for learning itself.

By the end, you'll read framework training code and see exactly which calculus concept each line enacts—and why differentiation is the central mechanism of the entire loop, not just the `backward()` call.

> In deep learning, calculus is the common language that turns prediction error into parameter movement, one training step at a time.


![calculus for ml 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/10/10-01-concept-at-a-glance.en.png)
*calculus for ml 101 chapter 10 flow overview*

## Questions to Keep in Mind

- What stages make up the deep learning training loop, and where does calculus appear in each one?
- How do the forward pass and loss computation prepare the work that backward needs to do?
- How do gradient computation and the optimizer update connect?

## Why It Matters

Deep learning frameworks compress the training loop into very few lines. The code is short, but the meaning of each stage easily blurs. Understanding what forward produces, what loss quantifies, what backward propagates, and what the optimizer changes is what lets you actually read training bugs.

In practice, the same model architecture can produce very different results depending on data pipeline, loss reduction, gradient zeroing, optimizer scheduling, and eval/train mode management. The common skeleton that cuts through all of these is the training loop. Once this skeleton is firm, you never lose the essence regardless of which framework you encounter.

This post also serves as the series summary. Calculus is no longer a separate math chapter—it becomes visible as the central mechanism that converts prediction into error, error into gradient, and gradient into parameter update.

## Core Perspective

The most practical way to understand deep learning training is to picture one loop. The model produces a prediction from input; the loss function computes error; backpropagation produces gradients; the optimizer updates parameters. Then it repeats.

Once this loop is clear, calculus becomes the common language threading through the entire cycle. Forward is function composition. Loss is the objective function. Backward is the execution of the chain rule. The optimizer step converts gradients into movement.

> In deep learning, calculus is not a formula for a specific layer—it is the common interface that converts prediction error into parameter updates across the entire training loop.

## Core Concepts

### The model is a function that maps input to prediction

```python
import math

def model(x, w, b):
    return sigmoid(w * x + b)

def sigmoid(z):
    return 1 / (1 + math.exp(-z))
```

This tiny model is the simplest form: a linear combination followed by sigmoid. But it already contains function composition and nonlinearity. Complex deep learning models are essentially longer compositions of such functions.

### Loss turns the gap between prediction and target into a number

```python
def bce(y, p, eps=1e-7):
    return -(y * math.log(p + eps) + (1 - y) * math.log(1 - p + eps))
```

Forward alone does not produce learning. The prediction must be quantified as an error via loss, and this loss is the starting point for gradients. The `eps` for numerical stability is a habit that matters greatly in real training code.

### Gradients can be expressed analytically

```python
def grads(x, y, w, b):
    p = model(x, w, b)
    err = p - y
    return err * x, err
```

This function shows the simplified gradient intuition from BCE + sigmoid. The key point: error is decomposed into each parameter's responsibility. The weight receives `err * x`; the bias receives `err`. Partial derivatives and the chain rule appearing as actual code output.

### The optimizer step converts gradients into movement

```python
def step(x, y, w, b, lr=0.1):
    dw, db = grads(x, y, w, b)
    return w - lr * dw, b - lr * db
```

This single line is the optimizer's essence. It scales the gradient from backward by the learning rate and moves in the opposite direction. Large frameworks add Adam, momentum, weight decay, but the core structure remains.

### The training loop is just iteration

```python
def train(data, epochs=100, lr=0.1):
    w, b = 0.0, 0.0
    for _ in range(epochs):
        for x, y in data:
            w, b = step(x, y, w, b, lr)
    return w, b
```

Training is not grand—it is this repetition. Data comes in, predictions are made, loss is computed, gradients become updates, and the new parameters feed the next forward pass. This closed loop is essentially all of training.

### Framework code expresses the same loop directly

```python
optimizer.zero_grad()
pred = model(x)
loss = criterion(pred, y)
loss.backward()
optimizer.step()
```

These five lines compress every concept in this series. `pred = model(x)` is function composition. `loss = criterion(pred, y)` makes the objective explicit. `loss.backward()` executes the chain rule across the computation graph. `optimizer.step()` converts gradient information into real parameter movement.

### Evaluation follows different rules—explained by the same structure

```python
with torch.no_grad():
    pred = model(x)
    metric = accuracy(pred, y)
```

Evaluation does not need gradients, so it should not build a backward graph. Once you see training as a forward-loss-backward-update loop, it becomes obvious why `train()`/`eval()` mode switches and `no_grad()` blocks matter. They are not framework rituals—they are part of running the loop correctly.

### First failure points to check in any training loop

- Did you forget `zero_grad()`, so stale gradients are leaking across steps?
- Is the loss decreasing while the evaluation metric gets worse, suggesting the loss design is misaligned with the real objective?
- Are scheduler timing, `train()`/`eval()` mode, or optimizer-step ordering inconsistent across experiments?
- Is reproducibility weak enough that you are blaming the model architecture for what is really a training-loop configuration issue?

Many training bugs come from this operating layer rather than from exotic calculus mistakes. That is why a clear loop-level mental model is so valuable.

## Automatic Differentiation: Forward Mode vs Reverse Mode

Automatic differentiation (AD) is different from both symbolic differentiation and numerical differentiation. It follows the program's computation graph to produce exact derivative values.

### Forward Mode

Forward mode propagates a derivative signal alongside values in the input direction. Each variable maintains both a value and a tangent:

$$
(x, \dot{x}) \rightarrow (f(x), \dot{f})
$$

It is efficient when input dimension is small and output dimension is large.

### Reverse Mode

Reverse mode first computes all values, then propagates adjoints from output toward inputs. Deep learning typically has very many parameters but a scalar output (loss), so reverse mode is overwhelmingly more efficient.

| Mode | Computation Direction | One Pass Yields | Best When |
| --- | --- | --- | --- |
| Forward mode | Input → Output | Derivative w.r.t. one input direction | Input dimension small |
| Reverse mode | Output → Input | All input gradients for one output | Many parameters (training) |

```python
# PyTorch reverse-mode example
optimizer.zero_grad()
loss = criterion(model(x), y)
loss.backward()  # computes dL/dtheta for all theta
optimizer.step()
```

## Jacobian and Hessian in Practice

The Jacobian is the first-derivative matrix of a vector-valued function; the Hessian is the second-derivative matrix of a scalar function.

$$
J_{ij} = \frac{\partial f_i}{\partial x_j}, \quad
H_{ij} = \frac{\partial^2 L}{\partial x_i \partial x_j}
$$

### When you need the Jacobian

- Sensitivity analysis in sequence-to-sequence models
- Log-det Jacobian computation in normalizing flows
- State-transition sensitivity in physics-informed models

```python
import torch
from torch.autograd.functional import jacobian

def f(v):
    x, y = v[0], v[1]
    return torch.stack([x * y, x + y**2])

v = torch.tensor([2.0, 3.0], requires_grad=True)
J = jacobian(f, v)
print(J)
```

### When you need the Hessian

- Loss landscape curvature analysis
- Sharpness-based generalization diagnostics
- Second-order approximation for step-size tuning

```python
import torch
from torch.autograd.functional import hessian

def scalar_loss(v):
    x, y = v[0], v[1]
    return (x - 1)**2 + 3*(y + 2)**2 + x*y

v = torch.tensor([0.0, 0.0], requires_grad=True)
H = hessian(scalar_loss, v)
print(H)
```

Full Hessian computation is prohibitively expensive at scale. In practice, Hessian-vector products (HVP) or diagonal approximations are used instead.

## Second-Order Optimization Overview

First-order methods (SGD, Adam) use only gradients. Second-order methods additionally incorporate curvature to navigate the loss landscape more precisely.

### Newton's Method Core

$$
\theta_{t+1} = \theta_t - H^{-1} \nabla L
$$

Theoretically fast convergence, but computing and inverting the Hessian is infeasible for large-scale deep learning.

### Practical Approximations

| Method | Idea | Strength | Limitation |
| --- | --- | --- | --- |
| L-BFGS | Low-rank curvature accumulation | Fast for small/medium problems | Ill-suited for large mini-batch |
| K-FAC | Per-layer Fisher approximation | Exploits DL structure | High implementation complexity |
| Shampoo family | Matrix preconditioner | Richer curvature than per-coord | Memory/compute cost increase |

In practice, full second-order methods are rarely adopted wholesale. The standard approach is to secure stability with AdamW + schedule + clipping, then selectively apply second-order tools at specific bottlenecks.

## Gradient Flow in Attention Mechanisms

The core of the Transformer is scaled dot-product attention:

$$
A = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right), \quad O = AV
$$

### Gradient Flow Summary

- Given `dL/dO`, the gradient toward `V` takes the form `A^T(dL/dO)`.
- The gradient toward `A` passes through `(dL/dO)V^T`, then through the softmax Jacobian.
- Softmax has a probability-sum constraint, so its Jacobian has both diagonal and off-diagonal terms.

In attention, matrix-multiplication differentiation + softmax differentiation + scaling combine through the chain rule.

### Shape Tracking Example

| Tensor | Shape (batch excluded) |
| --- | --- |
| `Q, K, V` | `(T, d)` |
| `scores = QK^T` | `(T, T)` |
| `A = softmax(scores)` | `(T, T)` |
| `O = AV` | `(T, d)` |

Fixing shapes first dramatically reduces dimension errors during backward debugging.

## Differentiation in Normalization Layers

BatchNorm and LayerNorm share a common "normalize → scale/shift" structure:

$$
\hat{x} = \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}}, \quad y = \gamma \hat{x} + \beta
$$

### Key Points in LayerNorm Backward

- Input gradients are coupled through mean and variance paths.
- Within the same token, inter-feature interaction terms appear, making it more complex than element-wise differentiation.
- `epsilon` directly affects numerical stability—setting it too small can paradoxically create instability.

### Operational Checks

| Item | Meaning | How to Check |
| --- | --- | --- |
| `eps` | Denominator stability | First suspect on NaN/Inf |
| `gamma` initial value | Scale freedom | Check output variance in early training |
| train/eval mode | BN statistics updates | Check inference performance wobble |

## Full Training Loop Anatomy: Where Differentiation Acts

A step-by-step dissection of the real training loop:

| Stage | Code Unit | Differentiation Perspective | Failure Symptom |
| --- | --- | --- | --- |
| 1 | `model.train()` | Prepare differentiable path | BN/Dropout behavior mismatch |
| 2 | `pred = model(x)` | Composite function evaluation, cache creation | Memory excess, shape error |
| 3 | `loss = criterion(pred, y)` | Objective scalarization | Loss scale distortion |
| 4 | `loss.backward()` | Reverse-mode AD execution | grad None, NaN |
| 5 | `clip_grad_norm_` | Gradient stabilization | Training stall/divergence |
| 6 | `optimizer.step()` | Gradient → parameter movement | Update missed |
| 7 | `scheduler.step()` | Time-axis policy applied | lr curve abnormal |
| 8 | `optimizer.zero_grad()` | Accumulation buffer reset | Prior step signal leaks |

### Full Skeleton in Code

```python
for epoch in range(num_epochs):
    model.train()
    for x, y in train_loader:
        pred = model(x)
        loss = criterion(pred, y)

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()

    model.eval()
    with torch.no_grad():
        for x_val, y_val in val_loader:
            val_pred = model(x_val)
            val_loss = criterion(val_pred, y_val)
```

Understanding this loop means the core diagnostic points stay the same regardless of framework. Differentiation's role does not end at `loss.backward()`—it gains meaning on top of the conditions established by the surrounding stages.

## Differentiation-Centric Debugging Checklist

1. **Gradient existence check**: Verify `.grad is None` for key parameters first.
2. **Gradient magnitude check**: Use per-layer norm histograms to detect vanishing/exploding.
3. **Loss scale check**: Ensure reduction setting (`mean`/`sum`) isn't causing excessive gradient magnitude.
4. **Mixed precision audit**: Log scaler updates and overflow-skip counts.
5. **Scheduler order audit**: Document the call order of `optimizer.step()` and `scheduler.step()`.

## Connecting the Entire Series in One Picture

The 10 posts of this series connect into a single sentence:

- Functions and slopes provide the language of rates of change.
- Partial derivatives and gradients define the descent direction on multi-variable loss landscapes.
- The chain rule and backpropagation extend that direction across deep composite functions.
- Optimizers and schedulers convert gradients into actual training trajectories.
- The training loop repeats this process to improve performance.

## Loss Function Gradient Characteristics

Even with the same model, changing the loss function changes gradient magnitude and training dynamics.

| Loss | Key Gradient Characteristic | Practical Point |
| --- | --- | --- |
| MSE | Linearly proportional to error magnitude | Sensitive to outliers |
| BCEWithLogits | Large signal on confident wrong predictions | Numerically stable implementation recommended |
| CrossEntropy | Simplifies when combined with softmax | Default for multi-class |
| Huber | Clamps large-error region | Robust to noisy labels |

If you change the loss but keep the learning rate unchanged, gradient-scale mismatch is likely. Loss changes and optimizer tuning changes should be treated as a single unit.

## Reproducibility Across the Full Loop

Differentiation-based training has many stochastic elements, making reproducibility management critical:

```python
import random
import numpy as np
import torch

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

Even with the same differentiation formulas, changing the seed, data shuffle, or mixed precision setting alters the training trajectory. Experiment logs must record both mathematical settings and operational settings together.

## Capstone Checklist: Reducing Training Failures from a Calculus Perspective

1. Verify shape alignment between model output and loss input first.
2. Save loss, lr, and grad norm together for the first 100 steps.
3. On NaN occurrence, check input scale, loss stabilization options, and clipping in order.
4. On val performance plateau, check data distribution and label quality alongside optimizer.
5. In final reports, state in words: "which differentiation signal, through which update policy, produced the performance improvement."

## Common Confusions

- Computing loss does not automatically produce updates. Backward and optimizer step must follow.
- Forgetting `zero_grad` lets previous-step gradients accumulate.
- Computing gradients during evaluation wastes memory and computation.
- Confusing train/eval mode changes Dropout and BatchNorm behavior, distorting result interpretation.
- Ignoring reproducibility makes it impossible to tell whether experiment differences are due to model architecture or training-loop configuration.

## Checklist

- [ ] Forward, loss, backward, update order is clearly documented as the team's shared loop
- [ ] `zero_grad` and optimizer step placement included in code review criteria
- [ ] Train/eval mode switching rules separated between training and inference code
- [ ] Learning rate, seed, scheduler, weight decay recorded together for reproducibility
- [ ] When diagnosing training issues, inspect the entire training loop alongside model architecture

## Wrap-up

In deep learning, calculus is not a specific formula fragment—it is the central mechanism that drives the entire training loop. Forward produces predictions via function composition; loss quantifies error; backward computes gradients via the chain rule; the optimizer converts those gradients into parameter updates.

Every concept in this series—derivatives, partial derivatives, gradients, the chain rule, loss functions, gradient descent, optimization, backpropagation—has a specific seat inside this one loop. Understanding deep learning ultimately means being able to explain what mathematical role each stage of this loop plays.

This post concludes the Calculus for ML 101 series. From now on, regardless of what model or framework you encounter, you'll be able to re-read how learning actually happens in the language of calculus.

## Answering the Opening Questions

- **What stages make up the deep learning training loop, and where does differentiation appear in each?**
  The training loop follows `forward → loss → backward → update` order. Differentiation doesn't appear only in backward—the intermediate values saved in forward and the scalarization of loss must exist for reverse-mode to work. That is, differentiation is the connection rule of the entire loop.
- **What do forward pass and loss computation prepare for backward?**
  Forward creates each operation node's values and graph connections; loss defines the final scalar objective. Only with these two stages ready can backward chain-multiply local gradients to compute each parameter's gradient.
- **How do gradient computation and optimizer update connect?**
  The `dL/dtheta` produced by backward is the optimizer's input. The optimizer applies policies like lr, moments, variance estimates, and weight decay to convert gradients into actual parameter movements. Thus gradient quality and optimizer policy aren't separate problems but consecutive stages of the same learning path.
<!-- toc:begin -->
## In this series

- [Calculus for ML 101 (1/10): What Is a Derivative](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): Functions and Slope](./02-functions-and-slope.md)
- [Calculus for ML 101 (3/10): Partial Derivatives](./03-partial-derivatives.md)
- [Calculus for ML 101 (4/10): Gradient](./04-gradient.md)
- [Calculus for ML 101 (5/10): Chain Rule](./05-chain-rule.md)
- [Calculus for ML 101 (6/10): Loss Function](./06-loss-function.md)
- [Calculus for ML 101 (7/10): Gradient Descent](./07-gradient-descent.md)
- [Calculus for ML 101 (8/10): Optimization](./08-optimization.md)
- [Calculus for ML 101 (9/10): Backpropagation Intuition](./09-backpropagation-intuition.md)
- **Calculus in Deep Learning (current)**

<!-- toc:end -->

## References

- [Deep Learning Book - Goodfellow et al.](https://www.deeplearningbook.org/)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [CS231n - Convolutional Neural Networks](https://cs231n.stanford.edu/)
- [Reproducibility - PyTorch](https://pytorch.org/docs/stable/notes/randomness.html)
- [Zeroing out gradients in PyTorch](https://pytorch.org/tutorials/recipes/recipes/zeroing_out_gradients.html)

Tags: Calculus, ML, DeepLearning, Capstone, Beginner

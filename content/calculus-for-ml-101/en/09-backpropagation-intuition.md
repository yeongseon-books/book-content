---
series: calculus-for-ml-101
episode: 9
title: "Calculus for ML 101 (9/10): Backpropagation Intuition"
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
  - Backprop
  - NeuralNetwork
  - Beginner
seo_description: A beginner-friendly tour of backpropagation, computation graphs, forward pass, backward gradients, and autograd intuition for ML
last_reviewed: '2026-05-15'
---

# Calculus for ML 101 (9/10): Backpropagation Intuition

So far in this series, we've built the math behind derivatives, partial derivatives, gradients, the chain rule, loss, and optimization. The remaining practical question is computational: how do you produce gradients for thousands or millions of weights without numerically perturbing each one?

This is the 9th post in the Calculus for ML 101 series.

In this post, we'll use computation graphs, forward and backward passes, local derivatives, and gradient accumulation to explain backpropagation. The goal is not to reimplement a deep learning framework, but to understand why one backward pass can still recover the full gradient efficiently.

By the end, terms like `zero_grad`, gradient accumulation, and graph retention will feel like natural operational concepts rather than API trivia.

> Backpropagation is not new math. It is the chain rule executed systematically over a computation graph, with cached forward values and accumulated backward signals.


![calculus for ml 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/09/09-01-concept-at-a-glance.en.png)
*calculus for ml 101 chapter 9 flow overview*

## Questions to Keep in Mind

- Why can backpropagation compute gradients for so many weights in a single pass?
- In computation-graph terms, what does the forward pass leave behind, and what does the backward pass do with it?
- What does it really mean to store a local derivative?

## Why It Matters

PyTorch, TensorFlow, and JAX all compute gradients automatically. So a model trains even if you don't understand backpropagation. But when training wobbles, when gradients accumulate unexpectedly, when memory grows unchecked, or when a detached branch silently stops learning—that's when understanding the principle lets you narrow the problem faster.

Once you understand backpropagation, you stop seeing gradients as "values the model somehow produces." It becomes clear that values are created in the forward pass, and backward multiplies each operation's local derivative by the upstream gradient then passes it to parents. Then it's obvious why shared nodes require gradient summation, and why retaining graphs costs more memory.

This post is also direct preparation for the final article. To see the full deep learning training loop, you need to understand that forward, loss, backward, and update form one closed cycle—and backpropagation is the backward step.

## Core Perspective

The most intuitive way to understand backpropagation is to think in terms of a computation graph. Each node computes a value and knows its local derivative with respect to its parent nodes. Starting from the final output and multiplying these local derivatives backward lets you compute how much each input contributed to the result.

In this structure, the roles of forward and backward are clearly separated. Forward creates and caches values; backward propagates gradients using those values. Backward cannot exist alone—it fundamentally requires the information stored during forward.

> Backpropagation is the procedure of applying the chain rule backward, and it works efficiently because each node in the computation graph provides its own local derivative.

## Core Concepts

### Start from the smallest computation graph node

```python
class Node:
    def __init__(self, val, parents=()):
        self.val = val
        self.parents = parents
        self.grad = 0.0
```

A node holds a current value, parent nodes, and a gradient buffer that gets filled during backpropagation. Real frameworks are far more complex, but the key insight is that each operation result knows its own computation history.

### Addition nodes have simple local derivatives

```python
def add(a, b):
    n = Node(a.val + b.val, (a, b))
    n.local = (1.0, 1.0)
    return n
```

For addition, the local derivative of the output with respect to each input is 1. The important point is that a node doesn't just produce a result during forward—it also records the local derivative needed for backward.

### Multiplication nodes use the counterpart's value as local derivative

```python
def mul(a, b):
    n = Node(a.val * b.val, (a, b))
    n.local = (b.val, a.val)
    return n
```

For multiplication, each input's local derivative is the other input's value. This example shows clearly why forward must cache intermediate values: backward needs those values to compute local derivatives.

### Backward accumulates gradients from output toward inputs

```python
def backward(n):
    n.grad = 1.0
    stack = [n]
    while stack:
        x = stack.pop()
        for p, lg in zip(x.parents, x.local):
            p.grad += x.grad * lg
            stack.append(p)
```

The output node's gradient is set to 1 because the derivative of anything with respect to itself is 1. Then each parent receives `current_gradient × local_derivative`, accumulated with `+=`. The `+=` is crucial because shared nodes receive contributions from multiple paths.

### A small example shows the full flow

```python
a, b, c = Node(2.0), Node(3.0), Node(4.0)
y = mul(add(a, b), c)
backward(y)
# a.grad == 4.0, b.grad == 4.0, c.grad == 5.0
```

Forward computes `add(a, b)` first, then multiplies the result by `c`. Backward starts at the output, applies the multiplication node's local derivatives, then follows through the addition node's local derivatives to reach `a`, `b`, `c`. Small as it is, this example contains the full essence of chain rule and gradient accumulation.

### Shared nodes make gradient accumulation visibly necessary

```python
a = Node(2.0)
b = add(a, a)
y = mul(b, a)
backward(y)

# y = (a + a) * a = 2a^2
# dy/da = 4a, so at a=2 the gradient is 8
print(a.grad)
```

**Expected output:** `8.0`

This example shows that a single node can be reused multiple times in a graph. `a` appears twice inside `add(a, a)`, and that result is multiplied by `a` again. During backpropagation, multiple paths contribute to the same variable. If you overwrite instead of accumulate, you lose part of the true gradient. This is exactly why frameworks accumulate gradients by default.

### The autograd operation point

Frameworks automate this process. But if you don't call `zero_grad`, gradients accumulate; if you retain unnecessary graphs, memory grows; if you misuse detach, learning paths break. Understanding autograd means understanding not just the internal math, but also graph lifetime and gradient buffer management from an operational perspective.

```python
optimizer.zero_grad()
pred = model(x)
loss = criterion(pred, y)
loss.backward()
optimizer.step()
```

The reason this order matters is that backward typically accumulates rather than overwrites gradients. If you don't clear the previous step's residue, the current batch's signal mixes with stale gradient state. In small toy code the effect is subtle, but in real training it is a common cause of hard-to-interpret loss curves.

## Forward and Backward: Line-by-Line Trace

The fastest way to internalize backpropagation is to trace forward and backward side by side on the same sample. We'll use a 2-layer fully-connected network:

$$
x \in \mathbb{R}^2, \quad h = \text{ReLU}(W_1x+b_1), \quad \hat{y}=W_2h+b_2, \quad L=\frac{1}{2}(\hat{y}-y)^2
$$

### Forward Trace Table

| Step | Expression | Output Shape | Values to Cache |
| --- | --- | --- | --- |
| 1 | `z1 = W1·x + b1` | `(2,)` | `x`, `W1`, `z1` |
| 2 | `h = ReLU(z1)` | `(2,)` | `z1`, `h` |
| 3 | `y_hat = W2·h + b2` | `(1,)` | `h`, `W2`, `y_hat` |
| 4 | `L = 0.5*(y_hat-y)^2` | scalar | `y_hat`, `y` |

The cache stored during forward is used directly to compute local gradients during backward. If this link breaks, backward cannot run.

### Backward Trace Table

| Step | Propagation Expression | Meaning |
| --- | --- | --- |
| 1 | `dL/dy_hat = y_hat - y` | Starting gradient from loss |
| 2 | `dL/dW2 = (dL/dy_hat) · h^T` | Output-layer weight gradient |
| 3 | `dL/db2 = dL/dy_hat` | Output-layer bias gradient |
| 4 | `dL/dh = W2^T · dL/dy_hat` | Signal propagated to hidden representation |
| 5 | `dL/dz1 = dL/dh * ReLU'(z1)` | Activation local gradient applied |
| 6 | `dL/dW1 = (dL/dz1) · x^T` | Input-layer weight gradient |
| 7 | `dL/db1 = dL/dz1` | Input-layer bias gradient |

## Computation Graph Chain Rule Example

Consider the expression as a computation graph:

$$
q = a \cdot b, \quad r = q + c, \quad y = r^2
$$

```python
def forward(a, b, c):
    q = a * b
    r = q + c
    y = r ** 2
    cache = (a, b, c, q, r)
    return y, cache

def backward(dy, cache):
    a, b, c, q, r = cache
    dr = dy * (2 * r)
    dq = dr * 1
    dc = dr * 1
    da = dq * b
    db = dq * a
    return da, db, dc
```

Setting `dy=1` gives derivatives with respect to `y`. Each node only needs to know "its own local gradient" and multiplies the upstream gradient by it before passing to parents. This is the chain rule from an implementation perspective.

### Hand-Calculation Verification

With `a=2, b=3, c=4`:

- `q=6`, `r=10`, `y=100`
- `dy/dr = 2r = 20`
- `dr/dq = 1`, `dr/dc = 1`
- `dq/da = b = 3`, `dq/db = a = 2`

Therefore:
- `dy/da = 20 × 1 × 3 = 60`
- `dy/db = 20 × 1 × 2 = 40`
- `dy/dc = 20`

Numerical differentiation confirms the same values. Repeating this exercise builds intuition for reading gradient magnitudes in backward logs.

## Full 2-Layer Network Numerical Example

A scalar-output 2-layer network with actual numbers:

- Input: `x=[1.0, -2.0]`
- Target: `y=1.0`
- `W1=[[0.2, -0.4], [0.7, 0.1]]`, `b1=[0.0, 0.0]`
- `W2=[0.6, -0.3]`, `b2=0.1`

### Forward

1. `z1 = W1·x + b1 = [0.2*1 + (-0.4)*(-2), 0.7*1 + 0.1*(-2)] = [1.0, 0.5]`
2. `h = ReLU(z1) = [1.0, 0.5]`
3. `y_hat = W2·h + b2 = 0.6*1 + (-0.3)*0.5 + 0.1 = 0.55`
4. `L = 0.5*(0.55 - 1)^2 = 0.10125`

### Backward

1. `dL/dy_hat = 0.55 - 1 = -0.45`
2. `dL/dW2 = -0.45 * [1.0, 0.5] = [-0.45, -0.225]`
3. `dL/db2 = -0.45`
4. `dL/dh = W2 * (-0.45) = [0.6*(-0.45), (-0.3)*(-0.45)] = [-0.27, 0.135]`
5. `ReLU'(z1) = [1, 1]` so `dL/dz1 = [-0.27, 0.135]`
6. `dL/dW1 = dL/dz1 ⊗ x`
   - Row 1: `-0.27 * [1, -2] = [-0.27, 0.54]`
   - Row 2: `0.135 * [1, -2] = [0.135, -0.27]`
7. `dL/db1 = [-0.27, 0.135]`

Tracing this by hand makes autograd output immediately interpretable.

## Gradient Accumulation: Behavior and Use Cases

By default, many frameworks do not overwrite `.grad`—they accumulate. The two code patterns below have different semantics:

```python
# Case A: Zero every step
for x, y in loader:
    optimizer.zero_grad()
    loss = model.loss(x, y)
    loss.backward()
    optimizer.step()
```

```python
# Case B: Accumulate over 4 steps then update
acc_steps = 4
optimizer.zero_grad()
for i, (x, y) in enumerate(loader):
    loss = model.loss(x, y) / acc_steps
    loss.backward()
    if (i + 1) % acc_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

Case B is useful when memory constraints prevent large effective batches. Note that without dividing loss by `acc_steps`, gradient magnitude scales up and learning-rate interpretation changes.

## Vanishing/Exploding Gradient Diagnosis

In deep networks, gradients undergo repeated multiplication across layers, causing magnitude issues.

### Diagnostic Checkpoints

| Symptom | Signal in Logs | First Response |
| --- | --- | --- |
| Vanishing gradient | Early-layer grad norm below `1e-8` | Check initialization, residual structure, norm layers |
| Exploding gradient | Grad norm spikes, loss NaN | Clipping, lr reduction, warmup |
| Single layer unstable | Large per-layer grad variance | Check per-layer lr/regularization/activation |

### Grad Norm Logging

```python
import torch

def grad_norm(model):
    total = 0.0
    for p in model.parameters():
        if p.grad is None:
            continue
        total += p.grad.detach().pow(2).sum().item()
    return total ** 0.5

# Inside training loop
loss.backward()
print('grad_norm=', grad_norm(model))
```

### Explosion Prevention: Clipping

```python
import torch

torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
optimizer.step()
```

Clipping does not "solve" the root cause, but it prevents divergence so experimentation can continue—a safety net.

## Backpropagation Debugging Sequence

1. **Single-batch overfit test**: Confirm loss drops to near-zero on one batch.
2. **Numerical gradient spot-check**: Pick a few parameters, compare with finite difference.
3. **Per-layer grad norm tracking**: Locate vanishing/exploding at the layer level.
4. **Detach/no_grad audit**: Verify no graph breaks in branches that should learn.
5. **Accumulation policy check**: Verify `zero_grad` placement and loss scaling.

## Mini-Batch Backpropagation: Summation Along the Sample Axis

Hand-calculation examples use single samples, but real training uses mini-batch mean loss:

$$
L = \frac{1}{B}\sum_{i=1}^{B} L_i
$$

So parameter gradients are also sample-gradient averages:

$$
\nabla_\theta L = \frac{1}{B}\sum_{i=1}^{B} \nabla_\theta L_i
$$

Understanding this immediately connects to why `reduction='sum'` vs `reduction='mean'` changes learning-rate interpretation.

### Reduction Setting Comparison

| Setting | Gradient Magnitude | Practical Interpretation |
| --- | --- | --- |
| `mean` | Less sensitive to batch size | Safe default |
| `sum` | Scales proportionally with batch size | Requires lr re-tuning |

## Backpropagation and Memory Usage

Because backward needs cached forward intermediate values, activation tensors dominate memory in deep networks.

### Memory Saving Strategies

1. **Gradient checkpointing**: Skip saving some intermediates; recompute during backward.
2. **Mixed precision**: Reduce storage precision for activations and gradients.
3. **Micro-batch accumulation**: Split batch and accumulate gradients to lower peak memory.

```python
# PyTorch gradient checkpointing concept
from torch.utils.checkpoint import checkpoint

def forward(self, x):
    x = checkpoint(self.block1, x)
    x = checkpoint(self.block2, x)
    return self.head(x)
```

Recomputation costs extra time, so the memory-speed tradeoff must be verified experimentally.

## Backpropagation Error Types and Debugging Table

| Error Message / Symptom | Candidate Cause | What to Check |
| --- | --- | --- |
| `element 0 does not require grad` | Misuse of detach/no_grad | Tensor `requires_grad` chain |
| `Trying to backward through the graph a second time` | Graph reuse | Review `retain_graph=True` necessity |
| Grad always 0 | Activation saturation, dead ReLU | Input distribution, initialization, lr |
| Specific layer grad None | Path disconnection | Module connections, branch merge |

## Local Derivative Intuition Table

These derivatives recur so often that they should feel like reflexes rather than things you look up:

| Operation | Local Gradient |
| --- | --- |
| `y = x + c` | `dy/dx = 1` |
| `y = c·x` | `dy/dx = c` |
| `y = x^2` | `dy/dx = 2x` |
| `y = ReLU(x)` | `dy/dx = 1 if x>0 else 0` |
| `y = sigmoid(x)` | `dy/dx = y(1-y)` |

With this table as a baseline, reading backward logs and tracing where gradients shrink or grow becomes much faster.

## Numerical Gradient Check Automation

When implementing custom backward logic, automating numerical-gradient verification on small tensors catches regression bugs early:

```python
import numpy as np

def numerical_grad(f, x, h=1e-5):
    grad = np.zeros_like(x)
    it = np.nditer(x, flags=['multi_index'], op_flags=['readwrite'])
    while not it.finished:
        idx = it.multi_index
        old = x[idx]
        x[idx] = old + h
        fx1 = f(x)
        x[idx] = old - h
        fx2 = f(x)
        x[idx] = old
        grad[idx] = (fx1 - fx2) / (2 * h)
        it.iternext()
    return grad
```

When verifying, compute relative error alongside:

$$
\text{rel\_err} = \frac{|g_{analytic}-g_{numeric}|}{\max(1,|g_{analytic}|,|g_{numeric}|)}
$$

A practical threshold is `1e-4`. Values above that warrant checking operation order, broadcasting, and axis reduction (`sum`, `mean`).

## Accumulation Operating Rules for Large-Scale Training

- Increasing accumulation steps grows the effective batch but reduces optimizer-step frequency.
- Step-based schedulers must be designed around "optimizer step count" for warmup length to behave as intended.
- Gradient clipping should be applied after accumulation completes, just before the optimizer step, for consistent semantics.

Failing to document these rules means teammates interpret the same code differently, making experiment comparison unreliable.

## Common Confusions

- Gradients are easily assumed to be overwritten each step, but in many frameworks the default is accumulation.
- Without cached forward values, local derivative computation is impossible during backward.
- At shared nodes, gradients from multiple paths must be summed—easy to forget.
- Unnecessarily retaining the graph causes memory usage to grow rapidly.
- Misusing detach or no-grad contexts can silently create branches where no gradient flows.

## Checklist

- [ ] `zero_grad` placement is explicitly managed at every training step
- [ ] Understand which forward values backward needs
- [ ] Aware that shared nodes trigger gradient accumulation
- [ ] When diagnosing memory issues, check graph retention and detach usage together
- [ ] Verify autograd results with numerical checks on small examples

## Wrap-up and Next Steps

Backpropagation is the procedure of executing the chain rule backward over a computation graph. Forward creates values and intermediate state; backward uses each node's local derivative to propagate the output's gradient toward inputs. This structure enables computing the entire model's gradients in a single backward pass.

The practically important points are gradient accumulation and graph lifetime. `zero_grad`, detach, cached activations, and memory usage are all operational topics that arise directly from backpropagation's structure. Even though frameworks automate much of this, knowing the principle lets you narrow bugs far more quickly.

Next post: the *Calculus in Deep Learning* capstone—tying forward, loss, backward, and optimizer step into one training cycle, and why this is the standard skeleton of all deep learning training.

## Answering the Opening Questions

- **Why can backpropagation compute gradients for numerous weights all at once?**
  Each node in the computation graph provides its local gradient, and when propagating gradient from output to input, the chain rule multiplies along each path then sums at shared parameters. So without running separate numerical differentiation per parameter, a single backward pass yields all gradients.
- **From the computation graph perspective, what does forward pass leave behind versus backward pass?**
  Forward pass caches not just predictions but intermediate values needed for backward (`z`, activations, branch results). Backward uses that cache to compute `dL/dnode` and propagate to parent nodes, ultimately filling each parameter's `.grad` buffer.
- **What does it actually mean to "store local derivatives"?**
  It means each operation node retains "the derivative of output with respect to input." For example, multiplication uses the counterpart's value as local gradient; ReLU uses a 0/1 mask based on input sign. Backward implements the chain rule by multiplying the upstream gradient by this local value.
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
- **Backpropagation Intuition (current)**
- Calculus in Deep Learning (upcoming)

<!-- toc:end -->

## References

- [Backpropagation - CS231n](https://cs231n.github.io/optimization-2/)
- [Calculus on Computational Graphs - Olah](https://colah.github.io/posts/2015-08-Backprop/)
- [PyTorch Autograd](https://pytorch.org/tutorials/beginner/blitz/autograd_tutorial.html)
- [JAX Autograd Cookbook](https://jax.readthedocs.io/en/latest/notebooks/autodiff_cookbook.html)
- [Zeroing out gradients in PyTorch](https://pytorch.org/tutorials/recipes/recipes/zeroing_out_gradients.html)

Tags: Calculus, ML, Backprop, NeuralNetwork, Beginner

---
title: "LLM from Scratch 101 (6/9): Learning via Gradients"
series: llm-from-scratch-101
episode: 6
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- PyTorch
- Transformer
- Tutorial
last_reviewed: '2026-05-14'
seo_description: Once the model class is complete, training becomes the moment where every earlier module finally starts moving through real data.
---

# LLM from Scratch 101 (6/9): Learning via Gradients

Once the model class is complete, training is the moment where everything starts to feel real. Until now, we have been assembling structure: embeddings, attention, blocks, and the GPT wrapper. The training loop is where those pieces finally meet data and start changing.

The reassuring part is that the core loop is short. You pull a batch, compute a loss, backpropagate, and let the optimizer update the weights. The harder part is that the surrounding details matter immediately: batch construction, optimizer choice, learning-rate scheduling, gradient clipping, evaluation cadence, and checkpointing.

TinyShakespeare is especially helpful here because the numbers move quickly enough to watch. The loss starts around 4 and gradually drops, which is often the first moment when the model stops feeling like a static class definition and starts feeling like a learner.

This is the 6th post in the LLM from Scratch 101 series. Here we will build a compact but usable `train.py` with AdamW, warmup, cosine decay, gradient clipping, periodic evaluation, and checkpoint saving.

![LLM from Scratch 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/06/06-01-the-5-line-core-of-the-training-loop.en.png)
*LLM from Scratch 101 chapter 6 flow overview*

> A training loop is four lines repeated — forward, loss, backward, step — and training a GPT is the engineering of keeping those four lines stable for hundreds of thousands of iterations. Gradient clipping, LR schedules, and mixed precision are not extras; they are what keeps the loop from collapsing.

## Questions to Keep in Mind

- What are the five lines at the heart of the training loop?
- Why is AdamW usually easier to work with than SGD for Transformers?
- What do warmup and cosine decay do for stability?

## Why this matters

The training loop is the boundary between a static architecture and a working learning system. Everything we built in earlier posts—embeddings, attention, blocks, and the GPT class—only becomes meaningful once it participates in repeated updates against real data.

It is also where many beginners finally connect the theory to code. In practice, what matters is not just knowing the definition of gradient descent. It is knowing when gradients are cleared, where the loss is computed, when the optimizer steps, and how to detect when the loop has gone off the rails.

From an engineering perspective, the support code matters early. Learning-rate schedules, clipping, validation checks, and checkpoints are not “advanced extras.” They are part of making experiments debuggable and repeatable from the start.

## The most practical mental model: training is repeated error correction

Training is not a magical state change. **The model predicts, compares itself against the target, computes gradients from that error, and shifts its weights slightly in the downhill direction.** That sequence repeats thousands of times.

The quality of the loop depends on its discipline. Batches must be valid, losses must be computed correctly, the optimizer must move at a safe scale, and monitoring must tell us whether the model is actually learning or simply memorizing noise.

That is why the loop is both simple and operational. It is a short core surrounded by the instrumentation that keeps the experiment trustworthy.

## Core ideas

### The center of the loop is five lines

At its smallest, the loop is `zero_grad()`, `forward`, `backward()`, `clip_grad_norm_`, and `step()`. Everything else is support code for scheduling, logging, validation, and saving.

The most important detail here is what `backward()` actually does. Autograd walks the computation graph in reverse and fills the `grad` field on each parameter. The optimizer then consumes those gradients and updates the weights.

### AdamW is a practical default for small GPTs

For a small char-level Transformer, AdamW is usually far easier to manage than SGD. It combines momentum-like behavior with adaptive scaling per parameter, which makes early training less brittle.

The decoupled weight decay is also important. In Transformer-style models full of embeddings and linear layers, that separation tends to produce a cleaner optimization experience. In this series, `lr=3e-4`, `weight_decay=0.1`, and `betas=(0.9, 0.95)` form a solid starting point.

### Warmup and cosine decay soften the start and finish

Applying a large learning rate immediately after random initialization can make the first updates too violent. We usually ramp up the rate for a short warmup period and then gradually reduce it with cosine decay.

```python
import math

def get_lr(it: int, learning_rate: float) -> float:
    warmup_iters = 100
    lr_decay_iters = 5000
    min_lr = learning_rate * 0.1

    if it < warmup_iters:
        return learning_rate * (it + 1) / warmup_iters
    if it > lr_decay_iters:
        return min_lr

    decay_ratio = (it - warmup_iters) / (lr_decay_iters - warmup_iters)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return min_lr + coeff * (learning_rate - min_lr)
```

Warmup is the engine reaching operating temperature. Cosine decay is the model shortening its step size as it gets closer to a useful basin.

### Gradient clipping is a small line with a large payoff

Even healthy training runs can hit occasional gradient spikes, especially early on. `torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)` is a simple guardrail that prevents those spikes from turning into numerical damage.

Clipping is not a glamorous trick. It is a stability tool. When a run behaves badly, it helps separate “the learning rate is too high” from “a single bad step just exploded the norm.”

## Building the training script step by step

### Step 1. Put the full loop in one `train.py`

The following script assumes the `GPT` class and the `train.bin` / `val.bin` files from earlier posts already exist.

```python
from dataclasses import asdict
from pathlib import Path
import math

import numpy as np
import torch

from model import GPT, GPTConfig

batch_size = 32
block_size = 64
max_iters = 5000
eval_interval = 500
eval_iters = 50
learning_rate = 3e-4
weight_decay = 0.1
betas = (0.9, 0.95)
device = "cuda" if torch.cuda.is_available() else "cpu"

config = GPTConfig(block_size=block_size)
model = GPT(config).to(device)
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=learning_rate,
    weight_decay=weight_decay,
    betas=betas,
)

train_data = np.memmap(Path("data") / "train.bin", dtype=np.uint16, mode="r")
val_data = np.memmap(Path("data") / "val.bin", dtype=np.uint16, mode="r")

def get_batch(split: str):
    data = train_data if split == "train" else val_data
    ix = torch.randint(len(data) - block_size - 1, (batch_size,))
    x = torch.stack([
        torch.from_numpy(np.array(data[i : i + block_size], dtype=np.int64))
        for i in ix.tolist()
    ])
    y = torch.stack([
        torch.from_numpy(np.array(data[i + 1 : i + block_size + 1], dtype=np.int64))
        for i in ix.tolist()
    ])
    return x.to(device), y.to(device)

def get_lr(it: int) -> float:
    warmup_iters = 100
    lr_decay_iters = 5000
    min_lr = learning_rate * 0.1
    if it < warmup_iters:
        return learning_rate * (it + 1) / warmup_iters
    if it > lr_decay_iters:
        return min_lr
    decay_ratio = (it - warmup_iters) / (lr_decay_iters - warmup_iters)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return min_lr + coeff * (learning_rate - min_lr)

@torch.no_grad()
def estimate_loss() -> dict[str, float]:
    model.eval()
    out = {}
    for split in ["train", "val"]:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            xb, yb = get_batch(split)
            _, loss = model(xb, yb)
            losses[k] = loss.item()
        out[split] = losses.mean().item()
    model.train()
    return out

for iter_num in range(max_iters + 1):
    lr = get_lr(iter_num)
    for param_group in optimizer.param_groups:
        param_group["lr"] = lr

    if iter_num % eval_interval == 0:
        losses = estimate_loss()
        print(
            f"step {iter_num}: train {losses['train']:.4f}, "
            f"val {losses['val']:.4f}, lr {lr:.6f}"
        )

    xb, yb = get_batch("train")
    optimizer.zero_grad(set_to_none=True)
    _, loss = model(xb, yb)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()

torch.save({"model": model.state_dict(), "config": asdict(config)}, "ckpt.pt")
```

This script is compact, but it already contains the essentials: batch sampling, scheduling, evaluation, clipping, and checkpoint saving.

### Step 2. Know what a healthy log trend looks like

When you first run training, focus on the trend rather than exact numbers. With random initialization and 65 output classes, the initial loss should land near `ln(65)`, which is about 4.17. From there, it should decline steadily over time.

**Expected output:**

```text
step 0: train 4.1731, val 4.1748, lr 0.000003
step 500: train 2.2114, val 2.3457, lr 0.000300
step 1000: train 1.9262, val 2.0410, lr 0.000293
step 2500: train 1.6038, val 1.7489, lr 0.000180
step 5000: train 1.4725, val 1.6182, lr 0.000030
```

The exact values will vary, but the shape of the run should not. If you start with `nan`, or if the loss barely moves after many hundreds of steps, revisit the model wiring and the batch logic before tuning anything else.

### Step 3. Train loss alone only tells half the story

By evaluating both train and validation loss at a fixed interval, you can spot overfitting, learning-rate issues, or data bugs much earlier. For a small experiment, averaging over a few batches under `@torch.no_grad()` is enough.

In small models, the trend is often easier to read than the absolute magnitude. If train keeps falling but validation stalls, overfitting is likely. If neither moves, the problem is often in the learning rate or the data pipeline.

### Step 4. Use a one-batch overfit test as a fast debugger

When full training looks broken, the fastest narrow test is often to overfit a single batch on purpose. If the loss falls quickly there, your forward pass, backward pass, and optimizer path are probably wired correctly.

```python
xb, yb = get_batch("train")

for step in range(200):
    optimizer.zero_grad(set_to_none=True)
    _, loss = model(xb, yb)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()

    if step % 20 == 0:
        print(step, loss.item())
```

**Expected output:**

```text
0 4.15
20 2.73
40 1.82
60 1.21
80 0.79
100 0.54
```

If even this does not improve, the bug is likely structural rather than statistical. At that point, re-check target shifting, logits flattening, and attention masking.

### Step 5. Save the experiment context, not just the weights

Saving only model weights is tempting, but incomplete. The config matters too. The generation script in the next post needs the same `block_size`, `n_embd`, `n_layer`, and related settings to rebuild the model correctly.

That is why `torch.save({'model': ..., 'config': ...}, 'ckpt.pt')` is worth keeping from the beginning. Once you have multiple experiments, it becomes the difference between reproducible work and mystery checkpoints.

## Fast failure triage

Training problems can feel vague at first. In practice, a short symptom-to-check sequence is enough to narrow most failures quickly.

| Symptom | First thing to inspect | Common cause |
| --- | --- | --- |
| `nan` from the first few steps | Learning rate, mask, logits scale | LR too high or broken attention |
| Train and val both refuse to improve | `get_batch()` and target shift | Incorrect `y` alignment |
| Train improves but val does not | Validation log trend | Overfitting or split issue |
| Loss occasionally spikes hard | Gradient norm | Missing clipping or unstable batch |
| Reloaded runs are hard to compare | Saved config and checkpoint naming | Missing experiment context |

This table matters because it turns “training feels wrong” into a concrete inspection plan.

## How to think about it in practice

The goal of this series is not maximum throughput. It is to build a training loop that is transparent and repeatable. That is why we leave mixed precision, gradient accumulation, and distributed training for later. First, the loop itself should be understandable and debuggable.

Even in a toy project, operational habits matter. A five-minute CPU run or a one-minute GPU run is still wasted if you cannot explain the loss curve or reproduce the checkpoint. Conversely, once the loop logs cleanly and saves enough context, even a small experiment becomes a solid learning artifact.

## Common mistakes

- It is easy to assume the training loop must be long and complex, but the core is just five lines.
- AdamW can look interchangeable with SGD, but for small Transformers it is usually much easier to tune.
- Warmup and decay can look optional, yet they directly affect startup stability and late-stage convergence.
- Watching only training loss hides overfitting and data issues.
- Saving weights without config makes checkpoints much less useful later.

## Checklist

- [ ] Can explain `zero_grad -> forward -> backward -> clip -> step` without reciting it mechanically.
- [ ] Printed or plotted the warmup + cosine schedule.
- [ ] Logged both train and validation loss through `estimate_loss()`.
- [ ] Ran a one-batch overfit test to verify the learning path.
- [ ] Saved both model weights and config into `ckpt.pt`.

## Summary

In this post, we built a minimal but practical `train.py` for GPT training. Batch sampling, AdamW, scheduling, clipping, periodic evaluation, and checkpointing now work together as one loop.

We also saw that training is less mysterious than it sounds. The core is just repeated error correction. The extra structure around it exists to keep that correction stable, observable, and reproducible.

In the next post, we will load `ckpt.pt` and turn the trained model into a generator, producing Shakespeare-like text one token at a time.

## Answering the Opening Questions

- **What are the five core lines that drive the training loop?**
  - The core loop in this article is `optimizer.zero_grad(set_to_none=True)`, `model(xb, yb)`, `loss.backward()`, `clip_grad_norm_`, and `optimizer.step()`. Everything else—`estimate_loss()`, lr schedule, `torch.save(...)`—wraps this repetition to make it more stable and reproducible.
- **Why is AdamW easier to handle than SGD for transformer training?**
  - AdamW automatically adjusts per-parameter update magnitudes and carries momentum-like properties, making even small GPT training far less sensitive than SGD. The article defaulting to `torch.optim.AdamW(..., lr=3e-4, weight_decay=0.1, betas=(0.9, 0.95))` reflects that practicality.
- **How do warmup and cosine decay help training stability?**
  - In `get_lr()`, the first 100 steps use linear warmup to ramp up the step size slowly, then a cosine curve reduces it again—mitigating both early-stage instability and late-stage oscillation. This prevents oversized initial steps and overfitting-driven wobble as loss descends from the 4.x range.

<!-- toc:begin -->
## In this series

- [LLM from Scratch 101 (1/9): Turning Text into Numbers](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): From Integers to Vectors and Positions](./02-embedding.md)
- [LLM from Scratch 101 (3/9): Deciding Which Tokens to Focus On](./03-attention.md)
- [LLM from Scratch 101 (4/9): The Transformer Block: A Unit of Depth](./04-transformer-block.md)
- [LLM from Scratch 101 (5/9): Assembly: Completing the GPT Model Class](./05-gpt-model.md)
- **LLM from Scratch 101 (6/9): Learning via Gradients (current)**
- LLM from Scratch 101 (7/9): Sampling — Generating Text from a Trained Model (upcoming)
- LLM from Scratch 101 (8/9): Adapting the Base Model to Specific Tasks (upcoming)
- LLM from Scratch 101 (9/9): Turning Your LLM into a Chatbot — FastAPI + Streaming (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [Decoupled Weight Decay Regularization (AdamW)](https://arxiv.org/abs/1711.05101)
- [nanoGPT train.py](https://github.com/karpathy/nanoGPT/blob/master/train.py)
- [PyTorch clip_grad_norm_](https://pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html)
- [PyTorch AdamW](https://pytorch.org/docs/stable/generated/torch.optim.AdamW.html)

### Related Series

- [LLM API Production 101 — Retry and error handling](../../llm-api-production-101/en/05-retry-and-error-handling.md)
- [AI Agent 101 — Agent evaluation](../../ai-agent-101/en/07-agent-evaluation.md)
- [LangGraph 101 — State and checkpoints](../../langgraph-101/en/02-state-and-checkpoints.md)

Tags: LLM, PyTorch, Transformer, Tutorial

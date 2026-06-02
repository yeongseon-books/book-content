---
title: "LLM from Scratch 101 (5/9): Assembly: Completing the GPT Model Class"
series: llm-from-scratch-101
episode: 5
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
last_reviewed: '2026-04-29'
seo_description: We've built the input stage and attention mechanism, and in the last
  post, we established the core transformer block.
---

# LLM from Scratch 101 (5/9): Assembly: Completing the GPT Model Class

> LLM from Scratch 101 series (5/9)

We've built the input stage and attention mechanism, and in the last post, we established the core transformer block. Most of the components are now in place. The remaining task is surprisingly clean: start with embeddings, pass them through the blocks, apply a final normalization, and project to the vocab size to get the logits.

When I first reached this stage, I felt a sense of anticlimax. The name GPT sounds so massive that I expected something far more complex. However, at the implementation level, the structure is quite linear. It's about stacking the same blocks and adding a head that reads the distribution of the next character.

Details matter, of course. Without practical mechanisms like input length validation, loss reshaping, and weight tying, the code can quickly become messy. Today, we'll organize those parts.

The mental model for today is this: **GPT is an autoregressive model that stacks blocks on top of embeddings and converts the final hidden states into the next token distribution.**

This is the 5th post in the LLM from Scratch 101 series.

---

![LLM from Scratch 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/05/05-01-the-forward-pass-at-a-glance.en.png)
*LLM from Scratch 101 chapter 5 flow overview*

## Questions to Keep in Mind

- In what order does the GPT class call its components?
- Why does weight tying shrink parameters without hurting quality?
- Why does cross-entropy loss fit on one line?

## The Forward Pass at a Glance

The input is a tensor of token IDs with shape `(B, T)`. We add token and position embeddings, then pass them through six blocks sequentially. After a final `ln_f` layer, we project to the vocab dimension via `lm_head` to produce logits of shape `(B, T, vocab_size)`.

All the components we created earlier appear here. The model class acts more as assembly code than a new algorithm.

## class GPT(nn.Module) — An 80-line Model

The code below completes our `model.py`. Assuming `Block` and `CausalSelfAttention` are available from previous posts, we wrap things up with `GPTConfig` and the `GPT` class itself.

```python
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F

@dataclass
class GPTConfig:
    vocab_size: int = 65
    n_layer: int = 6
    n_head: int = 4
    n_embd: int = 128
    block_size: int = 64

class GPT(nn.Module):
    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        self.config = config
        self.token_emb = nn.Embedding(config.vocab_size, config.n_embd)
        self.pos_emb = nn.Embedding(config.block_size, config.n_embd)
        self.blocks = nn.ModuleList([Block(config) for _ in range(config.n_layer)])
        self.ln_f = nn.LayerNorm(config.n_embd)
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)
        self.lm_head.weight = self.token_emb.weight

    def forward(
        self, idx: torch.Tensor, targets: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        b, t = idx.shape
        if t > self.config.block_size:
            raise ValueError(f"cannot forward sequence of length {t}")

        pos = torch.arange(t, device=idx.device)
        tok_emb = self.token_emb(idx)
        pos_emb = self.pos_emb(pos)
        x = tok_emb + pos_emb

        for block in self.blocks:
            x = block(x)

        x = self.ln_f(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(b * t, self.config.vocab_size),
                targets.view(b * t),
            )

        return logits, loss
```

At this point, the model is ready for training. Each `Block` hands back the same `(B, T, C)` residual stream it received, so the assembled GPT stays tensor-consistent from embeddings to logits.

## Weight Tying: Linking the LM Head and Embedding Matrix

The line `self.lm_head.weight = self.token_emb.weight` is a small but common optimization. We share the same weights between the input token embedding and the output projection matrix.

It makes intuitive sense. The vector space used to read a character shouldn't be radically different from the space used to score which character to output next. Since the Press & Wolf paper, this has become a default practice. In small models, it saves parameters and often makes training more stable.

## Loss Function: A Single Line for Cross Entropy

Language modeling is ultimately about predicting the next character at each position. Logits have the shape `(B, T, vocab_size)`, and the targets are `(B, T)`. Since `F.cross_entropy` prefers 2D inputs where the class dimension is last, we flatten both to `(B*T, ...)`.

Understanding this reshape makes the training loop much cleaner later. From the loss function's perspective, it just sees `N` prediction rows and `N` ground truth labels, regardless of batch or sequence dimensions.

## Initializing the Model and Counting Parameters

Let's look at the numbers. With `vocab_size=65`, `n_layer=6`, `n_head=4`, `n_embd=128`, and `block_size=64`, the model isn't as large as the 10M figure mentioned in the original plan.

With weight tying, the total parameter count is approximately 1,204,096. Token and position embeddings take up about 16k, six blocks account for 1.18M, and the final LayerNorm uses 256. Seeing these numbers makes the model's scale feel much more grounded.

```python
config = GPTConfig()
model = GPT(config)
num_params = sum(p.numel() for p in model.parameters())
print(f"params: {num_params:,}")
```

## Sanity Check: Forward Pass Before Training

Before starting the training loop, it's good practice to check if the loss is around `ln(65)`. With 65 classes and random initialization, the model's initial guesses should be roughly uniform, which results in a loss of about 4.17.

```python
import torch

config = GPTConfig()
model = GPT(config)
idx = torch.randint(0, config.vocab_size, (4, config.block_size))
targets = torch.randint(0, config.vocab_size, (4, config.block_size))
logits, loss = model(idx, targets)

print(logits.shape)
print(loss.item())
```

A loss in the low 4s is usually normal. If you see 20 or `nan`, you should re-examine the block connections, reshaping, and mask ranges.

## Organizing Hyperparameters with a Config Dataclass

Even in small examples, scattering hyperparameters makes the code tedious to maintain. The `GPTConfig` dataclass keeps model dimensions, layer counts, head counts, and context length in one place, making it easy to pass to `train.py` or `generate.py`.

The default settings for this series are conservative. `n_layer=6`, `n_head=4`, `n_embd=128`, and `block_size=64` are small enough to run TinyShakespeare on a CPU or a modest GPU. While the numbers are small, the architecture is identical to GPT. At this stage, a traceable model is a better teacher than a massive one.

## What's next

The model core is finished. In the next post, we'll implement the training loop—pulling mini-batches and running the `forward -> loss -> backward -> optimizer.step()` cycle. You'll see the TinyShakespeare loss drop from 4.17 down to the 1.0 range.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Traced the forward pass of the 80-line GPT class.
- [ ] Printed parameter counts with and without weight tying.
- [ ] Ran one forward + loss as a pre-training sanity check.
- [ ] Can explain every field of GPTConfig.

<!-- a-grade-example:end -->

## Common Misconceptions

- It feels like the GPT class hides some complex new algorithm, but the core is just assembling the parts you already built.
- Weight tying looks like an optional cosmetic, but it meaningfully saves parameters and can improve stability.
- The flatten step for loss feels like a hack, but it is standard reshaping to match the class dimension expected by `cross_entropy`.
- It seems safe to skip the `block_size` guard, but learned positional embeddings are bound to the maximum length.
- A config dataclass looks like mere convenience, but it directly affects experiment reproducibility and checkpoint portability.

## Operations Checklist

- [ ] Can you narrate the forward pass in order: embedding → block loop → `ln_f` → `lm_head`?
- [ ] Do you understand what `self.lm_head.weight = self.token_emb.weight` does?
- [ ] Can you explain why logits and targets are flattened to `(B*T, ...)` shapes?
- [ ] Have you verified the sanity check: random-init loss ≈ 4.17 (`-ln(1/65)`)?
- [ ] Is the model fully controlled by a single `GPTConfig` (dimensions, context length, layers)?

## Structure Verification Report After Assembly

Once the `GPT` class is complete, print a structure report before running any training. Checking parameter counts, per-module proportions, and forward-shape consistency up front prevents many downstream surprises.

```python
def report_model(model: GPT) -> None:
    total = sum(p.numel() for p in model.parameters())
    emb = sum(p.numel() for n, p in model.named_parameters() if "token_emb" in n or "pos_emb" in n)
    blocks = sum(p.numel() for n, p in model.named_parameters() if "blocks" in n)
    head = sum(p.numel() for n, p in model.named_parameters() if "lm_head" in n)

    print(f"total  : {total:,}")
    print(f"emb    : {emb:,} ({emb/total:.2%})")
    print(f"blocks : {blocks:,} ({blocks/total:.2%})")
    print(f"head   : {head:,} ({head/total:.2%})")
```

Sample output for the series' default config:

```text
total  : 1,204,096
emb    :   16,512 (1.37%)
blocks : 1,185,792 (98.48%)
head   :    8,320 (0.69%)
```

These numbers immediately tell you where optimization effort pays off. In a small char-level model, blocks dominate capacity, so structural experiments naturally focus on block parameters.

### Separate the forward-contract test into a file

```python
def test_forward_contract() -> None:
    cfg = GPTConfig(vocab_size=65, block_size=64, n_layer=2, n_head=2, n_embd=32)
    model = GPT(cfg)

    idx = torch.randint(0, cfg.vocab_size, (3, 16))
    tgt = torch.randint(0, cfg.vocab_size, (3, 16))
    logits, loss = model(idx, tgt)

    assert logits.shape == (3, 16, cfg.vocab_size)
    assert loss is not None and torch.isfinite(loss)
```

This single test catches most refactoring mistakes. It guards the `(logits, loss)` return contract early.

### Weight Tying: Before vs After

| Aspect | Without Tying | With Tying |
| --- | --- | --- |
| Parameter count | Higher | Lower |
| Input/output representation sharing | None | Shared |
| Small-model stability | Situation-dependent | Generally favorable |
| Implementation complexity | Low | Very low (one line) |

Weight tying is a single line, but it meaningfully affects parameter structure and generalization. Document *why* that line exists.

### Logging Activation Norms Per Layer

```python
@torch.no_grad()
def log_activation_norms(model: GPT, idx: torch.Tensor) -> None:
    x = model.token_emb(idx) + model.pos_emb(torch.arange(idx.size(1), device=idx.device))
    print("emb_norm", float(x.norm().item()))
    for i, block in enumerate(model.blocks):
        x = block(x)
        print(f"block_{i}_norm", float(x.norm().item()))
    x = model.ln_f(x)
    print("ln_f_norm", float(x.norm().item()))
```

Comparing these logs before and after training gives intuition for how blocks cumulatively transform representations. If norms monotonically increase or drop sharply, check initialization, learning rate, and norm placement together.

## Why Document Design Decisions at Assembly Time

`GPT(nn.Module)` looks clean once finished, but in practice, if "why we assembled it this way" is not recorded, maintenance difficulty spikes fast. Especially as small projects grow, briefly documenting architectural decisions pays off in long-term cost.

### Specify the input/output contract

Record model forward input shape, dtype, allowed lengths, and optional-targets rules in a docstring or design note. When this contract is ambiguous, inference code and training code end up with different assumptions, and bugs pass tests only to surface in production.

### Record weight-tying rationale

Sharing embedding and LM head reduces parameters and can improve generalization. But in some experiments it constrains expressivity. The key is not "always use it" but leaving evidence of *why* you chose it for the current experiment.

### Keep the loss computation path simple

Whether loss lives inside the model or outside in the training loop varies by team. Educational/research code benefits from internal computation (readability), while production pipelines often externalize it for finer monitoring granularity. Either way, fix the convention once and keep it consistent across the series.

### Include model metadata in checkpoints

Beyond the bare state dict, checkpoints should carry minimal metadata:

- Architecture hyperparameters (`n_layer`, `n_head`, `n_embd`, `block_size`)
- Tokenizer version or hash
- Training data version ID
- Code commit SHA

With this information, "same model" has a precise definition, and reproducibility and comparison experiment quality improve significantly.

## Quick Verification Experiments After Assembly

Right after completing the model class, short smoke tests come before full training. Run forward on random input several times to confirm shape and loss stability, then train on a tiny dataset for 200–500 steps to see that loss actually decreases. If both pass, the chance of architectural integration errors drops sharply.

Also verify that re-running with the same seed produces a similar early loss curve—this catches reproducibility issues early.

## Maintenance Perspective

The GPT class should be designed for *iterative extension*, not "one-time completion." When hyperparameter additions, new head experiments, or context-length changes arrive, the interface should remain stable. This makes team-scale development significantly more productive.

Simplicity at assembly time is not aesthetics—it is an operational strategy.

## Practice FAQ

### Should I follow these steps rigorously even for a tiny model?

Yes—smaller models actually benefit more from strict contracts. Low capacity magnifies the impact of input noise and implementation inconsistencies. Establishing reproducible experiment units first accelerates quality improvements even before you scale model size.

### What if experiment speed and quality management conflict?

To go faster, reduce failure cost rather than increasing experiment count. Locking config files, standardizing logs, and storing checkpoint metadata let you run more *valid* experiments in the same time.

### What single thing is most worth recording?

The change rationale, expected effect, and observed result—briefly. Especially "why this value was chosen" lets you reconstruct decision context weeks later.

## Summary

This article assembled all prior components into a single `GPT(nn.Module)` class. Once input embedding, block loop, final normalization, LM head, and optional loss computation are wired together, the model has a complete forward pass.

We also explored why implementation details like weight tying, flatten-based cross-entropy, and centralized `GPTConfig` matter. These details keep code short yet reproducible, and enable smooth extension to the next stage.

Next, we attach a training loop: feeding mini-batches repeatedly, computing loss, and using backprop plus an optimizer step to actually update weights.

## Answering the Opening Questions

- **In what order does the GPT class call its components?**
  - Input `(B, T)` first adds `token_emb(idx)` and `pos_emb(pos)` to form residual stream `x`, then passes through `for block in self.blocks: x = block(x)`, and finally goes through `ln_f` and `lm_head` to produce logits. The skeleton of GPT's forward pass is: embedding → repeated blocks → final normalization → vocab projection.
- **Why is weight tying between token embedding and LM head useful?**
  - `self.lm_head.weight = self.token_emb.weight` makes input embedding and output projection share the same vector space, reducing parameter count and tightening training for small models. The savings look modest here, but as vocab size grows, this single line's effect scales significantly.
- **Why can cross-entropy loss be computed with a single reshape?**
  - From the language model's perspective, batch and sequence dimensions don't need separate treatment—only the collection of `(prediction, target)` pairs matters. So `(B, T, vocab_size)` logits become `logits.view(b * t, vocab_size)` and `(B, T)` targets become `targets.view(b * t)`, feeding directly into `F.cross_entropy`.

<!-- toc:begin -->
## In this series

- [LLM from Scratch 101 (1/9): Turning Text into Numbers](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): From Integers to Vectors and Positions](./02-embedding.md)
- [LLM from Scratch 101 (3/9): Deciding Which Tokens to Focus On](./03-attention.md)
- [LLM from Scratch 101 (4/9): The Transformer Block: A Unit of Depth](./04-transformer-block.md)
- **LLM from Scratch 101 (5/9): Assembly: Completing the GPT Model Class (current)**
- LLM from Scratch 101 (6/9): Learning via Gradients (upcoming)
- LLM from Scratch 101 (7/9): Sampling — Generating Text from a Trained Model (upcoming)
- LLM from Scratch 101 (8/9): Adapting the Base Model to Specific Tasks (upcoming)
- LLM from Scratch 101 (9/9): Turning Your LLM into a Chatbot — FastAPI + Streaming (upcoming)

<!-- toc:end -->

## References

- [nanoGPT repository](https://github.com/karpathy/nanoGPT)
- [Using the Output Embedding to Improve Language Models](https://arxiv.org/abs/1608.05859)
- [PyTorch cross_entropy](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
- [Language Models are Unsupervised Multitask Learners (GPT-2)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)

Tags: LLM, PyTorch, Transformer, Tutorial

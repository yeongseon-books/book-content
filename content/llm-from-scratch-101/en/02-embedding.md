---
title: "LLM from Scratch 101 (2/9): From Integers to Vectors and Positions"
series: llm-from-scratch-101
episode: 2
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
seo_description: After finishing the tokenizer, you might feel like you're done. You
  have numbers as input, so everything should be fine, right?
---

# LLM from Scratch 101 (2/9): From Integers to Vectors and Positions

> LLM from Scratch 101 series (2/9)

After finishing the tokenizer, you might feel like you're done. You have numbers as input, so everything should be fine, right? Actually, we've barely started. To a neural network, an ID array like `[12, 4, 38, 2]` is just a list of indices. There's no inherent reason for 12 to be closer to 13, and there's no connection to Shakespeare's writing style yet.

When I first learned about embeddings, thinking of them as a "lookup table" was much more helpful than abstract definitions like "high-dimensional spaces of word meanings." Once you understand how to pull a single row, adding positional information becomes a natural next step.

Today, we're starting `model.py`. We won't build the Transformer blocks yet, but we'll create the entrance that converts token IDs into `(B, T, C)` tensors. It's a small step, but it's the first gate every GPT model must pass through.

Today's mental model is this: **The input vector for a token is the sum of its token embedding and its positional embedding.**

This is the 2nd post in the LLM from Scratch 101 series.

---

![LLM from Scratch 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/02/02-01-sinusoidal-vs-learned-positional-embeddi.en.png)
*LLM from Scratch 101 chapter 2 flow overview*

## Questions to Keep in Mind

- What operation does nn.Embedding actually perform?
- Why isn't token embedding alone enough?
- How do sinusoidal and learned positional embeddings differ?

## nn.Embedding is Just a Lookup Table

`nn.Embedding(vocab_size, n_embd)` is essentially a large table with dimensions `(vocab_size, n_embd)`. When a token ID comes in, it simply pulls the corresponding row. That's it. It might look complex through the lens of linear algebra, but the operation itself is just indexing.

The key is that the values in this table are learned. They start as random numbers, but after thousands of backpropagation steps, tokens appearing in similar contexts start moving in similar directions. The meaning isn't in the integer ID, but in the learned vector row.

This perspective explains why we don't bother with one-hot vectors. One-hot encoding explodes in dimensionality with vocabulary size and is mostly zeros. An embedding table is a mechanism to compress that massive sparse representation into small, dense vectors. It saves computation and allows similar tokens to become geometric neighbors as training progresses.

## Building it from Scratch — Embedding in 5 Lines

If `nn.Embedding` feels like a black box, you can implement it yourself quite easily:

```python
import torch
import torch.nn as nn

class MiniEmbedding(nn.Module):
    def __init__(self, vocab_size: int, n_embd: int) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.randn(vocab_size, n_embd) * 0.02)

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        return self.weight[idx]

idx = torch.tensor([[0, 1, 2], [2, 1, 0]])
emb = MiniEmbedding(vocab_size=4, n_embd=3)
print(emb(idx).shape)
```

If this code prints `(2, 3, 3)`, you've grasped the core concept. It means you have a batch size of 2, 3 tokens per sequence, and an embedding dimension of 3.

## What About the Order?

The problem is sequence order. While attention will later calculate relationships between tokens, the input stage itself has no way to distinguish between an `a` at position 1 and an `a` at position 10. If we treat the `To` at the start of a Shakespearean sentence the same as the `to` at the end, we lose the sense of progression.

This is why we use positional embeddings. We're effectively separating the learning of what a token is from where it's located.

This separation is quite useful in practice. Token meanings are reused across the entire dataset, but the sense of position changes with context length. Splitting these into separate tables keeps the design simple and makes debugging easier. If something goes wrong, you can often tell which side is at fault just by looking at the tensor shapes.

## Sinusoidal vs. Learned Positional Embedding

The original Transformer paper used sine and cosine functions for positional encoding. Calculating coordinates with functions allows for easier generalization to different sequence lengths. However, many GPT-style models use learned positional embeddings, which is what we'll use in this series. It's concise and easier to visualize in smaller models.

The structure simply carries both "what character" and "which position" information within a single token vector.

## Token Vector = token_emb + pos_emb

Let's set up the skeleton for `model.py`. For now, it only includes the embeddings.

```python
from dataclasses import dataclass

import torch
import torch.nn as nn

@dataclass
class GPTConfig:
    vocab_size: int = 65
    block_size: int = 64
    n_layer: int = 6
    n_head: int = 4
    n_embd: int = 128

class GPT(nn.Module):
    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        self.config = config
        self.token_embedding_table = nn.Embedding(config.vocab_size, config.n_embd)
        self.position_embedding_table = nn.Embedding(config.block_size, config.n_embd)

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        b, t = idx.shape
        pos = torch.arange(t, device=idx.device)
        tok_emb = self.token_embedding_table(idx)
        pos_emb = self.position_embedding_table(pos)
        x = tok_emb + pos_emb
        return x

config = GPTConfig()
model = GPT(config)
idx = torch.randint(0, config.vocab_size, (4, 8))
print(model(idx).shape)
```

An output shape of `(4, 8, 128)` is what we're looking for. We don't have logits or loss yet, but the GPT input stage is ready.

Notice the broadcasting here: `tok_emb` is `(B, T, C)` while `pos_emb` is `(T, C)`. PyTorch automatically handles the batch dimension when adding them together. This "shape sense" is crucial for implementing the rest of the blocks later on.

## Creating the First Mini-batch for TinyShakespeare

To see the input tensors, we need a batch function. Reading the `train.bin` file we created earlier as a memory map is the simplest way.

```python
from pathlib import Path

import numpy as np
import torch

def get_batch(split: str, batch_size: int = 4, block_size: int = 8):
    data_path = Path("data") / ("train.bin" if split == "train" else "val.bin")
    data = np.memmap(data_path, dtype=np.uint16, mode="r")
    ix = torch.randint(len(data) - block_size - 1, (batch_size,))
    x = torch.stack([
        torch.from_numpy(np.array(data[int(i) : int(i) + block_size], dtype=np.int64))
        for i in ix
    ])
    y = torch.stack([
        torch.from_numpy(
            np.array(data[int(i) + 1 : int(i) + block_size + 1], dtype=np.int64)
        )
        for i in ix
    ])
    return x, y

x, y = get_batch("train")
print(x.shape, y.shape)
print(x[0])
print(y[0])
```

Now the model is ready to receive `(B, T)` inputs, and we can pull batches of data. In the next step, the tokens will finally start "seeing" each other.

For those new to this, it's worth noting why we need both `x` and `y`. `x` is the current context, and `y` is the target (the same data shifted one position to the right). The model learns to predict the next character at every position in `x`. this one-position shift is the fundamental rhythm of language model training.

## What's next

In the next post, we'll move on to Attention. We'll enable each token to score and decide how much it should focus on other tokens in the sequence. This is where `Q`, `K`, and `V` finally make their appearance.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Reimplemented nn.Embedding as a lookup in 5 lines.
- [ ] Built the first TinyShakespeare mini-batch and printed embedding shapes.
- [ ] Compared the output of sinusoidal vs learned positional embedding.
- [ ] Can explain what token_emb + pos_emb represents.

<!-- a-grade-example:end -->

## Common misconceptions

- It is tempting to think embeddings already carry meaning like a dictionary, but initially they are just random parameters—meaning forms through training.
- It feels like token embeddings alone should suffice, but without positional information you cannot recover order.
- `nn.Embedding` looks like a complex layer, but its implementation essence is parameter-table indexing.
- Sinusoidal seems more theoretical, so learned positional embedding is assumed inferior—but the GPT family widely uses the learned variant.
- It is easy to miss why `x` and `y` are separate tensors, but in next-token prediction the one-position shift is the core contract.

## Operations checklist

- [ ] I can explain how `(B, T)` input becomes a `(B, T, C)` embedding tensor in terms of shapes.
- [ ] I can summarize in one sentence why token embedding and positional embedding are separated.
- [ ] I understand that learned positional embedding's maximum length is tied to `block_size`.
- [ ] I have verified via print output that `x` and `y` in `get_batch()` are in a one-position-shifted relationship.
- [ ] I have traced at the code level that embedding output is the common input to subsequent attention blocks.

## Debugging outputs you must check

The embedding stage has short code and is easy to skip, but mishandling shape or index range here silently breaks all subsequent training. Early on, it is safest to log `x.min()`, `x.max()`, `x.dtype`, `tok_emb.shape`, `pos_emb.shape`.

In particular, a state like `x.max() >= vocab_size` must be treated as an immediate failure. Adding this guard early saves enormous time tracking mysterious `nan` values in the attention stage.

## Practical pattern: leaving tensor shape annotations in code

The embedding stage is short, tempting you to skip verification, but real bugs start silently here. The most practical defense is **leaving shape annotations right beside the code and verifying with asserts on every forward pass**.

```python
def forward(self, idx: torch.Tensor) -> torch.Tensor:
    # idx: (B, T)
    b, t = idx.shape
    assert t <= self.config.block_size, "sequence too long"

    pos = torch.arange(t, device=idx.device)           # (T,)
    tok_emb = self.token_embedding_table(idx)          # (B, T, C)
    pos_emb = self.position_embedding_table(pos)       # (T, C)
    x = tok_emb + pos_emb                              # (B, T, C)

    assert x.shape == (b, t, self.config.n_embd)
    return x
```

This habit is especially powerful in collaboration. Because the shape agreement lives in code rather than docs, subsequent editors who mishandle `transpose` axes or `view` dimensions are caught immediately. For small models, these basic guards reduce debugging time dramatically.

### Calculate embedding memory usage upfront to simplify configuration

Embeddings tend to consume memory before computation. So estimating cost from `vocab_size`, `n_embd`, and `dtype` alone accelerates experiment design.

```python
def embedding_memory_bytes(vocab_size: int, n_embd: int, bytes_per_param: int = 4) -> int:
    return vocab_size * n_embd * bytes_per_param

for vocab, emb in [(65, 128), (8000, 256), (50000, 768)]:
    mb = embedding_memory_bytes(vocab, emb) / (1024**2)
    print(f"vocab={vocab:>6}, n_embd={emb:>4} -> {mb:7.2f} MB")
```

Example output:

```text
vocab=    65, n_embd= 128 ->    0.03 MB
vocab=  8000, n_embd= 256 ->    7.81 MB
vocab= 50000, n_embd= 768 ->  146.48 MB
```

The takeaway is immediate: char-level has such a small vocab that embedding cost is negligible. Conversely, large subword vocabs make the embedding table a significant memory chunk. Tokenizer choice and embedding dimension choice must always be considered together.

### Positional embedding method comparison table

| Method | Advantage | Limitation | This series |
| --- | --- | --- | --- |
| learned | simple implementation, high GPT-family alignment | weak generalization beyond `block_size` | used |
| sinusoidal | intuitive length generalization | implementation/interpretation disconnect | not used |
| rotary (RoPE) | strong long-context performance cases | higher implementation complexity | not used |

At the introductory stage, learned positional embedding has the highest explainability. However, remember that once you start extending context length in practice, positional representation must be revisited.

### Mini-probe for quick embedding quality checks

Early in training, vector meanings are nearly random, but after a few thousand steps, distances between tokens sharing similar contexts shrink slightly. A simple cosine similarity probe confirms this.

```python
import torch.nn.functional as F

def cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    return float(F.cosine_similarity(a[None], b[None]).item())

e = model.token_embedding_table.weight.detach()
id_space = stoi.get(" ")
id_e = stoi.get("e")
id_t = stoi.get("t")

print("cos(space, e)=", cosine(e[id_space], e[id_e]))
print("cos(e, t)=", cosine(e[id_e], e[id_t]))
```

The numbers themselves are not ground truth, but tracking before/after changes gives you a feel for whether embedding is actually learning. Watching representation-space changes alongside the loss curve reads model state more three-dimensionally.

## Implementation details often missed in the embedding layer

Embedding looks like a simple lookup on the surface, but several hidden decisions affect model quality and training stability. When building a small GPT from scratch, the following items govern "correctness" before performance.

### Padding token strategy

Batching sentences of different lengths requires padding. You must decide whether to train or freeze the padding token embedding. In small experiments the difference seems negligible, but when eval data length distributions differ, generation quality is affected. Typically, masking padding positions out of loss and minimizing embedding changes is the safe default.

### Positional embedding range and context extension

When increasing `block_size` from 256 to 512, it is tempting to think only the positional embedding table size needs to grow. But training data length distribution, batch memory, and learning rate schedule must all be co-adjusted for real gains. If instability grows after extending context, check warmup length and gradient clipping thresholds first.

### Dropout placement semantics

Dropout right after embedding summation reduces over-fitting of token representations. But too much slows early training; too little strengthens memorization on small datasets. On TinyShakespeare-like environments, rather than large dropout changes, fine-tune while watching eval loss trends.

### Weight initialization and scale intuition

If embedding vector initial variance is too large, the first attention computation becomes unstable; too small and signals are weak. When implementing from scratch, explicitly state initialization policy in code and build the habit of watching loss curves and gradient norms together for the first few hundred steps.

## Simple diagnostics for embedding quality

To see whether embeddings are forming properly in early-to-mid training, basic statistics beat complex analysis. Periodically record token embedding norm distribution, positional embedding norm distribution, and cosine similarity between a few key tokens. If the distribution collapses sharply or specific tokens grow disproportionately, suspect learning rate, initialization, or dropout settings first.

Even a small diagnostic routine turns the feeling of "the model looks off" into numbers, enabling faster decisions.

## Practice notes

When problems arise at the embedding stage, the instinct is to suspect the entire model, but the actual cause is often a mismatch in input length policy and masking. Check batch composition and masking first, then adjust learning rate—this order speeds up resolution.

Also, positional embedding extension experiments are more stable when done incrementally (256→384→512) rather than jumping in one step.

## Frequently asked questions in practice

### Should I follow this discipline even for small models?

Yes—in fact, smaller models require stricter adherence to basic contracts. The smaller the model capacity, the more it is affected by input noise and implementation mismatches. Securing reproducible experiment units first improves quality improvement velocity even before scaling model size.

### What do I do when experiment speed and quality control conflict?

To increase speed, the goal is not more experiments but lower failure cost. Introducing config file pinning, log standardization, and checkpoint metadata storage first lets you run more "valid" experiments in the same time.

### What's the single most useful thing to record?

Record the reason for the change, expected effect, and actual observed result briefly. Especially recording "why this value was chosen" lets you reconstruct decision context even weeks later.

## Summary

This article covered the embedding stage that transforms token IDs into meaningful vector representations, and the positional embedding stage that preserves order. The key insight is understanding `nn.Embedding` as a learnable lookup table rather than an abstract concept.

We also confirmed that the GPT input stage ultimately stands on the concise structure `token_emb + pos_emb`. Only with this single line can subsequent attention compute inter-token relationships and the model begin handling context that includes order.

In the next article, these vectors will start seeing each other. That is, attention and the QKV structure—where each token decides how much to reference other tokens—will appear in full.

## Answering the Opening Questions

- **What operation does `nn.Embedding` actually perform?**
  - `nn.Embedding(vocab_size, n_embd)` is less a complex calculator and more a learnable lookup that pulls the corresponding row from a `(vocab_size, n_embd)` table. The single line `return self.weight[idx]` in the article's `MiniEmbedding` showed that essence.
- **Why is token embedding alone insufficient?**
  - With only token embeddings, the same character looks identical whether it's at position 0 or position T—order is lost. That's why the GPT input stage builds `tok_emb + pos_emb`; only with that addition does the `(B, T, C)` tensor carry both token meaning and position.
- **Why is it practical to handle positional information as a separate embedding?**
  - Token meaning is reused across the entire vocab while position varies only within `block_size`, so separating the two into distinct tables simplifies implementation and debugging. The article's `position_embedding_table = nn.Embedding(config.block_size, config.n_embd)` managed learned positional embeddings separately for exactly this reason.

<!-- toc:begin -->
## In this series

- [LLM from Scratch 101 (1/9): Turning Text into Numbers](./01-tokenizer.md)
- **LLM from Scratch 101 (2/9): From Integers to Vectors and Positions (current)**
- LLM from Scratch 101 (3/9): Deciding Which Tokens to Focus On (upcoming)
- LLM from Scratch 101 (4/9): The Transformer Block: A Unit of Depth (upcoming)
- LLM from Scratch 101 (5/9): Assembly: Completing the GPT Model Class (upcoming)
- LLM from Scratch 101 (6/9): Learning via Gradients (upcoming)
- LLM from Scratch 101 (7/9): Sampling — Generating Text from a Trained Model (upcoming)
- LLM from Scratch 101 (8/9): Adapting the Base Model to Specific Tasks (upcoming)
- LLM from Scratch 101 (9/9): Turning Your LLM into a Chatbot — FastAPI + Streaming (upcoming)

<!-- toc:end -->

## References

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Let's build GPT: from scratch, in code, spelled out.](https://www.youtube.com/watch?v=kCc8FmEb1nY)
- [PyTorch nn.Embedding](https://pytorch.org/docs/stable/generated/torch.nn.Embedding.html)

Tags: LLM, PyTorch, Transformer, Tutorial

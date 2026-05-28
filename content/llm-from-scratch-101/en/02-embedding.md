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

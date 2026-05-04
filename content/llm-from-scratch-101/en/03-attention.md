---
title: Deciding Which Tokens to Focus On
series: llm-from-scratch-101
episode: 3
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- PyTorch
- Transformer
- Tutorial
last_reviewed: '2026-04-29'
seo_description: Humans don't read every word in a sentence with the same intensity.
  When you read "He threw it," your eyes instinctively scan back to earlier words…
---

# Deciding Which Tokens to Focus On

> LLM from Scratch 101 series (3/9)

Humans don't read every word in a sentence with the same intensity. When you read "He threw it," your eyes instinctively scan back to earlier words to figure out what "it" refers to. You're momentarily assigning different weights to the subject and the object. Transformer attention works in a very similar way.

When I first implemented attention, the acronym `QKV` was the most confusing part. The naming makes it feel more complex than it is. In reality, you're just applying three linear layers to the same input tensor, followed by score calculation, masking, softmax, and a weighted sum.

Today, we're adding `CausalSelfAttention` to `model.py`. We'll skip shortcuts like `einsum` for now and stick with `nn.Linear` and `reshape`. In these first three posts, traceability is more important than elegance.

Today's mental model is this: **Each token asks a question with its Query, provides a score with its Key, and pulls the information it needs from the Value.**

---

<!-- a-grade-intro:begin -->

## Key Questions

- Why do Q, K, V come from the same input but play different roles?
- Why divide attention scores by sqrt(d)?
- What breaks during training without the causal mask?
- Why does multi-head have more capacity than a single head?

<!-- a-grade-intro:end -->

## QKV are Just Three Linear Transformations

If the input `x` is `(B, T, C)`, attention creates three projections: `q = Wq x`, `k = Wk x`, and `v = Wv x`. All three come from the same source, but they serve different roles. The Query asks "What am I looking for?", the Key says "Here's what I have," and the Value provides the "actual content to be retrieved."

Despite the grand names, the implementation is just three linear layers.

## Calculating Scores: Q · K^T / sqrt(d)

To determine how much one token should focus on another, we need a score. We get this by taking the dot product of the Query and the Key. A higher value means a better match. Since the dot product grows with the number of dimensions, we divide by `sqrt(d)` to keep the variance under control.

Visualizing a 4×4 matrix makes this clear. For a sequence of length 4, the score matrix is 4×4. Each row represents "which tokens the current token is attending to."

Without scaling, the softmax can become extremely sharp early in training. If only a few entries approach 1 while the rest are suppressed to 0, gradients tend to vanish. The `sqrt(d)` isn't just a mathematical flourish; it's essential for training stability.

## Causal Mask — No Peeking at the Future

A language model is essentially a next-token predictor. The current position shouldn't be allowed to see the future answer. We enforce this by masking the upper triangular part of the score matrix, setting future values to `-inf`.

![Causal mask blocking future-token attention](../../../assets/llm-from-scratch-101/03/03-01-causal-mask-no-peeking-at-the-future.en.png)

*Causal mask blocking future-token attention*
This single line is the core discipline of an autoregressive model. It prevents the model from "cheating" by looking at future lines while it's still learning to predict the next character in Shakespeare.

## Softmax → V Weighted Sum → Output

A single-head attention mechanism can be implemented with just a few lines of code:

```python
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

class SingleHeadAttention(nn.Module):
    def __init__(self, n_embd: int, head_size: int, block_size: int) -> None:
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer("tril", torch.tril(torch.ones(block_size, block_size)))

    def forward(self, x: torch.Tensor):
        _, t, c = x.shape
        k = self.key(x)
        q = self.query(x)
        wei = q @ k.transpose(-2, -1) / math.sqrt(k.size(-1))
        wei = wei.masked_fill(self.tril[:t, :t] == 0, float("-inf"))
        wei = F.softmax(wei, dim=-1)
        v = self.value(x)
        out = wei @ v
        return out, wei

x = torch.randn(2, 4, 8)
head = SingleHeadAttention(n_embd=8, head_size=8, block_size=8)
out, wei = head(x)
print(out.shape)
print(wei[0])
```

The output is `(B, T, head_size)`, and `wei` shows us exactly where each token was looking. I always print this weight matrix during debugging to verify the attention patterns.

## Multi-head: Multiple Perspectives Simultaneously

Using a single head limits the model to one type of relationship. Multi-head attention splits the embedding dimension into several pieces, allowing each piece to score relationships from a different perspective. One head might focus on local context, while another might be sensitive to matching parentheses or changes in speaker.

Finally, we concatenate the outputs of all heads and apply a single projection to return to the original dimension. In our configuration (`n_embd=128`, `n_head=4`), each head will have 32 dimensions.

Increasing the number of heads doesn't automatically make a model smarter. Within the same `n_embd`, more heads mean fewer dimensions per head. In small models, you're trading representational depth for parallel perspectives. For a 101 series, 4 heads provide a good balance for observing the structure.

## Using nn.Linear and Reshape Without einsum

Now let's integrate `CausalSelfAttention` for our series. It might look like a lot of code, but the structure is exactly what we just discussed.

```python
from dataclasses import dataclass
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

@dataclass
class GPTConfig:
    vocab_size: int = 65
    block_size: int = 64
    n_layer: int = 6
    n_head: int = 4
    n_embd: int = 128

class CausalSelfAttention(nn.Module):
    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        assert config.n_embd % config.n_head == 0
        self.n_head = config.n_head
        self.head_size = config.n_embd // config.n_head
        self.key = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.query = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.value = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.proj = nn.Linear(config.n_embd, config.n_embd)
        self.register_buffer(
            "tril", torch.tril(torch.ones(config.block_size, config.block_size))
        )

    def forward(self, x: torch.Tensor):
        b, t, c = x.shape
        k = self.key(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)
        q = self.query(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)
        v = self.value(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)

        wei = q @ k.transpose(-2, -1) / math.sqrt(self.head_size)
        wei = wei.masked_fill(self.tril[:t, :t] == 0, float("-inf"))
        wei = F.softmax(wei, dim=-1)

        out = wei @ v
        out = out.transpose(1, 2).contiguous().view(b, t, c)
        out = self.proj(out)
        self.last_attn = wei
        return out

config = GPTConfig()
attn = CausalSelfAttention(config)
x = torch.randn(2, 8, config.n_embd)
out = attn(x)
print(out.shape)
print(attn.last_attn.shape)
```

The output shape is `(2, 8, 128)`. If you want to inspect the attention map, you can read `attn.last_attn`, whose shape is `(2, 4, 8, 8)` in this example.

## Checking a Single Head's Output

You can verify the causal mask by looking at the weights directly. The first row should only show the first token attending to itself, and the second row should only show attention to the first two positions. If the upper right area is blocked with zeros, the implementation is correct.

Skipping this verification makes it much harder to find errors when you start stacking blocks. Half of attention debugging is simply confirming shapes and masks.

When training behaves unexpectedly, the cause is often a minor tensor manipulation error rather than a deep mathematical flaw. It's usually a swapped transpose axis, a mask that doesn't match the `block_size`, or a missing `contiguous()` after a reshape. In attention, precision in handling tensor shapes is more important than the conceptual understanding.

## What's next

Now that our tokens can "see" each other, we'll move on to the next post. We'll add FeedForward, Residual connections, and LayerNorm to complete a full Transformer block—the fundamental unit of depth in our model.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Walked through the scale → softmax → weighted V flow by hand.
- [ ] Printed a single head's attention weights to see the pattern.
- [ ] Understood how multi-head outputs are reshaped and concatenated.
- [ ] Compared logits before and after mask application.

<!-- a-grade-example:end -->

<!-- toc:begin -->
## In this series

- [Turning Text into Numbers](./01-tokenizer.md)
- [From Integers to Vectors and Positions](./02-embedding.md)
- **Deciding Which Tokens to Focus On (current)**
- The Transformer Block: A Unit of Depth (upcoming)
- Assembly: Completing the GPT Model Class (upcoming)
- Learning via Gradients (upcoming)
- Sampling — Generating Text from a Trained Model (upcoming)
- Adapting the Base Model to Specific Tasks (upcoming)
- Turning Your LLM into a Chatbot — FastAPI + Streaming (upcoming)

<!-- toc:end -->

## References

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [nanoGPT model.py](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [PyTorch scaled_dot_product_attention](https://pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)

Tags: LLM, PyTorch, Transformer, Tutorial

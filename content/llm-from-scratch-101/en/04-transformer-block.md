---
title: "LLM from Scratch 101 (4/9): The Transformer Block: A Unit of Depth"
series: llm-from-scratch-101
episode: 4
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
seo_description: Implementing CausalSelfAttention provides a momentary sense of relief.
  Tokens can finally look at each other, and you've verified the weight matrices.
---

# LLM from Scratch 101 (4/9): The Transformer Block: A Unit of Depth

> LLM from Scratch 101 series (4/9)

Implementing `CausalSelfAttention` provides a momentary sense of relief. Tokens can finally look at each other, and you've verified the weight matrices. However, stacking these blocks reveals immediate limitations. While tokens can share information, the model still lacks the capacity to process those representations non-linearly within each position.

When I first implemented Transformer, this was the point where the architecture became crystal clear. Attention serves as the communication line between tokens, while the FeedForward network acts as a small, localized transformer for each token. Binding them together with residual connections makes it feel like a true unit of depth.

In GPT models, these blocks often seem like standard components. Writing them by hand makes their purpose obvious. For effective training, you must ensure that information can both flow through the transformations and survive via the original input path.

The mental model for today is simple: **Attention mixes information across tokens, FeedForward transforms it within each token, and Residual connections wrap them both for stability.**

This is the 4th post in the LLM from Scratch 101 series.

---

![LLM from Scratch 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/04/04-01-layernorm-pre-norm-vs-post-norm.en.png)
*LLM from Scratch 101 chapter 4 flow overview*

## Questions to Keep in Mind

- Why is a 2-layer MLP enough for FeedForward?
- How do residual connections rescue training?
- What's the practical difference between pre-norm and post-norm?

## FeedForward is Just a 2-layer MLP

Stacking only attention layers allows tokens to reference each other extensively, but the representational power doesn't grow as expected. Each position lacks sufficient non-linear transformation. To fix this, we add an MLP with the structure `Linear(C, 4C) -> GELU -> Linear(4C, C)` to every block.

Expanding the intermediate dimension by four is a practical choice. This brief expansion allows the token to form richer combinations before projecting back to the original dimension in the final linear layer. Even in small models, the FeedForward network handles a significant portion of the heavy lifting.

```python
import torch
import torch.nn as nn

class FeedForward(nn.Module):
    def __init__(self, n_embd: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
```

## Residual Connections — Skip Connections Save Training

As models grow deeper, original input information tends to fade. Residual connections in the form `x = x + f(x)` mitigate this issue. In the early stages of training, when transformations are still crude, the model can at least pass the raw input to the next layer. This also ensures a clear path for gradients during backpropagation.

If you had to reduce the reason why deep models actually work into a single word, it would likely be residuals. I view this structure as a way for the model to add what it just learned without discarding existing representations. It also helps during debugging, as even if a block is poorly initialized, the input doesn't evaporate completely.

## LayerNorm — Pre-norm vs Post-norm

The original Transformer placed LayerNorm after the sub-layers, known as Post-norm. Since GPT-2, Pre-norm—placing it before the sub-layers—has become the standard. It provides much better stability during training as depth increases.

We will use Pre-norm for this series. We normalize the input first, pass it through Attention and FeedForward, and then add the residual. It might look like a single-line change in code, but the training stability feels quite different.

## Implementing a Single Block in PyTorch — 25 Lines

Now we add the block to `model.py`. Using the `CausalSelfAttention` from the previous post, we combine it with the `FeedForward` and two `LayerNorm` layers.

```python
import torch
import torch.nn as nn

class Block(nn.Module):
    def __init__(self, config) -> None:
        super().__init__()
        self.ln1 = nn.LayerNorm(config.n_embd)
        self.attn = CausalSelfAttention(config)
        self.ln2 = nn.LayerNorm(config.n_embd)
        self.ffn = FeedForward(config.n_embd)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln1(x))
        x = x + self.ffn(self.ln2(x))
        return x
```

The logic is straightforward: normalize, run attention, and add to the original. Normalize again, run the MLP, and add again. Because `CausalSelfAttention.forward()` now returns only the residual-stream tensor, the residual addition stays shape-consistent all the way through.

## Stacking Blocks N Times

Transformer depth doesn't come from complex new parts but from repeating the same block. Implementation is as simple as using `nn.ModuleList`.

```python
self.blocks = nn.ModuleList([Block(config) for _ in range(config.n_layer)])

for block in self.blocks:
    x = block(x)
```

As these repetitions stack, early blocks refine local context while later blocks organize longer context relationships. Even with a small char-level model, stacking a few layers makes it act like a context-aware model rather than just a single-character predictor.

## Parameter Counting — Where the Weights Go

You can quickly estimate the cost of a single block. Attention consists of `Q`, `K`, `V`, and output projection, totaling roughly `4C²`. FeedForward is `C -> 4C -> C`, which is about `8C²`. The numbers show that the FeedForward network is twice as large.

With our setting of `C=128`, one block uses about 66k parameters for attention and 131k for FeedForward. Adding two LayerNorms brings the total for one block to roughly 198k. Six layers mean about 1.18M parameters are concentrated in the blocks. Working with a small GPT makes you realize that the FeedForward layers consume most of the model's capacity.

## What's next

The building blocks are ready. In the next post, we will wrap embeddings, `N` blocks, the final LayerNorm, and the LM head into a single `GPT(nn.Module)` class. We'll finish the model so it can produce both logits and loss in a single forward pass.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Implemented one block in 25 lines and verified forward shapes.
- [ ] Can draw the pre-norm data flow as a diagram.
- [ ] Calculated how parameters grow when stacking N blocks.
- [ ] Compared the parameter share between FeedForward and attention.

<!-- a-grade-example:end -->

## Common misconceptions

- It is tempting to think attention alone completes the Transformer, but without FFN, per-position nonlinear transformation is weak.
- Residual connections look like a convenience feature, but they are the core structure that makes deep model training viable.
- LayerNorm placement seems like a minor style choice, but pre-norm and post-norm differ significantly in training stability.
- Stacking more blocks feels like only attention cost grows, but in reality FFN accounts for a larger parameter share.
- Block repetition feels like complex architecture expansion, but the implementation is just repeating the same `(B, T, C)` transform.

### Debugging tip: test one block in isolation first

Before stacking multiple blocks, the habit of isolating one and checking its input/output is important:

```python
import torch

block = TransformerBlock(n_embd=128, n_head=4, block_size=64)
x = torch.randn(2, 64, 128)
out = block(x)
assert out.shape == x.shape, f"shape mismatch: {out.shape}"
print("block output shape:", out.shape)
```

Confirming output shape matches input `(B, T, C)` verifies residual paths and LayerNorm are properly connected in one shot. If shapes differ, check FFN output dimensions or projection matrix sizes first.

## Operations checklist

- [ ] I can explain the responsibility difference between attention and FFN in one sentence each.
- [ ] I can draw the pre-norm residual flow as a diagram.
- [ ] I have confirmed block input and output shapes always stay `(B, T, C)`.
- [ ] I can roughly calculate parameter increase when increasing `n_layer`.
- [ ] I understand that FFN holds a larger parameter share than attention.

## Block-level performance checkpoints

When Transformer training is slow or unstable, examining block by block is more effective than looking at the entire model at once. Checking these three items first quickly narrows the cause.

### Activation range

If each block output's mean and variance grow or shrink dramatically as layers deepen, suspect learning rate, initialization, or LayerNorm behavior. Even pre-norm structures can exhibit drift under certain settings.

### Attention distribution

If attention probabilities concentrate excessively on one token in some heads, or spread nearly uniformly, context utilization may be inefficient. Check head count, block size, and dropout together.

### FFN contribution

If the FFN path's contribution to block output change is too small, nonlinear transformation weakens; too large and it overwhelms the residual path. In practice, splitting gradient norm observation between attention/FFN makes balance easy to read.

These checks are not just for large models. The same principles operate in small educational GPTs, so building block-level instrumentation habits early improves debugging intuition when scaling later.

## Architecture comparison: Transformer block vs simple RNN stack

To see the Transformer block's necessity more clearly, compare it against RNN-family architectures for the same character model. The goal is not concluding which is absolutely superior but confirming **why this series chose the block-repetition structure**.

| Item | Simple RNN/LSTM stack | Transformer block |
| --- | --- | --- |
| Context combination | sequential update | parallel cross-reference across all positions (attention) |
| Long-dependency handling | path length grows | path length relatively short |
| Parallelization | low | high |
| Implementation debugging points | hidden state passing | shape/mask/projection |
| Series suitability | can explain principles | connects directly to modern LLM architecture |

For char-level toy problems, both work. But using Transformer blocks provides structural continuity with real GPT-family code, maximizing learning transfer.

### Mini hook for instrumenting tensor paths inside a block

Observing residual paths and sub-layer outputs together makes it easy to read "which path contributes more."

```python
def block_probe(block: Block, x: torch.Tensor) -> None:
    with torch.no_grad():
        h1 = block.ln1(x)
        a = block.attn(h1)
        x1 = x + a
        h2 = block.ln2(x1)
        f = block.ffn(h2)
        x2 = x1 + f

    print("attn_delta_norm:", float(a.norm().item()))
    print("ffn_delta_norm :", float(f.norm().item()))
    print("out_norm       :", float(x2.norm().item()))
```

These values are not ground truth, but watching changes across early/mid/late training builds intuition for how blocks update representations. If `ffn_delta_norm` is pinned near 0 at a certain stage, that's evidence the FFN path may be dead.

### Pre-norm vs Post-norm experiment log example

Changing only the structure while keeping the same hyperparameters reveals stability differences numerically:

```text
[pre-norm]
step 0    loss 4.17
step 500  loss 2.26
step 1500 loss 1.84

[post-norm]
step 0    loss 4.16
step 500  loss 2.49
step 1500 loss 2.31 (intermittent spikes)
```

This tendency is often observed even in small models. That's why pre-norm has become the de facto default in GPT-family production implementations.

### Principles to fix first when increasing block repetitions

Experimenting with more blocks is tempting but simultaneously makes comparisons harder. Fixing the items below first makes result interpretation easier:

- Fix `tokenizer`, `vocab_size`, `block_size`.
- Keep training step budget identical.
- Log gradient norm alongside train/val loss.
- Keep generation sample prompts identical.

This way you can separate "did depth help, or was it another variable?" As the series progresses, this kind of experiment design habit becomes far more important.

## Training stability issues when increasing block depth

A Transformer block looks simple in isolation, but increasing depth from 2 to 8+ blocks means residual connection and normalization placement differences immediately translate to training stability differences. What matters at this stage is not more complex structures but rules for repeating the same structure stably.

### Why Pre-Norm is preferred

In from-scratch implementations, Pre-Norm structure has relatively stable gradient flow and good reproducibility in small experiments. Post-Norm also works but more frequently shows early training instability, especially with small batches and high learning rate combinations.

### Separating the meaning of the residual path

Residual is both a "preserve the original" path and an "add new transformation" path. So when evaluating block output quality, check whether residual dominates excessively rather than only looking at the transformation path's expressiveness. Simply comparing activation distributions before and after a block reveals scale collapse.

### FeedForward expansion ratio selection

`4 * n_embd` is standard, but small models sometimes need 2x or 3x due to memory and speed constraints. When adjusting, compare not just loss values but also generation text repetitiveness, sentence boundary handling, and long-context maintenance ability.

### Value of per-block checkpointing

Tracking problems in deep models requires more than epoch-level saves. Saving checkpoints with per-block activation statistics at regular step intervals makes it easy to trace back sudden collapses after a specific point. From an operations perspective, the debugging time savings far outweigh storage cost.

## Block-level test checklist

Verifying one block independently before stacking depth significantly reduces later debugging cost:

- Input/output shapes are identical
- No NaN occurs under masking conditions
- Dropout behavior changes between train/eval modes
- Loss trend difference between residual-on and residual-off experiments is reasonable

Blocks that pass this checklist can be repeated with much more predictable model scaling.

## Practice priorities

When improving blocks, stability comes before novel structure experiments. That is, first ensure training converges with similar curves each time, reproduces without NaN, and eval loss doesn't spike. Once this baseline is established, subsequent architecture experiments become easier to interpret.

Ultimately, the core of block design is not flashy variations but creating repeatable depth.

## Frequently asked questions in practice

### Should I follow this discipline even for small models?

Yes—in fact, smaller models require stricter adherence to basic contracts. The smaller the model capacity, the more it is affected by input noise and implementation mismatches. Securing reproducible experiment units first improves quality improvement velocity even before scaling model size.

### What do I do when experiment speed and quality control conflict?

To increase speed, the goal is not more experiments but lower failure cost. Introducing config file pinning, log standardization, and checkpoint metadata storage first lets you run more "valid" experiments in the same time.

### What's the single most useful thing to record?

Record the reason for the change, expected effect, and actual observed result briefly. Especially recording "why this value was chosen" lets you reconstruct decision context even weeks later.

## Conclusion note

The value of block design is not adding complexity but stable repetition. When stacking the same block into multiple layers without training instability, subsequent experiment trust rises and improvement velocity accelerates.

## Summary

This article added FeedForward, residual connections, and LayerNorm on top of attention to complete one Transformer block. This block is a reusable depth unit that bundles inter-token information exchange, per-token internal transformation, and training stability.

We also confirmed that GPT's depth comes not from special new structures but from repeating the same block. And the cost of that repetition is weighted more toward FFN than might be expected.

In the next article, we will assemble all embeddings and blocks built so far into the complete `GPT(nn.Module)` class—a model shell that computes from input through logits and loss in a single forward pass.

## Answering the Opening Questions

- **Why does FeedForward commonly use `Linear(C, 4C) → GELU → Linear(4C, C)`?**
  - After attention mixes inter-token relationships, each position needs an MLP to further enrich its representation internally. `Linear(C, 4C) → GELU → Linear(4C, C)` briefly expands the dimension to create richer combinations, then returns to the residual stream size `C`.
- **How does the residual connection stabilize training?**
  - By keeping the original input path in `x = x + self.attn(self.ln1(x))` and `x = x + self.ffn(self.ln2(x))`, information and gradients don't vanish even in deep layers. Multiple stacked blocks can thus preserve prior representations while making incremental refinements.
- **What practical difference do pre-norm and post-norm make?**
  - The pre-norm used in this series applies `LayerNorm` before each sub-layer, keeping activations and gradients more stable in deep GPT models. It looks like a one-line difference in code, but the design choice of passing through `self.ln1(x)` and `self.ln2(x)` first significantly affects whether training succeeds at all.

<!-- toc:begin -->
## In this series

- [LLM from Scratch 101 (1/9): Turning Text into Numbers](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): From Integers to Vectors and Positions](./02-embedding.md)
- [LLM from Scratch 101 (3/9): Deciding Which Tokens to Focus On](./03-attention.md)
- **LLM from Scratch 101 (4/9): The Transformer Block: A Unit of Depth (current)**
- LLM from Scratch 101 (5/9): Assembly: Completing the GPT Model Class (upcoming)
- LLM from Scratch 101 (6/9): Learning via Gradients (upcoming)
- LLM from Scratch 101 (7/9): Sampling — Generating Text from a Trained Model (upcoming)
- LLM from Scratch 101 (8/9): Adapting the Base Model to Specific Tasks (upcoming)
- LLM from Scratch 101 (9/9): Turning Your LLM into a Chatbot — FastAPI + Streaming (upcoming)

<!-- toc:end -->

## References

- [nanoGPT model.py](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [On Layer Normalization in the Transformer Architecture](https://arxiv.org/abs/2002.04745)
- [Language Models are Unsupervised Multitask Learners (GPT-2)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
- [PyTorch nn.LayerNorm](https://pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html)

Tags: LLM, PyTorch, Transformer, Tutorial

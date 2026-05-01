---
title: 'Introduction to LLM Fine-tuning'
series: llm-finetuning-101
episode: 1
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Fine-tuning
- LoRA
- LLM
- Python
last_reviewed: '2026-05-01'
---

# Introduction to LLM Fine-tuning

## Questions this post answers

- Why is LoRA so much lighter than full fine-tuning?
- How do you separate tasks that need fine-tuning from tasks that only need prompting or RAG?
- What can you verify in Post 01 without loading a real model?

> If full fine-tuning is rebuilding the whole building, LoRA is reinforcing only the beams that carry the new load.

Example code: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/en/01-intro)

The first post in the series starts with arithmetic, not GPUs. Fine-tuning only feels expensive and mysterious when you skip the parameter story. Once you understand how many weights are actually updated, later decisions about datasets, training loops, and serving become much easier to reason about.

The executable example in this article does not load a model at all. Instead, it approximates a GPT-2-small-style transformer shape and computes the parameter count for the linear layers and the LoRA adapters. Running `python main.py` is enough to confirm that the trainable ratio stays around the low single digits.

## What to understand first

The first question in fine-tuning is not which dataset to use. It is **which weights will actually move**. Full fine-tuning updates every parameter and therefore drags optimizer state and memory pressure with it. LoRA freezes the base model and adds small low-rank matrices, so you should always look at the trainable subset separately from the full model size.

![What to understand first](../../../assets/llm-finetuning-101/01/01-01-what-to-understand-first.en.png)
## Minimal runnable example

```python
from dataclasses import dataclass

@dataclass
class TransformerShape:
    hidden_size: int
    intermediate_size: int
    num_layers: int

def total_linear_params(shape: TransformerShape) -> int:
    return shape.num_layers * (
        4 * shape.hidden_size * shape.hidden_size
        + 2 * shape.hidden_size * shape.intermediate_size
    )

def lora_params_per_layer(hidden_size: int, intermediate_size: int, rank: int) -> int:
    attention = 4 * rank * (hidden_size + hidden_size)
    mlp = rank * (hidden_size + intermediate_size) + rank * (intermediate_size + hidden_size)
    return attention + mlp
```

## What to notice in this code

- The example uses `hidden_size=768`, `intermediate_size=3072`, and `num_layers=12` to mimic a GPT-2-small-scale layout.
- The calculation focuses on the linear surfaces that LoRA touches, not on every parameter in the architecture.
- The ratio you get here becomes a useful intuition anchor for Post 03, where `LoraConfig(r=8)` appears in code.

## Where engineers get confused

- LoRA does not shrink the base model itself. It shrinks the trainable slice and the amount of new state you need to store.
- A cheaper training method does not make bad data good. Small adapters can still learn the wrong behavior very efficiently.
- The exact ratio changes by architecture and target modules, so treat this post as a mental model, not a universal constant.

## Checklist

- [ ] I can explain the difference between full model size and trainable parameter count.
- [ ] I understand that LoRA rank scales trainable parameters roughly linearly.
- [ ] I ran `python main.py` and verified the parameter-count example myself.
- [ ] I can connect this ratio back to later posts on adapters and training.

## Summary

Post 01 removes the mystery. Once the parameter story is concrete, LoRA stops looking like magic and starts looking like an engineering trade-off you can defend.

<!-- blog-only:start -->
Next: [Dataset preparation and preprocessing](./02-dataset.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- **Introduction to LLM Fine-tuning (current)**
- Dataset preparation and preprocessing (upcoming)
- Configuring the LoRA adapter (upcoming)
- Training loop and hyperparameters (upcoming)
- Model evaluation (upcoming)
- Model serving (upcoming)

<!-- toc:end -->

---

## References

- [LoRA paper](https://arxiv.org/abs/2106.09685)
- [Hugging Face PEFT documentation](https://huggingface.co/docs/peft)

Tags: Fine-tuning, LoRA, LLM, Python

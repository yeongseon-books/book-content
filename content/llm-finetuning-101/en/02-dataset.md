---
title: 'Dataset preparation and preprocessing'
series: llm-finetuning-101
episode: 2
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

# Dataset preparation and preprocessing

## Questions this post answers

![Flow from raw samples to training batches](../../../assets/llm-finetuning-101/02/02-01-questions-this-post-answers.en.png)
- How should instruction, input, and output fields be structured?
- How do you load a tiny JSONL dataset with Hugging Face datasets?
- Which preprocessing checks matter before you ever start training?

> A good fine-tuning dataset is not a pile of sentences. It is a contract that teaches the model which request shape should produce which answer shape.

Example code: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/en/02-dataset)

At this stage, consistency matters more than volume. If the model cannot tell where the instruction ends and where the answer begins, the training loop can run successfully while teaching the wrong pattern. That is why Post 02 focuses on structuring a tiny dataset clearly before scaling it.

The example script writes a `toy.jsonl` file, reads it with `datasets.load_dataset()`, applies an instruction template, and tokenizes the result with a tiny GPT-2 tokenizer. Running `python main.py` prints the row count, output columns, and token lengths so you can verify the pipeline end to end.

## The three layers of dataset preparation

![Dataset layers and boundary management structure](../../../assets/llm-finetuning-101/02/02-02-the-three-layers-of-dataset-preparation.en.png)
It helps to separate fine-tuning data into three layers: the **raw samples**, the **formatted prompts**, and the **tokenized tensors**. When these layers are explicit, you can debug filtering issues and token-length issues independently instead of mixing them together.

![The three layers of dataset preparation](../../../assets/llm-finetuning-101/02/02-01-the-three-layers-of-dataset-preparation.en.png)
## Minimal runnable example

```python
import json
from pathlib import Path

from datasets import load_dataset
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "toy.jsonl"

with DATA_PATH.open("w", encoding="utf-8") as file:
    file.write(json.dumps({
        "instruction": "Explain two ways to reverse a Python list.",
        "input": "Include a one-line code example.",
        "output": "You can use lst[::-1] or lst.reverse().",
    }) + "\n")

dataset = load_dataset("json", data_files=str(DATA_PATH), split="train")
tokenizer = AutoTokenizer.from_pretrained("sshleifer/tiny-gpt2")
```

## What to notice in this code

![Format validation and token length review flow](../../../assets/llm-finetuning-101/02/02-03-what-to-notice-in-this-code.en.png)
- Using `datasets.load_dataset()` keeps the example close to real JSONL-based workflows.
- Formatting prompts before tokenization makes it much easier to swap in a model-specific chat template later.
- The example fixes `max_length=64` so even a CPU-only run can expose token-length behavior immediately.

## Where engineers get confused

![Deduplication and split decision flow](../../../assets/llm-finetuning-101/02/02-04-where-engineers-get-confused.en.png)
- More rows do not automatically mean better training. Duplicates and inconsistent answer style can hurt a small model very quickly.
- It is normal that this post stops at tokenization. The `labels` field appears in Post 04, where the training loop is introduced.
- The simple length filters here are just a starting point. Production pipelines need checks for duplicates, PII, policy violations, and class balance.

## Checklist

- [ ] I can describe the raw sample schema as instruction, input, and output.
- [ ] I loaded a real JSONL file with `datasets.load_dataset()`.
- [ ] I verified the tokenized columns and prompt lengths after preprocessing.
- [ ] I understand why consistent formatting matters before adapter tuning begins.

## Summary

The key job of dataset preparation is making the input-output boundary unambiguous. Once that boundary is clean, training-loop debugging gets dramatically easier.

<!-- toc:begin -->
## In this series

- [Introduction to LLM Fine-tuning](./01-intro.md)
- **Dataset preparation and preprocessing (current)**
- Configuring the LoRA adapter (upcoming)
- Training loop and hyperparameters (upcoming)
- Model evaluation (upcoming)
- Model serving (upcoming)

<!-- toc:end -->

---

## References

- [Hugging Face Datasets documentation](https://huggingface.co/docs/datasets)
- [Instruction tuning overview](https://arxiv.org/abs/2203.02155)

Tags: Fine-tuning, LoRA, LLM, Python

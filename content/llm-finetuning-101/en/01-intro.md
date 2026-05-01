---
title: 'Introduction to LLM Fine-tuning'
series: llm-finetuning-101
episode: 1
language: en
status: draft
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

> LLM Fine-tuning 101 (1/6)

Example code: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/en/01-intro)

Pre-trained LLMs perform well on general tasks, but show clear limits in specialized domains. A customer support bot needs to use your product's exact terminology. A medical summarization model must follow a specific output format. When prompt engineering and RAG fall short, fine-tuning is the answer. This series walks through the complete process of efficient fine-tuning with LoRA.

---

## What fine-tuning is

Fine-tuning continues training a pre-trained model's weights for a specific task. Two broad approaches exist: full fine-tuning, which updates all weights, and parameter-efficient fine-tuning (PEFT), which freezes most weights and trains only a small adapter.

Full fine-tuning demands enormous GPU memory. A 7B-parameter model in fp32 occupies roughly 28 GB. LoRA and other PEFT methods freeze the original weights and learn a small low-rank adapter, cutting memory requirements by more than 90%.

---

## When fine-tuning makes sense

Try prompt engineering and RAG first. Fine-tune when those approaches don't reach the quality bar.

```python
"""
Fine-tuning is appropriate when:
- Domain-specific vocabulary or strict output format is required
- Hundreds of examples are too many to fit in a prompt
- You want to reduce inference-time context length (cost reduction)
- Consistent output format must be enforced reliably

Fine-tuning is not needed when:
- General question answering (GPT-4 or Claude already handles it)
- Latest information is required (RAG is a better fit)
- Fewer than 100 examples (overfitting risk is high)
"""

def should_finetune(task: dict) -> str:
    if task["examples"] < 100:
        return "Insufficient data — try prompt engineering first"
    if task["needs_latest_info"]:
        return "Use RAG"
    if task["domain_specific"] and task["format_strict"]:
        return "Fine-tuning is a good fit"
    return "Verify whether prompt engineering already meets the bar"
```

---

## Comparing fine-tuning methods

```python
from dataclasses import dataclass

@dataclass
class FinetuningMethod:
    name: str
    trainable_params: str
    memory_requirement: str
    use_case: str

methods = [
    FinetuningMethod(
        name="Full fine-tuning",
        trainable_params="100%",
        memory_requirement="Very high (>80 GB for 7B)",
        use_case="Full domain retraining with ample GPU resources",
    ),
    FinetuningMethod(
        name="LoRA",
        trainable_params="0.1–1%",
        memory_requirement="Low (~8 GB for 7B with 4-bit)",
        use_case="Task specialization on a single consumer GPU",
    ),
    FinetuningMethod(
        name="QLoRA",
        trainable_params="0.1–1%",
        memory_requirement="Very low (~4 GB for 7B)",
        use_case="Consumer GPU, severely memory-constrained environments",
    ),
    FinetuningMethod(
        name="Prompt tuning",
        trainable_params="<0.01%",
        memory_requirement="Minimal",
        use_case="Simple task switching, no inference overhead",
    ),
]

for m in methods:
    print(f"{m.name}: {m.trainable_params} trainable, memory: {m.memory_requirement}")
```

---

## Environment setup

This series uses Hugging Face `transformers`, `peft`, and `datasets`. All examples run on Google Colab with a free T4 GPU.

```python
# pip install transformers peft datasets accelerate bitsandbytes trl

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
```

---

## Loading the base model

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

MODEL_NAME = "microsoft/phi-2"  # 2.7B parameters, fits on a consumer GPU

def load_base_model(model_name: str = MODEL_NAME) -> tuple:
    """Load the base model with 4-bit quantization."""
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    return model, tokenizer

def count_parameters(model) -> dict:
    """Return trainable parameter statistics."""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return {
        "total": f"{total:,}",
        "trainable": f"{trainable:,}",
        "ratio": f"{100 * trainable / total:.2f}%",
    }

if __name__ == "__main__":
    model, tokenizer = load_base_model()
    stats = count_parameters(model)
    print(f"Total parameters: {stats['total']}")
    print(f"Trainable parameters: {stats['trainable']} ({stats['ratio']})")

    # Baseline inference test
    inputs = tokenizer("How do you sort a list in Python?", return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=100, do_sample=False)
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

---

## Series roadmap

Post 1 (this post) establishes the concepts and environment. Post 2 prepares training data. Post 3 configures the LoRA adapter. Post 4 is the training loop. Post 5 covers evaluation. Post 6 covers serving.

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

- [Hugging Face PEFT documentation](https://huggingface.co/docs/peft)
- [LoRA paper: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
- [QLoRA paper](https://arxiv.org/abs/2305.14314)

Tags: Fine-tuning, LoRA, LLM, Python

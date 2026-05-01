---
title: 'Dataset preparation and preprocessing'
series: llm-finetuning-101
episode: 2
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

# Dataset preparation and preprocessing

> LLM Fine-tuning 101 (2/6)

Example code: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/en/02-dataset)

Data quality determines fine-tuning quality. It has more impact on final model performance than model architecture or hyperparameters. This post covers the right data format for fine-tuning, collection strategies, and a preprocessing pipeline.

---

<!-- ebook-only:start -->

**The key idea**: dataset quality determines fine-tuning results. Consistent format and accurate labels matter more than volume.

## Where this chapter fits

This is chapter 2 of 6 in the series.
The previous chapter covered **Introduction to LLM Fine-tuning**.
After this chapter, the next one moves on to **Configuring the LoRA adapter**.
<!-- ebook-only:end -->

## Data format

Fine-tuning data is typically instruction-response pairs. The model learns to produce the desired output for a given input.

```python
from dataclasses import dataclass

@dataclass
class TrainingExample:
    instruction: str  # user question or task description
    input: str        # additional context (optional)
    output: str       # desired response

examples = [
    TrainingExample(
        instruction="Find and fix the bug in the following Python code.",
        input="def add(a, b):\n    return a - b",
        output="Bug: subtraction operator used in an addition function.\n\nFixed:\ndef add(a, b):\n    return a + b",
    ),
    TrainingExample(
        instruction="Write a SQL query.",
        input="Table: users(id, name, age). Return users aged 30 or older, sorted by age descending.",
        output="SELECT id, name, age FROM users WHERE age >= 30 ORDER BY age DESC;",
    ),
]
```

---

## Prompt templates

Each model family has a preferred prompt format. The same template must be used at training time and inference time.

```python
ALPACA_TEMPLATE = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input}

### Response:
{output}"""

ALPACA_NO_INPUT_TEMPLATE = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:
{output}"""

def format_example(example: dict, for_inference: bool = False) -> str:
    """Build a training or inference prompt."""
    has_input = bool(example.get("input", "").strip())
    if has_input:
        prompt = ALPACA_TEMPLATE.format(
            instruction=example["instruction"],
            input=example["input"],
            output="" if for_inference else example["output"],
        )
    else:
        prompt = ALPACA_NO_INPUT_TEMPLATE.format(
            instruction=example["instruction"],
            output="" if for_inference else example["output"],
        )
    return prompt

sample = {"instruction": "Reverse a Python list.", "input": "", "output": "lst[::-1] or lst.reverse()"}
print(format_example(sample))
```

---

## Data collection and cleaning

```python
import json
import re
import statistics
from pathlib import Path
from datasets import Dataset, DatasetDict

def load_jsonl(file_path: str) -> list[dict]:
    """Load a JSONL file."""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def validate_example(example: dict) -> tuple[bool, str]:
    """Check data quality."""
    if not example.get("instruction", "").strip():
        return False, "missing instruction"
    if not example.get("output", "").strip():
        return False, "missing output"
    if len(example["instruction"]) < 10:
        return False, "instruction too short"
    if len(example["output"]) < 5:
        return False, "output too short"
    if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", example["output"]):
        return False, "control characters found"
    return True, "ok"

def clean_example(example: dict) -> dict:
    """Normalize whitespace and strip."""
    return {
        "instruction": example["instruction"].strip(),
        "input": example.get("input", "").strip(),
        "output": example["output"].strip(),
    }

def build_dataset(raw_data: list[dict], tokenizer, max_length: int = 512) -> Dataset:
    """Build a training dataset from raw examples."""
    valid, invalid = [], []
    for ex in raw_data:
        ok, reason = validate_example(ex)
        if ok:
            valid.append(clean_example(ex))
        else:
            invalid.append((ex, reason))

    print(f"Valid: {len(valid)}, Excluded: {len(invalid)}")
    for ex, reason in invalid[:3]:
        print(f"  Excluded ({reason}): {str(ex)[:80]}")

    formatted = [{"text": format_example(ex)} for ex in valid]

    def tokenize_and_filter(batch):
        tokens = tokenizer(batch["text"], truncation=False)
        return {"length": [len(ids) for ids in tokens["input_ids"]]}

    dataset = Dataset.from_list(formatted)
    lengths = dataset.map(tokenize_and_filter, batched=True, batch_size=64)
    dataset = dataset.filter(
        lambda ex, idx: lengths[idx]["length"] <= max_length, with_indices=True
    )
    print(f"After max-length filter ({max_length} tokens): {len(dataset)} examples")
    return dataset
```

---

## Train/validation split and saving

```python
def split_and_save(dataset: Dataset, output_dir: str, val_ratio: float = 0.1) -> DatasetDict:
    """Split into train/validation and save to disk."""
    split = dataset.train_test_split(test_size=val_ratio, seed=42)
    dataset_dict = DatasetDict({"train": split["train"], "validation": split["test"]})

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    dataset_dict.save_to_disk(output_dir)

    print(f"Train: {len(dataset_dict['train'])}")
    print(f"Validation: {len(dataset_dict['validation'])}")
    print(f"Saved to: {output_dir}")
    return dataset_dict

def analyze_dataset(dataset: Dataset, tokenizer) -> dict:
    """Compute token-length statistics."""
    lengths = [len(tokenizer.encode(t)) for t in dataset["text"]]
    return {
        "count": len(lengths),
        "token_length": {
            "min": min(lengths),
            "max": max(lengths),
            "mean": round(statistics.mean(lengths), 1),
            "median": statistics.median(lengths),
            "p95": sorted(lengths)[int(len(lengths) * 0.95)],
        },
    }

if __name__ == "__main__":
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2", trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    raw_data = [
        {"instruction": "How do you create a dictionary in Python?", "input": "", "output": "d = {'key': 'value'} or d = dict(key='value')"},
        {"instruction": "Show a list comprehension example.", "input": "", "output": "[x**2 for x in range(10) if x % 2 == 0]"},
    ] * 50

    dataset = build_dataset(raw_data, tokenizer, max_length=256)
    stats = analyze_dataset(dataset, tokenizer)
    print(stats)
    split_and_save(dataset, "./data/finetuning")
```

<!-- blog-only:start -->
Next: [Configuring the LoRA adapter](./03-lora.md)
<!-- blog-only:end -->

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

- [Stanford Alpaca dataset](https://github.com/tatsu-lab/stanford_alpaca)
- [Hugging Face datasets documentation](https://huggingface.co/docs/datasets)
- [LIMA: Less is More for Alignment](https://arxiv.org/abs/2307.09288)

Tags: Fine-tuning, LoRA, LLM, Python

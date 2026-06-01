---
title: "LLM Fine-tuning 101 (2/6): Dataset Preparation and Preprocessing"
series: llm-finetuning-101
episode: 2
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Fine-tuning
- Dataset
- JSONL
- Tokenizer
- HuggingFace
- Python
last_reviewed: '2026-05-01'
seo_description: Learn how to preprocess LLM datasets by breaking them into raw samples, templated text, and tokenized tensors to ensure consistent fine-tuning.
---

# LLM Fine-tuning 101 (2/6): Dataset Preparation and Preprocessing

Dataset work fails less often because of size than because of shape. This article breaks the problem into raw samples, templated text, and tokenized tensors so you can verify each layer before training starts.

This is the second post in the LLM Fine-tuning 101 series.

![LLM Fine-tuning 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/02/02-02-the-three-layers-of-dataset-preparation.en.png)
*LLM Fine-tuning 101 chapter 2 flow overview*

> Dataset work fails on shape, not size — split the data into raw samples, templated text, and tokenized tensors so each layer is verifiable before the loss curve has a chance to lie to you.

## Questions to Keep in Mind

- How should we shape the three fields instruction / input / output?
- How do we read a small JSONL file directly with Hugging Face datasets?
- What minimum verification points must we hit during preprocessing?

## Why this matters

At the dataset stage, what matters most is not volume but **format consistency**. If it is unclear what counts as input and which span the model should learn as a response, the loss may drop while the answers stay blurry. With the same 1,000 samples a consistent prompt format lets LoRA r=8 succeed; a mixed format may not converge even at r=64 with 5× more data.

Nailing the format in post 2 means the same template flows untouched into the training loop (post 4), evaluation (post 5), and serving (post 6). Skim past it and you get the contradictory situation where loss drops in post 4 but answer quality looks broken in post 5.

## Mental model

Treat the dataset as three layers:

```text
┌───────────────────────────────┐
│ Layer 1: Raw samples (JSONL)  │  ← humans read and review here
├───────────────────────────────┤
│ Layer 2: Templated text       │  ← prompt + response as one string
├───────────────────────────────┤
│ Layer 3: Tokenized tensors    │  ← input_ids, attention_mask, labels
└───────────────────────────────┘
```

- **Layer 1** is where humans add, edit, and review. Field names, line breaks, and trailing whitespace must be consistent.
- **Layer 2** is one string per sample, after a model-specific chat template has been applied. Llama-3 and Qwen use different special tokens.
- **Layer 3** is built right before training. The prompt portion of `labels` must be set to -100 so it is excluded from loss.

Separating the three layers lets you diagnose "filtering problems," "token length problems," and "masking problems" independently.

## Core concepts

| Term | Meaning |
| --- | --- |
| Instruction format | `{instruction, input?, output}` shape. Alpaca-style standard |
| Chat format | `[{role, content}, ...]`. Best for multi-turn |
| Completion format | Plain prefix → continuation. Closer to base model pretraining |
| Label masking | Setting prompt tokens to -100 so they do not contribute to loss |
| EOS token | End-of-response signal. Without it the model never learns to stop |

## Before vs. after

**Before** — You collected data, but some rows use `prompt/response`, others `q/a`, others jam everything into a single column. Training runs, but in evaluation answers cut off mid-sentence or repeat the same phrase.

**After** — Every sample passes through the same instruction template and becomes one string:

```text
### Instruction:
Explain two ways to reverse a Python list.

### Input:
Include a one-line example.

### Response:
You can use lst[::-1] or lst.reverse().<eos>
```

The prompt prefix (everything up to `### Response:`) is masked to -100; only the response carries loss. EOS is explicit, so the model also learns when to stop at inference.

## What to fix first about the dataset

Fine-tuning data is usually three layers: **raw samples**, **template-applied text**, and **tokenized tensors**. Separating them is what lets you isolate filtering issues from token-length issues.

![Three layers of dataset preparation](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/02/02-01-the-three-layers-of-dataset-preparation.en.png)

*Three layers of dataset preparation*

## Step-by-step walkthrough

### Step 1 — Author the JSONL source

```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "toy.jsonl"

with DATA_PATH.open("w", encoding="utf-8") as file:
    file.write(json.dumps({
        "instruction": "Explain two ways to reverse a Python list.",
        "input": "Include a one-line example.",
        "output": "You can use lst[::-1] or lst.reverse().",
    }, ensure_ascii=False) + "\n")
```

### Step 2 — Load with datasets

```python
from datasets import load_dataset

dataset = load_dataset("json", data_files=str(DATA_PATH), split="train")
print(dataset.column_names)   # ['instruction', 'input', 'output']
print(len(dataset))           # 1
```

`load_dataset()` builds a cache, so the second load of the same JSONL takes milliseconds.

### Step 3 — Apply the template

```python
TEMPLATE = (
    "### Instruction:\n{instruction}\n\n"
    "### Input:\n{input}\n\n"
    "### Response:\n{output}"
)

def render(example):
    return {"text": TEMPLATE.format(**example)}

dataset = dataset.map(render)
print(dataset[0]["text"][:120])
```

### Step 4 — Tokenize

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("sshleifer/tiny-gpt2")
tokenizer.pad_token = tokenizer.eos_token

def tokenize(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=64,
    )

tokenized = dataset.map(tokenize, batched=True)
print(tokenized.column_names)
print(len(tokenized[0]["input_ids"]))   # 64
```

`padding="max_length"` and `max_length=64` are not training settings — they exist so length statistics show up immediately in this small exercise. Real training uses dynamic padding via a data collator.

## What to notice in this code

![Format checking and length verification flow](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/02/02-03-what-to-notice-in-this-code.en.png)

*Format checking and length verification flow*

- `datasets.load_dataset()` mimics the JSONL shape you typically receive in production.
- Splitting templating from tokenization makes it easy to swap a model-specific chat template later.
- The example fixes `padding="max_length"` and `max_length=64` so length stats are visible even in a tiny exercise.
- A tokenizer with no `pad_token` will crash training. For GPT-2 family the standard trick is to reuse `eos_token` as `pad_token`.

## Common mistakes

![Deduplication and split decision flow](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/02/02-04-where-engineers-get-confused.en.png)

*Deduplication and split decision flow*

- **Assuming more data is always better** — Duplicate answers or mixed formats break small models faster. 500 consistent samples almost always beat 5,000 noisy ones for LoRA.
- **Not building `labels` at the dataset stage** — That is fine. The collator in post 4 builds them while masking the prompt to -100.
- **Missing EOS** — Without `<eos>` after the response, the model never learns to stop. If inference produces unbounded continuations, suspect this first.
- **`max_length` too short** — Training at 64 and expecting 256-token answers truncates them. Decide based on the 95th percentile of your training data.
- **No train/eval split** — Reusing the same data for evaluation in post 5 grades memorization. Hold out at least a 90/10 split.

## Field notes

- **Start with 50 samples**: validate length distribution, missing prompts, and EOS presence on a tiny set before scaling.
- **Keep a golden set aside**: 100–200 samples reserved exclusively for evaluation. They become decisive in post 5.
- **Version your dataset**: name files like `dataset_v2025-04-30.jsonl` and record the version in model metadata.
- **Automate PII and dedup**: regex-based PII masking and MinHash deduplication should be in from day one. Adding them later forces you to rerun every experiment.
- **Visualize length distribution**: `tokenized.with_format("pandas")["input_ids"].apply(len).describe()` ends the `max_length` debate in one shot.

## Checklist

- [ ] Raw JSONL samples follow the instruction / input / output structure.
- [ ] You actually loaded the file with `datasets.load_dataset()`.
- [ ] After tokenization you inspected columns and lengths.
- [ ] `pad_token` is set, and EOS is appended to responses.
- [ ] train/eval split is in place.
- [ ] You connected which modules will receive LoRA in post 3 to your data length distribution.

## Exercises

1. Add five more instructions to the example and print the mean and 95th percentile token length. What `max_length` would you pick?
2. Add a sample where the `input` field is empty (a short-answer question) and harden `render()` so the template does not break.
3. Apply a Llama-3 chat template to the same data and re-tokenize. Explain why the same text now has a different token count.

## Wrap-up · next post

The point of dataset preparation is to make the input/output boundary the model must learn unmistakably clear. Locking in structure on a tiny set keeps the training loop debuggable later.

Post 3 moves on to LoRA adapter configuration. We dissect `LoraConfig`'s `r`, `alpha`, `target_modules`, and `dropout` line by line and see how each one shows up in training behavior.

## Data format comparison: instruction, chat, and completion under one lens

Format choice is not a matter of preference — it is a failure-cost decision. Pick wrong once and every subsequent training log is distorted.

| Format | Example structure | Strength | Weakness | Best for |
| --- | --- | --- | --- | --- |
| instruction | `instruction/input/output` | Simple to implement and review | Weak at multi-turn | Single Q&A, format correction |
| chat | `[{role, content}]` | Mirrors real conversation flow | Heavy template dependency | Chatbot, support UX |
| completion | `prefix + continuation` | Closest to pretraining format | Instruction boundary is vague | Code completion, sentence continuation |

Start with instruction format, then migrate to chat format if the product is multi-turn. This order is operationally stable.

## Data quality gate: automated checks that catch failures before training

These checks apply even to a small JSONL file.

```python
import json
from pathlib import Path

def validate_jsonl(path: Path) -> dict:
    total = 0
    missing = 0
    empty_output = 0
    long_samples = 0

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            total += 1
            row = json.loads(line)
            if "instruction" not in row or "output" not in row:
                missing += 1
                continue
            if not row["output"].strip():
                empty_output += 1
            if len((row.get("instruction", "") + row.get("output", ""))) > 2000:
                long_samples += 1

    return {
        "total": total,
        "missing": missing,
        "empty_output": empty_output,
        "long_samples": long_samples,
    }
```

Putting this check in CI prevents the "training finished but results look wrong" post-mortem.

## Label masking example: applying loss only to the response span

The single most important preprocessing technique is `labels` masking.

```python
def build_labels(input_ids, response_start_idx):
    labels = input_ids.copy()
    for i in range(response_start_idx):
        labels[i] = -100
    return labels
```

`-100` means "exclude from loss computation." Without this, the model spends loss budget copying the instruction itself, and actual generation quality becomes blurry.

## Connecting length distribution to VRAM: do not pick max_length by gut feeling

Input length is cost. Extracting the distribution as numbers lets you choose `max_length` rationally.

| Metric | Value (example) | Interpretation |
| --- | --- | --- |
| Mean token length | 148 | Room for small batches |
| p95 | 356 | Candidate for `max_length=384` |
| p99 | 612 | Consider splitting long samples separately |
| Max length | 1304 | Truncating wholesale loses significant information |

In practice, set p95 as the default length and handle extremely long samples by splitting or routing to a separate task.

## Preprocessed output sample: always verify with human eyes before training

```text
### Instruction:
Write an email validation API in FastAPI.

### Input:
Return 400 on regex validation failure.

### Response:
@app.post("/validate-email")
def validate_email(req: EmailRequest):
    if not EMAIL_RE.match(req.email):
        raise HTTPException(status_code=400, detail="invalid email")
    return {"ok": True}<eos>
```

When the template looks this consistent, you can narrow subsequent failures to model/training problems.

## Hyperparameter table: safe starting points by dataset size

| Sample count | `max_length` | Batch strategy | Learning rate | Note |
| --- | --- | --- | --- | --- |
| 100–500 | 256–384 | Small fixed batch | `5e-4` | Pipeline verification first |
| 500–5k | 384–512 | Gradient accumulation | `2e-4`–`5e-4` | Watch for overfitting |
| 5k+ | 512+ | Dynamic padding recommended | `1e-4`–`3e-4` | Evaluation set split is mandatory |

As dataset size grows, the first thing to change is length/batch policy, not rank. Maintaining this order keeps root-cause analysis possible.

## End-to-end pattern: data prep, LoRA config, and training input verification in one flow

Fine-tuning quality is determined by input contracts before model architecture. Validate dataset templates, LoRA settings, and length statistics in the same pipeline to reduce debugging cost.

```python
from dataclasses import dataclass
from typing import Iterable

from peft import LoraConfig

@dataclass
class Sample:
    instruction: str
    input: str
    output: str

def render(sample: Sample) -> str:
    return (
        "### Instruction:\n" + sample.instruction + "\n\n"
        "### Input:\n" + sample.input + "\n\n"
        "### Response:\n" + sample.output
    )

def build_lora_config() -> LoraConfig:
    return LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )

def length_stats(lengths: Iterable[int]) -> tuple[int, float, int]:
    data = sorted(lengths)
    if not data:
        return 0, 0.0, 0
    avg = sum(data) / len(data)
    p95 = data[int(len(data) * 0.95) - 1]
    return min(data), avg, p95
```

Operationally, `target_modules` and the data template must be managed together. When the template changes, token length distribution shifts, which directly affects batch size and training stability. Record data version, LoRA config version, and evaluation metrics as the same experiment unit. This is how you quickly separate whether a quality change came from data or adapter config.

## Dataset versioning in production: manage by experiment unit, not single file

In production, managing a single `train.jsonl` breaks reproducibility immediately. At minimum, bundle these three files as one version.

| File | Role | Example |
| --- | --- | --- |
| `dataset.train.jsonl` | Training samples | instruction/input/output originals |
| `dataset.eval.jsonl` | Evaluation samples | Hold-out golden candidates |
| `dataset.meta.yaml` | Generation rules/policy | Field conventions, masking policy, creation date |

Writing rules like "enforce `<eos>` at the end of every response" in `dataset.meta.yaml` keeps preprocessing results consistent even as team members change.

Additionally, keep data generation scripts alongside validation scripts in the examples repository. If only the raw JSONL remains, the intent behind changes disappears; with scripts, you can trace why specific samples were removed.

Document sample-level changes in the PR description. Unlike code, data diffs are hard to interpret by diff alone.

In practice, attaching a before/after comparison of 5 samples to dataset-change PRs dramatically improves review quality.

## Preprocessing pipeline example: filter → template → tokenize → validate

```python
def preprocess_pipeline(dataset, tokenizer, max_length=384):
    def filter_invalid(example):
        return bool(example.get("instruction")) and bool(example.get("output"))

    filtered = dataset.filter(filter_invalid)

    def render(example):
        input_text = example.get("input", "").strip()
        return {
            "text": (
                "### Instruction:\n" + example["instruction"].strip() + "\n\n"
                + "### Input:\n" + input_text + "\n\n"
                + "### Response:\n" + example["output"].strip() + "<eos>"
            )
        }

    rendered = filtered.map(render)

    def tokenize(example):
        return tokenizer(
            example["text"],
            truncation=True,
            max_length=max_length,
            padding=False,
        )

    tokenized = rendered.map(tokenize)
    return tokenized
```

This pipeline is simple, but because each stage's output is separated, you can pinpoint problems quickly.

## Diagnosing data problems from loss curves

Dataset issues leave signals in the loss curve after training starts.

- Loss nearly flat from the beginning: template/masking problem or adapter connection issue
- Sharp initial drop followed by explosive oscillation: excessive duplicates, length distribution imbalance
- Training loss descends but evaluation metrics plateau: format overfitting, lack of semantic quality

Recording these patterns lets you prioritize data refinement decisions quickly.

## Data example expansion: bad sample vs good sample

```text
[Bad sample]
instruction: "Python"
output: "Yes"

[Good sample]
instruction: "Explain two ways to iterate a Python list in reverse."
input: "Include a for-loop example."
output: "1) Using reversed(lst) lets you iterate in reverse while keeping the original intact..."
```

A good sample is not one that is long — it is one where the pattern the model should learn is unambiguous.

## Operational statistics output example

```python
def summarize_token_lengths(tokenized):
    lengths = [len(x["input_ids"]) for x in tokenized]
    lengths = sorted(lengths)
    n = len(lengths)
    p95 = lengths[int(n * 0.95) - 1]
    p99 = lengths[int(n * 0.99) - 1]
    return {
        "count": n,
        "min": lengths[0],
        "mean": sum(lengths) / n,
        "p95": p95,
        "p99": p99,
        "max": lengths[-1],
    }
```

This output connects to episode 4's batch strategy decisions and episode 6's serving `max_new_tokens` policy.

## Answering the Opening Questions

- **What shape should the `instruction / input / output` fields take?**
  - Keep a raw structure easy for humans to review, while ensuring the response boundary the model must learn is unambiguous. This article separated `instruction`, optional `input`, and the learning-target `output`, with the final text making only the segment after `### Response:` the model's imitation zone. Appending EOS teaches the model where to stop.
- **How can you read a small JSONL file directly with Hugging Face `datasets`?**
  - Even for small experiments, create a JSONL file and read it with `load_dataset("json", data_files=..., split="train")`. This connects column names, sample count, and later `map()` for template application and tokenization into one flow. What matters is not the reading technique itself but the habit of seeing three layers: raw sample → template text → token tensor.
- **What are the minimum verification points you must check during preprocessing?**
  - Missing required fields, empty `output`, EOS presence, `pad_token` configuration, length distribution, and train/eval split must all be checked. If any one is missing, episode 4 will show ambiguously oscillating loss and episode 5 will be hard to interpret. That's why the article treated JSONL validation, length statistics, and label masking as the basic gates of the preprocessing stage.

<!-- toc:begin -->
## In this series

- [LLM Fine-tuning 101 (1/6): LLM Fine-tuning Primer](./01-intro.md)
- **LLM Fine-tuning 101 (2/6): Dataset Preparation and Preprocessing (current)**
- LLM Fine-tuning 101 (3/6): Configuring LoRA Adapters (upcoming)
- LLM Fine-tuning 101 (4/6): Training Loop and Hyperparameters (upcoming)
- LLM Fine-tuning 101 (5/6): Model Evaluation (upcoming)
- LLM Fine-tuning 101 (6/6): Model Serving (upcoming)

<!-- toc:end -->

---

## References

- [Hugging Face Datasets documentation](https://huggingface.co/docs/datasets)
- [Instruction tuning overview](https://arxiv.org/abs/2203.02155)
- [Alpaca dataset format](https://github.com/tatsu-lab/stanford_alpaca#data-release)
- [Llama 3 chat template](https://huggingface.co/docs/transformers/main/en/chat_templating)

Tags: Fine-tuning, LoRA, LLM, Python

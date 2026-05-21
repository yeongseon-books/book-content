---
title: "LLM Fine-tuning 101 (4/6): Training Loop and Hyperparameters"
series: llm-finetuning-101
episode: 4
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Fine-tuning
- Trainer
- Hyperparameters
- LearningRate
- Optimizer
- Python
last_reviewed: '2026-05-01'
seo_description: Deconstruct one LLM training step into six stages to understand how learning rate, batch size, and gradient accumulation drive convergence.
---

# LLM Fine-tuning 101 (4/6): Training Loop and Hyperparameters

Training loops are easier to debug once you stop treating them like framework magic.

This is the fourth post in the LLM Fine-tuning 101 series.

This article breaks one training step into its six moving parts so you can reason about convergence and hyperparameters from first principles. The goal is not to chase a low loss number yet. The goal is to prove that one honest weight update actually happened.

![LLM Fine-tuning 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/04/04-02-what-you-can-shrink-and-what-you-cannot.en.png)
*LLM Fine-tuning 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What is the minimum you must set in `TrainingArguments` for a single training step to run?
- Why do `labels` and a data collator matter even in tiny experiments?
- When debugging a training loop, which output should you read first?

## Why this matters

Episode 4 is the first article in this series where actual weight updates happen. But the goal is still not high accuracy — it is to **prove that the training loop is alive**. Once you verify a single end-to-end step, future failures become easy to triage: is it the environment, the data, or the hyperparameters?

Episode 4 also breaks the habit of tuning many hyperparameters at once. If you change the learning rate by 10x and the batch size by 4x in the same run, you cannot tell which change moved the loss. Practicing one-change-at-a-time here pays off in episode 5 (evaluation), where "why is the score low?" gets answered much faster.

## Mental Model

A single training step decomposes into six stages:

```text
1. batch = data_collator([sample_i, sample_j, ...])
2. outputs = model(input_ids=..., attention_mask=..., labels=...)
3. loss = outputs.loss
4. loss.backward()                       # compute gradients
5. optimizer.step()                       # update parameters
6. lr_scheduler.step(); optimizer.zero_grad()
```

`Trainer` simply wraps these six stages. If any one of them is broken, the whole step is broken. So the 1-step run in this article is an integrity check: "all six stages passed once."

Two more relationships worth memorizing:

- **Effective batch size** = `per_device_train_batch_size × gradient_accumulation_steps × num_devices`. If this value is the same, the loss curves should look similar.
- **Learning rate** scales with effective batch size. If you grew the batch 4x, scale lr by something between √4 and 4x.

## Core concepts

| Item | Meaning |
| --- | --- |
| `labels` | Ground truth for next-token prediction. For causal LM, copy `input_ids` (mask the prompt with -100) |
| Data collator | Bundles variable-length samples into a batch and handles padding/masking in one place |
| `learning_rate` | LoRA typically uses 10x the value of full fine-tuning (1e-4 ~ 5e-4) |
| `per_device_train_batch_size` | Samples per GPU per forward pass |
| `gradient_accumulation_steps` | Accumulate small batches N times to emulate a large batch when memory is tight |
| `max_steps` / `num_train_epochs` | Use one or the other. `max_steps` wins if both are set |
| `warmup_ratio` | Linearly increases lr from 0 in the early steps |

## Before vs. After

**Before** — You call `Trainer.train()` and immediately get `KeyError: 'labels'` or NaN loss. You have no idea where to start.

**After** — Following the 1-step pattern in this article produces this single line:

```text
{'train_runtime': 1.42, 'train_samples_per_second': 1.41,
 'train_steps_per_second': 0.7, 'train_loss': 8.7421, 'epoch': 0.5}
```

The absolute loss value (8.74) is meaningless. What matters is (1) the run completed, (2) loss is a finite number (not NaN/Inf), and (3) `global_step=1`. When all three hold, your environment, data, adapter, and optimizer all worked at least once.

## What you can shrink and what you cannot

Sample count and step count can be cut down. But **tokenized inputs, labels, optimizer step, and loss computation** cannot be removed — drop any of them and you no longer have a training validation, just an inference test. That is why even the smallest example in this article keeps every training-related component intact.

![What you can shrink and what you cannot](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/04/04-01-what-you-can-shrink-and-what-you-cannot.en.png)

*What you can shrink and what you cannot*

## Step-by-step practice

### Step 1 — Build a two-line dataset

```python
from datasets import Dataset

texts = [
    "Q: How do I sort a Python list? A: Use sorted(lst) or lst.sort().",
    "Q: What does HTTP 404 mean? A: The requested resource was not found.",
]

rows = []
for text in texts:
    encoded = tokenizer(text, truncation=True, padding="max_length", max_length=64)
    encoded["labels"] = encoded["input_ids"].copy()
    rows.append(encoded)

dataset = Dataset.from_list(rows)
```

`labels = input_ids.copy()` is the simplest possible setup. In production you would mask the prompt portion with -100 so it does not contribute to the loss.

### Step 2 — Define `TrainingArguments`

```python
from transformers import TrainingArguments

args = TrainingArguments(
    output_dir="artifacts",
    per_device_train_batch_size=2,
    max_steps=1,
    learning_rate=5e-4,
    save_strategy="no",
    report_to=[],
)
```

Setting `report_to=[]` disables auto-connection to wandb/tensorboard. For a small validation run, an empty list is faster and cleaner.

### Step 3 — Run the Trainer

```python
from transformers import Trainer

trainer = Trainer(model=peft_model, args=args, train_dataset=dataset)
trainer.train()
```

### Step 4 — Verify the result

If the output shows `'train_loss': <number>` and `'global_step': 1`, you are done. If loss is exactly 0.0 or NaN, something is broken in your data, masking, or model dtype.

### Step 5 — Effective batch size experiment (optional)

```python
args.per_device_train_batch_size = 1
args.gradient_accumulation_steps = 2
args.max_steps = 1
```

The two configurations have the same effective batch size, so the loss output should be nearly identical. If it differs, there is a data leak somewhere.

## Runnable smoke test: one real training step

The most useful addition to this chapter is a self-contained script that performs exactly one weight update with the same ingredients you will later scale up.

```python
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

tokenizer = AutoTokenizer.from_pretrained("sshleifer/tiny-gpt2")
tokenizer.pad_token = tokenizer.eos_token

texts = [
    "Q: How do I sort a Python list? A: Use sorted(lst) or lst.sort().",
    "Q: What does HTTP 404 mean? A: The requested resource was not found.",
]

rows = []
for text in texts:
    encoded = tokenizer(text, truncation=True, padding="max_length", max_length=64)
    encoded["labels"] = encoded["input_ids"].copy()
    rows.append(encoded)

dataset = Dataset.from_list(rows)

base = AutoModelForCausalLM.from_pretrained("sshleifer/tiny-gpt2")
config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["c_attn", "c_proj"],
    bias="none",
)
model = get_peft_model(base, config)

args = TrainingArguments(
    output_dir="artifacts",
    per_device_train_batch_size=2,
    max_steps=1,
    learning_rate=5e-4,
    save_strategy="no",
    logging_steps=1,
    report_to=[],
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset,
    data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
)

metrics = trainer.train().metrics
print(metrics)
```

Run it with:

```bash
python main.py
```

**Expected output:**

```text
{'train_runtime': 1.2, 'train_samples_per_second': 1.6,
 'train_steps_per_second': 0.8, 'train_loss': 8.7, 'epoch': 1.0}
```

Your exact runtime and loss will differ by hardware and seed. The invariants to verify are simpler:

1. the process exits cleanly,
2. `train_loss` is finite,
3. `train_steps_per_second` is non-zero, and
4. the training loop reports one completed step.

## First-check guide when the step fails

| Symptom | Check first | Likely cause |
| --- | --- | --- |
| `KeyError: 'labels'` | Dataset columns | You forgot to create `labels` or renamed the field |
| Loss is `NaN` on step 1 | Learning rate and dtype | LR too high, unstable precision, or broken inputs |
| Training runs but loss never changes | Adapter wiring | `target_modules` are wrong or trainable params are 0 |
| CUDA OOM | Effective batch size | Batch too large, sequence too long, or accumulation too high |
| Step is extremely slow | Model loading and padding | Base model too large or `max_length` is much bigger than needed |

## Hyperparameter sweep order that stays debuggable

Once the single-step smoke test passes, widen only one dimension at a time.

1. **Hold the dataset fixed** and sweep `learning_rate` on a log scale.
2. **Hold lr fixed** and change effective batch size with accumulation.
3. **Hold both fixed** and extend `max_steps` or epochs.
4. **Only then** compare LoRA ranks or target modules.

This order matters because it preserves blame. If a run regresses, you can still point to one changed cause instead of three overlapping ones.

## What to notice in this code

![Relationship between batch size and gradient accumulation](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/04/04-03-what-to-notice-in-this-code.en.png)

*Relationship between batch size and gradient accumulation*

- `labels = input_ids.copy()` is the minimum setup needed for next-token prediction loss in causal LM.
- Even with `max_steps=1`, the backward pass and optimizer step actually execute.
- For this example, checking `training_loss` and `global_step` is enough. Whether the loop finishes matters more than the number itself.
- Setting `report_to=[]` disables wandb/tensorboard auto-connection and keeps small validations clean.

## Common mistakes

![Decision flow for training debug output priority](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/04/04-04-where-engineers-get-confused.en.png)

*Decision flow for training debug output priority*

- **Skipping the collator because samples are few** — once variable-length samples mix in, the run breaks immediately without a collator. Use `DataCollatorForLanguageModeling` even in tiny experiments.
- **Trusting the absolute loss value** — for a tiny model with 1 step, loss values of 8 to 10 are normal. Watch the trend and the NaN status, not the absolute number.
- **Column name mismatches** — Trainer silently drops any column that is not `input_ids`, `attention_mask`, or `labels`. A mistyped column will be invisible in your loss.
- **Changing lr by a huge factor at once** — jumping from 5e-4 to 5e-3 often produces NaN. Increase by 2-3x and observe.
- **Leaving `save_strategy="epoch"` on** — small validations fill the disk fast. Use `"no"` and call `trainer.save_model()` only at the end.
- **Ignoring fp16/bf16** — on bf16-capable GPUs (A100, H100, RTX 30+), `bf16=True` improves both memory and speed. For tiny model validation it is not necessary.

## Production application

- **Automate a 3-step smoke test**: every PR runs three steps, not one, and asserts loss is monotonically decreasing (or at least varying).
- **Sweep learning rate on a log scale**: try {1e-5, 5e-5, 1e-4, 5e-4, 1e-3} — five points is enough. Linear sweeps carry too little information.
- **Use gradient accumulation**: if GPU memory allows only batch=2 and you need effective batch=16, set `gradient_accumulation_steps=8`.
- **Evaluate on step intervals**: `eval_steps=50, evaluation_strategy="steps"` catches regressions early instead of waiting for an epoch.
- **Checkpoint policy**: `save_total_limit=2` protects the disk, and `load_best_model_at_end=True` lets episode 5 evaluate the best checkpoint automatically.
- **Wire wandb in**: once you compare two or more experiments, switch to `report_to=["wandb"]`. Overlaying loss curves and lr schedules in one view sharpens intuition fast.

## Checklist

- [ ] I can read and edit the required fields in `TrainingArguments`.
- [ ] I understand why `labels` is required.
- [ ] I ran `python main.py` and confirmed a 1-step training loss output.
- [ ] The loss was a finite number, not NaN.
- [ ] I can explain the effective batch size formula = `per_device × accum × devices`.
- [ ] I am ready to evaluate the same model in the next article.

## Exercises

1. Change `learning_rate` to 1e-5, 1e-4, and 1e-3, run 5 steps each, and compare loss curves. At which value does NaN appear?
2. Run `per_device_train_batch_size=1, gradient_accumulation_steps=4` and `per_device_train_batch_size=4, gradient_accumulation_steps=1` with the same lr. Are the loss curves similar? If not, list possible causes.
3. Build a collator that masks the prompt portion with -100. How does the loss change before and after masking?

## Summary · Next article

The training loop can be validated in surprisingly small units. Once a single step succeeds, the things that need to grow are data and time, not the basic structure. If the environment, data, adapter, or optimizer is broken, you will see the signal in step 1.

The next article (episode 5) covers evaluation. We will use perplexity as a quick sanity check and combine it with golden-set qualitative and quantitative evaluation, all in code.

## Answering the Opening Questions

- **What is the minimum you must set in `TrainingArguments` for a single training step to run?**
  - The article treats Training Loop and Hyperparameters as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why do `labels` and a data collator matter even in tiny experiments?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **When debugging a training loop, which output should you read first?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [LLM Fine-tuning 101 (1/6): LLM Fine-tuning Primer](./01-intro.md)
- [LLM Fine-tuning 101 (2/6): Dataset Preparation and Preprocessing](./02-dataset.md)
- [LLM Fine-tuning 101 (3/6): Configuring LoRA Adapters](./03-lora.md)
- **LLM Fine-tuning 101 (4/6): Training Loop and Hyperparameters (current)**
- LLM Fine-tuning 101 (5/6): Model Evaluation (upcoming)
- LLM Fine-tuning 101 (6/6): Model Serving (upcoming)

<!-- toc:end -->

---

## References

- [Transformers Trainer documentation](https://huggingface.co/docs/transformers/main_classes/trainer)
- [TrainingArguments reference](https://huggingface.co/docs/transformers/main_classes/trainer#transformers.TrainingArguments)
- [DataCollatorForLanguageModeling](https://huggingface.co/docs/transformers/main_classes/data_collator)
- [Mixed precision training](https://huggingface.co/docs/transformers/perf_train_gpu_one)

Tags: Fine-tuning, LoRA, LLM, Python

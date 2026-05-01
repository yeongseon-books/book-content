---
title: 'Training loop and hyperparameters'
series: llm-finetuning-101
episode: 4
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

# Training loop and hyperparameters

> LLM Fine-tuning 101 (4/6)

Example code: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/en/04-training)

With a LoRA adapter and dataset ready, it's time to train. Hugging Face TRL's `SFTTrainer` handles the training loop, gradient checkpointing, and logging cleanly. This post covers the training configuration and the key hyperparameters worth understanding.

---

<!-- ebook-only:start -->

**The key idea**: the training loop repeats batches until loss converges. Learning rate and batch size control convergence speed and stability.

## Where this chapter fits

This is chapter 4 of 6 in the series.
The previous chapter covered **Configuring the LoRA adapter**.
After this chapter, the next one moves on to **Model evaluation**.
<!-- ebook-only:end -->

## SFTTrainer setup

```python
import torch
from datasets import load_from_disk
from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM

MODEL_NAME = "microsoft/phi-2"
OUTPUT_DIR = "./outputs/finetuned"

def load_model_and_tokenizer():
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, quantization_config=bnb_config, device_map="auto", trust_remote_code=True
    )
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj", "k_proj", "dense"],
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model, tokenizer
```

---

## Training arguments

```python
def get_training_args(output_dir: str = OUTPUT_DIR) -> TrainingArguments:
    return TrainingArguments(
        output_dir=output_dir,
        # Epochs and batching
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=4,   # effective batch = 4 × 4 = 16
        # Optimizer
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        weight_decay=0.01,
        optim="paged_adamw_8bit",
        # Checkpointing and logging
        save_strategy="epoch",
        evaluation_strategy="epoch",
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        # Memory optimization
        fp16=True,
        gradient_checkpointing=True,
        dataloader_num_workers=0,
        # Reproducibility
        seed=42,
        data_seed=42,
    )
```

---

## Running training

```python
def train(dataset_path: str = "./data/finetuning"):
    """Run the fine-tuning job."""
    model, tokenizer = load_model_and_tokenizer()
    dataset_dict = load_from_disk(dataset_path)

    training_args = get_training_args()

    # Compute loss only on the response part, not the instruction
    response_template = "### Response:\n"
    collator = DataCollatorForCompletionOnlyLM(
        response_template=response_template,
        tokenizer=tokenizer,
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset_dict["train"],
        eval_dataset=dataset_dict["validation"],
        dataset_text_field="text",
        max_seq_length=512,
        data_collator=collator,
        args=training_args,
    )

    print("Starting training...")
    trainer.train()

    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"Model saved to {OUTPUT_DIR}")
    return trainer
```

---

## Key hyperparameter guide

```python
def hyperparameter_guide() -> list[dict]:
    return [
        {
            "param": "learning_rate",
            "recommended": "1e-4 to 3e-4",
            "note": "LoRA tolerates higher LR than full fine-tuning. Too high → divergence.",
        },
        {
            "param": "num_train_epochs",
            "recommended": "1 to 5",
            "note": "With fewer than 1K examples, use 1–2 epochs. More epochs risk overfitting.",
        },
        {
            "param": "gradient_accumulation_steps",
            "recommended": "4 to 16",
            "note": "Use instead of larger batch size when GPU memory is tight. Effective batch = batch × steps.",
        },
        {
            "param": "warmup_ratio",
            "recommended": "0.03 to 0.1",
            "note": "Spend 3–10% of total steps on warmup. Prevents loss explosion at the start.",
        },
        {
            "param": "lora_rank (r)",
            "recommended": "8 to 64",
            "note": "Higher rank = more expressiveness + more memory. 16 is a solid starting point.",
        },
    ]

for hp in hyperparameter_guide():
    print(f"\n{hp['param']}: {hp['recommended']}")
    print(f"  {hp['note']}")
```

---

## Monitoring training

```python
def monitor_training(trainer) -> None:
    """Print loss trends from the training log."""
    if not trainer.state.log_history:
        print("No log history found")
        return

    train_losses = [(e["epoch"], e["loss"]) for e in trainer.state.log_history if "loss" in e]
    eval_losses = [(e["epoch"], e["eval_loss"]) for e in trainer.state.log_history if "eval_loss" in e]

    print("Training loss (last 5):")
    for epoch, loss in train_losses[-5:]:
        print(f"  epoch {epoch:.1f}: {loss:.4f}")

    print("Validation loss:")
    for epoch, loss in eval_losses:
        print(f"  epoch {epoch:.0f}: {loss:.4f}")

    if len(eval_losses) >= 2:
        improvement = eval_losses[0][1] - eval_losses[-1][1]
        print(f"Validation loss improvement: {improvement:.4f}")
```

<!-- blog-only:start -->
Next: [Model evaluation](./05-evaluation.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- [Introduction to LLM Fine-tuning](./01-intro.md)
- [Dataset preparation and preprocessing](./02-dataset.md)
- [Configuring the LoRA adapter](./03-lora.md)
- **Training loop and hyperparameters (current)**
- Model evaluation (upcoming)
- Model serving (upcoming)

<!-- toc:end -->

---

## References

- [TRL SFTTrainer documentation](https://huggingface.co/docs/trl/sft_trainer)
- [Hugging Face TrainingArguments](https://huggingface.co/docs/transformers/main_classes/trainer#transformers.TrainingArguments)
- [Gradient checkpointing guide](https://huggingface.co/docs/transformers/perf_train_gpu_one#gradient-checkpointing)

Tags: Fine-tuning, LoRA, LLM, Python

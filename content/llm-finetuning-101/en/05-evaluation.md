---
title: 'Model evaluation'
series: llm-finetuning-101
episode: 5
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

# Model evaluation

> LLM Fine-tuning 101 (5/6)

Example code: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/en/05-evaluation)

A finished training run needs measurement. Loss alone is not enough. You need task-appropriate metrics, a quantitative comparison against the base model, and a look at actual outputs. This post covers how to evaluate a fine-tuned model.

---

## Loading the fine-tuned model

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

BASE_MODEL = "microsoft/phi-2"
ADAPTER_PATH = "./outputs/finetuned"

def load_finetuned_model(base_model: str = BASE_MODEL, adapter_path: str = ADAPTER_PATH):
    """Load the fine-tuned model with its LoRA adapter."""
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    tokenizer = AutoTokenizer.from_pretrained(adapter_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base, adapter_path)
    model.eval()
    return model, tokenizer

def generate_response(model, tokenizer, prompt: str, max_new_tokens: int = 200) -> str:
    """Generate a response for the given prompt."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=1.0,
            pad_token_id=tokenizer.eos_token_id,
        )
    generated = outputs[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True)
```

---

## Quantitative metrics

```python
import re
from collections import Counter

def compute_exact_match(predictions: list[str], references: list[str]) -> float:
    matches = sum(p.strip() == r.strip() for p, r in zip(predictions, references))
    return matches / len(references) if references else 0.0

def compute_f1(prediction: str, reference: str) -> float:
    """Token-level F1 score."""
    pred_tokens = prediction.lower().split()
    ref_tokens = reference.lower().split()
    pred_counter = Counter(pred_tokens)
    ref_counter = Counter(ref_tokens)
    common = sum((pred_counter & ref_counter).values())
    if common == 0:
        return 0.0
    precision = common / len(pred_tokens)
    recall = common / len(ref_tokens)
    return 2 * precision * recall / (precision + recall)

def compute_code_metrics(prediction: str, reference: str) -> dict:
    """Metrics for code generation tasks."""
    def extract_code(text: str) -> str:
        match = re.search(r"```(?:python)?\n?(.*?)```", text, re.DOTALL)
        return match.group(1).strip() if match else text.strip()

    pred_code = extract_code(prediction)
    ref_code = extract_code(reference)
    return {
        "exact_match": pred_code == ref_code,
        "f1": compute_f1(pred_code, ref_code),
        "line_coverage": len(set(pred_code.split("\n")) & set(ref_code.split("\n"))) / max(len(ref_code.split("\n")), 1),
    }
```

---

## Base model comparison

```python
from dataclasses import dataclass

@dataclass
class EvalResult:
    question: str
    reference: str
    base_answer: str
    finetuned_answer: str
    base_f1: float = 0.0
    finetuned_f1: float = 0.0

def compare_models(
    base_model,
    finetuned_model,
    tokenizer,
    test_cases: list[dict],
    prompt_formatter,
) -> list[EvalResult]:
    """Compare base and fine-tuned model on test cases."""
    results = []
    for tc in test_cases:
        prompt = prompt_formatter(tc, for_inference=True)
        base_ans = generate_response(base_model, tokenizer, prompt)
        ft_ans = generate_response(finetuned_model, tokenizer, prompt)
        result = EvalResult(
            question=tc["instruction"],
            reference=tc["output"],
            base_answer=base_ans,
            finetuned_answer=ft_ans,
            base_f1=compute_f1(base_ans, tc["output"]),
            finetuned_f1=compute_f1(ft_ans, tc["output"]),
        )
        results.append(result)
        print(f"Q: {tc['instruction'][:50]}...")
        print(f"  base F1: {result.base_f1:.3f}, fine-tuned F1: {result.finetuned_f1:.3f}")
    return results

def summarize_comparison(results: list[EvalResult]) -> dict:
    base_avg = sum(r.base_f1 for r in results) / len(results)
    ft_avg = sum(r.finetuned_f1 for r in results) / len(results)
    improved = sum(1 for r in results if r.finetuned_f1 > r.base_f1)
    return {
        "base_avg_f1": round(base_avg, 4),
        "finetuned_avg_f1": round(ft_avg, 4),
        "improvement": round(ft_avg - base_avg, 4),
        "improved_cases": f"{improved}/{len(results)}",
    }
```

---

## Running evaluation

```python
if __name__ == "__main__":
    model, tokenizer = load_finetuned_model()

    ALPACA_NO_INPUT_TEMPLATE = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:
{output}"""

    def format_example(example: dict, for_inference: bool = False) -> str:
        return ALPACA_NO_INPUT_TEMPLATE.format(
            instruction=example["instruction"],
            output="" if for_inference else example["output"],
        )

    test_cases = [
        {
            "instruction": "How do you merge two lists in Python?",
            "input": "",
            "output": "list1 + list2 or list1.extend(list2)",
        },
        {
            "instruction": "How do you check if a key exists in a dictionary?",
            "input": "",
            "output": "'key' in dict or dict.get('key') is not None",
        },
    ]

    for tc in test_cases:
        prompt = format_example(tc, for_inference=True)
        response = generate_response(model, tokenizer, prompt)
        f1 = compute_f1(response, tc["output"])
        print(f"\nQ: {tc['instruction']}")
        print(f"A: {response[:200]}")
        print(f"F1: {f1:.3f}")
```

<!-- blog-only:start -->
Next: [Model serving](./06-serving.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- [Introduction to LLM Fine-tuning](./01-intro.md)
- [Dataset preparation and preprocessing](./02-dataset.md)
- [Configuring the LoRA adapter](./03-lora.md)
- [Training loop and hyperparameters](./04-training.md)
- **Model evaluation (current)**
- Model serving (upcoming)

<!-- toc:end -->

---

## References

- [Hugging Face evaluate library](https://huggingface.co/docs/evaluate)
- [ROUGE metric](https://huggingface.co/spaces/evaluate-metric/rouge)
- [A survey on LLM evaluation](https://arxiv.org/abs/2307.03109)

Tags: Fine-tuning, LoRA, LLM, Python

---
title: 'Model serving'
series: llm-finetuning-101
episode: 6
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

# Model serving

> LLM Fine-tuning 101 (6/6)

Example code: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/en/06-serving)

This post covers deploying a fine-tuned model into a service. Merge the LoRA adapter into the base model to produce a single artifact, expose an inference endpoint with FastAPI, and push to the Hugging Face Hub.

---

## Merging the adapter

Merging the LoRA adapter into the base model lets you serve a single model at inference time, with no PEFT layer overhead. The merged model has the same parameter count as the original.

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

BASE_MODEL = "microsoft/phi-2"
ADAPTER_PATH = "./outputs/finetuned"
MERGED_PATH = "./outputs/merged"

def merge_adapter(
    base_model_name: str = BASE_MODEL,
    adapter_path: str = ADAPTER_PATH,
    output_path: str = MERGED_PATH,
) -> None:
    """Merge the LoRA adapter into the base model and save."""
    print("Loading base model...")
    # Merge in fp16 without 4-bit quantization
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(adapter_path)

    print("Loading and merging adapter...")
    model = PeftModel.from_pretrained(model, adapter_path)
    model = model.merge_and_unload()

    print(f"Saving merged model to {output_path}")
    model.save_pretrained(output_path, safe_serialization=True)
    tokenizer.save_pretrained(output_path)
    print("Merge complete")
```

---

## FastAPI inference server

```python
import time
from contextlib import asynccontextmanager
from typing import Optional

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

ALPACA_TEMPLATE = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:
"""

class InferenceRequest(BaseModel):
    instruction: str
    input: Optional[str] = ""
    max_new_tokens: int = 200
    temperature: float = 0.7
    do_sample: bool = True

class InferenceResponse(BaseModel):
    response: str
    latency_ms: float
    tokens_generated: int

_model = None
_tokenizer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model, _tokenizer
    model_path = "./outputs/merged"
    print(f"Loading model from {model_path}")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    _tokenizer = AutoTokenizer.from_pretrained(model_path)
    if _tokenizer.pad_token is None:
        _tokenizer.pad_token = _tokenizer.eos_token
    _model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    _model.eval()
    print("Model ready")
    yield
    _model = None
    _tokenizer = None

app = FastAPI(title="LLM Inference API", lifespan=lifespan)

@app.post("/generate", response_model=InferenceResponse)
async def generate(request: InferenceRequest):
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    prompt = ALPACA_TEMPLATE.format(instruction=request.instruction)
    inputs = _tokenizer(prompt, return_tensors="pt").to(_model.device)

    start = time.time()
    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=request.max_new_tokens,
            do_sample=request.do_sample,
            temperature=request.temperature if request.do_sample else 1.0,
            pad_token_id=_tokenizer.eos_token_id,
        )
    latency_ms = (time.time() - start) * 1000

    generated = outputs[0][inputs["input_ids"].shape[1]:]
    return InferenceResponse(
        response=_tokenizer.decode(generated, skip_special_tokens=True),
        latency_ms=round(latency_ms, 1),
        tokens_generated=len(generated),
    )

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": _model is not None}
```

---

## Pushing to Hugging Face Hub

```python
from huggingface_hub import HfApi

def push_to_hub(
    model_path: str,
    repo_id: str,
    private: bool = True,
    token: str | None = None,
) -> None:
    """Push the merged model to the Hugging Face Hub."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    print(f"Pushing to {repo_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, torch_dtype=torch.float16, trust_remote_code=True
    )
    tokenizer.push_to_hub(repo_id, private=private, token=token)
    model.push_to_hub(repo_id, private=private, token=token)
    print(f"Done: https://huggingface.co/{repo_id}")

def push_adapter_only(
    adapter_path: str,
    repo_id: str,
    private: bool = True,
    token: str | None = None,
) -> None:
    """Push adapter weights only (saves storage vs. full model)."""
    api = HfApi(token=token)
    api.create_repo(repo_id=repo_id, private=private, exist_ok=True)
    api.upload_folder(folder_path=adapter_path, repo_id=repo_id, token=token)
    print(f"Adapter pushed: https://huggingface.co/{repo_id}")
```

---

## Series summary

```python
pipeline_steps = [
    "1. Load base model (4-bit quantization)",
    "2. Prepare dataset (Alpaca instruction format)",
    "3. Configure LoRA adapter (r=16, alpha=32)",
    "4. Train with SFTTrainer (3 epochs, lr=2e-4)",
    "5. Evaluate (F1, comparison against base model)",
    "6. Merge adapter and serve with FastAPI",
]
for step in pipeline_steps:
    print(step)
```

The pipeline built across this series runs on a single consumer GPU. LoRA makes it possible to fine-tune a 7B model in 8 GB of VRAM. In practice, data quality, hyperparameter search, and evaluation metric design are what determine the outcome — not the framework.

<!-- toc:begin -->
## In this series

- [Introduction to LLM Fine-tuning](./01-intro.md)
- [Dataset preparation and preprocessing](./02-dataset.md)
- [Configuring the LoRA adapter](./03-lora.md)
- [Training loop and hyperparameters](./04-training.md)
- [Model evaluation](./05-evaluation.md)
- **Model serving (current)**

<!-- toc:end -->

---

## References

- [Hugging Face Hub upload documentation](https://huggingface.co/docs/hub/models-uploading)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [PEFT merge_and_unload](https://huggingface.co/docs/peft/package_reference/lora#peft.LoraModel.merge_and_unload)

Tags: Fine-tuning, LoRA, LLM, Python

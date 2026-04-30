# Configuring the LoRA adapter

> LLM Fine-tuning 101 (3/6)

LoRA (Low-Rank Adaptation) freezes the original model weights and adds a small pair of matrices at each layer. Trainable parameters drop below 1% of the original, while performance stays close to full fine-tuning. This post covers LoRA's mechanics and adapter configuration with the PEFT library.

---

## How LoRA works

Instead of updating the full weight matrix W (d×k), LoRA approximates the update with the product of two low-rank matrices A (d×r) and B (r×k), where r << min(d, k).

```python
"""
Original weights: W (d × k) — frozen, not trained
LoRA update:      ΔW = B × A
  A: (d × r), initialized: Gaussian
  B: (r × k), initialized: zeros

Forward pass: h = W₀x + (B×A)x × (alpha/r)
  - alpha: scaling hyperparameter
  - r: rank (typically 4–64)

Trainable parameter ratio = 2 × r / (d + k)
  - d=4096, k=4096, r=16: 0.39%
"""

import torch
import torch.nn as nn

class LoRALinear(nn.Module):
    """Linear layer with LoRA (for conceptual illustration)."""

    def __init__(self, in_features: int, out_features: int, rank: int = 16, alpha: float = 32.0):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features), requires_grad=False)
        self.lora_A = nn.Parameter(torch.randn(in_features, rank) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(rank, out_features))
        self.scale = alpha / rank

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        base = x @ self.weight.T
        lora = x @ self.lora_A @ self.lora_B * self.scale
        return base + lora

d, k, r = 4096, 4096, 16
total = d * k
lora_params = d * r + r * k
print(f"Total parameters: {total:,}")
print(f"LoRA parameters:  {lora_params:,} ({100 * lora_params / total:.2f}%)")
```

---

## Applying LoRA with PEFT

```python
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

def create_lora_config(
    rank: int = 16,
    alpha: float = 32.0,
    dropout: float = 0.05,
    target_modules: list[str] | None = None,
) -> LoraConfig:
    """Build a LoRA configuration."""
    if target_modules is None:
        target_modules = ["q_proj", "v_proj", "k_proj", "dense"]
    return LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=rank,
        lora_alpha=alpha,
        lora_dropout=dropout,
        target_modules=target_modules,
        bias="none",
        inference_mode=False,
    )

def apply_lora(model, lora_config: LoraConfig):
    """Wrap the base model with LoRA adapters."""
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model

def load_model_for_training(model_name: str = "microsoft/phi-2"):
    """Load a model with QLoRA configuration."""
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
    model = prepare_model_for_kbit_training(model)
    return model, tokenizer
```

---

## Choosing rank and alpha

```python
def rank_alpha_guide() -> dict:
    return {
        "conservative": {
            "r": 8, "alpha": 16,
            "use_case": "Simple tasks, data < 1K examples, overfitting concern",
            "trainable_ratio": "~0.2%",
        },
        "standard": {
            "r": 16, "alpha": 32,
            "use_case": "General instruction tuning (recommended starting point)",
            "trainable_ratio": "~0.4%",
        },
        "aggressive": {
            "r": 64, "alpha": 128,
            "use_case": "Complex tasks, data > 10K examples, high expressiveness needed",
            "trainable_ratio": "~1.6%",
        },
    }

for name, config in rank_alpha_guide().items():
    print(f"\n{name}: r={config['r']}, alpha={config['alpha']}")
    print(f"  {config['use_case']}")
    print(f"  trainable: {config['trainable_ratio']}")
```

---

## Finding target modules

```python
def find_target_modules(model) -> list[str]:
    """Print the names of linear layers available as LoRA targets."""
    modules = set()
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            modules.add(name.split(".")[-1])
    return sorted(modules)

if __name__ == "__main__":
    model, tokenizer = load_model_for_training()
    print("Linear layers:", find_target_modules(model))

    lora_config = create_lora_config(rank=16, alpha=32)
    model = apply_lora(model, lora_config)

    model.save_pretrained("./outputs/lora-adapter")
    tokenizer.save_pretrained("./outputs/lora-adapter")
    print("LoRA adapter saved")
```

<!-- toc:begin -->
## In this series

- [Introduction to LLM Fine-tuning](./01-intro.md)
- [Dataset preparation and preprocessing](./02-dataset.md)
- **Configuring the LoRA adapter (current)**
- Training loop and hyperparameters (upcoming)
- Model evaluation (upcoming)
- Model serving (upcoming)

<!-- toc:end -->

---

## References

- [PEFT LoRA conceptual guide](https://huggingface.co/docs/peft/conceptual_guides/lora)
- [LoRA paper](https://arxiv.org/abs/2106.09685)
- [QLoRA paper](https://arxiv.org/abs/2305.14314)

Tags: Fine-tuning, LoRA, LLM, Python

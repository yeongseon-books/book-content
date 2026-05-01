---
title: 'LoRA 어댑터 구성'
series: llm-finetuning-101
episode: 3
language: ko
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

# LoRA 어댑터 구성

> LLM 파인튜닝 101 (3/6)

예제 코드: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/ko/03-lora)

LoRA(Low-Rank Adaptation)는 원본 모델 가중치를 고정하고 각 레이어에 소형 행렬 쌍을 추가하는 방식입니다. 학습 가능한 파라미터 수를 1% 미만으로 줄이면서도 풀 파인튜닝에 근접한 성능을 냅니다. 이 포스트에서는 LoRA 원리와 PEFT 라이브러리를 사용한 어댑터 구성을 다룹니다.

---

## LoRA 동작 원리

기존 가중치 행렬 W(d×k)를 업데이트할 때 전체 행렬을 학습하는 대신, 두 개의 저랭크 행렬 A(d×r)와 B(r×k)의 곱으로 근사합니다. r은 랭크이며 r << min(d, k)입니다.

```python
"""
기존 가중치: W (d × k) — 고정, 학습하지 않음
LoRA 업데이트: ΔW = B × A
  A: (d × r), 초기화: 가우시안
  B: (r × k), 초기화: 0

순전파: h = W₀x + (B×A)x × (alpha/r)
  - alpha: 스케일링 하이퍼파라미터
  - r: 랭크 (일반적으로 4~64)

학습 파라미터 비율 = 2 × r / (d + k)
  - d=4096, k=4096, r=16: 0.39%
"""

import torch
import torch.nn as nn

class LoRALinear(nn.Module):
    """LoRA 적용 선형 레이어 (개념 시연용)."""

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

# 파라미터 비율 계산
d, k, r = 4096, 4096, 16
total = d * k
lora_params = d * r + r * k
print(f"전체 파라미터: {total:,}")
print(f"LoRA 파라미터: {lora_params:,} ({100 * lora_params / total:.2f}%)")
```

---

## PEFT로 LoRA 적용

```python
from peft import LoraConfig, get_peft_model, TaskType
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

def create_lora_config(
    rank: int = 16,
    alpha: float = 32.0,
    dropout: float = 0.05,
    target_modules: list[str] | None = None,
) -> LoraConfig:
    """LoRA 설정을 생성합니다."""
    if target_modules is None:
        # Phi-2 모델의 어텐션 레이어
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
    """베이스 모델에 LoRA를 적용합니다."""
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model

def load_model_for_training(model_name: str = "microsoft/phi-2"):
    """QLoRA 설정으로 모델을 로드합니다."""
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
    # 4비트 양자화 모델을 LoRA 학습에 맞게 준비
    from peft import prepare_model_for_kbit_training
    model = prepare_model_for_kbit_training(model)
    return model, tokenizer
```

---

## 랭크와 알파 선택

```python
import json

def rank_alpha_guide() -> dict:
    """랭크와 알파 설정 가이드."""
    return {
        "conservative": {
            "r": 8, "alpha": 16,
            "use_case": "단순 태스크, 데이터 < 1K, 과적합 우려",
            "trainable_ratio": "~0.2%",
        },
        "standard": {
            "r": 16, "alpha": 32,
            "use_case": "일반적인 인스트럭션 튜닝 (권장 시작점)",
            "trainable_ratio": "~0.4%",
        },
        "aggressive": {
            "r": 64, "alpha": 128,
            "use_case": "복잡한 태스크, 데이터 > 10K, 높은 표현력 필요",
            "trainable_ratio": "~1.6%",
        },
    }

for name, config in rank_alpha_guide().items():
    print(f"\n{name}:")
    print(f"  r={config['r']}, alpha={config['alpha']}")
    print(f"  사용 사례: {config['use_case']}")
    print(f"  학습 파라미터: {config['trainable_ratio']}")
```

---

## 타겟 모듈 탐색

```python
def find_target_modules(model) -> list[str]:
    """학습 가능한 선형 레이어 이름을 출력합니다."""
    modules = set()
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            # 마지막 레이어 이름만 추출
            layer_name = name.split(".")[-1]
            modules.add(layer_name)
    return sorted(modules)

if __name__ == "__main__":
    model, tokenizer = load_model_for_training()
    print("선형 레이어 목록:", find_target_modules(model))

    lora_config = create_lora_config(rank=16, alpha=32)
    model = apply_lora(model, lora_config)

    # 어댑터 가중치만 저장
    model.save_pretrained("./outputs/lora-adapter")
    tokenizer.save_pretrained("./outputs/lora-adapter")
    print("LoRA 어댑터 저장 완료")
```

<!-- blog-only:start -->
다음 글: [학습 루프와 하이퍼파라미터](./04-training.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [LLM 파인튜닝 입문](./01-intro.md)
- [데이터셋 준비와 전처리](./02-dataset.md)
- **LoRA 어댑터 구성 (현재 글)**
- 학습 루프와 하이퍼파라미터 (예정)
- 모델 평가 (예정)
- 모델 서빙 (예정)

<!-- toc:end -->

---

## 참고 자료

- [PEFT 라이브러리 문서](https://huggingface.co/docs/peft/conceptual_guides/lora)
- [LoRA 논문](https://arxiv.org/abs/2106.09685)
- [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314)

Tags: Fine-tuning, LoRA, LLM, Python

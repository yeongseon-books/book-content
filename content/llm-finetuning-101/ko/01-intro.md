---
title: 'LLM 파인튜닝 입문'
series: llm-finetuning-101
episode: 1
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

# LLM 파인튜닝 입문

> LLM 파인튜닝 101 (1/6)

예제 코드: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/ko/01-intro)

사전 학습된 LLM은 범용적으로 동작하지만, 특정 도메인이나 태스크에서는 한계가 뚜렷합니다. 고객 지원 봇이 자사 제품 용어를 정확히 사용해야 하거나, 의료 문서 요약 모델이 특정 형식을 따라야 할 때, 파인튜닝이 필요합니다. 이 시리즈는 LoRA를 활용한 효율적인 파인튜닝 전 과정을 다룹니다.

---

## 파인튜닝이란

파인튜닝은 사전 학습된 모델의 가중치를 특정 태스크에 맞게 추가 학습하는 과정입니다. 전체 가중치를 업데이트하는 풀 파인튜닝과, 일부 파라미터만 학습하는 파라미터 효율적 파인튜닝(PEFT)으로 나뉩니다.

풀 파인튜닝은 GPU 메모리가 매우 많이 필요합니다. 7B 파라미터 모델은 fp32 기준 약 28GB를 차지합니다. 반면 LoRA 같은 PEFT 기법은 원본 가중치를 고정하고 작은 어댑터 레이어만 학습해서 메모리 요구량을 90% 이상 줄입니다.

---

## 언제 파인튜닝이 필요한가

프롬프트 엔지니어링과 RAG로 해결되지 않을 때 파인튜닝을 고려합니다.

```python
"""
파인튜닝이 적합한 상황:
- 도메인 특화 어휘나 형식이 필요할 때
- 프롬프트에 담기 어려운 수백 개 예시가 필요할 때
- 추론 시 컨텍스트 길이를 줄이고 싶을 때 (비용 절감)
- 일관된 출력 형식을 강제해야 할 때

파인튜닝이 불필요한 상황:
- 범용 질문 답변 (GPT-4나 Claude가 이미 충분)
- 최신 정보 필요 (RAG가 더 적합)
- 데이터가 100개 미만 (과적합 위험)
"""

# 의사 결정 흐름
def should_finetune(task: dict) -> str:
    if task["examples"] < 100:
        return "데이터 부족 — 프롬프트 엔지니어링 먼저"
    if task["needs_latest_info"]:
        return "RAG 사용"
    if task["domain_specific"] and task["format_strict"]:
        return "파인튜닝 적합"
    return "프롬프트 엔지니어링으로 충분한지 먼저 확인"
```

---

## 파인튜닝 방법 비교

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
        name="풀 파인튜닝",
        trainable_params="100%",
        memory_requirement="매우 높음 (>80GB for 7B)",
        use_case="도메인 전체 재학습, 충분한 GPU 자원",
    ),
    FinetuningMethod(
        name="LoRA",
        trainable_params="0.1~1%",
        memory_requirement="낮음 (~8GB for 7B with 4-bit)",
        use_case="태스크 특화, 단일 GPU 환경",
    ),
    FinetuningMethod(
        name="QLoRA",
        trainable_params="0.1~1%",
        memory_requirement="매우 낮음 (~4GB for 7B)",
        use_case="소비자 GPU, 메모리 극도로 제한된 환경",
    ),
    FinetuningMethod(
        name="프롬프트 튜닝",
        trainable_params="<0.01%",
        memory_requirement="최소",
        use_case="단순 태스크 전환, 추론 시 오버헤드 없음",
    ),
]

for m in methods:
    print(f"{m.name}: 학습 파라미터 {m.trainable_params}, 메모리 {m.memory_requirement}")
```

---

## 환경 구성

이 시리즈에서는 Hugging Face `transformers`, `peft`, `datasets` 라이브러리를 사용합니다. 실습은 Google Colab(무료 T4 GPU)에서 가능합니다.

```python
# pip install transformers peft datasets accelerate bitsandbytes trl

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, TaskType

print(f"PyTorch: {torch.__version__}")
print(f"CUDA 사용 가능: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
```

---

## 기본 모델 로드

```python
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

MODEL_NAME = "microsoft/phi-2"  # 2.7B 파라미터, 소비자 GPU 적합

def load_base_model(model_name: str = MODEL_NAME) -> tuple:
    """4비트 양자화로 베이스 모델을 로드합니다."""
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
    """학습 가능한 파라미터 수를 반환합니다."""
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
    print(f"전체 파라미터: {stats['total']}")
    print(f"학습 가능 파라미터: {stats['trainable']} ({stats['ratio']})")

    # 베이스 모델 추론 테스트
    inputs = tokenizer("파이썬에서 리스트를 정렬하는 방법은?", return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=100, do_sample=False)
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

---

## 시리즈 전체 흐름

1편(현재)에서 파인튜닝 개념과 환경을 갖췄습니다. 2편에서는 학습 데이터를 준비하고, 3편에서 LoRA 어댑터를 구성합니다. 4편이 실제 학습 루프, 5편이 평가, 6편이 서빙으로 마무리됩니다.

<!-- blog-only:start -->
다음 글: [데이터셋 준비와 전처리](./02-dataset.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- **LLM 파인튜닝 입문 (현재 글)**
- 데이터셋 준비와 전처리 (예정)
- LoRA 어댑터 구성 (예정)
- 학습 루프와 하이퍼파라미터 (예정)
- 모델 평가 (예정)
- 모델 서빙 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Hugging Face PEFT 문서](https://huggingface.co/docs/peft)
- [LoRA 논문: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
- [QLoRA 논문](https://arxiv.org/abs/2305.14314)

Tags: Fine-tuning, LoRA, LLM, Python

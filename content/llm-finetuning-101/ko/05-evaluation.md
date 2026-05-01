---
title: '모델 평가'
series: llm-finetuning-101
episode: 5
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

# 모델 평가

> LLM 파인튜닝 101 (5/6)

학습이 끝난 모델은 실제로 얼마나 나아졌는지 측정해야 합니다. 손실 값만으로는 부족합니다. 태스크에 맞는 지표를 선택하고, 베이스 모델과 정량 비교하고, 실제 출력을 살펴봐야 합니다. 이 포스트에서는 파인튜닝된 모델 평가 방법을 다룹니다.

---

## 파인튜닝 모델 로드

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

BASE_MODEL = "microsoft/phi-2"
ADAPTER_PATH = "./outputs/finetuned"

def load_finetuned_model(base_model: str = BASE_MODEL, adapter_path: str = ADAPTER_PATH):
    """파인튜닝된 모델을 로드합니다."""
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
    """프롬프트에 대한 응답을 생성합니다."""
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

## 정량 평가 지표

```python
import re
from collections import Counter

def compute_exact_match(predictions: list[str], references: list[str]) -> float:
    """정확 일치율을 계산합니다."""
    matches = sum(p.strip() == r.strip() for p, r in zip(predictions, references))
    return matches / len(references) if references else 0.0

def compute_f1(prediction: str, reference: str) -> float:
    """토큰 수준 F1 점수를 계산합니다."""
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
    """코드 태스크용 지표를 계산합니다."""
    # 코드 블록 추출
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

## 베이스 모델 대비 비교

```python
from dataclasses import dataclass, field

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
    """베이스 모델과 파인튜닝 모델을 비교 평가합니다."""
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
        print(f"  베이스 F1: {result.base_f1:.3f}, 파인튜닝 F1: {result.finetuned_f1:.3f}")
    return results

def summarize_comparison(results: list[EvalResult]) -> dict:
    """비교 결과를 요약합니다."""
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

## 평가 실행

```python
if __name__ == "__main__":
    from transformers import AutoTokenizer

    # 파인튜닝 모델 로드
    model, tokenizer = load_finetuned_model()

    # 평가 케이스
    test_cases = [
        {
            "instruction": "파이썬에서 두 리스트를 합치는 방법은?",
            "input": "",
            "output": "list1 + list2 또는 list1.extend(list2)",
        },
        {
            "instruction": "딕셔너리에서 키가 존재하는지 확인하는 방법은?",
            "input": "",
            "output": "'key' in dict 또는 dict.get('key') is not None",
        },
    ]

    for tc in test_cases:
        from 03_lora import format_example  # 실제 프로젝트에서는 공통 모듈로 분리
        prompt = format_example(tc, for_inference=True)
        response = generate_response(model, tokenizer, prompt)
        f1 = compute_f1(response, tc["output"])
        print(f"\nQ: {tc['instruction']}")
        print(f"A: {response[:200]}")
        print(f"F1: {f1:.3f}")
```

<!-- toc:begin -->
## 시리즈 목차

- [LLM 파인튜닝 입문](./01-intro.md)
- [데이터셋 준비와 전처리](./02-dataset.md)
- [LoRA 어댑터 구성](./03-lora.md)
- [학습 루프와 하이퍼파라미터](./04-training.md)
- **모델 평가 (현재 글)**
- 모델 서빙 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Hugging Face evaluate 라이브러리](https://huggingface.co/docs/evaluate)
- [ROUGE 지표](https://huggingface.co/spaces/evaluate-metric/rouge)
- [LLM 평가 설문 논문](https://arxiv.org/abs/2307.03109)

Tags: Fine-tuning, LoRA, LLM, Python

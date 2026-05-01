---
title: '데이터셋 준비와 전처리'
series: llm-finetuning-101
episode: 2
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

# 데이터셋 준비와 전처리

> LLM 파인튜닝 101 (2/6)

파인튜닝의 품질은 데이터셋이 결정합니다. 모델 구조나 하이퍼파라미터보다 데이터 품질이 최종 성능에 더 큰 영향을 미칩니다. 이 포스트에서는 파인튜닝에 적합한 데이터 형식, 수집 전략, 전처리 파이프라인을 다룹니다.

---

## 데이터 형식

파인튜닝 데이터는 대개 인스트럭션-응답 쌍 형식입니다. 모델이 특정 입력에 대해 원하는 출력을 생성하도록 학습합니다.

```python
from dataclasses import dataclass

@dataclass
class TrainingExample:
    instruction: str  # 사용자 질문 또는 태스크 설명
    input: str        # 추가 컨텍스트 (선택)
    output: str       # 원하는 응답

# Alpaca 형식 예시
examples = [
    TrainingExample(
        instruction="다음 파이썬 코드의 버그를 찾아 수정하세요.",
        input="def add(a, b):\n    return a - b",
        output="버그: 덧셈 함수에서 빼기 연산자를 사용했습니다.\n\n수정:\ndef add(a, b):\n    return a + b",
    ),
    TrainingExample(
        instruction="SQL 쿼리를 작성하세요.",
        input="테이블: users(id, name, age). 30세 이상 사용자를 나이 내림차순으로 조회.",
        output="SELECT id, name, age FROM users WHERE age >= 30 ORDER BY age DESC;",
    ),
]
```

---

## 프롬프트 템플릿

모델마다 선호하는 프롬프트 형식이 있습니다. 학습 시와 추론 시 동일한 템플릿을 사용해야 합니다.

```python
from typing import Optional

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
    """학습 또는 추론용 프롬프트를 생성합니다."""
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

# 사용 예시
sample = {"instruction": "파이썬 리스트를 역순으로 만드세요.", "input": "", "output": "lst[::-1] 또는 lst.reverse()"}
print(format_example(sample))
```

---

## 데이터 수집과 정제

```python
import json
import re
from pathlib import Path
from datasets import Dataset

def load_jsonl(file_path: str) -> list[dict]:
    """JSONL 파일을 로드합니다."""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def validate_example(example: dict) -> tuple[bool, str]:
    """데이터 품질을 검증합니다."""
    if not example.get("instruction", "").strip():
        return False, "instruction 없음"
    if not example.get("output", "").strip():
        return False, "output 없음"
    if len(example["instruction"]) < 10:
        return False, "instruction 너무 짧음"
    if len(example["output"]) < 5:
        return False, "output 너무 짧음"
    # 중복 공백, 특수문자 제거
    if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", example["output"]):
        return False, "제어 문자 포함"
    return True, "ok"

def clean_example(example: dict) -> dict:
    """텍스트를 정제합니다."""
    return {
        "instruction": example["instruction"].strip(),
        "input": example.get("input", "").strip(),
        "output": example["output"].strip(),
    }

def build_dataset(raw_data: list[dict], tokenizer, max_length: int = 512) -> Dataset:
    """학습용 데이터셋을 빌드합니다."""
    valid, invalid = [], []
    for ex in raw_data:
        ok, reason = validate_example(ex)
        if ok:
            valid.append(clean_example(ex))
        else:
            invalid.append((ex, reason))

    print(f"유효: {len(valid)}, 제외: {len(invalid)}")
    if invalid[:3]:
        for ex, reason in invalid[:3]:
            print(f"  제외 이유: {reason} — {str(ex)[:80]}")

    # 프롬프트 포맷 적용
    formatted = [{"text": format_example(ex)} for ex in valid]

    # 토큰 길이 필터
    def tokenize_and_filter(batch):
        tokens = tokenizer(batch["text"], truncation=False)
        return {"length": [len(ids) for ids in tokens["input_ids"]]}

    dataset = Dataset.from_list(formatted)
    lengths = dataset.map(tokenize_and_filter, batched=True, batch_size=64)
    dataset = dataset.filter(lambda ex, idx: lengths[idx]["length"] <= max_length, with_indices=True)
    print(f"최대 길이 {max_length} 토큰 필터 후: {len(dataset)}개")
    return dataset
```

---

## 학습/검증 분할과 저장

```python
from datasets import DatasetDict

def split_and_save(dataset: Dataset, output_dir: str, val_ratio: float = 0.1) -> DatasetDict:
    """학습/검증 세트로 분할하고 저장합니다."""
    split = dataset.train_test_split(test_size=val_ratio, seed=42)
    dataset_dict = DatasetDict({"train": split["train"], "validation": split["test"]})

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    dataset_dict.save_to_disk(output_dir)

    print(f"학습: {len(dataset_dict['train'])}개")
    print(f"검증: {len(dataset_dict['validation'])}개")
    print(f"저장 위치: {output_dir}")
    return dataset_dict

if __name__ == "__main__":
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2", trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 샘플 데이터로 파이프라인 테스트
    raw_data = [
        {"instruction": "파이썬에서 딕셔너리를 생성하는 방법은?", "input": "", "output": "d = {'key': 'value'} 또는 d = dict(key='value')"},
        {"instruction": "리스트 컴프리헨션 예시를 보여주세요.", "input": "", "output": "[x**2 for x in range(10) if x % 2 == 0]"},
    ] * 50  # 반복해 데이터 수 확보

    dataset = build_dataset(raw_data, tokenizer, max_length=256)
    dataset_dict = split_and_save(dataset, "./data/finetuning")
```

---

## 데이터 품질 분석

```python
import statistics

def analyze_dataset(dataset: Dataset, tokenizer) -> dict:
    """데이터셋 통계를 분석합니다."""
    texts = dataset["text"]
    lengths = [len(tokenizer.encode(t)) for t in texts]
    return {
        "count": len(texts),
        "token_length": {
            "min": min(lengths),
            "max": max(lengths),
            "mean": round(statistics.mean(lengths), 1),
            "median": statistics.median(lengths),
            "p95": sorted(lengths)[int(len(lengths) * 0.95)],
        },
    }
```

<!-- toc:begin -->
## 시리즈 목차

- [LLM 파인튜닝 입문](./01-intro.md)
- **데이터셋 준비와 전처리 (현재 글)**
- LoRA 어댑터 구성 (예정)
- 학습 루프와 하이퍼파라미터 (예정)
- 모델 평가 (예정)
- 모델 서빙 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Alpaca 데이터셋](https://github.com/tatsu-lab/stanford_alpaca)
- [Hugging Face datasets 문서](https://huggingface.co/docs/datasets)
- [데이터 품질이 LLM 파인튜닝에 미치는 영향](https://arxiv.org/abs/2307.09288)

Tags: Fine-tuning, LoRA, LLM, Python

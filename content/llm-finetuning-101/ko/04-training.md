---
title: '학습 루프와 하이퍼파라미터'
series: llm-finetuning-101
episode: 4
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

# 학습 루프와 하이퍼파라미터

> LLM 파인튜닝 101 (4/6)

예제 코드: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/ko/04-training)

LoRA 어댑터와 데이터셋이 준비되면 실제 학습을 시작합니다. Hugging Face TRL 라이브러리의 `SFTTrainer`를 사용하면 학습 루프, 그래디언트 체크포인팅, 로깅을 간결하게 처리할 수 있습니다. 이 포스트에서는 학습 설정과 주요 하이퍼파라미터를 다룹니다.

---

## SFTTrainer 설정

```python
import os
from pathlib import Path

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

## 학습 인수

```python
def get_training_args(output_dir: str = OUTPUT_DIR) -> TrainingArguments:
    """학습 설정을 반환합니다."""
    return TrainingArguments(
        output_dir=output_dir,
        # 에폭과 배치
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=4,   # 유효 배치 크기 = 4 × 4 = 16
        # 옵티마이저
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        weight_decay=0.01,
        optim="paged_adamw_8bit",        # 메모리 효율적 옵티마이저
        # 체크포인트와 로깅
        save_strategy="epoch",
        evaluation_strategy="epoch",
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        # 메모리 최적화
        fp16=True,
        gradient_checkpointing=True,
        dataloader_num_workers=0,
        # 재현성
        seed=42,
        data_seed=42,
    )
```

---

## 학습 실행

```python
def train(dataset_path: str = "./data/finetuning"):
    """파인튜닝을 실행합니다."""
    model, tokenizer = load_model_and_tokenizer()
    dataset_dict = load_from_disk(dataset_path)
    train_dataset = dataset_dict["train"]
    eval_dataset = dataset_dict["validation"]

    training_args = get_training_args()

    # 응답 부분만 손실 계산 (instruction 부분 제외)
    response_template = "### Response:\n"
    collator = DataCollatorForCompletionOnlyLM(
        response_template=response_template,
        tokenizer=tokenizer,
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        dataset_text_field="text",
        max_seq_length=512,
        data_collator=collator,
        args=training_args,
    )

    print("학습 시작...")
    trainer.train()

    # 어댑터만 저장 (베이스 모델 제외)
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"모델 저장 완료: {OUTPUT_DIR}")
    return trainer
```

---

## 주요 하이퍼파라미터 가이드

```python
def hyperparameter_guide() -> list[dict]:
    return [
        {
            "param": "learning_rate",
            "recommended": "1e-4 ~ 3e-4",
            "note": "LoRA에서 전통적인 파인튜닝보다 높은 LR 사용 가능. 너무 높으면 발산.",
        },
        {
            "param": "num_train_epochs",
            "recommended": "1 ~ 5",
            "note": "데이터 < 1K이면 1~2 에폭. 많을수록 과적합 주의.",
        },
        {
            "param": "gradient_accumulation_steps",
            "recommended": "4 ~ 16",
            "note": "GPU 메모리 부족 시 배치 크기 대신 사용. 유효 배치 = batch × steps.",
        },
        {
            "param": "warmup_ratio",
            "recommended": "0.03 ~ 0.1",
            "note": "전체 스텝의 3~10%를 워밍업에 사용. 초기 손실 폭발 방지.",
        },
        {
            "param": "lora_rank (r)",
            "recommended": "8 ~ 64",
            "note": "높을수록 표현력 증가, 메모리 증가. 16이 좋은 시작점.",
        },
    ]

for hp in hyperparameter_guide():
    print(f"\n{hp['param']}: {hp['recommended']}")
    print(f"  {hp['note']}")
```

---

## 학습 모니터링

```python
def monitor_training(trainer) -> None:
    """학습 로그에서 손실 추이를 출력합니다."""
    if not trainer.state.log_history:
        print("로그 없음")
        return

    train_losses = [(e["epoch"], e["loss"]) for e in trainer.state.log_history if "loss" in e]
    eval_losses = [(e["epoch"], e["eval_loss"]) for e in trainer.state.log_history if "eval_loss" in e]

    print("학습 손실:")
    for epoch, loss in train_losses[-5:]:
        print(f"  epoch {epoch:.1f}: {loss:.4f}")

    print("검증 손실:")
    for epoch, loss in eval_losses:
        print(f"  epoch {epoch:.0f}: {loss:.4f}")

    if len(eval_losses) >= 2:
        improvement = eval_losses[0][1] - eval_losses[-1][1]
        print(f"검증 손실 개선: {improvement:.4f}")
```

<!-- blog-only:start -->
다음 글: [모델 평가](./05-evaluation.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [LLM 파인튜닝 입문](./01-intro.md)
- [데이터셋 준비와 전처리](./02-dataset.md)
- [LoRA 어댑터 구성](./03-lora.md)
- **학습 루프와 하이퍼파라미터 (현재 글)**
- 모델 평가 (예정)
- 모델 서빙 (예정)

<!-- toc:end -->

---

## 참고 자료

- [TRL SFTTrainer 문서](https://huggingface.co/docs/trl/sft_trainer)
- [Hugging Face TrainingArguments](https://huggingface.co/docs/transformers/main_classes/trainer#transformers.TrainingArguments)
- [그래디언트 체크포인팅 가이드](https://huggingface.co/docs/transformers/perf_train_gpu_one#gradient-checkpointing)

Tags: Fine-tuning, LoRA, LLM, Python

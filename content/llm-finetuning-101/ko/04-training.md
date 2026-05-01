---
title: '학습 루프와 하이퍼파라미터'
series: llm-finetuning-101
episode: 4
language: ko
status: publish-ready
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

## 이 글에서 답할 질문

- `TrainingArguments`에서 최소한 무엇을 지정해야 1 step 학습이 돌까?
- 왜 작은 실습에서도 `labels`와 data collator가 필요한가?
- 학습 루프를 디버깅할 때 먼저 봐야 할 출력은 무엇일까?

> 학습 루프는 거대한 블랙박스가 아니라, 토큰화된 배치를 모델에 넣고 loss를 한 번 줄이는 반복입니다.

예제 코드: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/ko/04-training)

4편은 파인튜닝 시리즈에서 처음으로 실제 업데이트를 발생시키는 글입니다. 하지만 여전히 목표는 큰 성능이 아니라 **학습 루프가 살아 있는지 확인하는 것**입니다. GPU 없는 환경에서 이 검증을 하려면 모델, 데이터셋, step 수를 극단적으로 줄여야 합니다.

예제 코드는 tiny GPT-2에 LoRA 어댑터를 붙이고, 질문-답변 두 줄짜리 데이터셋으로 `Trainer`를 1 step만 돌립니다. 실행 결과로 `global_step=1`과 `training_loss`가 출력되면, 옵티마이저와 backward 경로가 정상이라는 뜻입니다.

## 학습 루프에서 줄여도 되는 것과 줄이면 안 되는 것

샘플 수와 step 수는 줄여도 됩니다. 하지만 **토큰화된 입력, labels, optimizer step, loss 계산**은 줄이면 학습 검증이 아니라 단순 추론 테스트가 됩니다. 그래서 이 글의 예제는 가장 작은 데이터셋을 쓰더라도 학습 구성요소는 그대로 유지합니다.

![학습 루프에서 줄여도 되는 것과 줄이면 안 되는 것](../../../assets/llm-finetuning-101/04/04-01-what-you-can-shrink-and-what-you-cannot.ko.png)
## 최소 실행 예제

```python
from datasets import Dataset
from transformers import Trainer, TrainingArguments

texts = [
    "질문: 파이썬 리스트를 정렬하는 방법은? 답변: sorted(lst) 또는 lst.sort()를 사용합니다.",
    "질문: HTTP 404는 무엇을 뜻하나요? 답변: 요청한 리소스를 찾지 못했다는 뜻입니다.",
]

rows = []
for text in texts:
    encoded = tokenizer(text, truncation=True, padding="max_length", max_length=64)
    encoded["labels"] = encoded["input_ids"].copy()
    rows.append(encoded)

dataset = Dataset.from_list(rows)
args = TrainingArguments(
    output_dir="artifacts",
    per_device_train_batch_size=2,
    max_steps=1,
    learning_rate=5e-4,
    save_strategy="no",
    report_to=[],
)
trainer = Trainer(model=peft_model, args=args, train_dataset=dataset)
trainer.train()
```

## 이 코드에서 봐야 할 것

- `labels = input_ids.copy()`는 causal LM에서 다음 토큰 예측 손실을 계산하기 위한 최소 설정입니다.
- `max_steps=1`로 줄여도 backward와 optimizer step은 실제로 일어납니다.
- 이 예제는 `training_loss`와 `global_step`만 확인하면 충분합니다. 숫자 자체보다 루프가 끝까지 도는지가 더 중요합니다.

## 실무에서 헷갈리는 지점

- 샘플이 적다고 collator가 불필요한 것은 아닙니다. 배치 차원 정리가 필요하면 작은 실습에서도 collator가 도와줍니다.
- loss가 높게 나와도 실패가 아닙니다. tiny 모델에 한 step만 돌리는 예제라서 손실 절대값보다 실행 가능성이 중요합니다.
- Trainer가 편해 보여도 입력 컬럼 이름이 틀리면 바로 깨집니다. 그래서 2편에서 전처리 구조를 먼저 맞춘 것입니다.

## 체크리스트

- [ ] `TrainingArguments`의 필수 필드를 직접 읽고 수정할 수 있다.
- [ ] `labels`가 왜 필요한지 이해했다.
- [ ] `python main.py` 실행 후 1 step 학습과 loss 출력을 확인했다.
- [ ] 다음 글에서 동일한 모델을 평가할 준비가 되었다.

## 정리

학습 루프는 생각보다 작은 단위로도 검증할 수 있습니다. 1 step이 성공하면 이후에 늘려야 할 것은 데이터와 시간이지, 기본 구조가 아닙니다.

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

- [Transformers Trainer documentation](https://huggingface.co/docs/transformers/main_classes/trainer)
- [TrainingArguments reference](https://huggingface.co/docs/transformers/main_classes/trainer#transformers.TrainingArguments)

Tags: Fine-tuning, LoRA, LLM, Python

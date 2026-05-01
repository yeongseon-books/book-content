---
title: 'LoRA 어댑터 구성'
series: llm-finetuning-101
episode: 3
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

# LoRA 어댑터 구성

## 이 글에서 답할 질문

- `LoraConfig`에서 꼭 이해해야 할 필드는 무엇일까?
- `target_modules`를 잘못 고르면 어떤 문제가 생길까?
- 소형 GPT-2 계열에서 학습 가능한 파라미터 비율은 어느 정도로 내려갈까?

> LoRA 어댑터는 모델 전체를 다시 쓰는 장치가 아니라, 특정 선형 변환 옆에 붙는 작은 보정판입니다.

예제 코드: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/ko/03-lora)

3편부터는 실제 모델 객체를 만집니다. 다만 GPU 없는 환경을 전제로 하므로 `sshleifer/tiny-gpt2` 같은 초소형 모델을 사용합니다. 이 단계의 목표는 성능이 아니라 **구성이 올바른지**를 확인하는 것입니다.

예제 코드는 PEFT의 `LoraConfig`를 정의하고 `get_peft_model()`로 베이스 모델에 어댑터를 덧붙입니다. 실행하면 학습 가능한 파라미터 수와 전체 대비 비율이 출력되므로, 1편에서 계산한 감각이 코드 수준에서도 이어지는지 확인할 수 있습니다.

## 설정에서 의미가 큰 필드

`r`은 저랭크 차원, `lora_alpha`는 스케일, `lora_dropout`은 어댑터 경로에만 적용되는 드롭아웃입니다. 그리고 실무에서 가장 사고가 많이 나는 항목이 `target_modules`입니다. 이 목록이 틀리면 어댑터가 전혀 붙지 않거나, 원하지 않는 레이어에 붙습니다.

```mermaid
flowchart LR
    A[베이스 GPT-2 모델] --> B[target_modules 선택]
    B --> C[LoraConfig 정의]
    C --> D[get_peft_model 적용]
    D --> E[학습 가능 파라미터 비율 확인]
```

## 최소 실행 예제

```python
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("sshleifer/tiny-gpt2")
config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["c_attn", "c_proj"],
)
peft_model = get_peft_model(model, config)
peft_model.print_trainable_parameters()
```

## 이 코드에서 봐야 할 것

- GPT-2 계열은 attention과 projection 모듈 이름이 `c_attn`, `c_proj` 형태라서 target module을 문자열로 정확히 맞춰야 합니다.
- 실행 시 `fan_in_fan_out` 경고가 보일 수 있는데, GPT-2의 `Conv1D` 래퍼에 맞게 PEFT가 내부적으로 보정하는 정상 동작입니다.
- 이 글의 예제는 설정 확인용입니다. 실제 학습은 4편에서 `Trainer`와 연결합니다.

## 실무에서 헷갈리는 지점

- LoRA를 붙였다고 바로 학습되는 것은 아닙니다. 어댑터를 붙이는 단계와 옵티마이저로 업데이트하는 단계는 별개입니다.
- `r`을 크게 잡으면 성능이 무조건 좋아지지 않습니다. 데이터가 작을수록 과적합과 메모리 증가를 함께 봐야 합니다.
- 작은 데모 모델에서 맞는 모듈 이름이 큰 모델에서도 그대로 통하지 않을 수 있습니다. 항상 모델별 모듈 구조를 확인해야 합니다.

## 체크리스트

- [ ] `LoraConfig`의 핵심 필드 의미를 설명할 수 있다.
- [ ] `target_modules`가 왜 모델별로 달라지는지 이해했다.
- [ ] `python main.py`로 실제 어댑터 부착과 파라미터 비율 출력을 확인했다.
- [ ] 다음 글에서 이 모델을 1 step이라도 학습시킬 준비가 되었다.

## 정리

LoRA 구성 단계의 핵심은 성능 튜닝이 아니라 연결 검증입니다. 어댑터가 어디에 붙는지, 몇 개의 파라미터가 학습 대상이 되는지만 정확히 봐도 절반은 끝난 셈입니다.

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

- [PEFT quicktour](https://huggingface.co/docs/peft/quicktour)
- [Transformers model classes](https://huggingface.co/docs/transformers/index)

Tags: Fine-tuning, LoRA, LLM, Python

---
title: 모델 평가
series: llm-finetuning-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Fine-tuning
- Evaluation
- Perplexity
- GoldenSet
- Metrics
- Python
last_reviewed: '2026-05-12'
seo_description: 평가는 모델 내부 신호와 사용자 품질을 나눠 볼 때 가장 잘 작동합니다.
---

# 모델 평가

평가는 파인튜닝 데모가 가장 쉽게 오해를 부르는 단계입니다. 이 글은 LLM Finetuning 101 시리즈의 다섯 번째 글입니다. 여기서는 모델 내부 신호와 사용자 관점 품질을 분리해서, 개선과 회귀를 반복 가능한 루프로 어떻게 측정할지 정리하겠습니다.

학습이 끝나면 생성 예시부터 보고 싶어지지만, 운영에서는 그보다 먼저 정량 신호를 봐야 합니다. 그중 가장 기본이 perplexity입니다. 다만 perplexity 하나만으로 품질을 판단하면 금방 잘못된 결론에 도달합니다. 5편의 핵심은 평가를 **자동화 가능한 파이프라인**으로 바꾸는 데 있습니다.

## 이 글에서 다룰 문제

![이 글에서 다룰 문제](../../../assets/llm-finetuning-101/05/05-01-questions-this-post-answers.ko.png)

*이 글에서 다룰 문제*

- 파인튜닝 직후 가장 먼저 봐야 할 정량 신호인 perplexity는 어떻게 계산할까요?
- 학습 전후 perplexity 비교만으로는 왜 평가가 충분하지 않을까요?
- 작은 데모 모델에서도 왜 별도의 평가 루프를 유지해야 할까요?
- perplexity와 골든 세트 평가는 어떻게 함께 써야 할까요?

> Perplexity는 모델이 다음 토큰을 얼마나 낯설지 않게 예측하는지 보여 줍니다. 사람이 그 출력을 좋다고 느낄지까지 직접 보장하지는 않습니다.

예제 코드: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/en/05-evaluation)

## 왜 이 글이 중요한가

파인튜닝 직후 생성 샘플 몇 개만 보고 판단하면, 우연히 잘 나온 예시를 품질 개선으로 착각하기 쉽습니다. 운영에서는 먼저 정량 신호를 보고, 그다음에 정성 평가를 얹어야 합니다. perplexity는 평가 데이터에서 모델이 토큰을 얼마나 자연스럽게 예측하는지 보여 주는 가장 빠른 기준선입니다.

5편의 진짜 목적은 평가를 감이 아니라 **파이프라인**으로 만드는 것입니다. 매번 사람이 모든 출력을 읽는 방식은 확장되지 않습니다. 빠른 회귀 감지선으로 perplexity를 두고, 그 위에 골든 세트 기반 평가를 쌓아 두면 4편의 1-step 학습 검증처럼 평가도 자동화된 루프로 굴릴 수 있습니다.

## 멘탈 모델

평가는 **모델 내부 신호**와 **사용자 관점 품질**을 분리해서 볼 때 가장 잘 작동합니다.

```text
[Internal signals]              [User-facing quality]
- perplexity                    - answer match rate
- token-level accuracy          - format compliance
- gradient norm                 - human rating
        |                              |
        +--- fast regression line --+  |
                  |                    |
            run in CI            run on a separate
                                 schedule with golden set
```

내부 신호는 수 초에서 수 분 안에 빠르게 돌릴 수 있고, 사용자 관점 품질 평가는 수 분에서 수 시간까지 더 느립니다. 빠른 신호가 회귀하면 즉시 막고, 느린 신호는 주기적으로 추적하는 식이 운영에 맞습니다.

추가로 기억할 사실은 두 가지입니다.

- **perplexity = exp(mean cross-entropy loss)** 입니다. 손실이 내려가면 perplexity도 내려갑니다.
- **평가 데이터는 학습 데이터와 분리돼야 합니다.** 데모에서는 단순화를 위해 겹칠 수 있지만, 실제 프로젝트에서는 hold-out 세트가 필요합니다.

## 핵심 개념

| 항목 | 의미 |
| --- | --- |
| Perplexity | 다음 토큰 예측에서 모델이 느끼는 평균 "낯섦"입니다. 낮을수록 좋습니다. |
| Cross-entropy loss | 예측 분포와 정답 분포의 차이입니다. perplexity의 원료가 됩니다. |
| `model.eval()` | 드롭아웃과 배치 정규화를 추론 모드로 바꿉니다. |
| `torch.no_grad()` | 그래디언트 계산을 끄고 메모리와 시간을 절약합니다. |
| Golden set | 사람이 직접 검수한 평가용 입력/출력 쌍입니다. 회귀 감지의 기준점이 됩니다. |
| Hold-out set | 학습에 쓰지 않은 데이터입니다. perplexity 측정에 사용합니다. |
| Task metric | exact match, BLEU, ROUGE 같은 도메인별 지표입니다. |

## Before vs. After

**Before**

"손실이 줄었으니 학습이 된 것 같다"는 막연한 인상만 남습니다. 며칠 뒤 같은 결과를 다시 보여 달라고 하면 재현하기 어렵습니다.

**After**

5편의 평가 루프를 도입하면 결과는 아래 한 줄로 요약됩니다.

```text
{'before_ppl': 27431.84, 'after_ppl': 26890.17, 'delta_pct': -1.97}
```

중요한 것은 절대값이 아니라, (1) 평가가 학습과 분리되어 있고, (2) 같은 데이터로 전후를 비교하며, (3) CI에서도 같은 계산이 반복된다는 점입니다.

## perplexity를 올바르게 읽는 법

![perplexity와 품질 지표의 관계](../../../assets/llm-finetuning-101/05/05-02-the-right-way-to-read-perplexity.ko.png)

*perplexity와 품질 지표의 관계*

perplexity는 낮을수록 좋지만, 절대값만 보고 품질을 단정하면 안 됩니다. 작은 데모 모델, 작은 데이터셋, 짧은 컨텍스트 길이에서는 값이 크게 출렁일 수 있습니다. 그래서 perplexity는 실무에서 **회귀 감지 기준선**으로 가장 유용합니다. 무엇이 나빠졌는지, 혹은 설정을 바꾼 뒤 추세가 좋아졌는지를 빠르게 보는 데 강합니다.

![perplexity를 올바르게 읽는 법](../../../assets/llm-finetuning-101/05/05-01-the-right-way-to-read-perplexity.ko.png)

*perplexity를 올바르게 읽는 법*

## 단계별 설명

### 1단계 — 평가 함수를 작성합니다

```python
import math
import torch

def perplexity(model, dataset) -> float:
    losses = []
    model.eval()
    for row in dataset:
        batch = {key: torch.tensor([value]) for key, value in row.items()}
        with torch.no_grad():
            loss = model(**batch).loss
        losses.append(loss.item())
    return math.exp(sum(losses) / len(losses))
```

### 2단계 — 학습 전후를 측정합니다

```python
before = perplexity(peft_model, eval_dataset)
trainer.train()
after = perplexity(peft_model, eval_dataset)

delta = (after - before) / before * 100
print({"before_ppl": before, "after_ppl": after, "delta_pct": delta})
```

### 3단계 — 골든 세트를 정의합니다

```python
golden = [
    {"prompt": "Q: How to sort a Python list?", "expected_contains": "sorted"},
    {"prompt": "Q: What is HTTP 404?", "expected_contains": "not found"},
]
```

각 항목은 프롬프트와 기대 키워드의 쌍입니다. 작은 모델에서는 exact match보다 특정 핵심 단어가 포함되는지 보는 편이 더 현실적입니다.

### 4단계 — 골든 세트를 채점합니다

```python
def score_golden(model, tokenizer, golden) -> float:
    hits = 0
    for item in golden:
        ids = tokenizer(item["prompt"], return_tensors="pt").input_ids
        out = model.generate(ids, max_new_tokens=32)
        text = tokenizer.decode(out[0], skip_special_tokens=True)
        if item["expected_contains"] in text:
            hits += 1
    return hits / len(golden)
```

### 5단계 — 두 신호를 함께 출력합니다

```python
print({
    "ppl_after": after,
    "golden_score": score_golden(peft_model, tokenizer, golden),
})
```

이 두 줄이 한 화면에 함께 나오면, 빠른 정량 기준선과 사용자 관점 품질 신호를 동시에 볼 수 있게 됩니다.

## 이 코드에서 봐야 할 것

![평균 손실에서 perplexity로 가는 계산 흐름](../../../assets/llm-finetuning-101/05/05-03-what-to-notice-in-this-code.ko.png)

*평균 손실에서 perplexity로 가는 계산 흐름*

- 평가 함수는 학습 루프와 분리되어 있어야 합니다. 그렇지 않으면 손실을 읽는 동안 파라미터를 바꾸는 실수를 저지를 수 있습니다.
- `torch.no_grad()`와 `model.eval()`은 메모리 사용과 드롭아웃 동작을 안정화하는 가장 기본적인 보호장치입니다.
- 이 예제는 추세 확인용입니다. 실제 프로젝트에서는 hold-out 세트, 태스크 지표, 사람 검토가 함께 필요합니다.
- 골든 세트 채점은 사람이 모든 출력을 읽지 않아도 회귀를 잡을 수 있게 해 주는 가장 가벼운 자동화입니다.

## 자주 하는 실수

![과적합 신호와 비교 기준 판단 흐름](../../../assets/llm-finetuning-101/05/05-04-where-engineers-get-confused.ko.png)

*과적합 신호와 비교 기준 판단 흐름*

- **perplexity만 보고 배포를 결정하는 실수**: 형식 준수, 사실성, 안전성은 별도 평가가 필요합니다. perplexity는 한 축일 뿐입니다.
- **학습 데이터와 평가 데이터를 같게 쓰는 실수**: 숫자가 지나치게 낙관적으로 보입니다. 데모에서는 단순화를 위해 같게 쓸 수 있어도, 실제로는 반드시 분리해야 합니다.
- **골든 세트를 한 번 만들고 끝내는 실수**: 모델이 바뀌면 평가 항목도 함께 자라야 합니다. 매주 5~10개씩 추가하는 루틴이 유용합니다.
- **`model.eval()`을 빼먹는 실수**: 드롭아웃이 살아 있어 같은 입력에도 다른 출력이 나옵니다. 재현성이 무너집니다.
- **마지막 체크포인트만 평가하는 실수**: 언제부터 나빠졌는지 알 수 없습니다. `eval_steps`로 중간중간 측정해야 합니다.
- **CI에서 평가를 생략하는 실수**: 사람이 수동으로 돌리면 언젠가는 빠집니다. 5분짜리 perplexity 검사는 PR마다 돌릴 가치가 충분합니다.

## 실무 메모

- **두 단 구조를 유지합니다**: 빠른 perplexity 체크는 CI에서, 느린 골든 세트 평가는 nightly에서 함께 돌립니다.
- **회귀 허용폭을 정합니다**: perplexity가 5% 이상 나빠지면 PR을 막는 식의 기준이 실용적입니다.
- **골든 세트를 카테고리로 나눕니다**: 형식, 사실성, 안전성, 도메인 지식처럼 묶으면 약점이 더 빨리 드러납니다.
- **사람 평가는 페어 비교로 합니다**: 두 모델 출력을 나란히 놓고 어느 쪽이 더 나은지만 묻는 방식이 절대 점수보다 안정적입니다.
- **자동 평가는 어디까지나 보조선입니다**: BLEU, ROUGE, LLM-as-judge 모두 한계가 있습니다. 최종 판단은 사람 검토와 함께 가야 합니다.

## 체크리스트

- [ ] perplexity가 평균 손실의 지수값이라는 점을 이해했습니다.
- [ ] 평가 루프에서 `no_grad`와 `eval`을 쓰는 이유를 설명할 수 있습니다.
- [ ] `python main.py`를 실행해 학습 전후 perplexity 출력이 실제로 나오는지 확인했습니다.
- [ ] 골든 세트의 의미와 한계를 설명할 수 있습니다.
- [ ] 서빙 전에 최소한의 정량 평가를 수행하는 습관을 잡았습니다.

## 연습 문제

1. 평가 데이터셋을 2개에서 20개 항목으로 늘려 보세요. perplexity 분산이 줄어드나요?
2. 골든 세트에 수학 계산 항목 5개를 추가하고, 파인튜닝 전후 점수를 비교해 보세요. 모든 카테고리가 같은 폭으로 좋아지나요?
3. `model.eval()` 호출을 빼고 perplexity 함수를 두 번 실행해 보세요. 결과가 어떻게 달라지나요?

## 정리 · 다음 글

평가는 화려하지 않지만 파인튜닝 파이프라인의 신뢰를 만드는 단계입니다. 생성 예시를 보기 전에 기준선을 세워 두면 이후 실험이 감에 덜 의존하게 됩니다. 실무 패턴은 분명합니다. 아래에는 빠른 정량 신호인 perplexity를 두고, 위에는 느린 정성 평가인 골든 세트와 사람 검토를 둡니다.

다음 글인 6편에서는 서빙을 다룹니다. LoRA 어댑터를 베이스 모델과 분리한 채 배포하는 방법과, 추론 시 메모리와 지연 시간을 어떻게 다뤄야 하는지 보겠습니다.

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

- [예제 저장소 — llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101)
- [Perplexity of fixed-length models](https://huggingface.co/docs/transformers/perplexity)
- [Evaluation best practices for language models](https://huggingface.co/docs/evaluate/index)
- [LLM-as-a-judge survey](https://arxiv.org/abs/2306.05685)
- [HELM: Holistic Evaluation of Language Models](https://crfm.stanford.edu/helm/)

Tags: Fine-tuning, LoRA, LLM, Python

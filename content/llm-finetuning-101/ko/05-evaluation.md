---
title: '모델 평가'
series: llm-finetuning-101
episode: 5
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

# 모델 평가

## 이 글에서 답할 질문

- 파인튜닝 직후 가장 먼저 볼 정량 지표로 perplexity를 어떻게 계산할까?
- 학습 전후 perplexity 비교가 왜 완벽한 품질 평가가 아닌가?
- tiny 모델 데모에서도 평가 루프를 따로 두는 이유는 무엇일까?

> perplexity는 모델이 다음 토큰을 얼마나 덜 놀라며 예측하는지 보는 지표이지, 사람이 읽기 좋은 답변을 직접 보장하는 지표는 아닙니다.

예제 코드: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/ko/05-evaluation)

학습이 끝나면 곧바로 생성 결과만 보고 싶어집니다. 하지만 실무에서는 생성 예시보다 먼저 정량 지표를 봐야 합니다. 그중 가장 기본이 perplexity입니다. 이 값은 모델이 평가 데이터의 토큰을 얼마나 자연스럽게 예측하는지 보여줍니다.

예제 코드는 tiny GPT-2 + LoRA 모델을 1 step 학습한 뒤, 같은 형식의 평가 데이터셋에 대해 평균 loss를 구하고 `exp(loss)`로 perplexity를 계산합니다. 실행하면 학습 전과 후의 perplexity가 모두 출력되므로, 평가 루프가 분리되어 있는지 확인할 수 있습니다.

## perplexity를 해석하는 기본 태도

perplexity는 낮을수록 좋지만, 절대값만으로 품질을 단정하면 안 됩니다. 작은 데모 모델, 작은 데이터셋, 짧은 문맥에서는 값이 크게 튈 수 있습니다. 그래서 실무에서는 perplexity를 **회귀 방지용 기준선**으로 주로 씁니다. 학습 전보다 나빠졌는지, 설정을 바꿨을 때 추세가 개선되는지를 보는 데 강합니다.

![perplexity를 해석하는 기본 태도](../../../assets/llm-finetuning-101/05/05-01-the-right-way-to-read-perplexity.ko.png)
## 최소 실행 예제

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

before = perplexity(peft_model, eval_dataset)
trainer.train()
after = perplexity(peft_model, eval_dataset)
print(before, after)
```

## 이 코드에서 봐야 할 것

- 평가 함수는 학습 루프와 분리되어 있어야 합니다. 그렇지 않으면 loss를 보는 순간에도 파라미터가 바뀌는 실수를 하게 됩니다.
- `torch.no_grad()`와 `model.eval()`은 메모리 사용과 드롭아웃 동작을 안정화하는 기본 장치입니다.
- 이 글의 예제는 추세 확인용입니다. 실제 프로젝트에서는 hold-out set, task metric, human review가 함께 필요합니다.

## 실무에서 헷갈리는 지점

- perplexity가 좋아졌다고 서비스 품질이 무조건 좋아지는 것은 아닙니다. 포맷 준수나 사실성은 별도 평가가 필요합니다.
- 평가 데이터와 학습 데이터를 완전히 같게 쓰면 수치가 낙관적으로 보일 수 있습니다. 데모에서는 구조 이해를 위해 같게 썼습니다.
- tiny 모델에서 수치 차이가 작아 보여도 정상입니다. 1 step 데모의 목적은 평가 파이프라인 검증입니다.

## 체크리스트

- [ ] perplexity가 평균 loss의 지수값이라는 점을 이해했다.
- [ ] 평가 루프에서 `no_grad`와 `eval`을 사용하는 이유를 설명할 수 있다.
- [ ] `python main.py`로 학습 전후 perplexity 출력이 실제로 나오는지 확인했다.
- [ ] 서빙 전에 최소 정량 평가를 거치는 습관을 잡았다.

## 정리

평가는 화려하지 않지만 파인튜닝 파이프라인의 신뢰를 만드는 단계입니다. 생성 예시를 보기 전에 기준선을 만들면, 이후 실험이 훨씬 덜 감에 의존하게 됩니다.

<!-- blog-only:start -->
다음 글: [모델 서빙](./06-serving.md)
<!-- blog-only:end -->

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

- [Perplexity of fixed-length models](https://huggingface.co/docs/transformers/perplexity)
- [Evaluation best practices for language models](https://huggingface.co/docs/evaluate/index)

Tags: Fine-tuning, LoRA, LLM, Python

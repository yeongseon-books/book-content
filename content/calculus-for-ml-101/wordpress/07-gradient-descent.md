---
title: "바이브코딩을 위한 ML 미적분 (7/10): 경사하강법"
series: calculus-for-ml-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- 미적분
- 머신러닝
- 경사하강법
- 학습률
seo_description: "경사하강법의 작동 원리와 학습률 선택 기준을 이해합니다. SGD, Adam 등 optimizer 선택을 AI와 대화할 수 있는 수준으로 배웁니다."
---

# 바이브코딩을 위한 ML 미적분 (7/10): 경사하강법

이 글은 바이브코딩을 위한 ML 미적분 시리즈의 7번째 글입니다.

"학습률을 얼마로 설정해야 해요?"라고 AI에게 물으면 "0.001이나 0.01을 시작점으로 해보세요"라고 합니다. 그런데 왜 너무 크면 발산하고 너무 작으면 학습이 느린지 이해해야 더 나은 선택을 할 수 있습니다. 경사하강법의 수학적 원리가 그 이유를 설명합니다.

경사하강법은 간단합니다. 현재 파라미터에서 gradient를 계산하고, gradient의 반대 방향으로 학습률만큼 이동합니다. `파라미터 = 파라미터 - 학습률 × gradient`. 이 한 줄이 ML 학습의 핵심입니다.

학습률이 크면 큰 걸음으로 이동해 빠르지만 최솟값을 지나칠 수 있고, 학습률이 작으면 정밀하지만 느립니다. 이 트레이드오프를 이해하면 AI에게 "학습률 스케줄러는 어떤 걸 써야 해?"라고 구체적으로 물을 수 있습니다.

> 경사하강법: 파라미터 = 파라미터 - 학습률 × gradient. 손실 함수의 가장 가파른 하강 방향으로 이동합니다.

---

## 이 글에서 다룰 문제

- 경사하강법의 한 번 업데이트 수식은 무엇이고 왜 이렇게 동작할까요?
- 학습률이 너무 크거나 작을 때 어떤 현상이 나타날까요?
- SGD, Mini-batch SGD, Adam의 차이는 무엇일까요?
- 학습률 스케줄러를 사용하는 이유와 주요 전략은 무엇일까요?
- AI에게 optimizer 관련 질문을 어떻게 정확하게 할까요?

경사하강법은 ML 학습의 엔진입니다. 학습률, optimizer, 스케줄러 선택은 모두 이 원리 위에 있습니다. 이 이해가 있어야 AI에게 "왜 Adam이 SGD보다 대부분 더 잘 동작해?"라고 물을 수 있습니다.

## Before / After

**Before — optimizer를 기본값으로만 사용:**

```python
import torch.optim as optim
optimizer = optim.SGD(model.parameters(), lr=0.01)
# 왜 이 학습률인지, 왜 SGD인지 이해 없음
```

**After — 경사하강법 원리를 이해하고 optimizer 선택:**

```python
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR

# Adam: 각 파라미터별 적응적 학습률, 대부분 좋은 기본 선택
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)

# CosineAnnealing: 학습 후반에 학습률을 줄여 미세 조정
scheduler = CosineAnnealingLR(optimizer, T_max=100)

# AI에게: "Adam 대신 AdamW를 써야 할 때는 언제야?"
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 학습률 조정 없이 고정 사용 | 초반과 후반 학습 요구가 다름 | 학습률 스케줄러 적용 |
| SGD를 모든 문제에 사용 | 수렴이 느리고 학습률 선택 민감 | Adam을 기본값으로 시작 |
| 너무 큰 학습률로 시작 | loss가 발산하거나 NaN 발생 | 1e-3에서 시작해 loss 보며 조정 |
| optimizer.zero_grad() 생략 | gradient가 누적되어 틀린 업데이트 | 매 batch마다 zero_grad() 호출 |
| 학습률과 batch size 연관성 무시 | batch size 변경 시 성능 저하 | batch size 증가 시 학습률도 비례 조정 |

## AI 협업 팁

경사하강법/optimizer AI 질문 패턴:

1. **optimizer 선택**: "이 NLP 태스크에 Adam vs AdamW 중 뭐가 더 나을까?"
2. **학습률 진단**: "loss가 발산해. 학습률 문제인지 어떻게 확인해?"
3. **스케줄러 선택**: "CosineAnnealing과 ReduceLROnPlateau 중 어떤 게 더 나은지 이유는?"

예시 프롬프트:
> "학습 초반에 loss가 빠르게 줄다가 특정 지점에서 수렴이 멈춰. 학습률 스케줄러로 개선할 수 있는지, 어떤 전략이 좋은지 알려줘."

## 운영 체크리스트

- [ ] 경사하강법 업데이트 수식(θ = θ - α∇L)을 이해하는가?
- [ ] 학습률이 크거나 작을 때 나타나는 현상을 설명할 수 있는가?
- [ ] SGD와 Adam의 차이를 이해하고 상황에 맞게 선택할 수 있는가?
- [ ] 학습률 스케줄러의 필요성과 주요 전략(StepLR, CosineAnnealing)을 아는가?
- [ ] optimizer.zero_grad()를 매 batch마다 호출하는가?

## 처음 질문으로 돌아가기

"학습률을 얼마로 설정해야 해요?"라는 질문에서 출발해, "학습 초반에 빠른 수렴을 위해 높은 학습률로 시작하고 후반에 CosineAnnealing으로 서서히 줄이면 어떨까요?"라고 AI에게 제안할 수 있게 됩니다. 경사하강법의 원리가 이 제안을 가능하게 합니다.

## 정리

경사하강법은 gradient의 반대 방향으로 학습률만큼 파라미터를 업데이트합니다. 학습률은 이동 보폭이며, 너무 크면 발산하고 너무 작으면 느립니다. Adam 같은 적응적 optimizer와 학습률 스케줄러는 이 트레이드오프를 개선합니다.

다음 글에서는 최적화를 다룹니다. 경사하강법이 실패하는 local minimum, saddle point, plateau 문제와 해결 전략을 배웁니다.

## 참고 자료

### 공식 문서
- [PyTorch optimizer](https://pytorch.org/docs/stable/optim.html)
- [PyTorch lr_scheduler](https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 ML 미적분 (1/10): 미분이란 무엇인가
- 바이브코딩을 위한 ML 미적분 (2/10): 함수와 기울기
- 바이브코딩을 위한 ML 미적분 (3/10): 편미분
- 바이브코딩을 위한 ML 미적분 (4/10): Gradient
- 바이브코딩을 위한 ML 미적분 (5/10): 연쇄 법칙
- 바이브코딩을 위한 ML 미적분 (6/10): 손실 함수
- **바이브코딩을 위한 ML 미적분 (7/10): 경사하강법 (현재 글)**
- 바이브코딩을 위한 ML 미적분 (8/10): 최적화
- 바이브코딩을 위한 ML 미적분 (9/10): 역전파 직관
- 바이브코딩을 위한 ML 미적분 (10/10): 딥러닝에서의 미분
<!-- toc:end -->

Tags: 바이브코딩, 미적분, 머신러닝, 경사하강법, 학습률

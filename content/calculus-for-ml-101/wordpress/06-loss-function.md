---
title: "바이브코딩을 위한 ML 미적분 (6/10): 손실 함수"
series: calculus-for-ml-101
episode: 6
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- 미적분
- 머신러닝
- 손실함수
- MSE
seo_description: "손실 함수의 수학적 구조를 이해하고 적절한 손실 함수를 선택하는 기준을 배웁니다. AI에게 손실 함수 관련 질문을 정확하게 하는 법을 익힙니다."
---

# 바이브코딩을 위한 ML 미적분 (6/10): 손실 함수

이 글은 바이브코딩을 위한 ML 미적분 시리즈의 6번째 글입니다.

"손실 함수로 뭘 써야 해요?"라고 AI에게 물으면 "회귀에는 MSE, 분류에는 CrossEntropy"라는 답이 나옵니다. 그런데 "왜 분류에서 MSE를 쓰면 안 되나요?"라고 물을 수 있어야 합니다. 손실 함수의 수학적 구조를 이해하면 이 질문이 가능합니다.

손실 함수는 모델 예측과 실제 정답의 차이를 하나의 숫자로 표현합니다. ML에서 학습은 이 숫자를 최소화하는 파라미터를 찾는 과정입니다. 손실 함수의 형태는 gradient의 모양을 결정하고, gradient의 모양은 학습의 동작을 결정합니다.

MSE(Mean Squared Error)는 매끄러운 볼록 함수로 gradient descent가 전역 최솟값으로 수렴합니다. CrossEntropy는 확률 분포의 차이를 측정해 분류 문제에 더 적합한 gradient 신호를 제공합니다. 이 차이를 이해하면 AI에게 더 정확한 질문을 할 수 있습니다.

> 손실 함수는 모델이 얼마나 틀렸는지를 하나의 숫자로 표현합니다. 이 함수의 형태가 gradient descent의 경로를 결정합니다.

---

## 이 글에서 다룰 문제

- MSE와 CrossEntropy의 수학적 차이는 무엇일까요?
- 왜 분류 문제에 MSE를 쓰면 좋지 않을까요?
- 손실 함수 선택이 gradient 형태에 어떤 영향을 미칠까요?
- 커스텀 손실 함수를 만들 때 어떤 조건을 갖춰야 할까요?
- AI에게 손실 함수 관련 질문을 어떻게 구체적으로 할까요?

손실 함수 선택은 모델 성능에 직접적인 영향을 미칩니다. 잘못된 손실 함수를 사용하면 학습이 수렴하지 않거나, 틀린 목표를 최적화할 수 있습니다. 손실 함수의 수학적 구조를 이해하면 AI에게 "이 문제에 어떤 손실 함수가 적합해?"라고 정확하게 물을 수 있습니다.

## Before / After

**Before — 손실 함수를 구분 없이 사용:**

```python
# 분류 문제에 MSE 사용 — 나쁜 선택
import torch.nn as nn

criterion = nn.MSELoss()  # 이진 분류에 MSE?
# gradient가 작고 느린 학습, 확률 해석 불가
```

**After — 문제 유형에 맞는 손실 함수 선택:**

```python
import torch.nn as nn

# 이진 분류: BCEWithLogitsLoss (수치 안정성 포함)
binary_criterion = nn.BCEWithLogitsLoss()

# 다중 분류: CrossEntropyLoss
multi_criterion = nn.CrossEntropyLoss()

# 회귀: MSELoss 또는 smooth L1
regression_criterion = nn.MSELoss()

# AI에게: "이 문제에서 BCELoss 대신 BCEWithLogitsLoss를 써야 하는 이유가 뭐야?"
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 분류에 MSE 사용 | 느린 gradient, 확률 해석 불가 | CrossEntropyLoss 사용 |
| BCELoss와 BCEWithLogitsLoss 혼동 | 수치 불안정 또는 이중 sigmoid | BCEWithLogitsLoss는 sigmoid 포함임 인지 |
| 불균형 데이터에서 기본 CrossEntropy | 소수 클래스 무시 | class_weight 파라미터 설정 |
| 손실 함수 스케일 무시 | 학습률 조정 어려움 | loss.item() 범위 확인 |
| 커스텀 손실에서 미분 불가능 지점 | gradient 계산 오류 | 미분 가능한 연산만 사용 |

## AI 협업 팁

손실 함수 AI 질문 패턴:

1. **선택 이유 질문**: "이 문제에 CrossEntropy가 MSE보다 나은 이유는?"
2. **수치 안정성 질문**: "BCELoss와 BCEWithLogitsLoss의 차이는?"
3. **커스텀 손실 요청**: "Focal Loss를 PyTorch로 구현해줘"

예시 프롬프트:
> "이진 분류 문제에서 positive class가 전체의 5%밖에 없어. 클래스 불균형을 처리하는 손실 함수와 구현 방법을 알려줘."

## 운영 체크리스트

- [ ] 회귀에는 MSE, 이진 분류에는 BCEWithLogitsLoss, 다중 분류에는 CrossEntropyLoss를 사용하는가?
- [ ] 손실 함수의 출력 범위를 확인하고 학습률을 조정했는가?
- [ ] 클래스 불균형이 있는 경우 가중 손실 함수를 사용하는가?
- [ ] 커스텀 손실 함수가 미분 가능한지 확인했는가?
- [ ] AI에게 손실 함수 선택 이유를 질문하고 이해하는가?

## 처음 질문으로 돌아가기

"이 분류 문제에 어떤 손실 함수를 써야 해요?"라는 질문에서 "왜 CrossEntropy가 분류에 더 적합한지"를 이해하면, AI의 답변을 단순히 따르는 것이 아니라 검증하고 더 나은 선택을 할 수 있습니다.

## 정리

손실 함수는 모델 학습의 목표를 정의합니다. 문제 유형에 맞는 손실 함수를 선택하는 것이 학습 성공의 첫 번째 조건입니다. 손실 함수의 수학적 구조를 이해하면 AI와 더 정확한 대화를 할 수 있습니다.

다음 글에서는 경사하강법을 다룹니다. 손실 함수를 최소화하기 위해 gradient를 어떻게 사용하는지, 학습률이 어떤 역할을 하는지 배웁니다.

## 참고 자료

### 공식 문서
- [PyTorch 손실 함수](https://pytorch.org/docs/stable/nn.html#loss-functions)
- [Scikit-learn 손실 함수](https://scikit-learn.org/stable/modules/model_evaluation.html)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 ML 미적분 (1/10): 미분이란 무엇인가
- 바이브코딩을 위한 ML 미적분 (2/10): 함수와 기울기
- 바이브코딩을 위한 ML 미적분 (3/10): 편미분
- 바이브코딩을 위한 ML 미적분 (4/10): Gradient
- 바이브코딩을 위한 ML 미적분 (5/10): 연쇄 법칙
- **바이브코딩을 위한 ML 미적분 (6/10): 손실 함수 (현재 글)**
- 바이브코딩을 위한 ML 미적분 (7/10): 경사하강법
- 바이브코딩을 위한 ML 미적분 (8/10): 최적화
- 바이브코딩을 위한 ML 미적분 (9/10): 역전파 직관
- 바이브코딩을 위한 ML 미적분 (10/10): 딥러닝에서의 미분
<!-- toc:end -->

Tags: 바이브코딩, 미적분, 머신러닝, 손실함수, MSE

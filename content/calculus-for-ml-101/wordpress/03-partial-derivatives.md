---
title: "바이브코딩을 위한 ML 미적분 (3/10): 편미분"
series: calculus-for-ml-101
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- 미적분
- 머신러닝
- 편미분
- 파라미터
seo_description: "편미분의 직관을 ML 파라미터 업데이트 관점에서 이해합니다. 여러 파라미터가 있을 때 각각의 영향을 분리해 측정하는 법을 배웁니다."
---

# 바이브코딩을 위한 ML 미적분 (3/10): 편미분

이 글은 바이브코딩을 위한 ML 미적분 시리즈의 3번째 글입니다.

실제 ML 모델은 파라미터가 수백만 개입니다. 그 중 하나를 바꿨을 때 손실이 어떻게 변하는지 알아야 그 파라미터를 어떤 방향으로 업데이트할지 결정할 수 있습니다. 편미분은 "다른 변수들은 고정하고, 하나의 변수만 변화시켰을 때 함수가 어떻게 반응하는가"를 측정합니다.

바이브코딩에서 AI에게 "왜 gradient를 각 파라미터마다 따로 계산해요?"라고 물을 수 있으면, "편미분을 사용해서 각 파라미터가 손실에 미치는 독립적인 영향을 측정하기 때문"이라는 답을 이해할 수 있습니다. 역전파는 결국 편미분의 효율적인 계산 방법입니다.

> 편미분은 다른 변수를 모두 상수로 고정하고 하나의 변수에 대해서만 미분합니다. ML에서 이것이 각 파라미터의 gradient를 계산하는 방법입니다.

---

## 이 글에서 다룰 문제

- 편미분이 일반 미분과 어떻게 다를까요?
- ML에서 편미분이 각 파라미터 업데이트에 어떻게 사용될까요?
- gradient가 편미분의 집합임을 어떻게 이해할 수 있을까요?
- AutoDiff가 편미분을 자동으로 계산하는 원리는 무엇일까요?
- 편미분을 이해하면 역전파를 어떻게 더 잘 이해할 수 있을까요?

ML 모델의 파라미터 업데이트는 각 파라미터에 대한 손실 함수의 편미분을 계산하는 것입니다. AutoDiff(자동 미분)는 이 편미분들을 효율적으로 계산합니다. 편미분을 이해하면 AutoDiff의 동작 원리와 역전파의 구조를 자연스럽게 이해할 수 있습니다.

## Before / After

**Before — AutoDiff를 블랙박스로 사용:**

```python
import torch

x = torch.tensor(2.0, requires_grad=True)
y = torch.tensor(3.0, requires_grad=True)
z = x**2 + x*y + y**2

z.backward()
# x.grad와 y.grad가 나오는데 이게 뭔지 모름
print(x.grad)  # ?
print(y.grad)  # ?
```

**After — 편미분을 이해하고 AutoDiff 결과 검증:**

```python
import torch

x = torch.tensor(2.0, requires_grad=True)
y = torch.tensor(3.0, requires_grad=True)
z = x**2 + x*y + y**2

z.backward()

# ∂z/∂x = 2x + y = 2(2) + 3 = 7
print(x.grad)  # tensor(7.) — 예상값과 일치!
# ∂z/∂y = x + 2y = 2 + 2(3) = 8
print(y.grad)  # tensor(8.) — 예상값과 일치!
# AI에게 "이 gradient가 맞게 계산됐어?"라고 물어볼 수 있음
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| AutoDiff 결과를 검증 없이 믿음 | 버그가 있어도 모름 | 간단한 함수에서 수동 편미분과 비교 |
| gradient를 하나의 숫자로만 봄 | 방향 정보 손실 | gradient는 각 파라미터별 편미분 벡터임을 인식 |
| requires_grad 설정 실수 | gradient 계산 안 됨 | 학습할 파라미터에 requires_grad=True 확인 |
| gradient 누적 문제 | 이전 gradient가 더해져 틀린 업데이트 | optimizer.zero_grad() 필수 호출 확인 |
| 편미분과 전체 미분 혼동 | 다변수 함수 이해 오류 | "다른 변수 고정" 조건 항상 인식 |

## AI 협업 팁

편미분 관련 AI 질문 패턴:

1. **gradient 검증**: "f(x,y) = x² + xy에서 x=2, y=3일 때 각 편미분값은?"
2. **AutoDiff 원리 질문**: "PyTorch에서 backward()가 편미분을 어떻게 계산해?"
3. **실무 연결**: "이 파라미터의 gradient가 0이야. 뭐가 문제일 수 있어?"

예시 프롬프트:
> "z = x² + 2xy + y²에서 x=1, y=2일 때 ∂z/∂x와 ∂z/∂y를 계산하고, PyTorch로 검증하는 코드를 만들어줘."

## 운영 체크리스트

- [ ] 편미분이 "다른 변수를 고정하고 하나만 변화"시키는 것임을 이해하는가?
- [ ] gradient가 편미분의 벡터임을 설명할 수 있는가?
- [ ] PyTorch에서 requires_grad와 backward()의 역할을 이해하는가?
- [ ] optimizer.zero_grad()가 왜 필요한지 이해하는가?
- [ ] AutoDiff 결과를 수동 편미분으로 검증할 수 있는가?

## 처음 질문으로 돌아가기

"역전파가 뭐야?"라는 질문에 AI가 "편미분의 연쇄 규칙을 역방향으로 계산하는 것"이라고 답할 때, 편미분을 이해한 사람은 그 답이 무슨 뜻인지 알 수 있습니다. 편미분은 ML의 핵심인 파라미터 업데이트를 이해하는 수학적 기반입니다.

## 정리

편미분은 여러 변수가 있는 함수에서 하나의 변수가 함수 출력에 미치는 영향을 독립적으로 측정합니다. ML에서 gradient는 모든 파라미터에 대한 편미분의 집합이며, 역전파는 이 편미분들을 효율적으로 계산하는 알고리즘입니다.

다음 글에서는 Gradient를 다룹니다. 편미분들의 집합인 gradient가 경사하강법에서 어떻게 사용되는지 배웁니다.

## 참고 자료

### 공식 문서
- [PyTorch autograd 튜토리얼](https://pytorch.org/tutorials/beginner/blitz/autograd_tutorial.html)
- [NumPy gradient](https://numpy.org/doc/stable/reference/generated/numpy.gradient.html)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 ML 미적분 (1/10): 미분이란 무엇인가
- 바이브코딩을 위한 ML 미적분 (2/10): 함수와 기울기
- **바이브코딩을 위한 ML 미적분 (3/10): 편미분 (현재 글)**
- 바이브코딩을 위한 ML 미적분 (4/10): Gradient
- 바이브코딩을 위한 ML 미적분 (5/10): 연쇄 법칙
- 바이브코딩을 위한 ML 미적분 (6/10): 손실 함수
- 바이브코딩을 위한 ML 미적분 (7/10): 경사하강법
- 바이브코딩을 위한 ML 미적분 (8/10): 최적화
- 바이브코딩을 위한 ML 미적분 (9/10): 역전파 직관
- 바이브코딩을 위한 ML 미적분 (10/10): 딥러닝에서의 미분
<!-- toc:end -->

Tags: 바이브코딩, 미적분, 머신러닝, 편미분, 파라미터

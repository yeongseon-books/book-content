---
title: "바이브코딩을 위한 ML 미적분 (5/10): 연쇄 법칙"
series: calculus-for-ml-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- 미적분
- 머신러닝
- 연쇄법칙
- 역전파
seo_description: "연쇄 법칙이 역전파의 수학적 기반임을 이해합니다. 합성 함수의 미분을 AI 협업 관점에서 배웁니다."
---

# 바이브코딩을 위한 ML 미적분 (5/10): 연쇄 법칙

이 글은 바이브코딩을 위한 ML 미적분 시리즈의 5번째 글입니다.

"역전파(backpropagation)가 어떻게 작동해요?"라고 AI에게 물으면, "연쇄 법칙을 역방향으로 적용합니다"라는 답이 나옵니다. 그 답을 이해하려면 연쇄 법칙이 무엇인지 알아야 합니다.

연쇄 법칙은 합성 함수의 미분 규칙입니다. f(g(x))를 미분하면 f'(g(x)) × g'(x)가 됩니다. 딥러닝 모델은 수십 층의 연산이 합성된 거대한 합성 함수입니다. 역전파는 이 합성 함수의 gradient를 연쇄 법칙으로 출력층에서 입력층 방향으로 역으로 계산합니다.

연쇄 법칙을 이해하면 "왜 역전파가 깊은 층에서 gradient vanishing이 생기는가"를 설명할 수 있습니다. 0.9 × 0.9 × 0.9 × ... 를 여러 번 곱하면 0에 가까워지듯, 기울기가 1보다 작은 값들을 연속으로 곱하면 gradient가 소멸합니다.

> 연쇄 법칙: 합성 함수 f(g(x))의 미분은 f'(g(x)) × g'(x)입니다. 역전파는 이 규칙을 층 순서의 역방향으로 적용합니다.

---

## 이 글에서 다룰 문제

- 연쇄 법칙이 합성 함수의 미분에서 왜 필요할까요?
- 역전파가 연쇄 법칙을 어떻게 활용하는지 직관적으로 이해할 수 있을까요?
- 연쇄 법칙으로 gradient vanishing을 어떻게 설명할 수 있을까요?
- PyTorch의 computational graph가 연쇄 법칙과 어떻게 연결될까요?
- 바이브코딩에서 역전파 문제를 AI에게 어떻게 설명할까요?

역전파는 연쇄 법칙의 구현입니다. 이 연결을 이해하면 AI에게 "왜 이 층에서 gradient가 소멸하나요?"라고 물었을 때, "각 층의 gradient를 곱해나가는 과정에서 0.5보다 작은 값들이 연속으로 곱해지기 때문"이라는 답을 이해할 수 있습니다.

## Before / After

**Before — 역전파를 블랙박스로 사용:**

```python
loss = criterion(output, target)
loss.backward()  # 이게 어떻게 동작하는지 모름
optimizer.step()
```

**After — 연쇄 법칙으로 역전파 원리 이해:**

```python
import torch

# 간단한 2층 합성 함수의 gradient 수동 계산
x = torch.tensor(2.0, requires_grad=True)
# z = (x^2 + 1)^3
# 연쇄 법칙: dz/dx = 3*(x^2+1)^2 * 2x = 3*(4+1)^2 * 4 = 300
z = (x**2 + 1)**3
z.backward()
print(x.grad)  # tensor(300.) — 연쇄 법칙으로 수동 계산한 값과 일치!

# AI에게: "이 backward() 결과가 연쇄 법칙으로 계산하면 맞아요?"
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 역전파를 완전한 블랙박스로 취급 | gradient 문제 원인 파악 불가 | 연쇄 법칙으로 간단한 예시 수동 계산 |
| gradient vanishing 원인을 모름 | 활성화 함수 선택 오류 | sigmoid의 기울기 범위(0~0.25) 이해 |
| computational graph 개념 부재 | gradient 계산 오류 디버깅 불가 | detach()와 requires_grad 사용 이해 |
| 연쇄 법칙을 공식만 외움 | 새로운 층 구조 이해 불가 | "곱셈의 연쇄" 직관 우선 |
| backward() 후 graph 유지 시도 | 메모리 오류 | retain_graph=True 사용 조건 이해 |

## AI 협업 팁

연쇄 법칙/역전파 AI 질문 패턴:

1. **원리 확인**: "이 2층 모델에서 역전파가 어떤 순서로 gradient를 계산해?"
2. **문제 진단**: "이 층에서 gradient가 소멸하는 이유를 연쇄 법칙으로 설명해줘"
3. **개선 방법**: "gradient vanishing을 막기 위해 어떤 활성화 함수를 써야 해?"

예시 프롬프트:
> "f(x) = sigmoid(3x + 1)에서 x=0.5일 때 df/dx를 연쇄 법칙으로 계산하고 PyTorch로 검증해줘. sigmoid의 기울기가 작아서 gradient vanishing이 생기는 이유도 설명해줘."

## 운영 체크리스트

- [ ] 연쇄 법칙 f'(g(x)) × g'(x)를 직관적으로 설명할 수 있는가?
- [ ] 역전파가 연쇄 법칙을 역방향으로 적용하는 것임을 이해하는가?
- [ ] sigmoid 활성화 함수에서 gradient vanishing이 생기는 이유를 설명할 수 있는가?
- [ ] PyTorch에서 computational graph가 어떻게 형성되는지 아는가?
- [ ] AI에게 "이 층에서 gradient가 소멸하는 이유"를 질문할 수 있는가?

## 처음 질문으로 돌아가기

역전파가 왜 작동하는지 이해하면, "왜 sigmoid 활성화 함수를 깊은 네트워크에서 피해야 하나요?"라는 질문에 "연쇄 법칙으로 gradient를 곱해나갈 때 sigmoid의 기울기(최대 0.25)가 여러 층에 걸쳐 곱해지면 0에 수렴하기 때문"이라고 AI에게 설명할 수 있습니다.

## 정리

연쇄 법칙은 합성 함수의 미분 규칙이며, 역전파는 이를 딥러닝 네트워크에 역방향으로 적용합니다. gradient vanishing은 연쇄 법칙에서 작은 기울기들이 연속으로 곱해지는 현상으로 설명됩니다. 바이브코딩에서 이 이해를 갖추면 AI와 역전파 문제를 정확하게 논의할 수 있습니다.

다음 글에서는 손실 함수를 다룹니다. ML의 학습 목표인 손실 함수가 어떤 형태를 가지며, gradient descent가 어떻게 이를 최소화하는지 배웁니다.

## 참고 자료

### 공식 문서
- [PyTorch autograd mechanics](https://pytorch.org/docs/stable/notes/autograd.html)
- [PyTorch computational graph](https://pytorch.org/docs/stable/autograd.html#tensor-autograd-functions)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 ML 미적분 (1/10): 미분이란 무엇인가
- 바이브코딩을 위한 ML 미적분 (2/10): 함수와 기울기
- 바이브코딩을 위한 ML 미적분 (3/10): 편미분
- 바이브코딩을 위한 ML 미적분 (4/10): Gradient
- **바이브코딩을 위한 ML 미적분 (5/10): 연쇄 법칙 (현재 글)**
- 바이브코딩을 위한 ML 미적분 (6/10): 손실 함수
- 바이브코딩을 위한 ML 미적분 (7/10): 경사하강법
- 바이브코딩을 위한 ML 미적분 (8/10): 최적화
- 바이브코딩을 위한 ML 미적분 (9/10): 역전파 직관
- 바이브코딩을 위한 ML 미적분 (10/10): 딥러닝에서의 미분
<!-- toc:end -->

Tags: 바이브코딩, 미적분, 머신러닝, 연쇄법칙, 역전파

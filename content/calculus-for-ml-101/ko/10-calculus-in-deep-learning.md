---
series: calculus-for-ml-101
episode: 10
title: 딥러닝에서의 미분
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Calculus
  - ML
  - DeepLearning
  - Capstone
  - Beginner
seo_description: 신경망, 손실, 옵티마이저, 역전파, 미분이 딥러닝 학습 루프에서 결합되는 방식을 정리한 글
last_reviewed: '2026-05-11'
---

# 딥러닝에서의 미분

딥러닝 학습 루프는 순전파, 손실 계산, 역전파, 업데이트를 하나의 반복으로 묶고 그 중심에 미분을 둡니다.

이 글은 Calculus for ML 101 시리즈의 10번째 글입니다.

## 이 글에서 다룰 문제

- 지금까지 배운 미분 개념은 딥러닝 학습 루프에서 어떻게 합쳐질까요?
- 순전파, 손실 계산, 역전파, 업데이트는 어떤 순서로 연결될까요?
- 프레임워크를 블랙박스로만 보면 무엇을 놓치게 될까요?
- 학습 루프의 핵심 뼈대를 직접 구현하면 무엇이 보일까요?

> 딥러닝 학습은 순전파로 예측을 만들고, 손실로 오차를 재고, 역전파로 gradient를 구한 뒤, optimizer로 파라미터를 갱신하는 반복입니다. 이 네 단계의 중심에 미분이 있습니다.

> Calculus for ML 101 시리즈 (10/10)

## 이 글에서 배울 것

- 학습 루프의 5단계를 한 흐름으로 봅니다.
- 순전파와 손실 계산의 역할을 정리합니다.
- 역전파와 업데이트가 어디서 연결되는지 이해합니다.
- 시리즈 전체 개념이 하나의 루프로 묶이는 모습을 봅니다.

## 왜 중요한가

이 글은 시리즈의 마무리입니다. 개별 개념을 따로 이해하는 것도 중요하지만, 실제 딥러닝에서는 그 개념들이 한 루프 안에서 동시에 작동합니다. 이 골격을 이해해야 프레임워크가 숨기는 부분과 드러내는 부분을 구분할 수 있습니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    F[순전파] --> L[손실]
    L --> B[역전파]
    B --> U[업데이트]
    U --> F
```

## 핵심 용어

- **순전파**: 입력으로부터 예측을 계산하는 단계입니다.
- **손실**: 예측과 정답의 차이를 재는 수치입니다.
- **역전파**: 손실을 각 파라미터의 gradient로 분해하는 단계입니다.
- **업데이트**: gradient를 사용해 가중치를 조정하는 단계입니다.
- **epoch**: 전체 데이터를 한 번 모두 도는 주기입니다.

## Before / After

**Before**: 프레임워크가 알아서 학습한다고만 생각합니다.

**After**: 각 단계가 왜 필요한지, 어디서 미분이 쓰이는지 설명할 수 있습니다.

## 단계별 실습: 미니 학습 루프

### Step 1 — 모델

```python
import math

def model(x, w, b):
    return sigmoid(w * x + b)

def sigmoid(z):
    return 1 / (1 + math.exp(-z))
```

아주 작은 이진 분류 모델입니다. 입력 x와 파라미터 w, b로 예측 확률을 만듭니다.

### Step 2 — 손실 (BCE)

```python
def bce(y, p, eps=1e-7):
    return -(y * math.log(p + eps) + (1 - y) * math.log(1 - p + eps))
```

예측이 정답과 얼마나 다른지 숫자로 측정합니다. 여기서부터 미분이 학습 신호를 만들기 시작합니다.

### Step 3 — 기울기 (해석)

```python
def grads(x, y, w, b):
    p = model(x, w, b)
    err = p - y
    return err * x, err
```

손실을 w와 b에 대해 미분한 결과를 직접 씁니다. 실제 프레임워크는 이런 계산을 자동으로 처리합니다.

### Step 4 — 한 스텝 갱신

```python
def step(x, y, w, b, lr=0.1):
    dw, db = grads(x, y, w, b)
    return w - lr * dw, b - lr * db
```

gradient의 반대 방향으로 가중치를 한 번 업데이트합니다.

### Step 5 — 학습 루프

```python
def train(data, epochs=100, lr=0.1):
    w, b = 0.0, 0.0
    for _ in range(epochs):
        for x, y in data:
            w, b = step(x, y, w, b, lr)
    return w, b
```

이 반복이 바로 학습입니다. 예측, 손실, gradient, 업데이트가 계속 이어집니다.

## 이 코드에서 주목할 점

- 순전파는 예측을 만듭니다.
- 손실은 얼마나 틀렸는지 측정합니다.
- 역전파는 책임을 gradient로 나눕니다.
- optimizer 업데이트가 실제 파라미터 변화를 만듭니다.
- 반복 자체가 학습의 본체입니다.

## 자주 하는 실수 5가지

1. 학습률 조정을 뒤로 미뤄 전체 학습을 불안정하게 만듭니다.
2. zero_grad 위치를 잘못 잡아 gradient를 누적시킵니다.
3. 평가 단계에서도 gradient를 계산해 메모리를 낭비합니다.
4. train/eval 모드를 섞어 Dropout, BatchNorm 동작을 틀리게 만듭니다.
5. 재현성을 위한 시드와 로그를 남기지 않습니다.

## 실무에서는 이렇게 생각합니다

이미지 분류, 언어 모델, 추천 시스템, 강화학습은 겉모습은 달라도 공통 학습 골격은 거의 같습니다. 달라지는 것은 모델 구조와 손실, optimizer 선택이지만, 그 중심에는 항상 미분과 gradient가 있습니다. 결국 프레임워크를 잘 쓰는 사람은 추상화 뒤의 루프를 머릿속에 그리고 있습니다.

## 체크리스트

- [ ] 순전파가 어떤 예측을 만드는지 설명할 수 있습니다.
- [ ] 손실 함수가 문제 정의와 연결된다는 점을 이해했습니다.
- [ ] backward가 gradient를 만든다는 흐름을 알고 있습니다.
- [ ] optimizer step이 실제 업데이트라는 점을 확인했습니다.
- [ ] 학습 루프 전체를 한 사이클로 설명할 수 있습니다.

## 정리 및 마무리

이 시리즈에서 본 미분, 편미분, gradient, 손실, 경사하강법, 최적화, 역전파는 따로 떨어진 개념이 아닙니다. 모두 딥러닝 학습 루프 안에서 한 번에 작동합니다. 딥러닝이 학습한다는 말의 수학적 핵심은 결국 손실을 미분해 더 나은 방향으로 반복해서 이동한다는 뜻입니다.

<!-- toc:begin -->
- [미분이란 무엇인가](./01-what-is-derivative.md)
- [함수와 기울기](./02-functions-and-slope.md)
- [편미분](./03-partial-derivatives.md)
- [Gradient](./04-gradient.md)
- [연쇄 법칙](./05-chain-rule.md)
- [손실 함수](./06-loss-function.md)
- [경사하강법](./07-gradient-descent.md)
- [최적화](./08-optimization.md)
- [역전파 직관](./09-backpropagation-intuition.md)
- **딥러닝에서의 미분 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Deep Learning Book - Goodfellow et al.](https://www.deeplearningbook.org/)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [CS231n - Convolutional Neural Networks](https://cs231n.stanford.edu/)
- [Reproducibility - PyTorch](https://pytorch.org/docs/stable/notes/randomness.html)

Tags: Calculus, ML, DeepLearning, Capstone, Beginner

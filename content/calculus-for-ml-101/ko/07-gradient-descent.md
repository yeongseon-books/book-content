---
series: calculus-for-ml-101
episode: 7
title: 경사하강법
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
  - GradientDescent
  - Optimization
  - Beginner
seo_description: 경사하강법, 학습률, 수렴, 발산, 확률적 경사하강 직관을 ML 입문자 관점에서 정리한 글
last_reviewed: '2026-05-04'
---

# 경사하강법

> Calculus for ML 101 시리즈 (7/10)


## 이 글에서 다룰 문제

*ML 학습* 의 *대부분* 은 *경사하강* 의 *변형* 입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    W[Weights] --> G[Gradient]
    G --> S[Step]
    S --> W
    W --> L[Loss decrease]
```

## Before/After

**Before**: *그리드 탐색* 으로 *모든 조합* 시도.

**After**: *기울기* 따라 *효율적* 으로 이동.

## 실습: 미니 GD 키트

### 1단계 — 손실과 기울기

```python
def loss(w):
    return (w - 3) ** 2

def grad(w):
    return 2 * (w - 3)
```

### 2단계 — GD 한 스텝

```python
def step(w, lr=0.1):
    return w - lr * grad(w)
```

### 3단계 — 학습 루프

```python
def train(w0, lr=0.1, steps=100):
    w = w0
    for _ in range(steps):
        w = step(w, lr)
    return w
```

### 4단계 — SGD

```python
import random

def sgd(data, w0, lr=0.01, epochs=10):
    w = w0
    for _ in range(epochs):
        random.shuffle(data)
        for x in data:
            w -= lr * 2 * (w - x)
    return w
```

### 5단계 — 학습률 영향

```python
for lr in [0.001, 0.1, 1.5]:
    print(lr, train(0.0, lr, 50))
```

## 이 코드에서 주목할 점

- *반대 부호* 한 걸음.
- *학습률* 이 *결정적*.
- *SGD* 는 *노이즈* 동반.

## 자주 하는 실수 5가지

1. ***학습률* 을 *지나치게 크게* 설정.**
2. ***스케일* 다른 가중치 동일 학습률.**
3. ***수렴* 이전 *조기 종료*.**
4. ***SGD* 의 *노이즈* 무시.**
5. ***초기화* 를 *0* 으로만.**

## 실무에서는 이렇게 쓰입니다

*Adam*, *Momentum*, *RMSProp* 모두 *경사하강* 의 *개량형* 입니다.

## 체크리스트

- [ ] *학습률* 탐색.
- [ ] *수렴* 모니터링.
- [ ] *발산* 시 *조기 중단*.
- [ ] *초기화* 다양화.

## 정리 및 다음 단계

다음 글은 *최적화* 입니다.

<!-- toc:begin -->
- [미분이란 무엇인가](./01-what-is-derivative.md)
- [함수와 기울기](./02-functions-and-slope.md)
- [편미분](./03-partial-derivatives.md)
- [Gradient](./04-gradient.md)
- [연쇄 법칙](./05-chain-rule.md)
- [손실 함수](./06-loss-function.md)
- **경사하강법 (현재 글)**
- 최적화 (예정)
- 역전파 직관 (예정)
- 딥러닝에서의 미분 (예정)
<!-- toc:end -->

## 참고 자료

- [Gradient Descent - CS231n](https://cs231n.github.io/optimization-1/)
- [Adam Optimizer - Kingma and Ba](https://arxiv.org/abs/1412.6980)
- [Deep Learning Book - Optimization](https://www.deeplearningbook.org/contents/optimization.html)
- [PyTorch Optimizers](https://pytorch.org/docs/stable/optim.html)

Tags: Calculus, ML, GradientDescent, Optimization, Beginner

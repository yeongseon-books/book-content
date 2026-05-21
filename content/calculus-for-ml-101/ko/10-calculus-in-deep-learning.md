---
series: calculus-for-ml-101
episode: 10
title: "Calculus for ML 101 (10/10): 딥러닝에서의 미분"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Calculus
  - ML
  - DeepLearning
  - Capstone
  - Beginner
seo_description: 네트워크, 손실, optimizer, backprop과 미분이 딥러닝 학습 루프에서 어떻게 합쳐지는지 정리한 글
last_reviewed: '2026-05-12'
---

# Calculus for ML 101 (10/10): 딥러닝에서의 미분

이 시리즈에서 지금까지 본 개념들은 각각 따로 존재하지 않습니다. 함수와 기울기, 편미분, gradient, chain rule, 손실 함수, 경사하강법, optimizer, 역전파는 모두 딥러닝 학습 루프 안에서 하나의 사이클로 묶여 움직입니다. 마지막 글의 목표는 그 조각들을 하나의 운영 모델로 합치는 것입니다.

딥러닝 학습은 겉으로 보면 반복문 한 줄처럼 보일 수 있습니다. 하지만 그 안에서는 예측을 만들고, 오차를 수치화하고, chain rule로 gradient를 계산하고, optimizer가 파라미터를 조정하는 과정이 정밀하게 이어집니다. 이 전체 고리를 이해해야 프레임워크 사용법을 넘어서 학습 자체를 설명할 수 있습니다.

이 글은 Calculus for ML 101 시리즈의 마지막 글입니다.

이 글에서는 forward pass, loss computation, backward pass, optimizer update, 반복 학습을 하나의 training loop로 묶어 설명하겠습니다. 목표는 “딥러닝이 학습한다”는 문장을 추상적으로 두지 않고, 미분이 실제로 어디에서 어떤 역할을 하는지 단계별로 복원하는 것입니다.

끝까지 읽고 나면 딥러닝 훈련 코드를 볼 때 각 줄이 어떤 수학적 의미를 갖는지, 그리고 왜 미분이 그 전체 루프의 중심인지 선명하게 보이게 됩니다.

## 먼저 던지는 질문

- 딥러닝 학습 루프는 어떤 단계로 구성되고 각 단계에서 미분은 어디에 등장할까요?
- forward pass와 loss computation은 backward를 위해 무엇을 준비할까요?
- gradient 계산과 optimizer update는 어떻게 연결될까요?

## 큰 그림

![Calculus for ML 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/10/10-01-concept-at-a-glance.ko.png)

*Calculus for ML 101 10장 흐름 개요*

## 왜 이 글이 중요한가

딥러닝 프레임워크는 training loop를 매우 간결하게 감춰 줍니다. 그래서 코드는 짧아지지만, 각 단계의 의미가 흐려지기 쉽습니다. forward가 무엇을 만들고, loss가 무엇을 수치화하고, backward가 무엇을 전파하며, optimizer가 무엇을 바꾸는지 이해해야 학습 버그를 제대로 읽을 수 있습니다.

실무에서는 같은 모델 구조라도 data pipeline, loss reduction, gradient zeroing, optimizer scheduling, eval/train mode 관리에 따라 결과가 크게 달라집니다. 이 모두를 관통하는 공통 골격이 training loop입니다. 마지막 글에서 이 골격을 잡아 두면 이후 어떤 프레임워크를 보더라도 본질을 잃지 않게 됩니다.

또한 이 글은 시리즈 전체의 요약이기도 합니다. 미분은 더 이상 별도의 수학 단원이 아니라, 예측을 오차로 바꾸고 그 오차를 다시 파라미터 변화로 환원하는 전 과정을 움직이는 중심 메커니즘으로 보이게 됩니다.

## 핵심 관점

딥러닝 학습을 가장 실용적으로 이해하는 방법은 하나의 루프를 떠올리는 것입니다. 모델이 입력으로부터 예측을 만들고, 손실 함수가 오차를 계산하고, 역전파가 gradient를 만들고, optimizer가 파라미터를 갱신합니다. 그리고 이 과정이 반복됩니다.

이 루프를 이해하면 미분은 코드 한 줄이 아니라 루프 전체를 관통하는 공통 언어가 됩니다. forward는 함수 합성이고, loss는 목적 함수이며, backward는 chain rule의 실행이고, optimizer step은 gradient를 이동으로 바꾸는 절차입니다.

> 딥러닝에서 미분은 특정 레이어의 공식이 아니라, 예측 오차를 파라미터 업데이트로 변환하는 학습 루프 전체의 공통 인터페이스입니다.

## 핵심 개념

training loop의 핵심 흐름은 아래와 같습니다.

### 모델은 입력을 예측으로 바꾸는 함수입니다

```python
import math

def model(x, w, b):
    return sigmoid(w * x + b)

def sigmoid(z):
    return 1 / (1 + math.exp(-z))
```

이 작은 모델은 선형 결합 뒤에 sigmoid를 붙인 가장 단순한 형태입니다. 하지만 여기에 이미 함수 합성과 비선형성이 모두 들어 있습니다. 복잡한 딥러닝 모델도 본질적으로는 이런 함수들의 긴 합성입니다.

### 손실은 예측과 정답의 차이를 숫자로 만듭니다

```python
def bce(y, p, eps=1e-7):
    return -(y * math.log(p + eps) + (1 - y) * math.log(1 - p + eps))
```

forward만으로는 학습이 일어나지 않습니다. 예측이 얼마나 틀렸는지를 loss로 수치화해야 하고, 이 loss가 gradient의 출발점이 됩니다. 여기서 숫자 안정성을 위해 `eps`를 더하는 습관은 실제 training code에서도 매우 중요합니다.

### gradient는 analytic form으로도 볼 수 있습니다

```python
def grads(x, y, w, b):
    p = model(x, w, b)
    err = p - y
    return err * x, err
```

이 함수는 BCE와 sigmoid 조합에서 나오는 단순화된 gradient 직관을 보여 줍니다. 핵심은 error가 각 파라미터의 책임으로 분해된다는 점입니다. 입력 쪽 weight는 `err * x`, bias는 `err` 형태로 영향을 받습니다. 즉 편미분과 chain rule이 실제 코드 결과로 나타난 것입니다.

### optimizer step은 gradient를 이동으로 바꿉니다

```python
def step(x, y, w, b, lr=0.1):
    dw, db = grads(x, y, w, b)
    return w - lr * dw, b - lr * db
```

이 한 줄이 optimizer의 본질입니다. backward가 준 gradient를 learning rate만큼 스케일해 반대 방향으로 이동합니다. 대형 프레임워크에서는 Adam, momentum, weight decay 등이 추가되지만, 핵심 구조는 그대로입니다.

### 반복문이 곧 학습 루프입니다

```python
def train(data, epochs=100, lr=0.1):
    w, b = 0.0, 0.0
    for _ in range(epochs):
        for x, y in data:
            w, b = step(x, y, w, b, lr)
    return w, b
```

학습은 거창한 것이 아니라 이 반복입니다. 데이터가 들어오고, 예측이 만들어지고, 손실이 계산되고, gradient가 업데이트로 바뀌며, 그 결과 새로운 파라미터가 다음 forward에 사용됩니다. 이 닫힌 고리가 학습의 전부라고 해도 과언이 아닙니다.

### 프레임워크 코드에서도 같은 루프가 그대로 드러납니다

```python
optimizer.zero_grad()
pred = model(x)
loss = criterion(pred, y)
loss.backward()
optimizer.step()
```

이 다섯 줄에는 지금까지 본 개념이 모두 압축되어 있습니다. `pred = model(x)`는 함수 합성이고, `loss = criterion(pred, y)`는 목적 함수를 구체화하는 단계이며, `loss.backward()`는 연쇄 법칙과 역전파를 실행하는 부분입니다. 마지막 `optimizer.step()`은 그래디언트를 실제 파라미터 이동으로 바꿉니다.

### 평가 루프가 다른 이유도 같은 구조로 설명할 수 있습니다

```python
with torch.no_grad():
    pred = model(x)
    metric = accuracy(pred, y)
```

평가 단계에서는 그래디언트가 필요하지 않으므로 backward 그래프를 만들지 않는 편이 맞습니다. 이 차이를 이해하면 왜 `train()`/`eval()` 모드 전환과 `no_grad()` 문맥이 중요한지 자연스럽게 연결됩니다. 같은 모델 코드를 쓰더라도 학습 루프와 평가 루프는 목표가 다르기 때문입니다.

### 학습 루프를 볼 때 가장 먼저 확인할 실패 지점

- `zero_grad`를 빼먹어 이전 step의 gradient가 계속 누적되고 있지 않은가
- `loss`는 내려가는데 평가 metric은 나빠져 손실 설계가 실제 목표와 어긋나고 있지 않은가
- `optimizer.step()`은 호출했지만 scheduler 순서나 train/eval 모드 전환이 꼬이지 않았는가
- reproducibility 설정이 없어 실험 차이를 모델 구조 문제로 오해하고 있지 않은가

실전에서 자주 만나는 학습 버그는 복잡한 수식보다 이런 운영 디테일에서 시작합니다. 그래서 마지막 글에서는 루프 자체를 하나의 운영 단위로 보는 감각이 중요합니다.

### 실무에서는 루프 주변의 운영 규칙도 함께 봐야 합니다

실제 코드에서는 `zero_grad`, `model.train()`, `model.eval()`, seed 고정, mixed precision, gradient clipping, scheduler step 같은 규칙이 이 루프 주변에 붙습니다. 하지만 이런 운영 요소들도 결국 forward-loss-backward-update 구조를 안정적으로 실행하기 위한 보조 장치입니다.

## 흔히 헷갈리는 지점

- loss를 계산했다고 해서 자동으로 업데이트가 되는 것은 아닙니다. backward와 optimizer step이 이어져야 합니다.
- `zero_grad`를 빼먹으면 이전 step의 gradient가 누적될 수 있습니다.
- evaluation 중에도 gradient를 계산하면 불필요한 메모리와 계산을 사용하게 됩니다.
- train/eval mode를 혼동하면 Dropout, BatchNorm 동작이 달라져 결과 해석이 틀어질 수 있습니다.
- reproducibility를 무시하면 실험 차이가 모델 구조 때문인지 학습 루프 설정 때문인지 구분하기 어려워집니다.

## 운영 체크리스트

- [ ] forward, loss, backward, update의 순서를 팀 공통 학습 루프로 명확히 정리한다
- [ ] `zero_grad`와 optimizer step의 위치를 코드 리뷰 기준에 포함한다
- [ ] train/eval mode 전환 규칙을 실험 코드와 추론 코드에서 분리한다
- [ ] learning rate, seed, scheduler, weight decay를 함께 기록해 재현성을 확보한다
- [ ] 학습 문제를 볼 때 모델 구조뿐 아니라 training loop 전체를 한 번에 점검한다

## 정리

딥러닝에서 미분은 특정 수식의 일부가 아니라 학습 루프 전체를 움직이는 중심 메커니즘입니다. forward는 함수 합성으로 예측을 만들고, loss는 오차를 숫자로 바꾸고, backward는 chain rule로 gradient를 계산하고, optimizer는 그 gradient를 파라미터 업데이트로 바꿉니다.

이 시리즈에서 본 미분, 편미분, 그래디언트, 연쇄 법칙, 손실 함수, 경사하강법, 최적화, 역전파는 모두 이 하나의 루프 안에서 각자 자리를 갖습니다. 그래서 딥러닝을 이해한다면 결국 이 루프의 각 단계가 어떤 수학적 역할을 맡는지 설명할 수 있어야 합니다.

이 글로 Calculus for ML 101 시리즈를 마칩니다. 이제 이후 어떤 모델이나 프레임워크를 보더라도, 그 안에서 학습이 실제로 어떻게 일어나는지 미분의 언어로 다시 읽어 낼 수 있을 것입니다.


## 추가 실전 섹션: 미분 신호를 학습 루프로 연결하는 계산 연습

미분 개념을 오래 유지하려면 손으로 계산한 값과 코드에서 나온 값이 같은지 반복 확인하는 연습이 중요합니다. 아래 표는 손실 함수와 gradient를 빠르게 점검할 때 자주 쓰는 비교 축입니다.

| 항목 | 회귀(MSE) | 분류(BCE) | 점검 포인트 |
| --- | --- | --- | --- |
| 손실 형태 | 평균 제곱 오차 | 음의 로그 우도 | 문제 유형 일치 여부 |
| gradient 민감도 | 큰 오차에 더 민감 | 확신한 오답에 큰 페널티 | 폭주/포화 구간 확인 |
| 수치 안정성 | 비교적 안정적 | `log(0)` 방어 필요 | `eps` 처리 |
| 학습 신호 | 선형 오차 비례 | 확률 오차 반영 | calibration 해석 |

### 체인 룰 검증: 수치 미분과 해석 미분 비교

```python
import math

def f(x):
    return math.sin(3 * x + 1)

def analytic_grad(x):
    # d/dx sin(3x+1) = cos(3x+1) * 3
    return math.cos(3 * x + 1) * 3

def numeric_grad(fn, x, h=1e-5):
    return (fn(x + h) - fn(x - h)) / (2 * h)

x = 0.7
print(analytic_grad(x), numeric_grad(f, x))
```

해석 미분과 수치 미분이 비슷하게 나오면 체인 룰 구현이 올바르게 연결되었다는 강한 증거가 됩니다.

### 2변수 손실에서 gradient 벡터 해석

```python
def loss(w1, w2):
    return (w1 - 2) ** 2 + 4 * (w2 + 1) ** 2

def grad(w1, w2):
    return 2 * (w1 - 2), 8 * (w2 + 1)

w1, w2 = 0.0, 0.0
g1, g2 = grad(w1, w2)
print('grad=', (g1, g2))
```

이 예시에서는 두 번째 축 gradient가 더 크게 나오므로 동일 learning rate에서도 `w2` 방향 업데이트가 더 공격적으로 일어납니다. 좌표별 스케일 차이를 optimizer가 어떻게 다루는지 이해하는 출발점입니다.

### 손실 곡선 해석 표

| 관찰 패턴 | 가능한 원인 | 우선 점검 |
| --- | --- | --- |
| 초반 급상승 후 발산 | learning rate 과대, gradient 폭주 | lr 감소, clipping |
| 매우 느린 하강 | learning rate 과소, 특징 스케일 불일치 | lr 증가, 정규화 |
| 진동만 하고 정체 | 비등방 지형, batch noise 과다 | momentum, batch 조정 |
| train 감소 / val 정체 | 과적합 | weight decay, early stopping |

### 미니 실습: 간단한 업데이트 루프

```python
def train_step(w, x, y, lr=0.05):
    pred = w * x
    loss = (pred - y) ** 2
    grad = 2 * (pred - y) * x
    w = w - lr * grad
    return w, loss, grad

w = 0.0
for _ in range(5):
    w, L, g = train_step(w, x=3.0, y=12.0)
    print(f'w={w:.4f}, loss={L:.4f}, grad={g:.4f}')
```

짧은 루프지만 forward-loss-backward-update가 모두 포함되어 있습니다. 이 구조를 이해하면 어떤 딥러닝 프레임워크의 학습 코드도 핵심 의미를 잃지 않고 읽을 수 있습니다.

### 실전 점검 루틴

1. 해석 미분과 수치 미분을 작은 예제로 한 번 맞춰 봅니다.
2. gradient norm을 함께 기록해 신호 크기 변화를 확인합니다.
3. learning rate를 3개 이상 비교해 수렴 민감도를 봅니다.
4. train/validation 손실을 동시에 관찰해 과적합 신호를 분리합니다.
5. 이상 징후가 생기면 모델 구조보다 손실/미분/업데이트 순서를 먼저 점검합니다.

이 루틴이 자리 잡으면 미분 개념이 수학 노트에 머무르지 않고 실제 모델 훈련 의사결정으로 연결됩니다.


## 처음 질문으로 돌아가기

- **딥러닝 학습 루프는 어떤 단계로 구성되고 각 단계에서 미분은 어디에 등장할까요?**
  - 본문의 기준은 딥러닝에서의 미분를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **forward pass와 loss computation은 backward를 위해 무엇을 준비할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **gradient 계산과 optimizer update는 어떻게 연결될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Calculus for ML 101 (1/10): 미분이란 무엇인가](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): 함수와 기울기](./02-functions-and-slope.md)
- [Calculus for ML 101 (3/10): 편미분](./03-partial-derivatives.md)
- [Calculus for ML 101 (4/10): Gradient](./04-gradient.md)
- [Calculus for ML 101 (5/10): 연쇄 법칙](./05-chain-rule.md)
- [Calculus for ML 101 (6/10): 손실 함수](./06-loss-function.md)
- [Calculus for ML 101 (7/10): 경사하강법](./07-gradient-descent.md)
- [Calculus for ML 101 (8/10): 최적화](./08-optimization.md)
- [Calculus for ML 101 (9/10): 역전파 직관](./09-backpropagation-intuition.md)
- **딥러닝에서의 미분 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Deep Learning Book - Goodfellow et al.](https://www.deeplearningbook.org/)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [CS231n - Convolutional Neural Networks](https://cs231n.stanford.edu/)
- [Reproducibility - PyTorch](https://pytorch.org/docs/stable/notes/randomness.html)
- [Zeroing out gradients in PyTorch](https://pytorch.org/tutorials/recipes/recipes/zeroing_out_gradients.html)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, DeepLearning, Capstone, Beginner

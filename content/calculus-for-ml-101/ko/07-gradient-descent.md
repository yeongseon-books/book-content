---
series: calculus-for-ml-101
episode: 7
title: "Calculus for ML 101 (7/10): 경사하강법"
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
  - GradientDescent
  - Optimization
  - Beginner
seo_description: 경사하강법, learning rate, 수렴, 발산, stochastic gradient descent 직관을 ML 입문자 관점에서 정리한 글
last_reviewed: '2026-05-12'
---

# Calculus for ML 101 (7/10): 경사하강법

미분과 gradient를 안다고 해서 학습이 자동으로 진행되지는 않습니다. 이제 남은 질문은 그 gradient를 실제 움직임으로 어떻게 바꾸느냐입니다. 경사하강법은 현재 위치의 gradient를 읽고, 그 반대 방향으로 작은 스텝을 반복해 손실을 줄여 나가는 가장 기본적인 알고리즘입니다.

중요한 것은 경사하강법이 단순한 수학 장난이 아니라, 현대 optimizer들의 공통 뼈대라는 점입니다. Adam, Momentum, RMSProp도 결국 기본 경사하강법을 더 안정적이고 빠르게 만들기 위한 변형입니다.

이 글은 Calculus for ML 101 시리즈의 일곱 번째 글입니다.

이 글에서는 경사하강법의 기본 업데이트 식, learning rate의 역할, 수렴과 발산, SGD와 mini-batch 직관을 중심으로 설명하겠습니다. 목표는 “gradient가 있으니 이제 움직인다”를 단순한 문장이 아니라 반복 가능한 학습 절차로 이해하는 것입니다.

끝까지 읽고 나면 optimizer 로그에서 loss curve를 볼 때 왜 learning rate가 가장 먼저 의심되는지 자연스럽게 설명할 수 있게 됩니다.

## 먼저 던지는 질문

- gradient의 반대 방향으로 이동하면 왜 손실이 줄어들까요?
- learning rate는 단순한 배율 이상으로 어떤 역할을 할까요?
- 경사하강법이 수렴하거나 발산하는 패턴은 어떻게 구분할 수 있을까요?

## 큰 그림

![Calculus for ML 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/07/07-01-concept-at-a-glance.ko.png)

*Calculus for ML 101 7장 흐름 개요*

## 왜 이 글이 중요한가

대부분의 ML 학습은 경사하강법의 변형 위에서 돌아갑니다. 손실 함수가 목표를 정의하고 gradient가 방향을 제시한다면, 경사하강법은 그 둘을 실제 파라미터 업데이트로 연결하는 실행 절차입니다. 이 연결이 있어야 미분이 모델 학습으로 바뀝니다.

실무에서 학습이 실패하는 가장 흔한 원인 중 하나는 learning rate 설정입니다. 너무 크면 발산하고, 너무 작으면 거의 움직이지 않으며, 데이터 스케일과 초기화, batch size에 따라 적절한 값이 달라집니다. 경사하강법의 동작 원리를 이해하지 못하면 이런 현상을 optimizer 이름 탓으로 돌리기 쉽습니다.

또한 SGD가 가져오는 noise와 mini-batch가 만드는 trade-off를 이해해야 학습 곡선의 흔들림을 자연스럽게 읽을 수 있습니다. 이 감각은 다음 글의 고급 optimizer로 넘어갈 때도 그대로 이어집니다.

## 핵심 관점

경사하강법은 사실상 매우 단순한 루프입니다. 현재 파라미터에서 gradient를 계산하고, 그 gradient를 learning rate만큼 스케일한 뒤 반대 방향으로 이동합니다. 이 루프를 반복하면서 손실을 낮춥니다.

하지만 이 단순함 때문에 오히려 핵심이 잘 드러납니다. 방향은 gradient가 정하고, 스텝 크기는 learning rate가 정합니다. 따라서 학습이 이상하게 움직일 때는 대부분 “방향이 틀렸는가, 아니면 스텝 크기가 부적절한가”로 문제를 나눠 생각할 수 있습니다.

> 경사하강법은 손실을 줄이는 마법이 아니라, gradient가 알려 준 반대 방향으로 얼마나 조심스럽게 걸을지 정하는 반복 절차입니다.

## 핵심 개념

경사하강법의 흐름은 다음과 같습니다.

### 가장 단순한 손실과 gradient부터 봅시다

```python
def loss(w):
    return (w - 3) ** 2

def grad(w):
    return 2 * (w - 3)
```

이 손실은 $w=3$에서 최소가 됩니다. gradient는 현재 위치가 최소점보다 왼쪽인지 오른쪽인지, 그리고 얼마나 떨어져 있는지를 알려 줍니다. 경사하강법은 이 gradient를 반대로 사용해 최소점 쪽으로 이동합니다.

### 한 번의 스텝은 매우 단순합니다

```python
def step(w, lr=0.1):
    return w - lr * grad(w)
```

여기서 `lr`은 learning rate입니다. 방향은 `grad(w)`의 부호가 결정하고, 실제 이동 거리는 `lr`이 조절합니다. 같은 gradient라도 `lr`이 10배면 업데이트도 10배 커집니다. 그래서 learning rate는 optimizer에서 가장 먼저 손대는 하이퍼파라미터입니다.

### 학습은 이 스텝의 반복입니다

```python
def train(w0, lr=0.1, steps=100):
    w = w0
    for _ in range(steps):
        w = step(w, lr)
    return w
```

반복 횟수가 늘수록 파라미터는 최소점 근처로 이동합니다. 물론 실제 딥러닝은 다차원, 비볼록 손실, 노이즈가 있는 gradient를 다루므로 훨씬 복잡하지만, 기본 루프는 이와 같습니다.

### SGD는 일부 데이터만 보고 업데이트합니다

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

Full-batch GD가 전체 데이터의 gradient를 쓴다면, SGD는 샘플 하나 또는 매우 작은 batch만 보고 업데이트합니다. 그래서 gradient가 noisy해지지만 계산은 싸고, 때로는 그 noise가 평평한 지역을 벗어나거나 일반화에 도움을 주기도 합니다.

### learning rate는 학습 궤적을 바꿉니다

```python
for lr in [0.001, 0.1, 1.5]:
    print(lr, train(0.0, lr, 50))
```

작은 learning rate는 안정적이지만 느리고, 큰 learning rate는 빠를 수 있지만 최소점을 건너뛰며 진동하거나 발산할 수 있습니다. 그래서 loss curve를 볼 때는 값이 내려가느냐만 보지 말고, 요동치는지, plateau에 갇히는지, 특정 시점에 폭주하는지도 함께 봐야 합니다.

### 초기화와 noise도 경로를 바꿉니다

같은 알고리즘이라도 초기 파라미터와 데이터 순서가 다르면 최적화 경로가 달라집니다. 특히 비볼록 딥러닝 손실에서는 이 차이가 더 큽니다. 따라서 재현성과 실험 비교를 위해 seed, initialization, batching 정책을 함께 기록하는 습관이 중요합니다.

## 흔히 헷갈리는 지점

- gradient가 맞아도 learning rate가 너무 크면 손실은 쉽게 발산할 수 있습니다.
- loss가 천천히 줄어든다고 해서 모델 구조 문제라고 단정하면 안 됩니다. learning rate가 지나치게 작을 수 있습니다.
- SGD의 흔들림을 실패 신호로만 보면 안 됩니다. 일부 noise는 정상적인 특성입니다.
- 서로 다른 스케일의 파라미터에 동일한 learning rate를 적용할 때 문제가 생길 수 있습니다.
- 모든 weight를 0으로 초기화하면 대칭성 문제로 학습이 막히는 구조가 있을 수 있습니다.

## 운영 체크리스트

- [ ] learning rate 후보를 최소 두세 개 이상 비교해 본다
- [ ] loss curve에서 수렴, 진동, 발산 패턴을 구분해서 읽는다
- [ ] SGD 또는 mini-batch가 만드는 noise를 정상 특성과 오류로 구분한다
- [ ] 초기화와 seed를 기록해 실험 재현성을 확보한다
- [ ] optimizer 문제를 의심하기 전에 기본 gradient와 learning rate 해석부터 확인한다

## 정리

경사하강법은 gradient의 반대 방향으로 작은 스텝을 반복해 손실을 줄이는 가장 기본적인 학습 알고리즘입니다. 방향은 gradient가 정하고, 스텝 크기는 learning rate가 정합니다. 이 단순한 구조가 거의 모든 현대 optimizer의 출발점입니다.

실무적으로 가장 중요한 감각은 learning rate 해석입니다. 발산, 느린 수렴, noisy curve 같은 현상은 대부분 경사하강법의 기본 요소로 설명할 수 있습니다. 따라서 optimizer를 바꾸기 전에 먼저 기본 GD 관점에서 현상을 읽어 보는 습관이 중요합니다.

다음 글에서는 plain GD의 약점을 보완하는 momentum, RMSProp, Adam 같은 최적화 기법을 보겠습니다. 그러면 왜 현대 학습 루프가 그 변형들을 쓰는지 연결해서 이해할 수 있습니다.


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



## 추가 보강: 검증 가능한 예제 세트

### 입력 크기 대비 알고리즘/학습 선택 표

| 상황 | 빠른 선택 | 검증 기준 |
| --- | --- | --- |
| 작은 입력, 빠른 프로토타입 | 단순 구현 우선 | 정답 검증 테스트 3종 |
| 큰 입력, 지연시간 민감 | 차수 낮은 알고리즘 또는 안정적 optimizer | 시간/메모리 동시 측정 |
| 운영 장애 재현 필요 | 로그/추적 필드 강화 | 동일 입력 재실행 가능성 |

### 짧은 비교 코드

```python
import time

def measure(fn, *args, repeat=3):
    best = float('inf')
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn(*args)
        best = min(best, time.perf_counter() - t0)
    return best
```

측정 코드는 화려할 필요가 없습니다. 같은 입력, 같은 환경, 같은 반복 기준을 유지하는 것이 더 중요합니다. 이 습관이 있어야 최적화 전후의 차이를 신뢰할 수 있습니다.

### 실전 점검 질문

1. 지금 선택한 방법의 시간/공간 비용을 한 문장으로 설명할 수 있는가
2. 경계 입력에서 동작이 바뀌는 지점을 테스트로 고정했는가
3. 운영 로그만으로 실패 원인을 분리할 수 있는가

이 질문에 즉답할 수 있으면 구현이 아니라 설계 수준에서 품질을 확보한 상태에 가깝습니다.

## 처음 질문으로 돌아가기

- **gradient의 반대 방향으로 이동하면 왜 손실이 줄어들까요?**
  - 본문의 기준은 경사하강법를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **learning rate는 단순한 배율 이상으로 어떤 역할을 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **경사하강법이 수렴하거나 발산하는 패턴은 어떻게 구분할 수 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Calculus for ML 101 (1/10): 미분이란 무엇인가](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): 함수와 기울기](./02-functions-and-slope.md)
- [Calculus for ML 101 (3/10): 편미분](./03-partial-derivatives.md)
- [Calculus for ML 101 (4/10): Gradient](./04-gradient.md)
- [Calculus for ML 101 (5/10): 연쇄 법칙](./05-chain-rule.md)
- [Calculus for ML 101 (6/10): 손실 함수](./06-loss-function.md)
- **경사하강법 (현재 글)**
- 최적화 (예정)
- 역전파 직관 (예정)
- 딥러닝에서의 미분 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Gradient Descent - CS231n](https://cs231n.github.io/optimization-1/)
- [Adam Optimizer - Kingma and Ba](https://arxiv.org/abs/1412.6980)
- [Deep Learning Book - Optimization](https://www.deeplearningbook.org/contents/optimization.html)
- [PyTorch Optimizers](https://pytorch.org/docs/stable/optim.html)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, GradientDescent, Optimization, Beginner

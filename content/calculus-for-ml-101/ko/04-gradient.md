---
series: calculus-for-ml-101
episode: 4
title: "Calculus for ML 101 (4/10): Gradient"
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
  - Gradient
  - Vector
  - Beginner
seo_description: gradient vector, 방향, 크기, 등고선, 가장 가파른 증가 방향을 ML 입문자 관점에서 정리한 글
last_reviewed: '2026-05-12'
---

# Calculus for ML 101 (4/10): Gradient

편미분까지 이해했다면 이제 질문이 하나 더 생깁니다. 여러 변수에 대한 변화율을 각각 따로 계산한 뒤, 그 정보를 어떻게 한 번에 사용해야 할까요? 모델은 보통 파라미터를 한 개씩 따로 움직이지 않고, 현재 상태 전체를 기준으로 한 번의 업데이트를 수행합니다.

Gradient는 바로 그때 필요한 표현입니다. 여러 편미분을 순서 있는 벡터로 묶어, 함수가 가장 빠르게 증가하는 방향을 하나의 객체로 나타냅니다. 그래서 gradient는 단순한 숫자 모음이 아니라, 현재 지점에서 움직일 방향과 신호 강도를 함께 담은 구조입니다.

이 글은 Calculus for ML 101 시리즈의 네 번째 글입니다.

이 글에서는 gradient를 방향, 크기, 등고선, 반대 방향이라는 관점에서 설명하겠습니다. 핵심은 “편미분이 여러 개 있다”에서 멈추지 않고, 그것이 왜 업데이트 방향이 되는지 이해하는 것입니다.

끝까지 읽고 나면 gradient를 벡터 기호가 아니라 손실 지형 위에서 길을 찾는 지도처럼 해석하게 될 것입니다.

## 먼저 던지는 질문

- 여러 편미분을 하나의 gradient vector로 묶는다는 것은 정확히 무엇을 뜻할까요?
- gradient의 방향과 크기는 각각 어떤 실무 의미를 가질까요?
- 왜 gradient는 손실이 가장 빠르게 증가하는 방향을 가리킬까요?

## 큰 그림

![Calculus for ML 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/04/04-01-concept-at-a-glance.ko.png)

*Calculus for ML 101 4장 흐름 개요*

## 왜 이 글이 중요한가

optimizer는 scalar 하나가 아니라 parameter vector 전체를 다룹니다. 따라서 손실을 줄이려면 각 weight에 대한 편미분을 따로 보는 데서 한 걸음 더 나아가, 전체 상태를 움직일 방향을 정해야 합니다. gradient는 이 역할을 수행하는 가장 기본적인 수학적 표현입니다.

실무에서 gradient norm을 모니터링하거나, exploding gradient를 진단하거나, learning rate와 gradient magnitude를 함께 해석하는 이유도 여기에 있습니다. gradient를 단지 “autograd가 준 숫자 배열”로 보면 이런 현상이 분절된 이벤트처럼 보이지만, 방향 벡터라는 관점으로 보면 훨씬 일관되게 해석됩니다.

또한 gradient를 이해해야 다음 글의 chain rule과 backpropagation이 왜 효율적인지 자연스럽게 이어집니다. backpropagation은 결국 전체 모델의 gradient를 빠르게 계산하는 메커니즘이기 때문입니다.

## 핵심 관점

Gradient를 가장 잘 이해하는 방법은 손실 함수를 지형으로 상상하는 것입니다. 현재 위치에서 어느 쪽이 가장 가파르게 올라가는지 알려 주는 화살표가 gradient입니다. 이 화살표의 방향은 상승 방향을, 길이는 변화의 강도를 나타냅니다.

경사하강법은 이 화살표를 반대로 뒤집어 한 걸음 이동합니다. 즉 gradient를 알면 “어느 쪽으로 올라가는가”를 알고, 그 반대 방향으로 가면 “어느 쪽으로 내려가는가”를 알 수 있습니다. 그래서 gradient는 단지 미분의 결과가 아니라, 학습의 직접적인 제어 신호가 됩니다.

> Gradient는 여러 편미분의 목록이 아니라, 현재 위치에서 손실이 가장 빠르게 증가하는 방향과 강도를 동시에 담은 벡터입니다.

## 핵심 개념

gradient의 핵심 흐름은 다음과 같습니다.

### gradient는 편미분을 묶은 벡터입니다

```python
def grad(f, x, h=1e-5):
    g = []
    for i in range(len(x)):
        xp = x.copy(); xm = x.copy()
        xp[i] += h; xm[i] -= h
        g.append((f(xp) - f(xm)) / (2 * h))
    return g
```

이 함수는 각 좌표를 하나씩 움직여 편미분을 계산하고 리스트로 모읍니다. 구현은 단순하지만 의미는 분명합니다. 입력 벡터의 각 축에 대해 독립적인 변화율을 계산하고, 그 순서를 유지한 채 하나의 벡터로 묶습니다.

### 손실 함수에 적용하면 방향 정보가 드러납니다

```python
def loss(w):
    return (w[0] - 1) ** 2 + (w[1] + 2) ** 2
```

이 손실은 2차원 지형처럼 볼 수 있습니다. 특정 지점에서 gradient를 계산하면, 현재 위치에서 손실이 가장 빨리 증가하는 방향이 벡터로 나옵니다.

```python
g = grad(loss, [0.0, 0.0])  # about [-2, 4]
```

예를 들어 여기서는 첫 번째 축으로는 왼쪽, 두 번째 축으로는 위쪽 성분이 있다는 뜻입니다. 중요한 것은 각 성분을 따로 보는 것을 넘어서, 이 둘이 합쳐져 하나의 방향 화살표를 만든다는 점입니다.

### 크기는 신호의 강도를 말해 줍니다

```python
import math

def norm(v):
    return math.sqrt(sum(x ** 2 for x in v))
```

gradient norm은 현재 지점에서 얼마나 급한 지형에 서 있는지 알려 줍니다. norm이 크면 작은 이동에도 손실이 크게 변할 수 있고, norm이 작으면 평평한 지역에 가까울 수 있습니다. gradient clipping, exploding gradient 모니터링 같은 실무 기법도 결국 이 크기 해석에 기대고 있습니다.

### 반대 방향이 감소 방향입니다

```python
def step(w, g, lr=0.1):
    return [wi - lr * gi for wi, gi in zip(w, g)]
```

gradient는 증가 방향이므로, 손실을 줄이려면 부호를 뒤집어 이동해야 합니다. 이 한 줄이 경사하강법의 본질입니다. learning rate는 이 벡터를 얼마나 길게 반영할지 조절하는 배율이고, gradient 자체와는 다른 개념입니다.

### 등고선 관점이 특히 유용합니다

2차원 손실 표면을 등고선으로 생각하면 gradient는 항상 등고선에 수직인 방향을 가리킵니다. 그리고 그 방향이 가장 가파른 상승 방향입니다. 그래서 등고선 사이를 비스듬히 헤매는 대신, gradient를 따라가면 가장 직접적인 상승 경로를 얻게 됩니다. 경사하강법은 정확히 그 반대 경로를 택합니다.

## 흔히 헷갈리는 지점

- gradient를 scalar처럼 취급하면 각 좌표의 책임과 전체 방향을 동시에 놓치게 됩니다.
- learning rate와 gradient magnitude를 같은 것으로 생각하면 업데이트가 왜 커졌는지 잘못 해석할 수 있습니다.
- gradient의 부호를 반대로 읽으면 손실을 줄이는 대신 키우는 방향으로 움직일 수 있습니다.
- 좌표 순서가 weight 순서와 맞지 않으면 gradient vector 전체가 잘못 적용됩니다.
- 등고선 직관 없이 수치만 보면 왜 특정 방향이 선택되는지 설명이 약해집니다.

## 운영 체크리스트

- [ ] gradient를 벡터로 보고 각 성분과 전체 방향을 함께 해석한다
- [ ] learning rate와 gradient norm을 분리해서 모니터링한다
- [ ] 좌표 순서와 parameter 순서가 코드 전반에서 일치하는지 확인한다
- [ ] exploding 또는 vanishing gradient 징후를 norm 관점에서 읽는다
- [ ] 경사하강법은 gradient의 반대 방향이라는 기본 규칙을 항상 점검한다

## 정리

Gradient는 여러 편미분을 한데 묶은 벡터이며, 현재 지점에서 손실이 가장 빠르게 증가하는 방향을 가리킵니다. 방향은 어디로 움직일지를, 크기는 그 신호가 얼마나 강한지를 알려 줍니다. 그래서 gradient는 미분 결과이면서 동시에 학습 제어 신호입니다.

경사하강법은 이 gradient를 반대로 따라갑니다. 즉 gradient를 이해하는 것은 “왜 optimizer가 저 방향으로 움직였는가”를 이해하는 일과 같습니다. 실무에서 gradient norm, clipping, exploding gradient 같은 표현이 자연스럽게 쓰이는 이유도 모두 이 벡터 관점에서 설명됩니다.

다음 글에서는 함수가 함수 안에 들어가는 합성 구조에서 gradient가 어떻게 전달되는지 보겠습니다. 그러면 chain rule이 왜 backpropagation의 핵심인지 훨씬 분명해집니다.


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



### 보강 메모: 경계 입력과 수치 검증

경계 입력을 별도 표로 관리하면 알고리즘/학습 루프의 취약점을 빠르게 찾을 수 있습니다.

| 케이스 | 기대 동작 |
| --- | --- |
| 빈 입력 또는 최소 크기 | 예외 없이 명시적 반환 |
| 중복값 다수 | 안정성/경계 갱신 유지 |
| 극단적으로 큰 값 | 오버플로우/수치 불안정 방어 |

```python
def sanity_cases(fn, cases):
    out=[]
    for c in cases:
        out.append(fn(*c) if isinstance(c, tuple) else fn(c))
    return out
```

작은 검증 루틴을 글과 코드에 함께 남기면 이후 변경에서 같은 종류의 실수를 반복할 가능성이 크게 줄어듭니다.

## 처음 질문으로 돌아가기

- **여러 편미분을 하나의 gradient vector로 묶는다는 것은 정확히 무엇을 뜻할까요?**
  - 본문의 기준은 Gradient를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **gradient의 방향과 크기는 각각 어떤 실무 의미를 가질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **왜 gradient는 손실이 가장 빠르게 증가하는 방향을 가리킬까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Calculus for ML 101 (1/10): 미분이란 무엇인가](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): 함수와 기울기](./02-functions-and-slope.md)
- [Calculus for ML 101 (3/10): 편미분](./03-partial-derivatives.md)
- **Gradient (현재 글)**
- 연쇄 법칙 (예정)
- 손실 함수 (예정)
- 경사하강법 (예정)
- 최적화 (예정)
- 역전파 직관 (예정)
- 딥러닝에서의 미분 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Gradient - Khan Academy](https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives/partial-derivative-and-gradient-articles)
- [Vector Calculus - 3Blue1Brown](https://www.3blue1brown.com/topics/calculus)
- [Deep Learning Book - Numerical Computation](https://www.deeplearningbook.org/contents/numerical.html)
- [PyTorch Autograd Mechanics](https://pytorch.org/docs/stable/notes/autograd.html)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, Gradient, Vector, Beginner

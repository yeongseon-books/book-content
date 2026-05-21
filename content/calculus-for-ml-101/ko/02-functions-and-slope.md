---
series: calculus-for-ml-101
episode: 2
title: "Calculus for ML 101 (2/10): 함수와 기울기"
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
  - Functions
  - Slope
  - Beginner
seo_description: 함수, 기울기, 선형과 비선형, 도함수의 그래프 의미를 ML 입문자 관점에서 정리한 글
last_reviewed: '2026-05-12'
---

# Calculus for ML 101 (2/10): 함수와 기울기

머신러닝 모델은 본질적으로 입력을 출력으로 보내는 함수들의 조합입니다. 선형층도 함수이고, 활성화 함수도 함수이며, 마지막 예측값도 결국 여러 함수를 거쳐 나온 결과입니다. 그래서 모델 학습을 이해하려면 먼저 함수가 무엇을 하는지, 그리고 그 함수의 기울기가 왜 중요한지 분명히 알아야 합니다.

기울기는 직선에서만 등장하는 개념처럼 보이지만, 실제로는 비선형 함수에서도 각 지점마다 국소적으로 정의됩니다. 이때 기울기는 함수의 모양을 읽는 언어가 됩니다. 어디서 빠르게 증가하는지, 어디서 평평해지는지, 어디서 gradient가 사라질 위험이 있는지가 모두 기울기로 드러납니다.

이 글은 Calculus for ML 101 시리즈의 두 번째 글입니다.

이 글에서는 함수를 단순한 식이 아니라 입력-출력 계약과 그래프의 모양을 함께 가진 대상으로 보고, 선형 함수와 비선형 함수의 기울기 차이가 ML에서 왜 중요한지 설명하겠습니다.

끝까지 읽고 나면 함수의 그래프를 보는 것만으로도 학습이 쉬운 구간과 어려운 구간을 어느 정도 짐작할 수 있게 됩니다.


![Calculus for ML 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/02/02-01-concept-at-a-glance.ko.png)
*Calculus for ML 101 2장 흐름 개요*

## 먼저 던지는 질문

- 함수는 왜 단순한 수식이 아니라 입력과 출력의 계약으로 이해해야 할까요?
- 선형 함수의 기울기와 비선형 함수의 국소 기울기는 어떻게 다를까요?
- ReLU와 sigmoid의 기울기 차이는 학습 과정에 어떤 영향을 줄까요?

## 왜 이 글이 중요한가

신경망은 함수 합성입니다. 선형 변환이 입력을 새로운 표현으로 바꾸고, 비선형 활성화 함수가 표현력을 추가하며, 마지막 출력 함수가 예측값을 만듭니다. 이 모든 단계에서 학습이 일어나려면 각 함수가 기울기를 통해 자신의 변화 가능성을 뒤로 전달해야 합니다.

실무에서 activation을 선택하거나, vanishing gradient를 진단하거나, 입력 정규화의 필요성을 설명할 때 결국 다시 함수와 기울기로 돌아오게 됩니다. 예를 들어 sigmoid가 포화 구간에서 왜 학습을 느리게 만드는지, ReLU가 왜 실용적이지만 0 근처에서 미분 가능성 이슈를 갖는지 모두 함수의 모양과 기울기를 보면 설명됩니다.

즉, 함수와 기울기를 이해하는 일은 미분의 기초 복습이 아니라 모델 구성 요소를 읽는 능력을 키우는 일입니다. 이 관점이 있어야 이후 편미분과 gradient를 벡터 수준으로 확장할 때도 개념이 흔들리지 않습니다.

## 핵심 관점

함수를 가장 잘 이해하는 방법은 식만 보지 않고 그래프를 함께 보는 것입니다. 식은 계산 규칙을 알려 주고, 그래프는 입력이 변할 때 출력이 어떤 모양으로 반응하는지 보여 줍니다. 기울기는 이 둘 사이를 연결하는 다리입니다.

선형 함수에서는 기울기가 항상 일정하므로 해석이 단순합니다. 반대로 비선형 함수는 지점마다 기울기가 달라지므로, 모델이 어느 구간에서 쉽게 학습하고 어느 구간에서 신호를 잃는지가 함수의 모양에 직접 드러납니다. ML에서 activation을 선택할 때 함수 그래프를 반드시 함께 봐야 하는 이유입니다.

> 함수는 입력을 출력으로 보내는 계약이고, 기울기는 그 계약이 현재 지점에서 얼마나 민감하게 반응하는지 보여 주는 운영 지표입니다.

## 핵심 개념

함수와 기울기의 관계를 한 화면에 놓으면 아래처럼 정리할 수 있습니다.

### 함수는 입력을 출력으로 보내는 계약입니다

함수는 어떤 입력이 들어오면 어떤 출력이 나오는지를 일관되게 정의합니다. 이 단순한 정의가 ML에서 중요한 이유는 모델 전체가 결국 작은 함수들의 조합이기 때문입니다. 각 함수는 자기 입력 범위에서 어떤 응답을 보이는지, 그리고 그 응답이 얼마나 민감한지 기울기로 드러냅니다.

### 선형 함수에서는 기울기가 상수입니다

```python
def linear(x, a=2, b=1):
    return a * x + b
```

선형 함수는 입력이 일정하게 늘면 출력도 일정한 비율로 늘어납니다. 그래서 그래프는 직선이고, 기울기는 어느 지점에서나 동일합니다. 모델 관점에서는 해석이 쉽지만 표현력은 제한적입니다.

```python
def linear_slope(a):
    return a
```

기울기가 상수라는 사실은 선형 함수의 장점이자 한계입니다. 계산과 해석은 단순하지만, 복잡한 패턴을 표현하려면 비선형성이 반드시 추가되어야 합니다.

### 비선형 함수는 위치에 따라 다른 기울기를 가집니다

```python
def relu(x):
    return max(0.0, x)
```

ReLU는 음수 구간을 0으로 자르고 양수 구간을 그대로 통과시킵니다. 함수 형태가 단순해서 널리 쓰이지만, 이 단순함이 곧 기울기 구조를 결정합니다.

```python
def relu_grad(x):
    return 1.0 if x > 0 else 0.0
```

ReLU의 핵심은 gradient가 0 아니면 1이라는 점입니다. 양수 구간에서는 신호가 잘 흐르지만, 음수 구간에서는 gradient가 0이어서 업데이트 신호가 끊길 수 있습니다. "dying ReLU" 같은 문제가 왜 생기는지 여기서 출발합니다.

### sigmoid는 매끄럽지만 포화 구간이 있습니다

```python
import math

def sigmoid(x):
    return 1 / (1 + math.exp(-x))
```

sigmoid는 0과 1 사이로 값을 압축하는 부드러운 함수입니다. 출력 해석은 직관적이지만, 입력 절댓값이 커질수록 곡선이 평평해지는 포화 구간이 생깁니다. 이 구간에서는 기울기가 작아져 학습 신호가 약해집니다.

그래서 함수의 "좋아 보이는 모양"만 보면 안 됩니다. 실무에서는 출력 범위, 미분 가능성, 포화 구간, 계산 안정성을 함께 봅니다. 함수의 기울기 분포를 보지 않고 activation을 고르면 학습 성능을 설명하기 어려워집니다.

### 도함수의 그래프 의미를 읽어야 합니다

선형 함수의 도함수는 상수이고, ReLU의 도함수는 0 또는 1이며, sigmoid의 도함수는 가운데에서 크고 양끝에서 작습니다. 이 도함수의 모양은 곧 "어디서 학습이 잘 되는가"를 말해 줍니다. 입력 스케일 정렬과 정규화가 중요한 이유도, 모델을 더 많은 유효 기울기 구간에 머무르게 하기 위해서입니다.

## 활성화 함수 비교: 기울기 관점에서 읽기

activation 함수는 모델에 비선형성을 부여하는 유일한 도구입니다. 여기서는 주요 활성화 함수의 기울기를 코드로 직접 계산하고 비교합니다.

### sigmoid 도함수: $\sigma(x)(1-\sigma(x))$

```python
import numpy as np

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def sigmoid_grad(x):
    s = sigmoid(x)
    return s * (1 - s)

# 여러 지점에서 기울기 확인
x_vals = np.array([-5.0, -2.0, 0.0, 2.0, 5.0])
for x in x_vals:
    print(f"sigmoid({x:+.1f}) = {sigmoid(x):.4f}, grad = {sigmoid_grad(x):.6f}")
# sigmoid(-5.0) = 0.0067, grad = 0.006648
# sigmoid(-2.0) = 0.1192, grad = 0.104994
# sigmoid( 0.0) = 0.5000, grad = 0.250000
# sigmoid(+2.0) = 0.8808, grad = 0.104994
# sigmoid(+5.0) = 0.9933, grad = 0.006648
```

$x=0$에서 기울기가 최대(0.25)이고, $|x|$가 커질수록 기울기가 급격히 줄어듭니다. 기울기 최대값이 0.25라는 것은 역전파에서 매 레이어를 지날 때마다 gradient가 최소 1/4로 줄어들 수 있다는 뜻입니다. 층이 깊을수록 앞쪽 레이어의 gradient가 기하급수적으로 작아지는 vanishing gradient 문제의 직접적인 원인입니다.

### tanh 도함수: $1 - \tanh^2(x)$

```python
def tanh(x):
    return np.tanh(x)

def tanh_grad(x):
    return 1.0 - np.tanh(x) ** 2

for x in x_vals:
    print(f"tanh({x:+.1f}) = {tanh(x):+.4f}, grad = {tanh_grad(x):.6f}")
# tanh(-5.0) = -1.0000, grad = 0.000018
# tanh(-2.0) = -0.9640, grad = 0.070651
# tanh( 0.0) = +0.0000, grad = 1.000000
# tanh(+2.0) = +0.9640, grad = 0.070651
# tanh(+5.0) = +1.0000, grad = 0.000018
```

tanh는 sigmoid보다 출력 범위가 넓고(-1 ~ +1), $x=0$에서의 기울기가 1.0으로 sigmoid의 4배입니다. 그래서 초기 학습 속도가 sigmoid보다 빠른 경우가 많지만, 포화 구간 문제는 여전합니다.

### ReLU와 변형들의 기울기 비교

```python
def relu_grad(x):
    return 1.0 if x > 0 else 0.0

def leaky_relu_grad(x, alpha=0.01):
    return 1.0 if x > 0 else alpha

def elu_grad(x, alpha=1.0):
    return 1.0 if x > 0 else alpha * np.exp(x)

# 비교 표 출력
print(f"{'x':<8} {'ReLU':<8} {'Leaky':<8} {'ELU':<10}")
for x in [-2.0, -0.5, 0.0, 0.5, 2.0]:
    r = relu_grad(x)
    l = leaky_relu_grad(x)
    e = elu_grad(x)
    print(f"{x:<8.1f} {r:<8.1f} {l:<8.3f} {e:<10.6f}")
```

| x | ReLU | Leaky ReLU | ELU |
| --- | --- | --- | --- |
| -2.0 | 0.0 | 0.01 | 0.135 |
| -0.5 | 0.0 | 0.01 | 0.607 |
| 0.0 | 0.0 | 0.01 | 1.0 |
| 0.5 | 1.0 | 1.0 | 1.0 |
| 2.0 | 1.0 | 1.0 | 1.0 |

ReLU는 음수 구간에서 gradient가 완전히 0이므로, 한번 뉴런이 죽으면 다시 살아나기 어렵습니다. Leaky ReLU와 ELU는 이 문제를 작은 양의 gradient를 남겨 두는 방식으로 완화합니다.

### 활성화 함수 선택 가이드

| 기준 | sigmoid | tanh | ReLU | Leaky ReLU |
| --- | --- | --- | --- | --- |
| 출력 범위 | (0, 1) | (-1, 1) | [0, inf) | (-inf, inf) |
| 기울기 최대값 | 0.25 | 1.0 | 1.0 | 1.0 |
| 포화 구간 | 양끝 | 양끝 | 없음(양수) | 없음 |
| dying 문제 | 없음 | 없음 | 있음 | 없음 |
| 주 사용처 | 출력층(이진 분류) | RNN hidden | 은닉층(기본) | dying ReLU 방지 |

## 함수 합성과 기울기의 전파

신경망은 단일 함수가 아니라 여러 함수의 합성입니다. 기울기가 어떻게 전파되는지 단순한 2층 네트워크로 확인합니다.

### 2층 합성 함수 예시

```python
import numpy as np

def layer1(x, w1):
    return w1 * x

def activation(z):
    return 1.0 / (1.0 + np.exp(-z))  # sigmoid

def layer2(a, w2):
    return w2 * a

# forward pass
x = 2.0
w1, w2 = 0.5, 1.5
z1 = layer1(x, w1)      # 1.0
a1 = activation(z1)     # sigmoid(1.0) = 0.7311
y_hat = layer2(a1, w2)  # 1.5 * 0.7311 = 1.0966

print(f"z1={z1:.4f}, a1={a1:.4f}, y_hat={y_hat:.4f}")
```

### 기울기 역전파 추적

```python
# y = 3.0이 정답이라고 가정
y = 3.0
loss = (y_hat - y) ** 2  # MSE

# backward: dL/dy_hat 계산
dL_dy = 2 * (y_hat - y)  # -3.8068

# dy_hat/da1 = w2
dy_da1 = w2  # 1.5

# da1/dz1 = sigmoid_grad(z1)
s = activation(z1)
da1_dz1 = s * (1 - s)  # 0.1966

# dz1/dw1 = x
dz1_dw1 = x  # 2.0

# chain rule: dL/dw1 = dL/dy * dy/da1 * da1/dz1 * dz1/dw1
dL_dw1 = dL_dy * dy_da1 * da1_dz1 * dz1_dw1
print(f"dL/dw1 = {dL_dw1:.4f}")
# dL/dw1 = -2.2463

# 수치 검증
h = 1e-7
w1_plus = w1 + h
y_plus = layer2(activation(layer1(x, w1_plus)), w2)
loss_plus = (y_plus - y) ** 2
numeric_grad = (loss_plus - loss) / h
print(f"numeric dL/dw1 = {numeric_grad:.4f}")
```

여기서 핵심은 `da1_dz1 = 0.1966`입니다. sigmoid를 거치면서 gradient가 약 1/5로 줄었습니다. 층이 10개라면 $0.1966^{10} \approx 7 \times 10^{-8}$로 gradient가 사실상 사라집니다. ReLU를 쓰면 이 계수가 1이 되므로 gradient가 감쇠 없이 전파됩니다.

## 함수의 볼록성과 최적화 난이도

기울기만으로는 최적화의 전체 그림을 보기 어렵습니다. 함수의 볼록성(convexity)은 기울기 정보가 전역 최솟값으로 안내하는지 아닌지를 결정합니다.

### 볼록 함수 vs 비볼록 함수

```python
import numpy as np

# 볼록 함수: gradient가 항상 최솟값 방향을 가리킴
def convex_loss(w):
    return (w - 2.0) ** 2

# 비볼록 함수: 지역 최솟값이 여러 개
def non_convex_loss(w):
    return w ** 4 - 4 * w ** 2 + w

# 기울기
def convex_grad(w):
    return 2 * (w - 2.0)

def non_convex_grad(w):
    return 4 * w ** 3 - 8 * w + 1

# 비볼록 함수에서 시작점에 따라 다른 결과
for w_init in [-2.0, 0.0, 2.0]:
    w = w_init
    for _ in range(100):
        w = w - 0.01 * non_convex_grad(w)
    print(f"start={w_init:+.1f} -> converged to w={w:.4f}, loss={non_convex_loss(w):.4f}")
```

볼록 함수에서는 gradient descent가 어디서 시작하든 같은 최솟값에 도달합니다. 비볼록 함수에서는 시작점에 따라 다른 지역 최솟값에 빠질 수 있습니다. 딥러닝의 손실 함수는 거의 항상 비볼록이므로, 초기화 전략과 학습률 스케줄이 실질적인 수렴 성능을 좌우합니다.

### 이차 도함수와 곡률

기울기가 0인 지점이 최솟값인지 최댓값인지 안장점인지는 이차 도함수로 판별합니다.

| 조건 | 의미 |
| --- | --- |
| $f'(x) = 0$, $f''(x) > 0$ | 극소 (아래로 볼록) |
| $f'(x) = 0$, $f''(x) < 0$ | 극대 (위로 볼록) |
| $f'(x) = 0$, $f''(x) = 0$ | 판별 불가 (변곡점 가능) |

```python
# x^3은 x=0에서 f'=0, f''=0 -> 극값이 아니라 변곡점
def cubic(x):
    return x ** 3

def cubic_grad(x):
    return 3 * x ** 2

def cubic_hessian(x):
    return 6 * x

x = 0.0
print(f"f'(0)={cubic_grad(x)}, f''(0)={cubic_hessian(x)}")
# f'(0)=0.0, f''(0)=0.0 -> 변곡점
```

## 흔히 헷갈리는 지점

- 함수의 식만 이해하고 그래프를 보지 않으면 기울기와 포화 구간을 놓치기 쉽습니다.
- ReLU가 단순하다고 해서 항상 문제없다고 보면 안 됩니다. $x=0$에서 미분 가능성 이슈가 있고, 음수 구간에서는 gradient가 0입니다.
- sigmoid가 매끄럽다는 이유만으로 학습에 항상 유리한 것은 아닙니다. 포화 구간에서는 gradient가 매우 작아집니다.
- 서로 다른 입력 스케일을 그대로 비교하면 함수의 민감도를 잘못 해석할 수 있습니다.
- 선형 기울기와 비선형의 국소 기울기를 같은 방식으로 생각하면 activation이 왜 필요한지 설명이 약해집니다.
- 기울기가 0이라고 무조건 최솟값이라고 결론 짓지 말아야 합니다. 이차 도함수나 주변 지형을 함께 확인해야 합니다.

## 운영 체크리스트

- [ ] 모델의 주요 activation 함수 그래프와 기울기 특성을 함께 설명할 수 있다
- [ ] ReLU의 0 구간과 sigmoid의 포화 구간이 학습에 주는 영향을 구분한다
- [ ] 입력 스케일 정렬이 기울기 해석과 연결된다는 점을 기억한다
- [ ] 함수값뿐 아니라 도함수의 모양까지 함께 본다
- [ ] vanishing gradient 의심 시 활성화 함수의 국소 기울기부터 점검한다
- [ ] activation 선택 근거를 기울기 최대값과 포화 특성으로 설명할 수 있다
- [ ] 합성 함수의 기울기 전파 경로에서 병목 지점을 식별한다

## 정리

함수는 입력을 출력으로 보내는 계약이고, 기울기는 그 계약이 현재 지점에서 얼마나 민감하게 반응하는지 보여 줍니다. 선형 함수는 일정한 기울기를 가지지만, 비선형 함수는 위치마다 다른 기울기를 가지므로 학습 난이도와 신호 흐름이 달라집니다.

ML에서는 이 차이가 매우 실용적입니다. activation 함수 하나를 고르는 일도 결국 함수의 모양과 gradient 흐름을 고르는 일입니다. ReLU, sigmoid, tanh 같은 함수가 왜 각기 다른 장단점을 갖는지 이해하려면 출력 범위보다 먼저 기울기 구조를 봐야 합니다.

다음 글에서는 입력이 하나가 아니라 여러 개인 함수로 시야를 넓히겠습니다. 그러면 기울기를 변수별로 나눠 읽는 편미분 개념이 왜 필요한지 자연스럽게 드러납니다.

## 입력 정규화와 기울기의 관계

함수의 기울기가 입력 위치에 따라 달라진다면, 입력이 어떤 범위에 있는지가 학습 속도를 직접 좌우합니다. 이것이 입력 정규화(input normalization)가 단순한 전처리가 아니라 기울기 효율과 직결되는 이유입니다.

### 정규화 전후 기울기 변화 실험

```python
import numpy as np

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

def sigmoid_grad(x):
    s = sigmoid(x)
    return s * (1 - s)

# 정규화하지 않은 입력 (큰 스케일)
raw_inputs = np.array([100.0, 200.0, 300.0, 400.0, 500.0])
raw_grads = sigmoid_grad(raw_inputs)
print(f"Raw inputs grads: {raw_grads}")  # 거의 모두 0

# 정규화한 입력 (mean=0, std=1)
normalized = (raw_inputs - raw_inputs.mean()) / raw_inputs.std()
norm_grads = sigmoid_grad(normalized)
print(f"Normalized grads: {norm_grads}")  # 유효한 기울기
```

정규화 전에는 sigmoid의 포화 구간에 입력이 몰려 gradient가 거의 0입니다. 정규화 후에는 입력이 sigmoid의 민감한 구간(-2 ~ +2)에 분포하므로 유의미한 gradient가 전달됩니다. BatchNorm이 등장하기 전에도 입력 정규화가 학습 안정성의 기본이었던 이유가 여기 있습니다.

### BatchNorm의 기울기 관점 해석

BatchNorm은 각 미니배치에서 평균과 분산을 계산해 활성화 입력을 재정규화합니다. 기울기 관점에서 이것이 하는 일은 명확합니다.

| 효과 | 기울기 관점 해석 |
| --- | --- |
| 평균 제거 | sigmoid/tanh의 중심 구간에 입력을 집중시킴 |
| 분산 정규화 | 기울기가 유효한 범위 안에 입력을 가둠 |
| 학습 가능한 scale/shift | 필요시 포화 구간도 활용 가능하게 열어 둠 |

```python
def batch_norm(x, eps=1e-5):
    mean = np.mean(x)
    var = np.var(x)
    x_hat = (x - mean) / np.sqrt(var + eps)
    return x_hat

# 적용 전후 기울기 비교
x = np.array([3.0, 5.0, 7.0, 9.0, 11.0])
print(f"Before BN - sigmoid grads: {sigmoid_grad(x)}")
x_bn = batch_norm(x)
print(f"After BN  - sigmoid grads: {sigmoid_grad(x_bn)}")
```

## 함수의 연속성과 미분 가능성: 실무 관점

모든 함수가 미분 가능한 것은 아닙니다. ML에서 사용하는 함수들의 미분 가능성 조건을 정리합니다.

### 미분 가능 조건

함수가 한 점에서 미분 가능하려면 그 점에서 연속이어야 하고, 좌미분과 우미분이 같아야 합니다. 연속이지만 미분 불가능한 점(kink)이 있을 수 있고, 불연속 점은 당연히 미분 불가능합니다.

| 함수 | 문제 지점 | 프레임워크 처리 |
| --- | --- | --- |
| ReLU | x=0 (kink) | subgradient 0 사용 |
| Leaky ReLU | x=0 (kink) | 좌우 기울기 다르지만 학습에 큰 영향 없음 |
| abs(x) | x=0 (kink) | subgradient 또는 smooth 근사 |
| step function | 모든 정수 | 미분 불가 -> sigmoid로 대체 |
| max pooling | 경계 | argmax 위치만 gradient 전달 |

### smooth 근사 전략

미분이 불가능한 함수는 smooth 근사로 대체하는 전략이 흔합니다.

```python
# |x|의 smooth 근사: sqrt(x^2 + eps)
def smooth_abs(x, eps=0.01):
    return np.sqrt(x ** 2 + eps)

def smooth_abs_grad(x, eps=0.01):
    return x / np.sqrt(x ** 2 + eps)

# x=0 근처에서 비교
x_near_zero = np.linspace(-0.5, 0.5, 11)
for x in x_near_zero:
    grad = smooth_abs_grad(x)
    print(f"x={x:+.2f}, smooth_abs_grad={grad:+.4f}")
```

smooth 근사는 원래 함수와 거의 같은 값을 내면서도 모든 점에서 gradient를 정의할 수 있게 해 줍니다. Huber loss가 MSE와 MAE 사이에서 이 전략을 적용한 대표적인 예입니다.

## 실전 진단: 기울기로 학습 문제를 읽는 방법

함수와 기울기 지식을 실제 학습 디버깅에 적용하는 절차를 정리합니다.

### gradient 히스토그램 읽기

TensorBoard나 W\&B에서 레이어별 gradient 히스토그램을 볼 때 확인할 패턴입니다.

| 패턴 | 진단 | 조치 |
| --- | --- | --- |
| 대부분 0 근처 집중 | vanishing gradient | activation 교체, skip connection 추가 |
| 매우 넓은 분포 | exploding gradient | gradient clipping, lr 감소 |
| 특정 레이어만 0 | dying neuron | Leaky ReLU, 초기화 변경 |
| 학습 중 점점 좁아짐 | 수렴 중 (정상) | 모니터링 유지 |

### 레이어별 기울기 크기 추적 코드

```python
import torch
import torch.nn as nn

model = nn.Sequential(
    nn.Linear(10, 64),
    nn.Sigmoid(),
    nn.Linear(64, 64),
    nn.Sigmoid(),
    nn.Linear(64, 1),
)

# hook으로 gradient 크기 기록
grad_norms = {}

def hook_fn(name):
    def hook(module, grad_input, grad_output):
        if grad_output[0] is not None:
            grad_norms[name] = grad_output[0].norm().item()
    return hook

for name, layer in model.named_modules():
    if isinstance(layer, (nn.Linear, nn.Sigmoid)):
        layer.register_backward_hook(hook_fn(name))

# forward + backward
x = torch.randn(32, 10)
y = torch.randn(32, 1)
loss = nn.MSELoss()(model(x), y)
loss.backward()

for name, norm in grad_norms.items():
    print(f"{name}: grad_norm={norm:.6f}")
```

sigmoid를 activation으로 쓴 3층 네트워크에서 이 코드를 실행하면 앞쪽 레이어일수록 gradient norm이 급격히 작아지는 것을 확인할 수 있습니다. activation을 ReLU로 바꾸면 norm이 균일해집니다. 이것이 "함수의 기울기 특성이 학습에 직접 영향을 준다"는 이 글의 핵심 메시지를 실험으로 보여 주는 예시입니다.

## 처음 질문으로 돌아가기

- **함수는 왜 단순한 수식이 아니라 입력과 출력의 계약으로 이해해야 할까요?**
  - 모델의 각 층은 하나의 함수이며, 입력 범위와 출력 범위가 다음 층의 기대와 맞아야 학습이 안정적으로 진행됩니다. 수식만 보면 이 범위 계약이 보이지 않지만, 함수를 "무엇이 들어오고 무엇이 나가는가"라는 계약으로 보면 층 간 불일치(스케일 차이, 포화)를 사전에 잡을 수 있습니다.
- **선형 함수의 기울기와 비선형 함수의 국소 기울기는 어떻게 다를까요?**
  - 선형 함수는 어디서든 기울기가 같으므로 gradient가 균일하게 전파됩니다. 비선형 함수는 위치에 따라 기울기가 0에서 1 이상까지 변하므로, 같은 입력이라도 모델 내부 어느 구간에 있느냐에 따라 학습 속도가 달라집니다.
- **ReLU와 sigmoid의 기울기 차이는 학습 과정에 어떤 영향을 줄까요?**
  - ReLU는 양수 구간에서 기울기가 정확히 1이므로 gradient가 감쇠 없이 전파됩니다. 반면 sigmoid는 기울기 최대값이 0.25이므로 매 층마다 gradient가 줄어들어 깊은 네트워크에서 vanishing gradient를 유발합니다. 이것이 현대 모델 대부분이 은닉층에 ReLU 계열을 쓰는 실질적인 이유입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Calculus for ML 101 (1/10): 미분이란 무엇인가](./01-what-is-derivative.md)
- **함수와 기울기 (현재 글)**
- 편미분 (예정)
- Gradient (예정)
- 연쇄 법칙 (예정)
- 손실 함수 (예정)
- 경사하강법 (예정)
- 최적화 (예정)
- 역전파 직관 (예정)
- 딥러닝에서의 미분 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Functions - Khan Academy](https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:functions)
- [Activation Functions - Stanford CS231n](https://cs231n.github.io/neural-networks-1/)
- [Deep Learning Book - MLP](https://www.deeplearningbook.org/contents/mlp.html)
- [PyTorch Activations](https://pytorch.org/docs/stable/nn.html#non-linear-activations-weighted-sum-nonlinearity)

### 예제 코드
- [book-examples/calculus-for-ml-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/calculus-for-ml-101/ko)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, Functions, Slope, Beginner

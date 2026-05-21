---
series: calculus-for-ml-101
episode: 5
title: "Calculus for ML 101 (5/10): 연쇄 법칙"
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
  - ChainRule
  - Backprop
  - Beginner
seo_description: 연쇄 법칙, 함수 합성, 바깥 함수와 안쪽 함수, gradient 곱과 backprop 기초를 ML 입문자 관점에서 정리한 글
last_reviewed: '2026-05-12'
---

# Calculus for ML 101 (5/10): 연쇄 법칙

신경망은 단일 함수가 아니라 함수 위에 함수가 겹겹이 쌓인 구조입니다. 선형 변환 뒤에 activation이 오고, 그 뒤에 또 다른 선형층과 activation이 이어지며, 마지막에는 loss function이 붙습니다. 이렇게 함수가 함수 안에 들어가는 구조에서는 미분도 한 번에 계산되지 않습니다.

연쇄 법칙은 이 합성 구조를 따라 gradient를 전달하는 규칙입니다. 바깥 함수의 미분과 안쪽 함수의 미분을 적절한 순서로 곱해 전체 미분을 얻습니다. 이 단순한 규칙이 없으면 deep learning의 학습은 사실상 불가능합니다.

이 글은 Calculus for ML 101 시리즈의 다섯 번째 글입니다.

이 글에서는 함수 합성, outer/inner 구분, 단계별 미분의 곱, zero-gradient 구간의 위험이라는 관점에서 연쇄 법칙을 설명하겠습니다. 목표는 공식을 외우는 것이 아니라, 왜 backpropagation이 뒤로 곱을 전파하는지 이해하는 것입니다.

끝까지 읽고 나면 연쇄 법칙을 “복잡한 함수 미분법”이 아니라 “깊은 네트워크에서 gradient가 전달되는 유일한 길”로 보게 될 것입니다.

![Calculus for ML 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/05/05-01-concept-at-a-glance.ko.png)
*Calculus for ML 101 5장 흐름 개요*

## 먼저 던지는 질문

- 함수가 다른 함수 안에 들어갈 때 전체 미분은 왜 단순 합이 아니라 곱으로 연결될까요?
- 바깥 함수와 안쪽 함수를 구분하는 가장 실용적인 방법은 무엇일까요?
- 단계가 여러 개인 합성함수에서 gradient는 어떤 순서로 전달될까요?

## 왜 이 글이 중요한가

딥러닝 모델은 합성함수입니다. 입력에서 출력까지 가는 길에 수많은 변환이 있고, loss는 그 전체 결과 위에서 정의됩니다. 따라서 특정 weight가 loss에 미치는 영향을 계산하려면 중간의 모든 변환을 거슬러 올라가며 gradient를 연결해야 합니다. 이 연결 규칙이 바로 연쇄 법칙입니다.

실무에서는 activation saturation, dead ReLU, exploding or vanishing gradient 같은 현상이 모두 연쇄 법칙 관점에서 설명됩니다. 여러 단계의 미분이 곱해지므로, 중간에 작은 값이 반복되면 신호가 사라지고 큰 값이 반복되면 신호가 폭발합니다. 즉 연쇄 법칙을 이해하는 것은 backpropagation의 실패 모드를 이해하는 일이기도 합니다.

또한 이 글은 이후 손실 함수, 경사하강법, 역전파 직관 글을 잇는 핵심 다리입니다. chain rule을 모르면 backward pass는 라이브러리 내부 마법처럼 보이지만, chain rule을 이해하면 그 마법은 매우 체계적인 반복 곱셈으로 바뀝니다.

## 핵심 관점

연쇄 법칙을 가장 잘 이해하는 방법은 합성함수를 여러 단계 파이프라인으로 보는 것입니다. 입력은 먼저 안쪽 함수로 들어가 중간 표현을 만들고, 그 결과가 다시 바깥 함수의 입력이 됩니다. 전체 변화율은 각 단계의 변화율을 연결해서 계산해야 하므로 자연스럽게 곱셈이 등장합니다.

이 관점은 ML에서 매우 실용적입니다. 네트워크의 각 레이어는 자기 local derivative를 갖고, backward pass는 그 local derivative를 위에서 내려온 gradient와 곱해 이전 레이어로 전달합니다. 결국 backpropagation은 연쇄 법칙을 코드로 펼친 것에 가깝습니다.

> 연쇄 법칙의 본질은 “복잡한 함수를 한 번에 미분한다”가 아니라 “각 단계의 국소 미분을 올바른 순서로 연결한다”는 데 있습니다.

## 핵심 개념

연쇄 법칙의 흐름은 다음과 같습니다.

### 먼저 합성함수를 분리해 봅니다

```python
def g(x):
    return 2 * x + 1

def f(u):
    return u ** 2

def h(x):
    return f(g(x))
```

여기서 $g(x)$는 안쪽 함수이고 $f(u)$는 바깥 함수입니다. $h(x)$를 직접 전개해 미분할 수도 있지만, 합성 구조를 유지한 채 각 단계를 따로 보는 편이 딥러닝 직관과 더 잘 맞습니다.

### 안쪽과 바깥의 미분을 분리합니다

```python
def dg(x):
    return 2.0

def df(u):
    return 2 * u
```

안쪽 함수는 입력 $x$를 중간값 $u$로 바꾸고, 바깥 함수는 그 $u$를 최종 출력으로 바꿉니다. 따라서 전체 변화율을 구하려면 $x$가 $u$를 얼마나 바꾸는지, 그리고 $u$가 최종 출력을 얼마나 바꾸는지를 모두 알아야 합니다.

### 전체 미분은 연결된 곱입니다

```python
def dh(x):
    return df(g(x)) * dg(x)
```

중요한 점은 `df`를 raw `x`가 아니라 `g(x)`에서 평가한다는 것입니다. 이 한 줄이 outer/inner 구분의 핵심입니다. 먼저 안쪽 함수가 만들어 낸 중간값에서 바깥 함수의 민감도를 계산하고, 그다음 안쪽 함수의 민감도를 곱합니다.

### 수치 미분으로 검증할 수 있습니다

```python
def deriv(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)

assert abs(dh(1.0) - deriv(h, 1.0)) < 1e-3
```

연쇄 법칙 구현이 맞는지 확인할 때 수치 미분은 좋은 기준점이 됩니다. 실제 학습 경로는 해석 미분과 자동 미분이 담당하지만, 디버깅 단계에서는 이런 작은 numerical check가 매우 유용합니다.

### 단계가 많아져도 규칙은 같습니다

```python
def chain(*derivs):
    p = 1.0
    for d in derivs:
        p *= d
    return p
```

합성 단계가 늘어나도 원리는 바뀌지 않습니다. 각 단계의 local derivative를 올바른 순서로 곱하면 됩니다. 다만 차원이 커지면 이 곱은 scalar 곱을 넘어 Jacobian과 matrix multiplication 형태로 일반화됩니다. 그래도 본질은 여전히 “단계별 local derivative의 연결”입니다.

### zero-gradient 경로를 항상 경계해야 합니다

연쇄 법칙은 곱셈이기 때문에, 중간 단계 중 하나라도 0에 가까운 gradient를 자주 내면 전체 경로의 gradient가 빠르게 줄어듭니다. sigmoid 포화 구간이나 dead ReLU 문제가 실무에서 중요하게 다뤄지는 이유가 바로 이 구조 때문입니다.

## 흔히 헷갈리는 지점

- outer derivative를 raw input에서 평가하면 합성 구조를 잘못 해석하게 됩니다.
- 곱의 순서를 아무렇게나 바꿔도 된다고 생각하면 중간값 의존성을 놓칩니다.
- 한 단계의 gradient가 0이면 전체 경로가 막힐 수 있다는 점을 과소평가하기 쉽습니다.
- 다차원에서는 chain rule이 단순 숫자 곱이 아니라 matrix multiplication으로 일반화된다는 점을 놓치기 쉽습니다.
- 수치 검증 없이 backward 결과를 당연하게 받아들이면 미묘한 구현 버그를 놓칠 수 있습니다.

## 운영 체크리스트

- [ ] 합성함수의 단계 순서와 중간값을 먼저 명시한다
- [ ] outer derivative는 inner output에서 평가된다는 점을 확인한다
- [ ] zero-gradient 구간이 전체 경로를 막을 수 있는지 점검한다
- [ ] 작은 예제에서 numerical derivative로 backward 결과를 검증한다
- [ ] 다차원 모델에서는 chain rule이 행렬 연산으로 확장된다는 점을 염두에 둔다

## 연쇄 법칙 계산 예제: sin(x^2)와 중첩 함수

공식만 보면 단순해 보이지만, 실제로는 어느 지점에서 어떤 도함수를 평가하는지 자주 헷갈립니다. 먼저 대표 예제를 단계별로 분해해 보겠습니다.

`h(x) = sin(x^2)`를 다음처럼 나눕니다.

- 안쪽 함수: `u(x) = x^2`
- 바깥 함수: `h(u) = sin(u)`

연쇄 법칙에 따라

`dh/dx = (dh/du) * (du/dx) = cos(u) * 2x = 2x cos(x^2)`

```python
import math

def h(x):
    return math.sin(x**2)

def dh_analytic(x):
    return 2*x*math.cos(x**2)

def dh_numeric(x, eps=1e-6):
    return (h(x+eps)-h(x-eps))/(2*eps)

for x in [0.2, 0.7, 1.3]:
    print(x, dh_analytic(x), dh_numeric(x))
```

이 예제를 통해 확인할 포인트는 두 가지입니다.

1. 바깥 미분 `cos(·)`는 반드시 안쪽 결과 `x^2`에서 평가해야 합니다.
2. 마지막에 안쪽 도함수 `2x`를 곱해야 전체 변화율이 완성됩니다.

중첩 단계가 늘어난 예제로 `y = exp(sin(3x+1))`도 자주 씁니다.

| 단계 | 함수 | 도함수 |
| --- | --- | --- |
| 1 | `a(x)=3x+1` | `a'(x)=3` |
| 2 | `b(a)=sin(a)` | `b'(a)=cos(a)` |
| 3 | `y(b)=exp(b)` | `y'(b)=exp(b)` |

전체 미분은 `exp(sin(3x+1)) * cos(3x+1) * 3`입니다.

## 계산 그래프 관점의 연쇄 법칙

딥러닝 구현에서는 수식을 노드와 엣지로 바꿔 보는 편이 더 실용적입니다. 각 노드는 중간값을, 각 엣지는 국소 미분을 제공합니다.

```python
# y = (x1 * x2 + x3)^2

def forward(x1, x2, x3):
    m = x1 * x2
    s = m + x3
    y = s ** 2
    cache = (x1, x2, x3, m, s)
    return y, cache

def backward(dy, cache):
    x1, x2, x3, m, s = cache
    ds = dy * (2 * s)
    dm = ds * 1.0
    dx3 = ds * 1.0
    dx1 = dm * x2
    dx2 = dm * x1
    return dx1, dx2, dx3
```

`dy=1`부터 시작해 backward를 수행하면, loss가 출력 노드에 대해 어떻게 각 입력 노드로 분배되는지 명확하게 보입니다. 이 구조가 deep network 전체로 확장되면 backpropagation이 됩니다.

| 그래프 요소 | forward 역할 | backward 역할 |
| --- | --- | --- |
| 곱셈 노드 | 값 결합 | 상대 피연산자를 곱해 gradient 전달 |
| 덧셈 노드 | 경로 합침 | 동일 gradient를 각 입력으로 복사 |
| 비선형 노드 | 표현력 부여 | local derivative로 신호 스케일링 |

## 역전파는 연쇄 법칙의 반복 적용

역전파는 새로운 수학이 아니라, 연쇄 법칙을 대규모 그래프에서 효율적으로 계산하는 알고리즘입니다. 핵심은 "상류 gradient(upstream gradient)"와 "국소 도함수(local derivative)"의 곱입니다.

```python
# 1-layer linear + sigmoid + BCE 예시의 축약 형태
import numpy as np

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

def bce_grad(a, y):
    # 확률 기반 BCE에서 dL/da
    return -(y / (a + 1e-12)) + (1 - y) / (1 - a + 1e-12)

def backward_one_sample(x, w, b, y):
    z = x @ w + b
    a = sigmoid(z)
    dL_da = bce_grad(a, y)
    da_dz = a * (1 - a)
    dL_dz = dL_da * da_dz
    dL_dw = x[:, None] * dL_dz
    dL_db = dL_dz
    return dL_dw, dL_db
```

실제 프레임워크는 이 계산을 텐서 연산으로 벡터화하고, 그래프를 자동으로 추적해 backward를 수행합니다. 그러나 내부 원리는 동일합니다.

## Jacobian 입문: 스칼라 곱에서 행렬 곱으로

지금까지 스칼라 중심으로 설명했지만, 다변수 함수에서는 도함수가 Jacobian 행렬이 됩니다.

- `f: R^n -> R^m`이면 Jacobian `J`의 크기는 `m x n`입니다.
- 연쇄 법칙은 `J_(f∘g)(x) = J_f(g(x)) · J_g(x)`로 일반화됩니다.

간단한 예제를 보겠습니다.

`g(x1, x2) = [x1 + x2, x1x2]`

`f(u1, u2) = u1^2 + 3u2`

그러면 `f∘g: R^2 -> R`이고 gradient는 1x2 행벡터로 볼 수 있습니다.

```python
import numpy as np

def jac_g(x1, x2):
    return np.array([
        [1.0, 1.0],
        [x2,  x1],
    ])

def jac_f(u1, u2):
    return np.array([[2*u1, 3.0]])

x1, x2 = 2.0, -1.0
u1, u2 = x1 + x2, x1 * x2
J = jac_f(u1, u2) @ jac_g(x1, x2)
print(J)  # d(f∘g)/dx1, d(f∘g)/dx2
```

이 예제는 "곱의 순서"가 왜 중요한지 보여 줍니다. 차원이 맞지 않으면 연산 자체가 불가능하고, 순서를 바꾸면 다른 의미가 됩니다.

## 연쇄 법칙 검증 코드: 해석 미분 vs 수치 미분 vs 자동미분

구현 신뢰성을 높이려면 세 가지 관측을 맞춰 보는 방식이 좋습니다.

1. 손으로 구한 해석 미분
2. 중앙차분 수치 미분
3. 프레임워크 자동미분

```python
import math
import torch

# 함수: y = sin((2x+1)^2)
def fn(x):
    return math.sin((2*x + 1)**2)

def d_analytic(x):
    inner = 2*x + 1
    return math.cos(inner**2) * (2*inner) * 2

def d_numeric(x, h=1e-6):
    return (fn(x+h)-fn(x-h))/(2*h)

x = 0.4

xt = torch.tensor(x, requires_grad=True)
yt = torch.sin((2*xt + 1)**2)
yt.backward()

print('analytic:', d_analytic(x))
print('numeric :', d_numeric(x))
print('autograd:', float(xt.grad))
```

세 값이 근접하면 체인 연결이 올바르다는 강한 근거가 됩니다. 값이 크게 어긋나면 연산 순서, 브로드캐스팅, 미분 불가능 지점 처리를 먼저 확인해야 합니다.

## 실전에서 자주 만나는 오류 패턴

| 증상 | 가능 원인 | 빠른 확인 |
| --- | --- | --- |
| backward는 되지만 grad가 이상하게 큼 | 중복 곱 또는 차원 브로드캐스팅 오류 | 각 노드 shape와 local derivative 출력 |
| 특정 레이어 grad가 항상 0 | 포화 활성화, detach, mask 오류 | 해당 레이어 입력 분포와 그래프 연결 |
| 수치 미분과 autograd 불일치 | 비미분 연산 포함, eps 선택 부적절 | 함수 매끄러움, eps 민감도 스윕 |
| 학습 초반부터 NaN | exp/log 구간 불안정 | clip, log-sum-exp, 안정화 수식 적용 |

오류를 줄이려면 "작은 그래프에서 검증 후 확장" 순서를 고수하는 편이 좋습니다.

## 다층 합성 함수 손계산 예제

세 단계 합성 `y = ((2x+3)^2 + 1)^3`을 손계산으로 전개해 보겠습니다.

- `a = 2x+3`
- `b = a^2 + 1`
- `y = b^3`

각 단계 도함수는 `da/dx=2`, `db/da=2a`, `dy/db=3b^2`입니다. 따라서

`dy/dx = 3b^2 * 2a * 2 = 12a b^2`

```python
def d_manual(x):
    a = 2*x + 3
    b = a*a + 1
    return 12*a*(b**2)
```

중요한 점은 중간값 `a`, `b`를 재사용하면 계산이 단순해지고 실수도 줄어든다는 것입니다. 이 재사용 전략이 바로 계산 그래프의 캐시 개념과 같습니다.

## 벡터-행렬 연쇄 법칙 미니 예제

스칼라를 넘어가면 체인 룰은 자연스럽게 행렬 곱으로 바뀝니다.

`z = Wx + b`, `a = tanh(z)`, `L = ||a - t||^2 / 2` 라고 할 때

- `dL/da = a - t`
- `da/dz = 1 - tanh(z)^2` (원소별)
- `dL/dz = dL/da ⊙ da/dz`
- `dL/dW = (dL/dz) x^T`

```python
import numpy as np

x = np.array([[0.5], [1.2]])
W = np.array([[0.3, -0.2], [0.1, 0.4]])
b = np.array([[0.0], [0.2]])
t = np.array([[0.4], [-0.1]])

z = W @ x + b
a = np.tanh(z)
dL_da = a - t
dL_dz = dL_da * (1 - np.tanh(z)**2)
dL_dW = dL_dz @ x.T
print(dL_dW)
```

이 식을 이해하면 프레임워크가 반환하는 `W.grad` 형태를 더 빠르게 검증할 수 있습니다.

## 연쇄 법칙 디버깅 체크리스트

| 체크 순서 | 확인 내용 | 실패 시 조치 |
| --- | --- | --- |
| 1 | 중간값 캐시가 forward 값과 일치하는가 | 캐시 구조 단순화 |
| 2 | local derivative의 shape가 맞는가 | 브로드캐스팅 명시 |
| 3 | 수치 미분과 부호가 일치하는가 | 연산 순서 재검토 |
| 4 | 마지막 gradient scale이 비정상적으로 큰가 | 입력 스케일, 초기화 점검 |

체인 룰 오류는 대부분 shape mismatch와 중간값 참조 실수에서 시작합니다. 작은 그래프를 손계산으로 먼저 통과시킨 뒤 모델 전체에 확장하는 습관이 가장 안정적입니다.

## 연쇄 법칙과 역전파 복잡도

합성 단계 수를 `K`, 파라미터 수를 `P`라고 두면, naive 방식으로 각 파라미터마다 독립 미분을 계산하면 비용이 급격히 커집니다. 반면 역전파는 상류 gradient를 재사용해 대부분의 연산을 공유하므로, forward와 같은 차수의 계산량으로 전체 gradient를 얻습니다.

이 점이 딥러닝에서 연쇄 법칙이 "가능한가"가 아니라 "효율적인가"의 문제로 연결되는 이유입니다.

## 체인 룰 검증을 위한 미세 오차 분석

수치 미분 검증에서 오차가 0이 아닌 이유도 이해해야 합니다. 중앙차분은 `O(h^2)` 근사 오차와 부동소수점 반올림 오차를 동시에 가집니다. 따라서 `h`를 너무 크게 잡아도, 너무 작게 잡아도 오차가 커질 수 있습니다.

```python
import math

def f(x):
    return math.sin((x+1)**3)

def d_true(x):
    return math.cos((x+1)**3) * 3 * (x+1)**2

def d_num(x, h):
    return (f(x+h)-f(x-h))/(2*h)

x = 0.3
for h in [1e-2, 1e-4, 1e-6, 1e-8]:
    err = abs(d_true(x)-d_num(x,h))
    print(h, err)
```

이 실험은 검증 실패를 곧바로 구현 버그로 단정하지 않게 해 줍니다. 먼저 `h` 민감도를 보고, 그다음 연산 그래프 연결을 의심하는 순서가 안전합니다.

## backprop 구현 시 shape 규약

연쇄 법칙의 수학은 맞는데 코드가 틀리는 대표 원인은 shape 규약 부재입니다. 팀 단위 작업에서는 아래 규약을 문서로 고정하는 편이 좋습니다.

1. 벡터는 열벡터 `(d, 1)`로 통일합니다.
2. 미니배치는 `(batch, feature)`로 통일합니다.
3. Jacobian이 암묵적으로 숨어 있는 연산(`sum`, `mean`)은 축(axis)을 명시합니다.

규약만 맞춰도 체인 룰 오류의 상당수를 예방할 수 있습니다.

## 자동미분 의존도를 낮추는 학습 루틴

프레임워크 자동미분은 강력하지만, 연쇄 법칙 이해 없이 사용하면 디버깅 속도가 급격히 떨어집니다. 다음 루틴을 반복하면 구현 안정성이 크게 올라갑니다.

1. 새 연산 블록을 추가할 때 1개 샘플 기준 수치 미분 검증을 먼저 수행합니다.
2. 블록 단위 backward를 통과하면 배치 차원으로 확장합니다.
3. 마지막으로 전체 모델에서 gradient norm 분포를 확인합니다.

```python
def gradcheck_scalar(fn, x, d_analytic, h=1e-6):
    num = (fn(x+h)-fn(x-h))/(2*h)
    return abs(num-d_analytic(x))
```

또한 팀 협업에서는 "forward 캐시 항목"과 "backward 입력/출력 shape"를 문서화해야 합니다. 코드 리뷰에서 수식 자체보다 shape contract 위반이 더 흔하게 발견됩니다.

| 문서 항목 | 예시 | 목적 |
| --- | --- | --- |
| 노드 이름 | `z1`, `a1`, `logits` | 계산 경로 추적 |
| 텐서 shape | `(batch, hidden)` | 브로드캐스팅 오류 예방 |
| local derivative | `da/dz = 1-a^2` | backward 검증 근거 |
| 안정화 규칙 | `eps=1e-12` | NaN 방지 |

연쇄 법칙을 수식-코드-로그 세 층으로 연결해 두면, 모델 규모가 커져도 원인 추적 비용이 선형적으로 증가하지 않습니다.

현업에서는 새 레이어를 넣을 때마다 작은 합성함수 테스트를 먼저 통과시키는 절차를 표준화하면, 대규모 학습 실패를 사전에 줄일 수 있습니다.

연쇄 법칙을 정확히 쓰면 학습 속도보다 먼저 디버깅 속도가 개선됩니다. 수식과 코드의 대응 관계가 명확해져서, 어느 노드에서 gradient가 끊겼는지 빠르게 특정할 수 있기 때문입니다.

작은 비용으로 큰 효과를 보는 방법은 "새 연산 추가 시 수치 미분 검증 1회"를 팀 규칙으로 고정하는 것입니다. 이 한 단계가 누적되면 복잡한 모델에서도 backprop 신뢰도가 크게 높아집니다.

## 정리

연쇄 법칙은 합성함수의 미분을 각 단계의 local derivative 곱으로 계산하는 규칙입니다. 신경망처럼 함수가 길게 이어진 구조에서는 이 규칙이 아니면 전체 gradient를 효율적으로 구할 수 없습니다. 그래서 chain rule은 미적분의 세부 기법이 아니라 딥러닝 학습의 중심 규칙입니다.

실무에서 gradient가 사라지거나 폭발하는 현상도 연쇄 법칙 구조 위에서 이해하는 편이 가장 정확합니다. 여러 단계의 미분이 곱해지므로, 어떤 activation과 initialization을 선택하느냐가 gradient 전달 품질을 좌우합니다.

다음 글에서는 이 gradient가 최종적으로 무엇을 최적화하고 있는지, 즉 손실 함수가 어떤 숫자를 만들고 왜 그 설계가 모델 품질을 결정하는지 보겠습니다.

## 처음 질문으로 돌아가기

- **함수가 다른 함수 안에 들어갈 때 전체 미분은 왜 단순 합이 아니라 곱으로 연결될까요?**
  - 합성함수에서는 입력 변화가 각 단계를 연속 통과하면서 스케일이 누적되기 때문입니다. `sin(x^2)` 예제에서 `cos(x^2)`와 `2x`를 곱해야 전체 변화율이 맞는 것처럼, 단계별 민감도는 곱으로 연결되어야 실제 전달량을 보존합니다.
- **바깥 함수와 안쪽 함수를 구분하는 가장 실용적인 방법은 무엇일까요?**
  - 계산 그래프에서 노드 단위로 중간변수를 먼저 정의하면 구분이 분명해집니다. `u=x^2`, `h=sin(u)`처럼 이름을 분리하고, 바깥 미분은 항상 "중간값에서 평가"한다는 규칙을 적용하면 구현 오류를 크게 줄일 수 있습니다.
- **단계가 여러 개인 합성함수에서 gradient는 어떤 순서로 전달될까요?**
  - forward의 역순으로 전달됩니다. 출력에서 시작한 상류 gradient를 각 노드의 local derivative와 곱해 이전 노드로 보냅니다. Jacobian 관점에서는 이 과정이 행렬 곱 체인으로 일반화되며, 역전파는 그 연산을 효율적으로 수행한 구현입니다.

## 처음 질문으로 돌아가기

- **함수가 다른 함수 안에 들어갈 때 전체 미분은 왜 단순 합이 아니라 곱으로 연결될까요?**
  - 본문의 기준은 연쇄 법칙를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **바깥 함수와 안쪽 함수를 구분하는 가장 실용적인 방법은 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **단계가 여러 개인 합성함수에서 gradient는 어떤 순서로 전달될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Calculus for ML 101 (1/10): 미분이란 무엇인가](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): 함수와 기울기](./02-functions-and-slope.md)
- [Calculus for ML 101 (3/10): 편미분](./03-partial-derivatives.md)
- [Calculus for ML 101 (4/10): Gradient](./04-gradient.md)
- **연쇄 법칙 (현재 글)**
- 손실 함수 (예정)
- 경사하강법 (예정)
- 최적화 (예정)
- 역전파 직관 (예정)
- 딥러닝에서의 미분 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Chain Rule - Khan Academy](https://www.khanacademy.org/math/ap-calculus-ab/ab-differentiation-2-new/ab-3-1a/v/chain-rule-introduction)
- [Backpropagation - CS231n](https://cs231n.github.io/optimization-2/)
- [Deep Learning Book - Backprop](https://www.deeplearningbook.org/contents/mlp.html)
- [Automatic Differentiation - Baydin et al.](https://arxiv.org/abs/1502.05767)

### 예제 코드
- [book-examples/calculus-for-ml-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/calculus-for-ml-101/ko)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, ChainRule, Backprop, Beginner

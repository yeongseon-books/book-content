---
series: calculus-for-ml-101
episode: 3
title: "Calculus for ML 101 (3/10): 편미분"
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
  - PartialDerivative
  - MultiVariable
  - Beginner
seo_description: 편미분, 다변수 함수, 변수 고정, 변수별 기울기와 ML 가중치 직관을 ML 입문자 관점에서 정리한 글
last_reviewed: '2026-05-12'
---

# Calculus for ML 101 (3/10): 편미분

현실의 머신러닝 모델은 입력 하나만 받는 단순한 함수가 아닙니다. 가중치 수백 개, 수천 개, 때로는 수십억 개를 가진 다변수 함수입니다. 이런 함수에서 "지금 어떤 파라미터가 손실에 얼마나 책임이 있는가"를 알려면 전체를 한 번에 보는 대신 각 변수를 따로 떼어 볼 수 있어야 합니다.

편미분은 바로 그 분해를 가능하게 합니다. 나머지 변수는 고정해 두고 하나만 움직였을 때 함수가 어떻게 변하는지를 측정하는 방식입니다. 이 약속이 있어야 모델의 각 가중치에 대해 독립적인 업데이트 신호를 만들 수 있습니다.

이 글에서는 다변수 함수, 변수 고정, 변수별 책임 할당이라는 관점에서 편미분을 설명하겠습니다. 핵심은 수학 기호가 아니라, 모델 파라미터마다 "이 변수는 지금 얼마만큼 손실에 기여했는가"를 읽는 방법입니다.

끝까지 읽고 나면 편미분을 단지 미분의 확장판이 아니라, backpropagation이 각 파라미터에 책임을 나눠 주는 기본 단위로 이해하게 됩니다.

![Calculus for ML 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/03/03-01-concept-at-a-glance.ko.png)
*Calculus for ML 101 3장 흐름 개요*

## 먼저 던지는 질문

- 입력이 여러 개인 함수에서는 왜 변수별로 기울기를 따로 봐야 할까요?
- 편미분에서 "다른 변수는 고정한다"는 약속은 실제로 무엇을 뜻할까요?
- 같은 함수라도 어떤 변수에 대해 미분하느냐에 따라 왜 다른 값이 나올까요?

## 왜 이 글이 중요한가

딥러닝 모델의 손실 함수는 거의 항상 다변수 함수입니다. 하나의 weight만 바꿔도 loss가 달라지고, bias를 바꿔도 loss가 달라지며, 입력 스케일이나 내부 activation 역시 영향을 줍니다. 학습은 결국 이 다변수 함수의 표면에서 적절한 방향을 찾는 과정이므로, 변수별 변화량을 분리해 읽는 편미분이 필수입니다.

실무적으로도 이 개념은 매우 직접적입니다. optimizer는 weight마다 독립된 gradient 값을 사용해 업데이트를 수행합니다. 만약 편미분 개념이 없다면 "모델 전체가 얼마나 나빠졌는가"만 알 수 있을 뿐, 어느 파라미터를 얼마나 바꿔야 하는지는 알 수 없습니다.

또한 편미분을 이해해야 다음 글의 gradient를 벡터로 받아들일 수 있습니다. gradient는 여러 편미분을 한데 묶은 것이므로, 편미분의 의미가 흐리면 gradient도 방향 벡터가 아니라 숫자 목록처럼 보이기 쉽습니다.

## 핵심 관점

편미분을 가장 쉽게 이해하는 방법은 다변수 함수를 3차원 지형처럼 상상한 뒤, 한 축만 따라 잘라 보는 것입니다. $x$를 볼 때는 $y$를 고정하고, $y$를 볼 때는 $x$를 고정합니다. 이렇게 만든 단면에서의 기울기가 바로 편미분입니다.

이 약속은 단순하지만 매우 강력합니다. 함수 전체를 한 번에 다루기 어렵더라도, 변수 하나씩의 국소 반응으로 쪼개면 각 파라미터의 책임을 계산할 수 있기 때문입니다. ML에서 각 weight가 자신의 gradient를 갖는 이유도 이 단면 분석 덕분입니다.

> 편미분은 "전체를 포기한다"가 아니라 "한 번에 하나씩 본다"는 전략입니다. 나머지를 고정하는 약속이 있어야 변수별 책임이 분리됩니다.

## 핵심 개념

편미분의 흐름은 아래처럼 정리할 수 있습니다.

### 다변수 함수는 입력 축이 여러 개인 함수입니다

```python
def f(x, y):
    return x ** 2 + 3 * y
```

이 함수는 입력이 두 개입니다. $x$를 바꾸면 $x^2$ 항 때문에 함수값이 바뀌고, $y$를 바꾸면 $3y$ 항 때문에 함수값이 바뀝니다. 두 입력이 동시에 영향을 주므로, 어느 입력이 얼마나 기여하는지 따로 분리해 보는 것이 편미분의 출발점입니다.

### x만 움직이면 x에 대한 편미분입니다

```python
def partial_x(f, x, y, h=1e-5):
    return (f(x + h, y) - f(x - h, y)) / (2 * h)
```

여기서는 $y$를 그대로 둔 채 $x$만 좌우로 조금 움직입니다. 이 코드가 암묵적으로 말하는 것은 명확합니다. 지금은 $x$의 책임만 보겠다는 뜻입니다. 다른 변수는 여전히 함수값에 영향을 주지만, 이번 측정에서는 바꾸지 않습니다.

### y만 움직이면 y에 대한 편미분입니다

```python
def partial_y(f, x, y, h=1e-5):
    return (f(x, y + h) - f(x, y - h)) / (2 * h)
```

이번에는 반대로 $x$를 고정하고 $y$만 봅니다. 같은 함수라도 어느 변수를 선택하느냐에 따라 변화율이 달라진다는 사실이 중요합니다. 다변수 함수에서는 "기울기"가 하나의 숫자가 아니라 변수별 숫자 묶음으로 나타나기 시작합니다.

### 여러 편미분을 함께 계산하면 gradient의 재료가 됩니다

```python
def partials(f, x, y):
    return partial_x(f, x, y), partial_y(f, x, y)
```

이 함수는 gradient vector의 가장 단순한 전 단계입니다. 아직 벡터 해석까지는 가지 않더라도, 각 변수마다 독립적인 변화율이 존재하고 이것을 일정한 순서로 묶어 관리해야 한다는 점이 핵심입니다.

### ML에서는 각 가중치가 자기 편미분을 받습니다

```python
def loss(w1, w2):
    return (w1 - 1) ** 2 + (w2 + 2) ** 2

g1, g2 = partials(loss, 0.0, 0.0)  # responsibility per weight
```

이 코드는 두 개의 weight가 각자 어떤 방향으로 움직여야 loss를 줄일 수 있는지 보여 줍니다. $g1$과 $g2$는 같은 loss에서 나왔지만 서로 다른 책임을 갖습니다. backpropagation은 결국 이런 편미분을 네트워크 전체 파라미터에 대해 효율적으로 계산하는 절차입니다.

### 변수 순서와 고정값은 실무에서 중요합니다

gradient를 사용할 때는 변수 순서가 문서화되어 있어야 합니다. 예를 들어 첫 번째 값이 $w1$용인지 $w2$용인지 흐려지면 업데이트 대상이 섞입니다. 또한 "고정된 변수"도 중요합니다. 편미분은 나머지를 없애는 것이 아니라, 현재 값으로 고정한 상태에서 한 변수의 국소 반응만 읽는 것입니다.

## 해석 미분과 수치 미분의 비교: 다변수 함수에서

1장에서 다룬 수치 미분 검증을 다변수 함수로 확장합니다. 변수가 많아지면 해석 미분의 정확성을 보장하기 어려워지므로, 수치 검증의 중요성이 더 커집니다.

### 2변수 함수의 해석 편미분

$f(x, y) = x^2 y + \sin(xy)$를 봅시다.

$$\frac{\partial f}{\partial x} = 2xy + y\cos(xy)$$
$$\frac{\partial f}{\partial y} = x^2 + x\cos(xy)$$

```python
import numpy as np

def f(x, y):
    return x ** 2 * y + np.sin(x * y)

def df_dx_analytic(x, y):
    return 2 * x * y + y * np.cos(x * y)

def df_dy_analytic(x, y):
    return x ** 2 + x * np.cos(x * y)

def df_dx_numeric(f, x, y, h=1e-7):
    return (f(x + h, y) - f(x - h, y)) / (2 * h)

def df_dy_numeric(f, x, y, h=1e-7):
    return (f(x, y + h) - f(x, y - h)) / (2 * h)

# 검증
x, y = 1.5, 2.0
print(f"df/dx: analytic={df_dx_analytic(x, y):.6f}, numeric={df_dx_numeric(f, x, y):.6f}")
print(f"df/dy: analytic={df_dy_analytic(x, y):.6f}, numeric={df_dy_numeric(f, x, y):.6f}")
```

해석 미분과 수치 미분의 차이가 $10^{-6}$ 이내이면 유도가 맞다고 신뢰할 수 있습니다. 이 패턴은 커스텀 loss 함수를 작성할 때 특히 자주 씁니다.

### 고차원 함수에서의 편미분: numpy 벡터화

실제 ML에서는 파라미터가 벡터나 행렬이므로, 편미분도 벡터화된 형태로 계산합니다.

```python
import numpy as np

def loss_vector(w, X, y):
    """MSE loss: w는 (d,) 벡터, X는 (n, d), y는 (n,)"""
    pred = X @ w
    return np.mean((pred - y) ** 2)

def grad_vector_analytic(w, X, y):
    """dL/dw = (2/n) * X^T (Xw - y)"""
    n = len(y)
    pred = X @ w
    return (2.0 / n) * X.T @ (pred - y)

def grad_vector_numeric(loss_fn, w, X, y, h=1e-5):
    """각 원소별 수치 편미분"""
    grad = np.zeros_like(w)
    for i in range(len(w)):
        w_plus = w.copy(); w_plus[i] += h
        w_minus = w.copy(); w_minus[i] -= h
        grad[i] = (loss_fn(w_plus, X, y) - loss_fn(w_minus, X, y)) / (2 * h)
    return grad

# 테스트
np.random.seed(0)
X = np.random.randn(10, 3)
y = X @ np.array([2.0, -1.0, 0.5]) + np.random.randn(10) * 0.1
w = np.zeros(3)

analytic = grad_vector_analytic(w, X, y)
numeric = grad_vector_numeric(loss_vector, w, X, y)
print(f"Analytic grad: {analytic}")
print(f"Numeric grad:  {numeric}")
print(f"Max diff: {np.max(np.abs(analytic - numeric)):.2e}")
```

여기서 핵심은 `grad_vector_numeric` 함수입니다. 변수(weight) 하나를 움직일 때 나머지를 모두 고정한다는 편미분의 정의가 `w_plus[i] += h` 한 줄로 구현됩니다. 나머지 원소는 그대로 두므로, 정확히 $i$번째 변수에 대한 편미분만 측정합니다.

### 수치 편미분의 비용 문제

위 코드에서 변수가 $d$개이면 함수를 $2d$번 호출해야 합니다. BERT의 파라미터가 1억 1천만 개이므로, 수치 편미분으로 전체 gradient를 구하려면 함수를 2억 2천만 번 호출해야 합니다. 이것이 autograd(역방향 자동 미분)가 필수인 이유입니다. autograd는 함수를 단 2번(forward + backward)만 호출하면 모든 파라미터의 편미분을 한꺼번에 계산합니다.

| 방법 | 함수 호출 횟수 | 용도 |
| --- | --- | --- |
| 수치 미분 | $2d$ | 검증, 디버깅 |
| 전방향 자동 미분 | $d$ | 변수가 적을 때 |
| 역방향 자동 미분 | 2 (forward + backward) | 학습 (표준) |

## 편미분의 교차 효과: 혼합 편미분

같은 함수를 서로 다른 변수에 대해 두 번 편미분할 수 있습니다. 이것이 혼합 편미분(mixed partial derivative)이고, Hessian 행렬의 비대각 성분에 해당합니다.

### 의미와 계산

$f(x, y) = x^2 y + xy^3$이면:

$$\frac{\partial^2 f}{\partial x \partial y} = 2x + 3y^2$$

```python
def f(x, y):
    return x ** 2 * y + x * y ** 3

def mixed_partial_xy(f, x, y, h=1e-5):
    """d^2f / dx dy를 수치적으로 계산"""
    return (f(x+h, y+h) - f(x+h, y-h) - f(x-h, y+h) + f(x-h, y-h)) / (4 * h * h)

x, y = 1.0, 2.0
analytic = 2 * x + 3 * y ** 2  # = 14.0
numeric = mixed_partial_xy(f, x, y)
print(f"Mixed partial: analytic={analytic:.4f}, numeric={numeric:.4f}")
```

혼합 편미분은 "x를 바꿨을 때 y에 대한 민감도가 어떻게 달라지는가"를 말합니다. optimizer 관점에서는 변수 간 상호작용을 나타내므로, Newton 방법이나 자연 경사법에서 사용됩니다. 일반적인 SGD에서는 직접 사용하지 않지만, 학습 지형의 구조를 이해할 때 중요합니다.

## 편미분과 PyTorch autograd

PyTorch에서 편미분이 어떻게 자동으로 계산되는지 확인합니다.

```python
import torch

# 2변수 loss 함수
w1 = torch.tensor(0.5, requires_grad=True)
w2 = torch.tensor(-1.0, requires_grad=True)

loss = (w1 - 2.0) ** 2 + 3 * (w2 + 1.0) ** 2

# backward()는 모든 leaf tensor에 대한 편미분을 자동 계산합니다
loss.backward()

print(f"dL/dw1 = {w1.grad.item():.4f}")  # 2*(0.5 - 2) = -3.0
print(f"dL/dw2 = {w2.grad.item():.4f}")  # 6*(-1 + 1) = 0.0
```

`w1.grad`는 $\partial L / \partial w_1$이고, `w2.grad`는 $\partial L / \partial w_2$입니다. 각각 해당 변수만 움직였을 때의 loss 변화율입니다. `loss.backward()` 한 번의 호출로 모든 편미분이 계산된다는 점이 autograd의 핵심 효율입니다.

### 행렬 파라미터에 대한 편미분

실제 모델에서는 weight가 스칼라가 아니라 행렬입니다. 이때도 편미분의 논리는 동일합니다.

```python
import torch
import torch.nn as nn

# 간단한 선형 모델
model = nn.Linear(3, 1, bias=False)
X = torch.randn(5, 3)
y = torch.randn(5, 1)

# forward + backward
pred = model(X)
loss = ((pred - y) ** 2).mean()
loss.backward()

# weight.grad는 (1, 3) 행렬 - 각 원소가 편미분
print(f"weight shape: {model.weight.shape}")
print(f"grad shape:   {model.weight.grad.shape}")
print(f"grad values:  {model.weight.grad}")
```

weight가 (1, 3) 행렬이면 grad도 (1, 3)입니다. 각 원소 `grad[0, i]`는 "weight[0, i]만 미세하게 바꿨을 때 loss가 얼마나 변하는가"를 나타냅니다. 이것이 편미분의 정의 그 자체입니다.

## 편미분의 기하학적 해석: 등고선과 방향

편미분을 시각적으로 이해하는 가장 좋은 방법은 등고선(contour) 위에서 보는 것입니다.

### 등고선 위의 편미분 방향

```python
import numpy as np

def loss(w1, w2):
    return (w1 - 2) ** 2 + 4 * (w2 + 1) ** 2

# 격자 위에서 편미분 계산
w1_range = np.linspace(-1, 5, 7)
w2_range = np.linspace(-4, 2, 7)

print(f"{'w1':<6} {'w2':<6} {'dL/dw1':<10} {'dL/dw2':<10} {'방향 해석'}")
print("-" * 50)
for w1 in [0.0, 2.0, 4.0]:
    for w2 in [-3.0, -1.0, 1.0]:
        g1 = 2 * (w1 - 2)
        g2 = 8 * (w2 + 1)
        direction = []
        if g1 > 0: direction.append("w1 줄여야")
        elif g1 < 0: direction.append("w1 늘려야")
        if g2 > 0: direction.append("w2 줄여야")
        elif g2 < 0: direction.append("w2 늘려야")
        print(f"{w1:<6.1f} {w2:<6.1f} {g1:<10.2f} {g2:<10.2f} {', '.join(direction)}")
```

이 표에서 핵심은 다음과 같습니다. $w_1 = 2, w_2 = -1$에서 두 편미분이 모두 0이 됩니다. 이것이 최솟값 지점입니다. 그 외의 점에서는 각 편미분의 부호가 업데이트 방향을 가리킵니다.

## 흔히 헷갈리는 지점

- 편미분을 계산하면서 모든 변수를 동시에 바꾸면 편미분이 아니라 전혀 다른 값을 보게 됩니다.
- 고정된 변수는 중요하지 않다고 오해하기 쉽지만, 실제 편미분 값은 고정된 변수의 현재 값에도 의존할 수 있습니다.
- 변수 순서를 명시하지 않으면 gradient vector 해석이 틀어집니다.
- 편미분과 total derivative를 같은 것으로 생각하면 연쇄 효과를 설명하기 어려워집니다.
- 각 변수에 다른 스케일이 걸려 있을 때 동일한 크기의 gradient를 같은 의미로 받아들이면 안 됩니다.
- 수치 편미분의 $O(d)$ 비용과 autograd의 $O(1)$ 비용을 혼동하면 디버깅 도구를 학습 루프에 잘못 넣을 수 있습니다.

## 운영 체크리스트

- [ ] 다변수 loss를 볼 때 어떤 변수를 고정하고 무엇을 움직이는지 분명히 한다
- [ ] gradient vector의 변수 순서를 코드와 문서에서 일치시킨다
- [ ] 편미분 값은 각 변수의 책임 신호라는 점을 팀 내 공통 언어로 맞춘다
- [ ] 수치 검증 시 변수마다 같은 방식의 centered difference를 적용한다
- [ ] 고정된 변수의 현재 값도 해석에 영향을 준다는 점을 잊지 않는다
- [ ] 커스텀 loss 작성 후 수치 편미분으로 autograd 결과를 검증한다
- [ ] 파라미터 수가 클 때는 수치 검증을 일부 샘플 변수에만 적용한다

## 실전 응용: 선형 회귀의 편미분 전체 유도

편미분이 실제 학습에서 어떻게 작동하는지, 가장 간단한 모델인 2-파라미터 선형 회귀로 처음부터 끝까지 추적합니다.

### 모델과 손실 정의

모델: $\hat{y} = w_1 x_1 + w_2 x_2$
손실: $L = \frac{1}{n} \sum_{i=1}^{n} (\hat{y}_i - y_i)^2$

### 각 파라미터에 대한 편미분 유도

$$\frac{\partial L}{\partial w_1} = \frac{2}{n} \sum_{i=1}^{n} (\hat{y}_i - y_i) \cdot x_{i1}$$

$$\frac{\partial L}{\partial w_2} = \frac{2}{n} \sum_{i=1}^{n} (\hat{y}_i - y_i) \cdot x_{i2}$$

유도에서 핵심은 $w_1$에 대해 미분할 때 $w_2 x_2$ 부분은 상수 취급되어 사라진다는 점입니다. 이것이 편미분의 "고정" 약속이 실제로 하는 일입니다.

### 코드로 구현한 학습 루프

```python
import numpy as np

np.random.seed(42)
n = 50
X = np.random.randn(n, 2)
true_w = np.array([3.0, -2.0])
y = X @ true_w + np.random.randn(n) * 0.2

# 학습
w = np.zeros(2)
lr = 0.05

for epoch in range(30):
    pred = X @ w
    residual = pred - y
    
    # 편미분 계산
    grad_w1 = (2.0 / n) * np.sum(residual * X[:, 0])
    grad_w2 = (2.0 / n) * np.sum(residual * X[:, 1])
    
    # 업데이트
    w[0] -= lr * grad_w1
    w[1] -= lr * grad_w2
    
    if epoch % 10 == 0:
        loss = np.mean(residual ** 2)
        print(f"epoch={epoch:2d}  w=[{w[0]:.3f}, {w[1]:.3f}]  loss={loss:.4f}")

print(f"\nFinal w: [{w[0]:.4f}, {w[1]:.4f}]")
print(f"True  w: [{true_w[0]:.4f}, {true_w[1]:.4f}]")
```

두 편미분이 독립적으로 계산되고, 각각 대응하는 weight를 업데이트합니다. 이것이 편미분 기반 학습의 전체 구조입니다.

### 편미분 크기와 수렴 속도의 관계

| epoch | grad_w1 | grad_w2 | 해석 |
| --- | --- | --- | --- |
| 0 | 큼 | 큼 | 두 weight 모두 정답과 멀리 있음 |
| 10 | 작음 | 작음 | 수렴 중 |
| 30 | ~0 | ~0 | 수렴 완료, 두 편미분이 0에 수렴 |

편미분이 0에 가까워진다는 것은 해당 변수를 더 움직여도 loss가 거의 변하지 않는다는 뜻입니다. 모든 편미분이 동시에 0이면 gradient vector 전체가 영벡터가 되고, 이것이 수렴 조건입니다.

## 변수 간 스케일 차이와 편미분 해석

실무에서 흔히 만나는 문제입니다. 두 변수의 스케일이 크게 다르면 편미분의 절대값 비교만으로는 "어떤 변수가 더 중요한가"를 판단할 수 없습니다.

### 스케일 불일치 예시

```python
import numpy as np

# x1은 0~1 범위, x2는 0~1000 범위
np.random.seed(0)
X = np.column_stack([
    np.random.rand(100),          # 작은 스케일
    np.random.rand(100) * 1000    # 큰 스케일
])
y = 5 * X[:, 0] + 0.01 * X[:, 1] + np.random.randn(100) * 0.1

# gradient 계산
w = np.zeros(2)
pred = X @ w
residual = pred - y
grad = (2.0 / len(y)) * X.T @ residual

print(f"grad_w1 = {grad[0]:.4f}  (x1 scale: 0~1)")
print(f"grad_w2 = {grad[1]:.4f}  (x2 scale: 0~1000)")
print(f"|grad_w2| >> |grad_w1| but true_w1=5 >> true_w2=0.01")
```

gradient의 크기는 변수의 스케일에 영향을 받습니다. $x_2$의 스케일이 크면 해당 편미분도 커집니다. 이것이 feature 정규화가 필요한 이유이고, Adam 같은 adaptive optimizer가 변수별로 학습률을 조정하는 이유이기도 합니다.

### 해결 전략 비교

| 전략 | 방법 | 장점 | 단점 |
| --- | --- | --- | --- |
| 입력 정규화 | 모든 feature를 mean=0, std=1로 | 단순, 효과적 | 원본 해석 어려움 |
| Adaptive lr | Adam, RMSProp 등 | 자동 스케일 조정 | 하이퍼파라미터 추가 |
| 수동 스케일링 | 도메인 지식으로 조정 | 해석 유지 | 노동 집약적 |

실무에서는 입력 정규화 + Adam 조합이 가장 보편적입니다. 편미분의 절대값을 해석할 때는 항상 해당 변수의 스케일을 함께 고려해야 합니다.

### 편미분 부호로 읽는 업데이트 방향 요약

편미분의 부호는 해당 변수의 업데이트 방향을 직접 결정합니다. gradient descent에서 $w \leftarrow w - \eta \cdot \frac{\partial L}{\partial w}$이므로:

| 편미분 부호 | 의미 | 업데이트 방향 |
| --- | --- | --- |
| 양수 (+) | w를 늘리면 loss 증가 | w를 줄여야 함 |
| 음수 (-) | w를 늘리면 loss 감소 | w를 늘려야 함 |
| 0 | w를 바꿔도 loss 불변 | 업데이트 불필요 (수렴) |

이 표를 머리에 두면 학습 로그에서 gradient 부호를 볼 때 바로 해석할 수 있습니다. 부호가 계속 바뀌면 learning rate가 너무 크거나 loss surface가 진동 지형이라는 신호입니다.

## 정리

편미분은 여러 입력을 가진 함수에서 하나의 변수만 움직였을 때의 국소 변화율을 측정하는 도구입니다. 나머지를 고정한다는 약속 덕분에, 함수 전체의 복잡성을 잠시 접어 두고 변수별 책임을 분리해서 읽을 수 있습니다.

ML에서 이 개념은 곧 파라미터별 gradient로 이어집니다. 모델이 아무리 커져도 각 weight는 자신의 편미분 값을 받아 업데이트되고, 그 값들이 모여 gradient vector와 optimizer의 입력이 됩니다. 즉 편미분은 수학적 세부사항이 아니라, 학습 책임을 분배하는 기본 단위입니다.

다음 글에서는 이 편미분들을 하나의 벡터로 묶은 gradient를 보겠습니다. 그러면 변수별 책임이 어떻게 하나의 방향 정보로 합쳐지는지 더 선명해집니다.

## 처음 질문으로 돌아가기

- **입력이 여러 개인 함수에서는 왜 변수별로 기울기를 따로 봐야 할까요?**
  - 다변수 함수에서 하나의 숫자로는 모든 변수의 영향을 동시에 표현할 수 없습니다. 변수별로 기울기를 분리해야 각 파라미터가 loss에 얼마나 기여하는지 개별적으로 파악할 수 있고, 그래야 파라미터마다 적절한 크기와 방향으로 업데이트할 수 있습니다.
- **편미분에서 "다른 변수는 고정한다"는 약속은 실제로 무엇을 뜻할까요?**
  - 다른 변수의 현재 값을 그대로 유지한 채 관심 변수만 미세하게 변화시킨다는 뜻입니다. 이 약속이 있어야 측정 결과가 순수하게 한 변수의 효과만 반영합니다. 코드에서는 `w_plus[i] += h`처럼 한 원소만 건드리고 나머지는 그대로 두는 것으로 구현됩니다.
- **같은 함수라도 어떤 변수에 대해 미분하느냐에 따라 왜 다른 값이 나올까요?**
  - 각 변수가 함수에 기여하는 방식이 다르기 때문입니다. $f(x, y) = x^2 + 3y$에서 $x$에 대한 편미분은 $2x$이고 $y$에 대한 편미분은 $3$입니다. $x$는 비선형으로 기여하고 $y$는 선형으로 기여하므로 민감도가 다릅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Calculus for ML 101 (1/10): 미분이란 무엇인가](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): 함수와 기울기](./02-functions-and-slope.md)
- **편미분 (현재 글)**
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
- [Partial Derivatives - Khan Academy](https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives)
- [Multivariable Calculus - MIT OCW](https://ocw.mit.edu/courses/18-02-multivariable-calculus-fall-2007/)
- [Deep Learning Book - Chapter 4](https://www.deeplearningbook.org/contents/numerical.html)
- [JAX Automatic Differentiation](https://jax.readthedocs.io/en/latest/notebooks/autodiff_cookbook.html)

### 예제 코드
- [book-examples/calculus-for-ml-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/calculus-for-ml-101/ko)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, PartialDerivative, MultiVariable, Beginner

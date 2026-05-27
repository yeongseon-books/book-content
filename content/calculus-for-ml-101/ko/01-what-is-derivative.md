---
series: calculus-for-ml-101
episode: 1
title: "Calculus for ML 101 (1/10): 미분이란 무엇인가"
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
  - Derivative
  - Math
  - Beginner
seo_description: 미분의 정의, 변화율, 접선, 극한, 수치 미분 직관을 ML 입문자 관점에서 정리한 글
last_reviewed: '2026-05-12'
---

# Calculus for ML 101 (1/10): 미분이란 무엇인가

머신러닝에서 모델이 학습된다고 말할 때, 실제로는 손실이 줄어드는 방향으로 파라미터를 조금씩 움직이는 계산이 반복됩니다. 이때 가장 먼저 필요한 정보는 지금 서 있는 지점에서 함수가 어느 방향으로 얼마나 빠르게 변하는가입니다. 미분은 바로 그 질문에 답하는 가장 기본적인 도구입니다.

이 글은 Calculus for ML 101 시리즈의 첫 번째 글입니다.

처음 미분을 배울 때 많은 사람이 공식을 먼저 외웁니다. 하지만 실무에서 더 오래 남는 것은 공식보다 멘탈 모델입니다. 미분은 함수값 자체를 보는 도구가 아니라, 함수가 한 점 근처에서 어떤 움직임을 보이는지를 읽는 도구라는 관점을 먼저 잡아야 이후의 gradient, backpropagation, optimizer가 자연스럽게 이어집니다.

이 글에서는 평균 변화율, 접선, 극한, 수치 미분을 하나의 흐름으로 묶어 미분을 설명하겠습니다. 여기서 미분을 제대로 잡아 두면 이후 글에서 나오는 손실 함수의 gradient를 더 이상 추상적인 숫자로 보지 않게 됩니다.

끝까지 읽고 나면 미분을 "공식 조작"이 아니라 "학습 방향을 읽는 첫 번째 센서"로 이해하게 될 것입니다.

![Calculus for ML 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/01/01-01-concept-at-a-glance.ko.png)
*Calculus for ML 101 1장 흐름 개요*

## 먼저 던지는 질문

- 머신러닝에서 말하는 학습은 왜 미분과 직접 연결될까요?
- 평균 변화율과 순간 변화율은 무엇이 다르고, 왜 둘을 구분해야 할까요?
- 접선의 기울기와 도함수는 어떤 관계로 이해하면 가장 실용적일까요?

## 왜 이 글이 중요한가

경사하강법은 손실을 줄이는 방향으로 이동하는 절차이고, 그 방향은 미분에서 나옵니다. 역전파는 거대한 합성함수의 미분을 효율적으로 계산하는 방법입니다. 학습률은 그 미분값을 얼마나 크게 반영할지 정하는 하이퍼파라미터입니다. 즉, 학습 루프의 핵심 용어들은 거의 모두 미분 위에 서 있습니다.

프레임워크를 사용하면 gradient는 자동으로 계산됩니다. 그래서 미분을 몰라도 모델은 돌아갑니다. 그러나 훈련이 불안정하거나, gradient가 0에 가까워지거나, loss가 갑자기 발산하는 순간부터는 숫자를 해석할 언어가 필요합니다. 그때 미분 감각이 없으면 현상을 로그로만 보고, 미분 감각이 있으면 원인을 함수의 모양과 변화율로 연결해 볼 수 있습니다.

특히 이 시리즈는 미적분을 독립된 수학 과목으로 설명하려는 것이 아니라, ML 엔지니어가 학습 과정을 읽기 위해 꼭 필요한 최소한의 미분 직관을 만드는 데 목적이 있습니다. 첫 글에서 이 축을 제대로 세우면 뒤의 글들은 개별 기법이 아니라 하나의 연결된 시스템으로 읽히기 시작합니다.

## 핵심 관점

미분을 가장 실용적으로 이해하는 방법은 "한 점에서 함수값이 얼마인가"보다 "그 점 근처에서 조금 움직이면 함수가 어떻게 반응하는가"를 보는 것입니다. 평균 변화율은 넓은 구간을 보고, 미분은 그 구간을 무한히 좁혀 한 점의 국소적 움직임을 읽습니다. 이 차이를 잡는 순간, 미분은 암기 대상이 아니라 측정 도구가 됩니다.

ML에서는 이 국소적 움직임이 특히 중요합니다. 파라미터를 아주 조금 바꿨을 때 loss가 증가하는지 감소하는지 알아야 다음 스텝을 결정할 수 있기 때문입니다. 미분은 "조금 바꿨을 때 어떤 일이 일어날까?"라는 질문을 수학적으로 안정된 형태로 바꾼 결과입니다.

> 미분은 함수 전체를 한 번에 설명하는 도구가 아니라, 지금 서 있는 지점에서 어느 방향으로 얼마나 움직여야 하는지 알려 주는 국소 신호입니다.

## 핵심 개념

미분은 변화율, 접선, 극한, 근사 계산이 한 덩어리로 연결된 개념입니다. 아래 흐름을 먼저 머리에 두고 읽는 편이 좋습니다.

### 변화율은 먼저 평균에서 시작합니다

두 점 $a$와 $b$ 사이에서 함수가 얼마나 변했는지는 평균 변화율로 계산할 수 있습니다. 이 값은 구간 전체를 요약하는 기울기입니다. 직선이라면 이 값만으로도 충분하지만, 곡선 함수에서는 어느 지점을 보느냐에 따라 기울기가 달라지므로 평균만으로는 부족합니다.

그래서 미분은 평균 변화율을 출발점으로 삼되, 구간 폭을 계속 줄여 한 점의 순간 변화율에 도달합니다. 이 과정이 극한이고, 접선의 기울기와 도함수 개념이 여기서 만납니다.

### 함수를 하나 두고 직접 봅시다

```python
def f(x):
    return x ** 2
```

이 함수는 가장 단순한 비선형 함수 중 하나입니다. $x$가 커질수록 함수값이 더 빠르게 커지므로, 위치에 따라 기울기가 달라진다는 사실을 보여 주기에 좋습니다. 미분을 처음 설명할 때 이 예제가 자주 쓰이는 이유도 여기에 있습니다.

### 평균 변화율은 구간 전체의 기울기입니다

```python
def avg_rate(f, a, b):
    return (f(b) - f(a)) / (b - a)
```

이 식은 두 점을 잇는 secant line의 기울기입니다. 아직 미분은 아니지만, 미분이 무엇을 극한으로 보완하는지 드러내는 핵심 출발점입니다. 실무 감각으로 바꾸면, 평균 변화율은 "이 구간 전체에서는 대체로 이렇게 움직였다"는 요약입니다.

### 수치 미분은 미분 직관을 계산으로 확인하는 방법입니다

```python
def deriv(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)
```

이 코드는 centered difference를 사용합니다. 좌우에서 같은 폭만큼 이동한 뒤 평균 기울기를 계산하므로, 한쪽만 보는 전진 차분보다 보통 더 안정적입니다. 실제 딥러닝 학습에서 이런 형태를 직접 쓰지는 않지만, autograd 결과가 맞는지 검증할 때는 여전히 강력한 기준점이 됩니다.

여기서 중요한 실무 포인트는 $h$를 무조건 작게 잡는다고 더 좋은 것이 아니라는 사실입니다. 너무 작으면 부동소수점 오차가 커지고, 너무 크면 근사 오차가 커집니다. 수치 미분은 이론적으로 단순하지만 실제 계산에서는 수치 안정성을 늘 함께 봐야 합니다.

### 접선의 기울기는 곧 미분값입니다

```python
slope = deriv(f, 2.0)  # about 4.0
```

$x=2$ 근처에서 함수가 얼마나 빠르게 변하는지 수치적으로 읽은 값입니다. 접선의 기울기가 약 4라는 뜻은, 그 점 근처에서 입력을 아주 조금 늘리면 출력이 대략 네 배 속도로 증가한다는 뜻입니다. 이 "근처에서의 반응"이 바로 ML에서 gradient가 하는 역할과 연결됩니다.

### 손실 함수에 연결하면 미분의 역할이 선명해집니다

```python
def loss(w):
    return (w - 3) ** 2

g = deriv(loss, 0.0)   # negative -> increase w to reduce loss
```

손실 함수의 미분값이 음수라는 것은 현재 지점에서 오른쪽으로 움직이면 손실이 줄어든다는 뜻입니다. 이 한 줄이 경사하강법의 핵심 직관입니다. 미분은 단지 함수의 성질을 설명하는 것이 아니라, 다음 업데이트 방향을 결정하는 실질적인 신호입니다.

### 이 글에서 꼭 가져갈 문장

미분은 함수값 자체보다 변화의 방향과 속도를 알려 줍니다. 평균 변화율은 넓은 구간을 보고, 도함수는 한 점의 국소적 반응을 봅니다. 그리고 손실 함수에 이 관점을 적용하면, 미분은 곧 학습 방향을 정하는 정보가 됩니다.

## 미분 공식의 기초: 멱함수 규칙에서 합성함수까지

여기까지 수치적 직관을 다뤘다면, 이제 해석적(analytic) 미분 공식을 정리합니다. 수치 미분은 검증에 좋지만 계산 비용이 높습니다. 해석 미분은 닫힌 형태의 공식을 미리 유도해 둠으로써, 수천만 개의 파라미터에 대한 gradient를 빠르게 계산할 수 있게 만듭니다.

### 멱함수 규칙 (Power Rule)

가장 기본적인 미분 공식입니다. $f(x) = x^n$일 때 $f'(x) = n \cdot x^{n-1}$입니다.

```python
import numpy as np

def power_rule_check(n, x):
    """해석 미분과 수치 미분을 비교합니다."""
    analytic = n * x ** (n - 1)
    h = 1e-7
    numeric = ((x + h) ** n - (x - h) ** n) / (2 * h)
    return analytic, numeric, abs(analytic - numeric)

# n=2, 3, 4에 대해 x=2.0에서 검증
for n in [2, 3, 4]:
    a, num, err = power_rule_check(n, 2.0)
    print(f"x^{n} at x=2: analytic={a:.6f}, numeric={num:.6f}, error={err:.2e}")
# x^2에서 x=2: analytic=4.000000, numeric=4.000000, error=3.55e-10
# x^3에서 x=2: analytic=12.000000, numeric=12.000000, error=1.43e-09
# x^4에서 x=2: analytic=32.000000, numeric=32.000000, error=5.70e-09
```

오차가 $10^{-9}$ 수준이면 해석 미분과 수치 미분이 일치한다고 봐도 됩니다. 이 패턴은 이후 더 복잡한 함수의 gradient를 검증할 때도 동일하게 적용됩니다.

### 상수배 규칙과 합 규칙

$f(x) = c \cdot g(x)$이면 $f'(x) = c \cdot g'(x)$이고, $f(x) = g(x) + h(x)$이면 $f'(x) = g'(x) + h'(x)$입니다. 단순하지만 ML에서 매우 자주 쓰입니다. 손실 함수가 여러 항의 합으로 이루어질 때, 각 항의 gradient를 독립적으로 구한 뒤 합칠 수 있다는 뜻이기 때문입니다.

```python
# 합 규칙 예시: L(w) = 0.5*(w-3)^2 + 2*w
# dL/dw = 0.5*2*(w-3) + 2 = (w-3) + 2 = w-1
def loss_sum(w):
    return 0.5 * (w - 3) ** 2 + 2 * w

def loss_sum_grad(w):
    return (w - 3) + 2  # = w - 1

w_test = 1.5
print(f"analytic grad: {loss_sum_grad(w_test)}")  # 0.5
print(f"numeric grad:  {(loss_sum(w_test+1e-7) - loss_sum(w_test-1e-7))/(2e-7):.6f}")
```

### 곱 규칙 (Product Rule)

$f(x) = g(x) \cdot h(x)$일 때 $f'(x) = g'(x) \cdot h(x) + g(x) \cdot h'(x)$입니다. 정규화 항이 포함된 손실이나, attention score 계산처럼 두 함수의 곱이 등장하는 상황에서 필요합니다.

### 연쇄 법칙 맛보기

$f(g(x))$의 미분은 $f'(g(x)) \cdot g'(x)$입니다. 이 규칙은 5장에서 전체를 다루겠지만, 미분 공식 전체를 관통하는 핵심 아이디어이므로 여기서 한 번 맛보기로 봅니다.

```python
import math

# 함수: f(x) = sin(x^2)
# 도함수: f'(x) = cos(x^2) * 2x  (chain rule)
def f_composed(x):
    return math.sin(x ** 2)

def f_composed_grad(x):
    return math.cos(x ** 2) * 2 * x

x = 1.0
analytic = f_composed_grad(x)
numeric = (f_composed(x + 1e-7) - f_composed(x - 1e-7)) / (2e-7)
print(f"chain rule check: analytic={analytic:.6f}, numeric={numeric:.6f}")
# chain rule 확인: analytic=1.080605, numeric=1.080605
```

## 수치 미분 심화: h 선택과 오차 분석

수치 미분에서 $h$를 어떻게 정하느냐에 따라 결과의 신뢰도가 달라집니다. 이 절에서는 $h$ 선택이 실제로 어떤 영향을 미치는지 실험으로 확인합니다.

### 전진 차분 vs 중앙 차분

```python
import numpy as np

def f(x):
    return x ** 3

# x=2에서의 해석 미분값: 3*x^2 = 12.0
x = 2.0
true_deriv = 12.0

h_values = [1e-2, 1e-4, 1e-6, 1e-8, 1e-10, 1e-12, 1e-14]

print(f"{'h':<12} {'forward err':<16} {'central err':<16}")
print("-" * 44)
for h in h_values:
    forward = (f(x + h) - f(x)) / h
    central = (f(x + h) - f(x - h)) / (2 * h)
    fwd_err = abs(forward - true_deriv)
    ctr_err = abs(central - true_deriv)
    print(f"{h:<12.0e} {fwd_err:<16.2e} {ctr_err:<16.2e}")
```

실행하면 다음과 같은 패턴이 나타납니다.

| h | 전진 차분 오차 | 중앙 차분 오차 |
| --- | --- | --- |
| 1e-2 | ~6e-2 | ~2e-4 |
| 1e-4 | ~6e-4 | ~2e-8 |
| 1e-6 | ~6e-6 | ~1e-10 |
| 1e-8 | ~6e-8 | ~1e-8 (반등 시작) |
| 1e-10 | 부동소수점 지배 | 부동소수점 지배 |
| 1e-14 | 쓸모없음 | 쓸모없음 |

중앙 차분은 $h$가 적당한 범위(대략 $10^{-5}$ ~ $10^{-7}$)일 때 가장 정확합니다. 너무 작으면 $f(x+h)$와 $f(x-h)$의 차이가 부동소수점 정밀도 이하로 떨어져 오히려 오차가 커집니다. 실무에서는 `h = 1e-5`를 기본값으로 쓰고, 함수값의 스케일이 매우 크거나 작을 때만 조정합니다.

### gradient checking 실전 패턴

PyTorch에서 autograd 결과를 수치 미분으로 검증하는 패턴입니다.

```python
import torch

def gradient_check(fn, inputs, eps=1e-5, atol=1e-4):
    """각 입력 원소에 대해 수치 미분과 autograd를 비교합니다."""
    inputs = inputs.detach().requires_grad_(True)
    loss = fn(inputs)
    loss.backward()
    autograd = inputs.grad.clone()

    numeric = torch.zeros_like(inputs)
    flat = inputs.data.view(-1)
    for i in range(flat.numel()):
        orig = flat[i].item()
        flat[i] = orig + eps
        loss_plus = fn(inputs).item()
        flat[i] = orig - eps
        loss_minus = fn(inputs).item()
        flat[i] = orig
        numeric.view(-1)[i] = (loss_plus - loss_minus) / (2 * eps)

    max_diff = (autograd - numeric).abs().max().item()
    passed = max_diff < atol
    return passed, max_diff

# 사용 예
fn = lambda w: ((w - torch.tensor([1.0, 2.0, 3.0])) ** 2).sum()
w = torch.tensor([0.5, 1.5, 2.5])
ok, diff = gradient_check(fn, w)
print(f"gradient check {'PASS' if ok else 'FAIL'}, max_diff={diff:.2e}")
```

이 패턴은 커스텀 레이어를 만들거나, 기존 코드의 backward가 의심스러울 때 가장 먼저 사용하는 디버깅 도구입니다. 통과 기준은 보통 상대 오차 $10^{-4}$ 이내입니다.

## 미분이 존재하지 않는 경우

모든 점에서 미분이 정의되는 것은 아닙니다. ML에서도 이 문제가 실제로 등장합니다.

### 불연속점

함수가 점프하는 지점에서는 좌극한과 우극한이 다르므로 미분이 정의되지 않습니다. 실무에서는 step function 대신 sigmoid를 쓰는 이유가 여기에 있습니다.

### 뾰족한 점 (Kink)

$f(x) = |x|$는 $x=0$에서 좌미분과 우미분이 다릅니다. ReLU 활성화 함수가 정확히 이 구조입니다.

```python
# ReLU의 미분: x > 0이면 1, x < 0이면 0, x = 0에서는 정의 모호
def relu(x):
    return max(0, x)

def relu_grad(x):
    if x > 0:
        return 1
    elif x < 0:
        return 0
    else:
        return 0  # 관례상 0 또는 0.5를 사용

# PyTorch는 x=0에서 grad=0을 반환합니다
import torch
x = torch.tensor(0.0, requires_grad=True)
y = torch.relu(x)
y.backward()
print(f"ReLU grad at x=0: {x.grad.item()}")  # 0.0
```

프레임워크마다 kink point에서의 gradient 처리가 다를 수 있으므로, 활성화 함수를 직접 구현할 때는 이 경계 조건을 명시적으로 정해야 합니다.

### 발산하는 미분

$f(x) = x^{1/3}$는 $x=0$에서 미분값이 무한대입니다. 이런 상황은 드물지만, 특정 loss 함수에서 예측값이 정답과 정확히 일치할 때 비슷한 현상이 생길 수 있습니다. `log(0)` 방어와 같은 수치 안정성 처리가 필요한 이유입니다.

## 미분과 학습 루프의 연결: 완전한 예제

이 절에서는 미분이 실제 학습 루프에서 어떻게 사용되는지 처음부터 끝까지 추적합니다.

### 문제 설정

입력 $x$와 정답 $y$가 주어질 때, 파라미터 $w$를 찾아 $\hat{y} = w \cdot x$가 $y$에 가까워지도록 합니다. 손실은 $L(w) = (wx - y)^2$입니다.

### 미분 유도

$$\frac{dL}{dw} = 2(wx - y) \cdot x$$

이 식은 멱함수 규칙과 연쇄 법칙만으로 유도됩니다. 미분값이 양수이면 $w$를 줄여야 loss가 감소하고, 음수이면 $w$를 늘려야 합니다.

### 학습 루프 구현

```python
import numpy as np

# 데이터: y = 4x에 노이즈 추가
np.random.seed(42)
X = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
Y = 4.0 * X + np.random.randn(5) * 0.3

# 학습 파라미터
w = 0.0
lr = 0.01
history = []

for epoch in range(20):
    # forward
    pred = w * X
    loss = np.mean((pred - Y) ** 2)

    # backward (해석 미분)
    grad = np.mean(2 * (pred - Y) * X)

    # update
    w = w - lr * grad
    history.append({'epoch': epoch, 'w': w, 'loss': loss, 'grad': grad})

    if epoch % 5 == 0:
        print(f"epoch={epoch:2d}  w={w:.4f}  loss={loss:.4f}  grad={grad:.4f}")
```

출력에서 관찰할 수 있는 패턴은 세 가지입니다.

1. **초반**: grad 절대값이 크고, w가 빠르게 움직이며, loss가 급격히 줄어듭니다.
2. **중반**: grad가 점점 작아지면서 업데이트 폭도 줄어듭니다.
3. **후반**: grad가 거의 0에 가까워지고, w가 정답(~4.0) 근처에서 안정됩니다.

이 세 단계는 gradient descent의 보편적인 수렴 패턴이며, 그 모든 단계를 지배하는 것이 미분값입니다.

### 학습률에 따른 수렴 비교

```python
for lr in [0.001, 0.01, 0.05, 0.1]:
    w = 0.0
    for _ in range(50):
        grad = np.mean(2 * (w * X - Y) * X)
        w = w - lr * grad
    final_loss = np.mean((w * X - Y) ** 2)
    print(f"lr={lr:.3f}  final_w={w:.4f}  final_loss={final_loss:.6f}")
```

| learning rate | 50 epoch 후 w | 최종 loss | 관찰 |
| --- | --- | --- | --- |
| 0.001 | ~2.8 | 높음 | 수렴 미완 |
| 0.01 | ~3.97 | 낮음 | 안정 수렴 |
| 0.05 | ~3.99 | 최저 | 빠른 수렴 |
| 0.1 | 발산 | 증가 | lr 과대 |

학습률이 너무 크면 gradient 방향으로 너무 멀리 이동해 오히려 loss가 증가합니다. 미분값의 크기와 학습률의 곱이 업데이트 크기를 결정하므로, 두 값의 상호작용을 이해해야 학습을 안정적으로 제어할 수 있습니다.

### gradient norm으로 학습 상태 읽기

gradient의 크기(norm)는 학습 상태를 진단하는 간접 지표입니다. norm이 큰 초반에는 파라미터가 정답과 멀리 있다는 뜻이고, norm이 0에 수렴하면 수렴했거나 안장점(saddle point)에 빠졌다는 뜻입니다.

```python
# gradient norm 기록
grad_norms = [abs(h["grad"]) for h in history]
print(f"초반 norm: {grad_norms[0]:.4f}")
print(f"중반 norm: {grad_norms[9]:.4f}")
print(f"후반 norm: {grad_norms[19]:.4f}")
```

이 값을 TensorBoard나 W\&B에 기록해 두면 학습 중 gradient가 폭주(exploding)하거나 소실(vanishing)되는 시점을 사후에 정확히 짚을 수 있습니다. 미분 개념이 실제 운영 모니터링으로 연결되는 지점이 바로 여기입니다.

## 흔히 헷갈리는 지점

- 미분값과 함수값은 다릅니다. 함수값이 크다고 미분값도 큰 것은 아니고, 그 반대도 마찬가지입니다.
- 평균 변화율과 순간 변화율을 같은 개념으로 다루면 곡선 함수의 중요한 성질을 놓치게 됩니다.
- 수치 미분은 편리하지만 정답 그 자체가 아닙니다. $h$ 선택과 부동소수점 오차의 영향을 항상 받습니다.
- 기울기의 크기만 보고 부호를 무시하면 업데이트 방향을 반대로 해석할 수 있습니다.
- 극한이 성립하지 않는 지점에서는 미분이 존재하지 않을 수 있습니다. 불연속점이나 뾰족한 점에서 특히 주의해야 합니다.
- "미분 = 기울기"라고만 외우면 다변수로 넘어갈 때 혼란이 생깁니다. 미분은 "국소적 선형 근사의 계수"라고 이해하는 편이 확장성이 좋습니다.

## 운영 체크리스트

- [ ] 손실 함수를 볼 때 현재 점에서의 기울기 부호를 먼저 해석한다
- [ ] 평균 변화율과 순간 변화율을 구분해 설명할 수 있다
- [ ] 수치 미분은 검증용이고, 실제 학습은 해석 미분 또는 자동 미분이 맡는다는 점을 기억한다
- [ ] gradient가 이상할 때 작은 예제로 centered difference 검증을 해 본다
- [ ] 기울기의 크기와 방향을 각각 따로 읽는 습관을 갖는다
- [ ] 커스텀 레이어를 작성한 뒤에는 gradient check를 반드시 실행한다
- [ ] 학습률 변경 전에 현재 gradient norm 크기를 먼저 확인한다

## 정리

미분은 함수가 한 점 근처에서 어떤 방향과 속도로 변하는지 알려 주는 도구입니다. 접선, 극한, 도함수는 각각 다른 주제가 아니라 이 국소적 변화를 읽기 위해 서로 맞물린 개념입니다. 이 관점을 잡아 두면 미분은 더 이상 기호 조작이 아니라, 현재 상태를 해석하는 센서가 됩니다.

ML에서는 이 센서가 손실 함수 위에서 작동합니다. 손실의 미분은 파라미터를 어느 방향으로 움직여야 손실이 줄어드는지 알려 주고, 그 정보가 optimizer의 입력이 됩니다. 결국 "모델이 학습한다"는 문장은 "손실의 미분을 읽고 반복적으로 업데이트한다"는 문장으로 더 구체화됩니다.

다음 글에서는 함수와 기울기 자체를 조금 더 그래프 중심으로 보겠습니다. 미분을 한 점의 변화율로 이해했다면, 이제는 함수의 모양과 기울기가 어떻게 연결되는지 살펴볼 차례입니다.

## 처음 질문으로 돌아가기

- **머신러닝에서 말하는 학습은 왜 미분과 직접 연결될까요?**
  - 학습은 손실을 줄이는 방향으로 파라미터를 반복 업데이트하는 과정입니다. "줄이는 방향"을 알려면 현재 점에서 손실이 어느 쪽으로 감소하는지 알아야 하고, 그 정보가 바로 미분값(gradient)입니다. 미분 없이는 다음 스텝의 방향을 결정할 수 없으므로, 학습 자체가 성립하지 않습니다.
- **평균 변화율과 순간 변화율은 무엇이 다르고, 왜 둘을 구분해야 할까요?**
  - 평균 변화율은 넓은 구간의 전체 기울기를 요약한 값이고, 순간 변화율은 구간 폭을 0에 수렴시켜 한 점의 국소적 기울기를 읽은 값입니다. 곡선 함수에서는 위치마다 기울기가 다르므로, 현재 점에서의 정확한 업데이트 방향을 알기 위해 순간 변화율이 필요합니다.
- **접선의 기울기와 도함수는 어떤 관계로 이해하면 가장 실용적일까요?**
  - 접선은 함수를 한 점 근처에서 직선으로 근사한 것이고, 그 직선의 기울기가 곧 그 점에서의 도함수 값입니다. 도함수는 모든 점에서의 접선 기울기를 하나의 함수로 정리한 것이므로, "함수의 기울기 지도"라고 이해하면 gradient 개념으로 자연스럽게 확장됩니다.

<!-- toc:begin -->
## 시리즈 목차

- **미분이란 무엇인가 (현재 글)**
- 함수와 기울기 (예정)
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
- [Calculus - Khan Academy](https://www.khanacademy.org/math/calculus-1)
- [Essence of Calculus - 3Blue1Brown](https://www.3blue1brown.com/topics/calculus)
- [Deep Learning Book - Numerical Computation](https://www.deeplearningbook.org/contents/numerical.html)
- [NumPy Numerical Differentiation](https://numpy.org/doc/stable/reference/generated/numpy.gradient.html)

### 예제 코드
- [book-examples/calculus-for-ml-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/calculus-for-ml-101/ko)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, Derivative, Math, Beginner

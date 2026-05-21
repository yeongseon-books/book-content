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

## 먼저 던지는 질문

- 함수가 다른 함수 안에 들어갈 때 전체 미분은 왜 단순 합이 아니라 곱으로 연결될까요?
- 바깥 함수와 안쪽 함수를 구분하는 가장 실용적인 방법은 무엇일까요?
- 단계가 여러 개인 합성함수에서 gradient는 어떤 순서로 전달될까요?

## 큰 그림

![Calculus for ML 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/05/05-01-concept-at-a-glance.ko.png)

*Calculus for ML 101 5장 흐름 개요*

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

## 정리

연쇄 법칙은 합성함수의 미분을 각 단계의 local derivative 곱으로 계산하는 규칙입니다. 신경망처럼 함수가 길게 이어진 구조에서는 이 규칙이 아니면 전체 gradient를 효율적으로 구할 수 없습니다. 그래서 chain rule은 미적분의 세부 기법이 아니라 딥러닝 학습의 중심 규칙입니다.

실무에서 gradient가 사라지거나 폭발하는 현상도 연쇄 법칙 구조 위에서 이해하는 편이 가장 정확합니다. 여러 단계의 미분이 곱해지므로, 어떤 activation과 initialization을 선택하느냐가 gradient 전달 품질을 좌우합니다.

다음 글에서는 이 gradient가 최종적으로 무엇을 최적화하고 있는지, 즉 손실 함수가 어떤 숫자를 만들고 왜 그 설계가 모델 품질을 결정하는지 보겠습니다.


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

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, ChainRule, Backprop, Beginner

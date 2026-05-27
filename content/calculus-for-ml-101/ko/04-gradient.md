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

이 글은 Calculus for ML 101 시리즈의 4번째 글입니다.

Gradient는 바로 그때 필요한 표현입니다. 여러 편미분을 순서 있는 벡터로 묶어, 함수가 가장 빠르게 증가하는 방향을 하나의 객체로 나타냅니다. 그래서 gradient는 단순한 숫자 모음이 아니라, 현재 지점에서 움직일 방향과 신호 강도를 함께 담은 구조입니다.

이 글에서는 gradient를 방향, 크기, 등고선, 반대 방향이라는 관점에서 설명하겠습니다. 핵심은 “편미분이 여러 개 있다”에서 멈추지 않고, 그것이 왜 업데이트 방향이 되는지 이해하는 것입니다.

끝까지 읽고 나면 gradient를 벡터 기호가 아니라 손실 지형 위에서 길을 찾는 지도처럼 해석하게 될 것입니다.

![Calculus for ML 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/04/04-01-concept-at-a-glance.ko.png)
*Calculus for ML 101 4장 흐름 개요*

## 먼저 던지는 질문

- 여러 편미분을 하나의 gradient vector로 묶는다는 것은 정확히 무엇을 뜻할까요?
- gradient의 방향과 크기는 각각 어떤 실무 의미를 가질까요?
- 왜 gradient는 손실이 가장 빠르게 증가하는 방향을 가리킬까요?

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

예를 들어 여기서는 첫 번째 축으로는 왼쪽, 두 번째 축으로는 위쪽 성분이 있다는 뜻입니다. 중요한 것은 각 성분을 따로 보는 것을 넘어서, 이 둘이 합쳐져 하나의 방향 화살표를 만든다는 사실입니다.

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

## gradient 하강 경로를 수치로 시각화하기

gradient를 실제 업데이트 경로로 읽으려면, 등고선 위 점이 어떻게 이동하는지를 숫자로 추적하는 연습이 가장 효과적입니다. 아래 코드는 2차원 손실 함수에서 초기점을 두고 경사하강법을 수행하면서 좌표, 손실, gradient norm을 동시에 기록합니다.

```python
import numpy as np

def loss(w):
    x, y = w
    return (x - 1.5) ** 2 + 3.0 * (y + 0.5) ** 2

def grad(w):
    x, y = w
    return np.array([2.0 * (x - 1.5), 6.0 * (y + 0.5)])

def run_gd(w0, lr=0.1, steps=20):
    w = np.array(w0, dtype=float)
    history = []
    for t in range(steps):
        g = grad(w)
        history.append({
            'step': t,
            'x': float(w[0]),
            'y': float(w[1]),
            'loss': float(loss(w)),
            'gnorm': float(np.linalg.norm(g)),
        })
        w = w - lr * g
    return history

hist = run_gd(w0=[-2.0, 2.0], lr=0.12, steps=12)
for row in hist[:5]:
    print(row)
```

`x`보다 `y` 축의 곡률이 3배 크기 때문에, 동일한 learning rate에서도 `y` 방향 업데이트가 더 크게 흔들릴 수 있습니다. 이처럼 경로를 숫자로 보면, 왜 어떤 축에서 진동이 먼저 시작되는지 설명할 수 있습니다.

| 관찰 | 해석 | 대응 |
| --- | --- | --- |
| loss는 내려가는데 x 이동이 느림 | x 축 곡률이 완만함 | lr 유지, step 수 증가 |
| y 좌표가 과도하게 왕복 | y 축 곡률 대비 lr 과대 | lr 감소 또는 축 정규화 |
| gnorm이 초반 급감 후 정체 | 평평한 구간 진입 | lr schedule 또는 momentum 검토 |

## gradient norm 모니터링과 경보 기준

실무에서는 gradient 값 자체보다 norm 시계열이 더 먼저 이상 신호를 알려 줍니다. norm 로그는 exploding/vanishing, 잘못된 스케일링, dtype 문제를 빠르게 식별하는 공통 지표입니다.

```python
import numpy as np

def norms_from_grads(grad_list):
    out = []
    for t, g in enumerate(grad_list):
        out.append((t, float(np.linalg.norm(g))))
    return out

grads = [
    np.array([0.8, -0.4]),
    np.array([0.3, -0.1]),
    np.array([0.06, -0.02]),
    np.array([0.005, -0.001]),
]
print(norms_from_grads(grads))
```

운영 로그에서는 절대값 하나로 판단하기보다, 구간별 변화율과 함께 해석해야 합니다.

| 패턴 | 전형적 의미 | 우선 점검 |
| --- | --- | --- |
| norm이 반복적으로 10배 이상 급증 | 폭주 가능성 | lr, mixed precision 스케일러, clipping |
| norm이 매우 작은 값으로 고정 | 소실 또는 포화 | activation, 초기화, 입력 스케일 |
| norm 분산이 배치마다 과도함 | 미니배치 노이즈 과다 | batch size, 데이터 섞기 정책 |
| norm은 정상인데 loss만 정체 | 방향성 문제 | 손실 정의, 라벨 품질, 모델 표현력 |

현장에서 자주 쓰는 기준은 다음과 같습니다.

1. epoch마다 평균 norm, 95퍼센타일 norm을 함께 기록합니다.
2. 연속 N step 동안 norm이 임계치 이하이면 vanishing 경고를 냅니다.
3. 임계치 이상이 M회 연속이면 clipping 여부를 강제 점검합니다.

## gradient와 방향도함수의 관계

gradient를 벡터라고 이해한 다음 단계는 방향도함수와의 연결입니다. 단위 벡터 `u` 방향으로 함수가 얼마나 변하는지는 `∇f(x) · u`로 계산합니다. 즉 gradient는 모든 방향도함수를 한꺼번에 담은 기준 벡터입니다.

```python
import numpy as np

def f(w):
    x, y = w
    return x**2 + 2*x*y + 3*y**2

def grad_f(w):
    x, y = w
    return np.array([2*x + 2*y, 2*x + 6*y])

w = np.array([1.0, -0.5])
u = np.array([1.0, 2.0])
u = u / np.linalg.norm(u)

directional = grad_f(w) @ u
print('directional derivative =', directional)
```

같은 점에서 방향을 바꿔 계산하면 값이 달라집니다. 그중 최대값은 `||∇f||`이고, 그때의 방향이 gradient 방향과 일치합니다. 이 사실이 gradient를 "가장 가파른 증가 방향"으로 해석하는 수학적 근거입니다.

| 방향 선택 | 방향도함수 부호 | 의미 |
| --- | --- | --- |
| `u = grad / ||grad||` | 양수 최대 | 가장 빠른 상승 |
| `u = -grad / ||grad||` | 음수 최소 | 가장 빠른 하강 |
| `u ⟂ grad` | 0 근처 | 등고선 접선 방향 이동 |

## PyTorch에서 gradient 디버깅하기

자동미분을 쓸 때도 gradient 검증 습관은 필요합니다. 특히 `requires_grad`, `detach`, in-place 연산 때문에 신호가 끊기는 경우가 흔합니다.

```python
import torch

x = torch.tensor([[1.0, -1.0], [0.5, 2.0]], requires_grad=True)
w = torch.tensor([[0.2], [0.3]], requires_grad=True)
y_true = torch.tensor([[1.0], [0.0]])

y_pred = x @ w
loss = ((y_pred - y_true) ** 2).mean()
loss.backward()

print('loss:', float(loss))
print('w.grad:', w.grad.view(-1))
print('x.grad norm:', x.grad.norm())
```

다음 체크리스트를 적용하면 대부분의 gradient 문제를 빠르게 좁힐 수 있습니다.

- `param.grad is None`이면 그래프 연결이 끊겼는지 확인합니다.
- `grad` 값이 모두 0이면 activation 포화 또는 dead 경로를 의심합니다.
- `grad`가 `inf`/`nan`이면 입력 스케일, 손실 안정성, 학습률을 점검합니다.
- backward 직후 `torch.nn.utils.clip_grad_norm_` 적용 전후 norm을 함께 기록합니다.

```python
total_norm = torch.norm(torch.stack([p.grad.norm() for p in [w] if p.grad is not None]))
print('total grad norm:', float(total_norm))
```

## 등고선 해석 실전 규칙

등고선 그림을 볼 때는 단순히 "화살표가 아래로 간다" 수준을 넘어, 곡률과 축별 스케일을 같이 읽어야 합니다.

| 등고선 모양 | 수학적 힌트 | 학습에서 보이는 현상 |
| --- | --- | --- |
| 원형에 가까움 | 축별 곡률 유사 | 안정적 수렴 |
| 길게 늘어난 타원 | 축별 곡률 불균형 | 지그재그 경로, 느린 수렴 |
| 능선/협곡 구조 | 조건수 악화 | lr 민감도 증가 |
| 다중 분지 | 비볼록성 | 초기값 따라 경로 분기 |

좌표계 변환(정규화, whitening)을 적용하면 타원을 원형에 가깝게 만들어 경로를 단순화할 수 있습니다. 이 관점은 optimizer를 바꾸기 전에 먼저 시도할 가치가 높습니다.

## 고차원에서 gradient를 읽는 법

고차원에서는 등고선 그림을 직접 그릴 수 없으므로, 요약 지표와 투영 분석이 필요합니다. 핵심은 전체 벡터를 작은 수의 관측값으로 안정적으로 축약하는 것입니다.

```python
import numpy as np

def summarize_grad(g):
    return {
        'l2': float(np.linalg.norm(g)),
        'linf': float(np.max(np.abs(g))),
        'mean_abs': float(np.mean(np.abs(g))),
        'sparsity(<1e-6)': float(np.mean(np.abs(g) < 1e-6)),
    }

g = np.random.randn(10000) * 0.01
print(summarize_grad(g))
```

실전에서는 레이어별로 이 요약을 기록합니다.

| 지표 | 용도 |
| --- | --- |
| L2 norm | 전체 신호 강도 추적 |
| L∞ norm | 극단값 폭주 감시 |
| 평균 절대값 | 전반적 업데이트 크기 추정 |
| 희소도 | dead unit 증가 감시 |
| cosine similarity(연속 step) | 방향 안정성 추적 |

또한 연속 step 간 cosine similarity를 계산하면, gradient 방향이 일관적인지 확인할 수 있습니다.

```python
def cosine(a, b, eps=1e-12):
    return float((a @ b) / ((np.linalg.norm(a) * np.linalg.norm(b)) + eps))
```

값이 지속적으로 음수로 떨어지면 업데이트가 같은 계곡에서 왕복하고 있을 가능성이 높습니다. 이때는 learning rate 조정, momentum 도입, 입력 정규화 순으로 점검하는 편이 안전합니다.

## 좌표 스케일과 gradient 해석의 함정

동일한 수학식이라도 입력 스케일이 바뀌면 gradient 분포가 크게 달라집니다. 예를 들어 `x`는 0~1 범위인데 `y`는 0~1000 범위라면, 같은 손실식에서도 `y` 축 편미분이 압도적으로 커질 수 있습니다. 이때 업데이트가 사실상 `y` 축만 따라가면 모델은 수렴이 느리거나 진동하게 됩니다.

```python
import numpy as np

def grad_with_scale(x, y):
    # toy loss: (x-1)^2 + (y-1)^2
    return np.array([2*(x-1), 2*(y-1)])

raw = grad_with_scale(0.2, 800.0)
scaled = grad_with_scale(0.2, 0.8)
print('raw grad   :', raw, 'norm=', np.linalg.norm(raw))
print('scaled grad:', scaled, 'norm=', np.linalg.norm(scaled))
```

실무에서는 입력 정규화와 feature scaling이 단지 전처리 편의가 아니라 gradient 품질 관리라는 점을 반드시 연결해서 봐야 합니다.

| 점검 항목 | 질문 | 기대 상태 |
| --- | --- | --- |
| 입력 스케일 | 특성별 분산이 과도하게 다른가 | 표준화 또는 적절한 스케일링 적용 |
| 레이어별 grad norm | 특정 레이어만 과도하게 큰가 | 레이어 간 norm 편차가 과하지 않음 |
| 업데이트 비율 | `||Δw|| / ||w||`가 안정적인가 | 극단적 스파이크 없음 |

## 실험 기록 템플릿: gradient 중심 학습 일지

gradient 문제는 재현 로그가 없으면 다시 반복됩니다. 아래처럼 최소 필드를 고정해 두면 실험 간 비교가 쉬워집니다.

```python
def record(epoch, step, loss, grad_norm, lr, clip_applied):
    return {
        'epoch': epoch,
        'step': step,
        'loss': float(loss),
        'grad_norm': float(grad_norm),
        'lr': float(lr),
        'clip': bool(clip_applied),
    }
```

추천 기록 순서는 다음과 같습니다.

1. 학습 시작 5% 구간에서는 매 step 기록으로 초기 불안정을 잡습니다.
2. 이후에는 구간 평균과 백분위수 통계로 저장량을 줄입니다.
3. 이상 구간 발견 시 원시 step 로그를 다시 활성화합니다.

이 루틴은 "왜 이번 실험이 실패했는가"를 감이 아니라 수치로 설명하게 해 줍니다.

## 고차원 gradient 투영 해석

고차원에서는 전체 벡터를 직접 볼 수 없으므로, 기준 방향으로 투영한 값이 유용합니다. 예를 들어 이전 step gradient `g_{t-1}`과 현재 gradient `g_t`의 내적 부호를 보면 방향 일관성을 확인할 수 있습니다.

```python
import numpy as np

def projection(a, b):
    # b 위로 a를 투영한 스칼라 성분
    return float((a @ b) / (np.linalg.norm(b) + 1e-12))

g_prev = np.random.randn(1024)
g_curr = np.random.randn(1024)
print('proj:', projection(g_curr, g_prev))
```

투영값이 계속 음수면 이전 방향과 반복 충돌 중이라는 뜻입니다. 이 경우 lr 축소나 모멘텀 완화가 효과적인 경우가 많습니다.

## 현업 점검 시나리오: gradient 이상 징후 대응 순서

실제 운영에서는 여러 신호가 동시에 깨지므로 우선순위가 필요합니다. 다음 순서를 표준화하면 대응 시간이 줄어듭니다.

| 우선순위 | 점검 | 통과 기준 |
| --- | --- | --- |
| 1 | NaN/Inf 존재 여부 | 모든 grad가 유한값 |
| 2 | 레이어별 norm 분포 | 특정 레이어 독주 없음 |
| 3 | update/weight 비율 | 극단적 점프 없음 |
| 4 | 손실-정확도 동조성 | 손실 하락 시 성능 동반 개선 |

```python
def update_ratio(update, weight, eps=1e-12):
    import numpy as np
    return float(np.linalg.norm(update) / (np.linalg.norm(weight) + eps))
```

이 비율이 반복적으로 과도하면 학습률이나 정규화 강도를 먼저 조정하는 것이 일반적으로 효과적입니다.

### 현업 메모
gradient 해석은 단일 스텝보다 구간 추세가 중요합니다. 최소 100 step 단위 이동 평균으로 norm과 loss를 함께 보아야 일시적 노이즈와 구조적 불안정을 구분할 수 있습니다.

추가로, gradient 로그를 해석할 때는 단일 지표가 아니라 loss, norm, update ratio를 함께 읽어야 원인 분리가 정확해집니다.

## 정리

Gradient는 여러 편미분을 한데 묶은 벡터이며, 현재 지점에서 손실이 가장 빠르게 증가하는 방향을 가리킵니다. 방향은 어디로 움직일지를, 크기는 그 신호가 얼마나 강한지를 알려 줍니다. 그래서 gradient는 미분 결과이면서 동시에 학습 제어 신호입니다.

경사하강법은 이 gradient를 반대로 따라갑니다. 즉 gradient를 이해하는 것은 “왜 optimizer가 저 방향으로 움직였는가”를 이해하는 일과 같습니다. 실무에서 gradient norm, clipping, exploding gradient 같은 표현이 자연스럽게 쓰이는 이유도 모두 이 벡터 관점에서 설명됩니다.

다음 글에서는 함수가 함수 안에 들어가는 합성 구조에서 gradient가 어떻게 전달되는지 보겠습니다. 그러면 chain rule이 왜 backpropagation의 핵심인지 훨씬 분명해집니다.

## 처음 질문으로 돌아가기

- **여러 편미분을 하나의 gradient vector로 묶는다는 것은 정확히 무엇을 뜻할까요?**
  - 본문에서 본 것처럼 gradient는 축별 편미분을 순서 있게 모은 벡터이며, `run_gd` 예제에서처럼 한 번의 업데이트 방향을 바로 계산하는 실행 단위입니다. 따라서 개별 편미분 목록이 아니라, 현재 파라미터 상태 전체를 이동시키는 좌표계 기준 화살표입니다.
- **gradient의 방향과 크기는 각각 어떤 실무 의미를 가질까요?**
  - 방향은 방향도함수 관점에서 "어느 쪽이 상승/하강인지"를 정하고, 크기는 norm 모니터링에서 "신호가 과한지 약한지"를 판단하는 지표가 됩니다. PyTorch 디버깅 섹션의 `total grad norm` 로그가 바로 이 크기 해석을 운영 지표로 옮긴 사례입니다.
- **왜 gradient는 손실이 가장 빠르게 증가하는 방향을 가리킬까요?**
  - 방향도함수 식 `∇f · u`를 쓰면 단위 방향 `u` 중 최대값이 `u = ∇f/||∇f||`일 때 나온다는 것을 확인할 수 있습니다. 그래서 gradient 방향이 최대 상승 방향이고, 경사하강법이 그 반대 방향으로 이동하면 가장 빠른 국소 하강 경로를 선택하게 됩니다.

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

### 예제 코드
- [book-examples/calculus-for-ml-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/calculus-for-ml-101/ko)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, Gradient, Vector, Beginner

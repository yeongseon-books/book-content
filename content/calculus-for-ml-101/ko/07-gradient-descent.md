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

이 글에서는 경사하강법의 기본 업데이트 식, learning rate의 역할, 수렴과 발산, SGD와 mini-batch 직관을 중심으로 설명하겠습니다. 목표는 “gradient가 있으니 이제 움직인다”를 단순한 문장이 아니라 반복 가능한 학습 절차로 이해하는 것입니다.

끝까지 읽고 나면 optimizer 로그에서 loss curve를 볼 때 왜 learning rate가 가장 먼저 의심되는지 자연스럽게 설명할 수 있게 됩니다.

![Calculus for ML 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/07/07-01-concept-at-a-glance.ko.png)
*Calculus for ML 101 7장 흐름 개요*

## 먼저 던지는 질문

- gradient의 반대 방향으로 이동하면 왜 손실이 줄어들까요?
- learning rate는 단순한 배율 이상으로 어떤 역할을 할까요?
- 경사하강법이 수렴하거나 발산하는 패턴은 어떻게 구분할 수 있을까요?

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

## 순수 경사하강법 구현과 로그 해석

경사하강법을 이해할 때는 먼저 가장 단순한 구현을 직접 돌려 보는 것이 좋습니다. 다음 코드는 2차 함수에 대해 순수 GD를 적용합니다.

```python
import numpy as np

def f(w):
    return (w - 4.0) ** 2 + 1.0

def grad(w):
    return 2.0 * (w - 4.0)

def vanilla_gd(w0, lr, steps):
    w = float(w0)
    hist = []
    for t in range(steps):
        g = grad(w)
        hist.append((t, w, f(w), g))
        w = w - lr * g
    return hist

hist = vanilla_gd(w0=-3.0, lr=0.1, steps=10)
for row in hist[:5]:
    print(row)
```

로그를 읽을 때는 `w`, `loss`, `grad` 세 값을 같이 봐야 합니다. loss만 보면 감소 여부는 보이지만, 왜 느린지 또는 왜 진동하는지는 파악하기 어렵습니다.

| 로그 신호 | 의미 | 조치 |
| --- | --- | --- |
| `|grad|`가 큰데 loss 감소 폭도 큼 | 초기 정상 하강 | lr 유지 |
| `|grad|`가 작고 loss 변화 미미 | 평탄 구간 | lr 스케줄 또는 모멘텀 |
| loss가 교대로 증가/감소 | step 과대 | lr 감소 |

## 배치 방식 비교: batch vs mini-batch vs stochastic

같은 경사하강법이라도 gradient를 어떤 데이터 단위로 계산하느냐에 따라 동작이 달라집니다.

- Batch GD: 전체 데이터로 gradient 계산, 안정적이지만 비쌉니다.
- Mini-batch GD: 소규모 배치 사용, 현대 딥러닝의 기본 선택입니다.
- SGD: 샘플 1개 단위, 노이즈가 크지만 빠른 반응이 가능합니다.

```python
import numpy as np

def grad_linear_mse(x, y, w, b):
    pred = x * w + b
    err = pred - y
    dw = 2.0 * np.mean(err * x)
    db = 2.0 * np.mean(err)
    return dw, db

def sample_batch(x, y, batch_size):
    idx = np.random.choice(len(x), batch_size, replace=False)
    return x[idx], y[idx]
```

| 방식 | 분산(gradient noise) | 계산 비용 | 수렴 특성 |
| --- | --- | --- | --- |
| Batch | 낮음 | 높음 | 매끄럽지만 느릴 수 있음 |
| Mini-batch | 중간 | 중간 | 속도/안정성 균형 |
| SGD | 높음 | 낮음 | 흔들림 크지만 탈출력 있음 |

실무에서는 GPU 효율, 메모리, 일반화 특성을 함께 고려해 mini-batch를 기본으로 두고 batch size를 탐색합니다.

## learning rate 실험 설계

learning rate는 단일 값 고정이 아니라 실험 설계 대상으로 다뤄야 합니다. 같은 모델에서도 데이터 스케일과 초기화에 따라 최적 구간이 달라집니다.

```python
def run_lr_sweep(train_fn, lrs):
    results = []
    for lr in lrs:
        final_loss = train_fn(lr)
        results.append((lr, final_loss))
    return results
```

권장 절차는 다음과 같습니다.

1. 로그 스케일 후보(`1e-4, 3e-4, 1e-3 ...`)를 먼저 넓게 탐색합니다.
2. 가장 좋은 구간 주변을 촘촘히 재탐색합니다.
3. 고정 lr이 불안정하면 decay, cosine, warmup을 적용합니다.

| 관찰 패턴 | lr 해석 | 대응 |
| --- | --- | --- |
| 초반부터 loss 발산 | lr 과대 | 3~10배 낮춰 재실험 |
| 단조 감소하나 매우 느림 | lr 과소 | 2~3배 증가 |
| 중반 이후 정체 | 고정 lr 한계 | schedule 도입 |
| 특정 epoch에서 급격한 불안정 | 데이터/정규화와 상호작용 | lr + batch + clipping 동시 점검 |

## 수렴 조건을 직관적으로 이해하기

엄밀한 이론에서는 Lipschitz 연속 gradient 가정 아래 step 크기 상한이 제시됩니다. 실무에서는 이를 "너무 큰 스텝은 최소점을 건너뛴다"는 규칙으로 해석하면 충분합니다.

1차원 2차 함수 `f(w)=a(w-w*)^2`에서

`w_{t+1} = w_t - lr * 2a(w_t - w*)`

오차 `e_t = w_t - w*`는

`e_{t+1} = (1 - 2a*lr)e_t`

이 됩니다. 따라서 `|1-2a*lr| < 1`이면 수렴합니다.

```python
import numpy as np

def simulate(a, lr, e0=5.0, steps=10):
    e = e0
    out = []
    for t in range(steps):
        out.append((t, e))
        e = (1 - 2*a*lr) * e
    return out

print(simulate(a=1.0, lr=0.4)[:5])
```

이 식은 실무 감각과도 맞습니다. 곡률 `a`가 큰 방향에서는 같은 lr이 더 위험합니다.

## 모멘텀 직관과 기본 구현

모멘텀은 현재 gradient만 보지 않고, 과거 업데이트 방향을 누적해 관성처럼 반영합니다. 좁은 협곡에서 지그재그를 줄이고, 일관된 방향에서는 속도를 높입니다.

```python
def momentum_step(w, g, v, lr=0.01, beta=0.9):
    v = beta * v + (1 - beta) * g
    w = w - lr * v
    return w, v
```

| 상황 | 순수 GD | 모멘텀 |
| --- | --- | --- |
| 축별 곡률 차이가 큰 협곡 | 왕복 진동 잦음 | 진동 완화 |
| 장거리 완만한 경사 | 느린 전진 | 누적으로 속도 향상 |
| 노이즈 큰 SGD | 변동성 큼 | 평균화 효과 |

다만 모멘텀도 learning rate와 함께 조정해야 하며, 과도한 `beta`는 반응 지연을 만들 수 있습니다.

## 비볼록 표면에서의 경사하강법

딥러닝 손실은 대체로 비볼록입니다. 따라서 전역 최솟값 보장은 어렵고, 안장점(saddle), 평탄 구간, 다중 지역해를 상대해야 합니다.

```python
import numpy as np

# 안장점 형태의 toy function

def saddle(w):
    x, y = w
    return x**2 - y**2 + 0.1*(x**4 + y**4)

def saddle_grad(w):
    x, y = w
    return np.array([2*x + 0.4*x**3, -2*y + 0.4*y**3])
```

비볼록 표면에서 자주 관찰되는 현상은 다음과 같습니다.

| 현상 | 설명 | 대응 |
| --- | --- | --- |
| 안장점 주변 정체 | 한 축은 내려가고 다른 축은 올라감 | 노이즈 활용, 모멘텀, 재시작 |
| 지역해 간 성능 편차 | 초기값/셔플 영향 | 다중 시드 실험 |
| 평탄 구간에서 느린 진전 | gradient 작음 | lr schedule, adaptive optimizer |

즉 경사하강법의 목표는 항상 "완벽한 전역해"보다 "재현 가능한 좋은 해"를 찾는 쪽에 가깝습니다.

## 운영 체크포인트: 학습 루프 안정화

실전 학습 루프에서는 알고리즘보다 계측이 먼저입니다. 다음 항목을 표준 로그로 고정하면 실패 원인 분리가 빨라집니다.

1. step/epoch 기준으로 train loss, val loss를 분리 기록합니다.
2. 파라미터 전체 grad norm과 update norm을 함께 기록합니다.
3. lr 스케줄 값을 로그에 남겨 곡선 변화 시점과 연결합니다.
4. 배치 크기와 데이터 셔플 시드를 실험 메타데이터로 저장합니다.

```python
def log_step(step, loss, grad_norm, lr):
    print({'step': step, 'loss': float(loss), 'grad_norm': float(grad_norm), 'lr': float(lr)})
```

이 로그가 있으면 "모델이 나쁘다"는 모호한 결론 대신, "lr 과대", "gradient 폭주", "배치 노이즈 과다"처럼 조치 가능한 진단으로 전환할 수 있습니다.

## 미니배치 학습 루프 전체 예제

경사하강법을 실제 훈련 루프로 연결할 때는 데이터 셔플, 배치 반복, 검증 로그까지 한 덩어리로 보는 편이 좋습니다.

```python
import numpy as np

def train_epoch(x, y, w, b, lr=0.01, batch_size=16):
    n = len(x)
    order = np.random.permutation(n)
    x, y = x[order], y[order]

    losses = []
    for i in range(0, n, batch_size):
        xb = x[i:i+batch_size]
        yb = y[i:i+batch_size]
        pred = xb * w + b
        err = pred - yb
        loss = np.mean(err**2)
        dw = 2*np.mean(err*xb)
        db = 2*np.mean(err)
        w -= lr * dw
        b -= lr * db
        losses.append(loss)
    return w, b, float(np.mean(losses))
```

이 구조를 기준으로 optimizer만 바꿔도 실험 공정이 유지됩니다.

## learning rate schedule 실전 비교

고정 learning rate가 항상 최선은 아닙니다. 초반 탐색은 크게, 후반 미세 조정은 작게 가져가는 스케줄이 수렴 품질을 높이는 경우가 많습니다.

대표 스케줄 3가지를 비교하면 다음과 같습니다.

| 스케줄 | 식(개념) | 장점 | 단점 |
| --- | --- | --- | --- |
| Step decay | 일정 epoch마다 lr 감소 | 단순, 해석 쉬움 | 경계에서 급변 |
| Cosine decay | 코사인 형태로 점진 감소 | 부드러운 전환 | 하이퍼파라미터 추가 |
| Warmup + decay | 초반 작은 lr 후 증가/감소 | 대규모 모델 안정화 | 설정 복잡 |

```python
def cosine_lr(base_lr, step, total_steps):
    import math
    return base_lr * 0.5 * (1 + math.cos(math.pi * step / total_steps))
```

## 수렴 판정 기준을 명시하기

"대충 내려가는 것 같다"는 판정은 재현되지 않습니다. 종료 조건을 수치 기준으로 명시해야 합니다.

1. 최근 `k` step 평균 loss 개선량이 임계치 이하인지 확인합니다.
2. grad norm이 충분히 작고 변동성도 낮은지 확인합니다.
3. 검증 성능이 장기간 개선되지 않으면 조기 종료합니다.

| 판정 지표 | 예시 임계치 | 해석 |
| --- | --- | --- |
| `Δloss_ma` | `< 1e-5` | 수렴 또는 정체 |
| `grad_norm` | `< 1e-4` | 국소 최소 근접 가능 |
| `val metric patience` | `10 epoch` | 일반화 개선 정체 |

## 비볼록 구간에서 재시작 전략

비볼록 손실에서 한 번의 학습 경로만 믿으면 우연한 지역해에 갇힐 수 있습니다. 재시작 전략은 간단하지만 효과적입니다.

- 서로 다른 시드로 3~5회 독립 학습을 실행합니다.
- 각 실행의 최종 검증 지표와 안정성 로그를 비교합니다.
- 최고 점수 하나가 아니라 분산까지 함께 보고 모델을 선택합니다.

```python
def multi_seed(train_fn, seeds):
    out = []
    for s in seeds:
        np.random.seed(s)
        out.append((s, train_fn()))
    return out
```

이 방식은 "재현 가능한 성능"을 확보하는 데 중요합니다.

## 모멘텀과 순수 GD의 업데이트 크기 비교

같은 lr에서도 모멘텀은 유효 업데이트 크기를 바꿉니다. 따라서 손실 곡선을 비교할 때 `lr` 숫자만 같다고 공정한 비교가 되지 않습니다.

| 비교 항목 | 순수 GD | 모멘텀 GD |
| --- | --- | --- |
| 현재 gradient 의존도 | 100% | 부분 의존 + 과거 누적 |
| 진동 억제 | 약함 | 강함 |
| 초기 반응 속도 | 즉각적 | 다소 지연 가능 |
| 하이퍼파라미터 | lr | lr + beta |

운영에서는 `update_norm`도 함께 기록해 실제 이동량을 비교해야 합니다.

## 실험 재현성: 경사하강법 비교의 전제

학습률과 optimizer를 비교할 때 재현성이 없으면 결론이 흔들립니다. 최소한 다음 항목은 실험 메타데이터로 남겨야 합니다.

| 항목 | 기록 예시 |
| --- | --- |
| 난수 시드 | `seed=42` |
| 데이터 셔플 정책 | epoch마다 셔플 여부 |
| 배치 크기 | `batch_size=64` |
| 초기화 방식 | Xavier/He/normal |
| lr 스케줄 | cosine, step 등 |

```python
import numpy as np

def set_seed(seed):
    np.random.seed(seed)
```

작아 보이는 정보지만, 동일 곡선을 재현할 수 있는지 여부가 디버깅 효율을 크게 좌우합니다.

## 학습률-배치크기 동시 조정 원칙

배치 크기를 바꾸면 gradient 분산이 달라지므로 learning rate도 함께 조정해야 합니다. 일반적으로 배치를 키우면 lr을 일부 키워도 안정적이지만, 무조건 선형 비례는 아닙니다.

| 변경 | 기대 효과 | 주의점 |
| --- | --- | --- |
| batch 증가 | gradient 분산 감소 | 일반화 저하 가능 |
| lr 증가 | 수렴 속도 향상 가능 | 발산 위험 증가 |
| 둘 동시 조정 | 처리량 개선 | 튜닝 비용 증가 |

실무에서는 작은 탐색 격자를 먼저 돌린 뒤, 가장 안정적인 영역에서 세밀 조정하는 방식이 효과적입니다.

### 운영 메모
경사하강법 실험 결과를 비교할 때는 최종 점수 하나보다 학습 곡선의 안정성, 재시도 분산, 수렴 시간까지 함께 기록해야 합니다. 이 세 항목이 있어야 실제 배포 환경에서 예측 가능한 성능을 확보할 수 있습니다.

또한 학습률 조정은 단발성 변경이 아니라, 동일 조건 반복 실험을 통한 통계적 판단으로 수행해야 재현 가능한 결론을 얻을 수 있습니다.

## 정리

경사하강법은 gradient의 반대 방향으로 작은 스텝을 반복해 손실을 줄이는 가장 기본적인 학습 알고리즘입니다. 방향은 gradient가 정하고, 스텝 크기는 learning rate가 정합니다. 이 단순한 구조가 거의 모든 현대 optimizer의 출발점입니다.

실무적으로 가장 중요한 감각은 learning rate 해석입니다. 발산, 느린 수렴, noisy curve 같은 현상은 대부분 경사하강법의 기본 요소로 설명할 수 있습니다. 따라서 optimizer를 바꾸기 전에 먼저 기본 GD 관점에서 현상을 읽어 보는 습관이 중요합니다.

다음 글에서는 plain GD의 약점을 보완하는 momentum, RMSProp, Adam 같은 최적화 기법을 보겠습니다. 그러면 왜 현대 학습 루프가 그 변형들을 쓰는지 연결해서 이해할 수 있습니다.

## 처음 질문으로 돌아가기

- **gradient의 반대 방향으로 이동하면 왜 손실이 줄어들까요?**
  - gradient는 국소적으로 가장 빠른 상승 방향이므로, 그 반대 방향은 가장 빠른 하강 방향입니다. 순수 GD 구현과 2차 함수 시뮬레이션에서 실제로 매 스텝 손실이 감소하는 경로를 확인했습니다.
- **learning rate는 단순한 배율 이상으로 어떤 역할을 할까요?**
  - learning rate는 동일한 gradient를 실제 이동 거리로 변환하는 핵심 제어값입니다. lr 스윕 실험에서 보듯 수렴 속도, 진동 여부, 발산 위험을 동시에 결정하므로, optimizer 성능의 상당 부분을 좌우합니다.
- **경사하강법이 수렴하거나 발산하는 패턴은 어떻게 구분할 수 있을까요?**
  - 수렴은 loss 감소와 grad norm 안정화가 동반되고, 발산은 loss 급증·진동·비정상 norm 증가로 나타납니다. batch 방식, 모멘텀, 비볼록 표면 특성을 함께 해석하면 어떤 설정을 조정해야 하는지 구체적으로 판단할 수 있습니다.

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

### 예제 코드
- [book-examples/calculus-for-ml-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/calculus-for-ml-101/ko)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, GradientDescent, Optimization, Beginner

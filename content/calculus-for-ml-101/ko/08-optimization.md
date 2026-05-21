---
series: calculus-for-ml-101
episode: 8
title: "Calculus for ML 101 (8/10): 최적화"
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
  - Optimization
  - Adam
  - Beginner
seo_description: momentum, RMSProp, Adam, schedule, regularization을 ML 입문자 관점에서 정리한 글
last_reviewed: '2026-05-12'
---

# Calculus for ML 101 (8/10): 최적화

경사하강법은 학습의 기본 뼈대이지만, 실제 딥러닝 학습은 그보다 훨씬 거칠고 복잡한 손실 지형 위에서 일어납니다. 골짜기가 길게 늘어진 영역도 있고, gradient scale이 좌표마다 크게 다를 수도 있으며, 초반에는 불안정하고 후반에는 더 섬세한 업데이트가 필요한 경우도 많습니다. 그래서 plain gradient descent만으로는 속도와 안정성 모두에서 한계가 드러납니다.

현대 optimizer들은 이 한계를 보완하기 위해 만들어졌습니다. momentum은 관성을 더하고, RMSProp은 좌표별 scale 차이를 흡수하고, Adam은 둘을 결합합니다. 여기에 learning-rate schedule과 regularization이 더해져 실제 훈련 루프가 구성됩니다.

이 글은 Calculus for ML 101 시리즈의 여덟 번째 글입니다.

이 글에서는 momentum, RMSProp, Adam, schedule, L2 regularization을 하나의 optimization toolkit으로 묶어 설명하겠습니다. 핵심은 이름을 외우는 것이 아니라 plain GD의 어떤 약점을 각각 보완하는지 이해하는 것입니다.

끝까지 읽고 나면 optimizer 선택을 “유명하니까 Adam” 수준이 아니라, 현재 손실 지형과 학습 단계에 맞는 설계 판단으로 볼 수 있게 됩니다.


![Calculus for ML 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/08/08-01-concept-at-a-glance.ko.png)
*Calculus for ML 101 8장 흐름 개요*

## 먼저 던지는 질문

- plain gradient descent는 실제 딥러닝 학습에서 어떤 약점을 드러낼까요?
- momentum은 왜 관성이라는 비유로 설명하는 편이 가장 이해가 쉬울까요?
- RMSProp과 Adam은 좌표별 gradient scale 차이를 어떻게 완화할까요?

## 왜 이 글이 중요한가

실무에서 optimizer는 training recipe의 중심입니다. 같은 모델과 데이터라도 optimizer, learning-rate schedule, weight decay 설정이 바뀌면 수렴 속도와 최종 성능이 크게 달라집니다. 그래서 optimization은 “미분 이후의 디테일”이 아니라, 학습을 실제로 성공시키는 운영 계층입니다.

특히 대규모 모델에서는 초반 warmup이 없으면 발산하고, adaptive method가 없으면 좌표별 scale 차이를 다루기 어려우며, schedule이 없으면 후반 미세 조정이 둔해질 수 있습니다. 즉 optimizer는 하나의 함수 호출이 아니라, gradient를 어떻게 해석하고 누적하고 감쇠할지를 정하는 정책 묶음입니다.

또한 regularization을 optimization과 함께 봐야 하는 이유도 중요합니다. 손실만 줄이는 것이 목표라면 과적합된 해답으로 너무 쉽게 흘러갈 수 있기 때문입니다. 좋은 optimizer는 빠르기만 한 것이 아니라, 일반화 가능한 해로 가도록 학습을 제어해야 합니다.

## 핵심 관점

최적화를 가장 실용적으로 이해하는 방법은 plain GD가 어디서 힘들어하는지 먼저 보는 것입니다. 지그재그로 흔들리고, gradient scale 차이에 취약하고, 초반에는 불안정하고, 후반에는 너무 거칠 수 있습니다. momentum, RMSProp, Adam, schedule은 각각 이 약점에 대응합니다.

이렇게 보면 optimizer는 별개의 마법 상자가 아니라 설계 의도가 분명한 수정 패치들입니다. 실제 현업에서 optimizer 튜닝이 가능한 이유도 각 구성 요소가 어떤 문제를 겨냥하는지 비교적 명확하기 때문입니다.

> 현대 optimizer는 경사하강법을 대체하는 것이 아니라, 손실 지형의 거칠기와 gradient scale의 불균형, 학습 단계별 요구를 견디도록 보강한 버전입니다.

## 핵심 개념

최적화 흐름은 다음과 같습니다.

### momentum은 방향의 일관성을 키웁니다

```python
def momentum_step(w, v, g, lr=0.1, beta=0.9):
    v = beta * v + g
    return w - lr * v, v
```

momentum은 과거 gradient의 running mean을 함께 사용해 업데이트를 부드럽게 만듭니다. 지형이 길고 좁은 골짜기일 때 좌우로 흔들리는 대신, 주된 진행 방향으로 더 잘 나아가게 해 줍니다. 관성이라는 비유가 자주 쓰이는 이유가 여기에 있습니다.

### RMSProp은 좌표별 scale 차이를 완화합니다

```python
def rms_step(w, s, g, lr=0.01, beta=0.99, eps=1e-8):
    s = beta * s + (1 - beta) * g * g
    return w - lr * g / (s ** 0.5 + eps), s
```

RMSProp은 squared gradient의 running mean으로 각 좌표의 step size를 적응적으로 조절합니다. 특정 좌표의 gradient가 지속적으로 큰 경우에는 업데이트를 자동으로 줄여 주므로, 서로 다른 스케일의 파라미터를 같은 learning rate로 다루기 쉬워집니다.

### Adam은 momentum과 RMSProp을 결합합니다

```python
def adam_step(w, m, v, g, t, lr=0.001, b1=0.9, b2=0.999, eps=1e-8):
    m = b1 * m + (1 - b1) * g
    v = b2 * v + (1 - b2) * g * g
    mh = m / (1 - b1 ** t)
    vh = v / (1 - b2 ** t)
    return w - lr * mh / (vh ** 0.5 + eps), m, v
```

Adam은 방향 일관성과 scale 적응성을 동시에 취합니다. 그래서 기본값만으로도 꽤 강력한 출발점을 제공하지만, 그렇다고 항상 튜닝이 불필요한 것은 아닙니다. 학습률, betas, weight decay, warmup 정책까지 포함해 recipe 전체로 봐야 합니다.

### schedule은 학습 단계에 따라 스텝 크기를 바꿉니다

```python
def cosine_lr(step, total, lr0=0.01):
    import math
    return 0.5 * lr0 * (1 + math.cos(math.pi * step / total))
```

초반에는 크게 탐색하고, 후반에는 더 작은 스텝으로 세밀하게 조정하는 것이 일반적입니다. cosine schedule은 이런 흐름을 부드럽게 구현합니다. 대규모 학습에서 warmup을 함께 쓰는 이유는 초반 불안정한 gradient에 바로 큰 learning rate를 적용하지 않기 위해서입니다.

### regularization은 generalization을 위한 제동 장치입니다

```python
def l2_step(w, g, lr=0.1, wd=1e-4):
    return w - lr * (g + wd * w)
```

L2 regularization은 파라미터가 과도하게 커지는 것을 억제해 일반화에 도움을 줍니다. 다만 현대 프레임워크에서는 L2 penalty와 decoupled weight decay를 구분해 이해하는 것이 중요합니다. 이름은 비슷해 보여도 optimizer와 결합되는 방식이 다를 수 있기 때문입니다.

### 최적화는 optimizer 하나가 아니라 recipe입니다

실무에서는 “Adam을 쓴다”만으로 끝나지 않습니다. 초기 learning rate, warmup 길이, schedule 모양, weight decay, gradient clipping, batch size가 모두 함께 작동합니다. 따라서 optimization 문제를 볼 때는 단일 knob보다 recipe 전체를 점검하는 편이 정확합니다.

## 흔히 헷갈리는 지점

- Adam 기본값이 강력하다고 해서 언제나 최적이라는 뜻은 아닙니다.
- L2 regularization과 decoupled weight decay를 같은 것으로 취급하면 해석이 틀어질 수 있습니다.
- schedule 없이 고정 learning rate만 유지하면 후반 미세 조정이 거칠 수 있습니다.
- 초반 발산을 optimizer 종류 문제로만 보면 warmup 부재를 놓칠 수 있습니다.
- 체크포인트 재시작 시 momentum state를 어떻게 다룰지 무시하면 학습 궤적이 달라질 수 있습니다.

## 운영 체크리스트

- [ ] optimizer 선택 이유를 손실 지형과 gradient scale 관점에서 설명할 수 있다
- [ ] warmup, main schedule, final decay를 포함한 learning-rate 정책을 정의한다
- [ ] weight decay 또는 regularization 설정을 명시적으로 분리해 관리한다
- [ ] 재시작 시 optimizer state 복원 정책을 실험 설정에 포함한다
- [ ] 성능 문제를 볼 때 모델 구조와 함께 optimization recipe 전체를 점검한다

## 정리

최적화는 plain gradient descent를 더 빠르고 안정적으로 만들기 위한 보강 기법들의 조합입니다. momentum은 방향 일관성을, RMSProp은 좌표별 적응성을, Adam은 둘의 결합을 제공합니다. 여기에 schedule과 regularization이 더해져 실제 훈련 루프가 완성됩니다.

실무에서는 optimizer 이름보다 recipe 전체가 더 중요할 때가 많습니다. learning rate, warmup, weight decay, gradient clipping이 함께 설계되어야 같은 모델도 제대로 학습됩니다. 그래서 optimization은 “어떤 알고리즘을 썼는가”보다 “gradient를 어떻게 다뤘는가”의 문제에 가깝습니다.

다음 글에서는 이 optimization에 들어가는 gradient가 네트워크 전체에서 어떻게 계산되는지, 즉 backpropagation을 계산 그래프 관점에서 다시 보겠습니다.


## Adam을 식으로 다시 전개하기

Adam은 1차 모멘트(gradient 평균)와 2차 모멘트(gradient 제곱 평균)를 동시에 추적합니다. 핵심 식은 다음과 같습니다.

\[
m_t = eta_1 m_{t-1} + (1-eta_1) g_t, \quad
v_t = eta_2 v_{t-1} + (1-eta_2) g_t^2
\]

초기 단계에서는 `m_0=0`, `v_0=0`으로 시작하므로 편향이 큽니다. 이를 보정하기 위해 bias correction을 사용합니다.

\[
\hat{m}_t = rac{m_t}{1-eta_1^t}, \quad
\hat{v}_t = rac{v_t}{1-eta_2^t}
\]

최종 업데이트는 아래와 같습니다.

\[
	heta_{t+1} = 	heta_t - lpha rac{\hat{m}_t}{\sqrt{\hat{v}_t}+\epsilon}
\]

이 식을 좌표별로 해석하면, `hat(v)`가 큰 좌표는 step이 자동으로 줄고, `hat(m)`는 최근 gradient 방향을 안정적으로 모읍니다. 즉 Adam은 진동 완화와 좌표별 스케일 보정을 동시에 수행합니다.

### Adam 수치 예제

초기값 `w=1.0`, `g1=0.3`, `g2=0.1`, `alpha=0.001`, `beta1=0.9`, `beta2=0.999`라고 하겠습니다.

| 단계 | 값 |
| --- | --- |
| t=1, m1 | `0.03` |
| t=1, v1 | `0.00009` |
| t=1, m^1 | `0.3` |
| t=1, v^1 | `0.09` |
| 업데이트 | `0.001 * 0.3 / (sqrt(0.09)+eps) ≈ 0.001` |

첫 step에서 bias correction이 없으면 `m`과 `v`가 과소평가되어 업데이트 크기가 왜곡됩니다. 그래서 Adam 구현에서는 correction이 사실상 필수입니다.

### Adam 구현에서 자주 놓치는 세부점

- `eps`는 분모 0 방지뿐 아니라, 매우 작은 분산 구간의 step 폭을 제한하는 안전장치입니다.
- `beta2`를 너무 작게 잡으면 분산 추정이 흔들려 학습 곡선이 불안정해질 수 있습니다.
- mixed precision에서는 gradient scale과 Adam 분모 안정성(`eps`)을 함께 점검해야 합니다.

## 학습률 스케줄 설계

optimizer가 방향을 정한다면 scheduler는 시간축 정책을 정합니다. 같은 Adam이라도 스케줄이 다르면 완전히 다른 학습 궤적이 나옵니다.

### 계단식 감소(Step decay)

일정 epoch마다 학습률을 계단식으로 내리는 방식입니다.

\[
lpha_t = lpha_0 \cdot \gamma^{\lfloor t/s 
floor}
\]

- 장점: 단순하고 해석이 쉽습니다.
- 단점: 경계 시점에서 손실 곡선이 급하게 꺾일 수 있습니다.

```python
import math

def step_lr(step, base_lr=1e-3, drop_every=1000, gamma=0.5):
    return base_lr * (gamma ** (step // drop_every))
```

### 코사인 감소(Cosine decay)

초기 학습률에서 0 또는 최소값으로 부드럽게 감쇠합니다.

\[
lpha_t = lpha_{min} + rac{1}{2}(lpha_{max}-lpha_{min})(1 + \cos(\pi t/T))
\]

```python
import math

def cosine_lr(step, total_steps, lr_max=1e-3, lr_min=1e-5):
    ratio = step / total_steps
    return lr_min + 0.5 * (lr_max - lr_min) * (1 + math.cos(math.pi * ratio))
```

- 장점: 후반 미세 조정이 부드럽고 발산 위험이 낮습니다.
- 단점: 총 step 수를 대략 정확히 알아야 합니다.

### 워밍업 + 메인 스케줄

대규모 배치나 Transformer 계열에서는 초반 gradient가 불안정해 곧바로 큰 학습률을 주면 손실이 튈 수 있습니다. warmup은 초반 `N` step 동안 학습률을 선형 상승시키고, 이후 본 스케줄(보통 cosine)로 넘어갑니다.

```python
def warmup_cosine(step, warmup_steps, total_steps, lr_max=3e-4, lr_min=3e-5):
    if step < warmup_steps:
        return lr_max * (step + 1) / warmup_steps
    progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
    import math
    return lr_min + 0.5 * (lr_max - lr_min) * (1 + math.cos(math.pi * progress))
```

### 스케줄 선택 기준

| 상황 | 추천 스케줄 | 이유 |
| --- | --- | --- |
| 작은 모델, 빠른 실험 | Step decay | 튜닝 단순성 |
| 긴 학습, 후반 정밀 조정 | Cosine | 부드러운 감쇠 |
| 대규모 배치, 초반 발산 잦음 | Warmup + Cosine | 초기 안정성 + 후반 성능 |

## Weight Decay와 L2 정규화의 차이

표면적으로 둘 다 `w`를 줄이는 항이 들어가서 같아 보이지만, adaptive optimizer에서는 동치가 깨집니다.

### L2 penalty 방식

손실에 `\lambda/2 ||w||^2`를 더하면 gradient가 `g + \lambda w`로 바뀝니다. 즉 정규화 항이 gradient 경로에 결합됩니다.

### Decoupled weight decay 방식

AdamW는 gradient 경로와 별도로 파라미터를 직접 감쇠합니다.

\[
	heta_{t+1} = 	heta_t - lpha \cdot 	ext{AdamUpdate}(g_t) - lpha \lambda 	heta_t
\]

이 방식은 adaptive 분모와 정규화가 섞이지 않아 하이퍼파라미터 해석이 더 일관적입니다.

### 비교 표

| 항목 | L2 penalty (Adam) | Decoupled WD (AdamW) |
| --- | --- | --- |
| 적용 위치 | gradient 내부 | 파라미터 업데이트 외부 |
| adaptive 분모 영향 | 받음 | 받지 않음 |
| 튜닝 해석 | 복합적 | 비교적 명확 |
| 실무 권장 | 제한적 | 일반적으로 권장 |

## Optimizer 비교 표

| Optimizer | 핵심 아이디어 | 장점 | 단점 | 기본 시작점 |
| --- | --- | --- | --- | --- |
| SGD | 현재 gradient만 사용 | 단순, 메모리 작음 | 지형이 거칠면 느림 | lr=0.1 전후 |
| SGD+Momentum | 방향 누적 | 진동 완화, 일반화 양호 | lr 민감 | lr=0.1, m=0.9 |
| RMSProp | 좌표별 분산 보정 | 비등방 지형 대응 | 장기 기억 약함 | lr=1e-3 |
| Adam | 모멘트+분산 결합 | 초반 수렴 빠름 | 일반화가 항상 최선은 아님 | lr=1e-3 |
| AdamW | Adam + decoupled WD | 대규모 모델에서 안정적 | wd 튜닝 필요 | lr=3e-4, wd=0.01 |

## 하이퍼파라미터 튜닝 전략

튜닝은 무작정 조합 탐색이 아니라, 실패 징후를 근거로 순서를 정하는 작업입니다.

### 1) 학습률 범위 탐색

아주 작은 값에서 시작해 step마다 증가시키며 손실이 악화되는 구간을 찾습니다. 그 직전 값을 초기 학습률 후보로 사용합니다.

```python
def lr_range_test(model, optimizer, data_loader, lr_start=1e-6, lr_end=1, steps=200):
    mult = (lr_end / lr_start) ** (1 / steps)
    lr = lr_start
    for i, batch in enumerate(data_loader):
        if i >= steps:
            break
        for pg in optimizer.param_groups:
            pg['lr'] = lr
        loss = model.training_step(batch)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        print(i, lr, float(loss))
        lr *= mult
```

### 2) wd를 lr과 분리해서 튜닝

`lr`을 먼저 고정한 뒤 `wd`를 `0, 1e-4, 1e-3, 1e-2`로 비교하면 과적합 억제 효과를 더 명확히 볼 수 있습니다.

### 3) batch size와 함께 재조정

batch size를 키우면 gradient 분산이 줄어 학습률을 키울 여지가 생깁니다. 반대로 작은 batch에서는 lr를 낮추거나 warmup을 길게 잡는 편이 안정적입니다.

### 4) 로그 기반 진단

아래 지표를 같은 x축(step)으로 기록하면 원인 분리가 빨라집니다.

| 로그 지표 | 해석 |
| --- | --- |
| train loss | 최적화 진행 속도 |
| val loss | 일반화 경향 |
| grad norm | 폭주/소실 신호 |
| lr | 스케줄 영향 |
| parameter norm | wd/L2 효과 |

## 실무용 선택 가이드

### 작은 데이터, 빠른 반복 실험

- 우선 `Adam(lr=1e-3)`로 시작합니다.
- 초기 5~10 epoch에서 발산하면 `lr=3e-4`로 낮춥니다.
- 과적합이 보이면 `AdamW(wd=1e-3~1e-2)`로 전환합니다.

### 이미지/언어 대규모 사전학습 또는 파인튜닝

- 기본값은 `AdamW + warmup + cosine` 조합이 안정적입니다.
- warmup 비율은 전체 step의 1~5%에서 시작합니다.
- gradient clipping을 함께 적용해 초반 급격한 업데이트를 제한합니다.

### 일반화 성능이 특히 중요한 경우

- `SGD+Momentum`을 강한 baseline으로 유지합니다.
- 수렴 속도는 느려도 최종 val metric이 높게 나오는지 확인합니다.
- 동일한 epoch가 아니라 동일한 wall-clock 혹은 동일 step 기준으로 비교해야 공정합니다.

## 검증 가능한 미니 실험 설계

아래와 같이 같은 모델에서 optimizer만 바꾸어 기록하면 선택 근거를 팀에 설명하기 쉬워집니다.

| 실험 | 설정 | 관찰 포인트 |
| --- | --- | --- |
| A | Adam, lr=1e-3 | 초반 손실 하강 속도 |
| B | AdamW, lr=3e-4, wd=0.01 | val 안정성 |
| C | SGD+Momentum, lr=0.1 | 최종 일반화 |

실험 로그는 반드시 `seed`, `batch size`, `augmentation`, `scheduler`를 함께 저장해야 합니다. optimizer만 바꿨다고 생각했지만 실제로는 다른 조건이 섞여 있으면 결론이 왜곡됩니다.


## AdamW 구현 세부: 파라미터 그룹과 예외 규칙

실무 학습 코드에서는 모든 파라미터에 동일한 weight decay를 주지 않습니다. 일반적으로 bias와 normalization 계층 파라미터는 decay에서 제외합니다.

```python
import torch

def build_param_groups(model, wd=0.01):
    decay, no_decay = [], []
    for n, p in model.named_parameters():
        if not p.requires_grad:
            continue
        if n.endswith('bias') or 'norm' in n.lower():
            no_decay.append(p)
        else:
            decay.append(p)
    return [
        {'params': decay, 'weight_decay': wd},
        {'params': no_decay, 'weight_decay': 0.0},
    ]

optimizer = torch.optim.AdamW(build_param_groups(model), lr=3e-4, betas=(0.9, 0.999), eps=1e-8)
```

이 패턴을 적용하면 정규화 계층의 scale/shift 파라미터가 과도하게 수축되는 문제를 줄일 수 있습니다.

## 학습률 스케줄 실수 패턴

| 실수 | 결과 | 수정 방법 |
| --- | --- | --- |
| warmup 없이 큰 lr 시작 | 초반 loss 급등, NaN | warmup 1~5% 추가 |
| scheduler.step 위치 혼동 | lr 곡선 왜곡 | epoch/step 기준을 코드에 명시 |
| total_steps 오계산 | cosine 감쇠 타이밍 오류 | dataloader 길이 기반 재계산 |
| resume 시 scheduler state 미복원 | 재시작 직후 성능 흔들림 | checkpoint에 scheduler state 포함 |

```python
# step 단위 스케줄러 예시
for step, batch in enumerate(loader):
    loss = training_step(batch)
    loss.backward()
    optimizer.step()
    scheduler.step()  # step 기반이면 optimizer 다음
    optimizer.zero_grad()
```

## 최적화 실험 기록 템플릿

아래 템플릿으로 실험을 남기면 "왜 이 optimizer를 선택했는가"를 재현 가능하게 설명할 수 있습니다.

| 필드 | 예시 |
| --- | --- |
| 모델/데이터셋 | `resnet50 / cifar100` |
| optimizer | `AdamW` |
| lr policy | `warmup 5ep + cosine` |
| wd/betas/eps | `0.01 / (0.9,0.999) / 1e-8` |
| grad clipping | `1.0` |
| best val metric | `top1=82.4` |
| 실패 징후 | `epoch3에서 grad spike` |
| 조치 | `lr 3e-4 -> 2e-4` |

최적화는 결과만 기록하면 재사용하기 어렵습니다. "징후-가설-조치"까지 함께 저장해야 다음 프로젝트에서 의사결정 속도가 빨라집니다.


## Optimizer 선택 의사결정 트리

아래 트리는 팀 내에서 optimizer 기본값을 빠르게 정할 때 쓸 수 있는 실무형 규칙입니다.

1. **초반 수렴이 너무 느린가?**
   - 예: loss가 1~2 epoch 동안 거의 줄지 않음
   - 조치: AdamW로 시작하고 lr range test를 먼저 실행합니다.
2. **검증 성능이 후반에 흔들리는가?**
   - 조치: cosine 후반 최소 lr를 낮추고, wd를 소폭 증가시킵니다.
3. **학습이 안정적이지만 최종 일반화가 낮은가?**
   - 조치: SGD+Momentum baseline을 병렬 비교합니다.
4. **메모리 제약으로 batch가 작아 noisy한가?**
   - 조치: gradient accumulation + warmup을 결합합니다.

| 관찰된 징후 | 우선 가설 | 1차 조정 |
| --- | --- | --- |
| loss 진동 큼 | lr 과대, 모멘트 과대 | lr 0.5배, beta1 0.9 유지 |
| val gap 확대 | 정규화 부족 | wd 증가, augmentation 점검 |
| 후반 정체 | lr 하강 부족 | cosine min lr 하향 |
| 초반 NaN | scale 불안정 | warmup 추가, clipping 적용 |

결정 트리는 완벽한 정답표가 아니라, 실패를 빠르게 좁히는 공통 언어입니다. 같은 징후를 같은 순서로 점검하면 실험 반복 비용을 크게 줄일 수 있습니다.

## 처음 질문으로 돌아가기

- **plain gradient descent는 실제 딥러닝 학습에서 어떤 약점을 드러낼까요?**
  - 본문에서 확인했듯이 plain GD는 좌표별 gradient 스케일 차이를 직접 보정하지 못하고, 좁은 골짜기에서 진동이 커지며, 학습 단계별로 필요한 step 크기 변화를 반영하기 어렵습니다. 그래서 실무에서는 momentum, adaptive scaling, scheduler를 결합한 recipe가 필요합니다.
- **momentum은 왜 관성이라는 비유로 설명하는 편이 가장 이해가 쉬울까요?**
  - momentum은 과거 gradient를 지수평균으로 누적해 현재 업데이트 방향에 반영합니다. 즉 한 번의 noisy gradient보다 "최근 진행 방향"을 더 신뢰해 지그재그를 줄이고 주된 하강 방향을 유지하므로, 물리적 관성 비유가 동작 원리를 가장 정확하게 전달합니다.
- **RMSProp과 Adam은 좌표별 gradient scale 차이를 어떻게 완화할까요?**
  - RMSProp은 좌표별 `g^2` 이동평균으로 분모를 만들어 큰 gradient 좌표의 step을 줄입니다. Adam은 여기에 1차 모멘트까지 결합하고 bias correction을 적용해 초반 단계 왜곡을 줄입니다. 결과적으로 스케일이 다른 파라미터를 동일 lr로도 안정적으로 학습시키는 효과를 얻습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Calculus for ML 101 (1/10): 미분이란 무엇인가](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): 함수와 기울기](./02-functions-and-slope.md)
- [Calculus for ML 101 (3/10): 편미분](./03-partial-derivatives.md)
- [Calculus for ML 101 (4/10): Gradient](./04-gradient.md)
- [Calculus for ML 101 (5/10): 연쇄 법칙](./05-chain-rule.md)
- [Calculus for ML 101 (6/10): 손실 함수](./06-loss-function.md)
- [Calculus for ML 101 (7/10): 경사하강법](./07-gradient-descent.md)
- **최적화 (현재 글)**
- 역전파 직관 (예정)
- 딥러닝에서의 미분 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Adam - Kingma and Ba](https://arxiv.org/abs/1412.6980)
- [Optimizer Overview - Ruder](https://www.ruder.io/optimizing-gradient-descent/)
- [Cosine LR Schedule - Loshchilov and Hutter](https://arxiv.org/abs/1608.03983)
- [Decoupled Weight Decay - Loshchilov and Hutter](https://arxiv.org/abs/1711.05101)

### 예제 코드
- [book-examples/calculus-for-ml-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/calculus-for-ml-101/ko)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, Optimization, Adam, Beginner

---
series: calculus-for-ml-101
episode: 6
title: "Calculus for ML 101 (6/10): 손실 함수"
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
  - LossFunction
  - MSE
  - Beginner
seo_description: 손실 함수, MSE, cross entropy, gradient와 학습 신호 직관을 ML 입문자 관점에서 정리한 글
last_reviewed: '2026-05-12'
---

# Calculus for ML 101 (6/10): 손실 함수

모델이 예측을 만들었다고 해서 학습이 자동으로 시작되지는 않습니다. 예측이 얼마나 좋은지, 어떤 방향으로 수정해야 하는지를 숫자로 표현하는 기준이 필요합니다. 손실 함수는 예측과 정답 사이의 차이를 하나의 스칼라 값으로 바꾸고, 그 값의 gradient를 통해 학습 신호를 만들어 냅니다.

중요한 점은 손실 함수가 단순한 평가 점수표가 아니라는 사실입니다. 손실 함수를 어떻게 정의하느냐에 따라 모델이 “무엇을 잘하도록” 학습되는지가 달라집니다. 즉 손실 함수 선택은 최적화 대상 자체를 정하는 일입니다.

이 글은 Calculus for ML 101 시리즈의 여섯 번째 글입니다.

이 글에서는 회귀에서 자주 쓰는 MSE, 분류에서 자주 쓰는 cross entropy, gradient가 만드는 학습 신호라는 관점에서 손실 함수를 설명하겠습니다. 목표는 손실을 숫자 하나로만 보지 않고, 학습 목적을 코드로 명시하는 설계 요소로 이해하는 것입니다.

끝까지 읽고 나면 “왜 이 모델이 이런 방향으로 학습되었는가”를 손실 함수 정의에서부터 설명할 수 있게 됩니다.

## 먼저 던지는 질문

- 손실 함수는 단순한 평가 지표와 무엇이 다를까요?
- 회귀에서 MSE를, 분류에서 cross entropy를 자주 쓰는 이유는 무엇일까요?
- 손실 함수의 gradient는 왜 학습 신호라고 불릴까요?

## 큰 그림

![Calculus for ML 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/06/06-01-concept-at-a-glance.ko.png)

*Calculus for ML 101 6장 흐름 개요*

## 왜 이 글이 중요한가

손실 함수는 모델의 목적 함수를 구체적으로 정의합니다. 같은 데이터와 같은 네트워크를 써도 손실 함수를 다르게 잡으면 모델이 학습하는 방향이 바뀝니다. 그래서 손실 함수 선택은 사소한 구현 세부사항이 아니라 문제 정의의 일부입니다.

실무에서는 loss curve를 모니터링하고, class imbalance를 보정하고, multi-task loss에 가중치를 주는 일이 모두 손실 설계와 연결됩니다. 예를 들어 분류 문제에 부적절한 회귀 손실을 쓰면 예측이 느리게 수렴하거나 calibration이 어색해질 수 있습니다. 반대로 올바른 손실을 선택하면 optimizer가 훨씬 더 일관된 신호를 받습니다.

또한 손실 함수를 이해해야 gradient를 “숫자 변화량”이 아니라 “정답과 예측의 차이가 어느 방향으로 압력을 주는가”로 읽을 수 있습니다. 이 감각은 이후 경사하강법과 최적화 글에서 매우 중요해집니다.

## 핵심 관점

손실 함수를 가장 실용적으로 이해하는 방법은 예측 오차를 단순한 차이에서 학습 가능한 숫자 신호로 바꾸는 장치로 보는 것입니다. 모델 출력이 얼마나 틀렸는지, 그리고 그 틀림이 어떤 방향 업데이트를 요구하는지를 한꺼번에 담는 구조가 손실 함수입니다.

손실 함수와 평가 지표는 역할이 다릅니다. 평가 지표는 결과를 읽는 데 쓰고, 손실 함수는 그래디언트를 만들어 학습을 진행시키는 데 씁니다. 물론 둘이 비슷할 수도 있지만, 실무에서는 “잘 측정되는 것”과 “잘 학습되는 것”을 구분해서 보는 편이 안전합니다.

> 손실 함수는 예측이 얼마나 틀렸는지 점수만 매기는 도구가 아니라, 모델이 다음 스텝에서 어디로 움직여야 하는지 결정하는 학습 신호 생성기입니다.

## 핵심 개념

손실 함수의 흐름은 다음과 같습니다.

### MSE는 회귀 문제의 기본 손실입니다

```python
def mse(y, p):
    return sum((yi - pi) ** 2 for yi, pi in zip(y, p)) / len(y)
```

MSE는 예측과 정답의 차이를 제곱해 평균낸 값입니다. 오차가 클수록 더 큰 벌점을 주므로 큰 오차에 민감합니다. 회귀 문제에서 자주 쓰이는 이유는 구현이 단순하고, 미분도 매끄럽고, 평균적인 제곱 오차를 직접 줄이는 목적과 잘 맞기 때문입니다.

### MSE의 gradient는 예측을 정답 쪽으로 밀어 줍니다

```python
def mse_grad(y, p):
    n = len(y)
    return [-2 * (yi - pi) / n for yi, pi in zip(y, p)]
```

이 gradient는 예측이 정답보다 크면 음의 방향, 작으면 양의 방향으로 업데이트 신호를 만듭니다. 여기서 중요한 것은 손실 함수가 단순히 “틀렸다”를 말하는 데서 끝나지 않고, “어느 쪽으로 얼마나 수정할지”까지 제공한다는 점입니다.

### 분류에서는 binary cross entropy가 더 자연스럽습니다

```python
import math

def bce(y, p, eps=1e-7):
    return -sum(yi * math.log(pi + eps) + (1 - yi) * math.log(1 - pi + eps) for yi, pi in zip(y, p)) / len(y)
```

Binary cross entropy는 확률 예측과 이진 정답의 차이를 측정합니다. 정답 클래스에 높은 확률을 주지 못할수록 큰 손실이 발생합니다. 분류에서는 단순 오차 크기보다 확률 분포의 적합성이 중요하므로 BCE가 더 자연스럽게 문제를 표현합니다.

여기서 `eps`를 더하는 이유는 숫자 안정성 때문입니다. `log(0)`은 정의되지 않으므로, 실제 구현에서는 극단값을 방어해야 합니다. 손실 함수는 수학적으로 맞는 것만으로 충분하지 않고, 수치적으로도 안전해야 합니다.

### 실제 손실값을 비교해 보면 역할 차이가 드러납니다

```python
y = [1, 0, 1]
p = [0.9, 0.2, 0.7]
loss = bce(y, p)
```

같은 예측이라도 어떤 손실을 적용하느냐에 따라 벌점 구조가 달라집니다. 그래서 “모델이 왜 이런 방향으로 업데이트되는가”를 보려면 optimizer만 볼 것이 아니라 손실 정의부터 봐야 합니다.

### 학습 신호는 오차를 움직임으로 바꾸는 감각입니다

```python
def signal(y, p):
    return sum(abs(yi - pi) for yi, pi in zip(y, p)) / len(y)
```

이 함수는 엄밀한 gradient는 아니지만, 예측과 정답의 차이가 어느 정도 남아 있는지를 직관적으로 보여 줍니다. 실무에서는 실제 gradient magnitude, loss slope, update norm 등을 함께 보면서 학습 신호가 충분한지 판단합니다. 중요한 것은 손실이 단순한 보고용 숫자가 아니라 optimizer가 소비하는 신호를 낳는다는 사실입니다.

### 평균과 합의 차이도 무시하면 안 됩니다

배치 크기에 따라 손실을 평균낼지 합할지 결정하면 gradient scale이 달라집니다. 이 차이는 learning rate 해석에도 직접 영향을 줍니다. 그래서 팀마다 reduction 정책을 통일하고, 실험 비교 시 손실 scale이 같은지 먼저 확인하는 습관이 중요합니다.

## 흔히 헷갈리는 지점

- 평가 metric과 학습용 loss를 같은 것으로 취급하면 문제 설계가 흐려질 수 있습니다.
- 회귀 문제에 분류용 손실을, 분류 문제에 부적절한 회귀 손실을 쓰면 optimization 신호가 어긋날 수 있습니다.
- `log(0)` 같은 숫자 안정성 이슈를 무시하면 학습이 NaN으로 무너질 수 있습니다.
- 손실 합과 평균을 혼용하면 실험 간 gradient scale 비교가 왜곡됩니다.
- MSE가 큰 오차에 민감하다는 점을 잊으면 이상치(outlier)에 과도하게 끌리는 모델이 나올 수 있습니다.

## 운영 체크리스트

- [ ] 현재 문제가 회귀인지 분류인지에 맞춰 손실 함수를 선택한다
- [ ] 손실 구현에 `eps` 같은 숫자 안정성 장치를 포함한다
- [ ] reduction이 mean인지 sum인지 실험 설정과 문서에 명시한다
- [ ] class imbalance나 task weighting이 필요한지 손실 설계 단계에서 검토한다
- [ ] loss curve와 gradient scale을 함께 보며 학습 신호 품질을 점검한다

## 정리

손실 함수는 예측과 정답의 차이를 하나의 숫자로 요약하면서, 동시에 그 차이를 gradient를 통해 학습 신호로 바꾸는 장치입니다. 회귀에서는 MSE, 분류에서는 cross entropy처럼 문제 구조와 잘 맞는 손실을 선택해야 optimizer가 올바른 방향을 읽을 수 있습니다.

실무에서는 손실 함수가 곧 문제 정의입니다. 어떤 오차를 더 크게 벌줄지, 평균을 어떻게 낼지, 불균형을 어떻게 보정할지 모두 손실 설계에 담깁니다. 그래서 모델 성능이 어색할 때는 네트워크 구조만이 아니라 손실 정의부터 다시 봐야 합니다.

다음 글에서는 손실 gradient를 실제 업데이트로 바꾸는 경사하강법을 보겠습니다. 그러면 지금까지 쌓은 미분 직관이 처음으로 학습 루프의 움직임으로 연결됩니다.



## MSE 유도와 gradient 계산

회귀에서 가장 자주 쓰는 MSE를 식부터 다시 정리해 보겠습니다.

배치 크기 `N`에서

`L = (1/N) * Σ (y_i - p_i)^2`

예측 `p_i`에 대한 도함수는

`dL/dp_i = (2/N) * (p_i - y_i)`

입니다. 즉 오차가 양수면 예측을 줄이고, 음수면 예측을 키우라는 신호가 나옵니다.

```python
import numpy as np

def mse(y, p):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    return np.mean((y - p) ** 2)

def mse_grad(y, p):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    n = y.size
    return (2.0 / n) * (p - y)

y = np.array([3.0, -1.0, 2.0])
p = np.array([2.2, -0.5, 3.0])
print('mse:', mse(y, p))
print('grad:', mse_grad(y, p))
```

오차를 제곱하기 때문에 큰 오차에 더 민감하다는 특성이 분명하게 드러납니다. 이상치가 많은 데이터라면 MSE만 고집하지 말고 Huber 같은 대안을 검토하는 것이 안전합니다.

## cross entropy 유도와 gradient

이진 분류에서 binary cross entropy(BCE)는 다음과 같습니다.

`L = -(1/N) * Σ [ y_i log(p_i) + (1-y_i)log(1-p_i) ]`

`p_i`에 대한 도함수는

`dL/dp_i = -( y_i/p_i - (1-y_i)/(1-p_i) ) / N`

입니다. 확신한 오답(`p`가 0 또는 1에 매우 가까운데 라벨이 반대)에서 gradient가 커지므로, 모델이 잘못된 확신을 빠르게 수정하도록 압력을 줍니다.

```python
import numpy as np

def bce(y, p, eps=1e-12):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    p = np.clip(p, eps, 1.0 - eps)
    return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))

def bce_grad(y, p, eps=1e-12):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    p = np.clip(p, eps, 1.0 - eps)
    n = y.size
    return (-(y / p) + (1 - y) / (1 - p)) / n

y = np.array([1, 0, 1, 0], dtype=float)
p = np.array([0.9, 0.3, 0.6, 0.1], dtype=float)
print('bce :', bce(y, p))
print('grad:', bce_grad(y, p))
```

## 손실 지형(loss landscape) 읽기

손실 함수는 숫자 하나지만, 파라미터 공간에서는 지형을 이룹니다. 이 지형을 읽으면 왜 optimizer 설정이 민감한지 이해하기 쉬워집니다.

```python
import numpy as np

def loss_surface(w1, w2):
    return (w1 - 1.0)**2 + 0.5*(w2 + 2.0)**2 + 0.2*w1*w2

w1s = np.linspace(-3, 3, 7)
w2s = np.linspace(-4, 2, 7)
grid = np.array([[loss_surface(a, b) for b in w2s] for a in w1s])
print(grid)
```

등고선 관점에서는 다음을 먼저 확인합니다.

| 지형 특징 | 학습 영향 | 권장 대응 |
| --- | --- | --- |
| 완만한 평지(plateau) | gradient 작아 학습 정체 | lr schedule, warmup, 초기화 개선 |
| 좁은 협곡 | 축별 진동 증가 | 정규화, momentum, 적응형 optimizer |
| 다중 골짜기 | 초기값 의존성 증가 | seed 다중 실험, 앙상블 고려 |
| 날카로운 절벽 | 수치 불안정 위험 | gradient clipping, 손실 안정화 |

## 커스텀 손실 구현 예시

실무에서는 도메인 제약 때문에 기본 손실에 항을 추가하는 경우가 많습니다. 예를 들어 회귀 오차 + L2 정규화 + 임계치 초과 패널티를 함께 쓸 수 있습니다.

```python
import torch

class HybridLoss(torch.nn.Module):
    def __init__(self, l2_weight=1e-4, threshold=2.0, penalty_weight=0.5):
        super().__init__()
        self.l2_weight = l2_weight
        self.threshold = threshold
        self.penalty_weight = penalty_weight

    def forward(self, pred, target, model_params):
        mse = torch.mean((pred - target) ** 2)
        l2 = torch.zeros((), device=pred.device)
        for p in model_params:
            l2 = l2 + torch.sum(p ** 2)

        excess = torch.relu(torch.abs(pred - target) - self.threshold)
        robust_penalty = torch.mean(excess)

        return mse + self.l2_weight * l2 + self.penalty_weight * robust_penalty
```

커스텀 손실을 도입할 때는 반드시 세 항의 scale을 로그로 분리해 기록해야 합니다. 총손실만 보면 어느 항이 학습을 지배하는지 알 수 없습니다.

## 손실 함수 선택 가이드

손실 선택은 "문제 타입"과 "운영 제약"을 같이 봐야 합니다.

| 문제 상황 | 기본 후보 | 보강 옵션 | 점검 질문 |
| --- | --- | --- | --- |
| 연속값 회귀 | MSE | Huber, LogCosh | 이상치 비중이 높은가 |
| 이진 분류 | BCE | Focal Loss, class weight | 클래스 불균형이 큰가 |
| 다중 분류 | Cross Entropy | Label Smoothing | 과신(confidence) 완화가 필요한가 |
| 순위/추천 | Pairwise loss | sampled softmax | 상대 순서가 중요한가 |
| 다중 과제 | 가중 합 손실 | uncertainty weighting | 과제별 gradient 균형이 맞는가 |

실무 기준으로는 다음 순서를 권장합니다.

1. 문제 타입에 맞는 표준 손실로 시작합니다.
2. 실패 패턴을 관찰한 뒤 최소 보강만 추가합니다.
3. 보강 항을 넣을 때는 각 항의 scale과 gradient norm을 함께 모니터링합니다.

## 수치 안정성: NaN을 막는 구현 규칙

손실 함수는 미분 가능성뿐 아니라 수치 안정성까지 만족해야 합니다. 특히 log/exp 연산은 안정화 수식이 필수입니다.

```python
import torch

# logits 기반 BCE는 내부적으로 안정화된 구현을 사용
criterion = torch.nn.BCEWithLogitsLoss()
logits = torch.tensor([3.0, -2.0, 0.4])
target = torch.tensor([1.0, 0.0, 1.0])
loss = criterion(logits, target)
print(loss)
```

`sigmoid -> BCE`를 분리해서 직접 구현하면 underflow/overflow 위험이 커집니다. 가능하면 `BCEWithLogitsLoss`처럼 결합된 안정화 구현을 쓰는 편이 안전합니다.

추가로 자주 쓰는 안정화 규칙은 다음과 같습니다.

- `log(p)` 전에는 `p = clip(p, eps, 1-eps)`를 적용합니다.
- `exp(x)`는 큰 양수 입력에서 overflow가 나므로 `x` 범위를 제한합니다.
- 합-로그 형태는 `log-sum-exp` 트릭으로 계산합니다.
- mixed precision에서는 loss scaling과 gradient overflow 체크를 함께 사용합니다.

| 위험 연산 | 불안정 조건 | 안정화 방법 |
| --- | --- | --- |
| `log(p)` | `p -> 0` | clipping 또는 logits 기반 구현 |
| `exp(x)` | `x >> 0` | 입력 클램프, `torch.logsumexp` |
| `1/p` | `p -> 0` | 분모 epsilon 추가 |
| softmax | 큰 logits 차이 | max-shift softmax |

## 손실 디버깅 루틴

모델이 학습되지 않을 때는 복잡한 변경보다 손실 경로를 먼저 점검하는 것이 빠릅니다.

1. 배치 하나로 forward/backward를 돌려 loss와 grad의 유한성(`isfinite`)을 확인합니다.
2. 손실 항이 여러 개면 항별 값과 항별 gradient norm을 분리 로그로 남깁니다.
3. 라벨 분포, 예측 분포, threshold 기반 성능을 함께 비교합니다.
4. 학습률을 바꾸기 전에 손실 구현의 reduction(mean/sum) 일관성을 확인합니다.

```python
def assert_finite(tensor, name):
    if not torch.isfinite(tensor).all():
        raise ValueError(f'{name} contains NaN or Inf')
```

이 루틴을 자동화하면 손실 문제를 모델 구조 문제와 분리해 더 빠르게 해결할 수 있습니다.


## 다중 분류 cross entropy와 softmax gradient

다중 분류에서는 softmax와 cross entropy를 함께 사용합니다. 클래스 `k`의 확률을 `p_k`라고 하면

`L = - Σ y_k log(p_k)`

이며 one-hot 라벨일 때 `dL/dz = p - y` 형태로 단순화됩니다(`z`는 logits). 이 단순화 덕분에 구현이 안정적이고 계산도 효율적입니다.

```python
import numpy as np

def softmax(z):
    z = z - np.max(z)
    e = np.exp(z)
    return e / np.sum(e)

def ce_with_logits_grad(logits, y_onehot):
    p = softmax(logits)
    return p - y_onehot

logits = np.array([2.0, 0.5, -1.0])
y = np.array([1.0, 0.0, 0.0])
print(ce_with_logits_grad(logits, y))
```

실무에서 프레임워크의 `CrossEntropyLoss`가 logits 입력을 요구하는 이유도 여기에 있습니다. softmax를 밖에서 한 번 더 적용하면 gradient가 왜곡될 수 있습니다.

## 불균형 데이터에서 손실 설계

클래스 불균형이 큰 문제에서는 평균 손실만으로는 소수 클래스 학습이 약해질 수 있습니다. 가중치 기반 손실이나 focal loss를 통해 희귀 클래스에 더 큰 신호를 줄 수 있습니다.

| 방법 | 핵심 아이디어 | 장점 | 주의점 |
| --- | --- | --- | --- |
| class weight | 클래스별 손실 가중치 조정 | 구현 단순 | 과대 가중 시 불안정 |
| focal loss | 쉬운 샘플 가중치 감소 | 어려운 샘플 집중 | gamma 튜닝 필요 |
| resampling + 표준 손실 | 데이터 분포 보정 | 직관적 | 분산 증가 가능 |

```python
import torch

criterion = torch.nn.CrossEntropyLoss(weight=torch.tensor([1.0, 3.0, 6.0]))
logits = torch.randn(8, 3)
target = torch.tensor([0, 1, 2, 2, 1, 0, 2, 1])
loss = criterion(logits, target)
print(loss)
```

## 손실 항 가중치 조정 실무 규칙

다중 과제 모델이나 하이브리드 손실에서는 항별 가중치가 성능을 좌우합니다. 임의로 값을 정하기보다 다음 절차를 권장합니다.

1. 초기 100~500 step에서 각 항의 평균값과 gradient norm을 기록합니다.
2. 특정 항이 전체를 지배하면 가중치를 축소합니다.
3. 검증 지표 개선 폭이 작은 항은 제거를 검토합니다.

| 항목 | 기록 지표 | 해석 |
| --- | --- | --- |
| 기본 예측 손실 | 평균값, 분산 | 학습 목표 적합성 |
| 정규화 항 | 값 대비 grad 기여 | 과규제 여부 |
| 제약 패널티 | 활성화 비율 | 제약이 실제로 작동하는지 |

## 손실 구현 검증용 단위 테스트

손실 함수는 모델 코드보다 작지만, 작은 버그가 학습 전체를 망가뜨립니다. 최소 단위 테스트를 두면 위험을 크게 줄일 수 있습니다.

```python
import numpy as np

def test_mse_zero_when_equal():
    y = np.array([1.0, 2.0, 3.0])
    p = np.array([1.0, 2.0, 3.0])
    assert np.isclose(np.mean((y-p)**2), 0.0)

def test_bce_finite():
    y = np.array([0.0, 1.0])
    p = np.array([1e-15, 1-1e-15])
    p = np.clip(p, 1e-12, 1-1e-12)
    loss = -np.mean(y*np.log(p)+(1-y)*np.log(1-p))
    assert np.isfinite(loss)
```

이 정도 테스트만 있어도 `log(0)` 계열 문제를 커밋 전에 잡을 수 있습니다.


## 손실과 평가 지표의 분리 운영

학습 손실이 좋아도 운영 지표가 나빠질 수 있습니다. 따라서 손실과 지표를 분리해 모니터링해야 합니다.

| 구분 | 목적 | 예시 |
| --- | --- | --- |
| 학습 손실 | gradient 생성 | MSE, BCE, CE |
| 오프라인 평가 | 모델 비교 | RMSE, F1, AUC |
| 온라인 지표 | 제품 성과 | CTR, 전환율, 지연시간 |

손실은 최적화 편의 때문에 설계되고, 제품 지표는 비즈니스 목적 때문에 정의됩니다. 둘이 완전히 일치하지 않는 것이 일반적이므로, 실험 리포트에 두 축을 함께 기록해야 의사결정이 정확해집니다.

## 수치 안정성 회귀 테스트

손실 구현은 라이브러리 업데이트나 dtype 변경으로도 쉽게 흔들릴 수 있습니다. 정기 회귀 테스트를 추가해 안정성을 유지해야 합니다.

```python
def finite_check(loss_fn, inputs):
    import numpy as np
    vals = [loss_fn(*x) for x in inputs]
    return all(np.isfinite(v) for v in vals)
```

극단 logits, 극단 확률, 빈 배치 경계 케이스를 고정 세트로 두면 배포 전 사고를 크게 줄일 수 있습니다.

## 처음 질문으로 돌아가기

- **손실 함수는 단순한 평가 지표와 무엇이 다를까요?**
  - 평가 지표는 결과를 읽는 값이고, 손실 함수는 `dL/dp`를 만들어 파라미터 업데이트를 유도하는 학습 엔진입니다. MSE/BCE 유도식에서 보듯 손실은 오차의 크기뿐 아니라 수정 방향까지 제공합니다.
- **회귀에서 MSE를, 분류에서 cross entropy를 자주 쓰는 이유는 무엇일까요?**
  - MSE는 연속 오차를 제곱 벌점으로 다루어 회귀 목표와 잘 맞고, BCE는 확률 예측의 우도 관점과 연결되어 분류의 신뢰도 오류를 강하게 교정합니다. 따라서 문제 구조와 gradient 신호의 형태가 각각 자연스럽게 맞물립니다.
- **손실 함수의 gradient는 왜 학습 신호라고 불릴까요?**
  - gradient는 "얼마나 틀렸는가"를 "어느 방향으로 얼마나 움직일 것인가"로 변환합니다. 손실 지형, 커스텀 손실 항, 수치 안정화 규칙까지 포함해 이 신호 품질을 관리해야 실제 학습이 안정적으로 진행됩니다.

## 처음 질문으로 돌아가기

- **손실 함수는 단순한 평가 지표와 무엇이 다를까요?**
  - 본문의 기준은 손실 함수를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **회귀에서 MSE를, 분류에서 cross entropy를 자주 쓰는 이유는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **손실 함수의 gradient는 왜 학습 신호라고 불릴까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Calculus for ML 101 (1/10): 미분이란 무엇인가](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): 함수와 기울기](./02-functions-and-slope.md)
- [Calculus for ML 101 (3/10): 편미분](./03-partial-derivatives.md)
- [Calculus for ML 101 (4/10): Gradient](./04-gradient.md)
- [Calculus for ML 101 (5/10): 연쇄 법칙](./05-chain-rule.md)
- **손실 함수 (현재 글)**
- 경사하강법 (예정)
- 최적화 (예정)
- 역전파 직관 (예정)
- 딥러닝에서의 미분 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Loss Functions - PyTorch](https://pytorch.org/docs/stable/nn.html#loss-functions)
- [Cross Entropy - CS231n](https://cs231n.github.io/linear-classify/)
- [Deep Learning Book - Loss](https://www.deeplearningbook.org/contents/mlp.html)
- [Class Imbalance - scikit-learn](https://scikit-learn.org/stable/modules/svm.html#unbalanced-problems)

### 예제 코드
- [book-examples/calculus-for-ml-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/calculus-for-ml-101/ko)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, LossFunction, MSE, Beginner

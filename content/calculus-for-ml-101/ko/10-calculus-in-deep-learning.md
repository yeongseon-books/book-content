---
series: calculus-for-ml-101
episode: 10
title: "Calculus for ML 101 (10/10): 딥러닝에서의 미분"
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
  - DeepLearning
  - Capstone
  - Beginner
seo_description: 네트워크, 손실, optimizer, backprop과 미분이 딥러닝 학습 루프에서 어떻게 합쳐지는지 정리한 글
last_reviewed: '2026-05-12'
---

# Calculus for ML 101 (10/10): 딥러닝에서의 미분

이 시리즈에서 지금까지 본 개념들은 각각 따로 존재하지 않습니다. 함수와 기울기, 편미분, gradient, chain rule, 손실 함수, 경사하강법, optimizer, 역전파는 모두 딥러닝 학습 루프 안에서 하나의 사이클로 묶여 움직입니다. 마지막 글의 목표는 그 조각들을 하나의 운영 모델로 합치는 것입니다.

이 글은 Calculus for ML 101 시리즈의 마지막 글입니다.

딥러닝 학습은 겉으로 보면 반복문 한 줄처럼 보일 수 있습니다. 하지만 그 안에서는 예측을 만들고, 오차를 수치화하고, chain rule로 gradient를 계산하고, optimizer가 파라미터를 조정하는 과정이 정밀하게 이어집니다. 이 전체 고리를 이해해야 프레임워크 사용법을 넘어서 학습 자체를 설명할 수 있습니다.

이 글에서는 forward pass, loss computation, backward pass, optimizer update, 반복 학습을 하나의 training loop로 묶어 설명하겠습니다. 목표는 “딥러닝이 학습한다”는 문장을 추상적으로 두지 않고, 미분이 실제로 어디에서 어떤 역할을 하는지 단계별로 복원하는 것입니다.

끝까지 읽고 나면 딥러닝 훈련 코드를 볼 때 각 줄이 어떤 수학적 의미를 갖는지, 그리고 왜 미분이 그 전체 루프의 중심인지 선명하게 보이게 됩니다.

![Calculus for ML 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/10/10-01-concept-at-a-glance.ko.png)
*Calculus for ML 101 10장 흐름 개요*

## 먼저 던지는 질문

- 딥러닝 학습 루프는 어떤 단계로 구성되고 각 단계에서 미분은 어디에 등장할까요?
- forward pass와 loss computation은 backward를 위해 무엇을 준비할까요?
- gradient 계산과 optimizer update는 어떻게 연결될까요?

## 왜 이 글이 중요한가

딥러닝 프레임워크는 training loop를 매우 간결하게 감춰 줍니다. 그래서 코드는 짧아지지만, 각 단계의 의미가 흐려지기 쉽습니다. forward가 무엇을 만들고, loss가 무엇을 수치화하고, backward가 무엇을 전파하며, optimizer가 무엇을 바꾸는지 이해해야 학습 버그를 제대로 읽을 수 있습니다.

실무에서는 같은 모델 구조라도 data pipeline, loss reduction, gradient zeroing, optimizer scheduling, eval/train mode 관리에 따라 결과가 크게 달라집니다. 이 모두를 관통하는 공통 골격이 training loop입니다. 마지막 글에서 이 골격을 잡아 두면 이후 어떤 프레임워크를 보더라도 본질을 잃지 않게 됩니다.

또한 이 글은 시리즈 전체의 요약이기도 합니다. 미분은 더 이상 별도의 수학 단원이 아니라, 예측을 오차로 바꾸고 그 오차를 다시 파라미터 변화로 환원하는 전 과정을 움직이는 중심 메커니즘으로 보이게 됩니다.

## 핵심 관점

딥러닝 학습을 가장 실용적으로 이해하는 방법은 하나의 루프를 떠올리는 것입니다. 모델이 입력으로부터 예측을 만들고, 손실 함수가 오차를 계산하고, 역전파가 gradient를 만들고, optimizer가 파라미터를 갱신합니다. 그리고 이 과정이 반복됩니다.

이 루프를 이해하면 미분은 코드 한 줄이 아니라 루프 전체를 관통하는 공통 언어가 됩니다. forward는 함수 합성이고, loss는 목적 함수이며, backward는 chain rule의 실행이고, optimizer step은 gradient를 이동으로 바꾸는 절차입니다.

> 딥러닝에서 미분은 특정 레이어의 공식이 아니라, 예측 오차를 파라미터 업데이트로 변환하는 학습 루프 전체의 공통 인터페이스입니다.

## 핵심 개념

training loop의 핵심 흐름은 아래와 같습니다.

### 모델은 입력을 예측으로 바꾸는 함수입니다

```python
import math

def model(x, w, b):
    return sigmoid(w * x + b)

def sigmoid(z):
    return 1 / (1 + math.exp(-z))
```

이 작은 모델은 선형 결합 뒤에 sigmoid를 붙인 가장 단순한 형태입니다. 하지만 여기에 이미 함수 합성과 비선형성이 모두 들어 있습니다. 복잡한 딥러닝 모델도 본질적으로는 이런 함수들의 긴 합성입니다.

### 손실은 예측과 정답의 차이를 숫자로 만듭니다

```python
def bce(y, p, eps=1e-7):
    return -(y * math.log(p + eps) + (1 - y) * math.log(1 - p + eps))
```

forward만으로는 학습이 일어나지 않습니다. 예측이 얼마나 틀렸는지를 loss로 수치화해야 하고, 이 loss가 gradient의 출발점이 됩니다. 여기서 숫자 안정성을 위해 `eps`를 더하는 습관은 실제 training code에서도 매우 중요합니다.

### gradient는 analytic form으로도 볼 수 있습니다

```python
def grads(x, y, w, b):
    p = model(x, w, b)
    err = p - y
    return err * x, err
```

이 함수는 BCE와 sigmoid 조합에서 나오는 단순화된 gradient 직관을 보여 줍니다. 핵심은 error가 각 파라미터의 책임으로 분해된다는 사실입니다. 입력 쪽 weight는 `err * x`, bias는 `err` 형태로 영향을 받습니다. 즉 편미분과 chain rule이 실제 코드 결과로 나타난 것입니다.

### optimizer step은 gradient를 이동으로 바꿉니다

```python
def step(x, y, w, b, lr=0.1):
    dw, db = grads(x, y, w, b)
    return w - lr * dw, b - lr * db
```

이 한 줄이 optimizer의 본질입니다. backward가 준 gradient를 learning rate만큼 스케일해 반대 방향으로 이동합니다. 대형 프레임워크에서는 Adam, momentum, weight decay 등이 추가되지만, 핵심 구조는 그대로입니다.

### 반복문이 곧 학습 루프입니다

```python
def train(data, epochs=100, lr=0.1):
    w, b = 0.0, 0.0
    for _ in range(epochs):
        for x, y in data:
            w, b = step(x, y, w, b, lr)
    return w, b
```

학습은 거창한 것이 아니라 이 반복입니다. 데이터가 들어오고, 예측이 만들어지고, 손실이 계산되고, gradient가 업데이트로 바뀌며, 그 결과 새로운 파라미터가 다음 forward에 사용됩니다. 이 닫힌 고리가 학습의 전부라고 해도 과언이 아닙니다.

### 프레임워크 코드에서도 같은 루프가 그대로 드러납니다

```python
optimizer.zero_grad()
pred = model(x)
loss = criterion(pred, y)
loss.backward()
optimizer.step()
```

이 다섯 줄에는 지금까지 본 개념이 모두 압축되어 있습니다. `pred = model(x)`는 함수 합성이고, `loss = criterion(pred, y)`는 목적 함수를 구체화하는 단계이며, `loss.backward()`는 연쇄 법칙과 역전파를 실행하는 부분입니다. 마지막 `optimizer.step()`은 그래디언트를 실제 파라미터 이동으로 바꿉니다.

### 평가 루프가 다른 이유도 같은 구조로 설명할 수 있습니다

```python
with torch.no_grad():
    pred = model(x)
    metric = accuracy(pred, y)
```

평가 단계에서는 그래디언트가 필요하지 않으므로 backward 그래프를 만들지 않는 편이 맞습니다. 이 차이를 이해하면 왜 `train()`/`eval()` 모드 전환과 `no_grad()` 문맥이 중요한지 자연스럽게 연결됩니다. 같은 모델 코드를 쓰더라도 학습 루프와 평가 루프는 목표가 다르기 때문입니다.

### 학습 루프를 볼 때 가장 먼저 확인할 실패 지점

- `zero_grad`를 빼먹어 이전 step의 gradient가 계속 누적되고 있지 않은가
- `loss`는 내려가는데 평가 metric은 나빠져 손실 설계가 실제 목표와 어긋나고 있지 않은가
- `optimizer.step()`은 호출했지만 scheduler 순서나 train/eval 모드 전환이 꼬이지 않았는가
- reproducibility 설정이 없어 실험 차이를 모델 구조 문제로 오해하고 있지 않은가

실전에서 자주 만나는 학습 버그는 복잡한 수식보다 이런 운영 디테일에서 시작합니다. 그래서 마지막 글에서는 루프 자체를 하나의 운영 단위로 보는 감각이 중요합니다.

### 실무에서는 루프 주변의 운영 규칙도 함께 봐야 합니다

실제 코드에서는 `zero_grad`, `model.train()`, `model.eval()`, seed 고정, mixed precision, gradient clipping, scheduler step 같은 규칙이 이 루프 주변에 붙습니다. 하지만 이런 운영 요소들도 결국 forward-loss-backward-update 구조를 안정적으로 실행하기 위한 보조 장치입니다.

## 흔히 헷갈리는 지점

- loss를 계산했다고 해서 자동으로 업데이트가 되는 것은 아닙니다. backward와 optimizer step이 이어져야 합니다.
- `zero_grad`를 빼먹으면 이전 step의 gradient가 누적될 수 있습니다.
- evaluation 중에도 gradient를 계산하면 불필요한 메모리와 계산을 사용하게 됩니다.
- train/eval mode를 혼동하면 Dropout, BatchNorm 동작이 달라져 결과 해석이 틀어질 수 있습니다.
- reproducibility를 무시하면 실험 차이가 모델 구조 때문인지 학습 루프 설정 때문인지 구분하기 어려워집니다.

## 운영 체크리스트

- [ ] forward, loss, backward, update의 순서를 팀 공통 학습 루프로 명확히 정리한다
- [ ] `zero_grad`와 optimizer step의 위치를 코드 리뷰 기준에 포함한다
- [ ] train/eval mode 전환 규칙을 실험 코드와 추론 코드에서 분리한다
- [ ] learning rate, seed, scheduler, weight decay를 함께 기록해 재현성을 확보한다
- [ ] 학습 문제를 볼 때 모델 구조뿐 아니라 training loop 전체를 한 번에 점검한다

## 자동미분의 실제 동작: Forward mode와 Reverse mode

자동미분은 symbolic 미분이나 수치 미분과 다릅니다. 프로그램 연산 그래프를 그대로 따라가며 정확한 미분값을 계산합니다.

### 순방향 모드(Forward mode)

Forward mode는 입력 방향으로 미분 신호를 함께 전파합니다. 각 변수에 대해 값과 tangent를 동시에 유지합니다.

\[
(x, \dot{x}) 
ightarrow (f(x), \dot{f})
\]

입력 차원이 작고 출력 차원이 큰 문제에서 유리합니다.

### 역방향 모드(Reverse mode)

Reverse mode는 먼저 값을 전부 계산한 뒤, 출력에서 입력으로 adjoint를 전파합니다. 딥러닝은 보통 파라미터 수가 매우 많고 출력(loss)은 스칼라이므로 reverse mode가 압도적으로 효율적입니다.

| 방식 | 계산 방향 | 한 번 실행으로 얻는 정보 | 유리한 경우 |
| --- | --- | --- | --- |
| Forward mode | 입력 -> 출력 | 하나의 입력 방향 도함수 | 입력 차원 작음 |
| Reverse mode | 출력 -> 입력 | 하나의 출력에 대한 모든 입력 gradient | 파라미터가 매우 많은 학습 |

```python
# PyTorch reverse-mode 예시
optimizer.zero_grad()
loss = criterion(model(x), y)
loss.backward()  # dloss/dtheta 전체 계산
optimizer.step()
```

## Jacobian과 Hessian을 실전에 연결하기

Jacobian은 벡터 출력의 1차 미분 행렬, Hessian은 스칼라 함수의 2차 미분 행렬입니다.

\[
J_{ij} = rac{\partial f_i}{\partial x_j}, \quad
H_{ij} = rac{\partial^2 L}{\partial x_i\partial x_j}
\]

### Jacobian이 필요한 장면

- sequence-to-sequence 구조에서 입력 민감도 분석
- normalizing flow에서 log-det Jacobian 계산
- 물리 기반 모델에서 상태 전이 민감도 추정

```python
import torch
from torch.autograd.functional import jacobian

def f(v):
    x, y = v[0], v[1]
    return torch.stack([x * y, x + y**2])

v = torch.tensor([2.0, 3.0], requires_grad=True)
J = jacobian(f, v)
print(J)
```

### Hessian이 필요한 장면

- loss landscape curvature 분석
- sharpness 기반 일반화 진단
- 2차 근사 기반 step 크기 조정

```python
import torch
from torch.autograd.functional import hessian

def scalar_loss(v):
    x, y = v[0], v[1]
    return (x - 1)**2 + 3*(y + 2)**2 + x*y

v = torch.tensor([0.0, 0.0], requires_grad=True)
H = hessian(scalar_loss, v)
print(H)
```

전체 Hessian은 비용이 매우 커서, 실무에서는 Hessian-vector product(HVP)나 대각 근사(diagonal approximation)를 주로 사용합니다.

## 2차 최적화 방법 개요

1차 방법(SGD, Adam)은 gradient만 사용합니다. 2차 방법은 curvature 정보를 추가로 반영해 계곡 형태를 더 정교하게 따라갑니다.

### Newton 방법의 핵심

\[
	heta_{t+1} = 	heta_t - H^{-1}
abla L
\]

이론적으로 빠른 수렴을 기대할 수 있지만, 대규모 딥러닝에서는 Hessian 계산과 역행렬 비용이 너무 큽니다.

### 실무형 근사들

| 방법 | 아이디어 | 장점 | 한계 |
| --- | --- | --- | --- |
| L-BFGS | 저랭크 근사로 curvature 축적 | 작은/중간 문제에서 빠름 | 대규모 미니배치에 부적합 |
| K-FAC | 층 단위 Fisher 근사 | 딥러닝 구조 활용 | 구현 복잡도 높음 |
| Shampoo 계열 | 행렬 preconditioner | 좌표별보다 풍부한 곡률 반영 | 메모리/연산 비용 증가 |

실무에서는 2차 방법을 전면 도입하기보다, AdamW + 스케줄 + clipping 조합으로 충분한 안정성을 확보한 뒤 특정 병목에 선택적으로 적용하는 편이 일반적입니다.

## Attention 메커니즘에서의 미분

Transformer에서 핵심은 scaled dot-product attention입니다.

\[
A = softmax\left(rac{QK^T}{\sqrt{d_k}}
ight), \quad O = AV
\]

### gradient 흐름 요약

- `dL/dO`가 주어지면 `V` 방향 gradient는 `A^T(dL/dO)` 형태로 계산됩니다.
- `A` 방향 gradient는 `(dL/dO)V^T`를 거쳐 softmax Jacobian을 통과합니다.
- softmax는 확률합 제약이 있어 Jacobian이 대각/비대각 항을 모두 가집니다.

즉 attention에서는 행렬곱 미분 + softmax 미분 + scaling의 조합이 연쇄 법칙으로 연결됩니다.

### 작은 shape 추적 예시

| 텐서 | shape (배치 제외) |
| --- | --- |
| `Q, K, V` | `(T, d)` |
| `scores = QK^T` | `(T, T)` |
| `A = softmax(scores)` | `(T, T)` |
| `O = AV` | `(T, d)` |

shape를 먼저 고정해 두면 backward 디버깅에서 차원 오류를 크게 줄일 수 있습니다.

## 정규화 계층에서의 미분

BatchNorm, LayerNorm은 공통적으로 "정규화 -> 스케일/시프트" 구조를 갖습니다.

\[
\hat{x} = rac{x-\mu}{\sqrt{\sigma^2+\epsilon}}, \quad y = \gamma\hat{x}+eta
\]

### LayerNorm 역전파에서 중요한 점

- 입력 gradient는 평균/분산 경로를 통해 서로 결합됩니다.
- 같은 토큰 내부 feature 간 상호작용 항이 생겨 단순 element-wise 미분보다 복잡합니다.
- `epsilon`은 수치 안정성에 직접 관여하므로 아주 작은 값으로 고정하면 반대로 불안정해질 수 있습니다.

### 운영 관점 체크

| 항목 | 의미 | 점검 방법 |
| --- | --- | --- |
| `eps` | 분모 안정성 | NaN/Inf 발생 시 우선 점검 |
| `gamma` 초기값 | 스케일 자유도 | 학습 초반 출력 분산 확인 |
| train/eval 모드 | BN 통계 업데이트 | 추론 성능 흔들림 여부 확인 |

## 전체 학습 루프 해부: 미분이 움직이는 지점

아래는 실제 학습 루프를 단계별로 해부한 표입니다.

| 단계 | 코드 단위 | 미분 관점 의미 | 실패 시 증상 |
| --- | --- | --- | --- |
| 1 | `model.train()` | 미분 가능 경로 준비 | BN/Dropout 동작 불일치 |
| 2 | `pred = model(x)` | 합성함수 값 계산, 캐시 생성 | 메모리 과다, shape 오류 |
| 3 | `loss = criterion(pred, y)` | 목적 함수 스칼라화 | loss 스케일 왜곡 |
| 4 | `loss.backward()` | reverse-mode AD 실행 | grad None, NaN |
| 5 | `clip_grad_norm_` | gradient 안정화 | 학습 정체/발산 |
| 6 | `optimizer.step()` | gradient -> 파라미터 이동 | 업데이트 누락 |
| 7 | `scheduler.step()` | 시간축 정책 반영 | lr 곡선 비정상 |
| 8 | `optimizer.zero_grad()` | 누적 버퍼 초기화 | 이전 step 신호 혼입 |

### 코드로 보는 전체 골격

```python
for epoch in range(num_epochs):
    model.train()
    for x, y in train_loader:
        pred = model(x)
        loss = criterion(pred, y)

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()

    model.eval()
    with torch.no_grad():
        for x_val, y_val in val_loader:
            val_pred = model(x_val)
            val_loss = criterion(val_pred, y_val)
```

이 루프를 이해하면 프레임워크가 달라도 핵심 진단 포인트는 거의 같습니다. 미분의 역할은 `loss.backward()` 한 줄로 끝나는 것이 아니라, 그 앞뒤 단계가 만든 조건 위에서 의미를 갖습니다.

## 미분 중심 디버깅 체크리스트

1. **gradient 존재성 확인**: 주요 파라미터의 `.grad is None` 여부를 먼저 확인합니다.
2. **gradient 규모 확인**: 층별 norm 히스토그램으로 소실/폭주를 확인합니다.
3. **loss 스케일 확인**: reduction(`mean`/`sum`) 설정으로 gradient 규모가 과도하게 변하지 않는지 봅니다.
4. **mixed precision 점검**: scaler update, overflow skip 횟수를 기록합니다.
5. **스케줄러 순서 점검**: `optimizer.step()`과 `scheduler.step()` 호출 순서를 문서화합니다.

## 시리즈 전체를 한 장으로 연결하기

이 시리즈 10편의 개념은 아래처럼 하나의 문장으로 연결됩니다.

- 함수와 기울기는 변화율의 언어를 제공합니다.
- 편미분과 gradient는 다변수 손실 지형에서 하강 방향을 정의합니다.
- chain rule과 역전파는 그 방향을 깊은 합성함수 전체로 확장합니다.
- optimizer와 scheduler는 gradient를 실제 학습 궤적으로 변환합니다.
- 최종적으로 training loop가 이 과정을 반복해 성능을 개선합니다.

## 손실 함수와 미분 스케일링

같은 모델이라도 손실 설계가 바뀌면 gradient 규모와 학습 동역학이 크게 변합니다.

### 대표 손실의 gradient 특성

| 손실 | 핵심 gradient 특성 | 실무 포인트 |
| --- | --- | --- |
| MSE | 오차 크기에 선형 비례 | 이상치에 민감 |
| BCEWithLogits | 확신한 오답에 큰 신호 | 수치 안정 구현 권장 |
| CrossEntropy | softmax와 결합 시 단순화 | 다중분류 기본 선택 |
| Huber | 큰 오차 구간 완화 | 노이즈 라벨에 강함 |

손실을 바꾼 뒤 학습률을 그대로 유지하면 gradient 스케일 mismatch가 생기기 쉽습니다. 따라서 손실 변경은 optimizer 튜닝 변경과 한 세트로 다뤄야 합니다.

## 전체 루프에서 재현성까지 묶기

미분 기반 학습은 확률적 요소가 많아서 재현성 관리가 중요합니다.

```python
import random
import numpy as np
import torch

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

같은 미분 공식을 써도 seed, 데이터 셔플, mixed precision 설정이 바뀌면 학습 경로가 달라집니다. 그래서 실험 로그에는 수학적 설정과 운영 설정을 함께 기록해야 합니다.

## 캡스톤 점검표: 미분 관점에서 학습 실패 줄이기

1. 모델 출력과 손실 입력의 shape를 먼저 검증합니다.
2. 첫 100 step에서 loss, lr, grad norm을 함께 저장합니다.
3. NaN 발생 시 입력 스케일, 손실 안정화 옵션, clipping 순으로 점검합니다.
4. val 성능 정체 시 optimizer보다 데이터 분포/라벨 품질도 함께 확인합니다.
5. 최종 보고에는 "어떤 미분 신호가 어떤 업데이트 정책으로 성능 개선을 만들었는가"를 문장으로 남깁니다.

## 정리

딥러닝에서 미분은 특정 수식의 일부가 아니라 학습 루프 전체를 움직이는 중심 메커니즘입니다. forward는 함수 합성으로 예측을 만들고, loss는 오차를 숫자로 바꾸고, backward는 chain rule로 gradient를 계산하고, optimizer는 그 gradient를 파라미터 업데이트로 바꿉니다.

이 시리즈에서 본 미분, 편미분, 그래디언트, 연쇄 법칙, 손실 함수, 경사하강법, 최적화, 역전파는 모두 이 하나의 루프 안에서 각자 자리를 갖습니다. 그래서 딥러닝을 이해한다면 결국 이 루프의 각 단계가 어떤 수학적 역할을 맡는지 설명할 수 있어야 합니다.

이 글로 Calculus for ML 101 시리즈를 마칩니다. 이제 이후 어떤 모델이나 프레임워크를 보더라도, 그 안에서 학습이 실제로 어떻게 일어나는지 미분의 언어로 다시 읽어 낼 수 있을 것입니다.

## 처음 질문으로 돌아가기

- **딥러닝 학습 루프는 어떤 단계로 구성되고 각 단계에서 미분은 어디에 등장할까요?**
  - 학습 루프는 `forward -> loss -> backward -> update` 순서로 구성됩니다. 미분은 backward에서만 나타나는 것이 아니라, forward에서 저장한 중간값과 loss의 스칼라화가 있어야 reverse-mode가 성립합니다. 즉 미분은 루프 전체의 연결 규칙입니다.
- **forward pass와 loss computation은 backward를 위해 무엇을 준비할까요?**
  - forward는 각 연산 노드의 값과 그래프 연결을 만들고, loss는 최종 스칼라 목적을 정의합니다. 이 두 단계가 준비되어야 backward가 local gradient를 연쇄적으로 곱해 각 파라미터 gradient를 계산할 수 있습니다.
- **gradient 계산과 optimizer update는 어떻게 연결될까요?**
  - backward가 만든 `dL/dtheta`는 optimizer의 입력입니다. optimizer는 lr, 모멘트, 분산 추정, weight decay 같은 정책을 적용해 gradient를 실제 파라미터 이동으로 바꿉니다. 따라서 gradient 품질과 optimizer 정책은 분리된 문제가 아니라 같은 학습 경로의 연속 단계입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Calculus for ML 101 (1/10): 미분이란 무엇인가](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): 함수와 기울기](./02-functions-and-slope.md)
- [Calculus for ML 101 (3/10): 편미분](./03-partial-derivatives.md)
- [Calculus for ML 101 (4/10): Gradient](./04-gradient.md)
- [Calculus for ML 101 (5/10): 연쇄 법칙](./05-chain-rule.md)
- [Calculus for ML 101 (6/10): 손실 함수](./06-loss-function.md)
- [Calculus for ML 101 (7/10): 경사하강법](./07-gradient-descent.md)
- [Calculus for ML 101 (8/10): 최적화](./08-optimization.md)
- [Calculus for ML 101 (9/10): 역전파 직관](./09-backpropagation-intuition.md)
- **딥러닝에서의 미분 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Deep Learning Book - Goodfellow et al.](https://www.deeplearningbook.org/)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [CS231n - Convolutional Neural Networks](https://cs231n.stanford.edu/)
- [Reproducibility - PyTorch](https://pytorch.org/docs/stable/notes/randomness.html)
- [Zeroing out gradients in PyTorch](https://pytorch.org/tutorials/recipes/recipes/zeroing_out_gradients.html)

### 예제 코드
- [book-examples/calculus-for-ml-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/calculus-for-ml-101/ko)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, DeepLearning, Capstone, Beginner

---
series: calculus-for-ml-101
episode: 9
title: "Calculus for ML 101 (9/10): 역전파 직관"
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
  - Backprop
  - NeuralNetwork
  - Beginner
seo_description: 역전파, 계산 그래프, 순전파, 역방향 gradient, autograd 직관을 ML 입문자 관점에서 정리한 글
last_reviewed: '2026-05-12'
---

# Calculus for ML 101 (9/10): 역전파 직관

지금까지 이 시리즈에서는 미분, 편미분, gradient, chain rule, 손실, optimizer를 차례로 보았습니다. 이제 남은 핵심 질문은 하나입니다. 수천 개, 수백만 개의 파라미터에 대한 gradient를 실제로 어떻게 한 번에 계산할까요? 모든 weight를 수치 미분으로 하나씩 검사하는 방식은 너무 느리고 비현실적입니다.

역전파는 이 문제에 대한 계산적 해법입니다. 계산 그래프를 따라 순전파에서 값을 만들고, 역방향으로 chain rule을 적용해 각 파라미터의 gradient를 효율적으로 누적합니다. 즉 역전파는 새로운 수학이 아니라, 이미 본 연쇄 법칙을 대규모 계산 그래프에 맞게 실행하는 절차입니다.

이 글은 Calculus for ML 101 시리즈의 아홉 번째 글입니다.

이 글에서는 계산 그래프, forward pass, backward pass, gradient accumulation, autograd 직관을 중심으로 설명하겠습니다. 목표는 프레임워크 내부 동작을 완전히 구현하는 것이 아니라, backward가 왜 한 번의 패스로 전체 gradient를 만들 수 있는지 이해하는 것입니다.

끝까지 읽고 나면 `zero_grad`, gradient accumulation, graph retention 같은 실무 용어가 더 이상 API 암기가 아니라 자연스러운 운영 개념으로 보이게 됩니다.


![Calculus for ML 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/09/09-01-concept-at-a-glance.ko.png)
*Calculus for ML 101 9장 흐름 개요*

## 먼저 던지는 질문

- 역전파는 수많은 weight의 gradient를 왜 한 번에 계산할 수 있을까요?
- 계산 그래프 관점에서 순전파와 역전파는 각각 무엇을 남길까요?
- local derivative를 저장한다는 말은 실제로 어떤 의미일까요?

## 왜 이 글이 중요한가

PyTorch, TensorFlow, JAX는 모두 gradient를 자동으로 계산해 줍니다. 그래서 역전파를 몰라도 모델은 학습됩니다. 하지만 학습이 이상하게 흔들리거나, gradient가 누적되거나, 메모리가 계속 늘어나거나, 특정 branch가 detach되어 학습이 끊기는 순간부터는 원리를 이해하는 사람이 문제를 더 빨리 좁힐 수 있습니다.

역전파를 이해하면 gradient를 “모델이 somehow 계산해 주는 값”으로 보지 않게 됩니다. 값은 순전파에서 만들어지고, backward에서는 각 연산의 local derivative와 위에서 내려온 gradient를 곱해 부모로 전달한다는 사실이 선명해집니다. 그러면 shared node에서 왜 gradient를 더해야 하는지, 왜 그래프를 보존하면 메모리를 더 쓰는지도 자연스럽게 설명됩니다.

또한 이 글은 시리즈의 마지막 글을 위한 직접적인 준비입니다. 딥러닝 학습 루프 전체를 보려면 forward, loss, backward, update가 하나의 닫힌 고리라는 점을 이해해야 하고, 역전파는 그중 backward 단계를 담당합니다.

## 핵심 관점

역전파를 가장 직관적으로 이해하는 방법은 계산 그래프를 생각하는 것입니다. 각 노드는 값을 계산하고, 자신의 부모 노드에 대한 local derivative를 알고 있습니다. 최종 출력에서 시작해 이 local derivative를 곱해 뒤로 전달하면 각 입력이 결과에 얼마나 기여했는지 계산할 수 있습니다.

이 구조에서는 순전파와 역전파의 역할이 명확히 나뉩니다. 순전파는 값을 만들고 캐시하며, 역전파는 그 값을 바탕으로 gradient를 전파합니다. 그래서 backward만 따로 존재할 수 없고, forward에서 저장한 정보가 반드시 필요합니다.

> 역전파는 chain rule을 뒤로 적용하는 절차이며, 계산 그래프의 각 노드가 자기 local derivative를 제공하기 때문에 전체 gradient를 효율적으로 누적할 수 있습니다.

## 핵심 개념

역전파의 전체 흐름은 아래처럼 볼 수 있습니다.

### 가장 작은 계산 그래프 노드부터 시작합니다

```python
class Node:
    def __init__(self, val, parents=()):
        self.val = val
        self.parents = parents
        self.grad = 0.0
```

노드는 현재 값과 부모 노드들, 그리고 역전파 과정에서 채워질 gradient 저장 공간을 가집니다. 실제 프레임워크는 훨씬 복잡하지만, 핵심은 각 연산 결과가 자신의 계산 이력을 알고 있다는 점입니다.

### 덧셈 노드는 local derivative가 단순합니다

```python
def add(a, b):
    n = Node(a.val + b.val, (a, b))
    n.local = (1.0, 1.0)
    return n
```

덧셈의 경우 출력이 각 입력에 대해 갖는 local derivative는 1입니다. 중요한 것은 노드가 forward에서 결과값만 만드는 것이 아니라, backward 때 쓸 local derivative도 함께 기록한다는 점입니다.

### 곱셈 노드는 상대편 값을 local derivative로 가집니다

```python
def mul(a, b):
    n = Node(a.val * b.val, (a, b))
    n.local = (b.val, a.val)
    return n
```

곱셈에서는 각 입력에 대한 local derivative가 상대편 값이 됩니다. 이 예제는 왜 forward에서 중간값을 캐시해야 하는지 잘 보여 줍니다. backward 때 local derivative를 계산하려면 forward에서의 값이 필요하기 때문입니다.

### backward는 출력에서 입력 방향으로 gradient를 누적합니다

```python
def backward(n):
    n.grad = 1.0
    stack = [n]
    while stack:
        x = stack.pop()
        for p, lg in zip(x.parents, x.local):
            p.grad += x.grad * lg
            stack.append(p)
```

출력 노드의 gradient를 1로 두는 이유는 자기 자신을 자기 자신으로 미분한 값이 1이기 때문입니다. 그다음 각 부모 노드로 `현재 gradient × local derivative`를 누적하며 전달합니다. shared node라면 여러 경로에서 gradient가 합쳐질 수 있으므로 `+=`가 중요합니다.

### 작은 예제 하나로 전체 흐름을 볼 수 있습니다

```python
a, b, c = Node(2.0), Node(3.0), Node(4.0)
y = mul(add(a, b), c)
backward(y)
# a.grad == 4.0, b.grad == 4.0, c.grad == 5.0
```

순전파에서 `add(a, b)`가 먼저 계산되고, 그 결과가 `c`와 곱해집니다. 역전파에서는 출력에서 시작해 곱셈 노드의 local derivative를 적용하고, 다시 덧셈 노드의 local derivative를 따라 `a`, `b`, `c` 각각의 gradient를 얻습니다. 작은 예제지만 연쇄 법칙과 gradient accumulation의 핵심이 모두 들어 있습니다.

### shared node를 보면 gradient accumulation이 왜 필요한지 더 분명해집니다

```python
a = Node(2.0)
b = add(a, a)
y = mul(b, a)
backward(y)

# y = (a + a) * a = 2a^2
# dy/da = 4a, so at a=2 the gradient is 8
print(a.grad)
```

**Expected output:** `8.0`

이 예제는 하나의 노드가 그래프에서 여러 번 재사용될 수 있다는 사실을 보여 줍니다. `a`는 `add(a, a)` 안에서 두 번 등장하고, 그 결과가 다시 `a`와 곱해집니다. 그래서 backward에서는 한 경로의 미분만 저장하면 안 되고, 여러 경로에서 내려온 기여도를 모두 더해야 합니다. 프레임워크에서 gradient가 누적되는 기본 동작도 바로 이 구조와 연결됩니다.

### autograd를 이해할 때 기억할 점

프레임워크는 이 과정을 자동으로 해 줍니다. 하지만 `zero_grad`를 호출하지 않으면 gradient가 누적되고, 필요 없는 그래프를 유지하면 메모리가 늘어나며, detach를 잘못 쓰면 학습 경로가 끊깁니다. 즉 autograd를 안다는 것은 내부 수학을 아는 것뿐 아니라, 그래프 수명과 gradient 버퍼를 운영 관점에서 이해하는 것이기도 합니다.

```python
optimizer.zero_grad()
pred = model(x)
loss = criterion(pred, y)
loss.backward()
optimizer.step()
```

이 순서를 지키는 이유는 backward가 보통 gradient를 덮어쓰지 않고 누적하기 때문입니다. 따라서 이전 step의 흔적을 지우지 않으면 현재 batch의 신호만 반영되는 것이 아니라 과거 gradient까지 섞여 들어갑니다. 작은 실습 코드에서는 티가 덜 나도, 실제 학습에서는 loss curve 해석과 디버깅을 어렵게 만드는 흔한 원인입니다.

## 흔히 헷갈리는 지점

- gradient는 자동으로 덮어써진다고 생각하기 쉽지만, 많은 프레임워크에서 기본 동작은 누적입니다.
- backward 전에 forward에서 필요한 값이 저장되지 않으면 local derivative 계산이 불가능합니다.
- shared node에서는 여러 경로의 gradient를 더해야 한다는 점을 놓치기 쉽습니다.
- 그래프를 불필요하게 유지하면 메모리 사용량이 빠르게 커질 수 있습니다.
- detach나 no-grad 문맥을 잘못 쓰면 gradient가 전혀 흐르지 않는 branch가 생길 수 있습니다.

## 운영 체크리스트

- [ ] 학습 스텝마다 `zero_grad` 위치를 명확히 관리한다
- [ ] forward에서 어떤 값이 backward에 필요한지 이해한다
- [ ] shared node에서 gradient accumulation이 일어난다는 점을 염두에 둔다
- [ ] 메모리 문제를 볼 때 graph retention과 detach 사용을 함께 점검한다
- [ ] 작은 예제에서는 numerical check로 autograd 결과를 검증해 본다

## 정리

역전파는 chain rule을 계산 그래프 위에서 뒤로 실행하는 절차입니다. 순전파가 값과 중간 상태를 만들면, 역전파는 각 노드의 local derivative를 사용해 출력의 gradient를 입력 쪽으로 전파합니다. 이 구조 덕분에 모델 전체 gradient를 한 번의 backward pass로 효율적으로 계산할 수 있습니다.

실무적으로 중요한 포인트는 gradient accumulation과 그래프 수명입니다. `zero_grad`, detach, cached activations, 메모리 사용량은 모두 역전파 구조에서 직접 나온 운영 주제입니다. 프레임워크가 자동으로 해 주는 일이 많아도, 원리를 알면 버그를 훨씬 더 빠르게 좁힐 수 있습니다.

다음 글에서는 이 시리즈 전체를 하나의 학습 루프로 묶겠습니다. forward, loss, backward, optimizer step이 어떻게 하나의 사이클을 이루는지, 그리고 왜 이것이 딥러닝 학습의 표준 골격인지 정리하겠습니다.


## 순전파와 역전파를 한 줄씩 추적하기

역전파를 직관적으로 이해하려면 같은 샘플에 대해 forward와 backward를 나란히 적는 것이 가장 빠릅니다. 예제로 2층 완전연결 네트워크를 사용하겠습니다.

\[
x \in \mathbb{R}^2, \quad h = ReLU(W_1x+b_1), \quad \hat{y}=W_2h+b_2, \quad L=rac{1}{2}(\hat{y}-y)^2
\]

### 순전파 추적 표

| 단계 | 식 | 출력 차원 | 캐시해야 할 값 |
| --- | --- | --- | --- |
| 1 | `z1 = W1x + b1` | `(2,)` | `x`, `W1`, `z1` |
| 2 | `h = ReLU(z1)` | `(2,)` | `z1`, `h` |
| 3 | `y_hat = W2h + b2` | `(1,)` | `h`, `W2`, `y_hat` |
| 4 | `L = 0.5*(y_hat-y)^2` | 스칼라 | `y_hat`, `y` |

순전파에서 저장한 캐시는 역전파에서 local gradient를 계산할 때 그대로 쓰입니다. 이 연결이 끊기면 backward를 계산할 수 없습니다.

### 역전파 추적 표

| 단계 | 전달 식 | 의미 |
| --- | --- | --- |
| 1 | `dL/dy_hat = y_hat - y` | 손실의 시작 gradient |
| 2 | `dL/dW2 = (dL/dy_hat) * h^T` | 출력층 가중치 기울기 |
| 3 | `dL/db2 = dL/dy_hat` | 출력층 편향 기울기 |
| 4 | `dL/dh = W2^T * dL/dy_hat` | 은닉표현으로 신호 전파 |
| 5 | `dL/dz1 = dL/dh * ReLU'(z1)` | 활성함수 local gradient 적용 |
| 6 | `dL/dW1 = (dL/dz1) * x^T` | 입력층 가중치 기울기 |
| 7 | `dL/db1 = dL/dz1` | 입력층 편향 기울기 |

## 계산 그래프 예제로 보는 체인 룰

다음 식을 계산 그래프로 두면 역전파가 더 선명해집니다.

\[
q = a\cdot b, \quad r=q+c, \quad y=r^2
\]

```python
def forward(a, b, c):
    q = a * b
    r = q + c
    y = r ** 2
    cache = (a, b, c, q, r)
    return y, cache

def backward(dy, cache):
    a, b, c, q, r = cache
    dr = dy * (2 * r)
    dq = dr * 1
    dc = dr * 1
    da = dq * b
    db = dq * a
    return da, db, dc
```

`dy`를 1로 두면 `y`에 대한 미분이 됩니다. 각 노드는 "자신의 local gradient"만 알면 되고, 상위에서 내려온 gradient를 곱해 부모로 전달합니다. 이것이 연쇄 법칙의 구현 관점입니다.

## Local gradient와 chain rule을 손계산으로 맞춰보기

`a=2, b=3, c=4`일 때:

- `q=6`
- `r=10`
- `y=100`
- `dy/dr = 2r = 20`
- `dr/dq = 1`, `dr/dc = 1`
- `dq/da = b = 3`, `dq/db = a = 2`

따라서,

- `dy/da = 20 * 1 * 3 = 60`
- `dy/db = 20 * 1 * 2 = 40`
- `dy/dc = 20`

수치 미분으로 검증하면 같은 값이 나옵니다. 이 연습을 반복하면 backward 로그를 볼 때 값의 규모가 직관적으로 읽히기 시작합니다.

## 2층 신경망 완전 계산 예제

아래는 스칼라 출력을 갖는 2층 네트워크를 수치까지 넣어 계산한 예제입니다.

- 입력: `x=[1.0, -2.0]`
- 정답: `y=1.0`
- `W1=[[0.2, -0.4], [0.7, 0.1]]`, `b1=[0.0, 0.0]`
- `W2=[0.6, -0.3]`, `b2=0.1`

### 순전파

1. `z1 = W1x+b1 = [1.0, 0.5]`
2. `h = ReLU(z1) = [1.0, 0.5]`
3. `y_hat = W2h+b2 = 0.6*1 + (-0.3)*0.5 + 0.1 = 0.55`
4. `L = 0.5*(0.55-1)^2 = 0.10125`

### 역전파

1. `dL/dy_hat = 0.55-1 = -0.45`
2. `dL/dW2 = -0.45 * [1.0, 0.5] = [-0.45, -0.225]`
3. `dL/db2 = -0.45`
4. `dL/dh = W2 * (-0.45) = [-0.27, 0.135]`
5. `ReLU'(z1)=[1,1]`이므로 `dL/dz1=[-0.27, 0.135]`
6. `dL/dW1 = dL/dz1 outer x`
   - 첫 행: `-0.27 * [1, -2] = [-0.27, 0.54]`
   - 둘째 행: `0.135 * [1, -2] = [0.135, -0.27]`
7. `dL/db1 = [-0.27, 0.135]`

이 정도를 손으로 따라가 보면 autograd 출력이 왜 그런 모양인지 바로 해석할 수 있습니다.

## Gradient accumulation의 동작과 사용 시점

기본적으로 많은 프레임워크는 `.grad`를 덮어쓰지 않고 누적합니다. 그래서 아래 두 코드는 의미가 다릅니다.

```python
# 케이스 A: 매 step 초기화
for x, y in loader:
    optimizer.zero_grad()
    loss = model.loss(x, y)
    loss.backward()
    optimizer.step()
```

```python
# 케이스 B: 4 step 누적 후 업데이트
acc_steps = 4
optimizer.zero_grad()
for i, (x, y) in enumerate(loader):
    loss = model.loss(x, y) / acc_steps
    loss.backward()
    if (i + 1) % acc_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

케이스 B는 메모리 제약으로 큰 effective batch를 흉내 낼 때 유용합니다. 단, loss를 `acc_steps`로 나누지 않으면 gradient 규모가 커져 학습률 재해석이 필요합니다.

## 소실/폭주 gradient 진단

깊은 네트워크에서는 gradient가 층을 거치며 반복 곱셈을 하므로 크기 문제가 발생합니다.

### 진단 체크 포인트

| 증상 | 로그에서 보이는 신호 | 우선 대응 |
| --- | --- | --- |
| 소실 gradient | 초기층 grad norm이 `1e-8` 이하 | 초기화 점검, residual 구조, norm layer |
| 폭주 gradient | grad norm 급증, loss NaN | clipping, lr 감소, warmup |
| 특정 층만 불안정 | 층별 grad 분산 편차 큼 | 층별 lr/정규화/활성함수 점검 |

### grad norm 로깅 예제

```python
import torch

def grad_norm(model):
    total = 0.0
    for p in model.parameters():
        if p.grad is None:
            continue
        total += p.grad.detach().pow(2).sum().item()
    return total ** 0.5

# 학습 루프 내부
loss.backward()
print('grad_norm=', grad_norm(model))
```

### 폭주 방지용 clipping

```python
import torch

torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
optimizer.step()
```

clipping은 문제를 "근본 해결"하지는 않지만, 발산을 막아 실험을 계속 진행할 수 있게 해 주는 안전 장치입니다.

## 역전파 디버깅 실전 순서

1. **단일 배치 overfit 테스트**: 배치 1개에서 loss가 거의 0까지 떨어지는지 확인합니다.
2. **수치 미분 spot-check**: 파라미터 몇 개를 골라 finite difference와 비교합니다.
3. **층별 grad norm 추적**: 소실/폭주 위치를 층 단위로 찾습니다.
4. **detach/no_grad 점검**: 그래프가 끊긴 branch가 없는지 확인합니다.
5. **accumulation 정책 확인**: `zero_grad` 위치와 loss scaling을 검증합니다.


## 미니배치 역전파: 샘플 축에서의 합산

손계산 예제는 단일 샘플을 쓰지만, 실제 학습은 미니배치 평균 손실을 사용합니다.

\[
L = rac{1}{B}\sum_{i=1}^{B} L_i
\]

따라서 파라미터 gradient도 샘플별 gradient 평균이 됩니다.

\[

abla_	heta L = rac{1}{B}\sum_{i=1}^{B} 
abla_	heta L_i
\]

이 식을 이해하면 `reduction='sum'`과 `reduction='mean'` 차이가 왜 학습률 해석을 바꾸는지 바로 연결됩니다.

### reduction 설정 비교

| 설정 | gradient 규모 | 실무 해석 |
| --- | --- | --- |
| `mean` | 배치 크기에 덜 민감 | 기본값으로 안전 |
| `sum` | 배치 크기에 비례해 커짐 | lr 재조정 필요 |

## 역전파와 메모리 사용량

역전파를 위해 forward 중간값을 저장하므로, 활성값 텐서가 메모리의 큰 비중을 차지합니다.

### 메모리 절약 전략

1. **gradient checkpointing**: 일부 중간값을 저장하지 않고 backward 시 재계산합니다.
2. **mixed precision**: 활성값과 gradient의 저장 정밀도를 낮춰 메모리 사용을 줄입니다.
3. **micro-batch accumulation**: 배치를 쪼개고 gradient를 누적해 peak memory를 낮춥니다.

```python
# PyTorch gradient checkpointing 개념 예시
from torch.utils.checkpoint import checkpoint

def forward(self, x):
    x = checkpoint(self.block1, x)
    x = checkpoint(self.block2, x)
    return self.head(x)
```

재계산 비용이 추가되므로, 메모리와 속도 사이의 교환관계를 실험으로 확인해야 합니다.

## 역전파 오류 유형별 디버깅 표

| 오류 메시지/현상 | 원인 후보 | 확인 항목 |
| --- | --- | --- |
| `element 0 does not require grad` | detach/no_grad 오사용 | 텐서 `requires_grad` 체인 |
| `Trying to backward through the graph a second time` | 그래프 재사용 | `retain_graph=True` 필요성 검토 |
| grad가 항상 0 | 활성함수 포화, dead ReLU | 입력 분포, 초기화, lr |
| 특정 레이어 grad None | 경로 단절 | 모듈 연결, branch merge |

## 층별 로컬 미분 감각 기르기

아래 미분은 자주 반복되므로 암기가 아니라 "기울기 감각"으로 익혀 두는 것이 좋습니다.

| 연산 | local gradient |
| --- | --- |
| `y = x + c` | `dy/dx = 1` |
| `y = cx` | `dy/dx = c` |
| `y = x^2` | `dy/dx = 2x` |
| `y = ReLU(x)` | `dy/dx = 1(x>0)` |
| `y = sigmoid(x)` | `dy/dx = y(1-y)` |

이 표를 기준으로 backward 로그를 보면, 어느 지점에서 gradient가 줄거나 커지는지 원인을 더 빠르게 추적할 수 있습니다.


## 역전파 검증: 수치 미분 체크 자동화

역전파 구현을 직접 다루는 경우, 작은 텐서에서 수치 미분 검증을 자동화해 두면 회귀 버그를 크게 줄일 수 있습니다.

```python
import numpy as np

def numerical_grad(f, x, h=1e-5):
    grad = np.zeros_like(x)
    it = np.nditer(x, flags=['multi_index'], op_flags=['readwrite'])
    while not it.finished:
        idx = it.multi_index
        old = x[idx]
        x[idx] = old + h
        fx1 = f(x)
        x[idx] = old - h
        fx2 = f(x)
        x[idx] = old
        grad[idx] = (fx1 - fx2) / (2 * h)
        it.iternext()
    return grad
```

검증 시에는 상대 오차를 같이 계산합니다.

\[
	ext{rel\_err} = rac{|g_{analytic}-g_{numeric}|}{\max(1,|g_{analytic}|,|g_{numeric}|)}
\]

실무 기준으로는 `1e-4` 이하를 통과선으로 두고, 그보다 큰 경우 연산 순서/브로드캐스트/축 감소(`sum`, `mean`)를 우선 확인합니다.

## 대규모 학습에서의 accumulation 운영 규칙

- accumulation step을 늘리면 effective batch는 커지지만, optimizer step 빈도는 줄어듭니다.
- step 기반 scheduler는 "optimizer step 기준"으로 설계해야 warmup 길이가 의도대로 동작합니다.
- gradient clipping은 누적 완료 후, step 직전에 수행해야 의미가 일관됩니다.

이 규칙을 문서화하지 않으면 동일 코드라도 팀원마다 다른 해석으로 실험해 결과 비교가 어려워집니다.


### 역전파 이해를 고정하는 최소 연습 루틴

하루 학습 루틴으로는 "단일 스칼라 그래프 손계산 1개 + 2층 네트워크 로그 확인 1개" 조합이 가장 효율적입니다. 손계산으로 chain rule 경로를 확인하고, 코드 로그로 grad norm과 누적 동작을 확인하면 이론과 구현이 분리되지 않습니다. 이 루틴을 반복하면 새로운 아키텍처를 보더라도 backward 경로를 먼저 떠올리는 습관이 생깁니다.

## 처음 질문으로 돌아가기

- **역전파는 수많은 weight의 gradient를 왜 한 번에 계산할 수 있을까요?**
  - 계산 그래프의 각 노드가 자신의 local gradient를 제공하고, 출력에서 입력으로 gradient를 전달할 때 연쇄 법칙을 경로별로 곱한 뒤 같은 파라미터에서 합산하기 때문입니다. 그래서 파라미터마다 별도 수치 미분을 돌리지 않아도 한 번의 backward로 전체 기울기를 얻습니다.
- **계산 그래프 관점에서 순전파와 역전파는 각각 무엇을 남길까요?**
  - 순전파는 예측값뿐 아니라 backward에 필요한 중간값(`z`, 활성값, branch 결과)을 캐시합니다. 역전파는 그 캐시를 사용해 `dL/dnode`를 계산하고 부모 노드로 전파하며, 최종적으로 각 파라미터의 `.grad` 버퍼를 채웁니다.
- **local derivative를 저장한다는 말은 실제로 어떤 의미일까요?**
  - 각 연산 노드가 "출력을 입력으로 미분한 값"을 보관한다는 뜻입니다. 예를 들어 곱셈은 상대편 값을, ReLU는 입력 부호에 따른 0/1 마스크를 local gradient로 사용합니다. backward는 상위 gradient에 이 local 값을 곱해 체인 룰을 구현합니다.

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
- **역전파 직관 (현재 글)**
- 딥러닝에서의 미분 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Backpropagation - CS231n](https://cs231n.github.io/optimization-2/)
- [Calculus on Computational Graphs - Olah](https://colah.github.io/posts/2015-08-Backprop/)
- [PyTorch Autograd](https://pytorch.org/tutorials/beginner/blitz/autograd_tutorial.html)
- [JAX Autograd Cookbook](https://jax.readthedocs.io/en/latest/notebooks/autodiff_cookbook.html)
- [Zeroing out gradients in PyTorch](https://pytorch.org/tutorials/recipes/recipes/zeroing_out_gradients.html)

### 예제 코드
- [book-examples/calculus-for-ml-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/calculus-for-ml-101/ko)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, Backprop, NeuralNetwork, Beginner

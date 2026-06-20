---
series: linear-algebra-101
episode: 10
title: "Linear Algebra 101 (10/10): 머신러닝에서의 선형대수"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - LinearAlgebra
  - MachineLearning
  - DeepLearning
  - DataScience
  - Beginner
seo_description: 선형대수가 회귀, 신경망, 임베딩, 최적화 과정에서 어떻게 뼈대 역할을 하는지 종합적으로 정리하며 시리즈를 마무리합니다.
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (10/10): 머신러닝에서의 선형대수

시리즈를 여기까지 따라왔다면 이제 남은 질문은 하나입니다. 그래서 이 선형대수가 실제 머신러닝 안에서 어디에 나타나는가 하는 질문입니다. 답은 생각보다 단순합니다. 거의 모든 곳입니다. 데이터 표현, 모델 정의, 손실 계산, 최적화 과정이 모두 벡터와 행렬 위에서 돌아갑니다.

이 글은 Linear Algebra 101 시리즈의 마지막 글입니다.

여기서는 선형회귀, 신경망, 임베딩, 그래디언트, PCA를 한 흐름으로 묶어 시리즈를 마무리하겠습니다.

![Linear Algebra 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/10/10-01-concept-at-a-glance.ko.png)
*Linear Algebra 101 10장 흐름 개요*
> 선형대수는 머신러닝 언어의 기초입니다. 회귀·분류·차원 축소가 모두 벡터와 행렬 연산으로 표현됩니다.

## 이 글에서 다룰 문제

- 머신러닝 파이프라인의 어디에서 벡터와 행렬이 등장할까요?
- 선형회귀와 신경망은 선형대수 관점에서 어떻게 읽을 수 있을까요?
- 임베딩 유사도와 그래디언트 계산은 왜 선형대수 문제일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

선형대수 감각이 약하면 모델이 블랙박스로 남습니다. 입력 형상이 왜 안 맞는지, 임베딩 유사도가 왜 이상한지, 그래디언트가 왜 저렇게 생겼는지, PCA가 왜 저 방향을 선택했는지 설명하기 어려워집니다.

반대로 선형대수 관점이 잡히면 모델의 안쪽이 훨씬 덜 신비로워집니다. 레이어는 행렬 곱과 비선형 활성화의 조합이고, 임베딩 검색은 벡터 비교이며, 최적화는 파라미터 벡터를 업데이트하는 반복 과정이라는 점이 보입니다. 이 감각은 프레임워크를 바꿔도 남습니다.

- 설계 행렬 `X`: 행은 샘플, 열은 피처를 뜻합니다.
- 가중치 `W`: 선형변환의 학습 가능한 파라미터입니다.
- 임베딩: 고차원 대상을 벡터로 표현한 결과입니다.
- 그래디언트: 손실을 파라미터에 대해 미분한 값입니다.
- 배치 행렬 곱: 여러 입력을 한 번에 처리하는 계산 패턴입니다.

## 읽기 전과 후

읽기 전에는 머신러닝이 모델별 기법 모음처럼 보일 수 있습니다. 선형회귀, MLP, 임베딩 검색, 차원 축소가 서로 다른 세계처럼 느껴집니다.

읽은 후에는 이들이 모두 벡터와 행렬의 조합이라는 공통 뼈대를 공유한다는 점이 보입니다. 즉 알고리즘은 달라도 문법은 크게 다르지 않습니다.

## 머신러닝 알고리즘과 선형대수 연산 대응표

| ML 알고리즘 | 핵심 선형대수 연산 | 핵심 함수 |
| --- | --- | --- |
| 선형회귀 | `X @ w`, 최소제곱 정규방정식 | `np.linalg.lstsq` |
| 로지스틱 회귀 | `X @ w`, 시그모이드, `X.T @ err` | `scipy.special.expit` |
| SVM | 커널 행렬 `K`, 쌍대 문제 QP | `K = X @ X.T` |
| 신경망 | `X @ W`, ReLU, 역전파 체인룰 | 행렬 곱 + 비선형 |
| 임베딩 검색 | 정규화 후 내적/코사인 유사도 | `emb_n @ emb_n.T` |
| 추천 시스템(MF) | 저랭크 근사 `U @ V.T` | SVD, ALS |
| PCA | 공분산 고유분해 또는 SVD | `np.linalg.svd` |

## 다섯 단계로 연결해 보기

### 1단계 — 선형회귀

```python
import numpy as np
rng = np.random.default_rng(0)
X = rng.normal(size=(100, 3))
y = X @ np.array([1.0, -2.0, 0.5]) + rng.normal(scale=0.1, size=100)
w_hat, *_ = np.linalg.lstsq(X, y, rcond=None)
print("w_hat:", w_hat)
print("residual:", np.linalg.norm(X @ w_hat - y))
```

선형회귀는 가장 직관적인 출발점입니다. 입력 행렬 `X`와 가중치 벡터가 곱해져 예측을 만들고, 최소제곱 해법으로 적절한 가중치를 찾습니다.

### 2단계 — 신경망 한 레이어

```python
W1 = rng.normal(size=(3, 4))
b1 = np.zeros(4)
h = np.maximum(0, X @ W1 + b1)  # ReLU
print("hidden shape:", h.shape)  # (100, 4)
```

신경망도 구조는 비슷합니다. 입력 행렬과 가중치 행렬을 곱하고 편향을 더한 뒤 비선형 함수를 통과시킵니다. 선형대수 위에 비선형이 얹힌 형태입니다.

### 3단계 — 임베딩 유사도

```python
emb = rng.normal(size=(5, 8))
norms = np.linalg.norm(emb, axis=1, keepdims=True)
emb_n = emb / norms
sim = emb_n @ emb_n.T
print("sim matrix shape:", sim.shape)  # (5, 5)
print("diagonal (self-sim):", sim.diagonal())  # 모두 1.0
```

임베딩 검색은 벡터 비교 문제입니다. 정규화 후 내적을 쓰면 코사인 유사도 행렬이 만들어집니다.

### 4단계 — 그래디언트 한 스텝

```python
def loss_and_grad(w, X, y):
    pred = X @ w
    err = pred - y
    loss = (err ** 2).mean()
    grad = 2 * X.T @ err / len(y)
    return loss, grad

w = np.zeros(3)
for step in range(50):
    L, g = loss_and_grad(w, X, y)
    w -= 0.05 * g
print("learned w:", w)
print("true w:   [1.0, -2.0, 0.5]")
```

학습은 결국 파라미터 벡터를 조금씩 업데이트하는 반복입니다. 그래디언트 형상과 전치 위치가 왜 중요한지 여기서 바로 드러납니다.

### 5단계 — PCA로 피처 압축

```python
Xc = X - X.mean(axis=0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
X_2d = Xc @ Vt[:2].T
print("original shape:", X.shape)
print("compressed:", X_2d.shape)  # (100, 2)
print("explained:", (S**2 / (S**2).sum())[:2].round(3))
```

앞에서 배운 PCA는 데이터 자체를 더 잘 읽기 위한 선형대수 도구입니다. 모델을 학습하기 전, 데이터 구조를 압축하고 탐색하는 데 자주 쓰입니다.

## 작은 수치 예시로 다시 보기

- `np.linalg.lstsq`가 찾은 가중치는 대체로 `[1, -2, 0.5]` 근처로 수렴합니다. 생성한 데이터의 숨은 규칙을 다시 찾아낸 셈입니다.
- 은닉층 출력 형상은 `(100, 4)`, 임베딩 유사도 행렬 형상은 `(5, 5)`가 됩니다. 형상만 봐도 어떤 연산이 일어났는지 읽을 수 있습니다.
- 경사하강법으로 학습한 `w`도 최소제곱 해와 비슷한 방향으로 움직입니다. 해석과 학습이 같은 선형대수 위에 있다는 뜻입니다.

## NumPy로 역전파 한 번 계산하기

신경망의 역전파는 복잡해 보이지만, 행렬 미분 체인룰을 따라가면 명확한 선형대수 연산입니다.

```python
import numpy as np

rng = np.random.default_rng(123)
X = rng.normal(size=(4, 3))  # 4 샘플, 3 피처
y = np.array([0, 1, 0, 1])

# 파라미터 초기화
W1 = rng.normal(scale=0.1, size=(3, 2))
b1 = np.zeros(2)
W2 = rng.normal(scale=0.1, size=(2, 1))
b2 = np.zeros(1)

# 순전파
z1 = X @ W1 + b1
a1 = np.maximum(0, z1)   # ReLU
z2 = a1 @ W2 + b2
a2 = 1 / (1 + np.exp(-z2))  # Sigmoid

# 손실 (binary cross-entropy)
eps = 1e-8
loss = -np.mean(y.reshape(-1, 1) * np.log(a2 + eps)
                + (1 - y.reshape(-1, 1)) * np.log(1 - a2 + eps))

# 역전파
da2 = (a2 - y.reshape(-1, 1)) / len(y)
dW2 = a1.T @ da2       # (2, 1)
db2 = da2.sum(axis=0)  # (1,)

da1 = da2 @ W2.T       # (4, 2)
dz1 = da1 * (z1 > 0)  # ReLU 도함수
dW1 = X.T @ dz1        # (3, 2)
db1 = dz1.sum(axis=0)  # (2,)

print('loss:', round(float(loss), 4))
print('dW1 shape:', dW1.shape, 'dW2 shape:', dW2.shape)
```

여기서 핵심은 `X.T @ dz1`, `a1.T @ da2` 같은 행렬 곱 패턴입니다. 전치와 곱 순서만 맞으면 그래디언트 형상이 파라미터 형상과 일치합니다. 이 패턴을 이해하면 PyTorch나 TensorFlow의 자동미분 결과도 직접 검증할 수 있습니다.

## 머신러닝 파이프라인을 선형대수 체크리스트로 읽기

아래 코드는 데이터 행렬, 선형모델, 임베딩 유사도, PCA 압축을 한 흐름으로 묶습니다.

```python
import numpy as np

rng = np.random.default_rng(7)
X = rng.normal(size=(300, 6))
w_true = np.array([1.2, -0.8, 0.5, 0.0, 0.3, -0.2])
y = X @ w_true + 0.05 * rng.normal(size=300)

# 1) 회귀 가중치
w_hat, *_ = np.linalg.lstsq(X, y, rcond=None)
print('w_hat:', w_hat.round(3))
print('w_true:', w_true)

# 2) 임베딩 유사도 (샘플 10개)
E = X[:10]
E = E / np.linalg.norm(E, axis=1, keepdims=True)
S = E @ E.T
print('similarity matrix shape:', S.shape)
print('sim range: [{:.2f}, {:.2f}]'.format(S.min(), S.max()))

# 3) PCA 압축
Xc = X - X.mean(axis=0)
U, sv, Vt = np.linalg.svd(Xc, full_matrices=False)
X3 = Xc @ Vt[:3].T
ratio = (sv**2 / (sv**2).sum())[:3]
print('compressed shape:', X3.shape, '  explained:', ratio.round(3))
```

이 짧은 코드 안에 시리즈 핵심이 모두 들어 있습니다. `X @ w`는 선형변환, 유사도 행렬은 내적, `svd`는 분해와 차원 축소입니다.

## 실무 판단표: 어디서 선형대수를 먼저 점검할까

| 단계 | 흔한 문제 | 선형대수 점검 포인트 |
| --- | --- | --- |
| 데이터 준비 | 피처 중복/스케일 불균형 | 랭크, 표준화, 상관 구조 |
| 모델 학습 | 발산/느린 수렴 | 조건수, 학습률, 그래디언트 크기 |
| 임베딩 검색 | 유사도 품질 저하 | 정규화 여부, 코사인/L2 선택 |
| 압축/시각화 | 정보 손실 과다 | 누적 설명률, 재구성 오차 |
| 역전파 디버깅 | 형상 불일치, 그래디언트 폭발 | 전치 위치, 배치 축 평균 |

## GPU와 행렬 연산: 병렬화 원리

딥러닝이 빠른 이유 중 하나는 GPU가 행렬 곱을 병렬로 처리하기 때문입니다. 행렬 곱 `C = A @ B`는 각 `C[i, j]`를 독립적으로 계산할 수 있으므로 병렬화에 이상적입니다.

```python
import numpy as np
import time

# CPU에서 큰 행렬 곱 성능 측정
A = np.random.randn(1000, 1000)
B = np.random.randn(1000, 1000)

t0 = time.time()
C = A @ B
elapsed = time.time() - t0
print(f'1000x1000 행렬 곱: {elapsed*1000:.1f} ms')
print(f'연산 수: ~{2 * 1000**3 / 1e9:.0f} GFLOP')
```

실무에서 GPU 가속을 최대한 활용하려면 배치 크기를 크게 잡고, 행렬 형상을 32의 배수로 맞추며, 불필요한 CPU↔GPU 전송을 최소화합니다. Transformer는 행렬 곱으로 attention을 계산해 GPU 효율이 높고, RNN은 순차 의존성 때문에 병렬화가 어렵습니다.

## 이 코드에서 먼저 볼 점

- 모든 레이어는 행렬 곱과 비선형의 조합입니다.
- 임베딩 비교는 내적과 정규화 문제입니다.
- 그래디언트는 벡터와 행렬에 대한 미분 결과이며, 형상이 파라미터와 일치해야 합니다.
- 데이터 압축도 SVD와 PCA 같은 선형대수 도구로 이뤄집니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 형상 불일치 무시 | 런타임 오류 또는 의도치 않은 브로드캐스팅 | 모든 중간 텐서 형상 로그로 확인 |
| 정규화/표준화 누락 | 임베딩 유사도 왜곡, 학습 발산 | 코사인 유사도 전 반드시 L2 정규화 |
| `@` 대신 `*`(원소곱) 혼용 | 형상 맞아도 의미 다른 결과 | 행렬 곱은 `@`, 원소곱은 `*` 명확히 구분 |
| 역전파 전치 오류 | 그래디언트 형상 불일치 오류 | `dW = X.T @ dout` 패턴 공식처럼 기억 |
| `inv` 직접 사용 | 조건수 큰 행렬에서 수치 불안정 | `solve`, `lstsq`, 분해 기반 접근 우선 |

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 모델을 볼 때 먼저 형상과 변환을 읽습니다. 입력 행렬이 어떤 의미인지, 가중치가 어떤 차원을 잇는지, 그래디언트가 어느 방향으로 흐르는지 확인합니다. 이 습관이 있으면 프레임워크 에러 메시지도 훨씬 빨리 해석할 수 있습니다.

또한 임베딩 공간에서는 유사도 메트릭을, 회귀나 분류에서는 수치 안정성과 정규화를, 고차원 데이터에서는 PCA나 SVD를 함께 떠올립니다. 선형대수는 별도 과목이 아니라 머신러닝 전반의 공용 인터페이스입니다.

## 실전 확장 노트: 학습 루프를 선형대수 관점으로 점검하기

머신러닝 실험이 흔들릴 때는 모델 종류보다 연산 흐름을 먼저 점검하는 편이 빠릅니다. 아래 루틴은 입력 형상, 가중치 형상, 그래디언트 형상, 조건수, 수렴 속도를 한 번에 점검합니다.

```python
import numpy as np

rng = np.random.default_rng(7)
X = rng.normal(size=(64, 16))
W = rng.normal(scale=0.1, size=(16, 8))
y = rng.normal(size=(64, 8))

# 1) 형상 점검
print('X:', X.shape, 'W:', W.shape, 'y:', y.shape)

# 2) 조건수 점검
cond = np.linalg.cond(X)
print('cond(X):', cond)
if cond > 1e6:
    print('경고: 조건수 불량 — 학습 불안정 가능')

# 3) 학습 루프
lr = 0.05
losses = []
for step in range(30):
    pred = X @ W
    err = pred - y
    loss = float((err**2).mean())
    losses.append(loss)
    grad = (X.T @ err) / len(X)
    W -= lr * grad

print('pred shape:', pred.shape, 'grad shape:', grad.shape)
print('initial loss:', round(losses[0], 4))
print('final loss:', round(losses[-1], 4))
print('수렴:', losses[-1] < losses[0])

# 4) SVD로 데이터 구조 확인
U, S, Vt = np.linalg.svd(X, full_matrices=False)
print('singular values (top 4):', S[:4].round(2))
print('effective rank estimate:', (S > S[0] * 0.01).sum())
```

반드시 확인할 항목은 네 가지입니다.

1. **형상 일관성**: `pred`, `grad`, `W`의 형상이 설계와 일치하는지 매 단계 확인합니다.
2. **조건수**: `cond(X)`가 크면 학습률을 낮추거나 정규화를 추가해야 합니다.
3. **특이값 스펙트럼**: 급격히 작아지는 특이값은 사실상 불필요한 차원을 암시합니다.
4. **손실 단조 감소**: 발산하면 학습률, 초기화, 정규화 순으로 점검합니다.

## 시리즈를 실전에 연결하는 권장 루틴

1. 모든 모델 코드에서 텐서 형상을 로그로 남깁니다.
2. 유사도 문제는 정규화 유무를 실험군으로 분리합니다.
3. 회귀/선형시스템은 `inv` 대신 `solve`/`lstsq`를 기본값으로 둡니다.
4. 고차원 입력은 PCA 또는 SVD 기반 압축 실험을 선행합니다.
5. 역전파 구현 시 파라미터와 그래디언트 형상이 일치하는지 `assert`로 검증합니다.

## 운영 체크리스트

- [ ] 선형회귀를 선형대수 관점에서 설명할 수 있습니다.
- [ ] 신경망 한 레이어가 행렬 곱과 비선형의 조합임을 이해했습니다.
- [ ] 임베딩 유사도 계산이 왜 벡터 비교 문제인지 설명할 수 있습니다.
- [ ] 역전파의 전치 패턴 `X.T @ dout`을 직접 유도할 수 있습니다.
- [ ] 그래디언트와 PCA가 시리즈의 다른 개념들과 연결된다는 점을 이해했습니다.

## 연습 문제

1. 아이리스 데이터셋에 로지스틱 회귀를 경사하강법으로 학습해 보세요.
2. NumPy만으로 2층 MLP의 순전파와 역전파를 구현해 보세요.
3. 임베딩 다섯 개 사이에서 가장 큰 코사인 유사도 두 쌍을 찾아 보세요.
4. 학습 루프에서 그래디언트 폭발 현상을 재현하고 클리핑으로 해결해 보세요.

## 정리와 다음 글

이 시리즈에서 본 벡터, 행렬, 내적, 선형변환, 기저, 고유값, 분해, PCA는 머신러닝 안에서 따로 놀지 않습니다. 데이터는 벡터와 행렬로 표현되고, 모델은 변환으로 정의되며, 학습은 그래디언트로 그 구조를 조정하는 과정입니다. 선형대수를 이해하면 결국 모델의 뼈대를 읽을 수 있습니다.

시리즈는 여기서 마무리하지만, 이 내용은 이후 미적분과 최적화, 확률과 통계로 자연스럽게 이어집니다. 선형대수 감각이 잡히면 수식이 갑자기 쉬워지지는 않아도, 적어도 무엇이 어디서 움직이는지는 훨씬 분명하게 보이기 시작합니다.

## 처음 질문으로 돌아가기

- **머신러닝 파이프라인의 어디에서 벡터와 행렬이 등장할까요?**
  - 데이터 행렬 `X`는 샘플×피처 구조이고, 모델 파라미터 `W`는 입력 차원과 출력 차원을 잇는 행렬입니다. 손실 함수는 예측 벡터와 레이블 벡터의 차이로 계산되고, 그래디언트는 이 차이를 전치 행렬로 역전파합니다. 임베딩 유사도는 내적으로, 차원 축소는 SVD로, 정규화는 노름으로 처리됩니다. 파이프라인의 모든 단계가 선형대수 연산입니다.
- **선형회귀와 신경망은 선형대수 관점에서 어떻게 읽을 수 있을까요?**
  - 선형회귀는 `y_hat = X @ w` 하나의 행렬 곱으로 예측하고, `lstsq`로 최적 `w`를 구합니다. 신경망은 `h = relu(X @ W1 + b1)`, `y_hat = h @ W2 + b2`처럼 행렬 곱과 비선형 함수를 반복 쌓은 구조입니다. 핵심 차이는 비선형 활성화뿐이며, 기본 연산 단위는 동일한 행렬 곱입니다.
- **임베딩 유사도와 그래디언트 계산은 왜 선형대수 문제일까요?**
  - 임베딩 유사도는 두 벡터의 내적으로 정의됩니다. 코사인 유사도는 L2 정규화 후 내적이므로 `emb_n @ emb_n.T` 한 줄로 전체 유사도 행렬을 얻습니다. 그래디언트도 `grad = X.T @ err / n`처럼 행렬 곱으로 계산됩니다. 파라미터가 행렬이고 손실이 스칼라이면, 그래디언트는 같은 형상의 행렬이 나와야 하며, 이 조건을 만족시키는 연산이 행렬 전치 곱입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linear Algebra 101 (1/10): 선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): 벡터](./02-vectors.md)
- [Linear Algebra 101 (3/10): 행렬](./03-matrices.md)
- [Linear Algebra 101 (4/10): 내적과 거리](./04-inner-product-and-distance.md)
- [Linear Algebra 101 (5/10): 선형변환](./05-linear-transformation.md)
- [Linear Algebra 101 (6/10): 기저와 차원](./06-basis-and-dimension.md)
- [Linear Algebra 101 (7/10): 고유값과 고유벡터](./07-eigenvalues-and-eigenvectors.md)
- [Linear Algebra 101 (8/10): 행렬 분해](./08-matrix-decomposition.md)
- [Linear Algebra 101 (9/10): PCA](./09-pca.md)
- **머신러닝에서의 선형대수 (현재 글)**

<!-- toc:end -->

## 참고 자료

- 시리즈 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/linear-algebra-101/ko
- [Deep Learning Book — Linear Algebra](https://www.deeplearningbook.org/contents/linear_algebra.html)
- [fast.ai — Computational Linear Algebra](https://github.com/fastai/numerical-linear-algebra)
- [Stanford CS229 — Linear Algebra Review](https://cs229.stanford.edu/section/cs229-linalg.pdf)
- [3Blue1Brown — Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra)

Tags: LinearAlgebra, MachineLearning, DeepLearning, DataScience, Beginner

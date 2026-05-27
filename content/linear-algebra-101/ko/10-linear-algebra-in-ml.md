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

## 먼저 던지는 질문

- 머신러닝 파이프라인의 어디에서 벡터와 행렬이 등장할까요?
- 선형회귀와 신경망은 선형대수 관점에서 어떻게 읽을 수 있을까요?
- 임베딩 유사도와 그래디언트 계산은 왜 선형대수 문제일까요?

## 왜 중요한가

선형대수 감각이 약하면 모델이 블랙박스로 남습니다. 입력 형상이 왜 안 맞는지, 임베딩 유사도가 왜 이상한지, 그래디언트가 왜 저렇게 생겼는지, PCA가 왜 저 방향을 선택했는지 설명하기 어려워집니다.

반대로 선형대수 관점이 잡히면 모델의 안쪽이 훨씬 덜 신비로워집니다. 레이어는 행렬 곱과 비선형 활성화의 조합이고, 임베딩 검색은 벡터 비교이며, 최적화는 파라미터 벡터를 업데이트하는 반복 과정이라는 점이 보입니다. 이 감각은 프레임워크를 바꿔도 남습니다.

## 핵심 개념 한눈에 보기

머신러닝의 큰 흐름을 선형대수로 적으면 위 그림처럼 정리됩니다. 데이터는 행렬 `X`로 들어오고, 모델은 행렬 곱으로 정의되며, 손실의 미분 결과는 다시 벡터와 행렬이 됩니다.

## 핵심 용어

- 설계 행렬 `X`: 행은 샘플, 열은 피처를 뜻합니다.
- 가중치 `W`: 선형변환의 학습 가능한 파라미터입니다.
- 임베딩: 고차원 대상을 벡터로 표현한 결과입니다.
- 그래디언트: 손실을 파라미터에 대해 미분한 값입니다.
- 배치 행렬 곱: 여러 입력을 한 번에 처리하는 계산 패턴입니다.

## 읽기 전과 후

읽기 전에는 머신러닝이 모델별 기법 모음처럼 보일 수 있습니다. 선형회귀, MLP, 임베딩 검색, 차원 축소가 서로 다른 세계처럼 느껴집니다.

읽은 후에는 이들이 모두 벡터와 행렬의 조합이라는 공통 뼈대를 공유한다는 점이 보입니다. 즉 알고리즘은 달라도 문법은 크게 다르지 않습니다.

## 다섯 단계로 연결해 보기

### 1단계 — 선형회귀

```python
import numpy as np
rng = np.random.default_rng(0)
X = rng.normal(size=(100, 3))
y = X @ np.array([1.0, -2.0, 0.5]) + rng.normal(scale=0.1, size=100)
w_hat, *_ = np.linalg.lstsq(X, y, rcond=None)
print("w_hat:", w_hat)
```

선형회귀는 가장 직관적인 출발점입니다. 입력 행렬 `X`와 가중치 벡터가 곱해져 예측을 만들고, 최소제곱 해법으로 적절한 가중치를 찾습니다.

### 2단계 — 신경망 한 레이어

```python
W1 = rng.normal(size=(3, 4))
b1 = np.zeros(4)
h = np.maximum(0, X @ W1 + b1)  # ReLU
print("hidden shape:", h.shape)
```

신경망도 구조는 비슷합니다. 입력 행렬과 가중치 행렬을 곱하고 편향을 더한 뒤 비선형 함수를 통과시킵니다. 선형대수 위에 비선형이 얹힌 형태입니다.

### 3단계 — 임베딩 유사도

```python
emb = rng.normal(size=(5, 8))
norms = np.linalg.norm(emb, axis=1, keepdims=True)
emb_n = emb / norms
sim = emb_n @ emb_n.T
print("sim matrix shape:", sim.shape)
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
for _ in range(50):
    L, g = loss_and_grad(w, X, y)
    w -= 0.05 * g
print("learned w:", w)
```

학습은 결국 파라미터 벡터를 조금씩 업데이트하는 반복입니다. 그래디언트 형상과 전치 위치가 왜 중요한지 여기서 바로 드러납니다.

### 5단계 — PCA로 피처 압축

```python
Xc = X - X.mean(axis=0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
X_2d = Xc @ Vt[:2].T
print("compressed:", X_2d.shape)
```

앞에서 배운 PCA는 데이터 자체를 더 잘 읽기 위한 선형대수 도구입니다. 모델을 학습하기 전, 데이터 구조를 압축하고 탐색하는 데 자주 쓰입니다.

## 작은 수치 예시로 다시 보기

- `np.linalg.lstsq`가 찾은 가중치는 대체로 `[1, -2, 0.5]` 근처로 수렴합니다. 생성한 데이터의 숨은 규칙을 다시 찾아낸 셈입니다.
- 은닉층 출력 형상은 `(100, 4)`, 임베딩 유사도 행렬 형상은 `(5, 5)`가 됩니다. 형상만 봐도 어떤 연산이 일어났는지 읽을 수 있습니다.
- 경사하강법으로 학습한 `w`도 최소제곱 해와 비슷한 방향으로 움직입니다. 해석과 학습이 같은 선형대수 위에 있다는 뜻입니다.

## 이 코드에서 먼저 볼 점

- 모든 레이어는 행렬 곱과 비선형의 조합입니다.
- 임베딩 비교는 내적과 정규화 문제입니다.
- 그래디언트는 벡터와 행렬에 대한 미분 결과입니다.
- 데이터 압축도 SVD와 PCA 같은 선형대수 도구로 이뤄집니다.

## 자주 하는 실수

1. 형상 불일치 문제를 대충 넘깁니다.
2. 정규화와 표준화를 빼먹습니다.
3. 행렬 곱과 원소곱을 헷갈립니다.
4. 그래디언트의 전치 위치를 잘못 둡니다.
5. 수치 안정성을 무시하고 `inv`를 직접 사용합니다.

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 모델을 볼 때 먼저 형상과 변환을 읽습니다. 입력 행렬이 어떤 의미인지, 가중치가 어떤 차원을 잇는지, 그래디언트가 어느 방향으로 흐르는지 확인합니다. 이 습관이 있으면 프레임워크 에러 메시지도 훨씬 빨리 해석할 수 있습니다.

또한 임베딩 공간에서는 유사도 메트릭을, 회귀나 분류에서는 수치 안정성과 정규화를, 고차원 데이터에서는 PCA나 SVD를 함께 떠올립니다. 선형대수는 별도 과목이 아니라 머신러닝 전반의 공용 인터페이스입니다.

## 체크리스트

- [ ] 선형회귀를 선형대수 관점에서 설명할 수 있습니다.
- [ ] 신경망 한 레이어가 행렬 곱과 비선형의 조합임을 이해했습니다.
- [ ] 임베딩 유사도 계산이 왜 벡터 비교 문제인지 설명할 수 있습니다.
- [ ] 그래디언트와 PCA가 시리즈의 다른 개념들과 연결된다는 점을 이해했습니다.

## 연습 문제

1. 아이리스 데이터셋에 로지스틱 회귀를 경사하강법으로 학습해 보세요.
2. NumPy만으로 2층 MLP의 순전파를 구현해 보세요.
3. 임베딩 다섯 개 사이에서 가장 큰 코사인 유사도 두 쌍을 찾아 보세요.

## 정리와 다음 글

이 시리즈에서 본 벡터, 행렬, 내적, 선형변환, 기저, 고유값, 분해, PCA는 머신러닝 안에서 따로 놀지 않습니다. 데이터는 벡터와 행렬로 표현되고, 모델은 변환으로 정의되며, 학습은 그래디언트로 그 구조를 조정하는 과정입니다. 선형대수를 이해하면 결국 모델의 뼈대를 읽을 수 있습니다.

시리즈는 여기서 마무리하지만, 이 내용은 이후 미적분과 최적화, 확률과 통계로 자연스럽게 이어집니다. 선형대수 감각이 잡히면 수식이 갑자기 쉬워지지는 않아도, 적어도 무엇이 어디서 움직이는지는 훨씬 분명하게 보이기 시작합니다.

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

# 2) 임베딩 유사도 (샘플 10개)
E = X[:10]
E = E / np.linalg.norm(E, axis=1, keepdims=True)
S = E @ E.T

# 3) PCA 압축
Xc = X - X.mean(axis=0)
U, sv, Vt = np.linalg.svd(Xc, full_matrices=False)
X3 = Xc @ Vt[:3].T

print('w_hat:', w_hat)
print('similarity matrix shape:', S.shape)
print('compressed shape:', X3.shape)
```

이 짧은 코드 안에 시리즈 핵심이 모두 들어 있습니다. `X @ w`는 선형변환, 유사도 행렬은 내적, `svd`는 분해와 차원 축소입니다.

## 실무 판단표: 어디서 선형대수를 먼저 점검할까

| 단계 | 흔한 문제 | 선형대수 점검 포인트 |
| --- | --- | --- |
| 데이터 준비 | 피처 중복/스케일 불균형 | 랭크, 표준화, 상관 구조 |
| 모델 학습 | 발산/느린 수렴 | 조건수, 학습률, 그래디언트 크기 |
| 임베딩 검색 | 유사도 품질 저하 | 정규화, 코사인/L2 선택 |
| 압축/시각화 | 정보 손실 과다 | 누적 설명률, 재구성 오차 |

## 머신러닝 알고리즘과 선형대수 연산 대응표

| ML 알고리즘 | 핵심 선형대수 연산 |
| --- | --- |
| 선형회귀 | `X @ w`, `lstsq`, 최소제곱 정규방정식 |
| 로지스틱 회귀 | `X @ w`, 시그모이드, 그래디언트 `X.T @ (pred - y)` |
| SVM | 커널 행렬 `K`, `K @ alpha`, 쌍대 문제 QP |
| 신경망 | 행렬 곱 `X @ W`, 역전파 체인룰, 그래디언트 누적 |
| 추천 시스템(MF) | 저랭크 근사 `U @ V.T`, 잠재 요인 내적 |

이 표를 보면 거의 모든 ML 알고리즘이 벡터/행렬 연산 위에서 돌아간다는 점이 드러납니다. 학습 알고리즘은 다르지만, 선형대수 연산 패턴은 놀라울 만큼 비슷합니다.

## 넘파이로 역전파 한 번 계산하기

신경망의 역전파는 복잡해 보이지만, 행렬 미분 체인룰을 따라가면 명확한 선형대수 연산입니다. 아래는 2층 MLP의 순전파와 역전파를 NumPy로 직접 구현한 예시입니다.

```python
import numpy as np

# 데이터
rng = np.random.default_rng(123)
X = rng.normal(size=(4, 3))  # 4 샘플, 3 피처
y = np.array([0, 1, 0, 1])  # 이진 분류

# 파라미터 초기화
W1 = rng.normal(scale=0.1, size=(3, 2))  # 은닉층 2개 뉴런
b1 = np.zeros(2)
W2 = rng.normal(scale=0.1, size=(2, 1))  # 출력층 1개 뉴런
b2 = np.zeros(1)

# 순전파
z1 = X @ W1 + b1
a1 = np.maximum(0, z1)  # ReLU
z2 = a1 @ W2 + b2
a2 = 1 / (1 + np.exp(-z2))  # Sigmoid

# 손실 (binary cross-entropy)
loss = -np.mean(y.reshape(-1, 1) * np.log(a2 + 1e-8) + (1 - y.reshape(-1, 1)) * np.log(1 - a2 + 1e-8))

# 역전파
da2 = (a2 - y.reshape(-1, 1)) / len(y)  # (4, 1)
dz2 = da2  # sigmoid derivative 포함
dW2 = a1.T @ dz2  # (2, 1)
db2 = dz2.sum(axis=0)  # (1,)

da1 = dz2 @ W2.T  # (4, 2)
dz1 = da1 * (z1 > 0)  # ReLU derivative
dW1 = X.T @ dz1  # (3, 2)
db1 = dz1.sum(axis=0)  # (2,)

print('loss:', loss)
print('dW1 shape:', dW1.shape, 'dW2 shape:', dW2.shape)
print('dW1:\n', dW1)
```

출력 예시:

```
loss: 0.723
dW1 shape: (3, 2) dW2 shape: (2, 1)
dW1:
 [[-0.012  0.034]
 [ 0.021 -0.018]
 [ 0.005  0.011]]
```

여기서 핵심은 `X.T @ dz1`, `a1.T @ dz2` 같은 행렬 곱 패턴입니다. 전치와 곱 순서만 맞으면 그래디언트 형상이 파라미터 형상과 일치합니다. 이 패턴을 이해하면 PyTorch나 TensorFlow의 자동미분 결과도 직접 검증할 수 있습니다.

## 지피유와 행렬 연산

딥러닝이 빠른 이유 중 하나는 GPU가 행렬 곱을 병렬로 매우 빠르게 처리하기 때문입니다. GPU는 수천 개의 작은 코어로 이뤄져 있어, 같은 연산을 동시에 여러 데이터에 적용하는 SIMD(Single Instruction Multiple Data) 패턴에 강합니다.

행렬 곱 `C = A @ B`는 각 `C[i, j]`를 독립적으로 계산할 수 있으므로 병렬화에 이상적입니다. GPU는 이를 블록 단위로 쪼개 수천 개 스레드가 동시에 처리합니다.

실무에서 GPU 가속을 최대한 활용하려면:

1. **배치 크기를 크게**: 작은 배치 여러 번보다 큰 배치 한 번이 GPU 활용률이 높습니다.
2. **행렬 형상 정렬**: 32의 배수로 맞추면 메모리 접근 효율이 올라갑니다.
3. **불필요한 CPU↔GPU 전송 최소화**: 텐서를 CPU로 가져오는 순간 병목이 생깁니다.

선형대수를 이해하면 모델이 "왜 GPU에서 빠른지", "어떤 연산이 병목인지"도 읽을 수 있습니다. 예를 들어 순환 구조(RNN)는 순차 의존성 때문에 병렬화가 어렵고, Transformer는 행렬 곱으로 attention을 계산해 GPU 효율이 높습니다.

GPU 프로그래밍은 고급 주제지만, 그 밑바탕은 결국 "행렬 곱을 얼마나 잘게 쪼개 병렬로 돌리느냐"는 선형대수 질문입니다. CUDA, cuBLAS, cuDNN 같은 라이브러리는 모두 행렬 연산 최적화를 핵심으로 삼습니다.

이 관점을 갖추면 프레임워크 성능 팁을 단순 암기가 아니라 수학적 근거로 이해할 수 있습니다.
## 작은 역전파 예시로 보는 행렬 미분 구조

```python
# y_hat = XW, L = 평균((y_hat - y)^2)

pred = X @ w_hat
err = pred - y
grad = 2 * X.T @ err / len(y)
print('grad shape:', grad.shape)
```

`X.T @ err` 구조를 이해하면 프레임워크가 자동미분으로 계산하는 값도 직접 해석할 수 있습니다. 즉 선형대수는 딥러닝 시대에도 "이론 배경"이 아니라 "디버깅 언어"입니다.

## 시리즈를 실전에 연결하는 권장 루틴

1. 모든 모델 코드에서 텐서 형상을 로그로 남깁니다.
2. 유사도 문제는 정규화 유무를 실험군으로 분리합니다.
3. 회귀/선형시스템은 `inv` 대신 `solve`/`lstsq`를 기본값으로 둡니다.
4. 고차원 입력은 PCA 또는 SVD 기반 압축 실험을 선행합니다.

이 네 가지를 습관화하면 모델 이해 속도와 디버깅 품질이 동시에 올라갑니다.

## 실전 확장 노트: NumPy 계산 루틴과 해석 체크포인트

아래 루틴은 장이 달라도 반복해서 사용할 수 있는 공통 점검 템플릿입니다. 벡터/행렬 연산을 수행할 때 형상 확인, 수치 안정성, 기하학 해석을 함께 기록하면 학습 속도가 크게 빨라집니다.

```python
import numpy as np

rng = np.random.default_rng(123)
X = rng.normal(size=(6, 4))
v = rng.normal(size=4)
A = rng.normal(size=(4, 4))

print('X shape:', X.shape)
print('v shape:', v.shape)
print('A shape:', A.shape)

# 기본 연산
xv = X @ v
Av = A @ v
print('Xv shape:', xv.shape)
print('Av shape:', Av.shape)

# 대칭 행렬 구성 후 고유값 확인
S = A.T @ A
eigvals = np.linalg.eigvalsh(S)
print('eigvals(S):', eigvals)

# SVD와 랭크 근사
U, s, Vt = np.linalg.svd(X, full_matrices=False)
rank = np.linalg.matrix_rank(X)
X2 = U[:, :2] @ np.diag(s[:2]) @ Vt[:2, :]
rel_err = np.linalg.norm(X - X2) / np.linalg.norm(X)

print('rank(X):', rank)
print('singular values:', s)
print('relative error(rank-2):', rel_err)
```

위 코드에서 반드시 확인할 항목은 네 가지입니다.

1. **형상 보존**: `X @ v`의 결과 차원이 `(6,)`인지 즉시 확인합니다. 계산이 맞아도 형상이 다르면 이후 파이프라인에서 오류가 누적됩니다.
2. **대칭 양의 준정부호 구조**: `A.T @ A`는 항상 대칭이며 고유값이 음수가 나오지 않아야 합니다. 음수가 크게 나오면 수치 오차나 구현 실수를 의심해야 합니다.
3. **특이값 분포**: 특이값이 급격히 감소하면 저랭크 근사로도 구조를 상당 부분 유지할 가능성이 큽니다.
4. **상대 재구성 오차**: 압축 품질을 주관이 아닌 숫자로 판단합니다.

## 계산 결과를 문장으로 번역하는 연습

선형대수 실력이 빠르게 늘지 않는 가장 흔한 이유는 계산은 했지만 해석을 남기지 않기 때문입니다. 아래 질문을 매번 적어 두면 해석력이 올라갑니다.

- 이 연산은 공간에서 무엇을 보존하고 무엇을 바꾸는가?
- 결과 크기가 커진 이유는 변환 자체 때문인가, 입력 스케일 때문인가?
- 순서를 바꿨을 때 결과가 달라진다면 어떤 변환이 먼저 적용되었는가?
- 같은 결과를 분해 방식(LU/QR/SVD)으로 다시 계산하면 안정성이 좋아지는가?

## 작은 응용 시나리오

| 시나리오 | 선형대수 동작 | 점검 지표 |
| --- | --- | --- |
| 피처 압축 | SVD/PCA로 저차원 투영 | 누적 분산, 재구성 오차 |
| 유사도 검색 | 정규화 후 내적/코사인 | top-k 정확도, 스케일 민감도 |
| 회귀 학습 | `lstsq` 또는 경사하강 | 잔차 노름, 조건수 |
| 변환 파이프라인 | 행렬 합성 `A @ B @ x` | 중간 형상, 순서 민감성 |

이 표를 기준으로 실험 노트를 남기면, 한 번의 계산이 다음 장의 개념으로 자연스럽게 연결됩니다. 선형대수는 공식을 더 외울수록 좋아지는 과목이 아니라, 같은 계산을 더 정확히 해석할수록 깊어지는 과목입니다.

## 추가 연습: 단계별 검증 습관 만들기

아래 절차는 어떤 장의 코드에도 공통으로 적용할 수 있는 검증 루프입니다.

```python
# 1) shape 점검
# 2) 기준값(allclose) 점검
# 3) 수치 안정성(조건수/오차) 점검
# 4) 해석 메모(무엇이 커지고 줄었는지) 기록
```

짧아 보이지만 이 네 단계를 지키면 계산 실수 대부분을 초기에 막을 수 있습니다. 특히 교육용 예제에서는 결과 숫자만 맞추기보다, 왜 그 숫자가 나왔는지 한 줄 해석을 남기는 습관이 중요합니다. 예를 들어 노름이 커졌다면 입력 방향 때문인지 변환 스케일 때문인지 분리해서 적어야 합니다.

또한 동일한 문제를 두 방식으로 풀어 비교하는 연습이 좋습니다. 예를 들어 선형시스템은 `inv` 경로와 `solve` 경로를 비교하고, 차원 축소는 공분산 고유분해와 SVD 경로를 비교하면 계산 안정성과 해석력을 동시에 키울 수 있습니다. 이런 비교 루틴이 쌓이면 새로운 라이브러리를 만나도 핵심 검증 기준은 흔들리지 않습니다.

## 실전 연결: 학습 루프를 선형대수 관점으로 점검하기

머신러닝 실험이 흔들릴 때는 모델 종류보다 연산 흐름을 먼저 점검하는 편이 빠릅니다. 입력 행렬 형상, 가중치 형상, 그래디언트 형상, 업데이트 스텝의 스케일이 일관되는지 확인하면 상당수 문제를 초기에 차단할 수 있습니다.

```python
import numpy as np

rng = np.random.default_rng(7)
X = rng.normal(size=(64, 16))
W = rng.normal(scale=0.1, size=(16, 8))
y = rng.normal(size=(64, 8))

lr = 0.05
for _ in range(20):
    pred = X @ W
    err = pred - y
    grad = (X.T @ err) / len(X)
    W -= lr * grad

print('pred shape:', pred.shape, 'grad shape:', grad.shape)
print('loss:', float((err**2).mean()))
```

이 패턴은 선형회귀, 다층퍼셉트론, 임베딩 투영층에서도 그대로 반복됩니다. 표현은 달라도 핵심은 행렬 곱과 전치, 축 평균, 경사 업데이트입니다.

시리즈 관점에서 보면 이 한 루프 안에 대부분의 주제가 들어 있습니다. 벡터는 샘플 표현, 행렬은 파라미터, 내적은 유사도와 손실 계산, 고유값과 특이값은 데이터 구조 해석, 주성분분석은 전처리 압축으로 연결됩니다. 따라서 선형대수를 이해한다는 것은 개별 공식을 외우는 것이 아니라, 학습 시스템 전체를 같은 좌표계로 읽는 능력을 갖추는 일입니다.

## 복습 메모: 다음 글로 넘어가기 전 확인

- 이번 글의 핵심 계산을 넘파이 코드로 다시 실행해 결과를 직접 확인합니다.
- 기하학적 해석 한 줄과 대수적 해석 한 줄을 함께 적어 두면 기억 유지에 도움이 됩니다.
- 머신러닝 맥락에서는 이 개념이 입력 표현, 가중치 구조, 임베딩 비교, 주성분 해석 중 어디에 연결되는지 점검합니다.

## 처음 질문으로 돌아가기

- **머신러닝 파이프라인의 어디에서 벡터와 행렬이 등장할까요?**
  - 이 글에서는 처음부터 끝까지 거의 모든 단계가 행렬과 벡터로 적혔습니다. 데이터는 `X`, 회귀는 `X @ w`, 은닉층은 `X @ W1 + b1`, 임베딩 유사도는 `emb_n @ emb_n.T`, PCA는 `np.linalg.svd(Xc)`로 나타나니 파이프라인 전체가 선형대수 위에 서 있습니다.
- **선형회귀와 신경망은 선형대수 관점에서 어떻게 읽을 수 있을까요?**
  - 선형회귀는 `np.linalg.lstsq(X, y, rcond=None)`로 가중치 벡터를 찾는 단일 선형변환 문제이고, 신경망은 여기에 `np.maximum(0, X @ W1 + b1)` 같은 비선형을 층마다 얹은 구조입니다. 즉 둘의 문법은 다르지 않고, 신경망이 더 깊은 선형대수 연쇄라고 보면 됩니다.
- **임베딩 유사도와 그래디언트 계산은 왜 선형대수 문제일까요?**
  - 임베딩 비교는 정규화된 벡터의 내적 행렬 `sim = emb_n @ emb_n.T`를 계산하는 문제이고, 학습은 `grad = 2 * X.T @ err / len(y)`처럼 전치와 행렬 곱으로 파라미터 방향을 구하는 문제였습니다. 표현 비교와 파라미터 업데이트가 모두 같은 연산 체계를 공유하니, 둘 다 선형대수 문제라고 부르는 것이 정확합니다.

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

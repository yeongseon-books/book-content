---
series: linear-algebra-101
episode: 10
title: 머신러닝에서의 선형대수
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

# 머신러닝에서의 선형대수

시리즈를 여기까지 따라왔다면 이제 남은 질문은 하나입니다. 그래서 이 선형대수가 실제 머신러닝 안에서 어디에 나타나는가 하는 질문입니다. 답은 생각보다 단순합니다. 거의 모든 곳입니다. 데이터 표현, 모델 정의, 손실 계산, 최적화 과정이 모두 벡터와 행렬 위에서 돌아갑니다.

이 글은 Linear Algebra 101 시리즈의 마지막 글입니다. 여기서는 선형회귀, 신경망, 임베딩, 그래디언트, PCA를 한 흐름으로 묶어 시리즈를 마무리하겠습니다.

## 이 글에서 다룰 문제

- 머신러닝 파이프라인의 어디에서 벡터와 행렬이 등장할까요?
- 선형회귀와 신경망은 선형대수 관점에서 어떻게 읽을 수 있을까요?
- 임베딩 유사도와 그래디언트 계산은 왜 선형대수 문제일까요?
- 지금까지 배운 개념들은 실무에서 어떻게 연결될까요?

> 선형대수는 머신러닝의 주변 지식이 아니라 골격입니다. 데이터는 벡터와 행렬로 표현되고, 모델은 변환으로 정의되며, 학습은 그 구조를 조금씩 업데이트하는 과정입니다.

## 왜 중요한가

선형대수 감각이 약하면 모델이 블랙박스로 남습니다. 입력 형상이 왜 안 맞는지, 임베딩 유사도가 왜 이상한지, 그래디언트가 왜 저렇게 생겼는지, PCA가 왜 저 방향을 선택했는지 설명하기 어려워집니다.

반대로 선형대수 관점이 잡히면 모델의 안쪽이 훨씬 덜 신비로워집니다. 레이어는 행렬 곱과 비선형 활성화의 조합이고, 임베딩 검색은 벡터 비교이며, 최적화는 파라미터 벡터를 업데이트하는 반복 과정이라는 점이 보입니다. 이 감각은 프레임워크를 바꿔도 남습니다.

## 핵심 개념 한눈에 보기

![핵심 개념 한눈에 보기](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/10/10-01-concept-at-a-glance.ko.png)

*데이터 행렬, 모델, 손실, 그래디언트, 업데이트가 하나의 선형대수 흐름으로 연결되는 모습을 보여 줍니다.*

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

<!-- toc:begin -->
- [선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [벡터](./02-vectors.md)
- [행렬](./03-matrices.md)
- [내적과 거리](./04-inner-product-and-distance.md)
- [선형변환](./05-linear-transformation.md)
- [기저와 차원](./06-basis-and-dimension.md)
- [고유값과 고유벡터](./07-eigenvalues-and-eigenvectors.md)
- [행렬 분해](./08-matrix-decomposition.md)
- [PCA](./09-pca.md)
- **머신러닝에서의 선형대수 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Deep Learning Book — Linear Algebra](https://www.deeplearningbook.org/contents/linear_algebra.html)
- [fast.ai — Computational Linear Algebra](https://github.com/fastai/numerical-linear-algebra)
- [Stanford CS229 — Linear Algebra Review](https://cs229.stanford.edu/section/cs229-linalg.pdf)
- [3Blue1Brown — Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra)

Tags: LinearAlgebra, MachineLearning, DeepLearning, DataScience, Beginner

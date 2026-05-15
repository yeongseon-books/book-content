---
series: linear-algebra-101
episode: 9
title: PCA
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
  - PCA
  - DimensionalityReduction
  - DataScience
  - Beginner
seo_description: PCA가 분산이 큰 축을 새로 찾아 차원을 줄이는 원리를 설명하고 SVD와 분산 설명률을 활용한 실무 분석 방법을 정리합니다.
last_reviewed: '2026-05-12'
---

# PCA

차원이 큰 데이터를 다루다 보면 모든 축이 똑같이 중요하지 않다는 사실을 곧 느끼게 됩니다. 어떤 축은 정보가 많이 담겨 있고, 어떤 축은 노이즈에 가깝습니다. PCA는 이 차이를 가장 고전적이고 명확한 방식으로 다루는 도구입니다.

이 글은 Linear Algebra 101 시리즈의 9번째 글입니다. 여기서는 PCA를 분산이 가장 큰 축을 찾고 그 축으로 데이터를 다시 표현하는 방법으로 이해해 보겠습니다.

## 이 글에서 다룰 문제

- PCA는 왜 중요한 방향을 찾아낸다고 말할 수 있을까요?
- 공분산 관점과 SVD 관점은 어떻게 연결될까요?
- 왜 중심화가 빠지면 안 될까요?
- 몇 개의 주성분을 남길지 어떻게 판단할까요?

> PCA는 데이터를 가장 잘 설명하는 직교 축을 새로 찾은 뒤, 그중 중요한 축만 남겨 표현을 압축하는 방법입니다.

## 왜 중요한가

차원 축소, 시각화, 노이즈 제거, 피처 압축은 실무에서 자주 만나는 요구입니다. PCA는 이 문제를 가장 기본적인 선형대수 방식으로 풀어 줍니다. 특히 고차원 데이터를 먼저 가볍게 훑어 보고 싶을 때 매우 유용합니다.

또한 PCA는 앞에서 배운 기저, 고유값, SVD가 실제 데이터 문제에서 어떻게 합쳐지는지 보여 주는 좋은 예입니다. 주성분은 새로운 기저이고, 분산 설명률은 어떤 축이 얼마나 중요한지 알려 줍니다.

## 핵심 개념 한눈에 보기

```mermaid
flowchart LR
    Data["High-dim data X"] --> Center["Center"]
    Center --> Cov["Covariance or SVD"]
    Cov --> PC["Principal components"]
    PC --> Proj["Project to top-k axes"]
```

PCA의 핵심 흐름은 단순합니다. 먼저 평균을 빼서 중심화하고, 데이터의 분산이 큰 방향을 찾은 뒤, 상위 몇 개 축에 투영합니다. 남은 축의 수가 곧 줄인 차원입니다.

## 핵심 용어

- 주성분: 분산이 큰 순서대로 정렬된 새로운 직교 축입니다.
- 분산 설명률: 각 주성분이 전체 분산 중 얼마나 설명하는지 나타내는 비율입니다.
- 공분산 행렬: 중심화된 데이터의 축 간 관계를 담는 행렬입니다.
- SVD 기반 PCA: 데이터 행렬을 SVD로 분해해 주성분을 얻는 방식입니다.
- 재구성 오차: 차원을 줄였다가 다시 복원했을 때 생기는 손실입니다.

## 읽기 전과 후

읽기 전에는 차원 축소를 단순히 피처 몇 개를 버리는 일로 보기 쉽습니다. 이 경우 정보 손실이 어떻게 관리되는지 설명하기 어렵습니다.

읽은 후에는 PCA가 데이터를 더 잘 설명하는 축으로 먼저 회전한 뒤, 중요한 축만 남기는 과정이라는 점이 보입니다. 즉 무작정 버리는 것이 아니라 구조를 다시 잡는 작업입니다.

## 다섯 단계로 PCA 읽기

### 1단계 — 데이터 생성

```python
import numpy as np
rng = np.random.default_rng(0)
X = rng.normal(size=(100, 3)) @ np.array([[1, 0.8, 0],
                                          [0, 0.6, 0],
                                          [0, 0,   1]])
```

예제 데이터는 축마다 분산 구조가 다르게 나타나도록 만들어 두었습니다. PCA가 어떤 방향을 중요하게 보는지 확인하기 좋습니다.

### 2단계 — 중심화

```python
Xc = X - X.mean(axis=0)
```

중심화는 PCA에서 빠지면 안 됩니다. 평균이 남아 있으면 분산 구조 대신 위치 정보가 섞여 버립니다.

### 3단계 — SVD

```python
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
print("singular values:", S)
print("explained variance ratio:", (S**2) / (S**2).sum())
```

SVD를 통해 주성분과 분산 설명률을 얻을 수 있습니다. 특이값이 클수록 더 많은 분산을 설명합니다.

### 4단계 — 상위 2개 축으로 투영

```python
k = 2
X_2d = Xc @ Vt[:k].T
print("projected shape:", X_2d.shape)
```

상위 `k`개 축만 남기면 데이터 표현이 더 작아집니다. 이 단계가 실제 차원 축소입니다.

### 5단계 — 재구성 오차

```python
X_rec = X_2d @ Vt[:k]
err = np.linalg.norm(Xc - X_rec) / np.linalg.norm(Xc)
print("relative reconstruction error:", err)
```

차원을 줄인 만큼 정보 손실도 생깁니다. 재구성 오차는 그 손실을 숫자로 보여 줍니다.

## 이 코드에서 먼저 볼 점

- 중심화는 필수입니다.
- SVD는 PCA를 구현하는 안정적인 경로입니다.
- 분산 설명률은 `k` 선택의 중요한 기준입니다.
- 재구성 오차를 보면 압축 손실을 함께 판단할 수 있습니다.

## 자주 하는 실수

1. 중심화나 스케일링을 빼먹습니다.
2. 스케일이 큰 피처가 주성분을 지배한다는 점을 놓칩니다.
3. 주성분 부호가 임의적이라는 사실을 잊습니다.
4. 강한 비선형 구조에도 PCA가 모든 것을 해결할 거라 기대합니다.
5. 근거 없이 `k`를 정합니다.

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 PCA를 단순한 차원 축소 도구로만 보지 않습니다. 데이터가 실제로 몇 개의 큰 방향으로 요약되는지, 노이즈가 얼마나 많은지, 시각화나 모델 입력 압축에 도움이 되는지 함께 봅니다.

또한 PCA 전에 표준화가 필요한지 판단합니다. 피처 스케일이 크게 다르면 분산이 큰 변수 하나가 결과를 지배할 수 있기 때문입니다. 좋은 PCA 사용법은 알고리즘을 적용하는 것보다, 어떤 전처리와 어떤 `k`가 문제에 맞는지 결정하는 데 있습니다.

## 체크리스트

- [ ] PCA가 새로운 기저를 찾는 과정이라는 점을 설명할 수 있습니다.
- [ ] 중심화가 왜 필요한지 이해했습니다.
- [ ] 분산 설명률을 보고 `k`를 선택할 수 있습니다.
- [ ] 재구성 오차의 의미를 말할 수 있습니다.

## 연습 문제

1. 아이리스 데이터셋에 PCA를 적용해 2차원으로 시각화해 보세요.
2. 누적 분산 설명률이 90%를 넘는 최소 `k`를 찾아 보세요.
3. PCA와 단순 피처 선택의 차이를 설명해 보세요.

## 정리와 다음 글

PCA는 데이터를 더 잘 설명하는 축을 새로 찾고, 그중 중요한 축만 남겨 차원을 줄이는 방법입니다. 기저 선택, 고유값, SVD, 재구성 오차가 한 자리에서 만나는 대표적인 주제이기도 합니다. 그래서 PCA를 이해하면 선형대수가 실제 데이터 문제에 어떻게 쓰이는지 훨씬 또렷하게 보입니다.

다음 글에서는 시리즈를 마무리하며 머신러닝 전반에서 선형대수가 어떻게 이어지는지 종합합니다. 지금까지 배운 벡터, 행렬, 변환, 분해, PCA가 하나의 모델 안에서 어떻게 연결되는지 보겠습니다.

<!-- toc:begin -->
- [선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [벡터](./02-vectors.md)
- [행렬](./03-matrices.md)
- [내적과 거리](./04-inner-product-and-distance.md)
- [선형변환](./05-linear-transformation.md)
- [기저와 차원](./06-basis-and-dimension.md)
- [고유값과 고유벡터](./07-eigenvalues-and-eigenvectors.md)
- [행렬 분해](./08-matrix-decomposition.md)
- **PCA (현재 글)**
- 머신러닝에서의 선형대수 (예정)
<!-- toc:end -->

## 참고 자료

- [Wikipedia — Principal component analysis](https://en.wikipedia.org/wiki/Principal_component_analysis)
- [scikit-learn — PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)
- [Setosa — Principal Component Analysis](https://setosa.io/ev/principal-component-analysis/)
- [Stanford CS229 — Notes on PCA](https://cs229.stanford.edu/notes2020spring/cs229-notes10.pdf)

Tags: LinearAlgebra, PCA, DimensionalityReduction, DataScience, Beginner

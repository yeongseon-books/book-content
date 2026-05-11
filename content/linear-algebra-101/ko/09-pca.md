---
series: linear-algebra-101
episode: 9
title: PCA
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - LinearAlgebra
  - PCA
  - DimensionalityReduction
  - DataScience
  - Beginner
seo_description: PCA(주성분분석)의 정의와 SVD 기반 동작 원리, 그리고 ML에서의 차원 축소 활용을 NumPy 코드와 함께 정리한 입문 글
last_reviewed: '2026-05-04'
---

# PCA

> Linear Algebra 101 시리즈 (9/10)


## 이 글에서 다룰 문제

차원 축소, 시각화, 노이즈 제거, *피처 압축* — *PCA* 가 가장 기본이자 강력한 도구입니다.

> *PCA finds the directions that explain the most variance.*

## 전체 흐름
```mermaid
flowchart LR
    Data["High-dim data X"] --> Center["Center"]
    Center --> Cov["Covariance or SVD"]
    Cov --> PC["Principal components"]
    PC --> Proj["Project to top-k axes"]
```

## Before/After

**Before**: *“차원 축소? 그냥 일부 피처 버린다.”*

**After**: *“PCA는 *최적 회전 후 상위 k개 축* 을 선택 — *분산 손실 최소*.”*

## 5단계 PCA

### 1단계 — 데이터 생성

```python
import numpy as np
rng = np.random.default_rng(0)
X = rng.normal(size=(100, 3)) @ np.array([[1, 0.8, 0],
                                          [0, 0.6, 0],
                                          [0, 0,   1]])
```

### 2단계 — 중심화

```python
Xc = X - X.mean(axis=0)
```

### 3단계 — SVD

```python
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
print("singular values:", S)
print("explained variance ratio:", (S**2) / (S**2).sum())
```

### 4단계 — 상위 2개 PC로 투영

```python
k = 2
X_2d = Xc @ Vt[:k].T
print("projected shape:", X_2d.shape)
```

### 5단계 — 재구성 오차

```python
X_rec = X_2d @ Vt[:k]
err = np.linalg.norm(Xc - X_rec) / np.linalg.norm(Xc)
print("relative reconstruction error:", err)
```

## 이 코드에서 주목할 점

- *중심화* 는 *필수*.
- *SVD* 가 *수치적으로 안정*.
- *분산 설명률* 로 *k 선택*.

## 자주 하는 실수 5가지

1. ***중심화/스케일링* 누락.**
2. ***스케일이 큰 피처* 가 *PC 지배*.**
3. ***PC의 부호* 가 *임의* 임을 망각.**
4. ***비선형 관계* 에 *PCA* 적용 — 효과 적음.**
5. ***k* 를 *임의로* 선택.**

## 실무에서는 이렇게 쓰입니다

이미지 압축, 노이즈 제거, *EDA 시각화*, *피처 압축*, *유전체 데이터* 분석 — 모두 *PCA* 의 응용입니다.

## 체크리스트

- [ ] *PCA* 를 NumPy로 구현 가능.
- [ ] *분산 설명률* 계산 가능.
- [ ] *k 선택 기준* 안다.
- [ ] *재구성 오차* 측정 가능.

## 정리 및 다음 단계

PCA는 *차원 축소의 표준* 입니다. 다음 글에서는 *ML에서의 선형대수* 를 종합합니다.

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

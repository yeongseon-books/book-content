---
series: linear-algebra-101
episode: 6
title: 기저와 차원
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
  - Basis
  - Dimension
  - DataScience
  - Beginner
seo_description: 기저, 차원, 선형독립, 랭크의 정의와 의미를 NumPy 코드와 함께 정리한 입문 글
last_reviewed: '2026-05-04'
---

# 기저와 차원

> Linear Algebra 101 시리즈 (6/10)


## 이 글에서 다룰 문제

*특이행렬*, *과적합*, *PCA* 의 *분산축* — 모두 *기저와 차원* 으로 설명됩니다.

> *Dimension is the count; basis is the choice of axes.*

## 전체 흐름
```mermaid
flowchart LR
    Vecs["Set of vectors"] --> Indep["Linearly independent?"]
    Indep --> Basis["Basis"]
    Basis --> Dim["Dimension"]
    Dim --> Rank["Rank of matrix"]
```

## Before/After

**Before**: *“기저는 표준 단위벡터”* 만 안다.

**After**: *“기저는 *선택* 가능 — 같은 공간에 *여러 좌표계* 가 있다.”*

## 5단계 기저와 차원

### 1단계 — 표준기저

```python
import numpy as np
e1 = np.array([1.0, 0.0])
e2 = np.array([0.0, 1.0])
print("e1, e2:", e1, e2)
```

### 2단계 — 선형결합

```python
v = 3 * e1 + 4 * e2
print("v:", v)
```

### 3단계 — 선형독립 확인 (랭크)

```python
A = np.column_stack([e1, e2])
print("rank:", np.linalg.matrix_rank(A))  # 2
```

### 4단계 — 종속인 경우

```python
B = np.column_stack([np.array([1.0, 2.0]), np.array([2.0, 4.0])])
print("rank:", np.linalg.matrix_rank(B))  # 1
```

### 5단계 — 다른 기저로 표현

```python
b1 = np.array([1.0, 1.0])
b2 = np.array([1.0, -1.0])
B = np.column_stack([b1, b2])
v = np.array([3.0, 4.0])
coords = np.linalg.solve(B, v)
print("coords in {b1,b2}:", coords)
```

## 이 코드에서 주목할 점

- *랭크* 가 *차원* 을 알려준다.
- *기저는 유일하지 않다*.
- *선형종속* 이면 *공간을 충분히 못 채움*.

## 자주 하는 실수 5가지

1. ***랭크 부족(rank-deficient)* 행렬을 *역행렬* 시도.**
2. ***기저는 유일* 이라 오해.**
3. ***부동소수점* 으로 *랭크 계산 오차*.**
4. ***차원 = 행렬 크기* 라고 오해.**
5. ***선형독립* 을 *시각적 직관* 만으로 판단.**

## 실무에서는 이렇게 쓰입니다

PCA의 *주성분* 은 *새로운 기저*. *피처 선택/차원 축소* 가 *공간의 기저 변환*. *멀티콜리니어리티* 는 *랭크 부족*.

## 체크리스트

- [ ] *선형독립* 판별 가능.
- [ ] *랭크* 계산 가능.
- [ ] *다른 기저로 좌표* 변환 가능.
- [ ] *차원/랭크* 차이를 안다.

## 정리 및 다음 단계

기저는 *좌표축의 선택*, 차원은 *그 개수* 입니다. 다음 글에서는 *고유값과 고유벡터* 를 다룹니다.

<!-- toc:begin -->
- [선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [벡터](./02-vectors.md)
- [행렬](./03-matrices.md)
- [내적과 거리](./04-inner-product-and-distance.md)
- [선형변환](./05-linear-transformation.md)
- **기저와 차원 (현재 글)**
- 고유값과 고유벡터 (예정)
- 행렬 분해 (예정)
- PCA (예정)
- 머신러닝에서의 선형대수 (예정)
<!-- toc:end -->

## 참고 자료

- [3Blue1Brown — Basis vectors](https://www.3blue1brown.com/lessons/span)
- [Wikipedia — Basis (linear algebra)](https://en.wikipedia.org/wiki/Basis_(linear_algebra))
- [Wikipedia — Rank (linear algebra)](https://en.wikipedia.org/wiki/Rank_(linear_algebra))
- [NumPy — matrix_rank](https://numpy.org/doc/stable/reference/generated/numpy.linalg.matrix_rank.html)

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

특이행렬, 과적합, PCA의 분산축은 모두 기저와 차원 개념으로 설명할 수 있습니다.

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

**After**: *“기저는 하나로 고정되지 않습니다. 같은 공간도 여러 좌표계로 표현할 수 있습니다.”*

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

- 랭크를 보면 공간의 차원을 짐작할 수 있습니다.
- 기저는 하나로 정해지지 않습니다.
- 벡터들이 선형종속이면 공간을 충분히 채우지 못합니다.

## 자주 하는 실수 5가지

1. **랭크가 부족한 행렬에 역행렬을 구하려는 실수**
2. **기저가 유일하다고 오해하는 실수**
3. **부동소수점 오차를 무시한 채 랭크를 단정하는 실수**
4. **차원을 단순히 행렬 크기와 같다고 보는 실수**
5. **선형독립 여부를 시각적 직관만으로 판단하는 실수**

## 실무에서는 이렇게 쓰입니다

PCA의 주성분은 새로운 기저이고, 피처 선택과 차원 축소는 공간의 기저를 다시 잡는 과정으로 볼 수 있습니다. 멀티콜리니어리티 문제도 결국 랭크 부족과 연결됩니다.

## 체크리스트

- [ ] 선형독립 여부를 판별할 수 있다.
- [ ] 랭크를 계산할 수 있다.
- [ ] 다른 기저로 좌표를 변환할 수 있다.
- [ ] 차원과 랭크의 차이를 안다.

## 정리 및 다음 단계

기저는 좌표축을 어떻게 고를지의 문제이고, 차원은 그런 축이 몇 개 필요한지의 문제입니다. 다음 글에서는 고유값과 고유벡터를 다룹니다.

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

Tags: LinearAlgebra, Basis, Dimension, DataScience, Beginner

---
series: linear-algebra-101
episode: 8
title: 행렬 분해
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - LinearAlgebra
  - Decomposition
  - SVD
  - DataScience
  - Beginner
seo_description: LU, QR, 고유분해, SVD를 언제 왜 쓰는지 한 흐름으로 정리합니다
last_reviewed: '2026-05-12'
---

# 행렬 분해

행렬을 직접 다루다 보면 곧 한계를 만납니다. 역행렬을 바로 구하는 방식은 느리거나 불안정할 수 있고, 문제에 따라 더 적합한 계산 경로가 따로 있습니다. 이때 등장하는 것이 행렬 분해입니다. 복잡한 행렬을 해석 가능한 조각으로 나누어 계산을 더 안정적으로 만드는 방법입니다.

이 글은 Linear Algebra 101 시리즈의 8번째 글입니다. 여기서는 LU, QR, 고유분해, SVD를 같은 지도 위에서 정리해 보겠습니다.

## 이 글에서 다룰 문제

- 왜 역행렬보다 분해를 먼저 떠올려야 할까요?
- LU, QR, 고유분해, SVD는 각각 어디에 잘 맞을까요?
- 모든 분해가 모든 행렬에 적용되는 것은 아닐까요?
- 분해 결과는 어떻게 검증할 수 있을까요?

> 행렬 분해는 복잡한 변환을 더 단순한 조각으로 나누는 일입니다. 선형대수의 계산이 실제로 돌아가는 방식은 대개 역행렬보다 분해에 더 가깝습니다.

## 왜 중요한가

선형방정식 풀이, 최소제곱, 차원 축소, 이미지 압축, 추천 시스템의 행렬분해는 모두 어떤 형태로든 분해를 사용합니다. 수치 선형대수에서는 문제에 맞는 분해를 선택하는 것이 정확도와 속도를 함께 좌우합니다.

실무에서 특히 중요한 이유는 안정성입니다. `inv`를 바로 쓰는 코드는 짧아 보여도 수치적으로 약할 수 있습니다. 반대로 적절한 분해를 쓰면 더 안정적이고 해석도 쉬워집니다. 행렬 분해는 계산 트릭이 아니라 설계 선택입니다.

## 핵심 개념 한눈에 보기

```mermaid
flowchart LR
    A["Matrix A"] --> LU["LU: A = LU"]
    A --> QR["QR: A = QR"]
    A --> Eig["Eig: A = V D V^-1"]
    A --> SVD["SVD: A = U S V^T"]
```

이 네 분해는 서로 경쟁 관계라기보다 역할 분담에 가깝습니다. 어떤 문제는 LU가 맞고, 어떤 문제는 QR이나 SVD가 훨씬 자연스럽습니다.

## 핵심 용어

- LU 분해: 하삼각행렬과 상삼각행렬의 곱으로 나누는 방식입니다.
- QR 분해: 직교행렬과 상삼각행렬의 곱으로 표현하는 방식입니다.
- 고유분해: 대각화 가능한 경우 `V D V^-1` 형태로 쓰는 방식입니다.
- SVD: 모든 행렬에 대해 적용 가능한 가장 일반적인 분해 중 하나입니다.
- 특이값: SVD의 대각 성분으로, 항상 0 이상입니다.

## 읽기 전과 후

읽기 전에는 역행렬로 모든 문제를 풀고 싶어집니다. 공식이 간단해 보이기 때문입니다.

읽은 후에는 문제에 맞는 분해를 골라야 한다는 감각이 생깁니다. 같은 행렬이라도 어떤 질문을 던지느냐에 따라 좋은 분해가 달라집니다.

## 다섯 단계로 분해 읽기

### 1단계 — LU 분해

```python
import numpy as np
from scipy.linalg import lu
A = np.array([[4.0, 3.0], [6.0, 3.0]])
P, L, U = lu(A)
print("L:", L)
print("U:", U)
```

LU 분해는 방정식 풀이에서 자주 쓰입니다. 삼각행렬 구조 덕분에 계산을 단계적으로 단순화할 수 있습니다.

### 2단계 — QR 분해

```python
Q, R = np.linalg.qr(A)
print("Q^T Q ~ I:", np.allclose(Q.T @ Q, np.eye(2)))
print("R:", R)
```

QR 분해는 최소제곱 문제와 직교 기저를 다룰 때 특히 유용합니다. 직교 구조 덕분에 수치적으로 해석이 편한 경우가 많습니다.

### 3단계 — 고유분해

```python
vals, vecs = np.linalg.eig(A)
print("vals:", vals)
```

고유분해는 변환의 자연스러운 축을 찾고 싶을 때 의미가 큽니다. 다만 모든 행렬에 그대로 적용되는 것은 아닙니다.

### 4단계 — SVD

```python
U, S, Vt = np.linalg.svd(A)
print("U:", U)
print("S:", S)
print("Vt:", Vt)
```

SVD는 가장 범용적인 분해입니다. 직사각형 행렬에도 적용되고, 차원 축소와 저랭크 근사에도 직접 연결됩니다.

### 5단계 — SVD로 재구성

```python
A_reconstructed = U @ np.diag(S) @ Vt
print("close to A:", np.allclose(A_reconstructed, A))
```

재구성은 분해 결과를 확인하는 가장 직접적인 방법입니다. 분해가 맞다면 원래 행렬을 다시 얻을 수 있어야 합니다.

## 이 코드에서 먼저 볼 점

- 분해마다 잘 맞는 문제 유형이 다릅니다.
- SVD는 모든 행렬에 적용할 수 있습니다.
- 재구성은 좋은 검증 방법입니다.
- 수치 계산에서는 분해가 역행렬보다 안정적인 경우가 많습니다.

## 자주 하는 실수

1. 직사각형 행렬에도 LU를 그대로 적용하려고 합니다.
2. QR과 SVD의 차이를 모른 채 섞어 씁니다.
3. 특이값이 정렬되어 나온다는 점을 놓칩니다.
4. 부동소수점 결과를 `==`로 바로 비교합니다.
5. 최소제곱 문제를 역행렬로 직접 풀려고 합니다.

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 먼저 문제 유형을 묻습니다. 연립방정식인가, 최소제곱인가, 차원 축소인가, 저랭크 근사인가에 따라 도구가 달라져야 하기 때문입니다. 분해는 계산 도구이면서 문제 분류 도구이기도 합니다.

또한 안정성과 비용을 함께 봅니다. SVD는 강력하지만 비쌀 수 있고, LU는 빠르지만 모든 상황에 맞지 않습니다. 좋은 선택은 가장 유명한 분해를 고르는 것이 아니라, 지금 문제에 가장 적합한 분해를 고르는 것입니다.

## 체크리스트

- [ ] LU, QR, 고유분해, SVD의 쓰임새를 구분할 수 있습니다.
- [ ] 분해 결과를 재구성으로 검증할 수 있습니다.
- [ ] 역행렬보다 분해가 안정적인 이유를 설명할 수 있습니다.
- [ ] SVD가 왜 범용적인지 이해했습니다.

## 연습 문제

1. 3x2 직사각형 행렬의 SVD를 구하고 각 결과의 형상을 확인해 보세요.
2. 최소제곱 문제를 QR 분해로 푸는 방법을 정리해 보세요.
3. 저랭크 SVD로 원래 행렬을 근사하고 오차를 측정해 보세요.

## 정리와 다음 글

행렬 분해는 선형대수 계산을 실제로 작동하게 만드는 핵심 도구입니다. LU는 방정식 풀이에, QR은 최소제곱에, 고유분해는 축 해석에, SVD는 가장 일반적인 분해와 근사에 강합니다. 중요한 것은 이름을 나열하는 것이 아니라 문제에 맞는 분해를 고르는 감각입니다.

다음 글에서는 PCA를 다룹니다. 행렬 분해, 특히 SVD가 실제 데이터 차원 축소로 어떻게 이어지는지 가장 대표적인 예를 통해 살펴보겠습니다.

<!-- toc:begin -->
- [선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [벡터](./02-vectors.md)
- [행렬](./03-matrices.md)
- [내적과 거리](./04-inner-product-and-distance.md)
- [선형변환](./05-linear-transformation.md)
- [기저와 차원](./06-basis-and-dimension.md)
- [고유값과 고유벡터](./07-eigenvalues-and-eigenvectors.md)
- **행렬 분해 (현재 글)**
- PCA (예정)
- 머신러닝에서의 선형대수 (예정)
<!-- toc:end -->

## 참고 자료

- [Wikipedia — Matrix decomposition](https://en.wikipedia.org/wiki/Matrix_decomposition)
- [Wikipedia — Singular value decomposition](https://en.wikipedia.org/wiki/Singular_value_decomposition)
- [NumPy — linalg.svd](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html)
- [SciPy — linalg.lu](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lu.html)

Tags: LinearAlgebra, Decomposition, SVD, DataScience, Beginner

---
series: linear-algebra-101
episode: 3
title: "Linear Algebra 101 (3/10): 행렬"
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
  - Matrices
  - NumPy
  - DataScience
  - Beginner
seo_description: 행렬을 단순한 숫자 표를 넘어 벡터 공간에 작용하는 변환 규칙으로 정의하고 형상과 역행렬의 핵심 의미를 다룹니다.
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (3/10): 행렬

행렬은 선형대수에서 가장 자주 보이는 표기입니다. 데이터셋을 담는 테이블처럼 보이기도 하고, 어떤 벡터를 다른 벡터로 보내는 규칙처럼 읽히기도 합니다. 그래서 행렬을 숫자판으로만 이해하면 계산은 따라가도 왜 곱하는지는 남지 않습니다.

이 글은 Linear Algebra 101 시리즈의 3번째 글입니다.

여기서는 행렬을 형상과 변환이라는 두 관점으로 함께 이해해 보겠습니다.

![Linear Algebra 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/03/03-01-concept-at-a-glance.ko.png)
*Linear Algebra 101 3장 흐름 개요*
> 행렬은 단순한 숫자 표가 아니라 변환 규칙이자 벡터들의 집합입니다. 그래서 행렬의 구조(특히 행 개수와 열 개수)는 단순한 크기가 아니라 입력과 출력이 살고 있는 공간 자체를 정의합니다.

## 이 글에서 다룰 문제

- 행렬은 단순한 숫자 표와 무엇이 다를까요?
- 행렬 곱은 왜 변환의 합성으로 읽어야 할까요?
- 전치와 항등행렬, 역행렬은 각각 무엇을 뜻할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

선형회귀의 설계 행렬, 신경망의 가중치, 추천 시스템의 사용자-아이템 표현, 그래픽스의 변환 행렬은 모두 행렬로 적힙니다. 즉 행렬은 데이터 보관용 표기이면서 계산의 핵심 엔진입니다.

또한 실무에서 가장 흔한 오류 중 일부는 형상 불일치에서 시작합니다. 행렬이 몇 행 몇 열인지, 어떤 벡터를 입력으로 받아 어떤 벡터를 출력하는지 읽지 못하면 코드가 돌아가도 의미는 틀릴 수 있습니다.

## 핵심 용어 정리

행렬은 여러 역할을 동시에 가집니다. 표, 변환, 계산 규칙이 겹쳐 있습니다.

- **행렬**: `m x n` 형태의 숫자 배열입니다.
- **전치**: 행과 열을 바꾼 행렬 `A^T`입니다.
- **항등행렬**: 대각선만 1이고 나머지는 0인 행렬로, 벡터를 그대로 둡니다.
- **역행렬**: `A A^{-1} = I`를 만족하는 행렬입니다. 항상 존재하지는 않습니다.
- **행렬 곱**: 안쪽 차원이 맞을 때 정의되는 합성 연산입니다.

## 특수 행렬

특정 성질을 가진 행렬들은 실무에서 자주 등장합니다. 각 특수 행렬의 성질과 활용을 알면 더 효율적인 계산과 더 안정적인 알고리즘을 선택할 수 있습니다.

| 행렬 | 성질 | 활용 |
| --- | --- | --- |
| 단위행렬 | 대각선 1, 나머지 0 | 변환을 하지 않음, 곱셈 항등원 |
| 대각행렬 | 비대각 원소 0 | 축별 독립 스케일링, 고유값 행렬 |
| 대칭행렬 | `A = A^T` | 공분산 행렬, 고유값 실수 보장 |
| 직교행렬 | `A^T A = I` | 회전/반사, 길이 보존, QR 분해 |
| 희소행렬 | 대부분 0 | 메모리 절약, 효율적 저장/계산 |

대칭행렬은 고유값이 항상 실수로 나옵니다. 직교행렬은 벡터의 길이를 보존하며, 희소행렬은 큰 그래프나 추천 시스템의 사용자-아이템 행렬에서 효율적입니다.

## 읽기 전과 후

읽기 전에는 행렬 곱을 행과 열을 기계적으로 맞추는 절차로 보기 쉽습니다. 이 경우 왜 순서가 중요한지도 잘 남지 않습니다.

읽은 후에는 행렬 곱을 한 변환 뒤에 다른 변환을 적용하는 합성으로 읽게 됩니다. 그러면 비가환성이 낯선 규칙이 아니라 자연스러운 결과가 됩니다.

## 다섯 단계로 행렬 다루기

### 1단계 — 행렬 만들기

```python
import numpy as np
A = np.array([[1.0, 2.0], [3.0, 4.0]])
print("A:", A, "shape:", A.shape)
```

먼저 행렬을 만들고 형상을 확인합니다. 실무에서 가장 먼저 확인해야 할 정보도 바로 이 형상입니다.

### 2단계 — 전치

```python
print("A^T:", A.T)
print("A^T shape:", A.T.shape)
```

전치는 행과 열의 역할을 바꿉니다. 데이터 분석에서는 샘플과 피처의 축을 바꿔 보는 데도 자주 등장하고, 수식 전개에서도 매우 자주 나옵니다.

### 3단계 — 행렬 곱

```python
B = np.array([[5.0, 6.0], [7.0, 8.0]])
print("A B:", A @ B)
print("B A:", B @ A)  # different! non-commutative
print("same?", np.allclose(A @ B, B @ A))  # False
```

`A @ B`와 `B @ A`를 함께 보는 이유는 곱셈 순서가 결과를 바꾼다는 사실을 몸으로 익히기 위해서입니다.

### 4단계 — 항등행렬

```python
I = np.eye(2)
print("I:", I)
print("A I = A:", np.allclose(A @ I, A))  # True
print("I A = A:", np.allclose(I @ A, A))  # True
```

항등행렬은 아무것도 바꾸지 않는 변환입니다. 함수 관점으로 보면 입력을 그대로 돌려주는 규칙입니다.

### 5단계 — 역행렬

```python
A_inv = np.linalg.inv(A)
print("A^-1:", A_inv)
print("A A^-1 ~ I:", np.allclose(A @ A_inv, np.eye(2)))  # True
# 실무에서는 solve가 더 안정적
b = np.array([1.0, 2.0])
x = np.linalg.solve(A, b)
print("Ax = b 해:", x)
```

역행렬은 가능한 경우 변환을 되돌립니다. 다만 모든 행렬에 존재하지 않고, 수치 계산에서는 직접 역행렬을 구하는 방식보다 `solve`가 더 안정적입니다.

## 행렬 곱의 의미를 세 관점으로 읽기

행렬 곱 `C = AB`는 세 가지 관점으로 읽을 수 있습니다.

### 관점 1: 선형변환의 합성

`AB`는 먼저 `B` 변환을 적용한 후 `A` 변환을 적용하는 합성입니다.

```python
import numpy as np

theta = np.pi / 4
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
S = np.array([[2.0, 0.0],
              [0.0, 0.5]])

v = np.array([1.0, 0.0])
result1 = R @ (S @ v)   # 먼저 스케일, 그 다음 회전
result2 = (R @ S) @ v   # 합성 행렬을 미리 만듦
print('same?', np.allclose(result1, result2))  # True
```

### 관점 2: 내적의 모음

`C[i, j]`는 `A`의 `i`번째 행과 `B`의 `j`번째 열의 내적입니다.

```python
A = np.array([[1.0, 2.0], [3.0, 4.0]])
B = np.array([[5.0, 6.0], [7.0, 8.0]])
C = A @ B

# 수동 확인
c00 = np.dot(A[0, :], B[:, 0])
c01 = np.dot(A[0, :], B[:, 1])
print('C[0,0]:', C[0, 0], '== dot:', c00)  # 19.0
print('C[0,1]:', C[0, 1], '== dot:', c01)  # 22.0
```

### 관점 3: 열벡터의 선형 조합

`Ax`는 `A`의 열벡터들을 `x`의 원소로 가중합한 것입니다.

```python
A = np.array([[1.0, 2.0], [3.0, 4.0]])
x = np.array([5.0, 6.0])
result = A @ x
manual = 5 * A[:, 0] + 6 * A[:, 1]
print('same?', np.allclose(result, manual))  # True
```

## 실전 코드 패턴: 형상 점검과 안전한 풀이

```python
import numpy as np

# 형상 점검이 포함된 안전한 행렬 연산 패턴
X = np.array([[1.0, 2.0, 3.0],
              [0.5, 0.1, 0.2]])   # (2, 3)
W = np.array([[0.2, -0.3],
              [1.1,  0.4],
              [0.7,  0.2]])       # (3, 2)

Y = X @ W  # (2, 2)
print('X:', X.shape, 'W:', W.shape, 'Y:', Y.shape)

# 선형 시스템 풀기: solve vs inv
A = np.array([[3.0, 1.0],
              [1.0, 2.0]])
b = np.array([9.0, 8.0])

x_solve = np.linalg.solve(A, b)        # 권장 방법
x_inv = np.linalg.inv(A) @ b           # 덜 안정적
print('solve:', x_solve)
print('inv:', x_inv)
print('same?', np.allclose(x_solve, x_inv))

# 조건수 확인: 클수록 수치 불안정
print('cond(A):', np.linalg.cond(A))
```

`solve`와 `inv @ b`는 수학적으로 같지만, 수치 계산에서는 `solve`가 일반적으로 더 안정적입니다. 조건수가 커질수록 작은 입력 오차가 해에 크게 증폭됩니다.

## 행렬 연산을 단계별로 검증하기

```python
import numpy as np

A = np.array([[3.0, 1.0], [1.0, 2.0]])
B = np.array([[1.0, -1.0], [2.0, 0.0]])
v = np.array([2.0, 1.0])

first = B @ v
second = A @ first
direct = (A @ B) @ v

print('Bv =', first)
print('A(Bv) =', second)
print('(AB)v =', direct)
print('same?', np.allclose(second, direct))

# 행렬식: 면적 변환 비율
print('det(A):', np.linalg.det(A))  # 양수: 방향 보존
print('det(B):', np.linalg.det(B))  # 부호가 면적 방향 알려줌
```

이 확인이 익숙해지면, 복잡한 모델에서도 연산 순서를 논리적으로 추적할 수 있습니다.

## 응용 연결표

| 작업 | 행렬 역할 | 권장 계산 관점 |
| --- | --- | --- |
| 선형회귀 | 설계 행렬 | `lstsq`, QR/SVD 기반 풀이 |
| 추천 시스템 | 사용자-아이템 상호작용 | 저랭크 분해, 결측 처리 |
| 그래픽스 | 좌표 변환 | 합성 순서, 동차좌표 점검 |
| 신경망 | 가중치 행렬 | 배치 행렬 곱, 형상 일관성 |

행렬은 크기와 값만 보는 대상이 아니라, 수치 안정성·해석 가능성·연산 비용을 함께 고려하는 설계 대상입니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| `@`와 `*`를 같은 의미로 사용 | 원소별 곱이 행렬 곱으로 오해됨 | `@`는 행렬 곱, `*`는 Hadamard 곱 명확히 구분 |
| 행렬 곱 비가환성 무시 | `A @ B != B @ A` 오류 | 항상 순서 바꾼 결과를 `allclose`로 비교 확인 |
| 특이행렬의 역행렬 요청 | `LinAlgError` 또는 `nan` | `matrix_rank`로 랭크 먼저 확인, `lstsq` 사용 |
| 부동소수점 결과를 `==`로 비교 | 미세한 수치 오차로 `False` | `np.allclose` 사용, 허용 오차 명시 |
| 최소제곱 문제를 역행렬로 직접 풀기 | 수치 불안정, 느린 계산 | `np.linalg.lstsq` 또는 QR 분해 사용 |

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 행렬을 볼 때 먼저 계산보다 구조를 봅니다. 입력이 몇 차원이고, 출력이 몇 차원이며, 이 행렬이 데이터 표현인지 변환인지부터 구분합니다. 그래야 모델 디버깅에서 형상 문제와 의미 문제를 분리할 수 있습니다.

또한 직접 역행렬을 구하기보다 QR, SVD, LU 같은 분해를 더 선호합니다. 수치 안정성과 계산 비용을 함께 보기 때문입니다.

## 운영 체크리스트

- [ ] 행렬의 형상을 읽고 설명할 수 있습니다.
- [ ] 행렬 곱을 수행하고 순서 차이를 이해합니다.
- [ ] 전치와 항등행렬의 역할을 설명할 수 있습니다.
- [ ] 역행렬이 언제 존재하지 않는지 알고 있습니다.

## 연습 문제

1. 2x2 행렬 하나를 골라 전치와 역행렬을 직접 계산해 보세요.
2. 항등행렬을 임의의 벡터에 곱했을 때 결과가 왜 바뀌지 않는지 설명해 보세요.
3. 특이행렬 예시를 하나 만들고 역행렬이 왜 없는지 말해 보세요.

## 정리와 다음 글

행렬은 숫자 표이면서 동시에 변환의 압축 표현입니다. 전치는 축의 역할을 바꾸고, 항등행렬은 변환하지 않으며, 행렬 곱은 변환을 이어 붙입니다. 이 관점이 잡히면 행렬은 더 이상 계산 규칙의 모음이 아니라 공간을 다루는 실질적인 도구가 됩니다.

다음 글에서는 벡터 사이의 비교 기준인 내적과 거리를 다룹니다. 행렬이 벡터를 어떻게 바꾸는지 봤다면, 이제 벡터끼리 얼마나 비슷하고 얼마나 떨어져 있는지도 수식으로 읽을 차례입니다.

## 처음 질문으로 돌아가기

- **행렬은 단순한 숫자 표와 무엇이 다를까요?**
  - 행렬은 숫자 표이면서 동시에 변환의 압축 표현입니다. 형상 `(m, n)`은 단순한 크기가 아니라 `n`차원 입력을 `m`차원 출력으로 보내는 선형 함수를 정의합니다.

- **행렬 곱은 왜 변환의 합성으로 읽어야 할까요?**
  - `AB`는 먼저 `B`를 적용한 뒤 `A`를 적용하는 것과 같습니다. 각 행렬이 어떤 공간 변환인지 이해하면 곱셈의 의미가 자연스럽게 따라옵니다. 변환 관점이 없으면 비가환성도 설명하기 어렵습니다.

- **전치와 항등행렬, 역행렬은 각각 무엇을 뜻할까요?**
  - 전치는 행과 열의 역할을 바꾸는 연산으로, `A^T`를 곱하면 입력과 출력 공간이 뒤바뀝니다. 항등행렬은 변환하지 않는 항등 규칙이며, 역행렬은 변환을 되돌리는 연산입니다. 단, 역행렬은 정방이고 풀랭크인 경우에만 존재합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linear Algebra 101 (1/10): 선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): 벡터](./02-vectors.md)
- **Linear Algebra 101 (3/10): 행렬 (현재 글)**
- [Linear Algebra 101 (4/10): 내적과 거리](./04-inner-product-and-distance.md)
- [Linear Algebra 101 (5/10): 선형변환](./05-linear-transformation.md)
- [Linear Algebra 101 (6/10): 기저와 차원](./06-basis-and-dimension.md)
- [Linear Algebra 101 (7/10): 고유값과 고유벡터](./07-eigenvalues-and-eigenvectors.md)
- [Linear Algebra 101 (8/10): 행렬 분해](./08-matrix-decomposition.md)
- [Linear Algebra 101 (9/10): PCA](./09-pca.md)
- [머신러닝에서의 선형대수](./10-linear-algebra-in-ml.md)

<!-- toc:end -->

## 참고 자료

- 시리즈 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/linear-algebra-101/ko
- [3Blue1Brown — Matrix multiplication](https://www.3blue1brown.com/lessons/matrix-multiplication)
- [Khan Academy — Matrices](https://www.khanacademy.org/math/algebra-home/alg-matrices)
- [NumPy — linalg.inv](https://numpy.org/doc/stable/reference/generated/numpy.linalg.inv.html)
- [Wikipedia — Matrix](https://en.wikipedia.org/wiki/Matrix_(mathematics))

Tags: LinearAlgebra, Matrices, NumPy, DataScience, Beginner

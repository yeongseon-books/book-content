---
series: linear-algebra-101
episode: 6
title: "Linear Algebra 101 (6/10): 기저와 차원"
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
  - Basis
  - Dimension
  - DataScience
  - Beginner
seo_description: 기저, 차원, 선형독립, 랭크가 같은 공간을 어떻게 설명하는지 정리합니다
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (6/10): 기저와 차원

선형대수를 조금만 더 들어가면 공간을 표현하는 축은 왜 여러 개일 수 있는지, 또 그 축이 몇 개 필요한지가 궁금해집니다. 바로 이 질문에 답하는 개념이 기저와 차원입니다. 고유값, PCA, 랭크 부족 문제도 결국 여기서 다시 만납니다.

이 글은 Linear Algebra 101 시리즈의 6번째 글입니다.

여기서는 선형독립, 기저, 차원, 랭크를 하나의 그림으로 묶어 보겠습니다.

![Linear Algebra 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/06/06-01-concept-at-a-glance.ko.png)
*Linear Algebra 101 6장 흐름 개요*
> 기저와 차원은 벡터 공간의 언어를 정의합니다. 기저가 정해지면 그 공간의 모든 점을 고유하게 표현할 수 있습니다.

## 이 글에서 다룰 문제

- 어떤 벡터 집합이 공간을 충분히 설명한다는 말은 무슨 뜻일까요?
- 선형독립은 왜 기저의 핵심 조건일까요?
- 차원과 랭크는 어떻게 연결될까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

다중공선성, 차원 축소, PCA의 주성분, 특이행렬 문제는 모두 기저와 차원으로 설명할 수 있습니다. 즉 이 주제는 추상적인 정의를 외우는 단계에서 끝나지 않고, 모델 안정성과 데이터 표현 품질을 판단하는 데 직접 이어집니다.

예를 들어 어떤 피처가 다른 피처의 선형결합으로 거의 설명된다면 정보는 늘지 않는데 차원만 커집니다. 반대로 좋은 기저를 찾으면 같은 데이터를 더 간결하게 표현할 수 있습니다. 기저와 차원은 공간의 복잡도를 읽는 도구입니다.

## 핵심 용어 정리

- **선형결합**: 여러 벡터에 계수를 곱해 더한 표현입니다.
- **선형독립**: 한 벡터가 다른 벡터들의 선형결합으로 표현되지 않는 상태입니다.
- **기저**: 공간을 모두 생성하면서도 서로 독립인 벡터 집합입니다.
- **차원**: 기저에 포함된 벡터 개수입니다.
- **랭크**: 행렬의 독립적인 열 또는 행의 개수입니다.

## 기저 관련 개념 비교표

| 개념 | 정의 | 판별법 |
| --- | --- | --- |
| 생성(span) | 벡터 집합의 선형결합으로 만들 수 있는 모든 벡터 | 임의의 벡터를 주어진 집합의 선형결합으로 표현 가능한지 확인 |
| 선형독립 | 어떤 벡터도 나머지의 선형결합이 아님 | 계수가 모두 0일 때만 선형결합이 0이 되는지 확인 |
| 기저 | 생성하면서 독립인 벡터 집합 | 생성 조건 + 독립 조건 모두 만족 |
| 차원 | 기저의 원소 개수 | 최대 독립 벡터 개수 또는 랭크 |
| 랭크 | 행렬의 독립 열(또는 행) 개수 | `np.linalg.matrix_rank` 또는 SVD 이용 |

이 표를 기준으로 삼으면 다섯 개념이 따로 놀지 않고 하나의 구조로 연결됩니다.

## 읽기 전과 후

읽기 전에는 기저를 표준 단위벡터 정도로만 기억하기 쉽습니다. 그러면 공간마다 축이 하나로 정해져 있다고 오해하게 됩니다.

읽은 후에는 같은 공간이라도 여러 기저로 표현할 수 있고, 차원은 그 선택과 별개로 필요한 독립 방향의 수라는 점이 분명해집니다.

## 다섯 단계로 기저와 차원 읽기

### 1단계 — 표준기저

```python
import numpy as np
e1 = np.array([1.0, 0.0])
e2 = np.array([0.0, 1.0])
print("e1, e2:", e1, e2)
# 표준기저는 가장 익숙한 좌표계
```

가장 익숙한 기저부터 시작합니다. 2차원 평면에서는 두 단위벡터가 표준기저 역할을 합니다.

### 2단계 — 선형결합

```python
v = 3 * e1 + 4 * e2
print("v:", v)  # [3. 4.]
# 기저를 알면 임의의 벡터를 고유하게 표현할 수 있음
```

기저를 안다는 말은 그 기저를 이용해 임의의 벡터를 표현할 수 있다는 뜻입니다.

### 3단계 — 랭크로 독립성 보기

```python
A = np.column_stack([e1, e2])
print("rank:", np.linalg.matrix_rank(A))  # 2
```

랭크는 독립적인 방향이 실제로 몇 개인지 알려 줍니다. 여기서는 두 벡터가 독립이므로 랭크가 2입니다.

### 4단계 — 종속 예시

```python
B = np.column_stack([np.array([1.0, 2.0]), np.array([2.0, 4.0])])
print("rank:", np.linalg.matrix_rank(B))  # 1
# 두 번째 벡터가 첫 번째 벡터의 두 배 → 새로운 방향 없음
```

두 번째 벡터가 첫 번째 벡터의 두 배이므로 새로운 방향을 추가하지 못합니다.

### 5단계 — 다른 기저에서 좌표 구하기

```python
b1 = np.array([1.0, 1.0])
b2 = np.array([1.0, -1.0])
B_mat = np.column_stack([b1, b2])
v = np.array([3.0, 4.0])
coords = np.linalg.solve(B_mat, v)
print("coords in {b1,b2}:", coords)  # [3.5, -0.5]
# 같은 벡터, 다른 기저 → 다른 좌표
```

같은 벡터라도 기저가 바뀌면 좌표가 바뀝니다. 이 단계가 기저를 선택이라는 관점으로 이해하는 데 중요합니다.

## 랭크와 영공간 계산하기

랭크와 영공간을 직접 확인하면 독립성과 차원의 의미가 더 또렷해집니다.

```python
import numpy as np

A = np.array([
    [1.0, 2.0, 3.0],
    [2.0, 4.0, 6.0],
    [0.0, 1.0, 2.0],
])

rank = np.linalg.matrix_rank(A)
print('rank(A):', rank)  # 2 (두 번째 행이 첫 번째 행의 2배)

# 영공간 계산: Ax=0의 해 공간
U, S, Vt = np.linalg.svd(A)
null_mask = S < 1e-10
null_space = Vt[null_mask, :]

print('null space dim:', null_space.shape[0])
print('null space basis:\n', null_space)

# 검증: A @ v ≈ 0
if null_space.shape[0] > 0:
    v = null_space[0]
    result = A @ v
    print('A @ v:', result)
    print('close to zero:', np.allclose(result, 0))
```

랭크가 3보다 작으면 영공간 차원이 0보다 큽니다. 차원 정리(rank-nullity theorem)에 따라 랭크 + 영공간 차원 = 열 개수입니다.

## 기저 선택이 표현 품질에 미치는 영향

같은 벡터라도 기저에 따라 좌표가 달라집니다.

```python
import numpy as np

v = np.array([4.0, 1.0])

E = np.eye(2)
B = np.column_stack([
    np.array([1.0, 1.0]),
    np.array([-1.0, 1.0]),
])

coord_E = np.linalg.solve(E, v)
coord_B = np.linalg.solve(B, v)

print('표준기저 좌표:', coord_E)    # [4.0, 1.0]
print('B 기저 좌표:', coord_B)      # [2.5, -1.5]
print('B 기저로 복원:', B @ coord_B)  # [4.0, 1.0] 다시 원래 벡터
```

벡터 자체는 같지만 계수 표현이 바뀝니다. 즉 기저 변경은 데이터 자체 변경이 아니라 표현 체계 변경입니다.

## 랭크, 차원, 정보량

피처가 많아도 독립 방향이 적으면 실제 정보량은 낮습니다.

```python
import numpy as np

X = np.array([
    [1.0, 2.0, 3.0],
    [2.0, 4.0, 6.0],
    [0.0, 1.0, 1.0],
])

print('rank(X) =', np.linalg.matrix_rank(X))  # 2, 형상은 (3,3)이지만
print('shape(X) =', X.shape)

# SVD로 실제 정보 차원 파악
U, S, Vt = np.linalg.svd(X, full_matrices=False)
print('singular values:', S)
print('정보를 담는 축 수:', np.sum(S > 1e-10))
```

형상은 `(3, 3)`이지만 랭크는 더 작을 수 있습니다. 이는 역행렬 불가능성, 다중공선성, 불안정 회귀해의 원인과 직접 연결됩니다.

## 차원 축소의 수학적 의미

차원 축소는 단순히 피처를 줄이는 작업이 아닙니다. 기저 변경과 정보 압축의 조합으로 이해해야 합니다.

```python
import numpy as np

rng = np.random.default_rng(42)
X = rng.normal(size=(100, 5))
Xc = X - X.mean(axis=0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)

k = 2
X_compressed = Xc @ Vt[:k].T
X_reconstructed = X_compressed @ Vt[:k]

reconstruction_error = np.linalg.norm(Xc - X_reconstructed) / np.linalg.norm(Xc)
explained = (S[:k]**2).sum() / (S**2).sum()

print('상대 재구성 오차:', reconstruction_error)
print('분산 설명률:', explained)
```

차원 축소의 수학적 의미는 결국 "정보 손실을 관리하면서 표현을 간결하게 만드는 기저 선택"입니다.

## 응용 연결표

| 개념 | 실무 질문 | 점검 방법 |
| --- | --- | --- |
| 선형독립 | 피처가 중복되는가? | rank, condition number |
| 기저 변경 | 더 해석 쉬운 좌표가 있는가? | 직교기저/PCA 기저 비교 |
| 차원 | 실제 정보 축이 몇 개인가? | 누적 분산, 저랭크 근사 |
| 영공간 | 정보를 잃는 방향이 있는가? | SVD 소특이값 확인 |

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 랭크 부족 행렬에 역행렬 요청 | `LinAlgError` 또는 `inf`/`nan` | `matrix_rank` 먼저 확인, `lstsq` 사용 |
| 기저가 유일하다고 오해 | PCA 결과 부호 혼동 | 같은 공간도 무한히 많은 기저가 있음 인식 |
| 차원과 행렬 크기를 동일시 | 형상 `(n, m)`을 차원으로 착각 | 차원 = 랭크 = 독립 방향의 수 |
| 선형독립 여부를 눈대중으로 판단 | 미세한 선형종속 見落 | `matrix_rank` 또는 `det`으로 수치 확인 |
| 부동소수점 오차 무시 후 랭크 단정 | 거의 종속인 벡터도 독립으로 오판 | 절댓값 기준 임계값(tol) 명시 |

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 피처 공간을 볼 때 실제 정보 차원이 얼마나 되는지 먼저 봅니다. 열이 많아도 독립적인 방향이 적다면 모델은 불안정해지고 해석도 어려워집니다. 이때 랭크, 조건수, PCA 같은 도구가 함께 등장합니다.

또한 기저를 바꾸는 일이 곧 표현을 바꾸는 일이라는 점을 잘 압니다. PCA가 새로운 기저를 찾는 작업이라는 설명도, 결국 원래 좌표계보다 더 설명력이 좋은 축을 고르는 과정으로 읽습니다.

## 운영 체크리스트

- [ ] 선형독립을 설명할 수 있습니다.
- [ ] 랭크와 차원의 관계를 설명할 수 있습니다.
- [ ] 같은 공간을 여러 기저로 표현할 수 있다는 점을 이해했습니다.
- [ ] 다른 기저에서 좌표를 구하는 이유를 말할 수 있습니다.

## 연습 문제

1. 왜 2차원 공간에서 벡터 세 개가 모두 선형독립일 수 없는지 설명해 보세요.
2. 2x3 행렬의 최대 랭크가 왜 2인지 말해 보세요.
3. `[3, 4]`를 다른 기저에서 표현하는 예를 하나 직접 만들어 보세요.

## 정리와 다음 글

기저는 공간을 설명하는 축의 선택이고, 차원은 그 축이 몇 개 필요한지 말해 줍니다. 랭크는 행렬 안에 실제로 살아 있는 독립 방향의 개수를 알려 주며, 선형독립은 이 모든 판단의 바탕입니다. 이 연결이 잡히면 공간의 복잡도를 숫자와 구조로 함께 읽을 수 있습니다.

다음 글에서는 고유값과 고유벡터를 다룹니다. 공간을 표현하는 축을 이해했다면, 이제 어떤 변환 아래에서 특별히 방향이 보존되는 축이 무엇인지 볼 차례입니다.

## 처음 질문으로 돌아가기

- **어떤 벡터 집합이 공간을 충분히 설명한다는 말은 무슨 뜻일까요?**
  - 어떤 공간의 임의의 벡터를 그 집합의 선형결합으로 표현할 수 있다는 뜻입니다. 즉 그 집합이 공간을 "생성(span)"한다고 말합니다. 여기에 선형독립까지 만족하면 기저가 됩니다.

- **선형독립은 왜 기저의 핵심 조건일까요?**
  - 선형독립이 깨지면 중복된 방향이 생겨 같은 벡터를 여러 방식으로 표현할 수 있게 됩니다. 그러면 좌표가 유일하지 않아 기저의 역할을 못 합니다. 또한 랭크가 부족해 역행렬이 존재하지 않습니다.

- **차원과 랭크는 어떻게 연결될까요?**
  - 차원은 공간을 표현하는 데 필요한 독립 축의 수이고, 랭크는 행렬이 실제로 담고 있는 독립 방향의 수입니다. 행렬의 랭크가 작다는 것은 그 행렬이 만드는 출력 공간의 차원이 입력 공간보다 작다는 뜻입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linear Algebra 101 (1/10): 선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): 벡터](./02-vectors.md)
- [Linear Algebra 101 (3/10): 행렬](./03-matrices.md)
- [Linear Algebra 101 (4/10): 내적과 거리](./04-inner-product-and-distance.md)
- [Linear Algebra 101 (5/10): 선형변환](./05-linear-transformation.md)
- **Linear Algebra 101 (6/10): 기저와 차원 (현재 글)**
- [Linear Algebra 101 (7/10): 고유값과 고유벡터](./07-eigenvalues-and-eigenvectors.md)
- [Linear Algebra 101 (8/10): 행렬 분해](./08-matrix-decomposition.md)
- [Linear Algebra 101 (9/10): PCA](./09-pca.md)
- [머신러닝에서의 선형대수](./10-linear-algebra-in-ml.md)

<!-- toc:end -->

## 참고 자료

- 시리즈 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/linear-algebra-101/ko
- [3Blue1Brown — Basis vectors](https://www.3blue1brown.com/lessons/span)
- [Wikipedia — Basis (linear algebra)](https://en.wikipedia.org/wiki/Basis_(linear_algebra))
- [Wikipedia — Rank (linear algebra)](https://en.wikipedia.org/wiki/Rank_(linear_algebra))
- [NumPy — matrix_rank](https://numpy.org/doc/stable/reference/generated/numpy.linalg.matrix_rank.html)

Tags: LinearAlgebra, Basis, Dimension, DataScience, Beginner

---
series: linear-algebra-101
episode: 8
title: "Linear Algebra 101 (8/10): 행렬 분해"
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
  - Decomposition
  - SVD
  - DataScience
  - Beginner
seo_description: LU, QR, 고유분해, SVD를 언제 왜 쓰는지 한 흐름으로 정리합니다
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (8/10): 행렬 분해

행렬을 직접 다루다 보면 곧 한계를 만납니다. 역행렬을 바로 구하는 방식은 느리거나 불안정할 수 있고, 문제에 따라 더 적합한 계산 경로가 따로 있습니다. 이때 등장하는 것이 행렬 분해입니다. 복잡한 행렬을 해석 가능한 조각으로 나누어 계산을 더 안정적으로 만드는 방법입니다.

이 글은 Linear Algebra 101 시리즈의 8번째 글입니다.

여기서는 LU, QR, 고유분해, SVD를 같은 지도 위에서 정리해 보겠습니다.

![Linear Algebra 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/08/08-01-concept-at-a-glance.ko.png)
*Linear Algebra 101 8장 흐름 개요*
> 행렬 분해는 다양한 수치 계산 문제를 푸는 열쇠입니다. 상황에 맞는 분해를 선택해야 안정적이고 효율적인 계산을 할 수 있습니다.

## 이 글에서 다룰 문제

- 왜 역행렬보다 분해를 먼저 떠올려야 할까요?
- LU, QR, 고유분해, SVD는 각각 어디에 잘 맞을까요?
- 모든 분해가 모든 행렬에 적용되는 것은 아닐까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

선형방정식 풀이, 최소제곱, 차원 축소, 이미지 압축, 추천 시스템의 행렬분해는 모두 어떤 형태로든 분해를 사용합니다. 수치 선형대수에서는 문제에 맞는 분해를 선택하는 것이 정확도와 속도를 함께 좌우합니다.

실무에서 특히 중요한 이유는 안정성입니다. `inv`를 바로 쓰는 코드는 짧아 보여도 수치적으로 약할 수 있습니다. 반대로 적절한 분해를 쓰면 더 안정적이고 해석도 쉬워집니다. 행렬 분해는 계산 트릭이 아니라 설계 선택입니다.

이 네 분해는 서로 경쟁 관계라기보다 역할 분담에 가깝습니다. 어떤 문제는 LU가 맞고, 어떤 문제는 QR이나 SVD가 훨씬 자연스럽습니다.

- LU 분해: 하삼각행렬과 상삼각행렬의 곱으로 나누는 방식입니다.
- QR 분해: 직교행렬과 상삼각행렬의 곱으로 표현하는 방식입니다.
- 고유분해: 대각화 가능한 경우 `V D V^-1` 형태로 쓰는 방식입니다.
- SVD: 모든 행렬에 대해 적용 가능한 가장 일반적인 분해 중 하나입니다.
- 특이값: SVD의 대각 성분으로, 항상 0 이상입니다.

## 읽기 전과 후

읽기 전에는 역행렬로 모든 문제를 풀고 싶어집니다. 공식이 간단해 보이기 때문입니다.

읽은 후에는 문제에 맞는 분해를 골라야 한다는 감각이 생깁니다. 같은 행렬이라도 어떤 질문을 던지느냐에 따라 좋은 분해가 달라집니다.

## 분해 방식 비교표

| 분해 | 조건 | 주요 용도 | 계산 복잡도 |
| --- | --- | --- | --- |
| LU | 정방행렬 (피벗 피팅 시 일반화) | 선형 연립방정식 반복 풀이 | O(n³) |
| QR | 임의의 m×n | 최소제곱, 직교화, 고유값 반복 | O(mn²) |
| SVD | 임의의 m×n | 차원 축소, 저랭크 근사, 노이즈 제거 | O(min(m²n, mn²)) |
| 고유분해 | 대각화 가능 정방행렬 | 변환 모드 분석, 반복 시스템 | O(n³) |
| Cholesky | 대칭 양의 정부호 | 공분산 샘플링, 정규방정식 | O(n³/3) |

## 다섯 단계로 분해 읽기

### 1단계 — LU 분해

```python
import numpy as np
from scipy.linalg import lu
A = np.array([[4.0, 3.0], [6.0, 3.0]])
P, L, U = lu(A)
print("L:\n", L)
print("U:\n", U)
print("P @ A == L @ U:", np.allclose(P @ A, L @ U))
```

LU 분해는 방정식 풀이에서 자주 쓰입니다. `P @ A = L @ U` 관계를 먼저 검증하는 습관이 중요합니다. 삼각행렬 구조 덕분에 같은 `A`로 여러 번 방정식을 풀 때 LU를 미리 해 두고 재사용할 수 있습니다.

### 2단계 — QR 분해

```python
Q, R = np.linalg.qr(A)
print("Q^T Q ~ I:", np.allclose(Q.T @ Q, np.eye(2)))
print("A == Q @ R:", np.allclose(A, Q @ R))
```

QR 분해는 최소제곱 문제와 직교 기저를 다룰 때 특히 유용합니다. 직교 구조 덕분에 수치적으로 해석이 편한 경우가 많습니다. `lstsq`는 내부적으로 QR 또는 SVD를 사용합니다.

### 3단계 — 고유분해

```python
vals, vecs = np.linalg.eig(A)
print("vals:", vals)
# 재구성: A = V D V^(-1)
A_recon = vecs @ np.diag(vals) @ np.linalg.inv(vecs)
print("A == V D V^-1:", np.allclose(A, A_recon.real))
```

고유분해는 변환의 자연스러운 축을 찾고 싶을 때 의미가 큽니다. 다만 모든 행렬에 그대로 적용되는 것은 아닙니다. 결함 행렬이나 비대칭 행렬에서는 복소수 결과가 나올 수 있습니다.

### 4단계 — SVD

```python
U_svd, S_svd, Vt_svd = np.linalg.svd(A, full_matrices=False)
print("singular values:", S_svd)
print("A == U S Vt:", np.allclose(A, U_svd @ np.diag(S_svd) @ Vt_svd))
```

SVD는 가장 범용적인 분해입니다. 직사각형 행렬에도 적용되고, 차원 축소와 저랭크 근사에도 직접 연결됩니다. 특이값은 항상 0 이상이고 내림차순으로 정렬됩니다.

### 5단계 — 저랭크 SVD로 행렬 압축

```python
k = 1
A_k = U_svd[:, :k] @ np.diag(S_svd[:k]) @ Vt_svd[:k, :]
rel_err = np.linalg.norm(A - A_k) / np.linalg.norm(A)
print(f"rank-{k} relative error:", rel_err)
```

재구성은 분해 결과를 확인하는 가장 직접적인 방법입니다. 상위 특이값 `k`개만 남기면 행렬의 저랭크 근사를 얻을 수 있고, 상대 오차로 압축 품질을 측정할 수 있습니다.

## 작은 수치 예시로 다시 보기

- LU 분해는 원래 행렬을 삼각행렬 두 개로 바꿔 방정식 풀이를 단순하게 만듭니다.
- QR 분해에서는 `Q.T @ Q`가 항등행렬에 가깝게 나옵니다. 직교 구조가 살아 있다는 뜻입니다.
- SVD 재구성에서 `np.allclose(A_reconstructed, A)`가 `True`면 분해가 원래 행렬을 정확히 설명하고 있다는 뜻입니다.
- 저랭크 근사의 상대 오차는 떨어뜨린 특이값 에너지 비율로 해석할 수 있습니다.

## 분해 선택을 문제 유형에 맞추는 실전 규칙

행렬 분해는 이름을 아는 것보다 선택 기준이 중요합니다. 아래는 같은 행렬에 대해 LU, QR, SVD를 나란히 확인하는 예시입니다.

```python
import numpy as np
from scipy.linalg import lu

A = np.array([
    [3.0, 1.0, 1.0],
    [1.0, 3.0, 1.0],
    [1.0, 1.0, 3.0],
])

P, L, U = lu(A)
Q, R = np.linalg.qr(A)
U_svd, S_svd, Vt_svd = np.linalg.svd(A)

print('LU check:', np.allclose(P @ A, L @ U))
print('QR check:', np.allclose(A, Q @ R))
print('SVD check:', np.allclose(A, U_svd @ np.diag(S_svd) @ Vt_svd))
print('singular values:', S_svd)
print('condition number:', S_svd[0] / S_svd[-1])
```

검증 관점에서 세 분해 모두 "재구성 가능"이 핵심입니다. 다만 목적이 다릅니다.

## 언제 무엇을 우선할까

| 문제 | 1순위 분해 | 이유 |
| --- | --- | --- |
| `Ax=b` 반복 풀이 | LU | 삼각행렬 전진/후진 대입 효율 |
| 최소제곱 `min ||Ax-b||` | QR 또는 SVD | 직교 구조로 안정성 우수 |
| 차원 축소/압축 | SVD | 저랭크 근사와 직접 연결 |
| 대칭행렬 모드 분석 | 고유분해(`eigh`) | 축 해석이 명확, 실수 보장 |
| 공분산 샘플링 | Cholesky | 대칭 양의 정부호에서 절반 비용 |

## SVD로 행렬 압축하기: 상위 특이값만 남기기

```python
import numpy as np

# 간단한 그레이스케일 이미지 시뮬레이션 (64x64)
rng = np.random.default_rng(77)
img = rng.normal(size=(64, 64))

U, S, Vt = np.linalg.svd(img, full_matrices=False)

for k in [5, 10, 20]:
    img_k = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
    rel_error = np.linalg.norm(img - img_k) / np.linalg.norm(img)
    # 저장량 = 64*k + k + 64*k (U열, S원소, Vt행)
    compression_ratio = (64 * k + k + 64 * k) / (64 * 64)
    print(f'k={k:2d}: rel_err={rel_error:.4f}, compression={compression_ratio:.2%}')
```

특이값이 큰 순서대로 정렬되어 있으므로, 상위 몇 개만 남겨도 구조를 어느 정도 유지할 수 있습니다. 실제 사진에서는 자연 이미지의 저주파 구조 덕분에 더 높은 압축률로도 시각적 품질을 유지할 수 있습니다.

## SVD와 추천 시스템의 연결

SVD는 이미지 압축뿐 아니라 협업 필터링 기반 추천 시스템에도 쓰입니다. 사용자-아이템 평점 행렬 `R`을 저랭크로 근사하면 잠재 요인(latent factor)을 추출할 수 있기 때문입니다.

```python
import numpy as np

# 사용자 5명 x 아이템 4개 평점 행렬 (결측 없는 간단한 예시)
rng = np.random.default_rng(42)
R = np.array([
    [5.0, 3.0, 0.0, 1.0],
    [4.0, 0.0, 4.0, 1.0],
    [1.0, 1.0, 0.0, 5.0],
    [1.0, 0.0, 0.0, 4.0],
    [0.0, 1.0, 5.0, 4.0],
])

U, S, Vt = np.linalg.svd(R, full_matrices=False)
k = 2

# 저랭크 근사로 평점 예측
R_k = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
rel_err = np.linalg.norm(R - R_k) / np.linalg.norm(R)
print('top-2 singular values:', S[:k])
print('relative error:', rel_err)
print('predicted ratings (rank-2 approx):\n', R_k.round(1))
```

여기서 `U[:, :k]`는 사용자 잠재 벡터, `Vt[:k, :]`는 아이템 잠재 벡터를 나타냅니다. 평점이 없는 항목은 잠재 벡터 내적으로 예측할 수 있습니다. 실무에서는 희소 행렬에 경사하강법으로 잠재 요인을 학습하는 방식을 쓰지만, 그 아이디어의 뿌리는 SVD의 저랭크 근사와 같습니다.

## 이 코드에서 먼저 볼 점

- 분해마다 잘 맞는 문제 유형이 다릅니다.
- SVD는 모든 행렬에 적용할 수 있습니다.
- 재구성은 좋은 검증 방법입니다.
- 수치 계산에서는 분해가 역행렬보다 안정적인 경우가 많습니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| `inv`로 직접 선형계 풀기 | 조건수 불량 행렬에서 오차 증폭 | `np.linalg.solve` 또는 `lstsq` 사용 |
| 직사각형 행렬에 LU 바로 적용 | 형상 불일치 오류 | QR 또는 SVD로 대체 |
| 특이값 정렬 가정 누락 | 상위 `k` 선택 시 순서 착오 | SVD 결과는 항상 내림차순 정렬 확인 |
| `==`로 부동소수점 비교 | 수치 오차로 인한 False 반환 | `np.allclose(A, B, atol=1e-10)` 사용 |
| QR과 SVD 혼용 | 최소제곱과 저랭크 근사를 같은 도구로 처리 | 문제 유형에 따라 분해 선택 명확히 구분 |

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 먼저 문제 유형을 묻습니다. 연립방정식인가, 최소제곱인가, 차원 축소인가, 저랭크 근사인가에 따라 도구가 달라져야 하기 때문입니다. 분해는 계산 도구이면서 문제 분류 도구이기도 합니다.

또한 안정성과 비용을 함께 봅니다. SVD는 강력하지만 비쌀 수 있고, LU는 빠르지만 모든 상황에 맞지 않습니다. 좋은 선택은 가장 유명한 분해를 고르는 것이 아니라, 지금 문제에 가장 적합한 분해를 고르는 것입니다.

## 실전 확장 노트: 분해 선택과 검증 파이프라인

분해 기반 계산에서는 결과 검증과 수치 안정성 점검이 실무 품질을 결정합니다. 아래 루틴은 `inv` 대신 `solve`와 분해를 쓰는 이유를 수치로 직접 확인하는 예시입니다.

```python
import numpy as np
from scipy.linalg import lu

rng = np.random.default_rng(99)
A = rng.normal(size=(5, 5))
b = rng.normal(size=5)

# 방법 1: inv (비권장)
x_inv = np.linalg.inv(A) @ b

# 방법 2: solve (LU 내부 사용)
x_solve = np.linalg.solve(A, b)

# 방법 3: lstsq (SVD 내부 사용)
x_lstsq, _, _, _ = np.linalg.lstsq(A, b, rcond=None)

print('inv residual:', np.linalg.norm(A @ x_inv - b))
print('solve residual:', np.linalg.norm(A @ x_solve - b))
print('lstsq residual:', np.linalg.norm(A @ x_lstsq - b))
print('condition number:', np.linalg.cond(A))

# SVD 저랭크 근사 품질 점검
U, S, Vt = np.linalg.svd(A, full_matrices=False)
for k in range(1, 5):
    A_k = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
    err = np.linalg.norm(A - A_k) / np.linalg.norm(A)
    print(f'rank-{k} err: {err:.4f}')
```

반드시 확인할 항목은 세 가지입니다.

1. **잔차 비교**: `solve` 잔차가 `inv` 잔차보다 작거나 같아야 합니다.
2. **조건수**: `cond(A)`가 크면(`1e6` 이상) 역행렬 방법은 피해야 합니다.
3. **특이값 스펙트럼**: 급격히 작아지는 지점이 합리적인 저랭크 `k` 후보입니다.

## 운영 체크리스트

- [ ] LU, QR, 고유분해, SVD의 쓰임새를 구분할 수 있습니다.
- [ ] 분해 결과를 재구성으로 검증할 수 있습니다.
- [ ] 역행렬보다 분해가 안정적인 이유를 설명할 수 있습니다.
- [ ] SVD가 왜 범용적인지 이해했습니다.
- [ ] 저랭크 근사의 상대 오차를 계산할 수 있습니다.

## 연습 문제

1. 3x2 직사각형 행렬의 SVD를 구하고 각 결과의 형상을 확인해 보세요.
2. 최소제곱 문제를 QR 분해로 푸는 방법을 정리해 보세요.
3. 저랭크 SVD로 원래 행렬을 근사하고 `k`별 오차를 측정해 보세요.
4. `np.linalg.solve`와 `inv @ b`의 잔차를 조건수가 큰 행렬에서 비교해 보세요.

## 정리와 다음 글

행렬 분해는 선형대수 계산을 실제로 작동하게 만드는 핵심 도구입니다. LU는 방정식 풀이에, QR은 최소제곱에, 고유분해는 축 해석에, SVD는 가장 일반적인 분해와 근사에 강합니다. 중요한 것은 이름을 나열하는 것이 아니라 문제에 맞는 분해를 고르는 감각입니다.

다음 글에서는 PCA를 다룹니다. 행렬 분해, 특히 SVD가 실제 데이터 차원 축소로 어떻게 이어지는지 가장 대표적인 예를 통해 봅니다.

## 처음 질문으로 돌아가기

- **왜 역행렬보다 분해를 먼저 떠올려야 할까요?**
  - 역행렬은 수학적으로 깔끔하지만 수치 계산에서는 위험할 수 있습니다. 조건수가 큰 행렬에서 `inv`는 작은 입력 오차를 크게 증폭시킵니다. LU, QR, SVD는 수치적으로 훨씬 안정적이고, 같은 결과를 더 적은 비용으로 얻을 수 있습니다.
- **LU, QR, 고유분해, SVD는 각각 어디에 잘 맞을까요?**
  - LU는 정방행렬 선형방정식을 반복 풀 때, QR은 최소제곱과 직교화에, 고유분해는 변환의 모드 분석과 반복 시스템에, SVD는 직사각형 행렬을 포함한 저랭크 근사와 차원 축소에 가장 잘 맞습니다.
- **모든 분해가 모든 행렬에 적용되는 것은 아닐까요?**
  - 맞습니다. LU는 정방행렬이 원칙이고, 고유분해는 대각화 가능한 행렬에만 쓸 수 있습니다. Cholesky는 대칭 양의 정부호 행렬에만 적용됩니다. SVD와 QR만 임의의 `m×n` 행렬에 항상 적용 가능합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linear Algebra 101 (1/10): 선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): 벡터](./02-vectors.md)
- [Linear Algebra 101 (3/10): 행렬](./03-matrices.md)
- [Linear Algebra 101 (4/10): 내적과 거리](./04-inner-product-and-distance.md)
- [Linear Algebra 101 (5/10): 선형변환](./05-linear-transformation.md)
- [Linear Algebra 101 (6/10): 기저와 차원](./06-basis-and-dimension.md)
- [Linear Algebra 101 (7/10): 고유값과 고유벡터](./07-eigenvalues-and-eigenvectors.md)
- **Linear Algebra 101 (8/10): 행렬 분해 (현재 글)**
- [Linear Algebra 101 (9/10): PCA](./09-pca.md)
- [머신러닝에서의 선형대수](./10-linear-algebra-in-ml.md)

<!-- toc:end -->

## 참고 자료

- 시리즈 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/linear-algebra-101/ko
- [Wikipedia — Matrix decomposition](https://en.wikipedia.org/wiki/Matrix_decomposition)
- [Wikipedia — Singular value decomposition](https://en.wikipedia.org/wiki/Singular_value_decomposition)
- [NumPy — linalg.svd](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html)
- [SciPy — linalg.lu](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lu.html)

Tags: LinearAlgebra, Decomposition, SVD, DataScience, Beginner

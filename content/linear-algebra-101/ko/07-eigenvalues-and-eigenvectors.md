---
series: linear-algebra-101
episode: 7
title: "Linear Algebra 101 (7/10): 고유값과 고유벡터"
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
  - Eigenvalues
  - Eigenvectors
  - DataScience
  - Beginner
seo_description: 고유값과 고유벡터를 변환의 축과 확대율 관점에서 정의하고 PCA나 페이지랭크 같은 실무 문제와 어떻게 연결되는지 설명합니다.
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (7/10): 고유값과 고유벡터

선형변환을 여러 번 적용해 보면 어떤 방향은 유독 특별하게 남습니다. 다른 방향은 비틀리고 섞이는데, 어떤 방향은 방향 자체는 유지한 채 길이만 바뀝니다. 고유값과 고유벡터는 바로 이 특별한 축을 설명하는 도구입니다.

이 글은 Linear Algebra 101 시리즈의 7번째 글입니다.

여기서는 고유값과 고유벡터를 변환의 자연스러운 축이라는 관점으로 읽어 보겠습니다.

![Linear Algebra 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/07/07-01-concept-at-a-glance.ko.png)
*Linear Algebra 101 7장 흐름 개요*
> 고유값과 고유벡터는 선형변환의 본질입니다. 고유벡터는 변환 후에도 방향이 같고, 고유값은 그 방향에서의 확대율입니다.

## 이 글에서 다룰 문제

- 행렬을 반복해서 적용할 때 왜 어떤 방향은 유지될까요?
- 고유벡터와 고유값은 각각 무엇을 뜻할까요?
- 대칭행렬에서 결과가 특히 깔끔해지는 이유는 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

고유분해는 행렬을 더 단순한 좌표계에서 읽게 해 줍니다. 복잡한 변환도 적절한 축을 찾으면 축별 확대와 축소처럼 간단한 모습으로 바뀔 수 있습니다. 그래서 PCA, 안정성 분석, PageRank 같은 주제에서 반복해서 등장합니다.

특히 변환을 해석하고 싶을 때 고유값과 고유벡터는 매우 강력합니다. 이 도구가 있으면 행렬 전체를 한꺼번에 보지 않고도, 어떤 방향이 지배적인지, 어떤 모드가 커지고 작아지는지 읽을 수 있습니다.

`A v = lambda v`는 고유값 문제의 핵심 문장입니다. 행렬 `A`를 적용해도 방향은 `v` 그대로이고 길이만 `lambda`배 바뀝니다.

- 고유벡터: `A v = lambda v`를 만족하는 0이 아닌 벡터입니다.
- 고유값: 그 방향에서의 확대 또는 축소 비율입니다.
- 고유분해: 가능한 경우 행렬을 `V D V^-1` 형태로 분해하는 방식입니다.
- 스펙트럼: 행렬이 가진 모든 고유값 집합입니다.
- 대칭행렬: 실수 고유값과 서로 직교하는 고유벡터를 갖는 중요한 행렬 부류입니다.

## 읽기 전과 후

읽기 전에는 고유값을 공식으로 푸는 문제처럼 여기기 쉽습니다. 그러면 왜 중요한지 연결이 약합니다.

읽은 후에는 고유값과 고유벡터가 변환의 자연스러운 축을 찾는 도구라는 점이 보입니다. 변환을 가장 단순하게 읽을 수 있는 좌표계를 찾는 과정이라고 생각하면 훨씬 이해가 쉽습니다.

## 핵심 개념 비교표

| 개념 | 정의 | 특징 | 실무 연결 |
| --- | --- | --- | --- |
| 고유벡터 | `A v = λ v`를 만족하는 벡터 | 변환 후 방향 불변 | PCA 주성분 방향 |
| 고유값 | 고유벡터 방향의 확대 비율 | 실수 또는 복소수 | 분산 크기, 안정성 지표 |
| 스펙트럼 | 행렬의 모든 고유값 집합 | 크기 순 정렬 가능 | 시스템 모드 분석 |
| 고유분해 | `A = V D V⁻¹` | 대각화 가능 행렬에만 | 반복 변환 예측 |
| `eigh` | 대칭행렬 전용 분해 | 실수 고유값, 직교 고유벡터 | PCA, 공분산 분석 |

## 다섯 단계로 고유분해 읽기

### 1단계 — 행렬 정의

```python
import numpy as np
A = np.array([[2.0, 1.0], [0.0, 3.0]])
```

먼저 간단한 2x2 행렬을 준비합니다. 예제가 작을수록 고유벡터 검증 과정을 읽기 쉽습니다.

### 2단계 — 고유값과 고유벡터 계산

```python
vals, vecs = np.linalg.eig(A)
print("eigenvalues:", vals)
print("eigenvectors:\n", vecs)
```

NumPy는 고유값과 고유벡터를 함께 반환합니다. 각 열벡터가 하나의 고유벡터에 해당합니다.

### 3단계 — 식으로 검증

```python
for i in range(len(vals)):
    Av = A @ vecs[:, i]
    lv = vals[i] * vecs[:, i]
    print("A v == lambda v:", np.allclose(Av, lv))
```

고유분해는 결과를 반드시 검증해 보는 습관이 좋습니다. 계산된 벡터가 정말 정의를 만족하는지 직접 확인할 수 있기 때문입니다.

### 4단계 — 대칭행렬

```python
S = np.array([[2.0, 1.0], [1.0, 2.0]])
sv, svc = np.linalg.eigh(S)  # for symmetric/Hermitian
print("sym eigenvalues:", sv)
print("orthogonal? ", np.allclose(svc.T @ svc, np.eye(2)))
```

대칭행렬은 구조가 깔끔해서 고유벡터가 서로 직교합니다. 그래서 수치적으로도 다루기 더 편한 경우가 많습니다.

### 5단계 — 거듭제곱 반복과 지배 방향

```python
M = np.array([[0.9, 0.1], [0.2, 0.8]])
v = np.array([1.0, 0.0])
for _ in range(50):
    v = M @ v
    v = v / np.linalg.norm(v)
print("dominant direction:", v)
```

행렬을 반복해서 곱하면 보통 가장 큰 고유값 방향이 두드러집니다. 이 감각은 페이지랭크나 반복 알고리즘을 이해할 때 중요합니다.

## 작은 수치 예시로 다시 보기

- `[[2, 1], [0, 3]]`의 고유값은 `2`와 `3`입니다. 변환이 특별히 보존하는 축이 둘 있다는 뜻입니다.
- `np.allclose(A @ v, lambda * v)`가 `True`로 나오면 계산된 벡터가 실제 고유벡터라는 뜻입니다.
- 거듭제곱 반복을 계속하면 벡터는 지배적인 방향으로 수렴합니다. 이 예제에서는 대략 `[0.7, 0.7]` 근처 방향이 드러납니다.

## 고유값 분해의 기하학적 의미

고유값 분해는 단순히 행렬을 세 개로 쪼개는 기법이 아닙니다. 변환을 가장 자연스럽게 보이는 좌표계로 바꿔 읽는 방법입니다.

행렬 `A`가 고유분해 가능하면 `A = V D V^(-1)`로 쓸 수 있습니다. 이 식의 기하학적 해석은 이렇습니다:

1. **`V^(-1)`**: 표준 좌표계를 고유벡터 좌표계로 변환합니다.
2. **`D`**: 각 고유벡터 방향으로 고유값만큼 스케일링합니다.
3. **`V`**: 고유벡터 좌표계를 다시 표준 좌표계로 되돌립니다.

즉 복잡한 변환도 적절한 축에서 보면 단순한 스케일 변환이 됩니다. 회전과 찌그러짐이 섞여 있어도, 고유벡터 축에서는 각 방향이 독립적으로 확대 또는 축소될 뿐입니다.

이 관점은 특히 반복 적용할 때 강력합니다. `A^n = V D^n V^(-1)`이므로, 대각 행렬 `D`를 `n`제곱하는 것만으로 반복 변환 결과를 예측할 수 있습니다.

```python
# A^n = V D^n V^(-1) 검증
A = np.array([[2.0, 1.0], [1.0, 3.0]])
vals, vecs = np.linalg.eig(A)
n = 4
A_n_direct = np.linalg.matrix_power(A, n)
A_n_eig = vecs @ np.diag(vals ** n) @ np.linalg.inv(vecs)
print("matrix power matches:", np.allclose(A_n_direct, A_n_eig.real))
```

고유값 절댓값이 1보다 크면 해당 방향은 폭발하고, 1보다 작으면 수렴하며, 음수이면 방향이 반전됩니다. 이 규칙 하나로 반복 시스템의 장기 동작을 예측할 수 있습니다.

## 고유값 계산을 신뢰 가능한 절차로 만들기

고유값 문제는 결과 숫자보다 검증 루틴이 중요합니다. 아래 코드는 고유값/고유벡터 계산 후 잔차를 확인합니다.

```python
import numpy as np

A = np.array([
    [4.0, 1.0, 0.0],
    [1.0, 3.0, 0.0],
    [0.0, 0.0, 2.0],
])

vals, vecs = np.linalg.eigh(A)
print('eigenvalues:', vals)

for i in range(len(vals)):
    v = vecs[:, i]
    residual = np.linalg.norm(A @ v - vals[i] * v)
    print(f'i={i}, residual={residual:.3e}')
```

대칭행렬에서는 `eigh`를 쓰는 것이 일반적으로 더 안정적입니다. 잔차가 `1e-12` 수준이면 계산 신뢰도가 높다고 볼 수 있습니다. `eig`를 대칭행렬에 쓰면 복소수 결과가 나오거나 잔차가 커질 수 있습니다.

## 공분산 행렬 고유분해: 데이터 분산 구조 분석

고유값 분해는 데이터 분산 구조를 분석하는 데도 자주 쓰입니다. 공분산 행렬을 고유분해하면 데이터가 어느 방향으로 얼마나 퍼져 있는지 알 수 있습니다.

```python
import numpy as np

# 샘플 데이터 생성 (두 피처 간 상관 구조 부여)
rng = np.random.default_rng(42)
X = rng.normal(size=(200, 3))
X[:, 1] = X[:, 0] * 0.8 + rng.normal(scale=0.3, size=200)

# 공분산 행렬
Xc = X - X.mean(axis=0)
C = (Xc.T @ Xc) / (len(Xc) - 1)

# 고유값 분해 (대칭 행렬이므로 eigh 사용)
eigvals, eigvecs = np.linalg.eigh(C)

# 내림차순 정렬
idx = eigvals.argsort()[::-1]
eigvals = eigvals[idx]
eigvecs = eigvecs[:, idx]

print('고유값(분산):', eigvals)
print('분산 설명률:', eigvals / eigvals.sum())
print('직교성 확인:', np.allclose(eigvecs.T @ eigvecs, np.eye(3)))

# 재구성 검증: C = V Λ V^T
C_reconstructed = eigvecs @ np.diag(eigvals) @ eigvecs.T
print('재구성 오차:', np.linalg.norm(C - C_reconstructed))

# 주성분 방향으로 투영
X_pca = Xc @ eigvecs[:, :2]
print('투영 후 형상:', X_pca.shape)
```

공분산 행렬의 고유값은 각 주성분 방향의 분산을 나타냅니다. 고유값이 클수록 데이터가 그 방향으로 많이 퍼져 있다는 뜻입니다. 고유벡터가 직교하므로 새로운 좌표계에서는 축 간 상관이 사라집니다.

## 해석 표

| 신호 | 의미 | 실무 해석 |
| --- | --- | --- |
| 큰 절댓값 고유값 | 해당 모드의 강한 증폭/지배 | 불안정 가능성 또는 핵심 축 |
| 0에 가까운 고유값 | 정보 축소/평탄 모드 | 축소 가능 축 후보 |
| 음수 고유값(비대칭 행렬) | 방향 반전 모드 | 동적 시스템 불안정 신호 |
| 직교 고유벡터(대칭행렬) | 축 분리가 깔끔 | PCA, 분산 분해에 유리 |
| 복소 고유값 | 회전 성분 포함 | 진동 시스템에 나타남 |

## 고유값 활용 사례 비교표

| 활용 사례 | 고유값/고유벡터의 역할 |
| --- | --- |
| PCA | 공분산 행렬의 고유값이 분산, 고유벡터가 주성분 방향 |
| PageRank | 전이 행렬의 지배 고유벡터가 정상 분포(페이지 중요도) |
| 진동 분석 | 고유값이 고유 진동수의 제곱, 고유벡터가 모드 형상 |
| 안정성 분석 | 고유값 절댓값이 1보다 크면 불안정, 작으면 수렴 |
| 스펙트럼 클러스터링 | 그래프 라플라시안의 소고유값 고유벡터로 클러스터 분리 |

## 이 코드에서 먼저 볼 점

- 고유분해는 변환을 더 단순한 축으로 바꿔 읽게 해 줍니다.
- 대칭행렬에는 `eigh`를 쓰는 편이 안정적입니다.
- 반복 곱셈은 지배적인 방향을 드러낼 수 있습니다.
- 고유벡터는 부호와 스케일이 고정되지 않습니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 대칭행렬에 `eig` 사용 | 복소수 결과 또는 수치 불안정 | 대칭·에르미트 행렬에는 `eigh` 사용 |
| 모든 행렬이 대각화 가능하다고 가정 | 중복 고유값에서 고유벡터 부족 | 결함 행렬(defective matrix) 여부 확인 |
| 고유벡터 부호 고정 기대 | 부호만 다른 결과를 오류로 오해 | 부호와 스케일은 임의적임을 인지 |
| 복소 고유값 무시 | 비대칭 행렬에서 실수 결과 가정 | `.real` 사용 전 허수부 크기 점검 |
| 작은 행렬 결과를 대규모에 그대로 적용 | 수치 오차 누적으로 결과 틀림 | 조건수 확인 후 안정성 평가 |

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 고유분해를 공식 풀이보다 해석 도구로 먼저 봅니다. 어떤 방향이 시스템을 지배하는지, 어떤 모드가 안정적인지, 어떤 축이 가장 많은 분산을 설명하는지를 읽는 데 고유값과 고유벡터를 씁니다.

또한 행렬 구조를 먼저 확인합니다. 대칭행렬인지, 희소행렬인지, 꼭 전체 고유분해가 필요한지, 지배적인 몇 개만 필요한지에 따라 접근법이 달라지기 때문입니다. 좋은 선형대수 감각은 계산보다 해석 우선순위를 정하는 데서 드러납니다.

## 실전 확장 노트: 고유값 계산 루틴과 검증 체크포인트

고유값 계산을 실제 프로젝트에서 쓸 때는 계산 자체보다 검증 루틴이 더 중요합니다. 아래 절차는 공분산 분석부터 PCA 전처리까지 이어지는 공통 점검 흐름입니다.

```python
import numpy as np

rng = np.random.default_rng(7)
X = rng.normal(size=(100, 4))
X[:, 2] = 0.6 * X[:, 0] + 0.4 * rng.normal(size=100)

# 1) 중심화 및 공분산
Xc = X - X.mean(axis=0)
C = (Xc.T @ Xc) / (len(Xc) - 1)

# 2) 고유분해 (대칭 행렬이므로 eigh)
eigvals, eigvecs = np.linalg.eigh(C)
idx = eigvals.argsort()[::-1]
eigvals, eigvecs = eigvals[idx], eigvecs[:, idx]

# 3) 직교성 검증
assert np.allclose(eigvecs.T @ eigvecs, np.eye(4)), "직교성 실패"

# 4) 재구성 검증
C_recon = eigvecs @ np.diag(eigvals) @ eigvecs.T
print('재구성 오차:', np.linalg.norm(C - C_recon))

# 5) 잔차 점검
for i in range(4):
    v = eigvecs[:, i]
    res = np.linalg.norm(C @ v - eigvals[i] * v)
    print(f'잔차 [{i}]: {res:.2e}')

# 6) 분산 설명률
ratio = eigvals / eigvals.sum()
print('분산 설명률:', ratio)
print('누적:', ratio.cumsum())
```

반드시 확인할 항목은 네 가지입니다.

1. **직교성**: 대칭행렬의 고유벡터는 반드시 직교해야 합니다.
2. **재구성**: `V Λ V^T`가 원래 공분산과 일치해야 합니다.
3. **잔차**: 각 고유벡터 방향의 잔차가 `1e-12` 수준이어야 합니다.
4. **분산 설명률**: 누적 설명률로 `k` 선택 기준을 세웁니다.

## 운영 체크리스트

- [ ] 고유값과 고유벡터의 정의를 설명할 수 있습니다.
- [ ] `A v = lambda v`를 코드로 검증할 수 있습니다.
- [ ] 대칭행렬이 왜 특별한지 이해했습니다.
- [ ] 반복 곱셈이 지배적인 방향을 드러낼 수 있다는 점을 압니다.
- [ ] `eig`와 `eigh`의 차이를 구분할 수 있습니다.

## 연습 문제

1. `diag(2, 3)`의 고유값과 고유벡터를 직접 구해 보세요.
2. 대칭행렬의 고유벡터가 왜 직교하는지 예시로 확인해 보세요.
3. 거듭제곱 반복으로 가장 큰 고유값 방향을 추정해 보세요.
4. 공분산 행렬의 고유분해 결과로 `C = V Λ V^T`를 검증해 보세요.

## 정리와 다음 글

고유값과 고유벡터는 변환이 가장 자연스럽게 보이는 축을 찾아 줍니다. 어떤 방향은 유지되고 길이만 바뀐다는 사실을 잡아내면, 복잡한 행렬도 더 단순한 구조로 읽을 수 있습니다. 이 관점은 PCA, 반복 알고리즘, 안정성 해석의 공통 바탕이 됩니다.

다음 글에서는 행렬 분해를 다룹니다. 고유분해가 한 종류의 분해였다면, 이제 LU, QR, SVD처럼 문제에 따라 더 실용적으로 쓰이는 여러 분해 방식을 함께 정리해 보겠습니다.

## 처음 질문으로 돌아가기

- **행렬을 반복해서 적용할 때 왜 어떤 방향은 유지될까요?**
  - `A v = λ v`를 만족하는 방향(고유벡터)은 행렬을 아무리 반복 적용해도 방향 자체는 변하지 않습니다. `A^n v = λ^n v`이므로 길이만 `λ^n`배가 됩니다. 가장 큰 `|λ|`를 가진 방향이 반복 적용 시 지배적으로 드러나는 이유입니다.
- **고유벡터와 고유값은 각각 무엇을 뜻할까요?**
  - 고유벡터는 선형변환 후에도 방향이 바뀌지 않는 특별한 벡터입니다. 고유값은 그 방향에서의 확대/축소 비율로, 양수이면 같은 방향으로 확대되고, 음수이면 방향이 반전되며, 절댓값이 1보다 작으면 수축합니다.
- **대칭행렬에서 결과가 특히 깔끔해지는 이유는 무엇일까요?**
  - 대칭행렬(`A = A^T`)은 스펙트럼 정리에 의해 항상 실수 고유값을 가지며, 서로 다른 고유값에 대응하는 고유벡터는 반드시 직교합니다. 이 때문에 `A = V Λ V^T` 형태로 쓸 수 있어 역행렬 계산이 `V^T`로 대체되고, 수치 안정성도 높아집니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linear Algebra 101 (1/10): 선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): 벡터](./02-vectors.md)
- [Linear Algebra 101 (3/10): 행렬](./03-matrices.md)
- [Linear Algebra 101 (4/10): 내적과 거리](./04-inner-product-and-distance.md)
- [Linear Algebra 101 (5/10): 선형변환](./05-linear-transformation.md)
- [Linear Algebra 101 (6/10): 기저와 차원](./06-basis-and-dimension.md)
- **Linear Algebra 101 (7/10): 고유값과 고유벡터 (현재 글)**
- [Linear Algebra 101 (8/10): 행렬 분해](./08-matrix-decomposition.md)
- [Linear Algebra 101 (9/10): PCA](./09-pca.md)
- [머신러닝에서의 선형대수](./10-linear-algebra-in-ml.md)

<!-- toc:end -->

## 참고 자료

- 시리즈 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/linear-algebra-101/ko
- [3Blue1Brown — Eigenvectors and eigenvalues](https://www.3blue1brown.com/lessons/eigenvalues)
- [Wikipedia — Eigenvalues and eigenvectors](https://en.wikipedia.org/wiki/Eigenvalues_and_eigenvectors)
- [NumPy — linalg.eig](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eig.html)
- [NumPy — linalg.eigh](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigh.html)

Tags: LinearAlgebra, Eigenvalues, Eigenvectors, DataScience, Beginner

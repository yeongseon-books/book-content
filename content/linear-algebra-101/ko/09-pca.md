---
series: linear-algebra-101
episode: 9
title: "Linear Algebra 101 (9/10): PCA"
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
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (9/10): PCA

차원이 큰 데이터를 다루다 보면 모든 축이 똑같이 중요하지 않다는 사실을 곧 느끼게 됩니다. 어떤 축은 정보가 많이 담겨 있고, 어떤 축은 노이즈에 가깝습니다. PCA는 이 차이를 가장 고전적이고 명확한 방식으로 다루는 도구입니다.

이 글은 Linear Algebra 101 시리즈의 9번째 글입니다.

여기서는 PCA를 분산이 가장 큰 축을 찾고 그 축으로 데이터를 다시 표현하는 방법으로 이해해 보겠습니다.

![Linear Algebra 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/09/09-01-concept-at-a-glance.ko.png)
*Linear Algebra 101 9장 흐름 개요*
> PCA는 고유값과 고유벡터를 실제로 쓰는 가장 직관적인 사례입니다. 주성분은 데이터 변동이 가장 큰 축이고, 몇 개 주성분만으로도 데이터의 대부분 정보를 유지할 수 있습니다.

## 이 글에서 다룰 문제

- PCA는 왜 중요한 방향을 찾아낸다고 말할 수 있을까요?
- 공분산 관점과 SVD 관점은 어떻게 연결될까요?
- 왜 중심화가 빠지면 안 될까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

차원 축소, 시각화, 노이즈 제거, 피처 압축은 실무에서 자주 만나는 요구입니다. PCA는 이 문제를 가장 기본적인 선형대수 방식으로 풀어 줍니다. 특히 고차원 데이터를 먼저 가볍게 훑어 보고 싶을 때 매우 유용합니다.

또한 PCA는 앞에서 배운 기저, 고유값, SVD가 실제 데이터 문제에서 어떻게 합쳐지는지 보여 주는 좋은 예입니다. 주성분은 새로운 기저이고, 분산 설명률은 어떤 축이 얼마나 중요한지 알려 줍니다.

PCA의 핵심 흐름은 단순합니다. 먼저 평균을 빼서 중심화하고, 데이터의 분산이 큰 방향을 찾은 뒤, 상위 몇 개 축에 투영합니다. 남은 축의 수가 곧 줄인 차원입니다.

- 주성분: 분산이 큰 순서대로 정렬된 새로운 직교 축입니다.
- 분산 설명률: 각 주성분이 전체 분산 중 얼마나 설명하는지 나타내는 비율입니다.
- 공분산 행렬: 중심화된 데이터의 축 간 관계를 담는 행렬입니다.
- SVD 기반 PCA: 데이터 행렬을 SVD로 분해해 주성분을 얻는 방식입니다.
- 재구성 오차: 차원을 줄였다가 다시 복원했을 때 생기는 손실입니다.

## 읽기 전과 후

읽기 전에는 차원 축소를 단순히 피처 몇 개를 버리는 일로 보기 쉽습니다. 이 경우 정보 손실이 어떻게 관리되는지 설명하기 어렵습니다.

읽은 후에는 PCA가 데이터를 더 잘 설명하는 축으로 먼저 회전한 뒤, 중요한 축만 남기는 과정이라는 점이 보입니다. 즉 무작정 버리는 것이 아니라 구조를 다시 잡는 작업입니다.

## PCA 관련 개념 비교표

| 개념 | 역할 | 계산 방법 | 주의 사항 |
| --- | --- | --- | --- |
| 주성분 | 데이터 분산 최대화 방향 | 공분산 고유벡터 또는 SVD `V` | 부호가 임의적 |
| 분산 설명률 | 각 주성분이 담는 정보 비율 | 고유값 / 전체 고유값 합 | `k` 선택 기준 |
| 재구성 오차 | 압축 후 정보 손실량 | `||Xc - Z @ Vt[:k]||_F / ||Xc||` | 낮을수록 좋음 |
| 중심화 | 평균 편향 제거 | `Xc = X - X.mean(axis=0)` | 필수 전처리 |
| 표준화 | 피처 스케일 통일 | `(Xc) / std` | 스케일 차이 클 때 필수 |

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
print("mean after centering:", Xc.mean(axis=0))  # ~ [0, 0, 0]
```

중심화는 PCA에서 빠지면 안 됩니다. 평균이 남아 있으면 분산 구조 대신 위치 정보가 섞여 버립니다.

### 3단계 — SVD

```python
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
explained_ratio = (S**2) / (S**2).sum()
print("singular values:", S)
print("explained variance ratio:", explained_ratio)
print("cumulative:", explained_ratio.cumsum())
```

SVD를 통해 주성분과 분산 설명률을 얻을 수 있습니다. 특이값이 클수록 더 많은 분산을 설명합니다.

### 4단계 — 상위 2개 축으로 투영

```python
k = 2
X_2d = Xc @ Vt[:k].T
print("projected shape:", X_2d.shape)  # (100, 2)
```

상위 `k`개 축만 남기면 데이터 표현이 더 작아집니다. 이 단계가 실제 차원 축소입니다.

### 5단계 — 재구성 오차

```python
X_rec = X_2d @ Vt[:k]
err = np.linalg.norm(Xc - X_rec) / np.linalg.norm(Xc)
print("relative reconstruction error:", err)
```

차원을 줄인 만큼 정보 손실도 생깁니다. 재구성 오차는 그 손실을 숫자로 보여 줍니다.

## 작은 수치 예시로 다시 보기

- 투영 결과 `X_2d.shape`는 `(100, 2)`가 됩니다. 3차원 표현이 2차원으로 줄어든 셈입니다.
- 분산 설명률은 특이값 제곱의 비율로 계산됩니다. 큰 값일수록 더 중요한 축입니다.
- 재구성 오차는 0이 아니지만 충분히 작다면, 줄인 차원으로도 원래 구조를 꽤 잘 보존한 것입니다.

## 공분산 고유분해와 SVD의 수학적 연결

중심화된 데이터 `Xc`에 대해 공분산은 `C = Xc^T Xc / (n-1)`입니다. `Xc = U S V^T`라면

$$C = V \frac{S^2}{n-1} V^T$$

이므로, 공분산의 고유벡터는 `V`의 열벡터와 같고 고유값은 `S^2/(n-1)`에 대응합니다. 즉 SVD 기반 PCA와 공분산 고유분해 기반 PCA는 수학적으로 같은 구조를 공유합니다.

```python
import numpy as np

rng = np.random.default_rng(42)
X = rng.normal(size=(50, 3))
Xc = X - X.mean(axis=0)

# 방법 1: SVD 기반
U_svd, S_svd, Vt_svd = np.linalg.svd(Xc, full_matrices=False)

# 방법 2: 공분산 고유분해 기반
C = (Xc.T @ Xc) / (len(Xc) - 1)
eigvals, eigvecs = np.linalg.eigh(C)
idx = eigvals.argsort()[::-1]
eigvals, eigvecs = eigvals[idx], eigvecs[:, idx]

# 고유값 vs 특이값^2/(n-1) 비교
print('eigh eigenvalues:', eigvals)
print('SVD  eigenvalues:', S_svd**2 / (len(Xc) - 1))
print('두 방법 일치:', np.allclose(eigvals, S_svd**2 / (len(Xc) - 1)))
```

## 넘파이만으로 PCA 끝까지 구현하기

아래 코드는 중심화, SVD, 투영, 복원, 설명률 계산까지 한 번에 수행합니다.

```python
import numpy as np

rng = np.random.default_rng(42)
X = rng.normal(size=(200, 5))
X[:, 2] = 0.7 * X[:, 0] + 0.2 * X[:, 1] + 0.1 * rng.normal(size=200)

Xc = X - X.mean(axis=0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
explained_ratio = (S ** 2) / np.sum(S ** 2)
cum_ratio = np.cumsum(explained_ratio)

# 95% 누적 설명률을 넘는 최소 k
k = int(np.searchsorted(cum_ratio, 0.95) + 1)
Z = Xc @ Vt[:k].T
X_rec = Z @ Vt[:k]

recon_err = np.linalg.norm(Xc - X_rec) / np.linalg.norm(Xc)

print('explained ratio:', explained_ratio.round(3))
print('cumulative ratio:', cum_ratio.round(3))
print('chosen k:', k)
print('relative reconstruction error:', recon_err)
```

`k`를 95% 누적 설명률 기준으로 고르는 패턴은 교육용뿐 아니라 실무에서도 출발점으로 자주 씁니다.

## 단계별 구현: 표준화부터 투영까지

### 1단계: 표준화

피처 스케일이 크게 다르면 분산이 큰 변수가 주성분을 지배합니다. 표준화(standardization)는 각 피처를 평균 0, 표준편차 1로 맞춥니다.

```python
import numpy as np

X = np.array([[1.0, 2000.0], [2.0, 3000.0], [3.0, 4000.0], [4.0, 5000.0]])
X_std = (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)
print('표준화 후:\n', X_std)
```

표준화 후에는 모든 피처가 동등한 가중치를 갖게 되므로, 상관 구조만으로 주성분이 결정됩니다.

### 2단계: 공분산 행렬 계산

```python
C = np.cov(X_std, rowvar=False)
print('공분산 행렬:\n', C)
```

공분산 행렬은 피처 간 상관 정보를 담고 있습니다. 대칭 행렬이므로 실수 고유값과 직교 고유벡터를 갖습니다.

### 3단계: 고유값 분해

```python
eigvals, eigvecs = np.linalg.eigh(C)
idx = eigvals.argsort()[::-1]
eigvals = eigvals[idx]
eigvecs = eigvecs[:, idx]

print('고유값:', eigvals)
print('분산 설명률:', eigvals / eigvals.sum())
```

고유값은 각 주성분 방향의 분산입니다. 큰 고유값부터 정렬하면 중요한 축 순서대로 나열됩니다.

### 4단계: 투영

```python
k = 1
X_pca = X_std @ eigvecs[:, :k]
print('1차원 투영:', X_pca.shape)
```

상위 `k`개 고유벡터로 이뤄진 행렬에 데이터를 곱하면, 새로운 좌표계에서의 좌표를 얻습니다. 이 과정이 차원 축소의 실제 연산입니다.

## 사이킷런 PCA로 설명 분산 확인하기

```python
from sklearn.decomposition import PCA
import numpy as np

rng = np.random.default_rng(99)
X = rng.normal(size=(150, 5))
X[:, 3] = 0.9 * X[:, 0] + 0.1 * rng.normal(size=150)

pca = PCA()
pca.fit(X)

print('설명 분산 비율:', pca.explained_variance_ratio_)
print('누적 분산 비율:', pca.explained_variance_ratio_.cumsum())

n_components_95 = (pca.explained_variance_ratio_.cumsum() >= 0.95).argmax() + 1
print('95% 설명하는 최소 성분 수:', n_components_95)

pca_reduced = PCA(n_components=n_components_95)
X_reduced = pca_reduced.fit_transform(X)
print('축소 후 형상:', X_reduced.shape)
```

`explained_variance_ratio_`는 각 주성분이 전체 분산 중 얼마나 설명하는지 비율로 나타냅니다. 누적합이 0.95 이상이면 원래 데이터 정보의 95%를 유지하면서 차원을 줄일 수 있다는 뜻입니다.

## 적용 판단표

| 질문 | 점검 항목 | 실무 액션 |
| --- | --- | --- |
| 스케일 차이가 큰가? | 피처 분산 편차 | 표준화 후 PCA 고려 |
| 비선형 구조가 강한가? | 잔차/시각화 | 커널 PCA, UMAP 검토 |
| 압축 목적이 명확한가? | 목표 설명률, 오차 허용치 | `k`를 수치 기준으로 고정 |
| 역변환이 필요한가? | 재구성 요구사항 | `pca.inverse_transform` 사용 가능 여부 확인 |

## PCA, t-SNE, UMAP 비교표

| 기법 | 목적 | 보존 대상 | 속도 |
| --- | --- | --- | --- |
| PCA | 선형 차원 축소 | 전역 분산(글로벌 구조) | 매우 빠름 |
| t-SNE | 비선형 시각화 | 지역 이웃 관계(로컬 구조) | 느림 |
| UMAP | 비선형 차원 축소 | 지역+전역 구조 균형 | 중간(t-SNE보다 빠름) |

PCA는 선형 기법이므로 비선형 매니폴드를 제대로 펼치지 못할 수 있습니다. 반면 빠르고 해석이 명확하며, 역변환도 가능합니다. 선택 기준: 빠른 탐색·해석 우선이면 PCA, 클러스터 시각화이면 t-SNE, 전역+지역 균형이면 UMAP을 씁니다.

## 이 코드에서 먼저 볼 점

- 중심화는 필수입니다.
- SVD는 PCA를 구현하는 안정적인 경로입니다.
- 분산 설명률은 `k` 선택의 중요한 기준입니다.
- 재구성 오차를 보면 압축 손실을 함께 판단할 수 있습니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 중심화 누락 | 분산 대신 위치 정보가 첫 주성분에 포함됨 | 반드시 `Xc = X - X.mean(axis=0)` 적용 |
| 표준화 없이 스케일 큰 피처 포함 | 분산이 큰 피처 하나가 주성분 독점 | 스케일 차이가 크면 표준화 선행 |
| 주성분 부호 고정 기대 | 부호만 다른 결과를 오류로 해석 | PCA 부호는 임의적, 방향이 아닌 축으로 해석 |
| 비선형 구조에 PCA 단독 적용 | 주성분 2개로도 군집 분리 안 됨 | t-SNE 또는 UMAP 병행 검토 |
| `k`를 근거 없이 결정 | 과도한 정보 손실 또는 불필요한 차원 유지 | 누적 분산 설명률 기준 `k` 선택 |

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 PCA를 단순한 차원 축소 도구로만 보지 않습니다. 데이터가 실제로 몇 개의 큰 방향으로 요약되는지, 노이즈가 얼마나 많은지, 시각화나 모델 입력 압축에 도움이 되는지 함께 봅니다.

또한 PCA 전에 표준화가 필요한지 판단합니다. 피처 스케일이 크게 다르면 분산이 큰 변수 하나가 결과를 지배할 수 있기 때문입니다. 좋은 PCA 사용법은 알고리즘을 적용하는 것보다, 어떤 전처리와 어떤 `k`가 문제에 맞는지 결정하는 데 있습니다.

## 실전 확장 노트: PCA 파이프라인과 검증 루틴

PCA를 실제 파이프라인에 넣을 때는 단순 시각화에 그치지 않고, 차원 축소 전후의 학습 안정성과 압축 품질을 함께 수치로 확인해야 합니다.

```python
import numpy as np

rng = np.random.default_rng(1)
X = rng.normal(size=(200, 20))
# 첫 번째 피처와 강한 상관 구조 부여
X[:, 5] = 0.9 * X[:, 0] + 0.1 * rng.normal(size=200)
X[:, 10] = 0.8 * X[:, 1] + 0.2 * rng.normal(size=200)

# 1) 중심화
Xc = X - X.mean(axis=0)

# 2) SVD
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
ratio = (S**2) / (S**2).sum()
cum = np.cumsum(ratio)

# 3) k 선택 (95% 기준)
k = int(np.searchsorted(cum, 0.95) + 1)
Xk = Xc @ Vt[:k].T

# 4) 재구성 및 오차
X_rec = Xk @ Vt[:k]
recon_err = np.linalg.norm(Xc - X_rec) / np.linalg.norm(Xc)

print('95% 분산 유지 차원 k:', k)
print('축소 전후:', X.shape, Xk.shape)
print('재구성 오차:', recon_err)
print('상위 5개 설명률:', ratio[:5].round(3))

# 5) 직교성 검증 (주성분 간 상관 제거 확인)
cov_pca = np.cov(Xk, rowvar=False)
off_diag_max = np.abs(cov_pca - np.diag(np.diag(cov_pca))).max()
print('주성분 간 최대 공분산:', off_diag_max)
```

반드시 확인할 항목은 네 가지입니다.

1. **`k` 선택**: 감이 아닌 누적 설명률 기준을 세웁니다.
2. **재구성 오차**: 허용 손실 범위 내에 있는지 수치로 확인합니다.
3. **직교성**: 투영된 데이터의 축 간 공분산이 0에 가까워야 합니다.
4. **상위 설명률 분포**: 첫 몇 주성분이 급격히 많은 분산을 담으면 저차원 표현이 효율적입니다.

## 운영 체크리스트

- [ ] PCA가 새로운 기저를 찾는 과정이라는 점을 설명할 수 있습니다.
- [ ] 중심화가 왜 필요한지 이해했습니다.
- [ ] 분산 설명률을 보고 `k`를 선택할 수 있습니다.
- [ ] 재구성 오차의 의미를 말할 수 있습니다.
- [ ] SVD 기반 PCA와 공분산 고유분해 기반 PCA가 동등하다는 점을 압니다.

## 연습 문제

1. 아이리스 데이터셋에 PCA를 적용해 2차원으로 시각화해 보세요.
2. 누적 분산 설명률이 90%를 넘는 최소 `k`를 찾아 보세요.
3. PCA와 단순 피처 선택의 차이를 설명해 보세요.
4. 중심화 없이 PCA를 수행했을 때 결과가 어떻게 달라지는지 비교해 보세요.

## 정리와 다음 글

PCA는 데이터를 더 잘 설명하는 축을 새로 찾고, 그중 중요한 축만 남겨 차원을 줄이는 방법입니다. 기저 선택, 고유값, SVD, 재구성 오차가 한 자리에서 만나는 대표적인 주제이기도 합니다. 그래서 PCA를 이해하면 선형대수가 실제 데이터 문제에 어떻게 쓰이는지 훨씬 또렷하게 보입니다.

다음 글에서는 시리즈를 마무리하며 머신러닝 전반에서 선형대수가 어떻게 이어지는지 종합합니다. 지금까지 배운 벡터, 행렬, 변환, 분해, PCA가 하나의 모델 안에서 어떻게 연결되는지 보겠습니다.

## 처음 질문으로 돌아가기

- **PCA는 왜 중요한 방향을 찾아낸다고 말할 수 있을까요?**
  - PCA는 데이터의 분산이 가장 큰 방향을 첫 번째 주성분으로 잡습니다. 분산이 크다는 것은 데이터가 그 축 방향으로 많이 퍼져 있다는 뜻이고, 이는 해당 축이 데이터의 구조를 더 많이 담고 있다는 의미입니다. 공분산 행렬의 고유분해 또는 데이터 행렬의 SVD가 이 분산 최대화 문제를 수학적으로 풀어 줍니다.
- **공분산 관점과 SVD 관점은 어떻게 연결될까요?**
  - 중심화된 데이터 `Xc = U S V^T`이면 공분산 행렬은 `C = V (S²/(n-1)) V^T`가 됩니다. 따라서 공분산 고유벡터는 SVD의 `V` 열과 같고, 고유값은 특이값의 제곱을 `(n-1)`로 나눈 것입니다. 두 방법은 수학적으로 동등하며, 수치 안정성 때문에 실무에서는 SVD 방법을 선호합니다.
- **왜 중심화가 빠지면 안 될까요?**
  - 중심화하지 않으면 첫 번째 주성분이 데이터의 분산 방향 대신 평균 벡터 방향을 가리킵니다. 평균이 원점에서 멀리 떨어져 있을수록 이 편향이 커지며, 실제 데이터 구조를 반영하지 못하는 주성분이 나옵니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linear Algebra 101 (1/10): 선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): 벡터](./02-vectors.md)
- [Linear Algebra 101 (3/10): 행렬](./03-matrices.md)
- [Linear Algebra 101 (4/10): 내적과 거리](./04-inner-product-and-distance.md)
- [Linear Algebra 101 (5/10): 선형변환](./05-linear-transformation.md)
- [Linear Algebra 101 (6/10): 기저와 차원](./06-basis-and-dimension.md)
- [Linear Algebra 101 (7/10): 고유값과 고유벡터](./07-eigenvalues-and-eigenvectors.md)
- [Linear Algebra 101 (8/10): 행렬 분해](./08-matrix-decomposition.md)
- **Linear Algebra 101 (9/10): PCA (현재 글)**
- [머신러닝에서의 선형대수](./10-linear-algebra-in-ml.md)

<!-- toc:end -->

## 참고 자료

- 시리즈 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/linear-algebra-101/ko
- [Wikipedia — Principal component analysis](https://en.wikipedia.org/wiki/Principal_component_analysis)
- [scikit-learn — PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)
- [Setosa — Principal Component Analysis](https://setosa.io/ev/principal-component-analysis/)
- [Stanford CS229 — Notes on PCA](https://cs229.stanford.edu/notes2020spring/cs229-notes10.pdf)

Tags: LinearAlgebra, PCA, DimensionalityReduction, DataScience, Beginner

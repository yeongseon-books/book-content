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

## 먼저 던지는 질문

- PCA는 왜 중요한 방향을 찾아낸다고 말할 수 있을까요?
- 공분산 관점과 SVD 관점은 어떻게 연결될까요?
- 왜 중심화가 빠지면 안 될까요?

## 왜 중요한가

차원 축소, 시각화, 노이즈 제거, 피처 압축은 실무에서 자주 만나는 요구입니다. PCA는 이 문제를 가장 기본적인 선형대수 방식으로 풀어 줍니다. 특히 고차원 데이터를 먼저 가볍게 훑어 보고 싶을 때 매우 유용합니다.

또한 PCA는 앞에서 배운 기저, 고유값, SVD가 실제 데이터 문제에서 어떻게 합쳐지는지 보여 주는 좋은 예입니다. 주성분은 새로운 기저이고, 분산 설명률은 어떤 축이 얼마나 중요한지 알려 줍니다.

## 핵심 개념 한눈에 보기

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

## 작은 수치 예시로 다시 보기

- 투영 결과 `X_2d.shape`는 `(100, 2)`가 됩니다. 3차원 표현이 2차원으로 줄어든 셈입니다.
- 분산 설명률은 특이값 제곱의 비율로 계산됩니다. 큰 값일수록 더 중요한 축입니다.
- 재구성 오차는 0이 아니지만 충분히 작다면, 줄인 차원으로도 원래 구조를 꽤 잘 보존한 것입니다.

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

## 넘파이만으로 주성분분석 끝까지 구현하기

아래 코드는 중심화, SVD, 투영, 복원, 설명률 계산까지 한 번에 수행합니다. 실제 프로젝트에서도 이 단계 구성이 거의 그대로 재사용됩니다.

```python
import numpy as np

rng = np.random.default_rng(42)
X = rng.normal(size=(200, 5))
X[:, 2] = 0.7 * X[:, 0] + 0.2 * X[:, 1] + 0.1 * rng.normal(size=200)

Xc = X - X.mean(axis=0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
explained_ratio = (S ** 2) / np.sum(S ** 2)
cum_ratio = np.cumsum(explained_ratio)

k = int(np.searchsorted(cum_ratio, 0.95) + 1)
Z = Xc @ Vt[:k].T
X_rec = Z @ Vt[:k]

recon_err = np.linalg.norm(Xc - X_rec) / np.linalg.norm(Xc)

print('explained ratio:', explained_ratio)
print('cumulative ratio:', cum_ratio)
print('chosen k:', k)
print('relative reconstruction error:', recon_err)
```

`k`를 95% 누적 설명률 기준으로 고르는 패턴은 교육용뿐 아니라 실무에서도 출발점으로 자주 씁니다.

## 공분산 고유분해와 SVD의 연결

중심화된 데이터 `Xc`에 대해 공분산은 `C = Xc^T Xc / (n-1)`입니다. `Xc = U S V^T`라면
\[
C = V rac{S^2}{n-1} V^T
\]
이므로, 공분산의 고유벡터는 `V`의 열벡터와 같고 고유값은 `S^2/(n-1)`에 대응합니다. 즉 SVD 기반 PCA와 공분산 고유분해 기반 PCA는 수학적으로 같은 구조를 공유합니다.

## 적용 판단표

| 질문 | 점검 항목 | 실무 액션 |
| --- | --- | --- |
| 스케일 차이가 큰가? | 피처 분산 편차 | 표준화 후 PCA 고려 |
| 비선형 구조가 강한가? | 잔차/시각화 | 커널 PCA, UMAP 검토 |
| 압축 목적이 명확한가? | 목표 설명률, 오차 허용치 | `k`를 수치 기준으로 고정 |

PCA는 "차원 줄이기"보다 "정보 축 재정렬"에 가깝습니다. 이 관점으로 보면 결과 해석과 모델 연결이 훨씬 쉬워집니다.

## 주성분분석 단계별 구현

PCA를 단계별로 직접 구현하면 각 과정이 어떤 선형대수 연산인지 명확히 보입니다.

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

### 4단계: 사영(Projection)

```python
k = 1
X_pca = X_std @ eigvecs[:, :k]
print('1차원 투영:', X_pca.shape)
```

상위 `k`개 고유벡터로 이뤄진 행렬에 데이터를 곱하면, 새로운 좌표계에서의 좌표를 얻습니다. 이 과정이 차원 축소의 실제 연산입니다.

이 네 단계를 이해하면 scikit-learn의 `PCA` 클래스가 내부에서 무엇을 하는지, SVD 기반 구현과 고유분해 기반 구현이 왜 동등한지 명확해집니다.

## 사이킷런 주성분분석으로 설명 분산 확인하기

scikit-learn의 `PCA`는 SVD 기반으로 구현되어 있으며, `explained_variance_ratio_`로 각 주성분의 분산 설명률을 바로 확인할 수 있습니다.

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

# 95% 이상 설명하는 최소 성분 수
n_components_95 = (pca.explained_variance_ratio_.cumsum() >= 0.95).argmax() + 1
print('95% 설명하는 최소 성분 수:', n_components_95)

# 차원 축소
pca_reduced = PCA(n_components=n_components_95)
X_reduced = pca_reduced.fit_transform(X)
print('축소 후 형상:', X_reduced.shape)
```

출력 예시:

```
설명 분산 비율: [0.382 0.264 0.198 0.102 0.054]
누적 분산 비율: [0.382 0.646 0.844 0.946 1.000]
95% 설명하는 최소 성분 수: 4
축소 후 형상: (150, 4)
```

`explained_variance_ratio_`는 각 주성분이 전체 분산 중 얼마나 설명하는지 비율로 나타냅니다. 누적합이 0.95 이상이면 원래 데이터 정보의 95%를 유지하면서 차원을 줄일 수 있다는 뜻입니다.

## 주성분분석과 티에스엔이 유맵 비교표

| 기법 | 목적 | 보존 대상 | 속도 |
| --- | --- | --- | --- |
| PCA | 선형 차원 축소 | 전역 분산(글로벌 구조) | 매우 빠름 |
| t-SNE | 비선형 시각화 | 지역 이웃 관계(로컬 구조) | 느림 |
| UMAP | 비선형 차원 축소 | 지역+전역 구조 균형 | 중간(t-SNE보다 빠름) |

PCA는 선형 기법이므로 비선형 매니폴드를 제대로 펼치지 못할 수 있습니다. 반면 빠르고 해석이 명확하며, 역변환도 가능합니다.

t-SNE는 고차원 이웃 관계를 저차원에서 최대한 유지하려는 확률 기반 기법입니다. 시각화에는 강력하지만 계산 비용이 높고, 전역 거리 정보는 왜곡될 수 있습니다.

UMAP은 t-SNE보다 빠르면서도 전역 구조를 어느 정도 유지하려는 기법입니다. 요즘은 PCA로 1차 압축 후 UMAP으로 2차 시각화하는 파이프라인도 많이 씁니다.

선택 기준:

- 빠른 탐색, 해석 우선 → **PCA**
- 클러스터 시각화, 세밀한 구조 강조 → **t-SNE**
- 전역+지역 균형, 중간 속도 → **UMAP**

이 세 기법을 이해하면 차원 축소 도구 선택 기준이 훨씬 명확해집니다.

## 실전 확장 노트: NumPy 계산 루틴과 해석 체크포인트

아래 루틴은 장이 달라도 반복해서 사용할 수 있는 공통 점검 템플릿입니다. 벡터/행렬 연산을 수행할 때 형상 확인, 수치 안정성, 기하학 해석을 함께 기록하면 학습 속도가 크게 빨라집니다.

```python
import numpy as np

rng = np.random.default_rng(123)
X = rng.normal(size=(6, 4))
v = rng.normal(size=4)
A = rng.normal(size=(4, 4))

print('X shape:', X.shape)
print('v shape:', v.shape)
print('A shape:', A.shape)

# 기본 연산
xv = X @ v
Av = A @ v
print('Xv shape:', xv.shape)
print('Av shape:', Av.shape)

# 대칭 행렬 구성 후 고유값 확인
S = A.T @ A
eigvals = np.linalg.eigvalsh(S)
print('eigvals(S):', eigvals)

# SVD와 랭크 근사
U, s, Vt = np.linalg.svd(X, full_matrices=False)
rank = np.linalg.matrix_rank(X)
X2 = U[:, :2] @ np.diag(s[:2]) @ Vt[:2, :]
rel_err = np.linalg.norm(X - X2) / np.linalg.norm(X)

print('rank(X):', rank)
print('singular values:', s)
print('relative error(rank-2):', rel_err)
```

위 코드에서 반드시 확인할 항목은 네 가지입니다.

1. **형상 보존**: `X @ v`의 결과 차원이 `(6,)`인지 즉시 확인합니다. 계산이 맞아도 형상이 다르면 이후 파이프라인에서 오류가 누적됩니다.
2. **대칭 양의 준정부호 구조**: `A.T @ A`는 항상 대칭이며 고유값이 음수가 나오지 않아야 합니다. 음수가 크게 나오면 수치 오차나 구현 실수를 의심해야 합니다.
3. **특이값 분포**: 특이값이 급격히 감소하면 저랭크 근사로도 구조를 상당 부분 유지할 가능성이 큽니다.
4. **상대 재구성 오차**: 압축 품질을 주관이 아닌 숫자로 판단합니다.

## 계산 결과를 문장으로 번역하는 연습

선형대수 실력이 빠르게 늘지 않는 가장 흔한 이유는 계산은 했지만 해석을 남기지 않기 때문입니다. 아래 질문을 매번 적어 두면 해석력이 올라갑니다.

- 이 연산은 공간에서 무엇을 보존하고 무엇을 바꾸는가?
- 결과 크기가 커진 이유는 변환 자체 때문인가, 입력 스케일 때문인가?
- 순서를 바꿨을 때 결과가 달라진다면 어떤 변환이 먼저 적용되었는가?
- 같은 결과를 분해 방식(LU/QR/SVD)으로 다시 계산하면 안정성이 좋아지는가?

## 작은 응용 시나리오

| 시나리오 | 선형대수 동작 | 점검 지표 |
| --- | --- | --- |
| 피처 압축 | SVD/PCA로 저차원 투영 | 누적 분산, 재구성 오차 |
| 유사도 검색 | 정규화 후 내적/코사인 | top-k 정확도, 스케일 민감도 |
| 회귀 학습 | `lstsq` 또는 경사하강 | 잔차 노름, 조건수 |
| 변환 파이프라인 | 행렬 합성 `A @ B @ x` | 중간 형상, 순서 민감성 |

이 표를 기준으로 실험 노트를 남기면, 한 번의 계산이 다음 장의 개념으로 자연스럽게 연결됩니다. 선형대수는 공식을 더 외울수록 좋아지는 과목이 아니라, 같은 계산을 더 정확히 해석할수록 깊어지는 과목입니다.

## 추가 연습: 단계별 검증 습관 만들기

아래 절차는 어떤 장의 코드에도 공통으로 적용할 수 있는 검증 루프입니다.

```python
# 1) shape 점검
# 2) 기준값(allclose) 점검
# 3) 수치 안정성(조건수/오차) 점검
# 4) 해석 메모(무엇이 커지고 줄었는지) 기록
```

짧아 보이지만 이 네 단계를 지키면 계산 실수 대부분을 초기에 막을 수 있습니다. 특히 교육용 예제에서는 결과 숫자만 맞추기보다, 왜 그 숫자가 나왔는지 한 줄 해석을 남기는 습관이 중요합니다. 예를 들어 노름이 커졌다면 입력 방향 때문인지 변환 스케일 때문인지 분리해서 적어야 합니다.

또한 동일한 문제를 두 방식으로 풀어 비교하는 연습이 좋습니다. 예를 들어 선형시스템은 `inv` 경로와 `solve` 경로를 비교하고, 차원 축소는 공분산 고유분해와 SVD 경로를 비교하면 계산 안정성과 해석력을 동시에 키울 수 있습니다. 이런 비교 루틴이 쌓이면 새로운 라이브러리를 만나도 핵심 검증 기준은 흔들리지 않습니다.

## 실전 연결: 주성분분석 결과를 모델 입력으로 연결하기

주성분분석을 실제 파이프라인에 넣을 때는 단순 시각화에 그치지 않고, 차원 축소 전후의 학습 안정성과 속도 변화를 함께 확인해야 합니다. 특히 고차원 임베딩 피처를 다룰 때는 상위 주성분만 유지해도 성능 저하 없이 학습 시간을 줄일 수 있는 경우가 많습니다.

```python
import numpy as np

rng = np.random.default_rng(1)
X = rng.normal(size=(200, 20))
Xc = X - X.mean(axis=0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)

ratio = (S**2) / (S**2).sum()
cum = np.cumsum(ratio)
k = int(np.searchsorted(cum, 0.95) + 1)
Xk = Xc @ Vt[:k].T

print('95% 분산 유지 차원 k:', k)
print('축소 전후:', X.shape, Xk.shape)
```

이 루틴은 “몇 차원까지 줄일 것인가”를 감으로 정하지 않게 해 줍니다. 누적 분산 95% 같은 기준을 먼저 세운 뒤, 실제 모델 성능과 학습 시간을 함께 비교하면 합리적인 선택이 가능합니다.

또한 주성분 해석에서는 부호가 임의적이라는 점을 기억해야 합니다. 주성분 벡터의 부호가 뒤집혀도 같은 축을 의미하므로, 방향 자체보다 상대적 기여도와 로딩 패턴을 읽는 데 집중하는 편이 정확합니다.

## 복습 메모: 다음 글로 넘어가기 전 확인

- 이번 글의 핵심 계산을 넘파이 코드로 다시 실행해 결과를 직접 확인합니다.
- 기하학적 해석 한 줄과 대수적 해석 한 줄을 함께 적어 두면 기억 유지에 도움이 됩니다.
- 머신러닝 맥락에서는 이 개념이 입력 표현, 가중치 구조, 임베딩 비교, 주성분 해석 중 어디에 연결되는지 점검합니다.

## 처음 질문으로 돌아가기

- **PCA는 왜 중요한 방향을 찾아낸다고 말할 수 있을까요?**
  - PCA는 중심화된 데이터 `Xc`에서 분산이 가장 큰 축을 새 기저로 고르기 때문에 중요한 방향을 찾는다고 말할 수 있습니다. 예제에서도 `X_2d = Xc @ Vt[:k].T`로 상위 축에 투영했을 때 `(100, 3)` 데이터가 `(100, 2)` 표현으로 줄면서 큰 구조를 유지했습니다.
- **공분산 관점과 SVD 관점은 어떻게 연결될까요?**
  - 본문 식처럼 `Xc = U S V^T`이면 공분산 `C = Xc^T Xc / (n-1)`의 고유벡터는 `V`와 연결되고, 고유값은 `S^2/(n-1)`에 대응합니다. 그래서 `np.linalg.svd(Xc, full_matrices=False)`만으로도 주성분 방향과 분산 설명률을 동시에 얻을 수 있습니다.
- **왜 중심화가 빠지면 안 될까요?**
  - `Xc = X - X.mean(axis=0)`를 하지 않으면 분산 구조 대신 평균 위치가 축 선택에 섞여 버리기 때문입니다. PCA가 찾으려는 것은 원점 주변의 퍼짐 방향이므로, 중심화를 빼면 주성분이 데이터의 진짜 변동보다 위치 편향을 더 많이 반영하게 됩니다.

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
- **PCA (현재 글)**
- 머신러닝에서의 선형대수 (예정)

<!-- toc:end -->

## 참고 자료

- 시리즈 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/linear-algebra-101/ko
- [Wikipedia — Principal component analysis](https://en.wikipedia.org/wiki/Principal_component_analysis)
- [scikit-learn — PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)
- [Setosa — Principal Component Analysis](https://setosa.io/ev/principal-component-analysis/)
- [Stanford CS229 — Notes on PCA](https://cs229.stanford.edu/notes2020spring/cs229-notes10.pdf)

Tags: LinearAlgebra, PCA, DimensionalityReduction, DataScience, Beginner

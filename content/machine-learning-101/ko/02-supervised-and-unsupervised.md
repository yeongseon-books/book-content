---
series: machine-learning-101
episode: 2
title: "Machine Learning 101 (2/10): 지도학습과 비지도학습"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - MachineLearning
  - SupervisedLearning
  - UnsupervisedLearning
  - Classification
  - Clustering
seo_description: 지도학습과 비지도학습의 차이, 분류·회귀·군집의 경계, 그리고 문제 프레이밍의 중요성을 코드와 함께 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (2/10): 지도학습과 비지도학습

머신러닝을 처음 배우면 알고리즘 이름부터 외우기 쉽습니다. 하지만 실제 프로젝트에서 더 먼저 해야 하는 일은 모델 선택이 아니라 문제를 어떤 종류로 볼지 정하는 일입니다. 레이블이 있는지 없는지, 예측하려는 대상이 범주인지 숫자인지, 아니면 데이터 안의 구조를 발견해야 하는지에 따라 출발점이 완전히 달라집니다.

이 글은 머신러닝 101 시리즈의 2번째 글입니다. 여기서는 지도학습과 비지도학습의 경계를 정리하고, 분류·회귀·군집이 각각 어떤 질문에 답하는지 비교해 보겠습니다.

![Machine Learning 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/02/02-01-diagram.ko.png)
*Machine Learning 101 2장 흐름 개요*
> 지도학습과 비지도학습의 경계는 데이터에 라벨이 있는지 하나로 갈리고, 분류·회귀·군집 같은 모든 갈래는 거기서 파생됩니다.

## 이 글에서 다룰 문제

- 레이블이 있을 때와 없을 때 같은 알고리즘을 써도 될까요?
- 분류와 회귀는 둘 다 지도학습인데 무엇이 다를까요?
- 군집화는 분류와 왜 전혀 다른 문제로 취급할까요?
- 이 개념을 실무 프로젝트에 적용할 때 가장 먼저 확인할 점은 무엇일까요?
- 이 기법의 한계는 어디서 드러나고 어떻게 보완할까요?

## ML 패러다임 비교

| 유형 | 목표 | 출력 | 대표 알고리즘 |
|---|---|---|---|
| 분류(Classification) | 이산 레이블 예측 | 0, 1, 2 등 | Logistic Regression, Decision Tree |
| 회귀(Regression) | 연속값 예측 | 123.4, -0.89 등 | Linear Regression, SVR |
| 군집(Clustering) | 비슷한 점 묶기 | cluster ID | KMeans, DBSCAN |
| 차원축소(Dimensionality Reduction) | 피처 압축 | 낮은 차원 X | PCA, t-SNE |

분류와 회귀는 둘 다 지도학습이지만, 예측하려는 대상이 다릅니다. 군집과 차원축소는 비지도학습으로, 레이블 없이 데이터의 구조를 찾는 문제입니다.

패러다임을 잘못 고르면 이후 모델 개선은 거의 의미가 없어집니다. 문제 프레이밍이 첫 번째 레버인 이유가 여기에 있습니다. 연속값을 예측해야 하는데 분류처럼 접근하거나, 정답 레이블이 없는데 지도학습 지표를 기대하면 모델보다 문제 정의가 먼저 어긋납니다.

- **지도학습(Supervised learning)**: `(X, y)` 쌍에서 함수를 학습합니다.
- **비지도학습(Unsupervised learning)**: `X`만 보고 구조를 발견합니다.
- **분류(Classification)**: 이산적인 레이블을 예측합니다.
- **회귀(Regression)**: 연속적인 값을 예측합니다.
- **군집화(Clustering)**: 거리나 밀도를 기준으로 비슷한 점들을 묶습니다.

## 적용 전과 후

**Before**: "머신러닝은 회귀 한 줄이면 된다"고 생각해서 패러다임 구분을 건너뜁니다.

**After**: 먼저 **레이블 유무**를 확인하고, 그다음 **분류인지 회귀인지**를 정한 뒤 알고리즘을 고릅니다.

## 실습: 5단계로 패러다임 비교하기

### 단계 1 — 데이터 로드

```python
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
```

### 단계 2 — 지도학습 분류

```python
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(max_iter=1000).fit(X, y)
print("clf acc:", clf.score(X, y))
```

### 단계 3 — 회귀 데이터셋

```python
from sklearn.datasets import fetch_california_housing
Xr, yr = fetch_california_housing(return_X_y=True)
```

### 단계 4 — 회귀 모델

```python
from sklearn.linear_model import LinearRegression
reg = LinearRegression().fit(Xr, yr)
print("R^2:", reg.score(Xr, yr))
```

### 단계 5 — 비지도 군집화

```python
from sklearn.cluster import KMeans
km = KMeans(n_clusters=3, n_init=10).fit(X)
print("inertia:", km.inertia_)
```

**예상 출력:** 분류 예제는 정확도, 회귀 예제는 `R^2`, 군집화 예제는 inertia를 출력합니다. 숫자가 모두 성능처럼 보이지만 **서로 같은 의미가 아니며 직접 비교할 수도 없습니다.**

## 문제 유형별 데이터셋과 지표 정리

어떤 데이터셋을 쓰고 어떤 지표로 평가할지는 패러다임이 결정합니다. 지표의 범위와 방향을 모르면 숫자를 잘못 해석할 수 있습니다.

| 문제 유형 | scikit-learn 데이터셋 | 주요 지표 | 지표 방향 |
|---|---|---|---|
| 이진 분류 | `load_breast_cancer` | Accuracy, F1, AUC | 높을수록 좋음 |
| 다중 분류 | `load_iris` | Accuracy, macro-F1 | 높을수록 좋음 |
| 회귀 | `fetch_california_housing` | MAE, RMSE, R² | R²: 1에 가까울수록 좋음 |
| 군집 | `load_iris` (레이블 무시) | Silhouette, Inertia | Silhouette: 1에 가까울수록 좋음 |

```python
from sklearn.datasets import load_iris, load_breast_cancer, fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, r2_score, silhouette_score

# 이진 분류
Xbc, ybc = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(Xbc, ybc, test_size=0.2, stratify=ybc, random_state=42)
clf = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
print(f"이진분류 Accuracy: {accuracy_score(yte, clf.predict(Xte)):.4f}")

# 회귀
Xch, ych = fetch_california_housing(return_X_y=True)
Xtr_r, Xte_r, ytr_r, yte_r = train_test_split(Xch, ych, test_size=0.2, random_state=42)
reg = LinearRegression().fit(Xtr_r, ytr_r)
print(f"회귀 R²: {r2_score(yte_r, reg.predict(Xte_r)):.4f}")

# 군집 (레이블 사용 안 함)
X_iris, _ = load_iris(return_X_y=True)
from sklearn.preprocessing import StandardScaler
X_scaled = StandardScaler().fit_transform(X_iris)
km = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X_scaled)
print(f"군집 Silhouette: {silhouette_score(X_scaled, km.labels_):.4f}")
```

## 준지도학습과 자기지도학습

실무에서는 지도학습과 비지도학습 사이의 중간 지대가 더 흔합니다.

### 준지도학습(Semi-supervised learning)

- 레이블이 있는 데이터는 적고, 레이블이 없는 데이터는 많을 때 사용합니다.
- 예시: 이미지 100장은 사람이 레이블링했고, 10,000장은 레이블이 없을 때 준지도 기법을 쓰면 레이블링 비용을 크게 줄일 수 있습니다.
- scikit-learn의 `LabelPropagation`이나 `LabelSpreading`이 대표적입니다.

### 자기지도학습(Self-supervised learning)

- 데이터 자체에서 레이블을 자동으로 만드는 방식입니다.
- 예시: 문장에서 단어를 가리고 다음 단어를 예측하는 방식으로 언어 모델을 학습합니다.
- 현대 NLP와 컴퓨터 비전에서 널리 쓰이는 전략입니다.

입문 단계에서는 지도/비지도 경계만 명확히 잡으면 충분하지만, 실무에서는 중간 기법을 고려하는 것이 효율적일 때가 많습니다.

## Python 예제: KMeans vs LogisticRegression

```python
from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression

X, y = load_iris(return_X_y=True)

# 비지도: 군집
km = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X)
print("Inertia:", km.inertia_)  # 응집도 (낮을수록 좋음)

# 지도: 분류
clf = LogisticRegression(max_iter=1000).fit(X, y)
print("Accuracy:", clf.score(X, y))  # 정확도
```

군집 결과의 inertia와 분류 결과의 accuracy는 서로 비교할 수 없습니다. 비지도학습은 정답이 없기 때문에 해석이 더 어렵습니다.
- `clf.score`는 정확도, `reg.score`는 결정계수(R-squared), `km.inertia_`는 군집 응집도를 뜻합니다. **지표가 다르면 숫자의 의미도 달라집니다.**
- `KMeans(n_init=...)`는 재현성과 안정성에 직접 영향을 줍니다.
- 비지도학습은 정답이 없기 때문에 결과 해석이 더 어렵습니다.

## 평가 시나리오별 올바른 접근법

같은 데이터도 어떻게 문제를 정의하느냐에 따라 적합한 패러다임이 달라집니다. 실무 시나리오로 패러다임 선택을 연습해 봅니다.

**시나리오 1 — 신용카드 거래 데이터**

레이블이 있고 사기 여부를 예측해야 한다면 이진 분류입니다. 레이블 없이 이상한 패턴을 찾으려면 비지도 이상 탐지입니다. 사기 확률을 점수로 내려면 분류 모델의 `predict_proba`를 씁니다.

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

X, y = make_classification(n_samples=1000, n_features=10,
                            weights=[0.95, 0.05], random_state=42)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
m = LogisticRegression(class_weight="balanced", max_iter=1000).fit(Xtr, ytr)
print(f"F1 (불균형 보정): {f1_score(yte, m.predict(Xte)):.4f}")
```

**시나리오 2 — 고객 구매 이력**

구매 여부를 예측하면 분류, 평균 구매 금액을 예측하면 회귀, 비슷한 고객을 묶으면 군집입니다. 하나의 데이터셋에서 세 가지 패러다임 모두 적용할 수 있습니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 팀이 레이블이 무엇인지 답하지 못하면, 알고리즘보다 먼저 **예측 결과가 바꾸려는 행동**이 무엇인지 다시 물어야 합니다.
- 군집 결과를 곧바로 정답 클래스처럼 쓰려 하면, 먼저 **후속 검증 방법**을 정해야 합니다.
- 지표 해석이 자꾸 꼬인다면, 감독된 문제의 점수와 비지도학습의 응집도 숫자를 같은 표에서 읽고 있지 않은지 확인해야 합니다.

## 자주 하는 실수

| 실수 | 원인 | 교정 방법 |
|---|---|---|
| 회귀 문제를 분류로 풀음 | 출력 유형 미확인 | 예측 대상이 연속인지 이산인지 먼저 확인 |
| 레이블 있는 데이터를 군집으로만 분석 | 정답 활용 기회 낭비 | 지도학습 먼저 시도 |
| 군집 결과를 정답처럼 다룸 | 비지도 오해 | 군집은 가설, 별도 검증 필요 |
| 시각화 없이 K 고정 | 편의 | 엘보우 + 실루엣 + 도메인 지식 사용 |
| 거리 기반 전 표준화 생략 | 스케일 무시 | StandardScaler 항상 적용 |

## 실무에서는 이렇게 나타납니다

스팸 필터와 사기 탐지는 분류, 가격 책정과 수요 예측은 회귀, 고객 세그먼트 분석은 군집화에 기대는 경우가 많습니다. 실제 시스템은 이 셋을 함께 섞어 사용하면서 랭킹과 추천을 만듭니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 순서가 중요합니다. **문제 → 지표 → 패러다임** 순으로 정합니다.
- 비지도학습은 초기에 탐색용으로 매우 유용합니다.
- 업계에서는 준지도학습 상황이 오히려 더 흔합니다.
- 강화학습은 가장 마지막에 꺼내는 카드에 가깝습니다.
- 알고리즘 선택보다 **레이블링 전략**이 더 큰 차이를 만들기도 합니다.

## 운영 체크리스트

- [ ] 분류, 회귀, 군집의 예시를 각각 들 수 있습니다.
- [ ] 각 `.score()` 값 뒤에 있는 의미를 설명할 수 있습니다.
- [ ] KMeans의 `K`가 하이퍼파라미터라는 점을 알고 있습니다.
- [ ] 어떤 알고리즘이 표준화된 입력을 필요로 하는지 알고 있습니다.
- [ ] 레이블 유무를 확인하고 패러다임을 정한 뒤 알고리즘을 고릅니다.

## 패러다임 결정 플로차트

프로젝트에서 어떤 패러다임을 써야 할지 판단하는 체계적인 접근법입니다.

```
데이터에 레이블(y)이 있는가?
├── 예 → 지도학습
│   ├── y가 범주형(클래스)인가?
│   │   ├── 예 → 분류(Classification)
│   │   └── 아니오 → 회귀(Regression)
│   └── 레이블 수가 충분한가?
│       ├── 예 → 일반 지도학습
│       └── 아니오 → 준지도학습 고려
└── 아니오 → 비지도학습
    ├── 그룹을 찾고 싶은가? → 군집화(Clustering)
    ├── 차원을 줄이고 싶은가? → 차원축소(PCA, UMAP)
    └── 이상치를 찾고 싶은가? → 이상 탐지
```

이 흐름을 따르면 알고리즘을 먼저 고르는 실수를 줄일 수 있습니다.

## 세 패러다임 코드 한 번에 비교

분류, 회귀, 군집을 같은 데이터셋(iris)으로 비교해서 지표의 성격 차이를 확인합니다.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, silhouette_score
import numpy as np

X, y = load_iris(return_X_y=True)
sc = StandardScaler()
X_scaled = sc.fit_transform(X)

# 지도학습: 분류 (레이블 사용)
Xtr, Xte, ytr, yte = train_test_split(X_scaled, y, test_size=0.2, stratify=y, random_state=42)
clf = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
print(f"분류 정확도: {accuracy_score(yte, clf.predict(Xte)):.4f}")

# 비지도학습: 군집 (레이블 미사용)
km = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X_scaled)
sil = silhouette_score(X_scaled, km.labels_)
print(f"군집 실루엣: {sil:.4f}")

# 군집 결과와 실제 레이블 비교 (교차표)
from collections import Counter
for cluster_id in range(3):
    mask = km.labels_ == cluster_id
    class_counts = Counter(y[mask])
    print(f"  군집 {cluster_id}: {dict(class_counts)}")
```

군집화는 레이블을 쓰지 않았는데도 붓꽃 품종과 꽤 잘 맞는 그룹을 찾습니다. 하지만 이것이 항상 보장되는 것은 아닙니다. 군집 결과와 실제 레이블이 우연히 맞더라도 그것은 검증 결과이지 군집화의 목적이 아닙니다.

## 지도학습 vs 비지도학습 성능 비교 실험

같은 데이터에서 두 패러다임의 결과를 수치로 비교합니다.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.metrics import (
    accuracy_score, silhouette_score, adjusted_rand_score
)
from sklearn.pipeline import make_pipeline
import numpy as np

X, y = load_iris(return_X_y=True)
sc = StandardScaler()
X_scaled = sc.fit_transform(X)

# 지도학습: 5-fold CV
pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
cv_acc = cross_val_score(pipe, X, y, cv=5, scoring="accuracy")
print("=== 지도학습 (Logistic Regression) ===")
print(f"5-fold CV Accuracy: {cv_acc.mean():.4f} ± {cv_acc.std():.4f}")

# 비지도학습: KMeans
km = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X_scaled)
sil = silhouette_score(X_scaled, km.labels_)
ari = adjusted_rand_score(y, km.labels_)  # 정답 레이블을 참조로만 사용
print("\n=== 비지도학습 (KMeans) ===")
print(f"Silhouette Score: {sil:.4f}  (군집 내부 품질)")
print(f"ARI vs true labels: {ari:.4f}  (참조용 - 실제 운영에선 사용 불가)")

# 비교 요약
print("\n패러다임 비교 요약:")
print(f"  지도학습 정확도:   {cv_acc.mean():.4f} (레이블 필요)")
print(f"  비지도 실루엣:     {sil:.4f} (레이블 불필요)")
print("  두 숫자는 직접 비교할 수 없습니다 - 목적이 다릅니다.")
```

ARI(Adjusted Rand Index)는 군집 품질을 정답 레이블과 비교하는 지표지만, 실제 운영에서는 레이블이 없으므로 탐색 단계에서만 씁니다.

## 피처 엔지니어링과 패러다임 선택의 관계

같은 원시 데이터에서도 어떻게 피처를 만드느냐에 따라 적합한 패러다임이 달라집니다.

```python
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, silhouette_score

# 원형 클러스터 데이터 생성
np.random.seed(42)
X, y = make_blobs(n_samples=300, centers=3, cluster_std=1.5, random_state=42)
sc = StandardScaler()
X_scaled = sc.fit_transform(X)

print("=== 패러다임별 성능 비교 (원본 피처) ===")

# 지도학습: 분류
Xtr, Xte, ytr, yte = train_test_split(X_scaled, y, test_size=0.2, stratify=y, random_state=42)
clf = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
print(f"분류 정확도 (원본): {accuracy_score(yte, clf.predict(Xte)):.4f}")

# 비지도학습: 군집
km = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X_scaled)
print(f"군집 Silhouette (원본): {silhouette_score(X_scaled, km.labels_):.4f}")

# 다항 피처 추가 후 비교
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X_scaled)
Xtr_p, Xte_p = train_test_split(X_poly, test_size=0.2, random_state=42)[0:2]
ytr_p, yte_p = train_test_split(y, test_size=0.2, random_state=42)[0:2]

print("\n=== 다항 피처 추가 후 ===")
clf_p = LogisticRegression(max_iter=2000).fit(Xtr_p, ytr_p)
print(f"분류 정확도 (다항): {accuracy_score(yte_p, clf_p.predict(Xte_p)):.4f}")
km_p = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X_poly)
print(f"군집 Silhouette (다항): {silhouette_score(X_poly, km_p.labels_):.4f}")
print(f"원본 피처 수: {X_scaled.shape[1]} → 다항 피처 수: {X_poly.shape[1]}")
```

피처 엔지니어링은 지도학습과 비지도학습 모두에 영향을 줍니다. 하지만 비지도학습에서는 더 조심해야 합니다 - 피처가 늘면 거리 측정이 더 어려워지기 때문입니다.

## 연습 문제

1. KMeans로 `iris`를 군집화한 뒤 실제 `y`와 교차표를 만들어 보세요.
2. 회귀로 보는 편이 좋은 문제 세 개와 분류로 보는 편이 좋은 문제 세 개를 적어 보세요.
3. 준지도학습이 정답인 상황 하나를 설명해 보세요.
4. `fetch_california_housing`을 분류 문제로 바꿔서(중간값 기준 이진화) 풀어 보세요.
5. 같은 iris 데이터를 지도학습과 비지도학습 두 방식으로 분석하고 결과를 비교해 보세요.
6. 군집 결과 레이블과 실제 y 레이블을 교차표(confusion matrix)로 비교해서 군집이 얼마나 의미 있는지 평가해 보세요.

## 정리

지도학습과 비지도학습의 경계는 데이터에 라벨이 있는지 하나로 갈리고, 분류·회귀·군집 같은 모든 갈래는 거기서 파생됩니다. 이 글에서는 ML 패러다임 비교부터 시니어 엔지니어는 이렇게 생각합니다까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **레이블이 있을 때와 없을 때 같은 알고리즘을 써도 될까요?**
  - 레이블 유무에 따라 패러다임이 달라지므로, 같은 알고리즘을 쓰더라도 평가 방법이 완전히 달라집니다. 실무에서는 지도학습과 비지도학습 사이의 중간 지대가 더 흔합니다.
- **분류와 회귀는 둘 다 지도학습인데 무엇이 다를까요?**
  - 분류는 이산 레이블을 예측하고, 회귀는 연속값을 예측합니다. 지표도 달라지므로 예측 대상의 유형을 먼저 확인해야 합니다.
- **군집화는 분류와 왜 전혀 다른 문제로 취급할까요?**
  - 군집화는 정답 레이블 없이 데이터의 내부 구조를 찾는 비지도 작업입니다. 결과는 검증 가능한 가설이지 정답이 아닙니다. 준지도학습은 적은 레이블과 많은 비레이블 데이터를 함께 쓰고, 자기지도학습은 데이터 자체에서 레이블을 만들어 학습합니다.

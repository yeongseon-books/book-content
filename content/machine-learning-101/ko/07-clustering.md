---
series: machine-learning-101
episode: 7
title: "Machine Learning 101 (7/10): Clustering"
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
  - Clustering
  - KMeans
  - DBSCAN
  - UnsupervisedLearning
seo_description: KMeans와 DBSCAN의 차이, K 선택, 표준화, 군집 해석의 책임까지 함께 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (7/10): Clustering

레이블이 없는 데이터에서 군집을 찾는 일은 분류보다 더 애매하게 느껴질 수 있습니다. 정답이 없으니 점수가 높다고 바로 안심할 수도 없고, 반대로 숫자가 조금 낮다고 틀렸다고 말하기도 어렵기 때문입니다. 그래서 군집화는 알고리즘 자체보다도 결과를 어떻게 해석할지까지 함께 생각해야 하는 주제입니다.

이 글은 머신러닝 101 시리즈의 7번째 글입니다. 여기서는 KMeans와 DBSCAN의 차이, `K`를 고르는 감각, 표준화가 군집 결과를 왜 바꿔 놓는지, 그리고 군집을 왜 정답이 아니라 가설로 봐야 하는지를 정리하겠습니다.

![Machine Learning 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/07/07-01-diagram.ko.png)
*Machine Learning 101 7장 흐름 개요*
> 군집화는 라벨 없는 데이터에서 그룹을 찾아내는 작업이지만, 피처 스케일과 K 결정 기준이 갖춰지지 않으면 의미 있는 그룹은 보이지 않습니다.

## 이 글에서 다룰 문제

- 정답 레이블이 없는데 군집이 좋은지 어떻게 판단할까요?
- KMeans와 DBSCAN은 어떤 상황에서 다르게 써야 할까요?
- `K`는 어떤 기준으로 정하고, 잘못 고르면 어떤 문제가 생길까요?
- 실루엣 점수와 엘보 방법은 각각 무엇을 측정할까요?
- 군집 결과를 실무에 활용할 때 가장 흔한 실수는 무엇일까요?

군집화는 세그먼테이션, 이상 탐지, 탐색적 데이터 분석의 기본 도구입니다. 많은 경우 지도학습 모델보다 먼저 등장합니다.

- **KMeans**: 군집 내 거리 합이 작아지도록 `K`개의 중심점을 찾습니다.
- **DBSCAN**: 밀도를 기준으로 군집을 만들고 노이즈를 분리합니다.
- **Inertia**: 중심점까지의 제곱거리 합입니다.
- **Silhouette**: 응집도와 분리도를 함께 보는 지표입니다.
- **Elbow**: `K`를 더 늘려도 개선 폭이 크지 않아지는 지점입니다.

## 적용 전과 후
**Before**: "`K = 3`이면 됐다"고 근거 없이 끝냅니다.

**After**: Elbow, Silhouette, 도메인 지식을 함께 써서 `K`를 고릅니다.

## 실습: 5단계로 보는 군집화

### 단계 1 — 데이터

```python
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
X = StandardScaler().fit_transform(load_iris().data)
```

### 단계 2 — KMeans

```python
from sklearn.cluster import KMeans
km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(X)
print("inertia:", km.inertia_)
```

### 단계 3 — Silhouette

```python
from sklearn.metrics import silhouette_score
print("sil:", silhouette_score(X, km.labels_))
```

### 단계 4 — Elbow

```python
ks = list(range(2, 8))
scores = [KMeans(n_clusters=k, n_init=10, random_state=0).fit(X).inertia_ for k in ks]
print(list(zip(ks, scores)))
```

### 단계 5 — DBSCAN

```python
from sklearn.cluster import DBSCAN
db = DBSCAN(eps=0.5, min_samples=5).fit(X)
print("labels:", set(db.labels_))
```

**예상 출력:** KMeans는 inertia와 silhouette 점수를 내고, DBSCAN은 `-1`을 포함할 수 있는 레이블 집합을 반환합니다. `-1`이 보이면 그 점들은 어느 군집에도 자연스럽게 속하지 않는 **노이즈 후보**라는 뜻입니다.

- KMeans는 `K`가 필요하고, DBSCAN은 `eps`가 필요합니다.
- 표준화 여부가 결과 전체를 바꿉니다.
- DBSCAN에서 `-1` 레이블은 노이즈를 뜻합니다.

## 군집화 알고리즘 비교

군집화 방법은 데이터 형태에 따라 결과가 크게 달라집니다.

| 알고리즘 | 군집 형태 | 노이즈 처리 | 하이퍼파라미터 | 적합한 상황 |
|---|---|---|---|---|
| KMeans | 볼록한 구 | 없음 | K | 구형 군집, 데이터 많을 때 |
| DBSCAN | 임의 형태 | 자동 분리 | eps, min_samples | 불규칙 형태, 이상치 있을 때 |
| AgglomerativeClustering | 계층 구조 | 없음 | n_clusters, linkage | 계층 관계 탐색 |
| GaussianMixture | 타원형 | 없음 | n_components | 확률 분포 기반 군집 |

```python
from sklearn.datasets import make_moons
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score

X, _ = make_moons(n_samples=300, noise=0.1, random_state=42)
X = StandardScaler().fit_transform(X)

# KMeans는 초승달 형태를 잘 못 잡습니다
km = KMeans(n_clusters=2, n_init=10, random_state=42).fit(X)
print("KMeans Silhouette:", silhouette_score(X, km.labels_).round(4))

# DBSCAN은 복잡한 형태를 더 잘 잡습니다
db = DBSCAN(eps=0.3, min_samples=5).fit(X)
n_clusters = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
print("DBSCAN 군집 수:", n_clusters)
if n_clusters > 1:
    mask = db.labels_ != -1
    print("DBSCAN Silhouette:", silhouette_score(X[mask], db.labels_[mask]).round(4))
```

초승달이나 링 형태의 데이터에서는 KMeans가 실패합니다. 데이터를 시각화하고 군집 형태를 먼저 파악하는 습관이 중요합니다.

## K 선택: Elbow와 Silhouette 함께 쓰기

최적의 K를 찾는 방법으로 두 기준을 동시에 봅니다.

```python
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

X = StandardScaler().fit_transform(load_iris().data)

print(f"{'K':>4} {'Inertia':>10} {'Silhouette':>12}")
for k in range(2, 9):
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
    sil = silhouette_score(X, km.labels_)
    print(f"{k:>4} {km.inertia_:>10.2f} {sil:>12.4f}")
```

엘보 포인트(Inertia 감소 폭이 급격히 줄어드는 K)와 Silhouette 최고점이 일치하면 그 K가 강력한 후보입니다. 두 기준이 다른 K를 가리키면 도메인 지식을 함께 참고합니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 표준화 전후로 군집이 크게 바뀌면, 데이터 구조보다 **거리 스케일**이 더 많은 일을 하고 있던 것입니다.
- Elbow와 Silhouette이 서로 다른 답을 가리키면, 그림을 직접 보고 **비즈니스 의미**까지 포함해 결정해야 합니다.
- DBSCAN이 거의 전부를 노이즈로 보내면, 데이터에 구조가 없다고 결론 내리기보다 `eps`, `min_samples`, 스케일을 먼저 다시 봐야 합니다.

## 자주 하는 실수

| 실수 | 결과 | 교정 방법 |
|---|---|---|
| 표준화 없이 거리 기반 사용 | 단위가 큰 피처가 군집 지배 | 항상 StandardScaler 적용 |
| 시각화 없이 K 고정 | 의미 없는 군집 | Elbow + Silhouette + 시각화 |
| KMeans로 볼록하지 않은 군집 | 군집이 섞임 | DBSCAN 또는 다른 방법 시도 |
| 군집 레이블을 정답처럼 다룸 | 잘못된 의사결정 | 별도 검증 단계 필요 |
| eps 고정 후 DBSCAN 적용 | 전부 노이즈 또는 전부 하나 | 여러 eps 값 실험 |

## 실무에서는 이렇게 나타납니다

고객 세그먼테이션, 색상 양자화, 이상 탐지 같은 문제는 군집화를 비지도 탐색의 표준 도구로 사용합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 군집은 답이 아니라 가설입니다.
- 다운스트림 결과로 다시 검증합니다.
- 시각화가 실제 의사결정을 크게 좌우합니다.
- 밀도 기반 방법은 이상치에 더 자연스럽게 대응합니다.
- 최종 `K`는 결국 비즈니스 의미까지 포함해 정합니다.

## 운영 체크리스트

- [ ] 거리 기반 방법 전에 항상 표준화합니다.
- [ ] Elbow와 Silhouette을 함께 봅니다.
- [ ] DBSCAN의 노이즈 레이블 의미를 알고 있습니다.
- [ ] 군집 결과를 가설로 다룹니다.

## 고차원 데이터에서의 군집화 전략

피처 수가 많으면 거리 기반 알고리즘의 성능이 떨어집니다. PCA로 차원을 줄인 뒤 군집화하는 전략을 씁니다.

```python
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
import numpy as np

X, y = load_digits(return_X_y=True)
print(f"원본 차원: {X.shape[1]}")

sc = StandardScaler()
X_scaled = sc.fit_transform(X)

# 차원 축소 없이 군집화
km_raw = KMeans(n_clusters=10, n_init=10, random_state=42).fit(X_scaled)
sil_raw = silhouette_score(X_scaled, km_raw.labels_, sample_size=1000, random_state=42)
ari_raw = adjusted_rand_score(y, km_raw.labels_)
print(f"원본 - Silhouette: {sil_raw:.4f}, ARI: {ari_raw:.4f}")

# PCA로 차원 축소 후 군집화
for n_comp in [10, 20, 30, 50]:
    pca = PCA(n_components=n_comp, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    km = KMeans(n_clusters=10, n_init=10, random_state=42).fit(X_pca)
    sil = silhouette_score(X_pca, km.labels_)
    ari = adjusted_rand_score(y, km.labels_)
    var = pca.explained_variance_ratio_.sum()
    print(f"PCA({n_comp:2d}) {var:.1%} 분산 - Silhouette: {sil:.4f}, ARI: {ari:.4f}")
```

`ARI(Adjusted Rand Index)`는 레이블이 있을 때 군집 품질을 정량화합니다. 탐색 단계에서 정답 레이블이 있다면 ARI로 알고리즘을 빠르게 비교할 수 있습니다.

## 군집 결과를 비즈니스에 활용하는 패턴

군집 레이블을 얻은 뒤 각 군집의 특성을 요약해서 비즈니스 인사이트를 도출하는 방법입니다.

```python
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np

X, y = load_iris(return_X_y=True)
feature_names = load_iris().feature_names

sc = StandardScaler()
X_scaled = sc.fit_transform(X)
km = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X_scaled)

print("군집별 피처 평균 (표준화 전 원본 스케일):")
print(f"{'피처':>25}", end="")
for k in range(3):
    print(f"  군집{k}", end="")
print()

for j, name in enumerate(feature_names):
    print(f"{name:>25}", end="")
    for k in range(3):
        mask = km.labels_ == k
        print(f"  {X[mask, j].mean():5.2f}", end="")
    print()

print(f"\n군집 크기: {np.bincount(km.labels_)}")
```

군집별로 피처 평균을 보면 "대형 꽃 그룹", "소형 꽃 그룹" 같은 비즈니스 언어로 설명할 수 있습니다. 숫자를 해석 가능한 언어로 변환하는 것이 군집화 결과를 활용하는 핵심 단계입니다.

## 계층적 군집화(Agglomerative Clustering)

KMeans와 DBSCAN 외에 계층 구조를 탐색하는 방법입니다.

```python
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
import numpy as np

X, y = load_iris(return_X_y=True)
sc = StandardScaler()
X_scaled = sc.fit_transform(X)

print(f"{'방법':>25} {'K':>4} {'Silhouette':>12} {'ARI':>7}")

# KMeans 비교 기준
km = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X_scaled)
print(f"{'KMeans':>25} {'3':>4} {silhouette_score(X_scaled, km.labels_):>12.4f} {adjusted_rand_score(y, km.labels_):>7.4f}")

# 계층적 군집화 - 다양한 연결 방식
for linkage in ["ward", "complete", "average", "single"]:
    for k in [2, 3, 4]:
        ac = AgglomerativeClustering(n_clusters=k, linkage=linkage).fit(X_scaled)
        sil = silhouette_score(X_scaled, ac.labels_)
        ari = adjusted_rand_score(y, ac.labels_)
        if k == 3:  # K=3만 출력
            print(f"{'Agglo-'+linkage:>25} {k:>4} {sil:>12.4f} {ari:>7.4f}")
```

`ward` 연결 방식은 병합 시 분산 증가를 최소화해서 일반적으로 가장 균형 잡힌 군집을 만듭니다. `single`은 가장 가까운 포인트 기준이라 노이즈에 취약합니다.

## 군집화 실전 적용: 고객 세그먼트 분석 패턴

실무에서 군집화 결과를 비즈니스 인사이트로 전환하는 방법입니다.

```python
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# 고객 데이터 시뮬레이션 (구매 횟수, 평균 금액, 최근 구매일)
np.random.seed(42)
n = 500
purchase_freq = np.concatenate([
    np.random.poisson(2, 150),    # 저빈도 고객
    np.random.poisson(8, 200),    # 중빈도 고객
    np.random.poisson(20, 150),   # 고빈도 고객
])
avg_amount = np.concatenate([
    np.random.normal(15, 3, 150),
    np.random.normal(45, 8, 200),
    np.random.normal(120, 20, 150),
])
recency = np.concatenate([
    np.random.uniform(60, 180, 150),
    np.random.uniform(10, 60, 200),
    np.random.uniform(1, 30, 150),
])

X_cust = np.column_stack([purchase_freq, avg_amount, recency])
feature_names = ["구매빈도", "평균금액", "최근구매일"]

sc = StandardScaler()
X_scaled = sc.fit_transform(X_cust)

# 최적 K 탐색
print(f"{'K':>4} {'Silhouette':>12} {'Inertia':>12}")
best_k, best_sil = 2, -1
for k in range(2, 8):
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_scaled)
    sil = silhouette_score(X_scaled, km.labels_)
    if sil > best_sil:
        best_k, best_sil = k, sil
    print(f"{k:>4} {sil:>12.4f} {km.inertia_:>12.1f}")

# 최적 K로 세그먼트 프로파일 생성
print(f"\n최적 K={best_k}로 세그먼트 프로파일:")
km_best = KMeans(n_clusters=best_k, n_init=10, random_state=42).fit(X_scaled)
print(f"{'세그먼트':>8} {'크기':>6}", end="")
for fn in feature_names:
    print(f"  {fn:>8}", end="")
print()
for seg in range(best_k):
    mask = km_best.labels_ == seg
    print(f"{'세그'+str(seg):>8} {mask.sum():>6}", end="")
    for j in range(3):
        print(f"  {X_cust[mask, j].mean():>8.1f}", end="")
    print()
```

군집별 피처 평균을 원본 스케일로 출력하면 "고빈도 고가 고객", "저빈도 저가 고객" 같은 비즈니스 언어로 세그먼트를 설명할 수 있습니다.

## 군집화 결과 안정성 검증: 반복 실험 패턴

KMeans는 초기 중심점을 무작위로 설정하기 때문에 실행마다 결과가 달라질 수 있습니다. 여러 시드로 반복 실험해 안정성을 확인하는 패턴입니다.

```python
import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score, adjusted_rand_score

X, y_true = make_blobs(n_samples=300, centers=4, random_state=0)

# 서로 다른 random_state로 여러 번 실행
results = []
for seed in range(10):
    km = KMeans(n_clusters=4, random_state=seed, n_init=10)
    labels = km.fit_predict(X)
    sil = silhouette_score(X, labels)
    ari = adjusted_rand_score(y_true, labels)
    results.append({"seed": seed, "silhouette": sil, "ari": ari,
                    "inertia": km.inertia_})

# 결과 요약
sils = [r["silhouette"] for r in results]
aris = [r["ari"] for r in results]
print(f"Silhouette  mean={np.mean(sils):.4f}  std={np.std(sils):.4f}")
print(f"ARI         mean={np.mean(aris):.4f}  std={np.std(aris):.4f}")

# std가 크면 초기값 민감 → n_init 늘리거나 k-means++ 확인
best = max(results, key=lambda r: r["silhouette"])
print(f"\n최적 seed={best['seed']}  silhouette={best['silhouette']:.4f}")
```

표준편차가 0.01 이하면 결과가 안정적입니다. `n_init` 기본값은 10이지만 데이터가 불균형하면 30 이상으로 늘리는 것이 좋습니다.

## 연습 문제

1. `K`를 2부터 7까지 바꿔 가며 Silhouette 점수를 비교해 보세요.
2. 표준화 전후의 KMeans 결과를 비교해 보세요.
3. `eps`를 0.3, 0.5, 1.0으로 바꿔 DBSCAN 군집 수를 세어 보세요.
4. `make_moons` 데이터에서 KMeans와 DBSCAN 결과를 나란히 시각화해 보세요.
5. 군집 결과로 얻은 레이블과 실제 `y` 레이블을 교차표(crosstab)로 비교해 보세요.

## 정리

군집화는 라벨 없는 데이터에서 그룹을 찾아내는 작업이지만, 피처 스케일과 K 결정 기준이 갖춰지지 않으면 의미 있는 그룹은 보이지 않습니다. 이 글에서는 적용 전과 후부터 시니어 엔지니어는 이렇게 생각합니다까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **정답 레이블이 없는데 군집이 좋은지 어떻게 판단할까요?**
  - Inertia(내부 응집도), Silhouette Score(응집도와 분리도의 균형), 도메인 지식을 함께 씁니다. 단일 숫자로 끝낼 수 없고, 시각화와 해석이 반드시 따릅니다.
- **KMeans와 DBSCAN은 어떤 상황에서 다르게 써야 할까요?**
  - KMeans는 구형 군집과 노이즈가 없는 데이터에 적합합니다. DBSCAN은 불규칙한 형태의 군집과 이상치가 있는 데이터에서 강점을 보입니다.
- **`K`는 어떤 기준으로 정해야 할까요?**
  - Elbow 방법으로 Inertia 감소 폭이 꺾이는 지점을 찾고, Silhouette 점수가 높은 K를 교차 확인한 뒤, 도메인 의미까지 고려해서 최종 결정합니다.

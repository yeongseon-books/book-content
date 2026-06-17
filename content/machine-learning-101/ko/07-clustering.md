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

## 실패 신호를 먼저 이렇게 읽습니다

- 표준화 전후로 군집이 크게 바뀌면, 데이터 구조보다 **거리 스케일**이 더 많은 일을 하고 있던 것입니다.
- Elbow와 Silhouette이 서로 다른 답을 가리키면, 그림을 직접 보고 **비즈니스 의미**까지 포함해 결정해야 합니다.
- DBSCAN이 거의 전부를 노이즈로 보내면, 데이터에 구조가 없다고 결론 내리기보다 `eps`, `min_samples`, 스케일을 먼저 다시 봐야 합니다.

## 자주 하는 실수 5가지

1. **표준화 없이 거리 기반 방법을 사용합니다.**
2. **시각적 확인 없이 `K`를 고릅니다.**
3. **KMeans가 볼록한 군집에 더 잘 맞는다는 점을 잊습니다.**
4. **군집 레이블을 정답처럼 다룹니다.**
5. **데이터 스케일을 고려하지 않고 DBSCAN의 `eps`를 고정합니다.**

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

## 연습 문제

1. `K`를 2부터 7까지 바꿔 가며 Silhouette 점수를 비교해 보세요.
2. 표준화 전후의 KMeans 결과를 비교해 보세요.
3. `eps`를 0.3, 0.5, 1.0으로 바꿔 DBSCAN 군집 수를 세어 보세요.

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째, 정답 레이블이 없는데 군집이 좋은지 어떻게 판단할까요. 둘째, KMeans와 DBSCAN은 어떤 상황에서 다르게 써야 할까요. 셋째, `K`는 어떤 기준으로 정하고, 잘못 고르면 어떤 문제가 생길까요. 이 기초를 잡아 두면 다음 단계로 넘어갈 때 훨씬 안정적입니다.

## 처음 질문으로 돌아가기

- **정답 레이블이 없는데 군집이 좋은지 어떻게 판단할까요?**
  - - KMeans는 `K`가 필요하고, DBSCAN은 `eps`가 필요합니다
- **KMeans와 DBSCAN은 어떤 상황에서 다르게 써야 할까요?**
  - - KMeans는 `K`가 필요하고, DBSCAN은 `eps`가 필요합니다
- **`K`는 어떤 기준으로 정해야 할까요?**
  - - KMeans는 `K`가 필요하고, DBSCAN은 `eps`가 필요합니다

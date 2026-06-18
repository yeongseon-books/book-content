---
title: "바이브코딩을 위한 머신러닝 기초 (7/10): AI가 KMeans를 썼는데 K를 어떻게 정할지"
series: machine-learning-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- MachineLearning
- AI코딩
- KMeans
- 군집화
seo_description: "바이브코딩 시대, AI가 KMeans를 생성했을 때 K 값을 근거 있게 정하는 방법과 군집 결과 해석 주의점을 정리합니다"
---

# 바이브코딩을 위한 머신러닝 기초 (7/10): AI가 KMeans를 썼는데 K를 어떻게 정할지

이 글은 바이브코딩을 위한 머신러닝 기초 시리즈의 7번째 글입니다.

고객 세그먼트 분석을 AI에게 요청했더니 `KMeans(n_clusters=3)`를 사용한 코드가 나왔습니다. 코드가 돌아가서 3개 그룹이 만들어졌습니다. "그런데 왜 3이에요?"라고 AI에게 물었더니 "임의로 설정했습니다. 도메인 지식이나 Elbow 방법으로 결정해야 합니다"라는 답이 돌아왔습니다.

이것이 군집화를 처음 접하는 바이브코더들이 가장 많이 마주치는 상황입니다. AI가 K를 임의로 설정하거나, "몇 개로 하시겠어요?"라고 되물을 때 어떻게 결정해야 하는지 모릅니다. 더 어려운 건 군집화에는 "정답"이 없어서, 결과가 좋은지 나쁜지 판단하는 방법도 처음에는 막막합니다.

군집화는 지도학습과 다르게 정답 레이블이 없습니다. 그래서 "얼마나 잘 됐는지"를 판단하는 방법이 완전히 다릅니다. K를 어떻게 정하는지, 결과를 어떻게 검증하는지 알면 AI와의 군집화 작업이 훨씬 체계적이 됩니다.

> 군집화 결과는 "정답"이 아니라 "가설"입니다. K=3이 나왔다고 고객이 정확히 3그룹인 게 아닙니다. AI도 이 가설을 검증해야 한다고 스스로 말해 주지 않습니다.

---

## 이 글에서 다룰 문제
- AI가 K를 임의로 설정했을 때 어떻게 더 좋은 K를 찾나요?
- Elbow 방법과 실루엣 점수는 각각 어떤 기준으로 K를 제안하나요?
- 표준화를 빼먹으면 군집 결과가 어떻게 달라지나요?
- KMeans와 DBSCAN은 어떤 상황에서 각각 더 나은가요?
- 군집 결과를 "가설"로 다룬다는 게 실무에서 무슨 뜻인가요?

## K 결정 방법 비교

| 방법 | 원리 | AI에게 요청 방법 |
|---|---|---|
| Elbow 방법 | K가 늘어도 inertia 감소폭이 줄어드는 지점 | "K=2~8 Elbow 플롯 그려줘" |
| 실루엣 점수 | 군집 내 응집도와 군집 간 분리도 | "K=2~8 실루엣 점수 계산해줘" |
| 도메인 지식 | 비즈니스 의미 있는 그룹 수 | "고객 등급이 3개면 K=3 시작" |
| Gap 통계 | 무작위 데이터 대비 군집 품질 | "Gap 통계로 K 추천해줘" |

## AI에게 K 결정 코드 요청하기

AI가 K=3을 임의로 설정했다면 이렇게 추가 요청합니다.

```python
# AI에게 요청: "K=2~8 범위에서 Elbow와 실루엣 점수 계산해줘"
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

ks = range(2, 9)
inertias = []
silhouettes = []

for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, km.labels_))

# 두 지표를 함께 보고 K 결정
for k, i, s in zip(ks, inertias, silhouettes):
    print(f"K={k}  inertia={i:.1f}  silhouette={s:.3f}")
```

이 결과를 보면 Elbow(inertia가 꺾이는 지점)와 실루엣(높을수록 좋음)이 제안하는 K를 확인할 수 있습니다. 두 지표가 같은 K를 가리키면 좋고, 다르면 도메인 지식으로 최종 결정합니다.

## Before / After

**Before**: AI가 K=3으로 군집화, 보고서에 "3그룹으로 나뉘었다"고 썼습니다. "왜 3그룹인가"라는 질문에 답하지 못했습니다.

**After**: "K=2~8 Elbow와 실루엣 점수 계산 + 표준화 포함해줘"라고 요청해서 K=4가 가장 좋다는 근거를 찾았습니다. "실루엣 점수 기준으로 K=4가 최적이며, 비즈니스 관점에서도 VIP/활성/잠재/휴면 4그룹이 의미 있습니다"라고 보고했습니다.

## 표준화를 빼먹으면 생기는 문제

```python
# 잘못된 코드: 표준화 없이 KMeans
km = KMeans(n_clusters=3).fit(X)  # 단위가 큰 피처가 지배

# 올바른 코드: 표준화 후 KMeans
from sklearn.preprocessing import StandardScaler
X_scaled = StandardScaler().fit_transform(X)
km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(X_scaled)
```

AI에게 "KMeans 전에 StandardScaler 적용해줘"라고 요청하면 됩니다. 나이(0~100), 연소득(0~10,000,000) 같이 단위가 다른 피처가 있을 때 표준화 없이는 연소득이 군집을 지배합니다.

## KMeans vs DBSCAN 선택하기

| 상황 | 추천 알고리즘 | AI 요청 방법 |
|---|---|---|
| K 수를 미리 정해야 함 | KMeans | "KMeans, n_clusters=K 로 군집화" |
| 이상치를 별도 처리하고 싶음 | DBSCAN | "DBSCAN으로 군집화, 노이즈 포인트 확인" |
| 불규칙한 모양의 군집 | DBSCAN | "원형이 아닌 군집 패턴 찾아줘" |
| 빠른 처리 필요 | KMeans | "대용량 데이터라서 KMeans 사용" |

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| K 근거 없이 K=3 사용 | "왜 3이에요?" 질문에 답 못 함 | Elbow + 실루엣 + 도메인 지식으로 결정 |
| 표준화 없이 KMeans | 단위 큰 피처가 군집을 지배 | StandardScaler 먼저 적용 |
| 군집 결과를 정답으로 발표 | 군집은 가설, 검증 필요 | "가설로서의 군집" 명시 |
| DBSCAN의 -1 레이블 무시 | 노이즈 포인트가 중요한 정보 | "-1 레이블 = 노이즈" 별도 분석 |

## AI에게 ML 관련 질문하는 팁

**군집화 완전한 요청 패턴:**

"고객 데이터 군집화 코드 만들어줘. 다음 조건 포함:
1. StandardScaler로 표준화 먼저
2. K=2~8 범위 Elbow 플롯
3. K=2~8 범위 실루엣 점수
4. 최적 K로 KMeans 실행
5. 각 군집의 평균값 출력(군집 특성 파악용)"

**군집 결과 해석 요청:**
- "각 군집의 피처 평균값을 비교해서 각 군집의 특성을 설명해줘"
- "DBSCAN으로도 군집화해서 KMeans 결과와 비교해줘"
- "군집 결과를 시각화해줘 (2D PCA로 축소해서)"

## 운영 체크리스트
- [ ] K를 임의로 설정하지 않고 Elbow 또는 실루엣으로 근거를 찾습니다
- [ ] KMeans 전에 표준화를 적용했는지 확인합니다
- [ ] 군집 결과를 "정답"이 아닌 "가설"로 다룹니다
- [ ] DBSCAN의 -1 레이블(노이즈) 의미를 확인합니다
- [ ] 군집별 평균값으로 각 군집의 특성을 해석합니다

## 처음 질문으로 돌아가기

- **AI가 K를 임의로 설정했을 때 어떻게 더 좋은 K를 찾나요?**
  - Elbow 방법으로 inertia 감소폭이 꺾이는 지점, 실루엣 점수가 가장 높은 K를 함께 확인하고 도메인 지식으로 최종 결정합니다.
- **표준화를 빼먹으면 어떻게 되나요?**
  - 단위가 큰 피처(예: 연소득)가 군집 계산을 지배해서 단위가 작은 피처(예: 나이)의 영향이 사라집니다. 반드시 StandardScaler를 먼저 적용해야 합니다.
- **KMeans와 DBSCAN은 언제 각각 쓰나요?**
  - K를 미리 정할 수 있고 원형에 가까운 군집을 찾을 때 KMeans, 이상치를 자동으로 제거하고 불규칙한 모양의 군집을 찾을 때 DBSCAN이 적합합니다.
- **군집 결과를 "가설"로 다룬다는 게 무슨 뜻인가요?**
  - K=4가 나왔다고 고객이 정확히 4그룹인 것이 아닙니다. "이 데이터에서는 4그룹이 가장 응집도 높게 구분된다"는 가설이고, 각 군집의 특성을 해석하고 비즈니스 의미를 붙이는 것은 별도의 작업입니다.
- **DBSCAN의 -1 레이블은 어떻게 처리하나요?**
  - -1은 어느 군집에도 속하지 않는 노이즈 포인트입니다. 이상치일 수 있어서 별도로 분석하거나 제거를 고려합니다. AI에게 "-1 레이블 포인트를 별도 DataFrame으로 추출해줘"라고 요청할 수 있습니다.

## 정리

군집화에서 K는 임의로 정하는 게 아니라 데이터를 보고 결정해야 합니다. AI에게 Elbow와 실루엣 점수 계산을 요청하면 근거 있는 K를 찾을 수 있습니다. 표준화는 필수이고, 군집 결과는 정답이 아닌 가설로 다루며, 군집별 평균값으로 각 군집의 특성을 해석하는 것까지가 군집화 작업의 완성입니다.

## 참고 자료
### 공식 문서
- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Google ML Crash Course](https://developers.google.com/machine-learning/crash-course)
### 관련 시리즈
- [Data Science 101](../../data-science-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 머신러닝 기초 (1/10): ML이 뭔지 알아야 AI에게 제대로 시킬 수 있다](./01-what-is-machine-learning.md)
- [바이브코딩을 위한 머신러닝 기초 (2/10): 지도학습 vs 비지도학습 — AI에게 어떤 유형인지 말해줘야](./02-supervised-unsupervised.md)
- [바이브코딩을 위한 머신러닝 기초 (3/10): AI가 전체 데이터로 학습시켰다 — train/test split이 왜 필요한지](./03-training-test-split.md)
- [바이브코딩을 위한 머신러닝 기초 (4/10): AI가 선형 회귀를 썼는데 맞는 선택인지 판단하려면](./04-linear-regression.md)
- [바이브코딩을 위한 머신러닝 기초 (5/10): AI가 로지스틱 회귀를 쓴 이유를 이해하려면](./05-logistic-regression.md)
- [바이브코딩을 위한 머신러닝 기초 (6/10): AI가 랜덤 포레스트를 추천했다 — 트리 모델 이해하기](./06-tree-models.md)
- **AI가 KMeans를 썼는데 K를 어떻게 정할지 (현재 글)**
- [바이브코딩을 위한 머신러닝 기초 (8/10): AI 모델이 훈련에서만 잘 된다 — 과적합 이해하기](./08-overfitting.md)
- [바이브코딩을 위한 머신러닝 기초 (9/10): AI가 "정확도 95%"라고 했는데 진짜 좋은 건지 — 평가 지표](./09-evaluation-metrics.md)
- [바이브코딩을 위한 머신러닝 기초 (10/10): AI와 함께 ML 프로젝트 처음부터 끝까지](./10-ml-project-workflow.md)

<!-- toc:end -->
Tags: 바이브코딩, MachineLearning, AI코딩, KMeans, 군집화

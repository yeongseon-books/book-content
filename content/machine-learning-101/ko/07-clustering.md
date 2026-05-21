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

## 먼저 던지는 질문

- 정답 레이블이 없는데 군집이 좋은지 어떻게 판단할까요?
- KMeans와 DBSCAN은 어떤 상황에서 다르게 써야 할까요?
- `K`는 어떤 기준으로 정해야 할까요?

## 왜 중요한가

군집화는 세그먼테이션, 이상 탐지, 탐색적 데이터 분석의 기본 도구입니다. 많은 경우 지도학습 모델보다 먼저 등장합니다.

## 한눈에 보는 개념

## 핵심 용어

- **KMeans**: 군집 내 거리 합이 작아지도록 `K`개의 중심점을 찾습니다.
- **DBSCAN**: 밀도를 기준으로 군집을 만들고 노이즈를 분리합니다.
- **Inertia**: 중심점까지의 제곱거리 합입니다.
- **Silhouette**: 응집도와 분리도를 함께 보는 지표입니다.
- **Elbow**: `K`를 더 늘려도 개선 폭이 크지 않아지는 지점입니다.

## Before/After

**Before**: "`K = 3`이면 됐다"고 근거 없이 끝냅니다.

**After**: Elbow, Silhouette, 도메인 지식을 함께 써서 `K`를 고릅니다.

## 실습: 5단계로 보는 군집화

### Step 1 — 데이터

```python
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
X = StandardScaler().fit_transform(load_iris().data)
```

### Step 2 — KMeans

```python
from sklearn.cluster import KMeans
km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(X)
print("inertia:", km.inertia_)
```

### Step 3 — Silhouette

```python
from sklearn.metrics import silhouette_score
print("sil:", silhouette_score(X, km.labels_))
```

### Step 4 — Elbow

```python
ks = list(range(2, 8))
scores = [KMeans(n_clusters=k, n_init=10, random_state=0).fit(X).inertia_ for k in ks]
print(list(zip(ks, scores)))
```

### Step 5 — DBSCAN

```python
from sklearn.cluster import DBSCAN
db = DBSCAN(eps=0.5, min_samples=5).fit(X)
print("labels:", set(db.labels_))
```

**예상 출력:** KMeans는 inertia와 silhouette 점수를 내고, DBSCAN은 `-1`을 포함할 수 있는 레이블 집합을 반환합니다. `-1`이 보이면 그 점들은 어느 군집에도 자연스럽게 속하지 않는 **노이즈 후보**라는 뜻입니다.

## 이 코드에서 먼저 봐야 할 점

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

## 체크리스트

- [ ] 거리 기반 방법 전에 항상 표준화합니다.
- [ ] Elbow와 Silhouette을 함께 봅니다.
- [ ] DBSCAN의 노이즈 레이블 의미를 알고 있습니다.
- [ ] 군집 결과를 가설로 다룹니다.

## 연습 문제

1. `K`를 2부터 7까지 바꿔 가며 Silhouette 점수를 비교해 보세요.
2. 표준화 전후의 KMeans 결과를 비교해 보세요.
3. `eps`를 0.3, 0.5, 1.0으로 바꿔 DBSCAN 군집 수를 세어 보세요.

## 정리

클러스터링은 숨겨진 구조를 드러내는 도구입니다. KMeans는 빠르고 단순하지만 `K`를 요구하고, DBSCAN은 노이즈를 자연스럽게 다루지만 밀도 파라미터 선택이 중요합니다.

이 글에서 기억할 핵심은 네 가지입니다. 첫째, 군집화는 정답 맞히기보다 구조 탐색에 가깝습니다. 둘째, 표준화는 결과를 바꿀 정도로 중요합니다. 셋째, Elbow와 Silhouette은 보조 도구이지 최종 판단 자체는 아닙니다. 넷째, 군집 레이블은 항상 해석 단계를 거쳐야 합니다.

다음 글에서는 Overfitting과 Regularization을 통해 모델이 잡음을 외우는 문제와 이를 제어하는 방법을 살펴보겠습니다.

## 실전 확장: 학습·평가 파이프라인 통합

입문 단계에서 `fit()` 한 번으로 결과를 확인하면 모델이 잘 동작하는 것처럼 보이지만, 실무에서는 같은 데이터로 학습과 평가를 동시에 수행하면 성능이 과대평가되기 쉽습니다. 따라서 최소한 `train/validation/test` 구분을 갖춘 뒤, 피처 전처리와 모델 학습, 하이퍼파라미터 탐색, 최종 평가를 분리해야 합니다. 아래 예시는 분류 문제에서 재현 가능한 기준선을 만드는 기본 템플릿입니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

X, y = load_breast_cancer(return_X_y=True)

X_train_full, X_test, y_train_full, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_train_full, y_train_full, test_size=0.25, random_state=42, stratify=y_train_full
)

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=2000))
])

param_grid = {
    "model__C": [0.01, 0.1, 1.0, 10.0],
    "model__penalty": ["l2"],
    "model__solver": ["lbfgs"]
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
search = GridSearchCV(
    estimator=pipe,
    param_grid=param_grid,
    scoring="f1",
    cv=cv,
    n_jobs=-1
)
search.fit(X_train, y_train)

val_pred = search.predict(X_val)
val_proba = search.predict_proba(X_val)[:, 1]

print("Best Params:", search.best_params_)
print("Validation ROC-AUC:", roc_auc_score(y_val, val_proba))
print(classification_report(y_val, val_pred, digits=4))
print(confusion_matrix(y_val, val_pred))
```

핵심은 세 가지입니다. 첫째, 전처리(`StandardScaler`)를 파이프라인에 넣어 데이터 누수를 방지합니다. 둘째, `GridSearchCV`는 훈련 세트 내부에서만 교차검증을 수행하므로 검증 세트를 따로 남겨 둔 의미가 유지됩니다. 셋째, 검증 단계에서 `classification_report`와 `ROC-AUC`를 함께 확인해 임계값 민감도와 순위 품질을 동시에 점검합니다.

## 분류 지표를 함께 읽는 방법

정확도 하나만 보면 클래스 불균형 상황에서 착시가 발생합니다. 예를 들어 양성 비율이 5%인 데이터에서 모두 음성으로 예측해도 정확도는 95%가 될 수 있습니다. 그래서 아래 지표를 함께 봐야 합니다.

| 지표 | 질문 | 해석 포인트 |
| --- | --- | --- |
| Precision | 양성이라고 예측한 것 중 실제 양성 비율은? | 오탐(False Positive) 비용이 큰 문제에서 중요합니다. |
| Recall | 실제 양성 중 모델이 잡아낸 비율은? | 미탐(False Negative) 비용이 큰 문제에서 중요합니다. |
| F1-score | Precision과 Recall의 균형은 어떤가? | 한쪽만 높은 모델을 걸러내는 데 유용합니다. |
| ROC-AUC | 다양한 임계값에서 양성과 음성을 얼마나 잘 분리하나? | 임계값 고정 전 모델 비교에 적합합니다. |

실무에서는 보통 지표 우선순위를 도메인 비용으로 정합니다. 예를 들어 사기 탐지는 Recall을 높게 두고, 마케팅 리드 스코어링은 Precision을 우선 둘 수 있습니다. 즉, 좋은 모델이란 "절대적 최고 점수"가 아니라 "비즈니스 손실을 최소화하는 점수 조합"입니다.

## 혼동 행렬을 운영 관점으로 해석하기

혼동 행렬은 네 칸 숫자 자체보다, 어떤 유형의 오류가 반복되는지 보는 도구입니다.

- True Positive: 맞게 탐지한 양성입니다.
- True Negative: 맞게 걸러낸 음성입니다.
- False Positive: 잘못 탐지한 양성입니다.
- False Negative: 놓친 양성입니다.

예를 들어 의료 스크리닝에서는 False Negative가 치명적일 수 있어 Recall 중심 임계값 조정이 필요합니다. 반대로 자동 승인 심사에서는 False Positive가 비용을 키우므로 Precision 중심 정책이 필요할 수 있습니다. 따라서 모델 개선 회의에서는 "정확도 몇 점"보다 "현재 오류의 대부분이 FP인지 FN인지"를 먼저 공유하는 편이 의사결정에 유리합니다.

## 교차검증과 모델 비교 표준화

한 번의 분할 결과만으로 모델을 비교하면 우연에 휘둘립니다. 최소 5-fold 교차검증으로 분산을 같이 봐야 합니다.

```python
from sklearn.model_selection import cross_validate
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

candidates = {
    "logreg": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=2000))
    ]),
    "dt": DecisionTreeClassifier(max_depth=5, random_state=42),
    "rf": RandomForestClassifier(n_estimators=300, random_state=42)
}

for name, est in candidates.items():
    scores = cross_validate(
        est,
        X_train_full,
        y_train_full,
        cv=5,
        scoring={"acc": "accuracy", "f1": "f1", "auc": "roc_auc"},
        n_jobs=-1
    )
    print(name)
    print("acc:", scores["test_acc"].mean(), "+/-", scores["test_acc"].std())
    print("f1 :", scores["test_f1"].mean(), "+/-", scores["test_f1"].std())
    print("auc:", scores["test_auc"].mean(), "+/-", scores["test_auc"].std())
```

평균 점수만 비슷하면 표준편차가 더 작은 모델을 운영 초기 선택지로 두는 것이 안전합니다. 이후 트래픽과 데이터가 쌓이면 복잡한 모델로 단계적으로 전환하면 됩니다.

## 피처 엔지니어링에서 초기에 점검할 항목

피처 엔지니어링은 고급 기법보다 기본 위생이 먼저입니다.

1. 결측치 처리 규칙이 학습/추론에서 동일한지 확인합니다.
2. 범주형 인코딩 방식(One-Hot, Target Encoding 등)의 누수 가능성을 점검합니다.
3. 날짜 피처는 주기성(요일, 월, 시간대)을 분해해 반영합니다.
4. 로그 스케일 변환이 긴 꼬리 분포를 안정화하는지 확인합니다.
5. 파생 피처 추가 전후에 검증 지표가 실제로 개선되는지 기록합니다.

아래처럼 `ColumnTransformer`와 파이프라인을 결합하면 전처리 일관성이 높아집니다.

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

# df는 예시 데이터프레임이라고 가정합니다.
num_cols = ["age", "income", "tenure_month"]
cat_cols = ["region", "device_type"]

a_preprocess = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]), num_cols),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ]), cat_cols)
])
```

이 구조를 사용하면 학습 시점의 전처리 규칙이 추론 시점에도 동일하게 재현됩니다. 문서화가 쉬워지고, 팀 내 인수인계 비용도 줄어듭니다.

## 운영 직전 최종 점검 체크리스트

- 데이터 분할 기준(`random_state`, `stratify`)이 코드에 고정되어 있습니다.
- 평가 지표가 비즈니스 비용 구조와 연결되어 있습니다.
- 혼동 행렬 기반으로 FP/FN 대응 정책이 합의되어 있습니다.
- 교차검증 평균뿐 아니라 분산까지 비교했습니다.
- 피처 전처리와 모델을 하나의 파이프라인으로 묶었습니다.

이 다섯 가지를 만족하면, 단순히 "모델이 돌아간다" 수준을 넘어 "재현 가능하고 설명 가능한 학습 시스템"에 가까워집니다.


## 실전 보강: 손실 함수, 검증 곡선, 비교표를 한 번에 정리

이 절에서는 모델을 바꿔 가며 점수를 숫자 하나로만 보지 않고, 손실 함수의 형태와 혼동 행렬, 하이퍼파라미터 곡선을 함께 읽는 방법을 정리합니다. 핵심은 모델 교체보다 검증 루틴을 고정하는 것입니다.

### 손실 함수 관점으로 다시 보기

분류와 회귀는 예측 대상을 다르게 다루므로 손실 함수도 다릅니다.

- 선형 회귀: \(\mathcal{L} = \frac{1}{n}\sum_{i=1}^n (y_i-\hat{y}_i)^2\)
- 로지스틱 회귀: \(\mathcal{L} = -\frac{1}{n}\sum_{i=1}^n [y_i\log p_i + (1-y_i)\log(1-p_i)]\)
- 트리 계열 분류: Gini 또는 entropy 감소량을 기준으로 분할

수식 자체보다 중요한 점은, 손실 함수가 잘못 정의되면 같은 데이터에서도 완전히 다른 모델이 선택된다는 사실입니다.

### scikit-learn 기준 검증 코드 템플릿

```python
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=3000))
])

param_grid = {
    "model__C": [0.01, 0.1, 1.0, 10.0, 30.0],
    "model__class_weight": [None, "balanced"],
    "model__solver": ["lbfgs"]
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
search = GridSearchCV(
    pipe,
    param_grid=param_grid,
    scoring="f1",
    cv=cv,
    n_jobs=-1,
    return_train_score=True
)
search.fit(X_train, y_train)

print("best:", search.best_params_)
print("best_f1:", search.best_score_)
```

이 구조를 고정해 두면 모델을 바꿔도 실험 비교가 쉬워지고, 팀 내 리뷰 기준도 통일됩니다.

### 혼동 행렬을 운영 신호로 해석

예를 들어 다음과 같은 혼동 행렬이 나왔다고 가정합니다.

| 실제 \ 예측 | 음성 | 양성 |
|---|---:|---:|
| 음성 | 880 | 70 |
| 양성 | 35 | 215 |

이 경우 정밀도와 재현율은 모두 양호해 보이지만, 비용 구조가 "양성을 놓치면 큰 손실"이라면 `35`개의 FN을 더 줄이는 방향으로 임계값을 조정해야 합니다. 반대로 과도한 알람 비용이 문제라면 FP `70`을 줄이는 쪽이 우선입니다. 즉, 모델 점수는 의사결정을 대체하지 않고 의사결정을 돕는 재료입니다.

### 하이퍼파라미터 곡선 읽기

학습/검증 곡선을 함께 보면 과적합과 과소적합을 빠르게 구분할 수 있습니다.

```python
import numpy as np
from sklearn.model_selection import validation_curve

param_range = np.logspace(-3, 2, 8)
train_scores, val_scores = validation_curve(
    LogisticRegression(max_iter=3000),
    X_train_scaled,
    y_train,
    param_name="C",
    param_range=param_range,
    scoring="f1",
    cv=5
)

print("C values:", param_range)
print("train mean:", train_scores.mean(axis=1))
print("valid mean:", val_scores.mean(axis=1))
```

- 왼쪽 구간에서 train/valid가 모두 낮으면 과소적합 신호입니다.
- 오른쪽 구간에서 train만 높고 valid가 떨어지면 과적합 신호입니다.
- 두 곡선 간격이 작고 valid가 높은 지점이 운영 시작점으로 안전합니다.

### 모델 비교표 예시

아래 표처럼 동일한 분할 기준에서 평균과 분산을 함께 기록해야 비교가 공정해집니다.

| 모델 | CV F1 평균 | CV F1 표준편차 | 학습 시간(상대) | 해석 가능성 |
|---|---:|---:|---:|---|
| 로지스틱 회귀 | 0.911 | 0.012 | 1x | 높음 |
| 결정 트리 | 0.887 | 0.031 | 1x | 중간 |
| 랜덤 포레스트 | 0.924 | 0.015 | 4x | 중간 |

여기서 바로 "최고 점수 모델"만 고르지 않고, 분산과 운영 비용을 함께 고려해야 배포 이후의 품질이 안정됩니다.

### 7번째 글 기준 실전 체크

- 이 글에서 다룬 핵심 개념을 모델 선택 기준표와 연결해 문서화합니다.
- 데이터 분할, 스케일링, 임계값, 지표 계산 순서를 코드로 고정합니다.
- 검증 결과는 평균 점수와 표준편차를 함께 남깁니다.
- 혼동 행렬 기반 FP/FN 대응 전략을 운영 정책에 연결합니다.
- 다음 실험에서도 같은 템플릿을 재사용해 비교 가능성을 유지합니다.


### 추가 앵커: 학습/검증 곡선 해석 예시

아래는 하이퍼파라미터를 바꿨을 때 train/validation 곡선을 어떻게 읽는지 보여 주는 예시입니다.

| 구간 | train 점수 | validation 점수 | 해석 |
|---|---:|---:|---|
| 규제가 너무 강한 구간 | 낮음 | 낮음 | 과소적합 가능성이 큽니다. |
| 적정 규제 구간 | 높음 | 높음 | 일반화 관점에서 우선 후보입니다. |
| 규제가 너무 약한 구간 | 매우 높음 | 하락 | 과적합 가능성이 큽니다. |

운영에서는 최고 점수 하나보다, 곡선이 안정적으로 유지되는 구간을 고르는 편이 재학습 주기에서 유리합니다.

### 추가 앵커: 혼동 행렬 기반 임계값 조정 루프

```python
from sklearn.metrics import precision_score, recall_score, f1_score

thresholds = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
for t in thresholds:
    pred_t = (y_prob >= t).astype(int)
    p = precision_score(y_valid, pred_t)
    r = recall_score(y_valid, pred_t)
    f = f1_score(y_valid, pred_t)
    print(f"t={t:.1f}  precision={p:.3f}  recall={r:.3f}  f1={f:.3f}")
```

이 루프는 모델 교체 없이도 성능 체감을 크게 바꿀 수 있습니다. 특히 알람 시스템처럼 FP/FN 비용이 비대칭인 문제에서 효과가 큽니다.

### 추가 앵커: 모델 비교 의사결정 규칙

- 평균 점수 차이가 아주 작다면 표준편차가 더 작은 모델을 우선합니다.
- 점수 이득이 1% 미만이면 추론 비용과 운영 복잡도를 함께 계산합니다.
- 설명 가능성이 중요한 도메인에서는 해석 가능한 모델을 기본값으로 둡니다.
- 데이터가 늘어날 가능성이 크면 재학습 파이프라인 단순성을 더 높은 우선순위로 둡니다.
- 최종 선택 사유는 표와 로그로 남겨 다음 실험의 기준선으로 사용합니다.


### 추가 앵커: 재현성 로그 템플릿

실험 로그에는 최소한 다음 항목을 고정합니다.

| 항목 | 예시 |
|---|---|
| 데이터 스냅샷 | `dataset_version=2026-05-15` |
| 분할 시드 | `random_state=42` |
| 핵심 하이퍼파라미터 | `C=1.0`, `max_depth=5` |
| 평가 지표 | `f1`, `roc_auc`, `mae` |
| 실행 환경 | `python=3.11`, `sklearn=1.5.x` |

이 다섯 줄만 지켜도 같은 실험을 다시 돌리는 비용이 크게 줄어듭니다.


운영 팁으로는 실험 노트에 "이번 변경이 데이터, 전처리, 모델, 임계값 중 어디를 건드렸는지"를 한 줄로 남기는 습관이 중요합니다. 같은 점수 변화라도 원인 축이 달라지면 다음 대응 전략이 완전히 달라지기 때문입니다.


또한 모델 비교 회의에서는 "이번 실험으로 줄어든 오류 유형이 무엇인지"를 숫자로 남겨야 합니다. 예를 들어 FP가 20건 줄고 FN이 5건 늘었다면, 운영팀과 함께 비용을 환산해 변경 승인 여부를 결정하는 방식이 안전합니다. 이렇게 오류 유형 단위로 기록하면 다음 분기 모델 개선의 우선순위도 명확해집니다.

## 처음 질문으로 돌아가기

- **정답 레이블이 없는데 군집이 좋은지 어떻게 판단할까요?**
  - 본문의 기준은 Clustering를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **KMeans와 DBSCAN은 어떤 상황에서 다르게 써야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`K`는 어떤 기준으로 정해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Machine Learning 101 (1/10): Machine Learning이란 무엇인가?](./01-what-is-machine-learning.md)
- [Machine Learning 101 (2/10): 지도학습과 비지도학습](./02-supervised-and-unsupervised.md)
- [Machine Learning 101 (3/10): 훈련/테스트 분할](./03-train-test-split.md)
- [Machine Learning 101 (4/10): 선형 회귀](./04-linear-regression.md)
- [Machine Learning 101 (5/10): 로지스틱 회귀](./05-logistic-regression.md)
- [Machine Learning 101 (6/10): 결정 트리와 랜덤 포레스트](./06-decision-tree-and-random-forest.md)
- **Clustering (현재 글)**
- 과적합과 정규화 (예정)
- 모델 평가 (예정)
- ML 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Clustering](https://scikit-learn.org/stable/modules/clustering.html)
- [scikit-learn — Silhouette analysis](https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html)
- [DBSCAN — Ester et al. (1996)](https://www.aaai.org/Papers/KDD/1996/KDD96-037.pdf)
- [StatQuest — KMeans](https://www.youtube.com/watch?v=4b5d3muPQmA)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/machine-learning-101/ko)

Tags: MachineLearning, Clustering, KMeans, DBSCAN, UnsupervisedLearning

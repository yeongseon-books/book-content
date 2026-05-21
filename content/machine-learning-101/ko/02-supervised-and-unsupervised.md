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

이 글은 Machine Learning 101 시리즈의 두 번째 글입니다. 여기서는 지도학습과 비지도학습의 경계를 정리하고, 분류·회귀·군집이 각각 어떤 질문에 답하는지 비교해 보겠습니다.

## 먼저 던지는 질문

- 레이블이 있을 때와 없을 때 같은 알고리즘을 써도 될까요?
- 분류와 회귀는 둘 다 지도학습인데 무엇이 다를까요?
- 군집화는 분류와 왜 전혀 다른 문제로 취급할까요?

## 큰 그림

![Machine Learning 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/02/02-01-diagram.ko.png)

*Machine Learning 101 2장 흐름 개요*

이 그림은 이 장의 핵심 개념들이 어떻게 연결되는지 보여줍니다.

## ML 패러다임 비교

| 유형 | 목표 | 출력 | 대표 알고리즘 |
|---|---|---|---|
| 분류(Classification) | 이산 레이블 예측 | 0, 1, 2 등 | Logistic Regression, Decision Tree |
| 회귀(Regression) | 연속값 예측 | 123.4, -0.89 등 | Linear Regression, SVR |
| 군집(Clustering) | 비슷한 점 묶기 | cluster ID | KMeans, DBSCAN |
| 차원축소(Dimensionality Reduction) | 피처 압축 | 낮은 차원 X | PCA, t-SNE |

분류와 회귀는 둘 다 지도학습이지만, 예측하려는 대상이 다릅니다. 군집과 차원축소는 비지도학습으로, 레이블 없이 데이터의 구조를 찾는 문제입니다.


## 왜 중요한가

패러다임을 잘못 고르면 이후 모델 개선은 거의 의미가 없어집니다. 문제 프레이밍이 첫 번째 레버인 이유가 여기에 있습니다. 연속값을 예측해야 하는데 분류처럼 접근하거나, 정답 레이블이 없는데 지도학습 지표를 기대하면 모델보다 문제 정의가 먼저 어긋납니다.

## 한눈에 보는 개념

## 핵심 용어

- **지도학습(Supervised learning)**: `(X, y)` 쌍에서 함수를 학습합니다.
- **비지도학습(Unsupervised learning)**: `X`만 보고 구조를 발견합니다.
- **분류(Classification)**: 이산적인 레이블을 예측합니다.
- **회귀(Regression)**: 연속적인 값을 예측합니다.
- **군집화(Clustering)**: 거리나 밀도를 기준으로 비슷한 점들을 묶습니다.

## Before/After

**Before**: "머신러닝은 회귀 한 줄이면 된다"고 생각해서 패러다임 구분을 건너뜁니다.

**After**: 먼저 **레이블 유무**를 확인하고, 그다음 **분류인지 회귀인지**를 정한 뒤 알고리즘을 고릅니다.

## 실습: 5단계로 패러다임 비교하기

### Step 1 — 데이터 로드

```python
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
```

### Step 2 — 지도학습 분류

```python
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(max_iter=1000).fit(X, y)
print("clf acc:", clf.score(X, y))
```

### Step 3 — 회귀 데이터셋

```python
from sklearn.datasets import fetch_california_housing
Xr, yr = fetch_california_housing(return_X_y=True)
```

### Step 4 — 회귀 모델

```python
from sklearn.linear_model import LinearRegression
reg = LinearRegression().fit(Xr, yr)
print("R^2:", reg.score(Xr, yr))
```

### Step 5 — 비지도 군집화

```python
from sklearn.cluster import KMeans
km = KMeans(n_clusters=3, n_init=10).fit(X)
print("inertia:", km.inertia_)
```

**예상 출력:** 분류 예제는 정확도, 회귀 예제는 `R^2`, 군집화 예제는 inertia를 출력합니다. 숫자가 모두 성능처럼 보이지만 **서로 같은 의미가 아니며 직접 비교할 수도 없습니다.**

## 준지도학습과 자기지도학습

실무에서는 지도학습과 비지도학습 사이의 중간 지대가 더 흔합니다.

### 준지도학습(Semi-supervised learning)

- 레이블이 있는 데이터는 적고, 레이블이 없는 데이터는 많을 때 사용합니다.
- 예시: 이미지 100장은 사람이 레이블링했고, 10,000장은 레이블이 없을 때 준지도 기법을 쓰면 레이블링 비용을 크게 줄일 수 있습니다.

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
print("Inertia:", km.inertia_)  # 응집도 (낙을수록 좋음)

# 지도: 분류
clf = LogisticRegression(max_iter=1000).fit(X, y)
print("Accuracy:", clf.score(X, y))  # 정확도
```

군집 결과의 inertia와 분류 결과의 accuracy는 서로 비교할 수 없습니다. 비지도학습은 정답이 없기 때문에 해석이 더 어렵습니다.
## 이 코드에서 먼저 봐야 할 점

- `clf.score`는 정확도, `reg.score`는 결정계수(R-squared), `km.inertia_`는 군집 응집도를 뜻합니다. **지표가 다르면 숫자의 의미도 달라집니다.**
- `KMeans(n_init=...)`는 재현성과 안정성에 직접 영향을 줍니다.
- 비지도학습은 정답이 없기 때문에 결과 해석이 더 어렵습니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 팀이 레이블이 무엇인지 답하지 못하면, 알고리즘보다 먼저 **예측 결과가 바꾸려는 행동**이 무엇인지 다시 물어야 합니다.
- 군집 결과를 곧바로 정답 클래스처럼 쓰려 하면, 먼저 **후속 검증 방법**을 정해야 합니다.
- 지표 해석이 자꾸 꼬인다면, 감독된 문제의 점수와 비지도학습의 응집도 숫자를 같은 표에서 읽고 있지 않은지 확인해야 합니다.

## 자주 하는 실수 5가지

1. **회귀 문제를 분류로 풀거나 그 반대로 접근합니다.**
2. **부분적으로만 레이블이 있는 데이터를 버리고 준지도학습 가능성을 놓칩니다.**
3. **군집 결과를 마치 정답처럼 다룹니다.**
4. **시각화도 하지 않은 채 군집 수 `K`를 고정합니다.**
5. **거리 기반 알고리즘 전에 표준화를 생략합니다.**

## 실무에서는 이렇게 나타납니다

스팸 필터와 사기 탐지는 분류, 가격 책정과 수요 예측은 회귀, 고객 세그먼트 분석은 군집화에 기대는 경우가 많습니다. 실제 시스템은 이 셋을 함께 섞어 사용하면서 랭킹과 추천을 만듭니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 순서가 중요합니다. **문제 → 지표 → 패러다임** 순으로 정합니다.
- 비지도학습은 초기에 탐색용으로 매우 유용합니다.
- 업계에서는 준지도학습 상황이 오히려 더 흔합니다.
- 강화학습은 가장 마지막에 꺼내는 카드에 가깝습니다.
- 알고리즘 선택보다 **레이블링 전략**이 더 큰 차이를 만들기도 합니다.

## 체크리스트

- [ ] 분류, 회귀, 군집의 예시를 각각 들 수 있습니다.
- [ ] 각 `.score()` 값 뒤에 있는 의미를 설명할 수 있습니다.
- [ ] KMeans의 `K`가 하이퍼파라미터라는 점을 알고 있습니다.
- [ ] 어떤 알고리즘이 표준화된 입력을 필요로 하는지 알고 있습니다.

## 연습 문제

1. KMeans로 `iris`를 군집화한 뒤 실제 `y`와 교차표를 만들어 보세요.
2. 회귀로 보는 편이 좋은 문제 세 개와 분류로 보는 편이 좋은 문제 세 개를 적어 보세요.
3. 준지도학습이 정답인 상황 하나를 설명해 보세요.

## 정리

패러다임 선택은 모델 성능의 상한선을 정합니다. 지도학습과 비지도학습의 차이를 정확히 잡아야 이후 데이터 준비, 평가, 해석이 모두 같은 방향으로 정렬됩니다.

이 글에서 기억할 핵심은 세 가지입니다. 첫째, 분류와 회귀는 둘 다 지도학습이지만 예측 대상이 다릅니다. 둘째, 군집화는 정답이 없는 구조 탐색 문제입니다. 셋째, 문제 프레이밍을 잘못 잡으면 모델 개선 자체가 무의미해집니다.

다음 글에서는 Train/Test Split을 통해 일반화를 어떻게 측정하는지 살펴보겠습니다.

## 실전 확장: 학습·평가 파이프라인을 한 번에 구성하기

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

## 분류 평가 지표를 함께 읽는 방법

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

## 교차검증과 모델 비교를 표준화하기

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

## 처음 질문으로 돌아가기

- **레이블이 있을 때와 없을 때 같은 알고리즘을 써도 될까요?**
  - 본문의 기준은 지도학습과 비지도학습를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **분류와 회귀는 둘 다 지도학습인데 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **군집화는 분류와 왜 전혀 다른 문제로 취급할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Machine Learning 101 (1/10): Machine Learning이란 무엇인가?](./01-what-is-machine-learning.md)
- **지도학습과 비지도학습 (현재 글)**
- Train/Test Split (예정)
- Linear Regression (예정)
- Logistic Regression (예정)
- Decision Tree와 Random Forest (예정)
- Clustering (예정)
- Overfitting과 Regularization (예정)
- Model Evaluation (예정)
- ML 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Supervised learning](https://scikit-learn.org/stable/supervised_learning.html)
- [scikit-learn — Unsupervised learning](https://scikit-learn.org/stable/unsupervised_learning.html)
- [Pattern Recognition and Machine Learning — Bishop](https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/)
- [Google — ML Problem Framing](https://developers.google.com/machine-learning/problem-framing)

Tags: MachineLearning, SupervisedLearning, UnsupervisedLearning, Classification, Clustering

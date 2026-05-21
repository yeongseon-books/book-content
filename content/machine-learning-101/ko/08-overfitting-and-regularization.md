---
series: machine-learning-101
episode: 8
title: "Machine Learning 101 (8/10): Overfitting과 Regularization"
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
  - Overfitting
  - Regularization
  - Ridge
  - Lasso
seo_description: 과적합과 과소적합의 신호, 편향-분산, Ridge·Lasso·ElasticNet의 차이를 함께 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (8/10): Overfitting과 Regularization

훈련 점수는 99%인데 테스트 점수는 60%라면 모델이 똑똑한 것인지, 아니면 데이터를 외운 것인지부터 의심해야 합니다. 머신러닝에서 성능 개선의 절반은 더 강한 모델을 찾는 일이 아니라, 모델이 어디서 잡음을 외우고 있는지 진단하는 일에 가깝습니다. 과적합과 과소적합을 구분하지 못하면 점수가 좋아 보여도 실제 일반화는 오히려 나빠질 수 있습니다.

이 글은 Machine Learning 101 시리즈의 여덟 번째 글입니다. 여기서는 과적합과 과소적합의 신호, 편향-분산 트레이드오프, Ridge·Lasso·ElasticNet 같은 정규화 기법이 일반화를 어떻게 되찾아 주는지 살펴보겠습니다.

## 먼저 던지는 질문

- 과적합과 과소적합은 어떤 신호로 구분할까요?
- 편향-분산 트레이드오프는 무엇을 뜻할까요?
- Ridge, Lasso, ElasticNet은 어떻게 다를까요?

## 큰 그림

![Machine Learning 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/08/08-01-diagram.ko.png)

*Machine Learning 101 8장 흐름 개요*

이 그림은 이 장의 핵심 개념들이 어떻게 연결되는지 보여줍니다.



## 왜 중요한가

모델 개선의 절반은 정규화라고 해도 과장이 아닙니다. 모델 용량이 클수록 정규화가 모델을 살려 줍니다.

## 한눈에 보는 개념

## 핵심 용어

- 과적합: 훈련 성능은 좋지만 테스트 성능은 약한 상태입니다.
- **과소적합**: 훈련과 테스트 모두 약한 상태입니다.
- **편향(Bias)**: 모델 가정에 내장된 오차입니다.
- **분산(Variance)**: 데이터 변화에 민감한 정도입니다.
- **L1 / L2**: 계수 크기에 패널티를 주는 방식입니다.

## Before/After

**Before**: "모델을 더 크게 만들자"고 해서 더 심하게 과적합합니다.

**After**: 먼저 학습 곡선으로 진단하고, 그다음 정규화를 적용합니다.

## 실습: 5단계로 정규화 비교하기

### Step 1 — 데이터

```python
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
X, y = fetch_california_housing(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
sc = StandardScaler().fit(Xtr); Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
```

### Step 2 — Linear

```python
from sklearn.linear_model import LinearRegression
lin = LinearRegression().fit(Xtr, ytr)
print("lin :", lin.score(Xte, yte))
```

### Step 3 — Ridge (L2)

```python
from sklearn.linear_model import Ridge
ridge = Ridge(alpha=1.0).fit(Xtr, ytr)
print("ridge:", ridge.score(Xte, yte))
```

### Step 4 — Lasso (L1)

```python
from sklearn.linear_model import Lasso
lasso = Lasso(alpha=0.01).fit(Xtr, ytr)
print("lasso:", lasso.score(Xte, yte), "nz:", (lasso.coef_ != 0).sum())
```

### Step 5 — Alpha sweep

```python
import numpy as np
for a in np.logspace(-3, 2, 6):
    s = Ridge(alpha=a).fit(Xtr, ytr).score(Xte, yte)
    print(f"alpha={a:.3g}  R^2={s:.3f}")
```

**예상 출력:** 선형 회귀, Ridge, Lasso 각각의 테스트 점수가 나오고, `alpha`를 바꾸면 성능 곡선이 움직입니다. 어느 값에서도 결과가 시원치 않다면 정규화 강도보다 **피처 품질**이나 **모델 계열**이 먼저 문제일 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- Lasso는 계수를 0으로 만들어 피처 선택 효과까지 냅니다.
- Ridge는 모든 계수를 부드럽게 줄입니다.
- `alpha`는 감으로 찍는 값이 아니라 교차검증으로 정해야 합니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 모델 용량이 커질수록 train-test 간격이 벌어지면, 구조 변경 전에 **정규화**와 **데이터 양**을 먼저 점검해야 합니다.
- Lasso가 실행할 때마다 다른 피처를 고르면, 상관 피처가 많은지 보고 ElasticNet이나 Ridge도 함께 비교해야 합니다.
- train과 test가 둘 다 낮으면 과적합이 아니라 **과소적합**이나 **피처 설계 부족**일 수 있습니다.

## 자주 하는 실수 5가지

1. **스케일링 없이 L1이나 L2를 적용합니다.**
2. **`alpha`를 한 번만 시도하고 끝냅니다.**
3. **훈련 점수만 보고 과적합을 판단합니다.**
4. **상관 피처가 많을 때 Lasso의 불안정성을 무시합니다.**
5. **ElasticNet의 존재를 잊습니다.**

## 실무에서는 이렇게 나타납니다

광고 CTR, 검색 랭킹, 유전체 데이터처럼 고차원 문제에서는 Lasso와 ElasticNet이 피처 선택 도구로도 자주 쓰입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 학습 곡선을 먼저 봅니다.
- 더 많은 데이터는 가장 강한 정규화일 때가 많습니다.
- 드롭아웃과 데이터 증강도 넓게 보면 정규화입니다.
- `RidgeCV`로 `alpha`를 자동 선택하는 편이 실용적입니다.
- 과소적합이라면 모델 용량을 늘려야 합니다.

## 체크리스트

- [ ] 훈련 점수와 테스트 점수를 함께 추적합니다.
- [ ] 학습 곡선을 그립니다.
- [ ] `alpha`를 교차검증으로 정합니다.
- [ ] Lasso가 선택한 피처를 확인합니다.

## 연습 문제

1. `PolynomialFeatures(degree=10)`와 Ridge를 써서 과적합을 재현해 보세요.
2. `RidgeCV`와 수동으로 고른 `alpha`를 비교해 보세요.
3. Lasso가 0으로 줄인 피처 목록을 적어 보세요.

## 정리

정규화는 일반화를 회복하는 핵심 레버입니다. 모델을 더 크게 만드는 것보다 먼저, 모델이 어디서 잡음을 외우는지 읽고 자유도를 조절하는 편이 훨씬 실용적입니다.

이 글에서 기억할 핵심은 네 가지입니다. 첫째, 과적합은 훈련과 테스트 점수 차이에서 드러납니다. 둘째, 편향과 분산은 항상 함께 움직입니다. 셋째, Ridge는 부드럽게 줄이고 Lasso는 일부를 0으로 만듭니다. 넷째, `alpha`는 반드시 검증으로 골라야 합니다.

다음 글에서는 이런 모델을 올바른 지표로 비교하는 Model Evaluation을 다루겠습니다.

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

- **과적합과 과소적합은 어떤 신호로 구분할까요?**
  - 본문의 기준은 Overfitting과 Regularization를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **편향-분산 트레이드오프는 무엇을 뜻할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Ridge, Lasso, ElasticNet은 어떻게 다를까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Machine Learning 101 (1/10): Machine Learning이란 무엇인가?](./01-what-is-machine-learning.md)
- [Machine Learning 101 (2/10): 지도학습과 비지도학습](./02-supervised-and-unsupervised.md)
- [Machine Learning 101 (3/10): Train/Test Split](./03-train-test-split.md)
- [Machine Learning 101 (4/10): Linear Regression](./04-linear-regression.md)
- [Machine Learning 101 (5/10): Logistic Regression](./05-logistic-regression.md)
- [Machine Learning 101 (6/10): Decision Tree와 Random Forest](./06-decision-tree-and-random-forest.md)
- [Machine Learning 101 (7/10): Clustering](./07-clustering.md)
- **Overfitting과 Regularization (현재 글)**
- Model Evaluation (예정)
- ML 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Linear models (Ridge, Lasso)](https://scikit-learn.org/stable/modules/linear_model.html)
- [scikit-learn — Validation curves](https://scikit-learn.org/stable/modules/learning_curve.html)
- [Bias-Variance — Stanford CS229 notes](https://cs229.stanford.edu/notes2022fall/)
- [StatQuest — Regularization](https://www.youtube.com/watch?v=Q81RR3yKn30)

Tags: MachineLearning, Overfitting, Regularization, Ridge, Lasso

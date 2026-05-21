---
series: machine-learning-101
episode: 6
title: "Machine Learning 101 (6/10): Decision Tree와 Random Forest"
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
  - DecisionTree
  - RandomForest
  - Ensemble
  - scikit-learn
seo_description: 결정 트리가 피처 공간을 나누는 방식과 랜덤 포레스트가 분산을 줄이는 원리를 함께 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (6/10): Decision Tree와 Random Forest

거대한 `if-else` 규칙 묶음이 때로는 신경망보다 표 데이터에서 더 잘 동작한다는 사실이 처음에는 이상하게 느껴질 수 있습니다. 하지만 고객 정보, 거래 로그, 클릭 기록처럼 열과 행으로 정리된 데이터에서는 트리 계열이 여전히 매우 강한 베이스라인입니다. 이유는 단순합니다. 비선형 관계를 자연스럽게 잡고, 전처리 요구도 비교적 적기 때문입니다.

이 글은 Machine Learning 101 시리즈의 여섯 번째 글입니다. 여기서는 결정 트리의 분할 기준, 단일 트리의 과적합 문제, 그리고 랜덤 포레스트가 여러 트리를 묶어 어떻게 더 안정적인 앙상블이 되는지 정리하겠습니다.

## 먼저 던지는 질문

- 결정 트리는 피처 공간을 어떤 기준으로 나눌까요?
- Gini와 entropy는 무엇을 측정할까요?
- 단일 트리는 왜 쉽게 과적합될까요?

## 큰 그림

![Machine Learning 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/06/06-01-diagram.ko.png)

*Machine Learning 101 6장 흐름 개요*

이 그림은 이 장의 핵심 개념들이 어떻게 연결되는지 보여줍니다.



## 왜 중요한가

랜덤 포레스트와 그래디언트 부스팅 트리는 지금도 표 데이터에서 강력한 기본 선택지입니다. 딥러닝으로 가기 전에 반드시 비교해야 할 베이스라인입니다.

## 한눈에 보는 개념

## 핵심 용어

- **분할(Split)**: 하나의 피처와 임계값으로 데이터를 나눕니다.
- **Gini / entropy**: 불순도를 재는 기준입니다.
- **Pruning**: 깊이나 리프 크기를 제한합니다.
- **Bagging**: 부트스트랩 샘플을 평균내는 방식입니다.
- **Feature importance**: 각 피처가 분할에 기여한 정도입니다.

## Before/After

**Before**: "트리는 해석 가능하다"에서 설명이 끝납니다. 단일 트리는 분산이 매우 큽니다.

**After**: 포레스트로 분산을 줄이고, 설명은 SHAP 같은 도구까지 포함해 생각합니다.

## 실습: 5단계로 보는 트리와 포레스트

### Step 1 — 데이터

```python
from sklearn.datasets import load_breast_cancer
X, y = load_breast_cancer(return_X_y=True)
```

### Step 2 — 분할

```python
from sklearn.model_selection import train_test_split
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
```

### Step 3 — 단일 트리

```python
from sklearn.tree import DecisionTreeClassifier
tree = DecisionTreeClassifier(max_depth=4, random_state=0).fit(Xtr, ytr)
print("tree:", tree.score(Xte, yte))
```

### Step 4 — Random Forest

```python
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=200, random_state=0).fit(Xtr, ytr)
print("rf  :", rf.score(Xte, yte))
```

### Step 5 — 피처 중요도

```python
import numpy as np
order = np.argsort(rf.feature_importances_)[::-1][:5]
print("top:", order)
```

**예상 출력:** 단일 트리와 랜덤 포레스트의 테스트 정확도가 출력되고, 포레스트 쪽이 대체로 더 안정적인 편입니다. 중요도 목록은 어디를 더 볼지 알려 주는 **순위 힌트**이지, 인과관계를 증명하는 표는 아닙니다.

## 이 코드에서 먼저 봐야 할 점

- `max_depth`는 과적합을 막는 가장 중요한 손잡이입니다.
- `n_estimators`가 많을수록 더 안정적이지만, 증가 효과는 점점 줄어듭니다.
- `feature_importances_`는 상관된 피처들 사이에 기여도를 나눠 가집니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 훈련 점수는 완벽한데 테스트 점수가 떨어지면, 더 복잡한 모델보다 먼저 **깊이 제한**을 걸어야 합니다.
- 중요도 결과가 도메인 상식과 어긋나면 상관 피처와 **permutation importance**를 같이 봐야 합니다.
- 포레스트가 겨우 조금만 더 좋다면, 마지막 몇 점보다 **해석 가능성**이 더 중요한지 함께 판단해야 합니다.

## 자주 하는 실수 5가지

1. **깊이 제한 없이 하나의 깊은 트리만 사용합니다.**
2. **feature importance를 인과 해석으로 읽습니다.**
3. **트리에는 필요하지 않은 표준화를 습관적으로 합니다.**
4. **훈련 정확도 100%를 믿고 안심합니다.**
5. **그래디언트 부스팅 트리와의 비교를 건너뜁니다.**

## 실무에서는 이렇게 나타납니다

신용 점수, 클릭 예측, 추천 피처 모델처럼 표 데이터 중심의 ML 시스템은 지금도 트리 앙상블 위에서 돌아갑니다. 여전히 **tabular ML의 주력 모델**입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 랜덤 포레스트는 **베이스라인 + 약간 더**입니다.
- 보통은 그래디언트 부스팅이 더 강합니다.
- permutation importance가 더 믿을 만한 경우가 많습니다.
- 인스턴스 수준 해석이 필요하면 SHAP를 더합니다.
- 범주형 피처 처리는 모델 특성에 맞춰 따로 봅니다.

## 체크리스트

- [ ] `max_depth`를 명시적으로 설정합니다.
- [ ] 포레스트에 충분한 개수의 트리를 사용합니다.
- [ ] feature importance의 한계를 알고 있습니다.
- [ ] GBDT 모델과 비교합니다.

## 연습 문제

1. `max_depth`를 1부터 20까지 바꿔 가며 테스트 점수를 그려 보세요.
2. 랜덤 포레스트와 그래디언트 부스팅을 비교해 보세요.
3. 기본 importance와 permutation importance를 비교해 보세요.

## 정리

트리와 포레스트는 표 데이터 ML의 주력 도구입니다. 단일 트리는 해석이 쉽지만 흔들리기 쉽고, 랜덤 포레스트는 여러 트리의 평균으로 그 흔들림을 줄입니다.

이 글에서 기억할 핵심은 네 가지입니다. 첫째, 결정 트리는 분할 기준으로 피처 공간을 잘라 나갑니다. 둘째, 깊은 단일 트리는 과적합되기 쉽습니다. 셋째, 랜덤 포레스트는 bagging으로 분산을 줄입니다. 넷째, feature importance는 유용하지만 인과 설명은 아닙니다.

다음 글에서는 비지도학습 대표 주제인 Clustering으로 넘어가겠습니다.

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

- **결정 트리는 피처 공간을 어떤 기준으로 나눌까요?**
  - 본문의 기준은 Decision Tree와 Random Forest를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Gini와 entropy는 무엇을 측정할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **단일 트리는 왜 쉽게 과적합될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Machine Learning 101 (1/10): Machine Learning이란 무엇인가?](./01-what-is-machine-learning.md)
- [Machine Learning 101 (2/10): 지도학습과 비지도학습](./02-supervised-and-unsupervised.md)
- [Machine Learning 101 (3/10): Train/Test Split](./03-train-test-split.md)
- [Machine Learning 101 (4/10): Linear Regression](./04-linear-regression.md)
- [Machine Learning 101 (5/10): Logistic Regression](./05-logistic-regression.md)
- **Decision Tree와 Random Forest (현재 글)**
- Clustering (예정)
- Overfitting과 Regularization (예정)
- Model Evaluation (예정)
- ML 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Decision Trees](https://scikit-learn.org/stable/modules/tree.html)
- [scikit-learn — Ensemble methods](https://scikit-learn.org/stable/modules/ensemble.html)
- [Random Forests — Breiman (2001)](https://link.springer.com/article/10.1023/A:1010933404324)
- [StatQuest — Random Forests](https://www.youtube.com/watch?v=J4Wdy0Wc_xQ)

Tags: MachineLearning, DecisionTree, RandomForest, Ensemble, scikit-learn

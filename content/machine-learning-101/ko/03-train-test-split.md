---
series: machine-learning-101
episode: 3
title: "Machine Learning 101 (3/10): Train/Test Split"
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
  - TrainTestSplit
  - Generalization
  - CrossValidation
  - scikit-learn
seo_description: 일반화를 측정하기 위한 train/test split의 의미와 누수, stratify, random_state, 교차검증까지 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (3/10): Train/Test Split

훈련 정확도가 99%라고 해서 실제 서비스에서도 잘 동작한다는 뜻은 아닙니다. 머신러닝 입문에서 가장 자주 생기는 착각도 바로 여기서 나옵니다. 같은 데이터로 학습하고 같은 데이터로 점수를 재면 숫자는 좋아 보이지만, 그 숫자로는 배포 후 성능을 설명할 수 없습니다.

이 글은 Machine Learning 101 시리즈의 세 번째 글입니다. 여기서는 train/test split이 왜 일반화 측정의 최소 장치인지, 그리고 `random_state`, `stratify`, K-fold 교차검증이 각각 어떤 역할을 하는지 정리해 보겠습니다.

## 먼저 던지는 질문

- 훈련 세트, 검증 세트, 테스트 세트는 각각 무엇을 맡을까요?
- `random_state`를 왜 항상 고정하라고 할까요?
- `stratify`는 클래스 불균형에서 어떤 도움을 줄까요?

## 큰 그림

![Machine Learning 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/03/03-01-diagram.ko.png)

*Machine Learning 101 3장 흐름 개요*

이 그림은 이 장의 핵심 개념들이 어떻게 연결되는지 보여줍니다.

## 분할 전략 비교

| 전략 | 장점 | 단점 | 적합 상황 |
|---|---|---|---|
| 홀드아웃(Hold-out) | 빠름 | 한 번의 분할에 의존 | 데이터가 충분히 많을 때 |
| K-fold | 모든 데이터 활용 | 시간이 더 걸림 | 표본 수가 적을 때 |
| Stratified | 클래스 비율 유지 | 설정이 하나 더 | 불균형 데이터 |
| 시계열 분할 | 누수 방지 | 훈련 데이터 감소 | 시간 순서가 중요한 문제 |

분할 전략의 선택은 데이터의 특성과 문제 유형에 따라 결정됩니다. 무작위 분할이 항상 정답은 아닙니다.


## 왜 중요한가

일반화를 측정하지 못하면 모델을 고를 수도, 비교할 수도 없습니다. 훈련 점수는 보기에는 좋지만 그대로 배포할 수 있는 숫자가 아닙니다. 어떤 분할 전략을 썼는지가 결국 모델 선택과 MLOps 게이트의 기준을 결정합니다.

## 한눈에 보는 개념

## 핵심 용어

- **Train**: 모델을 학습시키는 데이터입니다.
- **Validation**: 하이퍼파라미터를 조정하는 데 쓰는 데이터입니다.
- **Test**: 마지막에 한 번만 보는 홀드아웃 데이터입니다.
- **Stratify**: 분할 뒤에도 클래스 비율이 유지되도록 맞춥니다.
- **K-fold**: 데이터를 K개로 나누고 테스트 폴드를 돌아가며 바꿔 가는 방식입니다.

## Before/After

**Before**: 전체 데이터에 학습하고 같은 데이터로 점수를 재서 성능을 과대평가합니다.

**After**: train으로 학습하고 홀드아웃 test로 평가해, 숫자가 현실에 더 가깝도록 만듭니다.

## 실습: 5단계로 분할하고 평가하기

### Step 1 — 데이터

```python
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
```

### Step 2 — 분할

```python
from sklearn.model_selection import train_test_split
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

### Step 3 — 모델

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
```

### Step 4 — 평가

```python
print("train:", model.score(Xtr, ytr))
print("test :", model.score(Xte, yte))
```

### Step 5 — 교차검증

```python
from sklearn.model_selection import cross_val_score
print(cross_val_score(model, X, y, cv=5).mean())
```

**예상 출력:** 훈련 점수는 테스트 점수보다 약간 높게 나오고, 교차검증 평균은 그 주변 값에 모이는 편이 자연스럽습니다. 세 숫자가 크게 벌어지면 모델보다 먼저 **분할 전략**을 의심해야 합니다.

## 데이터 누수(Data Leakage)

데이터 누수는 훈련 데이터에 테스트 데이터의 정보가 섮여 들어가는 현상으로, 가장 위험한 오류 중 하나입니다.

### 누수가 발생하는 주요 경우

1. **전처리 누수**: 분할 전에 전체 데이터로 스케일러를 학습합니다.
2. **타겟 누수**: 피처 안에 타겟 정보가 직접 들어갑니다.
3. **시간 누수**: 미래 정보를 과거 예측에 사용합니다.
4. **그룹 누수**: 같은 사용자/그룹이 train/test에 나뉘어 들어갑니다.

### 예방 방법

- 분할을 가장 먼저 수행합니다.
- 전처리는 훈련 데이터로만 `.fit()`하고 테스트 데이터는 `.transform()`만 합니다.
- 피처 선택 단계에서 타겟 정보가 섮인 컴럼을 제거합니다.
- 시계열 문제에서는 시간 순서를 엄격히 지킵니다.

## Python 예제: train_test_split + cross_val_score

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression

X, y = load_iris(return_X_y=True)

# 홀드아웃 분할
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
print("Train:", model.score(Xtr, ytr))
print("Test:", model.score(Xte, yte))

# 교차검증
scores = cross_val_score(model, X, y, cv=5)
print("CV mean:", scores.mean(), "std:", scores.std())
```

교차검증은 한 번의 분할에서 생길 수 있는 우연을 줄여 줍니다. 표본 수가 적을 때 특히 유용합니다.
## 이 코드에서 먼저 봐야 할 점

- `stratify=y`는 두 분할 모두에서 클래스 비율을 유지합니다.
- 고정된 `random_state`는 결과를 재현 가능하게 만듭니다.
- `cross_val_score`는 훈련과 평가를 K번 반복합니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 테스트 점수가 실행할 때마다 크게 흔들리면 표본 수가 너무 작거나 시드가 떠 있는지 먼저 봐야 합니다.
- train과 test가 모두 지나치게 좋다면, 성능보다 먼저 **전처리 누수**를 점검해야 합니다.
- 시계열이나 사용자 그룹 데이터인데 무작위 분할을 썼다면, 지표가 아니라 **분할 방식 자체가 버그**일 수 있습니다.

## 자주 하는 실수 5가지

1. **테스트 세트로 튜닝해서 성능 누수를 만듭니다.**
2. **분할 전에 전체 데이터에 스케일러를 먼저 학습합니다.**
3. **랜덤 시드를 고정하지 않고 노이즈를 쫓습니다.**
4. **불균형 데이터에서 `stratify`를 무시합니다.**
5. **시계열 데이터를 시간 순서가 아니라 무작위로 나눕니다.**

## 실무에서는 이렇게 나타납니다

A/B 실험, 모델 비교, MLOps 게이팅 모두 올바른 분할 전략에 기대고 있습니다. 결국 의사결정을 지배하는 것은 지표 이름만이 아니라 **어떻게 나눴는가**입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 테스트 세트는 **정말 한 번만** 봅니다.
- 검증 세트와 테스트 세트는 분리합니다.
- 시계열 데이터는 시간 순서대로 나눕니다.
- 항상 그룹 누수 가능성을 의심합니다.
- 전처리는 분할 이후에 합니다.

## 체크리스트

- [ ] train, valid, test의 역할을 설명할 수 있습니다.
- [ ] `stratify`가 하는 일을 이해했습니다.
- [ ] `random_state`를 항상 고정합니다.
- [ ] `cross_val_score`를 실행할 수 있습니다.

## 연습 문제

1. `test_size`를 0.1부터 0.3까지 바꿔 가며 테스트 점수를 관찰해 보세요.
2. `stratify=None`일 때 train과 test의 클래스 비율을 비교해 보세요.
3. 5-fold와 10-fold 점수의 분산을 비교해 보세요.

## 정리

올바른 분할은 그 뒤에 오는 모든 측정의 전제입니다. train/test split을 정확히 이해해야만 과대평가된 훈련 점수와 실제 일반화 성능을 구분할 수 있습니다.

이 글에서 기억할 핵심은 네 가지입니다. 첫째, test 세트는 마지막에 한 번만 봐야 합니다. 둘째, `stratify`는 클래스 비율을 지켜 줍니다. 셋째, `random_state`는 재현성을 위해 필수입니다. 넷째, 교차검증은 한 번의 분할에서 생길 수 있는 우연을 줄여 줍니다.

다음 글에서는 지도학습의 가장 기본적인 모델인 Linear Regression을 살펴보겠습니다.

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

- **훈련 세트, 검증 세트, 테스트 세트는 각각 무엇을 맡을까요?**
  - 본문의 기준은 Train/Test Split를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`random_state`를 왜 항상 고정하라고 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`stratify`는 클래스 불균형에서 어떤 도움을 줄까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Machine Learning 101 (1/10): Machine Learning이란 무엇인가?](./01-what-is-machine-learning.md)
- [Machine Learning 101 (2/10): 지도학습과 비지도학습](./02-supervised-and-unsupervised.md)
- **Train/Test Split (현재 글)**
- Linear Regression (예정)
- Logistic Regression (예정)
- Decision Tree와 Random Forest (예정)
- Clustering (예정)
- Overfitting과 Regularization (예정)
- Model Evaluation (예정)
- ML 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — train_test_split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
- [scikit-learn — Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Forecasting: Principles and Practice — Hyndman](https://otexts.com/fpp3/)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)

Tags: MachineLearning, TrainTestSplit, Generalization, CrossValidation, scikit-learn

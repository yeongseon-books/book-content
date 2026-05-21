---
series: machine-learning-101
episode: 1
title: "Machine Learning 101 (1/10): Machine Learning이란 무엇인가?"
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
  - AI
  - DataScience
  - Foundations
  - Beginner
seo_description: 머신러닝의 정의와 학습·일반화·예측의 직관, 그리고 통계·규칙 기반 코드와의 차이를 코드와 함께 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (1/10): Machine Learning이란 무엇인가?

추천, 의료, 금융, 자율주행처럼 머신러닝이 등장하지 않는 산업을 찾기 어려워졌습니다. 그런데 입문 단계에서는 오히려 가장 기본적인 질문이 흐려지기 쉽습니다. 머신러닝은 통계의 다른 이름인지, 규칙 기반 프로그래밍의 확장인지, 아니면 전혀 다른 문제 해결 방식인지부터 분명히 잡아야 이후 모델 선택도 흔들리지 않습니다.

이 글은 머신러닝 101 시리즈의 1번째 글입니다. 여기서는 머신러닝을 **데이터에서 함수를 학습해 새로운 입력에 대해 예측하는 방식**이라는 관점으로 정리하고, 학습·일반화·예측이 각각 무엇을 뜻하는지 출발점부터 잡아 보겠습니다.

## 먼저 던지는 질문

- 머신러닝은 정확히 무엇을 학습한다고 봐야 할까요?
- 일반화는 왜 훈련 성능과 다른 개념일까요?
- 통계, 규칙 기반 코드, 머신러닝은 어디서 갈릴까요?

## 큰 그림

![Machine Learning 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/01/01-01-diagram.ko.png)

*Machine Learning 101 1장 흐름 개요*

이 그림에서는 데이터가 모델로 학습되어 예측이 되는 흐름을 봅니다. 머신러닝의 출발점은 사람이 모든 규칙을 정하는 것이 아니라, 데이터에서 함수를 추정한다는 기본 가정을 이해하는 데 있습니다.

> 머신러닝은 **학습·일반화·예측**이라는 세 가지 단계로 나뉩니다. 이 구조를 이해하면 이후 모든 모델을 다루는 방식이 달라집니다.

## ML 유형 비교

| 유형 | 입력 | 출력 | 대표 예시 |
|---|---|---|---|
| 지도학습 | X, y (레이블 있음) | 분류/회귀 예측 | 스팸 필터, 가격 예측 |
| 비지도학습 | X (레이블 없음) | 구조 발견 | 고객 세그먼트, 이상 탐지 |
| 강화학습 | 상태, 보상 | 행동 정책 | 게임 AI, 로봇 제어 |

입문 단계에서는 지도학습과 비지도학습의 경계가 가장 먼저 보이기 시작합니다. 강화학습은 보상 신호를 어떻게 설계할지부터 문제가 크게 바뀌기 때문에 처음부터 함께 다루지는 않습니다.
## 왜 중요한가

추천 시스템, 의료 진단 보조, 금융 리스크 분석, 자율주행처럼 거의 모든 산업이 머신러닝의 영향을 받고 있습니다. 하지만 기초 개념이 약하면 뒤에서 어떤 모델을 올려도 해석이 무너집니다. 훈련 데이터에서 점수가 잘 나왔다고 곧바로 성공이라고 착각하거나, 문제 정의보다 알고리즘 이름에 먼저 끌리는 순간부터 프로젝트는 불안해집니다.

## 한눈에 보는 개념

## 핵심 용어

- **학습(Learning)**: 데이터에서 함수를 추정하는 과정입니다.
- **일반화(Generalization)**: 훈련 때 보지 못한 데이터에도 잘 동작하는 성질입니다.
- **예측(Prediction)**: 학습된 함수를 새로운 입력에 적용하는 일입니다.
- **피처(Feature)**: 모델에 들어가는 입력 변수입니다.
- **레이블(Label)**: 예측하려는 정답 또는 목표값입니다.

## Before/After

**Before**: "`if-else`로 모든 규칙을 직접 코딩한다"는 방식이라서 새로운 패턴이 생길 때마다 코드를 더 붙여야 합니다.

**After**: "데이터를 주면 모델이 규칙을 학습한다"는 방식이라서 코드보다 데이터가 확장의 중심이 됩니다.

## 실습: 5단계로 보는 첫 번째 ML

### Step 1 — 데이터

```python
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
print(X.shape, y.shape)
```

### Step 2 — 모델 선택

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000)
```

### Step 3 — 학습

```python
model.fit(X, y)
```

### Step 4 — 예측

```python
print(model.predict(X[:5]))
```

### Step 5 — 점수 확인

```python
print("acc:", model.score(X, y))
```

**예상 출력:** `X.shape`, `y.shape`는 `(150, 4)`, `(150,)`처럼 작은 표 데이터를 보여 주고, `predict`는 클래스 ID 배열을 출력합니다. 마지막 정확도는 대체로 높게 나오지만, 여기서는 **훈련 데이터 점수**라는 점을 먼저 기억해야 합니다.

## ML이 적합한 문제 vs 부적합한 문제

**적합한 경우:**

- 규칙을 명시하기 어렵지만 데이터는 충분합니다.
- 패턴이 복잡하거나 계속 변합니다.
- 확률적 예측이 유용합니다.

**부적합한 경우:**

- 규칙이 명확하고 안정적입니다.
- 데이터가 거의 없거나 레이블링 비용이 너무 높습니다.
- 결정 과정이 완전히 투명해야 합니다.

머신러닝은 만능 도구가 아닙니다. 문제 정의가 먼저고, 그 뒤에야 알고리즘 선택입니다.

## Python 예제: 3줄로 보는 분류

```python
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
X, y = load_iris(return_X_y=True)
model = LogisticRegression(max_iter=1000).fit(X, y)
print("Accuracy:", model.score(X, y))  # 예: 0.97
```

이 코드는 3줄이지만, 학습·일반화·예측의 전체 파이프라인을 보여 줍니다. 다만 여기서 나온 점수는 **훈련 정확도**이므로 과대평가되었을 가능성이 높습니다.

## 이 코드에서 먼저 봐야 할 점

- `fit / predict / score`는 **scikit-learn의 표준 인터페이스**입니다.
- 여기서 `score`는 **훈련 정확도**일 뿐이며, 일반화 성능을 바로 뜻하지는 않습니다.
- 어떤 모델을 고를지는 **문제 유형**에 따라 달라집니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 훈련 정확도는 높은데 새 데이터에서 바로 무너지면, 모델보다 먼저 **입력 분포 변화**나 **타깃 정의의 모호함**을 의심해야 합니다.
- 팀이 `X`와 `y`가 무엇인지 한 문장으로 설명하지 못하면, 아직 모델 비교 단계가 아니라 **문제 정의 단계**에 머물러 있는 것입니다.
- 노트북에서 늘 같은 샘플 행만 확인하며 잘 된다고 느낀다면, 알고리즘보다 먼저 **누수**와 **암기** 가능성을 살펴봐야 합니다.

## 자주 하는 실수 5가지

1. **훈련 데이터 점수만 보고 성공을 판단합니다.**
2. **피처 스케일링을 무시합니다.**
3. **피처 안에 타깃 누수(target leakage)가 섞인 것을 놓칩니다.**
4. **랜덤 시드를 고정하지 않아 재현 가능한 결과를 남기지 못합니다.**
5. **결측치나 이상치를 처리하지 않은 채 학습을 시작합니다.**

## 실무에서는 이렇게 나타납니다

추천, 사기 탐지, 수요 예측, 이미지 인식, NLP 챗봇까지, **데이터 → 학습 → 예측** 파이프라인은 거의 모든 ML 제품의 뼈대입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **문제 정의**가 **모델 선택**보다 먼저입니다.
- **데이터 품질**이 **알고리즘 이름**보다 더 중요할 때가 많습니다.
- 일반화는 항상 **분리된 데이터**에서 확인해야 합니다.
- 복잡한 모델보다 먼저 **베이스라인 모델**을 세웁니다.
- 복잡도는 처음이 아니라 **마지막 카드**로 아껴 둡니다.

## 체크리스트

- [ ] `X, y`가 무엇을 뜻하는지 설명할 수 있습니다.
- [ ] `fit / predict / score`를 호출할 수 있습니다.
- [ ] 훈련 정확도와 일반화 성능이 다르다는 점을 이해했습니다.
- [ ] 베이스라인 모델의 가치를 알고 있습니다.

## 연습 문제

1. `iris`가 아닌 **자신의 데이터셋**으로 `fit / predict`를 실행해 보세요.
2. `score`가 왜 **과도하게 낙관적**일 수 있는지 설명해 보세요.
3. 피처 스케일링이 결과를 바꾸는 예시를 하나 만들어 보세요.

## 정리

머신러닝은 **데이터에서 학습한 함수를 새로운 입력에 적용하는 방식**입니다. 이 한 문장을 정확히 잡아 두면 이후 분류, 회귀, 군집, 평가 지표를 만날 때도 길을 잃지 않습니다.

이 글에서 가져가야 할 핵심은 네 가지입니다. 첫째, 학습은 데이터를 외우는 일이 아니라 함수를 추정하는 일입니다. 둘째, 일반화는 훈련 점수와 별개로 측정해야 합니다. 셋째, `fit / predict / score`는 scikit-learn의 공통 언어입니다. 넷째, 좋은 출발은 복잡한 모델이 아니라 명확한 문제 정의와 베이스라인입니다.

다음 글에서는 지도학습과 비지도학습을 비교하면서, 레이블이 있을 때와 없을 때 어떤 식으로 문제를 나눠 생각해야 하는지 살펴보겠습니다.

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

### 1번째 글 기준 실전 체크

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

## 처음 질문으로 돌아가기

- **머신러닝은 정확히 무엇을 학습한다고 봐야 할까요?**
  - 본문의 기준은 Machine Learning이란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **일반화는 왜 훈련 성능과 다른 개념일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **통계, 규칙 기반 코드, 머신러닝은 어디서 갈릴까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **Machine Learning이란 무엇인가? (현재 글)**
- 지도학습과 비지도학습 (예정)
- 훈련/테스트 분할 (예정)
- 선형 회귀 (예정)
- 로지스틱 회귀 (예정)
- 결정 트리와 랜덤 포레스트 (예정)
- 군집화 (예정)
- 과적합과 정규화 (예정)
- 모델 평가 (예정)
- ML 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Getting Started](https://scikit-learn.org/stable/getting_started.html)
- [Andrew Ng — Machine Learning Specialization](https://www.coursera.org/specializations/machine-learning-introduction)
- [Hands-On Machine Learning — Aurélien Géron](https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/)
- [Google — Machine Learning Crash Course](https://developers.google.com/machine-learning/crash-course)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/machine-learning-101/ko)

Tags: MachineLearning, AI, DataScience, Foundations, Beginner

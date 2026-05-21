---
series: machine-learning-101
episode: 4
title: "Machine Learning 101 (4/10): Linear Regression"
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
  - LinearRegression
  - Regression
  - scikit-learn
  - Beginner
seo_description: 선형 회귀의 직관, 평균제곱오차와 R-squared, 잔차 해석까지 scikit-learn 예제로 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (4/10): Linear Regression

차트 위에 점이 대체로 직선처럼 보인다고 해서 바로 설명이 끝나는 것은 아닙니다. 직선 하나로 변동의 큰 부분을 설명할 수 있다면 그것만으로도 매우 강한 모델이 될 수 있지만, 반대로 그 직선이 무엇을 설명하지 못하는지도 함께 봐야 합니다. 선형 회귀는 단순한 만큼 속도가 빠르고, 그만큼 베이스라인으로도 강력합니다.

이 글은 머신러닝 101 시리즈의 4번째 글입니다. 여기서는 선형 회귀의 식과 직관, 평균제곱오차, R-squared, 잔차 해석을 함께 보면서 왜 이 모델이 여전히 가장 먼저 돌려 봐야 하는 기준선인지 정리하겠습니다.

![Machine Learning 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/04/04-01-diagram.ko.png)
*Machine Learning 101 4장 흐름 개요*

## 먼저 던지는 질문

- 선형 회귀 식은 어떤 방식으로 예측값을 만들까요?
- 평균제곱오차와 최소제곱 해는 무엇을 최소화할까요?
- R-squared는 정확히 무엇을 설명할까요?

## 비용함수와 경사하강법

선형 회귀는 `y_hat = Xw + b`로 예측하지만, 어떻게 `w`와 `b`를 찾을까요? 답은 **비용함수**를 최소화하는 것입니다.

### 평균제곱오차(MSE)

$$
\text{MSE} = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2
$$

오차를 제곱하기 때문에 큰 오차에 무거운 페널티를 줍니다. 그래서 이상치에 민감합니다.

### 경사하강법

경사하강법은 비용함수를 줄이기 위해 기울기 반대 방향으로 파라미터를 조금씩 움직이는 방법입니다.

1. 초기 가중치를 랜덤하게 설정합니다.
2. 현재 위치에서 비용함수의 기울기를 계산합니다.
3. 기울기의 반대 방향으로 가중치를 조금 움직입니다.
4. 수렴할 때까지 반복합니다.

선형 회귀는 경사하강 없이 폐형해로도 풀 수 있지만, 경사하강법의 기초를 이해하면 다른 모델을 다룰 때도 도움이 됩니다.

## Python 예제: Numpy로 직접 구현

```python
import numpy as np

# 간단한 데이터
X = np.array([[1], [2], [3], [4]])
y = np.array([2, 4, 6, 8])

# 편향 항 추가 (bias trick)
X_b = np.c_[np.ones((X.shape[0], 1)), X]

# 최소제곱 폐형해
theta = np.linalg.inv(X_b.T @ X_b) @ X_b.T @ y
print("w, b:", theta)
```

이 코드는 10줄 이내로 선형 회귀의 핵심을 보여 줍니다. `sklearn`은 이 과정을 최적화하고 다양한 옵션을 제공합니다.

## 선형회귀 가정 검증

| 가정 | 의미 | 검증법 |
|---|---|---|
| 선형성 | X와 y가 선형 관계 | 잔차 vs 예측 플롯 |
| 독립성 | 피처 간 다중공선성 없음 | VIF(분산팔창지수) |
| 등분산성 | 잔차 분산 일정 | 잔차 절대값 플롯 |
| 정규성 | 잔차가 정규분포 | Q-Q 플롯 |

선형 회귀는 이 가정들이 만족될 때 가장 잘 동작합니다. 가정이 깨지면 계수의 해석이 흘들리거나 예측 성능이 떨어집니다.

## 왜 중요한가

선형 회귀는 해석이 쉽고 빠르며, 생각보다 강력합니다. 그래서 가장 먼저 돌려 보는 편이 좋습니다. 베이스라인이 없으면 더 복잡한 모델을 쓸 정당성도 약해집니다.

## 한눈에 보는 개념

## 핵심 용어

- **가중치 `w`**: 각 피처가 예측에 기여하는 정도입니다.
- **절편 `b`**: 기준 수준의 예측값입니다.
- **MSE**: 평균제곱오차입니다.
- **R-squared**: 모델이 설명한 분산의 비율입니다.
- **잔차(Residual)**: `y - y_hat`입니다.

## 적용 전과 후
**Before**: "그래프상 직선처럼 보인다"는 인상만 있고 수치 검증은 없습니다.

**After**: 모델, 지표, 잔차를 함께 보며 세 단계로 검증합니다.

## 실습: 5단계로 보는 회귀

### 단계 1 — 데이터

```python
from sklearn.datasets import fetch_california_housing
X, y = fetch_california_housing(return_X_y=True)
```

### 단계 2 — 분할

```python
from sklearn.model_selection import train_test_split
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
```

### 단계 3 — 학습

```python
from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(Xtr, ytr)
```

### 단계 4 — 평가

```python
from sklearn.metrics import mean_squared_error, r2_score
pred = model.predict(Xte)
print("MSE:", mean_squared_error(yte, pred))
print("R^2:", r2_score(yte, pred))
```

### 단계 5 — 계수 확인

```python
for name, coef in zip(range(Xtr.shape[1]), model.coef_):
    print(f"x{name}: {coef:.3f}")
```

**예상 출력:** MSE, `R^2`, 그리고 부호가 있는 계수 목록이 출력됩니다. 여기서 먼저 볼 것은 절대적인 점수보다 **계수 방향이 상식과 맞는지**, 그리고 잔차가 직선 모델로 설명되지 않는 패턴을 보이는지입니다.

## 이 코드에서 먼저 봐야 할 점

- `coef_`의 부호와 크기가 해석의 중심입니다.
- R-squared가 낮다면 비선형성이 숨어 있다는 신호일 수 있습니다.
- MSE는 오차를 제곱하기 때문에 이상치에 특히 민감합니다.

## 실패 신호를 먼저 이렇게 읽습니다

- `R^2`가 낮고 잔차에 곡선 패턴이 보이면, 선형 모델을 버리기 전에 **비선형 피처**가 빠졌는지 봐야 합니다.
- 계수가 실행마다 크게 흔들리면 **다중공선성**과 **스케일 차이**를 먼저 점검해야 합니다.
- 일부 샘플이 오차를 지배하면, 이상치를 치울지 남길지 자체가 모델링 결정이라는 점을 드러내야 합니다.

## 자주 하는 실수 5가지

1. **스케일 차이를 무시한 채 계수를 바로 비교합니다.**
2. **다중공선성 때문에 계수가 흔들리는 상황을 놓칩니다.**
3. **잔차 플롯을 생략합니다.**
4. **이상치가 직선을 끌고 가는 상황을 방치합니다.**
5. **훈련 범위를 벗어난 구간까지 외삽합니다.**

## 실무에서는 이렇게 나타납니다

가격 책정, 수요 모델링, A/B 효과 추정처럼 이해관계자가 블랙박스보다 **해석 가능한 레버**를 원하는 영역에서는 선형 회귀가 여전히 중심에 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 항상 **베이스라인**에서 출발합니다.
- 해석 가능성은 기술 옵션이 아니라 **비즈니스 도구**입니다.
- 잔차는 모델의 일기장과 같습니다.
- 계수를 비교하기 전에는 표준화를 합니다.
- 규제가 필요하면 Ridge나 Lasso를 더합니다.

## 체크리스트

- [ ] MSE와 R-squared를 함께 보고합니다.
- [ ] 잔차를 시각화합니다.
- [ ] 계수를 읽기 전에 피처를 스케일링합니다.
- [ ] 외삽 위험을 명시적으로 표시합니다.

## 연습 문제

1. `PolynomialFeatures(degree=2)`를 추가하고 R-squared 변화를 관찰해 보세요.
2. 예측값 대비 잔차를 그린 뒤 어떤 패턴이 보이는지 설명해 보세요.
3. `Ridge(alpha=1.0)`와 `LinearRegression`의 계수 크기를 비교해 보세요.

## 정리

선형 회귀는 모든 회귀 작업의 출발점입니다. 단순하지만 강력하고, 숫자로 검증할 수 있으며, 해석 가능한 기준선을 제공합니다.

이 글에서 기억할 핵심은 네 가지입니다. 첫째, 선형 회귀는 `y_hat = Xw + b` 구조로 예측합니다. 둘째, MSE와 R-squared는 서로 다른 각도에서 성능을 읽게 해 줍니다. 셋째, 잔차 분석이 빠지면 모델 가정 검증도 빠집니다. 넷째, 복잡한 모델을 쓰기 전에는 항상 선형 회귀 베이스라인을 먼저 확인해야 합니다.

다음 글에서는 분류의 기본 모델인 Logistic Regression으로 넘어가겠습니다.

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

### 4번째 글 기준 실전 체크

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

- **선형 회귀 식은 어떤 방식으로 예측값을 만들까요?**
  - 본문의 기준은 Linear Regression를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **평균제곱오차와 최소제곱 해는 무엇을 최소화할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **R-squared는 정확히 무엇을 설명할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Machine Learning 101 (1/10): Machine Learning이란 무엇인가?](./01-what-is-machine-learning.md)
- [Machine Learning 101 (2/10): 지도학습과 비지도학습](./02-supervised-and-unsupervised.md)
- [Machine Learning 101 (3/10): 훈련/테스트 분할](./03-train-test-split.md)
- **Linear Regression (현재 글)**
- 로지스틱 회귀 (예정)
- 결정 트리와 랜덤 포레스트 (예정)
- 군집화 (예정)
- 과적합과 정규화 (예정)
- 모델 평가 (예정)
- ML 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Linear models](https://scikit-learn.org/stable/modules/linear_model.html)
- [An Introduction to Statistical Learning — James et al.](https://www.statlearning.com/)
- [Seeing Theory — Regression](https://seeing-theory.brown.edu/regression-analysis/index.html)
- [StatQuest — Linear Regression](https://www.youtube.com/watch?v=nk2CQITm_eo)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/machine-learning-101/ko)

Tags: MachineLearning, LinearRegression, Regression, scikit-learn, Beginner

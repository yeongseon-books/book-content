---
series: machine-learning-101
episode: 10
title: "Machine Learning 101 (10/10): ML 프로젝트 전체 흐름"
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
  - MLWorkflow
  - Pipeline
  - MLOps
  - Beginner
seo_description: 문제 정의부터 데이터, 모델, 배포, 모니터링까지 ML 프로젝트 전체 워크플로를 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (10/10): ML 프로젝트 전체 흐름

노트북에서 정확도가 높게 나왔는데도 실제 사용자에게 닿지 못하는 ML 프로젝트는 아주 많습니다. 이유는 대개 모델 점수가 아니라 그 앞뒤에 있습니다. 문제 정의가 약하거나, 데이터가 재현되지 않거나, 전처리가 흩어져 있거나, 배포 후 모니터링이 비어 있으면 좋은 모델도 곧 멈춥니다. ML의 성공은 점수 하나보다 전체 루프를 완성하는 데 달려 있습니다.

이 글은 머신러닝 101 시리즈의 10번째 글입니다. 여기서는 문제 정의부터 데이터, 피처, 모델, 평가, 배포, 모니터링까지 이어지는 7단계 워크플로를 정리하고, `Pipeline`이 왜 유지보수성과 재현성의 중심인지 살펴보겠습니다.

## 먼저 던지는 질문

- 정확도가 높아도 왜 많은 ML 프로젝트는 배포에 실패할까요?
- 문제 정의, 데이터, 모델, 배포, 모니터링을 왜 하나의 루프로 봐야 할까요?
- `Pipeline`은 왜 전처리 누수를 막는 핵심 도구일까요?

## 큰 그림

![Machine Learning 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/10/10-01-diagram.ko.png)

*Machine Learning 101 10장 흐름 개요*

이 그림은 이 장의 핵심 개념들이 어떻게 연결되는지 보여줍니다.



## 왜 중요한가

노트북에서 0.95 점수를 얻어도 모델이 사용자에게 도달하지 못하면 그 값은 0과 다르지 않습니다. 전체 루프를 소유해야 실제 영향이 생깁니다.

## 한눈에 보는 개념

## 핵심 용어

- **Pipeline**: 전처리와 모델을 하나로 묶은 객체입니다.
- 재현성: 시드, 버전, 데이터 스냅샷이 고정된 상태입니다.
- **Model Card**: 모델 메타데이터를 정리한 공식 문서입니다.
- **Drift**: 입력 또는 타깃 분포의 변화입니다.
- **Shadow deploy**: 실제로는 행동하지 않고 예측만 기록하는 배포 방식입니다.

## Before/After

**Before**: "모델 학습하고 점수 찍었으니 끝"이라고 생각합니다.

**After**: 문제, 데이터, 모델, 평가, 배포, 모니터링이 순환하는 루프로 봅니다.

## 실습: 5단계 미니 워크플로

### Step 1 — 문제와 데이터

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
```

### Step 2 — Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=2000)),
])
```

### Step 3 — 학습과 평가

```python
pipe.fit(Xtr, ytr)
print("test:", pipe.score(Xte, yte))
```

### Step 4 — 저장(재현성)

```python
import joblib
joblib.dump(pipe, "model.joblib")
loaded = joblib.load("model.joblib")
print("loaded:", loaded.score(Xte, yte))
```

### Step 5 — 모니터링 시뮬레이션

```python
import numpy as np
fresh = Xte + np.random.normal(0, 0.1, Xte.shape)
print("drifted:", loaded.score(fresh, yte))
```

**예상 출력:** 저장한 파이프라인은 다시 불러와도 같은 테스트 점수를 내야 하고, 입력에 노이즈를 넣은 `fresh` 점수는 대체로 더 낮게 나옵니다. 이 차이는 모델 파일을 보관하는 것만으로는 충분하지 않고 **입력 분포 변화**까지 지켜봐야 한다는 사실을 보여 줍니다.

## 이 코드에서 먼저 봐야 할 점

- `Pipeline`은 전처리 누수를 근본에서 막아 줍니다.
- `joblib`는 재현 가능한 배포를 가능하게 합니다.
- 작은 입력 노이즈만으로도 점수가 떨어질 수 있어 drift를 바로 체감하게 합니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 배포 직후 성능이 떨어지면, 모델 가중치보다 먼저 **학습 때와 실제 전처리 경로가 같은지** 확인해야 합니다.
- 깨끗한 환경에서 결과를 재현하지 못하면, 노트북 데모가 좋아 보여도 **워크플로 자체가 아직 불완전**합니다.
- 모니터링이 지연 시간과 에러율만 본다면, 서비스는 살아 있어도 **모델 품질**은 이미 무너지고 있을 수 있습니다.

## 자주 하는 실수 5가지

1. **전처리를 노트북 셀 여러 곳에 흩어 놓습니다.**
2. **시드와 버전 고정을 건너뛰어 재현성을 잃습니다.**
3. **모니터링 없이 배포만 합니다.**
4. **모델 카드 없이 모델을 공유합니다.**
5. **현실을 반영하지 않는 낡은 데이터로만 평가합니다.**

## 실무에서는 이렇게 나타납니다

추천, 사기 탐지, 검색 팀은 노트북 하나보다 **전체 ML 루프를 얼마나 잘 자동화했는지**로 경쟁합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 문제 정의가 가치의 60%를 좌우합니다.
- `Pipeline`이 유지보수성을 결정합니다.
- 모니터링이 진짜 시작입니다.
- drift는 반드시 일어납니다.
- 모델 카드는 조직 자산이 됩니다.

## 체크리스트

- [ ] 모든 단계를 `Pipeline` 안에 묶습니다.
- [ ] `joblib`로 저장하고 다시 불러옵니다.
- [ ] 시드와 버전을 고정합니다.
- [ ] drift 모니터링 전략을 세웁니다.

## 연습 문제

1. 파이프라인에 `PCA`를 추가하고 점수를 비교해 보세요.
2. 저장한 모델을 별도 스크립트에서 불러와 다시 평가해 보세요.
3. 입력 노이즈가 커질수록 점수가 어떻게 변하는지 곡선을 그려 보세요.

## 정리

축하합니다. Machine Learning 101 시리즈를 마쳤습니다. 하지만 실제 ML 프로젝트의 끝은 모델 학습이 아니라, 문제 정의부터 모니터링까지 이어지는 루프를 안정적으로 운영하는 데 있습니다.

이 글에서 기억할 핵심은 네 가지입니다. 첫째, 높은 점수만으로는 아무것도 배포되지 않습니다. 둘째, `Pipeline`은 전처리와 모델을 한 몸으로 묶어 누수를 막습니다. 셋째, 재현성은 운영 문제를 되짚는 기준선입니다. 넷째, 배포 후 모니터링이야말로 실제 ML 운영의 출발점입니다.

다음 단계로는 Model Evaluation 101이나 MLOps 101처럼 더 깊은 시리즈로 이어가면 좋습니다.

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

### 10번째 글 기준 실전 체크

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

## 처음 질문으로 돌아가기

- **정확도가 높아도 왜 많은 ML 프로젝트는 배포에 실패할까요?**
  - 본문의 기준은 ML 프로젝트 전체 흐름를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **문제 정의, 데이터, 모델, 배포, 모니터링을 왜 하나의 루프로 봐야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`Pipeline`은 왜 전처리 누수를 막는 핵심 도구일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Machine Learning 101 (1/10): Machine Learning이란 무엇인가?](./01-what-is-machine-learning.md)
- [Machine Learning 101 (2/10): 지도학습과 비지도학습](./02-supervised-and-unsupervised.md)
- [Machine Learning 101 (3/10): 훈련/테스트 분할](./03-train-test-split.md)
- [Machine Learning 101 (4/10): 선형 회귀](./04-linear-regression.md)
- [Machine Learning 101 (5/10): 로지스틱 회귀](./05-logistic-regression.md)
- [Machine Learning 101 (6/10): 결정 트리와 랜덤 포레스트](./06-decision-tree-and-random-forest.md)
- [Machine Learning 101 (7/10): 군집화](./07-clustering.md)
- [Machine Learning 101 (8/10): 과적합과 정규화](./08-overfitting-and-regularization.md)
- [Machine Learning 101 (9/10): 모델 평가](./09-model-evaluation.md)
- **ML 프로젝트 전체 흐름 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Pipelines](https://scikit-learn.org/stable/modules/compose.html)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Model Cards — Mitchell et al. (2019)](https://arxiv.org/abs/1810.03993)
- [Hidden Technical Debt in ML — Sculley et al.](https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/machine-learning-101/ko)

Tags: MachineLearning, MLWorkflow, Pipeline, MLOps, Beginner

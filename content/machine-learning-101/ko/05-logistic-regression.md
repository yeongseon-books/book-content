---
series: machine-learning-101
episode: 5
title: "Machine Learning 101 (5/10): Logistic Regression"
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
  - LogisticRegression
  - Classification
  - scikit-learn
  - Beginner
seo_description: 로지스틱 회귀가 선형 점수를 확률로 바꾸는 방식과 임계값, 정밀도, 재현율을 함께 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (5/10): Logistic Regression

0 또는 1을 예측하는데 왜 이름은 회귀인지, 입문 단계에서 가장 많이 받는 질문 중 하나입니다. 이 혼란은 자연스럽습니다. 로지스틱 회귀는 클래스를 곧바로 내놓는 모델처럼 보이지만, 실제로는 먼저 연속적인 확률을 계산한 뒤 임계값을 기준으로 분류를 결정합니다. 그래서 분류 문제를 다루지만 내부 동작은 확률 모델로 이해하는 편이 맞습니다.

이 글은 Machine Learning 101 시리즈의 다섯 번째 글입니다. 여기서는 시그모이드 함수, 임계값, 정밀도·재현율·F1의 의미를 함께 보면서 로지스틱 회귀를 분류의 가장 기본적인 기준선으로 정리해 보겠습니다.

## 먼저 던지는 질문

- 0 또는 1을 예측하는데 왜 이름은 회귀일까요?
- 시그모이드는 선형 점수를 어떻게 확률로 바꿀까요?
- 왜 0.5 임계값을 항상 정답처럼 쓰면 안 될까요?

## 큰 그림

![Machine Learning 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/05/05-01-diagram.ko.png)

*Machine Learning 101 5장 흐름 개요*

이 그림은 이 장의 핵심 개념들이 어떻게 연결되는지 보여줍니다.



## 시그모이드 함수의 직관

로지스틱 회귀의 핵심은 **시그모이드 함수**입니다. 시그모이드는 어떤 실수 값이든 0과 1 사이로 보냅니다.

$$
\sigma(z) = \frac{1}{1 + e^{-z}}
$$

### 왜 시그모이드를 쓸까요?

1. 선형 회귀 `y_hat = Xw + b`는 `-∞`부터 `+∞`까지의 값을 낼 수 있습니다.
2. 분류 문제에서는 0와 1 사이의 확률을 내고 싶습니다.
3. 시그모이드는 실수를 `(0, 1)` 구간으로 압축하므로 이 역할을 합니다.

### 시그모이드의 특징

- `z = 0` 일 때 `σ(0) = 0.5`입니다.
- `z`가 클수록 `σ(z) → 1`입니다.
- `z`가 작을수록 `σ(z) → 0`입니다.
- S자 모양의 부드러운 곡선입니다.

로지스틱 회귀는 선형 점수를 먼저 계산한 뒤, 시그모이드로 감싸서 확률로 바꿔 줍니다.

## Python 예제: predict_proba로 확률 확인

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)

model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)

# 확률 확인
proba = model.predict_proba(Xte)[:5]
print("Class 0 | Class 1")
for p0, p1 in proba:
    print(f"{p0:.3f}   | {p1:.3f}")

# 예측 레이블
print("Predicted:", model.predict(Xte)[:5])
```

`.predict()`는 확률이 0.5를 넘으면 1, 아니면 0을 반환합니다. `.predict_proba()`를 보면 모델의 확신 정도를 알 수 있습니다.

## 로지스틱 vs 선형 회귀

| 항목 | 로지스틱 회귀 | 선형 회귀 |
|---|---|---|
| 출력 | 0과 1 사이 확률 | 연속값 |
| 손실함수 | Log Loss (Cross-Entropy) | MSE |
| 활용 | 분류 | 회귀 |

이름이 혼란스러운 이유는 로지스틱 회귀가 확률을 출력하기 때문입니다. 최종 분류는 임계값 적용 후에 결정됩니다.
## 왜 중요한가

로지스틱 회귀는 분류 문제의 표준 베이스라인입니다. 해석이 가능하고 빠르며, 임계값을 조정하면 불균형 데이터에서도 꽤 경쟁력 있게 동작합니다.

## 한눈에 보는 개념

## 핵심 용어

- **시그모이드**: 어떤 실수 값이든 `(0, 1)` 구간으로 매핑합니다.
- 확률: 클래스 1일 것이라는 모델의 믿음입니다.
- 임계값: 확률을 클래스 레이블로 바꾸는 기준선입니다.
- 정밀도: 양성이라고 예측한 것 중 실제 양성의 비율입니다.
- 재현율: 실제 양성 중 모델이 잡아낸 비율입니다.

## Before/After

**Before**: "정확도 95%"라는 숫자만 보고 만족합니다. 불균형 데이터에서는 거의 의미가 없습니다.

**After**: 정밀도, 재현율, F1, AUC를 함께 보고 임계값까지 조정합니다.

## 실습: 5단계로 보는 분류

### Step 1 — 데이터

```python
from sklearn.datasets import load_breast_cancer
X, y = load_breast_cancer(return_X_y=True)
```

### Step 2 — 분할과 스케일링

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
```

### Step 3 — 학습

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
```

### Step 4 — 평가

```python
from sklearn.metrics import classification_report
print(classification_report(yte, model.predict(Xte)))
```

### Step 5 — 임계값 조정

```python
prob = model.predict_proba(Xte)[:, 1]
for t in [0.3, 0.5, 0.7]:
    pred = (prob >= t).astype(int)
    print(t, (pred == yte).mean())
```

**예상 출력:** `classification_report`는 클래스별 정밀도와 재현율을 보여 주고, 임계값 루프는 같은 모델이라도 cutoff를 바꾸면 결과가 달라진다는 점을 드러냅니다. 즉, 임계값 선택은 표시 옵션이 아니라 **모델링 결정**입니다.

## 이 코드에서 먼저 봐야 할 점

- `predict_proba`는 레이블이 아니라 확률을 반환합니다.
- 임계값은 정밀도-재현율 절충을 조절하는 손잡이입니다.
- `StandardScaler`는 최적화가 수렴하는 데 도움을 줍니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 정확도는 높은데 중요한 양성을 놓친다면, 모델보다 먼저 **재현율**과 **임계값**을 봐야 합니다.
- 확률이 지나치게 자신 있어 보이면 `predict_proba`를 곧바로 믿기보다 **보정(calibration)** 여부를 확인해야 합니다.
- 계수가 불안정하게 흔들리면 solver보다 먼저 **스케일링**과 **클래스 불균형**을 점검하는 편이 낫습니다.

## 자주 하는 실수 5가지

1. **원시 확률이 이미 보정되어 있다고 가정합니다.**
2. **항상 0.5를 임계값으로 사용합니다.**
3. **불균형 데이터에서 정확도만 보고합니다.**
4. **피처 스케일링을 빼먹습니다.**
5. **다중 클래스에서 명시적 multinomial 설정 없이 기본값만 믿습니다.**

## 실무에서는 이렇게 나타납니다

스팸 필터링, 사기 탐지, 이탈 예측처럼 다운스트림 시스템이 **비용을 저울질해야 하는 문제**에서는 확률 출력이 필수입니다. 그래서 로지스틱 회귀는 단순한 분류 모델이 아니라 운영 의사결정의 입력 신호가 됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 임계값은 **비즈니스 비용**이 결정합니다.
- 항상 정밀도-재현율 곡선을 그립니다.
- 불균형에는 class weight를 검토합니다.
- 해석 가능성은 중요한 레버리지입니다.
- 확률 보정은 별도로 검증합니다.

## 체크리스트

- [ ] 후속 의사결정에 `predict_proba`를 사용합니다.
- [ ] 정밀도와 재현율을 함께 보고합니다.
- [ ] 비용 기준으로 임계값을 정합니다.
- [ ] 항상 피처를 스케일링합니다.

## 연습 문제

1. 임계값을 0.1부터 0.9까지 바꿔 가며 정밀도와 재현율을 그려 보세요.
2. `class_weight="balanced"`를 적용했을 때 결과를 비교해 보세요.
3. 다중 클래스 데이터셋에 `multi_class="multinomial"`을 적용해 보세요.

## 정리

로지스틱 회귀는 분류의 기초입니다. 선형 점수를 시그모이드로 확률로 바꾸고, 그 확률에 임계값을 적용해 최종 클래스를 정한다는 구조를 이해하면 이름 때문에 생기는 혼란도 사라집니다.

이 글에서 기억할 핵심은 네 가지입니다. 첫째, 로지스틱 회귀는 확률 모델입니다. 둘째, 0.5는 기본 임계값일 뿐 절대 기준이 아닙니다. 셋째, 불균형 데이터에서는 정확도만으로는 부족합니다. 넷째, 분류 문제는 결국 비용 구조에 맞춰 임계값을 조정해야 합니다.

다음 글에서는 비선형 모델의 대표 예시인 Decision Tree와 Random Forest를 살펴보겠습니다.

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

- **0 또는 1을 예측하는데 왜 이름은 회귀일까요?**
  - 본문의 기준은 Logistic Regression를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **시그모이드는 선형 점수를 어떻게 확률로 바꿀까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **왜 0.5 임계값을 항상 정답처럼 쓰면 안 될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Machine Learning 101 (1/10): Machine Learning이란 무엇인가?](./01-what-is-machine-learning.md)
- [Machine Learning 101 (2/10): 지도학습과 비지도학습](./02-supervised-and-unsupervised.md)
- [Machine Learning 101 (3/10): Train/Test Split](./03-train-test-split.md)
- [Machine Learning 101 (4/10): Linear Regression](./04-linear-regression.md)
- **Logistic Regression (현재 글)**
- Decision Tree와 Random Forest (예정)
- Clustering (예정)
- Overfitting과 Regularization (예정)
- Model Evaluation (예정)
- ML 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Logistic Regression](https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression)
- [scikit-learn — Classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics)
- [Google — Classification thresholds](https://developers.google.com/machine-learning/crash-course/classification/thresholding)
- [StatQuest — Logistic Regression](https://www.youtube.com/watch?v=yIYKR4sgzI8)

Tags: MachineLearning, LogisticRegression, Classification, scikit-learn, Beginner

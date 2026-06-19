---
series: model-evaluation-101
episode: 2
title: "Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - ModelEvaluation
  - TrainValTest
  - DataLeakage
  - CrossValidation
  - scikit-learn
seo_description: 일반화 성능 보장을 위한 데이터 분할 방법과 데이터 누수를 방지하여 신뢰할 수 있는 실험 환경을 구축하는 원칙을 설명합니다.
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기

팀 동료가 "우리 모델 AUC 0.97 나왔어요!"라고 외쳤습니다. 모두가 기뻐했습니다. 그런데 며칠 뒤 배포 후 실제 성능은 AUC 0.71이었습니다. 무슨 일이 있었을까요? 조사해 보니 전처리 스케일러를 전체 데이터에 맞춘 뒤 분할을 했고, 같은 사용자의 데이터가 훈련과 테스트 양쪽에 들어가 있었습니다. 데이터 누수였습니다.

이 글은 Model Evaluation 101 시리즈의 2번째 글입니다.

모델 성능은 지표를 계산하는 순간보다 데이터를 나누는 순간에 이미 상당 부분 결정됩니다. 분할이 잘못되면 이후에 나오는 모든 점수는 그럴듯해 보여도 신뢰할 수 없습니다. 특히 전처리를 먼저 해 버리거나, 시계열 데이터를 무작위로 섞거나, 같은 사용자가 여러 세트에 동시에 들어가면 성능은 쉽게 부풀려집니다.

train, validation, test의 역할 분리는 단순한 교과서 규칙이 아닙니다. 어떤 데이터로 학습하고, 어떤 데이터로 고르고, 어떤 데이터로 최종 확인할지 구분하는 훈련이 평가의 바닥을 만듭니다.

![Model Evaluation 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/02/02-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 2장 흐름 개요*

> Train·validation·test는 학습·선택·최종 검증이라는 서로 다른 세 역할입니다 — 이 역할이 한 번 섞이면 이후 모든 숫자가 깔끔해 보이면서도 신뢰할 수 없는 상태가 됩니다.

## 이 글에서 다룰 문제

- train, validation, test는 각각 무엇을 맡아야 할까요?
- 왜 validation과 test를 같은 용도로 쓰면 안 될까요?
- 데이터 누수는 어떤 경로로 가장 자주 들어올까요?
- 누수를 탐지하는 방법이 있을까요?
- 시계열과 그룹 데이터에서는 어떻게 달라져야 할까요?

## 세 세트의 역할과 원칙

### 훈련 세트 (Train Set)

모델 파라미터를 학습하는 데이터입니다. 이 세트를 반복해서 보면서 가중치를 업데이트합니다. 전체 데이터의 60~70%를 차지합니다.

**규칙:** 전처리(스케일링, 인코딩 등)의 `fit`은 오직 훈련 세트에서만 수행합니다.

### 검증 세트 (Validation Set)

하이퍼파라미터를 조정하고 모델을 선택하는 데이터입니다. "어떤 모델이 더 좋은가?", "레이어를 몇 개로 할까?", "임계값을 어디에 둘까?" 같은 선택 문제를 해결합니다. 전체 데이터의 15~20%를 차지합니다.

**규칙:** 모델 선택과 임계값 결정은 이 세트에서만 합니다. 이 세트를 반복해서 보면 이 세트에 과적합될 위험이 있습니다.

### 테스트 세트 (Test Set)

최종 성능을 마지막으로 한 번만 확인하는 데이터입니다. 모든 선택이 끝난 뒤, 배포 결정을 내리기 직전에 한 번만 사용합니다. 전체 데이터의 15~20%를 차지합니다.

**규칙:** 이 세트는 절대 모델 선택이나 임계값 조정에 사용하지 않습니다. 한 번 사용하면 그것으로 끝입니다.

### 세 역할의 비유

- **훈련 세트** = 교과서와 연습 문제 (공부)
- **검증 세트** = 모의고사 (전략 조정)
- **테스트 세트** = 실제 수능 시험 (최종 평가)

모의고사를 보고 틀린 문제를 공부하는 것은 좋습니다. 하지만 실제 수능 문제지를 미리 보고 공부하면 그 점수는 의미가 없습니다.

## 데이터 누수의 세 가지 경로

### 누수 유형 1 — 전처리 누수 (가장 흔한 실수)

전체 데이터에 스케일러나 인코더를 먼저 맞추면 검증/테스트 세트의 통계 정보가 훈련에 새어 들어갑니다.

```python
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.metrics import roc_auc_score

X, y = make_classification(n_samples=5000, n_features=20, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# [나쁜 방식] 전체 데이터에 fit
scaler_bad = StandardScaler().fit(X)  # X_test 정보가 포함됨
X_train_bad = scaler_bad.transform(X_train)
X_test_bad = scaler_bad.transform(X_test)

# [올바른 방식] 훈련 데이터에만 fit
scaler_good = StandardScaler().fit(X_train)  # X_train만 봄
X_train_good = scaler_good.transform(X_train)
X_test_good = scaler_good.transform(X_test)

model_bad = LogisticRegression(max_iter=1000).fit(X_train_bad, y_train)
model_good = LogisticRegression(max_iter=1000).fit(X_train_good, y_train)

auc_bad = roc_auc_score(y_test, model_bad.predict_proba(X_test_bad)[:, 1])
auc_good = roc_auc_score(y_test, model_good.predict_proba(X_test_good)[:, 1])

print(f"나쁜 방식 AUC (누수 있음): {auc_bad:.4f}")
print(f"올바른 방식 AUC (누수 없음): {auc_good:.4f}")
print(f"누수로 인한 AUC 과대평가: {auc_bad - auc_good:.4f}")
```

이 예제에서 데이터가 충분하면 차이가 작아 보일 수 있습니다. 하지만 데이터가 적거나 반복 실험이 많을수록 누수 효과가 누적됩니다.

### 누수 유형 2 — 시계열 누수 (미래 정보 유입)

시간 순서가 있는 데이터를 무작위로 섞어 분할하면 미래 정보가 과거 학습에 유입됩니다.

```python
from sklearn.model_selection import TimeSeriesSplit
import numpy as np

# 시뮬레이션: 12개월 시계열 데이터
np.random.seed(42)
n_months = 24
time_index = np.arange(n_months)
X_ts = time_index.reshape(-1, 1)
y_ts = (np.sin(time_index * 0.3) + np.random.normal(0, 0.2, n_months) > 0).astype(int)

print("=== 올바른 시계열 분할: 항상 과거 → 미래 ===")
tscv = TimeSeriesSplit(n_splits=4)
for fold, (train_idx, test_idx) in enumerate(tscv.split(X_ts)):
    print(
        f"Fold {fold+1}: "
        f"훈련 월 {train_idx[0]+1}~{train_idx[-1]+1}, "
        f"테스트 월 {test_idx[0]+1}~{test_idx[-1]+1}"
    )

print()
print("=== 잘못된 시계열 분할: 무작위 섞기 ===")
from sklearn.model_selection import KFold
kf = KFold(n_splits=4, shuffle=True, random_state=42)
for fold, (train_idx, test_idx) in enumerate(kf.split(X_ts)):
    print(
        f"Fold {fold+1}: 훈련에 포함된 미래 데이터: "
        f"{sum(t < min(test_idx) for t in train_idx if t > min(test_idx))}건"
    )
```

시계열 데이터에서 무작위 분할을 하면 테스트 세트의 이전 데이터가 훈련에 포함되어 미래를 예측하는 척하지만 실제로는 미래를 보고 학습한 셈이 됩니다.

### 누수 유형 3 — 그룹 누수 (개체 중복)

같은 사용자, 환자, 문서 등이 훈련과 테스트 양쪽에 나타나면 "이 사람은 이전에 어떻게 행동했는가"를 모델이 기억한 채 테스트하게 됩니다.

```python
from sklearn.model_selection import GroupKFold, train_test_split
import numpy as np

# 시뮬레이션: 20명의 사용자, 각 5개의 거래
np.random.seed(42)
n_users = 20
n_transactions_per_user = 5
n_total = n_users * n_transactions_per_user

user_ids = np.repeat(np.arange(n_users), n_transactions_per_user)
X_grp = np.random.randn(n_total, 10)
y_grp = (user_ids % 2 == 0).astype(int)  # 사용자 기반 레이블

print("=== 올바른 그룹 분할: 사용자 단위로 분리 ===")
gkf = GroupKFold(n_splits=5)
for fold, (train_idx, test_idx) in enumerate(gkf.split(X_grp, y_grp, user_ids)):
    train_users = set(user_ids[train_idx])
    test_users = set(user_ids[test_idx])
    overlap = train_users & test_users
    print(f"Fold {fold+1}: 겹치는 사용자 수: {len(overlap)} (항상 0이어야 함)")

print()
print("=== 잘못된 분할: 무작위 (사용자 중복 발생) ===")
from sklearn.model_selection import KFold
kf = KFold(n_splits=5, shuffle=True, random_state=42)
for fold, (train_idx, test_idx) in enumerate(kf.split(X_grp)):
    train_users = set(user_ids[train_idx])
    test_users = set(user_ids[test_idx])
    overlap = train_users & test_users
    print(f"Fold {fold+1}: 겹치는 사용자 수: {len(overlap)} (누수!)")
```

## 누수 탐지 방법

실제 프로젝트에서 누수를 발견하는 실용적인 방법들입니다.

### 방법 1 — AUC가 너무 높으면 의심하기

```python
# 모델 성능이 비현실적으로 높을 때 누수 의심
def check_leakage_suspect(train_score, test_score, threshold=0.02):
    """
    훈련 점수와 테스트 점수의 차이가 너무 작으면 누수 의심
    (보통 테스트가 훈련보다 낮아야 정상)
    """
    diff = train_score - test_score
    if test_score > 0.95:
        print(f"경고: 테스트 AUC {test_score:.3f}가 비현실적으로 높습니다.")
        print("데이터 누수를 의심해야 합니다.")
    if abs(diff) < threshold:
        print(f"경고: 훈련-테스트 차이 {diff:.4f}가 너무 작습니다.")
        print("전처리 누수 또는 레이블 누수를 확인하세요.")
    return diff
```

### 방법 2 — 피처 중요도로 타겟 누수 탐지

```python
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np

def detect_target_leakage(X_df, y, top_n=10):
    """
    피처 중요도가 특정 피처에 극단적으로 몰리면 타겟 누수 의심
    """
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_df, y)

    importances = pd.Series(rf.feature_importances_, index=X_df.columns)
    top_features = importances.nlargest(top_n)

    print("=== 피처 중요도 상위 항목 ===")
    for feat, imp in top_features.items():
        flag = " ← 타겟 누수 의심!" if imp > 0.5 else ""
        print(f"{feat}: {imp:.4f}{flag}")

    return importances
```

### 방법 3 — 분할 전후 성능 비교로 누수 확인

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

def compare_leakage_impact(X, y, random_state=42):
    """
    누수 있는 방식과 올바른 방식의 AUC 차이를 비교
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )

    # 누수 있는 방식
    sc_bad = StandardScaler().fit(X)
    model_bad = LogisticRegression(max_iter=1000)
    model_bad.fit(sc_bad.transform(X_train), y_train)
    auc_bad = roc_auc_score(y_test, model_bad.predict_proba(sc_bad.transform(X_test))[:, 1])

    # 올바른 방식
    sc_good = StandardScaler().fit(X_train)
    model_good = LogisticRegression(max_iter=1000)
    model_good.fit(sc_good.transform(X_train), y_train)
    auc_good = roc_auc_score(y_test, model_good.predict_proba(sc_good.transform(X_test))[:, 1])

    print(f"누수 있는 방식 AUC: {auc_bad:.4f}")
    print(f"올바른 방식 AUC:    {auc_good:.4f}")
    print(f"누수로 인한 과대평가: +{auc_bad - auc_good:.4f}")

    return auc_bad, auc_good
```

## 올바른 분할 파이프라인 구현

아래는 전체적으로 올바른 분할 절차를 한 번에 보여주는 코드입니다.

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score, classification_report

# 1단계: 데이터 생성
X, y = make_classification(
    n_samples=5000,
    n_features=20,
    n_informative=8,
    weights=[0.8, 0.2],
    random_state=42,
)

# 2단계: 분할 (전처리보다 먼저!)
X_trainval, X_test, y_trainval, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
X_train, X_val, y_train, y_val = train_test_split(
    X_trainval, y_trainval, test_size=0.25, stratify=y_trainval, random_state=42
)

print(f"훈련 세트: {X_train.shape[0]}건 ({X_train.shape[0]/len(X)*100:.0f}%)")
print(f"검증 세트: {X_val.shape[0]}건 ({X_val.shape[0]/len(X)*100:.0f}%)")
print(f"테스트 세트: {X_test.shape[0]}건 ({X_test.shape[0]/len(X)*100:.0f}%)")
print()

# 3단계: 전처리 (훈련 세트에만 fit)
scaler = StandardScaler().fit(X_train)  # X_train만 봄!
X_train_sc = scaler.transform(X_train)
X_val_sc = scaler.transform(X_val)
X_test_sc = scaler.transform(X_test)

# 4단계: 훈련 및 검증
model = LogisticRegression(max_iter=2000, random_state=42)
model.fit(X_train_sc, y_train)

val_proba = model.predict_proba(X_val_sc)[:, 1]
val_auc = roc_auc_score(y_val, val_proba)
print(f"검증 세트 AUC: {val_auc:.4f}  ← 모델 선택/임계값 결정용")

# 5단계: 검증 세트로 임계값 결정
from sklearn.metrics import f1_score
import numpy as np

best_threshold = 0.5
best_f1 = 0
for t in np.arange(0.1, 0.9, 0.05):
    val_pred = (val_proba >= t).astype(int)
    f1 = f1_score(y_val, val_pred)
    if f1 > best_f1:
        best_f1 = f1
        best_threshold = t

print(f"검증 세트 최적 임계값: {best_threshold:.2f} (F1={best_f1:.4f})")

# 6단계: 최종 평가 (테스트 세트는 딱 한 번만!)
test_proba = model.predict_proba(X_test_sc)[:, 1]
test_pred = (test_proba >= best_threshold).astype(int)
test_auc = roc_auc_score(y_test, test_proba)
print(f"\n테스트 세트 AUC: {test_auc:.4f}  ← 최종 보고용 (한 번만 확인)")
print(f"\n{classification_report(y_test, test_pred)}")
```

## Before vs. After: 분할 방식 비교

| 항목 | 잘못된 방식 | 올바른 방식 |
| --- | --- | --- |
| 전처리 시점 | 전체 데이터에 fit | 훈련 세트에만 fit |
| 검증 세트 역할 | 없거나 테스트와 혼용 | 모델 선택 및 임계값 결정 전용 |
| 테스트 세트 사용 | 반복 확인 후 조정 | 딱 한 번만 최종 확인 |
| 시계열 처리 | 무작위 섞기 | 시간 순서 보존 |
| 그룹 처리 | 무시 | GroupKFold 사용 |
| 성능 추정 | 낙관적 (부풀어 있음) | 현실적 |

## 자주 하는 실수

**실수 1 — Pipeline 없이 수동으로 전처리**

가장 안전한 방법은 scikit-learn의 `Pipeline`을 사용하는 것입니다. Pipeline은 `fit` 단계에서 전처리와 학습을 묶어 처리하므로 전처리 누수가 구조적으로 차단됩니다.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# Pipeline을 쓰면 누수가 구조적으로 차단됨
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression(max_iter=1000)),
])

pipe.fit(X_train, y_train)  # scaler는 X_train만 봄
pipe.score(X_test, y_test)  # scaler는 X_train 통계를 X_test에 적용
```

**실수 2 — 탐색적 분석(EDA)도 금지라고 오해**

분할 전에 데이터를 탐색하고 이해하는 것은 괜찮습니다. 금지되는 것은 전처리의 `fit`(평균, 분산 등 통계 계산)이나 기준선 설정이 분할 전에 이루어지는 것입니다.

**실수 3 — 검증 세트를 너무 자주 보기**

검증 세트를 100번 들여다보며 임계값을 조정했다면, 그 검증 세트에 대한 과적합입니다. 검증 세트도 소중히 다루어야 합니다.

**실수 4 — 작은 데이터에서 고정 분할 고집**

데이터가 1,000건 미만이라면 고정 train/val/test 분할보다 교차 검증이 더 신뢰할 수 있는 추정치를 줍니다. 8장에서 다룰 교차 검증은 이런 상황을 위한 도구입니다.

## 운영 체크리스트

- [ ] 전처리(`fit`)는 반드시 훈련 세트에만 적용했습니다.
- [ ] 검증 세트와 테스트 세트의 역할을 명확히 분리했습니다.
- [ ] 테스트 세트는 최종 평가 직전까지 보지 않았습니다.
- [ ] 시계열 데이터라면 `TimeSeriesSplit`을 사용했습니다.
- [ ] 그룹 데이터라면 `GroupKFold`를 사용했습니다.
- [ ] `Pipeline`을 사용해 누수를 구조적으로 차단했습니다.
- [ ] 임계값 탐색은 검증 세트에서만 수행했습니다.

## 처음 질문으로 돌아가기

- **train, validation, test는 각각 무엇을 맡아야 할까요?**
  - 훈련 세트는 모델 파라미터 학습, 검증 세트는 하이퍼파라미터 조정과 모델 선택 및 임계값 결정, 테스트 세트는 최종 성능 확인(딱 한 번)을 담당합니다. 이 역할 분리가 무너지면 이후 모든 점수가 신뢰할 수 없어집니다.

- **왜 validation과 test를 같은 용도로 쓰면 안 될까요?**
  - 검증 세트를 반복해서 보며 모델을 조정하면, 그 세트에 과적합됩니다. 그렇게 되면 검증 세트는 더 이상 독립적인 평가 기준이 아닙니다. 테스트 세트를 최후의 독립적 검증 기준으로 보존하려면, 모든 선택 과정에서 테스트 세트는 사용하면 안 됩니다.

- **데이터 누수는 어떤 경로로 가장 자주 들어올까요?**
  - 세 가지 경로가 가장 흔합니다. 첫째, 전처리 누수: 전체 데이터에 스케일러를 맞추면 검증/테스트의 통계가 훈련에 새어 들어갑니다. 둘째, 시계열 누수: 무작위 분할로 미래 정보가 과거 학습에 포함됩니다. 셋째, 그룹 누수: 같은 개체(사용자, 환자 등)가 훈련과 테스트 양쪽에 나타납니다.

---

## 정리

데이터 분할은 평가의 준비 단계가 아니라 평가 그 자체의 일부입니다. train은 학습, validation은 선택, test는 최종 확인이라는 역할을 끝까지 지켜야 점수가 의미를 가집니다. 가장 중요한 규칙은 두 가지입니다. 전처리의 `fit`은 훈련 세트에만 적용하고, 테스트 세트는 배포 결정 직전에 딱 한 번만 봅니다.

다음 글에서는 이렇게 준비된 평가 위에서 정확도라는 지표가 어디까지 유효한지, 그리고 불균형 데이터에서 정확도가 어떻게 우리를 속이는지 살펴봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- **Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기 (현재 글)**
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): 정밀도와 재현율](./04-precision-and-recall.md)
- [Model Evaluation 101 (5/10): F1 점수](./05-f1-score.md)
- [Model Evaluation 101 (6/10): ROC와 AUC 이해하기](./06-roc-and-auc.md)
- [Model Evaluation 101 (7/10): 확률 보정 이해하기](./07-calibration.md)
- [Model Evaluation 101 (8/10): 교차 검증 이해하기](./08-cross-validation.md)
- [Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기](./09-error-analysis.md)
- [Model Evaluation 101 (10/10): 평가 리포트 만들기](./10-evaluation-report.md)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn — TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [Forecasting: Principles and Practice — Hyndman](https://otexts.com/fpp3/)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, TrainValTest, DataLeakage, CrossValidation, scikit-learn

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

이 글은 Model Evaluation 101 시리즈의 2번째 글입니다.

모델 성능은 지표를 계산하는 순간보다 데이터를 나누는 순간에 이미 상당 부분 결정됩니다. 분할이 잘못되면 이후에 나오는 모든 점수는 그럴듯해 보여도 신뢰할 수 없습니다. 특히 전처리를 먼저 해 버리거나, 시계열 데이터를 무작위로 섞거나, 같은 사용자가 여러 세트에 동시에 들어가면 성능은 쉽게 부풀려집니다.

그래서 train, validation, test의 역할 분리는 단순한 교과서 규칙이 아닙니다. 어떤 데이터로 학습하고, 어떤 데이터로 고르고, 어떤 데이터로 최종 확인할지 구분하는 훈련이 평가의 바닥을 만듭니다.


![Model Evaluation 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/02/02-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 2장 흐름 개요*

## 먼저 던지는 질문

- train, validation, test는 각각 무엇을 맡아야 할까요?
- 왜 validation과 test를 같은 용도로 쓰면 안 될까요?
- 데이터 누수는 어떤 경로로 가장 자주 들어올까요?

## 왜 이 글이 중요한가

분할 전략이 잘못되면 비교 자체가 불가능해집니다. 두 모델 중 하나가 더 좋아 보이더라도, 그 차이가 모델의 힘인지 누수의 부산물인지 알 수 없기 때문입니다. 평가가 아니라 착시가 되는 셈입니다.

실무에서는 특히 세 가지 누수가 자주 나옵니다. 전체 데이터에 스케일러를 먼저 맞추는 전처리 누수, 미래 정보를 과거 학습에 흘려보내는 시계열 누수, 같은 사용자나 문서가 서로 다른 분할에 등장하는 그룹 누수입니다. 이 셋을 막는 것만으로도 평가의 질이 크게 올라갑니다.

## 한눈에 보는 멘탈 모델

먼저 나누고, 그다음 학습해야 합니다. 전처리 역시 같은 원칙을 따릅니다. 나누기 전에 전체를 들여다보며 통계를 맞추는 순간, 답이 조금씩 새어 들어갑니다.

## 핵심 용어

- **훈련 세트(train)**: 모델 파라미터를 학습하는 데이터입니다.
- **검증 세트(validation)**: 하이퍼파라미터를 조정하고 모델을 고르는 데이터입니다.
- **테스트 세트(test)**: 최종 성능을 마지막으로 확인하는 데이터입니다.
- **누수(leakage)**: 정답이나 미래 정보가 부적절하게 학습 과정으로 스며드는 현상입니다.
- **그룹 분할(group split)**: 같은 개체가 서로 다른 분할에 동시에 나오지 않도록 막는 방식입니다.

## 분할을 잘못 볼 때와 제대로 볼 때

잘못된 방식은 전체 데이터를 다 본 뒤 일부를 떼어 점수를 확인하는 흐름입니다. 이 방법은 빠르지만, 실제로는 평가 기준을 스스로 흐리게 만듭니다. 반대로 제대로 된 방식은 train, validation, test를 분리하고, 전처리와 학습도 분할 이후에만 수행하는 것입니다.

이 차이는 점수 한두 자리보다 더 중요합니다. 분할 원칙이 지켜져야 이후의 정확도, F1, AUC도 해석할 수 있습니다.

## 다섯 가지 분할 패턴 실습

### 1단계 — 기본 분할

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
X, y = load_iris(return_X_y=True)
Xtrv, Xte, ytrv, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
Xtr, Xva, ytr, yva = train_test_split(Xtrv, ytrv, test_size=0.25, stratify=ytrv, random_state=42)
print(Xtr.shape, Xva.shape, Xte.shape)
```

### 2단계 — 누수 시연

```python
from sklearn.preprocessing import StandardScaler
sc_bad = StandardScaler().fit(X)
sc_ok = StandardScaler().fit(Xtr)
```

### 3단계 — 시계열 분할

```python
from sklearn.model_selection import TimeSeriesSplit
import numpy as np
ts = np.arange(20).reshape(-1, 1)
for tr, te in TimeSeriesSplit(n_splits=3).split(ts):
    print(tr[-1], te[0])
```

### 4단계 — 그룹 분할

```python
from sklearn.model_selection import GroupKFold
groups = np.array([1,1,1,2,2,3,3,3,4,4])
X = np.arange(10).reshape(-1, 1); y = np.arange(10)
for tr, te in GroupKFold(n_splits=2).split(X, y, groups):
    print(set(groups[te]))
```

### 5단계 — 분할 후 학습

```python
from sklearn.linear_model import LogisticRegression
sc = StandardScaler().fit(Xtr)
m = LogisticRegression(max_iter=1000).fit(sc.transform(Xtr), ytr)
print("valid:", m.score(sc.transform(Xva), yva))
```

**예상 결과:** 전체 데이터에 맞춘 스케일러와 훈련 세트에만 맞춘 스케일러의 차이가 왜 중요한지 감이 와야 합니다. 시간 순서와 그룹 경계를 지키는 분할이 단순한 형식이 아니라 평가 신뢰도를 지키는 장치라는 점이 핵심입니다.

## 이 코드에서 먼저 봐야 할 점

두 번째 코드가 이 글의 핵심입니다. 전체 데이터에 `StandardScaler`를 맞추면 훈련 전에 이미 검증과 테스트의 통계를 본 셈이 됩니다. 아주 작은 정보 누수처럼 보여도 비교가 반복될수록 성능은 부풀려집니다.

세 번째와 네 번째 코드는 분할 방식이 데이터 성격에 따라 달라져야 한다는 점을 보여 줍니다. 시간 순서가 중요한 데이터는 과거에서 미래로 가야 하고, 같은 사용자가 여러 샘플로 나뉜 데이터는 그룹 단위로 묶어야 합니다.

## 자주 헷갈리는 지점

많이 나오는 오해는 탐색적 데이터 분석도 금지라고 생각하는 것입니다. 분할 전에 데이터를 이해하는 일은 괜찮습니다. 문제는 전처리의 `fit`이나 기준선 결정이 분할 전 전체 데이터를 먹는 순간입니다.

또 다른 오해는 테스트 세트를 자주 봐도 괜찮다는 생각입니다. 하지만 테스트를 반복해서 확인하는 순간 그 세트는 더 이상 최종 검증 세트가 아닙니다. 검증 세트와 같은 역할로 전락합니다.

## 실무에서는 이렇게 생각한다

강한 팀은 분할 전략을 모델보다 먼저 리뷰합니다. 추천 시스템이면 사용자나 세션 누수를 먼저 의심하고, 금융 데이터면 시간 순서를 먼저 확인합니다. 모델 구조를 바꾸는 것보다 분할 원칙을 바로잡는 편이 더 큰 차이를 내는 경우도 많습니다.

또한 각 세트의 역할을 문서로 남깁니다. 무엇이 튜닝용이고 무엇이 최종 보고용인지 분명하지 않으면, 시간이 지난 뒤 누구나 테스트 점수를 다시 쓰고 싶어집니다. 평가의 엄격함은 기억이 아니라 규칙에서 나옵니다.

## 점검 목록

- [ ] train, validation, test를 분리해 사용합니다.
- [ ] 전처리 `fit`은 분할 이후에만 수행합니다.
- [ ] 시계열 데이터는 시간 순서를 지켜 분할합니다.
- [ ] 그룹 정보가 있으면 명시적으로 분리합니다.

## 정리

데이터 분할은 평가의 준비 단계가 아니라 평가 그 자체의 일부입니다. train은 학습, validation은 선택, test는 최종 확인이라는 역할을 끝까지 지켜야 점수가 의미를 가집니다. 다음 글에서는 이렇게 준비된 평가 위에서 정확도라는 지표가 어디까지 유효한지 살펴보겠습니다.


## 평가 실무에서 바로 쓰는 계산 루틴

### confusion matrix를 수식과 코드로 동시에 확인하기
평가 지표는 라이브러리 호출만으로 끝내면 해석이 약해집니다. confusion matrix를 직접 계산해 보면 지표의 민감도를 빠르게 이해할 수 있습니다.

```python
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
import numpy as np

y_true = np.array([1,0,1,1,0,0,1,0,1,0])
y_pred = np.array([1,0,1,0,0,1,1,0,1,0])

tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
precision = tp / (tp + fp)
recall = tp / (tp + fn)
f1 = 2 * precision * recall / (precision + recall)

print(tn, fp, fn, tp)
print(round(precision, 4), round(recall, 4), round(f1, 4))
```

직접 계산한 값과 `precision_score`, `recall_score`, `f1_score` 결과가 일치해야 합니다. 일치하지 않으면 positive label 설정, threshold, 또는 데이터 정렬이 틀린 경우가 많습니다. 이 교차검증 절차는 평가 파이프라인의 기본 안전장치입니다.

### threshold 스윕으로 ROC와 운영 임계값 연결하기
ROC-AUC는 모델 분리 능력을 보여주지만, 실제 운영은 단일 threshold를 선택해야 합니다. 따라서 `0.1` 간격 또는 더 촘촘한 구간으로 threshold를 스윕해 TPR/FPR 변화를 확인하는 단계가 필요합니다.

```python
from sklearn.metrics import roc_curve, roc_auc_score
import numpy as np

y_true = np.array([1,0,1,1,0,0,1,0,1,0])
y_score = np.array([0.91,0.12,0.82,0.45,0.31,0.72,0.88,0.28,0.79,0.21])

fpr, tpr, thresholds = roc_curve(y_true, y_score)
auc = roc_auc_score(y_true, y_score)

best = None
for th in np.linspace(0.1, 0.9, 17):
    pred = (y_score >= th).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
    tpr_now = tp / (tp + fn)
    fpr_now = fp / (fp + tn)
    score = tpr_now - fpr_now
    if best is None or score > best[0]:
        best = (score, th, tpr_now, fpr_now)

print("AUC:", round(auc, 4))
print("best threshold:", best)
```

여기서 `TPR - FPR` 최대 지점을 임시 후보로 잡고, 비즈니스 비용(오탐 처리 비용, 미탐 손실 비용)을 반영해 최종 threshold를 확정합니다. 즉, ROC는 시각화 도구이면서 동시에 정책 결정 입력값입니다.

### 교차검증 결과를 분포로 보고 불확실성 기록하기
단일 점수는 모델 안정성을 숨깁니다. `StratifiedKFold`로 fold별 점수 분포를 남기면 "성능 평균"뿐 아니라 "성능 흔들림"도 관리할 수 있습니다.

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=2000, n_features=20, weights=[0.8, 0.2], random_state=42)
model = LogisticRegression(max_iter=1000)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scores = cross_val_score(model, X, y, cv=cv, scoring="f1")
print("fold scores:", [round(s, 4) for s in scores])
print("mean/std:", round(scores.mean(), 4), round(scores.std(), 4))
```

표준편차가 큰 모델은 데이터 구간에 따라 성능이 크게 달라질 수 있으므로, 배포 전에 데이터 분할 기준과 샘플링 전략을 재점검해야 합니다. 보고서에는 평균과 함께 분산 정보를 반드시 기록해 의사결정의 근거를 명확히 남겨야 합니다.

## 운영 의사결정을 위한 평가 해석 확장

### 클래스 불균형에서 PR 곡선 확인
불균형 데이터에서는 ROC-AUC만으로 품질을 과대평가할 수 있습니다. 양성 비율이 낮을 때는 precision-recall 곡선을 함께 확인해야 실제 운영 난이도를 반영할 수 있습니다.

```python
from sklearn.metrics import precision_recall_curve, average_precision_score
import matplotlib.pyplot as plt

precision, recall, th = precision_recall_curve(y_true, y_score)
ap = average_precision_score(y_true, y_score)

print("AP:", round(ap, 4))
for i in range(0, len(th), max(1, len(th)//5)):
    print("th=", round(th[i], 3), "precision=", round(precision[i], 3), "recall=", round(recall[i], 3))
```

PR 곡선에서 운영팀이 감당 가능한 precision 구간을 먼저 정하고, 그때의 recall 손실을 확인하는 방식이 현실적입니다. 즉 지표 선택은 수학 문제가 아니라 운영 비용 문제와 연결됩니다.

### 비용 민감 confusion matrix
같은 오탐/미탐이라도 비용이 다르면 최적 모델이 달라집니다. 예를 들어 미탐 비용이 오탐보다 5배 크면 다음처럼 총비용을 계산해 비교할 수 있습니다.

```python
from sklearn.metrics import confusion_matrix

cost_fp = 1
cost_fn = 5

pred = (y_score >= 0.42).astype(int)
tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()

total_cost = fp * cost_fp + fn * cost_fn
print({"fp": int(fp), "fn": int(fn), "cost": int(total_cost)})
```

평가 보고서에 이 비용 지표를 함께 두면 모델 교체 기준이 명확해집니다. "AUC가 더 높다"는 주장보다 "월간 예상 손실을 18% 줄인다"는 근거가 훨씬 강합니다.

### 캘리브레이션 확인 루틴
점수 기반 의사결정에서는 확률 신뢰성이 중요합니다. 예측확률이 0.8인 샘플 집합에서 실제 양성 비율이 0.8에 근접하는지 확인해야 합니다.

```python
from sklearn.calibration import calibration_curve

prob_true, prob_pred = calibration_curve(y_true, y_score, n_bins=10)
for p_hat, p_real in zip(prob_pred, prob_true):
    print(round(p_hat, 3), round(p_real, 3), round(p_real - p_hat, 3))
```

차이가 큰 구간은 후처리 보정 대상입니다. Platt scaling이나 isotonic regression 적용 전후를 같은 표로 기록하면, 확률 품질이 실제로 개선되었는지 검증 가능합니다.


## 실무 앵커: 지표를 운영 의사결정으로 연결하는 확장 절차

앞선 본문이 개념의 뼈대를 잡아 주었다면, 이 절은 운영에서 바로 재사용할 수 있는 공통 앵커를 제공합니다. 모델 평가를 문서로만 끝내지 않고 재현 가능한 코드와 해석 규칙으로 남겨 두면, 다음 실험이나 다음 분기 리뷰에서도 같은 기준으로 비교할 수 있습니다. 특히 팀이 커질수록 "누가 돌려도 같은 결론이 나오는가"가 중요해지므로, 지표 계산 코드와 해석 문장을 함께 관리해야 합니다.

### 혼동 행렬을 숫자표에서 행동 지침으로 읽는 방법

혼동 행렬은 단순히 `TN, FP, FN, TP`를 보여 주는 표가 아닙니다. 어떤 오류를 줄여야 실제 비용이 내려가는지 가리키는 운영 지도입니다. 예를 들어 FP가 늘어나면 운영팀의 수동 검토 부담이 급증하고, FN이 늘어나면 놓침 손실이 직접 비용으로 돌아옵니다. 따라서 혼동 행렬을 읽을 때는 "점수"보다 "어떤 팀에 어떤 부담이 이동하는가"를 먼저 기록하는 편이 안전합니다.

```python
from sklearn.metrics import confusion_matrix
import numpy as np

y_true = np.array([1,0,1,1,0,0,1,0,1,0,1,0,0,1,0,1])
y_pred = np.array([1,0,1,0,0,1,1,0,1,0,0,0,0,1,0,1])

tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
print({'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)})

review_load = fp
missed_cases = fn
print('수동 검토 건수(오탐):', review_load)
print('놓친 중요 건수(미탐):', missed_cases)
```

해석 문장을 고정해 두면 리뷰 품질이 안정됩니다. 예를 들어 "이번 배포 후보는 오탐 9건을 추가로 만들지만 미탐 14건을 줄인다"처럼 효과를 방향성으로 적으면, 단일 지표 숫자보다 의사결정이 훨씬 명확해집니다.

### ROC 곡선과 임계값 탐색을 함께 기록하기

ROC-AUC는 모델이 양성과 음성을 얼마나 잘 분리하는지 보여 주는 요약 숫자이지만, 실제 운영은 특정 임계값 하나를 선택해야 끝납니다. 그래서 AUC만 보고 배포 결정을 내리면 운영에서 필요한 FPR 상한이나 알림량 제한을 놓치기 쉽습니다. 안전한 방식은 ROC 곡선과 함께 임계값 후보 표를 같이 남기는 것입니다.

```python
from sklearn.metrics import roc_curve, roc_auc_score
import numpy as np

y_true = np.array([1,0,1,1,0,0,1,0,1,0,1,0,0,1,0,1])
y_score = np.array([0.91,0.05,0.87,0.52,0.34,0.61,0.84,0.21,0.79,0.18,0.64,0.07,0.28,0.73,0.14,0.69])

fpr, tpr, thresholds = roc_curve(y_true, y_score)
auc = roc_auc_score(y_true, y_score)
print('roc_auc:', round(auc, 4))

for th in [0.2, 0.35, 0.5, 0.65, 0.8]:
    pred = (y_score >= th).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
    now_fpr = fp / (fp + tn)
    now_tpr = tp / (tp + fn)
    print({'threshold': th, 'fpr': round(now_fpr, 3), 'tpr': round(now_tpr, 3)})
```

운영 문서에는 "허용 가능한 오탐 비율(FPR)"을 먼저 적고 그 경계 안에서 재현율(TPR)이 가장 높은 임계값을 선택하는 규칙을 고정하는 편이 좋습니다. 이렇게 하면 담당자가 바뀌어도 같은 정책으로 같은 결론을 재현할 수 있습니다.

### 교차검증을 평균 점수에서 분포 분석으로 확장하기

교차검증은 평균 점수 한 줄로 끝내기 쉽지만, 실제로는 fold별 분포가 더 중요한 신호를 줍니다. 평균이 높아도 표준편차가 큰 모델은 특정 데이터 구간에서 갑자기 성능이 무너질 수 있기 때문입니다. 따라서 배포 전 리뷰에서는 "평균"과 "흔들림"을 함께 기록해야 합니다.

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
import numpy as np

X, y = make_classification(
    n_samples=3000,
    n_features=24,
    n_informative=8,
    n_redundant=4,
    weights=[0.85, 0.15],
    random_state=42,
)

model = LogisticRegression(max_iter=2000)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
result = cross_validate(
    model,
    X,
    y,
    cv=cv,
    scoring={'f1': 'f1', 'roc_auc': 'roc_auc', 'recall': 'recall'},
)

for key in ['test_f1', 'test_roc_auc', 'test_recall']:
    arr = result[key]
    print(key, 'mean=', round(arr.mean(), 4), 'std=', round(arr.std(), 4), 'min=', round(arr.min(), 4))
```

여기서 `std`와 `min`이 크게 흔들리면 모델 구조보다 데이터 분할과 표본 추출 전략을 먼저 재검토해야 합니다. 특히 소수 클래스 성능이 fold마다 크게 갈리면 임계값을 아무리 조정해도 운영 안정성이 낮습니다.

### 캘리브레이션 플롯으로 확률 신뢰성 점검하기

분류 모델 점수가 후속 의사결정의 우선순위를 정한다면, 확률의 신뢰성은 정확도만큼 중요합니다. 예측확률 0.8 집합의 실제 양성 비율이 0.8과 멀다면, 점수 기반 우선순위가 계속 왜곡됩니다. 그래서 보정(calibration) 단계에서는 플롯과 수치 요약을 함께 남겨야 합니다.

```python
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
import numpy as np

# 예시 점수
y_true = np.array([1,0,1,1,0,0,1,0,1,0,1,0,0,1,0,1])
y_score = np.array([0.91,0.05,0.87,0.52,0.34,0.61,0.84,0.21,0.79,0.18,0.64,0.07,0.28,0.73,0.14,0.69])

prob_true, prob_pred = calibration_curve(y_true, y_score, n_bins=6)
print('before calibration')
for p_hat, p_real in zip(prob_pred, prob_true):
    print(round(p_hat, 3), round(p_real, 3), 'diff=', round(p_real - p_hat, 3))

iso = IsotonicRegression(out_of_bounds='clip').fit(y_score, y_true)
y_cal = iso.predict(y_score)
prob_true2, prob_pred2 = calibration_curve(y_true, y_cal, n_bins=6)
print('after calibration')
for p_hat, p_real in zip(prob_pred2, prob_true2):
    print(round(p_hat, 3), round(p_real, 3), 'diff=', round(p_real - p_hat, 3))
```

리뷰 문서에는 "보정 전/후 Brier score 변화"와 "고확률 구간 과대신뢰 완화 여부"를 함께 남기면 좋습니다. 이렇게 기록하면 모델 교체 시 확률 품질이 실제로 개선되었는지 빠르게 검증할 수 있습니다.

### 오류 분석 워크플로를 표준 운영 절차로 만들기

지표가 하락했을 때 바로 모델 구조부터 바꾸면 원인 분해가 어려워집니다. 먼저 오류 샘플을 패턴으로 묶고, 데이터 문제인지 피처 문제인지 의사결정 경계 문제인지 분리해야 합니다. 아래와 같은 절차를 템플릿으로 운영하면 재발 방지까지 연결하기 좋습니다.

1. **오류 추출**: FP/FN 샘플을 최근 배치 기준으로 수집합니다.
2. **하위군 분해**: 채널, 지역, 디바이스, 시간대 등 운영 축으로 오류율을 나눕니다.
3. **설명 변수 확인**: 누락값, 스케일 불일치, 범주 희소성 같은 데이터 문제를 확인합니다.
4. **임계값 시뮬레이션**: 후보 임계값별 FP/FN 비용을 계산해 정책을 재검토합니다.
5. **수정 실험**: 데이터 정제/피처 보강/보정 모델 적용 후 동일 지표로 재검증합니다.
6. **재발 방지**: 실패 패턴을 경보 규칙과 체크리스트에 반영합니다.

```python
import pandas as pd

# 예시 오류 분석 테이블
analysis = pd.DataFrame(
    {
        'segment': ['web', 'app', 'kiosk', 'web', 'app', 'kiosk'],
        'is_error': [1, 1, 0, 1, 0, 1],
        'error_type': ['FN', 'FP', 'none', 'FN', 'none', 'FP'],
    }
)

summary = (
    analysis.groupby(['segment', 'error_type'])
    .size()
    .rename('count')
    .reset_index()
)
print(summary)
```

오류 분석 결과를 남길 때는 "무엇이 나빴다"보다 "어떤 축에서 반복적으로 나빴고 다음 주기에 무엇을 바꿀 것인가"를 중심으로 쓰는 편이 좋습니다. 그래야 평가가 회고 문서가 아니라 개선 루프의 입력으로 동작합니다.

### 최종 리뷰 문장 템플릿

실무 보고서에서는 숫자를 나열하는 대신 결정에 바로 연결되는 문장을 쓰는 편이 좋습니다. 다음 템플릿은 대부분의 분류 과제에서 그대로 재사용할 수 있습니다.

- 베이스레이트와 더미 기준선을 먼저 제시합니다.
- 핵심 운영 비용에 연결되는 지표(재현율, 정밀도, FPR)를 같은 문단에서 해석합니다.
- ROC/PR, 캘리브레이션, 교차검증 분포를 함께 보고 안정성을 평가합니다.
- 최종 임계값 선택 이유와 예상 운영 비용 변화를 수치로 남깁니다.
- 다음 실험에서 바꿀 가설을 한 줄로 명시합니다.

이 절의 목적은 평가를 더 복잡하게 만드는 것이 아닙니다. 오히려 동일한 질문을 반복 가능한 절차로 고정해, 모델이 바뀌어도 팀의 의사결정 품질을 유지하는 데 있습니다.

## 처음 질문으로 돌아가기

- **train, validation, test는 각각 무엇을 맡아야 할까요?**
  - 본문의 기준은 훈련·검증·테스트 데이터 나누기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **왜 validation과 test를 같은 용도로 쓰면 안 될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **데이터 누수는 어떤 경로로 가장 자주 들어올까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- **훈련·검증·테스트 데이터 나누기 (현재 글)**
- 정확도의 한계 (예정)
- 정밀도와 재현율 (예정)
- F1 점수 (예정)
- ROC와 AUC 이해하기 (예정)
- 확률 보정 이해하기 (예정)
- 교차 검증 이해하기 (예정)
- 오류 분석으로 약점 찾기 (예정)
- 평가 리포트 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn — TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [Forecasting: Principles and Practice — Hyndman](https://otexts.com/fpp3/)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, TrainValTest, DataLeakage, CrossValidation, scikit-learn

---
series: model-evaluation-101
episode: 3
title: "Model Evaluation 101 (3/10): 정확도의 한계"
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
  - Accuracy
  - ImbalancedData
  - BaselineModel
  - scikit-learn
seo_description: 불균형 데이터에서 정확도를 더미 기준선, 소수 클래스 재현율, 균형 정확도와 함께 읽는 방법을 설명합니다.
last_reviewed: '2026-05-17'
---

# Model Evaluation 101 (3/10): 정확도의 한계

이 글은 Model Evaluation 101 시리즈의 3번째 글입니다.


정확도는 계산이 쉽고 설명도 편하지만, 그래서 오히려 너무 일찍 결론을 내리게 만드는 지표입니다. issue #772가 지적한 핵심도 여기에 있습니다. 기존 글은 정확도의 한계를 설명했지만, 실제 판단 순서인 베이스레이트 → 더미 기준선 → 소수 클래스 재현율 → 균형 정확도 → 최종 리뷰 흐름으로 독자를 끌고 가지 못했습니다.

이번 글에서는 정확도를 맨 앞 숫자가 아니라 **마지막 확인 숫자**로 다루겠습니다. 특히 `ko/03-limits-of-accuracy.md:64-69,115-131`에서 약했던 부분을 보강해, 높은 정확도가 실제 개선인지 아니면 다수 클래스가 만든 착시인지 운영자 관점에서 판정하는 절차로 재구성하겠습니다.

## 먼저 던지는 질문

- 정확도의 한계를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?
- 정확도의 한계에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?
- 정확도의 한계를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?

## 큰 그림

![Model Evaluation 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/03/03-01-concept-at-a-glance.ko.png)

*Model Evaluation 101 3장 흐름 개요*

## 이 글이 답하는 질문

- 더미 기준선보다 약간 높은 정확도는 언제 의미가 약할까요?
- 소수 클래스 재현율과 균형 정확도는 정확도의 착시를 어떻게 벗겨 낼까요?
- 최종 보고서에서 정확도를 대표 숫자로 써도 되는지 어떻게 판단할까요?

## 이번 글의 판단 순서

정확도 해석은 다음 다섯 단계로 고정해 두는 편이 안전합니다.

1. **베이스레이트 확인**: 양성 비율이 얼마나 낮은지 먼저 봅니다.
2. **더미 기준선 비교**: 아무것도 학습하지 않은 모델이 이미 몇 점인지 확인합니다.
3. **소수 클래스 재현율 확인**: 정말 중요한 양성을 얼마나 놓치는지 봅니다.
4. **균형 정확도 추가**: 다수 클래스와 소수 클래스를 공평하게 평균 냅니다.
5. **정확도 보고 여부 결정**: 위 네 단계를 통과한 뒤에만 정확도를 요약 숫자로 남깁니다.

이 순서를 거꾸로 읽으면 `acc 96%` 같은 숫자에 속기 쉽습니다. 이 순서를 지키면 같은 96%라도 “실제 개선”과 “다수 클래스 안락함”을 구분할 수 있습니다.

## 한눈에 보는 멘탈 모델

핵심은 간단합니다. 클래스 비율이 크게 기울어져 있으면 정확도는 바로 읽는 숫자가 아니라, 다른 점검을 마친 뒤에만 참고할 수 있는 숫자입니다.

## 한 번에 끝내는 진단 코드

아래 코드는 정확도를 해석할 때 필요한 순서를 한 번에 보여 줍니다.

```python
from sklearn.datasets import make_classification
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    recall_score,
)
from sklearn.model_selection import train_test_split

X, y = make_classification(
    n_samples=5000,
    n_features=20,
    n_informative=5,
    n_redundant=2,
    weights=[0.96, 0.04],
    class_sep=1.1,
    flip_y=0.015,
    random_state=42,
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    stratify=y,
    random_state=42,
)

dummy = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
pred = model.predict(X_test)

print("base rate:", round(y.mean(), 4))
print("dummy accuracy:", round(dummy.score(X_test, y_test), 4))
print("model accuracy:", round(accuracy_score(y_test, pred), 4))
print("minority recall:", round(recall_score(y_test, pred), 4))
print("balanced accuracy:", round(balanced_accuracy_score(y_test, pred), 4))
print("confusion matrix:\n", confusion_matrix(y_test, pred))
print(classification_report(y_test, pred, digits=4))
```

예상 해석은 다음과 같습니다.

```text
base rate: 0.0468
dummy accuracy: 0.9536
model accuracy: 0.9608
minority recall: 0.1897
balanced accuracy: 0.5940
confusion matrix:
[[1190    2]
 [  47   11]]
```

정확도만 보면 96.08%라서 꽤 좋아 보입니다. 하지만 이 숫자를 더미 기준선 95.36%와 나란히 두는 순간 해석이 달라집니다. **정확도 이득은 0.72%포인트**뿐인데, 실제 양성 58개 중 47개를 놓쳤기 때문입니다.

## 1단계 — 베이스레이트를 먼저 보면 무엇이 달라질까요?

양성 비율이 4.68%라는 뜻은, 아무 생각 없이 대부분을 음성으로 찍어도 높은 정확도를 얻기 쉽다는 의미입니다. 즉 이 문제에서 정확도는 모델 실력보다 데이터 분포의 도움을 많이 받습니다.

이 한 줄이 중요한 이유는 이후 숫자들의 기준점을 미리 정해 주기 때문입니다. 베이스레이트가 50:50이 아니라는 사실을 먼저 알면, `96%`라는 숫자를 보는 순간에도 “실력”보다 “분포”를 먼저 의심하게 됩니다.

## 2단계 — 더미 기준선과의 비교가 왜 필수일까요?

`DummyClassifier(strategy="most_frequent")`는 모든 사례를 다수 클래스로 예측합니다. 여기서도 이 더미는 이미 **95.36% 정확도**를 냅니다. 즉 정확도만 놓고 보면 실제 모델은 겨우 조금 더 나아졌을 뿐입니다.

실무에서 이 비교가 빠지면 팀은 다음처럼 착각하기 쉽습니다.

- 잘못된 해석: `96%니까 충분히 좋다.`
- 올바른 해석: `기준선이 95.36%인데 96.08%면, 정확도 개선은 작다. 다른 지표를 바로 확인해야 한다.`

정확도는 더미와의 차이까지 붙여 읽어야 의미가 생깁니다.

## 3단계 — 소수 클래스 재현율이 사실상 본체입니다

이 예제의 소수 클래스 재현율은 **0.1897**입니다. 실제 양성 중 18.97%만 잡았다는 뜻입니다. 다시 말해 양성 100건이 들어오면 약 81건을 놓치는 모델입니다.

이 숫자가 중요한 이유는 정확도가 감추는 실패를 바로 드러내기 때문입니다. 혼동 행렬의 아래 행을 보면 실제 양성 58개 중 11개만 맞히고 47개를 놓쳤습니다. 사기 탐지, 희귀 질환 분류, 장애 경보처럼 놓침이 비싼 문제라면 이 모델은 아직 보고서 첫 줄에 올릴 상태가 아닙니다.

## 4단계 — 균형 정확도가 공평한 요약을 제공합니다

균형 정확도는 각 클래스 재현율의 평균입니다. 이 예제에서는 **0.5940**으로, 정확도 0.9608과 전혀 다른 그림을 보여 줍니다. 다수 클래스는 거의 완벽하게 맞히지만 소수 클래스는 크게 놓치므로, 공평하게 평균 내면 모델의 체감 성능이 급격히 내려갑니다.

이 차이가 바로 issue #772가 요구한 “정확도의 판단 순서”입니다. 정확도를 그대로 읽지 말고, 소수 클래스 재현율과 균형 정확도로 한번 뒤집어 봐야 합니다.

## 5단계 — 그러면 정확도를 보고서에 써도 될까요?

이제 마지막 질문을 던질 수 있습니다.

> 이 정확도는 실제 성능 향상인가, 아니면 다수 클래스를 편하게 맞힌 결과인가?

이 예제의 답은 후자에 가깝습니다. 정확도를 완전히 버릴 필요는 없지만, 최소한 다음 조건이 붙어야 합니다.

- 더미 기준선 대비 개선 폭을 함께 보고합니다.
- 소수 클래스 재현율을 같은 문단에 함께 둡니다.
- 균형 정확도를 같이 보고합니다.
- 운영에서 놓침 비용이 크다면 정확도를 대표 지표로 쓰지 않습니다.

즉 이 문제에서는 `accuracy=0.9608`보다 `minority recall=0.1897, balanced accuracy=0.5940`가 더 먼저 나와야 합니다.

## 실무 결정 리뷰 템플릿

정확도 검토를 보고서 문장으로 남길 때는 아래처럼 쓰면 됩니다.

> 베이스레이트 4.68% 문제에서 모델 정확도는 96.08%로 더미 기준선 95.36%보다 0.72%포인트 높았습니다. 그러나 소수 클래스 재현율은 18.97%, 균형 정확도는 59.40%에 그쳤으므로, 이 모델은 “정확도 개선”보다 “양성 놓침 위험”이 더 큰 상태로 판단합니다.

이 문장 구조를 익혀 두면, 정확도 하나만 강조하는 보고서를 자연스럽게 교정할 수 있습니다.

## 점검 목록

- [ ] 베이스레이트를 먼저 확인합니다.
- [ ] 더미 기준선과 정확도를 나란히 비교합니다.
- [ ] 소수 클래스 재현율을 별도 숫자로 적습니다.
- [ ] 균형 정확도를 함께 보고합니다.
- [ ] 정확도를 대표 지표로 쓸지 마지막에 결정합니다.

## 정리

정확도는 쓸모없는 지표가 아니라 **순서가 중요한 지표**입니다. 베이스레이트와 더미 기준선, 소수 클래스 재현율, 균형 정확도를 거친 뒤에야 비로소 읽을 수 있습니다. 다음 글에서는 이 흐름을 이어 받아, 임계값을 움직일 때 정밀도와 재현율이 어떤 운영 선택으로 연결되는지 살펴보겠습니다.


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

- **정확도의 한계를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?**
  - 본문의 기준은 정확도의 한계를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **정확도의 한계에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **정확도의 한계를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- **정확도의 한계 (현재 글)**
- 정밀도와 재현율 (예정)
- F1 점수 (예정)
- ROC와 AUC 이해하기 (예정)
- 확률 보정 이해하기 (예정)
- 교차 검증 이해하기 (예정)
- 오류 분석으로 약점 찾기 (예정)
- 평가 리포트 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — DummyClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html)
- [scikit-learn — accuracy_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html)
- [scikit-learn — balanced_accuracy_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html)
- [Wikipedia — Accuracy paradox](https://en.wikipedia.org/wiki/Accuracy_paradox)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, Accuracy, ImbalancedData, BaselineModel, scikit-learn

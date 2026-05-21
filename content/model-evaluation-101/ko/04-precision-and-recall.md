---
series: model-evaluation-101
episode: 4
title: "Model Evaluation 101 (4/10): 정밀도와 재현율"
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
  - Precision
  - Recall
  - ConfusionMatrix
  - scikit-learn
seo_description: 정밀도와 재현율을 정의 설명에서 끝내지 않고, 임계값을 바꿀 때 운영 알림 정책이 어떻게 달라지는지 결정 메모 형식으로 보여 줍니다.
last_reviewed: '2026-05-17'
---

# Model Evaluation 101 (4/10): 정밀도와 재현율

이 글은 Model Evaluation 101 시리즈의 4번째 글입니다.

issue #772는 이 장이 다른 장들과 비슷한 리듬으로 반복된다고 지적했습니다. 실제로 `ko/04-precision-and-recall.md:43-68`은 “왜 중요한가 → 멘탈 모델 → 핵심 용어” 설명에 머무르고, 운영자가 가장 먼저 던져야 할 질문인 **임계값을 내리면 무엇이 늘고, 올리면 무엇을 놓치는가**를 중심에 두지 못했습니다.

그래서 이번 글은 정의 설명보다 **운영 임계값 결정 메모**에 가깝게 다시 씁니다. 정밀도와 재현율은 개념 암기용 용어가 아니라, 알림을 얼마나 더 보내고 얼마나 더 놓칠지를 결정하는 숫자라는 관점으로 읽겠습니다.

## 먼저 던지는 질문

- 정밀도와 재현율를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?
- 정밀도와 재현율에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?
- 정밀도와 재현율를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?

## 큰 그림

![Model Evaluation 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/04/04-01-concept-at-a-glance.ko.png)

*Model Evaluation 101 4장 흐름 개요*

## 이 글이 답하는 질문

- 임계값을 낮추거나 올릴 때 리뷰 큐와 놓침은 어떻게 달라질까요?
- 운영 기본값으로 0.35 같은 절충점을 고르는 근거는 무엇일까요?
- AP는 왜 유용하지만 배포 임계값을 대신 정해 주지는 못할까요?

## 운영 시나리오 먼저 정하겠습니다

가정은 단순합니다. 이 모델은 사용자의 결제 이상 징후를 탐지해 리뷰 큐로 보내는 시스템입니다.

- **재현율이 낮으면** 실제 이상 거래를 놓칩니다.
- **정밀도가 낮으면** 리뷰 팀이 불필요한 경보를 너무 많이 받습니다.

이 문제에서 중요한 질문은 “정밀도와 재현율이 무엇인가?”보다 다음 문장입니다.

> 임계값을 0.20, 0.35, 0.50, 0.70 중 어디에 둘 때 운영이 버틸 수 있을까요?

## 한눈에 보는 멘탈 모델

임계값을 내리면 더 많은 사례를 양성으로 보게 되어 재현율은 올라가지만, 동시에 거짓 경보도 늘어나 정밀도는 내려가기 쉽습니다. 이 장의 핵심은 이 교환을 숫자와 운영 문장으로 연결하는 데 있습니다.

## 결정 메모를 만드는 코드

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

X, y = make_classification(
    n_samples=3000,
    n_features=10,
    n_informative=5,
    n_redundant=2,
    weights=[0.9, 0.1],
    class_sep=1.0,
    flip_y=0.02,
    random_state=7,
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    stratify=y,
    random_state=42,
)

model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
proba = model.predict_proba(X_test)[:, 1]

for threshold in [0.20, 0.35, 0.50, 0.70]:
    pred = (proba >= threshold).astype(int)
    print(
        threshold,
        "precision=", round(precision_score(y_test, pred), 3),
        "recall=", round(recall_score(y_test, pred), 3),
        "flagged=", int(pred.sum()),
        "cm=", confusion_matrix(y_test, pred).tolist(),
    )

print("AP:", round(average_precision_score(y_test, proba), 3))
```

위 코드는 임계값을 바꿀 때 알림 수와 혼동 행렬이 함께 어떻게 바뀌는지 보여 줍니다. 예상 결과는 다음과 같습니다.

```text
0.20 precision= 0.610 recall= 0.735 flagged= 118 cm= [[756, 46], [26, 72]]
0.35 precision= 0.795 recall= 0.633 flagged= 78  cm= [[786, 16], [36, 62]]
0.50 precision= 0.881 recall= 0.531 flagged= 59  cm= [[795, 7],  [46, 52]]
0.70 precision= 0.952 recall= 0.408 flagged= 42  cm= [[800, 2],  [58, 40]]
AP: 0.745
```

## 운영점 표로 읽으면 판단이 빨라집니다

| 임계값 | 정밀도 | 재현율 | 리뷰 큐 크기 | 실무 해석 |
| --- | ---: | ---: | ---: | --- |
| 0.20 | 0.610 | 0.735 | 118건 | 많이 잡지만 오탐이 많아 리뷰 부담이 큽니다. |
| 0.35 | 0.795 | 0.633 | 78건 | 놓침과 오탐이 모두 관리 가능한 절충점입니다. |
| 0.50 | 0.881 | 0.531 | 59건 | 큐는 가벼워지지만 놓침이 눈에 띄게 늘어납니다. |
| 0.70 | 0.952 | 0.408 | 42건 | 경보는 매우 깨끗하지만 실제 이상 거래를 많이 놓칩니다. |

이 표가 중요한 이유는 정밀도와 재현율을 정의가 아니라 **운영 결과**로 번역해 주기 때문입니다. 같은 모델이라도 임계값을 바꾸는 것만으로 전혀 다른 제품이 됩니다.

## 추천 운영점: 왜 0.35를 메모의 기본값으로 둘까요?

이 예제에서는 **0.35**가 가장 설명력 있는 기준점입니다.

- 0.20보다 정밀도가 크게 좋아집니다. `0.610 → 0.795`
- 0.50보다 재현율이 덜 무너집니다. `0.633` 대 `0.531`
- 리뷰 큐도 118건에서 78건으로 줄어 운영 부담이 낮아집니다.

즉 “실제 이상 거래를 너무 많이 놓치지 않으면서도, 리뷰 팀이 감당 가능한 수준으로 경보를 줄이자”라는 메모를 쓰기에 0.35가 자연스럽습니다.

## 정밀도와 재현율은 이렇게 짧게 기억하면 충분합니다

- **정밀도**: 경보를 울린 것 중 진짜가 얼마나 되나요?
- **재현율**: 실제 진짜를 얼마나 놓치지 않았나요?

중요한 것은 정의 자체보다, 이 두 숫자가 임계값과 함께 어떻게 움직이는지입니다. issue #772가 요구한 서사 전환도 바로 여기 있습니다. 이번 장은 “용어 설명”보다 “임계값 메모”가 되어야 합니다.

## 평균 정밀도(AP)는 왜 같이 남길까요?

위 코드의 AP는 **0.745**입니다. 이 숫자는 모든 임계값을 훑은 뒤의 요약 점수이므로, 현재 모델이 전반적으로 어느 정도의 정밀도-재현율 곡선을 갖는지 알려 줍니다. 다만 AP만으로는 배포할 임계값이 정해지지 않습니다.

즉 AP는 **후보 모델 비교용 숫자**이고, 실제 운영 메모는 여전히 표와 혼동 행렬에서 나와야 합니다.

## 운영 메모를 문장으로 남기면 이렇게 됩니다

> 결제 이상 징후 탐지 모델에서 임계값 0.35는 정밀도 0.795, 재현율 0.633, 리뷰 큐 78건을 제공합니다. 0.20은 재현율은 높지만 거짓 경보가 많고, 0.50 이상은 큐는 줄지만 놓침이 커집니다. 따라서 현재 운영 기본값은 0.35로 두고, 리스크 이벤트가 증가하는 기간에는 0.20으로 완화하는 방안을 별도 검토합니다.

이런 문장이 있으면 정밀도와 재현율이 단순 지표가 아니라 정책 결정 근거가 됩니다.

## 점검 목록

- [ ] 임계값별 정밀도·재현율 표를 만듭니다.
- [ ] 리뷰 큐 크기나 후속 작업량을 함께 적습니다.
- [ ] 혼동 행렬로 놓침과 오탐을 동시에 확인합니다.
- [ ] AP를 후보 모델 비교용 숫자로만 사용합니다.

## 정리

정밀도와 재현율은 정의보다 **운영점 선택**에서 가치가 드러납니다. 임계값을 바꿀 때 어떤 실수가 늘고 줄어드는지 메모 형식으로 남겨야 실제 의사결정에 쓸 수 있습니다. 다음 글에서는 이렇게 드러난 정밀도-재현율 교환을 하나의 숫자로 압축한 F1을 다루되, 그 요약이 무엇을 숨기는지도 함께 살펴보겠습니다.


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

## 처음 질문으로 돌아가기

- **정밀도와 재현율를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?**
  - 본문의 기준은 정밀도와 재현율를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **정밀도와 재현율에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **정밀도와 재현율를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- **정밀도와 재현율 (현재 글)**
- F1 점수 (예정)
- ROC와 AUC 이해하기 (예정)
- 확률 보정 이해하기 (예정)
- 교차 검증 이해하기 (예정)
- 오류 분석으로 약점 찾기 (예정)
- 평가 리포트 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html)
- [scikit-learn — recall_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.recall_score.html)
- [scikit-learn — average_precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
- [scikit-learn — precision_recall_curve example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html)

Tags: ModelEvaluation, Precision, Recall, ConfusionMatrix, scikit-learn

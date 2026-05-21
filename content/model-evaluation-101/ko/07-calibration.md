---
series: model-evaluation-101
episode: 7
title: "Model Evaluation 101 (7/10): 확률 보정 이해하기"
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
  - Calibration
  - BrierScore
  - Reliability
  - scikit-learn
seo_description: 분류 모델의 확률값이 실제 빈도와 일치하도록 보정하는 캘리브레이션 개념과 브라이어 점수 기반 신뢰도 측정법을 다룹니다.
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (7/10): 확률 보정 이해하기

모델이 0.8의 확률을 예측했다고 할 때, 우리는 보통 그 숫자를 직관적으로 받아들입니다. 하지만 그 0.8이 실제로도 10번 중 8번 정도 맞는지를 확인하지 않으면, 그 숫자는 점수처럼 보일 뿐 확률이라고 부르기 어렵습니다. 바로 이 지점을 다루는 개념이 calibration입니다.

순위 성능이 좋은 모델이 곧 확률까지 정직한 모델인 것은 아닙니다. AUC가 높아도 확률값은 과신하거나 과소신할 수 있습니다. 광고 입찰, 보험 심사, 리스크 스코어링처럼 확률값 그 자체를 비용 계산에 쓰는 시스템에서는 이 차이가 곧 손실로 이어집니다.

이 글은 Model Evaluation 101 시리즈의 7번째 글입니다.

## 먼저 던지는 질문

- 모델이 예측한 확률을 왜 그대로 믿으면 안 될까요?
- 신뢰도 곡선은 무엇을 보여 줄까요?
- Brier 점수는 어떤 종류의 오류를 요약할까요?

## 큰 그림

![Model Evaluation 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/07/07-01-concept-at-a-glance.ko.png)

*Model Evaluation 101 7장 흐름 개요*

## 왜 이 글이 중요한가

순위가 좋은 모델은 후보를 줄이는 데는 쓸 만할 수 있습니다. 그러나 확률값 자체를 가격 결정이나 경보 우선순위에 쓰려면 이야기가 달라집니다. 0.9라고 말한 사례가 실제로는 절반만 맞는다면, 시스템은 꾸준히 잘못된 의사결정을 하게 됩니다.

보정은 그래서 운영에서 특히 중요합니다. 예측 확률에 비용을 곱하거나, 기대값을 계산하거나, 여러 모델의 점수를 조합하는 순간부터는 점수의 순서뿐 아니라 숫자 자체의 의미가 중요해집니다.

## 한눈에 보는 멘탈 모델

예측 확률 구간별 평균과 실제 양성 빈도를 나란히 놓고 비교해야 합니다. 두 값이 대각선 위에 가깝게 맞아야 확률이 정직하다고 말할 수 있습니다.

## 핵심 용어

- **보정(calibration)**: 예측 확률과 실제 빈도가 잘 맞는 상태입니다.
- **신뢰도 곡선(reliability diagram)**: 확률 구간별 예측값과 실제 빈도를 비교하는 그래프입니다.
- **Brier 점수**: `(p - y)^2`의 평균이며 낮을수록 좋습니다.
- **Platt 보정**: 시그모이드 함수를 이용한 후처리 방식입니다.
- **Isotonic 회귀**: 단조 증가 제약만 두고 더 유연하게 맞추는 방식입니다.

## 보정을 읽는 방식의 전환

좋지 않은 습관은 확률값을 점수처럼만 보는 것입니다. `0.93`이 높아 보인다고 해서 실제로 93% 정도 맞는다고 가정하면 곧바로 해석 오류가 생깁니다.

좋은 습관은 확률값의 순위와 진실성을 분리해 보는 것입니다. 순위는 ROC나 PR이 말해 주고, 진실성은 보정이 말해 줍니다. 이 둘을 따로 읽을 수 있어야 확률 기반 의사결정이 안정해집니다.

## 보정을 살펴보는 다섯 단계

### 1단계 — 데이터와 모델

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
X, y = make_classification(n_samples=3000, weights=[0.7, 0.3], random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=42)
rf = RandomForestClassifier(n_estimators=100, random_state=0).fit(Xtr, ytr)
proba = rf.predict_proba(Xte)[:, 1]
```

### 2단계 — 신뢰도 곡선

```python
from sklearn.calibration import calibration_curve
frac_pos, mean_pred = calibration_curve(yte, proba, n_bins=10)
for mp, fp in zip(mean_pred, frac_pos):
    print(round(mp, 2), round(fp, 2))
```

### 3단계 — Brier 점수

```python
from sklearn.metrics import brier_score_loss
print("brier:", brier_score_loss(yte, proba))
```

### 4단계 — Platt 보정

```python
from sklearn.calibration import CalibratedClassifierCV
platt = CalibratedClassifierCV(rf, method="sigmoid", cv=5).fit(Xtr, ytr)
print("brier (platt):", brier_score_loss(yte, platt.predict_proba(Xte)[:, 1]))
```

### 5단계 — Isotonic 보정

```python
iso = CalibratedClassifierCV(rf, method="isotonic", cv=5).fit(Xtr, ytr)
print("brier (isotonic):", brier_score_loss(yte, iso.predict_proba(Xte)[:, 1]))
```

**예상 결과:** 원래 확률이 실제 빈도와 얼마나 어긋나는지 확인한 뒤, sigmoid와 isotonic 중 어떤 방식이 Brier 점수를 더 안정적으로 낮추는지 비교하면 됩니다. 순위가 좋아도 확률 해석은 여전히 틀릴 수 있다는 점이 핵심입니다.

## 이 코드에서 먼저 봐야 할 점

두 번째 단계는 확률 구간별로 실제 빈도가 얼마나 따라오는지 보여 줍니다. 대각선에서 멀어질수록 과신하거나 과소신하는 구간이 있다는 뜻입니다. 세 번째 단계의 Brier 점수는 이 차이를 한 숫자로 요약합니다.

네 번째와 다섯 번째 단계는 보정 방식의 차이를 보여 줍니다. 일반적으로 작은 데이터에서는 sigmoid 방식이 더 안정적이고, 데이터가 충분할 때는 isotonic이 더 유연하게 맞을 수 있습니다. 다만 유연함이 곧 안전함은 아닙니다.

## 자주 헷갈리는 지점

첫째, AUC가 높으면 확률도 믿을 만하다고 생각하기 쉽습니다. 하지만 둘은 다른 축입니다. 둘째, 훈련 데이터에 바로 보정을 맞추면 과적합 위험이 커집니다. 보정도 별도의 검증 절차가 필요합니다.

셋째, 신뢰도 곡선의 구간 수를 너무 적거나 많게 잡으면 해석이 흔들립니다. 넷째, 보정 후에도 예전 임계값을 그대로 쓰면 운영 성능이 어긋날 수 있습니다. 확률 분포가 바뀌었기 때문입니다.

## 실무에서는 이렇게 생각한다

시니어 엔지니어는 확률을 돈과 연결하는 순간부터 보정을 필수 항목으로 봅니다. 순위 성능이 충분하더라도, 확률이 거짓말하면 기대값 계산은 모두 틀어집니다. 그래서 보정은 선택적 미세 조정이 아니라 의사결정 품질 관리에 가깝습니다.

또한 보정은 한 번 하고 끝나지 않습니다. 데이터 분포가 바뀌면 확률 해석도 바뀔 수 있으므로, 드리프트가 생기면 다시 확인하고 필요하면 재보정해야 합니다.

## 점검 목록

- [ ] 신뢰도 곡선을 확인합니다.
- [ ] Brier 점수를 비교합니다.
- [ ] 보정용 데이터 분리를 지킵니다.
- [ ] 보정 후 임계값을 다시 검토합니다.

## 정리

보정은 모델이 얼마나 잘 맞히는가보다, 모델이 말한 확률을 얼마나 믿을 수 있는가를 다룹니다. 순위 성능과 확률 성능은 다르며, 운영에서는 둘 다 중요합니다. 다음 글에서는 한 번의 분할에 기대지 않고 평가 추정치의 안정성을 보는 교차 검증으로 넘어가겠습니다.


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

- **모델이 예측한 확률을 왜 그대로 믿으면 안 될까요?**
  - 본문의 기준은 확률 보정 이해하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **신뢰도 곡선은 무엇을 보여 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Brier 점수는 어떤 종류의 오류를 요약할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): 정밀도와 재현율](./04-precision-and-recall.md)
- [Model Evaluation 101 (5/10): F1 점수](./05-f1-score.md)
- [Model Evaluation 101 (6/10): ROC와 AUC 이해하기](./06-roc-and-auc.md)
- **확률 보정 이해하기 (현재 글)**
- 교차 검증 이해하기 (예정)
- 오류 분석으로 약점 찾기 (예정)
- 평가 리포트 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Calibration](https://scikit-learn.org/stable/modules/calibration.html)
- [scikit-learn — calibration_curve](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.calibration_curve.html)
- [Wikipedia — Brier score](https://en.wikipedia.org/wiki/Brier_score)
- [Niculescu-Mizil & Caruana 2005](https://www.cs.cornell.edu/~alexn/papers/calibration.icml05.crc.rev3.pdf)

Tags: ModelEvaluation, Calibration, BrierScore, Reliability, scikit-learn

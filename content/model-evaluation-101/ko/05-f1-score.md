---
series: model-evaluation-101
episode: 5
title: "Model Evaluation 101 (5/10): F1 점수"
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
  - F1Score
  - Fbeta
  - ImbalancedData
  - scikit-learn
seo_description: F1의 평균 방식 차이와 올바른 train/validation/test 임계값 선택 절차를 설명합니다.
last_reviewed: '2026-05-17'
---

# Model Evaluation 101 (5/10): F1 점수

이 글은 Model Evaluation 101 시리즈의 5번째 글입니다.


정밀도와 재현율을 임계값 메모로 읽고 나면, 팀은 곧바로 “그래서 하나의 숫자로 비교하면 무엇을 쓰면 되나요?”라고 묻습니다. F1은 바로 그 요구에서 자주 등장합니다. 문제는 기존 글의 이진 분류 예제가 `ko/05-f1-score.md:109-118`에서 **학습한 같은 데이터 위에서 임계값을 훑어 F1을 최대화하는 낙관적 패턴**을 가르쳤다는 점입니다.

이번 글은 그 약점을 바로잡습니다. F1은 여전히 유용한 요약 숫자이지만, 임계값 선택은 반드시 **train → validation → test** 순서로 분리해야 합니다. 동시에 macro, micro, weighted 평균이 서로 다른 질문에 답한다는 점도 운영 관점에서 다시 정리하겠습니다.

## 먼저 던지는 질문

- F1 점수를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?
- F1 점수에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?
- F1 점수를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?

## 큰 그림

![Model Evaluation 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/05/05-01-concept-at-a-glance.ko.png)

*Model Evaluation 101 5장 흐름 개요*

## 이 글이 답하는 질문

- macro, micro, weighted F1은 각각 어떤 리뷰 질문에 답할까요?
- 같은 데이터에서 학습과 임계값 탐색을 함께 하면 왜 낙관적일까요?
- 검증셋에서 최고 F1을 준 임계값이 왜 항상 최고의 운영 정책은 아닐까요?

## F1을 쓰기 전에 먼저 기억할 것

F1은 정밀도와 재현율의 조화평균입니다. 그래서 둘 중 하나가 크게 낮으면 점수도 함께 낮아집니다. 다만 F1은 어디까지나 **요약**입니다.

- 어떤 평균 방식을 썼는지 숨길 수 있습니다.
- 어떤 클래스가 약한지 숨길 수 있습니다.
- 어떤 임계값을 선택했는지 숨길 수 있습니다.
- 그 임계값이 검증셋이 아닌 테스트셋에 과적합했는지도 숨길 수 있습니다.

즉 F1은 편리하지만, 절차를 생략하면 쉽게 과신하게 됩니다.

## 한눈에 보는 멘탈 모델

이 그림에서 중요한 갈림길은 두 개입니다. 첫째, 다중 분류에서는 어떤 평균을 쓸지 결정해야 합니다. 둘째, 이진 분류에서는 어떤 임계값에서 F1을 계산할지 결정해야 합니다.

## 1부 — 평균 방식이 다르면 같은 예측도 다른 점수가 됩니다

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, fbeta_score
from sklearn.model_selection import train_test_split

X, y = make_classification(
    n_samples=3200,
    n_features=12,
    n_informative=6,
    n_redundant=2,
    n_classes=3,
    n_clusters_per_class=1,
    weights=[0.65, 0.25, 0.10],
    class_sep=1.1,
    flip_y=0.02,
    random_state=11,
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    stratify=y,
    random_state=42,
)

model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
pred = model.predict(X_test)

print("micro:", round(f1_score(y_test, pred, average="micro"), 3))
print("macro:", round(f1_score(y_test, pred, average="macro"), 3))
print("weighted:", round(f1_score(y_test, pred, average="weighted"), 3))
print("per class:", [round(x, 3) for x in f1_score(y_test, pred, average=None)])
print("F2 macro:", round(fbeta_score(y_test, pred, beta=2, average="macro"), 3))
print("F0.5 macro:", round(fbeta_score(y_test, pred, beta=0.5, average="macro"), 3))
```

예상 결과는 다음과 같습니다.

```text
micro: 0.927
macro: 0.881
weighted: 0.925
per class: [0.952, 0.923, 0.768]
F2 macro: 0.866
F0.5 macro: 0.900
```

이 숫자는 같은 예측을 서로 다르게 요약합니다.

- **micro F1 0.927**: 전체 빈도에 민감합니다. 다수 클래스가 잘 맞으면 높게 나옵니다.
- **macro F1 0.881**: 소수 클래스도 동등하게 한 표를 가집니다.
- **weighted F1 0.925**: 원래 클래스 비율을 반영합니다.
- **per class [0.952, 0.923, 0.768]**: 실제 약점은 세 번째 클래스에 있습니다.

즉 `F1=0.92`처럼 평균 방식을 숨긴 문장은 정보가 부족합니다.

## 2부 — 임계값 선택은 반드시 훈련·검증·테스트로 분리합니다

이제 issue #772가 직접 지적한 문제를 고칩니다. 아래 예제는 같은 데이터에서 학습과 임계값 탐색을 동시에 하지 않습니다.

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

X, y = make_classification(
    n_samples=4000,
    n_features=10,
    n_informative=5,
    n_redundant=2,
    weights=[0.88, 0.12],
    class_sep=1.0,
    flip_y=0.02,
    random_state=19,
)

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.4,
    stratify=y,
    random_state=42,
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.5,
    stratify=y_temp,
    random_state=42,
)

model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
val_proba = model.predict_proba(X_val)[:, 1]
test_proba = model.predict_proba(X_test)[:, 1]

thresholds = np.arange(0.10, 0.91, 0.05)
rows = []
for threshold in thresholds:
    val_pred = (val_proba >= threshold).astype(int)
    rows.append(
        (
            round(float(threshold), 2),
            f1_score(y_val, val_pred),
            precision_score(y_val, val_pred, zero_division=0),
            recall_score(y_val, val_pred, zero_division=0),
        )
    )

best_threshold, best_val_f1, _, _ = max(rows, key=lambda row: row[1])
print("validation sweep:")
for threshold, f1, precision, recall in rows:
    if threshold in {0.20, 0.30, 0.50, 0.70}:
        print(threshold, round(f1, 3), round(precision, 3), round(recall, 3))

print("best validation threshold:", best_threshold, round(best_val_f1, 3))

locked_test_pred = (test_proba >= best_threshold).astype(int)
print(
    "locked test:",
    round(f1_score(y_test, locked_test_pred), 3),
    round(precision_score(y_test, locked_test_pred), 3),
    round(recall_score(y_test, locked_test_pred), 3),
)

business_pred = (test_proba >= 0.50).astype(int)
print(
    "business threshold 0.50:",
    round(f1_score(y_test, business_pred), 3),
    round(precision_score(y_test, business_pred), 3),
    round(recall_score(y_test, business_pred), 3),
)
```

예상 결과는 다음과 같습니다.

```text
validation sweep:
0.20 0.596 0.485 0.775
0.30 0.585 0.564 0.608
0.50 0.503 0.776 0.373
0.70 0.354 0.821 0.225
best validation threshold: 0.2 0.596
locked test: 0.627 0.527 0.775
business threshold 0.50: 0.490 0.717 0.373
```

## 왜 이 절차가 중요한가요?

검증셋에서 **F1이 가장 높은 임계값은 0.20**입니다. 이 값을 고른 뒤, 다시 건드리지 않고 테스트셋에 잠그면 `F1=0.627, precision=0.527, recall=0.775`가 나옵니다. 이 결과는 “검증셋에서 선택한 정책이 테스트셋에서도 어느 정도 유지되는가?”를 확인하게 해 줍니다.

반대로 같은 데이터에서 학습과 임계값 탐색을 동시에 하면, 우연한 패턴까지 흡수한 낙관적 F1을 얻게 됩니다. issue #772가 고치라고 한 부분이 바로 이 지점입니다.

## 그런데 최고의 F1 임계값이 최고의 운영 임계값일까요?

반드시 그렇지는 않습니다. 위 예제에서 0.20은 F1 기준으로 가장 좋지만, 테스트셋 기준으로 보면 양성 경보 150건 중 약 절반이 오탐입니다. 반면 **0.50**은 F1이 낮아도 정밀도가 **0.717**까지 올라갑니다.

즉 이런 질문이 따라와야 합니다.

- 목표가 놓침을 줄이는 것인가요? 그렇다면 0.20이 더 적합할 수 있습니다.
- 목표가 리뷰 팀 피로를 줄이는 것인가요? 그렇다면 0.50 쪽이 나을 수 있습니다.

F1이 말해 주는 것은 “정밀도와 재현율의 균형”이지, “비즈니스가 감당 가능한 정책” 자체는 아닙니다.

## 에프베타 점수는 비용 비중을 숨기지 않는 방법입니다

앞의 다중 분류 예제에서 `F2 macro=0.866`, `F0.5 macro=0.900`이 나온 이유는, 같은 예측도 무엇을 더 중시하느냐에 따라 점수가 달라지기 때문입니다.

- **F2**는 재현율에 더 큰 가중치를 둡니다.
- **F0.5**는 정밀도에 더 큰 가중치를 둡니다.

따라서 beta 값은 취향이 아니라 비용 구조에서 와야 합니다. 놓침이 비싸면 F2 쪽이 맞고, 거짓 경보가 비싸면 F0.5 쪽이 맞습니다.

## 실무 리뷰 문장 예시

> macro F1은 0.881이지만 소수 클래스 F1은 0.768에 그쳤습니다. 이진 운영 정책에서는 검증셋 기준 최적 F1 임계값 0.20을 테스트셋에 잠가 F1 0.627, 정밀도 0.527, 재현율 0.775를 얻었습니다. 다만 리뷰 팀의 false positive 예산을 고려하면 배포 임계값은 0.50으로 더 보수적으로 둘 가능성도 함께 검토해야 합니다.

이 문장은 F1을 요약 숫자로 쓰면서도, 평균 방식과 임계값, 운영 비용을 모두 드러냅니다.

## 점검 목록

- [ ] F1의 평균 방식을 명시합니다.
- [ ] 클래스별 F1을 함께 확인합니다.
- [ ] 임계값 선택은 train/validation/test로 분리합니다.
- [ ] 검증셋에서 고른 임계값을 테스트셋에 잠가서 평가합니다.
- [ ] F1 최댓값과 운영 최적점이 다를 수 있음을 별도로 적습니다.

## 정리

F1은 여전히 유용한 요약 지표이지만, 절차가 빠지면 금세 낙관적 숫자가 됩니다. 올바른 질문은 “F1이 몇 점인가?”가 아니라 “어떤 평균 방식으로, 어떤 검증 절차를 거쳐, 어떤 임계값에서 그 점수가 나왔는가?”입니다. 다음 글에서는 임계값 하나에 덜 묶인 순위화 관점인 ROC와 AUC를 보되, 결국 다시 운영 임계값으로 돌아오는 흐름까지 완성하겠습니다.


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

- **F1 점수를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?**
  - 본문의 기준은 F1 점수를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **F1 점수에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **F1 점수를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): 정밀도와 재현율](./04-precision-and-recall.md)
- **F1 점수 (현재 글)**
- ROC와 AUC 이해하기 (예정)
- 확률 보정 이해하기 (예정)
- 교차 검증 이해하기 (예정)
- 오류 분석으로 약점 찾기 (예정)
- 평가 리포트 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — f1_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html)
- [scikit-learn — fbeta_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.fbeta_score.html)
- [scikit-learn — precision_recall_fscore_support](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html)
- [Wikipedia — F-score](https://en.wikipedia.org/wiki/F-score)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, F1Score, Fbeta, ImbalancedData, scikit-learn

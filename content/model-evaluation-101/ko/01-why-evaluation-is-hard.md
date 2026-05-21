---
series: model-evaluation-101
episode: 1
title: "Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?"
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
  - Metrics
  - MachineLearning
  - Foundations
  - Beginner
seo_description: 머신러닝 모델 평가가 비즈니스 목표와 일치해야 하는 이유를 설명하고, 올바른 평가 지표 설정을 위한 접근법을 제시합니다.
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?

이 글은 Model Evaluation 101 시리즈의 1번째 글입니다.

모델 평가는 처음 배울 때보다 실무에 들어간 뒤 더 어렵게 느껴집니다. 실습에서는 점수 하나만 출력해도 그럴듯해 보이지만, 실제 의사결정은 그렇게 단순하지 않기 때문입니다. 같은 정확도 95%라도 어떤 데이터에서 측정했는지, 어떤 오류가 더 비싼지, 임계값을 어디에 두었는지에 따라 의미가 완전히 달라집니다.

평가가 흔들리면 모델 선택도 흔들립니다. 더 큰 문제는 팀이 잘못된 숫자를 기준으로 같은 방향으로 달려간다는 점입니다. 그래서 평가를 지표 계산이 아니라 의사결정 설계의 일부로 이해해야 합니다.


![Model Evaluation 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/01/01-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 1장 흐름 개요*

## 먼저 던지는 질문

- 왜 정확도 하나만으로 모델을 판단하면 위험할까요?
- 데이터 분포와 베이스레이트는 평가를 어떻게 왜곡할까요?
- 임계값이 바뀌면 같은 모델의 점수는 왜 달라질까요?

## 왜 이 글이 중요한가

평가는 모델 선택의 언어입니다. 이 언어가 부정확하면 비교도 부정확해집니다. 정확도만 높게 나온 모델을 골랐는데 정작 중요한 양성 사례를 거의 잡지 못한다면, 팀은 좋은 모델을 고른 것이 아니라 좋은 착시를 고른 셈입니다.

현업에서는 이런 일이 드물지 않습니다. 데이터가 불균형한데 정확도만 보고 넘어가거나, 테스트 세트를 반복해서 들여다보며 임계값을 조정하거나, 비즈니스 비용을 반영하지 않은 지표로 배포 결정을 내리기도 합니다. 평가가 어려운 이유는 수식이 복잡해서가 아니라, 숫자 뒤의 맥락이 많기 때문입니다.

## 한눈에 보는 멘탈 모델

이 그림에서 중요한 점은 지표가 종착점이 아니라는 사실입니다. 예측은 지표로 요약되지만, 그 지표는 다시 실제 결정으로 이어집니다. 그리고 그 결정의 기준은 늘 비용 구조와 연결됩니다.

## 핵심 용어

- **지표(metric)**: 모델 성능을 숫자로 요약한 값입니다.
- **베이스레이트(base rate)**: 데이터에서 각 클래스가 차지하는 비율입니다.
- **임계값(threshold)**: 확률을 클래스 예측으로 바꾸는 기준선입니다.
- **드리프트(drift)**: 시간이 지나며 데이터 분포가 바뀌는 현상입니다.
- **비용 행렬(cost matrix)**: 서로 다른 오류에 서로 다른 비용을 두는 방식입니다.

## 평가를 잘못 볼 때와 제대로 볼 때

잘못된 출발점은 이렇습니다. 정확도 99%가 나오면 모델이 거의 완성된 것처럼 느낍니다. 그러나 데이터가 95 대 5로 기울어져 있다면, 아무것도 하지 않는 더미 모델도 95%를 만들 수 있습니다.

제대로 보는 방식은 조금 다릅니다. 정확도뿐 아니라 혼동 행렬, 재현율, 임계값 민감도, 비용 구조를 함께 보고, 마지막에는 이 모델이 실제로 어떤 결정을 돕는지까지 연결합니다.

## 평가의 함정을 직접 보는 다섯 단계

### 1단계 — 불균형 데이터

```python
import numpy as np
y = np.array([0]*95 + [1]*5)
pred_dummy = np.zeros_like(y)
print("acc:", (pred_dummy == y).mean())
```

### 2단계 — 정확도의 함정

```python
print("recall (1):", ((pred_dummy == 1) & (y == 1)).sum() / (y == 1).sum())
```

### 3단계 — 혼동 행렬

```python
from sklearn.metrics import confusion_matrix
print(confusion_matrix(y, pred_dummy))
```

### 4단계 — 임계값 민감도

```python
import numpy as np
prob = np.linspace(0, 1, 100)
yt = (prob > 0.5).astype(int)
for t in [0.3, 0.5, 0.7]:
    pred = (prob >= t).astype(int)
    print(t, (pred == yt).mean())
```

### 5단계 — 비용 가중치

```python
def cost(tp, fp, fn, c_fp=1, c_fn=10):
    return c_fp * fp + c_fn * fn
print("cost:", cost(tp=5, fp=10, fn=2))
```

**예상 결과:** 더미 모델은 정확도만 보면 그럴듯해 보여도 재현율과 비용 기준에서는 금방 한계를 드러냅니다. 같은 예측 점수라도 임계값과 비용 가정을 바꾸면 어떤 결정이 더 낫다는 결론이 달라지는 흐름을 확인하면 됩니다.

## 이 코드에서 먼저 봐야 할 점

첫 번째 코드는 95% 정확도가 얼마나 쉽게 만들어지는지 보여 줍니다. 하지만 두 번째 코드로 재현율을 보면 실제 양성을 하나도 잡지 못했다는 사실이 드러납니다. 세 번째 코드의 혼동 행렬은 이 문제를 더 노골적으로 보여 줍니다.

네 번째 코드는 임계값이 고정 상수가 아니라는 점을 보여 줍니다. 같은 점수 분포라도 기준선을 어디에 두느냐에 따라 결과가 달라집니다. 다섯 번째 코드는 결국 비즈니스가 원하는 것은 점수 자체가 아니라 총비용이 낮은 결정이라는 사실을 상기시킵니다.

## 자주 헷갈리는 지점

첫째, 지표를 곧 가치라고 오해하기 쉽습니다. 하지만 지표는 가치의 대리 변수일 뿐입니다. 둘째, 테스트 점수를 자주 확인할수록 더 객관적이라고 느끼기 쉽지만, 실제로는 테스트 세트를 튜닝에 끌어들이는 길이 됩니다.

셋째, 임계값 0.5를 기본값으로 두면 공정하다고 생각하기 쉽습니다. 그러나 임계값은 비용 구조와 운영 목표가 정해야 합니다. 넷째, 드리프트를 무시하면 오늘의 좋은 평가가 내일의 낡은 평가가 됩니다.

## 실무에서는 이렇게 생각한다

강한 팀은 지표를 보기 전에 먼저 묻습니다. 어떤 오류가 더 비싼가, 모델이 실제로 돕는 결정은 무엇인가, 데이터 분포는 배포 환경과 얼마나 비슷한가. 그런 다음 지표와 임계값을 정합니다. 순서가 바뀌면 숫자는 예뻐 보여도 의사결정은 약해집니다.

또한 평가는 한 번 끝나는 보고서가 아니라 계속 유지되는 코드에 가깝게 다룹니다. 어떤 데이터로 계산했는지, 어떤 임계값을 썼는지, 어떤 비용 가정을 뒀는지 남기지 않으면 다음 실험부터 비교가 불가능해집니다.

## 점검 목록

- [ ] 정확도 외에 최소 두 개 이상의 지표를 함께 봅니다.
- [ ] 혼동 행렬을 항상 확인합니다.
- [ ] 비즈니스 비용을 문서로 남깁니다.
- [ ] 임계값 선택 이유를 설명할 수 있습니다.

## 정리

모델 평가가 어려운 이유는 숫자가 많아서가 아닙니다. 하나의 숫자로 줄일 수 없는 현실을 상대하기 때문입니다. 데이터 분포, 오류 비용, 임계값, 드리프트를 함께 봐야 비로소 평가가 모델 선택의 언어가 됩니다. 다음 글에서는 이 언어의 출발점인 train, validation, test 세트의 역할을 정리하겠습니다.


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

- **왜 정확도 하나만으로 모델을 판단하면 위험할까요?**
  - 본문의 기준은 모델 평가는 왜 어려운가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **데이터 분포와 베이스레이트는 평가를 어떻게 왜곡할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **임계값이 바뀌면 같은 모델의 점수는 왜 달라질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **모델 평가는 왜 어려운가? (현재 글)**
- 훈련·검증·테스트 데이터 나누기 (예정)
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

- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Wikipedia — Confusion matrix](https://en.wikipedia.org/wiki/Confusion_matrix)
- [Pattern Recognition and Machine Learning — Bishop](https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, Metrics, MachineLearning, Foundations, Beginner

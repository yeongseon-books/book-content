---
series: model-evaluation-101
episode: 8
title: "Model Evaluation 101 (8/10): 교차 검증 이해하기"
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
  - CrossValidation
  - KFold
  - Stratified
  - scikit-learn
seo_description: 데이터 변동성에 따른 성능 변화를 측정하는 교차 검증 기법을 배우고, K-폴드 분할로 모델의 안정성과 신뢰도를 높입니다.
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (8/10): 교차 검증 이해하기

train/test를 한 번 나눠 점수 하나를 얻으면 평가가 끝난 것처럼 느껴질 수 있습니다. 작은 실습에서는 그 방식도 충분합니다. 그러나 모델 비교나 하이퍼파라미터 조정이 시작되면, 단 한 번의 분할에서 나온 숫자는 생각보다 시끄럽습니다. 데이터가 조금만 달라져도 순위가 뒤집히기 때문입니다.

그래서 교차 검증은 점수를 더 많이 만드는 기술이 아니라, 그 점수를 얼마나 믿어도 되는지 추정하는 기술에 가깝습니다. 평균은 물론이고 분산까지 함께 봐야 비교가 비로소 해석 가능해집니다.

이 글은 Model Evaluation 101 시리즈의 8번째 글입니다.

## 먼저 던지는 질문

- 테스트 세트 점수 하나만으로 모델을 고르면 왜 불안정할까요?
- K-Fold는 어떤 아이디어 위에서 동작할까요?
- 왜 분류 문제에서는 stratified가 기본 선택이 될까요?

## 큰 그림

![Model Evaluation 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/08/08-01-concept-at-a-glance.ko.png)

*Model Evaluation 101 8장 흐름 개요*

## 왜 이 글이 중요한가

모델 A가 0.842, 모델 B가 0.846이라면 얼핏 B가 더 좋아 보입니다. 하지만 분할이 달라질 때 점수가 0.02씩 흔들린다면 이 차이는 거의 의미가 없습니다. 교차 검증은 바로 이런 해석 문제를 줄여 줍니다.

또한 교차 검증은 누수 검출에도 도움을 줍니다. 그룹이 섞였거나 시간 순서를 깨뜨렸을 때 점수가 비정상적으로 좋아지는 경우가 많기 때문입니다. 그래서 평균 점수만이 아니라 올바른 분할 전략을 선택하는 일이 함께 중요합니다.

## 한눈에 보는 멘탈 모델

교차 검증에서는 하나의 검증 점수 대신 여러 분할에서 얻은 점수 묶음을 봅니다. 이 묶음이 있어야 평균뿐 아니라 흔들림도 읽을 수 있습니다.

## 핵심 용어

- **K-Fold**: 데이터를 k개로 나누고 k번 학습과 검증을 반복하는 방식입니다.
- **Stratified**: 각 폴드의 클래스 비율을 원본과 비슷하게 맞추는 방식입니다.
- **GroupKFold**: 같은 그룹이 서로 다른 폴드에 새지 않도록 막는 방식입니다.
- **TimeSeriesSplit**: 과거로 학습하고 미래로 검증하는 시간 순서 기반 분할입니다.
- **Repeated K-Fold**: 여러 시드로 K-Fold를 반복해 우연성을 줄이는 방식입니다.

## 교차 검증을 읽는 방식의 전환

좋지 않은 습관은 평균만 보고 표준편차를 숨기는 것입니다. 평균이 좋아 보여도 흔들림이 크면 모델 비교는 약합니다. 반대로 평균은 조금 낮아도 분산이 작고 누수 위험이 적은 평가가 더 믿을 만할 수 있습니다.

좋은 습관은 항상 두 가지를 함께 묻는 것입니다. 첫째, 이 분할 방식이 데이터의 구조를 제대로 보존하는가. 둘째, 점수의 평균과 분산이 비교 가능한 수준인가. 이 두 질문이 교차 검증의 핵심입니다.

## 교차 검증을 보는 다섯 단계

### 1단계 — 데이터와 모델

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
X, y = make_classification(n_samples=2000, weights=[0.7, 0.3], random_state=0)
m = LogisticRegression(max_iter=1000)
```

### 2단계 — Stratified K-Fold

```python
from sklearn.model_selection import cross_val_score, StratifiedKFold
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
scores = cross_val_score(m, X, y, cv=cv, scoring="f1_macro")
print("mean:", scores.mean(), "std:", scores.std())
```

### 3단계 — GroupKFold

```python
import numpy as np
from sklearn.model_selection import GroupKFold
groups = np.repeat(np.arange(100), 20)
gkf = GroupKFold(n_splits=5)
scores = cross_val_score(m, X, y, cv=gkf, groups=groups, scoring="f1_macro")
print("group cv:", scores.mean(), scores.std())
```

### 4단계 — TimeSeriesSplit

```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
scores = cross_val_score(m, X, y, cv=tscv, scoring="f1_macro")
print("time cv:", scores.mean(), scores.std())
```

### 5단계 — 여러 지표 함께 보기

```python
from sklearn.model_selection import cross_validate
out = cross_validate(m, X, y, cv=cv, scoring=["f1_macro", "roc_auc"])
print({k: v.mean() for k, v in out.items() if k.startswith("test_")})
```

**예상 결과:** 단일 점수 대신 평균과 표준편차가 함께 나오면서 비교의 흔들림을 읽을 수 있어야 합니다. 또 그룹 기반 분할이나 시간 기반 분할이 왜 일반 K-Fold보다 더 보수적이고 믿을 만한 결과를 주는지도 확인하면 좋습니다.

## 이 코드에서 먼저 봐야 할 점

두 번째 단계는 분류 문제에서 왜 stratified가 기본값에 가까운지 보여 줍니다. 클래스 비율을 각 폴드에 비슷하게 유지해야 평균 점수도 더 안정적으로 읽을 수 있습니다. 세 번째와 네 번째 단계는 교차 검증에서도 여전히 누수가 가장 큰 적이라는 점을 드러냅니다.

다섯 번째 단계는 교차 검증이 지표 하나만을 위한 도구가 아니라는 점을 보여 줍니다. 같은 분할 전략 안에서 여러 지표를 함께 읽어야 평가가 더 입체적이 됩니다.

## 자주 헷갈리는 지점

첫째, 일반 K-Fold를 모든 데이터에 그대로 적용해도 된다고 생각하기 쉽습니다. 하지만 시계열과 그룹 데이터에는 곧바로 누수가 들어옵니다. 둘째, 평균만 보고 표준편차를 무시하면 작은 차이를 과대해석하기 쉽습니다.

셋째, 교차 검증 점수가 많아 보인다고 해서 테스트 세트가 필요 없다고 오해하기도 합니다. 그러나 최종 보고를 위한 별도의 홀드아웃 세트는 여전히 중요합니다. 넷째, 매우 느린 모델에 무조건 큰 k를 쓰면 실험 속도가 지나치게 떨어질 수 있습니다.

## 실무에서는 이렇게 생각한다

시니어 엔지니어는 교차 검증을 평균 점수 생산기가 아니라 불확실성 측정기로 봅니다. 점수 차이가 작을수록 분산과 누수 여부를 더 꼼꼼히 봅니다. 안정적인 비교가 안 되면 모델 선택도 보류합니다.

또한 튜닝용 교차 검증과 최종 평가를 분리합니다. 내부 선택에는 교차 검증을 쓰고, 최종 보고에는 별도 테스트 세트를 남겨 둡니다. 이 선을 넘지 않아야 결과가 오래 버팁니다.

## 점검 목록

- [ ] 데이터 성격에 맞는 교차 검증 방식을 선택합니다.
- [ ] 평균과 표준편차를 함께 보고합니다.
- [ ] 그룹 누수와 시간 누수를 먼저 점검합니다.
- [ ] 최종 홀드아웃 세트를 별도로 유지합니다.

## 정리

교차 검증은 모델 점수의 평균을 보기 위한 도구이면서, 동시에 그 평균이 얼마나 흔들리는지 보여 주는 도구입니다. 올바른 분할 전략과 분산 해석이 함께 있어야 비교가 의미를 가집니다. 다음 글에서는 평균 점수 뒤에 숨은 실패 패턴을 꺼내는 오류 분석으로 넘어가겠습니다.


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

- **테스트 세트 점수 하나만으로 모델을 고르면 왜 불안정할까요?**
  - 본문의 기준은 교차 검증 이해하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **K-Fold는 어떤 아이디어 위에서 동작할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **왜 분류 문제에서는 stratified가 기본 선택이 될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): 정밀도와 재현율](./04-precision-and-recall.md)
- [Model Evaluation 101 (5/10): F1 점수](./05-f1-score.md)
- [Model Evaluation 101 (6/10): ROC와 AUC 이해하기](./06-roc-and-auc.md)
- [Model Evaluation 101 (7/10): 확률 보정 이해하기](./07-calibration.md)
- **교차 검증 이해하기 (현재 글)**
- 오류 분석으로 약점 찾기 (예정)
- 평가 리포트 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn — StratifiedKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html)
- [scikit-learn — TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [Wikipedia — Cross-validation](https://en.wikipedia.org/wiki/Cross-validation_(statistics))

Tags: ModelEvaluation, CrossValidation, KFold, Stratified, scikit-learn

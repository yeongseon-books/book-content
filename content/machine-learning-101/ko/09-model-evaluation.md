---
series: machine-learning-101
episode: 9
title: "Machine Learning 101 (9/10): Model Evaluation"
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
  - Evaluation
  - Metrics
  - ROC
  - scikit-learn
seo_description: 분류와 회귀 지표 선택, 혼동 행렬, ROC·PR 곡선의 읽는 법을 함께 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (9/10): Model Evaluation

누군가 "어떤 모델이 더 좋나요?"라고 묻는데 "어떤 지표 기준으로요?"라고 되묻지 않는다면 이미 곤란한 상황입니다. 머신러닝에서 평가는 숫자 하나를 출력하는 절차가 아니라, 무엇을 좋은 모델로 볼지 먼저 정의하는 과정입니다. 비즈니스 비용과 지표가 어긋나는 순간, 종이 위에서는 좋아 보이는 모델이 실제로는 나쁜 선택이 될 수 있습니다.

이 글은 머신러닝 101 시리즈의 9번째 글입니다. 여기서는 분류와 회귀 지표를 함께 정리하고, 혼동 행렬, ROC-AUC, PR-AUC, MAE, RMSE, R-squared를 언제 어떻게 읽어야 하는지 봅니다.

![Machine Learning 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/09/09-01-diagram.ko.png)
*Machine Learning 101 9장 흐름 개요*
> 올바른 지표는 어떤 오류가 가장 비싼지에 따라 정해지고, 불균형 데이터에서는 정확도가 거짓말을 하기 때문에 정밀도·재현율·ROC가 각자 다른 운영 질문에 답합니다.

## 이 글에서 다룰 문제

- 분류에서는 어떤 지표를 언제 써야 하고, 정확도만으로는 왜 부족할까요?
- 회귀에서는 MAE, MSE, RMSE, R-squared를 어떤 기준으로 골라야 할까요?
- 혼동 행렬은 어떤 구조를 보여 주고, 어떻게 읽어야 할까요?
- 클래스 불균형이 심할 때 평가 지표 선택은 어떻게 달라질까요?
- F1 점수와 AUC-ROC는 각각 어떤 질문에 답할까요?

지표가 틀리면 의사결정도 틀립니다. 비즈니스 비용과 지표가 어긋나는 순간, 모델은 서류상으로만 좋아 보이게 됩니다.

- **TP / FP / FN / TN**: 혼동 행렬의 네 칸입니다.
- **Accuracy**: 전체 예측 중 맞은 비율입니다.
- **Precision**: 양성이라고 예측한 것 중 실제 양성의 비율입니다.
- **Recall**: 실제 양성 중 모델이 잡아낸 비율입니다.
- **AUC**: 임계값 전반에서의 평균 성능입니다.

## 적용 전과 후
**Before**: 보고서에 정확도 숫자 하나만 적습니다.

**After**: 지표 표, 혼동 행렬, 그리고 PR 또는 ROC 곡선을 함께 봅니다.

## 실습: 5단계로 보는 평가

### 단계 1 — 데이터

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
```

### 단계 2 — 모델

```python
from sklearn.linear_model import LogisticRegression
m = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
prob = m.predict_proba(Xte)[:, 1]
pred = (prob >= 0.5).astype(int)
```

### 단계 3 — 혼동 행렬

```python
from sklearn.metrics import confusion_matrix
print(confusion_matrix(yte, pred))
```

### 단계 4 — 분류 지표

```python
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score
print(classification_report(yte, pred))
print("ROC-AUC:", roc_auc_score(yte, prob))
print("PR-AUC :", average_precision_score(yte, prob))
```

### 단계 5 — 회귀 지표

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
yt, yp = np.array([3.0, 5.0, 2.5]), np.array([2.8, 5.4, 2.1])
print("MAE:", mean_absolute_error(yt, yp))
print("RMSE:", mean_squared_error(yt, yp) ** 0.5)
print("R^2:", r2_score(yt, yp))
```

**예상 출력:** 혼동 행렬은 오류 구성을 그대로 보여 주고, ROC-AUC와 PR-AUC는 임계값 전반의 순위 품질을 요약합니다. 회귀 장난감 예제에서는 MAE와 RMSE가 비슷하게 보이지만, 큰 오차가 섞이면 RMSE가 더 민감하게 움직입니다.

- AUC는 특정 임계값 하나에 묶이지 않습니다.
- PR-AUC는 불균형 데이터에서 더 유용한 경우가 많습니다.
- RMSE와 MAE는 이상치 민감도가 다릅니다.

## 분류 지표 선택 가이드

어떤 지표를 써야 할지 혼란스러울 때 사용할 수 있는 판단 기준입니다.

| 상황 | 추천 지표 | 이유 |
|---|---|---|
| 클래스 균형, 단순 성능 비교 | Accuracy | 해석이 쉽고 직관적 |
| 양성을 놓치면 치명적 (예: 암 진단) | Recall (재현율) | 거짓 음성 최소화 |
| 오탐이 비용이 큰 경우 (예: 스팸) | Precision (정밀도) | 거짓 양성 최소화 |
| 불균형 데이터, 전반적 균형 | F1 Score | Precision과 Recall의 조화평균 |
| 임계값 무관 순위 성능 | ROC-AUC | 전체 임계값 범위를 요약 |
| 심한 불균형, 양성이 희귀 | PR-AUC | 희귀 양성 탐지 성능에 집중 |

## 혼동 행렬 읽는 법

혼동 행렬의 네 칸이 실제로 무엇을 뜻하는지 코드로 확인합니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)
m = LogisticRegression(max_iter=1000).fit(Xtr_s, ytr)
pred = m.predict(Xte_s)

cm = confusion_matrix(yte, pred)
tn, fp, fn, tp = cm.ravel()
print(f"TN={tn}  FP={fp}")
print(f"FN={fn}  TP={tp}")
print(f"Precision = TP/(TP+FP) = {tp/(tp+fp):.4f}")
print(f"Recall    = TP/(TP+FN) = {tp/(tp+fn):.4f}")
print(f"Accuracy  = (TP+TN)/total = {(tp+tn)/(tp+tn+fp+fn):.4f}")
```

- **TN (진짜 음성)**: 음성이라 예측했고 실제로도 음성
- **FP (거짓 양성)**: 양성이라 예측했지만 실제는 음성 (1종 오류)
- **FN (거짓 음성)**: 음성이라 예측했지만 실제는 양성 (2종 오류)
- **TP (진짜 양성)**: 양성이라 예측했고 실제로도 양성

## 회귀 지표 비교

```python
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 이상치가 있는 경우
y_true = np.array([3.0, 5.0, 2.5, 7.0, 4.0])
y_pred = np.array([2.8, 5.4, 2.1, 7.2, 3.9])
y_pred_outlier = np.array([2.8, 5.4, 2.1, 15.0, 3.9])  # 이상치 하나

for label, yp in [("정상 예측", y_pred), ("이상치 포함", y_pred_outlier)]:
    mae = mean_absolute_error(y_true, yp)
    rmse = mean_squared_error(y_true, yp) ** 0.5
    r2 = r2_score(y_true, yp)
    print(f"{label}: MAE={mae:.3f}, RMSE={rmse:.3f}, R²={r2:.3f}")
```

RMSE는 이상치에 매우 민감합니다. 이상치를 크게 페널티 주고 싶다면 RMSE를, 이상치 영향을 줄이려면 MAE를 씁니다. R²는 설명력 비율이므로 모델 품질을 요약할 때 씁니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 어떤 지표를 써야 할지 합의가 안 되면, 모델 이야기를 잠시 멈추고 **거짓 양성**과 **거짓 음성**의 비용부터 정리해야 합니다.
- 클래스 불균형이 심한데 ROC-AUC만 보고 있으면, PR 곡선과 임계값 민감도를 같이 봐야 합니다.
- 한 지표는 좋은데 다른 지표가 나쁘다면 모순이 아니라, **어떤 실패를 더 싫어하는지** 다시 분명히 하라는 신호입니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| 불균형 데이터에서 Accuracy만 보고 | 소수 클래스 성능 숨겨짐 | F1, Recall, PR-AUC 추가 |
| ROC-AUC만 믿는 불균형 상황 | 희귀 양성 탐지 과대평가 | PR-AUC 병행 |
| F1 최적화하면서 임계값 무시 | 비즈니스 비용 반영 안 됨 | PR 곡선에서 임계값 선택 |
| 회귀에서 MAE 또는 RMSE만 보고 | 이상치 민감도 놓침 | 둘 다 보고 차이 해석 |
| 같은 테스트 세트 반복 평가 | 지표 누수 | 테스트는 최종에 딱 한 번 |

## 실무에서는 이렇게 나타납니다

A/B 테스트, 모델 게이트, MLOps 모니터링은 모두 지표 정의 위에서 돌아갑니다. 지표는 조직이 합의하는 언어입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 순서는 **비즈니스 비용 → 지표 → 임계값**입니다.
- 불균형에서는 PR 곡선이 진실에 더 가깝습니다.
- 양성을 놓치면 큰일 나는 문제에서는 재현율을 극대화합니다.
- 보정(calibration)도 평가의 일부입니다.
- 지표 하나로 끝내는 일은 드뭅니다.

## 운영 체크리스트

- [ ] 항상 혼동 행렬을 출력합니다.
- [ ] ROC와 PR을 함께 봅니다.
- [ ] 회귀에서는 MAE와 RMSE를 함께 보고합니다.
- [ ] 테스트 세트는 마지막에 한 번만 봅니다.

## 불균형 데이터 평가의 함정 직접 확인하기

불균형 데이터에서 Accuracy가 얼마나 오해를 부르는지 실험합니다.

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score,
    average_precision_score, classification_report
)

# 95:5 불균형 데이터
X, y = make_classification(
    n_samples=2000, n_features=10,
    weights=[0.95, 0.05], random_state=42
)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# 항상 다수 클래스를 예측하는 더미 분류기
dummy = DummyClassifier(strategy="most_frequent").fit(Xtr, ytr)
dummy_pred = dummy.predict(Xte)
print("=== 더미 분류기 (항상 음성 예측) ===")
print(f"Accuracy: {accuracy_score(yte, dummy_pred):.4f}  ← 높아 보이지만 의미 없음")
print(f"F1      : {f1_score(yte, dummy_pred, zero_division=0):.4f}")

# 실제 로지스틱 회귀
m = LogisticRegression(class_weight="balanced", max_iter=1000).fit(Xtr, ytr)
pred = m.predict(Xte)
prob = m.predict_proba(Xte)[:, 1]
print("\n=== 로지스틱 회귀 (class_weight=balanced) ===")
print(f"Accuracy: {accuracy_score(yte, pred):.4f}")
print(f"F1      : {f1_score(yte, pred):.4f}")
print(f"ROC-AUC : {roc_auc_score(yte, prob):.4f}")
print(f"PR-AUC  : {average_precision_score(yte, prob):.4f}")
print(classification_report(yte, pred, target_names=["음성", "양성"]))
```

더미 분류기가 95% 정확도를 보이지만 F1은 0입니다. Accuracy 하나만 보면 더미 모델과 실제 모델을 구분하지 못합니다.

## 회귀 지표 선택 시나리오별 가이드

```python
import numpy as np
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error,
    r2_score, mean_absolute_percentage_error
)

# 이상치 하나가 있는 예측값
y_true = np.array([10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0])
y_pred_good = np.array([10.5, 20.3, 29.8, 40.2, 50.1, 59.9, 70.2, 79.8])
y_pred_outlier = np.array([10.5, 20.3, 29.8, 40.2, 50.1, 59.9, 70.2, 120.0])  # 마지막 값 이상치

print(f"{'지표':>6} {'좋은 예측':>12} {'이상치 포함':>12} {'차이':>10}")
for label, fn in [("MAE", mean_absolute_error),
                   ("RMSE", lambda a, b: mean_squared_error(a, b)**0.5),
                   ("R²", r2_score)]:
    good = fn(y_true, y_pred_good)
    out = fn(y_true, y_pred_outlier)
    print(f"{label:>6} {good:>12.4f} {out:>12.4f} {out-good:>10.4f}")

print("\n결론: RMSE는 이상치에 매우 민감, MAE는 더 강건합니다.")
print("이상치를 강하게 페널티 주려면 RMSE, 강건하게 보려면 MAE를 씁니다.")
```

이상치 하나가 RMSE를 크게 올리지만 MAE는 상대적으로 영향이 적습니다. 도메인에서 큰 오차가 특히 문제가 되는 경우에는 RMSE를 선택하고, 이상치 영향을 줄이려면 MAE를 씁니다.

## 연습 문제

1. 불균형 데이터에서 Accuracy와 F1을 비교해 보세요.
2. ROC 곡선과 PR 곡선을 나란히 그려 보세요.
3. MAE와 RMSE가 크게 다르게 나오는 데이터셋을 만들어 보세요.
4. 혼동 행렬에서 FP와 FN의 비용이 2:1일 때 최적 임계값을 탐색해 보세요.
5. `classification_report`의 각 수치(precision, recall, f1-score, support)를 직접 계산해서 검증해 보세요.

## 정리

올바른 지표는 어떤 오류가 가장 비싼지에 따라 정해지고, 불균형 데이터에서는 정확도가 거짓말을 하기 때문에 정밀도·재현율·ROC가 각자 다른 운영 질문에 답합니다. 이 글에서는 적용 전과 후부터 시니어 엔지니어는 이렇게 생각합니다까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **분류에서는 어떤 지표를 언제 써야 할까요?**
  - 거짓 음성이 비싼 경우(암 진단, 사기 탐지)에는 Recall, 거짓 양성이 비싼 경우(스팸 필터)에는 Precision, 전반적 균형이 필요하면 F1, 임계값 무관 성능 비교에는 AUC를 씁니다.
- **회귀에서는 MAE, MSE, RMSE, R-squared를 어떻게 나눠 읽을까요?**
  - MAE는 이상치에 강하고, RMSE는 큰 오차에 민감합니다. R²는 설명력 비율이므로 모델 품질을 요약할 때 씁니다. 셋을 함께 보고합니다.
- **혼동 행렬은 어떤 구조를 보여 줄까요?**
  - TP, FP, FN, TN 네 칸으로 구성됩니다. 어떤 종류의 오류가 얼마나 발생했는지 구체적으로 보여 주므로, 정확도 하나보다 훨씬 많은 정보를 담습니다.

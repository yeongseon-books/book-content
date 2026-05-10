---
series: machine-learning-101
episode: 9
title: Model Evaluation
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - MachineLearning
  - Evaluation
  - Metrics
  - ROC
  - scikit-learn
seo_description: 분류·회귀 지표의 의미와 선택 기준, 혼동 행렬과 ROC·PR 곡선까지 scikit-learn 코드로 정리한 평가 가이드
last_reviewed: '2026-05-04'
---

# Model Evaluation

> Machine Learning 101 시리즈 (9/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *어떤 모델이 더 좋은가요* 라는 질문에 — *“어떤 지표로?”* 라고 *되묻지 않는다면* 이미 위험합니다.

> *Model Evaluation 은 *지표 선택* 이 *모델 선택* 보다 *먼저* 라는 사실을 *코드로 증명* 하는 단계입니다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *분류 지표*: Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC
- *회귀 지표*: MAE, MSE, RMSE, R^2
- *혼동 행렬* 의 *해부*
- *ROC* vs *PR* 의 *선택 기준*
- 흔한 함정 5가지

## 왜 중요한가

*잘못된 지표* 는 *잘못된 결정*. *비즈니스 비용* 과 *지표* 가 *어긋나면* 모델은 *겉으로만* 좋아 보입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Pred["predictions"] --> CM["confusion matrix"]
    CM --> P["precision"]
    CM --> R["recall"]
    CM --> F["F1"]
    Prob["probabilities"] --> ROC["ROC-AUC"]
    Prob --> PR["PR-AUC"]
```

## 핵심 용어 정리

- **TP/FP/FN/TN**: *혼동 행렬* 의 4분면.
- **Accuracy**: *맞춘 비율*.
- **Precision**: *예측 양성* 의 *진짜 비율*.
- **Recall**: *실제 양성* 의 *포착 비율*.
- **AUC**: *임계값 전체* 평균 성능.

## Before/After

**Before**: *“정확도” 한 줄 보고서*.

**After**: *지표 표 + 혼동 행렬 + PR/ROC 곡선*.

## 실습: 5단계 평가

### 1단계 — 데이터

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
```

### 2단계 — 모델

```python
from sklearn.linear_model import LogisticRegression
m = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
prob = m.predict_proba(Xte)[:, 1]
pred = (prob >= 0.5).astype(int)
```

### 3단계 — 혼동 행렬

```python
from sklearn.metrics import confusion_matrix
print(confusion_matrix(yte, pred))
```

### 4단계 — 분류 지표

```python
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score
print(classification_report(yte, pred))
print("ROC-AUC:", roc_auc_score(yte, prob))
print("PR-AUC :", average_precision_score(yte, prob))
```

### 5단계 — 회귀 지표

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
yt, yp = np.array([3.0, 5.0, 2.5]), np.array([2.8, 5.4, 2.1])
print("MAE:", mean_absolute_error(yt, yp))
print("RMSE:", mean_squared_error(yt, yp) ** 0.5)
print("R^2:", r2_score(yt, yp))
```

## 이 코드에서 주목할 점

- *AUC* 는 *임계값* 에 *독립*.
- *PR-AUC* 는 *불균형* 에서 *더 정확*.
- *RMSE* 와 *MAE* 의 *민감도* 가 다름.

## 자주 하는 실수 5가지

1. ***불균형* 데이터에 *Accuracy* 만 보기.**
2. ***ROC-AUC* 를 *불균형* 에서 *과신*.**
3. ***임계값* 무시하고 *F1* 만 보기.**
4. ***회귀* 에서 *RMSE/MAE* 중 *하나만* 보기.**
5. ***test* 에 *반복 평가* (=test 누수).**

## 실무에서는 이렇게 쓰입니다

A/B 테스트, 모델 게이트, MLOps 모니터링 — *지표 정의* 가 *조직 합의* 의 *언어*.

## 시니어 엔지니어는 이렇게 생각합니다

- *비즈니스 비용 → 지표 → 임계값* 순서.
- *PR 곡선* 이 *불균형의 진실*.
- *재현율* 이 *치명적 비용* 일 때 우선.
- *Calibration* 도 *평가* 의 일부.
- *지표 한 개* 로는 *부족*.

## 체크리스트

- [ ] *혼동 행렬* 을 *항상* 출력.
- [ ] *ROC* 와 *PR* 을 *함께* 본다.
- [ ] *회귀* 는 *MAE + RMSE* 를 *함께*.
- [ ] *test* 평가는 *최후의 한 번*.

## 연습 문제

1. *불균형* 데이터에서 *Accuracy* 와 *F1* 의 차이를 측정하세요.
2. *ROC* 와 *PR* 곡선을 *그려* 비교하세요.
3. *RMSE* 와 *MAE* 가 *크게 어긋나는* 데이터를 만드세요.

## 정리 및 다음 단계

평가가 *모델 선택* 의 *언어* 입니다. 다음 글에서는 *ML 프로젝트 전체 흐름* 으로 시리즈를 마무리합니다.

<!-- toc:begin -->
- [Machine Learning이란 무엇인가?](./01-what-is-machine-learning.md)
- [지도학습과 비지도학습](./02-supervised-and-unsupervised.md)
- [Train/Test Split](./03-train-test-split.md)
- [Linear Regression](./04-linear-regression.md)
- [Logistic Regression](./05-logistic-regression.md)
- [Decision Tree와 Random Forest](./06-decision-tree-and-random-forest.md)
- [Clustering](./07-clustering.md)
- [Overfitting과 Regularization](./08-overfitting-and-regularization.md)
- **Model Evaluation (현재 글)**
- ML 프로젝트 전체 흐름 (예정)
<!-- toc:end -->

## 참고 자료

- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [scikit-learn — ROC and PR curves](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html)
- [Google — Classification metrics](https://developers.google.com/machine-learning/crash-course/classification/precision-and-recall)
- [Wikipedia — Confusion matrix](https://en.wikipedia.org/wiki/Confusion_matrix)

Tags: MachineLearning, Evaluation, Metrics, ROC, scikit-learn

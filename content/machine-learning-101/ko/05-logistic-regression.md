---
series: machine-learning-101
episode: 5
title: Logistic Regression
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
  - LogisticRegression
  - Classification
  - scikit-learn
  - Beginner
seo_description: 로지스틱 회귀로 이진 분류를 풀고, 시그모이드와 임계값, 정밀도·재현율의 직관까지 코드와 함께 정리한 글
last_reviewed: '2026-05-04'
---

# Logistic Regression

> Machine Learning 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *0과 1을 예측* 하는데 *왜 회귀* 라는 이름이 붙었을까요?

> *Logistic Regression 은 *연속 확률* 을 *예측* 하고, *임계값* 으로 *클래스* 를 결정하는 *분류기* 입니다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *시그모이드* 와 *확률 출력*
- *임계값 0.5* 의 *함정*
- *정밀도/재현율/F1* 의 의미
- *Multinomial* 확장
- 흔한 함정 5가지

## 왜 중요한가

*분류 베이스라인* 의 표준. *해석 가능* 하고 *빠르며*, *불균형 데이터* 에서도 *임계값 조정* 으로 강력.

## 개념 한눈에 보기

```mermaid
flowchart LR
    X["X"] --> Lin["z = X w + b"]
    Lin --> Sig["sigmoid(z)"]
    Sig --> P["P(y=1|X)"]
    P --> Cls["class = P > 0.5"]
```

## 핵심 용어 정리

- **시그모이드**: *실수 → (0, 1)*.
- **확률**: *클래스 1 의 가능성*.
- **임계값**: *확률 → 클래스* 변환.
- **정밀도**: *예측한 1* 중 *진짜 1*.
- **재현율**: *진짜 1* 중 *예측한 1*.

## Before/After

**Before**: *“정확도 95%”* — *불균형* 일 때 *무의미*.

**After**: *정밀도/재현율/F1/AUC* 를 *함께* 본다.

## 실습: 5단계 분류

### 1단계 — 데이터

```python
from sklearn.datasets import load_breast_cancer
X, y = load_breast_cancer(return_X_y=True)
```

### 2단계 — 분할 + 스케일

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
```

### 3단계 — 학습

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
```

### 4단계 — 평가

```python
from sklearn.metrics import classification_report
print(classification_report(yte, model.predict(Xte)))
```

### 5단계 — 임계값 조정

```python
import numpy as np
prob = model.predict_proba(Xte)[:, 1]
for t in [0.3, 0.5, 0.7]:
    pred = (prob >= t).astype(int)
    print(t, (pred == yte).mean())
```

## 이 코드에서 주목할 점

- *predict_proba* 는 *확률* 을 반환.
- *임계값* 이 *정밀도/재현율* 의 *트레이드오프*.
- *StandardScaler* 가 *수렴* 을 돕는다.

## 자주 하는 실수 5가지

1. ***확률 보정* 없이 *확률 그대로* 사용.**
2. ***임계값* 을 *항상 0.5* 로 두기.**
3. ***불균형 데이터* 에 *정확도* 만 보기.**
4. ***스케일링* 누락.**
5. ***다중 클래스* 에 *기본 설정* 그대로 사용 (multinomial 명시).**

## 실무에서는 이렇게 쓰입니다

스팸/사기/이탈 — *확률* 이 필요한 *모든 의사결정 시스템*.

## 시니어 엔지니어는 이렇게 생각합니다

- *비즈니스 비용* 이 *임계값* 을 결정.
- *PR 곡선* 을 *항상* 그린다.
- *클래스 가중치* 로 *불균형* 보정.
- *해석 가능성* 을 무기로 활용.
- *Calibration* 을 *반드시* 검증.

## 체크리스트

- [ ] *predict_proba* 를 사용한다.
- [ ] *정밀도/재현율* 을 *함께* 본다.
- [ ] *임계값* 을 *비용* 으로 정한다.
- [ ] *스케일링* 을 *항상* 적용.

## 연습 문제

1. *임계값* 을 0.1~0.9 로 *바꿔* PR 변화를 그리세요.
2. *class_weight="balanced"* 의 효과를 비교하세요.
3. *멀티클래스* 데이터에 *multinomial* 을 적용하세요.

## 정리 및 다음 단계

Logistic Regression 은 *분류의 기본기* 입니다. 다음 글에서는 *Decision Tree와 Random Forest* 로 *비선형 모델* 을 다룹니다.

<!-- toc:begin -->
- [Machine Learning이란 무엇인가?](./01-what-is-machine-learning.md)
- [지도학습과 비지도학습](./02-supervised-and-unsupervised.md)
- [Train/Test Split](./03-train-test-split.md)
- [Linear Regression](./04-linear-regression.md)
- **Logistic Regression (현재 글)**
- Decision Tree와 Random Forest (예정)
- Clustering (예정)
- Overfitting과 Regularization (예정)
- Model Evaluation (예정)
- ML 프로젝트 전체 흐름 (예정)
<!-- toc:end -->

## 참고 자료

- [scikit-learn — Logistic Regression](https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression)
- [scikit-learn — Classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics)
- [Google — Classification thresholds](https://developers.google.com/machine-learning/crash-course/classification/thresholding)
- [StatQuest — Logistic Regression](https://www.youtube.com/watch?v=yIYKR4sgzI8)

Tags: MachineLearning, LogisticRegression, Classification, scikit-learn, Beginner

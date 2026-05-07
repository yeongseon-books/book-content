---
series: model-evaluation-101
episode: 2
title: train/validation/test
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - ModelEvaluation
  - TrainValTest
  - DataLeakage
  - CrossValidation
  - scikit-learn
seo_description: train/validation/test의 역할 분리, 데이터 누수와 누설 방지, 시계열 분할까지 코드와 함께 정리한 글
last_reviewed: '2026-05-04'
---

# train/validation/test

> Model Evaluation 101 시리즈 (2/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *valid* 와 *test* 는 *왜 따로 둬야 할까요*?

> *train 은 학습, validation 은 *튜닝*, test 는 *최종 한 번* — 세 역할의 *분리* 가 *모든 평가* 의 출발점입니다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *세 데이터셋 의 역할*
- *데이터 누수 (leakage)* 의 종류
- *시계열 분할* 의 원칙
- *그룹 분할* (group leakage 방지)
- 흔한 함정 5가지

## 왜 중요한가

*잘못된 분할* = *측정 무효*. *모든 모델 비교* 가 *오해* 가 됩니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    All["all data"] --> Tr["train (fit)"]
    All --> Va["valid (tune)"]
    All --> Te["test (final)"]
```

## 핵심 용어 정리

- **train**: *모델 학습*.
- **validation**: *하이퍼파라미터 / 모델 선택*.
- **test**: *마지막 한 번* 의 진실.
- **leakage**: *답이 새는* 모든 경로.
- **group split**: *동일 객체* 가 *두 분할* 에 들어가지 않도록.

## Before/After

**Before**: *“전체에 fit, 일부 score”*.

**After**: *세 분할* + *분할 후 전처리*.

## 실습: 5단계 분할 패턴

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
sc_bad = StandardScaler().fit(X)  # leak: full data
sc_ok = StandardScaler().fit(Xtr)  # correct
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

## 이 코드에서 주목할 점

- *전체에 fit* 하면 *통계 누수*.
- *시계열* 은 *시간 순서* 유지.
- *그룹* 은 *동일 ID* 분리.

## 자주 하는 실수 5가지

1. ***test 로 튜닝*.**
2. ***시계열 무작위 분할*.**
3. ***그룹 누수* 방치.**
4. ***스케일러* 를 *전체* 에 fit.**
5. ***valid 없이* *test 로* *반복 비교*.**

## 실무에서는 이렇게 쓰입니다

추천(시간 기반), 의료(환자 그룹), 금융(고객 그룹) — *분할 전략* 이 *실서비스 성능* 의 80%.

## 시니어 엔지니어는 이렇게 생각합니다

- *분할 전* 에 *EDA* 만, *fit 은 분할 후*.
- *시계열* 은 *Walk-forward*.
- *그룹/시간 누수* 를 *항상* 의심.
- *test* 의 *희소성* 을 보호.
- *valid* 와 *test* 의 *역할* 을 *문서화*.

## 체크리스트

- [ ] *세 분할* 을 사용한다.
- [ ] *전처리* 는 *분할 후* fit.
- [ ] *시계열* 은 *시간 분할*.
- [ ] *그룹* 을 *명시*.

## 연습 문제

1. *전체 fit* vs *분할 후 fit* 의 *test 점수* 차이를 측정하세요.
2. *TimeSeriesSplit* 으로 *5-fold* 를 출력하세요.
3. *GroupKFold* 로 *그룹 누수 없는* 분할을 만드세요.

## 정리 및 다음 단계

분할 전략은 *모든 측정의 전제* 입니다. 다음 글에서는 *Accuracy 의 한계* 를 다룹니다.

<!-- toc:begin -->
- [모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- **train/validation/test (현재 글)**
- Accuracy의 한계 (예정)
- Precision과 Recall (예정)
- F1 Score (예정)
- ROC와 AUC (예정)
- Calibration (예정)
- Cross Validation (예정)
- Error Analysis (예정)
- 평가 리포트 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [scikit-learn — Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn — TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [Forecasting: Principles and Practice — Hyndman](https://otexts.com/fpp3/)
- [Google — Data leakage](https://developers.google.com/machine-learning/guides/rules-of-ml)

Tags: ModelEvaluation, TrainValTest, DataLeakage, CrossValidation, scikit-learn

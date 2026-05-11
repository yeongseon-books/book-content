---
series: data-science-101
episode: 7
title: 모델링
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataScience
  - Modeling
  - ScikitLearn
  - MachineLearning
  - Beginner
seo_description: 베이스라인부터 분류 모델까지, scikit-learn 으로 안전하게 첫 모델을 만드는 5단계 모델링 입문
last_reviewed: '2026-05-04'
---

# 모델링

> Data Science 101 시리즈 (7/10)


## 이 글에서 다룰 문제

복잡한 모델보다 *제대로 된 베이스라인* 이 *진짜 출발선* 입니다. *비교 기준* 이 *없으면* 모델의 *가치* 를 *증명할 수 없습니다*.

> *모든 모델은 *기준선* 과 *겨룬다*.*

## 전체 흐름
```mermaid
flowchart LR
    Data["Cleaned Data"] --> Split["Train / Test Split"]
    Split --> Base["Baseline"]
    Split --> Model["Model"]
    Base --> Compare["Compare"]
    Model --> Compare
```

## Before/After

**Before**: 복잡한 모델을 만들고 *95%* 정확도. 베이스라인이 *96%*. *개선이 아닌 퇴행*.

**After**: 먼저 *베이스라인 96%* 를 *기록* 하고 *그 이상* 을 *목표*.

## 5단계 모델링

### 1단계 — 데이터 준비

```python
from sklearn.model_selection import train_test_split
import pandas as pd

df = pd.read_csv("churn.csv")
X = df.drop(columns=["churn"])
y = df["churn"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

### 2단계 — 베이스라인

```python
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score

base = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
print("baseline:", accuracy_score(y_test, base.predict(X_test)))
```

### 3단계 — 파이프라인

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

num = X.select_dtypes("number").columns.tolist()
cat = X.select_dtypes("object").columns.tolist()

pre = ColumnTransformer([
    ("num", StandardScaler(), num),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
])
model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])
```

### 4단계 — 학습/평가

```python
model.fit(X_train, y_train)
print("model:", accuracy_score(y_test, model.predict(X_test)))
```

### 5단계 — 교차 검증

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy")
print(scores.mean(), "+/-", scores.std())
```

## 이 코드에서 주목할 점

- *베이스라인* 을 *먼저* 기록.
- *Pipeline* 으로 *데이터 누수* 를 막는다.
- *Cross-validation* 으로 *분산* 을 본다.

## 자주 하는 실수 5가지

1. ***베이스라인 없이* 모델 시작.** *개선 여부* 를 *모른다*.
2. ***test set* 에 *전처리 통계* 학습.** *데이터 누수*.
3. ***accuracy* 만 본다.** 클래스 *불균형* 에 *속는다*.
4. ***random_state* 미설정.** *재현* 이 *어려움*.
5. ***CV 없이* 한 번의 결과로 결정.** *운* 을 *실력* 으로 착각.

## 실무에서는 이렇게 쓰입니다

데이터팀은 *MLflow / W&B* 로 *실험* 을 *기록* 합니다. *베이스라인* 은 *항상 첫 실험*. *피처 변경* 은 *한 번에 하나* 만.

## 체크리스트

- [ ] *Baseline* 을 만들 수 있다.
- [ ] *Pipeline* 의 의미를 안다.
- [ ] *Train/Test 분리* 의 *이유* 를 안다.
- [ ] *CV* 의 *분산* 을 본다.

## 정리 및 다음 단계

모델링은 *기준선과의 대화* 입니다. 다음 글에서는 모델을 *어떻게 평가* 할지 *지표* 의 세계로 들어갑니다.

<!-- toc:begin -->
- [Data Science란 무엇인가?](./01-what-is-data-science.md)
- [문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- [데이터 수집](./03-data-collection.md)
- [데이터 정제](./04-data-cleaning.md)
- [탐색적 데이터 분석](./05-exploratory-data-analysis.md)
- [시각화](./06-visualization.md)
- **모델링 (현재 글)**
- 평가 (예정)
- 결과 해석 (예정)
- 데이터 프로젝트 전체 흐름 (예정)
<!-- toc:end -->

## 참고 자료

- [scikit-learn — User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Google — Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Kaggle — Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning)
- [Hands-On ML with Scikit-Learn](https://github.com/ageron/handson-ml3)

Tags: DataScience, Modeling, ScikitLearn, MachineLearning, Beginner

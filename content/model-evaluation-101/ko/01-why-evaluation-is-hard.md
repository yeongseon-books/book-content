---
series: model-evaluation-101
episode: 1
title: 모델 평가는 왜 어려운가?
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
  - Metrics
  - MachineLearning
  - Foundations
  - Beginner
seo_description: 정확도 한 줄로 모델을 평가하면 안 되는 이유, 평가가 비즈니스 비용·데이터 분포·임계값과 얽혀 있는 이유를 정리한 글
last_reviewed: '2026-05-04'
---

# 모델 평가는 왜 어려운가?

> Model Evaluation 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *정확도 99%* 모델은 *정말 좋은 모델* 일까요?

> *모델 평가는 *지표 하나* 가 아니라, *데이터 분포 / 비용 구조 / 의사결정* 의 *교집합* 입니다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *평가가 어려운 4가지 이유*
- *지표 ≠ 비즈니스 가치*
- *분포 변화* 의 *위협*
- *임계값* 이 *결정* 을 좌우
- 흔한 함정 5가지

## 왜 중요한가

*평가* 가 *모델 선택* 의 *언어*. *언어가 잘못되면* *팀 전체* 가 *잘못된 방향* 으로 갑니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Data["data"] --> Pred["predictions"]
    Pred --> Metric["metric(s)"]
    Cost["business cost"] --> Metric
    Metric --> Decide["decision"]
```

## 핵심 용어 정리

- **지표**: *모델 성능* 의 *수치*.
- **베이스레이트**: *클래스 비율*.
- **임계값**: *확률 → 클래스* 변환점.
- **드리프트**: *시간에 따른 분포 변화*.
- **비용 행렬**: *오분류 비용* 의 차이.

## Before/After

**Before**: *“정확도” 한 줄* 로 모델을 결정.

**After**: *지표 + 혼동행렬 + 비용 + 드리프트* 를 *함께* 본다.

## 실습: 5단계 평가의 함정 체험

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

### 3단계 — 혼동행렬

```python
from sklearn.metrics import confusion_matrix
print(confusion_matrix(y, pred_dummy))
```

### 4단계 — 임계값에 따른 변화

```python
import numpy as np
prob = np.linspace(0, 1, 100)
yt = (prob > 0.5).astype(int)
for t in [0.3, 0.5, 0.7]:
    pred = (prob >= t).astype(int)
    print(t, (pred == yt).mean())
```

### 5단계 — 비용 가중

```python
def cost(tp, fp, fn, c_fp=1, c_fn=10):
    return c_fp * fp + c_fn * fn
print("cost:", cost(tp=5, fp=10, fn=2))
```

## 이 코드에서 주목할 점

- *95% 정확도* 가 *완전 무용지물* 일 수 있다.
- *임계값* 이 *지표* 를 흔든다.
- *비용 행렬* 이 *진짜 의사결정* 을 결정.

## 자주 하는 실수 5가지

1. ***단일 지표* 만 보고 *모델 선택*.**
2. ***베이스레이트* 무시.**
3. ***test* 를 *반복 평가*.**
4. ***임계값* 을 *0.5 고정*.**
5. ***비즈니스 비용* 을 *무시*.**

## 실무에서는 이렇게 쓰입니다

A/B 실험, MLOps 게이트, 컴플라이언스 — *평가 정의* 가 *조직 합의* 의 핵심.

## 시니어 엔지니어는 이렇게 생각합니다

- *비즈니스 비용 → 지표 → 임계값* 순서.
- *지표는 한 개로는 부족*.
- *test 는 *마지막 한 번*.
- *드리프트* 는 *항상 일어난다*.
- *평가* 도 *코드 리뷰* 의 대상.

## 체크리스트

- [ ] *정확도* 외 *최소 2개* 지표.
- [ ] *혼동행렬* 을 *항상* 본다.
- [ ] *비즈니스 비용* 을 *문서화*.
- [ ] *임계값* 을 *근거* 와 함께 결정.

## 연습 문제

1. *베이스레이트 1%* 데이터에서 *Accuracy 99%* 가 나오는 *덤프 모델* 을 만드세요.
2. *임계값* 을 0.1~0.9 로 바꿔 *정밀도/재현율* 을 비교하세요.
3. *비용 행렬* 을 정의하고 *총 비용* 을 *임계값* 으로 *최소화* 하세요.

## 정리 및 다음 단계

평가는 *모델 선택의 언어* 입니다. 다음 글에서는 *train/validation/test* 의 *역할 분리* 를 다룹니다.

<!-- toc:begin -->
- **모델 평가는 왜 어려운가? (현재 글)**
- train/validation/test (예정)
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

- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Wikipedia — Confusion matrix](https://en.wikipedia.org/wiki/Confusion_matrix)
- [Pattern Recognition and Machine Learning — Bishop](https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/)

Tags: ModelEvaluation, Metrics, MachineLearning, Foundations, Beginner

---
series: data-science-101
episode: 8
title: "Data Science 101 (8/10): 평가"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataScience
  - Evaluation
  - Metrics
  - ScikitLearn
  - Beginner
seo_description: 정확도의 한계와 정밀도, 재현율, F1, ROC AUC 등 분류 및 회귀 평가지표의 선택 기준과 비즈니스 비용 반영법을 정리합니다.
last_reviewed: '2026-05-15'
---

# Data Science 101 (8/10): 평가

이 글은 Data Science 101 시리즈의 여덟 번째 글입니다.

모델링이 끝나면 많은 입문자가 가장 먼저 정확도를 봅니다. 물론 정확도는 유용한 지표일 수 있습니다. 하지만 언제나 좋은 지표는 아닙니다. 특히 클래스 불균형이 큰 문제에서는 정확도가 매우 높아도 실제로 중요한 대상을 거의 잡지 못할 수 있습니다. 사기 탐지, 장애 탐지, 이탈 예측처럼 놓치는 비용이 큰 문제에서는 더 그렇습니다.

그래서 평가는 단순히 점수를 보는 단계가 아니라, 우리가 어떤 문제를 풀고 있는지 다시 확인하는 단계에 가깝습니다. 어떤 지표를 선택하느냐가 곧 어떤 실패를 더 크게 볼지 정하는 일이기 때문입니다.

## 먼저 던지는 질문

- 정확도가 높으면 정말 좋은 모델이라고 말할 수 있을까요?
- 분류 문제에서 precision, recall, F1, ROC AUC는 각각 무엇을 말해 줄까요?
- 회귀 문제에서 MAE, RMSE, R²는 어떻게 다를까요?

## 큰 그림

![Data Science 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/08/08-01-concept-at-a-glance.ko.png)

*Data Science 101 8장 흐름 개요*

평가를 운영 시스템 속에서 올바르게 배치하려면 어떤 경계에서 무엇을 입력받고, 어디에서 검증하며, 어떤 신호를 남겨야 하는지 먼저 봐야 합니다.

> 평가의 핵심은 기능 이름이 아니라, 입력을 받는 경계에서 결과를 내보내는 경계까지 어떤 기준으로 데이터를 검증하고 처리할 것인가를 명확히 정하는 데 있습니다.

## 이 글에서 배우는 내용

- accuracy가 쉽게 오해를 만드는 이유
- 분류 문제에서 precision, recall, F1, ROC AUC를 읽는 법
- 회귀 문제에서 MAE, RMSE, R²를 비교하는 법
- 5단계 평가 실습 흐름
- 평가 단계에서 흔한 함정 다섯 가지

## 왜 중요한가

지표가 문제와 어긋나면 모델은 잘못된 방향으로 최적화됩니다. 예를 들어 실제로는 놓치는 비용이 큰 문제인데 accuracy만 올리면, 팀은 좋은 모델이라고 믿지만 현업에서는 계속 불만이 나올 수 있습니다.

평가 지표는 단순한 표시판이 아니라 최적화의 방향키입니다. 그래서 문제를 푸는 방식과 비용 구조를 지표 안에 반영해야 합니다.

> 지표는 우리가 최적화하는 대상이므로 매우 신중하게 골라야 합니다.

## 핵심 개념 한눈에 보기

## 핵심 용어

- **Confusion matrix**: TP, FP, FN, TN으로 예측 결과를 정리한 표입니다.
- **Precision**: 양성이라고 예측한 것 중 실제 양성이 얼마나 되는지 보여 줍니다.
- **Recall**: 실제 양성 중에서 우리가 얼마나 많이 잡았는지 보여 줍니다.
- **F1**: precision과 recall의 조화평균입니다.
- **ROC AUC**: 임계값에 덜 의존적으로 모델의 구분 능력을 보여 주는 지표입니다.

## Before / After

**Before**: 사기 탐지 모델이 정확도 99%를 찍습니다. 숫자만 보면 대단해 보이지만 재현율이 5%라면 실제 사기 대부분을 놓치고 있습니다.

**After**: recall을 주요 지표로 두고, F1과 비용 기반 지표를 보조 지표로 둡니다. 그제야 문제와 지표가 맞기 시작합니다.

## 실습: 5단계 평가

### 1단계 — confusion matrix 보기

```python
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)
print(cm)
```

분류 평가는 confusion matrix에서 시작합니다. precision, recall, F1도 결국 이 표에서 나옵니다. 어떤 오류가 얼마나 많이 발생했는지 직접 보는 습관이 중요합니다.

### 2단계 — precision, recall, F1 계산

```python
from sklearn.metrics import precision_score, recall_score, f1_score
print(precision_score(y_test, y_pred))
print(recall_score(y_test, y_pred))
print(f1_score(y_test, y_pred))
```

precision은 잘못 알람을 울리는 비용과 연결되고, recall은 놓치는 비용과 연결됩니다. F1은 둘 사이 균형을 보고 싶을 때 유용합니다.

### 3단계 — ROC AUC 보기

```python
from sklearn.metrics import roc_auc_score
proba = model.predict_proba(X_test)[:, 1]
print(roc_auc_score(y_test, proba))
```

ROC AUC는 특정 임계값 하나에 덜 묶여 있다는 장점이 있습니다. 그래서 분류기의 전반적인 구분 능력을 볼 때 자주 사용합니다.

### 4단계 — 회귀 지표 보기

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

print("MAE :", mean_absolute_error(y_test, y_pred))
print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))
print("R^2 :", r2_score(y_test, y_pred))
```

회귀에서는 오차를 어떻게 벌주고 싶은지에 따라 지표를 다르게 봅니다. RMSE는 큰 오차에 더 민감하고, MAE는 더 직관적인 평균 절대 오차를 보여 줍니다.

### 5단계 — 비즈니스 비용 직접 계산

```python
# A false negative costs 5x a false positive
cost = 5 * cm[1, 0] + 1 * cm[0, 1]
print("expected cost:", cost)
```

실무에서는 이 단계가 특히 중요합니다. false negative가 false positive보다 훨씬 비싼 문제라면 그 비용을 직접 숫자로 계산해 지표로 삼아야 합니다. 그래야 모델 점수와 실제 의사결정이 같은 방향을 봅니다.

**Expected output:** confusion matrix와 함께 precision, recall, F1, ROC AUC, 비용 기반 점수를 같은 평가 표에 적습니다.

## 이 코드에서 먼저 봐야 할 점

- confusion matrix는 분류 지표의 뿌리입니다.
- ROC AUC 같은 확률 기반 지표는 임계값 하나에 덜 묶입니다.
- 비즈니스 비용도 직접 계산해서 하나의 지표로 다뤄야 합니다.

## 자주 하는 실수 다섯 가지

1. **accuracy만 보는 실수**: 불균형 데이터에서는 특히 오해를 부릅니다.
2. **임계값 하나만 보고 판단하는 실수**: ROC나 threshold trade-off를 함께 봐야 합니다.
3. **RMSE만 보는 실수**: 이상치에 지나치게 민감할 수 있습니다.
4. **테스트셋에서 임계값을 조정하는 실수**: 평가 데이터에 맞춰 버리는 데이터 누수입니다.
5. **비즈니스 비용을 무시하는 실수**: 점수는 좋아 보여도 현업 만족도는 낮아질 수 있습니다.

## 실무에서는 이렇게 나타납니다

실무 팀은 하나의 주 지표와 여러 가드레일 지표를 함께 둡니다. 예를 들어 recall을 최우선으로 보되, precision이 0.7 아래로 내려가면 배포하지 않는 식입니다. 이렇게 해야 한쪽 지표만 좋아지고 다른 쪽이 무너지는 상황을 막을 수 있습니다.

## 시니어는 이렇게 생각합니다

- 지표는 문제와 함께 고릅니다.
- 비용 행렬은 문서로 남겨야 합니다.
- 주 지표와 가드레일 지표를 분리해 둡니다.
- 임계값은 validation에서 조정하고 test에서는 건드리지 않습니다.
- 지표 정의를 바꾸는 일도 PR 가치가 있는 변경입니다.

## 체크리스트

- [ ] precision, recall, F1의 차이를 설명할 수 있습니다.
- [ ] ROC AUC가 어떤 의미인지 알고 있습니다.
- [ ] MAE, RMSE, R²의 차이를 알고 있습니다.
- [ ] 비용 행렬을 직접 만들 수 있습니다.

## 연습 문제

1. 불균형 데이터에서 accuracy와 recall이 충돌하는 사례를 만들어 보세요.
2. ROC 곡선을 그리고 임계값에 따라 trade-off가 어떻게 달라지는지 관찰해 보세요.
3. 비용 기반 지표를 정의하고, 가장 좋은 임계값을 골라 보세요.

## 정리 및 다음 글

평가는 단순히 점수를 읽는 단계가 아니라, 문제와 모델이 같은 방향을 보고 있는지 확인하는 단계입니다. 어떤 오류가 더 비싼지 지표에 반영해야 결과가 실무 의사결정과 연결됩니다. 다음 글에서는 이렇게 얻은 결과를 어떻게 과장 없이 해석하고 결정으로 옮길지 살펴보겠습니다.

## 실무 확장: 평가 지표 비교와 혼동행렬 기반 해석

평가 단계에서는 지표를 많이 보는 것보다 올바르게 보는 것이 중요합니다. 정확도 하나로 모든 문제를 설명하려고 하면 비즈니스 비용과 실패 유형을 놓치기 쉽습니다. 이 섹션에서는 분류 평가를 중심으로 지표 비교표와 혼동행렬 해석 프레임을 제시합니다.

### 분류 지표 비교표

| 지표 | 질문 | 장점 | 한계 | 적합한 상황 |
| --- | --- | --- | --- | --- |
| Accuracy | 전체에서 맞춘 비율은? | 직관적 | 불균형 데이터에 취약 | 클래스 균형 문제 |
| Precision | 양성 예측 중 진짜 비율은? | 오탐 비용 관리 | 놓침 위험 반영 약함 | 알람 피로 큰 문제 |
| Recall | 실제 양성 중 잡은 비율은? | 놓침 비용 관리 | 오탐 증가 가능 | 탐지/진단 문제 |
| F1 | 정밀도-재현율 균형은? | 균형 판단 용이 | 비용 차이 직접 반영 어려움 | 균형형 의사결정 |
| ROC AUC | 임계값 전반 구분 능력은? | 임계값 의존도 낮음 | 실제 임계값 결정은 별도 필요 | 모델 비교 단계 |

### confusion matrix 해석 루틴

```python
from sklearn.metrics import confusion_matrix, classification_report

cm = confusion_matrix(y_test, y_pred)
print(cm)
print(classification_report(y_test, y_pred, digits=4))

# TN, FP, FN, TP
TN, FP, FN, TP = cm.ravel()
print({"false_positive": int(FP), "false_negative": int(FN)})
```

해석의 핵심은 FP/FN을 비용 관점으로 다시 읽는 것입니다. 예를 들어 의료 스크리닝에서는 FN 비용이 훨씬 크므로 recall 우선 전략이 자연스럽습니다.

### 임계값 조정 예시

```python
import numpy as np
from sklearn.metrics import f1_score

proba = model.predict_proba(X_valid)[:, 1]
thresholds = np.linspace(0.1, 0.9, 17)
records = []
for t in thresholds:
    pred = (proba >= t).astype(int)
    records.append((t, f1_score(y_valid, pred)))

best_t, best_f1 = max(records, key=lambda x: x[1])
print("best_threshold:", round(best_t, 2), "best_f1:", round(best_f1, 4))
```

이 과정은 "모델 점수"와 "운영 정책"을 연결합니다. 임계값을 정하지 않으면 모델은 확률만 내고 행동은 정해지지 않습니다.

### 평가 리포트 템플릿

- 데이터 버전: `churn_v2026_05`
- 주 지표: Recall@threshold=0.35
- 가드레일: Precision >= 0.70
- 비용 함수: `5 * FN + 1 * FP`
- 배포 판단: 조건 충족/미충족 + 근거

평가는 실험의 끝이 아니라 운영 시작점입니다. 지표를 비용과 연결해야 실제 서비스에서 의미 있는 성능 관리가 가능합니다.

### 보강 메모: 팀 운영 관점에서 꼭 남겨야 할 기록

입문 프로젝트에서는 코드가 돌아가는 것만으로도 큰 성취를 느끼기 쉽습니다. 하지만 실무에서 더 중요한 것은 같은 결과를 팀이 다시 만들 수 있는가입니다. 그래서 본문 실습을 수행한 뒤에는 다음 항목을 반드시 문서로 남기는 습관이 필요합니다.

- 실행 날짜와 데이터 버전
- 사용한 핵심 컬럼 목록과 정의
- 주요 가정(제외한 데이터, 임계값, 기간)
- 결과 해석 시 주의할 제약 조건
- 다음 반복에서 확인할 질문

이 다섯 가지를 기록하면 다음 사이클에서 같은 논의를 처음부터 반복하지 않아도 됩니다. 특히 모델 점수나 차트 결과처럼 숫자가 좋아 보이는 상황일수록 제약 조건을 함께 적는 것이 중요합니다. 수치의 강점과 약점을 함께 남겨야 팀이 과신하지 않고, 반대로 필요한 행동은 빠르게 실행할 수 있습니다.

### 보강 예시: 재현 가능한 결과 패키지 만들기

```python
from pathlib import Path
import json
import datetime as dt

meta = {
    "run_at": dt.datetime.utcnow().isoformat(),
    "dataset": "example_v1",
    "assumptions": [
        "trial users excluded",
        "analysis window = last 30 days",
        "threshold fixed before final test",
    ],
    "next_question": "Which segment shows largest variance next week?",
}

out = Path("artifacts")
out.mkdir(exist_ok=True)
(out / "run_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved", out / "run_meta.json")
```

이 코드는 분석 산출물을 실행 메타데이터와 함께 저장하는 가장 작은 예시입니다. 이렇게 작은 기록이 쌓이면 팀 차원의 학습 속도가 크게 올라갑니다. 프로젝트는 한 번의 정답을 찾는 작업이 아니라 반복을 통해 품질을 높이는 작업이기 때문입니다.

## 처음 질문으로 돌아가기

- **정확도가 높으면 정말 좋은 모델이라고 말할 수 있을까요?**
  - 본문의 기준은 평가를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **분류 문제에서 precision, recall, F1, ROC AUC는 각각 무엇을 말해 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **회귀 문제에서 MAE, RMSE, R²는 어떻게 다를까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Science 101 (1/10): Data Science란 무엇인가?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): 문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- [Data Science 101 (3/10): 데이터 수집](./03-data-collection.md)
- [Data Science 101 (4/10): 데이터 정제](./04-data-cleaning.md)
- [Data Science 101 (5/10): 탐색적 데이터 분석](./05-exploratory-data-analysis.md)
- [Data Science 101 (6/10): 시각화](./06-visualization.md)
- [Data Science 101 (7/10): 모델링](./07-modeling.md)
- **평가 (현재 글)**
- 결과 해석 (예정)
- 데이터 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Model Evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Google — Classification Metrics](https://developers.google.com/machine-learning/crash-course/classification)
- [Wikipedia — Receiver Operating Characteristic](https://en.wikipedia.org/wiki/Receiver_operating_characteristic)
- [Aurelien Geron — Hands-On ML](https://github.com/ageron/handson-ml3)

Tags: DataScience, Evaluation, Metrics, ScikitLearn, Beginner

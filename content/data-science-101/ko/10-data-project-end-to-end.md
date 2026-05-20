---
series: data-science-101
episode: 10
title: "Data Science 101 (10/10): 데이터 프로젝트 전체 흐름"
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
  - EndToEnd
  - Project
  - Workflow
  - Beginner
seo_description: 이탈 예측 예제로 문제 정의부터 결정까지 데이터 프로젝트 전체 흐름을 묶어 봅니다
last_reviewed: '2026-05-15'
---

# Data Science 101 (10/10): 데이터 프로젝트 전체 흐름

이 글은 Data Science 101 시리즈의 마지막 글입니다.

시리즈를 따라오면서 각각의 단계는 익혔지만, 막상 실무에 가면 또 다른 질문이 생깁니다. “그래서 이걸 하나의 프로젝트로 묶으면 어떤 흐름이 되는가?” 데이터 수집, 정제, EDA, 모델링, 평가, 해석은 각각 배울 수 있지만, 실제 업무는 언제나 이 단계를 연결해서 움직입니다.

마지막 글인 이번 편에서는 이탈 예측 예제를 중심으로, 문제를 정의하고 데이터를 모으고 모델을 만들고 의사결정으로 닫는 과정을 한 번에 훑어 보겠습니다. 핵심은 모든 단계를 외우는 것이 아니라, 하나의 루프가 어떻게 닫히는지 체감하는 것입니다.

## 먼저 던지는 질문

- 앞선 아홉 단계가 하나의 프로젝트 안에서 어떻게 연결될까요?
- 문제 정의, 수집, 정제, EDA, 모델링, 평가, 해석은 각각 어떤 산출물을 남길까요?
- 이탈 예측 같은 실전 예제에서는 무엇이 결정 시점이 될까요?

## 큰 그림

![Data Science 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/10/10-01-concept-at-a-glance.ko.png)

*Data Science 101 10장 흐름 개요*

이 그림에서는 데이터 프로젝트 전체 흐름를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 데이터 프로젝트 전체 흐름의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 이 글에서 배우는 내용

- 이탈 예측 프로젝트를 처음부터 끝까지 따라가는 방식
- 앞선 아홉 단계가 하나의 흐름으로 이어지는 모습
- 각 단계의 산출물과 결정 지점
- 5단계 미니 프로젝트 실습
- 끝까지 연결해 볼 때 자주 드러나는 실수 다섯 가지

## 왜 중요한가

단계를 따로따로 배우면 각각은 이해해도 전체 설계 감각은 잘 생기지 않습니다. 반대로 하나의 프로젝트를 처음부터 끝까지 한 번 조립해 보면, 이후 다른 도메인에서도 같은 흐름을 재사용하기 쉬워집니다.

실무에서 강한 팀은 개별 기술보다 흐름을 먼저 봅니다. 어떤 문제가 어떤 데이터로 연결되고, 어떤 모델이 어떤 의사결정을 밀어 주는지 한 장으로 설명할 수 있는 팀이 결국 반복 속도도 빨라집니다.

> 전체를 한 번 끝까지 만들어 본 사람이 다음 프로젝트도 더 빨리 만듭니다.

## 핵심 개념 한눈에 보기

## 핵심 용어

- **Churn Prediction**: 곧 이탈할 사용자를 예측하는 문제입니다.
- **Baseline**: 복잡한 모델과 비교할 단순 기준선입니다.
- **Feature**: 모델 입력으로 쓰는 신호입니다.
- **Threshold**: 확률을 행동으로 바꾸는 기준값입니다.
- **Decision**: 분석 결과를 실제 행동으로 닫는 문장입니다.

## Before / After

**Before**: “이탈이 늘고 있어요”라는 말만 있습니다. 누구를 말하는지, 얼마나 늘었는지, 무엇을 해야 하는지 없습니다.

**After**: “30일 내 이탈 위험 상위 10% 사용자 3,200명에게 재참여 캠페인을 보낸다. 예상 이탈 감소는 12%이며 95% 신뢰구간은 ±3%다”처럼 문제, 대상, 수치, 행동이 한 문장으로 연결됩니다.

## 실습: 5단계 미니 프로젝트

### 1단계 — 문제를 정의하기

```text
Q: "How can we reduce churn?"
→ "Predict the top 10% most-likely-to-churn users in 30 days as a campaign target."
Decision: a campaign target list
```

출발점은 “이탈을 줄이자”처럼 넓은 문제입니다. 이를 “30일 안에 이탈할 가능성이 높은 상위 10%를 예측한다”로 바꾸면 프로젝트가 비로소 움직일 수 있습니다. 산출물도 분명해집니다. 이 경우 결과물은 보고서가 아니라 캠페인 대상자 리스트입니다.

### 2단계 — 데이터를 모으고 정리하기

```python
import pandas as pd
df = pd.read_csv("events.csv", parse_dates=["ts"])
df = df.dropna(subset=["user_id"]).drop_duplicates(["user_id", "ts"])
```

원본 이벤트를 가져오고, 핵심 키가 비어 있는 행을 제거하고, 중복 이벤트를 정리합니다. 이 단계에서 데이터 품질이 불안정하면 이후 모든 계산이 흔들립니다.

### 3단계 — EDA와 피처 만들기

```python
features = (
    df.groupby("user_id")
      .agg(sessions=("ts", "count"),
           last_seen=("ts", "max"),
           plan=("plan", "last"))
)
features["days_since_last"] = (pd.Timestamp("2026-05-01") - features["last_seen"]).dt.days
```

여기서는 사용자별 세션 수, 마지막 접속 시점, 요금제 같은 피처를 만듭니다. EDA를 통해 어떤 신호가 이탈과 관계가 있어 보이는지도 함께 확인할 수 있습니다.

### 4단계 — 모델을 만들고 평가하기

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

X, y = features[["sessions", "days_since_last"]], features["churned_30d"]
model = LogisticRegression().fit(X, y)
print("AUC:", roc_auc_score(y, model.predict_proba(X)[:, 1]))
```

여기서는 logistic regression 같은 단순 모델로 시작합니다. 중요한 것은 가장 화려한 모델이 아니라, 빠르게 기준선을 만들고 문제-결정 루프를 닫는 것입니다.

### 5단계 — 결과를 해석하고 결정하기

```text
Top 10% risk segment = 3,200 users
Expected churn reduction = 12% (95% CI ±3%)
Decision: send the re-engagement campaign this Friday
Owner: Growth team / Review: in 2 weeks
```

이제 결과는 행동 문장으로 닫힙니다. 누구에게 무엇을 언제 할지, 누가 책임지고 언제 다시 볼지까지 써야 프로젝트가 실제로 움직입니다.

**Expected output:** 대상자 수, 예상 개선 폭, 실행 시점, 오너, 재검토 날짜가 포함된 프로젝트 액션 메모를 완성합니다.

## 이 코드에서 먼저 봐야 할 점

- 문제에서 결정까지 하나의 흐름으로 닫혀야 프로젝트가 완성됩니다.
- 복잡한 모델보다 먼저 베이스라인 수준의 짧은 루프를 만드는 편이 중요합니다.
- 의사결정 문장이 있어야 분석 결과가 행동으로 바뀝니다.

## 자주 하는 실수 다섯 가지

1. **도구를 먼저 고르는 실수**: 프로젝트는 문제에서 시작해야 합니다.
2. **복잡한 모델에 먼저 집착하는 실수**: 베이스라인을 건너뛰면 비교 기준이 사라집니다.
3. **평가 지표를 끝에서 정하는 실수**: 처음부터 정하지 않으면 프로젝트 중간에 방향이 흔들립니다.
4. **결정 오너가 없는 실수**: 결과가 보고서에서 멈춥니다.
5. **모니터링을 잊는 실수**: 모델은 시간이 지나면서 반드시 낡습니다.

## 실무에서는 이렇게 나타납니다

실무 데이터 팀은 이런 프로젝트를 한 페이지 문서로 시작하는 경우가 많습니다. 문제, 지표, 데이터 출처, 베이스라인, 결정 오너를 먼저 적고, 2주 단위 스프린트로 짧게 돌립니다. 모델은 Airflow, dbt, MLflow 같은 파이프라인 안에 넣어 재현성을 확보하고, 대시보드와 알림으로 드리프트를 계속 관찰합니다.

## 시니어는 이렇게 생각합니다

- 문제에서 결정까지의 루프를 짧게 만듭니다.
- 베이스라인을 존중합니다.
- 오너를 반드시 적습니다.
- 모니터링은 1일 차부터 설계합니다.
- 재현성은 말이 아니라 코드로 보장합니다.

## 체크리스트

- [ ] 문제를 한 줄로 적을 수 있습니다.
- [ ] 베이스라인을 실행할 수 있습니다.
- [ ] 의사결정 문장을 작성할 수 있습니다.
- [ ] 오너와 리뷰 날짜를 지정할 수 있습니다.

## 연습 문제

1. 여러분이 사용하는 서비스 하나를 골라 5단계 미니 프로젝트를 설계해 보세요.
2. 이탈 예측 예제에서 베이스라인보다 나아질 수 있는 피처 세 가지를 제안해 보세요.
3. 두 가지 지표를 사용해 모델 드리프트를 어떻게 정의할지 적어 보세요.

## 정리 및 다음 단계

이 시리즈는 문제 → 데이터 → 모델 → 결정으로 이어지는 하나의 흐름을 조립하는 과정이었습니다. 각 단계를 따로 배우는 것도 중요하지만, 결국 실무에서는 이 단계를 하나의 프로젝트 안에서 닫아야 합니다. 다음 학습 단계로는 Statistics 101, Machine Learning 101, MLOps 101처럼 각 부분을 더 깊게 파고드는 시리즈가 자연스럽게 이어질 것입니다.

## 처음 질문으로 돌아가기

- **앞선 아홉 단계가 하나의 프로젝트 안에서 어떻게 연결될까요?**
  - 본문의 기준은 데이터 프로젝트 전체 흐름를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **문제 정의, 수집, 정제, EDA, 모델링, 평가, 해석은 각각 어떤 산출물을 남길까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **이탈 예측 같은 실전 예제에서는 무엇이 결정 시점이 될까요?**
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
- [Data Science 101 (8/10): 평가](./08-evaluation.md)
- [Data Science 101 (9/10): 결과 해석](./09-result-interpretation.md)
- **데이터 프로젝트 전체 흐름 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Google — People + AI Research Guidebook](https://pair.withgoogle.com/guidebook/)
- [scikit-learn — Common Pitfalls and Recommended Practices](https://scikit-learn.org/stable/common_pitfalls.html)
- [Made With ML — End-to-End ML Course](https://madewithml.com/)
- [Full Stack Deep Learning](https://fullstackdeeplearning.com/)

Tags: DataScience, EndToEnd, Project, Workflow, Beginner

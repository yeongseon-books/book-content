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

시리즈를 따라오면서 각각의 단계는 익혔지만, 막상 실무에 가면 또 다른 질문이 생깁니다. “그래서 이걸 하나의 프로젝트로 묶으면 어떤 흐름이 되는가?” 데이터 수집, 정제, EDA, 모델링, 평가, 해석은 각각 배울 수 있지만, 실제 업무는 언제나 이 단계를 연결해서 움직입니다.

이 글은 Data Science 101 시리즈의 마지막 글입니다.

마지막 글인 이번 편에서는 이탈 예측 예제를 중심으로, 문제를 정의하고 데이터를 모으고 모델을 만들고 의사결정으로 닫는 과정을 한 번에 훑어 보겠습니다. 핵심은 모든 단계를 외우는 것이 아니라, 하나의 루프가 어떻게 닫히는지 체감하는 것입니다.

![Data Science 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/10/10-01-concept-at-a-glance.ko.png)
*Data Science 101 10장 흐름 개요*
> 데이터 프로젝트 전체 흐름의 핵심은 기능 이름이 아니라, 입력을 받는 경계에서 결과를 내보내는 경계까지 어떤 기준으로 데이터를 검증하고 처리할 것인가를 명확히 정하는 데 있습니다.

## 먼저 던지는 질문

- 앞선 아홉 단계가 하나의 프로젝트 안에서 어떻게 연결될까요?
- 문제 정의, 수집, 정제, EDA, 모델링, 평가, 해석은 각각 어떤 산출물을 남길까요?
- 이탈 예측 같은 실전 예제에서는 무엇이 결정 시점이 될까요?

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

## 핵심 용어

- **Churn Prediction**: 곧 이탈할 사용자를 예측하는 문제입니다.
- **Baseline**: 복잡한 모델과 비교할 단순 기준선입니다.
- **Feature**: 모델 입력으로 쓰는 신호입니다.
- **Threshold**: 확률을 행동으로 바꾸는 기준값입니다.
- **Decision**: 분석 결과를 실제 행동으로 닫는 문장입니다.

## 전/후 비교

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

## 실무 확장: 프로젝트 발표 구조와 비즈니스 임팩트 정량화

엔드투엔드 프로젝트의 마지막 품질은 "무엇을 만들었는가"보다 "무엇이 바뀌었는가"로 평가됩니다. 그래서 최종 보고에서는 기술 스택 나열보다 비즈니스 임팩트 정량화가 중요합니다. 이 섹션에서는 데이터 프로젝트 발표를 위한 구조와 계산 예시를 정리합니다.

### 발표 구조 템플릿(10분 기준)

| 순서 | 섹션 | 핵심 질문 | 필수 산출물 |
| --- | --- | --- | --- |
| 1 | 문제 정의 | 어떤 의사결정을 개선하려는가 | 문제 문장, KPI |
| 2 | 데이터/방법 | 어떤 데이터와 방법을 썼는가 | 데이터 범위, 모델 요약 |
| 3 | 결과 | 얼마나 개선되었는가 | 기준선 대비 지표 표 |
| 4 | 임팩트 | 비용/매출에 어떤 변화가 있는가 | 금액 환산 시나리오 |
| 5 | 실행 계획 | 누가 언제 무엇을 할 것인가 | 오너, 타임라인, 리스크 |

### 비즈니스 임팩트 계산 예시

```python
# 예시: 이탈 감소로 인한 월 매출 보전 효과
active_users = 32000
avg_mrr = 18.5
baseline_churn = 0.082
new_churn = 0.072

retained_users = active_users * (baseline_churn - new_churn)
impact_mrr = retained_users * avg_mrr

print({
    "retained_users": round(retained_users),
    "monthly_mrr_impact": round(impact_mrr, 2),
})
```

이 계산은 완벽한 재무 모델이 아니라 의사결정용 1차 추정치입니다. 중요한 것은 가정을 명시하고 민감도 분석을 함께 제시하는 것입니다.

### 시나리오 기반 임팩트 표

| 시나리오 | 이탈률 개선폭 | 월 보전 사용자 | 월 MRR 영향 |
| --- | --- | --- | --- |
| 보수적 | 0.5%p | 160명 | 약 2,960 |
| 기준 | 1.0%p | 320명 | 약 5,920 |
| 낙관적 | 1.5%p | 480명 | 약 8,880 |

### 최종 의사결정 문장 예시

"리텐션 모델을 유료 사용자 전체에 즉시 확대 배포하지 않고, 위험 상위 20% 세그먼트에 2주간 단계 적용합니다. 단계 적용 동안 비용 지표(`5*FN + FP`)와 월 보전 사용자 수를 동시에 모니터링하고, 가드레일 미충족 시 자동 롤백합니다."

### 프로젝트 마무리 체크리스트

- 기술 지표와 비즈니스 지표를 함께 보고했는가
- 기준선 대비 개선폭을 명확히 제시했는가
- 불확실성과 가정을 명시했는가
- 실행 오너와 검토 주기를 지정했는가
- 다음 실험 백로그를 우선순위와 함께 남겼는가

프로젝트를 끝까지 닫는다는 것은 모델을 만드는 것이 아니라, 결과를 조직의 반복 가능한 의사결정 루프로 편입시키는 것입니다. 이 관점이 있으면 다음 프로젝트의 시작 속도와 품질이 동시에 좋아집니다.

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

## 실무 심화: 분석 설계를 운영 가능한 루프로 만들기

앞에서 다룬 개념을 실제 팀 운영으로 연결하려면, 분석 노트 수준을 넘어 반복 가능한 실험 루프를 만들어야 합니다. 핵심은 세 가지입니다. 첫째, 피처를 만드는 규칙이 코드와 문서에 동시에 남아야 합니다. 둘째, 시각화는 설명용 그림이 아니라 의사결정 트리거를 확인하는 점검 도구여야 합니다. 셋째, 모델 평가는 점수 한 줄이 아니라 행동 변화까지 포함해 해석해야 합니다.

### 넘파이와 판다스로 만드는 피처 테이블 예시

```python
import numpy as np
import pandas as pd

orders = pd.read_csv('orders.csv', parse_dates=['ordered_at'])
users = pd.read_csv('users.csv', parse_dates=['signup_at'])

base = orders.merge(users[['user_id', 'signup_at', 'country']], on='user_id', how='left')
base['days_since_signup'] = (base['ordered_at'] - base['signup_at']).dt.days.clip(lower=0)
base['is_weekend'] = base['ordered_at'].dt.dayofweek.isin([5, 6]).astype(int)
base['amount_log1p'] = np.log1p(base['amount'].clip(lower=0))

agg = (
    base.groupby('user_id', as_index=False)
    .agg(
        order_count=('order_id', 'count'),
        avg_amount=('amount', 'mean'),
        recent_amount=('amount', 'last'),
        signup_age=('days_since_signup', 'max'),
        weekend_ratio=('is_weekend', 'mean'),
    )
)

print(agg.head())
```

이 예시는 원본 테이블을 그대로 쓰지 않고, 분석 목적에 맞는 사용자 단위 피처셋으로 변환합니다. `log1p` 같은 변환은 분포 왜곡을 완화하고, `weekend_ratio`처럼 행동 패턴 피처를 추가하면 단순 합계보다 설명력이 좋아지는 경우가 많습니다.

### 맷플롯립으로 분포와 구간별 패턴 확인

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
agg['avg_amount'].hist(bins=30, edgecolor='black', ax=ax[0])
ax[0].set_title('평균 주문금액 분포')
ax[0].set_xlabel('avg_amount')

agg.sort_values('signup_age').reset_index(drop=True)['order_count'].rolling(100).mean().plot(ax=ax[1])
ax[1].set_title('가입 경과일 기준 주문수 이동평균')
ax[1].set_ylabel('rolling mean')

plt.tight_layout()
plt.show()
```

시각화의 목적은 "예쁜 차트"가 아니라 이상 신호를 빨리 찾는 것입니다. 분포가 한쪽으로 치우치면 로그 변환을 검토하고, 구간별 이동평균이 급변하면 세그먼트 분할 기준을 다시 정하는 식으로 다음 행동을 결정합니다.

### sklearn 파이프라인으로 전처리와 모델을 한 번에 관리

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

num_cols = ['order_count', 'avg_amount', 'recent_amount', 'signup_age', 'weekend_ratio']
cat_cols = ['country']

numeric = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
])

categorical = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore')),
])

preprocess = ColumnTransformer([
    ('num', numeric, num_cols),
    ('cat', categorical, cat_cols),
])

model = Pipeline([
    ('preprocess', preprocess),
    ('clf', LogisticRegression(max_iter=1000, class_weight='balanced')),
])
```

파이프라인을 쓰면 학습과 추론 경로가 동일해져서 재현성이 올라갑니다. "노트북에서는 되는데 배치에서는 안 된다" 같은 문제를 줄이는 가장 확실한 방법 중 하나입니다.

### 간단한 A/B 테스트 설계 템플릿

실험 설계는 모델링 못지않게 중요합니다. 아래 템플릿은 마케팅 메시지 개선 같은 실무 시나리오에서 바로 쓸 수 있습니다.

| 항목 | 설계 예시 |
| --- | --- |
| 가설 | 신규 온보딩 메시지를 바꾸면 7일 재방문율이 증가합니다. |
| 모집단 | 지난 14일 내 가입한 신규 사용자(사내 계정 제외) |
| 무작위 배정 | user_id 해시 기준 50:50 |
| 1차 지표 | 7일 재방문율 |
| 가드레일 지표 | 고객센터 문의율, 결제 실패율 |
| 실험 기간 | 최소 2주 또는 표본 수 도달 시점 |
| 중지 조건 | 가드레일 지표 악화가 기준 임계치 초과 |

A/B 테스트에서 가장 흔한 실수는 결과를 너무 빨리 확정하는 것입니다. 중간 결과를 여러 번 들여다보는 경우, 사전에 정한 중지 규칙과 분석 계획을 문서로 고정해 두지 않으면 우연한 변동을 효과로 오해할 수 있습니다.

### 운영 체크포인트

- 피처 생성 규칙을 코드와 문서에 동시에 남깁니다.
- EDA 그래프마다 "이 그래프를 보고 어떤 결정을 내릴지"를 한 줄로 적습니다.
- 모델 점수와 함께 비용, 지연, 운영 복잡도를 같이 평가합니다.
- A/B 테스트는 가설, 표본, 중지 규칙을 실험 시작 전에 고정합니다.
- 결과 발표 문서는 "무엇을 배웠고 다음 주에 무엇을 바꿀지"로 마무리합니다.

### 추가 실전 예시: 파이프라인 결과를 실험 설계로 연결하기

아래 예시는 피처셋을 만든 뒤 바로 끝내지 않고, 실제 실험 대상으로 넘기는 최소 흐름을 보여 줍니다. 분석 결과를 운영으로 연결하는 팀은 보통 이런 형태의 전환 코드를 갖고 있습니다.

```python
import pandas as pd

scored = pd.read_csv('scored_users.csv')
scored = scored.sort_values('risk_score', ascending=False)

eligible = scored.query('is_marketing_opt_in == 1 and recent_complaint == 0').copy()
eligible['bucket'] = (eligible.index % 2).map({0: 'A', 1: 'B'})

plan = eligible[['user_id', 'risk_score', 'bucket']].head(5000)
print(plan['bucket'].value_counts())
print(plan.head())
```

이 단계에서 중요한 것은 점수보다 규칙입니다. 제외 조건, 배정 규칙, 실험 크기를 사전에 고정해야 실험 이후 해석 충돌이 줄어듭니다.

### 추가 점검표

- 데이터 추출 쿼리와 피처 생성 코드의 버전을 함께 기록합니다.
- 모델 점수 분포를 분위수로 확인하고, 상위 구간 편향을 검토합니다.
- 실험군 배정 후 집단 균형(국가, 디바이스, 유입채널)을 반드시 확인합니다.
- 실험 종료 전에는 중간 지표를 의사결정 근거로 확정하지 않습니다.

### 보강 메모: 결과 해석 전 확인할 최소 통제

분석 결과를 공유하기 전에 최소 통제를 거치면 해석 품질이 크게 안정됩니다. 기간 경계가 바뀌지 않았는지, 결측치 처리 규칙이 버전 간 동일한지, 실험군 배정이 무작위로 유지됐는지 세 가지는 반드시 확인하는 편이 좋습니다.

```python
import pandas as pd

report = pd.read_csv('experiment_daily_report.csv')
checks = {
    'date_min': str(report['date'].min()),
    'date_max': str(report['date'].max()),
    'null_rate': float(report.isna().mean().mean()),
    'groups': report['bucket'].value_counts(normalize=True).to_dict(),
}
print(checks)
```

이 기록은 화려하지 않지만, 다음 회차에서 "같은 기준으로 다시 봤는가"를 보장하는 가장 실용적인 안전장치입니다.

### 운영 관점 보충

실무에서는 분석 정확도만큼 운영 일관성이 중요합니다. 같은 코드를 실행해도 입력 데이터 스냅샷이 다르면 결론이 달라질 수 있으므로, 실행 시점과 데이터 버전을 함께 남겨야 합니다. 또한 배포 전에는 기준선 대비 개선 폭과 비용 증가 폭을 같이 보고, 작은 개선이라도 유지보수 비용이 크게 늘면 적용을 보류하는 판단이 필요합니다. 이 원칙은 시각화, 모델링, 평가, 해석 단계 모두에 동일하게 적용됩니다.

## 처음 질문으로 돌아가기

- **앞선 아홉 단계가 하나의 프로젝트 안에서 어떻게 연결될까요?**
  - 이 글에서는 문제 정의 → 수집/정제 → 피처 생성 → 모델링/평가 → 결정으로 하나의 루프를 닫았습니다. `events.csv`에서 출발해 `features["days_since_last"]`를 만들고, `LogisticRegression()`으로 위험도를 계산한 뒤 캠페인 실행 문장으로 마무리한 흐름이 그 연결 자체입니다.
- **문제 정의, 수집, 정제, EDA, 모델링, 평가, 해석은 각각 어떤 산출물을 남길까요?**
  - 문제 정의는 타깃 문장, 수집과 정제는 재현 가능한 데이터셋, EDA는 피처 후보 메모, 모델링은 baseline과 학습 코드, 평가는 AUC 같은 점수표, 해석은 액션 메모를 남깁니다. 본문에서도 마지막 산출물을 `target list`, `Expected churn reduction = 12%`, `Owner`, `Review`까지 적는 형식으로 구체화했습니다.
- **이탈 예측 같은 실전 예제에서는 무엇이 결정 시점이 될까요?**
  - 결정 시점은 모델 점수가 좋아 보이는 순간이 아니라, 예측을 실제 행동으로 바꿀 기준이 정해졌을 때입니다. 이 예제에서는 `Top 10% risk segment = 3,200 users`와 `send the re-engagement campaign this Friday`가 함께 적힌 순간이 바로 프로젝트의 결정 시점이었습니다.

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
- [book-examples — data-science-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-science-101/ko)

Tags: DataScience, EndToEnd, Project, Workflow, Beginner

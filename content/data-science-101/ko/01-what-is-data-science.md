---
series: data-science-101
episode: 1
title: "Data Science 101 (1/10): Data Science란 무엇인가?"
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
  - Introduction
  - Workflow
  - Analytics
  - Beginner
seo_description: 데이터 사이언스의 정의와 역할 구분, 문제-데이터-결정 흐름을 정리합니다
last_reviewed: '2026-05-15'
---

# Data Science 101 (1/10): Data Science란 무엇인가?

이 글은 Data Science 101 시리즈의 첫 번째 글입니다.

데이터 분야를 처음 접하면 가장 먼저 부딪히는 문제는 용어 혼선입니다. 데이터 분석, 데이터 사이언스, 머신러닝, MLOps가 한 덩어리처럼 들리고, 데이터 분석가와 데이터 사이언티스트, ML 엔지니어의 경계도 금방 흐려집니다. 이때 바로 도구로 들어가면 배우는 항목은 많아지지만 머릿속 구조는 오히려 더 흐릿해집니다.

그래서 출발점에서는 기술 목록보다 먼저 큰 그림이 필요합니다. 데이터 사이언스가 정확히 무엇을 하는 일인지, 데이터 작업이 왜 문제 정의에서 시작해 의사결정으로 끝나야 하는지, 각 역할이 어디서 갈리는지를 먼저 잡아 두어야 이후의 수집, 정제, EDA, 시각화, 모델링이 한 흐름으로 읽힙니다.


![Data Science 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/01/01-01-concept-at-a-glance.ko.png)
*Data Science 101 1장 흐름 개요*
> 데이터 사이언스의 핵심은 기술 이름이 아니라, 문제를 데이터로 답할 수 있는 형태로 바꾸고 그 답을 실제 행동으로 연결하는 것입니다.

## 먼저 던지는 질문

- 데이터 사이언스를 한 문장으로 어떻게 이해하면 좋을까요?
- 데이터 분석가, 데이터 사이언티스트, ML 엔지니어, 데이터 엔지니어는 무엇이 다를까요?
- 데이터 작업은 왜 늘 문제 정의에서 시작해야 할까요?

## 이 글에서 배우는 내용

- 데이터 사이언스를 실무적으로 정의하는 방법
- 분석가, 사이언티스트, 엔지니어 역할의 차이
- 문제에서 결정까지 이어지는 5단계 워크플로
- 입문자가 자주 하는 질문의 큰 그림
- 처음부터 피해야 할 대표적인 오해 다섯 가지

## 왜 중요한가

직무 이름이 겹치는 분야일수록 학습 순서는 쉽게 흔들립니다. 큰 그림 없이 도구부터 배우면 SQL, Pandas, 대시보드, 모델링 기법이 각각 따로 떠다니는 조각처럼 남습니다. 반대로 데이터 작업이 결국 문제를 정의하고, 데이터를 읽고, 모델이나 인사이트를 만들고, 마지막에 의사결정으로 닫는 일이라는 관점을 먼저 잡으면 무엇을 왜 배우는지가 분명해집니다.

저는 입문자에게 이 지점을 가장 먼저 강조합니다. 데이터 사이언스는 데이터를 많이 다루는 직무가 아니라, 데이터를 통해 문제를 답할 수 있는 구조로 바꾸는 직무에 더 가깝기 때문입니다.

> 큰 그림 없이 배우는 공부는 조각을 모으는 일에 머무르기 쉽습니다.

## 핵심 용어

- **Data Analyst**: 지표와 대시보드를 통해 비즈니스 질문에 답하는 역할입니다.
- **Data Scientist**: 모델을 만들고 실험을 설계해 예측과 최적화를 시도하는 역할입니다.
- **ML Engineer**: 모델을 서비스 환경에 올리고 운영 가능하게 만드는 역할입니다.
- **Data Engineer**: 데이터 파이프라인과 웨어하우스를 설계하고 유지하는 역할입니다.
- **EDA**: Exploratory Data Analysis의 약자로, 모델링 전에 데이터를 읽는 탐색 단계입니다.

## 데이터 사이언스 vs 통계학 vs 머신러닝

데이터 사이언스는 통계학, 머신러닝, 도메인 지식이 만나는 교차점입니다. 세 분야는 겹치기도 하지만 목적과 산출물에서 차이가 있습니다.

| 분야 | 주요 목적 | 대표 방법 | 대표 산출물 |
|---|---|---|---|
| 통계학 | 불확실성 하에서 추정과 검증 | 가설검정, 신뢰구간, 회귀분석 | p-value, 신뢰구간, 보고서 |
| 머신러닝 | 데이터에서 예측 모델 학습 | 지도학습, 비지도학습, 강화학습 | 예측 모델, 정확도, API |
| 데이터 사이언스 | 데이터로 비즈니스 문제 해결 | 전체 워크플로 (문제→데이터→결정) | 의사결정, 대시보드, 자동화 시스템 |

통계학은 모집단 파라미터를 추정하는 데 초점을 맞추고, 머신러닝은 예측 성능을 우선합니다. 데이터 사이언스는 둘을 모두 도구로 쓰되, 최종 목표는 문제 해결과 의사결정 개선입니다.

## 데이터 사이언스 프로세스 (CRISP-DM)

데이터 사이언스 프로젝트는 선형적으로 흐르지 않습니다. 문제를 이해하고, 데이터를 준비하고, 모델을 만들고, 배포한 뒤 다시 평가하는 순환 구조를 따릅니다. 이를 표준화한 대표 프레임워크가 CRISP-DM (Cross-Industry Standard Process for Data Mining)입니다.

CRISP-DM은 여섯 단계로 구성됩니다:

1. **Business Understanding** — 문제를 비즈니스 맥락에서 정의합니다.
2. **Data Understanding** — 데이터를 수집하고 탐색합니다.
3. **Data Preparation** — 정제, 변환, 피처 엔지니어링을 수행합니다.
4. **Modeling** — 모델을 학습하고 튜닝합니다.
5. **Evaluation** — 비즈니스 기준으로 모델을 평가합니다.
6. **Deployment** — 모델을 운영 환경에 배포하고 모니터링합니다.

중요한 것은 순서입니다. 문제를 먼저 이해하지 않고 데이터부터 보면 방향을 잃기 쉽습니다. 또 배포 후에는 다시 비즈니스 이해로 돌아가 결과가 실제로 문제를 해결했는지 확인해야 합니다.

## 파이썬 Pandas EDA 예제

이번에는 데이터 사이언스 워크플로의 초입부인 EDA를 간단한 Python 예제로 봅니다. Pandas는 표 형태 데이터를 다루는 대표 라이브러리이며, 거의 모든 데이터 사이언스 프로젝트의 출발점입니다.

```python
import pandas as pd

# 샘플 데이터 읽기
df = pd.read_csv("users.csv")

# 데이터 크기 확인
print("Shape:", df.shape)  # (행 수, 열 수)

# 첫 몇 행 확인
print(df.head())

# 컬럼별 타입 확인
print(df.dtypes)

# 기술 통계량 확인
print(df.describe())

# 결측치 확인
print(df.isna().sum())

# 특정 컬럼 분포 확인
print(df["country"].value_counts())
```

이 예제는 데이터 크기, 타입, 결측치, 분포를 빠르게 읽습니다. EDA는 가설을 세우거나 모델을 만들기 전에 데이터가 실제로 어떤 모습인지 확인하는 단계이며, 분석의 절반은 여기서 정해집니다.

## 전/후 비교

**Before**: 데이터가 있으니 일단 뭔가 분석해 보고, 그 결과가 어디에 쓰일지 나중에 생각합니다. 질문은 넓고 결과는 흐릿해서 보고서를 다 만들고도 “그래서 무엇을 해야 하죠?”라는 말이 남습니다.

**After**: 문제를 한 문장으로 좁히고, 그 문제에 필요한 데이터만 보고, 결과를 의사결정 문장으로 닫습니다. 같은 데이터라도 해석과 실행의 선명도가 완전히 달라집니다.

## 실습: 5단계 워크플로

### 1단계 — 문제 정의

```text
"Each week, pick 100 users most likely to churn"
```

좋은 문제 정의는 구체적입니다. 주기, 대상, 산출물이 들어 있어야 합니다. “이탈을 줄이자”보다 “매주 이탈 가능성이 높은 사용자 100명을 고른다”가 훨씬 낫습니다. 이렇게 써야 이후의 수집과 모델링이 흔들리지 않습니다.

### 2단계 — 데이터 수집

```python
import pandas as pd
df = pd.read_csv("users.csv")
print(df.shape, df.columns.tolist())
```

여기서 중요한 것은 파일을 읽는 문법보다, 지금 보고 있는 데이터가 어느 시점의 어떤 원본에서 왔는지 추적 가능해야 한다는 점입니다. 두 달 뒤에 같은 분석을 다시 할 수 없다면 그 결과는 신뢰를 얻기 어렵습니다.

### 3단계 — 정제와 EDA

```python
df = df.dropna(subset=["last_login"])
df["days_since_login"] = (
    pd.Timestamp.today() - pd.to_datetime(df["last_login"])
).dt.days
print(df["days_since_login"].describe())
```

수집한 데이터는 거의 항상 바로 쓰기 어렵습니다. 결측치가 있고, 타입이 맞지 않고, 분포를 먼저 읽어 봐야 합니다. EDA는 모델링 전의 형식적 절차가 아니라, 데이터가 스스로 자신을 소개하는 시간입니다.

### 4단계 — 모델 또는 규칙

```python
candidates = (
    df[df["days_since_login"] > 30]
      .sort_values("amount_total", ascending=False)
      .head(100)
)
```

모든 문제에 복잡한 모델이 필요한 것은 아닙니다. 때로는 간단한 규칙 기반 우선순위만으로도 충분한 가치를 만들 수 있습니다. 핵심은 정교함이 아니라 문제 적합성입니다.

### 5단계 — 의사결정으로 연결

```text
Email campaign for 100 users → measure conversion → adjust next week
```

마지막 단계가 빠지면 데이터 작업은 자주 보고서에서 멈춥니다. 결과는 반드시 “무엇을 할 것인가”로 닫혀야 합니다. 그래야 다음 주에 다시 측정하고, 개선하고, 같은 루프를 돌릴 수 있습니다.

**Expected output:** 문제 문장, 핵심 데이터, 최종 의사결정이 한 줄 흐름으로 이어진 작은 워크플로 메모를 얻습니다.

## 이 코드에서 먼저 봐야 할 점

- 문제를 한 문장으로 쓰는 순간 이후의 모든 코드가 방향을 갖습니다.
- 데이터 흐름은 읽기 → 정제 → 탐색 → 결정으로 이어집니다.
- 모델이나 대시보드는 결정으로 연결될 때 비로소 실무 가치를 가집니다.

## 자주 하는 실수 다섯 가지

1. **도구부터 배우는 실수**: 문제 없이 도구만 익히면 언제 무엇을 써야 할지 기준이 생기지 않습니다.
2. **모델 정확도만 보는 실수**: 비즈니스 지표가 함께 좋아졌는지 보지 않으면 엉뚱한 최적화가 됩니다.
3. **EDA를 건너뛰는 실수**: 데이터가 실제로 어떤 모습인지 확인하지 않으면 가설을 너무 빨리 굳히게 됩니다.
4. **역할 경계를 무시하는 실수**: 협업과 채용이 꼬이고, 책임 구분도 흐려집니다.
5. **결과를 결정과 연결하지 않는 실수**: 보고서는 남지만 행동은 바뀌지 않습니다.

## 실무에서는 이렇게 나타납니다

초기 스타트업 데이터 팀은 종종 작은 조직 하나처럼 움직입니다. 한쪽에서는 대시보드와 핵심 지표를 보고, 다른 쪽에서는 모델을 만들고, 또 다른 쪽에서는 데이터 파이프라인과 운영을 맡습니다. 역할은 겹칠 수 있어도 모든 작업은 결국 한 질문으로 모입니다. “이 결과가 어떤 결정을 바꾸는가?” 이 질문이 없는 데이터 작업은 오래 유지되기 어렵습니다.

## 시니어는 이렇게 생각합니다

- 문제를 잘 정의하는 일이 모델링보다 더 비쌀 때가 많습니다.
- EDA를 대충 하면 뒤의 모든 단계가 흔들립니다.
- 결과는 반드시 결정 문장으로 닫혀야 합니다.
- 역할 경계는 문서로 남겨야 협업이 단순해집니다.
- 데이터 품질은 특정 직군만의 일이 아니라 팀 전체의 책임입니다.

## 체크리스트

- [ ] 데이터 분석가, 데이터 사이언티스트, 엔지니어의 차이를 설명할 수 있습니다.
- [ ] EDA가 무엇인지 알고 있습니다.
- [ ] 문제 → 데이터 → 결정 흐름을 이해하고 있습니다.
- [ ] 비즈니스 지표가 왜 중요한지 설명할 수 있습니다.

## 연습 문제

1. 최근에 본 대시보드 하나를 떠올리고, 그 대시보드가 어떤 결정을 위해 쓰였는지 적어 보세요.
2. 분석가와 데이터 사이언티스트 역할의 공통점을 3가지 적어 보세요.
3. 한 문장짜리 문제 정의를 3개 작성해 보세요.

## 정리 및 다음 글

데이터 사이언스는 데이터 자체를 다루는 기술이 아니라, 문제와 데이터를 연결해 의사결정으로 닫는 일입니다. 이 관점을 잡고 나면 수집, 정제, EDA, 시각화, 모델링이 각각 어디에 놓이는지 훨씬 또렷해집니다. 다음 글에서는 막연한 문제를 실제로 데이터가 답할 수 있는 질문으로 어떻게 바꾸는지 다룹니다.

## 실무 확장: 데이터 과학 프로세스를 구조로 이해하기

앞 절에서 데이터 사이언스의 정의와 역할 경계를 잡았다면, 이제는 실제 프로젝트를 어떤 단계로 운영하는지 구조적으로 보는 것이 좋습니다. 입문자는 보통 도구 목록을 먼저 외우지만, 실무에서는 도구보다 순서와 산출물이 더 중요합니다. 같은 Python과 같은 pandas를 써도 문제 정의가 흐리면 결과는 재현되지 않고, 반대로 단계와 산출물이 명확하면 팀 규모가 커져도 품질이 유지됩니다. 이 섹션에서는 CRISP-DM 관점을 기준으로 데이터 과학의 반복 루프를 정리하고, 각 단계에서 어떤 역할이 중심이 되는지 비교합니다.

### CRISP-DM 6단계와 핵심 산출물

| 단계 | 핵심 질문 | 주요 활동 | 대표 산출물 | 실패 신호 |
| --- | --- | --- | --- | --- |
| 비즈니스 이해 | 무엇을 개선하려는가 | 목표/제약/비용 정리 | 문제 정의 문장, KPI | 목표가 추상적임 |
| 데이터 이해 | 어떤 데이터가 있는가 | 출처 확인, 초기 EDA | 데이터 인벤토리, 품질 메모 | 출처 불명 데이터 사용 |
| 데이터 준비 | 학습 가능한 형태인가 | 정제, 결합, 피처 설계 | 정제 스크립트, 피처셋 | 규칙이 문서화되지 않음 |
| 모델링 | 어떤 방법이 적합한가 | 베이스라인, 모델 실험 | 실험 로그, 모델 후보 | 기준선 대비 이득 불명 |
| 평가 | 실무에 쓸 수 있는가 | 지표, 비용, 리스크 검토 | 평가 리포트, 배포 판단 | 정확도만 보고 결정 |
| 배포/운영 | 실제 행동으로 이어지는가 | 모니터링, 재학습 계획 | 운영 대시보드, 알림 규칙 | 배포 후 추적 부재 |

표를 보면 중요한 공통점이 있습니다. 모든 단계는 "질문-활동-산출물"의 형태로 닫혀야 합니다. 활동만 있고 산출물이 없으면 다음 단계가 같은 맥락을 공유하지 못합니다. 특히 입문 단계에서는 "뭘 해봤다"보다 "무엇을 남겼다"를 기준으로 학습하는 편이 훨씬 빠릅니다.

### 역할 비교: 같은 팀, 다른 책임

역할 이름이 비슷해 보이더라도 책임의 중심은 분명히 다릅니다. 아래 비교표는 실무 협업에서 충돌이 자주 나는 지점을 기준으로 정리한 것입니다.

| 역할 | 주 질문 | 주 산출물 | 협업 접점 |
| --- | --- | --- | --- |
| 데이터 분석가 | 현재 상태를 어떻게 설명할까 | 지표 정의서, 대시보드, 분석 메모 | PM, 마케팅, 운영 |
| 데이터 사이언티스트 | 어떤 예측/최적화가 가능한가 | 실험 노트, 모델 평가 리포트 | 분석가, ML 엔지니어 |
| ML 엔지니어 | 모델을 어떻게 안정적으로 운영할까 | 서빙 파이프라인, 모니터링 | 백엔드, 플랫폼 |
| 데이터 엔지니어 | 신뢰 가능한 데이터를 어떻게 공급할까 | ETL/ELT, 웨어하우스 모델 | 전 역할 공통 |

핵심은 우열이 아니라 경계입니다. 경계가 선명해야 책임이 선명해지고, 책임이 선명해야 품질 이슈가 발생했을 때 빠르게 원인을 찾을 수 있습니다.

### Python으로 보는 최소 분석 루프

아래 코드는 복잡한 모델링이 아니라 "문제-지표-행동" 루프를 가장 작게 확인하는 예시입니다.

```python
import pandas as pd

orders = pd.read_csv("orders.csv")
orders["order_date"] = pd.to_datetime(orders["order_date"])

recent = orders[orders["order_date"] >= "2026-05-01"]
summary = (
    recent.groupby("channel", as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
)

print(summary)
print("Decision: next week paid budget focuses on top-2 channels")
```

이 코드는 단순하지만 중요한 원칙을 담고 있습니다. 첫째, 기간을 명시합니다. 둘째, 집계 기준을 명시합니다. 셋째, 출력을 행동 문장으로 닫습니다. 입문자일수록 이런 작은 루프를 반복해 문제 정의와 의사결정 연결 감각을 키우는 것이 좋습니다.

### 프로젝트 시작 전에 확인할 운영 체크포인트

- 목표 지표를 한 문장으로 적었는가
- 비교 기간과 대상 집단이 합의되었는가
- 데이터 출처와 추출 시각을 기록하는가
- 베이스라인과 최종 판단 기준이 있는가
- 결과를 받을 의사결정 오너가 지정되었는가

이 다섯 가지가 비어 있으면 기술 수준과 무관하게 프로젝트가 길어질 가능성이 큽니다. 반대로 이 항목이 채워져 있으면 도구가 조금 서툴러도 결과의 품질은 빠르게 올라갑니다.


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


## 처음 질문으로 돌아가기

- **데이터 사이언스를 한 문장으로 어떻게 이해하면 좋을까요?**
  - 데이터 사이언스는 문제를 읽고, 데이터로 증거를 만들고, 그 증거로 의사결정을 바꾸는 순환 고리입니다.
- **데이터 분석가, 데이터 사이언티스트, ML 엔지니어, 데이터 엔지니어는 무엇이 다를까요?**
  - 분석가는 지표를 추적하고, 사이언티스트는 모델을 만들고, 엔지니어는 이를 운영 시스템에 올립니다.
- **데이터 작업은 왜 늘 문제 정의에서 시작해야 할까요?**
  - 문제를 명확히 해야 필요한 데이터만 수집하고, 불필요한 분석을 건너뛸 수 있기 때문입니다.

<!-- toc:begin -->
## 시리즈 목차

- **Data Science란 무엇인가? (현재 글)**
- 문제를 데이터 문제로 바꾸기 (예정)
- 데이터 수집 (예정)
- 데이터 정제 (예정)
- 탐색적 데이터 분석 (예정)
- 시각화 (예정)
- 모델링 (예정)
- 평가 (예정)
- 결과 해석 (예정)
- 데이터 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [Drew Conway — The Data Science Venn Diagram](http://drewconway.com/zia/2013/3/26/the-data-science-venn-diagram)
- [Google — Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Hadley Wickham — R for Data Science](https://r4ds.hadley.nz/)
- [Stitch Fix — Multithreaded Engineering Blog](https://multithreaded.stitchfix.com/)
- [book-examples — data-science-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-science-101/ko)

Tags: DataScience, Introduction, Workflow, Analytics, Beginner

---
series: data-science-101
episode: 2
title: "Data Science 101 (2/10): 문제를 데이터 문제로 바꾸기"
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
  - ProblemFraming
  - Metrics
  - Workflow
  - Beginner
seo_description: 막연한 질문을 측정 가능한 데이터 질문으로 바꾸는 5단계 프레임을 설명합니다
last_reviewed: '2026-05-15'
---

# Data Science 101 (2/10): 문제를 데이터 문제로 바꾸기

이 글은 Data Science 101 시리즈의 두 번째 글입니다.

실무에서 데이터 작업이 느려지는 가장 흔한 이유는 도구 부족이 아닙니다. 질문이 흐릿한 상태로 출발했기 때문입니다. “왜 매출이 떨어졌지?”, “이탈이 늘었나?”, “이번 캠페인이 효과 있었나?” 같은 질문은 모두 중요하지만, 그대로는 데이터가 답하기 어렵습니다. 무엇을 측정할지, 어느 기간을 비교할지, 누구를 대상으로 볼지가 빠져 있기 때문입니다.

그래서 분석의 절반은 계산이 아니라 프레이밍입니다. 질문을 다시 써서 데이터가 실제로 답할 수 있는 형태로 바꾸는 일입니다. 이 글에서는 그 변환 과정을 다섯 단계로 정리하겠습니다.


![Data Science 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/02/02-01-concept-at-a-glance.ko.png)
*Data Science 101 2장 흐름 개요*
> 문제를 데이터 문제로 바꾸기의 핵심은 기능 이름이 아니라, 입력을 받는 경계에서 결과를 내보내는 경계까지 어떤 기준으로 데이터를 검증하고 처리할 것인가를 명확히 정하는 데 있습니다.

## 먼저 던지는 질문

- “왜 매출이 떨어졌지?” 같은 질문은 왜 그대로는 답하기 어려울까요?
- 지표, 기간, 대상 집단은 왜 문제 정의의 핵심일까요?
- 데이터가 답할 수 있는 질문은 어떤 형태여야 할까요?

## 이 글에서 배우는 내용

- 비즈니스 질문을 데이터 질문으로 바꾸는 5단계 틀
- 측정 가능한 지표를 고르는 방법
- 반증 가능한 가설을 쓰는 법
- 짧은 프레이밍 실습 흐름
- 자주 빠지는 다섯 가지 함정

## 왜 중요한가

질문이 흐릿하면 어떤 데이터를 가져와야 할지도 정할 수 없습니다. 팀마다 다른 기간을 보고, 다른 집단을 보고, 다른 지표를 쓰기 시작하면 같은 문제를 놓고도 전혀 다른 결론이 나옵니다. 반대로 문제를 한 문장으로 정확히 쓰면 쿼리도 빨라지고, 분석 범위도 줄고, 팀 간 오해도 크게 줄어듭니다.

좋은 데이터 팀일수록 질문을 다시 쓰는 일을 분석 전 단계의 부수 작업으로 보지 않습니다. 코드 리뷰만큼 중요한 질문 리뷰로 다룹니다.

> 정확한 질문 한 줄이 몇 주의 분석 시간을 아껴 주기도 합니다.

## 핵심 개념 한눈에 보기

## 핵심 용어

- **Metric**: DAU, 전환율, 매출처럼 실제로 측정할 수 있는 숫자입니다.
- **Window**: 최근 30일, 직전 7일처럼 비교할 시간 범위입니다.
- **Population**: 유료 구독자, 신규 가입자처럼 분석 대상 집단입니다.
- **Hypothesis**: 맞을 수도 틀릴 수도 있는 가설 문장입니다.
- **Counterfactual**: 변화가 없었다면 어떻게 되었을지를 상상하는 비교 기준입니다.

## 탐색적 데이터 분석 기법 비교

EDA(Exploratory Data Analysis)는 모델링 전에 데이터의 모양을 이해하는 단계입니다. 어떤 기법을 언제 써야 하는지 정리하면 분석이 훨씬 구체적으로 바뀝니다.

| 대상 | 도구 | 시각화 | 판단 기준 |
|---|---|---|---|
| 분포 | `describe()`, `hist()` | histogram, boxplot | 치우침, 이상치 여부 |
| 상관 | `corr()`, `scatter()` | scatter plot, heatmap | 선형 관계 강도 |
| 이상치 | IQR, Z-score | boxplot, scatter | 1.5*IQR 범위 논리 |
| 결측 | `isna().sum()`, `isna().mean()` | missing heatmap | 결측 비율, 패턴 |

예를 들어 분포를 볼 때는 평균보다 분위수를 먼저 확인하는 편이 안전합니다. 이상치가 많을 때 평균은 편향되기 쉽기 때문입니다.

## 파이썬 matplotlib/seaborn 시각화 예제

문제를 데이터 문제로 바꾸고 나면 다음 단계는 데이터를 실제로 확인하는 것입니다. Python의 matplotlib과 seaborn은 EDA에서 가장 많이 쓰는 시각화 라이브러리입니다.

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 데이터 로드
df = pd.read_csv("revenue_data.csv")
df["date"] = pd.to_datetime(df["date"])

# 1. 시계열 분포 확인
df.set_index("date")["revenue"].plot(figsize=(10, 4), title="Revenue over time")
plt.ylabel("Revenue")
plt.show()

# 2. 분포 확인 (histogram)
df["revenue"].hist(bins=30, edgecolor="black")
plt.title("Revenue distribution")
plt.xlabel("Revenue")
plt.show()

# 3. 상관관계 히트맵
sns.heatmap(df.select_dtypes("number").corr(), annot=True, cmap="coolwarm")
plt.title("Correlation heatmap")
plt.show()
```

이 예제는 시간에 따른 변화, 분포의 모양, 변수 간 상관을 빠르게 확인합니다. 문제를 데이터 문제로 바꾸는 과정에서 이런 시각화는 가설을 빠르게 검증하게 해 줍니다.

## 탐색적 데이터 분석 점검표

문제를 데이터 문제로 바꾸기 전에 확인해야 할 항목을 체크리스트로 정리하면 실수를 줄일 수 있습니다.

**문제 정의 단계:**

- [ ] 비즈니스 문제를 한 문장으로 적었습니다.
- [ ] 측정 가능한 지표를 명시했습니다.
- [ ] 비교 기간을 정했습니다.
- [ ] 대상 집단을 좋혔습니다.
- [ ] 반증 가능한 가설 문장으로 다시 썼습니다.

**데이터 확인 단계:**

- [ ] 필요한 데이터가 존재하는지 확인했습니다.
- [ ] 데이터 크기와 기간이 적절한지 판단했습니다.
- [ ] 결측치 비율을 확인했습니다.
- [ ] 이상치 여부를 확인했습니다.
- [ ] 측정 기준이 일관되는지 검토했습니다.

이 체크리스트는 문제를 데이터 문제로 바꾸는 과정에서 반복해서 확인해야 할 항목을 모은 것입니다. 실전에서는 이 목록을 부분적으로라도 문서화해 두는 편이 안전합니다.

## 전/후 비교

**Before**: “왜 매출이 떨어졌지?”라는 질문을 받고 어디서부터 봐야 할지 막막합니다. 사람마다 떠올리는 지표와 비교 구간도 달라집니다.

**After**: “최근 30일 동안 체험판을 제외한 유료 구독자의 월 매출이 직전 30일보다 5% 이상 감소했는가?”로 다시 씁니다. 그 순간 필요한 쿼리와 비교 방식이 거의 정해집니다.

## 실습: 5단계 프레이밍

### 1단계 — 막연한 질문을 그대로 적기

```text
"Revenue feels like it's dropping"
```

출발점은 대개 이렇게 모호합니다. 괜찮습니다. 중요한 것은 이 문장을 억지로 바로 분석하지 않는 것입니다. 먼저 지금 질문에 무엇이 빠져 있는지 드러내야 합니다.

### 2단계 — 지표를 고르기

```text
metric = monthly_revenue
```

지표는 분석의 중심축입니다. 매출인지, 활성 사용자 수인지, 주문 건수인지에 따라 필요한 데이터가 완전히 달라집니다. 그래서 보통은 지표를 가장 먼저 고릅니다.

### 3단계 — 기간을 고르기

```text
window = last 30 days vs previous 30 days
```

비교 기간이 다르면 결론도 쉽게 바뀝니다. 어떤 팀은 최근 7일을 보고, 어떤 팀은 월간 기준을 보면 논의가 엇갈릴 수밖에 없습니다. 기간은 질문 안에 명시되어야 합니다.

### 4단계 — 대상 집단을 좁히기

```text
population = paid subscribers (excluding trials)
```

전체 사용자를 한꺼번에 보면 중요한 패턴이 묻히기 쉽습니다. 무료 사용자와 유료 사용자를 섞거나, 체험판과 실제 고객을 섞으면 비교가 오염됩니다. 대상 집단을 좁히는 이유가 여기에 있습니다.

### 5단계 — 반증 가능한 문장으로 다시 쓰기

```text
"Paid-subscriber monthly revenue dropped more than 5% in the last 30 days versus the prior 30 days."
```

이제야 비로소 데이터가 답할 수 있는 질문이 됩니다. 맞는지 틀린지 확인할 수 있고, 필요한 집계도 분명합니다. 좋은 데이터 질문은 대부분 이 수준으로 구체적입니다.

**Expected output:** 지표·기간·대상 집단이 명시된 반증 가능한 질문 한 줄을 문서로 남깁니다.

## 이 코드에서 먼저 봐야 할 점

- 지표는 분석 전체를 잡아 주는 중심축입니다.
- 기간과 대상 집단을 명시해야 비교가 공정해집니다.
- 데이터가 답하려면 가설이 먼저 반증 가능해야 합니다.

## 자주 하는 실수 다섯 가지

1. **지표를 맨 마지막에 고르는 실수**: 분석이 계속 흔들립니다.
2. **팀마다 다른 기간을 쓰는 실수**: 같은 문제를 놓고도 불공정한 비교가 됩니다.
3. **대상 집단이 중간에 바뀌는 실수**: 추세가 섞여 원인을 읽기 어려워집니다.
4. **반증 불가능한 가설을 쓰는 실수**: 데이터가 답할 수 없는 질문이 됩니다.
5. **여러 질문을 한 번에 묻는 실수**: 답이 섞여 무엇이 원인인지 흐려집니다.

## 실무에서는 이렇게 나타납니다

좋은 데이터 팀은 모호한 요청을 받으면 바로 쿼리를 짜지 않습니다. 먼저 질문을 다시 씁니다. 어떤 팀은 이것을 질문 리뷰라고 부르고, 코드 리뷰만큼 엄격하게 다룹니다. 문제를 어떻게 정의했는지에 따라 이후 수집, EDA, 시각화, 모델링까지 모두 달라지기 때문입니다.

## 시니어는 이렇게 생각합니다

- 지표를 먼저 정해야 분석이 흔들리지 않습니다.
- 기간과 대상 집단은 문서에 명시해야 합니다.
- 반증 가능성은 질문 품질의 핵심 기준입니다.
- 질문 리뷰는 코드 리뷰만큼 중요합니다.
- 데이터가 답할 수 없다면 질문부터 다시 써야 합니다.

## 체크리스트

- [ ] 지표, 기간, 대상 집단을 분명하게 적을 수 있습니다.
- [ ] 반증 가능한 가설을 작성할 수 있습니다.
- [ ] counterfactual이 왜 필요한지 설명할 수 있습니다.
- [ ] 모호한 요청을 깔끔한 데이터 질문으로 바꿀 수 있습니다.

## 연습 문제

1. “이탈이 늘고 있다”를 5단계 프레임으로 다시 써 보세요.
2. 반증 불가능한 가설 3개를 적고, 각각을 반증 가능하게 고쳐 보세요.
3. 하나의 지표를 골라 기간이 달라질 때 결론이 어떻게 바뀌는지 적어 보세요.

## 정리 및 다음 글

데이터 분석은 답할 수 있는 질문에서만 시작됩니다. 문제를 데이터가 측정할 수 있는 형태로 바꾸는 일이 그만큼 중요합니다. 다음 글에서는 이렇게 정의한 질문을 뒷받침할 데이터를 실제로 어디서, 어떻게 수집할지 봅니다.

## 실무 확장: 문제를 측정 가능한 질문으로 바꾸는 프레이밍 템플릿

문제 프레이밍은 프로젝트 품질을 결정하는 초기 설계 단계입니다. 많은 팀이 "질문이 중요하다"는 말에는 동의하지만, 실제 문서에는 여전히 추상적인 요청이 남아 있는 경우가 많습니다. 그래서 실무에서는 요청을 그대로 받지 않고, 공통 템플릿으로 질문을 재작성합니다. 이 과정을 거치면 데이터 수집 범위가 줄고, 분석 속도는 빨라지며, 결과 해석의 충돌도 크게 줄어듭니다.

### 수집 방법 선택 전에 정리할 문제 프레임

| 항목 | 반드시 들어가야 할 내용 | 예시 |
| --- | --- | --- |
| 목표 | 무엇을 바꾸고 싶은가 | 유료 구독 해지율 감소 |
| 지표 | 무엇으로 측정하는가 | 30일 해지율, 재구독률 |
| 기간 | 언제를 비교하는가 | 최근 30일 vs 직전 30일 |
| 대상 | 누구를 포함/제외하는가 | 체험판 제외 유료 사용자 |
| 행동 | 결과로 무엇을 할 것인가 | 위험군 대상 리텐션 캠페인 |

이 표를 채우지 못하면 질문이 데이터 문제로 변환되지 않았다고 보는 편이 안전합니다. 특히 "대상"이 빠지면 분석 결과가 과도하게 일반화되기 쉽습니다.

### 요청 문장 개선 예시

- 개선 전: "요즘 결제가 줄어든 것 같은데 원인 좀 봐 주세요."
- 개선 후: "최근 4주 유료 사용자 결제액이 직전 4주 대비 7% 이상 감소했는지 확인하고, 감소가 확인되면 국가/디바이스/유입채널 기준으로 하위 세그먼트를 분해해 우선 대응 대상을 제안합니다."

개선 후 문장에는 측정 조건과 행동 조건이 함께 있습니다. 이 구조가 있어야 분석 결과가 보고서로 끝나지 않고 운영 작업으로 이어집니다.

### 파이썬 예시: 프레이밍 문장을 검증 가능한 조건으로 변환

```python
import pandas as pd

pay = pd.read_csv("payments.csv", parse_dates=["paid_at"])
now_start = pd.Timestamp("2026-05-01")
prev_start = pd.Timestamp("2026-04-01")

curr = pay[(pay["paid_at"] >= now_start) & (pay["paid_at"] < now_start + pd.Timedelta(days=30))]
prev = pay[(pay["paid_at"] >= prev_start) & (pay["paid_at"] < prev_start + pd.Timedelta(days=30))]

curr_amt = curr.query("plan_type == 'paid' and is_trial == 0")["amount"].sum()
prev_amt = prev.query("plan_type == 'paid' and is_trial == 0")["amount"].sum()
change = (curr_amt - prev_amt) / max(prev_amt, 1)

print({"current": curr_amt, "previous": prev_amt, "change_rate": round(change, 4)})
print("trigger_action:", change <= -0.07)
```

이 코드는 계산 그 자체보다 프레이밍을 코드화했다는 점이 중요합니다. 누구를 포함했는지, 기간이 무엇인지, 행동 트리거 임계값이 무엇인지가 드러납니다.

### 프레이밍 품질 점검 체크리스트

- 질문이 사실 확인형인지 원인 탐색형인지 구분했는가
- 지표가 단일 지표인지 복합 지표인지 정의했는가
- 반증 가능 조건(임계값, 비교 구간)이 있는가
- 데이터 미존재 시 대체 지표를 정했는가
- 결과를 받을 의사결정자와 회의 주기를 명시했는가

질문을 이렇게 구조화하면 "분석 잘하는 팀"이 아니라 "결정을 빠르게 만드는 팀"으로 전환됩니다. 데이터 과학의 성숙도는 코드 길이가 아니라, 문제 문장을 운영 가능한 규칙으로 바꾸는 능력에서 드러납니다.


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


## 처음 질문으로 돌아가기

- **“왜 매출이 떨어졌지?” 같은 질문은 왜 그대로는 답하기 어려울까요?**
  - 그대로는 `metric`, `window`, `population`이 빠져 있어서 같은 질문을 두고도 팀마다 전혀 다른 쿼리를 만들기 때문입니다. 본문에서 “Paid-subscriber monthly revenue dropped more than 5% in the last 30 days versus the prior 30 days.”로 다시 쓴 순간, 무엇을 집계할지가 비로소 고정됐습니다.
- **지표, 기간, 대상 집단은 왜 문제 정의의 핵심일까요?**
  - `monthly_revenue`, `last 30 days vs previous 30 days`, `paid subscribers (excluding trials)`처럼 세 축이 정해져야 비교 기준이 흔들리지 않습니다. 이 셋이 없으면 같은 매출 하락 질문도 무료 사용자 포함 여부나 주간·월간 비교에 따라 완전히 다른 결론이 나옵니다.
- **데이터가 답할 수 있는 질문은 어떤 형태여야 할까요?**
  - 데이터가 답할 수 있는 질문은 본문 5단계처럼 측정 가능하고 반증 가능한 한 문장이어야 합니다. 즉, 지표·기간·대상 집단이 명시되어 실제로 `pd.read_csv("revenue_data.csv")`나 SQL 집계로 맞는지 틀린지 확인할 수 있는 형태여야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Science 101 (1/10): Data Science란 무엇인가?](./01-what-is-data-science.md)
- **문제를 데이터 문제로 바꾸기 (현재 글)**
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

- [Google — Rules of Machine Learning (Rule #1)](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Cassie Kozyrkov — How to Ask Smart Questions](https://kozyrkov.medium.com/)
- [Stitch Fix — A/B Testing Lessons](https://multithreaded.stitchfix.com/)
- [Andrew Gelman — Statistical Modeling Blog](https://statmodeling.stat.columbia.edu/)
- [book-examples — data-science-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-science-101/ko)

Tags: DataScience, ProblemFraming, Metrics, Workflow, Beginner

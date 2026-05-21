---
series: data-science-101
episode: 6
title: "Data Science 101 (6/10): 시각화"
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
  - Visualization
  - Matplotlib
  - Seaborn
  - Beginner
seo_description: 데이터의 메시지에 맞는 차트 선택법과 축, 색상, 주석 활용 원칙 및 정직한 시각화를 위한 가이드를 상세히 정리합니다.
last_reviewed: '2026-05-15'
---

# Data Science 101 (6/10): 시각화

이 글은 Data Science 101 시리즈의 여섯 번째 글입니다.

시각화는 데이터를 예쁘게 꾸미는 작업이 아닙니다. 사람이 가장 빠르게 읽을 수 있는 형태로 결과를 다시 표현하는 작업입니다. 좋은 차트 하나가 설명 세 페이지를 줄여 주기도 하고, 반대로 잘못 고른 차트 하나가 완전히 다른 결정을 부르기도 합니다.

그래서 시각화의 핵심은 “무슨 차트 라이브러리를 쓰는가”보다 “무슨 메시지를 전달하려는가”에 있습니다. 이 글에서는 메시지와 차트를 연결하는 기본 지도, 그리고 차트를 정직하게 만드는 규칙들을 함께 정리하겠습니다.

## 먼저 던지는 질문

- 어떤 메시지에 어떤 차트를 써야 할까요?
- 같은 데이터를 두고도 왜 어떤 그래프는 이해를 돕고, 어떤 그래프는 오해를 만들까요?
- 축, 색상, 라벨은 왜 사소한 장식이 아니라 핵심 설계 요소일까요?

## 큰 그림

![Data Science 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/06/06-01-concept-at-a-glance.ko.png)

*Data Science 101 6장 흐름 개요*

시각화를 운영 시스템 속에서 올바르게 배치하려면 어떤 경계에서 무엇을 입력받고, 어디에서 검증하며, 어떤 신호를 남겨야 하는지 먼저 봐야 합니다.

> 시각화의 핵심은 기능 이름이 아니라, 입력을 받는 경계에서 결과를 내보내는 경계까지 어떤 기준으로 데이터를 검증하고 처리할 것인가를 명확히 정하는 데 있습니다.

## 이 글에서 배우는 내용

- 다섯 가지 메시지와 다섯 가지 차트의 기본 매핑
- 축, 색상, 라벨의 기본 원칙
- 독자를 오해하게 만드는 대표 패턴
- 5단계 시각화 실습 흐름
- 시각화에서 자주 생기는 함정 다섯 가지

## 왜 중요한가

데이터는 그림으로 봤을 때 훨씬 빨리 읽힙니다. 하지만 빠르게 읽힌다는 장점은 동시에 위험도 있습니다. 차트가 잘못 설계되면 사람은 그 오해도 빠르게 받아들입니다. 그래서 메시지와 차트를 올바르게 짝짓는 일은 분석의 마지막 품질 관리에 가깝습니다.

저는 좋은 시각화를 “예쁜 차트”보다 “오해를 덜 만드는 차트”로 정의하는 편이 더 실용적이라고 생각합니다.

> 시각화는 분석의 마지막 한 줄입니다.

## 핵심 개념 한눈에 보기

## 핵심 용어

- **Encoding**: 값을 위치, 길이, 색상 같은 시각 요소에 대응시키는 방식입니다.
- **Scale**: 선형 축인지 로그 축인지 같은 축 변환 방식입니다.
- **Faceting**: 여러 작은 차트를 나란히 배치해 비교하는 방식입니다.
- **Annotation**: 차트 위에 맥락을 덧붙이는 주석과 강조 표시입니다.
- **Colorblind-safe**: 색각 이상이 있는 독자도 구분하기 쉬운 팔레트입니다.

## 전/후 비교

**Before**: 3D 파이 차트로 비율을 보여 줍니다. 조각 크기를 정확히 비교하기 어려워서 중요한 차이를 읽기 힘듭니다.

**After**: 수평 막대 차트로 바꿉니다. 길이 비교가 쉬워져서 순위와 차이가 한눈에 들어옵니다.

## 실습: 5단계 시각화

### 1단계 — 분포는 히스토그램으로 보기

```python
import matplotlib.pyplot as plt
df["amount"].plot.hist(bins=30, title="amount distribution")
plt.show()
```

분포를 볼 때는 먼저 히스토그램이나 박스플롯을 떠올리는 편이 좋습니다. 평균이나 중앙값만으로는 보이지 않는 치우침과 긴 꼬리를 차트가 바로 드러내 줍니다.

### 2단계 — 비교는 막대 차트로 보기

```python
(
    df.groupby("country")["amount"]
      .sum()
      .sort_values()
      .plot.barh(title="revenue by country")
)
plt.show()
```

국가별 매출처럼 항목 간 비교가 목적일 때는 막대 차트가 가장 직관적입니다. 특히 수평 막대는 라벨이 긴 경우에도 읽기 편합니다.

### 3단계 — 추세는 선 차트로 보기

```python
df.groupby("order_date")["amount"].sum().plot(title="daily revenue")
plt.show()
```

시간 흐름이 핵심이면 선 차트가 자연스럽습니다. 날짜 축을 따라 상승과 하락, 계절성, 이벤트 전후 변화를 읽을 수 있기 때문입니다.

### 4단계 — 관계는 산점도와 faceting으로 보기

```python
import seaborn as sns
sns.relplot(
    data=df.sample(2000),
    x="quantity",
    y="amount",
    col="country",
    col_wrap=3,
)
```

두 수치형 변수의 관계를 볼 때는 산점도가 가장 강력합니다. 여기에 faceting을 더하면 국가별로 패턴이 어떻게 달라지는지도 함께 읽을 수 있습니다.

### 5단계 — 주석과 색상으로 맥락 더하기

```python
ax = df.groupby("order_date")["amount"].sum().plot()
ax.axvline(pd.Timestamp("2026-04-01"), color="red", linestyle="--", label="campaign")
ax.legend()
```

좋은 차트는 숫자만 그리지 않습니다. 중요한 이벤트 시점, 정책 변경, 캠페인 시작일 같은 맥락을 주석으로 표시해 주면 독자가 차트를 해석하는 시간이 크게 줄어듭니다.

**Expected output:** 분포·비교·추세 중 하나의 메시지에 맞는 차트 초안과 함께 해석에 필요한 주석 지점을 정리합니다.

## 이 코드에서 먼저 봐야 할 점

- 차트는 데이터보다 메시지에서 먼저 출발해야 합니다.
- 축의 스케일은 해석을 크게 바꿀 수 있습니다.
- 주석은 긴 설명 문단을 대신해 주는 실용적인 장치입니다.

## 자주 하는 실수 다섯 가지

1. **3D 차트를 쓰는 실수**: 비교가 어려워지고 왜곡도 커집니다.
2. **이중 축을 남용하는 실수**: 서로 다른 스케일이 오독을 만들기 쉽습니다.
3. **범주를 색으로만 구분하는 실수**: 색각 이상 독자에게 불친절합니다.
4. **막대 차트를 0이 아닌 값에서 시작하는 실수**: 차이를 과장하게 됩니다.
5. **라벨 없는 차트를 공유하는 실수**: 다음 주에는 아무도 다시 읽기 어렵습니다.

## 실무에서는 이렇게 나타납니다

실무에서는 Tableau나 Looker 같은 대시보드 도구와 Python 차트를 함께 씁니다. 주간 보고의 기본 단위가 대시보드인 팀도 많습니다. 중요한 것은 차트 수가 아니라, 몇 번의 스크롤 안에 의사결정이 가능하도록 설계되어 있는가입니다.

## 시니어는 이렇게 생각합니다

- 먼저 메시지를 쓰고, 그다음 차트를 고릅니다.
- 축과 라벨은 반드시 채웁니다.
- 기본 팔레트도 colorblind-safe를 우선합니다.
- 주석으로 독자가 맥락을 놓치지 않게 돕습니다.
- 대시보드는 세 화면 안에서 결정을 도와줘야 합니다.

## 체크리스트

- [ ] 다섯 가지 메시지와 차트의 기본 매핑을 알고 있습니다.
- [ ] 축과 라벨이 왜 중요한지 설명할 수 있습니다.
- [ ] colorblind-safe 팔레트 개념을 알고 있습니다.
- [ ] 주석을 넣어 해석을 돕는 습관이 있습니다.

## 연습 문제

1. 같은 데이터를 세 가지 차트로 그려 보고, 가장 명확한 차트를 골라 보세요.
2. 오해를 부르는 차트 하나를 찾아 더 정직한 형태로 고쳐 보세요.
3. 차트 세 개로 구성된 한 페이지 대시보드를 스케치해 보세요.

## 정리 및 다음 글

시각화는 분석을 사람이 읽을 수 있는 형태로 번역하는 작업입니다. 메시지와 차트를 올바르게 연결해야 결과가 결정으로 이어집니다. 다음 글에서는 정제된 데이터를 바탕으로 실제 예측 모델을 만드는 모델링 단계로 넘어가겠습니다.

## 실무 확장: 차트 선택 가이드와 설득 가능한 시각화 설계

시각화는 예쁜 결과물이 아니라 의사결정 인터페이스입니다. 같은 데이터라도 어떤 차트를 선택하느냐에 따라 독자의 해석이 달라집니다. 그래서 차트 설계는 취향 문제가 아니라 전달 목표 문제입니다. 이 섹션에서는 "무슨 메시지를 전할 것인가"를 기준으로 차트를 선택하는 표와 실전 코드 패턴을 정리합니다.

### 메시지-차트 선택 가이드

| 전달 목표 | 권장 차트 | 피해야 할 차트 | 이유 |
| --- | --- | --- | --- |
| 항목 간 비교 | 수평/수직 막대 | 3D 파이 | 길이 비교가 정확함 |
| 시간 추세 | 선 차트 | 누적 면적(초기 단계) | 변화 방향/속도 파악 용이 |
| 분포 확인 | 히스토그램, 박스플롯 | 평균만 표기 | 꼬리/이상치 확인 가능 |
| 관계 탐색 | 산점도 | 과밀 라인차트 | 변수 간 패턴 식별 용이 |
| 구성 비율 | 100% 누적 막대 | 파이 차트 과다 분할 | 카테고리 비교 용이 |

### matplotlib/seaborn 예시: 동일 데이터, 목적별 차트

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sales = pd.read_csv("sales.csv", parse_dates=["date"])

# 1) 추세
trend = sales.groupby("date", as_index=False)["revenue"].sum()
plt.figure(figsize=(10, 4))
plt.plot(trend["date"], trend["revenue"])
plt.title("Daily Revenue Trend")
plt.xlabel("Date")
plt.ylabel("Revenue")
plt.tight_layout()
plt.show()

# 2) 채널 비교
channel = sales.groupby("channel", as_index=False)["revenue"].sum().sort_values("revenue")
plt.figure(figsize=(8, 4))
plt.barh(channel["channel"], channel["revenue"])
plt.title("Revenue by Channel")
plt.tight_layout()
plt.show()
```

같은 데이터에서도 목적이 다르면 차트가 달라져야 합니다. 추세를 보여줄 때와 비교를 보여줄 때의 인코딩은 동일할 수 없습니다.

### 정직한 시각화를 위한 설계 규칙

- 막대 차트는 0축을 기본으로 사용합니다.
- 단위와 기간을 축 라벨에 반드시 명시합니다.
- 색상은 강조 하나, 나머지는 중립색으로 유지합니다.
- 범례가 없어도 읽히는 라벨 우선 배치를 사용합니다.
- 이벤트 시점(배포, 캠페인)을 세로선 주석으로 표시합니다.

### 차트 리뷰 체크리스트

- 이 차트가 답하는 질문이 한 문장으로 설명되는가
- 독자가 5초 안에 핵심 메시지를 읽을 수 있는가
- 축 왜곡이나 이중축 오해 가능성이 없는가
- 색각 이상 사용자도 구분 가능한가
- 캡션에 "그래서 무엇을 할지"가 적혀 있는가

### 보고서용 캡션 템플릿

"최근 4주간 모바일 채널 매출은 전주 대비 8% 하락했으며, 동일 기간 웹 채널은 2% 상승했습니다. 다음 주 예산 조정은 모바일 리텐션 캠페인 우선으로 권장합니다."

캡션이 행동 제안으로 닫히면 차트는 단순 시각 자료가 아니라 의사결정 도구가 됩니다.

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

### 추가 보강: 다음 반복에서 바로 쓰는 점검 질문

- 이번 결과를 다음 주에도 같은 방식으로 다시 계산할 수 있는가
- 세그먼트 기준이 바뀌면 결론이 얼마나 달라지는가
- 운영팀이 즉시 실행 가능한 행동 문장으로 정리되었는가

위 세 질문은 기술 난이도와 무관하게 모든 데이터 프로젝트에서 반복적으로 유효합니다. 프로젝트를 끝낼 때 이 질문에 답해 두면 다음 반복 주기의 출발 속도가 훨씬 빨라집니다.

### 마무리 보강: 운영 전 확인 포인트

최종 공유 전에 아래 항목을 마지막으로 점검합니다. 첫째, 결과 수치와 기준 기간이 문장 안에 함께 있는지 확인합니다. 둘째, 독자가 오해할 수 있는 축약 표현을 제거합니다. 셋째, 실행 오너와 재검토 날짜를 명시합니다. 이 세 가지는 글의 길이보다 품질을 크게 좌우하는 요소입니다.


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

- **어떤 메시지에 어떤 차트를 써야 할까요?**
  - 본문의 기준은 시각화를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **같은 데이터를 두고도 왜 어떤 그래프는 이해를 돕고, 어떤 그래프는 오해를 만들까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **축, 색상, 라벨은 왜 사소한 장식이 아니라 핵심 설계 요소일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Science 101 (1/10): Data Science란 무엇인가?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): 문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- [Data Science 101 (3/10): 데이터 수집](./03-data-collection.md)
- [Data Science 101 (4/10): 데이터 정제](./04-data-cleaning.md)
- [Data Science 101 (5/10): 탐색적 데이터 분석](./05-exploratory-data-analysis.md)
- **시각화 (현재 글)**
- 모델링 (예정)
- 평가 (예정)
- 결과 해석 (예정)
- 데이터 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [matplotlib — Tutorials](https://matplotlib.org/stable/tutorials/index.html)
- [seaborn — Tutorial](https://seaborn.pydata.org/tutorial.html)
- [Cole Knaflic — Storytelling with Data](https://www.storytellingwithdata.com/)
- [Tableau — Visual Best Practices](https://www.tableau.com/learn/articles/data-visualization-tips)
- [book-examples — data-science-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-science-101/ko)

Tags: DataScience, Visualization, Matplotlib, Seaborn, Beginner

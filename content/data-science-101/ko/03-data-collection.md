---
series: data-science-101
episode: 3
title: "Data Science 101 (3/10): 데이터 수집"
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
  - DataCollection
  - API
  - Database
  - Beginner
seo_description: 파일, API, DB, 로그에서 데이터를 모으는 방법과 출처 기록 원칙을 정리합니다
last_reviewed: '2026-05-15'
---

# Data Science 101 (3/10): 데이터 수집

이 글은 Data Science 101 시리즈의 세 번째 글입니다.

데이터 분석이라고 하면 모델링이나 시각화부터 떠올리기 쉽지만, 실제로는 수집 단계에서 이미 결과의 절반이 갈립니다. 누가 언제 어떤 경로로 데이터를 가져왔는지 모르면 같은 분석을 다시 할 수 없고, 결과를 검증하기도 어렵습니다. 팀원이 보내 준 엑셀 파일 하나로 시작한 분석이 나중에 왜 신뢰를 잃는지도 대개 여기서 시작됩니다.

이 글에서는 데이터를 수집하는 대표 경로 네 가지, 원본과 사본을 구분하는 습관, 출처를 기록하는 방법을 정리합니다. 수집은 단순히 데이터를 가져오는 단계가 아니라, 분석의 재현성을 만드는 기록 단계라는 점이 핵심입니다.


![Data Science 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/03/03-01-concept-at-a-glance.ko.png)
*Data Science 101 3장 흐름 개요*
> 데이터 수집의 핵심은 기능 이름이 아니라, 입력을 받는 경계에서 결과를 내보내는 경계까지 어떤 기준으로 데이터를 검증하고 처리할 것인가를 명확히 정하는 데 있습니다.

## 먼저 던지는 질문

- 분석에 필요한 데이터는 보통 어디서 가져올까요?
- 원본, 사본, 스냅샷은 왜 구분해야 할까요?
- 파일, API, 데이터베이스, 이벤트 로그는 각각 어떤 특성을 가질까요?

## 이 글에서 배우는 내용

- 파일, API, 데이터베이스, 이벤트 로그라는 네 가지 대표 출처
- 원본, 사본, 스냅샷의 차이
- 데이터 사전의 역할
- 5단계 수집 실습 흐름
- 수집 단계에서 자주 놓치는 함정 다섯 가지

## 왜 중요한가

수집 단계에서 빠진 행 하나, 잘못 가져온 기간 하나, 출처가 불분명한 파일 하나는 마지막 보고서까지 따라옵니다. 나중에 EDA를 잘하고 모델을 잘 만들어도 처음 데이터가 어디서 왔는지 설명할 수 없다면 결과를 믿기 어렵습니다.

현업에서 재현성은 거창한 시스템보다 작은 습관에서 시작됩니다. 원본 경로와 추출 시각을 적는 습관이 그 대표 사례입니다.

> 추적 가능한 데이터만 신뢰할 수 있습니다.

## 핵심 개념 한눈에 보기

## 핵심 용어

- **Source of truth**: 데이터의 권위 있는 원본입니다.
- **Snapshot**: 특정 시점에 고정해서 떠 놓은 사본입니다.
- **Schema**: 데이터의 컬럼 구조와 타입입니다.
- **Data dictionary**: 각 컬럼의 의미를 문서화한 표입니다.
- **Provenance**: 데이터의 출처와 생성 이력입니다.

## 피처 엔지니어링 기법 비교

데이터 수집 후에는 원본 그대로 모델에 넣기보다, 모델이 학습하기 좋은 형태로 변환하는 피처 엔지니어링 단계를 거칩니다. 주요 기법을 표로 비교하면 다음과 같습니다.

| 기법 | 적합 상황 | sklearn 함수 |
|---|---|---|
| 인코딩 (One-Hot) | 범주형 변수, cardinality 낮음 | `OneHotEncoder` |
| 인코딩 (Ordinal) | 순서가 있는 범주 | `OrdinalEncoder` |
| 스케일링 (Standard) | 정규분포 가정, 회귀/SVM | `StandardScaler` |
| 스케일링 (MinMax) | 범위 유지 필요, 신경망 | `MinMaxScaler` |
| 빈닝 (Binning) | 연속형을 구간으로 | `KBinsDiscretizer` |
| 교차 피처 | 변수 간 상호작용 포착 | `PolynomialFeatures` |

예를 들어 `country` 같은 범주형 변수는 One-Hot 인코딩으로 바꾸고, `age` 같은 숫자는 StandardScaler로 정규화하면 대부분의 모델에서 성능이 향상됩니다.

## 파이썬 sklearn ColumnTransformer 파이프라인 예제

피처 엔지니어링을 수동으로 하나씩 하면 코드가 길어지고 실수하기 쉽습니다. sklearn의 `ColumnTransformer`를 쓰면 여러 변환을 한 번에 파이프라인으로 묶을 수 있습니다.

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
import pandas as pd

# 샘플 데이터
df = pd.DataFrame({
    "age": [25, 30, 35, 40],
    "income": [50000, 60000, 70000, 80000],
    "country": ["KR", "US", "KR", "JP"],
    "churn": [0, 1, 0, 1]
})

X = df.drop("churn", axis=1)
y = df["churn"]

# 숫자형 컬럼과 범주형 컬럼 구분
numeric_features = ["age", "income"]
categorical_features = ["country"]

# ColumnTransformer로 변환 파이프라인 구성
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(drop="first"), categorical_features)
    ]
)

# 전처리 + 모델 파이프라인
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression())
])

pipeline.fit(X, y)
print("Pipeline 학습 완료")
```

이 파이프라인은 숫자형 변수는 표준화하고, 범주형 변수는 One-Hot 인코딩을 자동으로 적용한 뒤 모델까지 학습시킵니다. 데이터 수집 후 이런 전처리가 필수적이며, 파이프라인으로 관리하면 재현성이 크게 높아집니다.

## 피처 선택 vs 피처 생성

피처 엔지니어링은 크게 두 가지로 나뀜니다. 하나는 기존 피처 중에서 중요한 것만 골라내는 **피처 선택**(feature selection)이고, 다른 하나는 새로운 피처를 만드는 **피처 생성**(feature engineering)입니다.

**피처 선택의 목적:**

- 불필요한 변수를 제거해 모델 복잡도를 줄입니다.
- 과적합(overfitting)을 방지합니다.
- 학습 속도를 개선합니다.
- 해석 가능성을 높입니다.

**피처 생성의 목적:**

- 도메인 지식을 수치화합니다.
- 변수 간 상호작용을 포착합니다.
- 비선형 패턴을 선형 모델에서도 학습 가능하게 만듭니다.

예를 들어 `signup_date`를 그대로 쓰는 것보다, `days_since_signup` 같은 파생 변수로 바꾸면 모델이 패턴을 더 쉽게 학습할 수 있습니다. 반대로 상관이 거의 0인 변수는 제거하는 편이 모델 성능에 더 좋습니다.

## 전/후 비교

**Before**: 동료가 엑셀 파일을 보내 줍니다. 언제 뽑았는지, 어디서 추출했는지, 중간에 손으로 수정했는지 알 수 없습니다.

**After**: 같은 데이터를 웨어하우스에서 SQL로 다시 추출하고, 추출 시각과 해시를 기록합니다. 몇 달 뒤에도 같은 분석을 재현할 수 있습니다.

## 실습: 5단계 수집

### 1단계 — 파일에서 가져오기

```python
import pandas as pd
df = pd.read_csv("data/users-2026-05-04.csv")
print(df.shape)
```

파일 기반 수집은 가장 단순하지만 그만큼 위험하기도 합니다. 손으로 수정되기 쉽고 버전 추적도 약하기 때문입니다. 그래서 파일 이름에 날짜를 넣고 원본과 작업본을 분리하는 습관이 중요합니다.

### 2단계 — API에서 가져오기

```python
import requests
resp = requests.get("https://api.example.com/users", timeout=10)
resp.raise_for_status()
users = resp.json()
```

API 수집에서는 네트워크 실패, 인증, 응답 포맷 변경, rate limit을 항상 염두에 둬야 합니다. 한 번 성공했다고 끝이 아니라, 반복 수집에서도 안정적으로 동작하는지가 더 중요합니다.

### 3단계 — 데이터베이스에서 가져오기

```python
from sqlalchemy import create_engine
engine = create_engine("postgresql://user:pass@host/db")
df = pd.read_sql(
    "SELECT id, signup_at FROM users WHERE signup_at > '2026-01-01'",
    engine,
)
```

데이터베이스는 보통 가장 신뢰할 수 있는 원천입니다. 다만 운영 DB를 직접 조회하기보다 읽기 복제본이나 웨어하우스를 쓰는 편이 안전합니다. 어떤 쿼리로 가져왔는지도 함께 남겨야 합니다.

### 4단계 — 이벤트 로그에서 가져오기

```python
# JSONL — 한 줄에 하나의 JSON 이벤트
import json
with open("events.jsonl") as f:
    events = [json.loads(line) for line in f]
```

로그는 행동 데이터를 풍부하게 담지만 포맷 변경에 취약합니다. 이벤트 이름 하나, 필드 하나만 바뀌어도 분석이 조용히 깨질 수 있습니다. 그래서 로그 수집은 스키마 관리와 함께 봐야 합니다.

### 5단계 — 출처 기록하기

```python
import hashlib
import datetime

meta = {
    "source": "postgres://prod-replica/users",
    "fetched_at": datetime.datetime.utcnow().isoformat(),
    "row_count": len(df),
    "sha256": hashlib.sha256(
        pd.util.hash_pandas_object(df).values.tobytes()
    ).hexdigest()[:16],
}
print(meta)
```

출처, 시각, 행 수, 해시를 함께 남기면 나중에 같은 데이터였는지 빠르게 확인할 수 있습니다. 해시는 완벽한 메타데이터는 아니지만, 데이터가 바뀌었는지 감지하는 값싼 안전장치로 유용합니다.

**Expected output:** `source`, `fetched_at`, `row_count`, `sha256`가 담긴 provenance 메타데이터 한 건을 출력합니다.

## 이 코드에서 먼저 봐야 할 점

- 출처와 추출 시각은 항상 함께 기록해야 합니다.
- 해시는 데이터 변경 여부를 빠르게 확인하는 데 유용합니다.
- 원본은 수정하지 말고, 모든 변경은 스테이징 이후 단계에서 해야 합니다.

## 자주 하는 실수 다섯 가지

1. **원본 파일을 엑셀에서 바로 덮어쓰는 실수**: 되돌릴 방법이 사라집니다.
2. **API rate limit을 무시하는 실수**: 반복 수집 시 차단되거나 실패율이 높아집니다.
3. **스키마를 문서화하지 않는 실수**: 시간이 지나면 컬럼 의미가 증발합니다.
4. **로그 포맷 변경을 추적하지 않는 실수**: 분석이 조용히 깨집니다.
5. **민감 데이터를 개인 장비에 저장하는 실수**: 보안 사고로 이어질 수 있습니다.

## 실무에서는 이렇게 나타납니다

실무 데이터 팀은 수집 스크립트를 Airflow나 dbt 같은 파이프라인 안에서 돌립니다. 로드할 때마다 `load_id`, `fetched_at`, `source` 같은 메타데이터를 함께 붙이고, 데이터 사전은 Notion이나 Confluence에 유지합니다. 중요한 것은 도구 이름이 아니라 수집 과정을 반복 가능하고 설명 가능하게 만든다는 점입니다.

## 시니어는 이렇게 생각합니다

- 원본은 절대 수정하지 않습니다.
- 출처, 시각, 해시는 반사적으로 기록합니다.
- 스키마 변경은 알림으로 잡아야 합니다.
- 민감 데이터는 분석 전에 마스킹합니다.
- 데이터 사전은 가장 값비싼 문서 중 하나입니다.

## 체크리스트

- [ ] 대표적인 데이터 출처 네 가지를 알고 있습니다.
- [ ] snapshot이 무엇인지 설명할 수 있습니다.
- [ ] 데이터 사전을 작성할 수 있습니다.
- [ ] provenance를 기본값처럼 기록합니다.

## 연습 문제

1. 공개 API 하나를 골라 작은 샘플을 수집하고 메타데이터를 기록해 보세요.
2. 원본 → 스테이징 → 분석 흐름을 그림으로 그려 보세요.
3. 스키마 변경이 분석에 영향을 준 사례를 하나 적어 보세요.

## 정리 및 다음 글

데이터 수집은 단순한 입력 단계가 아니라 분석의 재현성을 만드는 기록 단계입니다. 원본, 스냅샷, 출처를 구분하는 습관이 있어야 이후 정제와 분석이 흔들리지 않습니다. 다음 글에서는 이렇게 모은 데이터를 실제로 어떻게 정제하고 검증하는지 살펴보겠습니다.

## 실무 확장: 데이터 수집 채널 비교와 안정적인 수집 패턴

데이터 수집은 단순 입력이 아니라 신뢰 체인을 만드는 단계입니다. 같은 분석도 수집 방식에 따라 재현성, 최신성, 운영비용이 크게 달라집니다. 이 섹션에서는 파일, API, DB, 이벤트 로그를 실무 관점에서 비교하고, 파이썬 기반 최소 수집 패턴을 정리합니다.

### 수집 채널 비교표

| 채널 | 장점 | 단점 | 권장 사용 시점 | 주의점 |
| --- | --- | --- | --- | --- |
| CSV/Parquet 파일 | 시작이 빠름, 이동 쉬움 | 버전 혼선, 수작업 오염 위험 | PoC, 외부 전달 데이터 | 원본 불변, 파일명 버전 규칙 |
| REST API | 최신 데이터 접근 용이 | 인증/쿼터/포맷 변경 리스크 | SaaS 통합, 외부 시스템 연동 | 재시도/백오프/스키마 검증 |
| 데이터베이스 | 질의 유연성, 신뢰도 높음 | 운영 DB 부하 가능성 | 정형 집계, 기준 데이터 조회 | 복제본 사용, 쿼리 기록 |
| 이벤트 로그 | 사용자 행동 맥락 풍부 | 스키마 드리프트 빈번 | 퍼널/세션/행동 분석 | 이벤트 버전 관리 필수 |

### API 수집 기본 패턴: 재시도와 검증

```python
import requests
import pandas as pd
from time import sleep

url = "https://api.example.com/v1/orders"
rows = []
for page in range(1, 6):
    for attempt in range(3):
        r = requests.get(url, params={"page": page}, timeout=10)
        if r.status_code == 200:
            data = r.json().get("items", [])
            rows.extend(data)
            break
        sleep(1.5 * (attempt + 1))

df = pd.DataFrame(rows)
required = {"order_id", "user_id", "amount", "created_at"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"schema mismatch: {missing}")

print(df.shape)
```

핵심은 성공 케이스가 아니라 실패 케이스 처리입니다. 수집은 실패를 전제로 설계해야 안정성이 올라갑니다.

### DB 수집 패턴: 쿼리와 메타데이터 동시 기록

```python
from sqlalchemy import create_engine
import pandas as pd
import datetime as dt

query = """
SELECT user_id, plan, amount, paid_at
FROM payments
WHERE paid_at >= '2026-05-01' AND paid_at < '2026-06-01'
"""

engine = create_engine("postgresql://reader:***@replica/warehouse")
df = pd.read_sql(query, engine)

meta = {
    "query_name": "payments_monthly_window",
    "fetched_at": dt.datetime.utcnow().isoformat(),
    "row_count": int(len(df)),
}
print(meta)
```

수집 결과만 저장하면 나중에 같은 결과를 재현하기 어렵습니다. 어떤 쿼리와 어떤 시점으로 가져왔는지 메타데이터를 함께 남겨야 합니다.

### 이벤트 로그 수집에서 자주 쓰는 방어 전략

- 이벤트 스키마 버전 컬럼을 필수화합니다.
- `event_name`과 `event_ts`가 없는 레코드는 격리 테이블로 보냅니다.
- 수집 파이프라인에서 일일 null 비율 알림을 둡니다.
- 키 컬럼(`user_id`, `session_id`) 누락률을 대시보드로 추적합니다.

### 수집 단계 운영 체크리스트

- 원본 저장소와 분석 저장소를 분리했는가
- 추출 쿼리와 파라미터를 버전 관리하는가
- API 오류율과 재시도 횟수를 기록하는가
- 수집 실패 시 알림과 재처리 경로가 있는가
- 민감 데이터 마스킹 규칙이 적용되는가

데이터 수집의 완성도는 "얼마나 많이 모았는가"가 아니라 "얼마나 다시 가져올 수 있는가"로 판단하는 편이 정확합니다. 이 기준이 있어야 이후 정제, EDA, 모델링까지 같은 기준으로 연결됩니다.


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


## 처음 질문으로 돌아가기

- **분석에 필요한 데이터는 보통 어디서 가져올까요?**
  - 이 글에서 정리한 기본 출처는 파일, API, 데이터베이스, 이벤트 로그 네 가지입니다. `pd.read_csv("data/users-2026-05-04.csv")`, `requests.get(...)`, `pd.read_sql(...)`, `events.jsonl` 예제가 각각 그 대표 경로를 보여 줬습니다.
- **원본, 사본, 스냅샷은 왜 구분해야 할까요?**
  - 동료가 준 엑셀 파일처럼 출처와 추출 시각이 없는 사본은 몇 달 뒤 다시 재현할 수 없기 때문입니다. 본문에서 강조한 `source of truth`, snapshot, 추출 SQL·해시 기록은 같은 분석을 같은 데이터로 다시 돌리기 위한 최소 계약입니다.
- **파일, API, 데이터베이스, 이벤트 로그는 각각 어떤 특성을 가질까요?**
  - 파일은 단순하지만 손수정과 버전 혼선에 약하고, API는 인증·rate limit·응답 포맷 변경을 신경 써야 하며, 데이터베이스는 가장 신뢰할 만하지만 쿼리와 읽기 경로를 남겨야 합니다. 이벤트 로그는 행동 데이터를 풍부하게 주는 대신 `events.jsonl`처럼 스키마가 바뀌면 분석이 조용히 깨지기 쉬운 출처입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Science 101 (1/10): Data Science란 무엇인가?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): 문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- **데이터 수집 (현재 글)**
- 데이터 정제 (예정)
- 탐색적 데이터 분석 (예정)
- 시각화 (예정)
- 모델링 (예정)
- 평가 (예정)
- 결과 해석 (예정)
- 데이터 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [requests — Quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [pandas — IO Tools](https://pandas.pydata.org/docs/user_guide/io.html)
- [Airflow — Concepts](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html)
- [Google — Data Validation for Machine Learning](https://research.google/pubs/data-validation-for-machine-learning/)
- [book-examples — data-science-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-science-101/ko)

Tags: DataScience, DataCollection, API, Database, Beginner

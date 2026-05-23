---
series: data-science-101
episode: 4
title: "Data Science 101 (4/10): 데이터 정제"
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
  - DataCleaning
  - Pandas
  - Quality
  - Beginner
seo_description: 결측, 중복, 이상치, 타입 문제를 다루는 데이터 정제의 기본 순서를 설명합니다
last_reviewed: '2026-05-15'
---

# Data Science 101 (4/10): 데이터 정제

이 글은 Data Science 101 시리즈의 네 번째 글입니다.

많은 사람이 데이터 작업의 핵심을 모델링이라고 생각하지만, 실제 시간을 가장 많이 잡아먹는 단계는 대개 정제입니다. 수집한 데이터를 그대로 쓰는 일은 거의 없습니다. 문자열이어야 할 값이 숫자로 들어오기도 하고, 날짜가 문자로 저장되기도 하고, 같은 사용자가 여러 번 들어오거나 결측치가 조용히 섞여 들어오기도 합니다.

정제는 지루한 사전 작업처럼 보일 수 있지만, 사실상 분석의 보험입니다. 입력이 불안정하면 그 위에 쌓은 시각화, 지표, 모델도 모두 흔들립니다. 이 글에서는 실무에서 가장 자주 만나는 네 가지 품질 문제와 이를 점검하는 기본 순서를 정리합니다.


![Data Science 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/04/04-01-concept-at-a-glance.ko.png)
*Data Science 101 4장 흐름 개요*
> 데이터 정제의 핵심은 기능 이름이 아니라, 입력을 받는 경계에서 결과를 내보내는 경계까지 어떤 기준으로 데이터를 검증하고 처리할 것인가를 명확히 정하는 데 있습니다.

## 먼저 던지는 질문

- 데이터 정제를 어떤 순서로 진행하면 좋을까요?
- 결측치, 중복, 이상치, 타입 불일치는 왜 가장 먼저 확인해야 할까요?
- `0`으로 채우기처럼 단순한 처리가 왜 위험할까요?

## 이 글에서 배우는 내용

- 가장 흔한 네 가지 데이터 품질 문제
- 결측치를 다루는 기본 전략
- 이상치를 탐지하는 가장 기초적인 방법
- 5단계 정제 실습 흐름
- 정제 단계에서 자주 생기는 함정 다섯 가지

## 왜 중요한가

오염된 입력에서 좋은 결과가 나오길 기대하기는 어렵습니다. 모델이 아무리 좋아도 입력이 틀리면 결과도 틀립니다. 그래서 정제는 미관을 위한 손질이 아니라, 분석 가능 여부를 결정하는 검증 단계입니다.

특히 입문 단계에서는 정제를 “모델링 전에 하는 귀찮은 준비”로 오해하기 쉽습니다. 하지만 실무에서는 정제가 부실한 프로젝트일수록 이후의 설명 비용과 디버깅 비용이 훨씬 더 커집니다.

> 정제는 분석을 가능하게 만드는 안전장치입니다.

## 핵심 개념 한눈에 보기

## 핵심 용어

- **Missing**: `NaN`, `None`, 빈 문자열처럼 값이 비어 있는 상태입니다.
- **Duplicate**: 같은 키를 가진 행이 여러 번 들어온 상태입니다.
- **Outlier**: 다른 값들과 통계적으로 멀리 떨어진 값입니다.
- **Type coercion**: 문자열을 숫자나 날짜로 변환하는 작업입니다.
- **Imputation**: 결측치를 일정한 규칙으로 채우는 전략입니다.

## 모델 선택 기준 비교

데이터 정제 후에는 적합한 모델을 고르는 단계가 왔습니다. 모델 선택은 단순히 정확도만 보는 것이 아니라, 데이터 크기, 해석 필요성, 속도, 정확도 간 균형을 모두 고려해야 합니다.

| 조건 | 데이터 크기 | 해석성 필요 | 속도 중요 | 최고 정확도 | 추천 모델 |
|---|---|---|---|---|---|
| 소규모, 해석 필수 | 작음 | 높음 | 보통 | 보통 | Logistic Regression, Decision Tree |
| 중규모, 균형 | 보통 | 보통 | 보통 | 높음 | Random Forest, Gradient Boosting |
| 대규모, 정확도 우선 | 크거나 매우 큼 | 낮음 | 느림 | 매우 높음 | XGBoost, LightGBM, Neural Network |
| 실시간 예측 | 중간 | 낮음 | 매우 빠름 | 보통 | Logistic Regression, Naive Bayes |

예를 들어 해석성이 중요하면 Decision Tree나 Logistic Regression이 적합하고, 정확도만 최대화하려면 XGBoost나 신경망을 고려하게 됩니다.

## 파이썬 여러 모델 비교 (cross_val_score)

데이터 정제가 끝나면 본격적으로 모델을 테스트해야 합니다. 한 가지 모델만 시도하기보다, 여러 모델을 교차 검증으로 비교하면 더 확신을 가지고 선택할 수 있습니다.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# 데이터 로드
X, y = load_iris(return_X_y=True)

# 모델 목록
models = {
    "Logistic Regression": LogisticRegression(max_iter=200),
    "Decision Tree": DecisionTreeClassifier(),
    "Random Forest": RandomForestClassifier()
}

# 각 모델의 교차 검증 점수
for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
    print(f"{name}: {np.mean(scores):.3f} (±{np.std(scores):.3f})")
```

이 예제는 세 가지 모델을 5-fold cross validation으로 비교합니다. 평균 정확도와 함께 표준편차도 출력하면 어느 모델이 안정적인지 판단할 수 있습니다. 데이터 정제 후에는 이런 비교를 기본적으로 수행하는 편이 안전합니다.

## 자유 점심은 없다 정리

모델 선택에서 가장 중요한 기준은 "자유 점심은 없다" 정리입니다. 이 정리는 **모든 문제에 전범위하게 가장 좋은 단일 모델은 존재하지 않는다**는 의미입니다.

특정 데이터에서 A 모델이 B보다 성능이 좋다더라도, 다른 데이터에서는 B가 더 좋을 수 있습니다. 그래서 실무에서는 한 가지 모델에 집착하기보다, 여러 모델을 실험하고 비교하는 일이 더 중요합니다.

**실무에서의 적용:**

- 한 가지 모델만 고집하지 말고, baseline 모델부터 시작해 점진적으로 복잡도를 높입니다.
- 모델 선택의 정답은 데이터에 달려 있습니다.
- 단순한 모델이 복잡한 모델보다 나을 때도 많습니다.
- 해석성, 속도, 정확도 사이의 trade-off를 항상 고려해야 합니다.

따라서 데이터 정제 후에는 모델 비교 단계를 반드시 거쳐야 하며, 단순한 모델부터 시작해 단계적으로 향상시키는 편이 안전합니다.

## 전/후 비교

**Before**: `signup_at` 컬럼이 문자열 상태라 날짜 비교가 틀린 결과를 냅니다. 최근 가입자만 보려 했는데 사전순 비교가 되어 버리는 식입니다.

**After**: `pd.to_datetime`으로 타입을 맞추고 나면 비교가 의도대로 동작합니다. 정제는 종종 이런 기본적인 오류를 바로잡는 작업입니다.

## 실습: 5단계 정제

### 1단계 — 타입 정리

```python
import pandas as pd
df = pd.read_csv("users.csv")
df["signup_at"] = pd.to_datetime(df["signup_at"], errors="coerce")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
```

타입 정리는 거의 모든 정제의 출발점입니다. 날짜가 문자열인 상태에서는 날짜 필터가 위험하고, 숫자가 문자열이면 집계 결과도 흔들립니다. `errors="coerce"`를 쓰면 변환 실패가 결측으로 드러나기 때문에 이상값 위치를 파악하기 쉽습니다.

### 2단계 — 중복 제거

```python
print("before:", len(df))
df = df.drop_duplicates(subset=["user_id"], keep="last")
print("after :", len(df))
```

중복은 단순히 지우는 것으로 끝내면 아쉬울 때가 많습니다. 왜 중복이 생겼는지 알아야 다음 수집 단계에서 같은 문제가 반복되지 않기 때문입니다. 정제는 임시 수리고, 원인 추적은 별도 과제라는 관점이 필요합니다.

### 3단계 — 결측 처리

```python
# Inspect missingness
print(df.isna().mean().sort_values(ascending=False).head())

# 전략: 중요 삭제, 선택 사항 채우기
df = df.dropna(subset=["user_id", "signup_at"])
df["country"] = df["country"].fillna("UNKNOWN")
```

결측치는 먼저 비율부터 봐야 합니다. 얼마나 비었는지, 특정 컬럼에 몰려 있는지, 중요한 컬럼인지에 따라 전략이 달라집니다. 핵심 키가 비었으면 보통 제거하고, 보조 컬럼은 채우는 편이 낫습니다.

### 4단계 — 이상치 탐지

```python
q1, q3 = df["amount"].quantile([0.25, 0.75])
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
df["amount_flag"] = ~df["amount"].between(lower, upper)
print(df["amount_flag"].mean())
```

이상치는 무조건 제거 대상이 아닙니다. 데이터 오류일 수도 있지만, 오히려 중요한 신호일 수도 있습니다. 그래서 보통은 먼저 표시한 뒤 도메인 맥락에서 검토합니다.

### 5단계 — 검증 리포트 만들기

```python
report = {
    "rows": len(df),
    "nulls": df.isna().sum().to_dict(),
    "outlier_rate": float(df["amount_flag"].mean()),
}
print(report)
```

정제가 끝났다면 무엇이 얼마나 바뀌었는지 남겨야 합니다. 행 수가 얼마나 줄었는지, 어떤 컬럼의 결측이 얼마나 남았는지, 이상치 비율이 얼마인지 적어 두면 다음 실행과 비교하기 쉬워집니다.

**Expected output:** 남은 행 수, 컬럼별 결측 수, 이상치 비율을 담은 검증 리포트를 얻습니다.

## 이 코드에서 먼저 봐야 할 점

- 타입 정리는 모든 정제의 출발점입니다.
- 결측 비율을 먼저 봐야 처리 전략을 정할 수 있습니다.
- 이상치는 바로 삭제하지 말고 먼저 표시해 두는 편이 안전합니다.

## 자주 하는 실수 다섯 가지

1. **결측치를 무조건 `0`으로 채우는 실수**: 평균과 분포가 쉽게 왜곡됩니다.
2. **중복을 조용히 지우는 실수**: 원인을 배우지 못해 같은 문제가 반복됩니다.
3. **이상치를 즉시 삭제하는 실수**: 실제 중요한 신호를 버릴 수도 있습니다.
4. **타입 변환 실패를 무시하는 실수**: 실패 지점을 드러내지 않으면 오류가 숨어 버립니다.
5. **정제 과정을 기록하지 않는 실수**: 재현 가능한 분석이 아니게 됩니다.

## 실무에서는 이렇게 나타납니다

실무 팀은 Great Expectations 같은 도구로 정제 규칙을 테스트하기도 합니다. 결측률이 일정 기준을 넘거나 허용하지 않은 값이 들어오면 파이프라인을 멈추게 만듭니다. 중요한 점은 정제를 사람의 감에만 맡기지 않고 규칙으로 끌어올린다는 것입니다.

## 시니어는 이렇게 생각합니다

- 결측률은 대시보드로 계속 봐야 합니다.
- 이상치는 표시 → 검토 → 결정 순서로 다룹니다.
- 정제 로직은 재사용 가능한 함수로 분리합니다.
- 원본은 건드리지 않고 복사본에서 작업합니다.
- 검증 규칙도 코드처럼 리뷰해야 합니다.

## 체크리스트

- [ ] 결측, 중복, 이상치, 타입을 어떤 순서로 볼지 알고 있습니다.
- [ ] imputation 전략을 설명할 수 있습니다.
- [ ] IQR이 무엇인지 알고 있습니다.
- [ ] 검증 리포트를 만들 수 있습니다.

## 연습 문제

1. 공개 데이터셋 하나를 골라 결측 비율을 출력해 보세요.
2. 이상치 플래그를 만든 뒤, 유지했을 때와 제거했을 때 차이를 비교해 보세요.
3. 타입 변환 실패가 분석을 깨뜨린 사례를 하나 문서화해 보세요.

## 정리 및 다음 글

데이터 정제는 조용하지만 가장 많은 결론을 떠받치는 작업입니다. 입력이 정리되어야 이후 EDA와 모델링도 믿을 수 있습니다. 다음 글에서는 이렇게 정리한 데이터를 실제로 읽고 이해하는 탐색적 데이터 분석을 봅니다.

## 실무 확장: 정제 패턴 라이브러리와 재사용 가능한 전처리 함수

정제는 프로젝트마다 새로 하는 일이 아니라, 반복 가능한 패턴을 축적하는 일입니다. 같은 도메인에서는 같은 오류가 반복됩니다. 날짜 형식 혼재, 금액 문자열, 중복 레코드, 결측치 규칙 부재는 거의 모든 데이터셋에서 다시 나타납니다. 그래서 실무 팀은 정제를 노트북 임시 코드로 끝내지 않고, 재사용 가능한 함수와 점검표로 관리합니다.

### 대표 정제 패턴 비교표

| 패턴 | 적용 조건 | 처리 방식 | 부작용 위험 | 기록 항목 |
| --- | --- | --- | --- | --- |
| 타입 강제 변환 | 문자열 숫자/날짜 혼재 | `to_numeric`, `to_datetime` | 변환 실패값 증가 | 실패 건수/비율 |
| 중복 축약 | 동일 키 다중 레코드 | 최신 기준 `drop_duplicates` | 과도 삭제 | 삭제 건수, 기준 컬럼 |
| 결측 대체 | 비핵심 컬럼 결측 | 규칙 기반 fill | 분포 왜곡 | 대체 규칙, 대체율 |
| 이상치 플래그 | 분포 꼬리 길음 | IQR/Z-score flag | 정상값 오탐 | 임계값, 플래그 비율 |
| 범주 정규화 | 표기 변형 다수 | 매핑 테이블 적용 | 매핑 누락 | 미매핑 목록 |

### pandas 전처리 코드: 규칙을 함수로 분리

```python
import pandas as pd


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["order_at"] = pd.to_datetime(out["order_at"], errors="coerce")
    out["amount"] = pd.to_numeric(out["amount"], errors="coerce")

    out = out.dropna(subset=["order_id", "user_id", "order_at"])
    out = out.drop_duplicates(subset=["order_id"], keep="last")

    q1, q3 = out["amount"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    out["amount_outlier"] = ~out["amount"].between(lo, hi)

    out["country"] = out["country"].fillna("UNKNOWN").str.upper()
    return out
```

함수화의 장점은 명확합니다. 같은 입력에 같은 출력이 보장되고, 코드 리뷰와 테스트가 가능해집니다.

### 정제 리포트 자동 생성 패턴

```python

def build_cleaning_report(raw: pd.DataFrame, clean: pd.DataFrame) -> dict:
    return {
        "raw_rows": int(len(raw)),
        "clean_rows": int(len(clean)),
        "dropped_rows": int(len(raw) - len(clean)),
        "null_rate_top5": clean.isna().mean().sort_values(ascending=False).head().to_dict(),
        "outlier_rate": float(clean["amount_outlier"].mean()) if "amount_outlier" in clean else 0.0,
    }
```

정제 자체만큼 중요한 것이 "무엇이 어떻게 바뀌었는지" 기록하는 일입니다. 팀 협업에서는 리포트가 정제 코드만큼 자주 읽힙니다.

### 정제 설계 원칙

- 원본 테이블은 절대 수정하지 않습니다.
- 정제 규칙은 자연어가 아니라 코드로 남깁니다.
- 삭제보다 플래그를 우선해 나중에 재검토 가능성을 남깁니다.
- 도메인 규칙(예: 금액 음수 허용 여부)을 문서와 코드에 동시에 반영합니다.
- 정제 변경은 모델 변경만큼 엄격하게 리뷰합니다.

### 품질 게이트 예시

- 핵심 키 결측률 0.1% 초과 시 파이프라인 실패
- 날짜 변환 실패율 1% 초과 시 경고
- 중복률 급증(전주 대비 +50%) 시 알림
- 이상치 플래그 비율 급증 시 원인 조사 티켓 자동 생성

정제는 데이터 과학의 "보이지 않는 기반"입니다. 기반이 단단해야 그 위에서 어떤 분석과 모델도 안정적으로 작동합니다.


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

- **데이터 정제를 어떤 순서로 진행하면 좋을까요?**
  - 이 글의 기본 순서는 타입 정리 → 중복 제거 → 결측 처리 → 이상치 표시 → 검증 리포트 작성입니다. `pd.to_datetime`, `drop_duplicates`, `dropna`/`fillna`, IQR 기반 `amount_flag`, 마지막 `report` 딕셔너리가 그 순서를 그대로 보여 줬습니다.
- **결측치, 중복, 이상치, 타입 불일치는 왜 가장 먼저 확인해야 할까요?**
  - 이 문제들은 모델 이전에 집계와 필터부터 틀리게 만들기 때문입니다. 예를 들어 `signup_at`이 문자열이면 날짜 비교가 깨지고, `user_id` 중복이나 `df.isna().mean()`으로 드러나는 결측을 놓치면 이후 지표와 피처가 처음부터 오염됩니다.
- **`0`으로 채우기처럼 단순한 처리가 왜 위험할까요?**
  - `0`은 종종 “값이 없음”이 아니라 실제 의미 있는 값이라서 결측과 진짜 0을 섞어 버립니다. 본문에서도 핵심 키는 `dropna(subset=[...])`로 제거하고, `country`처럼 보조 컬럼만 `fillna("UNKNOWN")`로 채우라고 구분한 이유가 여기에 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Science 101 (1/10): Data Science란 무엇인가?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): 문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- [Data Science 101 (3/10): 데이터 수집](./03-data-collection.md)
- **데이터 정제 (현재 글)**
- 탐색적 데이터 분석 (예정)
- 시각화 (예정)
- 모델링 (예정)
- 평가 (예정)
- 결과 해석 (예정)
- 데이터 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — Working with Missing Data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [Great Expectations — Data Quality Tests](https://docs.greatexpectations.io/docs/)
- [Wikipedia — Interquartile Range](https://en.wikipedia.org/wiki/Interquartile_range)
- [Hadley Wickham — Tidy Data](https://vita.had.co.nz/papers/tidy-data.pdf)
- [book-examples — data-science-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-science-101/ko)

Tags: DataScience, DataCleaning, Pandas, Quality, Beginner

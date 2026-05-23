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


![Data Science 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/08/08-01-concept-at-a-glance.ko.png)
*Data Science 101 8장 흐름 개요*
> 평가의 핵심은 기능 이름이 아니라, 입력을 받는 경계에서 결과를 내보내는 경계까지 어떤 기준으로 데이터를 검증하고 처리할 것인가를 명확히 정하는 데 있습니다.

## 먼저 던지는 질문

- 정확도가 높으면 정말 좋은 모델이라고 말할 수 있을까요?
- 분류 문제에서 precision, recall, F1, ROC AUC는 각각 무엇을 말해 줄까요?
- 회귀 문제에서 MAE, RMSE, R²는 어떻게 다를까요?

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

## 전/후 비교

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
# 위음성 비용이 위양성의 5배입니다
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

# 테네시, FP, FN, TP
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


평가 단계에서는 지표 간 우선순위를 사전에 고정하는 것이 중요합니다. 예를 들어 재현율을 우선할지 정밀도를 우선할지, 혹은 운영비용을 제한할지 결정하지 않으면 같은 수치도 팀마다 다르게 해석됩니다. 따라서 평가 문서는 점수표와 함께 "채택 기준"과 "배제 기준"을 한 문장으로 명시해야 합니다.

또한 동일 데이터로 재평가했을 때 같은 결론이 나오는지 재현성 확인 로그를 남기면, 모델 교체 시점 판단이 훨씬 명확해집니다.

## 처음 질문으로 돌아가기

- **정확도가 높으면 정말 좋은 모델이라고 말할 수 있을까요?**
  - 항상 그렇지는 않습니다. 본문 예시처럼 사기 탐지에서 accuracy 99%라도 recall이 5%면 실제 사기 대부분을 놓치고 있으므로, 높은 정확도만으로 좋은 모델이라고 결론 내릴 수 없습니다.
- **분류 문제에서 precision, recall, F1, ROC AUC는 각각 무엇을 말해 줄까요?**
  - precision은 `precision_score`가 보여 주듯 양성 예측의 신뢰도를, recall은 실제 양성 포착률을, F1은 그 둘의 균형을 나타냅니다. ROC AUC는 `model.predict_proba(X_test)[:, 1]`를 써서 임계값 하나에 덜 묶인 구분 능력을 읽게 해 주므로, 분류기의 전반적 분리력을 비교할 때 유용합니다.
- **회귀 문제에서 MAE, RMSE, R²는 어떻게 다를까요?**
  - MAE는 평균 절대 오차라 해석이 직관적이고, RMSE는 제곱 오차의 제곱근이라 큰 실수를 더 강하게 벌줍니다. `r2_score`는 오차 크기 자체보다 모델이 분산을 얼마나 설명했는지 보여 주므로, 세 지표는 같은 예측도 서로 다른 실패 양상을 드러냅니다.

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
- [book-examples — data-science-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-science-101/ko)

Tags: DataScience, Evaluation, Metrics, ScikitLearn, Beginner

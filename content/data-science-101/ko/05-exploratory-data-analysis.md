---
series: data-science-101
episode: 5
title: "Data Science 101 (5/10): 탐색적 데이터 분석"
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
  - EDA
  - Pandas
  - Statistics
  - Beginner
seo_description: 모델링 전에 데이터의 모양과 결측, 관계를 읽는 EDA 기본 흐름을 설명합니다
last_reviewed: '2026-05-15'
---

# Data Science 101 (5/10): 탐색적 데이터 분석

이 글은 Data Science 101 시리즈의 다섯 번째 글입니다.

탐색적 데이터 분석, 즉 EDA는 모델링 전에 잠깐 거치는 절차가 아닙니다. 데이터가 실제로 어떤 모양을 하고 있는지, 무엇이 비어 있는지, 어떤 변수들이 함께 움직이는지 먼저 읽어 보는 과정입니다. 이 단계를 성실하게 거치지 않으면 평균 하나만 보고 전형적인 값을 오해하거나, 상관관계를 인과로 착각하거나, 결측 패턴을 놓쳐 편향을 키우기 쉽습니다.

EDA를 잘한다는 말은 화려한 그래프를 많이 그린다는 뜻이 아닙니다. 데이터를 빠르게 읽되, 잘못 읽지 않는다는 뜻에 가깝습니다. 이 글에서는 입문자가 반복해서 써 볼 수 있는 5단계 EDA 흐름을 정리하겠습니다.


![Data Science 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/05/05-01-concept-at-a-glance.ko.png)
*Data Science 101 5장 흐름 개요*
> 탐색적 데이터 분석의 핵심은 기능 이름이 아니라, 입력을 받는 경계에서 결과를 내보내는 경계까지 어떤 기준으로 데이터를 검증하고 처리할 것인가를 명확히 정하는 데 있습니다.

## 먼저 던지는 질문

- 모델을 만들기 전에 데이터의 모양을 어떻게 빠르게 읽을 수 있을까요?
- 평균 하나만 보면 왜 자주 오해하게 될까요?
- 분포, 결측 패턴, 상관관계는 어떤 순서로 보는 편이 좋을까요?

## 이 글에서 배우는 내용

- EDA의 목적과 기본 순서
- 1차원 분포와 2차원 관계를 읽는 법
- 결측 패턴과 상관관계가 말해 주는 것
- 5단계 EDA 실습 흐름
- 입문자가 자주 빠지는 다섯 가지 함정

## 왜 중요한가

EDA가 약하면 잘못된 모델을 만들 가능성이 큽니다. 데이터가 스스로 보여 주는 분포와 패턴을 건너뛰고 바로 결론을 내리면, 나중에 모델 성능이 흔들리거나 해석이 빗나갔을 때 원인을 찾기 어려워집니다.

모델은 결국 자신이 받은 데이터를 흉내 냅니다. 그래서 입력을 제대로 읽지 못한 모델링은 빠르게 보일 뿐, 대개 더 비싼 우회를 만들게 됩니다.

> 모델은 결국 자신이 받은 데이터를 흉내 낼 뿐입니다.

## 핵심 개념 한눈에 보기

## 핵심 용어

- **Skewness**: 분포가 한쪽으로 얼마나 치우쳐 있는지 나타내는 정도입니다.
- **Outlier**: 다른 값들과 통계적으로 멀리 떨어진 값입니다.
- **Cardinality**: 범주형 값의 고유값 개수입니다.
- **Correlation**: 두 변수의 선형 관계 강도입니다.
- **MCAR / MAR / MNAR**: 결측이 생기는 방식의 분류입니다.

## 평가 지표 비교

EDA를 마친 후 모델을 학습시키면, 다음 단계는 모델의 성능을 평가하는 것입니다. 모델 평가는 단순히 정확도만 보는 것이 아니라, 문제 유형과 비즈니스 목표에 맞는 지표를 선택해야 합니다.

| 지표 | 공식 | 적합 상황 | 주의점 |
|---|---|---|---|
| Accuracy | (TP+TN) / Total | 균형 데이터 | 불균형 데이터에서 오해 |
| Precision | TP / (TP+FP) | FP 비용 클 때 | Positive 예측 신뢰도 |
| Recall | TP / (TP+FN) | FN 비용 클 때 | 실제 Positive 포착률 |
| F1-score | 2 * (P*R) / (P+R) | 균형 필요 | Precision과 Recall 조화 |
| AUC-ROC | ROC curve 아래 면적 | 임계값 비교 | 불균형 데이터에 강함 |
| RMSE | sqrt(mean((y-pred)²)) | 회귀, 큰 오차 강조 | 큰 오차에 민감 |
| MAE | mean(|y-pred|) | 회귀, 해석 쉽게 | 큰 오차에 덜 민감 |

예를 들어 암 진단 모델은 Recall이 중요하고 (암을 놓치면 안 됨), 스팸 필터는 Precision이 중요합니다 (정상 메일을 스팸으로 분류하면 안 됨).

## 파이썬 classification_report 예제

EDA와 모델 학습을 마치면 평가 단계에서 sklearn의 `classification_report`를 사용하면 여러 지표를 한 번에 확인할 수 있습니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

# 데이터 로드
X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 모델 학습
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# 예측
y_pred = model.predict(X_test)

# 평가 보고서
print(classification_report(y_test, y_pred, target_names=["Malignant", "Benign"]))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
```

이 예제는 유방암 데이터로 모델을 학습하고, Precision, Recall, F1-score를 클래스별로 출력합니다. Confusion Matrix도 함께 보면 어떤 클래스에서 오분류가 많은지 빠르게 파악할 수 있습니다. EDA 후에는 이런 평가 단계를 반드시 거쳐야 합니다.

## 지표 선택 가이드

EDA를 통해 데이터의 모양을 이해했다면, 모델 평가 단계에서는 어떤 지표를 봐야 할지 결정해야 합니다. 다음은 실무에서 자주 마주치는 상황별 가이드입니다.

**분류 문제 (Classification):**

1. **균형 데이터** → Accuracy로 시작하고, Precision/Recall/F1도 함께 확인
2. **불균형 데이터** → Accuracy 무시, Precision/Recall/F1 우선, AUC-ROC 추가
3. **False Positive 비용이 클 때** → Precision 우선 (예: 스팸 필터)
4. **False Negative 비용이 클 때** → Recall 우선 (예: 질병 진단)

**회귀 문제 (Regression):**

1. **큰 오차를 강하게 처벌하고 싶을 때** → RMSE
2. **해석 가능성을 우선할 때** → MAE
3. **비율 오차를 보고 싶을 때** → MAPE (Mean Absolute Percentage Error)

**실무에서의 주의점:**

- 단일 지표만 보지 말고 여러 지표를 함께 확인합니다.
- 테스트 세트는 학습 중에 절대 보지 말고, 최종 평가에만 사용합니다.
- Baseline 모델의 지표를 먼저 기록해 두고, 개선된 모델과 비교합니다.
- 비즈니스 지표와 모델 지표를 따로 추적하면, 모델은 좋아졌는데 비즈니스는 나빠진 경우를 발견할 수 있습니다.

EDA에서 데이터의 불균형을 파악했다면, 평가 단계에서는 그에 맞는 지표를 선택하는 것이 핵심입니다.

## 전/후 비교

**Before**: `mean`만 보고 대표값을 이해했다고 생각합니다. 하지만 분포가 한쪽으로 치우쳐 있거나 이상치가 많으면 이 평균은 실제 전형값을 잘 설명하지 못합니다.

**After**: 분포, 분위수, 이상치를 함께 봅니다. 그제야 값의 전체 모양이 보이고, 평균을 어디까지 믿어야 할지도 판단할 수 있습니다.

## 실습: 5단계 EDA

### 1단계 — 데이터 크기와 타입 보기

```python
import pandas as pd
df = pd.read_csv("orders.csv")
print(df.shape)
print(df.dtypes)
print(df.head())
```

가장 먼저 해야 할 일은 생각보다 단순합니다. 몇 행 몇 열인지, 각 컬럼 타입이 무엇인지, 실제 값이 어떻게 생겼는지 확인하는 것입니다. 이 단계만 해도 날짜가 문자열로 들어왔는지, 범주형처럼 보이지만 숫자인 컬럼이 있는지 바로 드러납니다.

### 2단계 — 1차원 분포 보기

```python
print(df["amount"].describe())
df["amount"].plot.hist(bins=30, title="amount")
```

`describe()`는 좋은 시작점이지만 답 자체는 아닙니다. 숫자 요약만으로는 치우침과 긴 꼬리를 놓치기 쉽기 때문에, 분포 그래프를 반드시 함께 보는 편이 좋습니다.

### 3단계 — 범주형 cardinality 보기

```python
print(df.select_dtypes("object").nunique().sort_values(ascending=False))
print(df["country"].value_counts(normalize=True).head())
```

범주형 컬럼은 고유값 개수를 꼭 봐야 합니다. 국가처럼 적당한 cardinality라면 다루기 쉽지만, 사용자 ID 수준으로 고유값이 많은 컬럼은 모델링 단계에서 바로 부담이 됩니다.

### 4단계 — 2차원 관계 보기

```python
import seaborn as sns
sns.scatterplot(data=df.sample(2000), x="quantity", y="amount")
```

변수 간 관계를 볼 때는 전체를 무조건 다 그리기보다 샘플링하는 편이 낫습니다. 속도도 빠르고 메모리도 덜 쓰며, 대부분의 패턴은 충분히 읽을 수 있습니다.

### 5단계 — 결측과 상관관계 보기

```python
print(df.isna().mean().sort_values(ascending=False).head())
print(df.select_dtypes("number").corr().round(2))
```

결측률은 어떤 컬럼이 불안정한지 보여 주고, 상관관계는 어떤 변수들이 함께 움직이는지 알려 줍니다. 다만 상관관계는 원인을 설명하지 않습니다. 여기서 읽을 수 있는 것은 관계의 방향과 강도이지 인과가 아닙니다.

**Expected output:** 분포 요약, 높은 cardinality 컬럼, 결측률 상위 컬럼을 한 번에 검토할 EDA 메모를 만듭니다.

## 이 코드에서 먼저 봐야 할 점

- `describe()`는 시작점일 뿐이며, 분포 그래프와 함께 봐야 합니다.
- correlation은 causation이 아닙니다.
- cardinality는 어떤 모델과 인코딩 전략이 맞을지 미리 알려 줍니다.

## 자주 하는 실수 다섯 가지

1. **평균만 보고 결론을 내리는 실수**: 분포의 모양을 놓치기 쉽습니다.
2. **상관관계를 인과로 읽는 실수**: 가장 흔한 해석 오류 중 하나입니다.
3. **전체 데이터를 그대로 시각화하는 실수**: 시간과 메모리를 불필요하게 씁니다.
4. **cardinality를 무시하는 실수**: 이후 인코딩 비용이 폭발합니다.
5. **결측이 MCAR라고 가정하는 실수**: 근거 없는 가정이 편향으로 이어질 수 있습니다.

## 실무에서는 이렇게 나타납니다

실무 팀은 모델 코드 옆에 EDA 노트북을 두고 함께 관리합니다. 주요 분포는 대시보드로 올려 두고, 시간이 지나 분포가 달라지는 데이터 드리프트도 같은 관점에서 봅니다. EDA는 한 번 하고 끝나는 작업이 아니라, 반복해서 다시 보는 관찰 루프에 가깝습니다.

## 시니어는 이렇게 생각합니다

- 순서는 분포 → 관계 → 결측 → 상관으로 잡는 편이 안정적입니다.
- 상관관계는 늘 조심스럽게 읽어야 합니다.
- EDA 노트북도 리뷰 가능한 산출물입니다.
- 샘플링은 시간을 아껴 주는 실용적인 습관입니다.
- 드리프트를 보기 위해 EDA를 주기적으로 다시 실행해야 합니다.

## 체크리스트

- [ ] `describe`와 분포를 함께 봅니다.
- [ ] cardinality가 무엇인지 알고 있습니다.
- [ ] correlation ≠ causation을 이해하고 있습니다.
- [ ] 결측 패턴을 분류한다는 개념을 알고 있습니다.

## 연습 문제

1. Iris나 Titanic 데이터셋으로 5단계 EDA를 직접 해 보세요.
2. 상관은 높지만 인과는 아닌 사례를 3개 적어 보세요.
3. 실제 프로젝트에서 cardinality가 모델 선택에 영향을 준 경험이나 가상의 예를 적어 보세요.

## 정리 및 다음 글

EDA는 데이터를 설득하기보다 먼저 듣는 시간입니다. 이 단계를 통해 데이터의 모양을 읽어야 이후 모델링과 해석도 제대로 서게 됩니다. 다음 글에서는 이렇게 읽은 내용을 다른 사람도 빠르게 이해할 수 있도록 시각화하는 방법을 살펴보겠습니다.

## 실무 확장: EDA 체크리스트와 시각화 기반 탐색 루틴

EDA는 감으로 하는 탐색이 아니라 반복 가능한 검증 루틴입니다. 많은 입문자가 EDA를 "그래프 몇 개 그리는 단계"로 오해하지만, 실무에서는 가설 후보를 만들고 데이터 위험을 조기에 찾는 품질 점검 단계로 사용합니다. 그래서 팀 단위로는 개인 취향 대신 체크리스트를 기준으로 EDA를 수행합니다.

### EDA 점검표(실무형)

| 영역 | 확인 질문 | 최소 산출물 |
| --- | --- | --- |
| 스키마 | 컬럼 타입이 기대와 일치하는가 | 타입 점검 표 |
| 규모 | 행/열 수, 고유 키 개수는 적절한가 | 데이터 크기 요약 |
| 분포 | 주요 수치형 분포가 치우쳤는가 | 히스토그램/박스플롯 |
| 결측 | 결측이 특정 세그먼트에 몰리는가 | 결측률 표 |
| 관계 | 목표 변수와 연관이 큰 피처는 무엇인가 | 상관 행렬/산점도 |
| 시간성 | 기간별 추세나 구조적 변화가 있는가 | 시계열 라인 차트 |

체크리스트의 목적은 "빠짐 방지"입니다. 경험이 많아도 프로젝트가 바쁘면 기본 검토가 누락되기 쉽습니다.

### matplotlib/seaborn으로 구성하는 기본 탐색 코드

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

orders = pd.read_csv("orders.csv", parse_dates=["order_date"])
print(orders.shape)
print(orders.isna().mean().sort_values(ascending=False).head())

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.histplot(orders["amount"], bins=30, ax=axes[0])
axes[0].set_title("Amount Distribution")

sns.boxplot(data=orders, x="channel", y="amount", ax=axes[1])
axes[1].set_title("Amount by Channel")
plt.tight_layout()
plt.show()
```

이 루틴은 "분포-세그먼트" 두 축을 빠르게 확인하는 데 유용합니다. 분포 왜곡과 채널별 차이를 동시에 파악할 수 있습니다.

### 상관관계 해석 시 주의할 점

- 상관계수 절대값이 높아도 인과를 의미하지 않습니다.
- 집계 단위가 바뀌면 상관 구조도 쉽게 바뀝니다.
- 시간 지연이 있는 변수는 단순 동시점 상관으로 해석하면 오류가 납니다.

### EDA 결과를 문장으로 남기는 템플릿

- 관찰: "모바일 채널의 주문 금액 중앙값이 웹 대비 낮습니다."
- 근거: "boxplot 기준 중앙값 약 18% 차이"
- 가설: "모바일 결제 플로우의 이탈 가능성"
- 다음 액션: "모바일 체크아웃 단계 로그 추가 수집"

이 구조를 지키면 EDA 결과가 단순 관찰에서 끝나지 않고 다음 분석 행동으로 이어집니다.

### 탐색 루틴 자동화 아이디어

- 일별 `profile report` 생성으로 분포 드리프트 감지
- 핵심 지표의 분위수 변화 알림
- 신규 범주값 유입 감지(카디널리티 급증)
- 결측률 임계치 초과 시 Slack 알림

EDA는 일회성 과제가 아니라 운영 관찰 루프입니다. 초기 프로젝트뿐 아니라 배포 이후 데이터 드리프트 점검에도 동일한 프레임을 반복 적용해야 안정적인 의사결정이 가능합니다.

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


## 처음 질문으로 돌아가기

- **모델을 만들기 전에 데이터의 모양을 어떻게 빠르게 읽을 수 있을까요?**
  - 본문의 기준은 탐색적 데이터 분석를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **평균 하나만 보면 왜 자주 오해하게 될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **분포, 결측 패턴, 상관관계는 어떤 순서로 보는 편이 좋을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Science 101 (1/10): Data Science란 무엇인가?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): 문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- [Data Science 101 (3/10): 데이터 수집](./03-data-collection.md)
- [Data Science 101 (4/10): 데이터 정제](./04-data-cleaning.md)
- **탐색적 데이터 분석 (현재 글)**
- 시각화 (예정)
- 모델링 (예정)
- 평가 (예정)
- 결과 해석 (예정)
- 데이터 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — Descriptive Statistics](https://pandas.pydata.org/docs/user_guide/basics.html#descriptive-statistics)
- [seaborn — Tutorial](https://seaborn.pydata.org/tutorial.html)
- [Wikipedia — Missing Data Patterns](https://en.wikipedia.org/wiki/Missing_data)
- [Tukey — Exploratory Data Analysis](https://archive.org/details/exploratorydataa00tuke_0)
- [book-examples — data-science-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-science-101/ko)

Tags: DataScience, EDA, Pandas, Statistics, Beginner

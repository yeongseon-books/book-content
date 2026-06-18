---
title: "바이브코딩을 위한 데이터 사이언스 기초 (7/10): AI가 모델을 골라줬는데 맞는 선택인지"
series: data-science-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- DataScience
- AI코딩
seo_description: "바이브코딩 시대, AI가 선택한 머신러닝 모델이 적절한 선택인지 검토하는 방법, 베이스라인부터 시작해야 하는 이유를 정리합니다"
---

# 바이브코딩을 위한 데이터 사이언스 기초 (7/10): AI가 모델을 골라줬는데 맞는 선택인지

이 글은 바이브코딩을 위한 데이터 사이언스 기초 시리즈의 7번째 글입니다.

AI 코딩 도구에게 "이 데이터로 이탈 예측 모델 만들어줘"라고 요청했습니다. AI가 즉시 XGBoost 모델 코드를 작성해주고, 정확도 94%라는 결과가 나왔습니다. 멋져 보입니다. 그런데 여기서 중요한 질문이 빠졌습니다. "94%가 좋은 건지 나쁜 건지 어떻게 알죠?"

AI가 모델을 골라줄 때 가장 먼저 확인해야 할 것이 있습니다. 바로 베이스라인(baseline)입니다. 베이스라인은 "항상 가장 흔한 답만 찍는 모델"입니다. 만약 전체 데이터에서 95%가 이탈하지 않는다면, 모든 사람을 "이탈 안 함"으로 예측하는 바보 모델도 정확도 95%가 됩니다. AI가 만든 XGBoost 모델이 94%라면 베이스라인보다 못한 겁니다.

또 다른 함정은 데이터 누수(data leakage)입니다. AI가 전처리와 모델을 따로 만들면, 테스트 데이터의 정보가 전처리 단계에 새어 들어가서 성능이 실제보다 좋아 보일 수 있습니다. 예를 들어 전체 데이터로 표준화(StandardScaler)를 먼저 적용하고 그 뒤에 train/test를 나누면 테스트 데이터의 통계가 이미 학습에 반영된 것입니다.

바이브코딩에서 AI에게 모델링을 맡길 때 세 가지를 반드시 요청해야 합니다. 첫째, 베이스라인 성능을 먼저 계산해줘. 둘째, 전처리와 모델을 Pipeline으로 묶어줘 (데이터 누수 방지). 셋째, 교차 검증으로 흔들림을 확인해줘.

> AI가 만든 모델 점수는 베이스라인과 비교하기 전까지는 의미가 없습니다.

---

## 이 글에서 다룰 문제
- AI가 XGBoost나 Random Forest를 선택했는데 좋은 선택인지 어떻게 알 수 있을까요?
- 베이스라인이 왜 반드시 필요한가요?
- AI가 만든 모델에서 데이터 누수가 있는지 어떻게 확인하나요?
- 교차 검증을 AI에게 요청하면 무엇이 달라질까요?
- 정확도 외에 어떤 지표를 함께 봐야 할까요?

## AI에게 모델링을 요청할 때 필수 요소

```python
# 좋지 않은 요청
"""
이 데이터로 이탈 예측 모델 만들어줘
"""

# 필수 요소를 포함한 요청 (좋음)
"""
이 데이터로 이탈 예측 모델을 만들어줘. 다음 순서로 진행해줘:
1. 먼저 DummyClassifier로 베이스라인 성능 계산 (most_frequent 전략)
2. 전처리(StandardScaler, OneHotEncoder)와 모델을 sklearn Pipeline으로 묶어줘
3. train/test 분리는 stratify=y 옵션 포함
4. 5-fold 교차 검증으로 평균 점수와 표준편차 계산
5. 베이스라인 대비 모델 개선 폭을 출력해줘
6. 정확도(accuracy) 외에 precision, recall, F1도 함께 출력해줘
"""

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.dummy import DummyClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd

df = pd.read_csv("churn.csv")
X = df.drop(columns=["churn"])
y = df["churn"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 1. 베이스라인 먼저
base = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
baseline_score = accuracy_score(y_test, base.predict(X_test))
print(f"베이스라인 정확도: {baseline_score:.3f}")

# 2. Pipeline으로 누수 방지
num_cols = X.select_dtypes("number").columns.tolist()
cat_cols = X.select_dtypes("object").columns.tolist()

pre = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
])
model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])

# 3. 교차 검증
cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy")
print(f"교차 검증 정확도: {cv_scores.mean():.3f} (±{cv_scores.std():.3f})")

# 4. 최종 평가
model.fit(X_train, y_train)
print(f"테스트 정확도: {accuracy_score(y_test, model.predict(X_test)):.3f}")
print(f"베이스라인 대비 개선: {accuracy_score(y_test, model.predict(X_test)) - baseline_score:.3f}")
print(classification_report(y_test, model.predict(X_test)))
```

## 모델 선택 기준: AI가 복잡한 모델을 제안할 때 검토할 것

AI는 종종 XGBoost나 Neural Network 같은 복잡한 모델을 제안합니다. 하지만 항상 옳은 선택이 아닙니다:

| 상황 | AI 추천 모델 | 실제 더 좋을 수 있는 선택 |
|---|---|---|
| 데이터가 적고(< 1000행), 해석 필요 | XGBoost | Logistic Regression |
| 빠른 베이스라인 필요 | Random Forest | DummyClassifier → Logistic Regression |
| 비즈니스 규칙 설명 필요 | Neural Network | Decision Tree |
| 불균형 데이터 | 기본 정확도 최적화 | class_weight="balanced" + Recall |

## Pipeline이 왜 중요한가: 데이터 누수 방지

AI가 전처리와 모델을 따로 작성하면 데이터 누수가 생길 수 있습니다:

```python
# 데이터 누수 있음 (잘못된 방법)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # 전체 데이터로 fit
X_train, X_test = train_test_split(X_scaled)  # 나중에 split

# 데이터 누수 없음 (올바른 방법 - Pipeline 사용)
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression())
])
pipeline.fit(X_train, y_train)  # train에서만 fit
pipeline.score(X_test, y_test)  # test에서 평가
```

AI에게 "Pipeline으로 묶어줘"라고 요청하면 이 문제를 자동으로 방지할 수 있습니다.

## Before / After

**Before**: AI에게 "이탈 예측 모델 만들어줘"라고 했더니 XGBoost 모델이 나왔고 정확도 94%가 나왔습니다. 팀에 보고했다가 나중에 베이스라인(가장 많은 클래스만 예측)이 95%라는 것을 알았습니다. AI가 만든 모델이 바보 모델보다 못했습니다.

**After**: "베이스라인부터 시작하고, Pipeline으로 전처리와 모델을 묶고, 교차 검증으로 흔들림을 확인해줘"라고 요청했습니다. 베이스라인 95%, 로지스틱 회귀 97%, XGBoost 98.5%로 개선 과정을 명확히 확인했습니다.

## 바이브코딩할 때 자주 하는 실수
| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 베이스라인 없이 모델 만들기 | 개선 여부를 판단할 수 없음 | DummyClassifier로 베이스라인 먼저 |
| Pipeline 없이 전처리와 모델 분리 | 데이터 누수로 성능 과장 | Pipeline으로 반드시 묶기 |
| 정확도만 확인 | 불균형 데이터에서 오해 | precision, recall, F1 함께 확인 |
| 교차 검증 없이 한 번만 평가 | 운이 좋은 결과를 실력으로 착각 | 5-fold 교차 검증 필수 |

## AI에게 데이터 분석 요청하는 팁

AI에게 모델링을 요청할 때 이 순서를 프롬프트에 포함하면 신뢰할 수 있는 결과를 얻을 수 있습니다:

1. **베이스라인 먼저**: "DummyClassifier(most_frequent)로 베이스라인 계산"
2. **Pipeline 사용**: "전처리와 모델을 sklearn Pipeline으로 묶어줘"
3. **데이터 분리**: "train/test 분리는 stratify=y 포함"
4. **교차 검증**: "5-fold CV로 평균과 표준편차 계산"
5. **지표 다양화**: "accuracy 외에 precision, recall, F1, AUC 포함"
6. **개선 폭 명시**: "베이스라인 대비 개선폭을 출력해줘"

## 운영 체크리스트
- [ ] AI가 만든 모델 전에 베이스라인을 계산합니다
- [ ] 전처리와 모델이 Pipeline으로 묶여 있는지 확인합니다
- [ ] train/test 분리가 모든 전처리 이전에 이루어졌는지 확인합니다
- [ ] 교차 검증으로 모델 성능의 안정성을 확인합니다
- [ ] 정확도 외에 비즈니스 문제에 맞는 지표도 확인합니다
- [ ] 베이스라인 대비 실제 개선 폭을 기록합니다

## 처음 질문으로 돌아가기

"AI가 모델을 골라줬는데 그게 맞는 선택인지 어떻게 알 수 있나요?"

세 가지를 확인하면 됩니다. 첫째, 베이스라인(가장 단순한 기준)보다 나은가? 둘째, Pipeline으로 데이터 누수 없이 만들어졌는가? 셋째, 교차 검증으로 결과가 안정적인가? 이 세 가지를 통과한 모델이라면 AI가 선택한 모델을 믿을 수 있습니다.

## 정리

AI에게 모델링을 맡길 때 "베이스라인, Pipeline, 교차 검증"을 항상 요청하면 됩니다. AI는 복잡한 모델을 쉽게 만들어주지만, 그게 실제로 의미 있는 개선인지는 베이스라인과 비교해야 알 수 있습니다. 다음 글에서는 AI 모델의 성능이 진짜 좋은 건지, 정확도 숫자에 속지 않는 방법을 다룹니다.

## 참고 자료
### 공식 문서
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
### 관련 시리즈
- [Machine Learning 101](../../machine-learning-101/ko/)
- [Statistics 101](../../statistics-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 데이터 사이언스 기초 (1/10): AI에게 데이터 분석 맡기기 전에 알아야 할 것](./01-what-is-data-science.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (2/10): 비즈니스 질문을 데이터 질문으로 바꾸는 법](./02-problem-to-data-problem.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (3/10): AI에게 줄 데이터를 어떻게 모을지](./03-data-collection.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (4/10): AI가 더러운 데이터로 분석하면 결과도 더럽다](./04-data-cleaning.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (5/10): AI에게 EDA 시키기 전에 알아야 할 것](./05-exploratory-data-analysis.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (6/10): AI가 만든 차트가 오해를 부를 때](./06-visualization.md)
- **바이브코딩을 위한 데이터 사이언스 기초 (7/10): AI가 모델을 골라줬는데 맞는 선택인지 (현재 글)**
- [바이브코딩을 위한 데이터 사이언스 기초 (8/10): AI 모델의 성능이 진짜 좋은 건지 평가하기](./08-evaluation.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (9/10): AI가 준 결과를 비즈니스에 설명하려면](./09-result-interpretation.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (10/10): AI와 함께 데이터 프로젝트 처음부터 끝까지](./10-data-project-end-to-end.md)
<!-- toc:end -->

Tags: 바이브코딩, DataScience, AI코딩, Modeling, MachineLearning

---
series: data-science-101
episode: 7
title: "Data Science 101 (7/10): 모델링"
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
  - Modeling
  - ScikitLearn
  - MachineLearning
  - Beginner
seo_description: 베이스라인부터 첫 분류 모델까지 안전하게 시작하는 모델링 기본 흐름을 설명합니다
last_reviewed: '2026-05-15'
---

# Data Science 101 (7/10): 모델링

이 글은 Data Science 101 시리즈의 일곱 번째 글입니다.

모델링은 데이터 작업에서 가장 눈에 띄는 단계입니다. 그래서 입문자는 복잡한 알고리즘부터 배우고 싶어집니다. 하지만 실무에서는 화려한 모델보다 먼저 확인해야 할 것이 있습니다. 아주 단순한 기준선, 즉 베이스라인입니다. 기준선이 없으면 지금 만든 모델이 정말 나아졌는지조차 말할 수 없습니다.

좋은 모델링의 출발점은 복잡함이 아니라 비교 가능성입니다. 무엇과 비교하는지, 학습과 평가 데이터를 어떻게 나누는지, 전처리 과정에서 누수가 없는지, 한 번의 우연한 결과를 실력으로 착각하지 않는지가 더 중요합니다. 이 글에서는 첫 지도 학습 모델을 안전하게 만드는 기본 흐름을 정리하겠습니다.

## 먼저 던지는 질문

- 첫 모델을 만들 때 왜 베이스라인부터 시작해야 할까요?
- train/test 분리는 무엇을 막아 주는 장치일까요?
- 전처리와 모델을 하나의 Pipeline으로 묶는 이유는 무엇일까요?

## 큰 그림

![Data Science 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/07/07-01-concept-at-a-glance.ko.png)

*Data Science 101 7장 흐름 개요*

모델링를 운영 시스템 속에서 올바르게 배치하려면 어떤 경계에서 무엇을 입력받고, 어디에서 검증하며, 어떤 신호를 남겨야 하는지 먼저 봐야 합니다.

> 모델링의 핵심은 기능 이름이 아니라, 입력을 받는 경계에서 결과를 내보내는 경계까지 어떤 기준으로 데이터를 검증하고 처리할 것인가를 명확히 정하는 데 있습니다.

## 이 글에서 배우는 내용

- 지도 학습 모델링의 기본 흐름
- 베이스라인 모델의 역할
- train/test 분리 원칙
- 5단계 모델링 실습
- 입문자가 자주 하는 실수 다섯 가지

## 왜 중요한가

베이스라인이 없는 모델은 잘했다는 말도, 못했다는 말도 하기 어렵습니다. 복잡한 모델이 95% 정확도를 냈더라도 가장 단순한 기준선이 96%라면 그 시도는 개선이 아니라 퇴행입니다. 그래서 모델링의 진짜 출발선은 늘 기준선입니다.

실무에서는 베이스라인이 단순한 예비 단계가 아니라, 이후의 모든 실험을 해석하게 만드는 기준점입니다. 그 기준이 없으면 숫자는 있어도 판단은 없습니다.

> 모든 모델은 결국 베이스라인과 경쟁합니다.

## 핵심 개념 한눈에 보기

## 핵심 용어

- **Baseline**: 항상 다수 클래스만 예측하는 것처럼 가장 단순한 기준선입니다.
- **Train/test split**: 학습용 데이터와 평가용 데이터를 분리하는 방식입니다.
- **Cross-validation**: 데이터를 여러 폴드로 나누어 반복 평가하는 방법입니다.
- **Overfitting**: 학습 데이터에는 잘 맞지만 테스트 데이터에는 약한 상태입니다.
- **Pipeline**: 전처리와 모델을 하나의 객체로 묶는 방식입니다.

## Before / After

**Before**: 복잡한 모델을 만들었더니 정확도 95%가 나옵니다. 성능이 좋아 보이지만, 베이스라인이 96%였다는 사실을 나중에 알게 됩니다.

**After**: 먼저 베이스라인 96%를 기록합니다. 그 위를 넘는지 확인하면서 모델링을 진행하니, 비교 기준이 분명해집니다.

## 실습: 5단계 모델링

### 1단계 — 데이터 준비와 분리

```python
from sklearn.model_selection import train_test_split
import pandas as pd

df = pd.read_csv("churn.csv")
X = df.drop(columns=["churn"])
y = df["churn"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

데이터를 먼저 나누는 이유는 미래의 성능을 흉내 내기 위해서입니다. 학습에 쓴 데이터를 그대로 다시 평가하면 성능이 과장되기 쉽습니다. `stratify=y`를 쓰는 이유도 클래스 비율을 유지하기 위해서입니다.

### 2단계 — 베이스라인 만들기

```python
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score

base = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
print("baseline:", accuracy_score(y_test, base.predict(X_test)))
```

이 단계는 단순하지만 매우 중요합니다. 가장 흔한 답만 찍는 모델보다 나은지조차 확인하지 않고 복잡한 모델로 가면 성능 해석이 쉽게 틀어집니다.

### 3단계 — 전처리와 모델을 Pipeline으로 묶기

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

num = X.select_dtypes("number").columns.tolist()
cat = X.select_dtypes("object").columns.tolist()

pre = ColumnTransformer([
    ("num", StandardScaler(), num),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
])
model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])
```

전처리를 Pipeline 안에 넣는 이유는 누수를 막기 위해서입니다. 테스트 데이터 정보가 전처리 단계에 섞이면 평가 점수가 실제보다 좋아 보일 수 있습니다. Pipeline은 이 과정을 안전하게 묶어 줍니다.

### 4단계 — 학습과 평가

```python
model.fit(X_train, y_train)
print("model:", accuracy_score(y_test, model.predict(X_test)))
```

이제야 실제 모델의 첫 점수를 봅니다. 중요한 것은 숫자 자체보다 베이스라인과 비교해 얼마나 나아졌는지입니다.

### 5단계 — 교차 검증으로 흔들림 보기

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy")
print(scores.mean(), "+/-", scores.std())
```

한 번의 분할 결과는 운이 섞일 수 있습니다. 교차 검증은 평균뿐 아니라 분산도 보여 주기 때문에, 모델이 얼마나 안정적인지 읽는 데 도움이 됩니다.

**Expected output:** 베이스라인 점수, 첫 모델 점수, 교차 검증 평균과 표준편차를 한 화면에서 비교합니다.

## 이 코드에서 먼저 봐야 할 점

- 베이스라인은 항상 가장 먼저 기록해야 합니다.
- Pipeline은 데이터 누수를 막아 주는 기본 안전장치입니다.
- 교차 검증은 평균 점수뿐 아니라 결과의 흔들림까지 보여 줍니다.

## 자주 하는 실수 다섯 가지

1. **베이스라인 없이 시작하는 실수**: 무엇이 개선인지 판단할 기준이 없습니다.
2. **테스트 데이터로 전처리 통계를 학습하는 실수**: 대표적인 데이터 누수입니다.
3. **accuracy만 보는 실수**: 클래스 불균형 상황에서는 특히 위험합니다.
4. **`random_state`를 고정하지 않는 실수**: 재현성이 무너집니다.
5. **한 번의 분할 결과로 결론 내리는 실수**: 운을 실력으로 착각하기 쉽습니다.

## 실무에서는 이렇게 나타납니다

실무 팀은 MLflow나 Weights & Biases 같은 도구로 실험을 기록합니다. 실험 1번은 거의 항상 베이스라인입니다. 피처 변경도 한 번에 하나씩 넣어야 어떤 변화가 점수를 움직였는지 설명할 수 있습니다.

## 시니어는 이렇게 생각합니다

- 가장 값진 실험은 종종 베이스라인입니다.
- 전처리와 모델은 항상 함께 묶습니다.
- `random_state`는 반드시 고정합니다.
- 평균뿐 아니라 교차 검증 분산도 봅니다.
- 한 번에 하나의 변화만 주는 편이 학습이 빠릅니다.

## 체크리스트

- [ ] 베이스라인 모델을 만들 수 있습니다.
- [ ] Pipeline이 왜 필요한지 설명할 수 있습니다.
- [ ] train/test 분리 이유를 알고 있습니다.
- [ ] 교차 검증 분산을 함께 봐야 한다는 점을 이해합니다.

## 연습 문제

1. Titanic 데이터셋에서 베이스라인과 logistic regression을 비교해 보세요.
2. Pipeline이 없어서 데이터 누수가 생긴 사례를 문서로 적어 보세요.
3. 교차 검증 폴드 수를 바꿔 가며 평균과 분산이 어떻게 달라지는지 확인해 보세요.

## 정리 및 다음 글

모델링은 복잡한 알고리즘 경연이 아니라, 기준선과 비교하며 조금씩 나아지는 과정입니다. 베이스라인, 분리, 누수 방지, 반복 평가를 챙겨야 모델 점수를 믿을 수 있습니다. 다음 글에서는 이렇게 만든 모델을 어떤 지표로 평가해야 하는지 살펴보겠습니다.

## 실무 확장: 모델 선택 흐름과 sklearn 파이프라인 설계

모델링에서 가장 흔한 실패는 알고리즘 선택보다 실험 설계 부재에서 시작됩니다. 어떤 문제인지, 데이터 형태가 무엇인지, 해석 가능성이 중요한지, 운영 제약이 있는지에 따라 모델 선택 기준은 달라집니다. 이 섹션에서는 초급 실무에서 바로 적용 가능한 선택 흐름과 `scikit-learn` 파이프라인 예시를 제시합니다.

### 모델 선택 플로차트(텍스트 버전)

1. 목표 변수가 연속형인가 범주형인가를 먼저 구분합니다.
2. 데이터 건수가 작고 해석이 중요하면 선형/로지스틱 회귀를 우선 검토합니다.
3. 비선형 패턴 가능성이 크면 트리 기반 모델을 후보에 추가합니다.
4. 클래스 불균형이 크면 클래스 가중치와 임계값 전략을 함께 설계합니다.
5. 배포 지연시간 제약이 있으면 추론 속도를 평가 항목에 포함합니다.

### sklearn Pipeline 예시: 전처리 + 모델 + 검증

```python
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score


df = pd.read_csv("churn.csv")
X = df.drop(columns=["churn"])
y = df["churn"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

num_cols = X.select_dtypes(include="number").columns.tolist()
cat_cols = X.select_dtypes(exclude="number").columns.tolist()

pre = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ]
)

clf = Pipeline(
    steps=[
        ("pre", pre),
        ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ]
)

clf.fit(X_train, y_train)
proba = clf.predict_proba(X_test)[:, 1]
print("test_auc:", round(roc_auc_score(y_test, proba), 4))
print("cv_auc:", cross_val_score(clf, X_train, y_train, cv=5, scoring="roc_auc").mean())
```

### 후보 모델 비교표(입문 실무 기준)

| 모델 | 장점 | 단점 | 추천 상황 |
| --- | --- | --- | --- |
| Logistic Regression | 빠름, 해석 쉬움 | 비선형 한계 | 베이스라인, 설명 필요 |
| Random Forest | 강건함, 튜닝 난이도 중간 | 해석 상대적 어려움 | 일반 탭уляр 데이터 |
| Gradient Boosting | 성능 우수 가능성 높음 | 튜닝/학습시간 증가 | 점수 극대화 필요 |

### 실험 운영 규칙

- 베이스라인 점수를 먼저 고정합니다.
- 한 번에 한 가지 변화만 적용합니다.
- 지표는 주 지표 + 가드레일 지표를 분리합니다.
- 실험 로그에 데이터 버전, 피처 목록, 파라미터를 반드시 기록합니다.
- 테스트셋은 마지막 검증에만 사용합니다.

모델링은 "좋은 알고리즘 찾기"보다 "검증 가능한 실험 반복"에 가깝습니다. 이 관점을 잡으면 성능 개선이 느려 보여도 결과 신뢰도는 훨씬 높아집니다.

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

## 처음 질문으로 돌아가기

- **첫 모델을 만들 때 왜 베이스라인부터 시작해야 할까요?**
  - 본문의 기준은 모델링를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **train/test 분리는 무엇을 막아 주는 장치일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **전처리와 모델을 하나의 Pipeline으로 묶는 이유는 무엇일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Science 101 (1/10): Data Science란 무엇인가?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): 문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- [Data Science 101 (3/10): 데이터 수집](./03-data-collection.md)
- [Data Science 101 (4/10): 데이터 정제](./04-data-cleaning.md)
- [Data Science 101 (5/10): 탐색적 데이터 분석](./05-exploratory-data-analysis.md)
- [Data Science 101 (6/10): 시각화](./06-visualization.md)
- **모델링 (현재 글)**
- 평가 (예정)
- 결과 해석 (예정)
- 데이터 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Google — Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Kaggle — Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning)
- [Hands-On Machine Learning with Scikit-Learn](https://github.com/ageron/handson-ml3)

Tags: DataScience, Modeling, ScikitLearn, MachineLearning, Beginner

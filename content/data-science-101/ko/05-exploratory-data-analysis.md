---
series: data-science-101
episode: 5
title: 탐색적 데이터 분석
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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
last_reviewed: '2026-05-12'
---

# 탐색적 데이터 분석

이 글은 Data Science 101 시리즈의 다섯 번째 글입니다.

탐색적 데이터 분석, 즉 EDA는 모델링 전에 잠깐 거치는 절차가 아닙니다. 데이터가 실제로 어떤 모양을 하고 있는지, 무엇이 비어 있는지, 어떤 변수들이 함께 움직이는지 먼저 읽어 보는 과정입니다. 이 단계를 성실하게 거치지 않으면 평균 하나만 보고 전형적인 값을 오해하거나, 상관관계를 인과로 착각하거나, 결측 패턴을 놓쳐 편향을 키우기 쉽습니다.

EDA를 잘한다는 말은 화려한 그래프를 많이 그린다는 뜻이 아닙니다. 데이터를 빠르게 읽되, 잘못 읽지 않는다는 뜻에 가깝습니다. 이 글에서는 입문자가 반복해서 써 볼 수 있는 5단계 EDA 흐름을 정리하겠습니다.

## 이 글에서 다룰 문제

- 모델을 만들기 전에 데이터의 모양을 어떻게 빠르게 읽을 수 있을까요?
- 평균 하나만 보면 왜 자주 오해하게 될까요?
- 분포, 결측 패턴, 상관관계는 어떤 순서로 보는 편이 좋을까요?
- cardinality는 왜 모델 선택과 직결될까요?
- correlation이 causation이 아니라는 말은 실제로 무엇을 경계하라는 뜻일까요?

> EDA는 모델링 전에 반드시 읽어야 하는 데이터의 자기소개서입니다.

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

```mermaid
flowchart LR
    Shape["모양과 타입"] --> Dist["1차원 분포"]
    Dist --> Pair["2차원 관계"]
    Pair --> Miss["결측 패턴"]
    Miss --> Corr["상관관계"]
```

## 핵심 용어

- **Skewness**: 분포가 한쪽으로 얼마나 치우쳐 있는지 나타내는 정도입니다.
- **Outlier**: 다른 값들과 통계적으로 멀리 떨어진 값입니다.
- **Cardinality**: 범주형 값의 고유값 개수입니다.
- **Correlation**: 두 변수의 선형 관계 강도입니다.
- **MCAR / MAR / MNAR**: 결측이 생기는 방식의 분류입니다.

## Before / After

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

<!-- toc:begin -->
- [Data Science란 무엇인가?](./01-what-is-data-science.md)
- [문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- [데이터 수집](./03-data-collection.md)
- [데이터 정제](./04-data-cleaning.md)
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

Tags: DataScience, EDA, Pandas, Statistics, Beginner

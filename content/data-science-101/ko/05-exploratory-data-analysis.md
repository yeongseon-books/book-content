---
series: data-science-101
episode: 5
title: 탐색적 데이터 분석
status: content-ready
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
seo_description: 데이터의 모양을 빠르게 읽기 위한 EDA 5단계 — describe, 분포, 결측, 상관, 이상치까지 한 번에 정리
last_reviewed: '2026-05-04'
---

# 탐색적 데이터 분석

> Data Science 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *모델을 만들기 전* 에 데이터의 *모양* 을 *어떻게* *빠르고 정확* 하게 파악할까요?

> *EDA 는 *모델보다 먼저* 읽어야 할 *데이터의 자기소개* 다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *EDA 의 목적* 과 *순서*
- 1차원/2차원 *분포* 보기
- *결측 패턴* 과 *상관* 의 의미
- 5단계 EDA 실습
- 흔한 함정 5가지

## 왜 중요한가

EDA 가 빈약하면 *엉뚱한 모델* 을 만들게 됩니다. *데이터의 자기소개* 를 듣지 않고 *결정* 부터 하면 *후회* 가 큽니다.

> *모델은 데이터를 *흉내* 낼 뿐이다.*

## 개념 한눈에 보기

```mermaid
flowchart LR
    Shape["Shape & dtypes"] --> Dist["1D Distribution"]
    Dist --> Pair["2D Relations"]
    Pair --> Miss["Missing Patterns"]
    Miss --> Corr["Correlation"]
```

## 핵심 용어 정리

- **Skewness**: 분포의 *치우침*.
- **Outlier**: *통계적으로 멀리* 떨어진 값.
- **Cardinality**: 카테고리의 *고유 값 개수*.
- **Correlation**: 두 변수의 *선형 관계* 정도.
- **MCAR/MAR/MNAR**: *결측이 발생하는 패턴* 분류.

## Before/After

**Before**: `mean` 만 보고 *대표값* 을 *오해*.

**After**: *분포 + 분위수 + 이상치* 를 함께 봐 *전체 모양* 을 파악.

## 실습: 5단계 EDA

### 1단계 — 모양/타입 파악

```python
import pandas as pd
df = pd.read_csv("orders.csv")
print(df.shape)
print(df.dtypes)
print(df.head())
```

### 2단계 — 1차원 분포

```python
print(df["amount"].describe())
df["amount"].plot.hist(bins=30, title="amount")
```

### 3단계 — 카테고리 cardinality

```python
print(df.select_dtypes("object").nunique().sort_values(ascending=False))
print(df["country"].value_counts(normalize=True).head())
```

### 4단계 — 2차원 관계

```python
import seaborn as sns
sns.scatterplot(data=df.sample(2000), x="quantity", y="amount")
```

### 5단계 — 결측/상관

```python
print(df.isna().mean().sort_values(ascending=False).head())
print(df.select_dtypes("number").corr().round(2))
```

## 이 코드에서 주목할 점

- *describe* 는 *시작* 일 뿐. *분포* 를 함께 본다.
- *상관* 은 *인과* 가 아니다.
- *카테고리 cardinality* 가 *모델 선택* 에 영향을 준다.

## 자주 하는 실수 5가지

1. ***mean* 만 보고 *결정*.** *분포 모양* 을 놓친다.
2. ***상관* 을 *인과* 로 해석.** 흔한 *오해*.
3. ***샘플* 없이 *전체* 를 *plot*.** 메모리/시간 폭주.
4. **카테고리 *cardinality* 를 *무시*.** *원-핫 폭발*.
5. ***결측 패턴* 을 *MCAR 로 가정*.** 편향된 결론.

## 실무에서는 이렇게 쓰입니다

데이터팀은 *EDA notebook* 을 *모델 코드 옆* 에 둡니다. *주요 분포* 는 *대시보드* 로 *상시 모니터링*. *데이터 드리프트* 도 EDA 의 연속입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *분포 → 관계 → 결측 → 상관* 순서.
- *상관* 은 *경계* 하며 본다.
- *EDA notebook* 을 *PR* 에 첨부.
- *샘플링* 으로 *시간을 산다*.
- *주기적으로* EDA 를 *다시* 돌려 *드리프트* 를 본다.

## 체크리스트

- [ ] *describe + 분포* 를 함께 본다.
- [ ] *Cardinality* 를 안다.
- [ ] *상관 ≠ 인과* 를 안다.
- [ ] *결측 패턴* 을 분류할 수 있다.

## 연습 문제

1. *Iris/Titanic* 데이터의 *5단계 EDA* 를 수행해 보세요.
2. *상관이 높지만 인과는 아닌* 사례 3개를 적어 보세요.
3. *카테고리 cardinality* 가 *모델 선택* 에 미친 영향을 적어 보세요.

## 정리 및 다음 단계

EDA 는 *데이터를 *듣는 시간* 입니다. 다음 글에서는 들은 것을 *그림으로 보여주는* *시각화* 를 살펴봅니다.

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

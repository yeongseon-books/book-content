---
series: pandas-101
episode: 4
title: filtering과 selection
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Pandas
  - Filtering
  - Selection
  - Indexing
  - Beginner
seo_description: loc·iloc·boolean indexing·query까지 Pandas의 행과 열 선택 4가지 방법을 코드와 함께 정리한 입문 글
last_reviewed: '2026-05-04'
---

# filtering과 selection

> Pandas 101 시리즈 (4/10)


## 이 글에서 다룰 문제

데이터 분석의 *모든 단계* 에서 *서브셋 추출* 이 일어납니다. *느리거나 잘못된 선택* 은 *전체 파이프라인* 을 흔듭니다.

## 전체 흐름
```mermaid
flowchart LR
    DF["DataFrame"] --> Loc["loc (label)"]
    DF --> Iloc["iloc (position)"]
    DF --> Bool["boolean mask"]
    DF --> Q["query (string)"]
```

## Before/After

**Before**: *“df[조건] 만 사용”* — *체이닝 인덱싱* 으로 *경고* 발생.

**After**: *“의도에 맞는 도구”* — *loc/iloc/query* 로 *명확하게* 분리.

## 5단계 선택

### 1단계 — 열 선택

```python
import pandas as pd
df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]}, index=["a", "b", "c"])
print(df["x"])
print(df[["x", "y"]])
```

### 2단계 — loc

```python
print(df.loc["a"])
print(df.loc[["a", "c"], "x"])
```

### 3단계 — iloc

```python
print(df.iloc[0])
print(df.iloc[0:2, 0])
```

### 4단계 — boolean indexing

```python
print(df[df["x"] > 1])
print(df[(df["x"] > 1) & (df["y"] < 30)])
```

### 5단계 — query와 isin

```python
print(df.query("x > 1 and y < 30"))
print(df[df["x"].isin([1, 3])])
```

## 이 코드에서 주목할 점

- *loc* 은 *끝점 포함*, *iloc* 은 *끝점 제외*.
- *&* 와 *|* 는 *비트 연산자* — *and/or* 가 아닙니다.
- *query* 는 *큰 표현식* 에서 *가독성* 이 좋습니다.

## 자주 하는 실수 5가지

1. ***and/or* 사용 → 오류.** *&/|* 와 *괄호* 필요.
2. ***체이닝 인덱싱***: `df[df["x"]>1]["y"] = ...` → *SettingWithCopyWarning*.
3. ***loc 의 끝점 포함* 을 모름.**
4. ***iloc 으로 라벨* 을 시도.**
5. ***isin 대신* 여러 *|* 로 길게 씀.**

## 실무에서는 이렇게 쓰입니다

KPI 대시보드, 이상치 탐지, A/B 테스트 분리 — *조건 기반 선택* 이 *분석 함수의 핵심* 입니다. *팀 코드 표준* 으로 *loc 사용* 을 *강제* 하기도 합니다.

## 체크리스트

- [ ] *loc* 과 *iloc* 을 구분한다.
- [ ] *&/|* 와 *괄호* 를 쓴다.
- [ ] *체이닝 인덱싱* 을 피한다.
- [ ] *query* 와 *isin* 을 안다.

## 정리 및 다음 단계

선택은 *분석의 기본 동작* 입니다. 다음 글에서는 *missing value* 처리를 다룹니다.

<!-- toc:begin -->
- [Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Series와 DataFrame](./02-series-and-dataframe.md)
- [CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- **filtering과 selection (현재 글)**
- missing value 처리 (예정)
- groupby (예정)
- merge와 join (예정)
- time series (예정)
- apply와 vectorization (예정)
- 실전 데이터 분석 (예정)
<!-- toc:end -->

## 참고 자료

- [pandas — Indexing and selecting data](https://pandas.pydata.org/docs/user_guide/indexing.html)
- [pandas — query](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html)
- [pandas — Boolean indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing)
- [Real Python — Pandas DataFrame Indexing](https://realpython.com/pandas-dataframe/)

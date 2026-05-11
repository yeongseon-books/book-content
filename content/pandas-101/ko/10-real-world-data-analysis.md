---
series: pandas-101
episode: 10
title: 실전 데이터 분석
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
  - DataAnalysis
  - EDA
  - Workflow
  - Beginner
seo_description: 적재·정제·변형·집계·시각화까지 실전 데이터 분석의 전체 흐름을 한 편의 코드로 정리한 입문 글
last_reviewed: '2026-05-11'
---

# 실전 데이터 분석

> Pandas 101 시리즈 (10/10)


## 이 글에서 다룰 문제

각 도구를 따로 아는 것과 *하나의 결과* 로 묶는 것은 다릅니다. *프로 분석가* 의 차이는 *연결 능력* 에서 나옵니다.

## 전체 흐름
```mermaid
flowchart LR
    Load["load (read_csv)"] --> Clean["clean (dropna / dtype)"]
    Clean --> Reshape["reshape (groupby / merge)"]
    Reshape --> Agg["aggregate (KPI)"]
    Agg --> Vis["visualize / report"]
```

## Before/After

**Before**: *“스크립트 한 덩어리”* — 다시 못 돌림.

**After**: *“함수 단위 파이프라인”* — *재현, 테스트, 공유* 가능.

## 5단계 끝까지 가기

### 1단계 — 적재

```python
import pandas as pd

def load(path):
    return pd.read_csv(path, parse_dates=["date"])

df = load("sales.csv")
print(df.shape)
```

### 2단계 — 정제

```python
def clean(df):
    df = df.dropna(subset=["sales"])
    df["sales"] = df["sales"].astype(float)
    return df

df = clean(df)
```

### 3단계 — 변형

```python
def enrich(df):
    df["month"] = df["date"].dt.to_period("M")
    return df

df = enrich(df)
```

### 4단계 — 집계 (KPI)

```python
def kpi(df):
    return df.groupby("month").agg(
        total=("sales", "sum"),
        n=("sales", "count"),
        mean=("sales", "mean"),
    )

monthly = kpi(df)
print(monthly)
```

### 5단계 — 시각화

```python
import matplotlib.pyplot as plt
monthly["total"].plot(kind="bar", title="Monthly Sales")
plt.tight_layout()
plt.savefig("monthly.png")
```

## 이 코드에서 주목할 점

- *함수 단위 분리* 로 *각 단계 독립 테스트* 가능.
- *parse_dates* 가 *시계열 분석* 의 시작.
- `plot`은 Pandas 내장 기능으로 빠르게 그립니다.

## 자주 하는 실수 5가지

1. ***모든 단계* 를 *하나의 셀* 에 작성.**
2. ***중간 결과* 를 *저장하지 않음*.**
3. ***컬럼 이름* 을 *문서화하지 않음*.**
4. ***시각화 없이* 표만 보고 결론.**
5. ***재현성* 무시 — *seed/버전* 미고정.**

## 실무에서는 이렇게 쓰입니다

KPI 리포트 자동화, 마케팅 분석, 운영 대시보드 — *분석 파이프라인* 은 *재사용 가능한 라이브러리* 가 됩니다. *Jupyter 노트북* 과 *Python 모듈* 을 함께 운영합니다.

## 체크리스트

- [ ] *load/clean/enrich/kpi/visualize* 함수 분리.
- [ ] 시각화 산출물을 생성한다.
- [ ] *컬럼 명세* 문서화.
- [ ] *재현 가능* 한지 확인.

## 정리 및 다음 단계

이제 Pandas 입문을 마쳤습니다. 다음 단계는 `Polars`, `Dask`, 시각화(`Matplotlib`/`Plotly`), 그리고 ML 전처리(`scikit-learn`)입니다. 데이터를 다루는 많은 길이 Pandas에서 시작합니다.

<!-- toc:begin -->
- [Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Series와 DataFrame](./02-series-and-dataframe.md)
- [CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [filtering과 selection](./04-filtering-and-selection.md)
- [missing value 처리](./05-missing-values.md)
- [groupby](./06-groupby.md)
- [merge와 join](./07-merge-and-join.md)
- [time series](./08-time-series.md)
- [apply와 vectorization](./09-apply-and-vectorization.md)
- **실전 데이터 분석 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [pandas — Cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html)
- [pandas — Visualization](https://pandas.pydata.org/docs/user_guide/visualization.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)
- [Kaggle — Pandas Course](https://www.kaggle.com/learn/pandas)

Tags: Pandas, DataAnalysis, EDA, Workflow, Beginner

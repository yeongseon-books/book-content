---
series: pandas-101
episode: 9
title: apply와 vectorization
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
  - Vectorization
  - Performance
  - Apply
  - Beginner
seo_description: apply의 함정과 NumPy·Pandas 벡터화의 위력을 코드와 함께 정리해 성능을 끌어올리는 입문 글
last_reviewed: '2026-05-04'
---

# apply와 vectorization

> Pandas 101 시리즈 (9/10)


## 이 글에서 다룰 문제

분석 속도가 *수십~수백 배* 차이날 수 있습니다. *벡터화* 는 *Pandas의 본질* 이며, *apply 남용* 은 *가장 흔한 안티패턴* 입니다.

## 전체 흐름
```mermaid
flowchart LR
    Loop["for-loop"] -->|slow| Apply["apply"]
    Apply -->|faster| Vec["vectorized (NumPy / Pandas ops)"]
```

## Before/After

**Before**: *“for i in range(len(df))”* — 100만 행에서 분 단위.

**After**: *“df["c"] = df["a"] + df["b"]”* — 밀리초.

## 5단계 성능

### 1단계 — 기준 데이터

```python
import numpy as np, pandas as pd
df = pd.DataFrame({"a": np.arange(1_000_000), "b": np.arange(1_000_000)})
```

### 2단계 — 느린 방식

```python
# %timeit df.apply(lambda r: r["a"] + r["b"], axis=1)
# 매우 느림 — apply(axis=1)은 행 단위 Python 호출
```

### 3단계 — 벡터화

```python
df["c"] = df["a"] + df["b"]   # 가장 빠름
```

### 4단계 — np.where 조건부

```python
df["flag"] = np.where(df["a"] % 2 == 0, "even", "odd")
```

### 5단계 — map 으로 코드 매핑

```python
mapping = {0: "zero", 1: "one"}
print(pd.Series([0, 1, 2]).map(mapping))
```

## 이 코드에서 주목할 점

- *axis=1* apply 는 *가장 느림* — *행마다 Python 호출*.
- *벡터 연산* 은 *C 레벨* 에서 실행됩니다.
- *np.where* 는 *if-else* 의 벡터 버전.

## 자주 하는 실수 5가지

1. ***apply(axis=1) 남용*.**
2. ***Python for문* 으로 *행 누적 합* 계산.**
3. ***eval/numexpr* 을 *모르고* 거대한 표현식 직접 작성.**
4. ***map* 의 *NaN 발생* 을 무시.**
5. ***dtype 불일치* 로 *벡터화 실패* 후 object dtype.**

## 실무에서는 이렇게 쓰입니다

ETL 변환, 피처 엔지니어링, 대규모 리포트 — *벡터화* 는 *비용과 시간* 을 직접적으로 절감합니다. *클라우드 비용 절감* 의 가장 쉬운 레버.

## 체크리스트

- [ ] *벡터화* 와 *apply* 를 구분한다.
- [ ] *np.where* 를 쓴다.
- [ ] *map* 으로 *코드 변환* 을 한다.
- [ ] *axis=1 apply* 를 피한다.

## 정리 및 다음 단계

벡터화는 *Pandas의 본질* 입니다. 다음 글에서는 *실전 데이터 분석* 을 다룹니다.

<!-- toc:begin -->
- [Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Series와 DataFrame](./02-series-and-dataframe.md)
- [CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [filtering과 selection](./04-filtering-and-selection.md)
- [missing value 처리](./05-missing-values.md)
- [groupby](./06-groupby.md)
- [merge와 join](./07-merge-and-join.md)
- [time series](./08-time-series.md)
- **apply와 vectorization (현재 글)**
- 실전 데이터 분석 (예정)
<!-- toc:end -->

## 참고 자료

- [pandas — Enhancing performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
- [pandas — apply](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html)
- [NumPy — Universal functions](https://numpy.org/doc/stable/reference/ufuncs.html)
- [Real Python — Fast, Flexible, Easy and Intuitive Pandas](https://realpython.com/fast-flexible-pandas/)

Tags: Pandas, Vectorization, Performance, Apply, Beginner

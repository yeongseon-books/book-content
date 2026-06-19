---
series: pandas-101
episode: 8
title: "Pandas 101 (8/10): 시계열 데이터 다루기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Pandas
  - TimeSeries
  - Resample
  - Datetime
  - Beginner
seo_description: 시계열 분석 기법을 익힙니다. DatetimeIndex, 리샘플링, 이동 평균, 시차 이동 및 시간대 처리 등 실무 시계열 패턴을 정리합니다.
last_reviewed: '2026-05-15'
---

# Pandas 101 (8/10): 시계열 데이터 다루기

매출, 트래픽, 센서, 금융 데이터처럼 시간 순서가 중요한 데이터는 일반 표와 같은 방식으로만 보면 자주 막힙니다. 날짜가 문자열로 남아 있으면 비교가 어색하고, 주간 합계나 이동 평균을 구하려 해도 코드가 금방 지저분해집니다. 시계열은 시간 축을 인덱스로 삼는 순간부터 다루는 감각이 바뀝니다.

이 글은 Pandas 101 시리즈의 8번째 글입니다.

이번 글에서는 시계열을 별도 라이브러리의 영역으로 보지 않고, Pandas 안에서 날짜 인덱스와 시간 단위 계산으로 푸는 기본 패턴으로 정리해 보겠습니다.

![Pandas 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/08/08-01-concept-at-a-glance.ko.png)
*Pandas 101 8장 흐름 개요*
> **시계열은 시간 순서가 의미**입니다. 정렬을 무시하거나 누락 주기를 처리하지 않으면 추세와 계절성 분석 자체가 무너집니다.

## 이 글에서 다룰 문제

- 날짜 열을 인덱스로 두면 무엇이 달라질까요?
- 리샘플링은 단순 집계와 어떤 차이가 있을까요?
- 이동 평균 같은 창 기반 계산은 어떻게 할까요?
- 이 기능을 대규모 데이터에 적용할 때 성능 함정은 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?

운영 지표의 대부분은 시간에 따라 변합니다. 시간 축을 제대로 다루면 주간 합계, 월간 평균, 이동 평균, 전일 대비 변화처럼 실무에서 자주 쓰는 질문을 짧고 안정적인 코드로 풀 수 있습니다.

## 핵심 개념 정의

- **DatetimeIndex**: 시간을 레이블로 가지는 인덱스입니다.
- **리샘플링**: 시간 단위를 바꿔 다시 묶는 작업입니다.
- **이동 창 계산**: 일정 구간을 밀어 가며 통계를 구하는 방식입니다.
- **시차 이동 (shift)**: 값을 시간 축에서 앞으로 또는 뒤로 미는 연산입니다.
- **시간대 (timezone)**: UTC 기준 오프셋이 붙은 시간 표현입니다.
- **dt accessor**: 날짜 열에서 년/월/일/요일을 추출하는 접근자입니다.

## 전과 후

이전 관점: 날짜를 문자열로 둔 채 필터링과 비교를 억지로 합니다.

이후 관점: 날짜 인덱스로 바꾼 뒤 시간 슬라이싱과 단위 변환을 자연스럽게 수행합니다.

## 실습: 다섯 단계로 시계열 다루기

### 1단계 - 날짜 인덱스 만들기

```python
import pandas as pd
import numpy as np

# 날짜 범위 생성
idx = pd.date_range("2026-01-01", periods=30, freq="D")

# 시계열 생성
np.random.seed(42)
ts = pd.Series(
    np.random.randint(80, 150, size=30),
    index=idx,
    name="daily_sales",
)
print(ts.head(7))
print()
print("인덱스 타입:", type(ts.index))
print("첫 날짜:", ts.index[0])
print("마지막 날짜:", ts.index[-1])
```

**예상 출력:**

```text
2026-01-01    112
2026-01-02    104
2026-01-03    128
2026-01-04    143
2026-01-05     91
2026-01-06    116
2026-01-07    108
Name: daily_sales, dtype: int64

인덱스 타입: <class 'pandas.core.indexes.datetimes.DatetimeIndex'>
첫 날짜: 2026-01-01 00:00:00
마지막 날짜: 2026-01-30 00:00:00
```

시계열 작업의 시작은 시간을 문자열이 아니라 날짜형 인덱스로 올려 두는 일입니다.

### 2단계 - 시간 구간 슬라이싱

```python
# 문자열로 날짜 슬라이싱 (매우 편리)
week1 = ts.loc["2026-01-01":"2026-01-07"]
print("1주차:\n", week1)
print()

# 월 전체 선택
jan = ts.loc["2026-01"]
print(f"1월 전체: {len(jan)}일")
print()

# 조건 필터링
high_days = ts[ts > 130]
print(f"130 이상인 날: {len(high_days)}일")
print(high_days)
```

**예상 출력:**

```text
1주차:
 2026-01-01    112
2026-01-02    104
2026-01-03    128
2026-01-04    143
2026-01-05     91
2026-01-06    116
2026-01-07    108
Name: daily_sales, dtype: int64

1월 전체: 30일
```

날짜 인덱스가 있으면 문자열 슬라이싱만으로도 기간 선택이 자연스럽게 됩니다.

### 3단계 - 리샘플링

```python
# 일별 → 주간 합계
weekly = ts.resample("W").sum()
print("주간 합계:")
print(weekly)
print()

# 일별 → 월간 통계
monthly = ts.resample("ME").agg(["sum", "mean", "max", "min"])
print("월간 통계:")
print(monthly.round(1))
```

**예상 출력:**

```text
주간 합계:
2026-01-04    487
2026-01-11    727
2026-01-18    731
2026-01-25    756
2026-02-01    469
Freq: W-SUN, Name: daily_sales, dtype: int64

월간 통계:
             sum   mean  max  min
2026-01-31  3170  105.7  143   81
```

`resample()`은 시간 축을 새 단위로 묶어 다시 계산하는 도구입니다. 일별 데이터를 주간이나 월간으로 바꾸는 식의 작업이 여기에 해당합니다.

### 4단계 - 이동 창 계산

```python
df_ts = ts.to_frame()

# 이동 평균
df_ts["ma7"]  = ts.rolling(window=7).mean()
df_ts["ma14"] = ts.rolling(window=14).mean()

# 이동 표준편차 (변동성)
df_ts["std7"] = ts.rolling(window=7).std()

# 확장 창 (누적 평균)
df_ts["cumavg"] = ts.expanding().mean()

print(df_ts.tail(10).round(1))
```

**예상 출력:**

```text
            daily_sales   ma7   ma14  std7  cumavg
2026-01-21          101  105.7  103.4  13.5   104.8
2026-01-22          118  107.1  104.7  15.1   105.2
2026-01-23           89  107.0  104.9  14.8   104.5
2026-01-24          130  108.7  105.7  15.7   105.0
2026-01-25          110  109.0  106.1  14.8   105.0
```

이동 창 계산은 추세를 부드럽게 보고 싶을 때 유용합니다. 특히 지표가 출렁이는 운영 데이터에서는 이동 평균이 패턴을 읽는 데 큰 도움이 됩니다.

### 5단계 - 시차 이동과 변화율

```python
df_shift = ts.to_frame()

# 전일 대비 변화
df_shift["prev_day"]  = ts.shift(1)
df_shift["day_change"] = ts - ts.shift(1)
df_shift["pct_change"] = ts.pct_change() * 100

# 전주 동일 요일 대비 (7일 전)
df_shift["last_week"] = ts.shift(7)
df_shift["wow_change"] = (ts - ts.shift(7)) / ts.shift(7) * 100

print(df_shift[["daily_sales", "day_change", "pct_change", "wow_change"]].head(12).round(1))
```

**예상 출력:**

```text
            daily_sales  day_change  pct_change  wow_change
2026-01-01          112         NaN         NaN         NaN
2026-01-02          104        -8.0        -7.1         NaN
2026-01-03          128        24.0        23.1         NaN
2026-01-04          143        15.0        11.7         NaN
2026-01-05           91       -52.0       -36.4         NaN
2026-01-06          116        25.0        27.5         NaN
2026-01-07          108        -8.0        -6.9         NaN
2026-01-08           99        -9.0        -8.3       -11.6
```

`shift()`는 특징 생성의 강력한 도구입니다. 전일 대비, 전주 대비, n기간 래그 특징을 만들 때 모두 사용합니다.

## dt accessor: 날짜 구성 요소 추출

```python
df_dt = pd.DataFrame({
    "date":  pd.date_range("2026-01-01", periods=10, freq="D"),
    "value": np.random.randint(50, 150, 10),
})

df_dt["year"]      = df_dt["date"].dt.year
df_dt["month"]     = df_dt["date"].dt.month
df_dt["day"]       = df_dt["date"].dt.day
df_dt["dayofweek"] = df_dt["date"].dt.dayofweek   # 0=월요일
df_dt["weekday"]   = df_dt["date"].dt.day_name()
df_dt["quarter"]   = df_dt["date"].dt.quarter
df_dt["is_weekend"]= df_dt["date"].dt.dayofweek >= 5

print(df_dt.to_string(index=False))
```

**예상 출력:**

```text
       date  value  year  month  day  dayofweek  weekday  quarter  is_weekend
 2026-01-01    112  2026      1    1          3  Thursday        1       False
 2026-01-02    104  2026      1    2          4    Friday        1       False
 2026-01-03    128  2026      1    3          5  Saturday        1        True
 2026-01-04    143  2026      1    4          6    Sunday        1        True
 2026-01-05     91  2026      1    5          0    Monday        1       False
```

날짜에서 구성 요소를 추출하면 월별, 요일별, 분기별 집계가 매우 쉬워집니다.

## resample 주기 코드 참조

| 코드 | 의미 | 예시 |
| --- | --- | --- |
| `D` | 일 | `resample("D")` |
| `W` | 주 (일요일 기준) | `resample("W")` |
| `ME` | 월말 | `resample("ME")` |
| `QE` | 분기말 | `resample("QE")` |
| `YE` | 연말 | `resample("YE")` |
| `h` | 시간 | `resample("h")` |
| `min` | 분 | `resample("min")` |
| `2D` | 2일 | `resample("2D")` |
| `3h` | 3시간 | `resample("3h")` |

## 시간대 처리

```python
# 시간대 없는 시계열
ts_utc = pd.date_range("2026-01-01", periods=5, freq="h", tz="UTC")
ts_no_tz = pd.date_range("2026-01-01", periods=5, freq="h")

# 시간대 부여 (localize)
ts_with_tz = pd.Series(range(5), index=ts_no_tz).tz_localize("UTC")

# 시간대 변환 (convert)
ts_seoul = ts_with_tz.tz_convert("Asia/Seoul")
ts_ny    = ts_with_tz.tz_convert("America/New_York")

print("UTC:")
print(ts_with_tz)
print("\n서울:")
print(ts_seoul)
print("\n뉴욕:")
print(ts_ny)
```

**예상 출력:**

```text
UTC:
2026-01-01 00:00:00+00:00    0
2026-01-01 01:00:00+00:00    1
2026-01-01 02:00:00+00:00    2
2026-01-01 03:00:00+00:00    3
2026-01-01 04:00:00+00:00    4

서울:
2026-01-01 09:00:00+09:00    0
2026-01-01 10:00:00+09:00    1
...
```

시간대는 먼저 부여(`tz_localize`)하고 그다음 변환(`tz_convert`)해야 합니다. 시간대 정보가 없는 시간과 있는 시간을 섞으면 비교와 병합에서 오류가 생깁니다.

## 누락 주기 처리

```python
# 불규칙 시계열
irregular = pd.Series(
    [100, 130, 90, 120],
    index=pd.to_datetime(["2026-01-01", "2026-01-03", "2026-01-06", "2026-01-10"]),
)

# 일별로 리인덱스 (빈 날짜 채우기)
full_idx  = pd.date_range("2026-01-01", "2026-01-10", freq="D")
reindexed = irregular.reindex(full_idx)

print("원본 (불규칙):")
print(irregular)
print("\n리인덱스 후 (빈 날짜 포함):")
print(reindexed)
print("\n선형 보간 후:")
print(reindexed.interpolate(method="time"))
```

**예상 출력:**

```text
원본 (불규칙):
2026-01-01    100
2026-01-03    130
2026-01-06     90
2026-01-10    120
dtype: int64

리인덱스 후 (빈 날짜 포함):
2026-01-01    100.0
2026-01-02      NaN
2026-01-03    130.0
...
```

## 실전 예제: 주간 매출 분석

```python
# 30일 일별 매출 데이터
dates = pd.date_range("2026-01-01", periods=30, freq="D")
np.random.seed(0)
sales = pd.DataFrame({
    "sales": np.random.randint(80, 200, size=30),
}, index=dates)

# 주간 집계
weekly = sales.resample("W").agg(
    total  =("sales", "sum"),
    average=("sales", "mean"),
    peak   =("sales", "max"),
).round(1)

# 7일 이동 평균
sales["ma7"] = sales["sales"].rolling(window=7, min_periods=1).mean().round(1)

# 요일별 평균 (패턴 분석)
sales["weekday"] = sales.index.day_name()
weekday_avg = sales.groupby("weekday")["sales"].mean().round(1)
# 요일 순서 정렬
days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday_avg = weekday_avg.reindex(days_order)

print("주간 집계:\n", weekly)
print("\n요일별 평균:")
print(weekday_avg)
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| `to_datetime` 없이 문자열 날짜 사용 | 슬라이싱/집계 불가 | `parse_dates` 또는 `pd.to_datetime()` |
| `resample()` 후 집계 함수 누락 | `ResampleGroupBy` 객체 반환 | `.sum()`, `.mean()` 등 집계 호출 |
| 이동 창 경계 NaN 미처리 | 처음 n행 NaN | `min_periods=1` 또는 별도 처리 |
| 시간대 없는 시간과 있는 시간 혼용 | `TypeError` | 모든 시계열을 UTC로 통일 |
| `shift()` 후 NaN 미처리 | 연산 오류 | `fillna()` 또는 `dropna()` 추가 |

## 실무에서는 이렇게 생각합니다

- 분석 전 시간 기준을 UTC로 통일할지 먼저 정합니다.
- 리샘플링 주기는 분석 목적에 맞춰 선택합니다.
- 이동 계산의 경계 `NaN`을 명시적으로 처리합니다.
- 빈 구간은 보간이 맞는지 검토합니다.
- `shift()`를 특징 생성 도구로도 활용합니다.

## 운영 체크리스트

- [ ] 날짜 인덱스를 만들 수 있습니다.
- [ ] `resample()`과 집계 함수를 함께 쓸 수 있습니다.
- [ ] `rolling()`으로 이동 평균을 계산할 수 있습니다.
- [ ] 시간대를 부여하고 변환할 수 있습니다.
- [ ] `dt` accessor로 날짜 구성 요소를 추출할 수 있습니다.

## 연습 문제

1. 일별 시리즈를 주간 합계로 리샘플링해 보세요.
2. 7일 이동 평균을 만들고 경계 `NaN`을 살펴보세요.
3. UTC 시간을 서울 시간으로 바꾼 결과를 출력해 보세요.
4. 요일별 평균 매출을 계산해 가장 많이 팔리는 요일을 찾아보세요.

## 정리와 다음 글

시계열 분석의 출발점은 시간을 날짜 인덱스로 올려 두는 일입니다. 이 감각만 잡혀도 기간 선택, 단위 변환, 이동 계산이 모두 같은 언어 안에서 풀립니다. 다음 글에서는 속도와 표현력에 큰 차이를 만드는 벡터화와 `apply`를 다루겠습니다.

## 처음 질문으로 돌아가기

- **날짜 열을 인덱스로 두면 무엇이 달라질까요?**
  - 문자열 슬라이싱으로 기간을 선택하고, `resample()`로 시간 단위를 바꾸며, `rolling()`으로 이동 창 계산을 할 수 있게 됩니다. 날짜 연산 전반이 자연스러워집니다.
- **리샘플링은 단순 집계와 어떤 차이가 있을까요?**
  - 단순 집계는 지정한 그룹 키 기준으로만 작동하지만, `resample`은 시간 주기를 기준으로 자동으로 그룹을 나눠 빈 구간도 만들어 줍니다.
- **이동 평균 같은 창 기반 계산은 어떻게 할까요?**
  - `rolling(window=N)` 뒤에 집계 함수를 붙이면 됩니다. `min_periods` 옵션으로 경계 처리를 제어하고, 확장 창이 필요하면 `expanding()`을 사용합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): 결측치 처리](./05-missing-values.md)
- [Pandas 101 (6/10): 그룹화와 집계](./06-groupby.md)
- [Pandas 101 (7/10): 병합과 조인](./07-merge-and-join.md)
- **Pandas 101 (8/10): 시계열 데이터 다루기 (현재 글)**
- [Pandas 101 (9/10): 적용 함수와 벡터화](./09-apply-and-vectorization.md)
- [실전 데이터 분석](./10-real-world-data-analysis.md)

<!-- toc:end -->

## 참고 자료

- [pandas — Time series / date functionality](https://pandas.pydata.org/docs/user_guide/timeseries.html)
- [pandas — resample](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html)
- [pandas — rolling](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html)
- [Forecasting — Hyndman & Athanasopoulos](https://otexts.com/fpp3/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, TimeSeries, Resample, Datetime, Beginner

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

이 글은 판다스 101 시리즈의 8번째 글입니다.

매출, 트래픽, 센서, 금융 데이터처럼 시간 순서가 중요한 데이터는 일반 표와 같은 방식으로만 보면 자주 막힙니다. 날짜가 문자열로 남아 있으면 비교가 어색하고, 주간 합계나 이동 평균을 구하려 해도 코드가 금방 지저분해집니다. 시계열은 시간 축을 인덱스로 삼는 순간부터 다루는 감각이 바뀝니다.

이번 글에서는 시계열을 별도 라이브러리의 영역으로 보지 않고, Pandas 안에서 날짜 인덱스와 시간 단위 계산으로 푸는 기본 패턴으로 정리해 보겠습니다.

![Pandas 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/08/08-01-concept-at-a-glance.ko.png)
*Pandas 101 8장 흐름 개요*
> **시계열은 시간 순서가 의미**입니다. 정렬을 무시하거나 누락 주기를 처리하지 않으면 추세와 계절성 분석 자체가 무너집니다.

## 먼저 던지는 질문

- 날짜 열을 인덱스로 두면 무엇이 달라질까요?
- 리샘플링은 단순 집계와 어떤 차이가 있을까요?
- 이동 평균 같은 창 기반 계산은 어떻게 할까요?

## 왜 중요한가

운영 지표의 대부분은 시간에 따라 변합니다. 시간 축을 제대로 다루면 주간 합계, 월간 평균, 이동 평균, 전일 대비 변화처럼 실무에서 자주 쓰는 질문을 짧고 안정적인 코드로 풀 수 있습니다.

## 핵심 용어

- **날짜 인덱스**: 시간을 레이블로 가지는 인덱스입니다.
- **리샘플링**: 시간 단위를 바꿔 다시 묶는 작업입니다.
- **이동 창 계산**: 일정 구간을 밀어 가며 통계를 구하는 방식입니다.
- **시차 이동**: 값을 시간 축에서 앞으로 또는 뒤로 미는 연산입니다.
- **시간대 부여와 변환**: 시간대 정보를 붙이고 다른 시간대로 바꾸는 작업입니다.
- **분주**: 특정 미세 함수로 병리 데이터를 나누는 작업입니다.

### 문자열 메서드 비교

다음 표는 Pandas 문자열 accessor(`str`)의 주요 메서드와 정규식 지원 여부, 실제 예시를 정리한 것입니다.

| 메서드 | 정규식 지원 | 반환 | 예시 |
|---|---|---|---|
| `str.contains()` | ● | bool 시리즈 | `s.str.contains("error")` |
| `str.extract()` | ● | DataFrame | `s.str.extract(r"(\d+)")` |
| `str.replace()` | ● | 시리즈 | `s.str.replace("old", "new")` |
| `str.split()` | - | 리스트 시리즈 | `s.str.split(",")` |
| `str.lower()` | - | 시리즈 | `s.str.lower()` |
| `str.strip()` | - | 시리즈 | `s.str.strip()` |

문자열 메서드는 텍스트 정제, 로그 파싱, 태그 추출 같은 실무 처리에서 매우 자주 쓰입니다. 특히 `contains`와 `extract`는 정규식을 지원하믰로 복잡한 패턴도 효율적으로 처리할 수 있습니다.

## 전과 후

이전 관점: 날짜를 문자열로 둔 채 필터링과 비교를 억지로 합니다.

이후 관점: 날짜 인덱스로 바꾼 뒤 시간 슬라이싱과 단위 변환을 자연스럽게 수행합니다.

## 실습: 다섯 단계로 시계열 다루기

### 1단계 - 날짜 인덱스 만들기

```python
import pandas as pd
idx = pd.date_range("2026-01-01", periods=10, freq="D")
ts = pd.Series(range(10), index=idx)
print(ts.head())
```

시계열 작업의 시작은 시간을 문자열이 아니라 날짜형 인덱스로 올려 두는 일입니다. 이 순간부터 Pandas의 시계열 문법을 사용할 수 있습니다.

### 2단계 - 시간 구간으로 자르기

```python
print(ts.loc["2026-01-03":"2026-01-06"])
```

날짜 인덱스가 있으면 문자열 슬라이싱만으로도 기간 선택이 자연스럽게 됩니다. 특정 월, 특정 주, 특정 날짜 범위를 빠르게 고를 수 있습니다.

### 3단계 - 시간 단위 바꾸기

```python
print(ts.resample("3D").sum())
```

리샘플링 결과를 보면 시간 단위를 바꾼다는 감각이 분명해집니다. 일별 값이 3일 단위 묶음으로 합쳐지며, 시간 축이 계산의 기준이 된다는 점을 눈으로 확인할 수 있습니다.

**예상 출력:**

```text
2026-01-01     3
2026-01-04    12
2026-01-07    21
2026-01-10     9
Freq: 3D, dtype: int64
```

`resample()`은 시간 축을 새 단위로 묶어 다시 계산하는 도구입니다. 일별 데이터를 3일 단위나 주간 단위로 바꾸는 식의 작업이 여기에 해당합니다.

### 4단계 - 이동 평균 계산하기

```python
print(ts.rolling(window=3).mean())
```

이동 창 계산은 추세를 부드럽게 보고 싶을 때 유용합니다. 특히 지표가 출렁이는 운영 데이터에서는 이동 평균이 패턴을 읽는 데 큰 도움이 됩니다.

### 5단계 - 시간대 바꾸기

```python
ts2 = ts.tz_localize("UTC").tz_convert("Asia/Seoul")
print(ts2.head())
```

시간대를 붙인 뒤 변환하면 같은 시각이 다른 지역 시각으로 어떻게 보이는지 바로 드러납니다. 글로벌 서비스 지표를 맞출 때 꼭 필요한 감각입니다.

**예상 출력:**

```text
2026-01-01 09:00:00+09:00    0
2026-01-02 09:00:00+09:00    1
2026-01-03 09:00:00+09:00    2
2026-01-04 09:00:00+09:00    3
2026-01-05 09:00:00+09:00    4
Freq: D, dtype: int64
```

시간대는 먼저 붙이고 그다음 변환해야 합니다. 시간대가 없는 시간과 있는 시간을 섞으면 비교와 병합에서 오류가 쉽게 생깁니다.

### datetime accessor 예제

날짜 열이 있을 때 `dt` accessor로 년/월/일/요일 같은 구성 요소를 바로 추출할 수 있습니다.

```python
import pandas as pd

df = pd.DataFrame({
    "date": pd.date_range("2026-01-01", periods=5, freq="D"),
    "value": [10, 20, 30, 40, 50],
})

df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["dayofweek"] = df["date"].dt.dayofweek  # 0=월요일
df["quarter"] = df["date"].dt.quarter

print(df.head())
```

**예상 출력:**

```text
        date  value  year  month  dayofweek  quarter
0 2026-01-01     10  2026      1          3        1
1 2026-01-02     20  2026      1          4        1
2 2026-01-03     30  2026      1          5        1
3 2026-01-04     40  2026      1          6        1
4 2026-01-05     50  2026      1          0        1
```

날짜에서 구성 요소를 바로 추출하면 월별, 분기별, 요일별 집계가 매우 쉽습니다. 특히 `dayofweek`는 주말/평일 패턴 분석에 자주 쓰입니다.

### resample 패턴

시계열 데이터를 다른 주기로 변환하는 `resample`은 실무에서 매우 자주 등장합니다.

```python
# 일별 데이터를 주간 합계로
df = df.set_index("date")
weekly = df.resample("W")["value"].sum()
print(weekly)
```

**예상 출력:**

```text
date
2026-01-04     60
2026-01-11    130
Freq: W-SUN, Name: value, dtype: int64
```

`resample`은 시간 축을 새 단위로 묶어 집계하는 도구입니다. 월별 매출, 주간 트래픽, 시간별 센서 값 같은 실무 지표를 만들 때 필수입니다.

## 이 코드에서 먼저 봐야 할 점

- 문자열 슬라이싱은 날짜 인덱스에서 특히 강력합니다.
- `resample()`은 항상 집계 함수와 함께 써야 의미가 생깁니다.
- 시간대는 먼저 부여하고 그다음 변환합니다.

### 카테고리 타입 변환

문자열로 저장된 범주형 데이터는 카테고리 타입으로 바꾸면 메모리와 속도가 크게 개선됩니다.

#### 카테고리 타입의 이점

1. **메모리 절감**: 문자열을 정수 코드로 저장합니다.
2. **속도 향상**: 그룹화와 비교 연산이 빠릅니다.
3. **순서 보존**: 범주형 변수의 순서를 명시할 수 있습니다.

```python
import pandas as pd

df = pd.DataFrame({
    "city": ["Seoul", "Busan", "Seoul", "Busan"] * 25000,
    "value": range(100000),
})

# 변환 전
print(f"문자열: {df['city'].memory_usage(deep=True) / 1024:.1f} KB")

# 변환 후
df["city"] = df["city"].astype("category")
print(f"카테고리: {df['city'].memory_usage(deep=True) / 1024:.1f} KB")
```

**예상 출력:**

```text
문자열: 5859.5 KB
카테곦0리: 97.8 KB
```

고유값이 적은 열은 카테곦0리로 바꾸는 것만으로도 메모리를 크게 줄일 수 있습니다. 특히 도시, 국가, 상태 코드 같은 반복되는 값에 효과적입니다.

#### 순서 명시

카테곦0리 타입은 범주의 순서를 명시할 수 있습니다.

```python
from pandas.api.types import CategoricalDtype

sizes = ["S", "M", "L", "M", "S", "L"]
cat_type = CategoricalDtype(categories=["S", "M", "L"], ordered=True)
s = pd.Series(sizes, dtype=cat_type)

print(s.sort_values())
print(s > "S")  # 비교 가능
```

**예상 출력:**

```text
4    S
0    S
1    M
3    M
2    L
5    L
dtype: category
Categories (3, object): ['S' < 'M' < 'L']

0    False
1     True
2     True
3     True
4    False
5     True
dtype: bool
```

순서가 있는 카테곦0리는 정렬과 비교가 의미 있게 동작합니다. 설문 응답의 리커트 척도, 학년, 우선순위 같은 데이터에 유용합니다.

## 자주 하는 실수 다섯 가지

1. `to_datetime` 없이 문자열 날짜를 그대로 사용합니다.
2. `resample()`만 호출하고 집계 함수를 빼먹습니다.
3. 이동 창 계산에서 `min_periods` 같은 경계 조건을 놓칩니다.
4. 시간대 정보가 없는 시간과 있는 시간을 섞습니다.
5. `shift()` 뒤에 생기는 `NaN` 처리를 잊습니다.

## 실무에서는 이렇게 이어집니다

매출 추세, 사용자 활동 패턴, 센서 모니터링처럼 시간 흐름이 핵심인 데이터에서는 시간 단위 변환과 이동 통계가 기본 도구가 됩니다. 특히 글로벌 서비스에서는 시간대를 통일하는 작업이 분석 정확도를 좌우합니다.

## 실무에서는 이렇게 생각합니다

- 분석 전 시간 기준을 UTC로 통일할지 먼저 정합니다.
- 리샘플링 주기는 분석 목적에 맞춰 선택합니다.
- 이동 계산의 경계 `NaN`을 명시적으로 처리합니다.
- 빈 구간은 보간이 맞는지 검토합니다.
- `shift()`를 특징 생성 도구로도 활용합니다.

## 체크리스트

- [ ] 날짜 인덱스를 만들 수 있습니다.
- [ ] `resample()`과 집계 함수를 함께 쓸 수 있습니다.
- [ ] `rolling()`으로 이동 평균을 계산할 수 있습니다.
- [ ] 시간대를 부여하고 변환할 수 있습니다.

### 실무 예제: 주간 매출 분석

실무에서 시계열 데이터를 분석할 때는 리샘플링과 이동 평균을 함께 사용하는 경우가 많습니다.

```python
import pandas as pd
import numpy as np

# 일별 매출 데이터
dates = pd.date_range("2026-01-01", periods=30, freq="D")
sales = np.random.randint(80, 150, size=30)
df = pd.DataFrame({"sales": sales}, index=dates)

# 주간 합계
weekly = df.resample("W").sum()

# 7일 이동 평균
df["ma7"] = df["sales"].rolling(window=7).mean()

print("\n주간 합계:")
print(weekly.head())
print("\n이동 평균 (마지막 5일):")
print(df[["sales", "ma7"]].tail())
```

이 패턴은 일별 데이터의 추세를 파악하는 데 매우 유용합니다. 주간 합계는 주단위 패턴을 보고, 이동 평균은 단기 변동성을 완화해 전반적인 추세를 드러냅니다.

## 연습 문제

1. 일별 시리즈를 주간 합계로 리샘플링해 보세요.
2. 7일 이동 평균을 만들고 경계 `NaN`을 살펴보세요.
3. UTC 시간을 서울 시간으로 바꾼 결과를 출력해 보세요.

## 정리와 다음 글

시계열 분석의 출발점은 시간을 날짜 인덱스로 올려 두는 일입니다. 이 감각만 잡혀도 기간 선택, 단위 변환, 이동 계산이 모두 같은 언어 안에서 풀립니다. 다음 글에서는 속도와 표현력에 큰 차이를 만드는 벡터화와 `apply`를 다루겠습니다.

## 처음 질문으로 돌아가기

- **날짜 열을 인덱스로 두면 무엇이 달라질까요?**
  - 본문의 기준은 시계열 데이터 다루기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **리샘플링은 단순 집계와 어떤 차이가 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **이동 평균 같은 창 기반 계산은 어떻게 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): 결측치 처리](./05-missing-values.md)
- [Pandas 101 (6/10): 그룹화와 집계](./06-groupby.md)
- [Pandas 101 (7/10): 병합과 조인](./07-merge-and-join.md)
- **시계열 데이터 다루기 (현재 글)**
- 적용 함수와 벡터화 (예정)
- 실전 데이터 분석 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — Time series / date functionality](https://pandas.pydata.org/docs/user_guide/timeseries.html)
- [pandas — resample](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html)
- [pandas — rolling](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html)
- [Forecasting — Hyndman & Athanasopoulos](https://otexts.com/fpp3/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, TimeSeries, Resample, Datetime, Beginner

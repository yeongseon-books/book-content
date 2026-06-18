---
series: pandas-101
episode: 8
title: "바이브코딩을 위한 Pandas 기초 (8/10): 시계열 데이터 다루기"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Pandas
  - 시계열
  - resample
  - 날짜
seo_description: AI가 생성한 pandas 시계열 코드를 이해하고 수정하는 방법. DatetimeIndex, resample, rolling, dt accessor를 바이브코딩 관점에서 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Pandas 기초 (8/10): 시계열 데이터 다루기

이 글은 **바이브코딩을 위한 Pandas 기초** 시리즈의 여덟 번째 글입니다.

---

AI에게 "일별 데이터를 주간 합계로 바꿔줘"라고 하면 `resample('W').sum()`이 나옵니다. 그런데 날짜 열이 문자열로 되어 있으면 이 코드는 바로 오류가 납니다. 날짜 인덱스가 설정되지 않아도 마찬가지입니다. 시계열 코드는 데이터 준비가 잘못되어 있으면 아무것도 동작하지 않습니다.

바이브코딩에서 시계열 처리는 준비 단계가 절반 이상입니다. AI가 `resample`이나 `rolling` 코드를 생성하기 전에 날짜 열을 제대로 파싱하고, 날짜 인덱스로 설정하는 것이 선행되어야 합니다. 이 준비가 잘 되어 있으면 AI 코드가 훨씬 자연스럽게 동작합니다.

이번 글에서는 시계열 데이터를 다루기 위한 준비 과정과 핵심 패턴을 바이브코딩 관점에서 정리합니다. `dt` accessor, `resample`, `rolling`이 핵심입니다.

> **바이브코딩 관점:** AI가 `resample` 코드를 생성했는데 오류가 난다면 날짜 인덱스 설정이 빠진 것입니다. "날짜 열을 인덱스로 설정하고 resample을 사용하는 전체 코드를 작성해줘"라고 요청하면 됩니다.

## 이 글에서 다룰 질문

- AI가 생성한 `resample` 코드가 오류가 나는 이유는 무엇일까요?
- 날짜 열을 인덱스로 설정하면 어떤 기능이 열릴까요?
- `dt` accessor로 연/월/일/요일을 어떻게 추출할까요?
- 이동 평균처럼 창 기반 계산을 어떻게 할까요?
- 시계열 데이터에서 자주 나오는 NaN은 어떻게 처리할까요?

---

## 시계열의 핵심: 날짜 인덱스

시계열 처리의 대부분은 날짜 열을 제대로 인식하고, 인덱스로 설정하는 것에서 시작합니다.

### 핵심 개념 용어

| 개념 | 설명 |
|---|---|
| **DatetimeIndex** | 날짜/시간을 인덱스로 가진 형태 |
| **resample** | 시간 단위를 바꿔 재집계. 일별 → 주별 → 월별 등 |
| **rolling** | 일정 구간을 밀어가며 계산. 이동 평균 등 |
| **dt accessor** | 날짜 열에서 연/월/일/요일 등 구성 요소 추출 |
| **shift** | 시계열 값을 시간 축으로 앞뒤로 이동 |

---

## Before / After: 시계열 준비 과정

**Before (AI 코드가 오류나는 상황):**
```python
# date 열이 문자열이면 resample 오류
df = pd.read_csv("sales.csv")
df.resample("W").sum()  # TypeError 발생
```

**After (올바른 준비 후 resample):**
```python
import pandas as pd

df = pd.read_csv("sales.csv", parse_dates=["date"])
df = df.set_index("date")
weekly = df.resample("W").sum()
print(weekly.head())
```

---

## AI가 자주 생성하는 시계열 패턴

### 날짜 인덱스 만들기

```python
import pandas as pd

# 날짜 범위 생성
idx = pd.date_range("2026-01-01", periods=10, freq="D")
ts = pd.Series(range(10), index=idx)
print(ts.head())
```

### dt accessor로 날짜 구성 요소 추출

```python
df = pd.DataFrame({
    "date": pd.date_range("2026-01-01", periods=5, freq="D"),
    "value": [10, 20, 30, 40, 50],
})

# 연/월/일/요일 추출
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["dayofweek"] = df["date"].dt.dayofweek   # 0=월요일
df["quarter"] = df["date"].dt.quarter

print(df.head())
```

**출력:**
```
        date  value  year  month  dayofweek  quarter
0 2026-01-01     10  2026      1          3        1
1 2026-01-02     20  2026      1          4        1
```

월별, 요일별 집계가 필요할 때 이 패턴을 사용합니다.

### resample: 시간 단위 변환

```python
ts = pd.Series(range(10), index=pd.date_range("2026-01-01", periods=10, freq="D"))

# 3일 단위로 합산
print(ts.resample("3D").sum())

# 주간 합계
print(ts.resample("W").sum())

# 월간 평균
print(ts.resample("ME").mean())
```

**출력 (3D):**
```
2026-01-01     3
2026-01-04    12
2026-01-07    21
2026-01-10     9
Freq: 3D, dtype: int64
```

`resample`은 항상 집계 함수와 함께 써야 합니다. `resample("W")` 만으로는 아무것도 반환되지 않습니다.

### rolling: 이동 창 계산

```python
# 3일 이동 평균
print(ts.rolling(window=3).mean())
```

처음 2개 행은 창을 채울 데이터가 부족해 NaN이 됩니다. `min_periods`로 조정할 수 있습니다:

```python
# 최소 1개 값이 있으면 계산
print(ts.rolling(window=3, min_periods=1).mean())
```

### 시간 구간으로 자르기

```python
ts = pd.Series(range(10), index=pd.date_range("2026-01-01", periods=10, freq="D"))

# 문자열로 날짜 범위 슬라이싱
print(ts.loc["2026-01-03":"2026-01-06"])
```

---

## AI 코드에서 자주 보이는 실수 패턴

| 실수 유형 | 문제 | 해결 방법 |
|---|---|---|
| 날짜가 문자열인 채로 resample | TypeError 발생 | `parse_dates` 또는 `pd.to_datetime()` 사용 |
| 날짜 인덱스 설정 안 함 | resample이 동작 안 함 | `df.set_index("date")` 선행 |
| resample만 호출 | 집계 함수 없으면 결과 없음 | `.sum()`, `.mean()` 등 추가 |
| rolling NaN 처리 누락 | 초기 행 NaN을 모르고 분석 | `min_periods` 설정 또는 NaN 처리 코드 추가 |
| 시간대 혼용 | tz-aware와 tz-naive 섞임 | `tz_localize` 후 `tz_convert` 사용 |

---

## AI 팁: 이런 프롬프트를 써보세요

**날짜 준비 요청:**
> "이 DataFrame의 'date' 열을 날짜형으로 변환하고 인덱스로 설정한 뒤, 주간 합계를 계산하는 코드를 작성해줘."

**dt accessor 활용 요청:**
> "date 열에서 연도, 월, 요일(0=월요일)을 각각 별도 열로 추가하는 코드를 작성해줘."

**이동 평균 요청:**
> "이 일별 데이터에서 7일 이동 평균을 계산하고, 초기 NaN을 최소 3개 값이 있으면 계산하도록 설정해줘."

---

## 체크리스트

- [ ] `parse_dates`로 CSV를 읽을 때 날짜 열을 처리할 수 있다
- [ ] `set_index("date")`로 날짜 인덱스를 설정할 수 있다
- [ ] `dt.year`, `dt.month`, `dt.dayofweek`로 날짜 구성 요소를 추출할 수 있다
- [ ] `resample()`에 집계 함수를 연결해서 사용할 수 있다
- [ ] `rolling(window=n).mean()`으로 이동 평균을 계산할 수 있다

---

## 처음 질문으로 돌아가기

- **AI가 생성한 `resample` 코드가 오류가 나는 이유는?**
  - 날짜 열이 문자열로 남아 있거나, 날짜 인덱스가 설정되지 않았기 때문입니다. `parse_dates`와 `set_index("date")`가 선행되어야 합니다.
- **`dt` accessor로 연/월/일/요일을 어떻게 추출할까요?**
  - `df["date"].dt.year`, `df["date"].dt.month`, `df["date"].dt.dayofweek`으로 추출합니다. 월별, 요일별 집계의 기준 열로 활용합니다.
- **이동 평균처럼 창 기반 계산을 어떻게 할까요?**
  - `series.rolling(window=7).mean()`으로 7일 이동 평균을 계산합니다. 초기 NaN은 `min_periods` 옵션으로 조정합니다.

---

## 정리

시계열 분석의 출발점은 날짜를 날짜형으로 인식하고 인덱스로 올려두는 일입니다. 이 준비가 되면 기간 선택, 단위 변환, 이동 계산이 모두 같은 언어 안에서 풀립니다. AI에게 시계열 코드를 요청할 때 "날짜 열 준비부터 포함해서 전체 코드를 작성해줘"라고 명시하면 오류 없는 코드를 받을 수 있습니다. 다음 글에서는 성능과 직결되는 벡터화와 `apply`를 다룹니다.

---

## 참고 자료

- [pandas Time series / date functionality](https://pandas.pydata.org/docs/user_guide/timeseries.html)
- [pandas resample 문서](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html)
- [pandas rolling 문서](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html)
- [예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Pandas 기초 (1/10): Pandas란 무엇인가?
- 바이브코딩을 위한 Pandas 기초 (2/10): 시리즈와 데이터프레임
- 바이브코딩을 위한 Pandas 기초 (3/10): CSV와 Excel 읽기
- 바이브코딩을 위한 Pandas 기초 (4/10): 필터링과 선택
- 바이브코딩을 위한 Pandas 기초 (5/10): 결측치 처리
- 바이브코딩을 위한 Pandas 기초 (6/10): 그룹화와 집계
- 바이브코딩을 위한 Pandas 기초 (7/10): 병합과 조인
- **바이브코딩을 위한 Pandas 기초 (8/10): 시계열 데이터 다루기 (현재 글)**
- 바이브코딩을 위한 Pandas 기초 (9/10): 적용 함수와 벡터화
- 바이브코딩을 위한 Pandas 기초 (10/10): 실전 데이터 분석
<!-- toc:end -->

Tags: 바이브코딩, Pandas, 시계열, resample, 날짜

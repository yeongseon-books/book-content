---
series: pandas-101
episode: 5
title: "Pandas 101 (5/10): 결측치 처리"
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
  - MissingValues
  - DataCleaning
  - Python
  - Beginner
seo_description: 결측치를 분석 신호로 보고 진단, 제거, 대체, 보간 등 상황별 처리 전략을 익힙니다. 왜곡을 줄이는 정제 원칙과 실무 패턴을 정리합니다.
last_reviewed: '2026-05-15'
---

# Pandas 101 (5/10): 결측치 처리

현실 데이터는 깔끔하게 채워져 있지 않습니다. 센서가 값을 놓치고, 설문 응답이 비고, 거래 로그 일부가 비정상적으로 빠지기도 합니다. 그래서 결측치를 어떻게 다루는지는 정제 단계의 작은 선택이 아니라 분석 신뢰도를 결정하는 핵심 판단이 됩니다.

이 글은 Pandas 101 시리즈의 5번째 글입니다.

이번 글에서는 `NaN`을 단순히 지워야 할 쓰레기 값으로 보지 않고, 데이터가 왜 비어 있는지 해석해야 할 신호로 보겠습니다.

![Pandas 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/05/05-01-concept-at-a-glance.ko.png)
*Pandas 101 5장 흐름 개요*
> **결측치는 오류가 아니라 신호**입니다. 제거와 대체는 모두 장단점이 있고, 선택에 따라 분포가 왜곡되거나 표본이 줄어듭니다.

## 이 글에서 다룰 문제

- `NaN`과 `pd.NA`는 어떤 의미를 가질까요?
- 결측치를 먼저 어떻게 진단해야 할까요?
- 언제 제거하고 언제 채워야 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

결측치 처리 방식은 모델 성능과 분석 해석을 모두 바꿉니다. 같은 데이터라도 무작정 `dropna`를 쓰면 표본이 심하게 줄어들 수 있고, 무심코 0이나 평균으로 채우면 분포가 왜곡될 수 있습니다.

## 핵심 개념 정의

- **NaN**: 숫자형 결측을 나타내는 대표 표식입니다.
- **pd.NA**: Pandas 1.0 이후의 통합 결측 표식입니다.
- **행 또는 열 제거**: 결측이 있는 축을 삭제하는 방식입니다.
- **채우기**: 상수, 평균, 이전 값 등으로 대체하는 방식입니다.
- **보간**: 주변 값을 이용해 중간 값을 추정하는 방식입니다.

## 전과 후

이전 관점: `dropna()` 한 줄로 끝내고 데이터 대부분을 잃습니다.

이후 관점: 결측 원인에 따라 제거, 대체, 보간을 다르게 선택합니다.

## 실습: 결측치를 다루는 다섯 단계

### 1단계 - 결측치 진단하기

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({
    "user_id":   [1, 2, 3, 4, 5, 6, 7, 8],
    "age":       [25, np.nan, 35, 45, np.nan, 28, np.nan, 52],
    "income":    [50000, 60000, np.nan, 80000, 45000, np.nan, 70000, 90000],
    "score":     [8.5, 7.2, 9.0, np.nan, 6.8, 7.9, np.nan, 8.1],
    "region":    ["서울", "부산", "서울", np.nan, "대구", "서울", "부산", np.nan],
})

# 기본 진단
print("결측치 개수:\n", df.isna().sum())
print()
print("결측치 비율 (%):")
print((df.isna().sum() / len(df) * 100).round(1))
print()

# 행별 결측 개수
df["missing_count"] = df.isna().sum(axis=1)
print("행별 결측 개수:")
print(df[["user_id", "missing_count"]].to_string(index=False))
```

**예상 출력:**

```text
결측치 개수:
 user_id    0
age        3
income     2
score      2
region     2
dtype: int64

결측치 비율 (%):
user_id     0.0
age        37.5
income     25.0
score      25.0
region     25.0
dtype: float64
```

진단 단계에서는 어떤 열에 결측이 몰려 있는지 먼저 확인해야 합니다. 결측 비율이 높은 열은 제거를 고려하고, 낮은 열은 대체 전략을 씁니다.

### 2단계 - 결측치 제거하기

```python
df_clean = df.drop(columns=["missing_count"])

# 행 제거 (any: 하나라도 결측, all: 전부 결측)
removed_any = df_clean.dropna()
removed_thresh = df_clean.dropna(thresh=4)   # 최소 4개 이상 유효값

print(f"원본 행 수: {len(df_clean)}")
print(f"dropna() 후: {len(removed_any)}행 ({len(df_clean) - len(removed_any)}행 제거)")
print(f"thresh=4 후: {len(removed_thresh)}행 ({len(df_clean) - len(removed_thresh)}행 제거)")

# 특정 열 기준
removed_age = df_clean.dropna(subset=["age", "income"])
print(f"age+income 기준 제거 후: {len(removed_age)}행")
```

**예상 출력:**

```text
원본 행 수: 8
dropna() 후: 2행 (6행 제거)
thresh=4 후: 5행 (3행 제거)
age+income 기준 제거 후: 5행
```

제거는 간단하지만 비용이 큽니다. `thresh`를 활용하면 너무 많은 데이터를 잃지 않으면서 불완전한 행을 걸러낼 수 있습니다.

### 3단계 - 값으로 채우기

```python
df_fill = df.drop(columns=["missing_count"])

# 상수 대체
df_zero = df_fill.fillna({"age": 0, "income": 0, "score": 0, "region": "미상"})

# 통계 대체
df_stat = df_fill.copy()
df_stat["age"]    = df_stat["age"].fillna(df_stat["age"].median())
df_stat["income"] = df_stat["income"].fillna(df_stat["income"].mean())
df_stat["score"]  = df_stat["score"].fillna(df_stat["score"].mean())
df_stat["region"] = df_stat["region"].fillna(df_stat["region"].mode()[0])

print("통계 대체 결과:")
print(df_stat.to_string())
```

**예상 출력:**

```text
통계 대체 결과:
   user_id   age     income  score region
0        1  25.0  50000.000    8.5     서울
1        2  31.0  60000.000    7.2     부산
2        3  35.0  65000.000    9.0     서울
3        4  45.0  80000.000    7.9     서울
4        5  31.0  45000.000    6.8     대구
5        6  28.0  65000.000    7.9     서울
6        7  31.0  70000.000    7.9     부산
7        8  52.0  90000.000    8.1     서울
```

### 4단계 - 앞값/뒷값으로 채우기 (시계열에 적합)

```python
ts = pd.DataFrame({
    "date":  pd.date_range("2026-01-01", periods=7),
    "sales": [100, np.nan, np.nan, 130, np.nan, 110, 120],
})
ts = ts.set_index("date")

ts["ffill"] = ts["sales"].ffill()        # 앞값 채우기
ts["bfill"] = ts["sales"].bfill()        # 뒷값 채우기
ts["interp"] = ts["sales"].interpolate() # 선형 보간

print(ts.to_string())
```

**예상 출력:**

```text
            sales  ffill  bfill  interp
date
2026-01-01  100.0  100.0  100.0  100.00
2026-01-02    NaN  100.0  130.0  110.00
2026-01-03    NaN  100.0  130.0  120.00
2026-01-04  130.0  130.0  130.0  130.00
2026-01-05    NaN  130.0  110.0  123.33
2026-01-06  110.0  110.0  110.0  110.00
2026-01-07  120.0  120.0  120.0  120.00
```

`ffill`은 직전 값을 그대로 복사하고, `bfill`은 다음 값을 사용합니다. `interpolate`는 선형으로 중간 값을 추정해 흐름을 보존합니다.

### 5단계 - 그룹별 대체 (고급)

```python
df_group = pd.DataFrame({
    "dept":   ["Engineering", "Engineering", "Marketing", "Marketing", "Engineering"],
    "salary": [90000, np.nan, 70000, np.nan, 95000],
})

# 같은 부서 평균으로 대체
df_group["salary_filled"] = df_group.groupby("dept")["salary"].transform(
    lambda x: x.fillna(x.mean())
)
print(df_group)
```

**예상 출력:**

```text
          dept   salary  salary_filled
0  Engineering  90000.0        90000.0
1  Engineering      NaN        92500.0
2    Marketing  70000.0        70000.0
3    Marketing      NaN        70000.0
4  Engineering  95000.0        95000.0
```

같은 범주에 속한 데이터의 평균으로 대체하면 전체 평균보다 더 정확한 추정이 됩니다.

## 결측치 처리 방법 비교

| 방법 | 함수 | 장점 | 단점 | 적합한 상황 |
| --- | --- | --- | --- | --- |
| 행 제거 | `dropna()` | 간단, 정확 | 표본 감소 | 결측 비율 < 5% |
| 상수 대체 | `fillna(0)` | 예측 가능 | 분포 왜곡 | 결측=0의 의미가 명확할 때 |
| 통계 대체 | `fillna(mean)` | 중심 경향 보존 | 분산 감소 | 연속값, MAR 가정 |
| 앞/뒤 채우기 | `ffill/bfill` | 순서 보존 | 끝단 결측 유지 | 시계열, 순서 있는 데이터 |
| 선형 보간 | `interpolate()` | 흐름 보존 | 이상치 민감 | 연속 시계열 |
| 그룹 평균 | `transform` | 맥락 반영 | 복잡도 증가 | 범주별 특성이 다를 때 |

각 방법은 장단점이 명확합니다. 데이터의 특성과 분석 목적에 따라 적절한 방법을 선택해야 합니다.

## 결측 패턴 분석

```python
import matplotlib.pyplot as plt

df_pattern = pd.DataFrame({
    "A": [1, np.nan, 3, np.nan, 5, 6, np.nan, 8],
    "B": [np.nan, 2, 3, 4, 5, np.nan, 7, 8],
    "C": [1, 2, 3, 4, 5, 6, 7, 8],
    "D": [np.nan, np.nan, 3, np.nan, np.nan, 6, np.nan, np.nan],
})

# 열별 결측 비율 시각화
missing_ratio = df_pattern.isna().mean() * 100
print("열별 결측 비율 (%):")
print(missing_ratio)

# 결측 패턴 행렬 (0=존재, 1=결측)
missing_map = df_pattern.isna().astype(int)
print("\n결측 패턴 행렬:")
print(missing_map.to_string())
```

**예상 출력:**

```text
열별 결측 비율 (%):
A    37.5
B    25.0
C     0.0
D    62.5
dtype: float64

결측 패턴 행렬:
   A  B  C  D
0  0  1  0  1
1  1  0  0  1
2  0  0  0  0
3  1  0  0  1
4  0  0  0  1
5  0  1  0  0
6  1  0  0  1
7  0  0  0  1
```

열 D처럼 결측 비율이 62%를 넘으면 해당 열을 아예 제거하거나 결측 여부 자체를 이진 특징으로 사용하는 방법을 고려합니다.

## 결측 여부를 특징으로 활용

```python
df_ml = pd.DataFrame({
    "age":    [25, np.nan, 35, np.nan, 50],
    "income": [50000, 60000, np.nan, 80000, 70000],
    "target": [0, 1, 0, 1, 1],
})

# 결측 여부를 별도 열로
df_ml["age_missing"]    = df_ml["age"].isna().astype(int)
df_ml["income_missing"] = df_ml["income"].isna().astype(int)

# 결측치 채우기 (ML 모델에 NaN 불가)
df_ml["age"]    = df_ml["age"].fillna(df_ml["age"].median())
df_ml["income"] = df_ml["income"].fillna(df_ml["income"].median())

print(df_ml)
```

**예상 출력:**

```text
    age  income  target  age_missing  income_missing
0  25.0  50000.0       0            0               0
1  35.0  60000.0       1            1               0
2  35.0  65000.0       0            0               1
3  35.0  80000.0       1            1               0
4  50.0  70000.0       1            0               0
```

머신러닝에서는 결측 여부 자체가 중요한 패턴을 담고 있을 수 있습니다. 이진 플래그를 별도 열로 추가하면 모델이 결측 패턴을 학습할 수 있습니다.

## 이상치를 결측치로 변환

```python
df_outlier = pd.DataFrame({
    "temperature": [-999, 25, 30, 28, 999, 22, 27, -888],
    "humidity":    [60, 65, 200, 55, 70, 68, 110, 62],
})

# 범위 밖 값을 NaN으로
df_outlier["temperature"] = df_outlier["temperature"].where(
    df_outlier["temperature"].between(-50, 60)
)
df_outlier["humidity"] = df_outlier["humidity"].where(
    df_outlier["humidity"].between(0, 100)
)

print(df_outlier)
print()
print("처리 후 결측치:\n", df_outlier.isna().sum())
```

**예상 출력:**

```text
   temperature  humidity
0          NaN      60.0
1         25.0      65.0
2         30.0       NaN
3         28.0      55.0
4          NaN      70.0
5         22.0      68.0
6         27.0       NaN
7          NaN      62.0

처리 후 결측치:
 temperature    3
humidity       2
dtype: int64
```

이상치를 결측치로 변환하는 전략은 데이터 정제의 흔한 패턴입니다. 원본 데이터는 별도로 보관하는 것이 안전합니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| `dropna` 남용 | 데이터 80% 소실 | 결측 비율 확인 후 `thresh` 활용 |
| 0으로 무조건 채우기 | 분포 왜곡, 0의 의미 혼동 | 결측 원인 파악 후 전략 선택 |
| `ffill`로 선두 결측 방치 | 첫 행 NaN 유지 | `bfill` 또는 상수 대체 병행 |
| 범주형 열에 숫자 평균 채우기 | 의미 없는 값 생성 | `mode()[0]`(최빈값) 사용 |
| 결측 처리 기준 미기록 | 재현 불가능 | 처리 정책을 코드 주석에 명시 |

## 실무에서는 이렇게 생각합니다

- 결측을 처리하기 전에 왜 비었는지 먼저 묻습니다.
- 처리 정책을 코드와 문서에 함께 남깁니다.
- 필요하면 결측 여부 자체를 별도 열로 남깁니다.
- 시계열에서는 보간을 적극적으로 검토합니다.
- 머신러닝에서는 결측 자체를 특징으로 활용할지 판단합니다.

## 운영 체크리스트

- [ ] `isna().sum()`으로 결측 규모를 진단할 수 있습니다.
- [ ] `dropna`가 데이터 양에 주는 영향을 측정합니다.
- [ ] `fillna` 전략을 명시적으로 정합니다.
- [ ] 결측 비율과 처리 기준을 기록합니다.
- [ ] 그룹별 대체를 `transform`으로 구현할 수 있습니다.

## 연습 문제

1. 열별 결측 비율을 계산하고 50% 이상인 열을 자동으로 제거하는 코드를 작성해 보세요.
2. `dropna` 전후의 행 수를 비교하고 표본 손실 비율을 계산해 보세요.
3. 시계열에서 `ffill`, `bfill`, `interpolate()`의 결과를 나란히 비교해 보세요.
4. 결측 여부를 이진 특징으로 추가한 뒤 원본 결측치를 중앙값으로 채우는 파이프라인을 작성해 보세요.

## 정리와 다음 글

결측치 처리는 데이터를 깨끗하게 만드는 작업이 아니라 데이터의 의미를 보존하는 작업입니다. 원인을 묻고 정책을 분명히 해야 분석 무결성이 유지됩니다. 다음 글에서는 여러 행을 기준별로 묶어 집계하는 `groupby`를 다루겠습니다.

## 처음 질문으로 돌아가기

- **`NaN`과 `pd.NA`는 어떤 의미를 가질까요?**
  - `NaN`은 NumPy의 float 결측 표식이고, `pd.NA`는 Pandas 1.0 이후에 추가된 정수/문자열/불리언 등 모든 타입을 위한 통합 결측 표식입니다.
- **결측치를 먼저 어떻게 진단해야 할까요?**
  - `isna().sum()`으로 열별 결측 개수를, `isna().mean() * 100`으로 비율을 확인합니다. 결측 비율이 높은 열과 낮은 열을 구분해 전략을 다르게 씁니다.
- **언제 제거하고 언제 채워야 할까요?**
  - 결측 비율이 낮고(5% 미만) 패턴이 무작위이면 제거가 안전합니다. 결측이 많거나 패턴이 있으면 대체 또는 보간이 적합합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- **Pandas 101 (5/10): 결측치 처리 (현재 글)**
- [Pandas 101 (6/10): 그룹화와 집계](./06-groupby.md)
- [Pandas 101 (7/10): 병합과 조인](./07-merge-and-join.md)
- [Pandas 101 (8/10): 시계열 데이터 다루기](./08-time-series.md)
- [Pandas 101 (9/10): 적용 함수와 벡터화](./09-apply-and-vectorization.md)
- [실전 데이터 분석](./10-real-world-data-analysis.md)

<!-- toc:end -->

## 참고 자료

- [pandas — Working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [pandas — fillna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html)
- [pandas — interpolate](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html)
- [scikit-learn — Imputation](https://scikit-learn.org/stable/modules/impute.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, MissingValues, DataCleaning, Python, Beginner

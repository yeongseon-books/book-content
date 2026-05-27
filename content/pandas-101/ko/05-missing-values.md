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

## 먼저 던지는 질문

- `NaN`과 `pd.NA`는 어떤 의미를 가질까요?
- 결측치를 먼저 어떻게 진단해야 할까요?
- 언제 제거하고 언제 채워야 할까요?

## 왜 중요한가

결측치 처리 방식은 모델 성능과 분석 해석을 모두 바꿉니다. 같은 데이터라도 무작정 `dropna`를 쓰면 표본이 심하게 줄어들 수 있고, 무심코 0이나 평균으로 채우면 분포가 왜곡될 수 있습니다.

## 핵심 용어

- **NaN**: 숫자형 결측을 나타내는 대표 표식입니다.
- **통합 결측 표식**: Pandas가 제공하는 결측 표현입니다.
- **행 또는 열 제거**: 결측이 있는 축을 삭제하는 방식입니다.
- 채우기: 상수, 평균, 이전 값 등으로 대체하는 방식입니다.
- 보간: 주변 값을 이용해 중간 값을 추정하는 방식입니다.

## 전과 후

이전 관점: `dropna()` 한 줄로 끝내고 데이터 대부분을 잃습니다.

이후 관점: 결측 원인에 따라 제거, 대체, 보간을 다르게 선택합니다.

## 실습: 결측치를 다루는 다섯 단계

### 1단계 - 결측치 찾기

```python
import numpy as np, pandas as pd
df = pd.DataFrame({"x": [1, np.nan, 3], "y": [np.nan, 2, 3]})
print(df.isna())
print(df.isna().sum())
```

진단 단계에서는 어떤 열에 결측이 몰려 있는지 먼저 확인해야 합니다. 숫자 하나만 봐도 제거가 나은지, 채우기가 나은지 판단의 출발점이 생깁니다.

**예상 출력:**

```text
x    1
y    1
dtype: int64
```

결측치 처리는 항상 진단에서 시작합니다. 특히 `isna().sum()`은 열별 결측 규모를 가장 빠르게 보여 주는 기본 점검입니다.

### 2단계 - 제거하기

```python
print(df.dropna())            # drop rows with any NaN
print(df.dropna(axis=1))      # drop columns with any NaN
```

제거는 간단하지만 비용이 큽니다. 어떤 행이나 열이 얼마나 사라지는지 측정하지 않으면 분석 대상 자체가 바뀔 수 있습니다.

### 3단계 - 값 채우기

```python
print(df.fillna(0))
print(df.fillna(df.mean(numeric_only=True)))
```

상수나 평균으로 채우는 방식은 빠르지만 의미가 약할 수 있습니다. 특히 평균 대체는 분포와 분산을 왜곡할 수 있다는 점을 염두에 둬야 합니다.

## 결측치 처리 방법 비교

결측치를 다루는 주요 방법을 표로 정리하면 상황별 선택 기준이 명확해집니다.

| 방법 | 함수 | 장점 | 단점 |
| --- | --- | --- | --- |
| 제거 | `dropna()` | 간단, 빠름 | 표본 감소 |
| 상수 대체 | `fillna(value)` | 간단, 예측 가능 | 분포 왜곡 |
| 통계 대체 | `fillna(df.mean())` | 중심 경향 보존 | 분산 감소 |
| 전후 채우기 | `ffill()`, `bfill()` | 시계열에 적합 | 끝단 결측 유지 |
| 보간 | `interpolate()` | 흐름 보존 | 복잡도 증가 |

각 방법은 장단점이 명확합니다. 데이터의 특성과 분석 목적에 따라 적절한 방법을 선택해야 합니다.

### 4단계 - 앞값이나 뒷값으로 채우기

```python
print(df.fillna(method="ffill"))
print(df.fillna(method="bfill"))
```

앞값 채우기와 뒷값 채우기는 순서가 있는 데이터에서 자주 쓰입니다. 다만 선두 결측이나 후미 결측은 그대로 남을 수 있으니 끝단 처리를 따로 생각해야 합니다.

### 5단계 - 보간하기

```python
ts = pd.Series([1.0, np.nan, np.nan, 4.0])
print(ts.interpolate())
```

보간은 앞뒤 값을 이어 빈 구간을 메우는 방식이라 시계열에서 특히 자연스럽습니다. 단순 상수 대체와 달리 흐름을 어느 정도 보존한다는 점을 눈으로 확인해 보세요.

**예상 출력:**

```text
0    1.0
1    2.0
2    3.0
3    4.0
dtype: float64
```

보간은 시계열처럼 흐름이 있는 데이터에 특히 잘 맞습니다. 모든 결측에 쓸 수 있는 만능 도구는 아니지만, 연속값의 빈 구간을 다룰 때는 매우 자연스럽습니다.

## 복합 조건 필터링

결측치를 기준으로 필터링할 때는 보통 여러 조건을 조합합니다.

### 특정 열에 결측이 있는 행

```python
df = pd.DataFrame({
    "x": [1, np.nan, 3],
    "y": [np.nan, 2, 3],
})
has_missing_x = df[df["x"].isna()]
print(has_missing_x)
```

특정 열에만 결측치가 있는 행을 골라내면 결측 패턴을 분석할 수 있습니다.

### 모든 열이 비지 않은 행

```python
complete_rows = df.dropna()
print(complete_rows)
```

모든 열이 채워져 있는 행만 남기면 완전한 데이터셋을 얻지만, 표본 크기는 크게 줄어듭니다.

### query로 결측치 필터링

Pandas 1.x부터는 `query`에서 `isna()`를 직접 쓸 수 없지만, 조건식을 미리 계산해 두면 가독성을 높일 수 있습니다.

```python
df["has_x"] = df["x"].notna()
result = df.query("has_x == True")
print(result)
```

## 이 코드에서 먼저 봐야 할 점

- `isna().sum()`은 결측 진단의 첫 단계입니다.
- 평균 대체는 분포를 왜곡할 수 있습니다.
- `interpolate()`는 시계열 결측에 잘 맞습니다.

## 자주 하는 실수 다섯 가지

1. `dropna`를 남용해 대부분의 행을 잃습니다.
2. 0으로 채워 분포를 인위적으로 바꿉니다.
3. `ffill`만 쓰고 선두 결측을 놓칩니다.
4. 범주형 열에 평균을 채우려 합니다.
5. 결측 처리 기준을 기록하지 않은 채 임의로 바꿉니다.

## 실무에서는 이렇게 이어집니다

센서 데이터, 설문 데이터, 거래 로그에서는 결측 패턴 자체가 중요한 신호일 수 있습니다. 그래서 결측 원인 가설을 먼저 세우고, 처리 방식을 문서화한 뒤 분석이나 모델링에 들어가는 편이 안전합니다.

## 실무에서는 이렇게 생각합니다

- 결측을 처리하기 전에 왜 비었는지 먼저 묻습니다.
- 처리 정책을 코드와 문서에 함께 남깁니다.
- 필요하면 결측 여부 자체를 별도 열로 남깁니다.
- 시계열에서는 보간을 적극적으로 검토합니다.
- 머신러닝에서는 결측 자체를 특징으로 활용할지 판단합니다.

## 고급 결측치 처리 기법

실무에서는 단순한 대체보다 더 정교한 방법이 필요할 때가 있습니다.

### 그룹별 평균 대체

```python
df = pd.DataFrame({
    "category": ["A", "A", "B", "B", "B"],
    "value": [10, np.nan, 20, 25, np.nan],
})
df["value"] = df.groupby("category")["value"].transform(
    lambda x: x.fillna(x.mean())
)
print(df)
```

같은 범주에 속한 데이터의 평균으로 대체하면 전체 평균보다 더 정확할 수 있습니다.

### 결측 여부를 특징으로 활용

```python
df["value_missing"] = df["value"].isna().astype(int)
print(df.head())
```

머신러닝에서는 결측 여부 자체가 중요한 정보일 수 있습니다. 별도 특징으로 추가하면 모델이 결측 패턴을 학습할 수 있습니다.

### 조건부 대체

```python
df["value"] = df["value"].apply(
    lambda x: 0 if pd.isna(x) and some_condition else x
)
```

특정 조건에서만 결측치를 대체하고 싶을 때는 `apply`와 조건식을 결합할 수 있습니다.

## 결측치 비율 분석

결측치를 처리하기 전에 그 규모와 분포를 파악하는 것이 중요합니다.

### 열별 결측 비율

```python
df = pd.DataFrame({
    "a": [1, np.nan, 3, np.nan, 5],
    "b": [np.nan, 2, 3, 4, 5],
    "c": [1, 2, 3, 4, 5],
})
missing_ratio = df.isna().sum() / len(df) * 100
print(missing_ratio)
```

**예상 출력:**

```text
a    40.0
b    20.0
c     0.0
dtype: float64
```

결측 비율이 높은 열은 아예 제거하거나 별도로 처리하는 편이 나을 수 있습니다.

### 행별 결측 개수

```python
missing_per_row = df.isna().sum(axis=1)
print(missing_per_row)
```

행마다 결측 개수를 세면 어떤 행이 데이터 품질이 낮은지 파악할 수 있습니다.

### 결측 패턴 시각화

```python
import matplotlib.pyplot as plt
df.isna().sum().plot(kind="bar")
plt.title("Missing Values per Column")
plt.ylabel("Count")
plt.show()
```

시각화를 통해 결측 분포를 한눈에 파악할 수 있습니다. 특정 열에 결측이 몰려 있다면 그 원인을 분석할 필요가 있습니다.

## 체크리스트

- [ ] `isna().sum()`으로 결측 규모를 진단할 수 있습니다.
- [ ] `dropna`가 데이터 양에 주는 영향을 측정합니다.
- [ ] `fillna` 전략을 명시적으로 정합니다.
- [ ] 결측 비율과 처리 기준을 기록합니다.

## 결측 패턴 분석

결측치를 처리하기 전에 패턴을 분석하면 더 나은 전략을 세울 수 있습니다.

### 결측 상관관계

```python
import seaborn as sns
import matplotlib.pyplot as plt

missing = df.isna()
correlation = missing.corr()
sns.heatmap(correlation, annot=True)
plt.title("Missing Value Correlation")
plt.show()
```

특정 열들의 결측치가 함께 나타나는 패턴이 있다면, 이는 데이터 수집 과정의 문제를 시사할 수 있습니다.

### 시계열 결측 패턴

```python
df["date"] = pd.to_datetime(df["date"])
df.set_index("date", inplace=True)
missing_by_time = df.isna().resample("D").sum()
missing_by_time.plot()
plt.title("Missing Values Over Time")
plt.show()
```

시간에 따른 결측치 분포를 보면 시스템 장애나 계절성 패턴을 발견할 수 있습니다.

### 머신러닝에서의 결측치

머신러닝 모델에서는 결측치 처리 전략이 모델 성능에 직접 영향을 줍니다.

```python
from sklearn.impute import SimpleImputer

# Scikit-learn imputer 사용
imputer = SimpleImputer(strategy="median")
df_imputed = pd.DataFrame(
    imputer.fit_transform(df),
    columns=df.columns
)
print(df_imputed.isna().sum())
```

Pandas 기본 기능 외에도 scikit-learn의 Imputer를 활용할 수 있습니다.

## 결측치 생성 패턴

때로는 의도적으로 결측치를 생성해야 할 때도 있습니다.

```python
# 조건부로 NaN 설정
df.loc[df["value"] < 0, "value"] = np.nan

# 특정 값을 NaN으로 변환
df.replace(-999, np.nan, inplace=True)

# 범위 밖 값을 NaN으로
df["temperature"] = df["temperature"].where(
    (df["temperature"] >= -50) & (df["temperature"] <= 50)
)
```

이상치를 결측치로 처리하는 것도 정제 전략 중 하나입니다.

이상치를 결측치로 변환하는 전략은 통계 분석에서 자주 사용됩니다. 다만 원본 데이터는 별도로 보관하는 것이 안전합니다.

## 결측 패턴 시각화

결측 패턴을 시각화하면 데이터의 구조적 문제를 발견할 수 있습니다.

```python
import matplotlib.pyplot as plt

missing_pattern = df.isna().astype(int)
plt.imshow(missing_pattern, cmap="gray", aspect="auto")
plt.xlabel("Column")
plt.ylabel("Row")
plt.title("Missing Value Pattern")
plt.show()
```

결측이 무작위로 퍼져 있는지, 특정 구간에 몰려 있는지에 따라 처리 전략이 달라집니다.

## 연습 문제

1. 열별 결측 비율을 계산해 보세요.
2. `dropna` 전후의 행 수를 비교해 보세요.
3. 시계열에서 `ffill`과 `interpolate()`의 결과 차이를 살펴보세요.

## 정리와 다음 글

결측치 처리는 데이터를 깨끗하게 만드는 작업이 아니라 데이터의 의미를 보존하는 작업입니다. 원인을 묻고 정책을 분명히 해야 분석 무결성이 유지됩니다. 다음 글에서는 여러 행을 기준별로 묶어 집계하는 `groupby`를 다루겠습니다.

## 처음 질문으로 돌아가기

- **`NaN`과 `pd.NA`는 어떤 의미를 가질까요?**
  - 둘 다 값이 비어 있음을 나타내지만, 핵심은 결측을 단순 오류가 아니라 해석해야 할 상태로 보는 데 있습니다. 본문도 `np.nan`이 들어 있는 DataFrame을 만든 뒤 이를 바로 지우지 않고 진단, 대체, 보간의 출발점으로 다뤘습니다.
- **결측치를 먼저 어떻게 진단해야 할까요?**
  - 가장 먼저 `isna()`와 `isna().sum()`으로 어느 열에 결측이 얼마나 몰려 있는지 봐야 합니다. 이후 `missing_ratio = df.isna().sum() / len(df) * 100`처럼 비율까지 계산하면 제거와 대체 중 무엇이 더 적절한지 판단할 근거가 생깁니다.
- **언제 제거하고 언제 채워야 할까요?**
  - 결측이 소수이고 의미 손실이 작으면 `dropna()`가 단순하지만, 흐름이 중요한 시계열이나 그룹 맥락이 있는 값은 `fillna`, `ffill`, `bfill`, `interpolate()`, 그룹별 평균 대체가 더 맞을 수 있습니다. 본문이 평균 대체의 분포 왜곡, `ffill`의 끝단 한계, `interpolate()`의 시계열 적합성을 각각 구분해 설명한 이유가 여기에 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- **결측치 처리 (현재 글)**
- 그룹화와 집계 (예정)
- 병합과 조인 (예정)
- 시계열 데이터 다루기 (예정)
- 적용 함수와 벡터화 (예정)
- 실전 데이터 분석 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — Working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [pandas — fillna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html)
- [pandas — interpolate](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html)
- [scikit-learn — Imputation](https://scikit-learn.org/stable/modules/impute.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, MissingValues, DataCleaning, Python, Beginner

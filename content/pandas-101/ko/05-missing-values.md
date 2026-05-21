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

이 글은 판다스 101 시리즈의 5번째 글입니다.

현실 데이터는 깔끔하게 채워져 있지 않습니다. 센서가 값을 놓치고, 설문 응답이 비고, 거래 로그 일부가 비정상적으로 빠지기도 합니다. 그래서 결측치를 어떻게 다루는지는 정제 단계의 작은 선택이 아니라 분석 신뢰도를 결정하는 핵심 판단이 됩니다.


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

## 한눈에 보는 개념

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

## 실전 확장: 데이터 처리 파이프라인과 성능 점검

앞선 절에서 개념과 기본 문법을 확인했다면, 이제는 실무에서 바로 재사용할 수 있는 형태로 흐름을 묶어 두는 것이 중요합니다. 이 절은 "읽기 → 정제 → 결합 → 집계 → 성능 점검 → 저장" 순서로 구성했습니다. 각 단계는 분리해서 테스트할 수 있고, 필요할 때 교체할 수 있습니다.

### 1) CSV 적재와 스키마 고정

```python
import pandas as pd

def load_orders(path: str) -> pd.DataFrame:
    return pd.read_csv(
        path,
        dtype={
            "order_id": "int64",
            "customer_id": "int64",
            "product_id": "int32",
            "qty": "int16",
            "unit_price": "float32",
            "channel": "string",
        },
        parse_dates=["order_date"],
    )

def load_customers(path: str) -> pd.DataFrame:
    return pd.read_csv(
        path,
        dtype={
            "customer_id": "int64",
            "segment": "string",
            "region": "string",
        },
        parse_dates=["signup_date"],
    )
```

자료형을 먼저 고정하면 이후 연산에서 경고가 줄고, 메모리 사용량도 예측하기 쉬워집니다. 문자열 식별자는 숫자로 변환하지 말고 원본 의미를 유지해야 합니다.

### 2) 데이터프레임 조작과 결측 처리

```python
def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.dropna(subset=["customer_id", "order_date", "qty", "unit_price"])
    df["qty"] = df["qty"].clip(lower=1)
    df["unit_price"] = df["unit_price"].clip(lower=0)
    df["order_amount"] = (df["qty"] * df["unit_price"]).astype("float32")
    df["order_month"] = df["order_date"].dt.to_period("M")
    return df
```

핵심은 복사본을 명시한 뒤 변경하는 것입니다. 체이닝 인덱싱 경고를 피하고, 각 단계의 의도를 분명히 남길 수 있습니다.

### 3) merge/join 비교와 안전한 결합

```python
def enrich_with_customer(orders: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    merged = orders.merge(
        customers,
        on="customer_id",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    # 조인 품질 확인
    print(merged["_merge"].value_counts(dropna=False))

    merged = merged.drop(columns=["_merge"])
    merged["segment"] = merged["segment"].fillna("UNKNOWN")
    merged["region"] = merged["region"].fillna("UNKNOWN")
    return merged

# 같은 작업을 인덱스 기반으로 할 때
# customers_indexed = customers.set_index("customer_id")
# orders.join(customers_indexed, on="customer_id", how="left")
```

`merge`는 열 기반 결합에, `join`은 인덱스 기반 결합에 더 자연스럽습니다. 중요한 점은 `validate`로 키 관계를 코드에 고정해 두는 것입니다.

### 4) groupby 집계와 피벗 테이블

```python
def monthly_kpi(df: pd.DataFrame) -> pd.DataFrame:
    by_month = df.groupby(["order_month", "segment"], observed=True).agg(
        orders=("order_id", "count"),
        customers=("customer_id", "nunique"),
        revenue=("order_amount", "sum"),
        aov=("order_amount", "mean"),
    ).reset_index()

    by_month["arpu_like"] = by_month["revenue"] / by_month["customers"].clip(lower=1)
    return by_month

def monthly_pivot(df: pd.DataFrame) -> pd.DataFrame:
    return df.pivot_table(
        index="order_month",
        columns="segment",
        values="order_amount",
        aggfunc="sum",
        fill_value=0,
    )
```

집계 결과는 폭이 넓은 피벗 형태와 긴 형태를 모두 준비해 두면 리포트와 후속 모델 입력에 유리합니다.

### 5) 벡터화와 iterrows 성능 벤치마크

```python
import time
import numpy as np

def benchmark_vectorized_vs_iterrows(df: pd.DataFrame) -> None:
    bench = df[["qty", "unit_price"]].copy()

    start = time.time()
    out = []
    for _, row in bench.iterrows():
        out.append(row["qty"] * row["unit_price"])
    iterrows_sec = time.time() - start

    start = time.time()
    vec = bench["qty"] * bench["unit_price"]
    vectorized_sec = time.time() - start

    print(f"iterrows: {iterrows_sec:.6f}s")
    print(f"vectorized: {vectorized_sec:.6f}s")
    print(f"speedup: {iterrows_sec / max(vectorized_sec, 1e-9):.1f}x")

    # 계산 결과 일치 확인
    assert np.allclose(np.array(out, dtype=float), vec.to_numpy(dtype=float))
```

행 반복은 학습용으로는 이해가 쉽지만, 운영 코드에서는 벡터화 연산을 우선으로 두는 편이 안전합니다. 성능뿐 아니라 코드 길이와 오류 가능성도 함께 줄어듭니다.

### 6) 메모리 최적화 규칙

```python
def optimize_memory(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 정수/실수 다운캐스팅
    for col in df.select_dtypes(include=["int64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="integer")
    for col in df.select_dtypes(include=["float64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="float")

    # 고유값이 적은 문자열 열은 category로 전환
    for col in ["segment", "region", "channel"]:
        if col in df.columns:
            ratio = df[col].nunique(dropna=False) / max(len(df), 1)
            if ratio < 0.2:
                df[col] = df[col].astype("category")

    return df
```

메모리 최적화는 대용량 데이터에서 체감 차이가 큽니다. 특히 `category` 전환은 `groupby` 속도와 메모리 사용량을 동시에 개선하는 경우가 많습니다.

### 7) 전체 파이프라인 실행 예시

```python
def run_pipeline(order_csv: str, customer_csv: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    orders = load_orders(order_csv)
    customers = load_customers(customer_csv)

    orders = clean_orders(orders)
    merged = enrich_with_customer(orders, customers)
    merged = optimize_memory(merged)

    kpi = monthly_kpi(merged)
    pivot = monthly_pivot(merged)

    benchmark_vectorized_vs_iterrows(merged)

    kpi.to_csv("kpi_monthly.csv", index=False)
    pivot.to_csv("kpi_monthly_pivot.csv")
    return kpi, pivot
```

결과를 CSV로 남기는 이유는 간단합니다. 노트북 화면에서 끝내지 않고, 다음 검토 단계와 배치 작업에서 그대로 재사용할 수 있기 때문입니다.

### 8) 운영 점검 체크리스트

- 조인 전후 행 수가 의도와 같은지 확인합니다.
- 집계 기준 열의 자료형과 시간대가 고정되어 있는지 확인합니다.
- 벡터화 가능한 계산에 `iterrows`나 `apply(axis=1)`가 남아 있지 않은지 확인합니다.
- `memory_usage(deep=True)`로 최적화 전후 변화를 기록합니다.
- 분석 결과 파일(CSV, PNG)의 생성 경로와 이름 규칙을 표준화합니다.

이 절의 목표는 기능 추가가 아니라 품질 고정입니다. 같은 입력 파일을 다시 넣었을 때 같은 지표가 나오고, 병목 구간을 재현해서 개선할 수 있어야 실무 파이프라인으로 쓸 수 있습니다.

## 실전 확장 2: 검증 가능한 분석 운영 습관

파이프라인이 길어질수록 코드 자체보다 검증 절차가 더 중요해집니다. 특히 판다스 기반 분석은 입력 파일 버전, 열 타입, 조인 키 품질에 따라 결과가 크게 달라집니다. 이 절에서는 재현성을 높이기 위한 최소 검증 세트를 정리합니다.

### 입력 검증 함수

```python
def validate_columns(df, required_cols):
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"필수 열 누락: {missing}")

def validate_dtypes(df, expected):
    for col, dtype in expected.items():
        if col not in df.columns:
            raise ValueError(f"열 없음: {col}")
        if str(df[col].dtype) != dtype:
            raise TypeError(f"{col} 자료형 불일치: {df[col].dtype} != {dtype}")
```

분석 스크립트 시작점에서 이 두 검증만 실행해도 하류 단계의 디버깅 시간을 크게 줄일 수 있습니다.

### 조인 안정성 점검

```python
def assert_merge_rowcount(before_left: int, after_merged: int, tolerance: float = 1.2):
    if after_merged > before_left * tolerance:
        raise RuntimeError(
            f"조인 후 행 수 급증: before={before_left}, after={after_merged}"
        )
```

`validate` 옵션과 함께 행 수 급증 감시를 두면 many-to-many 조인 사고를 조기에 차단할 수 있습니다.

### 그룹 집계 결과 점검

```python
def assert_non_negative(df, cols):
    for col in cols:
        if (df[col] < 0).any():
            raise ValueError(f"음수 값 발견: {col}")

def assert_no_nan(df, cols):
    for col in cols:
        if df[col].isna().any():
            raise ValueError(f"결측치 발견: {col}")
```

매출, 수량, 건수처럼 음수가 나오면 안 되는 지표를 명시적으로 점검하면 품질 문제가 빠르게 드러납니다.

### 성능 기록 템플릿

```python
import time

def timed(name, fn, *args, **kwargs):
    start = time.time()
    out = fn(*args, **kwargs)
    sec = time.time() - start
    print(f"[timing] {name}: {sec:.4f}s")
    return out
```

각 단계를 시간과 함께 기록하면 어느 구간이 병목인지 반복 실행에서 일관되게 추적할 수 있습니다.

### 저장 전 최종 점검

- 결과 데이터프레임의 행 수, 열 수, 핵심 열 결측 비율을 기록합니다.
- 파일 출력 전 `head()`와 `tail()`을 함께 확인해 경계값 오류를 찾습니다.
- 월별 집계 합계와 원본 합계가 일치하는지 대사(對査)합니다.
- 분석 코드와 결과 파일에 실행 날짜를 남겨 재현 경로를 유지합니다.

이 검증 절차는 화려한 기법이 아니라 기본 안전장치입니다. 작은 점검을 습관화하면 분석 품질이 급격히 흔들리는 상황을 안정적으로 막을 수 있습니다.

## 처음 질문으로 돌아가기

- **`NaN`과 `pd.NA`는 어떤 의미를 가질까요?**
  - 본문의 기준은 결측치 처리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **결측치를 먼저 어떻게 진단해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **언제 제거하고 언제 채워야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

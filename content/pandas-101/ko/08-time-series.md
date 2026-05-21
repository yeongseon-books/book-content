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

## 먼저 던지는 질문

- 날짜 열을 인덱스로 두면 무엇이 달라질까요?
- 리샘플링은 단순 집계와 어떤 차이가 있을까요?
- 이동 평균 같은 창 기반 계산은 어떻게 할까요?

## 큰 그림

![Pandas 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/08/08-01-concept-at-a-glance.ko.png)

*Pandas 101 8장 흐름 개요*

이 그림은 시간순 데이터를 올바르게 정렬하고 해석하는 흐름을 보여줍니다. 날짜 인덱스, 빈도 설정, 시간대별 집계가 차근차근 이어져야 의미 있는 시계열 분석이 가능합니다.

> **시계열은 시간 순서가 의미**입니다. 정렬을 무시하거나 누락 주기를 처리하지 않으면 추세와 계절성 분석 자체가 무너집니다.

## 왜 중요한가

운영 지표의 대부분은 시간에 따라 변합니다. 시간 축을 제대로 다루면 주간 합계, 월간 평균, 이동 평균, 전일 대비 변화처럼 실무에서 자주 쓰는 질문을 짧고 안정적인 코드로 풀 수 있습니다.

## 한눈에 보는 개념

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

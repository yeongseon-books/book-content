---
series: pandas-101
episode: 6
title: "Pandas 101 (6/10): 그룹화와 집계"
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
  - GroupBy
  - Aggregation
  - DataAnalysis
  - Beginner
seo_description: groupby 분할-적용-결합 모델을 이해합니다. 집계, 변환, 필터의 차이와 실무에서 자주 쓰이는 특징 생성 패턴, 최적화 전략을 정리합니다.
last_reviewed: '2026-05-15'
---

# Pandas 101 (6/10): 그룹화와 집계

이 글은 판다스 101 시리즈의 6번째 글입니다.

분석이 표를 읽는 단계에서 끝나는 경우는 거의 없습니다. 결국은 도시별 매출, 사용자군별 전환율, 월별 지표처럼 어떤 기준으로 묶고 요약해야 의미가 생깁니다. 그래서 `groupby`는 Pandas의 옵션 하나가 아니라 분석 자체를 움직이는 핵심 축에 가깝습니다.


이번 글에서는 `groupby`를 SQL 문법의 대응물로만 보지 않고, 분할하고 적용한 뒤 다시 결합하는 분석 패턴으로 이해해 보겠습니다.

## 먼저 던지는 질문

- `groupby`는 어떤 흐름으로 동작할까요?
- 집계, 변환, 필터는 왜 서로 다른 얼굴일까요?
- 여러 통계를 한 번에 계산할 때는 어떻게 쓰는 편이 좋을까요?

## 큰 그림

![Pandas 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/06/06-01-concept-at-a-glance.ko.png)

*Pandas 101 6장 흐름 개요*

이 그림은 분할-적용-결합 패턴을 보여줍니다. 같은 데이터도 어떤 열을 기준으로 그룹 지으냐, 그룹 내에서 어떤 통계를 계산하냐에 따라 완전히 다른 의미를 갖습니다.

> **집계는 분할의 선택으로 시작**합니다. 같은 데이터프레임을 고객별, 날짜별, 지역별로 묶으면 전혀 다른 지표가 나옵니다.

## 왜 중요한가

집계는 분석의 중심입니다. `groupby`를 제대로 쓰면 반복문 수십 줄이 한 줄로 줄어들 뿐 아니라, 계산 의도도 함께 선명해집니다. 비즈니스 지표, 코호트 분석, 특징 생성이 모두 여기서 이어집니다.

## 한눈에 보는 개념

## 핵심 용어

- 그룹화: 특정 키를 기준으로 데이터를 여러 묶음으로 나누는 일입니다.
- 집계: 그룹마다 하나의 값을 남기는 계산입니다.
- 변환: 그룹 계산 결과를 원본 길이에 맞춰 되돌리는 방식입니다.
- 필터: 그룹 단위 조건으로 행을 남기거나 버리는 방식입니다.
- **인덱스화 여부**: 그룹 키를 결과 인덱스로 둘지 결정하는 설정입니다.
- 분할-적용-결합: 데이터를 그룹으로 나누고, 계산을 적용한 뒤, 다시 하나의 표로 합치는 패턴입니다.

## 전과 후

이전 관점: 카테고리별 합계를 반복문으로 직접 계산합니다.

이후 관점: 기준 열로 나눈 뒤 요약 규칙을 한 번에 선언합니다.

## 실습: 다섯 단계로 그룹화하기

### 1단계 - 데이터 준비하기

```python
import pandas as pd
df = pd.DataFrame({
    "city": ["Seoul", "Seoul", "Busan", "Busan"],
    "month": ["Jan", "Feb", "Jan", "Feb"],
    "sales": [100, 120, 80, 95],
})
```

작은 예제지만 `groupby`의 기본 감각을 잡기에는 충분합니다. 어떤 열을 기준으로 묶을지 먼저 정하는 것이 출발점입니다.

### 2단계 - 합계 구하기

```python
print(df.groupby("city")["sales"].sum())
```
단순 합계만 보더라도 split과 combine이 이미 동작한다는 사실을 확인할 수 있습니다. 더 복잡한 통계로 가기 전에, 묶은 결과가 머릿속 계산과 맞는지 먼저 점검하는 습관이 중요합니다.

**예상 출력:**

```text
city
Busan    175
Seoul    220
Name: sales, dtype: int64
```

가장 기본적인 그룹화입니다. 도시별로 묶은 뒤 매출 열의 합계를 계산합니다. 이 한 줄이 `groupby`의 가장 단순한 얼굴입니다.

### groupby 집계 함수 비교

다음 표는 자주 사용하는 집계 함수의 반환 형태와 용도를 정리한 것입니다.

| 함수 | 반환 형태 | 용도 |
|---|---|---|
| `mean()` | 그룹당 한 값 | 그룹 평균 계산 |
| `sum()` | 그룹당 한 값 | 그룹 합계 계산 |
| `count()` | 그룹당 한 값 | 그룹 행 수 계산 |
| `agg()` | 그룹당 한 행 | 여러 통계를 동시에 계산 |
| `transform()` | 원본 행 수 유지 | 그룹 통계를 원본 길이에 맞춰 복원 |
| `apply()` | 가변 | 그룹마다 임의 함수 적용 |

집계 함수는 그룹당 하나의 값을 만들지만, `transform`은 원본 행 수를 유지한 채 그룹 통계를 되돌려 준다는 점이 가장 큰 차이입니다. 특징 생성에는 `transform`이 훨씬 자주 쓰입니다.

### 3단계 - 여러 통계 한 번에 계산하기

```python
print(df.groupby("city").agg(
    total=("sales", "sum"),
    mean=("sales", "mean"),
    n=("sales", "count"),
))
```

이름 붙은 집계를 쓰면 출력 열 이름을 제어할 수 있어 결과 표가 훨씬 읽기 쉬워집니다. 실무에서는 이 패턴을 가장 많이 씁니다.

### 4단계 - 원본 모양을 유지한 채 계산 붙이기

```python
df["share"] = df["sales"] / df.groupby("city")["sales"].transform("sum")
print(df)
```

`transform`은 원본 행 수를 유지한 채 그룹 정보를 되돌려 준다는 점이 핵심입니다. 그래서 각 도시 안에서 자기 매출 비중이 얼마인지 같은 특징을 바로 붙일 수 있습니다.

**예상 출력:**

```text
    city month  sales     share
0  Seoul   Jan    100  0.454545
1  Seoul   Feb    120  0.545455
2  Busan   Jan     80  0.457143
3  Busan   Feb     95  0.542857
```

`transform`은 그룹별 계산 결과를 원본 행 수에 맞춰 되돌려 줍니다. 그래서 비율, 평균 대비 편차, 표준화 같은 특징 생성에 잘 맞습니다.

### 다중 컬럼 groupby와 agg

실무에서는 여러 키로 묶고 여러 열에 대해 각기 다른 통계를 계산해야 할 때가 많습니다.

```python
df = pd.DataFrame({
    "city": ["Seoul", "Seoul", "Busan", "Busan"],
    "category": ["A", "B", "A", "B"],
    "sales": [100, 120, 80, 95],
    "visits": [50, 60, 40, 45],
})

result = df.groupby(["city", "category"]).agg(
    total_sales=("sales", "sum"),
    avg_sales=("sales", "mean"),
    total_visits=("visits", "sum"),
)
print(result)
```

**예상 출력:**

```text
               total_sales  avg_sales  total_visits
city  category
Busan A                 80       80.0            40
      B                 95       95.0            45
Seoul A                100      100.0            50
      B                120      120.0            60
```

여러 컬럼으로 묶으면 결과 인덱스가 계층형 인덱스가 됩니다. `reset_index()`를 호출하면 인덱스를 열로 풀어 평평한 표로 바꿀 수 있습니다. 이 패턴은 복잡한 비즈니스 리포트에서 매우 자주 등장합니다.

```python
print(result.reset_index())
```

**예상 출력:**

```text
    city category  total_sales  avg_sales  total_visits
0  Busan        A           80       80.0            40
1  Busan        B           95       95.0            45
2  Seoul        A          100      100.0            50
3  Seoul        B          120      120.0            60
```

계층 인덱스를 그대로 두면 `.loc[]`으로 그룹을 선택하기 편하지만, 다른 표와 조인할 때는 평평한 형태가 더 안전합니다. 상황에 맞게 선택하세요.

### 5단계 - 그룹 조건으로 걸러내기

```python
big = df.groupby("city").filter(lambda g: g["sales"].sum() > 200)
print(big)
```

`filter`는 그룹 전체가 조건을 만족할 때 그 그룹의 행을 남깁니다. 개별 행 조건이 아니라 그룹 수준 조건이라는 점이 핵심입니다.

### groupby 성능 팁

그룹화는 분석의 핵심이지만, 데이터가 커지면 병목이 되기 쉬운 연산이기도 합니다. 다음 팁은 groupby 성능을 개선하는 데 도움이 됩니다.

#### 1. 카테고리 타입 활용

그룹 키 열의 고유값이 적다면 카테고리 타입으로 바꾸면 메모리와 속도가 개선됩니다.

```python
df["city"] = df["city"].astype("category")
print(df.groupby("city")["sales"].sum())
```

카테고리 타입은 내부적으로 정수 코드로 저장하므로 문자열 비교보다 빠릅니다. 특히 그룹 수가 적고 데이터가 클 때 효과가 큽니다.

#### 2. 불필요한 열 제거

집계하기 전에 필요한 열만 선택하면 불필요한 계산을 줄일 수 있습니다.

```python
# 느림: 모든 열을 그룹화
df.groupby("city").mean()

# 빠름: 필요한 열만 집계
df.groupby("city")["sales"].mean()
```

#### 3. apply 대신 내장 함수 우선

`apply`는 느립니다. 가능하면 내장 집계 함수나 `agg`를 먼저 검토하세요.

```python
# 느림
df.groupby("city").apply(lambda g: g["sales"].sum())

# 빠름
df.groupby("city")["sales"].sum()
```

#### 4. sort=False 옵션

결과 정렬이 필요 없다면 `sort=False`를 전달해 정렬 비용을 제거할 수 있습니다.

```python
df.groupby("city", sort=False)["sales"].sum()
```

이 네 가지 팁만 기억해도 groupby 속도를 눈에 띄게 개선할 수 있습니다. 특히 카테고리 타입과 열 선택은 코드 한 줄로 큰 차이를 만들 수 있는 실용적인 방법입니다.

### 실무 예제: 코호트 분석

그룹화는 코호트 분석처럼 실무 분석의 핵심입니다.

```python
import pandas as pd

# 사용자 가입 데이터
df = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "signup_month": ["2026-01", "2026-01", "2026-02", "2026-02", "2026-03"],
    "purchase_month": ["2026-02", "2026-03", "2026-02", "2026-04", "2026-03"],
    "amount": [100, 150, 80, 200, 120],
})

# 가입 월별 평균 구매액
cohort = df.groupby("signup_month").agg(
    users=("user_id", "count"),
    avg_amount=("amount", "mean"),
    total_amount=("amount", "sum"),
)
print(cohort)
```

**예상 출력:**

```text
              users  avg_amount  total_amount
signup_month                                  
2026-01           2       125.0           250
2026-02           2       140.0           280
2026-03           1       120.0           120
```

코호트 분석은 같은 시점에 가입한 사용자 그룹의 행동을 추적하는 방법입니다. 가입 월별로 묶어 평균 구매액을 비교하면 어느 시점 사용자가 더 가치 있는지 파악할 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- `agg`는 그룹당 한 행을 만들고 `transform`은 원본 모양을 유지합니다.
- 이름 붙은 집계는 결과 열 이름을 읽기 좋게 만듭니다.
- `filter`는 참과 거짓을 반환하는 함수가 아니라 행을 남기는 도구입니다.

## 자주 하는 실수 다섯 가지

1. `agg`와 `transform`의 결과 모양 차이를 혼동합니다.
2. `as_index=False`를 의식하지 않아 예상 밖 인덱스를 만납니다.
3. `reset_index()`를 빼먹어 다음 조인이 불편해집니다.
4. 여러 키 그룹화에서 대괄호 문법을 놓칩니다.
5. `apply`를 남용해 속도와 가독성을 함께 잃습니다.

## 실무에서는 이렇게 이어집니다

세그먼트 분석, 유지율 계산, 월별 지표 집계처럼 `groupby`는 사실상 비즈니스 인텔리전스의 기본 엔진입니다. 특히 `transform`은 그룹 평균 대비 점수나 그룹 내 비중 같은 특징을 만들 때 자주 쓰입니다.

## 실무에서는 이렇게 생각합니다

- 먼저 `agg`를 생각하고 `apply`는 마지막에 검토합니다.
- 출력 열 이름은 이름 붙은 집계로 명확하게 만듭니다.
- 특징 생성에는 `transform`을 적극적으로 씁니다.
- 여러 키 그룹화는 복합 키 인덱스처럼 다룹니다.
- 그룹 키를 인덱스로 둘지 열로 둘지 의도적으로 결정합니다.

## 체크리스트

- [ ] 분할, 적용, 결합 모델을 설명할 수 있습니다.
- [ ] 집계, 변환, 필터의 차이를 이해하고 있습니다.
- [ ] 이름 붙은 집계를 사용할 수 있습니다.
- [ ] 여러 키 기준 그룹화를 할 수 있습니다.

## 연습 문제

1. 카테고리별 평균과 표준편차를 이름 붙은 집계로 출력해 보세요.
2. 그룹 평균을 원본 데이터프레임에 다시 붙여 보세요.
3. 합계가 특정 기준을 넘는 그룹만 `filter`로 남겨 보세요.

## 정리와 다음 글

`groupby`는 분석 결과를 만드는 핵심 동력입니다. 데이터를 묶고, 계산하고, 다시 표로 되돌리는 감각을 익혀 두면 이후의 지표 계산이 훨씬 빨라집니다. 다음 글에서는 여러 표를 하나로 합치는 병합과 조인을 다루겠습니다.

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

- **`groupby`는 어떤 흐름으로 동작할까요?**
  - 본문의 기준은 그룹화와 집계를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **집계, 변환, 필터는 왜 서로 다른 얼굴일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **여러 통계를 한 번에 계산할 때는 어떻게 쓰는 편이 좋을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): 결측치 처리](./05-missing-values.md)
- **그룹화와 집계 (현재 글)**
- 병합과 조인 (예정)
- 시계열 데이터 다루기 (예정)
- 적용 함수와 벡터화 (예정)
- 실전 데이터 분석 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — Group by: split-apply-combine](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [pandas — agg](https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.agg.html)
- [pandas — transform](https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.transform.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, GroupBy, Aggregation, DataAnalysis, Beginner

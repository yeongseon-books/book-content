---
series: pandas-101
episode: 7
title: "Pandas 101 (7/10): 병합과 조인"
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
  - Merge
  - Join
  - SQL
  - Beginner
seo_description: 데이터 병합과 조인 전략을 익힙니다. Inner, Left 조인의 차이와 키 관계 검증, 행 수 폭증 방지 등 안전한 결합 패턴을 정리합니다.
last_reviewed: '2026-05-15'
---

# Pandas 101 (7/10): 병합과 조인

이 글은 판다스 101 시리즈의 7번째 글입니다.

실무 데이터는 거의 항상 여러 표로 나뉘어 있습니다. 사용자 정보는 한 표에, 주문 기록은 다른 표에, 광고 지표는 또 다른 표에 있습니다. 그래서 두 표를 어떻게 합치느냐는 데이터 분석의 보조 기술이 아니라 핵심 능력에 가깝습니다.


이번 글에서는 `merge`와 `join`을 단순히 SQL 용어의 번역으로 보지 않고, 키가 어디에 놓여 있는지에 따라 표를 안전하게 결합하는 도구로 정리해 보겠습니다.

## 먼저 던지는 질문

- 왜 Pandas에는 `merge`와 `join`이 둘 다 있을까요?
- 안쪽, 왼쪽, 오른쪽, 바깥쪽, 교차 조인은 어떻게 다를까요?
- 중복 키가 있을 때 왜 행 수가 갑자기 늘어날까요?

## 큰 그림

![Pandas 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/07/07-01-concept-at-a-glance.ko.png)

*Pandas 101 7장 흐름 개요*

이 그림은 두 표를 관계로 연결하는 감각을 보여줍니다. 하나만 가지고는 답을 만들기 어려운 질문이 병합을 거치면서 비로소 의미를 갖게 됩니다.

> **`merge`는 관계를 검증하는 도구**입니다. 두 표를 합쳤을 때 행이 늘어나는지, 중복 키가 있는지, 자료형이 일치하는지를 항상 확인해야 합니다.

## 왜 중요한가

실무 분석의 상당수는 결국 표와 표를 연결하는 작업입니다. 사용자와 주문, 광고와 전환, 상품과 재고를 안전하게 합칠 수 있어야 지표도 맞고 모델 입력도 안정적입니다.

## 한눈에 보는 개념

## 핵심 용어

- **안쪽 조인**: 양쪽 모두에 있는 키만 남깁니다.
- **왼쪽 조인**: 왼쪽 표의 모든 행을 유지합니다.
- **오른쪽 조인**: 오른쪽 표를 기준으로 유지합니다.
- **바깥쪽 조인**: 양쪽 키의 합집합을 남깁니다.
- **교차 조인**: 가능한 모든 조합을 만듭니다.
- **키**: 두 표를 연결하는 기준 열입니다.

### 조인 방식 비교

다음 표는 다섯 가지 조인 방식의 차이와 사용 조건을 정리한 것입니다.

| 조인 방식 | how 파라미터 | 왼쪽 키 | 오른쪽 키 | 결과 행 | 주요 용도 |
|---|---|---|---|---|---|
| 안쪽 조인 | `inner` | 매칭된 행만 | 매칭된 행만 | 교집합 | 양쪽에 모두 존재하는 데이터만 분석 |
| 왼쪽 조인 | `left` | 전체 유지 | 매칭된 행만 | 왼쪽 기준 | 기준 표를 보존하며 정보 추가 |
| 오른쪽 조인 | `right` | 매칭된 행만 | 전체 유지 | 오른쪽 기준 | 왼쪽 조인의 역방향 |
| 바깥쪽 조인 | `outer` | 전체 유지 | 전체 유지 | 합집합 | 양쪽 키 모두 보존 |
| 교차 조인 | `cross` | 모든 행 | 모든 행 | 곱집합 | 모든 조합 생성 |

안쪽 조인은 기본값이므로 `how`를 생략하면 자동으로 적용됩니다. 왼쪽 조인은 실무에서 가장 많이 쓰이는 패턴으로, 기준 표의 모든 행을 유지한 채 다른 표의 정보를 추가할 때 사용합니다.

## 전과 후

이전 관점: 병합 한 번에 행 수가 갑자기 폭증하고도 원인을 모릅니다.

이후 관점: 키 관계를 먼저 검증하고 `validate`로 가정을 코드에 남깁니다.

## 실습: 다섯 단계로 표 합치기

### 1단계 - 데이터 준비하기

```python
import pandas as pd
users = pd.DataFrame({"uid": [1, 2, 3], "name": ["a", "b", "c"]})
orders = pd.DataFrame({"uid": [1, 1, 2], "amount": [100, 200, 50]})
```

작은 예제지만 이미 중요한 함정이 숨어 있습니다. `orders`에는 같은 `uid`가 두 번 나오므로, 키 관계를 의식하지 않으면 결과 행 수가 달라질 수 있습니다.

### 2단계 - 안쪽 조인하기

```python
print(users.merge(orders, on="uid"))
```

기본 `how`는 안쪽 조인입니다. 양쪽에 모두 있는 키만 남기므로 결과를 보면 사용자 3번은 빠집니다.

### 3단계 - 왼쪽 조인과 바깥쪽 조인하기

```python
print(users.merge(orders, on="uid", how="left"))
print(users.merge(orders, on="uid", how="outer", indicator=True))
```

조인 결과를 눈으로 확인할 때는 값보다 `_merge` 열이 더 중요할 때가 많습니다. 어느 키가 양쪽에 있었고, 어느 키가 한쪽에만 있었는지를 즉시 알려 주기 때문입니다.

**예상 출력:**

```text
   uid name  amount     _merge
0    1    a   100.0       both
1    1    a   200.0       both
2    2    b    50.0       both
3    3    c     NaN  left_only
```

왼쪽 조인은 기준 표를 보존하고, 바깥쪽 조인은 양쪽 키를 모두 살립니다. `indicator=True`를 켜면 각 행이 어느 쪽에서 왔는지 추적할 수 있습니다.

### 4단계 - 같은 이름의 열 충돌 피하기

```python
df1 = pd.DataFrame({"k": [1], "v": [10]})
df2 = pd.DataFrame({"k": [1], "v": [20]})
print(df1.merge(df2, on="k", suffixes=("_a", "_b")))
```

같은 이름의 열이 있을 때 접미사를 지정하지 않으면 결과 열이 읽기 어려워집니다. 접미사는 충돌 해결이자 문서화 장치입니다.

### 5단계 - 키 관계를 검증하기

```python
try:
    users.merge(orders, on="uid", validate="one_to_one")
except Exception as e:
    print("expected:", type(e).__name__)
```

`validate`는 잘못된 조인을 조용히 통과시키지 않게 만드는 안전장치입니다. 기대한 관계와 다르면 바로 예외가 나와서 행 수 폭증을 조기에 막아 줍니다.

**예상 출력:**

```text
expected: MergeError
```

`validate`는 조인 가정을 코드에 선언하는 매우 좋은 방법입니다. 기대한 관계와 실제 데이터 관계가 다르면 즉시 오류를 내서 조용한 데이터 오염을 막아 줍니다.

### 결측치 처리 전략

조인을 하면 왼쪽이나 오른쪽 표에만 있는 키 때문에 결측치가 생길 수 있습니다. 이 결측치를 어떻게 다룰지는 분석 목적에 따라 달라집니다.

| 전략 | 조건 | 장점 | 단점 |
|---|---|---|---|
| 삭제 | 결측이 소수 | 간단하고 명확 | 정보 손실 |
| 대체 | 합리적 기본값 존재 | 행 수 유지 | 왜곡 가능성 |
| 보간 | 시간/순서 데이터 | 추세 반영 | 추가 가정 필요 |
| 플래그 추가 | 결측 여부가 중요 | 정보 유지 | 열 증가 |

```python
users = pd.DataFrame({"uid": [1, 2, 3], "name": ["a", "b", "c"]})
orders = pd.DataFrame({"uid": [1, 1, 2], "amount": [100, 200, 50]})

merged = users.merge(orders, on="uid", how="left")

# 전략 1: 결측 삭제
print(merged.dropna())

# 전략 2: 기본값 대체
merged["amount"] = merged["amount"].fillna(0)
print(merged)

# 전략 4: 결측 플래그
merged["has_order"] = merged["amount"].notna()
print(merged)
```

**예상 출력 (플래그 추가):**

```text
   uid name  amount  has_order
0    1    a   100.0       True
1    1    a   200.0       True
2    2    b    50.0       True
3    3    c     0.0      False
```

결측치를 그냥 두면 이후 계산에서 예상치 못한 오류가 생길 수 있습니다. 조인 직후 결측 패턴을 확인하고 명시적으로 처리하는 습관이 중요합니다.

## 이 코드에서 먼저 봐야 할 점

- `indicator=True`는 각 행의 출처를 보여 줍니다.
- `suffixes`는 같은 이름의 열 충돌을 정리합니다.
- `validate`는 조인 가정을 코드에 남기는 장치입니다.

### fillna와 interpolate 예제

조인 후 결측치를 보간하는 패턴은 시계열 데이터나 순서가 있는 데이터에서 자주 등장합니다.

```python
import pandas as pd
import numpy as np

# 시간순 데이터
df = pd.DataFrame({
    "date": pd.date_range("2026-01-01", periods=5),
    "value": [10, np.nan, np.nan, 40, 50],
})

# 선형 보간
df["interpolated"] = df["value"].interpolate(method="linear")

# 앞 값으로 채우기
df["ffill"] = df["value"].fillna(method="ffill")

# 뒤 값으로 채우기
df["bfill"] = df["value"].fillna(method="bfill")

print(df)
```

**예상 출력:**

```text
        date  value  interpolated  ffill  bfill
0 2026-01-01   10.0          10.0   10.0   10.0
1 2026-01-02    NaN          20.0   10.0   40.0
2 2026-01-03    NaN          30.0   10.0   40.0
3 2026-01-04   40.0          40.0   40.0   40.0
4 2026-01-05   50.0          50.0   50.0   50.0
```

보간은 결측 구간의 값을 추정해서 채우는 방식입니다. 시계열 분석에서는 선형 보간이 자주 쓰이지만, 보간이 항상 정답은 아니므로 데이터 특성에 맞게 선택해야 합니다.

### 결측 패턴 시각화

조인 후 결측치가 어디에 얼마나 있는지 시각적으로 확인하면 패턴을 빠르게 파악할 수 있습니다.

```python
import pandas as pd
import numpy as np

users = pd.DataFrame({"uid": [1, 2, 3, 4, 5], "name": ["a", "b", "c", "d", "e"]})
orders = pd.DataFrame({"uid": [1, 1, 2], "amount": [100, 200, 50]})

merged = users.merge(orders, on="uid", how="left")

# 결측 여부를 0/1로 변환
missing_map = merged.isnull().astype(int)
print(missing_map)

# 열별 결측 비율
print(merged.isnull().mean())
```

**예상 출력:**

```text
   uid  name  amount
0    0     0       0
1    0     0       0
2    0     0       0
3    0     0       1
4    0     0       1

uid       0.0
name      0.0
amount    0.4
dtype: float64
```

결측 비율을 먼저 보면 조인이 제대로 됐는지 감을 잡을 수 있습니다. 예상보다 결측이 많다면 키 관계나 조인 방식을 다시 점검해야 합니다.

### 실무 예제: 고객-주문 병합

실무에서 가장 자주 마주치는 패턴은 고객 테이블과 주문 테이블을 합치는 것입니다.

```python
import pandas as pd

customers = pd.DataFrame({
    "customer_id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "tier": ["Gold", "Silver", "Gold"],
})

orders = pd.DataFrame({
    "order_id": [101, 102, 103, 104],
    "customer_id": [1, 1, 2, 3],
    "amount": [100, 150, 80, 200],
})

# 주문 총액 계산
order_sum = orders.groupby("customer_id").agg(
    total_amount=("amount", "sum"),
    order_count=("order_id", "count"),
)

# 고객 정보와 병합
result = customers.merge(order_sum, on="customer_id", how="left")
result["total_amount"] = result["total_amount"].fillna(0)
result["order_count"] = result["order_count"].fillna(0)
print(result)
```

**예상 출력:**

```text
   customer_id     name    tier  total_amount  order_count
0            1    Alice    Gold         250.0          2.0
1            2      Bob  Silver          80.0          1.0
2            3  Charlie    Gold         200.0          1.0
```

이 패턴은 고객별 KPI를 만들 때 기본이 됩니다. 주문 테이블을 먼저 그룹화해 집계한 다음, 고객 테이블과 병합하면 고객 수준의 통계를 얻을 수 있습니다.

## 자주 하는 실수 다섯 가지

1. 중복 키 때문에 행 수가 폭증하는데도 그대로 넘어갑니다.
2. 기본 조인 방식이 안쪽 조인이라는 사실을 놓칩니다.
3. 접미사를 지정하지 않아 결과 열 해석이 어려워집니다.
4. 왼쪽과 오른쪽 키의 자료형이 다른 채로 병합합니다.
5. 인덱스 정리를 하지 않아 다음 단계에서 충돌을 만듭니다.

## 실무에서는 이렇게 이어집니다

고객 데이터와 주문 데이터, 광고 데이터와 전환 데이터처럼 실무 분석은 대부분 조인 위에 세워집니다. 그래서 행 수 추적, 키 중복 확인, 자료형 일치 여부는 병합 전후의 기본 점검 항목이 됩니다.

## 실무에서는 이렇게 생각합니다

- 병합 전후 행 수를 항상 비교합니다.
- `validate`로 키 관계 가정을 명시합니다.
- 조인 키의 자료형을 먼저 맞춥니다.
- 병합 전에 중복을 정리할지 의도적으로 결정합니다.
- 결과 표를 한 번 더 점검해 예상과 맞는지 확인합니다.

## 체크리스트

- [ ] 다섯 가지 조인 방식의 차이를 설명할 수 있습니다.
- [ ] `validate`를 이용해 조인 가정을 검증할 수 있습니다.
- [ ] `indicator`로 행 출처를 확인할 수 있습니다.
- [ ] `suffixes`로 열 이름 충돌을 정리할 수 있습니다.

## 연습 문제

1. 왼쪽 조인과 바깥쪽 조인의 행 수 차이를 비교해 보세요.
2. `validate="one_to_one"`가 실패하는 예제를 만들어 오류를 확인해 보세요.
3. `indicator` 열을 이용해 오른쪽 표에만 있는 행을 찾아보세요.

## 정리와 다음 글

병합은 데이터를 이어 붙이는 기술이 아니라 데이터 관계를 검증하는 기술입니다. 키와 행 수를 함께 보아야 조인이 안전해집니다. 다음 글에서는 시간 축이 붙은 데이터를 다루는 시계열 작업을 다루겠습니다.

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

- **왜 Pandas에는 `merge`와 `join`이 둘 다 있을까요?**
  - 본문의 기준은 병합과 조인를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **안쪽, 왼쪽, 오른쪽, 바깥쪽, 교차 조인은 어떻게 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **중복 키가 있을 때 왜 행 수가 갑자기 늘어날까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): 결측치 처리](./05-missing-values.md)
- [Pandas 101 (6/10): 그룹화와 집계](./06-groupby.md)
- **병합과 조인 (현재 글)**
- 시계열 데이터 다루기 (예정)
- 적용 함수와 벡터화 (예정)
- 실전 데이터 분석 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — Merge, join, concatenate and compare](https://pandas.pydata.org/docs/user_guide/merging.html)
- [pandas — merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)
- [pandas — join](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.join.html)
- [SQL Joins Explained — Mode Analytics](https://mode.com/sql-tutorial/sql-joins/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, Merge, Join, SQL, Beginner

---
series: pandas-101
episode: 2
title: "Pandas 101 (2/10): 시리즈와 데이터프레임"
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
  - Series
  - DataFrame
  - Python
  - Beginner
seo_description: 시리즈와 데이터프레임의 관계를 이해합니다. 인덱스 정렬 원리, 열 중심 사고방식, 레이블 연산 등 Pandas 데이터 모델링 기초를 정리합니다.
last_reviewed: '2026-05-15'
---

# Pandas 101 (2/10): 시리즈와 데이터프레임

이 글은 판다스 101 시리즈의 2번째 글입니다.

Pandas를 쓰기 시작하면 금방 이런 질문이 나옵니다. 시리즈와 데이터프레임은 이름만 다른 두 자료구조일까요, 아니면 하나의 모델을 다른 크기로 보여 주는 걸까요. 이 관계를 초반에 분명히 잡아 두지 않으면 열 선택, 정렬, 산술 연산, 조인에서 계속 감으로만 코드를 쓰게 됩니다.


이번 글의 핵심은 간단합니다. 데이터프레임은 서로 같은 레이블 체계를 공유하는 시리즈의 묶음입니다. 이 관점을 잡으면 Pandas의 많은 동작이 훨씬 자연스럽게 읽힙니다.

## 먼저 던지는 질문

- 시리즈는 내부적으로 어떤 구조일까요?
- 데이터프레임을 열 중심으로 본다는 말은 무엇을 뜻할까요?
- 인덱스는 왜 단순한 행 번호가 아닐까요?

## 큰 그림

![Pandas 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/02/02-01-concept-at-a-glance.ko.png)

*Pandas 101 2장 흐름 개요*

이 그림은 시리즈와 데이터프레임이 어떻게 인덱스를 공유하는지 보여 줍니다. 시리즈는 값 배열에 레이블을 붙인 것이고, 데이터프레임은 같은 인덱스 위에 여러 시리즈를 놓은 구조입니다.

> 데이터프레임은 시리즈의 **묶음**입니다. 이 관점을 갖추면 정렬, 결합, 열 연산이 모두 같은 원리로 작동하는 이유가 명확해집니다.

## 왜 중요한가

Pandas의 대부분 연산은 결국 시리즈 수준의 계산으로 환원됩니다. 데이터프레임의 한 열이 시리즈라는 사실을 이해하면 열 선택이 왜 특정 타입을 반환하는지, 왜 인덱스 정렬이 자동으로 일어나는지, 왜 레이블이 숫자 배열만큼 중요한지가 한 번에 연결됩니다.

## 한눈에 보는 개념

## 핵심 용어

- 시리즈: 값과 인덱스를 함께 가진 1차원 구조입니다.
- **데이터프레임**: 공통 인덱스를 공유하는 시리즈들의 묶음입니다.
- **값 배열**: 내부 계산에 쓰이는 기저 배열입니다.
- 인덱스: 행 레이블입니다.
- **열 레이블**: 각 시리즈를 구분하는 이름입니다.

## 전과 후

이전 관점: 데이터프레임을 그저 행과 열이 있는 표로만 봅니다.

이후 관점: 데이터프레임을 여러 시리즈가 같은 인덱스 위에 놓인 구조로 이해합니다.

## 실습: 구조를 직접 만들어 보기

### 1단계 - 시리즈 만들고 속성 보기

```python
import pandas as pd
s = pd.Series([1.0, 2.0, 3.0], index=["a", "b", "c"], name="x")
print(s.values, s.index, s.name)
```

시리즈는 값만 담는 배열이 아니라 레이블과 이름까지 갖춘 구조입니다. 이후 정렬과 연산은 이 레이블을 기준으로 움직입니다.

### 2단계 - 시리즈끼리 계산하기

```python
print(s * 10)
print(s + s)
```

시리즈 산술은 단순 반복문이 아니라 인덱스가 붙은 배열 연산입니다. 이 차이가 나중에 정렬 기반 계산의 핵심이 됩니다.

## 시리즈와 데이터프레임 비교

이 두 구조의 관계는 표로 정리하면 명확해집니다.

| 항목 | Series | DataFrame |
| --- | --- | --- |
| 차원 | 1차원 | 2차원 |
| 인덱스 | 행 레이블 | 행 레이블 (공유) |
| 생성 방법 | `pd.Series(list, index=...)` | `pd.DataFrame(dict)` |

DataFrame은 같은 인덱스를 공유하는 Series의 묶음으로 볼 수 있습니다. 그래서 `df['column']`은 Series를 반환하고, `df[['column']]`은 1열 DataFrame을 반환합니다. 이 차이를 인지하는 것이 중요합니다.

### 3단계 - 데이터프레임 만들기

```python
df = pd.DataFrame({
    "x": [1, 2, 3],
    "y": [10, 20, 30],
}, index=["a", "b", "c"])
print(df)
```

데이터프레임을 시리즈 묶음으로 본다는 말은 출력 형태에서도 바로 드러납니다. 같은 인덱스를 공유하는 두 열이 한 표 안에 나란히 놓여 있는지 확인해 보세요.

**예상 출력:**

```text
   x   y
a  1  10
b  2  20
c  3  30
```

이 데이터프레임은 같은 인덱스를 공유하는 두 개의 시리즈를 옆으로 붙여 둔 것처럼 볼 수 있습니다. 그래서 열 단위 연산이 자연스럽습니다.

### 4단계 - 열 하나를 고르면 시리즈가 나옵니다

```python
col = df["x"]
print(type(col), col)
```

`df["x"]`가 데이터프레임이 아니라 시리즈라는 사실은 매우 중요합니다. 열 선택 뒤에 이어지는 메서드와 연산이 모두 시리즈 문법으로 연결되기 때문입니다.

### 5단계 - 인덱스가 자동으로 맞춰집니다

```python
s1 = pd.Series([1, 2, 3], index=["a", "b", "c"])
s2 = pd.Series([10, 20, 30], index=["b", "c", "d"])
print(s1 + s2)
```

여기서 핵심은 값이 아니라 인덱스 정렬입니다. 겹치지 않는 레이블에는 `NaN`이 생기고, 공통 레이블에서만 실제 덧셈이 일어납니다.

**예상 출력:**

```text
a     NaN
b    12.0
c    23.0
d     NaN
dtype: float64
```

Pandas는 단순히 같은 위치의 값을 더하지 않습니다. 먼저 인덱스를 맞춘 뒤 계산하고, 맞지 않는 위치는 `NaN`으로 남깁니다.

## 다양한 DataFrame 생성법

DataFrame을 만드는 방법은 여러 가지입니다. 각 방법은 데이터의 원본 형태에 따라 선택하면 됩니다.

### 딕셔너리로 만들기

```python
df = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "age": [25, 30],
})
print(df)
```

가장 직관적인 방법입니다. 딕셔너리의 키가 열 이름이 되고, 값 리스트가 각 열의 내용이 됩니다.

### 리스트 of 딕셔너리로 만들기

```python
data = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30},
]
df = pd.DataFrame(data)
print(df)
```

JSON API 응답이나 로그 파싱 결과처럼 행별로 데이터가 오는 경우에 자주 씁니다.

### NumPy 배열로 만들기

```python
import numpy as np
arr = np.array([[1, 2], [3, 4], [5, 6]])
df = pd.DataFrame(arr, columns=["x", "y"])
print(df)
```

내부적으로 Pandas는 NumPy 배열을 기반으로 동작하므로 이 방법도 매우 자연스럽습니다.
## 이 코드에서 먼저 봐야 할 점

- `df["x"]`는 시리즈를 반환합니다.
- 시리즈 산술에서는 인덱스 정렬이 자동으로 일어납니다.
- `NaN`은 정렬이 맞지 않았다는 중요한 단서가 될 수 있습니다.

## 자주 하는 실수 다섯 가지

1. `df["x"]`를 데이터프레임으로 착각합니다.
2. 인덱스가 어긋나 생긴 `NaN`을 단순 결측치로만 봅니다.
3. 항상 `values`로 넘겨 레이블 정보를 잃어버립니다.
4. `name` 속성을 무시해 시리즈 식별이 어려워집니다.
5. 두 데이터프레임의 행 순서가 같다고 가정한 채 더합니다.

## 실무에서는 이렇게 이어집니다

A/B 테스트 비교, 시계열 정렬, 여러 소스의 데이터 결합에서 Pandas가 강한 이유는 바로 인덱스 정렬입니다. 눈에 잘 보이지 않지만, 이 동작이 많은 계산의 정확도를 지탱합니다.

## 실무에서는 이렇게 생각합니다

- 먼저 인덱스가 무엇을 의미하는지 분명히 합니다.
- 열 선택은 곧 시리즈 사고방식으로 넘어가는 순간이라고 봅니다.
- 정렬 불일치에서 생긴 `NaN`을 디버깅 단서로 활용합니다.
- `df.values` 의존도를 낮춥니다.
- 시리즈 이름을 적극적으로 붙여 흐름을 읽기 쉽게 만듭니다.

## 실전 예제: 시계열 데이터

시리즈와 데이터프레임의 관계를 시계열 데이터로 확인해 보겠습니다.

```python
dates = pd.date_range("2024-01-01", periods=5, freq="D")
temp = pd.Series([15, 16, 14, 17, 16], index=dates, name="temperature")
humidity = pd.Series([60, 65, 55, 70, 68], index=dates, name="humidity")
weather = pd.DataFrame({"temp": temp, "humidity": humidity})
print(weather)
print("\n평균 기온:", weather["temp"].mean())
```

시계열에서는 인덱스가 날짜가 되고, 각 열은 시간에 따른 관측값을 나타냅니다. 이 구조를 이해하면 시계열 분석이 훨씬 수월해집니다.

## 성능 고려사항

Series와 DataFrame의 내부 구조를 이해하면 성능 최적화에도 도움이 됩니다.

### 벡터화를 우선하세요

```python
# Slow - 반복문
result = []
for val in df["x"]:
    result.append(val * 2)

# Fast - 벡터화
result = df["x"] * 2
```

반복문 대신 열 단위 연산을 사용하면 NumPy의 최적화된 C 코드를 활용할 수 있습니다.

### 메모리 효율적인 타입 선택

```python
# 기본 int64는 8바이트
df["count"] = df["count"].astype("int32")  # 4바이트로 절반
df["category"] = df["category"].astype("category")  # 범주형 데이터
print(df.memory_usage(deep=True))
```

대용량 데이터를 다룰 때는 타입 선택이 메모리 사용량에 크게 영향을 줍니다.

### copy vs view

```python
# view - 원본 데이터 공유
subset = df[["x", "y"]]

# copy - 독립적인 복사본
subset = df[["x", "y"]].copy()
```

할당을 할 때는 복사본을 명시적으로 만들어 SettingWithCopyWarning을 피하세요.
## 자료형 확인과 변환

데이터프레임의 각 열은 자료형을 가집니다. 이 자료형을 명시적으로 확인하고 변환하는 것이 후속 연산의 정확성을 보장합니다.

### 자료형 확인

```python
df = pd.DataFrame({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "score": [85.5, 90.0, 78.5],
})
print(df.dtypes)
```

**예상 출력:**

```text
id         int64
name      object
score    float64
dtype: object
```

Pandas는 자동으로 자료형을 추론하지만, 항상 정확한 것은 아닙니다. 그래서 명시적 변환이 필요할 때가 많습니다.

### 자료형 변환

```python
df["id"] = df["id"].astype("string")
df["score"] = df["score"].astype("int32")
print(df.dtypes)
```

`astype()`을 사용하면 모5시적으로 타입을 바꿀 수 있습니다. 실수를 정수로, 숫자를 문자열로 바꾸는 작업이 자주 등장합니다.

### 메모리 효율을 위한 타입 선택

Pandas 1.0 이후로 `int8`, `int16`, `int32` 같은 작은 정수형과 `string` 타입을 적극 활용하면 메모리를 크게 줄일 수 있습니다. 특히 대용량 데이터를 다룰 때 타입 선택은 성능에 직접 영향을 줍니다.

## 체크리스트

- [ ] 시리즈와 데이터프레임을 구분할 수 있습니다.
- [ ] 인덱스와 열 레이블의 역할을 설명할 수 있습니다.
- [ ] `df["col"]`이 시리즈임을 알고 있습니다.
- [ ] 인덱스 정렬이 자동이라는 점을 이해하고 있습니다.



## 인덱스 연산

인덱스가 있는 시리즈끼리 연산할 때는 인덱스 정렬이 자동으로 일어납니다. 이 동작을 이해하면 데이터 병합과 조인의 원리를 더 쉽게 파악할 수 있습니다.

```python
s1 = pd.Series([1, 2, 3], index=["a", "b", "c"])
s2 = pd.Series([10, 20], index=["b", "c"])
print(s1 + s2)
```

인덱스가 맞지 않는 위치에는 NaN이 생깁니다. 이 동작이 Pandas의 강력한 기능이자 조심해야 할 부분입니다.




### 주의사항

인덱스 불일치로 생긴 NaN은 의도한 것인지 확인이 필요합니다. 필요하다면 `fill_value` 파라미터로 기본값을 지정할 수 있습니다.

```python
result = s1.add(s2, fill_value=0)
print(result)
```

이렇게 하면 인덱스가 없는 위치에 0이 채워집니다.



## 데이터프레임 메서드 체이닝

Pandas는 메서드 체이닝을 지원하여 여러 연산을 연결할 수 있습니다.

```python
result = (df
    .assign(total=lambda x: x["price"] * x["qty"])
    .query("total > 100")
    .sort_values("total", ascending=False)
    .head(10)
)
print(result)
```

이 패턴은 코드를 읽기 쉽게 만들어 줍니다.



메서드 체이닝은 Pandas의 강력한 기능이지만, 너무 길어지면 디버깅이 어려워질 수 있습니다. 적절한 길이로 나누는 것이 좋습니다.


## 시리즈 내부 구조

Series는 내부적으로 NumPy 배열과 인덱스를 별도로 관리합니다. 이 구조를 이해하면 성능 최적화와 메모리 관리에 도움이 됩니다.

```python
s = pd.Series([1, 2, 3], index=["a", "b", "c"])
print("Data type:", s.dtype)
print("Array:", s.values)
print("Index:", s.index)
print("Memory:", s.memory_usage(deep=True), "bytes")
```

Series는 동일한 자료형만 담을 수 있습니다. 여러 자료형이 섞이면 `object` 타입으로 변환되어 성능이 떨어집니다. 따라서 생성 시 자료형을 명시적으로 설정하는 편이 좋습니다.

## 연습 문제

1. 시리즈 세 개를 만든 뒤 하나의 데이터프레임으로 합쳐 공통 인덱스를 확인해 보세요.
2. 서로 다른 인덱스를 가진 두 시리즈를 더해 `NaN` 위치를 살펴보세요.
3. `df["x"]`와 `df[["x"]]`의 타입 차이를 코드로 확인해 보세요.

## 정리와 다음 글

데이터프레임은 시리즈를 공통 인덱스 위에 모아 둔 구조입니다. 이 기본 모델을 이해하면 이후의 선택, 집계, 병합도 모두 한층 단단하게 읽힙니다. 다음 글에서는 CSV와 Excel 파일을 정확하게 읽는 방법을 다루겠습니다.

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

- **시리즈는 내부적으로 어떤 구조일까요?**
  - 본문의 기준은 시리즈와 데이터프레임를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **데이터프레임을 열 중심으로 본다는 말은 무엇을 뜻할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **인덱스는 왜 단순한 행 번호가 아닐까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- **시리즈와 데이터프레임 (현재 글)**
- CSV와 Excel 읽기 (예정)
- 필터링과 선택 (예정)
- 결측치 처리 (예정)
- 그룹화와 집계 (예정)
- 병합과 조인 (예정)
- 시계열 데이터 다루기 (예정)
- 적용 함수와 벡터화 (예정)
- 실전 데이터 분석 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — Series API](https://pandas.pydata.org/docs/reference/series.html)
- [pandas — DataFrame API](https://pandas.pydata.org/docs/reference/frame.html)
- [pandas — Intro to data structures](https://pandas.pydata.org/docs/user_guide/dsintro.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, Series, DataFrame, Python, Beginner

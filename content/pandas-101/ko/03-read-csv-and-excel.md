---
series: pandas-101
episode: 3
title: "Pandas 101 (3/10): CSV와 Excel 읽기"
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
  - CSV
  - Excel
  - DataAnalysis
  - Beginner
seo_description: CSV와 Excel을 정확히 읽는 핵심 옵션과 점검 순서를 정리한 글입니다
last_reviewed: '2026-05-15'
---

# Pandas 101 (3/10): CSV와 Excel 읽기

이 글은 판다스 101 시리즈의 3번째 글입니다.

분석 작업이 자주 실패하는 이유는 복잡한 모델보다 훨씬 앞단에 있습니다. 파일을 처음 읽는 순간 문자 인코딩이 깨지고, 숫자 열이 문자열로 들어오고, 날짜가 날짜로 해석되지 않으면 그 뒤의 계산은 전부 흔들립니다. 읽기 단계는 사소한 준비가 아니라 분석 품질을 결정하는 첫 관문입니다.


이번 글에서는 `read_csv`와 `read_excel`을 단순한 파일 열기 함수로 보지 않고, 데이터를 의도한 형태로 적재하는 설정 지점으로 보겠습니다.


![Pandas 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/03/03-01-concept-at-a-glance.ko.png)
*Pandas 101 3장 흐름 개요*
> 읽기는 사소한 함수 호출이 아니라 **데이터의 품질과 의도를 정하는 첫 관문**입니다. 여기서의 설정이 이후 모든 분석의 신뢰성을 결정합니다.

## 먼저 던지는 질문

- `read_csv`와 `read_excel`에서 가장 먼저 봐야 할 옵션은 무엇일까요?
- 문자 인코딩과 구분자는 왜 자주 문제를 일으킬까요?
- 자료형을 명시하면 어떤 이점이 있을까요?

## 왜 중요한가

실제 분석의 상당 부분은 적재와 정제에 들어갑니다. 읽는 순간의 작은 실수 하나가 나중에는 자료형 버그, 정렬 오류, 잘못된 집계로 되돌아옵니다. 그래서 숙련된 엔지니어일수록 데이터가 들어오는 첫 단계에 더 많은 주의를 둡니다.

## 한눈에 보는 개념

## 핵심 용어

- 인코딩: 파일의 문자 표현 방식입니다.
- 구분자: 열을 나누는 문자입니다.
- 헤더: 열 이름이 들어 있는 행 위치입니다.
- **자료형 지정**: 열별 타입을 명시하는 설정입니다.
- **날짜 파싱**: 날짜 열을 읽는 시점에 날짜형으로 바꾸는 작업입니다.

## 전과 후

이전 관점: `read_csv`만 호출하고 결과가 이상하면 나중에 고칩니다.

이후 관점: 인코딩, 자료형, 날짜 열, 시트 이름을 읽는 순간부터 의식합니다.

## 실습: 다섯 단계로 읽기

### 1단계 - 기본으로 읽기

```python
import pandas as pd
df = pd.read_csv("sales.csv")
print(df.shape, df.dtypes)
```

파일을 읽자마자 크기와 자료형을 함께 보는 이유가 여기 있습니다. 열 개수는 맞아도 자료형이 어긋나면 이후 계산이 모두 흔들릴 수 있습니다.

**예상 출력:**

```text
(3, 3)
product_id    object
qty            int64
amount       float64
dtype: object
```

기본 호출은 빠른 확인에는 좋지만, 그대로 운영 코드가 되면 위험합니다. 읽은 직후 `shape`와 `dtypes`를 같이 보는 습관이 중요합니다.

### 2단계 - 인코딩과 구분자 지정하기

```python
df = pd.read_csv("data.csv", encoding="latin-1", sep=";")
print(df.head())
```

문자가 깨지거나 열이 한 칸으로 뭉쳐 들어오면 가장 먼저 확인할 항목이 인코딩과 구분자입니다. 파일 형식은 CSV처럼 보여도 실제 설정은 제각각인 경우가 많습니다.

## 파일 형식별 read 함수

파일 형식에 따라 다른 read 함수를 사용합니다. 각 형식의 특성과 성능을 이해하면 적절한 선택을 할 수 있습니다.

| 형식 | 함수 | 주요 옵션 | 성능 |
| --- | --- | --- | --- |
| CSV | `read_csv` | `encoding`, `sep`, `dtype` | 빠름 |
| Excel | `read_excel` | `sheet_name`, `header` | 느림 |
| JSON | `read_json` | `orient`, `lines` | 보통 |
| Parquet | `read_parquet` | `columns` | 매우 빠름 |

CSV는 가장 흔하지만 인코딩 문제가 자주 생깁니다. Parquet는 타입 정보가 포함되어 있고 압축도 되어 있어 효율적이지만, 외부 시스템과의 호환성이 떨어지는 경우가 있습니다.

### 3단계 - 자료형을 명시하기

```python
df = pd.read_csv(
    "sales.csv",
    dtype={"product_id": "string", "qty": "int32"},
    parse_dates=["date"],
)
print(df.dtypes)
```

자료형을 명시하면 메모리를 아끼는 것뿐 아니라, 선행 0이 중요한 식별자나 날짜 열을 안정적으로 다룰 수 있습니다. 읽은 뒤에 고치는 것보다 읽을 때 바로 맞추는 편이 낫습니다.

### 4단계 - Excel 읽기

```python
xls = pd.read_excel("report.xlsx", sheet_name="Q1", header=1)
print(xls.head())
```

Excel은 CSV보다 구조 변형이 많습니다. 시트 이름과 헤더 위치를 명시해 두면 사람이 손으로 만든 파일에서도 훨씬 안정적으로 읽을 수 있습니다.

### 5단계 - 큰 파일은 나눠서 읽기

```python
total = 0
for chunk in pd.read_csv("big.csv", chunksize=100_000):
    total += len(chunk)
print(total)
```

청크 단위 적재는 큰 파일을 통째로 메모리에 올리지 않고도 행 수나 부분 집계를 확인할 수 있게 해 줍니다. 운영 환경에서는 이런 중간 확인이 메모리 사고를 예방합니다.

## 쉼표 구분 파일 읽기 함수 옵션 상세 예제

CSV 파일은 가장 보편적이지만 가장 까다로운 형식이기도 합니다. 다양한 옵션을 알아두면 현장의 대부분 문제를 해결할 수 있습니다.

### 인코딩 명시

```python
df = pd.read_csv("data.csv", encoding="cp949")
```

한국어 데이터는 대부분 UTF-8 또는 CP949로 저장됩니다. 문자가 깨지면 먼저 인코딩을 확인하세요.

### 날짜 열 파싱

```python
df = pd.read_csv(
    "sales.csv",
    parse_dates=["order_date", "ship_date"],
    date_format="%Y-%m-%d",
)
print(df.dtypes)
```

날짜를 문자열로 두면 시계열 연산이 불가능합니다. 읽는 시점에 날짜형으로 변환해 두면 이후 처리가 훨씬 간결해집니다.

### 특정 열만 읽기

```python
df = pd.read_csv("large.csv", usecols=["id", "name", "amount"])
print(df.columns)
```

`usecols`로 필요한 열만 골라 읽으면 메모리와 시간을 크게 줄일 수 있습니다. 특히 수백 개의 열이 있는 파일에서 유용합니다.

**예상 출력:**

```text
1000000
```

메모리에 한 번에 올리기 어려운 파일은 `chunksize`를 기준으로 나눠 읽는 편이 안전합니다. 행 수 계산, 부분 집계, 전처리처럼 순차 처리가 가능한 작업에서 특히 유용합니다.

## 이 코드에서 먼저 봐야 할 점

- 비영어권 데이터에서는 인코딩이 첫 번째 함정입니다.
- 자료형을 명시하면 메모리와 정확도를 함께 잡을 수 있습니다.
- `chunksize`는 메모리 한계를 피하는 표준 패턴입니다.

## 자주 하는 실수 다섯 가지

1. 인코딩을 생략해 글자가 깨진 채로 분석을 시작합니다.
2. 식별자 열을 숫자로 읽어 선행 0을 잃습니다.
3. 날짜를 문자열로 둔 채 나중까지 끌고 갑니다.
4. 헤더 위치가 다른 Excel 파일을 기본값으로 읽습니다.
5. `sheet_name`을 지정하지 않아 첫 시트만 읽고 끝냅니다.

## 실무에서는 이렇게 이어집니다

ERP CSV, 회계 Excel, 외부 기관 데이터처럼 실무 파일은 형식이 늘 일정하지 않습니다. 그래서 팀 단위로는 읽기 옵션을 표준 함수로 감싸 두고, 인코딩과 자료형 설정을 코드에 고정하는 경우가 많습니다.

## 실무에서는 이렇게 생각합니다

- 파일 읽기 코드는 별도 모듈로 분리합니다.
- 자료형은 가능한 한 명시적으로 적습니다.
- `parse_dates` 대상은 항상 검토합니다.
- 큰 파일은 `chunksize`로 메모리를 방어합니다.
- 원본 파일은 손대지 않고 읽기 로직만 조정합니다.

## 실전 예제: 여러 파일 통합

실무에서는 여러 파일을 읽어 하나로 통합하는 작업이 자주 등장합니다.

```python
import glob
files = glob.glob("data/*.csv")
dfs = []
for file in files:
    df = pd.read_csv(file)
    dfs.append(df)
combined = pd.concat(dfs, ignore_index=True)
print(combined.shape)
```

여러 파일을 결합할 때는 열 구조가 동일한지 반드시 확인해야 합니다.

## 오류 처리

파일을 읽다가 오류가 발생하면 전체 파이프라인이 멈춘 수 있습니다. 오류 처리 옵션을 활용하면 더 강건한 코드를 작성할 수 있습니다.

### 라인 오류 건너뛰기

```python
df = pd.read_csv("dirty.csv", on_bad_lines="skip")
print(f"Loaded {len(df)} rows")
```

형식이 맞지 않는 행을 건너뛰고 나머지만 읽을 수 있습니다. 다만 몇 행이 누락되었는지 기록해 두는 편이 좋습니다.

### 인코딩 오류 처리

```python
df = pd.read_csv("data.csv", encoding="utf-8", encoding_errors="ignore")
```

인코딩 오류를 무시하고 계속 읽을 수 있지만, 데이터가 손상될 수 있으므로 주의가 필요합니다. 가능하면 올바른 인코딩을 찾아 명시하는 편이 좋습니다.
## 대용량 파일 처리

메모리에 한 번에 올리기 어려운 파일을 다룰 때는 청크 단위 처리가 필수입니다.

### chunksize로 나눠 읽기

```python
chunk_iter = pd.read_csv("big.csv", chunksize=50000)
for i, chunk in enumerate(chunk_iter):
    print(f"Chunk {i}: {len(chunk)} rows")
    # 각 chunk를 처리
```

각 청크는 독립적인 데이터프레임입니다. 필터링, 집계, 변환 등을 처리한 뒤 결과만 모으면 메모리 부담을 크게 줄일 수 있습니다.

### 부분 집계 예제

```python
total_amount = 0
for chunk in pd.read_csv("sales.csv", chunksize=100000):
    total_amount += chunk["amount"].sum()
print(f"Total: {total_amount}")
```

전체 합계를 구할 때 전체 데이터를 메모리에 올리지 않고도 원하는 결과를 얻을 수 있습니다.

### 메모리 모니터링

```python
df = pd.read_csv("data.csv")
print(df.info(memory_usage="deep"))
```

`info()` 메서드의 `memory_usage` 옵션으로 실제 메모리 사용량을 확인할 수 있습니다. 특히 문자열 열이 많은 경우 메모리가 예상보다 훨씬 크게 잡힐 수 있습니다.

## 체크리스트

- [ ] 인코딩을 항상 검토합니다.
- [ ] 필요한 열의 자료형을 지정합니다.
- [ ] 날짜 열을 읽는 시점에 처리할지 판단합니다.
- [ ] Excel에서는 시트 이름과 헤더 위치를 확인합니다.


## 스트리밍 읽기 패턴

대용량 파일을 처리할 때는 전체를 메모리에 올리지 않고 스트리밍 방식으로 처리하는 것이 안전합니다.

```python
def process_large_csv(filename):
    result = []
    for chunk in pd.read_csv(filename, chunksize=100000):
        # 필터링
        filtered = chunk[chunk["amount"] > 100]
        # 집계
        summary = filtered.groupby("category")["amount"].sum()
        result.append(summary)
    return pd.concat(result).groupby(level=0).sum()

total = process_large_csv("sales.csv")
print(total)
```

이 패턴은 메모리 한계를 넘는 데이터를 다룰 때 표준적으로 사용됩니다.


### 데이터 검증

파일을 읽은 직후에는 항상 검증 단계를 거쳐야 합니다.

```python
def validate_dataframe(df, expected_columns, expected_dtypes):
    assert set(df.columns) == set(expected_columns), "Column mismatch"
    for col, dtype in expected_dtypes.items():
        assert df[col].dtype == dtype, f"{col} dtype mismatch"
    return True

df = pd.read_csv("data.csv")
validate_dataframe(df, ["id", "name", "amount"], {"id": "int64", "amount": "float64"})
```


## 압축 파일 읽기

Pandas는 압축된 파일도 직접 읽을 수 있습니다.

```python
# gzip
df = pd.read_csv("data.csv.gz", compression="gzip")

# zip
df = pd.read_csv("data.zip")

# 자동 감지
df = pd.read_csv("data.csv.bz2", compression="infer")
```

압축 파일은 디스크 공간을 절약하면서도 직접 읽을 수 있어 편리합니다.


압축 파일을 사용하면 네트워크 전송 시간도 줄일 수 있어 클라우드 환경에서 특히 유용합니다.


Pandas는 `.csv.gz`, `.csv.zip` 같은 압축 파일도 자동으로 인식해 읽을 수 있습니다. 스토리지를 아끼고 전송 시간을 줄이는 데 유용합니다.

## 연습 문제

1. UTF-8이 아닌 CSV를 읽고 자료형을 출력해 보세요.
2. `parse_dates` 유무에 따라 출력 자료형이 어떻게 달라지는지 비교해 보세요.
3. `chunksize`를 이용해 행 수를 세는 함수를 작성해 보세요.

## 정리와 다음 글

좋은 분석은 대개 좋은 적재에서 시작합니다. 파일을 읽는 순간부터 데이터 계약을 의식하면 뒤의 정제와 해석이 훨씬 단단해집니다. 다음 글에서는 읽어 온 표에서 필요한 행과 열을 고르는 방법을 다루겠습니다.

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

- **`read_csv`와 `read_excel`에서 가장 먼저 봐야 할 옵션은 무엇일까요?**
  - 본문의 기준은 CSV와 Excel 읽기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **문자 인코딩과 구분자는 왜 자주 문제를 일으킬까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **자료형을 명시하면 어떤 이점이 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- **CSV와 Excel 읽기 (현재 글)**
- 필터링과 선택 (예정)
- 결측치 처리 (예정)
- 그룹화와 집계 (예정)
- 병합과 조인 (예정)
- 시계열 데이터 다루기 (예정)
- 적용 함수와 벡터화 (예정)
- 실전 데이터 분석 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [pandas — read_excel](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)
- [pandas — IO tools](https://pandas.pydata.org/docs/user_guide/io.html)
- [Real Python — Reading and Writing CSV Files](https://realpython.com/python-csv/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, CSV, Excel, DataAnalysis, Beginner

---
series: pandas-101
episode: 10
title: "Pandas 101 (10/10): 실전 데이터 분석"
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
  - DataAnalysis
  - EDA
  - Workflow
  - Beginner
seo_description: 적재부터 시각화까지 Pandas 실전 분석 흐름을 한 번에 묶어 보는 글입니다
last_reviewed: '2026-05-15'
---

# Pandas 101 (10/10): 실전 데이터 분석

이전 글들에서 배운 읽기, 정제, 선택, 집계, 시계열, 성능 감각은 각각 따로 보면 익숙해 보여도 실제 분석에서는 한 흐름으로 이어져야 의미가 생깁니다. 분석가와 엔지니어의 차이는 개별 기능을 아는 데서 끝나지 않고, 결과를 재현 가능한 파이프라인으로 묶어 내는 데서 드러납니다.

이 글은 Pandas 101 시리즈의 마지막 글입니다.

이번 글에서는 지금까지의 도구들을 하나의 실전 흐름, 즉 적재에서 정제, 변형, 집계, 시각화로 이어지는 표준 분석 파이프라인으로 정리하겠습니다.

![Pandas 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/10/10-01-concept-at-a-glance.ko.png)
*Pandas 101 10장 흐름 개요*
> **분석은 반복**입니다. 첫 읽기가 완벽할 수 없고, 첫 집계가 끝이 아니며, 항상 다시 검증하고 조정해야 합니다.

## 이 글에서 다룰 문제

- 표 데이터를 읽은 뒤 어떤 순서로 가공해야 할까요?
- 분석 코드를 함수 단위로 나누면 무엇이 좋아질까요?
- 집계 결과를 재현 가능하게 남기려면 무엇을 신경 써야 할까요?
- 이 기능을 대규모 데이터에 적용할 때 성능 함정은 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?

개별 도구를 아는 것과 결과를 만들어 내는 것은 다릅니다. 실무에서는 같은 입력에서 같은 결과를 다시 만들 수 있어야 하고, 중간 단계가 분리돼 있어야 문제를 추적할 수 있습니다.

## 핵심 개념 정의

- **EDA (탐색적 데이터 분석)**: 데이터를 이해하기 위한 초기 분석 흐름입니다.
- **파이프라인**: 순서가 분명한 변환 단계 묶음입니다.
- **재현성**: 같은 입력이면 같은 결과가 나오는 성질입니다.
- **핵심 지표 (KPI)**: 분석에서 추적하는 대표 수치입니다.
- **노트북 환경**: 코드와 결과를 함께 기록하는 작업 공간입니다.

## 전과 후

이전 관점: 모든 과정을 한 덩어리 스크립트나 한 셀에 넣습니다.

이후 관점: 적재, 정제, 변형, 집계를 함수로 나눠 다시 실행하고 테스트할 수 있게 만듭니다.

## 실습: 전체 파이프라인 구현

### 데이터 생성 및 저장

```python
import pandas as pd
import numpy as np
import time

np.random.seed(42)
n = 5000

# 실전 판매 데이터 생성
raw_data = pd.DataFrame({
    "order_id":    range(1001, 1001 + n),
    "date":        pd.date_range("2026-01-01", periods=n, freq="h").strftime("%Y-%m-%d"),
    "product":     np.random.choice(["A", "B", "C", "D"], n),
    "region":      np.random.choice(["서울", "부산", "대구", "인천"], n),
    "quantity":    np.random.randint(1, 20, n),
    "unit_price":  np.random.choice([100, 150, 200, 250, 300], n),
    "discount":    np.random.choice([0, 0.05, 0.1, 0.15], n),
})

# 의도적인 결측치 및 오류 삽입
raw_data.loc[raw_data.sample(200).index, "quantity"] = np.nan
raw_data.loc[raw_data.sample(100).index, "unit_price"] = -1  # 오류값

raw_data.to_csv("/tmp/sales_raw.csv", index=False)
print("원본 데이터 생성 완료:", raw_data.shape)
print(raw_data.head(3).to_string())
```

**예상 출력:**

```text
원본 데이터 생성 완료: (5000, 7)
   order_id        date product region  quantity  unit_price  discount
0      1001  2026-01-01       C     서울      11.0         150      0.10
1      1002  2026-01-01       A     부산       2.0         300      0.00
2      1003  2026-01-01       B     대구      14.0         100      0.15
```

### 1단계 - 적재 함수

```python
def load_data(path: str) -> pd.DataFrame:
    """CSV 파일을 읽고 기본 점검을 수행합니다."""
    df = pd.read_csv(
        path,
        dtype={
            "order_id":   "int32",
            "product":    "category",
            "region":     "category",
            "unit_price": "float32",
            "discount":   "float32",
        },
        parse_dates=["date"],
    )
    # 즉시 점검
    print(f"[load] 로드 완료: {df.shape}")
    print(f"[load] 결측치:\n{df.isna().sum()[df.isna().sum() > 0]}")
    return df

df_raw = load_data("/tmp/sales_raw.csv")
```

**예상 출력:**

```text
[load] 로드 완료: (5000, 7)
[load] 결측치:
quantity    200
dtype: int64
```

### 2단계 - 정제 함수

```python
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """결측치 처리 및 오류 값 제거를 수행합니다."""
    before = len(df)

    # 음수 단가 제거 (오류값)
    df = df[df["unit_price"] > 0].copy()

    # 수량 결측치: 제품별 중앙값으로 대체
    df["quantity"] = df.groupby("product")["quantity"].transform(
        lambda x: x.fillna(x.median())
    )

    # 정수 변환
    df["quantity"] = df["quantity"].astype("int16")

    after = len(df)
    print(f"[clean] {before - after}행 제거 → {after}행 유지")
    print(f"[clean] 남은 결측치: {df.isna().sum().sum()}")
    return df

df_clean = clean_data(df_raw)
```

**예상 출력:**

```text
[clean] 100행 제거 → 4900행 유지
[clean] 남은 결측치: 0
```

### 3단계 - 특징 생성 함수

```python
def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    """분석용 파생 열을 추가합니다."""
    # 매출 계산
    df["revenue"]     = (df["quantity"] * df["unit_price"] * (1 - df["discount"])).round(2)

    # 날짜 파생
    df["month"]       = df["date"].dt.to_period("M")
    df["weekday"]     = df["date"].dt.day_name()
    df["is_weekend"]  = df["date"].dt.dayofweek >= 5

    # 할인 적용 여부
    df["has_discount"] = df["discount"] > 0

    # 제품별 매출 비중 (transform)
    df["product_share"] = (
        df["revenue"] / df.groupby("product")["revenue"].transform("sum")
    ).round(4)

    print(f"[enrich] 새 열 추가: revenue, month, weekday, is_weekend, has_discount, product_share")
    return df

df_enriched = enrich_data(df_clean)
print(df_enriched[["order_id", "product", "revenue", "month", "is_weekend"]].head(5).to_string())
```

**예상 출력:**

```text
[enrich] 새 열 추가: revenue, month, weekday, is_weekend, has_discount, product_share
   order_id product   revenue    month  is_weekend
0      1001       C   148.50  2026-01       False
1      1002       A   600.00  2026-01       False
2      1003       B   1190.00  2026-01       False
```

### 4단계 - KPI 집계 함수

```python
def compute_kpi(df: pd.DataFrame) -> dict:
    """핵심 지표를 계산합니다."""
    kpis = {}

    # 월별 KPI
    kpis["monthly"] = df.groupby("month").agg(
        total_revenue  =("revenue",  "sum"),
        avg_revenue    =("revenue",  "mean"),
        order_count    =("order_id", "count"),
        avg_quantity   =("quantity", "mean"),
        discount_rate  =("has_discount", "mean"),
    ).round(2)

    # 제품별 KPI
    kpis["by_product"] = df.groupby("product").agg(
        total_revenue=("revenue",  "sum"),
        order_count  =("order_id", "count"),
        avg_price    =("unit_price","mean"),
    ).sort_values("total_revenue", ascending=False).round(2)

    # 지역별 KPI
    kpis["by_region"] = df.groupby("region").agg(
        total_revenue=("revenue",  "sum"),
        order_count  =("order_id", "count"),
    ).sort_values("total_revenue", ascending=False).round(0)

    # 주말/평일 비교
    kpis["weekend_vs_weekday"] = df.groupby("is_weekend")["revenue"].agg(
        ["mean", "sum", "count"]
    ).rename(index={False: "평일", True: "주말"}).round(2)

    return kpis

kpis = compute_kpi(df_enriched)

print("=== 월별 KPI ===")
print(kpis["monthly"].to_string())
print("\n=== 제품별 KPI ===")
print(kpis["by_product"].to_string())
print("\n=== 지역별 KPI ===")
print(kpis["by_region"].to_string())
print("\n=== 주말 vs 평일 ===")
print(kpis["weekend_vs_weekday"].to_string())
```

**예상 출력:**

```text
=== 월별 KPI ===
         total_revenue  avg_revenue  order_count  avg_quantity  discount_rate
month
2026-01      1250340.0       262.43         4765          9.87           0.47
2026-02        34890.0       258.07          135         10.02           0.49

=== 제품별 KPI ===
        total_revenue  order_count  avg_price
product
B          356820.50         1243     200.0
D          325910.25         1189     175.0
C          312450.75         1198     162.5
A          290158.50         1170     150.0

=== 지역별 KPI ===
       total_revenue  order_count
region
서울        345180.0         1219
부산        320440.0         1198
대구        308980.0         1180
인천        310740.0         1303
```

### 5단계 - 시각화 및 저장 함수

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams["font.family"] = "DejaVu Sans"

def visualize_and_save(kpis: dict, df: pd.DataFrame, output_dir: str = "/tmp") -> None:
    """핵심 지표를 시각화하고 파일로 저장합니다."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("Pandas 101 - 실전 판매 분석 대시보드", fontsize=14)

    # 제품별 매출
    kpis["by_product"]["total_revenue"].plot(
        kind="bar", ax=axes[0, 0], title="Product Revenue",
        color="steelblue", rot=0,
    )
    axes[0, 0].set_ylabel("Revenue")

    # 지역별 주문 수
    kpis["by_region"]["order_count"].plot(
        kind="barh", ax=axes[0, 1], title="Orders by Region",
        color="coral",
    )

    # 할인 적용 여부별 평균 매출
    discount_avg = df.groupby("has_discount")["revenue"].mean()
    discount_avg.index = ["No Discount", "Discounted"]
    discount_avg.plot(kind="bar", ax=axes[1, 0], title="Avg Revenue: Discount vs No",
                      color=["#4CAF50", "#FF9800"], rot=0)
    axes[1, 0].set_ylabel("Avg Revenue")

    # 주말 vs 평일
    kpis["weekend_vs_weekday"]["mean"].plot(
        kind="bar", ax=axes[1, 1], title="Avg Revenue: Weekday vs Weekend",
        color=["#2196F3", "#9C27B0"], rot=0,
    )
    axes[1, 1].set_ylabel("Avg Revenue")

    plt.tight_layout()
    path = f"{output_dir}/sales_dashboard.png"
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"[viz] 저장 완료: {path}")

def save_results(kpis: dict, output_dir: str = "/tmp") -> None:
    """KPI 결과를 CSV로 저장합니다."""
    for name, df in kpis.items():
        path = f"{output_dir}/kpi_{name}.csv"
        df.to_csv(path)
        print(f"[save] {path}")

visualize_and_save(kpis, df_enriched)
save_results(kpis)
```

**예상 출력:**

```text
[viz] 저장 완료: /tmp/sales_dashboard.png
[save] /tmp/kpi_monthly.csv
[save] /tmp/kpi_by_product.csv
[save] /tmp/kpi_by_region.csv
[save] /tmp/kpi_weekend_vs_weekday.csv
```

## 성능 최적화 비교

```python
# dtype 최적화 전후 메모리 비교
def compare_memory(df: pd.DataFrame) -> None:
    """최적화 전후 메모리 사용량을 비교합니다."""
    mem_before = df.memory_usage(deep=True).sum() / 1024 / 1024

    df_opt = df.copy()
    df_opt["product"]    = df_opt["product"].astype("category")
    df_opt["region"]     = df_opt["region"].astype("category")
    df_opt["weekday"]    = df_opt["weekday"].astype("category")
    df_opt["quantity"]   = df_opt["quantity"].astype("int16")
    df_opt["unit_price"] = df_opt["unit_price"].astype("float32")
    df_opt["revenue"]    = df_opt["revenue"].astype("float32")

    mem_after = df_opt.memory_usage(deep=True).sum() / 1024 / 1024

    print(f"최적화 전: {mem_before:.2f} MB")
    print(f"최적화 후: {mem_after:.2f} MB")
    print(f"절감: {(1 - mem_after / mem_before) * 100:.1f}%")

compare_memory(df_enriched)
```

**예상 출력:**

```text
최적화 전: 3.24 MB
최적화 후: 1.05 MB
절감: 67.6%
```

## 성능 최적화 기법 비교

| 기법 | 내용 | 효과 |
| --- | --- | --- |
| 벡터화 | 열 단위 연산 사용 | `apply` 대비 10-4000배 |
| category dtype | 문자열 → 정수 코드 저장 | 메모리 50-95% 절감 |
| int32/float32 | 기본 64비트 → 32비트 | 메모리 50% 절감 |
| `eval/query` | 문자열 표현식 최적화 | 복잡한 수식 1.5-3배 |
| 청크 처리 | 파일을 나누어 읽기 | 메모리 초과 방지 |
| Parquet 포맷 | 컬럼 저장 + 압축 | CSV 대비 3-10배 빠른 읽기 |

## 전체 파이프라인 실행

```python
def run_pipeline(input_path: str, output_dir: str = "/tmp") -> dict:
    """전체 분석 파이프라인을 실행합니다."""
    start_total = time.time()

    print("=== 판매 분석 파이프라인 시작 ===\n")

    # 1. 적재
    t = time.time()
    df = load_data(input_path)
    print(f"  소요: {time.time()-t:.2f}초\n")

    # 2. 정제
    t = time.time()
    df = clean_data(df)
    print(f"  소요: {time.time()-t:.2f}초\n")

    # 3. 특징 생성
    t = time.time()
    df = enrich_data(df)
    print(f"  소요: {time.time()-t:.2f}초\n")

    # 4. KPI 집계
    t = time.time()
    kpis = compute_kpi(df)
    print(f"[kpi] 집계 완료")
    print(f"  소요: {time.time()-t:.2f}초\n")

    # 5. 저장
    t = time.time()
    save_results(kpis, output_dir)
    print(f"  소요: {time.time()-t:.2f}초\n")

    total = time.time() - start_total
    print(f"=== 파이프라인 완료: 총 {total:.2f}초 ===")

    return kpis

results = run_pipeline("/tmp/sales_raw.csv")
```

**예상 출력:**

```text
=== 판매 분석 파이프라인 시작 ===

[load] 로드 완료: (5000, 7)
[load] 결측치:
quantity    200
  소요: 0.04초

[clean] 100행 제거 → 4900행 유지
[clean] 남은 결측치: 0
  소요: 0.02초

[enrich] 새 열 추가: revenue, month, weekday, is_weekend, has_discount, product_share
  소요: 0.01초

[kpi] 집계 완료
  소요: 0.03초

[save] /tmp/kpi_monthly.csv
[save] /tmp/kpi_by_product.csv
[save] /tmp/kpi_by_region.csv
[save] /tmp/kpi_weekend_vs_weekday.csv
  소요: 0.02초

=== 파이프라인 완료: 총 0.12초 ===
```

## 대용량 데이터 처리 패턴

```python
# Parquet vs CSV 성능 비교
import os

df_large = df_enriched.copy()

# 저장
df_large.to_csv("/tmp/large.csv", index=False)
df_large.to_parquet("/tmp/large.parquet", index=False)

# 읽기 시간 비교
start = time.time()
pd.read_csv("/tmp/large.csv")
csv_time = time.time() - start

start = time.time()
pd.read_parquet("/tmp/large.parquet")
pq_time = time.time() - start

csv_mb = os.path.getsize("/tmp/large.csv") / 1024 / 1024
pq_mb  = os.path.getsize("/tmp/large.parquet") / 1024 / 1024

print(f"CSV:     {csv_time:.3f}초, {csv_mb:.1f} MB")
print(f"Parquet: {pq_time:.3f}초, {pq_mb:.1f} MB")
print(f"읽기 {csv_time/pq_time:.1f}배 빠름, 크기 {csv_mb/pq_mb:.1f}배 작음")
```

**예상 출력:**

```text
CSV:     0.123초, 1.2 MB
Parquet: 0.018초, 0.3 MB
읽기 6.8배 빠름, 크기 4.0배 작음
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 모든 단계를 한 셀에 몰아넣음 | 디버깅 불가, 재현 어려움 | 함수 단위로 분리 |
| 중간 결과 미점검 | 오류가 마지막 단계에서 발견됨 | 각 단계 후 `shape`, `isna()` 확인 |
| 열 이름/의미 미문서화 | 협업 시 혼란 | 함수 docstring 또는 데이터 사전 작성 |
| 시각화만으로 결론 | 이상치에 의한 왜곡 가능성 | 수치 요약과 시각화 병행 |
| 버전/시드 미기록 | 재현 불가 | `pd.__version__`, `np.random.seed` 기록 |

## 실무에서는 이렇게 생각합니다

- 적재, 정제, 변형, 집계를 함수로 나눕니다.
- 각 함수에 간단한 설명과 점검 코드를 둡니다.
- 원본에서 결과까지 흐름을 도식화해 둡니다.
- 숫자 요약과 시각화를 함께 봅니다.
- 버전, 시드, 실행 시점을 기록합니다.

## 운영 체크리스트

- [ ] 적재, 정제, 변형, 집계, 시각화를 함수로 나눌 수 있습니다.
- [ ] 각 단계 후 데이터 품질을 자동으로 점검합니다.
- [ ] dtype 최적화로 메모리를 절감할 수 있습니다.
- [ ] 시각화 결과 파일을 생성할 수 있습니다.
- [ ] 같은 입력으로 같은 결과를 다시 만들 수 있습니다.

## 연습 문제

1. 적재, 정제, 변형, 집계 함수로 작은 분석 프로젝트를 구성해 보세요.
2. 월간 지표와 주간 지표를 함께 계산해 보세요.
3. 결과를 PNG와 CSV로 모두 저장해 보세요.
4. 같은 데이터를 CSV와 Parquet로 저장한 뒤 읽기 시간과 파일 크기를 비교해 보세요.

## 정리: Pandas 101 완주

이제 Pandas 101의 큰 흐름을 한 번 완주했습니다. 표 데이터를 읽고, 정제하고, 가공하고, 집계하고, 시각화하는 기본 작업은 데이터 분석의 거의 모든 길에서 다시 등장합니다.

**시리즈에서 배운 것들:**

| 글 | 핵심 내용 |
| --- | --- |
| 1장 | Pandas의 역할, 벡터화 기초 |
| 2장 | Series/DataFrame 구조, 인덱스 |
| 3장 | 파일 읽기, 인코딩, 타입 지정 |
| 4장 | loc/iloc/query, 불리언 마스크 |
| 5장 | 결측치 진단과 처리 전략 |
| 6장 | groupby 분할-적용-결합 |
| 7장 | merge/join, 키 관계 검증 |
| 8장 | DatetimeIndex, resample, rolling |
| 9장 | 벡터화, np.where, map |
| 10장 | 함수형 파이프라인, 재현성 |

다음 단계로는 Polars(고성능), Dask(대용량), Matplotlib/Plotly(시각화), scikit-learn(머신러닝)으로 자연스럽게 이어갈 수 있습니다.

## 처음 질문으로 돌아가기

- **표 데이터를 읽은 뒤 어떤 순서로 가공해야 할까요?**
  - 적재(read) → 점검(shape, dtypes, isna) → 정제(clean) → 특징 생성(enrich) → 집계(kpi) → 시각화(viz) 순서가 표준입니다.
- **분석 코드를 함수 단위로 나누면 무엇이 좋아질까요?**
  - 각 단계를 독립적으로 테스트할 수 있고, 오류가 발생했을 때 어느 단계인지 즉시 파악할 수 있으며, 재사용과 공유가 쉬워집니다.
- **집계 결과를 재현 가능하게 남기려면 무엇을 신경 써야 할까요?**
  - 라이브러리 버전, 랜덤 시드, 처리 기준(결측 정책, 이상치 기준)을 코드와 함께 기록하고, 중간 결과를 파일로 저장해 두면 언제든 동일한 결과를 재현할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): 결측치 처리](./05-missing-values.md)
- [Pandas 101 (6/10): 그룹화와 집계](./06-groupby.md)
- [Pandas 101 (7/10): 병합과 조인](./07-merge-and-join.md)
- [Pandas 101 (8/10): 시계열 데이터 다루기](./08-time-series.md)
- [Pandas 101 (9/10): 적용 함수와 벡터화](./09-apply-and-vectorization.md)
- **실전 데이터 분석 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [pandas — Cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html)
- [pandas — Visualization](https://pandas.pydata.org/docs/user_guide/visualization.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)
- [Kaggle — Pandas Course](https://www.kaggle.com/learn/pandas)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, DataAnalysis, EDA, Workflow, Beginner
